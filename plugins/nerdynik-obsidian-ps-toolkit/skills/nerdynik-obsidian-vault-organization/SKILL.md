---
name: nerdynik-obsidian-vault-organization
description: >-
  The baseline for working in a Professional Services / C&SI / SI Obsidian vault — also called the
  vault, KB, knowledge base, or notes. Load it for anything that touches the vault at all: finding
  where something already lives, filing something new, or auditing what's there. Defines the
  canonical Customers / Partners / Practices / Company taxonomy, the people model behind
  relationships and org charts, the naming and cross-linking conventions everything else depends on,
  and the Obsidian mechanics they rest on — wikilinks, properties, MOCs, dashboards, link hygiene.
  This establishes the general conventions; other skills and project context may extend them for a
  particular vault or artifact, so treat it as the starting point rather than the last word.
---

# Obsidian PS Vault Organization

Keeps customer, partner, practice, and company content in a consistent place across a Professional Services / C&SI / SI practice's Obsidian vault, so both humans and an agent can predict where something lives without re-deriving structure each time.

Users call this vault different things — *the vault*, *the KB*, *the knowledge base*, *my notes*, *Obsidian notes*. They all mean the same thing; this skill applies regardless of which term is used.

This file carries the taxonomy and the routing — where things go and how they link. The specifications live beside it, and each is worth opening before you work on that artifact:

| Reference | Covers |
|---|---|
| `references/obsidian-mechanics.md` | Wikilinks, properties, MOCs, Dataview and Bases dashboards, attachments, orphan and broken-link hygiene, deduplication. **Read it when doing anything beyond placing a file.** |
| `references/org-charts-and-relationships.md` | The people model in full: who earns a relationship page, entry format, generating and syncing both charts, branding, splitting |
| `references/assets.md` | Filing and indexing assets, renaming screenshots, provenance |
| `references/dsu-notes.md` | Daily standup notes: frontmatter, provenance block, sections, transcription flags |
| `references/daily-summaries.md` | The daily-summary spec and template |
| `references/customer-stories-and-blog.md` | Customer stories, use cases, case studies, blog posts, and their tags |
| `references/company-folder.md` | The `<Company Name>/` subfolders: branding, narratives, townhalls, website copy |

This skill is self-contained: it does not depend on another skill being loaded for the basics. Other skills may extend these conventions for a particular vault or artifact — they build on this, they don't replace it.

**Hard rule, and the most damaging mistake available in a vault: never move or rename an existing note via a raw filesystem call.** Wikilinks resolve by filename, and only Obsidian's own rename/move updates backlinks — `mv`, `move_file`, or a script breaks every link pointing at that note, silently. Creating new files and editing content is always safe; moving and renaming are not. Everything below describes where *new* content goes. It does not license reshuffling what already exists — see "Auditing an existing vault" for a vault that predates this structure.

Filesystem access to the vault comes from **Desktop Commander** (`start_search`, `read_multiple_files`, `edit_block`, `write_file`) — a vault is a folder of Markdown files, not an API. See the plugin README for installing it.

## Before doing anything: confirm the vault root

Never assume a vault path. Confirm it with the user or by locating the `.obsidian/` folder via Desktop Commander's search — a wrong root means creating a second, orphaned structure next to the real one.

## Top-level taxonomy

One shared vault, not one vault per customer.

```
<Vault Root>/
  Customers/            # a.k.a. "Clients" — interchangeable; "Customers" is the folder name in use
    <Customer Name>/
      Organization/     # the customer's org chart + Relationships for people we work with
      Parties/          # who is working the account — us, the customer, partners
      Projects/<Project Name>/
        Contracts/
        DSU Notes/<YYYY-MM>/
        Assets/         # project-specific files, plus the index that makes them searchable
      Company Background/
      Customer Stories/ # stories about this customer's work — the source of record
      Blog/             # blog posts about this customer
      Assets/           # files that span projects, plus their index
      Resources.md
  Partners/
    <Partner Name>/
      Organization/     # org chart + per-person Relationships
      Branding/
  Practices/
    <Practice Name>/
  <Company Name>/       # the practice's own company
    Organization/       # our own org chart + per-person Relationships
    Branding/           # our branding — drives how every generated chart is styled
    Customer Stories/   # index over every customer's stories — links, not copies
    Blog/               # non-customer posts live here; customer ones are linked
    Marketing & Narrative/<Narrative Name>/
    Townhalls/
    Website Copy/<Page Name>/
    Philosophy & Background/
    Hiring/
    Resources.md
  Daily Summaries/<Year>/<Month>/
  Clippings/            # Obsidian Web Clipper's default drop folder
  Projects/             # Project Manager plugin's own store — global, flat
```

