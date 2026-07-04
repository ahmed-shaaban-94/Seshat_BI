# Implementation Plan: Customer / Loyalty Grain + Dimension Pattern

**Branch**: `098-customer-loyalty-grain` | **Date**: 2026-07-04 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/098-customer-loyalty-grain/spec.md`
(clarified 2026-07-04: Q1 canonical marker string adopted, Q2 structural FK join
adopted, Q3 grain pattern stays doc-only, Q4 SCD/historization slot added, Q5 the five
Principle-V rulings stay explicitly open).

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

**Status**: Draft. Stops at the design set below -- NOT approved, NOT implemented, NOT
ratified. Neither `docs/patterns/customer-dimension-pattern.md`,
`docs/patterns/customer-grain-pattern.md`, nor `templates/customer-dimension.md` exists
yet; none is authored by this planning stage.

## Summary

Customer is the heaviest KPI knowledge domain in the repo
(`skills/retail-kpi-knowledge/domains/customer.md`, spec 042) yet has no GENERIC
dimension or customer-grain pattern in the spine -- only one filled, table-scoped
instance (`gold.dim_customer_rss`, warehouse/migrations/0004) built on one
already-answered PII ruling for one source. This feature closes that structural gap
with THREE new artifacts: a generic conformed customer-dimension pattern doc
(`docs/patterns/customer-dimension-pattern.md`), a generic customer-grain pattern doc
(`docs/patterns/customer-grain-pattern.md`, doc-only, no template), and a copy-me
dimension template (`templates/customer-dimension.md`). Each carries explicit
`[NEEDS CLARIFICATION: ... -- owner ruling]` placeholder slots for the identity key, the
PII-publish decision, and the SCD/historization type -- never a default answer -- and
the grain pattern names candidate grains for the four Planned customer KPIs
(retention, frequency, CLV, new-vs-returning) as OPTIONS tied to the same
retention-window / CLV-horizon / anchor ambiguities `domains/customer.md` already
carries, deciding none of them.

The technical approach is DOCS + ONE TEMPLATE ONLY: no code, no `retail check` rule, no
database, no edit to any existing gold table, TMDL, or the `domains/customer.md`
knowledge file. This serves Stage 2 (Mapping Ready: a table's map can cite a pattern for
its customer dimension/grain instead of inventing one) and Stage 5 (Semantic Model
Ready: a future customer metric contract has a conformed dimension + grain shape to
bind to), without advancing or self-granting any readiness stage itself.

## Technical Context

**Language/Version**: N/A -- this feature authors markdown documentation and a
markdown template only. No source code, no interpreter, no build step.

**Primary Dependencies**: None. No new Python dependency, no new import, no CLI
surface. This is the same "docs + templates" shape as the original Phase 0/1 kit
foundation (spec 001) and the shipped Companion Modules skills (F025-F030) -- prose and
structured markdown, nothing executed.

**Storage**: N/A -- no database, no live connection. The only "storage" this feature
touches is the git-tracked repository text itself (two new docs, one new template).

**Testing**: No automated test suite is added (there is no code to unit-test). Verification
is by the checks quickstart.md enumerates: `retail check` exit 0 with the unchanged rule
count (SC-006), a grep-based scan for C086-specific defaults (SC-003) and for numeric
scores (SC-004), and a byte-identical diff on the two shipped neighbours (SC-005). These
are the same class of static/textual checks the constitution's "Compliance review"
section already prescribes for a docs-only slice.

**Target Platform**: N/A -- markdown files read by a human analyst and an agent; no
runtime target.

**Project Type**: Documentation/template addition to the existing single-project repo
(no new project, service, or top-level directory beyond the new `docs/patterns/`
subdirectory).

**Performance Goals**: N/A -- no code path, no measurable-scale requirement.

**Constraints**: ASCII, UTF-8 without BOM, short repo-relative paths (Principle IX,
FR-012); one canonical unresolved-ruling marker string used verbatim across all three
authored artifacts (FR-002); MUST NOT edit `warehouse/migrations/0004_...sql`, its TMDL
mirror, or `skills/retail-kpi-knowledge/domains/customer.md` (FR-007, FR-008, SC-005);
MUST NOT create or modify any file under `contracts/` (FR-009, SC-007); MUST NOT
introduce a new `retail check` rule id or widen/narrow which readiness stages carry an
`approvals[]` requirement (FR-015, SC-006); MUST NOT connect to a live database or
assume F016 exists (FR-013, Principle VIII); MUST NOT decide identity resolution, PII
publish-safety, SCD/historization type, retention window, CLV horizon, or the
new-vs-returning anchor (Principle V, FR-004, FR-005, FR-006).

**Scale/Scope**: Exactly THREE new files (`docs/patterns/customer-dimension-pattern.md`,
`docs/patterns/customer-grain-pattern.md`, `templates/customer-dimension.md`) plus this
Spec-Kit chain's own four planning documents under `specs/098-customer-loyalty-grain/`.
One new directory is created (`docs/patterns/`, confirmed absent before this feature).
No existing file is edited by the eventual implementation stage; no wiring surface
(rule registry, manifest, glossary rule count) is touched because no rule is added.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | How this design satisfies it |
|---|---|---|
| **I. Agent-First, Gate-Enforced** | A rule fails CLOSED (blocks), never merely advises; compliance is demonstrable by running `retail check`. | This feature adds NO new rule, so there is no advisory-surface-masquerading-as-a-gate risk to guard against. Compliance is demonstrable the honest way for a docs-only change: `retail check` exits 0 over the changed tree with the SAME registered-rule count as before (SC-006) -- the checker remains the sole authority on pass/fail; this feature does not add a second, competing compliance signal. |
| **III. Medallion/Gold-Only** | `gold` IS a Kimball star (fact + CONFORMED dimensions); Power BI reads `gold` only; Postgres-first. | The customer-dimension pattern IS a conformed Kimball dimension shape (surrogate `customer_sk`, `-1` unknown member, FK COALESCE -- RC14) -- it gives Principle III's "conformed dimensions" half a generic, reusable shape for the customer entity, which today exists only as one table-scoped instance. This feature writes no SQL and touches no `gold` schema itself; it authors the SHAPE a future table's own gold build would instantiate. |
| **IV. Source-Mapping-Before-Silver** | No `silver.*` SQL before the source-map is reviewed+approved. | This feature writes no `silver.*` SQL and no `source-map.yaml` for any table. The pattern and template are consumed UPSTREAM of a future table's own mapping-gate review (FR-014: cited by name from a `source-map.yaml` `gold_star.dimensions[]` entry, not embedded as a bypass). No table's mapping gate is weakened, skipped, or pre-approved by this feature's existence. |
| **V. Agent-Stops-at-Judgment** | The agent MUST NOT decide grain/PII/business-policy/approval alone; it raises an unresolved-questions entry and STOPS. NEVER self-grant a readiness pass. | Every load-bearing judgment call this feature touches -- the identity key, the PII-publish ruling, the SCD/historization type, the retention window, the CLV horizon/discounting choice, and the new-vs-returning anchor -- is named as an explicit `[NEEDS CLARIFICATION: ... -- owner ruling]` slot and decided by NEITHER document nor the template (FR-002, FR-004, FR-005, FR-006). Identity resolution across multiple raw ids is named as a reserved owner ruling with a cross-reference to `domains/customer.md`, proposing no merge algorithm (FR-005, User Story 3). This feature records no `approvals[]` entry, advances no readiness stage, and self-grants no pass (FR-009, FR-015). |
| **VI. Defaults-Then-Deviations** | Start from existing rulings; record only deviations. | The pattern reuses RC14 (surrogate keys, `-1` unknown member, FK COALESCE) and RC15-adjacent conventions verbatim as the structural mechanic -- no new key convention is invented (spec Assumptions). The spec's own Clarify session applied Principle VI THREE times as pure authoring-consistency defaults that decide no domain question: Q1 (one canonical marker spelling), Q2 (every candidate grain states its FK join to `customer_sk`), and Q4 (naming the SCD slot as a fourth dimension-shape element, deciding Type 1 vs. Type 2 for neither). None of the three genuinely open business/governance rulings (identity, PII, retention/CLV/anchor) was defaulted (Q5: explicitly left OPEN). |
| **VII. C086-is-an-example** | Generic templates carry no domain specifics. | Neither new pattern doc nor the template inlines a `retail_store_sales`/C086 column name, table name, or ruling as a default (FR-011). `gold.dim_customer_rss` and its Q1 PII answer are cited in prose ONLY as "one filled, source-specific answer" (research.md), never copied inline as the shown example value. The identity-key slot's illustration is the marker string itself, never `customer_id`. |
| **VIII. Static-First/Live-Deferred** | A live DB surface is deferred; author static structure + mark live PENDING. | This feature performs no live database connection, no `retail validate` run, and assumes no F016 execution adapter (FR-013). It authors STATIC structure only (two markdown docs, one markdown template) and marks every semantic ruling PENDING via the canonical marker rather than assuming a live profiling result. Any live application of the pattern to a real table is that future table's own Stage 1/2 profiling work, explicitly deferred. |
| **IX. Secrets/Reproducibility** | Never commit a real host/DSN/secret; ASCII, reproducible, Windows-safe. | This feature touches no connection string, DSN, or credential. All new artifacts are ASCII, UTF-8 without BOM, and keep short repo-relative paths (`docs/patterns/customer-dimension-pattern.md`, `docs/patterns/customer-grain-pattern.md`, `templates/customer-dimension.md`) well under the Windows `MAX_PATH` budget (FR-012). |
| **Hard rule #9** | NO fabricated confidence/health/maturity score or completeness count. | Neither pattern doc nor the template computes or displays a percentage, ratio, "N of 4 KPIs," or any other numeric confidence/health/maturity/completeness score anywhere (FR-010, SC-004). Applicability is expressed only as which slots are filled (generic, structural: surrogate key, unknown-member row, FK join) vs. which remain an explicit owner-ruling marker. |

**Result**: PASS. No principle requires a documented violation; Complexity Tracking
below is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/098-customer-loyalty-grain/
|-- spec.md              # Feature specification (input to this stage; already clarified)
|-- plan.md              # This file (/speckit-plan command output)
|-- research.md          # Phase 0 output (/speckit-plan command)
|-- data-model.md         # Phase 1 output (/speckit-plan command)
|-- quickstart.md         # Phase 1 output (/speckit-plan command)
`-- tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created here)
```

No `contracts/` directory: this feature has no network API/CLI contract to specify --
it is two static markdown documents and one static markdown template, no executable
surface (consistent with the docs-only precedent of the original Phase 0/1 kit
foundation and the F025-F030 Companion Modules skills, none of which added a
`contracts/` directory either).

### Source Code (repository root)

This is the existing single-project repo. No new project, service, or executable
surface is introduced. Concrete real paths this feature adds (implementation-stage;
recorded here so the plan does not miss any surface per FR-001):

```text
docs/
`-- patterns/                                # NEW directory (confirmed absent pre-feature)
    |-- customer-dimension-pattern.md        # NEW -- generic conformed customer-dimension shape (FR-002, FR-005, FR-006)
    `-- customer-grain-pattern.md            # NEW -- generic candidate-grain doc for the 4 Planned customer KPIs (FR-003, FR-004); DOC-ONLY, no template (Clarify Q3)

