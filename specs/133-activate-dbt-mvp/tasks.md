# Activate the Professional dbt MVP Detailed TDD Tasks

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to execute these tasks in order. Use `superpowers:test-driven-development` for every behavior change and `superpowers:verification-before-completion` before any completion claim.

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md), and `contracts/`.

**Execution mode**: Inline in the isolated `133-activate-dbt-mvp` worktree. Subagent dispatch is not used for this session.

**Runtime boundary**: Python test commands are `[PENDING LOCAL PYTHON 3.13]` until an interpreter is available. Live database commands are `[PENDING LIVE PROFILE]` until dbt, a governed profile, and PostgreSQL are available. Pending is never pass.

## Task Map

| Task | Story | Independently reviewable outcome |
|---|---|---|
| T001 | US1/US5 | Package, profile, ignore, and JSON contract foundation |
| T002 | US1/US2 | Fail-closed Mapping Ready working-set gate |
| T003 | US2 | Static project, selector, shadow-schema, and citation validation |
| T004 | US3 | Shell-free runner, current-environment executable, redaction, and lock |
| T005 | US2/US3 | Artifact validation and immutable accepted plans |
| T006 | US3/US4 | Parity interpretation and normalized evidence |
| T007 | US3 | Complete shadow staging and gold-star dbt models |
| T008 | US3/US4 | dbt data tests and structured parity audit |
| T009 | US1/US2/US3 | Nested lazy CLI with stable exits and output |
| T010 | US3/US4 | Pinned dbt parse/compile and fixture artifact integration |
| T011 | US5 | Canonical public command/skill surface and generated bundles |
| T012 | US5 | Capability, ADR/integration, install, roadmap, and release reconciliation |
| T013 | US4 | Optional ephemeral-Postgres parity and divergence proof |
| T014 | All | Full verification, review, and human-stop handoff |

---

### T001 [US1] Establish package, profile, ignore, and schema contracts

**Files:**

- Modify: `pyproject.toml`
- Modify: `.gitignore`
- Modify: `profiles.example.yml`
- Create: `schemas/dbt-run-evidence.schema.json`
- Create: `tests/contract/test_dbt_package_contract.py`
- Create: `tests/contract/test_dbt_evidence_schema.py`

**Interfaces:**

- Produces optional extra `dbt = ["dbt-core==1.12.0", "dbt-postgres==1.10.2"]`.
- Produces environment keys `SESHAT_DBT_HOST`, `SESHAT_DBT_PORT`, `SESHAT_DBT_USER`, `SESHAT_DBT_PASSWORD`, `SESHAT_DBT_DBNAME`, `SESHAT_DBT_SCHEMA`, `SESHAT_DBT_SSLMODE`.
- Produces the canonical schema loaded later by `evidence.write_evidence()`.

- [ ] **Step 1: Write the package and profile contract tests**

```python
def test_dbt_extra_is_an_exact_tested_pair() -> None:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert payload["project"]["optional-dependencies"]["dbt"] == [
        "dbt-core==1.12.0",
        "dbt-postgres==1.10.2",
    ]


def test_dbt_local_outputs_are_ignored() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for line in ("/profiles.yml", "/dbt/target/", "/dbt/logs/", "/.seshat/dbt/"):
        assert line in text.splitlines()


def test_example_profile_uses_environment_references_only() -> None:
    text = (ROOT / "profiles.example.yml").read_text(encoding="utf-8")
    for key in (
        "SESHAT_DBT_HOST", "SESHAT_DBT_PORT", "SESHAT_DBT_USER",
        "SESHAT_DBT_PASSWORD", "SESHAT_DBT_DBNAME", "SESHAT_DBT_SCHEMA",
        "SESHAT_DBT_SSLMODE",
    ):
        assert f"env_var('{key}'" in text
    assert "<your-postgres-host>" not in text
```

- [ ] **Step 2: Run the tests and confirm RED**

Run: `python -m pytest tests/contract/test_dbt_package_contract.py -q`  
Expected: FAIL because the `dbt` extra and dbt ignore entries do not exist and the profile still contains literal placeholders.

- [ ] **Step 3: Add the exact extra, ignore rules, and environment-only profile**

Add to `pyproject.toml`:

```toml
dbt = [
    "dbt-core==1.12.0",
    "dbt-postgres==1.10.2",
]
```

Add to `.gitignore`:

```gitignore
# Governed dbt adapter local state (spec 133)
/profiles.yml
/dbt/target/
/dbt/logs/
/.seshat/dbt/
```

Replace the profile output with:

```yaml
seshat_bi_warehouse:
  target: shadow
  outputs:
    shadow:
      type: postgres
      host: "{{ env_var('SESHAT_DBT_HOST') }}"
      port: "{{ env_var('SESHAT_DBT_PORT', '5432') | int }}"
      user: "{{ env_var('SESHAT_DBT_USER') }}"
      password: "{{ env_var('SESHAT_DBT_PASSWORD') }}"
      dbname: "{{ env_var('SESHAT_DBT_DBNAME') }}"
      schema: "{{ env_var('SESHAT_DBT_SCHEMA', 'seshat_dbt_shadow') }}"
      threads: 4
      sslmode: "{{ env_var('SESHAT_DBT_SSLMODE', 'prefer') }}"
```

Copy the approved feature contract `specs/133-activate-dbt-mvp/contracts/dbt-run-evidence.schema.json` byte-for-byte to `schemas/dbt-run-evidence.schema.json` using `apply_patch`.

- [ ] **Step 4: Validate the JSON Schema contract**

Add a test that loads both schemas with `json.loads`, asserts equality, and verifies required top-level fields, `additionalProperties is False`, authority const, outcomes, and exit range. Run:

`python -m pytest tests/contract/test_dbt_package_contract.py tests/contract/test_dbt_evidence_schema.py -q`

Expected: PASS.

- [ ] **Step 5: Commit the foundation**

```text
git add pyproject.toml .gitignore profiles.example.yml schemas/dbt-run-evidence.schema.json tests/contract/test_dbt_package_contract.py tests/contract/test_dbt_evidence_schema.py
git commit -m "feat(dbt): establish governed package contracts"
```

