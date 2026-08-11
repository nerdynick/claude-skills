---
name: nerdynik-okr-task-management
description: Use when setting, structuring, tracking, scoring, or reviewing OKRs and goals in a task tracker (Vikunja by default) — writing long-term/yearly/annual objectives, defining mid-term/quarterly key results, breaking a quarter into short-term/monthly SMART goals, running a weekly check-in or quarterly review, scoring key results at close, or auditing an existing goal set for quality. Handles multiple independent OKR sets scoped separately — personal, per-department, per-practice, or company-wide — for someone tracking several at once, such as a manager or practice leader over multiple departments. Not for general project or customer task tracking — use nerdynik-task-list-organization for that.
---

# OKR and Goal Management

Runs objectives and key results inside a task tracker, so goals live where the work lives instead of in a spreadsheet nobody opens after week three.

The same discipline as [[nerdynik-task-list-organization]] applies — naming that reads out of context, labels as the correlation axis, no fake due dates — but the structure is separate and deliberately small. Read that skill for the general conventions; this one covers only what's different about goals.

Written tool-agnostically. For Vikunja mechanics read `${CLAUDE_PLUGIN_ROOT}/references/vikunja.md`; for any other tracker start with `${CLAUDE_PLUGIN_ROOT}/references/capability-contract.md`. This skill leans hardest on hierarchy and numeric progress, so check those two first when adapting.

## Before doing anything: confirm the scope and horizon

Two questions, both before touching anything, plus the usual confirmation of instance and account.

**Which scope?** A person often tracks several independent OKR sets — their own, and one per department or practice they lead. "My OKRs" is ambiguous the moment more than one set exists. If several are in play, ask; don't guess from context. See [Scopes](#scopes).

**Which horizon?** "Help me with my OKRs" means something different in January than in the third week of a quarter, and the wrong answer wastes the conversation:

- **Long-term / yearly** — setting or revising objectives
- **Mid-term / quarterly** — defining or scoring key results
- **Short-term / monthly** — breaking a key result into SMART goals
- **Check-in** — updating progress against what already exists

If OKRs already exist in that scope, read them before proposing anything. Most requests are amendments, not blank pages.

## The three horizons

Each horizon answers a different question, and the value comes from the seam between them. A goal set that skips a level either drifts (no objective) or stays abstract (no monthly).

| Horizon | Also called | Question | Artifact | Changes |
|---|---|---|---|---|
| **Long-term** | yearly, annual, 1yr+ | Where am I trying to get to? | Objective — qualitative, directional | Rarely. Revising mid-year should feel like a real decision |
| **Mid-term** | quarterly, per-quarter | What would prove I'm getting there? | Key Result — measurable outcome | Set at quarter start, scored at quarter end |
| **Short-term** | monthly, per-month | What specifically am I doing about it now? | SMART goal — concrete, dated | Every month |

The two naming schemes are interchangeable and both are in common use — long-term *is* yearly, mid-term *is* quarterly, short-term *is* monthly. Accept whichever the user says and answer in their vocabulary rather than correcting them into the other one. Labels and project names use the concrete form (`okr/monthly`, not `okr/short-term`) because the date-based labels beside them are concrete too.

**Per scope: three to five objectives for the year, two to four key results each, two or three monthly goals per active key result.** Past that you have a list, not a set of priorities, and nothing gets the attention it needed.

## Scopes

An OKR set belongs to a **scope** — whose goals these are. A person commonly runs several independently:

| Scope | Example |
|---|---|
| Personal | Your own professional goals |
| Department | Each department a manager owns, tracked separately |
| Practice | A practice leader's goals for their practice |
| Company | Org-wide objectives everyone else's ladder up to |

**Each scope gets its own project, and one scope never shares a project with another.** Scopes have different owners, different review cadences, and different audiences — a department's targets get discussed with that department, not alongside your personal development goals. Merging them means every view has to filter the others back out, and the objective cap stops meaning anything.

This follows the two-axis model from [[nerdynik-task-list-organization]]: scope is *where a goal lives*, so it's a project concern, not a label.

### How many scopes to run

Each scope is a real recurring cost — a weekly check-in, a monthly close, a quarterly review. Four scopes is four quarterly reviews. Before adding one, ask whether the goals genuinely need independent tracking or whether they're key results inside a scope that already exists. A department with two objectives you glance at quarterly is usually the latter.

