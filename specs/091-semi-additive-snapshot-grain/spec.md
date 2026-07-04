# Feature Specification: Semi-Additive (Snapshot) Grain in the Metric Contract

**Feature Branch**: `091-semi-additive-snapshot-grain`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "gap #5. Semi-additive (snapshot) grain in the metric contract -- extend
templates/metric-contract.yaml with an explicit time_additivity field (fully/semi/non additive over
the date axis) plus a static check that a snapshot-grain fact's measures declare it."

## Overview

Every metric contract shipped in this repo today describes a TRANSACTION fact (retail_store_sales:
one row = one sale line). A transaction measure summed across dates is correct -- gross sales for a
month is the SUM of daily gross sales. That is fine. It also means every contract that exists is
silently, coincidentally "fully additive over time," and nothing in the schema has ever had to say
so out loud.

The gap surfaces the moment a SNAPSHOT fact enters the picture -- the canonical retail example is
inventory on-hand quantity, captured as a state at a point in time rather than a flow of events
(`skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md`, "Semi-additive"; the same
knowledge layer's ambiguities ledger already names this exact trap as **A10 -- Inventory snapshot
date**, `skills/retail-kpi-knowledge/knowledge/kpi-ambiguities.md`). A snapshot measure is additive
across products and branches at a single date, but summing it ACROSS dates silently produces a
number with no real-world meaning (an "inventory total" for a month that is actually the sum of
365 different point-in-time counts). None of the four explicit readiness statuses, none of the
existing contract fields (`grain`, `binds_to`, `readiness`, `ambiguities`), and no existing static
check (`retail check`) reads or requires a date-axis additivity declaration. A snapshot-grain
contract can reach `readiness.status: pass` today with every existing gate green while carrying a
wrong-by-construction time rollup -- the gate has no vocabulary to even ask the question.

This feature closes that gap with the smallest possible surface: one new schema field,
`time_additivity`, on `templates/metric-contract.yaml` (top-level, alongside `grain` and
`readiness`), classifying a metric's additivity specifically over the DATE axis
(fully | semi | non), plus one new static `retail check` rule (reserved id **HR5**) that ERRORs when
a contract already flagged as snapshot-adjacent -- via the existing, human-authored A10 ambiguities-
ledger entry -- does not carry a `time_additivity` declaration, or declares one the closed
vocabulary does not recognize, or declares `fully` while still carrying an undecided A10 entry. The
field and the rule ask a human to say the date-axis word out loud when the ledger has already
flagged the trap; they never decide what the word should be.

## Boundary against neighbouring shipped work (read first)

This feature is a narrow, DATE-AXIS-ONLY schema addition, not a restatement of the shipped
additivity machinery. One shipped neighbour must stay distinct, and two in-flight siblings share
this feature's file but not its field:

- **AD1 -- additivity-consistency lineage rule** (spec 068,
  `src/retail/rules/additivity_consistency.py`) already ERRORs when a metric's additivity
  CLASSIFICATION is composed illegally with its derivation-lineage parents/children (a ratio child
  summed directly by a parent; a semi-additive component poisoning a plain-SUM parent). AD1 reads
  its classification and lineage edges from committed DEFINE-LAYER PROSE
  (`skills/retail-kpi-knowledge/contracts/*.md`), by its own explicit design choice (068
  Clarifications Q2) and its own recorded Assumptions/Dependencies note: AD1 "introduces no new
  machine-readable contract field as part of this feature (adding a structured field would be a
  separate, larger define-layer change)." This feature IS that separate change -- but only for the
  date axis, and only on the deployable per-table contract
  (`mappings/<table>/metrics/*.yaml`), never on the prose corpus AD1 reads. AD1's "additivity
  classification" is a whole-metric composition class (can this metric be validly summed from its
  stated parents/children, any dimension); this feature's `time_additivity` is narrower and
  orthogonal -- one measure's behavior specifically when summed ACROSS DATES, independent of any
  derivation lineage. A metric can be AD1-legal in composition and still need `time_additivity: semi`
  if it is a snapshot. This feature does not read, write, or duplicate AD1's legality table, and
  does not touch `skills/retail-kpi-knowledge/contracts/*.md`.
- **AL1 / AL2** (specs 059/-, `src/retail/rules/assumptions.py`,
  `assumption_coherence.py`) are the sibling contract-reading rules this feature's HR5 clones the
  shape of (generic glob over `mappings/*/metrics/*.yaml`, template + test-path exemption, lazy
  `import yaml`, fail-loud on unreadable, ERROR-only, never-resolves). HR5 does not read or alter
  AL1/AL2's own trigger fields (`readiness.status`/`blocking_reasons`, decided/undecided
  `ambiguities[]` rulings); it adds a new, independent trigger keyed on the presence of an A10
  ambiguities-ledger entry.
- **Parallel metric-contract adders (092, 103) -- collision avoidance, not a boundary of shipped
  work.** Three features extend `templates/metric-contract.yaml` in the same working set: this
  feature (091) adds the top-level key `time_additivity`; 092 (RLS roles) adds a SEPARATE contract
  file, not a key on this template; 103 (unit/currency) adds its own, differently-named key. This
  feature touches ONLY the `time_additivity` key and must not rename, restructure, or add any other
  top-level key to `templates/metric-contract.yaml`.

This feature adds NO new readiness stage. HR5 is OFF-SPINE, exactly like AD1/AL1/AL2: it advances no
7-stage gate and grants no approval; it only reads committed contracts and returns findings via the
`retail check` exit code.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A snapshot-flagged contract must declare its date-axis additivity (Priority: P1)

A metric owner authors a contract for an inventory on-hand measure and records the known snapshot
trap by adding an `id: A10` entry to the contract's `ambiguities[]` list (the existing ledger
mechanism for "Inventory snapshot date"). They do not add a `time_additivity` field, or they add one
but set it to `fully`. When `retail check` runs, HR5 ERRORs, naming the contract and stating that a
contract carrying an A10 entry must declare `time_additivity` as `semi` or `non` -- never `fully` --
because a snapshot fact is, by the knowledge layer's own settled definition, never fully additive
over time.

**Why this priority**: This is the entire point of the gap being closed -- today this exact contract
passes every gate silently. Without this check, a snapshot measure with an undeclared or wrong
date-axis additivity ships to the semantic model and gets naively SUMmed across dates by the DAX
layer with no warning anywhere in the readiness pipeline.

**Independent Test**: Author a fixture contract carrying an `ambiguities: [{id: A10, ...}]` entry and
no `time_additivity` field, run `retail check`, and confirm exactly one HR5 ERROR naming that
contract. Add `time_additivity: semi` to the fixture and confirm the finding clears. Set
`time_additivity: fully` on the same A10-flagged fixture and confirm HR5 still ERRORs (a snapshot
contract may never self-declare fully additive).

**Acceptance Scenarios**:

1. **Given** a contract with an `ambiguities[]` entry whose `id` is `A10` and no `time_additivity`
   field, **When** `retail check` runs, **Then** HR5 emits an ERROR naming that contract and stating
   the missing date-axis declaration.
2. **Given** the same contract with `time_additivity: fully` added, **When** `retail check` runs,
   **Then** HR5 still emits an ERROR (a snapshot-flagged contract cannot be fully additive over
   time).
3. **Given** the same contract with `time_additivity: semi` (or `non`) added, **When** `retail check`
   runs, **Then** HR5 emits no finding for that contract.

---

### User Story 2 - Absent or out-of-vocabulary values are refused, never inferred (Priority: P1)

A contract declares `time_additivity` using a value outside the closed three-word vocabulary
(`fully`, `semi`, `non`) -- for example a free-text sentence, a typo, or a numeric placeholder. HR5
must not guess which of the three words was intended; it ERRORs that the value is unrecognized and
takes no further action on that contract. Likewise, a contract with no A10 entry and no
`time_additivity` field at all is NOT an error (the field is optional unless the A10 trigger fires) --
HR5 must not require every contract in the repo to declare a date-axis additivity, only the ones the
ledger has already flagged.

**Why this priority**: The same safety framing that makes AD1 ratifiable applies here -- act only on
exact committed words, never infer a classification, never widen the trigger beyond what a human
already flagged. If HR5 either guessed a value or fired on every contract in the repo, it would
smuggle in a grain judgment (Principle V) or make every transaction contract in the repo carry dead
weight it does not need.

**Independent Test**: Author a fixture with an A10 entry and `time_additivity: "sometimes"` (outside
the vocabulary); confirm HR5 ERRORs that the value is unrecognized, distinct from the missing-field
message. Author a second fixture with no A10 entry and no `time_additivity` field at all; confirm HR5
emits zero findings for it.

**Acceptance Scenarios**:

1. **Given** an A10-flagged contract whose `time_additivity` value is not one of `fully`/`semi`/`non`,
   **When** `retail check` runs, **Then** HR5 emits an ERROR that the value is unrecognized and infers
   nothing.
2. **Given** a contract with no A10 entry in `ambiguities[]` and no `time_additivity` field, **When**
   `retail check` runs, **Then** HR5 emits no finding for that contract.
3. **Given** a contract with no A10 entry but a `time_additivity` field present anyway (an owner
   volunteering the declaration early), **When** `retail check` runs, **Then** HR5 validates only
   that the value, if present, is in the closed vocabulary -- it does not require the field and does
   not treat its presence as an error.

---

### User Story 3 - The rule is wired in and counted like every other rule (Priority: P2)

The new rule appears in the rule registry, the expected-rule-id set, the authoritative rules
manifest, and the severity-posture manifest, so the wiring meta-gate and the rule-count reconciler
agree the rule count advanced by exactly one (reserved id **HR5**).

**Why this priority**: A registered rule that is not fully wired fails the shipped wiring checklist
(five places, per the AD1/AL1 precedent). Required to ship at all, but mechanical relative to the
rule's logic (P1).

**Independent Test**: Run the rule-wiring unit test and confirm the actual registered rule ids equal
the expected set (now including `HR5`) and the manifest count matches.

**Acceptance Scenarios**:

1. **Given** the new rule module is registered and all five wiring points updated, **When** the
   wiring unit test runs, **Then** actual rule ids equal expected rule ids and the manifest count
   equals the length of that set.

---

### Edge Cases

- **No contracts on disk, or no contract carries an A10 entry**: HR5 finds nothing to check and emits
  zero findings (clean pass) -- matching the current committed corpus, which is entirely
  transaction-grain and carries no A10 entry today (a genuine zero-findings baseline, not a
  suppressed one).
- **Template and test fixtures**: `templates/metric-contract.yaml` itself and any test-path fixtures
  are exempt from scanning, matching the AL1/AD1 exemption seam.
- **A contract carries A10 among several `ambiguities[]` entries, not as the only one**: HR5 fires on
  the presence of any entry whose `id` is `A10`, regardless of position or of the `decision_status`
  of other unrelated entries in the same list.
- **A10 entry is `decision_status: decided`**: the snapshot trap being decided (a human ruled on the
  snapshot policy) does not exempt the contract from declaring `time_additivity` -- the two fields
  answer different questions (business snapshot POLICY vs. schema-level date-axis additivity
  CLASSIFICATION); HR5 still requires the declaration and still rejects `fully`.
- **A tracked-but-unreadable contract file**: HR5 fails loud with an ERROR naming the unreadable path,
  never silently skips (matching the AL1 fail-loud-on-unreadable seam).
- **A non-inventory fact that is nonetheless semi-additive over time** (e.g., a running/cumulative
  balance): the A10 ambiguities-ledger id is titled "Inventory snapshot date" specifically. For THIS
  build, HR5's trigger is scoped to the existing A10 id only (see FR-018); whether a future
  non-inventory semi-additive case ever needs its own ledger id or a widened trigger remains
  [NEEDS CLARIFICATION -- resolved to OPEN owner ruling, see ## Clarifications Q4: this is a
  retail-kpi-knowledge ledger-scope decision the agent cannot settle, not a schema-field decision, and
  it is out of scope for this build regardless of how it is eventually answered].
- **`ambiguities[]` id-match casing**: an entry whose `id` field is written `a10` (lowercase) or
  `A10-inventory` (a near-miss token) rather than the exact literal `A10` does NOT trigger HR5 -- see
  `## Clarifications` for the adopted default and FR-004a.
- **`time_additivity` value casing/whitespace**: a value that differs from the closed vocabulary only
  by case or surrounding whitespace (e.g. `Fully`, `semi `, `NON`) is treated as out-of-vocabulary, not
  silently normalized to the matching word -- see `## Clarifications` and FR-002a.
- **`time_additivity` present but null/empty on an A10-flagged contract**: an explicit `time_additivity:`
  key with no value (YAML null) or an empty string is treated the same as the field being absent (the
  FR-004 missing-field finding), not as an out-of-vocabulary value (FR-006) -- see `## Clarifications`
  and FR-004b.
- **`time_additivity` present as a non-scalar** (a list or mapping instead of a string): HR5 treats this
  as out-of-vocabulary (FR-006) and ERRORs; it MUST NOT raise an unhandled parser exception -- see
  `## Clarifications` and FR-006a.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `templates/metric-contract.yaml` MUST gain one new, OPTIONAL top-level field named
  exactly `time_additivity`, positioned alongside the existing `grain` and `readiness` fields, with
  authoring commentary matching the template's existing documentation style (a comment block
  explaining the field, its closed vocabulary, and a link/citation to
  `skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md`).
- **FR-002**: The `time_additivity` field, when present, MUST hold exactly one of three values:
  `fully`, `semi`, or `non` (lowercase, matching the vocabulary style of the template's other
  enum-like fields). Any other value is out-of-vocabulary.
- **FR-002a**: The vocabulary match in FR-002 MUST be an exact, case-sensitive, untrimmed string
  comparison against the literal words `fully`, `semi`, `non`. A value differing only by case or by
  leading/trailing whitespace (e.g. `Fully`, `SEMI`, `non `) is out-of-vocabulary (FR-006), never
  silently normalized to the intended word (Default adopted; see `## Clarifications`).
