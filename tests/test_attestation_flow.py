from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from evaluation.holdout import HoldoutError, judge_fixed_holdouts
from evaluation.provider import (
    InvocationJournal,
    ProviderError,
    accept_release_authority,
    release_authority_request,
    run_fake_provider,
)
from evaluation.records import RecordError, canonical_sha256, validate_record
from evaluation.verify import (
    VerificationError,
    append_attestation,
    create_release_receipt,
    replay_attestation,
    verify_evaluation,
    verify_release,
)
from tests.attestation_fixtures import (
    SHA,
    attest_all,
    bundle,
    capability,
    result_for,
    terminal,
    previous_product,
    write_json,
)


REVEALED_AT = "2026-08-02T00:00:20Z"


def positive_evaluation():
    selected, spec, projections, mapping = bundle()
    attestations = attest_all(selected, spec, projections)
    evaluation = verify_evaluation(
        product=selected, spec=spec, attestations=attestations,
        previous_product=previous_product(),
        holdout_mapping=mapping, mapping_revealed_at=REVEALED_AT,
    )
    return selected, spec, projections, mapping, attestations, evaluation


class FakeProviderFlowTests(unittest.TestCase):
    def test_fake_provider_full_chain_positive(self):
        _, spec, _, _, attestations, evaluation = positive_evaluation()
        self.assertTrue(evaluation["verified"])
        self.assertTrue(evaluation["holdout"]["passed"])
        self.assertEqual(len(attestations), len(spec["units"]))
        self.assertEqual(evaluation["usage"]["model_calls"], len(spec["units"]))

    def test_forged_terminal_digest_is_rejected(self):
        _, _, _, _, attestations, _ = positive_evaluation()
        forged = deepcopy(attestations[0])
        forged["terminal"]["input_tokens"] += 1
        with self.assertRaises(RecordError):
            validate_record(forged)

    def test_provider_projection_mismatch_refuses_before_call(self):
        selected, spec, projections, _ = bundle()
        calls = []
        changed = deepcopy(projections[spec["units"][0]["unit_id"]])
        changed["prompt"] += " drift"
        with self.assertRaises(ProviderError):
            run_fake_provider(
                product=selected, spec=spec, unit_id=spec["units"][0]["unit_id"],
                projection=changed, capability=capability(spec),
                journal=InvocationJournal(),
                provider=lambda value: calls.append(value) or result_for("unused"),
                oracle=lambda _report: (True, []),
            )
        self.assertEqual(calls, [])

    def test_over_cap_is_terminal_and_not_retried(self):
        selected, spec, projections, _ = bundle(
            total_cap={
                "model_calls": 0, "input_tokens": 100, "output_tokens": 100,
                "wall_milliseconds": 100, "infrastructure_recoveries": 0,
            }
        )
        journal = InvocationJournal()
        unit_id = spec["units"][0]["unit_id"]
        with self.assertRaises(ProviderError):
            run_fake_provider(
                product=selected, spec=spec, unit_id=unit_id,
                projection=projections[unit_id], capability=capability(spec),
                journal=journal, provider=lambda _value: result_for(unit_id),
                oracle=lambda _report: (True, []),
            )
        self.assertEqual(journal.usage["model_calls"], 1)
        with self.assertRaises(ProviderError):
            journal.reserve(spec["units"][0]["invocation_sha256"])

    def test_ambiguous_or_partial_terminal_fails_evaluation(self):
        selected, spec, projections, mapping = bundle()
        unit_id = "goal-divergence"
        partial = result_for(
            unit_id,
            terminal_value=terminal(
                classification="ambiguous_or_partial", provider_reached=True,
                complete=False, model_calls=1,
            ),
        )
        attestations = attest_all(selected, spec, projections, results={unit_id: partial})
        result = verify_evaluation(
            product=selected, spec=spec, attestations=attestations,
            previous_product=previous_product(),
            holdout_mapping=mapping, mapping_revealed_at=REVEALED_AT,
        )
        self.assertFalse(result["verified"])
        self.assertIn("ambiguous_or_partial", {item["classification"] for item in result["failures"]})

    def test_secret_visible_in_env_refuses_attestation(self):
        selected, spec, projections, _ = bundle()
        unit_id = spec["units"][0]["unit_id"]
        with self.assertRaises(ProviderError):
            run_fake_provider(
                product=selected, spec=spec, unit_id=unit_id,
                projection=projections[unit_id], capability=capability(spec),
                journal=InvocationJournal(), provider=lambda _value: result_for(unit_id),
                oracle=lambda _report: (True, []), secrets=["SECRET-SENTINEL"],
                visible_surface={
                    "workspace": {}, "argv": ["fake"], "stdin": "",
                    "env": {"LEAK": "SECRET-SENTINEL"},
                },
            )

    def test_oracle_only_replay_uses_frozen_observation_and_zero_calls(self):
        selected, old_spec, projections, mapping = bundle()
        old = attest_all(selected, old_spec, projections)
        _, new_spec, _, _ = bundle(
            oracle_component=SHA["9"],
            unit_overrides={"goal-divergence": {"oracle_sha256": SHA["a"]}},
        )
        parent = next(item for item in old if item["unit_id"] == "goal-divergence")
        replay = replay_attestation(parent=parent, spec=new_spec, oracle=lambda _report: (True, []))
        updated = [replay if item["unit_id"] == "goal-divergence" else item for item in old]
        result = verify_evaluation(
            product=selected, spec=new_spec, attestations=updated,
            previous_product=previous_product(),
            holdout_mapping=mapping, mapping_revealed_at=REVEALED_AT,
        )
        self.assertTrue(result["verified"])
        self.assertEqual(replay["terminal"]["model_calls"], 0)
        self.assertEqual(replay["observation"]["parent_attestation_sha256"], parent["record_sha256"])


