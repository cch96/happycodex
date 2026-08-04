from __future__ import annotations
import hashlib
import json
from pathlib import Path
import stat
import subprocess
from typing import Any
from evaluation.records import (
    build_product_artifact, canonical_sha256, validate_product_artifact,
)
from evaluation.policy import DETERMINISTIC_DOMAINS, MODEL_ROLE_IDS
PACKAGE_PATHS = (".agents", ".codex-plugin", "README.md", "skills")
REVIEW_PATHS = (".agents", ".codex-plugin", "README.md", "evaluation", "skills", "tests")
PRIVATE_ORACLE = "evaluation/hidden-oracles-v1.json"
class IdentityError(ValueError):
    pass
def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True,
        check=False, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_OPTIONAL_LOCKS": "0"},
    )
    if completed.returncode:
        raise IdentityError(f"Git identity command failed: {' '.join(args)}")
    return completed.stdout.strip()
def _git_bytes(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=False,
        env={
            "PATH": "/usr/bin:/bin", "LC_ALL": "C",
            "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
        },
    )
    if completed.returncode:
        raise IdentityError(f"Git identity command failed: {' '.join(args)}")
    return completed.stdout
def _git_blob_sha(body: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
def _source_inventory(repo: Path, commit: str) -> list[dict[str, Any]]:
    entries = []
    for row in _git_bytes(repo, "ls-tree", "-r", "-z", commit).split(b"\0"):
        if not row:
            continue
        try:
            metadata, raw_path = row.split(b"\t", 1)
            mode, kind, object_id = metadata.decode("ascii").split()
            path = raw_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise IdentityError("frozen source inventory is malformed") from exc
        if kind != "blob" or mode not in {"100644", "100755"} or not path or path.startswith("/") or ".." in Path(path).parts:
            raise IdentityError("frozen source inventory is outside the closed blob subset")
        body = _git_bytes(repo, "cat-file", "blob", object_id)
        entries.append({
            "path": path, "git_mode": mode, "git_object": object_id,
            "sha256": hashlib.sha256(body).hexdigest(), "size_bytes": len(body),
        })
    if not entries or entries != sorted(entries, key=lambda item: item["path"]):
        raise IdentityError("frozen source inventory is empty or unsorted")
    return entries
def _review_included(path: str) -> bool:
    return path != PRIVATE_ORACLE and any(
        path == prefix or path.startswith(prefix + "/") for prefix in REVIEW_PATHS
    )
def _named_source_identity(repo: Path, identity: dict[str, Any]) -> tuple[str, str, str, str]:
    fields = {
        "baseline_ref", "baseline_commit", "baseline_tree", "source_ref",
        "source_commit", "source_tree", "package_tree",
        "package_artifact_sha256", "package_semantic_sha256",
    }
    if type(identity) is not dict or set(identity) != fields:
        raise IdentityError("frozen source identity fields differ")
    resolved = []
    for label in ("baseline", "source"):
        ref = identity[f"{label}_ref"]
        if type(ref) is not str or not ref.startswith("refs/"):
            raise IdentityError("frozen source ref is not explicit")
        _git(repo, "show-ref", "--verify", ref)
        commit = _git(repo, "rev-parse", f"{ref}^{{commit}}")
        tree = _git(repo, "rev-parse", f"{commit}^{{tree}}")
        if commit != identity[f"{label}_commit"] or tree != identity[f"{label}_tree"]:
            raise IdentityError("frozen source named ref differs")
        resolved.extend((commit, tree))
    baseline, baseline_tree, source, source_tree = resolved
    if baseline == source:
        raise IdentityError("frozen source is not a strict successor")
    completed = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", baseline, source],
        capture_output=True, check=False, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
    )
    if completed.returncode:
        raise IdentityError("frozen source is not a strict named-ref descendant")
    return baseline, baseline_tree, source, source_tree
