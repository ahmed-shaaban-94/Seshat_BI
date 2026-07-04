# Implementation Plan: Cross-Table Column-Level Lineage / Impact Analysis

**Branch**: `099-cross-table-lineage-impact` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/099-cross-table-lineage-impact/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

A read-only Product Module that DERIVES one ordered lineage/impact artifact from
already-committed repo text, starting from either a `schema.table.column`
identifier or a `mappings/<table>/metrics/<Metric>.yaml` contract identifier. It
walks the fixed forward chain -- source-map entry -> silver/gold migration SQL
reference -> metric contract -> TMDL measure -> dashboard visual binding --
citing the exact committed path for every hop it asserts, tiering each hop as
PROVEN / UNRESOLVED (candidate) / GAP (FR-016), and never fabricating an edge no
committed artifact already records (FR-005). It generalizes the shape of
`docs/demo/net-sales-end-to-end-readiness-trace.md` into a regeneratable
template. Technical approach: a `.claude/skills/` skill (the agent is the
runtime; no executor code) plus one generic `templates/` file, following the
F035 `approval-evidence-pack` shape (module-contract block embedded in
`SKILL.md`, an honest-state table, forbidden-operations list). It adds no
`retail check` rule and no readiness stage.

## Technical Context

**Language/Version**: N/A -- docs/skill/template only; no executable code is
authored (the agent, following the skill's numbered steps, is the runtime, per
the F025-F035 Product Module precedent). Any illustrative snippet in the skill
doc is prose, not shipped code.

**Primary Dependencies**: None (stdlib-only philosophy carried over from the
sibling static-rule precedent; this feature has no rule at all, so there is no
import surface to bound -- but the SCOPE GUARD's "no execution" still applies:
the agent reads text files with its normal file-reading tools, nothing more).

**Storage**: Files only -- reads committed YAML/SQL/TMDL/Markdown under the
repo working tree; writes one generated Markdown artifact per run. No database,
no external service.

**Testing**: Manual/agent-driven exercise per `quickstart.md` (generate the
artifact for a known column and a known contract; inspect for citation
completeness, FR-006/FR-007 negative checks, and the "composes-only" `git
status` proof -- the F028/F035 verification pattern). No `pytest` suite: there
is no `src/retail/rules/` entry and no Python module this feature adds (see
Constitution Check, Principle I below).

**Target Platform**: Local repo working tree (Windows-primary per repo
convention; ASCII/UTF-8-no-BOM per Principle IX).

**Project Type**: Docs/skill/template Product Module (no application code).

**Performance Goals**: N/A -- a single agent-driven read-and-render pass over a
handful of committed files; no throughput/latency target applies.

**Constraints**: Static-read only (Principle VIII); no live DB/PBIP/F016
surface; no `retail check` rule-id; Windows 260-char path budget (short skill
and template names); ASCII/UTF-8-no-BOM output (Principle IX; FR-012).

**Scale/Scope**: One lineage artifact per (starting point) per invocation;
scope is bounded to the five already-shipped artifact families enumerated in
`research.md` section 2. No new artifact family, no schema change, no shared
surface beyond the roadmap-ledger row (deferred to integration time, see
`research.md` section 1.5).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I -- Agent-First / Gate-Enforced (rule fails CLOSED, never merely
  advises; demonstrable via `retail check`)**: This feature adds **no rule and
  no gate** -- per the collision-avoidance allocation and FR-013, it is a
  Product Module, not a `retail-check` rule, and claims no rule-id. Principle
  I's "fails closed" mandate governs static-check RULES; there is none here, so
  it does not directly bind. The design's honest analog is a **fail-SAFE**
  default at the module-behavior level (not a gate): the module never asserts
  an edge no committed artifact records (FR-005), records an explicit BLOCKER
  or GAP rather than fabricating content when an input is missing/unreadable
  (FR-008/FR-015), and treats any unresolved name-similarity link as
  candidate-only, never silently promoted to proven (FR-010). `retail check`
  itself is unaffected by this feature and continues to run/pass exactly as
  before. **PASS** (no rule added; fail-safe module behavior documented as the
  correct, narrower analog).
- **Principle II -- Depend, Never Fork (execution-adapter relationship)**: N/A --
  this feature touches no execution adapter, no Power BI connection surface, and
  no engine/adapter dependency of any kind; it is a static text reader with zero
  adapter surface (FR-002, FR-013). Recorded here explicitly so the omission
  reads as a deliberate disposition, not an overlooked principle.
