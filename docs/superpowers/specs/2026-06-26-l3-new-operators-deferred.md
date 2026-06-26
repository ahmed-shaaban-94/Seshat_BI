# L3 new predicate operators (is_false / value_equality / in_set) — DEFERRED (2026-06-26)

> Ranked item #5 from the DAX-fortification sequence (M2 design §C). Assessed on
> 2026-06-26 after L4 (#4) shipped. **Deferred — no consumer exists in this repo.**
> Recording the finding rather than adding dead governance vocabulary.

## VERDICT: **DEFERRED** — the predicate-op whitelist has no unmet demand today.

L3 (`metric_drift.py`) recognizes two predicate ops in a denominator/numerator
filter-set: `is_not_null` (3 DAX spellings) and `is_true` (3 spellings). M2 §C
scoped three *more* ops — `is_false`, then `value_equality`, then `in_set` — each
behind a human gate (frozen-`Filter`-dataclass + contract-schema migration is a
Principle-V call). Before crossing that gate, the discriminating question is **does
any consumer need a new op at all?**

## The discriminating check (run 2026-06-26 — all three empty)

A new op is non-vacuous only if a real artifact reaches it. None does:

| Check | Command | Result |
|-------|---------|--------|
| A denominator predicate currently ESCALATES for being false-shaped | `retail semantic-check --repo .` | **no drift (0 findings)** — nothing escalates |
| A contract declares an op beyond the two recognized | `grep -rn "op:" mappings/*/metrics/*.yaml` | only `is_true` / `is_not_null` |
| A committed measure uses a `FALSE()` / `<> TRUE` predicate | `grep -rniE "FALSE\s*\(\s*\)\|<>\s*TRUE" powerbi/*/definition/` | **none** |

So `is_false` (and a fortiori `value_equality` / `in_set`) would recognize a
predicate **no measure writes** and accept a contract op **no contract declares**.
Adding it changes nothing the gate sees — a "0 new findings" re-verify would pass
**vacuously**, the absence of a consumer dressed as a green check.

## Why not "wire it anyway for completeness"

Unlike L4 (#4) — which had a **pre-approved** value (50.37% in
`DiscountedTransactionRate.yaml`'s `readiness.evidence`) to transcribe — there is
**no pre-approved `is_false` artifact** to make a new op non-vacuous. Manufacturing
one (writing `op: is_false` into a governed contract with no owner approval) would
be **minting** a governance change, the exact line the engine-vs-brain authority
model (ADR-0008 / Principle V) forbids. With no real gap and no approved consumer,
the honest outcome is to defer — the same call made for the pbi-tools spike.

## The vocabulary map (for whoever picks this up when a consumer appears)

A new predicate op touches the recognized-op vocabulary in up to four sites. They
are **not** all mandatory — the two L3 sites are the minimum; the other two **fail
closed** if omitted (so there is no "generator emits what the checker rejects"
landmine forcing all four):

| Site | Role | Required for a new op? |
|------|------|------------------------|
| `metric_drift._recognize_filter` | map DAX predicate text → `Filter(column, op)` | **yes** (the recognizer) |
| `metric_drift._contract_filters` | accept the contract YAML `op` value | **yes** (the contract validator) |
| `dax_gen._OP_TO_DAX` | the generator's canonical emit spelling | optional — omitting it makes `generate` refuse the op (fails closed) |
| `cli._filter_to_sql` (L4) | translate the op to a SQL predicate for `value-check` | optional — omitting it returns None → clean L4 error (fails closed) |

When a real consumer appears (a measure that legitimately filters on a FALSE /
equality / set predicate, with its contract op owner-approved), add the op to the
two L3 sites first (TDD, atomically), then extend the generator + L4 only if that
consumer also generates or value-checks.

## Disposition

- **#5 deferred** — revisit when a measure/contract legitimately needs a new
  predicate op; M2 §C's `is_false`-first ordering still holds.
- **Next item:** the prioritized DAX-fortification sequence (ADR-0013 +
  autopilot "Recommended next steps", items #1-#5) is now **fully shipped or
  honestly deferred** — this L3 deferral closes #5, the last of them. #6 (F016) is
  hard-rule-#6 gated (Semantic Model Ready must `pass` first; execution-only;
  deliberately last) — not startable. The Tier-5 companion tier (#7) is **mostly
  already shipped** (six skills under `.claude/skills/`; roadmap corrected
  2026-06-26); of the four genuinely-unbuilt items, F031-F033 have no consumer (the
  adapters they would maintain are docs-only skills) and F034 (Visual Implementation
  MVP) is the one consumer-backed item but is `Status: Draft` — a spec-finalization
  gate, a design-led report build entered deliberately, not as a drive-by. **Net:
  the autonomous sequence is complete; further work is owner-directed.**
