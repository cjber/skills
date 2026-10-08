---
name: docs-writing
description: Write or review human-facing software documentation, READMEs, how-to guides, tutorials, reference pages and troubleshooting instructions. Use for documentation audits and removing agent-generated filler while preserving technical meaning. For skills, AGENTS.md and other agent-facing instructions, use skill-writing instead.
---

# Documentation writing

Help the reader complete a task or understand a decision with verified information.
Read repository guidance first: its audience, vocabulary and publishing contract take
precedence over this general workflow. For the reasoning, evidence and examples behind
these rules, read [the research reference](references/research.md).

## Establish the reader's need

Name the intended reader, their goal, what they already know, and the supported
product version or client. Infer these from the request and existing docs; ask only
when the answer changes the content. Read the target page and its relevant neighbours.
Find the canonical home for the subject before adding a page.

Choose the form that serves the need:

- A tutorial teaches through a safe, bounded exercise with a visible result.
- A how-to solves a real problem for someone with the necessary background.
- A reference makes exact syntax, options, defaults and limits easy to look up.
- An explanation develops a mental model and the reasons behind it.

Use these distinctions to avoid mixing unrelated needs. They are not a requirement
to create four pages, add empty sections, or rebuild an existing information architecture.
Put an explanation beside a step only when the reader needs it to act correctly;
link to longer background.

## Verify claims before drafting

Build a small evidence list for the claims being added or changed: what is asserted,
which source proves it, and the version or release it applies to. Read the implementation
or authoritative specification rather than treating existing prose, command discovery,
an agent report, or a plausible UI label as proof.

For a product workflow, verify both the client entry point and the resulting behaviour.
Check relevant permissions, defaults, configuration and rollout conditions. Distinguish
merged code from a shipped capability. Keep evidence in the review record; product prose
should describe the reader's experience rather than internal implementation history.

If a claim remains unresolved, narrow it to what is proved or leave it out and identify
the missing evidence. Mark policy claims as requiring an authoritative policy source.
Follow a repository's stricter coverage requirement when it requires a whole-page audit.

## Write the shortest complete path

Lead with the useful outcome or definition. Include prerequisites where they affect
success. Write steps in execution order, placing the context before the action. Use
the actual control label and the verb that fits the action; give keyboard alternatives
when needed by the supported interface.

Describe controls by their names and actions. Position, colour or shape alone cannot
identify a control accessibly. Use meaningful link text, structured headings and
appropriate alternative text. Keep essential instructions available as text beside
screenshots or interactive previews.

Show the result a reader can use to recognise success. For a likely failure, explain
the symptom, its verified cause when known, and the recovery action. Place a material
warning before the action that creates the risk. Include alternatives only when they
change the reader's decision or path.

Use realistic examples with explicit placeholders and safe defaults. Check commands
and outputs against the supported version. An observed result and an illustrative
result are different claims: label an illustration and do not present it as a test.
Never fabricate successful execution, permissions, identifiers or capabilities.

## Remove filler without removing meaning

Every paragraph should support an action, a decision, a useful mental model or recovery.
Replace vague benefits and generic claims with concrete behaviour. Remove stock
introductions, repeated summaries, inflated adjectives, artificial contrasts,
announcements of what the next paragraph explains, and headings with no useful content.

Lead product copy with what it does and how to use it. Attribute it to the actual author;
do not invent a team, company, community, origin story or personal experience. First-person
claims need facts the author supplied. Remove slogans, preambles and obligatory feedback
closings. Preserve accurate contributor credits and licence notices.

Use the product's vocabulary consistently. Prefer direct verbs and concrete subjects.
Use passive voice when the actor is unknown or irrelevant. Keep qualifications that
affect correctness, and explain a technical term when the intended reader needs it.
Do not equate brevity with deleting prerequisites, limits, examples or failure paths.

Judge the passage in context. A word, punctuation mark, sentence length, detector score
or smooth tone does not prove AI authorship or poor quality. Apply local style preferences
as preferences, not as scientific rules. Edit for accuracy and usefulness rather than
for passing an AI detector or making prose artificially irregular.

## Check the delivered documentation

Read the draft as a first-time reader following the intended path. Inspect the rendered
page and any alternate output readers consume. Check links and anchors, headings,
examples, terminology, accessibility and required metadata. Search for other copies
of a corrected claim and reconcile them with the canonical page.

Run the repository's relevant docs checks. Automate decidable defects such as broken
links, schema failures and lost component text; use source review and walkthroughs
for semantics. Mechanical style lint is a suggestion unless the repository makes it
a rule. Do not add a test that merely repeats a prose edit.

Report what changed, how it was verified, and any specific unresolved claim. Include
the evidence needed for review without putting the research log into the product page.