`Projects/` at vault root is the Obsidian **Project Manager** plugin's storage folder (see [[nerdynik-obsidian-project-manager-notes]] for its file format) — a sibling of `Customers/`, never nested inside a customer. It has no concept of "customer"; see "Project Manager's projects and customers" below.

## The people model

Two folder names carry the whole model. Getting them straight prevents most filing mistakes:

| Folder | Lives under | Holds |
|---|---|---|
| **`Organization/`** | Customers, Partners, `<Company Name>` | Everything about *that org's own people* — org chart in all its forms, and a `Relationships/` subfolder of per-person primary records |
| **`Parties/`** | Customers | Who is *working the account*, across every company involved — us, the customer, partners |

`Organization/` has the same shape in all three places:

```
Organization/
  Org Chart.md              # entries + the Mermaid chart
  Org Chart.drawio          # source of truth for the visual chart
  Org Chart.drawio.svg      # rendered export, embeddable in any note
  Relationships/<Person>.md # one file per person who earns one
```

A person has exactly one primary record. Everything else carries their **name and email only** and links to it.

| Person is… | Primary record |
|---|---|
| Our own staff | `<Company Name>/Organization/Relationships/<Person>` |
| A partner rep | `Partners/<Partner>/Organization/Relationships/<Person>` |
| A customer contact we actually work with | `Customers/<Customer>/Organization/Relationships/<Person>` |
| Any other customer employee | Their entry in `Customers/<Customer>/Organization/Org Chart` — a heading link, e.g. `[[Org Chart#Their Name]]` |

**The full specification is in `references/org-charts-and-relationships.md`** — who earns a relationship page, what one holds, the per-person entry format, how both charts are generated and kept in sync, branding, splitting, and the per-context differences. Read it before touching an org chart or a relationship page. The per-context deltas are summarised under Customers, Partners, and `<Company Name>` below; the reference carries the mechanics.

## Diagram tooling

Org charts are the only thing in this vault that needs diagram tooling, and all of it comes from the **`nerdynik-diagram-toolkit`** plugin, installed automatically as a dependency. It bundles three MCP servers — `mermaid`, `drawio` (hosted), and `drawio-local` — and carries the mechanics in two skills:

- **[[nerdynik-mermaid-diagrams]]** — Mermaid syntax, escaping, and validating a chart with `generate_mermaid_diagram` before it goes into a note. One bad escape silently kills the whole block in Obsidian.
- **[[nerdynik-drawio-diagrams]]** — the `.drawio` XML format, ELK layout, PNG/SVG/PDF export, and page-level editing with `set_page` so a reorg in one division doesn't rewrite the whole chart.

Read the relevant one before generating a chart. Two consequences matter enough to repeat here:

- **New files come from Desktop Commander's `write_file`.** No MCP server creates one — `set_page` only edits a `.drawio` that already exists, and the hosted `drawio` server persists nothing at all.
- **draw.io Desktop is what exports `Org Chart.drawio.svg`**, and the only thing that can. Without it, write the `.drawio`, say the export is outstanding, and don't embed a file that isn't there.

## Splitting large files

Any single-file record can outgrow one file as a company gets large. **Once a file passes roughly 500 lines, split it into logical units** rather than letting it keep growing, and leave a short pointer in the original to where the content moved. Split proactively as a file approaches the threshold, not once it's already unwieldy.

Org Charts are the usual case and have their own split rule — reporting structure in `Org Chart.md`, per-person entries in `Contact Information.md`, plus a separate per-diagram threshold. See the reference.

## Partners

For each `Partners/<Partner Name>/`:

- **`Organization/`** — everything about the partner's own people: the Org Chart in all three forms and a `Relationships/` folder. Standard shape, per the reference.
- **`Branding/`** — the partner's own branding guidelines (logos, colors, co-branding rules) needed when producing co-branded material. Create once there's material to hold, not speculatively. **This is not what charts are styled with** — those follow our own `<Company Name>/Branding/` unless the material is explicitly co-branded.

Partner deltas from the reference:

- A person earns a `Relationships/` file once there's something beyond basic contact info to say, or once they appear on a customer account team. Don't pre-populate every org-chart name as an empty file.
- Their relationship page wikilinks into `Customers/` for **every account they touch**; the DrawIO nodes list those accounts.
- Chart only the parts of the partner we actually interact with. A partner's full org is neither knowable nor useful.

## Customers

For each `Customers/<Customer Name>/`:

