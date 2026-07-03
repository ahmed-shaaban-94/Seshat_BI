# Research: Postgres live-validation suite

**Feature**: `specs/082-postgres-live-validation-suite/spec.md`

This is a research/decision document only. Nothing here adds a dependency to any manifest; it
DESCRIBES what an implementation would need, per the task's explicit boundary.

## Decision 1: Container-orchestration mechanism

**Options considered**:

| Option | Pros | Cons |
|--------|------|------|
| Raw Docker (via the `docker` Python SDK or subprocess calls to the `docker` CLI) | No new abstraction layer; contributor can inspect exactly what runs; smallest new-dependency surface (`docker` SDK is one package, or zero if shelling out to the CLI). | Manual lifecycle management (start, wait-for-ready polling, port allocation, teardown-on-failure) must be hand-rolled; more code to get "never hang, always clean up" right; easy to leak a container on a crashed test run if teardown isn't in a `finally`/fixture `yield` boundary. |
| `testcontainers-python` (specifically its `testcontainers[postgres]` extra) | Purpose-built for exactly this: ephemeral, auto-torn-down containers per test/session, built-in wait-for-ready strategies, widely used in the Python ecosystem for this exact pattern, integrates cleanly as a pytest fixture. | A new third-party dependency (even if only in an optional extra); version-pins another moving part; still ultimately shells out to Docker, so it does not remove the "Docker must be installed" precondition -- it only removes hand-rolled lifecycle code. |
| `docker-compose` invoked from a test fixture (a checked-in `docker-compose.yml` + `subprocess.run(["docker", "compose", ...])`) | Declarative, human-readable service definition; easy for a contributor to run manually outside pytest for debugging (`docker compose up`); no new *Python* dependency at all (compose ships with Docker Desktop / `docker compose` plugin). | Two lifecycle mechanisms to keep in sync (the compose file's health-check config AND the Python fixture's wait logic); compose's own startup/readiness signaling is coarser than a library's `wait_for_logs`/`wait_for_port` primitives; slightly slower iteration loop (shelling out to the compose CLI vs an in-process client). |

**Recommendation (for the plan phase to adopt, not decided by this spec chain)**:
`testcontainers-python`'s `testcontainers[postgres]` extra is the best fit for this feature's
central requirement (FR-009, honest pending/skipped reporting): it exposes a `wait_for_logs`-
style readiness check with a bounded timeout, and its container lifecycle is already designed to
tear down deterministically (via a context manager / pytest fixture `yield`), which is exactly
the "never leave a stale container, never hang past a timeout" behavior User Story 4 needs.
Raw Docker calls would require re-implementing that readiness/timeout logic by hand, and a
hand-rolled loop is exactly the kind of code that silently degrades into "assume ready after N
seconds" (a hidden-pass risk) if not written carefully. `docker-compose` is a reasonable
alternative if a future implementer prefers zero *Python* dependencies, but its coarser
readiness signaling is a worse match for "distinguish container-failed-to-start from
container-slow-to-start" (edge case in `spec.md`).

**Would-be new optional extra** (described, not added): a `livetest` extra
(`pyproject.toml [project.optional-dependencies]`) bundling `testcontainers[postgres]`, kept
disjoint from `db` (which is only the `psycopg2-binary` runtime driver, reused as-is) and from
`dev` (which CI installs and which must keep installing no Docker-orchestration dependency, so
CI's behavior is provably unchanged by this feature's existence).

## Decision 2: How the ephemeral Postgres is seeded with generic sample data

**Options considered**:

