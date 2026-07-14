"""US5 accessibility / responsiveness / RTL coverage (spec 127).

The shell aligns to the SHIPPED spec-102 thresholds (``seshat.color``'s WCAG
contrast ratio and CIE76 delta-E, the same arithmetic the CT1/CT3 governance
rules apply) rather than inventing new criteria (FR-022). It must reflow at a
narrow viewport with no horizontal body scroll, and RTL/Arabic must render
correctly with the shipped Explorer assets left byte-unchanged (FR-023/024/025,
INV-6)."""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.color import contrast_ratio, delta_e76
from seshat.showcase.build import build_showcase_bundle, render_showcase_html

pytestmark = pytest.mark.integration

_REPO = Path(__file__).resolve().parents[2]
_EXPLORER_ASSETS = _REPO / "src/seshat/explorer/assets"

# The showcase shell's own declared palette (src/seshat/showcase/assets/showcase.css).
_PAPER = "#ffffff"
_NAVY = "#001e35"
_IVORY = "#f2ede1"
_INK = "#14222e"
_MUTED = "#4b5560"
_STATUS_COLORS = {
    "pass": "#0b7f70",
    "blocked": "#a4293a",
    "warning": "#8a6200",
    "idle": "#5a6570",
}

_TEXT_CONTRAST_FLOOR = 4.5  # WCAG AA for normal text (matches design_contrast.py)
# near-collapse guard, same concept as design_categorical_distinctness.py's floor
_CATEGORICAL_DELTA_FLOOR = 15.0


def test_shell_palette_meets_the_shipped_contrast_floor() -> None:
    assert contrast_ratio(_INK, _PAPER) >= _TEXT_CONTRAST_FLOOR
    assert contrast_ratio(_MUTED, _PAPER) >= _TEXT_CONTRAST_FLOOR
    assert contrast_ratio(_IVORY, _NAVY) >= _TEXT_CONTRAST_FLOOR


def test_shell_status_colors_meet_the_categorical_distinctness_floor() -> None:
    names = list(_STATUS_COLORS)
    for i, name_a in enumerate(names):
        for name_b in names[i + 1 :]:
            distance = delta_e76(_STATUS_COLORS[name_a], _STATUS_COLORS[name_b])
            assert distance >= _CATEGORICAL_DELTA_FLOOR, (name_a, name_b, distance)


def test_rtl_render_declares_dir_and_lang_and_shows_arabic_labels(
    tmp_path: Path,
) -> None:
    (tmp_path / "mappings/orders").mkdir(parents=True)
    (tmp_path / "mappings/orders/source-profile.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "mappings/orders/readiness-status.yaml").write_text(
        "table: orders\n"
        "current_stage: source_ready\n"
        "stages:\n"
        "  source_ready:\n"
        "    status: pass\n"
        "    evidence: [mappings/orders/source-profile.md]\n"
        "    blocking_reasons: []\n"
        "blocking_reasons: []\n"
        "approvals: []\n"
        "next_action: Continue mapping.\n",
        encoding="utf-8",
    )
    bundle = build_showcase_bundle(tmp_path)
    html = render_showcase_html(bundle, repo=tmp_path, rtl=True)
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    assert "بيان الإفصاح" in html  # "Disclosure manifest"
    assert "تتبع المقاييس" in html  # "Metric lineage"

    ltr_html = render_showcase_html(bundle, repo=tmp_path, rtl=False)
    assert 'dir="ltr"' in ltr_html
    assert 'lang="en"' in ltr_html


def test_css_contains_no_body_horizontal_scroll_and_own_scroll_containers() -> None:
    css = (
        Path(__file__).resolve().parents[2] / "src/seshat/showcase/assets/showcase.css"
    ).read_text(encoding="utf-8")
    assert "overflow-x: hidden" in css  # body: no horizontal body scroll
    assert ".stage-matrix" in css and "overflow-x: auto" in css
    assert "@media (max-width: 720px)" in css


def test_explorer_assets_are_byte_unchanged_after_an_rtl_render(tmp_path: Path) -> None:
    before = {path.name: path.read_bytes() for path in _EXPLORER_ASSETS.glob("*")}
    bundle = build_showcase_bundle(_REPO)
    render_showcase_html(bundle, repo=_REPO, rtl=True)
    after = {path.name: path.read_bytes() for path in _EXPLORER_ASSETS.glob("*")}
    assert after == before


@pytest.mark.parametrize("viewport", [(1280, 800), (390, 844)])
def test_narrow_viewport_reflows_without_horizontal_body_scroll(
    tmp_path: Path, viewport: tuple[int, int]
) -> None:
    sync_api = pytest.importorskip("playwright.sync_api")
    (tmp_path / "mappings/orders").mkdir(parents=True)
    (tmp_path / "mappings/orders/source-profile.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "mappings/orders/readiness-status.yaml").write_text(
        "table: orders\n"
        "current_stage: source_ready\n"
        "stages:\n"
        "  source_ready:\n"
        "    status: pass\n"
        "    evidence: [mappings/orders/source-profile.md]\n"
        "    blocking_reasons: []\n"
        "blocking_reasons: []\n"
        "approvals: []\n"
        "next_action: Continue mapping.\n",
        encoding="utf-8",
    )
    bundle = build_showcase_bundle(tmp_path)
    output = tmp_path / "index.html"
    output.write_text(render_showcase_html(bundle, repo=tmp_path), encoding="utf-8")

    with sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
        page.goto(output.as_uri())
        assert page.locator(".table-tab").count() == 1
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"
        )
        browser.close()