- **`Organization/`** — the customer's own people: the Org Chart in all three forms, and a `Relationships/` folder. Standard shape, per the reference.
- **`Parties/`** — who is working this account, across every company involved. See below.
- **`Projects/<Project Name>/`** — one folder per project. Supporting material only; Project Manager's task and milestone files live in the vault-root `Projects/`. Every project folder gets a **`Contracts/`** folder (SOWs, SOW primers, proposals, LOE/cost estimates) and a **`DSU Notes/`** folder from the start, since every project has both. Add an **`Assets/`** folder when the first file arrives, and `Meetings/`, `Deliverables/`, etc. as the project actually produces them.
- **`Company Background/`** — general information about the customer as a company: what they do, industry, HQ address. Spans projects. A brief web search to seed this is fine when the practice doesn't have it firsthand — mark anything web-sourced as unconfirmed and say where it came from.
- **`Customer Stories/`** and **`Blog/`** — stories and posts written about this customer's work. The source of record lives here; the company indexes them. See "Customer stories and blog posts".
- **`Assets/`** — files we hold *about this customer* that span projects: their brand kit, a company overview deck, a reference architecture, a data dictionary, a security questionnaire they use everywhere. See "Assets".
- **`Resources.md`** — pointers to where else this customer's information lives. See "Resource pointers".

Customer deltas from the reference:

- **`Relationships/` is for primary points of contact and people directly involved in the work** — the customer-side project team, the sponsor who actually steers scope or budget, the people we build and deliver with. **Not** people who merely attend or listen in on meetings: observers, skip-levels sitting in, rotating stakeholders. Those are captured in the Org Chart entry and in meeting attendee lists, and that's enough.
- Everyone else on the org chart is linked as `[[Org Chart#Their Name]]`. That's the normal case, not a gap.
- The chart is **partial by nature** — assembled from meetings and signature blocks, not an HR export. Mark inferred reporting lines as inferred; a confidently drawn wrong hierarchy gets repeated back to the customer.
- If someone who only attends keeps reappearing across calls, raise promoting them rather than deciding silently.

### `Parties/`

The account team, covering all three sides: **us**, the **customer**, and any **external third-party partners**.

- **`Account Team.md`** — the index. One row per individual, tracking **which projects at this customer they're on and their role on each**. This is the customer-level roll-up; the same information scoped to a single project lives in that project's team file.
- **`<Party Name>.md`** — optional per-party breakout (`Internal.md`, `<Partner Name>.md`) once a party has enough people that the index alone is hard to read. Create when earned, not up front.

Each row carries the person's name and email and **nothing more** — every other detail lives in their primary record, wikilinked. For our own staff that's `<Company Name>/Organization/Relationships/<Person>`; for partner reps, `Partners/<Partner>/Organization/Relationships/<Person>`; for customer people, their `Organization/Relationships/` page if they have one, otherwise a heading link into `Organization/Org Chart`.

A customer can run **multiple account teams at the same partner for separate divisions** simultaneously. The index must record which division/account team, not just which partner, or it can't disambiguate which applies to which project.

### Per-project team file

Inside `Customers/<Customer>/Projects/<Project Name>/`, a file listing everyone on that specific project, **grouped by which company they're part of**. Per person: name, email, Title, their Role on this project, and a wikilink to their primary record.

This is the customer-level `Parties/Account Team.md` narrowed to one project — same people, same roles, same links, just scoped. Keeping both is deliberate: the customer-level index answers "where is this person engaged across the account," and the project file answers "who is on this project."

Also record here which partner account team **and division** is engaged on this project specifically.

### `DSU Notes/`

Daily standup notes for the project, nested by month so a long engagement stays navigable:

```
DSU Notes/
  2026-08/
    11-Standup.md
    14-Blocked on VPN access.md
```

- **Month folder is `<YYYY-MM>`**, file is `<DD>-<Note Name>.md` — both zero-padded, so they sort
  chronologically. Name it for what happened when the standup was actually about something, since
  that's what makes it findable a quarter later. Several notes for one day is fine.
- **Every note needs a globally unique alias.** `11-Standup.md` is not unique across the vault and
  wikilinks resolve by filename alone, so give each note the canonical long form
  `<Customer Abbrev> - <Project> DSU <YYYY-MM-DD>` as its `title` and first alias, and link to that.
  Without it the chain between consecutive standups silently rots.
- **One recording, several projects → one note each**, citing the same recording and linking the
  siblings. Never one multi-project note.

Keep DSUs here, not in `Daily Summaries/`: a daily summary covers the *user's whole day* across every
project, a DSU covers *one project* and is read by its team. Cross-link them.

