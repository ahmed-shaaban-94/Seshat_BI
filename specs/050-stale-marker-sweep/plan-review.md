# Adversarial Plan-Review: Stale-Marker Sweep / Status-Claim Reconciler (SC1)

**Reviewer posture**: single default-adverse skeptic. READ-ONLY (findings only, no
edits). Five axes: hidden-principle-violation, assumes-deferred-capability,
c086-leak, fabricated-confidence, over-scope. Stage 6, 2026-06-30.

**Inputs reviewed**: spec.md, plan.md, tasks.md, research.md, data-model.md,
contracts/sc1-rule-contract.md, quickstart.md, analysis.md. All present (a draft
missing analyze or tasks would be automatic BLOCKED -- not the case here).

## Axis 1 -- Hidden principle violation

- **Probed**: Does SC1 quietly do more than a static read? Does the anchor step
  reintroduce a banned behavior? Does any finding leak a graded/numeric value?
- **Result**: No violation. SC1 is a pure (context -> findings) read of committed
  text + tracked-files set; lazy `import yaml` is the only dependency and it is
  in-handler (Principle VIII + never-execute; B1 would itself flag a module-scope
  DB/network import). Findings are categorical ERROR statements (Hard rule 9 held:
  data-model invariant 3 + FR-012 + SC-004 forbid any number). Principle V carve-out
  is honestly EMPTY -- SC1 genuinely raises no grain/PII/rollup/identity question, so
  declaring "none" is correct, not an evasion.
- **Finding R1 (LOW)**: The anchor check is the one place SC1 exceeds A1 (A1 only
  resolves a path; SC1 also substring-scans a doc). Research D2 deliberately narrows
  this to a literal substring PRESENCE test (no word-scan, no regex, no position) to
  avoid the false-positive trap the value reviewer flagged. This is sound and
  in-scope, but the implementer MUST NOT drift it toward "detect a status word in
  prose" -- that would be the hidden over-reach. Fix: keep T011's anchor branch a
  literal `anchor in text`; the contract already pins this. No action needed if
  followed.

## Axis 2 -- Assumes a deferred capability

- **Probed**: Does any artifact lean on F016 (Power BI execution adapter), F031-F033
  (spec-only runtimes), live DB, or ingestion?
- **Result**: No. Spec Out of Scope and plan Technical Context both explicitly
  exclude live DB / ingestion / F016 / F031-F033. SC1 runs on the repo checkout
  alone (tracked files + committed text). The live guard (T017) shells `git ls-files`
  only -- the same dependency A1's live guard already uses. No deferred capability is
  assumed. PASS.

## Axis 3 -- C086 / worked-example leak

- **Probed**: Does the rule, the seed manifest entry, the tests, or any message
  hardcode a pharmacy/C086 doc path, table, code, segment, or PII value?
- **Result**: No leak. The only `c086`/`pharmacy` tokens in the artifacts are the
  explicit "do NOT hardcode" guards (contract line 63, data-model line 51, plan
  Constitution Check, FR-016). The seed entry (T015) references
  `docs/quality/post-idea-bank-capability-state.md` and
  `docs/demo/net-sales-end-to-end-readiness-trace.md` -- generic repo-governance/demo
  infrastructure paths, NOT a worked-example value. Test fixtures are mandated
  synthetic (T003: `docs/x.md`, `src/x.py`). T020 is a final leak sweep. PASS.
- **Finding R2 (LOW / advisory)**: The net-sales trace doc is a *demo* artifact that
  happens to cite a real measure name internally; SC1 only references its PATH (a
  readiness claim about whether the file exists), never its content beyond the
  anchor in the *capability-state* doc. This stays generic. The implementer should
  ensure the chosen `anchor` (T016) is the structural "(planned)"-claim sentence, not
  any pharmacy-specific phrase. Low risk; flagged for the leak sweep.

## Axis 4 -- Fabricated confidence

- **Probed**: Does any artifact assert a readiness/quality score, a "verified"
  claim not backed by evidence, or a self-granted pass?
- **Result**: No fabrication. Status front-matter is "Draft" (FORBIDDEN to write
  Ratified -- confirmed Draft). SC1 emits zero numeric confidence (the rule's whole
  point is categorical reconciliation; SC-004 verifies). The seed defect is verified
  against the live repo (S1 in analysis: trace tracked + shipped per roadmap stage 2
  / PR #72; capability-state line 118 literally says "planned"). The 35->36 baseline
  is ground-truth (live wiring test holds 35), and the artifacts explicitly DISTRUST
  and correct the idea-bank's stale "33/34" assumption rather than parroting it.
  PASS.

## Axis 5 -- Over-scope

- **Probed**: Does the plan build past the first-step seam (YAGNI)? Does it pull in
  the delegated rule-count facet or a coverage rule?
- **Result**: No over-scope. The rule-count facet (T5.5) is explicitly OUT (spec Out
  of Scope; research D5); the completeness/coverage check is explicitly OUT and the
  drift gap is ACCEPTED (Q2; research D6 mirrors A1-before-A3). Scope is one rule
  module + one manifest + one test file + the wiring edit + a one-line prose fix + a
  roadmap row. That is the seam, not an implementation beyond it. PASS.
- **Finding R3 (LOW)**: Coupling between T015 (seed entry's `anchor`) and T016 (the
  prose correction) -- the anchor must be byte-identical to whatever corrected
  sentence T016 writes, or SC1's own anchor check fails on the seed. Tasks already
  call this out (T016: "set the T015 anchor to that exact text"). Recommend the
  implementer author T016's wording FIRST, then copy it verbatim into the T015
  anchor, and let the live guard (T017) prove they match. Not a blocker; ordering is
  already specified.

## Severity roll-up

- Critical: 0
- High: 0
- Medium: 0
- Low: 3 (R1 anchor-scope discipline, R2 anchor-must-stay-generic, R3 T015/T016
  anchor coupling) -- all are implementer-discipline reminders already pinned by the
  contract/tasks, none requires a spec/plan/tasks edit.

## Verdict: PASS-WITH-NOTES

The spec/plan/tasks are internally consistent, constitution-aligned, grounded in a
verified seed defect, correctly scoped to the A1-lift seam, and ship-green by
design. The three LOW notes are discipline reminders for the implement stage, not
defects in the planning artifacts. Ready for the human ratify gate.

No CRITICAL findings; no uncertainty requiring escalation. (Per protocol: no retry,
no override -- this is a clean PASS-WITH-NOTES.)
