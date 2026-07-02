# Feature Specification: Kit Drift Linter (Compass-Driven Phase-2 backstage)

**Feature Branch**: `072-kit-drift-linter`

**Created**: 2026-07-02

**Status**: Draft

**Input**: The Phase-2 backstage substrate deferred by feature 070's plan (MINOR-5):
a CI-runnable drift linter that fails loud when (1) a projection drifts from the
canonical kit source, or (2) the canonical source drifts from the constitution's
hard-stops. From `docs/roadmap/distribution-ideas.md` (lines 46, 57, 77-78, 239-250):
"the drift linter (B2) fails loud if any projection drifts from the source" and "must
eventually check the source *against* the constitution's hard-stops, not only the
projections against the source."

> **Provenance.** Phase-2 backstage of the Compass-Driven kit; the deferral is
> explicitly recorded in `specs/070-retail-init-bootstrap/plan.md` (Constitution
> Check, MINOR-5). Spec'd directly via speckit (not `idea-to-spec`), continuing the
> 070/071 pattern. F024 class: **Maintenance Automation** (CI-only, emits derived
> evidence, creates no truth, self-approves nothing).

## Overview

Feature 070 shipped the compass projection generator + two drift checks
(`check_yaml_drift`, `check_prose_drift`) as callables, but **nothing invokes them as
a gate** — they are library functions with no CI entry point. And the harder half of
the doc's drift-linter definition is unbuilt: the canonical source
(`.seshat/kit-source.yaml`) is declared "downstream of the constitution", yet nothing
verifies the source's `hard_stops` actually correspond to the constitution's
principles. 070's plan named this gap explicitly (MINOR-5): until the source-vs-
constitution check exists, the fenced `SESHAT-KIT` body is only human-reviewed at
ratify, not machine-verified.

This feature adds a **standalone `retail kit-lint` CI step** (NOT a `retail check`
core rule — see DEC-1) that runs three deterministic checks and fails loud (exit 1)
on any drift:

- **YAML projection drift** — `.seshat/compass.yaml` byte-equals `project_yaml(source)`
  (wraps the existing `check_yaml_drift`).
- **Prose projection drift** — the `SESHAT-KIT` fenced body of each governed file
  (`AGENTS.md`, `CLAUDE.md`) equals `render_prose(source)` (wraps the existing
  `check_prose_drift` via `read_fence_body`).
- **Source-vs-constitution correspondence** — each `hard_stop` id in the source maps
  to a declared constitutional anchor via a MAINTAINED correspondence table, and every
  constitutional hard-stop in that table is present in the source. A source hard_stop
  with no anchor, or a table anchor missing from the source, fails loud.

