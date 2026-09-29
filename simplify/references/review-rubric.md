# Critical review rubric

Apply every section. A “no finding” is a valid disposition only after examining
the relevant producer, consumers, and tests.

## Whole-system duplication

- Find multiple paths that produce the same concept, event, model, lookup, or
  side effect. Select the highest existing canonical producer and delete the
  others rather than synchronizing them.
- Find registries, mappings, enums, schemas, defaults, and feature gates that
  represent the same closed set. Keep one typed source of truth.
- Find old and new implementations retained “temporarily.” Require an actual
  supported-client or rollout constraint and a dated/versioned removal gate.
- Reject wrappers, helpers, services, protocols, and factories that have one
  trivial caller or merely rename an existing API.

## Dependency and platform leverage

- Locate custom regex grammars, Markdown/HTML parsing, URL handling, validation,
  serialization, pagination, retries, rate-limit handling, caching, crypto, and
  vendor HTTP calls. Check for an existing maintained library or official SDK.
- Prefer an already locked dependency. A new dependency must net-remove enough
  risky code to justify lifecycle and supply-chain cost.
- Lean on SDK types and errors inside the integration adapter. Do not leak vendor
  objects across your own protocol boundary.
- Do not replace a small obvious operation with a framework abstraction merely
  to satisfy “use a library.”

## Control flow and data shape

- Flatten nesting with guard clauses where it clarifies the happy path.
- Replace repeated condition computation with one named decision.
- Remove boolean flags that create hidden multi-mode functions; split only when
  the modes are genuinely separate contracts.
- Make closed-set branching exhaustive and typed. Reject stringly typed parallel
  maps and silent fallbacks.
- Remove conversions, copies, and projections that cross no real boundary.
- Keep functions focused and under the repository's size guidance, but do not
  create one-use fragments solely to satisfy a line target.

## Abstraction and indirection

- Demand at least three real uses or a genuine boundary before introducing a
  general abstraction.
- Remove pass-through layers, speculative configuration, unused extension
  points, premature protocols, and generic containers that erase useful types.
- Prefer direct calls to an authoritative model/service over local facades.
- Reject centralization that grows the system materially unless the existing
  boundary is proved incapable of owning the behavior.

## Tests

- Group tests by distinct behavior branch, not input trivia.
- Remove constant assertions, exhaustive permutations of library behavior,
  implementation-shape assertions, duplicate unit/integration coverage, and
  fixtures larger than the behavior they prove.
- Challenge every mock. Four or more collaborators usually means the test is
  verifying its own setup; move to a pure function or real integration seam.
- Preserve one sharp regression for every bug and high-risk contract. Never use
  simplification to erase evidence for auth, workspace isolation, billing,
  persistence, concurrency, cancellation, or migration safety.

## Text, prompts, and skills

- Delete comments that narrate the next line and docstrings that restate names.
- Consolidate repeated policy into the canonical domain skill and link to it.
- Keep prompts concise, natural, and free of duplicated or contradictory rules;
  agent-visible changes require the repository's end-to-end validation.
- Keep `SKILL.md` as a router and core workflow. Split large independently
  selectable topics into directly linked references, never reference chains.
- Treat large rule-numbered domain skills as semantic migrations: split them only
  with a section-to-reference inventory and link validation, not by line count.

## Operational residue

- Remove dead dependencies, flags, settings, environment variables, metrics,
  logger policy, workflows, generated outputs, and documentation with their code.
- Check async cancellation, task ownership, resource cleanup, query count, cache
  invalidation, and retry multiplication introduced by new layers.
- Confirm simplification did not move secrets toward sandboxes or weaken tenant
  predicates, access checks, audit events, or error visibility.
