from __future__ import annotations

from copy import deepcopy
import json
import unittest

from evaluation.canonical import canonical_sha256, sealed
from evaluation.manifest import load_production_inputs, public_provider_inputs
from evaluation.policy import RECORD_TYPES, UNIT_TOPOLOGY
from evaluation.records import RecordError, validate_record
from evaluation.schemas import SchemaError, validate_schema
from tests.attestation_fixtures import ROOT, RecordFactory, reseal


class DurableRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = RecordFactory()
        cls.terminals, cls.holdout, cls.evaluation = cls.factory.full_evaluation()
        cls.receipt, _ = cls.factory.release(cls.evaluation)
        cls.records = (
            cls.factory.product, cls.factory.spec, cls.terminals[0].record, cls.receipt,
        )

    def test_exactly_four_closed_durable_types(self):
        self.assertEqual(
            RECORD_TYPES, ("ProductArtifact", "EvalSpec", "Attestation", "ReleaseReceipt"),
        )
        for record in self.records:
            self.assertIs(validate_record(record), record)
            unknown = reseal(record, lambda value: value.__setitem__("unknown", True))
            with self.assertRaises(RecordError):
                validate_record(unknown)
        with self.assertRaisesRegex(RecordError, "unknown durable"):
            validate_record({"record_type": "EvidenceGraph"})

    def test_seals_and_headers_fail_closed(self):
        for record in self.records:
            changed = deepcopy(record)
            changed["schema_version"] = 2
            with self.assertRaises(RecordError):
                validate_record(changed)
            changed = deepcopy(record)
            changed["record_sha256"] = "0" * 64
            with self.assertRaises(RecordError):
                validate_record(changed)

    def test_nested_product_paths_modes_and_projection_are_closed(self):
        product = self.factory.product
        mutations = (
            lambda value: value["projections"]["plugin_runtime"]["entries"][0].__setitem__("extra", 1),
            lambda value: value["projections"]["plugin_runtime"]["entries"][0].__setitem__("path", "../escape"),
            lambda value: value["projections"]["plugin_runtime"]["entries"][0].__setitem__("mode", "120000"),
            lambda value: value["projections"]["plugin_runtime"]["entries"][0].__setitem__("state", "absent"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                with self.assertRaises(RecordError):
                    validate_record(reseal(product, mutate))

    def test_evalspec_nested_topology_and_caps_are_closed(self):
        for mutate in (
            lambda value: value["units"][0].__setitem__("extra", 1),
            lambda value: value["caps"].__setitem__("claimed_passes", 99),
            lambda value: value["component_identities"].__setitem__("combined", "0" * 64),
        ):
            with self.assertRaises(RecordError):
                validate_record(reseal(self.factory.spec, mutate))

    def test_attestation_observation_binding_and_attempt_rules_are_closed(self):
        record = self.terminals[0].record
        mutations = (
            lambda value: value["observation"].__setitem__("wall_claim", 0),
            lambda value: value["evidence_binding"].__setitem__("key", "self-signed"),
            lambda value: value["observation"].__setitem__("response_complete", False),
            lambda value: value["observation"].__setitem__("effect_cumulative_wall_milliseconds", 11),
        )
        for mutate in mutations:
            with self.assertRaises(RecordError):
                validate_record(reseal(record, mutate))
        no_effect = RecordFactory().make_attestation(
            "qualification-routing", outcome="not_landed",
        )
        with self.assertRaises(RecordError):
            validate_record(reseal(no_effect, lambda value: value["observation"].__setitem__("model_calls", 1)))

    def test_release_readback_shape_is_closed_and_terminal(self):
        for mutate in (
            lambda value: value["observation"].__setitem__("claimed_success", True),
            lambda value: value["observation"].__setitem__("readback_complete", False),
            lambda value: value["observation"].__setitem__("observed_destination", None),
        ):
            with self.assertRaises(RecordError):
                validate_record(reseal(self.receipt, mutate))
        body = deepcopy({key: value for key, value in self.receipt.items() if key != "record_sha256"})
        body["outcome"] = "not_landed"
        body["observation"].update({"effect_reached": False, "readback_complete": False})
        with self.assertRaises(RecordError):
            validate_record(sealed(body))


class ProviderSchemaTests(unittest.TestCase):
    def test_public_projection_excludes_oracles_mappings_answers_and_history(self):
        inputs = load_production_inputs(ROOT)
        public = public_provider_inputs(inputs)
        self.assertEqual(set(public), {"cases", "schemas"})
        visible = json.dumps(public, sort_keys=True).lower()
        for forbidden in ("hidden_oracles", "mapping_commitment", "desired_verdict", "repair_history"):
            self.assertNotIn(forbidden, visible)
        sentinel = "PRIVATE-ORACLE-SENTINEL"
        changed = deepcopy(inputs)
        changed["oracles"]["core"][next(iter(changed["oracles"]["core"]))]["sentinel"] = sentinel
        self.assertNotIn(sentinel, json.dumps(public_provider_inputs(changed)))

    def test_every_recursive_provider_schema_is_fixed_and_closed(self):
        schemas = load_production_inputs(ROOT)["schemas"]
        def walk(schema):
            validate_schema(schema)
            if schema["type"] == "object":
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual(schema["required"], list(schema["properties"]))
                for child in schema["properties"].values():
                    walk(child)
            elif schema["type"] == "array":
                walk(schema["items"])
        for group in ("provider_inputs", "provider_outputs"):
            for schema in schemas[group].values():
                walk(schema)
        bad = deepcopy(next(iter(schemas["provider_inputs"].values())))
        bad["description"] = "expected answer"
        with self.assertRaises(SchemaError):
            validate_schema(bad)

    def test_no_reveal_timestamp_or_extra_topology_unit_exists(self):
        for path in (ROOT / "evaluation").iterdir():
            if path.is_file() and path.suffix in {".py", ".json"}:
                self.assertNotIn("revealed_at", path.read_text(encoding="utf-8"))
        self.assertEqual(len(UNIT_TOPOLOGY), 12)


if __name__ == "__main__":
    unittest.main()
