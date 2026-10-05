# forever_tools

Offline, stdlib-only Python (3.10+) shared by the WoW: Forever addon repos. Each repo vendors
`forever_tools/` byte for byte as `tools/forever_tools/`; `MANIFEST.json` holds a sha256 per file and
the producer commit the copy came from.

## Modules

| Module | Does |
|---|---|
| `lua` | Lua 5.1 lexer (`tokenize`, `Token`, `LuaSyntaxError`) |
| `toc` | TOC and nested XML traversal, orphan Lua check per addon `runtime_dirs`, LuaLS coverage gate |
| `multivalue` | `select()` and multi-return expansion lint; `Rules` carries the addon's policy |
| `taint` | Taint lint; `Policy` carries the map openers, frames and getters (`C_Map.OpenWorldMap` is the safe call) |
| `changelog`, `release_check`, `latest_build` | Release gates and the newest Forever build |
| `csvtable`, `wago` | Strict DB2 CSV parsing and cached, validated downloads |
| `fsio` | `atomic_write`, and `publish` for multi-output generators (stage all, replace, roll back on failure) |
| `luadata`, `report` | Read generated Lua tables; the semantic change report |
| `generated` | The fresh-then-offline generated-data gate and `data_report` |
| `sync` | `check`, `update`, `pin`, `manifest` |

A repo's `tools/*.py` entry points stay thin (`changelog.py`, `release_check.py`, `lint_taint.py`,
`lint_multivalue.py`, `typecheck_coverage.py`) and add only per-addon policy such as `RUNTIME_DIRS`.
Addon-specific generators and hints stay in the repo.

## Change and update

1. Edit here and run `python3 -m unittest discover -s tests -t .` and `ruff format . && ruff check .`.
2. `python3 forever_tools/sync.py manifest`, commit, note the commit.
3. In each repo, from a clean producer checkout at that commit:
   `python3 tools/forever_tools/sync.py update --source <producer checkout>`.
   `check` runs offline in `typecheck.sh` and fails on any edited, missing or extra file or an unpinned
   manifest; `check --source <checkout>` also compares with the producer.
