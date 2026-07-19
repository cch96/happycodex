from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from evaluation.core import receipt as receipt_engine
from evaluation.corpus import engine as runner


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "evaluation" / "corpus" / "engine.py"


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


class HappyCodexEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = runner.load_cases()

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
        self.assertTrue(any("/goal pause" in failure for failure in failures))
        result["open_gates"] = ["Run `/goal pause` before waiting for reconciliation."]
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
            "protocol_may_review",
            "protocol_may_complete",
        }
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                self.assertEqual(set(case["oracle"]["expected"]), permission_fields)
                invalid = json.loads(json.dumps(case))
                del invalid["oracle"]["expected"]["protocol_may_review"]
                with self.assertRaisesRegex(ValueError, "permission fields"):
                    runner.validate_case(invalid, Path(f"{case['id']}.json"))

    def test_positive_contract_fixtures_use_03_claim_states(self) -> None:
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
            self.assertIn("State: skeleton", plan)
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
            runner_text = ENGINE_PATH.read_text()
            for phrase in (
                "codex exec resume",
                "model_auto_compact_token_limit",
                "default_permissions",
                "permission_profile_args",
                "compaction_event_count",
                "resumed_same_thread",
                "fresh_recovery_thread_id",
            ):
                self.assertIn(phrase, runner_text)
            self.assertNotIn("sandbox_mode=", runner_text)
            self.assertNotIn('"-s",\n            "read-only"', runner_text)

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
            references = public_source / "skills/happycodex/references"
            (references / "execplan.md").unlink()
            (references / "external-review.md").write_text("public review\n")
            (references / "task-packets.md").write_text("public tasks\n")

            public_package = root / "public-package"
            runner.copy_plugin_package(public_source, public_package, arm="public-0.2")
            with self.assertRaisesRegex(RuntimeError, "runtime surface"):
                runner.copy_plugin_package(
                    public_source, root / "candidate-rejects-public"
                )
            with self.assertRaisesRegex(RuntimeError, "runtime surface"):
                runner.copy_plugin_package(
                    ROOT, root / "public-rejects-candidate", arm="public-0.2"
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
            "identities": {
                "engine": {"manifest_sha256": "1" * 64},
                "package": {
                    "semantic_sha256": "2" * 64,
                    "artifact_sha256": "3" * 64,
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
                "protocol_may_review": False,
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
                        "identity": "SECRET-CANARY-VALUE:/tmp/private/blocker",
                        "class": "frozen_acceptance",
                        "blocking": True,
                        "reason": "SECRET-CANARY-VALUE /tmp/private/reason",
                    }
                ],
                "open_gates": ["SECRET-CANARY-VALUE /tmp/private/gate"],
                "evidence": ["SECRET-CANARY-VALUE /tmp/private/evidence"],
                "reason": "SECRET-CANARY-VALUE /tmp/private/model-prose",
                "recovery_state": {
                    "baseline_revision": "1" * 40,
                    "baseline_tree": "2" * 40,
                    "current_revision": "3" * 40,
                    "current_tree": "4" * 40,
                    "writer": "Root",
                    "milestone_phase": "review",
                    "next_action": "review",
                    "pending_gates": ["review"],
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
                    "marker_ids": ["SECRET-CANARY-VALUE:/tmp/private/marker"],
                },
            },
            "fresh_recovery_result": None,
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
            "oracle_failures",
            "native_compaction",
        ):
            self.assertIn(key, receipt)
        rendered = json.dumps(receipt, sort_keys=True)
        self.assertNotIn("SECRET-CANARY-VALUE", rendered)
        self.assertNotIn("/tmp/", rendered)
        self.assertNotIn("isolated_home", rendered)
        self.assertEqual(receipt["result"]["decision"], "incomplete")
        self.assertIs(receipt["result"]["goal_pause_handoff_present"], False)
        self.assertIn(
            "identity_sha256", receipt["result"]["finding_classifications"][0]
        )
        self.assertIn(
            "identity_match_sha256s",
            receipt["result"]["finding_classifications"][0],
        )
        self.assertIn(
            "identity_casefold_sha256",
            receipt["result"]["finding_classifications"][0],
        )
        self.assertIn("anchor_sha256s", receipt["result"]["finding_classifications"][0])
        self.assertIn("reason_sha256", receipt["result"]["blocker_classifications"][0])
        self.assertIn(
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
            "open_gates": [],
            "evidence": [],
            "reason": "",
            "recovery_state": None,
        }
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
                tool_bin = runner.prepare_native_tool_bin(temp)
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
            self.assertIn("State: skeleton", skeleton)
            self.assertIn("boundary-challenger-9: pending", skeleton)
            self.assertIn("State: frozen", contract)
            self.assertIn("boundary-challenger-9: terminal complete", contract)
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
            self.assertIn(
                f"source_baseline_commit={facts['commits'][0]}", review_output
            )
            self.assertIn(
                f"source_candidate_commit={facts['commits'][3]}", review_output
            )
            self.assertIn("baseline_manifest_equal=true", review_output)
            self.assertIn("candidate_manifest_equal=true", review_output)
            self.assertIn("phase_1_inventory_frozen=true", review_output)
            self.assertIn("phase_1_correctness_complete=true", review_output)
            self.assertIn("phase_1_diff_unit_coverage=complete", review_output)
            self.assertIn("configured_model_source=evaluator-default", review_output)
            self.assertIn("effective_model=gpt-5.6-sol", review_output)
            self.assertIn("effective_effort=max", review_output)
            self.assertIn(
                "effective_permission_profile=read-only-isolated", review_output
            )
            self.assertIn("effective_network=disabled", review_output)
            self.assertIn("effective_write_access=none", review_output)
            self.assertIn('"objective_verification":{', review_output)
            self.assertIn(f'"exclusions":["{excluded}"]', review_output)
            self.assertIn("independent_obligations=OBL-1", review_output)
            self.assertIn("OBL-2 unrelated-output-preservation", review_output)
            self.assertIn("phase_2_contract_projection=", review_output)
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
                        RuntimeError, f"injected {suffix} update-ref failure"
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
            self.assertIn(f"diff_unit_count={len(diff_units)}", receipt)
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
            sum("missing anchored blocker" in item for item in boundary_failures), 7
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

                result = {
                    **{
                        field: value[0] if isinstance(value, list) else value
                        for field, value in oracle["expected"].items()
                    },
                    "finding_classifications": [],
                    "blocker_classifications": [],
                    "open_gates": ["seeded defects remain open"],
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
        anchors = [
            item["anchor"] for item in isolation["oracle"]["required_anchored_blockers"]
        ]
        collapsed = {
            **{
                field: value[0] if isinstance(value, list) else value
                for field, value in isolation["oracle"]["expected"].items()
            },
            "finding_classifications": [
                {
                    "identity": "ONE-GENERIC-REVIEW-FINDING",
                    "domain": "receipt",
                    "state": "unknown",
                    "anchors": anchors,
                }
            ],
            "blocker_classifications": [
                {
                    "identity": "ONE-GENERIC-REVIEW-FINDING",
                    "class": "frozen_acceptance",
                    "blocking": True,
                    "reason": "generic review concern",
                }
            ],
            "open_gates": ["review remains open"],
            "evidence": ["generic evidence"],
            "reason": "completion remains blocked",
            "recovery_state": None,
        }
        self.assertTrue(runner.match_oracle(collapsed, isolation["oracle"]))

    def test_exact_finding_identity_can_supply_the_same_evidence_anchor(self) -> None:
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
        self.assertEqual(runner.match_oracle(result, oracle), [])

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
        }
        failures = runner.match_oracle(result, oracle)
        self.assertTrue(
            any("multiple blocker classifications" in item for item in failures)
        )

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
            "protocol_may_product_write": False,
            "protocol_may_review": False,
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
            "open_gates": ["rebuild exact review scope"],
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
        self.assertTrue(
            self.cases["review-inventory-gate"]["oracle"]["expected"][
                "protocol_may_review"
            ]
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
            self.assertIn("independent_obligations=greeting-change", receipt)
            self.assertNotIn("OBL-", receipt)
            self.assertIn(
                "phase_2_contract_projection=O1 greeting outcome; P1 format_name "
                "and unrelated-output preservation; delivered only after phase-1 "
                "inventory and correctness",
                receipt,
            )
            self.assertIn(
                "workspace=isolated synthetic repository; original history and full "
                "ExecPlan unavailable; the contract-only projection above was "
                "delivered after phase-1 correctness",
                receipt,
            )
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
            "protocol_may_review": False,
            "protocol_may_complete": False,
            "finding_classifications": [],
            "open_gates": [],
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
            "protocol_may_review": False,
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "REVIEW-SEARCH-TRUNCATED",
                    "domain": "receipt",
                    "state": "unknown",
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
            "open_gates": [],
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
            "protocol_may_review": False,
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "SECRET-BASE-1",
                    "domain": "secret",
                    "state": "baseline_unchanged",
                },
                {
                    "identity": "SECRET-OUTPUT-2",
                    "domain": "secret",
                    "state": "unknown",
                    "anchors": ["SECRET-OUTPUT-2"],
                },
                {
                    "identity": "MISSING-SNAPSHOT-REF",
                    "domain": "receipt",
                    "state": "unknown",
                    "anchors": ["1" * 40],
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
                    "identity": "MISSING-SNAPSHOT-REF",
                    "class": "production_condition",
                    "blocking": True,
                    "reason": "The no-commit snapshot has no durable locator.",
                },
            ],
            "open_gates": ["credential must be sanitized", "snapshot ref missing"],
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
        self.assertTrue(
            runner.finding_identity_matches(
                "baseline:test_old_fixture:fixture-17", "fixture-17"
            )
        )
        self.assertTrue(
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
            "protocol_may_review": False,
            "protocol_may_complete": True,
            "finding_classifications": [
                {
                    "identity": "REGRESSION-1",
                    "domain": "other",
                    "state": "candidate_new",
                }
            ],
            "open_gates": ["candidate regression remains open"],
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
        self.assertTrue(any("open_gates" in failure for failure in failures))
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
            "protocol_may_review": False,
            "protocol_may_complete": True,
            "finding_classifications": [
                {
                    "identity": "fixture-17",
                    "domain": "baseline_failure",
                    "state": "baseline_unchanged",
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
        self.assertEqual(runner.match_oracle(result, oracle), [])
        oracle["accepted_baseline_failures"] = [
            "fixture-17",
            "test_old_fixture:fixture-17",
        ]
        self.assertTrue(
            any(
                "ambiguous accepted baseline failure" in failure
                for failure in runner.match_oracle(result, oracle)
            )
        )

    def test_case_validation_rejects_ambiguous_accepted_failure_ids(self) -> None:
        case = json.loads(json.dumps(self.cases["review-admin-cycle"]))
        case["oracle"]["accepted_baseline_failures"] = [
            "fixture-17",
            "test_old_fixture:fixture-17",
        ]
        with self.assertRaisesRegex(ValueError, "ambiguous accepted"):
            runner.validate_case(case, Path("ambiguous.json"))

    def test_baseline_failure_case_requires_structured_identities(self) -> None:
        required = self.cases["compaction-recovery"]["oracle"][
            "required_classifications"
        ]
        self.assertIn(
            {
                "identity": "fixture-17",
                "domain": "baseline_failure",
                "state": "resolved",
            },
            required,
        )
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
        self.assertNotIn("uniqueItems", json.dumps(recovery, sort_keys=True))
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


if __name__ == "__main__":
    unittest.main()
