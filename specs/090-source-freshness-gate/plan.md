# Implementation Plan: Source Freshness / Staleness Declaration and Static Presence Check

**Branch**: `090-source-freshness-gate` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/090-source-freshness-gate/spec.md`
(clarified 2026-07-04: C1-C4 default-adopted, C1's token grammar deferred to this
plan, Q-FR014-SCOPE OPEN for the owner).

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

**Status**: Draft. Stops at the design set below -- NOT approved, NOT
implemented, NOT ratified. `src/retail/rules/rule_hr4.py` does not exist yet at
this stage, `templates/source-map.yaml` is not yet edited, and no filled
`mappings/<table>/source-map.yaml` is touched.

## Summary

The `bi-sql-knowledge` skill names PB-SQL-09 ("gates pass but data is stale / a
segment is missing") as a recurring production symptom with no gate anywhere in
the readiness spine today. This feature closes the FRESHNESS half only (not the
missing-segment half, FR-010): it adds exactly one new key,
`meta.freshness` (`expected_cadence` + `max_staleness`), to the existing
`source-map.yaml` `meta:` block, and exactly one new static `retail check`
rule, reserved id **HR4**, that fails closed when a FILLED table's
`meta.freshness` block is PRESENT but missing/blank/unparseable on either
sub-key.

The design mirrors the HR1 precedent (spec 087, same `HR*` id family) at the
mechanism layer: the existing `@register`/`Finding`/`RuleContext`/
`is_test_path` machinery, a LAZY `import yaml`, and the six-surface wiring
lockstep. It diverges from HR1 in one load-bearing way: HR1 explicitly adds NO
key to `source-map.yaml` (that surface was outside its allocation); this
feature's ENTIRE allocation IS a `source-map.yaml` key. So `templates/
source-map.yaml` is EDITED (schema documentation, generic placeholder values)
but the two committed FILLED maps (`retail_store_sales`, `demo_sample_orders`)
are left UNCHANGED and READ-ONLY -- populating them with a real SLA would
either fabricate a business judgment the agent may not make (hard rule #9,
FR-002) or silently pre-empt the OPEN FR-014 ruling.

HR4 therefore ships PRESENCE-GATED: it fails closed on a `meta.freshness`
block that IS PRESENT but malformed (this is uncontroversial Principle-I
enforcement of FR-002's well-formedness contract, and fires on zero tables
today). It does NOT fail closed on a filled map that carries NO
`meta.freshness` block at all -- deciding that omission is itself an error,
for which tables, and since when, is exactly Q-FR014-SCOPE's governance-shape
question (Principle V), which this plan does not settle. This keeps `retail
check` GREEN on the current tree (neither committed map has the block, so
there is nothing malformed to flag) while giving User Story 2's malformed-
block scenarios a real, fixture-exercised, fail-closed path today.

One mechanical decision this plan DOES resolve (deferred by spec.md
Clarification C1 to plan, not to implementation): the exact token grammar for
"well-formed." See Technical Context and data-model.md -- a small, generic,
permissive vocabulary (a closed cadence enum plus a magnitude+unit duration
grammar, with the `one_time`/`static` sentinel reserved per C2), chosen so
"unparseable" is a well-defined fail-closed test without inlining any C086/
`retail_store_sales` value (FR-011).

One governance-shape question stays genuinely OPEN for the owner (FR-014,
Q-FR014-SCOPE): whether `meta.freshness` becomes mandatory on every existing
and future map (retroactive) or only on newly-authored/re-touched ones going
forward, and how a one-time/static source's opt-out is handled. This plan does
not settle it; the presence-gated design is chosen precisely because it
requires no ruling to land safely and remains extensible either way once the
owner rules (see research.md "Open").

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `src/retail/` static
core; no new interpreter requirement).

**Primary Dependencies**: stdlib only at import time (`pathlib`, `re`,
`dataclasses`, `typing`) plus a LAZY `import yaml` inside the rule function
body, mirroring HR1/SF1 -- `yaml` (PyYAML, already a dev/optional dependency
elsewhere in the repo) is kept OUT of the `retail check` static-core import
chain so the checker's stdlib-only floor (Principle VIII) is unaffected.

**Storage**: N/A -- no database, no live connection. HR4 reads one class of
committed text file: `mappings/<table>/source-map.yaml` (existing, per-table,
owned by the source-mapping gate). It never reads `templates/source-map.yaml`
as an instance (C3) and never reads any file under `tests/` as a real subject
(`is_test_path` exemption for fixtures used only by the rule's own unit tests).

**Testing**: `pytest` with the existing `tests/unit/` fixture + mutation-verify
discipline (`tests/fixtures/<rule>/` good/bad corpora; each ERROR Finding is
RED before the assert and GREEN after, per the SF1/HR1 precedent).
`pytest.mark.unit` per repo convention (no live DB, no network -- this is a
pure static rule).

**Target Platform**: the existing `retail check` CLI surface (cross-platform
Python; developed/verified on Windows per repo CLAUDE.md, no OS-specific
behavior).

**Project Type**: single project -- an addition to the existing `src/retail/`
static-governance library plus its docs/tests, not a new service or app.

**Performance Goals**: N/A (a `retail check` rule reads at most a few dozen
small committed `source-map.yaml` files per run; no measurable-scale
requirement per the repo's existing rule set).

**Constraints**: fail CLOSED (non-zero exit) on a PRESENT-but-malformed
`meta.freshness` block on a filled map (Principle I); NEVER fail closed on a
filled map's OUTRIGHT ABSENCE of the block (that is FR-014's open ruling, not
this plan's to make); NEVER a numeric confidence/health/freshness score or an
"N of M" tally (hard rule #9); NEVER writes `source-map.yaml`,
`readiness-status.yaml`, or `approvals[]`, and NEVER auto-fills/defaults a
table's `expected_cadence`/`max_staleness` (Principle V, FR-008); NEVER opens
a database connection or reads a live Power BI/PBIP surface (Principle VIII);
ASCII, UTF-8 without BOM, short repo-relative paths (Principle IX, Windows
`MAX_PATH`).

**Token grammar (Clarification C1, resolved at this stage)**:

- `expected_cadence`: case-insensitive match against a small closed enum --
  `daily | weekly | monthly | quarterly | annual` (singular calendar-period
  words, generic and domain-agnostic) PLUS the reserved sentinel `one_time`
  (with `static` accepted as a synonym, Clarification C2). Any other string
  (including empty/whitespace-only) is malformed.
- `max_staleness`: case-insensitive match against a magnitude-plus-unit
  duration, `^\s*\d+\s*(hour|day|week|month|quarter|year)s?\s*$` (a positive
  integer, optional whitespace, a calendar-unit word, optional trailing `s`)
  PLUS the reserved non-duration sentinel `n/a` (paired with an
  `expected_cadence` of `one_time`/`static`, Clarification C2). Any other
  string (including empty/whitespace-only, a bare number with no unit, or an
  unrecognized unit word) is malformed.
- Both checks trim surrounding whitespace before matching (FR-002). Neither
  grammar inlines a C086/`retail_store_sales` value (FR-011) -- the units and
  enum members are generic calendar vocabulary, not domain-specific.

**Scale/Scope**: exactly ONE new `@register`-ed rule (HR4), one new
`meta.freshness` key on an existing schema (no new file), and the same
six-surface wiring lockstep the meta-gate already enforces for any new
registered rule (`__init__.py`, `EXPECTED_RULE_IDS`, the glossary rules-table
row + "Currently N rules" anchor, `docs/rules/rules-manifest.json`,
`docs/rules/severity-posture.json`, `docs/quality/rule-count-claims.yaml`).
Current live registered-rule count is **55** (verified via
`json.load("docs/rules/rules-manifest.json")` at research time); HR4 lands as
rule **56** if it lands before any other in-flight rule-adding feature (e.g.
087/HR1) -- re-verify against the live manifest at implement time rather than
trusting this number, exactly as 087's own plan cautions for itself. Likewise
the glossary's family list ("21 families") gains an `HR` family only if HR1
has not already added it; implement-time must check before appending a
duplicate family token.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | How this design satisfies it |
|---|---|---|
| **I. Agent-First, Gate-Enforced** | A rule fails CLOSED (blocks), never merely advises; compliance is demonstrable by running `retail check`. | HR4 is one `@register`-ed rule in the same registry every other checker rule uses; a present-but-malformed `meta.freshness` block on a filled map emits `Severity.ERROR`, a non-zero `retail check` exit, with no advisory/warn-only mode (FR-004(b)). There is no toggle to downgrade a malformed block to a warning. |
| **III. Medallion/Gold-Only** | `gold` IS a Kimball star (fact + CONFORMED dims); Power BI reads `gold` only; Postgres-first. | Not directly engaged by this feature -- HR4 is a Stage-1/2-adjacent SOURCE concern (arrival cadence), not a gold-shape check. It opens no Postgres connection and touches no Power BI surface, consistent with this principle's DATA-path boundary; it neither reads nor asserts anything about `gold_star`. |
| **IV. Source-Mapping-Before-Silver** | No `silver.*` SQL before the source-map is reviewed+approved. | HR4 does not write or gate any `silver.*` SQL. It reads `source-map.yaml` strictly as a CONSUMER, after Mapping Ready review already happened (FR-005: it never fires pre-Stage-2, when no `source-map.yaml` exists yet). |
| **V. Agent-Stops-at-Judgment** | The agent MUST NOT decide grain/PII/business-policy/approval alone; it raises an unresolved-questions entry and STOPS. NEVER self-grant a readiness pass. | The `expected_cadence`/`max_staleness` VALUES are a business-SLA judgment only a data owner supplies (FR-002) -- HR4 never invents, defaults, or auto-fills either (FR-008). The MANDATORY-vs-going-forward SCOPE question (FR-014, Q-FR014-SCOPE) is left explicitly OPEN in spec.md for a named-human ruling; this plan's presence-gated design is chosen precisely so it settles nothing about that scope on the agent's own authority. HR4 records no `approvals[]` entry and self-grants no readiness pass (FR-008) -- it reads and reports only. |
| **VI. Defaults-Then-Deviations** | Start from existing rulings; record only deviations. | HR4 introduces no new cleaning/modeling default; it enforces well-formedness of a value ALREADY declared under the existing `meta:` block convention. The C1/C2/C3 clarify-session defaults (grammar shape, one_time token, template exemption) are reasonable constitution-safe defaults per Principle VI, recorded in spec.md Clarifications and made concrete in this plan's Technical Context; the genuinely open FR-014 scope question is NOT defaulted (no safe default exists that avoids either fabrication or an unconsented status flip). |
| **VII. C086-is-an-example** | Generic templates carry no domain specifics. | The `templates/source-map.yaml` edit uses obvious generic placeholders (`"<cadence: daily\|weekly\|monthly\|quarterly\|annual\|one_time>"` style, no `retail_store_sales` value). The token grammar (data-model.md) uses only generic calendar-unit words, never a C086/pharmacy-specific cadence. The worked example (`retail_store_sales`) may be cited as a filled instance that currently HAS NO `meta.freshness` block (an honest fact, not a copied value) but is never edited by this feature. |
| **VIII. Static-First/Live-Deferred** | A live DB surface is deferred; author static structure + mark live PENDING. | HR4 is 100% static: it reads only committed `ctx.tracked_files` content, opens no database, and invokes no execution adapter (FR-003, FR-006). `yaml` is imported LAZILY, kept out of the stdlib-only static-core import chain. The live arrival-time comparison is explicitly OUT of scope and named as a future `retail validate` seam (FR-006); the `[PENDING LIVE FRESHNESS CHECK]` marker is recorded as that FUTURE surface's contract -- this feature introduces no live-reporting surface of its own (Clarification C4) and HR4 never emits the marker itself. |
| **IX. Secrets/Reproducibility** | Never commit a real host/DSN/secret; ASCII, reproducible, Windows-safe. | HR4 touches no connection string or credential -- it reads only repo-relative YAML paths. All new/edited artifacts (rule module, template edit, docs) are ASCII, UTF-8 without BOM, and keep short repo-relative paths (`src/retail/rules/rule_hr4.py`, `templates/source-map.yaml`) well under the Windows `MAX_PATH` budget (FR-013). |
| **Hard rule #9** | NO fabricated confidence/health/maturity score or completeness count. | HR4's `Finding` objects carry `rule_id`/`severity`/`message`/`locator` only (the existing `Finding` dataclass, unchanged). No percentage, ratio, "N of M", or freshness score is computed or emitted anywhere in the design (FR-007, SC-005). A human-declared `max_staleness` value is a declared SLA input, not a computed score (FR-007 explicitly distinguishes the two). |

**Result**: PASS. No principle requires a documented violation; Complexity
Tracking below is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/090-source-freshness-gate/
├── spec.md              # Feature specification (input to this stage; already clarified)
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` directory: HR4 is a static file-reading rule with no network
API/CLI contract beyond the existing `Rule = Callable[[RuleContext],
Iterable[Finding]]` shape already defined in `src/retail/core.py` -- there is
no new contract surface to specify separately (consistent with the SF1/AP1/HR1
precedent, none of which added a `contracts/` directory either).

