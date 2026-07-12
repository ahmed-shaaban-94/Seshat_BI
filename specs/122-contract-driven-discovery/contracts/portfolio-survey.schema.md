# Contract: Portfolio Survey (Layer A) Artifact Shape

**Feature**: `specs/122-contract-driven-discovery` | Anchors: FR-008, FR-009, FR-011,
FR-012, FR-014 | Phase 1 design artifact (FEATURE-LOCAL; not a top-level product contract)

This is the shape of the ONE new artifact this feature authors: the read-only,
metadata-only portfolio survey produced by the discovery skill. It is delivered to the
repo as the `templates/portfolio-survey.md` blank; this document is the design contract
its fixtures verify. It does **not** modify any top-level product contract
(`contracts/knowledge/database-to-pbip-flow.yaml` and siblings are consumed unchanged,
FR-026).

## Purpose and boundary

- The survey is the `required_outputs` of the existing `discovery` stage
  ("a committed discovery profile (tables, columns, types, candidate grains)") at
  **portfolio scale** and at the **metadata level**.
- It is **evidence and hints**, never approved semantics (FR-010).
- It is **not** the per-table value-backed profile. Value-backed checks are Layer B,
  produced by the existing per-table profiler for in-scope tables only (FR-009B/FR-013).

## MUST contain (per source)

- `source_kind`: one of `db-schema | csv | excel | file-folder` (the source kinds the
  existing profilers handle, R-7).
- `source_identity`: schema/folder identity **without** credentials, DSN, or connection
  string.
- `reachable_tables_total`: the count of inventoried tables.
- `coverage_limits`: a list that is empty when all reachable metadata was read;
  otherwise each entry names genuinely-unreachable metadata and its exact reason. It
  MUST NOT record an agent-chosen table-count or time cap (FR-014).
- `candidate_domain_evidence`, `candidate_first_scope_tables`: survey-level hints.

## MUST contain (per reachable table)

- `table_id`, `columns` (+ declared types), `declared_pk` / `declared_fks` (from
  metadata, candidate only), `candidate_grain` (from declared PK/metadata, candidate
  only), `approx_row_count` (or null + reason), `date_hints`, `pii_suspicion_hints`
  (hints only), `structural_role_hint`, `unavailable` (each item + exact reason).

## MUST NOT contain (fail-closed invariants; fixture-tested, R-4)

- **No value-backed measurement**: no measured PK uniqueness/nullability, no measured
  missingness, no measured date coverage, no raw or masked value samples, no
  returns-column population. (Those are Layer B.)
- **No raw suspected-PII value, credential, secret, DSN, or connection string** in any
  field (FR-011, Principle IX).
- **No asserted semantic ruling**: grain, PK, relationships, PII, and domain appear
  only as candidates/hints (FR-010).
- **No silent omission**: every reachable table appears; unreachable metadata is stated,
  not dropped (FR-014).

## Unavailable-boundary semantics (FR-012)

When metadata access, an optional reader, or a metadata item is unavailable, the
affected entry is marked `[PENDING LIVE PROFILE]` / `needs_sample` with the boundary
named and the enabling step stated; the survey records `warning`/`blocked`/`pending`
semantics as appropriate and never a fabricated value or false pass.

## Relationship to existing contracts (unchanged)

- Consumes the existing `discovery` stage's declared inputs/outputs; the domain guess
  and scope proposal consume this survey per the existing `domain_guess` /
  `scope_proposal` stage contracts. None of those three contract entries is modified.
- Domain/scope proposals produced downstream are records in the existing Decision Store
  (see `data-model.md` Entities 3-4 and `specs/121-.../contracts/decision-record.schema.json`).
