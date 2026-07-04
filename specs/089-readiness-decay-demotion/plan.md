# Implementation Plan: Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker

**Branch**: `089-readiness-decay-demotion` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/089-readiness-decay-demotion/spec.md`
(clarified 2026-07-04: same-day-not-stale, path-token extraction, latest-approvals-entry
all default-adopted; the `stale_review`-vs-drift-finding scope question left OPEN for the
owner).

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

**Status**: Draft. Stops at the design set below -- NOT approved, NOT implemented, NOT
ratified. No `src/retail/rules/rule_hr3.py` is written by this stage, and no existing file
(`readiness_status.py`, `gitutil.py`, `readiness-status.yaml`, the wiring surfaces) is
edited by this stage.

## Summary

`docs/readiness/source-drift.md:74` states a Downstream-invalidation rule in prose: a
`warning`/`blocked` drift at Source Ready makes every downstream `pass` stage SUSPECT, and
"the human/agent re-runs the stage gate" -- but nothing today enforces that sentence. RS1
(`src/retail/rules/readiness_status.py`) checks a `readiness-status.yaml` file's internal
consistency at a single point in time; it never compares dates and never treats
`source_ready`'s status as an implication for other stages. A table can drift, nothing
downstream ever gets re-confirmed, and `retail check` stays green.

This plan closes the hole with exactly one new static rule, reserved id **HR3**, plus
exactly one new optional, additive `readiness-status.yaml` key, `stale_review`. HR3 fails
`retail check` CLOSED with an ERROR-severity `stale_pass` finding whenever either (a) a
downstream stage is `pass` while `source_ready` is recorded `warning`/`blocked` (drift-
triggered staleness, FR-002), or (b) an approval-bearing `pass` stage cites evidence whose
git-commit date is strictly later than its (latest) recorded `approvals[].at` date
(approval-lag staleness, FR-003). HR3 never writes any file (FR-005); the human clears a
finding either by editing the stage's own state or by recording a shape-valid, correctly
dated `stale_review` entry (FR-006/FR-007), reusing RS1's existing
`"Person Name (authority_class)"` owner-shape discipline verbatim.

The design mirrors the shipped RS1 rule and the HR1 design-stage plan (spec
`087-conformed-dimension-readiness`) at the mechanism layer: a pure static, read-only
`@register`ed rule operating on `ctx.tracked_files` and (newly, for this feature) git
commit-date history, with no live DB, no executor, and no numeric score. The one genuinely
new mechanical piece is a git-commit-date-of-a-path helper, which does not exist in
`src/retail/gitutil.py` today and must be added (see Project Structure).

One governance-shape question is explicitly left OPEN per the spec's own Clarifications
rather than defaulted here: whether a `stale_review` entry may also clear a drift-triggered
(FR-002) finding, or is scoped to approval-lag (FR-003) findings only. FR-007 as written
scopes it to FR-003 only; this plan implements that as the PENDING DEFAULT and does not
broaden it (Principle V -- this is a product-scope ruling about what the reaffirmation
escape hatch is FOR, not a mechanical default this stage may silently pick).

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `src/retail/` static core; no new
interpreter requirement).

**Primary Dependencies**: stdlib only at import time (`pathlib`, `dataclasses`, `re`,
`datetime`, `subprocess` via the existing `gitutil` module) plus a LAZY `import yaml` inside
the rule function body, mirroring RS1 and HR1 -- `yaml` stays OUT of the `retail check`
static-core import chain (Principle VIII).

**Storage**: N/A -- no database, no live connection. HR3 reads two classes of committed
input: every `mappings/<table>/readiness-status.yaml` (existing, per-table, ADR 0004) and
the git commit history of paths those files cite as evidence (via a new `gitutil.py`
helper; committed history only, never the filesystem `mtime` of a local checkout).

**Testing**: `pytest` with the existing `tests/unit/` fixture + mutation-verify discipline
(`tests/fixtures/<rule>/` good/bad corpora; each ERROR Finding is RED before the assert and
GREEN after, per the RS1/SF1/AP1 precedent). `pytest.mark.unit` per repo convention. Because
HR3 reads real git commit dates, its fixtures need CONTROLLED commit timestamps (a small
throwaway fixture repo built and committed with `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` set to
DIFFERENT values inside the test, not a read of this repo's own live history) so
date-comparison assertions are deterministic, independent of when the fixture happens to be
committed to `Seshat_BI` itself, AND actually pin FR-004's author-vs-committer discipline --
a fixture where both dates match cannot prove the rule reads `%aI` and ignores `%cI`; at
least one fixture case MUST set `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` to dates that
straddle the approval date in OPPOSITE directions (e.g. author date before the approval,
committer date after it, via a simulated rebase) and assert HR3 reports NO finding for that
case -- proving it read author date, not committer date.

**Target Platform**: the existing `retail check` CLI surface (cross-platform Python;
developed/verified on Windows per repo CLAUDE.md, no OS-specific behavior; git subprocess
calls already run through `gitutil.git_output`, which is Windows-safe today).

**Project Type**: single project -- an addition to the existing `src/retail/`
static-governance library plus its docs/tests, not a new service or app.

**Performance Goals**: N/A (a `retail check` rule reads a few dozen small committed YAML
files plus, for each cited evidence path, one `git log -1` subprocess call per run; no
measurable-scale requirement per the repo's existing rule set. If the per-path subprocess
cost becomes material at implement time, batching via a single `git log --name-only`
walk is an internal optimization, not a design change -- deferred to implement-stage
judgment, not decided here).

**Constraints**: fail CLOSED (ERROR-severity, non-zero `retail check` exit) on both stale
conditions (Principle I); NEVER write, modify, or append to `readiness-status.yaml` or any
other source artifact (FR-005; SCOPE GUARD); NEVER a numeric decay/staleness/confidence/
completeness score (hard rule #9; FR-012); NEVER use filesystem `mtime` as the change
signal, only git-commit history (FR-004, Principle IX); NEVER auto-clear, auto-populate, or
auto-write a `stale_review` entry -- the agent may draft `stage`/`evidence`/`note` but MUST
leave `reviewer` for a human to supply (FR-009, Principle V); ASCII, UTF-8 without BOM,
short repo-relative paths (Principle IX, Windows `MAX_PATH`).

**Scale/Scope**: exactly ONE new `@register`ed rule (HR3), exactly ONE new optional
top-level `readiness-status.yaml` key (`stale_review`), one new `gitutil.py` helper
function, and the six-surface wiring lockstep the existing meta-gate enforces for any new
rule (`__init__.py`, `EXPECTED_RULE_IDS`, the glossary rules-table row + "Currently N
rules" anchor, `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
`docs/quality/rule-count-claims.yaml`). Current live registered-rule count is **55** (per
`docs/quality/rule-count-claims.yaml` / `docs/rules/rules-manifest.json`) at the time this
plan was written; HR3 lands as the next integer in that sequence. This count is a
serialization point across ~19 parallel in-flight features (including HR1 / spec 087,
itself still design-stage) -- re-verify against the live manifest at implement time rather
than trusting any specific number recorded here.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | How this design satisfies it |
|---|---|---|
| **I. Agent-First, Gate-Enforced** | A rule fails CLOSED (blocks), never merely advises; compliance is demonstrable by running `retail check`. | HR3 is one `@register`ed rule in the same registry every other checker rule uses. Both stale conditions (FR-002 drift-triggered, FR-003 approval-lag) emit `Severity.ERROR`, a non-zero `retail check` exit -- there is no advisory/warn-only mode for either (FR-001). Running `retail check` on a table with either condition demonstrably fails; running it after a human resolves the condition (edits the stage, or records a shape-valid, correctly-dated `stale_review`) demonstrably passes. |
| **III. Medallion/Gold-Only** | `gold` IS a Kimball star (fact + CONFORMED dimensions); Power BI reads `gold` only; Postgres-first. | HR3 touches no data path at all -- it reads only committed `readiness-status.yaml` text and git commit-date metadata of tracked paths. It opens no Postgres connection and reads no Power BI/PBIP surface. It does not gate, define, or alter what gold IS; it gates whether a recorded `pass` about gold (or any other stage) is still trustworthy given a later drift or evidence edit. |
| **IV. Source-Mapping-Before-Silver** | No `silver.*` SQL before the source-map is reviewed+approved. | HR3 writes no SQL and does not gate `silver.*` authorship. It reads `mapping_ready`'s already-approved state as one of several approval-bearing stages it evaluates; it never re-opens or re-decides that approval's substance, only whether the evidence backing it has since moved. |
| **V. Agent-Stops-at-Judgment** | The agent MUST NOT decide grain/PII/business-policy/approval alone; it raises an unresolved-questions entry and STOPS. NEVER self-grant a readiness pass. | HR3 raises a finding and stops (FR-005); it never demotes a `pass` to `blocked` on disk, never clears its own finding, and never writes a `stale_review` entry without a human-supplied `reviewer` name (FR-009). The agent MAY draft the non-judgment fields (`stage`, `evidence`, `note`) of a candidate `stale_review` entry, exactly as User Story 3 / FR-009 describe, but the human decision (who reaffirms, and whether they in fact judge the stage still sound) is never made by the rule or the agent. The genuinely open governance question in the spec's Clarifications (does `stale_review` also clear a drift-triggered finding?) is left OPEN in this plan rather than defaulted -- see "Open item," below. |
| **VI. Defaults-Then-Deviations** | Start from existing rulings; record only deviations. | HR3 introduces no new cleaning/modeling default. The three mechanical behavior choices in the spec's Clarifications (same-day-is-not-stale; path-token extraction scoped to file-resolving tokens; latest-`approvals[]`-entry-wins) are reversible rule-behavior defaults, not Principle-V rulings, and are recorded as defaults in spec.md, not invented fresh here. |
| **VII. C086-is-an-example** | Generic templates carry no domain specifics. | The `stale_pass` finding shape, the `stale_review` entry shape, and the HR3 rule module contain no C086/pharmacy/retail-domain-specific column, dimension, or metric name. `data-model.md` documents the entities generically. The canary table (`retail_store_sales`) appears only in `research.md`'s input-source verification, never in the rule's own logic, docstrings, or the generic schema shapes. |
| **VIII. Static-First/Live-Deferred** | A live DB surface is deferred; author static structure + mark live PENDING. | HR3 is 100% static: it reads only `ctx.tracked_files` content and git commit-date history of already-tracked paths (via `subprocess` calls to the local git binary, the same class of read `git_meta.py`/`gitutil.py` already perform for other rules) -- no network, no database, no `retail drift` CLI (none exists; source-drift.md is design-only). `yaml` is imported LAZILY, matching the existing static-core discipline. No live re-profiling runtime is invoked or assumed. |
| **IX. Secrets/Reproducibility** | Never commit a real host/DSN/secret; ASCII, reproducible, Windows-safe. | HR3 touches no connection string or credential. It explicitly uses git-commit history (a reproducible, version-controlled signal, identical across clones) rather than filesystem `mtime` (FR-004) -- the core reproducibility requirement this principle names for exactly this kind of "when did this change" check. All new artifacts (rule module, `gitutil.py` addition, docs) are ASCII, UTF-8 without BOM, with short repo-relative paths (`src/retail/rules/rule_hr3.py`) well under the Windows `MAX_PATH` budget. |
| **Hard rule #9** | NO fabricated confidence/health/maturity score or completeness count. | HR3's `Finding` objects carry `rule_id`/`Severity`/`message`/`locator` only (the existing `Finding` dataclass, unchanged). No percentage, ratio, "N of M," or staleness/decay score is computed or emitted anywhere in the design (FR-012, SC-004). A `stale_review` entry likewise carries no score field -- only `stage`, `evidence`, `reviewer`, `at`, optional `note`. |

