# Quickstart: Local Demo Harness

This walks through the demo as it is SPECIFIED to behave once built. It is a
design-time walkthrough for review, not a record of a run against real code
(no implementation exists yet as of this spec-work phase).

## Prerequisites

- A clone of the repo with the base dev install:
  `pip install -e ".[dev]"` (no `db` extra required for the offline path).
- No `.env`, no DSN, no Postgres required for User Story 1 (the primary path).
- Optional, for User Story 2 only: a reachable local/disposable Postgres and
  a DSN in a git-ignored `.env` (`DATABASE_URL` or `ANALYTICS_DB_*`), plus
  `pip install -e ".[dev,db]"`.

## Path A -- Offline (User Story 1, the primary path)

```bash
# 1. Materialize the committed sample fixtures into a git-ignored working area.
retail demo init

# 2. "Load" the sample. With no DSN configured, this reports the live leg
#    as skipped and why -- it does not error.
retail demo load

# 3. Recompute readiness for the sample table from committed artifacts +
#    retail check (no DB leg attempted -- none is configured).
retail demo run

# 4. Render the status/evidence/blockers report.
retail demo report
```

**Expected `demo report` shape (illustrative, not literal output):**

```text
Demo sample: demo_sample_orders (bronze.demo_sample_orders)

  1. Source Ready     -- pass     (evidence: source-profile.md, grain ratio 1.00;
                                     source_kind: csv -> encoding-confirmation
                                     approval is an illustrative fixture,
                                     pre-committed with the sample [RS1] -- see
                                     note below)
  2. Mapping Ready     -- pass     (evidence: source-map.yaml, gate CLEARED;
                                     mapping_ready approval is an illustrative
                                     fixture, pre-committed with the sample --
                                     see note below)
  3. Silver Ready      -- pass     (evidence: the committed silver migration
                                     fixture; retail check S1-S7 exit 0 --
                                     silver-ready.md's "authoring only" gate is
                                     static, so this is honestly reachable offline)
  4. Gold Ready        -- blocked  (deferred: live retail validate not run -- no
                                     DSN; this is the honest offline ceiling)
  5. Semantic Model Ready -- not_started (prior stage not pass)
  6. Dashboard Ready   -- not_started (prior stage not pass)
  7. Publish Ready     -- not_started (prior stage not pass)

Note: the source_ready and mapping_ready entries above are ILLUSTRATIVE
approval fixtures pre-committed with the sample -- NOT produced by this run.
No demo verb ever mints an approval.

Next action: configure a local Postgres DSN and re-run `retail demo load`
to exercise the live leg (see: 082-postgres-live-validation-suite), or read
docs/worked-examples/retail-store-sales.md for the full narrative on real data.

No numeric score is shown -- readiness is status + evidence + blockers only.
```

**What to verify (per the spec's acceptance scenarios):**

- `git status` is clean after all four commands (FR-010, SC-004).
- No network call was made at any point (User Story 1, Safety Constraints).
- Source/Mapping/Silver Ready show `pass` (Source/Mapping citing shipped
  labeled approval fixtures, Silver citing static `retail check`); Gold Ready
  and stages 5-7 never show `pass` (SC-002) -- they show `blocked`/`not_started`
  with a named reason, not a bare "not ready."
- No numeric score anywhere in the output (FR-006, SC-005).

## Path B -- With a local Postgres (User Story 2)

```bash
# Prerequisite: DATABASE_URL or ANALYTICS_DB_* set in a git-ignored .env,
# pointing at a local/disposable Postgres (e.g. the 082 live-validation
# harness, or any Postgres you control).

retail demo init
retail demo load     # now also materializes rows into the DB, using
                      # demo-scoped object names (e.g. a `demo_` marker)
                      # so it cannot collide with real schema objects
retail demo run       # now also runs the live leg (retail validate) against
                      # those demo-scoped objects
retail demo report
```

**Expected difference from Path A:** Gold Ready reaches `pass`, citing the
actual `retail validate` findings (PK uniqueness, 0 orphan FKs, penny-exact
reconciliation on the tiny sample) -- never a fabricated pass. Semantic Model
Ready and beyond remain honestly blocked on the named human-approval seam
(FR-007), UNLESS the sample ships the optional illustrative approval fixture
(User Story 3), in which case Semantic Model Ready may show `pass` but
**labeled** as resting on a pre-committed illustrative fixture, not something
this run produced.

**What to verify (in addition to Path A's checks):**

- `demo load`'s live-leg objects carry the demo-scoped naming marker (FR-011)
  -- inspect the target schema and confirm no name collides with
  `retail_store_sales`'s `_rss`-suffixed objects or any real client table.
- Re-running `demo load` a second time converges to the same row state
  (idempotent, FR-004) rather than duplicating rows or erroring.
- If the DSN is unset again after a successful load (simulating "DB went
  away"), `demo run` reports `gold_ready` as `pending` with the concrete
  reason, not a crash and not a stale cached `pass`.

## Path C -- Cold start (edge case)

```bash
# Fresh clone, nothing done yet.
retail demo report
```

**Expected**: renders a report with every stage `not_started` and
`next_action` pointing at `retail demo init` -- it does not error just because
`init`/`load`/`run` were never called.

## Reading further

- The full narrative on real (Kaggle) data: `docs/worked-examples/retail-store-sales.md`.
- The curated reading-path tour of that same worked example:
  `docs/demo/retail-store-sales-demo.md`.
- The readiness spine model this demo traverses honestly:
  `docs/readiness/readiness-model.md`.
- The sibling local-Postgres harness Path B optionally sits on top of:
  `082-postgres-live-validation-suite` (once its spec exists / merges).

This quickstart intentionally does NOT show a dashboard, a Power BI screen, or
any visual -- `demo report` is a status/evidence/blockers artifact only
(FR-013, Non-Goals).
