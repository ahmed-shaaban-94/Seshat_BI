"""The pluggable Bronze SOURCE-ADAPTER contract (issues #404 / #405).

A *source adapter* is the seam that satisfies the ingest head for one table:
it makes ``bronze.<table>`` be the agreed starting point for the gated tail,
and reports -- as an immutable :class:`SourcePrepared` value -- WHAT it did and
whether it touched the customer's data.

The contract is deliberately small and driver-free (stdlib + typing only): no
dagster, no psycopg2. Concrete adapters live in the orchestration package,
where the DB driver and dagster context are available, and delegate their
actual DB work to the lazily-imported ``db`` boundary. Keeping the Protocol,
the result type, and the fail-closed mode->adapter resolution here means the
whole seam is unit-testable in the parent environment with a fake adapter --
exactly as the runner's argv is tested without launching a child.

Two source modes ship (see :mod:`.source_mode`):

* CSV (default): a landing file OWNS and (re)creates the Bronze relation. This
  is the one mode that WRITES Bronze; it is destructive-by-design and unchanged
  from the pre-feature path.
* existing-Bronze: a pre-loaded Bronze relation is verified READ-ONLY. It is
  NON-DESTRUCTIVE -- it issues no DDL/DML and returns ``mutated_bronze=False``.

The extension point (#405): a new origin (object storage, API, stream) ships a
new mode token in :mod:`.source_mode` plus a new adapter satisfying this
Protocol, with NO change to the medallion graph, the jobs, or the gate tail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .source_mode import EXISTING_BRONZE


@dataclass(frozen=True)
class SourcePrepared:
    """The immutable outcome of preparing the Bronze relation for one table.

    ``outcome`` is an execution word the evidence layer accepts
    (``materialized`` on success; a halting adapter raises before returning, so
    this type only ever carries a successful preparation). ``measured`` is the
    free-form facts dict the asset merges into its evidence ``measured`` field
    (rows, columns, the resolved ``source_mode``). ``mutated_bronze`` is the
    load-bearing non-destruction flag: existing-Bronze MUST return ``False``.
    """

    source_mode: str
    outcome: str
    measured: dict = field(default_factory=dict)
    mutated_bronze: bool = False


@runtime_checkable
class SourceAdapter(Protocol):
    """A pluggable Bronze origin.

    One method: satisfy the ingest head for ``table`` and return what happened.
    An adapter that cannot proceed (absent DSN, missing landing file, absent /
    mismatched existing Bronze) MUST fail closed with a named blocker -- it
    raises through the asset's ``halt`` seam rather than returning a fabricated
    success. It NEVER writes readiness truth and, in a non-destructive mode,
    NEVER issues Bronze DDL/DML.
    """

    #: The closed mode token this adapter serves (a member of SOURCE_MODES).
    source_mode: str

    def prepare_bronze(self, table: str) -> SourcePrepared:
        """Make ``bronze.<table>`` the satisfied ingest upstream for ``table``.

        Returns a :class:`SourcePrepared` on success; raises (via the caller's
        fail-closed halt) on any blocking condition.
        """
        ...


#: Modes that are READ-ONLY against Bronze (issue zero DDL/DML). Everything
#: NOT in this set is treated as destructive, so a mislabeled / future mode can
#: never accidentally claim a false non-destruction guarantee (fail-closed).
_NON_DESTRUCTIVE_MODES: frozenset[str] = frozenset({EXISTING_BRONZE})


def is_destructive_mode(source_mode: str) -> bool:
    """True unless ``source_mode`` is a known READ-ONLY Bronze mode.

    existing-Bronze is read-only. CSV owns and recreates Bronze
    (destructive-by-design). Any unknown value is treated as destructive so a
    mislabeled or future mode never claims a false non-destruction guarantee.
    """
    return source_mode not in _NON_DESTRUCTIVE_MODES
