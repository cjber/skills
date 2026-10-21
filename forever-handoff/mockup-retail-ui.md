# Brief - Field Guide mockups: native retail UI parity

Repo: cjber/bestiary-forever. Tooling: `tools/mockups.py` (window scenes) and `tools/rarity.py` (rarity sheets),
both drawn through `tools/wowmock/wowmock.py` against pinned build `1.60.1.70124`. Owner feedback on the current
sheets: "visuals seem quite poor ... make it look clean and as close to native retail UI style as possible".

Read the skill `wow-retail-ui-style` first (agent skill on wow-addons-maintainer; same rules must land as
`skills/wow-retail-ui-style/SKILL.md` in cjber/skills so every addon agent can read it).

## What is wrong now
1. `tools/rarity.py` draws the nameplate from the cooldown-manager atlas (`UI-HUD-CoolDownManager-Bar-BG`) - not a
   nameplate texture at all. Replace with `interface/targetingframe/nameplatefill.blp` plus the plate's own tinted
   background.
2. Bars are flat `canvas.fill` rectangles. Use `interface/targetingframe/ui-targetingframe-barfill.blp` cropped to the
   fill fraction and tinted (that is the client StatusBar texture).
3. Target frame geometry is eyeballed. Measured from `targetframe.blp` (256x128): health window x 32-143 y 26-49,
   power window x 33-143 y 55-61, portrait well centre (183, 44) r 28, level badge centre (201, 66). Anchor the bars,
   the masked portrait and the level text to those, not to hand-picked offsets.
4. Nothing carries the client's font treatment: names/levels must use the `GameFontNormalSmall` /
   `NumberFontNormalSmall` font objects so the 1px shadow comes with them.

## Scope
- Rewrite `tools/rarity.py` to compose the target frame as the client does: trough fills, then bar fills, then the
  circular-masked portrait, then `targetframe.blp` / `targetframeelite.blp` (desaturated + vertex-coloured) on top,
  then text. Variants for rare / rare-elite exist in the same folder if a tier needs them.
- `tools/mockups.py`: audit every control against the rules - `PortraitFrameTemplate` chrome via nine-slice,
  `UIPanelButtonTemplate` buttons, `InputBoxTemplate` search, `PanelTabButtonTemplate` tabs, real subject icons,
  `GameFont*` objects only. Remove any hand-drawn gold hex, 1px border fills or invented diamond glyphs.
- Re-render all of `docs/screenshots/*.png`, update `scenes.sha256`, keep the renderer deterministic.
- Add `tools/wowmock` tests or a `check_screenshots.py` assertion for the new geometry so drift fails CI.

## Definition of done
`python3 tools/rarity.py && python3 tools/mockups.py` is byte-identical on a second run, luacheck/stylua/busted are
green, every screenshot is rendered from client art only, and a reviewer comparing the sheet with the client cannot
tell them apart. Open a PR, do not tag a release.
