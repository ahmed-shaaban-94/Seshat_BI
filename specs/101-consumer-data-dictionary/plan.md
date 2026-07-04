# Implementation Plan: Consumer-Facing Generated Data Dictionary

**Branch**: `101-consumer-data-dictionary` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/101-consumer-data-dictionary/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

A read-committed-input Product Module that COMPOSES one per-table, plain-
language consumer data dictionary from already-committed artifacts: the
deployed gold star's columns (read from the committed gold migration SQL,
`warehouse/migrations/*_create_gold_<table>*.sql`), each column's committed
mapping rationale (`mappings/<table>/source-map.yaml` `columns[].reason`), and
every metric contract under `mappings/<table>/metrics/*.yaml` (carrying
`formula_intent` forward verbatim and surfacing `readiness.status`). It never
invents meaning: a gold column with no committed consumer-facing or mapping-
rationale text gets an explicit, greppable gap marker, never a generated
gloss (FR-008, pending the OPEN Q1 owner ruling). Technical approach: a
`.claude/skills/` skill (the agent is the runtime; no executor code) plus one
generic `templates/` file, following the F035 `approval-evidence-pack` /
F039-proposal `cross-table-lineage` shape (module-contract block embedded in
`SKILL.md`, an honest-state table, forbidden-operations list). It adds no
`retail check` rule, no readiness stage, and no gate; its only write is its
own output file, `mappings/<table>/consumer-data-dictionary.md` (FR-018).

## Technical Context

**Language/Version**: N/A -- docs/skill/template only; no executable code is
authored (the agent, following the skill's numbered steps, is the runtime, per
the F025-F035/F039 Product Module precedent). Any illustrative snippet in the
skill doc is prose, not shipped code.

**Primary Dependencies**: None. Stdlib-only philosophy carried over from the
sibling static-rule precedent, though this feature adds no rule at all, so
there is no import surface to bound -- the SCOPE GUARD's "no execution" still
applies: the agent reads text files (SQL, YAML, Markdown) with its normal
file-reading tools, nothing more.

**Storage**: Files only -- reads committed SQL/YAML under the repo working
tree; writes one generated Markdown artifact per table per run. No database,
no external service, no live Power BI connection.

**Testing**: Manual/agent-driven exercise per `quickstart.md` (generate the
dictionary for a known table; inspect for citation completeness against
SC-002, the no-score/no-count negative check against SC-003, the "composes-
only" `git status` proof against SC-004 -- the F028/F035/F039 verification
pattern). No `pytest` suite: there is no `src/retail/rules/` entry and no
Python module this feature adds (see Constitution Check, Principle I below).

**Target Platform**: Local repo working tree (Windows-primary per repo
convention; ASCII/UTF-8-no-BOM per Principle IX).

**Project Type**: Docs/skill/template Product Module (no application code).

**Performance Goals**: N/A -- a single agent-driven read-and-render pass over
a handful of committed files per table; no throughput/latency target applies.

**Constraints**: Static-read only (Principle VIII); no live DB/PBIP/F016
surface; no `retail check` rule-id; Windows 260-char path budget (short skill
and template names); ASCII/UTF-8-no-BOM output (Principle IX; FR-016); output
path fixed at `mappings/<table>/consumer-data-dictionary.md` (FR-018), never
colliding with the handoff pack's item (e) or any F028 evidence-pack filename.

**Scale/Scope**: One consumer data dictionary per table per invocation, scoped
to a table that has reached Gold Ready (a committed gold migration SQL
exists); a pre-Gold-Ready table yields a document-level gap, not a fabricated
column list (FR-014). No new artifact family beyond the one output document,
no schema change, no shared surface beyond the roadmap-ledger row (deferred to
integration time, see `research.md` section 1.4).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I -- Agent-First / Gate-Enforced (rule fails CLOSED, never merely
  advises; demonstrable via `retail check`)**: This feature adds **no rule and
  no gate** -- per the Collision-Avoidance Allocation and FR-017, it is a
  Product Module, not a `retail-check` rule, and claims no rule-id. Principle
  I's "fails closed" mandate governs static-check RULES; there is none here, so
  it does not directly bind. The honest analog is a **fail-SAFE** default at
  the module-behavior level (not a gate): the module never asserts a meaning no
  committed artifact records (FR-005/FR-008/FR-009), records an explicit GAP
  marker rather than fabricating content when a source is missing/unreadable
  (FR-008, FR-014, FR-019), and never presents a non-`pass` metric contract as
  approved (FR-006). `retail check` itself is unaffected by this feature and
  continues to run/pass exactly as before. **PASS** (no rule added; fail-safe
  module behavior documented as the correct, narrower analog).
- **Principle III -- Medallion / Gold-Only (Power BI reads gold only; gold is a
  Kimball star; Postgres-first)**: This feature reads the SQL that already
  builds gold -- it does not change what Power BI is allowed to read, does not
  add a new schema layer, and asserts no new fact/dimension shape. It
  describes the DEPLOYED gold star only: a column dropped for PII or otherwise
  never materialized to gold MUST NOT appear (FR-010). **PASS** (no schema
  surface touched; the module is a reader over already-deployed gold DDL text,
  not a participant in the medallion pipeline).
