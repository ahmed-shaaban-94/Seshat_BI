# Implementation Plan: Source Data-Contract -- Forward Schema + Arrival + Restatement Policy

**Branch**: `105-source-data-contract-restatement` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/105-source-data-contract-restatement/spec.md`

## Summary

Add one new Source-Ready static `retail check` rule, reserved id **HR12**, that
verifies a table's OPT-IN forward source data-contract
(`mappings/<table>/source-data-contract.yaml`, instantiated from a NEW generic
template `templates/source-data-contract.yaml`) is PRESENT and STRUCTURALLY
WELL-FORMED -- every required section (expected column-level `schema`, an
`arrival` cadence, and a `restatement` policy) carries a non-placeholder value --
whenever that file exists for a table. The contract's absence is never penalized
(FR-002, mirrors 090/HR4 and 093/HR7's own "declare or default" posture); its
presence-but-incomplete state fails CLOSED, naming the specific incomplete section,
via a purely structural sentinel-token comparison (FR-006) rather than any semantic
judgment on the filled value (Principle V). A present file that fails to parse as
YAML at all is treated as a malformed case too, mirrored on the shipped SF1
precedent (`except (OSError, yaml.YAMLError)`): HR12 fails closed naming the FILE
itself, never an unhandled exception and never a silent not-applicable skip (spec
Clarifications Q6, FR-002). HR12 is static-only: it reads
`mappings/<table>/source-data-contract.yaml` (and its own template, for exclusion)
via `ctx.tracked_files`, never opens a database connection, never computes a live
`MAX(<date column>)`, and never detects an actual restatement event on live data
(Principle VIII) -- that live half is explicitly deferred to a future `retail
validate` extension. HR12 reads and writes nothing in `source-map.yaml` (090/HR4's
`meta.freshness` key stays untouched) and never reads `readiness-status.yaml` or
raises a `stale_pass` blocker (089/HR3's concern) -- the collision-avoidance
allocation keeps this a genuinely separate file and a genuinely separate rule. One
Principle-V question -- whether a present-but-broken contract should be wired into
a table's Source Ready `blocking_reasons[]` once opted in, or stay pure evidence
(FR-013) -- is recorded OPEN with a named, non-authoritative interim default
(evidence-only, never self-wired into a stage verdict); this feature does not
resolve it.

## Technical Context

**Language/Version**: Python 3.11+ (repo runs the retail check on CI Python; local
3.12/3.13).

**Primary Dependencies**: Python stdlib only at `retail.rules` PACKAGE import time
(Principle I/VIII wording). HR12's own module does a LAZY `import yaml` INSIDE its
handler function, mirroring the shipped AL2 (`assumption_coherence.py`) precedent
exactly -- the shared rules package import block stays stdlib-only; `yaml` (already
a repo dependency, used by AL2 and the mapping-gate template readers) is imported
only when HR12's handler actually runs.

**Storage**: None. Reads committed repository text (YAML) files only via
`ctx.tracked_files`. Writes nothing at runtime.

**Testing**: pytest, unit-marked. New rule-behavior tests over fixtures (a
fully-filled contract fixture -> zero Findings; a contract with the restatement
section left as the sentinel placeholder -> exactly one Finding naming
`restatement`; a contract with a blank/missing `arrival` field -> one Finding
naming `arrival`; a contract with an empty `schema` list -> one Finding naming
`schema`; a contract with a schema entry that has a `name` but no `type` -> one
Finding naming `schema` (spec Q3); a contract file present but not valid YAML at
all (a parse error) -> exactly one Finding naming the FILE itself, not a section,
and no unhandled exception raised (spec Q6, FR-002, mirrors the shipped SF1
`except (OSError, yaml.YAMLError)` precedent); a table with no contract file at
all -> zero Findings, not-applicable). The existing wiring/lockstep tests
(`test_rules_wiring.py`, `test_wiring_meta_gate.py`, `test_glossary_rule_table.py`)
extended with the new rule id, per the seven-surface wiring checklist in
research.md. No fixture is authored as a real table's committed contract (Principle
V, research.md "Landing analysis") -- all User Story 1-3 coverage lives under a
test-fixture root recognized by `is_test_path()`.

**Target Platform**: CI static check (the retail governance check, `retail check`)
+ local dev.

**Project Type**: Single project -- a library/CLI static linter (the retail rules
package). No frontend/backend split; no live surface.

**Performance Goals**: Not performance-sensitive; a bounded scan over the committed
`mappings/*/source-data-contract.yaml` corpus (currently zero files -- see
research.md's input-source confirmation). No goal beyond "runs in the existing
`retail check` budget."

**Constraints**: Pure static YAML read (Principle VIII). MUST NOT open a database
connection, compute a live `MAX(<date column>)`, or detect a live restatement event
(FR-003, scope guard). MUST NOT read or write `source-map.yaml` or `meta.freshness`
(FR-004, collision-avoidance allocation). MUST NOT read `readiness-status.yaml` or
raise a `stale_pass` blocker (FR-004). MUST NOT invent, infer, or default a table's
actual schema/cadence/restatement VALUES (FR-005, Principle V) -- the agent authors
only the generic template and the presence/well-formedness check. MUST NOT emit any
numeric confidence/health/maturity score or an "N of M" completeness count (hard
rule #9, FR-009). MUST NOT add a new readiness stage or change the Mapping Ready
gate's required five-artifact list (FR-010). MUST stay generic -- no worked-example
(C086/retail_store_sales) schema, cadence, or restatement specifics inlined into the
template or into HR12's fixed messages (Principle VII, FR-007). ASCII/UTF-8-no-BOM
in every authored artifact, short repo-relative paths (Principle IX, FR-011).

**Scale/Scope**: One new rule module + its tests + the seven wiring-surface updates
+ one new generic template (`templates/source-data-contract.yaml`) + one
`docs/readiness/source-ready.md` doc edit. No new readiness stage; no new top-level
directory (the per-table contract lives at the existing
`mappings/<table>/` path). Rule count advances by exactly one (current
authoritative count, read live at build time, plus one -- 55 at research time, but
the build must re-read the live count rather than hardcode it, since 089/090/093
are parallel same-batch drafts also contending for a next id).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. HR12 fails CLOSED with a
  Finding on a present-but-incomplete or placeholder-only contract (FR-006, User
  Story 2) -- it never silently treats a half-filled contract as good enough or
  silently skips the check when the file exists. Compliance is demonstrable by
  running `retail check` (Finding list for that table's contract path). The
  separate question of whether that Finding also blocks the Source Ready STAGE
  verdict (FR-013) is recorded open (see Principle V below) without weakening HR12's
  own fail-closed behavior as a check.
- **Principle III (Medallion/Gold-Only)**: PASS (non-interaction). HR12 reads only
  `mappings/<table>/source-data-contract.yaml`; it touches no bronze/silver/gold
  data, opens no Power BI surface, and does not alter the gold Kimball star shape
  that S6/S7/S8 already enforce.
- **Principle IV (Source-Mapping-Before-Silver)**: PASS (non-interaction). HR12 is a
  Source-Ready (Stage 1) check that runs strictly BEFORE any mapping-gate review or
  silver SQL exists; it adds no new silver SQL, does not read or relax the mapping
  gate's approval state, and does not touch `source-map.yaml` at all (collision-
  avoidance allocation, FR-004). It does not add a sixth artifact to the Mapping
  Ready gate's required list (FR-010).
- **Principle V (Agent-Stops-at-Judgment)**: PASS. HR12 itself never decides a
  table's actual schema, arrival cadence, or restatement policy -- these are
  owner-supplied facts about a real upstream system (FR-005); the agent's role is
  limited to authoring the generic template and the presence/well-formedness check.
  HR12 never grants a Source Ready `pass` and never judges whether a filled,
  non-placeholder value is a "good" answer (FR-006's structural-only test). The one
  live judgment call this feature surfaces (FR-013, Q-ENFORCEMENT-STRENGTH: whether
  an opted-in, later-broken contract should block the Source Ready stage verdict) is
  recorded as an OPEN Clarifications entry with a named, non-authoritative interim
  default (evidence-only; HR12's Finding is never self-wired into any table's
  `blocking_reasons[]`) that a governance owner may ratify via the approval-console
  workflow; the agent does not answer it unilaterally.
- **Principle VI (Defaults-Then-Deviations)**: PASS. A table with no
  `source-data-contract.yaml` incurs zero new burden (FR-002); every table mapped
  today (`retail_store_sales`, `demo_sample_orders`) passes HR12 as not-applicable
  with no edit required (SC-003, research.md's confirmed zero-contract landing).
  Only a table that OPTS IN by creating the file, and then leaves a section
  incomplete, must fix anything.
- **Principle VII (C086-Is-An-Example-Not-The-Schema)**: PASS. The template and
  HR12's fixed Finding messages bake in no specific table/column name, cadence
  wording, or restatement specifics (FR-007); the worked example may appear only as
  a cited FILLED instance under `mappings/<table>/` in illustrative documentation
  (e.g. quickstart.md), never as an authoritative part of the template or rule
  logic, and this feature does not author a real filled instance for
  `retail_store_sales` or `demo_sample_orders` (research.md's Principle-V landing
  note -- inventing those facts would itself violate Principle V/FR-005).
- **Principle VIII (Static-First/Live-Deferred)**: PASS. HR12 is 100% static: it
  reads only committed files via `ctx.tracked_files`, never connects to a database,
  never computes a live `MAX(<date column>)`, and never detects an actual
  restatement event on live data (FR-003, SC-004). Live enforcement of this contract
  is explicitly deferred to a future `retail validate` extension, which this feature
  does not name or design.
- **Principle IX (Secrets/Reproducibility)**: PASS. No host/DSN/secret is read or
  written by HR12 or its declaration artifacts. All authored artifacts (rule module,
  template, doc updates) are ASCII, UTF-8 without BOM, using short repo-relative
  paths well inside the Windows 260-char budget (FR-011). HR12 reads
  `mappings/<table>/source-data-contract.yaml` only via `ctx.tracked_files`
  membership, never the raw working tree, so an untracked local copy cannot
  influence the gate (reproducibility).
- **Hard rule #9 (No Fabricated Confidence)**: PASS. HR12's only outcomes are "no
  Finding" (pass-eligible / not-applicable) or a Finding naming the specific
  incomplete section(s) (FR-009); no numeric score, health/maturity band, or "N of
  M" completeness tally is ever emitted (SC-005).
- **F016 (Power BI execution adapter)**: N/A / not assumed to exist. HR12 never
  invokes it, directly or indirectly.

No deferred capability is assumed (no Power BI execution adapter, no live DB, no
new readiness stage). No principle is violated; **no Complexity Tracking entries are
required.**

## Project Structure

### Documentation (this feature)

```text
specs/105-source-data-contract-restatement/
|-- plan.md              # This file
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
|-- spec.md              # Already authored + clarified (input to this stage)
`-- tasks.md             # Phase 2 output (/speckit-tasks -- NOT produced by this stage)
```

### Source Code (repository root)

```text
templates/
`-- source-data-contract.yaml   # NEW generic template (FR-001): schema[], arrival,
                                 #   restatement sections, each required field
                                 #   pre-filled with a distinctive sentinel token
                                 #   (FR-006/spec Q2). No worked-example specifics
                                 #   (Principle VII).

mappings/
`-- <table>/
    `-- source-data-contract.yaml   # NOT created by this feature for any real
                                     #   table (Principle V; research.md landing
                                     #   analysis). Shape documented here for the
                                     #   first analyst who fills one.

src/retail/rules/
|-- source_data_contract.py     # NEW rule module (@register("HR12", ...)); lazy
|                                #   `import yaml` inside the handler (AL2 precedent)
|-- assumption_coherence.py     # UNCHANGED -- HR12 mirrors AL2's read-path shape
|                                #   (compiled path regex, _TEMPLATE_PATH exclusion,
|                                #   is_test_path exclusion, lazy yaml import) but
|                                #   does not import from or edit this module
`-- __init__.py                 # EDIT: add source_data_contract to the
                                 #   side-effecting import block AND to __all__

docs/
|-- readiness/
|   `-- source-ready.md         # EDIT: add HR12 to a new "Optional strengthening
|                                #   checks" row -- one sentence that HR12 is
|                                #   opt-in evidence only, never changes the
|                                #   stage's required-artifact list or its
|                                #   review-based gate procedure
|-- rules/
|   |-- rules-manifest.json     # EDIT: append {id: "HR12", title: "..."}
|   `-- severity-posture.json   # EDIT: append HR12 under "registered"
|-- glossary.md                 # EDIT: add an HR12 row to "Static check rules";
                                 #   bump "Currently 55 rules in 21 families" ->
                                 #   56/22 AND append the `HR` family token to the
                                 #   family list IF NOT ALREADY PRESENT (confirmed
                                 #   at research time: no `HR`-prefixed rule id
                                 #   exists yet, so HR12 is the family's FIRST
                                 #   member if it lands before 089/090/093; mirrors
                                 #   090/093's own plan caveat -- re-verify at
                                 #   implement time rather than trusting this count)
`-- quality/
    `-- rule-count-claims.yaml  # EDIT: reconcile any prose "N rules" claim
                                 #   (claimed-count 55 -> 56 for the
                                 #   glossary-rule-count entry, re-read live)

tests/unit/
|-- test_source_data_contract.py   # NEW rule-behavior tests over fixtures (no
|                                   #   real table's contract is authored)
|-- test_rules_wiring.py           # EDIT: add "HR12" to EXPECTED_RULE_IDS
|-- test_wiring_meta_gate.py       # UNCHANGED (passes once the golden files move)
`-- test_glossary_rule_table.py    # UNCHANGED (passes once the glossary row is added)
```

**Structure Decision**: Single project -- this is a pure addition to the existing
`retail check` static-rules package (Option 1 shape: no frontend/backend split, no
new top-level directory beyond the new template file). The seven wiring surfaces
enumerated in research.md are the complete edit set beyond the rule module and the
new template itself; `mappings/<table>/source-data-contract.yaml` is documented in
data-model.md but NOT created for any real table (nothing on the current tree has
owner-supplied contract facts to fill yet, and inventing them would violate
Principle V).

## Complexity Tracking

*No entries -- no Constitution Check line above requires justification. HR12 is a
single new static rule module reusing an already-shipped YAML-read pattern (AL2's
precedent), introducing no new project, no new live surface, no new dependency
(yaml is already a repo dependency, imported lazily per the shipped precedent), and
no principle violation.*
