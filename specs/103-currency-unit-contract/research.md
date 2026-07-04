# Research: Currency / Unit-of-Measure Contract

**Feature**: 103-currency-unit-contract | **Date**: 2026-07-04 | **Phase**: 0

## Purpose

Confirm this feature reuses shipped SHAPES and shipped PARSING mechanisms
rather than inventing new ones, before any design decision in `plan.md` is
made. Every finding below cites a real, already-committed repo path.

## Precedent survey

### P1 -- Closest sibling: `specs/092-rls-access-readiness/` (HR6, in-flight, reserved id, not yet shipped)

092 is cited in the spec itself as the pattern this feature mirrors (Boundary
section). It is the closest precedent available for HOW a new single-purpose
static rule folds into the EXISTING Semantic Model Ready gate: one new
template-or-template-field, one new rule module registered under a reserved
id, one doc-listing edit to `docs/readiness/semantic-model-ready.md`, zero
change to `retail-semantic-check`'s own logic. Its `plan.md`/`research.md`
Constitution Check table, Project Structure shape, and "Deferred capabilities
NOT assumed" section are the direct template this feature's four Phase-0/1
files follow.

**Critical structural difference from 092 (do not carry over by analogy):**
092 ADDS a wholly NEW file (`templates/rls-role-contract.yaml`) and touches
NEITHER existing template -- its success criterion is literally "zero lines
changed in `metric-contract.yaml`/`kpi-pack.yaml`." This feature (103) is the
opposite shape: it EDITS two existing templates that are already the
authoritative artifacts for their respective concerns --
`templates/source-map.yaml` gains two new per-column keys
(`columns[].unit`, `columns[].currency`), and `templates/metric-contract.yaml`
gains exactly one new top-level key (`unit`). There is no new template file
in this feature. Verification in this feature's `quickstart.md` therefore
confirms the additions LANDED (a non-empty, additive diff on both files),
not that a diff is empty.

**Decision**: reuse 092's SHIPPING PATTERN (declare via template field(s) +
one reserved-id static rule + one doc-listing edit), but do not reuse its
"new separate file" structural choice -- this feature's two template edits
are additive-only changes to the two already-shipped, in-place templates.

### P2 -- Metric-contract shape to extend: `templates/metric-contract.yaml` (F009)

Already defines `identity` (`name`), `grain`, `formula_intent`, `owner`, and
`binds_to` (`gold_table`, `columns[]`, `pii_sensitive`), plus the four-status
`readiness` block and the per-contract `ambiguities[]` ledger (spec 058). The
file's own header (`THE DEFINE / CHECK BOUNDARY`) states F009 DEFINES,
F010/HR11-style checks CHECK -- a later feature reading this template must
not blur that boundary by adding check logic into the template file itself.

**Decision**: add exactly one new top-level key, `unit`, sibling to `grain`
and `binds_to` (FR-002). Per the Scope Guard and Q3 (spec Clarifications),
this key is DOCUMENTARY only -- HR11 never cross-checks it against
`binds_to.columns[]`'s own declared units; HR11's comparison is strictly
column-to-column among `binds_to.columns[]`. No `currency` key is added to
this file (currency agreement is validated across the bound columns' own
`columns[].currency` declarations in `source-map.yaml`, never against a
metric-level field).

### P3 -- Source-map shape to extend: `templates/source-map.yaml` (medallion playbook Phase 2.1-2.5)

Already records, per source column, `decision`, `reason`, `rename_to`,
`silver_type`, `missing_policy`, `pii`, `gold_placement` -- the Phase
2.1-2.5/2.7-2.8 mapping decisions the source-mapping gate reviews before any
`silver.*` SQL exists.

**Decision**: add exactly two new OPTIONAL per-column keys inside each
`columns[]` entry -- `unit` and `currency` (FR-001) -- each defaulting to an
explicit not-yet-declared value (e.g. `null`) rather than silent absence, so
a reviewer can tell "declared N/A" from "field never filled in." No other
key in this file is touched (`decision`, `silver_type`, `missing_policy`,
`pii`, `derived_columns`, `gold_star` are all out of scope per the spec's
Boundary section).

### P4 -- Static rule shape + registration: `src/retail/rules/g6.py`, `src/retail/registry.py`, `src/retail/core.py`

Every static rule is a pure function `RuleContext -> Iterable[Finding]`,
registered exactly once via `@register("ID", "description")`
(`src/retail/core.py`: `Rule = Callable[[RuleContext], Iterable[Finding]]`).
`g6.py` is the minimal sibling: scans committed text via `ctx.tracked_files`,
applies a regex, emits `Finding(rule_id=..., severity=Severity.ERROR, ...)`
per violation, skips `tests/` fixtures via `is_test_path()`.

