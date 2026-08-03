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
import time
import unittest
from unittest.mock import patch

from evaluation.cli import parser
from evaluation.host import HostEvidenceError, attestation_from_raw
from evaluation.manifest import ManifestError, _validate_structural_schema
from evaluation.provider import BEHAVIOR_DEVELOPER_INSTRUCTIONS
from evaluation.records import canonical_sha256
from tests.attestation_fixtures import (
    HOST_CONTRACT, ROOT, SHA, bundle, host_metadata, mapping, passing_report,
    previous_product, product, raw_stream, terminal,
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


def _synthetic_snapshot(
    base: Path, *, hidden_file: bool = False, hidden_diff: bool = False,
    untracked_support: bool = False,
) -> tuple[Path, Path]:
    snapshot = base / "execution" / "exact-final-source"
    snapshot.mkdir(mode=0o700)
    oracle = base / "private" / "evaluation" / "hidden-oracles-v1.json"
    oracle.parent.mkdir(parents=True)
    oracle.write_bytes((ROOT / "evaluation" / "hidden-oracles-v1.json").read_bytes())
    body = oracle.read_bytes()
    readme = snapshot / "README.md"
    readme.write_text("frozen exact-final source\n", encoding="utf-8")
    diff = snapshot / "EXACT_FINAL_DIFF.patch"
    if hidden_diff:
        diff.write_bytes(
            b"diff --git a/public-copy.json b/public-copy.json\n"
            b"--- a/public-copy.json\n+++ b/public-copy.json\n@@ -1,22 +1,22 @@\n"
            + b"".join(b" " + line for line in body.splitlines(keepends=True))
            + b"-old trailer\n+new trailer\n"
        )
    else:
        diff.write_bytes(
            b"diff --git a/README.md b/README.md\n--- a/README.md\n+++ b/README.md\n"
        )
    private = {
        "path": "evaluation/hidden-oracles-v1.json", "git_mode": "100644",
        "git_object": _git_blob_sha(body), "sha256": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
    }
    manifest = {
        "aggregate_diff": {
            "path": diff.name, "sha256": hashlib.sha256(diff.read_bytes()).hexdigest(),
            "size_bytes": diff.stat().st_size,
        },
        "private_exclusion": private,
        "projection": {"included_paths": ["README.md"], "file_count": 1},
        "source_commit": "1" * 40, "source_tree": "2" * 40,
    }
    (snapshot / "EXACT_FINAL_SOURCE_MANIFEST.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8",
    )
    if hidden_file:
        path = snapshot / private["path"]
        path.parent.mkdir(parents=True)
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
        self.assertIn("provider_policy_sha256", HOST_CONTRACT)
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
    def _inputs(self, directory: str):
        from evaluation.host import build_fixed_host_policy, host_contract_from_policy

        base = Path(directory)
        execution = base / "execution"
        for path in (
            execution, execution / "units", execution / "raw",
            execution / "attestations", execution / "claims",
        ):
            path.mkdir(mode=0o700)
        snapshot, private_oracle = _synthetic_snapshot(base)
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
            behavior_model="gpt-fake",
        )
        contract = host_contract_from_policy(policy)
        selected = product(role=role_sha)
        baseline = previous_product(role=role_sha)
        selected, baseline, spec, blind = bundle(
            selected_product=selected, baseline_product=baseline,
            host_contract=contract,
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
            self.assertEqual(
                set(subprocess.check_output(
                    ["git", "-C", str(source), "ls-files"], text=True,
                    env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
                ).splitlines()),
                {"README.md", "EXACT_FINAL_DIFF.patch", "EXACT_FINAL_SOURCE_MANIFEST.json"},
            )
            relocated = Path(directory) / "relocated"
            shutil.copytree(source, relocated)
            self.assertEqual(
                policy["workspace_policy"]["exact_final_source_sha256"],
                exact_final_source_identity(relocated, private),
            )
            self.assertEqual(list((execution / "units").iterdir()), [])

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
                exact_final_source_identity(source, private)
            self.assertEqual(list((execution / "claims").iterdir()), [])

        for exposure in ("file", "diff"):
            with self.subTest(exposure=exposure), tempfile.TemporaryDirectory() as directory:
                base = Path(directory); (base / "execution").mkdir(mode=0o700)
                source, private = _synthetic_snapshot(
                    base, hidden_file=exposure == "file", hidden_diff=exposure == "diff",
                )
                with self.assertRaisesRegex(ProviderError, "hidden oracle"):
                    exact_final_source_identity(source, private)

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); (base / "execution").mkdir(mode=0o700)
            source, private = _synthetic_snapshot(base, untracked_support=True)
            with self.assertRaisesRegex(ProviderError, "clean synthetic commit"):
                exact_final_source_identity(source, private)

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

    def test_legacy_path_lacks_required_sandbox_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy_usr = Path(directory) / "usr" / "bin"
            legacy_bin = Path(directory) / "bin"
            legacy_usr.mkdir(parents=True); legacy_bin.mkdir()
            self.assertIsNone(
                shutil.which("codex-linux-sandbox", path=f"{legacy_usr}:{legacy_bin}")
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
                values = {first["unit_id"]: terminal(input_tokens=10000)} if mode == "cap" else {}
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

        cap = {"model_calls":12,"input_tokens":5,"output_tokens":10000,"wall_milliseconds":200000,"infrastructure_recoveries":1}
        with tempfile.TemporaryDirectory() as directory:
            execution, _, _, policy, selected, baseline, spec, _ = self._inputs(directory)
            selected, baseline, spec, _ = bundle(selected_product=selected, baseline_product=baseline, host_contract=spec["host_contract"], total_cap=cap)
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
            self.assertEqual(result["stop_reason"], "total_cap_exceeded")
            self.assertEqual(result["cap_exceeded"], ["input_tokens"])
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
