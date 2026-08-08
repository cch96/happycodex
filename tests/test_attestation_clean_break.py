from __future__ import annotations

from copy import deepcopy
import json
import unittest

from evaluation.canonical import sealed
from evaluation.policy import RECORD_TYPES, SCHEMA_VERSION
from evaluation.records import RecordError, validate_record
from tests.attestation_fixtures import ROOT, RecordFactory


class SchemaV3CleanBreakTests(unittest.TestCase):
    def test_schema_is_v3_only_with_no_legacy_record_alias(self):
        self.assertEqual(SCHEMA_VERSION, 3)
        self.assertEqual(len(RECORD_TYPES), 4)
        factory = RecordFactory()
        old = deepcopy({key: value for key, value in factory.product.items() if key != "record_sha256"})
        old["schema_version"] = 2
        with self.assertRaises(RecordError):
            validate_record(sealed(old))

    def test_retired_fields_fail_instead_of_migrating(self):
        factory = RecordFactory()
        retired = {
            "ProductArtifact": (factory.product, "package_semantic_sha256"),
            "EvalSpec": (factory.spec, "effect_cap"),
            "Attestation": (factory.make_attestation("qualification-routing"), "terminal"),
        }
        for record_type, (record, field) in retired.items():
            body = deepcopy({key: value for key, value in record.items() if key != "record_sha256"})
            body[field] = "retired"
            with self.subTest(record_type=record_type):
                with self.assertRaises(RecordError):
                    validate_record(sealed(body))

    def test_production_json_inputs_are_schema_v3_despite_stable_filenames(self):
        for name in (
            "manifest-v1.json", "provider-fixtures-v1.json",
            "hidden-oracles-v1.json", "report-schemas-v1.json",
        ):
            value = json.loads((ROOT / "evaluation" / name).read_text())
            self.assertEqual(value["schema_version"], 3)

    def test_no_compatibility_reader_ledger_or_controller_surface(self):
        source = "\n".join(
            path.read_text(encoding="utf-8") for path in (ROOT / "evaluation").glob("*.py")
        )
        for retired in (
            "compatibility_reader", "migrate_record", "dual_write",
            "execute_fixed_host_transaction", "reserve_claim", "replay_attestation",
        ):
            self.assertNotIn(retired, source)

    def test_product_skill_never_links_maintainer_evaluator(self):
        skill = (ROOT / "skills/happycodex/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("evaluation/", skill)
        self.assertNotIn("evaluator", skill.lower())


if __name__ == "__main__":
    unittest.main()
