# Implementation Plan: Cross-Star Conformed-Dimension Readiness Gate

**Branch**: `087-conformed-dimension-readiness` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/087-conformed-dimension-readiness/spec.md`
(clarified 2026-07-04: C1-C5 default-adopted, C3 deferred to this plan,
Q-APPROVAL-SEAM OPEN for the owner).

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

**Status**: Draft. Stops at the design set below -- NOT approved, NOT
implemented, NOT ratified. `docs/quality/conformed-dimension-map.yaml` does not
exist yet and no `src/retail/rules/rule_hr1.py` is written by this stage.

## Summary

Gold today is validated PER TABLE (Gold Ready, Stage 4): one star's own PK/grain
uniqueness, contiguous date dim, zero orphan FKs, penny-exact reconciliation.
Nothing checks whether two INDEPENDENT stars agree on a dimension they both
claim to share -- the "conformed" half of Principle III's "fact + conformed
dimensions" has no gate. This feature closes that gap with a MODEL-LEVEL tier
that is orthogonal to (sits above, not inside) the seven-stage per-table spine.

The design mirrors the shipped SF1 fork-detector shape (spec 086) exactly at
the mechanism layer: a NEW human-authored manifest,
`docs/quality/conformed-dimension-map.yaml`, in which a named human declares
per shared dimension name whether it is `conformed` (must match) or `distinct`
(intentionally may differ) across a listed set of tables; and a NEW static
`retail check` rule, reserved id **HR1**, that only READS that manifest plus
every table's already-approved `mappings/<table>/source-map.yaml` and fails
CLOSED on a proven divergence or an undeclared cross-star name collision. HR1
never writes the manifest, never merges or edits a dimension, never touches a
live database, and never self-grants any model-level pass -- it only emits
categorical Findings (ERROR/WARNING), never a numeric score.

One mechanical decision is deferred rather than defaulted (clarify C3): the
grain limb of FR-005 (compare each star's dimension on its natural-key
attribute) has NO machine-readable signal in the current
`gold_star.dimensions[].attributes[]` schema -- it is a bare list of strings,
and neither "first position" nor an `_id`-suffix heuristic survives contact
with the two committed instances (see research.md). This plan ships the KEY
limb (`surrogate_key` equality) and the TYPE limb (silver-type agreement on the
Kimball conformed-subset of shared attributes, clarify C4) now, and marks the
GRAIN limb `[PENDING SCHEMA PREREQUISITE]`: it needs an explicit natural-key
marker OWNED by the source-mapping-gate schema (`source-map.yaml`), which is
OUTSIDE this feature's collision-avoidance allocation (HR1 +
`conformed-dimension-map.yaml` only) and is therefore a cross-feature
prerequisite, not landed here. This is a schema/mechanics gap, not a
Principle-V ruling -- HR1 re-decides no table's own grain.

One governance-shape question stays genuinely OPEN for the owner (FR-016,
Q-APPROVAL-SEAM): whether the model-level conformed tier needs its own
named-human approval seam, or is purely mechanical (a clean HR1 run is the
sign-off, like Silver/Gold Ready). This plan does not settle it; it records the
PENDING DEFAULT (mechanical, no new `approvals[]` shape) and proceeds on that
basis until an owner rules otherwise.

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `src/retail/` static
core; no new interpreter requirement).

**Primary Dependencies**: stdlib only at import time (`pathlib`, `dataclasses`,
`typing`) plus a LAZY `import yaml` inside the rule function body, mirroring
SF1 (`rule_sf1.py`) -- `yaml` (PyYAML, already a dev/optional dependency for
manifest parsing elsewhere in the repo) is kept OUT of the `retail check`
static-core import chain so the checker's stdlib-only floor (Principle VIII) is
unaffected.

**Storage**: N/A -- no database, no live connection. HR1 reads two classes of
committed text file: every `mappings/<table>/source-map.yaml` (existing,
per-table, owned by the source-mapping gate) and the new
`docs/quality/conformed-dimension-map.yaml` (this feature's one new artifact).

**Testing**: `pytest` with the existing `tests/unit/` fixture + mutation-verify
discipline (`tests/fixtures/<rule>/` good/bad corpora; each ERROR/WARNING
Finding is RED before the assert and GREEN after, per the SF1/AP1 precedent).
`pytest.mark.unit` per repo convention (no live DB, no network -- this is a
pure static rule).

**Target Platform**: the existing `retail check` CLI surface (cross-platform
Python; developed/verified on Windows per repo CLAUDE.md, no OS-specific
behavior).

**Project Type**: single project -- an addition to the existing `src/retail/`
static-governance library plus its docs/tests, not a new service or app.

**Performance Goals**: N/A (a `retail check` rule reads at most a few dozen
small committed YAML files per run; no measurable-scale requirement per the
repo's existing rule set).

**Constraints**: fail CLOSED (non-zero exit) on a proven divergence, an
undeclared collision, or a missing/malformed manifest with 2+ stars (Principle
I); NEVER a numeric confidence/health/conformance score or an "N of M" /
"% conformed" tally (hard rule #9); NEVER writes any `source-map.yaml` or the
new manifest (Principle V); NEVER opens a database connection or reads a live
Power BI/PBIP surface (Principle VIII); ASCII, UTF-8 without BOM, short
repo-relative paths (Principle IX, Windows `MAX_PATH`).

**Scale/Scope**: exactly ONE new `@register`ed rule (HR1), one new manifest
file shape, and the six-surface wiring lockstep the meta-gate already enforces
(`__init__.py`, `EXPECTED_RULE_IDS`, the glossary rules-table row + "Currently
N rules" anchor, `docs/rules/rules-manifest.json`,
`docs/rules/severity-posture.json`, `docs/quality/rule-count-claims.yaml`).
Current live registered-rule count is **55** (per
`docs/quality/rule-count-claims.yaml` / `docs/rules/rules-manifest.json`); HR1
lands as rule **56**. This count is a serialization point across the 19
parallel in-flight features -- re-verify against the live manifest at
implement time rather than trusting this number if other rule-adding features
land first.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | How this design satisfies it |
|---|---|---|
| **I. Agent-First, Gate-Enforced** | A rule fails CLOSED (blocks), never merely advises; compliance is demonstrable by running `retail check`. | HR1 is one `@register`ed rule in the same registry every other checker rule uses; a divergence, an undeclared collision, or a missing manifest (2+ stars) emits `Severity.ERROR`, which is a non-zero `retail check` exit. There is no advisory/warn-only mode for these three cases (FR-005, FR-006, FR-010). |
| **III. Medallion/Gold-Only** | `gold` IS a Kimball star (fact + CONFORMED dimensions); Power BI reads `gold` only; Postgres-first. | HR1 gives the "conformed" clause of this principle its first enforced gate. It reads only the already-committed `gold_star` block of each table's `source-map.yaml` (the gold shape as reviewed at Mapping Ready) -- it opens no Postgres connection and touches no Power BI surface, consistent with the principle's gold-only / Postgres-first boundary being about the DATA path, not this static text-only check. |
| **IV. Source-Mapping-Before-Silver** | No `silver.*` SQL before the source-map is reviewed+approved. | HR1 does not write or gate any `silver.*` SQL; it reads `source-map.yaml` strictly as a CONSUMER, after that table's own Mapping Ready review already happened. It never re-opens or re-decides a table's Mapping Ready judgment (its own grain/PK/placement stand). |
| **V. Agent-Stops-at-Judgment** | The agent MUST NOT decide grain/PII/business-policy/approval alone; it raises an unresolved-questions entry and STOPS. NEVER self-grant a readiness pass. | Deciding that two stars' same-named dimensions ARE (or are not) one conformed business dimension is a Principle-V modelling judgment; `conformed-dimension-map.yaml` is HUMAN-AUTHORED and HR1 only reads it (FR-002, FR-011). An undeclared collision is never inferred as conformed-by-default -- it is a fail-closed ERROR demanding the human ruling (FR-006). HR1 records no `approvals[]` entry and self-grants no model-level pass (SCOPE GUARD; FR-011). FR-016's approval-seam SHAPE question is left OPEN for the owner, not settled here. |
| **VI. Defaults-Then-Deviations** | Start from existing rulings; record only deviations. | HR1 introduces no new cleaning/modeling default; it enforces conformance of shapes ALREADY decided under the existing RC1-RC16 defaults at each table's own Mapping Ready gate. The clarify session's C1/C2/C4 defaults (in-scope dim set, manifest shape, shared-attribute set) are reasonable constitution-safe defaults per Principle VI, recorded in spec.md Clarifications; C3 (grain signal) is NOT defaulted because no safe default exists (deferred, not decided). |
| **VII. C086-is-an-example** | Generic templates carry no domain specifics. | `dim_product` / `dim_store` / `dim_date` are illustrative only, never required names in the rule logic or the manifest annotation comments (FR-013). No worked-example (C086/pharmacy) dim name, grain key, or column name is inlined in the rule module, its docstring, or the manifest's authoring comments. |
| **VIII. Static-First/Live-Deferred** | A live DB surface is deferred; author static structure + mark live PENDING. | HR1 is 100% static: it reads only committed `ctx.tracked_files` content (mirroring SF1's read pattern), opens no database, and invokes no execution adapter. `yaml` is imported LAZILY so it stays out of the stdlib-only static-core import chain (Principle VIII's existing discipline). Live cross-star DATA reconciliation (whether the MATERIALIZED dimensions actually agree, not just their declared shapes) is explicitly OUT of scope and deferred to a future `retail validate` surface -- HR1 proves the DECLARED shapes agree, nothing more. The grain limb is likewise authored PENDING (marked, not silently skipped) rather than assumed. |
| **IX. Secrets/Reproducibility** | Never commit a real host/DSN/secret; ASCII, reproducible, Windows-safe. | HR1 touches no connection string or credential -- it reads only repo-relative YAML paths. All new artifacts (rule module, manifest, docs) are ASCII, UTF-8 without BOM, and keep short repo-relative paths (`docs/quality/conformed-dimension-map.yaml`, `src/retail/rules/rule_hr1.py`) well under the Windows `MAX_PATH` budget. |
| **Hard rule #9** | NO fabricated confidence/health/maturity score or completeness count. | HR1's `Finding` objects carry `rule_id` / `Severity` / `message` / `locator` only (the existing `Finding` dataclass, unchanged). No percentage, ratio, "N of M", or conformance score is computed or emitted anywhere in the design (FR-012, SC-005). |

**Result**: PASS. No principle requires a documented violation; Complexity
Tracking below is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/087-conformed-dimension-readiness/
├── spec.md              # Feature specification (input to this stage; already clarified)
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (pre-existing this stage; precedent survey + C3 deferral -- verified consistent, not rewritten)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` directory: HR1 is a static file-reading rule with no network
API/CLI contract beyond the existing `Rule = Callable[[RuleContext],
Iterable[Finding]]` shape already defined in `src/retail/core.py` -- there is
no new contract surface to specify separately (consistent with the SF1/AP1
precedent, neither of which added a `contracts/` directory either).

