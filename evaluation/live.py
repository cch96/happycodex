from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from evaluation.core.identity import canonical_sha256, sha256_bytes
from evaluation.core.impact import build_snapshot, plan_impact
from evaluation.core.ledger import (
    GATE_ORDER,
    derive_certified,
    derive_coverage,
    derive_failed,
    derive_freeze_eligibility,
    derive_pending,
    derive_receipt_tip,
    derive_status,
    load_ledger,
    validate_gate_plan,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "evaluation" / "results" / "current.json"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_LAUNCH_FIELDS = frozenset(
    {
        "schema_generation",
        "candidate_sha256",
        "snapshot_sha256",
        "plan_sha256",
        "gate",
        "unit",
        "state_key",
        "action",
        "action_key",
        "infrastructure_generation",
        "invocation",
        "cost_ceiling",
        "units",
        "resource_digests",
        "output",
        "approval_content_sha256",
        "launch_key",
    }
)
_ACTION_FIELDS = frozenset(
    {"kind", "target", "scope", "falsifier_id", "evidence_source_id"}
)
_INVOCATION_FIELDS = frozenset(
    {"argv", "cwd", "env", "timeout_ms", "model", "effort", "arm"}
)
_RESULT_FIELDS = frozenset(
    {
        "schema_generation",
        "action_key",
        "launch_key",
        "unit",
        "status",
        "effect",
        "output_sha256",
        "usage",
        "result_sha256",
    }
)
_USAGE_FIELDS = frozenset(
    {
        "model_calls",
        "uncached_input_tokens",
        "output_tokens",
        "wall_milliseconds",
    }
)
_CAPABILITY_SECRET = object()


class _LiveCapability:
    __slots__ = (
        "_secret",
        "candidate_sha256",
        "plan_sha256",
        "gate",
        "approval_content_sha256",
    )

    def __init__(
        self,
        secret: object,
        *,
        candidate_sha256: str,
        plan_sha256: str,
        gate: str,
        approval_content_sha256: str,
    ) -> None:
        if secret is not _CAPABILITY_SECRET:
            raise TypeError("live capability is Host-minted only")
        object.__setattr__(self, "_secret", secret)
        object.__setattr__(self, "candidate_sha256", candidate_sha256)
        object.__setattr__(self, "plan_sha256", plan_sha256)
        object.__setattr__(self, "gate", gate)
        object.__setattr__(
            self,
            "approval_content_sha256",
            approval_content_sha256,
        )

    def __setattr__(self, _name: str, _value: object) -> None:
        raise TypeError("live capability is immutable")

    def __reduce__(self) -> None:
        raise TypeError("live capability cannot be serialized")


def _digest(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise ValueError(f"invalid {label} digest")
    return value


def _real_private_directory(path: Path, label: str) -> Path:
    candidate = path.absolute()
    try:
        mode = candidate.lstat().st_mode
    except FileNotFoundError as exc:
        raise ValueError(f"{label} must already exist") from exc
    if (
        stat.S_ISLNK(mode)
        or not stat.S_ISDIR(mode)
        or stat.S_IMODE(mode) != 0o700
        or candidate.resolve() != candidate
    ):
        raise ValueError(f"{label} must be a private real directory")
    return candidate


def _expand(value: str, unit: str) -> str:
    return value.replace("{unit}", unit)


def _derive_action(
    plan: dict[str, Any],
    unit: str,
    invocation: dict[str, Any],
) -> tuple[str, dict[str, str], str]:
    state_key = canonical_sha256(
        {
            "domain": "happycodex/schema7/gate-state",
            "candidate_sha256": plan["candidate_sha256"],
            "snapshot_sha256": plan["snapshot_sha256"],
            "gate": plan["gate"],
            "unit": unit,
        }
    )
    action = {
        "kind": "RUN_GATE",
        "target": f"{plan['gate']}:{unit}",
        "scope": plan["candidate_sha256"],
        "falsifier_id": canonical_sha256(
            {
                "snapshot_sha256": plan["snapshot_sha256"],
                "gate": plan["gate"],
                "unit": unit,
            }
        ),
        "evidence_source_id": canonical_sha256(
            {
                "profile": invocation,
                "units": plan["units"],
                "resource_digests": plan["resource_digests"],
            }
        ),
    }
    action_key = canonical_sha256(
        {
            "domain": "happycodex/schema7/action-key",
            "state_key": state_key,
            "action": action,
        }
    )
    return state_key, action, action_key


def mint_host_capability(
    plan: dict[str, Any],
    approval_content: str,
) -> _LiveCapability:
    """Mint one process-local capability after Host authenticates the user line."""
    plan = validate_gate_plan(plan)
    if (
        type(approval_content) is not str
        or "\n" in approval_content
        or "\r" in approval_content
        or sha256_bytes((approval_content + "\n").encode())
        != plan["approval_content_sha256"]
    ):
        raise ValueError("approval content does not match GatePlan")
    return _LiveCapability(
        _CAPABILITY_SECRET,
        candidate_sha256=plan["candidate_sha256"],
        plan_sha256=plan["plan_sha256"],
        gate=plan["gate"],
        approval_content_sha256=plan["approval_content_sha256"],
    )


def validate_capability(
    capability: object,
    *,
    plan: dict[str, Any] | None = None,
    launch: dict[str, Any] | None = None,
) -> _LiveCapability:
    if type(capability) is not _LiveCapability or capability._secret is not _CAPABILITY_SECRET:
        raise ValueError("model-reaching work requires a Host capability")
    expected = plan if plan is not None else launch
    if expected is None:
        raise ValueError("capability validation requires a plan or launch")
    fields = (
        "candidate_sha256",
        "plan_sha256",
        "gate",
        "approval_content_sha256",
    )
    if any(getattr(capability, field) != expected[field] for field in fields):
        raise ValueError("Host capability does not bind this exact effect")
    return capability


def model_gate_profile(
    *,
    gate: str,
    repo: Path,
    output: Path,
    claim_root: Path,
    model: str,
    effort: str,
    timeout_ms: int,
    arm: str,
    codex_sha256: str,
    impact_sha256: str,
    public: Path | None = None,
) -> dict[str, Any]:
    """Return the exact canonical Host descriptor for one model gate."""
    if gate not in {"calibration", "corpus", "holdout"}:
        raise ValueError("model gate profile requires a model-reaching gate")
    _digest(codex_sha256, "Codex binary")
    _digest(impact_sha256, "impact receipt")
    repo = repo.resolve()
    output = output.absolute()
    claim_root = claim_root.resolve()
    argv = [
        "happycodex-host:run-authorized-v1",
        "--gate",
        gate,
        "--repository",
        str(repo),
        "--output",
        str(output),
        "--claim-root",
        str(claim_root),
        "--unit",
        "{unit}",
    ]
    if public is not None:
        argv.extend(("--public", str(public.resolve())))
    return {
        "argv": argv,
        "cwd": str(repo),
        "env": {
            "HAPPYCODEX_CLAIM_ROOT": str(claim_root),
            "HAPPYCODEX_CODEX_SHA256": codex_sha256,
            "HAPPYCODEX_IMPACT_SHA256": impact_sha256,
        },
        "timeout_ms": timeout_ms,
        "model": model,
        "effort": effort,
        "arm": arm,
    }


def model_gate_resource_digests(
    *,
    candidate: dict[str, Any],
    snapshot: dict[str, Any],
    profile: dict[str, Any],
    codex: dict[str, str],
    impact_sha256: str,
    public_identity: dict[str, str] | None = None,
) -> list[str]:
    _digest(impact_sha256, "impact receipt")
    resources: list[dict[str, Any]] = [
        {
            "kind": "release_candidate",
            "candidate_sha256": candidate["candidate_sha256"],
        },
        {
            "kind": "candidate_package",
            "artifact_sha256": candidate["package_artifact_sha256"],
            "semantic_sha256": candidate["package_semantic_sha256"],
        },
        {
            "kind": "executor_role",
            "sha256": candidate["executor_role_sha256"],
        },
        {
            "kind": "evaluator_snapshot",
            "sha256": canonical_sha256(snapshot),
        },
        {
            "kind": "codex_binary",
            "version": codex["version"],
            "sha256": codex["sha256"],
        },
        {
            "kind": "host_profile",
            "sha256": canonical_sha256(profile),
        },
        {
            "kind": "impact_receipt",
            "sha256": impact_sha256,
        },
    ]
    if public_identity is not None:
        resources.append({"kind": "public_baseline", **public_identity})
    return sorted(canonical_sha256(resource) for resource in resources)


def validate_model_gate_plan(
    plan: dict[str, Any],
    *,
    candidate: dict[str, Any],
    snapshot: dict[str, Any],
    repo: Path,
    output: Path,
    claim_root: Path,
    model: str,
    effort: str,
    timeout_ms: int,
    arm: str,
    codex: dict[str, str],
    impact_sha256: str,
    public: Path | None = None,
    public_identity: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Bind a persisted plan to the actual Host inputs before any launch."""
    plan = validate_gate_plan(plan)
    _real_private_directory(claim_root, "launch claim root")
    expected_profile = model_gate_profile(
        gate=plan["gate"],
        repo=repo,
        output=output,
        claim_root=claim_root,
        model=model,
        effort=effort,
        timeout_ms=timeout_ms,
        arm=arm,
        codex_sha256=codex["sha256"],
        impact_sha256=impact_sha256,
        public=public,
    )
    expected_resources = model_gate_resource_digests(
        candidate=candidate,
        snapshot=snapshot,
        profile=expected_profile,
        codex=codex,
        impact_sha256=impact_sha256,
        public_identity=public_identity,
    )
    if (
        plan["candidate_sha256"] != candidate["candidate_sha256"]
        or plan["snapshot_sha256"] != canonical_sha256(snapshot)
        or plan["output"] != str(output.absolute())
        or plan["profile"] != expected_profile
        or plan["resource_digests"] != expected_resources
    ):
        raise ValueError("GatePlan does not bind the exact Host invocation")
    return plan


def build_launch(
    plan: dict[str, Any],
    unit: str,
    *,
    infrastructure_generation: str | None = None,
) -> dict[str, Any]:
    """Derive one launch from an exact GatePlan; neither object is authority."""
    plan = validate_gate_plan(plan)
    if unit not in plan["units"]:
        raise ValueError("launch unit is outside GatePlan")
    profile = plan["profile"]
    invocation = {
        "argv": [_expand(item, unit) for item in profile["argv"]],
        "cwd": _expand(profile["cwd"], unit),
        "env": {
            key: _expand(value, unit)
            for key, value in sorted(profile["env"].items())
        },
        "timeout_ms": profile["timeout_ms"],
        "model": profile["model"],
        "effort": profile["effort"],
        "arm": profile["arm"],
    }
    state_key, action, action_key = _derive_action(plan, unit, invocation)
    infrastructure = (
        canonical_sha256(
            {
                "snapshot_sha256": plan["snapshot_sha256"],
                "profile": profile,
            }
        )
        if infrastructure_generation is None
        else infrastructure_generation
    )
    _digest(infrastructure, "launch infrastructure generation")
    output_root = Path(plan["output"]).absolute()
    child = (
        unit
        if infrastructure_generation is None
        else "replacement-"
        + canonical_sha256(
            {"unit": unit, "infrastructure_generation": infrastructure}
        )
    )
    output_path = (output_root / child).absolute()
    if output_path.parent != output_root:
        raise ValueError("launch output must be a direct GatePlan child")
    output = str(output_path)
    payload = {
        "schema_generation": 7,
        "candidate_sha256": plan["candidate_sha256"],
        "snapshot_sha256": plan["snapshot_sha256"],
        "plan_sha256": plan["plan_sha256"],
        "gate": plan["gate"],
        "unit": unit,
        "state_key": state_key,
        "action": action,
        "action_key": action_key,
        "infrastructure_generation": infrastructure,
        "invocation": invocation,
        "cost_ceiling": dict(plan["cost_ceiling"]),
        "units": list(plan["units"]),
        "resource_digests": list(plan["resource_digests"]),
        "output": output,
        "approval_content_sha256": plan["approval_content_sha256"],
    }
    payload["launch_key"] = canonical_sha256(
        {"domain": "happycodex/schema7/launch-key", "launch": payload}
    )
    return validate_launch(payload)


def validate_launch(
    value: Any,
    *,
    plan: dict[str, Any] | None = None,
    unit: str | None = None,
    argv: list[str] | None = None,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout_ms: int | None = None,
    output: Path | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != _LAUNCH_FIELDS:
        raise ValueError("invalid launch fields")
    if value["schema_generation"] != 7:
        raise ValueError("invalid launch schema")
    for field in (
        "candidate_sha256",
        "snapshot_sha256",
        "plan_sha256",
        "approval_content_sha256",
        "state_key",
        "action_key",
        "infrastructure_generation",
        "launch_key",
    ):
        _digest(value[field], f"launch {field}")
    if type(value["gate"]) is not str or value["gate"] not in GATE_ORDER:
        raise ValueError("invalid launch gate")
    if type(value["unit"]) is not str or not value["unit"]:
        raise ValueError("invalid launch unit")
    action = value["action"]
    if (
        not isinstance(action, dict)
        or set(action) != _ACTION_FIELDS
        or action["kind"] != "RUN_GATE"
        or any(type(item) is not str or not item for item in action.values())
    ):
        raise ValueError("invalid reducer-produced launch action")
    for field in ("scope", "falsifier_id", "evidence_source_id"):
        _digest(action[field], f"launch action {field}")
    invocation = value["invocation"]
    if not isinstance(invocation, dict) or set(invocation) != _INVOCATION_FIELDS:
        raise ValueError("invalid launch invocation")
    if (
        not isinstance(invocation["argv"], list)
        or not invocation["argv"]
        or any(type(item) is not str or not item for item in invocation["argv"])
        or type(invocation["cwd"]) is not str
        or not Path(invocation["cwd"]).is_absolute()
        or not isinstance(invocation["env"], dict)
        or any(type(key) is not str or type(item) is not str
               for key, item in invocation["env"].items())
        or type(invocation["timeout_ms"]) is not int
        or invocation["timeout_ms"] <= 0
    ):
        raise ValueError("invalid launch invocation")
    if (
        not isinstance(value["cost_ceiling"], dict)
        or set(value["cost_ceiling"]) != _USAGE_FIELDS
        or any(type(item) is not int or item < 0
               for item in value["cost_ceiling"].values())
    ):
        raise ValueError("invalid launch cost ceiling")
    if (
        not isinstance(value["units"], list)
        or value["units"] != sorted(set(value["units"]))
        or value["unit"] not in value["units"]
        or not isinstance(value["resource_digests"], list)
        or value["resource_digests"] != sorted(set(value["resource_digests"]))
    ):
        raise ValueError("invalid launch units or resources")
    for digest in value["resource_digests"]:
        _digest(digest, "launch resource")
    output_path = Path(str(value["output"]))
    if not output_path.is_absolute():
        raise ValueError("launch output must be absolute")
    expected_state = canonical_sha256(
        {
            "domain": "happycodex/schema7/gate-state",
            "candidate_sha256": value["candidate_sha256"],
            "snapshot_sha256": value["snapshot_sha256"],
            "gate": value["gate"],
            "unit": value["unit"],
        }
    )
    expected_action = {
        "kind": "RUN_GATE",
        "target": f"{value['gate']}:{value['unit']}",
        "scope": value["candidate_sha256"],
        "falsifier_id": canonical_sha256(
            {
                "snapshot_sha256": value["snapshot_sha256"],
                "gate": value["gate"],
                "unit": value["unit"],
            }
        ),
        "evidence_source_id": canonical_sha256(
            {
                "profile": value["invocation"],
                "units": value["units"],
                "resource_digests": value["resource_digests"],
            }
        ),
    }
    if value["state_key"] != expected_state or action != expected_action:
        raise ValueError("launch action differs from pure reduction")
    expected_action_key = canonical_sha256(
        {
            "domain": "happycodex/schema7/action-key",
            "state_key": expected_state,
            "action": expected_action,
        }
    )
    if value["action_key"] != expected_action_key:
        raise ValueError("launch ActionKey differs from reducer action")
    payload = dict(value)
    seal = payload.pop("launch_key")
    if seal != canonical_sha256(
        {"domain": "happycodex/schema7/launch-key", "launch": payload}
    ):
        raise ValueError("launch content changed")
    if plan is not None and value != build_launch(
        plan,
        value["unit"],
        infrastructure_generation=value["infrastructure_generation"],
    ):
        raise ValueError("launch does not match GatePlan")
    checks = (
        (unit, value["unit"], "unit"),
        (argv, invocation["argv"], "argv"),
        (str(cwd) if cwd is not None else None, invocation["cwd"], "cwd"),
        (env, invocation["env"], "env"),
        (timeout_ms, invocation["timeout_ms"], "timeout"),
        (str(output) if output is not None else None, value["output"], "output"),
    )
    for expected, actual, label in checks:
        if expected is not None and expected != actual:
            raise ValueError(f"launch {label} drift")
    return value


def _output_preflight(path: Path) -> tuple[Path, Path]:
    output = path.absolute()
    if output != Path(os.path.abspath(output)) or ".." in output.parts:
        raise ValueError("launch output path drift")
    if output.exists() or output.is_symlink():
        raise ValueError("launch output must be absent")
    base = output.parent
    if base.exists():
        _real_private_directory(base, "launch output parent")
        return base, output
    grandparent = _real_private_directory(
        base.parent,
        "launch output grandparent",
    )
    if base.parent != grandparent:
        raise ValueError("launch output parent alias")
    return base, output


def _launch_claim_path(launch: dict[str, Any], root: Path) -> Path:
    return root / (
        f"launch-{launch['action_key']}-{launch['launch_key']}.json"
    )


def _action_claim_path(launch: dict[str, Any], root: Path) -> Path:
    return root / f"action-{launch['action_key']}.json"


def _write_exclusive(path: Path, payload: dict[str, Any]) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        data = (
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            + b"\n"
        )
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _load_claim(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("launch claim is not a real file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("launch claim is malformed")
    return value


def _prior_launches(launch: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    prefix = f"launch-{launch['action_key']}-"
    prior = []
    for path in sorted(root.iterdir()):
        if not path.name.startswith(prefix):
            continue
        claim = _load_claim(path)
        if set(claim) != {
            "schema_generation",
            "action_key",
            "launch_key",
            "infrastructure_generation",
            "unit",
            "output",
        }:
            raise ValueError("launch claim fields are invalid")
        prior.append(claim)
    return prior


def reserve_launch(
    launch: dict[str, Any],
    claim_root: Path,
    *,
    plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Reserve one launch after local preflight without consuming ActionKey."""
    launch = validate_launch(launch, plan=plan)
    root = _real_private_directory(claim_root, "launch claim root")
    base, output = _output_preflight(Path(launch["output"]))
    claim = _launch_claim_path(launch, root)
    lock_path = root / f"lock-{launch['action_key']}"
    lock = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if _action_claim_path(launch, root).exists():
            raise ValueError("ActionKey is already consumed")
        prior = _prior_launches(launch, root)
        if prior:
            if len(prior) != 1:
                raise ValueError("ActionKey replacement launch is exhausted")
            previous = prior[0]
            result_path = Path(previous["output"]) / "result.json"
            result = _load_claim(result_path)
            if (
                result.get("effect") != "no_effect"
                or result.get("action_key") != launch["action_key"]
                or previous["infrastructure_generation"]
                == launch["infrastructure_generation"]
            ):
                raise ValueError("replacement launch lacks a distinct NO_EFFECT proof")
        _write_exclusive(
            claim,
            {
                "schema_generation": 7,
                "action_key": launch["action_key"],
                "launch_key": launch["launch_key"],
                "infrastructure_generation": launch[
                    "infrastructure_generation"
                ],
                "unit": launch["unit"],
                "output": launch["output"],
            },
        )
    finally:
        os.close(lock)
    if not base.exists():
        os.mkdir(base, 0o700)
    descriptor = os.open(
        base,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.mkdir(output.name, 0o700, dir_fd=descriptor)
    except FileExistsError as exc:
        raise ValueError("launch output collision after reservation") from exc
    finally:
        os.close(descriptor)
    return {
        "action_key": launch["action_key"],
        "launch_key": launch["launch_key"],
        "unit": launch["unit"],
        "claim": str(claim),
        "output": str(output),
    }


def consume_action(launch: dict[str, Any], claim_root: Path) -> str:
    """Consume ActionKey immediately before the first provider-reaching call."""
    launch = validate_launch(launch)
    root = _real_private_directory(claim_root, "launch claim root")
    launch_claim = _launch_claim_path(launch, root)
    claim = _load_claim(launch_claim)
    if (
        claim.get("launch_key") != launch["launch_key"]
        or claim.get("action_key") != launch["action_key"]
    ):
        raise ValueError("launch reservation does not bind ActionKey")
    action_claim = _action_claim_path(launch, root)
    _write_exclusive(
        action_claim,
        {
            "schema_generation": 7,
            "action_key": launch["action_key"],
            "launch_key": launch["launch_key"],
            "unit": launch["unit"],
        },
    )
    return str(action_claim)


def validate_consumed_action(
    launch: dict[str, Any],
    claim_root: Path,
) -> dict[str, Any]:
    launch = validate_launch(launch)
    root = _real_private_directory(claim_root, "launch claim root")
    launch_claim = _load_claim(_launch_claim_path(launch, root))
    action_claim = _load_claim(_action_claim_path(launch, root))
    expected = {
        "schema_generation": 7,
        "action_key": launch["action_key"],
        "launch_key": launch["launch_key"],
        "unit": launch["unit"],
    }
    if (
        launch_claim.get("launch_key") != launch["launch_key"]
        or action_claim != expected
    ):
        raise ValueError("provider call lacks its exact consumed ActionKey")
    return action_claim


def action_is_consumed(
    launch: dict[str, Any],
    claim_root: Path,
) -> bool:
    launch = validate_launch(launch)
    root = _real_private_directory(claim_root, "launch claim root")
    path = _action_claim_path(launch, root)
    if path.is_symlink():
        raise ValueError("ActionKey claim is not a real file")
    if not path.exists():
        return False
    validate_consumed_action(launch, root)
    return True


def enter_provider_call(
    launch: dict[str, Any],
    claim_root: Path,
    capability: object,
) -> dict[str, Any]:
    """Consume once at the provider edge; rebind later phases of that launch."""
    launch = validate_launch(launch)
    validate_capability(capability, launch=launch)
    root = _real_private_directory(claim_root, "launch claim root")
    lock_path = root / f"lock-{launch['action_key']}"
    lock = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result_path = Path(launch["output"]) / "result.json"
        if result_path.exists() or result_path.is_symlink():
            raise ValueError("completed launch cannot reach the provider again")
        if action_is_consumed(launch, root):
            return validate_consumed_action(launch, root)
        consume_action(launch, root)
        return validate_consumed_action(launch, root)
    finally:
        os.close(lock)


def _validate_launch_result(
    launch: dict[str, Any],
    root: Path,
    result: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(result, dict) or set(result) != _RESULT_FIELDS:
        raise ValueError("invalid immutable launch result")
    if (
        result["schema_generation"] != 7
        or result["action_key"] != launch["action_key"]
        or result["launch_key"] != launch["launch_key"]
        or result["unit"] != launch["unit"]
        or result["status"] not in {"succeeded", "failed"}
        or result["effect"] not in {
            "no_effect",
            "provider_reached",
            "ambiguous",
        }
        or not isinstance(result["usage"], dict)
        or set(result["usage"]) != _USAGE_FIELDS
    ):
        raise ValueError("launch result does not bind launch")
    _digest(result["output_sha256"], "launch output", nullable=True)
    _digest(result["result_sha256"], "launch result")
    payload = dict(result)
    payload.pop("result_sha256")
    if result["result_sha256"] != canonical_sha256(payload):
        raise ValueError("launch result seal is invalid")
    action_claim = _action_claim_path(launch, root)
    if result["effect"] == "no_effect":
        consumed_by = (
            _load_claim(action_claim)
            if action_claim.exists() or action_claim.is_symlink()
            else None
        )
        if (
            result["status"] != "failed"
            or result["output_sha256"] is not None
            or any(result["usage"].values())
            or (
                consumed_by is not None
                and consumed_by.get("launch_key") == launch["launch_key"]
            )
        ):
            raise ValueError("NO_EFFECT result cannot consume ActionKey")
    elif action_claim.is_symlink() or not action_claim.is_file():
        raise ValueError("provider-reaching result lacks consumed ActionKey")
    for field, ceiling in launch["cost_ceiling"].items():
        actual = result["usage"].get(field)
        if type(actual) is not int or actual < 0 or actual > ceiling:
            raise ValueError("launch result exceeds cost ceiling")
    return result


def load_launch_result(
    launch: dict[str, Any],
    claim_root: Path,
) -> dict[str, Any]:
    launch = validate_launch(launch)
    root = _real_private_directory(claim_root, "launch claim root")
    _load_claim(_launch_claim_path(launch, root))
    output = _real_private_directory(Path(launch["output"]), "launch output")
    result = _load_claim(output / "result.json")
    return _validate_launch_result(launch, root, result)


def write_launch_result(
    launch: dict[str, Any],
    claim_root: Path,
    result: dict[str, Any],
) -> str:
    launch = validate_launch(launch)
    root = _real_private_directory(claim_root, "launch claim root")
    _load_claim(_launch_claim_path(launch, root))
    output = _real_private_directory(Path(launch["output"]), "launch output")
    _validate_launch_result(launch, root, result)
    path = output / "result.json"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        data = json.dumps(result, sort_keys=True, indent=2).encode() + b"\n"
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return canonical_sha256(result)


def collect_plan_results(
    plan: dict[str, Any],
    claim_root: Path,
) -> list[dict[str, Any]]:
    """Collect the one provider-reaching terminal result for each reached unit."""
    plan = validate_gate_plan(plan)
    root = _real_private_directory(claim_root, "launch claim root")
    collected = []
    for unit in plan["units"]:
        default = build_launch(plan, unit)
        claims = _prior_launches(default, root)
        terminals = []
        for claim in claims:
            launch = (
                default
                if claim["launch_key"] == default["launch_key"]
                else build_launch(
                    plan,
                    unit,
                    infrastructure_generation=claim[
                        "infrastructure_generation"
                    ],
                )
            )
            if any(
                claim[field] != launch[field]
                for field in (
                    "action_key",
                    "launch_key",
                    "infrastructure_generation",
                    "unit",
                    "output",
                )
            ):
                raise ValueError("launch claim does not reconstruct exactly")
            result_path = Path(launch["output"]) / "result.json"
            if result_path.exists() or result_path.is_symlink():
                result = load_launch_result(launch, root)
                if result["effect"] != "no_effect":
                    terminals.append(result)
        if len(terminals) > 1:
            raise ValueError("unit has multiple provider-reaching results")
        if terminals:
            collected.append(terminals[0])
        elif plan["gate"] != "holdout":
            raise ValueError("planned unit lacks a provider-reaching result")
    if not collected:
        raise ValueError("GatePlan has no provider-reaching results")
    return collected


def write_launch_failure(
    launch: dict[str, Any],
    claim_root: Path,
    error: BaseException,
) -> str:
    """Persist a fail-closed result without turning local failure into authority."""
    launch = validate_launch(launch)
    consumed = action_is_consumed(launch, claim_root)
    effect = "ambiguous" if consumed else "no_effect"
    usage = (
        dict(launch["cost_ceiling"])
        if consumed
        else {field: 0 for field in _USAGE_FIELDS}
    )
    result = {
        "schema_generation": 7,
        "action_key": launch["action_key"],
        "launch_key": launch["launch_key"],
        "unit": launch["unit"],
        "status": "failed",
        "effect": effect,
        "output_sha256": (
            canonical_sha256(
                {
                    "domain": "happycodex/schema7/ambiguous-failure",
                    "launch_key": launch["launch_key"],
                    "error_type": type(error).__name__,
                }
            )
            if consumed
            else None
        ),
        "usage": usage,
    }
    result["result_sha256"] = canonical_sha256(result)
    return write_launch_result(launch, claim_root, result)


def load_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    ledger = load_ledger(LEDGER_PATH)
    current = build_snapshot(ROOT)
    if ledger["candidate"] is None:
        pending = {
            "gates": list(GATE_ORDER),
            "corpus_cases": sorted(current["corpus"]["cases"]),
            "holdout_pairs": sorted(current["holdout"]["pairs"]),
        }
        impact = plan_impact(current, current, pending=pending)
    else:
        impact = {
            "schema_version": 1,
            "reasons": ["persisted_candidate"],
            "gates": derive_pending(ledger)["gates"],
            "corpus_cases": derive_pending(ledger)["corpus_cases"],
            "holdout_pairs": derive_pending(ledger)["holdout_pairs"],
            "live_calls": None,
            "cost": None,
        }
    return ledger, current, impact


def derived_release_state(
    ledger: dict[str, Any], *, repo: Path | None = None
) -> dict[str, Any]:
    return {
        "state": derive_status(ledger, repo=repo),
        "pending_gates": derive_pending(ledger)["gates"],
        "coverage": derive_coverage(ledger),
        "receipt_tip": derive_receipt_tip(ledger),
        "freeze_eligibility": derive_freeze_eligibility(ledger, repo=repo),
        "failed": derive_failed(ledger),
        "certified": derive_certified(ledger, repo=repo),
    }


__all__ = (
    "LEDGER_PATH",
    "ROOT",
    "action_is_consumed",
    "build_launch",
    "collect_plan_results",
    "consume_action",
    "derived_release_state",
    "enter_provider_call",
    "load_state",
    "load_launch_result",
    "mint_host_capability",
    "model_gate_profile",
    "model_gate_resource_digests",
    "reserve_launch",
    "validate_consumed_action",
    "validate_capability",
    "validate_launch",
    "validate_model_gate_plan",
    "write_launch_failure",
    "write_launch_result",
)
