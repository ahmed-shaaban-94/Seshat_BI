# Localhost Status Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `retail dashboard` CLI verb that renders the tool's existing per-table readiness status into one self-contained static HTML file (Arabic RTL, navy/gold/teal) and auto-opens it in the browser.

**Architecture:** A read-only view over the existing `seshat.status_surface.build_status_projection()`. Four small units: a pure renderer (`dict -> HTML str`), a CSS-token constant, a thin disk-writing generator, and a CLI handler that writes + auto-opens. No server, no socket (rule B1), no new dependencies.

**Tech Stack:** Python 3.13 stdlib only (`html`, `pathlib`, `webbrowser`), pytest. Reuses `seshat.status_surface` (existing) and the escaping idiom of `seshat.demo.html_report`.

## Global Constraints

- **Python floor:** `>=3.13` (pyproject.toml). Type-annotate every signature.
- **Stdlib only:** no new dependency in `pyproject.toml`. Allowed stdlib: `html`, `pathlib`, `webbrowser`, `argparse`, `json` (tests). FORBIDDEN anywhere in `src/seshat/`: module-scope import of `http`, `socket`, `requests`, `httpx`, `urllib.request` (rule B1 in `src/seshat/rules/never_execute.py`).
- **Read-only + no fabricated score:** the dashboard never computes/derives/advances a stage and never emits a numeric/percent/confidence score it invented (repo hard rule #9). KPI numbers are integer COUNTS only. Evidence strings (which may contain literal `%`) pass through verbatim + escaped.
- **Encoding:** written HTML file is UTF-8 **without BOM** and declares `<meta charset="utf-8">`. Console output is ASCII only (Windows charmap lesson) — print the output PATH, never Arabic page content.
- **HTML safety:** every projection string is HTML-escaped before embedding (`html.escape(s, quote=True)`).
- **Self-contained:** all CSS and SVG are inline; the file references NO remote `http(s)://` asset.
- **Canonical stage order (7):** `source_ready, mapping_ready, silver_ready, gold_ready, semantic_model_ready, dashboard_ready, publish_ready`.
- **Status enum (4):** `not_started, blocked, warning, pass`.
- **Run tests with `PYTHONPATH=src`** (repo lesson: bare `python -m seshat.cli` hits a stale global install). Do NOT pass `-p no:cov` (false-greens against pyproject addopts).
- **Worktree:** all work happens on branch `worktree-dashboard` in `.claude/worktrees/dashboard`.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/seshat/dashboard/__init__.py` | Package marker (empty). |
| `src/seshat/dashboard/theme.py` | `DASHBOARD_CSS: str` — the design tokens as one CSS constant. |
| `src/seshat/dashboard/render.py` | **Pure.** `render_page(projection: dict) -> str` + private helpers. All view logic. |
| `src/seshat/dashboard/generate.py` | `generate(repo_root, out_path=None) -> Path` — reads projection, renders, writes file. Only disk unit. |
| `src/seshat/cli/commands/dashboard.py` | `dashboard_main(args) -> int` — CLI handler; writes + auto-opens. |
| `src/seshat/cli/parser.py` | Add `_add_dashboard_parser(sub)` + call it in `_build_parser`. |
| `src/seshat/cli/__init__.py` | Add one `_DISPATCH` row (lazy import). |
| `docs/capabilities/capabilities.yaml` | Add one typed `retail-dashboard` record. |
| `.gitignore` | Ignore the generated `reports/dashboard/` output. |
| `tests/unit/test_dashboard_render.py` | Pure-render tests. |
| `tests/unit/test_dashboard_generate.py` | Generator disk tests. |
| `tests/unit/test_dashboard_cli.py` | CLI wiring test. |

Note: there is NO `server.py`. The spec's B1 finding forbids it.

---

## Task 1: Renderer skeleton + status→color mapping (pure)

Establishes the pure render module with the one place status maps to color, and the empty-state path. Everything else builds on `render_page`.

**Files:**
- Create: `src/seshat/dashboard/__init__.py` (empty)
- Create: `src/seshat/dashboard/render.py`
- Test: `tests/unit/test_dashboard_render.py`

**Interfaces:**
- Consumes: nothing (pure; input is a plain dict shaped like `build_status_projection`'s output).
- Produces:
  - `render_page(projection: dict) -> str` — full self-contained HTML document.
  - `_STATUS_STYLE: dict[str, tuple[str, str]]` — `{status: (fg_hex, bg_hex)}` for all 4 statuses.
  - `_STAGE_ORDER: tuple[str, ...]` — the 7 stage keys in canonical order.
  - `_STAGE_LABELS_AR: dict[str, str]` — Arabic label per stage key.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_dashboard_render.py
import pytest

pytestmark = pytest.mark.unit

from seshat.dashboard.render import (
    render_page,
    _STATUS_STYLE,
    _STAGE_ORDER,
    _STAGE_LABELS_AR,
)


def test_status_style_covers_all_four_statuses():
    assert set(_STATUS_STYLE) == {"not_started", "blocked", "warning", "pass"}
    for fg, bg in _STATUS_STYLE.values():
        assert fg.startswith("#") and bg.startswith("#")


def test_stage_order_is_the_canonical_seven():
    assert _STAGE_ORDER == (
        "source_ready",
        "mapping_ready",
        "silver_ready",
        "gold_ready",
        "semantic_model_ready",
        "dashboard_ready",
        "publish_ready",
    )
    assert set(_STAGE_LABELS_AR) == set(_STAGE_ORDER)


def test_render_page_empty_projection_shows_empty_state_not_crash():
    html = render_page({"tables": []})
    assert "<!DOCTYPE html>" in html
    assert 'dir="rtl"' in html
    assert "mappings/" in html  # the empty-state hint mentions where files go


def test_render_page_is_self_contained_no_remote_assets():
    html = render_page({"tables": []})
    assert "http://" not in html
    assert "https://" not in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_render.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'seshat.dashboard'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/seshat/dashboard/__init__.py` as an empty file.

```python
# src/seshat/dashboard/render.py
"""Pure renderer: readiness projection dict -> one self-contained HTML string.

Read-only VIEW. No I/O, no socket, no fabricated score (repo hard rule #9):
the only numbers this module emits are integer COUNTS over the projection;
evidence strings (which may contain a literal '%') pass through verbatim and
escaped. Mirrors the escaping posture of seshat.demo.html_report.
"""

from __future__ import annotations

import html

_STAGE_ORDER: tuple[str, ...] = (
    "source_ready",
    "mapping_ready",
    "silver_ready",
    "gold_ready",
    "semantic_model_ready",
    "dashboard_ready",
    "publish_ready",
)

_STAGE_LABELS_AR: dict[str, str] = {
    "source_ready": "المصدر",
    "mapping_ready": "التوصيف",
    "silver_ready": "الفضي",
    "gold_ready": "الذهبي",
    "semantic_model_ready": "النموذج الدلالي",
    "dashboard_ready": "لوحة المعلومات",
    "publish_ready": "النشر",
}

# The ONE place status -> (foreground, background tint) lives.
_STATUS_STYLE: dict[str, tuple[str, str]] = {
    "pass": ("#1F8A54", "#E7F3EC"),
    "warning": ("#B5832A", "#FEF4E1"),
    "blocked": ("#C0392B", "#FDECEC"),
    "not_started": ("#6B7480", "#F1F5F9"),
}


def _esc(value: object) -> str:
    """HTML-escape any projection value (defense-in-depth; quote=True)."""
    return html.escape(str(value), quote=True)


def render_page(projection: dict) -> str:
    """Render the full self-contained dashboard document for ``projection``.

    ``projection`` is the shape returned by
    ``seshat.status_surface.build_status_projection`` — ``{"tables": [...]}``.
    An empty table list renders a friendly empty state, never an error.
    """
    tables = projection.get("tables", [])
    if not tables:
        body = (
            '<div class="empty">لا توجد ملفات readiness-status.yaml مُودعة تحت '
            "mappings/.</div>"
        )
    else:
        body = "<div>tables placeholder</div>"  # replaced in Task 3
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ar" dir="rtl">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Seshat BI — لوحة الحالة</title>\n"
        "<style>/* css placeholder */</style>\n"
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_render.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/seshat/dashboard/__init__.py src/seshat/dashboard/render.py tests/unit/test_dashboard_render.py
git commit -m "feat: dashboard renderer skeleton + status/stage constants"
```

---

## Task 2: Theme CSS constant + wire it into the page

Extracts the design tokens into one CSS string so colors live in one place, and inlines it into `render_page`.

**Files:**
- Create: `src/seshat/dashboard/theme.py`
- Modify: `src/seshat/dashboard/render.py` (import + inline `DASHBOARD_CSS`)
- Test: `tests/unit/test_dashboard_render.py` (add cases)

**Interfaces:**
- Consumes: nothing.
- Produces: `DASHBOARD_CSS: str` (a non-empty CSS string, no `@import`, no remote URL).

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_dashboard_render.py`:

```python
from seshat.dashboard.theme import DASHBOARD_CSS


def test_theme_css_is_local_only():
    assert DASHBOARD_CSS.strip()
    assert "@import" not in DASHBOARD_CSS
    assert "http://" not in DASHBOARD_CSS and "https://" not in DASHBOARD_CSS


def test_render_page_inlines_the_theme_css():
    html_out = render_page({"tables": []})
    # a distinctive token from the brand palette must appear inline
    assert "#001E35" in html_out  # navy sidebar
    assert "<style>" in html_out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_render.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'seshat.dashboard.theme'`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/seshat/dashboard/theme.py
"""Design tokens for the status dashboard as one inline CSS string.

Ported from the "Seshat BI — Control Center" handoff (colors_and_type.css +
the prototype's inline shell styles). No @import, no web fonts (fallback
stacks only), no remote asset — the output HTML must be self-contained.
"""

from __future__ import annotations

DASHBOARD_CSS: str = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: 'Segoe UI', Tahoma, system-ui, 'Inter', sans-serif;
  background: #F4F6F9; color: #1B2A3A;
}
.app { display: flex; min-height: 100vh; }
.sidebar {
  width: 224px; flex: none; background: #001E35; color: #F7F1E7;
  position: sticky; top: 0; height: 100vh; padding: 22px 16px;
}
.brand { font-size: 21px; font-weight: 700; letter-spacing: .06em; }
.brand small { display: block; font-size: 11px; color: #9FB2C4; font-weight: 500; }
.nav a {
  display: block; color: #A9BACB; text-decoration: none; padding: 12px 14px;
  border-radius: 11px; font-size: 14.5px; margin-top: 4px;
}
.nav a:hover { color: #F7F1E7; }
main { flex: 1; min-width: 0; padding: 24px 34px 48px; overflow: auto; }
h1 { font-size: 25px; font-weight: 700; color: #0F2033; margin: 0 0 4px; }
.sub { color: #64748B; font-size: 13px; margin: 0 0 22px; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 22px; }
.card {
  background: #fff; border: 1px solid #EAEEF3; border-radius: 16px;
  padding: 22px 24px; box-shadow: 0 1px 2px rgba(16,32,51,.04);
}
.kpi .label { font-size: 14px; color: #64748B; font-weight: 600; }
.kpi .value { font-size: 40px; font-weight: 800; color: #0F2033; line-height: 1; margin-top: 6px; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: right; padding: 12px 16px; font-size: 13px; }
th { background: #F8FAFC; color: #64748B; font-weight: 600; font-size: 12.5px; }
td { border-top: 1px solid #EEF1F5; color: #334155; }
.chip { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin: 0 2px; }
.stepper { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.stage {
  flex: 1 1 120px; text-align: center; padding: 10px 8px; border-radius: 12px;
  font-size: 12.5px; font-weight: 600;
}
.evidence { margin: 6px 0 0; padding-inline-start: 18px; color: #475569; font-size: 12.5px; }
.blocker {
  background: #FDECEC; color: #C0392B; border-radius: 10px; padding: 10px 14px;
  font-size: 12.5px; margin-top: 8px;
}
.next { color: #0F2033; font-weight: 600; margin-top: 10px; }
a.tealref { color: #0C7C7A; text-decoration: none; }
.empty { padding: 60px; text-align: center; color: #64748B; font-size: 15px; }
.meta { color: #64748B; font-size: 12.5px; margin-bottom: 14px; }
"""
```

Modify `render.py`: import the constant and inline it.

```python
# at top of render.py, after `import html`
from seshat.dashboard.theme import DASHBOARD_CSS
```

Replace the `"<style>/* css placeholder */</style>\n"` line in `render_page` with:

```python
        f"<style>{DASHBOARD_CSS}</style>\n"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_render.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add src/seshat/dashboard/theme.py src/seshat/dashboard/render.py tests/unit/test_dashboard_render.py
git commit -m "feat: dashboard theme CSS constant inlined into page"
```

---

## Task 3: Home + Tables body render (the real view)

Fills in the actual content: KPI count cards, per-table summary table, and the per-table 7-stage cards with evidence/blockers/next_action. This is where hard-rule-#9 (counts-not-scores) and escaping are proven.

**Files:**
- Modify: `src/seshat/dashboard/render.py`
- Test: `tests/unit/test_dashboard_render.py` (add cases with a two-table fixture)

**Interfaces:**
- Consumes: `_STATUS_STYLE`, `_STAGE_ORDER`, `_STAGE_LABELS_AR`, `_esc` (Task 1); `DASHBOARD_CSS` (Task 2).
- Produces: `render_page` now emits Home + Tables sections. New private helpers `_kpis(tables)`, `_summary_table(tables)`, `_table_card(t)`, `_count_blocked(tables)`.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_dashboard_render.py`:

```python
_FIXTURE = {
    "tables": [
        {
            "table": "bronze.retail_store_sales",
            "source_path": "mappings/retail_store_sales/readiness-status.yaml",
            "current_stage": "publish_ready",
            "stages": {
                name: {"status": "pass", "evidence": [], "blocking_reasons": []}
                for name in _STAGE_ORDER
            },
            "blocking_reasons": [],
            "next_action": "All seven stages pass.",
        },
        {
            "table": "bronze.demo_sample_orders",
            "source_path": "mappings/demo_sample_orders/readiness-status.yaml",
            "current_stage": "gold_ready",
            "stages": {
                "source_ready": {"status": "pass", "evidence": ["50.37% known"], "blocking_reasons": []},
                "gold_ready": {"status": "blocked", "evidence": [], "blocking_reasons": ["no DB offline"]},
            },
            "blocking_reasons": ["no DB offline"],
            "next_action": "Run the optional live leg.",
        },
    ]
}


def test_kpi_values_are_integer_counts_not_scores():
    html_out = render_page(_FIXTURE)
    # total tables = 2, publish-ready = 1, blocked = 1
    assert ">2<" in html_out          # total tables count
    assert ">1<" in html_out          # publish-ready / blocked counts
    assert "%" not in html_out.split("<table")[0]  # no % in the KPI/header region


def test_evidence_percent_passes_through_verbatim():
    html_out = render_page(_FIXTURE)
    assert "50.37%" in html_out  # evidence '%' is legitimate pass-through, not a score


def test_table_names_and_stage_labels_present():
    html_out = render_page(_FIXTURE)
    assert "bronze.retail_store_sales" in html_out
    assert "bronze.demo_sample_orders" in html_out
    for label in _STAGE_LABELS_AR.values():
        assert label in html_out


def test_blocked_stage_uses_blocked_color_and_shows_reason():
    html_out = render_page(_FIXTURE)
    assert "#C0392B" in html_out          # blocked fg color
    assert "no DB offline" in html_out    # blocking reason rendered


def test_injected_markup_is_escaped():
    evil = {
        "tables": [
            {
                "table": "<script>alert(1)</script>",
                "source_path": "mappings/x/readiness-status.yaml",
                "current_stage": "source_ready",
                "stages": {"source_ready": {"status": "pass", "evidence": ["<b>x</b>"], "blocking_reasons": []}},
                "blocking_reasons": [],
                "next_action": "<img src=x onerror=y>",
            }
        ]
    }
    html_out = render_page(evil)
    assert "<script>alert(1)</script>" not in html_out
    assert "&lt;script&gt;" in html_out
    assert "onerror=y" not in html_out or "&lt;img" in html_out


def test_table_has_anchor_id_for_in_page_nav():
    html_out = render_page(_FIXTURE)
    assert 'id="table-bronze.retail_store_sales"' in html_out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_render.py -v`
Expected: FAIL — new tests fail (placeholder body has no KPIs/tables/anchors).

- [ ] **Step 3: Write minimal implementation**

Add these helpers to `render.py` (above `render_page`):

```python
def _chip(status: str) -> str:
    fg, bg = _STATUS_STYLE.get(status, _STATUS_STYLE["not_started"])
    return f'<span class="chip" style="color:{fg};background:{bg};">{_esc(status)}</span>'


def _count_blocked(tables: list[dict]) -> int:
    total = 0
    for t in tables:
        stages = t.get("stages", {})
        any_blocked = any(
            isinstance(s, dict) and s.get("status") == "blocked" for s in stages.values()
        )
        if any_blocked or t.get("blocking_reasons"):
            total += 1
    return total


def _kpis(tables: list[dict]) -> str:
    total = len(tables)
    publish_ready = sum(1 for t in tables if t.get("current_stage") == "publish_ready")
    blocked = _count_blocked(tables)
    needs_attention = total - publish_ready
    cards = [
        ("إجمالي الجداول", total),
        ("جاهز للنشر", publish_ready),
        ("محظور", blocked),
        ("يحتاج انتباه", needs_attention),
    ]
    inner = "".join(
        f'<div class="card kpi"><div class="label">{_esc(label)}</div>'
        f'<div class="value">{value}</div></div>'
        for label, value in cards
    )
    return f'<div class="kpis">{inner}</div>'


def _stage_dots(t: dict) -> str:
    stages = t.get("stages", {})
    dots = []
    for name in _STAGE_ORDER:
        block = stages.get(name) or {}
        status = block.get("status", "not_started")
        fg, _bg = _STATUS_STYLE.get(status, _STATUS_STYLE["not_started"])
        dots.append(
            f'<span class="dot" style="background:{fg};" title="{_esc(_STAGE_LABELS_AR[name])}"></span>'
        )
    return "".join(dots)


def _summary_table(tables: list[dict]) -> str:
    rows = []
    for t in tables:
        name = t.get("table", t.get("source_path", ""))
        rows.append(
            "<tr>"
            f'<td><a class="tealref" href="#table-{_esc(name)}">{_esc(name)}</a></td>'
            f"<td>{_chip(t.get('current_stage') or 'not_started')}</td>"
            f"<td>{_stage_dots(t)}</td>"
            f"<td>{len(t.get('blocking_reasons') or [])}</td>"
            f"<td>{_esc(t.get('next_action') or '')}</td>"
            "</tr>"
        )
    return (
        '<div class="card"><table><thead><tr>'
        "<th>الجدول</th><th>المرحلة الحالية</th><th>المراحل</th>"
        "<th>المعرقلات</th><th>الإجراء التالي</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _table_card(t: dict) -> str:
    name = t.get("table", t.get("source_path", ""))
    stages = t.get("stages", {})
    stage_html = []
    for stage_name in _STAGE_ORDER:
        block = stages.get(stage_name) or {}
        status = block.get("status", "not_started")
        fg, bg = _STATUS_STYLE.get(status, _STATUS_STYLE["not_started"])
        evidence = block.get("evidence") or []
        reasons = block.get("blocking_reasons") or []
        ev = ""
        if evidence:
            ev = '<ul class="evidence">' + "".join(
                f"<li>{_esc(e)}</li>" for e in evidence
            ) + "</ul>"
        rs = "".join(f'<div class="blocker">{_esc(r)}</div>' for r in reasons)
        stage_html.append(
            f'<div class="stage" style="color:{fg};background:{bg};">'
            f"{_esc(_STAGE_LABELS_AR[stage_name])}<br>{_esc(status)}{ev}{rs}</div>"
        )
    top_blockers = "".join(
        f'<div class="blocker">{_esc(r)}</div>' for r in (t.get("blocking_reasons") or [])
    )
    return (
        f'<div class="card" id="table-{_esc(name)}">'
        f"<h3>{_esc(name)} {_chip(t.get('current_stage') or 'not_started')}</h3>"
        f'<div class="meta">{_esc(t.get("source_path", ""))}</div>'
        f'<div class="stepper">{"".join(stage_html)}</div>'
        f"{top_blockers}"
        f'<div class="next">الإجراء التالي: {_esc(t.get("next_action") or "-")}</div>'
        "</div>"
    )
```

Replace the `else: body = "<div>tables placeholder</div>"` branch in `render_page` with:

```python
    else:
        cards = "".join(f'<div style="margin-bottom:22px;">{_table_card(t)}</div>' for t in tables)
        body = (
            '<h1>صحة المشروع</h1>'
            '<p class="sub">حالة جاهزية كل جدول عبر مراحل الحوكمة السبع.</p>'
            f"{_kpis(tables)}"
            f"{_summary_table(tables)}"
            f'<h1 id="tables" style="margin-top:32px;">تفاصيل الجداول</h1>'
            f"{cards}"
        )
```

Also wrap `body` in the shell layout — change the `f"{body}\n"` line in `render_page`'s return to:

```python
        '<div class="app">\n'
        '<aside class="sidebar"><div class="brand">Seshat<small>BI لوحة الحالة</small></div>'
        '<nav class="nav"><a href="#">الرئيسية</a><a href="#tables">الجداول</a></nav></aside>\n'
        f"<main>{body}</main>\n"
        "</div>\n"
```

(Remove the old `f"{body}\n"` line.)

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_render.py -v`
Expected: PASS (all render tests green).

- [ ] **Step 5: Commit**

```bash
git add src/seshat/dashboard/render.py tests/unit/test_dashboard_render.py
git commit -m "feat: dashboard Home KPIs + per-table 7-stage cards (counts, escaped)"
```

---

## Task 4: Generator (reads projection, writes file)

The only disk-touching unit. Bridges the existing `build_status_projection` to `render_page` and writes the file.

**Files:**
- Create: `src/seshat/dashboard/generate.py`
- Modify: `.gitignore` (ignore generated output)
- Test: `tests/unit/test_dashboard_generate.py`

**Interfaces:**
- Consumes: `seshat.status_surface.build_status_projection(repo_root) -> dict` (existing); `render_page` (Task 1-3).
- Produces: `generate(repo_root: Path | str = ".", out_path: Path | str | None = None) -> Path`. Default `out_path` = `<repo_root>/reports/dashboard/index.html`. Returns the written path. Writes UTF-8 no BOM.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_dashboard_generate.py
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from seshat.dashboard.generate import generate
from seshat.dashboard.render import render_page
from seshat.status_surface import build_status_projection


def _make_repo(tmp_path: Path) -> Path:
    d = tmp_path / "mappings" / "orders"
    d.mkdir(parents=True)
    (d / "readiness-status.yaml").write_text(
        'table: "bronze.orders"\n'
        'current_stage: "source_ready"\n'
        "stages:\n"
        "  source_ready:\n"
        '    status: "pass"\n'
        "    evidence: []\n"
        "    blocking_reasons: []\n"
        'next_action: "next"\n',
        encoding="utf-8",
    )
    return tmp_path


def test_generate_writes_file_at_returned_path(tmp_path):
    repo = _make_repo(tmp_path)
    out = generate(repo)
    assert out.exists()
    assert out == repo / "reports" / "dashboard" / "index.html"


def test_generate_output_equals_render_of_projection(tmp_path):
    repo = _make_repo(tmp_path)
    out = generate(repo)
    written = out.read_text(encoding="utf-8")
    expected = render_page(build_status_projection(repo))
    assert written == expected


def test_generate_writes_utf8_without_bom(tmp_path):
    repo = _make_repo(tmp_path)
    out = generate(repo)
    raw = out.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")  # no BOM


def test_generate_custom_out_path(tmp_path):
    repo = _make_repo(tmp_path)
    target = tmp_path / "custom" / "dash.html"
    out = generate(repo, target)
    assert out == target and target.exists()


def test_generate_unwritable_path_raises_oserror(tmp_path):
    repo = _make_repo(tmp_path)
    # a path whose parent is a FILE, not a dir -> mkdir fails
    blocker = tmp_path / "afile"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(OSError):
        generate(repo, blocker / "nested" / "index.html")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_generate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'seshat.dashboard.generate'`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/seshat/dashboard/generate.py
"""Generate the static status-dashboard HTML file.

The ONLY disk-touching unit. Reads the existing read-only status projection,
renders it via the pure renderer, and writes ONE self-contained HTML file.
No socket, no network, no DB (rule B1). UTF-8 without BOM.
"""

from __future__ import annotations

from pathlib import Path

from seshat.dashboard.render import render_page
from seshat.status_surface import build_status_projection


def generate(
    repo_root: Path | str = ".", out_path: Path | str | None = None
) -> Path:
    """Render the dashboard for ``repo_root`` and write it to ``out_path``.

    Defaults ``out_path`` to ``<repo_root>/reports/dashboard/index.html``.
    Creates parent directories. Returns the written path. Raises ``OSError``
    if the path cannot be created/written (the caller renders a clean error).
    """
    root = Path(repo_root)
    target = Path(out_path) if out_path is not None else root / "reports" / "dashboard" / "index.html"
    projection = build_status_projection(root)
    document = render_page(projection)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")  # utf-8 (no BOM)
    return target
```

Modify `.gitignore` — append these two lines:

```
# Generated status dashboard (regenerated by `retail dashboard`)
reports/dashboard/
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_generate.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add src/seshat/dashboard/generate.py .gitignore tests/unit/test_dashboard_generate.py
git commit -m "feat: dashboard generator writes self-contained HTML file"
```

---

## Task 5: CLI handler + parser + dispatch wiring

Wires `retail dashboard` end-to-end: parser subcommand, dispatch row, and the handler that writes + auto-opens.

**Files:**
- Create: `src/seshat/cli/commands/dashboard.py`
- Modify: `src/seshat/cli/parser.py` (add `_add_dashboard_parser`, call it in `_build_parser`)
- Modify: `src/seshat/cli/__init__.py` (add `_DISPATCH` row)
- Test: `tests/unit/test_dashboard_cli.py`

**Interfaces:**
- Consumes: `generate(repo_root, out_path)` (Task 4).
- Produces: `dashboard_main(args) -> int` where `args` has `.repo: str`, `.out: str | None`, `.no_open: bool`. Returns 0 on success, 1 on `OSError`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_dashboard_cli.py
import argparse
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from seshat.cli.commands.dashboard import dashboard_main
from seshat.cli.parser import _build_parser


def _make_repo(tmp_path: Path) -> Path:
    d = tmp_path / "mappings" / "orders"
    d.mkdir(parents=True)
    (d / "readiness-status.yaml").write_text(
        'table: "bronze.orders"\ncurrent_stage: "source_ready"\n'
        "stages:\n  source_ready:\n    status: \"pass\"\n"
        "    evidence: []\n    blocking_reasons: []\n"
        'next_action: "next"\n',
        encoding="utf-8",
    )
    return tmp_path


def test_parser_registers_dashboard_with_flags():
    parser = _build_parser()
    ns = parser.parse_args(["dashboard", "--repo", "x", "--out", "y", "--no-open"])
    assert ns.command == "dashboard"
    assert ns.repo == "x" and ns.out == "y" and ns.no_open is True


def test_dashboard_main_writes_and_returns_zero(tmp_path, capsys):
    repo = _make_repo(tmp_path)
    out = tmp_path / "d.html"
    args = argparse.Namespace(repo=str(repo), out=str(out), no_open=True)
    rc = dashboard_main(args)
    assert rc == 0
    assert out.exists()
    captured = capsys.readouterr().out
    assert str(out) in captured
    assert captured.isascii()  # console output must be ASCII


def test_dashboard_main_oserror_returns_one(tmp_path, capsys):
    repo = _make_repo(tmp_path)
    blocker = tmp_path / "afile"
    blocker.write_text("x", encoding="utf-8")
    args = argparse.Namespace(
        repo=str(repo), out=str(blocker / "nested" / "index.html"), no_open=True
    )
    rc = dashboard_main(args)
    assert rc == 1


def test_dispatch_has_dashboard_row():
    from seshat import cli
    assert "dashboard" in cli._DISPATCH
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'seshat.cli.commands.dashboard'`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/seshat/cli/commands/dashboard.py
"""`dashboard` handler: render the readiness status to a static HTML file and
open it in the browser.

Read-only VIEW over committed readiness state. It writes ONE HTML file and
optionally opens it; it never opens a socket, DB, or network connection
(rule B1). ``webbrowser`` is imported LAZILY inside the handler.
"""

from __future__ import annotations

import argparse


def dashboard_main(args: argparse.Namespace) -> int:
    """Handler for ``dashboard``. Writes the dashboard HTML, prints its path
    (ASCII only), and (unless ``--no-open``) opens it. Returns 0 on success,
    1 if the file could not be written."""
    from seshat.dashboard.generate import generate

    repo = getattr(args, "repo", ".")
    out = getattr(args, "out", None)
    try:
        written = generate(repo, out)
    except OSError as exc:
        print(f"error: could not write dashboard: {exc}")
        return 1

    print(f"Dashboard written: {written}")
    if not getattr(args, "no_open", False):
        import webbrowser  # lazy: keep the CLI import chain socket-free (B1)

        webbrowser.open(written.resolve().as_uri())
    return 0
```

Add to `src/seshat/cli/parser.py` — a new helper (place it right after `_add_status_parser`, near line 114):

```python
def _add_dashboard_parser(sub: argparse._SubParsersAction) -> None:
    """`dashboard`: render committed readiness status to a self-contained
    static HTML file and open it. Read-only VIEW; no server, no socket (B1)."""
    p = sub.add_parser(
        "dashboard",
        help=(
            "render committed readiness status to a self-contained HTML file "
            "and open it (read-only view; no server)"
        ),
    )
    p.add_argument("--repo", default=".", help="repo root to read status from")
    p.add_argument(
        "--out",
        default=None,
        help="output HTML path (default: <repo>/reports/dashboard/index.html)",
    )
    p.add_argument(
        "--no-open",
        dest="no_open",
        action="store_true",
        help="write the file but do not open it in a browser",
    )
```

In `_build_parser` (near line 1097, right after `_add_status_parser(sub)`), add:

```python
    _add_dashboard_parser(sub)
```

Add to `src/seshat/cli/__init__.py` `_DISPATCH` dict (right after the `"status"` row near line 167):

```python
    "dashboard": _lazy(".commands.dashboard", "dashboard_main"),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_cli.py -v`
Expected: PASS (4 passed). Note: `test_dashboard_main_writes_and_returns_zero` passes `--no-open` so no browser opens.

- [ ] **Step 5: Commit**

```bash
git add src/seshat/cli/commands/dashboard.py src/seshat/cli/parser.py src/seshat/cli/__init__.py tests/unit/test_dashboard_cli.py
git commit -m "feat: retail dashboard CLI verb (write + auto-open static HTML)"
```

---

## Task 6: Capabilities inventory entry (governance gate)

Adds the typed `capabilities.yaml` record so `test_capability_inventory` (O1–O8 oracle) stays green. This task's "test" is the existing inventory test.

**Files:**
- Modify: `docs/capabilities/capabilities.yaml` (add one record)

**Interfaces:**
- Consumes: the `_DISPATCH["dashboard"]` wiring (Task 5) — the O2 oracle requires a `references.dispatch` covering the wired verb.
- Produces: nothing code-facing.

- [ ] **Step 1: Run the inventory test to see it fail on the unlisted verb**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_capability_inventory.py -v`
Expected: FAIL — an O2-style "wired command not covered by any entry" error naming `dashboard` (an unlisted `_DISPATCH` verb).

- [ ] **Step 2: Add the capabilities record**

In `docs/capabilities/capabilities.yaml`, in the "Available now — CLI, shipped, agent-runnable, no requirement" section (right after the `retail-status` record, ~line 118), add:

```yaml
  - id: retail-dashboard
    name: "retail / seshat dashboard"
    summary: "Read-only static HTML view of committed per-table readiness status (Home health overview + per-table 7-stage cards). Writes one self-contained file and opens it; no server."
    state: shipped
    authority: agent-runnable
    surface: cli
    requirements: []
    provenance: locally-verified
    readiness_stage: not-stage-scoped
    command: "dashboard"
    documentation: "docs/superpowers/specs/2026-07-19-localhost-status-dashboard-design.md"
    references:
      dispatch: "dashboard"
```

- [ ] **Step 3: Run the inventory test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_capability_inventory.py -v`
Expected: PASS. Note: the closed-schema check (`set(record) == DECLARED_RECORD_FIELDS`) runs against the BUILT inventory record, not the raw YAML — so `references` in the source YAML is correct and required (the O1/O2 oracle reads `references.dispatch` to cover the wired verb). Include the 11 declared fields shown above plus `references`; omit `group` (nullable/unused, as `retail-status` does).

- [ ] **Step 4: Commit**

```bash
git add docs/capabilities/capabilities.yaml
git commit -m "chore: capabilities inventory entry for retail dashboard verb"
```

---

## Task 7: Full-suite + governance gate verification

Proves the whole feature is green against the repo's real gates before any PR decision. No new code unless a gate fails.

**Files:** none (verification only; fixes are folded back into the relevant task's files if a gate fails).

- [ ] **Step 1: Run the full dashboard + capability test set**

Run: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_render.py tests/unit/test_dashboard_generate.py tests/unit/test_dashboard_cli.py tests/unit/test_capability_inventory.py -v`
Expected: PASS (all).

- [ ] **Step 2: Run the static governance gate (B1 is the critical one)**

Run: `PYTHONPATH=src python -m seshat.cli check --repo .`
Expected: exit 0. In particular NO B1 finding on `src/seshat/cli/commands/dashboard.py` or any `src/seshat/dashboard/*.py` (no module-scope `http`/`socket` import — `webbrowser` is lazy and not on B1's denylist).

- [ ] **Step 3: Ruff format + lint check (CI parity)**

Run: `ruff format --check src tests scripts && ruff check src/seshat/dashboard src/seshat/cli/commands/dashboard.py tests/unit/test_dashboard_render.py tests/unit/test_dashboard_generate.py tests/unit/test_dashboard_cli.py`
Expected: both clean. If `ruff format --check` reports a diff, run `ruff format src tests scripts` and re-commit.

- [ ] **Step 4: Smoke-test the real command against committed sample data**

Run: `PYTHONPATH=src python -m seshat.cli dashboard --repo . --out reports/dashboard/index.html --no-open`
Expected: prints `Dashboard written: ...reports/dashboard/index.html`; the file exists and contains `bronze.retail_store_sales` and `bronze.demo_sample_orders`. (Open it manually in a browser to eyeball the Arabic RTL layout.)

- [ ] **Step 5: Commit any gate fixes**

```bash
git add -A
git commit -m "chore: satisfy governance gates for dashboard verb"
```

(If Steps 1–4 were all green with no changes, skip this commit.)

---

## Self-Review

**Spec coverage:**
- Purpose / read-only view → Tasks 1–4. ✓
- Scope: Home + Tables only → Task 3. ✓
- Generate-static-HTML + auto-open (not server) → Tasks 4–5. ✓
- B1 compliance (no socket/http) → design honored throughout; verified Task 7 Step 2. ✓
- No fabricated score / counts only → Task 3 tests. ✓
- Evidence `%` verbatim → Task 3 test `test_evidence_percent_passes_through_verbatim`. ✓
- HTML escaping → Task 3 test `test_injected_markup_is_escaped`. ✓
- Empty-state graceful → Task 1 test. ✓
- Self-contained (no remote assets) → Task 1 + Task 2 tests. ✓
- UTF-8 no BOM / ASCII console → Task 4 + Task 5 tests. ✓
- capabilities.yaml typed entry → Task 6. ✓
- Not on public command surface → intentionally omitted (no distribution/ change). ✓
- Arabic labels + English keys as tooltip → `_STAGE_LABELS_AR` + `title=` in `_stage_dots`. ✓
- Stacked per-table cards, in-page anchors → Task 3 (`id="table-..."`, `href="#table-..."`). ✓
- Default output `reports/dashboard/index.html` + gitignore → Task 4. ✓

**Placeholder scan:** No TBD/TODO; every code step shows full code; no "similar to Task N". ✓

**Type consistency:** `render_page(dict) -> str`, `generate(repo_root, out_path) -> Path`, `dashboard_main(args) -> int` used consistently across tasks and tests. Helper names (`_kpis`, `_summary_table`, `_table_card`, `_stage_dots`, `_chip`, `_count_blocked`, `_esc`) defined in Task 1/3 and not renamed later. ✓