- **Principle III -- Medallion / Gold-Only (Power BI reads gold only; gold is a
  Kimball star; Postgres-first)**: This feature reads the SQL that already
  builds gold and the TMDL that already reads gold -- it does not change what
  Power BI is allowed to read, does not add a new schema layer, and asserts no
  new fact/dimension shape. It only cites already-committed silver/gold SQL and
  TMDL text. **PASS** (no schema surface touched; the module is a reader over
  text describing the existing medallion, not a participant in it).
- **Principle IV -- Source-Mapping-Before-Silver (no `silver.*` SQL before the
  source-map is reviewed+approved)**: This feature authors **zero** SQL of any
  kind (silver, gold, or otherwise) and moves no table through any readiness
  stage. When a table's `source-map.yaml` is not yet approved (or does not
  exist), the module records the source-map hop as a GAP/blocker and does not
  proceed to fabricate a downstream chain from an unreviewed map, per FR-015
  and the spec's edge-case note ("it never implies a stage is `pass` because an
  artifact for it happens to exist on disk unreviewed"). **PASS**.
- **Principle V -- Agent-Stops-at-Judgment (no self-granted grain/PII/business-
  policy/approval decision; raise unresolved-questions and STOP)**: This is the
  principle the feature is built around. FR-010 (contract<->gold-column and
  measure<->contract name-resolution) is an explicit OPEN owner ruling -- this
  plan does **not** resolve it and does not adopt a name-similarity heuristic;
  the fail-safe default (candidate-only, never proven, never silently
  auto-accepted) ships regardless of the eventual ruling (spec Clarifications).
  FR-007 forbids any verb of obligation ("must"/"should"/"needs to") applied to
  a downstream item -- the module states reachability and evidence only; a
  human (or a separate F014 drift run) decides what to re-review. FR-009
  forbids moving a stage, granting an approval, defining business meaning, or
  writing back to any artifact this module reads. **PASS** -- this design
  satisfies Principle V by construction; FR-010 remains genuinely OPEN and is
  surfaced to the human reviewer, not quietly closed here (see
  `open_principle_v` in this stage's structured output).
- **Principle VI -- Defaults-Then-Deviations**: FR-014's output-path convention
  (`mappings/<table>/lineage-column-<column>.md` /
  `lineage-metric-<Metric>.md`) is exactly this kind of reversible,
  non-Principle-V docs/naming default -- already adopted in the spec's own
  Clarifications and CONFIRMED (not deviated from) in this plan's Project
  Structure below, because it matches the existing co-location convention
  (`reconciliation-report.md`, `unresolved-questions.md` already live at
  `mappings/<table>/`). **PASS**.
- **Principle VII -- C086-is-an-example-not-the-schema**: The skill and its
  template resolve a generic `schema.table.column` or
  `mappings/<table>/metrics/<Metric>.yaml` starting point (FR-011); C086 /
  `retail_store_sales` appears in this plan set and in the skill doc only as a
  CITED FILLED INSTANCE (paths confirmed real in `research.md` section 2),
  never inlined into a fixed section label or the template body. **PASS**
  (verified per SC-007's own test: 0 generic artifacts contain a worked-example
  domain specific outside a cited-instance example).
- **Principle VIII -- Static-First / Live-Deferred**: The module reads
  ONLY already-committed repo text (source-map YAML, migration SQL, metric
  contract YAML, TMDL, binding-map Markdown). It opens no DB connection, runs
  no SQL, executes no DAX, and does not invoke F016 or the spec-only F031-F033
  runtimes (FR-002, research.md section 3). No live surface is assumed; none is
  even marked PENDING because none is needed -- the entire feature is
  structurally static. **PASS**.
- **Principle IX -- Secrets / Reproducibility**: No host, DSN, or secret is
  read, cited, or written anywhere in this feature's artifacts (the five input
  families are all schema/SQL/YAML/TMDL/Markdown text, never a `.env` or
  connection string). All authored/generated artifacts are ASCII, UTF-8 without
  BOM, using `--`/`->` in place of glyphs (FR-012), and short repo-relative
  paths respecting the Windows 260-char budget (informing the short skill name
  chosen below). **PASS**.
- **Hard rule #9 -- No fabricated confidence/health/maturity score or
  completeness count**: FR-006 explicitly forbids any numeric blast-radius
  score, "N artifacts affected" count, or confidence/health/maturity value; the
  downstream set is expressed only as a named SET of hops with evidence
  citations and gaps (SC-003). This plan's design carries no counter, no
  percentage, no score field anywhere in the artifact shape (see
  `data-model.md`). **PASS**.