**Decision**: HR11 follows the identical shape -- pure function over
`ctx.tracked_files`, one `@register("HR11", "...")`, `Finding` objects with
`Severity.ERROR` for every violation (fail CLOSED per Principle I; no
`Severity.WARNING` tier for a genuine unit/currency clash -- this mirrors
092's Clarification C1 posture for HR6, not the WARNING-tier S5/S6/S7 ADR-
default-advisory family, which is a different rule kind this feature must
not mirror by surface analogy).

### P5 -- Cross-file join precedent (metric contract <-> another committed artifact): `src/retail/rules/assumptions.py` (AL1) + `specs/092-rls-access-readiness` (HR6)

AL1 already establishes the pattern of reading every committed
`mappings/<table>/metrics/*.yaml` contract via a path regex
(`^mappings/[^/]+/metrics/[^/]+\.ya?ml$`), lazily importing `yaml`, and
emitting an ERROR finding naming the contract's file path when a structural
contradiction is found -- entirely self-contained, no second file read. HR6
(092) is the closer precedent for a CROSS-FILE join: it resolves a role
contract's `filter.gold_table`/`filter.column` against a SECOND committed
artifact (`warehouse/migrations/*.sql`) scoped to the SAME table, and records
a blocking finding (never assumes a match) when the second artifact is
missing, unreadable, or the referenced name is not found in it.

**Decision**: HR11 is the same cross-file-join shape as HR6, but the second
artifact is `source-map.yaml` (not migration SQL): for each committed
`mappings/<table>/metrics/*.yaml` contract whose `binds_to.columns[]` lists
two or more entries, HR11 reads that SAME table's
`mappings/<table>/source-map.yaml`, resolves each bound column, and compares
declared `unit`/`currency` values. The table identity for the join is the
`<table>` path segment shared by both files under `mappings/<table>/`
(matches how AL1's own path regex already isolates `<table>`, and how HR6's
plan derives the same table-scoped join). When the referenced
`source-map.yaml` is missing/unreadable, or a bound column cannot be
resolved within its `columns[]` list, HR11 records a blocking finding naming
the missing path or unresolved column (FR-010) -- it never assumes a
matching unit/currency when the source of truth cannot be read (mirrors
HR6's "unresolvable column" treatment cited directly in the spec's Edge
Cases).

### P6 -- Bound-column-to-source-column join key (resolves spec Clarification Q4)

`binds_to.columns[]` on a metric contract names GOLD-facing column names
(e.g. `total_spent`, per the filled instance
`mappings/retail_store_sales/metrics/AvgTransactionValue.yaml`).
`source-map.yaml`'s `columns[]` list is keyed by `source_name` with a
`rename_to` SILVER alias (e.g. `mappings/retail_store_sales/source-map.yaml`:
`source_name: "total_spent"`, `rename_to: "total_spent"`) -- it carries no
gold name field at all. In the current worked example the silver rename and
the eventual gold column name happen to read identically, but the ONLY
committed, literal field connecting the two artifacts is `rename_to`.

**Decision** (already fixed by the spec's own Clarification Q4, restated
here as the mechanism this plan relies on): HR11 resolves a
`binds_to.columns[]` entry against `source-map.yaml` `columns[].rename_to`.
A `binds_to.columns[]` entry that instead names a `derived_columns` entry
(which carries no `unit`/`currency` field) is never resolvable by this join
and therefore falls under the FR-010 cannot-be-resolved blocking path -- it
is NOT silently treated as unit/currency-agnostic. This is the most literal
join key already present in both committed artifacts; no new cross-reference
field is introduced by this feature to make the join easier.

### P7 -- YAML parsing mechanism: `src/retail/rules/readiness_status.py` (RS1), `src/retail/rules/assumptions.py` (AL1)

The static core documents itself as stdlib-only IN SPIRIT (Principle VIII),
but `pyyaml>=6` is an already-approved RUNTIME dependency
(`pyproject.toml`). Every YAML-reading rule follows a lazy, FUNCTION-SCOPE
`import yaml` (never module-scope) -- e.g. AL1: `import yaml  # lazy: keep
the retail-check core stdlib-only at module scope (B1/B3)`.

**Decision**: HR11 reads both `mappings/<table>/metrics/*.yaml` and
`mappings/<table>/source-map.yaml` the same way -- `read_text(encoding=
"utf-8-sig")`, lazy `import yaml` inside the rule function body, `safe_load`,
catching `OSError`/`UnicodeDecodeError`/`yaml.YAMLError` as findings (never
an uncaught crash of the whole gate). No new dependency is added; the import
stays function-scope so `never_execute.py` (B1)'s module-scope guard is
unaffected.

