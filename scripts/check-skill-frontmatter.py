#!/usr/bin/env python3
"""Mechanically enforce the SKILL.md rules that fail silently at runtime.

`claude plugin validate --strict` checks manifest *shape*. It never opens a
SKILL.md, so the failures that actually bite ship clean through validation:

  1. `description` over 1024 characters. The hard per-skill cap. It surfaces as
     an alert on the surfaces that load the skill -- long after the commit.
  2. Frontmatter that doesn't parse as YAML. A long unquoted one-line
     `description:` breaks the moment it contains ": " (colon-space) or " #".
     The skill then loads with *empty metadata* -- every frontmatter field
     silently dropped -- so it never fires and never errors.
  3. A missing or mismatched `name`. Omit it and Claude Code falls back to the
     install directory name, which for a marketplace install is a version
     string that changes on every update.
  4. A SKILL.md that has grown past the point where the model reads it well.

All four are mechanical. None should be caught by a human.

Stdlib only, so the pre-commit hook and the CI runner execute the same code.
PyYAML is used when importable, because agreeing with a real parser is the
whole point of the check; otherwise a narrow built-in parser covers the subset
of YAML that frontmatter actually uses and refuses anything it can't model.

Usage:
    scripts/check-skill-frontmatter.py [--root DIR] [--skills-dir NAME]
                                       [--plugins-dir NAME] [--strict]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Hard limits. These are the loader's, not ours -- don't relax them.
MAX_DESCRIPTION = 1024
MAX_NAME = 64
MAX_LINES = 500

# Soft thresholds, reported as warnings so a near-miss gets fixed before an
# ordinary edit tips it over the hard limit.
WARN_DESCRIPTION = 950
WARN_LINES = 450

# Every description loaded in a session shares one prompt budget. Over it,
# Claude Code truncates descriptions, drops them for less-used skills, or falls
# back to names-only -- so one bloated description costs every other skill's
# discoverability.
BUDGET = 12000

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# The loader IGNORES unrecognized keys rather than rejecting them, so a typo'd
# key fails silently and forever. Warn against the known set.
KNOWN_KEYS = {
    "name",
    "description",
    "allowed-tools",
    "disallowed-tools",
    "shell",
    "argument-hint",
    "when_to_use",
    "disable-model-invocation",
    "user-invocable",
    "hooks",
    "license",
    "metadata",
    "version",
}

# GitHub and Forgejo both render `::error file=...::` as an annotation on the diff.
ANNOTATE = os.environ.get("GITHUB_ACTIONS") == "true"

try:  # pragma: no cover - import availability is environmental
    import yaml  # type: ignore

    HAVE_YAML = True
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore
    HAVE_YAML = False


class FrontmatterError(Exception):
    """The frontmatter block does not parse, exactly as the loader would fail."""


# --------------------------------------------------------------------------
# Frontmatter extraction
# --------------------------------------------------------------------------


def split_frontmatter(text: str) -> str:
    """Return the raw YAML between the opening and closing `---` fences.

    Raises FrontmatterError when the block is absent or unterminated, which is
    how the loader treats it too.
    """
    if text.startswith("﻿"):
        raise FrontmatterError(
            "file begins with a UTF-8 BOM, which prevents the opening `---` from "
            "being recognized; save the file as UTF-8 without a BOM"
        )
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        raise FrontmatterError(
            "no YAML frontmatter block; the file must begin with a line containing "
            "exactly `---`"
        )
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return "\n".join(lines[1:index])
    raise FrontmatterError("frontmatter block is never closed by a second `---` line")


# --------------------------------------------------------------------------
# Built-in parser -- the fallback when PyYAML isn't installed
# --------------------------------------------------------------------------

KEY_RE = re.compile(r"^(?P<key>[A-Za-z0-9_][A-Za-z0-9_.-]*)\s*:(?:\s+(?P<value>.*))?$")
BLOCK_RE = re.compile(r"^(?P<style>[|>])(?P<chomp>[-+]?)(?P<indent>[0-9]*)\s*$")


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_plain(value: str, key: str) -> str:
    """Validate and return a plain (unquoted) scalar.

    Plain scalars are where frontmatter goes wrong. A ": " inside one is a hard
    YAML error, and a " #" silently truncates the value at the comment. Both
    lose the field, so both are refused here.
    """
    if ": " in value:
        raise FrontmatterError(
            f"`{key}:` is an unquoted plain scalar containing a colon-space (`: `), "
            "which YAML reads as a nested mapping -- the whole frontmatter block "
            "fails to parse and every field is silently dropped. Rewrite it as a "
            "folded block scalar (`>-`)"
        )
    if " #" in value:
        raise FrontmatterError(
            f"`{key}:` is an unquoted plain scalar containing ` #`, which YAML reads "
            "as a trailing comment and truncates the value there. Rewrite it as a "
            "folded block scalar (`>-`)"
        )
    if value.endswith(":"):
        raise FrontmatterError(
            f"`{key}:` is an unquoted plain scalar ending in a colon, which YAML "
            "reads as a nested mapping"
        )
    return value.strip()


def _parse_quoted(value: str, key: str) -> str:
    quote = value[0]
    body = value[1:]
    closing = body.rfind(quote)
    if closing == -1:
        raise FrontmatterError(f"`{key}:` has an unterminated {quote} quoted string")
    inner = body[:closing]
    if quote == '"':
        return inner.replace('\\"', '"').replace("\\\\", "\\").replace("\\n", "\n")
    return inner.replace("''", "'")


def _fold_block(lines: list[str], style: str, chomp: str) -> str:
    """Apply YAML block-scalar semantics to the already-dedented body lines."""
    if style == "|":
        text = "\n".join(lines)
    else:
        chunks: list[str] = []
        for line in lines:
            if not line.strip():
                chunks.append("\n")
            elif chunks and not chunks[-1].endswith("\n") and not line.startswith(" "):
                chunks.append(" " + line)
            else:
                chunks.append(line)
        text = "".join(chunks)
    text = text.rstrip("\n")
    if chomp == "+":
        return text + "\n"
    if chomp == "":
        return text + "\n" if lines else text
    return text


def parse_frontmatter_builtin(block: str) -> dict:
    """Parse the subset of YAML that SKILL.md frontmatter legitimately uses.

    Anything outside that subset raises rather than guessing, so the fallback
    never reports success on something PyYAML would reject.
    """
    data: dict[str, object] = {}
    lines = block.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if _indent_of(line) != 0:
            raise FrontmatterError(
                f"unexpected indentation on line {index + 2}: {line.strip()!r}"
            )
        match = KEY_RE.match(line)
        if not match:
            raise FrontmatterError(
                f"line {index + 2} is not a `key: value` pair: {line.strip()!r}"
            )
        key = match.group("key")
        if key in data:
            raise FrontmatterError(f"duplicate key `{key}` in frontmatter")
        raw = (match.group("value") or "").strip()
        index += 1

        block_match = BLOCK_RE.match(raw) if raw else None
        if block_match:
            body: list[str] = []
            while index < len(lines):
                nxt = lines[index]
                if nxt.strip() and _indent_of(nxt) == 0:
                    break
                body.append(nxt)
                index += 1
            while body and not body[-1].strip():
                body.pop()
            widths = [_indent_of(b) for b in body if b.strip()]
            base = min(widths) if widths else 0
            data[key] = _fold_block(
                [b[base:] if b.strip() else "" for b in body],
                block_match.group("style"),
                block_match.group("chomp"),
            )
            continue

        if not raw:
            items: list[str] = []
            while index < len(lines):
                nxt = lines[index]
                if not nxt.strip():
                    index += 1
                    continue
                if _indent_of(nxt) == 0:
                    break
                stripped = nxt.strip()
                if not stripped.startswith("- "):
                    raise FrontmatterError(
                        f"line {index + 2} is indented under `{key}:` but is not a "
                        f"list item: {stripped!r}"
                    )
                entry = stripped[2:].strip()
                if entry[:1] in {"'", '"'}:
                    items.append(_parse_quoted(entry, key))
                else:
                    items.append(_parse_plain(entry, key))
                index += 1
            data[key] = items if items else None
            continue

        if raw[0] == "[":
            closing = raw.rfind("]")
            if closing == -1:
                raise FrontmatterError(f"`{key}:` has an unterminated flow sequence")
            inner = raw[1:closing].strip()
            entries = [e.strip() for e in inner.split(",") if e.strip()] if inner else []
            data[key] = [
                _parse_quoted(e, key) if e[:1] in {"'", '"'} else _parse_plain(e, key)
                for e in entries
            ]
            continue

        if raw[0] in {"'", '"'}:
            data[key] = _parse_quoted(raw, key)
            continue

        if raw in {"true", "True", "false", "False"}:
            data[key] = raw.lower() == "true"
            continue
        if raw in {"null", "~"}:
            data[key] = None
            continue

        data[key] = _parse_plain(raw, key)

    return data


def parse_frontmatter(block: str) -> dict:
    """Parse with PyYAML when available, otherwise the built-in parser."""
    if HAVE_YAML:
        try:
            parsed = yaml.safe_load(block)
        except Exception as exc:  # yaml.YAMLError and friends
            detail = str(exc).replace("\n", " ")
            raise FrontmatterError(
                f"frontmatter is not valid YAML, so the skill loads with empty "
                f"metadata and never fires: {detail}"
            ) from exc
    else:
        parsed = parse_frontmatter_builtin(block)

    if parsed is None:
        raise FrontmatterError("frontmatter block is empty")
    if not isinstance(parsed, dict):
        raise FrontmatterError(
            f"frontmatter must be a mapping of fields, not a "
            f"{type(parsed).__name__}"
        )
    return parsed


def description_is_plain_scalar(block: str) -> bool:
    """True when `description:` is written as an unquoted one-line scalar.

    Style is a source-level property that a parsed value can't tell you, so it
    is read off the raw block regardless of which parser ran.
    """
    for line in block.split("\n"):
        if not line.startswith("description:"):
            continue
        value = line[len("description:") :].strip()
        if not value:
            return False
        return value[0] not in {">", "|", "'", '"'}
    return False


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    def error(self, path: Path, message: str) -> None:
        self.errors.append((self.rel(path), message))

    def warn(self, path: Path, message: str) -> None:
        self.warnings.append((self.rel(path), message))


def check_skill(path: Path, report: Report) -> int:
    """Validate one SKILL.md. Returns its description length for the budget sum."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.error(path, f"cannot be read: {exc}")
        return 0

    # Line count is independent of the frontmatter, so check it even if the
    # YAML is broken -- a long file and a broken header are separate problems.
    line_count = len(text.splitlines())
    if line_count > MAX_LINES:
        report.error(
            path,
            f"is {line_count} lines, over the {MAX_LINES}-line limit. Split the "
            "longest self-contained sections into their own files under "
            "`references/` (or `assets/`) and leave a one-line pointer plus a "
            "short summary in SKILL.md. Progressive disclosure keeps the skill "
            "body cheap to load and the detail available on demand",
        )
    elif line_count > WARN_LINES:
        report.warn(
            path,
            f"is {line_count} lines, approaching the {MAX_LINES}-line limit -- "
            "start planning which sections move into `references/`",
        )

    try:
        block = split_frontmatter(text)
        data = parse_frontmatter(block)
    except FrontmatterError as exc:
        report.error(path, str(exc))
        return 0

    for key in data:
        if key not in KNOWN_KEYS:
            report.warn(
                path,
                f"unrecognized frontmatter key `{key}` -- the loader ignores unknown "
                "keys rather than rejecting them, so a typo here fails silently "
                "forever. Check the spelling against the recognized field list",
            )

    # --- name -------------------------------------------------------------
    name = data.get("name")
    directory = path.parent.name
    if name is None:
        report.error(
            path,
            "has no `name:` field. Without one Claude Code falls back to the install "
            "directory name, which for a marketplace install is a version string that "
            f'changes on every update. Add `name: {directory}`',
        )
    elif not isinstance(name, str):
        report.error(path, f"`name` must be a string, not a {type(name).__name__}")
    else:
        if len(name) > MAX_NAME:
            report.error(
                path, f"`name` is {len(name)} characters, over the {MAX_NAME} limit"
            )
        if not NAME_RE.match(name):
            report.error(
                path,
                f"`name: {name}` must be lowercase letters, digits and single hyphens "
                "only (no capitals, underscores, spaces, or leading/trailing/doubled "
                "hyphens)",
            )
        elif name != directory:
            report.error(
                path,
                f"`name: {name}` does not match its directory `{directory}/`. The two "
                "must be identical -- rename the directory or the field so they agree",
            )

    # --- description ------------------------------------------------------
    description = data.get("description")
    length = 0
    if description is None:
        report.error(
            path,
            "has no `description:` field. The description is the only thing that "
            "routes work to this skill -- without it the skill never fires",
        )
    elif not isinstance(description, str):
        report.error(
            path, f"`description` must be a string, not a {type(description).__name__}"
        )
    else:
        length = len(description)
        if length > MAX_DESCRIPTION:
            report.error(
                path,
                f"`description` is {length} characters, over the hard "
                f"{MAX_DESCRIPTION}-character limit by {length - MAX_DESCRIPTION}. "
                "Cut near-duplicate trigger phrases first (a plural already covers "
                "its singular), then prose that restates the skill body. Keep the "
                "distinct trigger vocabulary",
            )
        elif length > WARN_DESCRIPTION:
            report.warn(
                path,
                f"`description` is {length} characters, close to the "
                f"{MAX_DESCRIPTION} limit -- an ordinary edit will tip it over",
            )
        if description_is_plain_scalar(block):
            report.warn(
                path,
                "`description` is written as an unquoted plain scalar. It breaks the "
                "moment the text gains a `: ` or ` #`, and the whole skill then loads "
                "with empty metadata. Rewrite it as a folded block scalar (`>-`)",
            )

    # --- tool lists and shell ---------------------------------------------
    for key in ("allowed-tools", "disallowed-tools"):
        value = data.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            continue
        if isinstance(value, list):
            bad = [item for item in value if not isinstance(item, str)]
            if bad:
                report.error(path, f"`{key}` has non-string entries: {bad!r}")
            continue
        report.error(
            path, f"`{key}` must be a string or a list of strings, not a {type(value).__name__}"
        )

    shell = data.get("shell")
    if shell is not None and shell not in {"bash", "powershell"}:
        report.error(
            path, f"`shell: {shell!r}` must be exactly `bash` or `powershell`"
        )

    return length


