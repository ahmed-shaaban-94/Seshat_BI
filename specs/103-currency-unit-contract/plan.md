# Implementation Plan: Currency / Unit-of-Measure Contract

**Branch**: `103-currency-unit-contract` | **Date**: 2026-07-04 | **Spec**: `specs/103-currency-unit-contract/spec.md`

**Input**: Feature specification from `specs/103-currency-unit-contract/spec.md` (clarified 2026-07-04)

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Today `templates/source-map.yaml` records a source column's silver type,
missing-value policy, and PII flag, but nothing about the UNIT or CURRENCY
its numeric value is expressed in; `templates/metric-contract.yaml` records
which `gold` column(s) a summed measure reads, but nothing about what unit
that sum is supposed to be in. A metric that sums `weight_kg` and
`unit_count`, or sums a money column landed in EGP with one landed in USD,
produces a number that is arithmetically well-formed and silently WRONG, and
no `retail check` rule notices. This feature closes that gap in two additive
parts, mirroring the shape the closest in-flight sibling
(`specs/092-rls-access-readiness/`, HR6) already demonstrates for folding a
new input into the EXISTING Semantic Model Ready gate: (1) two new OPTIONAL
per-column keys on `templates/source-map.yaml`
(`columns[].unit`, `columns[].currency`) and one new OPTIONAL top-level key
on `templates/metric-contract.yaml` (`unit`, documentary only, no
`currency` counterpart), and (2) exactly one new static `retail check` rule,
reserved id **HR11**, that for every committed metric contract whose
`binds_to.columns[]` names two or more columns, resolves each bound column
against that table's `source-map.yaml` (join key: `columns[].rename_to`,
per Clarification Q4) and fails closed when the resolved `unit` or
`currency` values disagree, or when a bound column cannot be resolved.
HR11 folds into the EXISTING Semantic Model Ready gate the same way G6
already does -- an additional `retail check` finding that blocks the stage
via the existing exit-code path -- no new stage, no new subcommand, no
change to F010/`retail-semantic-check`'s own logic. The feature is
DECLARATION + SAME-UNIT/SAME-CURRENCY STATIC CHECK only: it never converts a
currency or a unit, never normalizes/aliases unit vocabulary, and leaves two
governance-policy questions (FR-013's detection scope, FR-014's undeclared-
value enforcement posture) explicitly open rather than defaulting them.

## Technical Context

**Language/Version**: Python 3.11+ (matches `src/retail/` existing rule
modules; no new language/runtime introduced).

**Primary Dependencies**: stdlib (`re`, `pathlib`, `dataclasses`) for the
rule's control flow, plus the ALREADY-APPROVED runtime dependency
`pyyaml>=6` for parsing both the source-map and metric-contract YAML,
imported LAZILY inside the rule function body (never at module scope),
mirroring `src/retail/rules/readiness_status.py` (RS1) and
`src/retail/rules/assumptions.py` (AL1). No new dependency is added to
`pyproject.toml`.

**Storage**: N/A at runtime (no database connection). The rule reads two
kinds of already-committed TEXT per table: (1)
`mappings/<table>/metrics/*.yaml` (the committed metric-contract store), and
(2) `mappings/<table>/source-map.yaml` (the committed mapping-gate
artifact), both via `ctx.tracked_files` / `Path.read_text()`. No new storage
location is introduced.

**Testing**: `pytest`, `@pytest.mark.unit` (matches the existing
`tests/unit/test_*.py` convention for rule modules, e.g.
`tests/unit/test_readiness_status.py`,
`tests/unit/test_additivity_consistency.py`). Coverage target unchanged from
repo norm (`pytest --cov=src --cov-report=term-missing`).

**Target Platform**: Same as the rest of `src/retail/` -- CI-able,
stdlib+pyyaml only, Windows-safe (ASCII / UTF-8-no-BOM per Principle IX), no
network, no DB driver import in this module's import path.

**Project Type**: Single project (existing `src/retail/` governance checker
+ `templates/` + `docs/` + `mappings/` repo layout). No new top-level
project.

