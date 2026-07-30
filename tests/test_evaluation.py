from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from evaluation.core import ledger as ledger_engine
from evaluation.core import receipt as receipt_engine
from evaluation.corpus import engine as runner


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "evaluation" / "corpus" / "engine.py"
RECOVERY_MANIFEST_MARKER = "RECOVERY-MANIFEST-SHA256:" + "a" * 64


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def product_entries(repo: Path, revision: str, excluded: str) -> list[str]:
    output = git(repo, "ls-tree", "-r", revision)
    return sorted(
        line for line in output.splitlines() if not line.endswith(f"\t{excluded}")
    )




def validate_recovery_manifest(native: dict[str, object], case_id: str) -> None:
    path = ROOT / "evaluation" / "cases" / "pre-freeze-compaction.json"
    case = json.loads(path.read_text(encoding="utf-8"))
    case["fixture"]["native_compaction_resume"] = native
    runner.validate_case(case, Path(f"{case_id}.json"))

class HappyCodexEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = runner.load_cases()

    @staticmethod
    def _marker(value: str) -> dict[str, str]:
        return {"kind": "marker", "value": value}

    @staticmethod
    def _path(value: str) -> dict[str, str]:
        return {"kind": "path", "repository": "fixture", "value": value}

    @staticmethod
    def _digest(value: str, label: str = "git-oid") -> dict[str, str]:
        return {"kind": "digest", "label": label, "value": value}

    @classmethod
    def _finding(
        cls,
        finding_id: str,
        anchor: dict[str, str] | None = None,
        *,
        domain: str = "other",
        status: str = "resolved",
        blocker: str | None = None,
        reason: str = "bounded semantic blocker",
    ) -> dict[str, object]:
        if blocker is None and status in {
            "baseline_unchanged",
            "candidate_new",
            "unknown",
        }:
            blocker = "original_goal"
        return {
            "id": finding_id,
            "domain": domain,
            "status": status,
            "anchors": [anchor or cls._marker(finding_id)],
            "blocker": (
                None if blocker is None else {"class": blocker, "reason": reason}
            ),
        }

    @classmethod
    def _observation(
        cls,
        *,
        findings: list[dict[str, object]] | None = None,
        gate: str | None = None,
        qualifies: bool = True,
        execplan: str = "usable",
        recovery: dict[str, object] | None = None,
        reason: str = "bounded observation",
    ) -> dict[str, object]:
        return {
            "qualifies": qualifies,
            "execplan_condition": execplan,
            "findings": findings or [],
            "open_gates": [] if gate is None else [gate],
            "evidence": ["fixture evidence"],
            "reason": reason,
            "recovery": recovery,
        }

    @staticmethod
    def _context(
        *,
        task_id: str = "case:test:candidate",
        accepted: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "task_id": task_id,
            "root_task_id": "root:evaluator",
            "executor_task_id": "executor:evaluator",
            "owner_label": "happycodex-evaluator",
            "destination_id": "repository:fixture",
            "lineage_digest": "1" * 64,
            "role_config_digest": "2" * 64,
            "repository_digest": "3" * 64,
            "outcome_digest": "4" * 64,
            "invocation_profile": runner.invocation_profile(
                model="gpt-5.6-sol",
                effort="high",
                timeout_seconds=300,
                arm="candidate",
            ),
            "accepted_baseline_failures": sorted(accepted or []),
        }

    @classmethod
    def _report(
        cls,
        observation: dict[str, object],
        *,
        task_id: str = "case:test:candidate",
        accepted: list[str] | None = None,
    ) -> dict[str, object]:
        return runner.canonical_report_from_result(
            observation,
            context=cls._context(task_id=task_id, accepted=accepted),
        )

    @staticmethod
    def _anchor_key(anchor: dict[str, str]) -> str:
        return runner.canonical_sha256(anchor)

    @classmethod
    def _case_report(cls, case: dict[str, object]) -> dict[str, object]:
        oracle = case["oracle"]
        findings: list[dict[str, object]] = []
        anchored_blockers = list(oracle.get("required_anchored_blockers", []))
        consumed_blockers: set[int] = set()

        for index, required in enumerate(oracle.get("required_findings", [])):
            findings.append(
                cls._finding(
                    required["id"],
                    cls._marker(f"required-{index}"),
                    domain=required["domain"],
                    status=required["statuses"][0],
                )
            )
        for index, required in enumerate(oracle.get("required_blockers", [])):
            findings.append(
                cls._finding(
                    required["id"],
                    cls._marker(f"blocker-{index}"),
                    status="unknown",
                    blocker=required["classes"][0],
                )
            )
        for index, required in enumerate(
            oracle.get("required_anchored_findings", [])
        ):
            blocker = None
            if required["statuses"][0] != "resolved":
                for blocker_index, candidate in enumerate(anchored_blockers):
                    if (
                        blocker_index not in consumed_blockers
                        and cls._anchor_key(candidate["anchor"])
                        == cls._anchor_key(required["anchor"])
                    ):
                        blocker = candidate["classes"][0]
                        consumed_blockers.add(blocker_index)
                        break
            findings.append(
                cls._finding(
                    f"anchored-finding-{index}",
                    required["anchor"],
                    domain=required["domain"],
                    status=required["statuses"][0],
                    blocker=blocker,
                )
            )
        for index, required in enumerate(anchored_blockers):
            if index in consumed_blockers:
                continue
            findings.append(
                cls._finding(
                    f"anchored-blocker-{index}",
                    required["anchor"],
                    status="unknown",
                    blocker=required["classes"][0],
                )
            )
        for index, blocker_class in enumerate(
            oracle.get("required_blocker_classes", [])
        ):
            findings.append(
                cls._finding(
                    f"class-blocker-{index}",
                    cls._marker(f"class-{index}"),
                    status="unknown",
                    blocker=blocker_class,
                )
            )
        action_gate = {
            "ASK_USER": "user_selection",
            "RECONCILE": "reconciliation",
            "IMPLEMENT": "product_edit",
            "CHECK": "checks",
            "FREEZE": "contract_freeze",
            "EXACT_FINAL": "exact_final_review",
            "RELEASE": "release",
            "CLOSE": None,
        }
        action = oracle["expected_action"]
        observation = cls._observation(
            findings=findings,
            gate=action_gate[action],
            qualifies=oracle["required_observation"]["qualifies"],
            execplan=oracle["required_observation"]["execplan_conditions"][0],
        )
        return cls._report(
            observation,
            task_id=f"case:{case['id']}:candidate",
            accepted=oracle.get("accepted_baseline_failures", []),
        )

    @classmethod
    def _recovery(cls) -> dict[str, object]:
        marker = "RECOVERY-MANIFEST-SHA256:" + "a" * 64
        return {
            "baseline_revision": "1" * 40,
            "baseline_tree": "2" * 40,
            "current_revision": "3" * 40,
            "current_tree": "4" * 40,
            "writer": "Root",
            "milestone_phase": "working",
            "next_action": "run_checks",
            "pending_gates": ["checks"],
            "tests": {
                "passed": 1,
                "failed": 0,
                "accepted_failures": 0,
                "marker_ids": [marker],
            },
            "worktree": "clean",
            "live_agents": [],
            "marker_ids": [marker],
        }

    def test_batch1_direct_protocol_rejects_derived_and_contradictory_state(
        self,
    ) -> None:
        from evaluation.semantic import SemanticError, parse_model_observation

        raw = self._observation(gate=None)
        report = self._report(raw)
        self.assertEqual(report["schema_generation"], 7)
        self.assertEqual(report["next_action"]["kind"], "CLOSE")
        self.assertNotIn("decision", report["observation"])
        derived = copy.deepcopy(raw)
        derived["next_action"] = "close"
        with self.assertRaises(SemanticError):
            parse_model_observation(derived)
        contradictory = self._observation(
            findings=[
                self._finding(
                    "resolved",
                    status="resolved",
                    blocker="safety_data_integrity",
                )
            ]
        )
        with self.assertRaisesRegex(SemanticError, "resolved"):
            parse_model_observation(contradictory)
        duplicate = self._observation(
            findings=[
                self._finding("duplicate", status="unknown"),
                self._finding("duplicate", status="unknown"),
            ]
        )
        with self.assertRaisesRegex(SemanticError, "duplicate"):
            parse_model_observation(duplicate)

    def test_corpus_is_complete_and_bidirectional(self) -> None:
        covered = {tag for case in self.cases.values() for tag in case["covers"]}
        self.assertEqual(covered, runner.REQUIRED_TAGS)
        self.assertEqual(len(self.cases), 17)
        goal = self.cases["goal-divergence"]
        required = goal["oracle"]["required_anchored_blockers"]
        self.assertIn(
            {
                "anchor": self._path("GOAL.md"),
                "classes": ["frozen_acceptance", "original_goal"],
            },
            required,
        )
        for case in self.cases.values():
            self.assertEqual(
                runner.match_oracle(
                    self._case_report(case),
                    case["oracle"],
                    fixture=case["fixture"],
                ),
                [],
                case["id"],
            )

    def test_unavailable_active_goal_requires_explicit_pause_handoff(self) -> None:
        case = self.cases["goal-divergence"]
        report = self._case_report(case)
        self.assertEqual(report["next_action"]["kind"], "ASK_USER")
        self.assertEqual(report["observation"]["open_gates"], ["user_selection"])
        self.assertEqual(
            runner.match_oracle(report, case["oracle"], fixture=case["fixture"]),
            [],
        )
        reconciled = self._report(
            self._observation(gate="reconciliation"),
            task_id="case:goal-divergence:counterexample",
        )
        self.assertTrue(
            runner.match_oracle(
                reconciled,
                case["oracle"],
                fixture=case["fixture"],
            )
        )

    def test_goal_pause_handoff_uses_final_visible_goal_state(self) -> None:
        active = "Status: active\nAgent-side Goal pause action: unavailable\n"
        paused = "Status: paused\nAgent-side Goal pause action: unavailable\n"
        fixture = {
            "commits": [
                {"files": {"GOAL.md": active}},
                {"files": {"GOAL.md": paused}},
            ]
        }
        self.assertFalse(runner.fixture_requires_goal_pause_handoff(fixture))
        fixture["commits"].append({"files": {"GOAL.md": active}})
        self.assertTrue(runner.fixture_requires_goal_pause_handoff(fixture))
        fixture["commits"].append({"files": {"GOAL.md": None}})
        self.assertFalse(runner.fixture_requires_goal_pause_handoff(fixture))

    def test_every_case_constrains_all_permission_fields(self) -> None:
        retired = {
            "decision",
            "protocol_may_product_write",
            "protocol_review_mode",
            "protocol_may_complete",
        }
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                oracle = case["oracle"]
                self.assertIn("expected_action", oracle)
                self.assertEqual(
                    set(oracle["required_observation"]),
                    {"qualifies", "execplan_conditions"},
                )
                self.assertFalse(retired & set(oracle))
                invalid = copy.deepcopy(case)
                del invalid["oracle"]["expected_action"]
                with self.assertRaises(ValueError):
                    runner.validate_case(invalid, Path(f"{case['id']}.json"))

    def test_review_mode_is_a_two_state_clean_break(self) -> None:
        schema = runner.OUTPUT_SCHEMA
        self.assertNotIn("protocol_review_mode", schema["properties"])
        self.assertNotIn("decision", schema["properties"])
        self.assertEqual(
            self._case_report(self.cases["exact-final-ready"])[
                "next_action"
            ]["kind"],
            "EXACT_FINAL",
        )

    def test_live_projection_has_one_reducer_owned_boundary(self) -> None:
        self.assertIn("derives the sole NextAction", runner.EVALUATOR_CONTEXT)
        self.assertNotIn("permission fields", runner.EVALUATOR_CONTEXT)
        self.assertNotIn("protocol_may_", runner.EVALUATOR_CONTEXT)

    def test_live_projection_instructions_make_saturated_semantics_field_local(
        self,
    ) -> None:
        finding = runner.OUTPUT_SCHEMA["properties"]["findings"]["items"]
        self.assertEqual(finding, {"$ref": "finding"})
        finding_schema = runner.CONTRACTS["schemas"]["finding"]
        self.assertFalse(finding_schema["additionalProperties"])
        self.assertIn("blocker", finding_schema["properties"])
        self.assertEqual(
            runner.OUTPUT_SCHEMA["properties"]["open_gates"]["items"]["enum"],
            [
                "user_selection",
                "contract_freeze",
                "red_oracle",
                "product_edit",
                "checks",
                "reconciliation",
                "candidate_freeze",
                "exact_final_review",
                "release",
            ],
        )

    def test_projection_separates_path_anchors_from_ids_and_lifecycle_markers(
        self,
    ) -> None:
        left = self._report(
            self._observation(
                findings=[self._finding("same-id", self._path("Src/App.py"))],
                gate="product_edit",
            )
        )
        right = self._report(
            self._observation(
                findings=[self._finding("same-id", self._path("src/app.py"))],
                gate="product_edit",
            )
        )
        self.assertNotEqual(left["state_key"], right["state_key"])
        marker = self._report(
            self._observation(
                findings=[
                    self._finding(
                        "lifecycle",
                        self._marker("EXACT-FINAL-READY"),
                    )
                ],
                gate="exact_final_review",
            )
        )
        self.assertEqual(marker["next_action"]["kind"], "EXACT_FINAL")

    def test_live_oracles_follow_permission_and_classification_contracts(
        self,
    ) -> None:
        expected = {
            "multi-repo-submodule": "IMPLEMENT",
            "no-commit-unselected": "ASK_USER",
            "compaction-recovery": "RECONCILE",
            "exact-final-ready": "EXACT_FINAL",
        }
        for case_id, action in expected.items():
            self.assertEqual(
                self.cases[case_id]["oracle"]["expected_action"],
                action,
            )

    def test_remaining_markers_and_dirty_paths_have_anchored_classifications(
        self,
    ) -> None:
        required = {
            "no-commit-archive-recovery": self._marker(
                "ARCHIVE-RECOVERY-VALID"
            ),
            "pre-freeze-compaction": self._marker("RECOVERY-GIT-6D91"),
            "midflight-escalation": self._path("lib.py"),
            "no-commit-secret": self._path("scan.txt"),
        }
        for case_id, anchor in required.items():
            anchors = {
                self._anchor_key(item["anchor"])
                for item in self.cases[case_id]["oracle"].get(
                    "required_anchored_findings",
                    [],
                )
            }
            self.assertIn(self._anchor_key(anchor), anchors, case_id)

    def test_recovery_manifest_cross_binds_oracle_facts(self) -> None:
        native = self.cases["pre-freeze-compaction"]["fixture"][
            "native_compaction_resume"
        ]
        content = native["post_compaction_transition"]["files"][
            "docs/execplans/recovery-manifest.json"
        ]
        manifest = json.loads(content)
        self.assertEqual(
            set(manifest),
            {
                "schema_version",
                "repositories",
                "resource_claim",
                "selected_checkpoint",
                "writer",
                "tests",
                "agents",
                "gates",
            },
        )
        self.assertEqual(
            manifest["selected_checkpoint"],
            {
                "archive": "sha256:" + "8" * 64,
                "ref": None,
            },
        )
        self.assertEqual(
            manifest["repositories"],
            [
                {
                    "namespace": "queue-primary",
                    "revision": "1" * 40,
                    "tree": "2" * 40,
                },
                {
                    "namespace": "queue-secondary",
                    "revision": "5" * 40,
                    "tree": "6" * 40,
                },
            ],
        )
        self.assertEqual(
            {
                resource.split(":", 1)[0]
                for resource in manifest["resource_claim"]["resources"]
            },
            {"worktree", "ref", "ledger", "output", "activation"},
        )
        self.assertEqual(manifest["writer"], "Root")
        self.assertEqual(manifest["tests"]["failed"], 0)
        self.assertTrue(manifest["agents"][0]["receipt_reproduced"])
        self.assertEqual(
            manifest["gates"],
            ["contract_freeze", "red_oracle", "product_edit"],
        )

        content_tamper = json.loads(json.dumps(native))
        content_tamper["post_compaction_transition"]["files"][
            "docs/execplans/recovery-manifest.json"
        ] += " "
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_recovery_manifest(
                content_tamper,
                case_id="pre-freeze-compaction-content-tamper",
            )
        basename_alias = json.loads(json.dumps(native))
        content = basename_alias["post_compaction_transition"]["files"].pop(
            runner.RECOVERY_MANIFEST_PATH
        )
        basename_alias["post_compaction_transition"]["files"][
            "alias/recovery-manifest.json"
        ] = content
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_recovery_manifest(
                basename_alias,
                case_id="pre-freeze-compaction-basename-alias",
            )

        def resigned(mutator: object) -> dict[str, object]:
            tampered = json.loads(json.dumps(native))
            tampered_manifest = json.loads(
                tampered["post_compaction_transition"]["files"][
                    "docs/execplans/recovery-manifest.json"
                ]
            )
            mutator(tampered_manifest)
            tampered_content = (
                json.dumps(
                    tampered_manifest,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )
            tampered["post_compaction_transition"]["files"][
                "docs/execplans/recovery-manifest.json"
            ] = tampered_content
            marker = (
                "RECOVERY-MANIFEST-SHA256:"
                + hashlib.sha256(tampered_content.encode()).hexdigest()
            )
            tampered["recovery_oracle"]["marker_ids"] = [
                marker if item.startswith("RECOVERY-MANIFEST-SHA256:") else item
                for item in tampered["recovery_oracle"]["marker_ids"]
            ]
            return tampered

        invalid_states = (
            (
                "state",
                lambda value: value.__setitem__("writer", "unknown"),
            ),
            (
                "checkpoint",
                lambda value: value["selected_checkpoint"].__setitem__(
                    "archive",
                    "latest.tar",
                ),
            ),
            (
                "claim",
                lambda value: value["resource_claim"]["resources"].__setitem__(
                    4, "output:review/other"
                ),
            ),
            (
                "duplicate repository",
                lambda value: value["repositories"][1].__setitem__(
                    "namespace", "queue-primary"
                ),
            ),
            (
                "accepted failure overflow",
                lambda value: value["tests"].update(
                    accepted_failures=1,
                    failed=0,
                ),
            ),
            (
                "unreproduced agent",
                lambda value: value["agents"][0].__setitem__(
                    "receipt_reproduced", False
                ),
            ),
            (
                "empty agents",
                lambda value: value.__setitem__("agents", []),
            ),
            (
                "duplicate agent",
                lambda value: value["agents"].append(
                    json.loads(json.dumps(value["agents"][0]))
                ),
            ),
            (
                "empty gates",
                lambda value: value.__setitem__("gates", []),
            ),
            (
                "duplicate gates",
                lambda value: value["gates"].append("contract_freeze"),
            ),
            (
                "two checkpoints",
                lambda value: value["selected_checkpoint"].__setitem__(
                    "ref", "refs/tasks/queue"
                ),
            ),
        )
        for label, mutator in invalid_states:
            with self.subTest(label=label):
                with self.assertRaisesRegex(
                    ValueError,
                    "invalid Recovery Manifest state|"
                    "schema (type or enum|string|array) mismatch",
                ):
                    validate_recovery_manifest(
                        resigned(mutator),
                        case_id=f"pre-freeze-compaction-{label}-tamper",
                    )

        for label, mutator in (
            (
                "gates",
                lambda value: value.__setitem__("gates", ["user_selection"]),
            ),
            (
                "tests",
                lambda value: value["tests"].__setitem__("passed", 20),
            ),
            (
                "agents",
                lambda value: value["agents"][0].__setitem__("id", "OTHER"),
            ),
        ):
            with self.subTest(label=label), self.assertRaisesRegex(
                ValueError, "Recovery Manifest cross-binding mismatch"
            ):
                validate_recovery_manifest(
                    resigned(mutator),
                    case_id=f"pre-freeze-compaction-{label}-mismatch",
                )

        def select_safe_ref(value: dict[str, object]) -> None:
            value["selected_checkpoint"] = {
                "archive": None,
                "ref": "refs/tasks/queue",
            }

        validate_recovery_manifest(
            resigned(select_safe_ref),
            case_id="pre-freeze-compaction-safe-ref",
        )

    def test_live_oracle_alternatives_cannot_authorize_user_gated_writes(
        self,
    ) -> None:
        for case_id in (
            "goal-divergence",
            "no-commit-secret",
            "no-commit-unselected",
        ):
            case = self.cases[case_id]
            report = self._case_report(case)
            self.assertEqual(report["next_action"]["kind"], "ASK_USER")
            counterexample = self._report(
                self._observation(gate="product_edit"),
                task_id=f"case:{case_id}:write-counterexample",
            )
            self.assertTrue(runner.match_oracle(counterexample, case["oracle"]))

    def test_required_anchor_members_and_items_are_distinct(self) -> None:
        case = self.cases["boundary-cutover"]
        report = self._case_report(case)
        self.assertEqual(runner.match_oracle(report, case["oracle"]), [])
        missing = copy.deepcopy(report)
        target = self._path("docs/execplans/cutover.md")
        matches = [
            index
            for index, finding in enumerate(missing["observation"]["findings"])
            if target in finding["anchors"] and finding["blocker"] is not None
        ]
        del missing["observation"]["findings"][matches[0]]
        missing = self._report(
            missing["observation"],
            task_id="case:boundary-cutover:missing",
        )
        self.assertTrue(runner.match_oracle(missing, case["oracle"]))

    def test_resolved_finding_cannot_remain_blocking(self) -> None:
        from evaluation.semantic import SemanticError, parse_model_observation

        raw = self._observation(
            findings=[
                self._finding(
                    "resolved",
                    status="resolved",
                    blocker="original_goal",
                )
            ]
        )
        with self.assertRaisesRegex(SemanticError, "resolved"):
            parse_model_observation(raw)

    def test_case_validation_rejects_invalid_permission_states(self) -> None:
        for mutation in (
            lambda oracle: oracle.__setitem__("expected_action", "continue"),
            lambda oracle: oracle.__setitem__("decision", "continue"),
            lambda oracle: oracle["required_observation"].__setitem__(
                "qualifies",
                1,
            ),
        ):
            case = copy.deepcopy(self.cases["subthreshold-control"])
            mutation(case["oracle"])
            with self.assertRaises(ValueError):
                runner.validate_case(case, Path("invalid.json"))

    def test_case_validation_rejects_blank_expected_identities(self) -> None:
        mutations = (
            ("accepted_baseline_failures", [" "]),
            (
                "required_findings",
                [{"id": " ", "domain": "other", "statuses": ["unknown"]}],
            ),
            (
                "required_blockers",
                [{"id": " ", "classes": ["original_goal"]}],
            ),
        )
        for key, value in mutations:
            case = copy.deepcopy(self.cases["subthreshold-control"])
            case["oracle"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.validate_case(case, Path("blank.json"))

    def test_shared_constraint_rejects_contradictory_completion_receipts(
        self,
    ) -> None:
        from evaluation.semantic import SemanticError

        with self.assertRaises(SemanticError):
            self._report(
                self._observation(
                    findings=[
                        {
                            **self._finding("open", status="unknown"),
                            "blocker": None,
                        }
                    ],
                    gate=None,
                )
            )
        blocked = self._report(
            self._observation(
                findings=[self._finding("open", status="unknown")],
                gate=None,
            )
        )
        self.assertEqual(blocked["next_action"]["kind"], "IMPLEMENT")

    def test_fixed_convergence_cases_mechanically_bind_new_behavior(self) -> None:
        for case_id in (
            "clean-qualifying-control",
            "exact-final-ready",
            "review-admin-cycle",
            "review-inventory-gate",
        ):
            case = self.cases[case_id]
            self.assertEqual(
                runner.match_oracle(self._case_report(case), case["oracle"]),
                [],
                case_id,
            )

    def test_review_mode_and_recovery_phase_form_one_state_machine(self) -> None:
        scenarios = (
            ("product_edit", "usable", "IMPLEMENT"),
            ("checks", "usable", "CHECK"),
            ("candidate_freeze", "usable", "FREEZE"),
            ("exact_final_review", "usable", "EXACT_FINAL"),
            ("release", "usable", "RELEASE"),
            (None, "usable", "CLOSE"),
            (None, "missing", "RECONCILE"),
        )
        for gate, execplan, expected in scenarios:
            with self.subTest(gate=gate, execplan=execplan):
                report = self._report(
                    self._observation(gate=gate, execplan=execplan)
                )
                self.assertEqual(report["next_action"]["kind"], expected)

    def test_receipt_projection_binds_review_mode_without_alias(self) -> None:
        report = self._case_report(self.cases["exact-final-ready"])
        receipt = receipt_engine.sanitized_report_receipt(report)
        self.assertEqual(receipt["next_action"]["kind"], "EXACT_FINAL")
        self.assertNotIn("protocol_review_mode", json.dumps(receipt))
        tampered = copy.deepcopy(report)
        tampered["next_action"]["kind"] = "IMPLEMENT"
        with self.assertRaises(ValueError):
            receipt_engine.sanitized_report_receipt(tampered)

    def test_open_family_cannot_masquerade_as_exact_final(self) -> None:
        report = self._report(
            self._observation(
                findings=[
                    self._finding(
                        "open-family",
                        status="unknown",
                        blocker="frozen_acceptance",
                    )
                ],
                gate="exact_final_review",
            )
        )
        self.assertEqual(report["next_action"]["kind"], "IMPLEMENT")

    def test_review_write_and_stop_for_user_are_mechanically_exclusive(
        self,
    ) -> None:
        kinds = {
            self._report(self._observation(gate=gate))["next_action"]["kind"]
            for gate in ("user_selection", "product_edit", "exact_final_review")
        }
        self.assertEqual(kinds, {"ASK_USER", "IMPLEMENT", "EXACT_FINAL"})

    def test_unusable_execplan_cannot_review_or_complete_without_recovery(
        self,
    ) -> None:
        for gate in (None, "product_edit", "exact_final_review", "release"):
            report = self._report(
                self._observation(gate=gate, execplan="needs_amendment")
            )
            self.assertEqual(report["next_action"]["kind"], "RECONCILE")

    def test_exact_final_rejects_open_findings_blockers_and_repair_gates(
        self,
    ) -> None:
        clean = self._report(
            self._observation(gate="exact_final_review")
        )
        self.assertEqual(clean["next_action"]["kind"], "EXACT_FINAL")
        blocked = self._report(
            self._observation(
                findings=[self._finding("open", status="candidate_new")],
                gate="exact_final_review",
            )
        )
        self.assertEqual(blocked["next_action"]["kind"], "IMPLEMENT")

    def test_every_blocker_must_match_exactly_one_finding(self) -> None:
        from evaluation.semantic import SemanticError, parse_model_observation

        raw = self._observation(
            findings=[self._finding("one", status="unknown")]
        )
        parsed = parse_model_observation(raw)
        self.assertEqual(parsed.findings[0].finding_id, "one")
        invalid = copy.deepcopy(raw)
        invalid["blockers"] = []
        with self.assertRaises(SemanticError):
            parse_model_observation(invalid)

    def test_recovery_facts_and_content_addressed_manifest_fail_closed(
        self,
    ) -> None:
        recovery = self._recovery()
        report = self._report(
            self._observation(recovery=recovery, gate="checks")
        )
        self.assertEqual(report["observation"]["recovery"], recovery)
        missing = copy.deepcopy(recovery)
        missing["marker_ids"] = []
        with self.assertRaisesRegex(ValueError, "Recovery Manifest"):
            self._report(self._observation(recovery=missing, gate="checks"))

    def test_exact_final_fixture_is_reachable_evidence_not_plan_prose(self) -> None:
        case = self.cases["exact-final-ready"]
        commits = case["fixture"]["commits"]
        self.assertGreaterEqual(len(commits), 5)
        rendered = json.dumps(case, sort_keys=True)
        for marker in (
            "{{COMMIT_",
            "{{TREE_",
            "{{PRODUCT_SHA256_",
            "focused review receipt",
            "review_projection",
            "post-source offline evidence",
            "review prelaunch",
        ):
            self.assertIn(marker, rendered)

    def test_recovery_manifest_rejects_removed_state_machine_fields(self) -> None:
        from evaluation.semantic import SemanticError, parse_model_observation

        for mutation in (
            lambda recovery: recovery.__setitem__(
                "milestone_phase",
                "implementation",
            ),
            lambda recovery: recovery.__setitem__(
                "next_action",
                "focused_review",
            ),
            lambda recovery: recovery.__setitem__(
                "pending_gates",
                ["boundary_repair"],
            ),
        ):
            recovery = self._recovery()
            mutation(recovery)
            with self.assertRaises(SemanticError):
                parse_model_observation(
                    self._observation(recovery=recovery, gate="checks")
                )

    def test_positive_contract_fixtures_use_current_claim_states(self) -> None:
        plan_paths = {
            "authorized-rebaseline": "docs/execplans/schema.md",
            "clean-qualifying-control": ".work/plans/default-limit.md",
            "review-admin-cycle": "docs/execplans/greeting.md",
        }
        for case_id, relative in plan_paths.items():
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as raw:
                repo = Path(raw) / "repo"
                runner.build_fixture(self.cases[case_id], repo)
                plans = [repo / relative]
                self.assertTrue(plans[0].is_file())
                claim_lines = [
                    line.casefold()
                    for line in plans[0].read_text().splitlines()
                    if line.casefold().startswith(("- o", "- p", "- r"))
                ]
                self.assertTrue(claim_lines)
                self.assertFalse(
                    any(" closed" in line for line in claim_lines), claim_lines
                )

    def test_prompts_invoke_skill_without_leaking_hidden_terms(self) -> None:
        for case in self.cases.values():
            prompt = case["prompt"].casefold()
            self.assertIn("$happycodex:happycodex", prompt)
            for hidden in case["oracle"].get("prompt_forbidden", []):
                self.assertNotIn(hidden.casefold(), prompt, case["id"])

    def test_packaged_eval_arm_cannot_read_corpus_or_repository_controls(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            package = Path(raw) / "package"
            runner.copy_plugin_package(ROOT, package)
            files = {
                path.relative_to(package).as_posix()
                for path in package.rglob("*")
                if path.is_file()
            }
            self.assertIn("skills/happycodex/SKILL.md", files)
            self.assertIn("skills/happycodex/references/execplan.md", files)
            self.assertFalse(any(path.startswith("evaluation/") for path in files))
            self.assertFalse(any(path.startswith("tests/") for path in files))
            self.assertFalse(any(path.startswith("docs/") for path in files))
            self.assertNotIn("AGENTS.md", files)

    def test_dirty_recovery_fixture_has_real_git_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            facts = runner.build_fixture(self.cases["compaction-recovery"], repo)
            self.assertIn("A  staged-review.txt", facts["status_before"])
            self.assertIn(" M src/job.py", facts["status_before"])
            self.assertIn("?? scratch-recovery.txt", facts["status_before"])
            self.assertEqual(len(facts["commits"]), 1)

    def test_workspace_manifest_detects_content_only_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            facts = runner.build_fixture(self.cases["compaction-recovery"], repo)
            before_status = git(
                repo, "status", "--porcelain=v1", "--untracked-files=all"
            )
            before_files = facts["files"]
            (repo / "scratch-recovery.txt").write_text("changed in place\n")
            self.assertEqual(
                git(repo, "status", "--porcelain=v1", "--untracked-files=all"),
                before_status,
            )
            self.assertNotEqual(runner.workspace_file_manifest(repo), before_files)

    def test_fixture_can_freeze_a_prior_commit_and_tree(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            facts = runner.build_fixture(self.cases["clean-qualifying-control"], repo)
            plan = (repo / ".work/plans/default-limit.md").read_text()
            self.assertEqual(len(facts["commits"]), 2)
            self.assertIn(facts["commits"][0], plan)
            self.assertIn(facts["trees"][0], plan)
            self.assertNotIn("{{", plan)
            self.assertIn("Repository policy source: AGENTS.md", plan)
            self.assertFalse((repo / "docs/execplans/default-limit.md").exists())

    def test_pre_freeze_fixture_has_committed_skeleton_and_pending_gates(
        self,
    ) -> None:
        native = self.cases["pre-freeze-compaction"]["fixture"][
            "native_compaction_resume"
        ]
        self.assertIn(
            "full structured recovery object",
            native["fresh_recovery_prompt"],
        )
        self.assertEqual(
            native["recovery_oracle"]["pending_gates"],
            ["contract_freeze", "red_oracle", "product_edit"],
        )

    def test_post_compaction_transition_introduces_unseen_durable_facts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            case = self.cases["pre-freeze-compaction"]
            facts = runner.build_fixture(case, repo)
            before_head = facts["head"]
            transition = runner.apply_post_compaction_transition(
                repo,
                case["fixture"]["native_compaction_resume"][
                    "post_compaction_transition"
                ],
                facts,
            )
            self.assertNotEqual(before_head, transition["head"])
            self.assertEqual(git(repo, "status", "--porcelain=v1"), "")
            self.assertIn(
                "RECOVERY-PLAN-47B2",
                (repo / "docs/execplans/queue-migration.md").read_text(),
            )
            self.assertIn("RECOVERY-TEST-19C4", (repo / "tests.txt").read_text())
            self.assertEqual(
                transition["message"],
                "docs: record durable recovery marker RECOVERY-GIT-6D91",
            )
            self.assertEqual(transition["files"], runner.workspace_file_manifest(repo))
            self.assertEqual(transition["status"], "")

    def test_recovery_control_requires_distinct_task_and_equivalent_gates(
        self,
    ) -> None:
        observation = self._observation(
            recovery=self._recovery(),
            gate="checks",
        )
        primary = self._report(observation, task_id="case:primary")
        fresh = self._report(observation, task_id="case:fresh")
        self.assertEqual(
            runner.recovery_control_failures(
                primary=primary,
                primary_thread_id="thread-primary",
                fresh=fresh,
                fresh_thread_id="thread-fresh",
                expected_state=self._recovery(),
            ),
            [],
        )
        self.assertTrue(
            runner.recovery_control_failures(
                primary=primary,
                primary_thread_id="same",
                fresh=fresh,
                fresh_thread_id="same",
            )
        )

    def test_recovery_control_rejects_equal_but_false_durable_state(self) -> None:
        expected = self._recovery()
        false = copy.deepcopy(expected)
        false["current_tree"] = "9" * 40
        observation = self._observation(recovery=false, gate="checks")
        primary = self._report(observation, task_id="case:false-primary")
        fresh = self._report(observation, task_id="case:false-fresh")
        failures = runner.recovery_control_failures(
            primary=primary,
            primary_thread_id="one",
            fresh=fresh,
            fresh_thread_id="two",
            expected_state=expected,
        )
        self.assertTrue(any("current_tree" in item for item in failures))

    def test_install_validation_binds_the_entire_package(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            package = Path(raw) / "package"
            installed = Path(raw) / "installed"
            runner.copy_plugin_package(ROOT, package)
            runner.copy_plugin_package(ROOT, installed)
            receipt = runner.installed_package_receipt(package, installed)
            self.assertEqual(
                receipt["source_package_manifest_sha256"],
                receipt["installed_package_manifest_sha256"],
            )
            reference = installed / "skills/happycodex/references/execplan.md"
            reference.write_text(reference.read_text() + "\nchanged\n")
            with self.assertRaisesRegex(RuntimeError, "package manifest"):
                runner.installed_package_receipt(package, installed)

    def test_package_copy_rejects_hidden_or_unexpected_runtime_input(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "source"
            package = Path(raw) / "package"
            runner.copy_plugin_package(ROOT, source)
            hidden = source / "skills/happycodex/__pycache__/hidden.pyc"
            hidden.parent.mkdir()
            hidden.write_bytes(b"untracked runtime input")
            with self.assertRaisesRegex(RuntimeError, "runtime surface"):
                runner.copy_plugin_package(source, package)
            self.assertFalse(package.exists())

    def test_package_copy_rejects_unrelated_untracked_plugin_input(self) -> None:
        for relative in ("skills/other/SKILL.md", ".agents/unrelated.txt"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as raw:
                source = Path(raw) / "source"
                package = Path(raw) / "package"
                runner.copy_plugin_package(ROOT, source)
                unexpected = source / relative
                unexpected.parent.mkdir(parents=True, exist_ok=True)
                unexpected.write_text("untracked package input\n")
                with self.assertRaisesRegex(RuntimeError, "runtime surface"):
                    runner.copy_plugin_package(source, package)
                self.assertFalse(package.exists())

    def test_runtime_surface_is_exact_per_evaluation_arm(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            public_source = root / "public-source"
            runner.copy_plugin_package(ROOT, public_source)
            with self.assertRaisesRegex(RuntimeError, "runtime surface"):
                runner.copy_plugin_package(
                    public_source,
                    root / "public-rejects-candidate-script",
                    arm="public-0.2",
                )
            helper = public_source / "skills/happycodex/scripts/resource_claim.py"
            helper.unlink()
            helper.parent.rmdir()
            references = public_source / "skills/happycodex/references"
            (references / "execplan.md").unlink()
            (references / "external-review.md").write_text("public review\n")
            (references / "task-packets.md").write_text("public tasks\n")
            public_package = root / "public-package"
            runner.copy_plugin_package(
                public_source, public_package, arm="public-0.2"
            )

            legacy_source = root / "legacy-public-source"
            runner.copy_plugin_package(ROOT, legacy_source)
            legacy_references = legacy_source / "skills/happycodex/references"
            (legacy_references / "execplan.md").unlink()
            (legacy_references / "external-review.md").write_text("legacy review\n")
            (legacy_references / "task-packets.md").write_text("legacy tasks\n")
            with self.assertRaisesRegex(RuntimeError, "runtime surface"):
                runner.copy_plugin_package(
                    legacy_source,
                    root / "public-rejects-legacy-surface",
                    arm="public-0.2",
                )
            hidden = references / "__pycache__/hidden.pyc"
            hidden.parent.mkdir()
            hidden.write_bytes(b"untracked public runtime input")
            with self.assertRaisesRegex(RuntimeError, "runtime surface"):
                runner.copy_plugin_package(
                    public_source,
                    root / "public-rejects-hidden",
                    arm="public-0.2",
                )

            manifest = runner.package_identities(public_package)["semantic_sha256"]
            case = self.cases["review-inventory-gate"]
            common = {
                "package_semantic_sha256": manifest,
                "model": "gpt-5.6-sol",
                "effort": "high",
                "timeout": 300,
            }
            self.assertNotEqual(
                runner.semantic_input_sha256_from_package(
                    case, **common, arm="candidate"
                ),
                runner.semantic_input_sha256_from_package(
                    case, **common, arm="public-0.2"
                ),
            )

    def test_sanitized_case_receipt_preserves_auditable_fields(self) -> None:
        report = self._case_report(self.cases["exact-final-ready"])
        observation = report["observation"]
        profile = self._context()["invocation_profile"]
        result = {
            "case": "exact-final-ready",
            "model": "gpt-5.6-sol",
            "effort": "high",
            "timeout_seconds": 300,
            "timed_out": False,
            "elapsed_seconds": 1.0,
            "exit_code": 0,
            "semantic_input_sha256": "1" * 64,
            "invocation_profile": profile,
            "accepted_baseline_failures": [],
            "identities": {},
            "events_sha256": "2" * 64,
            "stderr_sha256": "3" * 64,
            "usage": {"output_tokens": 1},
            "usage_phases": [],
            "uncached_input_tokens": 1,
            "passed": True,
            "result": observation,
            "canonical_report": report,
            "fresh_recovery_result": None,
            "fresh_recovery_canonical_report": None,
            "installation": {},
            "oracle_failures": [],
        }
        receipt = receipt_engine.sanitized_case_receipt(
            result,
            metadata_sha256="4" * 64,
        )
        self.assertEqual(receipt["engine_generation"], "0.6.5")
        self.assertEqual(
            receipt["canonical_report"]["action_key"],
            report["action_key"],
        )
        self.assertNotIn("reason", receipt["result"])

    def test_compaction_receipt_proves_a_byte_append(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            rollout = home / "sessions" / "thread-append-proof.jsonl"
            rollout.parent.mkdir(parents=True)
            before_bytes = b'{"type":"compacted"}\n'
            rollout.write_bytes(before_bytes)
            before = runner.compaction_receipt(home, "thread-append-proof")

            rollout.write_bytes(before_bytes + b'{"type":"event_msg"}\n')
            after = runner.compaction_receipt(
                home,
                "thread-append-proof",
                prefix_length=before["rollout_byte_count"],
            )

        self.assertEqual(before["rollout_byte_count"], len(before_bytes))
        self.assertGreater(after["rollout_byte_count"], before["rollout_byte_count"])
        self.assertEqual(after["rollout_prefix_sha256"], before["rollout_sha256"])

    def test_phrase_presence_is_not_an_acceptance_oracle(self) -> None:
        case = self.cases["exact-final-ready"]
        report = self._report(
            self._observation(
                gate="exact_final_review",
                reason="EXACT-FINAL-READY appears only in prose",
            ),
            task_id="case:phrase-only",
        )
        self.assertTrue(runner.match_oracle(report, case["oracle"]))

    def test_fixture_build_is_deterministic_across_ambient_dates(self) -> None:
        case = self.cases["review-admin-cycle"]
        with tempfile.TemporaryDirectory() as raw:
            first = Path(raw) / "first"
            second = Path(raw) / "second"
            with mock.patch.dict(
                os.environ,
                {
                    "GIT_AUTHOR_DATE": "2020-01-01T00:00:00Z",
                    "GIT_COMMITTER_DATE": "2020-01-01T00:00:00Z",
                },
            ):
                first_facts = runner.build_fixture(case, first)
            with mock.patch.dict(
                os.environ,
                {
                    "GIT_AUTHOR_DATE": "2030-01-01T00:00:00Z",
                    "GIT_COMMITTER_DATE": "2030-01-01T00:00:00Z",
                },
            ):
                second_facts = runner.build_fixture(case, second)
            for field in (
                "commits",
                "trees",
                "product_manifest_sha256",
                "review_projections",
                "challenger_receipts",
                "head",
                "tree",
                "status_before",
                "files",
            ):
                self.assertEqual(first_facts[field], second_facts[field], field)

    def test_raw_output_path_must_be_outside_repository(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            runner.resolve_output_path(ROOT / "evaluation" / "raw", plugin=ROOT)
        with tempfile.TemporaryDirectory() as raw:
            expected = (Path(raw) / "results").resolve()
            self.assertEqual(
                runner.resolve_output_path(expected, plugin=ROOT), expected
            )
            alternate_plugin = Path(raw) / "public-0.2"
            alternate_plugin.mkdir()
            with self.assertRaisesRegex(ValueError, "evaluated plugin"):
                runner.resolve_output_path(
                    alternate_plugin / "raw", plugin=alternate_plugin
                )

    def test_native_permission_profile_hides_auth_and_oracle_sources(self) -> None:
        hidden_fd, hidden_raw = tempfile.mkstemp(prefix="happycodex-hidden-canary-")
        os.close(hidden_fd)
        hidden = Path(hidden_raw)
        try:
            with tempfile.TemporaryDirectory(
                prefix="happycodex-isolation-test-"
            ) as raw:
                temp = Path(raw).resolve()
                repo = temp / "repo"
                repo.mkdir()
                (repo / "visible.txt").write_text("visible\n")
                source_home = temp / "source-codex-home"
                source_home.mkdir()
                (source_home / "auth.json").write_text('{"test": true}\n')
                home, env = runner.isolated_home(temp, source_home=source_home)
                tool_bin = temp / "bin"
                probe = (
                    "from pathlib import Path; import subprocess; "
                    f"assert not Path({str(ROOT)!r}).exists(); "
                    f"assert not Path({str(hidden)!r}).exists(); "
                    f"assert not Path({str(home / 'auth.json')!r}).exists(); "
                    f"assert not Path({str(source_home / 'auth.json')!r}).exists(); "
                    f"assert not Path({str(temp / 'response-schema.json')!r}).exists(); "
                    "assert Path('visible.txt').read_text() == 'visible\\n'; "
                    "assert subprocess.run(['rg', '--version'], capture_output=True).returncode == 0; "
                    "assert subprocess.run(['touch', 'forbidden'], capture_output=True).returncode != 0"
                )
                argv = [
                    str(tool_bin / "codex"),
                    "sandbox",
                    "-P",
                    runner.PERMISSION_PROFILE,
                    "-C",
                    str(repo),
                    *runner.permission_profile_args(
                        tool_bin=tool_bin,
                        user_home=temp / "user-home",
                        select_default=False,
                    ),
                    "--",
                    "python3",
                    "-c",
                    probe,
                ]
                completed = runner.run(argv, cwd=repo, env=env)
                self.assertEqual(completed.returncode, 0, completed.stderr)
        finally:
            hidden.unlink(missing_ok=True)

    def test_isolated_home_strips_parent_task_context(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_home = root / "source-codex-home"
            source_home.mkdir()
            (source_home / "auth.json").write_text('{"test": true}\n')
            parent = root / "case"
            parent.mkdir()
            with mock.patch.dict(
                os.environ,
                {
                    "CODEX_REMOTE_PAYLOAD": "parent conversation",
                    "CODEX_THREAD_ID": "parent-thread",
                    "PWD": str(ROOT),
                },
            ):
                home, env = runner.isolated_home(parent, source_home=source_home)
            self.assertNotIn("CODEX_REMOTE_PAYLOAD", env)
            self.assertNotIn("CODEX_THREAD_ID", env)
            self.assertNotIn("PWD", env)
            self.assertEqual(env["HOME"], str(parent / "user-home"))
            self.assertEqual(env["CODEX_HOME"], str(home))
            self.assertEqual(env["PATH"].split(os.pathsep)[0], str(parent / "bin"))
            version = runner.run(["codex", "--version"], cwd=parent, env=env)
            self.assertEqual(version.returncode, 0, version.stderr)
            self.assertEqual(version.stdout.strip(), runner.codex_identity()["version"])
            copied_auth = home / "auth.json"
            self.assertFalse(copied_auth.is_symlink())
            self.assertEqual(copied_auth.read_text(), '{"test": true}\n')
            self.assertEqual(copied_auth.stat().st_mode & 0o777, 0o600)

    def test_review_admin_cycle_changes_only_control_record(self) -> None:
        case = self.cases["review-admin-cycle"]
        report = self._case_report(case)
        self.assertEqual(report["next_action"]["kind"], "CLOSE")
        self.assertEqual(runner.match_oracle(report, case["oracle"]), [])

    def test_review_projection_ref_failures_fail_closed(self) -> None:
        from evaluation.semantic import SemanticError, parse_report

        report = self._case_report(self.cases["review-isolation"])
        for field in ("state_key", "action_key"):
            tampered = copy.deepcopy(report)
            tampered[field] = "0" * 64
            with self.subTest(field=field), self.assertRaises(SemanticError):
                parse_report(tampered)

    def test_review_isolation_mechanically_omits_a_decisive_large_diff_tail(
        self,
    ) -> None:
        excluded = "docs/execplans/parser.md"
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            facts = runner.build_fixture(self.cases["review-isolation"], repo)
            projection = facts["review_projections"][0]
            diff_units = git(
                repo,
                "diff",
                "--name-only",
                projection["baseline_commit"],
                projection["candidate_commit"],
            ).splitlines()
            decisive_tail = "zz-generated/format-0127.txt"
            self.assertGreater(len(diff_units), 100)
            self.assertEqual(projection["diff_unit_count"], len(diff_units))
            self.assertEqual(projection["coverage_limit"], 64)
            self.assertEqual(projection["diff_units"], diff_units)
            self.assertEqual(projection["inspected_diff_units"], diff_units[:64])
            self.assertEqual(projection["omitted_diff_units"], diff_units[64:])
            self.assertEqual(diff_units[-1], decisive_tail)
            self.assertIn(decisive_tail, projection["omitted_diff_units"])
            tail = git(
                repo, "show", f"{projection['candidate_commit']}:{decisive_tail}"
            )
            self.assertIn("DECISIVE-TAIL-LEGACY-V1", tail)
            receipt = git(repo, "cat-file", "blob", projection["output_blob"])
            self.assertIn(f'"diff_unit_count":{len(diff_units)}', receipt)
            self.assertIn("phase_1_correctness_complete=false", receipt)
            self.assertIn("phase_1_diff_unit_coverage=incomplete", receipt)
            self.assertIn("truncation=detected", receipt)
            self.assertIn(f"decisive_tail={decisive_tail}", receipt)
            self.assertIn("omitted_diff_units=", receipt)
            self.assertIn(decisive_tail, receipt)
            plan = (repo / excluded).read_text()
            self.assertIn(projection["output_blob"], plan)
            self.assertIn(projection["output_sha256"], plan)

    def test_generated_large_diff_fixture_rejects_malformed_paths(self) -> None:
        config = self.cases["review-isolation"]["fixture"]["commits"][1][
            "generated_files"
        ]
        with self.assertRaisesRegex(ValueError, "unsafe"):
            runner.generated_fixture_files({**config, "prefix": "../escape-"})
        with self.assertRaisesRegex(ValueError, "invalid"):
            runner.generated_fixture_files({**config, "count": 0})

    def test_neutral_review_brief_withholds_anchor_material(self) -> None:
        receipt = runner.neutral_review_brief(
            operative_request="Change hello to welcome and preserve formatting.",
            scope="baseline..candidate",
            baseline_failures=[],
            objective_verification={
                "source_manifest_equal": True,
                "diff_unit_count": 3,
            },
            exclusions=["docs/execplans/task.md"],
            writer_narrative="WRITER-SAYS-PASS-ANCHOR-77",
            historical_findings=["OLD-FINDING-ANCHOR-88"],
        )
        serialized = json.dumps(receipt, sort_keys=True)
        self.assertNotIn("WRITER-SAYS-PASS-ANCHOR-77", serialized)
        self.assertNotIn("OLD-FINDING-ANCHOR-88", serialized)
        self.assertEqual(
            receipt["writer_narrative_sha256"],
            hashlib.sha256(b"WRITER-SAYS-PASS-ANCHOR-77").hexdigest(),
        )
        self.assertEqual(
            receipt["historical_findings_sha256"],
            runner.canonical_sha256(["OLD-FINDING-ANCHOR-88"]),
        )
        self.assertIn("Change hello to welcome", receipt["brief"])
        self.assertIn('"source_manifest_equal":true', receipt["brief"])
        self.assertIn('"exclusions":["docs/execplans/task.md"]', receipt["brief"])

    def test_seeded_multi_defect_cases_bind_each_coverage_tag_to_an_oracle(
        self,
    ) -> None:
        for case in self.cases.values():
            coverage = case["oracle"].get("coverage_assertions")
            if coverage is None:
                continue
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    {item["tag"] for item in coverage},
                    set(case["covers"]),
                )
                runner.validate_case(case, Path(f"{case['id']}.json"))

    def test_four_false_green_cases_bind_every_seeded_defect(self) -> None:
        for case_id in (
            "no-commit-secret",
            "receipt-mismatch",
            "review-inventory-gate",
            "review-isolation",
        ):
            case = self.cases[case_id]
            report = self._case_report(case)
            self.assertEqual(runner.match_oracle(report, case["oracle"]), [])
            required = case["oracle"].get("required_anchored_blockers", [])
            self.assertTrue(required)
            missing = copy.deepcopy(report)
            target = required[0]["anchor"]
            missing["observation"]["findings"] = [
                finding
                for finding in missing["observation"]["findings"]
                if target not in finding["anchors"]
            ]
            missing = self._report(
                missing["observation"],
                task_id=f"case:{case_id}:missing",
            )
            self.assertTrue(runner.match_oracle(missing, case["oracle"]))

    def test_exact_finding_identity_cannot_replace_an_anchor_member(self) -> None:
        case = self.cases["review-isolation"]
        report = self._case_report(case)
        required = case["oracle"]["required_anchored_blockers"][0]
        observation = copy.deepcopy(report["observation"])
        target = required["anchor"]
        for finding in observation["findings"]:
            if target in finding["anchors"]:
                finding["id"] = target["value"]
                finding["anchors"] = [self._marker("different-anchor")]
                break
        counterexample = self._report(
            observation,
            task_id="case:identity-is-not-anchor",
        )
        self.assertTrue(runner.match_oracle(counterexample, case["oracle"]))

    def test_one_finding_cannot_supply_multiple_blocker_classes(self) -> None:
        from evaluation.semantic import SemanticError, parse_model_observation

        finding = self._finding("one", status="unknown")
        finding["blocker"]["class"] = ["original_goal", "frozen_acceptance"]
        with self.assertRaises(SemanticError):
            parse_model_observation(self._observation(findings=[finding]))

    def test_result_identities_are_nonblank_and_globally_unique(self) -> None:
        from evaluation.semantic import SemanticError, parse_model_observation

        for findings in (
            [self._finding(" ", status="unknown")],
            [
                self._finding("duplicate", status="unknown"),
                self._finding("duplicate", status="unknown"),
            ],
        ):
            with self.assertRaises(SemanticError):
                parse_model_observation(self._observation(findings=findings))

    def test_raw_and_receipt_identity_matching_is_exact(self) -> None:
        raw = self._observation(
            findings=[self._finding("Finding-A", self._path("Src/App.py"))],
            gate="product_edit",
        )
        receipt = receipt_engine.sanitized_result_receipt(raw)
        self.assertEqual(
            receipt["findings"][0]["id_sha256"],
            receipt_engine.text_sha256("Finding-A"),
        )
        self.assertFalse(runner.finding_identity_matches("Finding-A", "finding-a"))

    def test_recovery_marker_receipt_uses_one_canonical_projection(self) -> None:
        recovery = self._recovery()
        receipt = receipt_engine.sanitized_recovery_receipt(recovery)
        self.assertEqual(receipt["recovery_manifest_count"], 1)
        self.assertEqual(receipt["recovery_manifest_sha256"], "a" * 64)
        self.assertTrue(receipt["summary_consistent"])

    def test_generation6_result_projection_replays_and_binds_raw_result(
        self,
    ) -> None:
        from evaluation.semantic import SemanticError, replay, semantic_digest

        report = self._report(
            self._observation(gate="product_edit"),
            task_id="case:roundtrip",
        )
        link = {
            "sequence": 0,
            "previous_hash": None,
            "report": report,
            "consumed_action": True,
        }
        replayed = replay([link])
        self.assertEqual(replayed[0].action_key, report["action_key"])
        duplicate = [
            link,
            {
                "sequence": 1,
                "previous_hash": semantic_digest("receipt-link", link),
                "report": report,
                "consumed_action": True,
            },
        ]
        with self.assertRaisesRegex(SemanticError, "consumed more than once"):
            replay(duplicate)

    def test_case_validation_correlates_recovery_oracle_permissions(
        self,
    ) -> None:
        self.assertEqual(
            self.cases["pre-freeze-compaction"]["oracle"]["expected_action"],
            "FREEZE",
        )
        self.assertEqual(
            self.cases["compaction-recovery"]["oracle"]["expected_action"],
            "RECONCILE",
        )

    def test_read_mode_oracle_requires_semantic_blocker_not_domain_label(
        self,
    ) -> None:
        case = self.cases["compaction-recovery"]
        blocker = next(
            item
            for item in case["oracle"]["required_anchored_blockers"]
            if item["anchor"] == self._marker("test_read_mode")
        )
        self.assertEqual(blocker["classes"], ["original_goal"])
        report = self._case_report(case)
        self.assertEqual(runner.match_oracle(report, case["oracle"]), [])

    def test_boundary_cutover_accepts_only_bounded_overlapping_semantics(
        self,
    ) -> None:
        case = self.cases["boundary-cutover"]
        classes = {
            blocker_class
            for item in case["oracle"]["required_anchored_blockers"]
            for blocker_class in item["classes"]
        }
        self.assertEqual(
            classes,
            {
                "exhaustive_claim",
                "frozen_acceptance",
                "original_goal",
                "production_condition",
                "safety_data_integrity",
            },
        )

    def test_multi_repo_oracle_binds_both_seeded_scope_failures(self) -> None:
        case = self.cases["multi-repo-submodule"]
        anchors = {
            self._anchor_key(item["anchor"])
            for item in case["oracle"]["required_anchored_blockers"]
        }
        self.assertEqual(
            anchors,
            {
                self._anchor_key(self._path("backend/shared-schema.pointer")),
                self._anchor_key(self._path("docs/execplans/contracts.md")),
            },
        )

    def test_inventory_gate_fixture_is_otherwise_complete_but_unnumbered(
        self,
    ) -> None:
        case = self.cases["review-inventory-gate"]
        self.assertEqual(case["oracle"]["expected_action"], "RECONCILE")
        self.assertEqual(
            case["oracle"]["required_anchored_blockers"],
            [
                {
                    "anchor": self._marker("review-task-9"),
                    "classes": ["frozen_acceptance"],
                }
            ],
        )

    def test_receipt_mismatch_has_real_review_but_no_challenger_terminal(
        self,
    ) -> None:
        case = self.cases["receipt-mismatch"]
        anchors = {
            item["anchor"]["value"]
            for item in case["oracle"]["required_anchored_blockers"]
        }
        self.assertIn("review-authority-7", anchors)
        self.assertIn("review-authority-full-task-7", anchors)
        self.assertEqual(case["oracle"]["expected_action"], "RECONCILE")

    def test_oracle_matcher_accepts_controls_and_reports_counterexamples(
        self,
    ) -> None:
        for case in self.cases.values():
            report = self._case_report(case)
            self.assertEqual(
                runner.match_oracle(report, case["oracle"]),
                [],
                case["id"],
            )
            wrong = copy.deepcopy(report["observation"])
            wrong["qualifies"] = not wrong["qualifies"]
            wrong_report = self._report(
                wrong,
                task_id=f"case:{case['id']}:wrong",
            )
            self.assertTrue(runner.match_oracle(wrong_report, case["oracle"]))

    def test_oracle_matcher_uses_blocker_classes_not_prose_phrases(self) -> None:
        case = self.cases["goal-divergence"]
        report = self._case_report(case)
        reworded = copy.deepcopy(report["observation"])
        for finding in reworded["findings"]:
            if finding["blocker"]:
                finding["blocker"]["reason"] = "entirely different prose"
        reworded_report = self._report(
            reworded,
            task_id="case:goal-divergence:reworded",
        )
        self.assertEqual(runner.match_oracle(reworded_report, case["oracle"]), [])
        changed = copy.deepcopy(reworded)
        changed["findings"][0]["blocker"]["class"] = "exhaustive_claim"
        changed_report = self._report(
            changed,
            task_id="case:goal-divergence:wrong-class",
        )
        self.assertTrue(runner.match_oracle(changed_report, case["oracle"]))

    def test_oracle_matcher_checks_structured_finding_identities(self) -> None:
        case = self.cases["exact-final-ready"]
        report = self._case_report(case)
        changed = copy.deepcopy(report["observation"])
        changed["findings"][0]["id"] = "MODEL:EXACT-FINAL-READY"
        changed_report = self._report(
            changed,
            task_id="case:exact-final-ready:alias",
        )
        self.assertTrue(runner.match_oracle(changed_report, case["oracle"]))

    def test_finding_identity_match_is_delimited_not_approximate(self) -> None:
        self.assertTrue(runner.finding_identity_matches("fixture-17", "fixture-17"))
        for actual in (
            "MODEL:fixture-17",
            "prefix-fixture-17",
            "fixture-170",
            "Fixture-17",
        ):
            self.assertFalse(runner.finding_identity_matches(actual, "fixture-17"))

    def test_completion_oracle_rejects_contradictory_output(self) -> None:
        case = self.cases["review-admin-cycle"]
        clean = self._case_report(case)
        self.assertEqual(clean["next_action"]["kind"], "CLOSE")
        blocked = self._report(
            self._observation(
                findings=[self._finding("new", status="candidate_new")],
                gate=None,
            ),
            task_id="case:admin-cycle:blocked",
        )
        self.assertTrue(runner.match_oracle(blocked, case["oracle"]))

    def test_completion_requires_explicit_baseline_failure_acceptance(
        self,
    ) -> None:
        accepted = self._report(
            self._observation(
                findings=[
                    {
                        **self._finding(
                            "baseline-1",
                            domain="baseline_failure",
                            status="baseline_unchanged",
                        ),
                        "blocker": None,
                    }
                ]
            ),
            accepted=["baseline-1"],
        )
        self.assertEqual(accepted["next_action"]["kind"], "CLOSE")
        blocked = self._report(
            self._observation(
                findings=[
                    self._finding(
                        "baseline-1",
                        domain="baseline_failure",
                        status="baseline_unchanged",
                    )
                ]
            )
        )
        self.assertEqual(blocked["next_action"]["kind"], "IMPLEMENT")

    def test_case_validation_rejects_ambiguous_accepted_failure_ids(
        self,
    ) -> None:
        case = copy.deepcopy(self.cases["review-admin-cycle"])
        case["oracle"]["accepted_baseline_failures"] = ["same", "same"]
        with self.assertRaises(ValueError):
            runner.validate_case(case, Path("ambiguous.json"))

    def test_baseline_failure_case_requires_structured_identities(self) -> None:
        case = self.cases["compaction-recovery"]
        identities = {
            item["id"]: (item["domain"], item["statuses"])
            for item in case["oracle"]["required_findings"]
        }
        self.assertEqual(
            identities["fixture-17"],
            ("baseline_failure", ["resolved"]),
        )
        self.assertEqual(
            identities["fixture-18"],
            ("baseline_failure", ["candidate_new"]),
        )

    def test_output_schema_forces_decision_fields(self) -> None:
        required = set(runner.OUTPUT_SCHEMA["required"])
        self.assertEqual(
            required,
            {
                "qualifies",
                "execplan_condition",
                "findings",
                "open_gates",
                "evidence",
                "reason",
                "recovery",
            },
        )
        self.assertNotIn("next_action", runner.OUTPUT_SCHEMA["properties"])
        self.assertNotIn("decision", runner.OUTPUT_SCHEMA["properties"])

    def test_provider_transport_schema_inlines_refs_and_removes_unique_items(
        self,
    ) -> None:
        original = json.loads(json.dumps(runner.OUTPUT_SCHEMA))

        def key_count(value: object, target: str) -> int:
            if isinstance(value, dict):
                return sum(key == target for key in value) + sum(
                    key_count(item, target) for item in value.values()
                )
            if isinstance(value, list):
                return sum(key_count(item, target) for item in value)
            return 0

        first = runner.provider_transport_schema(runner.OUTPUT_SCHEMA)
        second = runner.provider_transport_schema(runner.OUTPUT_SCHEMA)
        self.assertGreater(key_count(runner.OUTPUT_SCHEMA, "uniqueItems"), 0)
        self.assertGreater(key_count(runner.OUTPUT_SCHEMA, "$ref"), 0)
        self.assertEqual(key_count(first, "uniqueItems"), 0)
        self.assertEqual(key_count(first, "$ref"), 0)
        self.assertEqual(
            first["properties"]["reason"],
            {"type": "string", "minLength": 1},
        )
        self.assertEqual(first, second)
        self.assertEqual(runner.OUTPUT_SCHEMA, original)
        self.assertIsNot(first, runner.OUTPUT_SCHEMA)

    def test_provider_transport_schema_rejects_unknown_and_cyclic_refs(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown"):
            runner.provider_transport_schema(
                {"$ref": "missing"},
                {"known": {"type": "string"}},
            )
        with self.assertRaisesRegex(ValueError, "cyclic"):
            runner.provider_transport_schema(
                {"$ref": "first"},
                {
                    "first": {"$ref": "second"},
                    "second": {"$ref": "first"},
                },
            )
        with self.assertRaisesRegex(ValueError, "bare reference"):
            runner.provider_transport_schema(
                {"$ref": "known", "type": "string"},
                {"known": {"type": "string"}},
            )

    def test_internal_output_validation_still_rejects_duplicate_values(
        self,
    ) -> None:
        raw = self._observation(gate="checks")
        raw["evidence"] = ["same", "same"]
        with self.assertRaises(ValueError):
            runner.validate_output_result(raw)
        raw = self._observation(
            findings=[
                self._finding("duplicate"),
                self._finding("duplicate"),
            ]
        )
        with self.assertRaises(ValueError):
            runner.validate_output_result(raw)

    def test_fresh_and_resume_argv_have_no_fake_mcp_override(self) -> None:
        config = ["-m", "gpt-5.6-sol", "-c", 'approval_policy="never"']
        for thread in (None, "thread-123"):
            with self.subTest(thread=thread):
                argv = runner.evaluator_codex_argv(
                    repo=ROOT,
                    schema=ROOT / "response-schema.json",
                    config=config,
                    prompt="probe",
                    thread=thread,
                )
                self.assertFalse(
                    any("orchestrator.mcp" in item for item in argv)
                )
                self.assertIn("apps", argv)
                self.assertIn("remote_plugin", argv)
                self.assertEqual(argv[0:2], ["codex", "exec"])
                self.assertEqual("resume" in argv, thread is not None)

    def test_real_isolated_codex_has_empty_mcp_list_and_no_apps_context(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="happycodex-mcp-probe-") as raw:
            temp = Path(raw)
            _home, env = runner.isolated_home(temp)
            binary = temp / "bin" / "codex"
            mcp_argv = [str(binary), "mcp", "list", "--json"]
            mcp = runner.run(mcp_argv, cwd=ROOT, env=env, timeout=30)
            argv = [
                str(binary),
                "debug",
                "prompt-input",
                "-c",
                'model="gpt-5.6-sol"',
                *runner.disabled_feature_args(),
                "tool-surface-probe",
            ]
            completed = runner.run(argv, cwd=ROOT, env=env, timeout=30)
        self.assertEqual(mcp.returncode, 0, mcp.stderr)
        self.assertEqual(json.loads(mcp.stdout), [])
        self.assertEqual(completed.returncode, 0, completed.stderr)
        json.loads(completed.stdout)
        self.assertNotIn("<apps_instructions>", completed.stdout)
        self.assertFalse(any("orchestrator.mcp" in item for item in argv))

    def test_dry_run_is_executable_and_has_no_model_side_effect(self) -> None:
        completed = subprocess.run(
            ["python3", "-m", "evaluation.cli", "corpus", "--dry-run"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(set(payload["cases"]), set(self.cases))
        self.assertEqual(set(payload["coverage"]), runner.REQUIRED_TAGS)

    def test_structural_schema_validates_output_case_and_recovery_parity(
        self,
    ) -> None:
        from evaluation.core.schema import load_contracts, validate_named

        contracts = load_contracts(ROOT / "evaluation" / "contracts-v7.json")
        observation = self._observation(
            recovery=self._recovery(),
            gate="checks",
        )
        self.assertEqual(
            validate_named(contracts, "model_observation", observation),
            observation,
        )
        case = self.cases["pre-freeze-compaction"]
        self.assertEqual(validate_named(contracts, "case", case), case)

    def test_structural_schema_leaves_result_and_recovery_relations_in_python(
        self,
    ) -> None:
        from evaluation.core.schema import CONTRACTS, validate_named
        from evaluation.semantic import SemanticError, parse_model_observation

        raw = self._observation(
            findings=[
                self._finding(
                    "resolved",
                    status="resolved",
                    blocker="original_goal",
                )
            ]
        )
        validate_named(CONTRACTS, "model_observation", raw)
        with self.assertRaises(SemanticError):
            parse_model_observation(raw)


if __name__ == "__main__":
    unittest.main()
