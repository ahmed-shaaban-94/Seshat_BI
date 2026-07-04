# Phase 0 Research: Semi-Additive (Snapshot) Grain in the Metric Contract

**Feature**: 091-semi-additive-snapshot-grain | **Date**: 2026-07-04

## Purpose

Resolve, from committed artifacts only, what this feature reuses, what it must
stay distinct from, and what it must NOT assume exists. No new investigation
tool is introduced; every finding below cites a real repo path already read
during spec authoring / this planning pass.

## 1. Precedent survey -- what SHIPPED artifacts this feature reuses

### 1.1 The scaffold to clone: AL1 (`src/retail/rules/assumptions.py`, spec 059)

AL1 is the direct shape precedent named in the spec's own Assumptions and in
Edge Cases/FR-004/FR-014. Confirmed by reading the module:

- Lazy `import yaml` INSIDE the `@register`-decorated function only (module
  scope stays stdlib-only: `from __future__ import annotations`, `re`,
  `typing.Iterable`, plus the two local `..core` / `..registry` imports).
- Generic glob over the deployable per-table contract store:
  `re.compile(r"^mappings/[^/]+/metrics/[^/]+\.ya?ml$")`.
- Two-line exemption: the literal template path
  (`templates/metric-contract.yaml`) and `is_test_path(p)` from `..core`.
- Fail-loud-on-unreadable: a `try/except (OSError, UnicodeDecodeError,
  yaml.YAMLError)` around the read+parse that emits an ERROR `Finding` naming
  the path and continues to the next file, never silently skipping.
- ERROR-only, never-resolves: the function returns `list[Finding]`, every
  entry `Severity.ERROR`; nothing in the module writes back to a contract.
- `@register("AL1", "<one-line title>")` decorator wraps a function taking
  `ctx: RuleContext` and returning `Iterable[Finding]`.

HR5 (this feature) clones this exact scaffold. No new parsing library, no new
traversal pattern.

### 1.2 The neighbour to stay distinct from: AD1 (`src/retail/rules/additivity_consistency.py`, spec 068)

Confirmed by reading the module and its plan (`specs/068-additivity-consistency-rule/plan.md`):

- AD1 reads a DIFFERENT corpus entirely: committed **define-layer prose**
  under `skills/retail-kpi-knowledge/contracts/*.md` (a regex heading scan,
  not YAML), classifying a metric's additivity from a `**Additivity**`
  prose heading and cross-checking it against `**Derives from**` composition
  prose via a small closed legality table (`_FULLY/_SEMI/_NON/_ABSENT`).
- AD1's own recorded design boundary (spec 068 Clarifications Q2, restated in
  spec 091's "Boundary against neighbouring shipped work"): AD1 "introduces
  no new machine-readable contract field... adding a structured field would
  be a separate, larger define-layer change." Spec 091 IS that separate
  change, but scoped ONLY to the date axis and ONLY on the deployable
  per-table `mappings/<table>/metrics/*.yaml` contract -- never on
  `skills/retail-kpi-knowledge/contracts/*.md`.
- AD1's "additivity classification" is a whole-metric COMPOSITION legality
  question (can this metric be validly summed from its lineage parents/
  children); `time_additivity` is narrower and orthogonal -- one measure's
  behavior when summed across DATES, independent of derivation lineage. A
  metric can be AD1-legal and still need `time_additivity: semi`.
- HR5 does not read, alter, import from, or duplicate any table/regex from
  `additivity_consistency.py`, and does not touch
  `skills/retail-kpi-knowledge/contracts/*.md`. Confirmed: no cross-import
  exists between `assumptions.py`/`additivity_consistency.py` today, and HR5
  will not introduce one.

### 1.3 The template this feature edits: `templates/metric-contract.yaml`

Read in full. Confirmed structure to extend:

- Top-level scalar/block fields in order: `name`, `grain`, `formula_intent`,
  `owner`, `binds_to` (block), `readiness` (block), `ambiguities` (list),
  followed by an authoring-notes comment block and an OPTIONAL
  `definition` block (F-DAXGEN, unrelated to this feature).
