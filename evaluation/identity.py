"""Consumer product identities and readable immutable review projections."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
from typing import Any, Iterable

from evaluation.canonical import ContractError, canonical_sha256, exact, sha256, text
from evaluation.policy import (
    PRIVATE_ORACLE_PATH,
    PROJECTION_NAMES,
    SCHEMA_VERSION,
)
from evaluation.records import (
    build_product_artifact,
    validate_product_artifact,
)

PRODUCT_STATIC_PATHS = (
    ".agents/plugins/marketplace.json",
    ".codex-plugin/plugin.json",
    "README.en.md",
    "README.md",
)
PUBLIC_DOCS = ("README.en.md", "README.md")
PROVIDER_GUIDANCE = (
    "skills/happycodex/SKILL.md",
    "skills/happycodex/references/execplan.md",
)
DEFAULT_HOOK_PATHS = ("hooks/hooks.json", "hooks/session_firewall.py")
EVALUATOR_COMPONENT_PATHS = {
    "provider_input": (
        "evaluation/canonical.py",
        "evaluation/manifest-v1.json",
        "evaluation/manifest.py",
        "evaluation/policy.py",
        "evaluation/provider-fixtures-v1.json",
        "evaluation/provider.py",
        "evaluation/report-schemas-v1.json",
        "evaluation/schemas.py",
    ),
    "oracle": (
        "evaluation/canonical.py",
        "evaluation/hidden-oracles-v1.json",
        "evaluation/holdout.py",
        "evaluation/oracle.py",
        "evaluation/policy.py",
    ),
    "harness": (
        "evaluation/__init__.py",
        "evaluation/canonical.py",
        "evaluation/cli.py",
        "evaluation/host.py",
        "evaluation/identity.py",
        "evaluation/policy.py",
        "evaluation/records.py",
        "evaluation/verify.py",
    ),
}

class IdentityError(ContractError):
    pass

def _safe_relative(value: str) -> str:
    text(value, "path")
    parsed = PurePosixPath(value)
    if (
        value.startswith("/")
        or "\\" in value
        or ".." in parsed.parts
        or value != parsed.as_posix()
        or value == "."
    ):
        raise IdentityError("path escapes root")
    return value

def _mode(path: Path) -> str:
    return "100755" if stat.S_IMODE(path.stat().st_mode) & 0o111 else "100644"

def _entry(root: Path, relative: str) -> dict[str, Any]:
    relative = _safe_relative(relative)
    path = root / relative
    if not path.exists():
        return {
            "path": relative,
            "mode": "000000",
            "state": "absent",
            "sha256": hashlib.sha256(b"").hexdigest(),
            "size_bytes": 0,
        }
    if path.is_symlink() or not path.is_file():
        raise IdentityError(f"projection input is not a regular file: {relative}")
    body = path.read_bytes()
    return {
        "path": relative,
        "mode": _mode(path),
        "state": "present",
        "sha256": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
    }

def projection(root: Path, paths: Iterable[str]) -> dict[str, Any]:
    entries = [_entry(root, path) for path in sorted(set(paths))]
    if not entries:
        raise IdentityError("consumer projection is empty")
    return {
        "entries": entries,
        "projection_sha256": canonical_sha256(entries),
    }

def _load_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise IdentityError(f"{label} is missing or redirected")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityError(f"{label} is invalid JSON") from exc
    if type(value) is not dict:
        raise IdentityError(f"{label} is not an object")
    return value

def _no_redirect(root: Path, relative: str, label: str) -> None:
    current = root.resolve(strict=True)
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink():
            raise IdentityError(f"{label} contains a redirect")

def _resolve_relative(root: Path, raw: Any, label: str) -> Path:
    if type(raw) is not str or not raw or "\\" in raw:
        raise IdentityError(f"{label} path is invalid")
    parsed = PurePosixPath(raw)
    if parsed.is_absolute() or ".." in parsed.parts:
        raise IdentityError(f"{label} path escapes root")
    normalized = parsed.as_posix()
    relative = "." if normalized == "." else _safe_relative(normalized)
    try:
        resolved = (root / relative).resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise IdentityError(f"{label} path escapes or is missing") from exc
    _no_redirect(root, relative, label)
    return resolved

def _resolve_plugin(root: Path) -> tuple[Path, Path, Path]:
    marketplace_path = root / ".agents/plugins/marketplace.json"
    _no_redirect(root, ".agents/plugins/marketplace.json", "marketplace manifest")
    marketplace = _load_json(marketplace_path, "marketplace manifest")
    if (
        set(marketplace) != {"name", "interface", "plugins"}
        or marketplace["name"] != "happycodex"
        or marketplace["interface"] != {"displayName": "HappyCodex"}
        or type(marketplace["plugins"]) is not list
    ):
        raise IdentityError("marketplace contract differs")
    matches = [
        item
        for item in marketplace["plugins"]
        if type(item) is dict and item.get("name") == "happycodex"
    ]
    if len(matches) != 1 or len(marketplace["plugins"]) != 1:
        raise IdentityError("marketplace must contain one happycodex plugin")
    plugin = matches[0]
    if set(plugin) != {"name", "source", "policy", "category"}:
        raise IdentityError("marketplace plugin fields differ")
    if (
        plugin["category"] != "Productivity"
        or plugin["policy"]
        != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
        or type(plugin["source"]) is not dict
        or set(plugin["source"]) != {"source", "path"}
        or plugin["source"]["source"] != "local"
    ):
        raise IdentityError("marketplace plugin contract differs")
    plugin_root = _resolve_relative(root, plugin["source"]["path"], "plugin source")
    if plugin_root != root.resolve(strict=True) or not plugin_root.is_dir():
        raise IdentityError("plugin source does not resolve to the distribution root")
    manifest_path = plugin_root / ".codex-plugin/plugin.json"
    _no_redirect(plugin_root, ".codex-plugin/plugin.json", "plugin manifest")
    manifest = _load_json(manifest_path, "plugin manifest")
    required = {
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "skills",
        "interface",
    }
    if set(manifest) != required or manifest["name"] != "happycodex":
        raise IdentityError("plugin manifest contract differs")
    skills_root = _resolve_relative(plugin_root, manifest["skills"], "plugin skills")
    if not skills_root.is_dir() or skills_root.is_symlink():
        raise IdentityError("plugin skills root is not a regular directory")
    return plugin_root, manifest_path, skills_root

def _regular_inventory(distribution_root: Path, directory: Path) -> list[str]:
    paths = []
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise IdentityError("product inventory contains a symlink")
        if path.is_file():
            if not stat.S_ISREG(path.stat().st_mode):
                raise IdentityError("product inventory contains a non-regular file")
            paths.append(path.relative_to(distribution_root).as_posix())
        elif not path.is_dir():
            raise IdentityError("product inventory contains an unclassified input")
    return sorted(paths)

def _hook_inventory(distribution_root: Path, plugin_root: Path) -> list[str]:
    directory = plugin_root / "hooks"
    try:
        mode = directory.lstat().st_mode
    except FileNotFoundError:
        return list(DEFAULT_HOOK_PATHS)
    except OSError as exc:
        raise IdentityError("plugin hooks root cannot be classified") from exc
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise IdentityError("plugin hooks root is redirected or not a directory")
    _no_redirect(plugin_root, "hooks", "plugin hooks")
    return sorted({*DEFAULT_HOOK_PATHS, *_regular_inventory(distribution_root, directory)})

def product_projections(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    plugin_root, manifest_path, skills_root = _resolve_plugin(root)
    manifest_relative = manifest_path.relative_to(root).as_posix()
    skill_inventory = _regular_inventory(root, skills_root)
    hook_inventory = _hook_inventory(root, plugin_root)
    paths = {
        "source_distribution": (*PRODUCT_STATIC_PATHS, *skill_inventory, *hook_inventory),
        "marketplace_locator": (
            ".agents/plugins/marketplace.json",
            manifest_relative,
        ),
        "plugin_runtime": (manifest_relative, *skill_inventory, *hook_inventory),
        "public_docs": PUBLIC_DOCS,
        "provider_guidance": PROVIDER_GUIDANCE,
    }
    if tuple(paths) != PROJECTION_NAMES:
        raise IdentityError("named product projections differ")
    return {name: projection(plugin_root, values) for name, values in paths.items()}

def product_artifact_from_tree(
    root: Path,
    *,
    source_identity: str,
    baseline_identity: str,
    source_kind: str = "content_snapshot",
) -> dict[str, Any]:
    return build_product_artifact(
        source_provenance={
            "kind": source_kind,
            "identity": source_identity,
            "baseline_identity": baseline_identity,
        },
        projections=product_projections(root),
    )

def validate_product_against_tree(
    root: Path, product: dict[str, Any]
) -> dict[str, Any]:
    validate_product_artifact(product)
    provenance = product["source_provenance"]
    expected = product_artifact_from_tree(
        root,
        source_identity=provenance["identity"],
        baseline_identity=provenance["baseline_identity"],
        source_kind=provenance["kind"],
    )
    if expected != product:
        raise IdentityError("ProductArtifact differs from current consumer inputs")
    return product

def evaluator_components(root: Path) -> dict[str, str]:
    root = root.resolve(strict=True)
    return {
        name: projection(root, paths)["projection_sha256"]
        for name, paths in EVALUATOR_COMPONENT_PATHS.items()
    }

def _git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    environment = {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    }
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=not binary,
        check=False,
        env=environment,
    )
    if completed.returncode:
        raise IdentityError(f"git identity command failed: {' '.join(args)}")
    return completed.stdout if binary else completed.stdout.strip()

def _snapshot_entry(
    *, path: str, mode: str, git_object: str, body: bytes
) -> dict[str, Any]:
    private = path == PRIVATE_ORACLE_PATH
    return {
        "path": _safe_relative(path),
        "mode": mode,
        "git_object": git_object,
        "sha256": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
        "visibility": "digest_only" if private else "readable",
        "content_encoding": "none" if private else "base64",
        "content": "" if private else base64.b64encode(body).decode("ascii"),
    }

def review_snapshot_from_git(repo: Path, revision: str) -> dict[str, Any]:
    repo = repo.resolve(strict=True)
    commit = str(_git(repo, "rev-parse", f"{revision}^{{commit}}"))
    tree = str(_git(repo, "rev-parse", f"{commit}^{{tree}}"))
    raw = _git(repo, "ls-tree", "-r", "-z", commit, binary=True)
    assert isinstance(raw, bytes)
    entries = []
    for row in raw.split(b"\0"):
        if not row:
            continue
        try:
            metadata, raw_path = row.split(b"\t", 1)
            mode, kind, object_id = metadata.decode("ascii").split()
            path = raw_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise IdentityError("Git review inventory is malformed") from exc
        if kind != "blob" or mode not in ("100644", "100755"):
            raise IdentityError("Git review inventory is outside regular blobs")
        body = _git(repo, "cat-file", "blob", object_id, binary=True)
        assert isinstance(body, bytes)
        entries.append(
            _snapshot_entry(
                path=path,
                mode=mode,
                git_object=object_id,
                body=body,
            )
        )
    value = {
        "source_kind": "git_tree",
        "commit": commit,
        "tree": tree,
        "entries": entries,
    }
    snapshot = {**value, "snapshot_sha256": canonical_sha256(value)}
    return validate_review_snapshot(snapshot)

def validate_review_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    exact(
        snapshot,
        {"source_kind", "commit", "tree", "entries", "snapshot_sha256"},
        "review_snapshot",
    )
    if snapshot["source_kind"] != "git_tree":
        raise IdentityError("review snapshot kind differs")
    text(snapshot["commit"], "review_snapshot.commit")
    text(snapshot["tree"], "review_snapshot.tree")
    entries = snapshot["entries"]
    if type(entries) is not list or not entries:
        raise IdentityError("review snapshot inventory is empty")
    paths = []
    private_count = 0
    for index, entry in enumerate(entries):
        label = f"review_snapshot.entries[{index}]"
        exact(
            entry,
            {
                "path",
                "mode",
                "git_object",
                "sha256",
                "size_bytes",
                "visibility",
                "content_encoding",
                "content",
            },
            label,
        )
        path = _safe_relative(entry["path"])
        paths.append(path)
        if entry["mode"] not in ("100644", "100755"):
            raise IdentityError(f"{label}.mode differs")
        text(entry["git_object"], f"{label}.git_object")
        sha256(entry["sha256"], f"{label}.sha256")
        if type(entry["size_bytes"]) is not int or entry["size_bytes"] < 0:
            raise IdentityError(f"{label}.size_bytes differs")
        if path == PRIVATE_ORACLE_PATH:
            private_count += 1
            if (
                entry["visibility"] != "digest_only"
                or entry["content_encoding"] != "none"
                or entry["content"] != ""
            ):
                raise IdentityError("private oracle is provider-readable")
        else:
            if (
                entry["visibility"] != "readable"
                or entry["content_encoding"] != "base64"
                or type(entry["content"]) is not str
            ):
                raise IdentityError(f"{label} is not readable")
            try:
                body = base64.b64decode(entry["content"], validate=True)
            except (ValueError, TypeError) as exc:
                raise IdentityError(f"{label}.content is invalid base64") from exc
            if (
                hashlib.sha256(body).hexdigest() != entry["sha256"]
                or len(body) != entry["size_bytes"]
            ):
                raise IdentityError(f"{label}.content identity differs")
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise IdentityError("review snapshot paths are not sorted and unique")
    if private_count != 1:
        raise IdentityError("review snapshot private oracle partition differs")
    sha256(snapshot["snapshot_sha256"], "review_snapshot.snapshot_sha256")
    body = {key: snapshot[key] for key in snapshot if key != "snapshot_sha256"}
    if snapshot["snapshot_sha256"] != canonical_sha256(body):
        raise IdentityError("review snapshot identity differs")
    return snapshot

def build_review_projection(
    *, baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    validate_review_snapshot(baseline)
    validate_review_snapshot(candidate)
    baseline_entries = {item["path"]: item for item in baseline["entries"]}
    candidate_entries = {item["path"]: item for item in candidate["entries"]}
    changed_paths = sorted(
        path
        for path in set(baseline_entries) | set(candidate_entries)
        if baseline_entries.get(path) != candidate_entries.get(path)
    )
    value = {
        "projection_type": "ReviewProjection",
        "schema_version": SCHEMA_VERSION,
        "baseline": baseline,
        "candidate": candidate,
        "changed_paths": changed_paths,
        "candidate_snapshot_sha256": candidate["snapshot_sha256"],
    }
    return validate_review_projection(
        {**value, "projection_sha256": canonical_sha256(value)}
    )

def review_projection_from_git(
    repo: Path, *, baseline: str, candidate: str
) -> dict[str, Any]:
    return build_review_projection(
        baseline=review_snapshot_from_git(repo, baseline),
        candidate=review_snapshot_from_git(repo, candidate),
    )

def validate_review_projection_against_git(
    repo: Path, projection_value: dict[str, Any]
) -> dict[str, Any]:
    """Require the readable projection to be the complete clean HEAD snapshot."""
    validate_review_projection(projection_value)
    candidate = projection_value["candidate"]
    expected = review_projection_from_git(
        repo,
        baseline=projection_value["baseline"]["commit"],
        candidate=candidate["commit"],
    )
    if expected != projection_value:
        raise IdentityError("ReviewProjection differs from reconstructed Git snapshots")
    if (
        _git(repo, "rev-parse", "HEAD^{commit}") != candidate["commit"]
        or _git(repo, "rev-parse", "HEAD^{tree}") != candidate["tree"]
        or _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    ):
        raise IdentityError("ReviewProjection candidate is not the clean Git HEAD")
    return projection_value

def validate_review_projection(
    projection_value: dict[str, Any],
) -> dict[str, Any]:
    exact(
        projection_value,
        {
            "projection_type",
            "schema_version",
            "baseline",
            "candidate",
            "changed_paths",
            "candidate_snapshot_sha256",
            "projection_sha256",
        },
        "ReviewProjection",
    )
    if (
        projection_value["projection_type"] != "ReviewProjection"
        or projection_value["schema_version"] != SCHEMA_VERSION
    ):
        raise IdentityError("ReviewProjection header differs")
    baseline = validate_review_snapshot(projection_value["baseline"])
    candidate = validate_review_snapshot(projection_value["candidate"])
    expected_changed = sorted(
        path
        for path in {
            *(item["path"] for item in baseline["entries"]),
            *(item["path"] for item in candidate["entries"]),
        }
        if next(
            (item for item in baseline["entries"] if item["path"] == path),
            None,
        )
        != next(
            (item for item in candidate["entries"] if item["path"] == path),
            None,
        )
    )
    if projection_value["changed_paths"] != expected_changed:
        raise IdentityError("ReviewProjection changed paths are not derived")
    if (
        projection_value["candidate_snapshot_sha256"]
        != candidate["snapshot_sha256"]
    ):
        raise IdentityError("ReviewProjection candidate snapshot differs")
    sha256(
        projection_value["projection_sha256"],
        "ReviewProjection.projection_sha256",
    )
    body = {
        key: projection_value[key]
        for key in projection_value
        if key != "projection_sha256"
    }
    if projection_value["projection_sha256"] != canonical_sha256(body):
        raise IdentityError("ReviewProjection identity differs")
    return projection_value

__all__ = (
    "IdentityError",
    "build_review_projection",
    "evaluator_components",
    "product_artifact_from_tree",
    "product_projections",
    "review_projection_from_git",
    "review_snapshot_from_git",
    "validate_product_against_tree",
    "validate_review_projection",
    "validate_review_projection_against_git",
    "validate_review_snapshot",
)
