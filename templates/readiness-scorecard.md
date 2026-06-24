# Readiness Scorecard -- <schema>.<table>

> GENERIC template. Copy per table. A human-readable view of the readiness status
> (`templates/readiness-status.yaml`). Status + evidence + blockers, NOT a fake
> confidence number. See `docs/readiness/readiness-model.md`.

- **Table:** `<schema>.<table>`
- **Source family:** `<source_system>`
- **Current stage:** `<stage_key>`
- **Mapping version:** `<n>`
- **Last checked:** `<YYYY-MM-DD>` by `<agent | person>`

## Stage status

| # | Stage | Status | Evidence (committed) | Blockers |
|---|-------|--------|----------------------|----------|
| 1 | Source Ready | not_started | -- | -- |
| 2 | Mapping Ready | not_started | -- | -- |
| 3 | Silver Ready | not_started | -- | -- |
| 4 | Gold Ready | not_started | -- | -- |
| 5 | Semantic Model Ready | not_started | -- | -- |
| 6 | Dashboard Ready | not_started | -- | -- |
| 7 | Publish Ready | not_started | -- | -- |

Status is one of: `not_started` | `blocked` | `warning` | `pass`. A `pass` row
MUST name its evidence; a `blocked` row MUST name its blocker.

## Approvals

| Stage | Owner | Approved at |
|-------|-------|-------------|
| -- | -- | -- |

## Next allowed action

> `<one concrete next step>`

## Score (optional / DEFERRED)

Scoring rules are not defined yet -- prefer the explicit statuses above. Do not
record a number that reads as confidence. If a future feature defines scoring, a
score MUST cite the evidence it derives from and the rules doc that defines it.

## See also

- Machine-readable state: the table's `readiness-status.yaml`.
- Blockers detail: `blocking-reasons.md`. Data issues: `data-issues.md`.
- The model: `docs/readiness/readiness-model.md`.
