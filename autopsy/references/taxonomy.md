# Agent-harness failure taxonomy

Each class has a **trace signal** that detects it. The thresholds are starting points;
calibrate them against your own p50/p95. Keep the taxonomy open: you'll add classes as
you read traces.

## Latency

Split the wall clock into queue, TTFT, decode, tool, idle and orchestration time. Any
remainder is a finding.

| Class | Signal |
|---|---|
| Queueing / cold start | enqueue → first model span above 1s or p95 |
| TTFT regression | TTFT above p95 for the model/provider; check prompt size and cached tokens |
| Slow decode | tokens/s below p10; reasoning tokens make up most of the output; flex/batch/queued tier |
| Model time dominates | per-lane model time is more than 70% of the span while tools take about 1s each: one small step per model call |
| Serial work | independent calls run back to back when they could overlap |
| Hidden timeout | failures of near-constant duration (a client or connect timeout) |
| Hidden retry | span duration is an exact multiple of a backoff schedule |
| Idle gaps | gap between spans above p95 with no covering span: missing await, polling, locks |

## Tool layer

| Class | Signal |
|---|---|
| Wrong success classification | recorded ok, but the payload shows non-zero exit, stderr, HTTP ≥ 400, "Internal error", or is empty |
| Swallowed failure | an exception in the logs at the span's time, but the span has no error |
| Untyped failure | a failure with no machine-readable error class, so metrics and retry policy can't act on it |
| Unhelpful error text | after the error, the next call repeats the same args or tries another wrong approach; the error text has no remedy |
| Guidance in one tool only | a recovery hint like "retry once, then stop" appears in one tool's error but not in sibling tools that hit the same failure |
| No fail-fast / circuit breaker | the same dead dependency is called 3+ times in a run, across parent and child lanes |
| Misleading description | the model states a capability the tool doesn't have ("it probes devices") |
| Non-idempotent retry | duplicate side effects share one logical call |
| Output bloat / silent truncation | a result above N tokens or above 20% of context; cut with no "narrow it" hint |
| Toolset overlap or misroute | a discovery call routes to the wrong mechanism, e.g. "delegate" when a direct tool exists |

## Orchestration

| Class | Signal |
|---|---|
| Placement ignores known health | a child run starts on a target the parent just saw fail |
| Over- or under-delegation | subagent count doesn't fit the task; the parent explores for minutes before delegating the same exploration |
| Duplicated work | lanes' tool+arg sets overlap by more than 30%; a child re-fetches what the parent knew |
| Result not integrated | the parent's later text never references the child's output |
| Hidden child failure | the child errored or never finished, but the parent reports progress |
| Orphan spans | a span with no end; a child outlives its parent |
| Claimed parallelism | the model says "in parallel" but the lanes run one after another, or on one contended target |

## Context

| Class | Signal |
|---|---|
| Bloat | input tokens grow faster than linearly; any step above 50% of the window |
| Cache misses | cached/input ratio drops between calls sharing a prefix; diff the prefix for timestamps or reordering |
| Stale or duplicated injection | the same block hash twice in one request; data older than a state change in the timeline |
| Self-referential retrieval | memory or search returns the current run's own content and the model treats it as independent ("found a prior thread") |
| Compaction loss | a fact present before compaction is gone after, then re-asked or contradicted |

## Model / provider

| Class | Signal |
|---|---|
| Routing / fallback | served model ≠ requested model; fallback depth ≥ 2; provider varies within one lane |
| Slow upstream behind a router | one model, several upstreams; latency/TTFT per upstream differs by several times and the slow one gets most of the traffic |
| Under-powered tier | a flash or small tier drives a long multi-step task; many tiny steps, poor batching |
| Truncation | finish_reason is length/max_tokens; tool-call JSON cut off |
| Rate limits / 5xx | 429/5xx attempts, including ones the SDK retried and hid |
| Reasoning waste | reasoning tokens far above visible output on trivial steps |

## State / UI

| Class | Signal |
|---|---|
| Progress not propagated | the progress/todo state never changes while child lanes do most of the work |
| Missing events | a tool call that launched a lane has no recorded event of its own; sequence gaps |
| Duplicate render | one logical state emitted or rendered twice; two terminal events |
| Status lies | status "running" or "completed" contradicts the spans |
| Mis-attributed target | the event records the default host/sandbox, while the call's args targeted another one; outage attribution is then wrong |

## Environment

| Class | Signal |
|---|---|
| Dead or intermittent target | connection closed/refused/unreachable; long constant-duration failures |
| Shared-layer outage | several distinct targets fail in the same window: the fault is in a gateway, provider or your client, not one host |
| Read-only / missing path | EROFS, EACCES, ENOENT on the path the agent was told to use |
| Stale checkout | commit date or version on the target is well behind the deployed or expected one |
| Missing auth | 401/403, "run X auth login", an unconnected account |
| Empty env | unset variables, missing binaries |

## Model behaviour (always name the harness input that invited it)

| Class | Signal |
|---|---|
| Ignored instruction | a quoted constraint (system, user or error text) is broken by a later action |
| False claim | assistant text that no tool result supports, or that a tool result contradicts |
| Repetition / oscillation | the same tool+args hash 3+ times; A-B-A-B |
| Premature stop | an announced next step never happens; acceptance criteria unmet |
| Runaway | steps or tokens far above p95 with nothing new learned |
| Reasoning–action mismatch | the plan says X, the next call is Y |
| Reward hacking | tests skipped or stubbed; "verification" that only re-reads its own output |

## Sources

- Anthropic: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents),
  [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents),
  [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents),
  [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents),
  [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- OpenAI: [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- Hamel Husain: [Evals FAQ / error analysis](https://hamel.dev/blog/posts/evals-faq/). Annotate the first upstream failure; review until you reach saturation.
- Shankar et al.: [Who Validates the Validators?](https://arxiv.org/abs/2404.12272). The criteria drift, so keep the taxonomy open.
- Cemri et al.: [Why Do Multi-Agent LLM Systems Fail? (MAST)](https://arxiv.org/abs/2503.13657)
- Yao et al.: [tau-bench](https://arxiv.org/abs/2406.12045)
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)
