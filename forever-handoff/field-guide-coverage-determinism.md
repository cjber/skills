# Brief: Field Guide Forever - real DB, zero hand-written creatures

Repo: `cjber/bestiary-forever` (addon folder `FieldGuideForever`, Interface 16001, WoW: Forever).
Read `AGENTS.md` and `.agents/skills/sift-project/SKILL.md` first. Owner: @cillian.

**This brief replaces the earlier version that proposed a CMaNGOS classic-db dump. That was wrong and is
forbidden by the owner's standing rules: no CMaNGOS data, ever. Use the sources below and nothing else.**

## The data source decision (measured 2026-10-21, do not re-litigate)

Two candidate "WoW Forever databases" were tested against the live Forever build `1.60.1.70450`
(`wago.tools/api/builds`, product `wow_classic_beta`, 1.6x releases):

| Source | Verdict |
|---|---|
| Client DB2 via wago.tools | **Used for client constants only.** `AreaTable` (1375 rows), `Map` (75), `CreatureFamily` (27), `CreatureDisplayInfo` (14218) all export cleanly and are pinned per build. But this build's `Creature` table holds **184 rows and has no zone column**, and `InstanceEncounter`, `JournalEncounter`, `JournalInstance`, `Encounter`, `CreatureTemplate` and `NPCText` all return `Table not found`. Spawn placement is server-side. **It cannot produce a per-zone creature or boss catalogue.** |
| QuestieDB, Forever flavour | **The catalogue source.** Release `QuestieDB-Forever.zip` is generated for the Forever client (`## Interface: 16001`, `X-Flavor: Forever`, `X-Contract-Version: 4`) and its public `NpcDB` exposes exactly what a field journal needs: `name`, `minLevel`, `maxLevel`, `rank`, `subName`, `zoneID` and `spawns` grouped by zone, across outdoor zones and instances. It is regenerated as Forever moves. |
| Wowhead | **Excluded.** Owner: they are restrictive about data use. Do not scrape, cache or vendor it. |

Licensing rule from the suite applies unchanged: **QuestieDB carries no licence, so nothing from it is
committed to the repository.** `adventure-guide-forever` already sets this precedent for the same data
(`tools/gen_corpus.py` builds a gitignored corpus and never commits it, and `legacy-forever` reads QuestieDB
in game instead of copying it). Match it.

## Requirement 1 - delete every hand-written creature

1. `git rm Data/Creatures.lua`. The 10 zones and 183 species in it are gone. No replacement list is written
   by hand, and no generated file contains creature names, levels, families or zone placement.
2. New `Integrations/QuestieDB.lua`, the only reader of the player's QuestieDB, through its public API
   (`QuestieDB.NpcDB` / `LibQuestieDB`). It builds `ns.Catalogue` on demand: for a zone, the NPCs whose
   `zoneID` matches, with name, level range, family (`subName`), `rank` (rare/elite/boss), and the instance
   grouping for dungeons and raids. Read it exactly as `skillup-forever/Integrations/Questie.lua` reads
   Questie, including its guard for a QuestieDB that has not loaded yet: never build during a call, defer to
   the next frame and report a status (`"ok"`, `"missing"`, `"unsupported"`, `"loading"`).
3. Graceful degradation: without QuestieDB the window opens with an explanation and an install pointer, the
   way `legacy-forever` handles its Quests category. No errors, no nil indexing, no silent empty list.
4. Species identity is the QuestieDB NPC id - the game's own creature id. `ns.SpeciesById` is keyed by it, and
   `Model.Tier` keeps working off it so a creature's rarity colour stays identical for every player.
5. Coverage is whatever the player's Forever QuestieDB carries, which is the whole point: every outdoor zone
   with creatures, plus every dungeon and raid with its bosses, updates with the game and never needs a code
   change. Do not filter it down to a starting-zone subset.

## Requirement 2 - the client constants, generated and auto-refreshed

Constants that QuestieDB does not carry come from the client, pinned to the Forever build, never typed:

1. `tools/gen_zones.py` (stdlib only, no runtime network): download `AreaTable`, `Map`, `CreatureFamily`,
   `CreatureDisplayInfo` CSVs from `https://wago.tools/db2/<Table>/csv?build=<BUILD>` into `tools/.cache/`,
   parse fail-closed, and emit `Data/Client.lua` holding zone names and continents, instance maps with their
   `InstanceType`, family names, and the portrait display ids the journal draws. Header records table, build,
   row count and sha256 per input, as `legacy-forever/tools/gen_legacy.py` does.
