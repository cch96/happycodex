from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from types import MappingProxyType
from typing import Any, Mapping, TypeVar


class SemanticValidationError(ValueError):
    """A semantic value is malformed, ambiguous, or outside the frozen schema."""


class CapacityError(SemanticValidationError):
    """A bounded collection overflowed without truncation or eviction."""

    def __init__(self, *, limit: int, actual: int) -> None:
        self.limit = limit
        self.actual = actual
        super().__init__(f"capacity exceeded: limit={limit}, actual={actual}")


def _require_exact_int(value: object, *, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise SemanticValidationError(f"{name} must be an integer >= {minimum}")
    return value


def _require_exact_bool(value: object, *, name: str) -> bool:
    if type(value) is not bool:
        raise SemanticValidationError(f"{name} must be a boolean")
    return value


def _require_instance(value: object, expected: type | tuple[type, ...], *, name: str) -> None:
    allowed = expected if isinstance(expected, tuple) else (expected,)
    if type(value) not in allowed:
        raise SemanticValidationError(f"{name} has the wrong tagged type")


def _require_tuple_instances(values: object, expected: type | tuple[type, ...], *, name: str) -> None:
    allowed = expected if isinstance(expected, tuple) else (expected,)
    if not isinstance(values, tuple) or any(type(value) not in allowed for value in values):
        raise SemanticValidationError(f"{name} must be an immutable tuple of exact tagged values")


def _require_text(value: object, *, name: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise SemanticValidationError(f"{name} must be nonblank exact text")
    if len(value) > maximum or any(ord(character) < 32 for character in value):
        raise SemanticValidationError(f"{name} exceeds its safe text boundary")
    return value


def _require_identifier(value: object, *, name: str) -> str:
    text = _require_text(value, name=name, maximum=512)
    if "\\" in text or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/=+@-]*", text) is None:
        raise SemanticValidationError(
            f"{name} must match the bounded case-sensitive ASCII identity grammar"
        )
    return text


@dataclass(frozen=True)
class _Identifier:
    value: str

    def __post_init__(self) -> None:
        _require_identifier(self.value, name=type(self).__name__)


@dataclass(frozen=True)
class FindingId(_Identifier):
    pass


@dataclass(frozen=True)
class ClaimId(_Identifier):
    pass


@dataclass(frozen=True)
class FalsifierId(_Identifier):
    pass


@dataclass(frozen=True)
class EvidenceSourceId(_Identifier):
    pass


@dataclass(frozen=True)
class MarkerId(_Identifier):
    pass


@dataclass(frozen=True)
class RepositoryId(_Identifier):
    pass


@dataclass(frozen=True)
class GateWorkId(_Identifier):
    pass


@dataclass(frozen=True)
class CheckId(_Identifier):
    pass


@dataclass(frozen=True)
class ResourceId(_Identifier):
    pass


@dataclass(frozen=True)
class DecisionTargetId(_Identifier):
    pass


@dataclass(frozen=True)
class InfrastructureId(_Identifier):
    pass


@dataclass(frozen=True)
class ReceiptKind(_Identifier):
    pass


@dataclass(frozen=True)
class AttemptTarget(_Identifier):
    pass


@dataclass(frozen=True)
class AttemptScope(_Identifier):
    pass


@dataclass(frozen=True)
class SafeText:
    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, name="SafeText", maximum=4096)


@dataclass(frozen=True)
class Sha256:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or re.fullmatch(r"[0-9a-f]{64}", self.value) is None:
            raise SemanticValidationError("Sha256 must be lowercase 64-hex")


@dataclass(frozen=True)
class StateKey(Sha256):
    pass


@dataclass(frozen=True)
class AttemptKey(Sha256):
    pass


@dataclass(frozen=True)
class ReceiptLinkHash(Sha256):
    pass


@dataclass(frozen=True)
class GitCommit:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or re.fullmatch(r"[0-9a-f]{40}", self.value) is None:
            raise SemanticValidationError("GitCommit must be lowercase 40-hex")


@dataclass(frozen=True)
class GitTree:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or re.fullmatch(r"[0-9a-f]{40}", self.value) is None:
            raise SemanticValidationError("GitTree must be lowercase 40-hex")


class FindingStatus(str, Enum):
    OPEN = "OPEN"
    UNKNOWN = "UNKNOWN"
    RESOLVED = "RESOLVED"
    BASELINE_ACCEPTED = "BASELINE_ACCEPTED"


