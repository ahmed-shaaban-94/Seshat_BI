# Feature Specification: Reload / Idempotency Readiness (Anti-Double-Count)

**Feature Branch**: `093-reload-idempotency-readiness`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #16. Reload / idempotency readiness (anti-double-count) --
a Gold-Ready check that a load is idempotent: full drop-and-rebuild trivially passes; an
incremental/append load must declare its dedup/overwrite key."

## Overview

Every gold migration shipped so far (`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`)
uses full drop-and-rebuild: `DROP TABLE IF EXISTS` for fact and dims, then a clean
`INSERT ... SELECT` inside one transaction. Drop-and-rebuild is trivially idempotent --
rerunning it twice yields the same result, because nothing is appended. That pattern is the
only one this repo has ever authored, so nothing has ever tested whether the readiness system
notices its absence.

The gap: as a table outgrows a full nightly rebuild (volume, source-system load, or a
downstream consumer that cannot tolerate a rebuild window), an author will reach for an
incremental or append-style load -- and nothing in `retail check` or the Gold Ready gate
currently distinguishes a safe incremental load (one with a declared dedup/overwrite key)
from an unsafe one (a bare `INSERT` with no key, where a re-run of the same batch silently
doubles every row it touches). This is exactly the failure mode the `bi-bigdata-knowledge`
skill documents at BD-CN-057/058 ("a job that appends its output... each rerun adds another
copy") and BD-PB-005 ("reruns create duplicates"), and it is the SQL-layer lens named in this
gap: PB-SQL-10/14, "a reload doubled the data."

This feature closes that gap with a NEW static Gold-Ready check (reserved rule id **HR7**):
a load's migration must DECLARE its reload strategy. Full drop-and-rebuild declares nothing
extra and passes by default (Principle VI, defaults-then-deviations). Any load that is NOT a
full drop-and-rebuild is a DEVIATION and MUST declare a dedup/overwrite key; if it does not,
HR7 fails CLOSED. HR7 is a static, structural check -- it reads the declaration and the
migration's own SQL shape; it does NOT run the load, does NOT connect to a database, and does
NOT prove real data is duplicate-free (that is the live surface `retail validate` already owns
at Gold Ready via RC2/RC16 penny-exact reconciliation, and it stays deferred).

## Boundary against neighbouring shipped work (read first)

This feature is a genuinely NEW static check at the Gold Ready stage. Three shipped/adjacent
surfaces must stay distinct:

- **087 conformed-dimension-readiness (rule id HR1)**: HR1 is also a Gold-Ready, HR-series,
  static check, but its concern is CROSS-STAR dimension shape agreement (grain/key/type of a
  same-named dimension declared `conformed` across two or more Gold-Ready stars), reading each
  table's `source-map.yaml`. HR7's concern is SINGLE-TABLE reload safety (does this table's
  own load declare how it stays idempotent), reading the migration header / `load-policy.md`.
  Different concern, different id, different artifact; HR7 does not read or write anything
  HR1 owns, and HR1 does not read or write anything HR7 owns.
- **Gold Ready's existing live checks (RC2 / RC16, `retail validate`)**: RC2 proves grain/PK
  uniqueness and RC16 proves penny-exact silver<->gold reconciliation with zero orphan FKs --
  both AFTER data has actually been loaded, by executing a live, read-only query. That is the
  proof a reload did NOT, in fact, double the data. HR7 is the STATIC, pre-execution
  declaration that a reload is DESIGNED not to: it never runs a load and never queries a live
  table (Principle VIII). The two are complementary, not redundant -- HR7 can pass while RC2/
  RC16 are still PENDING (no DSN), and RC2/RC16 remain the only live proof of actual
  correctness.
- **`source-map.yaml` (the mapping-gate schema; also read by HR1)**: the dedup/overwrite key
  this feature requires is deliberately NOT a new `source-map.yaml` key. `source-map.yaml`
  already has four features reading/extending it (mapping gate, HR1's conformance reads,
  reconciliation, and others); adding a fifth concern there risks a 4-way collision on a single
  shared file. HR7's declaration lives instead in the migration SQL header comment or a NEW
  `warehouse/load-policy.md` (collision-avoidance allocation, non-negotiable per this feature's
  scope guard).
- **Gold Ready's existing static checks (S6, S7)**: S6 checks the `-1` unknown member exists
  per entity dim; S7 checks the date dimension is built via contiguous `generate_series`. Both
  are shape checks on a single already-written migration's structure. HR7 adds a THIRD,
  independent structural check to the same stage -- reload-strategy declaration -- and does not
  alter S6 or S7's checks or their Findings.

This feature adds no new readiness stage; it adds one static rule (HR7) at the existing Gold
Ready stage and, optionally, one new declaration artifact (`warehouse/load-policy.md`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A drop-and-rebuild migration passes with no extra declaration (Priority: P1)

An author writes a gold migration the same way every migration in this repo has been written
so far: `DROP TABLE IF EXISTS` for the fact and every dim, then a clean `INSERT ... SELECT`
inside one transaction, with no partial/append logic. They run `retail check`. HR7 recognizes
this as full drop-and-rebuild -- the default, trivially idempotent pattern -- and requires no
extra declaration; it passes with zero Findings.

**Why this priority**: This is the load pattern every existing migration already uses. If HR7
broke this default, it would fail closed on 100% of today's committed migrations -- an
immediate regression the feature must never cause (Principle VI: the default path stays free).

**Independent Test**: Run `retail check` against the committed
`0004_create_gold_retail_store_sales_star.sql` (or an equivalent full drop-and-rebuild
migration) with HR7 registered; HR7 emits no Finding for that migration.

**Acceptance Scenarios**:

1. **Given** a gold migration that drops every fact/dim table with `DROP TABLE IF EXISTS` and
   recreates them via `INSERT ... SELECT` with no append/upsert logic, **When** `retail check`
   runs, **Then** HR7 records no Finding for that migration.
2. **Given** the same migration has no reload-strategy declaration in its header comment and
   no entry in `warehouse/load-policy.md`, **When** `retail check` runs, **Then** HR7 does not
   require one, because full drop-and-rebuild needs no declaration to be judged idempotent.
3. **Given** HR7 is registered, **When** `retail check` runs against the full committed
   migration set, **Then** the rule-count/wiring lockstep stays green (no existing migration
   newly fails).

---

### User Story 2 - An incremental/append load with no declared key fails closed (Priority: P1)

An author, working on a table too large for a nightly full rebuild, writes a gold migration
that appends new rows into an existing gold table (no `DROP TABLE`, an `INSERT` with no
`ON CONFLICT` / merge-on-key logic, no `TRUNCATE` of a partition). They do not declare a
dedup/overwrite key anywhere. HR7 recognizes this migration as a DEVIATION from full
drop-and-rebuild and, finding no declared key, fails CLOSED with an ERROR Finding naming the
migration and the missing declaration -- exactly the anti-double-count this feature exists to
enforce (PB-SQL-10/14).

**Why this priority**: This is the entire point of the feature. Without this story, HR7 would
be a no-op that only ever confirms the one pattern already in use, and the actual gap (an
undeclared incremental load silently doubling data on rerun) would remain open.

**Independent Test**: Author (in a scratch/test fixture, never executed) a gold migration
that appends without a `DROP TABLE`/merge/partition-overwrite and with no reload-strategy
declaration; run `retail check`; HR7 emits an ERROR Finding naming that migration file and
stating the required declaration is absent.

**Acceptance Scenarios**:

1. **Given** a gold migration with a bare `INSERT INTO gold.<table>` and no `DROP TABLE`, no
   `ON CONFLICT`/merge clause, and no `TRUNCATE`, **When** `retail check` runs and no
   dedup/overwrite key is declared for that migration (neither in its header comment nor in
   `warehouse/load-policy.md`), **Then** HR7 emits an ERROR Finding naming the migration file
   and stating that a reload-strategy declaration is required and missing.
2. **Given** the same migration, **When** the author adds a declaration (header comment or
   `warehouse/load-policy.md` entry) naming the dedup/overwrite key the load uses, **Then**
   HR7's ERROR clears -- HR7 checks that a key is DECLARED, not that the load has been proven
   correct at runtime.
3. **Given** a migration uses `ON CONFLICT ... DO UPDATE` (upsert-on-key) or overwrites a
   named partition/date range before inserting, **When** `retail check` runs, **Then** HR7
   recognizes the merge/overwrite key already present in the SQL as satisfying the declaration
   requirement without requiring a redundant separate declaration for the same key.

---

### User Story 3 - HR7 stays static-only; live proof remains deferred (Priority: P2)

An analyst asks whether a table's incremental load is "actually" idempotent -- would running
it twice on live data really produce the same row count and totals. HR7's `pass` answers a
narrower question (a dedup/overwrite key is declared for this load) and explicitly does not
answer the live question; the live proof stays where Gold Ready already puts it (RC2 grain
uniqueness, RC16 penny-exact reconciliation via `retail validate`), and remains PENDING/
blocked-deferred when no DSN or `db` extra is available, exactly like the rest of Gold Ready.

**Why this priority**: Without this boundary, a reviewer could mistake a static HR7 `pass` for
proof the live data is duplicate-free, silently reintroducing the "static check alone is proof
of correctness" anti-pattern gold-ready.md already forbids. This is a guardrail on the
feature's own claims, not new end-user-visible capability, hence P2.

**Independent Test**: Inspect HR7's Finding/pass message and the Gold Ready doc update; confirm
neither states or implies that a static HR7 pass proves live idempotency, and confirm the
live reload-doubling proof still routes through RC2/RC16 exactly as before this feature.

**Acceptance Scenarios**:

1. **Given** HR7 passes (a dedup/overwrite key is declared) but no DSN/`db` extra is
   configured, **When** the Gold Ready status is composed, **Then** the stage's overall
   live-dependent checks (RC2/RC16) still report blocked-deferred, and HR7's pass is not used
   to substitute for or mask that deferred state.
2. **Given** HR7's documentation and Finding text, **When** read by a reviewer, **Then** no
   sentence claims or implies that a declared key or an HR7 pass proves an actual rerun would
   be duplicate-free.
3. **Given** HR7 is a new rule, **When** it is added, **Then** it introduces no new live check,
   no new DB connection, and no new dependency on the `db` extra (Principle VIII).

---

### Edge Cases

- What happens when a migration mixes patterns -- drops and recreates SOME tables (e.g. dims)
  but appends into another (e.g. the fact, for volume reasons)? HR7 MUST classify per-table
  within the migration: any table whose load is not full drop-and-rebuild is a deviation for
  that table and needs its own declared key; a mixed migration cannot inherit a pass from its
  drop-and-rebuild tables.
- What happens when the declaration exists but names a key that is not actually a column in
  the target table (a typo, a stale declaration after a schema change)? See FR-008 --
  RESOLVED conservatively to a mechanical Finding (a bare structural readability check), not
  a semantic proof of correctness; see FR-008 for the exact resolved boundary.
- What happens when `warehouse/load-policy.md` does not exist at all and no migration in the
  repo has ever needed a declaration (the current, all-drop-and-rebuild state)? HR7 MUST NOT
  require the file to exist; its absence is fine as long as every deviation is otherwise
  declared (e.g. entirely via header comments), and MUST NOT be treated as an ERROR when there
  are zero deviations to declare.
- What happens when a table's move from full-rebuild to incremental is itself a business
  decision (a capacity/ops tradeoff, possibly needing sign-off)? See the OPEN Principle-V
  question under Clarifications; HR7 itself never grants or requires that approval -- it only
  checks that a key is declared.
- What happens when the same table has more than one gold migration over time (a later
  migration changes the load strategy)? HR7 MUST evaluate the CURRENT (latest, per the
  contiguous numbering convention) migration for that table; superseded migrations are not
  re-evaluated as if still authoritative.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `retail check` MUST register a new static rule with reserved id **HR7** that
  evaluates every committed gold migration under `warehouse/migrations/` for reload-strategy
  declaration. RESOLVED (mechanics, non-Principle-V; see Clarifications): `warehouse/migrations/`
  interleaves silver and gold migrations by contiguous number (e.g. 0003 silver, 0004 gold, 0005
  silver) with no filename-level gold/silver marker; HR7 MUST identify a migration as "gold" by
  a static, structural signal already present in every committed migration -- the SQL text
  targets the `gold` schema (e.g. `CREATE SCHEMA IF NOT EXISTS gold`, or a DDL/DML statement
  qualifying a `gold.<table>` target) -- never by filename pattern-matching alone, since
  filenames are free-text and not a declared contract.
- **FR-002**: HR7 MUST classify a migration's (or, per Edge Cases, a migration's per-table)
  load pattern as either FULL DROP-AND-REBUILD (default; a `DROP TABLE IF EXISTS` for the
  target followed by a clean `INSERT ... SELECT` with no partial/append logic) or a DEVIATION
  (any other shape: a bare append `INSERT` with no prior drop/truncate of the target, an
  `ON CONFLICT`/merge-on-key upsert, or a partition/date-range overwrite). RESOLVED (mechanics,
  non-Principle-V; see Clarifications): a WHOLE-TABLE, unqualified `TRUNCATE gold.<table>` or
  unqualified `DELETE FROM gold.<table>` (no `WHERE` clause, no partition/date-range boundary)
  immediately followed by a clean `INSERT ... SELECT` is idempotency-equivalent to
  drop-and-rebuild -- rerunning it twice still yields the same result, because the prior
  contents are always fully cleared first -- so HR7 MUST classify it as FULL DROP-AND-REBUILD
  (no declaration required), the same as `DROP TABLE IF EXISTS`. Only a PARTIAL clear (a
  `WHERE` clause, or a named partition/date-range boundary per FR-006) is a DEVIATION requiring
  a declared key.
- **FR-003**: A migration (or per-table load) classified as full drop-and-rebuild MUST require
  no additional declaration and MUST pass HR7 with no Finding (Principle VI: the default
  incurs no new burden).
- **FR-004**: A migration (or per-table load) classified as a DEVIATION MUST declare its
  dedup/overwrite key in one of exactly two places: (a) the migration SQL file's own header
  comment block, or (b) a new `warehouse/load-policy.md` entry naming the migration file and
  the table. HR7 MUST NOT accept a declaration anywhere else, and MUST NOT accept or require a
  `source-map.yaml` key for this purpose (collision-avoidance allocation, non-negotiable).
  RESOLVED (mechanics, non-Principle-V; see Clarifications): today's committed header comments
  are free prose (e.g. "Idempotent: DROP+CREATE in one transaction"), which is not
  mechanically greppable for FR-008's structural check. A declaration (in either allowed
  location) MUST use a single-line, greppable marker of the form `reload-strategy: <key1>[,
  <key2>...]` (comma-separated column identifiers for a composite key); free prose elsewhere in
  the same comment block or file does not itself satisfy FR-004. A `warehouse/load-policy.md`
  entry MUST additionally name the migration filename and the target table, so HR7 can bind the
  entry to the specific migration/table it declares for; the minimal entry shape is: migration
  filename, table name, and the same `reload-strategy: <key(s)>` marker.
- **FR-005**: When a DEVIATION migration/table has no declaration in either allowed location,
  HR7 MUST fail CLOSED with an ERROR Finding naming the migration file (and table, if the
  deviation is per-table) and stating that a reload-strategy declaration is required and
  absent (Principle I: fails closed, never merely advises).
- **FR-006**: When a DEVIATION migration/table already expresses its key directly in SQL (an
  `ON CONFLICT (<key>) DO UPDATE` clause, or an explicit partition/date-range `DELETE`/
  `TRUNCATE` before insert naming the boundary), HR7 MUST recognize that in-SQL key as
  satisfying FR-004 without requiring a redundant separate declaration for the same key.
- **FR-007**: HR7 MUST be static-only (Principle VIII): it MUST read only committed files (the
  migration SQL text, and `warehouse/load-policy.md` if present) and MUST NOT connect to a
  database, execute or simulate a load, or query live row counts.
- **FR-008**: HR7's declaration check MUST be a bare structural/readability check -- confirming
  a key is named and that the named key(s) are syntactically plausible column identifiers --
  and MUST NOT attempt to semantically verify the declared key against a live schema or prove
  the load is actually duplicate-free at runtime. RESOLVED (mechanics, non-Principle-V):
  distinguishing "a key is declared" from "the key is correct" is a scope-narrowing boundary
  that keeps HR7 inside Principle VIII (static-only); live proof of correctness (a declared
  key that turns out to be wrong, or a rerun that turns out non-idempotent) is out of scope
  for HR7 and remains the live surface's territory (RC2/RC16 today; a future live idempotency
  re-run check, if ever built, is a separate feature).
- **FR-009**: HR7 MUST NOT prove, assert, or imply that a passing declaration means a live
  rerun would in fact produce identical data; it proves only that a declaration exists and is
  structurally well-formed. The live reload-doubling proof continues to route through the
  existing Gold Ready live checks (RC2 grain/PK uniqueness, RC16 penny-exact reconciliation),
  which HR7 does not alter, duplicate, or substitute for.
- **FR-010**: HR7 MUST NOT execute a reload, MUST NOT open a database connection, and MUST NOT
  depend on the `db` extra or a DSN being configured (Principle VIII; the scope guard's "MUST
  NOT execute a reload" is non-negotiable).
- **FR-011**: HR7 MUST NOT re-decide, re-derive, or cross-check a table's grain or primary key
  (that is a Mapping Ready / source-map.yaml decision, and is also the concern HR1 already
  reads for a different purpose). HR7 checks only that SOME dedup/overwrite key is declared
  for a deviation load; it does not judge whether that key is the "correct" grain key.
- **FR-012**: HR7 MUST NOT emit any numeric confidence/health/maturity/idempotency score and
  MUST NOT emit a completeness count or "N of M" tally (hard rule #9). HR7's outcome is
  expressed only as: no Finding (pass-eligible) or an ERROR Finding naming the missing
  declaration.
- **FR-013**: Whether a table's transition from full-rebuild to an incremental/append load
  strategy requires a NAMED-HUMAN approval (an operational/capacity decision, potentially
  parallel to the four approvals[] stage gates) is a genuine Principle-V judgment call this
  spec does NOT answer. [NEEDS CLARIFICATION: does moving a table to an incremental/append
  load strategy require a recorded named-human approval before HR7's pass can be treated as
  part of a Gold Ready `pass`, or does a clean HR7 run stand as the sign-off the same way
  Gold Ready's existing S6/S7/RC2/RC16 checks already do (per gold-ready.md, "Required owner /
  approval: None -- mechanical")? A conservative PENDING default is recorded in Clarifications
  below; HR7 itself never self-grants this and emits Findings only until an owner rules.]
- **FR-014**: `warehouse/load-policy.md`, if created, MUST be a NEW file distinct from
  `source-map.yaml`, and MUST NOT be positioned as a mapping-gate artifact -- it is read only
  by HR7 (and by an author authoring a declaration), never by the mapping gate, HR1, or the
  live validate surface.
- **FR-015**: This feature MUST stay generic (Principle VII): HR7's rule logic and any doc
  update MUST NOT bake in a specific table name, column name, or the C086/retail_store_sales
  worked example; the worked example may be cited only as an illustrative, non-authoritative
  example of a compliant drop-and-rebuild migration.
- **FR-016**: All authored artifacts (rule doc updates, `warehouse/load-policy.md` template if
  created) MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no glyphs), and MUST use short
  repo-relative paths (Windows 260-char budget) (Principle IX).
- **FR-017**: HR7 MUST be additive: it MUST NOT alter the behavior, Finding text, or pass/fail
  outcome of any existing rule (S6, S7, HR1, or any RC-series live check), and adding HR7 MUST
  NOT change the rule-count/wiring lockstep for any rule other than registering HR7 itself.

### Key Entities

- **Reload strategy classification**: the per-migration (or per-table) determination of
  whether a gold load is FULL DROP-AND-REBUILD (default, no declaration needed) or a DEVIATION
  (append/upsert/partition-overwrite, declaration required). Derived by HR7 from the
  migration's own SQL shape; never a stored/authored field.
- **Reload-strategy declaration**: the dedup/overwrite key an author records for a DEVIATION
  load, living in either the migration's header comment or a `warehouse/load-policy.md` entry
  -- never a `source-map.yaml` key (collision-avoidance allocation).
- **`warehouse/load-policy.md`**: a NEW, optional file (created only when at least one
  deviation load needs a declaration outside its own header comment) that HR7 reads; not a
  mapping-gate artifact, not read by HR1 or the mapping gate.
- **HR7 Finding**: a `Finding(HR7, ERROR, message, locator)` naming the migration file (and
  table, if per-table) missing a required declaration; the rule's only other outcome is no
  Finding (pass-eligible). No numeric field exists on this entity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of currently committed gold migrations (full drop-and-rebuild) pass HR7
  with zero Findings, with no change to any existing migration file required.
- **SC-002**: A migration authored with a bare append `INSERT` and no declared key produces
  exactly one HR7 ERROR Finding naming that migration file; adding a valid declaration (header
  comment, `load-policy.md` entry, or an in-SQL `ON CONFLICT`/partition-overwrite clause)
  clears that Finding with no other change to the migration's data logic.
- **SC-003**: 0 HR7 Findings or pass messages contain a numeric confidence/health/idempotency
  score or a completeness/"N of M" count (hard rule #9).
- **SC-004**: 0 HR7 evaluations open a database connection, execute a reload, or depend on a
  DSN or the `db` extra being present (Principle VIII: fully static).
- **SC-005**: The rule-count/wiring lockstep test suite stays green after HR7 is registered
  (the registered rule set contains `HR7`; no other rule's count or Finding output changes).
- **SC-006**: 0 HR7-related artifacts (rule doc, `load-policy.md` template) contain a
  domain-specific table/column name outside an explicitly labeled illustrative example
  (Principle VII).

## Assumptions

- `warehouse/migrations/*.sql` is the authoritative, committed source HR7 reads; the migration
  numbering/idempotency conventions already documented (gold-ready.md, "Numbering is
  contiguous and idempotent") are unchanged by this feature.
- Full drop-and-rebuild (`DROP TABLE IF EXISTS` + clean `INSERT ... SELECT`, no partial/append
  logic) is the only load pattern in the repo today (per `0004_create_gold_retail_store_sales_star.sql`
  and `0005_create_silver_demo_sample_orders.sql`); HR7's default-passes-free behavior (FR-003)
  is verifiable against the full current migration set at zero cost.
- HR7 is a Gold Ready stage check, alongside the existing S6/S7 static checks and the RC2/RC16
  live checks; it does not introduce a new readiness stage and does not change Gold Ready's
  four-status model (`not_started | blocked | warning | pass`).
- `warehouse/load-policy.md` is optional: it need not exist while zero migrations are
  deviations, and an author may satisfy FR-004 entirely via header comments without ever
  creating the file.
- The live proof that a reload did not, in fact, double the data remains RC2 (grain/PK
  uniqueness) and RC16 (penny-exact silver<->gold reconciliation) under `retail validate`;
  this feature adds no new live check and does not change the deferred/blocked-deferred
  behavior when no DSN or `db` extra is configured.
- The specific numeric HR7 rule id is fixed at **HR7** per this gap's collision-avoidance
  allocation (to avoid clashing with 087's HR1 and 18 other parallel features); no other
  feature is expected to claim HR7.

## Clarifications

<!-- Principle-V carve-out questions recorded here for a human ruling; the workflow is
     forbidden to answer these. Session answers to non-Principle-V ambiguities are added
     under a dated session heading by /speckit-clarify. -->

### Principle-V rulings (OPEN -- requires a named-human ruling)

- **Q-APPROVAL-SEAM (FR-013) -- OPEN.** Does a table's transition from full-rebuild to an
  incremental/append load strategy require a recorded named-human approval (an operational/
  capacity decision) before its Gold Ready status can rely on a passing HR7, or is a clean HR7
  run purely mechanical -- the same way Gold Ready's existing S6/S7 (static) and RC2/RC16
  (live) checks require no `approvals[]` entry today (gold-ready.md: "Required owner /
  approval: None -- mechanical")? RECORDED PENDING DEFAULT an owner may ratify: MECHANICAL,
  by direct precedent with the rest of Gold Ready and with 087/HR1's own pending default (a
  clean structural check is its own sign-off) -- no approval seam is invented until an owner
  rules one in. Until ruled, HR7 emits Findings only and never contributes to a self-granted
  Gold Ready `pass`; this spec does not resolve the question and the agent MUST NOT decide it
  unilaterally at build time.

### Session 2026-07-04 (/speckit-clarify) -- mechanics defaults (non-Principle-V)

- **Q-GOLD-IDENTIFY (FR-001) -- RESOLVED, default adopted.** `warehouse/migrations/` interleaves
  silver and gold migrations by contiguous number (0003 silver, 0004 gold, 0005 silver) with no
  filename-level marker distinguishing them, so "every committed gold migration" was
  underspecified as a matching rule. Default adopted: HR7 identifies a migration as gold by a
  static SQL-shape signal already present in every committed migration -- the file's SQL text
  targets the `gold` schema (`CREATE SCHEMA IF NOT EXISTS gold`, or a DDL/DML statement
  qualifying `gold.<table>`) -- never by filename pattern-matching. Constitution check: stays
  inside Principle VIII (a structural read of committed SQL text, no live schema lookup) and
  Principle VII (no table/schema name is hardcoded beyond the literal `gold` schema shared by
  the whole medallion convention). Encoded in FR-001.
- **Q-DECL-SHAPE (FR-004/FR-008) -- RESOLVED, default adopted.** FR-004 named the two allowed
  declaration locations but not the declaration's shape, and today's committed header comments
  are free prose ("Idempotent: DROP+CREATE in one transaction"), which FR-008's structural
  check cannot mechanically parse for "a key is named." Default adopted: a declaration (in
  either allowed location) is a single-line, greppable marker of the form
  `reload-strategy: <key1>[, <key2>...]`; a `warehouse/load-policy.md` entry additionally names
  the migration filename and target table alongside that marker. Free prose elsewhere in the
  same comment block does not itself satisfy FR-004. Constitution check: keeps FR-008 a bare
  structural/readability check (Principle VIII), introduces no numeric field (hard rule #9),
  and does not touch `source-map.yaml` (collision-avoidance allocation). Encoded in FR-004.
- **Q-TRUNCATE-CLASS (FR-002) -- RESOLVED, default adopted.** FR-002's binary classification
  (`DROP TABLE IF EXISTS` -> full-rebuild; anything else -> deviation) left a gap: a whole-table,
  unqualified `TRUNCATE gold.<table>` or unqualified `DELETE FROM gold.<table>` (no `WHERE`, no
  partition/date-range boundary) immediately followed by a clean `INSERT ... SELECT` is neither
  literally `DROP TABLE` (so not FR-002's stated full-rebuild shape) nor a bare append with no
  prior clear (so not the stated deviation shape either), and is distinct from FR-006's
  partition/date-range `TRUNCATE`/`DELETE` (which DOES name a boundary and IS a deviation).
  Verified against the only committed gold migration
  (`0004_create_gold_retail_store_sales_star.sql`, `DROP TABLE IF EXISTS` + `CREATE TABLE` +
  `INSERT`) that this exact shape is not yet in use, so no existing migration is affected either
  way. Default adopted: HR7 classifies a whole-table (unqualified, no `WHERE`, no named
  partition/date-range) `TRUNCATE`/`DELETE FROM` immediately followed by a clean
  `INSERT ... SELECT` as FULL DROP-AND-REBUILD (idempotency-equivalent to `DROP TABLE` -- prior
  contents are always fully cleared first, so a rerun cannot double rows) -- no declaration
  required. Only a PARTIAL clear (a `WHERE` clause, or a named partition/date-range boundary, per
  FR-006) remains a DEVIATION requiring a declared key. Constitution check: stays a structural,
  static SQL-shape read (Principle VIII), adds no new declaration location or numeric field, and
  does not touch `source-map.yaml`. Encoded in FR-002.
