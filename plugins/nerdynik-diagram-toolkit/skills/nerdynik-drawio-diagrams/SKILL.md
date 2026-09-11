---
name: nerdynik-drawio-diagrams
description: >-
  Use when creating, editing, laying out, or exporting a draw.io / diagrams.net diagram, working
  with .drawio or mxGraphModel XML, or building an architecture, network, cloud, BPMN, P&ID, or org
  chart diagram that needs real shape libraries. Covers the four draw.io integrations and which one
  can actually write a file — the hosted MCP app server previews only, the local @drawio/mcp server
  reads and writes .drawio files a page at a time via list_pages, get_page, and set_page, and only
  the draw.io Desktop CLI can auto-layout with ELK or export PNG, SVG, and PDF. Also the XML format,
  escaping rules, style strings, CSV import, shape search, and a troubleshooting table for diagrams
  that render blank or export corrupt. Bundles guides for org charts and project-schedule Gantt
  charts. Trigger on "draw.io", "drawio", "diagrams.net", ".drawio file", "mxgraph", "org chart",
  "reporting structure", "export diagram to SVG or PNG".
---

# Draw.io Diagrams

A `.drawio` file is mxGraphModel XML. Everything below is about producing that XML, getting it laid
out, and turning it into the format someone asked for.

Prefer [[nerdynik-mermaid-diagrams]] when the diagram is a standard type and lives in a document —
Mermaid source in Markdown beats a binary-ish file nobody can diff. Come here when you need a file,
precise control, real shape libraries, or an export.

## Diagram-type guides

Some diagram types have enough domain rules of their own that the syntax is the easy part. When the
request is one of these, **read its guide before drawing** — they cover what belongs in the diagram
and how to be sure it's right, then the tool specifics:

| Asked for | Read |
|---|---|
| Org chart, reporting structure, stakeholder map, who-reports-to-whom | `references/org-charts.md` |
| Gantt, project schedule, delivery plan, roadmap, timeline | `references/project-gantt-charts.md` |

Both guides cover Mermaid and draw.io, and say which tool the job actually wants — for a Gantt
that's usually Mermaid first, converted.

## Know which tool can do what

Four draw.io integrations exist and they are **not** interchangeable. Establish what's available
before planning the work, because the answer changes the whole approach.

| Capability | Tool | Fallback |
|---|---|---|
| Preview a diagram inline in chat | `drawio` (hosted) `create_diagram` | `drawio-local` `open_drawio_xml` — opens a browser tab |
| Convert Mermaid → draw.io | `create_diagram` with `mermaid`, or the CLI | author the XML yourself |
| Open in the full editor | `drawio-local` `open_drawio_xml` / `_csv` / `_mermaid` | build an `app.diagrams.net/#create=` URL |
| Find a shape's style string | `search_shapes` (either server) | use basic shapes |
| **Create a `.drawio` file** | your filesystem write tool | — nothing else creates one |
| **Edit one page in place** | `drawio-local` `set_page` | rewrite the whole file |
| **Read a page back** | `drawio-local` `get_page`, `list_pages` | read and parse the file |
| **Auto-layout** | draw.io Desktop CLI `--layout` | hand-place every coordinate |
| **Export PNG / SVG / PDF** | draw.io Desktop CLI | **no substitute** |

The two things with no MCP substitute are **layout** and **export** — both need draw.io Desktop
installed locally. Without it you can still write correct XML, but you must compute coordinates
yourself and you cannot produce an image at all. Say so rather than promising an export that won't
appear.

Neither MCP server creates a file. The hosted one persists nothing whatsoever; the local one's
`set_page` edits a `.drawio` that already exists.

## The pipeline

Author → `.drawio` → (layout) → deliver. The delivery step is identical regardless of how you
authored, which is why it's worth always landing on a `.drawio` first.

### 1. Author

**As Mermaid** — preferred for standard types when the desktop CLI is present, because draw.io's
Mermaid parser lays the diagram out for you:

```bash
drawio -x -f xml -o diagram.drawio diagram.mmd
```

Delete the `.mmd` afterward; the `.drawio` is the artifact. Don't add `--layout` — it's already
laid out. And never export a `.mmd` straight to an image: direct Mermaid → PNG with `-e` crashes
in current draw.io Desktop. Always convert first, then export the `.drawio`.

**As XML** — for precise control, specific shape libraries, or when there's no CLI at all. Write
the graph *structure* correctly and keep coordinates rough; the layout pass replaces them.

### 2. Lay out (XML only, needs the CLI)

Don't compute positions. Emit nodes at approximate — or even zero — coordinates and let ELK place
them:

```bash
drawio -x -f xml --layout verticalFlow -o diagram.drawio diagram.drawio
```

Reading and overwriting the same path is supported.

| Preset | Layout |
|---|---|
| `verticalFlow` | Layered top-to-bottom — flowcharts, pipelines |
| `horizontalFlow` | Layered left-to-right |
| `verticalTree` | Tree top-down — **hierarchies, org charts** |
| `horizontalTree` | Tree left-to-right |
| `radialTree` | Radial tree |
| `organic` | Force-directed — networks, mind-map-like graphs |
| `libavoid` | Reroutes **edges** orthogonally around shapes without moving any node |

`--layout libavoid` is the complement of the others: use it on hand-positioned XML whose connectors
cross shapes. Skip it after a flow or tree preset — those already route their edges.

For finer control, pass a JSON array instead of a preset name:

```bash
drawio -x -f xml --layout '[{"layout":"elkLayered","config":{"elk.direction":"RIGHT"}}]' -o d.drawio d.drawio
```

Algorithms: `elkLayered`, `elkTree`, `elkRadial`, `elkOrganic`, `elkStress`, `elkBox`. Config keys
starting with `elk.` are ELK options (`elk.direction`, `elk.spacing.nodeNode`); `edgeStyle` and
`corners` control connector rendering.

### 3. Deliver

| Want | Do |
|---|---|
| `.drawio` | Nothing — it's already the artifact |
| PNG / SVG / PDF | `drawio -x -f svg -e -b 10 -o diagram.drawio.svg diagram.drawio` |
| Browser URL | Deflate-raw the XML, base64 it, open `https://app.diagrams.net/#create=…` |

`-e` embeds the diagram XML in the exported file so it stays editable in draw.io; `-b 10` adds a
10px border. The `.drawio.*` double extension signals embedded XML.

**Decide deliberately whether to keep the source `.drawio` after an export.** draw.io's own pipeline
deletes it, since the export contains the full diagram. Keep it when the file is version-controlled
— plain XML diffs, an exported SVG effectively doesn't.

### Locating the CLI

Detect once; don't assume. Try `which drawio` first, then:

| Platform | Path |
|---|---|
| macOS | `/Applications/draw.io.app/Contents/MacOS/draw.io` |
| Linux | `drawio` on PATH (snap/apt/flatpak) |
| Windows | `"C:\Program Files\draw.io\draw.io.exe"` |
| WSL2 — `/proc/version` contains `microsoft` | `"/mnt/c/Program Files/draw.io/draw.io.exe"` |

Detect WSL2 with `grep -qi microsoft /proc/version`. Double-quote Windows paths for the space in
`Program Files`; **never backtick them** — in bash that executes the binary instead of storing its
path.

## Editing an existing file

Don't rewrite a whole diagram to change one box. `drawio-local` addresses pages individually —
by zero-based index, exact name, or id:

| Tool | Parameters | Result |
|---|---|---|
| `list_pages` | `path` | `[{index, id, name, approxSizeBytes}]` |
| `get_page` | `path`, `page` | That page's `mxGraphModel` XML |
| `set_page` | `path`, `page`, `content` | Replaces that page's `<mxGraphModel>`; every other page untouched |

Paths must end in `.drawio` or `.xml`. Compression is handled transparently, so a compressed file
round-trips without special handling.

