# Trace sources and writing a project profile

A profile is a short markdown file at `./.claude/autopsy.md` (committed, if your team
shares it) or `~/.claude/autopsy/<repo>.md` (private). It answers six questions, and
for each one gives a **read-only** command:

1. **How do I turn a screenshot or title into an id?** For example, a SQL lookup on the
   threads/runs table, or a trace search by name.
2. **Where are the app events?** Messages, tool calls with args and results, status and progress.
3. **Where are the model spans?** The observability backend.
4. **Where are the logs, and where is platform health?**
5. **What was deployed, and where did the tools run?**
6. **Sweep query:** which runs happened in a window, with cheap health signals per run
   (duration, tool calls, failed calls, max gap, finished?), so no-argument mode can
   pick the worst plus a baseline without fetching everything.

It also names an **adapter** that turns those sources into the canonical JSONL
(`scripts/autopsy.py` documents the schema). Keep the adapter next to the profile. It
is project code.

Never put credentials in a profile. Point to where they live: an env file, a
password manager entry, or a CLI config.

## Observability backends

**Langfuse** (public API, basic auth `public:secret`; use your region's host)
- `GET /api/public/traces?sessionId=<id>&fromTimestamp=<iso>` returns the traces in a session
- `GET /api/public/observations?traceId=<id>&type=GENERATION&limit=100&page=N`
- Fields: `startTime`, `endTime`, `completionStartTime` (TTFT = this − start),
  `model`, `usageDetails` (input / output / cache_read / reasoning), `level`,
  `statusMessage`, `metadata`.
- `meta.totalItems` gives exact counts for baselines without paging.

**LangSmith**
- `client.list_runs(project_name=..., trace_id=...)` or `filter='eq(thread_id, "...")'`
- Fields: `start_time`, `end_time`, `first_token_time`, `run_type` (llm/tool/chain),
  `prompt_tokens`, `completion_tokens`, `error`, `parent_run_id`.

**Arize Phoenix / any OTel GenAI backend**
- Query spans by trace id. Map `gen_ai.operation.name` (chat, execute_tool,
  invoke_agent) → `kind`, `gen_ai.request.model` vs `gen_ai.response.model`,
  `gen_ai.usage.input_tokens` / `cache_read` / `output_tokens`,
  `gen_ai.response.finish_reasons`, `gen_ai.tool.call.id`, `error.type`.
- The parent span id gives you `lane`: each agent/subagent root is a lane.

## App event stores

Most agent products persist messages and tool executions in their own DB. Find:

- the table and the id columns (thread/run, the id of the call that launched a nested run)
- whether args/results are persisted in full or redacted
- the timestamp unit (epoch ms vs timestamptz)
- partitioning, since big event tables should be queried by partition

Query a read replica if you have one. Filter by id and time; never scan the whole table.

## Logs

- **GCP**: `gcloud logging read '<filter>' --freshness=2h --format='value(timestamp,severity,jsonPayload.message)'`
  with a read-only configuration or service account.
- **AWS**: `aws logs filter-log-events --log-group-name ... --filter-pattern '"<id>"'`
- **Kubernetes**: `kubectl logs` / `get pods` / `describe` for restarts and OOM kills. Only read.

Search by every id you have: the run, the thread, each tool call id, the target (sandbox or host) id. A
cross-tenant count of the same error in the same window separates "this run" from
"platform incident".

## Adapter checklist

- One record per tool call: pair request and result events on the call id; `ts` =
  request time, `end` = result time.
- `lane` = the id of the call that spawned the nested run; `root` for the top level.
- `ok` = what the harness **recorded**. Don't fix it up. The detectors compare it
  with the payload.
- `target` = where the call **actually** ran: device, sandbox, host or account. Prefer an explicit target
  argument over a recorded default, and cross-check the two; a mismatch is itself a finding.
- Emit progress/todo snapshots as `kind: "state"`, and assistant/user text as `kind: "message"`.
- Emit model generations as `kind: "llm"` with tokens, TTFT and finish reason.