- **Principle IV -- Source-Mapping-Before-Silver (no `silver.*` SQL before the
  source-map is reviewed+approved)**: This feature authors **zero** SQL of any
  kind and moves no table through any readiness stage. It reads
  `source-map.yaml` read-only for its `reason` text; if the gold migration SQL
  does not yet exist for a table (i.e. the table has not reached Gold Ready,
  which itself requires a cleared Mapping Ready gate upstream), the module
  records a document-level gap (FR-014) rather than fabricating a column list
  from an unreviewed or aspirational source. **PASS**.
- **Principle V -- Agent-Stops-at-Judgment (no self-granted grain/PII/business-
  policy/approval decision; raise unresolved-questions and STOP)**: This is
  the principle the feature is built around. FR-008/Q1 (may the module
  GENERATE a simplified paraphrase of a column's technical source-map `reason`,
  or must it always verbatim-cite-or-gap) is an explicit OPEN owner ruling --
  this plan does **not** resolve it and does not adopt a paraphrase-generation
  capability; the fail-safe default (verbatim-cite-or-gap, never a generated
  gloss) ships regardless of the eventual ruling (spec Clarifications Q1).
  FR-009 forbids the module from defining, approving, revising, or resolving
  any metric's formula, grain, or business meaning, and from resolving any
  open mapping question. FR-011 forbids writing back to any upstream source
  artifact. **PASS** -- this design satisfies Principle V by construction;
  FR-008/Q1 remains genuinely OPEN and is surfaced to the human reviewer, not
  quietly closed here (see `open_principle_v` in this stage's structured
  output).
- **Principle VI -- Defaults-Then-Deviations**: The spec's own Clarifications
  session already resolved four non-Principle-V ambiguities as reversible,
  docs-only defaults, all CONFIRMED (not deviated from) in this plan: Q2
  (document ordering -- gold-SQL column definition order, then lexical
  `metrics/*.yaml` filename order), Q3 (gap-marker minimum shape -- a
  greppable `GAP:` label + identifier + checked-and-missing path(s)), Q4
  (metric inclusion scope -- list every contract found, approved and pending
  alike, each marked with its own recorded status), and Q5 (gold-column-to-
  source-map join basis -- a gold column matches its source-map entry by the
  source-map's own recorded `source_name`, or by the `gold_star` dimension's
  listed attribute name, NEVER by position or fuzzy string matching; a gold
  column with no such matching record -- a surrogate key or an RC15
  calendar-derived `dim_date` attribute alike -- falls through to FR-008's
  verbatim-cite-or-gap/gap behavior). Q5 is mechanical disambiguation over
  already-committed, deterministic fields (Principle VIII), not a business-
  meaning/PII/grain judgment call, so it is a Principle-VI default rather than
  a Principle-V open question -- and it is load-bearing: it is what stops one
  column's `reason` being misattributed to a different column (data-model.md
  Entity 2 states this join rule as an explicit invariant). FR-018's
  output-path convention (`mappings/<table>/consumer-data-dictionary.md`) is
  the same kind of reversible, non-Principle-V docs/naming default, matching
  the existing co-location convention (`reconciliation-report.md`,
  `unresolved-questions.md`, `evidence-pack-index.md` already live at
  `mappings/<table>/`). **PASS**.
- **Principle VII -- C086-is-an-example-not-the-schema**: The skill and its
  template resolve a generic `mappings/<table>/` and gold-migration path per
  table (FR-015); C086 / `retail_store_sales` appears in this plan set and in
  the skill doc only as a CITED FILLED INSTANCE (paths confirmed real in
  `research.md` section 2), never inlined into a fixed section label or the
  template body. **PASS** (verified per SC-006's own test: 0 generic artifacts
  contain a worked-example domain specific outside a cited-instance example).
- **Principle VIII -- Static-First / Live-Deferred**: The module reads ONLY
  already-committed repo text (gold migration SQL, source-map YAML, metric
  contract YAML). It opens no DB connection, runs no SQL, executes no DAX, and
  does not invoke F016 or the spec-only F031-F033 runtimes (FR-002,
  research.md section 3). Unlike a fully static sibling feature, this design
  has ONE genuine live-deferred surface: reconciling the dictionary's column
  list against the ACTUALLY-DEPLOYED database schema is explicitly OUT OF
  SCOPE and marked PENDING (spec Assumptions) -- a gold-SQL-vs-source-map
  disagreement between the two STATIC committed files is still detected and
  recorded as a gap (FR-019, in scope, no live surface needed); only the live
  catalog check itself is deferred, never silently assumed reconciled.
  **PASS** (the one live-adjacent surface is explicitly named and marked
  PENDING, not assumed).
