# Contract: Staleness / Truthfulness Oracle (`tests/unit/test_capability_inventory.py`)

An independent pytest oracle -- NOT a `retail check` rule. It sits ON the truthfulness risk
(a false "shipped" / "publicly-released"), reading ground truth from the FEEDER sources
independently of the builder's rendering code (no circularity). Fail-closed. Each failure
mode is exercised by a synthetic fixture manifest, so no real DB/network is needed.

## What MUST FAIL (each a distinct test)

| # | Condition | Direction | FR |
|---|-----------|-----------|----|
| O1 | A `references` target does not exist in its feeder (rule id absent from `rules-manifest.json`; skill name with no frontmatter'd `SKILL.md`; verb absent from `kit-source.yaml`; `command` not a `_DISPATCH` key). | orphan | FR-013(a) |
| O2 | A real wired representation of a covered kind (a `_DISPATCH` command; a frontmatter'd `SKILL.md`; a `kit-source.yaml` verb) is NOT REFERENCED BY ANY manifest entry. Completeness is REFERENCE-COVERAGE, not entry-per-representation: one capability with several wired representations (e.g. `retail validate` exists as the `validate` command, the `retail-validate` SKILL.md, AND a kit-source verb) is ONE manifest entry whose `references` cover all three; O2 fails only when some wired representation is covered by NO entry's `references`. It MUST NOT demand a separate entry per representation (that would defeat the inventory). | unlisted | FR-013(b) |
| O3 | `state: shipped` with NO `references` entry resolving to a positive ship signal (roadmap F-row SHIPPED; `status-claims` `built`; a wired command; a frontmatter'd `SKILL.md`). A spec-dir/file existing is explicitly NOT a signal. | false-shipped (fail-closed) | FR-013(c) |
| O4 | `provenance: publicly-released` with no committed release-evidence reference. | false-released (fail-closed) | FR-013(d) |
| O5 | The manifest echoes a feeder-owned fact (e.g. a rule title) that DISAGREES with the feeder. | contradiction | FR-014 |
| O6 | `state` holds an authority/provenance token, or any field holds a numeric maturity/confidence/completeness/health value. | axis/score violation | FR-005 / FR-009 |
| O7 | The machine form is NOT byte-identical across two renders over unchanged inputs, OR a record has an undeclared/missing field. | determinism/schema | FR-007 / SC-003 |
| O8 | A `readiness_stage` value is neither `not-stage-scoped` nor a snake_case `stages.*` key of the canonical `templates/readiness-status.yaml`. | invalid-stage | FR-004 |

## What MUST PASS

- A well-formed manifest over the real committed feeders (the shipped manifest itself)
  renders cleanly and reconciles: every `shipped` entry has a positive feeder signal;
  every `publicly-released` has release evidence; no orphan; no unlisted covered
  capability; byte-identical machine form.

## Independence (no circularity)

The oracle reads `rules-manifest.json`, `kit-source.yaml`, `roadmap.md`,
`status-claims.yaml`, `_DISPATCH`, and the `SKILL.md` frontmatter DIRECTLY -- it does not
call the builder to learn ground truth. It compares the MANIFEST's claims against those
feeders. (Repo lesson `verifier-must-sit-on-the-risk`: the oracle must not read its ground
truth from the code under test.)

## Not a gate

Failing this test fails CI (fail-closed), but it is NOT a `retail check` rule: no
registered rule, no non-zero `retail check` exit, no `blocking_reasons[]` entry. A CI test
failing is not a governance gate (plan.md Principle-I row).
