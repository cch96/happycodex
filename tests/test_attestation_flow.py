from __future__ import annotations

from copy import deepcopy
import unittest

from evaluation.canonical import canonical_sha256
from evaluation.holdout import HoldoutError, judge_fixed_holdouts
from evaluation.policy import UNIT_TOPOLOGY
from evaluation.records import RecordError, validate_attestation
from evaluation.verify import (
    VerifyError, assess_provider_report, authenticate_attestation,
    verify_effect_sequence, verify_evaluation, verify_release,
)
from tests.attestation_fixtures import RecordFactory, reseal, sha
from tests.fake_external_host import FakeBoundaryError


def evaluation_from(factory: RecordFactory, terminals):
    holdouts = [terminal for terminal in terminals if terminal.record["stage"] == "holdout"]
    result = judge_fixed_holdouts(spec=factory.spec, terminals=holdouts, mappings=factory.mappings)
    return result, verify_evaluation(spec=factory.spec, terminals=terminals, holdout_result=result)


class AuthenticationTests(unittest.TestCase):
    def test_valid_external_authority_and_terminal_authentication(self):
        factory = RecordFactory()
        record = factory.make_attestation("qualification-routing")
        verified = factory.authenticate(record)
        self.assertEqual(verified.record, record)
        self.assertEqual(verified.authenticator_id, factory.boundary.authenticator_id)

    def test_resealed_wrong_authenticator_and_signature_fail(self):
        for field, value in (("authenticator_id", "forged"), ("signature", "forged")):
            factory = RecordFactory()
            record = factory.make_attestation("qualification-routing")
            forged = reseal(record, lambda body: body["evidence_binding"].__setitem__(field, value))
            validate_attestation(forged)
            with self.assertRaises(VerifyError):
                factory.authenticate(forged)

    def test_resealed_wrong_effect_attempt_and_authority_fail(self):
        mutations = (
            lambda body: body.__setitem__("effect_subject_sha256", sha("wrong-effect")),
            lambda body: (
                body.__setitem__("attempt", 1),
                body.__setitem__("attempt_identity_sha256", canonical_sha256({
                    "effect_subject_sha256": body["effect_subject_sha256"], "attempt": 1,
                })),
                body["observation"].__setitem__("recovery_history_sha256", sha("history")),
            ),
            lambda body: body.__setitem__("authority_sha256", sha("wrong-authority")),
        )
        for mutate in mutations:
            factory = RecordFactory()
            record = factory.make_attestation("qualification-routing")
            forged = reseal(record, mutate)
            with self.assertRaises((RecordError, VerifyError)):
                factory.authenticate(forged)

    def test_unissued_authority_is_rejected(self):
        factory = RecordFactory()
        record = factory.make_attestation("qualification-routing")
        authority = deepcopy(factory.evaluation_authority)
        authority["signature"] = "forged"
        authority["authority_sha256"] = canonical_sha256({
            key: authority[key] for key in ("authority_identity", "request_sha256", "signature")
        })
        with self.assertRaises(VerifyError):
            authenticate_attestation(
                record, spec=factory.spec, provider_input=factory.inputs[record["unit_id"]],
                response_schema=factory.schemas[record["unit_id"]],
                oracle=factory.oracles[record["unit_id"]], authenticator=factory.boundary,
                evaluation_authority_request=factory.evaluation_request,
                evaluation_authority=authority, authority_validator=factory.boundary,
            )


