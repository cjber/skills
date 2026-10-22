#!/usr/bin/env python3
"""Generate the index from pinned Forever DB2 exports.

Map.CorpseMapID and Corpse_0/1 are the client's return-to-instance point. UiMapAssignment projects it onto a map,
following the data technique used by the suite's entrance-pin addon. No sibling coordinate is reused.
"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = "1.60.1.70450"
INPUTS = ROOT / "tools" / "data"
PINS = ROOT / "tools" / "pins.json"
OUTPUT = ROOT / "Data" / "Instances.lua"


def rows(table):
    with (INPUTS / f"{table}-{BUILD}.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def generate():
    pins = json.loads(PINS.read_text())
    for name, expected in pins["files"].items():
        actual = hashlib.sha256((INPUTS / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"{name}: sha256 {actual} does not match tools/pins.json")

    maps = {int(row["ID"]): row for row in rows("Map")}
    ui_maps = {int(row["ID"]): row for row in rows("UiMap")}
    assignments = rows("UiMapAssignment")
    assignment_by_map = {}
    for row in assignments:
        assignment_by_map.setdefault(int(row["MapID"]), []).append(row)
    art_by_map = {}
    for row in rows("UiMapXMapArt"):
        if int(row["PhaseID"]) == 0:
            art_by_map.setdefault(int(row["UiMapID"]), []).append(int(row["UiMapArtID"]))
    areas_by_map = {}
    for row in rows("AreaTable"):
        areas_by_map.setdefault(int(row["ContinentID"]), []).append(int(row["ID"]))
    result = []
    for instance_id, row in sorted(maps.items()):
        if row["InstanceType"] not in {"1", "2"}:
            continue
        if row["MapName_lang"] in {"Test Dungeon", "CashTest"} or row["MapName_lang"].startswith("<"):
            continue
        views = []
        for assignment in assignment_by_map.get(instance_id, []):
            ui_id = int(assignment["UiMapID"])
            art_ids = sorted(set(art_by_map.get(ui_id, [])))
            if art_ids:
                views.append({"uiMapID": ui_id, "mapArtIDs": art_ids})
        entry = {
            "id": instance_id,
            "name": row["MapName_lang"],
            "mapID": instance_id,
            "mapType": "party" if row["InstanceType"] == "1" else "raid",
            "continent": "Unknown",
            "mapViews": sorted(views, key=lambda value: value["uiMapID"]),
            "areaIDs": sorted(areas_by_map.get(instance_id, [])),
        }
        if int(row["WdtFileDataID"]) > 0:
            entry["wdtFileDataID"] = int(row["WdtFileDataID"])
        # Corpse coordinates are the client's only exposed entrance point; include only a valid projection.
        corpse_map, x, y = int(row["CorpseMapID"]), float(row["Corpse_0"]), float(row["Corpse_1"])
        if corpse_map >= 0 and (x != 0 or y != 0):
            for assignment in assignment_by_map.get(corpse_map, []):
                try:
                    if int(assignment["WMODoodadPlacementID"]) or int(assignment["WMOGroupID"]):
                        continue
                    r0, r1, r3, r4 = (float(assignment[f"Region_{i}"]) for i in (0, 1, 3, 4))
                    if not (r0 <= x <= r3 and r1 <= y <= r4) or r3 == r0 or r4 == r1:
                        continue
                    u0, u1 = float(assignment["UiMin_0"]), float(assignment["UiMax_0"])
                    v0, v1 = float(assignment["UiMin_1"]), float(assignment["UiMax_1"])
                    px = round(u0 + (r4 - y) / (r4 - r1) * (u1 - u0), 3)
                    py = round(v0 + (r3 - x) / (r3 - r0) * (v1 - v0), 3)
                    if 0 <= px <= 1 and 0 <= py <= 1:
                        entrance_map = int(assignment["UiMapID"])
                        entry["entrances"] = [{"mapID": entrance_map, "x": px, "y": py}]
                        visited = set()
                        current = entrance_map
                        while current in ui_maps and current not in visited:
                            visited.add(current)
                            ui_row = ui_maps[current]
                            if int(ui_row["Type"]) == 2:
                                entry["continent"] = ui_row["Name_lang"]
                                break
                            current = int(ui_row["ParentUiMapID"] or 0)
                        break
                except (KeyError, ValueError, ZeroDivisionError):
                    continue
        result.append(entry)

    def lua(value):
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, list):
            return "{ " + ", ".join(lua(item) for item in value) + " }"
        if isinstance(value, dict):
            return "{ " + ", ".join(f"{key} = {lua(item)}" for key, item in value.items()) + " }"
        raise TypeError(value)

    lines = [
        "-- Generated by tools/gen_instances.py; do not edit.",
        f"-- Source build: {BUILD}.",
        "local _, ns = ...",
        "ns.Instances = {",
    ]
    lines.extend("\t" + lua(entry) + "," for entry in result)
    OUTPUT.write_text("\n".join(lines + ["}", ""]), encoding="utf-8")


if __name__ == "__main__":
    generate()
