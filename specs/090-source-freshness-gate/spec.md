# Feature Specification: Source Freshness / Staleness Declaration and Static Presence Check

**Feature Branch**: `090-source-freshness-gate`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #9. Source freshness / staleness readiness -- add a
Source-Ready freshness declaration (expected arrival cadence + max staleness) and a check
that surfaces stale/late/missing source as a blocker."

## Overview

The `bi-sql-knowledge` skill names a recurring production symptom, **PB-SQL-09**: "gates
pass but data is stale / a segment is missing" (`skills/bi-sql-knowledge/INDEX.md`,
`skills/bi-sql-knowledge/knowledge/sql-diagnostics-playbook.md`). Its stated cause is "no
freshness/completeness gate; completeness checked off the fact, not a spine." Today, the
Seshat BI readiness spine has NO such gate anywhere: a table can hold `source_ready: pass`
through `gold_ready: pass` and beyond while the underlying source landed weeks late or
never landed at all for the latest period, because the spine only measures SHAPE (row/col
counts, missingness, candidate-key uniqueness, per `docs/readiness/source-ready.md`) and
never records what arrival cadence was EXPECTED or how STALE is tolerable. This feature
closes only the FRESHNESS half of PB-SQL-09: it adds a place for a human to DECLARE the
expected arrival cadence and the maximum tolerable staleness for a source, and a static
rule that fails closed when that declaration is missing or malformed on a table that
carries one.

This feature is deliberately narrow in two ways. First (Principle VIII, static-first /
live-deferred), it adds the DECLARATION and a STATIC presence/well-formedness check now;
it does NOT add a live arrival-time check (comparing a declared cadence against the actual
`MAX(<date column>)` of a live table is a `retail validate` -- style live surface, and is
explicitly deferred). Second, PB-SQL-09 as written bundles staleness together with "a
segment is missing" (missing-segment / date-spine completeness); this feature addresses
ARRIVAL-CADENCE STALENESS ONLY -- missing-segment / completeness detection is explicitly
out of scope (see Assumptions).

This feature reuses the existing `source-map.yaml` meta block (the same artifact that
already carries `grain`, `primary_key`, `reviewed_by`) as the home for the new
declaration, under the reserved key `meta.freshness` (`expected_cadence` +
`max_staleness`), and reserves the static-rule id **HR4** for the presence/well-formedness
check. It touches no other key in `source-map.yaml` and no other readiness artifact's
schema.

## Boundary against neighbouring shipped work (read first)

This feature sits between three existing surfaces and must not restate or absorb any of
them.

- **`docs/readiness/source-drift.md` (roadmap F014, design-only, "Later" tier)** is the
  nearest-sounding neighbour and the one most likely to be confused with this feature.
  Source-drift re-certifies a source's **SHAPE and SEMANTICS** over time -- columns added
  or removed, types changed, missingness/cardinality shifted, grain/PK no longer unique,
  the returns rule or a semantic pair broken, PII surface changed. It answers "does the
  source still look the way it did when we profiled it?" This feature answers a completely
  orthogonal question: "did the data ARRIVE ON TIME?" A source can be perfectly un-drifted
  (identical shape) and still be stale (three weeks late), and a source can arrive exactly
  on schedule and still be drifted (a column disappeared). Source-drift is also
  design-only today (docs/templates, no runtime code, no registered rule); this feature
  DOES add one registered static rule (HR4). This feature does not edit `source-drift.md`,
  its taxonomy, or its (future) `source-drift-report.md` template, and does not fold
  freshness into the nine-class drift taxonomy.
- **`retail validate` / the live-validation surface (spec 082, Postgres live-validation
  suite)** is where an eventual LIVE freshness check belongs -- actually querying
  `MAX(<date column>)` against a live connection and comparing it to the declared
  `max_staleness`. This feature is the STATIC HALF ONLY: it declares the SLA and checks
  that the declaration exists and is well-formed. It adds no live check, opens no DB
  connection, and does not extend `retail validate`'s finding set. The live comparison is
  named here as the deferred next step and is explicitly out of scope.
- **HR1 / spec 087 (conformed-dimension readiness)** is the immediately preceding
  reserved static-rule id in the same `HR*` id family. HR1 reads `gold_star.dimensions[]`
  across multiple `source-map.yaml` files to check cross-star dimension conformance; it is
  a different subject (gold-star shape), reads a different key, and does not touch `meta`.
  This feature (HR4) reads one table's own `meta.freshness` block; the two rules do not
  read each other's keys and do not share a manifest.
