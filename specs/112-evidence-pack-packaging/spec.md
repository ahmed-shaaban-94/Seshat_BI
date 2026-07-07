# Feature Specification: Evidence-pack packaging (roadmap M9, under Option B)

**Feature Branch**: `112-evidence-pack-packaging`

**Created**: 2026-07-07

**Status**: **BUILT** (docs-only) 2026-07-07 on branch `feat/112-evidence-pack-packaging`.
Under Option B: a walkthrough over the shipped `evidence-pack-generator` +
`approval-evidence-pack` skills — NO new CLI verb, NO new capability. Deliverable:
`docs/user/evidence-pack.md`.

**Input**: Roadmap M9 "Evidence Pack as Product Output".

---

## Context (Option B framing)

Evidence-pack generation already ships as skills: `evidence-pack-generator` (F028) and
`approval-evidence-pack` (F035, spec 063). The roadmap draft's own §2 half-admits this.
Under B, M9 is NOT `seshat evidence build/export` as verbs — it is making the evidence-pack
skills discoverable as a product output in an installed workspace (the M3 `evidence/` dir
is their landing home).

## Requirements (FR)

- **FR-001** A user-facing guide (`docs/user/evidence-pack.md`): how a user produces an
  evidence pack via the `evidence-pack-generator` / `approval-evidence-pack` skills, and
  where it lands (M3 `evidence/`).
- **FR-002** The M3 workspace `evidence/` layout matches what the skills write.
- **FR-003** No new logic/verb; packaging + docs over shipped skills (B). Evidence packs
  package evidence for a human sign-off — they never grant approval (Principle V,
  verify-slot-only, as the shipped skills already enforce).
- **FR-004** No fabricated score; categorical status + named blockers only.

## Out of scope
- `seshat evidence build/export` CLI verbs (B keeps skill-driven).
- Any approval-granting behavior.

## Held-decision notes
Spec only. Depends on M3. No `tasks.md`/code until owner review.
