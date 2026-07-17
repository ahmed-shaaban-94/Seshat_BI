---
description: Run the fixed governed dbt shadow build under an accepted plan
---

Load the `dbt-workflows` skill. Require the exact reviewed digest, then run
`seshat dbt build --table <table> --accept-plan <digest> --format json`.
Report the normalized evidence path and blockers. If the digest or live
profile is absent, stop; never replan implicitly or bypass the accepted-plan
gate.
