# Phase 0 Research: Capability Inventory

All NEEDS CLARIFICATION from Technical Context are resolved below. Each decision cites
the committed source or the owner ruling that settles it.

## D1 -- Surface: skill, not CLI verb

**Decision**: Ship as a `.claude/skills/capabilities/SKILL.md` wrapping a pure builder
module. Add NO top-level CLI verb.

**Rationale**: `docs/roadmap/decisions/cli-verbs-vs-skill-driven.md` (Option B, ratified
by the repo owner 2026-07-07) explicitly rejected growing the CLI verb surface for
discoverability -- it names "`seshat --help` lists everything" as the rejected Option-A
trait and sanctioned exactly ONE deliberate CLI addition (`status`, spec 109). Specs
110-113 each ship discoverability as docs/skills with "NO new CLI verb". A `capabilities`
verb would reopen a closed human decision. Owner reconfirmed the skill form in Session
2026-07-11.

**Alternatives considered**: (a) a CLI verb as the original brief asked -- rejected, see
above; would need the same owner ratification `status` got, out of scope. (b) a
regenerated golden doc via `retail <verb>` (mirrors `manifest.py`) -- rejected, the
regenerator IS a CLI verb.

## D2 -- Output mechanism: pure live builder, no committed golden

**Decision**: A pure Python builder joins `manifest ⋈ feeders` and renders BOTH forms
deterministically on each invocation. NO rendered output is committed.

**Rationale**: FR-007 + SC-003 require byte-identical machine output; a hand-authored or
agent-composed render is not deterministic. FR-003/FR-015 forbid re-declaring feeder
facts; a hand doc copying rule titles is the duplication the feature exists to kill.
Determinism + no-duplication force a pure sorted builder. The repo's golden pattern
(`rules-manifest.json`) regenerates via a `_DISPATCH` verb this feature cannot add;
rendering LIVE needs no regeneration verb, honoring the ratified decision by
construction. Owner chose "no committed golden" (Session 2026-07-11).

**Alternatives considered**: committed golden JSON + non-verb regenerator (pytest
`--update` or `scripts/`) -- viable and diff-reviewable, but adds a regeneration surface
and a ratify-ledger note; owner declined in favor of the simpler live render.

## D3 -- Source of truth: new YAML manifest owns gap fields; reference the rest

**Decision**: `docs/capabilities/capabilities.yaml` (hand-authored) is the canonical
authority for CLASSIFICATION, owning only fields no feeder records (`state` finer
buckets, `authority`, `requirements`, provenance). Structured facts are REFERENCED from
their existing owners, never copied.

**Rationale**: Agent survey confirmed NO single committed file enumerates the full
surface with the required fields, and `requires-db` / `advisory-vs-gated` / shipped-
`state` have no structured home (prose only). `.seshat/kit-source.yaml` self-scopes to 7
verbs + hard-stops (its FR-005 forbids run-state) and must not be overloaded. YAML matches
the hand-authored-ledger convention (`shipped-ideas.yaml`, `status-claims.yaml`); only
generated goldens are JSON.

**Feeders (authoritative for their own facts)**:

| Feeder | Owns (referenced, not copied) |
|--------|-------------------------------|
| `docs/rules/rules-manifest.json` | rule ids + titles |
| `.claude/skills/*/SKILL.md` frontmatter | skill name + description (a FRONTMATTER'D SKILL.md is a declaration, admissible evidence per FR-002; a bare dir is not) |
| `.seshat/kit-source.yaml` | orchestration verbs + hard-stops |
| `docs/roadmap/roadmap.md` | F-numbered ship status (SHIPPED / PARTLY / not) |
| `docs/quality/status-claims.yaml` | doc-anchored `claimed-status: built|planned` (reconciled by rule SC1 against tracked-file existence) |
| `src/retail/cli/__init__.py` `_DISPATCH` | wired CLI commands (a command's shipped-ness IS its dispatch wiring) |

## D4 -- Truthfulness oracle: fail-closed test, sits ON the risk

**Decision**: An independent pytest oracle (NOT a `retail check` rule) that reads ground
truth from the feeders and FAILS when:
(a) a manifest entry references a feeder fact that does not exist (orphan);
(b) a real wired capability of a covered kind is absent from the manifest (unlisted);
(c) `state: shipped` is not POSITIVELY backed by a ship-status feeder (fail-closed:
    "not contradicted" != "confirmed"; a spec-dir's existence is NOT shipped evidence);
(d) `provenance: publicly-released` is not backed by committed external-release evidence
    (fail-closed).

**Rationale**: The feature's whole value is truthfulness; the danger is a FALSE "shipped"
/ "released". Repo lesson `verifier-must-sit-on-the-risk`: the oracle must check the real
danger, reading ground truth INDEPENDENTLY of the builder's rendering (no circularity).
Non-goals forbid a `retail check` gate; a fail-closed CI test is not a governance gate
(Principle I row in plan.md).

**Alternatives considered**: reference-existence-only oracle -- rejected (the skeptic
found it lets a spec-only item render `shipped`). A `retail check` rule -- rejected
(violates non-goals; duplicates what the test proves).

## D5 -- `readiness_stage`: optional, reference an existing stage source, no consolidation

**Decision**: `readiness_stage` is OPTIONAL, defaulting to "not stage-scoped" (most
capabilities -- the plugin, doctor, the inventory itself -- are not stage-scoped). For the
FEW stage-scoped entries, valid stage tokens are the snake_case `stages.*` KEYS of the
SINGLE canonical source `templates/readiness-status.yaml` (`source_ready` ...
`publish_ready`). One source, not two -- `docs/readiness/readiness-model.md` is prose
+ diagram carrying stage names in two token forms (Title-Case vs snake_case), so it is
NOT the validation source; `templates/readiness-status.yaml`'s structured keys are.

**Rationale**: FR-004 flagged the seven-stage vocab has no single canonical data file (a
tuple duplicated across `status_surface.py`, `run_next.py`, `rules/readiness_status.py`).
FR-003's "reference, don't re-declare" is satisfied by REFERENCING one existing committed
source, NOT by consolidating the three tuples -- that consolidation is scope creep
(CLAUDE.md YAGNI) and touches shipped modules this read-only feature must leave unchanged.

**Alternatives considered**: consolidate the three tuples into one canonical module --
rejected as out-of-scope; a separate refactor spec if ever wanted.

## D6 -- Category vocabulary: reuse product-modules.md, don't invent

**Decision**: The categorical buckets reuse `docs/architecture/product-modules.md`'s
existing classification (Core Authority / Official Workflow Skill / Product Module /
Execution Adapter / Maintenance Automation, + read-only/artifact-writing/execution-capable
levels). The display groups (Available now / Requires DB-or-extra / Agent-companion /
Human-gated / Deferred) MAP onto it.

**Rationale**: Agent survey found `product-modules.md` already owns this vocabulary as an
author-facing contract; inventing a parallel taxonomy would create a second source of
truth. Reuse keeps one vocabulary.

**Alternatives considered**: a fresh taxonomy -- rejected (parallel-truth risk).
