---
name: parallax
description: "Set up Parallax evaluation tracking, run or compare agent evaluations, and create result dashboards. Use for /parallax setup or an explicitly requested Parallax eval campaign."
---

# Parallax evaluations

For `setup`, locate the user's Parallax checkout and read its `AGENTS.md` and
`docs/tracking.md`. Use `uv run parallax setup --help` from the checkout, or the installed CLI; the executable
command is `parallax setup`, while `/parallax setup` invokes this skill.

1. Find the intended non-production tracking project in the consuming repository's
   testing documentation. Obtain project-scoped credentials through the host's
   authorized secret manager or private environment. Keep keys out of command
   arguments, Git, artifacts, logs and user sandboxes.
2. Install the checkout's optional tracking dependencies. Run `uv run parallax setup` from that checkout with
   the documented project and regional service address. Setup is complete when the
   CLI verifies project access and reports its private configuration path.
3. Explain automatic tracking and `--no-track`. Use `parallax track dashboard` when
   a dashboard is requested, and open the returned URL to verify the result where
   browser access permits.

For an eval campaign, read the consuming repository's testing workflow and
Parallax's authoring and adapter docs before selecting fixtures. Use natural user
prompts and negative examples. Verify controls, preserve raw evidence locally,
and obtain authorization before paid calls or external writes that the user has
not already authorized.

Record failures, invalid trials, usage, provenance and tracking receipts alongside
successful trials. Unknown costs or timings stay unknown. Keep raw prompts, answers
and tool payloads private unless their upload is explicitly authorized.

Compare matching task versions, fixture hashes and judge policies. Keep controls,
retries, held-out panels and real-provider evidence distinguishable. Scope dashboard
charts with `--run-id`; do not pool incompatible panels or treat a dashboard as a
promotion decision. Finish with verified run and dashboard links, results, remaining
gaps, and the location of private artifacts without exposing their contents.
