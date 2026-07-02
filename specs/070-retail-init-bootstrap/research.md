# Phase 0 Research: `retail init` Bootstrap-to-First-Result

Resolves the open items from the plan's Technical Context. Each entry is
Decision / Rationale / Alternatives considered.

## R1. Canonical kit source: location + format

**Decision**: The canonical source is a single committed YAML file at
`.seshat/kit-source.yaml` in this repo, holding the verb list, the hard-stops, and
the integration list. `compass.yaml`, the fenced `AGENTS.md` / `CLAUDE.md` regions,
and the per-harness integration manifests are all PROJECTIONS generated from it. In
this repo the projections are committed too (dogfooding); a later drift linter
(Phase-2 backstage, spec'd separately) verifies projection == source.

**Rationale**: One source of truth is the load-bearing anti-fork requirement
(FR-015). YAML matches the existing declarative config convention
(`profiles.example.yml`, the metric-contract YAML). Keeping it under `.seshat/`
co-locates the source with its projections. The projection module MAY import
`pyyaml` LAZILY to parse the source and run the drift check, mirroring how `retail
semantic-check` / `value-check` — NOT the static `retail check` core — own YAML
parsing. (Correction to the plan's earlier "stdlib-only" phrasing: parsing YAML
needs a parser; only the `retail check` core stays stdlib-only, and this feature
adds no rule to it — MAJOR-4 from the adversarial review.)

**Verb-set delta (MINOR-7)**: `distribution-ideas.md`'s sketch listed 5 verbs and
omitted `first-hour-compass` / `retail-onboard-table`. The canonical source + compass
add BOTH, because they are the actual first-arrival and profiling front doors an
agent must discover (see R4/R5). This is a deliberate, recorded delta from the
sketch, not undocumented drift. Note also that the source→`compass.yaml` YAML pair is
a near-verbatim copy; the source/projection split earns its keep primarily via the
PROSE projections (`AGENTS.md`/`CLAUDE.md`), which have a genuinely different shape.

**Alternatives considered**:
- *Derive the compass directly from `COMPASS.md` prose* — rejected: prose is not a
  reliable machine source; `distribution-ideas.md` explicitly notes "speckit's router
  is its skills, not its manifest" and the novelty here is a machine-readable router.
- *Make `compass.yaml` itself the source (no separate canonical file)* — rejected:
  then the `AGENTS.md`/`CLAUDE.md` projections would have two possible parents and
  drift detection loses its single reference. The doc's diagram is explicit: one
  canonical source → many projections.
- *Store the source in `pyproject.toml`* — rejected: couples kit routing to the
  Python packaging file and complicates the stdlib-only static path.

## R2. The fence pattern for `AGENTS.md` / `CLAUDE.md`

**Decision**: Reuse the proven speckit fence. Generated content goes ONLY between
`<!-- SESHAT-KIT START -->` and `<!-- SESHAT-KIT END -->`. If the markers are absent,
`init` inserts a fresh fenced block at a safe append location (end of file, or a
declared anchor) and touches nothing else. If it cannot place the fence safely
(e.g. a malformed hand-edit), it reports and STOPS.

**Rationale**: `CLAUDE.md` already ships a working `<!-- SPECKIT START -->…END -->`
fence (constitution-safe, proven in production). Copying the exact mechanism means
no new fence design and inherits the amendment-safety property (FR-006/FR-007,
SC-002). Distinct marker name (`SESHAT-KIT`) so the two fences never collide.

**Alternatives considered**:
- *Regenerate the whole file* — rejected outright: clobbers constitution-owned law
  and routes changes around the amendment procedure (constitution.md:512–522).
- *A separate generated file instead of a fence* — rejected: the whole point is that
  a harness reading `AGENTS.md` / `CLAUDE.md` by convention sees the orientation
  inline; a sidecar file the harness doesn't read defeats Codex parity.

## R3. `compass.yaml` stores no run-state — how state is referenced

**Decision**: `compass.yaml` carries an `orient:` block that DECLARES the protocol
(`question_first`, `state_lives_in: readiness-status.yaml (per table)`,
`recompute_from: [committed artifacts, "Gate status", migration presence]`) and a
`verbs:` + `hard_stops:` + `integrations:` block. It has NO `current_stage` and no
per-table data. State is recomputed per table from `readiness-status.yaml` by the
verbs, exactly as `retail-orchestrate` already does.

**Rationale**: AGENTS.md is explicit — "there is no separate run-state engine"; a
repo has many tables at different stages, so a singleton repo-level stage is
incoherent and forbidden (FR-005, SC-004). This mirrors `retail-orchestrate`'s
"compute the current phase from what is already on disk — there is NO orchestration
state file".

**Alternatives considered**:
- *Cache the current stage in `compass.yaml` for speed* — rejected: forks the source
  of truth (`readiness-status.yaml`) and goes stale; the doc names this the
  "forbidden run-state engine".

## R4. First-arrival worked-example offer — delegate vs reimplement

**Decision**: DELEGATE to the existing `first-hour-compass` skill. The agent routes
into it for the offer + pick, then continues to `retail-onboard-table` for the
profile. `init` contains no copy of the offer table, the pick logic, OR the seam
list (`first-hour-compass` is the single source for all three).

**Rationale**: `first-hour-compass` already presents the two committed worked
examples, treats them as narrative patterns (not templates), routes to
`retail-onboard-table`, and states the human seams — verbatim what `init` would
need. Reimplementing any of it forks one behavior into two sources, which the repo's
anti-fork discipline forbids (SC-008). NOTE (MAJOR-3): the seam LIST is also a
single-source item — `first-hour-compass` says "grain/uniqueness, PII
publish-safety, business rollup/segment, product identity"; `init` must surface THAT
wording, not a divergent "metric policy" variant. `init`'s unique surface is the
INSTALL-TIME bootstrap + substrate projection, which has no existing home.

**Alternatives considered**:
- *Reimplement the offer inside `init`* — rejected: direct anti-fork violation.
- *Fold `first-hour-compass` into `init`* — rejected: `first-hour-compass` is the
  per-table (stateful) orientation card with its own value; `init` is install-time
  bootstrap. Different lifecycles; keep both, delegate across the seam.

## R5. Live profiling boundary — who owns it (and where grain comes from)

**Decision**: The EXISTING `retail-onboard-table` verb (reached via
`first-hour-compass`) owns the Stage-1 read-only profile, which is DB-backed —
`src/retail/profile.py` runs over a `QueryRunner` (`SELECT ... information_schema
.columns`, count/distinct queries). Grain candidates + column types come from THAT
profile. The AGENT routes into the verb; the `init` module never profiles and never
opens a DB. When the boundary is absent, the existing deferred mode applies: report
boundary + enable steps, mark `[PENDING LIVE PROFILE]`, stay useful, never traceback,
never fake a pass. There is NO CSV/Excel profiler, and building one is out of scope
(YAGNI, `CLAUDE.md`) — so the guaranteed visible result requires a live DB.

**Rationale**: Reuses the proven deferred-boundary contract (AGENTS.md "Live DB
steps — graceful deferred mode"; `retail validate`). Keeps the `init` module DB-free
(FR-003, FR-012, SC-005). `retail-onboard-table` (not `source-mapping`, which is the
downstream Stage-2 gate) is the verb that owns the Stage-1 profile — so it, not
`source-mapping`, is the route and must be in the compass `verbs[]` (BLOCKER-1 /
MAJOR-2 from the adversarial review).

**Alternatives considered**:
- *`init` module profiles directly* — rejected: duplicates profiling logic, pulls the
  DB boundary into the bootstrap path, and (since the verbs are agent-performed prose,
  not importable functions) is not even mechanically possible.
- *Route into `source-mapping` for grain candidates* — rejected: `source-mapping` is
  the Stage-2 gate, downstream of where the Stage-1 profile produces grain candidates.
- *Build a CSV/Excel profiler to guarantee a no-DB result* — rejected: YAGNI, out of
  Phase-1 scope; the honest no-DB outcome is `[PENDING LIVE PROFILE]`.

## R6. F024 classification (inherited, confirmed)

**Decision**: `init` = **Official Workflow Skill** (agent procedure that drives a
step, writes files, self-grants nothing). The projection generator + (future) drift
linter = **Maintenance Automation** (CI, derived evidence, no truth). No new F024
category; no constitution amendment.

**Rationale**: Resolved in `distribution-ideas.md` (pre-spec question 1): the closed
five-category set already fits because neither category restricts INPUT to Core
Authority — only Product Module does, and `init` consumes the kit's own files, not a
table's truth. Carried here, not reopened.

**Alternatives considered**: *A 6th "Bootstrap" category* — rejected: FR-001 of spec
018 declares the five a normative closed set; adding one is a versioned amendment,
over-engineering when an existing category fits.
