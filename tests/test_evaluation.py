from __future__ import annotations

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


def protocol_result_failures(result: dict[str, object]) -> list[str]:
    context = {
        "task_id": "case:test",
        "root_task_id": "root:test",
        "executor_task_id": "executor:test",
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
        "accepted_baseline_failures": [],
    }
    try:
        runner.protocol_result_projection(result, context=context)
    except ValueError as exc:
        return [str(exc)]
    return []


def validate_recovery_manifest(native: dict[str, object], case_id: str) -> None:
    path = ROOT / "evaluation" / "cases" / "pre-freeze-compaction.json"
    case = json.loads(path.read_text(encoding="utf-8"))
    case["fixture"]["native_compaction_resume"] = native
    runner.validate_case(case, Path(f"{case_id}.json"))


class HappyCodexEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = runner.load_cases()

    def test_batch1_direct_protocol_rejects_derived_and_contradictory_state(
        self,
    ) -> None:
        from evaluation.protocol import project_result

        result = {
            "decision": "complete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": ["offline checks passed"],
            "reason": "all direct protocol conditions are terminal",
            "recovery_state": None,
        }
        projection = project_result(
            result,
            invocation_profile_sha256="a" * 64,
            accepted_baseline_failures=[],
        )
        self.assertEqual(
            set(projection),
            {
                "schema_generation",
                "raw_result_sha256",
                "invocation_profile_sha256",
                "accepted_baseline_sha256",
                "decision",
                "qualifies",
                "execplan_condition",
                "protocol_may_product_write",
                "protocol_review_mode",
                "protocol_may_complete",
                "finding_identities_sha256",
                "blocker_identities_sha256",
                "open_gates",
                "recovery_state_sha256",
            },
        )
        self.assertNotIn("report", projection)
        self.assertNotIn("attempt_key", projection)

        derived = {**result, "next_action": "close"}
        with self.assertRaisesRegex(ValueError, "fields mismatch"):
            project_result(
                derived,
                invocation_profile_sha256="a" * 64,
                accepted_baseline_failures=[],
            )

        contradictory = json.loads(json.dumps(result))
        contradictory.update(
            decision="continue",
            protocol_may_product_write=True,
            protocol_may_complete=False,
            finding_classifications=[
                {
                    "identity": "F-RESOLVED",
                    "domain": "other",
                    "state": "resolved",
                    "anchors": ["app.py"],
                }
            ],
            blocker_classifications=[
                {
                    "identity": "F-RESOLVED",
                    "class": "safety_data_integrity",
                    "blocking": True,
                    "reason": "contradictory blocker",
                }
            ],
            open_gates=["product_edit"],
        )
        with self.assertRaisesRegex(ValueError, "contradictory"):
            project_result(
                contradictory,
                invocation_profile_sha256="a" * 64,
                accepted_baseline_failures=[],
            )

        duplicate = json.loads(json.dumps(contradictory))
        duplicate["finding_classifications"][0]["state"] = "unknown"
        duplicate["finding_classifications"].append(
            json.loads(json.dumps(duplicate["finding_classifications"][0]))
        )
        with self.assertRaisesRegex(ValueError, "duplicate finding identity"):
            project_result(
                duplicate,
                invocation_profile_sha256="a" * 64,
                accepted_baseline_failures=[],
            )

    def test_corpus_is_complete_and_bidirectional(self) -> None:
        covered = {tag for case in self.cases.values() for tag in case["covers"]}
        self.assertEqual(covered, runner.REQUIRED_TAGS)
        self.assertGreaterEqual(len(self.cases), 10)
        self.assertIn("subthreshold-control", self.cases)
        self.assertIn("clean-qualifying-control", self.cases)
        self.assertIn("review-admin-cycle", self.cases)
        self.assertIn("receipt-mismatch", self.cases)
        self.assertIn("pre-freeze-compaction", self.cases)
        self.assertIn("review-inventory-gate", self.cases)
        self.assertNotIn(
            "pre-freeze-compaction",
            self.cases["compaction-recovery"]["covers"],
        )
        goal_case = self.cases["goal-divergence"]
        goal_state = goal_case["fixture"]["commits"][0]["files"]["GOAL.md"]
        self.assertIn("Status: active", goal_state)
        self.assertIn("Automatic continuation: enabled", goal_state)
        self.assertIn(
            {
                "anchor": "GOAL.md",
                "class": ["original_goal", "frozen_acceptance"],
            },
            goal_case["oracle"]["required_anchored_blockers"],
        )

    def test_unavailable_active_goal_requires_explicit_pause_handoff(self) -> None:
        case = self.cases["goal-divergence"]
        result = {
            **{
                field: expected[0] if isinstance(expected, list) else expected
                for field, expected in case["oracle"]["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": "goal-outcome-divergence",
                    "domain": "other",
                    "state": "unknown",
                    "anchors": ["GOAL.md"],
                }
            ],
            "blocker_classifications": [
                {
                    "identity": "goal-outcome-divergence",
                    "class": "original_goal",
                    "blocking": True,
                    "reason": "The active Goal conflicts with the frozen outcome.",
                }
            ],
            "open_gates": ["user reconciliation of the active Goal"],
            "evidence": ["GOAL.md records the active divergent Goal."],
            "reason": "Stop for user reconciliation.",
            "recovery_state": None,
        }
        # The old oracle accepted this result even though the user would never learn
        # the native command that persistently stops automatic continuation.
        self.assertEqual(runner.match_oracle(result, case["oracle"]), [])
        failures = runner.match_oracle(result, case["oracle"], fixture=case["fixture"])
        self.assertTrue(any("pause handoff" in failure for failure in failures))
        result["open_gates"] = ["user_selection"]
        self.assertEqual(
            runner.match_oracle(result, case["oracle"], fixture=case["fixture"]), []
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
        permission_fields = {
            "decision",
            "qualifies",
            "execplan_condition",
            "protocol_may_product_write",
            "protocol_review_mode",
            "protocol_may_complete",
        }
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                self.assertEqual(set(case["oracle"]["expected"]), permission_fields)
                invalid = json.loads(json.dumps(case))
                del invalid["oracle"]["expected"]["protocol_review_mode"]
                with self.assertRaisesRegex(ValueError, "permission state"):
                    runner.validate_case(invalid, Path(f"{case['id']}.json"))

    def test_review_mode_is_a_two_state_clean_break(self) -> None:
        self.assertNotIn("protocol_may_review", runner.PERMISSION_FIELDS)
        self.assertIn("protocol_review_mode", runner.PERMISSION_FIELDS)
        schema = runner.OUTPUT_SCHEMA
        self.assertNotIn("protocol_may_review", schema["properties"])
        self.assertEqual(
            schema["properties"]["protocol_review_mode"]["enum"],
            ["none", "exact_final"],
        )
        self.assertIn("protocol_review_mode", schema["required"])
        recovery = schema["properties"]["recovery_state"]["properties"]
        self.assertEqual(
            recovery["milestone_phase"]["enum"],
            [
                "working",
                "candidate_frozen",
                "exact_final",
                "closed",
            ],
        )

    def test_live_projection_has_one_reducer_owned_boundary(self) -> None:
        self.assertIn("semantic reducer", runner.EVALUATOR_CONTEXT)
        self.assertIn("not authority", runner.EVALUATOR_CONTEXT)
        self.assertNotIn("PHASE_REVIEW_MODE", runner.EVALUATOR_CONTEXT)

    def test_live_projection_instructions_make_saturated_semantics_field_local(
        self,
    ) -> None:
        properties = runner.OUTPUT_SCHEMA["properties"]
        finding = properties["finding_classifications"]["items"]["properties"]
        identity = finding["identity"]
        self.assertEqual(identity, {"type": "string", "minLength": 1})
        self.assertFalse(
            properties["finding_classifications"]["items"]["additionalProperties"]
        )
        self.assertEqual(
            properties["open_gates"]["items"]["enum"],
            list(runner.RECOVERY_PENDING_GATES),
        )

    def test_projection_separates_path_anchors_from_ids_and_lifecycle_markers(
        self,
    ) -> None:
        finding = runner.OUTPUT_SCHEMA["properties"]["finding_classifications"][
            "items"
        ]["properties"]
        self.assertEqual(finding["identity"], {"type": "string", "minLength": 1})

        long_path = f"{'segment' * 12}/{'part' * 30}/file.py/{'tail' * 20}"
        self.assertEqual(finding["anchors"]["items"], {"type": "string"})
        paths = ("frontend/config.py", "backend/config.py", long_path)
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": True,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": identity,
                    "domain": "other",
                    "state": "candidate_new",
                    "anchors": [path],
                }
                for identity, path in zip(
                    ("FRONTEND-CONFIG", "BACKEND-CONFIG", "LONG-CONFIG"),
                    paths,
                    strict=True,
                )
            ],
            "blocker_classifications": [],
            "open_gates": ["product_edit"],
            "evidence": [],
            "reason": "three distinct path findings",
            "recovery_state": None,
        }
        oracle = {
            "expected": {field: result[field] for field in runner.PERMISSION_FIELDS},
            "required_anchored_classifications": [
                {"anchor": path, "domain": "other", "state": "candidate_new"}
                for path in paths
            ],
        }
        self.assertEqual(runner.match_oracle(result, oracle), [])

        exact_final = self.cases["exact-final-ready"]["oracle"]
        lifecycle = {
            **{
                field: value[0] if isinstance(value, list) else value
                for field, value in exact_final["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": "EXACT-FINAL-READY",
                    "domain": "other",
                    "state": "resolved",
                    "anchors": ["EXACT-FINAL-READY"],
                }
            ],
            "blocker_classifications": [],
            "open_gates": ["exact_final_review"],
            "evidence": ["docs/execplans/exact-final.md"],
            "reason": "lifecycle marker is ready",
            "recovery_state": None,
        }
        self.assertEqual(runner.match_oracle(lifecycle, exact_final), [])

    def test_live_oracles_follow_permission_and_classification_contracts(self) -> None:
        multi_repo = self.cases["multi-repo-submodule"]["oracle"]
        self.assertTrue(multi_repo["expected"]["protocol_may_product_write"])

        unselected = self.cases["no-commit-unselected"]["oracle"]
        self.assertEqual(unselected["expected"]["execplan_condition"], "usable")
        bare_object = next(
            finding
            for finding in unselected["required_classifications"]
            if finding["identity"] == "BARE-OBJECT-CHECKPOINT"
        )
        self.assertEqual(
            bare_object["state"],
            ["baseline_unchanged", "unknown"],
        )
        bare_object_blocker = next(
            blocker
            for blocker in unselected["required_anchored_blockers"]
            if blocker["anchor"] == "1111111111111111111111111111111111111111"
        )
        self.assertEqual(
            bare_object_blocker["class"],
            ["safety_data_integrity", "production_condition"],
        )

        sibling = next(
            blocker
            for blocker in self.cases["compaction-recovery"]["oracle"][
                "required_anchored_blockers"
            ]
            if blocker["anchor"] == "F-JOB-SIBLING-B"
        )
        self.assertEqual(
            sibling["class"],
            ["original_goal", "frozen_acceptance", "exhaustive_claim"],
        )

    def test_remaining_markers_and_dirty_paths_have_anchored_classifications(
        self,
    ) -> None:
        expected = {
            "no-commit-archive-recovery": {
                ("ARCHIVE-RECOVERY-VALID", "receipt", ("resolved",))
            },
            "pre-freeze-compaction": {
                ("RECOVERY-GIT-6D91", "receipt", ("resolved",)),
                ("RECOVERY-PLAN-47B2", "receipt", ("resolved",)),
                ("RECOVERY-TEST-19C4", "receipt", ("resolved",)),
            },
            "midflight-escalation": {("lib.py", "other", ("candidate_new", "unknown"))},
            "no-commit-secret": {
                ("product.cfg", "secret", ("baseline_unchanged",)),
                ("scan.txt", "secret", ("candidate_new", "unknown")),
            },
        }
        for case_id, required in expected.items():
            actual = set()
            for item in self.cases[case_id]["oracle"].get(
                "required_anchored_classifications", []
            ):
                states = item["state"]
                actual.add(
                    (
                        item["anchor"],
                        item["domain"],
                        tuple(states if isinstance(states, list) else [states]),
                    )
                )
            with self.subTest(case=case_id):
                self.assertTrue(required.issubset(actual))

        case = self.cases["pre-freeze-compaction"]
        result = {
            **{
                field: value[0] if isinstance(value, list) else value
                for field, value in case["oracle"]["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": f"MODEL:{marker}",
                    "domain": "receipt",
                    "state": "resolved",
                    "anchors": [marker],
                }
                for marker in (
                    "RECOVERY-MANIFEST-SHA256:"
                    "1621ab9f934155f63aa3ce897065854e67805de0e38359e6451fa2e947ad5308",
                    "RECOVERY-GIT-6D91",
                    "RECOVERY-PLAN-47B2",
                    "RECOVERY-TEST-19C4",
                )
            ],
            "blocker_classifications": [],
            "open_gates": ["contract_freeze"],
            "evidence": ["durable recovery facts"],
            "reason": "read-only recovery",
            "recovery_state": None,
        }
        self.assertEqual(runner.match_oracle(result, case["oracle"]), [])
        for index in range(4):
            missing = json.loads(json.dumps(result))
            del missing["finding_classifications"][index]
            self.assertTrue(
                any(
                    "missing anchored classification" in failure
                    for failure in runner.match_oracle(missing, case["oracle"])
                )
            )

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

    def test_live_oracle_alternatives_cannot_authorize_user_gated_writes(self) -> None:
        case = self.cases["multi-repo-submodule"]
        result = {
            **{
                field: (allowed[0] if isinstance(allowed, list) else allowed)
                for field, allowed in case["oracle"]["expected"].items()
            },
            "decision": "stop_for_user",
            "execplan_condition": "needs_amendment",
            "protocol_may_product_write": True,
            "finding_classifications": [
                {
                    "identity": "submodule-scope",
                    "domain": "other",
                    "state": "candidate_new",
                    "anchors": ["backend/shared-schema.pointer"],
                },
                {
                    "identity": "multi-repo-scope",
                    "domain": "receipt",
                    "state": "candidate_new",
                    "anchors": ["docs/execplans/contracts.md"],
                },
            ],
            "blocker_classifications": [
                {
                    "identity": "submodule-scope",
                    "class": "original_goal",
                    "blocking": True,
                    "reason": "missing dependency content",
                },
                {
                    "identity": "multi-repo-scope",
                    "class": "exhaustive_claim",
                    "blocking": True,
                    "reason": "colliding repository projection",
                },
            ],
            "open_gates": ["user_selection"],
            "evidence": [],
            "reason": "a user gate remains open",
            "recovery_state": None,
        }
        failures = runner.match_oracle(result, case["oracle"])
        self.assertTrue(failures)

        recovery_gated = {
            **result,
            "decision": "continue",
            "execplan_condition": "usable",
            "protocol_review_mode": "none",
            "recovery_state": {
                "baseline_revision": "1" * 40,
                "baseline_tree": "2" * 40,
                "current_revision": "3" * 40,
                "current_tree": "4" * 40,
                "writer": "Root",
                "milestone_phase": "implementation",
                "next_action": "ask_user",
                "pending_gates": ["user_selection"],
                "tests": {
                    "passed": 0,
                    "failed": 0,
                    "accepted_failures": 0,
                    "marker_ids": [],
                },
                "worktree": "clean",
                "live_agents": [],
                "marker_ids": [],
            },
        }
        failures = protocol_result_failures(recovery_gated)
        self.assertTrue(failures)

    def test_required_anchor_members_and_items_are_distinct(self) -> None:
        oracle = {
            "expected": {"protocol_may_complete": False},
            "required_anchored_classifications": [
                {
                    "anchor": "src/job.py",
                    "domain": "other",
                    "state": "unknown",
                },
                {
                    "anchor": "staged-review.txt",
                    "domain": "other",
                    "state": "unknown",
                },
            ],
        }
        collapsed = {
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "ALL-RECOVERY-PATHS",
                    "domain": "other",
                    "state": "unknown",
                    "anchors": ["src/job.py", "staged-review.txt"],
                }
            ],
            "blocker_classifications": [],
        }
        failures = runner.match_oracle(collapsed, oracle)
        self.assertTrue(
            any("distinct anchored classification" in item for item in failures)
        )
        duplicated = json.loads(json.dumps(collapsed))
        duplicated["finding_classifications"].append(
            json.loads(json.dumps(duplicated["finding_classifications"][0]))
        )
        failures = runner.match_oracle(duplicated, oracle)
        self.assertTrue(
            any("distinct anchored classification" in item for item in failures)
        )

    def test_resolved_finding_cannot_remain_blocking(self) -> None:
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": True,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "multi-repo-scope",
                    "domain": "receipt",
                    "state": "resolved",
                    "anchors": ["docs/execplans/contracts.md"],
                }
            ],
            "blocker_classifications": [
                {
                    "identity": "multi-repo-scope",
                    "class": "exhaustive_claim",
                    "blocking": True,
                    "reason": "contradictory resolved blocker",
                }
            ],
            "open_gates": ["product_edit"],
            "evidence": [],
            "reason": "false green",
            "recovery_state": None,
        }
        failures = protocol_result_failures(result)
        self.assertTrue(failures)

        aliased = json.loads(json.dumps(result))
        aliased["finding_classifications"][0]["identity"] = "MODEL:multi-repo-scope"
        failures = protocol_result_failures(aliased)
        self.assertFalse(any("resolved finding is blocking" in item for item in failures))
        self.assertTrue(any("exact finding" in item for item in failures))

    def test_case_validation_rejects_invalid_permission_states(self) -> None:
        case = json.loads(json.dumps(self.cases["clean-qualifying-control"]))
        case["oracle"]["expected"]["protocol_review_mode"] = "bogus"
        with self.assertRaisesRegex(ValueError, "permission state"):
            runner.validate_case(case, Path("bogus-review-mode.json"))

        case = json.loads(json.dumps(self.cases["clean-qualifying-control"]))
        case["oracle"]["expected"]["protocol_review_mode"] = "exact_final"
        case["oracle"]["expected"]["protocol_may_product_write"] = True
        runner.validate_case(case, Path("exact-final-write.json"))

        contradictions = (
            ("complete-without-permission", "complete", False, False),
            ("permission-without-complete", "continue", True, False),
            ("complete-with-active-write", "complete", True, True),
        )
        for name, decision, may_complete, may_write in contradictions:
            with self.subTest(state=name):
                case = json.loads(json.dumps(self.cases["clean-qualifying-control"]))
                case["oracle"]["expected"].update(
                    {
                        "decision": decision,
                        "protocol_may_complete": may_complete,
                        "protocol_may_product_write": may_write,
                    }
                )
                runner.validate_case(case, Path(f"{name}.json"))

    def test_case_validation_rejects_blank_expected_identities(self) -> None:
        invalid_oracles = (
            {"accepted_baseline_failures": [" \t "]},
            {
                "required_classifications": [
                    {"identity": " \t ", "domain": "other", "state": "resolved"}
                ]
            },
            {
                "required_blocker_classifications": [
                    {"identity": " \t ", "class": "original_goal"}
                ]
            },
        )
        for index, invalid_oracle in enumerate(invalid_oracles):
            with self.subTest(oracle=next(iter(invalid_oracle))):
                case = json.loads(json.dumps(self.cases["clean-qualifying-control"]))
                case["oracle"].update(invalid_oracle)
                with self.assertRaisesRegex(ValueError, "invalid"):
                    runner.validate_case(case, Path(f"blank-identity-{index}.json"))

    def test_shared_constraint_rejects_contradictory_completion_receipts(self) -> None:
        base = self.cases["clean-qualifying-control"]["oracle"]["expected"]
        contradictions = (
            ("complete", False, False),
            ("continue", True, False),
            ("complete", True, True),
        )
        for decision, may_complete, may_write in contradictions:
            with self.subTest(
                decision=decision,
                may_complete=may_complete,
                may_write=may_write,
            ):
                result = {
                    **base,
                    "decision": decision,
                    "protocol_may_complete": may_complete,
                    "protocol_may_product_write": may_write,
                    "finding_classifications": [],
                    "blocker_classifications": [],
                    "open_gates": [],
                    "evidence": [],
                    "reason": "",
                    "recovery_state": None,
                }
                self.assertTrue(protocol_result_failures(result))

    def test_fixed_convergence_cases_mechanically_bind_new_behavior(self) -> None:
        exact = self.cases["exact-final-ready"]
        self.assertEqual(
            exact["oracle"]["expected"]["protocol_review_mode"], "exact_final"
        )
        self.assertFalse(exact["oracle"]["expected"]["protocol_may_product_write"])
        self.assertFalse(exact["oracle"]["expected"]["protocol_may_complete"])

        overlap = self.cases["boundary-cutover"]
        self.assertIn(
            {
                "anchor": "RESOURCE-OVERLAP",
                "class": "safety_data_integrity",
            },
            overlap["oracle"]["required_anchored_blockers"],
        )
        disjoint = self.cases["clean-qualifying-control"]
        self.assertIn(
            {
                "identity": "RESOURCE-DISJOINT-OK",
                "domain": "other",
                "state": "resolved",
            },
            disjoint["oracle"]["required_classifications"],
        )

        family = self.cases["compaction-recovery"]
        self.assertIn(
            {
                "anchor": "F-JOB-SIBLING-B",
                "class": [
                    "original_goal",
                    "frozen_acceptance",
                    "exhaustive_claim",
                ],
            },
            family["oracle"]["required_anchored_blockers"],
        )
        for identity in ("F-DEFAULT-SIBLING-A", "F-DEFAULT-SIBLING-B"):
            self.assertIn(
                {
                    "identity": identity,
                    "domain": "other",
                    "state": "resolved",
                },
                disjoint["oracle"]["required_classifications"],
            )

        valid_archive = self.cases["no-commit-archive-recovery"]
        self.assertEqual(valid_archive["oracle"]["expected"]["decision"], "continue")
        self.assertTrue(
            valid_archive["oracle"]["expected"]["protocol_may_product_write"]
        )
        tampered = self.cases["no-commit-secret"]
        self.assertIn(
            {
                "anchor": "archive/checkpoint.txt",
                "class": "safety_data_integrity",
            },
            tampered["oracle"]["required_anchored_blockers"],
        )
        unselected = self.cases["no-commit-unselected"]
        self.assertIn(
            {
                "anchor": "1111111111111111111111111111111111111111",
                "class": ["safety_data_integrity", "production_condition"],
            },
            unselected["oracle"]["required_anchored_blockers"],
        )

        phases = []
        for commit in self.cases["review-admin-cycle"]["fixture"]["commits"]:
            for content in commit.get("files", {}).values():
                if isinstance(content, str):
                    phases.extend(
                        line.removeprefix("State: ").split(";", 1)[0]
                        for line in content.splitlines()
                        if line.startswith("State: ")
                    )
        self.assertEqual(
            phases,
            [
                "implementation",
                "implementation",
                "focused_hardening",
                "candidate_frozen",
                "exact_final",
                "closed",
            ],
        )

    def test_review_mode_and_recovery_phase_form_one_state_machine(self) -> None:
        recovery = {
            "baseline_revision": "1" * 40,
            "baseline_tree": "2" * 40,
            "current_revision": "3" * 40,
            "current_tree": "4" * 40,
            "writer": "Root",
            "milestone_phase": "closed",
            "next_action": "none",
            "pending_gates": [],
            "tests": {
                "passed": 1,
                "failed": 0,
                "accepted_failures": 0,
                "marker_ids": [],
            },
            "worktree": "clean",
            "live_agents": [],
            "marker_ids": [RECOVERY_MANIFEST_MARKER],
        }
        closed = {
            "decision": "complete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": ["exact-final review and administrative closure"],
            "reason": "The task is closed.",
            "recovery_state": recovery,
        }
        nonterminal = (
            (
                "implementation",
                "implementation",
                "none",
                True,
                "implement",
                ["product_edit"],
            ),
            (
                "focused-repair",
                "focused_hardening",
                "none",
                True,
                "repair",
                ["product_edit"],
            ),
            (
                "focused-review",
                "focused_hardening",
                "focused_hardening",
                False,
                "focused_review",
                ["focused_review"],
            ),
            (
                "candidate-frozen",
                "candidate_frozen",
                "none",
                False,
                "freeze_candidate",
                ["candidate_freeze"],
            ),
            (
                "exact-final",
                "exact_final",
                "exact_final",
                False,
                "exact_final_review",
                ["exact_final_review"],
            ),
        )
        for label, phase, mode, may_write, next_action, pending in nonterminal:
            with self.subTest(state=label):
                result = {
                    **closed,
                    "decision": "continue",
                    "protocol_may_product_write": may_write,
                    "protocol_review_mode": mode,
                    "protocol_may_complete": False,
                    "open_gates": pending,
                    "recovery_state": {
                        **recovery,
                        "milestone_phase": phase,
                        "next_action": next_action,
                        "pending_gates": pending,
                    },
                }
                oracle = {
                    "expected": {
                        field: result[field] for field in runner.PERMISSION_FIELDS
                    }
                }
                self.assertEqual(runner.match_oracle(result, oracle), [])
                result["protocol_review_mode"] = (
                    "focused_hardening" if mode == "none" else "none"
                )
                self.assertTrue(runner.match_oracle(result, oracle))

        contradictory = {
            **closed,
            "decision": "continue",
            "protocol_may_product_write": True,
            "protocol_review_mode": "exact_final",
            "protocol_may_complete": False,
            "open_gates": ["product_edit"],
            "recovery_state": {
                **recovery,
                "milestone_phase": "implementation",
                "next_action": "implement",
                "pending_gates": ["product_edit"],
            },
        }
        oracle = {
            "expected": {
                field: contradictory[field] for field in runner.PERMISSION_FIELDS
            }
        }
        self.assertTrue(
            protocol_result_failures(contradictory)
        )

    def test_receipt_projection_binds_review_mode_without_alias(self) -> None:
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "exact_final",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": ["exact_final_review"],
            "evidence": ["focused counterexample replay"],
            "reason": "The terminal GREEN wave permits one focused review.",
            "recovery_state": None,
        }
        receipt = receipt_engine.sanitized_result_receipt(result)
        self.assertEqual(receipt["protocol_review_mode"], "exact_final")
        self.assertNotIn("protocol_may_review", receipt)

    def test_open_family_cannot_masquerade_as_exact_final(self) -> None:
        sibling_findings = [
            {
                "identity": "F-SNAPSHOT-1",
                "domain": "other",
                "state": "candidate_new",
            },
            {
                "identity": "F-MANIFEST-1",
                "domain": "other",
                "state": "unknown",
            },
            {
                "identity": "F-ACTOR-RECEIPT-1",
                "domain": "receipt",
                "state": "candidate_new",
            },
            {
                "identity": "F-IDENTITY-1",
                "domain": "other",
                "state": "candidate_new",
            },
        ]
        oracle = {
            "expected": {
                "decision": "continue",
                "qualifies": True,
                "execplan_condition": "usable",
                "protocol_may_product_write": True,
                "protocol_review_mode": "none",
                "protocol_may_complete": False,
            },
            "required_classifications": sibling_findings,
            "required_anchored_blockers": [
                {
                    "anchor": "F-MANIFEST-1",
                    "class": "safety_data_integrity",
                }
            ],
        }
        result = {
            **oracle["expected"],
            "finding_classifications": [
                {
                    "identity": item["identity"],
                    "domain": item["domain"],
                    "state": item["state"],
                    "anchors": [item["identity"]],
                }
                for item in sibling_findings
            ],
            "blocker_classifications": [
                {
                    "identity": "F-MANIFEST-1",
                    "class": "safety_data_integrity",
                    "blocking": True,
                    "reason": "Nested manifest aliasing remains an unknown integrity risk.",
                }
            ],
            "open_gates": ["family_hardening"],
            "evidence": ["docs/execplans/evidence-hardening.md"],
            "reason": "The open family is in focused hardening.",
            "recovery_state": None,
        }
        self.assertEqual(runner.match_oracle(result, oracle), [])
        result["protocol_review_mode"] = "exact_final"
        self.assertTrue(
            any(
                "protocol_review_mode" in failure or "exact_final" in failure
                for failure in runner.match_oracle(result, oracle)
            )
        )

    def test_review_write_and_stop_for_user_are_mechanically_exclusive(self) -> None:
        base = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "exact_final",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": ["exact_final_review"],
            "evidence": ["terminal GREEN repair-wave receipt"],
            "reason": "Focused review is the only next gate.",
            "recovery_state": None,
        }
        self.assertEqual(protocol_result_failures(base), [])

        review_and_write = {**base, "protocol_may_product_write": True}
        self.assertTrue(protocol_result_failures(review_and_write))

        stopped = {
            **base,
            "decision": "stop_for_user",
            "protocol_review_mode": "exact_final",
        }
        self.assertTrue(protocol_result_failures(stopped))

    def test_unusable_execplan_cannot_review_or_complete_without_recovery(self) -> None:
        base = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "missing",
            "protocol_may_product_write": False,
            "protocol_review_mode": "focused_hardening",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": ["focused_review"],
            "evidence": [],
            "reason": "The plan is absent.",
            "recovery_state": None,
        }
        self.assertTrue(protocol_result_failures(base))
        completing = {
            **base,
            "decision": "complete",
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
        }
        self.assertTrue(protocol_result_failures(completing))

    def test_exact_final_rejects_open_findings_blockers_and_repair_gates(self) -> None:
        active = {
            "identity": "F-CONV-OPEN",
            "domain": "other",
            "state": "unknown",
            "anchors": ["F-CONV-OPEN"],
        }
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "exact_final",
            "protocol_may_complete": False,
            "finding_classifications": [active],
            "blocker_classifications": [
                {
                    "identity": "F-CONV-OPEN",
                    "class": "safety_data_integrity",
                    "blocking": True,
                    "reason": "The recovery boundary is still unknown.",
                }
            ],
            "open_gates": ["exact_final_review"],
            "evidence": [],
            "reason": "Invalid exact-final launch.",
            "recovery_state": None,
        }
        failures = protocol_result_failures(result)
        self.assertTrue(failures)
        self.assertTrue(any("direct result state" in failure for failure in failures))

    def test_every_blocker_must_match_exactly_one_finding(self) -> None:
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": True,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [
                {
                    "identity": "ORPHAN-BLOCKER",
                    "class": "original_goal",
                    "blocking": True,
                    "reason": "No finding owns this blocker.",
                }
            ],
            "open_gates": ["product_edit"],
            "evidence": [],
            "reason": "Invalid classification graph.",
            "recovery_state": None,
        }
        self.assertTrue(
            any(
                "exact finding" in failure
                for failure in protocol_result_failures(result)
            )
        )

    def test_recovery_facts_and_content_addressed_manifest_fail_closed(self) -> None:
        recovery = {
            "baseline_revision": "1" * 40,
            "baseline_tree": "2" * 40,
            "current_revision": "3" * 40,
            "current_tree": "4" * 40,
            "writer": "Root",
            "milestone_phase": "working",
            "next_action": "implement",
            "pending_gates": ["product_edit"],
            "tests": {
                "passed": 4,
                "failed": 0,
                "accepted_failures": 0,
                "marker_ids": [],
            },
            "worktree": "clean",
            "live_agents": [],
            "marker_ids": [RECOVERY_MANIFEST_MARKER],
        }
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": True,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": ["product_edit"],
            "evidence": ["Recovery Manifest"],
            "reason": "Resume the bounded repair.",
            "recovery_state": recovery,
        }
        self.assertEqual(protocol_result_failures(result), [])
        receipt = receipt_engine.sanitized_result_receipt(result)
        self.assertEqual(
            receipt["recovery_state"]["recovery_manifest_sha256"],
            "a" * 64,
        )

        mutations = {
            "unknown writer": lambda state: state.update(writer="unknown"),
            "unknown worktree": lambda state: state.update(worktree="unknown"),
            "missing agent": lambda state: state.update(
                live_agents=[
                    {
                        "id": "review-1",
                        "status": "missing",
                        "receipt_reproduced": False,
                    }
                ]
            ),
            "unaccepted failure": lambda state: state["tests"].update(
                failed=1, accepted_failures=0
            ),
            "missing Recovery Manifest": lambda state: state.update(marker_ids=[]),
            "duplicate Recovery Manifest": lambda state: state.update(
                marker_ids=[RECOVERY_MANIFEST_MARKER, RECOVERY_MANIFEST_MARKER]
            ),
        }
        for expected, mutate in mutations.items():
            with self.subTest(expected=expected):
                invalid = json.loads(json.dumps(result))
                mutate(invalid["recovery_state"])
                self.assertTrue(protocol_result_failures(invalid), expected)

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
        from evaluation.core.schema import load_contracts, validate_named

        contracts = load_contracts(ROOT / "evaluation" / "contracts-v6.json")
        native = self.cases["pre-freeze-compaction"]["fixture"][
            "native_compaction_resume"
        ]
        manifest = json.loads(
            native["post_compaction_transition"]["files"][
                "docs/execplans/recovery-manifest.json"
            ]
        )
        manifest.pop("convergence", None)
        self.assertEqual(
            validate_named(contracts, "recovery_manifest", manifest),
            manifest,
        )
        for field, value in (
            ("convergence", {"phase": "working", "families": []}),
            ("family", "F-QUEUE"),
            ("family_id", "F-QUEUE"),
            ("status", "open"),
            ("repair_batch", "RB-QUEUE/boundary"),
            ("recurrence", 1),
        ):
            invalid = json.loads(json.dumps(manifest))
            invalid[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "schema object mismatch"
            ):
                validate_named(contracts, "recovery_manifest", invalid)

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

    def test_pre_freeze_fixture_has_committed_skeleton_and_pending_gates(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            case = self.cases["pre-freeze-compaction"]
            facts = runner.build_fixture(case, repo)
            plan = (repo / "docs/execplans/queue-migration.md").read_text()
            self.assertEqual(len(facts["commits"]), 2)
            self.assertIn("State: implementation", plan)
            self.assertIn(facts["commits"][0], plan)
            self.assertIn(facts["trees"][0], plan)
            self.assertIn("Boundary inventory: open", plan)
            self.assertIn("BC-4: pending", plan)
            self.assertEqual(facts["status_before"], "")
            native = case["fixture"]["native_compaction_resume"]
            self.assertIn("$happycodex:happycodex", native["prepare_prompt"])
            self.assertIn("$happycodex:happycodex", native["fresh_recovery_prompt"])
            self.assertIn(
                "no prior conversation summary or task handle",
                native["fresh_recovery_prompt"],
            )
            self.assertIn(
                "runner's native compaction recovery control",
                native["fresh_recovery_prompt"],
            )
            self.assertIn(
                "full structured recovery_state", native["fresh_recovery_prompt"]
            )
            self.assertEqual(native["auto_compact_token_limit"], 1_000)
            self.assertIn("post_compaction_transition", native)
            transition = native["post_compaction_transition"]
            self.assertIn("RECOVERY-PLAN-47B2", str(transition))
            self.assertIn("RECOVERY-TEST-19C4", str(transition))
            self.assertTrue(callable(runner.apply_post_compaction_transition))
            self.assertTrue(callable(runner.recovery_control_failures))

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

    def test_recovery_control_requires_distinct_task_and_equivalent_gates(self) -> None:
        primary = {
            field: value
            for field, value in self.cases["pre-freeze-compaction"]["oracle"][
                "expected"
            ].items()
        }
        primary["decision"] = "continue"
        primary["execplan_condition"] = "usable"
        fresh = {
            **primary,
            "decision": "incomplete",
            "execplan_condition": "needs_amendment",
        }
        self.assertEqual(
            runner.recovery_control_failures(
                primary=primary,
                primary_thread_id="same-task",
                fresh=fresh,
                fresh_thread_id="fresh-task",
            ),
            [],
        )
        self.assertTrue(
            runner.recovery_control_failures(
                primary=primary,
                primary_thread_id="same-task",
                fresh={**primary, "protocol_may_product_write": True},
                fresh_thread_id="same-task",
            )
        )

    def test_recovery_control_rejects_equal_but_false_durable_state(self) -> None:
        expected = {
            "baseline_revision": "1" * 40,
            "baseline_tree": "2" * 40,
            "current_revision": "3" * 40,
            "current_tree": "4" * 40,
            "writer": "Root",
            "milestone_phase": "boundary_union_reproduced",
            "next_action": "create_contract_freeze_revision",
            "pending_gates": ["contract_freeze", "red_oracle", "product_edit"],
            "tests": {
                "passed": 19,
                "failed": 0,
                "accepted_failures": 0,
                "marker_ids": ["RECOVERY-TEST-19C4"],
            },
            "worktree": "clean",
            "live_agents": [
                {
                    "id": "BC-4",
                    "status": "terminal",
                    "receipt_reproduced": True,
                }
            ],
            "marker_ids": [
                "RECOVERY-GIT-6D91",
                "RECOVERY-PLAN-47B2",
                "RECOVERY-TEST-19C4",
            ],
        }
        wrong = {**expected, "baseline_revision": "9" * 40}
        primary = {
            **self.cases["pre-freeze-compaction"]["oracle"]["expected"],
            "decision": "continue",
            "execplan_condition": "usable",
            "recovery_state": wrong,
        }
        fresh = {
            **primary,
            "decision": "incomplete",
            "execplan_condition": "needs_amendment",
        }
        failures = runner.recovery_control_failures(
            primary=primary,
            primary_thread_id="resumed-task",
            fresh=fresh,
            fresh_thread_id="fresh-task",
            expected_state=expected,
        )
        self.assertTrue(any("baseline_revision" in item for item in failures))

        reordered = json.loads(json.dumps(expected))
        reordered["marker_ids"].reverse()
        reordered["tests"]["marker_ids"].reverse()
        reordered["live_agents"].reverse()
        self.assertEqual(
            runner.recovery_state_failures("recovery_state", reordered, expected),
            [],
        )
        misplaced = json.loads(json.dumps(expected))
        misplaced["live_agents"] = []
        misplaced["marker_ids"].append("BC-4")
        misplaced_failures = runner.recovery_state_failures(
            "recovery_state", misplaced, expected
        )
        self.assertTrue(any("live_agents" in item for item in misplaced_failures))
        self.assertTrue(any("marker_ids" in item for item in misplaced_failures))

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
        result = {
            "case": "fixture",
            "passed": False,
            "model": "gpt-5.6-sol",
            "effort": "high",
            "timeout_seconds": 300,
            "timed_out": False,
            "elapsed_seconds": 1.25,
            "exit_code": 0,
            "thread_id": "thread-1",
            "resume_thread_id": None,
            "fresh_recovery_thread_id": None,
            "semantic_input_sha256": "a" * 64,
            "invocation_profile": runner.invocation_profile(
                model="gpt-5.6-sol",
                effort="high",
                timeout_seconds=300,
                arm="candidate",
            ),
            "accepted_baseline_failures": [],
            "identities": {
                "engine": {"manifest_sha256": "1" * 64},
                "package": {
                    "semantic_sha256": "2" * 64,
                    "artifact_sha256": "3" * 64,
                },
                "codex": {
                    "sha256": "4" * 64,
                    "version": "codex-cli 0.145.0",
                },
            },
            "events_sha256": "b" * 64,
            "stderr_sha256": "c" * 64,
            "filesystem_isolation": {"default_access": "deny"},
            "installation": {
                "source_skill_sha256": "d" * 64,
                "installed_skill_sha256": "d" * 64,
                "source_package_manifest_sha256": "e" * 64,
                "installed_package_manifest_sha256": "e" * 64,
                "isolated_home": "/tmp/secret-home",
            },
            "usage": {
                "input_tokens": 12,
                "cached_input_tokens": 5,
                "output_tokens": 3,
            },
            "usage_phases": [
                {"input_tokens": 12, "cached_input_tokens": 5, "output_tokens": 3}
            ],
            "uncached_input_tokens": 7,
            "result": {
                "decision": "incomplete",
                "qualifies": True,
                "execplan_condition": "needs_amendment",
                "protocol_may_product_write": False,
                "protocol_review_mode": "none",
                "protocol_may_complete": False,
                "finding_classifications": [
                    {
                        "identity": "SECRET-CANARY-VALUE:/tmp/private/finding",
                        "domain": "other",
                        "state": "unknown",
                        "anchors": ["SECRET-CANARY-VALUE:/tmp/private/anchor"],
                    }
                ],
                "blocker_classifications": [
                    {
                        "identity": "SECRET-CANARY-VALUE:/tmp/private/finding",
                        "class": "frozen_acceptance",
                        "blocking": True,
                        "reason": "SECRET-CANARY-VALUE /tmp/private/reason",
                    }
                ],
                "open_gates": ["reconciliation"],
                "evidence": ["SECRET-CANARY-VALUE /tmp/private/evidence"],
                "reason": "SECRET-CANARY-VALUE /tmp/private/model-prose",
                "recovery_state": {
                    "baseline_revision": "1" * 40,
                    "baseline_tree": "2" * 40,
                    "current_revision": "3" * 40,
                    "current_tree": "4" * 40,
                    "writer": "Root",
                    "milestone_phase": "exact_final",
                    "next_action": "exact_final_review",
                    "pending_gates": ["exact_final_review"],
                    "tests": {
                        "passed": 1,
                        "failed": 0,
                        "accepted_failures": 0,
                        "marker_ids": ["SECRET-CANARY-VALUE:/tmp/private/test"],
                    },
                    "worktree": "clean",
                    "live_agents": [
                        {
                            "id": "SECRET-CANARY-VALUE:/tmp/private/agent",
                            "status": "terminal",
                            "receipt_reproduced": True,
                        }
                    ],
                    "marker_ids": [
                        "SECRET-CANARY-VALUE:/tmp/private/marker",
                        "SECRET-CANARY-VALUE:/tmp/private/test",
                        RECOVERY_MANIFEST_MARKER,
                    ],
                },
            },
            "fresh_recovery_result": None,
            "fresh_recovery_protocol_result": None,
            "terminal_projections": [],
            "oracle_failures": ["SECRET-CANARY-VALUE /tmp/private/mismatch"],
            "native_compaction": {
                "compaction_event_count": 1,
                "resumed_same_thread": True,
                "before_resume": {
                    "rollout_path": "SECRET-CANARY-VALUE/tmp/private/rollout.jsonl",
                    "rollout_sha256": "9" * 64,
                    "rollout_byte_count": 128,
                    "rollout_prefix_sha256": None,
                    "compaction_event_count": 1,
                    "context_compacted_marker_count": 1,
                    "event_types": ["compacted"],
                    "rollout_match_count": 1,
                },
                "after_resume": {
                    "rollout_path": "SECRET-CANARY-VALUE/tmp/private/rollout.jsonl",
                    "rollout_sha256": "8" * 64,
                    "rollout_byte_count": 256,
                    "rollout_prefix_sha256": "9" * 64,
                    "compaction_event_count": 1,
                    "context_compacted_marker_count": 1,
                    "event_types": ["compacted"],
                    "rollout_match_count": 1,
                },
                "post_compaction_transition": {
                    "message": "SECRET-CANARY-VALUE /tmp/private/transition"
                },
            },
        }
        result["protocol_result"] = runner.protocol_result_projection(
            result["result"],
            context={
                "task_id": "case:sanitizer",
                "root_task_id": "root:evaluator",
                "executor_task_id": "executor:evaluator",
                "owner_label": "happycodex-evaluator",
                "destination_id": "repository:happycodex",
                "lineage_digest": "a" * 64,
                "role_config_digest": "b" * 64,
                "repository_digest": "c" * 64,
                "outcome_digest": "d" * 64,
                "invocation_profile": result["invocation_profile"],
                "accepted_baseline_failures": [],
            },
        )
        receipt = receipt_engine.sanitized_case_receipt(
            result, metadata_sha256="f" * 64
        )
        for key in (
            "metadata_sha256",
            "model",
            "effort",
            "timeout_seconds",
            "filesystem_isolation",
            "installation",
            "usage",
            "usage_phases",
            "result",
            "oracle_failures_sha256",
            "native_compaction",
        ):
            self.assertIn(key, receipt)
        rendered = json.dumps(receipt, sort_keys=True)
        self.assertNotIn("SECRET-CANARY-VALUE", rendered)
        self.assertNotIn("/tmp/", rendered)
        self.assertNotIn("isolated_home", rendered)
        self.assertNotIn("toolchain", rendered)
        self.assertNotIn('"path"', rendered)
        self.assertEqual(
            set(receipt["identities"]["codex"]),
            {"sha256", "version"},
        )
        self.assertEqual(receipt["result"]["decision"], "incomplete")
        self.assertIs(receipt["result"]["goal_pause_handoff_present"], False)
        self.assertIn(
            "identity_sha256", receipt["result"]["finding_classifications"][0]
        )
        self.assertNotIn(
            "identity_match_sha256s",
            receipt["result"]["finding_classifications"][0],
        )
        self.assertNotIn(
            "identity_casefold_sha256",
            receipt["result"]["finding_classifications"][0],
        )
        self.assertIn("reason_sha256", receipt["result"]["blocker_classifications"][0])
        self.assertNotIn(
            "identity_match_sha256s",
            receipt["result"]["blocker_classifications"][0],
        )
        self.assertIn("anchors_sha256", receipt["result"]["finding_classifications"][0])
        before = receipt["native_compaction"]["before_resume"]
        after = receipt["native_compaction"]["after_resume"]
        self.assertEqual(before["rollout_byte_count"], 128)
        self.assertIsNone(before["rollout_prefix_sha256"])
        self.assertEqual(after["rollout_byte_count"], 256)
        self.assertEqual(after["rollout_prefix_sha256"], before["rollout_sha256"])

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
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                self.assertNotIn("required_term_groups", case["oracle"])
        case = self.cases["clean-qualifying-control"]
        result = {
            **case["oracle"]["expected"],
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": ["product_edit"],
            "evidence": [],
            "reason": "",
            "recovery_state": None,
        }
        failures = runner.match_oracle(result, case["oracle"])
        self.assertTrue(
            any("missing classification" in failure for failure in failures)
        )
        self.assertTrue(
            any("missing anchored classification" in failure for failure in failures)
        )
        result["finding_classifications"] = [
            {
                "identity": expected["identity"],
                "domain": expected["domain"],
                "state": expected["state"],
                "anchors": [expected["identity"], ".work/plans/default-limit.md"],
            }
            for expected in case["oracle"]["required_classifications"]
        ]
        self.assertEqual(runner.match_oracle(result, case["oracle"]), [])

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
        excluded = "docs/execplans/greeting.md"
        self.assertTrue(
            self.cases["review-admin-cycle"]["oracle"]["expected"]["qualifies"]
        )
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            facts = runner.build_fixture(self.cases["review-admin-cycle"], repo)
            fixture_commits = self.cases["review-admin-cycle"]["fixture"]["commits"]
            self.assertEqual(len(fixture_commits), 8)
            self.assertNotIn("review_projection", fixture_commits[5])
            self.assertIn("review_projection", fixture_commits[6])
            self.assertNotIn("review_projection", fixture_commits[7])
            self.assertEqual(len(facts["commits"]), 8)
            self.assertIn(
                "public api contract",
                (repo / "PUBLIC_CONTRACT.md").read_text().casefold(),
            )
            self.assertEqual(
                git(repo, "diff", "--name-only", "HEAD^", "HEAD"), excluded
            )
            self.assertEqual(
                product_entries(repo, "HEAD^", excluded),
                product_entries(repo, "HEAD", excluded),
            )
            self.assertEqual(git(repo, "status", "--porcelain=v1"), "")
            plan = (repo / excluded).read_text()
            self.assertIn(facts["product_manifest_sha256"][-2], plan)
            projection = facts["review_projections"][0]
            challenger = facts["challenger_receipts"][0]
            self.assertEqual(challenger["created_after_commit_index"], 2)
            self.assertEqual(challenger["terminal_record"], facts["commits"][2])
            self.assertLess(challenger["created_after_commit_index"], 3)
            self.assertEqual(projection["challenger_blob"], challenger["blob"])
            skeleton = git(repo, "show", f"{facts['commits'][1]}:{excluded}")
            contract = git(repo, "show", f"{facts['commits'][2]}:{excluded}")
            focused = git(repo, "show", f"{facts['commits'][4]}:{excluded}")
            prelaunch = git(repo, "show", f"{facts['commits'][5]}:{excluded}")
            exact_final = git(repo, "show", f"{facts['commits'][6]}:{excluded}")
            self.assertIn("State: implementation", skeleton)
            self.assertIn("boundary-challenger-9: pending", skeleton)
            self.assertIn("State: implementation", contract)
            self.assertIn("boundary-challenger-9: terminal complete", contract)
            self.assertIn("State: focused_hardening", focused)
            self.assertIn("Repair wave: terminal GREEN", focused)
            self.assertEqual(
                git(
                    repo,
                    "diff",
                    "--name-only",
                    facts["commits"][3],
                    facts["commits"][5],
                ),
                excluded,
            )
            self.assertEqual(
                product_entries(repo, facts["commits"][3], excluded),
                product_entries(repo, facts["commits"][5], excluded),
            )
            self.assertIn("State: candidate_frozen", prelaunch)
            self.assertIn("Review status: not started", prelaunch)
            self.assertIn(
                "Exact review command: codex exec review --commit "
                "refs/happycodex-eval/admin-cycle/candidate -m gpt-5.6-sol "
                '-c model_reasoning_effort="max" --ignore-user-config '
                "--ignore-rules --output-last-message "
                "/tmp/happycodex-eval/admin-cycle/review-task-9.final.json "
                "--json -",
                prelaunch,
            )
            self.assertIn(
                f"Authoritative source candidate: {facts['commits'][3]}", prelaunch
            )
            self.assertIn(f"tree {facts['trees'][3]}", prelaunch)
            self.assertIn(facts["product_manifest_sha256"][3], prelaunch)
            self.assertIn("refs/happycodex-eval/admin-cycle/baseline", prelaunch)
            self.assertIn("refs/happycodex-eval/admin-cycle/candidate", prelaunch)
            self.assertIn(
                "/tmp/happycodex-eval/admin-cycle/review-task-9.final.json",
                prelaunch,
            )
            self.assertIn("refs/happycodex-eval/admin-cycle/output", prelaunch)
            self.assertIn("State: exact_final", exact_final)
            self.assertIn("completion is still prohibited", exact_final)
            self.assertIn(f"Prelaunch revision {facts['commits'][5]}", plan)
            self.assertIn(projection["baseline_commit"], plan)
            self.assertIn(projection["candidate_commit"], plan)
            self.assertIn(projection["output_sha256"], plan)
            self.assertIn(projection["challenger_sha256"], plan)
            self.assertNotIn(
                excluded,
                git(repo, "ls-tree", "-r", projection["candidate_commit"]),
            )
            self.assertEqual(
                git(repo, "rev-parse", f"{projection['ref_prefix']}/output"),
                projection["output_blob"],
            )
            self.assertEqual(
                git(repo, "rev-parse", f"{projection['ref_prefix']}/challenger"),
                projection["challenger_blob"],
            )
            review_output = git(repo, "cat-file", "blob", projection["output_blob"])
            review_fields = dict(
                line.split("=", 1) for line in review_output.splitlines()
            )
            self.assertEqual(projection["source_baseline_commit"], facts["commits"][0])
            self.assertEqual(projection["source_candidate_commit"], facts["commits"][3])
            self.assertIn(
                "source_baseline_manifest_sha256="
                + projection["source_baseline_manifest_sha256"],
                review_output,
            )
            self.assertIn(
                "source_candidate_manifest_sha256="
                + projection["source_candidate_manifest_sha256"],
                review_output,
            )
            self.assertIn(
                "projected_baseline_manifest_sha256="
                + review_fields["projected_baseline_manifest_sha256"],
                review_output,
            )
            self.assertIn(
                "projected_candidate_manifest_sha256="
                + review_fields["projected_candidate_manifest_sha256"],
                review_output,
            )
            self.assertEqual(
                projection["source_baseline_manifest_sha256"],
                review_fields["projected_baseline_manifest_sha256"],
            )
            self.assertEqual(
                projection["source_candidate_manifest_sha256"],
                review_fields["projected_candidate_manifest_sha256"],
            )
            self.assertIn("phase_1_inventory_frozen=true", review_output)
            self.assertIn("phase_1_correctness_complete=true", review_output)
            self.assertIn("phase_1_diff_unit_coverage=complete", review_output)
            self.assertIn("configured_model_source=evaluator-default", review_output)
            self.assertIn("effective_model=gpt-5.6-sol", review_output)
            self.assertIn("effective_effort=max", review_output)
            self.assertIn('"objective_verification":{', review_output)
            self.assertIn(f'"exclusions":["{excluded}"]', review_output)
            self.assertIn("independent_obligations=OBL-1", review_output)
            self.assertIn("OBL-2 unrelated-output-preservation", review_output)
            self.assertIn("contract_mapping=OBL-1", review_output)
            challenger_output = git(
                repo, "cat-file", "blob", projection["challenger_blob"]
            )
            self.assertIn(
                f"predispatch_record={facts['commits'][1]}", challenger_output
            )
            self.assertIn(f"terminal_record={facts['commits'][2]}", challenger_output)
            self.assertNotIn("candidate_after_terminal=", challenger_output)

    def test_review_projection_ref_failures_fail_closed(self) -> None:
        case = self.cases["review-admin-cycle"]
        original_run = runner.run
        for suffix in ("baseline", "candidate", "output"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as raw:
                repo = Path(raw) / "repo"

                def fail_selected_update_ref(
                    argv: list[str], **kwargs: object
                ) -> subprocess.CompletedProcess[str]:
                    if argv[:2] == ["git", "update-ref"] and argv[2].endswith(
                        f"/{suffix}"
                    ):
                        return subprocess.CompletedProcess(
                            argv,
                            1,
                            stdout="",
                            stderr=f"injected {suffix} update-ref failure",
                        )
                    return original_run(argv, **kwargs)

                with (
                    mock.patch.object(
                        runner, "run", side_effect=fail_selected_update_ref
                    ),
                    self.assertRaisesRegex(
                        RuntimeError,
                        "review receipt persistence|review ref update",
                    ),
                ):
                    runner.build_fixture(case, repo)

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
        for case_id in ("boundary-cutover", "compaction-recovery"):
            case = self.cases[case_id]
            assertions = case["oracle"]["coverage_assertions"]
            with self.subTest(case=case_id):
                self.assertEqual(
                    {item["tag"] for item in assertions}, set(case["covers"])
                )
                invalid = json.loads(json.dumps(case))
                invalid["oracle"]["coverage_assertions"].pop()
                with self.assertRaisesRegex(ValueError, "coverage assertions"):
                    runner.validate_case(invalid, Path(f"{case_id}.json"))

        boundary = self.cases["boundary-cutover"]
        boundary_result = {
            **boundary["oracle"]["expected"],
            "decision": "incomplete",
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": [],
            "reason": "",
            "recovery_state": None,
        }
        boundary_failures = runner.match_oracle(boundary_result, boundary["oracle"])
        self.assertEqual(
            sum("missing anchored blocker" in item for item in boundary_failures), 8
        )
        anchored_findings = []
        anchored_blockers = []
        for index, expected in enumerate(
            boundary["oracle"]["required_anchored_blockers"], start=1
        ):
            identity = f"MODEL-GENERATED-{index}"
            allowed_classes = expected["class"]
            if not isinstance(allowed_classes, list):
                allowed_classes = [allowed_classes]
            anchored_findings.append(
                {
                    "identity": identity,
                    "domain": "other",
                    "state": "unknown",
                    "anchors": [expected["anchor"]],
                }
            )
            anchored_blockers.append(
                {
                    "identity": identity,
                    "class": allowed_classes[-1],
                    "blocking": True,
                    "reason": "counterexample",
                }
            )
        anchored_result = {
            **boundary_result,
            "finding_classifications": anchored_findings,
            "blocker_classifications": anchored_blockers,
        }
        self.assertEqual(runner.match_oracle(anchored_result, boundary["oracle"]), [])

        recovery = self.cases["compaction-recovery"]
        recovery_result = {
            **recovery["oracle"]["expected"],
            "decision": "incomplete",
            "finding_classifications": recovery["oracle"]["required_classifications"][
                :2
            ],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": [],
            "reason": "",
            "recovery_state": None,
        }
        recovery_failures = runner.match_oracle(recovery_result, recovery["oracle"])
        self.assertEqual(
            sum("missing classification" in item for item in recovery_failures), 0
        )
        self.assertEqual(
            sum(
                "missing anchored classification" in item for item in recovery_failures
            ),
            4,
        )
        self.assertGreaterEqual(
            sum("missing anchored blocker" in item for item in recovery_failures), 5
        )

    def test_four_false_green_cases_bind_every_seeded_defect(self) -> None:
        expected_blocker_counts = {
            "no-commit-secret": 2,
            "receipt-mismatch": 3,
            "review-inventory-gate": 1,
            "review-isolation": 6,
        }
        for case_id, blocker_count in expected_blocker_counts.items():
            case = self.cases[case_id]
            oracle = case["oracle"]
            with self.subTest(case=case_id):
                assertions = oracle.get("coverage_assertions", [])
                self.assertEqual(
                    {item["tag"] for item in assertions}, set(case["covers"])
                )
                required = oracle.get("required_anchored_blockers", [])
                self.assertEqual(len(required), blocker_count)

                with tempfile.TemporaryDirectory() as raw:
                    repo = Path(raw) / case_id
                    runner.build_fixture(case, repo)
                    fixture_surface = []
                    for path in repo.rglob("*"):
                        relative = path.relative_to(repo)
                        if ".git" in relative.parts or not path.is_file():
                            continue
                        fixture_surface.append(relative.as_posix())
                        fixture_surface.append(path.read_text(errors="replace"))
                    rendered_fixture = "\n".join(fixture_surface)
                    for blocker in required:
                        self.assertIn(blocker["anchor"], rendered_fixture)

                expected_values = {
                        field: value[0] if isinstance(value, list) else value
                        for field, value in oracle["expected"].items()
                }
                result = {
                    **expected_values,
                    "finding_classifications": [],
                    "blocker_classifications": [],
                    "open_gates": (
                        ["product_edit"]
                        if expected_values["protocol_may_product_write"] is True
                        else ["user_selection"]
                        if expected_values["decision"] == "stop_for_user"
                        else ["reconciliation"]
                    ),
                    "evidence": ["fixture evidence"],
                    "reason": "completion remains blocked",
                    "recovery_state": None,
                }
                for finding in oracle.get("required_classifications", []):
                    state = finding["state"]
                    result["finding_classifications"].append(
                        {
                            "identity": finding["identity"],
                            "domain": finding["domain"],
                            "state": state[0] if isinstance(state, list) else state,
                            "anchors": [finding["identity"]],
                        }
                    )
                used_anchored_findings: set[int] = set()
                for anchored in oracle.get("required_anchored_classifications", []):
                    states = anchored["state"]
                    allowed_states = states if isinstance(states, list) else [states]
                    match = next(
                        (
                            index
                            for index, finding in enumerate(
                                result["finding_classifications"]
                            )
                            if index not in used_anchored_findings
                            and finding["domain"] == anchored["domain"]
                            and finding["state"] in allowed_states
                        ),
                        None,
                    )
                    if match is None:
                        match = len(result["finding_classifications"])
                        result["finding_classifications"].append(
                            {
                                "identity": f"ANCHORED-{case_id}-{match}",
                                "domain": anchored["domain"],
                                "state": allowed_states[0],
                                "anchors": [],
                            }
                        )
                    used_anchored_findings.add(match)
                    result["finding_classifications"][match]["anchors"].append(
                        anchored["anchor"]
                    )

                nonproving = json.loads(json.dumps(result))
                self.assertTrue(runner.match_oracle(nonproving, oracle))

                for index, blocker in enumerate(required):
                    identity = f"PROOF-{case_id}-{index}"
                    classes = blocker["class"]
                    classes = classes if isinstance(classes, list) else [classes]
                    result["finding_classifications"].append(
                        {
                            "identity": identity,
                            "domain": "receipt",
                            "state": "unknown",
                            "anchors": [blocker["anchor"]],
                        }
                    )
                    result["blocker_classifications"].append(
                        {
                            "identity": identity,
                            "class": classes[0],
                            "blocking": True,
                            "reason": "seeded defect remains open",
                        }
                    )
                self.assertEqual(runner.match_oracle(result, oracle), [])

                for index in range(len(required)):
                    missing = json.loads(json.dumps(result))
                    del missing["finding_classifications"][
                        len(oracle.get("required_classifications", [])) + index
                    ]
                    del missing["blocker_classifications"][index]
                    self.assertTrue(runner.match_oracle(missing, oracle))

        isolation = self.cases["review-isolation"]
        required = isolation["oracle"]["required_anchored_blockers"]
        collapsed = {
            **{
                field: value[0] if isinstance(value, list) else value
                for field, value in isolation["oracle"]["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": "ONE-FROZEN-REVIEW-FINDING",
                    "domain": "receipt",
                    "state": "unknown",
                    "anchors": [item["anchor"] for item in required[:4]],
                },
                {
                    "identity": "ONE-EXHAUSTIVE-REVIEW-FINDING",
                    "domain": "receipt",
                    "state": "unknown",
                    "anchors": [item["anchor"] for item in required[4:]],
                },
            ],
            "blocker_classifications": [
                {
                    "identity": "ONE-FROZEN-REVIEW-FINDING",
                    "class": "frozen_acceptance",
                    "blocking": True,
                    "reason": "generic review concern",
                },
                {
                    "identity": "ONE-EXHAUSTIVE-REVIEW-FINDING",
                    "class": "exhaustive_claim",
                    "blocking": True,
                    "reason": "generic review concern",
                },
            ],
            "open_gates": ["reconciliation"],
            "evidence": ["generic evidence"],
            "reason": "completion remains blocked",
            "recovery_state": None,
        }
        failures = runner.match_oracle(collapsed, isolation["oracle"])
        self.assertTrue(any("distinct anchored blocker" in item for item in failures))

    def test_exact_finding_identity_cannot_replace_an_anchor_member(self) -> None:
        oracle = {
            "expected": {"protocol_may_complete": False},
            "required_anchored_classifications": [
                {
                    "anchor": "test_read_mode",
                    "domain": "other",
                    "state": "candidate_new",
                }
            ],
        }
        result = {
            "decision": "incomplete",
            "qualifies": True,
            "execplan_condition": "needs_amendment",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "test_read_mode",
                    "domain": "other",
                    "state": "candidate_new",
                    "anchors": ["tests.txt", "src/job.py"],
                }
            ],
            "blocker_classifications": [],
        }
        failures = runner.match_oracle(result, oracle)
        self.assertTrue(
            any("missing anchored classification" in item for item in failures)
        )

        qualified = json.loads(json.dumps(result))
        qualified["finding_classifications"][0]["identity"] = "MODEL:test_read_mode"
        failures = runner.match_oracle(qualified, oracle)
        self.assertTrue(
            any("missing anchored classification" in item for item in failures)
        )

    def test_one_finding_cannot_supply_multiple_blocker_classes(self) -> None:
        oracle = {
            "expected": {"protocol_may_complete": False},
            "required_anchored_blockers": [
                {
                    "anchor": "docs/execplans/contracts.md",
                    "class": ["exhaustive_claim", "frozen_acceptance"],
                }
            ],
        }
        result = {
            "decision": "incomplete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "MODEL-SCOPE",
                    "domain": "other",
                    "state": "candidate_new",
                    "anchors": ["docs/execplans/contracts.md"],
                }
            ],
            "blocker_classifications": [
                {
                    "identity": "MODEL-SCOPE",
                    "class": "exhaustive_claim",
                    "blocking": True,
                    "reason": "scope collision",
                },
                {
                    "identity": "MODEL-SCOPE",
                    "class": "production_condition",
                    "blocking": True,
                    "reason": "unrelated extra classification",
                },
            ],
            "open_gates": ["reconciliation"],
            "evidence": [],
            "reason": "duplicate blocker identity",
            "recovery_state": None,
        }
        failures = protocol_result_failures(result)
        self.assertTrue(
            any("blocker identities" in item for item in failures)
        )

    def test_result_identities_are_nonblank_and_globally_unique(self) -> None:
        archive = self.cases["no-commit-archive-recovery"]
        result = {
            **{
                field: value[0] if isinstance(value, list) else value
                for field, value in archive["oracle"]["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": "ARCHIVE-RECOVERY-VALID",
                    "domain": "receipt",
                    "state": "resolved",
                    "anchors": ["ARCHIVE-RECOVERY-VALID"],
                },
                {
                    "identity": "MODEL:ARCHIVE-RECOVERY-VALID",
                    "domain": "receipt",
                    "state": "unknown",
                    "anchors": ["ARCHIVE-RECOVERY-VALID"],
                },
            ],
            "blocker_classifications": [],
            "open_gates": ["product_edit"],
            "evidence": [],
            "reason": "duplicate identity probe",
            "recovery_state": None,
        }
        self.assertFalse(
            any(
                "duplicate finding" in item
                for item in runner.match_oracle(result, archive["oracle"])
            )
        )
        result["finding_classifications"][1]["identity"] = "ARCHIVE-RECOVERY-VALID"
        self.assertTrue(
            any("finding identities" in item for item in protocol_result_failures(result))
        )

        midflight = self.cases["midflight-escalation"]
        result = {
            **{
                field: value[0] if isinstance(value, list) else value
                for field, value in midflight["oracle"]["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": "MODEL:X",
                    "domain": "other",
                    "state": "unknown",
                    "anchors": ["lib.py"],
                }
            ],
            "blocker_classifications": [
                {
                    "identity": "MODEL:X",
                    "class": "original_goal",
                    "blocking": True,
                    "reason": "first",
                },
                {
                    "identity": "X",
                    "class": "production_condition",
                    "blocking": True,
                    "reason": "alias duplicate",
                },
            ],
            "open_gates": ["reconciliation"],
            "evidence": [],
            "reason": "duplicate blocker probe",
            "recovery_state": None,
        }
        self.assertFalse(
            any(
                "duplicate blocker" in item
                for item in runner.match_oracle(result, midflight["oracle"])
            )
        )
        result["blocker_classifications"][1]["identity"] = "MODEL:X"
        self.assertTrue(
            any("blocker identities" in item for item in protocol_result_failures(result))
        )

        result["finding_classifications"][0]["identity"] = " \t"
        result["blocker_classifications"] = []
        self.assertTrue(protocol_result_failures(result))
        result["finding_classifications"][0]["identity"] = "MODEL:X"
        result["blocker_classifications"] = [
            {
                "identity": "\n",
                "class": "original_goal",
                "blocking": True,
                "reason": "blank blocker",
            }
        ]
        self.assertTrue(protocol_result_failures(result))
        identity_schema = runner.OUTPUT_SCHEMA["properties"]["finding_classifications"][
            "items"
        ]["properties"]["identity"]
        blocker_identity_schema = runner.OUTPUT_SCHEMA["properties"][
            "blocker_classifications"
        ]["items"]["properties"]["identity"]
        self.assertEqual(identity_schema["minLength"], 1)
        self.assertEqual(blocker_identity_schema["minLength"], 1)
        self.assertNotIn("pattern", identity_schema)
        self.assertNotIn("pattern", blocker_identity_schema)

    def test_raw_and_receipt_identity_matching_is_exact(self) -> None:
        base = self.cases["midflight-escalation"]
        result = {
            **{
                field: value[0] if isinstance(value, list) else value
                for field, value in base["oracle"]["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": "X",
                    "domain": "other",
                    "state": "unknown",
                    "anchors": ["lib.py"],
                },
                {
                    "identity": "Y",
                    "domain": "other",
                    "state": "unknown",
                    "anchors": ["other.py"],
                },
            ],
            "blocker_classifications": [
                {
                    "identity": "Y",
                    "class": "original_goal",
                    "blocking": True,
                    "reason": "required blocker",
                }
            ],
            "open_gates": ["reconciliation"],
            "evidence": [],
            "reason": "alias projection probe",
            "recovery_state": None,
        }
        case = {
            "fixture": {},
            "oracle": {
                "expected": base["oracle"]["expected"],
                "required_classifications": [
                    {"identity": "MODEL:X", "domain": "other", "state": "unknown"}
                ],
                "required_blocker_classifications": [
                    {"identity": "MODEL:Y", "class": "original_goal"}
                ],
            },
        }
        self.assertTrue(runner.match_oracle(result, case["oracle"]))
        self.assertFalse(runner.finding_identity_matches("MODEL:X", "X"))
        self.assertFalse(runner.finding_identity_matches("Finding-A", "finding-a"))
        self.assertTrue(
            runner.finding_has_anchor(
                {"anchors": ["repository-a:src/lib.py"]},
                "repository-a:src/lib.py",
            )
        )
        self.assertFalse(
            runner.finding_has_anchor(
                {"anchors": ["repository-a:src/lib.py"]},
                "repository-a:src/Lib.py",
            )
        )
        self.assertFalse(
            runner.finding_has_anchor(
                {"anchors": ["repository-a:src/lib.py"]},
                "src/lib.py",
            )
        )
        receipt = receipt_engine.sanitized_result_receipt(result)
        finding = receipt["finding_classifications"][0]
        self.assertNotIn("identity_casefold_sha256", finding)
        self.assertNotIn("identity_match_sha256s", finding)
        self.assertIn("identity_sha256", finding)

        completed = {
            "decision": "complete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
            "finding_classifications": [
                {
                    "identity": "fixture-17",
                    "domain": "baseline_failure",
                    "state": "baseline_unchanged",
                    "anchors": ["tests.txt"],
                }
            ],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": ["unchanged baseline"],
            "reason": "complete",
            "recovery_state": None,
        }
        completed_case = {
            "fixture": {},
            "oracle": {
                "expected": {
                    field: completed[field] for field in runner.PERMISSION_FIELDS
                },
                "accepted_baseline_failures": ["MODEL:fixture-17"],
            },
        }
        self.assertTrue(runner.match_oracle(completed, completed_case["oracle"]))
        completed_receipt = receipt_engine.sanitized_result_receipt(completed)
        self.assertIsNotNone(completed_receipt)

    def test_recovery_marker_receipt_uses_one_canonical_projection(self) -> None:
        marker_ids = [
            RECOVERY_MANIFEST_MARKER,
            *[f"marker-{index}" for index in range(8)],
        ]
        recovery = {
            "baseline_revision": "1" * 40,
            "baseline_tree": "2" * 40,
            "current_revision": "3" * 40,
            "current_tree": "4" * 40,
            "writer": "Root",
            "milestone_phase": "implementation",
            "next_action": "implement",
            "pending_gates": ["product_edit"],
            "tests": {
                "passed": 1,
                "failed": 0,
                "accepted_failures": 0,
                "marker_ids": marker_ids,
            },
            "worktree": "clean",
            "live_agents": [],
            "marker_ids": marker_ids,
        }
        receipt = receipt_engine.sanitized_recovery_receipt(recovery)
        self.assertTrue(receipt["summary_consistent"])
        self.assertEqual(receipt["recovery_manifest_count"], 1)
        reordered = json.loads(json.dumps(recovery))
        reordered["marker_ids"].reverse()
        reordered["tests"]["marker_ids"].reverse()
        self.assertEqual(
            receipt_engine.sanitized_recovery_receipt(reordered)["marker_ids_sha256"],
            receipt["marker_ids_sha256"],
        )

    def test_generation6_result_projection_replays_and_binds_raw_result(self) -> None:
        self.assertEqual(
            runner._repository_binding_digest("fixture", "1" * 40, "2" * 40),
            runner.canonical_sha256(
                {
                    "domain": "happycodex/0.6/repository",
                    "repositories": [
                        {
                            "namespace": "case:fixture",
                            "baseline_revision": "1" * 40,
                            "baseline_tree": "2" * 40,
                        }
                    ],
                }
            ),
        )
        self.assertEqual(
            runner._outcome_binding_digest("exact prompt"),
            runner.canonical_sha256(
                {
                    "domain": "happycodex/0.6/outcome",
                    "operative_request": "exact prompt",
                }
            ),
        )
        result = {
            "decision": "complete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": ["release"],
            "evidence": ["release receipt pending"],
            "reason": "completion cannot erase a pending release",
            "recovery_state": None,
        }
        context = {
            "task_id": "case:pending-release",
            "root_task_id": "root:evaluator",
            "executor_task_id": "executor:evaluator",
            "owner_label": "happycodex-evaluator",
            "destination_id": "repository:happycodex",
            "lineage_digest": "a" * 64,
            "role_config_digest": "b" * 64,
            "repository_digest": "c" * 64,
            "outcome_digest": "d" * 64,
            "invocation_profile": runner.invocation_profile(
                model="gpt-5.6-sol",
                effort="high",
                timeout_seconds=300,
                arm="candidate",
            ),
            "accepted_baseline_failures": [],
        }
        with self.assertRaisesRegex(ValueError, "raw protocol assertions diverge"):
            runner.protocol_result_projection(result, context=context)
        result["decision"] = "continue"
        result["protocol_may_complete"] = False
        projection = runner.protocol_result_projection(result, context=context)
        self.assertEqual(projection["schema_generation"], 6)
        self.assertEqual(
            projection["raw_result_sha256"],
            runner.canonical_sha256(result),
        )
        self.assertEqual(projection["decision"], "continue")
        self.assertEqual(projection["open_gates"], ["release"])
        self.assertNotIn("report", projection)
        self.assertNotIn("attempt_key", projection)
        receipt_engine._validated_projection(
            projection,
            raw=result,
            profile=context["invocation_profile"],
            accepted=[],
        )

        wrong_gate = json.loads(json.dumps(projection))
        wrong_gate["open_gates"] = ["checks"]
        with self.assertRaisesRegex(ValueError, "does not replay"):
            receipt_engine._validated_projection(
                wrong_gate,
                raw=result,
                profile=context["invocation_profile"],
                accepted=[],
            )
        divergent = json.loads(json.dumps(projection))
        divergent["raw_result_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "does not replay"):
            receipt_engine._validated_projection(
                divergent,
                raw=result,
                profile=context["invocation_profile"],
                accepted=[],
            )

    def test_case_validation_correlates_recovery_oracle_permissions(self) -> None:
        case = json.loads(json.dumps(self.cases["pre-freeze-compaction"]))
        case["oracle"]["expected"]["protocol_may_product_write"] = True
        case["oracle"]["expected"]["execplan_condition"] = "usable"
        native = case["fixture"]["native_compaction_resume"]
        recovery = native["recovery_oracle"]
        recovery["next_action"] = "ask_user"
        recovery["pending_gates"] = ["user_selection"]
        manifest = json.loads(
            native["post_compaction_transition"]["files"][
                runner.RECOVERY_MANIFEST_PATH
            ]
        )
        manifest["gates"] = ["user_selection"]
        content = (
            json.dumps(
                manifest,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )
        native["post_compaction_transition"]["files"][
            runner.RECOVERY_MANIFEST_PATH
        ] = content
        marker = (
            "RECOVERY-MANIFEST-SHA256:"
            + hashlib.sha256(content.encode()).hexdigest()
        )
        recovery["marker_ids"] = [
            marker if item.startswith("RECOVERY-MANIFEST-SHA256:") else item
            for item in recovery["marker_ids"]
        ]
        runner.validate_case(case, Path("recovery-permission.json"))

    def test_read_mode_oracle_requires_semantic_blocker_not_domain_label(self) -> None:
        oracle = self.cases["compaction-recovery"]["oracle"]
        classifications = [
            item
            for item in oracle["required_anchored_classifications"]
            if item["anchor"] == "test_read_mode"
        ]
        blockers = [
            item
            for item in oracle["required_anchored_blockers"]
            if item["anchor"] == "test_read_mode"
        ]
        self.assertEqual(classifications, [])
        self.assertEqual(
            blockers, [{"anchor": "test_read_mode", "class": "original_goal"}]
        )
        lost_scout = [
            item
            for item in oracle["required_anchored_blockers"]
            if item["anchor"] == "S-2"
        ]
        self.assertEqual(len(lost_scout), 1)
        self.assertEqual(set(lost_scout[0]["class"]), runner.BLOCKER_CLASSES)
        dirty_untracked = [
            item
            for item in oracle["required_anchored_blockers"]
            if item["anchor"] == "scratch-recovery.txt"
        ]
        self.assertEqual(len(dirty_untracked), 1)
        self.assertEqual(
            dirty_untracked[0]["class"],
            ["safety_data_integrity", "frozen_acceptance"],
        )
        dirty_coverage = next(
            item
            for item in oracle["coverage_assertions"]
            if item["tag"] == "dirty-untracked"
        )
        self.assertEqual(dirty_coverage["class"], dirty_untracked[0]["class"])

    def test_boundary_cutover_accepts_only_bounded_overlapping_semantics(self) -> None:
        oracle = self.cases["boundary-cutover"]["oracle"]
        by_anchor = {
            item["anchor"]: item["class"]
            for item in oracle["required_anchored_blockers"]
        }
        expected = ["exhaustive_claim", "original_goal"]
        self.assertEqual(by_anchor["legacy/entry.py"], expected)
        self.assertEqual(by_anchor["app/router.py"], expected)
        outbox_classes = [
            "original_goal",
            "frozen_acceptance",
            "safety_data_integrity",
            "production_condition",
            "exhaustive_claim",
        ]
        self.assertEqual(set(outbox_classes), runner.BLOCKER_CLASSES)
        self.assertEqual(by_anchor["app/outbox.py"], outbox_classes)
        outbox_coverage = next(
            item
            for item in oracle["coverage_assertions"]
            if item["tag"] == "missing-worker"
        )
        self.assertEqual(outbox_coverage["class"], outbox_classes)

        outbox_oracle = {
            "expected": {"protocol_may_complete": False},
            "required_anchored_blockers": [
                {"anchor": "app/outbox.py", "class": outbox_classes}
            ],
        }
        base_result = {
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "MODEL-MISSING-WORKER",
                    "domain": "other",
                    "state": "candidate_new",
                    "anchors": ["app/outbox.py"],
                }
            ],
            "blocker_classifications": [
                {
                    "identity": "MODEL-MISSING-WORKER",
                    "class": "original_goal",
                    "blocking": True,
                    "reason": "the outbox has no consumers",
                }
            ],
        }
        for blocker_class in outbox_classes:
            with self.subTest(accepted_class=blocker_class):
                result = json.loads(json.dumps(base_result))
                result["blocker_classifications"][0]["class"] = blocker_class
                self.assertEqual(runner.match_oracle(result, outbox_oracle), [])

        for mutation in (
            "wrong-anchor",
            "nonblocking",
            "identity-mismatch",
            "missing-finding",
            "completion-open",
            "invalid-class",
        ):
            with self.subTest(rejected=mutation):
                result = json.loads(json.dumps(base_result))
                if mutation == "wrong-anchor":
                    result["finding_classifications"][0]["anchors"] = ["app/router.py"]
                elif mutation == "nonblocking":
                    result["blocker_classifications"][0]["blocking"] = False
                elif mutation == "identity-mismatch":
                    result["blocker_classifications"][0]["identity"] = "DIFFERENT-ID"
                elif mutation == "missing-finding":
                    result["finding_classifications"] = []
                elif mutation == "completion-open":
                    result["protocol_may_complete"] = True
                else:
                    result["blocker_classifications"][0]["class"] = "invalid-class"
                self.assertTrue(runner.match_oracle(result, outbox_oracle))

    def test_multi_repo_oracle_binds_both_seeded_scope_failures(self) -> None:
        case = self.cases["multi-repo-submodule"]
        assertions = case["oracle"]["coverage_assertions"]
        self.assertEqual({item["tag"] for item in assertions}, set(case["covers"]))
        equivalent_scope_classes = ["exhaustive_claim", "frozen_acceptance"]
        required_by_anchor = {
            item["anchor"]: item["class"]
            for item in case["oracle"]["required_anchored_blockers"]
        }
        self.assertEqual(
            required_by_anchor["docs/execplans/contracts.md"],
            equivalent_scope_classes,
        )
        multi_repo_assertion = next(
            item for item in assertions if item["tag"] == "multi-repository"
        )
        self.assertEqual(multi_repo_assertion["class"], equivalent_scope_classes)
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": True,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "MODEL-SUBMODULE",
                    "domain": "other",
                    "state": "candidate_new",
                    "anchors": ["backend/shared-schema.pointer"],
                },
                {
                    "identity": "MODEL-MULTI-REPO",
                    "domain": "receipt",
                    "state": "candidate_new",
                    "anchors": ["docs/execplans/contracts.md"],
                },
            ],
            "blocker_classifications": [
                {
                    "identity": "MODEL-SUBMODULE",
                    "class": "original_goal",
                    "blocking": True,
                    "reason": "candidate dependency content is absent",
                },
                {
                    "identity": "MODEL-MULTI-REPO",
                    "class": "exhaustive_claim",
                    "blocking": True,
                    "reason": "repository namespaces collide",
                },
            ],
            "open_gates": ["product_edit"],
            "evidence": ["repository facts"],
            "reason": "completion remains blocked",
            "recovery_state": None,
        }
        self.assertEqual(runner.match_oracle(result, case["oracle"]), [])
        result["blocker_classifications"][1]["class"] = "frozen_acceptance"
        self.assertEqual(runner.match_oracle(result, case["oracle"]), [])
        result["finding_classifications"] = result["finding_classifications"][1:]
        self.assertTrue(
            any(
                "backend/shared-schema.pointer" in failure
                for failure in runner.match_oracle(result, case["oracle"])
            )
        )

    def test_inventory_gate_fixture_is_otherwise_complete_but_unnumbered(self) -> None:
        excluded = "docs/execplans/inventory-gate.md"
        self.assertEqual(
            "none",
            self.cases["review-inventory-gate"]["oracle"]["expected"][
                "protocol_review_mode"
            ],
        )
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            facts = runner.build_fixture(self.cases["review-inventory-gate"], repo)
            self.assertIn(
                "public api contract",
                (repo / "PUBLIC_CONTRACT.md").read_text().casefold(),
            )
            projection = facts["review_projections"][0]
            receipt = git(repo, "cat-file", "blob", projection["output_blob"])
            self.assertIn("phase_1_inventory_frozen=true", receipt)
            self.assertIn("independent_obligations=\n", receipt)
            self.assertNotIn("OBL-", receipt)
            self.assertNotIn("phase_2_contract_projection=", receipt)
            self.assertNotIn("workspace=", receipt)
            self.assertIn(
                '"operative_request":"Change the greeting from hello to welcome. '
                'Preserve all other output."',
                receipt,
            )
            self.assertIn("contract_mapping=", receipt)
            self.assertEqual(git(repo, "status", "--porcelain=v1"), "")
            self.assertEqual(
                product_entries(repo, "HEAD^", excluded),
                product_entries(repo, "HEAD", excluded),
            )

    def test_receipt_mismatch_has_real_review_but_no_challenger_terminal(self) -> None:
        excluded = "docs/execplans/authority.md"
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            facts = runner.build_fixture(self.cases["receipt-mismatch"], repo)
            plan = (repo / excluded).read_text()
            self.assertIn("BC-7 completed", plan)
            self.assertNotIn("terminal receipt", plan.casefold())
            self.assertNotIn("BC-7", git(repo, "show-ref"))
            self.assertEqual(
                git(repo, "diff", "--name-only", "HEAD^", "HEAD"), excluded
            )
            projection = facts["review_projections"][0]
            self.assertEqual(
                git(repo, "rev-parse", f"{projection['ref_prefix']}/output"),
                projection["output_blob"],
            )

    def test_oracle_matcher_accepts_controls_and_reports_counterexamples(self) -> None:
        case = self.cases["subthreshold-control"]
        passing = {
            "decision": "continue",
            "qualifies": False,
            "execplan_condition": "not_required",
            "protocol_may_product_write": True,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "open_gates": ["product_edit"],
            "evidence": ["TASK.md"],
            "reason": "Clearly local and low-risk documentation correction.",
        }
        self.assertEqual(runner.match_oracle(passing, case["oracle"]), [])
        failing = {
            **passing,
            "qualifies": True,
            "protocol_may_product_write": False,
            "reason": "",
        }
        failures = runner.match_oracle(failing, case["oracle"])
        self.assertTrue(any("qualifies" in failure for failure in failures))
        self.assertTrue(
            any("protocol_may_product_write" in failure for failure in failures)
        )

    def test_oracle_matcher_uses_blocker_classes_not_prose_phrases(self) -> None:
        result = {
            "decision": "incomplete",
            "qualifies": True,
            "execplan_condition": "needs_amendment",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "R-TRUNCATED-COVERAGE",
                    "domain": "receipt",
                    "state": "unknown",
                    "anchors": [],
                }
            ],
            "blocker_classifications": [
                {
                    "identity": "R-TRUNCATED-COVERAGE",
                    "class": "frozen_acceptance",
                    "blocking": True,
                    "reason": (
                        "No bounded correctness review or repository-completeness "
                        "pass followed truncation."
                    ),
                }
            ],
            "open_gates": ["reconciliation"],
            "evidence": [],
            "reason": "Review remains open.",
        }
        oracle = {
            "expected": {field: result[field] for field in runner.PERMISSION_FIELDS},
            "required_blocker_classes": ["frozen_acceptance"],
        }
        self.assertEqual(runner.match_oracle(result, oracle), [])
        result["blocker_classifications"][0]["reason"] = "Unrelated blocker."
        self.assertEqual(runner.match_oracle(result, oracle), [])
        result["blocker_classifications"][0]["blocking"] = False
        self.assertEqual(
            runner.match_oracle(result, oracle),
            ["missing blocking class: frozen_acceptance"],
        )

    def test_oracle_matcher_checks_structured_finding_identities(self) -> None:
        case = self.cases["no-commit-secret"]
        result = {
            "decision": "stop_for_user",
            "qualifies": True,
            "execplan_condition": "needs_amendment",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "SECRET-BASE-1",
                    "domain": "secret",
                    "state": "baseline_unchanged",
                    "anchors": ["product.cfg"],
                },
                {
                    "identity": "SECRET-OUTPUT-2",
                    "domain": "secret",
                    "state": "unknown",
                    "anchors": ["SECRET-OUTPUT-2", "scan.txt"],
                },
                {
                    "identity": "TAMPERED-ARCHIVE",
                    "domain": "receipt",
                    "state": "unknown",
                    "anchors": ["archive/checkpoint.txt"],
                },
            ],
            "blocker_classifications": [
                {
                    "identity": "SECRET-OUTPUT-2",
                    "class": "safety_data_integrity",
                    "blocking": True,
                    "reason": "The candidate evidence still contains a secret.",
                },
                {
                    "identity": "TAMPERED-ARCHIVE",
                    "class": "safety_data_integrity",
                    "blocking": True,
                    "reason": "The selected archive digest does not match its payload.",
                },
            ],
            "open_gates": ["user_selection"],
            "evidence": [
                "No-commit mode must retain skeleton, freeze, and closure snapshots."
            ],
            "reason": "A secret remains open, the snapshot ref is missing, and the baseline finding is classified.",
        }
        self.assertEqual(runner.match_oracle(result, case["oracle"]), [])
        result["finding_classifications"] = result["finding_classifications"][1:]
        failures = runner.match_oracle(result, case["oracle"])
        self.assertTrue(any("SECRET-BASE-1" in failure for failure in failures))

    def test_finding_identity_match_is_delimited_not_approximate(self) -> None:
        self.assertTrue(runner.finding_identity_matches("fixture-17", "fixture-17"))
        self.assertFalse(
            runner.finding_identity_matches(
                "baseline:test_old_fixture:fixture-17", "fixture-17"
            )
        )
        self.assertFalse(
            runner.finding_identity_matches(
                "baseline/test_old_fixture/fixture-17", "fixture-17"
            )
        )
        self.assertFalse(
            runner.finding_identity_matches("prefix:fixture-170", "fixture-17")
        )
        self.assertFalse(
            runner.finding_identity_matches("prefix-fixture-17", "fixture-17")
        )

    def test_completion_oracle_rejects_contradictory_output(self) -> None:
        case = self.cases["review-admin-cycle"]
        result = {
            "decision": "complete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
            "finding_classifications": [
                {
                    "identity": "REGRESSION-1",
                    "domain": "other",
                    "state": "candidate_new",
                    "anchors": [],
                }
            ],
            "open_gates": ["reconciliation"],
            "evidence": ["product tree is unchanged"],
            "reason": "Administrative closure is otherwise valid.",
            "blocker_classifications": [
                {
                    "identity": "REGRESSION-1",
                    "class": "frozen_acceptance",
                    "blocking": True,
                    "reason": "The candidate violates a frozen preservation claim.",
                }
            ],
        }
        failures = runner.match_oracle(result, case["oracle"])
        self.assertTrue(
            any("permission or gates" in failure for failure in failures)
        )
        self.assertTrue(any("candidate_new" in failure for failure in failures))
        self.assertTrue(
            any("completion has blocking" in failure for failure in failures)
        )

    def test_completion_requires_explicit_baseline_failure_acceptance(self) -> None:
        result = {
            "decision": "complete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
            "finding_classifications": [
                {
                    "identity": "fixture-17",
                    "domain": "baseline_failure",
                    "state": "baseline_unchanged",
                    "anchors": [],
                }
            ],
            "open_gates": [],
            "evidence": ["failure identity unchanged"],
            "reason": "all other gates are closed",
        }
        oracle = {
            "expected": {field: result[field] for field in runner.PERMISSION_FIELDS},
            "accepted_baseline_failures": [],
        }
        self.assertTrue(
            any(
                "unaccepted baseline failure" in failure
                for failure in runner.match_oracle(result, oracle)
            )
        )
        oracle["accepted_baseline_failures"] = ["fixture-17"]
        self.assertEqual(runner.match_oracle(result, oracle), [])
        result["finding_classifications"][0]["identity"] = (
            "baseline:test_old_fixture:fixture-17"
        )
        self.assertTrue(
            any(
                "unaccepted baseline failure" in failure
                for failure in runner.match_oracle(result, oracle)
            )
        )
        oracle["accepted_baseline_failures"] = [
            "baseline:test_old_fixture:fixture-17"
        ]
        self.assertEqual(runner.match_oracle(result, oracle), [])
        oracle["accepted_baseline_failures"] = [
            "baseline:test_old_fixture:fixture-17",
            "baseline:test_old_fixture:fixture-17",
        ]
        self.assertTrue(
            any(
                "unaccepted baseline failure" in failure
                for failure in runner.match_oracle(result, oracle)
            )
        )

    def test_case_validation_rejects_ambiguous_accepted_failure_ids(self) -> None:
        case = json.loads(json.dumps(self.cases["review-admin-cycle"]))
        case["oracle"]["accepted_baseline_failures"] = [
            "fixture-17",
            "fixture-17",
        ]
        with self.assertRaisesRegex(ValueError, "invalid accepted"):
            runner.validate_case(case, Path("ambiguous.json"))

    def test_baseline_failure_case_requires_structured_identities(self) -> None:
        case = self.cases["compaction-recovery"]
        required = case["oracle"]["required_classifications"]
        self.assertIn(
            {
                "identity": "fixture-17",
                "domain": "baseline_failure",
                "state": "resolved",
            },
            required,
        )
        prompt = case["prompt"]
        self.assertIn("separate finding_classifications for both identities", prompt)
        self.assertIn("recorded identity as resolved", prompt)
        self.assertIn("replacement identity as candidate_new", prompt)
        self.assertIn("do not collapse them under the shared test name", prompt)
        self.assertIn("unsupported post-freeze amendment", prompt)
        self.assertIn("unmet production prerequisite", prompt)
        self.assertIn("blocker_classifications", prompt)
        self.assertIn("frozen_acceptance", prompt)
        self.assertIn("production_condition", prompt)
        self.assertIn("corresponding finding anchors that durable plan", prompt)
        self.assertIn(
            {
                "identity": "fixture-18",
                "domain": "baseline_failure",
                "state": "candidate_new",
            },
            required,
        )

    def test_output_schema_forces_decision_fields(self) -> None:
        required = set(runner.OUTPUT_SCHEMA["required"])
        self.assertEqual(required, set(runner.OUTPUT_SCHEMA["properties"]))
        self.assertFalse(runner.OUTPUT_SCHEMA["additionalProperties"])
        self.assertIn(
            "complete", runner.OUTPUT_SCHEMA["properties"]["decision"]["enum"]
        )
        self.assertNotIn("may_write", required)
        self.assertIn("control gate", runner.EVALUATOR_CONTEXT)
        self.assertIn("without inferring downstream gates", runner.EVALUATOR_CONTEXT)
        self.assertIn("never the Root writer", runner.EVALUATOR_CONTEXT)
        recovery = runner.OUTPUT_SCHEMA["properties"]["recovery_state"]
        self.assertEqual(recovery["type"], ["object", "null"])
        self.assertNotIn("oneOf", recovery)
        self.assertTrue(
            recovery["properties"]["pending_gates"]["uniqueItems"]
        )
        self.assertTrue(recovery["properties"]["marker_ids"]["uniqueItems"])
        findings = runner.OUTPUT_SCHEMA["properties"]["finding_classifications"]
        self.assertIn("anchors", findings["items"]["required"])
        self.assertIn("RED-test edits are product writes", runner.EVALUATOR_CONTEXT)
        for field in (
            "finding_classifications",
            "blocker_classifications",
            "open_gates",
            "evidence",
        ):
            self.assertNotIn("maxItems", runner.OUTPUT_SCHEMA["properties"][field])

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

    def test_internal_output_validation_still_rejects_duplicate_values(self) -> None:
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": ["product_edit", "product_edit"],
            "evidence": [],
            "reason": "duplicate gate probe",
            "recovery_state": None,
        }
        with self.assertRaisesRegex(ValueError, "schema array mismatch"):
            runner.validate_output_result(result)

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

    def test_structural_schema_validates_output_case_and_recovery_parity(self) -> None:
        from evaluation.core.schema import load_contracts, validate_named

        contracts = load_contracts(ROOT / "evaluation" / "contracts-v6.json")
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": [],
            "reason": "structurally valid",
            "recovery_state": None,
        }
        self.assertEqual(validate_named(contracts, "output_result", result), result)
        case = json.loads(
            (ROOT / "evaluation" / "cases" / "pre-freeze-compaction.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(validate_named(contracts, "case", case), case)
        content = case["fixture"]["native_compaction_resume"][
            "post_compaction_transition"
        ]["files"][runner.RECOVERY_MANIFEST_PATH]
        manifest = json.loads(content)
        self.assertEqual(
            validate_named(contracts, "recovery_manifest", manifest), manifest
        )

    def test_structural_schema_leaves_result_and_recovery_relations_in_python(
        self,
    ) -> None:
        from evaluation.core.schema import load_contracts, validate_named

        contracts = load_contracts(ROOT / "evaluation" / "contracts-v6.json")
        result = {
            "decision": "continue",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [{
                "identity": "RESOLVED",
                "domain": "other",
                "state": "resolved",
                "anchors": [],
            }],
            "blocker_classifications": [{
                "identity": "RESOLVED",
                "class": "production_condition",
                "blocking": True,
                "reason": "cross-field contradiction",
            }],
            "open_gates": [],
            "evidence": [],
            "reason": "structurally valid but semantically inconsistent",
            "recovery_state": None,
        }
        validate_named(contracts, "output_result", result)
        self.assertTrue(protocol_result_failures(result))

        milestone_phases = contracts["schemas"]["output_result"]["properties"][
            "recovery_state"
        ]["properties"]["milestone_phase"]["enum"]
        recovery = {
            "baseline_revision": "1" * 40,
            "baseline_tree": "2" * 40,
            "current_revision": "3" * 40,
            "current_tree": "4" * 40,
            "writer": "Root",
            "milestone_phase": milestone_phases[0],
            "next_action": runner.RECOVERY_ACTIONS[0],
            "pending_gates": [],
            "tests": {
                "passed": 1,
                "failed": 0,
                "accepted_failures": 0,
                "marker_ids": [],
            },
            "worktree": "clean",
            "live_agents": [],
            "marker_ids": [],
        }
        result["finding_classifications"] = []
        result["blocker_classifications"] = []
        result["recovery_state"] = recovery
        validate_named(contracts, "output_result", result)
        self.assertTrue(protocol_result_failures(result))


if __name__ == "__main__":
    unittest.main()
