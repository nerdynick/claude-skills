# DSU Notes

The full specification for a project's daily standup notes, living in
`Customers/<Customer>/Projects/<Project>/DSU Notes/<YYYY-MM>/<DD>-<Note Name>.md`. Read this before
writing or updating one.

A DSU note is the **durable record of one standup for one project** — what was said, by whom, in
their own words, and what it changed. It is not a transcript and not a recap. Its value is that
someone reading it a quarter later can reconstruct a decision and see who owned it.

Examples below use the vault's placeholder cast: `Acme Corp` as the customer (abbreviated `ACME`),
`Data Platform` as the project, `Globex` as a third-party vendor, and Doe / Smith / Roe / Major /
Coe as people.

## Where it goes, and the alias that makes it findable

The path carries the customer, the project, and the month. The filename carries only the day and a
name: `DSU Notes/2026-09/10-Standup.md`.

**That filename is not unique across the vault, and wikilinks resolve by filename alone.** Two
projects both standing up on the 10th produce two `10-Standup.md` files, and `[[10-Standup]]` is
then ambiguous. So every DSU note **must** carry a globally unique alias, and links from elsewhere
use the alias rather than the bare filename:

```yaml
aliases: [ACME - Data Platform DSU 2026-09-10, Data Platform DSU September 10]
```

The first alias is the canonical long form — `<Customer Abbrev> - <Project> DSU <YYYY-MM-DD>` — and
it's what the DSU chain and every inbound link should use:
`[[ACME - Data Platform DSU 2026-09-10]]`. The rest are the human phrasings someone would actually
type. Without the alias the note is reachable only by path-qualified link, and the previous/next
chain between standups silently rots.

## Frontmatter

```yaml
---
title: ACME - Data Platform DSU 2026-09-10
aliases: [ACME - Data Platform DSU 2026-09-10, Data Platform DSU September 10]
tags: [acme, data-platform, meeting-notes, dsu, sow, access, risk]
type: dsu
created: 2026-09-11
updated: 2026-09-11
status: evergreen
summary: "One dense paragraph — see below."
related: ["[[ACME - Data Platform Project MOC]]", "[[ACME - Data Platform DSU 2026-09-09]]", "[[2026-09-10]]"]
---
```

- **`title`** — the canonical long form, matching the first alias. The filename is short; the title
  is what identifies the note.
- **`tags`** — four fixed, then topical: the **customer slug**, the **project slug**,
  `meeting-notes`, and `dsu`, followed by whatever the day was actually about (`sow`, `staffing`,
  `access`, `risk`, `security`). The four fixed tags are what make "every DSU for this project" a
  query; the topical ones are what make "every time the SOW came up" a query.
- **`created` is when the note was *written*, not when the standup happened.** A catch-up writeup
  of a 09-10 standup created on 09-11 records `created: 2026-09-11` — the meeting date lives in the
  title, the aliases, and the path. Don't backdate it; the gap between meeting and writeup is itself
  information, and it's why the body says so explicitly.
- **`status`** — `evergreen` once published, because a DSU records a fixed event and won't grow.
  Use `seedling` only while the writeup is knowingly incomplete, pending a transcript review.
- **`summary`** — one dense paragraph, not a sentence. This is the highest-traffic field in the
  note: it's what gets read when scanning a month of standups. Lead with what *changed* — a
  decision, a status flip, a staffing move — and carry the hard specifics into it: dates, names,
  figures, and short verbatim fragments where the exact words matter. A summary that says "discussed
  the timeline" has wasted the field.
- **`related`** — the project MOC and Background, the **previous and next DSU**, the day's
  `Daily Summaries` entry, and any contact or glossary note the writeup leans on.

## Title and provenance block

```markdown
# Acme Corp — Data Platform DSU · September 10, 2026

Data Platform portion of the consolidated Acme Corp internal daily standup. Same recording also
carried a Billing Migration hold statement ([[ACME - Billing Migration DSU 2026-09-10]]) and a
Reporting Refresh ingestion status ([[ACME - Reporting Refresh DSU 2026-09-10]]).

Written 2026-09-11 (catch-up). Invite ***Data Platform Updates*** 8:45–9:15 AM MT, group-mailbox
organizer; roster Jane Doe, John Smith, Alex Roe, Mary Major, Carol Coe.

*9:01 AM MT (16 min late — the preceding architecture review overran) · 25 m 07 s · Jane Doe
(chair) · John Smith · Alex Roe · Mary Major 🟡 (Speaker 8 — see flags)*
*Source: recording `<recording-id>` ("09-10 Meeting: Project Reactivation and MVP Plan") — verbatim
transcript reviewed 2026-09-11*

**Heard:** Jane ✅ · John ✅ · Alex ✅. Not heard: Carol (addressed — likely present, silent).

---
```