- **The source-mapping gate itself (Principle IV, spec 001; `templates/source-map.yaml`)**
  is the artifact this feature extends. `meta.freshness` is a SIBLING key to the existing
  `meta.grain` / `meta.primary_key` / `meta.reviewed_by` keys, added under the existing
  `meta:` block per the collision-avoidance allocation; this feature adds no new top-level
  key and no new file to the mapping-gate's five-artifact set.
- **`docs/readiness/source-ready.md` (Stage 1)** states plainly that Stage 1 "has no
  `retail check` / `retail validate` gate. The gate is a review," and that
  `source-map.yaml` and its siblings "belong to Stage 2 (Mapping Ready)... and MUST NOT be
  authored" at Stage 1. HR4 does NOT become a Stage-1 gate and does NOT require
  `source-map.yaml` to exist before Stage 1 passes -- the Stage-1 review is unchanged. HR4
  is a static rule that fires once a `source-map.yaml` exists (Stage 2 onward) and reads
  its `meta.freshness` block; it SERVES the Source-Ready freshness concern the same way
  `meta.grain`/`meta.primary_key` already live in that Stage-2 artifact while informing the
  Stage-1-adjacent readiness picture. This spec does not change `source-ready.md`'s
  required-artifact table or its four statuses.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A data owner declares an expected cadence and max staleness (Priority: P1)

A data owner who has just cleared the source-mapping gate for a table wants to record how
often the source is expected to land and how stale it may be before the data is considered
unusable for reporting. They add a `freshness` block under the `meta:` key of the table's
`source-map.yaml`, stating an `expected_cadence` (how often new data is expected) and a
`max_staleness` (the longest tolerable gap before the source counts as stale), in the same
document that already records the table's grain and primary key.

**Why this priority**: Without a place to declare the SLA, there is nothing for any check
-- static or eventual live -- to check against; this is the foundation the rest of the
feature depends on.

**Independent Test**: Add a `meta.freshness` block with both sub-keys filled to a table's
`source-map.yaml` and confirm the file remains valid against the mapping-gate schema, with
no other key touched.

**Acceptance Scenarios**:

1. **Given** a `source-map.yaml` with a `meta:` block that already carries `grain` and
   `primary_key`, **When** a data owner adds `meta.freshness.expected_cadence` and
   `meta.freshness.max_staleness`, **Then** the file continues to satisfy every existing
   mapping-gate requirement (grain, PK, reviewed_by) unchanged.
2. **Given** the same table, **When** the freshness block is added, **Then** no key other
   than `meta.freshness` (and its two named children) is introduced or modified.

---

### User Story 2 - A missing or malformed freshness declaration is surfaced as a blocker (Priority: P1)

An analyst runs `retail check` against a table whose `source-map.yaml` exists (Stage 2
cleared) but carries no `meta.freshness` block, or one with an empty/missing
`expected_cadence` or `max_staleness`. The static rule HR4 fails closed, naming the table
and the missing/malformed field, so the gap cannot silently pass through to Silver/Gold/
Publish the way PB-SQL-09 describes.

**Why this priority**: This is the enforcement half of the feature (Principle I,
fail-closed, not advisory) -- without it, the declaration in User Story 1 is optional prose
that nothing checks, and the gate provides no real protection against the symptom it is
named for.

