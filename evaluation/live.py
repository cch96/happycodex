from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import threading
from types import MappingProxyType
from typing import Any

from evaluation.core.identity import canonical_sha256
from evaluation.core.impact import (
    build_snapshot,
    impact_token,
    plan_impact,
    validate_gate_plan,
)
from evaluation.core.ledger import derive_pending, load_ledger
from evaluation.semantic import EffectDecision, enforce_effect, make_attempt_key


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
_SPENT_PHASES: set[object] = set()
_SPENT_PHASE_LOCK = threading.Lock()


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
    __slots__ = ("authority", "authority_record", "binding", "plan", "_seal")

    def __init__(self) -> None:
        raise TypeError("trusted host context is host-issued")

    def __reduce__(self) -> object:
        raise TypeError("trusted host context cannot be serialized")


def _issue_trusted_host_context(
    authority: object,
    binding: dict[str, str],
    persisted_plan: dict[str, Any],
    persisted_authority: dict[str, Any],
) -> object:
    authority_record = dict(persisted_authority)
    expected = canonical_sha256({
        key: value for key, value in authority_record.items()
        if key != "authority_sha256"
    })
    if authority_record.get("authority_sha256") != expected:
        raise ValueError("persisted authority is invalid")
    context = object.__new__(_TrustedHostContext)
    context.authority = authority
    context.authority_record = MappingProxyType(authority_record)
    context.binding = MappingProxyType(_validate_binding(binding))
    context.plan = MappingProxyType({
        **validate_gate_plan(persisted_plan),
        "authority_sha256": expected,
    })
    context._seal = _HOST_SEAL
    return context


def _trusted_host_context(report: object, args: object) -> object | None:
    """Private host seam. Standalone CLI intentionally has no positive path."""
    return None


class _Sealed:
    def __init__(self) -> None:
        raise TypeError("capability is validator-issued")

    def __copy__(self) -> object:
        raise TypeError("capability cannot be copied")

    __deepcopy__ = __copy__

    def __reduce__(self) -> object:
        raise TypeError("capability cannot be serialized")


def _require_issued(value: object, expected: type, message: str) -> object:
    if type(value) is not expected or getattr(value, "_seal", None) is not _CAPABILITY_SEAL:
        raise ValueError(message)
    return value


