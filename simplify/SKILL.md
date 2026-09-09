---
name: simplify
description: "Reduce a diff without changing intended behavior. Use after implementation or substantive fixes to delete duplication, reuse canonical seams, trim low-value tests/comments, and leave a smaller coherent change. This skill simplifies only; review, commit, and push happen afterward."
---

# Simplify a coherent diff

Make the whole change smaller and clearer while preserving supported behavior.
This skill does not invoke `/review`, commit, push, or start another workflow.

## Budget

- Work in the current context with one editor. Do not spawn reviewers or agents.
- Read the repository's agent instructions (`AGENTS.md` / `CLAUDE.md`) and only the
  domain skills required by changed production files.
- Inspect the complete diff from its real base plus uncommitted changes.
- Read [the rubric](references/review-rubric.md) only for a broad or structurally
  complex diff; for a narrow change, use the checks below directly.

## Simplify in priority order

1. Delete unreachable, redundant, speculative, or superseded code. **Never**
   leave it behind a "remove in a follow-up" note - if this diff killed the
   last reader, this diff deletes it. Verify the compatibility claim that
   argues for keeping it; most do not survive being checked.
2. Extend the highest existing authoritative seam instead of adding a parallel one.
3. Replace hand-rolled parsing, retry, caching, serialization, or validation with
   an already-used trusted library or vendor SDK when semantics match.
4. Collapse abstractions with one caller or no independent contract.
5. Keep one test per distinct realistic failure; remove constant, private-shape,
   and duplicate permutation tests.
6. Remove narrating comments and duplicated docs; retain non-obvious safety,
   compatibility, and incident rationale.

Never reduce authorization, tenant isolation, billing, persistence, concurrency,
cancellation, migrations, or supported stale-client compatibility merely to
shrink the diff.

## Apply and prove

- Apply only high-confidence, behavior-preserving reductions.
- Remove the superseded path completely: imports, tests, configuration,
  dependencies, and stale documentation.
- Reject a candidate that is longer, less typed, or less explicit without a
  compensating whole-system deletion.
- Run focused checks after the edit batch and the repository-required full gate
  when this is the final pre-commit pass.
- Re-read the final diff once.

Report the meaningful deletions/unifications, checks run, and any complexity kept
for a concrete contract reason. Return control to the caller for review and
publication.
