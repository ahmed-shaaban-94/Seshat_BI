"""Shareable Seshat Proof / Showcase Bundle (spec 127).

A read-only composition + rendering layer over already-shipped surfaces
(the Explorer projection, the Passport, and the disclosure scanner). It
recomputes no readiness, defines no new evidence schema, and adds no new
CLI verb (ratified Option B: the surface is a skill over this library
function -- see ``.claude/skills/showcase-build/SKILL.md``).
"""

from __future__ import annotations

from .build import build_showcase_bundle, render_showcase_html

__all__ = ["build_showcase_bundle", "render_showcase_html"]
