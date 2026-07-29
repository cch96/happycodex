from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .types import (
    Anchor,
    DigestAnchor,
    EvidenceKind,
    EvidenceRef,
    EvidenceSourceId,
    FalsifierId,
    Finding,
    FindingCatalog,
    FindingId,
    FindingStatus,
    Marker,
    MarkerId,
    ModelObservation,
    ReceiptAnchor,
    ReceiptKind,
    RepoPath,
    RepositoryId,
    SafeText,
    SemanticValidationError,
    Sha256,
    ClaimId,
)


REPO_PATH_FIELDS = ("path", "repository_id", "tag")
EVIDENCE_REF_FIELDS = ("identity", "kind", "source", "tag")
FINDING_FIELDS = (
    "anchors",
    "claim_id",
    "claim_text",
    "evidence",
    "falsifier_id",
    "falsifier_text",
    "finding_id",
    "status",
    "tag",
)
MODEL_OBSERVATION_FIELDS = ("observations", "proposed_findings")
TERMINAL_AGENT_RESULT_FIELDS = (
    "attempt_key",
    "completion_tag",
    "model_observation",
    "provider",
    "schema_generation",
    "session",
    "thread",
    "turn",
)
COMPLETION_EVENT_FIELDS = (
    "attempt_key",
    "provider",
    "result_digest",
    "session",
    "thread",
    "turn",
    "usage",
)


