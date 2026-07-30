from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any


PACKAGE_PATHS = (".agents", ".codex-plugin", "README.md", "skills")
EVALUATOR_PYTHON_INPUTS = frozenset(
    {
        "evaluation/__init__.py",
        "evaluation/cli.py",
        "evaluation/live.py",
        "evaluation/semantic/__init__.py",
        "evaluation/semantic/codec.py",
        "evaluation/semantic/model.py",
        "evaluation/semantic/reducer.py",
        "evaluation/semantic/replay.py",
        "evaluation/core/__init__.py",
        "evaluation/core/identity.py",
        "evaluation/core/impact.py",
        "evaluation/core/ledger.py",
        "evaluation/core/receipt.py",
        "evaluation/core/schema.py",
        "evaluation/corpus/__init__.py",
        "evaluation/corpus/engine.py",
        "evaluation/holdout/__init__.py",
        "evaluation/holdout/blind.py",
        "evaluation/holdout/compare.py",
        "evaluation/holdout/engine.py",
    }
)
EVALUATOR_FIXED_JSON_INPUTS = frozenset(
    {"evaluation/contracts-v7.json", "evaluation/executor-role.json"}
)
_TOOL_EVENT_TYPES = {
    "collaboration": "collab_tool_call",
    "command_execution": "command_execution",
    "todo": "todo_list",
    "web_search": "web_search",
}
PERMISSION_PROFILE = "happycodex-evaluator"
RECOVERY_STATE_FIELDS = frozenset(
    {
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
        "writer",
        "milestone_phase",
        "next_action",
        "pending_gates",
        "tests",
        "worktree",
        "live_agents",
        "marker_ids",
    }
)
RECOVERY_MANIFEST_PREFIX = "RECOVERY-MANIFEST-SHA256:"
RECOVERY_MANIFEST_PATTERN = re.compile(
    rf"^{re.escape(RECOVERY_MANIFEST_PREFIX)}([0-9a-f]{{64}})$"
)
PUBLIC_02_ARM = "public-0.2"
PUBLIC_02_SOURCE_COMMIT = "3b9c11fac1f97df75263e0bfc6421c575e04e8b2"
PUBLIC_02_SOURCE_TREE = "4708ebc12f74d4482764796fdd00f1fa7194a13a"
PUBLIC_02_PACKAGE_ARTIFACT_SHA256 = (
    "77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89"
)
PUBLIC_02_PACKAGE_SEMANTIC_SHA256 = "fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4"
PUBLIC_02_SKILL_ENTRIES = ("SKILL.md", "agents/openai.yaml", "references/external-review.md", "references/task-packets.md")
NATIVE_TOOL_NAMES = ("apply_patch", "codex", "codex-linux-sandbox", "rg")
FILESYSTEM_ISOLATION_POLICY = {
    "mechanism": "codex-permission-profile",
    "profile": PERMISSION_PROFILE,
    "filesystem": "minimal-plus-current-workspace-and-native-tools",
    "default_access": "deny",
    "workspace": "read-only",
    "nonworkspace": "unreadable",
    "credential_file": "parent-only-command-denied",
    "native_tool_allowlist": NATIVE_TOOL_NAMES,
    "native_tools": "read-only",
    "home": "isolated",
    "parent_task_environment": "stripped",
    "command_environment": "inherit-none",
    "network": "disabled",
    "selection": "explicit-on-every-turn",
}
EXECUTOR_ROLE = {
    "schema_version": 1,
    "role_id": "happycodex_executor",
    "model": "gpt-5.6-sol",
    "reasoning_effort": "high",
    "writer_policy": "fixed_executor_only",
    "delegation": "forbidden",
    "repository_effects": "exact_grant_and_resource_claim",
    "external_effects": "separate_exact_user_authority",
}
def recovery_manifest_projection(value: Any) -> dict[str, Any]:
    markers = value.get("marker_ids", []) if isinstance(value, dict) else []
    candidates = [
        marker
        for marker in markers
        if isinstance(marker, str) and marker.startswith(RECOVERY_MANIFEST_PREFIX)
    ]
    match = (
        RECOVERY_MANIFEST_PATTERN.fullmatch(candidates[0])
        if len(candidates) == 1
        else None
    )
    return {
        "recovery_manifest_count": len(candidates),
        "recovery_manifest_sha256": match.group(1) if match else None,
    }


