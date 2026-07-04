# Adversarial Plan-Review: Customer / Loyalty Grain + Dimension Pattern

**Feature**: `098-customer-loyalty-grain` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md are present. **`analysis.md`
does NOT exist in this feature directory** -- `speckit-analyze` has not been run
for 098, so there is no cross-artifact analyze verdict to cite (same gap the
087 review recorded for its own feature). This review does not fabricate that
precondition; it proceeds on spec + plan + tasks + research.md + data-model.md
+ quickstart.md, and performs its own ground-truth verification in place of an
analyze pass. Recorded as a non-blocking N-note, not a BLOCKED precondition --
the six artifacts present are internally consistent and independently
verifiable against the live tree.

**Ground truth verified directly against the worktree** (not merely the plan's
self-report):

- `docs/patterns/` does **not** exist yet; neither
  `docs/patterns/customer-dimension-pattern.md`,
  `docs/patterns/customer-grain-pattern.md`, nor `templates/customer-dimension.md`
  is present in the current tree -- matches plan.md's "Status: Draft... none is
  authored by this planning stage" precondition.
- `skills/retail-kpi-knowledge/domains/customer.md` (spec 042) is confirmed on
  disk exactly as research.md describes: four Planned KPIs, four Principle-V
  stop bullets, no Seeded row -- and this review confirms the file is not
  edited by anything in 098 (no task targets it; FR-008).
- `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` and
  `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold
  dim_customer_rss.tmdl` both exist and are the real, already-shipped
  table-scoped instance the spec/plan cite -- `dim_customer_rss` is confirmed
  to be a bare two-column dimension (`customer_sk`, `customer_id`) with no SCD
  marker and no identity-resolution shape, matching research.md's "structurally
  thinner" characterization exactly.
- `mappings/retail_store_sales/unresolved-questions.md` Q1 is confirmed:
  "Proposed default (if unanswered): RC4 default = DROP before the BI layer.
  Agent RECOMMENDS keep... pending sign-off" -- KEEP was the table's own
  governance-approved deviation from the repo-wide DROP default, not a
  pattern-level default.
- `templates/source-map.yaml` is confirmed to already carry the
  `gold_star.dimensions[].name` / `.surrogate_key` / `.has_unknown_member` /
  `.attributes[]` fields FR-014/data-model.md say the new template maps onto --
  no new key is required for citability to work.
- **`docs/decisions/0002-retail-cleaning-defaults.md` RC4 reads: "Default to
  dropping PII; if a need exists, hash/mask or isolate... Override when...a
  governance sign-off explicitly permits it."** `domains/customer.md` restates
  this verbatim for the customer domain specifically: "The default is DROP,
  and Governance must sign off before any customer identifier is published."
  **Neither RC4 nor this DROP-default language is cited anywhere in 098's
  spec.md, plan.md, research.md, data-model.md, tasks.md, or quickstart.md** --
  grep for `RC4` across the entire `specs/098-customer-loyalty-grain/` tree
  returns zero matches. See Axis 1 for the resulting finding.

## Axis 1 -- hidden-principle-violation

Probe: does the spec secretly self-grant an approval, decide a Principle-V
judgment call, or advise-instead-of-block?

- The core posture is correct and repeatedly reinforced: every load-bearing
  slot (identity key, PII-publish, SCD/historization, retention window, CLV
  horizon, new-vs-returning anchor) is named as an explicit
  `[NEEDS CLARIFICATION: ... -- owner ruling]` marker and decided by neither
  document nor the template (FR-002, FR-004, FR-005, FR-006; Clarify Q5
  explicitly re-affirms all five stay OPEN). No `approvals[]` entry is
  recorded, no readiness stage is advanced or self-granted (FR-009, FR-015).
  This is the same fail-closed "raise and stop" shape the constitution
  requires and that the 087 sibling review found PASS on.
