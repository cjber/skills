"""Check the folders the BigWigs packager built before anything uploads them.

The release workflow hands the packager's output straight to GitHub, CurseForge and Wago, and `.pkgmeta`'s ignore
list is never compared with the TOC. Run the packager without uploading (`release.sh -d -z`, or the action with
`args: -d -z`), then this reads its release directory and fails on:

- an addon folder that is missing, or has no TOC of its own name;
- a file a TOC or its XML loads (`Script`, `Include`), or an `Interface\\AddOns\\<packaged folder>\\...` path a TOC
  tag, XML attribute or whole Lua string names, that is not in the package;
- a development folder that shipped (`tests`, `tools`, `types`, `.agents` and the like), or a required file that
  did not (`LICENSE`);
- a spec that fails when run against the packaged files instead of the checkout: the package is copied to a scratch
  folder, the addon's test support (`tests/`) is laid over it, and each spec runs there under LuaJIT.

    python3 tools/check_package.py [--release-dir .release]
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .lua import LuaSyntaxError, tokenize

__all__ = ["Policy", "check", "main", "run_specs"]

FORBIDDEN = (".agents", ".github", ".sift", "AGENTS.md", "tests", "tools", "types")
# What the client accepts for a texture, font or sound path given without its extension.
EXTENSIONS = ("", ".tga", ".blp", ".png", ".jpg", ".ttf", ".otf", ".ogg", ".mp3")
LOAD_TAGS = {"Include", "Script"}


@dataclass(frozen=True)
class Policy:
    """`addons`: every folder the package holds, the main addon first (`package-as`, then each `move-folders`
    target). `forbidden`: names that must not appear at any addon folder's top level. `required`: files the main
    addon folder must ship. `specs`: repository-relative specs to run on the packaged files, with `support` (paths in
    the checkout, never shipped) laid over a copy of the package first."""

    addons: tuple[str, ...]
    forbidden: tuple[str, ...] = FORBIDDEN
    required: tuple[str, ...] = ("LICENSE",)
    specs: tuple[str, ...] = ()
    support: tuple[str, ...] = ("tests",)


def addon_path(text: str, release: Path, addons: tuple[str, ...]) -> Path | None:
    """The packaged file an `Interface\\AddOns\\<folder>\\...` path names, or None when it names another addon."""
    parts = PurePosixPath(text.strip().replace("\\", "/")).parts
    if len(parts) < 4 or parts[0].lower() != "interface" or parts[1].lower() != "addons":
        return None
    folder = next((addon for addon in addons if addon.lower() == parts[2].lower()), None)
    return None if folder is None else release.joinpath(folder, *parts[3:])


def present(path: Path) -> bool:
    """Whether the client would find `path`, extension optional and case ignored, as Windows does."""
    folder = path.parent
    if not folder.is_dir():
        # Resolve each missing component case-insensitively.
        current = Path(path.anchor) if path.is_absolute() else Path()
        for part in folder.parts[len(current.parts) :]:
            match = next((child for child in current.iterdir() if child.name.lower() == part.lower()), None)
            if match is None or not match.is_dir():
                return False
            current = match
        folder = current
    names = {child.name.lower() for child in folder.iterdir()}
    return any((path.name + extension).lower() in names for extension in EXTENSIONS)


def lua_strings(source: str) -> list[tuple[int, str]]:
    """Each whole string literal in a Lua file with its line, escapes for backslashes and quotes undone."""
    tokens, _ = tokenize(source)
    found = []
    for token in tokens:
        if token.kind == "string" and token.text[:1] in "\"'":
            body = token.text[1:-1]
            found.append((token.line, body.replace("\\\\", "\\").replace('\\"', '"').replace("\\'", "'")))
    return found


def check(release: Path, policy: Policy) -> list[str]:
    """Every problem with the packaged folders under `release`, each as one line."""
    problems: list[str] = []
    for addon in policy.addons:
        folder = release / addon
        if not folder.is_dir():
            problems.append(f"{addon}: not in {release}; check package-as and move-folders in .pkgmeta")
            continue
        for child in sorted(folder.iterdir()):
            if child.name in policy.forbidden:
                problems.append(f"{addon}/{child.name}: shipped; add it to .pkgmeta's ignore list")
        toc = folder / f"{addon}.toc"
        if not toc.is_file():
            problems.append(f"{addon}/{addon}.toc: missing")
            continue
        problems += check_loaded(release, folder, toc, policy.addons)
    if policy.addons and (release / policy.addons[0]).is_dir():
        for name in policy.required:
            if not (release / policy.addons[0] / name).exists():
                problems.append(f"{policy.addons[0]}/{name}: missing; it must ship")
    return problems


def check_loaded(release: Path, folder: Path, toc: Path, addons: tuple[str, ...]) -> list[str]:
    """The TOC's files, their XML includes, and the addon paths any of them name, that are not in the package."""
    problems: list[str] = []
    seen: set[Path] = set()

    def where(path: Path) -> str:
        return path.relative_to(release).as_posix()

    def named(source: Path, line: int, text: str) -> None:
        target = addon_path(text, release, addons)
        if target is not None and not present(target):
            at = f"{where(source)}:{line}" if line else where(source)
            problems.append(f"{at}: names {text.strip()}, which is not in the package")

    def visit(path: Path, by: str) -> None:
        if path in seen:
            return
        seen.add(path)
        if not path.is_file():
            problems.append(f"{where(path)}: missing (loaded by {by}); check .pkgmeta's ignore list")
            return
        if path.suffix.lower() == ".xml":
            try:
                elements = list(ET.parse(path).iter())
            except ET.ParseError as error:
                problems.append(f"{where(path)}: {error}")
                return
            for element in elements:
                if element.tag.rsplit("}", 1)[-1] in LOAD_TAGS and "file" in element.attrib:
                    visit(path.parent / element.attrib["file"].replace("\\", "/"), where(path))
                for value in element.attrib.values():
                    named(path, 0, value)
        elif path.suffix.lower() == ".lua":
            try:
                strings = lua_strings(path.read_text(encoding="utf-8"))
            except (LuaSyntaxError, UnicodeDecodeError) as error:
                problems.append(f"{where(path)}: {error}")
                return
            for line, text in strings:
                named(path, line, text)

    for number, line in enumerate(toc.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if line.startswith("##") and ":" in line:
            named(toc, number, line.split(":", 1)[1])
        elif line and not line.startswith("#"):
            visit(folder / line.replace("\\", "/"), where(toc))
    return problems


def run_specs(root: Path, release: Path, policy: Policy) -> list[str]:
    """Run each spec from a scratch copy of the package with the test support laid over it; failures as lines."""
    if not policy.specs:
        return []
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch) / policy.addons[0]
        shutil.copytree(release / policy.addons[0], work)
        for addon in policy.addons[1:]:
            shutil.copytree(release / addon, Path(scratch) / addon)
        for name in policy.support:
            source, target = root / name, work / name
            if target.exists():
                return [f"{name}: shipped in the package, so the specs cannot tell it from the checkout's"]
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        for spec in policy.specs:
            result = subprocess.run(["luajit", spec], cwd=work, capture_output=True, text=True)
            if result.returncode:
                tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-20:])
                problems.append(f"{spec}: fails on the packaged files (exit {result.returncode}):\n{tail}")
            else:
                print(f"{spec}: passes on the packaged files")
    return problems


def main(root: Path, policy: Policy, argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release-dir", type=Path, default=root / ".release", help="the packager's release folder")
    args = parser.parse_args(argv)
    problems = check(args.release_dir, policy)
    if not problems:
        problems = run_specs(root, args.release_dir, policy)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"Package: {', '.join(policy.addons)} ship every loaded file and nothing from development")
    return 0
