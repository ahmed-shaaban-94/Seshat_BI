# Phase 1 Data Model: Live-Surface Import Boundary Guard (B3)

This feature is a static rule; its "data" is a small set of in-code constants and
the immutable Finding objects it emits. No persistent storage, no schema.

## Entity: Live-surface module set

- **What it is**: an explicit, closed collection of repo-relative POSIX module
  paths the rule scans.
- **Candidate members** (final set reserved for human ratification, spec
  ## Clarifications): `src/retail/validate.py`, `src/retail/value_proxy.py`,
  `src/retail/semantic.py`, `src/retail/dax_gen.py`.
- **Invariants**:
  - Disjoint from B1's `_GOVERNED_MODULES` and `_GOVERNED_PREFIX` (no module is
    covered by both rules).
  - Generic module paths only -- no domain-specific table / column / KPI name.
  - Defined in exactly one named place (the new rule module).
- **Lifecycle**: static; changes only by an explicit, ratified edit.

## Entity: Forbidden import roots / dotted modules (REUSED, not redefined)

- **What it is**: the connection-capable library set
  (`_FORBIDDEN_ROOTS` + `_FORBIDDEN_DOTTED`) imported unchanged from
  `retail.rules.never_execute`.
- **Members**: psycopg2, psycopg, asyncpg, sqlalchemy, pymysql, pyodbc, requests,
  httpx, aiohttp, socket, http, urllib3, ftplib, smtplib, telnetlib, websocket,
  websockets; dotted `urllib.request`, `urllib.error`. `urllib.parse` is NOT
  forbidden (pure stdlib string work).
- **Invariant**: B3 does not add to, remove from, or copy this set -- it imports
  the same objects, so B1 and B3 always agree on "connection-capable".

## Entity: Rule registration record

- **Fields**: `id` (a B-family registry id, reserved for human ratification),
  `title` (a short human-readable description), `rule` (the checker function).
- **Mirrors**: the id is added to `EXPECTED_RULE_IDS` in
  `tests/unit/test_rules_wiring.py` and appears in the regenerated
  `docs/rules/rules-manifest.json`.
- **Invariant**: registry id set == wiring expected set == manifest id set; the
  wiring test keys the count off `len(EXPECTED_RULE_IDS)`, never a literal.

## Entity: Finding (emitted, immutable)

- **Fields** (existing `retail.core.Finding`): `rule_id`, `severity`, `message`,
  `locator`.
- **For this rule**:
  - `rule_id` = the rule's registered id.
  - `severity` = `Severity.ERROR` (uniform; clarified 2026-06-30).
  - `message` = names the offending import and instructs to keep it lazy inside
    the connecting handler.
  - `locator` = the repo-relative path of the offending live-surface module.
- **Cardinality**: one Finding per offending module-scope forbidden import name;
  one Finding per unparseable scanned module (fail loud).
- **Invariant**: Findings are new immutable values; the rule mutates no shared
  state (coding-style immutability rule).

## State transitions

None. The rule is a pure function of `RuleContext` (`repo_root`,
`tracked_files`) -> a list of Findings. Given the same tracked source, it always
returns the same Findings.
