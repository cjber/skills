---
name: wow-forever-addon
description: Standards pack for cjber's WoW: Forever addons (legacy-forever, skillup-forever, tweaks-forever, shortest-path-forever, any new one) - the numbered requirements every addon repo shares for UI look and feel, assets, README and store pages, code and performance, CI and releases. Load before building or changing an addon's UI, icon, screenshots, README, store page, CI, release process or GitHub repo settings, or when `sift audit` reviews an addon that declares it under `## Standards` in AGENTS.md.
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
  settings API), or a menu on the addon's own UI when every option is about that UI (Legacy Forever's
  map menu). A slash command (short form plus the full name) and an addon compartment entry
  (`## AddonCompartmentFunc`) both open it. No minimap button, no custom options window.

### UI

- **WFA-4** Looks like the retail default UI. Stock frame templates, `GameFont*` objects, atlases,
  `GameTooltip`, `MenuUtil` menus, `MapCanvasDataProviderMixin` pins — copied from the Blizzard
  source for the Forever build (Gethe/wow-ui-source, branch `forever`). Never custom-styled frames,
  fonts or colours; addon-drawn art only where no atlas exists, in the atlas's palette.
- **WFA-5** Objective tracker sections sit above quests with a unique negative `uiOrder`. Registry:
  Legacy Forever `0` and `-1`, SkillUp Forever `-2`, Shortest Path Forever `-3`, Adventure Guide Forever `-4`. A new addon takes the
  next free number and adds it here. Attach by hooking `ObjectiveTrackerManager:AddContainer`.
- **WFA-6** Copy talks to the player in the game's voice: short, plain, no jargon or internal names.
  After an update, tell them to `/reload`, never to restart the game.
- **WFA-26** An audio cue is the sound the game itself makes for that thing: a ship's dock bell for a
  boat, the zeppelin's horn for a zeppelin. Never a raid warning, ready check or PvP alert, which mean
  something else to a player. Find it in the Forever build's listfile on wago.tools, check it exists with
  `/api/casc/<FileDataID>?build=`, and play it with `PlaySoundFile(<FileDataID>, "Master")` beside a
  comment naming the file.
- **WFA-27** Never stretch art. An icon, atlas or texture is drawn at its native aspect: size it from
  `C_Texture.GetAtlasInfo` and fit it inside its box, centred, never anchor or size it to a box of another
  shape. Inline markup (`CreateAtlasMarkup`, `|A`, `|T`) takes whole pixels, so pick sizes within 2% of the
  native shape and comment the native size. File icons are square; account for any texcoord crop. Only
  nine-slice pieces, bars, fills, colour textures and masks stretch by design. Each repo's `AGENTS.md`
  carries this rule under Rules.

### Assets

- **WFA-7** One icon family. `media/icon.svg` starts from [icon-template.svg](icon-template.svg):
  gold rounded frame, warm-brown radial background, a single centred emblem in the gold palette
  with the template's drop shadow and outline. Colour inside the emblem only where it carries
  meaning (difficulty colours, a tick). No scenes or alternative backgrounds.
- **WFA-8** Icon files are rendered, not hand-exported: `python3 <this skill>/render_icon.py`
  writes `media/icon-400.png` (README, store logo) and `media/Icon.tga` (64 px). The TOC uses
  `## IconTexture: Interface\AddOns\<Addon>\media\Icon`, and so does every child addon the zip
  ships (load-on-demand data or map addons), pointing at the parent's icon, so none shows a `?`.
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
- **WFA-23** One pitch for the family: the addon looks like it came with the game. The README
  pitch, store description and any post say so early, backed by something concrete from this addon,
  then that it steps aside for addons you already run. The lead image shows it looking native,
  against the stock UI where the change is subtle. See [voice.md](voice.md).
- **WFA-24** Store copy, README and posts read like cjber wrote them, never like AI marketing:
  first person where it helps, short plain sentences, British spelling, undersold, concrete, one
  honest limit. [voice.md](voice.md) is the rule set; `python3 <this skill>/check_copy.py
  docs/curseforge.md README.md` must pass before a store paste or post.
- **WFA-25** No two images stacked without words between them, in the README or the store page. Each
  image, or row of images in one `<p>`, gets a line under it saying what to look at in plain words,
  not a copy of its alt text. `check_copy.py` flags a stacked pair. Two things that belong side by side
  are one image, composed in `tools/screenshots.py` as one `scene()` with both widgets as layers.
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
  lua-language-server, ruff for the Python tools, actionlint and zizmor, and gitleaks over the full
  history. Extra checks (shellcheck) are welcome. Downloaded binaries are pinned by sha256. A job
  named `sift` runs the vendored `python3 .sift/gate.py --base "origin/$BASE"` and
  `python3 .sift/agents.py check`; `sift setup` vendors both and `sift update` refreshes them.
  Dependabot updates `github-actions` monthly, grouped.
- **WFA-16** Releases: a signed `v*` tag runs `release.yml` (BigWigs packager, pinned) with this
  version's CHANGELOG entry as notes (`tools/changelog.py`), uploading to GitHub, CurseForge and
  Wago; the TOC carries `X-Curse-Project-ID` and `X-Wago-ID`. Setup is in `wow-addon-publish`.
- **WFA-17** Every repo has a lean `AGENTS.md` passing `python3 .sift/agents.py check`, declaring
  this pack at a full commit SHA. Game-client verification the agent cannot do (in-game look, combat
  behaviour) is listed in the PR as a `/reload` test for the user; agents never drive the game.

### Repository

- **WFA-18** CI job names are the same in every repo, because the ruleset (WFA-21) requires checks
  by exact name: `check` (luacheck, StyLua, the specs), `typecheck` (lua-language-server),
  `secrets` (gitleaks), `workflows` (actionlint, zizmor), and `python` (ruff) only when
  the Python tooling is big enough to earn its own job. Rename a job and its required check
  together.
- **WFA-19** `refresh-data.yml`, where a repo has one, dispatches `ci.yml` on the branch it opens
  (`gh workflow run ci.yml --ref <branch>`, `actions: write`; `ci.yml` accepts
  `workflow_dispatch`), so the new data is tested at once. A PR opened with `GITHUB_TOKEN` gets
  its `pull_request` CI only as runs awaiting approval, and a dispatched run never counts toward
  required checks: approve those runs from the PR's merge box before merging.
- **WFA-20** `.gitattributes` normalises text to LF and marks generated data files
  `linguist-generated`, so their diffs collapse in review. Community health files (contributing,
  security policy, issue and PR templates) are inherited from `cjber/.github`; a repo carries its
  own copy only to override one.
- **WFA-21** `main` is protected by one ruleset: force-push and deletion blocked; changes land by
  PR with 0 required approvals and all review threads resolved; the WFA-18 checks required by
  exact job name, not strict (a branch need not be up to date); signed commits; linear history;
  squash the only merge method. Repository admins bypass it. A private repo on the free plan
  cannot have rulesets; add it when the repo goes public.
- **WFA-22** Repo settings: delete branch on merge; wiki and projects off; Dependabot alerts and
  security updates on; private vulnerability reporting on (public repos only); Actions may create
  pull requests (for WFA-19); Actions require full-SHA pinning; topics `wow-addon`,
  `world-of-warcraft`, `wow-forever`, `lua` plus one or two for what the addon does.
