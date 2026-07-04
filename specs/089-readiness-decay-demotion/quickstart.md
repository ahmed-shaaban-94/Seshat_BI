# Quickstart: Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker (089)

How an agent or developer exercises HR3 once it is implemented. This is a usage walkthrough
against the FUTURE, built rule -- nothing here runs today; it is the acceptance-scenario
script the implementation must satisfy (cross-referenced to spec.md's User Stories).

## Prerequisite

HR3 is implemented, registered (`src/retail/rules/rule_hr3.py`, wired into
`src/retail/rules/__init__.py`), and the `gitutil.git_last_commit_date` helper exists. A
table has a filled `mappings/<table>/readiness-status.yaml` (any table onboarded via
`retail-onboard-table` / the `source-mapping` skill already has one).

## Scenario 1 -- Drift blocks every downstream `pass` (User Story 1)

1. A table's `readiness-status.yaml` has `mapping_ready`, `silver_ready`, `gold_ready` all
   `pass`, and `source_ready.status: pass`.
2. Run `retail check`. HR3 reports no finding for this table (nothing is drifted).
3. A re-profile records `stages.source_ready.status: warning` (per the source-drift
   taxonomy in `docs/readiness/source-drift.md`) -- a human or the source-drift detector's
   own (currently design-only) process edits this field; HR3 itself never writes it.
4. Run `retail check` again. HR3 now reports THREE separate `HR3` findings, ERROR severity,
   one per stale downstream stage (`mapping_ready`, `silver_ready`, `gold_ready`), each
   naming its own stage and citing the drifted `source_ready` status as the reason. `retail
   check` exits non-zero.
5. Diff the working tree before and after step 4's run: it is empty. HR3 wrote nothing
   (FR-005; SC-003).
6. **Resolution path (human-only)**: the human either re-confirms the stage is still sound
   against the new source shape (re-running that stage's own gate and re-recording its
   `pass` with fresh evidence) or demotes it (editing `status: blocked` with
   `blocking_reasons[]`). Either way, it is the human's edit to the YAML, never HR3's.

## Scenario 2 -- Evidence changed after approval (User Story 2)

1. `mapping_ready` is `pass`, citing `mappings/<table>/source-map.yaml` as evidence, with an
   `approvals[]` entry `{stage: mapping_ready, owner: "Ahmed Shaaban (data_owner)", at:
   "2026-06-01"}`.
2. Run `retail check`. HR3 reports no finding (the evidence's last commit predates or ties
   the approval date).
3. `source-map.yaml` is edited and committed again on `2026-06-20` -- a legitimate follow-up
   change -- but no new `approvals[]` entry is recorded.
4. Run `retail check` again. HR3 reports one `HR3` finding naming `mapping_ready`, the path
   `mappings/<table>/source-map.yaml`, the approval date (`2026-06-01`), and the evidence's
   later commit date (`2026-06-20`).
5. **Resolution path A (re-approve)**: a human adds a fresh `approvals[]` entry for
   `mapping_ready` dated `2026-06-21` (on or after the evidence commit date). Run `retail
   check` again: HR3 no longer reports the finding for this stage (the LATEST `approvals[]`
   entry is the one HR3 compares against).
6. **Resolution path B (reaffirm without a full re-approval)**: see Scenario 3.

## Scenario 3 -- A human reaffirms without a full re-approval (User Story 3)

Starting from Scenario 2 step 4's stale state:

1. Ask the agent: "clear this stale_pass finding for mapping_ready." The agent drafts a
   candidate `stale_review` entry:
   ```yaml
   stale_review:
     - stage: "mapping_ready"
       evidence: "mappings/<table>/source-map.yaml"
       reviewer: "<AWAITING HUMAN NAME>"     # the agent leaves this for the human
       at: "2026-06-21"                       # on/after the evidence's 2026-06-20 commit
       note: "evidence edit was a formatting fix; ruling unchanged"
   ```
   The agent does NOT commit this entry with a placeholder or inferred reviewer name
   (FR-009, Principle V) -- it stops and asks the human to supply `reviewer`.
2. The human supplies the name; the entry becomes:
   ```yaml
   stale_review:
     - stage: "mapping_ready"
       evidence: "mappings/<table>/source-map.yaml"
       reviewer: "Ahmed Shaaban (data_owner)"
       at: "2026-06-21"
       note: "evidence edit was a formatting fix; ruling unchanged"
   ```
3. Commit this entry into `readiness-status.yaml` (a human/agent edit -- HR3 itself never
   writes it).
4. Run `retail check`. HR3 no longer reports the finding for the (mapping_ready,
   `source-map.yaml`) pair. No other file changed and no other finding appeared.
5. **Invalid-reviewer check**: if step 2's `reviewer` were instead `"data_owner"` (a bare
   role token, no name), `retail check` would report a DISTINCT `HR3` finding (invalid
   `stale_review` reviewer shape) and the original `stale_pass` finding would STILL fire --
   an invalid entry never silently counts (FR-008).