`list_pages` → `get_page` → patch → `set_page` is the correct edit loop. **Re-run layout and
re-export afterward**, or the file is laid out wrong and any exported image is stale.

Multi-page files are worth building deliberately — one `<diagram>` per subsystem, division, or
environment — precisely because `set_page` then scopes each change to one page.

## The XML

```xml
<mxfile host="app.diagrams.net">
  <diagram id="page1" name="Overview">
    <mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" page="1" adaptiveColors="auto">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="svc" value="Auth Service" style="rounded=1;whiteSpace=wrap;html=1;"
                vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="140" height="60" as="geometry" />
        </mxCell>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;"
                edge="1" parent="1" source="svc" target="db">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Non-negotiables:

- `<mxCell id="0">` and `<mxCell id="1" parent="0">` must both be present. Everything else parents
  to `1` (or to a container).
- **Every edge needs `<mxGeometry relative="1" as="geometry" />` as a child.** A self-closing edge
  cell does not render. This is the most common silent failure.
- **Unique `id` on every cell.**
- **No XML comments.** `<!-- -->` is not tolerated in diagram XML.
- Escape attribute values: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`.

### Labels

Put `html=1` in **every** style string — it's harmless on plain text and required the moment a
label contains a tag. HTML inside an XML attribute is escaped twice, so `<br>` is written
`&lt;br&gt;`:

```xml
<mxCell value="&lt;b&gt;Title&lt;/b&gt;&lt;br&gt;Description" style="rounded=1;whiteSpace=wrap;html=1;" .../>
```

Line breaks are `&#xa;` or `&lt;br&gt;` — **never `\n`**, which renders as literal backslash-n.

For a whole-label style use `fontStyle` in the style string (`1` bold, `2` italic, `4` underline,
bitwise-OR to combine). Use `<b>` / `<i>` tags only to style *part* of a label. Never both for the
same effect.

### Common style properties

`rounded=1` · `whiteSpace=wrap` · `fillColor=#dae8fc` · `strokeColor=#6c8ebf` · `fontColor=#333333`
· `dashed=1` · `ellipse` · `rhombus` (decision) · `shape=cylinder3` (database) · `swimlane` ·
`group` · `container=1` · `pointerEvents=0` · `edgeStyle=orthogonalEdgeStyle` ·
`edgeStyle=elbowEdgeStyle`

### Links and metadata

A bare `<mxCell>` can't carry a hyperlink or custom properties. Wrap it:

```xml
<UserObject id="svc" label="Auth Service" link="https://wiki.example/auth">
  <mxCell style="rounded=1;html=1;" vertex="1" parent="1">
    <mxGeometry width="140" height="60" as="geometry" />
  </mxCell>
</UserObject>
```

`<object>` does the same for structured data, and with `placeholders="1"` the custom attributes
substitute into the label:

```xml
<object id="svc" label="&lt;b&gt;%component%&lt;/b&gt;&lt;br&gt;Owner: %owner%"
        placeholders="1" component="Auth Service" owner="Team Backend">
  <mxCell style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
    <mxGeometry width="160" height="80" as="geometry" />
  </mxCell>
</object>
```

Built-in placeholders — `%id%`, `%date%`, `%filename%`, `%page%` — need no custom attributes. `%%`
is a literal percent.

### Dark mode

`strokeColor`, `fillColor`, and `fontColor` default to `"default"`, which renders black on light
and white on dark — so **setting no color is the most theme-safe choice**. An explicit color is
treated as the light-mode value and auto-inverted for dark. Override that with
`fontColor=light-dark(#7EA6E0,#FF0000)`. Set `adaptiveColors="auto"` on `mxGraphModel` to enable it.

## Shape libraries

`search_shapes(query, limit)` searches ~10,000 shapes and returns ready-to-use style strings.

**Use it for:** cloud architecture (AWS, Azure, GCP), network topology (Cisco, racks), Kubernetes,
BPMN task types, P&ID, electrical, and brand or concept icons (`react`, `slack`, `shopping cart`).

