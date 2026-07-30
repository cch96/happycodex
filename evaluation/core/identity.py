from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any


PACKAGE_PATHS = (".agents", ".codex-plugin", "README.md", "skills")
ENGINE_CATEGORIES = ("semantic", "harness", "artifact")
CORPUS_SEMANTIC_PATHS = frozenset(
    {
        "evaluation/corpus/engine.py",
        "evaluation/contracts-v6.json",
        "evaluation/protocol.py",
    }
)
MODULE_CATEGORIES = {
    "evaluation/__init__.py": "harness",
    "evaluation/cli.py": "harness",
    "evaluation/live.py": "harness",
    "evaluation/protocol.py": "semantic",
    "evaluation/core/__init__.py": "harness",
    "evaluation/core/identity.py": "harness",
    "evaluation/core/impact.py": "harness",
    "evaluation/core/ledger.py": "harness",
    "evaluation/core/receipt.py": "artifact",
    "evaluation/core/schema.py": "harness",
    "evaluation/corpus/__init__.py": "harness",
    "evaluation/corpus/engine.py": "semantic",
    "evaluation/holdout/__init__.py": "harness",
    "evaluation/holdout/blind.py": "harness",
    "evaluation/holdout/compare.py": "semantic",
    "evaluation/holdout/engine.py": "harness",
}
ARCHIVED_MODULE_CATEGORIES = {
    "evaluation/semantic/__init__.py": "semantic",
    "evaluation/semantic/canonical.py": "semantic",
    "evaluation/semantic/decide.py": "semantic",
    "evaluation/semantic/parse.py": "semantic",
    "evaluation/semantic/types.py": "semantic",
}
_TOOL_EVENT_TYPES = {
    "collaboration": "collab_tool_call",
    "command_execution": "command_execution",
    "todo": "todo_list",
    "web_search": "web_search",
}
PERMISSION_PROFILE = "happycodex-evaluator"
PROTOCOL_REVIEW_MODES = ("none", "focused_hardening", "exact_final")
CONVERGENCE_PHASES = (
    "implementation",
    "focused_hardening",
    "candidate_frozen",
    "exact_final",
    "closed",
)
PERMISSION_VALUES = {
    "decision": frozenset({"continue", "stop_for_user", "complete", "incomplete"}),
    "qualifies": frozenset({True, False}),
    "execplan_condition": frozenset(
        {"not_required", "missing", "usable", "needs_amendment"}
    ),
    "protocol_may_product_write": frozenset({True, False}),
    "protocol_review_mode": frozenset(PROTOCOL_REVIEW_MODES),
    "protocol_may_complete": frozenset({True, False}),
}
PERMISSION_FIELDS = frozenset(PERMISSION_VALUES)


def permission_assertions_invalid(expected: dict[str, Any]) -> bool:
    for field, allowed in PERMISSION_VALUES.items():
        raw = expected.get(field)
        values = raw if isinstance(raw, list) else [raw]
        expected_type = type(next(iter(allowed)))
        if (
            not values
            or len({(type(item), item) for item in values}) != len(values)
            or any(type(item) is not expected_type or item not in allowed for item in values)
        ):
            return True
    return False
RECOVERY_ACTIONS = (
    "ask_user",
    "create_execplan",
    "complete_boundary_union",
    "create_contract_freeze_revision",
    "observe_red",
    "implement",
    "repair",
    "run_checks",
    "reconciliation",
    "focused_review",
    "freeze_candidate",
    "exact_final_review",
    "release",
    "none",
    "unknown",
)
RECOVERY_PENDING_GATES = (
    "user_selection",
    "contract_freeze",
    "red_oracle",
    "product_edit",
    "checks",
    "family_hardening",
    "boundary_repair",
    "reconciliation",
    "focused_review",
    "candidate_freeze",
    "exact_final_review",
    "release",
)
RECOVERY_GATE_FIELDS = frozenset(
    {
        "qualifies",
        "protocol_may_product_write",
        "protocol_review_mode",
        "protocol_may_complete",
    }
)
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
BLOCKER_CLASSES = frozenset(
    {
        "original_goal",
        "frozen_acceptance",
        "safety_data_integrity",
        "production_condition",
        "exhaustive_claim",
    }
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


def classifications_share_identity(left: Any, right: Any) -> bool:
    return (
        isinstance(left, dict)
        and isinstance(right, dict)
        and type(left.get("identity")) is str
        and bool(left["identity"].strip())
        and left["identity"] == right.get("identity")
    )


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
    mcp: str = "disabled",
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
            "mcp": mcp,
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
            "engine_manifest_sha256": engine_inventory(extracted)["manifest_sha256"],
            "executor_role_sha256": executor_role_identity(extracted),
        }