class _GateCapability(_Sealed):
    __slots__ = (
        "_binding",
        "_binding_sha256",
        "_plan",
        "_pid",
        "_seal",
        "_attempt_key",
        "_authority",
        "_report",
        "authority_sha256",
    )

    def descriptor(self) -> dict[str, object]:
        _rebind_capability(self)
        return {
            "attempt_id": self._attempt_key,
            "authority_sha256": self.authority_sha256,
            "binding_sha256": self._binding_sha256,
            "gate": self._plan["gate"],
            "invocation_sha256": self._plan["invocation_sha256"],
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
    if (
        binding["permission_digest"]
        != _permission_digest(report, context.authority, context.plan)
        or binding["claim_digest"] != _claim_digest(context.plan)
    ):
        raise ValueError("persisted permission or claim binding changed")
    record = dict(context.authority_record)
    if (
        record["gate"] != context.plan["gate"]
        or record["phase"] != context.plan["phase"]
        or record["impact_token"] != context.plan["impact_token"]
        or record["invocation_sha256"] != context.plan["invocation_sha256"]
        or record["action"] != context.plan["action"]
        or record["host"]["message_id"] != binding["message_id"]
        or record["host"]["turn_id"] != binding["turn_id"]
        or record["host"]["content_sha256"] != binding["content_digest"]
    ):
        raise ValueError("persisted authority does not match runtime authority")
    capability = object.__new__(_GateCapability)
    capability._binding = MappingProxyType(binding)
    capability._binding_sha256 = canonical_sha256(binding)
    capability._plan = context.plan
    capability._pid = os.getpid()
    capability._seal = _CAPABILITY_SEAL
    capability._attempt_key = make_attempt_key(report).value
    capability._authority, capability._report = context.authority, report
    capability.authority_sha256 = record["authority_sha256"]
    return capability


def _permission_digest(report: object, authority: object, plan: object) -> str:
    return canonical_sha256({
        "next_action": report.to_wire()["next_action"],
        "authority": {
            "message_id": authority.message_id.value,
            "turn_id": authority.turn_id.value,
            "content_digest": authority.content_digest.value,
            "target": authority.target.value,
            "scope": authority.scope.value,
        },
        "action": dict(plan)["action"],
    })


def _claim_digest(plan: object) -> str:
    value = dict(plan)
    return canonical_sha256({
        "action": value["action"],
        "gate": value["gate"],
        "output": value["output"],
        "resource_digests": value["resource_digests"],
        "units": value["units"],
    })


def _rebind_capability(
    capability: object, binding: dict[str, str] | None = None
) -> object:
    _require_issued(capability, _GateCapability, "capability is not validator-issued")
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


def _claim_file(root: Path, key: str) -> None:
    if _CLAIM_KEY.fullmatch(key) is None:
        raise ValueError("invalid effect claim key")
    kind, digest = key.split("-", 1)
    payload = {"schema_version": 1, "kind": kind, "digest": digest}
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


class _ClaimedCapability(_Sealed):
    __slots__ = ("_gate", "_root", "_seal")

    def descriptor(self) -> dict[str, object]:
        _require_claimed(self)
        return self._gate.descriptor()


class _UnitCapability(_Sealed):
    __slots__ = ("_claimed", "_unit", "_seal")


class _PhaseProof(_Sealed):
    __slots__ = ("_unit", "_argv", "_cwd", "_env", "_timeout", "_nonce", "_seal")


class _PreflightCapability(_Sealed):
    __slots__ = ("_gate", "_seal")


def _preflight_effect(
    capability: object,
    *,
    gate: str,
    output: Path,
    units: list[str],
    model: str,
    effort: str,
    timeout_ms: int,
    arm: str,
) -> object:
    value = _rebind_capability(capability)
    plan, profile = value._plan, value._plan["profile"]
    if (
        plan["gate"] != gate
        or plan["output"] != str(output.resolve())
        or plan["units"] != units
        or profile["model"] != model
        or profile["effort"] != effort
        or profile["timeout_ms"] != timeout_ms
        or profile["arm"] != arm
    ):
        raise ValueError("persisted plan or invocation preflight mismatch")
    result = object.__new__(_PreflightCapability)
    result._gate, result._seal = value, _CAPABILITY_SEAL
    return result


def _effect_claim_specs(capability: object) -> list[tuple[str, str]]:
    _require_issued(capability, _PreflightCapability, "preflight capability is required")
    gate = _rebind_capability(capability._gate)
    return [
        ("authority", gate.authority_sha256),
        ("attempt", gate._attempt_key),
        *(("resource", digest) for digest in gate._plan["resource_digests"]),
        ("output", canonical_sha256({"output": gate._plan["output"]})),
    ]


def _claim_effect_set(capability: object) -> object:
    _require_issued(capability, _PreflightCapability, "preflight capability is required")
    gate = _rebind_capability(capability._gate)
    root = _effect_claim_root(Path(gate._plan["repo"]))
    claims = _effect_claim_specs(capability)
    _claim_set(root, claims)
    claimed = object.__new__(_ClaimedCapability)
    claimed._gate, claimed._root, claimed._seal = gate, root, _CAPABILITY_SEAL
    return claimed


def _claim_set(root: Path, claims: list[tuple[str, str]]) -> None:
    directory = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        fcntl.flock(directory, fcntl.LOCK_EX)
        if any((root / f"{kind}-{digest}").exists() for kind, digest in claims):
            raise FileExistsError("effect claim set collides")
        for kind, digest in claims:
            _claim_file(root, f"{kind}-{digest}")
    finally:
        fcntl.flock(directory, fcntl.LOCK_UN)
        os.close(directory)


def _require_claimed(value: object) -> object:
    _require_issued(value, _ClaimedCapability, "claimed capability is required")
    _rebind_capability(value._gate)
    return value


def _claim_unit(claimed: object, unit_id: str) -> object:
    value = _require_claimed(claimed)
    if unit_id not in value._gate._plan["units"]:
        raise ValueError("unit is outside persisted gate plan")
    digest = canonical_sha256({
        "gate": value._gate._plan["gate"],
        "invocation_sha256": value._gate._plan["invocation_sha256"],
        "unit": unit_id,
    })
    _claim_set(value._root, [("unit", digest)])
    unit = object.__new__(_UnitCapability)
    unit._claimed, unit._unit, unit._seal = value, unit_id, _CAPABILITY_SEAL
    return unit


def _claim_units(claimed: object, unit_ids: list[str]) -> dict[str, object]:
    value = _require_claimed(claimed)
    if unit_ids != sorted(set(unit_ids)) or unit_ids != value._gate._plan["units"]:
        raise ValueError("units do not equal persisted gate plan")
    specs = {
        unit: canonical_sha256({
            "gate": value._gate._plan["gate"],
            "invocation_sha256": value._gate._plan["invocation_sha256"],
            "unit": unit,
        }) for unit in unit_ids
    }
    _claim_set(value._root, [("unit", digest) for digest in specs.values()])
    result = {}
    for unit_id in unit_ids:
        unit = object.__new__(_UnitCapability)
        unit._claimed, unit._unit, unit._seal = value, unit_id, _CAPABILITY_SEAL
        result[unit_id] = unit
    return result


def _require_unit_capability(value: object, unit_id: str) -> object:
    _require_issued(value, _UnitCapability, "exact claimed unit capability is required")
    if value._unit != unit_id:
        raise ValueError("exact claimed unit capability is required")
    _require_claimed(value._claimed)
    return value


def _issue_phase_proof(unit: object) -> object:
    value = _require_unit_capability(unit, unit._unit if type(unit) is _UnitCapability else "")
    template = value._claimed._gate._plan["template"]
    argv = [item.replace("{unit}", value._unit) for item in template["argv"]]
    cwd = Path(template["cwd"].replace("{unit}", value._unit)).resolve()
    env = {
        key: item.replace("{unit}", value._unit)
        for key, item in template["env"].items()
    }
    payload = {
        "unit": value._unit,
        "argv": argv,
        "cwd": str(cwd),
        "env": dict(sorted(env.items())),
        "timeout_ms": template["timeout_ms"],
    }
    digest = canonical_sha256(payload)
    _claim_file(value._claimed._root, f"phase-{digest}")
    proof = object.__new__(_PhaseProof)
    proof._unit, proof._argv, proof._cwd = value, tuple(argv), cwd
    proof._env = MappingProxyType(payload["env"])
    proof._timeout = template["timeout_ms"] / 1000
    proof._nonce, proof._seal = object(), _CAPABILITY_SEAL
    return proof


def _consume_phase_proof(value: object) -> tuple[list[str], Path, dict[str, str], int]:
    _require_issued(value, _PhaseProof, "exact PID-bound phase proof is required")
    _require_unit_capability(value._unit, value._unit._unit)
    with _SPENT_PHASE_LOCK:
        if value._nonce in _SPENT_PHASES:
            raise ValueError("phase proof is spent")
        _SPENT_PHASES.add(value._nonce)
    return list(value._argv), value._cwd, dict(value._env), value._timeout
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
        ledger["snapshot"], current, pending=derive_pending(ledger)
    )
