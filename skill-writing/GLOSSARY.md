# Glossary

Leading words shared by the skills in this repo. One meaning per word; a skill uses the word
and leaves the definition here.

## Work

| Term | Meaning |
|---|---|
| **loop** | One command that reports pass or fail for a specific behaviour. |
| **tight** | Of a loop: fast, deterministic, agent-runnable. |
| **red** / **green** | The loop fails on the bug / passes once fixed. A loop is *red-capable* when it can catch this specific bug. |
| **producer** | Where a value is first created. Fixes land here so every **consumer** inherits them. |
| **seam** | A place where behaviour can be altered or tested without editing there; where a module's interface lives. |
| **gate** | The repo's required checks (lint, types, tests, project rules). CI is the merge gate. |
| **arm** | One independent model pass in a two-model phase of `/pr`. |
| **finding** | A defect with `file:line`, a concrete failure scenario and a fix, validated against the code. |
| **primary source** | The thing itself: source code, official docs, a spec, a trace. A write-up about it is secondary. |
| **environment** | Everything the agent works inside: checks, steering files, skills, memory, tooling. |
| **friction** | A moment a session lost time: wrong turn, retraction, repeated search, user correction. |

## Planning

| Term | Meaning |
|---|---|
| **destination** | What reaching the end of an effort looks like: a spec, a locked decision, a change in place. |
| **map** | The index issue for a multi-session effort. Lists decisions and links their tickets. |
| **ticket** | A child issue holding one question sized to one session. |
| **frontier** | The open, unblocked, unclaimed tickets: what can be taken now. |
| **fog** | In-scope work that cannot yet be phrased as a sharp question. |
| **HITL** / **AFK** | Needs the human live / the agent runs it alone. |
| **handoff** | A document that lets a fresh agent continue, pointing at artifacts instead of copying them. |

## Writing

| Term | Meaning |
|---|---|
| **pointer** | An always-loaded line naming out-of-context material and when to reach it. |
| **branch** | A distinct case a document handles. |
| **context load** | Cost of always-loaded text on the agent's window. |
| **cognitive load** | Cost on the human of remembering what exists. |
| **leading word** | A compact concept the model already holds, repeated as a token to anchor behaviour. |
| **disclosure** | Moving reference into a separate file behind a pointer. |
| **no-op** | An instruction the model already follows by default. |
| **cache** | Text restating what the environment would show on lookup. |
| **sediment** | Stale lines that settled because adding felt safer than removing. |
| **sprawl** | A document too long even though every line is live. |