- **FR-003**: The field MUST express classification ONLY -- it MUST NOT carry a DAX expression, a SQL
  statement, a business-rollup rule, or any restatement of what "semi-additive" means in business
  terms. The field cites the existing knowledge-layer definition; it does not redefine it (retail-kpi
  owns the KPI meaning per Principle V and this feature's scope guard).
- **FR-004**: A new static `retail check` rule, reserved id **HR5**, MUST read committed contracts
  under the generic glob `mappings/*/metrics/*.yaml` (excluding `templates/metric-contract.yaml`
  and test-path fixtures, matching the AL1/AD1 exemption seam) and MUST ERROR when a contract's
  `ambiguities[]` list contains an entry whose `id` is `A10` AND the contract's `time_additivity`
  field is absent.
- **FR-004a**: The `id` match in FR-004 MUST be an exact, case-sensitive string equality against the
  literal `A10` -- not a substring, prefix, or case-insensitive match. An entry such as `a10` or
  `A10-inventory` does NOT trigger HR5 (Default adopted; see `## Clarifications`). This mirrors
  AL1/AD1's own exact-token reading of committed human-authored fields.
- **FR-004b**: A `time_additivity` field that is present but holds a YAML null (an empty `time_additivity:`
  key) or an empty string MUST be treated identically to the field being absent (the FR-004
  missing-field finding), not as an out-of-vocabulary value under FR-006 (Default adopted; see
  `## Clarifications`).
- **FR-005**: HR5 MUST ERROR when an A10-flagged contract's `time_additivity` is present but equals
  `fully` -- a contract that has itself flagged the inventory-snapshot trap can never validly declare
  full additivity over time (per the knowledge layer's settled definition of semi-additive).
- **FR-006**: HR5 MUST ERROR when a contract's `time_additivity` value is present but is not one of
  the three closed-vocabulary words (FR-002), regardless of whether the contract carries an A10
  entry, and MUST NEVER infer or default a value to make the check pass.
- **FR-006a**: If `time_additivity` is present as a non-scalar YAML node (a list or a mapping) rather
  than a string, HR5 MUST treat it as out-of-vocabulary under FR-006 and ERROR; it MUST NOT raise an
  unhandled parser/type exception (Default adopted; see `## Clarifications`).
- **FR-007**: HR5 MUST NOT fire on a contract that carries no A10 entry and no `time_additivity`
  field -- the field is optional for any contract the ledger has not flagged; HR5 MUST NOT require
  every contract in the repo to carry a date-axis declaration.
- **FR-008**: HR5 MUST NOT read, alter, or duplicate AD1's additivity-composition legality table or
  AD1's define-layer prose corpus (`skills/retail-kpi-knowledge/contracts/*.md`); its entire read
  surface is the deployable per-table `metric-contract.yaml` copies plus the fixed A10 vocabulary
  word already defined in `skills/retail-kpi-knowledge/knowledge/kpi-ambiguities.md`.
- **FR-009**: HR5 MUST emit findings ONLY at the ERROR severity (categorical pass/ERROR). It MUST NOT
  emit a numeric score, a confidence value, a threshold band, or any graded/numeric output (No-Fake-
  Confidence, hard rule #9).
- **FR-010**: HR5 MUST NOT execute DAX, MUST NOT open any database or network connection, and MUST
  NOT render or evaluate any visual or PBIP surface. It is a pure static YAML read (Static-First
  Governance, Principle VIII).
- **FR-011**: HR5 MUST advance no readiness stage and grant no approval. It is off-spine, exactly like
  AD1/AL1/AL2: it only reads committed contracts and returns findings via the `retail check` exit
  code.
- **FR-012**: HR5 MUST be wired into all five required places so the wiring meta-gate and rule-count
  reconciler agree: the registry module import block and export list, the expected-rule-id set in
  the wiring unit test, the authoritative rules manifest (regenerated), and the severity-posture
  manifest/golden fixture (regenerated). The rule count MUST advance by exactly one (`HR5`).
- **FR-013**: On a corpus with no contracts, or with contracts that carry no A10 entry, HR5 MUST emit
  zero findings (clean pass) rather than erroring -- matching the current committed corpus.
- **FR-014**: A tracked contract file that is unreadable MUST cause HR5 to fail loud with an ERROR
  naming the unreadable path, never silently skip it (matching the AL1 fail-loud-on-unreadable seam).
- **FR-015**: This feature MUST NOT redefine, narrow, or restate what "semi-additive" or "fully
  additive" MEANS in business terms -- that vocabulary and its retail meaning belongs to
  `skills/retail-kpi-knowledge/` (Principle V / this feature's scope guard). `time_additivity` is a
  schema slot for a human to name that already-defined classification against one contract; the
  field and rule never choose the value on a contract's behalf.
- **FR-016**: The `time_additivity` addition and HR5 MUST stay generic (Principle VII): no C086 /
  retail_store_sales / pharmacy-specific value, metric name, or grain key may appear inlined in the
  template comments or in HR5's source; the worked example may only be cited as a filled instance.
- **FR-017**: All authored artifacts (template diff, rule module, docs) MUST be ASCII, UTF-8 without
  BOM (`--` and `->`, no glyphs), and MUST use short repo-relative paths (Windows 260-char budget)
  (Principle IX).

*Marker requiring human ruling before build (do not answer during automated planning):*

- **FR-018**: For THIS build, HR5's trigger is the existing A10 ambiguities-ledger id ONLY -- this part
  is decided and not open. Whether detection of a snapshot-grain trap should EVER extend beyond A10 --
  for example to a future non-inventory semi-additive-over-time shape (a cumulative/YTD balance) that
  carries no A10 entry -- remains
  [NEEDS CLARIFICATION -- resolved to OPEN owner ruling, see ## Clarifications Q4: this is a
  retail-kpi-knowledge ledger-scope decision (would the knowledge layer add a new ambiguity id, or
  should a future rule's trigger widen to a different signal), not a schema-field decision this build
  can resolve or a decision this workflow may make on its own authority; OUT OF SCOPE for this build
  regardless of the eventual answer, which triggers on the existing A10 id only].

### Key Entities

- **`time_additivity` field**: a new, optional, top-level scalar on `templates/metric-contract.yaml`
  and every filled copy under `mappings/<table>/metrics/*.yaml`, classifying one metric's additivity
  specifically over the DATE axis using the closed vocabulary `fully | semi | non`. Human-authored;
  the rule reads it, never writes or infers it.
- **A10 ambiguities-ledger entry**: the existing, human-authored `ambiguities[]` list entry (id
  `A10`, "Inventory snapshot date") that flags a contract as touching the known snapshot trap. HR5's
  sole detection trigger; unchanged by this feature.
- **HR5 finding**: a categorical ERROR (never a score) naming an offending contract and the specific
  missing/illegal/unrecognized date-axis declaration, surfaced for a human metric owner to resolve.
  Never a fix, never an inferred value.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the current committed corpus (no contract carries an A10 entry today), HR5 produces
  zero findings -- a genuine clean baseline, not a suppressed one.
- **SC-002**: Given a fixture contract with an A10 entry and no `time_additivity` field, HR5 emits
  exactly one ERROR naming that contract; adding `time_additivity: semi` (or `non`) to the same
  fixture clears the finding to zero.
- **SC-003**: Given the same A10-flagged fixture with `time_additivity: fully`, HR5 emits exactly one
  ERROR (a snapshot-flagged contract can never validly declare full time-additivity).
- **SC-004**: Given a fixture whose `time_additivity` value is outside the closed vocabulary, HR5
  emits exactly one ERROR distinguishable from the missing-field finding (unrecognized value, not
  absence).
- **SC-005**: The registered rule-id set equals the expected rule-id set including `HR5`, and the
  rules manifest count equals the length of that set (rule count advanced by exactly one); every
  wiring golden test passes.
- **SC-006**: HR5 emits no numeric score, confidence value, or threshold in any finding, and performs
  no execution (no DAX, no connection, no visual) -- verifiable by inspecting outputs and by the
  rule module remaining stdlib-only at import time (lazy YAML parser import).
- **SC-007**: Zero generic artifacts (the template diff, HR5's source, its docstring) contain a
  worked-example (C086/retail_store_sales/pharmacy) domain specific.

## Assumptions

- `skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md` and
  `kpi-ambiguities.md` (A10) remain the authoritative source of what "semi-additive over time" MEANS
  and of the A10 ambiguity id's existence and wording; this feature cites them and adds no competing
  definition.
- The existing `ambiguities[]` schema block on `templates/metric-contract.yaml` (id, decision_status,
  ruling, evidence, number_moving) is unchanged by this feature; HR5 only reads the `id` field of
  each entry to detect A10, and does not gate on `decision_status`.
- AD1 (spec 068, `src/retail/rules/additivity_consistency.py`) and its define-layer prose corpus are
  unmodified by this feature; the two rules are independent and may both fire on the same contract
  for unrelated reasons.
- HR5 clones the AL1/AD1 scaffold: lazy `import yaml`, generic contract glob, template + test-path
  exemption, fail-loud on unreadable, ERROR-only, never-resolves. No new parsing library is
  introduced.
- No deferred capability is assumed: no Power BI execution adapter (F016), no spec-only runtime, no
  live database connection. HR5 is a static text read only (add the seam, not an executor).
- The two other in-flight metric-contract adders (092 rls_roles as a separate contract file; 103
  unit/currency as a differently-named key) do not collide with this feature's `time_additivity` key;
  this feature adds and touches only that one key.
- Extending the detection trigger beyond the existing A10 id (FR-018) is out of scope for this build
  and is left to a human ruling recorded at a later date.

## Clarifications

### Session 2026-07-04

Four underspecified points were found. Three are mechanical parsing forks with a
constitution-safe DEFAULT adopted (Principle VI); one is a genuine Principle-V ledger-scope
judgment call left OPEN for a named human owner.

- **Q1 -- Is the A10 `id` match in FR-004 exact, or does it also catch near-miss casing/tokens
  (`a10`, `A10-inventory`)?** Decision: Default adopted -- exact, case-sensitive string equality
  against the literal `A10` only. A near-miss token does not trigger HR5. Rationale: HR5's whole
  design contract (Assumptions; FR-008) is that it transcribes an existing human-authored signal
  without ever guessing what a human meant; fuzzy-matching `a10` or `A10-inventory` as "probably
  A10" would be exactly the kind of inference FR-006 already forbids for the vocabulary side, just
  relocated to the trigger side. If a contract author mistypes the id, that is a defect in the
  ambiguities-ledger entry itself, not a case for HR5 to paper over. (Reflected in new FR-004a;
  referenced from Edge Cases.)

- **Q2 -- Is the closed-vocabulary comparison in FR-002 exact, or does it tolerate case/whitespace
  variants (`Fully`, `SEMI`, `non `)?** Decision: Default adopted -- exact, case-sensitive,
  untrimmed string comparison against `fully`/`semi`/`non`. Any variant is out-of-vocabulary under
  FR-006, never silently normalized. Rationale: FR-006 already states HR5 "MUST NEVER infer or
  default a value to make the check pass"; silently lowercasing or trimming a near-miss would be
  exactly that kind of inference, and it would also mean the same underlying YAML text passes on one
  run and not another if an editor's autoformat changes case. Exact-match keeps the check
  deterministic and keeps the vocabulary genuinely closed. (Reflected in new FR-002a; referenced
  from Edge Cases.)

- **Q3 -- Does a present-but-null/empty `time_additivity` field on an A10-flagged contract count as
  the FR-004 missing-field finding or the FR-006 out-of-vocabulary finding (SC-004 requires these be
  distinguishable)?** Decision: Default adopted -- a null (`time_additivity:` with no value) or
  empty-string value is treated identically to the field being ABSENT, i.e. it produces the FR-004
  missing-field finding, not FR-006. Rationale: a human who typed the key but left it empty has, in
  effect, not yet declared anything -- there is no candidate word to reject as unrecognized, so
  "missing declaration" is the more honest and more actionable message (it tells the owner to add a
  value, not that they wrote a bad one). This also matches the AL1/AD1 precedent of collapsing
  not-meaningfully-present states into one branch rather than multiplying finding types. A non-scalar
  value (a list or mapping) is different -- see Q3b. (Reflected in new FR-004b; referenced from Edge
  Cases.)

  - **Q3b -- What does HR5 do if `time_additivity` is present as a non-scalar (a YAML list or
    mapping) instead of a string?** Decision: Default adopted -- treat as out-of-vocabulary under
    FR-006 and ERROR; HR5 MUST NOT raise an unhandled parser/type exception. Rationale: FR-014
    already commits HR5 to fail loud only for an unreadable FILE, not for a well-formed-YAML,
    wrong-shaped VALUE; a non-scalar `time_additivity` is readable YAML that simply isn't one of the
    three accepted words, so it belongs in the same "unrecognized value" bucket as a stray string,
    keeping the rule's failure surface uniform and crash-free. (Reflected in new FR-006a.)

- **Q4 (FR-018) -- Should snapshot-grain detection ever extend beyond the existing A10
  ambiguities-ledger id to other semi-additive-over-time shapes (e.g. a cumulative/YTD balance) that
  carry no A10 entry? -- OPEN owner ruling, the workflow is forbidden to answer.** This is a
  retail-kpi-knowledge ledger-scope decision: whether the knowledge layer should mint a NEW
  ambiguity id for non-inventory semi-additive cases, or whether some future rule's trigger should
  widen to a different signal entirely, is a business/domain-ownership call that belongs to
  retail-kpi-knowledge (Principle V), not to this schema-and-static-check build, and not to the
  agent authoring this spec. RECORDED PENDING DEFAULT for THIS build only (not a resolution of the
  open question): HR5 triggers on the existing A10 id alone; no other ambiguities-ledger id or
  measure-name heuristic is read. The `[NEEDS CLARIFICATION]` marker on FR-018 stays in the spec,
  resolved-to-OPEN, until a named retail-kpi-knowledge owner rules on whether a new ledger id (or
  widened trigger) is warranted at a later date.