**Result**: PASS. No principle requires a documented violation; Complexity Tracking below
is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/089-readiness-decay-demotion/
├── spec.md              # Feature specification (input to this stage; already clarified)
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` directory: HR3 is a static file-reading rule with no network API/CLI
contract beyond the existing `Rule = Callable[[RuleContext], Iterable[Finding]]` shape
already defined in `src/retail/core.py` -- consistent with the RS1/SF1/AP1/HR1 precedent,
none of which added a `contracts/` directory either.

### Source Code (repository root)

This is the existing single-project `src/retail/` static-governance library. No new
project, service, or top-level directory is introduced. Concrete real paths this feature
adds or edits (implement-stage; recorded here so the plan does not miss a wiring surface
per FR-016):

```text
src/retail/
├── core.py                          # UNCHANGED -- Finding/RuleContext/Severity/is_test_path reused as-is
├── registry.py                      # UNCHANGED -- @register/all_rules() reused as-is
├── gitutil.py                       # EDIT: add git_last_commit_date(repo_root, path) -> str | None
│                                     #   ("git log -1 --format=%aI -- <path>", AUTHOR date (FR-004: not
│                                     #   committer date -- a rebase/cherry-pick can rewrite
│                                     #   committer date long after the content was actually
│                                     #   written), using the `--`
│                                     #   pathspec separator for the same option-injection
│                                     #   safety validate_commit_range already gives ranges;
│                                     #   returns None for a path with no commit history, which
│                                     #   HR3's FR-013 unresolvable-citation branch surfaces)
└── rules/
    ├── readiness_status.py          # UNCHANGED -- RS1 read-only design precedent, not edited by this feature
    └── rule_hr3.py                  # NEW -- the HR3 rule module (this feature's one new rule)

docs/
├── readiness/
│   └── source-drift.md              # REFERENCE ONLY, not edited -- HR3 consumes the
│                                     #   Downstream-invalidation rule (line 74) as already
│                                     #   written; this feature does not touch the drift
│                                     #   taxonomy or the doc's own text
├── quality/
│   └── rule-count-claims.yaml       # EDIT: bump claimed-count in lockstep with registration
├── rules/
│   ├── rules-manifest.json          # EDIT: add {"id": "HR3", "title": "..."} entry
│   └── severity-posture.json        # EDIT: add HR3 under the "registered" section
└── glossary.md                      # EDIT: add the HR3 row to the rules table + bump the
                                      #   "Currently N rules" anchor

templates/
└── readiness-status.yaml            # EDIT: confirmed present (the scaffold retail-onboard-table
                                      #   seeds a new table's instance from). Add a commented-out
                                      #   `stale_review: []` example block, additive only,
                                      #   so new tables see the shape without any existing
                                      #   filled instance needing migration (FR-006)

mappings/
└── */readiness-status.yaml           # UNCHANGED -- READ-ONLY input to HR3; no existing
                                      #   instance requires a stale_review entry to pass
                                      #   (absence of the key is valid, per FR-006)

tests/
├── unit/
│   ├── test_rules_wiring.py         # EDIT: add "HR3" to EXPECTED_RULE_IDS
│   ├── test_wiring_meta_gate.py     # UNCHANGED -- the wiring lockstep HR3 must satisfy
│   ├── test_gitutil.py              # EDIT (or NEW if it does not yet exist): unit tests
│   │                                 #   for git_last_commit_date against a controlled
│   │                                 #   throwaway fixture repo with fixed commit dates
│   └── test_rule_hr3.py             # NEW -- HR3 unit tests (mutation-verified fixtures,
│                                     #   per RS1/SF1/AP1/HR1 discipline)
└── fixtures/
    └── stale_pass/                   # NEW -- good/bad fixture corpus: drift + downstream
                                      #   pass (single and multi-stage), approval-lag stale
                                      #   with a resolving file evidence path, approval-lag
                                      #   clean (evidence predates or ties approval date),
                                      #   re-approval clears a prior approval-lag finding,
                                      #   valid stale_review clears an approval-lag finding,
                                      #   invalid-reviewer stale_review does not clear it and
                                      #   raises its own finding, stale_review dated before
                                      #   the triggering commit does not clear it, missing/
                                      #   malformed approvals[].at, unresolvable file-shaped
                                      #   evidence citation inside a real tracked directory
                                      #   (case (d): FR-013 fires), directory-shaped evidence
                                      #   token (case (b): prose, zero findings), a
                                      #   slash-bearing prose token whose parent path is NOT a
                                      #   real tracked directory -- e.g. a rule-id range like
                                      #   "D1-D8/C1/R1/G6" (case (c): prose, zero findings --
                                      #   the exact SC-006 near-miss this plan's research.md
                                      #   traced and fixed; pin it so it cannot regress), a
                                      #   formatted-decimal token (e.g. "1,552,071.00" ->
                                      #   "071.00") on a MECHANICAL stage (silver_ready/
                                      #   gold_ready: zero findings, both because it fails the
                                      #   step-2 candidate filter and because FR-013 is scoped
                                      #   away from mechanical stages entirely), mechanical
                                      #   stage with drift but no approvals[] concept, no
                                      #   readiness-status.yaml at all
