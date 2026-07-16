---
description: Run and interpret the Seshat workspace health check
---

Run the installed `seshat doctor` helper if available (add `--strict` only when
asked) and interpret its findings as workspace health facts. Doctor output
never grants a readiness pass or approval; report failures verbatim with their
remediation hints. If `seshat` is unavailable, explain that the Python package
`seshat-bi` must be installed instead of inventing results.
