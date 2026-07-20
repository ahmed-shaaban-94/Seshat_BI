# Dagster redaction robustness — explicit secret-key set (#357)

Date: 2026-07-19
Issue: #357
Module: `src/seshat/dagster_adapter/redaction.py`

## Problem

The Dagster adapter redactor decides which `os.environ` values to scrub with a
**negative** rule plus a length gate:

- `_is_secret_key(key)` treats *every* `ANALYTICS_DB_*` key as secret **except**
  an enumerated `_NON_SECRET_ANALYTICS_KEYS` allowlist
  (`PORT/SSLMODE/ENGINE/ODBC_DRIVER/TRUST_CERT`).
- `_secret_env_values()` only collects values with `len(value) >= 4`.

Since #348 loads the workspace `.env` into `os.environ` for the DB-touching
verbs, both halves became live and both are blunt:

- **Over-redaction (allowlist incompleteness):** any *new* non-secret
  `ANALYTICS_DB_*` config key that is not yet in the allowlist has its value
  globally string-replaced, corrupting ordinary output. The allowlist has
  already needed two reactive extensions; it will keep needing entries as
  `.env.example` grows.
- **Under-redaction (short values):** a valid but short `ANALYTICS_DB_HOST=db`
  or `ANALYTICS_DB_USER=sa` (< 4 chars) is ignored by the length gate, so a
  reformatted driver error like `connection to server at "db" failed for user
  "sa"` (not `key=value` shape, so `_KEYWORD_RE` misses it) prints the host/user
  verbatim.

## Approach — explicit SECRET-key set (chosen)

Invert the authority: enumerate the keys that ARE credentials, redact only
those, and treat everything else as non-secret by default. This mirrors the
existing `seshat.dbt.redaction` module (`_SECRET_ENVIRONMENT_KEYS`), which uses
exactly this positive-set shape.

```python
# The ANALYTICS_DB_* keys whose VALUES are credentials. Everything else in the
# namespace (PORT/SSLMODE/ENGINE/ODBC_DRIVER/TRUST_CERT and any FUTURE config
# knob) is non-secret BY DEFAULT -- no enumerated exclusion list to maintain.
_SECRET_ANALYTICS_KEYS = frozenset(
    {
        "ANALYTICS_DB_HOST",
        "ANALYTICS_DB_NAME",
        "ANALYTICS_DB_USER",
        "ANALYTICS_DB_PASSWORD",
        "ANALYTICS_DB_ACCOUNT",
    }
)
```

`_is_secret_key(key)` becomes: `True` iff `key == "DATABASE_URL"`, or
`key in _SECRET_ANALYTICS_KEYS`, or the generic `_SECRET_ENV_RE`
(`PASSWORD|SECRET|TOKEN|_KEY`) matches — the last preserved so non-`ANALYTICS_DB_`
secrets (`*_TOKEN`, `*_SECRET`, …) still redact.

`_secret_env_values()` drops the `len(value) >= 4` gate and collects any
**non-empty** value for a secret key (the user-approved short-value policy:
correctness over cosmetics — a host/user is sensitive infra at any length).

The `_DSN_RE` and `_KEYWORD_RE` passes in `redact_text` are unchanged.

### Why not the alternatives

- **Quoted-token / keyword-adjacent matching** (issue's option B): a new regex
  layer with its own edge cases — unquoted reformatted errors still slip, and
  driver quoting is inconsistent. Higher risk for the same low-severity residual;
  Codex itself questioned it.
- **Both** (belt-and-suspenders): over-engineering for what the issue describes.

## Behavior change (exactly two cells)

Verified against a characterization matrix (long secret / short secret / config
knob / `DATABASE_URL` / generic `*_TOKEN`) pinned on current `main`:

| Case | main | proposed |
|------|------|----------|
| `ANALYTICS_DB_NAME=warehouse` (long secret) | redacted | redacted (same) |
| `ANALYTICS_DB_USER=sa` (short secret) | **NOT** redacted | **redacted** ← under-redaction fix |
| `ANALYTICS_DB_ENGINE=postgres` / `PORT=25060` (config) | not redacted | not redacted (same) |
| `DATABASE_URL=postgresql://…` | redacted (via `_DSN_RE`) | redacted (same) |
| `FOO_TOKEN=…` (generic secret) | redacted | redacted (same) |

Strict improvement on #357's two axes; neutral everywhere else.

## Known accepted limitation (documented)

Redaction is a **global substring replace**, so a database literally named a
common word (`ANALYTICS_DB_NAME=gold`) has that word clobbered wherever it
appears in output — this is unchanged from `main` (NAME is already secret at
len>=4) and is the inherent tradeoff of the chosen approach vs. the quoted-token
alternative. It is safe-direction (a dbname must never surface, per the
all-output-redacted contract) and therefore a documented decision, not a defect.

## Testing (TDD, baseline-first)

1. **Characterization test** (RED baseline): pin `redact_text` output over the
   value matrix above against current behavior, so the refactor is provably
   correct iff it flips exactly the two intended cells and leaves the rest
   identical.
2. **Under-redaction regression test:** short `ANALYTICS_DB_USER=sa` /
   `HOST=db` in a reformatted (non-`key=value`) error string is redacted.
3. **Structural-exclusion test:** a *hypothetical future* config key
   (`ANALYTICS_DB_APP_NAME=seshat`) is NOT redacted without touching the module
   — proving the enumerated-allowlist churn is gone.
4. **Preserved-coverage tests:** `DATABASE_URL` DSN and a generic `FOO_TOKEN`
   still redact (guard against dropping either during the refactor).

## Scope

Single module, no public API change (`redact_text` / `redact_payload`
signatures unchanged). No behavior change outside the two matrix cells.
Supersedes the `_NON_SECRET_ANALYTICS_KEYS` enumerated allowlist added in #348.