6. **Backdated-reviewer check**: if step 2's `at` were `2026-06-15` (before the evidence's
   `2026-06-20` commit), the original `stale_pass` finding would STILL fire -- a
   reaffirmation cannot predate the thing it reaffirms (FR-007b).

## Scenario 4 -- Edge cases an agent should recognize without re-deriving them

- **No `readiness-status.yaml` at all**: HR3 does not fire (nothing to compare); this
  mirrors RS1's existing "absence is not an error" handling.
- **`source_ready` is `not_started` with a downstream `pass`**: HR3's drift check does NOT
  fire (that is an RS1-flagged stage-order oddity, not drift); FR-002 applies only to
  `warning`/`blocked`.
- **An approval-bearing `pass` stage with a directory-shaped or narrative evidence entry**
  (e.g. `"mappings/<table>/metrics/"` or `"retail check exit 0 (S1-S7); PK re-proven
  unique"`): produces NO finding under either FR-003 or FR-013 -- neither is a "cited
  evidence path" under the extraction rule (data-model.md); this is prose, not a citation.
- **A mechanical stage** (`silver_ready`, `gold_ready`) that is `pass` when drift fires at
  Source Ready: the approval-lag check (FR-003) does not apply (no `approvals[]` concept),
  but the drift-triggered check (FR-002) still fires independently -- a mechanical `pass` on
  a drifted source is exactly as suspect as an approval-bearing one.
- **Uncommitted (working-tree) edits to a cited evidence file**: invisible to HR3 until
  committed (Principle IX; HR3 reads committed git history only, like every other rule that
  reasons over `ctx.tracked_files`).

## Verifying the "wrote nothing" guarantee (SC-003) yourself

After any `retail check` run that produces an `HR3` finding:

```bash
git status --porcelain
```

Expected output: empty (or unrelated to the checked table's `readiness-status.yaml`). If
this file ever shows as modified after a bare `retail check` run, that is an HR3 regression
against FR-005/SC-003, not expected behavior.

## Verifying no new false positives against the current repo (SC-006)

```bash
git log -1 --format=%aI -- mappings/retail_store_sales/source-map.yaml
```

(`%aI` = AUTHOR date, per FR-004 -- HR3 never reads committer date, since a rebase or
cherry-pick can rewrite it long after the content was actually written.)

Compare the date portion against `mappings/retail_store_sales/readiness-status.yaml`'s
`mapping_ready` approval date (`2026-06-25`). As of this plan, they are the same calendar
day -- the confirmed "strictly later" default treats this as NOT stale. If a future edit to
`source-map.yaml` lands on a LATER calendar day without a fresh approval, HR3 firing against
this table is the CORRECT signal, not a regression -- re-verify research.md's canary table
before assuming a new HR3 finding here is a bug.
