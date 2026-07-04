# Quickstart: Cross-Star Conformed-Dimension Readiness Gate

How an agent or developer exercises HR1 once it is implemented. This is a
walkthrough of the INTENDED usage, not an implementation guide -- it assumes
`src/retail/rules/rule_hr1.py` and `docs/quality/conformed-dimension-map.yaml`
already exist per plan.md / data-model.md. All names below (`dim_product`,
`star_a`, `star_b`) are illustrative placeholders (Principle VII).

## 0. Preconditions

- Two or more tables already have an approved `mappings/<table>/
  source-map.yaml` with a `gold_star.fact` (i.e. two or more stars exist).
  With zero or one star, HR1 is a no-op -- there is nothing to exercise
  yet (US3).
- `docs/quality/conformed-dimension-map.yaml` exists as a tracked file (it
  may be an empty-but-present scaffold: `dimensions: {}`). If it is
  missing while 2+ stars exist, `retail check` already fails on FR-010 --
  that IS an exercise of the gate (see step 3 below), not a blocker to
  reading this quickstart.

## 1. Run the gate as-is (no manifest entries yet)

```
retail check
```

- If 2+ stars share NO dimension name at all: HR1 emits no Finding (there is
  nothing to adjudicate).
- If 2+ stars DO share a dimension name and it is not yet declared: HR1
  emits exactly one ERROR naming the dimension and every star carrying it,
  instructing a human to declare it `conformed` or `distinct` (US2, FR-006).
  This is the expected, correct failure mode on a fresh multi-star tree --
  it is not a bug in HR1, it is the gate doing its job.

## 2. A human declares the shared dimension (Principle V -- the agent does not do this)

A named human edits `docs/quality/conformed-dimension-map.yaml` and adds an
entry. Two illustrative outcomes:

**Outcome A -- the human rules it genuinely conformed:**

```yaml
dimensions:
  dim_product:
    status: conformed
    stars:
      - star_a
      - star_b
```

**Outcome B -- the human rules the two same-named dims are NOT one dimension:**

```yaml
dimensions:
  dim_product:
    status: distinct
    stars:
      - star_a
      - star_b
```

The agent's role here is limited to: (a) surfacing the undeclared-collision
Finding from step 1 so the human knows a ruling is needed, and (b) at the
human's explicit instruction, scaffolding the empty `dimensions: {}` shape
when there is nothing yet to adjudicate. The agent never picks `conformed`
vs `distinct` and never fills in the `stars:` list on its own judgment.

## 3. Re-run the gate after the declaration

```
retail check
```

- **Outcome A (`conformed`) and the stars genuinely agree** on surrogate key
  and every Kimball conformed-subset attribute's silver type: no Finding for
  `dim_product` (SC-001).
- **Outcome A (`conformed`) but the stars actually disagree** -- e.g.
  `star_a`'s `dim_product` surrogate key is `product_sk` while `star_b`'s is
  `prod_key`, or a shared attribute's silver type differs (`text` vs.
  `integer`): HR1 emits one ERROR naming the dimension, both stars, and
  exactly what diverged (SC-002, US1 scenarios 1-2). This is a proven
  modelling defect -- the fix is either to align the two stars' shapes in a
  future source-mapping-gate edit, or for the human to re-rule the entry
  `distinct` if the two dims are not actually meant to be the same.
- **Outcome B (`distinct`)**: no ERROR regardless of shape differences
  (US2 scenario 3, FR-008). The copies may legitimately differ.

## 4. Exercise the WARNING (surface, never block) cases

- **Stale entry**: remove or rename the second star's `dim_product` (or
  drop it below 2 surviving stars) while the manifest still declares it.
  `retail check` now emits a WARNING (not an ERROR) telling the human the
  entry no longer names a live cross-star collision and should be removed
  (FR-009). Unrelated work is not blocked.
- **Moot `distinct`**: if a `distinct`-declared pair's stars later become
  identical in every compared limb, `retail check` emits a WARNING
  suggesting the human consider promoting it to `conformed` (or leaving it,
  their call) -- HR1 never auto-promotes or auto-merges (Edge Cases,
  scope guard).

## 5. Exercise the missing/malformed manifest case

- Delete `docs/quality/conformed-dimension-map.yaml` entirely while 2+ stars
  exist: `retail check` emits one ERROR naming the missing file (FR-010).
- Set a `status` to something other than `conformed`/`distinct` (e.g.
  `status: partial`), or list a `stars:` entry whose `source-map.yaml`
  cannot be found: `retail check` emits one ERROR naming the offending entry
  (FR-010). An unrecognized value is never silently treated as a valid
  ruling.

## 6. Confirm the model-level tier is orthogonal to the per-table spine

- Inspect any `mappings/<table>/readiness-status.yaml`: HR1's outcome is
  NOT written there, and no eighth stage key appears (FR-001). The
  model-level conformance tier is a separate axis from the seven-stage
  per-table pipeline; a table can be Gold Ready while the MODEL still has
  an open HR1 Finding, and vice versa.
- Where (if anywhere) a clean HR1 run is recorded as a model-level "pass" is
  OPEN (FR-016, Q-APPROVAL-SEAM) pending an owner ruling. Until that ruling,
  a clean `retail check` run (zero HR1 Findings) is the only observable
  signal -- there is no `approvals[]`-style artifact to inspect for this
  tier yet.

## 7. Confirm the categorical-only output (hard rule #9)

At every step above, `retail check --format json` (or the default text
output) shows HR1 Findings with `rule_id`, `severity`, `message`, `locator`
only -- never a percentage, a ratio, a "N of M conformed" tally, or any
other numeric confidence/health/maturity score. This is checkable by reading
the Finding payload directly; no separate tool is needed to verify SC-005.

## 8. Confirm no live surface was touched

None of the steps above require a database connection, a Power BI Desktop
session, or network access. `retail check` running HR1 exits deterministically
from committed text alone (Principle VIII) -- this is directly observable by
running it offline.
