# Third-party notices

## Inputs

| Input | Source and pin | Licence | Ships in addon zip |
|---|---|---|---|
| Map, UiMap, UiMapAssignment, UiMapXMapArt, UiMapArt, UiMapArtStyleLayer and AreaTable | Blizzard client DB2 CSV exports from wago.tools; client build `1.60.1.70450`; per-file SHA-256 values in `tools/pins.json` | Blizzard game data; build-time factual metadata only | No. Generated names, map IDs, area IDs and WDT file IDs ship in `Data/Instances.lua` |
| Optional creature names, levels, ranks and spawn areas | The player's installed QuestieDB public tables; read at runtime only | QuestieDB's own terms; no QuestieDB data is copied or shipped | No |
| UI map conventions and art | Blizzard's WoW client UI and client textures/atlases, when used at runtime | Blizzard | No third-party art is bundled |

## Ideas and contributors

| Source | Idea used |
|---|---|
| Shortest Path Forever | Optional travel hand-off to the entrance |
| Field Guide Forever | Optional read-only instance creature context |
| Legacy Forever | Entrance placement technique |
| Bestiary Forever | QuestieDB instance-area matching technique |

No sibling code or data values are copied into this addon. No translators or reporters are recorded for this release.