def _private_oracle_metadata(path: Path) -> tuple[dict[str, Any], bytes]:
    path = path.absolute()
    if path.is_symlink() or not path.is_file() or path.name != "hidden-oracles-v1.json" or path.parent.name != "evaluation":
        raise IdentityError("private hidden oracle path differs")
    body = path.read_bytes()
    return {
        "path": "evaluation/hidden-oracles-v1.json", "git_mode": "100644",
        "git_object": _git_blob_sha(body), "sha256": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
    }, body
def _reject_oracle_diff(diff: bytes, oracle: bytes) -> None:
    private_path = b"evaluation/hidden-oracles-v1.json"
    old, new, in_hunk = bytearray(), bytearray(), False
    def reject_payload() -> None:
        if oracle in old or oracle in new:
            raise IdentityError("hidden oracle content reached exact-final diff")
    for line in diff.splitlines(keepends=True):
        if line.startswith(b"diff --git "):
            reject_payload(); old.clear(); new.clear(); in_hunk = False
        if line.startswith((b"diff --git ", b"--- ", b"+++ ", b"rename from ", b"rename to ", b"copy from ", b"copy to ", b"Binary files ")) and private_path in line:
            raise IdentityError("hidden oracle file reached exact-final diff")
        if line.startswith(b"@@"):
            in_hunk = True
        elif in_hunk and line.startswith(b" "):
            old.extend(line[1:]); new.extend(line[1:])
        elif in_hunk and line.startswith(b"-"):
            old.extend(line[1:])
        elif in_hunk and line.startswith(b"+"):
            new.extend(line[1:])
    reject_payload()
    if oracle in diff:
        raise IdentityError("hidden oracle content reached exact-final diff")
