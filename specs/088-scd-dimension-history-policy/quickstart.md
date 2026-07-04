# Quickstart: Dimension History / SCD Policy Readiness

How an agent or developer exercises HR2 once it is implemented. This is a walkthrough of the
INTENDED usage, not an implementation guide -- it assumes `src/retail/rules/rule_hr2.py` and
the `scd_type` key on `templates/source-map.yaml` already exist per plan.md / data-model.md.
All names below (`dim_product`, `example_table`) are illustrative placeholders (Principle VII).

## 0. Preconditions

- A table has an approved `mappings/<table>/source-map.yaml` with a `gold_star.dimensions[]`
  block (Mapping Ready, Stage 2, already reviewed).
- HR2's declaration limb (US1/US3) can run at Mapping Ready time, before any gold migration
  exists. Its build-honors-declaration limb (US2) additionally needs a gold migration file
  present to inspect (Gold Ready, Stage 4).

## 1. Run the gate on a table with no `scd_type` declared yet (the adoption case)

```
retail check
```

- Every `gold_star.dimensions[]` entry with no `scd_type` key emits exactly ONE Needs-decision
  ERROR naming that dimension (FR-005, US3). This fires even on a table whose Mapping Ready
  approval predates this feature -- there is no grandfather exemption (Principle I fails
  closed by design).
- **This is the expected first outcome on the current committed tree.** Both
  `mappings/retail_store_sales/source-map.yaml` and `mappings/demo_sample_orders/
  source-map.yaml` have dimensions with no `scd_type` today; landing HR2 makes `retail check`
  fail RED on this repo until a human resolves each finding (research.md "Landing
  precondition"). This is not a bug in HR2 -- it is the gate doing its job.

## 2. A human declares each dimension's history policy (Principle V -- the agent does not do this)

A named human edits `mappings/<table>/source-map.yaml` and adds `scd_type` to each dimension
entry, next to its `surrogate_key` / `has_unknown_member`:

```yaml
gold_star:
  dimensions:
    - name: "dim_product"
      surrogate_key: "product_sk"
      has_unknown_member: true
      scd_type: "type_1"     # overwrite -- the default, matches drop-and-rebuild
      attributes: ["product_id", "category"]

    - name: "dim_customer"
      surrogate_key: "customer_sk"
      has_unknown_member: true
      scd_type: "type_2"     # historized -- changes must be preserved as dated rows
      attributes: ["customer_id", "region"]
```

The agent's role here is limited to surfacing the Needs-decision Finding from step 1 so the
human knows a ruling is needed. The agent never fills in `type_1` or `type_2` on its own --
not even as a "safe default" -- because that would silently reproduce the exact
implicit-Type-1-by-omission gap this feature exists to close, one layer higher.

## 3. Re-run the gate after the declaration

```
retail check
```

- Every dimension now carrying a valid `scd_type` (`type_1` or `type_2`) clears its
  Needs-decision finding (US3 AS3).
- A `type_1` dimension produces no HR2 finding regardless of how its migration is built
  (FR-009) -- drop-and-rebuild is the correct, honored mechanism for an overwrite policy.
- A `type_2` dimension with NO gold migration yet also produces no finding for the
  build-honors-declaration limb (FR-008) -- HR2 never fabricates a pass or fail about SQL
  that does not exist.

## 4. Exercise the build-honors-declaration check (US2, the MVP enforcement)

Once a gold migration exists for the table (authored by `retail-build-warehouse`, per
`.claude/skills/retail-build-warehouse/SKILL.md`), re-run:

```
retail check
```

- **If a `type_2`-declared dimension's own gold table is built by the documented
  drop-and-rebuild construct** -- a `DROP TABLE IF EXISTS <dim_table>` paired, same file,
  with a `CREATE TABLE <dim_table>` that recreates it (either CTAS or explicit DDL plus
  `INSERT`, not required to be textually adjacent) -- HR2 emits ONE fail-closed ERROR naming
  the dimension and the migration file (FR-007, US2 AS1). This is the feature's whole point:
  the declared policy (preserve history) cannot be honored by a build regime that discards
  prior attribute values on every re-run.
- **If the same table has every dimension declared `type_1`**, no finding fires for the
  build limb (US2 AS2) -- the same drop-and-rebuild construct is the CORRECT mechanism for
  an overwrite policy.
- **A `type_1` dimension's drop-and-rebuild elsewhere in the same file never fires against
  an unrelated `type_2` dimension** -- the match is scoped to each dimension's OWN gold
  table by name (with an optional `<schema>.` prefix stripped from both sides before
  comparing, per research.md C4).

## 5. Exercise the invalid-value case

Set a dimension's `scd_type` to anything other than `type_1` or `type_2` (e.g.
`scd_type: "type_3"` or `scd_type: "historized"`):

```
retail check
```

HR2 emits one fail-closed ERROR naming the dimension and the invalid value seen (FR-006,
US1 AS3). An unrecognized value is never silently treated as a valid ruling and never
defaults to `type_1`.

## 6. Confirm the categorical-only output (hard rule #9)

At every step above, `retail check --format json` (or the default text output) shows HR2
findings with `rule_id`, `severity`, `message`, `locator` only -- never a percentage, a
ratio, a completeness count, or any other numeric confidence/health/maturity score. This is
directly checkable by reading the Finding payload; no separate tool is needed to verify
SC-006.

## 7. Confirm no live surface was touched

None of the steps above require a database connection, SQL execution, a Power BI Desktop
session, or network access. `retail check` running HR2 exits deterministically from
committed text alone (Principle VIII) -- both the `source-map.yaml` declaration and the
gold migration SQL are read as TEXT, never parsed as an executable statement or run against
Postgres. This is directly observable by running `retail check` offline.

## 8. Confirm the scope boundary against neighbouring gates

- Inspect `gold_star.degenerate_dimensions[]` and `gold_star.date_dimension` on any table's
  `source-map.yaml`: HR2 never reads or requires `scd_type` on either (FR-010, Edge Cases) --
  a degenerate dimension has no separate table to historize, and a generated append-only
  date dimension has no changing attribute in the SCD sense.
- Run `retail check` on a table whose gold star also has an HR1 finding (spec 087, once
  shipped): HR2 and HR1 read entirely different declarations (`scd_type` on the dimension
  entry vs. the separate `conformed-dimension-map.yaml`) and neither rule's finding affects
  the other's outcome -- they are orthogonal axes on the same `gold_star.dimensions[]`
  surface.
- Confirm S6 (`-1` unknown member) and S7 (contiguous date dim) still pass or fail
  independently of HR2 -- a table can be `pass` on S6/S7/live-validate while HR2 reports its
  own, separate finding, and vice versa.
