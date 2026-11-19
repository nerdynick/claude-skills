#!/usr/bin/env python3
"""Cross-check the packages on disk against .claude-plugin/marketplace.json.

`claude plugin validate --strict` only inspects manifest *shape*; it never looks
at the filesystem. Several mistakes therefore pass validation and only surface
when a user tries to install:

  1. A plugin or standalone skill exists in the repo but was never registered
     in marketplace.json, so nobody can install it.
  2. A relative `source` (or `skills`) path points at a directory that does not
     exist, escapes the repository root, or omits the required `./` prefix.
  3. A registered source is not actually loadable -- it has neither a
     `.claude-plugin/plugin.json` nor a `SKILL.md` at its root.
  4. An entry name disagrees with the name on disk, which is what drives the
     `/plugin install <name>@<marketplace>` namespace.
  5. The marketplace itself uses a name Claude Code reserves, or one that is
     not lowercase kebab-case, so it silently refuses to load.

This script closes those gaps. It has no dependencies beyond the standard
library so it runs identically on a dev machine and on a CI runner.

Usage:
    scripts/check-marketplace-coverage.py [--root DIR] [--plugins-dir NAME]
                                          [--skills-dir NAME] [--manifest PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# GitHub and Forgejo render `::error::` lines as annotations on the diff.
ANNOTATE = os.environ.get("GITHUB_ACTIONS") == "true"

# Marketplace names Claude Code and Claude Desktop refuse to load. A repo that
# picks one of these looks fine in every validator and simply never appears.
RESERVED_NAMES = {
    "agent-skills",
    "anthropic-agent-skills",
    "anthropic-marketplace",
    "anthropic-plugins",
    "claude-code-marketplace",
    "claude-code-plugins",
    "claude-community",
    "claude-for-financial-services",
    "claude-for-legal",
    "claude-plugins-community",
    "claude-plugins-official",
    "financial-services-plugins",
    "first-party-plugins",
    "healthcare",
    "knowledge-work-plugins",
    "life-sciences",
    "org",
    "org-provisioned",
    "unknown",
}

MARKETPLACE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# An untouched copy of the template still carries `<placeholder>` values. Those
# are the intended starting state, so they are reported as a notice rather than
# an error -- but only while nothing has been registered yet.
PLACEHOLDER_RE = re.compile(r"^<.*>$")


def is_placeholder(value: object) -> bool:
    return isinstance(value, str) and bool(PLACEHOLDER_RE.match(value.strip()))


def frontmatter_name(skill_md: Path) -> str | None:
    """Pull `name:` out of a SKILL.md frontmatter block.

    Deliberately a regex and not a YAML parse: this script only needs the name,
    and check-skill-frontmatter.py already owns full frontmatter validation.
    """
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    block = text[3:end] if end != -1 else text[3:]
    match = re.search(r"^name:\s*(\S+)\s*$", block, re.MULTILINE)
    return match.group(1) if match else None


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
    warnings: list[str] = []

    def fail(message: str, file: Path | None = None) -> None:
        errors.append((rel(file) if file else rel(manifest_path), message))

    def warn(message: str) -> None:
        warnings.append(message)

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
    untouched_template = not entries and not disk_plugins and not disk_skills

    # --- Top-level manifest shape -------------------------------------------
    # `claude plugin validate` covers most of this, but it is not always
    # installed (the pre-commit hook runs without it), and the reserved-name
    # list is checked nowhere else.
    for field in ("name", "owner", "plugins"):
        if field not in manifest:
            fail(f'missing required top-level field "{field}"')

    owner = manifest.get("owner")
    if isinstance(owner, dict) and "name" not in owner:
        fail('"owner" is missing its required "name" field')
    elif owner is not None and not isinstance(owner, dict):
        fail(f'"owner" must be an object, not a {type(owner).__name__}')

    market_name = manifest.get("name")
    if isinstance(market_name, str) and market_name:
        if is_placeholder(market_name):
            if not untouched_template:
                fail(
                    f'marketplace name "{market_name}" is still a template placeholder; '
                    "replace it with the real marketplace name before registering packages"
                )
        elif market_name.lower() in RESERVED_NAMES:
            fail(
                f'marketplace name "{market_name}" is reserved by Anthropic and will '
                "never load; pick another"
            )
        elif not MARKETPLACE_NAME_RE.match(market_name):
            fail(
                f'marketplace name "{market_name}" must be lowercase kebab-case '
                "(letters, digits and hyphens, starting with a letter or digit)"
            )

    if untouched_template:
        print("No plugins or skills registered or on disk yet — nothing to cross-check.")
        return 1 if errors else 0

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

        if "source" not in entry:
            fail(f'plugin "{name}" is missing its required "source" field')
            continue

        if isinstance(source, str):
            # A local source that does not start with ./ is resolved as a
            # marketplace-relative name rather than a path, so it silently
            # fails to install instead of erroring at validation time.
            if not source.startswith("./") and not plugin_root:
                fail(
                    f'plugin "{name}" has local source "{source}"; relative sources '
                    'must start with "./" so they resolve against the repository root'
                )
                continue
            if ".." in Path(source).parts:
                fail(
                    f'plugin "{name}" has source "{source}", which escapes the '
                    "repository root; a plugin is copied into the install cache and "
                    "cannot reference anything outside its own directory"
                )
                continue

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

        # A source may point straight at a standalone skill directory. That is
        # the documented single-skill-plugin pattern: plugin.json is optional,
        # so a directory holding just a SKILL.md loads as one skill and takes
        # its invocation name from the frontmatter. Such an entry covers that
        # skill without any `skills` list.
        plugin_manifest = base / ".claude-plugin" / "plugin.json"
        root_skill = base / "SKILL.md"
        if base != root and not plugin_manifest.is_file():
            if root_skill.is_file():
                if base.parent == skills_dir:
                    covered_skills.add(base)
                declared = frontmatter_name(root_skill)
                if declared is None:
                    fail(
                        f'plugin "{name}" points at {rel(base)}, whose SKILL.md has no '
                        "frontmatter `name`; Claude Code would name the skill after the "
                        "install directory, which for a marketplace install is a version "
                        "string that changes on every update",
                        root_skill,
                    )
                elif declared != name:
                    fail(
                        f'name mismatch: marketplace entry "{name}" points at '
                        f'{rel(root_skill)}, which declares "{declared}"',
                        root_skill,
                    )
            else:
                fail(
                    f'plugin "{name}" points at {rel(base)}, which has neither '
                    ".claude-plugin/plugin.json nor SKILL.md, so Claude Code cannot "
                    "load it as a plugin or as a skill"
                )
                continue

        # `version` on an entry is almost always a mistake, in both directions.
        if "version" in entry:
            if plugin_manifest.is_file():
                warn(
                    f'plugin "{name}" sets "version" on its marketplace entry while '
                    "its plugin.json also declares one; plugin.json wins, so the entry "
                    "copy only drifts. Drop it"
                )
            else:
                warn(
                    f'skill "{name}" sets "version" on its marketplace entry, which '
                    "pins it; installed users stop receiving updates until someone "
                    "bumps it. Omit it to track the repository"
                )

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
    for message in warnings:
        print(f"warning: {message}")
        if ANNOTATE:
            print(f"::warning file={rel(manifest_path)}::{message}")

    if errors:
        print(f"✘ {len(errors)} coverage problem(s) in {rel(manifest_path)}:\n")
        for file, message in errors:
            print(f"  - {message}")
            if ANNOTATE:
                print(f"::error file={file}::{message}")
        return 1

    skill_summary = "all (directory-wide)" if all_skills_covered else str(len(covered_skills))
    summary = (
        f"✔ Coverage OK — {len(entries)} marketplace entr{'y' if len(entries) == 1 else 'ies'}, "
        f"{len(disk_plugins)} plugin(s) on disk, {len(disk_skills)} skill(s) on disk "
        f"(skills exposed: {skill_summary})"
    )
    if warnings:
        summary += f", {len(warnings)} warning(s)"
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
