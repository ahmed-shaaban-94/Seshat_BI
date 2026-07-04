# Implementation Plan: Dimension History / SCD Policy Readiness

**Branch**: `088-scd-dimension-history-policy` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/088-scd-dimension-history-policy/spec.md`
(clarified 2026-07-04: C1-C7 default-adopted, Q-APPROVAL-SEAM (FR-017) OPEN for the owner).

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

**Status**: Draft. Stops at the design set below -- NOT approved, NOT implemented, NOT
ratified. Neither `src/retail/rules/rule_hr2.py` nor the `scd_type` key edit to
`templates/source-map.yaml` is written by this stage.

## Summary

Gold today is built by one documented mechanism, drop-and-rebuild (batched
`DROP TABLE IF EXISTS`, then each dimension recreated by CTAS or by explicit column DDL
plus `INSERT` -- `.claude/skills/retail-build-warehouse/SKILL.md`, confirmed against the one
committed gold migration in research.md). That mechanism is, in effect, SCD Type-1 for
every dimension in every star, chosen by omission: nothing today lets a human declare that a
dimension's attribute history must be PRESERVED (Type-2) rather than overwritten, and nothing
checks whether the build actually honors that intent. A fact from last year would silently
re-point to this year's attribute value the moment the dimension is rebuilt, with no error and
no warning.

This feature closes the gap at the STATIC layer only, mirroring the shipped SF1
(spec 086) / drafted HR1 (spec 087) shape exactly at the mechanism layer: (1) one new
nested field, `gold_star.dimensions[].scd_type` (`type_1` | `type_2`), added to
`templates/source-map.yaml` and declared by a human at Mapping Ready inside each table's own
`source-map.yaml` (the SAME reviewed artifact that already carries `surrogate_key` and
`has_unknown_member` -- unlike HR1, which declares in a separate cross-star manifest, because
this is a per-table, per-dimension judgment, not a cross-star one); and (2) one new
`@register`ed static `retail check` rule, reserved id **HR2**, that reads that declaration
alongside the table's gold migration SQL (`warehouse/migrations/*create_gold_<table>_star.sql`)
and fails CLOSED when a `type_2`-declared dimension's own gold table is built by the
documented drop-and-rebuild construct -- a proven mechanical contradiction the declared policy
cannot survive. HR2 never decides a dimension's `scd_type` (Principle V: same seam as
grain/PII), never executes SQL, and never writes any source-map or migration file.

Unlike HR1's grain limb (deferred because no machine-readable signal existed), HR2's MVP
detection signal is confirmed implementable NOW: the drop-and-rebuild construct is directly
grepable against the one construct this repo's tooling actually authors for gold, verified
line-for-line against the one committed migration (research.md). Only a FUTURE positive
signal -- recognizing a valid, correctly-authored Type-2 construct once one exists -- is
out of scope, and no such construct exists in any committed migration today.

One governance-shape question stays genuinely OPEN for the owner (FR-017, Q-APPROVAL-SEAM):
whether declaring `scd_type` needs its own named-human approval seam, or folds into the
existing Mapping Ready `approvals[]` sign-off. This plan does not settle it; it records the
PENDING DEFAULT (folds in, no new approval record) and proceeds on that basis until an owner
rules otherwise.

Landing this feature makes `retail check` fail RED on the current committed tree (both
`retail_store_sales` and `demo_sample_orders` have dimensions with no `scd_type` declared
yet, and FR-005 grants no grandfather exemption). This is a deliberate, already-recorded
severity choice (Assumptions: "Severity posture"), not an open question -- see research.md
"Landing precondition." The agent does not, and must not, green this by filling in a
placeholder `scd_type` value on a human's behalf.

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `src/retail/` static core; no new
interpreter requirement).

**Primary Dependencies**: stdlib only at import time (`pathlib`, `dataclasses`, `re`,
`typing`) plus a LAZY `import yaml` inside the rule function body, mirroring SF1
(`rule_sf1.py`) and HR1's plan -- `yaml` (PyYAML) is kept OUT of the `retail check`
static-core import chain so the checker's stdlib-only floor (Principle VIII) is unaffected.
No SQL parser dependency: FR-007's detection is a scoped regex/text match against the two
documented literal constructs (`DROP TABLE IF EXISTS <tok>` / `CREATE TABLE <tok>`), not a
general SQL AST parse.

**Storage**: N/A -- no database, no live connection. HR2 reads two classes of committed text
file: every `mappings/<table>/source-map.yaml` (existing, per-table, owned by the
source-mapping gate; gains one new nested key) and, when present, that table's
`warehouse/migrations/*create_gold_<table>_star.sql` (existing file class, read-only, never
executed).

**Testing**: `pytest` with the existing `tests/unit/` fixture + mutation-verify discipline
(`tests/fixtures/<rule>/` good/bad corpora; each ERROR finding is RED before the assert and
GREEN after, per the SF1/AP1/HR1 precedent). `pytest.mark.unit` per repo convention (no live
DB, no network -- this is a pure static rule). Fixture SQL files live under `tests/` and are
exempt from HR2's own scan via `is_test_path` (they are read directly as inputs to the rule,
not scanned by it as another rule's committed-file corpus).

**Target Platform**: the existing `retail check` CLI surface (cross-platform Python;
developed/verified on Windows per repo CLAUDE.md, no OS-specific behavior; the SQL text
match is line/whitespace-tolerant, not dependent on file-system line-ending normalization
beyond what `Path.read_text` already handles).

**Project Type**: single project -- an addition to the existing `src/retail/`
static-governance library plus its docs/tests/template, not a new service or app.

**Performance Goals**: N/A (a `retail check` rule reads at most a few dozen small committed
YAML files and a handful of migration SQL files per run; no measurable-scale requirement per
the repo's existing rule set).

**Constraints**: fail CLOSED (non-zero exit) on an undeclared `scd_type` (no grandfather
exemption, FR-005), an invalid `scd_type` value (FR-006), or a proven `type_2`-declared
dimension built by drop-and-rebuild (FR-007) -- Principle I; NEVER a numeric confidence/
health/maturity score or an "N of M" tally (hard rule #9, FR-013); NEVER writes any
`source-map.yaml`, migration file, or `scd_type` value, and NEVER decides a dimension's
`scd_type` on a human's behalf (Principle V, FR-011); NEVER opens a database connection,
executes SQL, or reads a live Power BI/PBIP surface (Principle VIII, FR-004, FR-012); ASCII,
UTF-8 without BOM, short repo-relative paths (Principle IX, FR-016, Windows `MAX_PATH`).

**Scale/Scope**: exactly ONE new `@register`ed rule (HR2), one new nested schema key on an
existing template, and the six-surface wiring lockstep the meta-gate already enforces
(`__init__.py`, `EXPECTED_RULE_IDS`, the glossary rules-table row + "Currently N rules"
anchor, `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
`docs/quality/rule-count-claims.yaml`). Current live registered-rule count is **55** (per
`docs/rules/rules-manifest.json`, confirmed by direct read); HR2 lands as rule **56**. This
count is a serialization point across the 19 parallel in-flight features -- re-verify against
the live manifest at implement time rather than trusting this number if other rule-adding
features (e.g. HR1/087) land first.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | How this design satisfies it |
|---|---|---|
| **I. Agent-First, Gate-Enforced** | A rule fails CLOSED (blocks), never merely advises; compliance is demonstrable by running `retail check`. | HR2 is one `@register`ed rule in the same registry every other checker rule uses; an undeclared `scd_type` (FR-005), an invalid value (FR-006), and a proven `type_2`-drop-and-rebuild mismatch (FR-007) all emit `Severity.ERROR`, a non-zero `retail check` exit. There is no advisory/warn-only mode for any of the three (Assumptions: "Severity posture"). FR-005 grants NO already-approved-map grandfather clause -- adopting this feature means every existing map needs an explicit `scd_type` before HR2 is clean, by design. |
| **III. Medallion/Gold-Only** | `gold` IS a Kimball star (fact + CONFORMED dimensions); Power BI reads `gold` only; Postgres-first. | HR2 gives Kimball's dimension-history axis (an axis Principle III's "star" language implies but no existing gate names) its first enforced check. It reads only the already-committed `gold_star.dimensions[]` block of each table's `source-map.yaml` plus that table's own gold migration TEXT -- it opens no Postgres connection and touches no Power BI surface, consistent with the principle's gold-only / Postgres-first boundary being about the DATA path, not this static text-only check. |
| **IV. Source-Mapping-Before-Silver** | No `silver.*` SQL before the source-map is reviewed+approved. | HR2 does not write or gate any `silver.*` SQL. It ADDS one new field to the source-map SCHEMA (`templates/source-map.yaml`), but that field is declared and reviewed exactly like every other Mapping Ready field (`surrogate_key`, `has_unknown_member`) -- inside the SAME artifact a human already reviews and approves before any silver SQL is authored, not a bypass of that review. HR2 reads the table's gold migration only as a CONSUMER, after Mapping Ready and after that migration was separately authored (by `retail-build-warehouse`, a distinct skill); it never re-opens or re-decides the table's own Mapping Ready judgment. |
| **V. Agent-Stops-at-Judgment** | The agent MUST NOT decide grain/PII/business-policy/approval alone; it raises an unresolved-questions entry and STOPS. NEVER self-grant a readiness pass. | Deciding whether a given dimension's attribute history matters enough to preserve (`type_1` vs `type_2`) is a business/modelling judgment the rule exists to ENFORCE, not one the agent may make (Assumptions: "The human authors the `scd_type` value (BLOCKING, Principle V)"). `scd_type` is HUMAN-AUTHORED; HR2 only reads it (FR-003, FR-011). A missing or invalid declaration is never inferred or defaulted -- it is a fail-closed Needs-decision ERROR naming the dimension, demanding the human ruling (FR-005, FR-006). HR2 records no `approvals[]` entry and self-grants no readiness pass. FR-017's approval-seam SHAPE question is left OPEN for the owner, not settled here (same Q-APPROVAL-SEAM shape as HR1's FR-016). |
| **VI. Defaults-Then-Deviations** | Start from existing rulings; record only deviations. | HR2 introduces no new cleaning/modeling default of its own; it enforces that a NEW, explicitly-scoped declaration (`scd_type`) is honored by the ALREADY-documented gold-build mechanism (RC14's drop-and-rebuild-as-Type-1 convention). The clarify session's C1/C2/C4 defaults (schema shape, enum scope, name-resolution normalization) are reasonable constitution-safe defaults per Principle VI, recorded in spec.md Clarifications; C5 is a drafting CORRECTION (what construct the tooling actually authors), not a new default choice; none touch a Principle-V question. |
| **VII. C086-is-an-example** | Generic templates carry no domain specifics. | `dim_<entity_a>` / `dim_customer_rss` are illustrative only, never required names in the rule logic, the template's `scd_type` example, or this plan. No worked-example (C086/pharmacy) dimension name, grain key, or column name is inlined in the rule module, its docstring, the template edit, or the fixture corpus's *naming* (fixture SQL content may mirror the committed `0004` SHAPE for realism, per SC-002's mutation-verified requirement, but introduces no new domain-specific business meaning) (FR-015). |
| **VIII. Static-First/Live-Deferred** | A live DB surface is deferred; author static structure + mark live PENDING. | HR2 is 100% static: it reads only committed `ctx.tracked_files` content (source-map YAML text and migration SQL text), opens no database, executes no SQL, and invokes no execution adapter (FR-004, FR-012). `yaml` is imported LAZILY, kept out of the stdlib-only static-core import chain. Live SCD-2 row-level data-correctness auditing (no duplicate current rows, `effective_to` gaps, correct `is_current` flags) is explicitly OUT of scope and deferred to a future `retail validate` extension (Assumptions) -- HR2 proves the DECLARED policy against the AUTHORED migration text, nothing more. A future positive-recognition signal for a valid Type-2 construct is likewise authored PENDING (recorded, not silently skipped) rather than assumed to exist. |
| **IX. Secrets/Reproducibility** | Never commit a real host/DSN/secret; ASCII, reproducible, Windows-safe. | HR2 touches no connection string or credential -- it reads only repo-relative YAML/SQL paths. All new/edited artifacts (rule module, template edit, docs, fixtures) are ASCII, UTF-8 without BOM, and keep short repo-relative paths (`src/retail/rules/rule_hr2.py`, `templates/source-map.yaml`) well under the Windows `MAX_PATH` budget (FR-016). |
| **Hard rule #9** | NO fabricated confidence/health/maturity score or completeness count. | HR2's `Finding` objects carry `rule_id` / `Severity` / `message` / `locator` only (the existing `Finding` dataclass, unchanged). No percentage, ratio, "N of M", or completeness count is computed or emitted anywhere in the design (FR-013, SC-006). |

**Result**: PASS. No principle requires a documented violation; Complexity Tracking below is
empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/088-scd-dimension-history-policy/
├── spec.md              # Feature specification (input to this stage; already clarified)
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` directory: HR2 is a static file-reading rule with no network API/CLI
contract beyond the existing `Rule = Callable[[RuleContext], Iterable[Finding]]` shape
already defined in `src/retail/core.py` -- there is no new contract surface to specify
separately (consistent with the SF1/AP1/HR1 precedent, none of which added a `contracts/`
directory either).

### Source Code (repository root)

This is the existing single-project `src/retail/` static-governance library. No new
project, service, or top-level directory is introduced. Concrete real paths this feature
adds or edits (implementation-stage; recorded here so the plan does not miss any wiring
surface per FR-014):

```text
templates/
└── source-map.yaml                  # EDIT: add `scd_type: "type_1"` (illustrative
                                      #   placeholder) as a new nested key on each
                                      #   `gold_star.dimensions[]` entry, alongside
                                      #   `surrogate_key` / `has_unknown_member` /
                                      #   `attributes[]`. This is the FEATURE'S ENTIRE
                                      #   schema footprint (collision-avoidance
                                      #   allocation) -- no top-level key, no other
                                      #   sibling key on the dimension entry.

src/retail/
├── core.py                          # UNCHANGED -- Finding/RuleContext/Severity/is_test_path reused as-is
├── registry.py                      # UNCHANGED -- @register/all_rules() reused as-is
└── rules/
    ├── __init__.py                  # EDIT: add "rule_hr2" to the import list AND __all__ (the only discovery step -- no autodiscovery)
    ├── rule_sf1.py                  # UNCHANGED -- read-only design precedent, not edited by this feature
    └── rule_hr2.py                  # NEW -- the HR2 rule module (this feature's one new rule)

docs/
├── quality/
│   └── rule-count-claims.yaml       # EDIT: bump claimed-count (55 -> 56) in lockstep with the registration
├── rules/
│   ├── rules-manifest.json          # EDIT: add {"id": "HR2", "title": "..."} entry (regenerated golden, the wiring meta-gate)
│   └── severity-posture.json        # EDIT: add HR2 under the "registered" section (["error"] -- no WARNING-only case)
├── glossary.md                      # EDIT: add the HR2 row to the rules table + bump the "Currently N rules" anchor (55 -> 56)
└── readiness/
    ├── mapping-ready.md             # REFERENCE ONLY (not edited unless the doc enumerates per-dimension fields) -- confirms `scd_type` is declared at Stage 2, not a new stage
    └── gold-ready.md                # REFERENCE ONLY (not edited unless the doc enumerates static rule ids) -- confirms HR2 runs on the existing Gold Ready static surface alongside S6/S7, adding no new stage key

mappings/
├── retail_store_sales/source-map.yaml   # UNCHANGED by this plan -- READ-ONLY input to HR2; per
│                                         #   research.md "Landing precondition," a HUMAN must
│                                         #   later add a real `scd_type` per dimension to clear
│                                         #   HR2's FR-005 finding -- NOT performed here
└── demo_sample_orders/source-map.yaml   # UNCHANGED by this plan -- same read-only/landing-cost note

warehouse/migrations/
└── 0004_create_gold_retail_store_sales_star.sql  # UNCHANGED -- READ-ONLY input to HR2 (confirms the FR-007 construct shape; research.md)

tests/
├── unit/
│   ├── test_rules_wiring.py         # EDIT: add "HR2" to EXPECTED_RULE_IDS (single source of truth the meta-gate imports)
│   ├── test_wiring_meta_gate.py     # UNCHANGED -- the wiring lockstep check that HR2 must satisfy, not edited by this feature
│   └── test_rule_hr2.py             # NEW -- HR2 unit tests (mutation-verified fixtures, per SF1/AP1/HR1 discipline)
└── fixtures/
    └── scd_history/                  # NEW -- good/bad fixture corpus:
        ├── source-map-declared.yaml       #   every dim has a valid scd_type (US1 AS1)
        ├── source-map-invalid-value.yaml  #   an scd_type outside {type_1, type_2} (US1 AS3)
        ├── source-map-undeclared.yaml     #   one or more dims missing scd_type entirely (US3)
        ├── gold-ddl-insert-drop-rebuild.sql  # type_2 dim built via batched-DROP + DDL+INSERT (US2 AS1, the primary/committed-tooling shape)
        ├── gold-ctas-drop-rebuild.sql        # type_2 dim built via CTAS drop-and-rebuild (US2 AS1, the additional authored-form case)
        └── gold-type1-drop-rebuild.sql       # type_1 dim built via drop-and-rebuild -- MUST emit no finding (US2 AS2, FR-009)
```

**Structure Decision**: Single project, additive-only. This feature touches exactly the six
wiring surfaces the existing meta-gate (`tests/unit/test_wiring_meta_gate.py`) already
enforces for any new `@register`ed rule, plus its own new rule module, its own new fixture
corpus, and ONE new nested key on the existing `templates/source-map.yaml` (the feature's
entire schema footprint, per the collision-avoidance allocation -- 090/103/105 stay in their
own, different sub-keys and none of their directories exist yet in this tree). It edits NO
other field on the dimension entry, NO existing rule module, and NO per-table
`readiness-status.yaml`. The module is named `rule_hr2.py` (not a generic name later
renamed) to match the LANDED naming convention of `rule_sf1.py` / `rule_ap1.py`, since the
id (HR2) is already reserved by the collision-avoidance allocation.

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring justification: HR2
reuses the existing `Finding`/`RuleContext`/`@register` mechanism unchanged, adds no new
dependency to the static-core import chain (the one new import, `yaml`, is LAZY and already
precedented by SF1/HR1), and introduces no new project, service, or architectural layer. The
one schema edit (`templates/source-map.yaml`) is a single additive nested key, not a
structural change to the file's shape.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |
