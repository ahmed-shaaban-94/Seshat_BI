# Phase 1 Data Model: SC1 Status-Claim Reconciler

SC1 introduces no new core types. It reuses the existing `Finding`, `Severity`, and
`RuleContext` from `src/retail/core.py` unchanged. The only new data shape is the
manifest record, defined entirely by the manifest YAML schema (not a Python class).

## Entity: Status-claim manifest (`docs/quality/status-claims.yaml`)

A committed, human-curated YAML file. Single source of truth for what SC1 checks.

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `claims` | list of records | yes | The status claims to reconcile. May be empty (honest no-op), but must be present and a list. |

Top-level shape: a mapping `{ "claims": [ <record>, ... ] }`. Anything else
(not a mapping, missing `claims`, `claims` not a list) -> fail loud (ERROR).

## Entity: Status-claim record (one item of `claims`)

| Field | Type | Required | Meaning | Failure if violated |
|-------|------|----------|---------|---------------------|
| `id` | string | yes | Stable handle for the claim (used in the locator). | missing -> ERROR for the entry |
| `doc` | string (repo-relative POSIX path) | yes | The document that makes the claim. | missing -> ERROR; not a tracked file -> ERROR |
| `anchor` | string | yes | Verbatim snippet that must still be present in `doc`. | missing -> ERROR; not a substring of `doc` text -> ERROR (stale/misplaced) |
| `claimed-artifact` | string (repo-relative POSIX path) | yes | The artifact whose readiness the claim asserts. | missing -> ERROR for the entry |
| `claimed-status` | enum `built` \| `planned` | yes | The asserted readiness. | missing or other value -> ERROR for the entry |

### Reconciliation truth table (per honest, well-formed record)

| `claimed-status` | `claimed-artifact` in tracked_files? | Outcome |
|------------------|--------------------------------------|---------|
| `built` | yes | OK (no finding) -- claim matches evidence |
| `built` | no | ERROR -- false built claim (artifact missing) |
| `planned` | no | OK (no finding) -- honest forward-looking claim |
| `planned` | yes | ERROR -- stale marker (artifact shipped, prose not updated) |

The anchor presence check is a precondition gate applied to every record regardless
of status: if `doc` is untracked, or `anchor` is absent from `doc`'s text, that
record is an ERROR and the truth table above is not the decisive output for it
(the entry is already failing loud).

## Entity: Finding (reused, unchanged)

`Finding(rule_id: str, severity: Severity, message: str, locator: str)` from
`src/retail/core.py`. SC1 emits ONLY `Severity.ERROR` findings. Every finding:

- `rule_id` = `"SC1"`.
- `severity` = `Severity.ERROR`.
- `message` = a human-readable, generic statement naming the offending
  doc / artifact / claim and the contradiction (no numeric/graded value, no
  C086/pharmacy specifics).
- `locator` = the manifest entry (e.g. `docs/quality/status-claims.yaml:<id>`)
  and/or the claiming doc, so the maintainer can find and fix it.

## Entity: RuleContext (reused, unchanged)

`RuleContext(repo_root: Path, tracked_files: tuple[str, ...], ...)`. SC1 consumes:

- `tracked_files` -- to test manifest presence, `doc` presence, and
  `claimed-artifact` presence (the evidence set).
- `repo_root` -- to read the manifest text and each claiming `doc`'s committed text.

SC1 adds no field to `RuleContext`.

## Invariants

1. SC1 never writes. Read-only over committed text + the tracked-files set.
2. SC1 never opens a DB/network/Power BI connection; the YAML dependency is the only
   import and it is lazy, inside the handler.
3. SC1 output is categorical only -- no number, percentage, or score in any finding.
4. The manifest and rule are generic -- no worked-example (C086/pharmacy) path,
   value, segment, or PII token hardcoded in the rule or seeded as a kit entry.
