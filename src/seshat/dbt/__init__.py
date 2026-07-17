"""Governed dbt transformation adapter.

This package deliberately imports no dbt module or database driver. External dbt
execution is resolved lazily by the runner in the active Python environment.
"""

from __future__ import annotations

DBT_CORE_VERSION = "1.12.0"
DBT_POSTGRES_VERSION = "1.10.2"
PROFILE_NAME = "seshat_bi_warehouse"
TARGET_NAME = "shadow"

__all__ = [
    "DBT_CORE_VERSION",
    "DBT_POSTGRES_VERSION",
    "PROFILE_NAME",
    "TARGET_NAME",
]
