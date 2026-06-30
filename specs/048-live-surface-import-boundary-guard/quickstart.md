# Quickstart: Live-Surface Import Boundary Guard (B3)

## What this feature adds

One static rule that fails closed (ERROR) when any live-surface module
(`validate.py`, `value_proxy.py`, `semantic.py`, `dax_gen.py`) imports a
connection-capable library at module scope -- making the modules' lazy-driver
discipline a structural error instead of prose. It reuses B1's AST helper
unchanged; the difference is only which modules are scanned.

## Run the rule's tests

```bash
pytest -m unit tests/unit/test_live_surface_boundary.py
```

Proves: a synthetic known-bad live-surface source yields an ERROR Finding (the
rule fires); a lazy / TYPE_CHECKING import yields none; a module-scope `try`/`if`
forbidden import is flagged; an unparseable source yields a fail-loud Finding;
`urllib.parse` is never flagged.

## Run the registry / wiring snapshot

```bash
pytest -m unit tests/unit/test_rules_wiring.py
```

Proves: the live registry id set equals `EXPECTED_RULE_IDS` (with the new id
added) and the count matches `len(EXPECTED_RULE_IDS)` -- no hard-coded baseline.

## Regenerate the manifest (if the snapshot test flags drift)

```bash
retail manifest --repo .
```

Rewrites `docs/rules/rules-manifest.json` from the live registry; the 043
snapshot test guards it.

## Run the whole gate (no DB, no network, no driver)

```bash
pytest -m unit
retail check
```

The rule is part of the stdlib-only static core; it opens no connection and
imports no driver. On the current tree it reports zero Findings (the four modules
already keep their driver imports lazy).
