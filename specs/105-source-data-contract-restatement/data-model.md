# Phase 1 Data Model: Source Data-Contract (HR12)

No persisted database schema is introduced. These are the on-disk YAML shapes this
feature defines, plus the in-memory shapes the rule builds while reading committed
text. All shapes are generic (Principle VII): no worked-example table/column name,
cadence wording, or restatement specifics appears in any field, enum value, or
sentinel token below. Any reference to a real table (`retail_store_sales`,
`demo_sample_orders`) is illustrative only, never an authoritative part of the
schema, and this feature does not author a filled instance for either table
(Principle V; see research.md's landing analysis).

## `templates/source-data-contract.yaml` (NEW generic template -- FR-001)

The copy-me template a human instantiates once per onboarded table. Ships with
every required field pre-filled with a distinctive sentinel token so a copy that is
never edited is mechanically distinguishable from a real, owner-authored value
(FR-006 / spec Clarifications Q2). Illustrative shape (values below are the
sentinel placeholders themselves, not real defaults):

```yaml
# =============================================================================
# source-data-contract.yaml -- forward schema + arrival + restatement policy
# =============================================================================
# A GENERIC, copy-me template. Instantiate ONE copy per onboarded table at
# mappings/<table>/source-data-contract.yaml. This is a FORWARD-LOOKING
# supplier agreement -- what the upstream source has committed to deliver and
# how it behaves over time -- distinct from source-map.yaml's DESCRIPTIVE map
# of what the source actually looks like once profiled (see spec Boundary
# section). Fill every field below with a real, owner-supplied fact about the
# actual upstream system. Do NOT leave the REPLACE_ME sentinel in any field --
# HR12 (retail check) fails closed on any section still carrying it.

schema:
  # One entry per column the supplier has committed to deliver. Each entry
  # MUST carry both a name and a type -- a name with no type is malformed on
  # the same footing as an empty list (spec Clarifications Q3).
  - name: "REPLACE_ME_COLUMN_NAME"
    type: "REPLACE_ME_COLUMN_TYPE"

arrival:
  # Plain-language statement of when the supplier commits to deliver data
  # (e.g. "daily by 6am", "weekly on Mondays"). HR12 checks only that this
  # field is present and non-placeholder -- it performs no semantic parsing
  # of cadence wording or format (spec Clarifications Q4).
  cadence: "REPLACE_ME_ARRIVAL_CADENCE"

restatement:
  # Whether the supplier ever resends rows for an already-loaded period, and
  # if so, how a correction is identified (a last-modified column, a resend
  # flag, a full-period reload) and how far back a resend can reach. A plain
  # "never, because <basis>" is a valid, complete answer (spec Edge Cases).
  # Where a restatement implies a downstream reload, reference 093/HR7's
  # load-policy check by name rather than re-declaring idempotency here
  # (FR-012) -- do not restate or re-check HR7's own concern.
  policy: "REPLACE_ME_RESTATEMENT_POLICY"
```

## Key entities

### `SourceDataContract` (the parsed per-table YAML document)

- `path`: repo-relative path, always `mappings/<table>/source-data-contract.yaml`
  (FR-008). Read only when it appears in `ctx.tracked_files` (Principle IX
  reproducibility; mirrors AL2's/093-HR7's own `ctx.tracked_files`-only pattern).
- `schema`: a list of `SchemaEntry`. Required section.
- `arrival`: an `ArrivalDeclaration`. Required section.
- `restatement`: a `RestatementPolicy`. Required section.

A table with NO file at this path is simply absent from HR12's evaluation set --
never represented as an empty/default `SourceDataContract` (FR-002's opt-in
posture: absence is not-applicable, not a defaulted empty value).

### `SchemaEntry`

- `name`: the column name the supplier commits to deliver. Required,
  non-placeholder.
- `type`: the expected type for that column. Required, non-placeholder. An entry
  with a `name` but a missing/blank/placeholder `type` is malformed on the same
  footing as an empty `schema` list overall (spec Clarifications Q3) and fails the
  `schema` section closed.

Rule: `schema` fails closed when the list is empty, OR when any entry is missing a
`name`, missing a `type`, or either field still holds the sentinel token verbatim.

### `ArrivalDeclaration`

- `cadence`: free-text plain-language statement. Required, non-placeholder,
  non-blank. HR12 performs NO semantic parsing of cadence structure or vocabulary
  (spec Clarifications Q4) -- presence and non-placeholder status only.

### `RestatementPolicy`

- `policy`: free-text statement of whether the supplier ever resends rows for an
  already-loaded period, how a correction is identified, and how far back a resend
  can reach (or an explicit "never" with its stated basis). Required,
  non-placeholder, non-blank. HR12 performs no judgment on whether the stated
  policy is a "good" or "complete" answer (Principle V, FR-005) -- only whether the
  sentinel is gone (FR-006).

### `SentinelToken` (the structural placeholder-detection mechanism, FR-006)

Not a stored entity -- a fixed set of literal string constants HR12's rule module
defines and the template ships verbatim, one per required field family (e.g. a
`REPLACE_ME`-prefixed token per section, as shown in the template above). Detection
is an EXACT, case-sensitive substring/equality check against the live field value
after whitespace normalization -- never a regex-based heuristic, never a semantic
judgment. A field is "still a placeholder" when:

- the field is absent from the parsed YAML, OR
- the field is blank/empty (empty string, `null`, or an empty list for `schema`),
  OR
- the field's value, once whitespace-normalized, is byte-identical to the
  sentinel token the template shipped for that field.

Any other non-empty value -- however short, however implausible-looking to a human
reviewer -- is accepted as filled. HR12 never scores or judges quality (Principle
V, FR-005, FR-009).

## `HR12Finding` (uses the existing `Finding` model -- no new entity)

- `rule_id`: `"HR12"`.
- `severity`: `Severity.ERROR` on a present-but-incomplete/placeholder contract
  (FR-002/FR-006, User Story 2: fails closed, never silently passes a half-filled
  contract). This governs `retail check`'s own pass/fail reporting for that
  Finding (Principle I) and is a SEPARATE layer from whether the Finding is wired
  into any table's `readiness-status.yaml` `blocking_reasons[]` -- that separate
  wiring question is FR-013's genuinely open item (see research.md's
  Q-ENFORCEMENT-STRENGTH note); HR12 itself never writes to
  `readiness-status.yaml`.
