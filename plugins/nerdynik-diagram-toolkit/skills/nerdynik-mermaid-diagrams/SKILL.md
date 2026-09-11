---
name: nerdynik-mermaid-diagrams
description: >-
  Use when writing, fixing, validating, or styling a Mermaid diagram — flowchart, sequence, class,
  state, ER, gantt, mindmap, timeline, quadrant, C4, git graph, pie, journey — or when embedding one
  in Markdown for GitHub, GitLab, Obsidian, or an Artifact. Covers the mcp-mermaid MCP server's
  generate_mermaid_diagram tool and its outputType, theme, and backgroundColor options, the quoting
  and escaping rules that silently break a diagram, why flowchart beats graph, how clickable links
  behave differently on every renderer, theming with init directives and classDef, and when to stop
  and hand the diagram to draw.io instead. Bundles guides for org charts and project-schedule Gantt
  charts. Trigger on "mermaid", "mermaid syntax", "flowchart", "sequence diagram", "ER diagram",
  "gantt chart", "project schedule", "roadmap", "org chart", "reporting structure", "mindmap", "my
  diagram won't render".
---

# Mermaid Diagrams

Mermaid is text that renders to a diagram. Its value is that the source stays in the document —
diffable, editable, reviewable — so **the source is the artifact**, not the image. Reach for it
first for any standard diagram type. Reach for draw.io instead when you need a file, precise
placement, or industry shape libraries; see [[nerdynik-drawio-diagrams]].

## Diagram-type guides

Some diagram types have enough domain rules of their own that the syntax is the easy part. When the
request is one of these, **read its guide before drawing** — they cover what belongs in the diagram
and how to be sure it's right, then the tool specifics:

| Asked for | Read |
|---|---|
| Org chart, reporting structure, stakeholder map, who-reports-to-whom | `references/org-charts.md` |
| Gantt, project schedule, delivery plan, roadmap, timeline | `references/project-gantt-charts.md` |

## Always validate before you ship

A malformed Mermaid block doesn't error usefully — most renderers show a broken box or nothing at
all, and the person who finds out is the reader, not you. So never write a Mermaid block into a
file or a message without rendering it first.

The bundled `mermaid` MCP server does this:

```
generate_mermaid_diagram(mermaid: "<source>", outputType: "svg")
```

| `outputType` | Returns |
|---|---|
| `base64` *(default)* | PNG as an inline image |
| `svg` | SVG markup as text — **best for validation**, you can read what came back |
| `mermaid` | The input echoed back, unchanged |
| `file` | Writes a PNG and returns its path — see the caveat below |
| `svg_url` / `png_url` | A public `mermaid.ink` link |

Also takes `theme` (`default`, `base`, `forest`, `dark`, `neutral`) and `backgroundColor`.

Two traps:

- **`outputType: "file"` doesn't take a path.** It writes `mermaid-<timestamp>-<random>.png` into
  the server's current working directory and returns the location. You cannot choose the name or
  the folder. To put an image somewhere specific, take the `svg` output and write it yourself.
- **`svg_url` / `png_url` publish the diagram to a third-party service** (`mermaid.ink`) by
  encoding it into the URL. Never use them for anything confidential.

Validate again after every edit, not just the first time. Most breakage arrives with a later change
— a new label containing a character that needed escaping.

## Syntax rules that actually bite

Most "my diagram won't render" reports are one of these:

- **Quote every label.** `A[VP, Sales]` breaks on the comma; `A["VP, Sales"]` is fine. Quote by
  default and you never have to think about which characters are special — `(` `)` `[` `]` `{` `}`
  `,` `:` `;` and `-` all cause trouble unquoted.
- **Escape what Mermaid eats**, even inside quotes: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`,
  `"` → `&quot;`. An ampersand in a label — "Sales & Marketing" — is the single most common break.
- **Line breaks are `<br>`**, not `\n`. `A["Line one<br>Line two"]`.
- **Node ids must not collide with keywords.** `end`, `graph`, `subgraph`, `class`, `click`,
  `style` as a bare id will break or silently misparse. Lowercase `end` inside a flowchart is a
  notorious one — use `end_node` or capitalise it.
- **`%%` starts a comment** and must be on its own line.
- **Indentation is not syntax**, but a stray tab inside a label is preserved and looks wrong.

## `flowchart`, not `graph`

`graph TD` is the legacy keyword. `flowchart TD` is the current one, gets the better renderer, and
is what interactive features are tested against — notably, click handling is reliable on
`flowchart` and flaky on `graph`. Use `flowchart` for every new diagram.

