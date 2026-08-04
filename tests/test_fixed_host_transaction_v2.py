from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from evaluation.cli import parser
from evaluation.host import HostEvidenceError, attestation_from_raw
from evaluation.identity import evaluator_components, evaluator_components_from_git
from evaluation.manifest import ManifestError, _validate_structural_schema
from evaluation.provider import BEHAVIOR_DEVELOPER_INSTRUCTIONS
from evaluation.records import canonical_sha256, evaluation_authority_request_payload
from tests.attestation_fixtures import (
    HOST_CONTRACT, ROOT, SHA, TOTAL_CAP, attest_all, bundle, host_metadata, mapping, passing_report,
    previous_product, product, raw_stream, reseal, terminal,
)


FAKE_BINARY = ROOT / "tests" / "fake_external_host.py"
EXECUTOR_INSTRUCTIONS = BEHAVIOR_DEVELOPER_INSTRUCTIONS


def _events(*items: dict) -> bytes:
    return b"".join(
        (json.dumps(item, sort_keys=True) + "\n").encode() for item in items
    )


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _git_blob_sha(body: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()


def _freeze_tree(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_file():
            path.chmod(0o500 if path.stat().st_mode & 0o111 else 0o400)
    for path in sorted(
        (item for item in root.rglob("*") if item.is_dir()),
        key=lambda item: len(item.parts), reverse=True,
    ):
        path.chmod(0o500)
    root.chmod(0o500)


def _exact_kwargs(
    source_repo: Path, *, role_sha256: str = SHA["3"],
    source_product: dict | None = None,
) -> dict:
    source_product = source_product or product()
    def resolve(value: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(source_repo), "rev-parse", value], text=True,
        ).strip()
    baseline_ref, source_ref = "refs/heads/baseline-review", "refs/heads/source-review"
    baseline_commit, source_commit = resolve(baseline_ref), resolve(source_ref)
    return {
        "source_repo": source_repo,
        "source_identity": {
            "baseline_ref": baseline_ref, "baseline_commit": baseline_commit,
            "baseline_tree": resolve(f"{baseline_commit}^{{tree}}"),
            "source_ref": source_ref, "source_commit": source_commit,
            "source_tree": resolve(f"{source_commit}^{{tree}}"),
            **{key: source_product[key] for key in (
                "package_tree", "package_artifact_sha256", "package_semantic_sha256",
            )},
        },
        "evaluator_identity": evaluator_components_from_git(source_repo, source_commit),
        "external_role_config_sha256": role_sha256,
    }


def _policy_exact_kwargs(policy: dict) -> dict:
    workspace = policy["workspace_policy"]
    return {
        "source_repo": Path(workspace["source_repo"]),
        "source_identity": workspace["source_identity"],
        "evaluator_identity": workspace["evaluator_identity"],
        "external_role_config_sha256": policy["provider_policy"]["external_role_config_sha256"],
    }


def _synthetic_snapshot(
    base: Path, *, hidden_file: bool = False, hidden_diff: bool = False,
    private_file_diff: bool = False, path_mention: bool = False,
    untracked_support: bool = False,
    external_role_config_sha256: str = SHA["3"],
    source_product: dict | None = None,
    unreachable_lineage: bool = False,
    incomplete_scope: bool = False,
    evaluator_override: dict[str, str] | None = None,
    copy_worktree: bool = True,
    managed_root_blob: str | None = None,
) -> tuple[Path, Path]:
    source_product = source_product or product()
    git_env = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C",
        "GIT_AUTHOR_NAME": "Exact Source", "GIT_AUTHOR_EMAIL": "source@invalid",
        "GIT_COMMITTER_NAME": "Exact Source", "GIT_COMMITTER_EMAIL": "source@invalid",
        "GIT_AUTHOR_DATE": "2000-01-02T00:00:00Z",
        "GIT_COMMITTER_DATE": "2000-01-02T00:00:00Z",
    }
    source_repo = base / "source-repo"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(source_repo)], check=True, env=git_env)
    subprocess.run(["git", "-C", str(source_repo), "branch", "baseline-review", "HEAD"], check=True, env=git_env)
    subprocess.run(["git", "-C", str(source_repo), "checkout", "-q", "-b", "source-review"], check=True, env=git_env)
    tracked_source = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
    for relative in tracked_source:
        if copy_worktree and (relative == "README.md" or relative.startswith((".agents/", ".codex-plugin/", "evaluation/", "skills/", "tests/"))):
            target = source_repo / relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
    if managed_root_blob:
        target = source_repo / managed_root_blob
        if target.is_dir(): shutil.rmtree(target)
        target.write_bytes(b"managed root blob\n")
    subprocess.run(["git", "-C", str(source_repo), "add", ".agents", ".codex-plugin", "README.md", "evaluation", "skills", "tests"], check=True, env=git_env)
    subprocess.run(
        ["git", "-C", str(source_repo), "-c", "commit.gpgSign=false", "commit", "--allow-empty", "-q", "-m", "Candidate exact source"],
        check=True, env=git_env,
    )
    exact = _exact_kwargs(
        source_repo, role_sha256=external_role_config_sha256,
        source_product=source_product,
    )
    source_commit = exact["source_identity"]["source_commit"]
    source_tree = exact["source_identity"]["source_tree"]
    baseline_commit = exact["source_identity"]["baseline_commit"]
    baseline_tree = exact["source_identity"]["baseline_tree"]
    inventory = []
    rows = subprocess.check_output(
        ["git", "-C", str(source_repo), "ls-tree", "-r", "-z", source_commit],
    ).split(b"\0")
    for row in rows:
        if not row:
            continue
        metadata, raw_path = row.split(b"\t", 1)
        mode, kind, object_id = metadata.decode().split()
        body = subprocess.check_output(
            ["git", "-C", str(source_repo), "cat-file", "blob", object_id],
        )
        inventory.append(
            {
                "path": raw_path.decode(), "git_mode": mode,
                "git_object": object_id, "sha256": hashlib.sha256(body).hexdigest(),
                "size_bytes": len(body),
            }
        )
    snapshot = base / "execution" / "exact-final-source"
    snapshot.mkdir(mode=0o700)
    oracle = base / "private" / "evaluation" / "hidden-oracles-v1.json"
    oracle.parent.mkdir(parents=True)
    private_source = next(item for item in inventory if item["path"] == "evaluation/hidden-oracles-v1.json")
    oracle.write_bytes(
        subprocess.check_output(
            ["git", "-C", str(source_repo), "cat-file", "blob", private_source["git_object"]],
        )
    )
    body = oracle.read_bytes()
    managed = (".agents", ".codex-plugin", "README.md", "evaluation", "skills", "tests")
    included = [
        item for item in inventory
        if item["path"] != "evaluation/hidden-oracles-v1.json"
        and any(item["path"] == root or item["path"].startswith(root + "/") for root in managed)
    ]
    if incomplete_scope:
        included = [item for item in included if item["path"] == "README.md"]
    excluded = [item for item in inventory if item not in included]
    for item in included:
        target = snapshot / item["path"]; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.check_output(
            ["git", "-C", str(source_repo), "cat-file", "blob", item["git_object"]]
        ))
    diff = snapshot / "EXACT_FINAL_DIFF.patch"
    if hidden_diff:
        diff.write_bytes(
            b"diff --git a/public-copy.json b/public-copy.json\n"
            b"--- a/public-copy.json\n+++ b/public-copy.json\n@@ -1,22 +1,22 @@\n"
            + b"".join(b" " + line for line in body.splitlines(keepends=True))
            + b"-old trailer\n+new trailer\n"
        )
    elif private_file_diff:
        diff.write_bytes(
            b"diff --git a/evaluation/hidden-oracles-v1.json b/evaluation/hidden-oracles-v1.json\n"
            b"--- a/evaluation/hidden-oracles-v1.json\n"
            b"+++ b/evaluation/hidden-oracles-v1.json\n@@ -1 +1 @@\n-old\n+new\n"
        )
    elif path_mention:
        diff.write_bytes(
            b"diff --git a/evaluation/provider.py b/evaluation/provider.py\n"
            b"--- a/evaluation/provider.py\n+++ b/evaluation/provider.py\n@@ -1 +1,2 @@\n"
            b" context\n+PRIVATE_PATH = 'evaluation/hidden-oracles-v1.json'\n"
        )
    else:
        diff.write_bytes(subprocess.check_output([
            "git", "-C", str(source_repo), "diff", "--binary", "--full-index", "--no-renames",
            "--no-ext-diff", "--no-textconv",
            baseline_commit, source_commit, "--", ".agents", ".codex-plugin", "README.md",
            "evaluation", "skills", "tests", ":(exclude)evaluation/hidden-oracles-v1.json",
        ]))
    private = private_source
    manifest = {
        "schema_version": 1,
        "source": {
            "baseline": {
                "ref": "refs/heads/baseline-review", "commit": baseline_commit,
                "tree": baseline_tree,
            },
            "source": {
                "ref": "refs/heads/source-review",
                "commit": "1" * 40 if unreachable_lineage else source_commit,
                "tree": source_tree,
            },
        },
        "product": {
            key: source_product[key]
            for key in ("package_tree", "package_artifact_sha256", "package_semantic_sha256")
        },
        "evaluator": evaluator_override or exact["evaluator_identity"],
        "external_role_config_sha256": external_role_config_sha256,
        "aggregate_diff": {
            "path": diff.name, "git_mode": "100644",
            "git_object": _git_blob_sha(diff.read_bytes()),
            "sha256": hashlib.sha256(diff.read_bytes()).hexdigest(),
            "size_bytes": diff.stat().st_size,
        },
        "private_exclusion": private,
        "projection": {
            "included": included, "excluded": excluded,
            "file_count": len(inventory),
        },
        "support_files": ["EXACT_FINAL_DIFF.patch", "EXACT_FINAL_SOURCE_MANIFEST.json"],
    }
    (snapshot / "EXACT_FINAL_SOURCE_MANIFEST.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8",
    )
    if hidden_file:
        path = snapshot / private["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    subprocess.run(
        ["git", "init", "-q", "-b", "exact-final", str(snapshot)],
        check=True, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
    )
    subprocess.run(
        ["git", "-C", str(snapshot), "add", "README.md"] if untracked_support else
        ["git", "-C", str(snapshot), "add", "-A"], check=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
    )
    commit_env = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C",
        "GIT_AUTHOR_NAME": "Exact Final", "GIT_AUTHOR_EMAIL": "exact@invalid",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
        "GIT_COMMITTER_NAME": "Exact Final", "GIT_COMMITTER_EMAIL": "exact@invalid",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z",
    }
    subprocess.run(
        ["git", "-C", str(snapshot), "-c", "commit.gpgSign=false", "commit", "-q", "-m", "Frozen exact-final projection"],
        check=True, env=commit_env,
    )
    _freeze_tree(snapshot)
    oracle.chmod(0o400)
    return snapshot, oracle


