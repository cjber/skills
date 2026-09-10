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

`bd` (beads) — a git-backed graph issue tracker. Workspace root
`/home/cjber/drive/agl`, prefix `neb-`, embedded Dolt at `.beads/`. It sits at
the workspace level, not inside a repo, because the work spans `nebula`,
`parallax`, `nebula-desktop` and the DGX box.

Two companion files live beside it: `alpha-roadmap.md` holds the *reasoning*,
beads holds the *actions*. Keep them in sync — when a track's shape changes,
change both.

`bd prime` prints the full command reference. **One exception to what it says:**
it instructs agents to abandon `MEMORY.md`. Ignore that line — cjber has an
established auto-memory system. Use `bd remember` for project knowledge that
belongs with the work; MEMORY.md keeps its own job.

## `/todos` — the digest

```bash
cd /home/cjber/drive/agl
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
| `/todos board` | publish the dashboard (below) |
| `/todos review` | the weekly review (below) |
| anything else | natural language against the tracker |

## `/todos board` — the visual

```bash
cd /home/cjber/drive/agl
bd export -o /tmp/beads.jsonl
python3 ~/skills/todos/scripts/dashboard.py /tmp/beads.jsonl /tmp/todos.html agent-labs-dev/nebula
```

Then publish `/tmp/todos.html` with the Artifact tool and hand over the link.
Tracks render as threads with issues strung along them as beads, coloured by
state; blocked items show what they wait on; `gh-NNNN` external refs become
links to the real issue. **Republishing:** pass the existing artifact URL as
`url` so it updates in place instead of minting a second board.

## `/todos review` — the anti-slippage pass

Run weekly, or whenever the list feels untrustworthy. Things slip in six
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
   `gh issue view <n> --repo agent-labs-dev/nebula --json state`.
6. **Unlinked roadmap work.** New GitHub issues that belong to a track but have
   no bead. Sweep by track keyword against `gh issue list --state open`, and
   **link, don't duplicate** — GitHub stays the execution tracker, beads is the
   strategic layer that sequences it. Use `--external-ref gh-NNNN` on a new
   bead, or `bd note` on an existing one.

## Rules

1. **File what you discover, when you discover it.** Follow-up work found
   mid-task becomes a bead immediately (`--deps discovered-from:<id>` links it to
   its origin), not a line in a closing message that gets lost. This single habit
   prevents most slippage.
2. **Put the evidence in the description** — file, line, root cause, the command
   that proves it. A bead naming `device_consent.py` and the missing consent tier
   is worth ten restating the symptom.
3. **Claim before working** (`bd update <id> --claim`) so parallel agents don't
   collide. Hash ids are safe across branches and worktrees.
4. **Close what you finish**, batched. Never report work done without closing it.
5. **Don't implement a decision.** Surface it; let cjber call it.
6. **Link, never duplicate.** One fact, one home.

## Commands

```bash
bd ready -n 40 · bd blocked · bd stale · bd status
bd show <id> · bd graph <epic> · bd children <epic>
bd list -l track-g --status=open
bd query 'status=open AND priority<=1'

bd create "Title" --parent <epic> -p 1 -d "Why" --external-ref gh-1234
bd q "quick capture"                # create, print id only
bd update <id> --claim · bd note <id> "..." · bd tag <id> decision
bd dep add <blocked> <blocker> --type blocks
bd close <id1> <id2>
bd remember "insight" · bd memories <keyword>
```

## Handing off

Once an item is picked: `/issue` if it needs a file-level plan, `/pr` to ship it.
Close the bead when the PR merges — not when it opens.
