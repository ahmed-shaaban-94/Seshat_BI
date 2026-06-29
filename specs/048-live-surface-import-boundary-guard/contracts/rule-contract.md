# Contract: Live-Surface Import Boundary Guard rule (B3)

The rule is a `RuleContext -> Iterable[Finding]` checker registered via
`@register`. This is the checkable contract its tests assert.

## C1 -- Module-scope forbidden import in a live-surface module -> ERROR Finding

Given a live-surface module (in the rule's set) whose source contains a
module-scope import of a connection-capable library (e.g. `import psycopg2`,
`from requests import get`), the rule emits exactly one ERROR `Finding` per
offending import name, with `locator` set to that module's repo-relative path and
a message naming the offending import.

## C2 -- Lazy / TYPE_CHECKING import -> no Finding

Given the same forbidden import placed inside a `def`/`async def`/`class` body
(lazy), or inside an `if TYPE_CHECKING:` block, the rule emits NO Finding for
that module. (Inherited directly from `module_scope_violations` semantics.)

## C3 -- Module-scope `try`/`if` forbidden import -> flagged

Given a forbidden import inside a module-level `try`/`except`/`else`/`finally` or
a plain module-level `if`/`else` (which execute on import), the rule emits an
ERROR Finding. A `try: import psycopg2 except ImportError:` optional-dependency
guard at module scope is therefore flagged.

## C4 -- Unparseable scanned module -> ERROR Finding (fail loud)

Given a scanned module whose source does not parse, the rule emits an ERROR
Finding for that module (never crashes the gate, never passes vacuously).
Mirrors B1's SyntaxError-to-Finding behavior.

## C5 -- `urllib.parse` is never flagged

A module-scope `from urllib.parse import quote` (pure stdlib string work, used for
DSN escaping) produces NO Finding. Only connection-capable roots and the dotted
`urllib.request` / `urllib.error` are forbidden.

## C6 -- Registry / wiring / manifest agree, with a firing test

After the rule is added: the live registry id set equals
`EXPECTED_RULE_IDS` in `tests/unit/test_rules_wiring.py`, the regenerated
`docs/rules/rules-manifest.json` contains the new id, and at least one test
invokes the rule directly on a known-bad fixture and observes a non-empty Finding
set (the rule fires, not merely registers). No literal baseline count is asserted
anywhere.

## C7 -- No new Severity tier

The rule emits only the existing `Severity.ERROR`. It adds no new severity or
status value and changes no existing gate exit mapping.

## C8 -- No domain-specific artifact

The rule's module set, its forbidden set (reused), and every test fixture
reference only generic module paths and library names -- no specific table,
column, or KPI. Fixtures are synthetic source strings.

## C9 -- Reuse, not fork

The rule imports `module_scope_violations`, `_FORBIDDEN_ROOTS`, and
`_FORBIDDEN_DOTTED` from `retail.rules.never_execute` rather than redefining a
parser or forbidden list. B1 and B3 share one definition of "connection-capable
module-scope import".

## C10 -- Scanned modules unchanged + green today

The four scanned modules are not modified by this feature, and the rule produces
zero Findings on the current committed tree (their driver/`yaml` imports are
already lazy). The rule fires only on a future regression.
