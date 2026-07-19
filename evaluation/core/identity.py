from __future__ import annotations

import hashlib
from functools import lru_cache
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
from typing import Any


PACKAGE_PATHS = (".agents", ".codex-plugin", "README.md", "skills")
ENGINE_CATEGORIES = ("semantic", "harness", "artifact")
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
    "evaluation/corpus/contract.py": "semantic",
    "evaluation/corpus/engine.py": "harness",
    "evaluation/holdout/__init__.py": "harness",
    "evaluation/holdout/blind.py": "harness",
    "evaluation/holdout/compare.py": "semantic",
    "evaluation/holdout/engine.py": "harness",
}


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


def package_manifest(plugin: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(plugin).as_posix(): path_record(path)
        for path in selected_package_paths(plugin)
    }


def package_manifest_sha256(plugin: Path) -> str:
    return canonical_sha256(package_manifest(plugin))


def package_content_sha256(plugin: Path) -> str:
    plugin = plugin.resolve()
    records: list[dict[str, Any]] = []
    for path in sorted(selected_package_paths(plugin)):
        relative = path.relative_to(plugin).as_posix()
        if path.is_symlink():
            records.append(
                {"path": relative, "kind": "symlink", "target": os.readlink(path)}
            )
        elif path.is_file():
            content = path.read_bytes()
            records.append(
                {
                    "path": relative,
                    "kind": "file",
                    "bytes": len(content),
                    "sha256": sha256_bytes(content),
                }
            )
    return canonical_sha256(records)


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
    unknown_json = sorted(discovered_json - set(schema_paths) - ledger_outputs)
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
        if item["category"] == category and (paths is None or item["path"] in paths)
    ]
    if not selected:
        raise IdentityError(f"empty engine category selection: {category}")
    return canonical_sha256(selected)


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
