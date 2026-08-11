# Plaud MCP reference

Tool surface, response shapes, and data model for the `plaud` MCP server (`@plaud-ai/mcp`). Read this before writing code against the API or debugging an unexpected response. The behavioral rules built on top of it are in `SKILL.md`.

Everything below was confirmed against a live account except where marked **unconfirmed**. When a real response disagrees with this document, trust the response — plugin and service updates change behavior, and account-level customization changes content.

## Tool surface

Seven tools: `login`, `logout`, `get_current_user`, `list_files`, `get_file`, `get_transcript`, `get_note`.

---

## `list_files`

Enumerates recordings, with optional filtering.

**`page_size` has an undocumented minimum of 10.** Anything lower fails:

```
Failed to list files: Error: page_size: Input should be greater than or equal to 10
```

The schema doesn't mention this. Don't try `page_size: 5` to be economical with context.

**The response shape changes depending on whether filters are set** — any parser must handle both:

| Call | Shape |
|---|---|
| Unfiltered | `{ type, data[], page, page_size }` |
| Filtered (`query` / `date_from` / `date_to`) | `{ data[], scanned, matched, truncated }` |

Note there is **no `type` field** on filtered responses.

`page` and `page_size` are **ignored** whenever any filter is set.

### `truncated` is the field that matters

Filtering is performed by the server *after* scanning a bounded window of the most recent recordings — roughly the 500 most recent, as several pages of a hundred each. When `truncated: true`, the result set is incomplete and older matches exist that were never scanned.

Surface this to the user. Reporting "no results found" on a truncated scan is a wrong answer, not a null one.

### `query` semantics

Case-insensitive substring match on the **recording name only**. It does not search transcript content.

Recording names are auto-generated and tend toward the topical (`08-07 Consultation: Northwind — Platform Migration`), which makes name search surprisingly good at finding a specific customer meeting — and blind to any topic discussed in a meeting whose title doesn't mention it.

### Unconfirmed: date filter timezone

Whether `date_from` / `date_to` are interpreted as UTC or account-local is **unconfirmed**; the schema says "the server's timezone." For recordings during the middle of the working day the two interpretations agree, which makes casual testing inconclusive.

It matters for recordings near midnight — an evening meeting is already the next day in UTC. Verify with a late-evening recording before relying on date boundaries.

---

## `get_file` — the context bomb

Returns *everything* about a recording in one response: metadata, a presigned audio URL, the entire transcript inline, the outline, and the AI notes.

Recordings routinely run 30–65 minutes (`duration` values in the millions of milliseconds). A single `get_file` on an hour-long recording consumes an enormous share of the context window and cannot be paged back.

**Call it only when you need the `presigned_url` for the audio, or want everything at once on a genuinely short recording.** Otherwise: `get_note` → `get_transcript(block="outline")` → paged `get_transcript`.

### Structure

```
id, name, created_at, serial_number, start_at, duration, presigned_url
source_list[]   → data_type: "transaction" | "outline" | "transaction_polish"
note_list[]     → data_type: "auto_sum_note"
```

The audio URL is an `.mp3` on S3 with roughly a 24-hour expiry (`X-Amz-Expires=86400`).

Each `source_list` entry carries `data_content` and `data_link`. **`data_content` is a JSON-encoded string, not a nested object** — it must be parsed.

| `data_type` | Content location |
|---|---|
| `transaction` | Full content inline; `data_link` empty |
| `outline` | Full content inline; `data_link` empty |
| `transaction_polish` | `data_content` is **empty**; content sits behind a `data_link` presigned URL with a **five-minute** expiry |

That five-minute expiry only matters if you're resolving the link yourself. Requesting the block through `get_transcript` avoids it entirely — see below.

---

## `get_transcript` — the workhorse

Paginated and block-selectable. Returns:

```
file_id, block, total, offset, limit, returned, next_cursor, segments[]
```