**Independent Test**: Run `retail check` against an in-scope `source-map.yaml` (per
FR-014's eventual ruling) with the `freshness` block entirely absent; confirm HR4 emits an
ERROR-severity Finding naming the table and the missing block, and that removing/blanking
either sub-key on an otherwise-present block also triggers HR4.

**Acceptance Scenarios**:

1. **Given** a `source-map.yaml` that is IN SCOPE for the freshness requirement (FR-014)
   and carries no `meta.freshness` key at all, **When** `retail check` runs, **Then** HR4
   emits a fail-closed ERROR Finding naming the table and stating the block is missing.
2. **Given** an in-scope `source-map.yaml` with `meta.freshness.expected_cadence` present
   but `meta.freshness.max_staleness` blank or absent, **When** `retail check` runs,
   **Then** HR4 emits a fail-closed ERROR Finding naming the specific missing sub-key.
3. **Given** a `source-map.yaml` with both `meta.freshness` sub-keys present and non-empty,
   **When** `retail check` runs, **Then** HR4 emits no Finding for that table (true
   regardless of how FR-014 is eventually ruled).
4. **Given** `retail check` runs across the full repo, **When** it completes, **Then** HR4
   is static-only: it opens no database connection, reads no live Power BI/PBIP surface,
   and invokes no deferred execution adapter (F016) or spec-only runtime (Principle VIII).

---

### User Story 3 - The live arrival-time comparison is marked pending, never fabricated (Priority: P2)

An analyst or the agent wants to know whether the ACTUAL latest arrival of a live table is
within the declared `max_staleness`. Because that comparison requires a live database
connection (Principle VIII, deferred), the feature does not compute it; instead, any
surface that would report this live state must mark it `[PENDING LIVE FRESHNESS CHECK]`
plus a `warning`-equivalent status rather than asserting a fabricated pass or fail.

**Why this priority**: This is the scope fence that keeps the feature from silently
growing into the deferred live surface; it is P2 because the P1 declaration + static check
already deliver the closable half of the gap, and the deferred marker is a documentation
discipline rather than new mechanism.

**Independent Test**: Confirm no artifact in this feature computes or asserts an actual
arrival timestamp, elapsed staleness duration, or live pass/fail verdict; any reference to
the live comparison is written as a named, explicitly deferred next step.

**Acceptance Scenarios**:

1. **Given** the live database boundary is unavailable (no DSN / no `db` extra), **When**
   any surface reports on a table's actual freshness, **Then** it records
   `[PENDING LIVE FRESHNESS CHECK]` and a non-`pass` status, never a fabricated `pass`.
2. **Given** this feature's deliverables (the schema addition + HR4), **When** they are
   inspected, **Then** none of them queries `MAX(<date column>)`, opens a database
   connection, or otherwise computes an actual staleness duration.

---

### Edge Cases

- What happens when a table's `source-map.yaml` does not exist yet (Stage 1, pre-mapping)?
  HR4 MUST NOT fire -- the rule reads a Stage-2 artifact; a table with no
  `source-map.yaml` yet is out of HR4's scope entirely, exactly as `source-ready.md`
  already forbids authoring `source-map.yaml` before Stage 1 clears.
- What happens to an EXISTING, already-approved `source-map.yaml` that predates this
  feature and carries no `meta.freshness` block (for example the committed
  `retail_store_sales` worked example)? OPEN -- see FR-014 and Clarifications 2026-07-04
  (Q-FR014-SCOPE) -- whether HR4 applies retroactively to every existing source-map, or only
  to newly-authored/newly-touched ones, is a genuine open question this spec does not
  resolve; only a RECORDED PENDING DEFAULT (going-forward-only, existing maps grandfathered)
  is on file, awaiting a named-human ruling.
- What happens for a genuinely one-time or static reference source (a table that is loaded
  once and never refreshed, e.g. a fixed lookup or a one-off historical extract) where
  "expected arrival cadence" may not apply? A recognized `one_time`/`static` cadence token
  is reserved in the well-formedness vocabulary (Clarifications 2026-07-04, C2) so such a
  value would pass HR4 if used -- but WHETHER a one-time source gets that opt-out, a full
  HR4 exemption, or neither remains OPEN under the same Q-FR014-SCOPE ruling; this spec does
  not decide applicability, only reserves the token.
- What happens when `meta.freshness` is present but one of its values is an
  unrecognized/unparseable form (e.g. a cadence string the rule cannot classify)? HR4 MUST
  treat this the same as a missing sub-key -- a fail-closed ERROR naming the table and the
  malformed value -- never a silent pass and never a best-guess interpretation.
- What happens when someone tries to have HR4 assert that a table's data IS currently
  stale, or emit a rolled-up "freshness score"? Out of scope by design (hard rule #9 and
  Principle VIII) -- HR4 checks only that a human-declared SLA is present and well-formed;
  it never measures or scores actual staleness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The source-mapping-gate schema (`templates/source-map.yaml` and each filled
  `mappings/<table>/source-map.yaml`) MUST gain exactly one new key, `meta.freshness`,
  nested under the existing `meta:` block alongside `grain`, `primary_key`, `reviewed_by`.
  No other top-level or `meta`-level key is added, renamed, or removed.
- **FR-002**: `meta.freshness` MUST carry exactly two named sub-keys: `expected_cadence`
  (how often new data is expected to land, human-declared) and `max_staleness` (the longest
  tolerable gap before the source is considered stale, human-declared). Neither value is
  computed or inferred by automation; both are a business-SLA judgment the agent MUST NOT
  fabricate on a human's behalf (no fabricated freshness). "Well-formed" means: present,
  non-empty after trimming whitespace, and matching a recognized declared-value form (see
  Clarifications 2026-07-04 for the shape; the exact token grammar is deferred to plan,
  matching the FR-002 spirit of a small, generic, non-domain-specific vocabulary).
- **FR-003**: The feature MUST add exactly ONE `@register`-ed static `retail check` rule
  with reserved id **HR4**, reading only committed files (each table's
  `mappings/<table>/source-map.yaml`); it MUST NOT connect to a database, read a live Power
  BI/PBIP surface, or invoke any deferred execution adapter (F016) or spec-only runtime
  (Principle VIII).
- **FR-004**: For any table that is IN SCOPE for the freshness requirement (the exact
  scope -- which tables must carry `meta.freshness` -- is the open governance ruling in
  FR-014 and is NOT decided here), HR4 MUST fail closed (ERROR-severity Finding, Principle
  I) when that table's `source-map.yaml` exists and either: (a) carries no
  `meta.freshness` block at all, or (b) carries a `meta.freshness` block missing, blank, or
  unparseable on either `expected_cadence` or `max_staleness`. The Finding MUST name the
  table and the specific missing/malformed field(s). This spec does NOT assert that any
  specific already-committed `source-map.yaml` (including the `retail_store_sales` worked
  example) is in scope or in violation -- that determination follows only from FR-014's
  ruling, never from this requirement alone.
- **FR-005**: HR4 MUST NOT fire on a table that has no `source-map.yaml` yet (Stage 1,
  pre-mapping) -- this preserves `source-ready.md`'s rule that `source-map.yaml` and its
  siblings are Stage-2 artifacts and are not required, and MUST NOT be authored, before
  Stage 1 clears.
- **FR-006**: HR4 MUST NOT compute, query, or assert an ACTUAL arrival time, an actual
  elapsed staleness duration, or a live pass/fail verdict against the declared SLA. That
  live comparison is explicitly DEFERRED (Principle VIII); any surface that would someday
  report it MUST mark it `[PENDING LIVE FRESHNESS CHECK]` with a non-`pass` status until a
  live boundary exists, never a fabricated result. This feature itself introduces no
  live-reporting surface to carry that marker (see Clarifications 2026-07-04); the marker
  convention is recorded here as the seam's contract for whichever future surface (most
  likely `retail validate`, spec 082) implements the live comparison.
