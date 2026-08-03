from __future__ import annotations

import hashlib
import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import stat
import subprocess
import signal
from typing import Any, Callable

from evaluation.holdout import judge_fixed_holdouts
from evaluation.manifest import load_production_inputs
from evaluation.oracle import hidden_oracle_for, score_hidden
from evaluation.provider import (
    EvaluationCapability, accept_evaluation_authority,
    build_fixed_host_policy, fixed_command_path, fixed_host_argv, fixed_host_instruction,
    host_contract_from_policy, rebind_evaluation_capability,
)
from evaluation.records import (
    canonical_json,
    canonical_sha256,
    evaluation_authority_request_payload,
    validate_attestation,
    validate_eval_spec,
    validate_product_artifact,
)
from evaluation.verify import (
    HostEvidenceError, attestation_from_raw, parse_raw_stream,
    exact_final_authority_proposal, verify_host_evidence,
)


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
    command_bin = unit_root / "command-bin"; os.mkdir(command_bin, 0o700)
    source = Path(policy["provider_policy"]["binary_path"])
    alias = command_bin / policy["provider_policy"]["sandbox_alias_name"]
    try:
        os.link(source, alias, follow_symlinks=False)
        _sync_directory(command_bin); command_bin.chmod(0o500)
        fixed_command_path(policy, command_bin)
    except Exception as exc:
        command_bin.chmod(0o700)
        if alias.exists() or alias.is_symlink(): alias.unlink()
        command_bin.rmdir(); codex_home.rmdir(); home.rmdir(); unit_root.rmdir()
        _sync_directory(units)
        if isinstance(exc, OSError):
            raise HostEvidenceError("unit-private sandbox hard link failed") from exc
        raise
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
    return {
        "unit_root": unit_root, "home": home, "codex_home": codex_home,
        "command_bin": command_bin, "cwd": cwd, "schema": schema,
    }


def _evidence_files(root: Path, suffix: str) -> dict[str, Path]:
    result = {}
    for path in _directory(root, 0o700).iterdir():
        if not path.name.endswith(suffix) or path.name == suffix:
            raise HostEvidenceError("unknown durable-prefix artifact")
        _regular(path, 0o600)
        unit_id = path.name[:-len(suffix)]
        if unit_id in result:
            raise HostEvidenceError("duplicate durable-prefix artifact")
        result[unit_id] = path
    return result