class AttemptSequenceTests(unittest.TestCase):
    def test_not_landed_then_landed_binds_history_and_cumulative_wall(self):
        factory = RecordFactory()
        first = factory.make_attestation(
            "qualification-routing", outcome="not_landed", wall=7,
            started_at="2026-08-08T00:00:00Z", finished_at="2026-08-08T00:00:01Z",
        )
        second = factory.make_attestation(
            "qualification-routing", attempt=1, prior=[first], wall=10,
            started_at="2026-08-08T00:00:01Z", finished_at="2026-08-08T00:00:02Z",
        )
        terminal = factory.terminal("qualification-routing", [first, second])
        self.assertEqual(terminal.attempt_sha256s, (first["record_sha256"], second["record_sha256"]))
        self.assertEqual(terminal.record["observation"]["effect_cumulative_wall_milliseconds"], 17)

    def test_cumulative_underreport_and_prior_wall_omission_fail(self):
        for cumulative in (10, 16):
            factory = RecordFactory()
            first = factory.make_attestation(
                "qualification-routing", outcome="not_landed", wall=7,
                started_at="2026-08-08T00:00:00Z", finished_at="2026-08-08T00:00:01Z",
            )
            second = factory.make_attestation(
                "qualification-routing", attempt=1, prior=[first], wall=10,
                cumulative=cumulative, started_at="2026-08-08T00:00:01Z",
                finished_at="2026-08-08T00:00:02Z",
            )
            with self.assertRaises(VerifyError):
                factory.terminal("qualification-routing", [first, second])

    def test_attempts_must_be_contiguous_and_within_recovery_cap(self):
        factory = RecordFactory(recovery_cap=0)
        first = factory.make_attestation("qualification-routing", outcome="not_landed")
        with self.assertRaises(FakeBoundaryError):
            factory.make_attestation("qualification-routing", attempt=1, prior=[first])
        with self.assertRaises(VerifyError):
            verify_effect_sequence([factory.authenticate(first)], spec=factory.spec, unit_id="context-isolation")

    def test_retry_after_landed_or_unknown_fails_across_execution_roots(self):
        for terminal_outcome in ("landed", "unknown"):
            first_factory = RecordFactory()
            first = first_factory.make_attestation(
                "qualification-routing", outcome=terminal_outcome,
                execution_root="/external/root-a",
            )
            with self.assertRaises(FakeBoundaryError):
                first_factory.make_attestation(
                    "qualification-routing", attempt=1, prior=[first],
                    execution_root="/external/root-b",
                )
            alternate = RecordFactory()
            prefix = alternate.make_attestation(
                "qualification-routing", outcome="not_landed",
                started_at="2026-08-08T00:00:00Z", finished_at="2026-08-08T00:00:01Z",
            )
            later = alternate.make_attestation(
                "qualification-routing", attempt=1, prior=[prefix],
                started_at="2026-08-08T00:00:05Z", finished_at="2026-08-08T00:00:06Z",
            )
            with self.assertRaises(VerifyError):
                first_factory.terminal("qualification-routing", [first, later])

    def test_recovered_wall_counts_toward_unit_cap(self):
        factory = RecordFactory()
        first = factory.make_attestation(
            "qualification-routing", outcome="not_landed", wall=600,
            started_at="2026-08-08T00:00:00Z", finished_at="2026-08-08T00:00:01Z",
        )
        second = factory.make_attestation(
            "qualification-routing", attempt=1, prior=[first], wall=500,
            started_at="2026-08-08T00:00:01Z", finished_at="2026-08-08T00:00:02Z",
        )
        with self.assertRaisesRegex(VerifyError, "unit cumulative"):
            factory.terminal("qualification-routing", [first, second])


class HoldoutTests(unittest.TestCase):
    def holdouts(self, factory, **candidate_options):
        terminals = []
        for unit in factory.spec["units"]:
            if unit["stage"] != "holdout":
                continue
            options = candidate_options if unit["unit_id"].endswith("-a") else {}
            terminals.append(factory.terminal(unit["unit_id"], [factory.make_attestation(unit["unit_id"], **options)]))
        return terminals

    def test_all_six_authenticated_landed_required_before_mapping_read(self):
        factory = RecordFactory()
        terminals = self.holdouts(factory)
        with self.assertRaisesRegex(HoldoutError, "six"):
            judge_fixed_holdouts(spec=factory.spec, terminals=terminals[:-1], mappings=None)

    def test_mapping_commitment_and_pair_concurrency_are_hard(self):
        factory = RecordFactory(); terminals = self.holdouts(factory)
        changed = deepcopy(factory.mappings)
        changed["holdout-safety"] = {
            "holdout-safety-a": "baseline", "holdout-safety-b": "candidate",
        }
        with self.assertRaisesRegex(HoldoutError, "commitment"):
            judge_fixed_holdouts(spec=factory.spec, terminals=terminals, mappings=changed)
        factory = RecordFactory(); terminals = []
        for unit in factory.spec["units"]:
            if unit["stage"] != "holdout": continue
            options = {}
            if unit["unit_id"] == "holdout-recovery-a":
                options = {"started_at": "2026-08-08T00:00:00Z", "finished_at": "2026-08-08T00:00:01Z"}
            if unit["unit_id"] == "holdout-recovery-b":
                options = {"started_at": "2026-08-08T00:00:01Z", "finished_at": "2026-08-08T00:00:02Z"}
            terminals.append(factory.terminal(unit["unit_id"], [factory.make_attestation(unit["unit_id"], **options)]))
        with self.assertRaisesRegex(HoldoutError, "concurrent"):
            judge_fixed_holdouts(spec=factory.spec, terminals=terminals, mappings=factory.mappings)

    def test_token_ratio_is_hard_and_wall_ratio_is_diagnostic(self):
        factory = RecordFactory()
        tokens = judge_fixed_holdouts(
            spec=factory.spec, terminals=self.holdouts(factory, input_tokens=10, output_tokens=10),
            mappings=factory.mappings,
        )
        self.assertFalse(tokens["aggregate"]["token_ratio_within_1_25"])
        self.assertFalse(tokens["passed"])
        factory = RecordFactory()
        wall = judge_fixed_holdouts(
            spec=factory.spec, terminals=self.holdouts(factory, wall=20), mappings=factory.mappings,
        )
        self.assertFalse(wall["aggregate"]["wall_ratio_within_1_25_diagnostic"])
        self.assertTrue(wall["passed"])


