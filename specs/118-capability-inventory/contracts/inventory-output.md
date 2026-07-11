# Contract: Inventory Output (the two rendered forms)

The builder renders BOTH forms deterministically from `manifest ⋈ feeders`. Read-only;
nothing is written. ASCII-only, UTF-8 no BOM. No numeric score in either form.

## Form 1 -- grouped human-readable (default)

Capabilities grouped under fixed categorical headings, in the fixed group order, each item
sorted by `id`. Each item shows its entry point (command or documentation) and its
per-record axes. A GAP marker (`[unrecorded]`) is shown for a genuinely unset field; the
surface NEVER rounds up to a stronger claim.

```text
Seshat BI -- capability inventory (read-only; grants nothing, computes no readiness)

Available now
  retail check -- Static governance gate over committed text.
    surface: cli | authority: agent-runnable | requires: none | provenance: publicly-released
    entry: retail check | doc: docs/rules/README.md

Requires database or optional dependency
  retail validate -- Live data checks against a materialized table.
    surface: cli | authority: agent-runnable | requires: database, optional-dependency
    entry: retail validate | doc: ...

Agent / companion
  dbt advisory adapter -- Advisory dbt transformation adapter (not connected).
    surface: execution-adapter | authority: advisory | provenance: locally-verified
    entry: (none) | doc: .claude/skills/dbt-transformation-adapter/SKILL.md

Human-gated
  approval console -- Records a named human's stage approval.
    surface: skill | authority: human-gated
    entry: (human action) | doc: ...

Deferred / not shipped
  F016 Power BI execution adapter -- Materialize/publish an approved model. [deferred]
    surface: execution-adapter | requires: optional-dependency | provenance: [unrecorded]
    entry: (none) | doc: docs/quality/parked-on.yaml
```

Rules:
- Group order FIXED: Available now; Requires database or optional dependency; Agent /
  companion; Human-gated; Deferred / not shipped.
- Each capability appears in EXACTLY ONE group (data-model precedence).
- An empty group is stated as empty ("(none)"), never fabricated to fill.
- No "N of M", no percentage, no maturity/confidence level anywhere (FR-009).

## Form 2 -- machine-readable (stable)

A deterministic JSON array (stdlib `json`, sorted keys, sorted by `id`, `indent=2`),
byte-identical over unchanged committed inputs (FR-007 / SC-003). One record per
capability with the CLOSED field set; feeder-owned facts (e.g. a rule title) are resolved
from the feeder at render time, not copied from the manifest.

```json
[
  {
    "id": "retail-check",
    "name": "retail check",
    "summary": "Static governance gate over committed text.",
    "state": "shipped",
    "authority": "agent-runnable",
    "surface": "cli",
    "requirements": [],
    "provenance": "publicly-released",
    "readiness_stage": "not-stage-scoped",
    "command": "retail check",
    "documentation": "docs/rules/README.md",
    "group": "available-now"
  }
]
```

Rules:
- Field set is CLOSED: no undeclared field, no missing required field (schema-testable).
- Deterministic: same committed inputs => byte-identical bytes (sorted keys + id sort +
  fixed indent + trailing-newline discipline).
- `group` is the derived primary group (from the fixed precedence), so an agent can route
  without re-deriving it.
- The form is selected by the module entry point's flag: `python -m
  retail.capability_inventory` (grouped human, default) vs `python -m
  retail.capability_inventory --format json` (machine). The `SKILL.md` instructs the agent
  to RUN that command. This is a `python -m` module entry point, NOT a `_DISPATCH`/argparse
  subcommand -- it does not appear in `seshat --help` / `retail --help`, so it adds no CLI
  verb (FR-001).
