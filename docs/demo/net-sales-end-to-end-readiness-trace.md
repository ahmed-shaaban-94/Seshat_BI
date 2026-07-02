# Net Sales End-to-End Readiness Trace

A single-KPI **paper trace** that walks **Net Sales** through every layer of
Seshat BI: business question → KPI contract → required fields → source/table
coverage → blockers → SQL/gold expectation → DAX/semantic readiness → dashboard
usage → readiness gates. It exists to prove the layers actually hand off to each
other on one real KPI before any broader (scale) work begins.

This is a **trace**, not a live run. It cites committed artifacts; it invents no
source data, writes no new SQL/DAX, grants no readiness, and claims no live
validation. Each step is labeled with one of three evidence tiers:

- **Proven (artifact present)** — a committed file exists and is cited.
- **Documented (not runtime-enforced)** — the gate exists as docs/templates only.
- **Needs real data / live run** — cannot be confirmed without a DB or a real source.

## Step 0 — Why Net Sales

Net Sales is the base realized-revenue KPI most other retail KPIs derive from
(growth, margin, ATV, vs-target), and it already has a **Seeded** metric contract
— the ideal single path to prove end-to-end.

## Step 1 — Business question

> "How much sales revenue did the business actually realize after discounts,
> before returns and tax?"

- **Tier:** Proven (artifact present), with one wording inconsistency to reconcile.
- **Evidence:** `skills/retail-kpi-knowledge/contracts/net-sales.md` ("Business
  question") and the F7 decision-question index in
  `skills/retail-kpi-knowledge/domains/sales-and-revenue.md` ("How much did we sell
  after returns and deductions?" → `contracts/net-sales.md`).
- **Inconsistency to reconcile (human ruling):** the F7 domain question phrases it
  as "after returns and deductions," but the contract's own business question is
  "after discounts, **before returns** and tax" with returns reported separately.
  The two are not identical; a domain owner should reconcile the wording (it does
  not change the measure, but it changes how a reader interprets "Net Sales").

## Step 2 — Net Sales KPI contract

- **Tier:** Proven (artifact present).
- **Evidence:** `skills/retail-kpi-knowledge/contracts/net-sales.md` (KPI-MC-02,
  **Status: Seeded**). Business definition: gross sales less line + header
  discounts, **pre-tax**, returns reported separately unless policy states
  otherwise. Grain: transaction line, additive to branch-day / product-day /
  customer-period. Owner: Finance (primary) + Sales.
- **Boundary:** the contract owns the *meaning*; it explicitly authors no DAX
  ("No DAX authored here"). KPI meaning stays in `retail-kpi-knowledge`.

## Step 3 — Required fields

- **Tier:** Proven (artifact present) for the field *list*; **Needs real data** for
  field *presence in a specific source*.
- **Evidence:** the contract's "Required fields" + the logical field list in
  `skills/retail-kpi-knowledge/references/source-field-requirements.md`.
- **Fields:** net sales amount per line *(assumption — or derive from gross + line
  discount + header discount)*; sale date key, branch key, product key,
  transaction id *(confirmed concept)*; cancellation/test flags, return flag /
  transaction type *(assumption)*.
- **Note:** "confirmed concept" means *expected in any retail sales model*, not
  *confirmed present in a named source* — that confirmation is a real-data step.

## Step 4 — Source / table coverage

- **Tier:** Needs real data.
- **What is needed:** a per-table KPI coverage assessment using the F8 scorecard
  template (`skills/retail-kpi-knowledge/references/kpi-coverage-scorecard-template.md`)
  against a real source table — confirming that net sales amount (or gross + the two
  discount fields) and the exclusion flags are actually present. Coverage is
  expressed as status + named blocker, never a score.
- **Not done here:** this trace does not assert any specific table is "covered";
  doing so requires confirming fields against a real source (F8's own rule: a field
  merely existing is not coverage, and an absent required field is a blocker).

## Step 5 — Blockers

- **Tier:** Proven (artifact present) — the *open rulings* are named in the contract.
- **Open policy rulings (each blocks until the owner decides):**
  - **VAT (A1):** the contract assumes **pre-tax**; confirm with Finance.
  - **Returns (A2):** excluded / netted / separate measure — must be documented.
  - **Sale vs posting date (A3):** name the primary date axis.
  - **Discount fields (A5):** confirm line vs header discount to avoid
    double-subtraction.
- Until these are ruled, a strict contract instance is **Needs business
  definition** for the unresolved policy — a human ruling, not an agent decision.

## Step 6 — SQL / gold expectation

- **Tier:** Mixed — gold **table present**; reconciliation **needs real data**.
- **Evidence (present):** a gold fact table exists in the committed, live c086
  semantic model,
  `powerbi/c086 _sales.SemanticModel/definition/tables/gold fct_sales.tmdl`
  (note the space before `_sales`), built by migration 0006
  (`warehouse/migrations/0006_create_gold_sales_c086_star.sql`). It supplies
  `gross_sales`, `quantity`, and `is_return` at transaction-line grain.
- **Superseded anchor (do not cite as current):** an earlier trace pointed at
  `powerbi/Retailgold.SemanticModel/.../gold fct_sales.tmdl` and its `net_amount`
  column. That model is SUPERSEDED and DEAD — migration 0006 DROPPED
  `net_amount`, `sales_amount`, `tax_amount`, and `discount_amount`, so it can no
  longer refresh (see `powerbi/Retailgold.SemanticModel/SUPERSEDED.md`). The
  current gold star exposes **no** discount/tax columns; there is therefore no
  live discount-net or tax figure to derive here.
- **Needs real data:** the SQL-knowledge reconciliation/validation expectations
  (PK uniqueness, no fan-out, gold-to-source reconciliation) are reasoning the
  `bi-sql-knowledge` layer provides; *running* them is a `retail validate` live
  step that needs a DB + the `db` extra + a filled source-map. **Not run here.**
- **No new SQL authored** in this trace.

## Step 7 — DAX / semantic readiness

- **Tier:** Proven (artifact present) for the measure; **Documented** for the
  semantic-model readiness gate.
- **Evidence (present):** a real, refreshable measure exists —
  `measure NetSales = SUM('gold fct_sales'[gross_sales])` in
  `powerbi/c086 _sales.SemanticModel/definition/tables/_Measures.tmdl` (note the
  space before `_sales`), alongside `GrossSales`
  (`CALCULATE([NetSales], is_return = FALSE())`) and `Returns`
  (`CALCULATE([NetSales], is_return = TRUE())`), so `GrossSales + Returns =
  NetSales`.
- **Meaning shift — the live measure is net of RETURNS, not net of DISCOUNTS
  (finding C15):** this c086 `NetSales` is net of **returns** (return lines carry
  negative `gross_sales`, so a plain SUM is already return-net). It is NOT the
  discount-net figure this trace's business question (Step 1), contract (Step 2),
  and A5 discount ruling (Step 5) describe. The old anchor,
  `NetSales = SUM('gold fct_sales'[net_amount])` in the SUPERSEDED
  `Retailgold.SemanticModel`, WAS discount-net, but that model is dead (0006
  dropped `net_amount` and all discount columns). The contract's handoff note
  wanted "separate Gross Sales **and Discount** measures"; the live model has
  `GrossSales` and `Returns` but **no discount measure**, because the gold star
  has no discount column. **A live, refreshable discount-net `NetSales` does not
  currently exist anywhere** — closing that gap needs a discount column in gold
  and an owner-approved contract, not a citation of the dead model.
- **Documented (not runtime-enforced):** Semantic Model Ready
  (`docs/readiness/semantic-model-ready.md`) is "Planning (docs/templates; no
  runtime code)". The L1–L2 DAX rules (`retail check` D1–D11) and the L3
  `retail semantic-check` (contract↔DAX denominator drift) and L4
  `retail value-check` (live value proxy) are the relevant gates; L4 needs real
  data.
- **Discount-field gap (needs human ruling + a schema change):** the current
  gold star (migration 0006) exposes **no** discount column at all — neither a
  single `discount_amount` nor the **line vs header discount** split the contract
  requires to audit double-subtraction (A5). (The superseded `Retailgold` model's
  single `discount_amount` / `TotalDiscount` is gone with that dead model.) So the
  discount-net path is not just an A5 wording ruling; it needs a discount column
  added to gold before any discount-net measure can be authored or relied on.
- **No new DAX authored** in this trace — the `NetSales` measure already exists and
  is cited as-is.

## Step 8 — Dashboard usage

- **Tier:** Documented (not runtime-enforced); gated, not approval.
- **Evidence:** the contract's "Dashboard use" lists Executive summary, Sales
  Performance, Branch/Product performance, Margin pages. The dashboard-design skill
  (`.claude/skills/powerbi-dashboard-design/`) designs **from approved contracts**.
- **Boundary:** dashboard usage here is a *step gated on contracts +
  `semantic_model_ready`*, **not** a publish approval. Using Net Sales on a page
  does not grant Dashboard Ready or Publish Ready.

## Step 9 — Readiness gates

- **Tier:** Documented (not runtime-enforced).
- **Evidence:** the readiness spine
  (`docs/readiness/readiness-model.md` + the per-stage docs) defines the gate order
  Source → Mapping → Silver → Gold → Semantic Model → Dashboard → Publish. The
  Gold/Semantic/Dashboard/Publish stage docs are each "Planning (docs/templates; no
  runtime code)".
