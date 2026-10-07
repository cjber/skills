---
name: skill-writing
description: "Reference for writing any document an agent reads: a skill, AGENTS.md or CLAUDE.md, a memory entry, a doc behind a pointer. Use when creating, editing, merging or pruning one of those, or when another skill needs the shared glossary."
---

# Writing for agents

For human-facing product documentation, use [`docs-writing`](../docs-writing/SKILL.md).

All reference. The goal is a document that makes the agent take the same *process* every run.
Shared vocabulary for every skill in this repo lives in [`GLOSSARY.md`](GLOSSARY.md); use those
words exactly, and add a term there before a second skill needs it.

## Pointers

A **pointer** is an always-loaded line naming out-of-context material and the condition for
reaching it: a skill description, an `AGENTS.md` line naming a doc, a memory index entry. Its
wording decides whether the agent reaches the target.

- State what the material is, then one trigger per distinct **branch** it handles.
- Put the leading word first. Collapse synonyms: they are one branch written twice.
- Cut anything the body already says.

## The two loads

- **Context load**: always-loaded text, paid in tokens and attention every turn.
- **Cognitive load**: what the human must remember exists. Spend it where their judgment
  matters.

Material behind a pointer costs only the pointer's line. Material with no pointer rides on the
human's memory.

## Information hierarchy

A document holds **steps** (ordered actions) and **reference** (consulted on demand). Place each
piece on the ladder by how immediately it is needed:

1. In-file step.
2. In-file reference.
3. Disclosed reference: a separate file behind a pointer.

Inline what every branch needs; disclose what only some branches reach. Keep a concept's
definition, rules and caveats under one heading. **Sprawl** (too long, though every line is
live) is cured by disclosure and by splitting per branch.

## Completion criteria

Every step ends on a criterion the agent can check. Two properties:

- **Clarity**: done is distinguishable from not-done. "Understanding reached" invites premature
  completion; "every modified model accounted for" does not.
- **Demand**: how much it requires. The criterion's wording sets how much legwork the agent
  does, so make it exhaustive where thoroughness matters.

Split a sequence into two documents when the visible later steps tempt the agent to rush the
current one.

## Leading words

A **leading word** is a compact concept the model already holds (*tight*, *red*, *frontier*,
*fog*, *producer*) repeated as a token so it anchors behaviour in few tokens. Replace a phrase
spelled out at three sites with one word, and define it once in the glossary. A word too weak
to beat the default (*be thorough*) is a no-op; pick a stronger one (*exhaustive*).

State the target behaviour. A prohibition puts the forbidden behaviour in context and makes it
more available; reserve `never` for hard safety and data rules, and give the reason with it.

## Pruning

- **Single source of truth**: one meaning, one place. Elsewhere, point at it.
- **Cache**: text restating what the environment shows (`--help`, a config file, the directory
  layout). Keep only what the agent cannot find by looking: the unwritten convention, the
  reason, the gotcha.
- **Relevance**: every line still bears on what the document does. Stale layers are
  **sediment**; remove them.
- **No-op**: an instruction the model follows by default. Test by running the document without
  the sentence; if behaviour holds, delete the whole sentence.

## Skill mechanics

- **Model-invoked** (has a trigger-bearing `description`): the agent and other skills can reach
  it. Costs permanent context load. Choose it when the agent must fire it unprompted or another
  skill calls it.
- **User-invoked** (`disable-model-invocation: true`): zero context load; only the human typing
  its name reaches it. The description becomes a one-line human summary.
- Reference shared by several skills lives in one model-invoked reference skill (this one), or
  in a plain file each can point at.
- Split off a new skill only for a distinct trigger word you use in prompts, or because another
  skill must call it.
- **Merge before adding**: a new behaviour is first a branch in the skill that already owns the
  concept. A new skill is the exception.
- Repo-specific commands, paths and credentials stay in that repo's files (`AGENTS.md`,
  `.claude/<skill>.md`); the skill names where to look.
- When user-invoked skills outgrow memory, one **router** skill lists them and when to reach
  for each.

Adapted from mattpocock/skills `writing-for-agents`, (c) 2026 Matt Pocock, MIT.
Notice: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
