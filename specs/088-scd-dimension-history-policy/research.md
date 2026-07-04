# Research: Dimension History / SCD Policy Readiness (088)

Phase 0 -- precedent survey, input-source confirmation, and the deferred-capability
note. Every read below was of a committed artifact in this worktree; no live DB, no
Power BI/PBIP surface, no network was touched.

## Precedents (what SHIPPED to reuse, what to stay distinct from)

- **HR1 cross-star conformed-dimension gate** (`specs/087-conformed-dimension-readiness/`,
  reserved id HR1, DRAFT -- not implemented; no `src/retail/rules/rule_hr1.py` exists in
  this tree). This is the DIRECT DESIGN PRECEDENT for the SHAPE of a new rule: a
  human-authored declaration read by a fail-closed static rule, `Finding`/`RuleContext`/
  `@register` reused unchanged, `yaml` imported LAZILY, `ctx.tracked_files`-only reads with
  the `is_test_path` fixture exemption, and the six-surface wiring lockstep in the same
  commit. REUSE that shape. STAY DISTINCT on four material points (do not silently copy
  these):
  1. **087 declares in a NEW separate manifest** (`docs/quality/conformed-dimension-map.yaml`)
     because its declaration is a CROSS-star ruling that does not belong to any one table's
     map. 088's declaration (`scd_type`) is a PER-dimension, PER-table judgment that belongs
     exactly where `surrogate_key` / `has_unknown_member` already live -- inside that table's
     own `source-map.yaml`. 088 THEREFORE EDITS `templates/source-map.yaml` (adds the new
     nested key); 087 explicitly does not touch that file. Different shape, deliberately.
  2. **087's MVP defers its hardest limb (grain)** because no machine-readable signal exists
     in `attributes[]` today (both candidate heuristics failed against the committed
     instances). 088's MVP detection signal (the drop-and-rebuild construct, FR-007) is
     CONFIRMED implementable now against the one committed gold migration (see below) --
     nothing is deferred at the MVP layer. Only a FUTURE positive-recognition signal (once a
     builder can author real Type-2 SQL) is out of scope, and that is a narrower deferral
     than HR1's, not the same shape.
  3. **087 reads only YAML** (per-table `source-map.yaml` + its own manifest). 088 reads a
     SECOND input class: gold migration SQL text
     (`warehouse/migrations/*create_gold_<table>_star.sql`), as committed text only, never
     executed (Principle VIII; SCOPE GUARD).
  4. **087's landing story is a clean scaffold** (an empty `dimensions: {}` manifest satisfies
     its fail-closed floor with no Principle-V act, because there is nothing yet to
     adjudicate on the current tree). 088's landing story is the OPPOSITE: both committed
     maps' dimension entries currently carry NO `scd_type` key, so HR2's FR-005 fires an
     ERROR on every one of them the moment HR2 registers -- there is no scaffold that greens
     this without a human declaring real values (see "Landing precondition" below).

- **SF1 cross-layer checklist fork detector** (`src/retail/rules/rule_sf1.py`, spec 086).
  SHIPPED. Secondary precedent for mechanics only: the fail-closed-on-missing-manifest
  pattern, the lazy `import yaml`, and the `Finding(rule_id, severity, message, locator)`
  usage. HR2 does not read `shared-spine.yaml` and does not edit `rule_sf1.py`.

- **The source-mapping gate / `source-map.yaml`** (Principle IV, spec 001; template
  `templates/source-map.yaml`; filled instances `mappings/retail_store_sales/source-map.yaml`,
  `mappings/demo_sample_orders/source-map.yaml`). SHIPPED. This is the PER-TABLE artifact HR2
  both READS and (via the template) gains one new nested key in. HR2 does not touch
  `surrogate_key`, `has_unknown_member`, or `attributes[]`, and does not re-decide any
  table's own grain/PK/placement (Mapping Ready judgments already reviewed).

- **`retail-build-warehouse`** (`.claude/skills/retail-build-warehouse/SKILL.md`, spec 006).
  SHIPPED. This is the documentation of the ONE gold-authoring pattern that exists in this
  repo's tooling today ("Gold: the Kimball star" section) -- HR2's FR-007 detection signal is
  read directly off this documented shape, not invented. HR2 does not edit this skill and
  does not teach it to author Type-2 SQL (out of scope; Assumptions).

