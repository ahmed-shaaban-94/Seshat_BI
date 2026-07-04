# Quickstart: Source Data-Contract -- Forward Schema + Arrival + Restatement (HR12)

## Run the rule as part of the retail check

HR12 runs automatically inside the existing `retail check` governance command (the
same command already wired into the pre-commit path and CI). No new command is
introduced. On the current committed tree, zero tables carry a
`source-data-contract.yaml` yet (research.md's confirmed input-source reading), so
HR12 produces ZERO Findings out of the box -- the contract is opt-in and no table is
penalized for not having authored one.

```bash
retail check
```

## Confirm the opt-in default stays free (no table penalized for omitting a contract)

1. Run `retail check` against the repo as committed today.
2. Confirm HR12 emits no Finding for `retail_store_sales` or `demo_sample_orders`
   (neither has a `source-data-contract.yaml` today) and that neither table's
   Source Ready evidence changes as a result (SC-003).

## Declare a forward contract for a table (analyst workflow)

1. Copy `templates/source-data-contract.yaml` to
   `mappings/<table>/source-data-contract.yaml`.
2. Fill the three required sections with REAL, owner-supplied facts about the
   actual upstream system -- never invented or assumed by an agent (Principle V,
   FR-005):
   - `schema`: every column the supplier has committed to deliver, each with both
     a `name` and a `type` (an entry with a name but no type is malformed, spec
     Clarifications Q3).
   - `arrival.cadence`: a plain-language statement of when data is expected to
     land (e.g. "daily by 6am", "weekly on Mondays"). Free text -- HR12 performs
     no semantic parsing of cadence wording (spec Clarifications Q4).
   - `restatement.policy`: whether the supplier ever resends rows for an
     already-loaded period; if so, how a correction is identified and how far
     back it can reach. An explicit "never, because <basis>" is a valid, complete
     answer (spec Edge Cases). If a restatement implies a downstream reload,
     reference 093/HR7's load-policy check by name rather than re-declaring
     idempotency here (FR-012).
3. Remove every `REPLACE_ME_*` sentinel token the template shipped -- HR12 treats
   any field still carrying its sentinel token verbatim as equivalent to that
   field being missing (FR-006).
4. Run `retail check`: HR12 passes for that table, citing the contract's
   committed path as its evidence (SC-001).

## Confirm a declared-but-incomplete contract fails closed (User Story 2)

1. In a scratch/test fixture (never a real table's committed contract -- see
   research.md's Principle-V landing note), author a `source-data-contract.yaml`
   with the `schema` section filled but the `restatement.policy` field left as the
   template's sentinel token.
2. Run the unit test suite (unit-marked): the HR12 rule-behavior test asserts
   exactly one `ERROR` Finding naming that fixture's contract path AND naming the
   `restatement` section specifically -- never a single undifferentiated failure
   (SC-002).
3. Repeat with a blank/missing `arrival.cadence` field: the Finding names
   `arrival`.
4. Repeat with an empty `schema` list: the Finding names `schema`.
5. Repeat with a `schema` entry that has a `name` but no `type`: the Finding names
   `schema` (spec Clarifications Q3 -- a name-only entry is malformed on the same
   footing as an empty list).
6. Repeat with a fixture that is present but not valid YAML at all (a syntax
   error): the Finding names the FIXTURE FILE ITSELF, not a section, and no
   unhandled exception escapes the rule handler (spec Clarifications Q6, FR-002 --
   mirrors the shipped SF1 `except (OSError, yaml.YAMLError)` precedent).

## Confirm HR12 stays static-only (User Story 3)

1. Inspect the HR12 rule module: confirm it imports no database driver, opens no
   connection, and never depends on the `db` extra or a DSN (SC-004).
2. Run `retail check` with no DSN configured and no live database reachable:
   confirm HR12 still evaluates fully and reports a result (pass, fail, or
   not-applicable) based solely on committed files.
3. Inspect HR12's Finding/pass message text: confirm it never states or implies
   that a passing HR12 result proves a live arrival-cadence match or that no
   restatement will ever actually occur on live data -- that live proof stays
   explicitly deferred to a future `retail validate` extension, which this
   feature does not name or build.

## Confirm HR12 stays distinct from its neighbours (Boundary section)

1. Confirm HR12 never reads or writes `source-map.yaml` or `meta.freshness`
   (090/HR4's key) -- grep the rule module for either string; neither should
   appear as a read or write target.
2. Confirm HR12 never reads `readiness-status.yaml` and never raises a
   `stale_pass` blocker (089/HR3's concern).
3. Confirm `templates/source-data-contract.yaml` was never merged into
   `templates/source-map.yaml`'s sister-artifact list, and that the Mapping Ready
   gate's required-artifact count is unchanged (FR-010, SC-006).

## Confirm the wiring / count

1. Run the rule-wiring unit tests: `test_rules_wiring.py` (HR12 is in
   `EXPECTED_RULE_IDS`), `test_wiring_meta_gate.py` (package symmetry, id/manifest/
   posture lockstep, no duplicate registration), and `test_glossary_rule_table.py`
   (HR12 has a row in `docs/glossary.md`'s "Static check rules" table).
2. Confirm `docs/rules/rules-manifest.json` and `docs/rules/severity-posture.json`
   both carry an `HR12` entry, and `docs/quality/rule-count-claims.yaml` is
   reconciled to the new live count.

## What HR12 never does

- Never opens a database connection, computes a live `MAX(<date column>)`, or
  detects a live restatement event (Principle VIII, FR-003).
- Never invents, infers, or defaults a table's actual schema, arrival cadence, or
  restatement policy VALUES -- these are owner-supplied facts a human fills
  (Principle V, FR-005).
- Never judges whether a filled, non-placeholder value is a "good" or "complete"
  answer -- only whether the sentinel token is gone (FR-006).
- Never reads or writes `source-map.yaml`, `meta.freshness`, or
  `readiness-status.yaml`, and never raises a `stale_pass` blocker
  (collision-avoidance allocation, FR-004).
- Never emits a numeric confidence/health/maturity score or an "N of M"
  completeness count (hard rule #9, FR-009).
- Never adds a new readiness stage or a sixth required artifact to the Mapping
  Ready gate (FR-010).
- Never self-grants a Source Ready `pass`, and never rules on the OPEN
  Q-ENFORCEMENT-STRENGTH question (FR-013) on an owner's behalf -- until a
  governance owner rules via the approval-console workflow, HR12's Finding stays
  evidence-only and is never self-wired into any table's `readiness-status.yaml`
  `blocking_reasons[]`.
