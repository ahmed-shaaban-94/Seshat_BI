"""Unit tests for the tokens->theme compiler (retail.theme_compile)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from retail.theme_compile import (
    ThemeCompileError,
    compile_theme,
    palette_from_tokens,
    seed_from_tokens,
)

pytestmark = pytest.mark.unit

# A committed-tokens doc in the exact shape render_tokens_yaml writes.
TOKENS = {
    "meta": {
        "name": "executive-dark-design-tokens",
        "style": "generated (dark)",
        "version": "1",
        "compiles_to": "themes/executive-dark.theme.json",
    },
    "colors": {
        "primary": "#2FB6C4",
        "secondary": "#7BD6DF",
        "background": "#12263A",
        "text": {"primary": "#F2F6FA", "secondary": "#C4D1DE", "muted": "#93A6B8"},
        "sentiment": {"success": "#2E7D5B", "warning": "#B5832A", "danger": "#B23A3A"},
        "data_colors": [
            "#A5E3E9",
            "#7BD6DF",
            "#52C9D6",
            "#2FB7C5",
            "#25919C",
            "#1C6B73",
        ],
    },
}


def test_palette_from_tokens_copies_every_color_field():
    pal = palette_from_tokens(TOKENS)
    c = pal["colors"]
    assert c["primary"] == "#2FB6C4"
    assert c["background"] == "#12263A"
    assert c["text"]["muted"] == "#93A6B8"
    assert c["sentiment"]["success"] == "#2E7D5B"
    assert c["data_colors"] == TOKENS["colors"]["data_colors"]


def test_seed_from_tokens_strips_suffix_for_name():
    seed = seed_from_tokens(TOKENS, name_override=None)
    assert seed.name == "executive-dark"  # -design-tokens stripped
    assert seed.mode == "dark"  # parsed from meta.style "generated (dark)"
    assert seed.accent == "#2FB6C4"


def test_seed_from_tokens_name_override_wins():
    seed = seed_from_tokens(TOKENS, name_override="my-theme")
    assert seed.name == "my-theme"


def test_seed_from_tokens_rejects_bad_slug():
    with pytest.raises(ThemeCompileError):
        seed_from_tokens(TOKENS, name_override="../escape")


def _write_tokens(tmp: Path, doc: dict) -> Path:
    p = tmp / "design" / "tokens" / "executive-dark-design-tokens.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return p


def test_compile_is_byte_identical_to_theme_gen(tmp_path: Path):
    # 1. theme-gen produces the reference theme.json for a seed.
    from retail.theme_gen import ThemeSeed, generate

    seed = ThemeSeed(
        name="executive-dark",
        mode="dark",
        accent="#2FB6C4",
        background="#12263A",
        text_primary="#F2F6FA",
        text_secondary="#C4D1DE",
        text_muted="#93A6B8",
        data_colors=("#A5E3E9", "#7BD6DF", "#52C9D6", "#2FB7C5", "#25919C", "#1C6B73"),
        good="#2E7D5B",
        neutral="#B5832A",
        bad="#B23A3A",
    )
    generate(seed, tmp_path, force=True)
    ref_theme = (tmp_path / "themes/executive-dark.theme.json").read_bytes()
    ref_tokens_doc = yaml.safe_load(
        (tmp_path / "design/tokens/executive-dark-design-tokens.yaml").read_text(
            encoding="utf-8-sig"
        )
    )

    # 2. delete the theme, keep the tokens theme-gen wrote.
    (tmp_path / "themes/executive-dark.theme.json").unlink()

    # 3. compile from those exact committed tokens.
    tokens_path = tmp_path / "design/tokens/executive-dark-design-tokens.yaml"
    out = compile_theme(tokens_path, out_path=None, force=False)

    # 4. byte-identical to theme-gen's output.
    assert out == tmp_path / "themes/executive-dark.theme.json"
    assert out.read_bytes() == ref_theme
    assert ref_tokens_doc  # sanity: tokens were real


def test_compile_refuses_overwrite_without_force(tmp_path: Path):
    tokens = _write_tokens(tmp_path, TOKENS)
    compile_theme(tokens, out_path=None, force=False)  # first write ok
    with pytest.raises(ThemeCompileError, match="refusing to overwrite"):
        compile_theme(tokens, out_path=None, force=False)


def test_compile_force_overwrites(tmp_path: Path):
    tokens = _write_tokens(tmp_path, TOKENS)
    compile_theme(tokens, out_path=None, force=False)
    out = compile_theme(tokens, out_path=None, force=True)  # no raise
    assert out.exists()


def test_missing_colors_field_is_clean_error(tmp_path: Path):
    doc = {"meta": TOKENS["meta"], "colors": {**TOKENS["colors"]}}
    del doc["colors"]["background"]
    tokens = _write_tokens(tmp_path, doc)
    with pytest.raises(ThemeCompileError, match="colors.background"):
        compile_theme(tokens, out_path=None, force=False)


def test_bad_hex_is_clean_error(tmp_path: Path):
    doc = {
        "meta": TOKENS["meta"],
        "colors": {**TOKENS["colors"], "primary": "not-a-hex"},
    }
    tokens = _write_tokens(tmp_path, doc)
    with pytest.raises(ThemeCompileError, match="#RRGGBB"):
        compile_theme(tokens, out_path=None, force=False)


def test_sub_aa_contrast_is_refused(tmp_path: Path):
    # muted text nearly equal to background -> below AA -> refuse.
    doc = {
        "meta": TOKENS["meta"],
        "colors": {
            **TOKENS["colors"],
            "text": {"primary": "#F2F6FA", "secondary": "#C4D1DE", "muted": "#13273B"},
        },
    }
    tokens = _write_tokens(tmp_path, doc)
    with pytest.raises(Exception):  # ThemeGenError from check_contrast_or_raise
        compile_theme(tokens, out_path=None, force=False)


def test_no_compiles_to_and_no_out_is_clean_error(tmp_path: Path):
    doc = {"meta": {"name": "x-design-tokens"}, "colors": TOKENS["colors"]}
    tokens = _write_tokens(tmp_path, doc)
    with pytest.raises(ThemeCompileError, match="compiles_to"):
        compile_theme(tokens, out_path=None, force=False)
