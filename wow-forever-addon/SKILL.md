---
name: wow-forever-addon
description: Standards pack for cjber's WoW: Forever addons (legacy-here, skillup-forever, tweaks-forever, shortest-path-forever, any new one) - the numbered requirements every addon repo shares for UI look and feel, assets, README and store pages, code and performance, CI and releases. Load before building or changing an addon's UI, icon, screenshots, README, store page, CI or release process, or when `sift audit` reviews an addon that declares it under `## Standards` in AGENTS.md.
---

# WoW: Forever addon standards

One family, one feel: each addon is a small, fast extension of the default Forever UI that works the
moment it is installed. These requirements are the shared contract. Each repo declares this pack in
its `AGENTS.md` under `## Standards`; `sift audit` reviews against the ids below, and a repo waives one
only in its `AGENTS.md`, with the reason.

Reference implementations: **skillup-forever** for CI and release, **tweaks-forever** for settings.
When this pack and a reference repo disagree, fix whichever is wrong in the same change.

## Requirements

### Product

- **WFA-1** Extend the base game, do not replace it. Add information or an action where the player
  already looks (a Blizzard frame, tooltip, menu, map, tracker, settings page); step aside when
  another popular addon already does the job, and say so in README under "Works alongside".
- **WFA-2** Zero setup. Every feature works out of the box: no required settings, extra downloads
  or companion installs. Data ships in the release zip (`.pkgmeta` `move-folders` for a
  load-on-demand data addon). Anything off by default is off because it acts for the player.
- **WFA-3** Minimal surface. Options live in one place: a Settings > AddOns page (Blizzard's
  settings API), or a menu on the addon's own UI when every option is about that UI (Legacy Here's
  map menu). A slash command (short form plus the full name) and an addon compartment entry
  (`## AddonCompartmentFunc`) both open it. No minimap button, no custom options window.

### UI

- **WFA-4** Looks like the retail default UI. Stock frame templates, `GameFont*` objects, atlases,
  `GameTooltip`, `MenuUtil` menus, `MapCanvasDataProviderMixin` pins — copied from the Blizzard
  source for the Forever build (Gethe/wow-ui-source, branch `forever`). Never custom-styled frames,
  fonts or colours; addon-drawn art only where no atlas exists, in the atlas's palette.
- **WFA-5** Objective tracker sections sit above quests with a unique negative `uiOrder`. Registry:
  Legacy Here `0` and `-1`, SkillUp Forever `-2`, Shortest Path Forever `-3`. A new addon takes the
  next free number and adds it here. Attach by hooking `ObjectiveTrackerManager:AddContainer`.
- **WFA-6** Copy talks to the player in the game's voice: short, plain, no jargon or internal names.
  After an update, tell them to `/reload`, never to restart the game.

### Assets

- **WFA-7** One icon family. `media/icon.svg` starts from [icon-template.svg](icon-template.svg):
  gold rounded frame, warm-brown radial background, a single centred emblem in the gold palette
  with the template's drop shadow and outline. Colour inside the emblem only where it carries
  meaning (difficulty colours, a tick). No scenes or alternative backgrounds.
- **WFA-8** Icon files are rendered, not hand-exported: `python3 <this skill>/render_icon.py`
  writes `media/icon-400.png` (README, store logo) and `media/Icon.tga` (64 px). The TOC uses
  `## IconTexture: Interface\AddOns\<Addon>\media\Icon`.
- **WFA-9** Screenshots come from `tools/screenshots.py` via the `wow-mock-screenshots` skill, one
  per headline feature, regenerated in the same PR as any UI change they show. README, store page
  and store gallery use the same files from `docs/screenshots/`.

### Docs

- **WFA-10** README shape: centred 96 px icon, `<h1 align="center">`, one-line pitch, CI and
  release badges; then Features, Install, Usage (slash commands), optional sections for how the
  numbers or data work, Works alongside, Development, Licence. Under 1,200 words: a feature is one
  bullet led by a bold name, at most ~60 words; depth moves to `docs/`.
- **WFA-11** `docs/curseforge.md` is the store description: the pitch, the headline screenshots,
  Features, Usage, a source/licence line; under 600 words; no Install or Development sections. It
  is pasted into CurseForge and Wago by hand after it changes (`wow-addon-publish`).
- **WFA-12** `CHANGELOG.md` follows Keep a Changelog with prose: `## [Unreleased]` on top,
  `## [x.y.z] - YYYY-MM-DD`, bullets led by a bold sentence then why it matters, in player terms.

### Code and performance

- **WFA-13** Fast in both senses: time to a result and per-frame cost. Benchmark the short and long
  case before and after a change to a hot path; no frame over 3 ms; no idle `OnUpdate` or timers;
  bounded work per event.
- **WFA-14** Saved variables never assume a key: every default is declared in one place (a
  `DEFAULTS` table, or the feature registry's `default =`), and a missing key reads as its default,
  so a new option and an old save file always agree.

### Build, CI and release

- **WFA-15** CI covers at least the skillup-forever baseline: actions pinned to full SHAs with a
  version comment, `persist-credentials: false`, `permissions: contents: read`; luacheck, every
  `tests/*_spec.lua` under LuaJIT (a glob, so a new spec cannot be left out), StyLua `--check`,
  ruff for the Python tools, actionlint and zizmor, gitleaks over the full history, and
  `sift agents`. Extra checks (lua-language-server, shellcheck) are welcome. Downloaded binaries
  are pinned by sha256. Dependabot updates `github-actions` monthly, grouped.
- **WFA-16** Releases: a signed `v*` tag runs `release.yml` (BigWigs packager, pinned) with this
  version's CHANGELOG entry as notes (`tools/changelog.py`), uploading to GitHub, CurseForge and
  Wago; the TOC carries `X-Curse-Project-ID` and `X-Wago-ID`. Setup is in `wow-addon-publish`.
- **WFA-17** Every repo has a lean `AGENTS.md` passing `sift agents` in CI, declaring this pack.
  Game-client verification the agent cannot do (in-game look, combat behaviour) is listed in the PR
  as a `/reload` test for the user; agents never drive the game.
