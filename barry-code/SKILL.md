---
name: barry-code
description: Run a coding task with the Barry coding team workflow. Use when the user invokes /barry-code.
---

# /barry-code

Run the current coding task using the `barry-coding-team` skill. Read its instructions and follow them for scoping, assigning work across Barry Claude, Barry Codex and Barry OpenCode, coordinating artifacts, integrating changes, and reporting the result.

Treat the user's text after `/barry-code` as the task brief. If no brief follows, use the request in the current conversation. Start by inspecting the active repository and working tree; do not invent a task when neither contains a clear request.
