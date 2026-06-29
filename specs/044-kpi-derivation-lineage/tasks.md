---
description: "Task list for KPI Derivation-Lineage Contract (base-vs-derived dependency graph)"
---

# Tasks: KPI Derivation-Lineage Contract (base-vs-derived dependency graph)

**Input**: Design documents from `specs/044-kpi-derivation-lineage/`

**Prerequisites**: plan.md (required), spec.md (required for user stories). No research.md /
data-model.md / Spec-Kit contracts/ exist by design (docs-only DEFINE-layer content; the edge set
is read from the existing KPI-MC contracts).

**Tests**: No software tests apply (no code). Verification is the static `retail check` gate plus
content/provenance scans, captured as explicit checking tasks below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 (lineage doc) / US2 (Derives-from section seam) / US3 (router stays accurate) /
  POL (cross-cutting policy)
- Paths are exact and committed-text only.

## Scope guard (read first)

- The unit of work is: ONE new file `references/kpi-derivation-lineage.md`; a `**Derives from**`
  section added to `references/metric-contract-template.md` (placeholder) and to two contracts
  (`contracts/net-sales.md`, `contracts/average-transaction-value.md`); and an OPTIONAL routing row
  in `INDEX.md`. Nothing else is created or edited.
- DO NOT add a `**Derives from**` section to the other 8 contracts (out of first-step scope; a later
  mechanical follow-up).
- DO NOT introduce YAML front-matter anywhere (the rejected over-scope representation).
- DO NOT INVENT any derivation edge not stated in committed contract prose (Principle V). Transcribe
  only; cite each edge's source. Declaring a new edge is a carried stop-and-ask the agent must not
  cross.
- DO NOT draw an edge to a non-contract node (growth, sales per sqm, vs-target, COGS, Return Value).
- DO NOT alter the existing Unicode glyphs in the contract bodies (out of scope); NEW text is ASCII.
- DO NOT compute, rank, or score any KPI; DO NOT build a generator/executor; DO NOT assume any
  deferred capability (F016 Power BI Execution Adapter; F031-F033 spec-only runtimes).

---

## Phase 1: Setup / grounding (shared)

- [ ] T001 [P] Re-read the 10 contract files in `skills/retail-kpi-knowledge/contracts/` and record,
  per contract, the verbatim "Formula in business terms" / "Required fields" prose that states (or
  does not state) a derives-from relationship. This is the source of every edge -- the edge set MUST
  come from here, not from this plan's restatement.
