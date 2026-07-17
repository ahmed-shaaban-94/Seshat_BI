# Data Model: Activate the Professional dbt MVP

**Feature**: 133-activate-dbt-mvp  
**Date**: 2026-07-16

This feature adds no readiness stage and no independent run-state engine. Its durable objects are an accepted local execution plan and a committed derived-evidence record. All other objects are in-memory validation or invocation results.

## 1. WorkingSet

Resolves one governed table to the files that authorize transformation work.

| Field | Type | Invariant |
|---|---|---|
| `repo_root` | `Path` | Existing repository root; never serialized into evidence. |
| `table_id` | `str` | Matches `^[a-z][a-z0-9_]*$`; resolves exactly one mapping directory. |
| `mapping_dir` | `Path` | Exactly `mappings/<table_id>`. |
| `source_map` | `Path` | Exactly `<mapping_dir>/source-map.yaml`; tracked and clean. |
| `readiness_status` | `Path` | Exactly `<mapping_dir>/readiness-status.yaml`. |
| `unresolved_questions` | `Path` | Exactly `<mapping_dir>/unresolved-questions.md`. |
| `source_map_revision` | `str` | Git blob object ID from `HEAD:<relative-path>`. |
| `source_map_sha256` | `str` | Lowercase 64-character SHA-256 of current bytes. |

Validation failures are represented as `GovernanceError` with a stable code; resolution never falls back to fuzzy directory matching.

## 2. GateDecision

Pure result of reading the working set.

| Field | Type | Invariant |
|---|---|---|
| `allowed` | `bool` | True only when all mapping conditions pass. |
| `table_id` | `str` | Same table as the working set. |
| `mapping_status` | `str` | Raw categorical Mapping Ready status; never converted to a score. |
| `approval` | `MappingApproval | None` | Named approval that matches Mapping Ready. |
| `mirror_cleared` | `bool` | True only for an unambiguous `Gate status: CLEARED` and no open question rows. |
| `blocking_reasons` | `tuple[Blocker, ...]` | Empty iff `allowed` is true; each entry names a concrete fact. |

`MappingApproval` reads the repository's canonical `stage`, `owner`, `at`, and `note` fields and derives `approval_id` as SHA-256 over their canonical JSON. Missing `owner` or ISO `at` is not a valid approval.

## 3. ProjectValidation

Static result before dbt is invoked.

| Field | Type | Invariant |
|---|---|---|
| `valid` | `bool` | True only when every check passes. |
| `project_fingerprint` | `str` | SHA-256 over sorted relative paths and bytes under `dbt/`, excluding `target/`, `logs/`, and packages. |
| `selector_name` | `str` | Exactly `seshat_table_<table_id>`. |
| `profile_name` | `str` | Exactly `seshat_bi_warehouse`. |
| `target_name` | `str` | Exactly `shadow`. |
| `schemas` | `ShadowSchemas` | Derived, validated identifiers only. |
| `model_contracts` | `tuple[ModelContract, ...]` | One contract for every selected model. |
| `blocking_reasons` | `tuple[Blocker, ...]` | Includes unsafe schemas, profiles, selectors, or citations. |

`ShadowSchemas` contains `silver`, `gold`, and `audit`, each derived as `<target_schema>_<layer>`. `target_schema` and all derived names match `^[a-z_][a-z0-9_]*$` and are not `silver`, `gold`, `bronze`, or `public`.

`ModelContract` contains:

- `unique_name`: expected dbt model name;
- `table_id`: governed mapping ID;
- `source_map`: repository-relative approved map path;
- `source_map_revision`: committed map blob ID;
- `grain`: exact approved grain for fact/staging models, or an explicitly named dimension/audit grain derived from the approved gold-star section;
- `business_key`: ordered tuple of approved keys or model-specific governed keys;
- `authority`: fixed `derived`;
- `columns`: tuple of `ColumnCitation`.

`ColumnCitation` contains `name`, `source_columns`, and optional `derivation`. Every output has at least one source column or a recognized physical derivation such as `surrogate_key`, `date_spine`, `unknown_member`, or `parity_measure`; derivations cannot introduce business meaning.

## 4. ExecutionPlan

Immutable facts authorized by `--accept-plan`. The digest is calculated from canonical JSON for this object; it is stored outside the object in `PlanEnvelope`.

