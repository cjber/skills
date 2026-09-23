# skills

Claude Code skills I actually use, kept here so they can be shared. One per
directory, each a self-contained `SKILL.md` plus whatever tooling it needs.

| Skill | What it's for |
|---|---|
| [`pr`](#pr--ship-one-green-pr-on-two-models) | Take an approved change all the way to a reviewed, green PR — planned, implemented and reviewed on two different models. |
| [`deadcode`](#deadcode--prove-it-dead-before-you-delete-it) | Clean up a whole project without shipping a silent breakage. The judgment layer on top of `vulture`/`knip`/`ts-prune`. |
| [`issue`](#issue--from-a-github-issue-to-a-plan-or-a-whole-backlog-to-one-pr) | Turn a GitHub issue into a file-level plan — or triage the entire open backlog into a single PR that closes all of it. |
| [`simplify`](#simplify--make-the-diff-smaller-before-anyone-reviews-it) | Shrink a finished diff without changing behaviour, so reviewers read the change and not the scaffolding. |
| [`review`](#review--one-diff-one-pass-a-budget) | Review a diff, branch or PR for defects that actually execute — with an explicit cap on what it is allowed to spend. |
| [`todos`](#todos--a-workload-that-does-not-leak) | Keep a durable cross-repo workload honest: what to do next, what is blocked, what decision is rotting, and a board you can look at. |
| [`autopsy`](#autopsy--account-for-every-second-of-one-agent-run) | Forensic audit of one LLM agent run: rebuild the full timeline from traces, events and logs, and list every harness, tool, model and environment defect with evidence and a fix. |
| [`wow-mock-screenshots`](#wow-mock-screenshots--addon-screenshots-without-the-game) | Render WoW addon README/store screenshots from the client's own art, fonts and data instead of capturing them in game. |

They are designed to work together — `/todos` decides what is worth doing next,
`/issue` produces the plan, `/pr` ships it, and `/pr` calls `/simplify`,
`/review` and `/deadcode` at its quality gates — but each one stands alone.

---

## `pr` — ship one green PR, on two models

`/pr` takes an approved change and drives it all the way to a reviewed, green
pull request: plan, isolate, implement, simplify, review, publish, and then sit
on CI until it goes green and every review comment has a reply.

What makes it different from "write the code and open a PR" is that every
judgment phase runs **twice, on two different models** — one Claude arm and one
Codex arm — and they critique each other exactly once before a single synthesis
turn resolves the disagreement.

The point is not more compute. It is that a second model does not share the
first one's assumptions, so it catches the class of mistake self-review
structurally cannot: the thing you were confident about. A *cheaper* second
opinion is worse than none, because shallow agreement reads as corroboration —
which is why the Codex arm is pinned to high reasoning effort throughout.

It is deliberately **not** a fan-out. Two arms, no scouts, no agent teams, no
nested subagents, no recursion. Every phase is bounded.

### The shape of a run

| Phase | What happens |
|---|---|
| **1. Plan** | Both models plan the same target independently, exchange *only* corrections, then one turn synthesizes a single plan. |
| **2. Isolate** | A worktree branched from fresh `origin/main`. Stacking requires a real dependency, not just an open branch. |
| **3. Implement** | The plan splits into two **disjoint** file-ownership slices, worked concurrently. Claude is the only git owner. |
| **4. Simplify + review** | Simplify the diff, clear the dead code the diff itself created, then two independent reviews that exchange only exclusive findings. |
| **5. Commit + publish** | Signed Conventional Commits, one ready-for-review PR per repo. |
| **6. Drive it green** | CI to completion, and *every* comment — bots included — gets a posted reply. A second review pass runs concurrently with CI rather than polling it. |
| **7. Merge** | Never on its own initiative. Merging needs the user to say so, for these specific PRs, now. |

### The opinions worth knowing about

Most of the file is hard-won operational detail. A few rules carry the most weight:

- **Fix a verified finding in this PR.** Filing an issue is not a resolution.
  Catching yourself writing "tracked separately" about something you have already
  verified and could fix is a stop-and-fix signal, not an outcome.
- **Never run the full test suite locally.** Run the one test that proves the fix;
  push and let CI be the test gate.
- **Every push reopens the comment window** — bots re-run and humans read the new
  head, so the sweep repeats after each push rather than happening once.
- **A green PR left unmerged is the expected end**, not an unfinished task.
- **Never `gh pr update-branch`** — it strips commit signatures. Rebase locally so
  `commit.gpgsign` re-signs.

There is also a full section of `codex exec` landmines, every one learned the
expensive way. The big one: `codex exec` blocks forever waiting on stdin whenever
stdin is not a TTY, having printed only `Reading additional input from stdin...`
— and it can exit **0** while doing nothing at all. Every invocation in the skill
redirects stdin for that reason.

### The watch scripts

Both take the state directory of a running `codex exec`, and both are optional.

- **`pr/scripts/watch_human.sh <STATE_DIR>`** — a live tail of the Codex arm's
  progress for *you*, in your own terminal. It never passes through the
  assistant, so watching costs zero tokens.
- **`pr/scripts/watch_digest.sh <STATE_DIR> [POLL_SECONDS] [START_LINE]`** — a
  bounded periodic digest for the assistant to monitor: one summary per interval
  instead of one notification per event, plus rate-limit and token usage read out
  of Codex's own rollout session file (the `exec --json` stream carries no usage
  data at all).

Both need `jq`.

---

## `deadcode` — prove it dead before you delete it

`/deadcode` is for cleaning up a whole project: removing dead code, unused
imports, orphaned files and dependencies, and consolidating duplicated
implementations into one source of truth.

The premise is that the tools are the easy part. `vulture`, `ruff`, `knip`,
`ts-prune` and `depcheck` produce *candidates*; the skill is the judgment that
turns a candidate into a safe deletion.

- **The absence of a reference is not proof of death.** A symbol with zero static
  call sites can be reached by dynamic dispatch, exported as public API, invoked
  from ops or docs, looked up by string from config, or reached from another
  service entirely. A missing grep hit is often the *symptom* of dynamic access.
- **And it cuts both ways: name-based scanners also MISS dead code.** They count a
  symbol as "used" if any file names it — including another already-dead module,
  or a test. So they are blind to dead islands and dead-referenced-by-dead chains.
  "It didn't show up in vulture" is not evidence of life.
- **Referenced only by a test is product-dead.** The symbol and its test are the
  dead pair; both go.
- **Cleanup is a behaviour-preserving change**, and "looks equivalent" is not "is
  equivalent".

It runs analyze → prove-dead → prioritized plan → **approval** → apply → verify,
and the approval gate is unconditional: "obviously dead", "trivial" and "it's
only formatting" are the rationalizations the gate exists to stop.

There is a companion [`cleanup-report-template.md`](deadcode/cleanup-report-template.md)
for the final write-up.

### On languages

The *judgment* is language-agnostic and the skill names TypeScript and Python
tooling alike. Two parts are not:

- The **module-reachability pass** it recommends is written around
  [`grimp`](https://github.com/seddonym/grimp), which is **Python-only**. In
  another ecosystem you need that layer's equivalent (`knip` gets closest for
  TS/JS) — it is the layer that catches whole dead files a name-scanner rates
  "used", so don't just drop it.
- `uv run dead-code` and `uv run sift deadcode`, referenced in both skills, are
  **my repo's own Python/uv runners** — a tuned vulture pass plus that
  reachability pass with the roots and allowlist already wired. They will not
  exist in your project. Substitute your own entrypoint.

---

## Install

Personal, available in every repository:

```sh
git clone https://github.com/cjber/skills.git
cp -r skills/pr skills/deadcode ~/.claude/skills/
```

Or for a single project, copy them into `.claude/skills/` in the repo root.

Then invoke as `/pr` and `/deadcode` — or just describe the task ("ship this",
"clean up this project") and Claude will pick them up.

## Requirements

- **Claude Code**
- **[Codex CLI](https://github.com/openai/codex)**, signed in — the second arm of `/pr`
- **`gh`**, authenticated — PR creation, checks, and comment threads
- **`jq`** — only for the two watch scripts
- Signed commits configured (`commit.gpgsign`); `/pr` assumes every commit is signed

---

## `issue` — from a GitHub issue to a plan, or a whole backlog to one PR

`/issue` has two modes, chosen by whether you passed it issue numbers.

**With numbers** (`/issue 3765`, or several at once) it is planning only: it reads
the issue, reads the code the issue is actually about, and writes a concrete
file-level implementation plan to `~/.claude/plans/`. No branches, no commits.
The output is something you can hand to `/pr`.

**With no arguments** it triages the entire open backlog: pulls every open issue,
clarifies scope with you — pushing for the largest batch you will accept — plans
the batch in parallel, then builds it **serially** onto one branch as one signed
commit per issue, and opens a single PR that closes all of them.

### Why the two phases have different shapes

Planning fans out because plans do not touch a shared resource. Building does
not, and the asymmetry is the whole design:

- **One branch, one PR, one commit per issue.** A stack of tiny interdependent
  PRs is worse to review than one coherent PR whose history explains itself.
- **A red gate drops that issue to plan-only.** It does not get a
  "best effort" commit. Revert its edits, leave the branch clean, record the
  blocker, move on — the batch keeps its green history and the dropped issue
  keeps its plan.
- **Explicit file lists, never `git add -A`.** A serialized build shares a
  worktree across issues; `-A` is how one issue's commit swallows the next one's
  half-finished edits.
- **The build is serialized because local checks share state.** If your check
  gate touches one local database across every worktree, concurrent builds
  corrupt each other's results rather than failing honestly.

---

## `simplify` — make the diff smaller before anyone reviews it

`/simplify` runs on a finished diff and does one job: make it smaller and clearer
without changing behaviour. It does not review, commit, or push.

The order it works in is the point — deletions first, then unification, then
abstraction collapse, then tests and comments:

1. Delete what is unreachable, redundant, speculative or superseded. **Never**
   behind a "remove in a follow-up" note — if this diff killed the last reader,
   this diff deletes it.
2. Extend the highest existing authoritative seam instead of adding a parallel one.
3. Replace hand-rolled parsing, retry, caching or validation with the trusted
   library already in the lockfile.
4. Collapse abstractions with one caller or no independent contract.
5. Keep one test per distinct realistic failure.
6. Cut comments that narrate the next line; keep the ones carrying incident
   rationale.

### The guardrail that makes it safe to run

A simplifier with no floor will happily delete your authorization checks. So there
is a hard stop: never reduce authorization, tenant isolation, billing,
persistence, concurrency, cancellation, migrations, or supported stale-client
compatibility merely to shrink the diff — and never use simplification to erase a
regression test for one of them.

It also refuses reductions that only *look* smaller: a candidate that is longer,
less typed, or less explicit is rejected unless it buys a real deletion somewhere
else.

[`references/review-rubric.md`](simplify/references/review-rubric.md) is the long
form — whole-system duplication, dependency leverage, control flow, indirection,
tests, and operational residue. The skill reads it only for a broad or
structurally complex diff.

---

## `review` — one diff, one pass, a budget

Most review skills fail by being too expensive to actually run, so you stop
running them. `/review` starts from a **resource budget** and works inward:

- Use the current model at medium effort. Do not force the biggest model.
- No parallel reviewers, no agent teams, no cross-reconciliation loops.
- Exactly one fresh-context second pass, allowed *only* for security,
  authorization, billing, migrations and data loss, concurrency, or a diff too
  large to hold in one coherent pass — and scoped to that risky area rather than
  repeating the whole review.

The review itself prioritizes **defects that execute**: wrong results, broken
security boundaries, data loss, races, compatibility failures. Every candidate is
validated against the surrounding code before it is reported, and style
preferences are dropped rather than listed. Findings come back as
`file:line` + the defect + a concrete failure scenario + the smallest viable fix,
followed by what was actually checked and what remains uncertain.

If nothing survives validation it says so plainly, which is the outcome that makes
the budget credible.

## Adapt before you use these

These are my working copies, not neutral templates. They hardcode the gates and
habits of the repository I use them in, and those are the first lines to change:

- `uv run sift check` and `uv run dead-code` are that repo's lint/type and
  dead-code gates. Substitute your own.
- `gpt-6-astra` is the Codex model pin. Model names move; check yours.
- The `cb/<slug>` branch convention and `gh stack` for stacked PRs are personal
  habits, safe to drop.
- `/deadcode` illustrates its rules with worked examples from that same private
  codebase, marked `(nebula: ...)`. They are there to show the *shape* of each
  reachability trap, not because you need that repo — read them as examples and
  map them onto your own stack.

Everything else — the two-arm structure, the review discipline, the codex
gotchas, the reachability rules, the CI and comment loops — is portable as
written.

## `todos` — a workload that does not leak

`/todos` is the layer above the rest: what is worth doing, in what order, and
what is quietly rotting. `/issue` turns one item into a plan and `/pr` ships it;
this skill decides *which* item, and makes sure nothing falls through the gaps.

It is a thin judgment layer over [beads](https://github.com/gastownhall/beads)
(`bd`), a git-backed graph issue tracker built for agents. Beads supplies the
machinery — hierarchical epics, a real dependency graph, atomic claims safe
across parallel agents, `bd ready` for unblocked work. The skill supplies the
part a CLI cannot: what to surface, what to ask about, and what to distrust.

### Why not a session todo list

`TaskCreate`/`TodoWrite` vanish when the session ends, which is exactly how work
slips. Anything meant to outlive the session goes in the tracker, and the first
rule is that follow-up work found mid-task gets filed **when it is discovered**,
with the file and line that prove it — not mentioned in a closing message that
nobody reads twice.

### The review pass

`/todos review` is the anti-slippage mechanism, and the reason the skill exists
rather than a shell alias. Work leaks in six specific ways, so it checks six:

| | What rots | What to do |
|---|---|---|
| 1 | **Uncaptured** — discussed, never filed | file it now |
| 2 | **Stale** — filed, untouched, rotting | re-prioritise, park with a reason, or close |
| 3 | **Decisions aging** — nothing downstream moves until they settle | surface any older than a week and ask directly |
| 4 | **Blocked on nothing** — the blocker is itself unowned | schedule the blocker or drop the edge |
| 5 | **Drift, both ways** — done but open, or closed upstream | reconcile against the real tracker |
| 6 | **Unlinked** — new issues that belong to a track | link, never duplicate |

Rule 2 carries more weight than it looks: a tracker nobody trusts is worse than
no tracker, because it converts an honest "I do not know" into a false "it is
handled". Rule 6 is the one that keeps two systems from becoming two truths —
the upstream tracker stays the execution record, beads stays the strategic layer
that sequences it, joined by `--external-ref`.

### The board

`/todos board` renders the whole graph as a self-contained page and publishes it
— tracks as threads, issues strung along them as beads coloured by state,
blocked items showing what they wait on, external refs linking back to the real
issue. `scripts/dashboard.py` takes `bd export` JSONL and emits standalone HTML,
so it works with any beads workspace and needs nothing at runtime.

### Portability

The skill names one workspace path, one issue prefix and one set of track
labels, because that is what makes a digest useful rather than generic. Swap
those for your own and the rest — the review pass, the capture discipline, the
board — is unchanged.

## `autopsy` — account for every second of one agent run

`/autopsy <thread id | screenshot | pasted text>` audits a single agent run when
it was slow, looped, failed, or said something untrue. Bare `/autopsy` sweeps
production: it samples the worst runs in a window plus a random baseline,
clusters their defects by root cause, and ranks them by users affected. It resolves the input to a
run, pulls every source you have (observability spans, app events, cloud logs,
the deployed version), and normalises them into one timeline.

Two things make it more than "read the trace":

- **A time budget that must add up.** Each lane's wall clock is split into tool,
  model, failed-tool and unaccounted time. Unaccounted time is itself a finding.
- **No "flaky".** Every anomaly needs evidence and a cause at the producer.
  "Transient" has to name the upstream event and the missing defence. "The model
  did something dumb" has to name the prompt, tool description or error text that
  invited it.

`scripts/autopsy.py` is backend-agnostic. You write a small adapter that emits a
canonical JSONL, and the script runs mechanical detectors:

- success recorded on failed output
- untyped failures
- repeated identical calls
- failures with no circuit breaker
- shared-layer outages across several hosts
- constant-duration timeouts
- retries after being told to stop
- read-only filesystems and missing auth
- long gaps
- TTFT-dominated calls, cache misses and context growth
- progress that never moved

Every hit is a lead to explain, not a verdict. Where your traces live goes in a
per-project profile (`.claude/autopsy.md`), never in the skill.
[`references/taxonomy.md`](autopsy/references/taxonomy.md) is the failure
taxonomy, with a detection signal for each class and its sources.

## `wow-mock-screenshots` — addon screenshots without the game

Screenshots captured in game go stale with every UI change and need someone at
the keyboard. This skill renders them instead: `wowmock.py` fetches the exact
client build's atlases, textures, fonts, item icons and DB2 data from
wago.tools (cached, so reruns are byte-identical), and provides the retail-UI
widgets — nine-slice frames, tooltips, menus, bag and item buttons, the
Professions and world map frames, the objective tracker — laid out with the
numbers from Blizzard's own XML. Each addon keeps a small
`tools/screenshots.py` that draws its scenes from its own source and data.

The skill's rule is accuracy over polish: every scene is checked, cropped and
enlarged, against a real capture before it ships, and `NOTES.md` records what
that turned up (BLP quirks, which atlas set wins, font layout, tooltip
spacing) so the next scene starts from it. Needs Python 3 and Pillow 12+.

## Licence

MIT. See [LICENSE](LICENSE).
