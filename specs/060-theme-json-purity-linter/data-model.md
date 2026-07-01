# Phase 1 Data Model: Theme JSON Purity Linter

The rule is a pure function over committed text. There is no persisted state and no
new stored entity. The "data model" here is the in-memory shapes the rule reads and
produces.

## Inputs (read, never mutated)

### RuleContext (existing)
The framework-provided context passed to every rule. The fields this rule uses:
- `tracked_files`: the committed file paths (used to discover theme files
  generically by suffix).
- `repo_root`: base path used to open a discovered file.

The rule treats the context as read-only (immutability rule) and returns a new list
of findings.

### Theme file (read)
A committed styling-defaults JSON document (surface 3). Conceptually a nested tree
of JSON objects/arrays. The rule cares about:
- the file's location (for the finding locator);
- the set of KEY NAMES present and their nesting path (for the categorical scan).
The rule inspects key names and structural positions, NOT free-text data values
(FR-005: a value that happens to equal a forbidden word is not a violation).

## Vocabulary (module-level generic constants -- derived from the contract)

### FORBIDDEN key categories (source: docs/powerbi/theme-json.md MUST-NOT list)
- DAX / measures / calculated columns / calculated tables
- metric definitions
- semantic-model relationships
- source mapping
- sentiment thresholds / rules (the RULE, not the color)
- data validation

### ALLOWED styling vocabulary (source: docs/powerbi/theme-json.md MAY list)
- color palette (data colors + named accent/structural colors)
- fonts (family + sizes)
- visual defaults (gridlines, borders, padding, data-label toggles, title styling)
- page / wallpaper defaults
- filter-pane defaults
- sentiment COLORS (the color that means good/caution/bad -- the color only)

**Boundary note (Principle V, OPEN)**: The exact literal key names that make up the
FORBIDDEN constant, and whether any keys are additionally asserted as REQUIRED, is a
human ruling recorded in the spec ## Clarifications. The constant is a single named
seam pending that ruling; the plan does not freeze its literal membership.

## Output

### Finding (existing framework type)
The rule emits zero or more findings. Each finding carries:
- `rule_id`: the single freshly-allocated identifier this rule declares.
- `severity`: `ERROR` for a forbidden-key violation and for a malformed-file
  finding.
- `message`: human-readable, naming the category/key that violated the contract (or
  that the file could not be parsed). ASCII only.
- `locator`: `file#/json/pointer` -- the file path plus the key path to the
  offending key, using the existing JSON-pointer-style locator convention.

## Invariants

- One finding per distinct forbidden-key occurrence (FR-004); no masking.
- Zero findings for an allowed-only file (FR-006) and for the current committed
  starter theme (SC-003).
- Fixtures under the test-exemption path are excluded from the live scan (FR-010).
- No tenant/example/brand-specific literal appears in any constant (FR-007).
