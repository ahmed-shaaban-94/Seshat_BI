# Agent Routing Smoke Test

## Purpose

This document is a lightweight **manual** smoke test for the Seshat BI agent
navigation layer. It checks that an agent entering through `COMPASS.md` and
`docs/knowledge-map.md` can route common Retail BI requests to the correct
readiness stage, skill, checklist, or blocked verdict.

What this is and is not:

- It is **not** a runtime test.
- It is **not** a database test.
- It is **not** a SQL/DAX correctness test.
- It **is** a routing and governance smoke test.
- It should be run **mentally** (or by an agent) before expanding the navigation
  docs — a cheap check that the compass, router, and knowledge layer still point
  agents to the right place and that the gates still block unsafe progression.

## Entry contract

The agent must start from:

```text
AGENTS.md
  -> COMPASS.md
    -> docs/readiness/readiness-model.md
    -> docs/knowledge-map.md
      -> relevant skill/router
        -> required artifact/checklist/verdict
```

The agent must **not** jump directly into a knowledge file unless the router
(`docs/knowledge-map.md`, or a skill's own `INDEX.md`) tells it to.

## Pass criteria

The smoke test passes only if every scenario:

- identifies the readiness stage being served;
- routes to the correct first document or skill;
- avoids reading the whole knowledge base (open only what the route names);
- ends on an artifact, checklist, verdict, or explicit blocker;
- does not bypass source mapping, validation, metric contracts, semantic
  readiness, or F016 gating;
- does not invent source meaning, metric meaning, approval, or readiness `pass`
  status.

## Scenario matrix

`Result` is the manual outcome cell. It is **`Not run`** by default — this PR
defines the test; it does not execute it (see "Expected result for this PR").

| ID | User request / symptom | Expected stage | Expected route | Expected end artifact/verdict | Must not do | Result |
|---|---|---|---|---|---|---|
| RT-001 | "Onboard a new retail sales source." | Source Ready | `AGENTS.md` → `COMPASS.md` → `docs/knowledge-map.md` → `docs/readiness/source-ready.md` (or `readiness-model.md` / `readiness-pipeline.md`) | source profile, or blocked verdict listing the missing source facts | Do not create silver/gold SQL directly. | Not run |
| RT-002 | "The source grain is unclear." | Mapping Ready | `COMPASS.md` → `docs/knowledge-map.md` → `docs/readiness/mapping-ready.md` | declared grain + uniqueness evidence, unresolved questions, or blocked verdict | Do not guess grain or approve mapping automatically. | Not run |
| RT-003 | "Gold totals do not reconcile to source." | Gold Ready / Validation | `COMPASS.md` → `docs/knowledge-map.md` → `skills/bi-sql-knowledge/SKILL.md` → `skills/bi-sql-knowledge/INDEX.md` → "Route by symptom" | PB-SQL verdict (PB-SQL-08) or SQL reconciliation checklist | Do not diagnose from `COMPASS.md` or read the whole SQL knowledge base. | Not run |
| RT-004 | "Review this silver/gold SQL transformation." | Silver Ready or Gold Ready | `COMPASS.md` → `docs/knowledge-map.md` → `skills/bi-sql-knowledge/SKILL.md` → `skills/bi-sql-knowledge/INDEX.md` | SQL review checklist, a VP-* validation gate shape, or a blocked metadata request | Do not execute the SQL or claim validation passed without evidence. | Not run |
| RT-005 | "Measure ignores slicers." | Semantic Model Ready / DAX review | `COMPASS.md` → `docs/knowledge-map.md` → `skills/bi-dax-knowledge/SKILL.md` → `skills/bi-dax-knowledge/INDEX.md` → "Route by symptom" | analyzer-style DAX verdict (via `checklists/dax-measure-review-checklist.md`) or blocked model-metadata request | Do not write arbitrary DAX before mapping model roles and filter behavior. | Not run |
| RT-006 | "Define Net Sales." | Semantic Model Ready / Metric contract | `COMPASS.md` → `docs/knowledge-map.md` → `skills/bi-dax-knowledge/SKILL.md` → `skills/bi-dax-knowledge/INDEX.md` → metric-contract route (`checklists/metric-contract-checklist.md`) | metric-contract checklist, or blocked business-definition question | Do not create a dashboard KPI or DAX measure before metric intent, grain, additivity, required fields, and filter behavior are known. | Not run |
| RT-007 | "Design the executive dashboard." | Dashboard Ready | `COMPASS.md` → `docs/knowledge-map.md` → `.claude/skills/powerbi-dashboard-design/` (router) → gated verb `.claude/skills/dashboard-design/` **only if** metric contracts + `semantic_model_ready: pass` exist | dashboard blueprint, or blocked verdict (no approved contracts / model not ready) | Do not design visuals before metric contracts and `semantic_model_ready` evidence. | Not run |
| RT-008 | "Publish this Power BI report." | Publish Ready / F016 boundary | `COMPASS.md` → `docs/knowledge-map.md` → `docs/roadmap/roadmap.md` (F016, gated / execution-only / later) | blocked verdict unless `semantic_model_ready` and the publish gates have passed | Do not run or advance the Power BI execution adapter (F016). | Not run |
| RT-009 | "SQL total doubled after a join." | SQL diagnostics / Silver–Gold validation | `COMPASS.md` → `docs/knowledge-map.md` → `skills/bi-sql-knowledge/INDEX.md` → "Route by symptom" | PB-SQL join fan-out diagnostic verdict (PB-SQL-01/02) | Do not apply a random `DISTINCT` or aggregate the issue away without grain evidence. | Not run |
| RT-010 | "YTD is wrong." | Semantic Model Ready / DAX time intelligence | `COMPASS.md` → `docs/knowledge-map.md` → `skills/bi-dax-knowledge/INDEX.md` → "Route by symptom" / time-intelligence route | date-table prerequisite checklist (`checklists/dax-model-review-checklist.md`), DAX shape, or blocked verdict | Do not fake a date table, "Mark as Date Table", a relationship, or calendar assumptions. | Not run |

## Manual run instructions

1. Pick one scenario from the matrix.
2. Start at `COMPASS.md`.
3. Identify the readiness stage being served.
4. Use `docs/knowledge-map.md` to select the route.
5. Open **only** the named skill/router (then its `INDEX.md` if it is a knowledge skill).
6. Stop on the expected artifact / checklist / verdict.
7. Mark `Result` as **PASS** or **BLOCKED**.
8. If blocked, record the missing route, the missing file, or the unsafe ambiguity.

## Failure examples

A scenario has **failed routing** (not merely blocked-by-design) if the agent:

- reads the whole SQL or DAX knowledge base instead of the one file the route names;
- writes silver SQL before Mapping Ready is `pass`;
- writes DAX before a metric contract / required model metadata exists;
- designs a dashboard before metric contracts and `semantic_model_ready`;
- routes a Power BI publish request to execution instead of the F016 blocked boundary;
- invents a readiness `pass` without citing evidence;
- treats C086 as the generic schema.

## Expected result for this PR

This PR **defines** the smoke test. It should leave every scenario `Result` cell as
**`Not run`** by default. A future PR may add an execution record once an agent has
actually walked the scenarios.

Do **not** fabricate a `PASS` run unless the manual checks were actually performed
and exact file evidence is cited.

## See also

- `COMPASS.md` — the compass (entry point + fast routing).
- `docs/knowledge-map.md` — the router (route by task and by symptom).
- `AGENTS.md` — the short operating contract.
- `docs/readiness/readiness-model.md` — the readiness spine and gate ordering.
