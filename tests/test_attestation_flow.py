from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import unittest

from evaluation.host import attestation_from_raw
from evaluation.provider import accept_release_authority, release_authority_request
from evaluation.records import RecordError, build_eval_spec, canonical_sha256, validate_record
from evaluation.verify import (
    VerificationError, append_attestation, create_release_receipt,
    replay_attestation, verify_evaluation, verify_release,
)
from tests.attestation_fixtures import (
    REVEALED_AT, ROOT, SHA, TOTAL_CAP, attest_all, bundle, host_metadata,
    passing_report, raw_stream, terminal,
)


def positive_evaluation():
    selected, baseline, spec, blind_mapping = bundle()
    records, raws = attest_all(selected, baseline, spec)
    evaluation = verify_evaluation(
        root=ROOT, product=selected, previous_product=baseline, spec=spec,
        attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
        mapping_revealed_at=REVEALED_AT,
    )
    return selected, baseline, spec, blind_mapping, records, raws, evaluation


class ExternalEvidenceFlowTests(unittest.TestCase):
    def test_fixed_host_raw_full_chain_positive(self):
        _, _, spec, _, records, _, result = positive_evaluation()
        self.assertTrue(result["verified"])
        self.assertTrue(result["holdout"]["passed"])
        self.assertEqual(len(records), len(spec["units"]))
        self.assertEqual(result["usage"]["model_calls"], len(spec["units"]))

    def test_forged_terminal_digest_is_rejected(self):
        _, _, _, _, records, _, _ = positive_evaluation()
        forged = deepcopy(records[0])
        forged["terminal"]["input_tokens"] += 1
        with self.assertRaises(RecordError):
            validate_record(forged)

    def test_missing_fixed_host_raw_is_rejected(self):
        selected, baseline, spec, blind_mapping, records, raws, _ = positive_evaluation()
        raws.pop(records[0]["unit_id"])
        with self.assertRaises(VerificationError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_terminal_failure_prefix_stops_without_later_calls(self):
        selected, baseline, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        raw = raw_stream(unit, report={"safety": {"goal_closed": True}})
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
            raw=raw, host_metadata=host_metadata(unit), authority_sha256=SHA["a"],
        )
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=[record], raw_streams={unit["unit_id"]: raw},
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["failures"][0]["unit_id"], "goal-divergence")

    def test_ambiguous_partial_terminal_is_terminal_failure(self):
        selected, baseline, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        partial = terminal(classification="ambiguous_or_partial", complete=False)
        raw = raw_stream(unit, terminal_value=partial)
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"],
            raw=raw, host_metadata=host_metadata(unit, terminal_value=partial),
            authority_sha256=SHA["a"],
        )
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=[record], raw_streams={unit["unit_id"]: raw},
        )
        self.assertEqual(result["failures"][0]["classification"], "ambiguous_or_partial")


