# Data Model: Postgres live-validation suite

**Feature**: `specs/082-postgres-live-validation-suite/spec.md`

This document describes the generic seed schema and the harness-internal entities. It is a
design description for the plan/tasks phases -- no SQL here is executed by this spec chain.

## 1. Generic seed schema (silver + gold, ADR-0002-shaped)

A minimal, non-worked-example schema, sized to exercise all four `retail validate` live checks
plus one L4 measure. Names are deliberately generic placeholders, per Constitution Principle VII
("C086 is an example, not the schema") -- this feature must not bake in any client-specific name.

> **Grain and foreign keys are declared LOGICALLY, not as DB constraints.** The
> columns below carry NO `PRIMARY KEY`, `UNIQUE`, or `REFERENCES` constraints. This
> is load-bearing, not an omission: the `retail validate` live checks exist precisely
> to catch grain/FK/coverage defects on *materialized rows* that the warehouse layers
> do NOT enforce as engine constraints (`src/retail/validate.py` docstring -- a real
> silver staging table does not PK-enforce the declared grain; gold validates FKs
> post-load, it does not delegate them to the engine). If the seed schema enforced
> PK/FK as constraints, the defect seeds below (duplicate grain, orphan FK, date gap)
> would be REJECTED at INSERT time -- the seed would fail, the check would `pytest.skip`,
> and the "true positive" proof (US2 / SC-002) would silently never run. So each
> defect must be *insertable*, and the check -- not the engine -- must be what flags it.

```text
silver.stg_order_line               -- one fact-shaped staging table (silver grain)
  order_line_id       TEXT NOT NULL   -- RC2 target: declared grain (logical, NOT a DB PK)
  order_date          DATE NOT NULL
  product_key         TEXT NOT NULL   -- logical FK target for the RC16 orphan check (no REFERENCES)
  quantity            NUMERIC NOT NULL
  net_amount          NUMERIC NOT NULL   -- RC16 reconciliation measure

gold.dim_date                        -- RC15 target: contiguous generate_series calendar
  date_key            DATE NOT NULL   -- logical calendar key (NOT a DB PK)
  year                INT NOT NULL
  month               INT NOT NULL
  day                 INT NOT NULL

gold.dim_product                     -- conformed dim with a -1 unknown member (RC14 pattern)
  product_key         TEXT NOT NULL   -- logical key; includes a '-1' unknown-member row (no DB PK)
  product_name        TEXT NOT NULL

gold.fct_order_line                  -- gold fact, same grain as silver.stg_order_line
  order_line_id       TEXT NOT NULL   -- logical grain (NOT a DB PK -- the RC2 check proves uniqueness on the rows)
  date_key            DATE NOT NULL   -- logical FK to gold.dim_date (NO REFERENCES -- the RC15 check proves coverage)
  product_key         TEXT NOT NULL   -- logical FK to gold.dim_product (NO REFERENCES -- the RC16 check proves 0 orphans)
  quantity            NUMERIC NOT NULL
  net_amount          NUMERIC NOT NULL   -- reconciled against silver.stg_order_line.net_amount
```

This shape deliberately mirrors the RC-default vocabulary already used by
`docs/decisions/0002-retail-cleaning-defaults.md` and `templates/reconciliation-report.md`
(silver grain, gold star with conformed dims + `-1` unknown member + contiguous date dim,
penny-exact reconciliation) at the smallest scale that exercises all four checks -- while
keeping every grain/FK relationship LOGICAL (a data property the checks verify) rather than
a DB constraint (which would make the defect seeds un-insertable; see the note above).

## 2. Seed scenario variants

Each variant is a separate `.sql` file (Decision 2 in `research.md`); all variants share the DDL
above and differ only in which rows are inserted.

