# Implementation Plan: Row-Level Security as a Semantic-Model-Ready Dimension

**Branch**: `092-rls-access-readiness` | **Date**: 2026-07-04 | **Spec**: `specs/092-rls-access-readiness/spec.md`

**Input**: Feature specification from `specs/092-rls-access-readiness/spec.md` (clarified 2026-07-04)

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Row-level security (RLS) currently appears in this repo only as prose caution
(`docs/medallion-playbook.md`, ADR `0002-retail-cleaning-defaults.md` RC4) and
is invisible to the Semantic Model Ready (Stage 5) gate: a model can reach
`semantic_model_ready: pass` while carrying zero RLS roles, or a role whose
filter is blank or points at a non-existent column. This feature closes that
gap the way F009 closed the missing-metric-contract gap: it adds a GENERIC,
human-authored DECLARATION artifact (`templates/rls-role-contract.yaml`, a
SEPARATE file from `templates/metric-contract.yaml` per the
collision-avoidance allocation) and exactly ONE new static `retail check`
rule, reserved id **HR6**, that verifies each declared role's filter binding
is present, non-empty, references a `gold` DIMENSION column that actually
exists in the committed gold migration SQL, is not a fact-table binding, does
not duplicate another role's name, and does not claim `pass` with empty
evidence. HR6 folds into the EXISTING Semantic Model Ready gate the same way
G6 already does (an additional `retail check` finding that blocks the stage
via the existing exit-code path) -- no new stage, no new subcommand, no
change to F010/`retail-semantic-check`'s own logic. The feature is
DECLARATION + STATIC BIND-CHECK only: it never decides WHO should see WHAT
(that stays an open Principle-V governance ruling, Q-ZERO-ROLES/FR-010), never
executes a filter, and never opens a live database or Power BI connection.

## Technical Context

**Language/Version**: Python 3.11+ (matches `src/retail/` existing rule
modules; no new language/runtime introduced).

**Primary Dependencies**: stdlib (`re`, `pathlib`, `dataclasses`) for the
rule's control flow, plus the ALREADY-APPROVED runtime dependency `pyyaml>=6`
for parsing the role-contract YAML, imported LAZILY inside the rule function
body (never at module scope), mirroring `src/retail/rules/readiness_status.py`
(RS1)'s `import yaml  # lazy: keep retail check import path stdlib-light`.
No new dependency is added to `pyproject.toml`.

**Storage**: N/A at runtime (no database connection). The rule reads two
kinds of already-committed TEXT: (1) `rls-role-contract.yaml` files under
`mappings/<table>/roles/`, and (2) `warehouse/migrations/*.sql` (the
committed gold-schema source of truth), both via `ctx.tracked_files` /
`Path.read_text()`. No new storage location is introduced.

**Testing**: `pytest`, `@pytest.mark.unit` (matches the existing
`tests/unit/test_*.py` convention for rule modules, e.g.
`tests/unit/test_readiness_status.py`, `tests/unit/test_additivity_consistency.py`).
Coverage target unchanged from repo norm (`pytest --cov=src --cov-report=term-missing`).

**Target Platform**: Same as the rest of `src/retail/` -- CI-able, stdlib+pyyaml
only, Windows-safe (ASCII / UTF-8-no-BOM per Principle IX), no network, no DB
driver import in this module's import path.

**Project Type**: Single project (existing `src/retail/` governance checker +
`templates/` + `docs/` repo layout). No new top-level project.

**Performance Goals**: N/A (a static text-scan rule over a handful of
committed YAML/SQL files per `retail check` run; no different performance
profile than the existing S6/S8/G6 rules it is modeled on).

**Constraints**: MUST NOT execute anything (no DAX eval, no live PBIP read, no
DB connection, no "view as role" simulation) -- Scope Guard, FR-012, FR-018.
MUST NOT add a key to `templates/metric-contract.yaml` or
`templates/kpi-pack.yaml` -- collision-avoidance allocation, SC-005. MUST fail
CLOSED (`Severity.ERROR`), never merely WARN -- Principle I, spec
Clarification C1. MUST NOT decide Q-ZERO-ROLES -- Principle V, FR-010, FR-013.
MUST NOT fabricate a confidence/health/maturity score or an "N of M"
completeness count anywhere -- hard rule #9, FR-014.

**Scale/Scope**: One template file, one rule module (~1 new `retail check`
rule id, HR6), a doc-listing edit to one existing readiness doc
(`semantic-model-ready.md`), and the corresponding unit tests + rules-manifest
regeneration. No change to any other rule, stage, or skill's own source.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design below.*