- **Gold Ready (Stage 4)** (`docs/readiness/gold-ready.md`; spec 006 + spec 004
  `retail validate`; static S6/S7 in `src/retail/rules/sql.py`, live RC2/RC15/RC16 in
  `src/retail/validate.py`). SHIPPED. HR2 is a NEW static check ADDED to this same Gold
  Ready static surface -- it does not re-implement S6 (`-1` unknown member) or S7
  (contiguous date dim), does not touch `retail validate`, and does not change any existing
  Gold Ready status meaning. A table can be `pass` on S6/S7/live-validate while HR2 reports
  its own, orthogonal finding.

- **HR1** is also the ORTHOGONAL-AXIS neighbour on the SAME `gold_star.dimensions[]` surface:
  HR1 checks that a shared dimension NAME agrees on grain/key/type ACROSS two or more stars;
  HR2 checks that ONE dimension's declared HISTORY POLICY is honored by its OWN star's build.
  HR1's declaration lives in a separate manifest; HR2's lives inside `source-map.yaml`. The
  two rule ids and concerns do not overlap and neither reads the other's artifact.

- **The wiring meta-gate + rule-count lockstep** (`tests/unit/test_wiring_meta_gate.py`,
  `tests/unit/test_rules_wiring.py` `EXPECTED_RULE_IDS`, `docs/rules/rules-manifest.json`,
  `docs/rules/severity-posture.json`, `docs/quality/rule-count-claims.yaml`,
  `docs/glossary.md`). SHIPPED. Adding one `@register`ed rule REQUIRES the SF1/AP1/HR1
  six-surface wiring update in the SAME commit (FR-014). REUSE the discipline exactly.

## Input-source confirmation (what HR2 reads on disk)

| Input | Confirmed on-disk source | Notes |
|-------|--------------------------|-------|
| Declared policy | `mappings/<table>/source-map.yaml` `gold_star.dimensions[].scd_type` | NEW nested key this feature introduces (schema footprint: exactly this one key, per collision-avoidance allocation) |
| Gold build shape | `warehouse/migrations/*create_gold_<table>_star.sql` | existing file class; ONE instance committed today, `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` |
| Rule mechanism | `@register` / `RuleContext` / `Finding` / `Severity` / `is_test_path` in `src/retail/core.py` + `src/retail/registry.py` | reused unchanged; nothing new at the mechanism layer |

### The committed gold migration confirms C5's corrected construct shape (load-bearing)

`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` was read directly (not
assumed) to verify what HR2's FR-007 signal must actually match:

- Lines 22-27: every `DROP TABLE IF EXISTS` for the star is BATCHED at the top of the file
  (`gold.fct_sales_rss`, `gold.dim_customer_rss`, `gold.dim_product_rss`,
  `gold.dim_payment_method_rss`, `gold.dim_location_rss`, `gold.dim_date_rss`) -- NOT adjacent
  to their matching `CREATE TABLE`.
- Each dimension is then recreated further down via explicit column DDL
  (`CREATE TABLE gold.dim_customer_rss (...)`) followed by one or more
  `INSERT INTO gold.dim_customer_rss ...` statements (the unknown-member row first, then the
  real rows) -- e.g. `CREATE TABLE gold.dim_product_rss (...)` at line 42, `INSERT INTO
  gold.dim_product_rss OVERRIDING SYSTEM VALUE VALUES (-1, ...)` at line 47.
- **Zero occurrences** of `CREATE TABLE ... AS SELECT` (CTAS) anywhere in this file. CTAS is
  the documented SILVER wrap shape only (`retail-build-warehouse/SKILL.md`, Silver section);
  the Gold section documents explicit DDL + `INSERT` instead.

This directly confirms spec.md Clarification C5's correction: a rule literally matching
"`DROP TABLE IF EXISTS <dim>` IMMEDIATELY FOLLOWED BY `CREATE TABLE <dim> AS SELECT`" would
match NOTHING in this file -- it would fail OPEN on a real Type-2-declared-but-drop-and-rebuilt
dimension, defeating the feature's MVP purpose. The corrected signal (DROP + same-file CREATE
for the same table, in EITHER authored form, WITHOUT requiring textual adjacency) matches this
file's actual shape and is what FR-007 specifies. A CTAS-form fixture is still required
(User Story 2 Independent Test) as an additional case, since FR-007 permits either authored
form, even though CTAS does not appear in the one committed gold migration today.

