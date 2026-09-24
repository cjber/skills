#!/usr/bin/env python3
"""Flag the mechanical AI tells voice.md bans in store copy and posts (WFA-24).

Usage: check_copy.py FILE... ; exits 1 and prints file:line: phrase for each hit, and each image
stacked under another with no text between (WFA-25).
Image alt text and code spans are skipped: they quote the game, not our voice.
"""

import re
import sys
from pathlib import Path

BANNED = [
    r"—",
    r" – ",
    r"\bseamless(ly)?\b",
    r"\belevat(e|es|ing)\b",
    r"\benhance your\b",
    r"\beffortless(ly)?\b",
    r"\bgame[- ]changer\b",
    r"\bsupercharge",
    r"\bunleash",
    r"\bunlock(s|ing)? (the|your|a)\b",
    r"\bdive (in|into)\b",
    r"\bdelv(e|es|ing)\b",
    r"\blook no further\b",
    r"\bwhether you'?re\b",
    r"\bit'?s not just\b",
    r"\bto the next level\b",
    r"\bsay goodbye to\b",
    r"\btailored\b",
    r"\brobust\b",
    r"\bstreamlin(e|ed|es|ing)\b",
    r"\bempower",
    r"\blevel up your\b",
    r"\bin today'?s\b",
    r"\bpowerful\b",
    r"\bultimate\b",
    r"\bamazing\b",
    r"\bstunning\b",
    r"\bsleek\b",
    r"\bcutting[- ]edge\b",
    r"\brevolutionary\b",
    r"\bkey features\b",
    r"^(in short|overall|in summary),",
    r"!(\s|$)",
]
PATTERN = re.compile("|".join(f"(?:{p})" for p in BANNED), re.IGNORECASE)
QUOTED = re.compile(r"!\[[^\]]*\]\([^)]*\)|`[^`]*`|alt=\"[^\"]*\"")


def hits(path: Path) -> list[str]:
    found = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for match in PATTERN.finditer(QUOTED.sub("", line)):
            found.append(f"{path}:{number}: {match.group(0).strip() or match.group(0)!r}")
    return found


IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>", re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")
OPEN_P = re.compile(r"<p\b", re.IGNORECASE)
CLOSE_P = re.compile(r"</p>", re.IGNORECASE)


def stacked(path: Path) -> list[str]:
    """Two images one above the other with no words between (WFA-25). Images in one <p> sit in a row: fine."""
    found = []
    last_image = 0  # line of the last image since any words
    in_p = False
    row_has_image = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if OPEN_P.search(line):
            in_p, row_has_image = True, False
        if IMAGE.search(line):
            if last_image and not row_has_image:
                found.append(f"{path}:{number}: image stacked under line {last_image} with no text between")
            last_image = number
            row_has_image = in_p
        if TAG.sub("", IMAGE.sub("", line)).strip():
            last_image = 0
        if CLOSE_P.search(line):
            in_p, row_has_image = False, False
    return found


def main() -> int:
    found = [hit for name in sys.argv[1:] for hit in hits(Path(name)) + stacked(Path(name))]
    for hit in found:
        print(hit)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