**The full specification is in `references/dsu-notes.md`** — frontmatter, the provenance block
(invite, roster, actual start time, recording identifier, heard vs. not heard), the section set,
severity markers, action-item format, the transcription-flag discipline that makes these notes
trustworthy, post-standup updates, and migrating standups written before this layout. Read it before
writing one.
### Assets

Files we hold rather than notes we wrote — decks, PDFs, spreadsheets, sample data, screenshots. Two
folders, split the same way `Resources.md` is:

| Folder | Holds |
|---|---|
| `Customers/<Customer>/Assets/` | Material about the customer that **spans projects** |
| `Customers/<Customer>/Projects/<Project>/Assets/` | Material **specific to one project** |

Create either when the first file arrives, not preemptively. Each folder carries one Markdown index
named for its scope (`Acme Corp Assets.md`), and that index is the point: **vault search can't read a
PDF, a `.pptx`, or an `.xlsx`**, so the entry is the only searchable surface those files have.

`Resources.md` and `Assets/` are opposites — `Resources.md` points *outward* at systems we don't
hold; `Assets/` holds the files themselves.

**The full specification is in `references/assets.md`** — the index entry format and what has to go
in it, provenance and superseded assets, renaming screenshots and other uselessly-named files on the
way in, and what belongs elsewhere. Read it before filing an asset.

### Resource pointers

`Resources.md` at the customer level, and another inside each project folder, hold pointers to where information about this customer or project lives **outside the vault** — the things you'd need for cross-referencing, lookups, and status updates:

- **Chat** — Slack and Teams channels and group chats used for the customer or the project, ours and any shared/Connect channels
- **Internal wikis and documentation sites** — SharePoint sites and pages, Confluence spaces, Notion, Google Sites, or whatever the customer or the engagement documents itself in. Record the space or site key alongside the URL; a Confluence space key and a SharePoint site path are what make the content findable through search and connectors, not just clickable.
- **Git repositories** — every repo associated with the work: ours, the customer's, and any shared fork. Per repo, record the host (GitHub, GitLab, Azure DevOps, Bitbucket), the `owner/repo` path or clone URL, the default branch, what it contains, and **who grants access** — an unreachable repo discovered mid-engagement is a delay, and the access owner is the part nobody writes down.
- **Document stores** — shared drives, document libraries, deliverable repositories
- **Ticketing, CI, and environments** — issue trackers, pipelines, and environment URLs relevant to the engagement
- Any customer-side portal or system we've been given access to

Record the human-readable name, the link or identifier, and one line on what it's used for. Note where access is customer-granted rather than ours, since that's what has to be re-requested when someone rolls onto the project.

Customer-level holds what spans projects; project-level holds what's specific to that project. Don't duplicate — a project's `Resources.md` links up to the customer's for the shared ones. A wiki space or a repo that serves the whole account belongs at the customer level even if only one project uses it today.

## Customer stories and blog posts

**Customer story, user story, use case, case study — all the same artifact**, and the vault uses
`Customer Stories` for all of them.

A story is always *about* a customer's projects and always *an asset of* the company, so the vault
splits along that difference:

| | Lives at |
|---|---|
| **The story itself** | `Customers/<Customer>/Customer Stories/<Customer> - <Title>.md` |
| **The catalogue** | `<Company Name>/Customer Stories/` — links and status, never a second copy |

Stories sit at customer level, not project level, because one routinely spans several projects.
Blog posts about a named customer are filed the same way; every other post lives directly in
`<Company Name>/Blog/`.

**The full specification is in `references/customer-stories-and-blog.md`** — the split and why it
exists, blog handling, the four tag axes (industries, cloud, practices, partners) and where their
permitted values come from, the `status` ladder and the customer-permission question behind it, and
what links to what. Read it before writing or cataloguing one.

## Practices

A practice can directly target a specific partner — e.g. a Databricks-focused practice, and Databricks itself as a partner. These stay separate:

- **`Partners/<Partner Name>/`** — information about the partner *as an organization*: org chart, contacts, whatever's true of the relationship regardless of which practice touches them.
- **`Practices/<Practice Name>/`** — information about *building and running the practice itself*: methodology, enablement, certifications, playbooks, roadmap.

When a practice is built around a partner, wikilink the two rather than duplicating. Not every practice maps to a partner, so only add the link when it applies.

### Common practice-level folders

Create under `Practices/<Practice Name>/` as needed, not all up front:

- **`Case Studies/`** — an index of the customer stories this practice delivered, plus summary references to any published elsewhere. "Case study" is the same artifact as a customer story, so this folder **links** to `Customers/<Customer>/Customer Stories/` rather than holding a second copy. See "Customer stories and blog posts".
- **`COE/`** — Center of Excellence material: portal page copy, plus the documents and findings behind building and maintaining the CoE.
- **`Website Copy/<Page Name>/`** — copy for public-facing pages about that practice, one folder per page, same structure as the company-level `Website Copy/` described below. Wikilink between the two where content overlaps rather than duplicating prose.
- **`Hiring/`** — hiring handbooks, repeatable interviewer questions, take-home or live exams specific to this practice. Wikilink to the company-level `Hiring/` for anything not practice-specific.
- **`Training/`** — exam info, lessons, learning academies, learning plans and journeys.

## `<Company Name>`

The company owns the practices and partnerships underneath it. Maintain wikilinks out to each `Practices/<Practice>/` and `Partners/<Partner>/` — this folder is an index/MOC over them, not a duplicate.

### `Organization/`

Our own org chart and our own people, the same shape as a customer's or a partner's — `Org Chart.md`, `Org Chart.drawio`, `Org Chart.drawio.svg`, and `Relationships/`. Per the reference.

Our deltas:

- **Who earns a `Relationships/` file:** anyone **attached to a customer project**, and anyone **important within the company** regardless of project work (executives, VPs, practice leads). Not every employee.
- Their page wikilinks to every `Customers/<Customer>/` and project they're engaged on, and the DrawIO nodes list those projects.
- This is the one chart expected to be **complete** — it's ours, and we have the HR system.

**Everywhere else refers to these files instead of duplicating.** A customer's `Parties/Account Team.md` and a project's team file carry a person's **name and email only** — every other detail is one wikilink away. When someone changes role, phone number, or Slack handle, exactly one file changes.

That means an internal staff member appears in at least three places: their primary record here, the customer-level index of which projects they're on with their role on each, and the per-project team file for each project.

### The rest of `<Company Name>/`

`Branding/`, `Customer Stories/` and `Blog/`, `Marketing & Narrative/`, `Townhalls/`,
`Website Copy/`, `Philosophy & Background/`, and the company-level `Resources.md` are each specified
in **`references/company-folder.md`**. Two of them have effects outside their own folder and are
worth knowing without opening it:

- **`Branding/`** styles *every* org chart the vault generates, for customers and partners as much
  as for us. Check it before generating a chart.
- **`Customer Stories/` and `Blog/`** are catalogues over material that lives in the customer
  folders — links, never copies. See "Customer stories and blog posts".

### The vault is not the whole picture

A company commonly keeps information about its customers, projects, practices, and partnerships in other systems — Microsoft 365/Teams, Google Docs, Slack. Don't assume the vault is complete. When starting substantive work (onboarding, background research, filling gaps) and it's unclear whether the vault has full context, **ask what other locations or connectors the company maintains**. Check `Resources.md` files first — company-level and customer-level — since they exist precisely to answer this. Ask once per topic or engagement, not on every small edit.

## Daily Summaries

`Daily Summaries/<Year>/<Month>/` with one file per day.

```
Daily Summaries/
  2026/
    08/
      2026-08-11.md
```

Zero-padded numeric months so folders sort chronologically. Full ISO date in the filename so a summary is unambiguous when linked from anywhere else in the vault.

A daily summary digests meeting recordings and calendar entries into action items, findings, a project breakdown, and a rough hour-by-hour schedule usable for time tracking.

**The full section-by-section specification and template is in `references/daily-summaries.md`.** Read it before creating or updating a daily summary — the section set is fixed, and the call/calendar reconciliation rules are specific.

## Clippings

`Clippings/` at vault root is the default drop folder for the **Obsidian Web Clipper** browser extension (Firefox and Chrome). The extension creates it automatically on first clip; don't create it preemptively, and don't rename it, since the extension writes to a configured path.

Treat it as an **inbox, not a destination.** Clips arrive unsorted, and the extension writes frontmatter worth preserving — source URL, author, published date, clipped date. That provenance is the main value of a clipping over a copy-paste.

Triage rules:

- A clipping that's **reference material for a specific customer, partner, practice, or project** should end up in that folder. Because of the hard rule on moves, either ask the user to move it inside Obsidian, or leave it in place and wikilink to it from the destination note. Never move it with a raw filesystem call.
- A clipping that's **source material for something being written** — a narrative, a website page, a case study — stays in `Clippings/` and gets wikilinked from the work in progress. It's a citation, and citations don't need to be relocated.
- A clipping with **no lasting purpose** is a deletion candidate. Propose it; don't delete unilaterally.

When summarizing or citing a clipping, carry its source URL through. A clipping that loses its provenance is worth less than the original link.

## Cross-linking model

The same person or relationship stays visible from multiple angles via wikilinks, never by duplicating substance:

