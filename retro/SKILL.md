---
name: retro
description: "Retrospective on a coding session that proposes changes to the agent's environment: checks, steering files, skills, memory and tooling. Use for 'retro', 'what should we change so that doesn't happen again', or after a session that wasted time. For defects inside one agent run use autopsy."
argument-hint: "[session id or path; defaults to the current session]"
---

# Retro: fix the environment, once

A retro turns one session's friction into a durable change to the **environment**, so the next
session starts ahead. It proposes; it applies only what the user picks.

## Steps

1. Load `skill-writing` for the writing rules and the glossary.
2. Read the primary sources: the session named (transcripts on this machine) or the current
   one, plus every steering file it loaded (`AGENTS.md`/`CLAUDE.md`, global and repo), the
   memory index, and the skills it invoked.
3. Walk the session for **friction**: a wrong turn, a retraction, a repeated search, a user
   correction, a check that failed late, an expensive tool call. Each one is a candidate.
4. Route each candidate to the cheapest **home** that would have prevented it (table below).
   Done when every piece of friction has a home or an explicit "one-off, no change".
5. Present candidates most-costly first: the friction (quote the moment), the home, the exact
   edit. Apply the ones the user picks.

## Homes, cheapest first

| Friction | Home |
|---|---|
| A **mechanical** violation: fixed syntactic pattern, banned API, import shape, file location | A deterministic check in the repo's own gate (lint rule, hook, CI job). Read the gate first: a check that exists but is unwired or silently broken is the finding, and so is a repo with no gate at all (no hook and no CI job running its lint, type check or tests). |
| A judgment-call standard the diff could show | The review standard the reviewer reads, where review has little context pressure. |
| Slow to find the right file or doc; a hidden dependency | A **pointer** in the nearest steering file or skill description. |
| A crucial fact was unreachable (logs, a third-party dashboard, a read-only credential) | Information access: tee the logs, add the read path. |
| An expensive or repeated tool call | A script, a narrower command, or a tool allowlist entry. |
| A multi-step procedure re-explained by hand | A skill, or a new branch in an existing one. |
| A user preference or project fact no file records | One memory entry, or an edit to the existing entry that covers it. |

Prefer a row higher in the table: a check enforces every run, a sentence only when read.

## Pruning pass

Steering files and the memory index are always-loaded **context load**. On every retro:

- **No-ops**: instructions the model already follows by default. Delete the whole sentence.
- **Sediment**: stale lines, and memories about code or tools that no longer exist.
- **Duplication**: one meaning in two files. Keep the single source of truth and point at it.
- **Caches**: text restating what one command or one file would show.
- **Promotions**: a steering rule that is really mechanical moves to a check and leaves the file.
- **Disclosures**: a steering section only some tasks reach moves to a doc behind a **pointer**.
  What stays is what every task needs: commands, hard rules, gotchas and pointers.
- An index over its size limit is a finding by itself: merge and shorten until it loads whole.

Adapted from mattpocock/skills `retro`, (c) 2026 Matt Pocock, MIT.
Notice: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
