---
name: issue
description: "Plans GitHub issues from the code, or works a whole backlog into one PR. With issue numbers: writes a file-level implementation plan per issue and makes no commits. With no arguments: triages every open issue, builds the shippable ones onto one branch, and opens one PR closing them. Use for '/issue', 'look at issue 3765', 'plan this issue', 'triage the issues', or 'close as many issues as you can'."
argument-hint: "[issue-number] [issue-number...]   (omit all args to triage the whole backlog)"
allowed-tools: Bash, Read, Glob, Grep, Edit, Write, WebFetch, AskUserQuestion, Workflow
---

# `/issue`: plan an issue, or work the backlog

Two branches, picked by the arguments:

- **Plan** (`/issue 3765`, `/issue 3765 3801`): one plan file per issue. No branch, no commit, no push.
- **Backlog** (`/issue` with no numbers): triage, plan, build and open one PR. Read
  [`backlog.md`](backlog.md) first; it reuses the plan steps below for each issue.

The repository is whatever `gh repo view --json nameWithOwner -q .nameWithOwner` returns in the
current directory. If an issue lives in a different repository, say so and confirm before going on.

## Plan

A **plan** is a file at `~/.claude/plans/<repo>-<issue#>-<kebab-title>.md`. It stays out of the
repository. If one exists for the issue, update it in place.

### 1. Fetch

```bash
gh issue view <n> --json number,title,state,body,labels,assignees,milestone,author,createdAt,closedAt,comments,url
gh api repos/{owner}/{repo}/issues/<n>/timeline \
  --jq '.[] | select(.event=="cross-referenced" or .event=="referenced" or .event=="closed") | {event, src: (.source.issue.html_url // .commit_id // null)}'
```

- For each linked PR, read what was tried, what merged and what was abandoned:
  `gh pr view <pr#> --json title,state,body,commits,files,reviewDecision`.
- A closed issue is reported as closed before anything else: the user may want a follow-up, not a
  fresh plan.
- Fetch an external link (a doc, a screenshot, a thread) when the issue's meaning depends on it,
  and quote the fragment that matters.

Done when the body, every comment and every cross-referenced PR, issue and commit has been read.

### 2. Investigate the code

- List every file path, symbol, identifier and error string the issue and its comments name, and
  find each in the repository. Record call sites as `path:line`.
- Read the three to five most central files end to end.
- For a commit the issue cites: `git show <sha> --stat`, then `git log <sha>..HEAD -- <paths>` for
  what has moved since.
- Read the repository's `AGENTS.md` for where things live and how it tests, and any project memory
  about the issue. Reuse what is recorded.

Done when every named item is either located at `path:line` or recorded as not found. A plan
written from the issue text alone fails this step.

### 3. Decide before writing

- A fork where a wrong guess means replanning: run `/grilling` now. "Open questions" holds what a
  reviewer confirms later, never a decision that could be made here.
- Too big for one session, with decisions that depend on each other: stop and offer `/wayfinder`.
- A bug whose cause the investigation did not pin down: the plan's first step is `/diagnose`.

### 4. Write the plan

Sections, in order:

1. **Issue summary**: two to four sentences. What is wanted or broken, its current state, the link.
2. **Current behaviour**: what the code does today, each claim with a `path:line`.
3. **Desired behaviour**: what changes. If the comments reframed the problem, lead with that.
4. **Approach**: numbered steps. Each names the file and the function or section, and maps to one
   commit.
5. **Tests and verification**: how the change is proven, following the repository's own testing
   rules.
6. **Risks and edge cases**: what could regress.
7. **Out of scope**: adjacent work deliberately deferred.
8. **Open questions**: what to confirm at review. May be empty.

One sentence per bullet. No personal names or emails, and no cryptocurrency examples, in plan
content.

### 5. Report

In chat: the issue's title, state and URL; the plan's absolute path; the top three risks or open
questions, one line each; and the next step, usually `/wt` then the plan's first step. The file is
the source of truth, so the plan is not pasted back.

For several issues, give one line per issue and one recommendation of which to start with, judged
by dependency, blast radius and whether one fix subsumes another.
