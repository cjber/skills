---
name: barry-coding-team
description: "Coordinate Barry Claude, Barry Codex and Barry OpenCode on one coding task: split roles, hand off through git artifacts and Nebula Tasks, then integrate one reviewed result. Use for 'use the Barry team', /barry-code, a multi-agent coding pass, or an independent implementation plus review across Barry agents."
---

# Barry coding team

Three external CLI agents run on the same Linux machine and share one filesystem: Barry Claude
(`barry-claude`), Barry Codex (`barry-codex`) and Barry OpenCode (`barry-opencode`). Each is a
separate session, so they share no context. Git carries the code, a run directory carries the
coordination, and Nebula carries the dispatch.

Use the team when independent implementation or review is worth the overhead. A small, isolated
fix stays with one agent.

## Roles

| Agent | Default role | Use for | Known limit |
|---|---|---|---|
| Barry OpenCode | Lead / integrator | Scope, brief, worktrees, integration, gate, publish, report | Smaller model: verify with commands, not memory |
| Barry Codex | Builder | One bounded implementation slice, disciplined commits | Has reported no signed GitHub identity: it does not publish |
| Barry Claude | Planner / reviewer / operator | Design and diff review, repo and environment repair | Its plan token can expire mid-turn |

If the human names a lead, that agent leads. Otherwise the first Barry tagged in the request leads;
if that is unclear, Barry OpenCode leads. One agent per role, one lead per run. A non-lead never
edits the lead's checkout.

## The two hard rules

1. **One writer per worktree.** All three agents see the same disk, so two agents editing one
   checkout corrupt work silently. Every writing agent gets its own worktree at the run's base
   commit. Reviewers inspect a branch or a read-only worktree and never commit.
2. **Artifacts, not claims.** A handoff is complete only when it names a commit SHA, a branch, a
   patch file or check output. "Done" and "looks good" are not handoffs.

## Run directory

The run directory is the shared mailbox, because the agents cannot read each other's Tasks.

```sh
repo="$(git rev-parse --show-toplevel)"
date_tag="$(date +%Y%m%d)"
run_dir="$HOME/.barry/team/$(basename "$repo")/$date_tag"
install -d -m 700 "$run_dir"
```

- The lead writes `brief.md` and `decisions.md`.
- Every agent, lead or not, reads `brief.md` and `brief-<slug>.md` when present before acting.
- Every agent writes `result-<slug>.md` before it finishes, even on failure.
- A reviewer writes `review-<slug>.md`; a builder writes the branch and head SHA in its result.
- If you are not the lead and no brief exists yet, work your default role from the current base and
  write your result; do not sit waiting for a file.
- If the directory already contains a brief for different work, use `$date_tag-2`, `-3`, and say
  which path you used in your reply.

Keep every file and every dispatched brief under 8 KB. Send paths and short excerpts, not whole
files: Nebula rejects an oversized dispatch rather than truncating it.

## Start a run

The lead does this before assigning any work.

1. Inspect the repository, branch and working tree. The run starts from a **committed base**:
   record `git rev-parse HEAD` and `git status --porcelain`. If the tree is dirty, commit the
   intended work or ask; never mix uncommitted changes into parallel arms.
2. Write `brief.md` from the template below; it must state the goal, acceptance criteria and gate.
3. Create one worktree per writer, all at the same base SHA. Do not use `origin/main` directly:
   the arms must be comparable.

```sh
base="$(git rev-parse HEAD)"
task="<kebab-task-slug>"
repo_name="$(basename "$repo")"
git -C "$repo" worktree add "$HOME/.worktrees/$repo_name/barry-codex-$date_tag" \
  -b "barry/codex/$date_tag-$task" "$base"
# Repeat per writer. Leave the primary checkout on its current branch.
```

Create a separate integration worktree for yourself; the primary checkout stays on its current
branch.

```sh
git -C "$repo" worktree add "$HOME/.worktrees/$repo_name/barry-integration-$date_tag" \
  -b "barry/integration/$date_tag-$task" "$base"
```

## Brief template

```text
Goal:
Acceptance criteria:
Repo / base SHA:
Your role and exact deliverable:
May you edit? Which files or worktree:
File ownership (what no one else may touch):
Publish target: none | branch | PR
Gate:
Rounds: one implementation round, one review round, stop at the merge gate
Return: branch, head SHA, changed paths, checks run, open risks
```

Disjoint file ownership is what makes parallel edits safe. If two arms must touch the same file,
run them as a pipeline instead of a fan-out.

## Dispatch