class ReproducedBlockerTests(unittest.TestCase):
    def test_every_provider_object_is_closed_and_exactly_required(self):
        schemas = json.loads((ROOT / "evaluation" / "report-schemas-v1.json").read_text())
        objects = []

        def walk(node):
            if isinstance(node, dict):
                if node.get("type") == "object":
                    objects.append(node)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(schemas)
        self.assertEqual(len(objects), 23)
        for node in objects:
            self.assertIs(node.get("additionalProperties"), False)
            self.assertEqual(set(node.get("required", [])), set(node.get("properties", {})))
        finding = schemas["exact_final"]["properties"]["findings"]["items"]
        self.assertEqual(finding["required"], ["summary"])
        self.assertEqual(finding["properties"], {"summary": {"type": "string"}})
        self.assertEqual(
            schemas["exact_final"]["properties"]["decision"],
            {"type": "string", "enum": ["GO", "NOT_YET"]},
        )

    def test_materializer_rejects_open_provider_object_offline(self):
        with self.assertRaises(ManifestError):
            _validate_structural_schema(
                {"type": "object", "required": ["safe"], "properties": {"safe": {"type": "boolean"}}}
            )

    def test_real_native_error_suffix_becomes_ambiguous_attestation(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        message = "provider returned invalid_json_schema"
        raw = _events(
            {"type": "thread.started", "thread_id": "native-failure"},
            {"type": "turn.started"},
            {"type": "error", "message": message},
            {"type": "turn.failed", "error": {"message": message}},
        )
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"], raw=raw,
            host_metadata=host_metadata(unit, exit_code=1), authority_sha256=SHA["a"],
        )
        self.assertEqual(record["terminal"]["classification"], "ambiguous_or_partial")
        self.assertTrue(record["terminal"]["provider_reached"])
        self.assertEqual(record["terminal"]["model_calls"], 1)
        self.assertEqual(record["observation"]["report"], {})

    def test_host_contract_binds_provider_policy_and_cli_has_no_writer(self):
        self.assertEqual(
            set(HOST_CONTRACT),
            {"schema_version", "trust_domain", "behavior_sha256", "holdout_sha256", "exact_final_sha256", "effect_namespace_sha256"},
        )
        choices = parser()._subparsers._group_actions[0].choices
        self.assertNotIn("claim", choices)

    def test_schema_valid_adverse_exact_final_is_durable(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["stage"] == "exact_final")
        report = {
            "neutral": False, "coverage": {"complete": False},
            "decision": "NOT_YET", "findings": [{"summary": "blocker"}],
        }
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
            raw=raw_stream(unit, report=report), host_metadata=host_metadata(unit),
            authority_sha256=SHA["a"],
        )
        self.assertEqual(record["verdict"], "fail")
        self.assertEqual(record["observation"]["report"], report)


