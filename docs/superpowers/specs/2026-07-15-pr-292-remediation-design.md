# PR 292 Remediation Design

## Goal

Make the decision change impact-map pull request mergeable by repairing the
capability-inventory omission and the two correctness defects found in review,
while splitting the large implementation into narrowly focused modules.

## Chosen approach

Use a small composition module for the public projection API, a graph-builder
module for evidence-backed artifact discovery and edge construction, and a
graph-walker module for traversal.  The public CLI and output shape remain
unchanged.  This reduces the CodeScene size and complexity findings without
changing the authority boundary: all modules remain read-only and compose the
existing Decision Store, explorer, readiness, artifact identity, disclosure,
and guard authorities.

## Correctness rules

Reference matching will tokenize normalized identifiers and paths rather than
searching for a raw substring.  A request for `sales` therefore cannot match
`net_sales`, and `gold.fact` cannot match `gold.fact_catalog` unless an exact
token or path segment is present.

Traversal will retain a path-local ancestry chain for every queued path.  A
previously affected node may still be queued through a different sibling path,
so an edge that closes a reachable cycle is recorded even when its target was
visited earlier.  A separate affected-node set keeps the external result
deduplicated.

## Inventory registration

Add one truthful `impact-map` record to the capabilities manifest, referencing
the wired dispatch command and the feature specification.  It is a read-only,
agent-runnable, non-stage-scoped capability; it grants no approval or
readiness-state change.

## Tests and verification

Add focused regressions for prefix/subsequence false matches and a cycle reached
through sibling paths.  Verify the inventory oracle, affected impact-map tests,
the full unit suite, and the repository governance command before pushing the
PR branch.
