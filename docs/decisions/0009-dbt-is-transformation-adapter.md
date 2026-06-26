# 0009 -- dbt is a transformation ADAPTER (the build engine), not the brain

- **Date:** 2026-06-26
- **Status:** Accepted -- this ADR, the two contract templates
  (`templates/dbt-adapter-contract.md`, `templates/dbt-model-contract.md`), the skill, and
  the integration doc are AUTHORED in this build slice; the dbt RUNTIME project (models,
  tests, macros, `dbt_project.yml`) is ENUMERATED as a future output and ships NO dbt files.
- **Roadmap feature:** F029 (on-disk spec `023-dbt-transformation-adapter`). When the
  spec-dir number and the F-number disagree, the roadmap F-number wins.
- **Authority category (F024):** Execution Adapter / `DB-connected` (NOT publish-capable).
  Declared against `docs/architecture/product-modules.md`; the copy-me declaration is
  `templates/adapter-contract.md`, specialized for dbt as `templates/dbt-adapter-contract.md`.
- **Context:** The warehouse already builds silver and gold as numbered, idempotent SQL
  migrations under `warehouse/migrations/`. That hand-authored SQL is the DEFAULT build
  path and it is approved and live. Teams that already standardize on dbt for warehouse
  transformation want the same silver/gold build expressed as dbt models -- gaining dbt's
  dependency graph, incremental materialization, test framework, and docs site -- WITHOUT
  giving up Tower BI's gate-enforced readiness. The open question this ADR closes: how can
  dbt build silver/gold while Tower BI -- not dbt -- remains the authority that decides
  whether Silver Ready and Gold Ready are `pass`? A green `dbt test` is EVIDENCE, never an
  approval. This ADR records the terms of entry.

## Decision

### 1. dbt is the build ENGINE; Tower BI is the brain

dbt compiles SQL, materializes models, and runs tests. Tower BI owns the approved
source-map (the only legal source of what each model means), owns the metric contracts,
owns the readiness spine, and routes every judgment call to a named human. dbt is an
Execution Adapter under F024: it READS truth (the approved map), EXECUTES approved steps
(builds + tests behind the gate), and WRITES DERIVED evidence (run/test/parity results).
It CREATES no truth. This is the F024 authority matrix made operational for a build engine.

### 2. The entry gate -- dbt may build ONLY after Mapping Ready = `pass`

> The adapter MUST refuse to run any staging/silver/gold dbt model for a table whose
> `mappings/<table>/readiness-status.yaml` does not record Mapping Ready = `pass`,
> recording a `blocking_reason` instead.

This is Principle IV made operational for a build engine: the presence of dbt model files
is NOT permission to build. Every dbt model MUST cite the already-approved `source-map.yaml`
(path + git ref + the rows that justify its grain, PK, and each column). A model that
introduces a meaning -- a grain, a PK, a PII flag, or a placement -- the approved map does
not state is a defect: the model cites the map, it does not extend it. The map is
re-approved first (Principle V).

### 3. The evidence-not-approval rule (the governance hinge)

