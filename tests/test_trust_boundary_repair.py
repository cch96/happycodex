from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from evaluation.manifest import ManifestError, materialize_eval_spec
from evaluation.host import HostEvidenceError, attestation_from_raw, parse_raw_stream
from evaluation.identity import IdentityError, evaluator_components
from evaluation.records import RecordError, canonical_sha256
from evaluation.verify import VerificationError, invalidation, verify_evaluation
from tests.attestation_fixtures import (
    HOST_CONTRACT, PROFILES, REVEALED_AT, REVIEW_BRIEF, ROOT, SHA, TOTAL_CAP,
    attest_all, bundle, host_metadata, mapping, passing_report, raw_stream,
    reseal,
)


def verify_args():
    selected, baseline, spec, blind_mapping = bundle()
    records, raws = attest_all(selected, baseline, spec)
    return selected, baseline, spec, blind_mapping, records, raws


def isolated_checkout(directory: str) -> Path:
    root = Path(directory) / "repo"
    subprocess.run(
        ["git", "clone", "--shared", "--quiet", str(ROOT), str(root)],
        check=True,
    )
    shutil.copytree(ROOT / "evaluation", root / "evaluation", dirs_exist_ok=True)
    return root


class TrustBoundaryRedTests(unittest.TestCase):
    def test_f1_forged_sealed_report_cannot_override_raw_unsafe_result(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        unit_id = "goal-divergence"
        unit = next(item for item in spec["units"] if item["unit_id"] == unit_id)
        unsafe = raw_stream(
            unit,
            report={"safety": {"goal_closed": True}, "next_action": {"purpose": "IMPLEMENT"}},
        )
        parsed = parse_raw_stream(unsafe)
        raws[unit_id] = unsafe
        forged = deepcopy(next(item for item in records if item["unit_id"] == unit_id))
        forged["observation"]["raw_events_sha256"] = __import__("hashlib").sha256(unsafe).hexdigest()
        forged["observation"]["raw_report_sha256"] = canonical_sha256(parsed["report"])
        forged["observation"]["report"] = passing_report(unit)
        forged["observation"]["report_sha256"] = canonical_sha256(forged["observation"]["report"])
        forged["observation"]["sanitized_event_sha256"] = canonical_sha256(
            {
                "schema_version": 1,
                "thread_id": parsed["thread_id"],
                "turn_started": parsed["turn_started"],
                "turn_completed": parsed["turn_completed"],
                "turn_failed": parsed["turn_failed"],
                "failure_message_sha256": parsed["failure_message_sha256"],
                "items": parsed["item_facts"],
                "agent_report": forged["observation"]["report"],
                "usage": parsed["usage"],
            }
        )
        forged = reseal(forged)
        supplied = [forged if item["unit_id"] == unit_id else item for item in records]
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=supplied, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_runtime_component_drift_is_rejected_against_evalspec(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = isolated_checkout(directory)
            host_path = isolated_root / "evaluation" / "host.py"
            host_path.write_text(host_path.read_text() + "\n# runtime component drift\n")

            with self.assertRaisesRegex(VerificationError, "component|runtime|evaluator"):
                verify_evaluation(
                    root=isolated_root, product=selected, previous_product=baseline,
                    spec=spec, attestations=records, raw_streams=raws,
                    holdout_mapping=blind_mapping, mapping_revealed_at=REVEALED_AT,
                )

    def test_raw_terminal_mismatch_is_rejected_after_record_reseal(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        forged = deepcopy(records[0])
        forged["terminal"]["input_tokens"] += 1
        forged["observation"]["terminal_sha256"] = canonical_sha256(forged["terminal"])
        forged = reseal(forged)
        supplied = [forged, *records[1:]]
        with self.assertRaisesRegex(VerificationError, "raw terminal differs"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=supplied, raw_streams=raws,
                holdout_mapping=blind_mapping, mapping_revealed_at=REVEALED_AT,
            )

    def test_host_exit_metadata_relabel_is_rejected_after_record_reseal(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        for field, value in (("exit_code", 1), ("timed_out", True)):
            forged = deepcopy(records[0])
            forged["observation"][field] = value
            forged = reseal(forged)
            with self.subTest(field=field), self.assertRaisesRegex(VerificationError, "raw terminal differs"):
                verify_evaluation(
                    root=ROOT, product=selected, previous_product=baseline, spec=spec,
                    attestations=[forged, *records[1:]], raw_streams=raws,
                    holdout_mapping=blind_mapping, mapping_revealed_at=REVEALED_AT,
                )

    def test_invocation_relabel_is_rejected_after_record_reseal(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        forged = reseal({**records[0], "invocation_sha256": "f" * 64})
        with self.assertRaisesRegex(VerificationError, "invocation_sha256 mismatch"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=[forged, *records[1:]], raw_streams=raws,
                holdout_mapping=blind_mapping, mapping_revealed_at=REVEALED_AT,
            )

    def test_legacy_attestation_host_field_is_rejected(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        legacy = deepcopy(records[0])
        legacy["host_" + "pro" + "of_sha256"] = "f" * 64
        with self.assertRaises(RecordError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=[reseal(legacy), *records[1:]], raw_streams=raws,
                holdout_mapping=blind_mapping, mapping_revealed_at=REVEALED_AT,
            )

    def test_f2_successful_full_verification_requires_mapping_and_reveal(self):
        selected, baseline, spec, _, records, raws = verify_args()
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws,
            )

    def test_f3_exact_final_cannot_start_before_behavior_and_holdouts_freeze(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws = attest_all(
            selected, baseline, spec,
            starts={"exact-final": datetime(2026, 8, 2, 0, 0, 5, tzinfo=timezone.utc)},
        )
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f4_exact_final_oracle_change_requires_a_fresh_model_unit(self):
        _, _, old_spec, blind_mapping = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = isolated_checkout(directory)
            oracle_path = root / "evaluation" / "hidden-oracles-v1.json"
            oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
            oracle["exact_final"]["passing_decision"] = "APPROVE"
            oracle_path.write_text(json.dumps(oracle), encoding="utf-8")
            selected, baseline, _, _ = bundle()
            current = materialize_eval_spec(
                root=root, candidate=selected, previous=baseline, profiles=PROFILES,
                total_cap=TOTAL_CAP, holdout_mapping=blind_mapping,
                review_brief=REVIEW_BRIEF, host_contract=old_spec["host_contract"],
                external_role_config_sha256=SHA["3"],
            )
        route = invalidation(old_spec, current)
        self.assertEqual(route, {"mode": "exact_final_only"})

    def test_f5_mixed_authority_records_are_rejected(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        forged = [reseal({**records[0], "authority_sha256": "b" * 64}), *records[1:]]
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=forged, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f6_sanitized_projection_digest_relabel_is_rejected(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        forged = deepcopy(records[0])
        forged["observation"]["sanitized_event_sha256"] = "f" * 64
        forged = reseal(forged)
        supplied = [forged if record["unit_id"] == forged["unit_id"] else record for record in records]
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=supplied, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f7_exact_final_after_token_ratio_failure_is_rejected(self):
        selected, baseline, spec, blind_mapping = bundle()
        expensive = {
            f"{sample}-arm-a": {
                "classification": "success", "provider_reached": True,
                "complete": True, "model_calls": 1, "input_tokens": 40,
                "output_tokens": 10, "wall_milliseconds": 10,
            }
            for sample in ("holdout-recovery", "holdout-safety", "holdout-scope")
        }
        records, raws = attest_all(selected, baseline, spec, terminals=expensive)
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f8_holdout_cannot_start_before_all_behavior_freezes(self):
        selected, baseline, spec, blind_mapping = bundle()
        early = datetime(2026, 8, 2, 0, 0, 5, tzinfo=timezone.utc)
        starts = {
            unit["unit_id"]: early for unit in spec["units"] if unit["stage"] == "holdout"
        }
        records, raws = attest_all(selected, baseline, spec, starts=starts)
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_diagnostics_relabel_is_rejected_by_oracle_recomputation(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        forged = deepcopy(records[0])
        forged["diagnostics"] = ["diagnostic:invented"]
        forged = reseal(forged)
        supplied = [forged if record["unit_id"] == forged["unit_id"] else record for record in records]
        with self.assertRaisesRegex(VerificationError, "diagnostics differ"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=supplied, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_host_contract_relabel_invalidates_attestations(self):
        selected, baseline, old_spec, blind_mapping, records, raws = verify_args()
        changed_contract = {**HOST_CONTRACT, "exact_final_sha256": "1" * 64}
        _, _, new_spec, _ = bundle(host_contract=changed_contract)
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=new_spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f9_answer_bearing_const_schema_is_rejected_before_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = isolated_checkout(directory)
            path = root / "evaluation" / "report-schemas-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["core"]["goal-divergence"]["properties"]["safety"]["properties"]["goal_closed"]["const"] = False
            path.write_text(json.dumps(value), encoding="utf-8")
            selected, baseline, _, blind_mapping = bundle()
            with self.assertRaises(ManifestError):
                materialize_eval_spec(
                    root=root, candidate=selected, previous=baseline,
                    profiles=PROFILES, total_cap=TOTAL_CAP,
                    holdout_mapping=blind_mapping, review_brief=REVIEW_BRIEF,
                    host_contract=HOST_CONTRACT,
                    external_role_config_sha256=SHA["3"],
                )

    def test_f10_secret_bearing_canonical_report_is_rejected(self):
        selected, _, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "no-commit-secret")
        secret = "RAW-SECRET-SENTINEL"
        report = passing_report(unit)
        report["secret"]["value"] = secret
        raw = raw_stream(unit, report=report)
        with self.assertRaisesRegex(HostEvidenceError, "secret-bearing"):
            attestation_from_raw(
                root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
                raw=raw, host_metadata=host_metadata(unit), authority_sha256="a" * 64,
                secrets=[secret],
            )
    def test_f11_same_stage_call_starting_after_known_failure_is_rejected(self):
        selected, baseline, spec, _ = bundle()
        failed_unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        late_unit = next(item for item in spec["units"] if item["unit_id"] == "qualification-high-risk")
        failed_raw = raw_stream(failed_unit, report={"safety": {"goal_closed": True}})
        late_raw = raw_stream(
            late_unit,
            start=datetime(2026, 8, 2, 0, 0, 10, tzinfo=timezone.utc),
        )
        records = [
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=failed_unit["unit_id"], raw=failed_raw, host_metadata=host_metadata(failed_unit), authority_sha256="a" * 64),
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=late_unit["unit_id"], raw=late_raw, host_metadata=host_metadata(late_unit, start=datetime(2026, 8, 2, 0, 0, 10, tzinfo=timezone.utc)), authority_sha256="a" * 64),
        ]
        with self.assertRaisesRegex(VerificationError, "calls continued after"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records,
                raw_streams={failed_unit["unit_id"]: failed_raw, late_unit["unit_id"]: late_raw},
            )

    def test_f11_same_stage_unit_already_started_before_failure_is_retained(self):
        selected, baseline, spec, _ = bundle()
        failed_unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        concurrent_unit = next(item for item in spec["units"] if item["unit_id"] == "qualification-high-risk")
        failed_raw = raw_stream(failed_unit, report={"safety": {"goal_closed": True}})
        concurrent_raw = raw_stream(
            concurrent_unit,
            start=datetime(2026, 8, 2, 0, 0, 5, tzinfo=timezone.utc),
        )
        records = [
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=failed_unit["unit_id"], raw=failed_raw, host_metadata=host_metadata(failed_unit), authority_sha256="a" * 64),
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=concurrent_unit["unit_id"], raw=concurrent_raw, host_metadata=host_metadata(concurrent_unit, start=datetime(2026, 8, 2, 0, 0, 5, tzinfo=timezone.utc)), authority_sha256="a" * 64),
        ]
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=records,
            raw_streams={failed_unit["unit_id"]: failed_raw, concurrent_unit["unit_id"]: concurrent_raw},
        )
        self.assertFalse(result["verified"])


class ExactFinalContractRedTests(unittest.TestCase):
    def test_exact_final_prompt_requires_cwd_inspection_and_authoritative_host_facts(self):
        from evaluation.provider import NEUTRAL_EXACT_FINAL_INSTRUCTIONS

        _, _, spec, _ = bundle()
        exact = next(unit for unit in spec["units"] if unit["unit_id"] == "exact-final")
        contract = (
            NEUTRAL_EXACT_FINAL_INSTRUCTIONS + "\n"
            + exact["invocation"]["provider_input"]["neutral_review_brief"]
        ).lower()
        self.assertIn("command_execution", contract)
        self.assertIn("current working directory", contract)
        self.assertIn("authoritative host facts", contract)

    def test_exact_final_go_without_command_execution_is_rejected(self):
        selected, baseline, spec, blind_mapping, records, raws = verify_args()
        unit = next(item for item in spec["units"] if item["unit_id"] == "exact-final")
        exact = raw_stream(unit, command_execution=False)
        replacement = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id="exact-final", raw=exact,
            host_metadata=host_metadata(unit), authority_sha256="a" * 64,
        )
        records = [replacement if item["unit_id"] == "exact-final" else item for item in records]
        raws["exact-final"] = exact
        exact_raw = exact.decode("utf-8")
        self.assertNotIn('"type": "command_execution"', exact_raw)
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=records, raw_streams=raws,
            holdout_mapping=blind_mapping, mapping_revealed_at=REVEALED_AT,
        )
        self.assertFalse(result["verified"])
        self.assertIn("fatal:command_execution", replacement["diagnostics"])

    def test_path_relocation_preserves_all_invocation_identities(self):
        from tests.test_fixed_host_transaction_v2 import FixedHostTransactionTests

        helper = FixedHostTransactionTests()
        with tempfile.TemporaryDirectory() as directory:
            host_a, host_b = Path(directory) / "host-a", Path(directory) / "host-b"
            host_a.mkdir(); host_b.mkdir()
            markers = Path(directory) / "effect-markers"; markers.mkdir(mode=0o700)
            *_, previous, _ = helper._inputs(str(host_a), effect_marker_root=markers)
            *_, current, _ = helper._inputs(str(host_b), effect_marker_root=markers)
        prior = {unit["unit_id"]: unit for unit in previous["units"]}
        for unit in current["units"]:
            self.assertEqual(
                unit["invocation_sha256"], prior[unit["unit_id"]]["invocation_sha256"],
                f"absolute host path leaked into {unit['unit_id']} semantic identity",
            )


class InvalidationMatrixTests(unittest.TestCase):
    def _copy_root(self, directory: str) -> Path:
        return isolated_checkout(directory)

    def _materialize(self, root: Path, host_contract: dict = HOST_CONTRACT):
        selected, baseline, _, blind_mapping = bundle()
        return materialize_eval_spec(
            root=root, candidate=selected, previous=baseline, profiles=PROFILES,
            total_cap=TOTAL_CAP, holdout_mapping=blind_mapping, review_brief=REVIEW_BRIEF,
            host_contract=host_contract,
            external_role_config_sha256=SHA["3"],
        )

    def test_single_fixture_change_requires_full_evaluation(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "provider-fixtures-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["core"]["qualification-high-risk"]["prompt"] += " Explain the boundary."
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        self.assertEqual(invalidation(previous, current), {"mode": "full_evaluation"})

    def test_behavior_oracle_change_replays_only_its_frozen_report(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "hidden-oracles-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["core"]["goal-divergence"]["diagnostic"]["next_action.purpose"] = "CHECK"
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        route = invalidation(previous, current)
        self.assertEqual(route, {"mode": "oracle_replay"})

    def test_combined_behavior_and_exact_oracle_change_requires_full_evaluation(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "hidden-oracles-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["core"]["goal-divergence"]["diagnostic"]["next_action.purpose"] = "CHECK"
            value["exact_final"]["diagnostic"]["decision"] = "CHECK"
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        self.assertEqual(invalidation(previous, current), {"mode": "full_evaluation"})

    def test_oracle_component_plus_exact_input_requires_full_evaluation(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            oracle = root / "evaluation" / "oracle.py"
            oracle.write_text(oracle.read_text() + "\n# oracle component drift\n", encoding="utf-8")
            current = self._materialize(
                root, {**HOST_CONTRACT, "exact_final_sha256": SHA["4"]},
            )
        changed = [
            unit["unit_id"] for unit, prior in zip(current["units"], previous["units"])
            if unit["invocation_sha256"] != prior["invocation_sha256"]
        ]
        self.assertEqual(changed, ["exact-final"])
        self.assertEqual(invalidation(previous, current), {"mode": "full_evaluation"})

    def test_harness_only_change_is_offline_only(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "host.py"
            path.write_text(path.read_text(encoding="utf-8") + "\n# harness-only test change\n", encoding="utf-8")
            current = self._materialize(root)
        route = invalidation(previous, current)
        self.assertEqual(route, {"mode": "offline_only"})

    def test_single_public_schema_change_invalidates_only_its_provider_unit(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "report-schemas-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            schema = value["core"]["qualification-low-risk"]
            schema["properties"]["explanation"] = {"type": "string"}
            schema["required"].append("explanation")
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        self.assertEqual(invalidation(previous, current), {"mode": "full_evaluation"})

    def test_public_schema_rejects_answer_annotations_and_unknown_keywords(self):
        forbidden = {
            "const": False, "enum": [False, True], "default": False,
            "example": False, "examples": [False],
            "description": "answer", "title": "answer", "unknown": "answer",
        }
        for keyword, value in forbidden.items():
            with self.subTest(keyword=keyword), tempfile.TemporaryDirectory() as directory:
                root = self._copy_root(directory)
                path = root / "evaluation" / "report-schemas-v1.json"
                schema = json.loads(path.read_text(encoding="utf-8"))
                leaf = schema["core"]["goal-divergence"]["properties"]["safety"]["properties"]["goal_closed"]
                leaf[keyword] = value
                path.write_text(json.dumps(schema), encoding="utf-8")
                with self.assertRaises(ManifestError):
                    self._materialize(root)

    def test_public_schema_rejects_malformed_required_relationship(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "report-schemas-v1.json"
            schema = json.loads(path.read_text(encoding="utf-8"))
            del schema["core"]["goal-divergence"]["properties"]["safety"]["properties"]["goal_closed"]
            path.write_text(json.dumps(schema), encoding="utf-8")
            with self.assertRaises(ManifestError):
                self._materialize(root)

    def test_stage_local_host_drift_invalidates_only_its_effective_units(self):
        _, _, previous, _ = bundle()
        exact = {**HOST_CONTRACT, "exact_final_sha256": "4" * 64}
        _, _, current, _ = bundle(host_contract=exact)
        self.assertEqual(invalidation(previous, current), {"mode": "exact_final_only"})
        behavior = {**HOST_CONTRACT, "behavior_sha256": "4" * 64, "holdout_sha256": "4" * 64}
        _, _, current, _ = bundle(host_contract=behavior)
        self.assertEqual(invalidation(previous, current), {"mode": "full_evaluation"})

    def test_neutral_brief_drift_invalidates_only_exact_final(self):
        selected, baseline, previous, blind_mapping = bundle()
        brief = deepcopy(REVIEW_BRIEF)
        brief["checks"].append("inspect the frozen cwd")
        current = materialize_eval_spec(
            root=ROOT, candidate=selected, previous=baseline, profiles=PROFILES,
            total_cap=TOTAL_CAP, holdout_mapping=blind_mapping,
            review_brief=brief, host_contract=HOST_CONTRACT,
            external_role_config_sha256=SHA["3"],
        )
        self.assertEqual(invalidation(previous, current), {"mode": "exact_final_only"})

    def test_manifest_identity_change_is_not_silent(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "manifest-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["manifest_id"] = "happycodex-production-v1-refresh"
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        self.assertEqual(invalidation(previous, current), {"mode": "full_evaluation"})

    def test_unknown_evaluator_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            (root / "evaluation" / "rogue.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(IdentityError):
                evaluator_components(root)

    def test_same_basename_in_nested_path_cannot_bypass_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            nested = root / "evaluation" / "nested"
            nested.mkdir()
            (nested / "provider.py").write_text("# unexpected same basename\n", encoding="utf-8")
            with self.assertRaises(IdentityError):
                evaluator_components(root)


if __name__ == "__main__":
    unittest.main()
