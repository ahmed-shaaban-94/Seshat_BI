# Implementation Plan: Additivity-Consistency Lineage Rule

**Branch**: `067-additivity-consistency-rule` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/067-additivity-consistency-rule/spec.md`

## Summary

Add one new OFF-SPINE retail-check rule module that statically cross-reads committed
define-layer additivity classifications and derivation-lineage edges and ERRORs on an
illegal additivity composition, per a small closed generic legality table. Clone the
shipped assumption-ledger rule (AL1) scaffold. Emit categorical ERROR/pass only. Never
execute. Never resolve. Wire the rule into the five required places so the count advances
by exactly one.

## Technical Context

**Language/Version**: Python 3.11+ (repo runs the retail check on CI Python; local 3.12/3.13)

**Primary Dependencies**: Python stdlib at module scope; a YAML/markdown-prose parser
imported lazily INSIDE the rule function only (retail-check core stays stdlib-only at
import time, matching AL1's lazy `import yaml`). No new third-party dependency is added.

**Storage**: None. Reads committed repository text files (define-layer markdown contracts,
the rendered lineage document). Writes nothing at runtime.

**Testing**: pytest, unit-marked. New rule-behavior tests over fixtures; the existing
rule-wiring unit test extended with the new rule id.

**Target Platform**: CI static check (the retail governance check) + local dev.

**Project Type**: Single project -- a library/CLI static linter (the retail rules package).

**Performance Goals**: Not performance-sensitive; a bounded scan over a small committed
corpus. No goal beyond "runs in the existing check budget."

**Constraints**: Pure static text read. MUST NOT run DAX, open a connection, or render a
visual (never-execute invariant). MUST NOT emit any numeric score/confidence/threshold.
MUST NOT infer or re-classify a metric (Principle V). MUST stay generic (no worked-example
metric names, ids, or paths). ASCII/UTF-8-no-BOM in every authored artifact.

**Scale/Scope**: One new rule module + its tests + the five wiring updates. Rule count
advances by exactly one (current authoritative count -> current + 1).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. The rule is a gate-style static
  check that advances no readiness stage and grants no approval; it only returns findings
  via the exit code.
- **Principle III (Gold-Only)**: PASS. Reads only committed define-layer artifacts; no
  raw/staging data touched.
- **Principle V (Agent Stops at Judgment Calls)**: PASS. The rule only SURFACES; it never
  picks a winner, invents an edge, or re-classifies. Two owner rulings (FR-011 identity,
  FR-012 legality-set ratification) are left OPEN for a human, not answered.
- **Principle VII / rule #7 (C086 Is An Example, Not The Schema)**: PASS. Generic glob;
  closed table drawn from generic knowledge; no worked-example names/ids/paths baked in.
- **Principle VIII / rule #8 (Static-First Governance) + never-execute (B1/B3)**: PASS.
  Pure static text read; lazy parser import keeps the core stdlib-only; no DAX/connection/
  visual.
- **Rule #9 (No Fake Confidence)**: PASS. Categorical ERROR/pass only; no score/band.
- **Rule #IX (ASCII/UTF-8-no-BOM)**: PASS. All authored artifacts use ASCII with `--`/`->`.

No deferred capability is assumed (no Power BI execution adapter, no spec-only runtime, no
live DB). No violation requires a complexity-tracking entry.

## Project Structure

### Documentation (this feature)

```text
specs/067-additivity-consistency-rule/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (rule I/O contract, not a metric contract)
├── checklists/
│   └── requirements.md  # From /speckit-specify
├── spec.md
├── analysis.md          # From /speckit-analyze
├── plan-review.md       # From the adversarial plan-review step
└── tasks.md             # From /speckit-tasks
```

### Source Code (repository root)

```text
src/retail/rules/
├── additivity_consistency.py   # NEW rule module (@register, cloned from assumptions.py)
├── assumptions.py              # AL1 -- clone target (unchanged)
├── __init__.py                 # EDIT: add module to import block + __all__
└── ...                         # (other existing rule modules unchanged)

docs/rules/
└── rules-manifest.json         # REGENERATE (authoritative count -> +1)

tests/unit/
├── test_rules_wiring.py        # EDIT: add new rule id to EXPECTED_RULE_IDS
└── test_additivity_consistency.py  # NEW rule-behavior tests over fixtures

<severity-posture manifest/golden fixture>   # REGENERATE (per the 5-place checklist)
```

## Phase 0 -- Research (research.md)

Resolve, from committed artifacts only:

1. Confirm the AL1 scaffold specifics to clone: `@register` signature, lazy parser import,
   generic contract glob regex, template-path + test-path exemption, fail-loud-on-
   unreadable pattern, ERROR-only return.
2. Confirm the READ corpus decided in Clarifications Q2: the define-layer prose contracts
   (additivity heading + derives-from heading) and the rendered lineage document; confirm
   the closed additivity vocabulary is exactly the three committed words.
3. Confirm the generic settled facts that seed the closed legality table live in the
   committed knowledge layer (ratio never summed; carry base and recompute; semi-additive
   must not be naively summed).
4. Confirm the five wiring points and the current authoritative rule count so the target
   count is "current + 1".

## Phase 1 -- Design (data-model.md, contracts/, quickstart.md)

- **data-model.md**: the in-memory shapes the rule builds -- a classification record
  (metric identity -> one of the three closed classes, or absent/ambiguous), a derivation
  edge (child -> parents), and the closed legality table (parent-class x child-class x
  composition-kind -> legal/illegal). No new persisted schema; no new contract field.
- **contracts/**: the rule's I/O contract (inputs = committed text corpus; output =
  iterable of categorical ERROR findings; invariants: never mutates, never executes, never
  infers, ERROR-only). This is a rule contract, NOT a metric contract.
- **quickstart.md**: how to run the retail check to see the rule fire and pass; how to add
  a fixture and assert exactly-one / zero findings.

Re-check Constitution after design: unchanged -- all gates still PASS; the design adds a
static reader + a fixed closed table, no executor, no score, no owner ruling.

## Scope discipline (YAGNI)

- Build the SEAM, not more: one rule that reads the define-layer prose corpus and enforces
  the closed table. Do NOT build a structured `additivity`/`derives_from` contract field
  (a separate, larger define-layer change explicitly out of scope).
- Do NOT build the cross-corpus id join (FR-011 is OPEN); the rule reads a single corpus.
- Do NOT build an ambiguity-ledger check half; this rule is standalone.
- Do NOT assume any deferred runtime/adapter exists.

## Complexity Tracking

No constitution gate is violated; no entries.
