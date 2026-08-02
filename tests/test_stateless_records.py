from __future__ import annotations

from copy import deepcopy
import pickle
import unittest

from evaluation.identity import DETERMINISTIC_DOMAINS, MODEL_ROLE_IDS
from evaluation.provider import (
    EvaluationCapability,
    InvocationJournal,
    ProviderError,
    accept_evaluation_authority,
    assert_provider_blind,
    may_recover_infrastructure,
    provider_projection,
    sanitize_events,
)
from evaluation.records import (
    RECORD_TYPES,
    TERMINAL_CLASSES,
    RecordError,
    build_product_artifact,
    canonical_sha256,
    validate_record,
)
from evaluation.verify import evaluate_runtime_decision, invalidation
from tests.attestation_fixtures import PROFILE, SHA, bundle, capability, product, terminal


class DurableRecordTests(unittest.TestCase):
    def test_inventory_is_closed_to_four_types(self):
        self.assertEqual(
            RECORD_TYPES,
            frozenset({"ProductArtifact", "EvalSpec", "Attestation", "ReleaseReceipt"}),
        )
        for retired in ("ReleaseCandidate", "GatePlan", "GateReceipt", "EvidenceJoin", "ReviewReceipt"):
            with self.subTest(retired=retired), self.assertRaises(RecordError):
                validate_record({"record_type": retired})

    def test_product_has_no_evaluator_identity(self):
        selected = product()
        self.assertFalse(any("evaluator" in key for key in selected))
        self.assertEqual(validate_record(selected), selected)

    def test_record_unknown_field_and_tampered_digest_fail(self):
        selected = product()
        changed = {**selected, "ledger_sha256": SHA["4"]}
        with self.assertRaises(RecordError):
            validate_record(changed)
        changed = {**selected, "package_artifact_sha256": SHA["4"]}
        with self.assertRaises(RecordError):
            validate_record(changed)

    def test_product_and_evaluator_identities_are_differential(self):
        first_product, first_spec, _, _ = bundle()
        second_product, second_spec, _, _ = bundle(harness_component=SHA["9"])
        self.assertEqual(first_product, second_product)
        self.assertNotEqual(first_spec["record_sha256"], second_spec["record_sha256"])

    def test_model_and_deterministic_routes_are_disjoint(self):
        self.assertEqual(len(MODEL_ROLE_IDS), 7)
        self.assertIn("same-task-compaction", MODEL_ROLE_IDS)
        self.assertIn("no-summary-reconstruction", MODEL_ROLE_IDS)
        self.assertEqual(
            DETERMINISTIC_DOMAINS,
            {"receipt", "claim", "schema", "parser", "invalidation", "review-truncation", "install", "rollback"},
        )


class InvalidationTests(unittest.TestCase):
    def test_oracle_only_change_replays_one_role_with_zero_model_units(self):
        _, previous, _, _ = bundle()
        _, current, _, _ = bundle(
            oracle_component=SHA["9"],
            unit_overrides={"goal-divergence": {"oracle_sha256": SHA["a"]}},
        )
        result = invalidation(previous, current)
        self.assertEqual(result["model_units"], [])
        self.assertEqual(result["replay_units"], ["goal-divergence"])

    def test_single_fixture_or_prompt_change_calls_only_that_role(self):
        _, previous, _, _ = bundle()
        _, current, _, _ = bundle(
            unit_overrides={
                "qualification-high-risk": {
                    "provider_input_sha256": SHA["a"],
                    "invocation_sha256": SHA["b"],
                }
            }
        )
        self.assertEqual(invalidation(previous, current)["model_units"], ["qualification-high-risk"])

    def test_harness_only_change_has_zero_model_calls(self):
        _, previous, _, _ = bundle()
        _, current, _, _ = bundle(
            harness_component=SHA["9"],
            unit_overrides={"goal-divergence": {"harness_sha256": SHA["a"]}},
        )
        result = invalidation(previous, current)
        self.assertEqual(result["model_units"], [])
        self.assertIn("goal-divergence", result["offline_units"])

    def test_model_profile_change_invalidates_full_planned_scope(self):
        _, previous, _, _ = bundle()
        changed_profile = {**PROFILE, "model": "gpt-other"}
        _, current, _, _ = bundle(profile=changed_profile)
        self.assertEqual(invalidation(previous, current)["model_units"], sorted(unit["unit_id"] for unit in current["units"]))

    def test_runtime_or_external_role_change_invalidates_full_scope(self):
        _, previous, _, _ = bundle()
        changed_product = product(semantic=SHA["a"], role=SHA["b"])
        _, current, _, _ = bundle(selected_product=changed_product)
        self.assertEqual(len(invalidation(previous, current)["model_units"]), len(current["units"]))