```json
{
  "schema_version": 1,
  "table_id": "retail_store_sales",
  "mapping": {
    "path": "mappings/retail_store_sales/source-map.yaml",
    "git_blob": "<git-object-id>",
    "sha256": "<64-lowercase-hex>",
    "readiness_sha256": "<64-lowercase-hex>",
    "unresolved_questions_sha256": "<64-lowercase-hex>",
    "approval_id": "<stable-approval-id>"
  },
  "project": {
    "path": "dbt",
    "sha256": "<64-lowercase-hex>"
  },
  "runtime": {
    "dbt_core": "1.12.0",
    "dbt_adapter": "dbt-postgres",
    "dbt_adapter_version": "1.10.2",
    "profile": "seshat_bi_warehouse",
    "target": "shadow",
    "selector": "seshat_table_retail_store_sales"
  },
  "schemas": {
    "silver": "seshat_dbt_shadow_silver",
    "gold": "seshat_dbt_shadow_gold",
    "audit": "seshat_dbt_shadow_audit"
  },
  "manifest": {
    "schema_uri": "https://schemas.getdbt.com/dbt/manifest/v12.json",
    "semantic_sha256": "<64-lowercase-hex>"
  },
  "selected_unique_ids": [
    "model.seshat_bi.audit_retail_store_sales_parity",
    "model.seshat_bi.dim_customer_rss"
  ]
}
```

The real array contains all governed model and test unique IDs in lexical order. The example above is shortened only to explain the shape; schema and tests require the complete selection.

### Canonicalization

- UTF-8 without BOM;
- JSON object keys sorted recursively;
- arrays retained in declared order, with selected IDs pre-sorted;
- separators `,` and `:` with no insignificant whitespace;
- no timestamp, absolute path, process ID, or digest field;
- SHA-256 over the resulting bytes.

`PlanEnvelope`:

```json
{
  "digest": "<64-lowercase-hex>",
  "plan": { "schema_version": 1 }
}
```

The full `plan` value must validate against `contracts/dbt-execution-plan.schema.json`. Local path: `.seshat/dbt/plans/<table_id>-shadow.json`.

## 5. RunContext

In-memory instruction for one controlled dbt invocation.

| Field | Type | Invariant |
|---|---|---|
| `repo_root` | `Path` | Never handed to the evidence serializer as an absolute path. |
| `project_dir` | `Path` | Fixed `<repo>/dbt`. |
| `profiles_dir` | `Path` | Fixed repository root containing ignored `profiles.yml`. |
| `operation` | `Operation` | One of `parse`, `list`, `build`, `test`, `show`. |
| `table_id` | `str` | Governed ID from accepted plan. |
| `selector` | `str` | Fixed selector from plan. |
| `target` | `str` | Fixed `shadow`. |
| `run_dir` | `Path` | `.seshat/dbt/runs/<invocation_id>` and ignored. |
| `environment` | `Mapping[str, str]` | Parent environment plus parsed `.env`, child-only. |
| `timeout_s` | `float` | Positive bounded command timeout, default 1800 seconds. |

`Operation` is an enum, not an arbitrary string supplied by users.

## 6. InvocationResult

Sanitized process boundary result.

| Field | Type | Invariant |
|---|---|---|
| `invocation_id` | `str` | UTC compact timestamp plus random lowercase hex; safe as a filename. |
| `operation` | `Operation` | Matches the fixed argv builder. |
| `argv_summary` | `tuple[str, ...]` | Contains command/flags but no absolute executable/profile/artifact path or secret. |
| `return_code` | `int` | Raw dbt process exit, later mapped to Seshat exit. |
| `started_at` | `str` | UTC RFC 3339. |
| `completed_at` | `str` | UTC RFC 3339, not earlier than start. |
| `stdout` | `str` | Sanitized in memory; never copied wholesale into committed evidence. |
| `stderr` | `str` | Sanitized in memory; never copied wholesale into committed evidence. |
| `target_dir` | `Path` | Local raw artifact directory. |
| `log_dir` | `Path` | Local raw log directory. |

## 7. Artifact Summaries

### ManifestSummary

| Field | Type | Invariant |
|---|---|---|
| `schema_uri` | `str` | Exact supported manifest v12 URI. |
| `dbt_version` | `str` | Exact accepted plan version. |
| `sha256` | `str` | Hash of raw `manifest.json`. |
| `semantic_sha256` | `str` | Canonical hash of allowlisted governed node fields; excludes volatile invocation metadata. |
| `nodes` | `Mapping[str, ManifestNode]` | Each key equals node `unique_id`. |
| `selected_unique_ids` | `tuple[str, ...]` | Enabled governed selection in lexical order. |

`ManifestNode` retains only allowlisted fields: `unique_id`, `resource_type`, `name`, `package_name`, `original_file_path`, `depends_on_nodes`, `tags`, `schema`, and `meta`. Absolute `root_path`, compiled SQL, and credentials are never normalized into evidence.

### RunResultsSummary

| Field | Type | Invariant |
|---|---|---|
| `schema_uri` | `str` | Exact run-results v6 URI. |
| `dbt_version` | `str` | Exact accepted plan version. |
| `which` | `str` | Expected `build`, `test`, or `show`. |
| `sha256` | `str` | Hash of raw `run_results.json`. |
| `results` | `tuple[NodeResult, ...]` | Executed nodes only. |

