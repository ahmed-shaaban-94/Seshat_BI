# Retail Tower Analytics — Repository Skeleton Design

- **Date:** 2026-06-22
- **Status:** Approved (brainstorming complete)
- **Scope:** Repository skeleton + documentation only (no live DB, no reports yet)
- **Repo:** `Retail_Tower_analytics`

## 1. Purpose

A **standalone analytics service** for the Retail Tower ecosystem. Power BI is the
primary reporting tool; the architecture leaves room for other tools later. Data is
served from a dedicated **PostgreSQL database hosted on DigitalOcean** — separate from
Data-Pulse-2's operational source-of-truth.

This repo is a **separate service with its own context**. For now it is NOT wired into
the Retail Tower OS contract-boundary / orchestrator rules; it stands on its own and may
integrate with the ecosystem later through a clean ingestion seam.

## 2. Decision Record

| # | Question | Decision | Implication |
|---|----------|----------|-------------|
| 1 | Where does Power BI read data from? | Remote **PostgreSQL on DigitalOcean** (dedicated analytics DB) | Repo holds SQL that builds/feeds the DB; Power BI reads from it. Never points at DP2's operational tables. |
| 2 | How is data ingested (scope)? | **Separate service, separate context** | Standalone repo, not bound by orchestrator/contract-boundary rules. |
| 3 | Power BI file format in git? | **PBIP** (plain-text TMDL/PBIR) | Semantic model + report diffable; DAX reviewable in PRs. |
| 4 | First-pass deliverable? | **Repo skeleton + docs** | Structure, gitignore, env example, README, CLAUDE.md, conventions. No DB/reports yet. |
| 5 | Repo layout? | **Approach A — layered by concern** | `warehouse/` (tool-agnostic) · `powerbi/` (only PBI-specific) · `pipelines/` · `docs/`. |
| 6 | Ingestion mechanism? | **Manual now; automated "flowing" service later** | `pipelines/` documents the manual procedure + the contract a future feed must honor. No ETL code yet. |

**Open questions:** none. All decisions above are settled.

## 3. Architecture

```
DigitalOcean PostgreSQL (analytics DB)
        ▲                        │
        │ manual loads (now)     │ read (parameters, read-only intent)
        │ automated feed (later) ▼
   raw schema  ──►  marts schema  ──►  Power BI (PBIP)
```

- **`raw` schema** — landing zone. Both today's manual loads and the future automated
  "flowing" service target this same contract, so the automation drops in without
  renegotiating the data shape.
- **`marts` schema** — reporting views/tables Power BI consumes. Tool-agnostic: any
  future BI tool reads the same marts.
- **Power BI** — connects via **parameters** (host/db/credentials supplied at refresh
  time), never a baked-in connection string in the committed model.

> Note: "read-only intent" describes how Power BI uses the DB. Enforcing it with a
> dedicated read-only Postgres role is a future hardening step, not part of this
> skeleton (see §9).

## 4. Repository Structure (Approach A)

```
Retail_Tower_analytics/
├── README.md                  # what this service is, setup, contribution flow
├── CLAUDE.md                  # repo-specific Claude Code rules + PBIP/Windows gotchas
├── .gitignore                 # MS PBIP baseline + Python/OS/secrets entries
├── .gitattributes             # line-ending handling for PBIP text files
├── .env.example               # ANALYTICS_DB_* placeholders, no real values
│
├── warehouse/                 # tool-agnostic data layer (SQL)
│   ├── schema/                #   DDL: schemas (raw, marts), tables
│   ├── marts/                 #   reporting views / mart definitions
│   ├── migrations/            #   ordered, idempotent SQL change scripts
│   └── README.md              #   naming conventions, how to apply against DO Postgres
│
├── powerbi/                   # ONLY Power-BI-specific folder
│   ├── README.md              #   enable PBIP, connect via parameters, save rules
│   └── .gitkeep               #   (.pbip projects added when reports are built)
│
├── pipelines/                 # ingestion
│   ├── README.md              #   manual load procedure NOW + contract for future feed
│   └── .gitkeep
│
└── docs/
    ├── superpowers/specs/     #   this design doc
    ├── conventions.md         #   SQL + PBIP + DAX naming/style conventions
    └── data-dictionary.md     #   stub catalog of tables/columns/marts (grows over time)
```

## 5. Version Control — committed vs. ignored

Sourced from Microsoft's official PBIP docs (Power BI Desktop projects, updated
2025-12-15).

**Committed:**
- `*.SemanticModel/definition/**` — TMDL (tables, relationships, **DAX measures**)
- `*.Report/definition/**`, `definition.pbir`, `.platform`, the `*.pbip` file
- All SQL under `warehouse/`, all docs

**Ignored** (`.gitignore`):
- `**/.pbi/localSettings.json` — local workspace settings (can carry connection context)
- `**/.pbi/cache.abf` — local data cache
- `.env` — real secrets, never tracked
- Standard Python (`__pycache__/`, `.venv/`, `*.pyc`) and OS junk (`.DS_Store`, `Thumbs.db`)

## 6. Secrets

- DO Postgres credentials live in **`.env`** (git-ignored).
- **`.env.example`** documents variable names (`ANALYTICS_DB_HOST`, `ANALYTICS_DB_PORT`,
  `ANALYTICS_DB_NAME`, `ANALYTICS_DB_USER`, `ANALYTICS_DB_PASSWORD`, `ANALYTICS_DB_SSLMODE`)
  with empty/placeholder values.
- Power BI uses **parameters** for the connection — no credentials in committed model files.

## 7. Conventions (`docs/conventions.md`)

- **SQL:** `snake_case`; schemas `raw` (landing) + `marts` (reporting); views `vw_`,
  facts `fct_`, dimensions `dim_`; migrations numbered and idempotent.
- **PBIP/DAX:** measures in `PascalCase` with display folders; one semantic model per
  subject area; reports reference the model relatively.

## 8. Windows / PBIP guardrails (`CLAUDE.md` + `.gitattributes`)

From Microsoft docs — these commonly bite teams:
- **260-char path limit** on Windows → keep PBIP project names short; repo at a short root path.
- **CRLF** → Power BI uses CRLF; configure `git config core.autocrlf` and use
  `.gitattributes` so PBIP text diffs stay clean.
- **UTF-8 without BOM** when editing PBIP files outside Power BI Desktop.
- **PBIP is in preview** (as of 2025-12) → must be enabled in Power BI Desktop
  Preview features; README notes this so "Save as PBIP" missing isn't confusing.

## 9. Out of scope (YAGNI — this pass)

- Live DigitalOcean Postgres provisioning.
- Actual SQL schema/mart content beyond placeholder structure.
- Any `.pbip` report or semantic model.
- Automated ingestion ("flowing" service) — only its contract is documented.
- Retail Tower OS orchestrator / contract-boundary integration.

## 10. Success criteria

- Repo has the Approach A structure with placeholder READMEs in each top-level folder.
- `.gitignore` matches the MS PBIP baseline plus Python/OS/secrets entries.
- `.env.example` present; no real secrets anywhere in tracked files.
- `README.md` + `CLAUDE.md` explain setup, PBIP preview enablement, and Windows guardrails.
- `docs/conventions.md` and a `data-dictionary.md` stub exist.
- A teammate can clone, read the READMEs, and understand how to add the first SQL mart
  and the first PBIP report without further explanation.
