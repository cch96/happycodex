from __future__ import annotations

from copy import deepcopy
import base64
import json
import os
import subprocess
import unittest

from evaluation.canonical import canonical_sha256
from evaluation.identity import (
    IdentityError, evaluator_components, product_artifact_from_tree,
    review_projection_from_git, validate_review_projection,
)
from evaluation.manifest import (
    ManifestError, build_production_spec, load_production_inputs,
    qualified_evaluation_authority_request,
)
from evaluation.policy import PROJECTION_NAMES, UNIT_TOPOLOGY
from evaluation.records import RecordError, build_eval_spec, validate_eval_spec
from tests.attestation_fixtures import CommittedWorkspace, ROOT


class TopologyContractTests(unittest.TestCase):
    def test_construction_and_validation_require_exact_five_six_one(self):
        with CommittedWorkspace() as workspace:
            construction, spec = workspace.production_construction()
            self.assertIs(validate_eval_spec(spec), spec)
            stages = [unit["stage"] for unit in spec["units"]]
            self.assertEqual(stages.count("behavior"), 5)
            self.assertEqual(stages.count("holdout"), 6)
            self.assertEqual(stages.count("exact_final"), 1)
            self.assertEqual(
                [(unit["unit_id"], unit["stage"]) for unit in spec["units"]],
                [(unit.unit_id, unit.stage) for unit in UNIT_TOPOLOGY],
            )
            self.assertEqual(build_production_spec(**construction), spec)

    def test_explicit_four_behavior_mutation_fails_during_build(self):
        with CommittedWorkspace() as workspace:
            _, spec = workspace.production_construction()
            values = deepcopy({
                key: value for key, value in spec.items()
                if key not in {"record_type", "schema_version", "record_sha256", "spec_subject_sha256", "spec_sha256"}
            })
            values["units"][0]["stage"] = "exact_final"
            with self.assertRaisesRegex(RecordError, "UNIT_TOPOLOGY"):
                build_eval_spec(**values)


class ProductConsumerTests(unittest.TestCase):
    def test_named_consumer_projections_follow_marketplace_and_plugin(self):
        product = product_artifact_from_tree(
            ROOT, source_identity="working", baseline_identity="baseline",
        )
        self.assertEqual(tuple(product["projections"]), PROJECTION_NAMES)
        paths = {
            name: {entry["path"] for entry in projection["entries"]}
            for name, projection in product["projections"].items()
        }
        self.assertEqual(paths["public_docs"], {"README.md", "README.en.md"})
        self.assertEqual(paths["marketplace_locator"], {
            ".agents/plugins/marketplace.json", ".codex-plugin/plugin.json",
        })
        self.assertIn("skills/happycodex/SKILL.md", paths["plugin_runtime"])
        self.assertEqual(paths["provider_guidance"], {
            "skills/happycodex/SKILL.md", "skills/happycodex/references/execplan.md",
        })

    def test_evaluator_only_mutation_leaves_product_identity_unchanged(self):
        with CommittedWorkspace() as workspace:
            before = product_artifact_from_tree(
                workspace.root, source_identity="same", baseline_identity="base",
            )
            path = workspace.root / "evaluation/README.md"
            path.write_text(path.read_text() + "\nmaintainer note\n", encoding="utf-8")
            after = product_artifact_from_tree(
                workspace.root, source_identity="same", baseline_identity="base",
            )
            self.assertEqual(before["artifact_sha256"], after["artifact_sha256"])

    def test_product_byte_mode_delete_symlink_and_escape_change_or_reject(self):
        with CommittedWorkspace() as workspace:
            baseline = product_artifact_from_tree(
                workspace.root, source_identity="same", baseline_identity="base",
            )
            readme = workspace.root / "README.md"
            readme.write_text(readme.read_text() + "\nchanged\n", encoding="utf-8")
            changed = product_artifact_from_tree(
                workspace.root, source_identity="same", baseline_identity="base",
            )
            self.assertNotEqual(baseline["artifact_sha256"], changed["artifact_sha256"])
        with CommittedWorkspace() as workspace:
            skill = workspace.root / "skills/happycodex/SKILL.md"
            os.chmod(skill, 0o755)
            changed = product_artifact_from_tree(
                workspace.root, source_identity="same", baseline_identity="base",
            )
            normal = product_artifact_from_tree(
                ROOT, source_identity="same", baseline_identity="base",
            )
            self.assertNotEqual(normal["artifact_sha256"], changed["artifact_sha256"])
        with CommittedWorkspace() as workspace:
            (workspace.root / "README.en.md").unlink()
            deleted = product_artifact_from_tree(
                workspace.root, source_identity="same", baseline_identity="base",
            )
            entry = next(item for item in deleted["projections"]["public_docs"]["entries"] if item["path"] == "README.en.md")
            self.assertEqual(entry["state"], "absent")
        with CommittedWorkspace() as workspace:
            skill = workspace.root / "skills/happycodex/SKILL.md"
            skill.unlink(); skill.symlink_to("references/execplan.md")
            with self.assertRaises(IdentityError):
                product_artifact_from_tree(workspace.root, source_identity="same", baseline_identity="base")
        with CommittedWorkspace() as workspace:
            marketplace = workspace.root / ".agents/plugins/marketplace.json"
            value = json.loads(marketplace.read_text())
            value["plugins"][0]["source"]["path"] = "../escape"
            marketplace.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(IdentityError):
                product_artifact_from_tree(workspace.root, source_identity="same", baseline_identity="base")

    def test_component_drift_stops_qualified_authority(self):
        with CommittedWorkspace() as workspace:
            construction, spec = workspace.production_construction()
            path = workspace.root / "evaluation/provider.py"
            path.write_text(path.read_text() + "\n# drift\n", encoding="utf-8")
            with self.assertRaises(ManifestError):
                qualified_evaluation_authority_request(spec, **construction)


class ReviewProjectionTests(unittest.TestCase):
    def test_snapshot_contains_every_tracked_regular_blob_and_only_oracle_is_digest_only(self):
        with CommittedWorkspace() as workspace:
            projection = review_projection_from_git(
                workspace.root, baseline=workspace.baseline, candidate="HEAD",
            )
            snapshot = projection["candidate"]
            tracked = {
                row.split("\t", 1)[1]
                for row in workspace._git("ls-tree", "-r", "HEAD").splitlines()
            }
            self.assertEqual({entry["path"] for entry in snapshot["entries"]}, tracked)
            private = [entry for entry in snapshot["entries"] if entry["visibility"] == "digest_only"]
            self.assertEqual([entry["path"] for entry in private], ["evaluation/hidden-oracles-v1.json"])
            for entry in snapshot["entries"]:
                if entry["visibility"] == "readable":
                    self.assertEqual(len(base64.b64decode(entry["content"])), entry["size_bytes"])

    def test_projection_content_changed_paths_and_identity_are_derived(self):
        with CommittedWorkspace() as workspace:
            path = workspace.root / "docs/execplans/happycodex-0-10-v3-thin-verifier.md"
            path.write_text(path.read_text() + "\nprojection change\n", encoding="utf-8")
            candidate = workspace.commit()
            projection = review_projection_from_git(
                workspace.root, baseline=workspace.baseline, candidate=candidate,
            )
            self.assertIn(path.relative_to(workspace.root).as_posix(), projection["changed_paths"])
            for mutate in (
                lambda value: value["candidate"]["entries"].pop(0),
                lambda value: value["changed_paths"].append("fake.diff"),
                lambda value: value["candidate"].__setitem__("commit", "fake-source"),
            ):
                bad = deepcopy(projection); mutate(bad)
                with self.assertRaises(IdentityError):
                    validate_review_projection(bad)

    def test_qualified_path_rejects_omitted_but_self_consistent_git_projection(self):
        with CommittedWorkspace() as workspace:
            construction, _ = workspace.production_construction()
            projection = deepcopy(construction["review_projection"])
            for side in ("baseline", "candidate"):
                snapshot = projection[side]
                snapshot["entries"] = [
                    entry for entry in snapshot["entries"] if entry["path"] != "AGENTS.md"
                ]
                body = {key: snapshot[key] for key in snapshot if key != "snapshot_sha256"}
                snapshot["snapshot_sha256"] = canonical_sha256(body)
            projection["changed_paths"] = []
            projection["candidate_snapshot_sha256"] = projection["candidate"]["snapshot_sha256"]
            body = {key: projection[key] for key in projection if key != "projection_sha256"}
            projection["projection_sha256"] = canonical_sha256(body)
            construction["review_projection"] = projection
            spec = build_production_spec(**construction)
            with self.assertRaises(ManifestError):
                qualified_evaluation_authority_request(spec, **construction)


