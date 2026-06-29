# Implementation Plan: Severity-Posture Regression Lock (golden severity table)

**Branch**: `044-045-severity-posture-lock` | **Date**: (date pending -- operator to fill) | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/044-severity-posture-lock/spec.md`

## Summary

Add a committed golden record of the severity posture each registered rule emits
(a JSON sibling of the existing `docs/rules/rules-manifest.json`), plus a
stdlib-only golden-equality snapshot test that compares the live OBSERVED posture
against the committed record and FAILS CLOSED on any drift. The record is OBSERVED
by forcing each rule to fire over planted synthetic fixtures -- it CANNOT be read
from the registry, because `RegisteredRule` carries no severity field and severity
is decided per-finding-branch (one shipped SQL rule emits both ERROR and WARNING).
This protects the Principle-I gate floor: a silent ERROR-to-WARNING downgrade on
any rule flips a failing build to passing, and today nothing catches it. Test-only:
adds NO new `@register` rule and NO new `EXPECTED_RULE_ID`, exactly like the
manifest-snapshot sibling (043). It advances no readiness stage.

**Load-bearing deferred ruling**: the record's GRAIN (rule_id -> set of classes,
vs per-branch, vs per-fixture-case) and the COVERAGE of the non-registry L3
severity surface are Principle-V human rulings recorded in spec `## Clarifications`
and intentionally UNRESOLVED. This plan is written to be CORRECT under any of the
grain options and treats grain/coverage as a parameter the implementer fills only
after the human ruling -- it does NOT pre-commit to one.

## Technical Context

**Language/Version**: Python 3.13 (repo interpreter); stdlib-only for this feature
(`json`, `pathlib`, `importlib`, `pkgutil`).

**Primary Dependencies**: NONE new. Reuses `retail.registry.all_rules()`,
`retail.core` (`Severity`, `Finding`, `RuleContext`, `is_test_path`), and the
existing `retail.cli` argparse seam. Test uses `pytest` (already in the repo).

**Storage**: A committed text artifact -- a JSON file under `docs/rules/`
(sibling of `rules-manifest.json`). No database.

**Testing**: `pytest` unit test, marked `@pytest.mark.unit`, mirroring
`tests/unit/test_rules_manifest_snapshot.py`.

**Target Platform**: CI + local dev on Windows (`core.autocrlf=true`) and Linux.
Must be cross-platform byte-stable.

**Project Type**: Single project (existing `src/retail` + `tests/unit`).

**Performance Goals**: N/A -- observes ~33 rules over tiny planted fixtures; runs
in well under a second.

**Constraints**: stdlib-only; no DB/network/Power BI/agent execution; UTF-8 no-BOM;
deterministic `\n`-terminated serialization with stable key + entry order;
data-structure (not raw-text) comparison so it cannot flake under autocrlf.

**Scale/Scope**: One observation helper, one golden JSON, one snapshot test, one
`.gitattributes` line, and (per clarify Q1) one generator path mirroring the
manifest generator. No more.

## Constitution Check

*GATE: Must pass before implementation. Re-checked after design below.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. The snapshot test fails
  closed on any severity drift (enforced, not advised). It directly protects the
  gate floor (exit 1 iff any ERROR). It adds NO new `EXPECTED_RULE_ID` and does
  not change `retail check` behavior -- it sits upstream of the gate as a guard.
- **Principle V (Agent Stops at Judgment Calls)**: PASS *by construction*. The
  grain and L3-coverage rulings are REFUSED and left in spec `## Clarifications`;
  this plan does not invent them. The implementer must obtain the human ruling
  before finalizing the record's key (see Implementation Notes).
- **Principle VII (C086 is an example)**: PASS. The record carries only generic
  rule ids and severity classes. The leakage vector is the planted fixtures used
  to trigger rules -- the plan mandates they be synthetic/minimal and never assert
  an example-domain table/column/value, and never bake an example specific into
  `docs/rules/`.
- **Principle VIII (Static-First Governance, Live Deferred)**: PASS. Observation
  forces rules to fire over planted TEXT fixtures; stdlib-only, CI-able, no DB,
  no network, no Power BI, no agent, no live model.
- **Principle IX (Secrets & Reproducibility / Windows-safe text)**: PASS *by
  construction* -- the load-bearing risk, identical to 043. The record is UTF-8
  no-BOM, stable key + entry order, `\n` endings, trailing newline; the test
  compares parsed data (not raw text); a `.gitattributes` entry pins the file to
  `text eol=lf`.
- **Hard rule #7 (generic only)**: PASS. rule ids + severity classes only.
- **Hard rule #8 (static-first hardening favored)**: PASS. A generated golden
  record + fail-closed test is exactly the low-risk static hardening favored.
- **Hard rule #9 (no fake confidence)**: PASS. The record is an EXACT observed
  posture (class equality), never a numeric confidence/health/readiness score.

No violations -> Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/044-severity-posture-lock/
|-- spec.md              # Stage 2 output (+ clarify edits)
|-- plan.md              # This file
|-- tasks.md             # Stage 4 output (/speckit-tasks)
|-- analysis.md          # Stage 5 output (/speckit-analyze) -- repo convention
|-- plan-review.md       # Stage 6 output (adversarial review)
`-- checklists/
    `-- requirements.md  # spec quality checklist