| Scenario file (working name) | Rows inserted | Which check it targets | Expected live-check result |
|---|---|---|---|
| `seed_clean.sql` | A small clean dataset: N order lines, all dates present in `dim_date`, all `product_key` values present in `dim_product`, silver/gold `net_amount` sums equal to the penny. | All four RC checks + L4 | Zero ERROR findings on all four; L4 match on the seeded measure. |
| `seed_defect_pk_duplicate.sql` | Two `fct_order_line`/`stg_order_line` rows sharing the same `order_line_id`. | `check_pk_uniqueness` (V-RC2) | Exactly one `V-RC2` ERROR naming the duplicate count; other checks stay clean on their own untouched rows. |
| `seed_defect_date_gap.sql` | One order line whose `order_date` has no corresponding `dim_date` row. | `check_date_coverage` (V-RC15) | Exactly one `V-RC15` ERROR naming the coverage gap; PK/orphan/reconciliation checks stay clean. |
| `seed_defect_orphan_fk.sql` | One `fct_order_line` row whose `product_key` matches no `dim_product` row (and is not the `-1` unknown member). | `check_orphan_fks` (V-RC16) | Exactly one `V-RC16` ERROR naming the orphan; other checks stay clean. |
| `seed_defect_reconciliation_mismatch.sql` | Silver and gold `net_amount` sums differing by exactly one cent (e.g. one gold row's amount is manually offset post-load). | `check_reconciliation` (V-RC16) | Exactly one `V-RC16` ERROR naming the one-cent gap; other checks stay clean. |
| `seed_value_check.sql` | A gold table with a known, hand-computable `sum(net_amount)` total for use as the L4 target measure. | `check_expected_value` (V-L4) | No finding when `ExpectedValue` matches; exactly one `V-L4` ERROR when perturbed beyond tolerance (two live scenarios reuse this one seed). |

Each defect scenario is seeded in **isolation** (its own fresh container/schema instance, per
`research.md` Decision 3's "fresh container or reset schema" note), so FR-005's "one check's
injected defect does not cause a different check to misfire" is structural, not just asserted.

## 3. Harness-internal entities (test code, not shipped package code)

These are pytest-fixture-level Python objects describing the harness's own bookkeeping -- they
live in test code under the live-DB test directory (`research.md` Decision 3), never in
`src/retail/`.

### `ContainerHandle` (conceptual)
- `dsn: str` -- the ephemeral container's connection string, valid only for the container's
  lifetime; never logged/printed unredacted (Safety Constraints).
- `ready: bool` -- whether the readiness wait succeeded within the bounded timeout.
- `failure_reason: str | None` -- one of a small closed set of honest reasons: `"docker not
  available"`, `"container failed to start"`, `"port conflict"`, `"seed failed"`, `"driver not
  installed"`. Exactly one of `ready` / `failure_reason` is meaningful at a time.

### `ScenarioOutcome` (conceptual)
- `mode: Literal["live", "skipped"]` -- never a third value (FR-008).
- `findings: list[Finding] | None` -- populated only when `mode == "live"`; the real
  `run_live_checks`/`check_expected_value` output, unmodified.
- `skip_reason: str | None` -- populated only when `mode == "skipped"`, one of the
  `ContainerHandle.failure_reason` values or `"seed failed"` / a scenario-specific seed error.
- Invariant enforced by construction (a wiring test asserts this, `tasks.md`): `mode == "live"`
  implies `skip_reason is None`; `mode == "skipped"` implies `findings is None`. This is the
  data-shape expression of FR-009 (no hidden live pass) -- there is no field combination that can
  represent "reported live pass but nothing actually ran."

### Relationship to existing entities (unmodified, referenced only)
- `retail.core.Finding` (frozen dataclass: `rule_id`, `severity`, `message`, `locator`) --
  produced by `validate.py`/`value_proxy.py`, consumed as-is by `ScenarioOutcome.findings`.
  This feature adds no new field to `Finding` and no subclass.
- `retail.validate.QueryRunner` (Protocol) -- the real `psycopg2`-backed implementation
  (`make_psycopg2_runner`) is what the harness must point at the ephemeral container's DSN; the
  harness never re-implements or wraps this Protocol.
- `retail.readiness_evidence.build_gold_ready_block` -- called once (User Story 1, FR-007) with
  a `live` scenario's real findings, to demonstrate the seam; its return value is inspected by a
  test assertion, never written to any file.

## 4. What is explicitly NOT modeled here

- No per-table `source-map.yaml`-driven target loading (`retail.validate_targets`) -- the seed
  schema's table/column names are hardcoded generic constants for this suite's own fixtures, not
  loaded from a mapping artifact (Non-Goals in `spec.md`).
- No readiness-status.yaml write path -- `ScenarioOutcome` and `build_gold_ready_block`'s return
  value are both in-memory/test-assertion only.
- No numeric confidence/score field anywhere in `ScenarioOutcome` or the seed data -- consistent
  with the readiness spine's "no fake confidence" rule.
