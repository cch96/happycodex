from __future__ import annotations

from copy import deepcopy
import unittest

from evaluation.manifest import ManifestError, materialize_eval_spec
from evaluation.records import (
    RecordError,
    canonical_sha256,
    evaluation_authority_request_payload,
    validate_eval_spec,
)
from evaluation.verify import invalidation
from tests.attestation_fixtures import (
    HOST_CONTRACT,
    PROFILES,
    REVIEW_BRIEF,
    ROOT,
    TOTAL_CAP,
    mapping,
    previous_product,
    product,
    reseal,
)


def materialize(profiles: dict = PROFILES, total_cap: dict = TOTAL_CAP) -> dict:
    return materialize_eval_spec(
        root=ROOT,
        candidate=product(),
        previous=previous_product(),
        profiles=deepcopy(profiles),
        total_cap=deepcopy(total_cap),
        holdout_mapping=mapping(),
        review_brief=deepcopy(REVIEW_BRIEF),
        host_contract=deepcopy(HOST_CONTRACT),
        external_role_config_sha256="3" * 64,
    )


class StageProfileContractTests(unittest.TestCase):
    def test_profiles_require_the_fixed_command_execution_tool(self):
        for tools in ([], ["command_execution", "extra"]):
            with self.subTest(tools=tools):
                profiles = deepcopy(PROFILES)
                profiles["behavior"]["tools"] = tools
                with self.assertRaises(RecordError):
                    materialize(profiles)

    def test_model_call_cap_must_equal_the_fixed_invocation_count(self):
        with self.assertRaises(ManifestError):
            materialize(total_cap={**TOTAL_CAP, "model_calls": 13})
        spec = deepcopy(materialize())
        spec["effect_cap"]["model_calls"] = 13
        spec["authority_request_sha256"] = canonical_sha256(
            evaluation_authority_request_payload(spec)
        )
        with self.assertRaises(RecordError):
            validate_eval_spec(reseal(spec))

    def test_materializer_binds_behavior_and_exact_final_profiles_by_stage(self):
        spec = materialize()
        self.assertEqual(spec["profiles"], PROFILES)
        for unit in spec["units"]:
            expected = PROFILES["exact_final" if unit["stage"] == "exact_final" else "behavior"]
            actual = {
                key: unit["invocation"][key]
                for key in ("model", "effort", "tools", "timeout_seconds")
            }
            self.assertEqual(actual, expected)

    def test_validator_rejects_profile_drift_in_both_stage_directions(self):
        for stage, wrong_profile in (
            ("behavior", PROFILES["exact_final"]),
            ("exact_final", PROFILES["behavior"]),
        ):
            with self.subTest(stage=stage):
                spec = deepcopy(materialize())
                unit = next(item for item in spec["units"] if item["stage"] == stage)
                invocation = unit["invocation"]
                for key, value in wrong_profile.items():
                    invocation[key] = deepcopy(value)
                invocation["provider_input"]["profile"] = deepcopy(wrong_profile)
                unit["provider_input_sha256"] = canonical_sha256(invocation["provider_input"])
                invocation["claim_key"] = canonical_sha256(
                    {
                        "unit_id": unit["unit_id"],
                        "stage": stage,
                        "product": unit["product_semantic_sha256"],
                        "role_config": unit["external_role_config_sha256"],
                        "effective_host": invocation["effective_host_sha256"],
                        "provider_input": invocation["provider_input"],
                    }
                )
                unit["invocation_sha256"] = canonical_sha256(invocation)
                spec["authority_request_sha256"] = canonical_sha256(
                    evaluation_authority_request_payload(spec)
                )
                with self.assertRaisesRegex(RecordError, "unit stage profile differs"):
                    validate_eval_spec(reseal(spec))

    def test_legacy_single_profile_field_is_rejected(self):
        spec = deepcopy(materialize())
        spec["profile"] = spec.pop("profiles")["behavior"]
        with self.assertRaises(RecordError):
            validate_eval_spec(reseal(spec))

    def test_authority_binds_both_profiles_and_every_invocation(self):
        spec = materialize()
        payload = evaluation_authority_request_payload(spec)
        self.assertEqual(payload["profiles"], PROFILES)
        self.assertEqual(payload["decision"], "full_evaluation")
        self.assertEqual(
            payload["effect_cap"],
            {key: TOTAL_CAP[key] for key in ("model_calls", "wall_milliseconds")},
        )
        self.assertEqual(payload["prerequisites"], [])
        self.assertIsNone(payload["prerequisite_state"])
        self.assertEqual(
            [item["invocation_sha256"] for item in payload["invocations"]],
            [unit["invocation_sha256"] for unit in spec["units"]],
        )

    def test_production_profile_target_uses_same_model_and_distinct_efforts(self):
        production = deepcopy(PROFILES)
        for profile in production.values():
            profile["model"] = "gpt-5.6-sol"
        spec = materialize(production)
        self.assertEqual(spec["profiles"]["behavior"]["effort"], "high")
        self.assertEqual(spec["profiles"]["exact_final"]["effort"], "max")
        self.assertEqual(
            {profile["model"] for profile in spec["profiles"].values()},
            {"gpt-5.6-sol"},
        )

    def test_profile_invalidation_uses_only_explicit_modes(self):
        original = materialize()

        exact_profiles = deepcopy(PROFILES)
        exact_profiles["exact_final"]["effort"] = "xhigh"
        exact_impact = invalidation(original, materialize(exact_profiles))
        self.assertEqual(exact_impact, {"mode": "exact_final_only"})

        behavior_profiles = deepcopy(PROFILES)
        behavior_profiles["behavior"]["effort"] = "medium"
        behavior_impact = invalidation(original, materialize(behavior_profiles))
        self.assertEqual(behavior_impact, {"mode": "full_evaluation"})

    def test_external_role_change_requires_full_evaluation(self):
        original = materialize()
        changed_role = canonical_sha256({"external_role": "changed"})
        changed_host = deepcopy(HOST_CONTRACT)
        changed_host["behavior_sha256"] = canonical_sha256({"behavior_host": changed_role})
        changed_host["holdout_sha256"] = canonical_sha256({"holdout_host": changed_role})
        changed = materialize_eval_spec(
            root=ROOT,
            candidate=product(),
            previous=previous_product(),
            profiles=deepcopy(PROFILES),
            total_cap=deepcopy(TOTAL_CAP),
            holdout_mapping=mapping(),
            review_brief=deepcopy(REVIEW_BRIEF),
            host_contract=changed_host,
            external_role_config_sha256=changed_role,
        )

        self.assertEqual(invalidation(original, changed), {"mode": "full_evaluation"})

        original_exact = next(unit for unit in original["units"] if unit["stage"] == "exact_final")
        changed_exact = next(unit for unit in changed["units"] if unit["stage"] == "exact_final")
        self.assertEqual(changed_exact["provider_input_sha256"], original_exact["provider_input_sha256"])
        self.assertEqual(
            changed_exact["invocation"]["claim_key"],
            original_exact["invocation"]["claim_key"],
        )
        self.assertEqual(changed_exact["invocation"], original_exact["invocation"])
        self.assertEqual(changed_exact["invocation_sha256"], original_exact["invocation_sha256"])


if __name__ == "__main__":
    unittest.main()
