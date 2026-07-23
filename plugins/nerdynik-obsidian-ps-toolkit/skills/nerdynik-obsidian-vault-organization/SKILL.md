---
name: nerdynik-obsidian-vault-organization
description: Use when creating, filing, or auditing notes and folders for a customer, partner, or practice inside a Professional Services / C&SI / SI Obsidian vault — onboarding a new customer or partner, starting a new project under an existing customer, deciding where a contact/org-chart/background note should live, or reviewing an existing vault's structure for drift from convention. Defines the canonical Customers/Partners/Practices taxonomy, cross-linking model, and how it interacts with the Project Manager plugin's own storage.
---

# Obsidian PS Vault Organization

Keeps customer, partner, and practice content in a consistent place across a Professional Services / C&SI / SI practice's Obsidian vault, so both humans and an agent can predict where something lives without re-deriving structure each time.

**Builds on Desktop Commander's `obsidian-vault` skill** (see the plugin README) for everything mechanical — wikilinks, frontmatter/property conventions, MOCs, dashboards. This skill only adds the customer/partner/practice-specific *taxonomy* on top of that base. It does not restate wikilink or property mechanics; assume that skill's rules apply everywhere below.

**Hard rule inherited from that base skill: never move or rename an existing note via a raw filesystem call.** Wikilinks resolve by filename, and only Obsidian's own rename/move updates backlinks. Everything below is written so that following it going forward only ever *creates* new files/folders in the right place the first time — it does not imply reshuffling what already exists. If a vault already deviates from this structure, see "Auditing an existing vault" for how to handle that without breaking links.

## Before doing anything: confirm the vault root

Never assume a vault path. Confirm it with the user or by locating the `.obsidian/` folder via Desktop Commander's search — a wrong root means creating a second, orphaned structure next to the real one.

## Top-level taxonomy

This is one shared vault, not one vault per customer. Four top-level folders, plus the Project Manager plugin's own storage folder as a fifth sibling:

```
<Vault Root>/
  Customers/            # a.k.a. "Clients" — interchangeable terms, "Customers" is the folder name in use
    <Customer Name>/
      ...               # see "Customers" below
  Partners/
    <Partner Name>/
      ...               # see "Partners" below
  Practices/
    <Practice Name>/    # one per practice a person is involved with (e.g. a technology practice)
  <Company Name>/       # the practice's own company: market research, org chart, ideas, etc.
  Projects/             # Project Manager plugin's own store — global, flat, NOT nested under Customers
```

`Projects/` at vault root is the Obsidian **Project Manager** plugin's own storage folder (see [[nerdynik-obsidian-project-manager-notes]] for its file format) — it is a sibling of `Customers/`, not something that lives inside a customer folder. It has no concept of "customer," so see "Project Manager's projects and customers" below for how the two connect.

## Splitting large files

Any single-file record (most often an Org Chart) can outgrow one file as a company gets large. **Once a file passes roughly 500 lines, split it into logical units** rather than letting it keep growing — for an Org Chart, the natural split is the reporting-structure/hierarchy itself in one file and the per-person contact information in another (e.g. `Org Chart.md` + `Contact Information.md`). Leave a short pointer in the original file to where the content moved, same as the progressive-disclosure pattern for any other oversized note. Do this split proactively when a file is approaching the threshold, not only after it's already unwieldy.

## Partners

For each `Partners/<Partner Name>/`:

