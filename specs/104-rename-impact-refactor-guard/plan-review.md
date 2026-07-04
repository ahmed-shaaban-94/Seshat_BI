# Adversarial Plan-Review: Rename/Impact Refactor-Safety Static Rule (HR9)

**Stage**: 6 (single default-adverse skeptic). READ-ONLY over spec.md, plan.md,
tasks.md (+ research.md, data-model.md, quickstart.md, analysis.md). Reports
fixes; edits no artifact.

**Date**: 2026-07-04

**Draft completeness precheck**: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md, and analysis.md are all present on the branch;
analyze ran (verdict: 15/16 FRs covered, one MEDIUM-HIGH task-authoring
finding F1, several LOW cosmetic nits, constitution PASS on every principle,
deferred-capability scan CLEAN). Not an automatic BLOCKED. This review does
not defer to analysis.md's verdict -- each axis below was independently
re-pressured against the primary artifacts and the live repo tree (`src/
retail/rules/` contents, `docs/rules/severity-posture.json`,
`docs/rules/rules-manifest.json`, a repo-wide `HR9`/`HR6` grep) before being
scored.

## Axis 1 -- Hidden principle violation

- **Self-grant probe (FR-016 / Q-APPROVAL-SEAM)**: FR-016 carries a "RECORDED
  PENDING DEFAULT (MECHANICAL -- no new approval seam)" and plan.md's
  Constitution Check row for Principle V states this stays PENDING, not
  promoted to adopted. Adversarial read: does *writing a preferred answer* to
  a Principle-V approval-model question amount to a soft self-grant? No --
  the preferred answer is the NULL action (add no new `approvals[]` entry,
  gate nothing new, decide nothing about who signs off); Q-APPROVAL-SEAM
  itself is explicitly carried as OPEN in spec.md Clarifications, and tasks.md
  T045 is titled "[OWNER SEAM -- OPEN, do not answer]" and only confirms that
  no new approval shape was added -- it does not answer the question. A
  self-grant would look like promoting the pending default to "ratified" or
  writing a new `approvals[]` key; nothing in the six artifacts does that.
  VERDICT: not a violation, but the BUILD must keep T045 a checklist
  confirmation only -- if an implementer "cleans up" by promoting the pending
  default to adopted, that crosses into Principle V.
- **Judgment-call probe (mechanical resolution vs. business judgment)**:
  "does this reference resolve against the current TMDL" is a deterministic
  string-lookup fact, not a grain/PII/business-rollup/product-identity
  decision -- this matches the SC1/DF1 precedent (both already compute their
  own reconcile facts directly without raising a Principle-V question). No
  violation.
