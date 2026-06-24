# 0004 -- Per-table readiness-status location

- **Date:** 2026-06-25
- **Status:** Accepted
- **Context:** The Tower BI Readiness System (the operating spine) tracks every
  source/table/report across the seven readiness stages with a machine-readable
  status record -- `templates/readiness-status.yaml` is the generic blank
  (four statuses + evidence + blockers, no fake confidence; see
  `docs/readiness/readiness-model.md`). The blank exists, but *where a table's
  filled copy lives* was never settled: no `readiness-status.yaml` instance
  exists anywhere in the repo today (only the template; `mappings/c086/` holds
  the five mapping artifacts but no status file). A batch of readiness features
  drafted together (specs 007/009/011/013/015) each began to **seed or read** a
  per-table status file without a ratified location -- a cross-table convention
  was about to be fixed by a batch default. This ADR settles it before any of
  those specs implement.

## Decision

**A table's filled readiness-status lives at `mappings/<table>/readiness-status.yaml`**
-- co-located with that table's mapping artifacts (ADR 0003), one file per table,
seeded from `templates/readiness-status.yaml`:

```
mappings/
`-- <table>/
    |-- source-profile.md
    |-- source-map.yaml
    |-- assumptions.md
    |-- unresolved-questions.md
    |-- reconciliation-report.md
    `-- readiness-status.yaml      <- this ADR
```

`<table>` is the table id (`snake_case`, short for the Windows MAX_PATH
discipline, Principle IX). The file records ALL SEVEN stages (source -> mapping
-> silver -> gold -> semantic-model -> dashboard -> publish), not only the two
mapping stages -- the location is by-table, not by-stage, so a single file
follows the table through its whole readiness lifecycle. `templates/` keeps the
generic blank; the table's folder holds the filled copy.

## Rationale

- **One table, one working set.** ADR 0003 already made `mappings/<table>/` the
  cohesive per-table working set (the gate's inputs). The readiness-status is the
  *state over* that working set -- it belongs with the artifacts it summarizes, so
  a reviewer finds a table's mapping AND its readiness in one place.
- **Survives all seven stages.** Although the folder is named `mappings/`, the
  status file is explicitly whole-lifecycle. Naming it by table (not by stage)
  means silver/gold/semantic/dashboard/publish state has a home from day one and
  the file is never orphaned when a table passes stage 2.
- **One ratified path for the batch.** Specs 007 (seeds it), 009 (records its
  grain card), 011 (reads it to enforce Gold-before-semantic ordering), 013
  (aggregates it across tables), and 015 (writes the drift outcome into it) all
  bind to the SAME path -- not five independent defaults.
- **No new top-level dir, no `docs/` overload.** Reuses the `mappings/` tree ADR
  0003 created; keeps `docs/` for finished narrative and `warehouse/` SQL-only.

## Alternatives rejected

- **A central `readiness/<table>.yaml` index.** A single dir of all tables' status
  files reads well as a roll-up, but splits a table's state from its artifacts and
  duplicates the table id as both a dir entry and a path. The Data Quality Control
  Room (spec 013) already provides the cross-table roll-up *view* by aggregating
  the per-table files -- the durable state stays with the table.
- **`mappings/<table>/readiness/...` subfolder.** Over-nests a single file and
  lengthens paths against the MAX_PATH discipline.
- **Rename the dir to something stage-neutral (e.g. `tables/<table>/`).** A larger
  churn that would invalidate ADR 0003 and every existing `mappings/<table>/`
  reference for a cosmetic naming gain; rejected for scope. The status file's own
  comment documents that it spans all seven stages despite the `mappings/` name.

## Consequence

- `templates/readiness-status.yaml` references `mappings/<table>/readiness-status.yaml`
  as its filled destination (the prior "location TBD" is replaced).
- Specs 007/009/011/013/015 cite this ADR for the canonical path instead of each
  asserting a batch default; the human-seam approvals the file records remain named
  human actions the agent cannot self-grant (Principle IV/V).
- No status file is back-filled here (C086 included) -- this ADR sets the
  convention; the first table to run the onboarding wizard (spec 007) creates the
  first instance.
- Pairs with ADR 0003 (`mappings/<table>/` mapping artifacts),
  `docs/readiness/readiness-model.md` (the state model), and
  `docs/architecture/readiness-pipeline.md` (the spine on the kit).
