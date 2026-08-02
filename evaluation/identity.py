from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from evaluation.records import build_product_artifact, canonical_sha256
from evaluation.policy import DETERMINISTIC_DOMAINS, MODEL_ROLE_IDS


PACKAGE_PATHS = (".agents", ".codex-plugin", "README.md", "skills")
class IdentityError(ValueError):
    pass


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True,
        check=False, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
    )
    if completed.returncode:
        raise IdentityError(f"Git identity command failed: {' '.join(args)}")
    return completed.stdout.strip()


def _tree_entries(repo: Path, revision: str, paths: tuple[str, ...]) -> list[dict[str, str]]:
    output = _git(repo, "ls-tree", "-r", revision, "--", *paths)
    entries: list[dict[str, str]] = []
    for line in output.splitlines():
        metadata, path = line.split("\t", 1)
        mode, kind, object_id = metadata.split()
        entries.append({"path": path, "mode": mode, "kind": kind, "object": object_id})
    if not entries:
        raise IdentityError("package inventory is empty")
    return entries


def product_artifact_from_git(
    repo: Path, revision: str, *, external_role_config_sha256: str,
) -> dict[str, Any]:
    repo = repo.resolve()
    revision_commit = _git(repo, "rev-parse", f"{revision}^{{commit}}")
    # Evaluator-only commits must not manufacture a new product identity.
    commit = _git(repo, "log", "-1", "--format=%H", revision_commit, "--", *PACKAGE_PATHS)
    tree = _git(repo, "rev-parse", f"{commit}^{{tree}}")
    package_tree = _git(repo, "rev-parse", f"{commit}:skills/happycodex")
    artifact_entries = _tree_entries(repo, commit, PACKAGE_PATHS)
    semantic_entries = [
        entry for entry in artifact_entries
        if entry["path"] == "README.md" or entry["path"].startswith("skills/")
    ]
    return build_product_artifact(
        source_commit=commit, source_tree=tree, package_tree=package_tree,
        package_artifact_sha256=canonical_sha256(artifact_entries),
        package_semantic_sha256=canonical_sha256(semantic_entries),
        external_role_config_sha256=external_role_config_sha256,
    )


def _file_entries(root: Path, paths: list[Path]) -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(paths)
    ]


def evaluator_components(root: Path) -> dict[str, str]:
    root = root.resolve()
    evaluation = root / "evaluation"
    files = [
        path for path in evaluation.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
        and path.suffix in {".py", ".json"}
    ]
    configuration = {"manifest-v1.json", "provider-fixtures-v1.json", "hidden-oracles-v1.json"}
    provider_names = {"provider.py", "identity.py", "manifest.py", "policy.py"}
    oracle_names = {"verify.py", "holdout.py", "oracle.py"}
    harness_names = {"__init__.py", "cli.py", "host.py", "records.py"}
    known = configuration | provider_names | oracle_names | harness_names
    unknown = sorted(path.name for path in files if path.name not in known)
    if unknown:
        raise IdentityError(f"unclassified evaluator inputs: {unknown}")
    provider = [path for path in files if path.name in provider_names]
    oracle = [path for path in files if path.name in oracle_names]
    harness = [path for path in files if path.name in harness_names]
    return {
        "evaluator_bundle_sha256": canonical_sha256(_file_entries(root, files)),
        "provider_component_sha256": canonical_sha256(_file_entries(root, provider)),
        "oracle_component_sha256": canonical_sha256(_file_entries(root, oracle)),
        "harness_component_sha256": canonical_sha256(_file_entries(root, harness)),
    }


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentityError(f"cannot load JSON: {path}") from exc
    if type(value) is not dict:
        raise IdentityError("JSON record must be an object")
    return value
