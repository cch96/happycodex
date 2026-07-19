from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


PACKAGE_PATHS = (".agents", ".codex-plugin", "README.md", "skills")
ENGINE_CATEGORIES = ("semantic", "harness", "artifact")
MODULE_CATEGORIES = {
    "evaluation/__init__.py": "harness",
    "evaluation/cli.py": "harness",
    "evaluation/core/__init__.py": "harness",
    "evaluation/core/identity.py": "harness",
    "evaluation/core/impact.py": "artifact",
    "evaluation/core/receipt.py": "artifact",
    "evaluation/corpus/__init__.py": "harness",
    "evaluation/corpus/contract.py": "semantic",
    "evaluation/corpus/engine.py": "harness",
    "evaluation/holdout/__init__.py": "harness",
    "evaluation/holdout/blind.py": "harness",
    "evaluation/holdout/compare.py": "harness",
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
