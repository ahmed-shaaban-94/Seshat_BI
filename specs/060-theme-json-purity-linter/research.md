# Phase 0 Research: Theme JSON Purity Linter

## R1 -- Structural precedent for a JSON-scanning rule

**Decision**: Model the new rule on `src/retail/rules/pbir.py`.

**Rationale**: pbir.py is the closest existing pattern to what A2 needs. It:
- discovers files from `ctx.tracked_files` filtered by suffix, excluding
  `is_test_path` fixtures;
- opens each with `encoding="utf-8-sig"` and `json.load`;
- emits `Finding(rule_id=..., severity=Severity.ERROR, message=..., locator="file#/json/pointer")`.

A2's asks -- a committed-JSON scan, a JSON-pointer-style locator, and a
fixture exemption -- are all directly supported by this precedent. No new
framework capability is required.

**Alternatives rejected**: Writing a bespoke JSON walker or adding a JSON-schema
dependency. Rejected -- stdlib `json` plus a recursive key walk is sufficient and
keeps the stdlib-only invariant (Principle VIII); a schema dependency would
violate "depend, never fork" spirit and add a third-party dep for no gain.

## R2 -- Theme-file discovery

**Decision**: Discover the files to scan generically from `ctx.tracked_files` by a
theme-file naming pattern (files ending in the theme-JSON suffix), excluding the
`is_test_path` fixture path. Never an enumerated or tenant-specific list.

**Rationale**: Principle VII requires generality; an enumerated list would silently
miss a newly added theme file and couple the rule to today's single-file corpus.
The committed corpus today is one file (`themes/tower-retail.theme.json`), so the
glob has a real, honest target and is trivially extensible.

**Alternatives rejected**: Hardcoding `themes/tower-retail.theme.json`. Rejected --
violates Principle VII and fails SC-005 (new files must be scanned with no code
change).

## R3 -- Forbidden-key vocabulary sourcing

**Decision**: The forbidden-key vocabulary is a single module-level generic
constant whose MEMBERS are derived from the MUST-NOT categories stated in
`docs/powerbi/theme-json.md` (DAX, measures, calculated columns/tables, metric
definitions, semantic-model relationships, source mapping, sentiment
thresholds/rules, data validation). The allowed styling vocabulary (palette,
fonts, visual defaults, page/wallpaper defaults, filter-pane defaults, sentiment
COLORS) is explicitly NOT flagged.

**Rationale**: The contract is the generic source of truth (Principle VII). The
one boundary that is easy to blur -- a sentiment COLOR (allowed) versus a sentiment
THRESHOLD/RULE (forbidden) -- is called out in the contract and must be honored: a
key named for a color stays allowed; a key named for a threshold/rule is forbidden.

**OPEN (Principle V, human ruling -- see spec ## Clarifications)**: The exact
literal membership of the forbidden-key constant, and whether the rule also asserts
any REQUIRED keys are present, is a judgment about where styling ends and business
meaning begins. This plan represents the vocabulary as a clearly-marked seam (a
single named constant plus its derivation note) so the human ruling can be dropped
in without reshaping the rule. The plan does NOT freeze the literal list.

## R4 -- Rule-id allocation

**Decision**: Allocate a fresh, non-colliding identifier at wiring time,
reconciled against the TRUE live registry (not a count claim); prefer a
design/theme-namespaced id over reusing a bare backlog letter.

**Rationale**: Backlog letters A1/A2 collide with shipped ids (A1 = Route Registry
Manifest, A3 = Route Coverage). Reusing "A2" would freeze a confusing id into the
golden records. A namespaced id is self-documenting and collision-safe, and leaves
room for the future (unbuilt) token-to-theme fidelity rule to share the namespace.

**Note on live-registry state**: Backlog reviewers flagged a possible count drift
(EXPECTED_RULE_IDS vs decorator count). Before wiring, reconcile the new id against
the actual registered set observed on this branch, not against any count claim.

## R5 -- Malformed-JSON handling

**Decision**: On a committed theme file that fails to parse as JSON, emit a finding
(the file could not be parsed) rather than raising and crashing the whole contract
check, and rather than silently passing the file.

**Rationale**: FR-009 + fail-closed (Principle I). A styling file that cannot be
parsed cannot be proven clean, so it must not pass silently; crashing the whole
gate would mask every other rule's result.

**Alternatives rejected**: Let the `json.load` exception propagate. Rejected -- one
malformed file would abort the entire governance gate, which is worse than a scoped
finding.

## R6 -- Severity model

**Decision**: The rule emits `Severity.ERROR` findings and declares one id; its
severity is OBSERVED per branch in the severity-posture golden record. No governed
per-rule severity table is added.

**Rationale**: Ratified 044 -- severity is observed, not declared. Attempting a
declared per-rule severity table is the E2/E5 ineligible-as-framed pattern and is
explicitly avoided.
