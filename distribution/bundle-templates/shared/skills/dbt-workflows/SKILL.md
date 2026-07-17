---
name: dbt-workflows
description: >-
  Use when a user asks to check, validate, plan, build, test, troubleshoot, or
  review Seshat BI's governed dbt shadow transformations and parity evidence.
---

# Governed dbt workflows

Read `../../portable-operating-contract.md` before acting. Use only the
installed `seshat dbt` helpers; never bypass their fixed selector, target,
profile, lock, redaction, or artifact checks with raw dbt commands.

## Fixed workflow

1. Check prerequisites without a database query:

   `seshat dbt doctor --format json`

2. Validate the Mapping Ready gate, shadow schemas, selector, and citations:

   `seshat dbt validate --table <table> --format json`

3. Produce and review the immutable plan:

   `seshat dbt plan --table <table> --format json`

   Confirm the approved mapping identity, pinned dbt versions, exact selected
   model/test IDs, and shadow-only schemas. The returned `digest` is the only
   valid `--accept-plan` value; it is neither a mapping approval nor a readiness
   approval.

4. With the reviewed digest, execute the fixed graph:

   `seshat dbt build --table <table> --accept-plan <digest> --format json`

   Use `seshat dbt test --table <table> --accept-plan <digest> --format json`
   only for a test-only rerun. Both recompute the plan before database access;
   drift stops execution and requires a new plan and review.

5. Review the returned normalized evidence. When a user supplies an existing
   run directory under `.seshat/dbt/runs/`, revalidate it offline with:

   `seshat dbt inspect-run --table <table> --artifacts <run-directory> --format json`

   Do not invent a run directory or treat `inspect-run` as a required second
   build. Report parity failures and `blocking_reasons`, then stop for a named human.
   Passing output is derived evidence only.

## Hard boundaries

- Stop before planning unless Mapping Ready has a named-human approval.
- Put real `SESHAT_DBT_*` values only in the gitignored `.env`; keep
  `profiles.yml` as `env_var()` references.
- If the dbt extra, profile, DSN, or live database is absent, report
  `[PENDING LIVE PROFILE]` with enable steps; never fabricate compile, build,
  test, or parity success.
- Migrations remain the default build path after parity. A separate named
  human must approve switching the active path, and migrations remain the
  parity oracle and rollback path until separately retired.
- Never write a readiness pass, migration-switch approval, confidence score,
  raw adapter output, credential, DSN, or absolute local path.

## Exit meanings

- exit 0: command completed; dbt output remains derived evidence.
- exit 1: handled model, test, or parity failure.
- exit 2: usage or runtime/profile/database prerequisite unavailable.
- exit 3: governance refusal, lock conflict, or accepted-plan drift.
- exit 4: artifact or normalized-evidence integrity failure.