def find_skills(root: Path, names: list[str]) -> list[Path]:
    found: list[Path] = []
    for name in names:
        base = root / name
        if base.is_dir():
            found.extend(base.rglob("SKILL.md"))
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--skills-dir", default="skills", help="default: skills")
    parser.add_argument("--plugins-dir", default="plugins", help="default: plugins")
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=BUDGET,
        help=f"combined description budget to warn at (default: {BUDGET})",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = Report(root)
    skills = find_skills(root, [args.skills_dir, args.plugins_dir])

    if not skills:
        print("No SKILL.md files found -- nothing to check.")
        return 0

    total = sum(check_skill(path, report) for path in skills)

    if total > args.budget:
        report.warnings.append(
            (
                "",
                f"combined description length is {total} characters across "
                f"{len(skills)} skills, over the {args.budget}-character budget. Every "
                "loaded description shares one prompt budget; over it Claude Code "
                "truncates descriptions or drops them for less-used skills, so this "
                "costs every skill's discoverability",
            )
        )

    for file, message in report.warnings:
        location = f"{file}: " if file else ""
        print(f"warning: {location}{message}")
        if ANNOTATE and file:
            print(f"::warning file={file}::{message}")

    for file, message in report.errors:
        print(f"error: {file}: {message}", file=sys.stderr)
        if ANNOTATE:
            print(f"::error file={file}::{message}")

    failed = bool(report.errors) or (args.strict and bool(report.warnings))
    if failed:
        counts = f"{len(report.errors)} error(s)"
        if args.strict and report.warnings:
            counts += f", {len(report.warnings)} warning(s) (--strict)"
        print(f"\n✘ {counts} across {len(skills)} skill(s)", file=sys.stderr)
        return 1

    parser_note = "PyYAML" if HAVE_YAML else "built-in parser"
    summary = (
        f"✔ Skill frontmatter OK — {len(skills)} skill(s), "
        f"{total} description characters ({parser_note})"
    )
    if report.warnings:
        summary += f", {len(report.warnings)} warning(s)"
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
