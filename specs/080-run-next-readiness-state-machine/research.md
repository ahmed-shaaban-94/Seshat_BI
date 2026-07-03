# Phase 0 Research: Run-Next Readiness State Machine

No external research was required -- every fact this feature depends on is
already committed in-repo. This document records what was looked up, where,
and the resulting decision, so a future implementer does not need to
re-derive it.

## R1. Does `readiness-status.yaml` already carry everything this feature needs?

**Question**: Do FR-001..FR-016 require any new field on the readiness-status
schema, or can everything be computed from what `templates/readiness-status.yaml`
(ADR 0004) already defines?

**Findings**: The template already defines: `current_stage`, per-stage
`status` (one of four words), per-stage `evidence[]`, per-stage
`blocking_reasons[]`, `approvals[]` (with `{stage, owner, at}`), and a
top-level `next_action` string. Every requirement in spec.md maps onto one or
more of these existing fields:

| Requirement | Field(s) used |
|-------------|----------------|
| FR-002 (stage-order walk) | `stages.<stage>.status` for all seven, in fixed order |
| FR-004 (blocked -> STOP) | `stages.<stage>.blocking_reasons[]` |
| FR-005 (approval-required stop) | `stages.<stage>.status`, `approvals[]` |
| FR-009 (pass-without-evidence flag) | `stages.<stage>.status`, `stages.<stage>.evidence[]` |
| FR-010 (disagreement flag) | top-level `next_action` vs. the computed value |
| FR-011/FR-012 (missing/malformed file) | file existence, YAML parseability, `stages` key presence |

**Decision**: No schema change. Adding a field would exceed a read-only
consumer's mandate and would need to be proposed to the schema's owner
(the readiness-model doc), not smuggled in by a downstream reader.

## R2. Is the "approval-shape" rule this feature needs already defined somewhere authoritative?

**Question**: FR-005/FR-015 require deciding whether an `approvals[]` entry
"counts." Should this feature define its own shape rule, or cite an existing
one?

**Findings**: `src/retail/rules/readiness_status.py` (RS1) already implements
exactly this check (`_owner_is_valid`, `_OWNER_SHAPE_RE`,
`_AUTHORITY_CLASSES = {analyst, governance, data_owner, metric_owner}`,
`_ROLE_TOKENS` rejecting a bare-role owner). RS1 is wired into `retail check`
as a static consistency gate over committed `readiness-status.yaml` files.

**Decision**: This feature CITES RS1's rule as its normative source rather
than re-deriving or forking a parallel copy. Concretely: an `approvals[]`
entry satisfies a stage's requirement here if and only if it would also
satisfy RS1's `_owner_is_valid` check. This feature does not call RS1's Python
directly (RS1 lives inside the `retail check` gate; this feature is not part
of that gate and must not become one -- Non-Goal NG-004), but its skill doc
must name RS1's file+function as the source of truth for this rule so the two
cannot silently drift apart without a reviewer noticing (see plan.md
Operational Risks).

## R3. What does `retail-orchestrate` already do that overlaps, and exactly where is the line?

**Question**: `retail-orchestrate`'s SKILL.md already contains a "Run-state:
read `mappings/<table>/` FIRST" table that maps observed disk state to a
current phase/action. Is this feature redundant with that table?

**Findings**: Reading `.claude/skills/retail-orchestrate/SKILL.md` in full:
its run-state table is coarser-grained (four rows: no dir / stopped-at-gate /
map-approved-resume-at-silver / migrations-exist-resume-at-validate) and its
purpose is to feed the orchestrator's OWN self-heal execution loop
immediately afterward -- it decides, then the same skill invocation acts.
There is no independently-invocable "just tell me the next action, don't act
on it" mode in orchestrate today.

**Decision**: This feature is the finer-grained (full seven-stage,
approval-aware, evidence-aware), STANDALONE, non-executing version of that
same class of decision. It is designed to be the kind of thing
`retail-orchestrate` COULD delegate to in a future refactor (Assumption A3),
but this slice does not perform that wiring -- doing so would touch
`retail-orchestrate`'s file, which is out of scope (NG-005).

## R4. What does `readiness-viewer` (F026) already surface, and exactly where is the line?

**Question**: `readiness-viewer`'s SKILL.md states plainly: "`next_action` |
already surfaced | also surfaced (SHARED, NOT a delta)." Does that mean this
feature duplicates readiness-viewer?

**Findings**: Reading `.claude/skills/readiness-viewer/SKILL.md`'s "Renders,
never re-derives" table: "the single next action | `readiness-status.yaml`
`next_action`" -- i.e. readiness-viewer copies the STORED STRING verbatim. Its
explicit scope boundary states: "Renders, never re-derives... a per-stage
`status` is shown EXACTLY as `readiness-status.yaml` records it... Core
Authority owns truth." It is designed NOT to compute anything.

**Decision**: This feature is the opposite half of that same coin: it
computes the next action FRESH from stage state and flags any disagreement
with the stored string (FR-010), rather than trusting or rendering the stored
string. The two are complementary, not duplicative, PROVIDED this feature
never silently starts just rendering the stored field as its own answer (that
would collapse the delta to zero and trigger the plan's merge-fallback
discussion).

## R5. Does the constitution/architecture forbid a persisted run-state engine?

**Question**: Could "state machine" in this feature's name be read as license
to build a stateful service (a daemon, a cache, a counter)?

**Findings**: Three independent sources say no:
- Constitution "Readiness System" section: "Recompute `current_stage` from
  committed artifacts... there is no separate run-state engine" (also echoed
  in `AGENTS.md`).
- `retail-orchestrate` SKILL.md: "there is no daemon, no scheduler, no
  persisted counter, and no fix-applying subagent... That is the parked
  orchestration runtime (architecture open decision #3)."
- `src/retail/compass_project.py` docstring: "Stores NO run-state /
  current_stage (FR-005)."

**Decision**: "State machine" here means the CONCEPTUAL ordering/transition
model only (Assumption A6). Every invocation of this feature recomputes fresh
from the committed file; no new persisted state of any kind is introduced.

## R6. Where should a future optional Python helper live, if one is ever built?

**Question**: If the stage-order walk logic becomes complex enough to warrant
code rather than pure agent-procedure text, where does it go?

**Findings**: `readiness-viewer`'s own plan.md enumerates exactly this
situation for itself and answers it: `src/retail/tools/readiness_viewer.py`
(NOT `src/retail/rules/`), "OPTIONAL, DEFERRED... a future read-only CLI
renderer, still no new validator." The `rules/` package is reserved for
`@register`-decorated `retail check` gate rules (confirmed by reading
`src/retail/registry.py`'s `register` decorator usage across `rules/*.py`).

**Decision**: Mirror that precedent exactly: an optional future helper for
this feature, if built, belongs under `src/retail/tools/`, is stdlib-only, and
registers no rule ID. Enumerated as PLANNED + DEFERRED in plan.md; not
designed in Python detail in this spec-only slice.