```

**Structure Decision**: Single project, additive-only. This feature touches exactly the six
wiring surfaces the existing meta-gate enforces for any new `@register`ed rule, plus one new
rule module, one new `gitutil.py` helper (the one genuinely new mechanical capability this
feature requires beyond precedent), and its own new fixture corpus. It edits NO existing
rule module's logic (`readiness_status.py` is read-only reference, not edited), NO
`source-map.yaml`, and NO per-table `readiness-status.yaml` instance. The module is named
`rule_hr3.py` from the start (not a generic working name later renamed), matching the landed
`rule_sf1.py`/`rule_ap1.py` convention and the same convention HR1's own design-stage plan
(spec 087) already adopted for its reserved id.

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring justification: HR3
reuses the existing `Finding`/`RuleContext`/`@register` mechanism unchanged, adds exactly
one small, narrowly-scoped helper to `gitutil.py` (a `git log -1 --format=%aI -- <path>`
wrapper reading AUTHOR date per FR-004, the same subprocess pattern every existing
`gitutil.py` function already uses), and introduces no new project, service, dependency, or
architectural layer.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |

## Open item carried to implement-stage (Principle V -- not resolved here)

**Does a `stale_review` entry clear a drift-triggered (FR-002) finding, or only an
approval-lag (FR-003) finding?** The spec's Clarifications section records this as
explicitly OPEN ("OPEN owner ruling") rather than default-adopted. This plan implements
FR-007 exactly as currently worded -- `stale_review` clears FR-003 findings for the specific
(stage, evidence path) pair only. A drift-triggered FR-002 finding clears exclusively via a
human edit to `stages.source_ready.status` (re-confirming or demoting) or to the stale
downstream stage's own status; it is NOT clearable via `stale_review` under this plan. This
mirrors how spec 087's plan carried its own open Q-APPROVAL-SEAM question forward as a
recorded PENDING DEFAULT rather than silently deciding it. If the owner later rules that
`stale_review` should also cover drift-triggered findings, that is a scoped follow-up
touching FR-002/FR-007/User-Story-1/User-Story-3, not a reinterpretation of this plan.