def recovery_summary_consistent(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    markers = value.get("marker_ids")
    tests = value.get("tests")
    if not isinstance(markers, list) or not isinstance(tests, dict):
        return False
    test_markers = tests.get("marker_ids")
    failed = tests.get("failed")
    accepted = tests.get("accepted_failures")
    return (
        isinstance(test_markers, list)
        and all(type(item) is str and item for item in [*markers, *test_markers])
        and len(markers) == len(set(markers))
        and len(test_markers) == len(set(test_markers))
        and set(test_markers).issubset(markers)
        and type(failed) is int
        and type(accepted) is int
        and 0 <= accepted <= failed
    )


IdentityError = ValueError


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return sha256_bytes(payload.encode())


def validate_invocation_profile(
    value: Any,
    *,
    require_bound_binary: bool = False,
) -> dict[str, Any]:
    from evaluation.core.schema import CONTRACTS, validate_named
    validate_named(CONTRACTS, "invocation_profile", value)
    binary, tools, session = value["binary"], value["tools"], value["session"]
    digest = binary["identity_sha256"]
    if require_bound_binary and digest is None:
        raise IdentityError("live invocation binary identity is unbound")
    allowed = tools["allowed"]
    if (
        allowed != sorted(set(allowed))
        or any(item not in _TOOL_EVENT_TYPES for item in allowed)
        or tools["event_item_types"]
        != sorted(_TOOL_EVENT_TYPES[item] for item in allowed)
    ):
        raise IdentityError("invalid invocation tool profile")
    if (
        "web_search" in allowed and value["network"] != "enabled"
    ):
        raise IdentityError("invalid invocation external access profile")
    if (
        session["history"] != "isolated"
    ):
        raise IdentityError("invalid invocation session profile")
    return value


def invocation_profile(
    *,
    model: str,
    effort: str,
    timeout_seconds: int,
    arm: str,
    binary_identity_sha256: str | None = None,
    allowed_tools: tuple[str, ...] = ("command_execution",),
    network: str = "disabled",
    hooks: str = "disabled",
    session_mode: str = "fresh-with-bounded-resume",
) -> dict[str, Any]:
    allowed = sorted(allowed_tools)
    return validate_invocation_profile(
        {
            "provider": "openai",
            "binary": {
                "command": "codex",
                "identity_sha256": binary_identity_sha256,
            },
            "model": model,
            "effort": effort,
            "timeout_seconds": timeout_seconds,
            "arm": arm,
            "tools": {
                "allowed": allowed,
                "event_item_types": sorted(_TOOL_EVENT_TYPES[item] for item in allowed),
            },
            "network": network,
            "hooks": hooks,
            "session": {"mode": session_mode, "history": "isolated"},
        }
    )


def path_record(path: Path) -> dict[str, Any]:
    mode = path.lstat().st_mode & 0o7777
    if path.is_symlink():
        return {"kind": "symlink", "mode": mode, "target": os.readlink(path)}
    if path.is_file():
        content = path.read_bytes()
        return {
            "kind": "file",
            "mode": mode,
            "bytes": len(content),
            "sha256": sha256_bytes(content),
        }
    if path.is_dir():
        return {"kind": "directory", "mode": mode}
    return {"kind": "other", "mode": mode}


def workspace_file_manifest(repo: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(repo).as_posix(): path_record(path)
        for path in sorted(repo.rglob("*"))
        if path.relative_to(repo).parts[0] != ".git"
    }


def selected_package_paths(plugin: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in PACKAGE_PATHS:
        root = plugin / relative
        if not root.exists() and not root.is_symlink():
            raise FileNotFoundError(root)
        paths.append(root)
        if root.is_dir() and not root.is_symlink():
            paths.extend(root.rglob("*"))
    return paths


def normalize_package_modes(plugin: Path) -> None:
    for path in selected_package_paths(plugin.resolve()):
        if not path.is_symlink() and path.is_dir():
            path.chmod(0o700)
        elif not path.is_symlink() and path.is_file():
            path.chmod(0o700 if path.stat().st_mode & 0o111 else 0o600)


def package_manifest_sha256(plugin: Path) -> str:
    return canonical_sha256(
        {
            path.relative_to(plugin).as_posix(): path_record(path)
            for path in selected_package_paths(plugin)
        }
    )


def package_identities(plugin: Path) -> dict[str, str]:
    plugin = plugin.resolve()
    manifest = _read_json(plugin / ".codex-plugin" / "plugin.json")
    if not isinstance(manifest, dict):
        raise IdentityError("plugin manifest must be an object")
    semantic_manifest = dict(manifest)
    semantic_manifest.pop("version", None)
    semantic_payload = {
        "schema_version": 1,
        "plugin_manifest": semantic_manifest,
        "marketplace": _read_json(plugin / ".agents" / "plugins" / "marketplace.json"),
        "skills": {
            path.relative_to(plugin).as_posix(): path_record(path)
            for root in [plugin / "skills"]
            for path in sorted([root, *root.rglob("*")])
        },
    }
    return {
        "semantic_sha256": canonical_sha256(semantic_payload),
        "artifact_sha256": package_manifest_sha256(plugin),
    }


def executor_role_identity(root: Path) -> str:
    role = _read_json(root.resolve() / "evaluation" / "executor-role.json")
    if role != EXECUTOR_ROLE:
        raise IdentityError("invalid executor role contract")
    return canonical_sha256(role)


def _git(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            env={**os.environ, "LC_ALL": "C"},
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise IdentityError(f"Git source identity failed: {' '.join(args)}") from exc


def source_archive_identity(repo: Path, revision: str) -> dict[str, Any]:
    repo = repo.resolve()
    commit = _git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}")
    if subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, "HEAD"],
        check=False,
        capture_output=True,
    ).returncode:
        raise IdentityError("source commit is not reachable from HEAD")
    with tempfile.TemporaryDirectory(prefix="happycodex-source-") as raw:
        archive = Path(raw) / "source.tar"
        extracted = Path(raw) / "source"
        extracted.mkdir()
        if subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "archive",
                "--format=tar",
                "--output",
                str(archive),
                commit,
            ],
            check=False,
            capture_output=True,
        ).returncode:
            raise IdentityError("cannot archive source commit")
        shutil.unpack_archive(str(archive), extracted)
        normalize_package_modes(extracted)
        return {
            "source_commit": commit,
            "source_tree": _git(repo, "rev-parse", f"{commit}^{{tree}}"),
            "package": package_identities(extracted),
            "executor_role_sha256": executor_role_identity(extracted),
        }


