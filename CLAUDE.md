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

## Marketplace
- The marketplace is named `nerdynik`; users install with `/plugin install <plugin>@nerdynik`
- Plugin `source` values are paths relative to the repository root and must start with `./`, e.g. `./plugins/nerdynik-<name>`
- Standalone skills are **not** listed in `marketplace.json` — that mechanism is plugin-only
- Bump a plugin's `version` in `.claude-plugin/plugin.json` on every published change; the version pins the plugin, so users get new code only when it changes
- Run `make validate` after touching any manifest. Note that validation does **not** check that a `source` path exists — that failure only surfaces at install time
- Renaming an already-published plugin breaks existing installs unless a `renames` entry is added to `marketplace.json`

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
