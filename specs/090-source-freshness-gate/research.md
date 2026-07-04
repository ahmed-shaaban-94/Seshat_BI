# Research: Source Freshness / Staleness Declaration and Static Presence Check (090)

Phase 0 -- precedent survey, input-source confirmation, and the deferred-capability
note. Every read below was of a committed artifact in this worktree; no live DB, no
Power BI/PBIP surface, no network was touched.

## Precedents (what SHIPPED to reuse, what to stay distinct from)

- **HR1 cross-star conformed-dimension gate** (`specs/087-conformed-dimension-readiness/`,
  reserved id HR1, not yet landed as code at the time of this research). This is the
  DIRECT DESIGN PRECEDENT for the "reserved id in the HR family, static rule reads
  committed YAML, fails closed on a proven problem, marks a mechanically-unready limb
  PENDING rather than guessing" shape. REUSE: (a) the `@register`-ed rule mechanism
  unchanged (`src/retail/core.py` `Finding`/`RuleContext`/`Severity`/`is_test_path`,
  `src/retail/registry.py` `register`); (b) the LAZY `import yaml` kept out of the
  `retail check` static-core chain; (c) the six-surface wiring lockstep
  (`src/retail/rules/__init__.py`, `tests/unit/test_rules_wiring.py`
  `EXPECTED_RULE_IDS`, `docs/rules/rules-manifest.json`,
  `docs/rules/severity-posture.json`, `docs/quality/rule-count-claims.yaml`,
  `docs/glossary.md`); (d) the "author the static structure, mark the
  mechanically-unready part PENDING, do not invent a substitute signal" discipline
  (087 did this for its grain limb; 090 does the analogous thing for the
  MANDATORY-vs-going-forward scope question, see below). STAY DISTINCT: HR1 reads
  MULTIPLE tables' `source-map.yaml` files plus a NEW cross-table manifest
  (`docs/quality/conformed-dimension-map.yaml`) to compare shapes ACROSS stars; HR4
  reads exactly ONE table's OWN `source-map.yaml` at a time and adds NO new manifest
  file -- it is a single-file presence/well-formedness check, structurally simpler.
  HR4 does not read `conformed-dimension-map.yaml` and does not touch `rule_hr1.py`.
  IMPORTANT DIVERGENCE from HR1's stance: HR1's research explicitly states it "adds
  NO new key to `source-map.yaml`" because that surface is shared/out-of-allocation
  for 087. This feature's allocation is the OPPOSITE: `meta.freshness` is 090's
  reserved key addition to `source-map.yaml` (per the collision-avoidance
  allocation in spec.md). The two features therefore touch the same file in
  different ways -- HR1 only READS `source-map.yaml`, 090 EDITS its schema (the
  template) and adds a rule that READS the new key. No key or rule id collides
  (090 owns `meta.freshness` + `HR4`; 087 owns `conformed-dimension-map.yaml` +
  `HR1`).

- **SF1 cross-layer checklist fork detector** (`src/retail/rules/rule_sf1.py`,
  spec 086, SHIPPED). Secondary precedent for the exact fail-closed shape on a
  malformed declared value (`Severity.ERROR` on an unrecognized token, never a
  silent pass) and for the `ctx.tracked_files`-only + `is_test_path` fixture
  exemption pattern. HR4 does not read `shared-spine.yaml` and does not edit
  `rule_sf1.py`.

- **`docs/readiness/source-drift.md`** (roadmap F014, design-only, "Later" tier,
  SHIPPED as docs). This is the nearest-sounding neighbour (see spec.md's
  "Boundary against neighbouring shipped work"). REUSE exactly one convention
  verbatim: the `[PENDING LIVE RE-PROFILE]` + non-`pass` marker pattern for "the
  live half of this concern is deferred, never fabricated" (source-drift.md line
  ~21, ~68). This feature's analogous marker is `[PENDING LIVE FRESHNESS CHECK]`
  (FR-006), reserved here as the CONTRACT a future live surface must honor. HR4
  itself never emits this marker (it never reports on live state at all -- C4).
  STAY DISTINCT: source-drift re-certifies SHAPE/SEMANTICS over time (columns,
  types, missingness, grain/PK, PII surface); this feature answers "did the data
  ARRIVE on time," an orthogonal question. No taxonomy, template, or key of
  source-drift is touched (FR-009).

- **`retail validate` / the live-validation surface** (spec 082, Postgres
  live-validation suite, SHIPPED as a capability separate from this feature).
  This is where the DEFERRED live comparison (declared `max_staleness` vs. an
  actual `MAX(<date column>)`) belongs eventually. This feature does not extend
  `retail validate`'s finding set (`src/retail/validate.py` is not touched) and
  opens no database connection anywhere in its own deliverables.

