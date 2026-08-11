# Vikunja mapping and mechanics

How the conventions in both skills land on Vikunja, plus the mechanics needed to execute them through the `vikunja` MCP server. Read this when actually creating or querying things; the skills themselves stay tool-agnostic.

## Capability mapping

Against [`capability-contract.md`](capability-contract.md):

| Capability | Vikunja | Notes |
|---|---|---|
| Containers | Projects | Nestable via a parent project; no documented depth limit |
| Cross-container tags | Labels | **Global per user**, not scoped to a project — this is what makes the practice/partner correlation work |
| Saved queries | Saved filters | Personal, cross-project, appear in the sidebar with a filter icon |
| Hierarchy | Parent/subtask relations, and child projects | Both exist; use task relations for OKR trees, child projects for customer grouping |
| Dates | `due_date`, `start_date`, `end_date` | Distinct fields |
| Progress | `percent_done` | 0–100 |

All six are native. No convention in either skill is degraded on Vikunja.

## Data model notes

- **Labels are global to the user, not the project.** A label created while working on one customer is immediately available on every other. This is a feature for correlation and a hazard for hygiene: the namespace is flat and shared, so the prefix conventions in the skills are what keep it navigable.
- **Projects nest.** A parent project groups children in the sidebar, but the parent name is *not* shown in cross-project views. That's why project titles must be self-describing — see the naming rules in the task-list-organization skill.
- **Archiving** hides a project from working views and makes it read-only, reversibly. This is the correct end state for a finished engagement — never delete.
- **Views (list, kanban, gantt, table) are per-project display settings.** Buckets belong to a kanban view. Treat both as presentation: never encode a fact in a bucket that isn't also in a field or label, or two people using different views will disagree about reality.
- **Priority is 1–5.** Vikunja's docs define the range but not authoritative names; the skills use `>= 3` as the "high" threshold, matching Vikunja's own filter example.
- **Favorites** pin a project to the top of the sidebar — useful for the handful of active engagements, and a good weekly-review trigger when the list drifts out of date.

## Filter syntax

Two dialects, and mixing them is the most common source of a filter that silently returns nothing.

| | UI filter | API filter (what the MCP server sends) |
|---|---|---|
| Field case | camelCase — `dueDate`, `percentDone` | snake_case — `due_date`, `percent_done` |
| Labels / assignees | by **name** — `labels in urgent` | by **ID** |

Fields: `done`, `priority`, `percentDone`, `dueDate`, `startDate`, `endDate`, `doneAt`, `assignees`, `labels`, `project`, `reminders`, `created`, `updated`.

Operators: `=`, `!=`, `>`, `>=`, `<`, `<=`, `like` (with `%` wildcards), `in` and `not in` (comma-separated). Combine with `&&` and `||`.

Date math anchors on `now` or a fixed date with `||`, then adds units `s m h d w M y`:

```
now/d          start of today
now+7d         a week out
now-1M/M       start of last month
2026-03-11||+1w
```

Worked examples:

```
done = false && due_date < now                       overdue
done = false && due_date < now/d+7d                  due within a week
done = false && priority >= 3                        high priority, open
labels in practice/data-platform && done = false     one practice, everywhere
assignees in currentUser && done = false             my open work
done = false && due_date > now/d && due_date < now/M+1M   rest of this month
```

Resolve label names to IDs with `vikunja_labels` before building an API filter that references them, and use `vikunja_filters` to validate a filter string before saving it.

## MCP tools

Provided by `@democratize-technology/vikunja-mcp`:

| Tool | Use for |
|---|---|
| `vikunja_auth` | Connection status, token refresh — check here first when anything 401s |
| `vikunja_tasks` | Create, list, get, update, delete, assign, comment, bulk ops, relations, reminders |
| `vikunja_projects` | CRUD, hierarchy, sharing, archiving |
| `vikunja_labels` | CRUD, and apply/remove on tasks |
| `vikunja_filters` | Create, list, validate, and build filters |
| `vikunja_templates` | Create templates, instantiate a project from one |
| `vikunja_batch_import` | Up to 100 tasks from CSV or JSON |
| `vikunja_teams` | List, create, delete teams |
| `vikunja_users` | Current user, search, settings — **JWT only** |
| `vikunja_webhooks` | Webhook CRUD, list events |
| `vikunja_export_project` | Export a project and optionally its children — **JWT only** |

### Authentication

Two credential types, and the difference determines which tools work:

- **API token** (`tk_…`, the default): tasks, projects, labels, teams, webhooks. Cannot reach user-specific endpoints. This is what the plugin's `userConfig` prompts for, and it covers everything either skill needs.
- **JWT** (`eyJ…`): full access including user management and export, but typically expires after 24 hours. Only worth it for a one-off export.

If `vikunja_users`, `vikunja_export_project`, or `vikunja_request_user_export` fails with a permissions error, an API token is in use and that's expected — don't try to work around it, tell the user a JWT is required for that specific operation.

## Operational rules

- **Confirm the target instance before writing anything.** Call `vikunja_auth` and report which instance and user you're operating as. There is no undo on a bulk update.
- **Read before you write.** List existing projects and labels before creating any. The most common damage this plugin can do is a near-duplicate label (`partner/databricks` alongside `partner/Databricks`) that silently splits every filter that depends on it.
- **Batch with care.** `vikunja_tasks` bulk operations and `vikunja_batch_import` apply to up to 100 tasks at once. Show the user the full list and get explicit confirmation before running one.
- **Never delete a project.** Archive it. Deletion takes its tasks with it, and the history is usually the point.
- **Prefer `percent_done` over a "done" subtask** for partial progress, so the OKR skill's scoring reads directly off the field.