- Documentation style: a large header comment citing the owning doc + the
  Constitution principles it instantiates, then per-field comment blocks
  immediately above each field explaining intent, vocabulary, and citing the
  authoritative source doc. FR-001 requires the new `time_additivity` field
  to match this existing style and cite
  `skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md`.
- The `ambiguities[]` block (lines ~144-177) is the existing, UNCHANGED
  ledger this feature's trigger reads: each entry has `id` (one of
  `A1..A11`), `decision_status`, `ruling`, `evidence`, `number_moving`. HR5
  reads only the `id` field of each entry, matching the literal `A10`.

### 1.4 The A10 ambiguity id: `skills/retail-kpi-knowledge/knowledge/kpi-ambiguities.md`

Confirmed by reading the file (lines 65-70): `A10 -- Inventory snapshot date`.
Body text: "Inventory is semi-additive: a snapshot is a state at a point in
time, not a flow... Must never be summed across dates. Snapshot policy is
**Needs business definition** until confirmed." This is the fixed,
already-authored definition this feature CITES (FR-003, FR-015) and never
restates or redefines. `skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md`
is the sibling doc that states the general semi-additive concept the
template's new field comment cites.

### 1.5 The wiring precedent: five required places (FR-012)

Confirmed by reading each artifact AD1/AL1/AL2 touch (mirrors spec
068's Project Structure section exactly):

1. `src/retail/rules/__init__.py` -- add the new submodule name to both the
   side-effecting import tuple and `__all__` (alphabetical placement;
   confirmed the existing list is alpha-sorted apart from grouped design_*
   entries, so the new module name inserts alphabetically).
2. `tests/unit/test_rules_wiring.py` -- add the new rule id literal to the
   `EXPECTED_RULE_IDS` frozenset (confirmed: the test derives the expected
   COUNT from `len(EXPECTED_RULE_IDS)`, never a hardcoded number, and
   separately asserts `actual == EXPECTED_RULE_IDS` after a forced
   re-registration via `importlib.reload` over every submodule found by
   `pkgutil.iter_modules`).
3. `docs/rules/rules-manifest.json` -- regenerate (the file states each rule
   as `{"id": ..., "title": ...}`, alpha-sorted by id; confirmed existing
   `AD1`/`AL1` entries). Constitution Principle VIII: "The authoritative,
   always-current rule inventory is the generated
   `docs/rules/rules-manifest.json` (regenerate with `retail manifest`...)
   -- this document does not restate a literal rule count." This plan
   follows that: no literal count is asserted anywhere in this feature's
   artifacts; the manifest is regenerated and its length is the count.
4. `docs/rules/severity-posture.json` -- regenerate (confirmed shape:
   `"registered": {"<id>": [<observed-severities-or-"<no-finding>">], ...}`;
   AD1, whose current corpus produces zero findings, is recorded as
   `["<no-finding>"]`). HR5 is expected to regenerate to the same shape
   given SC-001's genuine zero-findings baseline; the exact token is
   produced by the regeneration tool, not hand-asserted here.
5. The new rule module itself + its behavior-test file (not a "wiring"
   point in the strict FR-012 sense, but the artifact FR-012 wires in) --
   `src/retail/rules/<new_module>.py` and
   `tests/unit/test_<new_module>.py`, mirroring
   `test_additivity_consistency.py`'s fixture-based pattern (a fixture YAML
   string parsed via `yaml.safe_load`, wrapped in a minimal `RuleContext`
   double or the real one over a temp tree -- confirmed as the pattern by
   file existence; exact fixture mechanics are an implementation-phase
   (`/speckit-tasks` + build) concern, not a planning-phase one).

No other file (glossary, roadmap, scaffold generator, SKILL.md docs) is a
required wiring point per FR-012's explicit five; a broader grep surfaced
`AL1`/`AD1` mentions in `docs/glossary.md`, `docs/roadmap/roadmap.md`,
`src/retail/scaffold.py`, and skill docs, but the spec's FR-012 and the
068 precedent do not require touching these for a rule to ship, and this
plan does not add them as required edits (avoiding un-scoped surface growth).

### 1.6 Collision-avoidance confirmation (092, 103)