Prefer Nebula Tasks; they are the agents' native interface.

- **The human tagged the team:** their Tasks already exist. Put each agent's assignment in
  `brief-<slug>.md`; they read it from the run directory. Do not dispatch a duplicate Task.
- **The lead dispatches:** send a focused brief and keep the `thread_id`.

```sh
nebula-ai --json --workspace cillian chat --no-stream --agent barry-codex \
  -- "$(cat "$run_dir/brief-codex.md")" < /dev/null
```

The Barry agents live in the personal `cillian` workspace. Without `--workspace cillian`, `chat`
answers "Agent not found" whenever another workspace is active.

- One level deep only. An agent that was dispatched as part of a team run does not dispatch
  another Barry agent; the lead does the dispatching, at most one sub-task per agent per round.
- `status: incomplete` or exit `5` means the task was sent. Check
  `nebula-ai --json tasks status <thread-id>` and read the thread; never resend a mutating brief.
- If Nebula is unavailable and the human asked for a local run, the CLIs are on `PATH`. Give each
  arm its own worktree and a read-only mode for review; run only the arms you are not already
  running as:

```sh
(cd "$HOME/.worktrees/$repo_name/barry-codex-$date_tag" && codex exec -s workspace-write \
  "Read $run_dir/brief-codex.md and do it.")
(cd "$HOME/.worktrees/$repo_name/barry-claude-$date_tag" && claude -p \
  "$(cat "$run_dir/brief-claude.md")" --permission-mode plan)
(cd "$HOME/.worktrees/$repo_name/barry-opencode-$date_tag" && opencode run --auto \
  "Read $run_dir/brief-opencode.md and do it.")
```

## Execution patterns

Choose one pattern up front and say which one the run uses.

- **Solo** — one agent, no team. Small fix, single file, or an urgent hotfix.
- **Pair** — builder implements on its branch; reviewer reviews the diff from the same base; lead
  integrates. The default for a normal feature.
- **Pipeline** — Claude plans, Codex builds from the plan, OpenCode verifies and publishes. Use
  when the design is unclear or the change is risky; each stage must produce an artifact before
  the next starts.
- **Race** — two independent implementations from one base, timeboxed, for a genuinely contested
  design. The lead picks one and ports only the better ideas from the other. Never race routine
  work.

A review round returns findings in this shape, and nothing else:

```text
<file>:<line> — failure scenario — smallest fix — confidence
```

The reviewer does not redesign, edit or restate the diff. The lead verifies each finding against
the source before acting on it; a finding that does not reproduce is recorded and dropped.

## Integrate and publish

1. Read every `result-*.md`. If one is missing, check that agent's Task status; do not block the
   run on it. Treat an agent's claim as a lead, not proof: inspect its branch with
   `git log --oneline "$base"..<branch>` and `git diff --stat "$base"..<branch>`.
2. Merge into the integration worktree one arm at a time, running the gate after each merge.
   Resolve conflicts there; never force-push a branch another agent may still hold.
3. Run the repository's documented gate (for example `sift check`). Report the exact command and
   its result. A check you did not run is not passing.
4. Only the lead publishes: push the integration branch and open one PR for the effort. Follow the
   repository's signing rule: Codex's setup signs automatically, while the other agents sign with
   `-S` as the global agent rules require. Verify with `git log --show-signature -1`. Stop at the
   merge gate and wait for the human's say-so before merging.
5. Before pushing or committing, confirm this run created the branch. If it already existed,
   inspect it and ask; preserve work the run did not author.
6. After the branch is pushed, remove only the worktrees this run created
   (`git worktree remove <path>`) and keep their branches until the PR merges. Never touch the
   primary checkout.

## When something fails

- **An agent cannot run:** record it as unavailable, reassign the role to another agent, and say so
  in the final report. Do not retry in a loop.
- **Claude's plan token expires mid-run:** its branch or partial review is still usable. Verify the
  artifact, hand the remaining review to another agent, and record the failure.
- **Disk is full:** stop writing, run `df -h`, delete only temporary files this run created, and
  report. Do not delete caches or user data you do not own.
- **A brief is rejected as too large:** write it to the run directory and dispatch the path plus a
  ten-line summary.
- **Two agents changed the same file:** stop merging, compare both diffs against the base, and
  resolve on the integration branch with one owner.

## Report

End with the outcome and the evidence:

```text
Outcome:
Branch / PR / base..head:
Who did what (agent → artifact):
Checks (command → result):
Unresolved risks or agent limitations:
Next action:
```

Never imply all three agents completed if one did not, and never take credit for another agent's
work.
