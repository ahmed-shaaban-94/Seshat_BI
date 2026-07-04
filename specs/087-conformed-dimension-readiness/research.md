# Research: Cross-Star Conformed-Dimension Readiness Gate (087)

Phase 0 -- precedent survey, input-source confirmation, and the deferred-capability
note. Every read below was of a committed artifact in this worktree; no live DB, no
Power BI/PBIP surface, no network was touched.

## Precedents (what SHIPPED to reuse, what to stay distinct from)

- **SF1 cross-layer checklist fork detector** (`src/retail/rules/rule_sf1.py`,
  spec 086, idea I3). SHIPPED. This is the DIRECT DESIGN PRECEDENT. REUSE, verbatim in
  shape: (a) the human-authored `docs/quality/*.yaml` manifest declaring shared-vs-distinct
  INTENT; (b) a static rule that only READS the manifest and never writes it; (c) the
  fail-closed posture on an UNDECLARED collision, a bad enum value, and a missing/unparseable
  manifest, with WARNING on a stale entry and a moot declaration; (d) the LAZY `import yaml`
  (kept out of the `retail check` static-core chain); (e) `ctx.tracked_files`-only reads with
  the `is_test_path` fixture exemption. STAY DISTINCT: SF1 reconciles same-BASENAME CHECKLIST
  files under `skills/**/checklists/` by BYTE-HASH; HR1 reconciles same-NAMED GOLD DIMENSIONS
  across `mappings/*/source-map.yaml` stars by GRAIN+KEY+TYPE. Different subject, different
  manifest (`shared-spine.yaml` vs `conformed-dimension-map.yaml`), different rule id
  (SF1 vs HR1). HR1 does NOT edit `rule_sf1.py`, does NOT read `shared-spine.yaml`, and reuses
  only SF1's declaration-then-enforce structure.

- **Gold Ready (Stage 4)** (`docs/readiness/gold-ready.md`; spec 006 warehouse-builder +
  spec 004 `retail validate`; static S6/S7 in `src/retail/rules/sql.py`, live RC2/RC15/RC16
  in `src/retail/validate.py`). SHIPPED. This is the neighbour HR1 composes ABOVE, never
  duplicates. Gold Ready validates ONE star (PK/grain uniqueness, contiguous date dim, zero
  orphan FKs, penny-exact reconciliation) and is PER-TABLE -- it cannot see a second star.
  HR1 validates that shared dimensions AGREE across two or more stars, a property that only
  exists once more than one Gold-Ready star exists. HR1 re-runs no Gold Ready check, touches
  no `retail validate`, and adds no per-table gate.

- **The source-mapping gate / `source-map.yaml`** (Principle IV, spec 001; template
  `templates/source-map.yaml`; filled instances `mappings/retail_store_sales/source-map.yaml`,
  `mappings/demo_sample_orders/source-map.yaml`). SHIPPED. This is the PER-TABLE artifact HR1
  READS. HR1 adds NO new key to `source-map.yaml` (that surface is owned by the source-mapping
  gate and is shared across many in-flight features); the cross-star declaration lives in the
  NEW, separate `docs/quality/conformed-dimension-map.yaml`. HR1 never rewrites a
  `source-map.yaml` and never re-decides a table's own grain/PK/placement (those are that
  table's already-reviewed Mapping Ready judgments).