| Option | Pros | Cons |
|--------|------|------|
| Plain `.sql` seed scripts (DDL + `INSERT` statements) checked into the test-harness directory, executed via the real `QueryRunner`/`psycopg2` connection at fixture setup | Matches the repo's existing SQL-first convention (`warehouse/migrations/*.sql`); trivially reviewable as committed text; no new templating layer; directly mirrors how a real table's silver/gold migrations would look, so the seed doubles as a miniature worked-example. | Four defect variants (one per RC check) plus a clean variant means either several near-duplicate SQL files or a single script with parameterized toggles -- needs a deliberate file-per-scenario layout to stay simple (many-small-files, per repo coding style). |
| A Python builder (e.g. a small dataclass-based generator that emits `INSERT` statements) | Enables parameterizing "inject exactly this one defect" programmatically from a single source of truth, reducing duplication across the four defect scenarios. | Diverges from the repo's SQL-as-committed-artifact convention; adds a layer of indirection between "what got seeded" and "what a reviewer can read as plain SQL"; more code to test in its own right. |
| An ORM/fixture library (e.g. `factory_boy`-style factories) | Familiar pattern in some Python test ecosystems for generating rows. | Heavyweight for this feature's small, fixed dataset; another new dependency; the repo has no existing ORM usage to extend, so it would be a one-off pattern with no reuse elsewhere in the kit. |