---

### T002 [US1] Implement the fail-closed Mapping Ready gate

**Files:**

- Create: `src/seshat/dbt/__init__.py`
- Create: `src/seshat/dbt/contracts.py`
- Create: `src/seshat/dbt/gate.py`
- Create: `tests/unit/dbt/test_gate.py`

**Interfaces:**

- Produces `WorkingSet`, `MappingApproval`, `Blocker`, `GateDecision`, and `GovernanceError`.
- Produces `resolve_working_set(repo_root: Path, table_id: str) -> WorkingSet`.
- Produces `evaluate_mapping_gate(working_set: WorkingSet) -> GateDecision`.

- [ ] **Step 1: Write table-driven gate tests before source code**

```python
@pytest.mark.parametrize(
    ("mapping_status", "approval", "gate_line", "allowed", "code"),
    [
        ("pass", {"stage": "mapping_ready", "owner": "A Owner", "at": "2026-07-16", "note": "approved"}, "Gate status: CLEARED", True, None),
        ("blocked", {"stage": "mapping_ready", "owner": "A Owner", "at": "2026-07-16", "note": "approved"}, "Gate status: CLEARED", False, "DBT_MAPPING_NOT_PASS"),
        ("pass", None, "Gate status: CLEARED", False, "DBT_MAPPING_APPROVAL_MISSING"),
        ("pass", {"stage": "mapping_ready", "owner": "A Owner", "at": "2026-07-16", "note": "approved"}, "Gate status: BLOCKED", False, "DBT_MAPPING_MIRROR_BLOCKED"),
    ],
)
def test_mapping_gate_fails_closed(mapping_fixture, mapping_status, approval, gate_line, allowed, code):
    working_set = mapping_fixture(mapping_status, approval, gate_line)
    decision = evaluate_mapping_gate(working_set)
    assert decision.allowed is allowed
    assert ([b.code for b in decision.blocking_reasons] or [None])[0] == code
```

Also test invalid table IDs, zero/two matching directories, absent/dirty/untracked maps, malformed YAML, missing open-question mirror, and an approval without owner/date.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/unit/dbt/test_gate.py -q`  
Expected: collection FAIL with `ModuleNotFoundError: No module named 'seshat.dbt'`.

- [ ] **Step 3: Implement immutable gate data types**

Use frozen dataclasses and tuples. `Blocker` is exactly:

```python
@dataclass(frozen=True, slots=True)
class Blocker:
    code: str
    message: str
    assertion_id: str | None = None
```

Derive `approval_id` with canonical JSON:

```python
payload = json.dumps(approval, sort_keys=True, separators=(",", ":")).encode("utf-8")
approval_id = hashlib.sha256(payload).hexdigest()
```

- [ ] **Step 4: Implement exact working-set and gate resolution**

`resolve_working_set` validates `^[a-z][a-z0-9_]*$`, joins exact paths, checks `git ls-files --error-unmatch -- <map>`, checks `git diff --quiet HEAD -- <map>`, obtains `git rev-parse HEAD:<map>`, and hashes current bytes. It never searches fuzzy table aliases.

`evaluate_mapping_gate` uses `yaml.safe_load`, reads `stages.mapping_ready.status`, selects exactly one valid `approvals[]` row whose `stage == "mapping_ready"`, and accepts the mirror only when the Markdown contains exactly one `Gate status: CLEARED` and no open rows.

- [ ] **Step 5: Run GREEN and commit**

Run: `python -m pytest tests/unit/dbt/test_gate.py -q`  
Expected: PASS.

```text
git add src/seshat/dbt tests/unit/dbt/test_gate.py
git commit -m "feat(dbt): enforce the mapping entry gate"
```

---

### T003 [US2] Validate project, selector, shadow schemas, and model citations

**Files:**

- Create: `src/seshat/dbt/project.py`
- Create: `tests/unit/dbt/test_project.py`
- Create: `tests/fixtures/dbt_project/valid/`
- Create: `tests/fixtures/dbt_project/unsafe_profile/`
- Create: `tests/fixtures/dbt_project/stale_citation/`

**Interfaces:**

- Produces `ProjectValidation`, `ShadowSchemas`, `ModelContract`, and `ColumnCitation` in `contracts.py`.
- Produces `validate_project(repo_root: Path, working_set: WorkingSet) -> ProjectValidation`.
- Produces `fingerprint_project(repo_root: Path) -> str`.

- [ ] **Step 1: Write failing fingerprint/profile/schema/citation tests**

```python
def test_project_fingerprint_is_path_order_independent(valid_project: Path) -> None:
    first = fingerprint_project(valid_project.parent)
    os.utime(valid_project / "dbt" / "dbt_project.yml", None)
    assert fingerprint_project(valid_project.parent) == first


def test_profile_rejects_literal_connection_values(project_fixture) -> None:
    result = validate_project(project_fixture("unsafe_profile"), approved_working_set())
    assert not result.valid
    assert "DBT_PROFILE_LITERAL_VALUE" in {b.code for b in result.blocking_reasons}


def test_every_manifest_output_column_requires_a_current_citation(project_fixture) -> None:
    result = validate_project(project_fixture("stale_citation"), approved_working_set())
    assert not result.valid
    assert "DBT_MODEL_CITATION_STALE" in {b.code for b in result.blocking_reasons}
```

Test unsafe identifiers, direct `silver`/`gold`, missing selector, selector mismatch, missing model contract, missing output column citation, worked-table answers in generic macro/template paths, and ignored directory exclusion from fingerprints.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/unit/dbt/test_project.py -q`  
Expected: FAIL because `seshat.dbt.project` is absent.

- [ ] **Step 3: Implement deterministic fingerprint and profile validation**

Fingerprint algorithm:

```python
digest = hashlib.sha256()
for path in sorted(project_dir.rglob("*")):
    if not path.is_file() or {"target", "logs", "dbt_packages"} & set(path.parts):
        continue
    relative = path.relative_to(repo_root).as_posix().encode("utf-8")
    digest.update(len(relative).to_bytes(4, "big"))
    digest.update(relative)
    content = path.read_bytes()
    digest.update(len(content).to_bytes(8, "big"))
    digest.update(content)
return digest.hexdigest()
```

Parse profile YAML as text plus YAML structure: every connection field value must contain only a Jinja `env_var()` expression or a non-secret constant (`type`, `threads`). Validate the profile is ignored with `git check-ignore --quiet profiles.yml` when present.

- [ ] **Step 4: Implement selector, shadow schema, and citation validation**

Require selector `seshat_table_<table_id>`, target `shadow`, profile `seshat_bi_warehouse`, layers exactly `silver|gold|audit`, and property YAML `meta.seshat`. Compare every `source_map_revision` with the `WorkingSet` blob and every output column with a source or allowlisted derivation.

- [ ] **Step 5: Run GREEN and commit**

Run: `python -m pytest tests/unit/dbt/test_project.py -q`  
Expected: PASS.

```text
git add src/seshat/dbt/project.py src/seshat/dbt/contracts.py tests/unit/dbt/test_project.py tests/fixtures/dbt_project
git commit -m "feat(dbt): validate project and lineage contracts"
```

---

### T004 [US3] Build the shell-free runner, redaction, and target lock

**Files:**

- Create: `src/seshat/dbt/redaction.py`
- Create: `src/seshat/dbt/runner.py`
- Create: `tests/unit/dbt/test_redaction.py`
- Create: `tests/unit/dbt/test_runner.py`

**Interfaces:**

- Produces `Operation`, `RunContext`, `InvocationResult`, `DbtUnavailable`, and `LockUnavailable`.
- Produces `resolve_dbt_executable`, `build_dbt_argv`, `invoke_dbt`, and `target_lock` signatures from `plan.md`.
- Produces `load_child_environment(repo_root: Path) -> dict[str, str]` and `sanitize(value, secrets, repo_root)`.

- [ ] **Step 1: Write failing argv, shell, lock, and redaction tests**

```python
def test_build_argv_has_fixed_governed_selector(context: RunContext) -> None:
    argv = build_dbt_argv(Operation.BUILD, context)
    assert argv[1:4] == ("build", "--select", "selector:seshat_table_retail_store_sales")
    assert "--target" in argv and "shadow" in argv
    assert all(";" not in part and "&&" not in part for part in argv)


def test_invoke_never_uses_a_shell(monkeypatch, context: RunContext) -> None:
    seen = {}
    monkeypatch.setattr(subprocess, "run", lambda argv, **kw: seen.update(argv=argv, kw=kw) or completed())
    invoke_dbt(context, build_dbt_argv(Operation.PARSE, context))
    assert seen["kw"]["shell"] is False
    assert isinstance(seen["argv"], tuple)


def test_component_redaction_removes_reformatted_credentials(tmp_path: Path) -> None:
    text = 'connection to server at "private-host" failed for user "private-user" password private-pass'
    clean = sanitize(text, ("private-host", "private-user", "private-pass"), tmp_path)
    assert "private-" not in clean
```

Test no global PATH fallback, timeout handling, expected exceptions without traceback, recursive object redaction, absolute repo/home path replacement, lock refusal, stale lock non-deletion, and lock cleanup in `finally`.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/unit/dbt/test_runner.py tests/unit/dbt/test_redaction.py -q`  
Expected: FAIL because runner/redaction modules are absent.

- [ ] **Step 3: Implement environment and redaction first**

Parse `.env` lines as `KEY=VALUE`, ignore blank/comments, reject malformed or duplicate keys, and overlay them only into a child environment. Build the secret set from non-empty values for the seven `SESHAT_DBT_*` keys. `sanitize` recursively handles strings, mappings, tuples, and lists; redact longest secrets first, then parsed URI components, then repo/home absolute paths.

- [ ] **Step 4: Implement executable, fixed argv, subprocess, and lock**

Resolve `dbt.exe`/`dbt` only under `sysconfig.get_path("scripts")`. Use `subprocess.run(argv, cwd=project_dir, env=child_env, capture_output=True, text=True, timeout=timeout_s, shell=False, check=False)`. The lock uses `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`, polls no longer than one second, writes sanitized PID/timestamp metadata, and deletes only the lock it acquired.

- [ ] **Step 5: Run GREEN and commit**

Run: `python -m pytest tests/unit/dbt/test_runner.py tests/unit/dbt/test_redaction.py -q`  
Expected: PASS.

```text
git add src/seshat/dbt/redaction.py src/seshat/dbt/runner.py src/seshat/dbt/contracts.py tests/unit/dbt/test_runner.py tests/unit/dbt/test_redaction.py
git commit -m "feat(dbt): add isolated runner and redaction"
```

---

### T005 [US2] Validate artifacts and create immutable accepted plans

**Files:**

- Create: `src/seshat/dbt/artifacts.py`
- Create: `src/seshat/dbt/planning.py`
- Create: `tests/unit/dbt/test_artifacts.py`
- Create: `tests/unit/dbt/test_planning.py`
- Create: `tests/fixtures/dbt_artifacts/manifest-v12.json`
- Create: `tests/fixtures/dbt_artifacts/run-results-v6.json`

**Interfaces:**

- Produces `ManifestSummary`, `RunResultsSummary`, `ArtifactSet`, `ExecutionPlan`, `PlanEnvelope`, and `PlanDrift`.
- Consumes the gate, project validation, and runner.

- [ ] **Step 1: Write failing schema/node and digest-drift tests**

```python
def test_plan_digest_is_deterministic(sample_plan: ExecutionPlan) -> None:
    assert plan_digest(sample_plan) == plan_digest(sample_plan)
    assert len(plan_digest(sample_plan)) == 64


@pytest.mark.parametrize(
    "field",
    ["mapping", "project", "runtime", "schemas", "manifest", "selected_unique_ids"],
)
def test_each_bound_fact_changes_the_digest(sample_plan, mutate_plan, field) -> None:
    assert plan_digest(mutate_plan(sample_plan, field)) != plan_digest(sample_plan)


