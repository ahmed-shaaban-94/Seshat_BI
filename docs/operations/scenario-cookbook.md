# Seshat BI Scenario Cookbook

## 1. Purpose

This cookbook gives **practical routing scenarios** for Seshat BI agents — concrete
user requests mapped to the correct route, first file to open, expected artifact,
and PASS / BLOCKED behaviour. It complements the
`docs/operations/agent-operating-playbook.md` (which defines the general operating
rules); this file makes them concrete per request type.

It is **not** implementation. It executes no data, connects to no database, runs no
Power BI, and grants no readiness. It gives examples of correct routing, expected
artifacts, PASS/BLOCKED behaviour, and stop rules — nothing here may be used to
bypass a governance gate.

## 2. How To Use This Cookbook

1. Start from the scenario **closest** to the user request.
2. Use its **route** and **first-stop** layer.
3. Read the **required docs / knowledge** files it names.
4. Produce the **expected artifact / checklist / verdict**.
5. **Stop** if prerequisites are missing.
6. **Never** use these scenarios to bypass governance (validation, contracts,
   readiness, gates).
7. If evidence is missing, return **NOT_VERIFIED** or **BLOCKED** — do not guess.

Verdict vocabulary is shared with the playbook: `PASS` / `PASS_WITH_NOTES` /
`BLOCKED` / `PLANNED_DEFERRED` / `NEEDS_HUMAN_RULING` / `NOT_VERIFIED`.

## 3. Scenario Index

| ID | User request pattern | Primary route | Expected output |
|----|----------------------|---------------|-----------------|
| SCN-001 | Define a KPI (Net Sales) | `skills/retail-kpi-knowledge/` | metric contract + review verdict |
| SCN-002 | Which KPI answers margin leakage? | `skills/retail-kpi-knowledge/` (question index) | routed contract or planned note |
| SCN-003 | Can this source support Gross Margin? | KPI coverage scorecard | coverage status + blockers |
| SCN-004 | Write DAX for Net Sales | `skills/bi-dax-knowledge/` (after contract) | measure or route-back verdict |
| SCN-005 | Write DAX for Net Sales Growth % | `skills/bi-dax-knowledge/` (after contract) | measure or NEEDS_HUMAN_RULING |
| SCN-006 | Gold total does not reconcile | `skills/bi-sql-knowledge/` | reconciliation checklist/verdict |
| SCN-007 | Join doubled my sales rows | `skills/bi-sql-knowledge/` | join/fan-out review |
| SCN-008 | Python cleaning changed categories | `skills/bi-python-knowledge/` | cleaning review + ruling ask |
| SCN-009 | Python aggregates before grain declared | `skills/bi-python-knowledge/` | aggregation-grain review / BLOCKED |
| SCN-010 | Is this source ready for silver? | `docs/readiness/` | readiness status (status+evidence+blockers) |
| SCN-011 | Build executive dashboard | dashboard (after contracts) | blueprint or BLOCKED |
| SCN-012 | Publish to Power BI | F016 gated boundary | blocked verdict unless gated |
| SCN-013 | 20GB source — use Spark? | `docs/big-data/` | scale assessment verdict |
| SCN-014 | Profile this source for scale | data-volume / large-source templates | verdict or NOT_VERIFIED |
| SCN-015 | Skip validation, just build | refuse | BLOCKED |
| SCN-016 | New KPI not in catalog | `skills/retail-kpi-knowledge/` | contract-proposal path + ruling ask |
| SCN-017 | Source lacks required KPI fields (ATV) | KPI coverage scorecard | blocked-on-missing-field |
| SCN-018 | Run this on my database now | deferred / gated | deferred explanation + BLOCKED |
| SCN-019 | Define Net Sales AND give DAX | two phases (KPI → DAX) | contract first, then measure |
| SCN-020 | Dashboard visual uses unapproved measure | dashboard governance + KPI store | orphan-measure flag / BLOCKED |

## 4. Scenario Cards

### SCN-001 — Define Net Sales

