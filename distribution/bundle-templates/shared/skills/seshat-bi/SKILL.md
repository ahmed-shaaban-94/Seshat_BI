---
name: seshat-bi
description: >-
  Route a BI project through Seshat BI's governed seven-stage readiness flow.
  Use when a user asks to inspect a retail source, initialize a Seshat project,
  find the truthful next action, validate readiness evidence, or stop at the
  correct human approval gate.
---

# Seshat BI

Read `../../portable-operating-contract.md` before acting. Inspect the current
workspace and use installed `seshat` commands when available. If the workspace
has no `AGENTS.md`, this skill's portable operating contract still applies.

For subject reasoning, load only the relevant bundled skill:

- SQL and source grain: `bi-sql-knowledge`
- DAX and semantic measures: `bi-dax-knowledge`
- Python/dataframe preparation: `bi-python-knowledge`
- distributed data: `bi-bigdata-knowledge`
- retail KPI meaning and contracts: `retail-kpi-knowledge`
- Power BI design, review, theme, formatting, and PBIP adoption:
  `powerbi-workflows`
- governed dbt prerequisite, plan, shadow build, and evidence review:
  `dbt-workflows`
- governed Dagster preflight, gated medallion runs, and run-evidence review:
  `dagster-workflows`

End with one next action or one blocked stop. Cite evidence and named blockers;
never invent a pass or score.

## Discovering the surface (no name memorization needed)

A user or agent only needs this skill's name; everything else self-describes:

- On Claude Code, `/seshat-bi:help` prints the full installed command map; on
  Codex, the routing list above IS the map (there are no Codex slash
  commands).
- `seshat --help` lists every installed CLI verb, and
  `seshat next --format agent` returns the one machine-readable governed next
  action -- always prefer it over guessing a verb or a stage.
- Use only the commands, verbs, and skill names those surfaces report; never
  invent a name, and if `seshat` is not installed, say so and point to
  `pipx install seshat-bi` instead of simulating output.

## Agent-driven loop (programmatic automation)

For fully programmatic automation, the optional read-only MCP governor
(`seshat mcp --repo <workspace>`, installed via `pipx install "seshat-bi[mcp]"`)
exposes six tools: `seshat_get_status`, `seshat_get_next_action`,
`seshat_explain_blockers`, `seshat_prepare_approval_request`,
`seshat_run_static_check`, and `seshat_export_evidence_pack`.

The governed loop is: get the next action, perform exactly that one action,
re-run the static check, and repeat. When the next action is a named-human
decision, call `seshat_prepare_approval_request` to package it and STOP -- no
tool in this loop grants an approval, advances a stage, or emits a score, and
the loop must never route around a blocked gate.

## Existing PBIP projects

For an existing Power BI Project, first use the installed read-only entry path:

```powershell
seshat adopt-pbip assess --project <PBIP-project-directory> --format text
```

Treat PBIP structure as candidate evidence only. The assessment must not create
or approve mappings, metrics, business meaning, or readiness passes. It returns
one governed next action and an assessment digest. A `.pbix` is a conversion
boundary: save it as PBIP in Power BI Desktop before continuing.

Only after a human reviews the exact digest, and only in a clean existing Git
worktree, may the agent run:

```powershell
seshat adopt-pbip scaffold --project <PBIP-project-directory> --accept-assessment <assessment-digest>
```

This writes at most `.seshat/adoption/pbip-adoption.yaml`; it never initializes
Git, overwrites existing files, grants approval, or advances readiness.

## Resetting / re-running a project

There is no `seshat reset` verb yet (tracked separately). Until it ships, reset
a single table's derived state by hand, preserving its bronze landing, then
re-run readiness from Source.

Remove the table's derived artifacts:

```powershell
Remove-Item -Recurse -Force mappings/<table>
Remove-Item -Force warehouse/migrations/*_create_silver_<table>*.sql
Remove-Item -Force warehouse/migrations/*_create_gold_<table>*.sql
Remove-Item -Recurse -Force dbt/models/staging/<table>
Remove-Item -Recurse -Force dbt/models/marts/<table>
Remove-Item -Recurse -Force dbt/models/audit/<table>
```

This covers `mappings/<table>/` (including its nested `dbt-evidence/`
subfolder -- it lives under the mapping directory, not as a separate
top-level path), the silver and gold migration SQL for that table (plus any
generated `warehouse/gold/` or `warehouse/schema/` outputs), and the three
per-table dbt model folders. Do not touch the bronze landing.

The materialized dagster project under `orchestration/dagster/` is
regenerable rather than hand-edited; if it references the removed table,
regenerate it with `seshat dagster init`.

Stage the deletions before running `seshat check` -- an unstaged delete can
leave the static gate reading stale tracked content. Then verify no residual
state remains:

```powershell
git add -A
Select-String -Path .seshat/manifest.yaml -Pattern "<table>"
seshat next --format agent
```

A hit in `.seshat/manifest.yaml` after the deletions is a real residual-state
risk -- the manifest still believes the table is onboarded even though its
files are gone. `seshat next` should report a truthful fresh Source stage for
the table; if it does not, the reset is incomplete.
