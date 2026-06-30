# Feature Specification: Stale-Marker Sweep / Status-Claim Reconciler (SC1)

**Feature Branch**: `050-stale-marker-sweep`

**Created**: 2026-06-30

**Status**: Draft

**Input**: User description: "Stale-Marker Sweep / Status-Claim Reconciler (SC1)"

## Overview

The retail check kit already keeps *routing* honest: rule A1 reads a manifest of
declared routes and fails the gate when a route's target file does not match its
declared status (built target missing, or planned target that already exists).
Prose documents in the repo make the same kind of claim -- "this artifact is
built" / "this artifact is planned" -- but nothing checks those prose claims
against reality. They drift silently: a document can keep calling a shipped
artifact "(planned)" long after it landed.

SC1 closes that gap for the *general file-exists-vs-status prose-claim class*. A
human-curated manifest declares, per claim, which document makes the claim, the
verbatim text snippet that anchors it, which artifact it is a claim about, and
the claimed status. SC1 reconciles each claim against committed evidence (the
set of tracked files plus the claiming document's own text) and fails the gate
on any contradiction -- honestly in both directions, the same fail-closed shape
A1 uses for routing.

SC1 is a static governance rule, not a runtime feature. It maps to no roadmap
readiness stage; it is an idea-bank integrity rule in the same family as the
shipped A1 / A3 / B1 rules (routing / observability integrity), recorded outside
the seven-stage Source -> ... -> Publish spine.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catch a stale "planned" claim about a shipped artifact (Priority: P1)

A governance maintainer runs the retail check gate. A tracked document still
describes an artifact as "(planned)" even though that artifact has shipped and is
now a tracked file. SC1 reports an ERROR naming the document, the claimed
artifact, and the contradiction, so the maintainer can correct the prose (or flip
the claim to built) before the change merges.

**Why this priority**: This is the core value -- the named, confirmed seed defect
(a capability-state document calling a shipped end-to-end trace "(planned)") is
exactly this case. Catching planned-but-exists is the reason the rule exists.

**Independent Test**: Construct a manifest entry with `claimed-status: planned`
whose `claimed-artifact` resolves to a tracked file and whose `anchor` is present
in the named doc; run SC1; assert exactly one ERROR finding naming that entry.
Delivers value on its own: the gate now fails on stale planned markers.

**Acceptance Scenarios**:

1. **Given** a manifest entry `{doc, anchor, claimed-artifact, claimed-status: planned}` where the anchor text is present in the doc and the claimed-artifact is a tracked file, **When** SC1 runs, **Then** it emits one ERROR finding stating the planned claim is stale because the artifact now exists.
2. **Given** the same entry but the claimed-artifact is NOT a tracked file, **When** SC1 runs, **Then** SC1 emits no finding for that entry (a planned claim about a not-yet-built artifact is honest).

### User Story 2 - Catch a false "built" claim about a missing artifact (Priority: P1)

A maintainer marks a claim `built` in the manifest, but the artifact it asserts
is not (or no longer) a tracked file. SC1 fails the gate so a document cannot
assert that something is built when the evidence says otherwise.

**Why this priority**: The other half of honest-in-both-directions. Without it,
SC1 would only catch one drift direction and could pass vacuously on a deleted or
never-built artifact that prose still calls "built".

**Independent Test**: Manifest entry `claimed-status: built`, anchor present,
claimed-artifact absent from tracked files -> assert one ERROR.

**Acceptance Scenarios**:

1. **Given** a manifest entry with `claimed-status: built` whose anchor is present in the doc but whose claimed-artifact is not a tracked file, **When** SC1 runs, **Then** it emits one ERROR finding stating the built claim is false because the artifact is missing.
2. **Given** a manifest entry with `claimed-status: built` whose claimed-artifact is a tracked file and whose anchor is present, **When** SC1 runs, **Then** SC1 emits no finding for that entry.

### User Story 3 - Fail loud on an anchor that no longer exists or a malformed/missing manifest (Priority: P2)

A maintainer edits a document and removes the exact text the manifest anchors on,
or the manifest file is missing, untracked, or malformed. SC1 must fail loud in
every such case rather than silently passing, so the manifest can never quietly
stop checking anything.

**Why this priority**: Fail-closed integrity. A status reconciler that can go
vacuously green is worse than none, because it manufactures false confidence --
the exact failure the no-fake-confidence rule forbids.

**Independent Test**: (a) manifest absent/untracked -> one ERROR; (b) manifest
not valid YAML -> one ERROR; (c) entry whose anchor text is absent from the named
doc -> one ERROR.

**Acceptance Scenarios**:

1. **Given** the manifest file is missing or not tracked, **When** SC1 runs, **Then** it emits one ERROR finding that the manifest is missing/untracked and SC1 cannot verify status claims.
2. **Given** the manifest is present but not valid YAML, **When** SC1 runs, **Then** it emits one ERROR finding that the manifest is malformed.
3. **Given** a manifest entry whose `anchor` text is not found in the named `doc`, **When** SC1 runs, **Then** it emits one ERROR finding that the anchor is stale or misplaced for that entry.
4. **Given** a manifest entry whose `doc` path is not a tracked file, **When** SC1 runs, **Then** it emits one ERROR finding that the claiming document is missing/untracked.

### Edge Cases

- **Anchor matches more than once**: the anchor is used only as a presence check (is the claim text still in the doc), so multiple matches are treated the same as one match -- present is present. No line/offset is recorded (avoids a brittle positional matcher).
- **Invalid `claimed-status` value**: any value outside the enumerated set (`built` | `planned`) is an ERROR for that entry (mirrors A1's invalid-status handling).
- **Entry missing a required field** (`id` / `doc` / `anchor` / `claimed-artifact` / `claimed-status`): ERROR for that entry; SC1 never guesses a missing field.
- **Empty manifest** (`claims: []`): not an error in itself -- an explicitly empty list is honest. (Manifest *completeness* is explicitly NOT SC1's job; see Out of Scope.)
- **Anchor / artifact under `tests/`**: tracked-file resolution uses the same tracked-files set the other rules use; SC1 does not apply the test-fixture content exemption because it reconciles declared claims, not scans the tree. The manifest author is responsible for not anchoring on a throwaway fixture.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a registered static rule, id `SC1`, that the retail check gate runs as an enforced rule (a contradiction produces a finding at ERROR severity, which fails the build with a non-zero exit). SC1 MUST NOT be advisory-only prose.
- **FR-002**: SC1 MUST read its claims from a single human-curated manifest at a fixed repo-relative path (`docs/quality/status-claims.yaml`). The manifest MUST be parsed only when SC1 runs (not at module import).
- **FR-003**: SC1 MUST treat the manifest as a mapping containing a list of claim records under a top-level key (`claims`). Each record declares: `id` (stable handle), `doc` (repo-relative POSIX path of the claiming document), `anchor` (a verbatim text snippet expected to be present in that document), `claimed-artifact` (a repo-relative POSIX path whose readiness the claim asserts), and `claimed-status` (one of the enumerated set `built` | `planned`).
- **FR-004**: SC1 MUST fail loud if the manifest is absent or not a tracked file: emit one ERROR finding and verify nothing further. It MUST NOT pass vacuously when it has nothing to check.
- **FR-005**: SC1 MUST fail loud (ERROR) if the manifest is not valid YAML, or is not a mapping with a `claims` list.
- **FR-006**: For each claim record, SC1 MUST verify the claiming `doc` is itself a tracked file; if not, emit an ERROR for that entry.
- **FR-007**: For each claim record, SC1 MUST verify the `anchor` text is present (substring presence) in the claiming document's committed text; if absent, emit an ERROR that the anchor is stale or misplaced. SC1 MUST read the document text via the repository root provided in its run context, not from any live source.
- **FR-008**: For a record with `claimed-status: built`, SC1 MUST emit an ERROR if the `claimed-artifact` is not a tracked file (a false "built" claim).
- **FR-009**: For a record with `claimed-status: planned`, SC1 MUST emit an ERROR if the `claimed-artifact` IS a tracked file (a stale "planned" marker -- the artifact shipped but the prose was not updated). A planned claim whose artifact does not resolve is honest and produces no finding.
- **FR-010**: SC1 MUST emit an ERROR for any record whose `claimed-status` is outside the enumerated set, or which is missing any required field, rather than guessing or skipping silently.
- **FR-011**: Every SC1 finding MUST carry the rule id `SC1`, ERROR severity, a human-readable message naming the offending document / artifact / claim, and a locator that points at the manifest entry (and/or the claiming doc) so the maintainer can find it.
- **FR-012**: SC1 MUST remain strictly CATEGORICAL: a claim either matches the evidence or it does not. SC1 MUST NOT compute, emit, or infer any numeric confidence score, readiness percentage, or other graded value.
- **FR-013**: SC1's rule module MUST carry no module-scope database, network, or Power BI import; any YAML parsing dependency MUST be imported lazily inside the handler. SC1 MUST read only committed repository text and the tracked-files set -- no database, no network, no live Power BI surface.
- **FR-014**: The rule MUST self-register through the existing rule-registration mechanism (a decorator side effect on import of its submodule); no edit to the registry module is required.
- **FR-015**: The single-source-of-truth set of expected rule ids (in the rule-wiring test) MUST gain `SC1` in the same change that introduces the rule, so the wiring/drift test continues to pass. (The live set holds 35 ids today; SC1 takes it to 36.)
- **FR-016**: The manifest MUST be GENERIC prose-claim machinery. Neither the rule code nor any kit-level seed manifest entry may hardcode or special-case a worked-example-specific (C086 / pharmacy) document path, artifact, or value. The rule schema must be applicable to any document making a status claim.
- **FR-017**: The seed manifest MUST include the confirmed generic seed defect: the capability-state document that calls the shipped Net Sales end-to-end trace "(planned)" while that trace is a tracked, shipped artifact. The change that introduces SC1 MUST also CORRECT the seeded stale prose (flip the offending "(planned)" wording to reflect the shipped reality) in the SAME change, so the gate is green on the feature branch at merge. Rationale: an enforced rule that ships RED on main would block every subsequent change; the seed defect and its fix land together (a tracked-document text correction, not a re-decision). See Clarifications (Q1).
- **FR-018**: SC1 MUST be accompanied by unit tests that exercise: a stale planned marker (ERROR), an honest planned claim (no finding), a false built claim (ERROR), an honest built claim (no finding), a missing/untracked manifest (ERROR), malformed YAML (ERROR), an absent anchor (ERROR), and an invalid/missing field (ERROR).

### Out of Scope

- **The rule-count claim facet.** Stale numeric-count claims in prose (for example a document asserting a specific number of rules that no longer matches the live set) are explicitly DELEGATED to a separate sibling idea (T5.5) and are NOT covered by SC1. SC1 covers only the file-exists-vs-status prose-claim class. Rationale: a general prose number/phrase matcher risks false positives on legitimate forward-looking prose; keeping SC1 to path-resolution-against-tracked-files (the proven A1 shape) keeps it safe.
- **Manifest completeness / coverage.** Nothing in SC1 verifies that the manifest enumerates every status claim in the repo. SC1 checks only the claims that are listed. This leaves a known drift gap (a claim no one added to the manifest is not checked). The spec records this gap; it does NOT build a coverage rule. The drift gap is ACCEPTED for SC1's first step, mirroring how A1 shipped (route resolution) before its A3 coverage sibling (manifest bijection) was added later. A coverage check, if wanted, is a separate future idea -- not part of SC1. See Clarifications (Q2).
- **Any live capability.** No database provisioning, no ingestion, no Power BI execution adapter (F016), no spec-only runtimes (F031-F033). SC1 is static-only.
- **Amending any ratified decision.** If SC1's seed reconciles a claim that happens to live in a governance document, fixing the stale prose is a tracked-document text correction, not a re-decision or version bump of any ratified principle.

### Key Entities *(include if feature involves data)*

- **Status-claim manifest**: a committed, human-curated YAML file. Holds a list of status-claim records. Single source of truth for what SC1 checks. Generic -- not tied to any worked example.
- **Status-claim record**: one declared claim. Attributes: `id` (stable handle), `doc` (claiming document path), `anchor` (verbatim snippet that must still be present in the doc), `claimed-artifact` (path whose readiness is asserted), `claimed-status` (`built` | `planned`).
- **Finding**: the existing rule-output value (rule id, severity, message, locator). SC1 produces ERROR findings only.
- **Run context**: the existing read-only context handed to every rule -- provides the repository root (to read a document's committed text) and the tracked-files set (to resolve artifact existence). SC1 consumes both; it adds no new context field.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When the manifest contains the seeded stale-planned defect (a shipped artifact still claimed "planned"), running the gate fails with a non-zero exit and a finding that names the offending document and artifact -- demonstrated by a unit test.
- **SC-002**: Every contradiction class -- false built, stale planned, absent anchor, missing/untracked manifest, malformed manifest, invalid/missing field -- produces at least one ERROR finding; every honest claim (honest built, honest planned) produces zero findings. 100% of the eight enumerated cases are covered by passing unit tests.
- **SC-003**: After SC1 lands, the rule-wiring/drift test passes with the expected-id set containing `SC1` and the registered-rule count equal to the size of that set (36).
- **SC-004**: SC1 emits zero numeric confidence/readiness values in any finding (verifiable by inspecting finding messages -- they are categorical statements only).
- **SC-005**: SC1 performs no database, network, or Power BI access during a gate run (verifiable: the never-execute import rule reports no module-scope DB/network import in SC1's module, and the rule runs with only the repo checkout present).

## Assumptions

- SC1 reuses the existing rule abstraction (a pure function: read-only context in, findings out) and the existing finding/severity value types; it introduces no new core types.
- SC1 reuses the existing tracked-files population mechanism (derived from the version-control file list, repo-relative POSIX paths) -- the same source A1 resolves targets against -- so artifact-existence resolution behaves identically to A1.
- The YAML parsing dependency already used lazily by sibling rules (A1, the contract loader) is available as a development/optional dependency and is imported the same lazy way.
- The manifest is authored and maintained by humans; SC1 does not generate or auto-populate it. Ownership of keeping the manifest current is a human responsibility (see the open completeness question).
- SC1 maps to no roadmap F-number and advances no readiness stage; it is recorded as an idea-bank integrity rule (sibling to A1 / A3 / B1), OUTSIDE the seven-stage Source -> ... -> Publish readiness spine. This is the confirmed home: SC1 is governance/observability-integrity machinery, structurally identical to A1/A3/B1, none of which sit on the readiness spine. See Clarifications (Q3).

## Clarifications

### Session 2026-06-30

Three build-relevant ambiguities were resolved by the advisor against the
constitution, the readiness spine, and how the sibling A1/A3 rules shipped. None
is a Principle-V carve-out (SC1 touches no data grain, PII, business rollup, or
product identity -- it reconciles prose status claims against file existence), so
none is deferred to a human ruling.

- **Q1 (delivery sequencing of the seed fix)**: Should introducing SC1 also
  correct the seeded stale prose in the same change, or only register the claim?
  **Recommended answer**: Correct it in the same change. **Reasoning**: An enforced
  ERROR rule that ships RED on main would block every later change until someone
  fixes the prose; the seed defect and its one-line prose correction must land
  together so the gate is green at merge. Fixing the wording is a tracked-document
  text correction, not a re-decision of any ratified content. **Reversible**: easy
  (the prose fix is a small text edit). Integrated into FR-017.

- **Q2 (manifest-completeness drift gap)**: Accept that nothing checks the
  manifest is complete, or pair SC1 with a coverage rule now? **Recommended
  answer**: Accept the gap for SC1's first step. **Reasoning**: A1 shipped route
  resolution before its A3 coverage/bijection sibling existed; the same staged
  path applies here. Building a coverage rule now is scope creep (YAGNI) and a
  separate idea. **Reversible**: easy (a coverage rule can be added later as a
  sibling without changing SC1). Integrated into Out of Scope.

- **Q3 (readiness-spine placement)**: Is SC1 correctly outside the seven-stage
  readiness spine, recorded as an idea-bank integrity rule? **Recommended
  answer**: Yes -- outside the spine, sibling to A1/A3/B1. **Reasoning**: SC1 is
  governance/observability-integrity machinery with no roadmap F-number and
  advances no Source->...->Publish stage, structurally identical to the routing
  /never-execute integrity rules that are all recorded off-spine. **Reversible**:
  easy (a future roadmap edit could map it if ever wanted). Integrated into
  Assumptions.

### Deferred to human ruling (Principle V)

None. SC1 surfaces no grain/uniqueness, PII publish-safety, business
rollup/segment, or product-identity question. The rule resolves declared status
claims against the tracked-file set and committed text only.

