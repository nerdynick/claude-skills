# Project Gantt Charts

Read this before drawing a project schedule, delivery plan, roadmap, or timeline. It covers what a
**project** Gantt is made of — the milestone / story / task breakdown, who owns what, and how deep
to go — then how to render one in each tool.

Scoped to project schedules on purpose. The breakdown model below assumes work that decomposes into
milestones and owned deliverables, which is what a project plan is and what every tracker stores.
A Gantt of something else — a manufacturing run, a publishing calendar, a personal timeline — won't
want that model, though the Mermaid and draw.io mechanics at the end apply to any Gantt.

A project Gantt answers three questions: **what happens when**, **what blocks what**, and **what has
to be true by a given date**. A chart that shows bars but not dependencies answers only the first,
and is usually the one that gets a project into trouble.

## The breakdown

Almost every project schedule decomposes the same way, whatever the tracker calls the levels:

| Level | What it is | Owner | On the chart |
|---|---|---|---|
| **Phase / Workstream** | The coarse grouping — Discovery, Build, Migrate, Hypercare; or one per parallel track | A lead, if anyone | A section header; never a bar of its own |
| **Milestone** | A zero-duration marker: a date something must be *true*. Go-live, sign-off, gate, contract date | **Normally none** | A diamond, not a bar |
| **Epic / Story** | A deliverable unit spanning days or weeks | **One accountable owner** | The bars that carry the schedule |
| **Task / Subtask** | The work inside a story | **One owner each** | Detailed charts only — see below |
| **Dependency** | "B can't start until A finishes" | — | An edge, or `after <id>` |

### Owners

**Milestones don't carry owners; stories and tasks do.** A milestone is a date a condition has to be
true by, and that condition is usually the product of several people's work — naming one of them as
its owner either overstates their control or quietly turns the milestone back into a task. Where a
milestone genuinely needs a name against it, what's wanted is the person who *declares it met*;
label that as an approver, not an owner.

Below the milestone line, every bar gets **exactly one accountable owner**, even when several people
do the work. Two names on a bar means nobody is named. Trackers often hold a list of assignees —
pick the accountable one for the chart and leave the rest to the tracker.

An owner is a person, not a team, unless the team really is the unit of accountability. Either
convention is fine; say which one the chart uses, because a lone "Platform" among personal names
reads as a gap rather than a choice.

Rules of thumb:

- **Under ~30 bars** for a readable chart. Over that, split by phase or workstream and produce
  several.
- **Every phase should end in a milestone.** If a phase has no date something must be true by, it
  probably isn't a phase.
- **A bar with no dependency and no milestone is suspicious** — either it's genuinely independent,
  or a dependency wasn't captured.

## High-level and detailed are two different charts

Ask which one is wanted before drawing. Depth is the whole difference, and everything else follows
from it.

### High level

**Milestones, plus — optionally — one tier of the stories or tasks beneath each.** Nothing deeper.

This is the chart for a steering committee, a QBR, a status deck, or a customer conversation. Its
job is answering "are we going to make the dates," so it carries the dates that matter and at most
one remove of what they depend on. A high-level Gantt that has to be scrolled has failed at the only
thing it was for.

**Milestones-only is a legitimate high-level chart**, and often the right one. Add the tier beneath
when the reader needs to see *why* a milestone is at risk; leave it off when they only need to know
*whether* it is.

### Detailed

**Everything, down to the lowest subtask.**

This is the working chart — the delivery team, a sprint or workstream review, whoever is actually
sequencing the work. Depth is the point: a chart that stops at story level can't show that the thing
blocking go-live is a two-day subtask buried in week six.

Recurse to the leaves rather than stopping at the first level of subtasks; nesting is often deeper
than one level. The cost is that it stops working as a single picture, so **expect to split it** —
one chart per phase, workstream, or owner. The ~30-bar ceiling still applies, because it's a rule
about one rendered chart, not about the schedule as a whole.

### Don't produce something in between

The failure mode is the chart that renders every item in the tracker at one depth: 120 bars, nobody
can read it, and the milestones are lost among the work. That serves neither audience.

When the request is just "the Gantt," build the **high-level** one and offer the detailed split. It's
what most requests actually mean, and going deeper from there is cheap.

**Generate both from one dataset.** Two hand-maintained charts diverge, and the divergence shows up
in front of the customer.

## Things to get right

**Dates are claims.** A bar drawn to a date asserts a commitment. Mark anything not agreed as
proposed, and say which dates are baselined versus estimated. An estimated finish rendered
identically to a contractual go-live is how a schedule gets quoted back as a promise.

**Show the critical path** if you know it, and say so if you don't. Mermaid has `crit` for exactly
this. A Gantt whose critical path isn't visible hides the only thing that determines the end date.

**Don't fake precision.** If a story is "about three weeks in Q2," don't render it as
`2026-04-13 → 2026-05-01`. Round to weeks, or mark it explicitly as an estimate.

**Weekends and holidays.** `excludes weekends` changes every downstream date. Decide deliberately
whether the schedule is in working days or calendar days, and state which.

**Progress is a separate axis from status.** "60% complete" and "on track" are different claims.
Render one; don't imply the other.

## Sourcing from a tracker

When the schedule comes from a project tracker rather than a conversation, the mapping is usually
direct. For the Obsidian Project Manager plugin (see [[nerdynik-obsidian-project-manager-notes]] for
the full schema):

