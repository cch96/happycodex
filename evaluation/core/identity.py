from __future__ import annotations

import hashlib
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig
from typing import Any


PACKAGE_PATHS = (".agents", ".codex-plugin", "README.md", "skills")
ENGINE_CATEGORIES = ("semantic", "harness", "artifact")
CORPUS_SEMANTIC_PATHS = frozenset(
    {
        "evaluation/corpus/engine.py",
        "evaluation/semantic/__init__.py",
        "evaluation/semantic/types.py",
        "evaluation/semantic/canonical.py",
        "evaluation/semantic/parse.py",
        "evaluation/semantic/decide.py",
    }
)
MODULE_CATEGORIES = {
    "evaluation/__init__.py": "harness",
    "evaluation/cli.py": "harness",
    "evaluation/live.py": "harness",
    "evaluation/core/__init__.py": "harness",
    "evaluation/core/identity.py": "harness",
    "evaluation/core/impact.py": "harness",
    "evaluation/core/ledger.py": "harness",
    "evaluation/core/receipt.py": "artifact",
    "evaluation/corpus/__init__.py": "harness",
    "evaluation/corpus/engine.py": "semantic",
    "evaluation/holdout/__init__.py": "harness",
    "evaluation/holdout/blind.py": "harness",
    "evaluation/holdout/compare.py": "semantic",
    "evaluation/holdout/engine.py": "harness",
    "evaluation/semantic/__init__.py": "semantic",
    "evaluation/semantic/canonical.py": "semantic",
    "evaluation/semantic/decide.py": "semantic",
    "evaluation/semantic/parse.py": "semantic",
    "evaluation/semantic/types.py": "semantic",
}
INVOCATION_PROFILE_FIELDS = frozenset(
    {
        "provider",
        "binary",
        "model",
        "effort",
        "timeout_seconds",
        "arm",
        "tools",
        "network",
        "mcp",
        "hooks",
        "session",
    }
)
_PROFILE_BINARY_FIELDS = frozenset({"command", "identity_sha256"})
_PROFILE_TOOLS_FIELDS = frozenset({"allowed", "event_item_types"})
_PROFILE_SESSION_FIELDS = frozenset({"mode", "history"})
_TOOL_EVENT_TYPES = {
    "collaboration": "collab_tool_call",
    "command_execution": "command_execution",
    "todo": "todo_list",
    "web_search": "web_search",
}
_SESSION_MODES = frozenset({"fresh", "fresh-with-bounded-resume"})
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
PUBLIC_040_PACKAGE_ARTIFACT_SHA256 = (
    "ace7f39fd61341e5d4b1bc3b268fd89a1562acaaacb80d7456c2bb97fb9c497e"
)
PUBLIC_040_PACKAGE_SEMANTIC_SHA256 = (
    "c5030e99dd7cd1681148c069775671c5720bb8dd366930ff90f61cbc54cdfc05"
)
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


def identity_match_values(value: Any) -> frozenset[str]:
    """Return the one exact nonblank identity admitted by generation 6."""
    if type(value) is not str or not value.strip():
        return frozenset()
    return frozenset({value})


def is_nonblank_identity(value: Any) -> bool:
    return bool(identity_match_values(value))


def classification_identity_keys(item: Any) -> frozenset[str]:
    if not isinstance(item, dict):
        return frozenset()
    identity = item.get("identity")
    if isinstance(identity, str):
        return identity_match_values(identity)
    digest = item.get("identity_sha256")
    return frozenset({digest}) if isinstance(digest, str) else frozenset()


def classifications_share_identity(left: Any, right: Any) -> bool:
    return bool(
        classification_identity_keys(left) & classification_identity_keys(right)
    )


def classification_identity_failures(items: Any, *, label: str) -> list[str]:
    if not isinstance(items, list):
        return [f"invalid {label} classifications"]
    failures: list[str] = []
    seen: set[str] = set()
    for item in items:
        keys = classification_identity_keys(item)
        nonblank = isinstance(item, dict) and (
            is_nonblank_identity(item.get("identity"))
            or item.get("identity_nonblank") is True
        )
        if not nonblank or len(keys) != 1:
            failures.append(f"blank {label} identity")
            continue
        identity = next(iter(keys))
        if identity in seen:
            failures.append(f"duplicate {label} identity")
        seen.add(identity)
    return failures


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
    if (
        not isinstance(markers, list)
        or not all(isinstance(marker, str) and marker for marker in markers)
        or len(markers) != len(set(markers))
        or not isinstance(tests, dict)
    ):
        return False
    test_markers = tests.get("marker_ids")
    failed = tests.get("failed")
    accepted = tests.get("accepted_failures")
    return (
        isinstance(test_markers, list)
        and all(isinstance(marker, str) and marker for marker in test_markers)
        and len(test_markers) == len(set(test_markers))
        and set(test_markers).issubset(markers)
        and type(failed) is int
        and type(accepted) is int
        and 0 <= accepted <= failed
    )


