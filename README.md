# skills

Claude Code skills I actually use, kept here so they can be shared. One per
directory, each a self-contained `SKILL.md` plus whatever tooling it needs.

| Skill | What it's for |
|---|---|
| [`pr`](#pr--ship-one-green-pr-on-two-models) | Take an approved change all the way to a reviewed, green PR — planned, implemented and reviewed on two different models. |
| [`deadcode`](#deadcode--prove-it-dead-before-you-delete-it) | Clean up a whole project without shipping a silent breakage. The judgment layer on top of `vulture`/`knip`/`ts-prune`. |

They are designed to work together — `/pr` calls `/deadcode` in its review phase —
but either one stands alone.

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

## Adapt before you use these

These are my working copies, not neutral templates. They hardcode the gates and
habits of the repository I use them in, and those are the first lines to change:

- `uv run sift check` and `uv run dead-code` are that repo's lint/type and
  dead-code gates. Substitute your own.
- `/simplify` and `/review` are separate skills that live elsewhere and are not in
  this repository yet. Where a file invokes them, point at your equivalent or
  inline the intent.
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

## Licence

MIT. See [LICENSE](LICENSE).