class FixedHoldoutTests(unittest.TestCase):
    def test_exact_three_pairs_and_freeze_before_reveal(self):
        selected, spec, _, mapping, attestations, evaluation = positive_evaluation()
        self.assertEqual(len(spec["holdouts"]), 3)
        self.assertEqual(len(evaluation["holdout"]["pairs"]), 3)
        self.assertTrue(evaluation["holdout"]["aggregate"]["token_ratio_within_1_25"])
        self.assertTrue(evaluation["holdout"]["aggregate"]["wall_ratio_within_1_25"])
        with self.assertRaises(HoldoutError):
            judge_fixed_holdouts(
                spec=spec,
                attestations=[item for item in attestations if item["unit_id"].startswith("holdout-")],
                mapping=mapping, revealed_at="2026-08-02T00:00:05Z",
                candidate_product=selected, previous_product=previous_product(),
            )

    def test_pair_arms_must_overlap(self):
        selected, spec, projections, mapping = bundle()
        changed = result_for("holdout-1-arm-b")
        changed["started_at"] = "2026-08-02T00:00:11Z"
        changed["frozen_at"] = "2026-08-02T00:00:15Z"
        attestations = attest_all(selected, spec, projections, results={"holdout-1-arm-b": changed})
        holdouts = [item for item in attestations if item["unit_id"].startswith("holdout-")]
        with self.assertRaises(HoldoutError):
            judge_fixed_holdouts(
                spec=spec, attestations=holdouts, mapping=mapping,
                revealed_at=REVEALED_AT, candidate_product=selected,
                previous_product=previous_product(),
            )

    def test_baseline_must_be_the_previous_released_product(self):
        selected, spec, _, mapping, attestations, _ = positive_evaluation()
        wrong_previous = deepcopy(previous_product())
        wrong_previous["record_sha256"] = SHA["f"]
        with self.assertRaises((VerificationError, RecordError)):
            verify_evaluation(
                product=selected, spec=spec, attestations=attestations,
                previous_product=wrong_previous, holdout_mapping=mapping,
                mapping_revealed_at=REVEALED_AT,
            )

    def test_aggregate_token_and_wall_ratios_are_strict(self):
        selected, spec, projections, mapping = bundle()
        expensive = {}
        for index in range(1, 4):
            unit_id = f"holdout-{index}-arm-a"
            expensive[unit_id] = result_for(
                unit_id,
                terminal_value=terminal(input_tokens=20, output_tokens=2, wall_milliseconds=20),
            )
        attestations = attest_all(selected, spec, projections, results=expensive)
        result = judge_fixed_holdouts(
            spec=spec,
            attestations=[item for item in attestations if item["unit_id"].startswith("holdout-")],
            mapping=mapping, revealed_at=REVEALED_AT,
            candidate_product=selected, previous_product=previous_product(),
        )
        self.assertFalse(result["passed"])
        self.assertFalse(result["aggregate"]["token_ratio_within_1_25"])
        self.assertFalse(result["aggregate"]["wall_ratio_within_1_25"])


