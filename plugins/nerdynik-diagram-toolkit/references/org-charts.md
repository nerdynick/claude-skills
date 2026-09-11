# Org Charts

Read this before drawing any reporting structure, stakeholder map, or who-reports-to-whom picture.
It covers what belongs in the chart and how to be sure it's right — which is where org charts
actually go wrong — then how to render it in each tool.

An org chart is the diagram type most likely to be **confidently wrong**. A flowchart that's wrong
looks wrong. A reporting line that's wrong looks exactly like one that's right, gets shown to the
people it describes, and is repeated by everyone who saw it.

## The source of record is not the chart

Reporting data lives somewhere — a vault note, an HR export, a wiki page, a directory. The chart is
a **view** of that record, never the place a fact is first written down.

Two obligations follow:

1. **Read the record before drawing.** Never assemble a chart from what someone said on a call plus
   memory.
2. **Write back what you learn.** Building a chart surfaces new chains, corrected titles, and
   resolved questions. Put them in the record in the same session, dated, with the source named —
   otherwise the next chart starts from the same stale data. See "Write findings back" below for
   what that covers.

If there is no record, say so and offer to create one. A chart with no backing record is a one-time
artifact that silently rots.

## Scope: who's asked for, plus only what connects them

The ask is almost always "show me these people." Answer it literally:

- Include **every person asked for**.
- Include **only** the managers needed to connect them to a common root — *pass-through* managers.
- Include **nobody else**. Not their peers, not their teams, not the rest of the department.

A pass-through manager is not optional and must never be dropped to tidy the picture. If Ravi Patel
reports to Marcus Webb and Marcus wasn't requested, Marcus still appears — otherwise the chart
asserts a reporting line that doesn't exist.

**Name the pass-throughs when you deliver.** The reader needs to know some boxes are structural
rather than people being engaged.

## Verify every chain before drawing

This is the step that takes the time, and skipping it is how a chart ships wrong.

**The requested people usually do not share one branch.** An ask that sounds like "from the CIO
down" routinely spans two or three chains that only converge at the CEO. Discover that before
laying anything out — it changes the whole structure.

For each person, confirm the chain upward from an authoritative source: the record when it holds a
*verified* chain; a directory or profile that renders the full chain in one view (a Teams profile's
Organization tab does this, and a screenshot of it resolves a person completely); failing both,
ask.

**Never invent a reporting line.** In particular: never assume someone reports to the CEO because
you can't find their manager, and never promote a person to be a branch root to avoid drawing an
unresolved link. When a chain is genuinely unresolved, either

- **draw the edge dashed** and say plainly in your reply that the link is unconfirmed, or
- **stop and ask**, if the unresolved link would change the chart's structure.

A dashed edge is an honest placeholder, not a finished answer. Clear it once confirmed.

### Verified beats second-hand

- The **verified** line is the solid edge.
- A reported-but-unconfirmed change is **not** drawn as fact — dashed with a dated annotation, or
  left off the chart and mentioned in your reply.
- **Never overwrite a verified chain in the record on one second-hand remark.** Annotate it as
  unconfirmed; leave the verified entry intact.
- When the user confirms or disproves such a report, resolve it in the record the same session —
  mark it resolved and strike through what was disproven rather than deleting the history.

## Audience decides what a card carries

Get this wrong and the chart either under-informs or leaks contact details into a deck.

| | **Shareable** *(default)* | **Internal reference** |
|---|---|---|
| Name, title, department | yes | yes |
| Projects, standing-role pills | yes | yes |
| **Email, phone** | **never** | **yes** |
| Banner | none | `INTERNAL REFERENCE — CONTAINS CONTACT DETAILS` |
| Built for | account teams, QBR and status decks, anything screen-shared | desk reference for people who actually contact these individuals |

**Shareable is the default** — it's the version that gets pasted into decks and shared on calls,
which is exactly why it carries no contact information.

But an internal-reference chart **should** carry contact info; that's the entire reason it's a
separate mode. A desk reference without the details is worse than a plain contact table. Offer it
when the request is clearly for internal use.

Two rules in internal mode:

- **It stays internal.** Never to the customer, a public deck, or a website. Say so when handing it
  over.
- **Unknown is not blank.** Write `(email unknown)` rather than leaving the line empty — a blank
  reads as "no email," and sends someone hunting for a person who does have one.

When generating both modes, generate them from one dataset. Two hand-maintained variants diverge.

## Design decisions to stop re-deciding

Settled. Re-deciding per chart produces an inconsistent family of diagrams.

- **Cards are uniform.** Same size, same layout, same content grid for everyone. Do **not** style
  requested people differently from pass-through managers — a chart that visually ranks people by
  whether we happen to engage them reads as a judgment about the people.
- **Color codes the branch and nothing else.** One color per reporting branch, applied to the whole
  card and the edges into it.
- **No legend.** Put a named pill in the branch color above each branch instead. If a chart needs a
  legend, the encoding is wrong.
- **Label blocks, don't key them.** A `PROJECTS` heading on the card beats explaining what the
  orange text means.
- **Standing roles are pills, not projects.** A cross-project point of contact gets a filled pill
  (`PROJECT MGMT POC · ALL PROJECTS`) because it's a role, not another project. Reserve pills for
  genuinely cross-project roles.
- **Say "expected" when it's expected.** Unconfirmed involvement reads `SOI (expected)`, never as a
  plain project.
- **Use the organization's own palette** when one exists. If a chart needs a fifth and sixth branch
  color, it has probably outgrown one diagram — split it.

## Write findings back to the record