class PublicContractTests(unittest.TestCase):
    def test_public_metadata_and_templates_are_v013_and_bounded(self):
        plugin = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(plugin["version"], "0.13.0")
        self.assertEqual(plugin["name"], marketplace["plugins"][0]["name"])
        self.assertEqual(plugin["skills"], "./skills/")
        skill = (ROOT / "skills/happycodex/SKILL.md").read_text()
        self.assertTrue(skill.startswith("---\nname: happycodex\n"))
        self.assertLessEqual(len(skill.splitlines()), 120)
        self.assertLessEqual(len((ROOT / "skills/happycodex/references/execplan.md").read_text().splitlines()), 80)
        self.assertLessEqual(len((ROOT / "README.md").read_text().splitlines()), 80)
        self.assertLessEqual(len((ROOT / "README.en.md").read_text().splitlines()), 80)

    def test_boundary_routing_contract_is_closed_and_consistent(self):
        inputs = load_production_inputs(ROOT)
        case = inputs["cases"]["core"]["context-isolation"]
        oracle = inputs["oracles"]["core"]["context-isolation"]
        input_schema = inputs["schemas"]["provider_inputs"]["context-isolation"]
        schema = inputs["schemas"]["provider_outputs"]["context-isolation"]
        answers = {
            "judgment_core": "primary_direct",
            "focused_verification": "primary_direct",
            "stable_large_supporting_evidence": "one_read_only_agent_before_primary_ingestion",
            "independent_evidence_bodies": "parallel_read_only_agents_only_when_materially_helpful",
            "external_challenge_or_review": "primary_direct_tool_call_and_observation_assigned_question_only",
            "stable_substantial_implementation": "one_worker_before_primary_editing",
            "small_coherent_correction": "primary_direct",
            "agent_unavailable_or_failed": "state_fallback_before_primary_direct_work",
            "overlapping_mutable_paths": "single_writer_per_overlap",
            "context_offload_relation": "independent_of_parallelism",
        }
        scenario_fields = tuple(key for key in answers if key != "context_offload_relation")
        self.assertEqual(tuple(case["context"]["scenarios"]), scenario_fields)
        self.assertEqual(case["workspace"], {
            "remaining_context": "ample", "context_offload_requires_parallelism": False,
        })
        self.assertEqual(oracle["fatal"], answers)
        self.assertEqual(oracle["quality"], {
            "stable_large_supporting_evidence": answers["stable_large_supporting_evidence"],
            "external_challenge_or_review": answers["external_challenge_or_review"],
            "stable_substantial_implementation": answers["stable_substantial_implementation"],
            "context_offload_relation": answers["context_offload_relation"],
        })
        scenario_schema = input_schema["properties"]["context"]["properties"]["scenarios"]
        self.assertEqual(tuple(scenario_schema["properties"]), scenario_fields)
        self.assertEqual(scenario_schema["required"], list(scenario_fields))
        self.assertFalse(scenario_schema["additionalProperties"])
        self.assertEqual(tuple(schema["properties"]), tuple(answers))
        self.assertEqual(schema["required"], list(answers))
        routing_bytes = json.dumps(
            {"case": case, "oracle": oracle, "schema": schema}, sort_keys=True,
        )
        self.assertNotIn("one_offload_lane", routing_bytes)
        self.assertNotIn("parallel_read_lanes", routing_bytes)
        skill = " ".join((ROOT / "skills/happycodex/SKILL.md").read_text().split())
        for phrase in (
            "## Route work by boundary",
            "keep one focused verification direct",
            "requires a supporting body to be searched, summarized, compared, or filtered",
            "before the Primary ingests",
            "send substantial implementation to one native worker before editing",
            "Keep a small coherent correction direct",
            "Keep every challenge or review within its assigned question",
            "the Primary invokes that tool directly and observes its result directly",
            "Do not create a native agent to call, relay, or wrap the external invocation",
            "state the fallback before the Primary",
            "one fresh native read-only, no-history, blocker-only terminal review",
            "Keep that native exact-final review separate from any optional external challenge or review",
        ):
            self.assertIn(phrase, skill)

        external_scenario = "external_model_or_tool_bounded_assigned_question"
        self.assertEqual(
            case["context"]["scenarios"]["external_challenge_or_review"],
            external_scenario,
        )
        self.assertEqual(
            scenario_schema["properties"]["external_challenge_or_review"]["enum"],
            [external_scenario],
        )
        self.assertEqual(
            schema["properties"]["external_challenge_or_review"]["enum"][0],
            answers["external_challenge_or_review"],
        )

        candidate_oracle = inputs["oracles"]["core"]["candidate-review"]
        candidate_schema = inputs["schemas"]["provider_outputs"]["candidate-review"]
        native_exact_final = "one_fresh_native_read_only_blocker_only"
        self.assertEqual(candidate_oracle["fatal"]["terminal_review"], native_exact_final)
        self.assertEqual(candidate_oracle["quality"]["terminal_review"], native_exact_final)
        self.assertIn(
            native_exact_final,
            candidate_schema["properties"]["terminal_review"]["enum"],
        )

        chinese = " ".join((ROOT / "README.md").read_text().split())
        english = " ".join((ROOT / "README.en.md").read_text().split())
        self.assertIn("由 Primary 直接调用和观察", chinese)
        self.assertIn("不得创建原生 agent 代为调用、中转或包装外部调用", chinese)
        self.assertIn("独立的 fresh 原生只读、blocker-only 终审", chinese)
        self.assertIn("the Primary invoke and observe it directly", english)
        self.assertIn("never create a native agent to call, relay, or wrap", english)
        self.assertIn("separate fresh native read-only, blocker-only terminal review", english)

    def test_session_guardrails_are_closed_and_consistent(self):
        inputs = load_production_inputs(ROOT)

        candidate = inputs["cases"]["core"]["candidate-review"]
        candidate_oracle = inputs["oracles"]["core"]["candidate-review"]
        candidate_input = inputs["schemas"]["provider_inputs"]["candidate-review"]
        candidate_output = inputs["schemas"]["provider_outputs"]["candidate-review"]
        self.assertEqual(
            candidate["context"]["review_budget"],
            "authorized_repair_and_replacement_exhausted",
        )
        self.assertEqual(candidate["workspace"]["untracked_digest_present"], True)
        self.assertEqual(candidate["workspace"]["immutable_copy_reachable"], False)
        self.assertEqual(candidate_oracle["fatal"]["automatic_continuation_allowed"], False)
        self.assertEqual(candidate_oracle["fatal"]["exhausted_review_action"], "return_to_user")
        self.assertEqual(candidate_oracle["fatal"]["untracked_digest_durable"], False)
        self.assertEqual(
            candidate_oracle["fatal"]["untracked_digest_closure"],
            "modified_not_frozen",
        )
        self.assertFalse(candidate_input["properties"]["context"]["additionalProperties"])
        self.assertFalse(candidate_input["properties"]["workspace"]["additionalProperties"])
        self.assertFalse(candidate_output["additionalProperties"])
        for field in (
            "automatic_continuation_allowed",
            "exhausted_review_action",
            "untracked_digest_durable",
            "untracked_digest_closure",
        ):
            self.assertIn(field, candidate_output["required"])

        effect = inputs["cases"]["core"]["effect-closure"]
        effect_oracle = inputs["oracles"]["core"]["effect-closure"]
        effect_input = inputs["schemas"]["provider_inputs"]["effect-closure"]
        effect_output = inputs["schemas"]["provider_outputs"]["effect-closure"]
        self.assertEqual(effect["context"]["cleanup_target"], "branch_or_worktree")
        self.assertEqual(effect["workspace"]["cleanup_evidence_complete"], False)
        self.assertEqual(effect_oracle["fatal"]["cleanup_allowed"], False)
        self.assertEqual(effect_oracle["fatal"]["cleanup_action"], "stop_preserve")
        self.assertFalse(effect_input["properties"]["context"]["additionalProperties"])
        self.assertFalse(effect_input["properties"]["workspace"]["additionalProperties"])
        self.assertFalse(effect_output["additionalProperties"])
        self.assertIn("cleanup_allowed", effect_output["required"])
        self.assertIn("cleanup_action", effect_output["required"])

        skill = " ".join((ROOT / "skills/happycodex/SKILL.md").read_text().split())
        self.assertIn(
            "Before deleting a branch, worktree, or other recovery surface, prove required "
            "candidate, cutover, effect, and rollback evidence remains durably reachable",
            skill,
        )
        self.assertIn(
            "After that replacement review, any adverse result returns to the user",
            skill,
        )

    def test_published_v065_skill_tree_is_exact(self):
        observed = subprocess.check_output(
            ["git", "rev-parse", "refs/tags/v0.6.5:skills/happycodex"], cwd=ROOT, text=True,
        ).strip()
        self.assertEqual(observed, "d9e525a267fbf36669d409ba1b4b009a6beeeea5")

    def test_evaluator_components_are_separate_and_product_excludes_them(self):
        components = evaluator_components(ROOT)
        self.assertEqual(set(components), {"provider_input", "oracle", "harness"})
        self.assertEqual(len(set(components.values())), 3)
        product = product_artifact_from_tree(ROOT, source_identity="x", baseline_identity="y")
        self.assertNotIn("component", json.dumps(product))


if __name__ == "__main__":
    unittest.main()
