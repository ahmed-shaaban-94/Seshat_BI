# dashboard-qa (surface 1: the visual anti-pattern reference)

Surface 1 of the four-surface router (`../SKILL.md`). This workflow is the
visual-QA CATALOG -- the committed list of dashboard anti-patterns, each naming
the rule or principle it violates -- plus how to run a QA pass over a proposed or
existing page. The router opens it for a "final review". It is the procedure that
USES the prose explanations in `docs/powerbi/visual-qa.md`: the readable
why-each-is-bad lives there, the checklist-and-severity procedure lives here.
Keep the two in sync -- same thirteen anti-patterns, same names.

## Scope (read first)

This workflow CHECKS report visuals against the anti-pattern catalog and records
findings; it does not redesign the page (that is `page-blueprint.md` +
`visual-design-system.md`) and it does not produce the critique-output document
(that is `screenshot-review.md`, which consumes this catalog). It authors nothing
in Power BI (F016) and defines no metric (F009). It binds to contracts and fields
that already exist; where a checked visual has none, the gate below applies and
the finding is a blocker, not a style note.

## The inherited gate

No data-bound dashboard design before the subject area semantic_model_ready is pass (roadmap
rule 5). This feature DEFINES NO new gate and is NOT a second source of truth: the gate, the
design-review sign-off, and the dashboard_ready: pass are owned by docs/readiness/dashboard-ready.md
and the F011/012 dashboard-design verb (spec-only today). This feature documents and reuses them.

QA does not lift the gate: a data-bound page is QA-checked only after the subject
area's `semantic_model_ready` is `pass`. Two of the anti-patterns below ARE the
gate (a visual with no contract; an unmapped field) -- when QA finds them it
records the blocking reason and STOPS the visual, it does not file them as
cosmetic warnings.

## How to run a QA pass

1. **Confirm the surface + intent.** This is a final review of report visuals
   (surface 1). A request to critique a SCREENSHOT routes to `screenshot-review.md`
   (which uses this same catalog); a request to redesign routes to
   `page-blueprint.md`. If the intent is ambiguous, STOP and ask (Principle V).
2. **Walk the catalog below** against each page and each visual.
3. **Classify every finding by severity** (the split is load-bearing):
   - a **gate** finding (no contract / unmapped field) -> record the blocking
     reason, STOP that visual, point upstream (F009 / F010);
   - a **purity** finding (dynamic value in a static background / theme colors
     overridden per visual) -> a must-not violation, record it and require the
     fix before the page can pass;
   - a **style** finding (every other anti-pattern) -> a `warning`-class design
     note: record it, propose the accessible/clearer alternative, surface it for
     review; do not silently override the author.
4. **Record readiness** with the four statuses only -- `not_started` / `blocked`
   / `warning` / `pass` -- plus `evidence[]` and `blocking_reasons[]`. Never a
   numeric score (rule 9). Any open gate or purity finding makes the page
   `blocked`; only style notes outstanding makes it `warning`. Never self-grant
   `dashboard_ready: pass` -- that is the verb owner's recorded design-review.
5. **Hand the findings to the output procedure** (`screenshot-review.md`) when a
   written critique document is wanted; this workflow supplies the catalog and the
   severity, not the critique-document shape.

## The anti-pattern catalog (each names the rule it violates)

Thirteen anti-patterns. The Severity column drives the recording posture in step
3/4 above. The prose explanation of each lives in `docs/powerbi/visual-qa.md`.

