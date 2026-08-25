# CLAUDE.md

## Repository purpose
This repository is a Claude Code **plugin marketplace** plus a collection of standalone skills. Each package must live in its own directory and use the `nerdynik-` prefix.

## Project structure
- `.claude-plugin/marketplace.json` — the marketplace catalog; every plugin must be registered here
- `skills/` — standalone skills
- `plugins/` — standalone plugins
- `dist/` — generated package archives (gitignored)
- `Makefile` — build, validation, and packaging commands

## Package conventions
- Every skill and plugin directory must be prefixed with `nerdynik-`
- The directory name must match the `name` field in the package manifest
- Each package should include a README describing its purpose and usage
- Keep package metadata in the package directory itself
- Package manifests declare `"license": "GPL-3.0-or-later"`

## Skill frontmatter rules (`SKILL.md`)

Frontmatter is what makes a skill *findable*. Every rule below has a silent failure mode — a
broken or oversized skill throws no error, it just never fires. `claude plugin validate` catches
only a subset (noted per rule), so these are enforced by review, not tooling.

### Recognized fields

| Field | Type | Constraints |
|---|---|---|
| `name` | string | lowercase letters, digits, hyphens only; **≤64 chars**; must equal the directory name for a standalone skill |
| `description` | string | **≤1024 characters — hard limit** |
| `allowed-tools` / `disallowed-tools` | string or array of strings | array entries must all be strings |
| `shell` | string | exactly `bash` or `powershell`; nothing else |
| `argument-hint`, `when_to_use`, `disable-model-invocation`, `user-invocable`, `hooks` | — | recognized by the loader |

Unrecognized keys are **ignored, not rejected** — a typo'd key fails silently and forever.

`name` is technically optional, but omit it and Claude Code falls back to the install directory
name, which for a marketplace install is a **version string that changes on every update**. Always
set it explicitly.

### `description` must be ≤1024 characters

The hard per-skill cap. **Nothing in `make validate` or `claude plugin validate` checks it** — the
limit surfaces as an alert on the surfaces that load the skill, so a regression ships clean.
Measure it, don't eyeball it:

```bash
ruby -ryaml -e 'Dir.glob("**/SKILL.md").each{|f|
  y=YAML.safe_load(File.read(f).match(/\A---\n(.*?)\n---\n/m)[1]) rescue (puts "PARSE FAIL #{f}"; next)
  d=y["description"].to_s; puts format("%-4s %5d  %s", d.length>1024 ? "FAIL" : "ok", d.length, f)}'
```

When trimming to fit, cut redundant near-duplicate trigger phrases first — `"case study"` already
covers `"case studies"`, and plural/singular pairs are pure overhead. Cut prose that restates the
skill body second. Keep the distinct trigger vocabulary.

### Always write `description` as a folded block scalar (`>-`)

A long unquoted one-line `description:` is a plain YAML scalar, and it breaks the moment the text
contains `: ` (colon-space) or ` #`. That is a *parse* failure, and the consequence is severe:

> YAML frontmatter failed to parse … At runtime this skill loads with empty metadata
> (**all frontmatter fields silently dropped**).

No name, no description, no routing — the skill is invisible. This has already happened for real
in a sibling skills repo, where a description reading `…the three content types: general company
pages` silently disabled the skill it belonged to.

Use a folded block scalar for every description, wrapped at ~92 columns with a 2-space indent.
Inside a block scalar, colons and `#` are literal text, so the failure mode disappears:

```yaml
---
name: my-skill
description: >-
  Does the thing. Use when the user wants the thing, including cases like this: a colon here
  is safe because a folded scalar takes everything literally and joins these lines with single
  spaces. Trigger on "the thing", "do the thing".
---
```

`claude plugin validate <plugin-dir>` **does** catch a parse failure — but it reports the plugin,
not the file. Bisect with the ruby snippet above. Note it will not accept a path to a nested skill
directory or a `SKILL.md` directly; point it at the plugin root.

### Descriptions share one context budget

Every loaded skill's description sits in the prompt together, against a **combined budget**. Over
budget, Claude Code degrades — truncating descriptions, dropping them for less-used skills, or
falling back to names-only — and warns `Skill listing over budget: N skills, X chars > Y budget`.

