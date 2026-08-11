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
    nerdynik-obsidian-vault-organization/         # vault taxonomy: customers, partners, people, daily summaries
      references/
        daily-summaries.md                        # full daily-summary spec and template
```

## Depends on: Obsidian Toolkit

This plugin declares a dependency on [`nerdynik-obsidian-toolkit`](../nerdynik-obsidian-toolkit), which Claude Code installs automatically alongside it.

That plugin holds the general-purpose Obsidian skills — currently `nerdynik-obsidian-project-manager-notes`, which reads plan data written by the Obsidian **Project Manager** community plugin. The PS taxonomy here integrates with that store directly: vault-root `Projects/` is Project Manager's own folder, and this plugin's skills wikilink to that skill for its file format.

The split is by scope. Understanding how a community plugin serializes its data is true for any Obsidian user; the customer/partner/practice taxonomy is not.

## Prerequisite: Desktop Commander

Every skill in this plugin assumes filesystem access to the vault via the **Desktop Commander** MCP plugin's own `obsidian-vault` skill, not a bespoke Obsidian API — a vault is just a folder of Markdown files, and Desktop Commander is how Claude Code reads/searches/edits them (`start_search`, `read_multiple_files`, `edit_block`, `write_file`, etc.).

Install it once, separately from this plugin:

```
/plugin marketplace add wonderwhy-er/DesktopCommanderMCP
/plugin install desktop-commander
```

The skills here build *on top of* Desktop Commander's `obsidian-vault` skill rather than duplicating it — that skill already owns wikilink mechanics, frontmatter/property conventions, MOCs, dashboards (Dataview/Bases), and orphan-note cleanup. In particular, it establishes a hard rule this plugin's skills also follow: **renames and moves of existing notes must happen inside the Obsidian app**, never via a raw filesystem `move_file`, because wikilinks resolve by filename and only Obsidian's own rename updates backlinks. Skills here only ever create *new* files/folders directly, and otherwise defer moves to the user or flag the backlink risk.

## Recording sources

This plugin bundles no MCP servers. The daily-summary workflow needs a source of call recordings, but deliberately doesn't mandate which one — it's written to work from whatever system the user records with, or from calendar data alone.

For Plaud specifically, install [`nerdynik-plaud-toolkit`](../nerdynik-plaud-toolkit) alongside this plugin. It carries the Plaud MCP server and the skill for interpreting its output — the parts that matter for daily summaries being that the "polished" transcript paraphrases and must not be quoted, that diarization merges speakers into single turns, and that `created_at` is the *end* of a meeting rather than its start.

It's a soft pairing, not a declared dependency: recordings can come from anywhere, so forcing Plaud on someone who records elsewhere would be wrong.

## Skills

| Skill | Use it for |
|---|---|
| `nerdynik-obsidian-vault-organization` | Setting up a new customer/partner/project space, deciding where a note belongs, tracking people across the account, recording townhalls and narratives, producing daily summaries from call recordings and calendar data, triaging web clippings, and auditing an existing vault against the house convention. |

Reading and summarizing Project Manager plan data now lives in `nerdynik-obsidian-project-manager-notes`, in the [Obsidian Toolkit](../nerdynik-obsidian-toolkit) plugin installed alongside this one.
