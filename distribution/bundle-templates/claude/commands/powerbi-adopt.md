---
description: Adopt an existing PBIP project through the governed assess/scaffold path
---

Load the `seshat-bi` skill and follow its existing-PBIP route. Run the
read-only `seshat adopt-pbip assess --project <dir> --format text` first and
report its assessment digest plus one governed next action. Scaffolding
requires a human to review that exact digest: only then run
`seshat adopt-pbip scaffold --project <dir> --accept-assessment <digest>` in a
clean existing Git worktree. A `.pbix` file is a conversion boundary -- save it
as PBIP in Power BI Desktop first. Never treat assessment output as approval,
mapping, or readiness.
