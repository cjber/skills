#!/usr/bin/env python3
"""Render a beads workspace as a single self-contained HTML dashboard.

Usage: dashboard.py export.jsonl out.html [owner/repo] [--title TITLE]

Run from the beads workspace. The title defaults to BEADS_WORKSPACE's directory
name, then the nearest ancestor containing .beads/, then the current directory.
GitHub issue links are omitted unless a repository is supplied.

The layout follows the tool's own metaphor: each track is a thread, its issues
strung along it as beads coloured by state.
"""

import argparse
import html
import json
import os
from collections import defaultdict
from pathlib import Path

PRIO = {0: "now", 1: "next", 2: "parallel", 3: "later", 4: "backlog"}


def workspace_root():
    configured = os.environ.get("BEADS_WORKSPACE")
    if configured:
        return Path(configured).expanduser().resolve()
    current = Path.cwd()
    return next(
        (path for path in (current, *current.parents) if (path / ".beads").is_dir()),
        current,
    )


def load(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return [r for r in rows if r.get("issue_type") in {"task", "bug", "feature", "epic", "chore"}]


def build(rows, repo=None, title=None):
    by_id = {r["id"]: r for r in rows}
    blockers = defaultdict(list)
    parents = {}
    for r in rows:
        if "." in r["id"]:
            parents[r["id"]] = r["id"].rsplit(".", 1)[0]
        for d in r.get("dependencies") or []:
            dep_id = d.get("depends_on_id") or d.get("id") or d.get("target")
            if d.get("type") == "parent-child" and dep_id:
                parents[r["id"]] = dep_id
            if d.get("type") == "blocks" and dep_id and by_id.get(dep_id, {}).get("status") != "closed":
                blockers[r["id"]].append(dep_id)

    def track_labels(row):
        return [label for label in (row.get("labels") or []) if label.startswith("track-")]

    epics = {}
    for r in rows:
        if r.get("issue_type") == "epic":
            for track in track_labels(r):
                epics[track] = r

    def track_for(row):
        seen = set()
        while row and row["id"] not in seen:
            seen.add(row["id"])
            labels = track_labels(row)
            if labels:
                return labels[0]
            row = by_id.get(parents.get(row["id"]))
        return None

    e = html.escape
    open_rows = [r for r in rows if r["status"] != "closed" and r.get("issue_type") != "epic"]
    blocked = [r for r in open_rows if blockers.get(r["id"])]
    decisions = [r for r in open_rows if "decision" in (r.get("labels") or [])]
    ready = [r for r in open_rows if not blockers.get(r["id"])]
    tracks = defaultdict(list)
    for row in open_rows:
        tracks[track_for(row)].append(row)

    def bead(r):
        bid = r["id"]
        p = r.get("priority", 2)
        blk = blockers.get(bid) or []
        state = "blocked" if blk else ("decision" if "decision" in (r.get("labels") or []) else f"p{p}")
        ref = (r.get("external_ref") or "").strip()
        ref_html = ""
        if ref.startswith("gh-") and ref[3:].isdigit() and repo:
            n = ref[3:]
            ref_html = f'<a class="ref" href="https://github.com/{e(repo)}/issues/{e(n)}" target="_blank" rel="noopener">#{e(n)}</a>'
        wait = ""
        if blk:
            names = ", ".join(e(by_id[b]["title"][:38]) if b in by_id else e(b) for b in blk)
            wait = f'<p class="wait">waiting on <span>{names}</span></p>'
        return (
            f'<li class="bead {state}">'
            f'<span class="node" aria-hidden="true"></span>'
            f'<div class="body"><p class="ttl">{e(r["title"])}</p>'
            f'<p class="meta"><code>{e(bid)}</code>'
            f'<span class="tag">{PRIO.get(p, "p" + str(p))}</span>{ref_html}</p>{wait}</div></li>'
        )

    panels = []
    for key in sorted(tracks, key=lambda key: (key is None, key or "")):
        label = epics.get(key, {}).get("title") or key or "Other work"
        kids = sorted(tracks[key], key=lambda r: (r.get("priority", 2), r["id"]))
        nblk = sum(1 for k in kids if blockers.get(k["id"]))
        panels.append(
            f'<section class="track"><header><h2>{e(label)}</h2>'
            f'<p class="count">{len(kids)} open{f" · {nblk} blocked" if nblk else ""}</p></header>'
            f'<ul class="thread">{"".join(bead(k) for k in kids)}</ul></section>'
        )

    dec_html = "".join(
        f'<li><code>{e(d["id"])}</code> <span>{e(d["title"])}</span></li>' for d in
        sorted(decisions, key=lambda r: r["id"])
    )

    return TEMPLATE.format(
        title=e(title if title is not None else (workspace_root().name or "Work Threads")),
        panels="".join(panels),
        decisions=dec_html,
        n_open=len(open_rows), n_ready=len(ready),
        n_blocked=len(blocked), n_dec=len(decisions),
    )


TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Public+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root {{
  --ground:#F5F6F8; --surface:#FFFFFF; --line:#DFE3E9; --ink:#14181F;
  --muted:#69717F; --live:#1F6F5C; --p0:#A93226; --decision:#6B4FA0;
  --blocked:#8A94A6; --shadow:0 1px 2px rgba(20,24,31,.05);
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;
  --body:"Public Sans",ui-sans-serif,system-ui,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}}
@media (prefers-color-scheme:dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#0D1014; --surface:#151A21; --line:#242C36; --ink:#E7EAEF;
    --muted:#8F98A6; --live:#4FB89C; --p0:#E0736A; --decision:#A98CDB;
    --blocked:#6C7688; --shadow:none;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0D1014; --surface:#151A21; --line:#242C36; --ink:#E7EAEF;
  --muted:#8F98A6; --live:#4FB89C; --p0:#E0736A; --decision:#A98CDB;
  --blocked:#6C7688; --shadow:none;
}}
* {{ box-sizing:border-box; }}
body {{ background:var(--ground); color:var(--ink); font-family:var(--body);
  line-height:1.5; margin:0; padding:2.5rem 1.5rem 4rem; }}
