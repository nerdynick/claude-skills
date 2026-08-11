---
name: nerdynik-obsidian-vault-organization
description: Use when creating, filing, or auditing notes and folders in a Professional Services / C&SI / SI Obsidian vault — also referred to as the vault, KB, knowledge base, notes, or Obsidian notes — including onboarding a customer or partner, starting a project, deciding where a contact / org chart / background / web clipping belongs, writing or updating a daily summary, recording a townhall or narrative, or reviewing an existing vault for drift from convention. Defines the canonical Customers / Partners / Practices / Company / Daily Summaries taxonomy, the Organization + Parties + Relationships model for tracking people, and how it all interacts with the Project Manager plugin's own storage.
---

# Obsidian PS Vault Organization

Keeps customer, partner, practice, and company content in a consistent place across a Professional Services / C&SI / SI practice's Obsidian vault, so both humans and an agent can predict where something lives without re-deriving structure each time.

Users call this vault different things — *the vault*, *the KB*, *the knowledge base*, *my notes*, *Obsidian notes*. They all mean the same thing; this skill applies regardless of which term is used.

**Builds on Desktop Commander's `obsidian-vault` skill** (see the plugin README) for everything mechanical — wikilinks, frontmatter/property conventions, MOCs, dashboards. This skill only adds the customer/partner/practice-specific *taxonomy* on top of that base. It does not restate wikilink or property mechanics; assume that skill's rules apply everywhere below.

**Hard rule inherited from that base skill: never move or rename an existing note via a raw filesystem call.** Wikilinks resolve by filename, and only Obsidian's own rename/move updates backlinks. Everything below describes where *new* content goes. It does not license reshuffling what already exists — see "Auditing an existing vault" for handling a vault that predates this structure.

## Before doing anything: confirm the vault root

Never assume a vault path. Confirm it with the user or by locating the `.obsidian/` folder via Desktop Commander's search — a wrong root means creating a second, orphaned structure next to the real one.

## Top-level taxonomy

One shared vault, not one vault per customer.