So a bloated description isn't just that skill's problem; it costs every other skill's
discoverability. Treat 1024 as the ceiling, not the target. `/skill-doctor` shows which loaded
skills are unused and burning context.

### `description` is routing copy, not catalogue copy

Two different descriptions exist for a package and they must not be interchanged:

- **`SKILL.md` `description:`** — written for the *model*. Third person, dense with trigger words
  and phrases someone would actually type. States what the skill does *and* when to reach for it.
  Long and specific beats elegant.
- **`marketplace.json` `description`** — short human catalogue copy, one sentence.

Don't paste one into the other.

### What the validator does and does not check

**Checks:** frontmatter block present; YAML parses; frontmatter is a mapping (not a list or
scalar); `description` is a string; `name` is a string; `allowed-tools` is a string or array of
strings; `shell` is `bash` or `powershell`.

**Does not check:** the 1024-character limit, the combined budget, `name` ≤64 chars, `name`
matching the directory, or whether the description is any good. Those stay human — see the TODO
in the `claude-marketplace` repo for folding them into a validation action.

## Marketplace
- The marketplace is named `nerdynik`; users install with `/plugin install <plugin>@nerdynik`
- Plugin `source` values are paths relative to the repository root and must start with `./`, e.g. `./plugins/nerdynik-<name>`
- Standalone skills are **not** listed in `marketplace.json` — that mechanism is plugin-only
- Bump a plugin's `version` in `.claude-plugin/plugin.json` on every published change; the version pins the plugin, so users get new code only when it changes
- Run `make validate` after touching any manifest. Note that validation does **not** check that a `source` path exists — that failure only surfaces at install time
- Renaming an already-published plugin breaks existing installs unless a `renames` entry is added to `marketplace.json`

## Sharing files between skills in one plugin
- Do **not** use `${CLAUDE_PLUGIN_ROOT}` in skill content to reach bundled files. It isn't substituted on every surface that loads skills — Claude Desktop leaves it literal, and the read fails.
- Instead keep one copy at the plugin root (e.g. `references/`) and symlink it into each skill directory: `ln -s ../../references skills/<skill>/references`. The skill then uses a plain relative path, `references/vikunja.md`.
- This works because a symlink resolving *within* the plugin's own directory is preserved as a relative symlink in the plugin cache. Symlinks pointing outside the plugin are dereferenced or skipped.
- Edit the shared copy only; the skill-directory entries are links. `make package-plugins` dereferences them into real files in the archive, so an unzipped skill is self-contained.

## Naming: `nerdynik` vs `nerdynick`
Both spellings are intentional. The package prefix and marketplace name use `nerdynik`; anything pointing at GitHub (clone URLs, `owner/repo` shorthand, profile links) uses the account name `nerdynick`. Do not normalize one to the other.

## When adding or renaming a package, update
1. `.claude-plugin/marketplace.json` (plugins only)
2. The repository `README.md`

The `Makefile` discovers packages by glob, so it needs no change.

## Plugin vs standalone skill
- **Plugins** bundle skills, agents, hooks, and MCP servers, and are **Claude Code only** — claude.ai and Claude for Microsoft 365 don't support the bundling mechanism
- **Standalone skills** are a lone `SKILL.md` directory and work on any surface, but can't ship MCP servers or hooks
- A capability needed on both has to exist in both places; there is no single artifact that covers all surfaces

## Build and packaging workflow
Use the following commands from the repository root:
- `make list` — show discovered skill and plugin packages
- `make validate` — validate the marketplace and every plugin manifest (`--strict`)
- `make setup` — create packaging output directories
- `make package-skills` — build archives for all discovered skills
- `make package-plugins` — build archives for all discovered plugins
- `make package-all` — build both skill and plugin archives
- `make clean` — remove generated artifacts

## Important notes
- Plugins are distributed through git — publishing is `git push`, with no build step
- Archives (`dist/skills/`, `dist/plugins/`) exist for surfaces git can't reach, such as uploading a standalone skill to claude.ai
- The repo uses a simple zip packaging model for each standalone package
- New packages should be added under `skills/` or `plugins/` with the `nerdynik-` prefix
