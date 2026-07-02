# Adversarial Plan-Review: Additivity-Consistency Lineage Rule

Single default-adverse skeptic over spec.md, plan.md, tasks.md and the design artifacts.
READ-ONLY: findings report fixes; no artifact was edited by this review. Draft
completeness: spec + plan + tasks + research + data-model + contracts + analysis ALL
present (analyze ran clean) -> not an automatic BLOCKED.

## Axis 1 -- Hidden principle violation

- Finding (MEDIUM, note): The composition legality check depends on knowing HOW a child is
  composed (direct SUM vs base-over-base recompute). If the committed prose does not state
  the composition kind, the rule must NOT infer it -- inferring "this edge is a direct SUM"
  would be a metric-owner judgment (Principle V). The design already guards this
  (data-model: unknown composition_kind -> no verdict; only explicitly-stated illegal
  compositions ERROR). VERDICT: not a violation as specified, BUT the build must hold this
  line; a tempting "assume SUM by default" shortcut in T004 would cross into Principle V.
  Fix/guard: T013 already inspects for inference; add an explicit test that an edge with no
  stated composition kind yields NO composition verdict.
- Finding (LOW): Prose-word transcription (Q1) is safe under the strict exact-word framing.
  Confirmed the vocabulary is a genuinely closed 3-word set. No violation.

## Axis 2 -- Assumes a deferred capability

- No finding. The rule is a static text read; it assumes no Power BI execution adapter, no
  spec-only runtime, no live DB. Plan and tasks explicitly forbid an executor. CLEAN.

## Axis 3 -- C086 / worked-example leak

- Finding (MEDIUM, note -- the sharpest axis): The corpus chosen in Clarifications Q2 (the
  define-layer prose contracts) is, on `main` today, exactly the worked-example (El Ezaby)
  KPI-knowledge corpus -- the only filled additivity/lineage prose that exists. So the
  rule's real day-one input IS the example corpus. This is NOT itself a leak: the same is
  true of the shipped AL1, which globs the per-table contracts that today all live under the
  worked-example mapping. The leak test is the RULE CODE, and the design keeps it generic
  (generic glob, closed generic table, no worked-example metric names/ids/paths baked in;
  FR-006, T013). VERDICT: acceptable, matches shipped precedent. Guard: T013 must actually
  assert NO worked-example string (metric name, KPI-MC id, or path) appears in the rule
  module or the legality table -- keep that check teeth-in.
- Finding (LOW): The spec/plan reference the worked-example corpus only as the READ SOURCE
  location, never baking a name into the rule. Consistent with rule #7.

## Axis 4 -- Fabricated confidence

- No finding. Categorical ERROR/pass only; FR-002 forbids any score/confidence/threshold;
  T013 verifies. This is precisely why the band-based sibling (H5) was PARKED and H1
  ADOPTed. CLEAN.

## Axis 5 -- Over-scope

- No finding. Tasks Out-of-scope explicitly excludes: adding a structured
  additivity/derives_from field, the cross-corpus id join (FR-011 OPEN), the ambiguity-
  ledger check half, and any executor. Scope is one rule + tests + five wiring points.
  YAGNI respected. CLEAN.

## Open items correctly deferred to human (Principle V)

- FR-011: metric identity/uniqueness across the two corpora -- OPEN. (Not load-bearing under
  the single-corpus Q2 scope, but must be noted at ratification so future scope creep does
  not silently depend on it -- see analysis L2.)
- FR-012: the exact closed legality matrix as a ratified set -- OPEN. The rule enforces a
  synthesized matrix; a human owner must confirm it as the closed set before the rule's
  ERRORs carry authority.

## Verdict

Verdict: PASS-WITH-NOTES

Rationale: No CRITICAL or HIGH finding on any axis. Two MEDIUM notes (composition-kind must
never be inferred; the day-one corpus is the worked-example corpus but the rule code stays
generic per shipped precedent) are guard-rails for the BUILD, not spec defects -- both are
already constrained by the spec/data-model/tasks. Two Principle-V items (FR-011, FR-012) are
correctly left OPEN for the human, as required. The draft is ratifiable; the human ratifier
should confirm the closed legality matrix (FR-012) and note the corpus-identity caveat
(FR-011) before build.
