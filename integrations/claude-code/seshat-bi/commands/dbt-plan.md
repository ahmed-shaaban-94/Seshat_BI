---
description: Validate a mapping and prepare an immutable dbt execution plan
---

Load the `dbt-workflows` skill. Run `seshat dbt validate --table <table>
--format json`, then only when it passes run `seshat dbt plan --table <table>
--format json`. Present the complete plan and digest for review. Stop without
building; the digest is an execution acceptance token, never an approval.
