# Contract: `ImpactMapProjection` (machine-readable)

**Feature**: `132-decision-change-impact-map` | **Date**: 2026-07-15

The machine-readable projection is a single JSON-serializable dict. This contract fixes its required
keys and its invariants. Wire format (YAML vs JSON) is a plan-deferred detail (spec Assumptions); the
contract holds in either.

## Required top-level keys

- `schema_version` — string, `"1.0"`.
- `subject` — object: `{ decision_id, decision_type, trigger, is_preview, critical }`.
  `trigger` ∈ `"superseded"` | `"evidence_stale"` | a list of both.
- `supersession_chain` — array (possibly empty) of `{ decision_id, relation, resolved }` in pointer
  order.
- `affected` — array (possibly empty) of affected-artifact objects (see below).
- `incomplete_lineage` — array (possibly empty) of warning objects (see below).
- `cycles` — array (possibly empty) of `{ nodes[], detail }`.
- `blocking_condition` — `null` or `{ kind, detail }`.
- `generated_at` — string; EXCLUDED from any content digest.

### `affected[]` object

`{ artifact_id, kind, relation ∈ {direct,transitive}, evidence_paths[], contributing_decisions[], affected_stages[], next_actions[] }`
where `next_actions[]` items are `{ category, explanation, next_surface }` drawn from
`readiness_classify`, and `contributing_decisions[]` items are `{ decision_id, evidence_path }` naming
every changed decision that reaches this artifact (the artifact is listed once, not duplicated per
decision — spec Edge Case "multiple decisions affecting the same artifact").

### `incomplete_lineage[]` object

`{ kind ∈ {unresolved_scope_tag, unfollowable_edge, dangling_supersession_pointer, missing_cited_evidence}, locator, detail }`.

## Invariants (each maps to a spec requirement + a test)

| Invariant | Requirement | Verification |
| --- | --- | --- |
| INV-1 Disjoint `affected` vs `incomplete_lineage` | FR-015 | fixture with mixed resolvable/unresolvable refs; assert no shared reference |
| INV-2 Direct dominates a dual-reachable artifact | Edge Cases | fixture where an artifact is both; assert single `direct` entry |
| INV-3 Every `affected` has non-empty `evidence_paths` | FR-008 | structural scan |
| INV-4 No numeric score anywhere | FR-023, SC-005 | no digit-then-`%`; no `score`/`confidence`/`risk`/`risk_score`/`trust`/`completeness`/`blast_radius`/`weight` key |
| INV-5 Fail-closed, never false "no impact" | FR-019, SC-008 | degraded-input matrix; assert `blocking_condition` set, no empty-clean result |
| INV-6 Byte-deterministic modulo `generated_at` | NFR-001, SC-010 | double-run byte diff |
| INV-7 Disclosure-safe pre-write | NFR-003, SC-011 | `scan_disclosure` blocks a planted secret/PII/connection-string |
| INV-8 `affected`/`edges`/`incomplete_lineage`/`chain` stably ordered | NFR-001 | sorted-order assertion |
| INV-9 Transitive entries carry the full ordered edge evidence chain | FR-009/010/011, SC-002 | transitive fixture path assertion |
| INV-10 Cycle recorded + bounded, never a completed transitive path | FR-014, SC-006 | cyclic fixture terminates + records cycle |
| INV-11 Only reused authorities; no new store/engine/authority/model/stage/CLI-family/UI | FR-001/002/024/025, SC-013 | no-duplicate task asserts imports, not re-implementations |

## Affected-stage placement (bounded)

Affected readiness stages are recorded **per affected artifact** (`affected[].affected_stages`), read
from the existing readiness projection + flow→spine mapping (FR-017). There is intentionally no
top-level change-level `affected_stages` key: a stage is meaningful only relative to a resolved
artifact. On a run where `affected[]` is empty and everything is an `incomplete_lineage[]` warning,
there is correctly no affected stage to name — the honest reading is "impact undetermined" (the
warnings), not "no stages affected." If a change-level roll-up of the distinct affected stages is
wanted later, it is a deterministic derivation from `affected[].affected_stages` and adds no new
authority.

## Human/machine parity

The human rendering MUST present the identical content set (subject, chain, direct-then-transitive
affected with evidence paths + stages + next actions, incomplete-lineage, cycles, blocking condition).
No content in one form is absent from the other (SC-009).
