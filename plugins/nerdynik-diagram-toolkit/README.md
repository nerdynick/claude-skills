# Diagram Toolkit

A Claude Code plugin for producing diagrams with **Mermaid** and **draw.io**, bundling both toolchains' MCP servers and the knowledge of which tool can actually do what.

**⚠️ Claude Code only.** Because this is a Claude Code *plugin* (`.claude-plugin/plugin.json`), skills here are only reachable from Claude Code — claude.ai and Claude for Microsoft 365 don't support this bundling mechanism, only standalone `SKILL.md` skills. A capability needed on those surfaces has to also exist as a standalone skill under `../../skills/`.

## Structure

```
nerdynik-diagram-toolkit/
  .claude-plugin/
    plugin.json                          # plugin manifest
  .mcp.json                              # the three bundled MCP servers
  references/                            # diagram-type guides, shared by both skills
    org-charts.md
    project-gantt-charts.md
  skills/
    nerdynik-mermaid-diagrams/           # Mermaid syntax, validation, theming, renderer differences
      references -> ../../references
    nerdynik-drawio-diagrams/            # .drawio XML, ELK layout, export, page editing, CSV, shapes
      references -> ../../references
```

`references/` is kept once at the plugin root and symlinked into each skill, so both skills reach it as a plain relative path (`references/org-charts.md`). Packaging dereferences the links, so an unzipped skill is self-contained. Edit the copy at the root.

## Bundled MCP servers

| Server | Transport | Key tools | Does |
|---|---|---|---|
| `mermaid` | Local, `npx -y mcp-mermaid` | `generate_mermaid_diagram` | Renders Mermaid to SVG/PNG — the validation step |
| `drawio` | Remote, `https://mcp.draw.io/mcp` | `create_diagram`, `search_shapes` | Inline preview; Mermaid → draw.io conversion |
| `drawio-local` | Local, `npx -y @drawio/mcp` | `list_pages`, `get_page`, `set_page`, `open_drawio_*`, `search_shapes` | Reads and writes local `.drawio` files a page at a time; opens diagrams in the editor |

The two local servers run through `npx` and need Node.js. `mermaid` also downloads a headless browser on first use to render with, which takes a moment. `drawio` is remote and needs no install.

## What can't be done without installing something

This is the part worth knowing before promising an output:

- **Nothing here creates a `.drawio` file.** `set_page` edits one that exists; the hosted `drawio` server persists nothing at all. New files come from your filesystem write tool.
- **Layout and export need [draw.io Desktop](https://github.com/jgraph/drawio-desktop/releases).** Its CLI is the only thing that runs an ELK auto-layout (`--layout verticalTree` and friends) or exports PNG/SVG/PDF. No MCP server substitutes for either. Without it you can still write correct XML, but coordinates have to be hand-placed and there is no image output.
- **`generate_mermaid_diagram`'s `file` output ignores your path** — it writes `mermaid-<timestamp>-<random>.png` into the server's working directory. Take the `svg` output and write it yourself if the location matters.
- **`svg_url` / `png_url` publish to `mermaid.ink`**, a third-party service, by encoding the diagram into the URL. Not for anything confidential.

## Relationship to draw.io's own plugin

draw.io publishes [its own Claude Code plugin](https://github.com/jgraph/drawio-mcp/tree/main/plugins/claude-code) wrapping the same desktop CLI:

```
/plugin marketplace add jgraph/drawio-mcp
/plugin install drawio@drawio
```

It's a reasonable alternative and worth knowing about. It isn't installed alongside this one by design: its skill triggers on *any* diagram request at all, so running both means two broad competing triggers spending the same shared skill-description budget. This plugin carries the CLI invocations directly instead — install the desktop app, not the plugin.

## Skills

| Skill | Use it for |
|---|---|
| `nerdynik-mermaid-diagrams` | Writing, fixing, validating, or theming Mermaid — flowcharts, sequence, class, state, ER, gantt, mindmap and the rest. The quoting and escaping rules that silently break a render, why `flowchart` beats `graph`, how clickable links differ on GitHub vs Obsidian vs an Artifact, and when the diagram has outgrown Mermaid. |
| `nerdynik-drawio-diagrams` | Producing and editing `.drawio` files — the mxGraphModel XML format and its silent failure modes, ELK layout presets, PNG/SVG/PDF export, page-level editing with `set_page`, CSV import, and when shape search is worth a call. |

## Diagram-type guides

Some diagrams are mostly domain judgment, not syntax. Both skills point at the same two guides for those:

| Guide | Covers |
|---|---|
| `references/org-charts.md` | Scope (requested people plus only the pass-through managers that connect them), verifying every reporting chain before drawing, dashed edges for unconfirmed lines, the shareable-vs-internal contact-details boundary, uniform cards and branch-only color, and the name-collision pass. Then how to draw one in each tool. |
| `references/project-gantt-charts.md` | The phase / milestone / story / task breakdown, who owns what (milestones don't), and the high-level vs. detailed split that decides how deep to go; marking estimates against baselined dates, showing the critical path, mapping from a tracker's fields, and Mermaid's `gantt` limits (no dependency arrows, no resource axis, no percent-complete) — which is what decides when to convert to draw.io. |

Add a guide when a diagram type turns out to need one; the skills' own tables route to them by what the user asked for.

## Choosing between them

The two skills cross-reference each other: Mermaid is the default for standard diagrams that live in a document, draw.io takes over when you need a file, precise control, real shape libraries, or an export. draw.io converts Mermaid directly, so moving between them doesn't waste the first attempt.

## Used by

[`nerdynik-obsidian-ps-toolkit`](../nerdynik-obsidian-ps-toolkit) declares this plugin as a dependency. Its org charts are maintained as a Mermaid diagram plus a `.drawio` / `.drawio.svg` pair, and it defers all the diagram mechanics here — keeping only the vault-specific decisions (what goes in a node, how Obsidian links resolve, where branding comes from) in its own reference.