**Performance Goals**: N/A (a static text-scan-and-cross-reference rule over
a handful of committed YAML files per `retail check` run; no different
performance profile than the existing AL1/G6/AD1 rules it is modeled on).

**Constraints**: MUST NOT convert or normalize a unit or currency value, and
MUST NOT compute, embed, or suggest a conversion rate/factor anywhere
(Scope Guard, FR-008, SC-003). MUST NOT add a `currency` key to
`templates/metric-contract.yaml`, and MUST NOT introduce any key name other
than `columns[].unit` / `columns[].currency` (source-map) and `unit`
(metric-contract) for this purpose (Scope Guard, collision-avoidance
allocation). MUST fail CLOSED (`Severity.ERROR`), never merely WARN --
Principle I. MUST NOT decide FR-013's detection-scope question or FR-014's
undeclared-value enforcement posture -- Principle V, both recorded as
explicit open questions. MUST NOT fabricate a confidence/health/maturity
score or an "N of M" completeness count anywhere -- hard rule #9, FR-015.

**Scale/Scope**: Two existing template files edited (additive keys only),
one new rule module (~1 new `retail check` rule id, HR11), a doc-listing
edit to one existing readiness doc (`semantic-model-ready.md`), and the
corresponding unit tests + rules-manifest regeneration. No change to any
other rule, stage, or skill's own source, and no change to
`templates/kpi-pack.yaml` or the `ambiguities[]` ledger.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design below.*

| Principle | How this design satisfies it |
|---|---|
| **I. Agent-First, Gate-Enforced** | HR11 is a registered `retail check` rule (`@register("HR11", ...)`) returning `Finding(severity=Severity.ERROR, ...)` for every unit/currency clash or unresolved column -- a non-zero process exit, not advisory prose. Compliance is demonstrable by running `retail check` (spec Independent Tests for US1/US2/US3 are literally "run `retail check`, inspect the findings"). The agent never marks HR11 passing itself; the checker's exit code is the sole authority (mirrors G6/AL1/AD1). |
| **III. Medallion, Gold-Only** | HR11 reads `binds_to.columns[]`, which per F009's own template MUST already name `gold` columns (Principle III is enforced upstream, at contract-authoring time, not re-litigated here). This feature adds no new gold-reading surface and does not touch `binds_to.gold_table`; it only adds the unit/currency AGREEMENT check among already-gold-bound columns. |
| **IV. Source-Mapping-Before-Silver** | Directly engaged, unlike 092/HR6 (which operates purely at Stage 5): the two new source-map keys (`columns[].unit`, `columns[].currency`) are recorded at MAPPING time (Stage 2), inside the existing `columns[]` block the mapping gate already reviews. They are additive and OPTIONAL -- no existing mapping-gate field, review step, or approval requirement changes, and no `silver.*` SQL is authored, edited, or implied by this plan. A table's Mapping Ready status is unaffected by whether these two fields are filled. |
| **V. Agent-Stops-at-Judgment** | The feature explicitly does NOT decide WHAT unit or currency a column should be declared as (FR-020) -- the analyst who fills the source-map decides from the profiled data; the agent's role is limited to recording the human-supplied declaration and running the static comparison. FR-013 (detection-scope) and FR-014 (undeclared-value enforcement posture) are both carried forward UNRESOLVED into this plan -- see "Two open questions carried forward" below. The rule's own source MUST NOT encode a settled answer to either. |
| **VI. Defaults-Then-Deviations** | The metric-level `unit` field's scope (Q3: documentary only, never cross-checked against bound columns) and the bound-column resolution key (Q4: join on `columns[].rename_to`) are both already-ratified, reversible, constitution-safe defaults recorded in the spec's Clarifications -- this plan does not re-litigate them, only implements them (research P6). |
| **VII. C086-is-an-example** | Both template edits add only placeholder-shaped OPTIONAL fields (e.g. `unit: null  # e.g. "kg", "each"`) -- no `retail_store_sales`-specific unit label, currency code, or column name is inlined into either template or into the HR11 rule's own source/messages (FR-016). A filled instance (e.g. `mappings/retail_store_sales/source-map.yaml` gaining declared units) may be cited under `docs/worked-examples/` later, never baked into the generic artifact. |
| **VIII. Static-First/Live-Deferred** | HR11 reads only already-committed text (`mappings/<table>/metrics/*.yaml` + `mappings/<table>/source-map.yaml`) -- no live PBIP, no live database, no sampling of real column values (FR-009, FR-019). A live check that a materialized column's ACTUAL values match its declared unit/currency is explicitly deferred to a future `retail validate` extension and is not stubbed or TODO'd into this feature's module -- it simply is not written. |
| **IX. Secrets/Reproducibility** | No host/DSN/secret is introduced by this feature. The template edits and rule source are ASCII, UTF-8 without BOM (`--`/`->`, no glyphs), and no new path this feature adds exceeds the Windows 260-char budget (FR-017). |
| **Hard rule #9 (no fabricated score)** | Both new template fields and every HR11 `Finding.message` use only the four explicit statuses / a pass-fail finding -- no numeric confidence/health/maturity score or completeness count anywhere (FR-015, SC-005). |
| **F016 boundary** | This design assumes F016 (Power BI execution adapter) does NOT exist. HR11 never opens a PBIP file, never evaluates a DAX measure, never connects to the Power BI service. That remains F016's later, execution-only concern (Principle II), gated on Semantic Model Ready being `pass` -- unaffected by this feature. |

