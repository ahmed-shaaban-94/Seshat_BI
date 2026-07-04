# Research: Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker (089)

Phase 0 -- precedent survey, input-source confirmation, and the deferred-capability
note. Every read below was of a committed artifact in this worktree; no live DB, no
Power BI/PBIP surface, no network was touched.

## Precedents (what SHIPPED to reuse, what to stay distinct from)

- **RS1 -- readiness-status contradiction linter** (`src/retail/rules/readiness_status.py`,
  spec 002/ADR 0004). SHIPPED. This is the DIRECT DESIGN PRECEDENT and HR3's sibling, not
  its replacement. REUSE, verbatim in shape: (a) the `_INSTANCE_RE` glob over
  `mappings/<table>/readiness-status.yaml`; (b) `_owner_is_valid` / `_OWNER_SHAPE_RE` /
  `_AUTHORITY_CLASSES` -- the "Person Name (authority_class)" shape and its four classes
  (`analyst`, `governance`, `data_owner`, `metric_owner`) -- reused AS-IS for
  `stale_review.reviewer` (FR-007a); HR3 does not redefine a second owner shape; (c) the
  `_APPROVAL_REQUIRED` frozenset (`mapping_ready`, `semantic_model_ready`, `dashboard_ready`,
  `publish_ready`) plus the file-source `source_ready` approval carve-out, reused AS-IS to
  scope FR-011's "approval-bearing stage" set; (d) the `_finding()` helper shape (rule id +
  message + locator) and lazy `import yaml` inside the rule body, keeping `yaml` out of the
  stdlib-only `retail check` static-core import chain (Principle VIII). STAY DISTINCT: RS1
  checks structural self-consistency of ONE file at a single point in time and has no notion
  of TIME; it never compares an evidence path's git-commit date to an approval's `at:` date,
  and never reads `stages.source_ready.status` as an implication for OTHER stages. HR3 adds
  that time dimension. RS1 is UNCHANGED by this feature (FR-015) -- no field, no branch, no
  behavior of `readiness_status.py` is edited. A table can be simultaneously RS1-clean and
  HR3-flagged (both rules run independently over the same file).