The correspondence check is **structural presence, NOT semantic non-contradiction**
(DEC-2): it never parses constitution prose to "judge" whether a hard_stop contradicts
it — that would be fabricated confidence (hard rule #9). It is a categorical
present/absent map, the same shape as `scaffold.py`'s `FIVE_PLACES` or the glossary
drift check.

## Clarifications

### Session 2026-07-02

- Q: Is the drift linter a new `retail check` core rule, or a standalone step? -> A:
  **DEC-1: standalone `retail kit-lint` step** (like `retail semantic-check` /
  `retail value-check`). It parses YAML (and reads constitution structure), which the
  stdlib-only `retail check` core must never do (repeats the MAJOR-4 boundary the 070
  skeptic caught). It adds NO gate rule; the `retail check` rule count stays 47.
- Q: Does the source-vs-constitution check parse/interpret constitution prose? -> A:
  **DEC-2: NO. Structural correspondence only.** A maintained table maps each source
  `hard_stop` id to a constitutional anchor (principle number or hard-rule id). The
  check verifies presence in both directions (source ↔ table). It never reads prose to
  decide "does this hard_stop contradict the constitution" — that is fuzzy judgment and
  forbidden fabricated confidence.
- Q: Where does the correspondence table live? -> A: A committed, guard-tested constant
  in the linter module (mirroring `scaffold.py`'s `FIVE_PLACES` / `REPO_WIRING_KEYS`
  pattern), so it cannot silently drift and is itself covered by a test that asserts it
  matches the source's hard_stops.
- Q: Does `kit-lint` REPAIR drift? -> A: NO. Read-only report + exit code. Repairing a
  projection is `retail init` re-running (re-projection); repairing the source or the
  correspondence is a human edit. The linter reports and fails loud; it never rewrites.
- Q: What if `.seshat/` is absent (repo not yet bootstrapped)? -> A: `kit-lint` reports
  "not bootstrapped — run `retail init`" and exits 0 (nothing to lint yet), NOT a
  failure. Absence is the honest not-started state, not drift.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CI fails loud when a projection drifts from the source (Priority: P1)

A maintainer edits `.seshat/kit-source.yaml` (adds a verb) but forgets to re-run
`retail init`, so `compass.yaml` / the fenced regions go stale. CI catches it.

**Why this priority**: This is the linter's core purpose and the whole reason the doc
calls it "the enforcement arm for the compass itself". Without it, the single-source
guarantee is aspirational — projections silently rot. It also unblocks 070's MINOR-5:
once the fenced body is machine-verified against the source, it stops relying on
human-review-at-ratify.

**Independent Test**: In a bootstrapped repo, mutate `compass.yaml` (or a fenced body),
run `retail kit-lint`, and confirm exit 1 with a report naming the drifted projection.
Re-run `retail init`, run `kit-lint`, confirm exit 0.

**Acceptance Scenarios**:

1. **Given** a bootstrapped repo whose `compass.yaml` no longer matches
   `project_yaml(source)`, **When** `retail kit-lint` runs, **Then** it exits 1 and the
   report names the YAML projection drift.
2. **Given** a bootstrapped repo whose `AGENTS.md` fenced body no longer matches
   `render_prose(source)`, **When** `retail kit-lint` runs, **Then** it exits 1 and the
   report names the prose projection drift for that file.
3. **Given** a bootstrapped repo with all projections in sync, **When** `retail
   kit-lint` runs, **Then** it exits 0.

---

### User Story 2 - CI fails loud when the source drifts from the constitution (Priority: P1)

A maintainer adds a `hard_stop` to the source that has no constitutional basis, or the
correspondence table names a constitutional hard-stop the source dropped. CI catches
the mismatch — structurally, without judging prose.

**Why this priority**: This is the half 070 explicitly deferred (MINOR-5) — the reason
the fenced body is "human-reviewed until Phase-2". It makes "the source is downstream
of the constitution" a verified invariant rather than a comment. Same P1 as US1: the
two together are the drift linter the doc defines.

**Independent Test**: Add a `hard_stop` with no table anchor → exit 1. Remove a
source hard_stop that the table anchors → exit 1. Restore → exit 0. Confirm the check
reads NO constitution prose (it consults only the maintained table + the source list).

**Acceptance Scenarios**:

1. **Given** a source `hard_stop` id absent from the correspondence table, **When**
   `retail kit-lint` runs, **Then** it exits 1 naming the un-anchored hard_stop.
2. **Given** a correspondence-table anchor whose hard_stop is missing from the source,
   **When** `retail kit-lint` runs, **Then** it exits 1 naming the dropped hard_stop.
3. **Given** source hard_stops and the table in one-to-one correspondence, **When**
   `retail kit-lint` runs, **Then** it exits 0 — and the check has consulted only the
   table + the source, never constitution prose.

---

### User Story 3 - Runs in CI and pre-commit as the enforcement arm (Priority: P2)

The linter is wired into CI (a step after `retail semantic-check`) so drift can never
merge, and is documented so a maintainer runs it locally before pushing.

**Why this priority**: A linter no pipeline invokes is dead code. Wiring it into CI is
what turns the checks into enforcement (the doc: "fails loud"). P2 because the checks
(US1/US2) must exist and pass first; the wiring is the delivery mechanism.

**Independent Test**: The CI workflow has a `retail kit-lint` step; running the repo's
own committed substrate through it exits 0 (the dogfood proof).

**Acceptance Scenarios**:

1. **Given** the CI workflow, **When** it runs, **Then** a `retail kit-lint` step runs
   after `retail semantic-check` and a non-zero exit fails the build.
2. **Given** this repo's committed `.seshat/` + fenced regions, **When** `retail
   kit-lint` runs, **Then** it exits 0 (the substrate is self-consistent).

### Edge Cases

- **`.seshat/` absent**: report "not bootstrapped — run `retail init`", exit 0 (not a
  failure; absence is not drift).
- **A governed file lacks a `SESHAT-KIT` fence**: report it as prose drift for that file
  (the fence should exist post-bootstrap) OR, if `.seshat/` is absent, fold into the
  not-bootstrapped case. A malformed fence is reported, never rewritten.
- **Source unparseable / missing a required block**: report the parse/shape error and
  exit 1 (a broken source is drift the linter must surface, not swallow).
- **Correspondence table vs source out of sync in the LINTER's own code**: a guard test
  asserts the table's source-side ids equal the committed source's hard_stops, so the
  table cannot silently rot (mirrors `scaffold.py`'s FIVE_PLACES guard).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The kit MUST expose a standalone `retail kit-lint` CLI step that runs the
  drift checks and exits non-zero on any drift, zero when clean.
- **FR-002**: `kit-lint` MUST check YAML projection drift (`compass.yaml` byte-equals
  `project_yaml(source)`), wrapping the existing `check_yaml_drift`.
- **FR-003**: `kit-lint` MUST check prose projection drift (each governed file's
  `SESHAT-KIT` fenced body equals `render_prose(source)`), wrapping the existing
  `check_prose_drift` + `read_fence_body`.
- **FR-004**: `kit-lint` MUST check source-vs-constitution correspondence STRUCTURALLY:
  every source `hard_stop` maps to a maintained anchor, and every table anchor's
  hard_stop is present in the source. It MUST NOT parse or interpret constitution prose
  (DEC-2).
- **FR-005**: The correspondence table MUST be a committed, guard-tested constant in the
  linter module; a guard test MUST assert its source-side ids equal the committed
  source's `hard_stops` (mirrors `scaffold.py` FIVE_PLACES).
- **FR-006**: `kit-lint` MUST be read-only: it reports drift + exits, and NEVER rewrites
  a projection, the source, a governed file, or the correspondence table.
- **FR-007**: `kit-lint` MUST NOT be a `retail check` core rule and MUST NOT add a gate
  rule; the `retail check` rule count stays unchanged (DEC-1). It MAY import `pyyaml`
  (like `semantic-check`); the `retail check` core stays stdlib-only.
- **FR-008**: When `.seshat/` is absent, `kit-lint` MUST report "not bootstrapped" and
  exit 0 (absence is not drift).
- **FR-009**: `kit-lint` MUST be wired into CI as a step after `retail semantic-check`,
  so drift fails the build.
- **FR-010**: `kit-lint`'s report MUST name each specific drift (which projection / which
  file / which hard_stop), not just "drift found" — actionable, traceable output.
- **FR-011**: `kit-lint` MUST NOT emit a numeric health / confidence / drift score (hard
  rule #9); it emits explicit pass/fail per check + the exit code.

### Key Entities

- **Canonical kit source** — `.seshat/kit-source.yaml` (EXISTING): the single source
  the linter validates projections and hard_stops against.
- **Projections** — `.seshat/compass.yaml` + the `SESHAT-KIT` fenced regions (EXISTING):
  checked byte-exact / render-compare against the source.
- **Correspondence table** — NEW committed constant mapping each source `hard_stop` id
  to a constitutional anchor (principle number / hard-rule id). Structural, not semantic.
- **Constitutional anchor** — a principle id (I/IV/V/…) or hard-rule id (#9) the table
  references BY IDENTIFIER; the linter never reads the anchor's prose.

## Success Criteria *(mandatory)*

- **SC-001**: A drifted `compass.yaml` or fenced body causes `retail kit-lint` exit 1
  with a report naming the drift; a re-projected repo exits 0.
- **SC-002**: An un-anchored source `hard_stop`, or a table anchor missing from the
  source, causes exit 1 naming the specific hard_stop; a matched set exits 0.
- **SC-003**: The source-vs-constitution check reads NO constitution prose (verifiable:
  the check consults only the maintained table + the source hard_stops).
- **SC-004**: A guard test fails if the correspondence table's source-side ids diverge
  from the committed source's `hard_stops`.
- **SC-005**: `retail check` rule count is unchanged (no new gate rule); `kit-lint` is a
  standalone step.
- **SC-006**: On an un-bootstrapped repo (no `.seshat/`), `kit-lint` exits 0 with a
  "not bootstrapped" note — never a false-positive failure.
- **SC-007**: This repo's own committed substrate passes `retail kit-lint` (exit 0) — the
  dogfood proof — and a CI step runs it after `semantic-check`.
- **SC-008**: `kit-lint` emits no numeric drift/confidence score — explicit pass/fail +
  exit code only.

## Assumptions

- The 070 substrate (`compass_project`, `fence`, `.seshat/kit-source.yaml` + committed
  projections) is on `main` and is the linter's input.
- The four current source `hard_stops` map to: `never_self_grant_approval` → Principle
  V; `no_silver_before_mapping_cleared` → Principle IV; `no_dashboard_before_metric_contracts`
  → roadmap rule 5 (constitution-dependent); `never_fabricate_a_confidence_score` → hard
  rule #9. These are the seed correspondence entries.
- CI (`.github/workflows/ci.yml`) is where the step is wired, mirroring how
  `retail semantic-check` is a separate step from `retail check`.
- This feature advances NO readiness stage and takes NO roadmap F-row (kit maintenance
  automation), matching `scaffold.py` / `manifest.py` / the 070 substrate.