### The name-to-table resolution (C4) is confirmed against the same file

`mappings/retail_store_sales/source-map.yaml` records each dimension's `name` fully
schema-qualified (`name: "gold.dim_customer_rss"`, `name: "gold.dim_product_rss"`, etc.),
matching the `gold.dim_customer_rss` / `gold.dim_product_rss` tokens in
`0004_create_gold_retail_store_sales_star.sql` VERBATIM. `mappings/demo_sample_orders/
source-map.yaml` and the canonical `templates/source-map.yaml` placeholder instead leave
`name` bare (`dim_product`, `dim_<entity_a>`), with no gold migration file existing yet for
that table. Stripping an optional leading `<schema>.` token from both the declared `name` and
the `DROP`/`CREATE` token, then comparing the bare identifier, holds exactly on the one
committed data point available (`retail_store_sales`) and degrades safely on
`demo_sample_orders` (no migration to compare against -- FR-008's not-yet-buildable path
applies, not a false comparison).

## Landing precondition (088's landing story is the OPPOSITE of HR1's -- load-bearing)

087/HR1 lands GREEN via an empty-but-present manifest scaffold (`dimensions: {}`), because
authoring an empty scaffold when there is nothing yet to adjudicate is not a Principle-V act.

**088/HR2 CANNOT land the same way.** Both committed maps' `gold_star.dimensions[]` entries
(four in `retail_store_sales`, at least one in `demo_sample_orders`) carry no `scd_type` key
today. Per FR-005, an absent `scd_type` is a fail-closed ERROR with no grandfather clause --
by design, so that adopting this feature does not silently default every existing map to
Type-1 by omission (the exact gap the feature exists to close). The consequence: **the
instant HR2 registers, `retail check` returns non-zero on the current tree** -- HR2 lands RED,
not green, and stays red until a human declares a real `scd_type` value
(`type_1` or `type_2`) on every dimension of every already-mapped table.

