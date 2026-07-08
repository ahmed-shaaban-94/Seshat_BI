# semantic_pair_drift wiring — DEFERRED (2026-07-08)

> The fourth and last F014 drift taxonomy class. The other three always-Principle-V
> classes ship: `grain_pk_drift` (#230), `returns_rule_drift` + `pii_surface_drift`
> (#231), fed live by the source-map semantics loader (#232). This one is
> **deferred — it cannot be built the zero-ripple way the others were, has no live
> target, and its severity is itself a human ruling.** This is the honest verdict,
> not an omission: the schema `driftClass` enum already lists `semantic_pair_drift`,
> so the CONTRACT is whole; only the runtime detector is held.

## VERDICT: **DEFERRED** — no measurement exists, no carrier exists, no target, and it ripples the pure core.

## What the class is

Taxonomy (`docs/readiness/source-drift.md`): *"Semantic-pair drift — a baseline 1:1
code/label (or id->name) pair is no longer 1:1 — `warning` (auto) / `blocked` (if it
underpins identity)."* Example from the retail_store_sales mapping: `item -> category`
is 1:1 (0 fan-out); drift = that pairing developing fan-out on a re-profile.

## Why it is categorically different from the three shipped classes

The three shipped Principle-V classes were **zero-ripple re-classifications**: each
took an already-measured per-column diff (`column_removed` / `column_added` /
missingness-cardinality shift) and re-labelled it, keyed on a machine-readable
source-map ruling delivered through an OPTIONAL `DriftSemantics` param. `None` =>
they stay silent; nothing in the pure `ProfileResult` shape changed.

`semantic_pair_drift` cannot be done that way. It is a **pairwise** fact
(`is column A still 1:1 with column B?`), not a per-column one, and it needs a
BASELINE RATE to compare an observed rate against. Three things it needs do not
exist today:

| Missing piece | Current reality | Consequence |
|---------------|-----------------|-------------|
| **A pairwise fan-out MEASUREMENT** | `retail.profile.profile` computes per-column stats only. `profile.py`'s own docstring: "code<->label 1:1... needs the table's MEANING and is deliberately NOT computed here." | There is no `COUNT(DISTINCT a) vs COUNT(DISTINCT (a,b))` measurement to diff. The profiler must be extended to measure declared pairs. |
| **A BASELINE carrier for the rate** | `ProfileResult` (and `ParsedBaseline`) carry no pair-rate field. The 1:1 fact lives only as PROSE — a `reason:` string (`"1:1 with category (0 fan-out)"`) and a comment (`item->category 1:1`). | To compare baseline-vs-observed, the baseline must record the measured rate. That is a `ProfileResult`/`ParsedBaseline` shape change — RIPPLE into the pure core that `drift.py`, `source_profile_reader.py`, and every importer share. |
| **A machine field naming the pairs** | source-map.yaml records pairs only in prose. There is no `semantic_pairs:` list. | The loader has nothing to key on (unlike `pii`/`decision`/`derived_from`, which are real fields). The source-map TEMPLATE would need a new governed field. |

## The severity cannot be mechanically determined

Severity is `warning` (auto) / **`blocked` if it underpins identity**. WHICH pairs
underpin identity is itself a Principle-V ruling (per the taxonomy's own "NEVER
auto-assert entity identity when semantic-pair drift underpins identity -> raise it
for the analyst / data-owner"). So even the severity needs a human input recorded
somewhere — it is not a clean mechanical classification the way the column-diff
escalations were.

## No vacuous shortcut

A tempting shortcut is to emit `semantic_pair_drift` whenever a column's cardinality
changes near a "paired" column. **Rejected as fabrication.** Cardinality shift is
already its own class; re-labelling it as pair-drift without an actual pairwise
fan-out measurement invents a relationship the data was never checked for — exactly
the "never fabricate a comparison" hard rule. A real detector must MEASURE the pair,
not infer it from single-column stats.

## Why deferral is the correct call now (not manufactured progress)

- **No target:** the only filled mapping (retail_store_sales) records its one pair
  (`item->category`) as prose, not a machine field — so even a built detector is a
  no-op against real data, matching the [open-work] rule against manufacturing a
  build to "make progress."
- **No consumer demand:** nothing downstream requests pair-drift today.
- **Ripples the pure core:** ~8 touchpoints (ProfileResult shape, the profiler's
  pairwise measurement, ParsedBaseline, source_profile_reader parse, the source-map
  machine field, the source-map + source-profile templates, the loader, the
  classifier). A multi-PR feature, not a finish-it increment.
- **Precedent:** `docs/superpowers/specs/2026-06-26-pbi-tools-extract-spike-deferred.md`
  and `...-l3-new-operators-deferred.md` deferred for the same "no consumer/target"
  reason.

## Proposed design (for a future session with a filled target)

When a real table with an identity-bearing 1:1 pair lands, build in this order:
1. **source-map field:** add a governed `semantic_pairs:` list to
   `templates/source-map.yaml` — each entry names `left`, `right`, the measured
   baseline `fanout` (0 for clean 1:1), and an explicit `underpins_identity: bool`
   (the human ruling that sets severity). Fill it in the target's mapping.
2. **profiler:** extend `retail.profile` to measure each declared pair's fan-out
   (`COUNT(*) WHERE a maps to >1 b`) on the landed data; carry it on `ProfileResult`
   (a new `pair_fanout: tuple[PairFanout, ...]` field — the ripple, done once).
3. **baseline carrier:** `source_profile_reader` parses the recorded baseline rates
   into `ParsedBaseline`; the loader reads `semantic_pairs[].underpins_identity`
   into `DriftSemantics`.
4. **classifier:** add `_semantic_pair_findings(baseline, observed, semantics)` to
   `classify_drift` — fires when a baseline-0-fanout pair now has fan-out; severity
   `blocked` iff `underpins_identity`, else `warning`; `principle_v` iff blocked.
   Wire `_DEFAULT_OWNER["semantic_pair_drift"]="analyst"` +
   `_HANDOFF_QUESTION` in the SAME change (the scoped-dict discipline).

## Status of F014 without this class

**Buildable scope complete.** The taxonomy's schema enum already lists all nine
classes (the contract is whole); five are emitted (`column_added/removed`,
`missingness_shift`, `cardinality_shift`, `grain_pk_drift`) plus the two semantic
escalations (`returns_rule_drift`, `pii_surface_drift`) when a filled mapping
supplies the roles. Only `semantic_pair_drift` (this doc) and `column_retyped`
(needs `ProfileResult` to carry the landed type — a separate, smaller deferral)
remain, both held for want of a measurement/carrier, not design.
