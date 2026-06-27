# Seshat BI Agent Operating Playbook

## 1. Purpose

This playbook defines **how an agent should operate Seshat BI consistently** after
the stabilization phase. It translates the stabilized docs / knowledge / routing
system into a single operating procedure: which layer to open first, how to route
by intent, what artifact to produce, when to stop, when to ask for a human ruling,
when to return BLOCKED, and what must never be executed or claimed.

It is **not** implementation, and it is **not** runtime behaviour. It executes no
data, connects to no database, runs no Power BI, grants no readiness, and replaces
no human approval. Its job is to prevent the recurring failure modes: routing
drift, premature execution, fake readiness/confidence, and layer-ownership
confusion.

Read it alongside the entry contract (`AGENTS.md` → `COMPASS.md` →
`docs/readiness/readiness-model.md` → `docs/knowledge-map.md`) and the routing
smoke test (`docs/quality/agent-routing-smoke-test.md`).

## 2. Operating Contract

The agent must obey, in order:

1. **Read before acting.** Enter through `COMPASS.md` / `docs/knowledge-map.md`;
   never start inside a knowledge file unless a router sent you there.
2. **Route before answering.** Classify intent and resolve the route first.
3. **Use the most specific knowledge layer** the route names — and open only what
   it names (two-hop: `SKILL.md` → `INDEX.md` → the one file).
4. **Produce an artifact / checklist / verdict**, not vague advice.
5. **Stop on missing evidence.** No evidence → no claim.
6. **Ask for a human ruling** when business meaning/policy is unresolved.
7. **Return BLOCKED** when a required input is absent.
8. **Never self-grant approval.** A readiness `pass` is a named human action.
9. **Never execute** Power BI / a database / runtime work from a reasoning layer.
10. **Never invent** source data, validation results, metric contracts, or
    readiness.

## 3. First-File Decision Tree

| User intent | First stop | Then read | Expected output | Stop if |
|-------------|------------|-----------|-----------------|---------|
| Define a KPI (business meaning) | `skills/retail-kpi-knowledge/SKILL.md` | its `INDEX.md` → the named `contracts/*.md` | metric contract + review-checklist verdict | policy (VAT/returns/cost) unresolved → NEEDS_HUMAN_RULING |
| Which KPI answers a business question? | `skills/retail-kpi-knowledge/INDEX.md` | the domain doc's "Decision questions" section | the routed contract or a planned/deferred note | no contract and none planned → PLANNED_DEFERRED |
| Can a source/table support KPIs? | `skills/retail-kpi-knowledge/references/kpi-coverage-scorecard-template.md` | `references/source-field-requirements.md` | per-table coverage scorecard (status + blockers) | a required field is absent → BLOCKED (missing field) |
| Write or review a DAX measure | `skills/bi-dax-knowledge/SKILL.md` | its `INDEX.md` | generated/reviewed measure + contract assumptions | no ready contract → route back to retail-kpi (BLOCKED) |
| Review SQL grain / join / reconciliation | `skills/bi-sql-knowledge/SKILL.md` | its `INDEX.md` (route by symptom) | SQL review / reconciliation checklist or PB-SQL verdict | grain undeclared → BLOCKED (unknown grain) |
| Review Python / source-prep / dataframe logic | `skills/bi-python-knowledge/SKILL.md` | its `INDEX.md` | cleaning / aggregation-grain review artifact | route is planned-only → PLANNED_DEFERRED |
| Assess readiness status | `docs/readiness/readiness-model.md` | the relevant `docs/readiness/<stage>-ready.md` | readiness status (status + evidence + blockers) | evidence missing → BLOCKED; never fabricate a `pass` |
| Dashboard / report design | `.claude/skills/powerbi-dashboard-design/` (router) | the gated design verb | dashboard blueprint | no metric contracts / `semantic_model_ready` → BLOCKED |
| Power BI execution / publish | `docs/roadmap/roadmap.md` (F016 boundary) | — | blocked verdict unless gates passed | semantic-model readiness / publish gates not passed → BLOCKED |
| Big Data / large source / scale | `docs/big-data/big-data-capability-report.md` | `docs/big-data/data-volume-assessment.md` + `templates/data-volume-profile.md` + `templates/large-source-profile.md` + `checklists/large-source-review-checklist.md` | scale assessment with a verdict | evidence (size/growth/latency) missing → BLOCKED |
| Real-data execution | — | `docs/roadmap/roadmap.md` (deferred/gated) | explanation that execution is deferred | always: real execution is out of scope → BLOCKED / deferred |
| Bypass validation / readiness | — | the relevant hard stop | refusal + the gate that applies | always: shortcut refused → BLOCKED |