Every element there is load-bearing:

- **Which portion this is.** One recording routinely covers several projects. Each project gets its
  own note, each cites the same recording, and each links the siblings. Never file one multi-project
  note; never let a project's content land only in another project's note.
- **Who chaired, and why**, when it isn't the usual person — `Jane Doe chairing while the PM is
  OOO, back ~09-15`. Coverage explains gaps in the record later.
- **When the note was written**, whenever that isn't the day of the standup.
- **The invite** — its name, scheduled window, organizer, and full roster. The roster is what makes
  "who was invited but absent" answerable, which the attendance line alone can't.
- **Actual start time and duration**, with the reason for any slip. A standup that starts 16 minutes
  late and runs 25 minutes didn't cover what a 30-minute one would.
- **The attendance line** — chair marked, every attendee named, and any inferred speaker marked 🟡
  with a pointer to the flags section.
- **The source line** — the recording identifier (the thing that makes a transcript retrievable
  months later), the recording system's own generated title in quotes, and an explicit note that
  the **verbatim** transcript was reviewed and when.
- **Heard vs. not heard.** ✅ for anyone whose voice is actually in the recording; then who was
  expected and silent, and who was addressed but never answered. Silence is attributable; absence
  isn't.

## Body sections

Default to this set, in this order. Drop a section that has no content rather than writing "none".

1. **`## 🔄 Progress / Discussion`** — `###` subsections, one per topic, named for the topic itself
   (`### Vendor delivered a new file set — mapping paused`), not "Update 1". This is the bulk of the
   note.
2. **`## 🚧 Blockers / Risks`** — each with a severity marker, what it blocks, and who owns it.
3. **`## ✅ Next Steps`** — checkboxes, see below.
4. **`## ⚠️ Transcription Flags (human review)`** — see below.
5. **`## 🔗 Related Notes`** — the same links as `related:`, spelled out for a reader. The
   duplication is deliberate: frontmatter is for queries, the body is for reading.

When a standup had a clear agenda rather than a round of updates, **topical `##` headings replace
Progress / Discussion** — `## 🟢 Status`, `## 🎯 Scope`, `## 🔐 Access`, `## 👥 Staffing`,
`## 🔁 Process`, `## ⚠️ Flags`, `## ✅ Action items`. Blockers, action items and transcription flags
still appear; only the discussion body reorganizes.

## Quoting

**Quote verbatim, and mark it.** Bold the speaker, italicize their words:

```markdown
- **John's ruling (verbatim):** *"The terms that they use, we can't change those terms… the terms
  are the terms. They just need to understand what those terms are."*
```

The rules that make this safe rather than dangerous:

- **Quote only the verbatim transcript, never a polished or AI-rewritten one** — a paraphrase that
  reads cleanly can invert meaning. See [[nerdynik-plaud-recordings]] when the source is Plaud.
- **Never attribute from a speaker label alone.** Diarization merges both sides of an exchange into
  one turn. Confirm by direct address ("Hey Alex…" answered by that speaker) or by content only
  they could own, and record the inference in the flags section.
- **Separate observed from inferred.** What someone said is observed; what it means for the schedule
  is inferred and belongs in Blockers with its evidence.
- **Where the recording's own AI summary contradicts the audio, say so.** 🚨 in the flags section,
  with what the summary claims and what was actually said. That summary gets read by other people.

## Severity and status markers

One vocabulary, used consistently, so a reader can scan:

| Marker | Means |
|---|---|
| 🔴 | Critical, or unresolved and blocking |
| 🟠 | Real risk, not blocking yet |
| 🟡 | Probable — an inference or a name that needs confirming |
| ✅ | Resolved or confirmed, with the date and who confirmed it |
| ⚠️ | Contradiction, divergence, or something stated wrong on the call and left uncorrected |
| 🆕 | New finding, name, or artifact surfacing for the first time |
| 🚨 | The recording's AI summary is wrong |
| ℹ️ | Normalization note |
| 📌 | Post-standup update that supersedes the body |

## Action items

```markdown
- [ ] Surface the four pending rule questions to the vendor — **John Smith** — today (2026-09-10) — Vikunja #128
- [x] Schedule the internal morning standup — **Jane Doe** — ✅ done 09-11 8:30 AM MT
- [ ] Small-sample suppression in the dashboards — **unassigned**
```

Owner in bold, then the deadline as an absolute date, then the tracker reference where one exists.
Two rules earn their place:

- **`unassigned` is written out, never omitted.** An item with no owner is a finding, and hiding it
  behind a passive sentence is how it stays unowned.
- **A blocker with no owner isn't a blocker, it's a complaint.** An unowned blocker is the single
  most common reason the same one gets raised three days running.

Close items in place with `- [x]` and what happened. Don't delete them — the record of what was
committed to is the point.

## Transcription flags

The section that makes these notes trustworthy. One entry per uncertainty, each with its marker,
the evidence, and what would resolve it:

```markdown
- 🟡 **Speaker 8 = Mary Major** — inferred, not labelled by the recorder. John addresses her by
  name and Speaker 8 answers, and she gives the PM status. High confidence.
- 🔴 **"Carroll Cohen"** — new contact, name almost certainly mis-transcribed. Described as manager
  of data insights, peer of our main contact. The chair has a screen grab of the participant list —
  confirm the spelling from that before creating the contact record.
- ⚠️ **Kickoff date conflict** — stated as "Monday of last week" (09-01); the project MOC records
  08-25. Confirm which is used for reporting.
- ℹ️ Normalized per [[Plaud Transcription Glossary]]: *Jayne* → **Jane Doe**, *Smyth* → **John
  Smith**, *SAL* → **SOW**.
```

- **Resolve in place, don't delete.** Strike the original and append the resolution with its date
  and source: `~~🔴 Vendor contact "Carroll Cohen" — spelling unconfirmed~~` → `✅ **Resolved
  2026-09-12 — it is Carol Coe**, Research Director at Globex. Contact record created: [[Carol
  Coe]]`. The strikethrough is what tells the next reader this was already chased.
- **An unresolved name is an action item**, not just a flag — someone has to confirm it before a
  contact record or an org-chart entry gets created from a garble.
- **Feed confirmations back to the glossary** so the same garble isn't re-litigated next week.

## Post-standup updates

When something supersedes the note the same day, append rather than editing the body — the standup
said what it said:

```markdown
## 📌 Post-DSU Update — account exec reached the sponsor (same day, 11:16 AM MT)

> **@Jane Doe** — I talked to the sponsor. The SOW is in contract review and it should be approved.
> Till it is fully approved, we stay the course and continue to work as if it is a GO.

**What changes:**
- SOW moved from "no response" to "in contract review."
- The at-risk posture is now explicitly sanctioned rather than a judgment call.
- The body's characterization of the sponsor as unresponsive stands as of 8:30 AM but was resolved
  the same morning.

*Source: Teams chat message `<message-id>`*
```

Quote the source as a blockquote, cite its identifier, then state **what changes** — and say
explicitly which parts of the body are now stale. In Blockers, strike the superseded line and point
at the update rather than rewriting history.

## Cross-linking

- **Chain the standups.** Every note links the previous one, and gets linked by the next. A broken
  chain is how a week goes missing.
- **Link the day's `Daily Summaries` entry**, and expect the reverse link. The two are deliberately
  separate: a daily summary covers the user's whole day across every project; a DSU covers one
  project and is read by that project's team. Link across; never fold a day's standups into the
  daily summary instead of writing them.
- **Link sibling project notes from the same recording**, both ways.
- **Link people to their primary record**, per the people model. A name confirmed out of a
  transcription flag usually means an org-chart entry or a relationship page is now owed.
- **Link the tracker**, where action items actually live. The DSU records the commitment; it isn't
  the system of record for the task.

## Migrating notes that predate this layout

Standups already written as flat files (`ACME - Data Platform DSU 2026-09-10.md`) hold exactly the
right content in the wrong place. Moving them into `DSU Notes/<YYYY-MM>/` is a **move and a
rename**, so the hard rule applies: propose it, and let the user do it inside Obsidian.

Two things make this migration worse than a normal one, and both should be said out loud before it
starts: these notes are **densely cross-linked to each other** by filename, so the previous/next
chain is exactly what a filesystem move breaks; and the new short filenames **collide across
projects and months**, so every migrated note needs its canonical long form added to `aliases`
first — while the old filename still resolves — or the links have nothing to land on.
