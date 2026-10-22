#!/usr/bin/env python3
"""Regenerate the index from pinned inputs and fail if the committed output differs."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "Data" / "Instances.lua"
before = OUTPUT.read_bytes() if OUTPUT.exists() else b""
subprocess.run([sys.executable, str(ROOT / "tools" / "gen_instances.py")], check=True)
after = OUTPUT.read_bytes()
if before != after:
    OUTPUT.write_bytes(before)
    print("Data/Instances.lua is stale; run python3 tools/gen_instances.py", file=sys.stderr)
    raise SystemExit(1)
print("generated instance data: current")
