from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from types import MappingProxyType
from typing import Any, Callable

from evaluation.core.identity import canonical_sha256
from evaluation.core.impact import build_snapshot, impact_token, plan_impact
from evaluation.core.ledger import load_ledger
from evaluation.semantic import EffectDecision, Id, enforce_effect


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "evaluation" / "results" / "current.json"
_BINDING_FIELDS = {
    "task_id",
    "root_task_id",
    "executor_task_id",
    "owner_label",
    "destination_id",
    "lineage_digest",
    "role_config_digest",
    "repository_digest",
    "outcome_digest",
    "message_id",
    "turn_id",
    "content_digest",
    "session_id",
    "thread_id",
    "permission_digest",
    "claim_digest",
}
_DIGEST_FIELDS = {
    "lineage_digest",
    "role_config_digest",
    "repository_digest",
    "outcome_digest",
    "content_digest",
    "permission_digest",
    "claim_digest",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CLAIM_KEY = re.compile(r"^[a-z]+-[0-9a-f]{64}$")
_HOST_SEAL = object()
_CAPABILITY_SEAL = object()


def _validate_binding(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != _BINDING_FIELDS:
        raise ValueError("capability binding is invalid")
    for field, item in value.items():
        if type(item) is not str or not item:
            raise ValueError(f"capability binding field is invalid: {field}")
        if field in _DIGEST_FIELDS and _SHA256.fullmatch(item) is None:
            raise ValueError(f"capability binding digest is invalid: {field}")
    return dict(value)


class _TrustedHostContext:
    __slots__ = ("authority", "binding", "_seal")

    def __init__(self) -> None:
        raise TypeError("trusted host context is host-issued")

    def __reduce__(self) -> object:
        raise TypeError("trusted host context cannot be serialized")


def _issue_trusted_host_context(authority: object, binding: dict[str, str]) -> object:
    context = object.__new__(_TrustedHostContext)
    context.authority = authority
    context.binding = MappingProxyType(_validate_binding(binding))
    context._seal = _HOST_SEAL
    return context


def _trusted_host_context(report: object, args: object) -> object | None:
    """Private host seam. Standalone CLI intentionally has no positive path."""
    del report, args
    return None


class _GateCapability:
    __slots__ = (
        "_binding",
        "_binding_sha256",
        "_claim_root",
        "_pid",
        "_seal",
        "authority_sha256",
    )

    def __init__(self) -> None:
        raise TypeError("capability is validator-issued")

    def __copy__(self) -> object:
        raise TypeError("capability cannot be copied")

    __deepcopy__ = __copy__

    def __reduce__(self) -> object:
        raise TypeError("capability cannot be serialized")

    def descriptor(self) -> dict[str, object]:
        _rebind_capability(self)
        return {
            "attempt_id": self._binding["claim_digest"],
            "authority_sha256": self.authority_sha256,
            "binding_sha256": self._binding_sha256,
        }


def _authorize_effect(report: object, args: object) -> object:
    context = _trusted_host_context(report, args)
    if (
        type(context) is not _TrustedHostContext
        or getattr(context, "_seal", None) is not _HOST_SEAL
    ):
        raise ValueError("trusted host context is required")
    gate = enforce_effect(report, context.authority)
    if gate.decision is not EffectDecision.ALLOW:
        raise ValueError(f"effect authority refused: {gate.reason}")
    binding = dict(context.binding)
    expected = {
        **dict(report.facts.task.to_value()),
        "message_id": context.authority.message_id.value,
        "turn_id": context.authority.turn_id.value,
        "content_digest": context.authority.content_digest.value,
    }
    if any(binding[field] != value for field, value in expected.items()):
        raise ValueError("capability binding does not match reducer authority")
    capability = object.__new__(_GateCapability)
    capability._binding = MappingProxyType(binding)
    capability._binding_sha256 = canonical_sha256(binding)
    capability._claim_root = None
    capability._pid = os.getpid()
    capability._seal = _CAPABILITY_SEAL
    capability.authority_sha256 = canonical_sha256(
        {
            "message_id": binding["message_id"],
            "turn_id": binding["turn_id"],
            "content_digest": binding["content_digest"],
            "binding_sha256": capability._binding_sha256,
        }
    )
    return capability


def _rebind_capability(
    capability: object, binding: dict[str, str] | None = None
) -> object:
    if (
        type(capability) is not _GateCapability
        or getattr(capability, "_seal", None) is not _CAPABILITY_SEAL
    ):
        raise ValueError("capability is not validator-issued")
    if capability._pid != os.getpid():
        raise ValueError("capability cannot cross a process boundary")
    candidate = dict(capability._binding) if binding is None else _validate_binding(binding)
    if (
        candidate != dict(capability._binding)
        or canonical_sha256(candidate) != capability._binding_sha256
    ):
        raise ValueError("capability binding changed")
    return capability


def _effect_claim_root(repo: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--git-common-dir"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise ValueError("effect claims require a Git repository")
    raw = Path(result.stdout.strip())
    common = raw if raw.is_absolute() else repo / raw
    root = common.resolve() / "happycodex" / "effect-claims" / "v6"
    try:
        mode = root.lstat().st_mode
    except FileNotFoundError as exc:
        raise ValueError("effect claim namespace must be prepared by the host") from exc
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode) or stat.S_IMODE(mode) != 0o700:
        raise ValueError("effect claim namespace must be a private real directory")
    return root


def _claim_file(root: Path, key: str, payload: dict[str, object]) -> Path:
    if _CLAIM_KEY.fullmatch(key) is None:
        raise ValueError("invalid effect claim key")
    mode = root.lstat().st_mode
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode) or stat.S_IMODE(mode) != 0o700:
        raise ValueError("invalid effect claim namespace")
    path = root / key
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return path


@dataclass(frozen=True)
class _ClaimRequest:
    repo: Path
    authority_digest: str
    attempt_key: Id
    resource_digests: tuple[str, ...]
    output_digest: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.repo, Path)
            or type(self.attempt_key) is not Id
            or self.attempt_key.tag != "attempt_key"
        ):
            raise ValueError("invalid effect claim request")
        digests = (
            self.authority_digest,
            self.attempt_key.value,
            *self.resource_digests,
            self.output_digest,
        )
        if any(type(item) is not str or _SHA256.fullmatch(item) is None for item in digests):
            raise ValueError("invalid effect claim digest")
        if len(set(self.resource_digests)) != len(self.resource_digests):
            raise ValueError("duplicate resource claim")