class FixedHostTransactionTests(unittest.TestCase):
    def _inputs(
        self, directory: str, *, effect_marker_root: Path | None = None,
        copy_worktree: bool = True,
    ):
        from evaluation.host import build_fixed_host_policy, host_contract_from_policy

        base = Path(directory)
        execution = base / "execution"
        for path in (
            execution, execution / "units", execution / "raw",
            execution / "attestations", execution / "claims",
        ):
            path.mkdir(mode=0o700)
        role = base / "executor.toml"
        role.write_text(
            'name = "happycodex_executor"\n'
            'description = "Sole controlled-domain writer for HappyCodex/0.5."\n'
            'model = "gpt-fake"\nmodel_reasoning_effort = "high"\n'
            'developer_instructions = """\n' + EXECUTOR_INSTRUCTIONS +
            '"""\n[features]\nplugins = false\n',
            encoding="utf-8",
        )
        role.chmod(0o600)
        role_sha = hashlib.sha256(role.read_bytes()).hexdigest()
        selected = product()
        baseline = previous_product()
        snapshot, private_oracle = _synthetic_snapshot(
            base, external_role_config_sha256=role_sha, source_product=selected,
            copy_worktree=copy_worktree,
        )
        exact = _exact_kwargs(
            base / "source-repo", role_sha256=role_sha, source_product=selected,
        )
        effect_markers = effect_marker_root or base / "effect-markers"
        if not effect_markers.exists():
            effect_markers.mkdir(mode=0o700)
        mapping_path = base / "holdout-mapping.json"
        mapping_path.write_text(json.dumps(mapping(), sort_keys=True) + "\n", encoding="utf-8")
        mapping_path.chmod(0o600)
        binary = base / "provider-binary"
        binary.write_bytes(FAKE_BINARY.read_bytes())
        binary.chmod(0o500)
        policy = build_fixed_host_policy(
            execution_root=execution, binary_path=binary,
            external_role_config_path=role, exact_final_source=snapshot,
            holdout_mapping_path=mapping_path, private_oracle_path=private_oracle,
            effect_marker_root=effect_markers, source_repo=base / "source-repo",
            source_identity=exact["source_identity"],
            evaluator_identity=exact["evaluator_identity"],
            behavior_model="gpt-fake",
        )
        contract = host_contract_from_policy(policy)
        selected, baseline, spec, blind = bundle(
            selected_product=selected, baseline_product=baseline,
            host_contract=contract, external_role_config_sha256=role_sha,
        )
        return execution, role, mapping_path, policy, selected, baseline, spec, blind

    def _authority(self, spec):
        supplied = {
            "scope": "evaluation", "request_sha256": spec["authority_request_sha256"],
            "nonce": "n", "signature": "s",
        }
        return supplied, canonical_sha256(supplied), f"APPROVE HAPPYCODEX EVALUATION {spec['authority_request_sha256']}"

    def test_exact_final_source_is_clean_fully_bound_and_relocation_invariant(self):
        from evaluation.provider import exact_final_source_identity

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, _, _, _, _ = self._inputs(directory)
            source = Path(policy["workspace_policy"]["exact_final_source"])
            private = Path(policy["workspace_policy"]["private_oracle_path"])
            self.assertEqual(
                subprocess.check_output(
                    ["git", "-C", str(source), "status", "--porcelain=v1"], text=True,
                    env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
                ),
                "",
            )
            tracked = set(subprocess.check_output(
                ["git", "-C", str(source), "ls-files"], text=True,
                env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
            ).splitlines())
            manifest = json.loads((source / "EXACT_FINAL_SOURCE_MANIFEST.json").read_text())
            self.assertEqual(
                tracked,
                {item["path"] for item in manifest["projection"]["included"]}
                | {"EXACT_FINAL_DIFF.patch", "EXACT_FINAL_SOURCE_MANIFEST.json"},
            )
            self.assertTrue({
                "README.md", ".codex-plugin/plugin.json", "evaluation/provider.py",
                "evaluation/host.py", "evaluation/verify.py", "skills/happycodex/SKILL.md",
                "tests/test_fixed_host_transaction_v2.py",
            }.issubset(tracked))
            relocated = Path(directory) / "relocated"
            shutil.copytree(source, relocated)
            self.assertEqual(
                policy["workspace_policy"]["exact_final_source_sha256"],
                exact_final_source_identity(relocated, private, **_policy_exact_kwargs(policy)),
            )
            self.assertEqual(list((execution / "units").iterdir()), [])

    def test_exact_final_source_rejects_self_selected_projection_and_fake_diff(self):
        from evaluation.provider import ProviderError, exact_final_source_identity

        for mutation in ("scope", "diff", "old-source"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                base = Path(directory); (base / "execution").mkdir(mode=0o700)
                override = evaluator_components(ROOT) if mutation == "old-source" else None
                source, private = _synthetic_snapshot(
                    base, incomplete_scope=mutation == "scope",
                    path_mention=mutation == "diff",
                    copy_worktree=mutation != "old-source",
                    evaluator_override=override,
                )
                with self.assertRaises(ProviderError):
                    exact_final_source_identity(
                        source, private, **_exact_kwargs(base / "source-repo"),
                    )

    def test_exact_source_projection_includes_managed_root_blob(self):
        from evaluation.provider import exact_final_source_identity

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); (base / "execution").mkdir(mode=0o700)
            source, private = _synthetic_snapshot(base, managed_root_blob="tests")
            self.assertEqual(
                len(exact_final_source_identity(
                    source, private, **_exact_kwargs(base / "source-repo"),
                )),
                64,
            )
            self.assertIn("tests", subprocess.check_output(
                ["git", "-C", str(source), "ls-files"], text=True,
            ).splitlines())
            self.assertEqual((source / "tests").read_bytes(), b"managed root blob\n")

    def test_host_policy_rejects_fixed_tool_surface_drift_before_effect(self):
        from evaluation.provider import ProviderError, host_contract_from_policy

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, _, _, _, _ = self._inputs(directory)
            policy["tool_config"]["allowed_model_tools"] = []
            with self.assertRaises(ProviderError):
                host_contract_from_policy(policy)
            self.assertEqual(list((execution / "units").iterdir()), [])
            self.assertEqual(list(Path(policy["workspace_policy"]["effect_marker_root"]).iterdir()), [])

    def test_host_policy_rejects_fixed_permission_drift_before_effect(self):
        from evaluation.provider import ProviderError, host_contract_from_policy

        for mutation in ("filesystem", "network", "approval", "environment"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                execution, _, _, policy, _, _, _, _ = self._inputs(directory)
                permission = policy["permission_profile"]
                if mutation == "filesystem": permission["filesystem"][":minimal"] = "write"
                elif mutation == "network": permission["network_enabled"] = True
                elif mutation == "approval": permission["approval_policy"] = "on-request"
                else: permission["model_shell_environment"]["set"] = ["PATH"]
                with self.assertRaises(ProviderError):
                    host_contract_from_policy(policy)
                for name in ("units", "raw", "attestations", "claims"):
                    self.assertEqual(list((execution / name).iterdir()), [])
                self.assertEqual(list(Path(policy["workspace_policy"]["effect_marker_root"]).iterdir()), [])

    def test_wall_cap_bounds_runner_timeout_before_effect(self):
        from evaluation.host import execute_fixed_host_transaction
        from evaluation.provider import host_contract_from_policy

        with tempfile.TemporaryDirectory() as directory:
            _, _, _, policy, selected, baseline, _, _ = self._inputs(directory)
            _, _, spec, _ = bundle(
                selected_product=selected, baseline_product=baseline,
                host_contract=host_contract_from_policy(policy),
                external_role_config_sha256=policy["provider_policy"]["external_role_config_sha256"],
                total_cap={**TOTAL_CAP, "wall_milliseconds": 1},
            )
            unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
            supplied, _, line = self._authority(spec)
            captured = {}

            def provider(**kwargs):
                captured.update(kwargs)
                os.write(kwargs["stdout_fd"], raw_stream(unit))
                return 0, False

            execute_fixed_host_transaction(
                repo_root=ROOT, product=selected, previous_product=baseline,
                spec=spec, unit_id=unit["unit_id"], policy=policy,
                authority_line=line, supplied_authority=supplied,
                authenticate_line=lambda actual, _value: actual == line,
                provider_auth=b"private-auth", run_provider=provider,
                clock=lambda: datetime(2026, 8, 3, tzinfo=timezone.utc),
            )
            self.assertLessEqual(captured["timeout_seconds"], 0.001)

    def test_concurrent_selected_timeouts_share_remaining_wall(self):
        from evaluation.host import execute_fixed_host_transaction
        from evaluation.provider import host_contract_from_policy

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, _, _ = self._inputs(directory)
            _, _, spec, _ = bundle(
                selected_product=selected, baseline_product=baseline,
                host_contract=host_contract_from_policy(policy),
                external_role_config_sha256=policy["provider_policy"]["external_role_config_sha256"],
                total_cap={**TOTAL_CAP, "wall_milliseconds": 60000},
            )
            supplied, authority, line = self._authority(spec)
            behavior = {unit["unit_id"] for unit in spec["units"] if unit["stage"] == "behavior"}
            self._persist(
                execution, selected, baseline, spec, behavior, authority,
                terminal_values={unit_id: terminal(wall_milliseconds=10000) for unit_id in behavior},
            )
            holdouts = [unit for unit in spec["units"] if unit["stage"] == "holdout"][:2]
            barrier = threading.Barrier(2); timeouts = []; errors = []

            def launch(unit):
                def provider(**kwargs):
                    timeouts.append(kwargs["timeout_seconds"]); barrier.wait(timeout=5)
                    os.write(kwargs["stdout_fd"], raw_stream(unit)); return 0, False
                try:
                    execute_fixed_host_transaction(
                        repo_root=ROOT, product=selected, previous_product=baseline,
                        spec=spec, unit_id=unit["unit_id"], policy=policy,
                        authority_line=line, supplied_authority=supplied,
                        authenticate_line=lambda actual, _value: actual == line,
                        provider_auth=b"private-auth", run_provider=provider,
                        clock=lambda: datetime(2026, 8, 3, tzinfo=timezone.utc),
                    )
                except Exception as exc: errors.append(exc)

            threads = [threading.Thread(target=launch, args=(unit,)) for unit in holdouts]
            for thread in threads: thread.start()
            for thread in threads: thread.join(timeout=10)
            self.assertEqual(errors, [])
            self.assertEqual(len(timeouts), 2)
            self.assertLessEqual(sum(timeouts), 10)

    def test_exact_diff_ignores_source_repo_external_diff_config(self):
        from evaluation.provider import exact_final_source_identity

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); (base / "execution").mkdir(mode=0o700)
            source, private = _synthetic_snapshot(base)
            exact = _exact_kwargs(base / "source-repo")
            expected = exact_final_source_identity(source, private, **exact)
            subprocess.run(
                ["git", "-C", str(base / "source-repo"), "config", "diff.external", "true"],
                check=True,
            )
            self.assertEqual(exact_final_source_identity(source, private, **exact), expected)

    def test_old_source_components_cannot_back_a_new_dirty_evalspec(self):
        from evaluation.host import execute_fixed_host_transaction

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(
                directory, copy_worktree=False,
            )
            supplied, _, line = self._authority(spec)
            with self.assertRaisesRegex(HostEvidenceError, "source evaluator component"):
                execute_fixed_host_transaction(
                    repo_root=ROOT, product=selected, previous_product=baseline,
                    spec=spec, unit_id="goal-divergence", policy=policy,
                    authority_line=line, supplied_authority=supplied,
                    authenticate_line=lambda *_args: self.fail("authority accepted"),
                    provider_auth=b"private-auth",
                    run_provider=lambda **_kwargs: self.fail("provider reached"),
                )
            self.assertEqual(list((execution / "units").iterdir()), [])
            self.assertEqual(list(Path(policy["workspace_policy"]["effect_marker_root"]).iterdir()), [])

    def test_exact_final_source_rejects_untracked_support_and_hidden_oracle(self):
        from evaluation.provider import ProviderError, exact_final_source_identity

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, _, _, _, _ = self._inputs(directory)
            source = Path(policy["workspace_policy"]["exact_final_source"])
            private = Path(policy["workspace_policy"]["private_oracle_path"])
            source.chmod(0o700)
            untracked = source / "UNTRACKED"
            untracked.write_text("not bound\n", encoding="utf-8"); untracked.chmod(0o400)
            source.chmod(0o500)
            with self.assertRaisesRegex(ProviderError, "clean synthetic commit"):
                exact_final_source_identity(source, private, **_policy_exact_kwargs(policy))
            self.assertEqual(list((execution / "claims").iterdir()), [])

        for exposure in ("file", "diff"):
            with self.subTest(exposure=exposure), tempfile.TemporaryDirectory() as directory:
                base = Path(directory); (base / "execution").mkdir(mode=0o700)
                source, private = _synthetic_snapshot(
                    base, hidden_file=exposure == "file", hidden_diff=exposure == "diff",
                )
                with self.assertRaisesRegex(ProviderError, "hidden oracle"):
                    exact_final_source_identity(source, private, **_exact_kwargs(base / "source-repo"))

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); (base / "execution").mkdir(mode=0o700)
            source, private = _synthetic_snapshot(base, private_file_diff=True)
            with self.assertRaisesRegex(ProviderError, "hidden oracle file"):
                exact_final_source_identity(source, private, **_exact_kwargs(base / "source-repo"))

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); (base / "execution").mkdir(mode=0o700)
            source, private = _synthetic_snapshot(base, path_mention=True)
            with self.assertRaisesRegex(ProviderError, "aggregate diff"):
                exact_final_source_identity(source, private, **_exact_kwargs(base / "source-repo"))

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); (base / "execution").mkdir(mode=0o700)
            source, private = _synthetic_snapshot(base, untracked_support=True)
            with self.assertRaisesRegex(ProviderError, "clean synthetic commit"):
                exact_final_source_identity(source, private, **_exact_kwargs(base / "source-repo"))

    def test_exact_final_source_rejects_unreachable_placeholder_lineage(self):
        from evaluation.provider import ProviderError, exact_final_source_identity

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "execution").mkdir(mode=0o700)
            source, private = _synthetic_snapshot(base, unreachable_lineage=True)

            with self.assertRaisesRegex(ProviderError, "lineage|source|reachable"):
                exact_final_source_identity(source, private, **_exact_kwargs(base / "source-repo"))

    def test_post_policy_source_or_git_config_mutation_stops_before_effect(self):
        from evaluation.host import execute_fixed_host_transaction
        from evaluation.provider import ProviderError

        for relative in (Path("README.md"), Path(".git/config")):
            with self.subTest(relative=str(relative)), tempfile.TemporaryDirectory() as directory:
                execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
                source = Path(policy["workspace_policy"]["exact_final_source"])
                target = source / relative
                source.chmod(0o700); target.parent.chmod(0o700); target.chmod(0o600)
                target.write_bytes(target.read_bytes() + b"\nmutated\n")
                target.chmod(0o400); target.parent.chmod(0o500); source.chmod(0o500)
                supplied, _, line = self._authority(spec)
                with self.assertRaisesRegex(ProviderError, "clean synthetic commit|Git config differs|identity drift"):
                    execute_fixed_host_transaction(
                        repo_root=ROOT, product=selected, previous_product=baseline,
                        spec=spec, unit_id="goal-divergence", policy=policy,
                        authority_line=line, supplied_authority=supplied,
                        authenticate_line=lambda *_args: self.fail("authority accepted"),
                        provider_auth=b"private-auth",
                        run_provider=lambda **_kwargs: self.fail("provider reached"),
                    )
                self.assertEqual(list((execution / "units").iterdir()), [])
                self.assertEqual(list((execution / "claims").iterdir()), [])

    def _persist(self, execution, selected, baseline, spec, unit_ids, authority, *, terminal_values=None, reports=None):
        for unit in spec["units"]:
            if unit["unit_id"] not in unit_ids:
                continue
            unit_root = execution / "units" / unit["unit_id"]
            if not unit_root.exists(): unit_root.mkdir(mode=0o700)
            value = (terminal_values or {}).get(unit["unit_id"])
            raw = raw_stream(unit, terminal_value=value, report=(reports or {}).get(unit["unit_id"]))
            arm = selected if unit["product_semantic_sha256"] == selected["package_semantic_sha256"] else baseline
            record = attestation_from_raw(
                root=ROOT, product=arm, spec=spec, unit_id=unit["unit_id"], raw=raw,
                host_metadata=host_metadata(unit, terminal_value=value), authority_sha256=authority,
            )
            raw_path = execution / "raw" / f"{unit['unit_id']}.jsonl"
            raw_path.write_bytes(raw); raw_path.chmod(0o600)
            record_path = execution / "attestations" / f"{unit['unit_id']}.json"
            record_path.write_text(json.dumps(record, sort_keys=True) + "\n"); record_path.chmod(0o600)
            claim = {
                "schema_version": 1, "claim_key": unit["invocation"]["claim_key"],
                "effective_claim_key": canonical_sha256({"claim_key": unit["invocation"]["claim_key"], "recovery_index": 0}),
                "invocation_sha256": unit["invocation_sha256"], "recovery_index": 0,
            }
            claim_path = execution / "claims" / f"{claim['effective_claim_key']}.json"
            claim_path.write_text(json.dumps(claim, sort_keys=True) + "\n"); claim_path.chmod(0o600)

    def _persist_inflight(self, execution, unit):
        (execution / "units" / unit["unit_id"]).mkdir(mode=0o700)
        raw_path = execution / "raw" / f"{unit['unit_id']}.jsonl"
        raw_path.write_bytes(b""); raw_path.chmod(0o600)
        effective = canonical_sha256({"claim_key": unit["invocation"]["claim_key"], "recovery_index": 0})
        claim = {"schema_version":1,"claim_key":unit["invocation"]["claim_key"],"effective_claim_key":effective,"invocation_sha256":unit["invocation_sha256"],"recovery_index":0}
        path = execution / "claims" / f"{effective}.json"
        path.write_text(json.dumps(claim, sort_keys=True) + "\n"); path.chmod(0o600)
        descriptor = os.open(raw_path, os.O_RDWR)
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return descriptor

    def test_capability_precedes_preparation_and_mapping_read(self):
        from evaluation.host import execute_fixed_host_transaction, reveal_holdout_mapping

        with tempfile.TemporaryDirectory() as directory:
            execution, _, mapping_path, policy, selected, baseline, spec, _ = self._inputs(directory)
            supplied = {
                "scope": "evaluation", "request_sha256": spec["authority_request_sha256"],
                "nonce": "n", "signature": "s",
            }
            line = f"APPROVE HAPPYCODEX EVALUATION {spec['authority_request_sha256']}"
            with self.assertRaisesRegex(Exception, "authenticator"):
                execute_fixed_host_transaction(
                    repo_root=ROOT, product=selected, previous_product=baseline,
                    spec=spec, unit_id="goal-divergence", policy=policy,
                    authority_line=line, supplied_authority=supplied,
                    authenticate_line=lambda _line, _value: False,
                    provider_auth=b"private-auth", run_provider=lambda **_kwargs: self.fail("provider reached"),
                )
            self.assertEqual(list((execution / "units").iterdir()), [])
            self.assertEqual(list((execution / "claims").iterdir()), [])

            mapping_path.unlink()
            with self.assertRaisesRegex(HostEvidenceError, "six durable"):
                reveal_holdout_mapping(spec=spec, policy=policy)

    def test_behavior_transaction_is_exclusive_private_and_role_bound(self):
        from evaluation.host import _prepare_unit, execute_fixed_host_transaction
        from evaluation.provider import fixed_host_argv, fixed_host_instruction

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
            captured = {}
            private_auth = b'{"tokens":"PRIVATE-AUTH-SENTINEL"}'

            def fake_provider(**kwargs):
                captured.update(kwargs)
                self.assertEqual(_mode(Path(kwargs["env"]["CODEX_HOME"]) / "auth.json"), 0o600)
                os.write(
                    kwargs["stdout_fd"],
                    _events(
                        {"type": "thread.started", "thread_id": "fake-thread"},
                        {"type": "turn.started"},
                        {"type": "item.completed", "item": {
                            "id": "message", "type": "agent_message",
                            "text": json.dumps(passing_report(unit), sort_keys=True),
                        }},
                        {"type": "turn.completed", "usage": {
                            "input_tokens": 10, "cached_input_tokens": 0,
                            "cache_write_input_tokens": 0, "output_tokens": 2,
                            "reasoning_output_tokens": 0,
                        }},
                    ),
                )
                return 0, False

            supplied = {
                "scope": "evaluation", "request_sha256": spec["authority_request_sha256"],
                "nonce": "n", "signature": "s",
            }
            line = f"APPROVE HAPPYCODEX EVALUATION {spec['authority_request_sha256']}"
            times = iter(
                [datetime(2026, 8, 3, tzinfo=timezone.utc),
                 datetime(2026, 8, 3, tzinfo=timezone.utc) + timedelta(seconds=2)]
            )
            result = execute_fixed_host_transaction(
                repo_root=ROOT, product=selected, previous_product=baseline,
                spec=spec, unit_id=unit["unit_id"], policy=policy,
                authority_line=line, supplied_authority=supplied,
                authenticate_line=lambda actual, _value: actual == line,
                provider_auth=private_auth, run_provider=fake_provider,
                clock=lambda: next(times),
            )
            self.assertEqual(result["attestation"]["verdict"], "pass")
            unit_root = execution / "units" / unit["unit_id"]
            self.assertEqual(Path(captured["cwd"]), unit_root / "workspace")
            self.assertTrue((unit_root / "workspace" / ".git" / "HEAD").is_file())
            self.assertEqual(_mode(unit_root / "workspace"), 0o500)
            self.assertEqual(_mode(unit_root / "output-schema.json"), 0o400)
            self.assertFalse((unit_root / "codex-home" / "auth.json").exists())
            self.assertNotIn(private_auth, Path(result["raw_path"]).read_bytes())
            command_bin = unit_root / "command-bin"
            sandbox = command_bin / "codex-linux-sandbox"
            self.assertFalse((command_bin / "codex").exists())
            source = Path(policy["provider_policy"]["binary_path"])
            self.assertEqual(_mode(command_bin), 0o500)
            self.assertTrue(sandbox.is_file())
            self.assertTrue(os.access(sandbox, os.X_OK))
            self.assertEqual(
                (source.stat().st_dev, source.stat().st_ino),
                (sandbox.stat().st_dev, sandbox.stat().st_ino),
            )
            command_path = f"{command_bin}:/usr/bin:/bin"
            self.assertEqual(captured["env"]["PATH"], command_path)
            self.assertEqual(shutil.which("codex-linux-sandbox", path=command_path), str(sandbox))
            self.assertIn(
                "developer_instructions=" + json.dumps(EXECUTOR_INSTRUCTIONS),
                captured["argv"],
            )
            config_values = [
                captured["argv"][index + 1]
                for index, value in enumerate(captured["argv"][:-1])
                if value == "--config"
            ]
            disabled_values = [
                captured["argv"][index + 1]
                for index, value in enumerate(captured["argv"][:-1])
                if value == "--disable"
            ]
            self.assertEqual(policy["provider_policy"]["web_search"], "disabled")
            self.assertEqual(config_values.count('web_search="disabled"'), 1)
            self.assertIn(
                f'shell_environment_policy.set={{PATH={json.dumps(command_path)},HOME={json.dumps(str(unit_root / "home"))}}}',
                config_values,
            )
            self.assertNotIn("web_search_cached", disabled_values)
            self.assertNotIn("web_search_request", disabled_values)
            claim = list((execution / "claims").iterdir())
            self.assertEqual(len(claim), 1)
            self.assertEqual(claim[0].name, result["claim"]["effective_claim_key"] + ".json")
            self.assertEqual(_mode(Path(result["raw_path"])), 0o600)
            self.assertEqual(_mode(Path(result["attestation_path"])), 0o600)
            exact = next(item for item in spec["units"] if item["stage"] == "exact_final")
            exact_paths = _prepare_unit(policy, exact)
            exact_instruction = fixed_host_instruction(policy, exact)
            exact_argv = fixed_host_argv(policy, exact, exact_paths, exact_instruction)
            self.assertEqual(exact_paths["cwd"], Path(policy["workspace_policy"]["exact_final_source"]))
            self.assertIn("neutral, read-only", exact_instruction)
            self.assertNotIn(EXECUTOR_INSTRUCTIONS, " ".join(exact_argv))
            behavior_filesystem = next(value for value in config_values if ".filesystem=" in value)
            exact_configs = [exact_argv[index + 1] for index, value in enumerate(exact_argv[:-1]) if value == "--config"]
            exact_filesystem = next(value for value in exact_configs if ".filesystem=" in value)
            helper = exact_paths["command_bin"] / "codex-linux-sandbox"
            launcher = exact_paths["command_bin"] / "codex"
            self.assertEqual(exact_paths["launcher"], launcher)
            self.assertEqual(exact_argv[0], str(launcher))
            self.assertEqual(_mode(launcher), 0o500)
            self.assertEqual(
                (source.stat().st_dev, source.stat().st_ino),
                (launcher.stat().st_dev, launcher.stat().st_ino),
            )
            self.assertEqual(behavior_filesystem, 'permissions.happycodex_evaluator.filesystem={":minimal"="read",":workspace_roots"={"."="read"}}')
            self.assertIn(f'{json.dumps(str(helper))}="read"', exact_filesystem)
            self.assertIn(f'{json.dumps(str(launcher))}="read"', exact_filesystem)
            self.assertNotIn(json.dumps(str(exact_paths["command_bin"])) + "=", exact_filesystem)
            self.assertNotIn(":root", exact_filesystem)

    def test_same_authority_invocation_cannot_run_in_two_execution_roots(self):
        from evaluation.host import execute_fixed_host_transaction

        with tempfile.TemporaryDirectory() as directory:
            host_a = Path(directory) / "host-a"
            host_b = Path(directory) / "host-b"
            host_a.mkdir(mode=0o700)
            host_b.mkdir(mode=0o700)
            effect_markers = Path(directory) / "effect-markers"
            effect_markers.mkdir(mode=0o700)
            first = self._inputs(str(host_a), effect_marker_root=effect_markers)
            second = self._inputs(str(host_b), effect_marker_root=effect_markers)
            _, role_a, mapping_a, policy_a, selected_a, baseline_a, spec_a, blind_a = first
            _, role_b, mapping_b, policy_b, selected_b, baseline_b, spec_b, blind_b = second
            self.assertEqual(role_a.read_bytes(), role_b.read_bytes())
            self.assertEqual(mapping_a.read_bytes(), mapping_b.read_bytes())
            self.assertEqual(selected_a, selected_b)
            self.assertEqual(baseline_a, baseline_b)
            self.assertEqual(spec_a, spec_b)
            self.assertEqual(blind_a, blind_b)

            unit = next(item for item in spec_a["units"] if item["unit_id"] == "goal-divergence")
            supplied, _, line = self._authority(spec_a)
            provider_calls = []

            def fake_provider(**kwargs):
                provider_calls.append(str(kwargs["cwd"]))
                os.write(
                    kwargs["stdout_fd"],
                    _events(
                        {"type": "thread.started", "thread_id": "thread-cross-root"},
                        {"type": "turn.started"},
                        {"type": "item.completed", "item": {
                            "id": "message", "type": "agent_message",
                            "text": json.dumps(passing_report(unit), sort_keys=True),
                        }},
                        {"type": "turn.completed", "usage": {
                            "input_tokens": 5, "cached_input_tokens": 0,
                            "cache_write_input_tokens": 0, "output_tokens": 3,
                            "reasoning_output_tokens": 0,
                        }},
                    ),
                )
                return 0, False

            def execute(policy, selected, baseline, spec):
                return execute_fixed_host_transaction(
                    repo_root=ROOT, product=selected, previous_product=baseline,
                    spec=spec, unit_id=unit["unit_id"], policy=policy,
                    authority_line=line, supplied_authority=supplied,
                    authenticate_line=lambda actual, _value: actual == line,
                    provider_auth=b"private-auth", run_provider=fake_provider,
                    clock=lambda: datetime(2026, 8, 3, tzinfo=timezone.utc),
                )

            self.assertEqual(
                execute(policy_a, selected_a, baseline_a, spec_a)["attestation"]["verdict"],
                "pass",
            )
            with self.assertRaises(HostEvidenceError):
                execute(policy_b, selected_b, baseline_b, spec_b)
            self.assertEqual(len(provider_calls), 1)

    def test_effect_marker_is_cross_process_one_shot(self):
        from evaluation.host import _consume_effect_marker

        with tempfile.TemporaryDirectory() as directory:
            _, _, _, policy, _, _, _, _ = self._inputs(directory)
            policy_path = Path(directory) / "policy.json"
            policy_path.write_text(json.dumps(policy, sort_keys=True)); policy_path.chmod(0o600)
            _consume_effect_marker(
                policy, authority_sha256=SHA["a"], invocation_sha256=SHA["b"],
            )
            script = (
                "import json,sys;from pathlib import Path;"
                "from evaluation.host import _consume_effect_marker;"
                "p=json.loads(Path(sys.argv[1]).read_text());"
                "_consume_effect_marker(p,authority_sha256=sys.argv[2],invocation_sha256=sys.argv[3])"
            )
            child = subprocess.run(
                [sys.executable, "-c", script, str(policy_path), SHA["a"], SHA["b"]],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(child.returncode, 0)
            self.assertEqual(len(list(Path(policy["workspace_policy"]["effect_marker_root"]).iterdir())), 1)

    def test_legacy_path_lacks_required_sandbox_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy_usr = Path(directory) / "usr" / "bin"
            legacy_bin = Path(directory) / "bin"
            legacy_usr.mkdir(parents=True); legacy_bin.mkdir()
            self.assertIsNone(
                shutil.which("codex-linux-sandbox", path=f"{legacy_usr}:{legacy_bin}")
            )

    def test_real_linux_sandbox_needs_only_exact_helper_file_read(self):
        if os.uname().sysname != "Linux" or shutil.which("codex") is None:
            self.skipTest("real Codex Linux sandbox is unavailable")
        binary = Path(shutil.which("codex")).resolve()
        with tempfile.TemporaryDirectory(prefix="happycodex-sandbox-probe-") as directory:
            base = Path(directory); command_bin = base / "command-bin"
            command_bin.mkdir(mode=0o700)
            helper = command_bin / "codex-linux-sandbox"
            launcher = command_bin / "codex"
            os.link(binary, helper); os.link(binary, launcher); command_bin.chmod(0o500)
            cwd = base / "frozen-source"; cwd.mkdir(mode=0o500)
            home = base / "home"; home.mkdir(mode=0o700)
            codex_home = base / "codex-home"; codex_home.mkdir(mode=0o700)
            env = {"PATH": f"{command_bin}:/usr/bin:/bin", "HOME": str(home),
                   "CODEX_HOME": str(codex_home), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
            base_permissions = '{":minimal"="read",":workspace_roots"={"."="read"}'

            def run(extra: str):
                filesystem = base_permissions + extra + "}"
                return subprocess.run(
                    [str(launcher), "-c", 'permissions.probe.description="probe read only"',
                     "-c", f"permissions.probe.filesystem={filesystem}",
                     "-c", "permissions.probe.network.enabled=false",
                     "sandbox", "-P", "probe", "-C", str(cwd), "/bin/pwd"],
                    env=env, capture_output=True, text=True, timeout=20, check=False,
                )

            negative = run("")
            positive = run(
                f',{json.dumps(str(helper))}="read",{json.dumps(str(launcher))}="read"'
            )
            self.assertNotEqual(negative.returncode, 0)
            self.assertEqual(negative.stdout, "")
            self.assertNotEqual(negative.stderr, "")
            self.assertEqual(positive.returncode, 0)
            self.assertEqual(positive.stdout.strip(), str(cwd))
            self.assertIsInstance(positive.stderr, str)
            self.assertEqual(
                (binary.stat().st_dev, binary.stat().st_ino),
                (launcher.stat().st_dev, launcher.stat().st_ino),
            )

    def test_private_sandbox_alias_tamper_fails_closed(self):
        from evaluation.host import _prepare_unit
        from evaluation.provider import ProviderError, fixed_command_path

        for tamper in ("template", "directory-mode", "replacement"):
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory() as directory:
                _, _, _, policy, _, _, spec, _ = self._inputs(directory)
                unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
                paths = _prepare_unit(policy, unit)
                command_bin = paths["command_bin"]
                alias = command_bin / "codex-linux-sandbox"
                if tamper == "template":
                    policy["provider_policy"]["command_path_template"] = "/usr/bin:/bin"
                elif tamper == "directory-mode":
                    command_bin.chmod(0o700)
                else:
                    command_bin.chmod(0o700)
                    alias.unlink()
                    alias.write_bytes(Path(policy["provider_policy"]["binary_path"]).read_bytes())
                    alias.chmod(0o500)
                    command_bin.chmod(0o500)
                with self.assertRaises(ProviderError):
                    fixed_command_path(policy, command_bin)

    def test_exact_private_launcher_tamper_and_path_drift_fail_closed(self):
        from evaluation.host import _prepare_unit
        from evaluation.provider import ProviderError, fixed_host_argv, fixed_host_instruction

        for tamper in ("replacement", "path-drift"):
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory() as directory:
                _, _, _, policy, _, _, spec, _ = self._inputs(directory)
                exact = next(unit for unit in spec["units"] if unit["stage"] == "exact_final")
                paths = _prepare_unit(policy, exact)
                launcher = paths["launcher"]
                if tamper == "replacement":
                    command_bin = paths["command_bin"]
                    command_bin.chmod(0o700)
                    launcher.unlink()
                    launcher.write_bytes(Path(policy["provider_policy"]["binary_path"]).read_bytes())
                    launcher.chmod(0o500)
                    command_bin.chmod(0o500)
                else:
                    paths["launcher"] = Path(policy["provider_policy"]["binary_path"])
                with self.assertRaises(ProviderError):
                    fixed_host_argv(
                        policy, exact, paths, fixed_host_instruction(policy, exact),
                    )

    def test_exact_launcher_binding_changes_only_exact_host_identity(self):
        from evaluation.provider import host_contract_from_policy
        from evaluation.verify import invalidation

        with tempfile.TemporaryDirectory() as directory:
            _, _, _, policy, selected, baseline, _, blind = self._inputs(directory)
            captured = []

            def capture(value):
                captured.append(deepcopy(value))
                return canonical_sha256(value)

            with patch("evaluation.provider.canonical_sha256", side_effect=capture):
                contract = host_contract_from_policy(policy)
            surfaces = [value for value in captured if type(value) is dict and "sandbox_alias" in value]
            self.assertEqual(len(surfaces), 3)
            self.assertNotIn("launcher_alias", surfaces[0])
            self.assertNotIn("launcher_alias", surfaces[1])
            self.assertEqual(
                surfaces[2]["launcher_alias"],
                ["codex", "hard-link-to-provider-binary"],
            )
            legacy = {**contract, "exact_final_sha256": "4" * 64}
            _, _, previous, _ = bundle(
                selected_product=selected, baseline_product=baseline,
                host_contract=legacy,
            )
            _, _, current, _ = bundle(
                selected_product=selected, baseline_product=baseline,
                host_contract=contract,
            )
            self.assertEqual(blind, mapping())
            self.assertEqual(invalidation(previous, current), {"mode": "exact_final_only"})

    def test_exact_launcher_link_failure_stops_before_provider_reach(self):
        from evaluation.host import execute_fixed_host_transaction

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            supplied, authority, line = self._authority(spec)
            prior = {
                unit["unit_id"] for unit in spec["units"]
                if unit["stage"] != "exact_final"
            }
            self._persist(execution, selected, baseline, spec, prior, authority)
            real_link = os.link
            link_count = 0

            def fail_second_link(source, destination, **kwargs):
                nonlocal link_count
                link_count += 1
                if link_count == 2:
                    raise OSError(18, "cross-device launcher link")
                return real_link(source, destination, **kwargs)

            with patch("evaluation.host.os.link", side_effect=fail_second_link):
                with self.assertRaisesRegex(HostEvidenceError, "launcher hard link failed"):
                    execute_fixed_host_transaction(
                        repo_root=ROOT, product=selected, previous_product=baseline,
                        spec=spec, unit_id="exact-final", policy=policy,
                        authority_line=line, supplied_authority=supplied,
                        authenticate_line=lambda actual, _value: actual == line,
                        provider_auth=b"private-auth",
                        run_provider=lambda **_kwargs: self.fail("provider reached"),
                        clock=lambda: datetime(
                            2026, 8, 2, 0, 0, 35, tzinfo=timezone.utc,
                        ),
                    )
            for name in ("units", "raw", "attestations", "claims"):
                self.assertEqual(len(list((execution / name).iterdir())), 11)

    def test_cross_filesystem_sandbox_alias_fails_before_effect(self):
        from evaluation.host import _prepare_unit

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, _, _, spec, _ = self._inputs(directory)
            unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
            with patch("evaluation.host.os.link", side_effect=OSError(18, "cross-device link")):
                with self.assertRaisesRegex(HostEvidenceError, "hard link failed"):
                    _prepare_unit(policy, unit)
            self.assertEqual(list((execution / "units").iterdir()), [])
            self.assertEqual(list((execution / "claims").iterdir()), [])
            self.assertEqual(list((execution / "raw").iterdir()), [])

    def test_forged_prefix_raw_and_known_failure_or_cap_block_launch(self):
        from evaluation.host import execute_fixed_host_transaction

        for mode in ("forged", "failure", "cap"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
                supplied, authority, line = self._authority(spec)
                first = next(unit for unit in spec["units"] if unit["unit_id"] == "goal-divergence")
                values = {first["unit_id"]: terminal(input_tokens=10001)} if mode == "cap" else {}
                reports = {first["unit_id"]: {"safety": {"goal_closed": True}, "next_action": {"purpose": "STOP"}}} if mode == "failure" else {}
                self._persist(execution, selected, baseline, spec, {first["unit_id"]}, authority, terminal_values=values, reports=reports)
                if mode == "forged":
                    (execution / "raw" / f"{first['unit_id']}.jsonl").write_bytes(b"{}\n")
                with self.assertRaises(HostEvidenceError):
                    execute_fixed_host_transaction(
                        repo_root=ROOT, product=selected, previous_product=baseline,
                        spec=spec, unit_id="no-commit-secret", policy=policy,
                        authority_line=line, supplied_authority=supplied,
                        authenticate_line=lambda actual, _value: actual == line,
                        provider_auth=b"private-auth",
                        run_provider=lambda **_kwargs: self.fail("provider reached"),
                    )

    def test_only_same_stage_paired_inflight_prefix_is_legal(self):
        from evaluation.host import execute_fixed_host_transaction

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            supplied, _, line = self._authority(spec)
            first = next(unit for unit in spec["units"] if unit["unit_id"] == "goal-divergence")
            launch = next(unit for unit in spec["units"] if unit["unit_id"] == "no-commit-secret")
            owner = self._persist_inflight(execution, first)

            def provider(**kwargs):
                os.write(kwargs["stdout_fd"], raw_stream(launch))
                return 0, False

            try:
                result = execute_fixed_host_transaction(
                    repo_root=ROOT, product=selected, previous_product=baseline,
                    spec=spec, unit_id=launch["unit_id"], policy=policy,
                    authority_line=line, supplied_authority=supplied,
                    authenticate_line=lambda actual, _value: actual == line,
                    provider_auth=b"private-auth", run_provider=provider,
                )
            finally:
                fcntl.flock(owner, fcntl.LOCK_UN); os.close(owner)
            self.assertEqual(result["attestation"]["verdict"], "pass")
            with self.assertRaisesRegex(HostEvidenceError, "active provider owner"):
                execute_fixed_host_transaction(
                    repo_root=ROOT, product=selected, previous_product=baseline,
                    spec=spec, unit_id="qualification-high-risk", policy=policy,
                    authority_line=line, supplied_authority=supplied,
                    authenticate_line=lambda actual, _value: actual == line,
                    provider_auth=b"private-auth", run_provider=lambda **_kwargs: self.fail("provider reached"),
                )

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            supplied, authority, line = self._authority(spec)
            behavior = {unit["unit_id"] for unit in spec["units"] if unit["stage"] == "behavior"}
            self._persist(execution, selected, baseline, spec, behavior, authority)
            holdout = next(unit for unit in spec["units"] if unit["stage"] == "holdout")
            owner = self._persist_inflight(execution, holdout)
            try:
                with self.assertRaisesRegex(HostEvidenceError, "in-flight stage"):
                    execute_fixed_host_transaction(
                        repo_root=ROOT, product=selected, previous_product=baseline,
                        spec=spec, unit_id="exact-final", policy=policy,
                        authority_line=line, supplied_authority=supplied,
                        authenticate_line=lambda actual, _value: actual == line,
                        provider_auth=b"private-auth", run_provider=lambda **_kwargs: self.fail("provider reached"),
                    )
            finally:
                fcntl.flock(owner, fcntl.LOCK_UN); os.close(owner)

    def test_claim_directory_lock_is_cross_process(self):
        from evaluation.host import _lock_claims, _unlock_claims

        with tempfile.TemporaryDirectory() as directory:
            _, _, _, policy, _, _, _, _ = self._inputs(directory)
            policy_path = Path(directory) / "policy.json"
            policy_path.write_text(json.dumps(policy, sort_keys=True)); policy_path.chmod(0o600)
            marker = Path(directory) / "child-acquired"
            script = (
                "import json,sys;from pathlib import Path;"
                "from evaluation.host import _lock_claims,_unlock_claims;"
                "p=json.loads(Path(sys.argv[1]).read_text());fd=_lock_claims(p);"
                "Path(sys.argv[2]).write_text('acquired');_unlock_claims(fd)"
            )
            lock = _lock_claims(policy)
            try:
                child = subprocess.Popen(
                    [sys.executable, "-c", script, str(policy_path), str(marker)],
                    cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                )
                time.sleep(0.1)
                self.assertFalse(marker.exists())
            finally:
                _unlock_claims(lock)
            _, stderr = child.communicate(timeout=2)
            self.assertEqual(child.returncode, 0, stderr.decode())
            self.assertTrue(marker.exists())

    def test_current_cap_overrun_is_persisted_before_stop(self):
        from evaluation.host import execute_fixed_host_transaction

        cap = {"model_calls":12,"input_tokens":5,"output_tokens":10000,"wall_milliseconds":200000}
        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            selected, baseline, spec, _ = bundle(
                selected_product=selected, baseline_product=baseline,
                host_contract=spec["host_contract"], total_cap=cap,
                external_role_config_sha256=spec["external_role_config_sha256"],
            )
            unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
            supplied, _, line = self._authority(spec)

            def provider(**kwargs):
                os.write(kwargs["stdout_fd"], raw_stream(unit))
                return 0, False

            result = execute_fixed_host_transaction(
                repo_root=ROOT, product=selected, previous_product=baseline,
                spec=spec, unit_id=unit["unit_id"], policy=policy,
                authority_line=line, supplied_authority=supplied,
                authenticate_line=lambda actual, _value: actual == line,
                provider_auth=b"private-auth", run_provider=provider,
            )
            self.assertEqual(result["stop_reason"], "token_qualification_exceeded")
            self.assertEqual(result["token_exceeded"], ["input_tokens"])
            self.assertEqual(result["cap_exceeded"], [])
            for name in ("claims", "raw", "attestations"):
                self.assertEqual(len(list((execution / name).iterdir())), 1)

    def test_spawn_error_persists_no_effect_attestation(self):
        from evaluation.host import execute_fixed_host_transaction

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            supplied, _, line = self._authority(spec)
            def blocked_provider(**_kwargs):
                raise OSError("spawn blocked")

            result = execute_fixed_host_transaction(
                repo_root=ROOT, product=selected, previous_product=baseline,
                spec=spec, unit_id="goal-divergence", policy=policy,
                authority_line=line, supplied_authority=supplied,
                authenticate_line=lambda actual, _value: actual == line,
                provider_auth=b"private-auth", run_provider=blocked_provider,
            )
            self.assertEqual(result["attestation"]["terminal"]["classification"], "infrastructure_no_effect")
            self.assertEqual(len(list((execution / "claims").iterdir())), 1)
            self.assertEqual(len(list((execution / "raw").iterdir())), 1)
            self.assertEqual(len(list((execution / "attestations").iterdir())), 1)

    def test_auth_staging_failure_precedes_durable_claim_and_raw(self):
        import evaluation.host as host

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            supplied, _, line = self._authority(spec)
            exclusive = host._exclusive

            def fail_auth(path, body, mode):
                if path.name == "auth.json":
                    raise OSError("auth stage blocked")
                return exclusive(path, body, mode)

            with patch("evaluation.host._exclusive", side_effect=fail_auth), self.assertRaises(OSError):
                host.execute_fixed_host_transaction(
                    repo_root=ROOT, product=selected, previous_product=baseline,
                    spec=spec, unit_id="goal-divergence", policy=policy,
                    authority_line=line, supplied_authority=supplied,
                    authenticate_line=lambda actual, _value: actual == line,
                    provider_auth=b"private-auth",
                    run_provider=lambda **_kwargs: self.fail("provider reached"),
                )
            for name in ("claims", "raw", "attestations"):
                self.assertEqual(list((execution / name).iterdir()), [])

    def test_timeout_kills_descendant_process_group(self):
        from evaluation.host import _run_provider_once
        from evaluation.provider import accept_evaluation_authority

        with tempfile.TemporaryDirectory() as directory:
            _, _, _, _, _, _, spec, _ = self._inputs(directory)
            supplied, _, _ = self._authority(spec)
            capability = accept_evaluation_authority(spec, supplied, lambda _value: True)
            marker = Path(directory) / "descendant-survived"
            script = (
                "import subprocess,time,sys;"
                "subprocess.Popen([sys.executable,'-c',"
                + repr(f"import time;time.sleep(0.3);open({str(marker)!r},'w').write('alive')")
                + "]);time.sleep(30)"
            )
            raw_path = Path(directory) / "timeout.jsonl"
            descriptor = os.open(raw_path, os.O_WRONLY | os.O_CREAT, 0o600)
            try:
                _, timed_out = _run_provider_once(
                    capability, spec, argv=[sys.executable, "-c", script], stdin=b"",
                    env=dict(os.environ), cwd=Path(directory), timeout_seconds=0.1,
                    stdout_fd=descriptor, runner=None,
                )
            finally:
                os.close(descriptor)
            self.assertTrue(timed_out)
            time.sleep(0.5)
            self.assertFalse(marker.exists())

    def test_exact_final_returns_authoritative_reveal_timestamp(self):
        from evaluation.host import execute_fixed_host_transaction, reveal_holdout_mapping

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, blind = self._inputs(directory)
            supplied, authority, line = self._authority(spec)
            prior = {unit["unit_id"] for unit in spec["units"] if unit["stage"] != "exact_final"}
            self._persist(execution, selected, baseline, spec, prior, authority)
            exact = next(unit for unit in spec["units"] if unit["stage"] == "exact_final")
            forged_path = next((execution / "raw").glob("holdout-*.jsonl"))
            original = forged_path.read_bytes(); forged_path.write_bytes(b"{}\n")
            with self.assertRaisesRegex(HostEvidenceError, "six durable"):
                reveal_holdout_mapping(
                    spec=spec, policy=policy, candidate_product=selected,
                    previous_product=baseline, authority_sha256=authority,
                    repo_root=ROOT,
                )
            forged_path.write_bytes(original)

            adverse = {"neutral":False,"coverage":{"complete":False},"decision":"NOT_YET","findings":[{"summary":"blocker"}]}

            def provider(**kwargs):
                os.write(kwargs["stdout_fd"], raw_stream(exact, report=adverse))
                return 0, False

            times = iter(datetime(2026, 8, 2, 0, 0, second, tzinfo=timezone.utc) for second in (35, 40, 42))
            result = execute_fixed_host_transaction(
                repo_root=ROOT, product=selected, previous_product=baseline,
                spec=spec, unit_id=exact["unit_id"], policy=policy,
                authority_line=line, supplied_authority=supplied,
                authenticate_line=lambda actual, _value: actual == line,
                provider_auth=b"private-auth", run_provider=provider,
                clock=lambda: next(times),
            )
            self.assertEqual(result["holdout_reveal"]["mapping"], blind)
            self.assertEqual(result["holdout_reveal"]["revealed_at"], "2026-08-02T00:00:35Z")
            self.assertEqual(result["stop_reason"], "terminal_failure")
            self.assertEqual(result["attestation"]["observation"]["report"], adverse)
            self.assertLess(
                result["holdout_reveal"]["revealed_at"],
                result["attestation"]["observation"]["started_at"],
            )

    def test_fake_host_exact_only_refresh_composes_without_importing_prefix(self):
        from evaluation.host import execute_fixed_host_transaction
        from evaluation.provider import host_contract_from_policy
        from evaluation.verify import exact_final_authority_proposal, verify_evaluation

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, previous, blind = self._inputs(directory)
            records, raws = attest_all(selected, baseline, previous)
            prior = [record for record in records if record["unit_id"] != "exact-final"]
            prior_raws = {key: value for key, value in raws.items() if key != "exact-final"}
            prior_proposal = evaluation_authority_request_payload(previous)
            prior_supplied = {"scope": "evaluation", "request_sha256": canonical_sha256(prior_proposal), "nonce": "n1", "signature": "s1"}
            prior_authority = canonical_sha256(prior_supplied)
            prior = [reseal({**record, "authority_sha256": prior_authority}) for record in prior]
            current_policy = deepcopy(policy)
            current_policy["provider_policy"]["exact_final_developer_instructions"] += " Confirm the inspected tree."
            contract = host_contract_from_policy(current_policy)
            _, _, current, _ = bundle(
                selected_product=selected, baseline_product=baseline,
                host_contract=contract,
                external_role_config_sha256=previous["external_role_config_sha256"],
            )
            cap = {**current["effect_cap"], "model_calls": 1}
            proposal = exact_final_authority_proposal(
                root=ROOT, product=selected, previous_product=baseline,
                previous_spec=previous, spec=current, attestations=prior,
                raw_streams=prior_raws, holdout_mapping=blind,
                mapping_revealed_at="2026-08-02T00:00:35Z", effect_cap=cap,
            )
            request = canonical_sha256(proposal)
            supplied = {"scope": "evaluation", "request_sha256": request, "nonce": "n2", "signature": "s2"}
            line = f"APPROVE HAPPYCODEX EVALUATION {request}"
            exact = next(unit for unit in current["units"] if unit["stage"] == "exact_final")

            def provider(**kwargs):
                os.write(kwargs["stdout_fd"], raw_stream(exact))
                return 0, False

            times = iter(datetime(2026, 8, 2, 0, 0, second, tzinfo=timezone.utc) for second in (36, 40, 42))
            result = execute_fixed_host_transaction(
                repo_root=ROOT, product=selected, previous_product=baseline,
                spec=current, unit_id="exact-final", policy=current_policy,
                authority_line=line, supplied_authority=supplied,
                authenticate_line=lambda actual, _value: actual == line,
                provider_auth=b"private-auth", run_provider=provider,
                clock=lambda: next(times), authority_proposal=proposal,
                previous_spec=previous, prerequisite_attestations=prior,
                prerequisite_raw_streams=prior_raws, holdout_mapping=blind,
                mapping_revealed_at="2026-08-02T00:00:35Z",
            )
            self.assertEqual(result["attestation"]["verdict"], "pass")
            self.assertEqual(len(list((execution / "attestations").iterdir())), 1)
            raw = Path(result["raw_path"]).read_bytes()
            composed = verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=current,
                previous_spec=previous,
                attestations=[*prior, result["attestation"]],
                raw_streams={**prior_raws, "exact-final": raw},
                holdout_mapping=blind, mapping_revealed_at="2026-08-02T00:00:35Z",
                authority_bindings={
                    prior_authority: {"proposal": prior_proposal, "supplied_authority": prior_supplied},
                    result["attestation"]["authority_sha256"]: {"proposal": proposal, "supplied_authority": supplied},
                },
            )
            self.assertTrue(composed["verified"])
            self.assertEqual(len(composed["authority_sha256s"]), 2)

    def test_baseline_fatal_still_reveals_all_six_for_unified_judgment(self):
        from evaluation.host import reveal_holdout_mapping

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, blind = self._inputs(directory)
            _, authority, _ = self._authority(spec)
            baseline_units = {
                unit_id
                for pair in blind.values()
                for unit_id, label in pair.items()
                if label == "baseline"
            }
            reports = {
                unit_id: {
                    "decision": {"safe": False}, "coverage": {"complete": True},
                    "identity": {"bound": True}, "quality_score": 0,
                    "fatal_invariants": [],
                }
                for unit_id in baseline_units
            }
            prior = {unit["unit_id"] for unit in spec["units"] if unit["stage"] != "exact_final"}
            self._persist(execution, selected, baseline, spec, prior, authority, reports=reports)
            revealed = reveal_holdout_mapping(
                spec=spec, policy=policy, candidate_product=selected,
                previous_product=baseline, authority_sha256=authority,
                repo_root=ROOT,
                now=lambda: datetime(2026, 8, 2, 0, 0, 35, tzinfo=timezone.utc),
            )
            self.assertEqual(revealed["mapping"], blind)
            self.assertTrue(revealed["judgment"]["passed"])
            self.assertTrue(all(
                not pair["baseline_absolute_passed"]
                for pair in revealed["judgment"]["pairs"]
            ))

    def test_failed_unified_holdout_judgment_blocks_exact_provider(self):
        from evaluation.host import execute_fixed_host_transaction

        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, blind = self._inputs(directory)
            supplied, authority, line = self._authority(spec)
            candidate_units = {
                unit_id
                for pair in blind.values()
                for unit_id, label in pair.items()
                if label == "candidate"
            }
            reports = {
                unit_id: {
                    "decision": {"safe": False}, "coverage": {"complete": True},
                    "identity": {"bound": True}, "quality_score": 0,
                    "fatal_invariants": [],
                }
                for unit_id in candidate_units
            }
            prior = {unit["unit_id"] for unit in spec["units"] if unit["stage"] != "exact_final"}
            self._persist(execution, selected, baseline, spec, prior, authority, reports=reports)
            result = execute_fixed_host_transaction(
                repo_root=ROOT, product=selected, previous_product=baseline,
                spec=spec, unit_id="exact-final", policy=policy,
                authority_line=line, supplied_authority=supplied,
                authenticate_line=lambda actual, _value: actual == line,
                provider_auth=b"private-auth",
                run_provider=lambda **_kwargs: self.fail("exact provider reached"),
                clock=lambda: datetime(2026, 8, 2, 0, 0, 35, tzinfo=timezone.utc),
            )
            self.assertEqual(result["stop_reason"], "holdout_failure")
            self.assertFalse(result["holdout_reveal"]["judgment"]["passed"])
            self.assertIsNone(result["attestation"])
            self.assertFalse((execution / "raw" / "exact-final.jsonl").exists())
            self.assertFalse((execution / "attestations" / "exact-final.json").exists())


if __name__ == "__main__":
    unittest.main()