- **Boundary:** no stage is advanced by this trace. Readiness is status + evidence +
  blockers, and a `pass` is a named human action — never self-granted.

## What is proven (on paper)

- The Net Sales **business meaning** is contracted and Seeded (Steps 1–2).
- The **required-field list** is specified (Step 3).
- A real, refreshable **`NetSales` DAX measure** exists in the committed, live
  c086 semantic model (Step 7) — though it means net of **returns**
  (`SUM(gross_sales)`), NOT the net of **discounts** this trace's contract
  describes; the discount-net definition has no live backing (Step 7, finding C15).
- The **gold fact table** that measure sums exists (Step 6, migration 0006).
- The **open policy rulings** that gate a strict instance are named (Step 5).
- The **layer hand-off is coherent**: meaning (retail-kpi) → fields (sql/source) →
  measure (dax) → dashboard (gated) → readiness (human), with no layer redefining
  another's responsibility.

## What is not proven

- That any specific real source table **covers** Net Sales (Step 4 — needs an F8
  scorecard run against real fields).
- That the `NetSales` measure **reconciles** to source / P&L (Step 6/7 — needs a
  live `retail validate` / `value-check` run).
- That the documented readiness gates **pass** — they are docs/templates, not a
  runtime `pass`, and no human approval has been recorded here.

## What needs human ruling

- VAT treatment (A1), returns treatment (A2), date axis (A3), discount-field
  handling (A5) — and every readiness stage `pass`.
- The **F7 domain vs contract wording** for returns ("after returns" vs "before
  returns, reported separately") — a domain-owner reconciliation (Step 1).
- Whether/how to add a discount column to gold to back a discount-net measure at
  all — the current gold star (0006) has no discount field, so the line-vs-header
  A5 question cannot even be evaluated until one is added (Step 7).

## What needs real data

- F8 coverage confirmation of required fields in a named source.
- Live PK/coverage/orphan/reconciliation checks (`retail validate`, needs DB + `db`
  extra + source-map).
- L4 value-proxy reconciliation of the `NetSales` aggregate to an owner-approved
  expected value (`retail value-check`).

## Verdict

This trace **proves on paper** that Net Sales has an end-to-end path —
contract → fields → gold table → a real `NetSales` measure → gated dashboard use →
human-gated readiness — with each layer's boundary intact and no boundary crossed.
**One layer link is NOT clean, and this trace does not pretend it is (finding
C15):** the live `NetSales` measure means net of **returns**
(`SUM(gross_sales)`), while the contract layer defines Net Sales as net of
**discounts** — and no live, refreshable discount-net measure exists (the old
discount-net anchor lived in the now-SUPERSEDED `Retailgold` model, whose columns
0006 dropped). So the meaning layer and the measure layer currently implement
*different definitions* of "Net Sales"; reconciling them (or adding a discount
column + a discount-net contract) is an open item, not a proven coherence. It does
**not** claim live validation, does **not** grant readiness, and honestly separates
what is artifact-present from what still needs real data and a human ruling. The
next real-data step (live reconciliation) is out of scope for a trace and would be
a separate, explicitly authorized run.
