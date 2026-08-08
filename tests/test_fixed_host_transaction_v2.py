from __future__ import annotations

import ast
from copy import deepcopy
import unittest

from evaluation.provider import release_authority_request_payload, release_effect_subject
from tests.attestation_fixtures import ROOT, RecordFactory
from tests.fake_external_host import FakeBoundaryError, FakeExternalBoundary


class FakeExternalBoundaryTests(unittest.TestCase):
    def test_authority_kind_is_explicit_and_evaluation_release_are_separate(self):
        factory = RecordFactory()
        evaluation = factory.evaluation_authority
        effect = release_effect_subject(
            product_artifact_sha256=factory.product["artifact_sha256"], destination="cache",
            target_identity="target", rollback_identity="rollback",
            installed_projection_sha256=factory.product["projections"]["plugin_runtime"]["projection_sha256"],
        )
        request = release_authority_request_payload(
            product_artifact_sha256=factory.product["artifact_sha256"],
            eval_spec_sha256=factory.spec["spec_sha256"],
            prerequisite_attestation_sha256s=["1" * 64],
            exact_final_attestation_sha256="1" * 64,
            holdout_result_sha256="2" * 64,
            release_effect_subject_sha256=effect,
        )
        release = factory.boundary.issue_authority(request, kind="release")
        self.assertNotEqual(evaluation["authority_identity"], release["authority_identity"])
        with self.assertRaises(FakeBoundaryError):
            factory.boundary.issue_authority(request, kind="evaluation")

    def test_landed_and_unknown_are_one_shot_across_execution_roots(self):
        for outcome in ("landed", "unknown"):
            factory = RecordFactory()
            first = factory.make_attestation(
                "exact-final", outcome=outcome, execution_root="/root/one",
            )
            with self.assertRaisesRegex(FakeBoundaryError, "one-shot"):
                factory.make_attestation(
                    "exact-final", attempt=1, prior=[first],
                    execution_root="/root/two",
                )

    def test_malformed_and_not_yet_landed_exact_final_consume_one_shot(self):
        for report in ({}, RecordFactory().not_yet_report()):
            factory = RecordFactory()
            adverse = factory.make_attestation("exact-final", report=report)
            self.assertFalse(adverse["assessment"]["passed"])
            with self.assertRaises(FakeBoundaryError):
                factory.make_attestation(
                    "exact-final", attempt=1, prior=[adverse], report=factory.go_report(),
                )

    def test_only_pre_provider_zero_use_not_landed_can_recover_within_cap(self):
        factory = RecordFactory()
        first = factory.make_attestation("qualification-routing", outcome="not_landed")
        second = factory.make_attestation(
            "qualification-routing", attempt=1, prior=[first],
        )
        self.assertEqual(
            factory.boundary.attempts(factory.unit("qualification-routing")["effect_subject_sha256"]),
            (("not_landed", "/external/root-a"), ("landed", "/external/root-a")),
        )
        boundary = FakeExternalBoundary()
        statement = {
            "kind": "provider_terminal", "effect_subject_sha256": "e" * 64,
            "attempt": 0, "effect_outcome": "not_landed",
            "observation": {
                "provider_reached": True, "response_complete": False,
                "model_calls": 0, "input_tokens": 0, "output_tokens": 0,
            },
        }
        with self.assertRaisesRegex(FakeBoundaryError, "pre-effect"):
            boundary.sign_terminal(statement, execution_root="/root")

    def test_test_boundary_and_production_host_have_no_execution_engine(self):
        host = (ROOT / "evaluation/host.py").read_text(encoding="utf-8")
        tree = ast.parse(host)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertFalse(imports & {"subprocess", "socket", "requests", "os", "time"})
        for retired in ("execute_fixed_host_transaction", "reserve_claim", "effect_marker", "ledger"):
            self.assertNotIn(retired, host)


if __name__ == "__main__":
    unittest.main()
