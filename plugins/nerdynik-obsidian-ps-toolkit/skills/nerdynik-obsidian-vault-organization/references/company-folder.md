# The Company Folder

The `<Company Name>/` subfolders and what each holds. The taxonomy skill covers `Organization/`
(our own people) and points here for the rest.

## `Branding/`

Our own branding guidelines — color palette with hex values, typography, logo assets, and any rules on how diagrams and decks should look.

This isn't only reference material: **every org chart generated anywhere in the vault is styled from it**, for customers and partners as much as for us, because we're the ones maintaining and presenting the charts. Check it before generating a chart; if it's absent or has no palette, fall back to defaults and say branding wasn't found rather than inventing one. See `org-charts-and-relationships.md` for how it maps onto Mermaid and DrawIO.

## `Customer Stories/` and `Blog/`

`Customer Stories/` is the company's catalogue over every customer's stories — links, status, and
what's cleared for external use, never a second copy of the prose. `Blog/` holds every non-customer
post outright and indexes the customer-specific ones. Both are specified under "Customer stories and
blog posts" above.

These are the company's assets even though the stories are written about customers, which is exactly
why the split exists: the writing belongs next to the work it describes, the catalogue belongs with
the company that uses it.

## `Marketing & Narrative/`

**One folder per narrative**, not one shared folder holding everything:

```
Marketing & Narrative/
  <Narrative Name>/
    ...research, drafts, supporting material for that narrative
```

Each narrative's research, positioning work, drafts, and supporting material stay together in its own folder. A single flat folder mixing several narratives makes it impossible to tell which research belongs to which — and narratives get revisited, so this matters over time.

## `Townhalls/`

Company All Hands. **One file per townhall**, named by date so they sort chronologically: `<YYYY-MM-DD> Townhall.md`.

Each file tracks the whole lifecycle, not just the recap:

- **Leading up to it** — agenda, topics expected, questions to raise. If the user is **presenting**, this is where their material, talking points, demo notes, and rehearsal feedback live. This is the part that's most often needed and most often lost.
- **The meeting itself** — findings, announcements, decisions, notable Q&A.
- **Summary** — what was covered, what changed, and any action items, wikilinked out to wherever they're tracked.

Create the file when the townhall is announced, not after it happens — the pre-meeting material is half its value.

## `Website Copy/`

**One folder per page of copy**:

```
Website Copy/
  <Page Name>/
    ...the copy itself
    ...supporting assets, or an index pointing to them
```

Each page folder holds its copy and the supporting assets that copy needs. When an asset isn't held in the vault — already live on a public website, or delivered separately — record it in an **index file in that page's folder** giving the asset name, where it lives, and how to get it. An asset that exists only as "someone sent it over once" is the thing that stalls a page revision a year later.

Practice-level `Website Copy/` folders follow the same per-page structure; wikilink between the two where a page spans both.

## `Philosophy & Background/`

Company philosophy and company background together in one folder — mission, values, operating principles, history, founding story, positioning. These are read together and cite each other constantly, which is why they share a folder rather than sitting apart.

Distinct from a customer's `Company Background/`, which is about *that customer*.

## `Resources.md`

A **single file** of pointers and lookup information for common company resources. Not a folder — one file people can scan:

- SharePoint sites and Confluence spaces — with their site path or space key, not just a URL
- Other internal wikis and documentation sites
- Git hosting — the org or group under GitHub/GitLab/Azure DevOps/Bitbucket, and who administers access
- Teams channels
- Slack channels and workspaces
- Shared drives, HR and expense systems, other internal tooling

For each: the name, the link or identifier, and one line on what it's for. This is the first place to look when the question is "where does the company keep X."
