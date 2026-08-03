from __future__ import annotations

from copy import deepcopy
import json
import pickle
from pathlib import Path
import subprocess
import tempfile
import unittest

from evaluation.host import HostEvidenceError, attestation_from_raw, parse_raw_stream, reserve_claim
from evaluation.identity import (
    DETERMINISTIC_DOMAINS, MODEL_ROLE_IDS, IdentityError,
    product_artifact_from_git,
)
from evaluation.manifest import ManifestError
from evaluation.provider import (
    EvaluationCapability, ProviderError, accept_evaluation_authority,
    assert_provider_blind, provider_projection, sanitize_events,
)
from evaluation.records import (
    RECORD_TYPES, TERMINAL_CLASSES, RecordError, build_product_artifact,
    validate_record,
)
from evaluation.verify import evaluate_runtime_decision
from tests.attestation_fixtures import (
    BASELINE_REVISION, CANDIDATE_REVISION, HOST_CONTRACT, PROFILES, ROOT, SHA,
    bundle, host_metadata, product, raw_stream, terminal,
)


def source_runtime(root: Path, product_record: dict) -> str:
    return subprocess.check_output(
        [
            "git", "-C", str(root), "show",
            f"{product_record['source_commit']}:skills/happycodex/SKILL.md",
        ]
    ).decode()


class DurableRecordTests(unittest.TestCase):
    def test_inventory_is_closed_to_four_types(self):
        self.assertEqual(RECORD_TYPES, frozenset({"ProductArtifact", "EvalSpec", "Attestation", "ReleaseReceipt"}))
        for retired in ("ReleaseCandidate", "GatePlan", "GateReceipt", "EvidenceJoin"):
            with self.assertRaises(RecordError):
                validate_record({"record_type": retired})

    def test_product_has_no_evaluator_identity(self):
        selected = product()
        self.assertFalse(any("evaluator" in key for key in selected))
        self.assertEqual(validate_record(selected), selected)

    def test_unknown_field_and_tampered_digest_fail(self):
        selected = product()
        with self.assertRaises(RecordError):
            validate_record({**selected, "ledger_sha256": SHA["4"]})
        with self.assertRaises(RecordError):
            validate_record({**selected, "package_artifact_sha256": SHA["4"]})

    def test_materialized_spec_has_real_invocations_and_separate_arm_configs(self):
        selected, baseline, spec, _ = bundle()
        expected_units = {
            "goal-divergence", "no-commit-secret", "qualification-high-risk",
            "qualification-low-risk", "qualification-midflight",
            "holdout-recovery-arm-a", "holdout-recovery-arm-b",
            "holdout-safety-arm-a", "holdout-safety-arm-b",
            "holdout-scope-arm-a", "holdout-scope-arm-b", "exact-final",
        }
        self.assertEqual(spec["total_cap"]["model_calls"], 12)
        self.assertEqual(baseline["source_commit"], BASELINE_REVISION)
        self.assertEqual({unit["unit_id"] for unit in spec["units"]}, expected_units)
        self.assertEqual(len(spec["units"]), 12)
        expected_runtimes = {
            selected["package_semantic_sha256"]: source_runtime(ROOT, selected),
            baseline["package_semantic_sha256"]: source_runtime(ROOT, baseline),
        }
        self.assertNotEqual(*expected_runtimes.values())
        for unit in spec["units"]:
            projection = unit["invocation"]["provider_input"]
            self.assertIn("fixture", projection)
            self.assertIn("workspace", projection)
            self.assertIn("runtime", projection)
            self.assertIn("response_schema", projection)
            self.assertNotIn("fatal", str(projection["response_schema"]).lower())
            self.assertNotIn("expected", str(projection["response_schema"]).lower())
            expected = selected if unit["product_semantic_sha256"] == selected["package_semantic_sha256"] else baseline
            self.assertEqual(unit["external_role_config_sha256"], expected["external_role_config_sha256"])
            self.assertEqual(projection["runtime"], expected_runtimes[unit["product_semantic_sha256"]])
        units = {unit["unit_id"]: unit for unit in spec["units"]}
        for pair in spec["holdouts"]:
            left, right = (units[unit_id] for unit_id in pair["unit_ids"])
            for field in ("model", "effort", "tools", "timeout_seconds"):
                self.assertEqual(left["invocation"][field], right["invocation"][field])
            self.assertEqual(left["external_role_config_sha256"], right["external_role_config_sha256"])

    def test_dirty_worktree_runtime_cannot_replace_frozen_arm_sources(self):
        with tempfile.TemporaryDirectory() as raw:
            clone = Path(raw) / "repo"
            subprocess.run(
                ["git", "clone", "--shared", "--quiet", str(ROOT), str(clone)],
                check=True,
            )
            selected = product_artifact_from_git(
                clone, CANDIDATE_REVISION,
                external_role_config_sha256=SHA["3"],
            )
            baseline = product_artifact_from_git(
                clone, BASELINE_REVISION,
                external_role_config_sha256=SHA["3"],
            )
            dirty = "DIRTY MUTABLE RUNTIME MUST NEVER REACH AN ARM\n"
            (clone / "skills" / "happycodex" / "SKILL.md").write_text(dirty)
            _, _, spec, _ = bundle(
                root=clone, selected_product=selected, baseline_product=baseline,
            )
            expected = {
                selected["package_semantic_sha256"]: source_runtime(clone, selected),
                baseline["package_semantic_sha256"]: source_runtime(clone, baseline),
            }
            for unit in spec["units"]:
                runtime = unit["invocation"]["provider_input"]["runtime"]
                self.assertEqual(runtime, expected[unit["product_semantic_sha256"]])
                self.assertNotEqual(runtime, dirty)

    def test_forged_or_unavailable_product_source_fails_closed(self):
        selected = product()
        for name, source_commit, source_tree in (
            ("forged", selected["source_commit"], "0" * 40),
            ("unavailable", "0" * 40, selected["source_tree"]),
        ):
            forged = build_product_artifact(
                source_commit=source_commit, source_tree=source_tree,
                package_tree=selected["package_tree"],
                package_artifact_sha256=selected["package_artifact_sha256"],
                package_semantic_sha256=selected["package_semantic_sha256"],
                external_role_config_sha256=selected["external_role_config_sha256"],
            )
            with self.subTest(name=name), self.assertRaises(IdentityError):
                bundle(selected_product=forged)
        mismatched_config = product_artifact_from_git(
            ROOT, BASELINE_REVISION, external_role_config_sha256=SHA["6"],
        )
        with self.assertRaisesRegex(ManifestError, "one external role config"):
            bundle(baseline_product=mismatched_config)

    def test_model_and_deterministic_routes_are_disjoint(self):
        self.assertEqual(
            MODEL_ROLE_IDS,
            (
                "goal-divergence", "no-commit-secret",
                "qualification-high-risk", "qualification-low-risk",
                "qualification-midflight",
            ),
        )
        self.assertEqual(DETERMINISTIC_DOMAINS, {"receipt", "claim", "schema", "parser", "invalidation", "review-truncation", "install", "rollback"})


