"""DAX Generator (Phase 1): contract `definition` -> verified DAX measure.

The INVERSE of metric_drift.check_measure_drift: that answers "does this DAX
match this contract?"; this answers "what DAX matches this contract?", then
feeds its own output back through the checker. Fail-closed: `pass` is the only
acceptable round-trip; anything else is a refusal (no DAX/TMDL emitted).

Stdlib-only at import time (mirrors metric_drift.py). `yaml` is imported lazily
ONLY in load_contract(); this module is never in the `retail check` core chain.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["GenResult", "generate_measure", "load_contract"]


@dataclass(frozen=True)
class GenResult:
    """A sum type: EITHER (ok=True, dax, tmdl_block) OR (ok=False, reason).

    On refusal, dax and tmdl_block are None -- a caller cannot fish an
    unverified partial out of a refusal.
    """

    ok: bool
    dax: str | None = None
    tmdl_block: str | None = None
    reason: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.ok:
            if self.dax is None or self.tmdl_block is None:
                raise ValueError("ok GenResult must populate dax and tmdl_block")
            if self.reason is not None:
                raise ValueError("ok GenResult must not carry a reason")
        else:
            if self.dax is not None or self.tmdl_block is not None:
                raise ValueError("refusal GenResult must not carry dax/tmdl_block")
            if not self.reason:
                raise ValueError("refusal GenResult must carry a reason")

    @classmethod
    def success(
        cls, dax: str, tmdl_block: str, warnings: tuple[str, ...] = ()
    ) -> "GenResult":
        return cls(ok=True, dax=dax, tmdl_block=tmdl_block, warnings=warnings)

    @classmethod
    def refuse(cls, reason: str) -> "GenResult":
        return cls(ok=False, reason=reason)
