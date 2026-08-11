# Daily Summaries

The full specification for `Daily Summaries/<Year>/<Month>/<YYYY-MM-DD>.md`. Read this before creating or updating one.

A daily summary reconciles two independent sources — **meeting recordings** and **calendar entries** — into a single record of what happened, what came out of it, and where the time went.

## Layout

```
Daily Summaries/
  2026/
    08/
      2026-08-11.md
  _Meta/
    ...run state for scheduled tasks
```

Zero-padded numeric months, ISO dates. `_Meta/` is described under "Run state" below.

## Sources

Two independent inputs, neither guaranteed present. Confirm what's actually available before building a summary rather than assuming.

**Recordings.** Whatever system the user records with. Ask once; don't assume. Whichever it is, capture its **recording identifier** as the "where to find the recording" metadata — that's what makes a transcript retrievable months later.

If it's **Plaud**, the `nerdynik-plaud-toolkit` plugin carries that MCP server and [[nerdynik-plaud-recordings]], which covers retrieving recordings without blowing out the context window and interpreting the results correctly. Three of its rules change what a daily summary should say:

- **`created_at` is roughly the END of the meeting**, not its start. Use `start_at` — which is UTC, while the AI summary body renders local time.
- **Never quote from the polished transcript.** It paraphrases in ways that can change meaning.
- **Never attribute a quote from the speaker label alone.** Diarization folds both sides of an exchange into one turn, so an unchecked quote can be assigned to the wrong person.

Read that skill before digesting Plaud output into a summary. Without it, the failure mode is a summary that looks clean and attributes the wrong words to the wrong people.

**Calendar.** Not bundled with this plugin. Check what the session actually has — a Microsoft 365 / Outlook connector, Google Calendar, or nothing. If no calendar is reachable, build the digest from recordings alone and **say in the file that the calendar wasn't available**, so a later reader doesn't mistake an unreconciled day for a fully reconciled one.

Ask once which sources to use, then proceed; don't re-confirm per call.

## The reconciliation problem

**Not every recorded call has a meeting invite, and not every meeting has a recording.** An ad-hoc call gets recorded with no calendar entry; a scheduled meeting gets cancelled, moves to a hallway, or simply isn't recorded.

So never treat either source as the complete list. Build the day from **both**, and mark which sources each entry came from:

| Recording | Calendar invite | Handling |
|---|---|---|
| ✅ | ✅ | Matched. Merge both into one entry. |
| ✅ | ❌ | Record it anyway, from recording metadata alone. Note that no invite was found — don't imply one is missing by omission. |
| ❌ | ✅ | Record it anyway, from the invite. Note there's no recording, so no transcript exists to go back to. |

Match on overlapping time window plus participant or title similarity, not title alone — recurring meetings share titles across days, and recordings are often titled by whoever started them.

**When a match is uncertain, say so** rather than silently merging or silently splitting. A wrongly merged entry hides a meeting.

## Required sections

Every daily summary carries these, in this order. Include a section with an explicit "none" rather than omitting it — a missing section is ambiguous between "nothing happened" and "not checked."

### 1. Call & Meeting Digest

Only when the user maintains recordings of their meetings. Per call:

- **Title**
- **Start and end time, with timezone** — always include the timezone; summaries get read across regions and after travel
- **Duration**
- **Where to find the recording** — the metadata needed to pull the transcript or recording back up later: source system, recording ID, direct link if there is one. This is what makes the summary a durable index rather than a one-time read.
- **Attendees**

For attendees, wikilink each person to their record, resolved the same way as everywhere else in the vault:

1. Our own staff → `<Company Name>/Relationships/<Person>`
2. Partner reps → `Partners/<Partner>/Organization/Relationships/<Person>`
3. Customer employees → a heading link into `Customers/<Customer>/Organization/Org Chart`
4. **No individual relationship file exists** → link to the org chart entry instead. Falling back to the org chart is expected and correct; don't create a relationship file just to have a link target.
5. Not in the vault at all → plain text name plus email. Note them as unrecorded; a recurring unknown attendee is a signal someone needs a record.

**Cross-reference every recording against the available calendar** to find the correlated invite. When one is found, log **all** invitees from it — including those who didn't attend, which is itself information — and wikilink them per the rules above.

### 2. Action Items

A checklist of todos and action items from the day.

**Carry forward anything not completed from the previous day**, marked as carried so its age is visible. An item carried five days is a different problem from one raised today, and that only shows if the carry is explicit.

Link each item to the project, customer, or person it belongs to. Items that belong in Project Manager should be created there and linked, not tracked only here — see [[nerdynik-obsidian-project-manager-notes]].

### 3. Findings for Review

Things the user should be aware of, gathered while producing the summary. This is the section that earns the summary its keep, so be specific rather than filling it:

- **Clarifying questions** — information needed to do the work properly, stated as a direct question
- **Insights worth surfacing** — something the day's material implies that wasn't said outright
- **Important findings about a customer** — a change in stakeholders, budget, timeline, or sentiment
- **Risks and unforeseen issues** — anything spotted that could become a problem, with why

State each finding, then the evidence behind it. A finding with no source can't be acted on.

### 4. Projects Worked

Which projects and efforts the day covered. Wikilink each to `Customers/<Customer>/Projects/<Project>/` and to its Project Manager note.

Include internal and non-billable effort too. A day that looks empty of project work usually wasn't empty.

### 5. Schedule

A rough hour-by-hour reconstruction of the day, built from the Call & Meeting Digest and the calendar.

The purpose is **time tracking in another system**: someone who has to log hours elsewhere should be able to read this and fill that system in without reconstructing the day from memory.

- Timeslots with start and end, in order
- What each slot was, wikilinked to the project or effort
- Gaps left visible rather than padded — an unaccounted hour is honest and useful

Then an **estimated breakdown of hours by project and effort**, summing the slots.

Mark the totals as estimates. They're derived from meeting durations and won't capture focused work between meetings, so they're a starting point for a timesheet, not an authority. Say so in the file rather than leaving a precise-looking number to be trusted.

### 6. Proposed Updates

Anything learned while producing the summary that should change something *elsewhere* in the vault — new stakeholders heard on a call, a scope change, a partner division switch, a contact detail correction.

List each as a proposal with its target file, and apply them only per the normal rules: content additions are safe to make directly; anything requiring a move or rename gets flagged for the user. Keep the record of what was proposed even after applying it, so the summary explains why a file changed that day.

## Run state

Scheduled or repeated daily-summary generation needs somewhere to track its own bookkeeping — last successful run, the watermark of the last recording or calendar entry processed, and any source that errored.

Keep these in `Daily Summaries/_Meta/`, one file per scheduled task. They're operational metadata, not content: never link to them from a daily summary, and skip them when searching the vault for substance.

The leading underscore sorts them away from the year folders and signals they aren't summaries.

## Writing rules

- **Never invent a call, attendee, or timeslot.** An incomplete summary is useful; a plausible-looking wrong one poisons the record and gets cited later.
- **Distinguish observed from inferred.** "Discussed the Q3 timeline" is observed; "the timeline is slipping" is inferred and belongs in Findings with its evidence.
- **Timezone on every time.** Always.
- **Keep the previous day's file open when starting a new one** — action items carry forward, and unresolved findings often should too.
- Regenerating a summary must not silently drop hand-written additions. Merge, or ask before overwriting.
