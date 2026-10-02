---
name: wayfinder
description: "Plan an effort too big for one agent session as a map issue with decision tickets, resolved one per session until the way to the destination is clear. Use for 'wayfinder', 'map this out', a loose idea spanning many sessions, or a map issue to continue. A single issue goes to /issue."
argument-hint: "[loose idea]  |  [map issue number or URL] [ticket]"
---

# Wayfinder: chart the map, then walk it

A big idea arrives in **fog**: the way to the **destination** is not visible yet. Wayfinder
finds the way. It charts a **map** on the issue tracker and resolves its **tickets**, each a
question whose answer is a decision. It plans; when the pull is to build, the map is finished
and the work goes to `/issue` and `/pr`.

In everything the human reads, refer to a map or ticket by its title, wrapping the link.

## Tracker

Read the repo's tracker doc (`docs/agents/issue-tracker.md`, section "Wayfinding operations")
when it exists. Otherwise use GitHub through `gh`:

- **Map**: one issue labelled `wayfinder:map`.
- **Ticket**: a sub-issue of the map
  (`gh api -X POST repos/{o}/{r}/issues/<map>/sub_issues -F sub_issue_id=<db id>`), labelled
  `wayfinder:<type>`. Fallback: a task list in the map body and `Part of #<map>` in the ticket.
- **Blocking**: native dependencies
  (`gh api -X POST repos/{o}/{r}/issues/<n>/dependencies/blocked_by -F issue_id=<blocker db id>`;
  db id from `gh api repos/{o}/{r}/issues/<n> --jq .id`). Fallback: a `Blocked by: #n` line.
- **Frontier**: the map's open tickets with every blocker closed and nobody assigned.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: comment the answer, close the ticket, append one line to the map.

## The map body

An index. Each decision lives in its ticket; the map gists it and links.

```markdown
## Destination
<what reaching the end looks like: the spec, decision or change. One or two lines.>

## Notes
<domain; skills every session should load; standing preferences>

## Decisions so far
- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified
<the fog: in-scope questions not yet sharp enough to ticket>

## Out of scope
- <gist and why>, linking any ticket closed for it
```

Open tickets are found by query and stay out of the body.

## Tickets

Body: `## Question`, the decision or investigation, sized to one session. The answer goes in
the resolution comment. Assets are linked, never pasted.

| Type | Mode | Resolved by |
|---|---|---|
| `grilling` (default) | HITL | `/grilling` with the user, who speaks for themselves. Record a hard-to-reverse decision as an ADR where the repo keeps them. |
| `research` | AFK | A background agent reads **primary sources** (source code, official docs, specs), follows each claim to the source that owns it, and writes one cited Markdown file where the repo keeps such notes. |
| `prototype` | HITL | A throwaway artifact to react to: a single HTML file driving a state model through its hard cases, or UI variants behind a URL param. It lives on a throwaway branch linked from the ticket; the map keeps the verdict. |
| `task` | either | Manual work a decision waits on (access, a signup, moving data to see its shape). The answer records what was done and the facts later tickets need. |

**Ticket or fog?** Ticket when the question can be stated precisely now, even if blocked. Fog
when it cannot; leave fog coarse.

**Out of scope** is work beyond the destination. Close any such ticket and list it there. It
returns only if the destination is redrawn.

## Chart the map (invoked with an idea)

1. **Name the destination** with `/grilling`. It fixes the scope.
2. **Map the frontier**: grill breadth-first across the whole space for open decisions and the
   steps takeable now. If no fog appears, the effort fits one session: stop and offer `/issue`.
3. Create the map: Destination and Notes filled, fog sketched into Not yet specified.
4. Create every ticket that can be specified now, then wire blocking in a second pass.
5. Start a background agent for each `research` ticket.
6. Stop. Charting is one session's work and resolves nothing by hand.

## Walk the map (invoked with a map)

One ticket per session; `research` tickets are the exception.

1. Load the map body only.
2. Take the named ticket, or the first on the frontier. **Claim it** before any work.
3. Resolve it. Load the skills Notes names; fetch other ticket bodies on demand.
4. Record: resolution comment, close, one line in Decisions so far.
5. Update the map: create newly sharp tickets and remove their patch of fog, wire blocking,
   rule out of scope what the answer pushed past the destination, and fix tickets it
   invalidated.

Done when the frontier and the fog are both empty: nothing is left to decide. Hand the map to
`/issue` as the spec. Other sessions may be editing the tracker concurrently; re-query the
frontier before claiming.

Adapted from mattpocock/skills `wayfinder`, `research` and `prototype`, (c) 2026 Matt Pocock, MIT.
Notice: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
