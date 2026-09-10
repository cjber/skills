#!/usr/bin/env python3
"""Normalise an agent trace into one timeline and run mechanical bug detectors.

Input: JSONL, one record per span/event, in the canonical schema below. Write a
small per-project adapter that emits it (see references/sources.md); this script
never talks to a backend itself.

    {
      "ts": 1789027235843,            # start, epoch ms or ISO-8601 (required)
      "end": 1789027238043,           # end, same format (optional; instant if absent)
      "lane": "root",                 # run / sub-agent / nested-run id (parallel lanes)
      "kind": "tool|llm|message|log|state",
      "name": "bash",                 # tool name, model name, log logger, message role
      "call_id": "call_1",            # optional, to pair request/result
      "args": {...} | "str",          # tool arguments
      "result": {...} | "str",        # tool result / llm output excerpt
      "ok": true | false | null,      # what the harness RECORDED as success
      "error": "str" | null,
      "error_type": "str" | null,     # typed failure class, if the harness has one
      "target": "device-1",           # where it ran: sandbox, host, account, endpoint
      "model": "provider/model",
      "tokens_in": 0, "tokens_cached": 0, "tokens_out": 0, "tokens_reasoning": 0,
      "ttft_ms": 0, "finish_reason": "stop",
      "text": "assistant/user text",   # for kind=message
      "level": "ERROR"                 # for kind=log
    }

Usage:  autopsy.py trace.jsonl [--out DIR]
Writes DIR/timeline.md and DIR/findings.json and prints a summary. Every
detector hit is a CANDIDATE for the auditor to explain with evidence, not a verdict.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

STOP_HINTS = re.compile(r"stop retrying|do not retry|don't retry|retry once|one retry|give up|is down", re.I)
# Strong markers mean the call really failed; a bare non-zero exit is often benign (grep with no match).
HIDDEN_FAILURE = re.compile(
    r"Traceback \(most recent|Internal error|command not found|Permission denied|Read-only file system|"
    r"fatal:|ERR!|panic:|exited with code (?:12[6-9]|255)",
    re.I,
)
NONZERO_EXIT = re.compile(r'"?exit_code"?\s*[:=]\s*(?!0\b)-?\d+|exited with code (?!0\b)\d+', re.I)
ENV_SMELLS = {
    "read-only filesystem": re.compile(r"Read-only file system", re.I),
    "missing auth": re.compile(r"auth login|unauthori[sz]ed|401\b|403\b|invalid credentials|token expired", re.I),
    "rate limited": re.compile(r"\b429\b|rate.?limit|quota", re.I),
    "timeout": re.compile(r"timed? ?out|deadline exceeded", re.I),
    "connection loss": re.compile(r"connection (closed|reset|refused)|unreachable|EOF", re.I),
    "truncated output": re.compile(r"truncat", re.I),
}
GAP_FLOOR_MS = 20_000


def to_ms(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v if v > 1e11 else v * 1000)
    return int(dt.datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp() * 1000)


def clock(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.UTC).strftime("%H:%M:%S")


def text_of(v, n=None):
    s = v if isinstance(v, str) else json.dumps(v, default=str) if v is not None else ""
    return s if n is None else s[:n]


def load(path):
    recs = []
    for i, line in enumerate(Path(path).read_text().splitlines()):
        if not line.strip():
            continue
        r = json.loads(line)
        r["ts"] = to_ms(r["ts"])
        r["end"] = to_ms(r.get("end")) or r["ts"]
        r.setdefault("lane", "root")
        r.setdefault("kind", "tool")
        r["_i"] = i
        recs.append(r)
    return sorted(recs, key=lambda r: (r["ts"], r["_i"]))


def union_ms(spans):
    total, cur = 0, None
    for a, b in sorted(spans):
        if cur and a <= cur[1]:
            cur[1] = max(cur[1], b)
        else:
            total += (cur[1] - cur[0]) if cur else 0
            cur = [a, b]
    return total + ((cur[1] - cur[0]) if cur else 0)


def budget(recs):
    rows = []
    for lane in sorted({r["lane"] for r in recs}):
        rs = [r for r in recs if r["lane"] == lane]
        span = max(r["end"] for r in rs) - min(r["ts"] for r in rs)
        tool = union_ms([(r["ts"], r["end"]) for r in rs if r["kind"] == "tool"])
        llm = union_ms([(r["ts"], r["end"]) for r in rs if r["kind"] == "llm"])
        both = union_ms([(r["ts"], r["end"]) for r in rs if r["kind"] in ("tool", "llm")])
        failed = sum(r["end"] - r["ts"] for r in rs if r["kind"] == "tool" and r.get("ok") is False)
        rows.append(
            {
                "lane": lane,
                "span_s": span / 1000,
                "tool_s": tool / 1000,
                "llm_s": llm / 1000,
                "unaccounted_s": (span - both) / 1000,
                "failed_tool_s": failed / 1000,
                "tool_calls": sum(r["kind"] == "tool" for r in rs),
                "llm_calls": sum(r["kind"] == "llm" for r in rs),
            }
        )
    return rows


def detect(recs):
    f = []

    def hit(kind, sev, msg, refs):
        f.append({"detector": kind, "severity": sev, "message": msg, "refs": refs})

    tools = [r for r in recs if r["kind"] == "tool"]

    # Recorded success that the payload contradicts.
    soft = []
    untyped = defaultdict(list)
    for r in tools:
        body = text_of(r.get("result"))
        if r.get("ok") is True and (m := HIDDEN_FAILURE.search(body)):
            hit("success-but-failed", "high", f"{r['name']} recorded ok but result shows {m.group(0)!r}", [r["_i"]])
        elif r.get("ok") is True and NONZERO_EXIT.search(body):
            soft.append(r)
        if r.get("ok") is False and not r.get("error_type"):
            untyped[(r["name"], text_of(r.get("error"), 60))].append(r)
    if soft:
        hit("nonzero-exit-recorded-ok", "low", f"{len(soft)} call(s) exited non-zero but were recorded ok; "
            "check each is benign (e.g. grep no-match) and that the model read it that way", [r["_i"] for r in soft])
    for (name, err), rs in untyped.items():
        hit("untyped-failure", "medium", f"{len(rs)}x {name} failed with no error_type: {err!r}", [r["_i"] for r in rs])

    # Identical calls repeated.
    by_hash = defaultdict(list)
    for r in tools:
        by_hash[hashlib.sha1((r["name"] + text_of(r.get("args"))).encode()).hexdigest()].append(r)
    for rs in by_hash.values():
        if len(rs) >= 3:
            hit("repeated-identical-call", "medium", f"{rs[0]['name']} called {len(rs)}x with identical args",
                [r["_i"] for r in rs])

    # Same failure signature against the same target, and constant-duration failures (timeouts).
    sig = defaultdict(list)
    for r in tools:
        if r.get("ok") is False:
            sig[(r.get("target"), re.sub(r"\d+", "N", text_of(r.get("error"), 80)))].append(r)
    for (target, err), rs in sig.items():
        if len(rs) >= 2:
            durs = [(r["end"] - r["ts"]) / 1000 for r in rs]
            lanes = {r["lane"] for r in rs}
            hit("repeated-failure-no-circuit-breaker", "high",
                f"{len(rs)} failures '{err}' on target={target} across {len(lanes)} lane(s), "
                f"{sum(durs):.0f}s lost", [r["_i"] for r in rs])
            if len(durs) >= 3 and statistics.pstdev(durs) < 0.1 * statistics.mean(durs):
                hit("constant-duration-failure", "medium",
                    f"failures take ~{statistics.mean(durs):.1f}s each: a timeout, not work", [r["_i"] for r in rs])

    # One failure signature on several distinct targets at once: a shared layer, not one host.
    by_err = defaultdict(list)
    for (target, err), rs in sig.items():
        by_err[err].extend(rs)
    for err, rs in by_err.items():
        targets = {r.get("target") for r in rs}
        window = max(r["end"] for r in rs) - min(r["ts"] for r in rs)
        if len(targets) >= 2 and window <= 15 * 60_000:
            hit("shared-layer-outage", "high", f"'{err}' on {len(targets)} distinct targets within "
                f"{window / 1000:.0f}s: suspect the gateway/provider/client, not one host", [r["_i"] for r in rs])

    # Retries after the harness told the model to stop.
    for i, r in enumerate(tools):
        if r.get("ok") is False and STOP_HINTS.search(text_of(r.get("error")) + text_of(r.get("result"))):
            later = [x for x in tools[i + 1:] if x.get("target") == r.get("target") and x.get("ok") is False]
            if later:
                hit("ignored-stop-instruction", "high",
                    f"error told the model to stop retrying; {len(later)} further failures on the same target",
                    [r["_i"]] + [x["_i"] for x in later])

    # Environment smells in any tool payload.
    for label, rx in ENV_SMELLS.items():
        rs = [r for r in tools if rx.search(text_of(r.get("result")) + text_of(r.get("error")))]
        if rs:
            hit(f"env:{label}", "medium", f"{len(rs)} tool result(s) mention {label}", [r["_i"] for r in rs])

    # Dead air: gaps between actions not covered by any recorded span.
    for lane in {r["lane"] for r in recs}:
        rs = [r for r in recs if r["lane"] == lane and r["kind"] in ("tool", "llm", "message")]
        gaps = []
        horizon = None
        for r in rs:
            if horizon is not None and r["ts"] - horizon > 0:
                gaps.append((r["ts"] - horizon, r))
            horizon = max(horizon or 0, r["end"])
        if gaps:
            vals = sorted(g for g, _ in gaps)
            p50 = vals[len(vals) // 2]
            for g, r in gaps:
                if g >= max(GAP_FLOOR_MS, 3 * p50):
                    hit("long-gap", "medium", f"lane {lane}: {g / 1000:.0f}s before {r['name']} "
                        f"(lane median gap {p50 / 1000:.0f}s)", [r["_i"]])

    # LLM-side signals.
    llms = [r for r in recs if r["kind"] == "llm"]
    for r in llms:
        dur = r["end"] - r["ts"]
        if r.get("ttft_ms") and dur and r["ttft_ms"] / dur > 0.6 and dur > 10_000:
            hit("ttft-dominated", "medium", f"{r.get('model')}: {r['ttft_ms'] / 1000:.0f}s of {dur / 1000:.0f}s "
                "before first token (queueing/provider/reasoning)", [r["_i"]])
        if r.get("finish_reason") in ("length", "max_tokens"):
            hit("truncated-generation", "high", f"{r.get('model')} stopped on {r['finish_reason']}", [r["_i"]])
        tin, tc = r.get("tokens_in") or 0, r.get("tokens_cached") or 0
        if tin > 20_000 and tc / tin < 0.3:
            hit("cache-miss", "medium", f"{r.get('model')}: {tin} input tokens, only {tc} cached", [r["_i"]])
    if len(llms) >= 4:
        ins = [r.get("tokens_in") or 0 for r in llms]
        if ins[-1] > 3 * max(ins[0], 1):
            hit("context-growth", "low", f"input tokens grew {ins[0]} -> {ins[-1]} over {len(llms)} calls",
                [llms[0]["_i"], llms[-1]["_i"]])
    models = Counter((r["lane"], r.get("model")) for r in llms)
    for lane in {l for l, _ in models}:
        ms = [m for l, m in models if l == lane]
        if len(ms) > 1:
            hit("model-switch", "low", f"lane {lane} used several models: {ms}", [])

    # Progress/state that never moved while work happened.
    states = [r for r in recs if r["kind"] == "state"]
    if states and len(tools) > 10 and len({text_of(s.get("result")) for s in states}) == 1:
        hit("stale-progress", "medium", f"{len(tools)} tool calls but progress state never changed", [s["_i"] for s in states])

    return f


def timeline_md(recs, rows):
    out = ["# Timeline", "", "| lane | span | tool | llm | unaccounted | failed tool | tools | llm calls |", "|---|---|---|---|---|---|---|---|"]
    for b in rows:
        out.append(f"| {b['lane']} | {b['span_s']:.0f}s | {b['tool_s']:.0f}s | {b['llm_s']:.0f}s | "
                   f"{b['unaccounted_s']:.0f}s | {b['failed_tool_s']:.0f}s | {b['tool_calls']} | {b['llm_calls']} |")
    out += ["", "| # | start | +gap | dur | lane | kind | name | ok | target | detail |", "|---|---|---|---|---|---|---|---|---|---|"]
    prev = {}
    for r in recs:
        gap = (r["ts"] - prev[r["lane"]]) / 1000 if r["lane"] in prev else 0
        prev[r["lane"]] = max(prev.get(r["lane"], 0), r["end"])
        detail = r.get("text") or r.get("error") or r.get("args") or r.get("result")
        detail = text_of(detail, 140).replace("|", "\\|").replace("\n", " ")
        out.append(f"| {r['_i']} | {clock(r['ts'])} | {gap:+.1f}s | {(r['end'] - r['ts']) / 1000:.1f}s | {r['lane']} | "
                   f"{r['kind']} | {r.get('name', '')} | {r.get('ok', '')} | {r.get('target', '')} | {detail} |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    recs = load(a.trace)
    rows = budget(recs)
    findings = detect(recs)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "timeline.md").write_text(timeline_md(recs, rows))
    (out / "findings.json").write_text(json.dumps({"budget": rows, "findings": findings}, indent=1))
    for b in rows:
        print(f"lane {b['lane']}: span {b['span_s']:.0f}s = tool {b['tool_s']:.0f}s + llm {b['llm_s']:.0f}s "
              f"+ unaccounted {b['unaccounted_s']:.0f}s (failed tools {b['failed_tool_s']:.0f}s)")
    for x in sorted(findings, key=lambda x: ["high", "medium", "low"].index(x["severity"])):
        print(f"[{x['severity']}] {x['detector']}: {x['message']}  refs={x['refs'][:8]}")
    print(f"\n{len(recs)} records, {len(findings)} candidate findings -> {out}/timeline.md, {out}/findings.json")


if __name__ == "__main__":
    main()
