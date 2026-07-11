# Specification Quality Checklist: Capability Inventory

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-11
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`.

### Validation record (2026-07-11)

Two brief-level assumptions were in tension with committed, human-ratified project
reality; both were resolved by the repo owner during Session 2026-07-11 rather than
guessed, and encoded into the spec (Clarifications + Assumptions):

1. **Surface form.** The brief prescribed a `seshat capabilities` / `retail
   capabilities` CLI verb. `docs/roadmap/decisions/cli-verbs-vs-skill-driven.md`
   (Option B, ratified 2026-07-07) rejected new CLI verbs for discoverability. Owner
   chose the Option-B-compliant surface (skill/composer, no new CLI verb). Encoded in
   FR-001 and the scope wall.

2. **Canonical source of truth.** No single committed file enumerates the full
   capability surface, and `state` / `requirements` / `authority` have no structured
   home today. Owner chose "new manifest owns only the gap fields; reference the rest".
   Encoded in FR-003, FR-004, FR-014, and Key Entities.

**Content-quality note (no implementation detail):** the spec names committed
*artifacts* (the manifest, the feeder sources, the four existing authorities) because
truthfulness/authority is the feature's whole point and each is a reviewable project
fact -- it does NOT pin a file format, path, language, or library, all of which are
deferred to the plan phase. Naming the authority is a requirement; choosing YAML-at-
path-X is not.

**Deferred to `/speckit-plan`** (not spec gaps): the manifest's concrete file
format/path; the exact final field names (FR-004 fixes the categorical field SET, not
the spelling); the precise fixed precedence for FR-008 primary-group placement; the
exact feeder set the staleness oracle reconciles (FR-013 fixes the two-direction
behavior, not the enumeration); the spelled-out `state`/`authority`/`requirements`
enums; and the follow-up reconciliation of the prose predecessors
(`post-idea-bank-capability-state.md`, README table).

**Post-draft hardening (2026-07-11, advisor review):** three fixes applied so the
oracle sits ON the truthfulness risk, not adjacent to it (repo lesson
`verifier-must-sit-on-the-risk`):

1. `state` is NOT wholly unowned. Its shipped-vs-not-shipped axis is partially
   feeder-owned (`docs/roadmap/roadmap.md`, `docs/quality/status-claims.yaml` /
   rule SC1). FR-003 now requires reconciling shipped-ness against those feeders;
   FR-013(c) now FAILS a `state: shipped` whose only evidence is a spec file existing.
   Without this a false "shipped" passed the reference-existence check -- the exact
   failure the feature exists to prevent.
2. Appendix A added: the brief's named hard cases (F016, F034, dbt/Dagster adapters,
   the plugin's locally-verified-vs-released provenance, the four authorities-as-
   capabilities) are mapped to expected state/surface/authority/grouping, so the
   taxonomy is demonstrated, not just defined.
3. FR-004 flags that `readiness_stage`'s seven-stage vocabulary has no canonical
   committed data file (hardcoded tuple in 3 places); the plan MUST pick one so the
   field does not quietly violate FR-003.

**Adversarial skeptic round (2026-07-11):** an independent Opus skeptic (scoped: do
NOT reopen the owner-settled surface/manifest decisions; hunt truthfulness holes +
internal contradictions) found 5 real defects, all verified against committed feeders.
All fixed:

- **BLOCKER** -- FR-013(c) only "disagreed" when a feeder covered the capability, but
  the named feeders (roadmap F-rows + a 5-entry `status-claims.yaml`) cover almost none
  of the skill surface, so a spec-only capability (e.g. spec-044 KPI-lineage) marked
  `shipped` with a spec-dir pointer passed. FR-013(c) is now FAIL-CLOSED: `shipped`
  requires POSITIVE feeder backing; no feeder -> cannot be `shipped`. New US4 scenario 4.
- **MAJOR** -- no clause sat on the false-`publicly-released` risk (provenance is
  manifest-asserted, and the "Claude plugin" is not even in the tracked tree). Added
  FR-013(d), fail-closed on `publicly-released`. New US4 scenario 5.
- **MAJOR** -- Appendix A mis-classified dbt/Dagster as "Deferred" but roadmap marks
  F029/F030 SHIPPED and both skills exist -> the spec's own conformance target failed
  its own oracle. Reclassified as shipped advisory companions (Agent / companion), with
  the shipped-skill vs deferred-connected-executor facets split explicitly.
- **MAJOR** -- FR-005 conflated the lifecycle axis (shipped/spec-only/deferred) with the
  authority axis (advisory/agent-companion/human-gated), colliding with FR-004's
  orthogonal `authority`/`surface` and FR-008's single-group determinism. FR-005 now
  fixes FOUR orthogonal axes and forbids `state` absorbing authority/provenance values.
- **MINOR** -- KPI-lineage "per feeder" resolved to nothing; subsumed by the fail-closed
  fix and made explicit in its Appendix A row.

Skeptic confirmed CLEAN: no score/readiness leak (FR-009/SC-004/scope wall airtight);
all 7 brief scenarios have homes (the "db-configured live-tools" scenario is correctly
served by the STATIC `requirements` grouping, since the surface has no live DB leg by
design -- not a drop).

**Final reconciliation (2026-07-11):** the fail-closed fix initially let "a present
`SKILL.md`" count as shipped evidence, which contradicted FR-002's "no capability from
mere file existence" (skills have no registry -- discovery is filesystem-only, so
"wiring" for a skill would collapse to "a file exists"). Resolved by drawing the line
at DECLARED metadata, not bare presence: FR-002 now admits a committed `SKILL.md` with
`name`+`description` frontmatter as reviewable, human-authored capability metadata
(categorically distinct from an incidental file), and FR-013(c) + the KPI-lineage row
use the same "frontmatter'd SKILL.md, not a bare dir" language. A spec dir's existence
remains NOT shipped evidence. dbt/Dagster are unaffected (F029/F030 in roadmap.md is an
independent feeder).

**Cross-artifact analysis (`/speckit-analyze`, 2026-07-11):** an independent Opus
analyzer mapped every FR/SC to tasks and hunted spec<->plan<->tasks<->contracts<->
constitution inconsistencies. Result: 0 CRITICAL, constitution + both hard-stops CLEAN,
100% requirement coverage. 7 findings, all fixed in this pass:
- I1 (HIGH): US1 Independent Test + Scenario 2 read Available-now/Requires-DB as a
  requirements-BINARY, contradicting the fixed group precedence (requirements ranks 3rd).
  Reworded both to be precedence-aware; T006 test renamed `test_grouping_by_precedence`.
- C1 (MED): FR-011 "reads no readiness-status.yaml" had no test -> added
  `test_reads_no_readiness_state` to T015.
- A1+I2 (MED/LOW): `readiness_stage` source was ambiguous (readiness-model.md, prose,
  two token forms) -> collapsed to the single canonical `templates/readiness-status.yaml`
  snake_case `stages.*` keys across all artifacts; added oracle O8 + T004 reader.
- A2 (MED): SC-008/FR-017 doc content unverified -> added
  `test_readme_names_four_authorities` to T017.
- C2 (LOW): FR-018 genericity untested -> added `test_generic_no_hardcoded_table` to T018.
- C3 (LOW): FR-019 ASCII OUTPUT untested -> added `test_output_ascii` (T006) +
  `test_json_output_ascii` (T009).

**Result:** all checklist items pass; cross-artifact analysis clean after fixes. Spec +
plan + tasks are internally consistent and ready for the ratify seam (human action).
