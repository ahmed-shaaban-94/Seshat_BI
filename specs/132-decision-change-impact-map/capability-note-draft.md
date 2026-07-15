# Capability Note Draft: Decision Change Impact Map

Status: DRAFT for later owner-gated capability-ledger review.

The shipped surface is one narrow, read-only `impact-map` projection over an
approved Decision Store record. It composes the existing Decision Store,
artifact identity, decision evidence-staleness signal, explorer lineage,
readiness projection and blocker classifier. It separates direct and transitive
artifacts, cites the committed evidence path for each followed edge, records
unresolved scope tags, missing edges, cycles, and dangling supersession pointers,
and writes disclosure-scanned JSON and Markdown only beneath `.seshat-output/`.

The surface creates no new authority, readiness stage, approval, status model,
or persistent graph. It performs no execution or governed-state mutation and
emits no numeric impact assessment. Adding this note does not edit or ratify
`docs/capabilities/capabilities.yaml`; that remains a later named-owner action.
