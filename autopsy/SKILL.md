---
name: autopsy
description: "Forensic audit of LLM agent runs. With no argument, sweeps production: samples the worst runs plus a baseline, clusters defects by root cause, and ranks them by users affected. Give it a thread/run/trace id, a screenshot, or pasted text; it pulls the full trace (observability spans, app events, cloud logs), rebuilds one timeline, and reports every harness, tool, prompt, orchestration, environment, provider and model-behaviour defect with evidence, root cause and fix. Use when a run was slow, looped, failed, lied, or 'just felt wrong', or when asked why an agent task took so long."
---

# /autopsy — explain every second and every oddity of one agent run

The job is not "find the bug". It is: **account for the whole run**. Every second
of wall clock goes into a budget. Every anomaly gets a cause backed by evidence.
Nothing gets filed under "flaky", "transient", "LLM nondeterminism" or "the
model just does that". Those are what you write when you haven't found the cause yet.

## Ground rules

- **Read-only.** Never write to the systems you inspect. That includes minting tokens,
  re-running the task on production, or copying files into a live host. Reproduce
  locally if you need proof.
- **Privacy.** Fetch only the fields you need. Never paste full prompts, user
  content, or secrets into the report. Quote short excerpts and cite ids.
- **Evidence or it didn't happen.** Every claim in the report cites a span id, event
  id, log line, or timestamp. Anything you can't prove goes in *Unexplained*,
  along with the telemetry that would settle it.
- **Model behaviour is a symptom.** When the model does something dumb, name the
  harness input that allowed or invited it: the tool description, the error text,
  a prompt section, the retrieved context, routing. If none exists, the fix is an
  eval case with a negative example, not a shrug.
- **Transient is a symptom.** For a timeout, 429 or dropped connection, name the
  upstream event, then the missing defence: fail-fast, circuit breaker, fallback,
  or surfacing the problem to the user.
- **Root cause at the producer.** Group cascaded symptoms under the first place the
  value went wrong. Don't list five findings that are one bug.

## 0. No argument = production sweep

`/autopsy` with no argument audits **production as a population**, not one run.

1. **Window.** Default to the last 24h. If the user names a window, use theirs.
2. **Candidates.** Use the profile's *sweep query* to list runs in the window with cheap
   signals: wall-clock duration, tool-call count, failed-call count, the share of
   calls that failed, the max gap between steps, whether the run finished, and
   warnings/errors in the logs keyed to it.
3. **Sample.** Take the worst ~10 by each signal, dedupe, and add ~5 random
   *normal* runs as a baseline. Without the baseline you can't tell a bug from how
   everything behaves. Cap the total at ~25 runs; say how many runs were in the
   window and how you picked.
4. **Audit.** Fetch and adapt each run, then run the detectors over all of them at once:
   `autopsy.py run1.jsonl run2.jsonl ... --out <dir>` writes per-run output plus
   `sweep.md`, which ranks detector classes by severity and by how many runs hit them.
5. **Cluster by root cause, not by run.** Hits that share a producer are one finding.
   Examples: the same error signature, target, tool, or window. Count the runs and
   users each finding affects, and the seconds it cost. A class that shows up in the
   baseline too is systemic.
6. **Cross-check at population level.** Is a spike one tenant, one target, one model,
   one release? Compare against the previous window and the deployed-version change.
   Correlate with the platform-health logs.
7. **Deep-walk the top findings.** For each of the top ~5 clusters, pick its worst
   run and do the full per-run audit below (steps 5–8) to get a root cause at
   file:line.
8. **Report.** Findings ranked by users affected × cost. Give each the runs and users
   affected, the seconds lost, one exemplar run id, root cause, fix, class guard and
   verification. Then list the unexplained anomalies and a coverage statement: runs
   in the window, runs audited, sources reached.

## 1. Resolve the input

| Input | Do |
|---|---|
| id (thread, run, trace, session) | use it directly |
| screenshot | read it; extract title, timestamps, user, step labels and quoted text; search the app DB or trace store by title/text within a ±1 day window |
| pasted text | search for distinctive phrases; the same method as a screenshot |

Titles often change after creation. Match loosely, then confirm on the user and
the time. Say which id you settled on and why.

## 2. Load the project profile

Where the traces live is project knowledge, not skill knowledge. Look in order:

1. `./.claude/autopsy.md` in the current repo
2. `~/.claude/autopsy/<repo-name>.md`

A profile says how to reach each source read-only: the app event store, the
observability backend (Langfuse / LangSmith / Phoenix / OTel), cloud logs, the
deployed-version lookup, a **sweep query** that lists runs in a window with cheap
health signals, and an **adapter** that emits the canonical JSONL below.
If there is no profile, build one with the user from
[`references/sources.md`](references/sources.md) and save it. Don't hardcode any
of it into this skill.

## 3. Collect everything, and record what's missing

For the run's window (±5 min), pull:

- **App events.** Messages, tool calls with args and results, status and progress rows.
- **Model spans.** Every generation: model requested vs served, provider, latency,
  TTFT, tokens (in / cached / out / reasoning), finish reason, errors, retries,
  fallbacks.
- **Logs.** Everything carrying the run's ids, plus platform health in the window:
  restarts, queue depth, slow queries, outages of the sandbox or provider.
- **Environment.** The deployed version/SHA, and where each tool ran (host, sandbox,
  account). Record its state: writable, authenticated, how fresh its checkout is.
- **Baseline.** The same model/tool's p50/p95 across all traffic in the same hour.
  Without a baseline you can't tell "this run was slow" from "everything was slow".

A source you can't reach is a finding: an observability gap.

## 4. Normalise and run the detectors

Have the adapter emit one JSONL record per span/event in the canonical schema
documented at the top of `scripts/autopsy.py`. The fields are `ts`, `end`, `lane`, `kind`,
`name`, `args`, `result`, `ok`, `error`, `error_type`, `target`, `model`,
`tokens_*`, `ttft_ms`, `finish_reason` and `text`. Then:

```bash
python3 <skill-dir>/scripts/autopsy.py trace.jsonl --out <dir>
```

It writes `timeline.md` (a per-lane time budget plus every record with its gap and
duration) and `findings.json` (candidate hits). Treat each detector hit as a lead
to explain. It is not a finding until you've traced it. The detectors cover
recorded-success-but-failed, untyped failures, repeated identical calls, repeated
failures with no circuit breaker, one failure hitting several targets at once
(a shared-layer outage), constant-duration failures (timeouts),
retrying after being told to stop, environment smells (read-only filesystem,
auth, rate limits, connection loss), long gaps, TTFT-dominated calls, truncation,
cache misses, context growth, model switches and progress that never moved.

## 5. Budget the time

Split each lane's wall clock into **tool**, **model** (TTFT and decode separately),
**failed-tool** and **unaccounted** time. The parts must add up to the total. The
dominant cost goes first in the verdict. Unaccounted time is a finding: a missing
span, queueing, a serial loop, or lock waits. Compare per-call latency to the
baseline before blaming the model or the provider.

## 6. Walk every step

For every model call and tool call, in order, ask:

1. **What did it see?** The prompt or context diff since the last step, the injected
   blocks, what retrieval returned (is any of it its *own* output?).
2. **What did it decide?** Check the tool and args against that tool's description and
   schema. Could the description have misled it?
3. **What came back?** The payload vs how the harness *classified* it (ok/failed,
   typed error). Did the error text tell it how to recover?
4. **What did it do next?** Did it follow the guidance, retry the same thing, or
   switch approach? Would parallel calls have been possible?

Open-code each oddity as free text first, then map it onto
[`references/taxonomy.md`](references/taxonomy.md). New classes are allowed.
Walk **every** step and report the count walked. "Exhaustive" has to be checkable.

## 7. Check claims against evidence

List every factual, capability or completion claim in the assistant's text and in
the UI: "the harness probes devices", "found a prior thread", "done",
"sandbox recovered", progress "2/8". Give each one supporting or contradicting
evidence and a verdict. An unsupported claim about the harness's own abilities
means the prompt or tool description taught it that. Find where.

## 8. Root cause, fix, class guard, verification

For each root cause, read the code or config that produced it. That means installed
source and the deployed SHA, not your memory of how the code works. Give:

- **Root cause**: file:line or config key
- **Fix**: at the producer; one fix per root cause
- **Class guard**: what stops the whole class recurring. Examples: a success-classification
  rule, a per-target circuit breaker, a typed error, a cache-stable prefix, an
  eval case with a negative example.
- **Verification**: a re-run with the model pinned, a metric that should move and
  by how much, a log line that should appear or disappear. Repeat k times; one pass
  proves little.

## 9. Report

Write the report in this order:

1. **Verdict.** 3 lines: why the run was slow or wrong, with the dominant costs in seconds.
2. **Header.** Ids, window, deployed version, models, sources pulled or missing.
3. **Time budget.** Per lane: tool / model / failed / unaccounted.
4. **Timeline.** Collapse healthy stretches. Never collapse an anomaly.
5. **Claims vs evidence** table.
6. **Findings**, P0→P3. For each: ID, title, class, evidence, root cause, cascade,
   fix, class guard, verification. The severities are:
   - **P0**: wrong outcome, data loss, or a false claim to the user
   - **P1**: user-visible degradation, or more than 2x the time or cost
   - **P2**: latent or efficiency
   - **P3**: hygiene or observability gap
7. **Unexplained** anomalies and telemetry gaps. These are never omitted.
8. **Coverage.** Steps walked, steps with no finding, sources not reached.

Offer to file the findings as issues and to fix the clear bugs. Do neither until
the user says so.
