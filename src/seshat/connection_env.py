"""`.env`-aware environment for live DB connection resolution (issue #340).

`validate` / `drift` / `value-check` resolved the DB connection from
`dict(os.environ)` only, so a user who put the `ANALYTICS_DB_*` credentials in
the gitignored `.env` -- exactly as the tool's own error text, `.env.example`,
and the README all instruct -- still got "no database connection configured".

``connection_environment`` returns the process environment merged with the
workspace `.env`, so those resolution sites see the documented `.env` values.
Two invariants, both deliberate:

  - **Real environment variables win over `.env`** (least surprise: an
    explicitly exported var overrides the file), so `.env` only *fills gaps*.
  - **The process environment is never mutated** -- a COPY is returned, matching
    the non-mutation posture of ``dbt.redaction.load_child_environment``.

The `.env` parser is reused from ``seshat.dbt.redaction`` (governed,
dependency-free); no `python-dotenv` dependency is added.
"""

from __future__ import annotations

import os
from pathlib import Path


def connection_environment(repo_root: Path | str) -> dict[str, str]:
    """Process env merged with ``repo_root/.env``; env wins, no mutation.

    Missing `.env` returns a plain copy of the process environment. A malformed
    `.env` raises ``seshat.dbt.redaction.EnvironmentConfigError`` (the governed
    parser's contract) rather than silently ignoring the file.
    """
    from seshat.dbt.redaction import dotenv_values

    env = dict(os.environ)
    dotenv_path = Path(repo_root) / ".env"
    if dotenv_path.is_file():
        for key, value in dotenv_values(dotenv_path).items():
            env.setdefault(key, value)  # real env wins over .env
    return env
