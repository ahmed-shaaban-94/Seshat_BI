# Implementation Plan: Shareable Seshat Proof (Showcase Bundle)

**Branch**: `127-showcase-build` | **Date**: 2026-07-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/127-showcase-build/spec.md`

## Summary

Add a read-only **composition and rendering layer** that reads the shipped
readiness/Explorer projection, the Passport, and the disclosure scanner, then
renders one disclosure-safe, offline, accessible, RTL/Arabic-safe **showcase
bundle** (landing page + per-table detail + truthful badge/card + four-category
disclosure manifest + optional before/after). It recomputes no readiness,
defines no new evidence schema, and adds no new CLI verb. The technical approach
is a small library function (`build_showcase_bundle` + `render_showcase_html`)
that layers a badge, a manifest, an optional Passport-diff section, and an
a11y/RTL shell over `build_explorer_projection`, then writes locally through the
existing contained-output guard, fail-closed on `scan_disclosure`.

## Technical Context

**Language/Version**: Python 3.11+ (matches shipped `src/seshat/`; stdlib-only core, `yaml` already a lazy dep).

**Primary Dependencies**: None new for the core. Reuses shipped modules: `seshat.explorer.build` (projection + HTML helpers), `seshat.passport` (snapshot + verify vocabulary), `seshat.readiness_projection` / `readiness_classify` / `readiness_evidence`, `seshat.review_integration`, `seshat.blocker_explainer`, `seshat.approval_inbox`, `seshat.disclosure` (fail-closed scan), `seshat.cli.guards.resolve_local_output`, `seshat.color` + the spec-102 `design_contrast` / `design_categorical_distinctness` rule logic for the a11y shell.

**Storage**: Local files only, under the contained `.seshat-output/` root. No database. No network.

**Testing**: pytest (`tests/unit/` + `tests/integration/`), mirroring `tests/integration/test_explorer_disclosure.py` and `test_passport_cli.py`. Fixtures: worked example, all-missing, mixed-state, comparable/non-comparable snapshot pairs.

**Target Platform**: Cross-platform Python; generated bundle is a static offline HTML/asset set openable in any modern browser, including RTL.

**Project Type**: Single project (library + skill surface), matching the shipped `src/seshat/` layout. NO new top-level CLI verb (Option B).

**Performance Goals**: Generation is a single read-render pass; linear in table count (inherits the Explorer projection's per-table linearity). Interactivity is a non-goal (static bundle).

**Constraints**: Offline-only; fully self-contained (all assets inlined / data-URI); fail-closed on disclosure findings; read-only w.r.t. every source artifact; ASCII + UTF-8-no-BOM tracked text; short repo-relative paths (Windows MAX_PATH).

**Scale/Scope**: Worked-example scale (single-digit to low-tens of tables). No live DB, no Power BI Desktop.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / spine rule | Relevance | Compliance in this plan |
|------------------------|-----------|--------------------------|
| I. Agent-First, Gate-Enforced | The gate authority stays the checker/projection, not this renderer | The bundle READS the projection's classifications; it never asserts a pass. `retail check` stays the authority; this feature gates nothing. |
| II. Depend, Never Fork | No adapter change | No Power BI adapter touched; no fork. |
| III. Medallion, Postgres-First, Gold-Only | Read-only rendering | No warehouse read/write; no engine dependency. |
| IV. Source Mapping Before Silver | N/A build order | The feature builds nothing in the medallion; it renders committed evidence. |
| V. Agent Stops at Judgment Calls | Approval / PII / publish | Generation grants no approval and no publish sign-off (FR-011); PII/secret presence fails closed (FR-009/010); no grain/rollup/identity decision is made. No Principle-V seam is auto-cleared. |
| VI. Defaults Then Deviations | N/A | No cleaning defaults involved. |
| VII. C086 Is An Example | Genericity | Spec + plan are generic; C086/pharmacy specifics stay in worked-example artifacts, never baked into the renderer. |
| VIII. Static-First, Live Deferred | Live evidence | Deferred live checks render as `unavailable`, never as a pass (FR-003); no live DB dependency added. |
| IX. Secrets and Reproducibility | Disclosure + encoding | Fail-closed disclosure scan (FR-009/010); ASCII/UTF-8-no-BOM; short paths; local-only output. |
| Readiness spine: never a fabricated confidence number | Badge | Badge is a stage summary derived from evidence; no percentage/grade/score (FR-012/013). |
| Option B (ratified 2026-07-07) | Delivery shape | Skill/composer over a library function; no new CLI verb (FR-005). |
| Spec 102 a11y/RTL gate | Accessible/RTL shell | Shell aligns to shipped `design_contrast` / `design_categorical_distinctness`; no new a11y criteria invented (FR-022/024). |

No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/127-showcase-build/
|--- spec.md              # Feature specification (done)
|--- plan.md              # This file
|--- research.md          # Phase 0: reuse-vs-net-new resolutions
|--- data-model.md        # Phase 1: bundle / badge / manifest / comparison shapes
|--- quickstart.md        # Phase 1: how to generate + open the bundle
|--- contracts/           # Phase 1: skill contract + library function signatures
`--- tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/seshat/
|--- showcase/                 # NEW: the composition + rendering layer
|   |--- __init__.py           # exports build_showcase_bundle, render_showcase_html
|   |--- build.py              # compose over build_explorer_projection; badge + manifest + optional diff
|   |--- badge.py              # truthful evidence-derived badge/card (no score)
|   |--- manifest.py           # four-category disclosure manifest builder
|   |--- compare.py            # optional Passport-pair comparability + diff (reuses passport verdicts)
|   `--- assets/               # NEW showcase shell (own a11y/RTL css/js) -- NOT explorer.css/js
|       |--- showcase.css
|       `--- showcase.js
`--- (reused, unchanged) explorer/build.py, passport.py, readiness_projection.py,
    readiness_classify.py, readiness_evidence.py, review_integration.py,
    blocker_explainer.py, approval_inbox.py, disclosure.py, cli/guards.py,
    color.py, rules/design_contrast.py, rules/design_categorical_distinctness.py

.claude/skills/
`--- showcase-build/           # NEW: the Option-B read-only skill surface
    `--- SKILL.md              # invokes the library function; documents offline/fail-closed posture

tests/
|--- unit/
|   |--- test_showcase_badge.py       # truthful badge, no fabricated score
|   |--- test_showcase_manifest.py    # four-category coverage, no silent drops
|   `--- test_showcase_compare.py     # comparability + graceful omission
`--- integration/
    |--- test_showcase_disclosure.py  # fail-closed on secret/DSN/PII/abs-path; nothing written
    |--- test_showcase_render.py       # offline self-contained bundle over worked example + all-missing
    `--- test_showcase_a11y_rtl.py     # spec-102 contrast/colorblind; dir=rtl; explorer assets byte-unchanged