def _strict_mapping(value: object, *, name: str, fields: tuple[str, ...]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SemanticValidationError(f"{name} must be an object")
    if any(not isinstance(key, str) for key in value):
        raise SemanticValidationError(f"{name} keys must be strings")
    keys = tuple(sorted(value))
    expected = tuple(sorted(fields))
    if keys != expected:
        missing = tuple(field for field in expected if field not in value)
        unknown = tuple(field for field in keys if field not in fields)
        raise SemanticValidationError(
            f"{name} fields mismatch: missing={missing}, unknown={unknown}"
        )
    return value


def _strict_list(value: object, *, name: str, maximum: int) -> list[Any]:
    if not isinstance(value, list):
        raise SemanticValidationError(f"{name} must be a JSON array")
    if len(value) > maximum:
        from .types import CapacityError

        raise CapacityError(limit=maximum, actual=len(value))
    return value


def _required_string(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise SemanticValidationError(f"{name} must be a string")
    return value


def parse_repo_path(value: object) -> RepoPath:
    record = _strict_mapping(value, name="RepoPath", fields=REPO_PATH_FIELDS)
    if record["tag"] != "RepoPath":
        raise SemanticValidationError("unknown anchor tag")
    return RepoPath(
        RepositoryId(_required_string(record["repository_id"], name="repository_id")),
        _required_string(record["path"], name="path"),
    )


def parse_anchor(value: object) -> Anchor:
    if not isinstance(value, Mapping) or not isinstance(value.get("tag"), str):
        raise SemanticValidationError("anchor requires an exact tag")
    tag = value["tag"]
    if tag == "RepoPath":
        return parse_repo_path(value)
    if tag == "Marker":
        record = _strict_mapping(value, name="Marker", fields=("marker_id", "tag"))
        return Marker(MarkerId(_required_string(record["marker_id"], name="marker_id")))
    if tag == "Digest":
        record = _strict_mapping(value, name="Digest", fields=("kind", "sha256", "tag"))
        return DigestAnchor(
            _required_string(record["kind"], name="kind"),
            Sha256(_required_string(record["sha256"], name="sha256")),
        )
    if tag == "Receipt":
        record = _strict_mapping(
            value,
            name="Receipt",
            fields=("receipt_kind", "sha256", "tag"),
        )
        return ReceiptAnchor(
            ReceiptKind(_required_string(record["receipt_kind"], name="receipt_kind")),
            Sha256(_required_string(record["sha256"], name="sha256")),
        )
    raise SemanticValidationError(f"unknown anchor tag: {tag}")


def parse_evidence_ref(value: object) -> EvidenceRef:
    record = _strict_mapping(value, name="EvidenceRef", fields=EVIDENCE_REF_FIELDS)
    if record["tag"] != "EvidenceRef":
        raise SemanticValidationError("unknown evidence tag")
    try:
        kind = EvidenceKind(_required_string(record["kind"], name="kind"))
    except ValueError as error:
        raise SemanticValidationError("unknown EvidenceKind") from error
    return EvidenceRef(
        kind,
        Sha256(_required_string(record["identity"], name="identity")),
        EvidenceSourceId(_required_string(record["source"], name="source")),
    )


def parse_proposed_finding(value: object) -> Finding:
    record = _strict_mapping(value, name="Finding", fields=FINDING_FIELDS)
    if record["tag"] != "Finding":
        raise SemanticValidationError("unknown finding tag")
    try:
        status = FindingStatus(_required_string(record["status"], name="status"))
    except ValueError as error:
        raise SemanticValidationError("unknown FindingStatus") from error
    anchors = tuple(
        parse_anchor(item)
        for item in _strict_list(record["anchors"], name="anchors", maximum=64)
    )
    evidence = tuple(
        parse_evidence_ref(item)
        for item in _strict_list(record["evidence"], name="evidence", maximum=256)
    )
    return Finding.proposed(
        finding_id=FindingId(_required_string(record["finding_id"], name="finding_id")),
        claim_id=ClaimId(_required_string(record["claim_id"], name="claim_id")),
        falsifier_id=FalsifierId(
            _required_string(record["falsifier_id"], name="falsifier_id")
        ),
        status=status,
        anchors=anchors,
        claim_text=SafeText(_required_string(record["claim_text"], name="claim_text")),
        falsifier_text=SafeText(
            _required_string(record["falsifier_text"], name="falsifier_text")
        ),
        evidence=evidence,
    )


def parse_model_observation(
    value: object,
    *,
    catalog: FindingCatalog,
) -> ModelObservation:
    record = _strict_mapping(
        value,
        name="ModelObservation",
        fields=MODEL_OBSERVATION_FIELDS,
    )
    observations = tuple(
        SafeText(_required_string(item, name="observation"))
        for item in _strict_list(
            record["observations"],
            name="observations",
            maximum=256,
        )
    )
    proposed = tuple(
        parse_proposed_finding(item)
        for item in _strict_list(
            record["proposed_findings"],
            name="proposed_findings",
            maximum=64,
        )
    )
    existing = set(catalog.existing_finding_ids)
    claims = set(catalog.claim_ids)
    falsifiers = set(catalog.falsifier_ids)
    namespace_prefix = f"{catalog.namespace}."
    proposed_ids: set[FindingId] = set()
    for finding in proposed:
        if (
            not finding.finding_id.value.startswith(namespace_prefix)
            or finding.finding_id.value == namespace_prefix
        ):
            raise SemanticValidationError(
                "model proposal FindingId is outside the exact catalog namespace"
            )
        if finding.finding_id in proposed_ids:
            raise SemanticValidationError("duplicate proposed FindingId")
        proposed_ids.add(finding.finding_id)
        if finding.finding_id in existing:
            raise SemanticValidationError("model proposal must use a new FindingId")
        if finding.claim_id not in claims:
            raise SemanticValidationError("model proposal ClaimId is outside the catalog")
        if finding.falsifier_id not in falsifiers:
            raise SemanticValidationError("model proposal FalsifierId is outside the catalog")
    return ModelObservation(observations, proposed)


__all__ = (
    "COMPLETION_EVENT_FIELDS",
    "EVIDENCE_REF_FIELDS",
    "FINDING_FIELDS",
    "MODEL_OBSERVATION_FIELDS",
    "REPO_PATH_FIELDS",
    "TERMINAL_AGENT_RESULT_FIELDS",
    "parse_anchor",
    "parse_evidence_ref",
    "parse_model_observation",
    "parse_proposed_finding",
    "parse_repo_path",
)