`NodeResult` retains `unique_id`, normalized `status`, integer-or-null `failures`, and decimal execution seconds. It drops raw adapter messages and compiled code.

### ArtifactSet

Contains one verified manifest plus the relevant build/test/show run-results summaries. Missing or overwritten artifacts are an integrity failure, not partial success.

## 8. ParityAssertion

One required audit row.

| Field | Type | Invariant |
|---|---|---|
| `assertion_id` | `str` | Stable allowlisted ID. |
| `assertion_class` | `str` | `fact_row_count`, `business_key_count`, `additive_money_total`, or `dimension_member_count`. |
| `subject` | `str` | Stable table/measure/dimension identifier. |
| `expected` | `str` | Canonical decimal string from migration-owned relation. |
| `actual` | `str` | Canonical decimal string from shadow relation. |
| `delta` | `str` | Canonical non-negative decimal string. |
| `tolerance` | `str` | `0` for counts; `0.01` for additive money. |
| `passed` | `bool` | Exactly `Decimal(delta) <= Decimal(tolerance)`. |

Required IDs for the first example:

- `fact_row_count`;
- `fact_distinct_transaction_id`;
- `fact_total_spent_sum`;
- `dim_customer_member_count`;
- `dim_product_member_count`;
- `dim_payment_method_member_count`;
- `dim_location_member_count`;
- `dim_date_member_count`.

No evidence may have outcome `pass` unless all eight IDs occur exactly once and pass.

## 9. RunEvidence

Durable, sanitized, derived evidence. Canonical schema: `schemas/dbt-run-evidence.schema.json`.

```json
{
  "schema_version": 1,
  "authority": "derived-evidence-only",
  "invocation_id": "20260716T120000Z-a1b2c3d4",
  "table_id": "retail_store_sales",
  "command": "build",
  "outcome": "pass",
  "seshat_exit_code": 0,
  "started_at": "2026-07-16T12:00:00Z",
  "completed_at": "2026-07-16T12:01:00Z",
  "elapsed_seconds": 60.0,
  "plan_digest": "<64-lowercase-hex>",
  "project_fingerprint": "<64-lowercase-hex>",
  "mapping_path": "mappings/retail_store_sales/source-map.yaml",
  "mapping_revision": "<git-object-id>",
  "runtime": {
    "dbt_core": "1.12.0",
    "dbt_adapter": "dbt-postgres",
    "dbt_adapter_version": "1.10.2"
  },
  "target": {
    "name": "shadow",
    "schemas": {
      "silver": "seshat_dbt_shadow_silver",
      "gold": "seshat_dbt_shadow_gold",
      "audit": "seshat_dbt_shadow_audit"
    }
  },
  "selected_unique_ids": [],
  "executed_unique_ids": [],
  "tests": {"passed": 0, "failed": 0, "errored": 0, "skipped": 0},
  "parity": [],
  "artifacts": {
    "manifest.json": "<64-lowercase-hex>",
    "run_results.json": "<64-lowercase-hex>",
    "parity_run_results.json": "<64-lowercase-hex>"
  },
  "blocking_reasons": [],
  "readiness_effect": "none; named-human approval required"
}
```

Arrays contain the complete run data. Empty arrays in the illustration are shape examples, not a valid passing record.

### Outcomes

| Outcome | Meaning | Allowed Seshat exit |
|---|---|---|
| `pass` | Invocation, artifact integrity, tests, and complete parity succeeded. Evidence only. | `0` |
| `blocked` | Governance or parity condition prevents acceptance. | `1` or `3` |
| `failed` | dbt model/test execution failed with valid inspected artifacts. | `1` |
| `unavailable` | Python/dbt/profile/database prerequisite absent. | `2` |

Artifact integrity exit 4 does not produce a trusted `pass`; it may write a sanitized failure record only if the record can honestly state that artifacts were rejected. `doctor`, `validate`, and `plan` return stable CLI result objects but do not write run evidence because they have no completed DB-connected build/test invocation and no parity result.

### Blocker

```json
{
  "code": "DBT_PARITY_MISMATCH",
  "message": "fact_total_spent_sum delta 1.25 exceeds tolerance 0.01",
  "assertion_id": "fact_total_spent_sum"
}
```

`message` is sanitized and contains no absolute path, host, user, password, database, DSN, or raw adapter output.

## 10. State Transitions

```text
working set unresolved
  -> governance refusal (exit 3, zero dbt invocations)

gate allowed + project valid
  -> non-DB parse/list
  -> immutable plan + digest

accepted digest matches recomputed plan
  -> acquire table/target lock
  -> build or test fixed selector
  -> validate manifest/run-results
  -> show governed parity audit
  -> validate complete parity rows
  -> write normalized evidence
  -> recommend and STOP for named human
```

No transition writes a readiness stage or migration-switch approval.