- [ ] T002 [P] Re-read `skills/retail-kpi-knowledge/references/metric-contract-template.md` to find
  the exact insertion point for the new `**Derives from**` section (adjacent to "Formula in business
  terms").
- [ ] T003 [P] Re-read `skills/retail-kpi-knowledge/references/id-conventions.md` (KPI-MC ID table)
  and confirm the 10 ID-to-KPI bindings so every edge cites a real, correct KPI-MC ID, never a
  filename.
- [ ] T004 [P] Re-read `skills/retail-kpi-knowledge/INDEX.md` routing table (lines ~20-26) and the
  references prose summary (line ~85) to confirm INDEX does NOT claim a references file-count, so the
  optional router edit is a routing-row + prose-mention only (no count bump).

---

## Phase 2: US2 -- The `Derives from` section seam (Priority: P2, authored first as the reusable seam)

**Goal**: the template and two exemplar contracts carry a `**Derives from**` body section.
**Independent test**: diff the template + two contracts; each has the section; template is generic
placeholder; net-sales is "none -- base KPI"; ATV lists KPI-MC-02 + KPI-MC-04.

- [ ] T005 [US2] Edit `skills/retail-kpi-knowledge/references/metric-contract-template.md`: add a
  `**Derives from**` body section (placeholder guidance: "List the base KPI(s) this metric is
  computed from, by stable KPI-MC ID -- e.g. `KPI-MC-02, KPI-MC-04`. State `none -- base KPI` for a
  metric computed directly from fact fields. Reference IDs, never filenames."). Place it adjacent to
  "Formula in business terms". Keep it inside the template's markdown body -- NO YAML front-matter.
- [ ] T006 [US2] Edit `skills/retail-kpi-knowledge/contracts/net-sales.md` (KPI-MC-02): add a
  `**Derives from**` section stating "none -- base KPI" with a one-line note that this is the primary
  realized-revenue base (consistent with its committed "Base for growth, margin, ATV ..." prose). Do
  not alter existing glyphs.
- [ ] T007 [US2] Edit `skills/retail-kpi-knowledge/contracts/average-transaction-value.md`
  (KPI-MC-05): add a `**Derives from**` section listing `KPI-MC-02` (Net Sales) and `KPI-MC-04`
  (Transactions Count), transcribed from its committed "ATV = Net Sales / Transactions Count" and
  "net sales amount (from Net Sales contract)" prose. Do not alter existing glyphs.

(T005, T006, T007 are different files -- may run [P]. They are listed sequentially for clarity.)

---

## Phase 3: US1 -- The base-vs-derived lineage graph doc (Priority: P1, the core deliverable)

**Goal**: one new doc renders the full 10-node graph with cited edges. **Independent test**: open
the doc; 4 base + 6 derived; every edge cites contract prose; no edge to a non-contract node.

- [ ] T008 [US1] Create `skills/retail-kpi-knowledge/references/kpi-derivation-lineage.md` with an H1
  title, a 2-3 line generic-retail purpose (a static map of which KPIs are base vs derived and which
  base each derived KPI depends on; never a score; read from committed contract prose), and a stated
  scope: the 10 existing KPI-MC contracts only.
- [ ] T009 [US1] Add the BASE-KPI list: KPI-MC-01 Gross Sales, KPI-MC-03 Quantity Sold, KPI-MC-04
  Transactions Count, KPI-MC-06 Discount Amount -- each marked base (no derives-from edge), citing
  the contract prose that shows a direct SUM/COUNT over fact fields.
- [ ] T010 [US1] Add the DERIVED-KPI edge list, every edge by KPI-MC ID with a verbatim-ish prose
  citation:
  - KPI-MC-02 Net Sales derives_from KPI-MC-01, KPI-MC-06 -- "Net Sales = Gross Sales - total
    discount (line + header), pre-tax".
  - KPI-MC-05 ATV derives_from KPI-MC-02, KPI-MC-04 -- "ATV = Net Sales / Transactions Count".
  - KPI-MC-07 Discount Rate % derives_from KPI-MC-06, KPI-MC-01 -- "Discount Rate % = Discount Amount
    / Gross Sales * 100".
  - KPI-MC-08 Returns Rate % derives_from KPI-MC-02 -- "Returns Rate % = Return Value / Net Sales *
    100" (Return Value is a field, NOT a contract node -- so no edge to it).
  - KPI-MC-09 Gross Margin derives_from KPI-MC-02 -- "Gross Margin = Net Sales - COGS" (COGS is a
    field, NOT a contract node -- so no edge to it).
  - KPI-MC-10 Gross Margin % derives_from KPI-MC-09, KPI-MC-02 -- "Gross Margin % = Gross Margin /
    Net Sales * 100".
- [ ] T011 [US1] Add a short "Not nodes" note listing the named downstream USES (growth, sales per
  sqm, vs-target) and the FIELDS (COGS, Return Value) that appear in contract prose but are NOT
  contracts, so a reader understands why no edge points at them. Add a "blast-radius" sentence: a
  change to a base KPI's definition (e.g. Net Sales VAT ruling) propagates to KPI-MC-05, KPI-MC-08,
  KPI-MC-09, KPI-MC-10.
- [ ] T012 [US1] Add a "Provenance" closing note: every edge above was transcribed from committed
  contract prose; no edge was invented; declaring a NEW derivation relationship not stated in a
  committed contract is a metric-owner ruling (Principle V), out of scope for this doc.

---

## Phase 4: US3 -- Router stays accurate (Priority: P3, optional)

**Goal**: a reader can find the new doc from INDEX. **Independent test**: diff `INDEX.md`; a routing
row points at `references/kpi-derivation-lineage.md`; the references prose summary mentions it.

- [ ] T013 [US3] Edit `skills/retail-kpi-knowledge/INDEX.md`: add a routing-table row (e.g. "See how
  KPIs derive from base KPIs | `references/kpi-derivation-lineage.md` | -- ") and append
  "derivation lineage" to the references prose summary (line ~85). NO file-count bump (INDEX claims
  no references count). If, on re-read, INDEX genuinely has no suitable routing surface, SKIP this
  task and record in plan-review that the references dir is not enumerated.

---

## Phase 5: Verification / policy (cross-cutting)

- [ ] T014 [POL] Run the repo static gate `retail check` over the changed text; confirm it exits 0
  with no new rule violation and no fabricated readiness/confidence score (hard rule #9).
- [ ] T015 [P] [POL] Edge-provenance check: for every edge in `kpi-derivation-lineage.md` and the two
  contract `**Derives from**` sections, confirm a matching statement exists in the cited contract's
  committed prose; confirm ZERO invented edges and ZERO edges to a non-contract node (growth, sales
  per sqm, vs-target, COGS, Return Value) (Principle V; FR-005/FR-006).
- [ ] T016 [P] [POL] Generic-retail token scan: grep all authored/edited files for pharmacy/C086
  tokens (patient, insurance, payer, prescription, dispense, NDC, billing-code) -- must be ZERO
  (Principle VII).
- [ ] T017 [P] [POL] No-score scan: confirm the lineage doc and `**Derives from**` sections contain
  no computed value, ranking, or numeric confidence/readiness score (Principle VIII; hard rule #9).
- [ ] T018 [P] [POL] Representation check: confirm NO YAML front-matter was introduced; the
  `**Derives from**` section is in the markdown body of the template + exactly the two exemplar
  contracts; the other 8 contracts are unchanged (FR-001/FR-003 scope).
- [ ] T019 [P] [POL] Encoding check: all NEW authored text is ASCII, UTF-8 without BOM, using `-`,
  `/`, `*`, `->` (no Unicode glyphs); the existing contract-body glyphs were NOT altered (rule IX,
  FR-009).
- [ ] T020 [POL] Readiness check: confirm the work grants/advances NO readiness or
  dashboard-readiness stage (Principle I); the spec front-matter "Readiness stage advanced: none"
  stays true; no executor/DB/network/generator was added.

---

## Dependencies

- Phase 1 (T001-T004) before Phases 2-3 (the edge set must be read from the contracts first).
- Phase 2 (T005-T007, the seam) and Phase 3 (T008-T012, the doc) both consume the Phase-1 reading;
  the doc (US1) is the P1 core deliverable, the seam (US2) is authored first as it is the smaller,
  reusable change. Either order works since they touch different files.
- Phase 4 (T013) after Phase 3 (route should point at a file that exists).
- Phase 5 verification after Phases 2-4.
- T008 blocks T009-T012 (same new file). Verification scans T015-T019 are [P]; T014 and T020 gate
  the whole.

## Implementation notes

This is a human-approved authoring run executed LATER from this plan; the planning workflow itself
writes none of the contract/template/lineage/INDEX text. No code, no executor, no DB, no network, no
generator. The edge set is a transcription of committed contract prose, never an invention
(Principle V).
