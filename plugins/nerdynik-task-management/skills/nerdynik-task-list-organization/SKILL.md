---
name: nerdynik-task-list-organization
description: Use when creating, structuring, auditing, or reporting on task lists and projects in a task tracker (Vikunja by default) — setting up tracking for a new customer engagement, deciding which project a task belongs in, naming or reorganizing projects, designing or cleaning up a label taxonomy for practices and partners, building role-level views for a manager or practice leader who needs to see across departments and engagements, or running a weekly review. Covers customer/project work and internal company-wide tracking alike. Not for OKRs or goal setting — use nerdynik-okr-task-management for those.
---

# Task List Organization

Keeps task tracking legible when there are more engagements, practices, and partners than one person can hold in their head. The conventions below are the ones that survive scale; the reasoning is included because you'll hit cases they don't cover and will need to extend them consistently.

Written tool-agnostically. For Vikunja mechanics — filter syntax, MCP tools, the data model — read `${CLAUDE_PLUGIN_ROOT}/references/vikunja.md`. For any other tracker, read `${CLAUDE_PLUGIN_ROOT}/references/capability-contract.md` first to find what maps and what degrades.

## Before doing anything: confirm where you're writing

Never assume the instance or account. Confirm which tracker, which instance, and which user you're operating as, and say so before the first write. A task tree built in the wrong workspace is worse than none — it looks authoritative and nobody finds it.

Then **read before writing**: list the existing projects and labels. Almost every mess this skill exists to prevent starts as a near-duplicate of something already there.

## The two-axis model

This is the whole idea, and everything below follows from it:

> **Projects answer "where does this work live."** One project per unit of delivery, with one owner and one lifecycle.
> **Labels answer "what does this work relate to."** Practice, partner, department, work type — every axis that cuts *across* projects.

Keep the axes orthogonal. The failure that ruins a workspace is encoding a label axis as a project: a project per practice means an engagement spanning two practices has no home, and work gets duplicated or silently filed under one and lost to the other.

Test for which axis something belongs on: **can one task legitimately have two of them at once?** Two practices on one deliverable — yes, that's real. Two customer engagements for one task — no, that's two tasks. So practice is a label and engagement is a project.

## Projects

### Naming

Customer work is titled `<Customer> — <Project>`:

```
Acme Corp — Data Platform Migration
Acme Corp — Q3 Support Retainer
Globex — Kafka Assessment
```

Both halves, every time, even when the project sits nested under a customer parent. Cross-project views — saved filters, label views, search results, "my tasks" — show the project name **without its parent**, and those views are where the naming earns its keep. `Migration` tells you nothing in a list of forty; `Acme Corp — Data Platform Migration` tells you everything.

Use an em dash `—` as the separator, consistently. It never appears inside a customer or project name, so the title splits unambiguously when parsed for reporting.

Internal work uses the same shape with the function in the customer slot:

```
Internal — Recruiting
Internal — Practice Development
Marketing — Website Refresh
```

### Hierarchy

Nest for navigation, not for meaning:

```
Customers/
  Acme Corp/
    Acme Corp — Data Platform Migration
    Acme Corp — Q3 Support Retainer
  Globex/
    Globex — Kafka Assessment
Internal/
  Internal — Recruiting
  Marketing — Website Refresh
```

The parent folders make the sidebar navigable. They carry no information that isn't already in the child's title, which is deliberate — nothing breaks if a project is moved, and cross-project views lose nothing.

### One project per unit of delivery

A project should have one owner, one lifecycle, and an answerable "is this done?" A statement of work, a retainer period, an internal initiative. Not a whole customer relationship — that's the parent folder — and not a single deliverable, which is a task.

If you can't say what would make a project complete, it's probably a folder or a label.

### Closing

When an engagement ends: close or explicitly re-home every open task, then **archive** the project. Never delete it. The history is usually the point — it's what you'll want when the same customer comes back next year, and what a post-mortem needs.

## Labels

Labels come from one flat global namespace shared across every project. That's what makes cross-project correlation work at all, and it's also why an unmanaged label list becomes unusable within months. The prefix convention is what keeps it navigable.

### Namespace

Every label is `<axis>/<value>`, lowercase, kebab-case, no spaces:

| Prefix | For | Examples |
|---|---|---|
| `practice/` | The delivery practice or capability doing the work | `practice/data-platform`, `practice/app-modernization` |
| `partner/` | A partner or vendor the work involves | `partner/databricks`, `partner/confluent` |
| `dept/` | Internal department, for company-wide work | `dept/marketing`, `dept/recruiting` |
| `type/` | The nature of the work | `type/deliverable`, `type/admin`, `type/risk`, `type/follow-up` |
| `stage/` | Where a task sits in a workflow, when a workflow genuinely exists | `stage/blocked`, `stage/awaiting-customer` |

**No spaces, ever.** Filters take comma-separated label lists (`labels in practice/data-platform, partner/databricks`), and a space in a name makes those queries ambiguous or wrong. This constraint is why the whole scheme is kebab-case rather than prose.