**Two open questions carried forward -- explicitly NOT decided here.**

1. **FR-013 (detection scope).** This plan fixes only that HR11 acts on
   metric contracts whose `binds_to.columns[]` lists two or more columns
   AND that are determined (by a rule left to `tasks.md`/implementation) to
   represent a same-unit-relevant sum. It does NOT fix that determination
   rule here: neither "only when `definition.aggregation: sum`" nor "any
   2+-column bind, `definition` or not" is adopted, because each has a
   named failure mode the spec already identifies (the former silently
   exempts the common no-`definition` case and reopens the exact gap this
   feature exists to close; the latter false-positives on a legitimate
   ratio `[numerator, denominator]` pair, which User Story 2 rules out).
   **Non-negotiable constraint carried into `tasks.md`: no version of this
   feature may ship code that silently adopts either extreme as if it were
   already settled by this plan.**
2. **FR-014 (undeclared-value enforcement posture).** This plan fixes only
   that HR11 compares DECLARED, non-null unit/currency values when both
   sides declare one (FR-005/FR-006, literal). It does NOT fix what happens
   when one side is undeclared (null/absent) -- block, warn, or silent
   no-op is an explicit Principle-V/VI owner ruling, not an implementation
   detail this plan or `tasks.md` may default. **Non-negotiable constraint:
   no version of this feature may ship code that treats an undeclared-vs-
   declared pairing as a settled "matches" or "blocks" outcome without a
   recorded owner ruling.** (Q2a, the internal-consistency flag between
   User Story 3 Acceptance Scenario 3 and FR-006's literal wording, stays
   unresolved for the same reason -- FR-006 as written governs until FR-014
   is ruled.)

**Result**: PASS. No principle is violated; no Complexity Tracking entry is
required (see below).

## Project Structure

### Documentation (this feature)

```text
specs/103-currency-unit-contract/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` subfolder is needed: this feature's "contract" artifacts ARE
the two edited top-level templates themselves (documented in
`data-model.md`), not a new API/service contract.

### Source Code (repository root)

This is a **single-project** structure (the existing `src/retail/`
governance checker + `templates/` + `docs/` + `mappings/` repo layout) -- no
frontend/backend split, no mobile target. Concrete real paths this feature
ADDS or EDITS (all repo-relative to the worktree root):

