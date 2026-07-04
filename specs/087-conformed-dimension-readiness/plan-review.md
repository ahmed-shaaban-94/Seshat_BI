# Adversarial Plan-Review: Cross-Star Conformed-Dimension Readiness Gate (HR1)

**Feature**: `087-conformed-dimension-readiness` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md, analysis.md.

**Precondition check**: spec.md, plan.md, tasks.md, and `analysis.md` are ALL
present. `speckit-analyze` HAS been run for 087 (verdict: 16/16 FRs and 7/7 SCs
covered, no CRITICAL/HIGH finding, no contradiction, no constitution violation,
no deferred-capability leakage -- three LOW/LOW-MEDIUM findings F1/F2/F3). This
review leans on that clean analyze verdict the way the 061 gold-standard review
leans on its own analyze pass, and additionally performs its own independent
ground-truth verification below rather than trusting either artifact's
self-report at face value.

**Ground truth verified directly against the worktree** (not merely the plan's
or analysis.md's self-report): live rule count is **55**
(`docs/quality/rule-count-claims.yaml` `claimed-count: 55`;
`docs/rules/rules-manifest.json` parses to a JSON list of exactly 55 entries) --
matches plan.md's "56th rule" claim. `docs/quality/conformed-dimension-map.yaml`
and `src/retail/rules/rule_hr1.py` both confirmed **absent** from the live tree
-- matches plan.md's "Status: Draft, not implemented" claim. `grep -rn "HR1"
src/ docs/ tests/` (excluding `specs/087-*`) returns **zero** hits -- the id and
the `HR` family letter are genuinely free; no collision with any of the 19
parallel in-flight features as of this read. Both committed stars parse and
carry `gold_star.fact`:
- `retail_store_sales` (rich form): dims
  `gold.dim_customer_rss` / `gold.dim_product_rss` / `gold.dim_payment_method_rss`
  / `gold.dim_location_rss`, PLUS a standalone `date_dimension:` block
  (`gold.dim_date_rss`, `surrogate_key: date_sk`, `contiguous: true`), PLUS
  `degenerate_dimensions: [transaction_id, discount_applied]`. Each dimension
  carries `surrogate_key` (e.g. `dim_product_rss` -> `product_sk`) and a
  top-level `columns[]` block whose `gold_placement` values
  (`dim:dim_product.item`, `dim:dim_product.category`, etc.) support the type
  join.
- `demo_sample_orders` (compact form): dims `dim_product` / `dim_store` /
  `dim_payment` / `dim_date` (the date dim is an INLINE entry with
  `built_from: order_date`, no standalone `date_dimension:` block, confirming
  the two recognized forms are both real). NO `surrogate_key` on any
  dimension, NO top-level `columns[]` block at all -- confirms the
  graceful-degradation claim is not hypothetical.
- The two stars share **zero** dimension names (`dim_product` vs.
  `gold.dim_product_rss`, etc.) -- confirms the "empty-scaffold lands green
  honestly" claim below is traceable to a verified fact, not an assertion.
- `retail_store_sales`'s `dim_product` natural key is `item`, listed SECOND in
  `attributes: [item, category]` (not first, not `_id`-suffixed) -- independently
  confirms research.md's claim that neither a first-position nor an
  `_id`-suffix heuristic survives contact with the committed tree, i.e. the C3
  grain-signal deferral is not a scope shortcut but a genuine mechanics gap.

## Axis 1 -- hidden-principle-violation

Probe: does HR1 secretly self-grant an approval, decide a Principle-V judgment
call, or advise-instead-of-block?

- The core mechanism is read-only by construction: `conformed-dimension-map.yaml`
  is human-authored (FR-002, FR-011); HR1 only reads it and never rules an
  actual `conformed` vs `distinct` collision (spec Assumptions, data-model.md
  "Human-authored, never machine-generated"). An undeclared collision is never
  inferred as conformed-by-default -- it is a fail-closed ERROR demanding the
  human ruling (FR-006). This is the correct Principle-V shape and mirrors
  SF1's proven pattern exactly. analysis.md's Constitution-Alignment table
  reaches the same conclusion independently (Principle V row: "Satisfied
  (verified, not merely asserted)").
- **The load-bearing question an adversarial reviewer must not wave past**:
  T002/T003 have the agent author the manifest's initial content
  (`dimensions: {}`), and that scaffold is what lands `retail check` GREEN
  under FR-010 (a missing map with 2+ stars is otherwise a fail-closed ERROR).
  Is authoring the file that makes the gate pass a disguised self-grant? Traced
  through, and independently re-verified in this pass (direct parse of both
  files, above): no. The two committed stars share **zero** dimension names
  today -- so there is no collision to adjudicate and no Principle-V ruling is
  being bypassed by the empty scaffold. The green is EARNED (there is
  genuinely nothing to declare on this tree), not manufactured. This matches
  analysis.md's independent re-verification of the same claim via direct grep
  of both `source-map.yaml` files. FR-016 reinforces the guard: no
  model-level "pass" is recorded anywhere by a clean HR1 run (Findings only),
  so even the mechanical green carries no side-effect that could be read as a
  recorded approval.
- **Forward guard (carried into Notes)**: this reasoning is tree-state-dependent,
  not permanent. If a future tree introduces a genuine same-named collision
  between two stars, an empty (or stale) manifest at that point would no
  longer be a safe agent scaffold -- it would be papering over an actual
  Principle-V ruling the agent must not make. The plan does not claim
  otherwise, but this is worth restating explicitly since it is the single
  place this feature's "green" could quietly turn into a self-grant if the
  tree changes without the manifest being re-authored by a human.
- FR-016 (Q-APPROVAL-SEAM) is correctly left OPEN rather than silently settled
  -- the plan explicitly declines to invent a new `approvals[]` shape and
  proceeds on a PENDING DEFAULT the owner may later overturn (plan.md Summary,
  tasks.md T048 "do not answer"). No grain/PII/business-rollup/product-identity
  call is answered anywhere in the artifact set.
- The C3 grain-limb deferral (research.md) is a schema/mechanics gap, correctly
  distinguished from a Principle-V judgment: HR1 re-decides no table's own
  grain, it would only read a marker that does not exist yet. The plan does not
  smuggle in a first-attribute or `_id`-suffix heuristic to make the grain limb
  "work" -- it explicitly rejected both after testing them against the two real
  instances (research.md, independently reconfirmed above) and marked the limb
  PENDING instead.

Verdict: **PASS**. No hidden self-grant; the empty-scaffold green is earned, not
manufactured, and is traceable to a verified fact (zero shared dimension names
today), not an assertion taken on faith.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- HR1 is 100% static: `ctx.tracked_files` reads only, lazy `import yaml` kept
  out of the static-core chain (mirroring SF1), no database connection, no
  Power BI/PBIP surface read (plan.md Constitution Check row VIII; FR-003).
- F016 (Power BI execution adapter) is explicitly named as NOT existing and
  never invoked (research.md "Deferred capabilities NOT assumed"; spec
  Overview). analysis.md's dedicated Section F ("Deferred-Capability Leakage
  Scan") checks all six artifacts individually and finds no leak in any of
  them -- consistent with this review's own reading.
- Live cross-star DATA reconciliation is explicitly named as OUT of scope and
  deferred to a future `retail validate` surface (spec Assumptions,
  plan.md Summary) -- HR1 proves declared shapes agree, not materialized data.
- The grain limb is the interesting case: rather than assuming a natural-key
  marker will exist, the plan marks it `[PENDING SCHEMA PREREQUISITE]` in code
  (T022) and defers it to a cross-feature prerequisite OUTSIDE this feature's
  collision-avoidance allocation (research.md C3). This is the opposite failure
  mode from "assumes a deferred capability" -- it refuses to build against an
  input surface that does not exist, which is the correct Principle VIII
  posture (author static structure, mark pending explicitly).

Verdict: **PASS**. No deferred capability is assumed to exist; the one
mechanically-blocked limb (grain) is honestly marked pending rather than faked
with an unenforced heuristic.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- The rule logic and data-model.md's manifest shape use only illustrative
  placeholders (`dim_product`, `dim_store`, `dim_date`, `star_a`/`star_b`),
  explicitly marked as such in every artifact (spec FR-013, data-model.md
  header, quickstart.md header).
- FR-013 explicitly forbids inlining C086/pharmacy dim names, grain keys, or
  column names into the rule logic or the manifest template, and T044 is a
  dedicated grep-verification task for this at build time.
- The one place a REAL name is named at all is research.md's own analysis,
  which cites `retail_store_sales`'s actual `gold.dim_product_rss` /
  `demo_sample_orders`'s actual `dim_product` -- but this is in the
  research/precedent-survey artifact (a citation of the existing tree used
  to justify a design decision), not baked into the rule module or the
  manifest template T003 will author. T003's own scaffold is specified as an
  EMPTY `dimensions: {}` plus illustrative-only header comments -- it does
  not paste the real `demo_sample_orders`/`_rss` shapes into the committed
  template. analysis.md's Principle VII row reaches the same conclusion
  independently.
- Watch item for the implementer (carried forward as a note, not a spec
  defect): T003's authoring-comment header must stay illustrative
  (`# e.g. dim_product`) and never literally copy the real
  `gold.dim_product_rss` / compact-form field names from the two committed
  instances into the new file's comments -- that would be the one live leak
  surface this feature could introduce that T044's grep is specifically
  positioned to catch.

Verdict: **PASS**. No c086/pharmacy specifics are baked into rule logic or the
template; the one real-name citation lives in research.md's precedent-survey
prose, which is the correct place for it.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- `ConformanceFinding` reuses the existing `Finding` dataclass unchanged
  (`rule_id`/`severity`/`message`/`locator`) -- no new numeric field is added
  anywhere (data-model.md "Non-goals", FR-012).
- FR-012 explicitly forbids a numeric conformance score, a completeness count,
  or an "N of M" / "% conformed" tally, and T043 is a dedicated mechanical test
  (grep the rule module and every emitted message string for percentage/ratio/
  "N of M" formatting) rather than a review-only claim -- this is a stronger
  verification posture than a docstring promise.
- The one integer in the whole feature -- the rule COUNT (55 -> 56) -- is not a
  conformance score; it is the SAME `len(rules-manifest.json)` mechanism every
  other rule addition uses (SC2's existing reconciliation), independently
  re-verified live against the tree at 55 in this pass (JSON parse, above). It
  is correctly hedged in plan.md as "re-verify against the live manifest at
  implement time" given 19 parallel in-flight features, rather than asserted
  as a hard fact that could drift stale.
- No maturity/health label is introduced; Findings remain categorical
  (ERROR/WARNING) only, matching the existing `Severity` enum. analysis.md's
  hard-rule-#9 row reaches the same conclusion independently.

Verdict: **PASS**. No fabricated or invented number anywhere; the one integer
present (rule count) is an authoritative `len()`, not a score, and is
explicitly flagged as re-verify-at-implement-time rather than asserted as
settled.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are tightly bounded: one new rule module (`rule_hr1.py`), one
  new manifest file (`conformed-dimension-map.yaml`), the six-surface wiring
  lockstep every new rule already requires, and one new fixture corpus. This
  matches the SF1/AP1 sibling scope exactly (plan.md Project Structure).
- The plan explicitly REFUSES two scope-expansion temptations that would have
  been easy to fold in: (a) it does not add a natural-key marker key to
  `source-map.yaml` to make the grain limb work, even though that would have
  "completed" FR-005 -- because that schema is a SHARED surface outside this
  feature's collision-avoidance allocation (research.md C3, spec FR-004); (b)
  it does not invent an `approvals[]` shape or a new `readiness-status.yaml`
  key to answer FR-016, even though that would have made the model-level tier
  feel more "finished" -- because that is an open Principle-V governance-shape
  question for the owner (FR-016, tasks T048). Both refusals shrink scope
  rather than expand it, which is the correct discipline given 19 parallel
  features sharing adjacent surfaces.
- It adds NO eighth readiness stage and touches NO
  `mappings/<table>/readiness-status.yaml` (FR-001, verified: plan.md's file
  footprint lists `readiness-model.md`/`gold-ready.md` as REFERENCE ONLY,
  unedited).
- It does not touch `shared-spine.yaml` or `rule_sf1.py` (SF1's own manifest
  and module) despite reusing SF1's shape -- the boundary section in spec.md
  and research.md is explicit and the plan's file footprint confirms no edit
  to either.
- It does not re-decide any table's own grain/PK/placement (those remain that
  table's Mapping Ready judgment, per Assumptions) and does not touch
  `retail validate` or any live reconciliation surface.

Verdict: **PASS**. Scope is disciplined and, notably, actively resists two
plausible scope-creep paths (schema edit for grain, invented approval shape)
rather than merely avoiding accidental overreach.

## Notes / carry-forward (non-blocking)

- **`analysis.md`'s own findings (F1/F2/F3) are adopted here as N-notes**,
  independently re-checked against the underlying artifacts rather than
  copied at face value; none flips an axis or touches the SCOPE GUARD/hard
  rule #9:
  - **F1 (LOW)**: SC-002's prose still names "grain" as one of three
    mutation-verified divergence axes ("diverges ... on grain, key, or a
    shared attribute's type"), while FR-005/research.md C3/tasks.md T022 all
    consistently defer the grain limb this feature. Confirmed: T022 is a code
    comment, not an implementation, so there is no functional gap, but
    SC-002's literal wording over-promises relative to what actually ships.
    Recommend narrowing SC-002 to name only key and type (or adding a
    parenthetical pointing at C3) before/while this lands.
  - **F2 (LOW)**: "moot distinct" (a `distinct` entry whose stars have
    "become identical in shape") is undefined for a pair spanning one
    rich-form and one compact-form star, where the graceful-degradation rule
    means only the dimension NAME is genuinely comparable on both sides. No
    artifact states whether "identical in shape" here means "every
    comparable field happens to agree" (vacuously true when nothing is
    comparable) or "at least one limb was actually comparable and agreed."
    Not live on the current tree (no `distinct` entries exist yet); affects
    only the WARNING-level moot-distinct case. Recommend the implementer
    resolve it explicitly in `rule_hr1.py` with a code comment recording the
    choice, per analysis.md's own recommendation.
  - **F3 (LOW-MEDIUM, the most substantive of the three)**: data-model.md
    states a star's "identity string" for the manifest's `stars:` list is
    either `meta.table_id` (rich form) or `source_id` (compact form), but no
    artifact states which literal string a human author should write for a
    given table, nor whether HR1 normalizes both conventions to one canonical
    identity before matching. Independently confirmed in this pass: the two
    committed stars use two DIFFERENT identity conventions today
    (`retail_store_sales` is rich-form; `demo_sample_orders` is
    schema-bare/compact, keyed by directory name) -- a real author filling in
    `conformed-dimension-map.yaml` by hand has no documented rule to follow,
    which could produce a confusing FR-010 false-positive/false-negative
    ("unresolvable star") purely from picking the wrong string. Does not
    violate any constitution principle and does not affect the current
    empty-manifest landing (no real entries exist yet to misauthor). Recommend
    pinning down one canonical identity-resolution rule in data-model.md (or
    in `rule_hr1.py`'s `_discover_stars` docstring) before a human is asked to
    author a real entry.
- **The MVP's real-tree enforcement value is currently prospective, not
  active.** Because of the graceful-degradation rule (compare only fields
  present on both sides of a pair) and because the two committed stars share
  no dimension name today, a declared-conformed pair spanning the rich form
  (`retail_store_sales`, has `surrogate_key` + `columns[]` type join) and the
  compact form (`demo_sample_orders`, has neither) would today check only the
  shared NAME -- key and type comparisons degrade to no-ops wherever the field
  is absent on either side, and grain is deferred entirely. research.md
  records this honestly (Landing precondition, graceful-degradation rule) and
  it is not a defect the plan introduces -- correctly refusing to edit the
  shared `source-map.yaml` schema to manufacture a false positive rate is the
  right call. But it means SC-001's "zero ERROR findings" on the current tree
  should not be read as "conformance is actively being validated" -- it is
  validated only once two stars in the RICH form both declare the same
  dimension name conformed. Implementers and reviewers should not overclaim
  HR1's live bite until a second rich-form star exists.
- **Keep T003's manifest scaffold illustrative, never a copy of the real
  instances.** The only realistic c086-leak vector this feature could
  introduce is pasting `demo_sample_orders`'s or `retail_store_sales`'s actual
  field/dimension names into the new manifest's authoring-comment header
  instead of a placeholder (`dim_product`, `star_a`). T044's grep is
  positioned to catch this at build time; keep it in the task list as a hard
  gate, not a courtesy check.
- **The rule-count claim (55 -> 56) is a live serialization point.** Verified
  55 as of this review; plan.md already correctly hedges that other in-flight
  rule-adding features may land first and change the number the implementer
  must target. No action needed beyond honoring plan.md's own instruction to
  re-verify at implement time.
- **FR-016 stays genuinely open.** No task in tasks.md answers Q-APPROVAL-SEAM;
  T048 is explicitly a "do not answer" checklist confirmation. This is correct
  and should stay this way through implementation -- any future edit that adds
  an `approvals[]` shape for this tier without an owner ruling would flip Axis
  1 to a violation.
- **The empty-scaffold "green" is tree-state-dependent, not a permanent
  property.** Restated from Axis 1: if a future tree introduces a genuine
  cross-star name collision, the agent may no longer author or leave an empty
  manifest to keep the gate green -- that would become a disguised self-grant
  at that point, not the currently-earned one. This is implicit in the spec's
  own logic but worth stating explicitly as a guard for whoever implements or
  re-reviews this feature later.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification, not merely on the
plan's or analysis.md's self-report (rule count, manifest/module absence, both
stars' actual shapes, and id/family freedom were independently re-checked
against the live tree in this pass). `analysis.md` is present and clean (16/16
FR coverage, 7/7 SC testability, no contradiction, no constitution violation,
no deferred-capability leakage), and its three findings (F1 wording gap on
SC-002, F2 moot-distinct ambiguity under graceful degradation, F3 star-identity
convention underspecified) are adopted here as non-blocking N-notes after
independent re-verification -- none of them touches the SCOPE GUARD or hard
rule #9, and none flips an axis. The design is notably disciplined: it defers
a mechanically-unimplementable limb (grain) rather than faking it with an
unenforced heuristic, and it actively refuses two plausible scope-creep paths
(a `source-map.yaml` schema edit, an invented approval shape) rather than
merely avoiding them by omission. No CRITICAL or HIGH finding; no axis is RISK
or FAIL.