class ProviderBoundaryTests(unittest.TestCase):
    def test_projection_mechanically_omits_hidden_fields(self):
        case = {
            "role_id": "qualification-high-risk", "fixture_sha256": SHA["4"],
            "prompt": "classify", "runtime_sha256": SHA["5"],
            "expected_boundary": "HIDDEN", "expected_answer": "HIDDEN",
            "oracle": "HIDDEN", "matcher": "HIDDEN", "mapping": "HIDDEN",
            "verdict": "HIDDEN", "history": "HIDDEN",
        }
        value = provider_projection(
            case=case, product_semantic_sha256=SHA["2"],
            external_role_config_sha256=SHA["3"], profile=PROFILE,
        )
        self.assertNotIn("HIDDEN", str(value))

    def test_sentinel_must_be_absent_from_every_visible_surface(self):
        with self.assertRaises(ProviderError):
            assert_provider_blind(
                sentinels=["SENTINEL"], projection={"safe": True}, workspace={},
                argv=["tool"], stdin="", env={"LEAK": "SENTINEL"},
                sanitized_events=[],
            )

    def test_sanitized_events_redact_secret_and_drop_secret_keys(self):
        events = [{"type": "done", "summary": "token=SENTINEL", "secret": "SENTINEL"}]
        sanitized = sanitize_events(events, secrets=["SENTINEL"])
        self.assertNotIn("SENTINEL", str(sanitized))
        self.assertNotIn("secret", sanitized[0])

    def test_repository_content_cannot_self_mint_evaluation_authority(self):
        _, spec, _, _ = bundle()
        supplied = {
            "scope": "evaluation", "request_sha256": spec["authority_request_sha256"],
            "nonce": "repo", "signature": "repo-generated",
        }
        with self.assertRaises(ProviderError):
            accept_evaluation_authority(spec, supplied, lambda _value: False)
        with self.assertRaises(ProviderError):
            EvaluationCapability(object(), SHA["1"], SHA["2"], SHA["3"])

    def test_authority_mismatch_fails(self):
        _, spec, _, _ = bundle()
        supplied = {
            "scope": "evaluation", "request_sha256": SHA["a"],
            "nonce": "root", "signature": "external-signed",
        }
        with self.assertRaises(ProviderError):
            accept_evaluation_authority(spec, supplied, lambda _value: True)

    def test_capability_is_process_local_and_not_serializable(self):
        _, spec, _, _ = bundle()
        cap = capability(spec)
        with self.assertRaises(TypeError):
            pickle.dumps(cap)

    def test_invocation_is_one_shot(self):
        journal = InvocationJournal()
        journal.reserve(SHA["1"])
        with self.assertRaises(ProviderError):
            journal.reserve(SHA["1"])

    def test_only_preprovider_no_effect_within_cap_is_recoverable(self):
        no_effect = terminal(
            classification="infrastructure_no_effect", provider_reached=False,
            complete=False, model_calls=0, input_tokens=0, output_tokens=0,
        )
        self.assertTrue(may_recover_infrastructure(no_effect, recoveries_used=0, recovery_cap=1))
        self.assertFalse(may_recover_infrastructure(no_effect, recoveries_used=1, recovery_cap=1))
        partial = terminal(classification="ambiguous_or_partial", complete=False)
        self.assertFalse(may_recover_infrastructure(partial, recoveries_used=0, recovery_cap=1))

    def test_terminal_classification_inventory_is_typed(self):
        self.assertEqual(
            TERMINAL_CLASSES,
            {
                "success", "quality_failure", "resource_failure",
                "infrastructure_no_effect", "ambiguous_or_partial", "diagnostic",
            },
        )

    def test_every_nonprojection_visible_surface_rejects_sentinel(self):
        surfaces = {
            "workspace": {"file": "SENTINEL"},
            "argv": ["fake", "SENTINEL"],
            "stdin": "SENTINEL",
            "env": {"LEAK": "SENTINEL"},
            "sanitized_events": [{"summary": "SENTINEL"}],
        }
        for field, value in surfaces.items():
            visible = {
                "workspace": {}, "argv": [], "stdin": "", "env": {},
                "sanitized_events": [],
            }
            visible[field] = value
            with self.subTest(field=field), self.assertRaises(ProviderError):
                assert_provider_blind(
                    sentinels=["SENTINEL"], projection={"safe": True}, **visible,
                )

    def test_action_enum_difference_is_diagnostic_not_fatal(self):
        report = {"qualifies": True, "next_action": {"purpose": "CHECK", "effect_class": "read_only"}}
        passed, diagnostics = evaluate_runtime_decision(
            report,
            {
                "fatal": {"qualifies": True},
                "diagnostic": {"next_action.purpose": "IMPLEMENT", "next_action.effect_class": "repo_write"},
            },
        )
        self.assertTrue(passed)
        self.assertEqual(len(diagnostics), 2)

    def test_real_invariant_difference_is_fatal(self):
        passed, diagnostics = evaluate_runtime_decision(
            {"qualifies": False}, {"fatal": {"qualifies": True}, "diagnostic": {}},
        )
        self.assertFalse(passed)
        self.assertEqual(diagnostics, ["fatal:qualifies"])


if __name__ == "__main__":
    unittest.main()