def test_run_results_reject_nodes_outside_accepted_plan(sample_plan, run_results_path) -> None:
    results = load_run_results(run_results_path)
    with pytest.raises(ArtifactIntegrityError, match="outside accepted plan"):
        cross_check_execution(sample_plan, results)
```

Also test unknown manifest/run-results schema URI, malformed JSON, metadata version mismatch, dictionary key/unique-ID mismatch, duplicate selected IDs, extra model nodes, allowed generated test nodes, and local plan path containment.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/unit/dbt/test_artifacts.py tests/unit/dbt/test_planning.py -q`  
Expected: FAIL because artifact/planning modules are absent.

- [ ] **Step 3: Implement strict artifact summaries**

Accept exact URIs:

```python
MANIFEST_V12 = "https://schemas.getdbt.com/dbt/manifest/v12.json"
RUN_RESULTS_V6 = "https://schemas.getdbt.com/dbt/run-results/v6.json"
```

Retain only the fields defined in `data-model.md`. Validate `metadata.dbt_version == "1.12.0"`, `args.which`, node key equality, statuses, and SHA-256. Never retain compiled SQL or adapter messages.

- [ ] **Step 4: Implement parse/list plan creation and exact acceptance**

`create_plan` performs gate and project validation, invokes fixed `parse` and `ls`, loads manifest v12, parses newline-delimited JSON from `dbt ls`, sorts unique IDs, constructs `ExecutionPlan`, and does not include a timestamp. Canonicalize with:

```python
json.dumps(asdict(plan), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
```

`save_plan` writes the envelope atomically through a sibling temporary path and `Path.replace`. `require_accepted_plan` uses `hmac.compare_digest(expected_digest, plan_digest(actual))` and raises `PlanDrift` before any build/test call.

- [ ] **Step 5: Run GREEN and commit**

Run: `python -m pytest tests/unit/dbt/test_artifacts.py tests/unit/dbt/test_planning.py -q`  
Expected: PASS.

```text
git add src/seshat/dbt/artifacts.py src/seshat/dbt/planning.py src/seshat/dbt/contracts.py tests/unit/dbt/test_artifacts.py tests/unit/dbt/test_planning.py tests/fixtures/dbt_artifacts
git commit -m "feat(dbt): bind immutable plans to verified artifacts"
```

---

### T006 [US3] Normalize parity and evidence without granting approval

**Files:**

- Create: `src/seshat/dbt/evidence.py`
- Create: `tests/unit/dbt/test_evidence.py`
- Create: `tests/fixtures/dbt_artifacts/show-parity-pass.jsonl`
- Create: `tests/fixtures/dbt_artifacts/show-parity-missing.jsonl`
- Create: `tests/fixtures/dbt_artifacts/show-parity-fail.jsonl`

**Interfaces:**

- Produces `ParityAssertion`, `TestSummary`, and `RunEvidence`.
- Produces `parse_parity_rows`, `build_evidence`, and `write_evidence` from `plan.md`.

- [ ] **Step 1: Write failing completeness, tolerance, authority, and secret tests**

```python
def test_complete_parity_passes(pass_stdout: str) -> None:
    rows = parse_parity_rows(pass_stdout)
    assert {row.assertion_id for row in rows} == REQUIRED_RETAIL_STORE_SALES_ASSERTIONS
    assert all(row.passed for row in rows)


def test_missing_parity_row_blocks_even_with_green_tests(missing_stdout: str, green_artifacts) -> None:
    with pytest.raises(ArtifactIntegrityError, match="missing parity assertions"):
        build_evidence(sample_plan(), successful_invocation(), green_artifacts, parse_parity_rows(missing_stdout))


def test_evidence_never_changes_readiness(pass_evidence: RunEvidence) -> None:
    payload = evidence_to_dict(pass_evidence)
    assert payload["authority"] == "derived-evidence-only"
    assert payload["readiness_effect"] == "none; named-human approval required"
    assert "readiness_status" not in payload
```

Test delta `0.01` passes, `0.0101` fails, duplicate IDs fail, incorrect `passed` booleans are recomputed/rejected, failed rows create concrete blockers, evidence path containment, JSON Schema validation, stable key order, and secret/path absence.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/unit/dbt/test_evidence.py -q`  
Expected: FAIL because `seshat.dbt.evidence` is absent.

- [ ] **Step 3: Implement machine-readable show parsing**

Parse JSON lines, select exactly one dbt event whose structured payload contains the audit rows, convert numeric values through `Decimal(str(value))`, emit canonical decimal strings, and require the eight IDs from `data-model.md`. Ignore ordinary log events; reject zero or multiple result events.

- [ ] **Step 4: Implement normalized evidence and atomic write**

Outcome rules:

```python
if invocation.return_code != 0:
    outcome, exit_code = "failed", 1
elif any(not row.passed for row in parity):
    outcome, exit_code = "blocked", 1
else:
    outcome, exit_code = "pass", 0