**Required routing (canonical):**

- KPI meaning → `skills/retail-kpi-knowledge/`
- DAX implementation → `skills/bi-dax-knowledge/`
- SQL transformation / reconciliation → `skills/bi-sql-knowledge/`
- Python / source-prep → `skills/bi-python-knowledge/`
- Readiness → `docs/readiness/` + the readiness model
- Dashboard → dashboard/report guidance **only after** metric contracts
- Power BI execution → the gated adapter boundary, **not** immediate execution
- Big Data → `docs/big-data/` reports/templates, **not** tooling
- Real-data execution → **deferred**; requires an explicit, future, authorized
  execution path

## 4. Layer Ownership Rules

| Layer | Owns | Must not own | Handoff |
|-------|------|--------------|---------|
| Route registry / knowledge map | Resolving intent → the smallest route; route integrity (`docs/routing/routes.yaml`) | Executing anything; defining meaning | → the named knowledge/readiness layer |
| Retail KPI knowledge | **Business meaning** + metric contracts (VAT/returns/cost/grain rulings) | Writing SQL/DAX/Python; approving readiness; designing dashboards | → SQL/DAX/Python/Big-data with a ready contract |
| SQL knowledge | Transformation, **grain**, joins/fan-out, reconciliation reasoning | KPI meaning; running SQL | → DAX/semantic with a sound gold table |
| DAX knowledge | **Measure implementation** for a *ready* contract; filter context; model prerequisites | Redefining a KPI's meaning; running DAX | → semantic model / dashboard |
| Python knowledge | Single-node source-prep / cleaning / dataframe-grain reasoning | KPI meaning; distributed execution; declaring readiness | → SQL (or Big-data assessment if too large) |
| Readiness spine | **Status + evidence + blockers**; stage ordering | Self-granting a `pass`; fabricating a score | → the next stage once a human approves |
| Dashboard / report layer | Visual/page design **from approved contracts** | Designing before contracts; granting publish | → Power BI adapter (gated) |
| Power BI adapter boundary (F016) | Execution **only when gated** (semantic-model + publish gates passed) | Defining metrics/mappings/meaning; running before gates | — (terminal, execution-only) |
| Big Data / scale docs | **Assessing** scale (status/blocker verdicts) | Introducing runtime tooling/dependencies | → a future Python large-file slice or `analytics-scale-knowledge`, only if proven |

Explicit ownership: **Retail KPI owns meaning and contracts. SQL owns
transformation/grain/joins/reconciliation. DAX implements only after a ready
contract. Python owns source-prep, never KPI meaning. Readiness owns
status/evidence/blockers. Dashboard consumes contracts + semantic readiness.
Power BI executes only when gated. Big Data docs assess scale; they introduce no
runtime tooling.**

## 5. Standard Agent Workflow

1. **Classify** the user intent.
2. **Resolve the route** via `docs/routing/routes.yaml` / `docs/knowledge-map.md`.
3. **Open the most specific layer first.**
4. **Read** that layer's `SKILL.md` / `INDEX.md` (or the relevant docs).
5. **Check prerequisites** (contract exists? fields present? grain declared?
   gates passed?).
6. **Produce the required artifact / checklist / verdict.**
7. **Identify blockers** explicitly.
8. **Hand off** to the next layer **only if** prerequisites are satisfied.
9. **Refuse or BLOCK** unsafe/unsupported shortcuts.
10. **Record what was not verified.**

