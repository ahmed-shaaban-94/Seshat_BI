# PBIR-authoring adapter -- session handoff / what to do next

> A durable, in-repo resume note so this can be continued from any device or a later
> session. Written 2026-07-05. If anything here disagrees with the code, the code +
> `git log` win -- re-verify before acting.

## Where things stand (all on `main`)

The goal: a self-contained tool that generates themes/backgrounds and formats a
Power BI report's visuals -- writing the PBIR/PBIP JSON directly, no external tool
(no pbi-cli, no live Power BI). Authorized by ADR
`docs/decisions/0015-pbir-authoring-adapter-lifts-fr008-fr009.md`.

| Piece | Status | Verb / where |
|-------|--------|--------------|
| Slice 1 -- theme generator | **SHIPPED** (PR #204) | `retail theme-gen` -> `src/retail/theme_gen.py` |
| Adapter A -- apply theme to a report | **SHIPPED** (PR #206) | `retail pbir-apply-theme` -> `src/retail/pbir_theme_apply.py` |
| Adapter B -- format cards/charts | **SHIPPED** (PR #207) | `retail pbir-format-visual` -> `src/retail/pbir_visual_format.py` |
| Adapter C -- page background image | **SHIPPED** (2026-07-06, from a real owner sample) | `retail pbir-set-page-background` -> `src/retail/pbir_page_background.py` |
| Core lint R2 (polices written report.json) | SHIPPED | `src/retail/rules/pbir.py` |

Everything above is green on `main` (`retail check` exit 0; full `pytest -m unit`
passing). The three verbs chain: generate a theme -> apply it to a report -> format
individual visuals.

## Increment C (page background image) -- RESOLVED / SHIPPED 2026-07-06

Was held (blocked-on-real-wire-format). The owner provided a real Desktop-authored
sample (a page background on the c086 sales report), which revealed the wire format
that could not be guessed: the image URL is a **`ResourcePackageItem`** wrapper
(`PackageName`/`PackageType: 1`/`ItemName`), not a Literal. C was built from that real
format and shipped as `retail pbir-set-page-background`. The hold was vindicated --
guessing would have produced the wrong structure. (Background *color* was correctly
NOT used as a substitute; that is the surface-3 theme fill.)

### To unblock C (the ~5-minute task -- do this from any device with Power BI Desktop)

Follow **`docs/integrations/pbir-adapter-C-unblocker.md`** exactly. In short:
1. Save a PBIP project (enable the .pbip preview feature if needed).
2. Select a page -> Format your report page -> Canvas background -> Image -> add any
   small image; set fit = Fit, transparency = 0%; save.
3. Commit / hand back these 3 files from the saved `*.Report/`:
   - `definition/pages/<pageId>/page.json` (the real `objects.background` image block)
   - `definition/report.json` (the RegisteredResources entry Desktop wrote)
   - `StaticResources/RegisteredResources/<the image file>` (the asset)

Put them anywhere in the repo (e.g. a `samples/pbir-page-bg/` folder) and note the
path here, or just say "the sample is committed" -- the agent will locate it.

### What the agent does once the sample exists

Builds C exactly like A/B: a `tests/fixtures/pbir/` fixture copied from the real
sample, a `pbir-set-page-background` writer (references a committed surface-2 asset by
its RegisteredResources name; sets `page.json` `objects.background` image + scaling +
transparency; allow-list-only, deterministic, all-or-nothing, no external dep,
surface-2 purity enforced), tests, review, PR. No schema-guessing.

## Other open threads (not blocking, lower priority)

- **Smart-formatting layer (the actual "great dashboards automatically" dream):** a
  design-intelligence step where Opus picks good formatting from the generated theme
  and drives A/B/C. This is a NEW feature -- needs its own brainstorm -> spec -> plan,
  not a quick build. Not started.
- **End-to-end hardening:** an integration test that chains theme-gen -> apply ->
  format on one fixture report (proves the three verbs compose). Small; agent can do
  it autonomously anytime.
- **same-store-sales-growth / A11** (older, unrelated thread): still `[planned]`,
  deferred by the H9 D1=C ruling; needs an owner A11 decision to seed.

## How to resume (say any of these to the agent)

- "The C sample is committed at <path>" (or "...is committed") -> agent builds C.
- "Start the smart-formatting design" -> agent brainstorms the design-intelligence layer.
- "Do the end-to-end hardening" -> agent adds the chained integration test.

## Pointers

- Adapter overview + increments: `docs/integrations/pbir-adapter.md`
- C unblocker recipe: `docs/integrations/pbir-adapter-C-unblocker.md`
- Authorization ADR: `docs/decisions/0015-pbir-authoring-adapter-lifts-fr008-fr009.md`
- Spec: `specs/106-pbir-authoring-adapter/spec.md`