### P8 -- Stage-5 gate wiring: `docs/readiness/semantic-model-ready.md`, `retail-semantic-check` skill

`docs/readiness/semantic-model-ready.md`'s "Required checks" table already
lists `D1-D11, C1, R1, G6` as the `retail check` scope for this stage.
`retail-semantic-check` is READ-ONLY and invoke-and-interpret only: it runs
the full `retail check` rule set and inherits any new `Severity.ERROR`
finding's effect on the process exit code without special-casing individual
rule ids.

**Decision**: HR11 needs NO new code in `retail-semantic-check` -- wiring it
in is a documentation-only edit (FR-018): add HR11 to the "Required checks"
and "Blocking reasons" tables in `semantic-model-ready.md`, the same way G6
(and, prospectively, HR6) are/would be listed there. This is "one more input
to the existing verdict," never a replacement of F010's own measure-to-
contract trace logic (spec Boundary section, FR-012).

### P9 -- Additivity-legality rule is a DISTINCT, non-overlapping neighbour: `src/retail/rules/additivity_consistency.py`

This module (registered id `AD1` in code, despite an internal docstring
still calling it "H1" -- a pre-existing naming drift in that file, not
something this feature touches or corrects) checks whether a metric's
additivity CLASSIFICATION is legally composed with its derivation lineage
(e.g. a semi-additive component summed by a plain-sum parent is illegal).
That is a question about whether an AGGREGATION KIND is legal for a metric's
declared additivity class.

**Decision**: HR11 asks a different question entirely -- for a metric that
IS being summed, do the RAW INPUTS to that sum share the same declared unit
and currency in the first place. Per the spec's own Boundary section, a
metric can pass AD1's additivity-legality check and still fail HR11 (a
well-formed sum of two genuinely additive-but-differently-united columns),
and vice versa. HR11's implementation must not read AD1's classification or
`blocking_reasons`, and must not attempt to fold the two checks into one
rule module.

## Input-source confirmation

| Input this feature reads | Source | Already exists? |
|---|---|---|
| Metric-contract shape to extend | `templates/metric-contract.yaml` | Yes (F009, shipped) |
| Source-map shape to extend | `templates/source-map.yaml` | Yes (shipped, Phase 2.1-2.5) |
| Filled metric contract worked instance | `mappings/retail_store_sales/metrics/AvgTransactionValue.yaml` | Yes (shipped, citable, never copied into the generic template per Principle VII) |
| Filled source-map worked instance | `mappings/retail_store_sales/source-map.yaml` | Yes (shipped) |
| Rule registration mechanism | `src/retail/registry.py`, `src/retail/core.py` | Yes (shipped) |
| Sibling static-rule pattern (minimal) | `src/retail/rules/g6.py` | Yes (shipped) |
| Sibling cross-file-join pattern | `specs/092-rls-access-readiness/` (HR6, reserved id, in-flight, not yet shipped code) | Spec/plan precedent only; HR11 does not depend on HR6 landing first (spec Boundary section) |
| Same-table, single-file contract-only precedent | `src/retail/rules/assumptions.py` (AL1) | Yes (shipped) |
| YAML-parsing pattern | `src/retail/rules/readiness_status.py` (RS1), `assumptions.py` (AL1) | Yes (shipped) |
| Stage-5 gate doc to update | `docs/readiness/semantic-model-ready.md` | Yes (shipped; this feature edits it) |
| Distinct neighbouring rule (do not merge with) | `src/retail/rules/additivity_consistency.py` (registered `AD1`) | Yes (shipped) |
| Severity enum | `src/retail/core.py` (`Severity.ERROR/WARNING/INFO`) | Yes (shipped) |
| Per-table co-location convention | ADR 0003 (`docs/decisions/0003-*.md`); `mappings/<table>/metrics/`, `mappings/<table>/source-map.yaml` | Yes (shipped) |

No input this feature needs is missing or requires new infrastructure. Every
artifact this plan proposes to touch already has a load-bearing sibling in
the repo to model itself on.

## Deferred capabilities NOT assumed (Principle VIII / Scope Guard)

This feature's design MUST NOT assume, simulate, or partially build any of
the following. Restated explicitly so `plan.md`, `data-model.md`, and
`quickstart.md` cannot silently smuggle one in:

- **No F016 (Power BI execution adapter).** HR11 never opens a PBIP file,
  never connects to Power BI Desktop or the Power BI service, never
  evaluates a measure or a DAX expression. F016 does not exist in this repo
  and this feature does not assume any interface from it (FR-009).
- **No live database connection.** HR11 reads only already-committed
  `source-map.yaml` and metric-contract YAML text via `ctx.tracked_files` /
  `Path.read_text()`. It never connects to Postgres (or any engine) to
  sample real column values and check them against the declared unit/
  currency -- that live check is explicitly out of scope and deferred to a
  future `retail validate` extension, not this feature (FR-019). `retail
  validate`'s existing live surface is untouched.