def _verified_prefix(
    *, repo_root: Path, spec: dict[str, Any], policy: dict[str, Any],
    authority_sha256: str | None, launch: dict[str, Any], mode: str = "launch",
    prerequisites: list[dict[str, Any]] | None = None,
    effect_cap: dict[str, int] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if mode not in {"launch", "pending", "final"}:
        raise HostEvidenceError("durable-prefix verification mode differs")
    workspace = policy["workspace_policy"]
    planned = {unit["unit_id"]: unit for unit in spec["units"]}
    by_invocation = {unit["invocation_sha256"]: unit for unit in spec["units"]}
    raw_paths = _evidence_files(Path(workspace["raw_root"]), ".jsonl")
    attestation_paths = _evidence_files(Path(workspace["attestations_root"]), ".json")
    claims = {}
    for path in _directory(Path(workspace["claims_root"]), 0o700).iterdir():
        _regular(path, 0o600)
        try: value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc: raise HostEvidenceError("claim is not JSON") from exc
        if type(value) is not dict or set(value) != {"schema_version", "claim_key", "effective_claim_key", "invocation_sha256", "recovery_index"} or value["schema_version"] != 1 or value["recovery_index"] != 0:
            raise HostEvidenceError("claim fields differ from fixed transaction")
        unit = by_invocation.get(value["invocation_sha256"])
        expected = canonical_sha256({"claim_key": value["claim_key"], "recovery_index": 0})
        if unit is None or value["claim_key"] != unit["invocation"]["claim_key"] or value["effective_claim_key"] != expected or path.name != f"{expected}.json" or unit["unit_id"] in claims:
            raise HostEvidenceError("claim differs from EvalSpec")
        claims[unit["unit_id"]] = value
    artifact_units = set(raw_paths) | set(attestation_paths) | set(claims)
    if not artifact_units.issubset(planned) or set(raw_paths) != set(claims) or not set(attestation_paths).issubset(set(claims)):
        raise HostEvidenceError("durable-prefix inventories differ")
    unit_dirs = {}
    for path in _directory(Path(workspace["units_root"]), 0o700).iterdir():
        _directory(path, 0o700)
        if path.name not in planned or path.name in unit_dirs:
            raise HostEvidenceError("unknown prepared unit directory")
        unit_dirs[path.name] = path
    if set(unit_dirs) != artifact_units:
        raise HostEvidenceError("prepared units differ from durable-prefix artifacts")
    incomplete = set(claims) - set(attestation_paths)
    if any(planned[unit_id]["stage"] != launch["stage"] or planned[unit_id]["order"] != launch["order"] for unit_id in incomplete):
        raise HostEvidenceError("in-flight stage or order differs from launch")
    if mode == "launch":
        for unit_id in incomplete:
            descriptor = os.open(raw_paths[unit_id], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            try:
                try: fcntl.flock(descriptor, fcntl.LOCK_SH | fcntl.LOCK_NB)
                except BlockingIOError: continue
                fcntl.flock(descriptor, fcntl.LOCK_UN)
                raise HostEvidenceError("in-flight raw has no active provider owner")
            finally:
                os.close(descriptor)
    if mode == "launch" and launch["unit_id"] in artifact_units:
        raise HostEvidenceError("launch unit already has a durable effect")
    if mode == "pending" and launch["unit_id"] not in incomplete:
        raise HostEvidenceError("finalizing unit lacks paired claim and raw")
    if mode == "final" and launch["unit_id"] not in attestation_paths:
        raise HostEvidenceError("finalizing unit lacks its Attestation")
    inputs = load_production_inputs(repo_root); records = []; authorities = set()
    totals = {field: 0 for field in ("model_calls", "input_tokens", "output_tokens", "wall_milliseconds")}
    for unit_id in sorted(attestation_paths):
        unit = planned[unit_id]
        record = json.loads(attestation_paths[unit_id].read_text(encoding="utf-8"))
        raw = raw_paths[unit_id].read_bytes()
        verify_host_evidence(record=record, unit=unit, spec=spec, raw=raw)
        assessment = score_hidden(record["observation"]["report"], hidden_oracle_for(inputs, unit), stage=unit["stage"])
        expected = "pass" if assessment["passed"] and record["terminal"]["classification"] == "success" else "fail"
        diagnostics = [*(f"fatal:{path}" for path in assessment["fatal"]), *(f"diagnostic:{path}" for path in assessment["diagnostics"])]
        authorities.add(record["authority_sha256"])
        if (authority_sha256 is not None and record["authority_sha256"] != authority_sha256) or record["verdict"] != expected or record["diagnostics"] != diagnostics:
            raise HostEvidenceError("durable prefix authority or oracle differs")
        if mode == "launch" and (
            record["terminal"]["classification"] != "success"
            or (unit["stage"] != "holdout" and record["verdict"] != "pass")
        ):
            raise HostEvidenceError("durable prefix contains a terminal failure")
        for field in totals: totals[field] += record["terminal"][field]
        records.append(record)
    if len(authorities) > 1:
        raise HostEvidenceError("durable prefix contains mixed authorities")
    prerequisites = prerequisites or []
    if {record["unit_id"] for record in prerequisites} & {record["unit_id"] for record in records}:
        raise HostEvidenceError("prerequisite and current evidence overlap")
    records = [*prerequisites, *records]
    completed = {record["unit_id"] for record in records}
    behavior = {unit_id for unit_id, unit in planned.items() if unit["stage"] == "behavior"}
    if mode == "launch" and launch["stage"] == "behavior" and any(planned[unit_id]["stage"] != "behavior" for unit_id in completed):
        raise HostEvidenceError("behavior launch follows a later stage")
    if mode == "launch" and launch["stage"] == "holdout" and not behavior.issubset(completed):
        raise HostEvidenceError("holdout requires all behavior predecessors")
    if mode == "launch" and launch["stage"] == "exact_final" and (set(planned) - {launch["unit_id"]}) != completed:
        raise HostEvidenceError("exact-final requires the complete durable prefix")
    cap = effect_cap or spec["total_cap"]
    if mode == "launch" and any(totals[field] >= cap[field] for field in totals):
        raise HostEvidenceError("durable prefix exhausted the total cap")
    return records, totals


def _preflight_paths(policy: dict[str, Any], unit: dict[str, Any]) -> dict[str, Path]:
    workspace = policy["workspace_policy"]
    roots = {name: _directory(Path(workspace[f"{name}_root"]), 0o700) for name in ("units", "raw", "attestations", "claims")}
    effective = canonical_sha256({"claim_key": unit["invocation"]["claim_key"], "recovery_index": 0})
    targets = {
        "unit": roots["units"] / unit["unit_id"], "raw": roots["raw"] / f"{unit['unit_id']}.jsonl",
        "attestation": roots["attestations"] / f"{unit['unit_id']}.json", "claim": roots["claims"] / f"{effective}.json",
    }
    if any(path.exists() or path.is_symlink() for path in targets.values()):
        raise HostEvidenceError("fixed transaction target already exists")
    return targets


def _lock_claims(policy: dict[str, Any]) -> int:
    root = _directory(Path(policy["workspace_policy"]["claims_root"]), 0o700)
    descriptor = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    fcntl.flock(descriptor, fcntl.LOCK_EX)
    return descriptor


def _unlock_claims(descriptor: int) -> None:
    try: fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally: os.close(descriptor)


def _discard_preclaim(paths: dict[str, Path], raw_fd: int | None, raw_path: Path | None, auth: Path) -> None:
    if raw_fd is not None: os.close(raw_fd)
    if raw_path is not None and raw_path.exists(): raw_path.unlink(); _sync_directory(raw_path.parent)
    if auth.exists(): auth.unlink(); _sync_directory(auth.parent)
    root = paths["unit_root"]
    if root.exists():
        root.chmod(0o700)
        for child in root.rglob("*"):
            if child.is_dir() and not child.is_symlink(): child.chmod(0o700)
        for child in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
            child.rmdir() if child.is_dir() and not child.is_symlink() else child.unlink()
        root.rmdir(); _sync_directory(root.parent)

def _judge_holdout_mapping(
    *, spec: dict[str, Any], policy: dict[str, Any], prefix: list[dict[str, Any]],
    candidate_product: dict[str, Any], previous_product: dict[str, Any],
    repo_root: Path, now: Callable[[], datetime],
) -> dict[str, Any]:
    holdout_ids = {item for pair in spec["holdouts"] for item in pair["unit_ids"]}
    records = [record for record in prefix if record["unit_id"] in holdout_ids]
    if {record["unit_id"] for record in records} != holdout_ids:
        raise HostEvidenceError("all six durable holdout Attestations are required before mapping reveal")
    mapping_path = _regular(Path(policy["workspace_policy"]["holdout_mapping_path"]), 0o600)
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    if canonical_sha256(mapping) != policy["workspace_policy"]["holdout_mapping_sha256"]:
        raise HostEvidenceError("holdout mapping identity drift")
    revealed_at = now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    inputs = load_production_inputs(repo_root)
    units = {unit["unit_id"]: unit for unit in spec["units"]}
    assessments = {record["unit_id"]: score_hidden(record["observation"]["report"], hidden_oracle_for(inputs, units[record["unit_id"]]), stage="holdout") for record in records}
    judged = judge_fixed_holdouts(
        spec=spec, attestations=records, assessments=assessments, mapping=mapping,
        revealed_at=revealed_at, candidate_product=candidate_product,
        previous_product=previous_product,
    )
    return {"mapping": mapping, "revealed_at": revealed_at, "judgment": judged}


def reveal_holdout_mapping(
    *, spec: dict[str, Any], policy: dict[str, Any],
    candidate_product: dict[str, Any] | None = None,
    previous_product: dict[str, Any] | None = None,
    authority_sha256: str | None = None, repo_root: Path | None = None,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> dict[str, Any]:
    validate_eval_spec(spec)
    source = repo_root or Path(__file__).resolve().parents[1]
    exact = next(item for item in spec["units"] if item["stage"] == "exact_final")
    lock = _lock_claims(policy)
    try:
        prefix, _ = _verified_prefix(
            repo_root=source, spec=spec, policy=policy,
            authority_sha256=authority_sha256, launch=exact,
        )
        if candidate_product is None or previous_product is None:
            raise HostEvidenceError("holdout products are required")
        return _judge_holdout_mapping(
            spec=spec, policy=policy, prefix=prefix,
            candidate_product=candidate_product, previous_product=previous_product,
            repo_root=source, now=now,
        )
    except HostEvidenceError as exc:
        raise HostEvidenceError("all six durable holdout Attestations are required before mapping reveal") from exc
    finally:
        _unlock_claims(lock)


def _run_provider_once(
    capability: EvaluationCapability, spec: dict[str, Any], *, argv: list[str],
    stdin: bytes, env: dict[str, str], cwd: Path, timeout_seconds: int,
    stdout_fd: int, runner: Callable[..., tuple[int, bool]] | None,
) -> tuple[int, bool]:
    rebind_evaluation_capability(capability, spec)
    if runner is not None:
        try: return runner(argv=argv, stdin=stdin, env=env, cwd=cwd, timeout_seconds=timeout_seconds, stdout_fd=stdout_fd)
        except OSError: return 127, False
    try:
        process = subprocess.Popen(
            argv, stdin=subprocess.PIPE, stdout=stdout_fd, stderr=subprocess.DEVNULL,
            cwd=cwd, env=env, start_new_session=True,
        )
    except OSError:
        return 127, False
    try:
        process.communicate(stdin, timeout=timeout_seconds)
        return process.returncode, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            if process.poll() is None: process.kill()
        process.communicate()
        return process.returncode if process.returncode is not None else -9, True


def execute_fixed_host_transaction(
    *, repo_root: Path, product: dict[str, Any], previous_product: dict[str, Any],
    spec: dict[str, Any], unit_id: str, policy: dict[str, Any],
    authority_line: str, supplied_authority: dict[str, Any],
    authenticate_line: Callable[[str, dict[str, Any]], bool], provider_auth: bytes,
    run_provider: Callable[..., tuple[int, bool]] | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    authority_proposal: dict[str, Any] | None = None,
    previous_spec: dict[str, Any] | None = None,
    prerequisite_attestations: list[dict[str, Any]] | None = None,
    prerequisite_raw_streams: dict[str, bytes] | None = None,
    holdout_mapping: dict[str, dict[str, str]] | None = None,
    mapping_revealed_at: str | None = None,
) -> dict[str, Any]:
    validate_product_artifact(product); validate_product_artifact(previous_product); validate_eval_spec(spec)
    if host_contract_from_policy(policy) != spec["host_contract"]:
        raise HostEvidenceError("host policy differs from authority-bound contract")
    proposal = authority_proposal or evaluation_authority_request_payload(spec)
    prerequisites = prerequisite_attestations or []
    selected = proposal.get("selected_unit_ids") if type(proposal) is dict else None
    if selected == ["exact-final"]:
        if previous_spec is None or prerequisite_raw_streams is None or holdout_mapping is None or mapping_revealed_at is None:
            raise HostEvidenceError("exact-only authority lacks bound prerequisites")
        expected_proposal = exact_final_authority_proposal(
            root=repo_root, product=product, previous_product=previous_product,
            previous_spec=previous_spec, spec=spec, attestations=prerequisites,
            raw_streams=prerequisite_raw_streams, holdout_mapping=holdout_mapping,
            mapping_revealed_at=mapping_revealed_at, total_cap=proposal.get("total_cap", {}),
        )
    else:
        expected_proposal = evaluation_authority_request_payload(spec)
        if prerequisites or prerequisite_raw_streams:
            raise HostEvidenceError("full-bundle authority cannot import prerequisites")
    if proposal != expected_proposal:
        raise HostEvidenceError("evaluation authority proposal differs")
    request_sha256 = canonical_sha256(proposal)
    expected_line = f"APPROVE HAPPYCODEX EVALUATION {request_sha256}"
    if authority_line != expected_line:
        raise HostEvidenceError("evaluation authority line differs")
    capability = accept_evaluation_authority(
        spec, supplied_authority,
        lambda value: authenticate_line(authority_line, value),
        proposal=proposal,
    )
    rebind_evaluation_capability(capability, spec, unit_id)
    unit = next((item for item in spec["units"] if item["unit_id"] == unit_id), None)
    if unit is None:
        raise HostEvidenceError("unit is absent from EvalSpec")
    stdin = (canonical_json(unit["invocation"]["provider_input"]) + "\n").encode()
    if type(provider_auth) is not bytes or not provider_auth or provider_auth in stdin:
        raise HostEvidenceError("provider auth is invalid or visible")
    lock = _lock_claims(policy); paths = None; raw_fd = None; raw_path = None
    try:
        prefix_records, prefix_totals = _verified_prefix(
            repo_root=repo_root, spec=spec, policy=policy,
            authority_sha256=capability.authority_sha256, launch=unit,
            prerequisites=prerequisites, effect_cap=proposal["total_cap"],
        )
        targets = _preflight_paths(policy, unit); holdout_reveal = None
        if unit["stage"] == "exact_final":
            holdout_reveal = _judge_holdout_mapping(
                spec=spec, policy=policy, prefix=prefix_records,
                candidate_product=product, previous_product=previous_product,
                repo_root=repo_root, now=clock,
            )
            if not holdout_reveal["judgment"]["passed"]:
                return {
                    "attestation": None, "attestation_path": None,
                    "raw_path": None, "claim": None, "argv": None,
                    "holdout_reveal": holdout_reveal, "usage": prefix_totals,
                    "stop_reason": "holdout_failure", "cap_exceeded": [],
                }
        instruction = fixed_host_instruction(policy, unit); paths = _prepare_unit(policy, unit)
        argv = fixed_host_argv(policy, unit, paths, instruction)
        command_path = fixed_command_path(policy, paths["command_bin"])
        env = {
            "CODEX_HOME": str(paths["codex_home"]), "HOME": str(paths["home"]),
            "PATH": command_path, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
        }
        if provider_auth in canonical_json({"argv": argv, "env": env}).encode():
            raise HostEvidenceError("provider auth is visible in host surfaces")
        auth_path = paths["codex_home"] / policy["workspace_policy"]["auth_staging_filename"]
        _exclusive(auth_path, provider_auth, 0o600)
        raw_path = targets["raw"]
        raw_fd = os.open(raw_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        fcntl.flock(raw_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _sync_directory(raw_path.parent)
        claim = reserve_claim(
            root=Path(policy["workspace_policy"]["claims_root"]),
            claim_key=unit["invocation"]["claim_key"], invocation_sha256=unit["invocation_sha256"],
        )
    except Exception:
        if paths is not None:
            auth = paths["codex_home"] / policy["workspace_policy"]["auth_staging_filename"]
            _discard_preclaim(paths, raw_fd, raw_path, auth)
        raise
    finally:
        _unlock_claims(lock)
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
        root=repo_root,
        product=product if unit["product_semantic_sha256"] == product["package_semantic_sha256"] else previous_product,
        spec=spec, unit_id=unit_id, raw=raw,
        host_metadata=metadata, authority_sha256=capability.authority_sha256,
    )
    verify_host_evidence(record=record, unit=unit, spec=spec, raw=raw)
    attestation_path = targets["attestation"]
    lock = _lock_claims(policy)
    try:
        _verified_prefix(
            repo_root=repo_root, spec=spec, policy=policy,
            authority_sha256=capability.authority_sha256, launch=unit,
            mode="pending", prerequisites=prerequisites,
            effect_cap=proposal["total_cap"],
        )
        _exclusive(attestation_path, (canonical_json(record) + "\n").encode(), 0o600)
        records, totals = _verified_prefix(
            repo_root=repo_root, spec=spec, policy=policy,
            authority_sha256=capability.authority_sha256, launch=unit,
            mode="final", prerequisites=prerequisites,
            effect_cap=proposal["total_cap"],
        )
    finally:
        _unlock_claims(lock)
    exceeded = [field for field in totals if totals[field] > proposal["total_cap"][field]]
    stop_reason = None
    planned = {item["unit_id"]: item for item in spec["units"]}
    if any(
        item["terminal"]["classification"] != "success"
        or (planned[item["unit_id"]]["stage"] != "holdout" and item["verdict"] != "pass")
        for item in records
    ):
        stop_reason = "terminal_failure"
    elif exceeded:
        stop_reason = "total_cap_exceeded"
    return {
        "attestation": record, "attestation_path": str(attestation_path),
        "raw_path": str(raw_path), "claim": claim, "argv": argv,
        "holdout_reveal": holdout_reveal, "usage": totals,
        "stop_reason": stop_reason, "cap_exceeded": exceeded,
    }
