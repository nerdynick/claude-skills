# Assets

Files we hold rather than notes we wrote — decks, PDFs, spreadsheets, images, diagrams, sample data,
exports. Read this before filing one, and before adding to an asset index.

Two folders, split the same way `Resources.md` is:

| Folder | Holds |
|---|---|
| `Customers/<Customer>/Assets/` | Material about the customer that **spans projects** — brand kit, company overview deck, reference architecture, data dictionary, standard security questionnaire, an org chart they sent us |
| `Customers/<Customer>/Projects/<Project>/Assets/` | Material **specific to one project** — requirements documents, sample data files, screenshots, exported reports, diagrams received, draft deliverables |

Create either when the first file actually arrives, not preemptively. Don't duplicate across the
two: an asset that serves the whole account lives at customer level even if only one project uses it
today, and the project's index links up to it rather than holding a second copy.

**`Resources.md` and `Assets/` are opposites and both are needed.** `Resources.md` points *outward*
at systems we don't hold — a SharePoint site, a repo, a Slack channel. `Assets/` holds the files
themselves. When a file lives in the customer's SharePoint and we haven't been given a copy, that's
a `Resources.md` pointer, not an asset.

## The index is the whole point

Every `Assets/` folder carries one Markdown index beside the files, named for its scope so it
resolves from anywhere without a path — `Acme Corp Assets.md` at customer level,
`Acme Corp - Data Platform Assets.md` at project level. Same reasoning as the DSU alias rule: a file
called `Assets.md` in forty folders is ambiguous to every wikilink in the vault.

**Vault search reads Markdown. It cannot read a PDF, a `.pptx`, or an `.xlsx`.** Every binary in the
vault is invisible to `start_search` — so the index entry is the *only* searchable surface that file
has. That's what the index is for, and it's why a one-line entry restating the filename is worse
than useless: it adds an item to a list without making anything findable.

So **write down what's inside the file, not just what it's called.** Whatever an agent or a colleague
would otherwise have to open the file to learn — the decision it records, the figures it carries, the
architecture it shows, the people named on it, the assumptions it rests on — belongs in the entry.

One entry per asset:

```markdown
### Q3 Architecture Review.pptx
[[Q3 Architecture Review.pptx]]

- **What it is** — the customer's own current-state architecture, presented internally at their Q3 review.
- **From** — sent by their lead architect over email, 2026-08-14. Not a published document.
- **Covers** — 14 source systems feeding a central warehouse; the two integrations already flagged
  for retirement; their stated 18-month target state. Slide 9 carries the only written version of
  the data-retention rule we've been told about.
- **Status** — current. Supersedes [[2025 Architecture Overview.pdf]].
- **Related** — [[Acme Corp - Data Platform Project Background]]
```

- **Provenance is load-bearing.** Who gave it to us, how, and when. A "current" architecture diagram
  from eighteen months ago is a different claim from one sent last week, and the filename never says
  which it is.
- **Mark superseded assets superseded**; don't delete them and don't silently drop them from the
  index. What we were working from at the time explains decisions later.
- **Flag anything customer-confidential** in the entry, so nobody pastes it into a deck without
  knowing.
- **Group under `##` headings once a folder passes ~30 assets**, rather than letting one flat list
  grow past scanning.

**Write back when you open an asset.** If some other task makes you read one of these files, put what
you learned into its entry in the same session. The second read should be cheaper than the first, and
that only happens if the first one was recorded.

## Rename files that arrive with useless names

Screenshots are the common case. The macOS screenshot tool names them
`Screenshot 2026-09-11 at 3.45.12 PM.png` — and `Screen Shot …` with a space on older versions —
which says only when it was taken. Obsidian's own pasted-image default (`Pasted image
20260911154512.png`), Windows' `Screenshot (12).png`, and the `IMG_4821.jpg` / `image.png` /
`document.pdf` family are all the same problem: a filename carrying no information about content.

Left alone, these are the worst assets in the vault. They're binaries, so search can't read them,
and their names don't help either — the index entry becomes the only thing standing between the file
and total invisibility.

**Rename on the way in.** A file being filed for the first time has nothing pointing at it yet, so
renaming it is safe and is the one moment it will ever be safe. Once it's in `Assets/` and the index
or a note links to it, the hard rule takes over and renaming has to happen inside Obsidian.

Build the name from two sources, in this order:

1. **The conversation it arrived in.** Why someone shared it is almost always the best description
   available — better than anything in the image, because it says what the screenshot was *for*.
2. **The image itself.** Read it. The application or system shown, the page or dashboard title,
   the environment, the visible account or ticket identifier, an error message, the names on a
   profile card.

Name it for what it shows, and append the capture date in ISO form when the screenshot is a claim
about a moment — a dashboard state, a metric, a queue depth, a directory profile:

```
Screenshot 2026-09-11 at 3.45.12 PM.png
  → Admin Console Retention Settings 2026-09-11.png

Screen Shot 2026-08-02 at 9.13.44 AM.png
  → Pipeline Failure - Ingestion Timeout Error.png
```

A screenshot of a live system is only true as of when it was taken, so that date isn't decoration —
drop it only when the content is genuinely timeless. Either way the capture date goes in the index
entry's provenance line, since a rename can lose it.

Two things to hold to:

- **Don't name it for something the image doesn't show.** A guessed system or environment name
  becomes a fact the moment it's a filename, and nobody re-checks a filename against its image. When
  you can't tell what you're looking at, say so in the entry and use a name that claims only what you
  can see — the original timestamp is a better name than a confident wrong one.
- **Look at what else got captured.** Screenshots are the most common accidental-disclosure vector
  in a vault, because they catch whatever else was on screen — an adjacent row of customer data, a
  notification banner, another tab, a credential in a terminal. Check the whole frame, not the part
  someone meant to share, and flag or crop anything sensitive before it's filed.

## What doesn't go in `Assets/`

- **Contracts** — SOWs, proposals, LOEs → `Contracts/`, which already exists for exactly this.
- **Web clippings** → they stay in `Clippings/` with their provenance frontmatter; wikilink to them.
- **Generated diagram exports** → beside their source, not here. `Org Chart.drawio.svg` sits next to
  `Org Chart.drawio` so the pair travels together.
- **Images pasted into a note** → these land wherever Obsidian's attachment setting sends them, which
  is not this folder. Filing an asset here is a deliberate act; check the setting so pasted images
  don't scatter (see [[obsidian-mechanics]]).

And the hard rule applies to assets as much as notes: **creating them here is safe, moving them is
not.** An embed or link resolves by filename, so relocating an asset from the filesystem breaks every
reference to it, silently.