def exact_final_source_identity(
    root: Path, private_oracle_path: Path, *, source_repo: Path,
    source_identity: dict[str, Any], evaluator_identity: dict[str, str],
    external_role_config_sha256: str,
) -> str:
    """Validate the complete synthetic exact-final projection and source lineage."""
    if not (root / ".git").is_dir() or (root / ".git").is_symlink():
        raise IdentityError("exact-final Git metadata is not self-contained")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching"):
        raise IdentityError("exact-final source is not one clean synthetic commit")
    if Path(_git(root, "rev-parse", "--show-toplevel")) != root:
        raise IdentityError("exact-final Git root differs")
    head = _git(root, "rev-parse", "HEAD")
    refs = _git(root, "for-each-ref", "--format=%(refname)").splitlines()
    if _git(root, "rev-list", "--all").splitlines() != [head] or refs != ["refs/heads/exact-final"] or _git(root, "symbolic-ref", "-q", "HEAD") != refs[0]:
        raise IdentityError("exact-final source is not one clean synthetic commit")
    if _git(root, "remote") or _git(root, "rev-parse", "--show-object-format") != "sha1":
        raise IdentityError("exact-final Git repository differs")
    config = [line.split(None, 1) for line in _git(root, "config", "--local", "--get-regexp", ".*").splitlines()]
    if config != [["core.repositoryformatversion", "0"], ["core.filemode", "true"], ["core.bare", "false"], ["core.logallrefupdates", "true"]]:
        raise IdentityError("exact-final Git config differs")
    if (root / ".git/objects/info/alternates").exists() or _git(root, "fsck", "--full", "--no-reflogs", "--unreachable"):
        raise IdentityError("exact-final Git objects are not self-contained")
    if set(_git(root, "reflog", "--all", "--format=%H").splitlines()) != {head}:
        raise IdentityError("exact-final Git reflog differs")
    tracked = sorted(_git(root, "ls-files").splitlines())
    visible = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() and ".git" not in path.relative_to(root).parts)
    support = {"EXACT_FINAL_DIFF.patch", "EXACT_FINAL_SOURCE_MANIFEST.json"}
    if visible != tracked or not support.issubset(tracked):
        raise IdentityError("exact-final support files are not fully tracked")
    hidden = PRIVATE_ORACLE
    if hidden in tracked or (root / hidden).exists():
        raise IdentityError("hidden oracle reached exact-final workspace")
    manifest_path, diff_path = root / "EXACT_FINAL_SOURCE_MANIFEST.json", root / "EXACT_FINAL_DIFF.patch"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentityError("exact-final source manifest is invalid") from exc
    fields = {"schema_version", "source", "product", "evaluator", "external_role_config_sha256", "projection", "private_exclusion", "aggregate_diff", "support_files"}
    if type(manifest) is not dict or set(manifest) != fields or manifest.get("schema_version") != 1:
        raise IdentityError("exact-final source manifest fields differ")
    expected_private, oracle = _private_oracle_metadata(private_oracle_path)
    if manifest.get("private_exclusion") != expected_private:
        raise IdentityError("hidden oracle private exclusion differs")
    source_repo = source_repo.resolve()
    if not (source_repo / ".git").exists():
        raise IdentityError("frozen source repository differs")
    baseline, baseline_tree, commit, tree = _named_source_identity(source_repo, source_identity)
    product_fields = {"package_tree", "package_artifact_sha256", "package_semantic_sha256"}
    product = {key: source_identity[key] for key in product_fields}
    expected_source = {
        "baseline": {"ref": source_identity["baseline_ref"], "commit": baseline, "tree": baseline_tree},
        "source": {"ref": source_identity["source_ref"], "commit": commit, "tree": tree},
    }
    if manifest["source"] != expected_source or manifest["product"] != product:
        raise IdentityError("frozen source lineage or product identity differs")
    derived_product = product_artifact_from_git(source_repo, commit)
    if any(derived_product[field] != product[field] for field in product):
        raise IdentityError("frozen source package identity differs")
    derived_evaluator = evaluator_components_from_git(source_repo, commit)
    if manifest["evaluator"] != derived_evaluator or evaluator_identity != derived_evaluator:
        raise IdentityError("frozen evaluator identity differs")
    if manifest["external_role_config_sha256"] != external_role_config_sha256:
        raise IdentityError("frozen external role config identity differs")
    inventory, projection = _source_inventory(source_repo, commit), manifest["projection"]
    if type(projection) is not dict or set(projection) != {"included", "excluded", "file_count"}:
        raise IdentityError("exact-final projection fields differ")
    included, excluded = projection["included"], projection["excluded"]
    expected_included = [item for item in inventory if _review_included(item["path"])]
    expected_excluded = [item for item in inventory if not _review_included(item["path"])]
    if included != expected_included or excluded != expected_excluded or projection["file_count"] != len(inventory) or expected_private not in excluded:
        raise IdentityError("exact-final included/excluded partition differs")
    support_files = ["EXACT_FINAL_DIFF.patch", "EXACT_FINAL_SOURCE_MANIFEST.json"]
    if manifest["support_files"] != support_files:
        raise IdentityError("exact-final support file inventory differs")
    if tracked != sorted([item["path"] for item in included] + support_files):
        raise IdentityError("exact-final tracked projection differs from manifest")
    for expected in included:
        relative, path = expected["path"], root / expected["path"]
        if path.is_symlink() or not path.is_file():
            raise IdentityError("exact-final included source is not a regular file")
        body = path.read_bytes()
        if oracle in body:
            raise IdentityError("hidden oracle content reached exact-final included source")
        row = _git(root, "ls-tree", "HEAD", "--", relative)
        try:
            mode, kind, object_id = row.split("\t", 1)[0].split()
        except ValueError as exc:
            raise IdentityError("exact-final included source inventory differs") from exc
        actual = {"path": relative, "git_mode": mode, "git_object": object_id, "sha256": hashlib.sha256(body).hexdigest(), "size_bytes": len(body)}
        if kind != "blob" or actual != expected:
            raise IdentityError("exact-final included source bytes differ")
    if any((root / item["path"]).exists() for item in excluded):
        raise IdentityError("exact-final excluded source reached reviewer projection")
    diff = diff_path.read_bytes()
    expected_diff = {"path": diff_path.name, "git_mode": "100644", "git_object": _git_blob_sha(diff), "sha256": hashlib.sha256(diff).hexdigest(), "size_bytes": len(diff)}
    if manifest.get("aggregate_diff") != expected_diff:
        raise IdentityError("exact-final aggregate diff identity differs")
    _reject_oracle_diff(diff, oracle)
    source_diff = _git_bytes(
        source_repo, "diff", "--binary", "--full-index", "--no-renames", "--no-ext-diff", "--no-textconv",
        baseline, commit, "--", *REVIEW_PATHS, f":(exclude){PRIVATE_ORACLE}",
    )
    if diff != source_diff:
        raise IdentityError("exact-final aggregate diff differs from source commits")
    entries = []
    for relative in tracked:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise IdentityError("exact-final tracked source is not a regular file")
        body = path.read_bytes()
        entries.append({"path": relative, "mode": f"{stat.S_IMODE(path.stat().st_mode):04o}", "sha256": hashlib.sha256(body).hexdigest(), "size_bytes": len(body)})
    return canonical_sha256({"synthetic_tree": _git(root, "rev-parse", "HEAD^{tree}"), "manifest": manifest, "files": entries})
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
def product_artifact_from_git(repo: Path, revision: str) -> dict[str, Any]:
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
    )
