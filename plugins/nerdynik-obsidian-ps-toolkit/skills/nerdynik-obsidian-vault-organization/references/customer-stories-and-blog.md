# Customer Stories and Blog Posts

**Customer story, user story, use case, case study — all the same artifact**, and the vault uses
`Customer Stories` for all of them. Whichever word someone says, it means a written account of work
delivered for a named customer.

## Where they live, and why it's split

A customer story is always *about* a customer's project or projects, and it's always *an asset of*
the company — internal reference, external reference, and website material. Both are true, so the
vault splits along the difference between the writing and the catalogue:

| | Lives at | Holds |
|---|---|---|
| **The story itself** | `Customers/<Customer>/Customer Stories/<Customer> - <Title>.md` | The actual account: what the problem was, what was built, what changed |
| **The catalogue** | `<Company Name>/Customer Stories/` | An index note linking out to every customer's stories, plus what the company needs across all of them |

**Stories sit at customer level, not project level**, because one routinely spans several projects,
and a story about two projects can't live inside one of them. Name the file with the customer prefix
(`Acme Corp - Lakehouse Migration.md`) so it resolves as a wikilink from anywhere without a path.

**The company index links; it never copies.** A second copy of the prose in the company folder is
the failure here — it ages independently, and the published version ends up sourced from whichever
copy someone found first. The index carries the link, the one-line pitch, and the status.

The company folder also holds what's true *across* stories rather than inside any one of them: which
are cleared for external use, the house structure a story follows, and the running list of work
worth writing up but not yet written.

## Blog posts

Same split, but only for the subset that's about a customer:

- **About a specific customer** → `Customers/<Customer>/Blog/`, indexed from `<Company Name>/Blog/`.
  Identical treatment to a customer story, for the same reason.
- **About anything else** — a technology, a practice's point of view, a conference, a product
  opinion, a release — → `<Company Name>/Blog/` directly. That's the common case, and it has no
  customer folder to live in.

So `<Company Name>/Blog/` does two jobs at once: it *holds* every non-customer post, and it *indexes*
the customer ones. Keep the two visibly separate inside it rather than interleaving a list of links
with a set of actual posts.

A post that starts generic and acquires a named customer moves to the customer folder — which is a
move, so propose it rather than doing it, and leave the index entry pointing at the new location.

## Tagging a customer story

Every story carries frontmatter that makes the catalogue queryable. Four axes matter, because they
are what someone searches by when looking for a story to reuse:

```yaml
---
type: customer-story
customer: "[[Acme Corp]]"
projects: ["[[Acme Corp - Data Platform]]"]
industries: [...]      # the customer's or the project's industry
cloud: [...]           # AWS, Azure, GCP — whichever the work was built on
practices: [...]       # which of our practices delivered it
partners: [...]        # partners the work involved
status: draft          # draft | internal | approved-external | published
---
```

**Take the permitted values from the company's own lists — don't invent them per story.** The
industry taxonomy, the practice names, and the partner names are the company's, and they live in
its own material: a Company Background note, brand guidelines, or a dedicated skill. A story that
coins its own industry label is invisible to every query written against the real one, and that's
the whole failure mode the controlled-vocabulary rule exists to prevent (see
[[obsidian-mechanics]]).

If you can't find the company's list, ask for it rather than guessing — and say in the note that the
tags are unverified until someone confirms them.

## Status, and the permission question

`status` is not decoration. A customer story names a customer, and **naming a customer publicly is
usually something the customer has to agree to** — a story can be perfectly true and still not
cleared to leave the building.

- **`draft`** — being written.
- **`internal`** — usable as internal reference and in sales enablement, not outside.
- **`approved-external`** — the customer has agreed to be named. **Record who agreed, when, and
  where that's written down.** A remembered approval is not an approval.
- **`published`** — live. Link to the `Website Copy/<Page Name>/` folder holding the published
  rendering, and to the public URL.

Where a customer hasn't approved naming, the story can still be written and used **anonymized** —
"a global housing nonprofit" rather than the name. Mark it as anonymized explicitly, because the
un-anonymized draft usually still exists a folder away and the two get confused.

## What links where

- The story links to its customer, its projects, the practices and partners involved, and its
  published page.
- `<Company Name>/Customer Stories/` links to every story.
- `Practices/<Practice>/Case Studies/` links to the stories that practice delivered — it doesn't
  hold copies either.
- A narrative in `Marketing & Narrative/` cites the stories it draws on.
- `Website Copy/<Page Name>/` is the *published rendering*, not the source. Keep the story as the
  source and the page as the output, linked, rather than editing the two in parallel.