- **No currency-conversion rate, no unit-conversion factor, anywhere.** Not
  in either template, not in the HR11 rule's own source, not in a finding
  message, not as a lookup table, not as a suggestion (Scope Guard, FR-008,
  SC-003). Currency and unit-conversion RATES/FACTORS are an owner ruling
  (Principle V) entirely out of scope for this feature.
- **No unit-name normalization, alias table, or fuzzy matching.** HR11
  performs an exact, case-sensitive string comparison only (FR-007); `"kg"`
  vs `"Kg"` vs `"kilogram"` are distinct values whose mismatch is reported,
  never reconciled.
- **No new readiness stage, no new `retail check` subcommand.** The seven
  stages are unchanged. HR11 is one more `retail check` finding folded into
  the EXISTING Semantic Model Ready (Stage 5) gate (FR-012), exactly as G6
  and (prospectively) HR6 already are/would be.
- **No `templates/metric-contract.yaml` `currency` key.** Per the Scope
  Guard and the collision-avoidance allocation, only `unit` is added to that
  file; no key named `uom`, `unit_of_measure`, `measure_unit`,
  `binds_to.currency`, or `metric.currency` is introduced anywhere by this
  feature (FR-002, SC-006 by extension).
- **No answer to FR-013's detection-scope question.** Whether HR11 scopes
  itself to metrics whose optional `definition.aggregation` is `sum`
  specifically, or to any metric whose `binds_to.columns[]` lists two or
  more columns regardless of `definition` presence, is an OPEN design-
  detection-scope decision explicitly routed to implementation planning by
  the spec (FR-013, Edge Cases). Neither candidate is constitution-safe to
  adopt unilaterally here: scoping ONLY to `definition.aggregation: sum`
  would silently exempt the common no-`definition` case (reopening the exact
  gap this feature exists to close, contradicting SC-001/SC-002); scoping to
  ANY 2+-column bind would false-positive on a legitimate ratio metric
  (a `[numerator_col, denominator_col]` pair that is not a sum), which User
  Story 2 rules out as untrustworthy. This research/plan/data-model/
  quickstart set MUST NOT show either candidate as the settled answer.
- **No answer to FR-014's undeclared-value enforcement posture.** Whether an
  undeclared (null/absent) `unit`/`currency` on one side of a multi-column
  bind is itself a blocking finding, a warning, or a silent no-op is an OPEN
  Principle-V/VI governance-policy call (owner ruling required) about
  retroactive enforcement strictness against mappings that predate this
  feature. This design does not narrow, default, or pre-empt that ruling.
- **No resolution of Q2a's internal-consistency flag.** User Story 3
  Acceptance Scenario 3 (a currency-declared-vs-undeclared pairing "is not
  treated as matches anything") pre-supposes the STRICT answer to FR-014,
  while FR-006 as literally written only fires on two-or-more DIFFERENT,
  NON-NULL currency values (a null-vs-non-null pairing is outside that
  literal condition). This feature does not pick a side: until FR-014 is
  ruled, FR-006's literal non-null-vs-non-null comparison governs, and User
  Story 3 Acceptance Scenario 3 is recorded only as a CANDIDATE answer for
  the FR-014 owner to ratify or reject.
- **No metric-vs-bound-column unit cross-check.** Per Q3 (spec
  Clarifications, adopted default), the metric contract's own top-level
  `unit` field is DOCUMENTARY only; HR11 never compares it against the
  bound columns' declared units. Adding such a cross-check would be a
  second, un-scoped comparison the gap description and Scope Guard do not
  request (Principle VI: narrow, do not widen).
- **No numeric confidence/health/maturity score or completeness count
  anywhere** (hard rule #9): not in either template field, not in an HR11
  finding message, not in any doc this feature edits (FR-015).

## Open questions carried into plan.md

- **FR-013** (HR11's "is this a sum" detection scope when
  `definition.aggregation` is absent) -- carried forward unresolved into
  `plan.md`'s Constitution Check (Principle V / VI) and Project Structure
  notes on `hr11.py`. Not answered by this research or by any later Phase-0/1
  artifact in this feature; routed to implementation planning per the spec's
  own instruction.
- **FR-014** (undeclared unit/currency enforcement posture: block / warn /
  silent no-op) -- carried forward unresolved, Principle V/VI owner ruling
  required. Not narrowed by this research.
- **Q2a** (internal-consistency flag: User Story 3 Acceptance Scenario 3 vs
  FR-006's literal non-null-vs-non-null wording) -- carried forward
  unresolved; not reconciled by picking a side in any Phase-0/1 artifact.
