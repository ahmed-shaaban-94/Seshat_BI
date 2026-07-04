# Quickstart: Row-Level Security as a Semantic-Model-Ready Dimension

**Feature**: 092-rls-access-readiness | **Phase**: 1

This walks through how an agent or a human developer exercises HR6 and the
role contract once this feature is BUILT (post-`tasks.md`/implementation).
Nothing here executes early; it describes the intended usage of the shipped
artifacts.

## Prerequisites

- A table has already reached Gold Ready (`gold_ready: pass`) -- HR6 checks a
  role's filter column against the committed gold migration SQL, so the
  referenced `gold.dim_*` table must actually exist in
  `warehouse/migrations/*.sql` for the check to resolve cleanly.
- The table's PBIP semantic model exists and its measures already trace to
  approved metric contracts (F009/F010), i.e. Semantic Model Ready is
  otherwise on track to `pass` except for RLS.

## Step 1 -- A security owner authors a role contract

Copy the generic template into the table's mapping folder, one file per role:

```powershell
Copy-Item templates/rls-role-contract.yaml mappings/<table>/roles/<RoleName>.yaml
```

Fill in:
- `name`: the role's stable name (matches the PBIP `roles.tmdl` role name).
- `filter.gold_table`: the `gold.dim_*` table the role's filter restricts.
- `filter.column`: the column on that table the filter expression targets.
- `readiness.status`: starts `not_started` until reviewed.

The agent MUST NOT fill in `filter.gold_table`/`filter.column` on the owner's
behalf, and MUST NOT decide which roles a model needs (Principle V) -- if
asked to "add RLS", the agent raises this as a question for the security
owner rather than inventing a role.

## Step 2 -- Run the static check

```powershell
retail check
```

or, scoped to see only HR6 output, filter the JSON:

```powershell
retail check --format json | ConvertFrom-Json | Where-Object { $_.rule_id -eq "HR6" }
```

### Failure case (User Story 1)

If `filter.column` is blank, or names a column absent from the referenced
`gold` table, `retail check` exits non-zero and prints an HR6 finding:

```text
[ERROR] HR6  mappings/<table>/roles/RegionManager.yaml
  role 'RegionManager' filter.column is empty; a role contract must name a
  real gold dimension column
```

or, for an unresolvable column:

```text
[ERROR] HR6  mappings/<table>/roles/RegionManager.yaml
  role 'RegionManager' filter binds to gold.dim_store.region_code, which does
  not exist on gold.dim_store per warehouse/migrations/000N_....sql
```

### Fact-table binding (Edge Case / Clarification C1)

If `filter.gold_table` names a `gold.fct_*` table instead of a `gold.dim_*`
table, HR6 hard-fails (never a warning):

```text
[ERROR] HR6  mappings/<table>/roles/RegionManager.yaml
  role 'RegionManager' filter binds to gold.fct_sales (a FACT table); RLS
  must filter a conformed DIMENSION so the filter propagates via the
  relationship -- re-point filter.gold_table at the owning gold.dim_*
```

## Step 3 -- The security owner fixes and re-approves

The owner corrects `filter.column` to a real, existing gold dimension column,
adds evidence, and sets `readiness.status: pass`:

```yaml
name: "RegionManager"
filter:
  gold_table: "gold.dim_store"
  column: "region_code"
readiness:
  status: "pass"
  evidence:
    - "approved by <security owner> on <YYYY-MM-DD>"
  blocking_reasons: []
```

Re-run `retail check` (User Story 2): no HR6 finding is emitted for this
role, and the table's `semantic_model_ready.blocking_reasons[]` no longer
carries the HR6-sourced entry (assuming all other Stage-5 conditions --
D1-D11/C1/R1/G6, every measure traced to an approved metric contract -- are
already clean).

## Step 4 -- HR6 also catches an unearned pass (User Story 3)

If a contract claims `readiness.status: pass` but `evidence: []`, HR6 fails
closed regardless of how well-formed the filter binding looks:

```text
[ERROR] HR6  mappings/<table>/roles/RegionManager.yaml
  role 'RegionManager' claims readiness.status: pass with empty evidence[];
  a pass requires recorded owner approval
```

A `not_started` or `blocked` contract is not itself an HR6 defect (those are
honest, in-progress states) -- but it also does not count as a CLEARED role
for Semantic Model Ready purposes; see Step 5.

## Step 5 -- Reading the Semantic Model Ready verdict

Run the existing, unchanged Stage-5 checker skill:

```text
retail-semantic-check
```

It runs `retail check` (now including HR6) and reads the metric-contract
store exactly as before. Any HR6 `Severity.ERROR` finding surfaces in the
table's `mappings/<table>/readiness-status.yaml` under
`stages.semantic_model_ready.blocking_reasons[]`, prefixed `HR6:`, alongside
any existing D1-D11/C1/R1/G6 blocking reason. This is F010's EXISTING wiring
(it already folds every `retail check` finding into the verdict) -- no code
in `retail-semantic-check` itself changes for this feature (plan.md, Project
Structure).

## Step 6 -- Regenerate the rule manifest (implementation-time, not authoring-time)

After HR6 is registered in code (a `tasks.md`/implementation step, not this
plan), the authoritative rule inventory must be regenerated so the registry
snapshot test does not fail:

```powershell
retail manifest
```

This produces the updated `docs/rules/rules-manifest.json` listing HR6
alongside every other registered rule id.

## What this feature does NOT let you do (guardrails to demonstrate)

- **No auto-fill.** Asking the agent to "just pick a filter column" for a
  role contract is refused; the agent raises an unresolved question instead
  (Principle V, FR-013).
- **No live preview.** There is no `retail check --view-as-role` or
  equivalent; HR6 never evaluates a filter against data (FR-012, FR-018).
- **No score.** `retail check`'s HR6 output never prints a confidence/health
  number -- only the finding message + locator (hard rule #9).
- **No silent zero-contract pass.** A table with zero role contracts is not
  asserted "RLS not needed" by this feature; that remains Q-ZERO-ROLES,
  open for a named owner to rule on (FR-010).
- **No metric-contract.yaml diff.** `git diff templates/metric-contract.yaml`
  and `git diff templates/kpi-pack.yaml` show zero lines changed by this
  feature (SC-005) -- a useful one-line verification an agent can run after
  implementation:

  ```powershell
  git diff --stat templates/metric-contract.yaml templates/kpi-pack.yaml
  ```

  An empty diff confirms the collision-avoidance allocation held.
