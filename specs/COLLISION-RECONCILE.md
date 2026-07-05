# Cross-Feature Collision Reconcile — specs 087–105 (19 features)

**Reviewer role:** READ-ONLY pre-implementation integration check.
**Verdict:** **CLEAN** — items 1–4 are all empty. The pre-assigned collision-avoidance
allocation holds for real. Safe to implement (with the shared-file serialization below).

**Method:** authoritative rule set read from `tests/unit/test_rules_wiring.py`
(`EXPECTED_RULE_IDS`); every `@register("...")` literal across the 19 dirs enumerated and
mapped to its dir; schema-key adders traced in each `data-model.md`; new-file paths extracted
from `plan.md` / `tasks.md` / `data-model.md` and each classified new-vs-existing.

---

## 1. Duplicate rule-ids — NONE

Discriminating sweep: `grep -rloE '@register("HRx"' ` per id → each HR-id literal appears in
**exactly one** dir. The allocation matches the expected mapping exactly:

| Spec | Declared id (`@register`) | Rule module | Expected | Match |
|------|---------------------------|-------------|----------|-------|
| 087 | HR1  | `rule_hr1.py` | HR1 | ✓ |
| 088 | HR2  | `rule_hr2.py` | HR2 | ✓ |
| 089 | HR3  | `rule_hr3.py` | HR3 | ✓ |
| 090 | HR4  | `rule_hr4.py` | HR4 | ✓ |
| 091 | HR5  | `snapshot_time_additivity.py` | HR5 | ✓ |
| 092 | HR6  | `hr6.py` | HR6 | ✓ |
| 093 | HR7  | `reload_idempotency.py` | HR7 | ✓ |
| 094 | HR8  | inside existing `sql.py` | HR8 | ✓ |
| 104 | HR9  | `rename_impact_guard.py` | HR9 | ✓ |
| 103 | HR11 | `hr11.py` | HR11 | ✓ |
| 105 | HR12 | `source_data_contract.py` | HR12 | ✓ |

