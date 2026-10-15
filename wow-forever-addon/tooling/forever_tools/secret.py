"""Reject reads of values the client may hand back as secrets, and tooltip hooks that touch a forbidden tooltip.

In combat and other restricted states the client returns some unit and tooltip values as secrets: a value addon
code may pass along but not compare, index, concatenate or call a method on (`guid:match` raises). And a tooltip
the client has marked forbidden raises on any method call. Each addon routes these reads through one helper
(`Readable`: the value, or nil when it is secret) and starts every tooltip hook by returning on `IsForbidden()`.

- `secret-unguarded`: a call to a source (`UnitGUID`, `UnitName`, ...) that is not the whole argument of a guard,
  `Readable(UnitGUID(unit))`; a unit the policy calls safe (`"player"`, written as a literal) is exempt.
- `secret-unguarded`: a tooltip hook's data field that may be secret (`data.guid`) read outside a guard.
- `secret-forbidden`: a `TooltipDataProcessor` call or an `OnTooltip*` script hook whose callback never calls
  `IsForbidden`.

An exception carries `-- secret-ok: <reason>` on its line or the line above; one that excuses nothing is refused.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .lua import LuaSyntaxError, Token, tokenize

__all__ = ["DEFAULT_POLICY", "Policy", "check", "run"]

SOURCES = frozenset(
    {
        "UnitGUID",
        "UnitName",
        "UnitNameUnmodified",
        "UnitFullName",
        "GetUnitName",
        "UnitCreatureID",
        "GetDisplayedUnit",
    }
)
HOOKS = frozenset({"AddTooltipPostCall", "AddTooltipPreCall", "AddLinePostCall", "AddLinePreCall"})
WAIVER = re.compile(r"secret-ok:\s*\S")
MARK = re.compile(r"secret-ok")


@dataclass(frozen=True)
class Policy:
    """`guards`: the helper names that make a value safe (the last name of `ns.Readable`). `sources`: calls whose
    results may be secret. `safe_units`: literal unit tokens never secret. `data_fields`: tooltip data fields that may
    be secret inside a hook."""

    guards: frozenset[str] = frozenset({"Readable"})
    sources: frozenset[str] = SOURCES
    safe_units: frozenset[str] = frozenset({"player"})
    data_fields: frozenset[str] = frozenset({"guid"})


DEFAULT_POLICY = Policy()


def closing(tokens: list[Token], index: int, opening: str = "(", close: str = ")") -> int:
    """The index of the bracket closing the one at `index`."""
    depth = 0
    for cursor in range(index, len(tokens)):
        depth += tokens[cursor].text == opening
        depth -= tokens[cursor].text == close
        if depth == 0:
            return cursor
    raise LuaSyntaxError(f"{tokens[index].line}: unclosed {opening}")


def block_end(tokens: list[Token], index: int) -> int:
    """The index of the `end` closing the `function` at `index`."""
    depth = 0
    for cursor in range(index, len(tokens)):
        token = tokens[cursor]
        if token.kind == "keyword":
            if token.text in {"function", "do", "if", "repeat"}:
                depth += 1
            elif token.text in {"end", "until"}:
                depth -= 1
                if depth == 0:
                    return cursor
    raise LuaSyntaxError(f"{tokens[index].line}: unclosed function")


def chain_start(tokens: list[Token], index: int) -> int:
    """The first token of the name chain ending at the name at `index` (`ns.Model.UnitGUID` from `UnitGUID`)."""
    cursor = index
    while cursor >= 2 and tokens[cursor - 1].text in {".", ":"} and tokens[cursor - 2].kind == "name":
        cursor -= 2
    return cursor


def guarded(tokens: list[Token], start: int, end: int, policy: Policy) -> bool:
    """Whether tokens[start:end + 1] is the whole argument of a guard call: `Readable(<it>)`."""
    return (
        start >= 2
        and tokens[start - 1].text == "("
        and tokens[start - 2].text in policy.guards
        and tokens[end + 1].text == ")"
    )


def callbacks(tokens: list[Token]) -> list[tuple[int, int | str]]:
    """Each tooltip hook as (line index of the hook name, the callback's `function` index or its name)."""
    found: list[tuple[int, int | str]] = []
    for index, token in enumerate(tokens):
        is_hook = token.text in HOOKS and tokens[index - 1].text in {".", ":"}
        is_script = (
            token.text == "HookScript"
            and tokens[index + 2].kind == "string"
            and tokens[index + 2].text[1:-1].startswith("OnTooltip")
        )
        if not (is_hook or is_script) or tokens[index + 1].text != "(":
            continue
        end = closing(tokens, index + 1)
        depth, cursor = 0, index + 2
        while cursor < end:  # the callback is the argument after the first top-level comma
            depth += tokens[cursor].text in "({["
            depth -= tokens[cursor].text in ")}]"
            if depth == 0 and tokens[cursor].text == ",":
                break
            cursor += 1
        callback = tokens[cursor + 1] if cursor < end else None
        if callback is None:
            continue
        if callback.text == "function":
            found.append((index, cursor + 1))
        elif callback.kind == "name":
            last = cursor + 1
            while tokens[last + 1].text == "." and tokens[last + 2].kind == "name":
                last += 2
            found.append((index, tokens[last].text))
    return found


def definition(tokens: list[Token], name: str) -> int | None:
    """The `function` index of `local function name`, `function a.name` or `name = function`, if in this file."""
    for index, token in enumerate(tokens):
        if token.text != "function":
            continue
        cursor = index + 1
        while tokens[cursor].kind == "name" and tokens[cursor + 1].text in {".", ":"}:
            cursor += 2
        if tokens[cursor].text == name and tokens[cursor + 1].text == "(":
            return index
        if index >= 2 and tokens[index - 1].text == "=" and tokens[index - 2].text == name:
            return index
    return None


def parameters(tokens: list[Token], function: int) -> list[str]:
    cursor = function + 1
    while tokens[cursor].text != "(":
        cursor += 1
    names = []
    while tokens[cursor].text != ")":
        if tokens[cursor].kind == "name":
            names.append(tokens[cursor].text)
        cursor += 1
    return names


def _check(source: str, policy: Policy) -> list[tuple[int, str]]:
    tokens, _ = tokenize(source)
    lines = source.splitlines()
    raw: list[tuple[int, str]] = []
    for index, token in enumerate(tokens):
        if token.kind != "name" or token.text not in policy.sources or tokens[index + 1].text != "(":
            continue
        start = chain_start(tokens, index)
        if start >= 1 and tokens[start - 1].text == "function":
            continue
        end = closing(tokens, index + 1)
        argument = tokens[index + 2 : end]
        if len(argument) == 1 and argument[0].kind == "string" and argument[0].text[1:-1] in policy.safe_units:
            continue
        if not guarded(tokens, start, end, policy):
            raw.append((token.line, f"secret-unguarded: {token.text}() may return a secret; read it through a guard"))
    for hook, callback in callbacks(tokens):
        function = callback if isinstance(callback, int) else definition(tokens, callback)
        if function is None:
            raw.append((tokens[hook].line, f"secret-forbidden: {callback} is not defined here to check IsForbidden"))
            continue
        end = block_end(tokens, function)
        body = tokens[function:end]
        if not any(t.text == "IsForbidden" for t in body):
            raw.append((tokens[hook].line, "secret-forbidden: the hook never returns on tooltip:IsForbidden()"))
        names = parameters(tokens, function)
        data = names[1] if len(names) > 1 else None
        for offset, token in enumerate(body):
            at = function + offset
            if (
                data
                and token.text == data
                and tokens[at + 1].text == "."
                and tokens[at + 2].text in policy.data_fields
                and tokens[at - 1].text not in {".", ":"}
                and tokens[at + 3].text != "="
                and not guarded(tokens, at, at + 2, policy)
            ):
                field = f"{data}.{tokens[at + 2].text}"
                raw.append((token.line, f"secret-unguarded: {field} may be a secret; read it through a guard"))
    findings, excused = [], set()
    for number, message in sorted(set(raw)):
        waiver = next((at for at in (number, number - 1) if at >= 1 and WAIVER.search(lines[at - 1])), None)
        if waiver is None:
            findings.append((number, message))
        else:
            excused.add(waiver)
    for number, line in enumerate(lines, 1):
        if MARK.search(line) and number not in excused:
            reason = "names no reason" if not WAIVER.search(line) else "excuses no secret read"
            findings.append((number, f"secret-unused: this secret-ok {reason}"))
    return sorted(findings)


def check(source: str, policy: Policy = DEFAULT_POLICY) -> list[tuple[int, str]]:
    """`(line, message)` for each unguarded secret read in `source`; malformed Lua raises LuaSyntaxError."""
    try:
        return _check(source, policy)
    except IndexError as error:
        raise LuaSyntaxError("unexpected end of file") from error


def run(paths: list[Path], policy: Policy = DEFAULT_POLICY) -> int:
    failed, checked = False, 0
    for path in paths:
        checked += 1
        try:
            findings = check(path.read_text(encoding="utf-8"), policy)
        except (LuaSyntaxError, OSError, UnicodeDecodeError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
            continue
        for line, message in findings:
            print(f"{path}:{line}: {message}")
            failed = True
    if not failed:
        print(f"Secret lint: {checked} files checked")
    return int(failed)
