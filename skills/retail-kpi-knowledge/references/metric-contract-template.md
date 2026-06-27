# Metric Contract Template

Copy this blank to start a new contract in `contracts/`. Fill every section. Run the
metric-contract-review-checklist before handoff. Keep formulas in **business terms** — no
DAX, SQL, or Python code.

```markdown
# [KPI name] — Metric Contract

ID: KPI-MC-XX

**Business question**
[The single business question this KPI answers.]

**Business definition**
[Plain-language definition agreed with the owner: what is counted, what is excluded,
which policies apply.]

**Formula in business terms**
[Words and simple math. No code. Reference base KPIs where possible.]

**Required fields**
[Each field marked confirmed / assumption / derived. Do not assert unconfirmed fields
exist.]

**Grain**
[Computed-from grain and aggregable-to grains.]

**Additivity**
[Fully additive / semi-additive / non-additive, with a one-line reason.]

**Recommended dimensions**
[Date, branch, region, channel, product, category, brand, supplier, customer segment, …]

**Filters / exclusions**
[Cancelled/void/test, returns handling, VAT, internal transfers, zero-value, etc.]

**Interpretation**
[How to read it; healthy ranges; cautions.]

**Common mistakes**
[Summing non-additives, mixing gross/net, ignoring returns, wrong grain, name vs key, …]

**Validation checks**
[Reconciliation to source, sample spot-checks, bound checks, empty-period behaviour.]

**Implementation handoff notes (SQL / DAX / Python)**
[The same payload feeds all three implementation layers, each taking its slice:
SQL — required fields, grain, filters/exclusions, validation/reconciliation (+ it owns the
physical field binding); DAX — business formula, additivity, filter rules; Python —
required fields + their dtype/quality assumptions for source-prep. List the
fact/dimension fields, grain, additivity, filter rules, and open ambiguities. No
SQL/DAX/Python code.]

**Dashboard use**
[Which pages/tiles would use it.]

**Priority**
[Core / Important / Advanced.]

**Owner**
[One accountable business owner.]

**Status**
[Seeded / Planned / Needs business definition.]
```