- `<Company Name>/Organization/Relationships/<Person>` → wikilinks to every customer and project they're engaged on.
- `Partners/<Partner>/Organization/Relationships/<Person>` → wikilinks to every customer account they touch.
- `Customers/<Customer>/Organization/Relationships/<Person>` → wikilinks to the projects they're involved in and to the account team entry.
- `Customers/<Customer>/Parties/Account Team` → wikilinks to each person's primary record, and records their projects and roles at this customer.
- `Customers/<Customer>/Projects/<Project>/` team file → wikilinks to each person's primary record, scoped to this project.
- `Customers/<Customer>/Organization/Org Chart` → the heading targets that links resolve against for everyone without a relationship page.
- `<Company Name>/` → wikilinks to every `Practices/<Practice>/` and `Partners/<Partner>/` it owns.
- `Customers/<Customer>/Customer Stories/<Story>` → wikilinks to the customer, its projects, the practices and partners involved, and the published page; `<Company Name>/Customer Stories/` and `Practices/<Practice>/Case Studies/` both link *in* to it and never copy it.
- `Assets/<scope> Assets` → each entry links to the notes that asset informs, and a project's index links up to the customer-level one. The assets themselves are unsearchable, so this index is their only route into the link graph.
- `Resources.md` files → outward to systems beyond the vault; no reciprocal link exists, so these must be kept current deliberately.

When adding a person to one side, check whether the other side needs the reciprocal link. These are meant to stay two-way.

**Links inside a Mermaid chart don't count.** Obsidian doesn't register them as links — no backlinks, no graph view, no Outgoing Links — which is why every chart is followed by a plain wikilink index of the people in it. Without that index the relationship pages are orphans.

## Project Manager's projects and customers

Project Manager has no "customer" concept and stores every project flat in the vault-root `Projects/` folder (see [[nerdynik-obsidian-project-manager-notes]] for the file format). This practice disambiguates via a **naming convention on the project title**: `<Customer Abbreviation> - <Project Name>`. Follow it for new projects rather than introducing a custom field or tag.

The customer's `Projects/<Project Name>/` folder and the Project Manager project note are two different things about the same project — cross-link them rather than duplicating plan data into the customer-side folder.

## Naming conventions

- Customer, partner, and person names use normal display casing and spaces (`Acme Corp`). Avoid characters wikilinks treat specially: `# | ^ : \ [ ]`.
- Keep these folder and file names spelled **identically everywhere** — agents and Dataview/Bases queries look for these exact strings:

  `Organization`, `Parties`, `Relationships`, `Org Chart`, `Org Chart.drawio`, `Org Chart.drawio.svg`, `Contact Information`, `Account Team`, `Branding`, `Company Background`, `Philosophy & Background`, `Projects`, `Contracts`, `DSU Notes`, `Assets`, `Customer Stories`, `Blog`, `Resources.md`, `Case Studies`, `COE`, `Website Copy`, `Hiring`, `Training`, `Marketing & Narrative`, `Townhalls`, `Daily Summaries`, `Clippings`

- A relationship page is named for the person exactly as the Org Chart names them (`Jane Doe.md`), so `[[Jane Doe]]` resolves from anywhere without an alias.

- **Assets are named for their content**, never left on a tool's default name, with an ISO date appended when the file is a claim about a moment (`Admin Console Retention Settings 2026-09-11.png`). Rename on the way in — see "Assets".

- Dated files use ISO `YYYY-MM-DD` so they sort chronologically: `2026-08-11.md`, `2026-08-11 Townhall.md`. The exception is `DSU Notes/`, where the month lives in the folder name (`2026-08/`) and the file carries a zero-padded day prefix (`11-Standup.md`) — same chronological sort, less repetition. **That filename isn't vault-unique, so a DSU note must carry its canonical long form (`<Customer Abbrev> - <Project> DSU <YYYY-MM-DD>`) as `title` and first alias** and be linked by that, never by the bare filename.

## Playbooks