```

Build test counts from normalized node results; include the repository-relative map path, map revision, elapsed seconds, and every artifact hash; sanitize the complete dictionary; validate it against the root JSON Schema; and atomically write `mappings/<table>/dbt-evidence/<invocation-id>.json`. Never edit readiness YAML. `doctor`, `validate`, and `plan` return stable CLI results but do not write parity run evidence.

- [ ] **Step 5: Run GREEN and commit**

Run: `python -m pytest tests/unit/dbt/test_evidence.py tests/contract/test_dbt_evidence_schema.py -q`  
Expected: PASS.

```text
git add src/seshat/dbt/evidence.py src/seshat/dbt/contracts.py tests/unit/dbt/test_evidence.py tests/fixtures/dbt_artifacts/show-parity-*.jsonl
git commit -m "feat(dbt): emit sanitized parity evidence"
```

---

### T007 [US3] Create the complete shadow staging and gold-star dbt project

**Files:**

- Create: `dbt/dbt_project.yml`
- Create: `dbt/selectors.yml`
- Create: `dbt/macros/generate_schema_name.sql`
- Create: `dbt/models/sources/_sources.yml`
- Create: `dbt/models/staging/retail_store_sales/stg_retail_store_sales.sql`
- Create: `dbt/models/staging/retail_store_sales/_models.yml`
- Create: `dbt/models/marts/retail_store_sales/dim_customer_rss.sql`
- Create: `dbt/models/marts/retail_store_sales/dim_product_rss.sql`
- Create: `dbt/models/marts/retail_store_sales/dim_payment_method_rss.sql`
- Create: `dbt/models/marts/retail_store_sales/dim_location_rss.sql`
- Create: `dbt/models/marts/retail_store_sales/dim_date_rss.sql`
- Create: `dbt/models/marts/retail_store_sales/fct_sales_rss.sql`
- Create: `dbt/models/marts/retail_store_sales/_models.yml`
- Create: `tests/contract/test_dbt_project.py`

**Interfaces:**

- Produces selector `seshat_table_retail_store_sales` tagged across the seven transformation models and their tests.
- Produces refs used by the audit model in T008.

- [ ] **Step 1: Write static project contract tests**

```python
EXPECTED_MODELS = {
    "stg_retail_store_sales",
    "dim_customer_rss",
    "dim_product_rss",
    "dim_payment_method_rss",
    "dim_location_rss",
    "dim_date_rss",
    "fct_sales_rss",
}


def test_worked_project_has_complete_star() -> None:
    sql_names = {path.stem for path in (ROOT / "dbt/models").rglob("*.sql")}
    assert EXPECTED_MODELS <= sql_names


def test_no_model_targets_migration_owned_schemas() -> None:
    for path in (ROOT / "dbt").rglob("*.yml"):
        text = path.read_text(encoding="utf-8")
        assert "schema: silver" not in text
        assert "schema: gold" not in text
```

Also assert the macro allows only `silver`, `gold`, `audit`, selector name is exact, every model has a filled current citation, every properties YAML output column is cited, and generic macro/project files contain no worked-table business answer.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/contract/test_dbt_project.py -q`  
Expected: FAIL because `dbt/` is absent.

- [ ] **Step 3: Create project, selector, source, schema macro, and staging model**

Use project configuration:

```yaml
name: seshat_bi
version: 1.0.0
config-version: 2
profile: seshat_bi_warehouse
model-paths: [models]
macro-paths: [macros]
clean-targets: [target, dbt_packages]
models:
  seshat_bi:
    staging:
      +materialized: table
      +schema: silver
    marts:
      +materialized: table
      +schema: gold
    audit:
      +materialized: view
      +schema: audit
```

`stg_retail_store_sales.sql` must reproduce migration 0003 exactly: trim/empty-to-null text, numeric/date casts, blank discount to null boolean, retain lineage fields only if contracted, and no sentinel update.

- [ ] **Step 4: Create deterministic dimensions and fact**

Each entity dimension unions the explicit `-1` unknown row with deterministic natural members and uses `row_number() over (order by <natural-key>)` for positive keys. `dim_date_rss` uses `generate_series(date '2022-01-01', date '2025-01-18', interval '1 day')`, has no unknown row, and creates YYYYMMDD `date_sk`. The fact joins every dimension, coalesces only entity keys to `-1`, leaves date unmatched to fail, and emits transaction, discount, and approved measures.

- [ ] **Step 5: Fill properties contracts and run GREEN**

Each model `meta.seshat.source_map_revision` must be the current `git rev-parse HEAD:mappings/retail_store_sales/source-map.yaml` value at authoring time. Each column names source columns or one of the recognized physical derivations. Run:

`python -m pytest tests/contract/test_dbt_project.py tests/unit/dbt/test_project.py -q`

Expected: PASS.

- [ ] **Step 6: Commit the transformation project**

```text
git add dbt tests/contract/test_dbt_project.py
git commit -m "feat(dbt): add the retail shadow star"
```

---

### T008 [US4] Add dbt data tests and the structured parity audit

**Files:**

- Create: `dbt/models/audit/retail_store_sales/audit_retail_store_sales_parity.sql`
- Create: `dbt/models/audit/retail_store_sales/_models.yml`
- Modify: `dbt/models/marts/retail_store_sales/_models.yml`
- Modify: `dbt/selectors.yml`
- Modify: `tests/contract/test_dbt_project.py`

**Interfaces:**

- Produces all test nodes selected by `seshat_table_retail_store_sales`.
- Produces the exact eight audit rows consumed by `parse_parity_rows()`.

- [ ] **Step 1: Extend static tests and confirm RED**

Assert fact `transaction_id` has `unique` and `not_null`; customer/product/payment/location/date keys each have a `relationships` test to the corresponding dimension; audit SQL includes all eight assertion IDs and required output columns.

Run: `python -m pytest tests/contract/test_dbt_project.py -q`  
Expected: FAIL because tests/audit model are absent.

- [ ] **Step 2: Add fact and relationship tests**

Use dbt properties `data_tests` entries. Every relationship targets `ref()` and the exact surrogate key. Tag tests so the governed selector includes them; do not use package dependencies for standard tests.

- [ ] **Step 3: Implement the audit model as eight unioned rows**

Each row returns:

```sql
select
  'fact_row_count'::text as assertion_id,
  'fact_row_count'::text as assertion_class,
  'fct_sales_rss'::text as subject,
  expected_value::numeric::text as expected,
  actual_value::numeric::text as actual,
  abs(expected_value - actual_value)::numeric::text as delta,
  '0'::text as tolerance,
  abs(expected_value - actual_value) <= 0::numeric as passed
```

Repeat with the correct migration relation and `ref()` target for business-key count, `total_spent` sum tolerance `0.01`, and five dimension member counts. The output has exactly the fields and IDs in `data-model.md`.

- [ ] **Step 4: Validate selector and contract tests**

