# Brief: Field Guide Forever - complete mob coverage, and one rarity for every player

Repo: `cjber/bestiary-forever` (addon folder `FieldGuideForever`, Interface 16001, WoW: Forever).
Read `AGENTS.md` and `.agents/skills/sift-project/SKILL.md` in the repo before starting. Owner: @cillian.

## What exists today (measured, 2026-10-21, main @ 3a2353f)

- `Data/Creatures.lua` is hand-written: 10 zones, 183 species, `mob(id, name, family, minLevel,
  maxLevel, lore, rare)`. Zones are The Barrens, Durotar, Mulgore, Teldrassil, Elwynn Forest, Westfall,
  Redridge Mountains, Loch Modan, Tirisfal Glades, Silverpine Forest. Every one is an outdoor
  starting zone. There is no dungeon, raid, boss or Instance entry at all.
- `Core/Model.lua`: `Model.Tier(speciesId)` bands the id (`% 1000 == 0` shiny, `% 100 == 0` gold,
  `% 25 == 0` silver, else copper); `Model.Record` increments count, rare sightings and a
  `math.random(SHINY_CHANCE)` shiny roll per kill.
- `UI/Rarity.lua` paints the target frame and nameplate health-bar trough from `Model.Tier`, i.e. from
  the *catalogue id*, so the rarity colour a player sees for a creature is already player-independent.
  What is per-character is discovery: `entry.count`, `entry.rare` (three sightings) and `entry.shiny`.
- `Core/Core.lua`: `FieldGuideForeverDB` with `db.version = 1`, `db.chars["Name-Realm"]`,
  `db.window`, `db.options`; migration is two ad-hoc `or {}` defaults.
- Tests: `tests/{model,data,api,rarity}_spec.lua` on a headless harness. Mocked screenshots:
  `tools/mockups.py` -> `docs/screenshots/*.png` + `layout.json`, gated by `tools/visual_audit.py`
  (bounds, overlaps, button anchoring) and `tools/check_screenshots.py` (hash freshness).

## Requirement 1 - every mob covered properly

Ship a complete creature catalogue, generated, never guessed:

1. `tools/gen_creatures.py`, standard-library Python, no network at run time: read a **pinned** data
   source committed or cached under `tools/.cache/` (the same shape `adventure-guide-forever` uses:
   pinned CMaNGOS classic-db rows for creature spawns per zone, and the wago.tools DB2 export for
   creature families and levels). Record the source, its version and its hash in the generated file's
   header, as the other generators in the suite do.
2. Coverage: every Classic outdoor zone that has creatures, plus an `Instances` group for every
   dungeon and raid with its bosses as entries. A zone with no data must be absent, not empty.
3. Stable ids: the 183 ids already shipped keep their exact numbers (players have progress saved
   against them). New entries take ids derived deterministically from the source key, and the
   generator refuses to emit a duplicate id or a changed id for an existing name, raising instead of
   renumbering. Same for names: a rename keeps the id and is recorded in the header comment.
4. Deterministic output: two runs byte-identical, ordered by group, then zone, then id. Generators
   raise instead of clamping or filling a guess.
5. Budget: the file must stay inside a sane load cost (the whole suite cares about login time; see
   `forever-handoff/agf-166-login-catalogue-size.md` for the standard the AGF catalogue is held to).
   If the full DB2 set is too heavy, generate a per-zone top-N by spawn weight and say so in the file
   header and the CHANGELOG - do not silently truncate.
6. `tests/data_spec.lua` extended: every species has a zone, family, level range with min <= max, a
   non-empty lore line; ids unique; no duplicate display name inside one zone; the Instances group
   exists and every entry in it is a dungeon or raid creature.

## Requirement 2 - the same rarity for every player, and the same state after every logout

Two players must never disagree about *what kind of creature* something is. Their own progress may of
course differ, and the UI must say which is which.

1. Classification is data, not progress. The rarity tier painted on a nameplate, target frame or list
   row comes only from catalogue data or an id-derived pure function of it - never from
   `db.chars[...]`. Keep `Model.Tier` pure and cover it with a spec that asserts any two states give
   the same tier for the same id. If the generated data can supply an explicit `tier` field, prefer
   it and keep `Model.Tier` as the fallback, documented as such.
2. Personal discovery stays personal and is labelled so in the window ("your record"), so a
   player never reads a personal shiny as a shared fact about the creature.
3. SavedVariables: add `db.version` migration (`SCHEMA` constant, a `Migrate(db)` that walks old
   versions up), normalise every loaded entry once at login (integer counts clamped to
   `0..MASTERED_AT` / `RARE_TARGET` / `SHINY_TARGET`, unknown fields dropped, missing fields defaulted),
   keep the character key stable (`Name-Realm`) and never store a function, metatable or frame
   reference. A corrupt or partially written DB must load as a valid empty state instead of erroring.
4. Deterministic ordering: no `pairs()` where the order decides what the player sees. Sort explicitly
   (zone order as authored, species by id).
5. Specs: save/load round trip is identity for a populated state; a v0/absent DB migrates to the
   current schema; a deliberately corrupted DB loads; two characters' states never cross-contaminate;
   the same id gives the same tier on two states with different progress.

## Requirement 3 - a mocked screenshot for every feature, in the README

Standing rule from the owner: all mocked screenshots live in the README (they move to Curse and the
store listings at publish). Every user-facing feature needs a scene in `tools/mockups.py` and an image
in `docs/screenshots/` referenced from `README.md`:

- the three journal pages (CREATURES, RARES, SHINY); a search with a filter applied; tracking a
  species; the options panel; the sighting log; the rarity chrome on target and nameplates; one page
  per zone; and, once Requirement 1 lands, an Instances page and a boss entry.

`tools/visual_audit.py` must pass over every scene (bounds, overlap, 8-unit gaps, button anchoring),
`tools/check_screenshots.py --record` re-stamps the hashes, and the README gallery is regenerated from
the scene list rather than by hand where practical.

## Gate (all must pass locally and in CI before the PR is offered)

`stylua --check .` - `luacheck .` - `for s in tests/*_spec.lua; do luajit "$s"; done` -
`uvx ruff@0.16.8 check tools` and `format --check tools` - `python3 .sift/gate.py --base origin/main`
and `python3 .sift/agents.py check` - `python3 tools/visual_audit.py` - `python3 tools/check_screenshots.py`.

Open one PR against `main`, keep the CHANGELOG entry under a new version, and do not merge it
yourself: report the PR number, the gate output and the coverage counts (zones, species, instances,
bosses) back in the channel.
