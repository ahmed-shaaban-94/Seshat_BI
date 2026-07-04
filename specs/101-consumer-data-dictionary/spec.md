# Feature Specification: Consumer-Facing Generated Data Dictionary

**Feature Branch**: `101-consumer-data-dictionary`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #13. Consumer-facing generated data dictionary -- a
per-table consumer data dictionary generated from committed artifacts (gold columns +
metric contracts -> plain 'what does this column/measure mean' for the analyst)."

## Overview

Today, "what does this column/measure mean" answers exist but are scattered across
BUILDER-facing artifacts that were never written for a self-serve analyst: a gold
column's business meaning lives as a mapping-decision `reason` string inside
`mappings/<table>/source-map.yaml` (e.g. "the grain key; unique on the data -> degenerate
dim on the fact (RC14)" -- written for the person reviewing the mapping gate, not for
someone reading a report); a measure's plain-language meaning lives as `formula_intent`
inside `mappings/<table>/metrics/<Metric>.yaml` (already consumer-legible prose, e.g.
"The total money taken across all retail transactions..."); and the handoff pack's own
data dictionary section (`templates/handoff/bi-handoff-pack.md`, item e) exists to
satisfy the Publish Ready GATE for the data-owner/governance reviewer authorizing
release, not to serve the analyst who later queries the published model.