- **FR-007**: HR4 MUST NOT emit any numeric confidence / health / maturity / freshness
  score and MUST NOT emit a completeness count or "N of M" tally (hard rule #9). Its output
  is a categorical Finding (present-and-well-formed vs. missing/malformed) only. A
  human-declared `max_staleness` value or (once the live surface exists) a measured
  "last arrival N days ago" figure is not itself a forbidden score -- it is a declared
  input or a measured fact, not a rolled-up rating -- but no single combined "freshness
  score" may ever be emitted, mirroring the equivalent rule already adopted for
  source-drift (`docs/readiness/source-drift.md`, "No fake confidence").
- **FR-008**: HR4 MUST NOT re-decide, auto-fill, or default a table's `expected_cadence` or
  `max_staleness` value; it MUST NOT self-grant any readiness pass; and it MUST NOT write to
  `source-map.yaml`, `readiness-status.yaml`, or `approvals[]` (Principle V). It reads and
  reports only.
- **FR-009**: The feature MUST NOT edit, extend, or fold into `docs/readiness/source-drift.md`,
  its nine-class drift taxonomy, or any `source-drift-report.md` artifact. Arrival-cadence
  staleness (this feature) and shape/semantic drift (source-drift, F014) remain two
  independent signals.
- **FR-010**: The feature MUST NOT add or modify any missing-segment / date-spine
  completeness check. PB-SQL-09 as documented bundles staleness with missing-segment
  detection; this feature addresses arrival-cadence staleness only. Missing-segment /
  completeness detection is explicitly out of scope.
- **FR-011**: The feature and its rule MUST stay generic (Principle VII): no C086 /
  `retail_store_sales` cadence value, column name, or table name may be inlined into the
  schema template or the rule logic; the worked example may appear only as a cited filled
  instance. HR4 MUST resolve a generic `mappings/<table>/source-map.yaml` path. HR4 MUST
  evaluate only FILLED per-table maps (`mappings/<table>/source-map.yaml`); it MUST NOT fire
  on `templates/source-map.yaml` itself, whose `meta.freshness` sub-keys are placeholder
  schema documentation, not a real declaration (see Clarifications 2026-07-04).
- **FR-012**: The rule MUST be wired across every meta-gate surface required for a newly
  registered static rule (so `@register` fires and the wiring-meta-gate / rule-count
  reconciliation stay green with `HR4` present in the registered rule set), per the
  existing wiring convention used by HR1 and the SF1/AP1 rule-adding shape.
- **FR-013**: All authored artifacts MUST be ASCII, UTF-8 without BOM (`--` and `->`, no
  glyphs), and MUST use short repo-relative paths (Windows 260-char budget) (Principle IX).
- **FR-014**: OPEN (owner ruling required -- Principle V; see Clarifications 2026-07-04). Is
  a `meta.freshness` declaration MANDATORY on every existing and future `source-map.yaml`
  (making HR4 fire retroactively on already-approved tables such as the committed
  `retail_store_sales` worked example, which has no such block today and cannot supply one
  without a human providing a real SLA), or does HR4 apply only to newly-authored/
  newly-touched maps going forward, with pre-existing maps grandfathered or explicitly
  exempted? Relatedly, does a genuinely one-time/static reference source get an explicit
  opt-out value (e.g. a recognized `one_time`/`static` cadence) or a full HR4 exemption?
  This is a governance-shape / rollout decision the agent MUST NOT settle alone (Principle V)
  because it determines whether landing this feature immediately turns an already-`pass`
  table's readiness picture red, and because the SLA values themselves are a business
  judgment only a data owner can supply -- the agent cannot invent one to make an existing
  table comply.

### Key Entities

- **Freshness declaration (`meta.freshness`)**: the human-authored SLA statement living
  under a table's `source-map.yaml` `meta:` block -- `expected_cadence` (how often new data
  should arrive) + `max_staleness` (the longest tolerable gap before the source counts as
  stale). Declared, never computed, by this feature.
