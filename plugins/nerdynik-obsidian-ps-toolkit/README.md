# Obsidian PS Toolkit

A Claude Code plugin: skills for working inside Obsidian vaults on Professional Services, C&SI, and SI engagements, plus MCP server references for pulling external data into the vault.

**⚠️ Claude Code only.** Because this is a Claude Code *plugin* (`.claude-plugin/plugin.json`), skills added here are only reachable from Claude Code — claude.ai and Claude for Microsoft 365 (Copilot Cowork) don't support this bundling mechanism, only standalone `SKILL.md` skills. If a skill built here needs to work from those surfaces too, it needs to also exist as a standalone skill under `../../skills/`, not live only in this plugin.

## Structure

```
nerdynik-obsidian-ps-toolkit/
  .claude-plugin/
    plugin.json                                  # plugin manifest
  skills/
    nerdynik-obsidian-vault-organization/         # vault taxonomy: customers, partners, people, daily summaries
      references/
        obsidian-mechanics.md                     # wikilinks, properties, MOCs, dashboards, link hygiene
        org-charts-and-relationships.md           # the people model + what the vault's org charts contain
        assets.md                                 # filing and indexing assets; renaming screenshots
        dsu-notes.md                              # full daily-standup spec: frontmatter, provenance, flags
        daily-summaries.md                        # full daily-summary spec and template
        customer-stories-and-blog.md              # customer stories, use cases, case studies, blog posts
        company-folder.md                         # the <Company Name>/ subfolders
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

What's needed is the **filesystem access** — `start_search`, `read_multiple_files`, `edit_block`, `write_file`. The Obsidian knowledge itself is carried here, in `references/obsidian-mechanics.md`: wikilink forms, frontmatter/property conventions, MOCs, Dataview and Bases dashboards, orphan and broken-link hygiene, and deduplication. That used to be deferred to Desktop Commander's own `obsidian-vault` skill; in practice that skill didn't reliably load alongside this one, so the vault skill is now self-contained.

The hard rule it carries: **renames and moves of existing notes must happen inside the Obsidian app**, never via a raw filesystem `move_file`, because wikilinks resolve by filename and only Obsidian's own rename updates backlinks. Skills here only ever create *new* files and folders directly, and otherwise defer moves to the user or flag the backlink risk.

## Diagrams: depends on Diagram Toolkit

This plugin bundles no MCP servers. Org charts are maintained in three forms — the entries in `Org Chart.md`, a Mermaid diagram inside that file, and `Org Chart.drawio` / `Org Chart.drawio.svg` beside it — and all of that tooling lives in [`nerdynik-diagram-toolkit`](../nerdynik-diagram-toolkit), a declared dependency that Claude Code installs automatically.

That plugin carries the `mermaid`, `drawio`, and `drawio-local` MCP servers plus two skills covering the mechanics: Mermaid syntax and validation, and the `.drawio` XML format, ELK layout, export, and page-level editing. The split is by scope — how to write valid Mermaid is true for anyone; deciding that a customer org chart node shows Full Name, Title, and Email and links to an Obsidian relationship page is not.

What stays here, in `references/org-charts-and-relationships.md`, is the vault-specific half: which artifact is authoritative, what a node contains, how `obsidian://` links are built and why a wikilink index has to sit under every chart, where branding comes from, and how the three artifacts are kept in sync.

Two constraints worth knowing before you expect a chart to appear:

- **New files come from Desktop Commander.** No MCP server creates a `.drawio` — `set_page` edits one that exists, and the hosted `drawio` server persists nothing at all.
- **[draw.io Desktop](https://github.com/jgraph/drawio-desktop/releases) is what exports `Org Chart.drawio.svg`**, and the only thing that can. It also provides the `verticalTree` layout that saves hand-placing an org chart's coordinates. Without it the skill writes the `.drawio`, says the export is outstanding, and doesn't embed a file that isn't there.

## Recording sources

The daily-summary workflow needs a source of call recordings, but deliberately doesn't mandate which one — it's written to work from whatever system the user records with, or from calendar data alone. No recording MCP server is bundled here.

For Plaud specifically, install [`nerdynik-plaud-toolkit`](../nerdynik-plaud-toolkit) alongside this plugin. It carries the Plaud MCP server and the skill for interpreting its output — the parts that matter for daily summaries being that the "polished" transcript paraphrases and must not be quoted, that diarization merges speakers into single turns, and that `created_at` is the *end* of a meeting rather than its start.

It's a soft pairing, not a declared dependency: recordings can come from anywhere, so forcing Plaud on someone who records elsewhere would be wrong.

## Skills

| Skill | Use it for |
|---|---|
| `nerdynik-obsidian-vault-organization` | Setting up a new customer/partner/project space, deciding where a note belongs, tracking people across the account, building and regenerating org charts as Mermaid and DrawIO, filing and indexing assets so binaries stay findable, writing customer stories and blog posts, recording townhalls and narratives, producing daily summaries from call recordings and calendar data, triaging web clippings, and auditing an existing vault against the house convention. |

Reading and summarizing Project Manager plan data now lives in `nerdynik-obsidian-project-manager-notes`, in the [Obsidian Toolkit](../nerdynik-obsidian-toolkit) plugin installed alongside this one.
