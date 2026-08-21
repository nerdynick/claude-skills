#!/usr/bin/env python3
"""Stage the archives built by `make package-all` for a GitHub release.

Versioning has two levels and an asset name carries both:

  * The **marketplace version** — root `version` in marketplace.json — is the
    release identity, published as tag `v<version>`.
  * Each package's **own version** — `version` in a plugin's plugin.json, or the
    `version` on its marketplace entry — identifies the package within it.

So `nerdynik-demo-0.2.0-mp0.4.0.zip` is v0.2.0 of that plugin as shipped in
marketplace release v0.4.0. A package declaring no version of its own is staged
as `<package>-mp<marketplace version>.zip`.

Everything is written under the (gitignored) dist tree; nothing here builds or
packages, so the Makefile stays the single source of truth for archives.

Usage:
    scripts/prepare-release.py [--root DIR] [--dist DIR] [--plugins-dir NAME]
                               [--skills-dir NAME] [--staging DIR] [--notes FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def emit(**outputs: str) -> None:
    """Report step outputs to GitHub Actions, and to stdout either way."""
    for key, value in outputs.items():
        print(f"{key}={value}")
    target = os.environ.get("GITHUB_OUTPUT")
    if target:
        with open(target, "a", encoding="utf-8") as handle:
            for key, value in outputs.items():
                handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--dist", default="dist", help="default: dist")
    parser.add_argument("--plugins-dir", default="plugins", help="default: plugins")
    parser.add_argument("--skills-dir", default="skills", help="default: skills")
    parser.add_argument("--staging", default=None, help="default: <dist>/release")
    parser.add_argument("--notes", default=None, help="default: <dist>/release-notes.md")
    parser.add_argument(
        "--manifest",
        default=".claude-plugin/marketplace.json",
        help="default: .claude-plugin/marketplace.json",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    dist = root / args.dist
    manifest_path = root / args.manifest
    skills_dir = (root / args.skills_dir).resolve()
    staging = Path(args.staging).resolve() if args.staging else dist / "release"
    notes_path = Path(args.notes).resolve() if args.notes else dist / "release-notes.md"

    try:
        manifest = json.loads(manifest_path.read_text())
    except FileNotFoundError:
        print(f"error: {args.manifest} not found")
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: {args.manifest} is not valid JSON: {exc}")
        return 1

    legacy = manifest.get("metadata") or {}
    marketplace_version = str(manifest.get("version") or legacy.get("version") or "").strip()
    if not marketplace_version:
        print(
            f'error: {args.manifest} declares no "version"; the release tag comes from it.\n'
            '       Add a root "version" (e.g. "version": "0.1.0") and bump it to publish.'
        )
        return 1

    marketplace_name = str(manifest.get("name") or "").strip()
    entries = [entry for entry in (manifest.get("plugins") or []) if isinstance(entry, dict)]

    def entry_version(entry: dict) -> str | None:
        return str(entry.get("version") or "").strip() or None

    # Versions declared on marketplace entries, keyed by entry name.
    by_entry_name = {
        str(entry["name"]): entry_version(entry) for entry in entries if entry.get("name")
    }

    # Which entry's version applies to each standalone skill. Only an entry whose
    # source is the marketplace root can expose the top-level skills directory.
    by_skill: dict[str, str | None] = {}
    blanket: str | None = None
    for entry in entries:
        source = entry.get("source")
        if not isinstance(source, str):
            continue  # remote source; nothing of ours inside it
        base = (root / source).resolve()
        refs = entry.get("skills")
        if isinstance(refs, list):
            for ref in refs:
                if not isinstance(ref, str):
                    continue
                path = (base / ref).resolve()
                if path == skills_dir:
                    blanket = blanket or entry_version(entry)
                elif path.parent == skills_dir:
                    by_skill.setdefault(path.name, entry_version(entry))
        elif base == root:
            blanket = blanket or entry_version(entry)  # default ./skills scan

    def plugin_own_version(name: str) -> str | None:
        """plugin.json wins over the marketplace entry, matching Claude Code."""
        plugin_manifest = root / args.plugins_dir / name / ".claude-plugin" / "plugin.json"
        if plugin_manifest.is_file():
            try:
                declared = json.loads(plugin_manifest.read_text()).get("version")
            except json.JSONDecodeError:
                declared = None
            if declared:
                return str(declared).strip()
        return by_entry_name.get(name)

    def skill_own_version(name: str) -> str | None:
        return by_skill.get(name) or blanket or by_entry_name.get(name)

    # --- Stage assets -------------------------------------------------------
    found = [
        ("plugin", archive, plugin_own_version(archive.stem))
        for archive in sorted((dist / args.plugins_dir).glob("*.zip"))
    ] + [
        ("skill", archive, skill_own_version(archive.stem))
        for archive in sorted((dist / args.skills_dir).glob("*.zip"))
    ]

    if not found:
        print(f"No archives under {args.dist}/ — run `make package-all` first. Nothing to release.")
        emit(version=marketplace_version, assets="0")
        return 0

    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    rows = []
    for kind, archive, own in found:
        stem = f"{archive.stem}-{own}" if own else archive.stem
        asset = f"{stem}-mp{marketplace_version}.zip"
        shutil.copy2(archive, staging / asset)
        rows.append((archive.stem, kind, own or "—", asset))
        print(f"staged {kind:7} {archive.stem:32} -> {asset}")

    # --- Release notes ------------------------------------------------------
    lines = [
        f"Marketplace release **v{marketplace_version}**.",
        "",
        "| Package | Type | Version | Asset |",
        "| --- | --- | --- | --- |",
    ]
    for name, kind, own, asset in rows:
        lines.append(f"| `{name}` | {kind} | {own} | `{asset}` |")
    lines += [
        "",
        "Assets are named `<package>-<package version>-mp<marketplace version>.zip`.",
        "",
    ]

    slug = os.environ.get("GITHUB_REPOSITORY")
    if slug and marketplace_name:
        first_plugin = next((name for name, kind, _, _ in rows if kind == "plugin"), None)
        lines += [
            "Plugins install over git — the attached archives are only for surfaces git",
            "cannot reach, such as uploading a standalone skill to claude.ai.",
            "",
            "```",
            f"/plugin marketplace add {slug}",
        ]
        if first_plugin:
            lines.append(f"/plugin install {first_plugin}@{marketplace_name}")
        lines += ["```", ""]

    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text("\n".join(lines), encoding="utf-8")

    emit(
        version=marketplace_version,
        assets=str(len(rows)),
        staging=str(staging.relative_to(root) if staging.is_relative_to(root) else staging),
        notes=str(notes_path.relative_to(root) if notes_path.is_relative_to(root) else notes_path),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