| # | Anti-pattern | Rule / principle it violates | Severity |
|---|--------------|------------------------------|----------|
| 1 | Too many visuals on one page | Executive pages use FEWER visuals (visual hierarchy; max-visuals-per-executive-page) -- `docs/powerbi/visual-design-system.md` | warning |
| 2 | KPI without comparison/context | Every KPI has comparison/context (vs prior period / vs target) -- `docs/powerbi/visual-design-system.md` | warning |
| 3 | Unclear date context | Every page answers a clear business question, which fixes the period it covers; a number with no stated date context is unreadable -- `docs/powerbi/visual-design-system.md` | warning |
| 4 | Wrong number formats | Consistent, correct number formats (defaults from `design/tokens/tower-retail-design-tokens.yaml`) -- `docs/powerbi/visual-design-system.md` | warning |
| 5 | Slicers taking too much space | Slicers do not dominate the page; the filter rail stays to the side, insight stays primary -- `docs/powerbi/visual-design-system.md` | warning |
| 6 | Table used as the main executive visual | Tables are for row-level DETAIL, not executive insight -- `docs/powerbi/visual-design-system.md` | warning |
| 7 | No visual hierarchy | A page has a clear hierarchy (headline KPIs, then main insight, then diagnostic/detail); flat layouts hide the answer -- `docs/powerbi/visual-design-system.md` | warning |
| 8 | Inconsistent branch/category colors | Colors carry meaning; the same branch/category keeps the same color across visuals (consistent category colors) -- `docs/powerbi/visual-design-system.md` | warning |
| 9 | No tooltip explanation | Colors/encodings carry meaning that on-hover tooltips must explain; an unexplained visual forces guessing -- `docs/powerbi/visual-design-system.md` | warning |
| 10 | Visual using a metric with NO contract | The contract rule (FR-002/FR-003): every data-bound visual cites one approved metric contract (F009); a visual with none is an ORPHAN -- the inherited gate, `docs/readiness/dashboard-ready.md` | blocked (gate) |
| 11 | Visual using an UNMAPPED field | The field rule (FR-002): every data-bound visual binds to a field present in the governed semantic model (F010); a field not in the model is UNMAPPED -- the inherited gate, `docs/readiness/dashboard-ready.md` | blocked (gate) |
| 12 | Background containing dynamic values | Surface-2 purity rule (BLOCK 3): background is STATIC STRUCTURE, never data -- no KPI value or dynamic title baked into a static image -- `background-asset-design.md`, `docs/powerbi/background-assets.md` | blocked (purity) |
| 13 | Theme colors overridden randomly per visual | Surface-3 purity rule (BLOCK 4): colors are theme DEFAULTS carrying meaning, not per-visual overrides invented ad hoc -- `theme-json-design.md`, `docs/powerbi/theme-json.md` | blocked (purity) |

### The two gate findings (10, 11) -- record and STOP, do not style-fix

A visual with no backing approved contract is an ORPHAN; a field not in the
governed model is UNMAPPED. These are not cosmetic. Do NOT invent a metric to
fill the card and do NOT bind the visual to an unmapped field to make the finding
go away. Record the blocking reason and STOP the visual:

- no backing contract -> `orphan visual: no contract for <question>`;
- a field not in the governed model -> `unmapped field: <field>`.

Then point upstream: a missing metric is F009's job to define and approve; a
missing field is an F010 semantic-model concern. The foundation never closes
either by improvising.

### The two purity findings (12, 13) -- must-not, not warning

A dynamic value baked into a static background never refreshes (a number frozen in
a PNG). A theme color overridden ad hoc per visual breaks the meaning the palette
carries. Both are must-not violations of a surface-purity rule, recorded and
required-fixed before the page passes -- not filed as a soft style note. The fix
for 12 is to move the value to a live surface-1 card above the background
(`background-asset-design.md`); the fix for 13 is to pull the color from the theme
default, not a per-visual override (`theme-json-design.md`).

### The nine style findings (1-9) -- warning-class design notes

The remaining anti-patterns are violations of the committed design principles
(`docs/powerbi/visual-design-system.md`). Each is a `warning`-class note: record
it, propose the clearer/accessible alternative, and surface it for the human
review. A readability or grain deviation a user insists on (a dark, dense
executive page; a chart shown at a grain finer than its contract) is recorded as
a `warning` with the reason and the accessible alternative proposed -- never
silently overridden, never silently complied with against the principle
(Principle V / Principle VI).

## Stop-and-ask (Principle V)

STOP and surface to a human rather than self-answering when:

- which business question a page/visual answers is unclear;
- a finding implies a readability or grain deviation that needs an owner's call;
- a finding implies a metric is wrong -- QA may FLAG that a visual seems to use an
  uncontracted/unmapped metric, but it does NOT redefine the metric (that is
  F009); it records the finding and points upstream;
- the design-review sign-off itself -- the `dashboard_ready: pass` is the verb
  owner's recorded approval, never QA's to self-grant.

## See also

- The router + the four-surface table: `../SKILL.md`.
- The prose home of this catalog (the readable per-anti-pattern explanations):
  `docs/powerbi/visual-qa.md`.
- The committed design principles each style finding cites:
  `docs/powerbi/visual-design-system.md`.
- The output procedure that consumes this catalog (findings + fixes + forbidden
  changes): `screenshot-review.md` and its template `templates/screenshot-review.md`.
- Where the gate + the four statuses are owned: `docs/readiness/dashboard-ready.md`,
  `docs/readiness/readiness-model.md`.
- The surface-2 / surface-3 purity rules in full: `background-asset-design.md`,
  `theme-json-design.md`.
- Conservative number-format / KPI-card / max-visuals defaults:
  `design/tokens/tower-retail-design-tokens.yaml`.