**Recommendation**: plain `.sql` seed scripts, one clean scenario + one file per defect scenario
(five to six small files total: `seed_clean.sql`, `seed_defect_pk_duplicate.sql`,
`seed_defect_date_gap.sql`, `seed_defect_orphan_fk.sql`, `seed_defect_reconciliation_mismatch.sql`,
`seed_value_check.sql`), executed against the ephemeral database at fixture setup via the same
`psycopg2` connection the real `QueryRunner` uses. This keeps the seed data reviewable as plain
committed SQL (consistent with `warehouse/migrations/` conventions), keeps each scenario's
defect isolated to its own file (satisfying FR-005's "one check's injected defect does not cause
a different check to misfire"), and requires no new templating/generation dependency.

## Decision 3: Structural repo-only vs live-DB separation mechanism

**Options considered**:

| Option | Pros | Cons |
|--------|------|------|
| A dedicated pytest marker, e.g. `@pytest.mark.live_db`, registered in `pyproject.toml`'s pytest config, combined with a directory convention (`tests/live_db/`) | Mirrors the repo's existing `unit`/`integration` marker convention exactly (see global Python rules: "Categorize: `@pytest.mark.unit` / `@pytest.mark.integration`"); a marker is filterable (`pytest -m "not live_db"`) without needing to know directory layout; a directory additionally makes the separation visible in `git status`/file browsing. | Two mechanisms (marker + directory) to keep in sync; a stray test placed in the wrong directory but correctly marked (or vice versa) is a possible drift point -- needs a small wiring test (mirroring the repo's existing "wiring test" pattern, e.g. `tests/unit/test_rules_wiring.py`) asserting every test under `tests/live_db/` carries the marker. |
| Directory-only separation (no marker; rely on contributors only running `pytest tests/live_db/` deliberately) | Simplest; no pytest config change. | Weaker: a plain `pytest` invocation with no path argument would still collect and attempt to run live tests, which risks exactly the "silently hangs/fails when Docker is absent" outcome this feature exists to prevent, unless every live test independently guards itself with a `pytest.importorskip`/fixture-level skip (which the design needs anyway per FR-010, so the marker is a cheap second layer of defense, not a replacement for the skip logic). |
| Marker-only (no directory convention; tests live alongside existing unit tests) | Also simple; leans entirely on marker discipline. | Loses the "visible at a glance in the file tree" benefit; makes it easier to accidentally import a Docker-orchestration library at module scope in a file that also contains repo-only tests, which risks the exact FR-011 violation (a live-surface import leaking where it shouldn't) this feature must avoid. |

**Recommendation**: both -- a dedicated `tests/live_db/` (or `tests/integration/live_db/`,
final path to be confirmed against the repo's actual `tests/` layout in `plan.md`'s Project
Structure section) directory AND a registered `@pytest.mark.live_db` marker, with a small wiring
test asserting the two stay in sync (mirroring the existing `test_rules_wiring.py` pattern
already in this repo). Every test in that directory additionally self-guards with a
session-scoped fixture that attempts Docker/container startup and calls `pytest.skip(reason=...)`
on any precondition failure (FR-009/FR-010), so even a bare `pytest` invocation with no marker
filter fails safe (skips, never hangs, never false-passes) if run on a Docker-less machine.

## Decision 4: How "pass" vs "skipped/pending" is reported, structurally

**Options considered**:

| Option | Pros | Cons |
|--------|------|------|
| Native pytest `skip`/`xfail` outcomes (`pytest.skip(reason=...)` inside the fixture) | Reuses pytest's own PASSED/SKIPPED/FAILED vocabulary, which every contributor and any future CI report already understands; a SKIPPED test is unambiguously distinct from a PASSED one in every pytest report format (terminal, JUnit XML, `--tb`), which directly satisfies SC-004's verifiable claim. | None significant for this use case -- pytest's skip mechanism is exactly built for "this test's precondition wasn't met." |
| A custom result-object/report (e.g. the suite prints its own "LIVE / PENDING / BLOCKED" table independent of pytest's outcome) | Gives full control over the report's wording (can align exactly with the readiness spine's four-status vocabulary: `not_started`/`blocked`/`warning`/`pass`). | Duplicates what pytest already reports; risks drifting from pytest's own outcome (e.g. a test that internally logs "PENDING" but pytest still marks PASSED because it didn't call `skip` or `fail` -- reintroducing the exact hidden-pass risk this feature must close). |

**Recommendation**: use pytest's native `skip` outcome as the primary, structurally-enforced
signal (this is what SC-004 verifies against), and additionally have the suite print a short
human-readable line per scenario naming the precondition (for a contributor reading terminal
output without parsing JUnit XML) -- but the printed line is a convenience layered ON TOP of the
pytest outcome, never a substitute for it. This avoids Option 2's drift risk while still giving
FR-014's "reviewer can act on without reading source code" requirement a concrete, readable line.

## Decision 5: Windows-specific operational risk (Docker Desktop)

Docker Desktop on Windows has known behaviors relevant to this feature's honesty requirement:

- Cold-start latency after a reboot can exceed a naively-short timeout, which -- if the harness's
  readiness wait is too aggressive -- risks a false "container failed to start" skip on a machine
  where Docker is simply slow to warm up, not actually broken. The plan phase should budget a
  generous-but-bounded startup timeout (e.g. tens of seconds, not a few), documented in
  `quickstart.md`, rather than a value tuned only against a CI-speed Linux host.
  Since this feature adds no CI wiring, the timeout only needs to serve local interactive use.
- Docker Desktop requires a running background service/VM; if it is installed but not started,
  the failure mode looks different from "Docker not installed at all" (a connection-refused error
  vs a command-not-found error). Both must map to the same reported precondition family ("Docker
  not available") per the spec's edge cases, so the harness's Docker-availability check should
  treat "installed but not running" and "not installed" as the same honest-skip reason, not leak
  a raw exception message as if it were a novel failure mode.
- Port conflicts are more visible on Windows when a prior WSL2-backed container did not clean up;
  the harness should let the container runtime allocate an ephemeral host port (rather than
  hardcoding one) wherever the chosen library supports it, reducing (not eliminating) the port-
  conflict edge case's likelihood -- the edge case itself (spec.md) still requires detecting and
  honestly reporting a conflict if the library's chosen port happens to collide.

## Alignment with 057 / validate.py / value_proxy.py (the overlap this feature must not duplicate)

- `validate.py` (`retail validate`, feature 004) owns the four live-check *algorithms*. This
  feature reuses them unmodified, via their existing public functions
  (`check_pk_uniqueness`, `check_date_coverage`, `check_orphan_fks`, `check_reconciliation`,
  `run_live_checks`, `make_psycopg2_runner`).
- `value_proxy.py` owns the L4 *algorithm* (`check_expected_value`). This feature reuses it
  unmodified.
- `057-live-validation-evidence-recorder` (`readiness_evidence.build_gold_ready_block`) owns
  turning a `Finding[]` list into a proposed readiness block. This feature calls it, once, to
  DEMONSTRATE that a real live run's output is a valid input to that function -- it does not
  change the function's behavior, its FR-012 "never sets pass" rule, or its FR-013 "emit-only,
  never writes `readiness-status.yaml`" rule.
- This feature's unique contribution, present nowhere else in the repo today, is the **local
  ephemeral database substrate + seed data + skip-honest harness** that gives those three
  existing modules something real to execute against, without cloud infrastructure or
  credentials. See `plan.md`'s Constitution Check and `analysis.md`'s overlap section for the
  full argument that this is additive, not duplicative.
