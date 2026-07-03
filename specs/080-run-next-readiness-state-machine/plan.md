# Implementation Plan: Run-Next Readiness State Machine

**Branch**: `080-run-next-readiness-state-machine` | **Date**: 2026-07-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/080-run-next-readiness-state-machine/spec.md`

## Summary

Build a **read-only, stateless "next allowed action" oracle** for one table's
readiness status. Given a single `mappings/<table>/readiness-status.yaml`
(ADR 0004 canonical location), it walks the seven-stage spine in fixed order,
finds the earliest non-`pass` stage, and returns exactly one of: a forward next
action, a STOP citing `blocking_reasons[]` verbatim, or a "named-human approval
required" flag -- plus attached caveats (evidence-gap, `next_action`
disagreement, invalid-status defect). It never executes anything, never writes
anything, never grants an approval, and never emits a numeric score. It is the
extracted, standalone READ half of the decision `retail-orchestrate` already
makes inline before it executes a phase; it is a fresh COMPUTATION (not a
verbatim render) unlike `readiness-viewer`/F012; and it applies (but does not
re-implement) RS1's approval-shape rule. This slice is **docs/templates/skill
only** (constitution Principle VIII, roadmap rule #8): no Python module, no new
`retail check` rule ID, no CLI, no DB read, no dependency added.

## Technical Context

**Language/Version**: None this slice -- docs/planning + agent-procedure text
(Markdown). The agent is the runtime, exactly as `retail-orchestrate` and
`readiness-viewer` are: a skill the agent follows, not a service that runs.

**Primary Dependencies**: None at runtime. Consumes the existing
`templates/readiness-status.yaml` schema (ADR 0004) and the existing
`docs/readiness/<stage>-ready.md` "Next allowed action" / "Required owner /
approval" fields as its reference vocabulary. Applies the same named-human
approval-shape rule RS1 (`src/retail/rules/readiness_status.py`) already
encodes, without importing or calling RS1's code (RS1 runs inside `retail
check`; this feature is not part of that gate).

**Storage**: Committed text in the repo only. Reads (never writes)
`mappings/<table>/readiness-status.yaml` and the relevant
`docs/readiness/<stage>-ready.md` files. Produces no new committed artifact
type -- its output is an ephemeral response to the caller (agent/human), not a
file this feature persists.

**Testing**: No code this slice, so no automated unit-test suite is produced by
the SPEC/PLAN work itself; the plan DOES design the fixture-based test matrix a
future implementation slice must satisfy (see `quickstart.md` and
`contracts/run-next-response.md`). Verification of THIS slice (spec/plan/tasks
only) is: `retail check` exit 0 with zero new rule IDs; every new file is valid
Markdown/YAML; ASCII-only, UTF-8 no BOM; ruff/black not applicable (no `.py`
touched).

**Target Platform**: Repo text artifacts consumed by an agent, reviewed by a
human. Repo-only mode always; no live-DB mode exists for this feature (FR-016)
-- there is nothing here for a live mode to add, since the input is entirely
committed text.

**Project Type**: Product Module (read-only) -- a skill + a short contract doc;
no `src/` change, no new template file needed beyond referencing the existing
`templates/readiness-status.yaml`.

**Performance Goals**: N/A (single-file read, single-table scope, no loops over
a corpus).

**Constraints**: ASCII + UTF-8 no BOM; generic (no C086/retail_store_sales
specifics); ships no numeric confidence/health/percent-ready score; introduces
no persisted run-state (no daemon, no cache, no counter file); adds no new
`retail check` rule ID; changes no existing skill's behavior
(`retail-orchestrate`, `readiness-viewer`, RS1) as part of this slice.

**Scale/Scope**: 1 skill (agent-facing procedure) + 1 short contract/response-shape
doc + fixture-based test-design docs. No CLI, no library module, in this slice.

## Constitution Check

*GATE: must pass before Phase 0 research and be re-checked after Phase 1 design.
Constitution at `.specify/memory/constitution.md`.*

| Principle | How this feature complies |
|-----------|---------------------------|
| I. Agent-First, Gate-Enforced | The surface is agent-procedure text; the agent is the runtime. It adds no gate and claims no pass/fail authority of its own -- `retail check` / `retail validate` remain the only gates. It only reads what those gates (and human review) have already recorded. |
| II. Depend, Never Fork | No engine, no Power BI execution adapter involved. Nothing to fork; it is a pure local read-and-decide skill layered on existing artifacts. |
| III. Medallion, Gold-Only | Not triggered -- no SQL, no DB connection, no Power BI read. |
| IV. Source Mapping Before Silver | Reinforced, not violated: the surface's own stage-order walk (FR-002) is exactly "no forward action past mapping_ready until it is pass," which is this principle expressed as a read-only check rather than a gate. |
| V. Agent Stops at Judgment Calls | This is the feature's central property. FR-005/FR-015 and Non-Goal NG-002 make "stop and report, never grant" the surface's defining behavior at every one of the five named-human seams (Mapping, Semantic Model, Dashboard, Publish, file-source Source Ready). |
| VI. Defaults Then Deviations | The surface reports the recorded state as-is; a stage recorded `pass` without evidence is flagged (FR-009), never silently accepted or silently rejected -- the deviation is surfaced, not smoothed. |
| VII. C086 Is An Example | The skill and its examples are generic. Any worked-example table name used in illustration is cited as a filled instance, never baked into the logic. |
| VIII. Static-First, Live Deferred | No Python, no rule, no CLI, no DB read this slice. `retail check` stays at its current rule count; this slice adds zero rule IDs (rule #8 compliance, matching readiness-viewer's precedent). |
| IX. Secrets & Reproducibility | No secrets, no DSNs. ASCII + UTF-8 no BOM. No numeric score anywhere (rule #9). |

**Result**: PASS. No violations; Complexity Tracking left empty.

### Boundary gate (feature-specific, load-bearing)

The single biggest design risk is silent duplication of three existing
surfaces. The plan holds three explicit boundaries, matching the advisor-grade
overlap analysis performed during specification:

1. **vs. `retail-orchestrate`**: orchestrate already contains an inline
   "observe disk state -> current phase/action" table (`.claude/skills/retail-orchestrate/SKILL.md`,
   "Run-state" section) that it uses internally, then EXECUTES the resulting
   phase via the self-heal loop. This feature extracts the READ-ONLY decision
   half into a standalone, independently invocable surface. It does not change
   orchestrate's execution/self-heal behavior (NG-005); a future wiring change
   (orchestrate calling this surface instead of recomputing inline) is
   explicitly out of scope here.
2. **vs. `readiness-viewer` (F026) / `retail-control-room` (F012)**: both
   already surface a `next_action` value, but they RENDER the file's stored
   string VERBATIM across many tables (a rendering lens). This feature
   COMPUTES a fresh next action from the seven stage statuses for ONE table,
   and when the computed value disagrees with the stored string, reports BOTH
   and flags the disagreement (FR-010) rather than picking one. Cross-table
   aggregation remains F012/F026 territory (NG-003).
3. **vs. RS1** (`src/retail/rules/readiness_status.py`): RS1 is the static
   consistency LINTER wired into `retail check` (invalid status values, `pass`
   without evidence, `blocked` without reasons, invalid approval-owner shape,
   `current_stage` skipping a blocker). This feature applies the SAME
   approval-owner shape rule (so its notion of "approved" agrees with the
   gate's) but does not call RS1's code, does not add a rule ID, and does not
   assume its input has already passed RS1 -- it degrades gracefully (reports
   the defect) on RS1-dirty input rather than requiring RS1-clean input first
   (NG-004).

If any of these three deltas collapses under implementation scrutiny (e.g. the
"fresh computation" turns out to always agree trivially with the stored
`next_action` and never needs FR-010's disagreement path), the documented
fallback is: fold the computation into `retail-orchestrate`'s existing table as
a named, independently-callable sub-step rather than shipping a fourth
overlapping surface. This mirrors `readiness-viewer`'s own explicit
merge-fallback discipline.

## Project Structure

### Documentation (this feature)

```text
specs/080-run-next-readiness-state-machine/
|-- spec.md                        # feature specification (done)
|-- plan.md                        # this file
|-- research.md                    # Phase 0 output
|-- data-model.md                  # Phase 1 output
|-- quickstart.md                  # Phase 1 output
|-- contracts/
|   `-- run-next-response.md       # Phase 1 output -- the response-shape contract
|-- checklists/
|   `-- requirements.md            # spec-quality checklist (done)
|-- analysis/
|   `-- analyze-report.md          # Step 4 cross-artifact analysis
`-- tasks.md                       # Phase 2 output (a later step in this chain)
```

### Repository artifacts this feature PLANS (not created this slice)

These are FUTURE outputs the spec enumerates for a later implementation slice.
This planning slice writes ONLY the spec-kit documentation files above.

```text
.claude/skills/run-next-readiness/SKILL.md   # PLANNED -- the read-only "next allowed
                                              #   action" verb (agent-facing procedure)
