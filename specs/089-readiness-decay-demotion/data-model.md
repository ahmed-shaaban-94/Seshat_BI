# Data Model: Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker (089)

Phase 1 output. Every shape below is generic (Principle VII -- no C086/pharmacy/retail
domain specifics leak into the schema); the one worked example that appears is confined to
a "Worked example" callout, clearly marked as illustration, not requirement.

## Entities

### 1. `stale_pass` finding (in-memory only; never persisted)

The `retail check` `Finding` HR3 raises. Reuses the existing, unchanged `Finding` dataclass
from `src/retail/core.py` -- no new finding schema is introduced.

| Field | Value for HR3 | Notes |
|---|---|---|
| `rule_id` | `"HR3"` | the reserved id this feature owns |
| `severity` | `Severity.ERROR` | both stale conditions fail CLOSED (FR-001); there is no WARNING-only HR3 finding for staleness itself (the distinct sibling findings below use ERROR too, for the same fail-closed reason) |
| `message` | one of the message shapes below | human-readable, names the stage and (where applicable) the evidence path and both dates -- never a score |
| `locator` | `"<repo-relative-path-to-readiness-status.yaml>:stages.<stage_name>"` | mirrors RS1's `loc` convention (`{rel}:stages.{stage_name}`) so tooling that already parses RS1 locators can parse HR3's the same way |

**Message shapes** (four distinct finding kinds, all rule id `HR3`, distinguished by
message text so a human/tool can tell them apart without a second field):

1. **Drift-triggered** (FR-002): `stage {stage!r} is pass but stages.source_ready.status is
   {drift_status!r} (drift signal, docs/readiness/source-drift.md); the human must
   re-confirm or demote this stage`.
2. **Approval-lag** (FR-003): `stage {stage!r} is pass but evidence path {evidence_path!r}
   was committed {evidence_date} which is after its approval ({approval_date}, owner
   {owner!r}); the human must re-approve or record a stale_review entry`.
3. **Unresolvable evidence citation** (FR-013): `stage {stage!r} cites evidence path
   {evidence_path!r} which does not resolve to a tracked file; the citation cannot be
   date-compared`.
4. **Unparseable approval date** (FR-014): `stage {stage!r} has an approvals[] entry with an
   unparseable or missing 'at' date ({raw_value!r}); the approval-lag check cannot run for
   this stage`.
5. **Invalid `stale_review` reviewer shape** (FR-008, mirroring RS1's C4 message):
   `stale_review entry for stage {stage!r} has invalid reviewer {reviewer!r}; record the
   reviewer by name + authority class (e.g. "Ada Lovelace (data_owner)") -- a bare role, a
   name without a class, or an unknown class does not count toward clearing a stale_pass
   finding`.

A table with N stale downstream `pass` stages under FR-002 produces N separate findings
(one per stage), never one rolled-up finding (FR-002, hard rule #9).

### 2. `stale_review` entry (new, additive, persisted top-level key)

A new, OPTIONAL, ADDITIVE top-level list key in `readiness-status.yaml`, structurally
parallel to the existing `approvals[]` list. A file without this key is valid and unaffected
(back-compatible with every already-filled instance, per FR-006).

```yaml
# Generic shape -- illustrative field names only, no domain specifics.
stale_review:
  - stage: "<stage_name>"              # one of the seven stage names (same vocabulary
                                        #   RS1 already validates: source_ready,
                                        #   mapping_ready, silver_ready, gold_ready,
                                        #   semantic_model_ready, dashboard_ready,
                                        #   publish_ready)
    evidence: "<repo-relative-path>"   # the SPECIFIC evidence path being reaffirmed --
                                        #   must match the path token that triggered the
                                        #   FR-003 finding this entry targets
    reviewer: "<Person Name> (<authority_class>)"
                                        # REQUIRED shape-valid form, reusing RS1's
                                        #   _owner_is_valid / _OWNER_SHAPE_RE verbatim;
                                        #   authority_class in {analyst, governance,
                                        #   data_owner, metric_owner}, the same four
                                        #   RS1 already defines -- no new vocabulary
    at: "YYYY-MM-DD"                   # ISO date; must be on or after the triggering
                                        #   evidence path's git-commit date to clear
                                        #   the finding (FR-007)
    note: "<optional short free-text note>"
                                        # OPTIONAL; not validated for shape, carries no
                                        #   score
```

**Field semantics**:

- `stage` + `evidence` together identify the SPECIFIC (stage, evidence-path) pair an entry
  reaffirms -- this is the same granularity FR-003's finding is raised at, so one
  `stale_review` entry clears exactly one such finding, never a whole stage's or a whole
  table's worth of findings at once (no batch-clear; hard rule #9 discipline extends to "no
  rolled-up clearing" as well as "no rolled-up finding").
- `reviewer` MUST pass the same shape check RS1 already applies to `approvals[].owner`
  (`"Person Name (authority_class)"`, case/whitespace/hyphen-insensitive on the class,
  rejecting a bare role token, a name with no class, a role masquerading as a name, or an
  unknown class). An entry whose `reviewer` fails this check does NOT clear the finding
  (FR-007a) and produces its own distinct finding instead (FR-008; message shape 5 above).
- `at` MUST be on or after the triggering evidence path's git-commit date to clear the
  finding (FR-007b); an entry dated strictly before does not clear it (Edge Cases; the
  finding still fires).
- **Scope of what `stale_review` can clear (OPEN item, PENDING DEFAULT per plan.md)**: an
  entry clears an FR-003 approval-lag finding for its named (stage, evidence) pair only. It
  does NOT clear an FR-002 drift-triggered finding under this plan -- that finding clears
  only via a human edit to `stages.source_ready.status` or the stale stage's own status. This
  is the spec's OPEN Clarifications item, implemented per FR-007's literal wording, not
  broadened here.
- The agent MAY draft `stage`, `evidence`, and `note` for a human to complete but MUST NOT
  supply or infer `reviewer`, and MUST NOT commit the entry without a human-supplied
  `reviewer` name (FR-009, Principle V).

### 3. Source-drift signal (existing; read-only for HR3)

Not a new entity -- the already-defined `stages.source_ready.status` field, exactly as
`docs/readiness/source-drift.md` specifies it. HR3 reads the literal string value
(`not_started` | `blocked` | `warning` | `pass`, the same four-word vocabulary RS1
validates) and treats `warning` or `blocked` as the drift signal for FR-002. HR3 does not
redefine, recompute, or add a field to this signal.

### 4. Approval record (existing; read-only for HR3)

Not a new entity -- the already-defined `approvals[]` entry (`stage`, `owner`, `at`, optional
`note`) RS1 already validates for shape. HR3 additionally parses the `at` field as a date and,
when a stage carries more than one `approvals[]` entry, uses the entry with the LATEST `at`
as "that stage's matching entry" for the FR-003 comparison (Clarifications default). HR3 does
not alter RS1's ownership/shape validation.

### 5. Cited evidence path (derived; computed by HR3, not persisted)

Not a stored entity -- a value HR3 derives at check-time from a stage's `evidence[]` list.
This is the entity requiring the most care, because the real committed canary
(`mappings/retail_store_sales/readiness-status.yaml`, see research.md) demonstrates that a
naive "any string containing a slash" extraction rule misfires against directory-shaped
tokens already present in a `pass` stage's `evidence[]` today.

#### Cited evidence path extraction rule (the exact algorithm)

**Design note (why resolution, not shape, is the gate)**: an earlier draft of this
algorithm gated the FR-013 unresolvable-citation check on "looks path-shaped" (contains `/`,
or ends in a plausible extension). Tracing that draft against every token the canary
actually produces -- not just the tokens intended as citations -- found two false-positive
classes: a prose token like `D1-D8/C1/R1/G6` (a rule-id range, from
`semantic_model_ready`'s evidence in `mappings/retail_store_sales/readiness-status.yaml`)
contains `/` but is not a path at all, and a formatted number like `1,552,071.00` splits (on
`,`) into a token `071.00` that superficially matches a "trailing extension" heuristic. Both
would have misfired as unresolvable citations under a shape-only gate, breaking SC-006
against the very canary this design must stay clean against. The corrected rule below gates
on RESOLUTION against real tracked paths at every step, never on shape alone -- shape is
used only to decide whether a token is a plausible candidate worth resolving at all, never
to decide the finding.

For each string entry `e` in a stage's `evidence[]`:

1. **Tokenize.** Split `e` on whitespace and the characters `()[]{}"';,` (the punctuation a
   free-text evidence sentence commonly wraps a path in, e.g. `"...(mappings/foo/
   source-map.yaml)"`). Note this also splits a formatted number like `1,552,071.00` into
   separate tokens (`1`, `552`, `071.00`) -- expected, and handled by step 3's resolution
   gate, not by trying to special-case numeric formatting in the tokenizer.
2. **Candidate filter (cheap pre-filter only, decides nothing on its own).** A token is a
   CANDIDATE for path resolution only if it contains at least one `/`, or matches an entry
   in `ctx.tracked_files` outright. A token with no `/` and no exact tracked-file match
   (e.g. `071.00`, `retail`, `check`, `0`, `(S1-S7);`) is discarded here as prose and
   receives no finding of any kind -- it is never passed to step 3.
3. **Resolve against `ctx.tracked_files`, in this order:**
   - **(a) Exact file match**: the token, taken as a repo-relative path, exactly matches an
     entry in `ctx.tracked_files`. This IS a "cited evidence path" -- proceed to FR-003's
     date comparison.
   - **(b) Real-directory-prefix, no exact match**: the token does NOT exactly match any
     tracked file, but the token (with a trailing `/` appended if it does not already end in
     one) IS a literal prefix of one or more entries in `ctx.tracked_files` -- i.e., it names
     a directory that genuinely exists in this repo's tracked tree (e.g.
     `mappings/retail_store_sales/design/`, which is a real prefix of three tracked `.md`
     files). This is treated as PROSE, not a citation -- a bare directory reference is not
     itself "the evidence," the files inside it are, and this feature does not attempt to
     pick one. Produces NEITHER an FR-003 date comparison NOR an FR-013 finding.
   - **(c) vs (d) -- the ONE discriminator**: for a token containing `/` that is not itself
     an exact tracked-file match (a) and is not itself a real tracked-directory prefix (b),
     the sole question is whether a LEADING PORTION of the token, up to and including some
     `/`, matches a real tracked-directory prefix. Concretely: does the token's parent path
     (everything before its final `/`-separated segment) name a directory that genuinely
     contains at least one tracked file?
     - **(c) NO -- parent path is not a real tracked directory**: e.g. `D1-D8/C1/R1/G6` --
       no tracked path begins with `D1-D8/`, so this token's parent (`D1-D8/C1/R1`) is not a
       real directory either. Treated as PROSE, not an unresolvable citation. This is a
       direct application of the Clarifications' own adopted wording -- "only an
       `evidence[]` entry containing an extractable repo-relative path token that RESOLVES
       TO A PATH IN `ctx.tracked_files` is a cited evidence path" -- a token whose parent
       directory does not exist in the tracked tree at all has nothing in
       `ctx.tracked_files` for it to resolve relative TO; it is exactly the free-text case
       the Clarifications already carve out, not a narrower reading invented here. FR-013
       ("a path token IS present but does not resolve") presumes the token was plausibly
       heading somewhere real; case (c) is not that -- it is indistinguishable from any
       other narrative fragment that happens to contain a slash, and flagging it would
       manufacture exactly the false-positive class the Clarifications exist to prevent
       (confirmed against `D1-D8/C1/R1/G6` in research.md).
     - **(d) YES -- parent path IS a real tracked directory, but the full token still does
       not resolve to any tracked file inside it**: e.g. a citation
       `mappings/retail_store_sales/design/removed-file.md` where
       `mappings/retail_store_sales/design/` is confirmed (via case (b)'s own prefix test)
       to be a real tracked directory, but `removed-file.md` is not among the files tracked
       there. THIS is the FR-013 unresolvable-citation case: the token named something
       plausibly real (a file inside a directory that does exist) and it is not there --
       the "looks like a citation but the file is absent" case FR-013's own text describes.
4. **Scope of FR-013 to approval-bearing stages.** Because FR-013's purpose (a stale
   citation to a deleted evidence file) only has bite where FR-003's date-comparison already
   applies, this design scopes the FR-013 unresolvable-citation check to the SAME
   approval-bearing stage set FR-011 already defines for FR-003 (RS1's `_APPROVAL_REQUIRED`
   plus file-source `source_ready`). A mechanical stage's (`silver_ready`, `gold_ready`)
   evidence is never resolution-checked by HR3 at all -- those stages are covered only by
   the drift-triggered check (FR-002), which does not read `evidence[]`. This keeps a
   mechanical stage's numeric/prose-heavy evidence (e.g. `gold_ready`'s reconciliation totals)
   entirely out of HR3's path-resolution logic, closing the `071.00`-class hole at the scope
   level as well as the resolution-gate level.

This algorithm is a PARSING/SCOPE rule over the existing free-text `evidence[]` shape (per
the Clarifications), not a schema change -- `evidence[]` stays a bare list of strings
(FR-015 stays intact). It is deliberately CONSERVATIVE toward case (c): a rule that is
unsure whether a slash-bearing token is a real citation or prose treats it as prose rather
than risk a false-positive `retail check` failure against innocuous text -- the cost of that
conservatism is that a truly novel path pattern outside the tracked tree (impossible by
definition, since a citation to something not in the repo can never resolve to a tracked
file anyway) is never falsely flagged either.

**Worked example (illustrative only, not a requirement -- Principle VII)**: given the
evidence entry `"mappings/retail_store_sales/source-map.yaml (grain=transaction, PK=
transaction_id, gold star: fct_sales + 4 dims + dim_date)"`, tokenizing and resolving each
candidate yields exactly one case-(a) exact match, `mappings/retail_store_sales/
source-map.yaml` -- that is the cited evidence path HR3 date-compares. The remaining
parenthesized prose tokens (`grain=transaction,`, `PK=transaction_id,`, etc.) contain no
`/` and match no tracked file, so they are discarded at the step-2 candidate filter and
never reach resolution at all.

### 6. Evidence git-commit date (derived; computed by HR3, not persisted)

The last commit date, in tracked git history, of a cited evidence path -- obtained via the
new `gitutil.git_last_commit_date(repo_root, path)` helper (`git log -1 --format=%aI --
<path>`, using AUTHOR date, not committer date, in ISO-8601 with offset -- per FR-004's
Clarifications default: author date reflects when the content was actually written, while
committer date can be rewritten by a rebase or cherry-pick long after the fact). Compared at
DAY granularity against
an `approvals[].at` date (which is date-only): the comparison truncates the commit timestamp
to its calendar date component before comparing, so a same-calendar-day commit is never
"strictly later" than a same-day approval, matching the confirmed "same-day is not stale"
default (FR-003's "strictly later" wording; Clarifications). A path with no commit history
(should not occur for a tracked file, but handled defensively) yields `None`, which HR3
treats the same as an unresolvable citation (FR-013's sibling case) rather than crashing or
silently skipping.

## Relationships

```text
readiness-status.yaml (one per table)
├── stages.source_ready.status ──────────────┐
│                                              │ (drift signal, read-only)
├── stages.<stage>.status = "pass" ───────────┤
├── stages.<stage>.evidence[] ────────┐        │
│                                      │        ▼
│                            [cited evidence   HR3 (FR-002, drift-triggered)
│                             path extraction]  │
│                                      │        ▼
│                                      ▼   stale_pass finding (per stale downstream stage)
│                            evidence git-commit date
│                                      │
├── approvals[] (stage, owner, at) ────┤
│         (latest 'at' per stage)      ▼
│                              HR3 (FR-003, approval-lag: commit date > approval date?)
│                                      │
│                                      ▼
│                            stale_pass finding (stage + evidence path + both dates)
│                                      │
└── stale_review[] (stage, evidence, ─┘
    reviewer, at, note)          (clears the matching FR-003 finding IF reviewer is
                                   shape-valid AND at >= evidence commit date; FR-007)
```

## Validation rules summary (cross-reference to functional requirements)

| Rule | Enforced by | FR |
|---|---|---|
| A stage `pass` while `source_ready` is `warning`/`blocked` is a `stale_pass` finding, one per stage | HR3 | FR-002 |
| An approval-bearing `pass` stage whose cited evidence commit-date is strictly later (day granularity) than its latest `approvals[].at` is a `stale_pass` finding | HR3 | FR-003, FR-004 |
| HR3 never writes any file | HR3 (structural: no write call exists in the module) | FR-005 |
| `stale_review` is optional, additive, four/five-field, structurally parallel to `approvals[]` | schema + HR3 read path | FR-006 |
| A `stale_review` entry clears its matching FR-003 finding only if reviewer is shape-valid AND dated on/after the evidence commit date | HR3 | FR-007 |
| An invalid `stale_review.reviewer` produces its own distinct finding, never silently ignored/accepted | HR3 | FR-008 |
| The agent never auto-populates or auto-commits a `stale_review.reviewer` | agent behavior (skill-level, out of rule scope) | FR-009 |
| FR-002 reads only the committed `source_ready.status` field; no live runtime | HR3 (no subprocess/network call for this branch) | FR-010 |
| FR-003 applies only to approval-bearing stages (RS1's `_APPROVAL_REQUIRED` + file-source `source_ready`) | HR3, reusing RS1's frozenset | FR-011 |
| No numeric score anywhere in a `stale_pass` finding or a `stale_review` entry | schema + HR3 | FR-012 |
| A token that resolves into a real tracked directory but not to an exact tracked file within it is a distinct "unresolvable citation" finding; scoped to the same approval-bearing stages as FR-003/FR-011 (a slash-bearing token resolving to NEITHER a real file NOR a real tracked directory is prose, not a citation -- see data-model.md's case (c) vs (d)) | HR3 | FR-013 |
| A missing/malformed `approvals[].at` is a distinct finding, never a skipped stage or a guessed date | HR3 | FR-014 |
| HR3 changes no existing rule's behavior or field meaning; the only new schema surface is `stale_review` | additive design (RS1 untouched) | FR-015 |
| All new files are ASCII, UTF-8 without BOM, short repo-relative paths | authoring discipline | FR-016 |
| No new readiness stage, no new `retail validate` live check, no executor/adapter | design scope (Project Structure) | FR-017 |