class ProviderBoundaryTests(unittest.TestCase):
    def test_projection_uses_actual_inputs_and_omits_hidden_fields(self):
        case = {
            "role_id": "qualification-high-risk", "prompt": "classify",
            "fixture": {"request": "write"}, "workspace": {"clean": True},
            "runtime": "runtime", "oracle": "HIDDEN", "mapping": "HIDDEN",
            "response_schema": {"type": "object"},
        }
        value = provider_projection(
            case=case, product_semantic_sha256=SHA["2"],
            external_role_config_sha256=SHA["3"], profile=PROFILES["behavior"],
        )
        self.assertNotIn("HIDDEN", str(value))
        self.assertEqual(value["runtime"], "runtime")

    def test_digest_only_projection_is_rejected(self):
        with self.assertRaises(ProviderError):
            provider_projection(
                case={"role_id": "x", "prompt": "x", "fixture_sha256": SHA["1"]},
                product_semantic_sha256=SHA["2"], external_role_config_sha256=SHA["3"],
                profile=PROFILES["behavior"],
            )

    def test_every_visible_surface_rejects_sentinel(self):
        for field in ("workspace", "argv", "stdin", "env", "sanitized_events"):
            visible = {"workspace": {}, "argv": [], "stdin": "", "env": {}, "sanitized_events": []}
            visible[field] = {"x": "SENTINEL"} if field in {"workspace", "env"} else (["SENTINEL"] if field in {"argv", "sanitized_events"} else "SENTINEL")
            with self.subTest(field=field), self.assertRaises(ProviderError):
                assert_provider_blind(sentinels=["SENTINEL"], projection={"safe": True}, **visible)

    def test_sanitized_events_redact_secret(self):
        value = sanitize_events([{"summary": "SENTINEL", "secret": "SENTINEL"}], secrets=["SENTINEL"])
        self.assertNotIn("SENTINEL", str(value))
        self.assertEqual(value[0]["secret"], "<redacted>")

    def test_authority_is_external_and_capability_process_local(self):
        _, _, spec, _ = bundle()
        supplied = {"scope": "evaluation", "request_sha256": spec["authority_request_sha256"], "nonce": "n", "signature": "s"}
        with self.assertRaises(ProviderError):
            accept_evaluation_authority(spec, supplied, lambda _value: False)
        capability = accept_evaluation_authority(spec, supplied, lambda _value: True)
        with self.assertRaises(TypeError):
            pickle.dumps(capability)
        with self.assertRaises(ProviderError):
            EvaluationCapability(object(), SHA["1"], SHA["2"], SHA["3"])

    def test_legacy_host_contract_field_is_rejected(self):
        contract = deepcopy(HOST_CONTRACT)
        contract["pro" + "of_" + "ver" + "ifier_sha256"] = SHA["1"]
        with self.assertRaises(RecordError):
            bundle(host_contract=contract)


