# Feature Specification: Row-Level Security as a Semantic-Model-Ready Dimension

**Feature Branch**: `092-rls-access-readiness`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #3 -- Row-Level Security as a Semantic-Model-Ready
dimension. Add a role/RLS contract (like a metric contract) + a static check that
declared roles carry a filter expression binding to a real dim column, wired into
Semantic Model Ready."

## Overview

The Semantic Model Ready gate (`docs/readiness/semantic-model-ready.md`, Stage 5)
today defines "ready" purely in terms of measures: every measure traces to an
APPROVED metric contract, relationships are set, the date table is marked, and
`retail check` passes the DAX/TMDL + connection rules. Row-level security (RLS) --
which role filters restrict which rows a Power BI viewer can see -- appears in the
repo in exactly two places, and only as a CAUTION, never as a governed artifact:
`docs/medallion-playbook.md` ("never rely on row-level security to hide a *column*")
and `docs/decisions/0002-retail-cleaning-defaults.md` (RC4, the same caution). Neither
document defines what a valid RLS role looks like, requires one to exist, or checks
that a declared role actually filters anything. A PBIP model can therefore reach
`semantic_model_ready: pass` -- every measure approved, `retail check` green -- while
carrying zero RLS roles, or carrying a role whose filter expression is blank, refers
to a column that does not exist in `gold`, or was quietly typo'd into a no-op. The
gate has no way to notice. A "ready" model can leak every store's, every branch's, or
every customer's numbers to every viewer, and nothing in the readiness spine records
that risk as evidence.

This feature closes that gap the same way F009 closed the missing-metric-contract
gap: it defines a GENERIC, reviewable DECLARATION artifact (a role/RLS contract,
modeled on `templates/metric-contract.yaml`'s shape) that a human author fills per
role, and it adds ONE new static `retail check` rule (reserved id **HR6**) that
verifies, for each DECLARED role, that a filter expression is present and that the
expression names a column that actually exists on a real `gold` dimension table. The
rule is wired into the Semantic Model Ready gate as an additional blocking condition,
the same way D1-D11 (DAX/TMDL) and G6 (no real host) already are. Both the contract
and the rule are STATIC ONLY: nothing here executes a role, evaluates a filter
against data, opens a database connection, or renders a "logged in as role X" preview
(F016's future concern, and out of scope even then per this feature's guard). Most
importantly, this feature never decides WHO should see WHAT -- that is a Principle V
governance ruling reserved for a named human. It only makes the DECLARATION
reviewable and checks that the declaration is internally well-formed.

## Boundary against neighbouring shipped work (read first)

This feature adds a NEW, independent artifact and a NEW, independent rule. It must
stay distinct from these shipped neighbours:

- **F009 metric-contract.yaml / metric-contract-store** (`templates/metric-contract.yaml`,
  `docs/metrics/metric-contract-store.md`) defines a MEASURE's binding (a metric name
  -> a `gold` fact/dim column, owned and approved by a metric owner). This feature
  defines a ROLE's binding (a role name -> a filter expression -> a `gold` DIMENSION
  column, owned and approved by a governance/security owner). The two contracts share
  a declare-bind-approve SHAPE (by deliberate convention, mirroring F009's
  identity/binds_to/readiness sections) but are separate concerns on separate rows of
  data: a metric answers "what does this number mean", a role answers "which rows may
  this viewer see". Per the collision-avoidance allocation, this feature MUST NOT add
  keys to `templates/metric-contract.yaml` -- it ships a wholly separate file,
  `templates/rls-role-contract.yaml`.