- **HR4 (static presence/well-formedness rule)**: the one new `@register`-ed `retail
  check` rule this feature adds. Reads a table's `source-map.yaml` only; fails closed
  (ERROR) when `meta.freshness` is missing or malformed on a table that has a
  `source-map.yaml`; never fires pre-Stage-2; never touches a live boundary.
- **Deferred live freshness check**: the NOT-YET-BUILT comparison of a declared
  `max_staleness` against an actual, live-measured arrival time. Named here as an explicit
  future seam (Principle VIII); not implemented, not simulated, not fabricated by this
  feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every `source-map.yaml` that carries a `meta.freshness` block with both
  `expected_cadence` and `max_staleness` present and non-empty produces ZERO HR4 Findings.
- **SC-002**: Every IN-SCOPE `source-map.yaml` (per FR-014's eventual ruling) that exists
  but omits `meta.freshness`, or leaves either sub-key blank/malformed, produces exactly
  one fail-closed HR4 ERROR Finding naming the table and the specific missing/malformed
  field (mutation-verified: removing/blanking the block or a sub-key flips a
  previously-clean, in-scope table to a Finding). This criterion does not itself determine
  which tables are in scope.
- **SC-003**: A table with no `source-map.yaml` yet produces ZERO HR4 Findings (no
  premature firing ahead of Stage 2).
- **SC-004**: HR4 opens zero database connections and reads zero live Power BI/PBIP
  surfaces in its own execution (verified by test/review: it touches only committed
  `source-map.yaml` text).
- **SC-005**: Zero generated Findings, and zero generic artifacts (schema template, rule
  logic), contain a numeric confidence/health/maturity/freshness score or an "N of M" /
  completeness tally.
- **SC-006**: The wiring + rule-count lockstep stays green after HR4 lands (the
  wiring-meta-gate and rule-count-claim tests pass; the registered rule set contains
  `HR4`).
- **SC-007**: Zero generic artifacts (the rule logic, the schema template) contain a
  worked-example (C086/`retail_store_sales`) cadence value, column name, or table name;
  any C086 reference appears only as a cited filled instance.

## Assumptions

- `templates/source-map.yaml` and the per-table `mappings/<table>/source-map.yaml` files
  are the authoritative mapping-gate artifact set (Principle IV, spec 001); this feature
  extends their existing `meta:` block rather than introducing a new artifact or file.
- The collision-avoidance allocation for this feature reserves exactly one new key,
  `meta.freshness` (with children `expected_cadence` + `max_staleness`), and exactly one
  new static-rule id, `HR4`; no other key or id is touched.
- Missing-segment / date-spine completeness detection (the other half of PB-SQL-09) is OUT
  OF SCOPE for this feature and is left to a future spec.
- The live comparison of a declared `max_staleness` against an actual, live-measured
  arrival time is OUT OF SCOPE for this feature (Principle VIII, deferred); it is left as a
  named future seam, most naturally alongside the `retail validate` live-check surface
  (spec 082) rather than as a new command.
- `docs/readiness/source-drift.md` (F014) remains the authoritative surface for
  shape/semantic drift; this feature does not alter its taxonomy, statuses, or forbidden
  actions, and treats arrival-cadence staleness as a distinct signal from drift.
- Whether `meta.freshness` is mandatory on every table (retroactively and going forward) or
  only on newly-authored maps, and how one-time/static sources are handled, is left OPEN per
  FR-014 (see Clarifications 2026-07-04, Q-FR014-SCOPE); this spec does not adopt the
  recorded pending default as a ruling -- it remains a decision only a named human can make,
  because settling it would otherwise flip already-`pass` tables red or require the agent to
  fabricate a business SLA on a human's behalf.
- This feature adds no new readiness stage, no new required artifact file, and no change to
  the four-status model (`not_started | blocked | warning | pass`); HR4 is a static `retail
  check` Finding, not a fifth status or an eighth stage.

## Clarifications

<!-- Principle-V carve-out questions are recorded under their own subsection for a human
     ruling; the workflow is forbidden to answer these. Non-Principle-V ambiguities resolved
     with reasonable constitution-safe defaults (Principle VI) are recorded under the dated
     session subsection. -->

### Session 2026-07-04

Non-Principle-V ambiguities resolved against the constitution, the HR1/spec-087 precedent
(same `HR*` id family, same two-subsection Clarifications shape), and the existing
`source-map.yaml` template + filled `retail_store_sales` instance. All are reversible
docs/plan choices that confirm a shape the spec already implies.

- **C1 (what counts as "well-formed" -- FR-002/FR-004) -- Default adopted.** Q: FR-004(b)
  requires HR4 to fail closed on an "unparseable" `expected_cadence` or `max_staleness`
  value (the Edge Cases example is "a cadence string the rule cannot classify"), but the
  spec never defines what a PARSEABLE value looks like -- so HR4 cannot be presence-only and
  needs some recognized form. A: well-formed means present, non-empty after trimming
  whitespace, and matching a recognized declared-value FORM -- `max_staleness` as a
  magnitude-plus-unit duration (e.g. a number and a calendar-unit word) and
  `expected_cadence` as a value drawn from a small, generic cadence vocabulary (e.g. daily /
  weekly / monthly / quarterly plus an explicit `one_time`/`static` sentinel, see C2). The
  exact token grammar (which unit words, exact regex/enum) is DEFERRED TO PLAN, mirroring
  the 087/C2 precedent ("exact field names are confirmable at plan/template time") -- plan
  MUST keep the grammar small, generic, and permissive enough to avoid false-positive
  ERRORs on legitimate phrasings, and MUST NOT inline any C086/`retail_store_sales` cadence
  value into the grammar itself (FR-011). Reasoning: a fail-closed rule (Principle I) cannot
  rest on an undefined "parseable" test, but the specific grammar is an implementation
  mechanic, not a business-SLA or governance judgment, so it is safe to default the SHAPE
  and defer the exact tokens. Reversible: easy. Touches: FR-002, FR-004.
- **C2 (one-time/static cadence token -- Edge Cases/FR-014) -- Default adopted (vocabulary
  only; applicability stays OPEN).** Q: If a one-time/static opt-out cadence is eventually
  ruled in by FR-014, what should the token look like? A: reserve the literal value
  `one_time` (with `static` accepted as a synonym) as a RECOGNIZED, well-formed
  `expected_cadence` value in the grammar from C1, paired with a `max_staleness` of `n/a` or
  equivalent explicit non-duration sentinel -- so the grammar does not have to be re-touched
  later if FR-014 rules the opt-out in. Reasoning: reserving the token now is a cheap,
  reversible, non-domain-specific vocabulary choice (Principle VII); it does NOT decide
  whether any table may actually USE it, or whether HR4 exempts one-time sources at all --
  that remains the open FR-014 governance ruling below. Reversible: easy. Touches: FR-002,
  FR-014 (vocabulary only, not the ruling).
- **C3 (template vs filled maps -- FR-001/FR-011) -- Default adopted.** Q: FR-001 adds
  `meta.freshness` to `templates/source-map.yaml` as schema documentation -- does HR4 also
  evaluate the template file itself, which by definition carries no real per-table SLA? A:
  HR4 evaluates only FILLED per-table maps (`mappings/<table>/source-map.yaml`); it MUST NOT
  fire on `templates/source-map.yaml`, whose freshness sub-keys are placeholder
  documentation, not a declaration. Reasoning: matches the existing HR1 and mapping-gate
  convention that the template is the schema, not an instance subject to instance-level
  rules; firing on the template would be a permanent, unfixable false Finding. Reversible:
  easy. Touches: FR-001, FR-011.
- **C4 (does this feature add a live-reporting surface -- FR-006) -- Default adopted.** Q:
  FR-006 requires any surface that reports live freshness to mark it `[PENDING LIVE
  FRESHNESS CHECK]` -- does THIS feature add such a surface now? A: No. This feature adds no
  live-reporting surface of its own; the marker convention is recorded as the CONTRACT a
  future surface (most likely `retail validate`, spec 082, per the Assumptions) must follow
  when it is eventually built. HR4 itself never emits the marker because HR4 never reports
  on live state at all (Principle VIII, static-only). Reasoning: keeps the feature's own
  surface area at exactly the declaration + HR4 named in the scope guard, with no
  incidental live-adjacent surface sneaking in. Reversible: easy. Touches: FR-006.

### Principle-V carve-out (OPEN -- owner ruling required; the workflow is forbidden to answer)

- **Q-FR014-SCOPE (FR-014) -- OPEN owner ruling.** Q: Is a `meta.freshness` declaration
  MANDATORY on every existing and future `source-map.yaml` (making HR4 fire retroactively on
  already-approved tables such as the committed `retail_store_sales` worked example, which
  has no such block today and cannot supply one without a human providing a real SLA), or
  does HR4 apply only to newly-authored/newly-touched maps going forward, with pre-existing
  maps grandfathered or explicitly exempted? Relatedly, does a genuinely one-time/static
  reference source get the `one_time`/`static` opt-out value reserved in C2, a full HR4
  exemption, or neither? This is a governance-shape / rollout decision the agent MUST NOT
  settle alone (Principle V): resolving it either forces the agent to fabricate a business
  SLA value on an existing table's behalf (forbidden, hard rule #9 / FR-002), or flips an
  already-`pass` table's readiness picture red without a named human choosing that outcome.
  RECORDED PENDING DEFAULT the owner may ratify: GOING-FORWARD ONLY -- HR4 applies to any
  `source-map.yaml` newly authored or materially re-touched (a reviewed_by / grain / PK
  change) after this feature lands; pre-existing approved maps (including
  `retail_store_sales`) are grandfathered and do not retroactively flip to a Finding until
  their next material edit or an owner explicitly opts them in; a genuinely one-time/static
  source uses the reserved `one_time`/`static` cadence token from C2 rather than a blanket
  rule exemption, so it stays auditable and HR4 still checks it is PRESENT and well-formed.
  Until the owner rules, HR4's in-scope set is UNDECIDED and this spec asserts no verdict on
  any specific already-committed map (per FR-004's own caveat). Touches: FR-004, FR-014,
  Edge Cases (retroactive-map and one-time-source bullets), SC-002.
