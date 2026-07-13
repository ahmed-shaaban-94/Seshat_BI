"""Fail-closed validators for public-distribution evidence records.

These helpers validate evidence shape only. They never grant approval, publish
an artifact, or convert a factual check into a readiness score.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping

_SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PROHIBITED_SCORE_KEYS = {
    "confidence",
    "confidence_score",
    "readiness_score",
    "score",
}

PUBLICATION_ACTIONS = {
    "configure_pypi_trusted_publisher",
    "publish_pypi",
    "publish_github_release",
    "publish_claude_marketplace",
    "submit_claude_catalog",
    "create_release_tag",
    "rollback_pypi",
    "rollback_github_release",
    "rollback_claude_marketplace",
    "rollback_claude_catalog",
    "rollback_codex_marketplace",
    "submit_openai_plugin",
    "publish_openai_plugin",
    "rollback_openai_plugin",
}

PUBLIC_SURFACES = {
    "python_pypi",
    "claude_repository",
    "codex_repository",
    "claude_public_catalog",
    "openai_public_plugin",
}
COORDINATED_REQUIRED_SURFACES = {
    "python_pypi",
    "claude_repository",
    "codex_repository",
}
ROLLBACK_ACTIONS_BY_SURFACE = {
    "python_pypi": {"rollback_pypi"},
    "claude_repository": {"rollback_claude_marketplace"},
    "codex_repository": {"rollback_codex_marketplace"},
    "claude_public_catalog": {"rollback_claude_catalog"},
    "openai_public_plugin": {"rollback_openai_plugin"},
}


class EvidenceValidationError(ValueError):
    """Evidence is incomplete, ambiguous, or outside the safe contract."""


def _require_mapping(record: object, label: str) -> Mapping[str, Any]:
    if not isinstance(record, Mapping):
        raise EvidenceValidationError(f"{label} must be an object")
    return record


def _require_fields(record: Mapping[str, Any], fields: set[str]) -> None:
    missing = sorted(field for field in fields if field not in record)
    if missing:
        raise EvidenceValidationError(f"missing required fields: {', '.join(missing)}")


def _require_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise EvidenceValidationError(f"{field} must be non-empty text")
    return value


def _require_timestamp(record: Mapping[str, Any], field: str) -> datetime:
    value = _require_text(record, field)
    if not value.endswith("Z"):
        raise EvidenceValidationError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise EvidenceValidationError(
            f"{field} must be an ISO-8601 UTC timestamp"
        ) from exc
    if parsed.tzinfo != timezone.utc:
        raise EvidenceValidationError(f"{field} must be UTC")
    return parsed


def _require_artifact_digests(
    record: Mapping[str, Any], field: str = "artifact_digests"
) -> Mapping[str, str]:
    value = record.get(field)
    if not isinstance(value, Mapping) or not value:
        raise EvidenceValidationError(f"{field} must be a non-empty object")
    for name, digest in value.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(digest, str):
            raise EvidenceValidationError(f"{field} contains an invalid entry")
        if _SHA256.fullmatch(digest) is None:
            raise EvidenceValidationError(f"artifact digest for {name} must be SHA-256")
    return value


def _require_text_list(
    record: Mapping[str, Any], field: str, *, allow_empty: bool = False
) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise EvidenceValidationError(f"{field} must be a list of concrete strings")
    if not value and not allow_empty:
        raise EvidenceValidationError(f"{field} must not be empty")
    return value


def _reject_scores(value: object, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in _PROHIBITED_SCORE_KEYS:
                raise EvidenceValidationError(
                    f"{path}.{key} is prohibited; evidence uses status and blockers"
                )
            _reject_scores(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_scores(child, f"{path}[{index}]")


def _validate_status_and_blockers(
    record: Mapping[str, Any], *, allowed: set[str]
) -> None:
    status = record.get("status")
    if status not in allowed:
        raise EvidenceValidationError(
            f"status must be one of: {', '.join(sorted(allowed))}"
        )
    blockers = record.get("blockers")
    if not isinstance(blockers, list) or any(
        not isinstance(item, str) or not item.strip() for item in blockers
    ):
        raise EvidenceValidationError("blockers must be a list of concrete strings")
    if status in {"blocked", "fail"} and not blockers:
        raise EvidenceValidationError(f"{status} evidence requires concrete blockers")
    if status in {"validated", "pass", "approved", "completed"} and blockers:
        raise EvidenceValidationError(f"{status} evidence cannot retain blockers")


def validate_release_candidate(record: object) -> Mapping[str, Any]:
    """Validate a release-candidate evidence record and return it unchanged."""

    item = _require_mapping(record, "release candidate")
    _reject_scores(item)
    _require_fields(
        item,
        {
            "schema_version",
            "candidate_id",
            "version",
            "source_revision",
            "artifact_digests",
            "status",
            "blockers",
            "created_at",
            "authority_disclaimer",
        },
    )
    if item.get("schema_version") != "1.0":
        raise EvidenceValidationError("schema_version must be 1.0")
    _require_text(item, "candidate_id")
    version = _require_text(item, "version")
    if _SEMVER.fullmatch(version) is None:
        raise EvidenceValidationError("version must be SemVer")
    revision = _require_text(item, "source_revision")
    if _FULL_SHA.fullmatch(revision) is None:
        raise EvidenceValidationError(
            "source_revision must be a full lowercase Git SHA"
        )
    _require_artifact_digests(item)
    _validate_status_and_blockers(item, allowed={"blocked", "validated"})
    _require_timestamp(item, "created_at")
    _require_text(item, "authority_disclaimer")
    return item


def validate_external_acceptance(record: object) -> Mapping[str, Any]:
    """Validate one external Claude/Codex acceptance observation."""

    item = _require_mapping(record, "external acceptance")
    _reject_scores(item)
    _require_fields(
        item,
        {
            "schema_version",
            "run_id",
            "candidate_id",
            "platform",
            "client",
            "fresh_workspace",
            "development_repo_available",
            "fixture_id",
            "observed_stage",
            "next_action",
            "human_gate_observed",
            "secrets_or_pii_exposed",
            "fabricated_score",
            "status",
            "blockers",
            "recorded_at",
        },
    )
    if item.get("schema_version") != "1.0":
        raise EvidenceValidationError("schema_version must be 1.0")
    if item.get("platform") not in {"claude-code", "codex"}:
        raise EvidenceValidationError("platform must be claude-code or codex")
    for field in (
        "fresh_workspace",
        "development_repo_available",
        "human_gate_observed",
        "secrets_or_pii_exposed",
        "fabricated_score",
    ):
        if not isinstance(item.get(field), bool):
            raise EvidenceValidationError(f"{field} must be boolean")
    if item.get("fresh_workspace") is not True:
        raise EvidenceValidationError("acceptance must use a fresh workspace")
    if item.get("development_repo_available") is not False:
        raise EvidenceValidationError("acceptance must hide the development repository")
    if item.get("secrets_or_pii_exposed") is not False:
        raise EvidenceValidationError("acceptance exposed secrets or PII")
    if item.get("fabricated_score") is not False:
        raise EvidenceValidationError("acceptance fabricated a readiness score")
    _require_text(item, "run_id")
    _require_text(item, "candidate_id")
    _require_text(item, "client")
    _require_text(item, "fixture_id")
    _require_text(item, "observed_stage")
    _require_text(item, "next_action")
    _validate_status_and_blockers(item, allowed={"fail", "pass"})
    _require_timestamp(item, "recorded_at")
    return item


def validate_publication_approval(
    record: object,
    *,
    candidate_id: str | None = None,
    version: str | None = None,
    source_revision: str | None = None,
    artifact_digests: Mapping[str, str] | None = None,
    action: str | None = None,
) -> Mapping[str, Any]:
    """Validate exact, named, action-scoped publication authority."""

    item = _require_mapping(record, "publication approval")
    _reject_scores(item)
    _require_fields(
        item,
        {
            "schema_version",
            "approval_id",
            "candidate_id",
            "version",
            "source_revision",
            "artifact_digests",
            "action",
            "approver",
            "scope",
            "evidence_reviewed",
            "constraints",
            "approved_at",
            "expires_at",
            "status",
            "authority_disclaimer",
        },
    )
    if item.get("schema_version") != "1.0":
        raise EvidenceValidationError("schema_version must be 1.0")
    for field in (
        "approval_id",
        "candidate_id",
        "approver",
        "scope",
        "authority_disclaimer",
    ):
        _require_text(item, field)
    recorded_version = _require_text(item, "version")
    if _SEMVER.fullmatch(recorded_version) is None:
        raise EvidenceValidationError("version must be SemVer")
    recorded_revision = _require_text(item, "source_revision")
    if _FULL_SHA.fullmatch(recorded_revision) is None:
        raise EvidenceValidationError(
            "source_revision must be a full lowercase Git SHA"
        )
    recorded_digests = _require_artifact_digests(item)
    recorded_action = _require_text(item, "action")
    if recorded_action not in PUBLICATION_ACTIONS:
        raise EvidenceValidationError("action is not an allowed owner-only action")
    if item.get("status") != "approved":
        raise EvidenceValidationError("status must be approved")
    approved_at = _require_timestamp(item, "approved_at")
    expires_at = _require_timestamp(item, "expires_at")
    if expires_at <= approved_at:
        raise EvidenceValidationError("expires_at must be later than approved_at")
    _require_text_list(item, "evidence_reviewed")
    _require_text_list(item, "constraints", allow_empty=True)
    expected = {
        "candidate_id": candidate_id,
        "version": version,
        "source_revision": source_revision,
        "action": action,
    }
    for field, value in expected.items():
        if value is not None and item.get(field) != value:
            raise EvidenceValidationError(
                f"approval {field} does not match the requested action scope"
            )
    if artifact_digests is not None and dict(recorded_digests) != dict(
        artifact_digests
    ):
        raise EvidenceValidationError(
            "approval artifact_digests do not match the requested action scope"
        )
    return item


def validate_action_authorization(
    record: object,
    *,
    candidate_id: str,
    version: str,
    source_revision: str,
    artifact_digests: Mapping[str, str],
    action: str,
    used_approval_ids: set[str] | frozenset[str] = frozenset(),
    at: datetime | None = None,
) -> Mapping[str, Any]:
    """Validate a still-current, unused approval for one exact action."""

    item = validate_publication_approval(
        record,
        candidate_id=candidate_id,
        version=version,
        source_revision=source_revision,
        artifact_digests=artifact_digests,
        action=action,
    )
    approval_id = str(item["approval_id"])
    if approval_id in used_approval_ids:
        raise EvidenceValidationError(
            "approval was already consumed and cannot authorize another action"
        )
    checked_at = at or datetime.now(timezone.utc)
    expires_at = _require_timestamp(item, "expires_at")
    if expires_at <= checked_at:
        raise EvidenceValidationError("approval has expired")
    return item


def validate_surface_availability(record: object) -> Mapping[str, Any]:
    """Validate truthful per-surface availability and coordinated wording."""

    item = _require_mapping(record, "surface availability")
    _reject_scores(item)
    _require_fields(
        item,
        {
            "schema_version",
            "surfaces",
            "coordinated_release_status",
            "summary",
        },
    )
    if item.get("schema_version") != "1.0":
        raise EvidenceValidationError("schema_version must be 1.0")
    surfaces = _require_mapping(item.get("surfaces"), "surfaces")
    if set(surfaces) != PUBLIC_SURFACES:
        raise EvidenceValidationError("availability must name every public surface")
    allowed = {"available", "unavailable", "unverified", "blocked"}
    for name, raw in surfaces.items():
        surface = _require_mapping(raw, f"surface {name}")
        status = surface.get("status")
        if status not in allowed:
            raise EvidenceValidationError(
                f"surface {name} status must be available, unavailable, "
                "unverified, or blocked"
            )
        reason = surface.get("reason")
        if status != "available" and (
            not isinstance(reason, str) or not reason.strip()
        ):
            raise EvidenceValidationError(
                f"surface {name} {status} status requires a concrete reason"
            )
    coordinated = item.get("coordinated_release_status")
    if coordinated not in allowed:
        raise EvidenceValidationError("coordinated_release_status is invalid")
    required_available = all(
        surfaces[name].get("status") == "available"
        for name in COORDINATED_REQUIRED_SURFACES
    )
    summary = _require_text(item, "summary")
    if coordinated == "available" and not required_available:
        raise EvidenceValidationError(
            "coordinated release cannot be available while a required surface is not"
        )
    if not required_available and "full launch" in summary.casefold():
        raise EvidenceValidationError(
            "partial availability must not be described as a full launch"
        )
    return item


def validate_rollback_record(record: object) -> Mapping[str, Any]:
    """Validate rollback evidence without treating rollback as self-authorizing."""

    item = _require_mapping(record, "rollback record")
    _reject_scores(item)
    _require_fields(
        item,
        {
            "schema_version",
            "rollback_id",
            "candidate_id",
            "surface",
            "trigger",
            "actor",
            "action",
            "status",
            "blockers",
            "recorded_at",
            "approval_id",
        },
    )
    if item.get("schema_version") != "1.0":
        raise EvidenceValidationError("schema_version must be 1.0")
    for field in (
        "rollback_id",
        "candidate_id",
        "surface",
        "trigger",
        "actor",
        "action",
        "approval_id",
    ):
        _require_text(item, field)
    surface = _require_text(item, "surface")
    if surface not in ROLLBACK_ACTIONS_BY_SURFACE:
        raise EvidenceValidationError("rollback surface is not a public surface")
    action = str(item.get("action"))
    if (
        action not in PUBLICATION_ACTIONS
        or action not in ROLLBACK_ACTIONS_BY_SURFACE[surface]
    ):
        raise EvidenceValidationError(
            "rollback action must match the affected public surface"
        )
    _validate_status_and_blockers(item, allowed={"blocked", "completed"})
    _require_timestamp(item, "recorded_at")
    return item


def validate_rollback_authorization(
    rollback_record: object,
    approval_record: object,
    *,
    version: str,
    source_revision: str,
    artifact_digests: Mapping[str, str],
    used_approval_ids: set[str] | frozenset[str] = frozenset(),
    at: datetime | None = None,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Bind rollback evidence to a fresh approval for that affected surface."""

    rollback = validate_rollback_record(rollback_record)
    approval = validate_action_authorization(
        approval_record,
        candidate_id=str(rollback["candidate_id"]),
        version=version,
        source_revision=source_revision,
        artifact_digests=artifact_digests,
        action=str(rollback["action"]),
        used_approval_ids=used_approval_ids,
        at=at,
    )
    if rollback.get("approval_id") != approval.get("approval_id"):
        raise EvidenceValidationError(
            "rollback record approval_id does not match its action-scoped approval"
        )
    return rollback, approval