Nobody currently serves the CONSUMER: the analyst who opens the published table/report
and wants, in one place and in plain language, "what is this column, what is this
measure, where did that meaning come from." This feature defines a new, generic Product
Module (skill + template, read-only/read-derive) that COMPOSES a per-table consumer data
dictionary from already-committed artifacts -- the gold star's deployed columns (read
from the committed gold migration SQL, e.g.
`warehouse/migrations/0004_create_gold_<table>_star.sql`) and the approved metric
contracts (`mappings/<table>/metrics/*.yaml`) -- and renders one plain-language,
analyst-facing reference. It composes; it never invents. Where a committed source
carries a consumer-legible meaning (a metric's `formula_intent`), the module cites and
carries it forward. Where a gold column's only committed meaning is a technical mapping
rationale (a source-map `reason` written for the mapping gate, not for a report reader),
the module does not manufacture consumer prose to fill the gap -- see FR-008 and the
open Principle-V question below.

## Boundary against neighbouring shipped work (read first)

This feature is a genuinely NEW, narrowly-scoped artifact, not a re-skin of an existing
one. Three shipped/committed neighbours must stay distinct:

- **F013 BI Handoff Pack** (`templates/handoff/bi-handoff-pack.md`, item e "Data
  dictionary") is a REQUIRED section of the Publish Ready (Stage 7) GATE bundle: its
  audience is the data-owner/governance reviewer deciding whether to authorize release,
  its lifecycle moment is BEFORE publish (gate evidence), and a mismatch against the
  deployed schema FAILS the checklist (publish-ready.md). This feature's dictionary is
  an OPTIONAL companion consumed AFTER a table is published, by the analyst querying it
  self-serve; it adds NO gate, NO blocking reason, and NO required section to Publish
  Ready. It follows the precedent already set by
  `templates/handoff/answerability-summary.md` ("NOT a required Stage 7 artifact, not a
  gate") rather than extending the handoff pack itself. It composes from the SAME
  upstream truth (gold columns + metric contracts) but does not edit, re-render, or
  duplicate-govern F013's item (e); a change to F013's dictionary is not a change to
  this artifact and vice versa.
- **F028 evidence-pack-generator** (`.claude/skills/evidence-pack-generator/`, spec 022)
  composes a late-stage, 10-section READINESS evidence bundle (blockers, scorecards,
  approvals) for the Semantic Model -> Dashboard -> Publish window. This feature composes
  a MEANING reference (what a column/measure means), not a readiness bundle; it carries
  no blocker list, no stage status, no approval slot, and is not part of any stage's
  evidence[] by default.
- **The `power-bi-docs` skill family** (per this repo's Power BI CLI router) generates
  model documentation FROM A LIVE, CONNECTED semantic model (`pbi connect` required).
  This feature is Principle-VIII static-first: it reads only committed, on-disk
  artifacts (gold migration SQL, metric-contract YAML) and never opens a live Power BI
  or database connection; any live-schema drift against the deployed model is marked
  PENDING, never silently assumed reconciled.

This feature adds NO new readiness stage, NO new `retail check` rule, and NO rule id
(Collision-Avoidance Allocation: Product Module, read-only skill/template). It touches
no shared schema and needs no new roadmap F-number decision beyond what is recorded at
plan time (063 precedent: the spec does not invent one).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An analyst gets one plain-language reference for a published table (Priority: P1)

An analyst who has access to a published table/report wants to know, in their own
words-level of plain language, what each gold column and each approved measure means,
without hunting through `source-map.yaml` mapping rationale or metric-contract YAML
files written for a different audience. They ask for the consumer data dictionary for
that table and receive one ordered document: every deployed gold column listed exactly
once with its business meaning (where a committed consumer-legible meaning exists) or an
explicit gap marker (where it does not), and every approved metric listed with its
`formula_intent` carried forward verbatim, each entry citing the committed artifact it
came from.

**Why this priority**: This is the entire value of the feature -- a self-serve, plain-
language reference for the consumer. Without it the feature delivers nothing.

**Independent Test**: For a table with a committed gold migration SQL file and at least
one approved (`readiness.status: pass`) metric contract, generating the dictionary
produces one document listing every deployed gold column and every approved metric, each
entry traceable to a committed source path, with no invented prose.

**Acceptance Scenarios**:

1. **Given** a table with a committed gold migration SQL (e.g.
   `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`) and approved
   metric contracts under `mappings/<table>/metrics/`, **When** the consumer data
   dictionary is generated for that table, **Then** the output lists every column
   defined in the deployed gold star exactly once and every metric contract file found
   under `mappings/<table>/metrics/*.yaml` exactly once (approved contracts whose
   `readiness.status` is `pass` are included alongside any pending contract, per
   FR-004/FR-006, each clearly marked with its own recorded status).
2. **Given** the same table, **When** the dictionary is generated, **Then** every metric
   entry carries forward that contract's `formula_intent` text and cites the contract's
   file path.
3. **Given** the dictionary is generated, **When** it is inspected, **Then** it does not
   write to, modify, or append to `source-map.yaml`, any `metrics/*.yaml` contract, the
   gold migration SQL, `readiness-status.yaml`, or the handoff pack.

---

### User Story 2 - A column has no committed consumer-legible meaning, so the entry records a gap (Priority: P1)

The analyst requests the dictionary for a table where a deployed gold column's only
committed meaning is a technical mapping-decision `reason` (written for the mapping-gate
reviewer, not for a report reader) -- for example a surrogate key or a degenerate-dim
column whose source-map `reason` reads "the grain key; unique on the data -> degenerate
dim on the fact (RC14)". The module does not rewrite or simplify that technical rationale
into invented consumer prose (composing, never inventing meaning -- retail-kpi/source-map
owns meaning); the entry instead surfaces the committed rationale AS RECORDED and/or
marks the column's consumer-facing definition as an explicit GAP, never fabricating a
plain-language gloss that no committed artifact actually states.

**Why this priority**: The no-invention scope guard is the module's integrity guarantee.
A dictionary that silently improvises consumer prose for ungoverned columns would present
agent-invented meaning as if a human had defined it -- exactly the Principle-V violation
this module must not commit. This must hold from day one, matching the same priority the
063 precedent gives its no-fabrication story (its User Story 2).

**Independent Test**: Generate the dictionary for a table with at least one gold column
whose only committed source is a technical source-map `reason` (no separate consumer-
meaning field); the corresponding entry cites that `reason` verbatim (or records an
explicit gap), and contains no sentence that does not trace to a committed source.

**Acceptance Scenarios**:

1. **Given** a gold column whose only committed meaning is a source-map `reason` written
   for the mapping gate, **When** the dictionary is generated, **Then** the entry either
   quotes that `reason` verbatim with its source path or records an explicit "no
   consumer-facing definition committed" gap -- it does not paraphrase the rationale into
   new prose.
2. **Given** a gold column present in the deployed gold star with NO corresponding
   `source-map.yaml` column entry at all (e.g. a surrogate key generated in the gold
   migration itself, or a calendar-derived `dim_date` attribute such as `month_name`,
   `day_name`, or `is_weekend` produced by the RC15 `generate_series` logic rather than
   read from any source column -- see FR-005/Clarifications 2026-07-04 Q5 for the
   column-to-source-map matching basis), **When** the dictionary is generated, **Then**
   the entry records an explicit gap naming the column and the missing source, rather
   than omitting the column or inventing a definition.
3. **Given** a metric contract file referenced by the table that is missing or unreadable,
   **When** the dictionary is generated, **Then** the entry records that unreadable path
   as a gap rather than silently dropping the metric.

---

### User Story 3 - The same generator serves any mapped, gold-built table (Priority: P2)

An analyst uses the same module, changing only the table identifier, to produce a
dictionary for a second table that has reached Gold Ready. The module resolves that
table's own committed gold migration SQL and its own `mappings/<table>/metrics/*.yaml`
set, and produces a dictionary with no worked-example (C086 / `retail_store_sales`)
specifics baked into the template's fixed structure.

**Why this priority**: Genericity across tables (Principle VII) is what makes this a
reusable Product Module rather than a one-table script; a single working table (P1) is
already a viable, demonstrable slice, so this is P2.

**Independent Test**: Generate the dictionary for two different tables; each output
resolves its own gold migration SQL and its own metrics folder, and the template's fixed
section labels contain no domain-specific column name, grain key, or metric name.

**Acceptance Scenarios**:

1. **Given** table identifier `retail_store_sales`, **When** the dictionary is
   generated, **Then** it resolves `mappings/retail_store_sales/metrics/*.yaml` and the
   gold migration SQL that creates `gold.fct_sales_rss` (or the equivalent committed
   gold star for that table).
2. **Given** a second, different mapped table, **When** the dictionary is generated,
   **Then** it resolves that table's own gold migration SQL and metrics folder, not the
   first table's.
3. **Given** any table, **When** the dictionary is generated, **Then** the template and
   any fixed section labels contain no C086/`retail_store_sales`-specific column name,
   grain key, or metric name (Principle VII).

---

### Edge Cases

- What happens when the table has not yet reached Gold Ready (no committed gold
  migration SQL exists)? The module must record that as a top-level gap/blocker-style
  note (this module writes no readiness status, so it is a document-level gap, not a
  `blocking_reasons[]` entry) and must not fabricate a column list from an aspirational
  design instead of the deployed schema.
- What happens when a metric contract exists but its `readiness.status` is not `pass`
  (e.g. `not_started` or a proposal)? See FR-006 -- the module surfaces the metric
  contract's own recorded status rather than treating it as approved, and clearly marks
  it as not-yet-approved.
- What happens when the gold migration SQL and `source-map.yaml` disagree on a column's
  presence or name (drift)? The module records the discrepancy as a gap rather than
  silently picking one source as authoritative; live-schema reconciliation against the
  actually-deployed database is out of scope (Principle VIII; PENDING) since this module
  never opens a live connection.
- What happens when a column is marked `pii: true` and dropped in `source-map.yaml`
  (never reaches gold)? It must not appear in the dictionary at all -- the dictionary
  describes the DEPLOYED gold star only, consistent with the handoff pack's own
  deployed-schema-only rule.
- What happens when the same table already has a generated consumer data dictionary on
  disk from a prior run? Regenerating overwrites only this module's own output path; it
  never touches the handoff pack's data dictionary section or any upstream source
  artifact.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The module MUST accept a target table identifier and produce exactly one
  ordered, plain-language consumer data dictionary document for that table. "Ordered"
  means: gold column entries appear in the column definition order of the committed gold
  migration SQL, followed by metric entries in the filename order of
  `mappings/<table>/metrics/*.yaml` (see Clarifications 2026-07-04 Q2).
- **FR-002**: The module MUST read only already-committed artifacts. It MUST NOT connect
  to a database, read a live Power BI/PBIP surface, or invoke any deferred execution
  adapter (F016) or spec-only runtime (F031-F033); it MUST NOT require or assume `pbi
  connect` (Principle VIII).
- **FR-003**: The module MUST enumerate the table's deployed gold columns by reading the
  table's committed gold migration SQL (`warehouse/migrations/*_create_gold_<table>*.sql`
  or the equivalent committed gold DDL), not a live database catalog and not an
  aspirational design doc.
- **FR-004**: The module MUST enumerate the table's approved and pending metric
  contracts by reading `mappings/<table>/metrics/*.yaml`.
- **FR-005**: For each gold column, the dictionary MUST cite the column's committed
  business/mapping meaning from `mappings/<table>/source-map.yaml` (the `reason` and/or
  any explicit consumer-facing meaning field the source-map records for that column),
  quoted or linked as recorded -- it MUST NOT paraphrase or simplify that meaning into
  new wording not present in the committed source. The module MUST match a gold column
  to its source-map entry by the source-map's own recorded `source_name` (or, when the
  gold column lives under a dimension attribute, that dimension's attribute name as
  listed in `gold_star`), NEVER by fuzzy or positional matching; a gold column with no
  `source_name` that resolves this way (e.g. a surrogate key or a calendar-derived
  attribute such as a `dim_date` `month_name`/`day_name`/`is_weekend` column generated by
  RC15, which is never a `source-map.yaml` column entry) falls to FR-008's gap behavior.
  See FR-008 for the case where no committed meaning exists at all (see Clarifications
  2026-07-04 Q5).
- **FR-006**: For each metric contract, the dictionary MUST carry forward that contract's
  `formula_intent` text verbatim and MUST surface the contract's recorded
  `readiness.status`; a metric whose status is not `pass` MUST be clearly marked as not
  yet approved, never presented as if it were.
- **FR-007**: Every entry in the dictionary (per column, per metric) MUST cite the
  committed repo-relative source path it was composed from.
- **FR-008**: When a gold column has NO committed consumer-facing or mapping-rationale
  meaning available (no corresponding `source-map.yaml` column entry, or a source-map
  entry with no `reason` recorded), the module MUST record an explicit GAP naming the
  column and the missing source; it MUST NOT invent, infer, or generate a plausible
  business definition to fill the gap. Whether the module may additionally GENERATE a
  simplified, consumer-plain paraphrase of a column's existing TECHNICAL source-map
  `reason` (e.g. turning "the grain key; unique on the data -> degenerate dim on the fact
  (RC14)" into "a unique identifier for each transaction"), versus always falling back to
  verbatim-cite-or-gap for that case, is [OPEN -- Principle-V owner ruling; see
  Clarifications 2026-07-04 Q1]. Until a named human rules on Q1, the module MUST apply
  the verbatim-cite-or-gap behavior (never a generated paraphrase).
- **FR-009**: The module MUST NOT define, approve, revise, or resolve any metric's
  formula, grain, or business meaning, and MUST NOT resolve any open mapping question
  (Principle V) -- it composes only what committed artifacts already state.
- **FR-010**: The dictionary MUST describe the DEPLOYED gold star only: a column dropped
  for PII (per `source-map.yaml` `pii: true` drops) or otherwise never materialized to
  gold MUST NOT appear in the dictionary.
- **FR-011**: The module MUST NOT write to, modify, or append to any upstream source
  artifact (`source-map.yaml`, any `metrics/*.yaml`, the gold migration SQL,
  `readiness-status.yaml`, `unresolved-questions.md`, or the handoff pack) -- its only
  write is its own generated dictionary file.
- **FR-012**: The module MUST NOT write to any readiness stage status;
  it adds no `blocking_reasons[]` entry and no `approvals[]` entry, and its existence or
  absence MUST NOT be treated as a gate requirement for any of the seven readiness
  stages (see Boundary section -- it is an optional companion, not required Publish
  Ready evidence).
- **FR-013**: The dictionary MUST NOT emit any numeric confidence / health / maturity
  score and MUST NOT emit a completeness count or "N of M" tally (hard rule #9); gaps are
  expressed as explicit named gap markers, never as a percentage or ratio.
- **FR-014**: When the table has not yet reached Gold Ready (no committed gold migration
  SQL is found for it), the module MUST record that as a document-level gap and MUST NOT
  fabricate a column list from a design or profiling document instead.
- **FR-015**: The module and its template MUST stay generic (Principle VII): the worked
  example (C086 / `retail_store_sales`) may appear only as a cited filled instance, never
  inlined into the template or a fixed section label; the module MUST resolve a generic
  `mappings/<table>/` and gold-migration path per table.
- **FR-016**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and
  `->`, no glyphs), and MUST use short repo-relative paths (Windows 260-char budget)
  (Principle IX).
- **FR-017**: This feature MUST ship as a Product Module in the read-only skill/template
  shape -- a skill under `.claude/skills/` plus a generic copy-me template under
  `templates/` -- with NO runtime executor code and NO `src/retail/rules/` entry, and
  NO new `retail check` rule id (the agent is the runtime; Collision-Avoidance
  Allocation).
- **FR-018**: The generated dictionary MUST be written to
  `mappings/<table>/consumer-data-dictionary.md` -- a table-co-located path under the
  table's mappings folder (ADR 0003/0004 co-location precedent) that is distinct from
  the handoff pack's data-dictionary section and from any F028 evidence-pack file name,
  so it never collides with or overwrites either.
- **FR-019**: When the gold migration SQL and `source-map.yaml` disagree on a column's
  presence or name, the module MUST record the discrepancy as an explicit gap rather than
  silently preferring one source.

### Key Entities

- **Consumer Data Dictionary**: the derived, per-table, plain-language document this
  module writes. Composed only from committed artifacts; owns no meaning of its own;
  carries no score; every entry cites its source.
- **Gold column entry**: one row per deployed gold-star column, its committed meaning
  (verbatim-cited or gap), and its source path.
- **Metric entry**: one row per metric contract under `mappings/<table>/metrics/`,
  carrying forward `formula_intent` and the contract's recorded `readiness.status`.
- **Gap marker**: an explicit, named record that a column or metric has no committed
  consumer-facing meaning available -- never filled with invented prose. Minimum shape
  (see Clarifications 2026-07-04 Q3): a greppable label (e.g. `GAP:`), the column or
  metric identifier, and the repo-relative path(s) checked and found missing/unreadable.
- **Gold migration SQL**: the committed DDL (`warehouse/migrations/*_create_gold_*.sql`)
  that is the authoritative, static source of the deployed gold star's columns
  (Principle VIII: static, not a live catalog read).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An analyst can obtain, in one generated artifact, a plain-language
  reference for every deployed gold column and every metric contract of one table,
  without opening `source-map.yaml`, individual `metrics/*.yaml` files, or the handoff
  pack directly.
- **SC-002**: 100% of entries in a generated dictionary resolve to a committed
  repo-relative source path; 0 entries state a meaning, status, or value not present in
  a committed source.
- **SC-003**: 0 generated dictionaries contain a numeric confidence/health/maturity score
  or a completeness count.
- **SC-004**: 0 generated dictionaries write to, append to, or modify any upstream
  source artifact, the handoff pack, or any readiness-status file (the module is
  verifiably read-only apart from writing its own dictionary).
- **SC-005**: The same module, with only the table identifier changed, produces a
  correct dictionary for at least two differently-shaped mapped tables that have each
  reached Gold Ready.
- **SC-006**: 0 generic artifacts (template, fixed section labels) contain a
  worked-example (C086/`retail_store_sales`) domain specific.
- **SC-007**: 100% of gold columns with no committed consumer-facing or mapping-
  rationale meaning are recorded as an explicit gap, never as invented prose (0
  fabricated definitions).

## Assumptions

- `warehouse/migrations/*_create_gold_<table>*.sql` (the committed gold migration SQL)
  is the authoritative, static source of a table's deployed gold-star columns; the
  module reads it rather than a live database catalog (Principle VIII) or an
  aspirational design document.
- `mappings/<table>/source-map.yaml` remains the canonical source of a gold column's
  committed mapping rationale (ADR co-location precedent); the module reads the table's
  filled copy and does not re-implement or re-decide any mapping decision.
- `mappings/<table>/metrics/*.yaml` remains the canonical source of a measure's approved
  business meaning (`formula_intent`) and readiness status (spec 009/010 precedent); the
  module reads it read-only.
- This module is docs/skill/template only (the agent is the runtime, per the F025-F028
  precedent); it adds no runtime executor and no new `retail check` rule.
- The exact roadmap F-number for this feature is assigned at plan time via a
  roadmap-ledger edit; this spec does not invent one (063 precedent).
- The dictionary is an OPTIONAL companion artifact: it is never a required Publish
  Ready (or any other stage) gate section, and its absence never produces a
  `blocking_reasons[]` entry.
- Live reconciliation of the dictionary's column list against the actually-deployed
  database schema is OUT OF SCOPE for this feature (Principle VIII; deferred until a
  live-capable adapter such as F016/dashboard-design's live checks is invoked
  separately); a gold-migration-vs-source-map disagreement is recorded as a static gap,
  not resolved by a live query.
- Whether the module may generate a simplified paraphrase of a column's existing
  technical source-map rationale, or must always fall back to verbatim-cite-or-gap, is
  an OPEN Principle-V question (FR-008; Clarifications 2026-07-04 Q1) left for a named
  human to rule on; this spec does not assume an answer.
- The output path (FR-018) is a reversible naming/placement choice, not a Principle-V
  question; `mappings/<table>/consumer-data-dictionary.md` follows the same
  table-co-location convention F028/F035 already use and avoids colliding with the
  handoff pack or any evidence-pack file name.

## Clarifications

<!-- Principle-V carve-out questions recorded here for a human ruling; the workflow is
     forbidden to answer these. Session answers to non-Principle-V ambiguities are added
     under a dated session heading by /speckit-clarify. -->

### Session 2026-07-04

**Q1 (FR-008, business-meaning-authoring) -- OPEN, owner ruling required.** Q: When a
gold column's only committed meaning is a TECHNICAL source-map `reason` (written for the
mapping-gate reviewer, not a report reader), may the module GENERATE a simplified,
consumer-plain paraphrase of that rationale (e.g. turning "the grain key; unique on the
data -> degenerate dim on the fact (RC14)" into "a unique identifier for each
transaction"), or must it always fall back to FR-008's verbatim-cite-or-gap behavior
(quote the `reason` as recorded, or mark an explicit gap, never a generated gloss)? This
is retail-kpi/data-owner territory (Principle V: the agent must not decide business
meaning or its acceptable degree of simplification) and is NOT resolved by this
clarification pass. Until a named human rules, the module MUST apply the
verbatim-cite-or-gap behavior (FR-008, as amended). Owner: retail-kpi / data-owner
(named human TBD at plan/approval time). Not decided here.

Advisor-resolved (non-Principle-V) ambiguities, highest Impact*Uncertainty first. Each was
decided against the constitution, the readiness spine, and this repo's existing
FR-018/FR-013 style of reversible, docs-only defaults:

- **Q2 (document ordering -- FR-001)**: Q: FR-001 requires an "ordered" document but never
  defines the order. What order? A (Default adopted): gold column entries in the column
  definition order of the committed gold migration SQL, followed by metric entries in the
  filename order (lexical) of `mappings/<table>/metrics/*.yaml`. Reasoning: both orderings
  are already-committed, deterministic, static artifacts (Principle VIII); using them
  avoids inventing a new business-relevance ranking (which would itself be a Principle-V
  call) and keeps regeneration byte-stable for a fixed source state. Reversible: easy (a
  presentation choice, no data). Touches: FR-001.
- **Q3 (gap marker shape -- FR-008/FR-014/FR-019)**: Q: FR-008, FR-014, and FR-019 all
  require an "explicit gap" but never define its minimum shape, risking three different
  ad hoc formats. A (Default adopted): every gap marker carries a greppable label (e.g.
  `GAP:`), the column or metric identifier it concerns, and the repo-relative path(s) that
  were checked and found missing/unreadable/disagreeing. Reasoning: SC-007 requires gaps
  to be recorded "as an explicit gap, never as invented prose," and FR-007 requires every
  entry to cite a source path; a labeled, path-citing marker satisfies both without adding
  any new field to an upstream artifact. Reversible: easy (a template formatting choice).
  Touches: FR-008, FR-014, FR-019, Key Entities ("Gap marker").
- **Q4 (metric inclusion scope -- FR-004/FR-006 vs. User Story 1 Acceptance Scenario 1)**:
  Q: User Story 1's Acceptance Scenario 1 said the dictionary lists "every metric contract
  whose `readiness.status` is `pass`," which reads as pass-only, while FR-004, FR-006, and
  the "metric contract exists but is not `pass`" edge case all require enumerating and
  clearly marking pending (non-`pass`) contracts too -- an internal contradiction. A
  (Default adopted): list every metric contract file found under
  `mappings/<table>/metrics/*.yaml` (approved and pending alike), each clearly marked with
  its own recorded `readiness.status`; Acceptance Scenario 1 is corrected to describe this
  as the general case rather than a pass-only filter. Reasoning: FR-006's own text ("a
  metric whose status is not `pass` MUST be clearly marked as not yet approved, never
  presented as if it were") only makes sense if non-`pass` contracts are included at all;
  silently dropping them would also contradict User Story 2 Acceptance Scenario 3 (an
  unreadable/missing contract must still produce a gap entry, not a silent drop).
  Reversible: easy (a scope clarification resolved by re-reading the spec's own
  requirements, not a new policy). Touches: User Story 1 Acceptance Scenario 1, FR-004,
  FR-006.
- **Q5 (gold-column-to-source-map join basis -- FR-005/FR-003, User Story 2 Acceptance
  Scenario 2)**: Q: FR-005 requires citing "the column's committed... meaning from
  `mappings/<table>/source-map.yaml`... for that column," and User Story 2 Acceptance
  Scenario 2 names "a surrogate key generated in the gold migration itself" as one case
  with no corresponding source-map entry, but the spec never states the matching key a
  gold column name is looked up by, and this is not always 1:1: in the worked example,
  `gold.dim_date_rss` columns `month_name`, `day_name`, and `is_weekend` are produced by
  the RC15 `generate_series` calendar logic and have NO `source-map.yaml` column entry at
  all -- distinct from the already-covered surrogate-key case. An unstated join basis
  risks naive positional or fuzzy name matching, which could misattribute one column's
  `reason` to a different column, or fabricate a false gap for a column whose meaning is
  recorded under a different key. A (Default adopted): the module matches a gold column
  to its source-map entry by the source-map's own recorded `source_name` (fact/degenerate
  -dim columns) or by the `gold_star` dimension's listed attribute name (dimension
  attributes), never by position or fuzzy string matching; any gold column with no such
  matching record -- surrogate keys and RC15 calendar-derived `dim_date` attributes alike
  -- falls through to FR-008's verbatim-cite-or-gap/gap behavior. Reasoning: both
  `source_name` and the `gold_star` attribute lists are already-committed, deterministic,
  static fields (Principle VIII); defining the join key this way is a mechanical
  disambiguation, not a business-meaning/PII/grain judgment call, so it is a Principle-VI
  default rather than a Principle-V open question. Reversible: easy (a lookup-key
  definition, not a data or policy change). Touches: FR-005, User Story 2 Acceptance
  Scenario 2.