```
<Vault Root>/
  Customers/            # a.k.a. "Clients" — interchangeable; "Customers" is the folder name in use
    <Customer Name>/
      Organization/     # the customer's own org charts
      Parties/          # who is working the account — us, the customer, partners
      Projects/<Project Name>/
      Company Background/
      Resources.md
  Partners/
    <Partner Name>/
      Organization/     # org chart + per-person Relationships
      Branding/
  Practices/
    <Practice Name>/
  <Company Name>/       # the practice's own company
    Relationships/      # our own people — the primary record for each
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

Three folder names carry the whole model. Getting them straight prevents most filing mistakes:

| Folder | Lives under | Holds |
|---|---|---|
| **`Organization/`** | Customers, Partners | That org's own structure — org chart, reporting lines, their employees |
| **`Parties/`** | Customers | Who is *working the account*, across every company involved — us, the customer, partners |
| **`Relationships/`** | Partners, `<Company Name>` | One file per person, the **primary record** for that individual |

A person has exactly one primary record. Everything else links to it rather than restating it.

| Person is… | Primary record |
|---|---|
| Our own staff | `<Company Name>/Relationships/<Person>` |
| A partner rep | `Partners/<Partner>/Organization/Relationships/<Person>` |
| A customer employee | Their entry in `Customers/<Customer>/Organization/Org Chart` — a heading/block link, e.g. `[[Org Chart#Their Name]]` |

Customer employees get no per-person file. If one genuinely warrants that depth, raise it rather than inventing a `Relationships/` folder under a customer — that would collide with the `Parties/` model.

## Splitting large files

Any single-file record (most often an Org Chart) can outgrow one file as a company gets large. **Once a file passes roughly 500 lines, split it into logical units** rather than letting it keep growing — for an Org Chart, the natural split is the reporting structure in one file and per-person contact information in another (`Org Chart.md` + `Contact Information.md`, both inside `Organization/`). Leave a short pointer in the original to where the content moved. Split proactively as a file approaches the threshold, not once it's already unwieldy.

When an Org Chart has been split, per-person heading links resolve against `Contact Information` instead — so whichever file holds contact info needs one heading or block per person.

## Partners

For each `Partners/<Partner Name>/`:

- **`Organization/`** — everything about the partner as an organization:
  - **`Org Chart`** — contact info and reporting structure for each individual: Title, Email, Phone, who they report to. Split per the rule above once it grows.
  - **`Relationships/`** — one file per person. Each file repeats that person's basic contact info (so it stands alone), adds the detail that doesn't belong in an org chart (relationship history, preferences, working notes), and wikilinks into `Customers/` for every account they touch.
- **`Branding/`** — the partner's own branding guidelines (logos, colors, co-branding rules) needed when producing co-branded material. Create once there's material to hold, not speculatively.

Only create a person's `Relationships/` file once there's something beyond basic contact info to say, or once they appear on a customer account team. Don't pre-populate every org-chart name as an empty file.

## Customers

For each `Customers/<Customer Name>/`:

- **`Organization/`** — the customer's own **Org Chart** (Title, Email, Phone, reporting structure), same shape and splitting rule as a partner's. No `Relationships/` here; per-person depth for customer staff isn't part of the model.
- **`Parties/`** — who is working this account, across every company involved. See below.
- **`Projects/<Project Name>/`** — one folder per project. Supporting material only; Project Manager's task and milestone files live in the vault-root `Projects/`. Every project folder gets a **`Contracts/`** folder (SOWs, SOW primers, proposals, LOE/cost estimates) from the start, since every project has these. Add `Meetings/`, `Deliverables/`, etc. as the project actually produces them.
- **`Company Background/`** — general information about the customer as a company: what they do, industry, HQ address. Spans projects. A brief web search to seed this is fine when the practice doesn't have it firsthand — mark anything web-sourced as unconfirmed and say where it came from.
- **`Resources.md`** — pointers to where else this customer's information lives. See "Resource pointers".

### `Parties/`

The account team, covering all three sides: **us**, the **customer**, and any **external third-party partners**.

- **`Account Team.md`** — the index. One row per individual, tracking **which projects at this customer they're on and their role on each**. This is the customer-level roll-up; the same information scoped to a single project lives in that project's team file.
- **`<Party Name>.md`** — optional per-party breakout (`Internal.md`, `<Partner Name>.md`) once a party has enough people that the index alone is hard to read. Create when earned, not up front.

Each row carries the person's name and email and **nothing more** — every other detail lives in their primary record, wikilinked. For our own staff that's `<Company Name>/Relationships/<Person>`; for partner reps, `Partners/<Partner>/Organization/Relationships/<Person>`; for customer employees, a heading link into `Organization/Org Chart`.

A customer can run **multiple account teams at the same partner for separate divisions** simultaneously. The index must record which division/account team, not just which partner, or it can't disambiguate which applies to which project.

### Per-project team file

Inside `Customers/<Customer>/Projects/<Project Name>/`, a file listing everyone on that specific project, **grouped by which company they're part of**. Per person: name, email, Title, their Role on this project, and a wikilink to their primary record.

This is the customer-level `Parties/Account Team.md` narrowed to one project — same people, same roles, same links, just scoped. Keeping both is deliberate: the customer-level index answers "where is this person engaged across the account," and the project file answers "who is on this project."

Also record here which partner account team **and division** is engaged on this project specifically.

### Resource pointers

`Resources.md` at the customer level, and another inside each project folder, hold pointers to where information about this customer or project lives **outside the vault** — the things you'd need for cross-referencing, lookups, and status updates:

- Slack and Teams channels and group chats used for the customer or the project
- SharePoint sites, shared drives, document libraries
- Ticketing, CI, or environment links relevant to the engagement
- Any customer-side portal or system we've been given access to

Record the human-readable name, the link or channel ID, and one line on what it's used for. Customer-level holds what spans projects; project-level holds what's specific to that project. Don't duplicate — a project's `Resources.md` links up to the customer's for the shared ones.

## Practices

A practice can directly target a specific partner — e.g. a Databricks-focused practice, and Databricks itself as a partner. These stay separate:

- **`Partners/<Partner Name>/`** — information about the partner *as an organization*: org chart, contacts, whatever's true of the relationship regardless of which practice touches them.
- **`Practices/<Practice Name>/`** — information about *building and running the practice itself*: methodology, enablement, certifications, playbooks, roadmap.

When a practice is built around a partner, wikilink the two rather than duplicating. Not every practice maps to a partner, so only add the link when it applies.

### Common practice-level folders

Create under `Practices/<Practice Name>/` as needed, not all up front:

- **`Case Studies/`** — case studies the company developed, or summary references to ones published elsewhere.
- **`COE/`** — Center of Excellence material: portal page copy, plus the documents and findings behind building and maintaining the CoE.
- **`Website Copy/<Page Name>/`** — copy for public-facing pages about that practice, one folder per page, same structure as the company-level `Website Copy/` described below. Wikilink between the two where content overlaps rather than duplicating prose.
- **`Hiring/`** — hiring handbooks, repeatable interviewer questions, take-home or live exams specific to this practice. Wikilink to the company-level `Hiring/` for anything not practice-specific.
- **`Training/`** — exam info, lessons, learning academies, learning plans and journeys.

## `<Company Name>`

The company owns the practices and partnerships underneath it. Maintain wikilinks out to each `Practices/<Practice>/` and `Partners/<Partner>/` — this folder is an index/MOC over them, not a duplicate.

### `Relationships/`

One file per person, the **primary record** for our own staff — same pattern as a partner's `Relationships/`, applied internally.

Who gets a file: anyone **attached to a customer project**, and anyone **important within the company** regardless of project work (executives, VPs). Not every employee.

Each file holds:

- Known contact information — email, phone, office/region
- **Quick links for discovering more about the person**: LinkedIn profile, Teams profile/chat link, Slack member link, internal directory entry
- Role, practice affiliation, and areas of expertise
- Wikilinks to every `Customers/<Customer>/` and project they're engaged on

**Everywhere else refers to this file instead of duplicating.** A customer's `Parties/Account Team.md` and a project's team file carry a person's **name and email only** — every other detail is one wikilink away. When someone changes role, phone number, or Slack handle, exactly one file changes.

That means an internal staff member appears in at least three places: their primary record here, the customer-level index of which projects they're on with their role on each, and the per-project team file for each project.

### `Marketing & Narrative/`

**One folder per narrative**, not one shared folder holding everything:

```
Marketing & Narrative/
  <Narrative Name>/
    ...research, drafts, supporting material for that narrative
```

Each narrative's research, positioning work, drafts, and supporting material stay together in its own folder. A single flat folder mixing several narratives makes it impossible to tell which research belongs to which — and narratives get revisited, so this matters over time.

### `Townhalls/`

Company All Hands. **One file per townhall**, named by date so they sort chronologically: `<YYYY-MM-DD> Townhall.md`.

Each file tracks the whole lifecycle, not just the recap:

- **Leading up to it** — agenda, topics expected, questions to raise. If the user is **presenting**, this is where their material, talking points, demo notes, and rehearsal feedback live. This is the part that's most often needed and most often lost.
- **The meeting itself** — findings, announcements, decisions, notable Q&A.
- **Summary** — what was covered, what changed, and any action items, wikilinked out to wherever they're tracked.

Create the file when the townhall is announced, not after it happens — the pre-meeting material is half its value.

### `Website Copy/`

**One folder per page of copy**:

```
Website Copy/
  <Page Name>/
    ...the copy itself
    ...supporting assets, or an index pointing to them
```

Each page folder holds its copy and the supporting assets that copy needs. When an asset isn't held in the vault — already live on a public website, or delivered separately — record it in an **index file in that page's folder** giving the asset name, where it lives, and how to get it. An asset that exists only as "someone sent it over once" is the thing that stalls a page revision a year later.

Practice-level `Website Copy/` folders follow the same per-page structure; wikilink between the two where a page spans both.

### `Philosophy & Background/`

Company philosophy and company background together in one folder — mission, values, operating principles, history, founding story, positioning. These are read together and cite each other constantly, which is why they share a folder rather than sitting apart.

Distinct from a customer's `Company Background/`, which is about *that customer*.

### `Resources.md`

A **single file** of pointers and lookup information for common company resources. Not a folder — one file people can scan:

- SharePoint sites
- Wikis and internal documentation
- Teams channels
- Slack channels and workspaces
- Shared drives, HR and expense systems, other internal tooling

For each: the name, the link or identifier, and one line on what it's for. This is the first place to look when the question is "where does the company keep X."

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

- `<Company Name>/Relationships/<Person>` → wikilinks to every customer and project they're engaged on.
- `Partners/<Partner>/Organization/Relationships/<Person>` → wikilinks to every customer account they touch.
- `Customers/<Customer>/Parties/Account Team` → wikilinks to each person's primary record, and records their projects and roles at this customer.
- `Customers/<Customer>/Projects/<Project>/` team file → wikilinks to each person's primary record, scoped to this project.
- `Customers/<Customer>/Organization/Org Chart` → the heading targets that customer-employee links resolve against.
- `<Company Name>/` → wikilinks to every `Practices/<Practice>/` and `Partners/<Partner>/` it owns.
- `Resources.md` files → outward to systems beyond the vault; no reciprocal link exists, so these must be kept current deliberately.

When adding a person to one side, check whether the other side needs the reciprocal link. These are meant to stay two-way.

## Project Manager's projects and customers

Project Manager has no "customer" concept and stores every project flat in the vault-root `Projects/` folder (see [[nerdynik-obsidian-project-manager-notes]] for the file format). This practice disambiguates via a **naming convention on the project title**: `<Customer Abbreviation> - <Project Name>`. Follow it for new projects rather than introducing a custom field or tag.

The customer's `Projects/<Project Name>/` folder and the Project Manager project note are two different things about the same project — cross-link them rather than duplicating plan data into the customer-side folder.

## Naming conventions

- Customer, partner, and person names use normal display casing and spaces (`Acme Corp`). Avoid characters wikilinks treat specially: `# | ^ : \ [ ]`.
- Keep these folder and file names spelled **identically everywhere** — agents and Dataview/Bases queries look for these exact strings:

  `Organization`, `Parties`, `Relationships`, `Org Chart`, `Contact Information`, `Account Team`, `Branding`, `Company Background`, `Philosophy & Background`, `Projects`, `Contracts`, `Resources.md`, `Case Studies`, `COE`, `Website Copy`, `Hiring`, `Training`, `Marketing & Narrative`, `Townhalls`, `Daily Summaries`, `Clippings`

- Dated files use ISO `YYYY-MM-DD` so they sort chronologically: `2026-08-11.md`, `2026-08-11 Townhall.md`.

## Playbooks

### Onboarding a new customer
1. Create `Customers/<Customer Name>/` with `Organization/`, `Parties/`, `Projects/`, `Company Background/`, and `Resources.md`.
2. Create the Org Chart inside `Organization/` and `Account Team.md` inside `Parties/`.
3. Populate `Company Background/` — from what the practice already knows first; a brief web search for general company/industry/HQ facts only when that's missing, marked as web-sourced.
4. Fill `Resources.md` with the Slack/Teams channels and any other systems already in use for this customer.
5. If the account came in through a partner, add the partner-side people to `Parties/Account Team.md` now, wikilinked to their `Partners/<Partner>/Organization/Relationships/` files, with the reciprocal link added on their side.
6. Add our own staff to `Parties/Account Team.md` with their projects and roles, wikilinked to `<Company Name>/Relationships/`. Create any missing relationship file.

### Onboarding a new partner
1. Create `Partners/<Partner Name>/Organization/` with an Org Chart and an adjacent `Relationships/` folder.
2. Create a person's `Relationships/` file only once there's something beyond basic contact info, or once they appear on a customer account team.

### Starting a new project for an existing customer
1. Create `Customers/<Customer>/Projects/<Project Name>/` with its team file, a `Contracts/` folder, and `Resources.md`.
2. Create the actual Project Manager project (title prefixed with the customer abbreviation), not a hand-authored lookalike.
3. Cross-link the two.
4. Populate the team file — each person's name, email, title, project role, and a wikilink to their primary record. Record which partner account team and division is engaged.
5. Add each internal person's project and role to the customer-level `Parties/Account Team.md` too.
6. File any SOW, primer, proposal, or LOE already in hand into `Contracts/`.
7. Record the project's Slack/Teams channels in its `Resources.md`.

### Adding an internal staff member to a project
1. Does `<Company Name>/Relationships/<Person>` exist? If not, create it with contact info and the LinkedIn/Teams/Slack quick links.
2. Add them to the project's team file — name, email, title, role, wikilink to their record.
3. Add or update their row in `Customers/<Customer>/Parties/Account Team.md`, listing this project and their role on it.
4. Add the reciprocal wikilink from their relationship file to the customer and project.

### Filing a piece of content ("where does X go?")
1. Plan or schedule data (task, milestone, project record)? → Project Manager's store (vault-root `Projects/`).
2. A web clipping? → stays in `Clippings/`; wikilink to it from wherever it's used. See "Clippings".
3. A contractual document for a specific project? → `Customers/<Customer>/Projects/<Project>/Contracts/`.
4. A pointer to a system outside the vault? → the nearest `Resources.md` — project, customer, or company.
5. About one specific project otherwise? → `Customers/<Customer>/Projects/<Project>/`.
6. About a person? → their primary record (see "The people model"), never a second copy.
7. About the customer relationship broadly? → `Customers/<Customer>/` — `Organization/`, `Parties/`, or `Company Background/`.
8. About a partner as an organization? → `Partners/<Partner>/Organization/` or `Branding/`.
9. About building or running a practice? → `Practices/<Practice>/`.
10. About a specific day's activity? → `Daily Summaries/<Year>/<Month>/<date>.md`.
11. About the company itself? → `<Company Name>/` — the matching subfolder, or `Resources.md` if it's a pointer.

### Auditing an existing vault for drift
This taxonomy is the target, not necessarily what's on disk. A vault built up organically — or one that predates the `Organization/`, `Parties/`, and company `Relationships/` structure — will only partially follow it.

1. Search each `Customers/<Name>/` and `Partners/<Name>/` against the expected shape: Is the Org Chart inside `Organization/`, or still at the folder's top level? Does the customer have `Parties/` with an `Account Team.md`? Does the partner have `Organization/Relationships/`? Does each project folder have `Contracts/` and `Resources.md`? Is the org chart split once past ~500 lines?
2. Check the people model for duplication: contact details restated in an account team or project file instead of wikilinked to a primary record. That's the drift that costs the most later, because every copy ages independently.
3. Check `<Company Name>/` for the newer folders — `Relationships/`, `Marketing & Narrative/` broken out per narrative, `Townhalls/`, per-page `Website Copy/`, `Philosophy & Background/`, `Resources.md`.
4. **Flag, don't silently fix, anything requiring a move or rename.** Relocating an existing Org Chart into `Organization/` is exactly this case: propose it, and let the user execute the move inside Obsidian. If they ask you to do it, warn which notes' backlinks may break first and offer to search-and-repair `[[links]]` afterward.
5. Content-only fixes — adding a missing `Account Team.md`, filling an empty `Company Background/`, adding a missing reciprocal wikilink, creating a `Resources.md` — are safe to make directly with `edit_block`/`write_file`.

Report findings with counts and one concrete example each, and lead with the duplication problems: a structure that's merely in the wrong folder still works, while a contact detail copied into four files is already wrong in at least three.
