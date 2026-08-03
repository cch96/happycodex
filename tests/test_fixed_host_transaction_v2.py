from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from evaluation.cli import parser
from evaluation.host import HostEvidenceError, attestation_from_raw
from evaluation.manifest import ManifestError, _validate_structural_schema
from evaluation.provider import BEHAVIOR_DEVELOPER_INSTRUCTIONS
from tests.attestation_fixtures import (
    HOST_CONTRACT, ROOT, SHA, bundle, host_metadata, mapping, passing_report,
    previous_product, product,
)


FAKE_BINARY = ROOT / "tests" / "fake_external_host.py"
EXECUTOR_INSTRUCTIONS = BEHAVIOR_DEVELOPER_INSTRUCTIONS


def _events(*items: dict) -> bytes:
    return b"".join(
        (json.dumps(item, sort_keys=True) + "\n").encode() for item in items
    )


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


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
        snapshot = execution / "exact-final-source"
        snapshot.mkdir(mode=0o500)
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
        policy = build_fixed_host_policy(
            execution_root=execution, binary_path=FAKE_BINARY,
            external_role_config_path=role, exact_final_source=snapshot,
            holdout_mapping_path=mapping_path, behavior_model="gpt-fake",
        )
        contract = host_contract_from_policy(policy)
        selected = product(role=role_sha)
        baseline = previous_product(role=role_sha)
        selected, baseline, spec, blind = bundle(
            selected_product=selected, baseline_product=baseline,
            host_contract=contract,
        )
        return execution, role, mapping_path, policy, selected, baseline, spec, blind

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
            self.assertNotIn("tool-bin", " ".join(captured["argv"]))
            self.assertIn(
                "developer_instructions=" + json.dumps(EXECUTOR_INSTRUCTIONS),
                captured["argv"],
            )
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


if __name__ == "__main__":
    unittest.main()
