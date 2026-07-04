# Research: Date-Spine Completeness Static Gate (HR8)

Phase 0 -- precedent survey, input-source confirmation, and the deferred-capability
note. Every read below was of a committed artifact in this worktree; no live DB, no
Power BI/PBIP surface, no network was touched.

## Precedents (what SHIPPED to reuse, what to stay distinct from)

- **S7 contiguous date dim** (`src/retail/rules/sql.py:503-544`,
  `s7_contiguous_date_dim`, feature 003). SHIPPED. This is the DIRECT DESIGN
  PRECEDENT and the DISCOVERY MECHANISM HR8 reuses. REUSE, verbatim in shape: (a)
  `iter_sql_files(ctx)` + `is_test_path` fixture exemption to enumerate committed
  SQL; (b) `tokenize_sql`-based token scan to find an `INSERT` statement whose
  span (up to the next `;`) targets a name starting with `dim_date`; (c) the
  `Finding(rule_id, severity, message, locator)` shape with a `file:line`
  locator. STAY DISTINCT: S7 only asks "does this statement's token span contain
  a `generate_series` token" (WARNING if it instead used `SELECT DISTINCT`); it
  never reads what is INSIDE the `generate_series(...)` call. HR8 is the NEXT
  check, firing only once S7's own precondition (a `generate_series` call
  exists in that span) already holds, and inspects the call's own arguments
  (step, bounds) that S7 does not. HR8 does NOT edit `s7_contiguous_date_dim`,
  does NOT change its severity or message, and does NOT re-implement
  comment-stripping/statement-scoping from scratch (Assumptions; FR-002;
  FR-010).

- **S8 date-dim-no-unknown-member** (`src/retail/rules/sql.py:458-500`,
  `s8_date_dim_no_unknown_member`, same file). SHIPPED. Confirms the SAME-FILE
  convention: a date-dimension-specific check that shares S7's statement-target
  matching idiom (`dim.startswith("dim_date")`) but lives as its OWN
  `@register`ed function in `sql.py`, not a new module. HR8 follows this exact
  precedent -- one more `@register`ed function inside `sql.py`, not a new
  `rule_hr8.py` module (contrast 087/HR1, which DID add a new module because its
  subject, a cross-star YAML manifest, has nothing to do with `sql.py`'s SQL-text
  scanning; HR8's subject is squarely SQL-text scanning, same as S1-S8).

- **`V-RC15` date coverage** (`src/retail/validate.py`, `check_date_coverage`,
  feature 004). SHIPPED. The LIVE, read-only check that every distinct fact date
  exists in the materialized date dimension, run at Gold Ready with a DSN and the
  `db` extra (Principle VIII). HR8 composes ABOVE this, never duplicates it: HR8
  proves the migration's DECLARED structure (daily step, sane literal bounds) is
  even capable of producing a complete calendar; V-RC15 proves the MATERIALIZED
  data actually is complete against the real fact span. HR8 never opens a
  database connection, never reads `src/retail/validate.py`, and never invokes
  `retail validate`. Where HR8 cannot prove real coverage from static text alone
  (literal bounds, the common case), it emits an INFO record naming live
  coverage as PENDING V-RC15 -- it never claims what only V-RC15 can prove.

- **087 conformed-dimension-map / HR1** (`specs/087-conformed-dimension-readiness/`,
  in flight, NOT yet landed in this worktree -- confirmed by `grep -n "HR"
  tests/unit/test_rules_wiring.py` returning no match and `ls src/retail/rules/`
  showing no `rule_hr1.py`). This is the SIBLING rule-adding feature whose PLAN
  SHAPE (Summary / Technical Context / Constitution Check table / Project
  Structure / Complexity Tracking, and a research.md with this same section
  layout) this plan mirrors at the DOCUMENT level. STAY DISTINCT at the SUBJECT
  level: HR1 is a MODEL-LEVEL, cross-star check reading a NEW human-authored
  YAML manifest (`docs/quality/conformed-dimension-map.yaml`) plus every table's
  `source-map.yaml`; HR8 is a PER-MIGRATION, single-file static check reading
  ONLY the already-committed migration SQL, with NO new manifest and NO new
  `source-map.yaml` key. HR1's own dim_date edge-case note states plainly that
  HR1's date-dim conformance "reduces to grain + type agreement across stars,
  not a re-check of RC15's contiguity (that is Gold Ready's job per star)" --
  HR8 IS that per-star contiguity check HR1 explicitly deferred. Both reserve
  DIFFERENT rule ids (HR1, HR8) under the same new "HR" family prefix; neither
  spec's collision-avoidance allocation touches the other's new surface (HR1:
  `conformed-dimension-map.yaml` + HR1; HR8: no new file + HR8 only).

- **The wiring meta-gate + rule-count lockstep**
  (`tests/unit/test_wiring_meta_gate.py`, `tests/unit/test_rules_wiring.py`
  `EXPECTED_RULE_IDS`, `docs/rules/rules-manifest.json`,
  `docs/rules/severity-posture.json`, `docs/quality/rule-count-claims.yaml`,
  `docs/glossary.md`). SHIPPED. Adding one `@register`ed rule REQUIRES this
  multi-surface wiring update in the SAME commit (FR-011). REUSE the discipline
  exactly, per the S7/S8/HR1 precedent.

## Input-source confirmation (what HR8 reads on disk)

| Input | Confirmed on-disk source | Notes |
|-------|--------------------------|-------|
| Subject SQL | `warehouse/migrations/*.sql` (committed migration files), enumerated via `iter_sql_files(ctx)` | same universe S1-S8 already scan; `ctx.tracked_files` only |
| Statement discovery | `tokenize_sql` (`src/retail/sql.py:81`) token span for an `INSERT INTO ... dim_date...` statement, reused unchanged from `s7_contiguous_date_dim`'s own loop shape | confirmed: `tokenize_sql`'s docstring states string literals "collapse to an empty-text placeholder token" -- usable to LOCATE the statement and the `generate_series` token, NOT to read literal text |
| Literal classification | `strip_sql_comments` (`src/retail/sql.py:135`) raw text over the SAME statement's line span, to read the `generate_series(...)` call's actual step/bounds literal text | confirmed: its docstring states it "keeps `'...'` literals ... intact" -- already relied on this way by S1 |
| Rule mechanism | `@register` / `RuleContext` / `Finding` / `Severity` (`src/retail/core.py`) + `registry.py`; `iter_sql_files` / `is_test_path` (`src/retail/sql.py`, `src/retail/core.py`) | reused unchanged; nothing new at the mechanism layer |

### The committed tree today -- landing precondition confirmed (verified, not assumed)

Enumerated ALL committed migrations (not just the one named in the spec), because
HR8 fires on every qualifying statement, not one named file:

```text
warehouse/migrations/0003_create_silver_retail_store_sales.sql   -- no dim_date, silver only
warehouse/migrations/0004_create_gold_retail_store_sales_star.sql -- ONE dim_date build (gold.dim_date_rss)
warehouse/migrations/0005_create_silver_demo_sample_orders.sql   -- no dim_date, silver only (no gold star yet)
```

Only `0004_create_gold_retail_store_sales_star.sql` contains a `dim_date`-prefixed
`INSERT` with a `generate_series` call (line 107):

```sql
FROM generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 day') AS g(d);
```

Step is the literal `INTERVAL '1 day'` (passes FR-003); both bounds are literal
dates in chronological order, `2022-01-01` before `2025-01-18` (passes FR-005).
**HR8 lands GREEN on the tree as it exists today with zero ERROR findings**
(SC-001) -- no fixture-only claim; this is a fact about the live committed tree,
re-verified at implement time per the parallel-landing note below.
`demo_sample_orders` has no gold migration yet (silver-only per 0005), so it
supplies zero `dim_date` statements for HR8 to evaluate -- consistent with the
Edge Cases section's "no `dim_date` INSERT found -> no-op" behavior.

## Design sketch -- how the two reused utilities compose (feasibility, not implementation)

The 2026-07-04 Clarification session settled WHICH utility supplies which fact;
this sketch confirms HOW they compose so the split is not hand-waved:

