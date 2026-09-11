# Obsidian Mechanics

Everything about *how Obsidian works* that this vault's conventions depend on. The taxonomy skill
says where things go; this says how to write them so links, properties, and dashboards keep working.

These facts shape every rule:

- **Links are wikilinks resolved by filename, not path** — `[[Note title]]`. Two notes can't share a
  filename anywhere in the vault without ambiguity.
- **Metadata is Properties** — YAML frontmatter at the top of a note.
- **Dashboards come from Dataview** (a plugin: query language, read-only, flexible) or **Bases**
  (native since Obsidian 1.9: editable tables, fast on large vaults, properties-only).

## The hard rule: never move or rename from the filesystem

Renaming a note **inside Obsidian** updates every `[[link]]` pointing at it. Moving or renaming the
file any other way — `mv`, `move_file`, a script — breaks all of them silently, because wikilinks
resolve by filename and nothing else rewrites them.

So: **create new files and edit content freely** with `write_file` / `edit_block`. **Never move or
rename an existing note.** When the right fix requires one, propose it and let the user do it in the
app. If they ask you to do it anyway, name which notes' backlinks will break first, and offer to
search-and-repair `[[links]]` afterward.

This is the single most damaging mistake available in a vault, and it's silent.

## Wikilinks

| Form | Syntax |
|---|---|
| Basic | `[[Three laws of motion]]` — filename, no path, no extension |
| Display text | `[[jane-doe\|Jane Doe, VP Engineering]]` |
| Heading | `[[Org Chart#Jane Doe]]` |
| Block | `[[Note#^block-id]]` |
| Embed / transclude | `![[Note]]`, `![[Note#Section]]`, `![[diagram.svg]]` |
| Alias | add an `aliases` property so the note also resolves under other names |

**Avoid `# | ^ : % [ ]` in filenames** — every one of them means something inside a link.

**Use wikilinks for everything internal.** Standard Markdown links (`[text](path)`) are only worth
reaching for when the vault is also published through a tool that can't parse `[[ ]]` — and the
trade runs both ways, because a Markdown link is a *path* and breaks on exactly the moves a wikilink
survives. Same answer for an AI tool that can't read wikilinks: convert on export, don't convert the
vault.

When adding links, also look for **unlinked mentions**: a note's title appearing as plain text
elsewhere. Converting those is usually the highest-value linking work in a vault, because the
connection was already intended.

## Attachments and embeds

Where an embedded or pasted file lands is a **vault setting**, not a per-note choice: Settings →
Files and links → *Default location for new attachments*. Confirm it before generating anything that
embeds a file — the default drops attachments at the vault root, scattering them across the top
level alongside the taxonomy folders.

Two things follow from embeds resolving the same way links do:

- **`![[diagram.svg]]` resolves by filename.** Two attachments sharing a name anywhere in the vault
  are ambiguous, so generic names (`chart.png`, `image1.png`) are a slow-motion collision. Name an
  attachment for what it is and where it belongs.
- **The move rule covers attachments too.** Moving one from the filesystem breaks every `![[embed]]`
  pointing at it, silently, exactly like a note.

This vault splits the two cases deliberately:

- **Generated from something already in the vault** → keep it **beside its source**, not in an
  attachment folder. `Org Chart.drawio.svg` sits next to `Org Chart.drawio` so the pair travels
  together and the filename already says which chart it is.
- **Received from someone** — a deck, a PDF, a spreadsheet, sample data → an `Assets/` folder with
  an index entry, per the taxonomy skill. Those files are opaque to vault search, so the entry is
  the only thing about them that's findable.

Neither is the Obsidian attachment setting's job. That setting catches what gets *pasted* into a
note; filing an asset is a deliberate act.

## Properties (frontmatter)

A consistent baseline on every note:

```yaml
---
title: Session tokens
aliases: [tokens, session token]
tags: [auth, security]
type: note            # note | moc | dashboard | template | person | project | dsu | customer-story | blog-post
created: 2026-06-18
updated: 2026-06-18
status: evergreen     # seedling | growing | evergreen
related: ["[[auth-flow]]"]
---
```

- **Controlled tag vocabulary.** Decide the tags up front and reuse them; nested tags (`auth/tokens`)
  are fine. Sprawl makes tags useless for filtering.
- **No `#` on tags in frontmatter.** Dates in ISO `YYYY-MM-DD`.
- **One name per concept, vault-wide.** `created`, not `created` / `date` / `Created`. Dataview and
  Bases both key off exact property names, so an inconsistent name is an invisible hole in every
  query. When normalizing, pick the canonical name and migrate the rest.
- **Bump `updated`** whenever you change a note.

## Maps of Content (MOCs)

A MOC is a note that links the related notes on a topic — the navigation layer. More flexible than
folders, and it needs no institutional knowledge to follow.