Use this output formula every time:

- **Status:**
- **Evidence:**
- **Blockers:**
- **Human rulings needed:**
- **Next valid handoff:**
- **Must not do:**

## 6. Common Scenarios

### Scenario 1 — Define Net Sales

- **User asks:** "Define Net Sales."
- **Correct route:** `skills/retail-kpi-knowledge/` → `INDEX.md` →
  `contracts/net-sales.md`.
- **Expected artifact:** the Net Sales metric contract + a
  metric-contract-review-checklist verdict.
- **PASS:** the contract's meaning/grain/additivity/required-fields are stated and
  consistent.
- **BLOCKED / NEEDS_HUMAN_RULING:** VAT / returns / cancellations policy unclear →
  surface options and ask the owner.
- **Must not do:** write DAX first; assume a VAT or returns policy.

### Scenario 2 — Which KPI answers margin leakage?

- **User asks:** "Which KPI tells me if margin is leaking?"
- **Correct route:** the KPI decision-question index → the margin/profitability
  domain.
- **Expected artifact:** the routed contract (`contracts/gross-margin.md` /
  `gross-margin-percent.md`) or a planned note.
- **PASS:** the question resolves to a real seeded contract.
- **BLOCKED:** the required **cost** field is missing → blocked-on-missing-field.
- **Must not do:** invent a margin formula; push meaning into DAX.

### Scenario 3 — Can this source support Gross Margin?

- **User asks:** "Can `raw.sales` support Gross Margin?"
- **Correct route:** the KPI coverage scorecard template +
  `source-field-requirements.md`.
- **Expected artifact:** a per-table coverage scorecard (status + named blockers).
- **PASS:** required fields present **and** contract Seeded → Covered.
- **BLOCKED:** no cost field → **Blocked — missing field**.
- **Must not do:** emit a numeric coverage score/percentage; infer "covered" from a
  field merely existing.

### Scenario 4 — Write DAX for Net Sales Growth

- **User asks:** "Write the DAX for Net Sales Growth."
- **Correct route:** `skills/bi-dax-knowledge/` — **only** if a ready contract
  exists.
- **Expected artifact:** the measure + contract assumptions, **or** a blocked
  verdict routing back to retail-kpi.
- **PASS:** a ready Net Sales (and growth-baseline) contract exists.
- **BLOCKED:** the comparison baseline is unresolved → route back to KPI meaning /
  owner ruling.
- **Must not do:** invent the formula or the baseline.

### Scenario 5 — SQL total does not reconcile

- **User asks:** "Gold total doesn't match source."
- **Correct route:** `skills/bi-sql-knowledge/` → symptom route.
- **Expected artifact:** a reconciliation checklist / PB-SQL fan-out verdict.
- **PASS:** the grain/join/fan-out cause is identified with evidence.
- **BLOCKED:** grain undeclared or evidence missing.
- **Must not do:** "fix" it in DAX first; apply a blind `DISTINCT`.

### Scenario 6 — Python cleaning pipeline changes categories

- **User asks:** "Review this category-cleaning step."
- **Correct route:** `skills/bi-python-knowledge/` → cleaning / aggregation-grain
  route.
- **Expected artifact:** a cleaning/standardization + dtype/category review.
- **PASS:** the standardization and dtype rules are sound.
- **BLOCKED:** the route is planned-only → PLANNED_DEFERRED.
- **Must not do:** declare readiness; redefine a KPI's meaning.

### Scenario 7 — Build executive dashboard

- **User asks:** "Build an executive dashboard."
- **Correct route:** dashboard design — **not** the first stop.
- **Expected artifact:** a dashboard blueprint **after** contracts + semantic
  readiness.
- **PASS:** metric contracts + `semantic_model_ready: pass` exist.
- **BLOCKED:** no approved contracts or model not ready.
- **Must not do:** design visuals before metric contracts.

### Scenario 8 — Publish to Power BI

