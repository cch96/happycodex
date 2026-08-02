from __future__ import annotations

import unittest

from evaluation.records import (
    RECORD_TYPES,
    RecordError,
    build_product_artifact,
    validate_record,
)
from evaluation.provider import provider_projection


H = {
    "artifact": "1" * 64,
    "semantic": "2" * 64,
    "role": "3" * 64,
    "evaluator": "4" * 64,
}


class CleanBreakRedTests(unittest.TestCase):
    def test_durable_record_inventory_is_exactly_four(self):
        self.assertEqual(
            RECORD_TYPES,
            frozenset(
                {"ProductArtifact", "EvalSpec", "Attestation", "ReleaseReceipt"}
            ),
        )
        with self.assertRaises(RecordError):
            validate_record({"record_type": "GateReceipt"})

    def test_product_identity_has_no_evaluator_component(self):
        record = build_product_artifact(
            source_commit="a" * 40,
            source_tree="b" * 40,
            package_tree="c" * 40,
            package_artifact_sha256=H["artifact"],
            package_semantic_sha256=H["semantic"],
            external_role_config_sha256=H["role"],
        )
        self.assertNotIn("evaluator", str(record).lower())
        self.assertEqual(validate_record(record), record)

    def test_provider_projection_is_allowlisted_not_redacted(self):
        case = {
            "role_id": "qualification-high-risk",
            "fixture": {"request": "classify"},
            "workspace": {"clean": True},
            "runtime": "runtime bytes",
            "prompt": "classify the task",
            "expected_answer": "SENTINEL",
            "oracle": {"answer": "SENTINEL"},
            "matcher": "SENTINEL",
            "mapping": "SENTINEL",
            "verdict": "SENTINEL",
            "history": "SENTINEL",
        }
        projection = provider_projection(
            case=case,
            product_semantic_sha256=H["semantic"],
            external_role_config_sha256=H["role"],
            profile={
                "model": "gpt-test",
                "effort": "high",
                "tools": ["command_execution"],
                "timeout_seconds": 30,
            },
        )
        self.assertNotIn("SENTINEL", str(projection))
        self.assertEqual(projection["prompt"], "classify the task")


if __name__ == "__main__":
    unittest.main()
