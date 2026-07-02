# Data Model: Approval Evidence Pack for the Named-Human Stage Gate

There is no database and no runtime code. This document models the SHAPE of the generated
pack and the READ-source field map it composes from. All shapes are Markdown/YAML text.

## Entities

### ApprovalEvidencePack (the derived artifact this feature writes)

The ordered document written to `mappings/<table>/approval-evidence-pack-<stage>.md`
(FR-018). Owns no truth; carries an empty approval slot; carries no score.

| Field | Source | Rule |
|-------|--------|------|
| table | invocation parameter | identity |
| stage | invocation parameter (one of 7 stage keys) | selects sources |
| generated_at | authoring time | quoted date, ASCII |
| source_list | the paths actually read | every claim traceable (SC-002) |
| gate_requirements | `docs/readiness/<stage>-ready.md` | summarised/linked, not re-authored |
| readiness_states[] | `readiness-status.yaml` selected + prior stages | verbatim status; never later stages (FR-020) |
| open_blockers[] | `blocking_reasons[]` per stage + cross-cutting | each traceable (FR-005) |
| unresolved_assumptions[] | AL1 signal per `metrics/<Metric>.yaml` | per-contract (FR-021); never resolved |
| blocking_parked_on[] | `docs/quality/parked-on.yaml` | edge blocker/doc/evidence (FR-007) |
| pending_contracts[] | OPEN (FR-008) | definition is a Principle-V human ruling |
| approval_slot | none (empty) OR recorded (read-only) OR N/A | see ApprovalSlot below |

NO field is a numeric confidence/health/maturity value; NO field is a completeness count
(FR-012).

### ReadinessStateRow (read-only, one per surfaced stage)

`{ stage_key, status in {not_started|blocked|warning|pass}, evidence[], blocking_reasons[] }`
-- read verbatim from `mappings/<table>/readiness-status.yaml`. Never written.

### AssumptionSignalItem (read-only, per offending contract)

`{ contract_path (mappings/<table>/metrics/<Metric>.yaml), recorded_contradiction }` -- the
AL1 result surfaced per contract. The pack never resolves it (Principle V).

### ParkedOnEdge (read-only)

`{ id, blocked, parked_on, doc, evidence }` from `docs/quality/parked-on.yaml`. Surfaced only
when the edge blocks this table's stage.

### ApprovalSlot (the terminal section -- exactly one of three forms)

- **Empty slot** -- the selected stage is an approval gate and `approvals[]` has no entry for
  it: render an empty `{ stage, owner: <blank>, at: <blank> }` for the named human to fill.
  The module cannot fill it (FR-009).
- **Recorded (read-only)** -- `approvals[]` already has an entry for this stage: surface
  `{ stage, owner, at }` from source, no fresh slot (FR-016).
- **Not applicable** -- the stage is a mechanical gate (Silver / Gold Ready): state "no
  stage-approval slot applies" and surface the mechanical gate result (FR-015).

## Stage-key -> readiness-doc map (1:1)

| stage key | approval gate? | readiness doc |
|-----------|----------------|---------------|
| source_ready | data-owner confirm | docs/readiness/source-ready.md |
| mapping_ready | YES (analyst/governance) | docs/readiness/mapping-ready.md |
| silver_ready | mechanical | docs/readiness/silver-ready.md |
| gold_ready | mechanical | docs/readiness/gold-ready.md |
| semantic_model_ready | YES (metric owner) | docs/readiness/semantic-model-ready.md |
| dashboard_ready | YES (report owner) | docs/readiness/dashboard-ready.md |
| publish_ready | YES (data-owner/governance) | docs/readiness/publish-ready.md |

(Silver/Gold are mechanical per readiness-model.md; Source Ready needs a data-owner confirm
of proposed semantics/PII but is not one of the four highlighted `approvals[]` stages -- the
pack surfaces its recorded state and any confirm the source records.)

## Invariants

- Read-only apart from writing the one pack (SC-004).
- Missing/unreadable source -> a blocker naming the path; never fabricated (FR-011).
- Generic only; C086 cited, never inlined (FR-014, SC-006).
