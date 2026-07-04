# Phase 1 Data Model: Reload / Idempotency Readiness (HR7)

No persisted database schema is introduced. These are the in-memory shapes the rule
builds while reading committed text, plus the one NEW optional artifact
(`warehouse/load-policy.md`) this feature defines the shape of but does not create.
All shapes are generic (Principle VII): (a) no worked-example table/column name
appears in any field or enum value below; (b) any reference to the one committed
migration that already exists (`0004_create_gold_retail_store_sales_star.sql`) is
illustrative only, never an authoritative part of the schema.

## ReloadStrategy (closed enum)

The per-migration (or per-table, see MigrationTableLoad) classification HR7 derives
from a migration's own SQL shape. Never a stored/authored field -- always DERIVED.

- `FULL_DROP_AND_REBUILD` -- a `DROP TABLE IF EXISTS <target>` for the target,
  followed by a clean `INSERT ... SELECT` with no partial/append logic. The DEFAULT
  (Principle VI); requires no declaration.
- `DEVIATION` -- any other shape: a bare append `INSERT` with no prior drop/truncate
  of the target, an `ON CONFLICT`/merge-on-key upsert, or a partition/date-range
  overwrite before insert. Requires a declared dedup/overwrite key (FR-004/FR-005).

Rule: classification is derived ONLY from the migration's own SQL tokens
(`DROP TABLE IF EXISTS`, `ON CONFLICT`, a `TRUNCATE`/`DELETE ... WHERE <date-range>`
before an `INSERT`, presence/absence of a bare `INSERT INTO gold.<table>` with none
of the above). HR7 never infers a strategy from anything outside the migration file
under evaluation.

## MigrationTableLoad

The per-table load classification WITHIN one migration file (Edge Cases: a mixed
migration may drop-and-rebuild some tables and append into another; each target
table is classified independently).

- `migration_path`: the repo-relative path of the migration file (e.g.
  `warehouse/migrations/NNNN_*.sql`), read via `iter_sql_files(ctx)`.
- `target_table`: the `gold.<table>` identifier the load targets, resolved via
  `schema_zone()`/`tokenize_sql()` the same way S6/S7/S8 resolve a `gold.dim_*`
  target -- never a hardcoded name.
- `strategy`: a `ReloadStrategy`.
- `in_sql_key`: the key already expressed directly in the SQL, if any (an
  `ON CONFLICT (<key>) DO UPDATE` clause's key list, or an explicit partition/
  date-range boundary named in a `DELETE`/`TRUNCATE` before insert). `None` if the
  load carries no in-SQL key (FR-006).

## GoldMigrationSignal

The FR-001 gate that decides whether a `warehouse/migrations/*.sql` file is even
in-scope for HR7 (silver migrations are out of scope).

- `is_gold`: `True` only if the file's SQL text contains `CREATE SCHEMA IF NOT
  EXISTS gold` OR a DDL/DML statement qualifying a `gold.<table>` target (the same
  structural signal `schema_zone()` already exposes). Never determined by filename
  pattern-matching (FR-001's resolved default).

## ReloadStrategyDeclaration

The dedup/overwrite key an author records for a `DEVIATION` load. Lives in EXACTLY
one of two places (FR-004); HR7 must never accept or require a third location
(especially not `source-map.yaml` -- the collision-avoidance allocation).

- `location`: one of `MIGRATION_HEADER_COMMENT` | `LOAD_POLICY_FILE`.
- `migration_path`: which migration file the declaration binds to. For a
  `MIGRATION_HEADER_COMMENT` declaration this is simply the file it was found in;
  for a `LOAD_POLICY_FILE` entry this is an EXPLICIT field the entry must name
  (FR-004's binding requirement).
- `target_table`: the table the declaration applies to (required for a
  `LOAD_POLICY_FILE` entry so a mixed-migration per-table deviation binds to the
  right table; implied to be the migration's own gold target for a header-comment
  declaration).
- `keys`: a non-empty list of column-identifier strings parsed from the marker
  `reload-strategy: <key1>[, <key2>...]` (comma-separated). Each key MUST look like
  a syntactically plausible column identifier (bare structural check, FR-008) --
  HR7 never verifies a key exists in a live schema.
- `source_locator`: the file (+ line, for a header comment) the declaration was read
  from, for the Finding/pass-context trail.

### The `reload-strategy:` marker (exact shape, FR-004/FR-004-session-default)

A single-line, greppable marker of the form:

```text
reload-strategy: <key1>[, <key2>, ...]
```

- MUST appear on its own line (inside a `--` SQL comment for a header-comment
  declaration, or as a plain Markdown line for a `load-policy.md` entry).
- Comma-separated column identifiers only; free prose ELSEWHERE in the same comment
  block or file does NOT itself satisfy FR-004 (e.g. "Idempotent: DROP+CREATE in one
  transaction" -- today's actual committed prose -- is not a marker and is not
  required to become one, because it accompanies a FULL_DROP_AND_REBUILD load that
  needs no declaration at all).
- A `warehouse/load-policy.md` entry additionally names the migration FILENAME and
  the TARGET TABLE alongside the marker (see `LoadPolicyEntry` below); a bare marker
  with no binding fields does not satisfy FR-004 for that location.

## `warehouse/load-policy.md` (NEW, OPTIONAL file -- shape documented, not created)

Per research.md's Landing analysis, this file does NOT exist on the current tree and
is NOT created by this feature (zero committed migrations are deviations today). Its
shape is recorded here so the first author who authors a deviation load has a
committed contract to follow, and so HR7's reader has a fixed shape to parse.

- **Existence is optional** (FR-014 + Assumptions): its absence is NEVER an ERROR
  when there are zero deviations needing an entry here (a deviation may satisfy
  FR-004 entirely via its own header comment instead).
- **Not a mapping-gate artifact**: distinct from `source-map.yaml`; never read by
  the mapping gate, HR1, or the live `retail validate` surface (FR-014).
- **Read gated on `ctx.tracked_files`, not the raw working tree** (reproducibility,
  Principle IX; mirrors SF1's `ctx.tracked_files`-only read pattern): HR7 reads
  `warehouse/load-policy.md` only when it appears in `ctx.tracked_files`. An
  untracked local copy of this file on disk MUST NOT influence the gate -- the same
  discipline `iter_sql_files(ctx)` already applies to the migration corpus.
- **Shape**: a Markdown file whose body is a list of `LoadPolicyEntry` records, each
  minimally naming:
  - the migration filename (repo-relative or bare basename; HR7 resolves either
    against the actual `warehouse/migrations/` tree),
  - the target table name,
  - the `reload-strategy: <key(s)>` marker.

  Illustrative shape (generic; no worked-example name used as a live requirement):

  ```markdown
  # Load policy declarations

  Entries here declare the dedup/overwrite key for a gold migration whose load is
  NOT full drop-and-rebuild. A full drop-and-rebuild migration needs no entry.

  ## <migration-filename>.sql -- gold.<table>

  reload-strategy: <key1>, <key2>
  ```

## HR7 Finding (uses the existing `Finding` model -- no new entity)

- `rule_id`: `"HR7"`.
- `severity`: always `Severity.ERROR` (FR-005: fails CLOSED, never merely advises --
  mirrors S8's ERROR posture for a hard correctness gate, not S6/S7's WARNING
  "override-when" posture).
- `message`: names the offending migration file (and target table, if the deviation
  is per-table within a mixed migration) and states that a reload-strategy
  declaration is required and absent. Never states or implies that a passing
  declaration proves a live rerun would be duplicate-free (FR-009, US3).
- `locator`: `"<migration_path>"` or `"<migration_path>:<line>"` for the offending
  migration/table.
- The rule's only other outcome is emitting NO Finding for that migration/table
  (pass-eligible). No numeric field exists anywhere on this entity (hard rule #9,
  FR-012).

## Invariants

- Read-only: HR7 mutates no source artifact, ever (Principle VIII).
- No execution: HR7 opens no database connection, runs no reload, queries no live
  row count (FR-007/FR-010).
- Default-free-pass: a `FULL_DROP_AND_REBUILD` classification requires and accepts
  no declaration at all (FR-003; Principle VI).
- Fail-closed on deviation: a `DEVIATION` classification with no
  `ReloadStrategyDeclaration` (neither header comment, `load-policy.md` entry, nor
  an `in_sql_key`) always produces exactly one `ERROR` Finding (FR-005).
- Structural-only verification: a declaration is checked for PRESENCE and
  syntactic plausibility of its key list only, never cross-checked against a live
  schema or proven correct at runtime (FR-008).
- No grain re-derivation: HR7 never judges whether a declared key is the "correct"
  grain/PK key -- that is Mapping Ready's/HR1's territory (FR-011).
- No score, ever: outcome is categorical (Finding or no Finding) only (FR-012).
- Collision-avoidance: `source-map.yaml` is never read or written by HR7 for this
  purpose (FR-004, the collision-avoidance allocation).
- Additive: HR7 changes no existing rule's (S6/S7/S8/HR1/any RC-series) Finding text
  or pass/fail outcome (FR-017).