class GateId(str, Enum):
    CONTRACT_FREEZE = "CONTRACT_FREEZE"
    IMPLEMENTATION = "IMPLEMENTATION"
    CUMULATIVE_CHECKS = "CUMULATIVE_CHECKS"
    FOCUSED_REVIEW = "FOCUSED_REVIEW"
    CANDIDATE_FREEZE = "CANDIDATE_FREEZE"
    EXACT_FINAL = "EXACT_FINAL"
    EXECUTOR_PILOT = "EXECUTOR_PILOT"
    CORPUS = "CORPUS"
    HOLDOUT = "HOLDOUT"
    RECEIPT = "RECEIPT"
    ISOLATED_INSTALL = "ISOLATED_INSTALL"
    RELEASE = "RELEASE"
    ACTIVATION = "ACTIVATION"
    GOAL_PAUSE = "GOAL_PAUSE"


class GateState(str, Enum):
    OPEN = "OPEN"
    SATISFIED = "SATISFIED"
    WAIVED = "WAIVED"
    BLOCKED = "BLOCKED"


class ClaimState(str, Enum):
    OPEN = "OPEN"
    VERIFIED = "VERIFIED"
    N_A = "N_A"


class EvidenceKind(str, Enum):
    SOURCE = "SOURCE"
    CONFIG = "CONFIG"
    AUTHORITY = "AUTHORITY"
    CHECK = "CHECK"
    CORPUS = "CORPUS"
    HOLDOUT = "HOLDOUT"
    REVIEW = "REVIEW"
    RECEIPT = "RECEIPT"
    OFFLINE_SUMMARY = "OFFLINE_SUMMARY"
    INSTALLATION = "INSTALLATION"
    RECOVERY = "RECOVERY"
    COST = "COST"


class AuthorityScope(str, Enum):
    EXECUTOR_PILOT = "EXECUTOR_PILOT"
    CORPUS = "CORPUS"
    HOLDOUT = "HOLDOUT"


class Arm(str, Enum):
    CANDIDATE = "CANDIDATE"
    PUBLIC_0_2 = "PUBLIC_0_2"


class GoalState(str, Enum):
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"
    CLEARED = "CLEARED"


class CheckState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BASELINE_ACCEPTED = "BASELINE_ACCEPTED"


class GrantState(str, Enum):
    BOUND_IDLE = "BOUND_IDLE"
    GRANTED = "GRANTED"
    INTENT_RECORDED = "INTENT_RECORDED"
    APPLYING = "APPLYING"
    RECONCILING = "RECONCILING"
    RECEIPTED = "RECEIPTED"
    CLOSED = "CLOSED"
    FAILED_CLOSED = "FAILED_CLOSED"


class AttemptState(str, Enum):
    AVAILABLE = "AVAILABLE"
    CONSUMED = "CONSUMED"
    INFRASTRUCTURE_FAILED = "INFRASTRUCTURE_FAILED"
    SUCCEEDED = "SUCCEEDED"


class InfrastructureTransitionKind(str, Enum):
    STARTED = "STARTED"
    FAILED = "FAILED"
    REPLACED = "REPLACED"
    RECOVERED = "RECOVERED"


class CompletionTag(str, Enum):
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    REFUSED = "REFUSED"


class Decision(str, Enum):
    DISCOVER = "DISCOVER"
    RECONCILE = "RECONCILE"
    IMPLEMENT_BATCH = "IMPLEMENT_BATCH"
    VERIFY = "VERIFY"
    FOCUSED_REVIEW = "FOCUSED_REVIEW"
    EXACT_FINAL = "EXACT_FINAL"
    ASK_USER = "ASK_USER"
    FREEZE_CANDIDATE = "FREEZE_CANDIDATE"
    CLOSE = "CLOSE"
    REFUSE = "REFUSE"


@dataclass(frozen=True)
class RepoPath:
    repository_id: RepositoryId
    path: str

    def __post_init__(self) -> None:
        _require_instance(self.repository_id, RepositoryId, name="RepoPath.repository_id")
        path = self.path
        if not isinstance(path, str) or not path or path.startswith("/") or path.endswith("/"):
            raise SemanticValidationError("RepoPath must be a nonempty root-relative path")
        if "\\" in path or "//" in path:
            raise SemanticValidationError("RepoPath aliases are forbidden")
        parts = path.split("/")
        if any(part in ("", ".", "..") for part in parts):
            raise SemanticValidationError("RepoPath dot or empty segments are forbidden")
        if any(any(ord(character) < 32 for character in part) for part in parts):
            raise SemanticValidationError("RepoPath contains control characters")


@dataclass(frozen=True)
class Marker:
    marker_id: MarkerId

    def __post_init__(self) -> None:
        _require_instance(self.marker_id, MarkerId, name="Marker.marker_id")


