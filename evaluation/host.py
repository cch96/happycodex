from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import stat
import subprocess
from typing import Any, Callable

from evaluation.holdout import judge_fixed_holdouts
from evaluation.manifest import load_production_inputs
from evaluation.oracle import hidden_oracle_for, score_hidden
from evaluation.provider import (
    EvaluationCapability, accept_evaluation_authority,
    build_fixed_host_policy, fixed_host_argv, fixed_host_instruction,
    host_contract_from_policy, rebind_evaluation_capability, sanitize_events,
)
from evaluation.records import (
    build_attestation,
    canonical_json,
    canonical_sha256,
    validate_attestation,
    validate_eval_spec,
    validate_product_artifact,
)


class HostEvidenceError(ValueError):
    pass


_USAGE_FIELDS = {
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
    "output_tokens", "reasoning_output_tokens",
}


def _exact(value: dict[str, Any], fields: set[str], label: str) -> None:
    if type(value) is not dict or set(value) != fields:
        raise HostEvidenceError(f"{label} fields differ")


def _usage(value: Any) -> dict[str, int]:
    if type(value) is not dict or set(value) != _USAGE_FIELDS:
        raise HostEvidenceError("native usage fields differ")
    if not all(type(value[field]) is int and value[field] >= 0 for field in _USAGE_FIELDS):
        raise HostEvidenceError("native usage values are invalid")
    return value