- Tag them `tags: [moc]` or `type: moc` so MOCs are themselves discoverable.
- Keep a top-level **Home / Index MOC** linking to every topic MOC. In this vault, `<Company Name>/`
  serves that role for practices and partners.
- A MOC is a short intro plus grouped wikilinks. Hand-curate it, or generate it with a query.

```markdown
---
type: moc
tags: [moc]
updated: 2026-06-18
---
# Acme Corp — Map of Content

## Organization
- [[Org Chart]]
- [[Account Team]]

## Related MOCs
- [[Partners MOC]]
```

### Folders vs. MOCs in this vault

General Obsidian advice holds that folders are coarse buckets and MOCs plus tags do the real
organizing. **This vault deliberately inverts that:** the taxonomy is strict and folder-first,
because a Professional Services vault has to be predictable for someone who never learned its MOC
layer — a new engineer looking for a SOW should land on it without reading an index first.

MOCs still earn their place *on top of* the folders, for the views a tree can't express: one person
across every account they touch, a practice across its partner and its customers. Use them to
cross-cut the taxonomy, never to replace it, and don't build a parallel tag hierarchy that just
restates folder names.

## Dashboards

**Bases** — native, editable, fast. A `.base` file or a `base` code block builds table and board
views from properties, and each cell edits the underlying note's frontmatter. Use it for anything
operational: task lists, project pipelines, account rosters.

**Dataview** — a plugin, read-only, more expressive. Use it for reports and auto-generated MOCs.

```dataview
TABLE status, updated, tags
FROM #auth
WHERE type = "note"
SORT updated DESC
```

```dataview
LIST FROM #auth WHERE type != "moc" SORT file.name ASC
```

```dataview
TABLE updated FROM "" WHERE updated >= date(today) - dur(7 days) SORT updated DESC
```

Heavy Dataview queries lag on large vaults — prefer Bases there. **Confirm which the user actually
has** before writing a dashboard; Dataview is a community plugin and may not be installed.

## Orphans and link hygiene

An orphan has no inbound *and* no outbound links. Finding them:

1. **Search** the vault for `[[<title>]]` — zero hits means no inbound links. Scan the note's own
   body for `[[...]]` to confirm no outbound. The same searches surface **unlinked mentions** (the
   title as plain text) and **broken links** (a `[[target]]` whose file doesn't exist).
2. **Graph view** (Cmd/Ctrl+G) — orphans float as isolated dots at the edges.
3. **Dataview:**
   ```dataview
   LIST WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
   ```

For each orphan: link it from a relevant MOC or note, tag it `#needs-link` for a batch pass, or
propose archiving it. Fix broken links and convert unlinked mentions with `edit_block`.

In this vault, the most common orphan source is a **relationship page with no wikilink index under
the org chart it belongs to** — Mermaid `click` links don't register as Obsidian links.

## Deduplicating

Search titles and aliases for near-identical notes. To merge: keep the most-linked filename, copy
the unique content across with `edit_block`, search for inbound `[[links]]` to the note being
discarded and repoint them, *then* delete it. Add the old name as an `aliases` entry if it was
widely referenced.

Standardize filenames on one convention and stay on it. This vault uses display casing with spaces
(`Acme Corp`, `Jane Doe`).

## Keeping the vault usable by an agent

- **Consistent property names and types**, so metadata can be filtered and reasoned over.
- **A Home/Index MOC** as the single entry point to read first.
- **A one-line `summary` or `description` property** per note for quick scanning.
- **Few orphans and no broken links**, so the link graph is a reliable map.
- **Atomic notes** — one idea each — are easier to retrieve and cite.

## Maintenance workflows

Recipes for the generic vault work. The taxonomy-specific playbooks are in the skill itself.

- **Build navigation** — write the topic MOCs, edit the notes to link into them, refresh the
  Home/Index MOC, then convert unlinked mentions into real wikilinks.
- **Normalize metadata** — audit which property names are actually in use *first*, pick the
  canonical name per concept, then migrate note by note and add the missing baseline properties.
  Discovering a fourth spelling of `created` halfway through means redoing the pass.
- **Cleanup pass** — search for orphans, broken links, and unlinked mentions; dedupe; report what
  changed. Renames and moves stay with the user, in the app.
- **Dashboard** — confirm Dataview vs. Bases, then build the view from properties and tags that
  already exist. A dashboard querying a property nobody populates renders empty and reads as broken.

## Checklist before finishing

- [ ] New and changed notes carry consistent frontmatter under canonical property names.
- [ ] No move or rename was done from the filesystem; any needed one was flagged for the user.
- [ ] Every new note is linked from at least one MOC or note — no new orphans.
- [ ] Tags come from the controlled vocabulary.
- [ ] Dashboards reference properties that actually exist.
- [ ] `updated` bumped on every changed note.