When someone is tracking more than they can review, say so. The failure mode isn't the extra project, it's six scopes all going stale together.

## Structure

One project per **scope per year**, each holding a complete tree:

```
OKRs/
  Personal/
    OKR — Personal — 2026
  Marketing/
    OKR — Marketing — 2026
  Data Platform/
    OKR — Data Platform — 2026
```

The title carries `OKR — <Scope> — <Year>`, all three parts, for the same reason project titles do in [[nerdynik-task-list-organization]]: cross-project views show the project name without its parent folder, and an objective surfacing in a filter needs to say which scope and which year it belongs to. The leading `OKR` keeps every set sorted together.

Nest by scope for navigation. The folders carry nothing the titles don't, so moving a set breaks nothing.

Prior years stay as their own projects and get archived, never deleted — next year's baselines come from them.

Inside each project, three levels of task nesting:

```
Objective: Establish the data platform practice as a repeatable offering
├── KR: Ship 3 delivered engagements using the standard reference architecture   (Q1, 0–100%)
│   ├── Mar: Complete Acme migration phase 2 against the reference architecture
│   └── Mar: Publish the architecture decision record for the ingest tier
└── KR: Cut median time-to-first-value from 6 weeks to 4                          (Q2, 0–100%)
```

- **Objective** — a top-level task. Labeled `okr/objective`. Due at year end. Never scored directly; its score is its key results'.
- **Key Result** — a subtask of the objective. Labeled `okr/kr` and the quarter, `okr/2026-q1`. Due on the quarter's last day. Progress tracked as a numeric percentage, which is what makes scoring read straight off the record.
- **Monthly goal** — a subtask of the key result. Labeled `okr/monthly` and the month, `okr/2026-03`. Due on the month's last working day. Binary: met or not.

Objectives and key results **stay in this project**. Nothing else goes in it.

### The tree is not a task list

The most common way this structure dies is by becoming a dumping ground — every task related to a goal gets nested under it, and within a quarter the tree is 200 items and nobody reads it.

Execution work lives in its normal project under [[nerdynik-task-list-organization]], and is *related* to the key result, not nested under it. The relation gives you traceability in both directions; the separation keeps the goal tree small enough to read in one screen.

The test: **if it has a specific assignee and a delivery date, it's execution work.** If it's a statement about an outcome, it belongs here.

## Writing objectives

Qualitative, directional, and worth caring about. An objective is the sentence you'd use to explain what you're trying to change.

- ✅ "Establish the data platform practice as a repeatable offering"
- ❌ "Complete 5 data platform projects" — that's a key result wearing an objective's hat
- ❌ "Improve data platform" — no direction, nothing would count as progress

Write it so someone else could tell whether the year went well. If the objective is only meaningful to the person who wrote it, it won't survive the year.

## Writing key results

This is where goal sets fail, almost always the same way: **key results that measure output rather than outcome.**

- ❌ "Deliver the training program" — that's a deliverable. It's done or not, and doing it proves nothing.
- ✅ "80% of consultants certified on the reference architecture" — an outcome. The training is one way to get there, and if it doesn't work you'll know.

Each key result needs a **baseline, a target, and a unit**. "Cut median time-to-first-value from 6 weeks to 4" carries all three; "reduce time-to-value" carries none, and can't be scored.

Checks worth running against every proposed key result:

1. **Could I hit this and not advance the objective?** Then it's the wrong measure.
2. **Do I know the baseline?** If not, the first monthly goal is measuring it. That's a legitimate use of a month.
3. **Can I tell today whether I'm on track?** If the answer only arrives at quarter end, it's a milestone, not a key result.
4. **Is it within my influence?** Not fully within your control — that's too weak a bar for a goal — but influence, or scoring it teaches nothing.

Mark each key result **committed** (expected to reach 1.0) or **stretch** (0.7 is success). Do this at the start. Deciding afterward which kind it was is how scoring becomes theater.

## Monthly SMART goals

The monthly horizon is where a key result becomes something you can act on this week. Each letter maps to a specific part of the record — that mapping is the useful part of SMART, not the acronym:

