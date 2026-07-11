# Phase 1 Data Model: Capability Inventory

The model is a single hand-authored manifest of `Capability` records, plus the derived
`InventoryRecord` the builder renders. All enums are CLOSED (FR-004: no free-form catch-all
that defeats determinism). The manifest adds NO run-state (it is not a readiness file).

## Entity: Capability (one entry in `docs/capabilities/capabilities.yaml`)

| Field | Type | Owner | Notes |
|-------|------|-------|-------|
| `id` | string (stable slug) | manifest | Stable identity; the sort key for determinism. Kebab-case. |
| `name` | string | manifest | Human-readable name. |
| `summary` | string | manifest | One-line description. |
| `state` | enum `LIFECYCLE` | manifest (shipped-ness feeder-reconciled) | LIFECYCLE axis ONLY: `shipped` \| `spec-only` \| `deferred`. MUST NOT hold authority/provenance values. `shipped` requires positive feeder backing (D4c). |
| `authority` | enum `AUTHORITY` | manifest | `agent-runnable` \| `advisory` \| `human-gated`. Whose decision/action it is. |
| `surface` | enum `SURFACE` | manifest | `cli` \| `skill` \| `execution-adapter` \| `plugin` \| `docs` \| `human-artifact`. What KIND of thing it is. |
| `requirements` | enum `REQUIREMENT` (list, may be empty) | manifest | `[]` (none) \| `database` \| `optional-dependency`. Empty => "Available now" eligible. |
| `provenance` | enum `PROVENANCE` | manifest | `locally-verified` \| `publicly-released` \| `unrecorded`. `publicly-released` requires committed release evidence (D4d). Default `unrecorded`. |
| `readiness_stage` | enum `STAGE` \| `not-stage-scoped` | manifest (validated vs existing stage source) | Optional; default `not-stage-scoped`. Valid stage tokens are the snake_case `stages.*` KEYS of `templates/readiness-status.yaml` (the single canonical source, D5) -- e.g. `source_ready`, `mapping_ready`, ... `publish_ready`. NOT the Title-Case prose form. |
| `command` | string \| null | manifest, MUST match feeder | Canonical entry-point command when one exists (e.g. `retail check`); reconciled against `_DISPATCH` wiring. `null` for non-command capabilities. |
| `documentation` | string (repo-relative path) | manifest, MUST exist | Canonical doc/spec pointer; the referenced path MUST exist (orphan check, D4a). |
| `references` | map<feeder, key> (optional) | manifest | Explicit pointers to feeder facts (e.g. `{rules_manifest: "AP1"}`, `{skill: "retail-validate"}`, `{roadmap: "F029"}`). Drives the oracle's reconciliation. |

### Validation rules (enforced by the oracle test, D4)

1. Every `id` is unique and kebab-case; the record set sorts deterministically by `id`.
2. `state` in `{shipped, spec-only, deferred}` ONLY -- never an authority/provenance token.
3. `state: shipped` => at least one `references` entry resolves to a POSITIVE ship signal
   (roadmap F-row SHIPPED; `status-claims` `built`; a `_DISPATCH` command; or a
   frontmatter'd `SKILL.md`). No positive signal => oracle FAILS (fail-closed).
4. `provenance: publicly-released` => a committed release-evidence reference resolves;
   else oracle FAILS.
5. Every `references` target EXISTS in its feeder (orphan check); every referenced fact
   the manifest echoes (e.g. a rule title, if echoed) AGREES with the feeder (FR-014).
6. Every real wired REPRESENTATION of a covered kind (a `_DISPATCH` command; a
   frontmatter'd `SKILL.md`; a `kit-source.yaml` verb) is REFERENCED BY SOME manifest
   entry's `references` (unlisted check = reference-coverage, not one-entry-per-
   representation; a capability with a command + same-named skill + verb is ONE entry
   whose `references` cover all three).
7. `documentation` path exists; `command` (if non-null) is a wired `_DISPATCH` key.
8. No field carries a numeric maturity/confidence/completeness/health value (FR-009).

## Derived entity: InventoryRecord (what the builder renders)

Projected per Capability by joining the manifest with the referenced feeders. Read-only;
never persisted. Carries the manifest's categorical fields PLUS any referenced feeder fact
resolved at render time (e.g. the rule title from `rules-manifest.json`), so titles are
shown from the feeder, not the manifest.

## Grouping (FR-006 / FR-008): fixed precedence -> exactly one primary group

Each capability lands in EXACTLY ONE primary human-readable group by this fixed, documented
precedence (top wins), so no item is dropped or duplicated:

1. **Deferred / not shipped** -- if `state in {spec-only, deferred}`.
2. **Human-gated** -- else if `authority == human-gated`.
3. **Requires database or optional dependency** -- else if `requirements` non-empty.
4. **Agent / companion** -- else if `authority == advisory` OR `surface == skill`.
5. **Available now** -- otherwise (shipped, agent-runnable, no requirement).

The record's OTHER axes remain visible in its line/record even though the primary group is
singular (e.g. a shipped human-gated console shows `state: shipped` in its record while
sitting in the Human-gated group). Provenance is shown verbatim on every record and never
upgraded.

## The four axes are orthogonal (FR-005)

`state` (lifecycle) x `authority` x `requirements` x `provenance` are independent; the
primary-group precedence above is the ONLY place they are collapsed, and only for display
ordering -- the underlying record keeps all four. This is what makes FR-008 well-defined.