**User may ask:** "Define Net Sales for retail reporting."
**Correct route:** `skills/retail-kpi-knowledge/`.
**Read first:** `SKILL.md` → `INDEX.md` → `contracts/net-sales.md`.
**Expected artifact:** the Net Sales metric contract + a
metric-contract-review-checklist verdict.
**PASS behavior:** meaning, grain, additivity, and required fields stated and
consistent; VAT assumed pre-tax and disclosed.
**BLOCKED behavior:** VAT / returns / cancellations policy unresolved →
NEEDS_HUMAN_RULING (surface options to the owner).
**Must not do:** write DAX first; invent a VAT/returns policy.
**Minimal response shape:**
Route: retail-kpi-knowledge
Files/docs used: SKILL.md, INDEX.md, contracts/net-sales.md
Status: PASS or NEEDS_HUMAN_RULING
Evidence: the contract sections
Blockers: any unresolved policy
Human rulings needed: VAT/returns if unclear
Next valid step: handoff to SQL/DAX with a ready contract
Must not do: author DAX; assume policy

### SCN-002 — Which KPI answers margin leakage?

**User may ask:** "Which KPI tells me if promotions are hurting margin?"
**Correct route:** `skills/retail-kpi-knowledge/` (decision-question index).
**Read first:** `INDEX.md` → the margin/profitability and discounts/promotions
domain "Decision questions" sections.
**Expected artifact:** the routed contract(s) (`contracts/gross-margin.md` /
`gross-margin-percent.md`, `discount-amount.md` / `discount-rate.md`) or a planned
note.
**PASS behavior:** the question resolves to real seeded contracts across the two
domains.
**BLOCKED behavior:** the required **cost** field is missing → BLOCKED
(blocked-on-missing-field); or the relevant KPI is planned → PLANNED_DEFERRED.
**Must not do:** invent a new KPI contract; push meaning into DAX.
**Minimal response shape:**
Route: retail-kpi-knowledge (question index)
Files/docs used: INDEX.md, margin + discounts domain docs
Status: PASS / BLOCKED / PLANNED_DEFERRED
Evidence: the routed contract paths
Blockers: missing cost field, if any
Human rulings needed: cost method if undecided
Next valid step: coverage check on a real source
Must not do: fabricate a contract

### SCN-003 — Can this source support Gross Margin?

**User may ask:** "This source has sales and quantity but no cost. Can it support
Gross Margin?"
**Correct route:** the KPI coverage scorecard.
**Read first:** `skills/retail-kpi-knowledge/references/kpi-coverage-scorecard-template.md`
+ `references/source-field-requirements.md`.
**Expected artifact:** a per-table coverage scorecard (status + named blockers).
**PASS behavior:** for KPIs whose fields are present, Covered; the answer is per-KPI.
**BLOCKED behavior:** Gross Margin requires **cost** → **Blocked — missing field**.
**Must not do:** emit a numeric coverage percentage; grant readiness; infer
"covered" from a field merely existing.
**Minimal response shape:**
Route: retail-kpi coverage scorecard
Files/docs used: kpi-coverage-scorecard-template.md, source-field-requirements.md
Status: BLOCKED (Gross Margin) / Covered (others with fields)
Evidence: present vs absent required fields
Blockers: cost amount (COGS) absent
Human rulings needed: cost method
Next valid step: gather cost field / confirm with owner
Must not do: numeric score; readiness

### SCN-004 — Write DAX for Net Sales

**User may ask:** "Write the Net Sales DAX measure."
**Correct route:** `skills/bi-dax-knowledge/` — only after a ready contract.
**Read first:** confirm `contracts/net-sales.md` is ready; then
`skills/bi-dax-knowledge/SKILL.md` → `INDEX.md`.
**Expected artifact:** the measure + contract assumptions, or a route-back verdict.
**PASS behavior:** a ready Net Sales contract exists → generate/review the measure.
**BLOCKED behavior:** business definition unresolved → route back to retail-kpi.
**Must not do:** define Net Sales inside the DAX layer.
**Minimal response shape:**
Route: bi-dax-knowledge (gated on contract)
Files/docs used: contracts/net-sales.md, bi-dax SKILL/INDEX
Status: PASS / BLOCKED (route back)
Evidence: contract readiness
Blockers: unresolved meaning, if any
Human rulings needed: deferred to KPI layer
Next valid step: semantic-model readiness
Must not do: redefine meaning in DAX

### SCN-005 — Write DAX for Net Sales Growth

**User may ask:** "Write DAX for Net Sales Growth %."
**Correct route:** `skills/bi-dax-knowledge/` — after the contract.
**Read first:** the Net Sales contract + the time-intelligence domain
(growth-baseline policy).
**Expected artifact:** the measure, or a NEEDS_HUMAN_RULING verdict.
**PASS behavior:** baseline resolved (YoY / previous period / fiscal calendar /
same-store if relevant) → generate the measure.
**BLOCKED behavior:** baseline unresolved → NEEDS_HUMAN_RULING.
**Must not do:** invent the comparison baseline or fiscal calendar.
**Minimal response shape:**
Route: bi-dax-knowledge (gated)
Files/docs used: net-sales contract, time-intelligence domain
Status: PASS / NEEDS_HUMAN_RULING
Evidence: baseline definition state
Blockers: undefined baseline
Human rulings needed: YoY vs prev-period; fiscal calendar; same-store
Next valid step: measure generation once ruled
Must not do: invent baseline

### SCN-006 — SQL totals do not reconcile

**User may ask:** "My gold sales total does not match source."
**Correct route:** `skills/bi-sql-knowledge/`.
**Read first:** `SKILL.md` → `INDEX.md` (route by symptom).
**Expected artifact:** a reconciliation checklist / PB-SQL verdict.
**PASS behavior:** the grain/join/fan-out/dedup/filter cause is identified with
evidence.
**BLOCKED behavior:** grain undeclared or reconciliation evidence absent →
BLOCKED / NOT_VERIFIED (a live reconciliation needs real data).
**Must not do:** fix it in DAX first; claim validation passed without evidence.
**Minimal response shape:**
Route: bi-sql-knowledge (symptom)
Files/docs used: SKILL.md, INDEX.md
Status: PASS / BLOCKED / NOT_VERIFIED
Evidence: grain + cardinality findings
Blockers: undeclared grain; no live data
Human rulings needed: none (technical)
Next valid step: fix at the right grain in SQL/gold
Must not do: DAX patch; fake validation

### SCN-007 — Join doubled my sales rows

**User may ask:** "After joining the product dimension, sales doubled."
**Correct route:** `skills/bi-sql-knowledge/`.
**Read first:** `INDEX.md` → join/fan-out symptom route.
**Expected artifact:** a join / fan-out review (cardinality, m:m, duplicate keys).
**PASS behavior:** the fan-out cause (duplicate dim keys / m:m) is named with the
cardinality evidence.
**BLOCKED behavior:** grain/cardinality unresolved → BLOCKED until established.
**Must not do:** apply a blind `DISTINCT`; aggregate the problem away.
**Minimal response shape:**
Route: bi-sql-knowledge (fan-out)
Files/docs used: INDEX.md symptom route
Status: PASS / BLOCKED
Evidence: join cardinality, duplicate keys
Blockers: unresolved grain/cardinality
Human rulings needed: none
Next valid step: correct the join key/grain
Must not do: blind DISTINCT

### SCN-008 — Python cleaning changed product categories

**User may ask:** "My Python cleaning standardized product categories. Is that
okay?"
**Correct route:** `skills/bi-python-knowledge/`.
**Read first:** `SKILL.md` → `INDEX.md` (cleaning/standardization route).
**Expected artifact:** a cleaning/standardization review (mapping + dtype/category
rules).
**PASS behavior:** the standardization follows an analyst-supplied mapping and is
sound.
**BLOCKED behavior:** the change alters business meaning → NEEDS_HUMAN_RULING.
**Must not do:** declare source/silver readiness; invent a category mapping.
**Minimal response shape:**
Route: bi-python-knowledge (cleaning)
Files/docs used: SKILL.md, INDEX.md
Status: PASS / NEEDS_HUMAN_RULING
Evidence: the mapping + dtype rules applied
Blockers: meaning-changing remap without a ruling
Human rulings needed: category mapping ownership
Next valid step: handoff to SQL/readiness
Must not do: declare readiness

### SCN-009 — Python pipeline aggregates before grain is declared

