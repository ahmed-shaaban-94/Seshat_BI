# Feature Specification: F038 -- Tabular Editor BPA Adapter Spike (optional, proven-headless DAX best-practice engine)

## Naming note (numbering vs roadmap)

The roadmap's shipped feature IDs run F005-F016; the spec directories run 003-017.
"F038" is the owner-assigned label for this work item (the Tabular Editor BPA adapter
spike). It is filed at `specs/038-tabular-editor-bpa-adapter/` to keep that label
stable; it does NOT imply 21 intervening unbuilt features. This is a SPIKE spec: the
spike (a smoke test that proves -- or disproves -- headless reproducibility) IS the
deliverable. A full adapter is built only if the spike passes AND the owner approves.

## Why this feature exists

Retail Tower is building a LAYERED DAX governance system. Most layers are home-grown,
in-repo, stdlib, CI-reproducible (the kit's `dependencies = []` core). One layer --
generic DAX/model BEST-PRACTICE checking (the industry "hard rules of DAX": no implicit
measures, prefer DIVIDE, no bidirectional relationships, fully-qualified columns, etc.)
-- is a solved problem owned by an external tool: Tabular Editor's Best Practice
Analyzer (BPA), with a mature community ruleset (~80 rules). Reimplementing all of BPA
by hand would be large, fragile, and duplicative.

Tabular Editor 2 (`TabularEditor.exe`) was found installed on the dev machine. The
QUESTION this spike answers is NOT "is BPA useful" (it is) but: **can it be driven
fully agent-driven / headless / reproducibly, without a GUI and without a human
clicking anything?** If yes, it earns a place as an OPTIONAL external engine. If no, it
is rejected/deferred and the home-grown Tower BI DAX governance carries the load.

## The authority boundary (the load this feature respects)

**Tower BI remains the sole AUTHORITY for business truth.** Tabular Editor/BPA, if
adopted, is ONLY a generic DAX/model best-practice engine. It NEVER decides any of:

| Tower BI owns (authority) | Tabular Editor/BPA may advise (generic) |
|---------------------------|------------------------------------------|
| metric contracts (the approved definition) | DAX style/form best-practice (DIVIDE, qualified cols) |
| denominator logic (e.g. known-status vs all) | implicit-measure / auto-aggregation warnings |
| blank / unknown handling (the Q2-class rulings) | relationship hygiene (bidirectional flags) |
| source-map owner decisions | naming / display-folder conventions |
| approval gates, publish readiness | generic performance anti-patterns |

A BPA finding is ADVISORY input to a human/agent; it can never override a Tower BI
contract, flip an approval, or assert a business-semantic verdict. The 50.37%-vs-33.55%
class of bug (a wrong denominator that is still valid, best-practice-clean DAX) is
OUT of BPA's reach BY DESIGN -- that is the contract-drift layer (L3), Tower-owned.

## The layered DAX governance system (context -- this spec builds ONE optional layer)

| Layer | Catches | Engine | Owner | This spec? |
|-------|---------|--------|-------|------------|
| L1 syntax/parse | invalid DAX (arity, parens, unknown funcs) | DAX parser | TBD | candidate (if TE proven) |
| L2 best-practice | the "hard rules of DAX" (~80 BPA rules) | **Tabular Editor BPA** OR home-grown | external/optional | **YES (spike)** |
| L3 contract drift | wrong denominator/filter vs approved contract (50.37 class) | skill + lazy metric_drift module | **Tower BI** | no (separate) |
| L4 value | wrong number | SQL/DuckDB proxy vs contract expected | **Tower BI** | no (separate) |

This spec covers ONLY the L2 adapter SPIKE. L3/L4 and any L1 decision are separate work.

## Hard requirements the adapter MUST satisfy (the proof gates)

The spike PASSES only if ALL of these are demonstrated; any failure => REJECTED/DEFERRED:

1. **Headless.** Runs with NO GUI, NO window, NO interactive prompt. A bare
   `TabularEditor.exe` (no CLI args) opens the GUI and hangs -- that invocation is
   FORBIDDEN; the adapter only ever calls the documented headless CLI form.
2. **No live Power BI Desktop session.** Opens/parses the committed model
   (PBIP/TMDL, or a derived `.bim`/`model.bim`) from disk -- no running Desktop, no
   workspace, no network.
3. **Repo-controlled rules.** BPA runs a rules file committed IN the repo (e.g.
   `tools/bpa-rules/retail-bpa.json`), not a machine-global or cloud ruleset.
4. **Machine-readable / stable exit.** Returns machine-readable output (or at minimum
   a documented, stable exit code) the agent/CI can branch on.
5. **CI / scripted runnable.** Invocable from a single scripted command (no clicks).
6. **Fails safe.** If the binary is absent or `TABULAR_EDITOR_PATH` is unset, the
   adapter REFUSES TO RUN with a clear message and a non-crashing skip -- never a
   traceback, never a silent pass, never a GUI launch.

## Scope boundary (read first)

- **The spike AUTHORS a small runner + a smoke test + an evidence file. In scope.**
- **NOT a blocking core dependency.** The adapter is OPTIONAL and skip-safe; the kit's
  `dependencies = []` stdlib core and `retail check` are UNCHANGED and remain
  mandatory + portable. CI without Tabular Editor still passes (the adapter skips).
- **No GUI, ever. No human clicks, ever. No bare-exe launch, ever.**
- **Never promoted to core until the spike passes AND the owner explicitly approves.**

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prove (or disprove) headless reproducibility (Priority: P1)

As the kit maintainer, I want a one-command smoke test that proves Tabular Editor can
analyze our model headlessly, so I can decide whether to adopt BPA as an optional L2
engine without ever opening a GUI.

**Acceptance:**
- A runner locates `TabularEditor.exe` via `TABULAR_EDITOR_PATH` (env) or a configured
  path; if absent -> prints the enable steps and exits 0 with status "skipped (not
  configured)" -- NO crash, NO GUI.
