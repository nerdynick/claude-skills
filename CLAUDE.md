# CLAUDE.md

## Repository purpose
This repository is a collection of standalone AI skills and plugins. Each package must live in its own directory and use the `nerdynik-` prefix.

## Project structure
- `skills/` — standalone skills
- `plugins/` — standalone plugins
- `dist/` — generated package archives
- `Makefile` — build and packaging commands

## Package conventions
- Every skill and plugin directory must be prefixed with `nerdynik-`
- Each package should include a README describing its purpose and usage
- Keep package metadata in the package directory itself
- Update the repository README whenever a new package is added or renamed

## Build and packaging workflow
Use the following commands from the repository root:
- `make setup` — create packaging output directories
- `make package-skills` — build archives for all discovered skills
- `make package-plugins` — build archives for all discovered plugins
- `make package-all` — build both skill and plugin archives
- `make clean` — remove generated artifacts
- `make list` — show discovered skill and plugin packages

## Important notes
- Generated archives are written to `dist/skills/` and `dist/plugins/`
- The repo uses a simple tar.gz packaging model for each standalone package
- New packages should be added under `skills/` or `plugins/` with the `nerdynik-` prefix