```

**Structure Decision**: Single-project library + skill, mirroring the shipped
`src/seshat/explorer/` package (a sibling `showcase/` package with its own
`assets/`). The showcase package DEPENDS ON the explorer/passport/disclosure
modules and MUST NOT modify them or their assets. The user-facing surface is an
Option-B skill (`.claude/skills/showcase-build/`) that calls the library
function; no `_DISPATCH` CLI-verb entry is added.

## Phase 0: Research (resolutions to record in research.md)

1. **Delivery shape (verb vs skill)** -- RECOMMENDED DEFAULT, ratifier decides (open_for_human): skill over a library function (applying the ratified Option B policy, 2026-07-07); the default adds no new verb. This is NOT auto-resolved -- it is a reversible-but-costly product-identity choice routed to the ratifier (spec FR-005 + "Open for Human"). Sibling-tension note (verified): the peer explorer/passport verbs were added by spec 120 (created 2026-07-11, AFTER the ratification), so they are NOT grandfathered -- they are a live verb-parity precedent the ratifier may use to override to a verb. Whichever shape is ratified, the composition logic lives in a reusable library function so the shape stays separable.
2. **Redact vs fail-closed tension (req 4 vs req 7)** -- RESOLVED: live secret/DSN/PII/residual-abs-path findings block generation. The scan MUST run over the FULL composed body (tables + enriched lineage + approvals + badge + manifest + comparison), merged with the base projection's invariant findings -- NOT a carry-through of `build_explorer_projection`'s `disclosure` (which scanned only the base body before lineage/approvals/comparison, notably leaving user-supplied before/after snapshot content unscanned). "Redacted" names by-design portability normalizations only (abs-path -> repo-relative, private URL stripped), applied BEFORE the scan. Order: compose -> normalize/redact -> scan full body -> fail-closed.
3. **"Private URL" scanner coverage** -- OPEN for Phase 1: `scan_disclosure` today covers connection strings, absolute paths, secret keys, PII, raw arrays, but NOT private/internal URLs. DECISION to record in research.md: prefer a small additive extension to the shared scanner (a private-host/URL rule) so the guarantee is central and testable; fall back to composer-local stripping listed under "redacted" if extending the shared scanner would broaden its blast radius. Either way, absolute-path and secret handling stay fail-closed.
4. **Badge semantics** -- RESOLVED: highest contiguous `pass` stage + passed-stage count (e.g. "3/7 stages ready; Gold: blocked"); offline inline SVG/markup or data URI; never a percentage/grade/score.
5. **Comparability rule for before/after** -- RESOLVED: two Passport snapshots comparable iff same `schema_version` and same `scope`, differing `source_revision`; diff expressed in the Passport verify vocabulary; otherwise omitted with a note.
6. **a11y/RTL alignment** -- RESOLVED: reuse spec-102 `design_contrast` + `design_categorical_distinctness` thresholds against the showcase shell's own palette; render the shell over the projection data; do not edit `explorer.css`/`explorer.js`.

## Phase 1: Design outputs

- **data-model.md**: shapes for the showcase bundle document, badge/card, four-category disclosure manifest, and comparison pair -- each expressed as a projection over reused documents (no new persisted schema).
- **contracts/**: the skill contract (inputs: repo root, optional output path, optional RTL mode, optional two snapshot paths; outputs: written bundle path OR fail-closed findings) and the library function signatures (`build_showcase_bundle(repo_root, *, snapshots=None) -> dict`, `render_showcase_html(bundle, *, repo, rtl=False) -> str`).
- **quickstart.md**: generate the bundle from the worked example, open it offline, read the badge + manifest, and confirm source artifacts are byte-unchanged.

## Complexity Tracking

No Constitution Check violations; no entries required.
