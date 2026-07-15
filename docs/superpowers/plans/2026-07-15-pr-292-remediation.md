# PR 292 Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the PR 292 CI, correctness review findings, and structural CodeScene findings without changing the impact-map public contract.

**Architecture:** Keep `impact_map.py` as the public composition and rendering seam. Move graph evidence parsing/matching into a graph builder module and traversal into a graph walker module. Both helpers accept the existing graph dataclasses so the output schema and CLI surface stay stable.

**Tech Stack:** Python 3.13, pytest, PyYAML, existing Seshat CLI and governance checker.

## Global Constraints

- The impact map remains read-only, offline, deterministic, and score-free.
- Matching may only use identifier or path boundaries; substrings are not dependencies.
- Traversal reports every reachable cycle while affected artifacts remain unique.
- Capability records are evidence-backed and do not self-grant readiness or approval.

---

### Task 1: Lock down the review regressions

**Files:**
- Modify: `tests/unit/test_impact_map.py`
- Modify: `tests/unit/test_capability_inventory.py`

**Interfaces:**
- Consumes: `impact_module._text_references(text: str, token: str) -> bool` and `impact_module._walk_graph(...)`.
- Produces: regression coverage for false dependency matches, sibling-path cycles, and real-manifest command coverage.

- [ ] **Step 1: Write the failing tests**

```python
def test_reference_matching_requires_boundaries() -> None:
    assert impact_module._text_references("gold.fact", "gold.fact")
    assert not impact_module._text_references("gold.fact_catalog", "gold.fact")
    assert not impact_module._text_references("net_sales", "sales")

def test_cycle_reached_by_sibling_paths_is_recorded(...) -> None:
    # A -> B, A -> C, B -> C, C -> B
    assert cycles == [{"nodes": ["B", "C", "B"], "detail": "dependency cycle detected"}]
```

- [ ] **Step 2: Verify they fail on the reviewed implementation**

Run: `pytest tests/unit/test_impact_map.py -q`

Expected: the reference matcher accepts one of the false substring pairs and the sibling-path cycle is absent.

- [ ] **Step 3: Add the manifest assertion**

```python
def test_impact_map_capability_covers_its_dispatch() -> None:
    raw = {entry["id"]: entry for entry in load_manifest(_REPO_ROOT)}
    assert raw["decision-change-impact-map"]["command"] == "impact-map"
    assert raw["decision-change-impact-map"]["references"]["dispatch"] == "impact-map"
```

- [ ] **Step 4: Run the focused tests**

Run: `pytest tests/unit/test_impact_map.py tests/unit/test_capability_inventory.py -q`

Expected: failures remain only until Tasks 2 and 4 are complete.

### Task 2: Extract boundary-aware graph construction

**Files:**
- Create: `src/seshat/impact_map_graph.py`
- Modify: `src/seshat/impact_map.py`

**Interfaces:**
- Produces: `build_graph(root: Path) -> _ImpactGraph` and `text_references(text: str, token: str) -> bool`.
- Consumes: `artifact_identity`, `explorer_build._lineage`, and `_GraphNode`, `_GraphEdge`, `_ImpactGraph` data structures re-exported from the public module.

- [ ] **Step 1: Implement exact normalized token/path matching**

```python
def text_references(text: str, reference: str) -> bool:
    expected = _normalized_parts(reference)
    return bool(expected) and expected <= _normalized_parts(text)
```

The helper must recognize exact dotted or path segments, not a contiguous substring.

- [ ] **Step 2: Move file discovery, metric/warehouse-node construction, and additional-edge creation into `impact_map_graph.py`**

Keep the graph builder limited to evidence reading and graph construction. The public module imports and delegates to the builder; it does not duplicate the moved rules.

- [ ] **Step 3: Run the impact-map unit suite**

Run: `pytest tests/unit/test_impact_map.py tests/unit/test_impact_map_no_duplicate.py -q`

Expected: PASS.

### Task 3: Extract path-aware traversal

**Files:**
- Create: `src/seshat/impact_map_walk.py`
- Modify: `src/seshat/impact_map.py`

**Interfaces:**
- Produces: `walk_graph(root: Path, graph: _ImpactGraph, direct: set[str]) -> tuple[dict[str, list[str]], list[dict[str, str]], list[dict[str, Any]]]`.
- Consumes: graph nodes and edges plus `explorer_build._evidence_state`.

- [ ] **Step 1: Implement path-scoped queueing**

```python
if edge.target in node_chain:
    record_cycle(node_chain, edge.target)
elif target_is_available:
    record_affected_path(edge.target, chain)
    queue.append((edge.target, tuple(chain), (*node_chain, edge.target)))
```

Use a separate `expanded_paths` set keyed by `(target, node_chain)` only to prevent duplicate queue states; never skip the cycle test merely because the node is globally affected.

- [ ] **Step 2: Delegate from `impact_map._walk_graph` or re-export the walker seam**

The public module retains the existing private seam required by current tests while its implementation delegates to the focused walker.

- [ ] **Step 3: Run regression and contract tests**

Run: `pytest tests/unit/test_impact_map.py tests/unit/test_impact_map_no_driver.py tests/unit/test_impact_map_no_leak.py tests/unit/test_impact_map_no_score.py -q`

Expected: PASS.

### Task 4: Register the command and repair PR metadata

**Files:**
- Modify: `docs/capabilities/capabilities.yaml`
- Modify: `tests/unit/test_capability_inventory.py`

**Interfaces:**
- Produces: the `decision-change-impact-map` capability record with `command` and `references.dispatch` both set to `impact-map`.

- [ ] **Step 1: Add the truthful manifest record**

```yaml
- id: decision-change-impact-map
  name: "decision-change-impact-map"
  state: shipped
  authority: agent-runnable
  readiness_stage: not-stage-scoped
  command: "impact-map"
  documentation: "specs/132-decision-change-impact-map/spec.md"
  references:
    dispatch: "impact-map"
```

Use the surrounding manifest record's required fields and valid vocabulary.

- [ ] **Step 2: Run the CI failure reproduction**

Run: `pytest tests/unit/test_capability_inventory.py::test_real_manifest_passes_all_eight_oracle_checks -q`

Expected: PASS.

- [ ] **Step 3: Amend the original PR commit subject**

Run: `git commit --amend -m "feat: implement decision change impact map"`

Expected: the repository hook accepts the conventional subject after the capability and code fixes are staged.

### Task 5: Final verification and PR update

**Files:**
- Verify: all modified files.

- [ ] **Step 1: Run focused suites**

Run: `pytest tests/unit/test_impact_map.py tests/unit/test_evidence_stale_promotion.py tests/unit/test_capability_inventory.py -q`

Expected: PASS.

- [ ] **Step 2: Run the repository checks**

Run: `retail check`

Expected: exit 0 with no governance errors.

- [ ] **Step 3: Push the repaired PR branch and recheck Actions**

Run: `git push --force-with-lease origin 132-decision-change-impact-map-implementation` followed by `gh pr checks 292 --watch --interval 10`.

Expected: the GitHub Actions `check` job passes. CodeScene is re-evaluated after the module split; report any external residual separately.