docs/tools/run-next-readiness.md             # PLANNED -- usage + boundary doc (parallel
                                              #   to docs/tools/readiness-viewer.md if that
                                              #   exists, or docs/readiness/ siblings)
tests/fixtures/readiness/run_next/*.yaml      # PLANNED -- the fixture readiness-status.yaml
                                              #   files exercising the 15 quickstart.md cases
                                              #   (the implementation slice must first confirm,
                                              #   per tasks.md T007, whether an existing
                                              #   tests/fixtures/ readiness convention should
                                              #   be reused instead of this new subdir)
tests/unit/test_run_next_fixtures.md          # PLANNED, OPTIONAL -- if a future slice adds
                                              #   a thin Python helper (see below), a fixture
                                              #   -based unit-test plan lives here first
```

**No new `src/retail/` module is planned by default.** The spec and this plan
describe an agent-followed procedure (like `readiness-viewer` and
`retail-orchestrate`), not a library function. IF a future slice decides the
computation is complex enough to warrant a small pure-Python helper (e.g. to
guarantee the stage-order walk and approval-shape check are applied
identically everywhere this surface is invoked), that helper would be:

- **Location or a `src/retail/tools/` (NOT `src/retail/rules/`)** -- exactly
  the same distinction `readiness-viewer`'s plan draws for its own optional
  future CLI (`src/retail/tools/readiness_viewer.py`, planned + deferred). The
  `rules/` package is reserved for `@register`-decorated `retail check` gate
  rules; this feature is explicitly NOT a gate (Non-Goal NG-004) and MUST NOT
  register a rule ID.
- **stdlib-only and read-only**, taking a parsed readiness-status mapping and
  returning a plain-data response (see `contracts/run-next-response.md`) --
  never a DB connection, never a side effect.
- Enumerated as PLANNED + DEFERRED here; not designed in Python detail in this
  spec-only slice.

**Structure Decision**: Product Module (read-only) -- no `src/` change this
slice. The feature's home is a skill (agent procedure), mirroring
`readiness-viewer` and `retail-orchestrate`'s own delivery shape (Assumption
A7). An optional future pure-Python helper is enumerated and deferred under
`src/retail/tools/`, never `src/retail/rules/`.

## Phase 0 -- Research

See `research.md` for the full write-up. Two questions were resolved without
external research (everything needed is already in-repo):

1. **Does this feature need any new schema field on `readiness-status.yaml`?**
   No. FR-001..FR-016 are all computable from the fields the template already
   defines (`current_stage`, `stages.<stage>.{status,evidence,blocking_reasons}`,
   `approvals[]`, `next_action`). Adding a field would be schema scope creep
   outside a read-only consumer's mandate.
2. **Does the approval-shape check need to be re-derived, or can it be stated
   as "the same rule RS1 already enforces"?** Restated as a citation, not
   re-derived independently -- both must agree, or the surface's notion of
   "approved" would diverge from the gate's, which is a defect class this
   feature specifically exists to avoid introducing.

## Phase 1 -- Design

See `data-model.md` (the entities and their fields/relationships),
`quickstart.md` (how a caller invokes this surface and what fixture types
prove it works), and `contracts/run-next-response.md` (the exact shape of the
response this surface returns, and the exact read-only guarantee it provides).

**`.claude/skills/run-next-readiness/SKILL.md`** (planned shape, for a later
implementation slice): frontmatter naming triggers ("what's the next allowed
action for this table", "is this table blocked", "can I proceed to silver
yet"); a scope-boundary section (read-only; computes no truth; grants no
approval; no fake confidence; generic; ASCII no BOM); a "Relationship to
retail-orchestrate / readiness-viewer / RS1" section (the three boundary-gate
deltas above, verbatim); the stage-order walk procedure (FR-002..FR-005); the
honest-state rules (FR-009..FR-012, mirroring readiness-viewer's table shape);
the read-only proof (`git status` clean after a run); See also.

## Phase 1 -- Constitution re-check

Re-checked after design: still PASS. The design adds only a generic skill (a
later slice) + a documentation contract this slice, reads no DB, adds no rule,
computes no persisted status, infers no approval, and emits no score. Boundary
gate holds (three named deltas against the three nearest neighbors, with an
explicit merge-fallback).

## Complexity Tracking

> No Constitution Check violations. Section intentionally empty.

## Operational Risks

- **Risk: drift between this surface's approval-shape logic and RS1's.** If a
  future change to RS1's `_owner_is_valid` shape rule is not mirrored here, the
  two surfaces would disagree on whether a stage is "really" approved. Mitigation:
  the skill doc must cite RS1's exact rule by file+function name as its
  normative source (not restate a parallel copy that can drift silently), and a
  future implementation slice's test fixtures should assert agreement against
  RS1's own test fixtures where they overlap.
- **Risk: silent scope creep into execution.** Because this surface sits right
  next to `retail-orchestrate` (which DOES execute), there is a natural pull to
  "just also run the next step for convenience." Mitigation: FR-008/NG-001 are
  explicit and load-bearing; the skill doc's "What this must NOT do" section
  (mirroring `readiness-viewer`'s Forbidden-operations list) is non-negotiable
  in any implementation.
- **Risk: `next_action` disagreement noise.** If the stored `next_action`
  string is very frequently stale (e.g. because nothing currently updates it
  reliably), FR-010's disagreement flag could fire on nearly every invocation,
  becoming noise rather than signal. Mitigation: the implementation slice
  should sample real/fixture `readiness-status.yaml` files to gauge how often
  this fires before finalizing wording; if it is nearly always noisy, the skill
  doc should say so plainly rather than pretend the flag is rare.
- **Risk: fourth-surface fatigue.** Adding a fourth reader of
  `readiness-status.yaml` (after RS1, readiness-viewer, retail-control-room)
  raises the "why does this repo have four things reading the same file"
  question at review time. Mitigation: the boundary-gate section above and the
  analysis step (Step 4) must answer this head-on, including the documented
  merge-fallback, rather than leaving it implicit.

## Backwards-Compatibility Concerns

- **None for existing artifacts.** This feature reads
  `readiness-status.yaml` and `docs/readiness/<stage>-ready.md` without
  requiring any schema change; every existing filled instance remains readable
  as-is.
- **RS1 compatibility.** If RS1's approval-shape rule changes in the future,
  this feature's cited logic must be updated in lockstep (see Operational
  Risks); until then, no backward-incompatibility exists because this feature
  does not fork the rule, it cites it.
- **No API/CLI surface exists yet to break.** Because this slice ships no code,
  there is no compatibility contract yet to preserve; the contract this plan
  DOES fix (`contracts/run-next-response.md`) is the one a future
  implementation must not casually change once callers (e.g. a future
  `retail-orchestrate` wiring) depend on it.

## Repo-only vs. live-DB mode

This feature has **no live-DB mode**. Every input (`readiness-status.yaml`,
the stage docs) is committed text; `evidence[]` entries may CITE the result of
a live `retail validate` run (e.g. "retail validate exit 0, 2026-07-01"), but
this feature reads that citation as text -- it never opens a database
connection itself, never re-runs `retail validate`, and never needs the `db`
extra. FR-016 makes this explicit. There is therefore no "graceful degradation
when the DSN is absent" behavior to design, unlike `retail-onboard-table` or
`retail-validate` -- this surface is always in repo-only mode.

## Test & Validation Commands (for a future implementation slice)

- `retail check` -- MUST exit 0 with the SAME rule count as before this
  feature ships (zero new rule IDs added).
- A fixture-based test file (location TBD by the implementation slice, e.g.
  `tests/unit/test_run_next_readiness.py` if a Python helper is built, or a
  manual fixture walkthrough documented in `quickstart.md` if the surface
  stays pure agent-procedure) covering: unblocked-stage, blocked-stage,
  approval-pending (valid and shape-invalid owner), fully-passed chain,
  missing file, malformed file, `current_stage` disagreement, `warning`
  status, dual-blocked stages, and the file-source approval sub-case -- the
  full edge-case list from spec.md.
- `git status --short` after any manual/automated run -- MUST show zero
  changes (the read-only proof, SC-003).
- A manual textual scan of the skill doc / any Python helper for a numeric
  score pattern (`%`, `score:`, `confidence`) -- MUST find none outside a
  comment citing why it is deliberately absent (SC-004).

## Forbidden Scope (restated for the implementation slice)

- No `src/retail/rules/*.py` addition (no new `retail check` rule ID).
- No CI workflow change.
- No new dependency in `pyproject.toml` / lockfile.
- No change to `retail-orchestrate`, `readiness-viewer`, or RS1's existing
  behavior.
- No schema change to `templates/readiness-status.yaml`.
- No live DB code path.
- No numeric score, ever.
