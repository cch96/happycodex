from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from evaluation.records import (
    build_product_artifact, canonical_sha256, validate_product_artifact,
)
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


def runtime_from_product_artifact(repo: Path, product: dict[str, Any]) -> str:
    """Validate a product against Git and return its exact frozen Runtime text."""
    validate_product_artifact(product)
    expected = product_artifact_from_git(
        repo, product["source_commit"],
        external_role_config_sha256=product["external_role_config_sha256"],
    )
    if expected != product:
        raise IdentityError("ProductArtifact differs from its exact Git source")
    completed = subprocess.run(
        [
            "git", "-C", str(repo.resolve()), "cat-file", "blob",
            f"{product['source_commit']}:skills/happycodex/SKILL.md",
        ],
        capture_output=True, check=False,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
    )
    if completed.returncode:
        raise IdentityError("exact product Runtime is unavailable")
    try:
        return completed.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IdentityError("exact product Runtime is not UTF-8") from exc


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
    configuration = {"evaluation/manifest-v1.json", "evaluation/provider-fixtures-v1.json", "evaluation/hidden-oracles-v1.json", "evaluation/report-schemas-v1.json"}
    provider_names = {"evaluation/provider.py", "evaluation/identity.py", "evaluation/manifest.py", "evaluation/policy.py"}
    oracle_names = {"evaluation/verify.py", "evaluation/holdout.py", "evaluation/oracle.py"}
    harness_names = {"evaluation/__init__.py", "evaluation/cli.py", "evaluation/host.py", "evaluation/records.py"}
    known = configuration | provider_names | oracle_names | harness_names
    relative = {path: path.relative_to(root).as_posix() for path in files}
    unknown = sorted(value for value in relative.values() if value not in known)
    if unknown:
        raise IdentityError(f"unclassified evaluator inputs: {unknown}")
    provider = [path for path in files if relative[path] in provider_names]
    oracle = [path for path in files if relative[path] in oracle_names]
    harness = [path for path in files if relative[path] in harness_names]
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


def validate_authority_composition(
    records: list[dict[str, Any]], bindings: dict[str, dict[str, Any]] | None,
) -> list[str]:
    authorities = {record["authority_sha256"] for record in records}
    if len(authorities) <= 1:
        return sorted(authorities)
    if type(bindings) is not dict or set(bindings) != authorities:
        raise IdentityError("mixed evaluation authorities lack exact request bindings")
    for authority, binding in bindings.items():
        if type(binding) is not dict or set(binding) != {"proposal", "supplied_authority"}:
            raise IdentityError("evaluation authority binding fields differ")
        proposal, supplied = binding["proposal"], binding["supplied_authority"]
        if (
            type(proposal) is not dict or type(supplied) is not dict
            or set(supplied) != {"scope", "request_sha256", "nonce", "signature"}
            or supplied["scope"] != "evaluation"
            or supplied["request_sha256"] != canonical_sha256(proposal)
            or canonical_sha256(supplied) != authority
        ):
            raise IdentityError("evaluation authority binding identity differs")
        invocations = {(item.get("unit_id"), item.get("invocation_sha256")) for item in proposal.get("invocations", []) if type(item) is dict}
        if any((record["unit_id"], record["invocation_sha256"]) not in invocations for record in records if record["authority_sha256"] == authority):
            raise IdentityError("evaluation authority does not select its Attestation")
    return sorted(authorities)
