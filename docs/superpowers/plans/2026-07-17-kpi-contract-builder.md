# kpi-contract-builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an agent-first `kpi-contract-builder` skill that drives the already-shipped spec-124 contract engine to help a human turn a named-but-`[planned]` KPI into a governed, owner-ready project metric-contract — reused engine, no new runtime module.

**Architecture:** A docs-first skill (`SKILL.md` + a worked walkthrough) orchestrates the existing `kpi_contracts.py` (`draft_project_metric_contract` / `finalize_project_metric_contract`) and `kpi_answerability.py`. On first contact (no approved decisions), the skill assesses answerability, lists the exact Decision Store records to get approved, and renders a **preview** including a new skill-composed `field_provenance` block — it does NOT call the engine (which raises `ContractDraftRefused` in that state). Once decisions + a named owner + committed evidence exist, the skill drives `draft_project_metric_contract` (contract blocked-on-gold) and later `finalize_project_metric_contract` (promotion to `pass`). The capability is authored in kit source and projected to Claude + Codex, advertised on the public command surface.

**Tech Stack:** Markdown (SKILL.md, walkthrough, command wrappers), YAML (`kit-source.yaml`, `public-command-surface.yaml`), the shipped Python engine (`src/seshat/kpi_contracts.py`, unchanged), `seshat kit-lint` + `seshat check` as gates. No new Python module; no new `retail check` rule.

## Global Constraints

- Agent-first: no new CLI verb family, runtime engine, readiness stage, or `retail check` rule (verbatim from design §2).
- Reuse the shipped engine: `draft_project_metric_contract`, `finalize_project_metric_contract` (`src/seshat/kpi_contracts.py`) and `derive_answerability` / `render_answerability_artifact` (`src/seshat/kpi_answerability.py`). Do NOT modify these files or `tests/unit/test_kpi_contracts.py`.
- Valid `readiness.status` values are exactly `not_started | blocked | warning | pass`. There is no `draft` status.
- Never invent business meaning, DAX, SQL, gold columns, approvals, owners, confidence scores, or registry entries.
- Registry-known KPI ⇒ existing `generic_kpi_ref`; custom KPI ⇒ `custom: true`, no `generic_kpi_ref`, no registry mutation, no suggested `KPI-MC` id.
- A persisted contract requires an approved `kpi_definition`, all applicable approved policy/governance decisions, and a named eligible owner (`Name (authority_class)` shape). Before those exist: preview + decision-gap list only, no YAML written.
- Missing gold evidence ⇒ `readiness.status: blocked`; source-profile evidence alone cannot justify `binds_to`.
- `field_provenance` is skill-composed in the preview only; the persisted contract keeps the engine's `decision_refs` / `source_evidence`. Origin vocabulary is exactly `knowledge | profile | human | provisional | gap`.
- `field_provenance` must never be written inside a business value.
- Every projection change must leave `seshat kit-lint` and `seshat check` green.
- All authored text is ASCII, UTF-8 without BOM; keep paths short (Windows 260-char limit).

---

### Task 1: Skill body (`SKILL.md`)

The skill's canonical instructions: when to use it, the two-trip flow driving the shipped engine, the first-contact decision-gap behavior, and the hard stops. Docs-only; the gate is a structural self-check + `retail check` staying green.

**Files:**
- Create: `.claude/skills/kpi-contract-builder/SKILL.md`
- Reference (do not modify): `src/seshat/kpi_contracts.py`, `src/seshat/kpi_answerability.py`, `specs/124-generic-kpi-contract-authoring/quickstart.md`, `.claude/skills/business-knowledge-interview/SKILL.md` (structure model)

**Interfaces:**
- Consumes: the shipped engine signatures — `ContractDraftRequest(name, formula_intent, grain, owner, generic_kpi_ref, custom, registry_ids, decisions, authority, required_decision_types, source_evidence, time_additivity=None, unit=None, pii_sensitive=False, required_fields=())` → `draft_project_metric_contract(request) -> dict`; `FinalizationContext(decisions, authority, evidence_freshness, named_human_approval, by_id={})` → `finalize_project_metric_contract(contract, ctx) -> dict`; `ContractDraftRefused` raised when approved decisions/owner/evidence are absent.
- Produces: the skill contract other tasks reference — a `name: kpi-contract-builder` skill whose SKILL.md documents the Trip-1 (preview + decision-gap, no engine call) and Trip-2 (drive `draft`, then `finalize`) behaviors, and the five-value `field_provenance` origin vocabulary. Task 2's walkthrough and Task 3's verb `purpose` must stay consistent with this file.

- [ ] **Step 1: Write the SKILL.md with YAML frontmatter + body**

Create `.claude/skills/kpi-contract-builder/SKILL.md`:

```markdown
---
name: kpi-contract-builder
description: >-
  Help a human turn a named-but-planned retail KPI into a governed, owner-ready
  project metric-contract by driving the shipped kpi_contracts engine (spec 124).
  On first contact, when no approved decisions exist yet, it assesses source
  answerability, lists the exact Decision Store decisions to get approved via
  business-knowledge-interview, and renders a preview with per-field provenance
  -- writing no YAML. Once the approved kpi_definition / policy_ruling decisions,
  a named eligible owner, and committed source evidence exist, it drives
  draft_project_metric_contract (a gold-blocked contract) and, after the gold
  binding is materialized, finalize_project_metric_contract. Use when someone
  asks to draft, author, or start a metric contract for a planned KPI in the
  Seshat BI repo. It never invents business meaning, DAX, SQL, gold columns,
  approvals, owners, a confidence score, or a registry entry; it never promotes
  a KPI to Seeded and never self-grants an approval.
---

# kpi-contract-builder

This skill is the agent-facing front door to the shipped `kpi_contracts` stage.
It does NOT reimplement contract authoring: the engine
(`src/seshat/kpi_contracts.py`) and the answerability scorecard
(`src/seshat/kpi_answerability.py`) already exist (spec 124). This skill DRIVES
them and adds the first-contact assessment the engine deliberately refuses to do.

## When to use

- Someone asks to draft / author / start a metric contract for a KPI that the
  registry marks `planned` (no seeded contract yet), or for a user-supplied
  custom KPI.
- You are at the `kpi_contracts` flow stage (downstream of
  `business-knowledge-interview`, upstream of silver/gold model planning).

Do NOT use it to define DAX (`retail generate`), to check a PBIP model
(`retail semantic-check`), or to run the interview itself
(`business-knowledge-interview`).

## The two-trip flow

The shipped `draft_project_metric_contract` REQUIRES an approved decision, a named
owner, and committed source evidence; without them it raises
`ContractDraftRefused`. So the flow has two trips.

### Trip 1 -- Assess & preview (the common first-contact case; writes nothing)

1. Identify the KPI. Registry-known -> resolve its `generic_kpi_ref: KPI-MC-NN`
   from `skills/retail-kpi-knowledge/registry.yaml` (`custom: false`).
   User-supplied -> `custom: true`, no ref, no suggested id.
2. Consume answerability (read-only): use `derive_answerability` /
   `render_answerability_artifact` for this (KPI, table). Its coverage status is
   an INPUT SIGNAL only (e.g. `Blocked -- missing field` -> a `binds_to` gap).
   Never persist or re-decide it -- contract authoring is a separate concern.
3. Check the Decision Store for the required `kpi_definition` + applicable
   `policy_ruling` decisions. If any is missing/unapproved, do NOT call the
   engine (it will raise).
4. Render a PREVIEW: the contract's business body (clean; no provenance inside
   values) + a `field_provenance` block + the gap list.
5. Emit the decision-gap list: the exact `kpi_definition` / `policy_ruling`
   decisions to get approved (route to `business-knowledge-interview`) and the
   owner to name. STOP. Write no YAML.

### Trip 2 -- Draft & finalize (only when preconditions hold)

6. When an approved `kpi_definition` (+ every applicable approved `policy_ruling`)
   and a named eligible owner exist, build a `ContractDraftRequest` and call
   `draft_project_metric_contract`. The result is a contract with
   `readiness.status: blocked` and the reason `physical gold binding is not
   materialized` -- this is correct and expected until gold exists.
7. On explicit human confirmation, write the returned contract to
   `mappings/<table>/metrics/<Name>.yaml`.
8. After the gold binding is materialized and validated, call
   `finalize_project_metric_contract` with a `FinalizationContext`; it promotes
   to `readiness.status: pass` ONLY when every precondition (binding, decisions,
   fresh evidence, named-human approval) holds. The skill never sets `pass`
   itself.

## field_provenance (preview only; five-value origin vocabulary)

Rendered by this skill in the PREVIEW to show where each field came from. It is
NOT written into the persisted contract (which uses the engine's `decision_refs`
/ `source_evidence`). It is NEVER inserted inside a business value.

    field_provenance:
      formula_intent: { origin: knowledge,   ref: "KPI-MC-02/net-sales.md", resolved: true }
      binds_to:       { origin: profile,     ref: "source-profile.md#net_amount", resolved: false }
      grain:          { origin: human,       ref: "interview 2026-07-13", resolved: true }
      cost_method:    { origin: gap,         ref: "", resolved: false }

Origin is exactly one of: `knowledge` (transcribed from a generic
retail-kpi-knowledge contract), `profile` (proposed from the read-only source
profile -- never self-justifying), `human` (a recorded answer / approved
decision reference), `provisional` (a live unapproved answer shown in preview
only), `gap` (un-inferable). `provisional` and `gap` are never `resolved: true`;
either on a required field means the drafted contract stays `readiness.status:
blocked`.

## Hard stops

- Never self-grant an approval; `owner` and `approvals` are named-human fields.
- Never fabricate a confidence score or percentage.
- Never write DAX / SQL / a silver or bronze binding into any field.
- Never mutate `registry.yaml`; never suggest a `KPI-MC` id for a custom KPI;
  never promote a KPI from Planned to Seeded.
- For a `planned` KPI, contribute identity / concepts / roles / blockers only --
  never an invented `formula_intent`.
```

- [ ] **Step 2: Verify the frontmatter parses and the required sections exist**

Run:
```bash
python -c "import yaml,sys; t=open('.claude/skills/kpi-contract-builder/SKILL.md',encoding='utf-8').read(); fm=t.split('---',2)[1]; d=yaml.safe_load(fm); assert d['name']=='kpi-contract-builder', d.get('name'); assert 'never' in d['description'].lower(); print('frontmatter OK:', d['name'])"
grep -qE '^## The two-trip flow' .claude/skills/kpi-contract-builder/SKILL.md && grep -qE '^## Hard stops' .claude/skills/kpi-contract-builder/SKILL.md && grep -qE 'field_provenance' .claude/skills/kpi-contract-builder/SKILL.md && echo "sections OK"
```
Expected: `frontmatter OK: kpi-contract-builder` then `sections OK`.

- [ ] **Step 3: Confirm no forbidden content leaked into the skill body**

Run (guards against accidentally embedding DAX/SQL as if authored):
```bash
grep -niE '\b(CALCULATE|SUMX|SELECT |INSERT INTO|CREATE TABLE)\b' .claude/skills/kpi-contract-builder/SKILL.md || echo "no forbidden implementation content"
```
Expected: `no forbidden implementation content` (the DAX/SQL tokens appear only inside the "never write" hard-stop sentence, which this pattern does not match because it targets standalone calls; if a match appears, confirm it is only the prohibition sentence).

- [ ] **Step 4: Run the static gate**

Run: `python -m seshat.cli check --repo .`
Expected: exit 0 (adding a skill file adds no rule and must not trip any existing rule).

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/kpi-contract-builder/SKILL.md
git commit -m "feat: add kpi-contract-builder skill body

Agent-facing skill that drives the shipped spec-124 contract engine
(draft/finalize + answerability); documents the two-trip flow, the
first-contact decision-gap behavior, and the preview-only field_provenance
block. No runtime change."
```

---

### Task 2: Worked walkthrough (two cases)

A concrete, copy-followable walkthrough proving the skill end to end on a registry-known KPI (reaching `blocked` on a missing gold snapshot) and a custom KPI (all meaning fields `gap`). This is the skill's test surface, per docs-first (hard rule #8).

**Files:**
- Create: `.claude/skills/kpi-contract-builder/walkthrough.md`
- Reference (do not modify): `skills/retail-kpi-knowledge/domains/inventory.md`, `skills/retail-kpi-knowledge/contracts/net-sales.md`, `specs/124-generic-kpi-contract-authoring/quickstart.md`

**Interfaces:**
- Consumes: the Task-1 SKILL.md two-trip flow and `field_provenance` vocabulary.
- Produces: two named worked cases (`registry-known-inventory-turnover`, `custom-kpi`) the pr-readiness reviewer and any future test fixture can cite as the canonical examples.

- [ ] **Step 1: Write the walkthrough**

Create `.claude/skills/kpi-contract-builder/walkthrough.md`:

```markdown
# kpi-contract-builder -- worked walkthrough

Two end-to-end cases. Both are illustrative and generic (no C086/pharmacy
specifics). Neither writes YAML unless its stated preconditions hold.

## Case A -- registry-known planned KPI (Inventory Turnover)

Context: `skills/retail-kpi-knowledge/domains/inventory.md` marks Inventory
Turnover `Planned (needs COGS + average inventory cost)`; no seeded contract.

Trip 1 (first contact, no approved decisions):
1. Registry lookup: Inventory Turnover -> `generic_kpi_ref: KPI-MC-<NN>`,
   `custom: false`.
2. Answerability for the sales-only source: `Out of scope` or
   `Blocked -- missing field` (no inventory snapshot fact).
3. Decision Store: no approved `kpi_definition` for turnover -> engine would
   raise; do not call it.
4. Preview business body (clean):
   - `formula_intent`: transcribed intent from the knowledge layer if present,
     else omitted.
   - `binds_to`: gold snapshot columns are absent -> left unbound.
   - `readiness.status: blocked`.
5. field_provenance (preview only):

       field_provenance:
         formula_intent: { origin: knowledge, ref: "<knowledge-contract-ref>", resolved: true }
         binds_to:       { origin: gap,       ref: "", resolved: false }   # no gold snapshot
         cost_method:    { origin: gap,       ref: "", resolved: false }

6. Decision-gap list emitted: "Get approved via business-knowledge-interview: a
   `kpi_definition` for Inventory Turnover and a `policy_ruling` for the cost
   method (A6). Name the metric owner." STOP -- no YAML written.

Trip 2 (later, once the above are approved and a gold inventory snapshot exists):
- Build a `ContractDraftRequest` and call `draft_project_metric_contract`; write
  the returned contract (still `blocked` until the gold binding is materialized)
  to `mappings/<table>/metrics/InventoryTurnover.yaml` on confirmation.
- After the gold binding is validated, `finalize_project_metric_contract`
  promotes to `pass` only if every precondition holds.

## Case B -- custom (user-supplied) KPI

Context: a user names "Shrinkage Adjusted Margin", not in the registry.

Trip 1:
1. `custom: true`, no `generic_kpi_ref`, no suggested id.
2. There is NO citable generic meaning -> every meaning field is `gap`:

       field_provenance:
         formula_intent: { origin: gap, ref: "", resolved: false }
         grain:          { origin: gap, ref: "", resolved: false }

