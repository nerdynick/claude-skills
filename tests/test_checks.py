#!/usr/bin/env python3
"""Unit tests for the validation scripts in scripts/.

These are the backup for the pre-commit hook. The hook is the fast path and is
trivially bypassable (`--no-verify`), so CI runs both the real checks and this
suite -- the checks catch bad content, and these tests catch a check that has
stopped catching anything. A validator that silently passes everything is worse
than no validator, because it is trusted.

Stdlib only, no fixtures on disk: every case builds a throwaway repository in a
temporary directory, so the tests never depend on the repo's own contents.

Run with `make test`, or directly:
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def load(filename: str):
    """Import a hyphenated script as a module."""
    path = SCRIPTS / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


frontmatter = load("check-skill-frontmatter.py")
coverage = load("check-marketplace-coverage.py")
agent_docs = load("check-agent-docs.py")


GOOD_DESCRIPTION = (
    "Use when the user wants the thing. Covers the cases that matter and the "
    "phrases someone would actually type."
)


def skill_text(name: str, description: str = GOOD_DESCRIPTION, body_lines: int = 10) -> str:
    body = "\n".join(f"Line {n} of the skill body." for n in range(body_lines))
    return f"---\nname: {name}\ndescription: >-\n  {description}\n---\n\n# {name}\n\n{body}\n"


class TempRepo:
    """A disposable repository tree."""

    def __init__(self) -> None:
        self.path = Path(tempfile.mkdtemp(prefix="check-test-"))

    def write(self, relative: str, content: str) -> Path:
        target = self.path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def skill(self, relative: str, name: str, **kwargs) -> Path:
        return self.write(f"{relative}/SKILL.md", skill_text(name, **kwargs))

    def cleanup(self) -> None:
        shutil.rmtree(self.path, ignore_errors=True)


class RepoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = TempRepo()
        self.addCleanup(self.repo.cleanup)

    def report_for(self, *paths: Path) -> "frontmatter.Report":
        report = frontmatter.Report(self.repo.path)
        for path in paths:
            frontmatter.check_skill(path, report)
        return report

    def assertNoErrors(self, report) -> None:
        self.assertEqual([m for _, m in report.errors], [], "unexpected errors")

    def assertErrorMatching(self, report, needle: str) -> None:
        joined = " | ".join(m for _, m in report.errors)
        self.assertIn(needle, joined)

    def assertWarningMatching(self, report, needle: str) -> None:
        joined = " | ".join(m for _, m in report.warnings)
        self.assertIn(needle, joined)


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


class TestFrontmatterParsing(unittest.TestCase):
    def parse(self, block: str) -> dict:
        return frontmatter.parse_frontmatter_builtin(block)

    def test_folded_block_scalar_joins_lines_with_spaces(self) -> None:
        data = self.parse("name: a\ndescription: >-\n  one two\n  three four\n")
        self.assertEqual(data["description"], "one two three four")

    def test_folded_scalar_tolerates_colon_space(self) -> None:
        # This is the entire reason the convention exists.
        data = self.parse("name: a\ndescription: >-\n  three types: alpha and beta\n")
        self.assertEqual(data["description"], "three types: alpha and beta")

    def test_folded_scalar_tolerates_hash(self) -> None:
        data = self.parse("name: a\ndescription: >-\n  channel #general matters\n")
        self.assertEqual(data["description"], "channel #general matters")

    def test_literal_block_scalar_keeps_newlines(self) -> None:
        data = self.parse("name: a\ndescription: |-\n  one\n  two\n")
        self.assertEqual(data["description"], "one\ntwo")

    def test_blank_line_in_folded_scalar_becomes_newline(self) -> None:
        data = self.parse("name: a\ndescription: >-\n  one\n\n  two\n")
        self.assertEqual(data["description"], "one\ntwo")

    def test_plain_scalar_with_colon_space_is_a_parse_error(self) -> None:
        with self.assertRaises(frontmatter.FrontmatterError) as caught:
            self.parse("name: a\ndescription: three types: alpha\n")
        self.assertIn("colon-space", str(caught.exception))

    def test_plain_scalar_with_hash_is_a_parse_error(self) -> None:
        with self.assertRaises(frontmatter.FrontmatterError) as caught:
            self.parse("name: a\ndescription: ask in #general\n")
        self.assertIn("comment", str(caught.exception))

    def test_plain_scalar_without_traps_is_fine(self) -> None:
        data = self.parse("name: a\ndescription: a perfectly ordinary sentence\n")
        self.assertEqual(data["description"], "a perfectly ordinary sentence")

    def test_quoted_scalar_may_contain_a_colon(self) -> None:
        data = self.parse('name: a\ndescription: "types: alpha"\n')
        self.assertEqual(data["description"], "types: alpha")

    def test_block_list(self) -> None:
        data = self.parse("name: a\nallowed-tools:\n  - Read\n  - Bash\n")
        self.assertEqual(data["allowed-tools"], ["Read", "Bash"])

    def test_flow_sequence(self) -> None:
        data = self.parse("name: a\nallowed-tools: [Read, Bash]\n")
        self.assertEqual(data["allowed-tools"], ["Read", "Bash"])

    def test_booleans_and_null(self) -> None:
        data = self.parse("name: a\nuser-invocable: true\nshell: ~\n")
        self.assertIs(data["user-invocable"], True)
        self.assertIsNone(data["shell"])

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(frontmatter.FrontmatterError):
            self.parse("name: a\nname: b\n")

    def test_missing_opening_fence(self) -> None:
        with self.assertRaises(frontmatter.FrontmatterError) as caught:
            frontmatter.split_frontmatter("# Just a heading\n")
        self.assertIn("no YAML frontmatter", str(caught.exception))

    def test_unterminated_block(self) -> None:
        with self.assertRaises(frontmatter.FrontmatterError) as caught:
            frontmatter.split_frontmatter("---\nname: a\n")
        self.assertIn("never closed", str(caught.exception))

    def test_bom_is_reported_clearly(self) -> None:
        with self.assertRaises(frontmatter.FrontmatterError) as caught:
            frontmatter.split_frontmatter("﻿---\nname: a\n---\n")
        self.assertIn("BOM", str(caught.exception))

    def test_list_frontmatter_is_not_a_mapping(self) -> None:
        with self.assertRaises(frontmatter.FrontmatterError):
            frontmatter.parse_frontmatter("- one\n- two\n")

    def test_style_detection(self) -> None:
        self.assertTrue(frontmatter.description_is_plain_scalar("description: bare text"))
        self.assertFalse(frontmatter.description_is_plain_scalar("description: >-\n  folded"))
        self.assertFalse(frontmatter.description_is_plain_scalar('description: "quoted"'))

    @unittest.skipUnless(frontmatter.HAVE_YAML, "PyYAML not installed")
    def test_builtin_parser_agrees_with_pyyaml(self) -> None:
        import yaml  # type: ignore

        samples = [
            "name: a\ndescription: >-\n  one two\n  three\n",
            "name: a\ndescription: |-\n  one\n  two\n",
            "name: a\ndescription: >-\n  types: alpha\n",
            'name: a\ndescription: "quoted: value"\n',
            "name: a\nallowed-tools:\n  - Read\n  - Bash\n",
            "name: a\nallowed-tools: [Read, Bash]\n",
            "name: a\nuser-invocable: true\n",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(
                    frontmatter.parse_frontmatter_builtin(sample), yaml.safe_load(sample)
                )


# ---------------------------------------------------------------------------
# Frontmatter rules
# ---------------------------------------------------------------------------


class TestDescriptionLimit(RepoTestCase):
    def test_exactly_at_the_limit_passes(self) -> None:
        path = self.repo.skill("skills/demo", "demo", description="x" * 1024)
        self.assertNoErrors(self.report_for(path))

    def test_one_over_the_limit_fails(self) -> None:
        path = self.repo.skill("skills/demo", "demo", description="x" * 1025)
        report = self.report_for(path)
        self.assertErrorMatching(report, "over the hard 1024-character limit by 1")

    def test_approaching_the_limit_warns(self) -> None:
        path = self.repo.skill("skills/demo", "demo", description="x" * 1000)
        report = self.report_for(path)
        self.assertNoErrors(report)
        self.assertWarningMatching(report, "close to the 1024 limit")

    def test_missing_description_fails(self) -> None:
        path = self.repo.write("skills/demo/SKILL.md", "---\nname: demo\n---\n\nBody\n")
        self.assertErrorMatching(self.report_for(path), "no `description:` field")

    def test_plain_scalar_style_warns(self) -> None:
        path = self.repo.write(
            "skills/demo/SKILL.md", "---\nname: demo\ndescription: plain text here\n---\n\nBody\n"
        )
        report = self.report_for(path)
        self.assertNoErrors(report)
        self.assertWarningMatching(report, "unquoted plain scalar")


class TestLineLimit(RepoTestCase):
    def test_exactly_500_lines_passes(self) -> None:
        path = self.repo.write("skills/demo/SKILL.md", "\n".join(["x"] * 500) + "\n")
        content = skill_text("demo", body_lines=0)
        padding = 500 - len(content.splitlines())
        path.write_text(content + "\n".join(["filler"] * padding) + "\n", encoding="utf-8")
        self.assertEqual(len(path.read_text().splitlines()), 500)
        self.assertNoErrors(self.report_for(path))

    def test_501_lines_fails_with_split_guidance(self) -> None:
        content = skill_text("demo", body_lines=0)
        padding = 501 - len(content.splitlines())
        path = self.repo.write(
            "skills/demo/SKILL.md", content + "\n".join(["filler"] * padding) + "\n"
        )
        report = self.report_for(path)
        self.assertErrorMatching(report, "is 501 lines, over the 500-line limit")
        self.assertErrorMatching(report, "references/")

    def test_approaching_the_limit_warns(self) -> None:
        content = skill_text("demo", body_lines=0)
        padding = 470 - len(content.splitlines())
        path = self.repo.write(
            "skills/demo/SKILL.md", content + "\n".join(["filler"] * padding) + "\n"
        )
        report = self.report_for(path)
        self.assertNoErrors(report)
        self.assertWarningMatching(report, "approaching the 500-line limit")

    def test_line_limit_is_reported_even_when_frontmatter_is_broken(self) -> None:
        body = "\n".join(["filler"] * 600)
        path = self.repo.write("skills/demo/SKILL.md", f"# No frontmatter\n{body}\n")
        report = self.report_for(path)
        self.assertErrorMatching(report, "over the 500-line limit")
        self.assertErrorMatching(report, "no YAML frontmatter")


class TestNameRules(RepoTestCase):
    def test_name_matching_directory_passes(self) -> None:
        path = self.repo.skill("skills/my-skill", "my-skill")
        self.assertNoErrors(self.report_for(path))

    def test_name_not_matching_directory_fails(self) -> None:
        path = self.repo.skill("skills/my-skill", "other-skill")
        self.assertErrorMatching(self.report_for(path), "does not match its directory")

    def test_nested_plugin_skill_matches_its_own_directory(self) -> None:
        path = self.repo.skill("plugins/toolkit/skills/my-skill", "my-skill")
        self.assertNoErrors(self.report_for(path))

    def test_missing_name_fails(self) -> None:
        path = self.repo.write(
            "skills/demo/SKILL.md", f"---\ndescription: >-\n  {GOOD_DESCRIPTION}\n---\n\nBody\n"
        )
        report = self.report_for(path)
        self.assertErrorMatching(report, "has no `name:` field")
        self.assertErrorMatching(report, "name: demo")

    def test_uppercase_name_fails(self) -> None:
        path = self.repo.skill("skills/My-Skill", "My-Skill")
        self.assertErrorMatching(self.report_for(path), "must be lowercase letters")

    def test_underscore_name_fails(self) -> None:
        path = self.repo.skill("skills/my_skill", "my_skill")
        self.assertErrorMatching(self.report_for(path), "must be lowercase letters")

    def test_doubled_hyphen_name_fails(self) -> None:
        path = self.repo.skill("skills/my--skill", "my--skill")
        self.assertErrorMatching(self.report_for(path), "must be lowercase letters")

    def test_trailing_hyphen_name_fails(self) -> None:
        path = self.repo.skill("skills/my-skill-", "my-skill-")
        self.assertErrorMatching(self.report_for(path), "must be lowercase letters")

    def test_name_over_64_characters_fails(self) -> None:
        long_name = "a" * 65
        path = self.repo.skill(f"skills/{long_name}", long_name)
        self.assertErrorMatching(self.report_for(path), "over the 64 limit")

    def test_digits_and_hyphens_are_allowed(self) -> None:
        path = self.repo.skill("skills/skill-2-go", "skill-2-go")
        self.assertNoErrors(self.report_for(path))


class TestOtherFields(RepoTestCase):
    def build(self, extra: str) -> Path:
        return self.repo.write(
            "skills/demo/SKILL.md",
            f"---\nname: demo\ndescription: >-\n  {GOOD_DESCRIPTION}\n{extra}---\n\nBody\n",
        )

    def test_shell_bash_is_allowed(self) -> None:
        self.assertNoErrors(self.report_for(self.build("shell: bash\n")))

    def test_shell_zsh_is_rejected(self) -> None:
        self.assertErrorMatching(
            self.report_for(self.build("shell: zsh\n")), "must be exactly `bash` or `powershell`"
        )

    def test_allowed_tools_as_string(self) -> None:
        self.assertNoErrors(self.report_for(self.build("allowed-tools: Read\n")))

    def test_allowed_tools_as_list(self) -> None:
        self.assertNoErrors(self.report_for(self.build("allowed-tools:\n  - Read\n  - Bash\n")))

    def test_unrecognized_key_warns(self) -> None:
        report = self.report_for(self.build("descriptionn: typo\n"))
        self.assertNoErrors(report)
        self.assertWarningMatching(report, "unrecognized frontmatter key `descriptionn`")


class TestDiscoveryAndBudget(RepoTestCase):
    def test_finds_skills_under_both_trees(self) -> None:
        self.repo.skill("skills/standalone", "standalone")
        self.repo.skill("plugins/toolkit/skills/nested", "nested")
        found = frontmatter.find_skills(self.repo.path, ["skills", "plugins"])
        self.assertEqual(len(found), 2)

    def test_plugin_root_skill_is_found(self) -> None:
        self.repo.skill("plugins/solo", "solo")
        found = frontmatter.find_skills(self.repo.path, ["skills", "plugins"])
        self.assertEqual(len(found), 1)

    def test_description_length_is_returned_for_the_budget(self) -> None:
        path = self.repo.skill("skills/demo", "demo", description="x" * 300)
        report = frontmatter.Report(self.repo.path)
        self.assertEqual(frontmatter.check_skill(path, report), 300)


# ---------------------------------------------------------------------------
# Marketplace coverage
# ---------------------------------------------------------------------------


class CoverageTestCase(RepoTestCase):
    def manifest(self, **overrides) -> None:
        import json

        data = {
            "name": "demo-market",
            "owner": {"name": "Demo"},
            "version": "0.1.0",
            "plugins": [],
        }
        data.update(overrides)
        self.repo.write(".claude-plugin/marketplace.json", json.dumps(data, indent=2))

    def plugin(self, name: str) -> None:
        import json

        self.repo.write(
            f"plugins/{name}/.claude-plugin/plugin.json",
            json.dumps({"name": name, "description": "d", "version": "0.1.0"}),
        )
        self.repo.skill(f"plugins/{name}/skills/{name}-skill", f"{name}-skill")

    def run_check(self) -> tuple[int, str]:
        import contextlib
        import io
        import sys

        argv = sys.argv
        sys.argv = ["check", "--root", str(self.repo.path)]
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = coverage.main()
        finally:
            sys.argv = argv
        return code, out.getvalue() + err.getvalue()


class TestMarketplaceCoverage(CoverageTestCase):
    def test_registered_plugin_passes(self) -> None:
        self.plugin("demo-tool")
        self.manifest(plugins=[{"name": "demo-tool", "source": "./plugins/demo-tool"}])
        code, output = self.run_check()
        self.assertEqual(code, 0, output)

    def test_unregistered_plugin_fails(self) -> None:
        self.plugin("demo-tool")
        self.manifest()
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("is not registered", output)

    def test_source_pointing_nowhere_fails(self) -> None:
        self.manifest(plugins=[{"name": "ghost", "source": "./plugins/ghost"}])
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("no directory exists there", output)

    def test_source_without_dot_slash_fails(self) -> None:
        self.plugin("demo-tool")
        self.manifest(plugins=[{"name": "demo-tool", "source": "plugins/demo-tool"}])
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('must start with "./"', output)

    def test_source_escaping_the_root_fails(self) -> None:
        self.manifest(plugins=[{"name": "escapee", "source": "./../elsewhere"}])
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("escapes the", output)

    def test_plugin_name_mismatch_fails(self) -> None:
        self.plugin("demo-tool")
        self.manifest(plugins=[{"name": "wrong-name", "source": "./plugins/demo-tool"}])
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("name mismatch", output)

    def test_duplicate_entry_names_fail(self) -> None:
        self.plugin("demo-tool")
        self.manifest(
            plugins=[
                {"name": "demo-tool", "source": "./plugins/demo-tool"},
                {"name": "demo-tool", "source": "./plugins/demo-tool"},
            ]
        )
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("duplicate plugin name", output)

    def test_standalone_skill_as_single_skill_plugin_passes(self) -> None:
        # plugin.json is optional: a directory with only a SKILL.md loads as one
        # skill. This is how standalone skills reach the marketplace.
        self.repo.skill("skills/solo-skill", "solo-skill")
        self.manifest(plugins=[{"name": "solo-skill", "source": "./skills/solo-skill"}])
        code, output = self.run_check()
        self.assertEqual(code, 0, output)

    def test_standalone_skill_name_mismatch_fails(self) -> None:
        self.repo.skill("skills/solo-skill", "different-name")
        self.manifest(plugins=[{"name": "solo-skill", "source": "./skills/solo-skill"}])
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("name mismatch", output)

    def test_uncatalogued_standalone_skill_fails(self) -> None:
        self.repo.skill("skills/solo-skill", "solo-skill")
        self.manifest()
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("not reachable from any marketplace entry", output)

    def test_source_with_neither_manifest_nor_skill_fails(self) -> None:
        self.repo.write("plugins/empty/README.md", "nothing here")
        self.manifest(plugins=[{"name": "empty", "source": "./plugins/empty"}])
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("neither", output)

    def test_reserved_marketplace_name_fails(self) -> None:
        self.manifest(name="agent-skills")
        self.repo.skill("skills/solo-skill", "solo-skill")
        self.manifest(
            name="agent-skills",
            plugins=[{"name": "solo-skill", "source": "./skills/solo-skill"}],
        )
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("reserved by Anthropic", output)

    def test_non_kebab_marketplace_name_fails(self) -> None:
        self.repo.skill("skills/solo-skill", "solo-skill")
        self.manifest(
            name="Demo_Market",
            plugins=[{"name": "solo-skill", "source": "./skills/solo-skill"}],
        )
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("lowercase kebab-case", output)

    def test_missing_owner_fails(self) -> None:
        import json

        self.repo.write(
            ".claude-plugin/marketplace.json",
            json.dumps({"name": "demo-market", "plugins": []}),
        )
        self.repo.skill("skills/solo-skill", "solo-skill")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('missing required top-level field "owner"', output)

    def test_version_on_a_skill_entry_warns_without_failing(self) -> None:
        self.repo.skill("skills/solo-skill", "solo-skill")
        self.manifest(
            plugins=[
                {"name": "solo-skill", "source": "./skills/solo-skill", "version": "1.0.0"}
            ]
        )
        code, output = self.run_check()
        self.assertEqual(code, 0, output)
        self.assertIn("pins it", output)

    def test_version_on_a_plugin_entry_warns_without_failing(self) -> None:
        self.plugin("demo-tool")
        self.manifest(
            plugins=[
                {"name": "demo-tool", "source": "./plugins/demo-tool", "version": "1.0.0"}
            ]
        )
        code, output = self.run_check()
        self.assertEqual(code, 0, output)
        self.assertIn("plugin.json wins", output)

    def test_untouched_template_passes(self) -> None:
        self.manifest(name="<marketplace-name>", owner={"name": "<owner-name>"})
        code, output = self.run_check()
        self.assertEqual(code, 0, output)

    def test_placeholder_name_with_real_packages_fails(self) -> None:
        self.repo.skill("skills/solo-skill", "solo-skill")
        self.manifest(
            name="<marketplace-name>",
            plugins=[{"name": "solo-skill", "source": "./skills/solo-skill"}],
        )
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("template placeholder", output)

    def test_invalid_json_fails(self) -> None:
        self.repo.write(".claude-plugin/marketplace.json", "{ not json")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", output)


# ---------------------------------------------------------------------------
# Agent docs
# ---------------------------------------------------------------------------


class TestAgentDocs(RepoTestCase):
    def run_check(self, *extra: str) -> tuple[int, str]:
        import contextlib
        import io
        import sys

        argv = sys.argv
        sys.argv = ["check", "--root", str(self.repo.path), *extra]
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = agent_docs.main()
        finally:
            sys.argv = argv
        return code, out.getvalue() + err.getvalue()

    def test_symlink_passes(self) -> None:
        self.repo.write("CLAUDE.md", "# Guidance\n")
        os.symlink("CLAUDE.md", self.repo.path / "AGENTS.md")
        code, output = self.run_check()
        self.assertEqual(code, 0, output)
        self.assertIn("symlink", output)

    def test_identical_copy_passes(self) -> None:
        self.repo.write("CLAUDE.md", "# Guidance\n")
        self.repo.write("AGENTS.md", "# Guidance\n")
        code, output = self.run_check()
        self.assertEqual(code, 0, output)
        self.assertIn("maintained copy", output)

    def test_drifted_copy_fails(self) -> None:
        self.repo.write("CLAUDE.md", "# Guidance\nnew rule\n")
        self.repo.write("AGENTS.md", "# Guidance\n")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("drifted", output)

    def test_missing_mirror_fails(self) -> None:
        self.repo.write("CLAUDE.md", "# Guidance\n")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("is missing", output)

    def test_symlink_to_the_wrong_file_fails(self) -> None:
        self.repo.write("CLAUDE.md", "# Guidance\n")
        self.repo.write("OTHER.md", "# Other\n")
        os.symlink("OTHER.md", self.repo.path / "AGENTS.md")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("not to CLAUDE.md", output)

    def test_absolute_symlink_fails(self) -> None:
        source = self.repo.write("CLAUDE.md", "# Guidance\n")
        os.symlink(str(source), self.repo.path / "AGENTS.md")
        code, output = self.run_check()
        self.assertEqual(code, 1)

    def test_missing_source_fails(self) -> None:
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("CLAUDE.md is missing", output)

    def test_balanced_shared_markers_pass(self) -> None:
        self.repo.write(
            "CLAUDE.md", "# G\n<!-- BEGIN SHARED: template -->\nx\n<!-- END SHARED -->\n"
        )
        os.symlink("CLAUDE.md", self.repo.path / "AGENTS.md")
        code, output = self.run_check()
        self.assertEqual(code, 0, output)
        self.assertIn("1 shared block", output)

    def test_unbalanced_shared_markers_fail(self) -> None:
        self.repo.write("CLAUDE.md", "# G\n<!-- BEGIN SHARED: template -->\nx\n")
        os.symlink("CLAUDE.md", self.repo.path / "AGENTS.md")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("must pair up", output)

    def test_missing_shared_block_only_fails_when_required(self) -> None:
        self.repo.write("CLAUDE.md", "# G\n")
        os.symlink("CLAUDE.md", self.repo.path / "AGENTS.md")
        self.assertEqual(self.run_check()[0], 0)
        self.assertEqual(self.run_check("--require-shared-block")[0], 1)


if __name__ == "__main__":
    unittest.main()