### Source Code (repository root)

This is the existing single-project `src/retail/` static-governance library.
No new project, service, or top-level directory is introduced. Concrete real
paths this feature adds or edits (implementation-stage; recorded here so the
plan does not miss any wiring surface per FR-012):

```text
src/retail/
├── core.py                          # UNCHANGED -- Finding/RuleContext/Severity/is_test_path reused as-is
├── registry.py                      # UNCHANGED -- @register/all_rules() reused as-is
└── rules/
    ├── __init__.py                  # EDIT: add "rule_hr4" to the import list AND __all__ (the only discovery step -- no autodiscovery)
    ├── rule_sf1.py                  # UNCHANGED -- read-only design precedent, not edited by this feature
    ├── rule_hr1.py                  # UNCHANGED IF PRESENT -- sibling HR-family rule (spec 087); not read, not edited, order-independent
    └── rule_hr4.py                  # NEW -- the HR4 rule module (this feature's one new rule)

templates/
└── source-map.yaml                  # EDIT: add a `meta.freshness` placeholder block (expected_cadence + max_staleness) as a sibling of the existing meta keys; generic placeholder values only (Principle VII); HR4 MUST NOT evaluate this file (C3)

mappings/
├── retail_store_sales/source-map.yaml   # UNCHANGED, READ-ONLY -- this feature does not add a real freshness declaration here (FR-002: no fabricated SLA; FR-014 scope is OPEN)
└── demo_sample_orders/source-map.yaml   # UNCHANGED, READ-ONLY -- same reasoning

docs/
├── quality/
│   └── rule-count-claims.yaml       # EDIT: bump claimed-count in lockstep with the registration (re-verify the live number at implement time; do not hardcode 56)
├── rules/
│   ├── rules-manifest.json          # EDIT: add {"id": "HR4", "title": "..."} entry (regenerated golden, wiring meta-gate)
│   └── severity-posture.json        # EDIT: add HR4 under the "registered" section (wiring meta-gate)
├── glossary.md                      # EDIT: add the HR4 row to the rules table + bump the "Currently N rules" anchor + add the `HR` family token to the family list IF NOT ALREADY PRESENT (re-verify at implement time; do not duplicate if 087/HR1 landed first)
└── readiness/
    ├── source-ready.md              # REFERENCE ONLY, not edited -- confirms Stage 1 has no `retail check` gate and that `source-map.yaml` is a Stage-2 artifact; HR4's Stage-2-onward firing boundary (FR-005) is consistent with this doc's existing rule, not a change to it
    └── source-drift.md              # REFERENCE ONLY, not edited -- FR-009 forbids touching its taxonomy/templates; cited only for the `[PENDING LIVE ...]` marker convention this feature's FR-006 reuses by name

tests/
├── unit/
│   ├── test_rules_wiring.py         # EDIT: add "HR4" to EXPECTED_RULE_IDS (single source of truth the meta-gate imports)
│   ├── test_wiring_meta_gate.py     # UNCHANGED -- the lockstep check that HR4 must satisfy, not edited by this feature
│   └── test_rule_hr4.py             # NEW -- HR4 unit tests (mutation-verified fixtures, per SF1/HR1 discipline)
└── fixtures/
    └── source_freshness/            # NEW -- good/bad fixture corpus: well-formed block (both sub-keys valid), missing block entirely (must produce NO Finding per this plan's presence-gated design -- a fixture proving the negative), block present with one sub-key blank, block present with an unparseable cadence token, block present with an unparseable staleness duration, one_time/static + n/a pairing (valid), template-file exemption (must produce NO Finding even though the template's placeholder text would otherwise fail the grammar), pre-Stage-2 table with no source-map.yaml at all (no Finding)
```

**Structure Decision**: Single project, additive-only. This feature touches
the same six wiring surfaces the existing meta-gate enforces for any new
`@register`-ed rule, plus its own new rule module, its own new fixture corpus,
and one schema edit to `templates/source-map.yaml`. It edits NO filled
`source-map.yaml`, NO other readiness artifact's schema, and NO per-table
`readiness-status.yaml`. The module is named `rule_hr4.py` from the start
(not a generic name later renamed) to match the landed naming convention of
`rule_sf1.py`/`rule_ap1.py`/`rule_hr1.py`, since the id (HR4) is already
reserved by the collision-avoidance allocation.

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring
justification: HR4 reuses the existing `Finding`/`RuleContext`/`@register`
mechanism unchanged, adds no new dependency to the static-core import chain
(the one new import, `yaml`, is LAZY and already precedented by SF1/HR1), and
introduces no new project, service, or architectural layer. The one
schema edit (`templates/source-map.yaml`) is additive (one new sibling key
under an existing block) and does not restructure any existing field.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |
