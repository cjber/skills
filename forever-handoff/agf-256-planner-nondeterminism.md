# AGF #256: fix the planner rebuild nondeterminism on QuestieDB v1.0.7

Repo: cjber/adventure-guide-forever. Branch from current origin/main (20720be).
Supersedes the diagnosis in forever-handoff/agf-256-refresh-questiedb-1.0.7.md (keep that task, add this root cause).

## Repro (verified)

```sh
git worktree add --detach /tmp/agf-fix main && cd /tmp/agf-fix
python3 tools/refresh_pins.py            # QUESTIEDB_TAG v1.0.6 -> v1.0.7
python3 tools/gen_quests.py && python3 tools/diff_forever.py && \
python3 tools/gen_zoneart.py && python3 tools/gen_corpus.py && \
python3 tools/catalogue_revision.py --write
luajit tests/laps_spec.lua               # 531776 checks, 2 failed
```
Both failures are the Stability invariant `Keys(third, key) == Keys(again, key)`
(`again = Plan(..., last=first)`, `third = Plan(..., last=again)`):
- seed 4, character 56 (level 10 at 1426:0.8628:0.4881)
- seed 12, character 42 (level 21 at 1413:0.3526:0.2788)

Reproduce one alone with `AGF_LAPS_SEED=4 luajit tests/laps_spec.lua` (add a temporary
`CHARACTERS=56` cap and `SEEDS={4}` to iterate in ~13 s instead of 4 min).

## Root cause (confirmed with instrumentation)

The rebuild does not reach a fixed point: the route oscillates 10 -> 8 -> 10 steps for
seed 4 char 56, because `Planning/Laps.lua` `Verify()` over-reserves quest-log capacity.

`Verify` walks the re-committed steps simulating the client log (`cap = player.logMax`,
`left` = slots held). For a **new** pickup it requires `left + owed < cap`, where
`owed` counts the committed pickups (`lap.picked`, i.e. the previous route's
`order.picked`) still ahead in the step list. For a committed pickup it only requires
`left < cap`.

`lap.picked` is every town pickup of the previous route. A route with `logMax = 4`
legitimately picks up 7 quests, because hand-ins along the way free slots. So
`#picked (7) > cap (4)`, and the reservation "leave room for all 7 committed pickups at
once" is unsatisfiable — every new pickup is rejected, the towns empty, and `Verify`
drops those steps.

Trace of the three builds (`VERIFY-HEAD n=<steps> count=<log> cap=<logMax> pickedN=<#picked> owed0=<initial owed>`):

```
first  (last=nil):    walk 30 -> commit 26 -> route 10, order 26
again  (last=first):  VERIFY-HEAD n=30 count=0 cap=4 pickedN=7 owed0=7  -> route 8,  order 8
third  (last=again):  VERIFY-HEAD n=30 count=0 cap=4 pickedN=6 owed0=6  -> route 10, order 28
```

The collapsed `again` route commits the smaller `picked` set (6), so `third`'s
reservation is satisfiable and the route grows back to 10 — a period-2 cycle. `first`
(no committed order, `picked={}`) and `third` both reach 10; only the middle rebuild
shrinks. That is exactly the "rebuild with nothing changed keeps the route" invariant
failing.

The committed order for `first` holds 26 idents (10 route steps + 16 steps past
`Model.MAX_STEPS`, which `MergeLapVisits` deliberately keeps). That is by design and is
not itself the bug; the bug is the capacity reservation in `Verify`.

## What to fix

Fix the reservation in `Planning/Laps.lua` `Verify()` so a committed route that is
walkable stays walkable on rebuild. The reservation must not require room for more
committed pickups than the log can hold at once: it has to account for the committed
hand-ins ahead that free slots (e.g. reserve only the peak excess of committed pickups
over committed hand-ins still ahead, instead of the raw count), so new pickups in held
steps are not rejected when the committed pickups ahead will not coexist.

Constraints:
- Do NOT loosen, skip or delete the stability check, and do NOT touch `tests/golden/`.
- Keep the QuestieDB pin at v1.0.7 (`tools/gen_corpus.py` QUESTIEDB_TAG/SHA256) and the
  regenerated `Data/` from the repo's own generators. Never hand-edit generated data.
- Preserve the committed-order semantics of docs/design.md §4.3.

## Gate (all must pass locally with v1.0.7)

```sh
luacheck .
for s in tests/*_spec.lua; do luajit "$s" || exit 1; done     # laps_spec included (~4 min)
luajit -joff tests/plan_bench.lua
python3 tools/check_generated.py --offline
stylua 2.5.2 --check .
ruff format --check tools && ruff check tools
python3 tools/changelog.py --check
# generator unit tests
python3 tools/gen_corpus_test.py && python3 tools/gen_quests_test.py && \
python3 tools/gen_zoneart_test.py && python3 tools/diff_forever_test.py && \
python3 tools/catalogue_revision_test.py && python3 tools/refresh_pins_test.py && \
python3 tools/check_generated_test.py
```

## Deliverable

ONE PR to cjber/adventure-guide-forever main carrying the v1.0.7 pin bump, the
regenerated `Data/`, the `Planning/Laps.lua` fix and a `CHANGELOG.md` **Unreleased**
line. Commit without `-s`. Report the PR number, the root-cause explanation and the
exact local gate output. Do not merge.