- **`Org Chart`** (single file, directly under the partner folder) — basic contact info for each individual at that partner and their reporting structure: Title, Email, Phone, who they report to. Split per "Splitting large files" above once this grows past ~500 lines.
- **`Relationships/`** folder, adjacent to the Org Chart — one file per person. Each file:
  - Repeats that person's general contact info from the Org Chart (so the file is self-contained).
  - Adds detail beyond basic contact info (relationship history, notes, preferences — whatever's relevant to working with them).
  - Wikilinks into `Customers/` for every customer account that person is involved in with us. This is the mechanism that makes a partner rep discoverable from the customer side too (see "Cross-linking" below).
- **`Branding/`** — anything pertinent to that partner's own branding guidelines (logos, colors, co-branding rules) needed when producing partner-facing or co-branded material. Create this folder once there's actual branding material to hold, not speculatively.

A person's file under `Relationships/` is their **primary information document** — other notes that reference a partner rep (a customer's account-team file, a project's team file) link to *this* file rather than restating their details.

## Customers

For each `Customers/<Customer Name>/`:

- **`Projects/<Project Name>/`** — one folder per project at that customer. This folder holds *supporting* material for the project; it is not where Project Manager's own task/milestone files live (those are in the vault-root `Projects/`, see below). At minimum it holds the per-project team file described below and a **`Contracts/`** folder for that project's contractual documents — SOWs, SOW primers, project proposals, LOE/cost estimates. Add `Meetings/`, `Deliverables/`, etc. as the project actually produces them, rather than pre-creating empty structure speculatively — `Contracts/` is called out explicitly because every project has this category of document from the start, unlike the others.
- **Org Chart** (single file) — same shape as a partner's Org Chart (Title, Email, Phone, reporting structure), including the same "Splitting large files" rule above. Unlike Partners, **no separate `Relationships/` breakout** — one file (or its two split halves) is enough here.
- **Account Team** tracking file — which account teams are engaged on this customer relationship, broken out by the partnership they come from, plus any additional individuals (from us or the customer) working across the various projects. Wikilink out to the relevant `Partners/<Partner>/Relationships/<Person>` file for anyone who has one, and expect `Partners/.../Relationships/` files to wikilink back into this customer — it's a two-way cross-reference, not just outbound.
- **`Company Background/`** folder — assembled the first time a customer is added. General information about the company as a whole (spans multiple projects, not project-specific): what they do, industry, and similar. Include HQ address. A brief web search to derive this is fine when the practice doesn't already have it firsthand — treat anything sourced that way as background context to confirm, not as verified fact, and say where it came from.

### Per-project team file

Inside `Customers/<Customer>/Projects/<Project Name>/`, maintain a file listing everyone involved in that specific project, **grouped by which company they're part of** (us, the customer, any partner). For each person: basic contact info, Title, their Role on this project, and a wikilink to their primary information document.

"Primary information document" resolves differently depending on who the person is:
- A **partner rep** → their file under `Partners/<Partner>/Relationships/`.
- A **customer employee** → they don't get their own file (Customers has no Relationships breakout); link into their entry in the customer's Org Chart — an Obsidian heading/block link (`[[Org Chart#Their Name]]`, or `[[Contact Information#Their Name]]` if that Org Chart has been split per "Splitting large files") rather than a whole-note link, so whichever file holds contact info needs one heading/block per person for this to resolve.
- **Our own staff** → the spec above doesn't define a primary-document location for internal team members the way it does for partner reps and customer employees. Flag this as an open question rather than inventing one: ask whether internal staff should get the same file-per-person treatment somewhere under `<Company Name>/` (mirroring Partners' `Relationships/` pattern) or whether a plain-text name is fine for now. Don't create that structure speculatively before it's actually decided.

### Per-project partner relationship

Track which partner account team is engaged on *this specific project*, in addition to the customer-level Account Team file — a customer can be working with **multiple account teams at the same partner for separate divisions** at once (e.g. two different projects at one customer, each fronted by a different division of the same partner), so the customer-level file alone can't disambiguate which division applies to which project. Note this on the per-project team file itself (or a short companion note in the project folder): which partner, and which division/account team within that partner, wikilinked to the relevant `Partners/<Partner>/Relationships/<Person>` entries — same mechanism as the customer-level Account Team file, just scoped to one project.

## Practices

A practice can directly target a specific partner — e.g. a Databricks-focused practice, and Databricks itself as a partner. These stay in two different places, not merged:

- **`Partners/<Partner Name>/`** — general information *about the partner as an organization*: org chart, contacts, whatever's generally true of the relationship regardless of which of our practices touches them.
- **`Practices/<Practice Name>/`** — information about *building and running the practice itself*: methodology, enablement, certifications, playbooks, roadmap — whatever it takes to grow or operate that practice, independent of any one partner's org chart.

