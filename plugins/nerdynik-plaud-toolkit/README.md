# Plaud Toolkit

A Claude Code plugin: the official Plaud MCP server, plus a skill for interpreting what it returns correctly.

**⚠️ Claude Code only.** Because this is a Claude Code *plugin* (`.claude-plugin/plugin.json`), the skill here is only reachable from Claude Code — claude.ai and Claude for Microsoft 365 (Copilot Cowork) support standalone `SKILL.md` skills only.

```
/plugin install nerdynik-plaud-toolkit@nerdynik
```

## What Plaud is

[Plaud](https://www.plaud.ai/) makes AI voice recorders — the Note and Note Pro (phone-attached) and the NotePin (wearable) — with a companion app and cloud service. Recordings sync to a Plaud account, which transcribes them with speaker diarization across a wide range of languages, supports custom vocabulary, and generates structured AI summaries from a large template library.

The MCP server reads that account. It's **read-only**: no audio is uploaded, altered, or deleted.

## Structure

```
nerdynik-plaud-toolkit/
  .claude-plugin/
    plugin.json
  .mcp.json                              # the Plaud MCP server
  skills/
    nerdynik-plaud-recordings/
      SKILL.md                           # guardrails, retrieval strategy, glossary loop
      references/
        mcp-reference.md                 # tool schemas, response shapes, data model
```

## Why the skill exists

The API is straightforward. Interpreting its output correctly is not. Four properties of the data will produce confidently wrong results if you don't plan around them, and each one fails in a way that looks like success:

- **`get_file` returns everything inline** — metadata, the full transcript, the outline, and the notes in one response. On an hour-long recording that's an enormous single-call context cost with no way to page it back.
- **The "polished" transcript paraphrases.** It rewrites wording rather than just stripping filler, in ways that can change meaning. It's fine for skimming and unusable for quoting.
- **Diarization merges speakers.** One attributed turn regularly contains both sides of an exchange, so attributing a quote from the segment label alone is unsafe.
- **Proper nouns get mangled**, consistently and creatively — one short recording can render a single unfamiliar name four different ways. Uncorrected, those names get written into notes and cited later as fact.

The skill also handles the timestamp trap: `start_at` is UTC while the AI summary renders account-local time, and `created_at` is the upload time — roughly the *end* of the meeting, never its start.

## Setup

**One-time, per machine**, before Claude Code can use the server:

1. `npx -y @plaud-ai/mcp@latest install` — opens a browser; click **Authorize**.
2. Fully restart Claude Code (not just the window) so it picks up the authorized session.
3. To re-authenticate from inside a session later, just ask: "Log me into Plaud."

Requires Node.js ≥ 20 and a Plaud account. MCP servers a plugin declares still go through per-server approval, so Claude Code will ask before the server starts.

Tools exposed: `login`, `logout`, `get_current_user`, `list_files`, `get_file`, `get_note`, `get_transcript`.

## The glossary

The single highest-leverage thing in this workflow: a living record of how the transcription renders the names, products, and jargon specific to your world. The skill reads it before interpreting anything and proposes additions as it finds them.

**Keep it in your knowledge base, not in a loose file.** If you have an Obsidian vault, notes repo, or team wiki, put it at the root as `Transcription Glossary.md`. That way it sits with the notes the corrections feed into, it's already backed up and synced, other people can extend it — and the skill finds it by convention with no configuration at all.

The skill will suggest exactly this when it can tell a vault exists, and offer to create the file and save the path for you.

### Optional configuration

| Field | Value |
|---|---|
| **Transcription glossary file** | Path to the glossary. Optional. |

Leave it blank if you keep the glossary at the conventional location above, or don't have one yet.

To set it later:

- **Claude Code** — `/plugin configure nerdynik-plaud-toolkit@nerdynik`
- **At install** — `claude plugin install nerdynik-plaud-toolkit@nerdynik --config glossary_path=<path>`
- **By hand** — add to `~/.claude/settings.json`:

  ```json
  "pluginConfigs": {
    "nerdynik-plaud-toolkit@nerdynik": {
      "options": { "glossary_path": "/path/to/Transcription Glossary.md" }
    }
  }
  ```

- **Claude Desktop** — **Customize → Plugins** in the left sidebar

The skill resolves the path in that order and falls back to the conventional vault location, so it keeps working even on surfaces that don't expose plugin configuration.

**Glossary entries are proposed, never written autonomously.** A wrong entry is worse than a missing one, because it launders a guess into an authority that later work trusts.

## Related

Filing transcript-derived content into a Professional Services vault structure is covered by [`nerdynik-obsidian-ps-toolkit`](../nerdynik-obsidian-ps-toolkit), whose daily-summary workflow consumes recordings from this plugin. The two are independent — that plugin works with any recording source, and this one doesn't assume a notes vault exists.
