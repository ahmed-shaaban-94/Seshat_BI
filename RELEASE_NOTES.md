# Seshat BI Release Notes

## v0.1.0 - Release readiness snapshot

This is the first tagged **release-readiness snapshot** of Seshat BI. It does not
add new behaviour. It turns the current `main` into a state a new user can read,
verify locally, and pick up as a downloadable kit.

### What v0.1 contains

v0.1 is the governance kit that is already on `main`, captured as a coherent
snapshot:

- The **seven-stage readiness spine** (Source Ready -> Mapping Ready -> Silver
  Ready -> Gold Ready -> Semantic Model Ready -> Dashboard Ready -> Publish
  Ready), where each stage is a gate that the next stage cannot skip.
- The **source-mapping gate**: no `silver.*` SQL is written until a table's
  `source-map.yaml` has been reviewed.
- **Medallion warehouse conventions** (`bronze` -> `silver` -> `gold`), with
  Power BI reading `gold` only.
- The `retail` CLI surfaces:
  - `retail check` -- the static governance gate over committed SQL, TMDL/PBIR,
    config, and repo text (the exit code is the authority).
  - `retail validate` -- live data checks against a materialized table (requires
    a database).
  - `retail semantic-check` -- contract-vs-measure drift detection.
  - `retail value-check` -- value-proxy check of a live aggregate against an
    owner-approved expected value (requires a database).
  - `retail generate` -- a verified best-practice DAX measure from an approved
    metric contract.
- The **SQL**, **DAX**, and **Python** knowledge layers that the agent routes
  through.
- One worked example, **retail_store_sales**
  (`docs/worked-examples/retail-store-sales.md`), the domain that traverses the
  full spine to Dashboard Ready with Publish Ready honestly at `warning`. An
  earlier client-specific (C086) example was archived out of the kit so that
  the shipped example stays generic, not tied to one client's schema.
- **Power BI / PBIP governance and handoff** conventions (plain-text TMDL/PBIR,
  handoff packs, gold-only reads).

### How Seshat BI should be understood

Seshat BI is an **agent-first Retail BI readiness system**. It answers one
question safely: *is this retail source ready to become trusted Power BI
analytics?* Readiness is never a faked confidence score -- it is
`status` + `evidence` + `blocking_reasons`, held by a gate.

- **Power BI is a reporting target, not the source of truth.** The warehouse
  (medallion `gold`) is the source of truth; Power BI reads `gold` only.
- **The product is the readiness system** -- the gates, contracts, examples, and
  agent workflow -- not Power BI automation.
- The current CLI / package alias is **`retail`** (see `pyproject.toml`).

### What is intentionally not included yet

These are deliberately deferred or human-gated, not missing through neglect:

- **F016 -- Power BI execution adapter.** Execution-only, deferred by design; not
  startable before `semantic_model_ready` is `pass`.
- **One-click dashboard generation.** Seshat BI is not an automatic dashboard
  generator; dashboards are designed from approved metric contracts.
- **Automated ingestion / live DB provisioning.** Manual load now; no automated
  feed shipped.
- **Fully automated mapping approval.** The mapping gate requires human review.

### How to verify locally

From a clean checkout with Python 3.13:

```bash
pip install -e ".[dev]"
ruff format --check src tests
ruff check src tests
pytest -m unit
retail check
retail semantic-check --repo .
```

