---
name: nerdynik-plaud-recordings
description: Use when retrieving, searching, quoting, summarizing, or otherwise working with recordings, transcripts, AI notes, or meeting summaries from a Plaud account or the plaud MCP server — finding a past call, answering what was said in a meeting, pulling an exact quote, extracting action items, identifying who spoke, or writing transcript-derived content into notes or a task tracker. Covers the specific failure modes of this data — oversized responses, a paraphrased transcript variant that must never be quoted, speaker diarization that merges two people into one turn, UTC-versus-local timestamps, and mistranscribed proper nouns.
---

# Working with Plaud Recordings

[Plaud](https://www.plaud.ai/) makes wearable and phone-attached AI voice recorders (the Note, Note Pro, and NotePin lines) plus a companion app. Recordings sync to a Plaud account, where the service transcribes them with speaker diarization across a wide range of languages and generates structured AI summaries from templates.

The `plaud` MCP server exposes that account **read-only** — it retrieves recordings, transcripts, and notes, and cannot alter or delete the source audio.

The data is genuinely useful, but four of its characteristics will silently produce wrong output if you don't plan around them. They're stated as guardrails below because each one has a failure mode that looks like success.

Full tool schemas, response shapes, and field-level detail are in `references/mcp-reference.md`. Read it before writing any code against the API or debugging an unexpected response.

## The four guardrails

**1. Never call `get_file` as an exploratory first step.** It returns metadata, an audio URL, the *entire* transcript inline, the outline, and the AI notes in a single response. On an hour-long recording that consumes an enormous share of the context window at once, and it can't be paged back. Call it only when you specifically need the presigned audio URL, or when a recording is genuinely short and you want everything.

**2. Never quote from the polished transcript.** The `transaction_polish` block is an AI rewrite, not a cleanup pass — it changes wording, not just filler. Use it to skim and understand; quote only from `transaction`. See "Choosing a block".

**3. Never attribute a quote from the segment label alone.** Diarization regularly folds both sides of an exchange into one attributed turn. See "Speaker identity".

**4. Read the glossary before interpreting anything.** Automatic transcription mangles proper nouns — names, companies, products — and an uncorrected name written into a note gets cited later as fact. See "The glossary loop".

## Entry: pick the cheapest path that answers the question

| The user wants | Do this |
|---|---|
| "What happened in that meeting?" | `get_note` alone. Often sufficient, and far lighter than anything else. |
| To find a meeting | `list_files` with `query` or a date range — then **check `truncated`**. |
| Exact words / a quotable line | `get_transcript(block="outline")` to locate the moment, then paged `get_transcript(block="transaction")`. |
| The audio itself | `get_file`, for the presigned URL. This is the one legitimate reason to call it. |

Escalate through these in order. Most requests stop at the first or second row.

### Searching

`query` is a case-insensitive substring match on the **recording name only** — it does not search transcript content. Names are auto-generated and tend to be topic-ish (`08-07 Consultation: Northwind — Platform Migration`), which makes name search unexpectedly effective for finding a customer meeting, and useless for finding a topic that was discussed but not in the title.

**Filtered results are capped.** Filtering happens after scanning a bounded window of the most recent recordings. If the response comes back `truncated: true`, older matches exist that were never examined. Say so — reporting "no results found" on a truncated scan is wrong, and the user may be able to narrow by date instead.

## Choosing a block

| Block | What it is | Use for | Never use for |
|---|---|---|---|
| `transaction` | Raw transcription plus diarization | **All quoting, evidence, anything cited or customer-facing** | — |
| `transaction_polish` | AI-cleaned rewrite | Skimming, summarizing, readability | **Quoting. Ever.** |
| `outline` | Topic index with time windows | A cheap navigation map of a long recording | Extracting content |

The polish block rewrites meaning, not just delivery. A representative case: a speaker says they're *"light on the service side on the [product]"* — a statement about a practice area — and the polished version renders it *"light on the service side at [product]"*, which reads as a statement about where they work. Filler removal is harmless; that class of grammatical normalization is not, and it's invisible unless you compare the two blocks side by side.

So: understand with `transaction_polish` if it helps, attribute only from `transaction`. Any "pull the quote" capability must hit `transaction`.

## Long recordings

There's no offset parameter — only an opaque cursor — so seeking into the middle of a recording means walking pages from the start. Plan the retrieval before starting:

1. `get_note` — the summary and topic list. Frequently answers the question outright.
2. `get_transcript(block="outline")` — a compact list of `{start_time, end_time, topic}` windows, cheap to pull in full.
3. Pick the target window from the outline.
4. Page `get_transcript(block="transaction")` until segment times enter that window, then read verbatim.

For a target late in a long recording, weigh several sequential pages against one large-limit call. Both are expensive; pick deliberately rather than drifting into the large one.

**Prefer verbatim extraction over summarization when delegating to a subagent.** Paraphrase compounds transcription error with interpretation error, and the polish-block drift above shows how quietly that happens.

## Speaker identity

Every segment carries two fields:

```json
{ "speaker": "Jordan M",  "original_speaker": "Speaker 2" }
{ "speaker": "Speaker 1", "original_speaker": "Speaker 1" }
```

`original_speaker` is always the raw diarization label. `speaker` is the resolved identity **where the service matched a voice profile** — typically the account owner and enrolled colleagues. External participants usually stay `Speaker N`.

Treat a resolved name as high confidence and an unresolved `Speaker N` as requiring inference plus an explicit confidence marker. Resolved names sometimes carry an organization annotation (`Alex R (Acme Corp)`).

### Diarization bleed

**This is the most dangerous property of the data.** A segment attributed to one speaker frequently contains the other participant's words inline. Real shapes this takes:

- A turn labeled with one speaker reading *"…Are you in front of your screen? I am, so this is basically what we're looking at…"* — the **"I am"** is the other person answering.
- *"Those work, right? Yep. Yeah, any of the links…"* — question and answer merged into a single attributed turn.
- *"Okay. That sounds good. Cool. … Sounds good. Yeah. All right."* — a closing exchange from both parties collapsed under one label.

Before quoting, scan the segment for embedded question-and-answer pairs, tone shifts, or self-contradiction. If a segment appears to hold both parties, quote only the unambiguous portion or mark the attribution uncertain. **This persists in the polished block too** — it's a diarization artifact, not a transcription one, so switching blocks doesn't escape it.

### The gap propagates into AI notes

The generated notes inherit these labels verbatim, which means **action items get assigned to unidentified people**:

```
> Participants: [Alex R (Acme Corp)] [Jordan M] [Speaker 3]
- [ ] Jordan and Speaker 3 to coordinate on goals for the platform practice…
```

Anything lifting action items into a task tracker or a notes vault must resolve `Speaker N` first, or carry the placeholder through explicitly. Never guess an owner — a confidently wrong assignee is worse than an open question.

## Time handling

Two different timezones appear in one response, and mixing them produces wrong dates.

- **`start_at` is UTC**, though it looks local.
- **The AI summary body renders account-local time.** A recording whose `start_at` reads `22:08:17` can show `16:08:17` in its own summary header — six hours apart, the account's local offset.
- **`created_at` is roughly the END of the meeting** — it tracks upload/finalize, landing near `start_at + duration`. Never treat it as the start time.
- **`duration` is milliseconds.** So is every per-utterance `start_time` / `end_time`, measured from the start of the recording rather than wall clock.

Wall-clock time for an utterance is therefore `start_at` (UTC) `+ start_time` ms.

That conversion is the most useful thing in the data model: it makes utterances directly cross-referenceable against chat and calendar timestamps, which is how you resolve identities and settle "who said that, and when." Don't hardcode the local offset — it shifts with daylight saving.

## The glossary loop

Automatic transcription mangles proper nouns badly and consistently. Uncorrected, it injects wrong people, wrong companies, and wrong products into notes that later get cited as fact.

**Before interpreting any Plaud output, read the transcription glossary** — a maintained file of known mistranscriptions and their corrections, with confidence markers. **The glossary is the authority** — read it fresh rather than relying on any list baked into a skill file, including this one.

See "Locating the glossary" below for how to find it, and "Where the glossary should live" for setting one up.

Illustrative of what it catches (your glossary's real contents will differ):

| Rendered as | Actually | Why it happens |
|---|---|---|
| `"Nemo Systems"` | Nimbus Systems | brand guessed phonetically |
| `"and you"`, `"a new"` | Anu (a person) | short name collides with common words |
| `"on PEM"` | on-prem | industry contraction absent from the vocabulary |
| `"Marissa"`, `"Maurice"`, `"Morris"` | one person: Maurizio | **the same name rendered several ways in a single recording** |

That last row is the reason the glossary exists. One short recording can render a single unfamiliar name four different ways, and any frequency-based heuristic will read them as four distinct people.

### Rules when handling output

1. **Never write a transcribed proper noun into a note without checking the glossary.** If a name isn't there and isn't obviously right, mark it uncertain and flag it rather than guessing.
2. **Cross-reference before trusting.** Chat and calendar systems carry real names, real timestamps, and real email addresses. **When a transcript and a chat disagree, the chat wins.** Member lists are especially good for turning a garbled first name into a full name; the UTC `start_at` makes time-window correlation straightforward.
3. **Mark inference as inference.** Record a confidence level in the note itself and state what the inference rests on. If one speaker label appears to answer to two different names, say so — diarization both merges and splits people.
4. **Preserve the garble inside quotes.** Quote exactly and put the correction in brackets or a footnote. Never silently repair a quote — someone comparing the note against the recording needs them to match.
5. **Don't repair acronyms by guessing.** If it isn't resolvable from context, record it as unresolved.
6. **Feed the glossary back.** When a new mistranscription is resolved, or an existing entry's confidence improves, add it with its evidence, and log the recording as reviewed. That maintenance loop is the entire point of the file.

**Propose glossary additions; never write them autonomously.** A wrong entry is worse than a missing one, because it launders a guess into an authority that later work will trust.

## Locating the glossary

Work down this list and stop at the first hit. Don't ask the user if an earlier step already answered it.

1. **A path given earlier in this session.** Use it.
2. **The plugin's configured path.** If it's available, it appears between the arrows here → `${user_config.glossary_path}` ← and is a usable path. Two other outcomes are both "not configured, move on": the arrows sit empty (no value set), or the placeholder text shows verbatim (this surface doesn't substitute plugin config into skill text). Never treat a literal `${…}` string as a filename.
3. **The settings file, read directly.** With filesystem access, read `~/.claude/settings.json` and look for:

   ```json
   "pluginConfigs": {
     "nerdynik-plaud-toolkit@nerdynik": {
       "options": { "glossary_path": "…" }
     }
   }
   ```

   This works regardless of whether the surface substitutes config into skill text, which is why it's worth trying before asking.
4. **A knowledge base, at the conventional location.** If a vault or notes root is known, look for `Transcription Glossary.md` at its root. See below.
5. **Ask.** If nothing turned it up, ask where the glossary lives — and if there isn't one yet, offer to create it.

## Where the glossary should live

**Prefer a shared knowledge base over a loose file.** If the user keeps an Obsidian vault, a notes repository, or a team wiki, that's the right home:

- It sits with the notes the corrections feed into, so a derived note can link straight to the glossary entry behind a correction.
- It's already backed up and synced, and reachable from other machines and other tools.
- Other people can read and extend it. A glossary in one person's home directory dies with that laptop.

You may already know a knowledge base exists — the user mentioned one, a `.obsidian/` folder is reachable, or a vault-structure skill such as [[nerdynik-obsidian-vault-organization]] is active. **When you do, suggest it rather than asking an open-ended question.** Propose a concrete path:

```
<Vault Root>/Transcription Glossary.md
```

Root level, consistent filename so it's findable without configuration. In Obsidian, link it from the home note and give it an alias so it's reachable by wikilink from any note that relied on a correction.

**If the user agrees, do both things:** create the file if it doesn't exist, and persist the path so the next session finds it without asking.

### Persisting the path

**Claude Code, interactive** — the supported route:

```
/plugin configure nerdynik-plaud-toolkit@nerdynik
```

**Claude Code, at install time** — `claude plugin install nerdynik-plaud-toolkit@nerdynik --config glossary_path=<path>`. This flag only applies during install, so it's no help for an already-installed plugin.

**Editing settings directly** — for an installed plugin, this is the route you can perform on the user's behalf. Add to `~/.claude/settings.json`, preserving everything already in the file:

```json
{
  "pluginConfigs": {
    "nerdynik-plaud-toolkit@nerdynik": {
      "options": { "glossary_path": "/absolute/path/to/Transcription Glossary.md" }
    }
  }
}
```

The key is the full `plugin@marketplace` identifier, and the value goes under `options`. Confirm before writing, show what changed afterward, and mention that the plugin may need a reload or restart to pick it up.

**Claude Desktop** — install and manage plugins under **Customize → Plugins** in the left sidebar. If that surface exposes a configuration field for this plugin, use it. If it doesn't, fall back to the settings-file edit above when a Claude Code settings file exists on the machine, and otherwise just tell the skill the path each session — the conventional vault location in step 4 means that's usually a one-line answer, not a hunt.

**Any other AI tool** — there's no plugin configuration to write. Rely on the conventional location instead: keep the glossary at the knowledge base root under the standard filename, and state that path when starting work.

Persisting is a convenience, not a requirement. A glossary in a predictable place inside the knowledge base is found in step 4 with no configuration at all — which is the main reason to prefer that location.

## Writing transcript-derived content

- Record the recording's own identifier alongside anything derived from it, so the transcript can be pulled back up later. A derived note that can't be traced to its source is unverifiable.
- Cross-link derived notes to the glossary whenever a correction was applied.
- Distinguish observed from inferred throughout. "Discussed the Q3 timeline" is observed; "the timeline is slipping" is inference and needs its evidence attached.
- If the vault follows a domain structure — for Professional Services work, [[nerdynik-obsidian-vault-organization]] — file derived content per that taxonomy and follow its rule that moves and renames happen inside the notes app, never via raw filesystem calls.

## Authentication

`login` opens a browser for OAuth. **Only invoke it reactively**, when another call fails on authentication — never proactively at the start of a session. Never call `logout` unless the user explicitly asks to disconnect the account.

## What isn't confirmed

Treat these as open until verified against a live account, and say so rather than assuming:

- Whether `date_from` / `date_to` are interpreted in UTC or account-local time. It matters most for recordings near midnight, where the two dates diverge.
- What `data_error_code` values mean. The value `10` appears on perfectly healthy notes, so **a non-zero code is not by itself a failure signal**.
- How the `speaker` field gets populated — enrolled voice profiles, attendee metadata, or something else. This determines whether identity coverage can be improved at the source, which would beat correcting downstream.
- Behavior on a recording that is still processing: whether a status field exists, or blocks simply return empty.
