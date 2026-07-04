# Implementation Plan: Date-Spine Completeness Static Gate

**Branch**: `094-date-spine-completeness` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/094-date-spine-completeness/spec.md`
(clarified 2026-07-04: Q1 default-adopted -- discovery via `tokenize_sql`,
literal classification via `strip_sql_comments`; no `[NEEDS CLARIFICATION]`
markers outstanding; no Principle-V question raised).

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

**Status**: Draft. Stops at the design set below -- NOT approved, NOT
implemented, NOT ratified. No `src/retail/rules/sql.py` edit exists yet and no
test file is written by this stage.

## Summary

Gold Ready (Stage 4) carries two date-dimension checks today, and both stop
short of one gap: `S7` (static, shipped) only checks WHICH BUILDER populated
`dim_date` (`SELECT DISTINCT` vs `generate_series`), never the
`generate_series` call's own arguments; `V-RC15` (live, shipped) proves actual
data coverage but only once a database exists and only after `retail validate`
runs (Principle VIII deferred mode). A migration can satisfy S7 today (it
genuinely calls `generate_series`) while producing a structurally gappy
calendar -- most concretely a non-daily step (`INTERVAL '1 month'`) or a
reversed literal bounds range -- and nothing in the static gate catches it.

This feature adds exactly ONE new `retail check` rule, reserved id **HR8**, as
a new `@register`ed function inside the EXISTING `src/retail/rules/sql.py`
module (the same file S7/S8 already live in, not a new module -- HR8's subject
is SQL-text scanning, same as S1-S8). HR8 reuses S7's own statement-DISCOVERY
loop shape (`tokenize_sql`-based token span for an `INSERT INTO ... dim_date`
statement containing a `generate_series` call) and, for each qualifying call,
reads the call's literal step/bounds text via `strip_sql_comments` (a
literal-preserving stripper, unlike `tokenize_sql` which blanks string
contents) to classify: the step MUST be literal `INTERVAL '1 day'` (ERROR
otherwise, FR-003/FR-004) and, where both bounds are literal dates, `start`
MUST NOT be after `end` (ERROR otherwise, FR-005). Every call clearing those
checks gets exactly one `Severity.INFO` record stating live coverage against
the fact's real span remains PENDING `retail validate` (V-RC15) -- never a
coverage claim (FR-007; hard rule #9). Live, row-level coverage stays fully out
of scope (Principle VIII) and V-RC15 is untouched.

The design mirrors the shipped 087/HR1 rule-adding shape at the DOCUMENT level
(Constitution Check table, wiring-surface enumeration) but is lighter at the
IMPLEMENTATION level: no new manifest file, no new module, no new
`source-map.yaml` key -- the collision-avoidance allocation is the reserved
rule id **HR8** alone. Because `sql.py` is already imported by
`src/retail/rules/__init__.py`, adding HR8 there requires NO edit to
`__init__.py` -- a smaller wiring footprint than a new-module rule.

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `src/retail/` static
core; no new interpreter requirement).

**Primary Dependencies**: stdlib only (`re`, `dataclasses` already used by
`sql.py`) -- no new dependency of any kind, not even a lazy one. HR8 reuses
`tokenize_sql` and `strip_sql_comments`, both already defined in
`src/retail/sql.py` and already imported by `src/retail/rules/sql.py`.

**Storage**: N/A -- no database, no live connection. HR8 reads only committed
`warehouse/migrations/*.sql` text via `ctx.tracked_files` /
`iter_sql_files(ctx)`, the same universe S1-S8 already scan.

**Testing**: `pytest`, `tmp_path`-built inline fixtures per the S5/S6/S7/S8
convention in `tests/unit/test_rc_defaults.py` (NOT a new
`tests/fixtures/<rule>/` corpus directory -- that pattern belongs to
manifest-reading rules like SF1/HR1, not to SQL-text-scanning rules, which
build their fixture SQL inline per test). `pytest.mark.unit` (no live DB, no
network). Mutation-verify discipline: each ERROR/INFO Finding is RED before the
fix and GREEN after, per SC-002/SC-003.

**Target Platform**: the existing `retail check` CLI surface (cross-platform
Python; developed/verified on Windows per repo CLAUDE.md).

**Project Type**: single project -- an addition to the existing
`src/retail/rules/sql.py` static-governance module, not a new service, app, or
module.

**Performance Goals**: N/A -- a `retail check` rule reads at most a few dozen
small committed SQL files per run; no measurable-scale requirement, consistent
with S1-S8's existing cost profile.

**Constraints**: fail CLOSED (non-zero exit) on a non-daily step, an
unclassifiable step, or reversed literal bounds (Principle I); NEVER a numeric
confidence/health/completeness score or an "N of M" / "% covered" tally (hard
rule #9); NEVER proves live row-level coverage (Principle VIII -- that stays
V-RC15's job); NEVER writes any migration file, `source-map.yaml`, or readiness
artifact (Principle V; FR-009); NEVER opens a database connection or reads a
live Power BI/PBIP surface (Principle VIII); does NOT change S7's or V-RC15's
behavior, severity, or message text (FR-010); ASCII, UTF-8 without BOM, short
repo-relative paths (Principle IX).

**Scale/Scope**: exactly ONE new `@register`ed rule (HR8) added inside an
EXISTING module, plus the wiring-surface lockstep the meta-gate already
enforces for any new rule (`EXPECTED_RULE_IDS`, the glossary rules-table row +
"Currently N rules in M families" anchor, `docs/rules/rules-manifest.json`,
the severity-posture record -- both `docs/rules/severity-posture.json` (an
OBSERVED golden regenerated by, not hand-edited alongside) and
`src/retail/severity_posture.py` (the unchanged generator/harness that
produces it; FR-011 names both) -- and `docs/quality/rule-count-claims.yaml`).
No
`src/retail/rules/__init__.py` edit is needed (`sql.py` is already imported).
Current live registered-rule count is **55** in **21** families (per
`docs/quality/rule-count-claims.yaml` / `docs/glossary.md`); HR8 introduces a
brand-new "HR" family (confirmed: no "HR"-prefixed id exists in
`EXPECTED_RULE_IDS` in this worktree today). This is a serialization point
across 19 parallel in-flight features -- most notably 087/HR1, an in-flight
sibling that ALSO introduces the "HR" family under a different id (HR1);
whichever of the two lands first is the commit that appends "HR" to the
family-letter list. Re-verify the live count and family list against the
actual committed files at implement time rather than trusting the numbers
above (see research.md's Parallel-landing serialization note).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | How this design satisfies it |
|---|---|---|
| **I. Agent-First, Gate-Enforced** | A rule fails CLOSED (blocks), never merely advises; compliance is demonstrable by running `retail check`. | HR8 is one `@register`ed rule in the same registry every other checker rule uses. A non-daily step (FR-003), an unclassifiable step (FR-004), or reversed literal bounds (FR-005) each emit `Severity.ERROR`, a non-zero `retail check` exit -- no advisory/warn-only mode for any of the three proven-defect cases. |
| **III. Medallion/Gold-Only** | `gold` IS a Kimball star (fact + CONFORMED dimensions); Power BI reads `gold` only; Postgres-first. | HR8 strengthens Gold Ready's existing date-dimension checks (alongside S6/S7/S8) that gate what reaches `gold` before Power BI ever reads it. It opens no Postgres connection and touches no Power BI surface -- it reads only the committed migration TEXT that will later be run to build `gold`. |
| **IV. Source-Mapping-Before-Silver** | No `silver.*` SQL before the source-map is reviewed+approved. | HR8 does not write or gate any `silver.*` SQL and adds no source-mapping-gate obligation; it inspects an already-authored GOLD migration's `dim_date` build, a step that by convention (S6/S7/S8's own precondition) already happens after Mapping Ready and Silver Ready are cleared for that table. |
| **V. Agent-Stops-at-Judgment** | The agent MUST NOT decide grain/PII/business-policy/approval alone; it raises an unresolved-questions entry and STOPS. NEVER self-grant a readiness pass. | HR8 enforces an ALREADY-SETTLED convention (daily-grain date dimensions, presupposed today by S7's own docstring, V-RC15, and `docs/readiness/gold-ready.md`) -- it decides no new grain, PII, or business-policy question, and the spec's own Clarifications section confirms both candidate ambiguities resolve against existing conventions, not an open ruling. HR8 records no readiness stage, no `approvals[]` entry, and self-grants no pass anywhere (SCOPE GUARD; FR-009). |
| **VI. Defaults-Then-Deviations** | Start from existing rulings; record only deviations. | HR8 introduces no new cleaning/modeling default; it enforces conformance to the daily-grain convention ADR RC15 and S7 already presuppose. The 2026-07-04 clarification (which existing utility supplies discovery vs literal text) is itself a Principle-VI mechanism default, recorded in spec.md Clarifications, not a new business rule. |
| **VII. C086-is-an-example** | Generic templates carry no domain specifics. | `dim_date`, `retail_store_sales`, and any other worked-example name in the spec/plan are ILLUSTRATIVE only; HR8's matching logic keys off the existing generic `dim_date`-prefix convention (already used by S7/S8) and resolves any `warehouse/migrations/*.sql` path, never a hardcoded filename or domain-specific identifier (FR-014; SC-007). |
| **VIII. Static-First/Live-Deferred** | A live DB surface is deferred; author static structure + mark live PENDING. | HR8 is 100% static: it reads only `ctx.tracked_files` content via `iter_sql_files`, opens no database, and invokes no execution adapter. Live row-level date-spine coverage against the fact's real min/max (whether the MATERIALIZED calendar actually covers the fact) is explicitly deferred to `V-RC15`/`retail validate`, unchanged (FR-006). Every structurally-sound build gets an explicit `Severity.INFO` "pending live validate" marker (FR-007) rather than silence or a fabricated pass. |
| **IX. Secrets/Reproducibility** | Never commit a real host/DSN/secret; ASCII, reproducible, Windows-safe. | HR8 touches no connection string or credential -- it reads only repo-relative SQL file paths already tracked by git. The one code change (`src/retail/rules/sql.py`) and its tests are ASCII, UTF-8 without BOM, using short repo-relative paths well under the Windows `MAX_PATH` budget (FR-013). |
| **Hard rule #9** | NO fabricated confidence/health/maturity score or completeness count. | HR8's `Finding` objects carry `rule_id` / `Severity` / `message` / `locator` only (the existing, unchanged `Finding` dataclass). No percentage, ratio, "N of M", or completeness count is computed or emitted anywhere in the design; the FR-007 INFO record explicitly forbids coverage-proof language ("covers", "complete", "gap-free") (FR-008; SC-004; SC-005). |

**Result**: PASS. No principle requires a documented violation; Complexity
Tracking below is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/094-date-spine-completeness/
├── spec.md              # Feature specification (input to this stage; already clarified)
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` directory: HR8 is a static file-reading rule with no network
API/CLI contract beyond the existing `Rule = Callable[[RuleContext],
Iterable[Finding]]` shape already defined in `src/retail/core.py` -- there is
no new contract surface to specify separately (consistent with the S7/S8/HR1
precedent, none of which added a `contracts/` directory either).

### Source Code (repository root)

This is the existing single-project `src/retail/` static-governance library.
No new project, service, top-level directory, or rule MODULE is introduced.
Concrete real paths this feature adds or edits (implementation-stage; recorded
here so the plan does not miss any wiring surface per FR-011):

```text
src/retail/
├── core.py                          # UNCHANGED -- Finding/RuleContext/Severity/is_test_path reused as-is
├── sql.py                           # UNCHANGED -- tokenize_sql / strip_sql_comments reused as-is (both already exist)
├── registry.py                      # UNCHANGED -- @register/all_rules() reused as-is
├── severity_posture.py              # UNCHANGED (code) -- this is the GENERATOR/observation harness (feature 044) that PRODUCES docs/rules/severity-posture.json by forcing each live registered rule; HR8 needs no edit to this module's code, only a re-run of its generator/golden test so the JSON output picks up HR8's observed ["error", "info"] entry (FR-011's "severity-posture record" names both files; this is the mechanism, not a hand-edit target)
└── rules/
    ├── __init__.py                  # UNCHANGED -- `sql` submodule is ALREADY in the import list; no edit needed for HR8 specifically
    └── sql.py                       # EDIT: add one new @register("HR8", ...) function alongside s7_contiguous_date_dim/s8_date_dim_no_unknown_member; does NOT edit s7_contiguous_date_dim's body (FR-010) -- HR8 re-derives its own statement span via the same public tokenize_sql/strip_sql_comments utilities rather than factoring a shared helper that would touch S7's function

docs/
├── quality/
│   └── rule-count-claims.yaml       # EDIT: bump claimed-count in lockstep with registration (re-read live count at implement time, do not assume 55->56 -- see Technical Context serialization note)
├── rules/
│   ├── rules-manifest.json          # EDIT: add {"id": "HR8", "title": "..."} entry (regenerated golden, the wiring meta-gate's manifest check)
│   └── severity-posture.json        # REGENERATE (not hand-edited): this file is an OBSERVED golden record produced by src/retail/severity_posture.py, which drives every registered rule over a forced/synthetic fixture and records the SORTED SET of severity classes it emits (feature 044; confirmed by reading the module docstring) -- HR8 emits BOTH Severity.ERROR (FR-003/FR-004/FR-005) and Severity.INFO (FR-007), so its observed entry is "HR8": ["error", "info"], the same multi-class shape already precedented by "S4b" (a shipped rule that also emits two severities). No manual JSON edit; re-run the generator/golden test (test_severity_posture.py) after HR8 registers.
├── glossary.md                      # EDIT: add a NEW "HR" family row to the static-check rules table (HR8 is the family's first member; its CODE lives in sql.py, but its FAMILY IDENTITY is HR, not SQL -- do not fold the row into the existing SQL-family row) + bump the "Currently N rules in M families" anchor (re-read live numbers at implement time; if 087/HR1 has already landed and added "HR" to the family-letter list, this edit adds HR8's row under the EXISTING HR family and does not re-add "HR" to the letter list a second time)
└── readiness/
    └── gold-ready.md                # EDIT (FR-012): "Required checks" table's static retail check row names HR8 alongside S6/S7, and states live coverage remains V-RC15's job

warehouse/
└── migrations/
    └── 0004_create_gold_retail_store_sales_star.sql   # UNCHANGED, READ-ONLY -- confirmed (research.md) to already pass HR8 cleanly (daily step, chronological literal bounds); this is the SC-001 mutation-verification target, never edited by this feature

tests/
└── unit/
    └── test_rc_defaults.py          # EDIT: add HR8 tests following the existing S5/S6/S7/S8 tmp_path-fixture convention in this SAME file (not a new tests/fixtures/ corpus directory); also add "HR8" to EXPECTED_RULE_IDS in test_rules_wiring.py
```

**Structure Decision**: Single project, additive-only, and the LIGHTEST-FOOTPRINT
option available: HR8 is a NEW `@register`ed FUNCTION inside the ALREADY-EXISTING
`src/retail/rules/sql.py` module (same file as S1-S8), not a new module like
087/HR1's `rule_hr1.py`. This means `src/retail/rules/__init__.py` needs NO
edit at all (the `sql` submodule import already fires HR8's `@register` as a
side effect of the existing `sql` import). The feature touches exactly the five
wiring-surface files the existing meta-gate enforces for any new rule id
(`EXPECTED_RULE_IDS`, glossary, rules-manifest, severity-posture,
rule-count-claims) plus its own new function body, its own new inline test
fixtures, and one `docs/readiness/gold-ready.md` prose edit (FR-012). It edits
NO existing rule's body or message (S7/S8 stay byte-unchanged), NO
`source-map.yaml`, and NO per-table `readiness-status.yaml`.

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring
justification: HR8 reuses the existing `Finding`/`RuleContext`/`@register`
mechanism and the existing `tokenize_sql`/`strip_sql_comments` utilities
unchanged, adds NO new dependency at all (not even a lazy one, unlike SF1/HR1's
lazy `yaml` import), and introduces no new project, service, module, or
architectural layer.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |
