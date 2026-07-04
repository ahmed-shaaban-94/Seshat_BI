# Feature Specification: Date-Spine Completeness Static Gate

**Feature Branch**: `094-date-spine-completeness`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #17. Date-spine completeness readiness. Serves Stage 4
Gold Ready. Lens/justification: DAX time-intelligence + PB-SQL-07 (missing periods). A
Gold-Ready check that a fact's date dimension is contiguous and gap-free vs the fact's own
min/max (generate_series coverage), so time-intelligence measures don't silently break on
missing periods."

## Overview

Gold Ready (Stage 4) already carries two date-dimension checks, and both stop short of the
one gap this feature closes. `S7` (static, shipped) scans an `INSERT INTO ... dim_date`
statement and flags `SELECT DISTINCT` (gappy) versus `generate_series` (contiguous) --
but it only checks WHICH BUILDER was used; it never inspects the `generate_series` call's
own arguments. `V-RC15` (live, shipped) proves, against a real database, that every
distinct fact date exists in the date dimension -- but it is a LIVE check, unusable until
`retail validate` runs with a DSN and the `db` extra installed (Principle VIII deferred
mode), and unusable at plan/build time before data exists at all.

The gap sits between them: a migration can pass S7 (it genuinely calls `generate_series`,
so it is not flagged as gappy) while still being structurally incapable of covering the
fact's real span -- most concretely, a `generate_series(start, end, INTERVAL '1 month')`
call produces one row per MONTH, leaving every day inside that month absent from the
calendar. DAX time-intelligence measures (`TOTALYTD`, `SAMEPERIODLASTYEAR`,
`DATEADD`, and similar) require a calendar with no missing days in the marked date table's
grain; a month-stepped or otherwise non-daily-stepped "calendar" silently breaks them,
and today NOTHING in the static gate catches it -- S7 passes, and the break is invisible
until a live `retail validate` run (if one ever happens) or, worse, until a report in
production returns a silently wrong year-to-date or year-over-year number (PB-SQL-07: a
time-intelligence measure that quietly omits rows for missing periods).

This feature adds that missing static check as a NEW `retail check` rule, reserved id
**HR8**: it reads a gold-star migration's `generate_series(...)` call that builds
`dim_date` and verifies the STEP argument is `INTERVAL '1 day'` (the grain every
shipped date-dimension convention in this repo already presupposes), and, where the call's
bounds are literal dates, that the start bound is not after the end bound. Live,
row-level coverage against the fact's actual min/max transaction date remains
OUT OF SCOPE here (Principle VIII, live deferred) -- that is V-RC15's job, unchanged. Where
HR8 cannot prove real coverage from static text alone (the common case: literal bounds,
exactly like the shipped worked example), it does not claim coverage is proven; it records
that live coverage is PENDING (`retail validate` / V-RC15), never a fabricated pass. HR8
reads only the already-committed migration SQL; it adds no new source-map key and no new
declaration file (the collision-avoidance allocation for this feature is the reserved rule
id only -- no shared-schema addition).

## Boundary against neighbouring shipped work (read first)

This feature is a genuine NEW static check for a gap neither shipped date check closes, not
a restatement of either. Three shipped neighbours must stay distinct:

- **`S7` contiguous date dim** (`src/retail/rules/sql.py`, `s7_contiguous_date_dim`) is a
  STATEMENT-SHAPE check: for an `INSERT INTO ... dim_date` statement, it flags `SELECT
  DISTINCT` (gappy) and passes anything using `generate_series` (contiguous), full stop. It
  never reads `generate_series`'s own arguments -- a `generate_series(start, end, INTERVAL
  '1 month')` call satisfies S7 today even though it produces a gappy, non-daily calendar.
  HR8 does not re-implement or replace S7's DISTINCT-vs-`generate_series` check; it is the
  NEXT check that fires only once S7's precondition (a `generate_series` call exists) is
  already met, and inspects what S7 does not: the call's step (and, where literal, its
  bounds). HR8 does not edit `s7_contiguous_date_dim` and does not change S7's severity or
  message.
- **`V-RC15` date coverage** (`src/retail/validate.py`, `check_date_coverage`) is the LIVE,
  read-only check that every distinct fact date actually exists in the materialized date
  dimension, run against a real database at Gold Ready. It proves the DATA is complete. HR8
  proves the migration's declared STRUCTURE is even capable of being complete (daily step,
  sane literal bounds) -- a static, pre-data check that can run with no DSN and no `db`
  extra. HR8 does not connect to a database, does not read a live Power BI/PBIP surface, and
  does not invoke `retail validate` or duplicate its SQL; where HR8 cannot prove real
  coverage from static text alone, it defers to V-RC15 (records live coverage as PENDING)
  rather than asserting a pass V-RC15 alone can prove.
- **087 conformed-dimension-map / HR1** (`specs/087-conformed-dimension-readiness/spec.md`)
  is a MODEL-LEVEL, cross-star check (do two or more stars' shared dimensions agree on
  grain/key/type); its own dim_date edge-case note states plainly that HR1's date-dim
  conformance "reduces to grain ... + type agreement across stars, not a re-check of RC15's
  contiguity (that is Gold Ready's job per star)". HR8 IS that per-star contiguity check
  087 explicitly deferred to Gold Ready -- the two are complementary, not overlapping: HR1
  never inspects a `generate_series` call's step or bounds, and HR8 never compares two
  stars' dimensions to each other. HR8 fires per single migration file; it needs no second
  star to engage (unlike HR1's multi-fact trigger).

This feature adds exactly ONE new `retail check` rule (id **HR8**, reserved). Unlike a
Product Module (F024 shape, e.g. spec 063), this is a rule-adding feature in the S-series /
087-HR1 shape: one registered static rule wired across the meta-gate surfaces, plus its
fixtures. It adds NO new declaration file, NO new `source-map.yaml` key, and NO new
readiness stage -- HR8 is one more static check feeding the existing Gold Ready `retail
check` column (`docs/readiness/gold-ready.md`), exactly where S6/S7/S8 already live.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fail closed on a non-daily generate_series step (Priority: P1)

As the `retail check` gate, when a gold-star migration's `INSERT INTO ... dim_date`
statement calls `generate_series(start, end, STEP)` to build the date dimension and `STEP`
is anything other than `INTERVAL '1 day'` (illustratively `INTERVAL '1 month'` or
`INTERVAL '7 days'`), I emit a fail-closed ERROR naming the file, the line, and the
offending step -- because a non-daily step leaves every day between generated rows absent
from the calendar, and every shipped date-dimension convention in this repo (S7, V-RC15,
Gold Ready) already presupposes a daily grain.

**Why this priority**: This is the concrete, previously-invisible defect the feature exists
to catch -- a migration that satisfies S7 (it does call `generate_series`) yet is
structurally incapable of a gap-free calendar. Without this check, exactly this class of
bug reaches Power BI silently and breaks time-intelligence measures. This is the MVP; the
feature delivers nothing without it.

**Independent Test**: Given a fixture gold migration whose `dim_date` `INSERT` calls
`generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 month')`, running HR8
emits exactly one ERROR naming the file:line and `INTERVAL '1 month'`. Changing the step to
`INTERVAL '1 day'` clears the ERROR with the bounds otherwise unchanged.

**Acceptance Scenarios**:

1. **Given** a migration's `dim_date` `INSERT` uses
   `generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 month')`, **When**
   `retail check` runs, **Then** it emits one ERROR naming the file, the line, and the
   literal step text `INTERVAL '1 month'`.
2. **Given** the same migration with the step corrected to `INTERVAL '1 day'`, **When**
   `retail check` runs, **Then** HR8 emits no ERROR for that statement.
3. **Given** the shipped worked-example migration
   (`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`, step
   `INTERVAL '1 day'`), **When** `retail check` runs, **Then** HR8 emits no ERROR (the
   already-shipped tree must stay green).

---

### User Story 2 - Fail closed on literal bounds that are already inverted (Priority: P1)

As the gate, when a `generate_series` call builds `dim_date` with LITERAL date bounds
(both the start and end arguments are date literals, not a subquery or expression) and the
start bound is after the end bound, I emit a fail-closed ERROR naming the file, the line,
and both literal values -- because an inverted literal range is a structural authoring
defect (in PostgreSQL it silently produces zero rows), independent of any live data.

**Why this priority**: An inverted literal range is a PROVEN defect visible from the text
alone (no live data needed to know start > end is wrong); catching it here, before a
migration is ever run against a database, is strictly cheaper than discovering an empty
date dimension downstream. It is co-equal in priority with US1 as the other half of the
"structurally incapable of covering the fact" defect class this feature targets.

**Independent Test**: Given a fixture migration whose `dim_date` `INSERT` calls
`generate_series(DATE '2025-01-18', DATE '2022-01-01', INTERVAL '1 day')` (bounds
reversed), running HR8 emits exactly one ERROR naming both literal dates. Swapping the
bounds back to chronological order clears the ERROR.

**Acceptance Scenarios**:

1. **Given** literal bounds `DATE '2025-01-18'` (start) and `DATE '2022-01-01'` (end) with
   step `INTERVAL '1 day'`, **When** `retail check` runs, **Then** it emits one ERROR
   naming the file:line and both literal values in the order given.
2. **Given** the bounds corrected to chronological order, **When** `retail check` runs,
   **Then** HR8 emits no ERROR for that statement.
3. **Given** a `generate_series` call whose start or end argument is NOT a literal (for
   example `(SELECT min(transaction_date) FROM silver.orders)`), **When** `retail check`
   runs, **Then** HR8 does not attempt the bounds-order comparison for that argument (a
   non-literal bound is not statically comparable) -- see FR-006 and User Story 3.

---

### User Story 3 - Record live coverage as pending, never as a fabricated pass (Priority: P2)

As the gate, when a `dim_date` `generate_series` call passes both the step check (US1) and
the bounds-order check where applicable (US2), I record, alongside the clean static result,
that whether the calendar actually covers the fact's real min/max transaction date is a
LIVE property this static rule cannot prove -- and I never emit language implying full
date-spine coverage is proven. Live coverage remains `V-RC15`'s job, unchanged, run at Gold
Ready with a DSN and the `db` extra.

**Why this priority**: The no-fabrication discipline (hard rule #9; Principle VIII) is the
check's integrity guarantee -- a rule that let "step is daily and bounds are sane" read as
"the calendar is complete" would mislead a reader into skipping the live V-RC15 run this
feature explicitly does not replace. This is what keeps HR8 honest about its own limits,
but a working step/bounds check (US1/US2) is already the viable slice, so this is P2.

**Independent Test**: Run HR8 against the shipped worked-example migration (literal
bounds, daily step); confirm the result set contains zero ERROR/WARNING findings for that
statement and one INFO-level record stating live coverage against the fact is pending
`retail validate` (V-RC15) -- and confirm no finding or message anywhere asserts the
calendar "covers" or "is complete" as fact.

**Acceptance Scenarios**:

1. **Given** a `dim_date` build with literal bounds and a daily step, **When** `retail
   check` runs, **Then** HR8 emits an INFO-level record (not ERROR, not WARNING) stating
   that live date-coverage against the fact's real span is pending `retail validate`
   (V-RC15), and asserts no coverage fact.
2. **Given** the same build, **When** the INFO record's wording is inspected, **Then** it
   does not contain "covers", "complete", "gap-free", or any phrase asserting the fact's
   actual date range is proven spanned -- only that the STRUCTURE (step, bounds order) is
   sound and live coverage is unverified here.
3. **Given** a `dim_date` build whose bounds are fact-derived (a subquery reading
   `min()`/`max()` of the fact's own date column) rather than literal, **When** `retail
   check` runs, **Then** HR8 still emits the same pending-live INFO record (a fact-derived
   bound narrows the RISK of drift but does not make static-text coverage a proof; live
   V-RC15 is still the only proof of actual coverage).

---

### Edge Cases

- **No `dim_date` `INSERT` statement found in any migration** (a table has no gold star
  yet, or its date dimension has a non-standard name): HR8 is a no-op for that file -- no
  Finding, consistent with S7's own precondition (it only fires on a statement that
  targets a name starting with `dim_date`, per the existing S7 implementation this feature
  reuses for statement discovery).
- **A `generate_series` call inside a comment or a non-`INSERT` statement**: out of scope
  -- HR8, like S7, operates on comment-stripped, statement-scoped SQL tokens, and only
  inspects `generate_series` calls that appear inside an `INSERT INTO ... dim_date`
  statement's token span.
- **A `generate_series` call whose step argument is not a literal `INTERVAL` at all**
  (a parameter, a computed expression, or a step written as a bare number without
  `INTERVAL`): the step is not statically classifiable as daily -- treat as a fail-closed
  ERROR (Principle I: a fail-closed rule must not let an unclassifiable step pass by
  default) naming the file:line and the literal step text found, distinct in wording from
  the daily-step-violation message in US1 so a reader can tell "wrong step" from
  "unreadable step" apart.
- **A `generate_series` call with only one bound literal and the other an expression**
  (for example a literal start and a fact-derived `max()` end): the bounds-order check
  (US2) does not fire (one side is not comparable), but the pending-live INFO record (US3)
  still applies.
- **Multiple `dim_date` builds in the same migration file** (unusual, but not forbidden by
  any existing rule): HR8 evaluates each qualifying `INSERT` statement independently and
  may emit multiple findings in one file, each with its own file:line locator -- consistent
  with S7's own per-statement scoping.
- **This feature's rule fires on tables whose Gold Ready is otherwise not yet reached**
  (an early-authored migration draft): HR8, like S6/S7/S8, is a `retail check` static rule
  and runs on any committed SQL file regardless of that table's current readiness-status
  stage (Principle I: static rules are order-blind, per `silver-ready.md`'s own framing of
  S1-S7) -- it is not gated on the table already being at Stage 4.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST add exactly ONE `@register`ed static `retail check` rule
  with reserved id **HR8**, reading only committed migration SQL under
  `warehouse/migrations/`; it MUST NOT connect to a database, read a live Power BI/PBIP
  surface, or invoke `retail validate` / duplicate V-RC15's live query (Principle VIII).
- **FR-002**: HR8 MUST locate its subject statements the same way S7 does: an
  `INSERT INTO ... dim_date` statement (comment-stripped, statement-scoped tokens, matched
  on a target name starting with `dim_date`) that contains a `generate_series(...)` call.
  This statement-DISCOVERY step reuses S7's `tokenize_sql`-based token span (per
  Clarifications 2026-07-04, since `tokenize_sql` collapses string-literal contents and
  cannot itself supply the literal text FR-003/FR-005 classify). HR8 MUST NOT re-flag the
  DISTINCT-vs-`generate_series` builder choice itself (that remains S7's exclusive
  concern); HR8 only fires on a statement that already contains a `generate_series` call.
- **FR-003**: For each qualifying `generate_series(start, end, step)` call, HR8 MUST
  classify the `step` argument: if it is a literal `INTERVAL` value textually equal to
  `INTERVAL '1 day'` (whitespace-insensitive), the step passes; if it is a literal
  `INTERVAL` value of any other span, HR8 MUST emit a fail-closed ERROR naming the file,
  line, and the offending literal step text (US1). Reading the literal's actual text (the
  `'1 day'` / `'1 month'` contents) MUST use `strip_sql_comments`
  (`src/retail/sql.py`) or equivalent literal-preserving raw text over the statement span
  located per FR-002 -- NOT `tokenize_sql`, which collapses string-literal contents to an
  empty placeholder and cannot supply this text (Clarifications, 2026-07-04). A
  step-grain other than daily is a proven structural defect given every shipped
  date-dimension convention in this repo already presupposes a daily grain (Assumptions).
- **FR-004**: If the `step` argument is present but is not a literal `INTERVAL` expression
  HR8 can classify (a bare identifier, a computed expression, or a non-`INTERVAL` literal),
  HR8 MUST emit a fail-closed ERROR naming the file, line, and the literal text found, with
  wording distinct from the FR-003 daily-step-violation message (Edge Cases: "unclassifiable
  step" vs "wrong step"). A fail-closed rule (Principle I) MUST NOT let an unclassifiable
  step pass silently.
- **FR-005**: When BOTH the `start` and `end` arguments of a qualifying `generate_series`
  call are literal date values, HR8 MUST verify `start` is not chronologically after `end`;
  a reversed literal range MUST be a fail-closed ERROR naming the file, line, and both
  literal values in the order given (US2). A "literal date value" is recognized in EITHER
  of the two spellings already present in this repo's committed migrations (per
  Clarifications, 2026-07-04): a typed literal `DATE '2022-01-01'`, or a cast literal
  `'2022-01-01'::date` (case-insensitive on `DATE`/`date`). Reading the literal date text
  (e.g. `'2022-01-01'`) MUST use the same literal-preserving raw text as FR-003
  (`strip_sql_comments` or equivalent), not `tokenize_sql` (Clarifications, 2026-07-04). Any
  bound written in neither recognized spelling (a subquery, a function call, a parameter, or
  any other literal form not listed above) is treated as NON-literal for this check: the
  bounds-order comparison MUST NOT fire for that call (skip, not ERROR) -- a form HR8 does
  not recognize is not statically comparable and MUST NOT be treated as a violation by
  default (Edge Cases). This check MUST NOT fire when either bound is a non-literal
  expression (a subquery, a function call, a parameter) -- a non-literal bound is not
  statically comparable and MUST NOT be treated as a violation by default (Edge Cases).
- **FR-006**: HR8 MUST NOT attempt to prove, from static text alone, that the generated
  calendar's actual span covers the fact table's real minimum/maximum date. That is
  `V-RC15`'s live, read-only responsibility, unchanged by this feature (Principle VIII;
  Boundary section).
- **FR-007**: For every qualifying `generate_series` call that passes FR-003/FR-004 (and
  FR-005 where applicable), HR8 MUST emit exactly one `Severity.INFO` record, distinct from
  its ERROR findings, stating that live date-coverage against the fact's actual span is
  PENDING `retail validate` (V-RC15) and asserting no coverage fact. This record MUST NOT
  use language ("covers", "complete", "gap-free", or equivalent) that could be read as a
  coverage proof (US3; hard rule #9).
- **FR-008**: HR8 MUST NOT emit any numeric confidence / health / maturity / completeness
  score and MUST NOT emit a completeness count or "N of M" / "% covered" tally (hard rule
  #9). Output is categorical Findings only -- ERROR for a proven structural defect (FR-003,
  FR-004, FR-005), INFO for the pending-live marker (FR-007).
- **FR-009**: HR8 MUST NOT auto-fix, rewrite, or reformat any migration SQL; MUST NOT
  author or edit `warehouse/migrations/*.sql`; and MUST NOT self-grant, record, or move any
  readiness stage or the Gold Ready mechanical sign-off (SCOPE GUARD; Principle V). On a
  breach it STOPS at the finding and a human/agent-author must fix the migration.
- **FR-010**: HR8 MUST NOT add any new key to `source-map.yaml`, MUST NOT introduce any new
  declaration/manifest file (unlike 087's `conformed-dimension-map.yaml`), and MUST NOT
  change S7's or V-RC15's behavior, severity, or message text -- the only new surface this
  feature adds is the HR8 rule itself (collision-avoidance allocation: reserved id HR8, no
  shared-schema addition).
- **FR-011**: The rule MUST be wired across every meta-gate surface in the same commit so
  `@register` fires and the wiring/count locks stay green: the module entry in
  `src/retail/rules/__init__.py` (or the existing SQL-rules module if HR8 is added there),
  the `EXPECTED_RULE_IDS` membership, the glossary rules-table row (`docs/glossary.md`),
  `docs/rules/rules-manifest.json`, the severity-posture record
  (`docs/rules/severity-posture.json` and `src/retail/severity_posture.py`), and the
  rule-count claim -- the same S7/S8/HR1 wiring-meta-gate discipline. (Wiring is an
  implementation-stage concern; recorded here so the plan does not miss it.)
- **FR-012**: `docs/readiness/gold-ready.md`'s "Required checks" table MUST be updated to
  list HR8 alongside S6/S7 under the static `retail check` row, naming what HR8 proves
  (daily-step + literal-bounds-order structural soundness) and naming that live coverage
  remains V-RC15's job -- so a reader of the stage doc sees the boundary this spec draws,
  not just the rule's existence.
- **FR-013**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`,
  no glyphs), and MUST use short repo-relative paths (Windows 260-char budget)
  (Principle IX).
- **FR-014**: HR8 and its fixtures MUST stay generic (Principle VII): `dim_date`,
  `retail_store_sales`, and any other worked-example name appearing in this spec are
  ILLUSTRATIVE only and MUST NOT be required literal identifiers in the rule's matching
  logic beyond the existing `dim_date`-prefix convention S7 already relies on; HR8 resolves
  generic `warehouse/migrations/*.sql` paths, not a hardcoded filename.

### Key Entities *(include if feature involves data)*

- **Date-spine build statement**: an `INSERT INTO ... dim_date` statement (per S7's
  existing discovery logic) that contains a `generate_series(start, end, step)` call --
  the unit HR8 inspects.
- **Step classification**: the literal `INTERVAL` text of a `generate_series` call's third
  argument, classified as `daily` (passes), `non-daily-literal` (ERROR, FR-003), or
  `unclassifiable` (ERROR, FR-004).
- **Bounds-order check**: a comparison of a `generate_series` call's `start` and `end`
  arguments, performed only when BOTH are literal date values in a form HR8 recognizes
  (`DATE '...'` or `'...'::date`, per FR-005 and Clarifications 2026-07-04); a reversed
  literal order is an ERROR (FR-005); a non-literal bound, or a bound in an unrecognized
  spelling, on either side skips this check.
- **Pending-live coverage record**: the `Severity.INFO` Finding HR8 emits for every
  structurally-sound build stating that actual fact-to-calendar coverage remains unproven
  here and is `V-RC15`'s job (FR-007). Carries no score, no count, no coverage claim.
- **HR8 Finding**: a `Finding(HR8, severity, message, locator)` -- ERROR for a step or
  bounds-order defect, INFO for the pending-live marker. Categorical only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The shipped worked-example migration
  (`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`) produces ZERO HR8
  ERROR findings when `retail check` runs (mutation-verified against the actual committed
  file: this must hold on the tree as it exists today, not only on a synthetic fixture).
- **SC-002**: Changing a fixture migration's `generate_series` step from `INTERVAL '1 day'`
  to any other literal span (illustratively `INTERVAL '1 month'`) causes HR8 to ERROR
  (mutation-verified), naming the file, line, and the offending step text; reverting the
  step to `INTERVAL '1 day'` clears the ERROR with no other change.
- **SC-003**: Reversing a fixture migration's literal `generate_series` bounds (start after
  end) causes HR8 to ERROR (mutation-verified), naming both literal values; restoring
  chronological order clears the ERROR.
- **SC-004**: Every qualifying `generate_series` call that passes the step and bounds-order
  checks produces exactly one `Severity.INFO` pending-live-coverage record whose message
  text contains no coverage-proof language ("covers", "complete", "gap-free", or
  equivalent), verified by text-content assertion in tests.
- **SC-005**: HR8 adds no numeric score anywhere and never writes to any migration file,
  `source-map.yaml`, or readiness artifact (verified by test + review) -- the rule's only
  output is Findings.
- **SC-006**: The wiring + rule-count lockstep stays green after HR8 lands (the
  wiring-meta-gate and rule-count-claim tests pass; the registered rule set contains
  `HR8`; `docs/readiness/gold-ready.md`'s static-checks row names HR8).
- **SC-007**: 0 generic artifacts (the rule logic, its fixtures) require a
  worked-example-specific identifier (a literal `retail_store_sales` or `demo_sample_orders`
  table/column name) to be present for HR8 to fire correctly on an arbitrary gold-star
  migration.

## Assumptions

- **Daily grain is the settled convention, not an open ambiguity.** Every shipped
  date-dimension surface in this repo (S7's own docstring "enforces ADR RC15", V-RC15's
  coverage check, `docs/readiness/gold-ready.md`'s "contiguous `generate_series` date
  dimension" requirement, and the shipped worked-example migration itself) already
  presupposes a one-row-per-day calendar. HR8 enforces that existing, already-adopted
  convention; it does not introduce a new business rule, so no Principle-V ruling is
  needed to fix the grain at daily. A future non-daily-grain date dimension (a weekly
  reporting mart, for example) is explicitly OUT OF SCOPE (YAGNI) and would need its own
  future spec, not a widening of HR8.
- **HR8 is a mechanical static check added to an already-mechanical stage.** Gold Ready's
  "Required owner / approval" is already "None -- mechanical" (`docs/readiness/
  gold-ready.md`); HR8 joins the existing static-check column (alongside S6/S7/S8) and
  introduces no new approval seam and no new readiness tier -- unlike 087/HR1 (a genuinely
  new model-level tier), this feature raises no Principle-V "who approves" question.
- **`Severity.INFO` (already defined in `src/retail/core.py`) is the pending-live marker
  mechanism**, reused rather than inventing a new severity level or a new artifact; exact
  message wording is confirmable at plan/build time within the FR-007 constraint (no
  coverage-proof language).
- **S7's existing statement-discovery logic (`src/retail/rules/sql.py`,
  `s7_contiguous_date_dim`) is the reused mechanism for finding the `INSERT INTO ...
  dim_date` statement span** -- HR8 does not reimplement comment-stripping or
  statement-scoping from scratch; the plan may factor a shared helper or call the existing
  tokenization utilities S7 already uses. Statement DISCOVERY and literal CLASSIFICATION
  are two different sub-steps reusing two different existing utilities, not one -- see
  Clarifications (2026-07-04) for why, and FR-002/FR-003/FR-005 for where the split
  applies.
- **Live, row-level coverage remains fully out of scope for HR8 (Principle VIII).**
  Whether the generated calendar's actual span covers the fact's actual min/max date is
  a live-data question; this feature never attempts to answer it statically and never
  weakens, duplicates, or replaces `V-RC15`. A migration that passes HR8 cleanly still
  requires a passing `retail validate` run before Gold Ready is `pass` (unchanged).
- **Out of scope for this feature (YAGNI):** live coverage checking of any kind; a
  non-daily-grain calendar convention; auto-fixing a bad step or reversed bounds;
  cross-star date-dimension conformance (087/HR1's job); any new declaration file or
  `source-map.yaml` key; any numeric completeness score. Extending scope is a future spec.
- **Reused mechanism, no new dependency.** `@register` / `RuleContext` / `Finding` /
  `Severity` from `src/retail/core.py` and `src/retail/registry.py`, and the SQL
  tokenization utilities (`tokenize_sql`, `iter_sql_files`, `is_test_path`) already used by
  S5/S6/S7/S8 in `src/retail/rules/sql.py`. Nothing new at the mechanism layer.

## Clarifications

<!-- Principle-V carve-out questions are recorded under their own subsection for a human
     ruling; the workflow is forbidden to answer these. Non-Principle-V ambiguities
     resolved with reasonable constitution-safe defaults (Principle VI) are recorded under
     the dated session subsection. -->

No `[NEEDS CLARIFICATION]` markers are raised in this spec. The two candidate ambiguities
considered -- (a) whether daily grain should be configurable and (b) whether the
mechanical Gold Ready stage needs a new approval seam for this check -- both resolve
against already-settled repo conventions (see Assumptions) rather than against a genuine
open judgment call: (a) every shipped date-dimension surface already presupposes daily
grain, so fixing it is enforcing an existing convention, not inventing a new one; (b) Gold
Ready is already fully mechanical with no approval seam, and HR8 is one more static check
in that same mechanical column, not a new tier (contrast 087/HR1, which genuinely does
raise a new-tier approval question and correctly carries an OPEN Principle-V marker). If a
future reviewer disagrees that either is fully settled, it should be raised at
`/speckit-clarify` time rather than defaulted here.

### 2026-07-04 session

Two further ambiguities were found by inspecting the actual reused mechanism and the
actual committed migration SQL named in the Assumptions section, not by re-reading the
spec text alone. Both are mechanism/feasibility questions, not
grain/PII/business-policy/who-approves judgment calls, so both resolve to a Default adopted
(Principle VI), not an OPEN ruling.

- **Q1 -- Which existing utility can HR8 reuse to read a `generate_series` call's
  literal step/bounds text, given the spec's own Assumptions section named `tokenize_sql`
  (S7's statement-discovery mechanism) as "the reused mechanism"?**
  Verified against the committed source: `tokenize_sql` (`src/retail/sql.py:81`)
  deliberately collapses every `'...'` string-literal's contents to an empty placeholder
  token (`SqlToken("", line)`, see its docstring: "String literals collapse to an
  empty-text placeholder token so no inner word leaks into rule matching"). Since
  `INTERVAL '1 day'` / `INTERVAL '1 month'` and the date bounds (`DATE '2022-01-01'`) are
  themselves string literals, `tokenize_sql` alone cannot supply the text FR-003/FR-004/
  FR-005 need to classify -- confirmed against the shipped worked-example migration
  (`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql:107`), whose
  `generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 day')` call has its
  entire step/bounds text inside quotes.
  **Resolution: Default adopted.** HR8 uses TWO existing utilities for two different
  sub-steps, not one: (1) statement DISCOVERY (finding the qualifying `INSERT INTO ...
  dim_date` statement that contains a `generate_series` call) reuses S7's
  `tokenize_sql`-based token span, unchanged, per FR-002; (2) literal CLASSIFICATION
  (reading the step's and bounds' actual literal text) reads the same statement span via
  `strip_sql_comments` (`src/retail/sql.py:135`) or equivalent literal-preserving raw
  text, because that function's own docstring confirms it "keeps `'...'` literals ...
  intact" (verified: it is already relied on this way by S1) -- unlike `tokenize_sql`,
  it does not blank string contents. This is a mechanism/feasibility default (not a new
  dependency: both functions already ship in `src/retail/sql.py`), so it is recorded here
  rather than left for a human owner. No new business rule or new approval seam results.
  **FRs touched**: FR-002 (states the discovery step uses `tokenize_sql`), FR-003 and
  FR-005 (state the literal-reading step must use `strip_sql_comments` or equivalent, not
  `tokenize_sql`), and the "reused mechanism" bullet in Assumptions (corrected from "one
  mechanism" to "two mechanisms for two sub-steps"). No FR's pass/fail behavior changes --
  this only fixes which existing utility supplies the text FR-003/FR-005 already required
  reading.

- **Q2 -- FR-005 says a "literal date value, however the dialect spells it"; which
  concrete spellings must the bounds-order check (US2) recognize, given the committed
  migrations already use more than one form?**
  Verified against the committed source: `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql:107`'s
  `generate_series` call spells its bounds `DATE '2022-01-01'` / `DATE '2025-01-18'`
  (a typed literal), while other committed migrations in the same tree spell a date
  literal as a cast, e.g. `warehouse/migrations/0003_create_silver_retail_store_sales.sql:58`'s
  `'...'::date` and `warehouse/migrations/0005_create_silver_demo_sample_orders.sql:39`'s
  `order_date::date`. An implementer who recognizes only `DATE '...'` would silently skip
  the bounds-order check on a `generate_series('2025-01-18'::date, '2022-01-01'::date, ...)`
  call -- a reversed range in the OTHER spelling already live in this repo's own
  conventions -- which is a real behavioral fork, not a cosmetic one.
  **Resolution: Default adopted.** FR-005 now names the two concrete forms HR8 must
  recognize as a literal date bound: a typed literal `DATE '2022-01-01'` and a cast literal
  `'2022-01-01'::date` (case-insensitive on the `DATE`/`date` keyword), matched against the
  same `strip_sql_comments`-preserved raw text already used for FR-003's step text (no new
  utility). A bound written in neither recognized spelling is treated as NON-literal for
  this check -- the comparison is skipped (not an ERROR), consistent with FR-005's existing
  "a non-literal bound MUST NOT be treated as a violation by default" design and with
  Principle I's fail-closed spine living in the FR-003/FR-004 step check, not here: this
  default only narrows what US2 can statically prove, it does not widen what counts as a
  proven defect. This is a mechanism/feasibility default (recognizing an existing,
  already-committed spelling convention), not a new business rule or approval seam, so it
  is recorded here rather than left for a human owner.
  **FRs touched**: FR-005 (names the two recognized literal-date spellings and states that
  an unrecognized spelling skips, not fails, the bounds-order check) and the "Bounds-order
  check" Key Entity (same clarification).