Run: `python -m pytest tests/contract/test_dbt_project.py tests/unit/dbt/test_evidence.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit parity and tests**

```text
git add dbt/models dbt/selectors.yml tests/contract/test_dbt_project.py
git commit -m "feat(dbt): prove shadow parity against migrations"
```

---

### T009 [US1] Add the nested lazy CLI and stable exit mapping

**Files:**

- Create: `src/seshat/cli/parser_dbt.py`
- Create: `src/seshat/cli/commands/dbt.py`
- Modify: `src/seshat/cli/parser.py`
- Modify: `src/seshat/cli/__init__.py`
- Create: `tests/unit/test_cli_dbt.py`
- Modify: `tests/unit/test_cli.py`

**Interfaces:**

- Produces `_DISPATCH["dbt"] = _lazy(".commands.dbt", "dbt_main")`.
- Consumes all adapter services from T002-T006.

- [ ] **Step 1: Write parser/dispatch/lazy/error tests**

```python
def test_dbt_group_exposes_exact_subcommands() -> None:
    parser = _build_parser()
    help_text = parser.parse_args(["dbt", "doctor", "--help"])
    assert help_text is not None


@pytest.mark.parametrize("command", ["doctor", "validate", "plan", "build", "test", "inspect-run"])
def test_dbt_subcommands_are_parseable(command: str) -> None:
    argv = ["dbt", command]
    if command != "doctor":
        argv += ["--table", "retail_store_sales"]
    if command in {"build", "test"}:
        argv += ["--accept-plan", "a" * 64]
    if command == "inspect-run":
        argv += ["--artifacts", ".seshat/dbt/runs/run-id"]
    assert _build_parser().parse_args(argv).dbt_command == command
```

Also assert base `import seshat.cli` does not import a module named `dbt`, no forbidden raw flag parses, handled errors return 1/2/3/4 without traceback, JSON output is one object, and output contains no patched secret/path.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/unit/test_cli_dbt.py -q`  
Expected: FAIL because the `dbt` group is absent.

- [ ] **Step 3: Implement exact nested argparse surface**

`parser_dbt.py` creates one parent parser and six child parsers. Common options are `--repo` and `--format {text,json}`. Table commands require `--table`; build/test require a 64-hex `--accept-plan`; inspect-run requires `--artifacts`. Add no other dbt flags.

- [ ] **Step 4: Implement orchestration and stable presentation**

`dbt_main(args)` dispatches to private functions by `args.dbt_command`, catches `DbtUnavailable -> 2`, `GovernanceError|PlanDrift|LockUnavailable -> 3`, `ArtifactIntegrityError -> 4`, and handled dbt/parity failure -> 1. It never catches unexpected programmer exceptions. Expected exceptions print sanitized messages and no traceback. Build/test always recompute and compare the plan before entering `target_lock` and invoking DB-connected operations.

- [ ] **Step 5: Run GREEN and commit**

Run: `python -m pytest tests/unit/test_cli_dbt.py tests/unit/test_cli.py -q`  
Expected: PASS.

```text
git add src/seshat/cli src/seshat/dbt tests/unit/test_cli_dbt.py tests/unit/test_cli.py
git commit -m "feat(dbt): expose the governed CLI workflow"
```

---

### T010 [US3] Prove the pinned dbt pair and fixture artifact flow

**Files:**

- Create: `tests/integration/test_dbt_artifact_flow.py`
- Modify: `tests/fixtures/dbt_artifacts/manifest-v12.json`
- Modify: `tests/fixtures/dbt_artifacts/run-results-v6.json`
- Modify: `docs/operations/adapter-compatibility-matrix.md`

**Interfaces:**

- Produces real pinned manifest/list/compile fixtures or a concrete compatibility blocker.

- [ ] **Step 1: Install the exact optional pair in Python 3.13**

Run: `python -m pip install -e ".[dev,dbt]"`  
Expected: successful resolver output with Core 1.12.0 and Postgres 1.10.2. If not available, record `[PENDING LOCAL PYTHON 3.13]` and do not fabricate fixtures.

- [ ] **Step 2: Run non-DB parse/list and inspect artifact versions**

With environment variables set to non-secret local placeholders sufficient for parse/list:

```text
dbt parse --project-dir dbt --profiles-dir . --target shadow --no-partial-parse
dbt ls --project-dir dbt --profiles-dir . --target shadow --select selector:seshat_table_retail_store_sales --output json
```

Expected: no DB query, manifest URI v12, Core 1.12.0, and the complete governed model/test selection.

- [ ] **Step 3: Write the integration test around copied sanitized fixtures**

```python
def test_pinned_artifacts_round_trip() -> None:
    manifest = load_manifest(FIXTURES / "manifest-v12.json")
    results = load_run_results(FIXTURES / "run-results-v6.json")
    plan = fixture_execution_plan(manifest)
    cross_check_execution(plan, results)
    assert manifest.schema_uri.endswith("/v12.json")
    assert results.schema_uri.endswith("/v6.json")
```

Sanitize absolute paths, compiled SQL, adapter messages, IDs unrelated to the governed selector, and connection metadata before committing fixtures.

- [ ] **Step 4: Run compile and integration GREEN**

Run: `dbt compile --project-dir dbt --profiles-dir . --target shadow --select selector:seshat_table_retail_store_sales`  
Run: `python -m pytest tests/integration/test_dbt_artifact_flow.py -q`  
Expected: PASS. Update the compatibility matrix with the exact pair and artifact schemas.

- [ ] **Step 5: Commit compatibility evidence**

```text
git add tests/integration/test_dbt_artifact_flow.py tests/fixtures/dbt_artifacts docs/operations/adapter-compatibility-matrix.md
git commit -m "test(dbt): verify the pinned artifact contract"
```

---

### T011 [US5] Ship the canonical public dbt agent surface

**Dependency stop**: Do not edit the listed registry/templates until the primary checkout's feature-126 canonical public-command-surface work is committed and integrated into this worktree. Never reconstruct or overwrite that uncommitted work.

**Files:**

