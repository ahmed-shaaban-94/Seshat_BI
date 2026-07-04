# Implementation Plan: Reload / Idempotency Readiness (Anti-Double-Count)

**Branch**: `093-reload-idempotency-readiness` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/093-reload-idempotency-readiness/spec.md`

## Summary

Add one new Gold-Ready static `retail check` rule, reserved id **HR7**, that proves a
gold migration's reload strategy is DECLARED, not that a rerun has actually been
proven duplicate-free. Full drop-and-rebuild (`DROP TABLE IF EXISTS` + clean
`INSERT ... SELECT`, no partial/append logic) is the default and passes free with
zero Findings (Principle VI). Any other shape -- a bare append `INSERT`, an
`ON CONFLICT`/merge-on-key upsert, or a partition/date-range overwrite -- is a
DEVIATION that MUST declare its dedup/overwrite key via a single-line, greppable
`reload-strategy: <key1>[, <key2>...]` marker, either in the migration's own header
comment or in a NEW, optional `warehouse/load-policy.md` entry; an in-SQL
`ON CONFLICT`/overwrite key already satisfies the requirement without a redundant
separate declaration. HR7 is static-only (reads committed `warehouse/migrations/*.sql`
and, if present, `warehouse/load-policy.md`; never opens a database connection,
never executes a load, never depends on a DSN or the `db` extra). It is a bare
structural/readability check -- it confirms a key is NAMED, never that the key is
CORRECT or that a rerun would in fact be duplicate-free; that live proof stays with
the existing Gold-Ready live checks (RC2 grain/PK uniqueness, RC16 penny-exact
silver<->gold reconciliation via `retail validate`), which HR7 does not alter,
duplicate, or substitute for. The dedup/overwrite key is deliberately NOT a new
`source-map.yaml` key (collision-avoidance allocation: that file already has four
features reading/extending it). One genuine Principle-V question -- whether the
full-rebuild-to-incremental transition itself needs a named-human approval seam
(FR-013) -- is recorded OPEN with a PENDING mechanical default; this feature does
not resolve it.

## Technical Context

**Language/Version**: Python 3.11+ (repo runs the retail check on CI Python; local
3.12/3.13).

**Primary Dependencies**: Python stdlib only, at module scope AND inside the rule
handler -- unlike the AL1/additivity-consistency precedent (which lazily imports
`yaml` for a YAML/prose corpus), HR7's two inputs (`warehouse/migrations/*.sql`,
`warehouse/load-policy.md`) are read as plain text; no third-party parser is needed
at all. Reuses `src/retail/sql.py`'s existing `tokenize_sql`, `schema_zone`,
`iter_sql_files`, and the noise-aware raw-text scan pattern from S6/S8's
`_strip_sql_noise` precedent (see research.md "Read-path subtlety").

**Storage**: None. Reads committed repository text files only. Writes nothing at
runtime.

**Testing**: pytest, unit-marked. New rule-behavior tests over fixtures (a
drop-and-rebuild fixture -> zero Findings; a bare-append-with-no-declaration fixture
-> exactly one ERROR Finding; a declared-deviation fixture -> zero Findings; an
`ON CONFLICT`-only fixture with no separate declaration -> zero Findings; a
mixed-pattern fixture -> per-table classification). The existing wiring/lockstep
tests (`test_rules_wiring.py`, `test_wiring_meta_gate.py`,
`test_glossary_rule_table.py`) extended with the new rule id, per the seven-surface
wiring checklist below.

**Target Platform**: CI static check (the retail governance check, `retail check`) +
local dev.

**Project Type**: Single project -- a library/CLI static linter (the retail rules
package). No frontend/backend split; no live surface.

**Performance Goals**: Not performance-sensitive; a bounded scan over the committed
`warehouse/migrations/` corpus (currently 3 files) plus one optional Markdown file.
No goal beyond "runs in the existing `retail check` budget."

**Constraints**: Pure static text read (Principle VIII). MUST NOT open a database
connection, execute or simulate a load, or query live row counts (FR-007/FR-010,
scope guard). MUST NOT emit any numeric confidence/health/idempotency score or an
"N of M" completeness count (hard rule #9, FR-012). MUST NOT re-decide a table's
grain/PK (FR-011; that is Mapping Ready's / HR1's territory). MUST NOT accept or
require a `source-map.yaml` key (collision-avoidance allocation, FR-004). MUST stay
generic -- no worked-example table/column name baked into rule logic (Principle
VII, FR-015). ASCII/UTF-8-no-BOM in every authored artifact, short repo-relative
paths (Principle IX, FR-016). MUST read `warehouse/load-policy.md` gated on
`ctx.tracked_files` membership (mirrors SF1's `ctx.tracked_files`-only pattern and
`iter_sql_files`'s own gating), never the raw working tree -- an untracked local
copy must not influence the gate (Principle IX reproducibility).

**Scale/Scope**: One new rule module + its tests + the seven wiring-surface updates
+ one `docs/readiness/gold-ready.md` doc edit. No new readiness stage; no new
directory beyond the (undocumented-until-needed) `warehouse/load-policy.md` shape.
Rule count advances by exactly one (current authoritative count, read live at build
time, plus one -- 55 -> 56 at research time, but the build must re-read the live
count rather than hardcode it).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. HR7 fails CLOSED with an
  `ERROR` Finding on an undeclared deviation (FR-005); it never merely advises or
  warns on the case the feature exists to catch. Compliance is demonstrable by
  running `retail check` (exit code + Finding list), same as every other rule.
- **Principle III (Medallion/Gold-Only)**: PASS. HR7 reads only `warehouse/migrations/`
  SQL text and, if present, `warehouse/load-policy.md`; it touches no bronze/silver
  data, opens no Power BI surface, and does not alter the gold Kimball star shape
  (fact + conformed dims) that S6/S7/S8 already enforce.
- **Principle IV (Source-Mapping-Before-Silver)**: PASS (non-interaction). HR7 is a
  Gold-Ready check that runs strictly AFTER a table's silver SQL already exists; it
  adds no new silver SQL, does not read or relax the mapping-gate's approval state,
  and does not touch `source-map.yaml` at all (the collision-avoidance allocation
  keeps the dedup/overwrite key OUT of that file, FR-004).
- **Principle V (Agent-Stops-at-Judgment)**: PASS. HR7 itself never decides whether
  a table SHOULD move to an incremental load, never picks a dedup key on an author's
  behalf, and never grants a Gold Ready `pass`. The one live judgment call this
  feature surfaces (FR-013, Q-APPROVAL-SEAM: does the full-rebuild -> incremental
  transition need a named-human approval) is recorded as an OPEN Clarifications
  entry with a PENDING mechanical default an owner may ratify; the agent does not
  answer it unilaterally.
- **Principle VI (Defaults-Then-Deviations)**: PASS -- this IS the feature's design
  center. Full drop-and-rebuild is the DEFAULT and incurs zero new burden (FR-003):
  every migration committed today passes with no edit required (SC-001). Only a
  DEVIATION from that default (an append/upsert/partition-overwrite load) must
  declare anything (FR-004/FR-005). The default path is never taxed to catch the
  deviation case.
- **Principle VII (C086-Is-An-Example-Not-The-Schema)**: PASS. HR7's rule logic and
  doc updates bake in no specific table/column name; the worked example
  (`retail_store_sales` / `0004_create_gold_retail_store_sales_star.sql`) is cited
  only as an illustrative, non-authoritative example of a compliant drop-and-rebuild
  migration (FR-015, SC-006).
- **Principle VIII (Static-First/Live-Deferred)**: PASS. HR7 is 100% static: it
  reads only committed files, never connects to a database, never executes or
  simulates a reload, and never depends on the `db` extra or a DSN (FR-007/FR-010,
  SC-004). The live proof of actual duplicate-free correctness remains RC2/RC16 under
  `retail validate`, explicitly deferred and unaltered by this feature (FR-009).
- **Principle IX (Secrets/Reproducibility)**: PASS. No host/DSN/secret is read or
  written by HR7 or its declaration artifacts. All authored artifacts (rule module,
  doc updates, the `warehouse/load-policy.md` shape documented in data-model.md) are
  ASCII, UTF-8 without BOM, using short repo-relative paths well inside the Windows
  260-char budget (FR-016).
- **Hard rule #9 (No Fabricated Confidence)**: PASS. HR7's only outcomes are "no
  Finding" (pass-eligible) or an `ERROR` Finding naming the missing declaration
  (FR-012); no numeric score, health/maturity band, or "N of M" tally is ever
  emitted (SC-003).
- **F016 (Power BI execution adapter)**: N/A / not assumed to exist. HR7 never
  invokes it, directly or indirectly.

No deferred capability is assumed (no Power BI execution adapter, no live DB, no
new readiness stage). No principle is violated; **no Complexity Tracking entries are
required.**

## Project Structure

### Documentation (this feature)

```text
specs/093-reload-idempotency-readiness/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── spec.md               # Already authored + clarified (input to this stage)
└── tasks.md              # Phase 2 output (/speckit-tasks -- NOT produced by this stage)
```

### Source Code (repository root)

```text
src/retail/rules/
├── reload_idempotency.py       # NEW rule module (@register("HR7", ...))
├── sql.py                      # UNCHANGED -- HR7 imports tokenize_sql/schema_zone/
│                                #   iter_sql_files from here; does not edit S1-S8
├── __init__.py                 # EDIT: add reload_idempotency to the side-effecting
│                                #   import block AND to __all__

warehouse/
├── migrations/                 # UNCHANGED -- HR7 only READS this tree
└── load-policy.md              # NOT created by this feature (optional; see
                                 #   research.md "Landing analysis" -- zero committed
                                 #   migrations are deviations today, so nothing needs
                                 #   to declare here yet). Its shape is documented in
                                 #   data-model.md for the first author who needs it.

docs/
├── readiness/
│   └── gold-ready.md           # EDIT: add HR7 to the "Required checks" static row;
│                                #   one sentence that a static HR7 pass does NOT
│                                #   prove live idempotency (RC2/RC16 stay the proof)
├── rules/
│   ├── rules-manifest.json     # EDIT: append {id: "HR7", title: "..."}
│   └── severity-posture.json   # EDIT: append HR7 under "registered" (severity ERROR)
├── glossary.md                 # EDIT: add an HR7 row to "Static check rules"
└── quality/
    └── rule-count-claims.yaml  # EDIT: reconcile any prose "N rules" claim

tests/unit/
├── test_reload_idempotency.py  # NEW rule-behavior tests over fixtures
├── test_rules_wiring.py        # EDIT: add "HR7" to EXPECTED_RULE_IDS
├── test_wiring_meta_gate.py    # UNCHANGED (reads EXPECTED_RULE_IDS + the two
│                                #   golden JSON files; passes once those move)
└── test_glossary_rule_table.py # UNCHANGED (reads the live registry + glossary.md;
                                 #   passes once the glossary row is added)
```

**Structure Decision**: Single project -- this is a pure addition to the existing
`retail check` static-rules package (Option 1 shape: no frontend/backend split, no
new top-level directory). The seven wiring surfaces enumerated in research.md
("Wiring points and target count") are the complete edit set beyond the rule module
itself; `warehouse/load-policy.md` is documented but NOT created (nothing on the
current tree needs it yet), and `warehouse/migrations/` itself is read-only from
HR7's perspective (this feature authors no new migration).

## Complexity Tracking

*No entries -- no Constitution Check line above requires justification. HR7 is a
single new static rule module reusing an already-shipped SQL-token/raw-text reading
pattern (S6/S8's precedent); it introduces no new project, no new live surface, no
new dependency, and no principle violation.*
