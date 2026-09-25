---
name: wow-mock-screenshots
description: Use when a WoW addon (especially cjber's WoW: Forever addons - tweaks-forever, skillup-forever, legacy-here, shortest-path-forever) needs README/store screenshots, or existing screenshots are stale after a UI change, and taking them in game is not wanted. Builds faithful mock screenshots from the client's own UI art, fonts and item data fetched from wago.tools, composed with Pillow, reproducibly from a per-repo tools/screenshots.py.
---

# Mock WoW screenshots from the game's own art

Screenshots taken in game go stale with every UI change and need someone at the keyboard. This skill
renders them instead: the same atlases, textures, fonts, item icons and colours the client uses, laid out
with the numbers from Blizzard's own XML/Lua, and the addon's own drawing reproduced from its source. A
mock is only worth shipping if a player could not tell it from a capture, so accuracy is checked against
real screenshots before anything is committed.

Never launch, focus or send input to the game client to do this.

## Pieces

| Piece | Where |
|---|---|
| Library (fetch/cache, atlases, nine-slice, fonts, items, widgets, `scene`) | `wowmock.py` in this directory; API at the top of the file |
| Gotchas: endpoints, BLP quirks, atlas choice, colours, fonts, widget numbers | [`NOTES.md`](NOTES.md) - read before adding a widget |
| Per-addon scenes | `tools/screenshots.py` in each addon repo, importing wowmock from `$WOWMOCK` or `~/.claude/skills/wow-mock-screenshots` |
| Output | `docs/screenshots/*.png`, referenced from `README.md` and `docs/curseforge.md` |
| Cache | `~/.cache/wowmock/<build>/` (DB2 CSVs, files by fdid, path lookups) |
| Blizzard UI source for layout numbers | `~/drive/proj/wow-handoff/blizzard-ui/Interface/AddOns` |

Requirements: Python 3 with Pillow 12+. Everything else is fetched from wago.tools on first run and cached.

## Workflow

1. **Pick the scenes** from what the README says the addon does: one image per headline feature, showing the
   addon's own UI in the context a player sees it (a bag, a tooltip, a menu, a map, a tracker). Plain dark
   backdrop from `scene()`; never fake a 3D world.
2. **Read the addon's source** for exactly what it draws: textures, sizes, anchors, colours, text, order of
   menu entries. The mock reproduces the code, not the feature description.
3. **Read Blizzard's source** for the frames around it (XML sizes/anchors, NineSliceLayouts, font objects).
   Where a number is engine-side and not in the source, pick it by comparison with a real screenshot and
   note it as an assumption in `NOTES.md`.
4. **Use real data**: real item IDs present in the Forever build's ItemSparse, real names, real icons, real
   stats. Choose content a player of that level would actually carry. Don't invent items, quests or NPCs.
5. **Build the scene** in `tools/screenshots.py` with wowmock widgets. A widget only that addon draws stays
   in the repo script; anything another addon could reuse goes into `wowmock.py`, documented in its header,
   with what you learned added to `NOTES.md`.
6. **Verify**: view each PNG with Read, then crop and enlarge regions side by side with a real in-game
   screenshot of the same kind of frame (the list is in `NOTES.md`) and compare borders, colours,
   text size and baseline, spacing. Iterate until they match. State in the report any place the mock
   still deviates from the real UI.
7. **Reproducibility**: running `python3 tools/screenshots.py` twice must give byte-identical PNGs.
7a. **Animated demo** (`docs/screenshots/demo.gif`) when a headline feature is about motion or time: a
   route settling, a countdown, a sort reordering. Render the frames from the same scene builders
   rather than screen-recording; `render_demo` in shortest-path-forever's `tools/screenshots.py` is the
   template. Render each frame at the GIF's final size (thin strokes and dashes do not survive a
   downscale), quantize every frame to one shared palette built from the first frame plus an enlarged
   crop of the small UI, with no dither, then save with `duration=100, loop=0, optimize=True`. That
   keeps text colours stable, repeated encodes byte-identical and the file under the stores' 2 MB limit.
   Six to ten seconds is enough. It leads the store gallery when it exists.
8. **Ship**: images, the script and the README/store references in the addon repo's PR; library and notes
   changes in a `cjber/skills` commit.

## Rules

- Always pass the build to wago.tools file downloads (`&build=`); without it you get retail art.
- Forever's own art (atlas set 1, "c60") wins where it exists; `NOTES.md` explains the selection rule and
  the tooltip-centre case that proves it.
- Don't draw a mouse cursor. Place hover tooltips and menus where the client anchors them.
- Keep scenes honest: show what the addon does today, with the defaults a new player gets unless the
  image is about an option.
- Put every bar, meter and count at 0 in at least one scene. The client takes a width of 0 as unset, so a
  left-anchored fill set to 0 draws at its art's full width; the layout pass does the same, but only a
  scene with an empty state shows it (Adventure Guide Forever #33 shipped that bug past its mocks).
- When the client build moves, bump `BUILD` in `wowmock.py`, regenerate every repo's screenshots and
  re-verify; art does change between builds.
