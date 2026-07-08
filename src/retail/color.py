"""Shared, stdlib-only sRGB/WCAG color math.

The single source of truth for the WCAG 2.x relative-luminance contrast ratio.
Both the CT1 governance rule (retail.rules.design_contrast) and the theme
generator (retail.theme_gen) import from here, so the generator's pre-write
self-check uses the exact arithmetic the gate later applies. No dependency
beyond the stdlib.
"""

from __future__ import annotations

import re

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def is_valid_hex(s: str) -> bool:
    """True iff ``s`` is a ``#RRGGBB`` hex color."""
    return isinstance(s, str) and _HEX_RE.match(s) is not None


def channel_luminance(c: int) -> float:
    """Linearize one 0-255 sRGB channel to its WCAG luminance component."""
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """WCAG 2.x relative luminance of an ``#RRGGBB`` color."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"not a 6-digit hex color: {hex_color!r}")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return (
        0.2126 * channel_luminance(r)
        + 0.7152 * channel_luminance(g)
        + 0.0722 * channel_luminance(b)
    )


def contrast_ratio(a: str, b: str) -> float:
    """WCAG contrast ratio (>= 1.0) between two ``#RRGGBB`` colors."""
    la = relative_luminance(a)
    lb = relative_luminance(b)
    lighter, darker = (la, lb) if la >= lb else (lb, la)
    return (lighter + 0.05) / (darker + 0.05)


def _lab_f(t: float) -> float:
    """CIE Lab nonlinearity: cube root above the linear-segment threshold."""
    epsilon = (6.0 / 29.0) ** 3
    kappa = (1.0 / 3.0) * (29.0 / 6.0) ** 2
    return t ** (1.0 / 3.0) if t > epsilon else kappa * t + 4.0 / 29.0


def hex_to_lab(hex_color: str) -> tuple[float, float, float]:
    """CIE L*a*b* (D65 white point) of an ``#RRGGBB`` color.

    Reuses ``channel_luminance`` for the sRGB->linear step, then applies the
    standard linRGB->XYZ (D65) matrix before the Lab nonlinearity. The XYZ Y
    row (0.2126, 0.7152, 0.0722) matches ``relative_luminance``'s WCAG
    coefficients -- same underlying linear-light Y, different downstream use.
    """
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"not a 6-digit hex color: {hex_color!r}")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    rl, gl, bl = channel_luminance(r), channel_luminance(g), channel_luminance(b)

    x = 0.4124564 * rl + 0.3575761 * gl + 0.1804375 * bl
    y = 0.2126729 * rl + 0.7151522 * gl + 0.0721750 * bl
    z = 0.0193339 * rl + 0.1191920 * gl + 0.9503041 * bl

    x_n, y_n, z_n = 0.95047, 1.0, 1.08883
    fx, fy, fz = _lab_f(x / x_n), _lab_f(y / y_n), _lab_f(z / z_n)

    lightness = 116.0 * fy - 16.0
    a_axis = 500.0 * (fx - fy)
    b_axis = 200.0 * (fy - fz)
    return (lightness, a_axis, b_axis)


def delta_e76(a: str, b: str) -> float:
    """CIE76 color difference: Euclidean distance between two Lab colors."""
    l1, a1, b1 = hex_to_lab(a)
    l2, a2, b2 = hex_to_lab(b)
    return ((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5
