# AGENTS.md

Atlas Forever targets the WoW: Forever client (Interface 16001). It is the suite's map surface: a browsable atlas of
every map the client has, a live coordinate readout, and bookmarks that set the game's own waypoint. It never routes,
never chooses what to do, never owns another addon's pins, and never touches protected functions.

Read `forever-handoff/boundaries.md` in [cjber/skills](https://github.com/cjber/skills) before adding a feature: it
says which addon owns what, and this file only says how to write code here.

## Commands

```sh
stylua --check .
luacheck .
for spec in tests/*_spec.lua; do luajit "$spec" || exit 1; done
uvx ruff@0.16.8 check tools && uvx ruff@0.16.8 format --check tools
python3 tools/changelog.py --check
```

Specs are Lua 5.1 scripts run with LuaJIT through `tests/wow_mock.lua`, a headless client with inert frames and
hand-delivered events. `tools/` holds development tooling, which `.pkgmeta` keeps out of the package:
`tools/changelog.py` prints or checks a release's entry, `tools/check_package.py` checks what the packager built, and
`tools/release_check.py` gates the release on a green full CI run.

## Layout

- `AtlasForever.toc` is the client's runtime file list and load order. Files sit at the repository root or in one of
  the flat folders below; no other nesting.
- `Locales/enUS.lua` contains every player-visible phrase. UI code uses `L["whole sentence"]`, never a bare string.
- `Core/Model.lua` is pure: bookmark arithmetic, coordinate formatting and search, with no WoW API, no frames and no
  globals beyond `ns.Model`.
- `Core/Core.lua` owns the saved variables, the ready callbacks (`ns.OnReady`) and the slash command. Event handlers
  go through `Core/SafeCall.lua` so one bad row cannot take the addon down.
- `Core/API.lua` is the versioned addon-to-addon contract, read as `AtlasForever.API`. It answers `nil` until saved
  state exists: a caller asks again after `PLAYER_LOGIN` instead of reading silence as "nothing here".
- `UI/` holds the window and its views. `UI/Art.lua` owns frame helpers and the palette; the other files own one view
  each.

## Scope

Owns: the atlas window (browse continents, zones, dungeons and raids the client has, with a breadcrumb and search),
the coordinate readout, bookmarks, and setting the client's user waypoint.

Never: route or order travel, estimate flight, boat, zeppelin or portal time (`shortest-path-forever`), choose quests
or judge eligibility (`adventure-guide-forever`), own pins for a place type another addon registers (`forever-core`
marker contract), shade exploration or track completion (`legacy-forever`), or show loot and boss tables
(`adventure-guide-forever` owns AtlasLoot lookups).

## Rules

- Runtime code targets Lua 5.1. Keep new globals limited to SavedVariables, the public API table, and the
  client-required slash globals.
- The addon works with nothing else installed. When another addon is present, use its API and keep a fallback that
  works without it; never make an integration the only path.
- Keep `Core/Model.lua` pure and keep its specs free of a client.
- Never hand-write map, instance or zone data. Read it from the client's own `C_Map` API; a place the client does not
  report is absent, not invented.
- Keep SavedVariables flat and serialisable: no frames, functions, userdata, or caches of client tables.
- Do not hook Blizzard methods. Every change must be safe for secure UI and taint.
- Use tabs, annotations, `local addonName, ns = ...`, the established palette and Blizzard fonts. Add a
  `read_globals` entry to `.luacheckrc` only for a genuine client API, never to hide a real warning.
- Every user-facing feature gets a mocked scene and a README screenshot before it ships. Screenshots live strictly in
  the README for now; they go to CurseForge and Wago once the addon is published.
- Do not edit `.pkgmeta` to include development-only tools, tests, or screenshots.

## Release flow

Keep changes under an appropriate `CHANGELOG.md` version heading, run the full gate, and check the packaged TOC
contents before releasing. The BigWigs packager reads `.pkgmeta`, substitutes the release version in the TOC, and
publishes the changelog entry as release notes. Commit without `-s`; signing is handled by GitHub.
