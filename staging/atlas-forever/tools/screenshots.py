#!/usr/bin/env python3
"""Render deterministic screenshots of Atlas's shipped v0.1.0 UI states."""

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "wowmock"))
import wowmock as wm  # noqa: E402

OUT = Path(os.environ.get("ATLAS_SCREENSHOT_OUT", ROOT / "docs" / "screenshots"))


def instances():
    source = next((ROOT / "tools" / "data").glob("Map-*.csv"))
    with source.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return sorted(
        [
            row
            for row in rows
            if row["InstanceType"] in {"1", "2"}
            and row["MapName_lang"] not in {"Test Dungeon", "CashTest"}
            and not row["MapName_lang"].startswith("<")
        ],
        key=lambda row: row["MapName_lang"].casefold(),
    )


def render():
    ui = wm.Ui(scale=2)
    data = instances()
    rows = data[:10]
    deadmines = next((row for row in data if row["MapName_lang"] == "Deadmines"), rows[0])
    ahn_qiraj = next((row for row in data if row["MapName_lang"] == "Ahn'Qiraj Temple"), rows[0])

    def draw(selected, with_tooltip=False):
        atlas, ox, oy = wm.basic_panel(ui, "Atlas Forever", 760, 470)
        x, y = ox + 12, oy + 32
        atlas.text(x, y, "Continents", wm.FONTS["GameFontNormal"], wm.NORMAL)
        for index, name in enumerate(["All continents", "Eastern Kingdoms", "Kalimdor", "Unknown"]):
            wm.ui_panel_button(atlas, x, y + 24 + index * 28, 160, 24, name)
        type_y = y + 24 + 4 * 28 + 10
        atlas.text(x, type_y, "Type", wm.FONTS["GameFontNormal"], wm.NORMAL)
        for index, name in enumerate(["All types", "Dungeons", "Raids"]):
            wm.ui_panel_button(atlas, x, type_y + 24 + index * 28, 160, 24, name)
        atlas.text(x + 174, y, "Instances", wm.FONTS["GameFontNormal"], wm.NORMAL)
        for index, row in enumerate(rows):
            row_x = x + 170
            row_y = y + 24 + index * 32
            wm.ui_panel_button(
                atlas,
                row_x,
                row_y,
                180,
                28,
                "",
            )
            atlas.text(
                row_x + 8,
                row_y + 3,
                row["MapName_lang"],
                wm.FONTS["GameFontHighlightSmall"],
                width=118,
                box_height=22,
            )
            row_type = "Raid" if row["InstanceType"] == "2" else "Dungeon"
            atlas.text(
                row_x + 126,
                row_y + 3,
                row_type,
                wm.FONTS["GameFontDisableSmall"],
                justify="RIGHT",
                width=46,
                box_height=22,
            )
        if selected:
            atlas.text(x + 418, y, selected["MapName_lang"], wm.FONTS["GameFontNormalLarge"], wm.NORMAL)
            type_name = "Raid" if selected["InstanceType"] == "2" else "Dungeon"
            continent = "Kalimdor" if selected["ID"] == "531" else "Eastern Kingdoms"
            atlas.text(x + 418, y + 23, f"{type_name} · {continent}", wm.FONTS["GameFontHighlight"])
            atlas.text(
                x + 418, y + 62, "The client does not expose an interior map", wm.FONTS["GameFontHighlight"], width=260
            )
            atlas.text(x + 418, y + 78, "for this instance.", wm.FONTS["GameFontHighlight"])
            atlas.text(x + 418, y + 143, "Contents", wm.FONTS["GameFontNormal"], wm.NORMAL)
            atlas.text(
                x + 418,
                y + 165,
                "Install QuestieDB to see",
                wm.FONTS["GameFontHighlightSmall"],
            )
            atlas.text(x + 418, y + 180, "creature contents.", wm.FONTS["GameFontHighlightSmall"])
            wm.ui_panel_button(atlas, x + 418, y + 365, 150, 24, "Travel to entrance")
            if with_tooltip:
                tip = wm.tooltip(ui, [wm.TooltipLine(selected["MapName_lang"]), wm.TooltipLine(type_name)])
                selected_index = rows.index(selected) if selected in rows else 0
                atlas.paste(tip, x + 350, y + 24 + selected_index * 32)
        return atlas

    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "atlas-list.png": wm.scene(ui, [(draw(deadmines), 0, 0)]),
        "atlas-instance.png": wm.scene(ui, [(draw(ahn_qiraj), 0, 0)]),
        "atlas-tooltip.png": wm.scene(ui, [(draw(deadmines, True), 0, 0)]),
    }
    for name, image in files.items():
        image.save(OUT / name)
    source_files = (
        "Core/Model.lua",
        "Data/Instances.lua",
        "Locales/enUS.lua",
        "UI/List.lua",
        "UI/Map.lua",
        "UI/Window.lua",
        "tools/screenshots.py",
    )
    scenes = {
        "build": wm.BUILD,
        "sources": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_files},
        "scenes": {
            "atlas-list.png": {"selectedMapID": 36, "questie": False, "floorViews": 0},
            "atlas-instance.png": {"selectedMapID": 531, "questie": False, "floorViews": 0},
            "atlas-tooltip.png": {"selectedMapID": 36, "questie": False, "tooltip": True, "floorViews": 0},
        },
        "instanceRows": len(data),
    }
    scene_dump = json.dumps(scenes, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    (OUT / "scenes.json").write_text(scene_dump, encoding="utf-8")
    scene_hash = hashlib.sha256(scene_dump.encode()).hexdigest()
    image_hashes = [hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in sorted(files)]
    (OUT / "scenes.sha256").write_text(
        f"{scene_hash}  scenes.json\n"
        + "".join(f"{value}  {name}\n" for value, name in zip(image_hashes, sorted(files), strict=True)),
        encoding="utf-8",
    )


if __name__ == "__main__":
    render()
