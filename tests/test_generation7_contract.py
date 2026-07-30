from __future__ import annotations

from dataclasses import FrozenInstanceError
import copy
import hashlib
from pathlib import Path
import unittest


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def path_anchor(value: str = "Src/App.py") -> dict[str, str]:
    return {"kind": "path", "repository": "fixture", "value": value}


def finding(
    *,
    finding_id: str = "hc7.case.fact-001",
    status: str = "resolved",
    blocker: dict[str, str] | None = None,
) -> dict[str, object]:
    return {
        "id": finding_id,
        "domain": "other",
        "status": status,
        "anchors": [path_anchor()],
        "blocker": blocker,
    }


def machine_facts() -> dict[str, object]:
    return {
        "schema_generation": 7,
        "task_binding": {
            "task_id": "case:test",
            "root_task_id": "root:test",
            "executor_task_id": "executor:test",
            "owner_label": "happycodex-evaluator",
            "destination_id": "repository:fixture",
            "lineage_digest": digest("lineage"),
            "role_config_digest": digest("role"),
            "repository_digest": digest("repository"),
            "outcome_digest": digest("outcome"),
            "invocation_profile_digest": digest("profile"),
        },
        "accepted_baseline_failures": [],
        "infrastructure_generation": digest("infra-0"),
    }


def observation() -> dict[str, object]:
    return {
        "qualifies": True,
        "execplan_condition": "usable",
        "findings": [finding()],
        "open_gates": ["product_edit"],
        "evidence": ["tests passed"],
        "reason": "implementation is the next bounded action",
        "recovery": None,
    }