class ExactFinalAndReleaseTests(unittest.TestCase):
    def test_adverse_exact_final_is_durable_and_cannot_be_replaced(self):
        selected, spec, projections, _ = bundle()
        adverse = attest_all(
            selected, spec, projections,
            results={"exact-final": result_for("exact-final", decision="NOT_YET")},
        )
        adverse_final = next(item for item in adverse if item["unit_id"] == "exact-final")
        self.assertEqual(adverse_final["verdict"], "fail")
        friendly = next(
            item for item in attest_all(selected, spec, projections)
            if item["unit_id"] == "exact-final"
        )
        with self.assertRaises(VerificationError):
            append_attestation([adverse_final], friendly)

    def _release_fixture(self):
        selected, _, _, _, _, evaluation = positive_evaluation()
        destination = {"kind": "plugin-cache", "identity_sha256": SHA["a"]}
        rollback = {"artifact_sha256": SHA["b"], "config_sha256": SHA["c"], "ready": True}
        request = release_authority_request(
            product_record_sha256=selected["record_sha256"],
            attestation_sha256s=evaluation["attestation_sha256s"],
            destination_sha256=canonical_sha256(destination),
            rollback_sha256=canonical_sha256(rollback),
        )
        supplied = {
            "scope": "release", "request_sha256": request,
            "nonce": "release-turn", "signature": "external-release",
        }
        capability_value = accept_release_authority(
            request, supplied, lambda value: value["signature"] == "external-release"
        )
        install = {
            "artifact_sha256": selected["package_artifact_sha256"],
            "install_sha256": SHA["d"], "invocation_sha256": SHA["e"],
            "status": "success",
        }
        receipt = create_release_receipt(
            product=selected, evaluation=evaluation, isolated_install=install,
            destination=destination, rollback=rollback, capability=capability_value,
        )
        return selected, evaluation, destination, rollback, receipt

    def test_release_positive_binds_install_destination_rollback_and_authority(self):
        selected, evaluation, destination, rollback, receipt = self._release_fixture()
        result = verify_release(
            product=selected, evaluation=evaluation, receipt=receipt,
            destination=destination, rollback=rollback,
        )
        self.assertTrue(result["verified"])
        self.assertNotEqual(receipt["release_authority_sha256"], evaluation["authority_sha256"])

    def test_release_mismatch_is_refused(self):
        selected, evaluation, destination, rollback, receipt = self._release_fixture()
        with self.assertRaises(VerificationError):
            verify_release(
                product=selected, evaluation=evaluation, receipt=receipt,
                destination={**destination, "identity_sha256": SHA["f"]},
                rollback=rollback,
            )
        with self.assertRaises(VerificationError):
            verify_release(
                product=selected, evaluation=evaluation, receipt=receipt,
                destination=destination,
                rollback={**rollback, "config_sha256": SHA["f"]},
            )

    def test_release_receipt_rejects_installing_different_artifact(self):
        selected, _, _, _, _, evaluation = positive_evaluation()
        destination = {"kind": "plugin-cache", "identity_sha256": SHA["a"]}
        rollback = {"artifact_sha256": SHA["b"], "config_sha256": SHA["c"], "ready": True}
        request = release_authority_request(
            product_record_sha256=selected["record_sha256"],
            attestation_sha256s=evaluation["attestation_sha256s"],
            destination_sha256=canonical_sha256(destination),
            rollback_sha256=canonical_sha256(rollback),
        )
        cap = accept_release_authority(
            request,
            {"scope": "release", "request_sha256": request, "nonce": "n", "signature": "s"},
            lambda _value: True,
        )
        with self.assertRaises(RecordError):
            create_release_receipt(
                product=selected, evaluation=evaluation,
                isolated_install={
                    "artifact_sha256": SHA["f"], "install_sha256": SHA["d"],
                    "invocation_sha256": SHA["e"], "status": "success",
                },
                destination=destination, rollback=rollback, capability=cap,
            )


class FreshProcessTests(unittest.TestCase):
    def test_cli_verifies_caller_supplied_immutable_records_without_ledger(self):
        selected, spec, _, mapping, attestations, _ = positive_evaluation()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            product_path, previous_path, spec_path, mapping_path = root / "product.json", root / "previous.json", root / "spec.json", root / "mapping.json"
            write_json(product_path, selected)
            write_json(previous_path, previous_product())
            write_json(spec_path, spec)
            write_json(mapping_path, mapping)
            attestation_paths = []
            for index, record in enumerate(attestations):
                path = root / f"attestation-{index}.json"
                write_json(path, record)
                attestation_paths.extend(["--attestation", str(path)])
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "verify",
                    "--product", str(product_path), "--spec", str(spec_path),
                    "--previous-product", str(previous_path),
                    *attestation_paths, "--mapping", str(mapping_path),
                    "--revealed-at", REVEALED_AT,
                ],
                cwd=Path(__file__).resolve().parents[1], capture_output=True,
                text=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["verified"])


if __name__ == "__main__":
    unittest.main()
