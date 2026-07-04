# Implementation Plan: Semi-Additive (Snapshot) Grain in the Metric Contract

**Branch**: `091-semi-additive-snapshot-grain` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/091-semi-additive-snapshot-grain/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Extend `templates/metric-contract.yaml` with one new, OPTIONAL top-level
scalar field, `time_additivity` (closed vocabulary `fully | semi | non`,
classifying a metric's additivity specifically over the DATE axis), and add
one new OFF-SPINE `retail check` rule, reserved id **HR5**, that ERRORs when
a contract already flagged by the existing, human-authored A10
ambiguities-ledger entry ("Inventory snapshot date") does not carry a valid,
non-`fully` `time_additivity` declaration. HR5 is cloned from the shipped
AL1 scaffold (`src/retail/rules/assumptions.py`): lazy `import yaml`, a
generic glob over `mappings/*/metrics/*.yaml`, template + test-path
exemption, fail-loud on unreadable, ERROR-only, never-resolves. The rule
transcribes an existing human-authored signal (the A10 entry) into a
required companion declaration; it never infers, defaults, or chooses the
value itself (Principle V). It stays narrowly distinct from the shipped AD1
lineage-composition rule (spec 068), which reads a different corpus
(define-layer prose) for a different, orthogonal question (composition
legality vs. date-axis additivity). The rule is wired into all five required
places so the wiring meta-gate and rule-count reconciler agree the count
advanced by exactly one.

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `retail check` core;
CI Python, local 3.12/3.13 also exercised in this repo).

**Primary Dependencies**: Python stdlib at module scope (`__future__`, `re`,
`typing`). `PyYAML` is imported LAZILY inside the rule function only,
matching AL1's `import yaml` placement -- no new third-party dependency is
introduced; PyYAML is already a repo dependency used by every YAML-reading
rule (AL1, AL2).

**Storage**: None. HR5 reads committed repository text
(`mappings/*/metrics/*.yaml`) and writes nothing at runtime. The template
edit (`templates/metric-contract.yaml`) is a one-time authored diff, not a
storage concern.

