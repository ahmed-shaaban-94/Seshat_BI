<!--
=============================================================================
 approval-evidence-pack.md  --  the generic copy-me PRE-approval evidence pack
=============================================================================
 Seshat BI -- Product Module F035 (Approval Evidence Pack for the Named-Human
 Stage Gate). Spec: specs/063-approval-evidence-pack/.
 Composer skill: .claude/skills/approval-evidence-pack/SKILL.md.

 WHAT THIS IS
   A GENERIC, copy-me shape for ONE (table, stage) PRE-approval decision packet.
   A named human about to sign a stage gate reads one ordered, fully-traceable
   document instead of hunting across a dozen scattered artifacts. The pack
   SURFACES committed evidence; it OWNS no truth; it carries an EMPTY approval
   slot only the named human fills; it carries NO numeric score and NO count.

 THE F024 MODULE CONTRACT (banner -- reused by the skill; see SKILL.md for the
   fully-filled declaration)
   - Authority category: Product Module
   - Capability level: `artifact-writing` (exactly one; per docs/architecture/
     product-modules.md -- reads Core Authority, writes one derived artifact,
     executes nothing).
   - READS (never writes): docs/readiness/<stage>-ready.md,
     mappings/<table>/readiness-status.yaml, mappings/<table>/metrics/*.yaml
     (the AL1 assumption signal, per contract), docs/quality/parked-on.yaml.
   - WRITES: this one derived pack at
     mappings/<table>/approval-evidence-pack-<stage>.md.
   - EXECUTES: none.
   - FORBIDDEN (the matrix says NO): no writing approvals[], no moving a stage to
     `pass`, no granting an approval, no defining/approving business meaning, no
     numeric confidence/health/maturity score, no completeness/"N of M" count, no
     DB / Power BI / PBIP read, no deferred adapter (F016) or spec-only runtime
     (F031-F033).

 HOW TO USE
   The skill FILLS one copy of this shape as
   mappings/<table>/approval-evidence-pack-<stage>.md. Fill every <ANGLE-BRACKET>
   placeholder from a committed source; a missing/unreadable source becomes an
   explicit BLOCKER naming the path (never fabricated). ASCII only, UTF-8 no BOM
   (use `--` and `->`, no glyphs); short repo-relative paths (Windows 260-char
   budget). Delete this comment banner in a filled copy. GENERIC -- no
   worked-example (C086 / retail_store_sales) label, grain key, or column name.
=============================================================================
-->

# Approval Evidence Pack -- <table> / <stage>

> PRE-approval decision packet for ONE stage gate of ONE table. Every claim below
> cites the committed artifact it came from. This pack writes NOTHING back: it
> ends with an EMPTY approval slot only the named human fills (or surfaces an
> already-recorded approval read-only, or states that no stage-approval applies
> for a mechanical gate). No score, no count.

## (H) Header

- **Table:** `<schema.table or table id>`  *(from mappings/<table>/)*
- **Stage:** `<stage_key>`  *(one of: source_ready | mapping_ready | silver_ready |
  gold_ready | semantic_model_ready | dashboard_ready | publish_ready)*
- **Generated at:** "<YYYY-MM-DD>"  *(quoted; authoring time; ASCII)*
- **Sources read (every claim traces to one of these):**
  - `docs/readiness/<stage>-ready.md`  *(gate requirements)*
  - `mappings/<table>/readiness-status.yaml`  *(state + blockers + approvals[])*
  - `mappings/<table>/metrics/*.yaml`  *(AL1 assumption signal, per contract)*
  - `docs/quality/parked-on.yaml`  *(blocking parked-on edges)*

## (1) What this gate requires

Summarised/linked from `docs/readiness/<stage>-ready.md` -- NOT re-authored here.

- **Gate:** <one-line name of the stage gate, from the readiness doc>
- **Requirements (linked):** see `docs/readiness/<stage>-ready.md`
  - <requirement 1 -- link/point, do not re-decide>
  - <requirement 2 -- link/point, do not re-decide>
- **Required owner / approval:** <the named human/role the readiness doc says must
  sign, or "mechanical gate -- no stage approval" per FR-015>

## (2) Readiness state -- selected stage + all prior stages

Read VERBATIM from `mappings/<table>/readiness-status.yaml`. Surface the selected
stage and every stage BEFORE it in the seven-stage order; NEVER a stage after it
(FR-020). Status is one of `not_started | blocked | warning | pass` -- never a
status the source does not record.

| Stage (in order, up to selected) | Status (verbatim) | Evidence (committed paths) |
|----------------------------------|-------------------|----------------------------|
| `<prior_stage_1>` | `<status>` | `<evidence[] paths, or -- >` |
| `<prior_stage_2>` | `<status>` | `<evidence[] paths, or -- >` |
| `<selected_stage>` | `<status>` | `<evidence[] paths, or -- >` |

> If the path up to and including the selected stage is not all `pass`, the gate is
> not yet clear -- see blockers below. (A stage is entered only when the prior is
> `pass`; readiness-pipeline.md.)

## (3) Open blockers

Read from the source `blocking_reasons[]` (per selected stage and cross-cutting).
Each line traceable to its source (FR-005). List every one; invent none.

- `<blocker text, verbatim>` -- source: `mappings/<table>/readiness-status.yaml`
  (`<stage>.blocking_reasons[]` or top-level `blocking_reasons[]`)
- <... or, if none recorded: "None recorded in readiness-status.yaml.">

## (4) Unresolved assumptions (per metric contract)

The AL1 assumption-ledger signal, surfaced PER offending contract (FR-021). Each
item names the specific contract file and the recorded contradiction. The pack
NEVER resolves the assumption (Principle V) and NEVER re-runs the AL1 rule -- it
surfaces the recorded result.

- Contract: `mappings/<table>/metrics/<Metric>.yaml` -- recorded contradiction:
  <verbatim/pointed, not re-decided>
- <... or, if none: "No unresolved assumption recorded in the metric contracts.">

## (5) Blocking parked-on edges

Read from `docs/quality/parked-on.yaml`. Surface only edges that block this
table's stage; cite each edge's recorded blocker, doc, and evidence (FR-007).

- Edge `<id>` -- blocked: `<blocked>` parked on `<parked_on>`; doc: `<doc>`;
  evidence: `<evidence>`
- <... or, if none: "No blocking parked-on edge for this table's stage.">

## (6) Pending contracts

<!-- FR-008 RESOLVED (Clarifications 2026-07-02): "pending contracts" = the
     mappings/<table>/metrics/*.yaml contracts whose readiness.status is not
     `pass` (the existing on-disk set, read-only). No new artifact; the KPI-layer
     Seeded/Planned markers are NOT reinterpreted here. A missing/unreadable
     contract is a BLOCKER (FR-011), never fabricated. -->

Contracts under `mappings/<table>/metrics/` whose `readiness.status` is not `pass`,
read-only. Business-rule content is LINK-AND-CITE ONLY (FR-013): cite the recorded
ruling's own text + its source path; NEVER paraphrase a grain / rollup / segment /
PII decision into fresh wording.

- Contract: `mappings/<table>/metrics/<Metric>.yaml` -- `readiness.status`:
  `<status != pass>`; see that file for the recorded ruling (not restated here).
- <... or, if none: "No pending contract (all readiness.status == pass), or none
  present -- see blockers if the metrics dir is missing.">

## (7) Approval slot -- exactly one of three forms

<!-- Choose the ONE form that matches the source; delete the other two in a filled
     copy. The module is structurally INCAPABLE of filling an empty slot, appending
     to approvals[], moving a stage to `pass`, or granting an approval (FR-009,
     FR-010). -->

### Form A -- EMPTY approval slot (selected stage is an approval gate; approvals[] has no entry)

Only the named human fills this. The module leaves it blank.

```yaml
approvals:
  - stage: "<selected_stage>"
    owner: ""        # <- the named human writes their name/role here
    at: ""           # <- the named human writes the date here (quoted YYYY-MM-DD)
```

### Form B -- RECORDED (read-only; approvals[] already has an entry for this stage)

Surfaced from source; NO fresh slot is offered and nothing is overwritten (FR-016).

- **Already signed:** owner `<owner>` at "<YYYY-MM-DD>"
  -- source: `mappings/<table>/readiness-status.yaml` `approvals[]`.

### Form C -- NOT APPLICABLE (mechanical gate: silver_ready / gold_ready)

No named-human stage approval applies (FR-015). Surface the mechanical gate result
instead of a human-approval slot.

- **No stage-approval slot applies** for this mechanical gate. Mechanical result:
  `<status from readiness-status.yaml for this stage>` -- source:
  `mappings/<table>/readiness-status.yaml`.

---

<!-- END OF PACK. No numeric confidence/health/maturity score anywhere; no
     completeness / "N of M" count (FR-012). Readiness is only the four statuses +
     evidence + blockers. The module wrote only this file; it edited no source
     artifact, wrote no approval, and moved no stage to `pass`. -->
