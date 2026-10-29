---
name: barry-ship
description: Ship a change end to end across the three Barry agents, with plan, build, simplify, gate, review and CI chained automatically. Use when the user invokes /barry-ship.
disable-model-invocation: true
---

# /barry-ship

`/pr`, fanned out across Barry. The text after `/barry-ship` is the brief; without one, use the
request in the conversation. Dispatch, worktrees, the run directory and the two hard rules come
from [`barry-coding-team`](../barry-coding-team/SKILL.md): read it first. This skill fixes the
pattern and the chain around it.

**Roles for this pattern.** The calling session is the **coordinator**: it scopes, synthesizes,
owns git (stage, sign, push, PR, replies) and runs every chained skill. Barry Claude and Barry
Codex plan and build; Barry OpenCode is the third reviewer and the fallback for an arm that cannot
run. Every arm runs as a local CLI in its own worktree. No arm commits to the integration branch,
pushes or opens a PR.

Run the stages in order. Each ends on its artifact; a stage without one is not done.

## 1. Scope

- Read the repository's `AGENTS.md`. Find its gate (`sift check` where `.sift/gate.py` exists).
- Check open PRs for this effort (`gh pr list --author "@me" --state open`): continue an open PR
  instead of opening a second one.
- A bug with no evident cause goes through `/diagnose` first; its red loop is part of the brief.
- An open design decision that changes what gets built goes through `/grilling`. Otherwise take
  the obvious default and record it.
- Start the run directory and one `cb/<slug>` worktree per writer from fresh `origin/main`.

**Done:** `brief.md` in the run directory names the goal, the gate command and the base SHA.

## 2. Plan on two models

- Start the Claude and Codex arms on the brief in parallel. Each returns
  `plan-<agent>.md`: decisions, files and contracts touched, risks, checks.
- Send each plan to the other agent once. Replies hold only wrong assumptions, missing risks and
  corrections.
- Resolve the disagreements from the source and write one `plan.md` with two disjoint file sets.

**Done:** `plan.md` exists, every disagreement has a recorded resolution, and the two slices
share no file.

## 3. Build on two models

- Start each slice's arm in its own worktree. Each runs only its slice's focused checks
  and returns `result-<agent>.md` with a branch and SHA.
- If the change cannot be split, one agent builds and the other reviews its seam in stage 5.
- Exchange the two diffs once for seam mismatches only. Merge both into the integration worktree
  one at a time, running the gate after each.

**Done:** one integration branch holds both slices and the gate passes on it.

## 4. Simplify and gate

1. `/simplify` on the full diff from the base.
2. `sift audit diff` where the repository has sift: clear what the diff itself made dead.
3. The gate (`/sift check`), fixed by changing code, never the check.

**Done:** the gate's exact command and its passing output are in `checks.md`.

## 5. Review on three models

- Run `/review` on the branch in this session.
- Start the Codex and OpenCode arms on the same base..head as read-only reviews, in the finding
  shape from `barry-coding-team`.
- Verify every finding against the source. Fix the ones that reproduce, rerun the gate once, and
  record the dropped ones with the reason.

**Done:** `review.md` lists every finding as fixed or dropped, and the gate is green after fixes.

## 6. Publish and watch

- Commit and push through `/commit`: signed commits, the repository's PR template, ready for
  review. A follow-up goes onto the open PR.
- Watch CI and review comments until both settle. Fix each failing check at its producer; reply
  to every inline comment with the fix's SHA or the reason it stands.
- A failure that needs investigation goes through `/diagnose`.

**Done:** every required check is green and every review comment has a reply.

## 7. Stop at the merge gate

Merging waits for the human. Remove only the worktrees this run created, then report in the
`barry-coding-team` report shape, adding the chained skills run and the PR link.
