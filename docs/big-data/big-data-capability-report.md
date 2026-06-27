# Big Data Analytics Capability Report

A **strategy-only** report on how Big Data / scale should fit Seshat BI. It defines
what "Big Data" means here, what conditions would justify new capability later, and
the boundaries that protect the project's agent-first, non-executing, medallion
discipline.

This report **builds nothing**. It creates no skill, no template, no checklist, no
dependency, no code, and no execution adapter. It is the boundary-setting step that
must precede any scale assessment templates (those are a separate, later PR).

## 1. Big Data is a condition, not a tool

**Big Data is a scale / latency condition, not a tool to install.** The right
question is never "should we adopt Spark/Fabric/Databricks?" — it is "does the data
no longer fit, or no longer arrive in time, on the path we already have?" Most
retail BI work in this project fits comfortably on a single machine or pushes down
to the warehouse. Tooling is a *response to proven scale pressure*, never a default.

The existing `skills/bi-bigdata-knowledge/` layer already encodes this: it is a
**reasoning/review layer, not an executor** — it reasons about engine choice,
partitioning, shuffle, skew, file formats, and scale reconciliation, and its single
most important call is often *"don't scale out — push this down to SQL/warehouse."*

## 2. What this report explicitly states

- **Do not create a Big Data skill now.** The `bi-bigdata-knowledge` reasoning layer
  already exists; no new runtime skill is warranted without proven need.
- **Do not add runtime Big Data tooling now.** No Spark/Dask/cluster runtime, no
  orchestration engine, no new dependency.
- **Extend Python later — and only for single-machine large-file analysis.** The
  first legitimate scale step is a single-node performance/large-file slice in
  `bi-python-knowledge` (e.g. chunked reads, dtype discipline, out-of-core within
  one machine), **not** distribution.
- **Create `analytics-scale-knowledge` only later** — and only if **distributed /
  lakehouse / streaming** needs are *proven* (not anticipated). Until then it does
  not exist.
- **No Spark / Fabric / Databricks / Snowflake / BigQuery adoption before
  evidence.** A named, measured scale problem (volume, latency, or cost) with a
  reviewed assessment must precede any platform choice.
- **Power BI remains an adapter, not the product.** Scale decisions never elevate a
  BI/execution tool into the core; the core is the readiness spine + knowledge
  layers.
- **Scale decisions must preserve the medallion flow** Source → Mapping → Silver →
  Gold → Semantic Model → Dashboard → Publish. A scale change may alter *how* a
  stage is computed; it may never reorder, skip, or bypass a stage or its gate.

## 3. When scale capability would be justified (later, with evidence)

Capability should be added **incrementally, on proven pressure**, in this order:

1. **Single-node large-file (Python slice)** — when a real source is large but
   still fits one machine with care. Cheapest, least disruptive.
2. **Push-down to the warehouse** — when the heavy join/aggregation belongs in SQL
   anyway; often the correct answer instead of scaling out.
3. **Distributed / lakehouse / streaming (`analytics-scale-knowledge`)** — only
   when single-node and push-down are both proven insufficient by a measured
   assessment, and a human has ruled the trade-off.

Each step is a separate, human-decided feature with its own spec — none is
authorized by this report.

## 4. Boundaries this report protects

- **Agent-first, not CLI-first; knowledge layers reason, never execute.** A scale
  layer would still be reasoning/review only — no running of jobs.
- **No fake confidence.** Any future scale assessment expresses risk as
  status/blockers, never a numeric score.
- **KPI meaning stays in `retail-kpi-knowledge`.** Scale changes *how* a metric is
  computed at volume; they never redefine its meaning.
- **Human approvals are not self-granted.** Adopting a platform is a named human
  decision backed by evidence.
- **No readiness granted by scale work.** Scale capability advances no readiness
  stage.

## 5. What this report does NOT do

- It creates **no templates or checklists** — the data-volume / large-source
  assessment artifacts are a separate, later PR that applies the boundaries set
  here.
- It adds **no dependency, no code, no execution adapter**.
- It claims **no implementation** — nothing about Big Data is built by this report.
- It adopts **no platform** and recommends none.

## 6. Recommended next step

After this report defines the boundaries, the next step is **data-volume /
large-source assessment templates** (a separate, gated PR) so that any future scale
decision is made from a repeatable, evidence-based assessment with an explicit
verdict vocabulary (e.g. local-OK / warehouse-recommended / scale-review-required /
blocked) — not from anticipation. No scale tooling is adopted until such an
assessment, reviewed by a human, says it is needed.
