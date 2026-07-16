---
description: Run the governed autonomous readiness loop until the next human gate
---

Load the `seshat-bi` skill and run its governed agent-driven loop. Each
iteration: obtain the one allowed next action (prefer the MCP governor's
`seshat_get_next_action` when wired, else the installed
`seshat next --format agent`), perform exactly that one action, then re-run
`seshat check` and report what changed. Repeat until the next action is a
named-human decision: package it for review (`seshat_prepare_approval_request`
when the governor is wired) and STOP with the concrete blockers. Never grant
an approval, skip or route around a blocked gate, invent a mapping or metric
meaning, or emit a readiness/confidence score. If `seshat` is unavailable,
stop and explain the install step instead of simulating the loop.
