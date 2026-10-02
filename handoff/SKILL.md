---
name: handoff
description: "Compact the current conversation into a handoff document a fresh agent can continue from. Use for 'handoff', 'hand this off', or before ending a session with work still open."
argument-hint: "[what the next session will focus on]"
---

# Handoff

Write one Markdown file to the OS temp directory, outside the workspace, and report its path.
Tailor it to the focus the user passed, if any.

Contents, in order:

1. **Goal** and the user's decisions so far, including rejected approaches and why.
2. **State**: what is implemented, verified, committed, pushed. Name the branch, worktree and PR.
3. **Open**: failing checks with exact error text, unanswered questions, and the single next
   verification step.
4. **Pointers**: paths and URLs for every existing artifact (plans, specs, issues, ADRs,
   commits). Link them; their content stays where it is.
5. **Suggested skills** for the next agent to load.

Redact secrets and personal data. Done when a reader with only this file and the repo could
take the next step without asking.

Adapted from mattpocock/skills `handoff`, (c) 2026 Matt Pocock, MIT.
Notice: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
