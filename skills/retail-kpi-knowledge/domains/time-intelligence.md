# Time Intelligence Domain

Cumulative and comparison views over time. Needs a properly marked date table and care
with additivity (cumulative measures are semi-additive).

## KPIs in this domain

| KPI | Contract | Status |
|-----|----------|--------|
| YTD Net Sales | — | Planned (reuses Net Sales over fiscal calendar) |
| Net Sales Growth % (period-over-period) | — | Planned |

## Key ambiguities (see knowledge/kpi-ambiguities.md)

- Fiscal vs calendar year — use the business's fiscal calendar.
- A3 Which date drives the axis (sale vs posting).
- Comparison baseline: same period last year vs previous period — state it.
- Partial vs full period comparisons must be normalised.

## Owner

Finance and BI.

## Notes

YTD is **semi-additive**: it is already cumulative, so YTD values must not be summed
across months (KPI-AP-10 logic). Growth % is non-additive. Both are planned until the
date table and fiscal attributes are confirmed.