@dataclass(frozen=True)
class DigestAnchor:
    kind: str
    digest: Sha256

    def __post_init__(self) -> None:
        _require_identifier(self.kind, name="DigestAnchor.kind")
        _require_instance(self.digest, Sha256, name="DigestAnchor.digest")


@dataclass(frozen=True)
class ReceiptAnchor:
    receipt_kind: ReceiptKind
    digest: Sha256

    def __post_init__(self) -> None:
        _require_instance(self.receipt_kind, ReceiptKind, name="ReceiptAnchor.receipt_kind")
        _require_instance(self.digest, Sha256, name="ReceiptAnchor.digest")


Anchor = RepoPath | Marker | DigestAnchor | ReceiptAnchor


def _semantic_sort_key(value: object) -> tuple[str, str]:
    semantic_identity = getattr(value, "semantic_identity", None)
    if callable(semantic_identity):
        identity = semantic_identity()
        return type(value).__name__, getattr(identity, "value", repr(identity))
    scalar = getattr(value, "value", None)
    if isinstance(scalar, str):
        return type(value).__name__, scalar
    return type(value).__name__, repr(value)


T = TypeVar("T")


def sorted_unique(values: tuple[T, ...], *, name: str, maximum: int | None = None) -> tuple[T, ...]:
    if not isinstance(values, tuple):
        raise SemanticValidationError(f"{name} must be an immutable tuple")
    if maximum is not None and len(values) > maximum:
        raise CapacityError(limit=maximum, actual=len(values))
    ordered = tuple(sorted(values, key=_semantic_sort_key))
    keys = tuple(_semantic_sort_key(value) for value in ordered)
    if len(keys) != len(set(keys)):
        raise SemanticValidationError(f"duplicate canonical identity in {name}")
    return ordered


def _freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return freeze_mapping(value)
    if isinstance(value, tuple):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, (list, set, bytearray)):
        raise SemanticValidationError("mutable values cannot inhabit a frozen mapping")
    return value


def freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SemanticValidationError("mapping input required")
    if any(not isinstance(key, str) for key in value):
        raise SemanticValidationError("mapping keys must be strings")
    normalized: dict[str, Any] = {}
    for key in sorted(value):
        normalized[key] = _freeze_value(value[key])
    return MappingProxyType(normalized)


def _reject_authority_evidence(values: tuple[EvidenceRef, ...], *, name: str) -> None:
    if any(evidence.kind is EvidenceKind.AUTHORITY for evidence in values):
        raise SemanticValidationError(f"authority receipts are excluded from {name}")


@dataclass(frozen=True)
class EvidenceRef:
    kind: EvidenceKind
    identity: Sha256
    source: EvidenceSourceId

    def __post_init__(self) -> None:
        if not isinstance(self.kind, EvidenceKind):
            raise SemanticValidationError("EvidenceRef.kind must be an EvidenceKind")
        _require_instance(self.identity, Sha256, name="EvidenceRef.identity")
        _require_instance(self.source, EvidenceSourceId, name="EvidenceRef.source")


@dataclass(frozen=True)
class SourceIdentity:
    commit: GitCommit
    tree: GitTree
    package_semantic: Sha256
    package_artifact: Sha256
    engine_manifest: Sha256
    config: Sha256

    def __post_init__(self) -> None:
        _require_instance(self.commit, GitCommit, name="SourceIdentity.commit")
        _require_instance(self.tree, GitTree, name="SourceIdentity.tree")
        for name in ("package_semantic", "package_artifact", "engine_manifest", "config"):
            _require_instance(getattr(self, name), Sha256, name=f"SourceIdentity.{name}")


@dataclass(frozen=True)
class CandidateIdentity:
    commit: GitCommit
    tree: GitTree
    package_semantic: Sha256
    package_artifact: Sha256
    engine_manifest: Sha256
    config: Sha256
    snapshot: Sha256

    def __post_init__(self) -> None:
        _require_instance(self.commit, GitCommit, name="CandidateIdentity.commit")
        _require_instance(self.tree, GitTree, name="CandidateIdentity.tree")
        for name in (
            "package_semantic",
            "package_artifact",
            "engine_manifest",
            "config",
            "snapshot",
        ):
            _require_instance(getattr(self, name), Sha256, name=f"CandidateIdentity.{name}")