- **Source Drift Detector (design-only)** (spec `015-source-drift-detector`, roadmap F014,
  `docs/readiness/source-drift.md`). SHIPPED AS A DESIGN DOC, no runtime. Defines the
  nine-class drift taxonomy and the Downstream-invalidation rule this feature enforces
  (`source-drift.md:74`: "A `blocked`/`warning` drift at Source Ready makes downstream `pass`
  stages ... SUSPECT ... The detector FLAGS this; it MUST NOT silently demote or auto-`pass`
  any downstream stage"). HR3 CONSUMES the signal exactly as that doc already defines it is
  observable today: the committed `stages.source_ready.status` field. This feature does NOT
  reopen spec 015, does NOT add a drift class, does NOT build a `retail drift` CLI or live
  re-profile comparator, and does NOT compute drift itself -- it is the missing ENFORCEMENT
  half of the sentence source-drift.md:74 already wrote.

- **HR1 -- cross-star conformed-dimension gate** (spec `087-conformed-dimension-readiness`,
  reserved id HR1, not yet implemented at time of writing -- design-stage plan/research only).
  SHIPPED AS A DESIGN (plan+research, same stage as this feature). This is the STRUCTURAL
  precedent for how a second `HR*`-family static rule is planned in this repo: a
  Constitution-Check table naming I/III/IV/V/VI/VII/VIII/IX + hard rule #9, a Project
  Structure section listing the exact six-surface wiring lockstep
  (`src/retail/rules/__init__.py`, `tests/unit/test_rules_wiring.py::EXPECTED_RULE_IDS`,
  `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
  `docs/quality/rule-count-claims.yaml`, `docs/glossary.md`'s rules table + "Currently N
  rules" anchor) as IMPLEMENT-STAGE edits, and a `rule_<id>.py` module-naming convention.
  HR3 mirrors that scaffolding. STAY DISTINCT: HR1 reconciles CROSS-TABLE dimension shape
  agreement via a new human-authored manifest (`docs/quality/conformed-dimension-map.yaml`);
  HR3 reconciles WITHIN-TABLE time-staleness of an already-`pass` stage via git-commit-date
  comparison. Different subject, different (and non-conflicting) reserved id, no shared file.
  HR3 does not edit `rule_hr1.py` or `conformed-dimension-map.yaml`.

- **F027 Approval Console** (`.claude/skills/approval-console/`, spec `021`). SHIPPED. The
  tool a named human uses to RECORD a decision (an approval, a demotion, or -- per this
  feature -- a `stale_review` reaffirmation) into the committed artifacts. HR3 raises the
  finding that gives the Approval Console something to act on; HR3 itself writes nothing back
  and this feature does not edit the Approval Console skill.

- **F028 Evidence Pack Generator / F035 Approval Evidence Pack**
  (`.claude/skills/evidence-pack-generator/`, `.claude/skills/approval-evidence-pack/`).
  SHIPPED. Compose human-facing packets from already-recorded evidence and blockers. Once
  HR3 exists, a `stale_pass` finding is one more recorded blocker those packs may cite; this
  feature does not edit either pack generator's template or section list.

- **Readiness Viewer / retail-control-room / run-next-readiness**
  (`.claude/skills/readiness-viewer/`, `.claude/skills/retail-control-room/`,
  `.claude/skills/run-next-readiness/`). SHIPPED. Display or aggregate ALREADY-recorded
  state; they compute or render, they do not create new findings. A `stale_pass` HR3 finding
  becomes one more fact those read-only tools can surface once it exists; this feature does
  not change any of their logic.

## Input-source confirmation (what HR3 reads on disk)

| Input | Confirmed on-disk source | Notes |
|-------|--------------------------|-------|
| Per-table state file | `mappings/<table>/readiness-status.yaml` | same `_INSTANCE_RE` glob as RS1; the canonical per-table artifact (ADR 0004) |
| Drift signal | `stages.source_ready.status` inside that file | `warning`/`blocked` = drift-triggered staleness (FR-002); no separate drift-report parse required |
| Approval record | `approvals[]` entries (`stage`, `owner`, `at`) inside that file | RS1 already validates owner shape; HR3 additionally reads `at` and, when a stage has 2+ entries, uses the LATEST `at` (Clarifications) |
| Evidence citation | `stages.<stage>.evidence[]` string entries | free text today (confirmed against the canary below); only entries containing an extractable repo-relative path token are "cited evidence paths" (Clarifications) |
| Evidence recency | git-commit history of a cited path | via a NEW `gitutil.py` helper (see Project Structure in plan.md); NOT filesystem mtime (FR-004, Principle IX) |
| Rule mechanism | `@register` / `RuleContext` / `Finding` / `Severity` / `is_test_path` in `src/retail/core.py` + `src/retail/registry.py` | reused unchanged; nothing new at the mechanism layer |

## The SC-006 canary, verified against the real committed file (load-bearing)

SC-006 requires "0 new HR3 findings" against the current committed state. The spec names
`mappings/retail_store_sales/readiness-status.yaml` as the canary. Because HR3 is the first
rule in this repo to compare a git-commit DATE against an approval date, this canary was
checked LITERALLY -- using `git log -1 --format=%aI -- <path>` (AUTHOR date, per FR-004's
ratified default: HR3 MUST NOT use committer date, since a rebase/cherry-pick can rewrite it
long after the content was actually written) -- not assumed clean by inspection, and not
assumed equal to committer date without checking. Both `%aI` and `%cI` were pulled for
EVERY date-bearing row in the table below (not only the FR-003-in-scope ones) so the
"(identical)" claim in each row is a measured fact, not an inference from the in-scope
subset:

| Stage | `approvals[].at` (latest) | Cited evidence token | Token shape | Author date (`%aI`) | Committer date (`%cI`) | Same-day-or-earlier than approval? (author date governs, FR-004) |
|-------|---------------------------|----------------------|-------------|----------------------|--------------------------|-------------------------------------|
| `mapping_ready` | `2026-06-25` | `mappings/retail_store_sales/source-map.yaml` | file, resolves in `ctx.tracked_files` | `2026-06-25T15:33:29+03:00` | `2026-06-25T15:33:29+03:00` (identical) | YES (same calendar day) |
| `semantic_model_ready` | `2026-06-25` | `mappings/retail_store_sales/metrics/` | **directory-shaped token** (trailing slash, no extension) | `2026-06-26T13:31:14+03:00` | `2026-06-26T13:31:14+03:00` (identical) | N/A -- case (b) prose (directory token), out of FR-003 scope regardless of date field |
| `semantic_model_ready` | `2026-06-25` | `powerbi/RetailStoreSales.SemanticModel` | **directory-shaped token** (no trailing slash; contains a dot before `.SemanticModel`, which a naive "has an extension" heuristic misreads as a file) | `2026-07-03T02:45:57+03:00` | `2026-07-03T02:45:57+03:00` (identical) | N/A -- case (b) prose, out of FR-003 scope regardless of date field |
| `dashboard_ready` | `2026-06-25` | `mappings/retail_store_sales/design/` | **directory-shaped token** | `2026-07-03T14:21:10+03:00` | `2026-07-03T14:21:10+03:00` (identical) | N/A -- case (b) prose, out of FR-003 scope regardless of date field |
| `publish_ready` | (no approval recorded; stage is `blocked`, not `pass`) | -- | -- | -- | -- | FR-011/FR-003 do not apply -- not a `pass` stage |

**Why author date vs. committer date does not change the SC-006 verdict on THIS canary**: for
every commit touching every path in the table above (all six date-bearing rows, not only the
three in FR-003's scope), author date and committer date are identical -- no rebase or
cherry-pick has ever touched these commits, confirmed by pulling both fields for each path,
not assumed. The only path actually in FR-003's scope (`source-map.yaml`, an exact
tracked-file match; the three directory-shaped tokens are case (b) prose and never reach the
date comparison regardless of which date field governs) lands on the same calendar day as its
approval under EITHER date field. FR-004's choice of author date over committer date is a
reproducibility safeguard against a FUTURE rebase silently manufacturing staleness on this or
any other table, not a change that happens to flip this particular canary's verdict today.

**Finding**: if HR3's path-extraction rule treated every one of these tokens as a "cited
evidence path" the way it treats `source-map.yaml`, three of the four would fire FR-003
(approval-lag staleness) against the CURRENT committed tree, and SC-006 would fail on day one.
This is not a hypothetical edge case invented for this research -- it is the literal state of
the one canary the spec names.

**First-draft resolution (superseded -- kept here as a documented near-miss)**: an initial
draft scoped "cited evidence path" to a token resolving to a FILE in `ctx.tracked_files`, and
treated a directory-shaped token (ends in `/`, or matches no file but IS a prefix of one or
more tracked files) as prose. That correctly clears `metrics/`, `design/`, and
`...SemanticModel`. But re-tracing EVERY token the canary's `evidence[]` entries actually
produce (not just the tokens intended as citations) surfaced two further adversarial cases
that draft did NOT clear:

- `semantic_model_ready`'s third evidence line -- `"retail-semantic-check 5-step verdict =
  pass: retail check exit 0 (D1-D8/C1/R1/G6), gold_ready=pass, all 5 model measures bind
  1:1 to an approved contract"` -- tokenizes (on whitespace/punctuation) to include
  `D1-D8/C1/R1/G6`, a rule-id range that CONTAINS a `/` but is not a path at all. Under the
  first-draft rule (any non-resolving, non-directory slash-bearing token is unresolvable),
  this would have fired FR-013 against `semantic_model_ready`, which IS one of RS1's
  `_APPROVAL_REQUIRED` stages and IS `pass` here -- a real SC-006 break.
- `gold_ready`'s reconciliation evidence line contains `1,552,071.00`; splitting on `,`
  (the tokenizer's punctuation set) yields a bare token `071.00`, which superficially matches
  a "trailing extension" shape heuristic. `gold_ready` is a MECHANICAL stage (no
  `approvals[]` concept), so this only matters if FR-013 is not scoped away from mechanical
  stages -- confirming the scope question flagged below is load-bearing, not cosmetic.

**Corrected resolution, verified against both adversarial tokens (final; see
data-model.md's numbered algorithm)**: gate every check on RESOLUTION against
`ctx.tracked_files`, never on shape alone, and scope the FR-013 unresolvable-citation check
to the same approval-bearing stage set as FR-003/FR-011:

- `D1-D8/C1/R1/G6` contains a `/` but is NEITHER an exact tracked-file match NOR a prefix of
  any tracked file (no tracked path begins with `D1-D8/`) -- under the corrected algorithm's
  case (c), a slash-bearing token that resolves to NEITHER a real file NOR a real tracked
  directory is prose, not a citation. Verified: `git ls-files` contains no path with prefix
  `D1-D8/`. Produces ZERO findings.
- `071.00` contains no `/` and matches no tracked file, so it is discarded at the step-2
  candidate filter before resolution is even attempted; AND `gold_ready` is a mechanical
  stage, outside FR-013's approval-bearing scope entirely, so this token is never inspected
  a second way either. Produces ZERO findings, doubly.
- `mappings/retail_store_sales/metrics/` and `mappings/retail_store_sales/design/` are real
  tracked-directory prefixes (case (b)) -- prose, zero findings, as in the first draft.
- `powerbi/RetailStoreSales.SemanticModel` does not resolve to an exact tracked file (no
  such single file exists; it is a directory), and IS a real tracked-directory prefix once a
  trailing `/` is considered (`powerbi/RetailStoreSales.SemanticModel/.platform` etc. are
  tracked) -- case (b), prose, zero findings.
- `mappings/retail_store_sales/source-map.yaml` is an exact tracked-file match -- case (a),
  the one real citation in this table, correctly IN scope for FR-003 (see the "strictly
  later" tie discussion below).

A third adversarial case, checked the same way: `dashboard_ready`'s evidence line lists
bare filenames alongside a directory token -- `"design authored: mappings/
retail_store_sales/design/ (dashboard-layout.md, visual-list.md,
visual-contract-binding-map.md)"`. The bare names (`dashboard-layout.md`,
`visual-list.md`, `visual-contract-binding-map.md`) contain no `/` and do NOT exactly match
any entry in `ctx.tracked_files` (the tracked files are the fully-qualified
`mappings/retail_store_sales/design/dashboard-layout.md` etc. -- confirmed via `git
ls-files`, which returns no bare-named match). Under step 2's candidate filter (a
no-slash token is a candidate only if it matches a tracked file outright), these are
discarded as prose before resolution, never reaching FR-013. `dashboard_ready` IS
approval-bearing and `pass`, so this case is directly in HR3's scope and had to be checked,
not assumed.

This keeps the canary's directory tokens AND all three adversarial cases (rule-id range,
formatted decimal, bare co-listed filenames) out of scope on both FR-003 and FR-013, while
`source-map.yaml` (a real file) stays in scope and correctly produces ZERO findings under
the same-day tie rule. See data-model.md "Cited evidence path extraction rule" for the
exact algorithm; this table and the three adversarial tokens above are its confirming
fixture -- every `evidence[]` line across every `pass`, approval-bearing stage in the
canary has now been traced, not merely the lines this research initially thought of as
citations.

The `mapping_ready` / `source-map.yaml` pair is the one case in the canary that DOES fall
inside FR-003's scope, and it is same-calendar-day (approval `2026-06-25`, commit
`2026-06-25T15:33:29+03:00`) -- exactly the tie case the Clarifications resolved as NOT stale
("strictly later"). This is the confirming case for the "strictly later" default, not a
loophole: had the commit landed even one minute into `2026-06-26`, the canary itself would be
stale under FR-003, and that would be the CORRECT signal (source-map.yaml would in fact have
changed after its approval) -- not a false positive to design around.

**Assumptions.md / unresolved-questions.md**, the other two file-shaped tokens appearing
elsewhere in the same table's evidence (e.g. `mapping_ready`'s second evidence line), commit
at `2026-06-25T15:33:29+03:00` -- the same commit as `source-map.yaml` -- and are likewise
same-day, non-stale.

## The "N most recent approvals[] entry" default, verified against the real file

The canary carries exactly one `approvals[]` entry per stage today (no stage has been
re-approved yet), so the "latest `at` wins" rule (Clarifications) is inert on the current
tree -- confirmed by inspection of `approvals[]` in `mappings/retail_store_sales/
readiness-status.yaml`. It is exercised by unit-test fixtures at implement time, not by the
canary.

## Deferred capabilities NOT assumed

- **F016 Power BI execution adapter** (official Power BI MCP / connection; `pbi-cli` no
  longer preferred) is gated + LAST and is assumed NOT to exist. HR3 never invokes it and
  never reasons about a live Power BI/PBIP surface.
- **Live DB / `retail validate`**. HR3 opens no database connection. "Evidence recency" is a
  git-commit-history read of already-committed text, never a live re-profile, never a
  `retail drift` CLI (none exists -- source-drift.md is design-only, per its own scope note).
- **A drift-detection runtime**. HR3 does not compute drift; it reads the already-recorded
  `stages.source_ready.status` field exactly as `docs/readiness/source-drift.md` defines it
  is observable today. No new drift class, comparator, or re-profile trigger is introduced.
- **A new readiness stage or approval shape beyond `stale_review`**. No eighth stage, no
  change to the four existing statuses, no change to `approvals[]`'s existing shape.
- **Auto-demotion or auto-(re-)pass of any kind**. HR3 never writes `readiness-status.yaml`
  (FR-005); the human is the only actor who can clear a finding, either by editing the
  stage's own status/evidence or by recording a shape-valid, correctly-dated `stale_review`
  entry.

## Honesty limitation (recorded, not designed around)

HR3's approval-lag check (FR-003) can only date-compare evidence that resolves to an EXACT
tracked FILE (case (a) in data-model.md's extraction algorithm). A stage whose `evidence[]`
cites its evidence ONLY as a directory token (case (b)) gets ZERO FR-003 coverage -- not
because its evidence is fresh, but because a directory reference does not name a specific
file HR3 can date-compare, and the Clarifications correctly forbid guessing which file
inside it "is" the evidence. This is a real, load-bearing gap on the canary itself, not a
hypothetical: `semantic_model_ready` cites `mappings/retail_store_sales/metrics/` (last
commit `2026-06-26`) and `powerbi/RetailStoreSales.SemanticModel` (last commit
`2026-07-03`), and `dashboard_ready` cites `mappings/retail_store_sales/design/` (last
commit `2026-07-03`) -- ALL three postdate their shared `2026-06-25` approval by one to
eight days, yet HR3 raises NO finding for either stage, because neither cites a single
resolving file. Of the three approval-bearing `pass` stages on this canary, only
`mapping_ready` receives any real FR-003 coverage at all, and even that coverage passes
only via the same-day tie ("strictly later," not "on or after").

**This is a coverage boundary, not a bug to fix.** Turning a directory token into a citation
(e.g. "compare against the latest-committed file inside it") would let HR3 silently pick
which file inside a directory "is" the evidence -- a call this feature does not have the
authority to make, and one that would also reintroduce the `D1-D8/C1/R1/G6`-class false
positive this research spent its effort ruling out. The correct fix, if this gap is judged
unacceptable, is a FUTURE change to how evidence is CITED (e.g. authoring convention:
evidence entries should name the specific file(s), not the containing directory) -- a
documentation/authoring-discipline fix, not an HR3 parsing fix. Until then: **an HR3-clean
`retail check` run proves the absence of the two conditions HR3 CAN see (recorded drift, and
a resolving-file citation dated before its approval) -- it does not prove "this stage's
evidence is fresh" for a stage that cites only directories.** This limitation should be
stated plainly wherever HR3's guarantee is described (e.g. in the eventual rule docstring
and the glossary rules-table row) so a clean HR3 run is never over-read as a freshness
assurance it cannot actually give -- the same false-assurance concern hard rule #9 and this
feature's own purpose exist to guard against.

## Open (Principle V -- NOT resolved here; carried to the owner)

- **Whether `stale_review` may also clear a drift-triggered (FR-002) finding**, in addition
  to the approval-lag (FR-003) finding FR-007 already scopes it to. The spec's Clarifications
  section records this as explicitly OPEN ("OPEN owner ruling") and directs that, until
  answered, HR3 implements FR-007 exactly as worded: `stale_review` clears FR-003
  (approval-lag) findings only; an FR-002 (drift-triggered) finding clears only via a change
  to `stages.source_ready.status` or the stale downstream stage's own status, never via
  `stale_review`. This plan does NOT settle the question -- it records the PENDING DEFAULT
  (FR-007-as-written) the owner may later broaden, mirroring how spec 087 carried its own
  Q-APPROVAL-SEAM question forward as an explicit OPEN item rather than silently deciding it.