**User may ask:** "My pandas pipeline groups sales by branch before mapping is
reviewed."
**Correct route:** `skills/bi-python-knowledge/` (aggregation-grain review).
**Read first:** `SKILL.md` → `INDEX.md` (aggregation-grain route).
**Expected artifact:** an aggregation-grain review.
**PASS behavior:** grain is declared/reviewed and the groupby matches it.
**BLOCKED behavior:** source profile / source map / declared grain absent →
BLOCKED (Mapping Ready not satisfied).
**Must not do:** approve silver/gold readiness; assume the grain.
**Minimal response shape:**
Route: bi-python-knowledge (agg-grain)
Files/docs used: SKILL.md, INDEX.md
Status: BLOCKED until grain declared
Evidence: presence/absence of profile+map+grain
Blockers: no source map / grain
Human rulings needed: grain declaration
Next valid step: profile+map, then re-review
Must not do: approve readiness

### SCN-010 — Assess readiness for a table

**User may ask:** "Is this source ready for silver?"
**Correct route:** `docs/readiness/`.
**Read first:** `docs/readiness/readiness-model.md` → `mapping-ready.md`.
**Expected artifact:** a readiness status — **status + evidence + blockers**.
**PASS behavior:** source profile + source map + declared grain + reviewed
unresolved questions all present → Mapping Ready can be `pass` (a human grants it).
**BLOCKED behavior:** any of those absent → BLOCKED with the missing item named.
**Must not do:** use a fake score; self-grant the `pass`.
**Minimal response shape:**
Route: readiness spine
Files/docs used: readiness-model.md, mapping-ready.md
Status: status + evidence + blockers (never a score)
Evidence: the committed artifacts present
Blockers: any missing gate input
Human rulings needed: the stage approval (named human)
Next valid step: human approval → silver
Must not do: fake score; self-grant pass

### SCN-011 — Build executive dashboard

**User may ask:** "Build an executive dashboard for branch performance."
**Correct route:** dashboard design — **not** the first stop.
**Read first:** `.claude/skills/powerbi-dashboard-design/` (router) — only after
contracts + `semantic_model_ready`.
**Expected artifact:** a dashboard blueprint, or a BLOCKED verdict.
**PASS behavior:** metric contracts + `semantic_model_ready: pass` + validation
evidence exist → blueprint from approved contracts.
**BLOCKED behavior:** metric contracts missing (or model not ready) → BLOCKED.
**Must not do:** design the final dashboard before contracts.
**Minimal response shape:**
Route: dashboard design (gated)
Files/docs used: powerbi-dashboard-design router, contracts, readiness
Status: PASS / BLOCKED
Evidence: contracts + semantic readiness
Blockers: missing contracts / model not ready
Human rulings needed: KPI pack selection
Next valid step: design once gated
Must not do: visuals before metrics

### SCN-012 — Publish to Power BI

**User may ask:** "Publish this to Power BI."
**Correct route:** the F016 gated adapter boundary (`docs/roadmap/roadmap.md`).
**Read first:** the roadmap F016 boundary + the publish gates.
**Expected artifact:** a blocked verdict unless the gates have passed.
**PASS behavior:** semantic-model readiness + validation + publish approval all
present (a human-gated state).
**BLOCKED behavior:** any gate missing → BLOCKED; no immediate execution.
**Must not do:** run or advance the execution adapter.
**Minimal response shape:**
Route: F016 boundary (gated)
Files/docs used: roadmap.md (F016), publish-ready.md
Status: BLOCKED unless all gates pass
Evidence: gate states
Blockers: missing readiness/validation/approval
Human rulings needed: publish approval
Next valid step: satisfy gates (human)
Must not do: execute/publish

### SCN-013 — Assess Big Data risk

**User may ask:** "This source is 20GB. Should we use Spark?"
**Correct route:** `docs/big-data/`.
**Read first:** `docs/big-data/big-data-capability-report.md` +
`docs/big-data/data-volume-assessment.md`.
**Expected artifact:** a scale assessment with a verdict.
**PASS behavior:** the assessment yields a verdict treating Big Data as a
scale/latency *condition* (single-node → push-down → distributed only if proven).
**BLOCKED behavior:** size/growth/latency evidence missing → BLOCKED.
**Must not do:** recommend Spark/Fabric/Databricks/Snowflake/BigQuery without
evidence; add a runtime dependency.
**Minimal response shape:**
Route: docs/big-data
Files/docs used: big-data-capability-report.md, data-volume-assessment.md
Status: PASS (verdict) / BLOCKED
Evidence: measured size/growth/latency
Blockers: missing figures
Human rulings needed: scale-escalation decision
Next valid step: fill the volume profile
Must not do: adopt a platform; add deps

