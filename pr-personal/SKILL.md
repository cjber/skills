---
name: pr-personal
description: "Ship an approved change in one of Cillian's PERSONAL GitHub repos (owner `cjber` — dotfiles, skills, config; NOT the agent-labs-dev monorepo) as one reviewed, green, unmerged PR. Use for 'ship this', 'open a PR for this', 'fix it and PR it' on a personal repo, or `/pr-personal`. Personal-repo fork of `/pr`: the monorepo machinery (uv/sift, Postgres, gh stack, migrations) is dropped and personal guard rails are added."
---

# /pr-personal — one reviewed PR on a personal repo

Fork of `/pr` for repos under Cillian's own GitHub account (`cjber`) rather than the `agent-labs-dev` monorepo.

## Route first

- Remote is **`cjber/*`** (dotfiles, skills, config) or another owner that is personally Cillian's → this skill.
- Remote is **`agent-labs-dev/*`** (nebula, nebula-web, parallax, nebula-desktop) → use `/pr`. This skill's lighter gates are wrong there, and the monorepo's own `AGENTS.md` gate is the contract.

## Where this can run

Runs **locally** — Claude Code, Codex, or the Nebula CLI on `barry`, where `git` and `gh` already authenticate as `cjber`.

It **cannot run from a Nebula cloud agent.** The workspace GitHub App is installed only for the `agent-labs-dev` org, so every write to a personal `cjber` repo is refused — this is an installation-scope limit, not a credentials one, and re-delegating to another agent does not help. Anonymous reads (`api.github.com`, `raw.githubusercontent.com`, `git ls-remote`) still work. A cloud agent should do the read-only part, then stop and say the PR needs a local run: do not retry the write, and never reach for a personal access token to work around it.

## Guard rails — these outrank everything below

- **Never merge.** A green PR awaiting Cillian is the finished state, not an unfinished task.
- **Never touch a contributor's PR** — do not merge, close, approve, review, rebase, force-push, label or edit one. Report it, and take no action on it.
- **Never rewrite history:** no force-push, no rebase of pushed history, no amending a pushed commit, no deleting tags, releases or branches.
- **Never change repo state:** no visibility change, rename, transfer, archival, deletion, branch protection, Actions secrets, deploy keys or webhooks.
- **Never commit a secret.** `.env*`, keys, tokens and machine-local config stay ignored. If a file looks like a credential, stop and report rather than committing it.
- **Never push to a fork you do not own**, and never open a PR against an upstream you do not control.
- **One PR per repo.** If Cillian already has an open PR covering this work, add commits to it rather than opening a second.

## Scale the second opinion

Unlike `/pr`, a personal change does not automatically earn two models and a critique round — most of these diffs are a file or two of shell, config or markdown, and the coordination overhead would exceed the change.

- **Single pass by default:** plan, implement, verify, review once, publish.
- **Add the Codex arm** (below) when the diff touches any of: destructive shell (`rm`, `mv` over user data, partitioning/disk, systemd units, anything touched by a timer), credential or secret handling, a repo others consume (a published skill, a package, a tap), git history or hooks, or more than roughly 3 files / 200 lines.
- When the arm is used: one Codex pass and one Claude pass over the **same final diff**, exchanging only exclusive findings, one reply each, no recursive fan-out. Claude remains the only git owner — Codex never stages, commits, pushes or opens PRs.

### Invoking Codex without hanging

`codex exec` waits for stdin EOF whenever stdin is not a TTY, so a backgrounded call blocks forever after printing only `Reading additional input from stdin...`. Always redirect stdin, and always pin the tier:

```sh
cd "$WORKTREE" && codex exec -m gpt-6-astra -c model_reasoning_effort=xhigh \
  -c service_tier=default --skip-git-repo-check - < prompt.md
```