def _consume_effect_claims(
    capability: object, request: _ClaimRequest, effect: Callable[[], Any]
) -> Any:
    _rebind_capability(capability)
    root = _effect_claim_root(request.repo)
    claims = [
        ("authority", request.authority_digest),
        ("attempt", request.attempt_key.value),
        *(("resource", digest) for digest in sorted(request.resource_digests)),
        ("output", request.output_digest),
    ]
    for kind, digest in claims:
        _claim_file(
            root,
            f"{kind}-{digest}",
            {"schema_version": 1, "kind": kind, "digest": digest},
        )
    if capability._claim_root is not None:
        raise ValueError("capability already consumed an effect claim set")
    capability._claim_root = root
    _rebind_capability(capability)
    return effect()


def _run_model_phase(
    capability: object, phase_digest: str, invoke: Callable[[], Any]
) -> Any:
    _rebind_capability(capability)
    claim_root = capability._claim_root
    if not isinstance(claim_root, Path):
        raise ValueError("model phase requires consumed effect claims")
    if _SHA256.fullmatch(phase_digest) is None:
        raise ValueError("invalid phase claim digest")
    _claim_file(
        claim_root,
        f"phase-{phase_digest}",
        {"schema_version": 1, "kind": "phase", "digest": phase_digest},
    )
    _rebind_capability(capability)
    return invoke()
def load_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    ledger = load_ledger(LEDGER_PATH)
    settings = ledger["snapshot"]["settings"]
    current = build_snapshot(
        ROOT,
        model=settings["model"],
        effort=settings["effort"],
        timeout=settings["timeout_seconds"],
    )
    return ledger, current, plan_impact(
        ledger["snapshot"], current, pending=ledger["pending"]
    )