| Principle | How this design satisfies it |
|---|---|
| **I. Agent-First, Gate-Enforced** | HR6 is a registered `retail check` rule (`@register("HR6", ...)`) returning `Finding(severity=Severity.ERROR, ...)` for every violation -- a non-zero process exit, not advisory prose. Compliance is demonstrable by running `retail check` (spec Independent Tests for US1/US2/US3 are literally "run `retail check`, inspect the findings"). The agent never marks HR6 passing itself; the checker's exit code is the sole authority (mirrors G6/S6/RS1). |
| **III. Medallion, Gold-Only** | FR-003/FR-006/FR-007: a role contract's `filter.gold_table` MUST be a `gold.*` object; HR6 fails closed if it names `silver.*`/`bronze.*` or a `gold` table absent from committed migrations. FR-005/C1: HR6 additionally hard-fails a binding to a `gold.fct_*` table -- RLS in this repo's Kimball star filters a CONFORMED DIMENSION, and the filter propagates to the fact via the relationship (research P5/P6); a fact-table binding is the exact leak-through direction this feature exists to close. |
| **IV. Source-Mapping-Before-Silver** | Not directly engaged by this feature (HR6 operates at Stage 5, after Gold Ready). No `silver.*` SQL is authored, edited, or implied by this plan. |
| **V. Agent-Stops-at-Judgment** | The feature explicitly does NOT decide who-sees-what: HR6 checks that a DECLARED role's binding is well-formed, never which roles a model NEEDS or which column is the "correct" security boundary (FR-013). Q-ZERO-ROLES (FR-010, spec's Principle-V carve-out) is carried forward UNRESOLVED into this plan -- see "Zero-contract handling" below. The rule and template's own source MUST NOT encode a final "pass" or "block" answer to it. |
| **VI. Defaults-Then-Deviations** | The role-contract shape defaults to mirroring `metric-contract.yaml`'s declare/bind/readiness structure (research P1) rather than inventing a new one; the fact-vs-dim hard-fail default (Clarification C1) and the dim/fact-prefix classification default (Clarification C3) are both recorded, reversible, constitution-safe defaults already ratified in the spec's Clarifications -- this plan does not re-litigate them. |
| **VII. C086-is-an-example** | `templates/rls-role-contract.yaml` carries only placeholders (`<RoleName>`, `<gold_dim_table>`, `<column>`) -- see `data-model.md`. No `retail_store_sales`-specific role, column, or table name (e.g. `dim_location_rss`) is inlined into the template or the HR6 rule's own source/messages (FR-015, SC-007). A filled instance may later be cited under `docs/worked-examples/`, never baked into the generic artifact. |
| **VIII. Static-First/Live-Deferred** | HR6 reads only already-committed text (the contract YAML + `warehouse/migrations/*.sql`) -- no live PBIP, no live database, no `information_schema` query (FR-006, FR-012). A live check that a role's filter ACTUALLY restricts rows is explicitly deferred (FR-018) and is not stubbed or TODO'd into this feature's module -- it simply is not written, matching how `retail validate`'s live surface is a wholly separate, later-built module. |
| **IX. Secrets/Reproducibility** | No host/DSN/secret is introduced by this feature. The template and rule source are ASCII, UTF-8 without BOM (`--`/`->`, no glyphs), and the new `mappings/<table>/roles/<RoleName>.yaml` path stays well under the Windows 260-char budget (FR-016). |
| **Hard rule #9 (no fabricated score)** | The role contract's `readiness` block uses exactly the four explicit statuses + `evidence[]` + `blocking_reasons[]` -- no numeric field anywhere in the template or in an HR6 `Finding.message` (FR-014, SC-004). |
| **F016 boundary** | This design assumes F016 (Power BI execution adapter) does NOT exist. HR6 never opens a PBIP file, never previews "view as role", never connects to the Power BI service. That remains F016's later, execution-only concern (Principle II), gated on Semantic Model Ready being `pass` -- unaffected by this feature. |

