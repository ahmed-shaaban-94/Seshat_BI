# Specification Analysis Report: Portfolio Watch (131)

Non-destructive cross-artifact consistency + quality analysis across `spec.md`,
`plan.md`, `tasks.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
Read-only: no other artifact was modified. This file is the analyze-step deliverable
of the spec-kit chain (the task explicitly names it).

## Summary verdict

No CRITICAL or HIGH issues. One MEDIUM cross-artifact ambiguity plus one MEDIUM
constitution latent-gap (both recorded as implement-time verify notes, not spec
blockers) and two LOW notes. Requirement->task coverage is complete by task CONTENT for
all 25 FR + 4 SEC + 12 SC. Constitution invariants (no-score, no-gate, read-only,
Principle-V relay-only, ratified Option-B CLI) hold across all artifacts. Recommendation:
proceed to ratification (a named-human seam); resolve the MEDIUMs during
`/speckit-implement`.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Consistency (rank scope) | MEDIUM | research.md D4 vs data-model.md prioritized-next-action / summary INV-4 | D4 says classify each scope's "open conditions" (broad -- would include relayed drift blockers); data-model relays the readiness projection's `next_action` (narrow -- readiness blockers only). The scope of "what the shipped `readiness_classify` rank ranks" is not identical across the two docs. | Pin, at implement-time (T012), that the rank orders the READINESS blocker categories (the projection's `next_action` source), and that relayed drift/approval conditions set `requires_human_attention` (FR-006) independently of the rank. Add an assertion. |
| C2 | Constitution latent-gap | MEDIUM (RESOLVED in spec) | data-model dimension->source map + readiness_classify rank | The shipped rank buckets are `approval > grain > live_validation > artifact > readiness` -- there is NO `pii` bucket. A `pii_surface_drift` blocker (the most dangerous Principle-V class) keyword-falls to the catch-all and ranks LOWEST, so a scope with any higher-ranked open condition could bury it. FR-006 as ORIGINALLY worded gated the attention flag on the scope's "highest-ranked open condition" -- which would have let a buried PII blocker escape the flag. | RESOLVED by rewording FR-006 (2026-07-14): the attention flag is now set INDEPENDENTLY of rank for any relayed Principle-V / PII drift blocker, so a PII blocker sets `requires_human_attention` even when a higher-ranked non-PII condition is also open. The rank still orders only the single prioritized next action (FR-005), not this flag. Implement-time verify (T010/T012): keep PII-class relays on the attention flag, not dependent on the rank bucket. Do NOT invent a new rank bucket (that would edit a shipped committed lookup, hard rule #9). |
| L1 | Traceability | LOW | tasks.md vs spec.md | 13 requirement IDs (FR-001/002/007/018/025, SEC-001/003/004, SC-001/002/004/007/011) are covered by task CONTENT but not cited by literal ID in the task text. Each verified to map to >=1 task (coverage table below). | Optional: add the literal FR/SC id in the relevant task descriptions for grep-traceability. Not a coverage hole. |
| L2 | Terminology | LOW | spec.md L9/L55, research.md D7, tasks.md, plan.md | Artifacts use both `seshat watch` (3x) and `retail watch` (5x). | Intentional and consistent: `seshat watch` only QUOTES the source feature title / the rejected verb-family alternative; `retail watch` is the chosen shipped-invocation name. The `retail`->`seshat` console-script rename is a separate in-flight spec (119). No change needed; noted for the reader. |

## Coverage Summary (requirement -> task)

All requirements are covered by at least one task (by content; L1 notes the literal-ID gap).

| Requirement group | Count | Covered | Representative tasks |
|---|---|---|---|
| FR-001..FR-006 (summary) | 6 | 6/6 | T006, T011, T012, T013 (+ tests T008-T010) |
| FR-007..FR-012 (baseline/change) | 6 | 6/6 | T019, T020, T021 (+ tests T015-T018, T022) |
| FR-013..FR-017 (truthful degradation) | 5 | 5/5 | T028, T029 (+ tests T023-T027) |
| FR-018..FR-025 (governance/boundaries) | 8 | 8/8 | T001, T013/T014, T021, T030, T031, T036, T037, T038 |
| SEC-001..SEC-004 | 4 | 4/4 | T007, T019, T029, T032, T037 |
| SC-001..SC-012 | 12 | 12/12 | T007/T008, T009, T016/T022, T023-T027, T014/T037, T038, T010/T037, T029 |

Uncited-but-covered spot checks (each verified to >=1 task): FR-001 -> T013; FR-002 ->
T006; FR-007 -> T019/T021; FR-018 -> T001/T014/T021; FR-025 -> T002/T003; SEC-001 ->
T007/T032; SEC-003 -> T019; SEC-004 -> T010/T030/T037; SC-001 -> T008; SC-002 -> T028;
SC-004 -> T016; SC-007 -> T023-T027; SC-011 -> T029/T038.

## Constitution Alignment (checked)

| Principle / rule | Result | Evidence |
|---|---|---|
| I -- Agent-First, Gate-Enforced (no gate added; agent not pass-authority) | PASS | FR-019/SC-009; Watch reads gate/evidence outputs, asserts no `pass`; `retail check` exit unchanged (T038). |
| V -- Agent Stops at Judgment Calls (no self-grant; relay only) | PASS | FR-021/SC-010; no Principle-V ruling ORIGINATES in Watch; relays with named owner (T010/T030/T037). `open_for_human` empty. |
| VIII -- Static-First, Live Deferred | PASS | SEC-001/FR-013; MVP no-DB, committed readers only; live-only -> `[PENDING LIVE]` (T023, T028). |
| Readiness spine + hard rule #9 (no fake confidence) | PASS | FR-020/SC-003; four statuses + shipped categorical enums + measured magnitudes only; the one next action uses the shipped fixed rank, never a computed priority (T012, T037). See C1/C2 for the rank-scope refinement. |
| Ratified Option-B CLI decision + hard rule #1 | PASS | FR-023/D7; skill-driven + one narrow read-only surface (`retail watch --format json`), no verb family (T030/T031). |
| VII -- Example, Not Schema | PASS | FR-025; generic fixtures, no C086/pharmacy (T002/T003). |

## Unmapped tasks

None. Every task maps to a story (US1-US4) or to setup/foundational/interface/polish, and
each names an exact file path. Task IDs T001-T038 are sequential with no gaps.

## Metrics

- Total requirements: 41 (25 FR + 4 SEC + 12 SC).
- Total tasks: 38 (T001-T038).
- Coverage: 100% of requirements have >=1 task (by content; 13 lack a literal-ID citation -- L1).
- Ambiguity findings: 1 (C1, MEDIUM).
- Constitution latent-gap findings: 1 (C2, MEDIUM, bounded by FR-006).
- Duplication findings: 0.
- CRITICAL issues: 0. HIGH: 0. MEDIUM: 2. LOW: 2.

## Next Actions

- No CRITICAL/HIGH -- the spec is ready for the standing human seam (ratification;
  Principle V). This chain does NOT ratify or implement.
- At `/speckit-implement`: resolve C1 (pin the rank to readiness-blocker categories; keep
  relayed drift/approval on the attention flag) and honor C2 (PII-class relays ride the
  attention flag, not the rank bucket; do not edit the shipped rank). Both are already
  bounded by FR-006 -- they are correctness-confirmations, not redesigns.
- Optional: apply L1 (add literal FR/SC ids to task text) for grep-traceability.
