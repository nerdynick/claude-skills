# Task Management

A Claude Code plugin: conventions for running task lists that stay legible at scale, plus the Vikunja MCP server for acting on them.

**⚠️ Claude Code only.** Because this is a Claude Code *plugin* (`.claude-plugin/plugin.json`), the skills here are only reachable from Claude Code — claude.ai and Claude for Microsoft 365 (Copilot Cowork) support standalone `SKILL.md` skills only. Anything that needs to work from those surfaces has to also exist under `../../skills/`.

```
/plugin install nerdynik-task-management@nerdynik
```

## Structure

```
nerdynik-task-management/
  .claude-plugin/
    plugin.json                            # manifest + userConfig for Vikunja credentials
  .mcp.json                                # Vikunja MCP server
  references/                              # shared by both skills
    capability-contract.md                 # what any tracker must provide; fallbacks when it doesn't
    vikunja.md                             # Vikunja mapping, filter syntax, MCP tools, operational rules
  skills/
    nerdynik-task-list-organization/       # projects, labels, role-level views
    nerdynik-okr-task-management/          # long-term → mid-term → short-term goals, per scope
```

## Skills

| Skill | Use it for |
|---|---|
| `nerdynik-task-list-organization` | Setting up tracking for a new engagement, deciding where a task belongs, designing or cleaning up a practice/partner label taxonomy, building role-level views for a manager or practice leader, running a weekly review, auditing an existing workspace. |
| `nerdynik-okr-task-management` | Writing long-term objectives, defining mid-term key results, breaking a quarter into short-term SMART goals, weekly check-ins, scoring at quarter close, auditing a goal set for quality. Handles several independent OKR sets at once, scoped per department, practice, or person. |

The two share a vocabulary and stay out of each other's way: delivery work lives in normal projects, goals live in their own tree, and an execution task is *related* to a key result rather than nested under it.

### Horizons

The three goal horizons go by two interchangeable names, and both are accepted:

| | Also called | Artifact |
|---|---|---|
| **Long-term** | yearly, annual, 1yr+ | Objective |
| **Mid-term** | quarterly | Key Result |
| **Short-term** | monthly | SMART goal |

### Scopes

One person often runs several OKR sets independently — their own, plus one per department or practice they lead. Each scope gets its own project (`OKR — Marketing — 2026`), never a shared one, so reviews and audiences stay separate. Cross-scope roll-up views are what keep that reviewable: one "at risk everywhere" query beats opening four projects a week.

## The core idea

**Projects answer "where does this work live." Labels answer "what does this work relate to."**

One project per unit of delivery, titled `<Customer> — <Project>` so it reads correctly in cross-project views where the parent folder isn't shown. Everything that cuts across projects — practice, partner, department, work type — is a label from one namespaced global list (`practice/data-platform`, `partner/databricks`).

Keeping those axes orthogonal is what makes role-level views possible: a practice leader's "everything my practice is on, across every customer" is one saved query, not a weekly reporting exercise.

## Tool adaptability

Vikunja is the default, not a requirement. Both skills are written against a six-capability contract — containers, cross-container tags, saved queries, hierarchy, dates, numeric progress — documented in `references/capability-contract.md` along with the fallback for each when a tool lacks it.

Vikunja provides all six natively, so nothing is degraded there. To adapt to another tracker, map the six capabilities and add a `references/<tool>.md` alongside `vikunja.md`. Keep the label vocabulary identical across tools; migrations and cross-tool reporting depend on the names being stable even when the mechanism isn't.

## Vikunja setup

The plugin bundles the [vikunja-mcp](https://github.com/democratize-technology/vikunja-mcp) server (`@democratize-technology/vikunja-mcp`) and prompts for two values when you enable it:

| Field | Value |
|---|---|
| **Vikunja API URL** | Your instance's API endpoint *including* `/api/v1` — e.g. `https://vikunja.example.com/api/v1` |
| **Vikunja API token** | A personal API token from **Settings → API Tokens**, starting with `tk_` |

The token needs read/write on tasks, projects, and labels. It's stored in your OS keychain, not in `settings.json`.

Both fields are optional — leave them blank if you use a different tracker, and the skills still work as conventions with the MCP server simply unavailable.

Requires Node.js ≥ 20. MCP servers a plugin declares still go through per-server approval, so Claude Code will ask before the Vikunja server starts.

### API token vs JWT

An API token (`tk_…`) covers tasks, projects, labels, teams, and webhooks — everything either skill needs. It cannot reach user-specific endpoints, so `vikunja_users`, `vikunja_export_project`, and `vikunja_request_user_export` will fail with a permissions error. That's expected; those need a JWT (`eyJ…`), which expires after about 24 hours and is only worth obtaining for a one-off export.

## Safety

`references/vikunja.md` sets the operational rules the skills follow. The ones worth knowing up front:

- The target instance and account are confirmed and reported before any write.
- Existing projects and labels are listed before new ones are created — a near-duplicate label silently splits every filter built on it.
- Bulk operations (up to 100 tasks) are shown in full and confirmed before running.
- Projects are archived, never deleted.
