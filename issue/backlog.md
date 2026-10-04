# `/issue` with no arguments: work the backlog

Drive as many open issues as possible into **one ready-for-review PR** in one run. The user picks
the size of the batch, never the individual issues.

`/pr` owns how a change is built, committed, published and driven green, and its guard rails apply
here unchanged: one PR per repository, opened ready for review, never merged without authorization
given at merge time. This file adds only what a batch of issues changes.

## 1. Triage

```bash
gh issue list --state open --limit 300 \
  --json number,title,labels,assignees,milestone,comments,updatedAt,author
```

Put every issue in exactly one bucket:

- **shippable**: well scoped, needs no product or design decision, plausibly reaches a commit
  unaided. This is a candidate; step 3 confirms it.
- **needs-decision**: real work, blocked on a call only the user can make.
- **needs-info**: blocked on a repro or detail from the reporter.
- **stale**: old, superseded or already fixed. A candidate to close with a comment, and only with
  the user's sign-off.
- **too-big**: an epic or a multi-PR effort. Plan only.

Note **clusters**: issues that share files, or where one fix subsumes another.

Done when every open issue has a bucket and the counts are stated:
`triaged N open: X shippable, Y needs-decision, Z needs-info, W stale, V too-big`.

## 2. Scope

Ask once, with the largest safe batch first and marked recommended:

- **All shippable** (recommended): every shippable issue, one commit each, one PR.
- **A themed slice**: the largest coherent cluster.
- **Top K by confidence**.
- **Plans only**: a plan file per shippable and too-big issue, no PR.

When the user's words already answer it ("close as many as you can" is all shippable, one PR),
skip the question and state the scope being run.

## 3. Plan in parallel

Fan out one investigator per issue: subagents, or one `Workflow` for a large batch (this skill is
the opt-in). Each runs the plan steps in [`SKILL.md`](SKILL.md) and returns
`{shippable, slug, summary, plan_path, skip_reason}`.

Investigators only read and write plan files. Concurrent writers on one branch corrupt each other,
so nothing in this step edits, commits or branches.

Done when every issue in scope has a plan file and a confirmed `shippable` verdict.

## 4. Build serially

One worktree, one branch off the default branch, named for the batch.

1. **Order** the confirmed issues: a fix that subsumes another goes first, and a cluster sits
   together so its commits do not conflict.
2. **Per issue**: implement the plan, stage its files by explicit path, run the repository's gate,
   and on green make one commit whose message names the issue.
3. **A red gate or a blocker drops that issue to plan-only**: revert its edits, leave the branch
   clean, record the reason and move on. A low-confidence commit never goes onto the shared branch.

The build is serial because the gate and any migration must not run twice at once against shared
local state such as one database.

## 5. One PR

Publish through `/pr`. The body carries one `Closes #<n>` line per issue, since `Closes #A, #B`
closes only A, with each issue's plan path and test plan. A branch left by an earlier run of the
same batch is appended to, and its PR's title and body are updated.

## 6. Report

- Per issue in scope: `committed <sha>`, `plan-only: <reason>`, `blocked: <reason>` or
  `skipped: <reason>`.
- The PR's number and URL, and the issues it closes.
- Counts: `shipped P in PR #N, planned Q, blocked R, skipped S`.
- Each needs-decision, needs-info and stale issue, with the one action that unblocks it.
