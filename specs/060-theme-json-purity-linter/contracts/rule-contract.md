# Rule Behavioral Contract: Theme JSON Purity Linter

This is the behavioral contract the rule must satisfy. It is the checkable
interface between the spec's requirements and the unit tests. No code here -- only
observable behavior.

## Registration contract

- The rule is a single `@register(<fresh-id>, <title>)`-decorated function that
  returns an iterable of findings, discovered by importing the rules package.
- `<fresh-id>` MUST NOT equal any already-registered id (backlog letters A1/A2 are
  disallowed because A1/A3 are taken); a design/theme-namespaced id is preferred.
- The id is present in: the registry (via import), the expected-rule-id set the
  wiring test asserts, the generated rule manifest, and the generated
  severity-posture record. (Five-place wiring; drift fails closed.)

## Input contract

- Reads committed theme JSON files discovered generically from the tracked-file set
  by a theme-file naming pattern.
- Excludes files under the test-fixture exemption path from the live scan.
- Does not read any non-theme file; requires no network, service, or Desktop.

## Behavioral contract (each row is a unit test)

| # | Given | Then |
|---|-------|------|
| C1 | a committed theme file with one forbidden business-logic key | exactly one ERROR finding, locator points at that key, non-zero exit |
| C2 | a forbidden key nested inside a deeper object | the finding locator points at the nested key path, not just the file |
| C3 | a theme file with two distinct forbidden keys | exactly two ERROR findings (one per key); neither masks the other |
| C4 | a theme file using only allowed styling keys | zero findings |
| C5 | a theme file with a sentiment COLOR but no threshold/rule | zero findings (color allowed, threshold would not be) |
| C6 | the current committed starter theme in its clean state | zero findings (green build preserved) |
| C7 | a value string that equals a forbidden word (not a key) | zero findings (values are not scanned) |
| C8 | a committed theme file that is not valid JSON | one finding that the file could not be parsed; the gate does not crash and the file does not pass silently |
| C9 | no committed theme files at all | zero findings; no error |
| C10 | a theme file under the test-fixture exemption path | not treated as a live theme file during the live scan |
| C11 | two committed theme files (a second added) | both are scanned with no code change (generic discovery) |

## Non-goals (explicit, to bound scope)

- The rule does NOT check whether the theme's palette matches the design tokens
  (token-to-theme FIDELITY is a separate, unbuilt rule -- OUT OF SCOPE).
- The rule does NOT adjudicate a borderline business-meaning question; genuinely
  ambiguous cases are a human ruling (Principle V), not an auto-verdict.
- The rule does NOT declare a governed per-rule severity table; severity is
  observed per branch (ratified 044).
- The rule does NOT (in this slice) assert REQUIRED-key presence unless/until a
  human defines the required set (spec ## Clarifications OPEN item).

## Constitution ties

- Principle I: violation is ERROR -> non-zero exit (fail closed).
- Principle V: categorical scan only; boundary is a recorded human ruling.
- Principle VII: generic glob + generic vocabulary; no tenant/example literal.
- Principle VIII: stdlib-only over committed text; no live dependency.
- Principle IX: ASCII, UTF-8-no-BOM, short paths; no secrets read.
- Ratified 044: one declared id; observed severity.