@dataclass(frozen=True)
class ExecutorIdentity:
    provider: str
    session: str
    thread: str
    owner: str
    role_config: Sha256
    actual_profile: Sha256
    permission_profile: Sha256
    write_scope: Sha256

    def __post_init__(self) -> None:
        for name in ("provider", "session", "thread", "owner"):
            _require_text(getattr(self, name), name=f"ExecutorIdentity.{name}")
        for name in ("role_config", "actual_profile", "permission_profile", "write_scope"):
            _require_instance(getattr(self, name), Sha256, name=f"ExecutorIdentity.{name}")


@dataclass(frozen=True)
class InvocationProfileIdentity:
    provider: str
    binary: Sha256
    model: str
    effort: str
    timeout_seconds: int
    tool_surface: Sha256
    network: bool
    mcp: Sha256
    hooks: Sha256
    settings: Sha256

    def __post_init__(self) -> None:
        _require_text(self.provider, name="InvocationProfileIdentity.provider")
        _require_text(self.model, name="InvocationProfileIdentity.model")
        _require_text(self.effort, name="InvocationProfileIdentity.effort")
        _require_exact_int(self.timeout_seconds, name="timeout_seconds", minimum=1)
        _require_exact_bool(self.network, name="network")
        for name in ("binary", "tool_surface", "mcp", "hooks", "settings"):
            _require_instance(getattr(self, name), Sha256, name=f"InvocationProfileIdentity.{name}")


@dataclass(frozen=True)
class ResourceClaim:
    resource_id: ResourceId
    owner_token_digest: Sha256

    def __post_init__(self) -> None:
        _require_instance(self.resource_id, ResourceId, name="ResourceClaim.resource_id")
        _require_instance(self.owner_token_digest, Sha256, name="ResourceClaim.owner_token_digest")


@dataclass(frozen=True)
class ClaimFact:
    claim_id: ClaimId
    claim_type: str
    state: ClaimState
    anchors: tuple[Anchor, ...]
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        _require_instance(self.claim_id, ClaimId, name="ClaimFact.claim_id")
        _require_identifier(self.claim_type, name="ClaimFact.claim_type")
        if not isinstance(self.state, ClaimState):
            raise SemanticValidationError("ClaimFact.state must be a ClaimState")
        _require_tuple_instances(self.anchors, (RepoPath, Marker, DigestAnchor, ReceiptAnchor), name="ClaimFact.anchors")
        _require_tuple_instances(self.evidence, EvidenceRef, name="ClaimFact.evidence")
        _reject_authority_evidence(self.evidence, name="ClaimFact.evidence")
        object.__setattr__(self, "anchors", sorted_unique(self.anchors, name="ClaimFact.anchors"))
        object.__setattr__(self, "evidence", sorted_unique(self.evidence, name="ClaimFact.evidence"))


@dataclass(frozen=True)
class GoalFact:
    state: GoalState
    objective: Sha256 | None
    outcome_match: bool

    def __post_init__(self) -> None:
        if not isinstance(self.state, GoalState):
            raise SemanticValidationError("GoalFact.state must be a GoalState")
        if self.objective is not None:
            _require_instance(self.objective, Sha256, name="GoalFact.objective")
        _require_exact_bool(self.outcome_match, name="GoalFact.outcome_match")
        if self.state is GoalState.NONE and self.objective is not None:
            raise SemanticValidationError("GoalState.NONE cannot carry an objective")


@dataclass(frozen=True)
class GateFact:
    gate_id: GateId
    state: GateState
    work_id: GateWorkId | None
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.gate_id, GateId) or not isinstance(self.state, GateState):
            raise SemanticValidationError("GateFact requires exact gate enums")
        if self.work_id is not None:
            _require_instance(self.work_id, GateWorkId, name="GateFact.work_id")
        _require_tuple_instances(self.evidence, EvidenceRef, name="GateFact.evidence")
        _reject_authority_evidence(self.evidence, name="GateFact.evidence")
        object.__setattr__(self, "evidence", sorted_unique(self.evidence, name="GateFact.evidence"))


@dataclass(frozen=True)
class CheckFact:
    check_id: CheckId
    command_digest: Sha256
    state: CheckState
    candidate_identity: Sha256 | None
    receipt: EvidenceRef

    def __post_init__(self) -> None:
        _require_instance(self.check_id, CheckId, name="CheckFact.check_id")
        _require_instance(self.command_digest, Sha256, name="CheckFact.command_digest")
        if not isinstance(self.state, CheckState):
            raise SemanticValidationError("CheckFact.state must be a CheckState")
        if self.candidate_identity is not None:
            _require_instance(self.candidate_identity, Sha256, name="CheckFact.candidate_identity")
        _require_instance(self.receipt, EvidenceRef, name="CheckFact.receipt")
        _reject_authority_evidence((self.receipt,), name="CheckFact.receipt")


