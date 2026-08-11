---
name: nerdynik-obsidian-project-manager-notes
description: Use when reading, summarizing, querying, or reporting on project plans stored by the Obsidian "Project Manager" community plugin (obsidian-pm) — milestones, tasks, subtasks, dependencies, status, priority, and other planning data written to the vault. Use for status reports, "what's overdue/blocked," milestone tracking, or turning plan data into a client-facing update.
---

# Reading Project Manager Plugin Data

The Obsidian community plugin **Project Manager** (`obsidian-pm`, by StepanKropachev) stores every project, task, subtask, and milestone as its own plain-Markdown file with YAML frontmatter, inside one configurable vault folder (default `Projects/`). No database, no export step — read the files directly.

**Builds on Desktop Commander's `obsidian-vault` skill** for the mechanics of searching and reading vault files (`start_search`, `read_multiple_files`). This skill is specifically about *parsing and reasoning over* what Project Manager writes, and applies to any vault using the plugin regardless of what the projects are for.

Nothing here assumes a particular vault taxonomy. If the vault also follows a domain-specific structure — for Professional Services work, [[nerdynik-obsidian-vault-organization]] — that skill defines where a project's *supporting* material lives relative to this plan data, and how project titles encode which customer they belong to. Use it when it's available; don't require it.

## Storage layout (confirmed against a live vault)

For a project titled `<Project Title>`, the Projects folder contains:

```
Projects/
  <Project Title>.md            # the project note — pm-project: true
  <Project Title>_tasks/        # every task/milestone/subtask for that project, flat
    <slug-of-item-title>.md
    <slug-of-item-title>.md
    ...
```

The tasks folder name is literally the project note's filename stem plus `_tasks` — not a setting, a fixed convention the plugin applies per project. Item filenames are a slugified form of `title` (lowercase, spaces→hyphens; the plugin's slugifier doesn't always strip everything — e.g. `&` can survive into a filename as a literal character, and multi-word symbol replacements can produce doubled hyphens like `raw--bronze.md` for "Raw->Bronze"). Don't try to reverse-derive a title from a filename; read `title` from frontmatter instead.

All items — regardless of `type` — live in that one flat `_tasks/` folder side by side; there is no further subfolder nesting for milestones vs. subtasks vs. deeper subtask levels.

## Confirmed frontmatter schema

**Project note** (`pm-project: true`):

| Field | Meaning |
|---|---|
| `id` | The project's own unique ID (opaque alphanumeric token, plugin-generated) |
| `title`, `description` | Name and free-text description (often empty) |
| `color`, `icon` | Display color (hex) and emoji, used in the plugin's own UI |
| `taskIds` | Array of `id`s for this project's **direct top-level items only** (not every descendant — a milestone's subtasks are not repeated here) |
| `customFields` | Per-project custom field *definitions* (often `[]` if none were configured — this defines the fields, it isn't where a task's custom-field *values* live) |
| `teamMembers` | This project's own member roster (separate from the vault-wide team roster in plugin settings) |
| `savedViews` | Saved Table view filter/sort configs |
| `createdAt` / `updatedAt` | ISO 8601 timestamps |

Body: a `## Tasks` checklist, one line per top-level item as a wikilink — kept in sync with `taskIds`.

**Task / Subtask / Milestone note** (`pm-task: true`):