def _executable_identity(name: str, *, executable: str | None = None) -> dict[str, str]:
    raw = executable or shutil.which(name)
    path = Path(raw).resolve() if raw else None
    if path is None or not path.is_file():
        raise IdentityError(f"required certification tool is unavailable: {name}")
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
        raise IdentityError(f"cannot identify certification tool: {name}") from exc
    lines = (completed.stdout or completed.stderr).strip().splitlines()
    if completed.returncode or not lines:
        raise IdentityError(f"cannot identify certification tool: {name}")
    return {
        "path": str(path),
        "sha256": sha256_bytes(path.read_bytes()),
        "version": lines[0],
    }


def toolchain_identity() -> dict[str, dict[str, Any]]:
    return {
        "python": _executable_identity("python", executable=sys.executable),
        "codex": _executable_identity("codex"),
        "git": _executable_identity("git"),
        "rg": _executable_identity("rg"),
    }


def _schema_paths(root: Path) -> dict[str, str]:
    result = {"evaluation/executor-role.json": "artifact", "evaluation/contracts-v6.json": "semantic"}
    for path in sorted((root / "evaluation" / "cases").glob("*.json")):
        result[path.relative_to(root).as_posix()] = "semantic"
    holdout_root = root / "evaluation" / "holdouts"
    manifest = holdout_root / "manifest.json"
    if manifest.is_file():
        result[manifest.relative_to(root).as_posix()] = "semantic"
    for path in sorted((holdout_root / "cases").glob("*.json")):
        result[path.relative_to(root).as_posix()] = "semantic"
    return result


def engine_inventory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    evaluation = root / "evaluation"
    modules = {
        path.relative_to(root).as_posix()
        for path in evaluation.rglob("*.py")
        if "__pycache__" not in path.parts
    }
    module_categories = (
        MODULE_CATEGORIES
        if "evaluation/protocol.py" in modules
        else {
            **{
                path: category
                for path, category in MODULE_CATEGORIES.items()
                if path != "evaluation/protocol.py"
            },
            **ARCHIVED_MODULE_CATEGORIES,
        }
    )
    unknown = sorted(modules - set(module_categories))
    missing = sorted(set(module_categories) - modules)
    if unknown or missing:
        detail = unknown or missing
        label = "unclassified" if unknown else "missing classified"
        raise IdentityError(f"{label} engine input: {', '.join(detail)}")
    schemas = _schema_paths(root)
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
    unknown_json = sorted(discovered_json - set(schemas) - outputs)
    if unknown_json:
        raise IdentityError(f"unclassified engine input: {', '.join(unknown_json)}")
    classified = {**module_categories, **schemas}
    entries = []
    for relative, category in sorted(classified.items()):
        path = root / relative
        if not path.is_file():
            raise IdentityError(f"missing classified engine input: {relative}")
        content = path.read_bytes()
        entries.append(
            {
                "path": relative,
                "category": category,
                "bytes": len(content),
                "sha256": sha256_bytes(content),
            }
        )
    categories = {
        category: canonical_sha256([
            {"path": item["path"], "sha256": item["sha256"]}
            for item in entries
            if item["category"] == category
        ])
        for category in ENGINE_CATEGORIES
    }
    payload = {
        "schema_version": 1,
        "categories": categories,
        "entries": entries,
    }
    return {**payload, "manifest_sha256": canonical_sha256(payload)}


def engine_category_sha256(
    inventory: dict[str, Any],
    category: str,
    *,
    paths: set[str] | None = None,
) -> str:
    if category not in ENGINE_CATEGORIES:
        raise IdentityError(f"unknown engine category: {category}")
    selected = [
        {"path": item["path"], "sha256": item["sha256"]}
        for item in inventory["entries"]
        if item["category"] == category
        and (paths is None or item["path"] in paths)
    ]
    if not selected:
        raise IdentityError(f"empty engine category selection: {category}")
    return canonical_sha256(selected)


def engine_paths_sha256(
    inventory: dict[str, Any],
    paths: set[str],
) -> str:
    by_path = {
        item["path"]: {"path": item["path"], "sha256": item["sha256"]}
        for item in inventory["entries"]
    }
    if not paths or not paths.issubset(by_path):
        raise IdentityError("engine source bundle is incomplete")
    return canonical_sha256([by_path[path] for path in sorted(paths)])


def case_semantic_sha256(
    case: dict[str, Any],
    *,
    shared_semantic_sha256: str,
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
            "shared_semantic_sha256": shared_semantic_sha256,
            "package_semantic_sha256": package_semantic_sha256,
            "model": model,
            "effort": effort,
            "timeout_seconds": timeout,
            "arm": arm,
        }
    )