3. Decision-gap list: an approved `kpi_definition` for the custom KPI plus each
   applicable `policy_ruling`; a named eligible owner in `Name (authority_class)`
   form (the engine's `owner_shape_ok` requires it for custom KPIs). Note
   explicitly: promotion of this custom KPI into the product registry is a
   SEPARATE owner workflow -- this skill never does it.
4. STOP -- no YAML written until the decisions + owner + evidence exist.
```

- [ ] **Step 2: Verify both cases and the no-write discipline are present**

Run:
```bash
grep -qE '## Case A' .claude/skills/kpi-contract-builder/walkthrough.md && grep -qE '## Case B' .claude/skills/kpi-contract-builder/walkthrough.md && grep -qE 'STOP -- no YAML written' .claude/skills/kpi-contract-builder/walkthrough.md && echo "walkthrough OK"
```
Expected: `walkthrough OK`.

- [ ] **Step 3: Run the static gate**

Run: `python -m seshat.cli check --repo .`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/kpi-contract-builder/walkthrough.md
git commit -m "docs: add kpi-contract-builder worked walkthrough (2 cases)"
```

---

### Task 3: Register the verb in kit source (projects to Claude + Codex)

Add `kpi-contract-builder` as a driven verb in the single source of truth, then regenerate the projections so Claude and Codex both surface it. `kit-lint` is the gate.

**Files:**
- Modify: `.seshat/kit-source.yaml` (the `verbs:` list)
- Regenerated (do not hand-edit): the projected `AGENTS.md` / `CLAUDE.md` fenced regions + `.seshat/compass.yaml` (whatever `kit-lint` compares)
- Reference: `src/seshat/kit_lint.py`, `src/seshat/compass_project.py`

**Interfaces:**
- Consumes: the Task-1 skill name `kpi-contract-builder`.
- Produces: a `verbs[]` entry whose `id` matches the skill name and the public-surface `skill` field in Task 4.

- [ ] **Step 1: Confirm the current projection is clean (baseline)**

Run: `python -m seshat.cli kit-lint --repo .`
Expected: `kit-lint: no projection drift.`

- [ ] **Step 2: Add the verb entry**

In `.seshat/kit-source.yaml`, in the `verbs:` list (after the `source-mapping` entry), add:

```yaml
  - id: kpi-contract-builder
    purpose: "drive the shipped kpi_contracts engine: assess answerability, list the decisions to approve, preview with per-field provenance, then draft/finalize -- never self-grants approval"
```

- [ ] **Step 3: Regenerate projections and re-run kit-lint**

Regenerate the projected surfaces from kit-source (the same mechanism `retail init` uses), then verify no drift:
```bash
python -m seshat.cli kit-lint --repo .
```
If `kit-lint` reports drift, regenerate the projection it names (via `seshat init` / the compass projection path used in this repo) until it reports:
Expected: `kit-lint: no projection drift.`

- [ ] **Step 4: Confirm the verb reaches both integrations**

Run:
```bash
grep -rl 'kpi-contract-builder' integrations/claude-code/ integrations/codex/ 2>/dev/null && echo "projected to both" || echo "CHECK: expected the verb in both integration trees"
```
Expected: matches under both `integrations/claude-code/` and `integrations/codex/`, then `projected to both`. (If this repo projects verbs into a single AGENTS/CLAUDE region rather than per-integration files, confirm the regenerated region lists the verb and treat that as the projection of record.)

- [ ] **Step 5: Run the full static gate**

Run: `python -m seshat.cli check --repo .`
Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add .seshat/ integrations/ AGENTS.md CLAUDE.md
git commit -m "feat: register kpi-contract-builder verb in kit source

Projects the verb to Claude + Codex via kit-source; kit-lint clean."
```

---

### Task 4: Advertise on the public command surface

Add the capability to `public-command-surface.yaml` so the installed `seshat` package/help surface advertises it, with a command wrapper for Claude.

**Files:**
- Modify: `distribution/public-command-surface.yaml`
- Create: `distribution/bundle-templates/claude/commands/kpi-contract-builder.md`
- Reference: the shipped `review` entry (a skill-backed, no-CLI-verb command) as the shape to copy.

**Interfaces:**
- Consumes: the Task-1 skill name; the Task-3 verb id.
- Produces: a surface entry with `name: kpi-contract-builder`, `platform: claude`, `cli_verbs: []`, `skill: kpi-contract-builder`, `mode: preview-then-write`, `gates: [named-human-approval]`.

- [ ] **Step 1: Add the command wrapper**

Create `distribution/bundle-templates/claude/commands/kpi-contract-builder.md`:

```markdown
Drive the kpi-contract-builder skill: assess a planned or custom KPI's
answerability, list the exact Decision Store decisions to get approved, and
preview a governed project metric-contract (with per-field provenance). Writes a
contract only after the approved decisions, a named owner, and committed source
evidence exist. Never self-grants an approval, fabricates a score, or promotes a
KPI to Seeded.
```

- [ ] **Step 2: Add the public-surface entry**

In `distribution/public-command-surface.yaml`, append a new command entry (matching the `review` shape):

```yaml
  - name: kpi-contract-builder
    platform: claude
    intent: Draft a governed project metric-contract for a planned or custom KPI, gated on approved decisions.
    cli_verbs: []
    skill: kpi-contract-builder
    wrapper_template: distribution/bundle-templates/claude/commands/kpi-contract-builder.md
    bundle_destination: commands/kpi-contract-builder.md
    mode: preview-then-write
    gates: [named-human-approval]
    documentation: docs/install/agent-install.md
    status: shipped
```

- [ ] **Step 3: Verify the surface entry parses and references resolve**

Run:
```bash
python -c "import yaml; d=yaml.safe_load(open('distribution/public-command-surface.yaml',encoding='utf-8')); e=[c for c in d.get('commands',d) if isinstance(c,dict) and c.get('name')=='kpi-contract-builder']; assert e, 'entry missing'; import os; assert os.path.exists(e[0]['wrapper_template']), 'wrapper missing'; print('surface entry OK')"
```
Expected: `surface entry OK`. (If the top-level key is not `commands`, adjust the accessor to the file's actual shape.)

- [ ] **Step 4: Run the full static gate + kit-lint**

Run:
```bash
python -m seshat.cli check --repo .
python -m seshat.cli kit-lint --repo .
```
Expected: `check` exit 0; `kit-lint: no projection drift.`

- [ ] **Step 5: Commit**

```bash
git add distribution/public-command-surface.yaml distribution/bundle-templates/claude/commands/kpi-contract-builder.md
git commit -m "feat: advertise kpi-contract-builder on the public command surface"
```

---

### Task 5: Final consistency sweep + design reconciliation

Prove the whole capability coheres and the committed design matches what shipped.

**Files:**
- Modify (if any drift found): `docs/superpowers/specs/2026-07-17-kpi-contract-builder-design.md`
- Reference: all files created in Tasks 1-4

**Interfaces:**
- Consumes: everything above.
- Produces: a green `retail check` + `kit-lint` + `doctor` and a design doc consistent with the shipped skill.

- [ ] **Step 1: Run all gates together**

Run:
```bash
python -m seshat.cli check --repo .
python -m seshat.cli kit-lint --repo .
python -m seshat.cli doctor --repo . --strict
```
Expected: `check` exit 0; `kit-lint: no projection drift.`; `doctor: no drift found`.

- [ ] **Step 2: Confirm the shipped engine + its tests are untouched**

Run:
```bash
git diff --name-only origin/main -- src/seshat/kpi_contracts.py src/seshat/kpi_answerability.py tests/unit/test_kpi_contracts.py
```
Expected: empty output (these files were reused, never modified).

- [ ] **Step 3: Run the reused engine's tests to prove no regression**

Run: `python -m pytest tests/unit/test_kpi_contracts.py -q`
Expected: all pass (we changed none of it; this is a safety confirmation).

- [ ] **Step 4: Reconcile the design doc with reality**

Re-read `docs/superpowers/specs/2026-07-17-kpi-contract-builder-design.md` §4/§7/§9 against the shipped skill. If any statement now diverges (e.g. a path or a section that no longer matches), fix it inline. Confirm §9 still reads "no runtime change" and matches Task-5 Step-2's empty diff.

- [ ] **Step 5: Commit any reconciliation**

```bash
git add docs/superpowers/specs/2026-07-17-kpi-contract-builder-design.md
git commit -m "docs: reconcile kpi-contract-builder design with shipped skill" || echo "no reconciliation needed"
```

---

## Self-Review (completed by plan author)

**1. Spec coverage:** design §1 purpose → Task 1/2 (skill + walkthrough); §3 boundaries → Task 1 hard stops; §4 two-trip → Task 1 flow; §5/§6 field composition + field_provenance → Task 1 + Task 2 previews; §7 packaging (Claude+Codex+wheel) → Tasks 3+4; §8 reuse → enforced by Task 5 Step 2 (engine untouched); §9 docs-first/no-runtime → Tasks all docs/config, verified Task 5. §10 out-of-scope (batch, registry mutation, rule) → none of the tasks add them. All covered.

**2. Placeholder scan:** `<NN>`, `<table>`, `<Name>`, `<knowledge-contract-ref>`, `<authority_class>` are intentional template tokens shown to the engineer, not unfilled plan gaps; every step has concrete content and a runnable command.

**3. Type consistency:** `ContractDraftRequest` / `FinalizationContext` / `draft_project_metric_contract` / `finalize_project_metric_contract` / `ContractDraftRefused` / `derive_answerability` / `render_answerability_artifact` are used verbatim as read from the shipped source. The verb `id` (Task 3) = skill `name` (Task 1) = surface `skill` (Task 4) = `kpi-contract-builder`. Origin vocabulary (`knowledge|profile|human|provisional|gap`) is identical across Task 1 and Task 2.
