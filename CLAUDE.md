# CLAUDE.md

Rules for working in this repository. **[`README.md`](README.md) is the
background** — what this marketplace is, what each plugin covers, and how to
install from it. This file does not repeat any of that.

## Repository purpose

A Claude Code **plugin marketplace** plus a collection of standalone skills.
Built from the [`claude-marketplace`](https://github.com/nerdynick/claude-marketplace)
template, which is where the generic half of this file and all of `scripts/`,
`tests/` and `.github/workflows/` come from.

## Project structure

- `.claude-plugin/marketplace.json` — the marketplace catalog; every plugin must be registered here
- `skills/` — standalone skills
- `plugins/` — standalone plugins
- `scripts/` — validation scripts, the release stager, and `hooks/pre-commit`
- `tests/` — unit tests for those scripts
- `dist/` — generated package archives (gitignored)
- `Makefile` — build, validation, and packaging commands

## Package conventions

- Every skill and plugin directory must be prefixed with `nerdynik-`
- The directory name must match the `name` field in the package manifest
- Each package should include a README describing its purpose and usage
- Keep package metadata in the package directory itself
- Package manifests declare `"license": "GPL-3.0-or-later"`

<!-- BEGIN SHARED: claude-marketplace -->
<!--                                                                          -->
<!-- Generic marketplace-repo rules. This span is maintained in the           -->
<!-- claude-marketplace template and copied VERBATIM into every repo built    -->
<!-- from it. Edit it there first, then copy the whole span forward.          -->
<!-- Anything repo-specific belongs OUTSIDE the markers.                      -->
<!--                                                                          -->

## AGENTS.md and CLAUDE.md

`CLAUDE.md` is the source of truth. `AGENTS.md` is a **symlink** to it, so an
assistant looking for the other filename reads the same bytes and the two can
never drift.

- **Edit `CLAUDE.md`.** Never write to `AGENTS.md`: on a normal checkout you
  would be writing through the symlink into `CLAUDE.md` anyway, and on one
  without symlink support you would be forking it.
- `make validate-agent-docs` fails if the symlink is missing, points somewhere
  else, or — where a real file is used instead — has drifted.
- **These two files hold the rules. `README.md` holds the background.** What
  this repository is, what it contains, who it is for, and how to install from
  it live in `README.md` and are deliberately not duplicated here. A change
  that affects both means updating `README.md` for the humans and this file for
  the rules.

## Before you commit

A pre-commit hook runs the checks below and **blocks the commit** on any
failure. Install it once per clone:

```
make install-hooks
```

That points `core.hooksPath` at the tracked `scripts/hooks/` directory, so the
hook updates with the repository rather than going stale as a copy in
`.git/hooks`.

**Satisfy these while writing, rather than discovering them at the hook.**
Every one fails *silently* at runtime — the skill loads with empty metadata, or
never fires, and nothing anywhere reports a problem. That is the whole reason
they are enforced mechanically instead of by review:

| Rule | Enforced by |
|---|---|
| `SKILL.md` `description` is ≤ 1024 characters | `make validate-skills` |
| `SKILL.md` frontmatter parses as YAML and is a mapping | `make validate-skills` |
| `SKILL.md` has a `name`: lowercase letters, digits and hyphens only, ≤ 64 characters | `make validate-skills` |
| `SKILL.md` `name` equals the directory that contains it | `make validate-skills` |
| `SKILL.md` is ≤ 500 lines | `make validate-skills` |
| Every package on disk is registered, and every `source` resolves | `make validate-coverage` |
| Manifests pass `claude plugin validate --strict` | `make validate-manifests` |
| `AGENTS.md` still mirrors `CLAUDE.md` | `make validate-agent-docs` |

Run `make validate` before committing. It is the same set, plus the warnings
the hook reports but does not block on — a description at 980 characters, a
`SKILL.md` at 470 lines, an unrecognized frontmatter key.

**Bypassing.** `git commit --no-verify`, or `SKIP_SKILL_CHECKS=1 git commit` to
skip only this hook. Both are reasonable for a work-in-progress commit on a
branch. Neither gets anything merged: **CI runs the identical checks**, and
`make test` runs unit tests over the checkers themselves, so a validator that
has quietly stopped catching anything is caught too.

**When a check fails, fix the content — never loosen the check.** These limits
belong to the loader, not to this repository.

## Commands

| Command | Does |
|---|---|
| `make list` | Show discovered skills and plugins |
| `make validate` | Every check below, in one go |
| `make validate-manifests` | `claude plugin validate --strict` on the marketplace and each plugin |
| `make validate-coverage` | Every package registered, every `source` resolvable |
| `make validate-skills` | `SKILL.md` frontmatter, description length, line count, naming |
| `make validate-agent-docs` | `AGENTS.md` still mirrors `CLAUDE.md` |
| `make test` | Unit tests for the validation scripts |
| `make install-hooks` / `make uninstall-hooks` | Install or remove the pre-commit hook |
| `make package-all` | Build archives under `dist/` |
| `make clean` | Remove `dist/` |

CI runs the same Makefile targets, so `make validate` locally is exactly what
the pull-request check runs.

## Skill frontmatter rules (`SKILL.md`)

Frontmatter is what makes a skill *findable*. Every rule below has a silent
failure mode — a broken or oversized skill throws no error, it just never
fires. Most are now enforced by `make validate-skills`; the ones that aren't
are marked, and stay human.

### Recognized fields

| Field | Type | Constraints |
|---|---|---|
| `name` | string | lowercase letters, digits, hyphens only; **≤64 chars**; must equal the containing directory name |
| `description` | string | **≤1024 characters — hard limit** |
| `allowed-tools` / `disallowed-tools` | string or array of strings | array entries must all be strings |
| `shell` | string | exactly `bash` or `powershell`; nothing else |
| `argument-hint`, `when_to_use`, `disable-model-invocation`, `user-invocable`, `hooks` | — | recognized by the loader |

Unrecognized keys are **ignored, not rejected** — a typo'd key fails silently
and forever. `make validate-skills` warns about any key outside the recognized
set, which is the only way a misspelling ever surfaces.

`name` is technically optional, but omit it and Claude Code falls back to the
install directory name, which for a marketplace install is a **version string
that changes on every update**. Always set it explicitly — the validator
requires it.

### `description` must be ≤1024 characters

The hard per-skill cap. `claude plugin validate` does not check it; the limit
otherwise surfaces as an alert on the surfaces that load the skill, long after
the commit. `make validate-skills` measures the *parsed* value and fails over
the limit, warning from 950 so an ordinary edit doesn't tip it over.

When trimming to fit, cut redundant near-duplicate trigger phrases first —
`"case study"` already covers `"case studies"`, and plural/singular pairs are
pure overhead. Cut prose that restates the skill body second. Keep the distinct
trigger vocabulary.

### Always write `description` as a folded block scalar (`>-`)

A long unquoted one-line `description:` is a plain YAML scalar, and it breaks
the moment the text contains `: ` (colon-space) or ` #`. That is a *parse*
failure, and the consequence is severe:

> YAML frontmatter failed to parse … At runtime this skill loads with empty
> metadata (**all frontmatter fields silently dropped**).

No name, no description, no routing — the skill is invisible. This has already
happened for real: a description reading `…the three content types: general
company pages` silently disabled the skill it belonged to.

Use a folded block scalar for every description, wrapped at ~92 columns with a
2-space indent. Inside a block scalar, colons and `#` are literal text, so the
failure mode disappears:

```yaml
---
name: my-skill
description: >-
  Does the thing. Use when the user wants the thing, including cases like this: a colon here
  is safe because a folded scalar takes everything literally and joins these lines with single
  spaces. Trigger on "the thing", "do the thing".
---
```

`make validate-skills` fails on a plain scalar that already contains one of
those sequences, and warns on any plain scalar at all — a latent break waiting
for the next edit.

### `SKILL.md` must be ≤500 lines

Past roughly 500 lines a skill stops being read well: the body is loaded whole,
so every line costs context on every invocation, and the instructions that
matter get buried among the ones that don't.

**When a file goes over, split it rather than trimming prose.** Move the
longest self-contained sections into their own files under `references/` (or
`assets/`) and leave a one-line pointer plus a short summary in `SKILL.md`.
That is progressive disclosure: the body stays cheap to load and the detail is
still there when it's needed.

Good candidates to extract, in order: long reference tables, worked examples,
per-case playbooks, and setup or environment instructions. A section that reads
as "here is everything about X" is almost always better as `references/x.md`.

Two things to carry with the extraction: fix any "(see X above)"-style
cross-references elsewhere in `SKILL.md` that assumed the content was still
local, and keep a one-line summary at the pointer so the model can tell whether
it needs to open the file at all.

`make validate-skills` fails over 500 lines and warns from 450.

### Descriptions share one context budget

Every loaded skill's description sits in the prompt together, against a
**combined budget**. Over budget, Claude Code degrades — truncating
descriptions, dropping them for less-used skills, or falling back to names-only
— and warns `Skill listing over budget: N skills, X chars > Y budget`.

So a bloated description isn't just that skill's problem; it costs every other
skill's discoverability. Treat 1024 as the ceiling, not the target.
`make validate-skills` reports the combined total and warns past 12,000
characters. `/skill-doctor` shows which loaded skills are unused and burning
context.

### `description` is routing copy, not catalogue copy

Two different descriptions exist for a package and they must not be
interchanged:

- **`SKILL.md` `description:`** — written for the *model*. Third person, dense
  with trigger words and phrases someone would actually type. States what the
  skill does *and* when to reach for it. Long and specific beats elegant.
- **`marketplace.json` `description`** — short human catalogue copy, one
  sentence.

Don't paste one into the other. No validator can tell them apart; this one
stays human.

### What is checked where

| Check | Where |
|---|---|
| frontmatter present, parses, is a mapping | `check-skill-frontmatter.py` |
| `description` present, a string, ≤1024 characters | `check-skill-frontmatter.py` |
| `name` present, a string, ≤64 characters, charset, matches directory | `check-skill-frontmatter.py` |
| file ≤500 lines | `check-skill-frontmatter.py` |
| `allowed-tools` / `disallowed-tools` types, `shell` value | `check-skill-frontmatter.py` |
| unrecognized keys, plain-scalar style, near-limit sizes, combined budget | `check-skill-frontmatter.py` (warnings) |
| package registered, `source` resolvable and loadable, names agree, reserved marketplace name | `check-marketplace-coverage.py` |
| manifest shape | `claude plugin validate --strict` |
| `AGENTS.md` mirrors `CLAUDE.md` | `check-agent-docs.py` |
| **whether a description is any good** — accurate, well-triggered, routing-friendly | **human review** |

The last row is the point of the other rows: mechanical limits are enforced
mechanically so that review time goes to the part a script cannot judge.
<!-- END SHARED -->

## Marketplace

- The marketplace is named `nerdynik`; users install with `/plugin install <plugin>@nerdynik`
- Plugin `source` values are paths relative to the repository root and must start with `./`, e.g. `./plugins/nerdynik-<name>`
- Standalone skills are **not** listed in `marketplace.json` — that mechanism is plugin-only
- Bump a plugin's `version` in `.claude-plugin/plugin.json` on every published change; the version pins the plugin, so users get new code only when it changes
- Renaming an already-published plugin breaks existing installs unless a `renames` entry is added to `marketplace.json`

## Sharing files between skills in one plugin

- Do **not** use `${CLAUDE_PLUGIN_ROOT}` in skill content to reach bundled files. It isn't substituted on every surface that loads skills — Claude Desktop leaves it literal, and the read fails.
- Instead keep one copy at the plugin root (e.g. `references/`) and symlink it into each skill directory: `ln -s ../../references skills/<skill>/references`. The skill then uses a plain relative path, `references/vikunja.md`.
- This works because a symlink resolving *within* the plugin's own directory is preserved as a relative symlink in the plugin cache. Symlinks pointing outside the plugin are dereferenced or skipped.
- Edit the shared copy only; the skill-directory entries are links. `make package-plugins` dereferences them into real files in the archive, so an unzipped skill is self-contained.

## Naming: `nerdynik` vs `nerdynick`

Both spellings are intentional. The package prefix and marketplace name use
`nerdynik`; anything pointing at GitHub (clone URLs, `owner/repo` shorthand,
profile links) uses the account name `nerdynick`. Do not normalize one to the
other.

## When adding or renaming a package, update

1. `.claude-plugin/marketplace.json` (plugins only)
2. The repository `README.md`

The `Makefile` discovers packages by glob, so it needs no change.
`make validate` catches a package that was added to disk but not to the
catalog; nothing catches a stale `README.md`, so that one is on you.

## Plugin vs standalone skill

- **Plugins** bundle skills, agents, hooks, and MCP servers, and are **Claude Code only** — claude.ai and Claude for Microsoft 365 don't support the bundling mechanism
- **Standalone skills** are a lone `SKILL.md` directory and work on any surface, but can't ship MCP servers or hooks
- A capability needed on both has to exist in both places; there is no single artifact that covers all surfaces

## Important notes

- Plugins are distributed through git — publishing is `git push`, with no build step
- Archives (`dist/skills/`, `dist/plugins/`) exist for surfaces git can't reach, such as uploading a standalone skill to claude.ai
- The repo uses a simple zip packaging model for each standalone package
- New packages should be added under `skills/` or `plugins/` with the `nerdynik-` prefix
- CI lives in `.github/workflows/` and runs the same Makefile targets as the hook; its variables and secrets are documented in [`.github/workflows/README.md`](.github/workflows/README.md)