- **Principle IX -- Secrets / Reproducibility**: No host, DSN, or secret is
  read, cited, or written anywhere in this feature's artifacts (the three
  input families are all SQL/YAML text, never a `.env` or connection string).
  All authored/generated artifacts are ASCII, UTF-8 without BOM, using
  `--`/`->` in place of glyphs (FR-016), and short repo-relative paths
  respecting the Windows 260-char budget (informing the short skill name
  chosen below). **PASS**.
- **Hard rule #9 -- No fabricated confidence/health/maturity score or
  completeness count**: FR-013 explicitly forbids any numeric score or "N of
  M" completeness tally; gaps are expressed only as explicit named gap
  markers (SC-003, SC-007). This plan's design carries no counter, no
  percentage, no score field anywhere in the artifact shape (see
  `data-model.md`). **PASS**.
- **F016 assumption**: F016 (Power BI execution adapter) does not exist and is
  never invoked, called, or assumed reachable by this design (FR-002,
  research.md section 3). **PASS**.

**Overall**: All checked principles PASS. No Complexity Tracking entry is
required (no principle is being knowingly stretched or deferred with a
justification owed) -- the single genuine open question (FR-008/Q1) is a
Principle-V human ruling, not a design compromise this plan is asking for an
exception on, so it is surfaced, not justified-around.

## Project Structure

### Documentation (this feature)

```text
specs/101-consumer-data-dictionary/
|-- plan.md              # This file (/speckit-plan command output)
|-- research.md          # Phase 0 output (/speckit-plan command)
|-- data-model.md        # Phase 1 output (/speckit-plan command)
|-- quickstart.md        # Phase 1 output (/speckit-plan command)
`-- spec.md               # Already exists (clarified)
```

No `contracts/` directory is created -- this feature has no API/service
contract; its output SHAPE is documented in `data-model.md` instead (matching
the F035/F039 precedent, which also carries no `contracts/`).

### Source Code (repository root)

This feature is **docs/skill/template only** (Product Module, `artifact-
writing` capability level per `docs/architecture/product-modules.md` -- see
`research.md` section 1.3 for why `artifact-writing`, not `read-only`, is the
correct F024 capability-level label even though the spec's own SCOPE GUARD
calls it a "read-only skill/template" in the input-discipline sense). It adds
NO `src/retail/rules/` entry, NO Python module, and NO test suite under
`tests/`.

```text
# Real repo paths this feature ADDS
.claude/skills/consumer-data-dictionary/
`-- SKILL.md                          # the skill: numbered compose steps,
                                       #   embedded Module Contract block,
                                       #   honest-state table, forbidden-ops
                                       #   list (F035/F039 SKILL.md shape)

templates/
`-- consumer-data-dictionary.md       # ONE generic copy-me template; no C086
                                       #   specifics; short filename (Windows
                                       #   260-char budget)

# Real repo paths this feature EDITS
(none -- this stage authors no edits to existing shipped files; the
 roadmap-ledger row for the new F-number is an INTEGRATION-TIME edit to
 docs/roadmap/roadmap.md, deliberately deferred past this plan per
 research.md section 1.4 to avoid colliding with other in-flight features on
 that shared file)

# Real repo paths this feature READS ONLY (Core Authority, never edited)
warehouse/migrations/*_create_gold_<table>*.sql
mappings/<table>/source-map.yaml
mappings/<table>/metrics/*.yaml

# Real repo paths this feature WRITES (its own generated output only)
mappings/<table>/consumer-data-dictionary.md
```

**Structure Decision**: Docs/skill/template Product Module, matching the
F025-F035/F039 precedent exactly. One skill directory
(`.claude/skills/consumer-data-dictionary/`, short name for the Windows path
budget), one generic template (`templates/consumer-data-dictionary.md`), zero
`src/retail/rules/` entries, zero new schema/DB surface. The skill's embedded
Module Contract block declares `Capability level: artifact-writing` (per
`docs/architecture/product-modules.md`'s three-level vocabulary; see
research.md 1.3) and `Product layer: 6` (Dashboard & Delivery / BI handoff --
the same functional-axis layer F013's handoff pack and F028's evidence pack
occupy, since this module also serves the post-Gold-Ready-through-Publish
window, though as an optional companion rather than gate evidence). The
proposed roadmap feature number is **F040** (research.md section 1.4: F035 is
the highest shipped Product Module, F038 is the highest shipped F-number
overall and belongs to a different category, F036/F037 are unaccounted for in
the committed ledger, and F039 is already proposed by the in-flight sibling
`specs/099-cross-table-lineage-impact/`; F040 is the next unclaimed slot) --
this is a PROPOSAL recorded here at plan time, not a roadmap-ledger edit;
reconciling the actual row (including resolving what F036/F037/F039 turn out
to be at integration time) is left to whoever merges this feature, matching
the spec 044 / spec 063 / spec 099 precedent of not self-assigning a number.

## Complexity Tracking

*No entries.* The Constitution Check above found no principle requiring a
justified exception. The single open item (FR-008/Q1, the paraphrase-
authoring-latitude question) is a Principle-V human-ruling gap, not a
complexity/deviation this plan is asking forgiveness for -- it is carried
forward unresolved and surfaced to the reviewer, per Principle V's own
"stop and ask" mandate.
