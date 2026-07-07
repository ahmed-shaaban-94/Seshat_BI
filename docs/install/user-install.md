# Installing Seshat BI (user path)

> **Status: Proposed / forward-looking (roadmap M2).** This documents the *intended*
> installable-product experience. Seshat BI is **not yet published to a package index**,
> so `pipx install seshat-bi` does not work today — until M2's packaging/distribution
> milestone ships (see `docs/roadmap/seshat-bi-agent-controlled-user-tool-roadmap.md`),
> use the **developer path** in the top-level `README.md` Quickstart (`git clone` +
> `pip install -e ".[dev]"`). This page describes where the product is headed and is kept
> in lockstep with the roadmap; it is not a claim that the published install works now.

Seshat BI is an agent-controlled Retail BI readiness tool. There are two ways to run it:
a **developer path** (clone the repo, work inside it) and the **user path** below (install
the tool, run it against your own project). This page covers the user path.

## The `seshat` command

The tool exposes a `seshat` console command (an alias of the canonical `retail` command;
both dispatch the same entry point — roadmap M1, shipped). Once installed, `seshat` and
`retail` are interchangeable; `seshat` is the product-facing brand name.

## Intended install (once published — M2)

```bash
# isolated, recommended (pipx keeps the tool off your global env)
pipx install seshat-bi

# or into the active environment
pip install seshat-bi
```

Verify:

```bash
seshat --help
seshat check --help
```

## Until then — run from source (works today)

```bash
git clone https://github.com/ahmed-shaaban-94/Seshat_BI.git
cd Seshat_BI
pip install -e ".[dev]"     # exposes both `retail` and `seshat` commands
seshat check                 # or: retail check
```

Not installing at all? The checker runs straight from source (no console script needed):

```bash
python -m retail.cli check
```

## What `seshat` does

It is a **gate the agent calls**, not a dashboard generator. It profiles a retail source,
governs the source→mapping decisions a human must approve, gates silver/gold warehouse work,
validates the warehouse live, defines metric contracts, protects Power BI semantic meaning,
and prepares the PBIP handoff — advancing one **readiness stage** at a time, always with
evidence and blocking reasons, never a fabricated confidence score. Publishing/execution
stays gated behind semantic-model readiness and a named-human approval.

See the [seven-star readiness spine](../readiness/readiness-model.md) and the
[medallion playbook](../medallion-playbook.md) for the full flow.

## Requirements

- Python 3.13
- Git (Seshat reads committed evidence; several checks are git-aware)
- For live DB validation: the `db` extra and a DSN (`pip install -e ".[db]"`) — see
  `docs/powerbi-connection.md`. Static `check` needs no database.

## Configuration

Credentials live only in `.env` (git-ignored) and reach Power BI via parameters, never
baked-in connection strings. See the top-level `README.md` and `docs/powerbi-connection.md`.