- Modify: `distribution/public-command-surface.yaml`
- Modify: `distribution/public-knowledge-allowlist.yaml`
- Create: `distribution/bundle-templates/claude/commands/dbt-doctor.md`
- Create: `distribution/bundle-templates/claude/commands/dbt-plan.md`
- Create: `distribution/bundle-templates/claude/commands/dbt-build.md`
- Create: `distribution/bundle-templates/claude/commands/dbt-review.md`
- Create: `distribution/bundle-templates/shared/skills/dbt-workflows/SKILL.md`
- Modify: `distribution/bundle-templates/shared/skills/seshat-bi/SKILL.md`
- Modify: `distribution/bundle-templates/claude/commands/seshat-help.md`
- Modify: `docs/install/agent-install.md`
- Regenerate: `integrations/claude-code/seshat-bi/`
- Regenerate: `integrations/codex/seshat-bi/`
- Create: `tests/contract/test_dbt_public_surface.py`

**Interfaces:**

- Produces one `dbt-workflows` skill in both platform bundles.
- Produces four Claude commands mapped to real CLI verbs/agent stops.

- [ ] **Step 1: Integrate the owning command-surface change and confirm a clean base**

Use a non-destructive rebase or cherry-pick only after the owning commit exists. Run `git status --short` and verify no files outside feature 133 are unintentionally changed.

- [ ] **Step 2: Write failing canonical-surface tests**

```python
def test_public_surface_declares_dbt_skill_and_commands() -> None:
    surface = load_public_surface()
    assert {"dbt-doctor", "dbt-plan", "dbt-build", "dbt-review"} <= {
        item["name"] for item in surface["commands"] if item["status"] == "shipped"
    }
    skill = next(item for item in surface["skills"] if item["name"] == "dbt-workflows")
    assert skill["platforms"] == ["claude", "codex"]
```

Also assert wrappers route to the shared skill, mention only real `seshat dbt` commands, encode named-human stops, contain no `.claude/skills/` path, are allowlisted, and generated trees equal templates.

- [ ] **Step 3: Add registry, portable skill, and thin wrappers**

Command mapping:

| Wrapper | CLI/helper behavior | Mode/gate |
|---|---|---|
| `dbt-doctor` | `seshat dbt doctor` then explain blockers | read-only |
| `dbt-plan` | validate + plan + show digest for review | read-only, mapping approval |
| `dbt-build` | build/test only with accepted digest | mutating, mapping approval + accepted plan |
| `dbt-review` | inspect normalized evidence and stop for human | read-only, named-human approval |

The shared skill contains the full fixed workflow and `[PENDING LIVE PROFILE]` behavior. Wrappers only invoke and route.

- [ ] **Step 4: Regenerate bundles and run contract tests**

Run: `python scripts/export_agent_bundles.py`  
Run: `python -m pytest tests/contract/test_public_command_surface.py tests/contract/test_dbt_public_surface.py tests/contract/test_claude_plugin_bundle.py tests/contract/test_codex_plugin_bundle.py -q`  
Expected: PASS and identical regenerated trees.

- [ ] **Step 5: Commit the public surface**

```text
git add distribution integrations docs/install/agent-install.md tests/contract/test_dbt_public_surface.py
git commit -m "feat(dbt): ship public agent workflows"
```

---

### T012 [US5] Reconcile capability and historical documentation

**Files:**

- Modify: `.claude/skills/dbt-transformation-adapter/SKILL.md`
- Modify: `docs/integrations/dbt-adapter.md`
- Modify: `docs/decisions/0009-dbt-is-transformation-adapter.md`
- Modify: `templates/dbt-adapter-contract.md`
- Modify: `templates/dbt-model-contract.md`
- Modify: `docs/capabilities/capabilities.yaml`
- Modify: `docs/roadmap/roadmap.md`
- Modify: `docs/worked-examples/retail-store-sales.md`
- Modify: `docs/install/developer-install.md`
- Modify: `docs/operations/adapter-update-policy.md`
- Modify: `CHANGELOG.md`
- Modify: `CLAUDE.md`
- Modify: `AGENTS.md`
- Create: `tests/contract/test_dbt_documentation.py`

**Interfaces:**

- Capability state is derived from real feeders: CLI dispatch, runtime project, public skill/bundles, exact extra, and tests.
- ADR remains historical and records that feature 133 activated the planned runtime; it is not rewritten as though runtime existed in 2026-06-26.

- [ ] **Step 1: Write stale-claim tests and confirm RED**

```python
STALE = (
    "the dbt project itself is a PLANNED future output",
    "this slice creates NO dbt files",
    "Until the dbt project exists",
)


def test_active_dbt_docs_do_not_claim_runtime_is_absent() -> None:
    for relative in ACTIVE_DBT_DOCS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for phrase in STALE:
            assert phrase not in text, relative
```

Also assert history mentions feature 023 planning and feature 133 activation, capability does not claim shipped without feeders, exact versions agree across docs, and `AGENTS.md` active Spec Kit plan points to feature 133 while this branch is active.

- [ ] **Step 2: Reconcile active docs and skill**

Replace future-runtime instructions with real `seshat dbt` commands, shadow-schema semantics, immutable plan, `.env`-only secrets, normalized evidence, and named-human stop. Keep ADR's original decision date/status and append an activation note referencing feature 133.

- [ ] **Step 3: Correct the capability claim**

The dbt capability declares Execution Adapter / DB-connected, command `dbt`, optional extra `dbt`, runtime project `dbt/dbt_project.yml`, public skill `dbt-workflows`, and required tests. Capability feeder code must compute `shipped` only when those files/dispatch/tests exist; otherwise it is `partial` or `planned`, never advisory-only shipped.

- [ ] **Step 4: Run documentation/capability contracts**

