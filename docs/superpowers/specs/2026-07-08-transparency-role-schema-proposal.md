# Transparency-role schema proposal (Idea 2 / T18 OWNER STOP)

> **STATUS: PROPOSAL awaiting owner ratification.** No code is wired against this
> yet. `check_composite_contrast_or_raise` and `composite_over` are already built,
> unit-tested, and importable (T18), but **unwired** because `ThemeSeed` /
> `build_palette` carry zero transparency fields today. This document proposes the
> concrete schema so wiring stops being a self-invented decision (rule #9 /
> Principle V) and becomes an owner-ratified one. Approve the five choices below
> (or amend them) and the wiring follow-up can proceed.

## Why this stop exists

The composite-transparency check proves a narrow, computable fact: *a
semi-transparent foreground, once alpha-composited over the theme background,
still clears the 4.5:1 AA contrast floor.* That check is real and passing in
tests. But it has nothing to read: there is no committed description of **what a
"transparency role" is** -- which colour field is allowed to be semi-transparent,
what its default opacity is, whether opacity is per-role or global, and how the
value round-trips through `design/tokens/*.yaml` and `themes/*.theme.json`.
Inventing those answers is exactly the kind of schema decision the owner must make.

## The five choices to ratify

Each choice lists a **recommended default** first, with the trade-off. Ratify one
value per row (or propose your own).

| # | Decision | Recommended | Alternatives / trade-off |
|---|----------|-------------|--------------------------|
| 1 | **Which field(s) may carry transparency** | A single new optional `overlay` role (background-overlay panels / card fills) | Per-data-colour alpha (much larger surface, CVD-sensitive, not needed for AA); text alpha (rejected -- text must stay opaque for legibility) |
| 2 | **Default `transparency_pct`** | `0.0` (fully opaque unless a caller opts in) | A non-zero default silently weakens contrast on every theme; opt-in keeps the gate honest |
| 3 | **Per-role or global** | Per-role dict `{role: {fg, transparency_pct}}` (matches the check's existing signature) | A single global pct can't express "panel 20%, tooltip 0%"; per-role is strictly more expressive and already what the check iterates |
| 4 | **Tokens YAML shape** | A new top-level `transparency:` block, sibling of `colors:` -- `transparency:\n  overlay:\n    fg: "#RRGGBB"\n    transparency_pct: 20.0` | Nesting under `colors:` conflates opaque palette entries with alpha specs; a sibling block keeps `build_palette`'s colour contract unchanged |
| 5 | **theme.json key + blend space** | Write to Power BI `visualStyles` transparency keys; blend in **sRGB (gamma) space** to match how the renderer composites already-encoded colours (this is what `composite_over` already does) | Linear-light blend would mismatch the renderer and make the AA proof unfaithful to what ships |

## What wiring would then look like (for reference only -- not built yet)

Once the five choices are ratified:

1. `ThemeSeed` gains an optional `transparency: dict | None = None` field
   (default `None` -> no behaviour change for every existing caller).
2. `build_palette` copies a validated `transparency` block onto the palette dict
   under a `"transparency"` key (the exact key `check_composite_contrast_or_raise`
   already reads).
3. `_validate_and_collect` calls `check_composite_contrast_or_raise(palette)` in
   the same choke point as the other gates -- so a transparency role that fails AA
   once composited refuses the write, exactly like a failing text contrast does.
4. `render_tokens_yaml` emits the ratified `transparency:` block; `render_theme_json`
   emits the matching `visualStyles` transparency keys; `seed_from_tokens`
   round-trips it back.
5. The theme-spec's accessibility section gains a **computed `[x]` line** for
   composite contrast -- never a `[x]` until wiring is approved and passing.

## Explicit non-goals (stay open regardless)

- Transparency does **not** become a `pass`-granting fact on its own; the human
  seams (CVD, on-screen legibility, saturation) remain `[ ]` OPEN.
- No render / PBIR write / live Power BI is introduced -- this stays DEFINE-only.
- Until the owner ratifies choices 1-5, `check_composite_contrast_or_raise`
  remains standalone and unwired, and no theme-spec line claims composite contrast
  as satisfied.
