# Obsidian PS Toolkit

A Claude Code plugin: skills for working inside Obsidian vaults on Professional Services, C&SI, and SI engagements, plus MCP server references for pulling external data into the vault.

**⚠️ Claude Code only.** Because this is a Claude Code *plugin* (`.claude-plugin/plugin.json`), skills added here are only reachable from Claude Code — claude.ai and Claude for Microsoft 365 (Copilot Cowork) don't support this bundling mechanism, only standalone `SKILL.md` skills. If a skill built here needs to work from those surfaces too, it needs to also exist as a standalone skill under `../../skills/`, not live only in this plugin.

## Structure

```
nerdynik-obsidian-ps-toolkit/
  .claude-plugin/
    plugin.json                                  # plugin manifest
  .mcp.json                                       # bundled MCP server references
  skills/
    nerdynik-obsidian-vault-organization/         # client/project folder structure
    nerdynik-obsidian-project-manager-notes/      # reading Project Manager plan data
```

## Prerequisite: Desktop Commander

Every skill in this plugin assumes filesystem access to the vault via the **Desktop Commander** MCP plugin's own `obsidian-vault` skill, not a bespoke Obsidian API — a vault is just a folder of Markdown files, and Desktop Commander is how Claude Code reads/searches/edits them (`start_search`, `read_multiple_files`, `edit_block`, `write_file`, etc.).

Install it once, separately from this plugin:

```
/plugin marketplace add wonderwhy-er/DesktopCommanderMCP
/plugin install desktop-commander
```

The skills here build *on top of* Desktop Commander's `obsidian-vault` skill rather than duplicating it — that skill already owns wikilink mechanics, frontmatter/property conventions, MOCs, dashboards (Dataview/Bases), and orphan-note cleanup. In particular, it establishes a hard rule this plugin's skills also follow: **renames and moves of existing notes must happen inside the Obsidian app**, never via a raw filesystem `move_file`, because wikilinks resolve by filename and only Obsidian's own rename updates backlinks. Skills here only ever create *new* files/folders directly, and otherwise defer moves to the user or flag the backlink risk.

## MCP integrations

External data sources get wired in here as `.mcp.json` entries plus a short setup note, added one at a time as a real need arises (not sped up speculatively).

### Plaud (call transcripts & summaries)

[Plaud](https://www.plaud.ai/) devices/app record and transcribe calls, meetings, and discussions, with AI-generated summaries and notes. The bundled `.mcp.json` entry runs the official server (`@plaud-ai/mcp`), which reads a signed-in Plaud account read-only — no audio is uploaded or modified.

**One-time setup** (per machine, before Claude Code can use it):

1. `npx -y @plaud-ai/mcp@latest install` — opens a browser; click **Authorize**.
2. Fully restart Claude Code (not just the window) so it picks up the authorized session.
3. If you ever need to (re-)authenticate from inside a session, just ask: "Log me into Plaud."

Requires Node.js ≥ 20 and a Plaud account. Tools exposed: `login`, `logout`, `get_current_user`, `list_files`, `get_file`, `get_note`, `get_transcript`.

## Skills

| Skill | Use it for |
|---|---|
| `nerdynik-obsidian-vault-organization` | Setting up a new client/project space, deciding where a note belongs, auditing an existing vault's structure against the house convention. |
| `nerdynik-obsidian-project-manager-notes` | Reading/summarizing milestones, tasks, and subtasks written by the Obsidian **Project Manager** community plugin (`obsidian-pm`), and turning that plan data into status updates. |