templates/
`-- customer-dimension.md                    # NEW -- copy-me dimension template instantiating the pattern's shape (FR-001, FR-014)
```

**Explicitly untouched (so a reviewer sees these were considered, not missed)**:

```text
src/retail/rules/                            # UNTOUCHED -- no new rule id; no wiring-meta-gate edit (FR-001, FR-015)
tests/                                       # UNTOUCHED -- no code exists to test
docs/rules/rules-manifest.json               # UNTOUCHED -- rule count unchanged (SC-006)
docs/rules/severity-posture.json             # UNTOUCHED -- no new rule registered
docs/glossary.md                             # UNTOUCHED -- rule-count anchor unchanged
docs/roadmap/roadmap.md                      # UNTOUCHED -- spec.md Assumptions: no new F-number allocation required by this spec
contracts/                                   # UNTOUCHED -- FR-009, SC-007 (F009's gated process stays the only route to a seeded metric contract)
warehouse/migrations/0004_create_gold_retail_store_sales_star.sql   # UNTOUCHED -- FR-007, SC-005 (byte-identical)
powerbi/RetailStoreSales.SemanticModel/definition/tables/gold dim_customer_rss.tmdl   # UNTOUCHED -- FR-007, SC-005 (byte-identical)
skills/retail-kpi-knowledge/domains/customer.md   # UNTOUCHED -- FR-008, SC-005 (byte-identical; cited, never edited)
mappings/**                                  # UNTOUCHED -- this feature seeds no filled instance for any table
templates/source-map.yaml                    # UNTOUCHED -- FR-014's citability is by naming convention only; no new schema key added
```

**Structure Decision**: Single project, additive-only, docs + one template. This
feature touches exactly three new files and creates one new directory
(`docs/patterns/`). It edits NO existing file. Unlike a rule-adding feature (e.g. spec
087's HR1), there is no `src/retail/rules/` entry, no wiring-meta-gate lockstep, no
rule-count bump, and no fixture corpus to author -- the collision-avoidance allocation
for this parallel-build round is explicit that this feature "adds NO static rule" and
"touches no shared schema."

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring justification:
this feature adds no code, no dependency, no rule, no schema change, and no new
project/service/architectural layer. It is strictly additive documentation plus one
template.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| (none) | -- | -- |