.wrap {{ max-width:1180px; margin:0 auto; }}
h1 {{ font-family:var(--display); font-size:clamp(1.8rem,3.4vw,2.5rem); font-weight:700;
  letter-spacing:-.02em; margin:0 0 .3rem; text-wrap:balance; }}
.sub {{ color:var(--muted); margin:0 0 2rem; max-width:62ch; }}
.bar {{ display:flex; flex-wrap:wrap; gap:2.25rem; padding:1rem 1.25rem; margin-bottom:2.25rem;
  background:var(--surface); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
.bar div {{ display:flex; flex-direction:column; gap:.15rem; }}
.bar b {{ font-family:var(--display); font-size:1.5rem; font-weight:700;
  font-variant-numeric:tabular-nums; line-height:1; }}
.bar span {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.09em; color:var(--muted); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:1.25rem; }}
.track {{ background:var(--surface); border:1px solid var(--line); border-radius:8px;
  padding:1.1rem 1.25rem 1.35rem; box-shadow:var(--shadow); }}
.track header {{ display:flex; align-items:baseline; justify-content:space-between;
  gap:1rem; padding-bottom:.75rem; border-bottom:1px solid var(--line); }}
h2 {{ font-family:var(--display); font-size:1.02rem; font-weight:700; margin:0; letter-spacing:-.01em; }}
.count {{ font-size:.74rem; color:var(--muted); margin:0; font-variant-numeric:tabular-nums; }}
.thread {{ list-style:none; margin:0; padding:.9rem 0 0 0; position:relative; }}
.thread::before {{ content:""; position:absolute; left:4px; top:1.35rem; bottom:.55rem;
  width:1px; background:var(--line); }}
.bead {{ position:relative; padding:0 0 .95rem 1.5rem; }}
.bead:last-child {{ padding-bottom:0; }}
.node {{ position:absolute; left:0; top:.42rem; width:9px; height:9px; border-radius:50%;
  background:var(--surface); border:2px solid var(--blocked); }}
.bead.p0 .node {{ border-color:var(--p0); background:var(--p0); }}
.bead.p1 .node {{ border-color:var(--live); background:var(--live); }}
.bead.p2 .node, .bead.p3 .node {{ border-color:var(--live); }}
.bead.decision .node {{ border-color:var(--decision); background:var(--decision); }}
.bead.blocked .node {{ border-style:dashed; }}
.ttl {{ margin:0 0 .2rem; font-size:.885rem; font-weight:500; text-wrap:pretty; }}
.bead.blocked .ttl {{ color:var(--muted); }}
.meta {{ margin:0; display:flex; flex-wrap:wrap; align-items:center; gap:.5rem; }}
code {{ font-family:var(--mono); font-size:.7rem; color:var(--muted); }}
.tag {{ font-size:.66rem; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); }}
.bead.p0 .tag {{ color:var(--p0); font-weight:600; }}
.ref {{ font-family:var(--mono); font-size:.7rem; color:var(--live); text-decoration:none;
  border-bottom:1px solid transparent; }}
.ref:hover, .ref:focus-visible {{ border-bottom-color:currentColor; }}
.wait {{ margin:.28rem 0 0; font-size:.73rem; color:var(--muted); }}
.wait span {{ color:var(--blocked); }}
.dec {{ margin-top:2.25rem; background:var(--surface); border:1px solid var(--line);
  border-left:3px solid var(--decision); border-radius:8px; padding:1.1rem 1.35rem 1.25rem; }}
.dec h2 {{ margin-bottom:.15rem; }}
.dec p.note {{ margin:0 0 .8rem; font-size:.8rem; color:var(--muted); }}
.dec ul {{ margin:0; padding:0; list-style:none; display:flex; flex-direction:column; gap:.5rem; }}
.dec li {{ display:flex; gap:.65rem; align-items:baseline; font-size:.885rem; }}
a:focus-visible, .ref:focus-visible {{ outline:2px solid var(--live); outline-offset:2px; }}
@media (prefers-reduced-motion:reduce) {{ * {{ transition:none !important; }} }}
</style>
<div class="wrap">
<h1>{title}</h1>
<p class="sub">Open work across this workspace. Priority reads as sequence, not importance:
<em>now</em>, <em>next</em>, <em>parallel</em>, <em>later</em>, then <em>backlog</em>.</p>
<div class="bar">
  <div><b>{n_open}</b><span>Open</span></div>
  <div><b>{n_ready}</b><span>Ready</span></div>
  <div><b>{n_blocked}</b><span>Blocked</span></div>
  <div><b>{n_dec}</b><span>Decisions</span></div>
</div>
<div class="grid">{panels}</div>
<section class="dec"><h2>Decisions waiting on you</h2>
<p class="note">Calls to make, not code to write. Nothing downstream moves until each is settled.</p>
<ul>{decisions}</ul></section>
</div>
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", help="beads JSONL export")
    parser.add_argument("out", help="output HTML path")
    parser.add_argument("repo", nargs="?", help="owner/repo for gh-NNNN links (default: no links)")
    parser.add_argument("--title", help="dashboard title (default: workspace directory name)")
    args = parser.parse_args()
    Path(args.out).write_text(build(load(args.src), args.repo, args.title), encoding="utf-8")
    print(f"wrote {args.out}")
