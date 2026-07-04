# Feature Specification: Cross-Table Column-Level Lineage / Impact Analysis

**Feature Branch**: `099-cross-table-lineage-impact`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #6. Cross-table column-level lineage / impact analysis -- a
read-only lineage artifact derived from committed artifacts (source-map -> migration SQL ->
metric contract -> TMDL measure -> dashboard visual). Enables #2 (scope what to re-review on
drift) and turns the Net-Sales paper-trace into a generated artifact."

## Overview

Seshat BI can already answer "does this ONE source drift from its own profile" (F014 / spec
015, Source Ready) and "what does this ONE KPI derive from, conceptually, inside the contract
layer" (spec 044, KPI Derivation-Lineage). Neither answers the question a table owner actually
asks the moment a column changes: **"if `bronze.<schema>.<table>.<column>` changes shape or
disappears, which migrations, metric contracts, TMDL measures, and dashboard visuals sit
downstream of it, and how far does the chain actually reach before it runs out of committed
evidence?"** Today that question is answered by hand -- `docs/demo/net-sales-end-to-end-
readiness-trace.md` proves it can be done for exactly one KPI, on paper, by a human reading five
different artifact families in sequence (KPI contract, required fields, gold table/SQL, TMDL
measure, dashboard usage) and citing each hop. That trace is real evidence the hand-off is
coherent, but it is a one-off prose document: it does not generalize to any other column or
table, and nothing regenerates it when the underlying artifacts change.

This feature defines a read-only Product Module that DERIVES a column-level lineage graph from
already-committed artifacts -- a table's `source-map.yaml`, the silver/gold migration SQL under
`warehouse/migrations/`, the table's metric contracts (`mappings/<table>/metrics/*.yaml`), the
committed TMDL measures under `powerbi/*.SemanticModel/definition/tables/*.tmdl`, and any
committed dashboard visual-to-contract binding (per the dashboard-design skill's binding map) --
and renders it as one traceable artifact per starting column or per starting KPI. It generalizes
the Net-Sales trace's shape (evidence tiers, hop-by-hop citation, "what is proven" vs "what is
not proven") into a repeatable, generic template instead of a hand-authored prose document. It
answers "what depends on this column" (forward/downstream lineage) and, by the same graph, lets
a reader scope "what would need re-review if this column drifted" -- but it never re-runs drift
detection itself and never decides what MUST be re-reviewed; it only shows the reachable set so a
human can decide.

The module derives evidence only. It does not execute SQL, does not open a database connection,
does not run DAX, does not compute or assert a blast-radius score, a completeness count, or a
confidence/health/maturity value (hard rule #9), and does not create a lineage edge that no
committed artifact already records. A hop with no committed downstream artifact yet (for
example: a table with metric contracts but no TMDL measure, or a measure with no dashboard
binding yet) is a recorded GAP in the chain, never a fabricated edge and never treated as an
error -- most tables are mid-journey through the seven readiness stages, and partial chains are
the normal case (as the Net-Sales trace itself shows for its own Step 8 dashboard-usage hop).

## Boundary against neighbouring shipped work (read first)

This feature is a genuine EXTENSION of lineage-adjacent ideas already ratified or shipped, not a
restatement of any of them. Four close neighbours must stay distinct:

- **Spec 044 KPI Derivation-Lineage Contract** (`specs/044-kpi-derivation-lineage/`, ratified,
  no runtime code) authors a `Derives from` PROSE section inside each metric contract plus a
  hand-authored lineage reference doc, describing METRIC-TO-METRIC conceptual derivation (which
  KPI's formula reuses which other KPI, e.g. Net Sales derives from Gross Sales and Discount
  Amount) inside the DEFINE/reasoning layer. This feature does not touch contract prose and does
  not declare or transcribe metric-to-metric derivation edges at all; it derives a PHYSICAL,
  cross-ARTIFACT chain (column -> SQL -> contract -> measure -> visual) by reading structural
  references already present in committed YAML/SQL/TMDL/binding files, generated as an artifact,
  not authored as prose. Spec 044's edges are a reasoning-layer input this feature may cite at
  the contract hop; this feature never edits, re-derives, or second-guesses a 044 `Derives from`
  edge.
- **F014 Source Drift Detector** (spec 015, shipped) DETECTS that one source's shape or
  semantics has drifted from its own recorded profile, and turns that into Source Ready
  evidence/blockers. This feature does not detect drift and does not run any comparison against
  a baseline profile. It is the DOWNSTREAM-SCOPING half of the same idea: given a column F014
  already flagged (or a column a human is about to change), this feature shows what commits to
  the readiness chain sit downstream of it, so a reviewer knows what to re-check. It ENABLES
  F014's aftermath; it does not re-implement F014's comparison logic and emits no drift finding
  of its own.
- **F012 Data Quality Control Room** (spec 013, shipped) is also a cross-table, read-only
  aggregator, but it rolls up DATA-QUALITY findings and blockers across tables (the "worst
  first" triage view credited in ADR 0004 with the cross-table roll-up role). This feature
  aggregates LINEAGE EDGES, not DQ findings -- a different evidence category entirely. It does
  not read or restate Control Room's findings, and Control Room does not gain a lineage view
  from this feature; the two remain independent read-only aggregators over different source
  material.
- **The Net-Sales end-to-end readiness trace** (`docs/demo/net-sales-end-to-end-readiness-
  trace.md`, shipped) is the single hand-authored PROOF that the hand-off chain is coherent for
  exactly one KPI. This feature GENERALIZES that trace's shape into a generic, regeneratable
  template usable for any column or KPI; it supersedes nothing (the existing trace stays
  committed as the original proof-of-concept) and does not retro-edit that file.
- **OpenLineage** was evaluated and explicitly DEFERRED in ADR 0013 ("column-level lineage ...
  emitter, not a gated reader; external-service boundary; duplicates F014"). This feature is not
  a revival of that evaluation: it is a static reader over already-committed repository text
  (Principle VIII, static-first), never a running emitter, never a client of an external lineage
  backend, and it adds no new runtime service or dependency.

This feature adds NO new readiness stage and NO new `retail check` rule -- per the collision-
avoidance allocation, it is a Product Module (read-only skill under `.claude/skills/`) plus a
generic lineage template under `templates/`, not a governance rule (no rule-id is claimed). It
needs a NEW roadmap F-number in the Product Module series (after the highest-numbered shipped
Product Module); the exact number is a roadmap-ledger edit recorded at plan time, not invented
here (matching the spec 044 / spec 063 precedent of not self-assigning a number).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader traces one column's downstream reach (Priority: P1)

An analyst is about to change (or has just been told F014 flagged drift on) one column of a
mapped source table. Before touching anything, they ask for the lineage/impact view for that
`schema.table.column`. They receive one ordered artifact that walks the chain forward: which
source-map row consumes the column, which silver/gold migration SQL references it, which metric
contract(s) depend on the resulting gold column, which TMDL measure(s) reference that contract,
and which dashboard visual(s), if any, bind to that measure -- each hop citing the exact
committed file and line/anchor it came from. Where a hop has no committed downstream artifact
yet, the artifact records that as a gap, not a stop.

**Why this priority**: This is the feature's whole reason to exist -- replace "grep five folders
by hand" with one generated, evidence-cited answer to "what depends on this column." Without it
the feature delivers nothing.

**Independent Test**: For a column that is referenced in a committed source-map, a migration
file, a metric contract, and a TMDL measure, generating the lineage artifact for that column
produces an ordered chain whose every hop cites a committed repo-relative path, with no hop
asserting a downstream link that no cited artifact contains.

**Acceptance Scenarios**:

1. **Given** a column present in `mappings/<table>/source-map.yaml`, referenced in a committed
   `warehouse/migrations/*.sql` file, consumed by a metric contract, and summed by a TMDL
   measure, **When** the lineage artifact is generated for that column, **Then** the artifact
   lists all four hops in order, each citing its source path.
2. **Given** the same column has no committed dashboard visual binding yet, **When** the
   artifact is generated, **Then** the dashboard hop is recorded as an open gap ("no committed
   visual binding found"), not as an error and not as an invented visual reference.
3. **Given** the artifact is generated, **When** it is inspected, **Then** it contains no
   numeric blast-radius score, no "N artifacts affected" count, and no confidence/health/
   maturity value.

---

### User Story 2 - A reader traces one KPI's full chain, mirroring the Net-Sales precedent
(Priority: P1)

A metric owner wants the same proof the Net-Sales trace gave for Net Sales, but for a different
KPI or a different table, without hand-writing a new prose document. They ask for the lineage
artifact starting from a metric contract rather than a raw column. They receive an artifact
structured like the Net-Sales trace (business meaning cited, required fields, gold table/SQL,
DAX measure, dashboard usage, each tiered by evidence strength) but generated from the current
committed state of the repository rather than hand-authored.

**Why this priority**: This is the explicit "turn the Net-Sales paper-trace into a generated
artifact" mandate; a KPI-rooted trace is the natural counterpart to the column-rooted trace in
User Story 1 and proves the module generalizes beyond one hand-picked KPI.

**Independent Test**: Generate the lineage artifact for a metric contract other than Net Sales
that has at least a committed contract and a TMDL measure; the artifact cites both hops from
committed paths and does not require a hand-authored prose file to exist.

**Acceptance Scenarios**:

1. **Given** a metric contract `mappings/<table>/metrics/<Metric>.yaml` with a `Grain`/
   `Formula intent` and a same-named TMDL measure, **When** the lineage artifact is generated
   starting from that contract, **Then** it cites the contract file and the TMDL measure file as
   the two proven hops.
2. **Given** the same contract has no upstream committed migration SQL reference resolvable from
   the source-map, **When** the artifact is generated, **Then** the upstream hop is recorded as
   a gap naming what is missing, not silently omitted.
3. **Given** the artifact is generated for the Net Sales contract itself, **When** it is
   compared against `docs/demo/net-sales-end-to-end-readiness-trace.md`, **Then** the generated
   artifact's cited hops are consistent with (not contradicting) the hand-authored trace's cited
   evidence.

---

### User Story 3 - The same module scopes "what to re-review" without deciding it
(Priority: P2)

A reviewer has a column or contract that is about to change. They use the lineage artifact's
downstream set as the CANDIDATE list of what to re-review, then apply their own judgment (or a
separate drift-detector run) to decide what actually needs re-work. The module never states that
an item "must be re-reviewed," "is broken," or "is at risk" -- it states only that the item is
reachable in the downstream set, with its own evidence citation.

**Why this priority**: This is the "enables #2" half of the feature's stated purpose; it is a
direct, low-cost consequence of User Stories 1/2's graph rather than new derivation, so it is
P2.

**Independent Test**: Generate a lineage artifact for a column with three downstream hops; the
artifact's downstream set names exactly those three items with citations, and no accompanying
recommendation, priority, or risk label is present anywhere in the output.

**Acceptance Scenarios**:

1. **Given** a lineage artifact with a downstream set of contracts and measures, **When** it is
   inspected, **Then** it contains no verb of obligation ("must", "should", "needs to") applied
   to a downstream item -- only "is downstream of" / "cites" language.
2. **Given** a reviewer reads the downstream set, **When** they decide what to re-check, **Then**
   that decision is made outside the artifact (by the reviewer or a separate drift-detector run)
   -- the artifact supplies the candidate set only.

---

### Edge Cases

- What happens when the requested starting column does not appear in any committed
  `source-map.yaml`? The artifact records that the starting point itself is unresolved (a
  blocker naming the missing source-map row), and does not fabricate a plausible chain from it.
- What happens when a metric contract references a column by a business-friendly name that does
  not textually match the gold column name (no explicit `derives_from`/field-reference the
  module can resolve)? The hop is recorded as an UNRESOLVED / candidate link (see FR-010) rather
  than asserted as a proven edge, and is never silently dropped or silently promoted to proven.
- What happens when two different TMDL measures in different `*.SemanticModel/` model folders
  both reference the same gold column? Both are surfaced as separate downstream hops; the
  artifact does not pick one arbitrarily.
- What happens when the table has not yet passed Mapping Ready (no approved source-map) or Gold
  Ready (no migration SQL)? The chain starts wherever committed evidence exists and records the
  earlier, missing stages as gaps -- it never implies a stage is `pass` because an artifact for
  it happens to exist on disk unreviewed.
- What happens when the same lineage artifact is regenerated after an artifact it cited changes
  (for example, a TMDL measure is renamed)? The regenerated artifact reflects the current
  committed state; it carries no memory of the prior run and makes no claim about what changed
  (that comparison is F014 drift detection's job, not this module's).
- What happens when a dashboard visual binds to a measure via the dashboard-design skill's
  binding map but the underlying PBIR page is still an empty scaffold (per the F034 precedent)?
  The visual hop is surfaced as committed (the binding record exists) with its own evidence tier,
  never conflated with a claim that the visual is built or published.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The module MUST accept a starting point that is either a `schema.table.column`
  identifier or a metric contract identifier (`mappings/<table>/metrics/<Metric>.yaml`) and
  produce exactly one ordered lineage/impact artifact for that starting point.
- **FR-002**: The module MUST read only already-committed artifacts. It MUST NOT connect to a
  database, execute SQL, run DAX, open a live Power BI/PBIP surface, or invoke any deferred
  execution adapter (F016) or spec-only runtime (F031-F033).
- **FR-003**: The artifact MUST trace, in a fixed forward order, the chain: source-map entry ->
  silver/gold migration SQL reference -> metric contract -> TMDL measure -> dashboard visual
  binding -- surfacing each hop that has a committed artifact and recording as a gap each hop
  that does not.
- **FR-004**: Every hop the artifact reports as part of the chain MUST cite the exact committed
  repo-relative path (and, where the source format supports it, an anchor/line or YAML key) it
  was read from; the module MUST NOT assert a hop for which no committed artifact is cited.
- **FR-005**: The module MUST NOT create, infer-and-assert, or silently invent a lineage edge
  that no committed artifact already records. Where the linkage between two artifacts (for
  example a metric contract's plain-English field name and a gold column) cannot be resolved to
  an explicit committed reference, the module MUST record it as an UNRESOLVED / candidate link
  distinct from a proven hop (see FR-010), never merge the two.
- **FR-006**: The artifact MUST NOT compute or emit any numeric blast-radius score, "N artifacts
  affected" completeness count, or confidence/health/maturity value (hard rule #9). Impact is
  expressed only as the named SET of downstream hops plus their evidence citations and gaps.
- **FR-007**: The artifact MUST NOT contain a verb of obligation ("must", "should", "needs to",
  "requires re-review") applied to any downstream item. It states reachability and evidence
  only; deciding what to re-review is a human/reviewer action outside the artifact (Principle V
  -- the module never decides business/technical priority on the human's behalf).
- **FR-008**: When a required upstream or downstream artifact is missing, unreadable, or a blank
  template, the module MUST record it as an explicit GAP naming the missing/unreadable path,
  distinguished from an UNRESOLVED candidate link (FR-005/FR-010) and from a proven hop; it MUST
  NOT fabricate the artifact's content.
- **FR-009**: The module MUST NOT move any readiness stage, grant any approval, define or
  approve any business meaning (metric, mapping, rollup, segment, grain, PII ruling), or write
  back to any source artifact it reads -- these remain named-human / Core Authority / owning-
  skill actions (Principle V; F024 forbidden-operations matrix). The module is read-only apart
  from writing its own generated lineage artifact.
- **FR-010**: [NEEDS CLARIFICATION -- OPEN owner ruling, see Clarifications: What resolution
  method, if any, is authorized for the contract<->gold-column and TMDL-measure<->contract hops
  when no explicit machine-readable cross-reference field exists in either committed artifact
  (for example: matching a contract's business-friendly required-field name against a gold
  column name, or matching a TMDL measure name against a contract's title)? Name-similarity
  matching risks asserting an edge a human has not declared (the same Principle-V line spec 044
  drew for metric-to-metric derivation). Until a human rules on an authorized matching method and
  its confidence handling, the module MUST treat any such link as UNRESOLVED / candidate-only
  (never proven) and MUST NOT silently auto-accept a name match as a hop. This fail-safe
  (candidate-only, never proven, no silent auto-accept) is already binding regardless of how the
  owner ruling resolves; the OPEN question is narrowly whether ANY matching method may ever be
  authorized to promote a candidate toward proven, and if so, under what evidence/confidence
  handling -- it does not block shipping FR-010's candidate-only behavior as specified.]
- **FR-011**: The module and its template MUST stay generic (Principle VII): the worked example
  (C086 / retail_store_sales, including the Net-Sales trace) may appear only as a cited filled
  instance, never inlined into the template or a fixed section label; the module MUST resolve a
  generic `schema.table.column` or `mappings/<table>/metrics/<Metric>.yaml` starting point.
- **FR-012**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no
  glyphs), and MUST use short repo-relative paths (Windows 260-char budget) (rule IX).
- **FR-013**: This feature ships as a Product Module in the read-only shape (per the F025/F026
  precedent) -- a skill under `.claude/skills/` plus a generic copy-me lineage template under
  `templates/` -- and adds NO runtime executor code and NO `src/retail/rules/` entry (the agent
  is the runtime; it adds no gate and claims no rule-id).
- **FR-014**: The generated artifact MUST be written to a table-co-located, starting-point-named
  path so a generated lineage artifact never collides with another table's or another starting
  point's artifact, and so the artifact is independently regeneratable without manual merge.
  Default adopted (see Clarifications; reversible, plan may confirm or deviate): the artifact is
  written to `mappings/<table>/lineage-column-<column>.md` when the starting point is a
  `schema.table.column` identifier, or `mappings/<table>/lineage-metric-<Metric>.md` when the
  starting point is a metric contract identifier -- co-located per the existing
  `mappings/<table>/` convention (matching how `reconciliation-report.md` and
  `unresolved-questions.md` already co-locate there) rather than a repo-level `docs/lineage/`
  index. The `column`/`metric` root-type token in the filename is load-bearing: it is what
  prevents a column and a metric contract that happen to share a name from colliding on the same
  path.
- **FR-015**: When the starting point itself cannot be resolved against any committed
  source-map or metric contract, the module MUST record that as a top-level blocker naming the
  unresolved starting identifier and MUST NOT proceed to fabricate a downstream chain from it.
- **FR-016**: The artifact MUST distinguish, per hop, at least three evidence states mirroring
  the Net-Sales trace's tiering: a PROVEN hop (committed artifact cites the link explicitly), an
  UNRESOLVED/candidate hop (artifacts exist on both sides but the link between them is not an
  explicit committed reference), and a GAP (no committed downstream artifact exists yet at that
  hop) -- so a reader can tell proof apart from inference apart from absence.

### Key Entities

- **Lineage/Impact Artifact**: the derived, ordered document this module writes for one starting
  point (a column or a metric contract). Composed from committed evidence; owns no truth; carries
  no score.
- **Starting point**: either a `schema.table.column` identifier or a
  `mappings/<table>/metrics/<Metric>.yaml` contract identifier that anchors the traced chain.
- **Hop**: one stage in the fixed chain order (source-map entry, migration SQL reference, metric
  contract, TMDL measure, dashboard visual binding), each carrying an evidence state (proven /
  unresolved / gap) and a citation to its committed source path where one exists.
- **Downstream set**: the ordered collection of hops reachable forward from the starting point;
  the candidate list a reviewer may choose to re-check, without the artifact itself prescribing
  that choice.
- **Gap**: a recorded absence of a committed downstream (or upstream) artifact at a given hop;
  distinct from an error and distinct from an unresolved candidate link.
- **Unresolved / candidate link**: a hop where committed artifacts exist on both sides but no
  explicit machine-readable cross-reference connects them; never promoted to a proven hop by
  this module.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can obtain, for a given column or metric contract, one artifact that
  shows the full forward chain of committed downstream artifacts, replacing a manual multi-
  folder search with one generated document.
- **SC-002**: 100% of hops an artifact marks PROVEN cite a committed repo-relative path; 0
  PROVEN hops assert a link that no cited artifact contains.
- **SC-003**: 0 generated artifacts contain a numeric blast-radius score, an "N artifacts
  affected" completeness count, or a confidence/health/maturity value.
- **SC-004**: 0 generated artifacts contain a verb of obligation ("must"/"should"/"needs to")
  applied to a downstream item.
- **SC-005**: 0 generated artifacts write to, modify, or append to any artifact this module
  reads (the module is verifiably read-only apart from writing its own generated artifact).
- **SC-006**: The same module, given the Net Sales metric contract as its starting point,
  produces an artifact whose cited hops do not contradict
  `docs/demo/net-sales-end-to-end-readiness-trace.md`'s cited evidence.
- **SC-007**: 0 generic artifacts (template, fixed section labels) contain a worked-example
  (C086/pharmacy/retail_store_sales) domain specific outside a cited-instance example.

## Assumptions

- `mappings/<table>/source-map.yaml`, `warehouse/migrations/*.sql`,
  `mappings/<table>/metrics/*.yaml`, and the committed TMDL under
  `powerbi/*.SemanticModel/definition/tables/*.tmdl` are the four upstream-to-mid-chain artifact
  families already established by shipped features (F006/F007 mapping, retail-build-warehouse
  SQL, F009 metric contract store, F010 semantic model readiness); this module reads them
  read-only rather than re-defining their shape.
- A dashboard visual-to-contract binding record (as produced by the dashboard-design skill's
  binding map, F011/F012 lineage) is the fifth, final-hop artifact family this module reads when
  present; when a table has not yet reached Dashboard Ready, this hop is a recorded gap, not an
  error.
- `docs/demo/net-sales-end-to-end-readiness-trace.md` is the reference shape (evidence tiers,
  hop-by-hop citation) this module's output style follows, but it is not retro-edited or
  superseded by this feature; it remains the original hand-authored proof-of-concept.
- Spec 044's `Derives from` contract-prose edges are a citable input at the metric-contract hop
  when a chain happens to pass through a derived KPI, but this module does not re-derive,
  validate, or extend spec 044's metric-to-metric graph.
- This module is docs/skill/template only (the agent is the runtime, per the F025-F028/F035
  Product Module precedent); it adds no runtime executor and no new `retail check` rule.
- The new roadmap F-number is assigned at plan time via a roadmap-ledger edit; the spec does not
  invent one.
- Reverse (upstream-only) lineage queries, a graphical/visual rendering of the lineage graph, and
  any live-database cross-check of a proven hop are OUT OF SCOPE for this feature; this feature
  is strictly the static, forward, artifact-derived chain.

## Clarifications

### Session 2026-07-04

- **Q (FR-010)**: What resolution method, if any, is authorized for the contract<->gold-column
  and TMDL-measure<->contract hops when no explicit machine-readable cross-reference field exists
  in either committed artifact (e.g., matching a contract's business-friendly field name against
  a gold column name, or a TMDL measure name against a contract title)?
  **Resolution**: OPEN owner ruling. This is a genuine Principle-V line, the same one spec 044
  drew for metric-to-metric derivation: authorizing any name-similarity method to promote a
  candidate link toward "proven" would let the module assert an edge no human declared, which is
  creating truth -- forbidden by this feature's SCOPE GUARD. No default is adopted. The
  `[NEEDS CLARIFICATION]` marker in FR-010 stays in place, reframed to point here, until a named
  human rules on whether any matching method may ever be authorized and, if so, its confidence
  handling. This OPEN status does NOT block shipping the feature: FR-010's fail-safe behavior
  (treat every such link as UNRESOLVED / candidate-only, never proven, never silently
  auto-accepted) is already fully specified and is what ships absent a ruling. The owner ruling
  only widens or narrows that default in the future; it never loosens it silently.
  **Touches**: FR-010 (and the UNRESOLVED/candidate-link definition under Key Entities, FR-005,
  FR-016).

- **Q (FR-014)**: What exact output path convention should the generated lineage artifact use, so
  it never collides with another table's or another starting point's artifact?
  **Resolution**: Default adopted (Principle VI defaults-then-deviations; reversible docs/naming
  choice, not a Principle-V question). The artifact is written to
  `mappings/<table>/lineage-column-<column>.md` (column-rooted) or
  `mappings/<table>/lineage-metric-<Metric>.md` (metric-rooted), co-located under the table's
  existing `mappings/<table>/` folder alongside `reconciliation-report.md` and
  `unresolved-questions.md`, rather than a repo-level `docs/lineage/` index. The `column`/`metric`
  root-type token is the collision-avoidance mechanism the requirement calls for: it keeps a
  column and a metric contract that happen to share a name from writing to the same path. This
  default may be confirmed or deviated from at plan time alongside the roadmap F-number
  assignment; it is not re-litigated as a Principle-V question.
  **Touches**: FR-014.

- **Q**: FR-002/FR-004 and the Overview repeatedly say the module reads "already-committed
  artifacts," but the spec never pins whether that means the artifact at the last `git commit`
  (a specific ref) or the current on-disk working-tree state of the same tracked files.
  **Resolution**: Default adopted (Principle VI defaults-then-deviations; Principle VIII
  static-first -- this module is a static reader over repository TEXT, not a git-history tool).
  "Committed" means the current on-disk working-tree content of the tracked repo files the module
  reads (`source-map.yaml`, `warehouse/migrations/*.sql`, `mappings/<table>/metrics/*.yaml`,
  `*.SemanticModel/definition/tables/*.tmdl`, the binding-map instance) -- i.e., whatever a
  reviewer would see by opening those files right now, matching how `retail check` and the other
  read-only skills in this repo (retail-govern, retail-semantic-check) already read state. It is
  NOT a `git show <ref>:<path>` history lookup, and it does not require a clean git status or a
  specific commit to run against. This is a reversible docs/behavior default, not a Principle-V
  question (no grain/PII/policy/approval is at stake).
  **Touches**: FR-002, FR-004, Overview.

- **Q**: The dashboard visual hop cites "the dashboard-design skill's binding map," but the spec
  does not name the concrete generic template path or where a table's filled instance is expected
  to live, leaving an implementer to guess which file the module actually opens.
  **Resolution**: Default adopted (Principle VI defaults-then-deviations; reversible reference
  detail, not a Principle-V question). The generic shape is
  `templates/visual-contract-binding-map.md` (per the dashboard-design skill's own "See also"
  list); a table's FILLED instance is read wherever the dashboard-design skill has already
  committed it for that table. This module does not define, relocate, or standardize that filled
  instance's path -- it is read-only against whatever the dashboard-design skill produces, and if
  no filled instance exists yet for a table, the dashboard-visual hop is recorded as a GAP
  (per FR-008), never fabricated. This default may be confirmed or refined at plan time once the
  dashboard-design skill's committed per-table output path is inspected; it does not block
  shipping FR-003's fixed hop order.
  **Touches**: FR-003, Assumptions (dashboard visual-to-contract binding record).
