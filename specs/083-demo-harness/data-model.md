# Data Model: Local Demo Harness

Phase 1 output. This describes the SHAPE of the demo's sample dataset and its
supporting artifacts. **Nothing in this document is created by this spec-work
phase** -- no CSV, no fixture file, no YAML is written here. Creating the
actual sample data file(s) is implementation work for a later, separately
authorized pass (tasks.md enumerates it as a build task).

## Entity: `demo_sample_orders` (working name, TBD at implementation time)

An invented, generic small retail transaction dataset -- a fictional small
store's order lines. Chosen to be structurally recognizable (same *kind* of
grain as `retail_store_sales`: one transaction/order line) without reusing any
of its actual field names, values, or scale (see `research.md` R1).

### Bronze shape (landed, all-TEXT, faithful-as-landed per RC1/RC7 discipline)

| Column (invented name, TBD) | Kind | Notes |
|---|---|---|
| `order_id` | degenerate-dim candidate / grain key | invented alphanumeric id, e.g. `ORD-000123`-shaped; target: unique per row (grain ratio 1.00, mirroring the worked example's discipline of measuring, not assuming, uniqueness) |
| `order_date` | date | plain `YYYY-MM-DD` text as landed |
| `product_name` | dimension attribute | a small invented product vocabulary (a few dozen distinct values), NOT any real brand or C086 product |
| `product_category` | dimension attribute | a handful of invented category values, 1:1 or near-1:1 with `product_name` (mirrors the worked example's measured item<->category 1:1 check) |
| `quantity` | measure (integer) | small positive integers |
| `unit_price` | measure (money) | small positive decimal values, invented currency-neutral amounts |
| `line_total` | measure (money) | `quantity * unit_price`, to exercise the same "identity holds on N% of rows" profiling check the worked example performs on `total_spent` |
| `store_location` | dimension attribute | a small invented set of generic location labels (e.g. "North", "South", "Online") -- deliberately NOT real city/branch names tied to any client |
| `payment_method` | dimension attribute | a small invented set (e.g. "card", "cash", "voucher") |

**Deliberately excluded from this sample** (kept out to keep the demo small
and avoid recreating judgment calls the worked example already demonstrates):
no customer-identifying column (no PII deviation question to re-litigate),
no returns/discount flag (keeps the RC8/RC4-style deviation story out of scope
for a *small* demo -- the worked example remains the reference for those
richer judgment calls).

### Mapping-gate artifacts (pre-filled, pre-reviewed fixtures)

Per Principle IV, silver is never built before a reviewed map exists. For this
sample, the five mapping-gate artifacts are **authored once, by a human, as
part of building this feature** (an implementation-time act reviewed like any
other committed artifact) -- never invented at `demo run` time:

- `source-profile.md` -- row count, column list, measured grain ratio (target
  1.00 on `order_id`), measured `line_total == quantity * unit_price` rate.
- `source-map.yaml` -- grain = one order line; PK = `order_id` (degenerate
  dim); gold star placement for each column (fact measure vs. dimension
  attribute); RC defaults adopted (see below).
- `assumptions.md` -- records which RC defaults (RC1-RC16) were adopted as-is
  for this sample (expected: nearly all adopted as-is, since the sample is
  deliberately simple -- no PII, no returns, no sentinel judgment calls to
  deviate on). Any deviation, if one turns out to be needed, MUST cite its
  triggering data fact per Principle VI.
- `unresolved-questions.md` -- expected to close with Gate status: CLEARED,
  since the sample is authored to have no open judgment call by design (it
  exists to demonstrate the *mechanism*, not to showcase a hard judgment
  call -- that role stays with the worked example).
- `readiness-status.yaml` -- the demo sample's own per-stage record, in the
  same shape as `templates/readiness-status.yaml` / `mappings/retail_store_sales/readiness-status.yaml`,
  but scoped to this sample table and never a tracked file the demo *run*
  itself mutates (FR-008/FR-010) -- it exists as a committed starting fixture,
  and `demo run`/`report` render a **derived, git-ignored** working view, not
  edits to this tracked file. Because the sample is a CSV file source, this
  fixture MUST declare `source_kind: csv` in its `source_ready` block and MUST
  carry (FR-017) the two mandatory pre-committed illustrative approval entries
  in `approvals[]`: a `{stage: source_ready}` encoding-confirmation approval
  (required by rule RS1 for a file source's `source_ready: pass`) and a
  `{stage: mapping_ready}` gate approval (required for Mapping Ready to read
  `pass`). Each `owner` is a fictional named human + authority class (e.g.
  `"Jordan Rivera (analyst)"`) and each is labeled illustrative per FR-016.
  Without them, `retail check` fails RS1 on the committed fixture and Mapping
  Ready cannot honestly show `pass`.

### Silver / gold shape (silver migration committed as a Foundational fixture; gold built with the live leg)

The **silver migration `.sql` is a committed Foundational fixture** (not
deferred to the live-leg story), because Silver Ready's gate is "authoring
only" (`docs/readiness/silver-ready.md`): `retail check` (S1-S7) exit 0 over
the committed migration + a Phase-5-order self-review, with no owner approval.
Shipping the migration fixture is what lets `silver_ready` reach `pass`
OFFLINE (User Story 1). Applying it to a database is the deferred DB-write
seam handled by the live leg (User Story 2), NOT a Silver Ready requirement.

- **Silver**: one typed/cleaned table at order-line grain, `NULLIF('','')`
  cleanup, `NUMERIC` money/qty types, `order_id` kept TEXT (RC7).
- **Gold**: one fact (`fct_orders_demo`-shaped name, exact naming TBD) at
  order-line grain + a small number of dimension tables
  (`dim_product_demo`, `dim_location_demo`, `dim_payment_method_demo`,
  `dim_date_demo`), each carrying a `-1` unknown member per RC14, sharing
  naming with a demo-scoped marker (see `research.md` R4) so it can safely
  coexist with `retail_store_sales`'s `_rss`-suffixed objects and any real
  client schema in the same Postgres instance.

## Entity: Demo working directory

A single git-ignored directory (exact path TBD at implementation time, e.g.
`.demo-work/` or similar, chosen to be unambiguous and easy to add to
`.gitignore`) where:

- `demo init` copies/materializes the committed fixture rows into a working
  copy (so `demo load` never mutates the committed fixture itself).
- `demo load` writes its offline "load summary" (rows counted, idempotency
  check) or, in the live-DB case, records the DSN it loaded into
  (host/DB name only -- never a full DSN with credentials, per Principle IX).
- `demo run` writes its last-computed per-stage status snapshot, which
  `demo report` reads by default (falling back to computing the offline-only
  legs itself if no snapshot exists yet -- see `contracts/demo-report-contract.md`).

This directory is **never** committed and **never** contains a real credential
(FR-010, FR-014).

## Entity: Illustrative approval fixtures

Pre-committed, clearly-labeled `approvals[]` entries (each a fictional named
owner + authority class + fictional date) shipped in the sample's
`readiness-status.yaml` fixture. THREE positions matter:

- **`source_ready` approval (MANDATORY)**: RS1 requires it for a CSV file
  source's `source_ready: pass` (see the `readiness-status.yaml` entry above).
- **`mapping_ready` approval (MANDATORY)**: required for Mapping Ready to read
  `pass` (`docs/readiness/mapping-ready.md`).
- **`semantic_model_ready` approval (OPTIONAL, User Story 3)**: shipped only
  to illustrate what a `pass` looks like one stage past the offline/live
  ceiling (Gold Ready). Its absence does not block User Stories 1 or 2.

Every one MUST be labeled, in both the fixture file (a comment) and wherever
`demo report` renders it, as "illustrative fixture, pre-committed with the
sample -- not produced by this run" (FR-016). NO demo verb ever mints any of
them (FR-008).

## Relationships

```text
demo_sample_orders (bronze, invented CSV)
        |
        v  (Mapping Ready gate: source-profile.md, source-map.yaml,
        |   assumptions.md, unresolved-questions.md -- pre-filled fixtures)
        v
silver.demo_sample_orders_demo (described; built at implementation time)
        |
        v  (Gold Ready gate: retail validate, live leg only)
        v
gold.fct_orders_demo + dim_*_demo (described; built at implementation time)
        |
        v  (Semantic Model Ready: illustrative-only beyond this point,
        |   per the optional fixture above -- never actually reached by
        |   a live `demo run`)
        v
[not reached by this feature's own live leg -- named as the next honest
 blocker, per FR-007]
```

## Non-created artifacts (explicit inventory, per the SPEC-WORK-ONLY boundary)

None of the following are created by this spec/plan/tasks/analyze chain; they
are described here for a future implementation pass to author:

- The invented sample CSV (or equivalent flat file) itself.
- `mappings/demo_sample_orders/` (or final chosen name) and its five
  mapping-gate artifacts.
- Any `silver.*` / `gold.*` migration SQL for the demo sample.
- The `src/retail/demo/` subpackage and its CLI wiring in `src/retail/cli.py`.
- `docs/demo/demo-harness.md` (or final chosen doc path).
- Any test fixtures under `tests/unit/` for the above.