class IdentityError(ValueError):
    """The engine cannot classify an input without weakening invalidation."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def validate_invocation_profile(
    value: Any,
    *,
    require_bound_binary: bool = False,
) -> dict[str, Any]:
    """Validate one exact administrative invocation identity."""
    if not isinstance(value, dict) or set(value) != INVOCATION_PROFILE_FIELDS:
        raise IdentityError("invalid invocation profile envelope")
    binary = value["binary"]
    tools = value["tools"]
    session = value["session"]
    if not isinstance(binary, dict) or set(binary) != _PROFILE_BINARY_FIELDS:
        raise IdentityError("invalid invocation binary profile")
    if binary.get("command") != "codex":
        raise IdentityError("invalid invocation binary command")
    binary_digest = binary.get("identity_sha256")
    if binary_digest is not None and (
        type(binary_digest) is not str
        or re.fullmatch(r"[0-9a-f]{64}", binary_digest) is None
    ):
        raise IdentityError("invalid invocation binary identity")
    if require_bound_binary and binary_digest is None:
        raise IdentityError("live invocation binary identity is unbound")
    if not isinstance(tools, dict) or set(tools) != _PROFILE_TOOLS_FIELDS:
        raise IdentityError("invalid invocation tool profile")
    allowed = tools.get("allowed")
    if (
        not isinstance(allowed, list)
        or allowed != sorted(set(allowed))
        or any(item not in _TOOL_EVENT_TYPES for item in allowed)
    ):
        raise IdentityError("invalid invocation tool allowlist")
    expected_events = sorted(_TOOL_EVENT_TYPES[item] for item in allowed)
    if tools.get("event_item_types") != expected_events:
        raise IdentityError("invocation event types diverge from allowed tools")
    if value.get("network") not in {"disabled", "enabled"}:
        raise IdentityError("invalid invocation network profile")
    if "web_search" in allowed and value["network"] != "enabled":
        raise IdentityError("web search requires enabled invocation network")
    if value.get("mcp") not in {"disabled", "enabled"}:
        raise IdentityError("invalid invocation MCP profile")
    if value.get("hooks") not in {"disabled", "enabled"}:
        raise IdentityError("invalid invocation hook profile")
    if not isinstance(session, dict) or set(session) != _PROFILE_SESSION_FIELDS:
        raise IdentityError("invalid invocation session profile")
    if session.get("mode") not in _SESSION_MODES or session.get("history") != "isolated":
        raise IdentityError("invalid invocation session profile")
    for field in ("provider", "model", "effort", "arm"):
        if type(value.get(field)) is not str or not value[field]:
            raise IdentityError(f"invalid invocation profile field: {field}")
    timeout = value.get("timeout_seconds")
    if type(timeout) is not int or timeout <= 0:
        raise IdentityError("invalid invocation profile field: timeout_seconds")
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
    profile = {
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
            "allowed": sorted(allowed_tools),
            "event_item_types": sorted(
                _TOOL_EVENT_TYPES[item] for item in allowed_tools
            ),
        },
        "network": network,
        "mcp": mcp,
        "hooks": hooks,
        "session": {
            "mode": session_mode,
            "history": "isolated",
        },
    }
    return validate_invocation_profile(profile)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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
    """Reconstruct the repository's private package modes from Git mode classes."""
    for path in selected_package_paths(plugin.resolve()):
        if path.is_symlink():
            continue
        if path.is_dir():
            path.chmod(0o700)
        elif path.is_file():
            path.chmod(0o700 if path.stat().st_mode & 0o111 else 0o600)


def package_manifest(plugin: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(plugin).as_posix(): path_record(path)
        for path in selected_package_paths(plugin)
    }


def package_manifest_sha256(plugin: Path) -> str:
    return canonical_sha256(package_manifest(plugin))


def _skill_semantic_manifest(plugin: Path) -> dict[str, dict[str, Any]]:
    root = plugin / "skills"
    paths = [root, *root.rglob("*")]
    return {
        path.relative_to(plugin).as_posix(): path_record(path) for path in sorted(paths)
    }


def package_identities(plugin: Path) -> dict[str, str]:
    plugin = plugin.resolve()
    manifest = read_json(plugin / ".codex-plugin" / "plugin.json")
    if not isinstance(manifest, dict):
        raise IdentityError("plugin manifest must be an object")
    semantic_manifest = dict(manifest)
    semantic_manifest.pop("version", None)
    semantic_payload = {
        "schema_version": 1,
        "plugin_manifest": semantic_manifest,
        "marketplace": read_json(plugin / ".agents" / "plugins" / "marketplace.json"),
        "skills": _skill_semantic_manifest(plugin),
    }
    return {
        "semantic_sha256": canonical_sha256(semantic_payload),
        "artifact_sha256": package_manifest_sha256(plugin),
    }


def _executable_identity(name: str, *, executable: str | None = None) -> dict[str, str]:
    raw_path = executable or shutil.which(name)
    if not raw_path:
        raise IdentityError(f"required certification tool is unavailable: {name}")
    path = Path(raw_path).resolve()
    if not path.is_file():
        raise IdentityError(f"invalid certification tool path: {name}")
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
    version = (completed.stdout or completed.stderr).strip().splitlines()
    if completed.returncode or not version:
        raise IdentityError(f"cannot identify certification tool: {name}")
    return {
        "path": str(path),
        "sha256": sha256_bytes(path.read_bytes()),
        "version": version[0],
    }


