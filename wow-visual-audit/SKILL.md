---
name: wow-visual-audit
description: "Use in a WoW addon repo that renders its screenshots from source (cjber's WoW: Forever addons and any addon using wowmock) when a UI change, a README/store screenshot or a layout bug has to be checked against what actually renders. Turns a rendered scene into a gate: every widget inside the frame, no overlapping controls, no art bleeding past an edge, plus the reading order for judging a screenshot by eye. Not for functional Lua tests or in-game behaviour."
---

# Audit a WoW addon's rendered UI

Layout bugs survive every other gate because nothing asserts on what was drawn. Unit tests pass, luacheck is
clean, the image is committed - and two buttons sit on top of each other, or the last one hangs off the frame into
the backdrop. Nobody looked, and nothing was looking.

This is the QA loop Bugpatrol runs against a running app, adapted to an addon whose "running app" is the render
`tools/mockups.py` produces: **look first, measure second, and make the measurement part of CI.**

## The loop

| Role | In an addon repo | Output |
|---|---|---|
| Explorer | render every scene with `python3 tools/mockups.py`, then read the PNGs | one finding per visible defect, with the image and the widget named |
| Judge | measure the same defect (`tools/visual_audit.py`, manifest + pixels) and decide whether it is real | keep or dismiss, with the numbers |
| Fixer | change the shared layout constants - never the PNG | a fresh render that passes the gate |

A finding is only closed when the re-render passes. "Regenerated the screenshots" is not a fix; the layout is.

## 1. Look at the render

View every changed image at full size before reading any code (`read_file` the PNG, or `describe_image` with a
targeted prompt). Ask for the frame's bounds and each control's bounds in the same pass, so an overlap or a bleed
is stated in numbers rather than as a feeling. The defects that reach users are dull and obvious:

- a control that crosses the window frame's inner edge, or hangs outside it into the backdrop;
- two controls that touch, overlap, or sit under 8 units apart;
- text that overruns its box, wraps into the next row, or is clipped;
- a row that lost its baseline with the row above;
- a panel whose content stops short of the frame, leaving a hole the client never draws;
- anything drawn over the close button or the title.

Rule: **a screenshot is evidence of the layout, not decoration for the README.** If an image is in the repo, the
layout in it is what players are promised.

## 2. Measure it

The renderer records the layout it drew, so the audit never guesses at pixels:

```sh
python3 tools/mockups.py          # writes docs/screenshots/*.png and docs/screenshots/layout.json
python3 tools/visual_audit.py     # exits 1 with one line per finding
```

`layout.json` carries the window frame, the canvas and every widget (`name`, `role`, `x`, `y`, `w`, `h`) in the
addon's own units. The audit enforces:

1. every widget inside the frame and on the canvas;
2. interactive widgets (`button`, `tabs`, `input`) never overlap, and keep `MIN_GAP` (8) between them;
3. a widget inside a container (`bar`) keeps `MIN_INSET` (8) from that container's edge;
4. in the pixels, the button art sits inside the frame the image actually shows, in as many pieces as there are
   buttons, at the declared size, with the declared gap - so a manifest that drifted from the drawing code fails.

Copy `scripts/visual_audit.py` into the repo's `tools/` and wire it into CI. It needs Pillow only.

## 3. Fix at the source

Draw from the same numbers the addon anchors with, in one place:

```python
BAR_X, BAR_Y, BAR_W, BAR_H = 18, H - 12 - 58, 924, 58      # UI/Window.lua: BOTTOMLEFT (18, 12), 924 x 58
OPEN_W, OPEN_RIGHT = 112, 158                               # TOPRIGHT -158
TRACK_W, TRACK_RIGHT = 132, 12                              # TOPRIGHT -12
OPEN_X = BAR_X + BAR_W - OPEN_RIGHT - OPEN_W
TRACK_X = BAR_X + BAR_W - TRACK_RIGHT - TRACK_W
```

The bug this skill exists for: the renderer used the addon's *bar-relative* `TOPRIGHT` insets as *window*
coordinates, so both buttons sat ~94 units too far right and the last one ran 26 units past the frame in every
screenshot. Nothing caught it because the numbers were retyped rather than derived.

A rect the addon anchors, the renderer must derive. A number that appears twice will disagree with itself.

## 4. Keep it closed

- CI runs the audit after the screenshot-freshness check: a stale render and a broken layout are different failures.
- `AGENTS.md` says it: never merge a `UI/` change that leaves the audit red.
- When a new widget is drawn, `note()` its rect in the same edit; an unrecorded widget is invisible to the gate.
- Screens the journal does not draw (target frames, nameplates) stay out of `layout.json`'s `scenes` list; the audit
  only judges scenes it has a manifest for.

## Report

State what the image showed, the numbers that proved it, the constant that changed, and the re-render result. If a
defect is visible but cannot be measured yet, add the widget to the manifest rather than writing it off.

See [`references/audit-rules.md`](references/audit-rules.md) for the rule table and the dismissals worth knowing.