- `limit` defaults to 50, maximum 500. A 14-minute recording produced 34 segments; expect roughly 100–200 for an hour.
- `limit: 500` will usually pull an entire recording in one page — convenient, but it recreates the `get_file` context problem. Choose deliberately rather than reaching for it by default.
- **`next_cursor` is opaque base64.** Treat it as opaque. There is no `offset` *input* parameter, only `cursor`, so seeking into the middle of a long recording means walking pages sequentially from the start.
- **The server resolves the `transaction_polish` S3 link for you.** Requesting `block: "transaction_polish"` returns parsed segments directly; you never handle the short-lived presigned URL.

### Unconfirmed

Whether `outline` respects `limit` / `cursor` or always returns whole. The schema notes that pagination "only applies to blocks returned as an utterance list," which suggests outline comes back complete — but this is unverified. Outlines are small enough that it rarely matters.

---

## `get_note`

Returns only the `note_list` array. Far lighter than `get_file`, and the correct **first call** for "what happened in this meeting."

`auto_sum_note` is the observed type. A `consumer_note` type reachable only via a presigned URL is documented elsewhere but was **not observed** — it may be a manual-notes feature that isn't in use, or may no longer exist. Confirm before writing handling logic for it.

**`data_error_code: 10` appears on perfectly healthy notes.** Do not treat a non-zero `data_error_code` as a failure signal without independent evidence about what the codes mean.

### Note structure is not stable

Section headings vary between recordings. One recording used `## Next Steps` where another used `## Next Arrangements` for the same purpose. The `> Date:` line was full-precision in one and date-only in another. `> Location:` was an unfilled placeholder in both observed samples.

**Do not parse `auto_sum_note` by exact heading match.** Match loosely, or read it as prose.

Elements that were consistent:

- A `>` blockquote header carrying Date / Location / Participants
- `## Meeting Notes` with `###` topic subsections
- A checkbox list of follow-ups
- A final `## AI Suggestions` blockquote flagging unresolved items — genuinely useful, since it surfaces open decisions the participants left dangling

---

## `login` / `logout` / `get_current_user`

`login` runs an OAuth flow that opens a browser. Invoke it **only reactively**, after another call fails on authentication. Never call `logout` unless the user explicitly asks to disconnect.

`get_current_user` identifies the signed-in account — useful for confirming which account you're reading before doing anything a user might attribute to the wrong one.

---

## Data model

| Field | Meaning | Trap |
|---|---|---|
| `duration` | Recording length in **milliseconds** | `1811000` is ~30 minutes, not ~30 seconds |
| `start_time` / `end_time` | Per-utterance offsets in **milliseconds from recording start** | Not wall clock, and not rendered as timestamps anywhere |
| `start_at` | Recording start, **UTC** | Looks local. It isn't |
| `created_at` | ≈ `start_at + duration` | This is the upload/finalize time, i.e. roughly the **end** of the meeting. Never read it as the start |
| `serial_number` | Epoch-ms-like value tracking `start_at` | No known independent use |
| `speaker` | Resolved identity where a voice profile matched | Falls back to `Speaker N` |
| `original_speaker` | Raw diarization label | Always `Speaker N` |

### Two timezones in one response

`start_at` is UTC while the AI summary body renders account-local time. A recording with `start_at` of `2026-08-07T22:08:17` carried a summary header reading `Date: 2026-08-07 16:08:17` — a six-hour difference, the account's local offset at that date.

Wall-clock time for an utterance is `start_at` (UTC) `+ start_time` ms.

This is what makes utterances cross-referenceable against chat and calendar timestamps — the most useful property in the data model for resolving identity and settling disputes about what was said when.

**Don't hardcode the offset.** It changes with daylight saving.

### Unconfirmed

- How `speaker` gets populated: enrolled voice profiles, attendee metadata, or something else. Determines whether identity coverage can be improved at the source rather than corrected downstream.
- Behavior on a recording still being processed — whether a status field exists, or blocks return empty.

---

## Environment notes

Observed when writing transcript-derived content to disk through a filesystem MCP server. Not Plaud-specific, but they recur in this workflow:

- Large writes **time out intermittently and succeed on a single identical retry.** Don't assume a partial write, and don't defensively rewrite in chunks — that turns one clean file into several partial ones.
- Directory creation must be **strictly sequential**: parent before child.
- Exact-match edits work cleanly when the target text matches precisely, whitespace included.
- Reading the tail of a file is a reliable way to verify a write landed.
