from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from evaluation.manifest import materialize_eval_spec
from evaluation.identity import IdentityError, evaluator_components
from evaluation.records import canonical_sha256
from evaluation.verify import VerificationError, invalidation, verify_evaluation
from tests.attestation_fixtures import (
    PROFILE, REVEALED_AT, REVIEW_BRIEF, ROOT, TOTAL_CAP,
    attest_all, bundle, mapping, passing_report, proof_verifier, raw_stream, reseal,
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
        proofs[unit_id] = {
            **proofs[unit_id],
            "raw_sha256": __import__("hashlib").sha256(unsafe).hexdigest(),
        }
        forged = deepcopy(next(item for item in records if item["unit_id"] == unit_id))
        forged["observation"]["raw_events_sha256"] = proofs[unit_id]["raw_sha256"]
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
            oracle["exact_final"]["fatal"]["artifact_reviewed"] = True
            oracle_path.write_text(json.dumps(oracle), encoding="utf-8")
            selected, baseline, _, _ = bundle()
            current = materialize_eval_spec(
                root=root, candidate=selected, previous=baseline, profile=PROFILE,
                total_cap=TOTAL_CAP, holdout_mapping=blind_mapping,
                review_brief=REVIEW_BRIEF,
            )
        route = invalidation(old_spec, current)
        self.assertIn("exact-final", route["model_units"])
        self.assertNotIn("exact-final", route["replay_units"])


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
            value["core"]["goal-divergence"]["diagnostic"]["next_action.effect_class"] = "repo_write"
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

    def test_unknown_evaluator_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_root(directory)
            (root / "evaluation" / "rogue.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(IdentityError):
                evaluator_components(root)


if __name__ == "__main__":
    unittest.main()