class ExactFinalAndEvaluationTests(unittest.TestCase):
    def test_full_favorable_twelve_unit_path(self):
        factory = RecordFactory()
        terminals, result, evaluation = factory.full_evaluation()
        self.assertEqual(len(terminals), 12)
        self.assertTrue(result["passed"])
        self.assertEqual(len(evaluation.result["prerequisite_attestation_sha256s"]), 12)
        self.assertEqual(evaluation.result["cumulative_effect_wall_milliseconds"], 120)

    def test_missing_duplicate_and_adverse_behavior_terminal_fail(self):
        factory = RecordFactory(); terminals, result, _ = factory.full_evaluation()
        for changed in (terminals[:-1], terminals + [terminals[0]]):
            with self.assertRaises(VerifyError):
                verify_evaluation(spec=factory.spec, terminals=changed, holdout_result=result)
        factory = RecordFactory(); terminals = []
        for unit in UNIT_TOPOLOGY:
            report = {"ok": False} if unit.unit_id == "qualification-routing" else None
            terminals.append(factory.terminal(unit.unit_id, [factory.make_attestation(unit.unit_id, report=report)]))
        holdout, = [judge_fixed_holdouts(
            spec=factory.spec,
            terminals=[item for item in terminals if item.record["stage"] == "holdout"],
            mappings=factory.mappings,
        )]
        with self.assertRaisesRegex(VerifyError, "behavior"):
            verify_evaluation(spec=factory.spec, terminals=terminals, holdout_result=holdout)

    def test_exact_final_starts_strictly_after_all_prior_terminals(self):
        factory = RecordFactory(); terminals = []
        for unit in UNIT_TOPOLOGY:
            options = ({"started_at": "2026-08-08T00:00:04Z", "finished_at": "2026-08-08T00:00:07Z"}
                       if unit.unit_id == "exact-final" else {})
            terminals.append(factory.terminal(unit.unit_id, [factory.make_attestation(unit.unit_id, **options)]))
        holdout = judge_fixed_holdouts(
            spec=factory.spec,
            terminals=[item for item in terminals if item.record["stage"] == "holdout"],
            mappings=factory.mappings,
        )
        with self.assertRaisesRegex(VerifyError, "before prior"):
            verify_evaluation(spec=factory.spec, terminals=terminals, holdout_result=holdout)

    def test_absolute_cap_includes_recovered_wall(self):
        factory = RecordFactory(absolute_wall=1000); terminals = []
        for unit in UNIT_TOPOLOGY:
            if unit.unit_id == "qualification-routing":
                first = factory.make_attestation(
                    unit.unit_id, outcome="not_landed", wall=50,
                    started_at="2026-08-08T00:00:00Z", finished_at="2026-08-08T00:00:01Z",
                )
                second = factory.make_attestation(
                    unit.unit_id, attempt=1, prior=[first], wall=80,
                    started_at="2026-08-08T00:00:01Z", finished_at="2026-08-08T00:00:02Z",
                )
                terminals.append(factory.terminal(unit.unit_id, [first, second]))
            else:
                record = factory.make_attestation(unit.unit_id, wall=80)
                terminals.append(factory.terminal(unit.unit_id, [record]))
        result = judge_fixed_holdouts(
            spec=factory.spec,
            terminals=[item for item in terminals if item.record["stage"] == "holdout"],
            mappings=factory.mappings,
        )
        with self.assertRaisesRegex(VerifyError, "absolute cumulative"):
            verify_evaluation(spec=factory.spec, terminals=terminals, holdout_result=result)

    def test_malformed_incomplete_not_yet_and_unknown_coverage_are_landed_adverse(self):
        reports = [{}, {"neutral": True}, RecordFactory().not_yet_report()]
        proxy_only_go = RecordFactory().go_report()
        proxy_only_go["coverage"] = {
            "complete": True,
            "unverified": ["native FE typecheck unavailable; regex proxy only"],
        }
        reports.append(proxy_only_go)
        unknown = RecordFactory().go_report()
        unknown["coverage"] = {"complete": False, "unverified": ["required check"]}
        unknown["decision"] = "NOT_YET"
        reports.append(unknown)
        for report in reports:
            factory = RecordFactory()
            record = factory.make_attestation("exact-final", report=report)
            terminal = factory.terminal("exact-final", [record])
            self.assertEqual(terminal.record["effect_outcome"], "landed")
            self.assertFalse(terminal.record["assessment"]["passed"])
            with self.assertRaises(FakeBoundaryError):
                factory.make_attestation("exact-final", attempt=1, prior=[record], report=factory.go_report())

    def test_style_or_optimization_cannot_be_typed_as_a_blocker(self):
        factory = RecordFactory()
        for classification in ("style", "optimization"):
            report = factory.not_yet_report()
            report["findings"][0]["classification"] = classification
            assessment = assess_provider_report(
                report, stage="exact_final", response_schema=factory.exact_schema,
                oracle=None, provider_input=factory.inputs["exact-final"],
            )
            self.assertEqual(assessment["fatal"], ["malformed_report"])

    def test_exact_final_finding_shape_and_one_shot_recovery_stay_fixed(self):
        factory = RecordFactory()
        finding = factory.exact_schema["properties"]["findings"]["items"]
        self.assertEqual(
            set(finding["properties"]),
            {"classification", "reproduction", "evidence", "materiality", "candidate_new", "summary"},
        )
        self.assertFalse(finding["additionalProperties"])
        first = factory.make_attestation("exact-final", outcome="unknown")
        with self.assertRaises(FakeBoundaryError):
            factory.make_attestation(
                "exact-final", attempt=1, prior=[first], report=factory.go_report(),
            )