- **User asks:** "Publish this to Power BI."
- **Correct route:** the F016 gated adapter boundary (`roadmap.md`).
- **Expected artifact:** a blocked verdict unless the gates have passed.
- **PASS:** semantic-model readiness + publish gates passed (a human-gated state).
- **BLOCKED:** validation/readiness missing → no publish.
- **Must not do:** run or advance the execution adapter.

### Scenario 9 — Big Data / multi-GB source

- **User asks:** "This source is multiple GB — what do we do?"
- **Correct route:** `docs/big-data/big-data-capability-report.md` +
  `docs/big-data/data-volume-assessment.md` + `templates/data-volume-profile.md`,
  `templates/large-source-profile.md`, `checklists/large-source-review-checklist.md`.
- **Expected artifact:** a scale assessment with a verdict
  (`LOCAL_OK` / `WAREHOUSE_RECOMMENDED` / `SCALE_REVIEW_REQUIRED` / `BLOCKED`).
- **PASS:** measured figures support a verdict.
- **BLOCKED:** size/growth/latency evidence missing.
- **Must not do:** add Spark/Fabric/Databricks/Snowflake/BigQuery; add a runtime
  dependency; create `analytics-scale-knowledge`.

### Scenario 10 — User asks to skip validation

- **User asks:** "Skip validation, just build the dashboard."
- **Correct route:** refuse; cite the gate.
- **Expected artifact:** a BLOCKED verdict with the reason.
- **PASS:** n/a — the shortcut is never valid.
- **BLOCKED:** always — validation precedes dashboard/publish.
- **Must not do:** comply; fabricate a validation result.

## 7. BLOCKED Conditions

| Condition | Why BLOCKED | Required next action |
|-----------|-------------|----------------------|
| No metric contract | Meaning is undefined; downstream layers have nothing to consume | Route to retail-kpi to define the contract |
| Missing required field(s) | The KPI cannot be computed from this source | Name the absent field; gather it / confirm with source owner |
| Unresolved VAT / returns / cost policy | Business meaning is ambiguous | NEEDS_HUMAN_RULING from the owner |
| Unknown grain | Aggregation correctness cannot be guaranteed | Declare + verify grain (SQL/source mapping) |
| Fan-out risk unresolved | Totals may be inflated by a join | Diagnose cardinality before any total |
| No source profile / source map | Mapping Ready not satisfied | Profile + map the source; review unresolved questions |
| No reconciliation evidence | Gold cannot be trusted vs source | Mark NOT_VERIFIED; reconciliation is a **deferred** live step — flag it for a future, gated execution path (do not run it from here) |
| No semantic-model readiness | Model not proven for measures | Achieve Semantic Model Ready first |
| No dashboard metric contract | Visuals would have no agreed meaning | Define contracts before design |
| Power BI execution before gates | Hard rule #6 (execution gated/last) | Pass semantic-model + publish gates (human) |
| Big Data tooling without evidence | Premature platform adoption | Fill the data-volume assessment (a doc, not a run); reach a verdict + human ruling |
| Human approval required but not provided | A `pass`/publish needs a named human | Surface the decision; wait for the human |

## 8. Human Ruling Points

The agent **surfaces options and blockers** but **cannot choose policy silently**.
A human ruling is required for:

- Metric business definition
- VAT / tax treatment
- Returns / cancellations treatment
- Cost methodology (FIFO / average / standard)
- Target / budget handling
- Same-store definition
- Grain declaration
- PII / business sensitivity
- Publish approval
- Thresholds for exceptions
- Scale-escalation decision (single-node → push-down → distributed)

## 9. Output Verdict Vocabulary

