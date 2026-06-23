"""DAX/TMDL rules (D1-D5). D6-D8 and C1 will be added in M4b.

Rules registered here:
  D1 - Measure names must be PascalCase (^[A-Z][A-Za-z0-9]*$)
  D2 - Each measure must have a displayFolder
  D3 - No duplicated measure logic (exact normalized-body collision)
  D4 - Use DIVIDE() not the bare / operator
  D5 - WARNING: numeric column summarizeBy != none
"""

from __future__ import annotations

import re
from typing import Iterable

from ..core import Finding, RuleContext, Severity
from ..registry import register
from ..tmdl import iter_model_files, normalize_measure_body, parse_tmdl

# ---------------------------------------------------------------------------
# D1 — PascalCase measure names
# ---------------------------------------------------------------------------

_PASCAL = re.compile(r"^[A-Z][A-Za-z0-9]*$")


@register("D1", "Measure names must be PascalCase")
def d1_pascalcase_measures(ctx: RuleContext) -> Iterable[Finding]:
    """Flag any measure whose name does not match ``^[A-Z][A-Za-z0-9]*$``."""
    for rel, text in iter_model_files(ctx, ".tmdl"):
        table = parse_tmdl(text)
        if table is None:
            continue
        for m in table.measures:
            if not _PASCAL.match(m.name):
                yield Finding(
                    rule_id="D1",
                    severity=Severity.ERROR,
                    message=(
                        f"Measure '{m.name}' is not PascalCase" " (^[A-Z][A-Za-z0-9]*$)"
                    ),
                    locator=f"{rel}:{m.line}",
                )


# ---------------------------------------------------------------------------
# D2 — displayFolder required on every measure
# ---------------------------------------------------------------------------


@register("D2", "Each measure must have a displayFolder")
def d2_display_folder(ctx: RuleContext) -> Iterable[Finding]:
    """Flag any measure that is missing a ``displayFolder`` property."""
    for rel, text in iter_model_files(ctx, ".tmdl"):
        table = parse_tmdl(text)
        if table is None:
            continue
        for m in table.measures:
            if not m.display_folder:
                yield Finding(
                    rule_id="D2",
                    severity=Severity.ERROR,
                    message=f"Measure '{m.name}' has no displayFolder",
                    locator=f"{rel}:{m.line}",
                )


# ---------------------------------------------------------------------------
# D3 — no duplicated measure logic
# ---------------------------------------------------------------------------


@register("D3", "No duplicated measure logic")
def d3_no_duplicate_logic(ctx: RuleContext) -> Iterable[Finding]:
    """Flag any measure whose normalized body is identical to a previously seen one.

    Normalization (via ``normalize_measure_body``): strip ``//`` and ``/* */``
    comments, collapse whitespace, lowercase.  Two measures sharing the same
    normalized body are reported as duplicates; the *second* occurrence is the
    locator.
    """
    seen: dict[str, tuple[str, str, int]] = {}  # norm -> (rel, name, line)
    for rel, text in iter_model_files(ctx, ".tmdl"):
        table = parse_tmdl(text)
        if table is None:
            continue
        for m in table.measures:
            norm = normalize_measure_body(m.expression)
            if not norm:
                continue
            if norm in seen:
                prev_rel, prev_name, prev_line = seen[norm]
                yield Finding(
                    rule_id="D3",
                    severity=Severity.ERROR,
                    message=(
                        f"Measure '{m.name}' duplicates logic of "
                        f"'{prev_name}' (identical normalized body)"
                    ),
                    locator=f"{rel}:{m.line}",
                )
            else:
                seen[norm] = (rel, m.name, m.line)


# ---------------------------------------------------------------------------
# D4 — use DIVIDE() not the / operator
# ---------------------------------------------------------------------------


def _strip_dax_comments_and_strings(expr: str) -> str:
    """Strip ``/* */`` block comments, ``//`` line comments, and string literals.

    Returns the cleaned expression text, safe to scan for a bare ``/`` that
    would signal a division operator rather than a comment delimiter.
    """
    no_block = re.sub(r"/\*.*?\*/", " ", expr, flags=re.DOTALL)
    no_line = re.sub(r"//[^\n]*", " ", no_block)
    # Strip double-quoted DAX string literals (escaped quote is "")
    return re.sub(r'"(?:[^"]|"")*"', " ", no_line)


@register("D4", "Use DIVIDE() not the / operator")
def d4_divide_not_slash(ctx: RuleContext) -> Iterable[Finding]:
    """Flag any measure expression containing a bare ``/`` after stripping comments."""
    for rel, text in iter_model_files(ctx, ".tmdl"):
        table = parse_tmdl(text)
        if table is None:
            continue
        for m in table.measures:
            cleaned = _strip_dax_comments_and_strings(m.expression)
            if "/" in cleaned:
                yield Finding(
                    rule_id="D4",
                    severity=Severity.ERROR,
                    message=f"Measure '{m.name}' uses '/'; use DIVIDE() instead",
                    locator=f"{rel}:{m.line}",
                )


# ---------------------------------------------------------------------------
# D5 — WARNING: numeric column summarizeBy != none
# ---------------------------------------------------------------------------

_NUMERIC_TYPES = frozenset({"int64", "decimal", "double", "int", "currency"})


@register("D5", "Prefer explicit measures over implicit aggregation")
def d5_explicit_aggregation(ctx: RuleContext) -> Iterable[Finding]:
    """Warn when a numeric column has ``summarizeBy`` set to anything other than
    ``none``.

    Severity is WARNING (does not fail the build). The ``summarizeBy`` property
    is only flagged when explicitly present and != ``none``; absent property is
    treated as acceptable (conservative: missing != implicit sum).
    """
    for rel, text in iter_model_files(ctx, ".tmdl"):
        table = parse_tmdl(text)
        if table is None:
            continue
        for c in table.columns:
            dt = (c.data_type or "").lower()
            sb = (c.summarize_by or "none").lower()
            if dt in _NUMERIC_TYPES and sb != "none":
                yield Finding(
                    rule_id="D5",
                    severity=Severity.WARNING,
                    message=(
                        f"Numeric column '{c.name}' has"
                        f" summarizeBy='{c.summarize_by}';"
                        " prefer explicit measures (summarizeBy: none)"
                    ),
                    locator=f"{rel}:{c.line}",
                )
