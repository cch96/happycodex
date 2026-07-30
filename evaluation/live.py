from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from evaluation.core.identity import canonical_sha256
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
_INTENT_FIELDS = frozenset(
    {
        "schema_version",
        "candidate_sha256",
        "plan_sha256",
        "gate",
        "unit",
        "invocation",
        "cost_ceiling",
        "units",
        "resource_digests",
        "output",
        "approval_content_sha256",
        "intent_digest",
    }
)
_INVOCATION_FIELDS = frozenset(
    {"argv", "cwd", "env", "timeout_ms", "model", "effort", "arm"}
)
_RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "intent_digest",
        "unit",
        "status",
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


def build_effect_intent(plan: dict[str, Any], unit: str) -> dict[str, Any]:
    """Build audit-bound effect content; this object grants no permission."""
    plan = validate_gate_plan(plan)
    if unit not in plan["units"]:
        raise ValueError("EffectIntent unit is outside GatePlan")
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
    output_root = Path(plan["output"]).absolute()
    output_path = (output_root / unit).absolute()
    if output_path.parent != output_root:
        raise ValueError("EffectIntent output must be a direct GatePlan child")
    output = str(output_path)
    payload = {
        "schema_version": 1,
        "candidate_sha256": plan["candidate_sha256"],
        "plan_sha256": plan["plan_sha256"],
        "gate": plan["gate"],
        "unit": unit,
        "invocation": invocation,
        "cost_ceiling": dict(plan["cost_ceiling"]),
        "units": list(plan["units"]),
        "resource_digests": list(plan["resource_digests"]),
        "output": output,
        "approval_content_sha256": plan["approval_content_sha256"],
    }
    payload["intent_digest"] = canonical_sha256(payload)
    return validate_effect_intent(payload)


def validate_effect_intent(
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
    if not isinstance(value, dict) or set(value) != _INTENT_FIELDS:
        raise ValueError("invalid EffectIntent fields")
    if value["schema_version"] != 1:
        raise ValueError("invalid EffectIntent schema")
    for field in (
        "candidate_sha256",
        "plan_sha256",
        "approval_content_sha256",
        "intent_digest",
    ):
        _digest(value[field], f"EffectIntent {field}")
    if type(value["gate"]) is not str or value["gate"] not in GATE_ORDER:
        raise ValueError("invalid EffectIntent gate")
    if type(value["unit"]) is not str or not value["unit"]:
        raise ValueError("invalid EffectIntent unit")
    invocation = value["invocation"]
    if not isinstance(invocation, dict) or set(invocation) != _INVOCATION_FIELDS:
        raise ValueError("invalid EffectIntent invocation")
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
        raise ValueError("invalid EffectIntent invocation")
    if (
        not isinstance(value["cost_ceiling"], dict)
        or set(value["cost_ceiling"]) != _USAGE_FIELDS
        or any(type(item) is not int or item < 0
               for item in value["cost_ceiling"].values())
    ):
        raise ValueError("invalid EffectIntent cost ceiling")
    if (
        not isinstance(value["units"], list)
        or value["units"] != sorted(set(value["units"]))
        or value["unit"] not in value["units"]
        or not isinstance(value["resource_digests"], list)
        or value["resource_digests"] != sorted(set(value["resource_digests"]))
    ):
        raise ValueError("invalid EffectIntent units or resources")
    for digest in value["resource_digests"]:
        _digest(digest, "EffectIntent resource")
    output_path = Path(str(value["output"]))
    if not output_path.is_absolute():
        raise ValueError("EffectIntent output must be absolute")
    payload = dict(value)
    seal = payload.pop("intent_digest")
    if seal != canonical_sha256(payload):
        raise ValueError("EffectIntent content changed")
    if plan is not None and value != build_effect_intent(plan, value["unit"]):
        raise ValueError("EffectIntent does not match GatePlan")
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
            raise ValueError(f"EffectIntent {label} drift")
    return value


def _output_preflight(path: Path) -> tuple[Path, Path]:
    output = path.absolute()
    if output != Path(os.path.abspath(output)) or ".." in output.parts:
        raise ValueError("EffectIntent output path drift")
    if output.exists() or output.is_symlink():
        raise ValueError("EffectIntent output must be absent")
    base = output.parent
    if base.exists():
        _real_private_directory(base, "EffectIntent output parent")
        return base, output
    grandparent = _real_private_directory(
        base.parent,
        "EffectIntent output grandparent",
    )
    if base.parent != grandparent:
        raise ValueError("EffectIntent output parent alias")
    return base, output


def _consumption_path(intent: dict[str, Any], claim_root: Path) -> Path:
    digest = canonical_sha256(
        {"intent_digest": intent["intent_digest"], "unit": intent["unit"]}
    )
    return claim_root / f"effect-{digest}"


def reserve_effect(
    intent: dict[str, Any],
    claim_root: Path,
    *,
    plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Consume one intent+unit and create its absent output before any runner."""
    intent = validate_effect_intent(intent, plan=plan)
    root = _real_private_directory(claim_root, "effect claim root")
    base, output = _output_preflight(Path(intent["output"]))
    claim = _consumption_path(intent, root)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(claim, flags, 0o600)
    try:
        data = (
            json.dumps(
                {
                    "schema_version": 1,
                    "intent_digest": intent["intent_digest"],
                    "unit": intent["unit"],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            + b"\n"
        )
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if not base.exists():
        os.mkdir(base, 0o700)
    descriptor = os.open(
        base,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.mkdir(output.name, 0o700, dir_fd=descriptor)
    except FileExistsError as exc:
        raise ValueError("EffectIntent output collision after consumption") from exc
    finally:
        os.close(descriptor)
    return {
        "intent_digest": intent["intent_digest"],
        "unit": intent["unit"],
        "claim": str(claim),
        "output": str(output),
    }


def write_effect_result(
    intent: dict[str, Any],
    claim_root: Path,
    result: dict[str, Any],
) -> str:
    intent = validate_effect_intent(intent)
    root = _real_private_directory(claim_root, "effect claim root")
    claim = _consumption_path(intent, root)
    if claim.is_symlink() or not claim.is_file():
        raise ValueError("EffectIntent unit is not durably consumed")
    output = _real_private_directory(Path(intent["output"]), "effect output")
    if not isinstance(result, dict) or set(result) != _RESULT_FIELDS:
        raise ValueError("invalid immutable effect result")
    if (
        result["schema_version"] != 1
        or result["intent_digest"] != intent["intent_digest"]
        or result["unit"] != intent["unit"]
        or result["status"] not in {"succeeded", "failed"}
        or not isinstance(result["usage"], dict)
        or set(result["usage"]) != _USAGE_FIELDS
    ):
        raise ValueError("effect result does not bind intent")
    _digest(result["output_sha256"], "effect output", nullable=True)
    _digest(result["result_sha256"], "effect result")
    payload = dict(result)
    seal = payload.pop("result_sha256")
    if result["result_sha256"] != canonical_sha256(payload):
        raise ValueError("effect result seal is invalid")
    for field, ceiling in intent["cost_ceiling"].items():
        actual = result["usage"].get(field)
        if type(actual) is not int or actual < 0 or actual > ceiling:
            raise ValueError("effect result exceeds cost ceiling")
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
    "build_effect_intent",
    "derived_release_state",
    "load_state",
    "reserve_effect",
    "validate_effect_intent",
    "write_effect_result",
)
