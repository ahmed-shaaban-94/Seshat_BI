---
description: "Task list for Capability Inventory implementation"
---

# Tasks: Capability Inventory

**Input**: Design documents from `specs/118-capability-inventory/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: INCLUDED. The fail-closed truthfulness ORACLE is the feature's mechanical
guarantee -- it sits ON the real risk (a FALSE `shipped` / `publicly-released`), reading
ground truth from the FEEDERS independently of the builder (research D4; repo lesson
`verifier-must-sit-on-the-risk`). Repo mandates TDD, so tests precede code.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no incomplete-task dependency)
- **[Story]**: US1..US5 (maps to spec.md user stories)
- Paths repo-relative; single-project layout (`src/retail`, `tests/unit`,
  `docs/capabilities`, `.claude/skills/capabilities`).

**Surface note (compliance-critical)**: NO CLI verb is added (Option-B ratified decision).
The builder is a `python -m retail.capability_inventory [--format json]` MODULE entry point
(invisible to `seshat --help`); the skill instructs the agent to RUN it. Tasks MUST NOT
touch `src/retail/cli/parser.py` or `_DISPATCH`.

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 [P] Author the initial capability manifest `docs/capabilities/capabilities.yaml` per contracts/manifest-schema.md: one entry per real capability across the covered kinds, using Appendix A of spec.md as the conformance target (the four authorities `check`/`status`/`next`/`doctor`; `validate`/`semantic-check`/`value-check`/`generate`/`init-project`/`scaffold`/`evidence-pack`; pbir-* adapters; the advisory skills incl. dbt/Dagster = F029/F030 shipped; F016 deferred; F034 human-gated; spec-only/deferred roadmap items). Closed enums, four orthogonal axes, `references` pointing at each feeder. YAML, UTF-8 no BOM, ASCII.
- [x] T002 [P] Add oracle fixtures under `tests/unit/fixtures/capability_inventory/`: `good/` (a well-formed manifest that reconciles cleanly against synthetic feeders), `orphan/` (entry referencing a non-existent rule id + a skill with no frontmatter'd SKILL.md), `unlisted/` (a wired command/skill/verb no entry references), `false_shipped/` (`state: shipped` whose only "evidence" is a spec dir existing -- no positive feeder), `false_released/` (`provenance: publicly-released` with no release evidence), `contradiction/` (echoes a rule title that disagrees with the feeder), `axis_violation/` (`state` holding an authority token; a numeric maturity field), and `empty/` (minimal manifest -- drop-in edge case). Each with the synthetic feeder stubs it reconciles against. ASCII, UTF-8 no BOM.
- [x] T003 Create the builder skeleton `src/retail/capability_inventory.py`: `build_inventory(repo_root) -> list[dict]` (join manifest ⋈ feeders), `render_human(records) -> str`, `render_json(records) -> str`, and a `__main__` (`python -m`, thin `--format text|json` arg) writing ONLY to stdout (raise NotImplementedError in the render/build bodies). NO DB/driver import at module load; NO file-write call anywhere (grep-verifiable). NOT a `_DISPATCH` entry.

**Checkpoint**: manifest + fixtures exist; module imports; `python -m retail.capability_inventory` is runnable (even if NotImplementedError).

---

## Phase 2: Foundational (Blocking Prerequisites)

CRITICAL: the feeder-readers + the fail-closed oracle gate every story.

- [x] T004 [P] Implement the feeder-reader helpers in `src/retail/capability_inventory.py` (or a sibling `capability_feeders.py`): read rule ids/titles from `docs/rules/rules-manifest.json`; skill name+description from `.claude/skills/*/SKILL.md` FRONTMATTER (a frontmatter'd SKILL.md is admissible evidence per FR-002; a bare dir is NOT); verbs from `.seshat/kit-source.yaml`; F-numbered ship status from `docs/roadmap/roadmap.md`; doc-anchored built/planned from `docs/quality/status-claims.yaml`; wired commands from `src/retail/cli/__init__.py` `_DISPATCH` keys (READ, never modify); and the VALID readiness-stage token set (the snake_case `stages.*` keys of `templates/readiness-status.yaml` -- the single canonical source, research D5) for `readiness_stage` validation. Driver-free.
- [x] T005 Write the fail-closed ORACLE `tests/unit/test_capability_inventory.py` implementing O1-O8 (contracts/staleness-oracle.md): O1 orphan, O2 unlisted-as-REFERENCE-COVERAGE (one entry's `references` cover a capability's command+skill+verb; NOT one-entry-per-representation), O3 false-shipped fail-closed, O4 false-released fail-closed, O5 feeder contradiction, O6 axis/score violation, O7 determinism+closed-schema, O8 invalid `readiness_stage` (not `not-stage-scoped` and not a `templates/readiness-status.yaml` `stages.*` key). CRITICAL anti-circularity: the oracle reads ground truth from the FEEDERS DIRECTLY, never by calling the builder to learn it (else a builder bug hides the drift on both sides -- spec 114/115 join-defect class). Drive each failing mode with its Phase-1 fixture. TEST-only: NO `@register` rule, NO `_DISPATCH` change, NO manifest gate (FR-012/FR-013).

**Checkpoint**: feeder-readers return correct facts on the real committed feeders; oracle is importable and FAILS on each stale fixture, PASSES on `good`.

---

## Phase 3: User Story 1 - New user sees what works without a database (Priority: P1) -- MVP

**Goal**: grouped human read; "Available now" vs "Requires database or optional dependency" cleanly separated by the manifest's `requirements`, deterministic, no score.

**Independent Test**: run `python -m retail.capability_inventory` with no DB configured -> "Available now" lists only empty-`requirements` capabilities; DB/extra ones under their own group; no capability in both; no numeric score.

### Tests for User Story 1 (write first, must FAIL)

- [x] T006 [P] [US1] In `tests/unit/test_capability_inventory.py`, add `test_grouping_by_precedence`, `test_no_numeric_score`, and `test_output_ascii`: build over the `good` fixture; assert the FIXED PRECEDENCE (Deferred > Human-gated > Requires-DB/extra > Agent-companion > Available-now) places each capability in EXACTLY ONE group -- "Available now" holds only shipped+agent-runnable+empty-`requirements`; "Requires DB/extra" holds shipped+agent-runnable WITH a requirement; a deferred/human-gated item that also needs a DB lands in its higher-ranked group (NOT a naive requirements-binary, per spec US1); none in two groups; no numeric maturity/confidence/completeness/health token appears; and `render_human` output `.isascii()` (FR-019). Assert FAIL before T007.

### Implementation for User Story 1

- [x] T007 [US1] Implement `build_inventory` (join manifest ⋈ feeders; resolve referenced feeder facts at build time) and the fixed-precedence group assignment (Deferred > Human-gated > Requires-DB/extra > Agent-companion > Available-now) in `src/retail/capability_inventory.py`.
- [x] T008 [US1] Implement `render_human` per contracts/inventory-output.md Form 1: fixed group order, items sorted by `id`, per-record axes shown, empty groups stated as "(none)", GAP marker `[unrecorded]` for unset fields (never rounded up). ASCII `--`/`->`, no glyphs, no numeric token.

**Checkpoint**: MVP -- `python -m retail.capability_inventory` renders the grouped human inventory over the REAL manifest; US1 tests green.

---

## Phase 4: User Story 2 - Agent requests machine form and routes correctly (Priority: P1)

**Goal**: stable, byte-identical machine (JSON) form; closed schema; each record's entry point resolves to a real committed command/doc.

**Independent Test**: run `--format json` twice over unchanged inputs -> byte-identical; each shipped record's `command`/`documentation` resolves to a real target; `group` present.

### Tests for User Story 2 (write first, must FAIL)

- [x] T009 [P] [US2] Add `test_json_determinism` (two `render_json` calls over unchanged inputs are byte-identical), `test_json_closed_schema` (every record has exactly the declared field set -- no undeclared, none missing), `test_entrypoint_resolves` (each shipped record's non-null `command` is a real `_DISPATCH` key; `documentation` path exists), and `test_json_output_ascii` (`render_json` output `.isascii()`, FR-019). Assert FAIL before T010.

### Implementation for User Story 2

- [x] T010 [US2] Implement `render_json` per contracts/inventory-output.md Form 2: stdlib `json`, sorted keys, records sorted by `id`, `indent=2`, deterministic trailing-newline; include the derived `group`. Wire the `__main__` `--format json` path.

**Checkpoint**: `python -m retail.capability_inventory --format json` is byte-stable and schema-closed; US1 + US2 green.

---

## Phase 5: User Story 3 - Not misled about human-gated / deferred / provenance (Priority: P1)

**Goal**: human-gated shown as a human decision (never automated); deferred/spec-only never grouped with shipped; provenance shown verbatim, never upgraded.

**Independent Test**: run over fixtures with a human-gated, a deferred, and a locally-verified-provenance capability -> each renders under its own group with truthful wording; none in "Available now"; provenance never upgraded to publicly-released.

### Tests for User Story 3 (write first, must FAIL)

- [x] T011 [P] [US3] Add `test_human_gated_not_automated` (an `authority: human-gated` capability lands in Human-gated with human-decision wording, no automated entry point), `test_deferred_never_shipped_group` (a `state: spec-only`/`deferred` capability is in Deferred, never with shipped items, doc-pointer = its spec), and `test_provenance_verbatim_never_upgraded` (a `locally-verified`/`unrecorded` provenance is shown as-is; the renderer never prints publicly-released for it). Assert FAIL before T012.

### Implementation for User Story 3

- [x] T012 [US3] In `render_human`/`render_json`, ensure human-gated wording (human action, not automated), deferred grouping with the spec/doc pointer, and verbatim provenance with the GAP marker for `unrecorded` -- never rounding an unset field up (FR-020). No new code path invents a state; classification is read from the manifest.

**Checkpoint**: truthful presentation of human-gated / deferred / provenance; US1-US3 green.

---

## Phase 6: User Story 4 - Maintainer catches contradictory/stale metadata (Priority: P2)

**Goal**: the oracle FAILS in BOTH directions (orphan entry; unlisted real capability) AND on false-shipped/false-released/contradiction -- so a rename/removal cannot silently make the inventory stale.

**Independent Test**: introduce each stale condition via its fixture -> the corresponding oracle test fails and names the discrepancy; the real shipped manifest passes.

### Tests for User Story 4 (the oracle from T005 is the deliverable; finalize both directions)

- [x] T013 [P] [US4] Finalize the O1-O8 oracle assertions against ALL Phase-1 stale fixtures: confirm orphan (O1), unlisted-by-reference-coverage (O2), false-shipped fail-closed (O3), false-released fail-closed (O4), contradiction (O5), axis/score (O6), determinism/schema (O7), invalid-stage (O8) each FAIL with a message naming the offending `id`/reference; confirm the REAL committed manifest PASSES all eight. Re-assert anti-circularity (ground truth from feeders, not the builder).

### Implementation for User Story 4

- [x] T014 [US4] Author `docs/capabilities/README.md` explaining the fail-closed truthfulness contract (a file existing is not a capability; `shipped`/`publicly-released` need positive feeder evidence; the oracle guards drift) so maintainers understand why an entry may fail CI.

**Checkpoint**: stale metadata cannot pass; both-direction + fail-closed proven; US1-US4 green.

---

## Phase 7: User Story 5 - Existing surfaces undisturbed and distinguished (Priority: P2)

**Goal**: `retail check`/`status`/`next`/`doctor` behavior unchanged; docs explain how capabilities differs from each; NO CLI verb added.

**Independent Test**: `seshat --help` shows no `capabilities` verb; the four authorities behave byte-identically; docs state the distinction.

### Tests for User Story 5 (write first, must FAIL)

- [x] T015 [P] [US5] Add `test_no_new_cli_verb` (assert `_DISPATCH` / `_build_parser` contain NO `capabilities` entry and `seshat/retail --help` is unchanged); `test_no_write_no_db` (grep/AST-assert the module has no `open(...,"w")`/`write_*` and no driver import at module scope); and `test_reads_no_readiness_state` (FR-011: AST/grep-assert the module references NO `readiness-status.yaml` / `readiness_status` -- it must not read per-table readiness state, only capability metadata). Assert FAIL only if a violation is introduced.

### Implementation for User Story 5

- [x] T016 [P] [US5] Create the Option-B surface `.claude/skills/capabilities/SKILL.md` (frontmatter `name: capabilities` + `description`) instructing the agent to RUN `python -m retail.capability_inventory [--format json]` -- NOT to add or call a CLI verb. ASCII, UTF-8 no BOM.
- [x] T017 [P] [US5] Complete `docs/capabilities/README.md` (FR-017): the table distinguishing capabilities (what the kit can do) vs `status` (per-table readiness) vs `next` (next action) vs `doctor` (repo drift) vs `check` (governance gate). Point the README predecessors (`docs/quality/post-idea-bank-capability-state.md`, README "What is built today") at the manifest as the structured authority (follow-up reconciliation note, no rewrite of frozen snapshots). Add `test_readme_names_four_authorities` (SC-008/FR-017: assert `docs/capabilities/README.md` names `status`, `next`, `doctor`, AND `check` in the distinction section) so the doc's testable core is verified, not just authored.

**Checkpoint**: no verb added; existing surfaces byte-identical; distinction documented; all stories green.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T018 [P] Run `ruff format --check src tests` + `ruff check src tests`; fix any lint. Confirm CodeScene new-code health on `capability_inventory.py` (extract helpers / flatten guards if a function is flagged; bundle >4 args into a dataclass). Add `test_generic_no_hardcoded_table` (FR-018/Principle VII: assert the module and `docs/capabilities/capabilities.yaml` contain no client-specific onboarded-table token, e.g. `c086`/`C086`/`retail_store_sales`, so genericity is verified, not just asserted).
- [x] T019 [P] Confirm `retail check` exit code is UNCHANGED (this feature adds NO rule/gate) and the full `pytest -m unit` suite is green; verify `python -m retail.capability_inventory --format json` is byte-identical on a second run over the real manifest.
- [x] T020 Update the spec's checklist / ratify-ledger note: confirm every ratified FR (FR-001..FR-020) is grep-traceable to a task + a test; flag any hole per the `bulk-checkbox-marking-lies` discipline (mark per-verified-deliverable, never sweep).

---

## Dependencies (story completion order)

- **Setup (T001-T003)** -> everything.
- **Foundational (T004-T005)** -> all user stories (feeder-readers + oracle gate each).
- **US1 (P1, T006-T008)** = MVP; independent once Foundational done.
- **US2 (P1, T009-T010)** depends on `build_inventory` (T007); otherwise independent.
- **US3 (P1, T011-T012)** depends on the renderers (T008/T010).
- **US4 (P2, T013-T014)** finalizes the T005 oracle; independent of the renderers.
- **US5 (P2, T015-T017)** independent (surface + docs); can run alongside US3/US4.
- **Polish (T018-T020)** last.

## Parallel opportunities

- Setup: T001 (manifest) ∥ T002 (fixtures) ∥ (T003 after).
- Foundational: T004 (readers) ∥ start of T005 (oracle scaffolding).
- Per story, the `[P]` test task is authored alongside the prior story's implementation.
- US5's T016 (SKILL.md) ∥ T017 (README) ∥ US4's T014.

## Implementation strategy

MVP = **US1** (grouped human read over the real manifest). Ship the manifest + builder +
human render + the fail-closed oracle first; that alone delivers a truthful, grouped
"what can this kit do" read. Layer the machine form (US2), truthful human-gated/deferred/
provenance presentation (US3), full both-direction oracle (US4), and the surface + docs
(US5) incrementally. Every increment keeps `retail check` unchanged and adds no CLI verb.