- **F016 assumption**: F016 (Power BI execution adapter) does not exist and is
  never invoked, called, or assumed reachable by this design (FR-002,
  research.md section 3). **PASS**.

**Overall**: All checked principles PASS. No Complexity Tracking entry is
required (no principle is being knowingly stretched or deferred with a
justification owed) -- the single genuine open question (FR-010) is a
Principle-V human ruling, not a design compromise this plan is asking for an
exception on, so it is surfaced, not justified-around.

## Project Structure

### Documentation (this feature)

```text
specs/099-cross-table-lineage-impact/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── spec.md               # Already exists (clarified)
```

No `contracts/` directory is created -- this feature has no API/service
contract; its output SHAPE is documented in `data-model.md` instead (matching
the F035 precedent, which also carries no `contracts/`).

### Source Code (repository root)

This feature is **docs/skill/template only** (Product Module, `artifact-
writing` capability level per `docs/architecture/product-modules.md` -- see
`research.md` section 1.4 for why `artifact-writing`, not `read-only`, is the
correct F024 capability-level label even though the spec's own framing calls it
a "read-only aggregator" in the input-discipline sense). It adds NO
`src/retail/rules/` entry, NO Python module, and NO test suite under `tests/`.

```text
# Real repo paths this feature ADDS
.claude/skills/cross-table-lineage/
└── SKILL.md                          # the skill: numbered compose steps,
                                       #   embedded Module Contract block,
                                       #   honest-state table, forbidden-ops list
                                       #   (F035 approval-evidence-pack shape)

templates/
└── lineage-trace.md                  # ONE generic copy-me template covering
                                       #   BOTH starting-point shapes (column-
                                       #   rooted and metric-rooted); no C086
                                       #   specifics; short filename (Windows
                                       #   260-char budget)

# Real repo paths this feature EDITS
(none -- this stage authors no edits to existing shipped files; the
 roadmap-ledger row for the new F-number is an INTEGRATION-TIME edit to
 docs/roadmap/roadmap.md, deliberately deferred past this plan per
 research.md section 1.5 to avoid colliding with 18 other in-flight features
 on that shared file)

# Real repo paths this feature READS ONLY (Core Authority, never edited)
mappings/<table>/source-map.yaml
warehouse/migrations/*.sql
mappings/<table>/metrics/*.yaml
powerbi/*.SemanticModel/definition/tables/*.tmdl
templates/visual-contract-binding-map.md (+ any filled per-subject-area copy
  the dashboard-design skill has produced)

# Real repo paths this feature WRITES (its own generated output only)
mappings/<table>/lineage-column-<column>.md      # column-rooted starting point
mappings/<table>/lineage-metric-<Metric>.md      # metric-rooted starting point
```

**Structure Decision**: Docs/skill/template Product Module, matching the
F025-F035 precedent exactly. One skill directory
(`.claude/skills/cross-table-lineage/`, short name for the Windows path
budget), one generic template (`templates/lineage-trace.md`), zero
`src/retail/rules/` entries, zero new schema/DB surface. The skill's embedded
Module Contract block declares `Capability level: artifact-writing` (per
`docs/architecture/product-modules.md`'s three-level vocabulary; see
research.md 1.4) and `Product layer: 6` (Dashboard & Delivery /
cross-cutting -- the same functional-axis layer F028's evidence pack and F035's
approval pack occupy, since this module also composes committed evidence into
one traceable document spanning the Mapping-through-Dashboard stages). The
proposed roadmap feature number is **F039** (research.md section 1.5: F035 is
the highest shipped Product Module, F038 is the highest shipped F-number
overall and belongs to a different category, F036/F037 are unaccounted for in
the committed ledger, F039 is unclaimed) -- this is a PROPOSAL recorded here at
plan time, not a roadmap-ledger edit; reconciling the actual row (including
resolving what, if anything, F036/F037 were) is left to integration time,
matching the spec 044 / spec 063 precedent of not self-assigning a number.

## Complexity Tracking

*No entries.* The Constitution Check above found no principle requiring a
justified exception. The single open item (FR-010, the name-resolution
authorization) is a Principle-V human-ruling gap, not a complexity/deviation
this plan is asking forgiveness for -- it is carried forward unresolved and
surfaced to the reviewer, per Principle V's own "stop and ask" mandate.
