# Design: Localhost Status Dashboard

- **Date:** 2026-07-19
- **Status:** Approved design; awaiting user review of the written spec
- **Approvals in this session:** scope (real status only), open mechanism
  (generate + auto-open static HTML, file://), prototype-first. B1 governance
  pivot confirmed with user.
- **Worktree:** `.claude/worktrees/dashboard` (branch `worktree-dashboard`)
- **Fidelity source:** `E:\Dashboard design directive.zip` -> "Seshat BI - Control Center" handoff
  (extracted to scratchpad; RTL Arabic navy/gold/teal design language).

## 1. Purpose

Give a Seshat BI user a **local web view of the project status the tool already
tracks** -- opened on localhost -- so they can see, at a glance, where every
onboarded table stands across the seven governance/readiness stages, what
evidence backs each pass, what is blocked and why, and the single next action.

It is a **view**, not a new subsystem. All data it shows already exists and is
already contract-locked; the dashboard renders it, and nothing more.

## 2. Scope (locked with user)

| Decision | Choice |
|---|---|
| How much of the 8-screen handoff design | **Real status only** -- Home health overview + Tables 7-gate readiness. Other screens (decisions/runs/evidence/lineage/powerbi/settings) are OUT of this spec. |
| How it is opened | **`retail dashboard` GENERATES a self-contained static `.html` and auto-opens it in the browser** (mirrors `demo/html_report.py`). Re-run to refresh. NOT a live server -- see B1 below. |
| Render model | **Pure Python renders a full static HTML file** (no JS SPA, no build step, no socket). |
| Home for the code | **Prototype in this worktree first**; commit/PR decided later. |
| Reuse vs. fresh renderer | **New standalone renderer** in the handoff's visual language, stdlib-only. Reuse only the stage-label/escaping *patterns* from `demo/html_report.py`, not its look. |

### Why static-generate, not a live server (governance finding)

The obvious "launch a tiny `http.server` on 127.0.0.1" mechanism is **non-compliant
with this repo** and was rejected after checking the rules:

- Rule **B1** (`src/seshat/rules/never_execute.py`) denylists module-scope imports
  of connection-capable libraries in governed modules, and the denylist includes
  **`"http"` (http.server) and `"socket"`**. The governed prefix covers
  **`src/seshat/cli/`**. A CLI handler that opens a listening socket violates the
  ratified invariant: *"the reasoning/CLI layers are static ... they never open a
  database connection or a network socket."*
- Generating a static file opens no socket, so it clears B1 and matches how the
  repo already produces HTML (`demo/html_report.py`). The "localhost" experience
  is preserved by auto-opening the file; a user who wants a true `http://localhost`
  URL can run `python -m http.server` in the output dir themselves (documented,
  never invoked by our code).

### Explicit non-goals (YAGNI)

- No new readiness logic. The dashboard **never** computes, derives, advances, or
  upgrades a stage, and **never** emits a numeric / percent / confidence score
  (repo hard rule #9; `never_fabricate_a_confidence_score`).
- No writes (beyond the one output HTML file), no DB connection, no network call,
  no listening socket. Read-only over committed state, mirroring
  `status_surface.py`'s ratified Option-B contract.
- No server, no authentication, no multi-user, no ports. Just a generated file.
- No new third-party dependency (no Flask/FastAPI/Jinja2). Python stdlib only.
- Not the other 6 handoff screens. Not a React app. Not live publish.

## 3. Data source (already exists)

The single input is the existing status projection:

- Function: `seshat.status_surface.build_status_projection(repo_root) -> dict`
- CLI equivalent: `retail status --format json`
- Schema: `schemas/agent-status.schema.json` (`$defs/tableStatus`)
- Shape (verbatim from real committed sample data):

```json
{
  "tables": [
    {
      "table": "bronze.retail_store_sales",
      "source_path": "mappings/retail_store_sales/readiness-status.yaml",
      "current_stage": "publish_ready",
      "stages": {
        "source_ready":  { "status": "pass",    "evidence": ["..."], "blocking_reasons": [] },
        "gold_ready":    { "status": "blocked", "evidence": [],      "blocking_reasons": ["..."] }
      },
      "blocking_reasons": ["..."],
      "next_action": "..."
    }
  ]
}
```

- Stage order (canonical, 7):
  `source_ready -> mapping_ready -> silver_ready -> gold_ready ->
   semantic_model_ready -> dashboard_ready -> publish_ready`
- Status enum (exactly 4, categorical -- never a number):
  `not_started | blocked | warning | pass`
- Approvals: the projection does NOT currently expose `approvals[]`; the
  dashboard shows only what the projection returns. (Approvals timeline is a
  future enhancement, out of scope here.)

Real repo data spans the useful extremes: `retail_store_sales` = all 7 `pass`;
`demo_sample_orders` = `gold_ready` **blocked** with a real reason. Both render.

## 4. Architecture

Four small, independently-testable units. The render layer is a **pure function
of the projection dict** -- no I/O -- so it is trivially unit-tested without the
filesystem. The ONLY unit that touches disk is the thin generator that writes the
output file; the ONLY unit that touches the CLI is the handler.

```
retail dashboard  (CLI verb)
        |
        v
+-------------------------------+
| cli/commands/dashboard.py     |  arg parsing; calls generate(); prints path;
| dashboard_main(args) -> int   |  auto-opens file. Flags: --out, --repo, --no-open
+---------------+---------------+
                | calls
                v
+-------------------------------+     reads (no socket, no net)
| dashboard/generate.py         | --------------------------+
| generate(repo, out) -> Path   |                           |
|  - build_status_projection()  |                           v
|  - render one HTML string     |            +-----------------------------------+
|  - write out (default:        |            | status_surface.py (EXISTING)      |
|    reports/dashboard/index.html)|          | build_status_projection(repo)     |
|  - returns the written path   |            +-----------------------------------+
+---------------+---------------+
                | calls (pure)
                v
+-------------------------------+
| dashboard/render.py           |  pure: dict -> ONE self-contained HTML str.
|  render_page(projection)      |  builds shell + Home + Tables in one document
|  (helpers: _shell, _kpi,      |  (single file; nav = in-page anchors / sections)
|   _stage_pill, _status_chip)  |
+---------------+---------------+
                | embeds
                v
+-------------------------------+
| dashboard/theme.py            |  the design tokens as one CSS string constant
|  DASHBOARD_CSS: str           |  (navy/gold/teal, RTL, from colors_and_type.css)
+-------------------------------+
```

### Module responsibilities

- **`cli/commands/dashboard.py`** -- thin handler. Parses `--out`/`--repo`/`--no-open`,
  calls `generate(...)`, prints `Dashboard written: <path>` and (unless `--no-open`)
  auto-opens it. Uses `webbrowser.open` LAZILY, imported inside the handler
  (`webbrowser` opens no socket and is not on B1's denylist, but lazy-import keeps
  the CLI import chain clean). Registered as one `_DISPATCH` row + one lazy import,
  exactly like `status`, PLUS a `capabilities.yaml` entry (see s.9).
- **`dashboard/generate.py`** -- the only disk-touching unit. Calls the existing
  `build_status_projection(repo_root)`, passes the dict to `render_page`, writes
  the string to the output path (UTF-8, no BOM), creates parent dirs, returns the
  `Path`. No socket, no network, no DB -- clears B1.
- **`dashboard/render.py`** -- **pure**. Turns the projection dict into ONE
  complete, self-contained HTML document (Home + Tables sections, inline CSS +
  inline SVG). Reuses the `_STAGE_LABELS` / HTML-escape idiom from
  `demo/html_report.py`. This is where all tests concentrate.
- **`dashboard/theme.py`** -- the tokens (ported from the handoff's
  `colors_and_type.css` + the inline shell styles) as a single CSS string the
  render layer inlines into `<style>`. Keeps colors out of the render logic.

### One file, two sections (no routes)

Because the output is a single static file, there is no router. The Home overview
and the Tables 7-gate detail live in one document; the sidebar nav uses in-page
anchors (`href="#tables"`) to jump between sections. This keeps it fully static,
zero-JS, and openable via `file://`. (A future live-server variant could split
these into routes, but that is out of scope and would need the B1 question
re-opened.)

## 5. Screens

### 5.1 Home (screen title: "صحة المشروع" / Project Health)

Faithful to the handoff Home, but every number is **derived only by counting the
real projection** (a count is a measured fact, not a fabricated score):

- **Meta row:** "آخر تحديث" is the process time the page was rendered
  (honestly a render timestamp, labeled as such -- not invented data freshness).
- **KPI cards (counts over the real tables):**
  - Total tables tracked (= `len(tables)`)
  - Publish-ready (= count where `current_stage == "publish_ready"`)
  - Blocked (= count with any stage `status == "blocked"` OR top-level
    `blocking_reasons`)
  - Needs attention / not fully advanced (= tables not at `publish_ready`)
  - (These are COUNTS, not percentages or health scores. If a percentage is ever
    shown it is "N of M", never a bare %.)
- **Per-table summary table:** one row per table -- name, current_stage (as a
  labeled pill), a compact 7-dot stage strip (dot color per status), blocker
  count, next_action (truncated), and an in-page anchor to its card in the Tables
  section (`href="#table-<name>"`).
- **Info banner:** the fixed governance-reminder copy from the design.

### 5.2 Tables (screen title: "تفاصيل الجدول" / Table Detail)

The 7-gate readiness view -- v1 is a vertical stack of one per-table card each
(fully static, zero JS; each card has an `id="table-<name>"` anchor target):

- Per table: header (name + current_stage pill + source_path), then the
  **7-stage stepper** -- each stage a labeled node colored by its status
  (`pass` green / `blocked` red / `warning` amber / `not_started` gray),
  connected in canonical order.
- Under each stage (or expanded): its `evidence[]` as a list and its
  `blocking_reasons[]` as a red callout.
- Table-level `blocking_reasons[]` and `next_action` shown prominently.

### Visual language (from the handoff, applied verbatim as tokens)

- RTL (`dir="rtl"`), navy sidebar `#001E35`, gold accent `#C69214` / `#E0A93B`,
  teal links `#0C7C7A`, ivory-on-navy text, app bg `#F4F6F9`, white cards,
  16px card radius, `0 1px 2px rgba(16,32,51,.04)` card shadow.
- Status color mapping (the ONE place status -> color lives):
  `pass -> #1F8A54 / #E7F3EC`, `warning -> #B5832A / #FEF4E1`,
  `blocked -> #C0392B / #FDECEC`, `not_started -> #6B7480 / #F1F5F9`.
- Fonts: fallback stacks only (`'Segoe UI', Tahoma, system-ui`); no web fonts.
- Icons: inline SVG (a minimal set), matching the Feather-style of the handoff.

## 6. Data flow

1. User runs `retail dashboard` (optionally `--out <path> --repo <path> --no-open`).
2. Handler calls `generate(repo_root, out)`.
3. `generate` reads `build_status_projection(repo_root)`, calls
   `render_page(projection)`, writes the self-contained `.html`, returns its path.
4. Handler prints `Dashboard written: <path>` and (unless `--no-open`) opens it in
   the default browser via `webbrowser.open`.
5. To refresh: re-run `retail dashboard` (the file is regenerated from current
   committed YAML). To view on a real `http://localhost`, the user may run
   `python -m http.server` in the output directory themselves -- documented, never
   run by our code.

## 7. Error handling

- **Empty repo / no mappings:** projection returns `{"tables": []}`. Page renders
  a friendly empty state ("no readiness-status.yaml committed under mappings/"),
  never an error. (Mirrors `status`'s graceful-empty contract.)
- **Malformed `readiness-status.yaml`:** already skipped best-effort by
  `build_status_projection` (RS1 is the fail-loud gate, not this view). Dashboard
  shows the tables it CAN read.
- **Output path not writable:** `generate` catches `OSError` on write, the handler
  prints a clear message ("could not write dashboard to <path>: <reason>") and
  exits non-zero. No traceback.
- **HTML injection safety:** every projection string (evidence, blockers,
  next_action, table names) is HTML-escaped before embedding. The projection is
  local committed data, but escaping is unconditional -- defense in depth.
- **Encoding:** the written file is UTF-8 without BOM and declares
  `<meta charset="utf-8">` (Arabic copy requires this). The handler prints only
  ASCII to the console (repo lesson: Windows charmap codec errors) -- e.g. it
  prints the output PATH, never the Arabic page content.

## 8. Testing

Because `render.py` is pure, the bulk of tests need no disk and no browser:

- **Unit (render, pure):**
  - `render_page` over a fixture projection produces HTML containing the expected
    table names, the 7 stage labels, and status classes.
  - **No-fabricated-score assertion (hard rule #9) -- correctly framed:** the rule
    governs numbers the dashboard *itself computes*, NOT characters in pass-through
    text. (Real committed evidence legitimately contains `%`, e.g. "9.65% missing"
    and "DiscountedTransactionRate = 50.37%".) So:
    - **KPI values are counts:** over a fixture, assert each KPI card value equals
      the expected INTEGER count (e.g. 2 tables, 1 publish-ready, 1 blocked) --
      never a percentage or adjective the dashboard invented.
    - **Evidence is verbatim, not mangled:** inject a fixture evidence string
      containing `50.37%` and assert it appears verbatim (escaped) in the output --
      proving `%` in output is expected pass-through, not a fabricated score.
    - Do NOT add a blanket "no `%` anywhere" grep -- it would fail on valid data.
  - Empty projection -> empty-state markup, not a crash.
  - Every projection string appears HTML-escaped (inject a `<script>`-bearing
    fixture string; assert it is escaped in output).
  - Status->color mapping is total: every one of the 4 statuses maps.
  - Output is one self-contained document: no external `href`/`src` to a remote
    host (assert no `http://`/`https://` asset refs; CSS + SVG inline).
- **Unit (generate, light disk):**
  - `generate(repo, tmp_out)` writes a file at the returned path, UTF-8, and the
    contents equal `render_page(build_status_projection(repo))`.
  - Unwritable path surfaces a clean error, not a traceback.
- **CLI:** `retail dashboard --help` lists `--out/--repo/--no-open`; the
  `_DISPATCH` row resolves to `dashboard_main`.
- **Governance (must pass before any commit):**
  - `retail check` exits 0 -- in particular **B1 raises no finding** on the new
    `cli/commands/dashboard.py` (no module-scope `http`/`socket` import).
  - `test_capability_inventory` passes -- the new verb has a `capabilities.yaml`
    entry (see s.9); an unlisted verb fails this test.
- Run with `PYTHONPATH=src` (repo lesson: avoids the stale global install) and
  respect the repo's ruff/CodeScene pre-push gates.

## 9. Repo-fit & governance

- **B1 never-execute (the decisive constraint):** static generation opens no
  socket and imports no `http`/`socket` at module scope, so `retail check`'s B1
  rule stays green. This is WHY the design generates a file instead of serving.
- **Option-B discipline:** the dashboard is a read-only projection consumer,
  introducing no new readiness logic and no score -- consistent with
  `status_surface.py`'s ratified contract. The "ONE sanctioned CLI addition"
  phrase is scoped to spec-109's status projection, not a global verb freeze
  (`_DISPATCH` already carries ~30 verbs), so adding a read-only render verb is
  permissible.
- **No new deps:** stdlib only (`webbrowser`, `pathlib`, `html`); nothing added
  to `pyproject.toml`. Keeps the driver-free / lazy-import posture.
- **CLI shape:** new verb = one `_DISPATCH` row + one lazy handler + one parser
  subcommand (mirroring `status`) **+ one typed entry in
  `docs/capabilities/capabilities.yaml`**. That inventory is a CLOSED-SCHEMA, typed
  manifest guarded by an O1-O8 fail-closed oracle (`test_capability_inventory` +
  `_capability_oracle`), not a flat allowlist -- a present-but-inconsistent entry
  fails differently than an absent one. The new record must carry EXACTLY the
  declared fields, mirroring the `retail-check` / `retail-status` entries:
  `id`, `name`, `summary`, `state`, `authority: agent-runnable`, `surface: cli`,
  `requirements: []`, `provenance: locally-verified`, `readiness_stage:
  not-stage-scoped`, `command: dashboard`, `references`/`dispatch: dashboard`,
  `documentation`. Classify honestly: it is CLI + agent-runnable + no requirement,
  but NOT on the public command surface (that is a separate promotion). Getting
  this entry right is its own plan step, not a footnote.
- **Public surface:** because this is a prototype-first build, it is NOT added to
  `distribution/public-command-surface.yaml` yet. Promoting it to a shipped
  public command is a separate, later decision (would need a wrapper template +
  allowlist entry + bundle + contract-test update).
- **Naming:** verb is `dashboard`. Note existing neighbors -- `dashboard_planner.py`,
  `dashboard_coordinator.py`, the `dashboard_ready` stage, and the
  `no_dashboard_before_metric_contracts` hard-stop. Those are about AUTHORING a
  Power BI dashboard for a table; this verb RENDERS the project readiness status.
  If the overlap reads as confusing at review, `status-dashboard` is the fallback
  name. (Decided: keep `dashboard` for the prototype; revisit at promotion.)
- **Windows/encoding:** ASCII-only console output (repo charmap lesson); the
  written HTML file is UTF-8 without BOM.

## 10. Open questions (none blocking)

- Master-detail vs. stacked cards on the Tables section: v1 ships **stacked
  per-table cards** in one static document (zero JS). A list->detail with
  selection can come later if a live-server variant is ever revisited.
- Stage labels in the UI: use **Arabic** labels (the design is RTL Arabic), with
  the English stage keys available as `title`/tooltip for traceability. Do NOT
  inherit `html_report.py`'s English labels by accident.
- Default output path `reports/dashboard/index.html` (the repo already has a
  `reports/` dir); `index.html` so `python -m http.server` serves it at `/`.
