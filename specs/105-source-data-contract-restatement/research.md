# Phase 0 Research: Source Data-Contract -- Forward Schema + Arrival + Restatement (HR12)

Phase 0 -- precedent survey, input-source confirmation, and the deferred-capability
note. Every read below was of a committed artifact in this worktree; no live DB, no
Power BI/PBIP surface, no network was touched.

## Precedents (what SHIPPED to reuse, what to stay distinct from)

- **The HR-series static rule precedent, esp. 093/HR7 (reload-idempotency-readiness;
  `specs/093-reload-idempotency-readiness/`) -- NOT YET MERGED to `src/retail/rules/`
  as of this feature's authoring (confirmed by an empty `src/retail/rules/**/HR7*`
  glob), but its four-document design set is the DIRECT STRUCTURAL PRECEDENT for this
  plan: a declare-then-check static rule, a NEW per-table declaration artifact, a
  default-free-pass posture, and the seven-surface wiring discipline. REUSE the shape
  of: (a) a closed set of named sections a rule checks for presence/well-formedness,
  never for semantic quality; (b) an opt-in-by-file-existence posture (090/HR4,
  093/HR7's own "declare or default"); (c) the seven wiring surfaces (rule module,
  `__init__.py`, `test_rules_wiring.py`, `rules-manifest.json`,
  `severity-posture.json`, `docs/glossary.md`, `rule-count-claims.yaml`); (d) an OPEN
  Principle-V Clarifications entry carried forward with a named, non-authoritative
  interim default (093's Q-APPROVAL-SEAM / FR-013 is the direct mirror of this
  feature's own FR-013). STAY DISTINCT: HR7 checks a SINGLE-TABLE reload-mechanism
  declaration read from SQL text (`warehouse/migrations/*.sql` +
  `warehouse/load-policy.md`); HR12 checks a SINGLE-TABLE forward SUPPLIER-FACING
  contract read from a YAML file (`mappings/<table>/source-data-contract.yaml`).
  Different concern, different id, different input format (SQL vs YAML), different
  directory. HR12 reads or writes nothing HR7 owns, and HR7 reads or writes nothing
  HR12 owns.

- **AL2 assumption-coherence (`src/retail/rules/assumption_coherence.py`, rule id
  AL2).** SHIPPED (hand-built; see that module's own provenance note -- not
  spec-driven, but the CODE is real and running today). This is the DIRECT READ-PATH
  PRECEDENT for HR12, not the SQL-token family: AL2 scans a per-table YAML corpus
  under `mappings/*/<subpath>/*.yaml` via a compiled path regex
  (`^mappings/[^/]+/metrics/[^/]+\.ya?ml$`), excludes the generic template path
  constant (`_TEMPLATE_PATH = "templates/metric-contract.yaml"`) and any
  `is_test_path(rel)` fixture, and does a LAZY `import yaml` INSIDE the rule
  function/module (not at package `__init__` import time) so the shared
  `retail.rules` package import stays stdlib-only.

- **SF1 cross-layer checklist fork detector (`src/retail/rules/rule_sf1.py`, rule id
  SF1).** SHIPPED (spec 086, idea I3). This is the DIRECT PRECEDENT for HR12's
  malformed-YAML branch (spec Clarifications Q6, FR-002): SF1's own manifest read
  wraps `yaml.safe_load` in `except (OSError, yaml.YAMLError) as exc` and returns a
  single `Severity.ERROR` Finding naming the FILE ITSELF (not a sub-key), rather than
  letting the exception escape or silently treating the file as absent. HR12 REUSES
  this exact shape for a present-but-unparseable
  `mappings/<table>/source-data-contract.yaml`: one ERROR Finding, `locator` = the
  contract's path, message names the file, never a section (since none could be
  parsed). REUSE this exact shape for HR12:
  a compiled path regex `^mappings/[^/]+/source-data-contract\.ya?ml$`, a
  `_TEMPLATE_PATH = "templates/source-data-contract.yaml"` exclusion constant, an
  `is_test_path(rel)` exclusion, and a lazy `import yaml` inside the handler. AL2 also
  demonstrates the placeholder-vs-real-value STRUCTURAL (non-semantic) detection
  pattern this feature's FR-006 requires, though AL2's own placeholder shape
  (`_PLACEHOLDER_RE = re.compile(r"<[^>]*>")`, an angle-bracket scan) is a SIBLING
  pattern, not identical: FR-006 requires HR12's own template to ship a distinctive
  sentinel TOKEN (e.g. `REPLACE_ME`-style), not a bare angle-bracket placeholder, per
  the spec's Q2 resolution -- HR12 does its own exact-token match, reusing only AL2's
  overall structural-comparison DISCIPLINE (never a semantic judgment on a filled
  value), not its specific regex.

