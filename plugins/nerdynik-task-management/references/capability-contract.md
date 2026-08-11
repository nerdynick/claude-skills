# Capability contract

Both skills in this plugin describe *conventions*, not Vikunja features. The conventions rest on six capabilities. Any task tracker that provides them can carry the conventions unchanged; where one is missing, the fallback below applies.

Read this before adapting either skill to a tool other than Vikunja, and before concluding that a convention "can't be done" in some tool.

| # | Capability | Used for | If the tool lacks it |
|---|---|---|---|
| 1 | **Containers** — a named grouping of tasks | Projects: one per customer engagement or internal initiative | Fall back to a mandatory `project/<slug>` tag. Loses per-container permissions and archiving. |
| 2 | **Cross-container tags** — labels that apply across every container, from one flat global namespace | Practice, partner, department, and work-type correlation | Fall back to prefixed text in task titles (`[practice:data-platform]`) and rely on search. Loses reliable filtering; treat as a serious downgrade. |
| 3 | **Saved queries** — a stored filter over all containers, reachable in one click | Role-level views: what a practice leader or manager sees | Recreate the query manually each time, or script it. Views stop being self-serve, which is most of their value. |
| 4 | **Hierarchy** — parent/child between tasks, and ideally between containers | Objective → key result → monthly goal; epic → deliverable | Flatten one level and encode the parent in a tag. The OKR skill degrades the most here. |
| 5 | **Dates** — a due date per task, distinct from a start date | Time-bounding, cadence tasks, the "is this late" question | A due date alone is workable. With no dates at all, neither skill applies — pick a different tool. |
| 6 | **Progress** — a numeric completion value per task, not just done/not-done | OKR scoring, partially-met key results | Use a `score/0.3`-style tag updated at each check-in. Clumsy but functional. |

## What the conventions deliberately do *not* require

Avoid designing around these; they vary too much between tools and lock the conventions to one vendor.

- **Custom fields.** Encode meaning in labels and titles instead.
- **Automation rules.** Every convention here is maintainable by hand.
- **Comments or attachments** as a system of record. They're fine for discussion, but nothing structural should depend on reading them.
- **Kanban buckets** as data. Buckets are a per-view display concern; two people looking at the same project through different views must not see different facts.

## Applying a convention to a new tool

1. Map each of the six capabilities to the tool's equivalent, and write the mapping down next to this file.
2. For anything unmapped, take the fallback above and record that the convention is degraded — don't silently drop it.
3. Keep the *names* identical across tools. A practice is `practice/data-platform` everywhere. Migrations and cross-tool reporting depend on the vocabulary being stable even when the mechanism isn't.

The current mappings live alongside this file: `vikunja.md` for Vikunja. Add one file per tool.
