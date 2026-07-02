# Phase 0 Research: Additivity-Consistency Lineage Rule

All findings are grounded in committed artifacts (read-only); no capability is assumed.

## R1 -- AL1 scaffold to clone

Decision: clone the shipped assumption-ledger rule module as the structural template.

Confirmed pattern (source: the assumption-ledger rule module `src/retail/rules/assumptions.py`):

- A module docstring stating what it ERRORs on and the Principle-V never-resolve stance.
- `from ..core import Finding, RuleContext, Severity, is_test_path` and
  `from ..registry import register` at module scope (stdlib + core only).
- A compiled glob regex for the contract corpus and a template-path constant.
- A `@register("<ID>", "<one-line description>")` decorated handler returning
  `Iterable[Finding]`.
- The parser (`import yaml`) imported LAZILY inside the handler -- this is the load-bearing
  invariant that keeps the retail-check core stdlib-only at module import time.
- Iterates a sorted list of eligible files, `read_text(encoding="utf-8-sig")`, and on
  `(OSError, UnicodeDecodeError, ParseError)` appends a fail-loud ERROR finding naming the
  path (never silently skips).
- Excludes the generic template path and any `is_test_path(...)` fixture path.
- Emits `Severity.ERROR` only; never mutates the source; never resolves.

Rationale: reusing this scaffold satisfies FR-001, FR-002, FR-003, FR-005 by construction
and keeps the new rule consistent with the shipped rule family.

## R2 -- Read corpus + closed vocabulary (Clarifications Q2)

Decision: read the COMMITTED DEFINE-LAYER PROSE corpus, reached by a generic glob.

Confirmed:

- Additivity is committed as PROSE under an additivity heading in each define-layer metric
  contract; the vocabulary is a genuinely CLOSED three-word set: "Fully additive",
  "Semi-additive", "Non-additive".
- Derivation edges are committed as PROSE under a derives-from heading per contract, plus a
  rendered lineage document that lists base-vs-derived edges.
- The deployable per-table metric contracts carry NEITHER a machine-readable additivity
  field NOR a derives-from field today (additivity appears only inside free-text grain;
  there is no lineage field). Therefore reading those would find no additivity/edge data --
  this is why Q2 chose the define-layer prose corpus.

Generality guard (rule #7): the rule globs whatever define-layer contracts exist; it
hardcodes no worked-example metric names, no worked-example ids, and no worked-example file
paths. The closed vocabulary and the legality table are generic retail arithmetic.

## R3 -- Settled generic facts seeding the closed legality table

Decision: the legality table is drawn from committed GENERIC knowledge, not invented.

Confirmed generic settled facts (source: the committed additivity-and-grain knowledge doc):

- Fully additive -> the measure is a SUM; safe in any total row.
- Non-additive (ratio / average / percentage) -> cannot be summed across ANY dimension;
  must be recomputed base-over-base at each grain ("carry the base components, recompute the
  ratio at every grain").
- Semi-additive -> must NOT be naively summed (needs a time rule: last / average / no-sum);
  flag so the DAX layer does not naively SUM it.

Legality table synthesized from those facts (the exact closed matrix is FR-012, left OPEN
for owner ratification -- it is recorded, not self-approved):

- A non-additive child recomputed from fully-additive parents (base-over-base): LEGAL.
- A ratio/percentage/average (non-additive) child composed by direct SUM: ILLEGAL.
- A semi-additive component composed into a plain-SUM parent: ILLEGAL.

## R4 -- Wiring points and target count

Decision: wire the five places; target count = current authoritative count + 1.

Confirmed five wiring points (source: the shipped new-rule wiring checklist and the live
files):

1. Rule module under `src/retail/rules/`.
2. `src/retail/rules/__init__.py` -- add the module to the side-effecting import block AND
   to `__all__`.
3. `tests/unit/test_rules_wiring.py` -- add the new rule id to the expected-rule-id set
   (the test asserts actual registered ids == expected AND len(all) == len(expected)).
4. `docs/rules/rules-manifest.json` -- regenerate (authoritative count the rule-count
   reconciler reads).
5. The severity-posture manifest / golden fixture -- regenerate.

Current authoritative count is read from the manifest at build time; the target is that
count plus one. (At spec time the manifest and expected set both stand at 44, so the target
is 45 -- but the build MUST read the live count rather than hardcode, in case another rule
lands first.)

## Open items carried forward (NOT resolved here -- Principle V)

- FR-011: metric identity/uniqueness across the two corpora -- OPEN (human ruling).
- FR-012: the exact closed legality matrix as a ratified set -- OPEN (human ruling).
