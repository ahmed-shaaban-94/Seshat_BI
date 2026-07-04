# Quickstart: Source Freshness / Staleness Declaration and Static Presence Check

How an agent or developer exercises HR4 once it is implemented. This is a
walkthrough of the INTENDED usage, not an implementation guide -- it assumes
`src/retail/rules/rule_hr4.py` and the `templates/source-map.yaml`
`meta.freshness` schema edit already exist per plan.md / data-model.md. All
table names, cadence values, and durations below (`<table>`, `weekly`,
`"3 days"`) are illustrative placeholders (Principle VII).

## 0. Preconditions

- A table has already cleared the source-mapping gate (Stage 2, Mapping
  Ready) -- its `mappings/<table>/source-map.yaml` exists and is approved.
  A table with no `source-map.yaml` yet (Stage 1) is entirely outside HR4's
  scope; nothing to exercise there (FR-005).
- Whether adding `meta.freshness` is REQUIRED for this particular table is
  governed by the OPEN Q-FR014-SCOPE ruling (spec.md FR-014), not by this
  feature. Until an owner rules, adding the block is voluntary and its
  absence produces no Finding (see step 1).

## 1. Run the gate on a table with no `meta.freshness` block at all

```
retail check
```

- If the table's `source-map.yaml` has no `freshness` key under `meta:`:
  HR4 emits **no Finding** for that table. This is the presence-gated design
  (research.md "Landing precondition") -- it is expected and correct, not a
  bug, and it is why `retail check` stays green on both currently-committed
  worked examples (`retail_store_sales`, `demo_sample_orders`) even though
  neither carries the block today.

## 2. A data owner declares the SLA (Principle V -- the agent does not invent this)

A named data owner, not the agent, edits the table's `source-map.yaml` and
adds a `freshness` block under `meta:`, alongside the existing `grain`/
`primary_key`/`reviewed_by` keys:

```yaml
meta:
  table_id: "<table>"
  # ... existing keys unchanged ...
  freshness:
    expected_cadence: "weekly"
    max_staleness: "3 days"
```

The agent's role here is limited to: (a) explaining the recognized grammar
(the closed cadence enum + duration form, or `one_time`/`static` paired with
`n/a`) if asked, and (b) running `retail check` afterward to confirm the
block is well-formed. The agent never picks a cadence or staleness value on
the owner's behalf (FR-002, FR-008, hard rule #9 -- no fabricated freshness).

## 3. Re-run the gate after the declaration

```
retail check
```

- **Both sub-keys well-formed**: no HR4 Finding for that table (SC-001).
- **A sub-key left blank or removed** (e.g. `max_staleness: ""` or the key
  deleted while `freshness:` itself remains): HR4 emits one ERROR naming the
  table and the specific missing sub-key (SC-002, User Story 2 scenario 2).
- **A sub-key present but unparseable** (e.g. `expected_cadence: "sometimes"`
  or `max_staleness: "a while"`): HR4 emits one ERROR naming the table and
  the malformed value -- never a silent pass, never a best-guess
  interpretation (Edge Cases, FR-004(b)).

## 4. Exercise the one-time/static reference-source token

```yaml
meta:
  freshness:
    expected_cadence: "one_time"     # or "static"
    max_staleness: "n/a"
```

- This pairing is WELL-FORMED at the grammar level (Clarification C2): HR4
  emits no Finding for it. Whether a genuinely one-time source is REQUIRED
  or permitted to use this opt-out (as opposed to a full HR4 exemption) is
  still the OPEN Q-FR014-SCOPE ruling -- this step only demonstrates that the
  reserved token itself is recognized, not that any particular table is
  mandated to use it.

## 5. Confirm the template file is exempt

- Inspect `templates/source-map.yaml`: it now carries a `meta.freshness`
  placeholder block (schema documentation, generic placeholder text such as
  `"<cadence: daily|weekly|monthly|quarterly|annual|one_time>"`).
- Run `retail check`: HR4 emits **no Finding** for the template file, even
  though its placeholder text does not literally match the grammar
  (Clarification C3) -- the template is schema documentation, not a real
  per-table declaration, exactly like the existing convention for every
  other `meta` field's placeholder text.

## 6. Confirm no live surface is touched

None of the steps above require a database connection, a Power BI Desktop
session, or network access. `retail check` running HR4 exits deterministically
from committed text alone (Principle VIII) -- directly observable by running
it offline. HR4 never computes an actual arrival timestamp or elapsed
staleness duration; it only checks that a human-declared SLA is present (once
offered) and well-formed.

## 7. Confirm the categorical-only output (hard rule #9)

At every step above, `retail check --format json` (or the default text
output) shows HR4 Findings with `rule_id`, `severity`, `message`, `locator`
only -- never a percentage, a computed staleness duration, a freshness score,
or an "N of M declared" tally. A human-declared `max_staleness` value itself
(e.g. `"3 days"`) is a declared SLA input, not a forbidden score (FR-007
explicitly distinguishes the two); HR4 never rolls that value up into any
kind of rating.

## 8. What this quickstart does NOT cover (explicitly deferred)

- **Live freshness verdicts.** Nothing here compares a declared
  `max_staleness` against an actual measured arrival time. That comparison
  is deferred to a future `retail validate` surface (most likely spec 082);
  until it exists, any surface reporting on a table's ACTUAL freshness must
  say `[PENDING LIVE FRESHNESS CHECK]` with a non-`pass` status, never a
  fabricated pass. This feature introduces no such surface itself
  (Clarification C4) -- there is nothing to click through here for it.
- **Missing-segment / date-spine completeness.** PB-SQL-09 as documented also
  covers "a segment is missing"; that is explicitly out of scope for HR4
  (FR-010) and is not exercised by any step above.
- **The FR-014 rollout ruling.** This quickstart does not demonstrate a
  "mandatory block" failure mode, because that mode does not exist yet --
  it is gated on a named-human decision (Q-FR014-SCOPE) this feature does
  not make.