When a practice is built around a specific partner, wikilink the two rather than duplicating — the practice folder links to `Partners/<Partner>/` for the relationship/org-chart side, and the partner folder can note which practice(s) target it. Not every practice maps to a partner, so only add this link when it genuinely applies.

### Common practice-level folders

Create these under `Practices/<Practice Name>/` as they're actually needed, not all up front:

- **`Case Studies/`** — case studies the company developed itself, or summary references to ones published elsewhere about that practice.
- **`COE/`** — Center of Excellence material: copy for CoE portal web pages, plus the documents/findings behind developing and maintaining the CoE.
- **`Website Copy/`** — copy for the company's public-facing website covering that practice: practice pages, service-offering pages, etc. `<Company Name>/` commonly maintains a parallel `Website Copy/` folder for company-wide copy — wikilink between the two where content overlaps (e.g. a practice page that also feeds a company-level services overview) rather than duplicating the prose.
- **`Hiring/`** — hiring handbooks, repeatable interviewer questions, take-home or live exams, and anything else specific to hiring for that practice. `<Company Name>/` commonly maintains its own `Hiring/` folder too, for broad questions/material that spans every practice — wikilink a practice's `Hiring/` folder to the company-level one for anything not practice-specific, rather than restating it.
- **`Training/`** — everything about training for that practice: exam info, lessons, learning academies, learning plans/journeys.

## `<Company Name>`

The company owns the practices and partnerships underneath it. Maintain wikilinks from `<Company Name>/` out to each `Practices/<Practice>/` and `Partners/<Partner>/` it operates — this folder functions as an index/MOC over them, not a duplicate of their content.

Company-wide `Website Copy/` and `Hiring/` folders here mirror the practice-level ones described above — company-wide website copy and hiring material lives here, practice-specific material lives in that practice's own folder, and the two wikilink together where content overlaps rather than one restating the other.

**The vault is not necessarily the whole picture.** A company commonly keeps additional information about its customers, projects, practices, and partnerships in other systems — Microsoft 365/Teams, Google Docs, Slack, and similar — as employee records, documents, or conversations. Don't assume the vault is complete. When starting substantive work in this domain (onboarding, background research, filling gaps) and it's unclear whether the vault already has full context, **ask the user what other locations/connectors the company maintains** that might hold relevant information, rather than silently working around a gap or assuming one doesn't exist. Ask this once per topic/engagement, not on every small edit.

## Cross-linking model

The design deliberately makes the same person/relationship visible from multiple angles via wikilinks, not by duplicating the substance of a record:

- `Partners/<Partner>/Relationships/<Person>` → wikilinks out to every `Customers/<Customer>/...` they touch.
- `Customers/<Customer>/Account Team` → wikilinks out to the `Partners/<Partner>/Relationships/<Person>` for every partner-side person on the account.
- `Customers/<Customer>/Projects/<Project>/Team` → wikilinks to each person's primary document, wherever that lives.
- `<Company Name>/` → wikilinks out to every `Practices/<Practice>/` and `Partners/<Partner>/` it owns; a practice built around a specific partner links back to that partner's folder.

When adding a person (or a practice/partner) to one side of a relationship, check whether the other side's file needs the reciprocal link too — these are meant to stay two-way.

## Project Manager's projects and customers

Project Manager has no "customer" concept and stores every project as a flat entry in the vault-root `Projects/` folder regardless of which customer it's for (see [[nerdynik-obsidian-project-manager-notes]] for the exact file format). The observed way this practice disambiguates customer within that single flat store is a **naming convention on the project title itself** — prefixing it with the customer's name or a short abbreviation, e.g. a project titled `<Customer Abbreviation> - <Project Name>`. Follow that convention for new Project Manager projects rather than introducing a separate custom field or tag, since it's already the established pattern.

The customer's own `Projects/<Project Name>/` folder (under `Customers/`) and the Project Manager project note (in the vault-root `Projects/`) are two different things about the same project — cross-link them (a wikilink from the customer-side project folder's team file to the Project Manager project note, and the reverse from the project note's body) rather than duplicating plan data into the customer-side folder.

