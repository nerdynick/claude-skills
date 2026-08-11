# claude-skills

A personal collection of Claude Skills and Plugins, distributed as a **Claude Code plugin marketplace**.

## Install

```
/plugin marketplace add nerdynick/claude-skills
/plugin install nerdynik-obsidian-ps-toolkit@nerdynik
```

The marketplace registers under the name `nerdynik`, so plugins install as `<plugin>@nerdynik`. Browse everything it offers with `/plugin`.

Update later with `/plugin marketplace update nerdynik`, then `/plugin update <plugin>@nerdynik`. Plugins pin a `version`, so a catalog refresh alone won't pull new code — the version has to change.

## Plugins

| Plugin | Description |
|---|---|
| [`nerdynik-obsidian-toolkit`](plugins/nerdynik-obsidian-toolkit) | General-purpose Obsidian vault skills, independent of any industry. Currently reading and reasoning over plan data written by the Obsidian Project Manager community plugin. |
| [`nerdynik-obsidian-ps-toolkit`](plugins/nerdynik-obsidian-ps-toolkit) | Obsidian vault structure for Professional Services / C&SI / SI engagements — customer/partner/practice taxonomy, tracking people across accounts, daily summaries from call recordings and calendar data. Depends on `nerdynik-obsidian-toolkit`; pairs with `nerdynik-plaud-toolkit`. |
| [`nerdynik-plaud-toolkit`](plugins/nerdynik-plaud-toolkit) | The Plaud MCP server plus a skill for interpreting what it returns — avoiding context-bomb calls, never quoting the paraphrased transcript, handling diarization that merges speakers, UTC-vs-local timestamps, and the proper-noun glossary loop. |
| [`nerdynik-task-management`](plugins/nerdynik-task-management) | Conventions for task lists that stay legible at scale — customer/project naming, labels as the cross-project axis for practices and partners, role-level saved views — plus an OKR structure across annual, quarterly, and monthly SMART horizons. Bundles the Vikunja MCP server, written to port to other trackers. |

Each plugin's README covers its own prerequisites — read it before installing.

## Standalone skills

None yet. Skills under [`skills/`](skills) are plain `SKILL.md` directories that work on any surface supporting Agent Skills — Claude Code, claude.ai, and Claude for Microsoft 365. Skills bundled inside a plugin are Claude Code only, so anything that needs to work on the other surfaces has to exist here too.

They aren't distributed through the marketplace; copy the directory into `~/.claude/skills/`, or build an archive with `make package-skills` and upload it.

## Development

```bash
make list       # discovered skills and plugins
make validate   # validate marketplace + plugin manifests
make package-all
make help
```

Test marketplace changes locally before pushing:

```
/plugin marketplace add ./path/to/claude-skills
```

Note that a local path and the GitHub source share the name `nerdynik`, and adding one replaces the other — run `/plugin marketplace remove nerdynik` and re-add from GitHub when you're done.

See [`CLAUDE.md`](CLAUDE.md) for repo conventions.

## License

[GPL-3.0-or-later](LICENSE)
