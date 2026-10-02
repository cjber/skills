---
name: grilling
description: "Interview the user one question at a time to resolve a plan or design before any code is written. Use for 'grill me', 'grill this', 'poke holes', stress-testing a plan, or an ambiguous task where guessing would cost more than asking."
argument-hint: "[plan, design, or task to interrogate]"
---

# Grilling

The most expensive failure is misalignment: building the wrong thing confidently because the
task was underspecified. Grilling spends a few cheap questions to prevent it.

Treat the plan as a **design tree**: each decision branches into the decisions that hang off
it. The **frontier** is every decision whose prerequisites are settled.

## Rules

1. **One question at a time**, taken from the frontier. Ask, wait, then ask the next.
2. **Carry a recommended answer.** "I'd lean X because Y - agree?" The user corrects a proposal
   faster than they author one.
3. **Facts are your job; decisions are the user's.** Anything discoverable in the code, the
   docs or a tool, go and read. When a fact takes real digging, send a background agent and
   keep asking the questions that do not depend on it. Ask the user only for intent,
   priorities, tradeoffs and scope.
4. **Follow dependencies.** Resolve first the decision that unblocks the most downstream
   questions. When an answer opens a branch, walk it before backing out.
5. **Record what must outlive the conversation.** A decision that is hard to reverse,
   surprising without its context, and the result of a real tradeoff becomes an ADR where the
   repo keeps them. A term the conversation sharpened goes into the repo's glossary or domain
   doc. Everything else stays in the summary.

Done when the frontier is empty: no branch left that would change what gets built. Summarise
the resolved design in a few lines and wait for the user to confirm before acting on it.

## When to reach for it

- Before a non-trivial plan or PR whose spec has real ambiguity.
- When `/issue` or `/wayfinder` would otherwise have to guess at intent.
- When the user asks to be grilled.

A task with one obvious interpretation skips it: state the default and proceed.

Adapted from mattpocock/skills `grilling` and `grill-with-docs`, (c) 2026 Matt Pocock, MIT.
Notice: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