**Skip it for:** flowcharts, UML, ERD, org charts, mind maps, timelines, wireframes — anything built
from rectangles, diamonds, circles, cylinders, and arrows. Searching for those wastes a call and
returns worse shapes than the primitives.

## CSV import

draw.io's CSV importer builds a whole diagram from tabular data, which is often less work than XML
for anything that's really a table with a parent column — org charts, dependency trees, inventories:

```
# label: %name%<br><b>%role%</b>
# style: rounded=1;html=1;whiteSpace=wrap;fillColor=%fill%;
# connect: {"from":"manager","to":"id","invert":true,"style":"edgeStyle=orthogonalEdgeStyle;"}
# layout: verticaltree
id,name,role,manager,fill
1,Jane Doe,CTO,,#dae8fc
2,Ravi Patel,Director,1,#ffffff
```

`# connect` turns a parent column into edges; `# layout` accepts `auto`, `none`, `verticalflow`,
`horizontalflow`, `verticaltree`, `horizontaltree`, `organic`, `circle`.

`open_drawio_csv` opens this in the editor — it **returns a URL, not a file**, so the result must be
saved out of draw.io by hand. Treat CSV as a fast way to stand something up or sanity-check a
hierarchy, not as a maintained pipeline.

## Don't overthink placement

The single biggest waste when authoring draw.io XML is reasoning about coordinates. Declare the
logical structure — which nodes exist, what connects them, what groups them — and let the layout
pass or the rough grid handle the rest.

When there's no CLI and you must place by hand, use a rigid grid and move on:

- Column `x = col * 180 + 40`, row `y = row * 120 + 40`
- Rectangles `140×60`, diamonds `140×80`, circles `60×60`, cylinders `100×70`

Don't add `<Array as="points">` waypoints or `exitX`/`entryX` overrides — edges route themselves.
Don't re-check positions after placing a node. Slight misalignment is invisible; a diagram that
never got finished because of coordinate arithmetic is not.

## Troubleshooting

Symptom-first, because these all present as "the diagram is broken":

| Symptom | Cause | Fix |
|---|---|---|
| Diagram opens but is blank | Missing root cells `id="0"` and `id="1"` | Complete the basic `mxGraphModel` structure |
| Edges don't render | Edge `mxCell` is self-closing | Every edge needs `<mxGeometry relative="1" as="geometry" />` as a child |
| Export is empty or corrupt | Invalid XML — unescaped characters, or an XML comment | Escape `&amp; &lt; &gt; &quot;`; never emit `<!-- -->` |
| CLI not found | draw.io Desktop not installed or not on PATH | Author as XML, deliver a `.drawio`, and tell the user installing draw.io Desktop enables Mermaid conversion, layout, and export |
| Mermaid → PNG crashes | Direct `.mmd` → image with `-e` is broken in current draw.io Desktop | Two steps: convert to `.drawio` with `-f xml`, then export that |
| Blank diagram from Mermaid | Misspelled type keyword, or a syntax error | The first non-directive line's keyword selects the type — validate the Mermaid first ([[nerdynik-mermaid-diagrams]]) |
| `--layout` does nothing or errors | Unknown preset, custom JSON not an array, or a desktop build too old | Use a listed preset, or JSON starting with `[`; on an old build, place coordinates explicitly and suggest updating |
| File won't open after export | Bad path or no file association | Print the absolute path so the user can open it manually |
| Browser opens an empty diagram in `url` mode | `cmd.exe` stripped the `#create=` fragment | On Windows/WSL2 write a `.url` temp file and open that — never pass the URL to `cmd.exe /c start` |
| URL too long for the browser | Large diagram exceeds the URL length limit | Fall back to writing the `.drawio` and opening it locally |

## Further reference

draw.io maintains the exhaustive guides these notes condense — containers and swimlanes,
cross-functional grids, layers, tags, nested architecture containers:

- `https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-reference.md`
- `https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/mermaid-reference.md`

Fetch them when a diagram needs those structures. Everything above is enough without them.
