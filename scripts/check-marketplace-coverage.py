#!/usr/bin/env python3
"""Cross-check the packages on disk against .claude-plugin/marketplace.json.

`claude plugin validate --strict` only inspects manifest *shape*; it never looks
at the filesystem. Two mistakes therefore pass validation and only surface when
a user tries to install:

  1. A plugin or standalone skill exists in the repo but was never registered
     in marketplace.json, so nobody can install it.
  2. A relative `source` (or `skills`) path in marketplace.json points at a
     directory that does not exist.

This script closes both gaps. It has no dependencies beyond the standard
library so it runs identically on a dev machine and on a CI runner.

Usage:
    scripts/check-marketplace-coverage.py [--root DIR] [--plugins-dir NAME]
                                          [--skills-dir NAME] [--manifest PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# GitHub renders `::error::` lines as annotations on the pull request diff.
ANNOTATE = os.environ.get("GITHUB_ACTIONS") == "true"


def subdirs(directory: Path) -> list[Path]:
    """Package directories inside `directory`, ignoring dotfiles and files."""
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if p.is_dir() and not p.name.startswith("."))


def join(base: Path, ref: str) -> Path:
    """Resolve a manifest path reference against a base directory."""
    return (base / ref).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--plugins-dir", default="plugins", help="default: plugins")
    parser.add_argument("--skills-dir", default="skills", help="default: skills")
    parser.add_argument(
        "--manifest",
        default=".claude-plugin/marketplace.json",
        help="default: .claude-plugin/marketplace.json",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / args.manifest
    plugins_dir = root / args.plugins_dir
    skills_dir = root / args.skills_dir

    def rel(path: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)

    errors: list[tuple[str, str]] = []  # (file for annotation, message)

    def fail(message: str, file: Path | None = None) -> None:
        errors.append((rel(file) if file else rel(manifest_path), message))

    try:
        manifest = json.loads(manifest_path.read_text())
    except FileNotFoundError:
        print(f"error: {rel(manifest_path)} not found")
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: {rel(manifest_path)} is not valid JSON: {exc}")
        return 1

    entries = manifest.get("plugins") or []
    disk_plugins = subdirs(plugins_dir)
    disk_skills = subdirs(skills_dir)

    if not entries and not disk_plugins and not disk_skills:
        print("No plugins or skills registered or on disk yet — nothing to cross-check.")
        return 0

    # `metadata.pluginRoot` is prepended to relative sources, letting an entry
    # say "formatter" instead of "./plugins/formatter".
    plugin_root = str((manifest.get("metadata") or {}).get("pluginRoot") or "").strip()

    def resolve_source(source: object) -> tuple[Path | None, bool]:
        """Local directory a `source` refers to, and whether it exists.

        Returns (None, False) for object sources, which are fetched remotely and
        have nothing on disk to check.
        """
        if not isinstance(source, str):
            return None, False
        candidates = []
        if plugin_root:
            candidates.append(join(root, f"{plugin_root.rstrip('/')}/{source}"))
        candidates.append(join(root, source))
        for candidate in candidates:
            if candidate.is_dir():
                return candidate, True
        return candidates[0], False

    # --- Manifest entries -> disk -------------------------------------------
    registered: dict[Path, str] = {}  # plugin directory -> entry name
    seen_names: set[str] = set()

    covered_skills: set[Path] = set()
    all_skills_covered = False

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"plugins[{index}] is not an object")
            continue

        name = entry.get("name") or f"plugins[{index}]"
        if name in seen_names:
            fail(f'duplicate plugin name "{name}"')
        seen_names.add(name)

        source = entry.get("source")
        base, exists = resolve_source(source)

        if isinstance(source, str) and not exists:
            fail(
                f'plugin "{name}" has source "{source}" but no directory exists there '
                f"(expected {rel(base)}); relative sources must start with ./ and "
                "resolve against the repository root"
            )
            continue
        if base is None:
            continue  # remote source; nothing on disk to reconcile

        if base != root:
            registered[base] = name

        # Which top-level skills does this entry expose? An explicit `skills`
        # list normally ADDS to the default `<plugin root>/skills` scan; with a
        # marketplace-root source the list becomes the complete set instead.
        refs = entry.get("skills")
        scan: list[Path] = []
        if isinstance(refs, list) and refs:
            listed = [ref for ref in refs if isinstance(ref, str)]
            resolved = [join(base, ref) for ref in listed]
            for ref, path in zip(listed, resolved):
                if not path.is_dir():
                    fail(f'plugin "{name}" lists skills path "{ref}" but {rel(path)} does not exist')
            scan.extend(resolved)
            if not (base == root and any(path.is_dir() for path in resolved)):
                scan.append(base / "skills")
        else:
            scan.append(base / "skills")

        for path in scan:
            if path == skills_dir:
                all_skills_covered = True
            elif path.parent == skills_dir:
                covered_skills.add(path)

    # --- Disk -> manifest entries -------------------------------------------
    for plugin in disk_plugins:
        if plugin not in registered:
            fail(
                f'plugin "{plugin.name}" is not registered in {rel(manifest_path)}; '
                f'add an entry with "source": "./{rel(plugin)}"',
                plugin,
            )
            continue

        plugin_manifest = plugin / ".claude-plugin" / "plugin.json"
        if not plugin_manifest.is_file():
            fail(f'plugin "{plugin.name}" has no {rel(plugin_manifest)}', plugin)
            continue
        try:
            declared = json.loads(plugin_manifest.read_text()).get("name")
        except json.JSONDecodeError as exc:
            fail(f"{rel(plugin_manifest)} is not valid JSON: {exc}", plugin_manifest)
            continue
        if declared and declared != registered[plugin]:
            fail(
                f'name mismatch: {rel(plugin_manifest)} declares "{declared}" but '
                f'marketplace.json registers that directory as "{registered[plugin]}"',
                plugin_manifest,
            )

    if not all_skills_covered:
        for skill in disk_skills:
            if skill not in covered_skills:
                fail(
                    f'skill "{skill.name}" is not reachable from any marketplace entry; '
                    f'add "./{rel(skill)}" to the "skills" list of an entry, or expose the '
                    f'whole "./{args.skills_dir}/" directory',
                    skill,
                )

    # --- Report -------------------------------------------------------------
    if errors:
        print(f"✘ {len(errors)} coverage problem(s) in {rel(manifest_path)}:\n")
        for file, message in errors:
            print(f"  - {message}")
            if ANNOTATE:
                print(f"::error file={file}::{message}")
        return 1

    skill_summary = "all (directory-wide)" if all_skills_covered else str(len(covered_skills))
    print(
        f"✔ Coverage OK — {len(entries)} marketplace entr{'y' if len(entries) == 1 else 'ies'}, "
        f"{len(disk_plugins)} plugin(s) on disk, {len(disk_skills)} skill(s) on disk "
        f"(skills exposed: {skill_summary})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