## Naming conventions

- Customer, partner, and person names may use normal display casing and spaces (e.g. `Acme Corp`) — Obsidian users read these as titles, unlike this plugin's own repo files. Still avoid the characters wikilinks treat specially: `# | ^ : \ [ ]`.
- Keep "Org Chart," "Contact Information," "Relationships," "Branding," "Account Team," "Company Background," "Projects," "Contracts," "Case Studies," "COE," "Website Copy," "Hiring," and "Training" spelled identically across every customer/partner/practice folder — an agent (and Dataview/Bases queries) will look for these exact names.

## Playbooks

### Onboarding a new customer
1. Create `Customers/<Customer Name>/` with `Projects/`, an Org Chart file, an Account Team file, and a `Company Background/` folder.
2. Populate `Company Background/` — pull from what the practice already knows first; fall back to a brief web search for general company/industry/HQ-address facts only when that's missing, and mark anything web-sourced as such.
3. If the account came in through a partner, add the partner-side people to the Account Team file now, wikilinked to their `Partners/<Partner>/Relationships/` files (and add the reciprocal link on their side).

### Onboarding a new partner
1. Create `Partners/<Partner Name>/` with an Org Chart file and an adjacent `Relationships/` folder.
2. Only create a person's `Relationships/` file once there's something beyond basic contact info to say about them, or once they show up on a customer account team — don't pre-populate every name from the Org Chart as an empty file.

### Starting a new project for an existing customer
1. Create `Customers/<Customer>/Projects/<Project Name>/` with its team file and a `Contracts/` folder.
2. Create the actual Project Manager project (title prefixed with the customer per the convention above), not a hand-authored lookalike — let that plugin own its own frontmatter shape.
3. Cross-link the two: the team file (or a short note in the project folder) links to the Project Manager project note, and vice versa.
4. Populate the team file, resolving each person's primary-document link per the rules above, and record which partner account team/division is engaged on this project specifically (see "Per-project partner relationship").
5. File any SOW, SOW primer, proposal, or LOE/cost estimate already in hand into `Contracts/`.

### Filing a piece of content ("where does X go?")
Decision order:
1. Is it plan/schedule data (a task, milestone, or project record)? → Project Manager's own store (vault-root `Projects/`), not here.
2. Is it a contractual document (SOW, SOW primer, proposal, LOE/cost estimate) for a specific project? → `Customers/<Customer>/Projects/<Project>/Contracts/`.
3. Is it about one specific project at a customer otherwise? → `Customers/<Customer>/Projects/<Project>/`.
4. Is it about the customer relationship broadly (not one project)? → `Customers/<Customer>/` directly (Org Chart, Account Team, Company Background).
5. Is it about a partner or a specific person there? → `Partners/<Partner>/` (Org Chart, or a `Relationships/` file).
6. Is it about building/running a practice, rather than any one customer or partner? → `Practices/<Practice>/`.
7. Is it about the company itself, or about which practices/partners it owns? → `<Company Name>/`.

### Auditing an existing vault for drift
This taxonomy is the target, not necessarily what's on disk today — a vault built up organically may only partially follow it.
1. Use Desktop Commander's search to check each `Customers/<Name>/` and `Partners/<Name>/` folder against the expected shape (Org Chart present, and split into `Org Chart`/`Contact Information` if it's grown past ~500 lines? Account Team present for customers? `Relationships/` present for partners, and *not* present for customers? Each project folder has a `Contracts/` folder?).
2. Flag, don't silently fix, anything that would require moving or renaming an existing note — per the inherited hard rule, propose the fix and let the user execute the move/rename inside Obsidian, or do it yourself only after explicitly warning which notes' backlinks may break and offering to search-and-repair `[[links]]` afterward.
3. Content-only fixes (adding a missing Account Team file, filling in an empty Company Background, adding a missing reciprocal wikilink) are safe to make directly with `edit_block`/`write_file`, same as the base skill's own normalization workflow.