This is NOT something the agent may fix by scaffolding a placeholder value: filling in
`scd_type: type_1` on a human's behalf, even as a "safe default," is exactly the Principle-V
violation FR-011/FR-005 forbid (Assumptions: "The human authors the `scd_type` value
(BLOCKING, Principle V)"). Unlike HR1's empty-manifest scaffold (no judgment made), every
dimension here needs an actual per-dimension judgment call before it can go green.

Two things stay true independent of this landing cost, and must not be conflated:
- **Unit tests are unaffected.** `tests/fixtures/scd_history/**` fixtures are exempted by
  `is_test_path` (`src/retail/core.py`), so `pytest -m unit` on `tests/unit/test_rule_hr2.py`
  passes green regardless of the live tree's state -- fixtures construct their own
  RuleContext with synthetic tracked files.
- **`retail check` clean on the real committed tree is a SEPARATE, later fact**, gated on a
  human resolving the adoption-cliff Needs-decision findings this feature's landing produces.
  This plan does not attempt to pre-resolve those findings by writing `scd_type` values into
  `mappings/retail_store_sales/source-map.yaml` or `mappings/demo_sample_orders/source-map.yaml`
  -- that is future work for whichever human/PR chooses to adopt this feature's declaration on
  each already-mapped table, explicitly out of this plan's scope.

## Deferred capabilities NOT assumed

- **F016 Power BI execution adapter** (official Power BI MCP / connection; `pbi-cli` no
  longer preferred) is gated + LAST and is assumed NOT to exist. HR2 never invokes it.
- **Live DB / `retail validate`** SCD-2 data-correctness auditing (whether a MATERIALIZED
  Type-2 dimension actually preserves history correctly at the row level -- no duplicate
  current rows, `effective_to` gaps, correct `is_current` flags) is explicitly DEFERRED to a
  future `retail validate` extension (Principle VIII; Assumptions). HR2 checks the DECLARED
  policy against the AUTHORED migration TEXT only; it opens no database connection.
- **A positive recognition signal for a valid Type-2 construct** (so a correctly
  hand-authored history-preserving migration does not false-positive against FR-007) is
  future scope, deferred to whichever future feature adds Type-2 authoring to
  `retail-build-warehouse` (Clarification C3). No such construct exists in any committed
  migration today, so there is nothing to false-positive against yet.
- **Type-2 authoring itself** (teaching `retail-build-warehouse` to emit a genuine
  history-preserving upsert/merge/dated-row migration) is explicitly out of scope for this
  feature (Assumptions: "This feature does not teach `retail-build-warehouse` to author
  Type-2 SQL"). HR2 only detects the ABSENCE of any non-destructive construct; it never
  authors one.
- **A migration/backfill mechanism for a dimension changing declared type after gold already
  exists** is out of scope (Edge Cases); a type change is treated as an ordinary Mapping
  Ready map edit that re-triggers HR2 on the next `retail check`.
- No new readiness stage and no new `approvals[]` shape are assumed to exist; whether
  `scd_type` needs its OWN approval seam is OPEN (FR-017, Q-APPROVAL-SEAM) and not invented
  here.

## Open (Principle V -- NOT resolved here; carried to the owner)

- **Q-APPROVAL-SEAM (FR-017)**: whether declaring a dimension's `scd_type` requires its OWN
  named-human approval seam distinct from Mapping Ready's existing `approvals[]` entry, or
  folds into that same existing sign-off (no new approval record). This is a who-approves
  governance-shape ruling (Principle V) the agent MUST NOT settle. RECORDED PENDING DEFAULT
  the owner may ratify: FOLDS IN (one more field inside the same `source-map.yaml` a human
  already reviews and approves at Mapping Ready; no second approval record is invented until
  the owner rules one in). Until the owner rules, `scd_type` review happens inside the
  existing Mapping Ready approval and HR2 adds no new `approvals[]` stage key anywhere.
  (This is distinct from the landing-cost narrative above: FR-005's adoption-cliff severity
  choice is already a recorded, non-open default -- Q-APPROVAL-SEAM is the one thing left
  genuinely OPEN for a human ruling.)

## Decisions carried from Clarifications (Session 2026-07-04)

- **C1** (schema shape): `scd_type` nests directly under each existing
  `gold_star.dimensions[]` entry, alongside `surrogate_key` / `has_unknown_member` /
  `attributes[]` -- not a separate top-level list/map.
- **C2** (enum scope): exactly two values, `type_1` and `type_2` -- no fuller SCD taxonomy
  (Type-0/3/4/6) in scope.
- **C3** (detection signal): the MVP negative signal (drop-and-rebuild construct) is
  implementable NOW, confirmed against the one committed gold migration above; only a FUTURE
  positive-recognition signal is deferred, and only once Type-2 authoring exists.
- **C4** (name-to-table resolution): strip an optional leading `<schema>.` prefix from both
  the declared `name` and the `DROP`/`CREATE` token, then compare the bare identifier;
  confirmed exact on `retail_store_sales`, degrades safely on `demo_sample_orders`.
- **C5** (construct shape correction): the actual detected construct is a `DROP TABLE IF
  EXISTS <dim_table>` PLUS a same-file `CREATE TABLE <dim_table>` that recreates it, in
  EITHER authored form (CTAS or DDL-plus-`INSERT`), WITHOUT requiring textual adjacency --
  confirmed directly against `0004_create_gold_retail_store_sales_star.sql` above; the
  as-first-drafted "adjacent CTAS only" wording would have matched nothing in this repo's
  real gold output.
- **C6** (empty/placeholder value routing): an empty string, `null`, or a case-insensitive
  `"tbd"` value routes to FR-005's Needs-decision finding (same message/remedy as a wholly
  missing key), NOT FR-006's invalid-value finding -- because a placeholder is semantically
  an undeclared decision. FR-006 is reserved for a value that is present, non-empty, and not
  a recognized placeholder (e.g. a typo `"type1"` or an out-of-scope taxonomy value
  `"type_3"`). Both routes are already fail-closed ERROR; the choice changes only which
  finding message a reviewer sees, not the enforcement posture.
- **C7** (migration-file resolution + multi-match handling): `<table>` in the
  `warehouse/migrations/*create_gold_<table>_star.sql` glob resolves to that map's own
  mapping-directory name (confirmed exact against `retail_store_sales` above); the leading
  `*` absorbs the migration's arbitrary numeric filename prefix (`0004_`). If the glob
  matches MORE THAN ONE file for a table, HR2 emits a single fail-closed ERROR naming the
  table and every matched filename, rather than inspecting any one of them or guessing which
  is current -- an ambiguous migration set is itself a fail-closed condition, mirroring
  FR-008's no-fabrication stance for the zero-match case. No committed table has more than
  one matching migration today, so this default has nothing to contradict on the current
  tree.