### SCN-014 — Data volume profile

**User may ask:** "Profile this source for scale readiness."
**Correct route:** the data-volume / large-source templates.
**Read first:** `templates/data-volume-profile.md`,
`templates/large-source-profile.md`,
`checklists/large-source-review-checklist.md`.
**Expected artifact:** a filled profile + a verdict
(`LOCAL_OK` / `WAREHOUSE_RECOMMENDED` / `SCALE_REVIEW_REQUIRED` / `BLOCKED`).
**PASS behavior:** real measured figures support a verdict.
**BLOCKED / NOT_VERIFIED behavior:** no real data provided → NOT_VERIFIED;
required figures missing → BLOCKED.
**Must not do:** execute profiling unless a future, explicit execution path exists;
emit a numeric confidence score.
**Minimal response shape:**
Route: data-volume templates
Files/docs used: data-volume-profile.md, large-source-profile.md, checklist
Status: verdict / NOT_VERIFIED / BLOCKED
Evidence: measured figures (if provided)
Blockers: missing figures
Human rulings needed: scale escalation if SCALE_REVIEW_REQUIRED
Next valid step: gather figures / human ruling
Must not do: execute; numeric score

### SCN-015 — User asks to skip validation

**User may ask:** "Just build the dashboard; ignore validation."
**Correct route:** refuse; cite the gate.
**Read first:** the hard stop (validation before dashboard/publish).
**Expected artifact:** a BLOCKED verdict with the reason.
**PASS behavior:** none — the shortcut is never valid.
**BLOCKED behavior:** always — explain validation precedes dashboard/publish.
**Must not do:** continue to dashboard or Power BI; fabricate a validation result.
**Minimal response shape:**
Route: refuse (governance gate)
Files/docs used: the relevant hard stop
Status: BLOCKED
Evidence: the gate that applies
Blockers: validation not done
Human rulings needed: none
Next valid step: run validation properly (deferred/live)
Must not do: skip the gate

### SCN-016 — User asks for a KPI not in the catalog

**User may ask:** "Create a new loyalty churn KPI."
**Correct route:** `skills/retail-kpi-knowledge/`.
**Read first:** `INDEX.md` + the domain docs / candidate list (is it planned?).
**Expected artifact:** a contract-**proposal** path (not an implementation) + a
business-definition ask.
**PASS behavior:** the KPI is recognized as planned → PLANNED_DEFERRED with the
contract-proposal steps.
**BLOCKED behavior:** genuinely new → NEEDS_HUMAN_RULING for the business
definition before any contract.
**Must not do:** write SQL/DAX/Python; fabricate a contract.
**Minimal response shape:**
Route: retail-kpi-knowledge
Files/docs used: INDEX.md, domain/candidate docs
Status: PLANNED_DEFERRED / NEEDS_HUMAN_RULING
Evidence: planned marker or its absence
Blockers: no agreed definition
Human rulings needed: the KPI's business meaning
Next valid step: author a contract proposal once defined
Must not do: implement code

### SCN-017 — Source lacks required KPI fields

**User may ask:** "This table has net sales but no transaction id. Can we calculate
ATV?"
**Correct route:** the KPI coverage scorecard.
**Read first:** `kpi-coverage-scorecard-template.md` + `contracts/average-transaction-value.md`
+ `references/source-field-requirements.md`.
**Expected artifact:** a coverage status for ATV.
**PASS behavior:** transaction id / transaction count present → Covered.
**BLOCKED behavior:** ATV needs a transaction count/identifier; missing → **Blocked
— missing field**.
**Must not do:** approximate ATV without an owner ruling.
**Minimal response shape:**
Route: coverage scorecard
Files/docs used: scorecard template, ATV contract, field requirements
Status: BLOCKED (missing field)
Evidence: transaction id/count absent
Blockers: no transaction identifier
Human rulings needed: any approximation policy
Next valid step: gather transaction id / confirm owner
Must not do: approximate silently