- **Source Ready (Stage 1)** (`docs/readiness/source-ready.md`; no `retail check` /
  `retail validate` gate exists at this stage today -- the doc states plainly "This
  stage has no `retail check` / `retail validate` gate. The gate is a review.").
  SHIPPED. HR12 is the FIRST static `retail check` rule to attach EVIDENCE at Source
  Ready; it does not replace the stage's existing review-based gate (the profile
  numbers + PROPOSED semantics still require human confirmation exactly as today),
  and it does not change `source-ready.md`'s Required-artifacts table (the profile
  remains the ONLY required artifact; `source-data-contract.yaml` is an ADDITIONAL,
  independent, opt-in artifact, per FR-010/spec Boundary section). `source-ready.md`
  gets one new doc row describing HR12 as an optional, evidence-only static check;
  the stage's actual `pass`/`blocked`/`warning` decision procedure (human review) is
  unchanged.

- **The 090/HR4 (`meta.freshness` in `source-map.yaml`), 089/HR3 (`stale_pass`), and
  093/HR7 (`load-policy.md`) siblings** -- all Draft, same dated batch, confirmed by
  direct read of each spec's own Boundary/FR sections (090 spec FR-related freshness
  key; 089 spec `stale_pass` blocker shape; 093 spec's own load-policy shape). Per
  this feature's own spec Boundary section, all three are RESERVED, DISTINCT
  neighbours: HR12 reads only `mappings/<table>/source-data-contract.yaml`; it never
  reads or writes `source-map.yaml` (090/HR4's key lives there), never reads
  `readiness-status.yaml` or raises a `stale_pass` blocker (089/HR3's concern), and
  never restates or duplicates 093/HR7's load-idempotency check even where the
  restatement policy text cites it by reference (FR-012).

- **The source-mapping gate itself** (`templates/source-map.yaml`, Principle IV,
  spec 001). SHIPPED. Confirmed by direct read: the current template's "SISTER
  ARTIFACTS IN THE MAPPING GATE" comment block lists exactly five sister artifacts
  (`source-profile.md`, `source-map.yaml`, `assumptions.md`,
  `unresolved-questions.md`, `reconciliation-report.md`) as the mapping gate's
  required set. `templates/source-data-contract.yaml` is added as a NEW, sixth,
  INDEPENDENT template -- it is never added to that sister-artifact list and never
  becomes a required Mapping-Ready artifact (FR-010); the Mapping Ready gate's
  required-artifact count and list are untouched by this feature.

- **The wiring meta-gate + rule-count lockstep** (`src/retail/rules/g6.py`,
  `tests/unit/test_wiring_meta_gate.py`, `tests/unit/test_rules_wiring.py`
  [`EXPECTED_RULE_IDS`], `tests/unit/test_glossary_rule_table.py`,
  `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
  `docs/quality/rule-count-claims.yaml`, `docs/glossary.md`). SHIPPED. Confirmed by
  direct read: `docs/rules/rules-manifest.json` holds 55 entries and
  `docs/rules/severity-posture.json`'s `registered` map holds 55 keys at research
  time, neither containing an `HR12`, `HR7`, `HR3`, or `HR4` entry yet (all four
  sibling HR-rules remain unregistered Draft specs as of this reading, matching
  093/HR7's own research.md note that "089/090/093/105 are parallel drafts each
  claiming a next id"). Adding one `@register`ed rule REQUIRES all seven surfaces to
  move in the SAME commit at implement time; the BUILD must re-read the live count
  rather than hardcode "56th."

- **The severity-vs-stage-blocking mechanism** (`src/retail/rules/sql.py`'s S6/S7
  `Severity.WARNING` findings vs S8's `Severity.ERROR`; `src/retail/rules/
  readiness_status.py`'s `blocking_reasons[]` handling). SHIPPED. Confirmed by direct
  read: a rule's `Severity` (ERROR/WARNING) governs whether `retail check` itself
  reports that FINDING as a failure -- it does NOT, by itself, wire that finding into
  any table's `readiness-status.yaml` `blocking_reasons[]` list. That wiring is a
  SEPARATE, human-authored decision recorded in the per-table `readiness-status.yaml`
  file (`readiness_status.py`'s own rule reads `blocking_reasons[]` as authored data,
  it does not compute it from arbitrary rule findings). This is the resolving
  mechanism for FR-013: HR12 can fail closed as a CHECK (never silently pass an
  incomplete, opted-in contract -- satisfying User Story 2 from day one) while the
  separate question of whether that failure is wired into the Source Ready STAGE
  VERDICT's `blocking_reasons[]` remains the genuinely open, unresolved
  Principle-V question FR-013 describes. The two are different layers (rule-level
  Finding vs stage-level blocking_reasons), exactly as 093/HR7's own research.md
  distinguishes "an ERROR Finding" from "contributing to a self-granted Gold Ready
  pass."

## Input-source confirmation (what HR12 reads on disk)

| Input | Confirmed on-disk source | Notes |
|-------|--------------------------|-------|
| Per-table contract corpus | `mappings/<table>/source-data-contract.yaml` (via `ctx.tracked_files`, filtered by the compiled path regex `^mappings/[^/]+/source-data-contract\.ya?ml$`) | tracked files only, mirrors AL2's `_METRICS_RE` pattern and 093/HR7's `ctx.tracked_files`-only load-policy read discipline (Principle IX reproducibility: an untracked local copy must not influence the gate) |
| Template exclusion | `templates/source-data-contract.yaml` (a `_TEMPLATE_PATH` constant, excluded from the scan exactly like AL2 excludes `templates/metric-contract.yaml`) | the template ships ALL sentinel placeholders by design; if HR12 scanned it as a table contract it would self-flag every section as incomplete |
| Fixture exclusion | any path under a test-fixture root, via the existing `is_test_path(rel)` helper (`src/retail/core.py`) | mirrors every other rule's fixture exemption |
| Section values | the three required top-level YAML sections (`schema`, `arrival`, `restatement`) and their sub-fields, parsed via a LAZY `import yaml` inside the rule module/handler (never at `retail.rules` package import time) | mirrors AL2's own lazy-import discipline; keeps the shared rules package stdlib-only at import time (constitution Principle I/VIII wording: "stdlib-only at import") |
| Placeholder sentinel | a distinctive, greppable token shipped in every required field of `templates/source-data-contract.yaml` (FR-006/spec Q2 resolution, e.g. a `REPLACE_ME`-style string, one per section) | HR12 does an exact-match structural comparison against this literal token; no regex-based angle-bracket heuristic (distinct from AL2's own placeholder regex, which is a sibling pattern, not reused verbatim) |
| Rule mechanism | `@register` / `RuleContext` / `Finding` / `Severity` / `is_test_path` in `src/retail/core.py` + `src/retail/registry.py` | reused unchanged; nothing new at the mechanism layer |

### Confirmed: no live source-data-contract.yaml exists on the tree today

A glob of `mappings/**/source-data-contract.yaml` at research time returns zero
matches: `mappings/retail_store_sales/` and `mappings/demo_sample_orders/` each
carry the existing five-artifact mapping set (`source-map.yaml`,
`source-profile.md`, `assumptions.md` / equivalents, `reconciliation-report.md`,
`unresolved-questions.md`) plus their own `readiness-status.yaml`, `design/`,
`handoff/`, `metrics/` -- but no `source-data-contract.yaml` for either table. This
confirms the LANDING case below and is the direct input-source proof for SC-003 (a
table with no contract is not-applicable, not penalized).

## Landing analysis (green by construction, mirrors 093/HR7's own green landing --
the opposite of 087/HR1's red landing)

Because zero tables on the current tree carry a `source-data-contract.yaml`, and
because HR12's presence check is opt-in (FR-002: the file's ABSENCE is never a
Finding), HR12 registers and evaluates to NOT-APPLICABLE (no Finding at all) for
every currently mapped table with ZERO edits required to any existing artifact. This
is the direct analogue of 093/HR7's "green, not red" landing note. Per Principle V
(FR-005), this feature MUST NOT invent a filled instance to force a demonstration
pass -- fabricating `mappings/retail_store_sales/source-data-contract.yaml`'s actual
schema/cadence/restatement VALUES would require inventing owner-supplied facts about
a real upstream system that were never gathered. The SAFE landing is therefore:

- `templates/source-data-contract.yaml` is CREATED by this feature (FR-001 mandates
  the template itself, unlike 093/HR7's `load-policy.md`, which was documented but
  never created because nothing needed it yet -- this feature's template is a
  concrete FR-001 deliverable regardless of whether any table has filled a copy).
- NO `mappings/<table>/source-data-contract.yaml` is authored for any real table by
  this feature. Test coverage for the fail-closed / pass paths (User Stories 1-3) is
  authored EXCLUSIVELY as unit-test fixtures under a test-fixture root recognized by
  `is_test_path()`, never as a real table's committed contract.
- SC-001 ("a table that fills the contract with real values passes HR12") is
  demonstrated by a FIXTURE, not by fabricating `retail_store_sales`'s or
  `demo_sample_orders`'s actual real-world contract facts.

## Wiring points and target count (mirrors 093/HR7's R4-derived seven-surface set)

Reading the CURRENT `tests/unit/test_wiring_meta_gate.py` (the authoritative
lockstep gate, feature 061) confirms the same seven surfaces 093/HR7 already
enumerated remain current and unchanged for HR12:

1. **Rule module** under `src/retail/rules/` (the new `HR12` `@register`), e.g.
   `source_data_contract.py`.
2. **`src/retail/rules/__init__.py`** -- add the module to the side-effecting import
   block AND to `__all__` (C1 package-symmetry).
3. **`tests/unit/test_rules_wiring.py`** -- add `HR12` to `EXPECTED_RULE_IDS` (C2).
4. **`docs/rules/rules-manifest.json`** -- add `{id: "HR12", title: "..."}` (C3).
5. **`docs/rules/severity-posture.json`** -- add `HR12` under `registered` with its
   severity (C4).
6. **`docs/glossary.md`** -- add an `HR12` row to the "Static check rules" table
   (glossary-rule-table bijection test).
7. **`docs/quality/rule-count-claims.yaml`** -- reconcile any prose "N rules" claim.

Current authoritative count (read live, not hardcoded): 55 entries in
`docs/rules/rules-manifest.json` at research time; the BUILD must re-read the live
count at implement time rather than hardcode a number, because 089/090/093 are
parallel drafts each contending for "the next id" in the same dated batch.

## Deferred capabilities NOT assumed

- **F016 Power BI execution adapter** (official Power BI MCP / connection; `pbi-cli`
  no longer preferred) is gated + LAST and is assumed NOT to exist. HR12 never
  invokes it, directly or indirectly.
- **Live DB / `retail validate`** proof that a declared arrival cadence matches an
  actual live `MAX(<date column>)`, or that an actual restatement event occurred on
  live data, is explicitly DEFERRED to a future `retail validate` extension
  (Principle VIII, FR-003). HR12 opens no database connection, computes no live
  signal, and needs no DSN or the `db` extra.
- **A live drift comparison** between the contract's declared schema and
  `source-map.yaml` / the latest profile is explicitly out of scope (per the spec's
  own Edge Cases and Boundary section); this feature does not edit
  `docs/readiness/source-drift.md`, its taxonomy, or any future
  `source-drift-report.md` template, and does not fold restatement into the
  nine-class drift taxonomy.
- **Cross-artifact reconciliation** between this feature's arrival section and
  090/HR4's `meta.freshness` key is explicitly out of scope; HR12 does not read
  `source-map.yaml` at all, and does not detect or flag disagreement between the two
  declarations (spec Edge Cases).
- **The FR-013 enforcement-strength question** (whether an opted-in, later-broken
  contract can block the Source Ready stage's `pass` verdict) is NOT resolved here.
  It is carried forward as a genuinely OPEN Principle-V Clarifications item with a
  named, non-authoritative interim stance (HR12 emits its own Finding but nothing
  wires that Finding into any table's `readiness-status.yaml` `blocking_reasons[]`
  by default) -- exactly mirroring 093/HR7's own Q-APPROVAL-SEAM treatment.
- No new readiness stage, no new key in `source-map.yaml`, and no change to the
  Mapping Ready gate's five-artifact list are assumed or added.

## Open (Principle V -- NOT resolved here; carried to the owner)

- **Q-ENFORCEMENT-STRENGTH (FR-013)**: whether HR12's Finding on a present-but-broken
  contract should be wired into a table's `readiness-status.yaml`
  `blocking_reasons[]` (making Source Ready `pass` block on it), or whether it stays
  purely evidence-level (the rule's own pass/fail/not-applicable result, visible in
  `retail check` output, but never itself wired into any stage-verdict
  `blocking_reasons[]`). RECORDED PENDING DEFAULT an owner may ratify: EVIDENCE-ONLY
  -- HR12 never contributes to a stage's `blocking_reasons[]` until an owner rules
  one in via the approval-console workflow. This mirrors 093/HR7's own
  Q-APPROVAL-SEAM pending-default treatment and 090/HR4 FR-014's identically-shaped
  open question in the same dated batch.