def parse_raw_stream(raw: bytes) -> dict[str, Any]:
    if type(raw) is not bytes:
        raise HostEvidenceError("raw stream must be bytes")
    try:
        lines = raw.decode().splitlines()
        if any(not line for line in lines):
            raise HostEvidenceError("raw stream contains an empty JSONL event")
        events = [json.loads(line) for line in lines]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HostEvidenceError("raw stream is not JSONL") from exc
    if not all(type(event) is dict for event in events):
        raise HostEvidenceError("raw stream event is invalid")
    thread_id: str | None = None
    turn_started = False
    turn_completed = False
    turn_failed = False
    failure_message: str | None = None
    open_items: dict[str, str] = {}
    completed_items: set[str] = set()
    item_facts: list[dict[str, str]] = []
    report: dict[str, Any] | None = None
    usage: dict[str, int] | None = None
    for index, event in enumerate(events):
        kind = event.get("type")
        if kind == "thread.started":
            _exact(event, {"type", "thread_id"}, "thread.started")
            if index != 0 or thread_id is not None or type(event["thread_id"]) is not str or not event["thread_id"]:
                raise HostEvidenceError("native thread start is invalid or duplicated")
            thread_id = event["thread_id"]
        elif kind == "turn.started":
            _exact(event, {"type"}, "turn.started")
            if thread_id is None or turn_started or turn_completed:
                raise HostEvidenceError("native turn start is invalid or duplicated")
            turn_started = True
        elif kind in {"item.started", "item.completed"}:
            _exact(event, {"type", "item"}, kind)
            item = event["item"]
            if type(item) is not dict or type(item.get("id")) is not str or not item["id"] or type(item.get("type")) is not str or not item["type"]:
                raise HostEvidenceError("native item identity is invalid")
            if not turn_started or turn_completed:
                raise HostEvidenceError("native item is outside the single turn")
            if report is not None:
                raise HostEvidenceError("native item appears after the final agent message")
            item_id, item_type = item["id"], item["type"]
            if item_type == "agent_message":
                if kind != "item.completed" or set(item) != {"id", "type", "text"} or item_id in completed_items or open_items:
                    raise HostEvidenceError("native final agent message is invalid or duplicated")
                if type(item["text"]) is not str:
                    raise HostEvidenceError("native final agent message text is invalid")
                try:
                    value = json.loads(item["text"])
                except json.JSONDecodeError as exc:
                    raise HostEvidenceError("native final agent message is not JSON") from exc
                if type(value) is not dict:
                    raise HostEvidenceError("native final agent message is not an object")
                report = value
            elif kind == "item.started":
                if item_id in open_items or item_id in completed_items:
                    raise HostEvidenceError("native item start is duplicated")
                open_items[item_id] = item_type
            else:
                if open_items.get(item_id) != item_type:
                    raise HostEvidenceError("native item completion lacks a matching start")
                del open_items[item_id]
                completed_items.add(item_id)
            item_facts.append({"event": kind, "id": item_id, "type": item_type})
        elif kind == "error":
            _exact(event, {"type", "message"}, "error")
            if (
                not turn_started or turn_completed or turn_failed
                or report is not None or failure_message is not None
                or type(event["message"]) is not str or not event["message"]
            ):
                raise HostEvidenceError("native error event is invalid")
            failure_message = event["message"]
        elif kind == "turn.failed":
            _exact(event, {"type", "error"}, "turn.failed")
            error = event["error"]
            if (
                index != len(events) - 1 or not turn_started or turn_completed
                or turn_failed or report is not None or open_items
                or type(error) is not dict or set(error) != {"message"}
                or error.get("message") != failure_message
            ):
                raise HostEvidenceError("native failed terminal is invalid")
            turn_failed = True
        elif kind == "turn.completed":
            _exact(event, {"type", "usage"}, "turn.completed")
            if index != len(events) - 1 or not turn_started or turn_completed or open_items or report is None:
                raise HostEvidenceError("native turn terminal is invalid or not last")
            usage = _usage(event["usage"])
            turn_completed = True
        else:
            raise HostEvidenceError("native stream event type is forbidden")
    if events and thread_id is None:
        raise HostEvidenceError("native stream lacks a thread start")
    if failure_message is not None and not turn_failed:
        raise HostEvidenceError("native error lacks its exact failed terminal")
    return {
        "events": events, "thread_id": thread_id,
        "turn_started": turn_started, "turn_completed": turn_completed,
        "turn_failed": turn_failed,
        "item_facts": item_facts, "report": report, "usage": usage,
        "failure_message_sha256": (
            hashlib.sha256(failure_message.encode()).hexdigest()
            if failure_message is not None else None
        ),
        "raw_events_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _validate_host_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    _exact(metadata, {"started_at", "frozen_at", "exit_code", "timed_out"}, "host metadata")
    if type(metadata["exit_code"]) is not int or type(metadata["timed_out"]) is not bool:
        raise HostEvidenceError("host exit metadata is invalid")
    try:
        started = datetime.fromisoformat(metadata["started_at"].replace("Z", "+00:00"))
        frozen = datetime.fromisoformat(metadata["frozen_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise HostEvidenceError("host timestamps are invalid") from exc
    if started.tzinfo is None or frozen.tzinfo is None or frozen < started:
        raise HostEvidenceError("host timestamps lack timezone or run backwards")
    return {
        **metadata,
        "wall_milliseconds": int(
            (frozen.astimezone(timezone.utc) - started.astimezone(timezone.utc)).total_seconds() * 1000
        ),
    }


def _derive_terminal(parsed: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    host = _validate_host_metadata(metadata)
    usage = parsed["usage"] or {field: 0 for field in _USAGE_FIELDS}
    if parsed["turn_completed"] and host["exit_code"] == 0 and not host["timed_out"]:
        classification, complete = "success", True
    elif (
        host["exit_code"] != 0 and not host["timed_out"]
        and not parsed["turn_started"] and not parsed["turn_completed"]
        and parsed["report"] is None
    ):
        classification, complete = "infrastructure_no_effect", False
    else:
        classification, complete = "ambiguous_or_partial", False
    return {
        "classification": classification,
        "provider_reached": parsed["turn_started"],
        "complete": complete,
        "model_calls": 1 if parsed["turn_started"] else 0,
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "wall_milliseconds": host["wall_milliseconds"],
    }


def _sanitized_projection(parsed: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "thread_id": parsed["thread_id"],
        "turn_started": parsed["turn_started"],
        "turn_completed": parsed["turn_completed"],
        "turn_failed": parsed["turn_failed"],
        "failure_message_sha256": parsed["failure_message_sha256"],
        "items": parsed["item_facts"],
        "agent_report": report if parsed["report"] is not None else None,
        "usage": parsed["usage"],
    }


def attestation_from_raw(
    *, root: Path, product: dict[str, Any], spec: dict[str, Any], unit_id: str,
    raw: bytes, host_metadata: dict[str, Any], authority_sha256: str,
    secrets: list[str] | None = None,
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_eval_spec(spec)
    unit = next((item for item in spec["units"] if item["unit_id"] == unit_id), None)
    if unit is None:
        raise HostEvidenceError("unit is absent from EvalSpec")
    if product["package_semantic_sha256"] != unit["product_semantic_sha256"] or product["external_role_config_sha256"] != unit["external_role_config_sha256"]:
        raise HostEvidenceError("host product differs from planned unit")
    parsed = parse_raw_stream(raw)
    metadata = _validate_host_metadata(host_metadata)
    terminal = _derive_terminal(parsed, host_metadata)
    report = sanitize_events([parsed["report"]], secrets=secrets or [])[0] if parsed["report"] is not None else {}
    inputs = load_production_inputs(root)
    assessment = score_hidden(report, hidden_oracle_for(inputs, unit), stage=unit["stage"])
    observation = {
        "raw_events_sha256": parsed["raw_events_sha256"],
        "raw_report_sha256": canonical_sha256(parsed["report"]),
        "sanitized_event_sha256": canonical_sha256(_sanitized_projection(parsed, report)),
        "terminal_sha256": canonical_sha256(terminal),
        "report": report, "report_sha256": canonical_sha256(report),
        "provenance": {
            "provider": "fixed-host-runner", "model": unit["invocation"]["model"],
            "effort": unit["invocation"]["effort"],
            "tools": unit["invocation"]["tools"],
            "timeout_seconds": unit["invocation"]["timeout_seconds"],
        },
        "parent_attestation_sha256": None,
        "started_at": metadata["started_at"], "frozen_at": metadata["frozen_at"],
        "exit_code": metadata["exit_code"], "timed_out": metadata["timed_out"],
    }
    verdict = "pass" if assessment["passed"] and terminal["classification"] == "success" else "fail"
    diagnostics = [f"fatal:{path}" for path in assessment["fatal"]]
    diagnostics.extend(f"diagnostic:{path}" for path in assessment["diagnostics"])
    return build_attestation(
        kind=unit["kind"], unit_id=unit_id,
        product_semantic_sha256=unit["product_semantic_sha256"],
        product_artifact_sha256=product["package_artifact_sha256"] if unit["stage"] == "exact_final" else None,
        external_role_config_sha256=unit["external_role_config_sha256"],
        provider_input_sha256=unit["provider_input_sha256"],
        oracle_sha256=unit["oracle_sha256"], harness_sha256=unit["harness_sha256"],
        invocation_sha256=unit["invocation_sha256"],
        authority_sha256=authority_sha256,
        host_claim_key=unit["invocation"]["claim_key"],
        observation=observation, terminal=terminal, verdict=verdict,
        diagnostics=diagnostics,
    )


def verify_host_evidence(
    *, record: dict[str, Any], unit: dict[str, Any], spec: dict[str, Any],
    raw: bytes,
) -> dict[str, Any]:
    validate_attestation(record)
    validate_eval_spec(spec)
    parsed = parse_raw_stream(raw)
    if record["observation"]["raw_events_sha256"] != parsed["raw_events_sha256"]:
        raise HostEvidenceError("raw stream digest differs from Attestation")
    observation = record["observation"]
    metadata = {
        key: observation[key]
        for key in ("started_at", "frozen_at", "exit_code", "timed_out")
    }
    terminal = _derive_terminal(parsed, metadata)
    if observation["raw_report_sha256"] != canonical_sha256(parsed["report"]):
        raise HostEvidenceError("raw report digest differs from Attestation")
    if record["terminal"] != terminal or observation["terminal_sha256"] != canonical_sha256(terminal):
        raise HostEvidenceError("raw terminal differs from Attestation")
    if record["unit_id"] != unit["unit_id"] or record["invocation_sha256"] != unit["invocation_sha256"]:
        raise HostEvidenceError("fixed-host invocation differs from EvalSpec")
    if record["host_claim_key"] != unit["invocation"]["claim_key"]:
        raise HostEvidenceError("fixed-host claim differs from EvalSpec")
    if unit["invocation"]["host_contract_sha256"] != spec["host_contract_sha256"]:
        raise HostEvidenceError("fixed-host contract differs from invocation")
    if observation["sanitized_event_sha256"] != canonical_sha256(_sanitized_projection(parsed, observation["report"])):
        raise HostEvidenceError("sanitized projection digest differs from Attestation")
    return {
        **parsed, "terminal": terminal,
        "started_at": observation["started_at"],
        "frozen_at": observation["frozen_at"],
    }


def _safe_claim_root(root: Path) -> Path:
    root = root.absolute()
    if root.is_symlink() or not root.is_dir() or stat.S_IMODE(root.stat().st_mode) != 0o700:
        raise HostEvidenceError("claim root must be a real mode-0700 directory")
    return root


def reserve_claim(
    *, root: Path, claim_key: str, invocation_sha256: str,
    recovery_index: int = 0, recovery_cap: int = 0,
    previous_raw: bytes | None = None,
    previous_attestation: dict[str, Any] | None = None,
    previous_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = _safe_claim_root(root)
    if recovery_index:
        if (
            previous_raw is None or previous_attestation is None or previous_spec is None
            or recovery_index > recovery_cap
        ):
            raise HostEvidenceError("recovery is outside the preauthorized cap")
        validate_attestation(previous_attestation)
        validate_eval_spec(previous_spec)
        unit = next((item for item in previous_spec["units"] if item["unit_id"] == previous_attestation["unit_id"]), None)
        if unit is None:
            raise HostEvidenceError("recovery unit is absent from EvalSpec")
        previous = verify_host_evidence(
            record=previous_attestation, unit=unit, spec=previous_spec, raw=previous_raw,
        )["terminal"]
        if (
            previous_attestation["host_claim_key"] != claim_key
            or previous_attestation["invocation_sha256"] != invocation_sha256
        ):
            raise HostEvidenceError("recovery evidence binds another invocation")
        if not (
            previous["classification"] == "infrastructure_no_effect"
            and previous["provider_reached"] is False
            and previous["model_calls"] == 0
        ):
            raise HostEvidenceError("only proven pre-provider no-effect may recover")
    effective = canonical_sha256(
        {"claim_key": claim_key, "recovery_index": recovery_index}
    )
    path = root / f"{effective}.json"
    payload = {
        "schema_version": 1, "claim_key": claim_key,
        "effective_claim_key": effective, "invocation_sha256": invocation_sha256,
        "recovery_index": recovery_index,
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise HostEvidenceError("provider claim is already reserved") from exc
    try:
        os.write(descriptor, (canonical_json(payload) + "\n").encode())
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return {**payload, "path": str(path), "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _regular(path: Path, mode: int | None = None) -> Path:
    path = path.absolute()
    if path.is_symlink() or not path.is_file() or (mode is not None and stat.S_IMODE(path.stat().st_mode) != mode):
        raise HostEvidenceError(f"private file is not regular mode-{mode:04o}: {path}")
    return path


def _directory(path: Path, mode: int) -> Path:
    path = path.absolute()
    if path.is_symlink() or not path.is_dir() or stat.S_IMODE(path.stat().st_mode) != mode:
        raise HostEvidenceError(f"private directory is not real mode-{mode:04o}: {path}")
    return path


def _sync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _exclusive(path: Path, body: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, mode)
    try:
        os.write(descriptor, body)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _sync_directory(path.parent)


def _freeze(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_symlink():
            raise HostEvidenceError("prepared workspace contains a symlink")
        child.chmod(0o500 if child.is_dir() else 0o400)
    path.chmod(0o500)


def _prepare_unit(policy: dict[str, Any], unit: dict[str, Any]) -> dict[str, Path]:
    workspace = policy["workspace_policy"]
    units = _directory(Path(workspace["units_root"]), 0o700)
    if not unit["unit_id"].replace("-", "").isalnum():
        raise HostEvidenceError("unit id is unsafe for a private path")
    unit_root = units / unit["unit_id"]
    os.mkdir(unit_root, 0o700)
    home, codex_home = unit_root / "home", unit_root / "codex-home"
    os.mkdir(home, 0o700); os.mkdir(codex_home, 0o700)
    schema = unit_root / "output-schema.json"
    _exclusive(schema, (canonical_json(unit["invocation"]["provider_input"]["response_schema"]) + "\n").encode(), 0o600)
    schema.chmod(0o400)
    with schema.open("rb") as frozen_schema:
        os.fsync(frozen_schema.fileno())
    if unit["stage"] == "exact_final":
        cwd = _directory(Path(workspace["exact_final_source"]), 0o500)
    else:
        cwd = unit_root / "workspace"; os.mkdir(cwd, 0o700)
        git = cwd / ".git"; os.mkdir(git, 0o700)
        for name in ("objects", "refs"): os.mkdir(git / name, 0o700)
        os.mkdir(git / "objects" / "info", 0o700); os.mkdir(git / "objects" / "pack", 0o700)
        os.mkdir(git / "refs" / "heads", 0o700); os.mkdir(git / "refs" / "tags", 0o700)
        _exclusive(git / "HEAD", b"ref: refs/heads/main\n", 0o600)
        _exclusive(git / "config", b"[core]\n\trepositoryformatversion = 0\n\tbare = false\n", 0o600)
        _freeze(cwd)
    return {"unit_root": unit_root, "home": home, "codex_home": codex_home, "cwd": cwd, "schema": schema}

def _durable_attestations(spec: dict[str, Any], policy: dict[str, Any], unit_ids: set[str]) -> list[dict[str, Any]]:
    root = _directory(Path(policy["workspace_policy"]["attestations_root"]), 0o700)
    records = []
    planned = {unit["unit_id"]: unit for unit in spec["units"]}
    for unit_id in sorted(unit_ids):
        path = root / f"{unit_id}.json"
        if not path.exists():
            raise HostEvidenceError("required durable predecessor Attestation is absent")
        record = json.loads(_regular(path, 0o600).read_text(encoding="utf-8"))
        validate_attestation(record)
        if record["unit_id"] != unit_id or record["invocation_sha256"] != planned[unit_id]["invocation_sha256"] or record["verdict"] != "pass" or record["terminal"]["classification"] != "success":
            raise HostEvidenceError("required durable predecessor Attestation failed")
        records.append(record)
    return records


def reveal_holdout_mapping(
    *, spec: dict[str, Any], policy: dict[str, Any],
    candidate_product: dict[str, Any] | None = None,
    previous_product: dict[str, Any] | None = None,
    authority_sha256: str | None = None,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> dict[str, Any]:
    validate_eval_spec(spec)
    holdout_ids = {item for pair in spec["holdouts"] for item in pair["unit_ids"]}
    try:
        records = _durable_attestations(spec, policy, holdout_ids)
    except HostEvidenceError as exc:
        raise HostEvidenceError("all six durable holdout Attestations are required before mapping reveal") from exc
    if authority_sha256 is not None and any(item["authority_sha256"] != authority_sha256 for item in records):
        raise HostEvidenceError("holdout Attestations bind another authority")
    if candidate_product is None or previous_product is None:
        raise HostEvidenceError("holdout products are required after six durable Attestations")
    mapping_path = _regular(Path(policy["workspace_policy"]["holdout_mapping_path"]), 0o600)
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    if canonical_sha256(mapping) != policy["workspace_policy"]["holdout_mapping_sha256"]:
        raise HostEvidenceError("holdout mapping identity drift")
    revealed_at = now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    inputs = load_production_inputs(Path(__file__).resolve().parents[1])
    units = {unit["unit_id"]: unit for unit in spec["units"]}
    assessments = {record["unit_id"]: score_hidden(record["observation"]["report"], hidden_oracle_for(inputs, units[record["unit_id"]]), stage="holdout") for record in records}
    judged = judge_fixed_holdouts(
        spec=spec, attestations=records, assessments=assessments, mapping=mapping,
        revealed_at=revealed_at, candidate_product=candidate_product,
        previous_product=previous_product,
    )
    if not judged["passed"]:
        raise HostEvidenceError("fixed holdout decision failed")
    return {"mapping": mapping, "revealed_at": revealed_at, "judgment": judged}


def _run_provider_once(
    capability: EvaluationCapability, spec: dict[str, Any], *, argv: list[str],
    stdin: bytes, env: dict[str, str], cwd: Path, timeout_seconds: int,
    stdout_fd: int, runner: Callable[..., tuple[int, bool]] | None,
) -> tuple[int, bool]:
    rebind_evaluation_capability(capability, spec)
    if runner is not None:
        return runner(argv=argv, stdin=stdin, env=env, cwd=cwd, timeout_seconds=timeout_seconds, stdout_fd=stdout_fd)
    process = subprocess.Popen(
        argv, stdin=subprocess.PIPE, stdout=stdout_fd, stderr=subprocess.DEVNULL,
        cwd=cwd, env=env, start_new_session=True,
    )
    try:
        process.communicate(stdin, timeout=timeout_seconds)
        return process.returncode, False
    except subprocess.TimeoutExpired:
        process.kill(); process.communicate()
        return process.returncode if process.returncode is not None else -9, True


def execute_fixed_host_transaction(
    *, repo_root: Path, product: dict[str, Any], previous_product: dict[str, Any],
    spec: dict[str, Any], unit_id: str, policy: dict[str, Any],
    authority_line: str, supplied_authority: dict[str, Any],
    authenticate_line: Callable[[str, dict[str, Any]], bool], provider_auth: bytes,
    run_provider: Callable[..., tuple[int, bool]] | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> dict[str, Any]:
    validate_product_artifact(product); validate_product_artifact(previous_product); validate_eval_spec(spec)
    if host_contract_from_policy(policy) != spec["host_contract"]:
        raise HostEvidenceError("host policy differs from authority-bound contract")
    expected_line = f"APPROVE HAPPYCODEX EVALUATION {spec['authority_request_sha256']}"
    if authority_line != expected_line:
        raise HostEvidenceError("evaluation authority line differs")
    capability = accept_evaluation_authority(
        spec, supplied_authority,
        lambda value: authenticate_line(authority_line, value),
    )
    rebind_evaluation_capability(capability, spec)
    unit = next((item for item in spec["units"] if item["unit_id"] == unit_id), None)
    if unit is None:
        raise HostEvidenceError("unit is absent from EvalSpec")
    if unit["stage"] == "holdout":
        prior = {item["unit_id"] for item in spec["units"] if item["stage"] == "behavior"}
        if any(item["authority_sha256"] != capability.authority_sha256 for item in _durable_attestations(spec, policy, prior)):
            raise HostEvidenceError("behavior predecessors bind another authority")
    elif unit["stage"] == "exact_final":
        prior = {item["unit_id"] for item in spec["units"] if item["stage"] == "behavior"}
        if any(item["authority_sha256"] != capability.authority_sha256 for item in _durable_attestations(spec, policy, prior)):
            raise HostEvidenceError("behavior predecessors bind another authority")
        reveal_holdout_mapping(
            spec=spec, policy=policy, candidate_product=product,
            previous_product=previous_product, authority_sha256=capability.authority_sha256,
            now=clock,
        )
    instruction = fixed_host_instruction(policy, unit)
    paths = _prepare_unit(policy, unit)
    argv = fixed_host_argv(policy, unit, paths, instruction)
    env = {
        "CODEX_HOME": str(paths["codex_home"]), "HOME": str(paths["home"]),
        "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
    }
    stdin = (canonical_json(unit["invocation"]["provider_input"]) + "\n").encode()
    if type(provider_auth) is not bytes or not provider_auth or provider_auth in (stdin + canonical_json({"argv": argv, "env": env}).encode()):
        raise HostEvidenceError("provider auth is invalid or visible")
    claim = reserve_claim(
        root=Path(policy["workspace_policy"]["claims_root"]),
        claim_key=unit["invocation"]["claim_key"], invocation_sha256=unit["invocation_sha256"],
    )
    raw_path = Path(policy["workspace_policy"]["raw_root"]) / f"{unit_id}.jsonl"
    raw_fd = os.open(raw_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    _sync_directory(raw_path.parent)
    auth_path = paths["codex_home"] / policy["workspace_policy"]["auth_staging_filename"]
    _exclusive(auth_path, provider_auth, 0o600)
    started = clock()
    try:
        exit_code, timed_out = _run_provider_once(
            capability, spec, argv=argv, stdin=stdin, env=env, cwd=paths["cwd"],
            timeout_seconds=unit["invocation"]["timeout_seconds"], stdout_fd=raw_fd,
            runner=run_provider,
        )
        os.fsync(raw_fd)
    finally:
        os.close(raw_fd)
        if auth_path.exists(): auth_path.unlink(); _sync_directory(paths["codex_home"])
    frozen = clock()
    raw = _regular(raw_path, 0o600).read_bytes()
    if provider_auth in raw:
        raise HostEvidenceError("provider auth reached raw events")
    metadata = {
        "started_at": started.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "frozen_at": frozen.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "exit_code": exit_code, "timed_out": timed_out,
    }
    record = attestation_from_raw(
        root=repo_root, product=product, spec=spec, unit_id=unit_id, raw=raw,
        host_metadata=metadata, authority_sha256=capability.authority_sha256,
    )
    verify_host_evidence(record=record, unit=unit, spec=spec, raw=raw)
    attestation_path = Path(policy["workspace_policy"]["attestations_root"]) / f"{unit_id}.json"
    _exclusive(attestation_path, (canonical_json(record) + "\n").encode(), 0o600)
    return {
        "attestation": record, "attestation_path": str(attestation_path),
        "raw_path": str(raw_path), "claim": claim, "argv": argv,
    }
