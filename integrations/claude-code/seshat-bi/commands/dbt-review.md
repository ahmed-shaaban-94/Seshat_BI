---
description: Review normalized dbt evidence and stop at the human gate
---

Load the `dbt-workflows` skill. Review the normalized evidence returned by a
governed build. When an existing local run directory is supplied, validate it
with `seshat dbt inspect-run --table <table> --artifacts <run-directory>
--format json`. Report parity and blocking reasons, then stop for a named human;
never grant readiness or switch away from migrations.