Grepped the working tree for `time_additivity`: zero hits outside this
feature's own `spec.md`. Confirmed no other in-flight branch has already
claimed this key on `templates/metric-contract.yaml`. This feature adds and
touches ONLY the `time_additivity` top-level key; it does not rename,
reorder, or restructure any existing field, and does not add any other new
top-level key (092 adds a SEPARATE file; 103 adds its own differently-named
key -- neither is touched here).

## 2. Input-source confirmation

The following are the ONLY inputs this feature's design draws from, each
independently confirmed present and current in the working tree during this
research pass:

| Input | Path | Confirmed |
|---|---|---|
| Feature spec (clarified) | `specs/091-semi-additive-snapshot-grain/spec.md` | read in full |
| Metric contract template | `templates/metric-contract.yaml` | read in full |
| A10 ambiguity definition | `skills/retail-kpi-knowledge/knowledge/kpi-ambiguities.md` | read (lines 65-70) |
| Additivity/grain concept doc | `skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md` | path cited by spec; field comment cites it, content not restated here |
| AL1 scaffold (clone source) | `src/retail/rules/assumptions.py` | read in full |
| AD1 boundary precedent | `src/retail/rules/additivity_consistency.py` + `specs/068-additivity-consistency-rule/plan.md` | read in full |
| Rule registry package | `src/retail/rules/__init__.py` | read in full |
| Wiring unit test | `tests/unit/test_rules_wiring.py` | read (EXPECTED_RULE_IDS + regen mechanics) |
| Rules manifest | `docs/rules/rules-manifest.json` | read (shape + AD1/AL1 entries) |
| Severity posture manifest | `docs/rules/severity-posture.json` | read (shape + AD1 `<no-finding>` entry) |
| Current per-table contract corpus | `mappings/retail_store_sales/metrics/*.yaml` (5 files) | grepped for `A10` -- zero hits (genuine SC-001 baseline) |
| Constitution | `.specify/memory/constitution.md` (v1.7.0) | read in full |

No other document, script, or external source informs this design. No live
database, no Power BI file, no `pbi-cli`/execution-adapter surface was read
or is assumed.

## 3. Deferred capabilities NOT assumed

Per Principle VIII (Static-First, Live Deferred) and the task framing, this
design explicitly does NOT assume any of the following exist or are
reachable, and the built artifact will not import, call, or reference them:

- **F016 (Power BI execution adapter)**: not assumed to exist. HR5 never
  opens a PBIP file, never calls the official Power BI MCP/connection, and
  never calls `pbi-cli`.
- **Live database connection**: not assumed. HR5's entire read surface is
  committed repository text (`mappings/*/metrics/*.yaml`); no DSN, no
  `psycopg2`/driver import, no `retail validate` invocation.
- **A `time_additivity`-aware DAX generator / F-DAXGEN extension**: not
  assumed. The optional `definition:` block documented in the template
  (kind: base/ratio) is unrelated to this feature and is not read, written,
  or extended.
- **A new readiness stage or gate advancement**: not assumed. HR5 is
  OFF-SPINE (FR-011), exactly like AD1/AL1/AL2 -- it advances no readiness
  stage, grants no approval, and is not wired into
  `readiness-status.yaml`/`retail-orchestrate`.
- **A widened detection trigger beyond A10 (FR-018/Q4)**: not assumed or
  pre-built. No speculative second ambiguity id, measure-name heuristic, or
  "future-proofing" branch is added. If Q4 is ever answered by a named
  retail-kpi-knowledge owner, that is a separate future change.
- **Any live-marked-PENDING surface**: none is introduced by this feature at
  all (no partial live surface exists here to mark pending); this note is
  included only to record that the "no live DB unless via a marked-pending
  surface" constraint is satisfied vacuously -- there is no live surface of
  any kind in this feature.

## 4. Open item carried forward (not resolved here)

**FR-018 / Clarifications Q4** (whether snapshot-grain detection should ever
extend beyond the existing A10 id to a non-inventory semi-additive-over-time
shape) is a Principle-V retail-kpi-knowledge ledger-scope judgment call. This
planning pass does not answer it, does not scope build-work toward it, and
does not encode a placeholder for it in code or schema. It remains recorded
as `[NEEDS CLARIFICATION -- OPEN owner ruling]` in the spec and is carried
into this plan's Constitution Check (Principle V) unresolved.