Run: `python -m pytest tests/contract/test_dbt_documentation.py tests/unit/test_distribution_compat.py tests/contract/test_generated_agent_bundles.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit reconciliation**

```text
git add .claude/skills/dbt-transformation-adapter AGENTS.md CLAUDE.md CHANGELOG.md docs templates tests/contract/test_dbt_documentation.py
git commit -m "docs(dbt): reconcile the activated adapter boundary"
```

---

### T013 [US4] Add optional ephemeral-Postgres parity and divergence proof

**Files:**

- Create: `tests/live_db/test_dbt_retail_store_sales.py`
- Create: `tests/live_db/seeds/dbt_retail_store_sales.sql`
- Modify: `tests/live_db/conftest.py`
- Modify: `docs/operations/adapter-compatibility-matrix.md`

**Interfaces:**

- Reuses existing `live_db`, `db`, `dbt`, and `livetest` extras.
- Produces no committed real DSN or raw dbt artifact.

- [ ] **Step 1: Write live tests with truthful skip behavior**

```python
@pytest.mark.live_db
def test_migration_and_shadow_outputs_have_complete_parity(live_dbt_project) -> None:
    evidence = live_dbt_project.build("retail_store_sales")
    assert evidence.outcome == "pass"
    assert len(evidence.parity) == 8
    assert all(row.passed for row in evidence.parity)


@pytest.mark.live_db
@pytest.mark.parametrize(
    "mutation,assertion_id",
    [
        ("delete_fact", "fact_row_count"),
        ("duplicate_business_key", "fact_distinct_transaction_id"),
        ("change_money", "fact_total_spent_sum"),
        ("remove_unknown_member", "dim_product_member_count"),
    ],
)
def test_each_parity_class_blocks(live_dbt_project, mutation, assertion_id) -> None:
    evidence = live_dbt_project.build_with_mutation(mutation)
    assert evidence.outcome == "blocked"
    assert assertion_id in {b.assertion_id for b in evidence.blocking_reasons}
```

Use `pytest.importorskip` for optional libraries and report the skip reason as `[PENDING LIVE PROFILE]`; no broad exception-to-pass behavior.

- [ ] **Step 2: Seed and apply the retained migrations in disposable Postgres**

The fixture starts one container, loads a deterministic subset with null item/discount cases, applies migrations 0003/0004, creates child-only profile environment, and invokes the real CLI. It never prints or writes the container DSN to tracked files.

- [ ] **Step 3: Run live RED/GREEN**

Run: `python -m pytest tests/live_db/test_dbt_retail_store_sales.py -m live_db -v`  
Expected when prerequisites exist: all matching and divergence tests PASS.  
Expected when unavailable: explicit SKIP containing `[PENDING LIVE PROFILE]`; do not count as live pass.

- [ ] **Step 4: Record compatibility outcome and commit**

```text
git add tests/live_db docs/operations/adapter-compatibility-matrix.md
git commit -m "test(dbt): verify live shadow parity"
```

---

### T014 [All] Run full verification and stop for review

**Files:**

- Modify only files required to fix verified defects.
- Do not write readiness `pass`, migration-switch approval, or Power BI execution artifacts.

- [ ] **Step 1: Read `superpowers:verification-before-completion` fully and construct the verification matrix**

Required matrix rows: unit, contract, integration, lint, static gate, bundle equality, package build/import, secret scan, git diff integrity, pinned dbt parse/compile, optional live DB.

- [ ] **Step 2: Run focused and full Python verification**

```text
python -m pytest tests/unit/dbt tests/unit/test_cli_dbt.py tests/contract/test_dbt_package_contract.py tests/contract/test_dbt_evidence_schema.py tests/contract/test_dbt_project.py tests/contract/test_dbt_public_surface.py tests/integration/test_dbt_artifact_flow.py -q
python -m pytest -m "not live_db" -q
python -m ruff check src tests
```

Expected: PASS. If Python is unavailable, status remains `[PENDING LOCAL PYTHON 3.13]` and feature completion cannot be claimed.

- [ ] **Step 3: Run governance, bundle, package, and secret checks**

```text
python -m seshat.cli check --repo .
python scripts/export_agent_bundles.py --check
python -m build
python scripts/install_smoke_test.py
git grep -n -I -E "postgres(ql)?://|password[[:space:]]*[:=][[:space:]]*[^<{]" -- . ":(exclude)specs/133-activate-dbt-mvp"
git diff --check
```

Expected: PASS/no secret hits. The grep excludes the feature spec examples, not runtime source or bundles.

- [ ] **Step 4: Run pinned dbt and optional live checks**

```text
dbt parse --project-dir dbt --profiles-dir . --target shadow --no-partial-parse
dbt compile --project-dir dbt --profiles-dir . --target shadow --select selector:seshat_table_retail_store_sales
python -m pytest tests/live_db/test_dbt_retail_store_sales.py -m live_db -v
```

Record exact versions, artifact schema URIs, selected node count, and live PASS or `[PENDING LIVE PROFILE]`.

- [ ] **Step 5: Review the diff and request code review**

Read `superpowers:requesting-code-review` fully. Review `git diff --stat`, `git status --short`, no change to migration ownership/readiness pass, no raw artifacts, and no unrelated primary-checkout changes.

- [ ] **Step 6: Commit verified fixes and hand off at the human boundary**

The final report cites commands and results. If all non-live requirements pass but live prerequisites are absent, report the static/compile result and `[PENDING LIVE PROFILE]`; do not call live parity complete. If parity passes, recommend named-human build-path review and STOP. Never self-grant it.

## Requirement Coverage

| Requirements | Tasks |
|---|---|
| FR-001..FR-010 | T002, T003, T005, T006, T009 |
| FR-011..FR-018 | T001, T003, T007, T008 |
| FR-019..FR-033 | T001, T004, T005, T006, T009, T010 |
| FR-034..FR-040 | T011, T012 |
| FR-041..FR-046 | T002..T014 |

## Execution Order and Checkpoints

1. T001-T006 are foundational and sequential because each locks interfaces consumed by the next.
2. T007-T008 implement the dbt graph after static contract validation exists.
3. T009 wires the CLI only after services have unit coverage.
4. T010 proves the exact external version/artifact boundary.
5. T011 waits for the owning feature-126 registry commit, then integrates once.
6. T012 reconciles claims only after runtime and public feeders exist.
7. T013 is optional-environment verification but required for a live-parity completion claim.
8. T014 is the final evidence gate; no completion claim precedes it.