**One casing, forever.** `partner/databricks` and `partner/Databricks` are two labels, and every filter built on one silently misses the other. Before creating a label, list the existing ones and match what's there.

### Rules

- **Adding an axis is a real decision.** A new prefix means every future task has one more thing to consider. Add one only when you can name the view it enables that's impossible today.
- **Don't label what a project already says.** A task in `Acme Corp — Data Platform Migration` doesn't need `customer/acme-corp`. It's noise, and it will drift out of sync with the project.
- **Label the task, not the project.** A project-level label doesn't propagate to tasks in most tools, so filters miss them. If every task in a project shares a label, apply it to the tasks — at creation, as a habit.
- **`stage/` is a last resort.** Status usually belongs in the tool's own fields — done, due date, assignee, priority. Reach for `stage/` only for states the tool can't express, like `stage/awaiting-customer`, where the distinction from "just not started" actually changes what you'd do.

## Role-level views

This is what the label discipline buys, and it's the payoff worth optimizing for. Each of these is a saved cross-project query, made once and then self-serve:

| Who | Question | Query shape |
|---|---|---|
| Practice leader | Everything my practice is on, across every customer | `labels in practice/data-platform && done = false` |
| Partner manager | Where is this partner engaged | `labels in partner/databricks && done = false` |
| Manager | What's late anywhere in my area | `labels in dept/marketing && done = false && due_date < now` |
| Anyone | My own open work | `assignees in currentUser && done = false` |
| Anyone | What's actually next | `assignees in currentUser && done = false && due_date < now/d+7d` |
| Delivery lead | Risks across the portfolio | `labels in type/risk && done = false` |

Two rules that keep these useful:

- **Name a saved view for the question it answers**, not the filter it runs — "Data Platform — open across customers", not "practice filter 3".
- **A view that's never empty is a backlog, not a view.** If the overdue view always has forty items, it has stopped conveying information. Either the work is genuinely late and that's the finding to report, or the due dates are aspirational and need fixing.

## Task hygiene

- **Titles carry a verb and an object**: "Draft migration runbook for Acme ingest tier", not "Runbook". Titles are read out of context in every cross-project view.
- **A due date means committed.** If a date is a guess, leave it empty and let priority carry the urgency. Fake due dates are the single fastest way to make every date-based view worthless.
- **Priority is comparative, not descriptive.** If everything is high, nothing is. Use the tool's high threshold sparingly and re-check it during review.
- **Assign every task, including your own.** Unassigned work is nobody's, and it makes every per-person view lie.
- **One task, one outcome.** "Set up environments and run the load test" is two tasks with different done conditions and probably different owners.

## Cadence

**Weekly review** — per person, 15 minutes:

1. Overdue view: for each item, complete it, re-date it with a real commitment, or drop it.
2. Unassigned or undated open work in your active projects: fix or close.
3. New engagements from the week: project created, labeled, first tasks in.

**Monthly** — per workspace owner:

1. Label list: merge near-duplicates, retire labels with no open tasks and no plausible future.
2. Projects with no activity: finished (archive), stalled (say so), or abandoned (close).
3. Saved views that are always empty or never empty: fix or delete.

## Setting up a new engagement

1. Confirm the customer parent exists, or create it.
2. Create `<Customer> — <Project>` under it.
3. Decide the labels once, up front: which `practice/`, which `partner/` if any. Reuse existing ones — list them first.
4. Create the tasks you know about, each with an owner, and a due date only where there's a real commitment.
5. Add a repeating `type/admin` task for the engagement's own cadence — status report, check-in — so the recurring work is tracked rather than remembered.

## Auditing an existing workspace

Report before changing anything. Renaming projects and merging labels breaks saved views and other people's habits, so the user decides what's worth the disruption.

Look for, in rough order of damage:

1. **Near-duplicate labels** — casing or spelling variants splitting a filter. Highest damage, cheapest fix.
2. **Label axes encoded as projects** — a project per practice or per partner. Expensive to fix; flag it and propose the target shape before touching anything.
3. **Projects whose titles aren't self-describing** — bare `Migration`, or a customer name with no project.
4. **Unlabeled open tasks** in projects where the rest are labeled — these are invisible to every role view.
5. **Stale due dates** — a large overdue set usually means dates were used as intentions.
6. **Projects that should be archived.**

For each, give the count and one example. A user who sees "31 open tasks are missing a `practice/` label, e.g. #482" can decide; one who sees "labeling is inconsistent" can't.

## Working with the OKR skill

Personal and organizational goals do **not** live in this structure. Objectives and key results belong in [[nerdynik-okr-task-management]], which keeps its own tree — one per scope and year, so someone tracking several departments' goals has a separate set for each.

The bridge runs one way: an execution task tracked here can be *related* to a key result there. Don't copy it, and don't nest delivery work under an objective — the OKR tree stays small enough to read in one screen, and this is what keeps it that way.
