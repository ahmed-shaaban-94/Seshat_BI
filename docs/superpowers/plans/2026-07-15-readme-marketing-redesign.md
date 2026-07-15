# README Marketing Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `README.md` with an evidence-led public landing page that converts first-time visitors into adopters, contributors, and prospective sponsors.

**Architecture:** Keep the README as one self-contained GitHub landing page backed by existing repository assets and documentation. Use progressive disclosure: product promise and proof first, community and sponsorship calls to action second, and detailed technical references last. The existing `assets/brand/seshat-bi-logo.png` is the canonical hero image; no new art or runtime behavior is required.

**Tech Stack:** GitHub-flavored Markdown, HTML alignment/image tags, Mermaid, Shields.io badges, Seshat BI CLI, existing PNG/SVG assets.

## Global Constraints

- Position Seshat BI as `the evidence-gated path from messy retail data to trusted Power BI`.
- Primary CTA: run the offline demo. Secondary CTAs: find a first contribution and sponsor a public roadmap lane.
- Preserve `seshat` as the primary command and `retail` as the deprecated compatibility alias.
- Use `assets/brand/seshat-bi-logo.png`; do not generate or redesign brand art.
- Use ASCII punctuation in committed prose.
- Never fabricate a readiness score, approval, live-validation pass, adoption statistic, sponsor, or funding destination.
- Never present the deferred Power BI execution adapter as shipped.
- Do not change product behavior, readiness rules, or roadmap state.

---

### Task 1: Replace the README with the evidence-led landing page

**Files:**
- Modify: `README.md`
- Reference: `assets/brand/seshat-bi-logo.png`
- Reference: `assets/demo/readiness-proof.png`
- Reference: `docs/superpowers/specs/2026-07-15-readme-marketing-redesign.md`

**Interfaces:**
- Consumes: current CLI names from `pyproject.toml`, contribution paths from `docs/contributing/first-contribution.md`, and readiness rules from `AGENTS.md`.
- Produces: a GitHub-renderable public landing page whose stable anchors are `#see-it-work`, `#contributing`, and `#sponsor-seshat-bi`.

- [x] **Step 1: Replace the hero and public positioning**

Use a centered hero with the canonical logo at 360px width, the exact promise
`From messy retail data to trusted Power BI -- with evidence at every gate.`, and
this one-sentence product definition:

```markdown
An agent-first readiness system that profiles sources, governs mappings, validates
the medallion warehouse, binds metrics to contracts, and prepares Power BI delivery
without skipping the human decisions that make analytics trustworthy.
```

Include factual badges for PyPI version, CI, Python 3.13+, Apache-2.0, PostgreSQL,
and Power BI PBIP. Put these three CTAs immediately below the badges:

```markdown
[**Run the demo**](#see-it-work) &nbsp;&middot;&nbsp;
[**Start contributing**](docs/contributing/first-contribution.md) &nbsp;&middot;&nbsp;
[**Sponsor a roadmap lane**](#sponsor-seshat-bi)
```

- [x] **Step 2: Tell the problem and product story**

Add a short `Why Seshat BI` section explaining that polished dashboards can still
contain undefined metrics, unsafe assumptions, and unreconciled numbers. Explain
that Seshat records `status + evidence + blocking_reasons`, preserves named human
approvals, and answers: `Is this retail source ready to become trusted Power BI?`

Follow with a compact Mermaid readiness flow using exactly these ordered nodes:

```text
Source -> Mapping -> Silver -> Gold -> Semantic Model -> Dashboard -> Publish
```

Under the diagram, state the four hard boundaries: no silver before Mapping Ready,
no Power BI before gold validation, no dashboard before metric contracts, and no
execution adapter before semantic-model readiness.

- [x] **Step 3: Put runnable proof before the capability catalog**

Create the `## See it work` section with this exact clean-start path:

```bash
pipx install seshat-bi
seshat demo init
seshat demo run
seshat demo report --format html
```

Render `assets/demo/readiness-proof.png` and explicitly say that the offline demo
shows evidence, blockers, approvals, and next actions while stopping honestly at
Gold Ready because live validation needs a database.

- [x] **Step 4: Explain differentiation and operation**

Add four concise value pillars: evidence instead of scores, human judgment stays
human, agent-safe stage sequencing, and governed gold plus approved metric contracts
for Power BI. Add one Mermaid architecture flow from raw source through bronze,
silver, gold, and PBIP, with Seshat governance wrapping the transformations and
validation boundary.

Add a `Choose your path` table with these destinations:

| Visitor | First action |
|---|---|
| Evaluating quickly | Offline demo |
| Starting a new project | `seshat init-project my-bi` |
| Adopting an existing PBIP | `seshat adopt-pbip assess --project <path>` |
| Working as an agent | `docs/agent-mode.md` |
| Contributing | `docs/contributing/first-contribution.md` |

- [x] **Step 5: Curate shipped capabilities and technical references**

Use a short visible capability list covering: static and live gates; seven-stage
status/next control surfaces; governed mapping and metric contracts; DAX drift,
value, and generation checks; offline proof and review/SARIF; read-only MCP governor
and readiness passports; extension packs; PBIR authoring and read-only PBIP adoption;
and optional dbt/Dagster adapters.

Keep detailed repository layout and documentation links in compact tables or a
collapsed `<details>` block. Separate the deferred execution adapter and human Power
BI Desktop work from shipped capabilities with a warning callout.

- [x] **Step 6: Add contributor and sponsor conversion sections**

The `## Contributing` section must link:

- `docs/contributing/first-contribution.md`
- `docs/contributing/contribution-lanes.yaml`
- the starter issue form at
  `https://github.com/ahmed-shaaban-94/Seshat_BI/issues/new?template=starter.yml`
- `CONTRIBUTING.md`

Name contribution lanes in accessible language: KPI contract templates, synthetic
fixtures, dialect notes, accessibility checks, and blocker explanations.

The `## Sponsor Seshat BI` section must explain that funding accelerates public,
evidence-backed work such as database compatibility, reproducible demo coverage,
documentation, and contributor support. State that sponsorship cannot buy an
approval or weaken a gate. Link `Start a sponsorship conversation` to:

```text
https://github.com/ahmed-shaaban-94/Seshat_BI/issues/new?title=%5Bsponsorship%5D%20Sponsor%20a%20public%20roadmap%20lane
```

Do not create an empty sponsor grid or `.github/FUNDING.yml` without a verified
funding account.

- [x] **Step 7: Close with install choices, project links, and brand line**

Keep concise install examples for the Python CLI, Claude Code plugin, and Codex
plugin. Link the user install guide, agent install guide, support matrix, readiness
model, architecture, roadmap, FAQ, changelog/release notes, license, and visual
identity. End with:

```text
Governed knowledge. Measured structure. Trusted BI.
```

- [x] **Step 8: Review the rendered narrative in source order**

Read `README.md` top to bottom and confirm the first screen contains the product,
proof-oriented promise, and all three CTAs; the demo precedes the capability catalog;
contributors and sponsors each have one unambiguous action; and no section duplicates
the full detail already owned by linked documentation.

---

### Task 2: Verify links, Markdown hygiene, and governance truth

**Files:**
- Verify: `README.md`
- Verify: all relative paths referenced from `README.md`

**Interfaces:**
- Consumes: the completed README from Task 1.
- Produces: evidence that the public landing page is internally navigable and passes the repository's static governance gate.

- [x] **Step 1: Scan for forbidden placeholders and non-ASCII text**

Run:

```powershell
rg -n "Tower BI Agent Kit|fully automated|readiness score" README.md
$text = Get-Content -Raw README.md
if ($text.ToCharArray() | Where-Object { [int]$_ -gt 127 }) { throw 'README contains non-ASCII text' }
```

Expected: `rg` returns no matches and the PowerShell check exits without error.

- [x] **Step 2: Verify every repository-relative link and image**

Extract Markdown link targets and HTML `src` values from `README.md`. Ignore
`http://`, `https://`, `mailto:`, and `#` targets; remove any `#fragment` from local
targets; decode `%20`; then assert every remaining path exists relative to the
repository root.

Expected: no missing local targets, including both brand/demo images and every
linked documentation file.

- [x] **Step 3: Check the Markdown diff**

Run:

```bash
git diff --check -- README.md
git diff --stat -- README.md
```

Expected: `git diff --check` emits nothing; the stat reports only `README.md` for
the implementation change.

- [x] **Step 4: Run the repository governance gate**

Run:

```bash
seshat check
```

Expected: exit code 0. This proves static policy compliance only; do not describe
it as live semantic correctness.

- [x] **Step 5: Commit the verified README**

Run:

```bash
git add README.md docs/superpowers/plans/2026-07-15-readme-marketing-redesign.md
git commit -m "docs: redesign the public readme"
```

Expected: the commit contains only the README implementation and its implementation
plan; unrelated `.claude/settings.local.json` and `.test-tmp/` files remain untracked.