class ReleaseTests(unittest.TestCase):
    def test_valid_release_uses_separate_authority_and_exact_readback(self):
        factory = RecordFactory(); _, _, evaluation = factory.full_evaluation()
        receipt, verified = factory.release(evaluation)
        self.assertEqual(verified.receipt, receipt)
        self.assertNotIn(
            receipt["release_authority_identity"],
            evaluation.result["evaluation_authority_identities"],
        )

    def test_signed_destination_product_target_rollback_projection_and_readback_drift_fail(self):
        mutations = (
            lambda value: value["observation"].__setitem__("observed_destination", "wrong"),
            lambda value: value.__setitem__("product_artifact_sha256", sha("wrong-product")),
            lambda value: value.__setitem__("target_identity", "wrong-target"),
            lambda value: value.__setitem__("rollback_identity", "wrong-rollback"),
            lambda value: value.__setitem__("installed_projection", deepcopy(RecordFactory().previous_product["projections"]["plugin_runtime"])),
        )
        for mutate in mutations:
            factory = RecordFactory(); _, _, evaluation = factory.full_evaluation()
            with self.assertRaises((RecordError, VerifyError)):
                factory.release(evaluation, mutate_statement=mutate)

    def test_forged_authenticator_and_release_authority_fail(self):
        factory = RecordFactory(); _, _, evaluation = factory.full_evaluation()
        receipt, _ = factory.release(evaluation)
        forged = reseal(
            receipt, lambda value: value["evidence_binding"].__setitem__("signature", "forged"),
        )
        with self.assertRaises(VerifyError):
            verify_release(
                forged, evaluation=evaluation, product=factory.product, spec=factory.spec,
                authenticator=factory.boundary,
                release_authority={
                    "authority_identity": receipt["release_authority_identity"],
                    "request_sha256": receipt["release_authority_request_sha256"],
                    "signature": "forged", "authority_sha256": receipt["release_authority_sha256"],
                }, authority_validator=factory.boundary,
            )

    def test_not_landed_and_unknown_release_never_verify(self):
        for outcome in ("not_landed", "unknown"):
            factory = RecordFactory(); _, _, evaluation = factory.full_evaluation()
            with self.assertRaises(VerifyError):
                factory.release(evaluation, outcome=outcome)


if __name__ == "__main__":
    unittest.main()