@dataclass(frozen=True)
class InfrastructureTransition:
    kind: InfrastructureTransitionKind
    infrastructure_id: InfrastructureId
    prior_envelope: Sha256
    new_envelope: Sha256
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.kind, InfrastructureTransitionKind):
            raise SemanticValidationError("InfrastructureTransition.kind is invalid")
        _require_instance(self.infrastructure_id, InfrastructureId, name="InfrastructureTransition.infrastructure_id")
        _require_instance(self.prior_envelope, Sha256, name="InfrastructureTransition.prior_envelope")
        _require_instance(self.new_envelope, Sha256, name="InfrastructureTransition.new_envelope")
        _require_tuple_instances(self.evidence, EvidenceRef, name="InfrastructureTransition.evidence")
        _reject_authority_evidence(
            self.evidence,
            name="InfrastructureTransition.evidence",
        )
        if self.prior_envelope == self.new_envelope:
            raise SemanticValidationError("infrastructure replacement must change envelope")
        object.__setattr__(self, "evidence", sorted_unique(self.evidence, name="InfrastructureTransition.evidence"))


@dataclass(frozen=True)
class ResolutionEvidence:
    evidence: EvidenceRef

    def __post_init__(self) -> None:
        _require_instance(self.evidence, EvidenceRef, name="ResolutionEvidence.evidence")
        if self.evidence.kind is EvidenceKind.AUTHORITY:
            raise SemanticValidationError("machine resolution evidence cannot be authority")


@dataclass(frozen=True)
class BaselineAcceptance:
    authority: EvidenceRef
    baseline: Sha256

    def __post_init__(self) -> None:
        _require_instance(self.authority, EvidenceRef, name="BaselineAcceptance.authority")
        _require_instance(self.baseline, Sha256, name="BaselineAcceptance.baseline")
        if self.authority.kind is not EvidenceKind.AUTHORITY:
            raise SemanticValidationError("baseline acceptance requires authority evidence")