### Onboarding a new customer
1. Create `Customers/<Customer Name>/` with `Organization/`, `Parties/`, `Projects/`, `Company Background/`, and `Resources.md`.
2. Inside `Organization/`, create `Org Chart.md` and an empty `Relationships/`. Create `Account Team.md` inside `Parties/`.
3. Populate the Org Chart entries from what's known, then generate the Mermaid chart and the wikilink index, and `Org Chart.drawio` / `Org Chart.drawio.svg` — per the reference. A one-person chart is still worth generating; it's the shape everything else gets added to.
4. Add a `Relationships/` page for each primary contact and anyone already known to be directly involved in the work. Not attendees.
5. Populate `Company Background/` — from what the practice already knows first; a brief web search for general company/industry/HQ facts only when that's missing, marked as web-sourced.
6. Fill `Resources.md` with the Slack/Teams channels, wiki spaces, Git repos, and any other systems already in use for this customer.
6a. If material about the customer already exists — a brand kit, an overview deck, an architecture they sent — create `Assets/` with its index (`<Customer> Assets.md`) and record each file's provenance and contents. Skip the folder entirely if there's nothing yet.
7. If the account came in through a partner, add the partner-side people to `Parties/Account Team.md` now, wikilinked to their `Partners/<Partner>/Organization/Relationships/` files, with the reciprocal link added on their side.
8. Add our own staff to `Parties/Account Team.md` with their projects and roles, wikilinked to `<Company Name>/Organization/Relationships/`. Create any missing relationship file.

### Onboarding a new partner
1. Create `Partners/<Partner Name>/Organization/` with `Org Chart.md`, its generated `Org Chart.drawio` / `Org Chart.drawio.svg`, and an adjacent `Relationships/` folder.
2. Create a person's `Relationships/` file only once there's something beyond basic contact info, or once they appear on a customer account team.
3. Add `Branding/` only when there's actual co-branded material to hold — it is not what the charts are styled with.

### Starting a new project for an existing customer
1. Create `Customers/<Customer>/Projects/<Project Name>/` with its team file, a `Contracts/` folder, a `DSU Notes/` folder, and `Resources.md`.
2. Create the actual Project Manager project (title prefixed with the customer abbreviation), not a hand-authored lookalike.
3. Cross-link the two.
4. Populate the team file — each person's name, email, title, project role, and a wikilink to their primary record. Record which partner account team and division is engaged.
5. Add each internal person's project and role to the customer-level `Parties/Account Team.md` too.
6. File any SOW, primer, proposal, or LOE already in hand into `Contracts/`. Anything else handed over at kickoff — requirements, sample data, diagrams — goes to `Assets/` with an index entry each, not loose in the project folder.
7. Record the project's Slack/Teams channels, wiki spaces, and Git repos in its `Resources.md`, noting who grants access to each.
8. Add a `Relationships/` page under `Customers/<Customer>/Organization/` for any customer-side person on the project team who doesn't have one, and add the project to the `Projects` line of everyone's Org Chart entry. Regenerate both charts.

### Adding an internal staff member to a project
1. Does `<Company Name>/Organization/Relationships/<Person>` exist? If not, create it with contact info and the LinkedIn/Teams/Slack quick links, and add their entry to our Org Chart.
2. Add them to the project's team file — name, email, title, role, wikilink to their record.
3. Add or update their row in `Customers/<Customer>/Parties/Account Team.md`, listing this project and their role on it.
4. Add the reciprocal wikilink from their relationship file to the customer and project.
5. Add the project to their Org Chart entry and regenerate our `Org Chart.drawio` / `.drawio.svg` — the project list on the DrawIO nodes is now stale otherwise.

### Filing a piece of content ("where does X go?")
1. Plan or schedule data (task, milestone, project record)? → Project Manager's store (vault-root `Projects/`).
2. A web clipping? → stays in `Clippings/`; wikilink to it from wherever it's used. See "Clippings".
3. A contractual document for a specific project? → `Customers/<Customer>/Projects/<Project>/Contracts/`.
4. A pointer to a system outside the vault? → the nearest `Resources.md` — project, customer, or company. We hold the file itself? → the nearest `Assets/`, with an index entry, per "Assets".
5. A daily standup for a project? → `Customers/<Customer>/Projects/<Project>/DSU Notes/<YYYY-MM>/<DD>-<Name>.md`. The user's whole day across projects goes to `Daily Summaries/` instead.
6. A customer story, use case, or case study — all the same thing? → `Customers/<Customer>/Customer Stories/<Customer> - <Title>.md`, indexed from `<Company Name>/Customer Stories/`. A blog post about a named customer goes the same way into `Customers/<Customer>/Blog/`; every other post lives in `<Company Name>/Blog/`.
7. About one specific project otherwise? → `Customers/<Customer>/Projects/<Project>/`.
8. About a person? → their primary record (see "The people model"), never a second copy. No primary record and they're only an attendee? → nothing to file beyond the org chart entry.
   8a. A reporting-line, title, or org change? → the Org Chart entry, then regenerate both charts.
9. About the customer relationship broadly? → `Customers/<Customer>/` — `Organization/`, `Parties/`, or `Company Background/`.
10. About a partner as an organization? → `Partners/<Partner>/Organization/` or `Branding/`.
11. About building or running a practice? → `Practices/<Practice>/`.
12. About a specific day's activity? → `Daily Summaries/<Year>/<Month>/<date>.md`.
13. About the company itself? → `<Company Name>/` — the matching subfolder, or `Resources.md` if it's a pointer.