- `-c service_tier=default` on every call: the `priority` tier bills in credits, not against the plan.
- Pass the model fully qualified (`gpt-6-astra`); a bare name is rejected on a ChatGPT account.
- `Reading additional input from stdin...` is a hard failure **whatever the exit code** — it has exited `0` while doing nothing.
- A fast exit is not a fast success: confirm the arm actually changed something. An arm silent for ~5 minutes has almost certainly hit the hang.
- `codex review` takes `-m`/`-c` as top-level flags before the subcommand, and always `--base origin/main` (bare `main` reviews against the stale local branch).

## 1. Plan

- Read the repo's `AGENTS.md` / `CLAUDE.md` / `README` if it has one, and follow its conventions. Personal repos frequently have none — infer the convention from the surrounding files instead of importing one.
- One decision-complete plan: what changes, why, how it will be verified, and what is explicitly out of scope.
- Ask only when a missing decision would materially change behaviour.
- For a bug, reproduce it first — these repos rarely have tests, so a one-liner that shows the break is the cheapest durable reproduction.

## 2. Isolate

- Never edit the primary checkout. Create a worktree off fresh `origin/main`, matching the `/wt` convention:

```sh
git fetch origin main
git worktree add -b cb/<slug> ~/.worktrees/<repo>/cb-<slug> origin/main
```

- Copy git-ignored local config such as `.env` when the repo needs it; never commit it.
- Keep a stray local change out of the branch — personal repos often carry uncommitted scratch edits in the main checkout, and those are not yours to ship.

## 3. Implement and verify

- Make the smallest coherent change that does the job. No opportunistic tidying in an unrelated file.
- Run whatever verification the repo already has: `make check`, `bun run check`, `npm test`, `shellcheck`, `bash -n`, `pre-commit run --all-files`, `nix flake check`, `terraform validate`.
- **Most personal repos have no CI.** When that is the case, local verification *is* the whole gate: say exactly what you ran in the PR body, and do not call a change green when nothing was run.
- Do not add a CI workflow inside an unrelated PR; that is its own change, with its own PR.

## 4. Review

- Review the final `git diff origin/main` once, against the code as it actually is.
- Fix verified findings **in this PR**. Filing an issue is not a resolution — and on a personal repo nobody will ever pick the issue up.
- Defer only what genuinely cannot land here, say so in the report, and let Cillian decide.

## 5. Commit and publish

- Stage explicit paths — never `git add -A` or `git add .`.
- Signed Conventional Commits (`git commit -S`); do not bypass hooks.
- Push one branch and open **one ready-for-review, non-draft PR**. If the branch already has a PR, update it rather than opening another.
- PR body: what changed and why, how it was verified, anything deliberately deferred. Keep it short.
- The mermaid-diagram rule from `/pr` applies only when the change has a structure worth drawing — a new script with several stages, a systemd/scheduler flow. Do not manufacture a diagram for a dotfile edit.

## 6. Drive it green

- If the repo has checks, wait for them and read the result: never assume green because the push succeeded.
- If it has no checks, say so plainly instead of implying a green tick that does not exist.
- Fetch review comments explicitly — a PR-level body hides the inline set:

```sh
gh api "repos/{owner}/{repo}/pulls/{n}/comments?per_page=100" \
  --jq '.[] | select(.in_reply_to_id == null) | {id, path, user: .user.login}'
```

- **Every comment gets a posted reply** — accepted (name the commit), rejected (name the evidence), or partially accepted. A fix without a reply reads as an ignored comment.
- Every push reopens the comment window: re-check for both new checks and new comments after each push.

## 7. Never merge

Merging is Cillian's call and needs him to say so for these specific PRs, now. A standing preference, an old approval, or a "ship it" from earlier is not authorisation. If merging looks obvious, say so and ask.

## Finish

Report the PR URL and base, the branch and worktree, the commits, the final check state (or that the repo has no checks), how each comment was resolved, and any real blocker. Do not report success while checks are red, still running, unchecked, or while any comment lacks a posted reply.

State the merge status plainly: green and awaiting review. A green PR left unmerged is the expected end of this skill.