def runtime_from_product_artifact(repo: Path, product: dict[str, Any]) -> str:
    """Validate a product against Git and return its exact frozen Runtime text."""
    validate_product_artifact(product)
    expected = product_artifact_from_git(repo, product["source_commit"])
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
def _component_digests(files: dict[str, bytes]) -> dict[str, str]:
    configuration = {"evaluation/manifest-v1.json", "evaluation/provider-fixtures-v1.json", "evaluation/hidden-oracles-v1.json", "evaluation/report-schemas-v1.json"}
    provider_names = {"evaluation/provider.py", "evaluation/identity.py", "evaluation/manifest.py", "evaluation/policy.py"}
    oracle_names = {"evaluation/verify.py", "evaluation/holdout.py", "evaluation/oracle.py"}
    harness_names = {"evaluation/__init__.py", "evaluation/cli.py", "evaluation/host.py", "evaluation/records.py"}
    known = configuration | provider_names | oracle_names | harness_names
    unknown = sorted(set(files) - known)
    if unknown:
        raise IdentityError(f"unclassified evaluator inputs: {unknown}")
    def entries(names: set[str]) -> list[dict[str, Any]]:
        return [
            {"path": path, "bytes": len(files[path]), "sha256": hashlib.sha256(files[path]).hexdigest()}
            for path in sorted(set(files) & names)
        ]
    return {
        "evaluator_bundle_sha256": canonical_sha256(entries(set(files))),
        "provider_component_sha256": canonical_sha256(entries(provider_names)),
        "oracle_component_sha256": canonical_sha256(entries(oracle_names)),
        "harness_component_sha256": canonical_sha256(entries(harness_names)),
    }
def evaluator_components(root: Path) -> dict[str, str]:
    root = root.resolve()
    files = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in (root / "evaluation").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix in {".py", ".json"}
    }
    return _component_digests(files)
def evaluator_components_from_git(repo: Path, commit: str) -> dict[str, str]:
    inventory = _source_inventory(repo.resolve(), commit)
    files = {
        item["path"]: _git_bytes(repo, "cat-file", "blob", item["git_object"])
        for item in inventory
        if item["path"].startswith("evaluation/") and Path(item["path"]).suffix in {".py", ".json"}
    }
    return _component_digests(files)
def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentityError(f"cannot load JSON: {path}") from exc
    if type(value) is not dict:
        raise IdentityError("JSON record must be an object")
    return value