### Auditing an existing vault for drift
This taxonomy is the target, not necessarily what's on disk. A vault built up organically — or one that predates the `Organization/` + `Parties/` structure, or that still keeps its org chart as ASCII art — will only partially follow it.

1. Search each `Customers/<Name>/` and `Partners/<Name>/` against the expected shape: Is everything about that org's people inside `Organization/` — chart and `Relationships/` both — or still scattered at the folder's top level? Does the customer have `Parties/` with an `Account Team.md`? Does each project folder have `Contracts/`, `DSU Notes/`, and `Resources.md`? Is the org chart split once past ~500 lines?
2. Check the people model for duplication: contact details restated in an account team or project file instead of wikilinked to a primary record. That's the drift that costs the most later, because every copy ages independently.
3. **Check the three org-chart artifacts against each other.** For each `Organization/`: does `Org Chart.md` still carry an ASCII or indented-text chart instead of Mermaid? Do `Org Chart.drawio` and `Org Chart.drawio.svg` exist, and does every person in the entries appear in both charts with the same title and email? Is a `.drawio.svg` embedded somewhere but older than its `.drawio`? A chart that disagrees with the entries is the highest-value finding here, because it reads as current.
4. **Check `Assets/` against its index.** Are there binaries sitting loose in a customer or project folder instead of in `Assets/`? Does every file in `Assets/` have an entry, and does every entry still point at a file that exists? Do the entries record provenance and contents, or just restate filenames — the last case is the common one, and it means the assets are still effectively invisible to search. Is project-specific material sitting at customer level, or account-wide material duplicated into several projects? **Search for default names** — `Screenshot `, `Screen Shot `, `Pasted image `, `IMG_`, `image.png`, `Untitled` — they're the fastest signal that assets were filed without being described. Renaming those is a rename, so flag them rather than fixing them; doing it inside Obsidian updates the index's link automatically, which makes it a cheap job for the user.
5. **Check customer stories and blog posts.** Is any story's prose duplicated into `<Company Name>/Customer Stories/` or a practice's `Case Studies/` instead of linked — and if so, have the copies already diverged? Does every story carry the four tag axes, with values drawn from the company's own lists rather than coined locally? Does anything marked `approved-external` or `published` record who approved being named and when? An unsourced external approval is the highest-risk finding here, because it's the one that reaches the customer. Are customer-specific blog posts sitting in `<Company Name>/Blog/` instead of the customer's folder?
6. **Check `DSU Notes/` for the layout and the alias.** Are standups nested under `<YYYY-MM>/`, or still flat in the project folder (or in `Meetings/`)? Does each note carry its canonical long-form alias, and does the previous/next chain between consecutive standups actually resolve? A DSU with no alias is reachable only by path, and it's the link chain that breaks first. Moving existing notes is a move and a rename — flag it, per step 10, and add the aliases before anything moves.
7. Check `Relationships/` against the gate: pages for people who only attend meetings, or empty stubs created preemptively — both make "has a page" stop meaning anything. And the reverse: someone showing up repeatedly in account teams and project files with no page at all.
8. Check `<Company Name>/` for the newer folders — `Organization/` with `Relationships/` inside it, `Branding/`, `Customer Stories/`, `Blog/`, `Marketing & Narrative/` broken out per narrative, `Townhalls/`, per-page `Website Copy/`, `Philosophy & Background/`, `Resources.md`.
9. Check `Resources.md` files for the categories added later: wiki spaces (SharePoint, Confluence) with their site path or space key, and Git repos with their host, path, and access owner.
10. **Flag, don't silently fix, anything requiring a move or rename.** Relocating an existing Org Chart into `Organization/`, or moving `<Company Name>/Relationships/` under a new `<Company Name>/Organization/`, are exactly this case: propose them, and let the user execute the move inside Obsidian. If they ask you to do it, warn which notes' backlinks may break first and offer to search-and-repair `[[links]]` afterward.
11. Content-only fixes — adding a missing `Account Team.md`, filling an empty `Company Background/`, adding a missing reciprocal wikilink, creating a `Resources.md`, generating a missing chart from entries that already exist — are safe to make directly with `edit_block`/`write_file`.

Report findings with counts and one concrete example each, and lead with the duplication and disagreement problems: a structure that's merely in the wrong folder still works, while a contact detail copied into four files is already wrong in at least three, and an org chart that contradicts its own entries is wrong in front of a customer.
