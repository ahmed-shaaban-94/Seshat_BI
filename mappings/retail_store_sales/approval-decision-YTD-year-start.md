# Approval Decision -- `YTD-year-start`

- **question_id:** `YTD-year-start`  *(matches the open request `approval-request-YTD-year-start.md`)*
- **selected_option:** `E1=A, E2=C`  *(the two sub-decisions the named human chose; transcribed, not picked by the console)*
- **owner:** `Ahmed Shaaban (metric_owner)`  *(the named human; metric_owner is the authority class the request required for this F009 metric-contract policy; Finance owns the fiscal-year boundary and this ruling elects calendar, so no fiscal declaration is invoked)*
- **date:** `2026-07-05`
- **rationale:** The named metric owner ruled the two `ytd-net-sales` year-boundary
  policies as follows.
  - **E1 = A (calendar year).** "Year" means the calendar year; year-start = 1 January.
    No fiscal calendar is declared. Per the request's Impact analysis for option A: this
    is implementable today on the existing marked date table (`dim_date_rss`) with no new
    field, so `ytd-net-sales` becomes seedable now. If the organization later declares a
    fiscal year, this is revisited (Finance owns that boundary).
  - **E2 = C (both, to-date primary).** To-date-vs-to-date (like-for-like: Jan 1 -> the
    selected date, both years) is the PRIMARY comparison; the full prior-year YTD is an
    explicitly-labelled SECONDARY comparison; each visual states which it uses. This
    mirrors the H9 D3=C both-baselines convention already ruled for Net Sales Growth %,
    keeping the time-intelligence layer consistent.

## artifacts_updated

The committed artifacts this decision was written THROUGH to. This decision file is the
durable record (written first); the write-throughs below were applied idempotently.

- `mappings/retail_store_sales/approval-request-YTD-year-start.md` -- `status` flipped
  `open` -> `answered`, pointing at this decision record.
- `mappings/retail_store_sales/readiness-status.yaml` -- `approvals[]` entry appended:
  `stage: semantic_model_ready`, `owner: "Ahmed Shaaban (metric_owner)"`, `at: 2026-07-05`,
  framed as a POLICY AMENDMENT that unblocks future F009 authoring of `ytd-net-sales`
  (NOT a re-pass of the already-`pass` stage; its original evidence is untouched).
- `mappings/retail_store_sales/unresolved-questions.md` -- pointer note recording
  `YTD-year-start` as `answered` (recorded off the CLEARED mapping-stage Q1-Q4 table, as
  with H9).

## remaining_blockers

- **Contract internals not authored by this record.** Authoring
  `skills/retail-kpi-knowledge/contracts/ytd.md` from `[planned]` to `[seeded]` (resolving
  its Open ambiguity to E1=A + E2=C, flipping its INDEX/domain rows, and unblocking the
  YTD portion of H6/H10) is a SEPARATE F009 contract-authoring step -- explicitly NOT
  done by this console (per the request's `artifacts_to_update_after_decision`). It
  requires the owner to fire that step.
- **semantic_model_ready stays `pass` on its original evidence.** This ruling is an
  additive policy amendment; it does not re-pass and touches no other stage.

## The `pass`-flip rule (mechanical, gated -- never discretionary)

No stage flips on this decision. `semantic_model_ready` is already `pass`; this amendment
records a policy ruling that unblocks future contract authoring, and adds no new `pass`.
The new `ytd-net-sales` contract will carry its own `[planned] -> [seeded]` transition
when the F009 authoring step runs against this ruling.

## Conflict + amendment posture

- **Not a contradiction of a prior approval.** No prior ruling covered the ytd year-start
  boundary (H9 explicitly did not). Recorded as an AMENDMENT with its own `approvals[]`
  entry and surfaced here -- never a silent re-pass.

## See also

- The decision package this answers: `mappings/retail_store_sales/approval-request-YTD-year-start.md`.
- The contract this unblocks for F009 authoring: `skills/retail-kpi-knowledge/contracts/ytd.md` (Open ambiguity -> resolve to E1=A calendar + E2=C both/to-date-primary).
- The prior time-intelligence ruling this complements: `mappings/retail_store_sales/approval-decision-H9-time-intel.md` (D1/D2/D3).
- The stage state: `mappings/retail_store_sales/readiness-status.yaml` (`approvals[]`).
- The console verb + boundary: `.claude/skills/approval-console/SKILL.md`, `docs/tools/approval-console.md`.