| | Lives in | Failing looks like |
|---|---|---|
| **S**pecific | The task title — a verb and a concrete object | "Work on certification" |
| **M**easurable | A number or a binary condition in the title | "Make progress on the ADR" |
| **A**chievable | Sized to fit one month alongside real delivery work | Three months of work due the 31st |
| **R**elevant | Its parent key result — if it doesn't have one, it doesn't belong | An orphan monthly goal |
| **T**ime-bound | The due date, on the last working day of the month | No due date |

Worked example, from key result to monthly goal:

> **KR:** 80% of consultants certified on the reference architecture (baseline 15%, Q2)
> **Mar:** Run 2 certification sessions and get 8 consultants through the assessment

Specific (run sessions, put people through assessment), measurable (2 and 8), achievable (sized for the month), relevant (parent KR), time-bound (due March 31).

A monthly goal is **binary at month end** — met or not. Partial credit belongs on the key result's percentage, not here. This is what makes the monthly close fast and honest.

## Scoring

Score key results 0.0–1.0 at quarter end, reading directly off the tracked percentage:

| Score | Means |
|---|---|
| 1.0 | Target met or exceeded |
| 0.7 | Real progress; the expected landing spot for a stretch key result |
| 0.3 | Started, didn't move the number |
| 0.0 | No meaningful progress |

The objective's score is the average of its key results. Don't round it up.

An all-1.0 quarter means the targets were too easy, and is worth saying out loud. Consistent 0.3s mean they were fantasy, or the work never got prioritized — different problems with different fixes, and the review should establish which.

**Score the number, not the effort.** A key result missed for excellent reasons is still missed. The reasons belong in the review notes, where they inform next quarter; letting them adjust the score destroys the only thing scoring is for.

## Cadence

Each of these is a repeating task **in its own scope's project**, labeled `type/admin`, so the process is tracked rather than remembered. Each scope runs its own cycle — separate reviews, separate audiences.

**Weekly check-in** — 10 minutes per scope, or one pass over the cross-scope at-risk view:
1. Update the percentage on each active key result. If nothing moved, that's the signal — say so rather than skipping.
2. Look at this month's SMART goals against the days remaining.
3. Confirm at least one piece of execution work is in flight for each key result. A key result with no related work is a key result that won't move.

**Monthly close** — 20 minutes per scope:
1. Mark each monthly goal met or not met. Binary.
2. Roll progress up into the key result percentages.
3. Write next month's goals from where the key results actually stand — not from a plan made three months ago.

**Quarterly review** — an hour per scope:
1. Score every key result. Record the score in the task.
2. Note *why* for anything under 0.7, in the task itself, where next quarter's planning will find it.
3. Check each objective still matters. This is the moment to retire one — mid-quarter is not.
4. Set the next quarter's key results.

**Annual retro** — per scope:
1. Score objectives from their key results.
2. Archive that scope's year project. Never delete it — next year's targets come from this year's baselines.
3. Create next year's project for the scope, and carry forward what's still true. An objective repeating for a third year is either the real long-term direction or a goal nobody is actually pursuing; decide which.
4. Decide whether the scope itself still earns a separate set. A scope that scored nothing all year is a scope that should be folded into another.

### Running several scopes

Don't scale by repetition — four separate weekly reviews won't happen. Instead:

- **Weekly**, work the cross-scope at-risk view once, and only open the scopes it surfaces.
- **Monthly and quarterly**, go scope by scope. These are the reviews that need the full context and usually have a different audience each time, so they don't merge.
- **Stagger** quarterly reviews across different days if the scopes have different stakeholders. Four reviews in one afternoon get progressively less honest.

## Labels

The OKR tree uses its own axis, on top of the shared namespace from [[nerdynik-task-list-organization]]:

| Label | On |
|---|---|
| `okr/objective` | Objectives |
| `okr/kr` | Key results |
| `okr/monthly` | Monthly SMART goals |
| `okr/<year>-q<n>` | Key results, e.g. `okr/2026-q1` |
| `okr/<year>-<mm>` | Monthly goals, e.g. `okr/2026-03` |

Same rules as always: lowercase, kebab-case, no spaces.

Apply `practice/` and `dept/` labels to objectives and key results too, where they fit. That's what lets a practice leader see goals and delivery work on the same axis — the payoff for keeping one shared vocabulary across both skills.

