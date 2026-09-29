---
name: todos
description: Show, work through, and keep honest a durable cross-repo workload in the `bd` (beads) graph tracker. Use when the user types /todos, asks what to work on, what's left, what's blocked, what decisions are outstanding, wants a visual dashboard, or asks to add, claim, close, re-prioritise or re-sequence work — and whenever you discover follow-up work that must outlive the session.
---

# todos

The layer above `/issue` and `/pr`: what is worth doing, in what order, and what
is quietly rotting. `/issue` turns one item into a plan, `/pr` ships it. This
skill decides which item, and makes sure nothing falls through the gaps.

**Never** use `TaskCreate`/`TodoWrite` or a markdown checklist for work meant to
outlive the session. Those vanish, which is precisely how things slip.

## The tracker

`bd` (beads) — a git-backed graph issue tracker, with its data in `.beads/`.
The workspace root is `$BEADS_WORKSPACE` when set; otherwise, use the nearest
ancestor of the current directory (including itself) containing `.beads/`.
Run the commands below **from the workspace root**. `bd` discovers `.beads/`
upward; explicitly change to `$BEADS_WORKSPACE` when using that override.
If neither identifies a workspace, ask the user which workspace to use.
A workspace can contain one repo or coordinate work across several repos.

Beads is the only home, with no companion markdown. Cross-cutting strategy
(thesis, operating principle, track sequencing) lives in `bd memories roadmap`.
Each track's reasoning lives in its epic's description and notes. When a track's
shape changes, update the epic. Never start a parallel roadmap doc; multiple
copies drift.

`bd prime` prints the full command reference. **One exception to what it says:**
it instructs agents to abandon `MEMORY.md`. If the user already has an agent
memory system, keep it; use `bd remember` for knowledge that belongs with the
work. `MEMORY.md` keeps its own job.

## `/todos` — the digest

```bash
# From the workspace root
bd ready -n 40 && bd blocked && bd list -l decision --status=open && bd status
```

**Synthesise, never paste.** Render as:

1. **One line of state** — open / ready / blocked / decisions.
2. **Do next** — top items by priority, grouped by track, each with its id.
   Priority is *sequence*, not importance: P0 now, P1 next, P2 parallel, P3 later.
3. **Decisions waiting on you** — say what each one hinges on, in a clause.
4. **Blocked** — only if non-empty, each with what unblocks it.

Lead with what to do. Short enough to read without scrolling.

## Arguments

| Input | Action |
|---|---|
| `/todos <track>` | one track (`bd list -l track-<x>`), same shape |
| `/todos decisions` | the `decision` label, with what each hinges on |
| `/todos blocked` | `bd blocked`, explained |
| `/todos <id>` | `bd show <id>` — detail, edges, notes |
| `/todos add <text>` | create it; infer epic and priority, then say what you chose |
| `/todos close <id>...` | `bd close <id1> <id2>` — always batch |
| `/todos ship` | suggest shippable bundles and let the user pick (below) |
| `/todos ship <id>...` | turn beads into one `/pr` per repo (below) |
| `/todos ship next` | the top `ready-to-build` bead, plus its same-repo cluster |
| `/todos board` | publish the dashboard (below) |
| `/todos review` | the weekly review (below) |
| anything else | natural language against the tracker |

## `/todos board` — the visual

From the workspace root, set `TODOS_SKILL_DIR` to the installed directory
containing this `SKILL.md`, then run:

```bash
bd export -o /tmp/beads.jsonl
python3 "$TODOS_SKILL_DIR/scripts/dashboard.py" /tmp/beads.jsonl /tmp/todos.html
```

The title defaults to the workspace directory name; override it with
`--title "Work Threads"`. Pass an optional third positional argument,
`owner/repo`, to link `gh-NNNN` refs to GitHub issues; without it, links are
omitted. Only supply a repo when those refs belong to that repo. Track names
come from each `track-*` label's epic title, falling back to the label.

Then publish `/tmp/todos.html` with the Artifact tool and hand over the link.
Tracks render as threads with issues strung along them as beads, coloured by
state; blocked items show what they wait on. **Republishing:** pass the existing
artifact URL as `url` so it updates in place instead of minting a second board.

## `/todos ship` — beads into PRs

`/pr` ships an *approved change*, and knows nothing about beads. This is the
handoff between the two.

**No arguments means suggest, don't build.** Run
`bd list -l ready-to-build --status=open` and `bd ready`, drop anything
claimed or already carrying a `PR #` note, and group the rest into
**bundles**: same epic, same repo, one PR each. Then offer 2–4 bundles with
AskUserQuestion (multiSelect, recommended bundle first). Each option is labelled
with the bundle's theme; its description lists the ids, the repo, the rough size,
and why now (priority, what it unblocks, related issues it closes). If
`ready-to-build` is thin, also suggest 1–2 near-ready beads with the one gap
that stops them (e.g. "needs /issue plan"). Ship only what the user picks,
running the steps below.