- **Finding (non-blocking, but a real factual gap the build must close)**: the
  spec's own framing of the PII-publish slot is imprecise in a way that
  understates an EXISTING, already-cited-elsewhere default. FR-002 requires
  the slot be "marked as an unresolved ruling (not defaulted to keep or
  drop)"; the Edge Cases section requires the doc state "explicitly that no
  default is implied." But the repo already has an operative, unedited,
  fail-closed default for exactly this case: RC4 ("default to dropping PII")
  and `domains/customer.md`'s restatement ("The default is DROP... Governance
  must sign off before any customer identifier is published"). The spec never
  cites RC4 anywhere and frames "no default" as if the slot starts from a
  blank slate, when the correct framing (and the one C086's own Q1 actually
  used: "Proposed default = DROP (RC4)... agent recommends keep, pending
  governance sign-off") is "defaults to DROP per RC4/domains/customer.md;
  overriding to keep requires named governance sign-off," matching Principle
  VI (Defaults-Then-Deviations) rather than presenting the slot as
  default-free.
  - **Why this does not rise to a blocking violation**: this feature ships no
    rule, no gate, and no enforcement surface (verified: zero `retail check`
    wiring, docs-only). A doc that under-cites an existing default cannot
    itself override that default -- RC4 continues to govern every real
    table's PII decision via `source-map.yaml`/`unresolved-questions.md`
    regardless of what this pattern doc says or omits. The practical effect is
    under-documentation (a reader of the new pattern doc alone would not learn
    that DROP is the fail-safe starting point), not a self-granted or
    silently-flipped ruling. No table's PII outcome is decided or defaulted by
    this feature.
  - **Build-time fix (see Notes)**: the PII-publish slot in both
    `docs/patterns/customer-dimension-pattern.md` and
    `templates/customer-dimension.md` should cite RC4 by id, state the
    fail-safe default is DROP, and state that KEEPING requires explicit
    governance sign-off (mirroring C086's own recorded pattern) -- while still
    carrying the `[NEEDS CLARIFICATION: PII publish-safety not ruled -- owner
    ruling]` marker and deciding nothing for any real table.
- Identity resolution across multiple raw ids is correctly named as a
  reserved owner ruling with a cross-reference to `domains/customer.md`,
  proposing no merge algorithm (FR-005, User Story 3) -- the sharpest
  Principle-V edge in the feature is not smuggled past.
- The SCD/historization slot (Clarify Q4) genuinely decides nothing -- it
  names Type 1 and Type 2 as options and defaults to neither, and there is no
  pre-existing repo-wide SCD default (unlike PII/RC4) to under-cite here.

Verdict: **PASS**. The RC4/PII framing gap is real and must be fixed at build
time, but it is a documentation-completeness gap, not an operative self-grant
or a decided Principle-V ruling -- this feature has no enforcement surface
capable of overriding RC4, and RC4 continues to govern every real table's PII
outcome untouched.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016 / a live DB / a running adapter exists?

- FR-013 explicitly forbids a live database connection, an F016 invocation, or
  any assumed live-profile result; research.md's "Deferred capabilities NOT
  assumed" section names F016 explicitly as gated + LAST and not invoked.
- The technical approach is verified as docs + one template only: no code, no
  CLI, no `src/retail/rules/` entry (plan.md Technical Context, Project
  Structure; verified no such path is listed anywhere in tasks.md).
- The one place a live surface could plausibly sneak in -- `retail check`
  (T014) -- is confirmed to be a STATIC gate run, not a live DB check; the
  task only confirms the existing rule count is unchanged, matching Principle
  VIII's "author static structure, mark live PENDING" posture.
- No task requires a live-profiled real table; the pattern/template are
  explicitly readable and verifiable "in isolation" per every User Story's
  Independent Test, before any real table exists.

Verdict: **PASS**. No deferred capability is assumed anywhere in the artifact
set; static-only posture is consistent across spec, plan, research, and tasks.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- FR-011 explicitly forbids inlining any C086/`retail_store_sales` column
  name, table name, or ruling as a default anywhere in the two new pattern
  docs or the new template; T010 is a dedicated grep-verification task at
  build time for exactly this (`retail_store_sales`, `customer_id`, "keep"/
  "drop" as a filled default).
- research.md and data-model.md DO name `customer_id` and "keep, no raw PII"
  directly -- but only in precedent-survey / illustration prose describing the
  ALREADY-SHIPPED `dim_customer_rss` instance, explicitly labeled "STAY
  DISTINCT... never `customer_id` or 'keep' baked in as the shown example."
  This is the same place the 087 sibling review found acceptable ("the one
  real-name citation lives in research.md's precedent-survey prose, which is
  the correct place for it") -- the leak guard (FR-011/SC-003/T010) targets
  the AUTHORED pattern docs and template, not the planning-stage research
  artifact that exists precisely to document what to avoid.
- data-model.md's illustrated slots use only generic markers (the canonical
  `[NEEDS CLARIFICATION: ...]` string, `customer_sk`, `dim_customer`) -- no
  field name candidate (`email`, `phone`, `loyalty_id`) is ever presented as
  a filled value, only as an explicit list of names the slot must NOT default
  to (spec Acceptance Scenario 2, data-model.md IdentityKeySlot).
- The template's schema-mapping claim (FR-014) targets the EXISTING generic
  `templates/source-map.yaml` fields (`.name`, `.surrogate_key`,
  `.has_unknown_member`, `.attributes[]`) -- verified on disk to already be
  generic placeholders (`dim_<entity_a>`, `<entity_a>_sk`), not C086-specific.

Verdict: **PASS**. No C086/pharmacy/retail_store_sales specifics are baked
into the pattern docs or template as authored; the one real-name citation
lives in research.md's precedent-survey prose, which is the correct location
for it, matching the 087 precedent.

## Axis 4 -- fabricated-confidence

Probe: does the spec emit ANY numeric score/health/maturity/completeness
count?

- FR-010 explicitly forbids any numeric confidence/health/maturity/
  completeness score; data-model.md's "Non-goals" section states "No numeric
  field, percentage, ratio, or 'N of 4 KPIs covered' score anywhere... Coverage
  is expressed only as 'which slots are filled... vs. which remain an explicit
  owner ruling.'"
- **Watch item (non-blocking)**: SC-002 and SC-003/SC-004 are phrased as
  "100% of the four Planned customer KPIs have a corresponding
  candidate-grain entry... 0 of the four have a decided period length" and
  "0 new pattern/template files contain a C086-specific..." This is
  percentage/count language, but it appears only in the SPEC's own Success
  Criteria section -- a test-time measurement a reviewer/CI check computes
  ABOUT the artifacts from outside, never a number the authored pattern docs
  or template themselves display to a reader. T011 is a dedicated grep task
  confirming no percentage/health/count string survives inside the three
  authored files. The distinction (score emitted BY the artifact vs. score
  used TO VERIFY the artifact) is the same one hard rule #9 draws elsewhere in
  the repo (e.g. `retail check`'s own rule-count reconciliation is not itself
  a fabricated confidence score). The build must keep this distinction intact:
  the four-KPI coverage in `customer-grain-pattern.md` must read as four
  structural table rows, never as a "100%" or "4/4" string inside the doc.
- No maturity/health label is proposed anywhere; every readiness expression is
  categorical (slot filled vs. `[NEEDS CLARIFICATION]`), never numeric.

Verdict: **PASS**. No fabricated or invented number appears inside any
authored artifact; the SC-002/SC-003/SC-004 percentage framing is
external verification language, not an artifact-emitted score, but the build
must not let that phrasing leak into the doc content itself (T011 already
guards this).

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job / cross into
another feature's territory?

- Deliverables are tightly bounded to exactly three new files under two
  directories (`docs/patterns/`, `templates/`) plus this Spec-Kit chain's own
  planning docs -- verified: no task in tasks.md touches any existing file.
- The plan explicitly and repeatedly REFUSES plausible scope-expansion paths:
  it does not retrofit `dim_customer_rss` to the new pattern's shape (Edge
  Cases, FR-007); it does not seed a metric contract (FR-009, F009 stays the
  gated route); it does not edit `domains/customer.md`'s KPI table or stop
  section (FR-008); it does not add a copy-me template for the grain pattern
  even though FR-001 mandates one for the dimension (Clarify Q3 -- explicitly
  because a grain template would instantiate a chosen grain, itself a
  reserved ruling); it adds no new `source-map.yaml` schema key (FR-014,
  verified the existing fields already suffice).
- It adds NO new `retail check` rule and touches none of the six rule-wiring
  surfaces (collision-avoidance allocation; verified zero wiring-surface
  paths appear in tasks.md, matching the 087 sibling's wiring footprint
  exactly by contrast -- 087 touches six surfaces for its new rule, 098
  touches zero).
- It does not widen or narrow which readiness stages carry an `approvals[]`
  requirement (FR-015) and does not touch `mappings/**` for any table
  (verified: no task creates or edits a `mappings/<table>/` path).
- The one place scope discipline could have slipped -- naming a candidate
  identity field or a specific retention window "just to be concrete" -- is
  explicitly and repeatedly refused (FR-002 Acceptance Scenario 2's explicit
  list of forbidden field names; FR-004's explicit list of forbidden decided
  values).

Verdict: **PASS**. Scope is disciplined and matches its single Stage-2/
Stage-5 pattern-authoring job; no static rule, no schema edit, no metric
contract, and no existing file is touched.

## Notes / carry-forward (non-blocking)

- **PII-publish slot must cite RC4 and state the DROP default, not present
  the slot as default-free.** This is the one substantive build-time fix this
  review surfaces. `docs/decisions/0002-retail-cleaning-defaults.md` RC4 and
  `skills/retail-kpi-knowledge/domains/customer.md` ("The default is DROP")
  are both existing, cited-elsewhere, unedited defaults that 098's own spec
  never references (`RC4` appears zero times across the entire
  `specs/098-customer-loyalty-grain/` tree). `mappings/retail_store_sales/
  unresolved-questions.md` Q1 shows the CORRECT pattern already in production
  use: "Proposed default (if unanswered): RC4 default = DROP... Agent
  RECOMMENDS keep... pending sign-off." The new pattern doc and template
  should mirror that shape -- cite RC4, state DROP is the fail-safe default,
  state that KEEP requires named governance sign-off -- while still leaving
  the actual per-table answer as `[NEEDS CLARIFICATION: PII publish-safety not
  ruled -- owner ruling]`. This does not decide any table's PII ruling; it
  makes the pattern doc consistent with the repo's own existing
  Defaults-Then-Deviations convention (Principle VI) instead of implying the
  slot starts from a blank slate. Recommend adding this as an explicit FR-002
  sentence or a T005 authoring note before implementation.
- **`analysis.md` is absent for this feature.** `speckit-analyze` has not been
  run. This review substituted direct ground-truth verification (file
  absence/presence, `domains/customer.md` content, `dim_customer_rss` shape,
  `source-map.yaml` schema, RC4 grep) for the missing cross-artifact analyze
  pass, the same substitution the 087 review recorded for itself. Recommend
  running `speckit-analyze` before or during implementation.
- **Keep the SC-002/SC-003/SC-004 percentage framing external to the
  artifacts.** These Success Criteria correctly describe how a reviewer/CI
  verifies the docs from outside; T011's grep task is the right guard to keep
  that language from leaking into `customer-grain-pattern.md` itself as a
  displayed "100%" or "4/4" string.
- **Grain-pattern doc-only decision (Clarify Q3) is the correct Principle-V
  call and should not be revisited casually.** A future temptation to add a
  copy-me grain template "for completeness" would re-open exactly the
  period/horizon/anchor rulings this feature is designed to leave open --
  flag any such addition in a later feature as a fresh Principle-V check, not
  a natural follow-on to 098.
- **Identity-resolution section (US3/T008) is a same-file, sequential
  dependency on T005** -- confirmed correctly ordered in tasks.md
  (Dependencies & Execution Order); no parallel-execution risk of the two
  tasks clobbering each other's edits to
  `docs/patterns/customer-dimension-pattern.md`.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification against the live
tree (file absence/presence, `domains/customer.md` and `dim_customer_rss`
content, `source-map.yaml` schema, and a repo-wide RC4 grep), not merely on
the plan's self-report. The design is disciplined in the same register as its
087 sibling: it repeatedly refuses plausible scope-expansion and
default-smuggling paths (no grain template, no metric contract, no schema
edit, no restated Q1 default) rather than merely avoiding them by omission.
The one real finding -- the PII-publish slot's "no default implied" framing
omits the repo's own existing, cited-elsewhere RC4/DROP default -- is a
documentation-completeness gap, not an operative self-grant or a decided
Principle-V ruling, because this feature ships no rule and no enforcement
surface capable of overriding RC4; RC4 continues to govern every real table's
PII outcome regardless of this pattern doc's wording. It is recorded as a
non-blocking N-note the build must honor (cite RC4, state DROP is the
fail-safe default, state KEEP requires governance sign-off, while still
leaving the actual ruling to `[NEEDS CLARIFICATION]`). No CRITICAL or HIGH
finding; no axis is RISK or FAIL. Other non-blocking notes: `analysis.md` is
absent (ground-truth substitution applied, as 087 also required), the
SC-002/003/004 percentage framing must stay external to the artifacts
(T011 already guards this), and the grain-pattern doc-only decision (Clarify
Q3) should not be casually revisited by a later feature.