### Source Code (repository root)

This is the existing single-project `src/retail/` static-governance library.
No new project, service, or top-level directory is introduced. Concrete real
paths this feature adds or edits (implementation-stage; recorded here so the
plan does not miss any wiring surface per FR-014):

```text
src/retail/
├── core.py                          # UNCHANGED -- Finding/RuleContext/Severity/is_test_path reused as-is
├── registry.py                      # UNCHANGED -- @register/all_rules() reused as-is
└── rules/
    ├── __init__.py                  # EDIT: add "rule_hr1" to the import list AND __all__ (the only discovery step -- no autodiscovery)
    ├── rule_sf1.py                  # UNCHANGED -- read-only design precedent, not edited by this feature
    └── rule_hr1.py                  # NEW -- the HR1 rule module (this feature's one new rule)

docs/
├── quality/
│   ├── shared-spine.yaml            # UNCHANGED -- SF1's manifest; HR1 does not read it
│   ├── rule-count-claims.yaml       # EDIT: bump claimed-count (55 -> 56) in lockstep with the registration
│   └── conformed-dimension-map.yaml # NEW -- the human-authored declaration file (this feature's one new artifact; collision-avoidance allocation)
├── rules/
│   ├── rules-manifest.json          # EDIT: add {"id": "HR1", "title": "..."} entry (regenerated golden, C3 in the wiring meta-gate)
│   └── severity-posture.json        # EDIT: add HR1 under the "registered" section (C4 in the wiring meta-gate)
├── glossary.md                      # EDIT: add the HR1 row to the rules table + bump the "Currently N rules" anchor (55 -> 56)
└── readiness/
    └── readiness-model.md           # REFERENCE ONLY, not edited -- confirms the model-level tier is orthogonal to the seven-stage spine (no new stage key added here)

mappings/
├── retail_store_sales/source-map.yaml   # UNCHANGED -- READ-ONLY input to HR1
└── demo_sample_orders/source-map.yaml   # UNCHANGED -- READ-ONLY input to HR1

tests/
├── unit/
│   ├── test_rules_wiring.py         # EDIT: add "HR1" to EXPECTED_RULE_IDS (single source of truth the meta-gate imports)
│   ├── test_wiring_meta_gate.py     # UNCHANGED -- the 5/6-place lockstep check that HR1 must satisfy, not edited by this feature
│   └── test_rule_hr1.py             # NEW -- HR1 unit tests (mutation-verified fixtures, per SF1/AP1 discipline)
└── fixtures/
    └── conformed_dimension/          # NEW -- good/bad fixture corpus (undeclared collision, declared-conformed drift on key/type, declared-distinct, stale entry, moot-distinct, missing/malformed manifest, zero/one-star no-op)
```

**Structure Decision**: Single project, additive-only. This feature touches
exactly the six wiring surfaces the existing meta-gate (C1-C7 in
`tests/unit/test_wiring_meta_gate.py`) already enforces for any new
`@register`ed rule, plus its own new rule module, its own new fixture corpus,
and its own new human-authored manifest. It edits NO existing rule module, NO
`source-map.yaml`, and NO per-table `readiness-status.yaml`. The module is
named `rule_hr1.py` (not a generic name later renamed) to match the LANDED
naming convention of `rule_sf1.py` / `rule_ap1.py` -- both of those started
under different working names in their own plans and were renamed to the
`rule_<id>.py` shape at landing; this plan uses the landed shape from the
start since the id (HR1) is already reserved by the collision-avoidance
allocation.

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring
justification: HR1 reuses the existing `Finding`/`RuleContext`/`@register`
mechanism unchanged, adds no new dependency to the static-core import chain
(the one new import, `yaml`, is LAZY and already precedented by SF1), and
introduces no new project, service, or architectural layer.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |
