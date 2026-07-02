# Feature Specification: Additivity-Consistency Lineage Rule

**Feature Branch**: `068-additivity-consistency-rule-build`

**Created**: 2026-07-02

**Status**: Ratified (Ahmed Shaaban, 2026-07-02)

> Ratified by the owner in their own name (2026-07-02), authorizing the build of the
> deferred ADOPT idea H1. The two open items FR-011 (cross-corpus metric identity) and
> FR-012 (legality-table closure) stay DEFERRED to a human metric-owner ruling and are
> explicitly OUT OF SCOPE for this build (tasks.md "Out of scope"); the rule functions
> day-one on the define-layer prose corpus without them. Build guard (plan-review):
> ERROR only on prose-stated illegal compositions; an unknown composition kind or an
> absent/ambiguous classification yields NO inferred verdict (never assume SUM) --
> Principle V. analyze: clean (0 critical / 0 high); plan-review: PASS-WITH-NOTES.

**Input**: User description: "H1. Additivity-Consistency Lineage Rule"

## Overview

A new OFF-SPINE retail-check integrity rule (a sibling of the shipped assumption-ledger
rule AL1) that statically cross-reads two committed define-layer facts about each
metric -- its declared **additivity classification** and its **derivation-lineage edges**
-- and ERRORs when a metric's additivity is COMPOSED illegally with its parents or
children per a small CLOSED, generic additivity-composition legality table.

The rule is a pure static text read: it reads committed markdown/YAML, applies a settled
generic legality table, and returns categorical findings via the check exit code. It
never runs DAX, never opens a database connection, never renders a visual, and never
computes a numeric score. It only SURFACES an inconsistency for a human metric owner to
resolve; it never picks a winner, never invents a derivation edge, and never
re-classifies a metric.

This rule is OFF-SPINE: it advances no 7-stage readiness stage and grants no approval,
exactly like the shipped integrity rules (coverage-scorecard, publish-pack, define-layer,
assumption-ledger). It only reads committed define-layer artifacts.

## Clarifications

### Session 2026-07-02

Resolved design-level ambiguities (recommended answers adopted into the spec):

- **Q1 - Is parsing the closed additivity words a safe categorical transcription, or does
  it smuggle in a Principle-V judgment?** Decision: SAFE, under a strict framing. The rule
  acts ONLY on the exact committed classification words in the closed three-word
  vocabulary ("Fully additive" / "Semi-additive" / "Non-additive"); it treats an absent or
  out-of-vocabulary classification as absent/ambiguous and ERRORs, and NEVER infers or
  defaults a class. Recognizing a word a human already wrote is transcription, not a
  ruling; inventing a class where the human wrote none would be the ruling and is
  forbidden. (Reflected in FR-004, User Story 2.)

- **Q2 - WHERE does the rule read additivity + derivation edges from?** Decision: read the
  COMMITTED DEFINE-LAYER PROSE corpus where these facts actually exist -- the additivity
  classification under each metric contract's additivity heading and the derivation edges
  under each contract's derives-from heading plus the rendered lineage document -- reached
  by a GENERIC glob, not a hardcoded worked-example path. Rationale: the deployable
  per-table metric contracts carry NEITHER a machine-readable additivity field NOR a
  derives-from field today (additivity is buried in free-text grain, there is no lineage
  field), so reading them would find no data. Reading the define-layer corpus is where the
  settled facts live. To honor the C086-Is-An-Example rule, the rule globs whatever
  define-layer contracts exist and hardcodes no worked-example metric names, ids, or paths.
  (Reflected in FR-009; the glob generality is FR-006/FR-001.)

- **Q3 - Which readiness stage does this advance?** Decision (as advisor default): OFF-
  SPINE, advancing NO 7-stage readiness stage, exactly like the shipped integrity rules
  (coverage-scorecard, publish-pack, define-layer, assumption-ledger). The spec asserts no
  stage advancement. NOTE: whether a roadmap F-row should be ASSIGNED is a human-only act
  and is carried to open_for_human below, not decided here. (Reflected in FR-007,
  Assumptions.)

Reversibility of the above: Q1 (easy -- widening the vocabulary later is additive), Q2
(costly -- switching corpora changes the whole read path and fixtures), Q3 (easy -- a
human can assign an F-row later without changing the rule).

Deferred to human ruling (Principle V -- Agent Stops at Judgment Calls; recorded, NOT
answered):

- **Q4 - Does the additivity-composition legality table itself need human ratification as
  the CLOSED set it enforces?** The settled generic facts exist, but the exact
  parent->child legality matrix (fully-additive parents -> a non-additive ratio child is
  legal; SUMming a ratio/percentage child is illegal; a semi-additive component poisoning a
  plain-SUM parent is illegal) is the rule author's synthesis. A human owner must confirm
  it as the closed set. Marked FR-012. Left open.

- **Q5 - Metric identity / uniqueness across the two corpora.** The classification+edges
  facts and the deployable contracts are two separate corpora with no committed id mapping
  between them; deciding what constitutes the same metric across them (identity / grain /
  uniqueness) is a metric-owner ruling. Marked FR-011. Left open. (Because Q2 scopes the
  rule to READ ONLY the define-layer prose corpus, the rule does not need this join to
  function on day one; the join only becomes load-bearing if a future change asks the rule
  to reconcile the two corpora.)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Illegal composition is surfaced as an ERROR (Priority: P1)

A metric owner (or the CI gate acting on their behalf) commits a set of metric contracts
in which one metric declares an additivity classification that is illegal given how it is
composed from, or composed into, other metrics via committed derivation edges -- for
example, a ratio/percentage/average child that a parent metric SUMs directly. When the
retail check runs, the rule ERRORs on the offending metric with a message naming the
metric and the specific illegal composition, so the human owner can correct the
classification or the composition. The rule does NOT correct it.

**Why this priority**: This is the entire point of the rule -- catching a class of silent
dashboard-corrupting errors (summing a ratio, poisoning a plain-SUM total with a
semi-additive component) at define time, before the DAX layer ever naively SUMs. Without
it, there is no automated guard against additivity-composition inconsistency.

**Independent Test**: Author a fixture pair of contracts where a fully-additive parent
declares it SUMs a non-additive (ratio) child, run the rule against the fixture corpus,
and confirm exactly one ERROR finding is emitted naming the offending metric and the
illegal edge. Delete/repair the illegal edge and confirm zero findings.

**Acceptance Scenarios**:

1. **Given** a corpus where a parent metric composes a non-additive ratio child by direct
   SUM, **When** the retail check runs, **Then** the rule emits an ERROR naming that
   metric and the illegal composition, and never mutates any contract.
2. **Given** a corpus where a non-additive child is recomputed from fully-additive
   parents (base-over-base), **When** the retail check runs, **Then** the rule emits no
   finding for that composition (it is legal).
3. **Given** a corpus where a semi-additive component feeds a plain-SUM parent, **When**
   the retail check runs, **Then** the rule emits an ERROR naming that composition.

---

### User Story 2 - Absent or ambiguous classification is refused, never inferred (Priority: P1)

A metric participates in a committed derivation edge but its additivity classification is
absent, or is written in words the closed vocabulary does not recognize. The rule must
NOT guess a classification to complete the composition check; it must ERROR that the
classification is absent/ambiguous and stop there for that metric. Inferring a
classification would be a metric-owner judgment the rule is forbidden to make
(Principle V).

**Why this priority**: The safety framing that makes this rule ratifiable is "act only on
the exact committed classification words; ERROR on absent/ambiguous; never infer." If the
rule silently defaulted a missing classification it would smuggle in an owner ruling.

**Independent Test**: Author a fixture where a metric on a derivation edge has no
recognizable additivity word, run the rule, and confirm it emits an ERROR that the
classification is absent/ambiguous (not a composition verdict) and does not fabricate a
class.

**Acceptance Scenarios**:

1. **Given** a metric on a derivation edge whose additivity section is missing, **When**
   the rule runs, **Then** it ERRORs that the classification is absent and emits no
   composition verdict inferred from a guessed class.
2. **Given** a metric whose additivity text uses words outside the closed vocabulary,
   **When** the rule runs, **Then** it ERRORs that the classification is ambiguous.

---

### User Story 3 - Rule is wired in and counted like every other rule (Priority: P2)

The rule appears in the rule registry, the expected-rule-id set, the authoritative rules
manifest, and the severity-posture manifest, so the wiring meta-gate and the rule-count
reconciler agree the rule count advanced by exactly one (from the current count to the
current count plus one). A missing wiring point causes a golden test to fail.

**Why this priority**: A registered rule that is not fully wired fails the shipped wiring
checklist (five places). This is required for the rule to ship at all, but it is
mechanical relative to the rule's logic (P1).

**Independent Test**: Run the rule-wiring unit test and confirm the actual registered
rule ids equal the expected set (now including the new id) and the manifest count matches.

**Acceptance Scenarios**:

1. **Given** the new rule module is registered and all five wiring points updated,
   **When** the wiring unit test runs, **Then** actual rule ids equal expected rule ids
   and the manifest count equals the length of the expected set.

---

### Edge Cases

- **No contracts on disk**: the rule finds no corpus to read and emits zero findings
  (clean pass), never errors on an empty repo.
- **Template and test fixtures**: the generic contract template and any test-fixture
  paths are exempt from scanning, matching the AL1 exemption seam (template path +
  test-path predicate).
- **A metric with a classification but no derivation edges**: nothing to compose, so no
  composition verdict -- a standalone fully-additive base metric is not an error.
- **A derivation edge naming a parent/child that has no contract at all**: the referenced
  metric's classification is absent -> treated per User Story 2 (ERROR absent/ambiguous),
  never inferred.
- **A tracked-but-unreadable source artifact**: the rule fails loud with an ERROR finding
  naming the unreadable path (matching the AL1 fail-loud-on-unreadable seam), never
  silently skips.
- **Duplicate or conflicting classification words for the same metric**: treated as
  ambiguous -> ERROR, never resolved to one class.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The rule MUST be a new retail-check rule module registered through the
  existing rule-registry decorator, cloning the shipped assumption-ledger (AL1) pattern:
  a lazy in-function import of any non-stdlib parser (keeping the retail-check core
  stdlib-only at module scope), a generic glob over whatever committed contracts exist, a
  template + test-path exemption, fail-loud on an unreadable tracked source, and a return
  of an iterable of findings.
- **FR-002**: The rule MUST emit findings ONLY at the ERROR severity (categorical
  pass/ERROR). It MUST NOT emit a numeric score, a confidence value, a threshold band, or
  any graded/numeric output (No-Fake-Confidence rule).
- **FR-003**: The rule MUST NOT execute DAX, MUST NOT open any database or network
  connection, and MUST NOT render or evaluate any visual. It reads committed text only
  (Static-First Governance / never-execute invariant).
- **FR-004**: The rule MUST act ONLY on the exact committed additivity classification
  words in the closed vocabulary ("Fully additive", "Semi-additive", "Non-additive") and
  ONLY on derivation edges stated in committed prose. It MUST ERROR when a metric on a
  derivation edge has an absent or ambiguous classification, and MUST NEVER infer,
  default, or fabricate a classification.
- **FR-005**: The rule MUST only SURFACE an additivity-composition inconsistency. It MUST
  NEVER pick a winner between two conflicting facts, invent a derivation edge, or
  re-classify a metric's additivity -- those are metric-owner rulings (Agent-Stops-at-
  Judgment-Calls / Principle V).
- **FR-006**: The rule MUST apply a small CLOSED, generic additivity-composition legality
  table drawn from the settled generic retail-arithmetic facts already committed in the
  knowledge layer. The table MUST be generic retail arithmetic (a ratio/percentage/
  average child may never be composed by direct SUM; a non-additive child recomputed
  base-over-base from fully-additive parents is legal; a semi-additive component composed
  into a plain-SUM parent is illegal). The table MUST contain no domain-specific metric
  names, no worked-example metric ids, and no worked-example file paths (C086-Is-An-
  Example-Not-The-Schema rule).
- **FR-007**: The rule MUST advance no readiness stage and grant no approval. It is
  off-spine: it only reads committed define-layer artifacts and returns findings via the
  exit code, exactly like the other integrity rules.
- **FR-008**: The rule MUST be wired into all five required places so the wiring meta-gate
  and rule-count reconciler agree: the registry module import block and the module export
  list, the expected-rule-id set in the wiring unit test, the authoritative rules
  manifest (regenerated), and the severity-posture manifest/golden fixture (regenerated).
  The rule count MUST advance by exactly one.
- **FR-009**: The rule MUST read the additivity classification and the derivation edges
  from the corpus decided in Clarifications (see Q2). It MUST NOT assume a machine-readable
  `additivity` field or a machine-readable `derives_from` field exists on the deployable
  per-table metric contracts, because neither exists today; additivity is committed as
  prose under an additivity heading and edges are committed as prose under a derives-from
  heading plus a rendered lineage document.