**Testing**: pytest, `@pytest.mark.unit`. New rule-behavior tests over
fixture YAML strings (mirroring `tests/unit/test_additivity_consistency.py`
and `tests/unit/test_assumptions.py`'s fixture pattern); the existing
`tests/unit/test_rules_wiring.py` extended with the new rule id in
`EXPECTED_RULE_IDS`.

**Target Platform**: CI static check (the `retail check` governance gate) +
local developer run. No runtime platform (no server, no scheduled job).

**Project Type**: Single project -- a library/CLI static linter addition
inside the existing `retail` Python package (`src/retail/rules/`).

**Performance Goals**: Not performance-sensitive. A bounded scan over a small
committed corpus (currently 5 contract files repo-wide). No goal beyond
"runs inside the existing `retail check` budget."

**Constraints**: Pure static YAML read only. MUST NOT execute DAX, open a
database/network connection, or render/evaluate a visual or PBIP surface
(never-execute invariant, FR-010). MUST NOT emit a numeric score, confidence
value, or threshold (hard rule #9, FR-009). MUST NOT infer, default, or
choose a `time_additivity` value on a contract's behalf (Principle V,
FR-002a/FR-004a/FR-006/FR-015). MUST stay generic -- no C086 /
retail_store_sales / pharmacy-specific value in the template comment or the
rule source (Principle VII, FR-016). MUST touch only the `time_additivity`
key on the shared template (collision avoidance vs. parallel adders 092,
103). All authored artifacts ASCII, UTF-8 without BOM, short repo-relative
paths (Principle IX, FR-017).

**Scale/Scope**: One template field addition + one new rule module + its
test file + the five wiring-point edits. Registered rule count advances by
exactly one (current authoritative count, per `docs/rules/rules-manifest.json`,
-> current + 1; this plan does not assert a literal number, per Constitution
Principle VIII's "this document does not restate a literal rule count"
posture).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. HR5 is a registered
  `retail check` rule; a violation is a non-zero exit / categorical ERROR
  finding, never a comment or advisory note. Compliance is demonstrable by
  running `retail check` over a fixture corpus (spec Independent Tests /
  Acceptance Scenarios). The agent does not decide pass/fail; the rule's
  return value and the checker's exit code do.

- **Principle III (Medallion, Gold-Only)**: PASS (not directly engaged, no
  violation surface). HR5 reads only `mappings/*/metrics/*.yaml` (per-table
  metric-contract copies, which themselves bind to `gold` per the existing
  `binds_to.gold_table` field, unchanged by this feature). HR5 opens no
  database connection and reads no bronze/silver/gold data directly.

- **Principle IV (Source Mapping Before Silver)**: N/A / PASS by
  non-engagement. This feature writes no `silver.*` SQL, does not touch the
  source-mapping gate artifacts (`source-profile.md`, `source-map.yaml`,
  `assumptions.md`, `unresolved-questions.md`, `reconciliation-report.md`),
  and does not reorder or bypass the mapping-before-silver sequence. It
  operates entirely at the metric-contract layer, which is already
  downstream of an approved source map for any table it touches.

- **Principle V (Agent Stops at Judgment Calls)**: PASS -- this is the
  principle this feature is most carefully bounded against. HR5 never
  decides a contract's `time_additivity` value; it only checks that a human
  who has already flagged the A10 snapshot trap has also supplied a
  declaration, and that the declaration is not `fully` and is in the closed
  vocabulary. The field itself is human-authored; the rule reads, never
  writes or infers (Key Entities, FR-015). FR-018/Clarifications Q4 (whether
  the detection trigger should ever widen beyond A10) is explicitly left
  `[NEEDS CLARIFICATION -- OPEN owner ruling]` in the spec and is NOT
  resolved, scoped-toward, or pre-built for in this plan -- it is a
  retail-kpi-knowledge ledger-scope decision this build cannot make on its
  own authority (see `open_principle_v`).

- **Principle VI (Defaults Then Deviations)**: PASS. The spec's
  Clarifications session adopted three constitution-safe DEFAULTS for
  mechanical parsing forks rather than inventing behavior: Q1 (exact,
  case-sensitive `A10` id match -- no near-miss fuzzing), Q2 (exact,
  case-sensitive, untrimmed vocabulary match -- no normalization), Q3/Q3b
  (null/empty/non-scalar collapse to defined, non-inferring buckets). Each
  default is recorded with its rationale in the spec, matching the
  Defaults-Then-Deviations discipline of recording what was adopted and why,
  and each is a DEFAULT this plan carries forward unchanged (a deviation
  would require a new triggering fact, and none is presented here). The one
  point NOT defaulted (Q4/FR-018) was correctly left OPEN rather than
  defaulted, because it is a Principle-V ledger-scope call, not a mechanical
  parsing fork.

- **Principle VII (C086 Is An Example, Not The Schema)**: PASS. The new
  template field comment cites `skills/retail-kpi-knowledge/knowledge/
  kpi-additivity-and-grain.md` and the worked-example doc directory
  generically; it does not inline any C086/retail_store_sales/pharmacy
  metric name, column, or grain key (FR-016, SC-007). HR5's source and
  docstring are equally generic.

- **Principle VIII (Static-First Governance, Live Deferred)**: PASS. HR5 is
  a pure static text reader: lazy `import yaml` inside the function keeps
  the rules-package import surface stdlib-only at module scope (matching
  AL1/AL2/AD1); no database, network, or `pbi-cli`/execution-adapter call
  exists anywhere in the design (FR-010). No live surface is introduced, so
  none needs a PENDING marker.

- **Principle IX (Secrets and Reproducibility)**: PASS. No credential, host,
  or DSN is introduced. All new/edited files are authored ASCII, UTF-8
  without BOM, using existing short repo-relative paths (FR-017).

- **Hard rule #9 (No Fabricated Confidence)**: PASS. HR5 emits categorical
  ERROR findings only -- no numeric score, health value, or completeness
  count anywhere in the finding message, the template field, or the
  wiring/manifest artifacts (FR-009, SC-006).

No deferred capability is assumed (research.md Section 3: no F016, no live
DB, no widened trigger, no DAX-generator extension). No principle violation
requires justification; **Complexity Tracking is empty** (see below).

## Project Structure

### Documentation (this feature)

```text
specs/091-semi-additive-snapshot-grain/
|-- spec.md               # Already authored + clarified (input to this plan)
|-- plan.md               # This file (/speckit-plan command output)
|-- research.md           # Phase 0 output (/speckit-plan command)
|-- data-model.md         # Phase 1 output (/speckit-plan command)
|-- quickstart.md         # Phase 1 output (/speckit-plan command)
`-- tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` subfolder is produced by this plan: the "contract" HR5 reads
is the existing, unchanged `ambiguities[]` block on the per-table metric
contract (a data shape, captured in data-model.md), not a new rule I/O
contract document. (068's plan added a `contracts/` folder for the rule I/O
shape; this feature's rule I/O is simple enough -- read committed YAML,
return categorical findings, per the AL1 precedent it clones directly -- that
data-model.md captures it without a separate document. No scope is lost by
omitting it.)

### Source Code (repository root)

**Structure Decision**: Single project (this repo's existing shape -- a
Python governance-checker package under `src/retail/`, no
frontend/backend/mobile split applies). This feature ADDS one rule module
and EDITS the shared template + the five wiring points; it creates no new
top-level directory.

```text
templates/
`-- metric-contract.yaml        # EDIT: add the new, OPTIONAL top-level
                                 #   `time_additivity` field (alongside
                                 #   `grain`/`readiness`), with a comment
                                 #   block matching the file's existing
                                 #   documentation style. Touches ONLY this
                                 #   one new key -- no rename/restructure of
                                 #   any existing field, no other new
                                 #   top-level key (collision avoidance vs.
                                 #   092/103, both in-flight on this same
                                 #   file).

src/retail/rules/
|-- snapshot_time_additivity.py # NEW rule module (HR5). @register("HR5", ...),
                                 #   cloned from assumptions.py's scaffold:
                                 #   lazy `import yaml`, the existing
                                 #   `mappings/*/metrics/*.ya?ml` glob (or an
                                 #   equivalent shared with AL1), template +
                                 #   test-path exemption, fail-loud-on-
                                 #   unreadable, ERROR-only, never-resolves.
|-- assumptions.py               # UNCHANGED -- AL1 clone source, read-only reference
|-- additivity_consistency.py    # UNCHANGED -- AD1, the neighbour this feature
                                 #   stays distinct from (different corpus,
                                 #   different question); not imported by HR5
|-- __init__.py                  # EDIT: add `snapshot_time_additivity` to the
                                 #   side-effecting import tuple and to `__all__`
                                 #   (alphabetical placement)
`-- ...                          # every other existing rule module unchanged

docs/rules/
|-- rules-manifest.json          # REGENERATE (`retail manifest`): adds the
                                 #   `{"id": "HR5", "title": "..."}` entry,
                                 #   alpha-sorted; authoritative count -> +1
`-- severity-posture.json        # REGENERATE + golden fixture: adds the
                                 #   `"HR5": [...]` entry under `"registered"`
                                 #   (expected `["<no-finding>"]` on the
                                 #   current corpus, matching AD1's shape,
                                 #   pending the actual regeneration run)

tests/unit/
|-- test_rules_wiring.py         # EDIT: add the literal `"HR5"` to
                                 #   `EXPECTED_RULE_IDS` (count derives from
                                 #   `len(...)`, never hardcoded)
`-- test_snapshot_time_additivity.py  # NEW: rule-behavior tests over fixture
                                 #   YAML strings, one per Acceptance
                                 #   Scenario / Edge Case in the spec
                                 #   (missing-field, fully-on-A10,
                                 #   semi/non-clears, out-of-vocab incl.
                                 #   non-scalar, null/empty-collapses-to-
                                 #   missing, no-A10-no-field-clean,
                                 #   no-A10-with-valid-field-clean,
                                 #   unreadable-file-fail-loud)
```

No file outside this list is required for the feature to ship, per FR-012's
explicit five wiring points plus the new module and its test (research.md
Section 1.5). Docs that merely MENTION AL1/AD1 in prose (glossary, roadmap,
scaffold generator, skill docs) are not required edits for this build.

## Phase 0 -- Research (research.md)

See `research.md` for the full precedent survey. Summary of what it
resolves, from committed artifacts only:

1. Confirms the exact AL1 scaffold to clone (signature, lazy import, glob,
   exemptions, fail-loud pattern, ERROR-only return).
2. Confirms AD1's distinct corpus and question, and that no cross-import or
   duplication is introduced.
3. Confirms the metric-contract template's current field order and
   documentation style, and the unchanged shape of the `ambiguities[]` block
   HR5 reads.
4. Confirms the A10 definition's exact source (`kpi-ambiguities.md` lines
   65-70) and that this feature only cites it.
5. Confirms the five wiring points and that the current committed corpus
   (5 contract files, zero A10 entries) gives a genuine SC-001 zero-findings
   baseline.
6. Confirms zero collision with the 092/103 parallel adders (`time_additivity`
   is unclaimed elsewhere in the working tree).
7. Records the deferred-capabilities-NOT-assumed list (no F016, no live DB,
   no widened trigger, no DAX-generator extension) and carries FR-018/Q4
   forward as OPEN, not resolved.

## Phase 1 -- Design (data-model.md, quickstart.md)

- **data-model.md**: the two artifact shapes this feature introduces/reads
  -- the `time_additivity` template field (new) and the HR5 finding
  (categorical, per the closed decision table) -- plus the full ERROR/CLEAN
  truth table over {A10 present/absent} x {field absent/null/empty/`fully`/
  `semi`/`non`/out-of-vocab/non-scalar} x {file readable/unreadable}. No new
  persisted schema beyond the one scalar field; the `ambiguities[]` shape is
  read, not modified.
- **quickstart.md**: how a developer/agent adds a `time_additivity`
  declaration to a real contract, how to author a fixture contract and run
  `retail check` to see HR5 fire and clear, and how to run the wiring test
  after registering the rule.

Re-check Constitution after design: unchanged from the initial gate above --
every principle still PASSes; the design adds one optional schema field
(human-authored) and one static reader (never infers, never executes, never
scores); FR-018/Q4 remains explicitly OPEN, not answered by this design.

## Complexity Tracking

*No entries.* The Constitution Check above records PASS (or N/A-by-
non-engagement, for Principle IV) for every relevant principle; no violation
requires justification.