> [!NOTE]
> On the current `main`, `retail check` exits `1` because its P2 rule scans the
> recent commit range (`HEAD~20..HEAD`) and flags two pre-existing nonconforming
> commit subjects (#48, #42) that predate this release -- a known, recorded
> condition, not a regression from this pack. The other surfaces above exit
> cleanly. (`HEAD~20..HEAD` is the local fallback range; CI passes an explicit
> `--commit-range`, so it scopes to the PR's own commits.) See
> [`docs/quality/local-verification.md`](docs/quality/local-verification.md).
>
> **Update (#112):** the local fallback was later narrowed to `HEAD~1..HEAD`
> (current commit only); a bare `retail check` on a compliant HEAD now exits
> cleanly and no longer surfaces those aged-out subjects. CI/commit-msg P2
> enforcement is unchanged. Note retained as the release-time record.

A full local-verification checklist (including the optional DB/live path) is in
[`docs/quality/local-verification.md`](docs/quality/local-verification.md).

### Honesty note

- **GitHub Actions status must not be claimed unless it is visible.** Do not state
  that CI is green unless a successful run is actually shown in GitHub Actions.
- **Live validation must not be claimed unless it was run against a real
  database.** Without a DB, `retail validate` and `retail value-check` are
  *pending*, not *passed*. The kit never fakes a pass.

## 2026-07-03 — Design-layer governance wave

A governance wave (not a versioned release cut — versioning is the release
owner's call). It makes the Power BI **design layer** machine-checkable, closing
the surface-3 loop the theme-purity (`DL1`) and background-purity (`DL2`) rules
began. Drafted per the F033 release-note structure; **not** approved — `status:
draft`, awaiting a named release owner (no `approvals[]` entry, no version tag).

### 1. What became possible

- **Token→theme fidelity is now enforced** — `DL3` errors when the compiled
  theme's `dataColors`/`background` drift from the design tokens they compile
  from (evidence: `src/retail/rules/design_theme_fidelity.py`, PR #146). The live
  theme was reconciled to the tokens per the owner's canonical-palette ruling.
- **WCAG contrast is pre-checked from static tokens** — `CT1` computes the sRGB
  luminance ratio for text/background pairs against the token-declared floor,
  pass/fail, never a score (evidence: `src/retail/rules/design_contrast.py`, new
  `CT` family, PR #146).
- **Design-review evidence is gated for well-formedness** — `DL4` requires a
  filled design-review-evidence record to carry every required field before a
  `dashboard_ready` pass can cite it; verify-slot-only, grants nothing (evidence:
  `src/retail/rules/design_review_evidence.py` + `templates/design-review-evidence.md`,
  PR #146).
- **Layout-grid arithmetic is self-checked** — `DL5` recomputes each grid
  profile's column/row closure and flags a stale declared `arithmetic_check`
  (evidence: `src/retail/rules/design_grid_closure.py`, PR #147).
- **The orphaned card validator is now governed** — the Claude Design System
  `validate_cards.py` runs in the test suite over its committed preview bundle
  (evidence: `tests/unit/test_design_cards.py` + `docs/quality/design-cards-count.yaml`,
  PR #148).

### 2. What changed

- Rule registry **47 → 51** rules; the design-lint family grew to `DL1`–`DL5`
  and a new `CT` (contrast) family was added (evidence: `docs/rules/rules-manifest.json`,
  `docs/glossary.md`; PRs #146–147).
- `themes/tower-retail.theme.json` `dataColors` reconciled to the categorical
  token palette (owner ruled tokens canonical; PR #146). **Still to validate in
  Power BI Desktop** — the theme schema is treated as uncertain (`themes/README.md`).
- The desktop `16x9` grid now enumerates all seven section-vocabulary zones
  (added `exception_detail` + `filter_rail`), reconciling it to
  `docs/powerbi/dashboard-blueprints.md` (PR #154).

### 3. Readiness stages affected

None. This wave advances no per-table readiness stage — it is design-layer
governance, orthogonal to the seven-stage spine.

### 4. New rules / families

- `DL3`, `DL4`, `DL5` — design-lint family (surface-2/3 governance).
- `CT1` — new `CT` contrast/accessibility family.
- No new module or execution adapter; no new CLI verb. All five are read-only
  static checks (no execution, no DAX, no PBIP authoring, no score, no approval).

### 5. Known limitations

- Maturity is **unchanged** (see the maturity note below): this wave adds
  governance rules, not worked examples or execution adapters.
- The `filter_rail` grid zone's geometry is authored, not vocabulary-derived
  (flagged for human review in PR #154).
- Ruled but **not built** (owner decisions, recorded in
  `docs/roadmap/design-ideas-decisions.md`): D3, F2, F3 (declined on committed
  evidence); B1, E2, E7, H4, D1, I3 (recommended, owner call); the A6
  section-zone-resolution rule (held). Design ideas inert until content lands:
  A4, A5, A9, A11.

### 6. Migration notes

None. All five rules are additive static checks; no existing artifact schema
changed except the additive theme `dataColors` reconciliation and the additive
grid-zone enumeration. Three post-merge Codex P2 findings were resolved in
PR #149; severity-posture regression-locks all six design rules (PR #151).

### 7. Next best slice

Owner's call. The recorded candidates are the A6 section-zone-resolution rule
(grounded and green, held pending a human eyeball on the authored grid geometry),
then the owner-decision queue (B1 first — the anti-pattern catalogs are drifting).

### Maturity note (observed evidence, not an approval)

Reported level: **L1** (one worked example, `mappings/retail_store_sales/`),
**unchanged by this wave**. The maturity ladder measures worked-example breadth
and execution adapters, not rule count — L2 remains not achieved (missing a
second worked-example table on disk), and L4/L5/L6 (dbt / Dagster / Power BI
execution adapters in-repo) remain not achieved. Stated as observed evidence; a
release owner confirms the level (this is not a granted sign-off).
