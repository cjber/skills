# Client data limits

Generated from the pinned Forever build `1.60.1.70450`. The generator omits values the client does not expose.

## Values not present in the exports

- **Interior map art, floor names and wing names:** no `UiMapAssignment` rows link any of the 47 listed instance maps to a UI map, so the client exposes zero interior map views. The `Map.WdtFileDataID` values are recorded as WDT asset IDs; they are not treated as flat UI map images.
- **Level ranges:** the `Map` export has no minimum or maximum instance-level fields. `minLevel` and `maxLevel` are absent on all 47 rows.
- **Entrance coordinates and parent continent:** 22 rows have `CorpseMapID = -1` or a zero corpse position. No entrance coordinate or continent is inferred for them.
- **Creature positions:** QuestieDB spawn-zone membership can support a names list, but this addon does not have reliable instance map coordinates for those rows. No creature pins are drawn.
- **Optional catalogue cross-link:** Field Guide's `API.Species(zoneName)` indexes outdoor zones, not these instance-area IDs, so no misleading count or tab is shown. Legacy's read-only API covers zone challenges/completion, which is outside this addon's instance view.

Instances without entrance coordinates or a parent continent:

| Map ID | Client name |
|---:|---|
| 169 | Emerald Dream |
| 269 | Caverns of Time |
| 533 | Naxxramas (raid) |
| 2720 | The Searing Basin |
| 2784 | Demon Fall Canyon |
| 2789 | The Tainted Scar |
| 2791 | Storm Cliffs |
| 2804 | The Crystal Vale |
| 2806 | Shadow Hold |
| 2807 | Burning of Andorhal |
| 2817 | Starfall Barrow Den |
| 2832 | Nightmare Grove |
| 2853 | Deadwind Pass |
| 2856 | Scarlet Enclave |
| 2875 | Karazhan Crypts |
| 2902 | The Scarab Dais |
| 2921 | Naxxramas (party map) |
| 2959 | City of Dalaran |
| 2998 | Excavation Site: Wetlands |
| 2999 | Ruins of Lordaeron |
| 3065 | The Hall of Thanes |
| 3109 | Manor Mistmantle |
