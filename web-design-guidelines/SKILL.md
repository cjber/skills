---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files, or all public routes and shared components for a full-site audit.
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files are specified, review all public routes and shared components.

## Maintained adaptation

Adapted from vercel-labs/agent-skills web-design-guidelines. Upstream source:
https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines

Project instructions override upstream typography and copy preferences. Preserve
the product's chosen theme, voice and layout. Inspect rendered pages as well as
source. Include navigation, theme discoverability and persistence, landmarks,
keyboard access, touch targets, motion, media, metadata and responsive content.
Verify findings before changing code, then add browser coverage for the behavior
that failed. Report remaining limitations separately from verified fixes.

For a copy audit, apply [copywriting](../copywriting/SKILL.md) to public text,
metadata, labels and empty states. Preserve factual limits and measurement caveats;
verify the rewritten text in the rendered interface. Prose-only changes do not need
a test that repeats the new wording.
