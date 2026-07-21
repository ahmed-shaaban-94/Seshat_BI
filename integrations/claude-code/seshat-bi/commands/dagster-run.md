---
description: Execute one governed Dagster orchestration job (fail-closed)
---

Load the `dagster-workflows` skill. Run
`seshat dagster run --job <full_sequence_job|through_gold_job>` (add
`--table <table>` to scope one mapped table) and interpret the result. Choose
the Bronze source with `--source-mode`: the default `csv` lands a raw
`<table>.csv` and OWNS/reloads `bronze.<table>`; `existing-bronze` is the
non-destructive DB-first mode -- it verifies an already-loaded `bronze.<table>`
READ-ONLY (zero Bronze writes) and starts the gated tail from there. Use
`existing-bronze` when Bronze already lives in the warehouse (loaded by BCP,
COPY, an external ETL, or a prior tool) and must not be dropped or reloaded;
never export Bronze back to a CSV just to feed the default path. The run
executes ONLY already-approved steps behind every gate: a failed gate halts all
downstream assets and the command exits 3 -- report that as the honest
fail-closed signal with the recorded blocking reason and named owner, never as
something to bypass. The mapping gate, semantic-model approval, and
publish_ready are READ from committed artifacts; never edit them to make a run
green (approval is a named human's action). Run evidence is rendered to
`orchestration/dagster/run-evidence/<run-id>.md`; cite it. Without database
credentials the DB-touching assets record a deferred boundary -- say so
truthfully. A green run is evidence, never a readiness `pass`.
