# Contract: the `SESHAT-KIT` fence in `AGENTS.md` / `CLAUDE.md`

Defines how `init` writes generated orientation prose into constitution-governed
files WITHOUT ever touching the hand-authored / constitution-owned content.

## Markers

```text
<!-- SESHAT-KIT START -->
...generated prose projection of kit-source.yaml (verbs, hard-stops, orient)...
<!-- SESHAT-KIT END -->
```

## Producer guarantees (MUST)

- **F1 (fence-only writes)**: `init` writes ONLY the bytes between the two markers
  (inclusive of the markers on first insertion). It never edits, moves, or deletes
  any content outside the fence.
- **F2 (outside-fence invariance)**: For any file that already has a fence, every
  byte outside the fence is identical before and after `init` runs (SC-002). A diff
  is limited to the fenced region.
- **F3 (idempotency)**: Running `init` twice yields exactly one fenced region; no
  duplicate markers, no nested fences (FR-008, SC-003).
- **F4 (safe insertion)**: If the markers are absent, `init` inserts a single fresh
  fenced block at a safe, declared location (end of file or a named anchor). If it
  cannot determine a safe location (malformed file), it REPORTS and STOPS — it never
  rewrites the file to force the fence in (edge case: constitution-owned conflict).
- **F5 (distinct from SPECKIT)**: The `SESHAT-KIT` markers never collide with the
  existing `SPECKIT` fence; both may coexist in the same file untouched by each
  other.
- **F6 (no amendment bypass)**: Because only the fenced region changes, no
  constitution-owned line is ever altered; a constitutional change can never be
  routed through `init` (FR-007).

## Consumer guarantees (MAY rely on)

- **FC1**: The fenced region is a faithful PROSE projection of the same
  `kit-source.yaml` that `compass.yaml` projects. NOTE: this is a DIFFERENT check
  from the YAML byte-exact projection (compass-yaml contract P1). Prose cannot be
  byte-compared to YAML; the drift check for the fence RENDERS the canonical prose
  from `kit-source.yaml` and compares that render to the fenced body. Two mechanisms,
  not one: (a) `compass.yaml == project_yaml(kit-source.yaml)` byte-exact; (b)
  `fenced_body == render_prose(kit-source.yaml)`.
- **FC2**: Anything OUTSIDE the fence is authoritative hand-authored / constitutional
  law and takes precedence over the generated region if they ever appear to conflict.

## Test hooks (for `tasks.md`)

- Snapshot a file, run `init` twice, assert: exactly one fence, outside-fence bytes
  unchanged, fenced body == projection.
- Run `init` on a file with NO markers → assert one fence appended, rest unchanged.
- Run `init` on a malformed/unsafe file → assert STOP + report, file unchanged.