| Tracker field | Gantt use |
|---|---|
| `type: milestone` | A milestone marker — the plugin defines these as zero-duration (`start` == `due`) |
| `type: task` with no `parentId` | A top-level bar — this is the story level |
| `type: subtask` | Rolled into the parent's bar on a high-level chart; its own bar on a detailed one |
| `subtaskIds` | The children to recurse into for a detailed chart — keep going until it's empty, since nesting runs deeper than one level |
| `start` / `due` | Bar start and end (`YYYY-MM-DD`) |
| `progress` (0–100) | Percent complete, if the renderer shows it |
| `status` | `done` / `active` / `crit` tagging — but read the project's own palette, it can be overridden |
| `dependencies` | The `after` relationships — see the caution below |
| `assignees` | The bar's owner. It's an array, so pick the accountable one for the label; **ignore it on milestones** |

Three cautions from that schema specifically:

- A project may use only a **subset** of the three types — all-milestones-plus-subtasks with no bare
  `task` items is a normal observed shape, so don't treat a missing story level as bad data.
- `status` and `priority` values come from a **per-project palette** that can fully replace the
  defaults. Read the literal strings; don't match against assumed ones.
- **`dependencies` is frequently empty**, and an empty array is not evidence that nothing blocks
  anything. Don't render a chart that implies an independent, parallel schedule off the back of it,
  and don't claim a critical path you derived from no dependency data — say the dependencies weren't
  in the tracker and ask, or mark the sequence as inferred.

**Other trackers map the same way** — Jira epics and stories, Asana sections and tasks, a
spreadsheet with start/end/parent columns. The level names change; the four-level breakdown doesn't.

## Which tool

**Mermaid is the right default.** It has a real `gantt` type, the source diffs, and dependencies are
first-class. Reach for draw.io only when you need a file to hand over, heavy branding, or a layout
Mermaid won't produce.

### In Mermaid

```
gantt
    title Lakehouse Migration
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    excludes weekends
    todayMarker stroke-width:3px,stroke:#c00

    section Discovery
    Kickoff                  :milestone, m_kick, 2026-01-05, 0d
    Stakeholder interviews   :done,     d_int,  2026-01-05, 10d
    Current-state assessment :active,   d_asm,  after d_int, 8d
    Discovery sign-off       :milestone, m_disc, after d_asm, 0d

    section Build
    Ingestion pipeline       :crit,     b_ing,  after m_disc, 15d
    Transformation layer     :          b_tfm,  after b_ing, 12d

    section Cutover
    Go-live                  :milestone, m_live, after b_tfm, 0d
```

Syntax that matters:

- **Item form:** `Label :tag1, tag2, id, start, duration`. Tags are optional, the id is optional but
  you need it for anything depended on.
- **Tags:** `done`, `active`, `crit` (critical path), `milestone`. Combine them — `crit, active`.
- **Dependencies:** `after <id>` in place of a start date. Chain them; that's how the critical path
  stays honest when a date moves. `after id1 id2` waits on both.
- **Milestones** take `0d` duration.
- **`dateFormat`** parses your input; **`axisFormat`** formats the axis (`%b %d`, `%Y-%m-%d`).
- **`excludes weekends`** or `excludes 2026-07-04` skips non-working days. There's a matching
  `includes`.
- **`tickInterval 1week`** with `weekday monday` controls gridlines.
- **`todayMarker off`** hides the today line — do that for a plan that isn't about right now.
- **Compact mode** packs non-overlapping bars onto shared rows:
  `%%{init: {"gantt": {"displayMode": "compact"}}}%%`

Limits worth knowing before you commit: Mermaid Gantt **doesn't draw dependency arrows** — `after`
sequences the bars but the link is implicit. It has **no resource or swimlane axis** (approximate it
with one `section` per owner). And **percent-complete isn't rendered**; `done` / `active` is the
whole vocabulary. If any of those are required, that's the signal to use draw.io.

### In draw.io

draw.io has no native Gantt type. Two routes:

1. **Convert the Mermaid.** draw.io's Mermaid parser supports `gantt`, so pass the Mermaid source
   to `create_diagram`, or convert it with the desktop CLI (`drawio -x -f xml -o plan.drawio
   plan.mmd`). You get editable draw.io shapes from a schedule you can keep in text. **This is the
   right first move** — author in Mermaid, convert, then adjust.
2. **Build the grid by hand** when you need what Mermaid can't do — real dependency arrows, a
   resource axis, per-bar progress fill, or brand styling. A Gantt is then just a table: a header
   row of time buckets, one row per item, and a positioned rectangle per bar.

   Hand-building means you own the date arithmetic, so fix a scale first — e.g. `x = 40 + weeks *
   60`, `width = duration_weeks * 60` — and place every bar from it. **Don't use `--layout` on a
   hand-built Gantt**; it will move the bars off their dates and destroy the chart. This is one of
   the few diagrams where coordinates genuinely are the content.

   Milestones are diamonds (`rhombus`) at a single x. Dependency arrows are ordinary edges with
   `edgeStyle=orthogonalEdgeStyle`. Progress is a second rectangle overlaid at partial width, not a
   label.

## Before delivering

- [ ] The chart is deliberately high-level *or* deliberately detailed — not a blur of the two.
- [ ] Milestones carry no owner; every story and task bar carries exactly one.
- [ ] Every phase ends in a milestone.
- [ ] Dependencies are expressed with `after` or arrows, not implied by position.
- [ ] Estimated dates are marked as estimates; baselined ones are identified.
- [ ] Working-days vs calendar-days is stated.
- [ ] Critical path is shown, or its absence is called out.
- [ ] Under ~30 bars, or split into several charts.
- [ ] You looked at the rendered output — Gantt text overflows its bars constantly.