@dataclass(frozen=True)
class Finding:
    finding_id: FindingId
    claim_id: ClaimId
    falsifier_id: FalsifierId
    status: FindingStatus
    anchors: tuple[Anchor, ...]
    claim_text: SafeText
    falsifier_text: SafeText
    evidence: tuple[EvidenceRef, ...]
    resolution: ResolutionEvidence | None = field(default=None, repr=False, compare=False)
    baseline_acceptance: BaselineAcceptance | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        _require_instance(self.finding_id, FindingId, name="Finding.finding_id")
        _require_instance(self.claim_id, ClaimId, name="Finding.claim_id")
        _require_instance(self.falsifier_id, FalsifierId, name="Finding.falsifier_id")
        if not isinstance(self.status, FindingStatus):
            raise SemanticValidationError("Finding.status must be a FindingStatus")
        _require_tuple_instances(self.anchors, (RepoPath, Marker, DigestAnchor, ReceiptAnchor), name="Finding.anchors")
        _require_instance(self.claim_text, SafeText, name="Finding.claim_text")
        _require_instance(self.falsifier_text, SafeText, name="Finding.falsifier_text")
        _require_tuple_instances(self.evidence, EvidenceRef, name="Finding.evidence")
        _reject_authority_evidence(self.evidence, name="Finding.evidence")
        anchors = sorted_unique(self.anchors, name="Finding.anchors")
        evidence = sorted_unique(self.evidence, name="Finding.evidence")
        if not anchors:
            raise SemanticValidationError("Finding.anchors must be nonempty")
        object.__setattr__(self, "anchors", anchors)
        object.__setattr__(self, "evidence", evidence)
        if self.status in (FindingStatus.OPEN, FindingStatus.UNKNOWN):
            if self.resolution is not None or self.baseline_acceptance is not None:
                raise SemanticValidationError("open findings cannot carry resolution proof")
        elif self.status is FindingStatus.RESOLVED:
            if self.resolution is None or self.baseline_acceptance is not None:
                raise SemanticValidationError("RESOLVED requires exact machine evidence")
            if self.resolution.evidence not in evidence:
                raise SemanticValidationError(
                    "RESOLVED evidence must include the exact ResolutionEvidence"
                )
        elif self.status is FindingStatus.BASELINE_ACCEPTED:
            if self.baseline_acceptance is None or self.resolution is not None:
                raise SemanticValidationError("BASELINE_ACCEPTED requires exact user authority")
            baseline_anchors = tuple(
                anchor
                for anchor in anchors
                if isinstance(anchor, DigestAnchor) and anchor.kind == "baseline"
            )
            if (
                len(baseline_anchors) != 1
                or baseline_anchors[0].digest != self.baseline_acceptance.baseline
            ):
                raise SemanticValidationError(
                    "BASELINE_ACCEPTED requires one exact matching baseline DigestAnchor"
                )

    @classmethod
    def proposed(
        cls,
        *,
        finding_id: FindingId,
        claim_id: ClaimId,
        falsifier_id: FalsifierId,
        status: FindingStatus,
        anchors: tuple[Anchor, ...],
        claim_text: SafeText,
        falsifier_text: SafeText,
        evidence: tuple[EvidenceRef, ...],
    ) -> Finding:
        if status not in (FindingStatus.OPEN, FindingStatus.UNKNOWN):
            raise SemanticValidationError("model proposals may only be OPEN or UNKNOWN")
        return cls(
            finding_id,
            claim_id,
            falsifier_id,
            status,
            anchors,
            claim_text,
            falsifier_text,
            evidence,
        )

    @classmethod
    def resolved(
        cls,
        *,
        finding_id: FindingId,
        claim_id: ClaimId,
        falsifier_id: FalsifierId,
        anchors: tuple[Anchor, ...],
        claim_text: SafeText,
        falsifier_text: SafeText,
        evidence: tuple[EvidenceRef, ...],
        resolution: ResolutionEvidence,
    ) -> Finding:
        return cls(
            finding_id,
            claim_id,
            falsifier_id,
            FindingStatus.RESOLVED,
            anchors,
            claim_text,
            falsifier_text,
            evidence,
            resolution=resolution,
        )

    @classmethod
    def baseline_accepted(
        cls,
        *,
        finding_id: FindingId,
        claim_id: ClaimId,
        falsifier_id: FalsifierId,
        anchors: tuple[Anchor, ...],
        claim_text: SafeText,
        falsifier_text: SafeText,
        evidence: tuple[EvidenceRef, ...],
        acceptance: BaselineAcceptance,
    ) -> Finding:
        return cls(
            finding_id,
            claim_id,
            falsifier_id,
            FindingStatus.BASELINE_ACCEPTED,
            anchors,
            claim_text,
            falsifier_text,
            evidence,
            baseline_acceptance=acceptance,
        )

    def semantic_value(self) -> Mapping[str, Any]:
        return freeze_mapping(
            {
                "finding_id": self.finding_id,
                "claim_id": self.claim_id,
                "falsifier_id": self.falsifier_id,
                "status": self.status,
                "anchors": self.anchors,
                "evidence": self.evidence,
            }
        )

    def semantic_identity(self) -> Sha256:
        from .canonical import canonical_sha256

        return canonical_sha256("happycodex/0.6/finding", self.semantic_value())


@dataclass(frozen=True)
class FindingCatalog:
    namespace: str
    existing_finding_ids: tuple[FindingId, ...]
    claim_ids: tuple[ClaimId, ...]
    falsifier_ids: tuple[FalsifierId, ...]

    def __post_init__(self) -> None:
        _require_identifier(self.namespace, name="FindingCatalog.namespace")
        _require_tuple_instances(self.existing_finding_ids, FindingId, name="existing_finding_ids")
        _require_tuple_instances(self.claim_ids, ClaimId, name="claim_ids")
        _require_tuple_instances(self.falsifier_ids, FalsifierId, name="falsifier_ids")
        object.__setattr__(self, "existing_finding_ids", sorted_unique(self.existing_finding_ids, name="existing_finding_ids"))
        object.__setattr__(self, "claim_ids", sorted_unique(self.claim_ids, name="claim_ids"))
        object.__setattr__(self, "falsifier_ids", sorted_unique(self.falsifier_ids, name="falsifier_ids"))


@dataclass(frozen=True)
class ModelObservation:
    observations: tuple[SafeText, ...]
    proposed_findings: tuple[Finding, ...]

    def __post_init__(self) -> None:
        _require_tuple_instances(self.observations, SafeText, name="observations")
        _require_tuple_instances(self.proposed_findings, Finding, name="proposed_findings")
        proposed = sorted_unique(self.proposed_findings, name="proposed_findings", maximum=64)
        if any(finding.status not in (FindingStatus.OPEN, FindingStatus.UNKNOWN) for finding in proposed):
            raise SemanticValidationError("model proposals may only be OPEN or UNKNOWN")
        object.__setattr__(self, "proposed_findings", proposed)


