#!/usr/bin/env python3
"""Render screenshots into a temporary directory and compare them with the reviewed images."""

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "docs" / "screenshots"

with tempfile.TemporaryDirectory(prefix="atlas-shots-") as temporary:
    target = Path(temporary)
    environment = os.environ.copy()
    environment["ATLAS_SCREENSHOT_OUT"] = str(target)
    subprocess.run([sys.executable, str(ROOT / "tools" / "screenshots.py")], env=environment, check=True)
    expected = sorted(path.name for path in IMAGES.glob("*.png"))
    actual = sorted(path.name for path in target.glob("*.png"))
    if expected != actual or not expected:
        raise SystemExit("screenshot set differs; rerun tools/screenshots.py and review the output")
    for name in expected:
        if (
            hashlib.sha256((IMAGES / name).read_bytes()).digest()
            != hashlib.sha256((target / name).read_bytes()).digest()
        ):
            raise SystemExit(f"{name} differs from the current rendered scene")
    if (IMAGES / "scenes.sha256").read_bytes() != (target / "scenes.sha256").read_bytes():
        raise SystemExit("scenes.sha256 differs from the current rendered scene manifest")
    if (IMAGES / "scenes.json").read_bytes() != (target / "scenes.json").read_bytes():
        raise SystemExit("scenes.json differs from the current addon UI and data state")
print("screenshots: current and reproducible")