> dbt test results (counts of passing/failing tests and the failing rows' measured numbers)
> are recorded as `evidence[]` / `blocking_reasons[]` in the readiness status. A green
> `dbt test` MUST NOT move Silver Ready or Gold Ready to `pass`. Tower readiness + a named
> human decide that, citing the dbt evidence + the recorded approval.

Conflating a green `dbt test` with an approved gate is exactly how a DB-connected adapter
rots into the brain. There is NO path by which a green run alone writes `pass`: every such
transition cites dbt evidence PLUS a named human approval (owner + date).

### 4. dbt is an OPTIONAL ALTERNATIVE; migrations stay the default until parity

> `warehouse/migrations` remains the DEFAULT build path. dbt becomes a table's build path
> ONLY after the reconciliation parity test passes AND a named human approves the switch.
> Both paths MUST NOT silently feed the same gold tables.

This is Principle VI (defaults then deviations): migrations are the default; dbt is the
deviation, allowed only after a passing parity test + a recorded human approval. The agent
never flips the default on its own.

After an approved switch, that table's migration files are RETAINED (not deleted) as the
parity oracle and the rollback path, marked superseded-but-kept. Retiring a retained
migration is a SEPARATE, later named-human decision -- never a side effect of the switch.
While the migration oracle is retained, the reconciliation parity test (decision 5) MUST
re-run on EVERY dbt build for that table; a one-time-at-switch check is insufficient
because it would let the two paths silently diverge afterward.

### 5. The reconciliation parity test (four assertions, exact to the cent)

For a table already built by migrations, the dbt mart must reproduce the SAME gold output.
The parity test asserts, against the migration-built gold fact:

1. equal fact row count;
2. preserved distinct count of the fact's degenerate / business key;
3. each additive money-measure sum equal to the cent -- absolute delta `<= 0.01` per
   additive measure, matching the committed money scale (e.g. `NUMERIC(12,2)`);
4. equal per-dimension distinct member counts -- each conformed dimension's member count,
   including any unknown / sentinel member where the gold model defines one.

The per-dimension count closes the divergent-unknown-member gap (a dbt unknown-member
handling that diverges from the migration's sentinel would otherwise pass a fact-only
check). The parity result is EVIDENCE; a named human approves any build-path switch. The
tolerance is the stated default (cent-level, given the money scale); it stays owner-
confirmable when the adapter is built.

### 6. dbt is DB-connected, NOT publish-capable -- it stops at gold

dbt materializes gold and stops. Materializing or publishing a Power BI model is the
parked F016 execution adapter (`publish-capable`), gated separately on Semantic Model
Ready. dbt and F016 are different adapter categories and never overlap (Principle III:
medallion, gold-only -- Power BI reads gold).

### 7. Auto-update policy -- pin dbt-core + dbt-postgres together

`dbt-core` and `dbt-postgres` are pinned TOGETHER. Patch / minor versions open a PR; a
major version requires named-human review. NO automerge for a dbt minor or major bump
until compatibility tests exist. The policy is recorded in the adapter contract
(`templates/dbt-adapter-contract.md`) and here.

### 8. No secrets -- only `profiles.example.yml` is committed

Only `profiles.example.yml` (placeholders, NO secrets, NO DSN, NO tokens, NO host) MAY be
committed. The real `profiles.yml` MUST be git-ignored and supplied by the operator. No
connection string, credential, or host MAY appear in any tracked file (Principle IX).

### 9. Docs-first; this slice ships NO dbt files

Consistent with Principle VIII and the spec's scope wall, this slice writes the planning
artifacts only. The dbt project (`dbt/`), the two contract templates, this ADR, the
integration doc, and the skill enumerate the future shape; the dbt models, tests, macros,
and `dbt_project.yml` are NOT created now. The enumerated shape lives in
`docs/integrations/dbt-adapter.md`.

## Consequences

- dbt can be adopted as a build engine without surrendering the gate: the entry gate
  (decision 2), the evidence-not-approval rule (decision 3), and the parity rule
  (decision 5) keep dbt a reader-and-executor of truth, never an author of it.
- A team may run two build paths during a transition with NO silent divergence: migrations
  stay the default and the parity test re-runs on every dbt build while the oracle is kept.
- The static `retail check` gate is untouched: dbt adds no `retail check` rule and no
  readiness stage; dbt evidence flows into the EXISTING `readiness-status.yaml` `evidence[]`.
- No maturity/confidence score is introduced (hard rule #9): `<= 0.01` is a money tolerance
  and the version pins are reproducibility, not a score. A "parity confidence %" is forbidden.
- `retail_store_sales` stays a CITED example (the first MVP), never inlined into the generic
  templates / ADR / skill (Principle VII).

## Alternatives considered

- **Let a green `dbt build` / `dbt test` advance the stage.** Rejected: it conflates
  evidence with approval and lets the adapter become the brain (decision 3). Tower
  readiness + a named human decide, citing the evidence.
- **Replace `warehouse/migrations` with dbt.** Rejected: migrations stay the DEFAULT and
  the parity oracle (decisions 4-5); dbt is an optional alternative proven by parity, not a
  replacement.
- **Run the parity test once at switch.** Rejected: it would let the two paths silently
  diverge afterward; the test re-runs on every dbt build while the oracle is retained.
- **Make dbt publish-capable (build the Power BI model too).** Rejected: that is the parked
  F016 adapter, gated separately; dbt stops at gold (decision 6, Principle III).
- **A universal multi-engine transformation adapter.** Rejected for this slice: only
  dbt-core + dbt-postgres are in scope; a second engine would be its own spec.

## See also

- The spec / plan / tasks: `specs/023-dbt-transformation-adapter/{spec,plan,tasks}.md`.
- The category contract: `docs/architecture/product-modules.md` (the F029 row declares
  Execution Adapter / `DB-connected`); the copy-me declaration `templates/adapter-contract.md`.
- The dbt-specific contracts: `templates/dbt-adapter-contract.md`,
  `templates/dbt-model-contract.md` (planned generic templates, no `retail_store_sales`).
- The integration doc + the enumerated `dbt/` shape: `docs/integrations/dbt-adapter.md`.
- The skill: `.claude/skills/dbt-transformation-adapter/SKILL.md`.
- The example connection profile: `profiles.example.yml` (placeholders only, Principle IX).
- The parity target + the worked example: `warehouse/migrations/` + `docs/worked-examples/c086-pharmacy.md`.
- `.specify/memory/constitution.md` (Principles III, IV, V, VI, VII, VIII, IX).
- The append-only ADR allotment for this tier: 0008 (F024), **0009 (F029, this)**,
  0010 (F030), 0011 (F031). Shipped ADRs are never reused.