@dataclass(frozen=True)
class ControlBlocker:
    blocker_code: str
    gate_id: GateId | None
    finding_id: FindingId | None
    anchors: tuple[Anchor, ...]

    def __post_init__(self) -> None:
        _require_identifier(self.blocker_code, name="ControlBlocker.blocker_code")
        if self.gate_id is not None:
            _require_instance(self.gate_id, GateId, name="ControlBlocker.gate_id")
        if self.finding_id is not None:
            _require_instance(self.finding_id, FindingId, name="ControlBlocker.finding_id")
        _require_tuple_instances(self.anchors, (RepoPath, Marker, DigestAnchor, ReceiptAnchor), name="ControlBlocker.anchors")
        object.__setattr__(self, "anchors", sorted_unique(self.anchors, name="ControlBlocker.anchors"))


@dataclass(frozen=True)
class DecisionTarget:
    decision: Decision
    target: DecisionTargetId
    scope: AttemptScope

    def __post_init__(self) -> None:
        if not isinstance(self.decision, Decision):
            raise SemanticValidationError("DecisionTarget.decision must be exact")
        _require_instance(self.target, DecisionTargetId, name="DecisionTarget.target")
        _require_instance(self.scope, AttemptScope, name="DecisionTarget.scope")


@dataclass(frozen=True)
class StateProjection:
    schema_generation: int
    source: SourceIdentity
    candidate: CandidateIdentity | None
    executor: ExecutorIdentity
    invocation_profile: InvocationProfileIdentity
    claimed_resources: tuple[ResourceClaim, ...]
    claims: tuple[ClaimFact, ...]
    goal: GoalFact
    gates: tuple[GateFact, ...]
    checks: tuple[CheckFact, ...]
    accepted_evidence: tuple[EvidenceRef, ...]
    infrastructure_replacements: tuple[InfrastructureTransition, ...]
    findings: tuple[Finding, ...]
    blockers: tuple[ControlBlocker, ...]
    decision_target: DecisionTarget

    def __post_init__(self) -> None:
        if _require_exact_int(self.schema_generation, name="schema_generation", minimum=0) != 6:
            raise SemanticValidationError("schema_generation must be exactly 6")
        _require_instance(self.source, SourceIdentity, name="StateProjection.source")
        if self.candidate is not None:
            _require_instance(self.candidate, CandidateIdentity, name="StateProjection.candidate")
        _require_instance(self.executor, ExecutorIdentity, name="StateProjection.executor")
        _require_instance(self.invocation_profile, InvocationProfileIdentity, name="StateProjection.invocation_profile")
        _require_instance(self.goal, GoalFact, name="StateProjection.goal")
        _require_instance(self.decision_target, DecisionTarget, name="StateProjection.decision_target")
        typed_collections = (
            ("claimed_resources", ResourceClaim),
            ("claims", ClaimFact),
            ("gates", GateFact),
            ("checks", CheckFact),
            ("accepted_evidence", EvidenceRef),
            ("infrastructure_replacements", InfrastructureTransition),
            ("findings", Finding),
            ("blockers", ControlBlocker),
        )
        for name, expected in typed_collections:
            _require_tuple_instances(getattr(self, name), expected, name=f"StateProjection.{name}")
        for name in (
            "claimed_resources",
            "claims",
            "gates",
            "checks",
            "accepted_evidence",
            "findings",
            "blockers",
        ):
            object.__setattr__(self, name, sorted_unique(getattr(self, name), name=f"StateProjection.{name}", maximum=4096))
        if any(evidence.kind is EvidenceKind.AUTHORITY for evidence in self.accepted_evidence):
            raise SemanticValidationError("authority receipts are excluded from accepted semantic evidence")
        if not isinstance(self.infrastructure_replacements, tuple):
            raise SemanticValidationError("infrastructure_replacements must be an immutable tuple")
        if any(item.kind is not InfrastructureTransitionKind.REPLACED for item in self.infrastructure_replacements):
            raise SemanticValidationError("StateProjection accepts only REPLACED infrastructure facts")

    def semantic_value(self) -> Mapping[str, Any]:
        return freeze_mapping(
            {
                "schema_generation": self.schema_generation,
                "source": self.source,
                "candidate": self.candidate,
                "executor": self.executor,
                "invocation_profile": self.invocation_profile,
                "claimed_resources": self.claimed_resources,
                "claims": self.claims,
                "goal": self.goal,
                "gates": self.gates,
                "checks": self.checks,
                "accepted_evidence": self.accepted_evidence,
                "infrastructure_replacements": self.infrastructure_replacements,
                "findings": tuple(finding.semantic_value() for finding in self.findings),
                "blockers": self.blockers,
                "decision_target": self.decision_target,
            }
        )