### SCN-018 — User asks for real data execution

**User may ask:** "Run this on my database now."
**Correct route:** deferred / gated — explain, do not execute.
**Read first:** the roadmap (execution deferred/gated) + the relevant readiness
gates.
**Expected artifact:** an explanation of what artifacts/gates are needed first.
**PASS behavior:** none here — real execution is out of scope for a reasoning
layer.
**BLOCKED behavior:** always — execution is deferred unless an explicit execution
adapter/path exists and its gates are satisfied.
**Must not do:** connect to a DB; run runtime commands.
**Minimal response shape:**
Route: deferred / gated
Files/docs used: roadmap.md, readiness gates
Status: BLOCKED (deferred)
Evidence: no execution path / gates unmet
Blockers: execution is deferred
Human rulings needed: authorize a future execution path
Next valid step: produce the prerequisite artifacts
Must not do: connect/execute

### SCN-019 — Route conflict between KPI and DAX

**User may ask:** "Define Net Sales and give me DAX."
**Correct route:** split into two phases.
**Read first:** phase 1 — `skills/retail-kpi-knowledge/contracts/net-sales.md`;
phase 2 — `skills/bi-dax-knowledge/` only if the contract is ready.
**Expected artifact:** the contract first, then the measure (separately).
**PASS behavior:** contract produced/confirmed, then DAX generated from it.
**BLOCKED behavior:** if meaning is unresolved, stop at phase 1
(NEEDS_HUMAN_RULING); do not proceed to DAX.
**Must not do:** blend business definition into the DAX layer.
**Minimal response shape:**
Route: retail-kpi (phase 1) → bi-dax (phase 2)
Files/docs used: net-sales contract, bi-dax SKILL/INDEX
Status: phased PASS / BLOCKED at phase 1
Evidence: contract readiness
Blockers: unresolved meaning
Human rulings needed: VAT/returns if unclear
Next valid step: DAX only after contract ready
Must not do: define meaning in DAX

### SCN-020 — Dashboard visual uses unapproved measure

**User may ask:** "This dashboard visual uses a measure not in any contract."
**Correct route:** dashboard/visual governance + the KPI contract store.
**Read first:** the dashboard design router + `skills/retail-kpi-knowledge/contracts/`.
**Expected artifact:** an orphan/rogue-measure flag.
**PASS behavior:** every visual measure ties to an approved metric contract.
**BLOCKED behavior:** the measure has no approved contract → BLOCKED until it is
tied to one (or the contract is authored + approved).
**Must not do:** approve the dashboard; back-fill a contract to legitimize the
measure without a ruling.
**Minimal response shape:**
Route: dashboard governance + KPI store
Files/docs used: dashboard router, contracts/
Status: BLOCKED (orphan measure)
Evidence: measure has no contract
Blockers: unapproved measure
Human rulings needed: define+approve the contract, or remove the visual
Next valid step: tie measure to a contract
Must not do: approve the dashboard

## 5. Scenario Summary Matrix