```text
templates/
├── source-map.yaml                 # EDIT. Adds columns[].unit and
│                                    # columns[].currency, two new OPTIONAL
│                                    # per-column keys (FR-001). No other
│                                    # key in this file changes.
└── metric-contract.yaml            # EDIT. Adds exactly one new OPTIONAL
                                     # top-level key, unit, sibling to grain
                                     # and binds_to (FR-002). No currency
                                     # key is added here (Scope Guard). No
                                     # other key in this file changes.

src/retail/rules/
└── hr11.py                         # NEW. The HR11 static rule module.
                                     # Sibling of g6.py/assumptions.py (AL1):
                                     # @register("HR11", ...), pure function
                                     # RuleContext -> Iterable[Finding],
                                     # Severity.ERROR on every violation
                                     # (fail-closed, Principle I). Lazy
                                     # `import yaml` inside the function body
                                     # only (mirrors readiness_status.py /
                                     # RS1 and assumptions.py / AL1). Resolves
                                     # each metric contract's bound columns
                                     # against that table's source-map.yaml
                                     # (join key: columns[].rename_to, per
                                     # Clarification Q4) -- the cross-file
                                     # join shape mirrors HR6's contract<->SQL
                                     # join (specs/092-rls-access-readiness),
                                     # applied here to contract<->source-map.
                                     # The FR-013 detection-scope rule and the
                                     # FR-014 undeclared-value posture are
                                     # implemented here ONLY once resolved by
                                     # tasks.md/an owner ruling -- this plan
                                     # does not pre-select either.

docs/readiness/
└── semantic-model-ready.md          # EDIT. Add HR11 to the existing
                                     # "Required checks" and "Blocking
                                     # reasons" tables (FR-018) -- doc-
                                     # listing only, no narrative rewrite of
                                     # the stage's meaning.

docs/rules/
└── rules-manifest.json              # REGENERATE (via `retail manifest`)
                                     # after HR11 registers -- the registry
                                     # snapshot test (Principle VIII: "the
                                     # authoritative, always-current rule
                                     # inventory") fails closed on a stale
                                     # manifest, so this regeneration is a
                                     # required implementation step, not
                                     # optional cleanup.

tests/unit/
└── test_hr11.py                     # NEW. Unit tests for HR11: clashing
                                     # unit, clashing currency, both clashing,
                                     # neither clashing (clean pass-through),
                                     # single-bound-column no-op (FR-011),
                                     # unresolvable bound column (FR-010),
                                     # missing/unreadable source-map.yaml
                                     # (FR-010), and a finding-text assertion
                                     # that no conversion rate/factor/
                                     # converted value ever appears (SC-003)
                                     # (mirrors the style of
                                     # tests/unit/test_readiness_status.py and
                                     # tests/unit/test_additivity_consistency.py).
                                     # FR-013/FR-014-dependent cases are NOT
                                     # authored here until those two open
                                     # questions are ruled -- authoring a test
                                     # that assumes an answer would itself be
                                     # deciding the judgment call in code.

mappings/<table>/
├── source-map.yaml                  # EXISTING FILE, no new file. A table's
│                                     # own source-map.yaml gains filled
│                                     # columns[].unit / columns[].currency
│                                     # values ONLY when its analyst chooses
│                                     # to declare them (optional; retroactive
│                                     # filling on existing mappings is not
│                                     # required by this feature, per FR-014
│                                     # staying open).
└── metrics/<MetricName>.yaml        # EXISTING FILE, no new file. A metric
                                      # contract gains a filled top-level
                                      # unit value ONLY when its owner
                                      # chooses to declare one (optional).
```

**Structure Decision**: Single project, additive-only. This feature edits
two already-shipped templates in place (adding optional fields only), adds
one new rule module, one new test module, one doc-listing edit, and one
regenerated manifest -- no restructuring of `src/retail/`, no new top-level
directory, no new template file, no change to any existing rule's
registration or behavior, and no change to `templates/kpi-pack.yaml` or the
`ambiguities[]` ledger.

## Complexity Tracking

*No entry required.* The Constitution Check above found no principle
violation needing justification: the design adds two additive template
fields plus one rule module, following two already-shipped precedents
(F009's contract shape / AL1's contract-only read, and HR6's cross-file join
shape) rather than introducing a new pattern, a new dependency, a new stage,
or a new subcommand. The two items left explicitly open (FR-013, FR-014) are
Principle-V/VI judgment calls the spec itself routes to implementation
planning or an owner ruling, not unresolved complexity in this design.