- When configured, the runner invokes ONLY the headless CLI form (script/analyze mode
  with explicit args) against the committed model, with a bounded timeout.
- It writes an evidence file (`specs/038-.../evidence/smoke-<date>.md` or a
  tool-output path) recording: the exact command, the exit code, whether a GUI window
  was spawned (must be NO), stdout/stderr head, and the PASS/REJECT verdict against the
  six proof gates.
- If headless analysis is NOT achievable (GUI opens, requires Desktop, requires auth,
  no machine-readable result), the runner records REJECTED with the specific failed
  gate, and the spec is marked deferred -- the home-grown path continues.

### User Story 2 - The adapter never blocks the portable core (Priority: P1)

As a CI operator on a machine WITHOUT Tabular Editor, I want `retail check` and the
full test suite to pass unchanged, so the optional adapter never makes the core
non-portable.

**Acceptance:**
- `retail check` rule count, import path, and `dependencies = []` are UNCHANGED by this
  spike (the adapter lives outside `src/retail/`'s core import chain -- e.g. under
  `tools/` or a clearly optional module).
- A test asserts the adapter SKIPS cleanly (exit 0, "skipped") when the binary path is
  unset, with no import of any .NET/Tabular dependency at collection time.

### User Story 3 - The authority boundary is enforced in the output (Priority: P2)

As the data owner, I want any BPA output to be clearly ADVISORY and scoped to generic
DAX best-practice, so it can never read as a Tower BI business-truth verdict.

**Acceptance:**
- The evidence file and any adapter output label BPA findings as "advisory / generic
  DAX best-practice (NOT a Tower BI contract/approval verdict)".
- The repo-controlled BPA ruleset contains ONLY generic rules; it carries NO metric
  definition, denominator logic, or approval semantics (those stay in contracts).

### Edge Cases

- **Binary present but wrong version / no CLI support** -> REJECT with the gate it
  failed (machine-readable / headless), do not fall back to GUI.
- **Model is TMDL-only and the installed TE wants `.bim`** -> the smoke test records
  this as a gate-2 limitation (parses model from disk?) and either derives a `.bim`
  headlessly or marks the format unsupported -> REJECTED for now.
- **CLI hangs (GUI/prompt)** -> the bounded timeout kills it; recorded as a gate-1
  failure (not headless). (This already happened once with a bare launch -- the runner
  must NEVER invoke the bare form.)
- **Auth prompt in headless/cron** -> gate failure (not reproducible) -> REJECTED.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** The runner MUST resolve the binary via `TABULAR_EDITOR_PATH` (env) first,
  then a documented default path; on neither, it MUST exit 0 with a "skipped (not
  configured)" message and the enable steps. It MUST NOT crash and MUST NOT launch a GUI.