| Field | Meaning |
|---|---|
| `id` | This item's own unique ID |
| `projectId` | The owning project's `id` — the real cross-reference back to the project, independent of the folder it happens to sit in |
| `parentId` | The parent item's `id` if this is a subtask of another task/milestone; **blank/omitted for top-level items** |
| `title` | Item name |
| `type` | `milestone`, `subtask`, or `task` — lowercase in frontmatter (the docs' capitalized "Task/Subtask/Milestone" are just display labels). A milestone is a zero-duration marker (`start` == `due`). **A given project may only use a subset of the three** — e.g. an all-milestones-plus-subtasks project with no bare `task` items at all is a normal, observed real-world shape, not a gap in the data. |
| `status` | Lowercase value from the active palette — default palette is To do/In progress/Blocked/In review/Done/Cancelled, but **a project can define and swap in its own palette that fully replaces the global one for every item in that project**. Only `todo` was directly observed in the vault checked; the other five are inferred as lowercased versions of their display labels, not yet confirmed character-for-character (e.g. whether "In progress" serializes as `in-progress`, `inprogress`, or something else) — read the literal string from a real item in that state before matching against it exactly. |
| `priority` | Lowercase value from the active palette, e.g. `medium` — same per-project override caveat as `status` |
| `start` / `due` | Plain dates (`YYYY-MM-DD`) — distinct from the `createdAt`/`updatedAt` ISO timestamps |
| `progress` | 0–100 |
| `assignees` | Array of names/identifiers, drawn from the project's `teamMembers` roster |
| `tags` | Freeform array |
| `subtaskIds` | Array of this item's direct children's `id`s (empty on leaf subtasks) |
| `dependencies` | Array of blocking/dependent items — **not observed populated in the wild yet**; given every other cross-reference in this schema (`projectId`, `parentId`, `taskIds`, `subtaskIds`) uses the opaque `id`, treat a populated `dependencies` entry as almost certainly another item's `id` too, but confirm on a real populated example if the vault has one before relying on it. |
| `recurrence`, custom field values, time estimate, time logs, task-level `description` | All documented as supported, but were **absent from frontmatter entirely** (not present as empty) on every real item inspected — treat a missing key as "not set," not as a parse error, and don't assume a key's absence means the plugin doesn't support it. |

Body: a `Project: [[...]]` backlink line always present; a `Parent: [[...]]` backlink line if `parentId` is set; a `## Subtasks` checklist (wikilinks, kept in sync with `subtaskIds`) if the item has children.

**Net effect on linkage**: project↔task and subtask↔parent are each encoded **twice, redundantly** — once as frontmatter ID references (`projectId`, `parentId`, `taskIds`, `subtaskIds`) and once as human-readable wikilink checklists/backlinks in the body. For programmatic reasoning, prefer the ID fields — they're unambiguous — and use the body wikilinks only as a human-facing cross-check or when you don't yet have the full ID graph loaded.

Remember the per-project status/priority override above when aggregating across multiple projects in a shared vault — check each project's own palette rather than assuming the six/four defaults apply uniformly everywhere.

## Reading algorithm

1. **Locate the store.** Ask, or search the vault for files containing `pm-task: true` / `pm-project: true` frontmatter, to find the configured Projects folder (don't assume the default `Projects/` name is still in use).
2. **Find the project(s) in scope.** Search for `pm-project: true` and match on the project note's `title`. In a shared vault holding many projects, the title is usually what disambiguates — vaults commonly prefix it with an owning customer, team, or area (e.g. `<Customer Abbreviation> - <Project Name>`, the convention [[nerdynik-obsidian-vault-organization]] defines for PS vaults). Ask which project is meant rather than guessing when several titles are close. Note the project note's own `id`.
3. **Gather that project's items** by reading every file in `<Project Title>_tasks/` (fastest: `read_multiple_files` on the whole folder) and/or filtering by `projectId` equal to the project's `id` — the two should agree; if they don't, trust `projectId` since that's what the plugin itself uses.
4. **Build the ID graph in memory**: map `id → item`, then link children by `parentId` (or equivalently each parent's `subtaskIds`). Top-level items are those with no `parentId`.
5. **Read each item's `type`, `status`, `priority`**, remembering these are lowercase and that `status`/`priority` come from that project's own palette if it defines a custom one rather than the global default.
6. **Resolve `dependencies`** the same way as `parentId` — treat entries as other items' `id`s and look them up in the graph you built in step 4.
7. **Compute derived facts** as needed: overdue = `due` in the past and `status` not one of the project's "done-like" statuses; blocked = `status` is that project's "blocked"-equivalent value or the item has an unresolved dependency; upcoming milestone = nearest `type: milestone` by `due`.

## Common playbooks

### Status report for a project
Group items by `status` (using that project's own palette), list anything overdue or blocked with its `title`/`assignees`/`due`, and surface the next 1–3 upcoming milestones by `due` date. Keep raw internal fields (assignee identifiers, custom fields meant for internal tracking) out of anything meant to go to the client — restate in plain language instead of dumping frontmatter.

### "What's blocking X?"
Resolve `X`'s `dependencies` entries to their titles/current status; if any dependency isn't itself in a "done-like" status, name it as the actual blocker rather than just echoing "blocked."

### Translating plan data into a client-facing update
Roll milestones and top-level tasks (not every subtask) into prose organized by outcome, not by internal status label — a client update says "on track for the July 30 rollout milestone," not a raw `status` value. Never surface internal `assignees` identifiers, custom fields, or time-log notes unless the update is explicitly internal-facing.

### Editing an item (marking done, logging time, updating progress)
Edit only the relevant frontmatter keys with `edit_block`, leaving every other key and the body untouched — Project Manager (and, if present, the TaskNotes plugin) both re-parse this frontmatter and expect non-destructive edits from other tools. Bump `updatedAt` to the current ISO timestamp on any change, matching the plugin's own behavior; never touch `id`, `projectId`, or `parentId`.

## Adjacent plugin: TaskNotes

If the vault also uses the **TaskNotes** plugin, Project Manager tasks can be exposed there too (via a `pm-task: true` identification rule mapping `scheduled` → `start`), but the two plugins use different vocabulary for the same concepts — TaskNotes uses `blockedBy` and project *links*, Project Manager uses dependency/parent *id references*. If a vault has both, check which plugin actually wrote a given file's frontmatter shape before parsing it against the table above; don't assume every task file in the Projects folder follows the Project Manager schema.

## Source & drift warning

The storage layout and frontmatter schema above were confirmed directly against a real, in-use Project Manager project (cross-checked against the `obsidian-pm` README's documented field list) — not read off the docs alone. Plugin updates or vault-specific customization (custom fields, custom statuses/priorities) can still change what a given vault contains — when something doesn't match, trust the files in front of you over this document, and update this file if the mismatch turns out to be a real plugin-version change rather than one vault's local customization.
