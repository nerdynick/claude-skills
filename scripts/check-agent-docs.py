#!/usr/bin/env python3
"""Keep CLAUDE.md and AGENTS.md from drifting apart.

Different assistants read different filenames. CLAUDE.md is the source of
truth; AGENTS.md is the same bytes under the name other tooling looks for.
Two arrangements are accepted:

  * a symlink `AGENTS.md -> CLAUDE.md` (preferred -- it cannot drift), or
  * a regular file whose contents are byte-identical to CLAUDE.md.

A stale AGENTS.md is worse than a missing one: an assistant reads it, follows
rules that were revised months ago, and nothing anywhere reports a problem.

The script also checks the SHARED block markers. The generic half of CLAUDE.md
is maintained in the `claude-marketplace` template and copied into each repo
built from it; the markers are what make that half findable, so an unbalanced
or missing pair means the next sync has nothing to aim at.

Stdlib only, so the pre-commit hook and the CI runner execute the same code.

Usage:
    scripts/check-agent-docs.py [--root DIR] [--source CLAUDE.md]
                                [--mirror AGENTS.md] [--require-shared-block]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BEGIN = "<!-- BEGIN SHARED:"
END = "<!-- END SHARED -->"

ANNOTATE = os.environ.get("GITHUB_ACTIONS") == "true"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--source", default="CLAUDE.md", help="default: CLAUDE.md")
    parser.add_argument("--mirror", default="AGENTS.md", help="default: AGENTS.md")
    parser.add_argument(
        "--require-shared-block",
        action="store_true",
        help="fail when the SHARED markers are absent entirely",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    source = root / args.source
    mirror = root / args.mirror
    errors: list[tuple[str, str]] = []

    def fail(path: Path, message: str) -> None:
        try:
            name = str(path.relative_to(root))
        except ValueError:
            name = str(path)
        errors.append((name, message))

    if not source.is_file():
        fail(source, f"{args.source} is missing; it is the source of truth for both files")
        print(f"error: {args.source} is missing", file=sys.stderr)
        return 1

    text = source.read_text(encoding="utf-8")

    # --- AGENTS.md mirrors CLAUDE.md ---------------------------------------
    if not mirror.exists() and not mirror.is_symlink():
        fail(
            mirror,
            f"{args.mirror} is missing. Assistants that read {args.mirror} get no "
            f"repository guidance at all. Create it as a symlink: "
            f"`ln -s {args.source} {args.mirror}`",
        )
    elif mirror.is_symlink():
        target = os.readlink(mirror)
        if Path(target).name != args.source or Path(target).is_absolute():
            fail(
                mirror,
                f"{args.mirror} is a symlink to {target!r}, not to {args.source}. "
                f"Point it at {args.source} with a relative link so it resolves in "
                "every checkout and in an exported archive",
            )
        elif not mirror.resolve().is_file():
            fail(mirror, f"{args.mirror} is a symlink that does not resolve to a file")
    elif mirror.is_file():
        if mirror.read_text(encoding="utf-8") != text:
            fail(
                mirror,
                f"{args.mirror} is a maintained copy that has drifted from "
                f"{args.source}. Regenerate it with `make sync-agent-docs`, or replace "
                f"it with a symlink so it can never drift again",
            )
    else:
        fail(mirror, f"{args.mirror} is neither a regular file nor a symlink")

    # --- SHARED block markers ----------------------------------------------
    begins = text.count(BEGIN)
    ends = text.count(END)
    if begins == 0 and ends == 0:
        if args.require_shared_block:
            fail(
                source,
                f"{args.source} has no SHARED block. The generic half is maintained in "
                "the claude-marketplace template and copied here; without the markers "
                f"there is nothing for the next sync to replace. Wrap it in `{BEGIN} "
                f"... -->` and `{END}`",
            )
    elif begins != ends:
        fail(
            source,
            f"{args.source} has {begins} `{BEGIN}` marker(s) and {ends} `{END}` "
            "marker(s). They must pair up, or a sync will overwrite the wrong span",
        )

    for file, message in errors:
        print(f"error: {file}: {message}", file=sys.stderr)
        if ANNOTATE:
            print(f"::error file={file}::{message}")

    if errors:
        print(f"\n✘ {len(errors)} agent-docs problem(s)", file=sys.stderr)
        return 1

    how = "symlink" if mirror.is_symlink() else "maintained copy"
    shared = f", {begins} shared block(s)" if begins else ""
    print(f"✔ Agent docs OK — {args.mirror} is a {how} of {args.source}{shared}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