- **FR-002** The runner MUST invoke Tabular Editor ONLY via its documented headless CLI
  (script/analyze flags + explicit model + explicit rules file). A bare
  `TabularEditor.exe` invocation is forbidden in code.
- **FR-003** The runner MUST pass a bounded timeout; on timeout it records a gate-1
  (headless) FAILURE and terminates the process.
- **FR-004** The runner MUST parse the model from committed files on disk with NO live
  Power BI Desktop session and NO network.
- **FR-005** BPA MUST run a repo-committed rules file; the runner MUST NOT use a
  machine-global or remote ruleset.
- **FR-006** The runner MUST emit machine-readable output or a documented stable exit
  code, and MUST write an evidence file recording command, exit code, GUI-spawned?
  (must be NO), output head, and the PASS/REJECT verdict per the six gates.
- **FR-007** The adapter MUST live OUTSIDE `src/retail/`'s core import chain and MUST
  NOT add to `dependencies = []`; `retail check` and the unit suite MUST be unchanged.
- **FR-008** The adapter MUST be skip-safe in CI: absent binary => clean skip, no
  failure, no import of external deps at collection.
- **FR-009** All adapter output MUST label BPA findings as advisory/generic, explicitly
  NOT a Tower BI contract/approval/business-truth verdict.
- **FR-010** The adapter MUST NOT be referenced by any mandatory readiness gate or
  `retail check` rule until the spike passes AND the owner records approval.

### Key Entities

- **BPA runner** -- the small scripted entrypoint (locate -> guard -> headless invoke ->
  evidence). Lives under `tools/` (optional), not `src/retail/` (core).
- **Repo BPA ruleset** -- `tools/bpa-rules/retail-bpa.json` (generic DAX rules only).
- **Evidence file** -- the dated smoke-test record + the six-gate verdict.
- **The six proof gates** -- headless / no-Desktop / repo-rules / machine-readable /
  CI-runnable / fail-safe (the PASS criteria).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** A single scripted command produces an evidence file with a PASS or REJECT
  verdict against all six gates -- with zero GUI windows and zero human clicks.
- **SC-002** On a machine without the binary (or with `TABULAR_EDITOR_PATH` unset), the
  runner exits 0 "skipped" and `retail check` + the unit suite pass unchanged.
- **SC-003** If PASS: a repo-committed BPA ruleset runs headlessly against the model and
  returns machine-readable findings, all labeled advisory/generic.
- **SC-004** If REJECT: the spec is marked rejected/deferred with the specific failed
  gate, and the home-grown Tower BI DAX governance is confirmed as the carrying path.
- **SC-005** `dependencies = []`, the `retail check` rule count, and the core import
  path are provably unchanged by this spike.

## Assumptions

- Tabular Editor 2 exposes a headless CLI (`-S`/script, `-A`/analyze BPA, batch). The
  spike PROVES this on our model rather than assuming it.
- The model may be TMDL-only; whether TE parses TMDL directly or needs a derived `.bim`
  is one of the things the smoke test establishes (gate 2).
- The dev machine has the binary; CI does not -- so skip-safe behavior is the norm, not
  the exception.

## Deferred decisions (future specs / issues -- recorded, not built)

- **L1 syntax validation** (own DAX tokenizer vs TE) -- decided separately, after this
  spike informs whether TE is reproducible enough to lean on.
- **Promotion to a gate** -- whether a passing BPA becomes part of semantic-model
  readiness is a future decision, gated on owner approval (FR-010).
- **A home-grown BPA subset** -- if TE is rejected, which generic rules we implement as
  `retail check` D-rules ourselves.

## See also

- The authority it must not cross: `mappings/<table>/metrics/*.yaml` (contracts),
  `docs/readiness/semantic-model-ready.md`.
- The contract-drift layer (L3, Tower-owned, separate): the `retail-semantic-check`
  skill + a future lazy `metric_drift` module.
- The stdlib-only invariant it must not break: `pyproject.toml` (`dependencies = []`),
  `tests/unit/test_validate_targets.py::test_validate_module_stays_stdlib_only`.
- The execution-adapter precedent (optional, gated, not core): F016 in
  `docs/roadmap/roadmap.md`.