```

### Source Code (repository root)

```text
src/retail/
|-- severity_posture.py  # NEW: observe(all_rules()) -> posture data + serializer
|                        #      (mirrors manifest.py: build/serialize/render/write)
|-- registry.py          # UNCHANGED -- the rule source of truth
|-- core.py              # UNCHANGED -- Severity / Finding / RuleContext / is_test_path
|-- cli.py               # ADD a generator subcommand (per clarify Q1), mirroring manifest
`-- manifest.py          # UNCHANGED -- the sibling pattern this imitates

docs/rules/
|-- rules-manifest.json  # UNCHANGED -- the existing sibling golden artifact
`-- severity-posture.json # NEW generated golden record (committed)

tests/unit/
|-- test_severity_posture.py         # NEW golden-equality test (fails closed on drift)
|-- test_rules_manifest_snapshot.py  # UNCHANGED -- the proven clear+reload pattern to copy
`-- test_rules_wiring.py             # UNCHANGED -- existing id-set guard (no new id)

tests/fixtures/severity/   # NEW (if needed): synthetic minimal planted fixtures
                           # to force each rule to fire -- generic, no example domain

.gitattributes             # ADD: docs/rules/severity-posture.json text eol=lf
```

**Structure Decision**: Single-project layout. The observation logic lives in a
new `src/retail/severity_posture.py` that mirrors `manifest.py` (a `build_*`
function over `all_rules()`, a deterministic `serialize_*`, a `render_*`, a
`write_*`), and a generator subcommand is added to the existing `cli.py` argparse
seam (clarify Q1). The committed JSON is a sibling under the existing `docs/rules/`.

## Implementation Notes (seam, not over-build)

- **Observation helper** (`severity_posture.py`): a function that, for each
  registered rule, forces it to fire over a minimal synthetic `RuleContext` /
  planted fixture and collects the `Severity` class(es) of the findings it emits.
  Returns a deterministic data structure keyed per the GRAIN ruling (see below).
  A serializer writes UTF-8 no-BOM, `\n`, trailing newline, sorted by id + stable
  key order -- byte-identical to a re-run (SC-002).

- **GRAIN is a parameter, not a plan decision (Principle V)**: the record's key
  is the spec's REFUSED clarify question. The implementer MUST obtain the human
  ruling first, then encode exactly that grain. The plan stays correct under all
  three options: (a) `rule_id -> sorted set of classes`, (b)
  `(rule_id, branch/message-key) -> class`, (c) `(rule_id, fixture-case) -> class`.
  Whichever is chosen, the multi-class rule (S4b: ERROR + WARNING) MUST NOT be
  collapsed to a single class (FR-009 / Edge Cases).

- **L3 COVERAGE is a parameter, not a plan decision (Principle V)**: whether the
  record also covers the non-registry L3 governance surface (drift -> ERROR /
  escalate -> WARNING via `semantic.verdict_to_finding`) is the spec's REFUSED
  scope ruling. If the human rules it IN, the record gains a separate explicit
  section for that surface (observed by calling the mapping over both verdict
  statuses); if OUT, the record documents that exclusion explicitly so the gap is
  visible. The implementer does NOT add a `@register` to `semantic.py` either way
  (ADR-0007).

- **Forcing rules to fire vs the test-path exemption**: file-scanning rules skip
  paths under `tests/` via `is_test_path`. The observation harness must plant
  fixtures so the rule actually fires (e.g. construct a `RuleContext` whose
  tracked paths are NON-exempt synthetic paths, or invoke the rule against an
  in-memory/temp non-exempt path), while keeping the fixture content synthetic
  and generic. A rule that genuinely cannot be forced to fire gets an EXPLICIT
  no-finding marker entry (FR-011 / clarify Q3), never a silent omission.

- **Snapshot test** (`test_severity_posture.py`): copy the proven clear+reload
  pattern from `test_rules_manifest_snapshot.py` (clear `registry._RULES`,
  `importlib.reload` each `retail.rules.*` submodule) so it is order-proof; read
  the committed JSON as UTF-8, parse, and assert equality against the live
  observed posture data (FR-012, data comparison not raw text). On mismatch, emit
  an actionable message (drifted/missing/stale rule + observed-vs-recorded class
  + "regenerate and commit") (FR-003/FR-004). Add an idempotency test (SC-002)
  and a "no new registered rule" test mirroring the sibling (SC-004).

- **No deferred capability**: nothing here depends on the Power BI Execution
  Adapter (F016) or the spec-only runtimes (F031-F033). Pure static/test-only.

## Out of Scope (YAGNI)

- No new `@register` rule; no new `EXPECTED_RULE_ID`; no change to `retail check`
  behavior or exit-code logic.
- No `@register` added to `semantic.py` (L3 stays non-registered per ADR-0007),
  regardless of whether L3 is ruled in-scope for the record.
- No numeric severity score, no health/readiness/confidence number.
- No `--check` CI-verify subcommand mode for the first step (the snapshot test
  already enforces drift; add the seam, not the extra mode).
- No reordering/refactor of existing rules to make them "easier to observe".
- No DB/network/Power BI/agent integration.
- No resolution of the grain or L3-coverage rulings (human-only; spec
  `## Clarifications`).
