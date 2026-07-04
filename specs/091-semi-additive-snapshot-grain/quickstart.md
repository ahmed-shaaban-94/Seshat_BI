# Quickstart: Semi-Additive (Snapshot) Grain in the Metric Contract

**Feature**: 091-semi-additive-snapshot-grain | **Date**: 2026-07-04

This walks through exercising HR5 once built: authoring a `time_additivity`
declaration on a metric contract, seeing HR5 fire and clear, and confirming
the rule is fully wired. All commands assume a repo root working directory
and the existing `retail` CLI already installed (matching how AL1/AD1 are
exercised today).

## 1. Author (or edit) a metric contract with the new field

Copy `templates/metric-contract.yaml` (or open an existing filled contract
under `mappings/<table>/metrics/<MetricName>.yaml`) and, if the metric is a
snapshot-grain fact (the canonical example is inventory on-hand quantity --
see `skills/retail-kpi-knowledge/knowledge/kpi-ambiguities.md`, A10), record
the trap in the existing ledger and declare the new field:

```yaml
ambiguities:
  - id: A10
    decision_status: undecided
    ruling: ""
    evidence: []
    number_moving: true

time_additivity: "semi"   # or "non"; never "fully" on an A10-flagged contract
```

If the metric is a normal transaction measure (the current committed
corpus), do nothing -- `time_additivity` stays absent and HR5 will not ask
for it (FR-007).

## 2. Run the static check

```powershell
retail check
```

or, to see only HR5's findings while iterating:

```powershell
retail check | Select-String "HR5"
```

**Expected on the current committed corpus (no A10 entries anywhere):**
zero HR5 findings (SC-001) -- the check's overall exit code is unaffected by
this feature until a contract actually carries an A10 entry.

## 3. Exercise each fixture scenario (mirrors the spec's Independent Tests)

Author a throwaway fixture contract (e.g. under a `tests/`-marked path, which
HR5 exempts from its normal scan the same way AL1/AD1 do, or use the rule's
own unit-test fixtures once the rule module exists) and confirm each row of
`data-model.md`'s decision table:

1. **Missing declaration** -- A10 entry present, `time_additivity` absent:
   `retail check` emits exactly one HR5 ERROR naming the fixture and stating
   the missing date-axis declaration.
2. **Illegal `fully`** -- same fixture, add `time_additivity: fully`: HR5
   still ERRORs (a snapshot contract can never validly declare full
   additivity over time), with a message distinguishable from (1).
3. **Clears** -- same fixture, set `time_additivity: semi` (or `non`): the
   finding disappears -- zero HR5 findings for that contract.
4. **Out-of-vocabulary** -- an A10-flagged fixture with
   `time_additivity: "sometimes"` (or a case/whitespace variant like
   `"Fully"`, or a non-scalar YAML list): HR5 ERRORs that the value is
   unrecognized, with a message distinguishable from (1)/(2), and does not
   crash on the non-scalar case.
5. **Not flagged, not required** -- a fixture with no A10 entry and no
   `time_additivity` field: zero findings.
6. **Volunteered early** -- a fixture with no A10 entry but a valid
   `time_additivity` value present anyway: zero findings (the field is
   validated when present, never required when absent and never flagged).
7. **Unreadable file** -- a tracked contract path that cannot be read/parsed:
   HR5 fails loud with an ERROR naming the path (never a silent skip).

## 4. Confirm the wiring (mirrors the shipped AL1/AD1 wiring checklist)

```powershell
pytest tests/unit/test_rules_wiring.py -m unit
```

Expected: `test_registered_rule_ids_match_expected_set` passes with `HR5`
included in `EXPECTED_RULE_IDS`, and the manifest count
(`docs/rules/rules-manifest.json`, regenerated via `retail manifest`) equals
`len(EXPECTED_RULE_IDS)`.

```powershell
pytest tests/unit/test_snapshot_time_additivity.py -m unit
```

Expected: one passing test per row of the data-model decision table.

## 5. What this quickstart deliberately does NOT do

- It does not open Power BI Desktop, call the Power BI execution adapter, or
  touch any `.pbip`/`.SemanticModel`/`.Report` path -- HR5 has no relationship
  to that surface (F016 remains gated and unbuilt).
- It does not connect to a database -- every step above reads only committed
  repository text.
- It does not decide what value `time_additivity` should be for any real
  metric -- that is a named human owner's call (Principle V); this quickstart
  only shows the mechanics of declaring and checking it.
- It does not attempt to answer FR-018/Clarifications Q4 (whether the
  trigger should ever widen beyond A10) -- that remains an OPEN owner
  ruling, out of scope for exercising this build.
