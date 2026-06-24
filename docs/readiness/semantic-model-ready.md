# Semantic Model Ready

Status note: Planning (docs/templates; no runtime code).

## Purpose

Stage 5. A governed Power BI semantic model whose measures each bind to an
APPROVED metric contract. "Ready" means: the PBIP model is committed and clean
(relationships set, date table marked, PascalCase measures in display folders,
parameterized connection with NO real host), `retail check` passes the DAX/TMDL
+ connection rules, and every measure traces to a metric contract owned by the
metric owner. Maps to playbook Phase 7 (the model half, before any dashboard).

## Required artifacts

| Artifact | Where | Must show |
|----------|-------|-----------|
| PBIP model | `powerbi/<Model>.SemanticModel/definition/` | relationships, date table marked, PascalCase measures in display folders |
| Connection params | model expressions/parameters | parameterized host -- NO real host string (G6) |
| Metric contracts | feature 009/010 artifact (F009/F010) | per measure: name, grain, formula intent, owner |

Note: metric-contract artifacts (F009/F010) are PLANNED, not yet built. Until
they exist, this stage is `not_started` for any new table -- there is nothing for
a measure to bind to. (C086 is the first worked example / a filled instance, not
the schema.)

## Required checks

| Gate | Scope | Pass condition |
|------|-------|----------------|
| `retail check` | D1-D8 (DAX/TMDL), C1 (connection params), R1 (relative ref), G6 (no real host) | exit 0 |
| Metric-contract review | every measure | each measure traces to an approved contract |

## Statuses

| Status | Meaning HERE |
|--------|--------------|
| `not_started` | Gold not `pass`, OR no metric contracts exist yet (F009/F010 unbuilt) -- default for new tables |
| `blocked` | a D/C/R/G6 finding, a measure with no contract, or a real host in PBIP params (G6) -- see Blocking reasons |
| `warning` | `retail check` clean but a non-fatal item recorded (e.g. an accepted display-folder deviation); never auto-promotes |
| `pass` | model committed + clean, `retail check` exit 0, every measure traces to an approved contract, owner signed off |

## Blocking reasons

- Prior stage `gold_ready` is not `pass` (gold star / live validation incomplete).
- A `retail check` D1-D8 DAX/TMDL finding.
- A C1 connection-parameter finding or R1 relative-reference finding.
- G6: a real connection host baked into PBIP params (must be parameterized).
- A measure with no corresponding metric contract.
- Metric contracts (F009/F010) do not exist yet -> stays `not_started`/`blocked`.

## Required owner / approval

Metric owner approves the metric contracts. A `pass` records that approval as
evidence (contract name + owner + date). Mechanical checks (`retail check`) need
no human; the contract binding does.

## Next allowed action

When this stage is `pass`: proceed to Stage 6 -- design the dashboard against the
approved contracts (`dashboard-ready.md`).

## What the agent must NOT do

- Do NOT design dashboards or visuals yet (that is Stage 6).
- Do NOT author a measure that has no metric contract.
- Do NOT commit a real connection host -- keep PBIP params parameterized (G6).
- Do NOT write a `pass` without owner-approved contracts as evidence.
- Do NOT run pbi-cli/PBIP automation before this stage is `pass`.

## See also

- The state model: `readiness-model.md`
- The stage sequence + hard gates: `readiness-pipeline.md`
- The committed model: `../../powerbi/Retailgold.SemanticModel/definition/model.tmdl`
- Playbook Phase 7 + conventions: `../conventions.md`