- `message`: names the offending contract file path and the SPECIFIC incomplete
  section(s) -- `schema`, `arrival`, or `restatement` -- individually, never a
  single undifferentiated "contract incomplete" message (FR-006, spec
  Clarifications). Never states or implies that a passing HR12 result proves a
  live arrival cadence match or that no restatement will ever occur (FR-003, US3).
- `locator`: the contract's repo-relative path (`mappings/<table>/
  source-data-contract.yaml`), the same string cited as passing evidence when the
  contract is complete (SC-001).
- **Malformed-YAML branch (spec Clarifications Q6, FR-002)**: when the file is
  present in `ctx.tracked_files` but `yaml.safe_load` raises (`yaml.YAMLError`) or
  the read itself fails (`OSError`), HR12 emits exactly ONE `Severity.ERROR`
  Finding naming the FILE ITSELF -- not a section, since none could be parsed --
  with `locator` set to the contract's path. This mirrors the shipped SF1
  precedent (`rule_sf1.py`'s `except (OSError, yaml.YAMLError)` branch) and AL2's
  "tracked-but-unreadable contract fails loud" posture: HR12 MUST NOT raise an
  unhandled exception out of the rule handler, and MUST NOT silently treat an
  unparseable file as not-applicable (which would be indistinguishable from the
  file not existing at all, defeating FR-002's opt-in-but-fail-closed-when-present
  contract). This is a DISTINCT outcome from the per-section Findings above: a
  parse-error Finding never also enumerates `schema`/`arrival`/`restatement` by
  name, since no section was ever successfully parsed.
- The rule's other two outcomes: (a) emitting NO Finding when every section is
  filled and well-formed (pass-eligible; evidence cites the contract path per
  SC-001); (b) emitting NO Finding at all, for a table with no contract file
  (not-applicable, SC-003). No numeric field exists anywhere on this entity (hard
  rule #9, FR-009).

## Invariants

- Read-only: HR12 mutates no source artifact, ever (Principle VIII).
- No execution: HR12 opens no database connection, computes no live `MAX(<date
  column>)`, and detects no live restatement event (FR-003).
- Opt-in / default-free-pass: a table with no `source-data-contract.yaml` produces
  no Finding at all -- not represented as a defaulted-empty contract (FR-002;
  Principle VI).
- Fail-closed on incomplete-but-present: a contract missing any required section,
  or carrying an unedited sentinel token in any required field, always produces at
  least one `ERROR` Finding naming the specific section(s) (FR-006).
- Fail-closed on unparseable: a present file that is not valid YAML at all (a
  parse error) always produces exactly one `ERROR` Finding naming the FILE itself
  (never a section, since none could be parsed), and never raises an unhandled
  exception out of the rule handler (spec Clarifications Q6, FR-002).
- Structural-only verification: a field is checked for presence and exact-token
  non-placeholder status only, never judged for semantic quality or "correctness"
  against a live schema (FR-005, Principle V).
- No collision: `source-map.yaml`, `meta.freshness`, and `readiness-status.yaml`
  are never read or written by HR12 (FR-004, collision-avoidance allocation).
- No score, ever: outcome is categorical (Finding(s) or no Finding) only (FR-009).
- No new gate artifact list change: `templates/source-data-contract.yaml` is never
  added to the Mapping Ready gate's five-artifact list (FR-010).
- Additive: HR12 changes no existing rule's (S6/S7/S8/HR1/HR3/HR4/HR7/AL2/any
  RC-series) Finding text or pass/fail outcome.
