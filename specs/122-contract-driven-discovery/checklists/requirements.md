# Specification Quality Checklist: Contract-Driven Discovery-to-Decision Flow

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-12
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- **All 3 clarifications resolved by the owner 2026-07-12** (recommended option each; see spec Clarifications):
  1. **FR-005** — delivery surface = **a new dedicated skill** (Option-B skill-driven; mirrors 121's `business-knowledge-interview`).
  2. **FR-013** — profile boundary = **portfolio survey first, then per-table onboarding** (does not restate per-table `source-profile.md`).
  3. **FR-019** — domain/scope = **non-critical proposals confirmed in the interview**; NO new critical decision type, NO new `approval-authority.yaml` row (121's vocabulary + authority map stay frozen).

### Review corrections applied (spec revision, 2026-07-12)

Four scope/contract inconsistencies found during review were resolved. Each is now internally consistent and verified against what is shipped on `main` (spec 121, PR #257, the Decision Store schema/loader):

1. **Portfolio survey vs deep per-table profiling** — the FR-009/FR-013 conflict (survey deep-measures every table vs "do not duplicate the per-table profiler") is removed by defining two explicit layers: **Layer A** (FR-009) is a read-only portfolio *metadata* survey across all reachable tables (identity, inventory, declared types, declared PK/FK metadata, approximate/metadata row count, name/type-based date & PII *hints*, structural role hints, coverage limits, candidate domain/scope evidence — hints, never rulings); **Layer B** (FR-009B) is the deep value-backed profile that runs ONLY for in-scope tables through the existing `retail-onboard-table` / Source Ready profiler. US1 (incl. AC1/AC2/AC4/AC6 + new AC7), SC-001/SC-002, MVP Boundary, entities, and the value-backed edge cases were swept to match. The MVP shrinks cleanly to Layer A; no deep profiling occurs at MVP. It is structurally impossible for the future plan to build a second per-table profiler.
2. **Deterministic scope-bounding** — the subjective, non-testable phrase "reasonable first delivery slice" is removed (0 occurrences remain). FR-018 / US3 now bound scope deterministically: honor an explicit user-supplied scope limit; else prefer one coherent business process / one primary fact grain / KPIs sharing a coherent model boundary; detect cross-boundary evidence; present narrower coherent options or record `needs_user_input`; describe a scope categorically only as coherent / cross-boundary / unresolved / needs-user-input (prose, not a stored scale); no numeric score, table-count threshold, fabricated rank, or silent default.
3. **Explicit Decision Store lifecycle for domain/scope proposals** — verified against `decision-record.schema.json`, `decision_store.py`, the DS-rule code, the DS3 batch test fixtures (`test_decision_store_rules.py`), and spec 121's `data-model.md`: there is **no `confirmed` status**; the nine statuses and the batch/supersession mechanics are 121's. Spec 122 introduces no new status and no new confirmation mechanic, and pins only what is provably true under 121 (the exact recorded status of a batch-confirmed member is left to follow 121's existing convention — the shipped `batch` object lacks `evidence_identity`/`reviewed_scope`, so the resting status is under-determined in what is shipped and is NOT 122's to fix). FR-019 maps all six lifecycle events to existing statuses/fields only: agent proposes (`proposed` + `confidence` + `proposed_by`=agent) -> named human confirms via a `batches[]` entry (`confirmed_by` = named human + authority class, `batch_id` on the member) on the non-critical batch path (which triggers no authority-class eligibility check and needs no new authority-map row) -> reject (`status: rejected`) -> partial accept (FR-019B: a bounded superseding `proposed` record; original -> `superseded`) -> change (supersession) -> rerun (present, never overwrite). The DS2 fact (any `approved` record fires the full approval-completeness requirement regardless of criticality) is used as the *reason* confirmation must route through the low-risk batch path rather than a naive status flip — not as a pin on the outcome. The agent never self-confirms; no new status, no new decision_type, no new authority-map row.
4. **Global machine-readable missing-decision work deferred** — spec 122 no longer expands into a global Decision Gate repair. US5 / FR-024–FR-027 are narrowed to truthful *local* stops within the bounded flow (`portfolio discovery -> domain -> scope -> selected-table onboarding -> interview handoff -> stop`). The global concerns (all-eleven-stage machine-readable `required_inputs`, detecting a specific completely-absent critical decision inside a non-empty store, general Decision Gate / all-stage next-action) are moved to a clearly labeled non-blocking **"Future follow-up: Machine-Readable Required Decisions and Stage Inputs"** section, which records that PR #257 already fails closed for absent/empty/malformed store, invalid approvals, conflicts, and missing evidence. That future spec is NOT created here. SC-005/SC-007 were narrowed accordingly.

- All checklist items pass **after** the four corrections above (each was re-verified against the revised text, not auto-retained). No `[NEEDS CLARIFICATION]` marker remains and no unresolved contradiction survives. Spec is ready for `/speckit-clarify` (optional) or `/speckit-plan`. Per project policy the plan chain is not fired without an owner "go".
- Bound references to already-shipped artifacts (contracts, spine, Decision Store schema) are binding product contracts, not implementation leakage — citing them is required by the reconciliation mandate.