1. **Gate.** Refuse a bead labelled `decision` (not approved work) or one that
   `bd blocked` lists. `ship next` only picks beads labelled `ready-to-build`:
   the root cause is known and the fix is clear, so it isn't still an
   investigation. When a bead reaches that state, add the label
   (`bd tag <id> ready-to-build`).
2. **Claim** every id: `bd update <id> --claim`.
3. **Brief.** For each bead, combine its description and notes (file, line, root
   cause, proof), its epic's reasoning note (`bd show <epic>`), and the body of
   any linked issue (`gh issue view <n>`). The brief is the approved change.
4. **Batch by repo.** Every id touching the same repo goes into ONE `/pr` run
   (one PR per repo). A cluster that spans repos becomes one `/pr` per repo.
   `ship next` pulls in the top bead's ready siblings under the same epic that
   touch the same repo.
5. **Hand off.** Invoke `/pr` with the brief. The PR body carries
   `Closes #NNNN` once per linked issue (the keyword applies to one issue each).
6. **Record.** As soon as the PR opens: `bd note <id> "PR #NNNN"` on every bead
   it covers. Don't close the bead yet.

## `/todos review` — the anti-slippage pass

Run weekly, or whenever the list feels untrustworthy. Things slip in seven
specific ways; check each, and report only what needs a decision.

1. **Uncaptured.** Scan the session and recent commits for work that was
   discussed or discovered but never filed. File it now.
2. **Stale** — `bd stale`. Filed, untouched, quietly rotting. For each: still
   real? Then re-prioritise or add a note saying why it's parked. Not real?
   Close it. A tracker nobody trusts is worse than none.
3. **Decisions aging.** The highest-leverage thing that silently rots, because
   nothing downstream moves until they're settled. Surface every one older than
   a week and ask directly.
4. **Blocked on nothing** — `bd blocked`. A blocker that is itself unowned and
   unscheduled means the blocked item is parked indefinitely. Either schedule
   the blocker or drop the edge.
5. **Drift both ways.** Beads open for work already done (close them), and
   linked `gh-NNNN` issues closed upstream while the bead stays open:
   `gh issue view <n> --repo <owner/repo> --json state`, using the bead's repo. Also
   open GitHub issues whose fix already merged (a PR fixed them but never
   closed them). **Standing permission:** close stale beads *and* stale GitHub
   issues without asking. Leave a comment naming the evidence (the merged PR or
   commit) with `gh issue close <n> --comment "Fixed by #NNNN ..."`, then report
   what you closed. Only close with evidence. If you're unsure it's really done,
   ask.
6. **Unlinked roadmap work.** New GitHub issues that belong to a track but have
   no bead. Sweep by track keyword against `gh issue list --state open`, and
   **link, don't duplicate** — GitHub stays the execution tracker, beads is the
   strategic layer that sequences it. Use `--external-ref gh-NNNN` on a new
   bead, or `bd note` on an existing one.
7. **PRs in flight.** Beads with a `PR #NNNN` note. Check each with
   `gh pr view <n> --json state,statusCheckRollup`. If it merged, close the bead
   citing the PR (standing permission). If it's closed without merging, un-claim
   the bead and note why. If it's red or untouched for 3+ days, report it.

## Rules

1. **File what you discover, when you discover it.** Follow-up work found
   mid-task becomes a bead immediately (`--deps discovered-from:<id>` links it to
   its origin), not a line in a closing message that gets lost. This single habit
   prevents most slippage.
2. **Put the evidence in the description** — file, line, root cause, the command
   that proves it. A bead naming `parser.py` and the failing input
   is worth ten restating the symptom.
3. **Claim before working** (`bd update <id> --claim`) so parallel agents don't
   collide. Hash ids are safe across branches and worktrees.
4. **Close what you finish**, batched. Never report work done without closing it.
   Closing stale issues (beads or GitHub) never needs approval — close with an
   evidence comment and report it.
5. **Don't implement a decision.** Surface it; let the user call it.
6. **Link, never duplicate.** One fact, one home.

## Commands

```bash
bd ready -n 40 · bd blocked · bd stale · bd status
bd show <id> · bd graph <epic> · bd children <epic>
bd list -l track-<name> --status=open
bd query 'status=open AND priority<=1'

bd create "Title" --parent <epic> -p 1 -d "Why" --external-ref gh-1234
bd q "quick capture"                # create, print id only
bd update <id> --claim · bd note <id> "..." · bd tag <id> decision
bd dep add <blocked> <blocker> --type blocks
bd close <id1> <id2>
bd remember "insight" · bd memories <keyword>
```

## Handing off

Once an item is picked: `/issue` if it still needs a file-level plan (then tag it
`ready-to-build`), `/todos ship` to build it. Close the bead when the PR merges,
not when it opens. Review check 7 does that closing.