1. **Discovery** (S7's existing loop shape, unchanged): tokenize the file with
   `tokenize_sql`; walk tokens for an `INSERT` token; collect that statement's
   token span up to the next `;`; keep it only if some token's text
   case-insensitively starts with `dim_date` AND some token's text (lowercased)
   equals `generate_series`. This yields a `(start_line, end_line)` bound on the
   ORIGINAL file (both `tokenize_sql`'s `SqlToken.line` values), not a text
   span -- token positions carry line numbers only, not character offsets.
2. **Slice**: take `strip_sql_comments(file_text)` (comments blanked, ALL
   literals intact, exact same line numbering as the original file because both
   strippers preserve line counts) and select the line range
   `[start_line, end_line]` found in step 1, joined back into a text block.
3. **Classify**: run one small literal-preserving regex/scan over that block
   for `generate_series\s*\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)` (three
   comma-separated top-level arguments -- balanced-paren aware, since a bound
   MAY itself be a parenthesized subquery per Edge Cases). Each captured group
   is then classified independently:
   - `step` (3rd arg): literal-`INTERVAL`-shaped (`INTERVAL\s+'...'`) and daily
     (`'1 day'`, whitespace-insensitive) -> pass; literal-`INTERVAL`-shaped but a
     different span -> FR-003 ERROR; anything else (bare identifier, computed
     expression, non-`INTERVAL` literal) -> FR-004 ERROR (unclassifiable,
     distinct wording).
   - `start`/`end` (1st/2nd args): literal-date-shaped
     (`DATE\s+'YYYY-MM-DD'` or an equivalent dialect spelling) on BOTH sides ->
     compare chronologically, FR-005 ERROR if reversed; if EITHER side is not
     literal-date-shaped (a subquery, a function call, a parameter) -> skip the
     bounds-order comparison entirely (not a violation by default).
4. **Pending-live marker**: for every qualifying `generate_series` call that
   clears steps 3's ERROR checks, emit exactly one `Severity.INFO` Finding
   (FR-007) -- independent of the ERROR/no-ERROR outcome of the bounds check,
   since FR-007 fires "for every qualifying call that passes FR-003/FR-004 (and
   FR-005 where applicable)".

This is a design-level sketch fixing the feasibility question (the split is
buildable with existing stdlib `re` + the two named utilities, no new
dependency); the exact regex/parse code is an implementation-stage decision, not
fixed here.

## Deferred capabilities NOT assumed

- **F016 Power BI execution adapter** (official Power BI MCP / connection;
  `pbi-cli` no longer preferred) is gated + LAST and is assumed NOT to exist.
  HR8 never invokes it and never reads a live Power BI/PBIP surface.
- **Live DB / `retail validate` (V-RC15) row-level coverage** -- whether the
  MATERIALIZED calendar's actual span covers the fact's actual min/max date --
  is explicitly OUT OF SCOPE for HR8 and remains V-RC15's unchanged job
  (Principle VIII; FR-006). HR8 opens no database connection anywhere in its
  implementation.
- **A non-daily-grain date-dimension convention** (e.g. a future weekly
  reporting mart) is explicitly OUT OF SCOPE (YAGNI per spec Assumptions); no
  configurability is designed in.
- **Auto-fixing a bad step or reversed bounds** is OUT OF SCOPE (FR-009); HR8
  never authors or edits `warehouse/migrations/*.sql`.
- **087/HR1's cross-star conformance** is a DIFFERENT, complementary check (see
  Precedents above); HR8 never compares two stars' dimensions and needs no
  second star to fire.
- No new `source-map.yaml` key and no new declaration/manifest file are assumed
  or introduced (FR-010) -- unlike 087/HR1, this feature's collision-avoidance
  allocation is the reserved rule id ONLY.

## Parallel-landing serialization note

Per the feature brief, 19 features are in flight in parallel worktrees. Two
facts here are LIVE-STATE, not fixed constants, and MUST be re-verified against
the actual committed tree at implement time rather than trusted from this
research pass:

- **The authoritative rule count** is `len(docs/rules/rules-manifest.json)`,
  currently **55** (per `docs/quality/rule-count-claims.yaml` /
  `docs/glossary.md`'s "Currently 55 rules in 21 families" line). HR8 adds ONE
  rule; whatever the live count is when HR8 actually lands, it becomes
  count-plus-one there, not a number fixed here.
- **The family list.** HR8 is the FIRST rule in a brand-new "HR" family
  (confirmed: `grep -n "HR" tests/unit/test_rules_wiring.py` finds no existing
  "HR"-prefixed id in this worktree today). 087/HR1 is ALSO an in-flight
  sibling introducing the SAME new "HR" family under a DIFFERENT id (HR1).
  Whichever of the two lands first is the commit that appends "HR" to the
  family-letter list (`docs/glossary.md`'s "(S, D, C, ... , SF)" enumeration);
  the second to land finds "HR" already present and adds no new family, only a
  new id inside it. This plan does not assume landing order -- the glossary
  edit at implement time must READ the live file, not assume 21 or 22 families.

## Open (Principle V) -- none raised by this feature

Unlike 087/HR1 (which carries a genuinely OPEN Q-APPROVAL-SEAM question), HR8
raises no Principle-V judgment call: it enforces an ALREADY-SETTLED convention
(daily-grain date dimensions, presupposed by S7, V-RC15, and
`docs/readiness/gold-ready.md` already) rather than deciding a new one, and
Gold Ready is already fully mechanical with no approval seam for HR8 to
interact with (per spec Clarifications, both candidate ambiguities resolved
against settled conventions, not left OPEN).
