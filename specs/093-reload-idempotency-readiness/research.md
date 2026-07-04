# Phase 0 Research: Reload / Idempotency Readiness (HR7)

Phase 0 -- precedent survey, input-source confirmation, and the deferred-capability
note. Every read below was of a committed artifact in this worktree; no live DB, no
Power BI/PBIP surface, no network was touched.

## Precedents (what SHIPPED to reuse, what to stay distinct from)

- **The static SQL-rule family** (`src/retail/rules/sql.py`: S1-S8, esp. S4b/S6/S7/S8).
  SHIPPED. This is the DIRECT DESIGN PRECEDENT for a static, per-migration-file SQL
  shape check. REUSE verbatim in shape: (a) `iter_sql_files(ctx)` to enumerate
  tracked `warehouse/**/*.sql`; (b) `tokenize_sql()` / `SqlToken` for
  keyword/identifier-shape checks (comment- and string-safe); (c) `schema_zone()` +
  `_DDL_MODIFIERS` to recognize a `gold.<table>` DDL target without hardcoding a
  table name; (d) `_strip_sql_noise()` (S6/S8's noise stripper) as the pattern for
  reading a NUMERIC/text literal (`-1`, or here a `reload-strategy:` comment marker)
  that `tokenize_sql` would otherwise discard; (e) `is_test_path(rel)` fixture
  exemption on every rule; (f) `Severity.ERROR` fail-closed posture for a hard
  correctness gate (S8's precedent), not `Severity.WARNING` (S6/S7's "override-when"
  posture) -- HR7 is FR-005's fail-CLOSED case, not an advisory. STAY DISTINCT: S6/S7/
  S8 check a dimension's `-1` member and calendar contiguity (RC14/RC15 defaults);
  HR7 checks a DIFFERENT, new concern -- reload-strategy declaration (the anti-
  double-count lens, PB-SQL-10/14). HR7 does not edit `sql.py`'s existing rules and
  adds a NEW module + a NEW rule id (HR7), never repurposing S6/S7/S8's ids or
  Findings (FR-017).

- **HR-series static Gold-Ready rule precedent** (087 conformed-dimension-readiness,
  rule id HR1; `specs/087-conformed-dimension-readiness/research.md` -- NOT YET
  MERGED to `src/retail/rules/` as of this feature's authoring, confirmed by an empty
  `src/retail/rules/**/HR1*` glob). HR1 is the sibling HR-series precedent for
  "declaration-then-enforce" at Gold Ready: a human/author declares a shape in a
  committed artifact, a static rule reads and reconciles it, fails closed on an
  undeclared case. REUSE the shape of that posture (declare-or-default, never invent
  the declaration). STAY DISTINCT: HR1's concern is CROSS-STAR dimension shape
  agreement (grain/key/type of a same-named dimension declared `conformed` across two
  or more Gold-Ready stars), reading each table's `source-map.yaml` plus a NEW
  `docs/quality/conformed-dimension-map.yaml`. HR7's concern is SINGLE-TABLE reload
  safety (does this table's own load declare how it stays idempotent), reading the
  migration file itself plus an optional NEW `warehouse/load-policy.md`. Different
  concern, different id, different artifact, different directory
  (`docs/quality/` vs `warehouse/`); HR7 reads or writes nothing HR1 owns, and (per
  087's own research.md) HR1 reads or writes nothing HR7 owns.

- **Gold Ready (Stage 4)** (`docs/readiness/gold-ready.md`; static S6/S7/S8 in
  `src/retail/rules/sql.py`; live RC2/RC15/RC16 in `src/retail/validate.py`, per
  `docs/readiness/gold-ready.md`'s "Required checks" table). SHIPPED. HR7 is a THIRD
  independent static check added to the SAME stage, alongside S6/S7/S8 -- it does not
  alter their Finding text or pass/fail outcome (FR-017), and it does not touch the
  live RC2/RC15/RC16 surface at all (FR-007/FR-010, Principle VIII). RC2 (grain/PK
  uniqueness) and RC16 (penny-exact silver<->gold reconciliation) remain the ONLY
  live proof that a reload did not, in fact, double the data; HR7 is the static,
  pre-execution declaration that a reload is DESIGNED not to.

- **The committed migration set** (`warehouse/migrations/0003_create_silver_retail_store_sales.sql`,
  `0004_create_gold_retail_store_sales_star.sql`, `0005_create_silver_demo_sample_orders.sql`).
  SHIPPED. Confirmed by direct read: `0004` is the ONLY committed GOLD migration
  today (targets `gold.*` via `CREATE SCHEMA IF NOT EXISTS gold` and
  `CREATE TABLE gold.dim_*` / `gold.fct_*`); its header comment states
  "Idempotent: drop fact before dims (FK order), recreate all in one transaction,"
  and its body is `DROP TABLE IF EXISTS` for every fact/dim followed by a clean
  `INSERT ... SELECT` inside a single `BEGIN ... COMMIT` transaction -- textbook
  full drop-and-rebuild, with NO `ON CONFLICT`, NO bare append `INSERT` without a
  prior drop, and NO partition/date-range overwrite. `0003`/`0005` are SILVER
  migrations (out of HR7's scope by FR-001's gold-schema-targeting signal). This is
  the input-source confirmation for SC-001/Assumptions: the entire current committed
  migration set is a single full-drop-and-rebuild gold migration.

- **The wiring meta-gate + rule-count lockstep** (`src/retail/rules/g6.py`,
  `tests/unit/test_wiring_meta_gate.py` [C1-C7 checks], `tests/unit/test_rules_wiring.py`
  [`EXPECTED_RULE_IDS`], `tests/unit/test_glossary_rule_table.py` [glossary-table
  bijection], `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
  `docs/quality/rule-count-claims.yaml`, `docs/glossary.md`). SHIPPED. Adding one
  `@register`ed rule REQUIRES all of these to move in the SAME commit (see "Wiring
  points" below); missing one fails `test_wiring_meta_gate.py`'s C2/C3/C4 checks or
  `test_glossary_rule_table.py`'s bijection, both of which are exercised by
  `retail check`'s own CI path. REUSE the discipline exactly; do not invent a
  shortcut.

## Input-source confirmation (what HR7 reads on disk)

| Input | Confirmed on-disk source | Notes |
|-------|--------------------------|-------|
| Migration corpus | `warehouse/migrations/*.sql` (via `iter_sql_files(ctx)`, filtered to files whose SQL text targets `gold`) | tracked files only; `ctx.tracked_files`-backed, per `sql.py::iter_sql_files` |
| Gold-schema signal | SQL text containing `CREATE SCHEMA IF NOT EXISTS gold` or a DDL/DML statement qualifying `gold.<table>` (via `tokenize_sql` + `schema_zone`) | FR-001's resolved default; never filename pattern-matching |
| Load-pattern shape | `DROP TABLE IF EXISTS <target>` presence/absence, `ON CONFLICT` clause, `TRUNCATE`/partition-`DELETE` before insert, within the SAME migration file, via `tokenize_sql` | FR-002's classification signal; all keyword-level, comment/string-safe |
| Declaration marker | a `reload-strategy: <key1>[, <key2>...]` single-line marker, read from RAW (non-comment-stripped) file text via a noise-aware scan (see "Read-path subtlety" below), OR from `warehouse/load-policy.md` if it exists | FR-004's resolved shape; greppable, not free prose |
| `warehouse/load-policy.md` | a NEW, OPTIONAL file; confirmed by glob that it does NOT exist yet on this tree | FR-014; HR7 must tolerate its absence without treating that as an ERROR (Edge Cases) |
| Rule mechanism | `@register` / `RuleContext` / `Finding` / `Severity` / `is_test_path` in `src/retail/core.py` + `src/retail/registry.py` | reused unchanged; nothing new at the mechanism layer |

### Read-path subtlety: the declaration marker lives INSIDE a SQL comment (load-bearing)

FR-004 allows the declaration to live in "the migration SQL file's own header
comment block." But every SQL reader HR7 would otherwise reuse deliberately DROPS
comments: `tokenize_sql()` collapses `--`/`/* */` spans entirely (they never become
tokens), and `strip_sql_comments()` blanks them to whitespace by design. A rule that
looked for `reload-strategy:` in either of those outputs would never find a marker
that lives in a header comment -- it would always read as absent, misclassifying
every declared deviation as undeclared.

RESOLUTION (mirrors S6/S8's own precedent for the same problem: their `-1` unknown-
member literal is dropped by `tokenize_sql`'s numeric-literal handling, so S6/S8
scan `_strip_sql_noise()`'s output instead, which preserves comment TEXT while only
blanking string/dollar-quote BODIES). HR7 needs the mirror-image read: it scans the
RAW, un-stripped file text (or a comment-preserving light scan) specifically for the
single-line `reload-strategy: <key(s)>` marker, entirely independent of the
tokenized/noise-stripped passes used for load-PATTERN classification (FR-002). Two
separate read passes over the same file, each fit for its own purpose:

1. **Tokenized pass** (`tokenize_sql` + `schema_zone`): gold-schema identification
   (FR-001) and load-pattern classification -- DROP-then-INSERT vs bare-INSERT vs
   `ON CONFLICT` vs partition-overwrite (FR-002/FR-006).
2. **Raw-text pass**: a line-oriented scan of the UN-stripped file text for the
   `reload-strategy:` marker inside a `--` comment line (FR-004), independent of
   token boundaries.

`warehouse/load-policy.md` is plain Markdown, not SQL -- it is read as a committed
text file directly (line-oriented `reload-strategy:` marker scan plus the migration-
filename/table-name binding fields FR-004 requires), with no SQL lexer involved.

## Landing analysis (green, not red -- the opposite of 087/HR1's landing risk)

087/HR1 landed RED on the current tree the instant it registered (two committed
stars + a missing cross-star map = an immediate fail-closed ERROR by its own FR-010),
requiring an empty-but-present scaffold file just to reach green. HR7 is the OPPOSITE
case: the ONLY committed gold migration (`0004_create_gold_retail_store_sales_star.sql`)
is full drop-and-rebuild -- the default, no-declaration-required path (FR-003) -- so
HR7 registers and lands GREEN with ZERO Findings and requires NO new file to be
created. This is exactly SC-001 ("100% of currently committed gold migrations pass
HR7 with zero Findings, with no change to any existing migration file required"),
verified against the real tree at zero cost, not merely asserted.

Corollary: because zero migrations are deviations today, `warehouse/load-policy.md`
is NOT created as part of shipping HR7 (FR-014 + Assumptions: "optional... need not
exist while zero migrations are deviations"). Its SHAPE is documented in
`data-model.md` (and may be scaffolded as a generic template under `templates/` on a
later feature that actually needs a declaration), but HR7 itself must handle the
file's total absence gracefully -- it is not an ERROR condition (Edge Cases).

## Wiring points and target count (mirrors 068's R4, refreshed to the CURRENT surface set)

The prior similarly-scoped rule feature (068 additivity-consistency-rule) recorded
"five wiring places." Reading the CURRENT `tests/unit/test_wiring_meta_gate.py` (the
authoritative lockstep gate, feature 061) shows the complete set is now SEVEN
surfaces (the meta-gate's C1-C7 checks plus the glossary-table sibling test added
after 068 landed):

1. **Rule module** under `src/retail/rules/` (the new `HR7` `@register`).
2. **`src/retail/rules/__init__.py`** -- add the module to the side-effecting import
   block AND to `__all__` (C1 package-symmetry: on-disk == import-list == `__all__`).
3. **`tests/unit/test_rules_wiring.py`** -- add `HR7` to `EXPECTED_RULE_IDS` (C2: live
   registry ids == expected set).
4. **`docs/rules/rules-manifest.json`** -- add the `{id: "HR7", title: "..."}` entry
   (C3: manifest `{id, title}` matches the live map).
5. **`docs/rules/severity-posture.json`** -- add `HR7` under the `registered` section
   with its severity (C4: every live id appears in the posture golden).
6. **`docs/glossary.md`** -- add an `HR7` row to the "Static check rules" table
   (the glossary-rule-table bijection test, `test_glossary_rule_table.py`: every
   live rule id must appear as a backtick-quoted id in that table).
7. **`docs/quality/rule-count-claims.yaml`** -- update the hand-curated prose-count
   claims manifest the `rule_count_claims.py` (a separate registered rule) reads, so
   any prose "N rules" claim stays reconciled.

Current authoritative count (read live, not hardcoded): `docs/rules/rules-manifest.json`
holds 55 entries at research time; HR7 is the 56th. The BUILD must read the live
count at build time (never hardcode a number in rule logic), per 068's own R4 caution
that another rule may land first.

## Deferred capabilities NOT assumed

- **F016 Power BI execution adapter** (official Power BI MCP / connection; `pbi-cli`
  no longer preferred) is gated + LAST and is assumed NOT to exist. HR7 never invokes
  it.
- **Live DB / `retail validate`** (RC2/RC16) proof that a reload did not, in fact,
  double the data is DEFERRED to the live surface exactly as it is today (Principle
  VIII). HR7 opens no database connection, executes no reload, and reads no live
  Power BI/PBIP surface; it proves only that a declaration exists and is
  structurally well-formed (FR-007/FR-008/FR-009/FR-010).
- **A live idempotency re-run check** (actually re-running a load twice and diffing
  row counts) is explicitly out of scope and not designed toward; if ever built it
  is a separate, future feature (FR-008's boundary note).
- **`warehouse/load-policy.md`** is NOT created by this feature (see Landing
  analysis); only its shape is documented, and HR7 must tolerate its absence.
- **A named-human approval seam** for the full-rebuild -> incremental transition
  (FR-013 / Q-APPROVAL-SEAM) is NOT invented here; it is a genuine OPEN Principle-V
  question carried to Clarifications, with a recorded PENDING default (mechanical,
  no approval seam) that the agent does not self-ratify.
- No new readiness stage, no new live check, and no new dependency on the `db` extra
  or a DSN are assumed or added (SC-004).

## Open (Principle V -- NOT resolved here; carried to the owner)

- **Q-APPROVAL-SEAM (FR-013)**: whether a table's transition from full-rebuild to an
  incremental/append load strategy requires a recorded named-human approval before
  its Gold Ready status can rely on a passing HR7, or whether a clean HR7 run is
  purely mechanical (direct precedent: `gold-ready.md`'s "Required owner / approval:
  None -- mechanical," and 087/HR1's own identically-shaped pending default). RECORDED
  PENDING DEFAULT an owner may ratify: MECHANICAL -- no approval seam is invented
  until an owner rules one in. Until ruled, HR7 emits Findings only and never
  contributes to a self-granted Gold Ready `pass` beyond what a clean static check
  already contributes today (same as S6/S7/S8).