@dataclass(frozen=True)
class AdminFacts:
    authority_receipts: tuple[Sha256, ...] = ()
    approval_receipts: tuple[Sha256, ...] = ()
    grant_lifecycle: tuple[str, ...] = ()
    receipt_lifecycle: tuple[str, ...] = ()
    receipt_head: ReceiptLinkHash | None = None
    cursor: str | None = None
    consumed_attempts: tuple[AttemptKey, ...] = ()
    timestamps: tuple[str, ...] = ()
    turn_ids: tuple[str, ...] = ()
    random_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "authority_receipts",
            "approval_receipts",
            "grant_lifecycle",
            "receipt_lifecycle",
            "consumed_attempts",
            "timestamps",
            "turn_ids",
            "random_ids",
        ):
            if not isinstance(getattr(self, name), tuple):
                raise SemanticValidationError(f"AdminFacts.{name} must be an immutable tuple")
        _require_tuple_instances(self.authority_receipts, Sha256, name="AdminFacts.authority_receipts")
        _require_tuple_instances(self.approval_receipts, Sha256, name="AdminFacts.approval_receipts")
        _require_tuple_instances(self.consumed_attempts, AttemptKey, name="AdminFacts.consumed_attempts")
        for name in ("grant_lifecycle", "receipt_lifecycle", "timestamps", "turn_ids", "random_ids"):
            _require_tuple_instances(getattr(self, name), str, name=f"AdminFacts.{name}")
        if self.receipt_head is not None:
            _require_instance(self.receipt_head, ReceiptLinkHash, name="AdminFacts.receipt_head")
        if self.cursor is not None:
            _require_text(self.cursor, name="AdminFacts.cursor", maximum=1024)


@dataclass(frozen=True)
class MachineEnvelope:
    projection: StateProjection
    admin: AdminFacts

    def __post_init__(self) -> None:
        _require_instance(self.projection, StateProjection, name="MachineEnvelope.projection")
        _require_instance(self.admin, AdminFacts, name="MachineEnvelope.admin")


@dataclass(frozen=True)
class ReceiptLink:
    sequence: int
    previous_hash: ReceiptLinkHash | None
    report_hash: Sha256
    attempt_key: AttemptKey
    evidence_kind: EvidenceKind

    def __post_init__(self) -> None:
        sequence = _require_exact_int(self.sequence, name="ReceiptLink.sequence", minimum=0)
        if (sequence == 0) != (self.previous_hash is None):
            raise SemanticValidationError("previous_hash is absent exactly at sequence zero")
        if self.previous_hash is not None:
            _require_instance(self.previous_hash, ReceiptLinkHash, name="ReceiptLink.previous_hash")
        _require_instance(self.report_hash, Sha256, name="ReceiptLink.report_hash")
        _require_instance(self.attempt_key, AttemptKey, name="ReceiptLink.attempt_key")
        if not isinstance(self.evidence_kind, EvidenceKind):
            raise SemanticValidationError("ReceiptLink.evidence_kind must be exact")


__all__ = (
    "AdminFacts",
    "Anchor",
    "Arm",
    "AttemptKey",
    "AttemptScope",
    "AttemptState",
    "AttemptTarget",
    "AuthorityScope",
    "BaselineAcceptance",
    "CandidateIdentity",
    "CapacityError",
    "CheckFact",
    "CheckId",
    "CheckState",
    "ClaimFact",
    "ClaimId",
    "ClaimState",
    "CompletionTag",
    "ControlBlocker",
    "Decision",
    "DecisionTarget",
    "DecisionTargetId",
    "DigestAnchor",
    "EvidenceKind",
    "EvidenceRef",
    "EvidenceSourceId",
    "ExecutorIdentity",
    "FalsifierId",
    "Finding",
    "FindingCatalog",
    "FindingId",
    "FindingStatus",
    "GateFact",
    "GateId",
    "GateState",
    "GateWorkId",
    "GitCommit",
    "GitTree",
    "GoalFact",
    "GoalState",
    "GrantState",
    "InfrastructureId",
    "InfrastructureTransition",
    "InfrastructureTransitionKind",
    "InvocationProfileIdentity",
    "MachineEnvelope",
    "Marker",
    "MarkerId",
    "ModelObservation",
    "ReceiptAnchor",
    "ReceiptKind",
    "ReceiptLink",
    "ReceiptLinkHash",
    "RepoPath",
    "RepositoryId",
    "ResolutionEvidence",
    "ResourceClaim",
    "ResourceId",
    "SafeText",
    "SemanticValidationError",
    "Sha256",
    "SourceIdentity",
    "StateKey",
    "StateProjection",
    "freeze_mapping",
    "sorted_unique",
)