class Generation7SemanticContractTests(unittest.TestCase):
    def test_public_surface_is_closed_to_twenty_exports(self) -> None:
        import evaluation.semantic as semantic

        self.assertEqual(
            semantic.__all__,
            (
                "SemanticError",
                "MachineFacts",
                "ModelObservation",
                "Finding",
                "ControlBlocker",
                "NextAction",
                "CanonicalReport",
                "CorpusCase",
                "parse_machine_facts",
                "parse_model_observation",
                "parse_corpus_case",
                "parse_report",
                "corpus_case_to_raw",
                "report_to_raw",
                "canonical_bytes",
                "semantic_digest",
                "reduce",
                "build_report",
                "validate_report",
                "replay",
            ),
        )

    def test_semantic_package_is_exactly_five_files(self) -> None:
        import evaluation.semantic as semantic

        root = Path(semantic.__file__).parent
        self.assertEqual(
            sorted(path.name for path in root.glob("*.py")),
            ["__init__.py", "codec.py", "model.py", "reducer.py", "replay.py"],
        )

    def test_generation_six_alias_and_unknown_fields_fail_closed(self) -> None:
        from evaluation.semantic import SemanticError, parse_machine_facts

        for mutate in (
            lambda raw: raw.__setitem__("schema_generation", 6),
            lambda raw: raw.__setitem__("admin", {}),
            lambda raw: raw["task_binding"].__setitem__("authority", "prose"),
        ):
            raw = machine_facts()
            mutate(raw)
            with self.subTest(raw=raw), self.assertRaises(SemanticError):
                parse_machine_facts(raw)

    def test_parsed_facts_are_deeply_immutable(self) -> None:
        from evaluation.semantic import parse_machine_facts

        facts = parse_machine_facts(machine_facts())
        with self.assertRaises(FrozenInstanceError):
            facts.infrastructure_generation = digest("forged")
        with self.assertRaises(TypeError):
            facts.task_binding["task_id"] = "other"
        self.assertIsInstance(facts.accepted_baseline_failures, tuple)

    def test_blocker_is_embedded_and_resolved_cannot_carry_it(self) -> None:
        from evaluation.semantic import SemanticError, parse_model_observation

        raw = observation()
        raw["blocker_classifications"] = []
        with self.assertRaises(SemanticError):
            parse_model_observation(raw)
        raw = observation()
        raw["findings"][0]["blocker"] = {
            "class": "original_goal",
            "reason": "contradiction",
        }
        with self.assertRaises(SemanticError):
            parse_model_observation(raw)

    def test_path_anchors_are_typed_case_sensitive_and_unaliased(self) -> None:
        from evaluation.semantic import (
            SemanticError,
            parse_model_observation,
        )

        left = observation()
        right = observation()
        right["findings"][0]["anchors"][0]["value"] = "src/app.py"
        self.assertNotEqual(
            parse_model_observation(left),
            parse_model_observation(right),
        )
        alias = observation()
        alias["findings"][0]["anchors"][0] = {
            "kind": "path",
            "repository": "other",
            "value": "App.py",
            "basename_alias": "App.py",
        }
        with self.assertRaises(SemanticError):
            parse_model_observation(alias)

    def test_display_rewording_does_not_change_state_or_action(self) -> None:
        from evaluation.semantic import (
            build_report,
            parse_machine_facts,
            parse_model_observation,
        )

        facts = parse_machine_facts(machine_facts())
        left = build_report(facts, parse_model_observation(observation()))
        raw = observation()
        raw["reason"] = "different display wording"
        raw["evidence"] = ["same source described differently"]
        right = build_report(facts, parse_model_observation(raw))
        self.assertEqual(left.state_key, right.state_key)
        self.assertEqual(left.action_key, right.action_key)
        self.assertNotEqual(left.observation, right.observation)

    def test_semantic_dimensions_change_state_key(self) -> None:
        from evaluation.semantic import (
            build_report,
            parse_machine_facts,
            parse_model_observation,
        )

        base_raw = machine_facts()
        observation_raw = observation()
        base = build_report(
            parse_machine_facts(base_raw),
            parse_model_observation(observation_raw),
        )
        variants: list[tuple[dict[str, object], dict[str, object]]] = []
        changed = copy.deepcopy(base_raw)
        changed["task_binding"]["outcome_digest"] = digest("other-outcome")
        variants.append((changed, observation_raw))
        changed = copy.deepcopy(base_raw)
        changed["infrastructure_generation"] = digest("infra-1")
        variants.append((changed, observation_raw))
        changed_observation = copy.deepcopy(observation_raw)
        changed_observation["findings"][0]["anchors"][0]["value"] = "Src/Other.py"
        variants.append((base_raw, changed_observation))
        changed_observation = copy.deepcopy(observation_raw)
        changed_observation["open_gates"] = ["checks"]
        variants.append((base_raw, changed_observation))
        for raw_facts, raw_observation in variants:
            with self.subTest(
                facts=raw_facts,
                observation=raw_observation,
            ):
                report = build_report(
                    parse_machine_facts(raw_facts),
                    parse_model_observation(raw_observation),
                )
                self.assertNotEqual(base.state_key, report.state_key)

    def test_action_key_is_only_from_reducer_produced_action(self) -> None:
        from evaluation.semantic import (
            build_report,
            parse_machine_facts,
            parse_model_observation,
            semantic_digest,
        )

        report = build_report(
            parse_machine_facts(machine_facts()),
            parse_model_observation(observation()),
        )
        self.assertEqual(
            report.action_key,
            semantic_digest(
                "action-key",
                {
                    "state_key": report.state_key,
                    "next_action": report.next_action,
                },
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            report.action_key = digest("forged")

    def test_disposition_is_one_unambiguous_union(self) -> None:
        from evaluation.semantic import (
            build_report,
            parse_machine_facts,
            parse_model_observation,
        )

        facts = parse_machine_facts(machine_facts())
        scenarios = (
            (["product_edit"], "usable", "IMPLEMENT"),
            (["checks"], "usable", "CHECK"),
            (["candidate_freeze"], "usable", "FREEZE"),
            (["exact_final_review"], "usable", "EXACT_FINAL"),
            (["release"], "usable", "RELEASE"),
            (["user_selection"], "usable", "ASK_USER"),
            (["reconciliation"], "usable", "RECONCILE"),
            (["product_edit"], "needs_amendment", "RECONCILE"),
            ([], "usable", "CLOSE"),
        )
        for gates, execplan, expected in scenarios:
            raw = observation()
            raw["open_gates"] = gates
            raw["execplan_condition"] = execplan
            report = build_report(facts, parse_model_observation(raw))
            with self.subTest(gates=gates, execplan=execplan):
                self.assertEqual(report.next_action.kind, expected)

    def test_unresolved_finding_derives_exact_blocker_and_repair(self) -> None:
        from evaluation.semantic import (
            build_report,
            parse_machine_facts,
            parse_model_observation,
        )

        raw = observation()
        raw["findings"][0] = finding(
            status="unknown",
            blocker={
                "class": "safety_data_integrity",
                "reason": "candidate bytes are uncertain",
            },
        )
        raw["open_gates"] = ["candidate_freeze"]
        report = build_report(
            parse_machine_facts(machine_facts()),
            parse_model_observation(raw),
        )
        self.assertEqual(len(report.blockers), 1)
        self.assertEqual(report.blockers[0].finding_id, "hc7.case.fact-001")
        self.assertEqual(report.next_action.kind, "IMPLEMENT")

    def test_report_roundtrip_recomputes_every_derived_field(self) -> None:
        from evaluation.semantic import (
            SemanticError,
            build_report,
            parse_machine_facts,
            parse_model_observation,
            parse_report,
            report_to_raw,
        )

        report = build_report(
            parse_machine_facts(machine_facts()),
            parse_model_observation(observation()),
        )
        raw = report_to_raw(report)
        self.assertEqual(parse_report(raw), report)
        raw["action_key"] = digest("forged")
        with self.assertRaises(SemanticError):
            parse_report(raw)

    def test_receipt_chain_owns_order_not_progress(self) -> None:
        from evaluation.semantic import (
            SemanticError,
            build_report,
            parse_machine_facts,
            parse_model_observation,
            replay,
            report_to_raw,
            semantic_digest,
        )

        report = build_report(
            parse_machine_facts(machine_facts()),
            parse_model_observation(observation()),
        )
        first = {
            "sequence": 0,
            "previous_hash": None,
            "report": report_to_raw(report),
            "consumed_action": False,
        }
        second = {
            "sequence": 1,
            "previous_hash": semantic_digest("receipt-link", first),
            "report": report_to_raw(report),
            "consumed_action": True,
        }
        self.assertEqual(replay([first, second]), (report, report))
        second["previous_hash"] = digest("wrong")
        with self.assertRaises(SemanticError):
            replay([first, second])

    def test_builtin_subclasses_and_mutable_values_fail_closed(self) -> None:
        from evaluation.semantic import SemanticError, canonical_bytes

        class StringSubclass(str):
            pass

        class DictSubclass(dict):
            pass

        for value in (
            StringSubclass("x"),
            DictSubclass({"x": 1}),
            {"x": {1, 2}},
        ):
            with self.subTest(value=value), self.assertRaises(SemanticError):
                canonical_bytes(value)


if __name__ == "__main__":
    unittest.main()
