---
description: Report the truthful per-table readiness status
---

Run the installed `seshat status` helper if available (use `--format json` when
summarizing programmatically) and report each table's recorded stage exactly as
returned. Never invent a stage, upgrade a warning, or emit a numeric
readiness/confidence score; an empty table list is a truthful answer, not an
error. If `seshat` is unavailable, explain that the Python package `seshat-bi`
must be installed.