| Verdict | When to use | Evidence required | Must not claim |
|---------|-------------|-------------------|----------------|
| **PASS** | The asked-for artifact is satisfied by current docs/rules/contracts | Cited files/contracts; prerequisites met | runtime execution, live validation, or readiness `pass` (unless a human granted it) |
| **PASS_WITH_NOTES** | Satisfied, but with caveats/follow-ups worth recording | Same as PASS + the named caveats | that the caveats are resolved |
| **BLOCKED** | A required input is absent or a gate is not passed | The specific missing input / unpassed gate | that the work can proceed anyway |
| **PLANNED_DEFERRED** | The route/KPI is recognized but not yet built/contracted | The planned marker in the route/domain | that a contract/route exists |
| **NEEDS_HUMAN_RULING** | Business meaning/policy is unresolved | The specific undecided policy + options | a chosen policy |
| **NOT_VERIFIED** | A claim could not be confirmed from the repo / needs real data | What was checked and why it is unconfirmed | the claim as proven |

## 10. Anti-Patterns

The agent must avoid:

- Starting with DAX before a metric contract.
- Starting with a dashboard before metrics.
- Treating KPI coverage as readiness.
- Using numeric confidence / coverage scores.
- Inventing source data.
- Claiming validation without evidence.
- Treating Big Data as a tool-install decision.
- Adding runtime dependencies from docs.
- Letting SQL/DAX/Python redefine KPI meaning.
- Granting human approval automatically.
- Publishing before semantic-model readiness.
- Running commands from route/knowledge docs.
- Treating the Idea Bank (`docs/roadmap/idea-backlog.md`) as a roadmap commitment.

## 11. Handoff Map

| From | To | Allowed when | Handoff artifact |
|------|----|--------------|------------------|
| Source (profiled) | Mapping | Source Ready: a source profile exists | source profile |
| Mapping | Silver | **Mapping Ready: pass** — source map + declared grain + reviewed unresolved questions (a human gate; no source goes straight to silver) | reviewed source map + grain |
| Silver | Gold | Silver Ready: typed/cleaned silver built + statically clean | built silver table |
| Retail KPI | SQL | Contract Seeded; fields/grain/exclusions stated | required fields + grain + filter rules |
| Retail KPI | DAX | Contract ready (meaning + additivity + filters) | business formula + additivity call (no DAX from KPI) |
| Retail KPI | Python | Contract states required fields + dtype/quality assumptions | required-field + dtype notes for single-node prep |
| Python | SQL | Source-prep reasoned; transform belongs in-warehouse | cleaned-field expectations + grain |
| SQL | DAX / Semantic | Gold table sound (grain, no fan-out, reconciled) | gold table contract + reconciliation evidence |
| Semantic | Dashboard | `semantic_model_ready: pass` + approved contracts | model + measures + contract bindings |
| Dashboard | Publish | Dashboard Ready + publish gates (human-approved) | BI handoff pack |
| Big Data assessment | Python large-file (future slice) | Single-node-with-care is the verdict | the data-volume profile + `LOCAL_OK` reasoning |
| Big Data assessment | `analytics-scale-knowledge` (future layer) | Distributed need **proven** + human ruling | `SCALE_REVIEW_REQUIRED` verdict + evidence |

## 12. Minimal Response Template for Agents

Keep responses concise but evidence-backed:

```text
Route:
Files/docs used:
Status:
Evidence:
Blockers:
Human rulings needed:
Next valid step:
Must not do:
```

Every field should be answerable from the route and the files opened; if a field
would require guessing, that is itself a Blocker or a NOT_VERIFIED note.

## 13. Final Operating Rule

**When unsure, stop at the nearest governance gate and return:**

- what is **known**,
- what is **not verified**,
- what **human ruling** is needed,
- what **artifact** should be produced next.

Do not guess, execute, publish, or approve.

## See also

- `COMPASS.md` — the compass (entry + fast routing).
- `docs/knowledge-map.md` — the router (by task and by symptom).
- `docs/routing/routes.yaml` — the machine-checkable route registry.
- `docs/readiness/readiness-model.md` — the readiness spine and gate ordering.
- `docs/quality/agent-routing-smoke-test.md` — the routing smoke test.
- `docs/quality/post-idea-bank-capability-state.md` — what the system can do now.
- `docs/demo/net-sales-end-to-end-readiness-trace.md` — one KPI path, end to end.
- `docs/big-data/big-data-capability-report.md` + `data-volume-assessment.md` — scale boundaries.