2. Reuse `legacy-forever`'s helpers rather than reinventing them: copy `tools/forever_tools/wago.py`,
   `csvtable.py`, `latest_build.py` and `fsio.py` into this repo (same shape, same checks, credits to Agent
   Labs not needed - these are cjber's own files).
3. `.github/workflows/refresh-data.yml`, modelled on `legacy-forever`'s: daily `schedule`, reads the newest
   Forever build from `https://wago.tools/api/builds`, regenerates `Data/Client.lua`, and opens a PR when it
   differs. That is what "updates with WoW Forever" means in practice.
4. `tools/check_generated.py` (copy from the suite) fails CI if `Data/Client.lua` is hand-edited or stale
   against its recorded build.
5. Delete `tools/mockups.py`'s `load_catalogue()` that parses `Data/Creatures.lua`. Mockups instead read a
   fixture built from a pinned QuestieDB release (tag + sha256, same pin shape as
   `adventure-guide-forever/tools/gen_corpus.py`, `v1.0.6` /
   `d78b066c362eaf28258d9e2d041c0a7b03d6943a2dfc741dec70c6bfd8e1fc27` is current) into the gitignored
   `tools/.cache/`. No overlap or layout constant may regress: the bottom bar fix from #5 stays.

## Requirement 3 - deterministic state per player, consistent rarity for everyone

Personal progress stays personal; classification never depends on it.

1. `Model.Tier` stays a pure function of catalogue data. A spec asserts that two states with very different
   progress give the same tier for the same NPC id.
2. The UI labels what is personal: a "your record" marker on kill counts, rare confirmations and shinies, so a
   player never reads their own shiny as a shared fact about the creature.
3. SavedVariables: `SCHEMA = 2`, a `Migrate(db)` that walks old versions up, and one normalisation pass at
   login that clamps counts to `0..MASTERED_AT` / `RARE_TARGET` / `SHINY_TARGET`, drops unknown fields and
   defaults missing ones. Corrupt or partial DB loads as a valid empty state instead of erroring.
4. Old saves: v1 entries were keyed by the deleted synthetic ids. Ship `Core/LegacyIds.lua`, generated once by
   a throwaway script from the deleted `Data/Creatures.lua` before it is removed, mapping old id -> NPC name,
   and use it only inside `Migrate` to re-key progress onto QuestieDB ids by exact name match. It is a
   migration artifact, never read for display, and is deleted in the following release. Say so in CHANGELOG.
5. No `pairs()` where order decides what the player sees. Sort explicitly: zones as the client orders them,
   species by id, instances by map id.

## Requirement 4 - a mocked screenshot for every feature, in the README

Standing owner rule: every user-facing feature gets a scene in `tools/mockups.py` and an image under
`docs/screenshots/`, embedded in `README.md` until we publish to Curse and the stores. Needed: the three
journal pages (CREATURES, RARES, SHINY), search with a filter applied, tracking a species, the options panel,
the sighting log, the rarity chrome on target frame and nameplates, one page per zone, the Instances page
with a boss entry, and the no-QuestieDB state.

`tools/visual_audit.py` must report 0 findings over every scene, `tools/check_screenshots.py --record`
re-stamps hashes, and the README gallery is generated from the scene list.

## Gate (must pass locally and in CI)

`stylua --check .` - `luacheck .` - `for s in tests/*_spec.lua; do luajit "$s"; done` -
`uvx ruff@0.16.8 check tools` and `format --check tools` - `python3 tools/check_generated.py` -
`python3 .sift/gate.py --base origin/main` and `python3 .sift/agents.py check` -
`python3 tools/visual_audit.py` - `python3 tools/check_screenshots.py`.

Specs to add: catalogue built from a fixture with no QuestieDB present; catalogue built from a populated
fixture; a boss from an instance appears in its map's group; identical tier across differing progress;
v1 DB migrates by name; corrupt DB loads; save/load round trip identity.

Open one PR against `main`, CHANGELOG entry under a new version, and report the PR number, gate output and
coverage counts (zones, species, instances, bosses from the fixture). Do not merge it yourself.