- **Advise-instead-of-block probe**: data-model.md Entity 5 fixes every HR9
  finding at `Severity.ERROR` with no WARNING tier (tasks.md T008 explicitly
  rejects copying HR1's two-tier `["error","warning"]` shape). plan.md's
  Constitution Check states a finding "fails `retail check`'s exit code
  (non-zero), not a WARNING an agent could rationalize past." This is a fail
  CLOSED design, not advisory. No violation.
- **Verdict**: PASS.

## Axis 2 -- Assumes a deferred capability

- research.md Sec 4 states plainly, and independently for each candidate
  capability, that F016 (Power BI execution adapter), a live database
  surface, and HR1's `conformed-dimension-map.yaml` are each "not assumed."
  plan.md's Constitution Check (Principle VIII row) states F016 "is
  correctly treated as non-existent; HR9 does not call it, wait on it, or
  reference its API." quickstart.md Sec 7 states HR9 "has no live/execution
  path to demonstrate." No task in tasks.md (T001-T046) opens a DB
  connection, runs DAX, or invokes an adapter; T043's `retail check`/`retail
  kit-lint` run is static-only, against the committed tree.
- Cross-checked against the live repo: `docs/rules/severity-posture.json`
  exists and is a static JSON file (no live dependency); `src/retail/rules/`
  contains no HR9 module yet, consistent with a not-yet-built feature that
  assumes nothing about a runtime that does not exist.
- **Verdict**: PASS. Clean -- no artifact assumes F016, a live DB, or a
  running adapter exists or is required for HR9 to be specified, built, or to
  function.

## Axis 3 -- C086 / worked-example leak

This is the sharpest axis (per the 068/AD1 precedent) precisely because HR9's
day-one *evidence* is drawn entirely from `retail_store_sales` -- the only
committed model instance with a filled TMDL, metric contracts, and a
binding map. The leak test is the RULE SOURCE and its logic, not whether the
design docs cite the worked example as an inspected instance.

- research.md Sec 1.4 and data-model.md Entity 4 read the worked instance's
  real files (`gold.fct_sales_rss` / `'gold fct_sales_rss'` / `dim_product_
  rss[category]` / `dim_date_rss[full_date]` / `dim_customer_rss[customer_
  id]`) to CONFIRM the two qualifier forms (dotted `schema.table` and bare
  dim identifier) that `normalize_qualifier` (Entity 4) must bridge. This is
  citation-as-evidence, matching the 068/AD1 precedent exactly (that review's
  Axis 3 accepted the same posture for the additivity corpus).
- The load-bearing question: does `normalize_qualifier`'s logic itself
  REQUIRE a worked-example literal? Entity 4's pseudocode strips "its
  leading `<word> ` (the schema segment)... whatever it is, generically" --
  i.e., the schema word ("gold") is read from whatever `TmdlTable.name`
  actually carries at check-time, never hardcoded as `"gold "` in the
  function body. Same for column/measure/table names throughout Entities
  1-3: every shape field is generic (`token`, `qualifier`, `table_name`), and
  FR-013 explicitly forbids inlining `retail_store_sales`/C086/pharmacy
  specifics into the rule's own source. tasks.md T004's stub docstring is
  tasked to describe the rule generically, and T041/T042 are dedicated grep
  sweeps -- T041 over `rename_impact_guard.py`'s source, T042 over the test
  fixtures under `tests/fixtures/rename_impact_guard/` -- both confirming no
  worked-example name is a required literal.
- **Verdict**: PASS, conditioned on T041/T042 actually landing with teeth (a
  real grep assertion, not a comment). This is a BUILD-STAGE guard, not a
  spec defect: the design as written keeps the rule generic; the risk is
  purely in execution discipline at implementation time.

## Axis 4 -- Fabricated confidence

- data-model.md Entity 5 fixes `Finding.severity` at `Severity.ERROR` only --
  "HR9 has no WARNING tier; a reference either resolves or it is a genuine
  orphan (binary, hard rule #9 posture)." FR-012 states this explicitly:
  "HR9 MUST NOT emit or require any numeric confidence/health/maturity/
  completeness score... a table either has zero HR9 findings (clean) or
  one-or-more (blocked)."
- tasks.md T008 wires `docs/rules/severity-posture.json` with `"HR9":
  ["error"]` only, explicitly declining to copy HR1's `["error","warning"]`
  two-tier shape. T040 is a dedicated test asserting no `Finding.message`
  contains "a numeric percentage, ratio, or 'N of M' style confidence/
  health/maturity/completeness phrasing."
- No artifact anywhere in the six documents introduces a score, percentage,
  weighting, or maturity level. Entity 3's `OrphanedReference.reason` field
  is a human-readable string ("no column named X in table Y's current
  TMDL"), not a numeric field.
- **Verdict**: PASS. Clean binary posture throughout, with an explicit
  regression test (T040) guarding it.

## Axis 5 -- Over-scope

- **Collision-avoidance allocation compliance**: the feature is scoped to
  the reserved id HR9 only; a live repo-wide grep for `HR9` found matches
  only inside this feature's own spec directory -- no other in-flight
  feature or shipped rule claims it, confirming the allocation is clean as
  of this branch's base (tasks.md T001 tasks exactly this confirmation).
- **No shared-schema addition**: research.md Sec 2.1 states explicitly that
  HR9 is "manifest-less by design" -- unlike SC1/DF1/SF1 (each backed by a
  hand-curated `docs/quality/*.yaml`), both of HR9's sets (truth set,
  reference set) are DERIVED from already-committed TMDL/YAML/Markdown, so
  no new manifest schema is introduced. A live check of `docs/quality/`
  confirms no HR9-related file is proposed anywhere in tasks.md. This
  directly satisfies the SCOPE GUARD's "reuses SC1/DF1 manifest pattern --
  no shared-schema addition" clause.
- **No auto-rename**: FR-009 explicitly forbids HR9 from deciding which name
  is correct, editing any file, or suggesting a replacement; it "names the
  orphaned reference and the artifact that carries it, and stops." T039 adds
  a source-inspection test asserting the rule module contains no
  file-write/open-for-write call anywhere, mirroring SF1's own
  write-absence test. This directly satisfies the SCOPE GUARD's "MUST NOT
  auto-rename" clause.
- **No execution**: FR-010 forbids DAX execution, a live DB connection, or a
  live PBIP surface; already independently confirmed clean under Axis 2.
  This satisfies the SCOPE GUARD's "no execution" clause.
- **No score**: already independently confirmed clean under Axis 4. This
  satisfies the SCOPE GUARD's "no score" clause.
- **Boundary discipline against neighbouring features**: spec.md's "Boundary
  against neighbouring shipped work" section draws five explicit lines (SC1,
  DF1, HR1, SF1, spec 099) and none of the six artifacts blurs any of them --
  HR9 does not touch `docs/quality/parked-on.yaml`, `docs/quality/shared-
  spine.yaml`, or `conformed-dimension-map.yaml`; it does no fuzzy matching
  (099's territory); research.md Sec 2 independently re-confirms each
  boundary by inspection rather than merely restating the spec's claim.
- **Verdict**: PASS. The feature does exactly one job (static cross-artifact
  reconcile on the model surface) and stays inside the collision-avoidance
  allocation's stated bounds on every sub-clause of the SCOPE GUARD.

## Notes (non-blocking, build must honor)

- **N-1 (MEDIUM-HIGH, inherited from analysis.md F1 -- off-axis for this
  review but load-bearing for correctness)**: tasks.md T037's no-op
  condition for FR-007/US3/SC-005 is written in tree-global language ("does
  not resolve to ANY TMDL table anywhere in the tree" / "TMDL model surfaces
  exist elsewhere in the tree"), which -- read literally -- would make a
  newly onboarded table's contract-column references fire as false orphans
  the moment ANY other table in the repo has a committed TMDL (already true
  today via `retail_store_sales`). This is a task-authoring ambiguity, not a
  violation of any of the five axes above (it does not self-grant an
  approval, does not assume a deferred capability, does not leak a
  worked-example name, does not fabricate a score, and does not expand the
  feature's scope) -- but if implemented per the literal tree-global reading
  it would break FR-007/US3/SC-005's own guarantee. BUILD MUST: key the
  no-op condition on "does the referenced table's OWN model folder have at
  least one committed TMDL file," never on tree-global TMDL existence, per
  Entity 1's folder-scoping discipline and FR-007's already-correctly-scoped
  text ("A table with metric contracts but no TMDL model surface yet").
- **N-2 (LOW)**: data-model.md Entity 2b documents, honestly and explicitly,
  that every unqualified DAX bracket token is assumed to be a measure
  reference and every qualified token a column reference, because "DAX has
  no such [unqualified-column] form in practice on this model." This is a
  disclosed, not silent, limitation. BUILD MUST: keep this assumption
  visible in the rule's own docstring/comments (not just the design doc) so
  a future maintainer does not rediscover it the hard way; no task currently
  tests the failure mode it describes, which is acceptable for this feature's
  scope but should not be forgotten.
- **N-3 (LOW)**: spec.md FR-014 cites "the HR6 FR-017 precedent" as an
  established pattern, but a repo-wide grep confirms HR6 has no shipped rule
  source anywhere in the tree -- only references inside other in-flight,
  unshipped specs (092/103/105). research.md Sec 2 already self-corrects
  this ("a NAMING CONVENTION... not a file to open or depend on"), and no
  task actually depends on HR6 code, so there is no implementation risk.
  BUILD MUST NOT: attempt to read, import, or depend on any HR6 file --
  none exists.
- **N-4 (LOW, cosmetic)**: spec.md SC-007 and tasks.md T002/T003/T046 refer
  to both gate docs' "Blocking reasons" sections as a "table," but a direct
  read of `docs/readiness/dashboard-ready.md` shows that section is a
  bullet list, not a Markdown table (only `semantic-model-ready.md`'s
  section arguably qualifies, and T002 itself hedges with "section/table").
  BUILD MUST: add the HR9 line in whatever structural form (table row or
  bullet) each doc already uses -- do not introduce a new Markdown table
  into `dashboard-ready.md` just to satisfy the word "table" in SC-007.
- **N-5 (LOW, naming-convention footnote, not a defect)**: tasks.md T004
  names the new module `rename_impact_guard.py` (a descriptive-name
  pattern, matching `status_claims.py`/`parked_on.py`), while the most
  recently shipped sibling rule SF1 used `rule_sf1.py` (an id-based
  pattern). Both patterns already coexist in `src/retail/rules/`
  (confirmed: `status_claims.py`, `parked_on.py`, `rule_sf1.py`,
  `rule_ap1.py` all present). No artifact asserts a single mandatory
  file-naming convention, so this is not a contradiction -- flagged only so
  the implementer does not need to second-guess the choice.

## Verdict

Verdict: PASS-WITH-NOTES

Rationale: No CRITICAL or HIGH finding on any of the five review axes.
Axis 1 (hidden principle violation): PASS -- Q-APPROVAL-SEAM stays genuinely
OPEN, and the rule's own resolution logic is mechanical fact-lookup, not a
Principle-V judgment call. Axis 2 (deferred capability): PASS -- F016 and
any live DB surface are consistently and correctly treated as non-existent
across all six artifacts. Axis 3 (c086 leak): PASS -- the rule logic itself
(normalize_qualifier, the truth-set/reference-set derivation) is fully
generic; the worked example is used only as a cited, inspected instance,
matching the 068/AD1 precedent, conditioned on T041/T042 landing with real
grep teeth. Axis 4 (fabricated confidence): PASS -- strictly binary
ERROR-only output, with a dedicated regression test (T040) and an explicit
single-tier severity-posture wiring (T008) guarding it. Axis 5 (over-scope):
PASS -- the feature satisfies every clause of its own SCOPE GUARD
(manifest-less/no-shared-schema, no auto-rename via T039's write-absence
test, no execution, no score) and respects every boundary line drawn against
SC1/DF1/HR1/SF1/spec-099. One MEDIUM-HIGH note (N-1, inherited from
analysis.md's F1) is a genuine correctness risk for the BUILD stage --
T037's tree-global-vs-folder-scoped no-op language could silently break
FR-007/US3/SC-005 the first time it is implemented literally -- but it is a
task-authoring ambiguity, not a violation of any of the five review axes,
and does not block ratification: FR-007's own requirement text is already
correctly table/folder-scoped, so the fix is confined to tightening T037's
wording before implementation, not to the spec or plan. The remaining four
notes (N-2 through N-5) are low-severity build guidance. The one genuine
Principle-V item (Q-APPROVAL-SEAM, FR-016) is correctly left OPEN for an
owner ruling rather than self-decided by any artifact. The draft is
ratifiable; the human ratifier should (a) note N-1 as a build-time
instruction to the implementer, and (b) confirm Q-APPROVAL-SEAM's pending
default (MECHANICAL, no new approval seam) remains pending pending their own
ruling, not adopted by this review.
