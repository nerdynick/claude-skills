# Obsidian Toolkit

A Claude Code plugin: general-purpose skills for working inside an Obsidian vault, independent of any particular industry or line of work.

**⚠️ Claude Code only.** Because this is a Claude Code *plugin* (`.claude-plugin/plugin.json`), the skills here are only reachable from Claude Code — claude.ai and Claude for Microsoft 365 (Copilot Cowork) support standalone `SKILL.md` skills only.

```
/plugin install nerdynik-obsidian-toolkit@nerdynik
```

## Scope

This plugin holds vault skills that are true for **any** Obsidian user: how a community plugin stores its data, how to parse a particular frontmatter shape, how to work with a vault convention that isn't tied to a domain.

Anything specific to a line of business belongs elsewhere. Professional Services / C&SI / SI vault structure — customers, partners, practices, account teams, daily summaries — lives in [`nerdynik-obsidian-ps-toolkit`](../nerdynik-obsidian-ps-toolkit), which depends on this plugin.

## Structure

```
nerdynik-obsidian-toolkit/
  .claude-plugin/
    plugin.json
  skills/
    nerdynik-obsidian-project-manager-notes/     # reading Project Manager plan data
```

## Prerequisite: Desktop Commander

The skills here assume filesystem access to the vault through the **Desktop Commander** MCP plugin's own `obsidian-vault` skill, not a bespoke Obsidian API — a vault is just a folder of Markdown files, and Desktop Commander is how Claude Code reads, searches, and edits them (`start_search`, `read_multiple_files`, `edit_block`, `write_file`).

Install it once, separately:

```
/plugin marketplace add wonderwhy-er/DesktopCommanderMCP
/plugin install desktop-commander
```

That skill already owns wikilink mechanics, frontmatter and property conventions, MOCs, dashboards, and orphan-note cleanup, along with a hard rule the skills here follow: **renames and moves of existing notes must happen inside the Obsidian app**, never through a raw filesystem call, because wikilinks resolve by filename and only Obsidian's own rename updates backlinks.

## Skills

| Skill | Use it for |
|---|---|
| `nerdynik-obsidian-project-manager-notes` | Reading, summarizing, and reporting on plans written by the Obsidian **Project Manager** community plugin (`obsidian-pm`) — milestones, tasks, subtasks, dependencies, status, priority. Status reports, "what's overdue or blocked," milestone tracking, and non-destructive edits to plan frontmatter. |

The Project Manager skill documents a storage layout and frontmatter schema confirmed against a live vault rather than read off the plugin's docs, including where the real data diverges from what's documented. It carries its own drift warning: when a vault disagrees with the schema, trust the files.