### Labeling the scope

Scope lives on the project, so by the rule in [[nerdynik-task-list-organization]] — don't label what the project already says — it normally needs no label.

**One narrow exception.** Once someone runs more than two or three scopes, add `scope/<slug>` to **objectives only**:

```
scope/personal    scope/marketing    scope/data-platform    scope/company
```

The reason is queries that must survive change. "Every department objective" as a project list breaks the moment a department is added; as `labels in scope/marketing, scope/sales` it still breaks, but as a `scope/` filter it can be maintained in one place. Restricting the label to objectives keeps the cost at three to five tasks per set rather than the whole tree, and the roll-up views below only ever need it at that level.

Don't put `scope/` on key results or monthly goals. They inherit their scope from their parent, and labeling them buys nothing while tripling the maintenance.

### Saved views

Within one scope — build these per scope, named for the scope:

```
project = <scope project> && labels in okr/kr && done = false        live key results
project = <scope project> && labels in okr/2026-03 && done = false   this month's goals
project = <scope project> && labels in okr/objective                 the year at a glance
```

Across every scope you own — the reason multi-scope tracking is workable at all:

```
labels in okr/kr && done = false && percent_done < 50   key results at risk, everywhere
labels in okr/2026-03 && done = false                   every scope's goals this month
labels in okr/objective && done = false                 every objective you own
labels in scope/marketing, scope/sales                  one slice of scopes
```

That last one needs no `okr/objective` clause: objectives are the only tasks carrying a `scope/` label, so the filter is already narrowed. Stacking two `labels in` lists in one filter is best avoided anyway — the comma-separated list makes the parse ambiguous.

The cross-scope at-risk view is the one that earns its keep. With four scopes, no one opens four projects every week; they open one view that surfaces whatever is slipping and go from there.

## Anti-patterns

Name these when you see them; each has a specific fix.

| Pattern | Why it fails | Fix |
|---|---|---|
| Key results that are task lists | Measures activity, not outcome — you can complete them all and change nothing | Ask what the tasks are *for*, and measure that |
| Sandbagging | Targets set where they'll be hit; scoring becomes ceremony | Mark stretch vs committed up front |
| Too many objectives | Six objectives is no priority order; everything gets partial attention | Three to five per scope, and force the cut |
| Set and forgotten | No weekly touch, so quarter end is archaeology | The weekly check-in, as a repeating task |
| Scopes mixed in one project | Every view has to filter the others out, and the objective cap stops meaning anything | One project per scope per year |
| A scope per team that has two goals | Multiplies review load for goals nobody reviews | Fold it in as key results under an existing scope |
| More scopes than can be reviewed | They all go stale together, which is worse than not tracking them | Cap at what fits the calendar; say so when it doesn't |
| Goals nested with delivery work | The tree becomes unreadable within a quarter | Relate execution tasks, never nest them |
| Rewriting a key result mid-quarter | Guarantees a good score, teaches nothing | Let it score badly; note why; fix the target next quarter |
| Monthly goals with no parent | Nothing connects the month to the year | Every monthly goal has a parent key result, or it's just a task |

## Auditing an existing goal set

Report first, change nothing until the user decides. Audit one scope at a time and report per scope — findings averaged across scopes hide which set is actually in trouble.

1. **Key results with no baseline, target, or unit** — the most common and most damaging; they can't be scored.
2. **Key results measuring output** — quote the KR and propose the outcome version.
3. **Objectives with one key result** — usually a key result mislabeled as an objective.
4. **Objectives with six or more** — the objective is really two.
5. **Stale percentages** — nothing updated in weeks means the check-in isn't happening; that's the finding.
6. **Orphan monthly goals** — no parent key result.
7. **Key results with no related execution work** — nothing is actually being done.

Across scopes, also check:

8. **A scope that's entirely stale** while others are current — usually a scope that shouldn't exist, not a discipline problem.
9. **The same objective in two scopes** — decide which one owns it; duplicated goals get scored twice and pursued once.
10. **Mixed scopes in one project** — flag before anything else, since every other finding for that project is unreliable until it's split.

Give counts and one concrete example each, and lead with the ones that block scoring — a goal set that can't be scored fails at the only moment it matters.