**Zero-contract handling (Q-ZERO-ROLES, FR-010) -- explicitly NOT decided here.**
This plan fixes only what HR6 does when a role contract EXISTS and is
malformed (fails closed, `Severity.ERROR`). It does NOT fix what happens when
a table has ZERO `rls-role-contract.yaml` files, and this slice's shipped HR6
behavior (data-model.md, Entity 3) does not synthesize any finding for that
absence -- HR6 evaluates declared contracts only. The spec's PENDING DEFAULT
(not ratified) is that absence of any role contract should eventually be
surfaced as an explicit, visible fact rather than silently treated as `pass`;
IF a later slice implements that surfacing at all, it would have to take the
form of an `Severity.INFO`-tier finding-or-note that CANNOT block the build
and CANNOT itself grant a `pass` either, so that neither answer is silently
shipped. Whether to ever add that INFO-tier surfacing, versus leaving the
zero-contract case permanently unaddressed by HR6 until an owner rules, is
left to a future slice/`tasks.md` to decide against this non-negotiable
constraint: **no version of this feature may ship
code that treats zero contracts as either a hard block or a clean pass.**

**Result**: PASS. No principle is violated; no Complexity Tracking entry is
required (see below).

## Project Structure

### Documentation (this feature)

```text
specs/092-rls-access-readiness/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` subfolder is needed: this feature's only "contract" artifact
IS the top-level `templates/rls-role-contract.yaml` deliverable itself
(documented in `data-model.md`), not an API/service contract.

### Source Code (repository root)

This is a **single-project** structure (the existing `src/retail/` governance
checker + `templates/` + `docs/` + `mappings/` repo layout) -- no
frontend/backend split, no mobile target. Concrete real paths this feature
ADDS or EDITS (all repo-relative to the worktree root):

```text
templates/
└── rls-role-contract.yaml          # NEW. Generic copy-me template (FR-001/002).
                                     # Sibling of templates/metric-contract.yaml;
                                     # shares its declare/bind/readiness SHAPE,
                                     # adds no key to that file (collision guard).

src/retail/rules/
└── hr6.py                          # NEW. The HR6 static rule module.
                                     # Sibling of g6.py: @register("HR6", ...),
                                     # pure function RuleContext -> Iterable[Finding],
                                     # Severity.ERROR on every violation (fail-closed,
                                     # Principle I / Clarification C1). Lazy
                                     # `import yaml` inside the function body only
                                     # (mirrors readiness_status.py / RS1); reuses
                                     # the sql.py-style noise-stripped regex family
                                     # (research P5) to read gold table/column
                                     # existence from warehouse/migrations/*.sql.

docs/readiness/
└── semantic-model-ready.md          # EDIT. Add HR6 to the existing "Required
                                     # checks" and "Blocking reasons" tables
                                     # (FR-017, SC-006) -- doc-listing only, no
                                     # narrative rewrite of the stage's meaning.

docs/rules/
└── rules-manifest.json              # REGENERATE (via `retail manifest`) after
                                     # HR6 registers -- the registry snapshot
                                     # test (Principle VIII: "the authoritative,
                                     # always-current rule inventory") fails
                                     # closed on a stale manifest, so this
                                     # regeneration is a required implementation
                                     # step, not optional cleanup.

tests/unit/
└── test_hr6.py                      # NEW. Unit tests for HR6: missing/blank
                                     # filter column, non-existent gold column,
                                     # silver/bronze binding, fact-table binding
                                     # (hard fail per C1), duplicate role name,
                                     # pass-with-empty-evidence, and the clean/
                                     # well-formed pass-through case (mirrors the
                                     # style of tests/unit/test_readiness_status.py
                                     # and tests/unit/test_additivity_consistency.py).

mappings/<table>/roles/              # NEW co-location pattern (per-table, not a
└── <RoleName>.yaml                  # single global path). Mirrors
                                     # mappings/<table>/metrics/<MetricName>.yaml
                                     # (ADR 0003 cohesive-per-table-working-set).
                                     # No filled instance is authored BY THIS
                                     # PLAN stage -- a security owner fills one
                                     # later, per-table, when ready (Principle V:
                                     # the agent does not decide role contents).
```

**Structure Decision**: Single project, additive-only. This feature adds
exactly one template file, one rule module, one test module, one doc-listing
edit, and one regenerated manifest -- no restructuring of `src/retail/`, no
new top-level directory, no change to any existing rule's registration or
behavior. The `mappings/<table>/roles/` co-location path is a NEW subfolder
convention (parallel to the existing `metrics/` subfolder) but not a new
top-level location; it follows the same ADR 0003 precedent already governing
`metrics/`.

## Complexity Tracking

*No entry required.* The Constitution Check above found no principle
violation needing justification: the design adds one template + one rule
module, following two already-shipped precedents (F009's contract shape,
G6's rule shape) rather than introducing a new pattern, a new dependency, a
new stage, or a new subcommand.
