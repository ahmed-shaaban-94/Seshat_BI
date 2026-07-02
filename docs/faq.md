# FAQ — Seshat BI

Short answers to the questions that come up most. Each answer cites the authoritative
source; follow it for the full story. For terms and rule ids, see `docs/glossary.md`.

## Project & scope

**What is Seshat BI?**
A standalone, agent-first retail BI **readiness** service: it walks a source through seven
readiness stages (`raw` → `marts` → Power BI) with evidence and gates at each step. The
agent is the interface; `retail check` / `retail validate` are gates it calls. See
`README.md` and `docs/readiness/readiness-model.md`.

**Is this part of the Retail Tower OS orchestrator?**
No. It is a standalone analytics service, not bound by the orchestrator / contract-boundary
rules (`CLAUDE.md`).

**Why "agent-first"? Isn't it a CLI?**
The CLI (`retail`) is a set of gates and helpers the agent calls; the agent + skills are
the interface. This is hard rule #1 (`docs/roadmap/roadmap.md`).

## The readiness spine

**What are the seven stages?**
Source Ready → Mapping Ready → Silver Ready → Gold Ready → Semantic Model Ready →
Dashboard Ready → Publish Ready. A stage is entered only when the prior one is `pass`. See
the diagram in `docs/readiness/readiness-model.md`.

**Why are there no confidence scores / percentages?**
Hard rule #9: readiness is explicit `status` + `evidence` + `blocking_reasons`, never a
fabricated number. A `pass` with no evidence is a defect (`readiness-model.md`).

**Why is a stage sometimes `warning` instead of `pass`?**
`warning` means advanced but with a non-fatal issue recorded (a static WARN or an accepted
deviation). It does **not** block the next stage; only `blocked` does. Example: in
`docs/worked-examples/retail-store-sales.md`, Publish Ready is `warning` because a prior
publish approval was retracted after a metric correction — a fresh approval is pending.

**Can the agent approve a mapping, a metric, or a publish?**
No. Grain, PII, business rollups, and approvals are human judgment calls recorded in
`approvals[]` by a named owner (Principle V). The agent authors and recommends; it never
self-grants. Four stages require a named-human approval: Mapping, Semantic Model,
Dashboard, Publish.

## Checks & gates

**What's the difference between `retail check` and `retail validate`?**
`retail check` is the **static** gate — it runs over committed text (SQL/TMDL/PBIR), needs
no database, and is stdlib-only. `retail validate` is the **live** surface — it reconciles
a materialized table against a running Postgres (read-only). Static-green is necessary but
not sufficient; semantic correctness needs the live boundary. See `docs/glossary.md`.

**`retail check` flagged a rule id like `S4b` / `D7` / `G6`. What do I do?**
The `retail-govern` skill maps each id to its meaning and fix; `docs/glossary.md` lists the
families (S = SQL, D = DAX/TMDL, C = connection/secrets, R = PBIR, G = git hygiene,
P = process). The live registry in `src/retail/rules/` is authoritative.

**Why did `RC7` and `D7` used to collide?**
They didn't really — `RC1–RC16` are ADR-0002 *cleaning defaults*; `D1…`, `S1…` are
*checker rules*. The namespaces were disambiguated in feature 002 so a cleaning default
reads `RC<n>` and a checker rule reads its letter prefix.

## Data modeling

**Why land bronze as all-TEXT?**
A faithful landing preserves the source exactly (leading zeros, blanks, encodings) so
typing/cleaning decisions happen explicitly in silver. Missingness is measured as
`'' OR NULL` because a faithful landing writes `''`, not `NULL`. See
`docs/medallion-playbook.md`.

**Why does every gold dimension get a `-1` "unknown" member — except the date dimension?**
Entity dims use a `-1` member so unmatched/missing keys join cleanly via
`COALESCE(..., -1)` (RC14, rule S6). The **date** dim is the exception: it is a *marked
date table* (contiguous, no nulls) that Power BI validates for time-intelligence — a `-1`
member would break refresh. Rule **S8** enforces "no `-1` on the date dim"; an unmatched
fact date fails loud via `date_sk NOT NULL`. See `docs/worked-examples/retail-store-sales.md` §6
and the trap-checklist in `docs/medallion-playbook.md` (Appendix A, #18–19).

**Why keep IDs (transaction/customer) as TEXT, not integers?**
Leading zeros and non-numeric ids must survive; casting them to int corrupts keys (RC7,
rule S5).

## Power BI

**Why PBIP and not `.pbix`?**
PBIP saves the report/model as plain-text TMDL/PBIR, which diffs and reviews in git. It's a
preview feature you enable in Power BI Desktop. See the `pbip-workflow` skill and
`docs/conventions.md`. Keep names short (Windows 260-char path limit).

**What can I commit vs ignore for a PBIP?**
Commit the `definition/` folders (that's the model). The `.gitignore` baseline is exactly
`**/.pbi/localSettings.json` and `**/.pbi/cache.abf` — never ignore `definition/`
(`CLAUDE.md`).

**When can the agent actually publish to Power BI?**
Not yet — that's **F016**, the deferred, execution-only Power BI adapter, gated by hard
rule #6 (cannot start before Semantic Model Ready is `pass`) and deliberately last. It
materializes/publishes an already-approved model; it cannot define metrics, mappings, or
design. See `docs/roadmap/roadmap.md`.

## Metrics

**Where do metric definitions live, and who approves them?**
A metric **contract** (intent + grain + owner + gold binding) lives at
`mappings/<table>/metrics/<MetricName>.yaml`; reusable groupings live at
`metrics/packs/<pack_name>.yaml`. Only the named metric owner moves a contract to `pass`.
For a generic starting menu, see `docs/metrics/retail-kpi-catalog.md`. The rules are in
`docs/metrics/metric-contract-store.md`.

**Can a contract contain DAX?**
No — a contract is *intent + binding*, never DAX, SQL, a visual, or a check. It binds to a
`gold` column only (never silver/bronze).

## Contributing & environment

**How do I set up and run the checks locally?**
The package needs **Python 3.13+**: `pip install -e ".[dev]"`, then run `ruff format
--check`, `ruff check`, `pytest -m unit`, `retail check`, `retail semantic-check --repo .`
(what CI runs). Full detail in `CONTRIBUTING.md`.

**Are dbt and Dagster required?**
No. F029 (dbt) and F030 (Dagster) are **optional** companion engines — advisory adapters
that execute approved steps but never create truth. They are not prerequisites for anything
(`docs/roadmap/roadmap.md`, Tier 5).

**Why is C086 everywhere — is it the schema to follow?**
No. C086 (a retail pharmacy example) is the *first* worked example, not the universal schema (hard
rule #7). A second example (`retail-store-sales.md`) exists precisely to prove the kit is
generic. Copy the *structure*, not C086's *answers*.

## See also

- Glossary: `docs/glossary.md` · Conventions: `docs/conventions.md` · Contributing:
  `CONTRIBUTING.md`.
- The spine: `docs/readiness/readiness-model.md` · The method: `docs/medallion-playbook.md`.
- Worked examples: `docs/worked-examples/README.md` · Roadmap + hard rules:
  `docs/roadmap/roadmap.md`.