Non-adders (add **no** rule, confirmed in each spec's prose): 095, 096, 097, 098, 099, 100, 101, **102**.

**HR10 is intentionally DECLINED by 102**, not a missing allocation. 102 reasoned that a
second contrast/a11y static rule would duplicate the existing CT1 rule and add no new coverage;
it enforces its checklist via the existing human `dashboard_ready` design-review gate instead.
HR10 therefore has zero `@register` literals anywhere — this is correct, not a gap.

Cross-references that are NOT claims (verified as prose / template placeholders, not registrations):
088 mentions HR1; 089/093/094/105 mention sibling HR-ids in "additive: changes no existing rule"
notes; 103 cites "mirrors 092/HR6's pattern" and "mirrors AL1"; 104 says "do not copy HR1's shape";
091 cites `@register("AL1", ...)` (existing rule); 092 cites `@register("G6", ...)` (existing rule);
091/092/103 show `@register("<ID>"/"ID", ...)` template placeholders. None registers a duplicate id.

## 2. rule-ids vs the already-registered set — NO COLLISION

`EXPECTED_RULE_IDS` today contains **no HR-id** (full set enumerated in item 5). All eleven new
ids (HR1–HR9, HR11, HR12) fall in the reserved HR namespace and collide with none of the
currently-registered ids. No spec introduces a non-HR rule id.

## 3. Schema-key conflicts — NONE

Every adder stays inside its assigned slot; no two specs touch the same key.

**source-map.yaml:**
- 088 → `gold_star.dimensions[].scd_type` (nested per-dimension) ✓
- 090 → `meta.freshness` (sibling of `meta.grain`/`meta.primary_key`) ✓
- 103 → `columns[].unit` and `columns[].currency` (per-column, optional) ✓

**metric-contract.yaml:**
- 091 → `time_additivity` (top-level, optional) ✓
- 103 → top-level `unit` (documentary) ✓

**Separate contract files (not metric-contract keys):**
- 092 → `templates/rls-role-contract.yaml` (NEW, its own file) ✓
- 105 → `templates/source-data-contract.yaml` (NEW, its own file) ✓

**Explicit negative confirmations:** No spec outside {088, 090, 103} adds a source-map.yaml key,
and none outside {091, 103} adds a metric-contract.yaml key. 096/097/098 reference those templates
but add no new field ("no new field / no new vocabulary" per their own plans).

## 4. New-file path conflicts — NONE

Each newly-created file is claimed by exactly one spec:

- **Rule modules** (all distinct): `rule_hr1.py`, `rule_hr2.py`, `rule_hr3.py`, `rule_hr4.py`,
  `snapshot_time_additivity.py`(091), `hr6.py`(092), `reload_idempotency.py`(093),
  `rename_impact_guard.py`(104), `hr11.py`(103), `source_data_contract.py`(105),
  `design_contrast.py`(102). (094 edits existing `sql.py`; not a new file.)
- **New pattern docs** (distinct): 095 `docs/patterns/target-budget-fact.md`;
  097 `docs/patterns/promotion-markdown-factless.md`;
  098 `docs/patterns/customer-dimension-pattern.md` + `customer-grain-pattern.md`.
- **New templates** (distinct): 095 `metric-contract-shape.variance-vs-target.yaml`;
  097 `factless-fact.yaml`; 098 `templates/customer-dimension.md`;
  092 `rls-role-contract.yaml`; 105 `source-data-contract.yaml`.
- **New per-rule test files** (distinct): `test_rule_hr1..4.py`, `test_hr6.py`, `test_hr11.py`,
  `test_reload_idempotency.py`, `test_rename_impact_guard.py`, `test_snapshot_time_additivity.py`,
  `test_source_data_contract.py`.

Overlaps observed are all **edits to EXISTING files** (verified on disk), which are serialized,
not new-file conflicts — see item 4-note below.

## 5. EXPECTED_RULE_IDS room — CONFIRMED FREE

`tests/unit/test_rules_wiring.py` `EXPECTED_RULE_IDS` currently holds (no HR-id present):
AP1, SF1, DR1, S1, S2, S3, S4a, S4b, S5, S6, S7, S8, D1–D11, R1, RS1, A1, A3, B1, B3, C1, C2,
G1–G6, P1, P2, PP1, SC1, SC2, DF1, SL1, AL1, AL2, DL1–DL6, CT1, AD1, AQ1.
All twelve HR slots (HR1–HR12) are free to add. (Note: the live set includes S4a/S4b/S4 not in
the task's "56" enumeration, but that does not affect HR reservation.)

## 6. Build-order notes

**HARD constraint — shared-file co-edits must be serialized** (each is an edit to a single
existing file; concurrent adders will conflict on line-level edits and on the count bump):
- The ~11 rule-adders each edit: `src/retail/rules/__init__.py`, `tests/unit/test_rules_wiring.py`
  (`EXPECTED_RULE_IDS` + count), `docs/rules/severity-posture.json`, `docs/rules/rules-manifest.json`,
  `docs/glossary.md` rules table, `tests/unit/test_wiring_meta_gate.py`,
  `tests/unit/test_rule_count_claims.py`. Serialize; each PR rebases the live count.
- Existing rule-module co-edits: `assumptions.py` (091 + 103), `readiness_status.py` (092 + 103).
- Existing template co-edits: `source-map.yaml` (088, 090, 103), `metric-contract.yaml` (091, 103).
- Existing doc co-edits: `docs/worked-examples/retail-store-sales.md` (095, 096, 097),
  `docs/architecture/product-modules.md` (099, 101), `docs/roadmap/roadmap.md` (multiple),
  `mappings/retail_store_sales/design/visual-contract-binding-map.md` (102, 103, 104).

**SOFT constraint — recommended ordering (prose references, NOT hard consumes; not blockers):**
- 096 and 098 defer conformed-dimension identity questions to 087/HR1 (prose only; 096 explicitly
  notes `docs/quality/conformed-dimension-map.yaml` does not yet exist and 087 is spec-only).
  Build 087 first if the conformed-dim concept is to be cited concretely.
- 101 cites 099's lineage precedent (prose); build 099 first if 101 links to lineage docs.
- 104 (HR9 rename-impact guard) reads `binds_to.columns` and the new `columns[].unit`/`currency`
  and metric-contract fields; it reconciles across 087/092/099/103/105 surfaces → best built LAST,
  after the schema-adders (088, 090, 091, 103) land so its scan corpus is stable.
- 089 (readiness decay) and 105 (source-data-contract) are thematically related (both touch
  source-freshness / source-ready); no hard dependency, additive to each other.