- **The source-mapping gate / `source-map.yaml`** (Principle IV, spec 001;
  template `templates/source-map.yaml`; filled instances
  `mappings/retail_store_sales/source-map.yaml`,
  `mappings/demo_sample_orders/source-map.yaml`; SHIPPED). This is the artifact
  090 EXTENDS (schema) and HR4 READS (per-table, read-only). See "Input-source
  confirmation" below for the exact edit boundary.

- **The wiring meta-gate + rule-count lockstep** (`tests/unit/test_wiring_meta_gate.py`,
  `tests/unit/test_rules_wiring.py` `EXPECTED_RULE_IDS`,
  `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
  `docs/quality/rule-count-claims.yaml`, `docs/glossary.md`; SHIPPED). Adding one
  `@register`-ed rule REQUIRES the same six-surface update in the same commit.
  REUSE the discipline exactly (see plan.md Project Structure).

## Input-source confirmation (what HR4 reads and edits on disk)

| Surface | Confirmed on-disk state (read 2026-07-04) | This feature's action |
|---|---|---|
| `templates/source-map.yaml` | 260-line generic template; `meta:` block currently has `table_id`, `source_system`, `profiled_from`, `grain`, `primary_key`, `reviewed_by`, `reviewed_on`. No `freshness` key today. | EDIT: add a `meta.freshness` placeholder block (schema documentation only, generic placeholder values per Principle VII) as a sibling of the existing `meta` keys. HR4 MUST NOT fire on this file (C3, FR-011) -- confirmed by the same "template is schema, not an instance" convention HR1's precedent already established for `source-map.yaml` template vs. filled maps. |
| `mappings/retail_store_sales/source-map.yaml` | Filled instance; `meta:` block has `table_id`, `source_system`, `profiled_from`, `grain`, `primary_key`, `reviewed_by: "data_owner"`, `reviewed_on: "2026-06-25"`. No `freshness` key today. | UNCHANGED, READ-ONLY. This feature does NOT populate this file with a real `expected_cadence`/`max_staleness` value -- that is a business-SLA judgment only the table's data owner can supply (FR-002, hard rule #9: no fabricated freshness), and whether it is even REQUIRED on this pre-existing map is the OPEN Q-FR014-SCOPE ruling. HR4 is authored to be presence-gated (see "Landing precondition" below) so this file produces zero Findings until a human either adds the block or FR-014 is ruled. |
| `mappings/demo_sample_orders/source-map.yaml` | Filled instance; compact `meta:` shape, no `freshness` key today. | UNCHANGED, READ-ONLY, same reasoning as above. |
| Rule mechanism | `@register` / `RuleContext` / `Finding` / `Severity` / `is_test_path` in `src/retail/core.py` (`is_test_path` = `path.startswith("tests/")`) + `src/retail/registry.py`. | REUSED unchanged; nothing new at the mechanism layer. |
| Registered rule count | `docs/rules/rules-manifest.json` is a JSON list of `{"id", "title"}`; `len(...) == 55` today (verified: `json.load` returns a 55-element list). `docs/glossary.md` line ~101 states "Currently 55 rules in 21 families" (families: S, D, C, R, RS, G, P, A, B, PP, SC, DF, SL, AL, AD, AQ, DL, CT, DR, AP, SF -- no `HR` family listed yet in the committed glossary at research time). | HR4 lands as rule 56 IF it lands before any other in-flight rule-adding feature (e.g. 087/HR1); the exact number and whether "21" becomes "22 families (adds HR)" or stays "22" (if HR1 already added the family) MUST be re-verified against the live manifest at implement time, not hardcoded from this research snapshot (same caution 087's plan records for its own count). |

### Landing precondition -- how HR4 lands GREEN on the current tree

Neither committed filled map (`retail_store_sales`, `demo_sample_orders`) carries a
`meta.freshness` block today. If HR4's fail-closed ERROR fired on ABSENCE for every
filled map unconditionally, `retail check` would flip both currently-`pass`-adjacent
tables red the instant HR4 registers -- landing RED, which is exactly the 086/087
"no manifest = no green landing" risk, and here it would also silently PRE-EMPT the
still-OPEN Q-FR014-SCOPE ruling (Principle V: the agent may not decide "mandatory
everywhere, including retroactively" on its own).

Resolution carried into plan.md: HR4 ships PRESENCE-GATED. It fails closed on a
`meta.freshness` block that IS PRESENT but malformed (missing/blank/unparseable
sub-key) -- this is real, uncontroversial Principle-I enforcement of FR-002's
well-formedness contract, and it fires on ZERO tables today (neither committed map
has the block, so there is nothing malformed to flag). It does NOT fire on a
FILLED MAP with NO `meta.freshness` block at all -- that is exactly the "which
tables must carry the block" question FR-014 reserves for a named human. This
keeps `retail check` GREEN on the current tree (SC-001/SC-003 both hold trivially:
zero blocks present -> zero malformed, zero pre-mapping tables checked) while still
giving User Story 2's malformed-block acceptance scenarios a real, exercisable
fail-closed path today (via test fixtures, mirroring how 087's undeclared-collision
path was real but inert on the current tree because the two committed stars share
no dimension name).

**Honesty limitation (recorded, not designed around, mirrors 087's own honesty
note):** presence-gating can be trivially bypassed by never adding the block at
all -- a table that omits `meta.freshness` entirely produces no Finding, exactly
like a table that has never been asked the question. This is NOT a loophole this
feature quietly accepts as a permanent design; it is the explicit, visible seam
where FR-014's ruling plugs in. Making the block MANDATORY (absence itself an
ERROR, for some or all tables) is a governance-shape decision this spec defers to
the owner (Q-FR014-SCOPE) precisely because it would otherwise (a) force the
agent to fabricate an SLA value on an existing table's behalf to make it "pass",
or (b) flip an already-`pass` table's readiness picture red without a named human
choosing that outcome. Until ruled, "no block = no Finding" is the only
constitution-safe default (Principle VI/VIII: author the static structure now,
defer the part that requires a human ruling and/or a live-adjacent rollout
decision -- here the "rollout scope" plays the role 087's "grain-limb schema
prerequisite" played: a real, named, un-invented gap, not a silently-skipped one).

## The token grammar is a Phase-1 deliverable, not deferred further

Clarification C1 defers the exact `expected_cadence`/`max_staleness` token grammar
to plan (not to implementation), so this stage must commit to it. See
`data-model.md` for the concrete, generic (Principle VII), small vocabulary. It is
recorded here as a research finding, not invented ad hoc: the SHAPE (a closed
cadence enum plus a magnitude+unit duration grammar, with a reserved
`one_time`/`static` sentinel per C2) is the smallest vocabulary that (a) makes
"unparseable" a well-defined, fail-closed-able test (Principle I cannot rest on an
undefined predicate), (b) stays generic and inlines no C086/`retail_store_sales`
value (FR-011), and (c) is permissive enough that a legitimate phrasing is not
false-positived into an ERROR (C1's explicit caution).

## Deferred capabilities NOT assumed

- **F016 Power BI execution adapter** (official Power BI MCP / connection;
  `pbi-cli` no longer preferred) is gated + LAST and is assumed NOT to exist. HR4
  never invokes it.
- **Live DB / `retail validate` freshness comparison** (actually querying
  `MAX(<date column>)` against a live connection and comparing it to the declared
  `max_staleness`) is DEFERRED (Principle VIII, FR-006). HR4 opens no database
  connection and reads no live Power BI/PBIP surface; the `[PENDING LIVE
  FRESHNESS CHECK]` marker is recorded as a future surface's contract, not
  implemented here (this feature adds no live-reporting surface of its own, C4).
- **HR1 / `docs/quality/conformed-dimension-map.yaml`** (spec 087) is a
  sibling reserved id/feature in the same `HR*` family; this feature does not
  assume HR1 has landed and does not read its manifest or rule module. If HR1
  lands first, the wiring surfaces (rule count, family list) simply already
  reflect it and this feature's implement-time count re-verification accounts
  for that; if HR4 lands first, HR1's future plan re-verifies against HR4's
  count instead. Neither feature depends on the other's registration order.
- **A mandatory-everywhere freshness requirement** (FR-014's eventual ruling) is
  NOT assumed. This feature does not decide, default, or simulate that ruling; it
  ships the presence-gated static structure described above and leaves the
  absence-triggers-ERROR question to the owner.
- **Missing-segment / date-spine completeness detection** (the other half of
  PB-SQL-09) is OUT OF SCOPE and not touched (FR-010).

## Open (Principle V -- NOT resolved here; carried to the owner)

- **Q-FR014-SCOPE (FR-014)**: whether `meta.freshness` is mandatory on every
  existing and future `source-map.yaml` (making HR4 fire retroactively, including
  on the committed `retail_store_sales` worked example) or applies only to
  newly-authored/re-touched maps going forward, with pre-existing maps
  grandfathered; and whether a genuinely one-time/static source gets the
  `one_time`/`static` opt-out token (C2) or a full HR4 exemption. RECORDED
  PENDING DEFAULT the owner may ratify (from spec.md Clarifications): GOING-
  FORWARD ONLY, existing maps grandfathered until next material edit, one-time
  sources use the reserved token rather than a blanket exemption. This research
  does not adopt that default as a ruling; plan.md's presence-gated design is
  chosen precisely because it requires NO ruling to land safely either way (it
  neither forecloses "mandatory everywhere" nor "going-forward only" -- both
  remain implementable as a later, separate change to HR4's absence-handling
  once the owner rules, without re-touching the well-formedness limb shipped
  now).