class ExternalHostClaimTests(unittest.TestCase):
    def test_native_codex_stream_extracts_single_agent_report_and_usage(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        report = {"safety": {"goal_closed": False}, "next_action": {"purpose": "IMPLEMENT"}}
        secret = "RAW-TOOL-OUTPUT-SENTINEL"
        events = [
            {"type": "thread.started", "thread_id": "thread-1"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"id": "item-1", "type": "command_execution", "status": "in_progress", "command": secret, "aggregated_output": "", "exit_code": None}},
            {"type": "item.completed", "item": {"id": "item-1", "type": "command_execution", "status": "completed", "command": secret, "aggregated_output": secret, "exit_code": 0}},
            {"type": "item.completed", "item": {"id": "message-1", "type": "agent_message", "text": json.dumps(report)}},
            {"type": "turn.completed", "usage": {"input_tokens": 12, "cached_input_tokens": 3, "cache_write_input_tokens": 0, "output_tokens": 4, "reasoning_output_tokens": 2}},
        ]
        raw = b"".join((json.dumps(event, sort_keys=True) + "\n").encode() for event in events)
        parsed = parse_raw_stream(raw)
        self.assertEqual(parsed["report"], report)
        self.assertEqual(parsed["usage"]["input_tokens"], 12)
        self.assertTrue(parsed["turn_started"])
        self.assertTrue(parsed["turn_completed"])
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
            raw=raw, host_metadata=host_metadata(unit), authority_sha256=SHA["a"],
        )
        self.assertNotIn(secret, str(record))

    def test_native_parser_rejects_legacy_duplicate_and_malformed_shapes(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        valid = [json.loads(line) for line in raw_stream(unit).decode().splitlines()]
        legacy = [
            {"type": "started", "at": "2026-08-02T00:00:00Z"},
            {"type": "report", "report": {}},
            {"type": "usage", "model_calls": 1, "input_tokens": 1, "output_tokens": 1, "wall_milliseconds": 1},
            {"type": "terminal", "classification": "success", "provider_reached": True, "complete": True, "at": "2026-08-02T00:00:01Z"},
        ]
        duplicate_turn = [*valid[:2], {"type": "turn.started"}, *valid[2:]]
        missing_message = [*valid[:2], valid[-1]]
        malformed_message = deepcopy(valid)
        malformed_message[-2]["item"]["text"] = "not-json"
        terminal_not_last = [*valid, {"type": "turn.started"}]
        malformed_usage = deepcopy(valid)
        del malformed_usage[-1]["usage"]["cached_input_tokens"]
        duplicate_message = [*valid[:-1], deepcopy(valid[-2]), valid[-1]]
        forbidden_terminal = [*valid[:-1], {"type": "turn.failed", "error": "x"}]
        for name, events in (
            ("legacy", legacy),
            ("duplicate-turn", duplicate_turn),
            ("missing-message", missing_message),
            ("malformed-message", malformed_message),
            ("terminal-order", terminal_not_last),
            ("usage", malformed_usage),
            ("duplicate-message", duplicate_message),
            ("forbidden-terminal", forbidden_terminal),
        ):
            raw = b"".join((json.dumps(event, sort_keys=True) + "\n").encode() for event in events)
            with self.subTest(name=name), self.assertRaises(HostEvidenceError):
                parse_raw_stream(raw)

    def test_host_metadata_is_closed_and_terminal_facts_are_derived(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        raw = raw_stream(unit)
        metadata = host_metadata(unit)
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
            raw=raw, host_metadata=metadata, authority_sha256=SHA["a"],
        )
        self.assertEqual(record["terminal"]["classification"], "success")
        self.assertEqual(record["terminal"]["wall_milliseconds"], 10000)
        self.assertEqual(record["terminal"]["model_calls"], 1)
        self.assertEqual(record["terminal"]["input_tokens"], 10)
        with self.assertRaises(HostEvidenceError):
            attestation_from_raw(
                root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
                raw=raw, host_metadata={**metadata, "report": {}},
                authority_sha256=SHA["a"],
            )

    def test_timeout_post_turn_nonzero_and_exit_zero_empty_are_ambiguous(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        success_raw = raw_stream(unit)
        cases = (
            (success_raw, host_metadata(unit, timed_out=True)),
            (success_raw, host_metadata(unit, exit_code=1)),
            (b"", host_metadata(unit, exit_code=0)),
        )
        for raw, metadata in cases:
            record = attestation_from_raw(
                root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
                raw=raw, host_metadata=metadata, authority_sha256=SHA["a"],
            )
            self.assertEqual(record["terminal"]["classification"], "ambiguous_or_partial")
            self.assertFalse(record["terminal"]["complete"])

    def test_claim_is_cross_process_durable_and_one_shot(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            root.chmod(0o700)
            first = reserve_claim(root=root, claim_key=SHA["1"], invocation_sha256=SHA["2"])
            self.assertTrue(Path(first["path"]).exists())
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "claim",
                    "--claim-root", str(root), "--claim-key", SHA["1"],
                    "--invocation-sha256", SHA["2"],
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(completed.returncode, 0)

    def test_only_proven_no_effect_can_use_bounded_recovery_claim(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        no_effect = terminal(classification="infrastructure_no_effect", provider_reached=False, complete=False, model_calls=0, input_tokens=0, output_tokens=0)
        partial = terminal(classification="ambiguous_or_partial", complete=False)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            root.chmod(0o700)
            no_effect_raw = raw_stream(unit, terminal_value=no_effect)
            no_effect_record = attestation_from_raw(
                root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
                raw=no_effect_raw, host_metadata=host_metadata(unit, terminal_value=no_effect),
                authority_sha256=SHA["a"],
            )
            self.assertEqual(no_effect_record["terminal"]["classification"], "infrastructure_no_effect")
            reserve_claim(root=root, claim_key=unit["invocation"]["claim_key"], invocation_sha256=unit["invocation_sha256"])
            with self.assertRaises(HostEvidenceError):
                reserve_claim(
                    root=root, claim_key=unit["invocation"]["claim_key"],
                    invocation_sha256=unit["invocation_sha256"], recovery_index=1,
                    recovery_cap=1, previous_raw=no_effect_raw,
                )
            recovered = reserve_claim(
                root=root, claim_key=unit["invocation"]["claim_key"],
                invocation_sha256=unit["invocation_sha256"], recovery_index=1,
                recovery_cap=1, previous_raw=no_effect_raw,
                previous_attestation=no_effect_record, previous_spec=spec,
            )
            self.assertEqual(recovered["recovery_index"], 1)
            mismatched_raw = (json.dumps({"type": "thread.started", "thread_id": "mismatch"}) + "\n").encode()
            with self.assertRaises(HostEvidenceError):
                reserve_claim(
                    root=root, claim_key=unit["invocation"]["claim_key"],
                    invocation_sha256=unit["invocation_sha256"], recovery_index=2,
                    recovery_cap=2, previous_raw=mismatched_raw,
                    previous_attestation=no_effect_record, previous_spec=spec,
                )
            partial_raw = raw_stream(unit, terminal_value=partial)
            partial_record = attestation_from_raw(
                root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
                raw=partial_raw, host_metadata=host_metadata(unit, terminal_value=partial),
                authority_sha256=SHA["a"],
            )
            with self.assertRaises(HostEvidenceError):
                reserve_claim(
                    root=root, claim_key=unit["invocation"]["claim_key"],
                    invocation_sha256=unit["invocation_sha256"], recovery_index=2,
                    recovery_cap=2, previous_raw=partial_raw,
                    previous_attestation=partial_record, previous_spec=spec,
                )

    def test_raw_parser_rejects_incomplete_or_reordered_stream(self):
        with self.assertRaises(HostEvidenceError):
            parse_raw_stream(b'{"type":"report","report":{}}\n')


class OracleSemanticsTests(unittest.TestCase):
    def test_action_enum_difference_is_diagnostic_not_fatal(self):
        passed, diagnostics = evaluate_runtime_decision(
            {"qualifies": True, "next_action": {"purpose": "CHECK"}},
            {"fatal": {"qualifies": True}, "diagnostic": {"next_action.purpose": "IMPLEMENT"}},
        )
        self.assertTrue(passed)
        self.assertEqual(len(diagnostics), 1)

    def test_real_invariant_difference_is_fatal(self):
        passed, diagnostics = evaluate_runtime_decision(
            {"qualifies": False}, {"fatal": {"qualifies": True}, "diagnostic": {}},
        )
        self.assertFalse(passed)
        self.assertEqual(diagnostics, ["fatal:qualifies"])

    def test_terminal_inventory_is_typed(self):
        self.assertIn("ambiguous_or_partial", TERMINAL_CLASSES)
        self.assertIn("infrastructure_no_effect", TERMINAL_CLASSES)


if __name__ == "__main__":
    unittest.main()
