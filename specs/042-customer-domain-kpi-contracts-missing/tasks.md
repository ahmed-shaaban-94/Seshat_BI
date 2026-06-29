---
description: "Task list for Customer Domain KPI Overview (domains/customer.md)"
---

# Tasks: Customer Domain KPI Overview (domains/customer.md)

**Input**: Design documents from `specs/042-customer-domain-kpi-contracts-missing/`

**Prerequisites**: plan.md (required), spec.md (required for user stories). No research.md /
data-model.md / contracts/ exist by design (docs-only content feature; no contracts authored).

**Tests**: No software tests apply (no code). Verification is the static `retail check` gate plus
content scans, captured as explicit checking tasks below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 (customer.md exists) / US2 (router stays accurate) / POL (cross-cutting policy)
- Paths are exact and committed-text only.

## Scope guard (read first)

- The unit of work is ONE new file `skills/retail-kpi-knowledge/domains/customer.md` plus TWO edits
  to `skills/retail-kpi-knowledge/INDEX.md`. Nothing else is created or edited.
- DO NOT author any file under `skills/retail-kpi-knowledge/contracts/` (Principle: each customer
  contract needs the F009 process + a confirmed PII ruling first).
- DO NOT answer the four Principle-V judgment calls (identity/grain, PII publish-safety,
  business-segment rollup, product identity); carry them as stop-and-ask markers only.
- DO NOT assume any deferred capability exists (F016 Power BI Execution Adapter; F031-F033
  spec-only runtimes). No executor, no DB, no network.

---

## Phase 1: Setup / grounding (shared)

- [ ] T001 [P] Re-read the 11 sibling files in `skills/retail-kpi-knowledge/domains/` to confirm the
  exact mirror structure (H1 + summary; `## KPIs in this domain`; `## Decision questions this domain
  answers`; `## Key ambiguities`; `## Owner`; `## Notes`). Use `domains/inventory.md` (all-Planned
  domain) as the closest precedent.
- [ ] T002 [P] Re-read `skills/retail-kpi-knowledge/knowledge/retail-kpi-domains.md` Customer section
  (the meta-reference the overview expands from) and confirm the 10 contract filenames in
  `skills/retail-kpi-knowledge/contracts/` so the decision-questions table references only real files.
- [ ] T003 [P] Re-read constitution Principle V text in `.specify/memory/constitution.md` to copy the
  stop-and-ask wording VERBATIM (default-drop PII; analyst-supplied value->group table; grain ruling).

---

## Phase 2: US1 -- Customer domain has an honest, navigable overview (Priority: P1)

**Goal**: the single deliverable file exists, mirrors siblings, all-Planned, with the Principle-V
section. **Independent test**: open the file; every KPI/decision row is a seeded ref or honest Planned
marker; the PII/identity section restates the stops and answers none.

- [ ] T004 [US1] Create `skills/retail-kpi-knowledge/domains/customer.md` with the H1 title and a 1-2
  line generic-retail summary (retention, frequency, lifetime value; requires reliable customer
  identification -- which is an unmade ruling).
- [ ] T005 [US1] Add the `## KPIs in this domain` table (KPI | Contract | Status). Rows: Customer
  Retention Rate, Purchase Frequency, Customer Lifetime Value (CLV), New-vs-Returning Customer split
  -- ALL Status `Planned`, Contract column `--`, each naming the identity-ruling prerequisite. Zero
  `Seeded` rows; zero fabricated formula.
- [ ] T006 [US1] Add the `## Decision questions this domain answers` table (Decision question | Routes
  to | Status). Each row routes to a seeded contract reference ONLY where genuinely applicable, else an
  honest Planned marker. Include the invariant line "a question never implies a formula and never
  invents a contract." Invent no contract.
- [ ] T007 [US1] Add the `## Key ambiguities` section (e.g. identity resolution across channels;
  retention window definition; CLV horizon and discounting; one-time vs repeat customer) -- as ambiguity
  notes, not decisions.
- [ ] T008 [US1] Add the `## Owner` section naming generic retail functions only: "Marketing / CRM and
  Finance (with Governance for any PII publish ruling)". No named person, no C086 specifics.
- [ ] T009 [US1] Add the `## Notes` section: explicitly state no customer metric contract is seeded;
  each future contract needs the F009 contract-template + review process AND a confirmed identity/PII
  ruling first; customer KPIs are non-additive (rates/ratios) and identity-dependent.
- [ ] T010 [US1] Add the NEW `## Owner ruling triggers (PII / identity)` section (absent from the 11
  siblings) carrying the Principle-V stop-and-ask VERBATIM for: customer identity/grain; PII
  publish-safety (DEFAULT IS DROP; governance signs off); business-segment rollups (analyst supplies
  the value->group table). State the stops; decide NONE. Note this section is customer-only for now
  (not retrofitted to the 11 siblings).

---

## Phase 3: US2 -- Router file-map and route status stay accurate (Priority: P2)

**Goal**: INDEX resolves the Customer route to the new file and the file-map count is correct.
**Independent test**: diff `INDEX.md`; Customer row points at `domains/customer.md`; count reads 12.

- [ ] T011 [US2] Edit `skills/retail-kpi-knowledge/INDEX.md` Customer domain route (around line 59):
  replace the `[planned] -- ... no dedicated domains/customer.md file yet` text with a pointer to
  `domains/customer.md` and status "[seeded] -- overview; per-KPI contracts [planned]".
- [ ] T012 [US2] Edit `skills/retail-kpi-knowledge/INDEX.md` file-map (around line 81): change
  "per-domain KPI overviews (11 files)" to "(12 files)".

(T011 and T012 edit the same file -- run sequentially, not [P].)

---

## Phase 4: Verification / policy (cross-cutting)

- [ ] T013 [POL] Run the repo static gate `retail check` over the changed text; confirm it exits 0
  with no new rule violation and no fabricated readiness/confidence score (hard rule #9).
- [ ] T014 [P] [POL] Generic-retail token scan: grep `domains/customer.md` for pharmacy/C086 tokens
  (patient, insurance, payer, prescription, dispense, NDC, loyalty-card-specifics) -- must be ZERO
  (Principle VII).
- [ ] T015 [P] [POL] All-Planned scan: confirm zero `Seeded` rows and zero numeric/formula content in
  the KPIs and decision-questions tables (Principle VIII).
- [ ] T016 [P] [POL] Principle-V integrity check: confirm the four judgment calls remain UNANSWERED in
  the file (stated as stops, not resolved) and that no file under `contracts/` was created (count stays
  10).
- [ ] T017 [P] [POL] Encoding check: `domains/customer.md` and the `INDEX.md` edits are ASCII, UTF-8
  without BOM, using `--` and `->` (no Unicode glyphs; rule IX).
- [ ] T018 [POL] Readiness check: confirm the work grants/advances NO readiness or dashboard-readiness
  stage anywhere (Principle I); the front-matter "Readiness stage advanced: none" stays true.

---

## Dependencies

- Phase 1 (T001-T003) before Phase 2.
- Phase 2 (T004-T010) before Phase 3 (the route should point at a file that exists).
- Phase 3 before Phase 4 verification.
- T004 blocks T005-T010 (same file). T011 blocks T012 (same file).
- Verification tasks T014-T017 are [P] (independent read-only scans); T013 and T018 gate the whole.

## Implementation notes

This is a human-approved authoring run executed LATER from this plan; the planning workflow itself
writes none of `domains/customer.md` or the `INDEX.md` edits. No code, no executor, no DB, no network.