| Scenario | First stop | Required evidence | Valid verdicts | Common wrong move |
|----------|------------|-------------------|----------------|-------------------|
| SCN-001 Define Net Sales | retail-kpi-knowledge | contract sections; resolved policy | PASS / NEEDS_HUMAN_RULING | writing DAX first |
| SCN-002 Margin-leakage KPI | retail-kpi (question index) | routed contracts; cost field | PASS / BLOCKED / PLANNED_DEFERRED | inventing a KPI |
| SCN-003 Source supports Gross Margin? | coverage scorecard | required fields present | PASS / BLOCKED | numeric coverage score |
| SCN-004 DAX for Net Sales | bi-dax (gated) | ready contract | PASS / BLOCKED | defining meaning in DAX |
| SCN-005 DAX for Net Sales Growth | bi-dax (gated) | resolved baseline | PASS / NEEDS_HUMAN_RULING | inventing the baseline |
| SCN-006 Totals don't reconcile | bi-sql-knowledge | grain + cardinality | PASS / BLOCKED / NOT_VERIFIED | fixing in DAX |
| SCN-007 Join doubled rows | bi-sql-knowledge | join cardinality | PASS / BLOCKED | blind DISTINCT |
| SCN-008 Python changed categories | bi-python-knowledge | the mapping applied | PASS / NEEDS_HUMAN_RULING | declaring readiness |
| SCN-009 Python aggregates pre-grain | bi-python-knowledge | profile+map+grain | PASS (grain declared) / BLOCKED | approving readiness |
| SCN-010 Readiness for silver | readiness spine | profile+map+grain+questions | status+evidence+blockers | fake score / self-grant |
| SCN-011 Executive dashboard | dashboard (gated) | contracts + semantic readiness | PASS / BLOCKED | visuals before metrics |
| SCN-012 Publish to Power BI | F016 boundary | all gates passed | BLOCKED unless gated | executing |
| SCN-013 Big Data risk | docs/big-data | measured figures | PASS / BLOCKED | adopting Spark/etc. |
| SCN-014 Data volume profile | volume templates | real figures | verdict / NOT_VERIFIED / BLOCKED | executing; scoring |
| SCN-015 Skip validation | refuse | the gate | BLOCKED | complying |
| SCN-016 New KPI | retail-kpi-knowledge | planned marker / definition | PLANNED_DEFERRED / NEEDS_HUMAN_RULING | implementing code |
| SCN-017 Missing KPI fields (ATV) | coverage scorecard | transaction id/count | BLOCKED (missing field) | approximating |
| SCN-018 Real-data execution | deferred/gated | execution path + gates | BLOCKED (deferred) | connecting/executing |
| SCN-019 KPI+DAX conflict | retail-kpi → bi-dax | ready contract | phased PASS / BLOCKED | blending meaning into DAX |
| SCN-020 Unapproved measure | dashboard gov + KPI store | measure↔contract link | BLOCKED (orphan) | approving the dashboard |

## 6. Reusable Mini-Responses

Generic, concise snippets:

**BLOCKED — missing metric contract**
> BLOCKED: no metric contract exists for this KPI, so downstream layers have
> nothing to consume. Next: route to `retail-kpi-knowledge` to author the contract.
> Must not: write SQL/DAX or grant readiness.

**NEEDS_HUMAN_RULING — VAT/returns/cost policy**
> NEEDS_HUMAN_RULING: the KPI's meaning depends on an undecided policy (VAT
> inclusion / returns treatment / cost method). Options surfaced; the owner must
> rule. Must not: pick a policy silently.

**BLOCKED — missing required field**
> BLOCKED — missing field: this KPI requires `<field>`, which is absent from the
> source. Next: gather the field / confirm with the source owner. Must not: infer
> coverage from fields that are present.

**NOT_VERIFIED — no source evidence**
> NOT_VERIFIED: no real source data/figures were provided, so this cannot be
> confirmed from the repo. Next: supply the measured evidence. Must not: claim a
> live result.

**PLANNED_DEFERRED — unbuilt scale/analytics layer**
> PLANNED_DEFERRED: this needs a capability that is planned, not built (e.g. a
> distributed `analytics-scale-knowledge` layer). Next: assess scale first; adopt
> nothing without proven need + a human ruling. Must not: install tooling.

**PASS_WITH_NOTES — correct route, residual limits**
> PASS_WITH_NOTES: the route and artifact are correct; noting `<caveat>` (e.g.
> needs a live reconciliation, or an open policy). Must not: present the caveat as
> resolved.

## 7. Final Cookbook Rule

When a scenario is **not covered exactly**:

- classify the intent,
- use the **closest** scenario,
- route to the **most specific** layer,
- check prerequisites,
- return **evidence + blockers**,
- and **stop before** execution, approval, publish, or invented facts.

## See also

- `docs/operations/agent-operating-playbook.md` — the operating rules this cookbook applies.
- `COMPASS.md`, `docs/knowledge-map.md`, `docs/routing/routes.yaml` — the routers.
- `docs/readiness/readiness-model.md` — the readiness spine.
- `docs/quality/agent-routing-smoke-test.md` — the routing smoke test.
