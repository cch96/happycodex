from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from evaluation.manifest import ManifestError, materialize_eval_spec
from evaluation.host import attestation_from_raw
from evaluation.identity import IdentityError, evaluator_components
from evaluation.records import canonical_sha256
from evaluation.verify import VerificationError, invalidation, verify_evaluation
from tests.attestation_fixtures import (
    HOST_CONTRACT, PROFILE, REVEALED_AT, REVIEW_BRIEF, ROOT, TOTAL_CAP,
    attest_all, bundle, host_proof, mapping, passing_report, proof_verifier, raw_stream, reseal,
)


def verify_args():
    selected, baseline, spec, blind_mapping = bundle()
    records, raws, proofs = attest_all(selected, baseline, spec)
    return selected, baseline, spec, blind_mapping, records, raws, proofs


class TrustBoundaryRedTests(unittest.TestCase):
    def test_f1_forged_sealed_report_cannot_override_raw_unsafe_result(self):
        selected, baseline, spec, blind_mapping, records, raws, proofs = verify_args()
        unit_id = "goal-divergence"
        unsafe = raw_stream(
            next(unit for unit in spec["units"] if unit["unit_id"] == unit_id),
            report={"safety": {"goal_closed": True}, "next_action": {"purpose": "IMPLEMENT"}},
        )
        raws[unit_id] = unsafe
        unit = next(unit for unit in spec["units"] if unit["unit_id"] == unit_id)
        proofs[unit_id] = host_proof(unit, unsafe, spec)
        forged = deepcopy(next(item for item in records if item["unit_id"] == unit_id))
        forged["observation"]["raw_events_sha256"] = __import__("hashlib").sha256(unsafe).hexdigest()
        forged["observation"]["report"] = passing_report(
            next(unit for unit in spec["units"] if unit["unit_id"] == unit_id)
        )
        forged["observation"]["report_sha256"] = canonical_sha256(forged["observation"]["report"])
        forged["host_proof_sha256"] = canonical_sha256(proofs[unit_id])
        forged = reseal(forged)
        supplied = [forged if item["unit_id"] == unit_id else item for item in records]
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=supplied, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f2_successful_full_verification_requires_mapping_and_reveal(self):
        selected, baseline, spec, _, records, raws, proofs = verify_args()
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier,
            )

    def test_f3_exact_final_cannot_start_before_behavior_and_holdouts_freeze(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws, proofs = attest_all(
            selected, baseline, spec,
            starts={"exact-final": datetime(2026, 8, 2, 0, 0, 5, tzinfo=timezone.utc)},
        )
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f4_exact_final_oracle_change_requires_a_fresh_model_unit(self):
        _, _, old_spec, blind_mapping = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "evaluation", root / "evaluation")
            shutil.copytree(ROOT / "skills", root / "skills")
            oracle_path = root / "evaluation" / "hidden-oracles-v1.json"
            oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
            oracle["exact_final"]["passing_decision"] = "APPROVE"
            oracle_path.write_text(json.dumps(oracle), encoding="utf-8")
            selected, baseline, _, _ = bundle()
            current = materialize_eval_spec(
                root=root, candidate=selected, previous=baseline, profile=PROFILE,
                total_cap=TOTAL_CAP, holdout_mapping=blind_mapping,
                review_brief=REVIEW_BRIEF, host_contract=old_spec["host_contract"],
            )
        route = invalidation(old_spec, current)
        self.assertIn("exact-final", route["model_units"])
        self.assertNotIn("exact-final", route["replay_units"])

    def test_f5_authority_relabel_cannot_reuse_external_proofs(self):
        selected, baseline, spec, blind_mapping, records, raws, proofs = verify_args()
        forged = [reseal({**record, "authority_sha256": "b" * 64}) for record in records]
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=forged, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f6_sanitized_digest_relabel_cannot_reuse_external_proof(self):
        selected, baseline, spec, blind_mapping, records, raws, proofs = verify_args()
        forged = deepcopy(records[0])
        forged["observation"]["sanitized_event_sha256"] = "f" * 64
        forged = reseal(forged)
        supplied = [forged if record["unit_id"] == forged["unit_id"] else record for record in records]
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=supplied, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f7_exact_final_after_aggregate_holdout_failure_is_rejected(self):
        selected, baseline, spec, blind_mapping = bundle()
        expensive = {
            f"{sample}-arm-a": {
                "classification": "success", "provider_reached": True,
                "complete": True, "model_calls": 1, "input_tokens": 40,
                "output_tokens": 10, "wall_milliseconds": 40,
            }
            for sample in ("holdout-recovery", "holdout-safety", "holdout-scope")
        }
        records, raws, proofs = attest_all(selected, baseline, spec, terminals=expensive)
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f8_holdout_cannot_start_before_all_behavior_freezes(self):
        selected, baseline, spec, blind_mapping = bundle()
        early = datetime(2026, 8, 2, 0, 0, 5, tzinfo=timezone.utc)
        starts = {
            unit["unit_id"]: early for unit in spec["units"] if unit["stage"] == "holdout"
        }
        records, raws, proofs = attest_all(selected, baseline, spec, starts=starts)
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_diagnostics_relabel_is_rejected_by_oracle_recomputation(self):
        selected, baseline, spec, blind_mapping, records, raws, proofs = verify_args()
        forged = deepcopy(records[0])
        forged["diagnostics"] = ["diagnostic:invented"]
        forged = reseal(forged)
        supplied = [forged if record["unit_id"] == forged["unit_id"] else record for record in records]
        with self.assertRaisesRegex(VerificationError, "diagnostics differ"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=supplied, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_host_contract_relabel_invalidates_attestations_and_proofs(self):
        selected, baseline, old_spec, blind_mapping, records, raws, proofs = verify_args()
        changed_contract = {**HOST_CONTRACT, "workspace_policy_sha256": "1" * 64}
        _, _, new_spec, _ = bundle(host_contract=changed_contract)
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=new_spec,
                attestations=records, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_f9_answer_bearing_const_schema_is_rejected_before_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "evaluation", root / "evaluation")
            shutil.copytree(ROOT / "skills", root / "skills")
            path = root / "evaluation" / "report-schemas-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["core"]["goal-divergence"]["properties"]["safety"]["properties"]["goal_closed"]["const"] = False
            path.write_text(json.dumps(value), encoding="utf-8")
            selected, baseline, _, blind_mapping = bundle()
            with self.assertRaises(ManifestError):
                materialize_eval_spec(
                    root=root, candidate=selected, previous=baseline,
                    profile=PROFILE, total_cap=TOTAL_CAP,
                    holdout_mapping=blind_mapping, review_brief=REVIEW_BRIEF,
                    host_contract=HOST_CONTRACT,
                )

    def test_f10_secret_raw_can_verify_as_proof_bound_sanitized_attestation(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws, proofs = attest_all(selected, baseline, spec)
        unit = next(item for item in spec["units"] if item["unit_id"] == "no-commit-secret")
        secret = "RAW-SECRET-SENTINEL"
        report = passing_report(unit)
        report["secret"]["value"] = secret
        raw = raw_stream(unit, report=report)
        proof = host_proof(unit, raw, spec, secrets=[secret])
        sanitized = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
            raw=raw, authority_sha256="a" * 64, host_proof=proof,
            secrets=[secret],
        )
        self.assertNotIn(secret, canonical_sha256(sanitized) + str(sanitized))
        supplied = [sanitized if record["unit_id"] == unit["unit_id"] else record for record in records]
        raws[unit["unit_id"]] = raw
        proofs[unit["unit_id"]] = proof
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=supplied, raw_streams=raws, host_proofs=proofs,
            proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
            mapping_revealed_at=REVEALED_AT,
        )
        self.assertTrue(result["verified"])
        changed_report = deepcopy(sanitized)
        changed_report["observation"]["report"]["secret"]["value"] = "<different-redaction>"
        changed_report["observation"]["report_sha256"] = canonical_sha256(changed_report["observation"]["report"])
        changed_report = reseal(changed_report)
        changed_records = [changed_report if record["unit_id"] == unit["unit_id"] else record for record in records]
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=changed_records, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )
        wrong_proof = host_proof(unit, raw, spec)
        mismatched = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
            raw=raw, authority_sha256="a" * 64, host_proof=wrong_proof,
            secrets=[secret],
        )
        wrong_records = [mismatched if record["unit_id"] == unit["unit_id"] else record for record in records]
        proofs[unit["unit_id"]] = wrong_proof
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=wrong_records, raw_streams=raws, host_proofs=proofs,
                proof_verifier=proof_verifier, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
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
        failed_proof = host_proof(failed_unit, failed_raw, spec)
        late_proof = host_proof(late_unit, late_raw, spec)
        records = [
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=failed_unit["unit_id"], raw=failed_raw, authority_sha256="a" * 64, host_proof=failed_proof),
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=late_unit["unit_id"], raw=late_raw, authority_sha256="a" * 64, host_proof=late_proof),
        ]
        with self.assertRaisesRegex(VerificationError, "calls continued after"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records,
                raw_streams={failed_unit["unit_id"]: failed_raw, late_unit["unit_id"]: late_raw},
                host_proofs={failed_unit["unit_id"]: failed_proof, late_unit["unit_id"]: late_proof},
                proof_verifier=proof_verifier,
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
        failed_proof = host_proof(failed_unit, failed_raw, spec)
        concurrent_proof = host_proof(concurrent_unit, concurrent_raw, spec)
        records = [
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=failed_unit["unit_id"], raw=failed_raw, authority_sha256="a" * 64, host_proof=failed_proof),
            attestation_from_raw(root=ROOT, product=selected, spec=spec, unit_id=concurrent_unit["unit_id"], raw=concurrent_raw, authority_sha256="a" * 64, host_proof=concurrent_proof),
        ]
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=records,
            raw_streams={failed_unit["unit_id"]: failed_raw, concurrent_unit["unit_id"]: concurrent_raw},
            host_proofs={failed_unit["unit_id"]: failed_proof, concurrent_unit["unit_id"]: concurrent_proof},
            proof_verifier=proof_verifier,
        )
        self.assertFalse(result["verified"])


class InvalidationMatrixTests(unittest.TestCase):
    def _copy_root(self, directory: str) -> Path:
        root = Path(directory)
        shutil.copytree(ROOT / "evaluation", root / "evaluation")
        shutil.copytree(ROOT / "skills", root / "skills")
        return root

    def _materialize(self, root: Path):
        selected, baseline, _, blind_mapping = bundle()
        return materialize_eval_spec(
            root=root, candidate=selected, previous=baseline, profile=PROFILE,
            total_cap=TOTAL_CAP, holdout_mapping=blind_mapping, review_brief=REVIEW_BRIEF,
            host_contract=HOST_CONTRACT,
        )

    def test_single_fixture_change_invalidates_only_its_provider_unit(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "provider-fixtures-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["core"]["qualification-high-risk"]["prompt"] += " Explain the boundary."
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        self.assertEqual(invalidation(previous, current)["model_units"], ["qualification-high-risk"])

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
        self.assertEqual(route["model_units"], [])
        self.assertEqual(route["replay_units"], ["goal-divergence"])

    def test_harness_only_change_is_offline_only(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "host.py"
            path.write_text(path.read_text(encoding="utf-8") + "\n# harness-only test change\n", encoding="utf-8")
            current = self._materialize(root)
        route = invalidation(previous, current)
        self.assertEqual(route["model_units"], [])
        self.assertEqual(route["replay_units"], [])
        self.assertEqual(route["offline_units"], ["__bundle__"])

    def test_single_public_schema_change_invalidates_only_its_provider_unit(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "report-schemas-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["core"]["qualification-low-risk"]["properties"]["explanation"] = {"type": "string"}
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        self.assertEqual(invalidation(previous, current)["model_units"], ["qualification-low-risk"])

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

    def test_host_tool_permission_workspace_or_provider_drift_invalidates_full_plan(self):
        _, _, previous, _ = bundle()
        for field in ("provider_binary_sha256", "tool_config_sha256", "permission_profile_sha256", "workspace_policy_sha256"):
            changed = {**HOST_CONTRACT, field: "1" * 64}
            _, _, current, _ = bundle(host_contract=changed)
            with self.subTest(field=field):
                self.assertEqual(len(invalidation(previous, current)["model_units"]), len(current["units"]))

    def test_manifest_identity_change_is_not_silent(self):
        _, _, previous, _ = bundle()
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            path = root / "evaluation" / "manifest-v1.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["manifest_id"] = "happycodex-production-v1-refresh"
            path.write_text(json.dumps(value), encoding="utf-8")
            current = self._materialize(root)
        self.assertIn("__manifest__", invalidation(previous, current)["offline_units"])

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
