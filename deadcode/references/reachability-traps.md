# Reachability traps and production invariants

Read this before ruling a reachability path out, or before removing a candidate that looks
redundant. It holds the recurring concrete shapes behind Phase 2's five paths, and the
load-bearing classes a cleanup must not strip.

## Non-code and off-disk reachability (worked traps)

The five paths have recurring concrete shapes where **an empty grep is the *expected* look of live code, not evidence of death.** These examples generalize across repos; consult the project's documented framework and persistence rules before deciding a candidate is dead.

- **Durable-workflow step names.** A durable/orchestration step (DBOS `@DBOS.step`, Temporal activity, Celery task) is resumed by its *pinned string name from persisted in-flight state*, not from a static call site. A step function with zero callers can still be mid-flight in a running workflow; deleting or renaming it breaks those runs. → KEEP unless you prove no in-flight or scheduled workflow references the name. *(E.g. a durable-workflow engine with explicit `name=` registrations.)*
- **Enum / literal values at rest.** A `StrEnum`/`Literal` member with zero code references may still exist as a *stored value in the database* (persisted as text). Deleting the member breaks row-load for every existing row carrying it. Query the data for the value (`SELECT DISTINCT col`), don't just grep code. → KEEP unless the value is provably absent at rest. *(E.g. SQLAlchemy enums stored via `Enum(..., native_enum=False, values_callable=...)`.)*
- **Migration chains are append-only.** A migration file is never "old dead code" — migrations form a linked `down_revision` chain; deleting one breaks `upgrade`/`downgrade` on every environment that has not already run past it. → NEVER delete a migration to tidy.
- **Name-dispatched plugin registries.** Tools/agents/handlers registered by string into a registry and dispatched by name (LLM-selected tool names, route tables, entry-point plugins) have no static caller — the registry is the caller. → KEEP; enumerate the registry's keys, not the symbol.

**Docs, specs, and rule/skill files are part of the tree — in BOTH directions:**
- A prose reference (README, runbook, in-repo skill, `AGENTS.md`/design doc) to logic you are *removing or merging* becomes dangling cruft the moment the code goes — fix or delete it in the **same** behavior-preserving change so code and docs never drift. Enumerate mentions with `rg` across `*.md`/docs, not just source; a symbol rename with a stale doc line is a half-done change.
- But a doc mention is **not** a keep-alive signal. Docs go stale independently: a symbol referenced *only* in prose (never reached by code, config, or any of the five paths) can still be dead — the doc is simply describing already-removed or never-wired logic. Prove death by the code paths; then the sweep removes the dead symbol **and** its stale mention together. (Worked shape: an enum member that no code path constructs, still named in a skill doc — the member is dead *and* the doc line is stale; both get fixed, after approval — never delete the mention while leaving a live symbol, or vice versa.)

## Load-bearing code that looks dead or redundant (production invariants)

Beyond reachability, a production codebase carries code that *looks* removable or redundant but is a live safety, correctness, or scale guarantee. These are **proven-alive** classes — a "cleanup" that strips one is a regression, not tidy. Prove a candidate is NOT one of these before removing; when unsure → KEEP.

- **Idempotency / dedup / guarded mutations.** A dedup-key check, `INSERT ... ON CONFLICT`, or `update().where(status="pending")` guard looks redundant on the happy path — it exists so a *retry* doesn't double-apply. Removing it is a duplicate-processing bug visible only under retry / at-least-once delivery.
- **Security / scope / validation defense-in-depth.** A `workspace_id` predicate, permission/access check, or "redundant" re-validation at a second boundary is intentional layering. Removing it is a data-leak or authz regression, not cleanup. *(E.g. every tenant-scoped read filters by tenant ID, even after an access check.)*
- **Feature-flag / kill-switch / rollout code.** Code behind a flag is *statically unreached with the flag off* yet is a live rollback lever; deleting it removes the ability to turn the feature off in prod. → KEEP until the flag itself is retired as a deliberate, separate step.
- **Compatibility at rest (generalises the enum-at-rest trap).** A column, serialized event/message payload field, or API response field with no *current* code reader may still be **written by a prior deploy, carried by stored rows, in-flight in a queue, or read by an old client**. You cannot delete what the previous version still writes or a persisted record still holds — that's a multi-deploy *expand-contract*, not a sweep. → KEEP; retire in phases.
- **Observability with off-disk consumers.** A metric, log field, or trace attribute with no code *reader* may feed a dashboard or alert defined outside the repo — deleting it silently breaks the alert (same shape as a cross-boundary route). → KEEP unless the dashboard/alert is retired too.
- **Error / cleanup / cancellation paths.** `except CancelledError: <cleanup>; raise`, `finally:` blocks, and compensating rollbacks look like no-ops but are correctness under failure/cancellation. → NEVER "simplify away"; never swallow `CancelledError`.
- **Performance-load-bearing "redundancy".** A cache, an eager-load (`selectinload`), request batching, or a "duplicate-looking" DB index exists to avoid an N+1, a lock, or a hot-path recompute at scale — invisible in a single-row test. → Measure before removing; prove it isn't load-bearing.
