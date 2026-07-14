# Phase 1 Data Model: Shareable Seshat Proof (Showcase Bundle)

All shapes below are **derived projections** over already-shipped documents. None
is a new persisted schema; none is written back to any source artifact. The
showcase reads the Explorer projection and (optionally) two Passport snapshots
and renders a bundle plus a manifest. "Reused (verbatim)" means the field is
carried straight from the shipped document without re-derivation.

## Entity: ShowcaseBundle

The top-level in-memory document `build_showcase_bundle` returns; the input to
`render_showcase_html`.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `schema_version` | string | new (`"1.0"`) | Bundle projection version; NOT a readiness schema. |
| `workspace` | object | reused from Explorer projection | `{label, source_revision}`; revision truncated for display at render time. |
| `tables` | list[TableView] | reused from `build_explorer_projection` | Per-table stages/evidence/blockers/approvals/next-action, verbatim. |
| `lineage` | object | reused from Explorer projection | `{nodes, edges}`; includes input-defect nodes verbatim. |
| `badge` | Badge | new (derived, R4) | Evidence-derived; no score. |
| `manifest` | DisclosureManifest | new (derived, US3) | Four-category ledger. |
| `comparison` | Comparison \| null | new (optional, R5) | Present only when two comparable snapshots supplied. |
| `disclosure` | object | reused from Explorer projection | `scan_disclosure` result; render is gated on `status == "pass"`. |
| `generated_at` | string \| null | new | Set at render/write time; excluded from any content digest. |

## Entity: TableView (reused verbatim)

Carried straight from `build_explorer_projection`'s per-table entry; the showcase
does not add or re-derive any field.

| Field | Type | Notes |
|-------|------|-------|
| `table_id` | string | Reused. |
| `source_path` | string | Reused. |
| `current_stage` | string \| null | Reused; `null`/input-defect entries preserved. |
| `stages` | map[stage -> {status, evidence[], blocking_reasons[]}] | Reused; `evidence[]` items carry `{reference, state}` where state in {available, missing, deferred}. |
| `next_action` | string | Reused. |
| `approvals` | list[receipt] | Reused (`_approval_receipts`); records `valid_shape`, never grants approval. |
| `input_defect` | string (optional) | Reused; a malformed readiness file is an input defect, never a pass. |

## Entity: Badge (new, derived -- R4/FR-012..015)

| Field | Type | Derivation | Constraint |
|-------|------|------------|------------|
| `highest_contiguous_pass` | string \| null | The last stage in spine order for which this and all prior stages are `pass`; `null` if none. | Reflects evidence only. |
| `passed_stage_count` | int | Count of `pass` stages (portfolio or per-table, per render mode). | 0..7. |
| `total_stages` | int | 7 | Constant. |
| `next_blocked_stage` | string \| null | First non-`pass` stage after the contiguous run. | For the "X: blocked" label. |
| `label` | string | e.g. `"3/7 stages ready -- Gold: blocked"`; when none pass: earliest-stage/onboarding text. | MUST NOT contain `%`, a grade, or a fabricated score (FR-013). |
| `svg` | string | Inline SVG markup / data URI. | Offline; no external fetch (FR-014). |

## Entity: DisclosureManifest (new -- US3/FR-016..019)

A four-category ledger. Every composed item appears under exactly one category
(FR-018). Each entry carries a locator.

| Field | Type | Notes |
|-------|------|-------|
| `included` | list[ManifestEntry] | Evidence with state `available`. |
| `unavailable` | list[ManifestEntry] | Deferred live sentinels (`[...]`) and prose evidence (Passport `unavailable`). |
| `omitted` | list[ManifestEntry] | Missing artifacts, input defects, out-of-scope tables/stages. |
| `redacted` | list[ManifestEntry] | By-design portability normalizations the composer applied. |

### ManifestEntry

| Field | Type | Notes |
|-------|------|-------|
| `category` | enum | included \| unavailable \| omitted \| redacted. |
| `locator` | string | Table/stage/evidence reference or path label. |
| `reason` | string | Short human note (e.g. "deferred live check", "absolute path reduced to repo-relative", "table out of scope"). |
| `original_class` | string \| null | For redacted: what was normalized (e.g. `absolute_path`, `private_url`). |

## Entity: Comparison (new, optional -- R5/FR-020..021)

Present only when two comparable Passport snapshots are supplied.

| Field | Type | Notes |
|-------|------|-------|
| `comparable` | bool | True iff same `schema_version` + `scope`, differing `source_revision`. |
| `omitted_reason` | string \| null | When not comparable, the truthful note (e.g. "scopes differ"); the section is omitted. |
| `before_revision` | string \| null | From the earlier snapshot. |
| `after_revision` | string \| null | From the later snapshot. |
| `stage_transitions` | list[{table_id, stage, before_status, after_status}] | Only real transitions; empty list is valid (no fabricated delta). |
| `evidence_verdicts` | list[{path, verdict}] | Uses Passport verify vocabulary (verified/changed/missing/unavailable/incompatible). |

## Invariants (enforced by tests, not a new gate)

- **INV-1**: No `stages[*].status == "pass"` renders without at least one evidence item (inherited from the Explorer projection invariant; re-asserted in showcase tests).
- **INV-2**: `badge.label` matches none of `/%/`, grade tokens, or numeric confidence patterns.
- **INV-3**: Every reference in `tables`/`lineage` appears in exactly one manifest category (coverage + disjointness).
- **INV-4**: When `disclosure.status != "pass"`, no bundle file is written (fail-closed).
- **INV-5**: `comparison` is `null` unless two comparable snapshots are supplied; `stage_transitions` contains only observed transitions.
- **INV-6**: The shipped `explorer.css` / `explorer.js` and every source artifact are byte-unchanged after generation.