Directions: `TD`/`TB` (top-down), `BT`, `LR` (left-right), `RL`. Prefer `LR` when labels are long
— boxes get wide, and wide boxes stack badly top-down.

## Picking the diagram type

| Want to show | Use |
|---|---|
| Steps, decisions, control flow | `flowchart` |
| Who calls whom, in what order | `sequenceDiagram` |
| Data model, entities, cardinality | `erDiagram` |
| Types, inheritance, fields | `classDiagram` |
| States and transitions | `stateDiagram-v2` |
| Schedule, phases, dependencies | `gantt` — see `references/project-gantt-charts.md` |
| Hierarchy of ideas | `mindmap` |
| Reporting structure | `flowchart` — see `references/org-charts.md` |
| Dated events in order | `timeline` |
| System context and containers | `C4Context`, `C4Container` |
| Branches and merges | `gitGraph` |

Don't force a flowchart to be a sequence diagram. A flowchart with lifeline-shaped columns is
harder to read than the `sequenceDiagram` that was built for it.

## Links, and why they behave differently everywhere

Two mechanisms, and which one works depends entirely on the renderer:

```
click nodeId "https://example.com" "Optional tooltip"
click nodeId call someCallback()
```

| Renderer | Link behavior |
|---|---|
| **GitHub / GitLab** | `click` is **stripped**. Diagrams are rendered in a sandbox; no links, no callbacks. Don't rely on them. |
| **Obsidian** | `click` with a URL works on `flowchart`, unreliably on `graph`. Internal notes need an `obsidian://open?vault=<Vault>&file=<url-encoded-path>` URI. |
| **Artifacts / own page** | Works, subject to the page's `securityLevel`; `strict` disables click handling entirely. |
| **mermaid.ink** (`*_url`) | Static image. No links at all. |

Obsidian also offers `class nodeId internal-link`, which is native and reliable — but it resolves
the link target from the node's **label text**, which must therefore equal the note name exactly.
That rules it out for any node whose label carries extra lines. Use `click` when the label is more
than a bare name.

**Links inside a Mermaid diagram are invisible to the document's own link graph.** Obsidian
backlinks, GitHub's cross-references, and wiki graph views all ignore them. If the links matter for
navigation, repeat them as plain links beneath the diagram.

## Theming

Three levels, least to most invasive:

1. **`theme`** on the MCP call, or `%%{init: {"theme": "base"}}%%` as the first line of the source.
   `base` is the only one that responds fully to customization; the others largely ignore overrides.
2. **`themeVariables`** for brand colors:
   ```
   %%{init: {"theme":"base","themeVariables":{"primaryColor":"#1F3A5F","lineColor":"#888"}}}%%
   ```
3. **`classDef` + `class`** for per-node styling, which is the portable option and survives
   renderers that strip `init` directives:
   ```
   classDef exec fill:#1F3A5F,stroke:#0D1B2A,color:#FFF
   class jane_doe,marcus_webb exec
   ```

Prefer `classDef`. An `init` directive is a single point of failure — one renderer ignoring it
takes the entire look with it.

**Don't hard-code colors that only work on one background.** Diagrams get read in dark mode. Either
set both foreground and background explicitly on every styled node, or style nothing and let the
renderer's theme handle it.

## Keep it readable

A diagram stops earning its keep well before it stops rendering:

- **Past ~25 nodes**, split it. One overview showing groups, then one diagram per group.
- **Use `subgraph`** to group related nodes rather than relying on layout luck.
- **Put detail in node labels, not in more edges.** Edges are the expensive layer — every one
  added is another line to trace.
- **Don't fight the layout engine.** Mermaid places nodes automatically and you cannot set
  coordinates. If the arrangement is genuinely wrong, that's the signal to move to draw.io, not to
  add invisible spacer nodes.

## When to hand off to draw.io

Mermaid is the wrong tool when you need:

- A **file artifact** — `.drawio`, `.svg`, `.png`, `.pdf` — that someone edits in an editor
- **Precise placement**, or a layout Mermaid's engine won't produce
- **Industry shape libraries** — AWS, Azure, GCP, Cisco, Kubernetes, BPMN, P&ID, electrical
- **Multi-page** diagrams
- Per-shape **metadata** carried with the diagram

draw.io converts Mermaid directly, so the Mermaid source is a good starting point rather than
wasted work. See [[nerdynik-drawio-diagrams]].
