from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from evaluation import run_corpus
from evaluation import run_holdouts as holdouts


def metadata(*, passed: bool, uncached: int, output: int, elapsed: float) -> dict:
    return {
        "case": "hidden-pair",
        "arm": "identity-must-be-stripped",
        "package_manifest_sha256": "a" * 64,
        "passed": passed,
        "timed_out": False,
        "exit_code": 0,
        "oracle_failures": [] if passed else ["hidden mismatch"],
        "uncached_input_tokens": uncached,
        "usage": {"output_tokens": output},
        "elapsed_seconds": elapsed,
    }


class HappyCodexHoldoutTests(unittest.TestCase):
    def test_manifest_has_distinct_hidden_pairs_and_required_coverage(self) -> None:
        manifest = holdouts.load_manifest()
        pairs = manifest["pairs"]
        self.assertEqual(len(pairs), 3)
        self.assertEqual(len({pair["id"] for pair in pairs}), 3)
        self.assertEqual(len({pair["case"]["id"] for pair in pairs}), 3)
        self.assertTrue(any(pair["outside_diff_boundary"] for pair in pairs[:2]))
        self.assertTrue(
            any(
                pair["oracle_kind"] in {"mechanical", "behavioral"}
                for pair in pairs[:2]
            )
        )
        corpus_ids = set(run_corpus.load_cases())
        for pair in pairs:
            self.assertNotIn(pair["case"]["id"], corpus_ids)
            run_corpus.validate_case(pair["case"], pair["case_path"])

    def test_blind_view_strips_every_identity_field(self) -> None:
        view = holdouts.blind_view(
            metadata(passed=True, uncached=40, output=10, elapsed=3.5)
        )
        self.assertEqual(
            set(view),
            {
                "passed",
                "timed_out",
                "exit_code",
                "oracle_failures_count",
                "uncached_input_tokens",
                "output_tokens",
                "elapsed_seconds",
            },
        )
        rendered = repr(view)
        self.assertNotIn("identity-must-be-stripped", rendered)
        self.assertNotIn("package_manifest", rendered)
        self.assertNotIn("hidden-pair", rendered)

    def test_blind_decision_rejects_identity_contamination(self) -> None:
        views = {
            "arm-a": holdouts.blind_view(
                metadata(passed=True, uncached=40, output=10, elapsed=3.5)
            ),
            "arm-b": holdouts.blind_view(
                metadata(passed=False, uncached=45, output=10, elapsed=4.0)
            ),
        }
        contaminated = copy.deepcopy(views)
        contaminated["arm-a"]["arm"] = "candidate"
        with self.assertRaisesRegex(ValueError, "blind receipt fields"):
            holdouts.freeze_blind_decision(contaminated)
        decision = holdouts.freeze_blind_decision(views)
        self.assertEqual(
            {item["quality"] for item in decision["aliases"]}, {"pass", "fail"}
        )

    def test_reveal_is_committed_and_chained_after_blind_decision(self) -> None:
        sealed = holdouts.seal_mapping(
            "pair-one", candidate_alias="arm-b", nonce="n" * 32
        )
        views = {
            "arm-a": holdouts.blind_view(
                metadata(passed=False, uncached=45, output=10, elapsed=4.0)
            ),
            "arm-b": holdouts.blind_view(
                metadata(passed=True, uncached=40, output=10, elapsed=3.5)
            ),
        }
        decision = holdouts.freeze_blind_decision(views)
        reveal = holdouts.reveal_mapping(
            sealed, pre_reveal_decision_sha256=holdouts.canonical_sha256(decision)
        )
        holdouts.validate_reveal(reveal, decision)
        self.assertEqual(reveal["mapping"]["candidate"], "arm-b")
        self.assertEqual(holdouts.compare_pair(decision, reveal), "better")
        tampered = copy.deepcopy(reveal)
        tampered["mapping"]["candidate"] = "arm-a"
        with self.assertRaisesRegex(ValueError, "mapping commitment"):
            holdouts.validate_reveal(tampered, decision)

    def test_candidate_failure_is_always_a_pair_regression(self) -> None:
        expected = {
            (True, True): "equal",
            (True, False): "better",
            (False, True): "regression",
            (False, False): "regression",
        }
        for (candidate_passed, public_passed), outcome in expected.items():
            with self.subTest(
                candidate=candidate_passed,
                public=public_passed,
            ):
                sealed = holdouts.seal_mapping(
                    "pair-matrix", candidate_alias="arm-a", nonce="n" * 32
                )
                views = {
                    "arm-a": holdouts.blind_view(
                        metadata(
                            passed=candidate_passed,
                            uncached=40,
                            output=10,
                            elapsed=3.5,
                        )
                    ),
                    "arm-b": holdouts.blind_view(
                        metadata(
                            passed=public_passed,
                            uncached=40,
                            output=10,
                            elapsed=3.5,
                        )
                    ),
                }
                decision = holdouts.freeze_blind_decision(views)
                reveal = holdouts.reveal_mapping(
                    sealed,
                    pre_reveal_decision_sha256=holdouts.canonical_sha256(decision),
                )
                self.assertEqual(holdouts.compare_pair(decision, reveal), outcome)

    def test_any_reachable_candidate_regression_rejects_release(self) -> None:
        metrics = {
            "uncached_input_tokens": 10,
            "output_tokens": 2,
            "elapsed_seconds": 1.0,
        }
        histories = [
            ["regression"],
            ["better", "regression"],
            ["equal", "regression"],
            ["better", "equal", "regression"],
            ["equal", "better", "regression"],
        ]
        for history in histories:
            with self.subTest(history=history):
                self.assertEqual(holdouts.adaptive_next(history), "reject")
                quality = holdouts.aggregate_quality(history)
                self.assertEqual(quality, "regression")
                self.assertFalse(
                    holdouts.cost_gate(metrics, metrics, quality=quality)[
                        "release_permitted"
                    ]
                )

    def test_pair_runner_persists_commitment_before_runs_and_reveal_after(self) -> None:
        pair = holdouts.load_manifest()["pairs"][0]
        observations: list[tuple[bool, bool, bool]] = []

        def fake_evaluator(
            case: dict,
            *,
            plugin: Path,
            output: Path,
            model: str,
            effort: str,
            timeout: int,
            arm: str,
        ) -> dict:
            del plugin, model, effort, timeout
            pair_output = output.parents[1]
            observations.append(
                (
                    (pair_output / "01-mapping-commitment.json").is_file(),
                    (pair_output / "02-pre-reveal-decision.json").exists(),
                    (pair_output / "03-mapping-reveal.json").exists(),
                )
            )
            result = metadata(
                passed=arm == "candidate", uncached=40, output=10, elapsed=3.5
            )
            result["case"] = case["id"]
            result["arm"] = arm
            result["oracle_failures"] = [] if result["passed"] else ["mismatch"]
            metadata_path = output / case["id"] / "metadata.json"
            metadata_path.parent.mkdir(parents=True)
            metadata_path.write_text(json.dumps(result), encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            receipt = holdouts.run_pair(
                pair,
                candidate=root / "candidate",
                public=root / "public",
                output=root / "results",
                model="test-model",
                effort="high",
                timeout=10,
                evaluator=fake_evaluator,
            )
            pair_output = root / "results" / pair["id"]
            self.assertEqual(observations, [(True, False, False), (True, False, False)])
            self.assertEqual(receipt["outcome"], "better")
            self.assertTrue((pair_output / "02-pre-reveal-decision.json").is_file())
            self.assertTrue((pair_output / "03-mapping-reveal.json").is_file())
            self.assertTrue((pair_output / "04-pair-receipt.json").is_file())

    def test_live_run_rejects_unpinned_public_package_before_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            candidate = root / "candidate"
            public = root / "not-public-0.2"
            output = root / "results"
            candidate.mkdir()
            public.mkdir()
            output.mkdir()
            with (
                mock.patch.object(
                    holdouts.run_corpus,
                    "package_manifest_sha256",
                    side_effect=["c" * 64, "b" * 64],
                ),
                mock.patch.object(
                    holdouts,
                    "run_pair",
                    side_effect=AssertionError(
                        "holdout execution started before public baseline binding"
                    ),
                ) as run_pair,
            ):
                with self.assertRaisesRegex(
                    ValueError, "public-0.2 package manifest mismatch"
                ):
                    holdouts.run_holdouts(
                        candidate=candidate,
                        public=public,
                        output=output,
                        model="test-model",
                        effort="high",
                        timeout=10,
                    )
            run_pair.assert_not_called()
            self.assertEqual(list(output.iterdir()), [])

    def test_adaptive_sequence_rejects_first_regression_and_requires_second(
        self,
    ) -> None:
        self.assertEqual(holdouts.adaptive_next([]), "run_first")
        self.assertEqual(holdouts.adaptive_next(["regression"]), "reject")
        self.assertEqual(holdouts.adaptive_next(["equal"]), "run_second")
        self.assertEqual(holdouts.adaptive_next(["better"]), "run_second")
        self.assertEqual(holdouts.adaptive_next(["equal", "equal"]), "stop")
        self.assertEqual(holdouts.adaptive_next(["better", "equal"]), "run_third")
        self.assertEqual(holdouts.adaptive_next(["equal", "uncertain"]), "run_third")
        self.assertEqual(
            holdouts.adaptive_next(["equal", "uncertain", "equal"]), "stop"
        )
        self.assertEqual(
            holdouts.aggregate_quality(["equal", "uncertain", "equal"]), "equal"
        )
        self.assertEqual(
            holdouts.aggregate_quality(["better", "equal", "better"]),
            "materially_better",
        )
        self.assertEqual(
            holdouts.aggregate_quality(["better", "equal", "equal"]), "equal"
        )
        self.assertEqual(
            holdouts.aggregate_quality(["better", "uncertain", "equal"]),
            "inconclusive",
        )
        self.assertEqual(
            holdouts.aggregate_quality(["uncertain", "uncertain", "equal"]),
            "inconclusive",
        )

    def test_cost_gate_uses_combined_tokens_and_wall_as_only_ratios(self) -> None:
        public = {
            "uncached_input_tokens": 90,
            "output_tokens": 10,
            "elapsed_seconds": 10.0,
        }
        equal_total_different_components = {
            "uncached_input_tokens": 80,
            "output_tokens": 20,
            "elapsed_seconds": 10.0,
        }
        gate = holdouts.cost_gate(
            equal_total_different_components, public, quality="equal"
        )
        self.assertEqual(gate["decision"], "pass")
        self.assertEqual(gate["blocking_ratios"], {"combined_tokens": 1.0, "wall": 1.0})
        self.assertEqual(gate["diagnostic_ratios"]["output_tokens"], 2.0)

        expensive = {
            "uncached_input_tokens": 120,
            "output_tokens": 10,
            "elapsed_seconds": 12.6,
        }
        gate = holdouts.cost_gate(expensive, public, quality="equal")
        self.assertEqual(gate["decision"], "simplify_and_retest")
        self.assertFalse(gate["release_permitted"])
        self.assertGreater(gate["blocking_ratios"]["combined_tokens"], 1.25)
        self.assertGreater(gate["blocking_ratios"]["wall"], 1.25)

    def test_better_but_expensive_requires_user_confirmation(self) -> None:
        candidate = {
            "uncached_input_tokens": 120,
            "output_tokens": 10,
            "elapsed_seconds": 11.0,
        }
        public = {
            "uncached_input_tokens": 90,
            "output_tokens": 10,
            "elapsed_seconds": 10.0,
        }
        gate = holdouts.cost_gate(candidate, public, quality="materially_better")
        self.assertEqual(gate["decision"], "user_confirmation_required")
        self.assertFalse(gate["release_permitted"])

    def test_zero_public_cost_serializes_as_strict_json_and_blocks(self) -> None:
        candidate = {
            "uncached_input_tokens": 1,
            "output_tokens": 0,
            "elapsed_seconds": 1.0,
        }
        public = {
            "uncached_input_tokens": 0,
            "output_tokens": 0,
            "elapsed_seconds": 0.0,
        }
        gate = holdouts.cost_gate(candidate, public, quality="equal")
        self.assertEqual(
            gate["blocking_ratios"],
            {"combined_tokens": "infinity", "wall": "infinity"},
        )
        self.assertEqual(gate["decision"], "simplify_and_retest")
        json.dumps(gate, allow_nan=False)

    def test_regression_or_persistent_uncertainty_never_releases(self) -> None:
        metrics = {
            "uncached_input_tokens": 10,
            "output_tokens": 2,
            "elapsed_seconds": 1.0,
        }
        for quality in ("regression", "inconclusive"):
            with self.subTest(quality=quality):
                gate = holdouts.cost_gate(metrics, metrics, quality=quality)
                self.assertEqual(gate["decision"], "reject")
                self.assertFalse(gate["release_permitted"])


if __name__ == "__main__":
    unittest.main()
