# Quickstart: `retail init` first run (the "aha")

The analyst-visible walk-through. This is an AGENT-PERFORMED flow (the agent executes
the `retail-init` skill), NOT a terminal wizard: there is no menu the CLI prompts
for. The `retail init` CLI only writes the substrate and prints the next agent step.
The substrate steps are written but NOT shown as steps — they happen silently under
the profile step.

## The first run (what the analyst experiences, agent-driven)

The agent, performing the `retail-init` skill:

1. **Bootstraps** — runs `retail init`, which writes `.seshat/` + the `SESHAT-KIT`
   fenced regions and prints the next agent step. No prompt, no menu.
2. **Delegates the worked-example offer** to `first-hour-compass`, which presents the
   two committed examples and takes the user's pick:
   - `c086-pharmacy` — build pattern (bronze→silver→gold + live validation), to Gold Ready
   - `retail-store-sales` — full seven-stage spine (metric contracts → dashboard → handoff)
3. **States expectations honestly** (seam wording from `first-hour-compass`, its
   single source): *"the agent handles the sequence and the plumbing; you still own
   grain/uniqueness, PII publish-safety, business rollup/segment, and product
   identity — the agent will STOP and ask on those, never guess."*
4. **Routes into `retail-onboard-table`** for the Stage-1 read-only profile of the
   user's named table.

### With a live DB reachable (`db` extra + DSN) — the aha

```text
Profiling YOUR table (retail-onboard-table Stage-1, read-only)…
  grain candidates: [store_id, sale_date]   (uniqueness 99.8% — review; grain is YOUR call)
  columns: 14  (3 numeric, 2 date, 9 text)
  → next: review the source map, then the mapping gate
You're at: Source → (next) Mapping Ready.
```

The grain/column result comes from `profile.py` running over the DB — produced by the
agent executing `retail-onboard-table`, never by the `init` module.

### With no DB configured — honest degrade (the common first-run case)

```text
Profiling YOUR table…
  [PENDING LIVE PROFILE] — no database configured.
  To enable: pip install 'retail[db]' ; set DATABASE_URL (or ANALYTICS_DB_*) in .env
  I've drafted the source-map / orientation structure so you can keep going.
  → next: fill the source map, or configure a DSN to profile live.
```

No traceback, no faked pass, no invented grain — the flow stays useful (FR-012,
SC-005). This is still more than "the machine describing the machine": the analyst
gets the orientation structure for their own table. There is NO CSV/Excel profiler;
a live result requires a DB (YAGNI — see research R5).

## What happened silently (the backstage substrate)

During bootstrap, `init` also wrote — without showing them as steps:

```text
.seshat/kit-source.yaml        # the canonical source (if not present)
.seshat/compass.yaml           # projected router (verbs incl. retail-onboard-table; NO stage)
.seshat/manifest.yaml          # file inventory + checksums
.seshat/integrations/*.json    # per-harness manifests (claude, codex)
AGENTS.md  / CLAUDE.md          # ONLY the <!-- SESHAT-KIT --> fenced region
```

## Re-running `init` (idempotent)

```text
$ retail init
Already bootstrapped. Re-projecting the SESHAT-KIT regions… done.
(no duplicate fences; your hand-authored content untouched)
→ next agent step: <printed>
```

## Verifying the guarantees (maps to SC / tests)

| Check | Command / assertion | SC |
|-------|---------------------|-----|
| First result on my table (live DB) | agent flow ends on grain candidates + column types | SC-001 |
| Honest degrade (no DB) | flow ends on `[PENDING LIVE PROFILE]` structure, non-error | SC-001 / SC-005 |
| Outside-fence untouched | `git diff` limited to the fenced region | SC-002 |
| Idempotent re-run | second run → one fence, "already bootstrapped" | SC-003 |
| No run-state | `compass.yaml` has no `current_stage` | SC-004 |
| Seam statement shown (single source) | expectation text (from first-hour-compass) precedes profile | SC-006 |
| Harness-neutral | agent enumerates verbs (incl. retail-onboard-table) from `compass.yaml` alone | SC-007 |
| Anti-fork | no restated offer table or seam list in `init` | SC-008 |
| No wizard | `retail init` CLI does not prompt / read stdin / print a profile | FR-001 |