class FixedHoldoutTests(unittest.TestCase):
    def test_model_self_scores_are_ignored_in_favor_of_hidden_oracle(self):
        *_, result = positive_evaluation()
        self.assertTrue(result["holdout"]["passed"])
        self.assertTrue(all(pair["candidate_score"] == 2 for pair in result["holdout"]["pairs"]))

    def test_pair_arms_must_overlap(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws = attest_all(
            selected, baseline, spec,
            starts={"holdout-recovery-arm-b": datetime(2026, 8, 2, 0, 0, 31, tzinfo=timezone.utc)},
        )
        with self.assertRaises(ValueError):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at="2026-08-02T00:00:45Z",
            )

    def test_relative_wall_ratio_is_diagnostic_only(self):
        selected, baseline, spec, blind_mapping = bundle()
        candidate_units = {
            unit_id
            for pair in blind_mapping.values()
            for unit_id, label in pair.items()
            if label == "candidate"
        }
        exact_start = datetime(2026, 8, 2, 0, 0, 50, tzinfo=timezone.utc)
        records, raws = [], {}
        for unit in spec["units"]:
            arm = selected if unit["product_semantic_sha256"] == selected["package_semantic_sha256"] else baseline
            start = exact_start if unit["stage"] == "exact_final" else None
            duration = 20 if unit["unit_id"] in candidate_units else 10
            raw = raw_stream(unit, start=start, duration_seconds=duration)
            records.append(attestation_from_raw(
                root=ROOT, product=arm, spec=spec, unit_id=unit["unit_id"],
                raw=raw, host_metadata=host_metadata(
                    unit, start=start, duration_seconds=duration,
                ), authority_sha256=SHA["a"],
            ))
            raws[unit["unit_id"]] = raw
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
            mapping_revealed_at="2026-08-02T00:00:45Z",
        )
        self.assertTrue(result["verified"])
        self.assertTrue(result["holdout"]["passed"])
        self.assertTrue(result["holdout"]["aggregate"]["token_ratio_within_1_25"])
        self.assertFalse(result["holdout"]["aggregate"]["wall_ratio_within_1_25"])

    def test_aggregate_token_ratio_is_strict_and_blocks_exact_final(self):
        selected, baseline, spec, blind_mapping = bundle()
        expensive = {
            f"{sample}-arm-a": terminal(input_tokens=20, output_tokens=2)
            for sample in ("holdout-recovery", "holdout-safety", "holdout-scope")
        }
        records, raws = attest_all(selected, baseline, spec, terminals=expensive)
        with self.assertRaisesRegex(VerificationError, "calls continued after fixed-holdout failure"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_absolute_cumulative_wall_cap_is_independently_hard(self):
        cap = {**TOTAL_CAP, "wall_milliseconds": 119_999}
        selected, baseline, spec, blind_mapping = bundle(total_cap=cap)
        records, raws = attest_all(selected, baseline, spec)
        self.assertTrue(all(record["terminal"]["classification"] == "success" for record in records))
        self.assertLess(sum(record["terminal"]["input_tokens"] for record in records), cap["input_tokens"])
        self.assertLess(sum(record["terminal"]["output_tokens"] for record in records), cap["output_tokens"])
        self.assertEqual(sum(record["terminal"]["wall_milliseconds"] for record in records), 120_000)
        with self.assertRaisesRegex(VerificationError, "evaluation exceeds total cap: wall_milliseconds"):
            verify_evaluation(
                root=ROOT, product=selected, previous_product=baseline, spec=spec,
                attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_aggregate_failure_prefix_is_retained_without_exact_final(self):
        selected, baseline, spec, blind_mapping = bundle()
        expensive = {
            f"{sample}-arm-a": terminal(input_tokens=20, output_tokens=2)
            for sample in ("holdout-recovery", "holdout-safety", "holdout-scope")
        }
        records, raws = attest_all(selected, baseline, spec, terminals=expensive)
        records = [record for record in records if record["unit_id"] != "exact-final"]
        raws.pop("exact-final")
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
            mapping_revealed_at=REVEALED_AT,
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["failures"][0]["unit_id"], "fixed-holdouts")

    def test_baseline_fatal_is_comparison_evidence_not_an_absolute_gate(self):
        selected, baseline, spec, blind_mapping = bundle()
        baseline_units = {
            unit_id
            for pair in blind_mapping.values()
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
        records, raws = attest_all(selected, baseline, spec, reports=reports)
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
            mapping_revealed_at=REVEALED_AT,
        )
        self.assertTrue(result["verified"])
        self.assertTrue(result["holdout"]["passed"])
        self.assertTrue(all(not pair["baseline_absolute_passed"] for pair in result["holdout"]["pairs"]))

    def test_candidate_fatal_returns_a_failed_unified_judgment(self):
        selected, baseline, spec, blind_mapping = bundle()
        candidate_units = {
            unit_id
            for pair in blind_mapping.values()
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
        records, raws = attest_all(selected, baseline, spec, reports=reports)
        records = [record for record in records if record["unit_id"] != "exact-final"]
        raws.pop("exact-final")
        result = verify_evaluation(
            root=ROOT, product=selected, previous_product=baseline, spec=spec,
            attestations=records, raw_streams=raws, holdout_mapping=blind_mapping,
            mapping_revealed_at=REVEALED_AT,
        )
        self.assertFalse(result["verified"])
        self.assertFalse(result["holdout"]["passed"])
        self.assertTrue(all(not pair["candidate_absolute_passed"] for pair in result["holdout"]["pairs"]))
        self.assertEqual(result["failures"], [
            {"unit_id": "fixed-holdouts", "classification": "quality_failure", "verdict": "fail"}
        ])


class ExactFinalAndReleaseTests(unittest.TestCase):
    def test_adverse_exact_final_is_durable_and_one_shot(self):
        selected, baseline, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "exact-final")
        report = passing_report(unit)
        report["decision"] = "NOT_YET"
        raw = raw_stream(unit, report=report)
        adverse = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id="exact-final", raw=raw,
            host_metadata=host_metadata(unit), authority_sha256=SHA["a"],
        )
        self.assertEqual(adverse["verdict"], "fail")
        _, _, _, _, friendly_records, _, _ = positive_evaluation()
        friendly = next(item for item in friendly_records if item["unit_id"] == "exact-final")
        with self.assertRaises(VerificationError):
            append_attestation([adverse], friendly)

    def test_behavior_replay_reuses_frozen_external_observation(self):
        _, _, old_spec, _, records, raws, _ = positive_evaluation()
        parent = next(item for item in records if item["unit_id"] == "goal-divergence")
        units = deepcopy(old_spec["units"])
        next(unit for unit in units if unit["unit_id"] == "goal-divergence")["oracle_sha256"] = SHA["b"]
        new_spec = build_eval_spec(
            product_semantic_sha256=old_spec["product_semantic_sha256"],
            external_role_config_sha256=old_spec["external_role_config_sha256"],
            evaluator_bundle_sha256=old_spec["evaluator_bundle_sha256"],
            provider_component_sha256=old_spec["provider_component_sha256"],
            oracle_component_sha256=SHA["c"],
            harness_component_sha256=old_spec["harness_component_sha256"],
            manifest_sha256=old_spec["manifest_sha256"], fixtures_sha256=old_spec["fixtures_sha256"],
            oracles_sha256=SHA["d"], neutral_review_brief_sha256=old_spec["neutral_review_brief_sha256"],
            response_schemas_sha256=old_spec["response_schemas_sha256"],
            host_contract=old_spec["host_contract"], host_contract_sha256=old_spec["host_contract_sha256"],
            profiles=old_spec["profiles"], units=units, holdouts=old_spec["holdouts"],
            total_cap=old_spec["total_cap"], previous_product_record_sha256=old_spec["previous_product_record_sha256"],
        )
        replay = replay_attestation(
            parent=parent, spec=new_spec, oracle=lambda _report: (True, []),
        )
        self.assertEqual(replay["observation"]["raw_events_sha256"], parent["observation"]["raw_events_sha256"])
        self.assertEqual(replay["terminal"], parent["terminal"])
        self.assertEqual(replay["observation"]["parent_attestation_sha256"], parent["record_sha256"])

    def _release_fixture(self):
        selected, _, _, _, _, _, evaluation = positive_evaluation()
        destination = {"kind": "plugin-cache", "identity_sha256": SHA["b"]}
        rollback = {"artifact_sha256": SHA["c"], "config_sha256": SHA["d"], "ready": True}
        request = release_authority_request(
            product_record_sha256=selected["record_sha256"],
            attestation_sha256s=evaluation["attestation_sha256s"],
            destination_sha256=canonical_sha256(destination), rollback_sha256=canonical_sha256(rollback),
        )
        capability = accept_release_authority(
            request, {"scope": "release", "request_sha256": request, "nonce": "n", "signature": "s"},
            lambda _value: True,
        )
        install = {"artifact_sha256": selected["package_artifact_sha256"], "install_sha256": SHA["e"], "invocation_sha256": SHA["f"], "status": "success"}
        receipt = create_release_receipt(
            product=selected, evaluation=evaluation, isolated_install=install,
            destination=destination, rollback=rollback, capability=capability,
        )
        return selected, evaluation, destination, rollback, receipt

    def test_release_receipt_binds_install_destination_and_rollback(self):
        selected, evaluation, destination, rollback, receipt = self._release_fixture()
        self.assertTrue(verify_release(product=selected, evaluation=evaluation, receipt=receipt, destination=destination, rollback=rollback)["verified"])
        with self.assertRaises(VerificationError):
            verify_release(product=selected, evaluation=evaluation, receipt=receipt, destination={**destination, "identity_sha256": SHA["1"]}, rollback=rollback)


if __name__ == "__main__":
    unittest.main()
