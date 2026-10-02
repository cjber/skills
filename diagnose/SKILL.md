---
name: diagnose
description: "Diagnose a bug or performance regression by building a tight, red-capable loop before theorising, then fixing at the producer. Use for 'diagnose', 'debug this', or a report that something is broken, throwing, flaky or slow in code you can run. For one production agent run use autopsy."
argument-hint: "[symptom, error text, failing command, or issue number]"
---

# Diagnose with a loop, then fix the producer

A bug with a **tight** loop that goes **red** on it is nearly fixed; a bug without one is a
guessing game. Build the loop first. Repository instructions win wherever they are stricter.

Redact secrets in everything you show: keep credentials in env vars and write `<REDACTED>` in
quoted output.

## 1. Build the loop

One command that goes red on this bug and green once it is fixed. Try, roughly in this order:

1. An existing failing check, or a focused test at the seam that reaches the bug.
2. A curl or CLI invocation against a running dev stack, diffed against known-good output.
3. A replayed capture: a real request, payload, event log or trace run through the code path.
4. A throwaway harness that calls the suspect path directly.
5. A differential: same input through old and new commit, or two configs, outputs diffed.
6. `git bisect run` when the bug appeared between two known states.
7. A browser script asserting on DOM, console or network.
8. A scripted human step, when only a person can trigger it: the script prompts, captures, asserts.

Then tighten it: narrow the scope until it runs in seconds, assert the exact symptom, pin time,
seeds and network. For a flaky bug raise the reproduction rate (repeat, parallelise, add load,
inject sleeps) until it is high enough to debug against.

**Done when** you have run one command, shown its redacted output, and it is:

- **Red-capable**: drives the real code path and asserts the user's symptom, the one they reported.
- **Deterministic**: same verdict each run, or a pinned high rate for a flaky bug.
- **Fast** and **agent-runnable**.

Reading code to form a theory before this command exists is the failure this skill prevents.
If no loop can be built, stop: list what you tried and ask for the environment that reproduces
it, a captured artifact, or leave to add temporary instrumentation.

## 2. Minimise

Cut inputs, callers, config and data one at a time, re-running after each cut. Done when every
remaining element is load-bearing: removing any one turns the loop green.

## 3. Hypothesise

Write 3-5 ranked hypotheses before testing any. Each states a prediction: "if X is the cause,
changing Y makes it disappear." One without a prediction is discarded. Show the list; the user
often re-ranks it instantly. Proceed on your own ranking if they are away.

## 4. Probe

One probe per prediction, one variable at a time. Prefer a debugger or REPL, then targeted logs
at the boundary that separates two hypotheses. Tag every temporary log with one unique prefix
(`[DBG-a4f2]`) so cleanup is a single grep.

**Performance**: measure a baseline first (timing harness, profiler, query plan), then bisect.

## 5. Fix at the producer

Trace the wrong value to where it is first produced and fix it there, so every consumer inherits
the correction. Then audit what silently depended on the old behaviour. A patch at the consumer
that showed the symptom leaves the other consumers broken.

Re-run the loop against the original, un-minimised scenario.

Keep the loop as a permanent test when it is the cheapest durable protection for a regression
likely to recur and a seam exists that exercises the real bug pattern. Otherwise delete it. A
bug with no seam to test it through is itself a finding: report it.

## 6. Close out

- The step-1 command is green on the original scenario.
- `grep` for the debug prefix returns nothing; harnesses and scratch files are deleted.
- The commit or PR message names the confirmed hypothesis and the producer that was fixed.
- Hand the change to `/pr`, or report the diagnosis if no fix was requested.

Adapted from mattpocock/skills `diagnosing-bugs`, (c) 2026 Matt Pocock, MIT.
Notice: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