- **FR-010**: On a corpus with no contracts, or contracts with classifications but no
  derivation edges, the rule MUST emit zero findings (clean pass) rather than erroring.

*Markers requiring human ruling before build (do not answer during automated planning):*

- **FR-011**: The rule reads and cross-references committed metric identifiers to join a
  classification to a lineage edge (DEFERRED TO HUMAN RULING: metric identity / uniqueness
  across the two corpora is a metric-owner ruling -- see Clarifications Q5; OUT OF SCOPE
  for this build, the day-one read stays within the single define-layer corpus).
- **FR-012**: The composition legality table the rule enforces MUST be the CLOSED set a
  human owner confirms (DEFERRED TO HUMAN RULING: the exact parent->child legality matrix
  is a synthesis that should be owner-ratified -- see Clarifications Q4; OUT OF SCOPE for
  this build, the rule ships the generic-arithmetic seed table pending that ratification).

### Key Entities *(include if feature involves data)*

- **Metric classification**: a committed, human-authored additivity class for one metric,
  expressed in a closed three-word vocabulary (fully additive / semi-additive /
  non-additive). The rule reads it; it never writes or infers it.
- **Derivation edge**: a committed, human-authored statement that one metric derives from
  one or more other metrics. The rule reads it; it never invents one.
- **Composition legality table**: a small closed, generic table of which parent->child
  additivity compositions are legal versus illegal, drawn from settled generic retail
  arithmetic. Fixed in the rule; owner-ratified as a closed set.
- **Finding**: a categorical ERROR (never a score) naming an offending metric and the
  specific illegal or absent/ambiguous composition, surfaced for a human to resolve.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the current committed corpus (all committed contracts are consistent),
  the rule produces zero findings -- a genuine clean baseline, not a suppressed one.
- **SC-002**: Given a fixture with exactly one illegal additivity composition, the rule
  emits exactly one ERROR finding naming that metric; given the repaired fixture, it emits
  zero.
- **SC-003**: Given a fixture whose metric on a derivation edge has an absent or
  ambiguous classification, the rule emits an ERROR that the classification is
  absent/ambiguous and emits no inferred composition verdict.
- **SC-004**: The registered rule-id set equals the expected rule-id set including the new
  id, and the rules manifest count equals the length of that set (rule count advanced by
  exactly one); every wiring golden test passes.
- **SC-005**: The rule emits no numeric score, confidence value, or threshold in any
  finding, and performs no execution (no DAX, no connection, no visual) -- verifiable by
  inspecting outputs and by the core module remaining stdlib-only at import time.

## Assumptions

- The rule is OFF-SPINE and advances no readiness stage. Whether it should be assigned a
  roadmap F-row is a human-only act and is recorded for human resolution, not decided here.
- The shipped assumption-ledger rule (AL1) is the exact clone target: lazy parser import,
  generic contract glob, template + test-path exemption, fail-loud on unreadable, ERROR-
  only, never-resolves. The rule reuses this scaffold.
- The settled generic additivity facts (a ratio is never summed; carry base components and
  recompute at each grain; a semi-additive component must not be naively summed) already
  exist as committed generic knowledge and are the source of the closed legality table --
  the rule enforces settled facts, it is not a statistics engine.
- No deferred capability is assumed: no Power BI execution adapter, no spec-only runtime,
  no live database. The rule is a static text read only (add the seam, not an executor).
- The idea's one-line "load each contract's additivity + lineage edges from the contract
  YAML" is only HALF-grounded: neither a machine-readable additivity field nor a
  machine-readable derives-from field exists on the deployable per-table contracts today.
  The corpus the rule reads and how it obtains additivity + edges is the load-bearing
  design decision resolved in Clarifications, not assumed here.

## Dependencies

- Depends on the existing rule registry, findings model, severity model, and test-path
  predicate (all shipped).
- Depends on committed define-layer additivity classifications and derivation edges as
  the READ source; it introduces no new machine-readable contract field as part of this
  feature (adding a structured field would be a separate, larger define-layer change).
- No dependency on the unshipped ambiguity-ledger CHECK half; this rule is standalone and
  keys on existing committed facts, giving it a real convention to check on day one.