Building a chart is the most productive audit the record ever gets — chains get walked, titles get
read off profiles, and gaps become obvious. All of that is lost unless it lands back in the record
**in the same session**, each entry dated and with its source named:

- **Newly mapped chains** — the reporting tree, plus whatever per-person detail the record holds,
  each annotated with where it came from and when (`directory profile, captured 2026-09-11`).
- **Corrected titles and departments.** A title read off a live profile supersedes one typed in
  months ago — but record that it changed rather than silently overwriting.
- **Involvement** — which projects or accounts each person turned out to be on. Where the existing
  structure can't express what's now in play, add to it and flag the old view as narrower rather
  than rewriting a verified record.
- **Resolved open questions** — mark them resolved where they were originally asked; don't just
  delete them. The next person needs to know it was chased.
- **New open questions**, and they're the most valuable output: a manager whose own chain is
  unknown, a missing email, an involvement that's expected rather than confirmed, a name that needs
  its spelling checked.
- **Truncated source data, marked as truncated.** Directory cards clip long values. Record
  `US Remote Amer… (truncated in source)` — never complete it by guessing, because a plausible
  completion is indistinguishable from a fact once it's written down.

**Keep the chart's source** — the Mermaid text, the `.drawio`, or whatever spec generated it — beside
the record. It's the input to the next revision, and re-deriving it from a rendered image is
guesswork. Store it with the engagement's material, not in a shared tooling repo, since a real chart
carries a customer's internal reporting structure and possibly staff contact details.

## Run a name-collision pass

Before delivering, check the cast for names easy to confuse — both against each other and against
people in the record who aren't on the chart. A single account routinely turns up several: two
people sharing a first name where one is ours and one is the customer's, two more sharing a first
name in different branches, two at similar seniority whose surnames differ by a letter, and two
directors whose titles differ only by a trailing qualifier.

For each collision, make sure titles disambiguate them on the chart, and **write a warning into the
record**. This matters most for meeting transcripts, where a first name is often all that gets
captured — a stray first name attributed to the wrong person propagates quietly, and nothing in the
downstream note will look wrong.

## Which tool

| Want | Use |
|---|---|
| A chart that lives in a document and diffs | **Mermaid** |
| A file to hand over, print, or drop in a deck | **draw.io** |
| Rich cards — multi-line, pills, contact blocks | **draw.io** |
| Links out to per-person pages | Either; Mermaid `click`, draw.io `<UserObject link=…>` |
| 40+ people | Neither as one diagram — split by branch first |

### In Mermaid

`flowchart TD`, one node per person, edges from manager to report. Keep the label to a fixed small
set of lines — name, title, and at most one more — and link out for the rest. A label carrying
everything defeats the diagram.

```
flowchart TD
  marcus_webb["<b>Marcus Webb</b><br>CTO"]
  jane_doe["<b>Jane Doe</b><br>VP of Data Engineering"]
  marcus_webb --> jane_doe
  ravi_patel["<b>Ravi Patel</b><br>Director, Platform"]
  jane_doe -.-> ravi_patel
  classDef unconfirmed stroke-dasharray: 5 5
```

- **Node ids are the person's name, lowercased with underscores.** Stable ids mean a regenerated
  chart diffs cleanly instead of reshuffling every line.
- **Dashed edge (`-.->`) for an unconfirmed reporting line.** Mermaid gives you this for free; use
  it rather than dropping the edge.
- Branch color via `classDef` + `class`, not inline styles — it survives renderers that strip
  `init` directives.
- Mermaid lays out automatically and you cannot place nodes. If the arrangement is genuinely wrong,
  that's the signal to move to draw.io.

### In draw.io

- **`--layout verticalTree`** is the preset built for hierarchies. Never hand-place an org chart's
  coordinates. `horizontalTree` for a wide, shallow org.
- **Card content goes in an HTML label** — `<b>Name</b><br>Title<br>Email`, with `<hr>` to separate
  a projects band. Remember the double escaping (`&lt;br&gt;` inside the XML attribute).
- **`<UserObject>` for anyone with a page to link to**; a bare `<mxCell>` can't carry a link.
- **Dashed edge for unconfirmed:** add `dashed=1` to the edge style.
- **Skip `search_shapes`.** Org charts are rectangles and lines.
- **The CSV importer is often the fastest route in** — it maps one-to-one onto a person-per-row
  record and builds the edges from a manager column:

  ```
  # label: %name%<br><b>%title%</b>
  # style: rounded=1;html=1;whiteSpace=wrap;fillColor=%fill%;
  # connect: {"from":"manager","to":"id","invert":true,"style":"edgeStyle=orthogonalEdgeStyle;"}
  # layout: verticaltree
  id,name,title,manager,fill
  1,Marcus Webb,CTO,,#dae8fc
  2,Jane Doe,VP of Data Engineering,1,#ffffff
  ```

  It opens in the editor rather than writing a file, so it's a fast way to check a hierarchy or
  stand something up — not the maintained pipeline.

## Before delivering

- [ ] Every requested person is on the chart.
- [ ] Every pass-through manager is present, and named as such in your reply.
- [ ] Every chain was verified against a source, or is drawn dashed and called out.
- [ ] No contact details on a shareable chart.
- [ ] `(unknown)` rather than blank on an internal chart.
- [ ] Name-collision pass done; warnings written back.
- [ ] New chains, corrected titles, resolved *and* newly opened questions written back to the
      record, dated and sourced; anything truncated in the source marked as truncated.
- [ ] The chart's source is kept beside the record, not left as only a rendered image.
- [ ] You looked at the rendered output. Text overflow and collisions are only visible there.