- **The wiring meta-gate + rule-count lockstep** (C2 in `src/retail/rules/g6.py` family,
  `tests/unit/test_wiring_meta_gate.py`, `tests/unit/test_rules_wiring.py` `EXPECTED_RULE_IDS`,
  `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
  `docs/quality/rule-count-claims.yaml`, `docs/glossary.md`). SHIPPED. Adding one
  `@register`ed rule REQUIRES the SF1/AP1 six-surface wiring update in the SAME commit
  (see FR-014 and this plan's sequencing). REUSE the discipline exactly.

## Input-source confirmation (what HR1 reads on disk)

| Input | Confirmed on-disk source | Notes |
|-------|--------------------------|-------|
| Per-star shape | `mappings/<table>/source-map.yaml` `gold_star` block | a table is a STAR when it carries `gold_star.fact`; both committed maps do |
| Declaration manifest | `docs/quality/conformed-dimension-map.yaml` | NEW file -- does NOT exist yet (see Landing precondition) |
| Rule mechanism | `@register` / `RuleContext` / `Finding` / `Severity` / `is_test_path` in `src/retail/core.py` + `src/retail/registry.py` | reused unchanged; nothing new at the mechanism layer |

### Committed star shapes -- two DIFFERENT recorded conventions (load-bearing)

The two filled instances record their stars in NOTABLY different shapes; HR1 must parse BOTH:

- `mappings/retail_store_sales/source-map.yaml` -- the RICH form: dimension entries carry
  `name`, `surrogate_key`, `has_unknown_member`, and `attributes[]`; the date dim is a
  STANDALONE `gold_star.date_dimension:` block; dim names are schema-qualified and `_rss`-suffixed
  (`gold.dim_product_rss`) because this table shares the `gold` schema with the C086 star.
- `mappings/demo_sample_orders/source-map.yaml` -- the COMPACT form: dimension entries carry
  only `name` + `attributes[]` (NO `surrogate_key`, NO per-column `silver_type` join); the date
  dim is an ENTRY INSIDE `gold_star.dimensions[]` with `built_from` (not a standalone block);
  dim names are bare (`dim_product`, `dim_store`).

Two consequences the plan and data-model carry:

1. **The two committed stars share NO dimension name** (`dim_product` != `gold.dim_product_rss`).
   So the same-name cross-star detector (US2 / FR-006) is correctly INERT on the current tree;
   it is exercised by FIXTURES, and its real-tree value is guarding the FUTURE case where a new
   star reuses a bare dim name that an existing star also carries. This is expected, not a gap.
2. **The key and type limbs must DEGRADE GRACEFULLY.** `name` is present in both forms (so the
   name-collision + missing-map logic works today), but `surrogate_key` and a
   `columns[].silver_type` join are ABSENT from the compact form. HR1 MUST compare only fields
   that are present on both sides of a declared-conformed pair and never crash on an absent field
   (data-model records this). This is a robustness case BEYOND FR-004's date-dim note, surfaced by
   reading the real instances.

### The type limb IS mechanically implementable from committed fields

The type check resolves an attribute's silver type via the ALREADY-COMMITTED join
`columns[].gold_placement` -> `columns[].silver_type`: a column whose `gold_placement` is
`dim:<dim_name>.<attr>` contributes `<attr>`'s `silver_type` to `<dim_name>`. HR1 reads both
fields as they stand (FR-004: no new key). This clears the "implementable from committed fields"
bar. (In the compact demo form the `columns[]` join is absent, so the type limb is a no-op for
that pair -- graceful degradation, per above.)

### The grain limb is NOT mechanically implementable as written -- DEFERRED (C3)

FR-005's grain limb compares "the natural-key attribute", but `gold_star.dimensions[].attributes[]`
is a BARE LIST OF STRINGS with NO machine-readable natural-key marker (confirmed in the template
and both instances). No reliable signal exists: first-position fails
(`demo_sample_orders` `dim_product` lists the descriptive `product_name` first, not a key) and an
`_id`-suffix heuristic fails (`retail_store_sales` `dim_product` natural key is `item`, no suffix).
A fail-closed ERROR rule (Principle I) MUST NOT rest on an unenforced authoring convention.

RESOLUTION (this plan): 087 ships the KEY limb and the TYPE limb NOW and marks the GRAIN limb
`[PENDING SCHEMA PREREQUISITE]` (Principle VIII: author the static structure, defer the part whose
input surface does not yet exist). The natural-key SIGNAL must be an explicit marker OWNED by the
source-mapping-gate schema (`source-map.yaml`) that HR1 would READ (never write -- FR-004). Because
`source-map.yaml` is a SHARED surface OUTSIDE this feature's collision-avoidance allocation (which
is exactly HR1 + `conformed-dimension-map.yaml`), 087 does NOT edit it. The marker is recorded as a
cross-feature PREREQUISITE, not landed here. This is a schema/mechanics question, NOT a Principle-V
grain ruling -- HR1 re-decides no table's grain; it only reads a shape decided at Mapping Ready.

## Landing precondition (the 086-class defining risk -- via FR-010, not FR-006)

Both committed tables carry `gold_star.fact`, so 2+ stars exist TODAY, and
`docs/quality/conformed-dimension-map.yaml` does NOT exist yet. By FR-010, a MISSING map WITH 2+
stars is itself a fail-closed ERROR. So the instant HR1 registers, `retail check` returns non-zero
-- HR1 lands RED, not green, on the current tree. This is the 086 "no manifest = no green landing"
risk, transferred through FR-010 (map absence) rather than FR-006 (name collision).

To land GREEN the map file must EXIST. Because the two committed stars share NO dimension name,
there is NOTHING to adjudicate conformed-vs-distinct: an EMPTY-BUT-PRESENT map (a
`dimensions:` mapping with no entries) satisfies FR-010 on the current tree. Authoring an empty
scaffold when there is no collision to rule is NOT a Principle-V act (no human judgment is being
made). If a future tree DID carry a real same-name collision, the owner would have to rule it
`conformed` or `distinct` first (a Principle-V act the agent may NOT perform); the agent may
scaffold only the SHAPE on request. plan.md sequences "map file exists (empty scaffold OK on
current tree)" BEFORE the gate goes green.

## Deferred capabilities NOT assumed

- **F016 Power BI execution adapter** (official Power BI MCP / connection; `pbi-cli` no longer
  preferred) is gated + LAST and is assumed NOT to exist. HR1 never invokes it.
- **Live DB / `retail validate`** cross-star reconciliation (proving the MATERIALIZED dimensions
  agree at the data level) is DEFERRED to the `retail validate` surface (Principle VIII). HR1
  proves the DECLARED shapes agree from committed text only; it opens no database connection and
  reads no live Power BI/PBIP surface.
- **The grain-limb natural-key marker** is a source-mapping-gate schema PREREQUISITE that does not
  exist yet; the grain limb is authored PENDING and not exercised against real data here.
- No new per-table readiness stage and no model-level pass sink are assumed to exist; where (if
  anywhere) a model-level pass is recorded is OPEN (FR-016) and not invented here.

## Open (Principle V -- NOT resolved here; carried to the owner)

- **Q-APPROVAL-SEAM (FR-016)**: whether the model-level conformed tier needs a NAMED-HUMAN
  approval seam on top of the mechanical HR1 gate, or is purely mechanical like Silver/Gold Ready
  (a clean HR1 run IS the sign-off, no `approvals[]` entry). This is a who-approves governance-shape
  ruling (Principle V) the agent MUST NOT settle. RECORDED PENDING DEFAULT the owner may ratify:
  MECHANICAL. Until the owner rules, HR1 emits Findings only and records no model-level pass
  anywhere.

## Decisions carried from Clarifications (Session 2026-07-04)

- **C1** (in-scope dims): conformance set = `gold_star.dimensions[]` lookup dims PLUS a
  `gold_star.date_dimension` block where present; EXCLUDES `gold_star.degenerate_dimensions[]`.
- **C2** (map shape): mirror `shared-spine.yaml` -- top-level `dimensions:` mapping, each entry
  `status: conformed|distinct` + `stars: [<table_id>, ...]`.
- **C3** (natural-key signal): DEFERRED to plan; grain limb pending a source-mapping-gate marker
  HR1 reads (above).
- **C4** (shared-attribute set): the INTERSECTION of attribute-NAME sets across the conformed stars
  (Kimball conformed-subset); a type disagreement on an intersection attribute is an ERROR, a
  differing attribute SET alone is not.

## Honesty limitation (recorded, not designed around)

HR1's trigger and the `conformed-dimension-map.yaml` key are a single dimension NAME. A conformed
dimension deliberately named DIFFERENTLY per star (e.g. `dim_product` vs `gold.dim_product_rss`)
cannot be expressed in the name-keyed map shape and is therefore OUT OF HR1's reach. Cross-NAME
conformance is future scope; this feature enforces conformance of same-NAMED dimensions only.
