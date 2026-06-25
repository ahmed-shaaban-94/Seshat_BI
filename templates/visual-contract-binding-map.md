# Visual -> contract binding map -- <subject-area>

<!--
  GENERIC TEMPLATE (roadmap rule 7). Copy this blank into a per-subject-area
  working set and fill the placeholders. This is the artifact the DESIGN REVIEW
  signs off: it proves every visual binds to exactly ONE approved metric contract
  (no orphan visual) and that no approved contract is silently dropped.

  C086 IS AN EXAMPLE, NEVER INLINED HERE. Do NOT copy any C086/pharmacy specifics
  into this file. ASCII, UTF-8 no BOM. No real connection host or secret.

  The dashboard-design skill authors this; it NEVER invents a metric (binds only
  to approved F009 contracts) and NEVER self-grants dashboard_ready: pass.
-->

## Subject area

- subject_area: `<schema.table or model name>`
- governed_model: `<relative path>`
- semantic_model_ready: `pass`

## Binding map (every visual -> exactly one APPROVED contract)

| visual_id | visual_type | business_question | bound_contract (approved) | semantic_model_field(s) |
|-----------|-------------|-------------------|---------------------------|-------------------------|
| `v01` | `<card/bar/line/table>` | `<question>` | `<approved-contract-name>` | `<mapped field(s)>` |
| `v02` | `<...>` | `<...>` | `<approved-contract-name>` | `<...>` |

> Every row MUST cite one APPROVED contract by name and mapped model field(s).
> A visual with no backing approved contract is an ORPHAN -> do not emit it -> STOP.

## Dropped contracts (more approved contracts than visuals -- record each, no silent omission)

| dropped_contract | reason it is not on this page |
|------------------|-------------------------------|
| `<approved-contract-name>` | `<e.g. covered by the Stage 7 handoff pack, not the dashboard>` |

## Review sign-off (Principle V -- the reviewer's action, NOT the skill's)

- reviewer (BI report owner): `<name>`
- decision: `<pending | approved>`
- approvals entry (added by the reviewer on approval):
  `{stage: dashboard_ready, owner: <bi-report-owner>, at: <YYYY-MM-DD>}`

## Readiness

- dashboard_ready: `warning`   # the skill records at most warning; pass requires the approvals entry above
- evidence: ["<layout plan>", "<visual list>", "<this binding map>"]
- next_action: "get the design review (visual->contract binding) signed off by the BI report owner"