def codex_identity() -> dict[str, str]:
    raw = shutil.which("codex")
    path = Path(raw).resolve() if raw else None
    if path is None or not path.is_file():
        raise IdentityError("required Codex executable is unavailable")
    try:
        completed = subprocess.run(
            [str(path), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise IdentityError("cannot identify Codex executable") from exc
    lines = (completed.stdout or completed.stderr).strip().splitlines()
    if completed.returncode or not lines:
        raise IdentityError("cannot identify Codex executable")
    return {
        "sha256": sha256_bytes(path.read_bytes()),
        "version": lines[0],
    }


def _evaluator_json_inputs(root: Path) -> set[str]:
    result = set(EVALUATOR_FIXED_JSON_INPUTS)
    for path in sorted((root / "evaluation" / "cases").glob("*.json")):
        result.add(path.relative_to(root).as_posix())
    holdout_root = root / "evaluation" / "holdouts"
    manifest = holdout_root / "manifest.json"
    if manifest.is_file():
        result.add(manifest.relative_to(root).as_posix())
    for path in sorted((holdout_root / "cases").glob("*.json")):
        result.add(path.relative_to(root).as_posix())
    return result


def engine_inventory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    evaluation = root / "evaluation"
    modules = {
        path.relative_to(root).as_posix()
        for path in evaluation.rglob("*.py")
        if "__pycache__" not in path.parts
    }
    unknown = sorted(modules - EVALUATOR_PYTHON_INPUTS)
    missing = sorted(EVALUATOR_PYTHON_INPUTS - modules)
    if unknown or missing:
        detail = unknown or missing
        label = "unknown" if unknown else "missing"
        raise IdentityError(f"{label} engine input: {', '.join(detail)}")
    json_inputs = _evaluator_json_inputs(root)
    discovered_json = {
        path.relative_to(root).as_posix()
        for path in evaluation.rglob("*.json")
        if "__pycache__" not in path.parts
    }
    outputs = {
        item
        for item in discovered_json
        if item == "evaluation/results/current.json"
        or Path(item).parts[:3] == ("evaluation", "results", "evidence")
    }
    unknown_json = sorted(discovered_json - json_inputs - outputs)
    if unknown_json:
        raise IdentityError(f"unknown engine input: {', '.join(unknown_json)}")
    entries = []
    for relative in sorted(EVALUATOR_PYTHON_INPUTS | json_inputs):
        path = root / relative
        if not path.is_file():
            raise IdentityError(f"missing engine input: {relative}")
        content = path.read_bytes()
        entries.append(
            {
                "path": relative,
                "bytes": len(content),
                "sha256": sha256_bytes(content),
            }
        )
    payload = {
        "schema_version": 1,
        "entries": entries,
    }
    return {**payload, "manifest_sha256": canonical_sha256(payload)}


def case_semantic_sha256(
    case: dict[str, Any],
    *,
    evaluator_bundle_sha256: str,
    package_semantic_sha256: str,
    model: str,
    effort: str,
    timeout: int,
    arm: str,
) -> str:
    return canonical_sha256(
        {
            "schema_version": 1,
            "case": case,
            "evaluator_bundle_sha256": evaluator_bundle_sha256,
            "package_semantic_sha256": package_semantic_sha256,
            "model": model,
            "effort": effort,
            "timeout_seconds": timeout,
            "arm": arm,
        }
    )