- **F010 / retail-semantic-check (Stage 5 checker)** (`.claude/skills/retail-semantic-check/`,
  on-disk feature 011) computes the Semantic Model Ready verdict by checking that
  every measure traces to an approved metric contract, plus the existing D1-D11 /
  C1 / R1 / G6 `retail check` rules. This feature ADDS ONE MORE input to that same
  verdict (the HR6 rule's result) -- it does not replace, re-run, or duplicate F010's
  measure-to-contract check, and it does not re-implement retail-semantic-check's
  read-only invoke-and-interpret pattern; it plugs into the existing gate the same
  way G6 already does.
- **retail-govern / `retail check`** (`src/retail/rules/`) is the existing static
  rule runner (each rule self-registers with `@register("ID", "description")`, e.g.
  `g6.py` registers `G6`). This feature adds exactly one new rule module registering
  **HR6** to that runner; it does not touch, rename, or renumber any existing rule id,
  and it reserves HR6 so no other in-flight feature collides on the id.
- **Row-level PII guidance (RC4 / medallion-playbook 2.2)** already tells an author
  "do not rely on RLS to hide a column; drop or mask PII instead." This feature does
  not change or re-litigate that guidance -- it operates one layer up, on whatever
  roles an author DOES declare, regardless of why. It does not adjudicate whether a
  given role/column pairing is the RIGHT security boundary (Principle V; see Scope
  Guard below); it only checks that a declared role is not a hollow, no-op
  declaration.
- **F016 (Power BI execution adapter, gated + last)** would be the only place a role
  filter is ever actually EVALUATED against live data or previewed ("view as role").
  This feature assumes F016 does not exist yet and never simulates, executes, or
  approximates what F016 would do; the HR6 check is static structure only (Principle
  VIII).

## Scope Guard (non-negotiable)

- This feature MUST NOT define, recommend, or default WHO sees WHAT -- which roles
  should exist, which viewers map to which role, or which column is the "correct"
  security boundary for a given table. That is a named-human governance ruling
  (Principle V) recorded outside this feature's artifacts.
- This feature MUST NOT execute anything: no DAX evaluation, no live PBIP read, no
  database connection, no "view as role" simulation.
- This feature is DECLARATION + STATIC BIND-CHECK only: a human-authored contract
  file, and a rule that verifies the contract's shape and its column reference
  against the committed gold schema -- nothing more.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A declared role with no real filter binding fails the gate (Priority: P1)

A table's PBIP model already has every measure traced to an approved metric contract
and `retail check` is otherwise green. A security owner has authored one RLS role
contract for the model, but the filter expression field is blank, or it references a
column name that does not exist on any committed `gold` dimension table (a typo, a
renamed column, or a column that was later dropped). Today, nothing in the readiness
spine would notice; Semantic Model Ready could still read `pass`. With this feature,
running `retail check` fails closed with an HR6 finding naming the broken role and
the unresolvable column, and the Semantic Model Ready gate records HR6 as a blocking
reason -- the stage cannot reach `pass` while the finding stands.

**Why this priority**: This is the entire point of the feature -- a hollow or broken
RLS declaration must stop the gate the same way a hollow metric contract already
does. Without this, the feature delivers nothing (a role contract nobody checks is
just more unread documentation).

**Independent Test**: Author one `rls-role-contract.yaml` with a filter expression
that names a non-existent gold column (or an empty filter expression), run
`retail check`, and confirm an HR6 finding is emitted naming the role and the
unresolved column, with the finding recorded in the table's Semantic Model Ready
blocking reasons.

**Acceptance Scenarios**:

1. **Given** a filled `rls-role-contract.yaml` whose `filter.column` is empty,
   **When** `retail check` runs, **Then** it fails closed with an HR6 finding naming
   the role and stating the filter expression is missing.
2. **Given** a filled `rls-role-contract.yaml` whose `filter.column` names a column
   that does not exist on the referenced `gold` dimension table, **When**
   `retail check` runs, **Then** it fails closed with an HR6 finding naming the role,
   the referenced table, and the unresolved column.
3. **Given** an HR6 finding exists for a table's model, **When** the Semantic Model
   Ready status is read for that table, **Then** HR6 appears in `blocking_reasons[]`
   and the stage does not read `pass`.

---

### User Story 2 - A well-formed role contract binds cleanly and clears HR6 (Priority: P1)

The same security owner fixes the contract: the filter expression now names a column
that genuinely exists on a committed `gold` dimension table, the role has a name, and
the contract's readiness is recorded (not fabricated) as owner-approved. Running
`retail check` again shows HR6 passing for that role; the finding that was blocking
Semantic Model Ready is gone (all other Stage 5 conditions being already met).

**Why this priority**: A gate that can only fail is not trustworthy -- authors must
be able to reach a clean, positive state by doing the declaration correctly. This is
the other half of the same slice as User Story 1 and is required for the feature to
be usable at all, so it is also P1.

**Independent Test**: Point the same contract's `filter.column` at a column that is
confirmed present on the bound `gold` dimension table (via the committed gold
migration SQL), re-run `retail check`, and confirm no HR6 finding is emitted for that
role.

**Acceptance Scenarios**:

1. **Given** a filled `rls-role-contract.yaml` whose `filter.column` names a column
   that exists on the referenced `gold` dimension table, **When** `retail check`
   runs, **Then** no HR6 finding is emitted for that role.
2. **Given** all other Semantic Model Ready conditions already hold (measures traced
   to approved contracts, D1-D11/C1/R1/G6 clean) and HR6 now passes, **When** the
   Semantic Model Ready status is recomputed, **Then** HR6 no longer appears in
   `blocking_reasons[]`.
3. **Given** a role contract passes HR6, **When** the contract is inspected, **Then**
   it carries no numeric confidence/health score -- only the four explicit statuses
   plus evidence/blocking_reasons (hard rule #9).

---

### User Story 3 - HR6 flags a role contract that is present but never reviewed/approved (Priority: P2)

An author drops a filled-looking `rls-role-contract.yaml` into the mappings folder
with a plausible role name and a plausible-looking filter binding, but its
`readiness.status` is still `not_started` (no owner has reviewed it) or its
`readiness.evidence[]` is empty despite claiming `pass`. HR6 must not treat a
structurally-valid-looking file as an approved one; a contract that is well-formed
but unreviewed is still a blocking condition, and a `pass` with no evidence is a
defect the rule must catch.

**Why this priority**: This closes the "looks done but was never actually signed
off" loophole that a purely structural bind-check would miss. It matters, but the
core bind-check (P1) already delivers the primary value, so this hardening is P2.

**Independent Test**: Author a role contract with a well-formed filter binding but
`readiness.status: pass` and an empty `evidence[]`; run `retail check` and confirm
HR6 flags the missing evidence rather than accepting the unearned `pass`.

**Acceptance Scenarios**:

1. **Given** a role contract with `readiness.status: pass` and `evidence: []`,
   **When** `retail check` runs, **Then** HR6 emits a finding that a `pass` status
   requires non-empty evidence.
2. **Given** a role contract with `readiness.status: not_started`, **When**
   `retail check` runs, **Then** HR6 records that the role is not yet reviewed and
   the table's Semantic Model Ready stage does not treat that role as cleared.
3. **Given** a role contract with a well-formed binding and `readiness.status:
   blocked` with a non-empty `blocking_reasons[]`, **When** `retail check` runs,
   **Then** HR6 surfaces the recorded blocking reason rather than re-deciding it.

---

### Edge Cases

- What happens when a table's PBIP model has NO `rls-role-contract.yaml` at all
  (zero declared roles)? Whether the absence of any RLS declaration should BLOCK,
  WARN, or be silently allowed to PASS Semantic Model Ready is a governance policy
  decision (does every gold-backed model require at least one role, or is
  "no RLS needed" itself a valid, ownable state?) -- see FR-010. OPEN (owner ruling
  required -- Principle V; see Clarifications 2026-07-04); the agent MUST NOT
  default this to "pass" or "block" on its own authority.
- What happens when a role contract's filter expression binds to a column on a
  `gold` FACT table rather than a `gold` DIMENSION table? The contract template
  models RLS as filtering a conformed dimension (the Kimball pattern: a role filters
  `dim_store`, and the filter propagates to `fct_sales` via the relationship), so a
  fact-table binding is flagged by HR6 as a structural mismatch requiring the
  security owner to re-point it at the correct dimension, per FR-005. Default
  adopted (see Clarifications 2026-07-04): HR6 treats a fact-table binding as a
  hard failure (`Severity.ERROR`, blocking), not a warning -- Principle I requires a
  rule to fail closed rather than merely advise, and the leak-through direction
  (a fact-bound role silently slipping past) is the one this feature exists to
  prevent. A model with a genuine fact-grain "own records only" design is a
  Principle-V deviation an owner may later carve out explicitly; this feature does
  not invent or pre-approve that exception.
- What happens when two role contracts declare the same role `name`? HR6 flags the
  duplicate name as a defect (mirrors metric-contract's uniqueness rule) so the
  Semantic Model Ready evidence never carries two contradictory definitions of the
  same role.
- What happens when the referenced `gold` dimension table itself does not exist yet
  (Gold Ready is not `pass`)? HR6 records that the binding cannot be resolved because
  the prior stage is incomplete -- it is a blocking finding, not a silent pass,
  mirroring how the metric-contract binds_to check treats a missing gold column.
- What happens when the filter expression is present and points at a real column,
  but the column's data type cannot possibly express a row filter (e.g. a free-text
  comment column)? HR6 checks existence and non-emptiness only (Principle VIII,
  static-first); it does not evaluate whether the column is a SENSIBLE filter target
  -- that plausibility judgment is left to the human reviewer, not fabricated by the
  rule.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST define a new, generic, copy-me template,
  `templates/rls-role-contract.yaml`, modeled on the declare/bind/readiness shape of
  `templates/metric-contract.yaml`, that declares ONE Power BI RLS role per filled
  copy: a stable role `name`, a `filter` binding (the `gold` dimension table +
  column the role's filter expression restricts), and a `readiness` block using
  exactly the four explicit statuses (`not_started | blocked | warning | pass`) plus
  `evidence[]` and `blocking_reasons[]`.
- **FR-002**: `templates/rls-role-contract.yaml` MUST be a SEPARATE file from
  `templates/metric-contract.yaml`. The feature MUST NOT add, rename, or repurpose
  any key in `templates/metric-contract.yaml` or `templates/kpi-pack.yaml`.
- **FR-003**: The filled role contract's binding MUST reference the `gold` schema
  ONLY (Principle III); a contract binding to a `silver` or `bronze` object is a
  defect the static check MUST catch (mirrors FR-012 of the metric-contract
  template).
- **FR-004**: The feature MUST add exactly one new static `retail check` rule,
  registered under the reserved id **HR6**, that runs over every committed
  `rls-role-contract.yaml` under a table's mapping folder.
- **FR-005**: HR6 MUST fail (record a finding) when a role contract's filter binding
  is missing a column reference, is empty, or is blank.
- **FR-006**: HR6 MUST fail when a role contract's filter binding names a column
  that does not exist on the referenced `gold` table, verified against the committed
  gold migration SQL / schema definition (static structural check; no live database
  connection, per Principle VIII).
- **FR-007**: HR6 MUST fail when a role contract's filter binding references a
  `silver` or `bronze` table (Principle III boundary), or references a `gold` table
  that does not exist in the committed migrations at all.
- **FR-008**: HR6 MUST fail when a role contract records `readiness.status: pass`
  with an empty `evidence[]` (an unearned pass is a defect, mirroring the
  metric-contract precedent).
- **FR-009**: HR6 MUST fail when two or more committed role contracts declare the
  same `name` (duplicate role identity is a defect).
- **FR-010**: OPEN (owner ruling required -- Principle V; see Clarifications
  2026-07-04). The feature MUST record, as an explicit open question (not
  resolve), what the Semantic Model Ready gate does when a table has ZERO
  committed `rls-role-contract.yaml` files -- whether absence of any RLS
  declaration is a blocking condition, a warning, or an allowed pass state is a
  Principle V governance ruling; see Edge Cases. PENDING DEFAULT the owner may
  ratify: absence of any role contract is NOT silently treated as `pass` --
  HR6 records the zero-contract state as an explicit, visible fact (not a
  fabricated pass) until an owner either (a) declares roles for the model, or
  (b) records an explicit "no RLS needed, ruled by <owner>" decision outside this
  feature's artifacts. The agent MUST NOT default this to "pass" or "block" on
  its own authority, and this feature's own artifacts MUST NOT encode either
  answer as final.
- **FR-011**: When HR6 produces one or more findings for a table's committed role
  contracts, the Semantic Model Ready readiness computation (`retail-semantic-check`)
  MUST surface HR6's finding(s) in that table's `blocking_reasons[]`, the same way an
  existing D1-D11/G6 finding already blocks that stage -- this feature adds an input
  to the existing verdict, it does not replace F010's measure-to-contract check.
- **FR-012**: HR6 MUST NOT execute a filter expression, connect to a live database,
  or read a live PBIP/Power BI surface -- it verifies structure (presence, shape, and
  static existence of the referenced column) against already-committed text (the
  contract YAML and the committed gold SQL), and nothing else (Principle VIII).
- **FR-013**: The feature MUST NOT decide, recommend a default for, or auto-fill
  WHO should see WHAT: it MUST NOT choose which roles a model needs, which viewers
  map to a role, or which column is the "correct" security boundary for a table.
  Any such judgment is recorded as an open question for a named human (Principle V)
  and the feature's artifacts MUST NOT contain a filled-in answer to it.
- **FR-014**: The role contract template and the HR6 rule MUST NOT emit or require
  any numeric confidence/health/maturity score or a completeness count ("N of M");
  readiness is expressed only via the four explicit statuses plus `evidence[]` and
  `blocking_reasons[]` (hard rule #9).
- **FR-015**: The template and rule MUST stay generic (Principle VII): no C086 /
  retail_store_sales-specific role name, column name, or store/branch label may be
  inlined into `templates/rls-role-contract.yaml` or into the HR6 rule's own source;
  C086 may appear only as a cited filled instance elsewhere (e.g. a worked example
  under `docs/worked-examples/`), never as a hardcoded default.
- **FR-016**: All authored artifacts MUST be ASCII, UTF-8 without BOM (`--` and `->`,
  no glyphs), and MUST use short repo-relative paths respecting the Windows 260-char
  PBIP path budget (Principle IX).
- **FR-017**: `docs/readiness/semantic-model-ready.md` MUST be updated to list HR6
  alongside the existing D1-D11/C1/R1/G6 gate checks in its "Required checks" and
  "Blocking reasons" tables, so the gate documentation and the running rule stay in
  sync (mirrors how G6 is already documented there).
- **FR-018**: The feature MUST NOT introduce any live-database-backed check; a live
  verification that a role's filter actually restricts rows as intended is
  explicitly deferred (marked PENDING LIVE PROFILE / left to a future live-validate
  surface), consistent with Principle VIII (static-first, live-deferred).

### Key Entities

- **RLS role contract**: a filled copy of `templates/rls-role-contract.yaml`,
  co-located under `mappings/<table>/` (mirroring where metric contracts live),
  declaring one Power BI RLS role's name, its filter binding (`gold` dimension table
  + column), and its readiness state. Human-authored; never agent-filled.
- **Filter binding**: the `{gold_table, column}` pair a role's filter expression is
  claimed to restrict on. Declares intent to bind; does not itself carry the DAX/M
  filter expression's logic -- only which column it targets.
- **HR6 finding**: a static `retail check` finding raised when a role contract is
  missing its filter reference, references a non-existent or non-gold column,
  duplicates another role's name, or claims `pass` with no evidence.
- **Semantic Model Ready blocking reason (HR6-sourced)**: an entry in a table's
  `readiness-status.yaml` `semantic_model_ready.blocking_reasons[]` that traces back
  to a live HR6 finding; cleared only when the underlying contract is corrected and
  HR6 re-runs clean.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of committed `rls-role-contract.yaml` files with an empty or
  missing filter-column reference produce an HR6 finding when `retail check` runs.
- **SC-002**: 100% of committed `rls-role-contract.yaml` files whose filter column
  does not exist on the referenced `gold` table (per committed migration SQL)
  produce an HR6 finding.
- **SC-003**: 0 well-formed role contracts (real gold dimension column, non-empty
  evidence for any claimed `pass`, unique role name) produce an HR6 finding.
- **SC-004**: 0 HR6 findings, role contracts, or the HR6 rule's own source contain a
  numeric confidence/health/maturity score or an "N of M" completeness count.
- **SC-005**: 0 keys are added to `templates/metric-contract.yaml` or
  `templates/kpi-pack.yaml` by this feature (verifies the collision-avoidance
  allocation held).
- **SC-006**: `docs/readiness/semantic-model-ready.md`'s "Required checks" and
  "Blocking reasons" tables list HR6, so a reader of the gate doc and a reader of
  `retail check` output see the same rule set.
- **SC-007**: 0 generic artifacts (the template, the rule's own messages) contain a
  C086/pharmacy/retail_store_sales-specific role, column, or table name.

## Assumptions

- `templates/metric-contract.yaml`'s declare/bind/readiness shape (identity, a
  `binds_to`-style block, a four-status `readiness` block with `evidence[]` /
  `blocking_reasons[]`) is the right precedent to mirror for a role contract; this
  feature reuses the SHAPE, not the FILE.
- The committed gold migration SQL under the warehouse migrations directory is the
  authoritative, static source of truth for "does this gold column exist" -- HR6
  reads that committed text rather than a live database (Principle VIII). DEFERRED
  to plan (see Clarifications 2026-07-04): the exact parsing approach for
  extracting gold table/column names from migration SQL is an implementation
  detail for the plan stage, not a Principle-V question and not resolved here.
- RLS in this feature means Power BI's row-level security role/filter mechanism
  (TMDL `roles.tmdl` / role definitions with a table filter expression), consistent
  with how `docs/medallion-playbook.md` and ADR `0002-retail-cleaning-defaults.md`
  already use the term.
- A role contract is co-located under `mappings/<table>/` following the same
  co-location convention as metric contracts (ADR 0003 "cohesive per-table working
  set"); the exact filename pattern within that folder is an implementation detail
  left to the plan stage.
- This feature ships as a template + a `src/retail/rules/` static-check module
  (like G6), wired into the existing Semantic Model Ready gate computation; it adds
  no new readiness STAGE (the seven stages are unchanged) and no new top-level
  `retail check` command.
- Whether a model that legitimately needs no RLS at all should be required to
  record an explicit "no RLS needed, ruled by <owner>" declaration, versus silently
  passing with zero contracts, is NOT decided by this spec (see FR-010); it is
  carried forward as an open Principle-V question for the plan/implementation stage
  or a named human to rule on.

## Clarifications

<!-- Principle-V carve-out questions are recorded under their own subsection for a human
     ruling; the workflow is forbidden to answer these. Non-Principle-V ambiguities resolved
     with reasonable constitution-safe defaults (Principle VI) are recorded under the dated
     session subsection. -->

### Session 2026-07-04

Non-Principle-V ambiguities resolved against the constitution and the F009
metric-contract / F010 retail-semantic-check / G6 precedents already shipped in
this repo. One true who-sees-what governance question is left OPEN rather than
answered, per this feature's Scope Guard and Principle V.

- **C1 (fact-table binding severity -- Edge Cases / FR-005) -- Default adopted.**
  Q: When a role contract's filter binds to a column on a `gold` FACT table
  instead of a `gold` DIMENSION table, does HR6 hard-fail (`Severity.ERROR`,
  blocking) or merely warn (`Severity.WARNING`, non-blocking)? A: HR6 hard-fails.
  Reasoning: `src/retail/core.py` already defines a real `Severity.WARNING` tier
  used elsewhere in `src/retail/rules/`, so a warning tier was mechanically
  available -- this is a genuine rule-mechanics choice, not an architecture
  default. Principle I requires a rule to fail CLOSED rather than merely advise,
  and treating a fact-bound role as only a warning is exactly the leak-through
  direction this feature exists to close (a "ready" model could still leak rows
  while showing a merely-advisory finding). Hard-fail is therefore both the
  constitution-safe default and the conservative reading of the feature's own
  purpose. This default does NOT pre-approve or name any legitimate fact-grain
  "own records only" exception -- an owner may later carve one out explicitly
  (Principle V), but this feature does not invent or bless it (FR-013). Reversible:
  easy (a later spec can add an explicit, owner-named exception path without
  touching this feature's shape). Touches: Edge Cases (fact-table binding bullet),
  FR-005.

- **C2 (migration-SQL parsing approach -- Assumptions) -- DEFERRED to plan; not
  Principle-V.** Q: HR6 must verify a filter-bound column exists on a committed
  `gold` table by reading committed migration SQL rather than a live database
  (Principle VIII) -- what is the exact parsing approach (regex over `CREATE
  TABLE` / `ALTER TABLE` statements, a lightweight SQL parser, or reuse of an
  existing extractor already used by another rule)? A: not resolved here -- this
  is an implementation-mechanics question for the plan stage, not a governance
  judgment call; the spec only fixes the CONTRACT (committed gold migration SQL is
  the authoritative static source of truth) and leaves HOW HR6 reads it to
  planning, consistent with how F009's own binds_to-column check is implemented.
  Touches: Assumptions (gold-migration-SQL-as-source-of-truth bullet).

- **C3 (dim-vs-fact table detection -- FR-005/FR-006) -- Default adopted.** Q: How
  does HR6 mechanically decide whether a referenced `gold` table is a DIMENSION
  (`dim_*`) or a FACT (`fct_*`) for the purposes of C1's hard-fail check, without
  adding a new key anywhere? A: HR6 reads the `dim_`/`fct_` table-name prefix
  convention already fixed by this repo's SQL conventions
  (`docs/conventions.md`: schemas `bronze`/`silver`/`gold`, `vw_`/`fct_`/`dim_`
  prefixes) against the committed gold migration SQL identified for C2 -- no new
  naming convention or metadata key is introduced. Reasoning: the convention is
  already constitution-fixed and repo-wide; reusing it costs nothing and avoids
  inventing a second classification mechanism. Reversible: easy. Touches: FR-005,
  FR-006.

- **C4 (role-contract filename pattern -- Assumptions) -- Default adopted.** Q:
  What is the exact filename (or filenames, for multiple roles) a filled
  `rls-role-contract.yaml` copy takes under `mappings/<table>/`? A: mirror the
  co-location convention already used for metric contracts under
  `mappings/<table>/` (ADR 0003 "cohesive per-table working set"); a single role
  per file, one file per role, so two roles never collide inside one YAML
  document and HR6's duplicate-name check (FR-009) can run per-file across the
  folder. The exact literal filename token (e.g. a `rls-role-<name>.yaml` pattern
  vs. a fixed `rls-role-contract.yaml` name reused across multiple copies in
  differently-named directories) remains an implementation detail confirmable at
  plan/template time -- this default only fixes that it is co-located,
  one-role-per-file, and discoverable by a folder scan, not a specific token.
  Reversible: easy. Touches: Assumptions (co-location bullet), Key Entities (RLS
  role contract).

### Principle-V carve-out (OPEN -- owner ruling required; the workflow is forbidden to answer)

- **Q-ZERO-ROLES (FR-010) -- OPEN owner ruling.** Q: What does the Semantic Model
  Ready gate do when a table has ZERO committed `rls-role-contract.yaml` files --
  is the absence of any RLS declaration a blocking condition, a warning, or an
  allowed pass state? This is a who-sees-what / governance-policy decision
  (Principle V): it amounts to deciding whether every gold-backed model is
  REQUIRED to carry at least one governed role, which the agent MUST NOT settle on
  its own authority. RECORDED PENDING DEFAULT the owner may ratify: absence of any
  role contract is NOT silently treated as a `pass` -- HR6 (or the Semantic Model
  Ready computation reading HR6's evidence) surfaces the zero-contract state as an
  explicit, visible fact rather than fabricating a clean pass, until a named owner
  either declares the roles a model needs or records an explicit "no RLS needed,
  ruled by <owner>" decision. Until the owner rules, this feature's own artifacts
  (the template and the HR6 rule's source) MUST NOT encode either "pass" or
  "block" as the final, shipped answer. Touches: FR-010, Edge Cases (zero-roles
  bullet), Assumptions (final bullet).
