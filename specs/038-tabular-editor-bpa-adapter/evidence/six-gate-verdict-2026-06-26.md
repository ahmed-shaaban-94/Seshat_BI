# F038 Tabular Editor BPA Spike — Six-Gate Verdict (2026-06-26)

- **Tool:** Tabular Editor 2.25.0 (build 2.25.8952.22276), found at
  `C:\Program Files (x86)\Tabular Editor\TabularEditor.exe`.
- **Model under test:** the committed TMDL `powerbi/Retailgold.SemanticModel/definition/`
  folder. `RetailStoreSales.SemanticModel/definition/` was also run and loads cleanly
  (`Loading model... No objects in violation`).
- **Ruleset:** repo-committed `tools/bpa-rules/retail-bpa.json` (1 generic DAX rule —
  prefer `DIVIDE()`; see the rule-authoring caveat below).
- **Runner:** `tools/bpa_runner.py` (stdlib-only, OUTSIDE `src/retail/` core).

## VERDICT: **PASS** — Tabular Editor 2 drives BPA fully headless against our committed TMDL.

All six proof gates demonstrated; zero GUI windows, zero human clicks.

| # | Gate | Verdict | Evidence |
|---|------|---------|----------|
| 1 | **Headless** (no GUI/window/prompt) | ✅ PASS | The documented CLI form `<model> -A <rules> -V` returns immediately; no window. A bounded `timeout` wraps every invocation — a GUI/hang would surface as a gate-1 failure, never a stuck run. The bare-exe form (which opens the GUI) is forbidden in the runner. |
| 2 | **No live Desktop** (TMDL from disk) | ✅ PASS | TE 2.25 loads the committed `definition/` folder directly from disk — **no `.bim` conversion, no Power BI Desktop, no network**. All three input forms worked (`definition/` folder, `definition/database.tmdl`, `definition/model.tmdl`); the folder form is canonical. This was the make-or-break question — answered YES. |
| 3 | **Repo-controlled rules** | ✅ PASS | `-A tools/bpa-rules/retail-bpa.json` runs the committed ruleset (machine/cloud rulesets not used). |
| 4 | **Machine-readable / stable** | ✅ PASS *(with a caveat)* | `-V` emits parseable `##vso[task.logissue type=warning;]Measure [X] violates rule "Y"` lines. **CAVEAT:** TE exits **0 even WITH violations** — so the verdict MUST be derived by *parsing* the log lines (`bpa_runner._parse_violations`), NOT from the exit code. A genuine tool error emits `##vso[task.complete result=Failed;]` + `Error on rule`/`File not found`, which the runner distinguishes. |
| 5 | **CI / scripted** | ✅ PASS | One command: `python tools/bpa_runner.py`. Bounded timeout, no clicks. |
| 6 | **Fails safe** | ✅ PASS | With `TABULAR_EDITOR_PATH` unset and no default binary, the runner exits **0 "skipped (not configured)"** with enable steps — no crash, no GUI, no `subprocess` launch. Proven by `tests/unit/test_bpa_runner.py` (monkeypatched, so it holds on CI without TE). |

## Non-vacuous rule proof

The committed `DIVIDE` rule returns **0 violations on the real model** — the correct
result (every ratio measure already uses `DIVIDE`, none uses a bare `/`). To prove it is
not vacuous, a throwaway copy with an injected `measure BadRatio = [TotalDiscount] /
[TotalSales]` fired it:
```
Measure [BadRatio] violates rule "Use DIVIDE() instead of the '/' operator"
```
The real repo tree was untouched (analyze is read-only; `git status` clean after every run).

## Rule-authoring caveat (a real adoption finding)

A second candidate rule — "measures should have a description"
(`string.IsNullOrWhitespace(Description)`) — was **dropped from the committed ruleset**
because its behavior could not be explained: the Retailgold measures have **no
`description:` line** (verified: `git grep -c "description:"` → 0), yet the predicate
returned **"No objects in violation"** on the real model — while the *same* predicate
*did* fire on the injected description-less `BadRatio`. Same property, opposite results on
two description-less measures. Rather than ship a rule whose semantics on committed TMDL
are unverified, only the `DIVIDE` rule (which fires as expected *and* is understood) is
committed. **Adoption finding:** BPA Dynamic-LINQ predicate semantics over a TMDL-loaded
model are fragile / version-sensitive — any curated community ruleset must be validated
rule-by-rule against our actual model before it is trusted, not assumed from the rule name.

## Authority boundary (enforced in output)

Every runner message and this evidence label BPA findings as **advisory / generic DAX
best-practice ONLY — never a Tower BI contract / approval / business-truth verdict**. The
50.37%-vs-33.55% contract-drift class is structurally OUT of BPA's reach and stays
Tower-owned (L3 `metric_drift`).

## Core invariants UNCHANGED (SC-005)

- `pyproject.toml` `dependencies = []` — unchanged (runner is stdlib-only, under `tools/`).
- `retail check` rule set — unchanged (0 S/D/C findings; only the pre-existing historical
  P2 commit-subject warning remains, unrelated).
- Full unit suite green (392), ruff clean. The adapter imports **no** .NET/Tabular
  dependency at test-collection time.

## Recommendation (owner decision — FR-010)

The spike **PASSES**: BPA is reproducibly headless on our committed TMDL and earns a place
as an **OPTIONAL, skip-safe L2 best-practice engine**. It is NOT promoted to a mandatory
readiness gate or a `retail check` rule by this spike — that requires explicit owner
approval (FR-010). Next steps if adopted: curate the generic community ruleset (drop rules
duplicating the home-grown D1/D2/D4…) **validating each rule against our actual model**
(per the caveat above — rule names cannot be trusted blind), and decide whether a passing
BPA becomes part of semantic-model readiness.