@lru_cache(maxsize=1)
def _python_stdlib_identity() -> dict[str, Any]:
    raw_root = sysconfig.get_paths().get("stdlib")
    if not raw_root:
        raise IdentityError("cannot locate the Python standard library")
    root = Path(raw_root).resolve()
    if not root.is_dir():
        raise IdentityError("invalid Python standard-library path")
    excluded = {"__pycache__", "site-packages", "dist-packages"}
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if excluded.intersection(relative.parts) or path.suffix == ".pyc":
            continue
        if path.is_file():
            content = path.read_bytes()
            records.append(
                {
                    "path": relative.as_posix(),
                    "bytes": len(content),
                    "sha256": sha256_bytes(content),
                }
            )
    if not records:
        raise IdentityError("empty Python standard-library identity")
    return {
        "stdlib_sha256": canonical_sha256(records),
        "stdlib_file_count": len(records),
    }


@lru_cache(maxsize=1)
def _python_shared_library_identity() -> dict[str, Any]:
    raw_root = sysconfig.get_paths().get("stdlib")
    ldd = shutil.which("ldd")
    if not raw_root or not ldd:
        raise IdentityError("cannot identify Python shared libraries")
    root = Path(raw_root).resolve()
    excluded = {"__pycache__", "site-packages", "dist-packages"}
    targets = {Path(sys.executable).resolve()}
    for path in root.rglob("*.so*"):
        relative = path.relative_to(root)
        if not excluded.intersection(relative.parts) and path.is_file():
            targets.add(path.resolve())
    completed = subprocess.run(
        [ldd, *(str(path) for path in sorted(targets))],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "LC_ALL": "C"},
    )
    if completed.returncode:
        raise IdentityError("cannot resolve Python shared-library dependencies")
    libraries: set[Path] = set()
    for line in completed.stdout.splitlines():
        value = line.strip().split(" => ", maxsplit=1)[-1].split(" (", maxsplit=1)[0]
        if value.endswith(":"):
            continue
        if value.startswith("/"):
            path = Path(value)
            if not path.is_file():
                raise IdentityError(f"unreadable Python shared library: {path}")
            libraries.add(path.resolve())
    if not libraries:
        raise IdentityError("empty Python shared-library identity")
    resolver = Path(ldd).resolve()
    records = [
        {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_bytes(path.read_bytes()),
        }
        for path in sorted(libraries)
    ]
    return {
        "shared_libraries_sha256": canonical_sha256(records),
        "shared_library_count": len(records),
        "shared_library_resolver_sha256": sha256_bytes(resolver.read_bytes()),
    }


def _python_identity() -> dict[str, Any]:
    return {
        **_executable_identity("python", executable=sys.executable),
        **_python_stdlib_identity(),
        **_python_shared_library_identity(),
    }


def toolchain_identity() -> dict[str, dict[str, Any]]:
    return {
        "python": _python_identity(),
        "codex": _executable_identity("codex"),
        "git": _executable_identity("git"),
        "rg": _executable_identity("rg"),
    }


def _schema_paths(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
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
    discovered_modules = {
        path.relative_to(root).as_posix()
        for path in evaluation.rglob("*.py")
        if "__pycache__" not in path.parts
    }
    expected_modules = set(MODULE_CATEGORIES)
    unknown = sorted(discovered_modules - expected_modules)
    missing = sorted(expected_modules - discovered_modules)
    if unknown:
        raise IdentityError(f"unclassified engine input: {', '.join(unknown)}")
    if missing:
        raise IdentityError(f"missing classified engine input: {', '.join(missing)}")

    classified = dict(MODULE_CATEGORIES)
    schema_paths = _schema_paths(root)
    discovered_json = {
        path.relative_to(root).as_posix()
        for path in evaluation.rglob("*.json")
        if "__pycache__" not in path.parts
    }
    ledger_outputs = {"evaluation/results/current.json"}
    evidence_outputs = {
        relative
        for relative in discovered_json
        if Path(relative).parts[:3] == ("evaluation", "results", "evidence")
    }
    unknown_json = sorted(
        discovered_json - set(schema_paths) - ledger_outputs - evidence_outputs
    )
    if unknown_json:
        raise IdentityError(f"unclassified engine input: {', '.join(unknown_json)}")
    classified.update(schema_paths)
    entries: list[dict[str, Any]] = []
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

    category_digests = {
        category: canonical_sha256(
            [
                {"path": item["path"], "sha256": item["sha256"]}
                for item in entries
                if item["category"] == category
            ]
        )
        for category in ENGINE_CATEGORIES
    }
    return {
        "schema_version": 1,
        "categories": category_digests,
        "entries": entries,
        "manifest_sha256": canonical_sha256(
            {
                "schema_version": 1,
                "categories": category_digests,
                "entries": entries,
            }
        ),
    }


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
    """Bind an exact cross-category source bundle without reclassifying inputs."""
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
