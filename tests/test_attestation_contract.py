from __future__ import annotations

from copy import deepcopy
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from evaluation.canonical import canonical_sha256
from evaluation.identity import (
    IdentityError, build_review_projection, evaluator_components,
    product_artifact_from_tree, product_projections, review_projection_from_git,
    review_snapshot_from_git, validate_review_projection,
)
from evaluation.manifest import (
    ManifestError, build_production_spec, load_production_inputs,
    public_provider_inputs, qualified_evaluation_authority_request,
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
        self.assertIn("hooks/hooks.json", paths["source_distribution"])
        self.assertIn("hooks/session_firewall.py", paths["source_distribution"])
        self.assertIn("hooks/hooks.json", paths["plugin_runtime"])
        self.assertIn("hooks/session_firewall.py", paths["plugin_runtime"])
        self.assertEqual(paths["provider_guidance"], {
            "skills/happycodex/SKILL.md", "skills/happycodex/references/effects.md",
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
            skill.unlink(); skill.symlink_to("references/effects.md")
            with self.assertRaises(IdentityError):
                product_artifact_from_tree(workspace.root, source_identity="same", baseline_identity="base")
        with CommittedWorkspace() as workspace:
            marketplace = workspace.root / ".agents/plugins/marketplace.json"
            value = json.loads(marketplace.read_text())
            value["plugins"][0]["source"]["path"] = "../escape"
            marketplace.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(IdentityError):
                product_artifact_from_tree(workspace.root, source_identity="same", baseline_identity="base")

    def test_optional_hook_bytes_mode_delete_and_redirect_are_classified(self):
        for mutation in ("bytes", "mode", "delete", "symlink"):
            with self.subTest(mutation=mutation), CommittedWorkspace() as workspace:
                hooks = workspace.root / "hooks"
                hooks.mkdir(exist_ok=True)
                script = hooks / "session_firewall.py"
                script.write_text("print('{}')\n", encoding="utf-8")
                config = hooks / "hooks.json"
                config.write_text('{"hooks": {}}\n', encoding="utf-8")
                before = product_projections(workspace.root)["plugin_runtime"]
                if mutation == "bytes":
                    script.write_text("print('{}')  # changed\n", encoding="utf-8")
                elif mutation == "mode":
                    os.chmod(script, 0o755)
                elif mutation == "delete":
                    config.unlink()
                else:
                    script.unlink()
                    script.symlink_to("hooks.json")
                    with self.assertRaises(IdentityError):
                        product_projections(workspace.root)
                    continue
                after = product_projections(workspace.root)["plugin_runtime"]
                self.assertNotEqual(before["projection_sha256"], after["projection_sha256"])
                if mutation == "delete":
                    entry = next(item for item in after["entries"] if item["path"] == "hooks/hooks.json")
                    self.assertEqual(entry["state"], "absent")

    def test_previous_reference_inventory_and_optional_hooks_are_materialized(self):
        with CommittedWorkspace() as workspace, tempfile.TemporaryDirectory() as raw:
            previous_root = Path(raw) / "previous"
            shutil.copytree(workspace.root, previous_root)
            # The previous distribution can have a different reference inventory
            # and optional hooks without a version-specific compatibility reader.
            reference = previous_root / "skills/happycodex/references/effects.md"
            reference.rename(reference.with_name("operation-notes.md"))
            skill = previous_root / "skills/happycodex/SKILL.md"
            skill.write_text(skill.read_text().replace("references/effects.md", "references/operation-notes.md"))
            hooks = previous_root / "hooks"
            hooks.mkdir(exist_ok=True)
            (hooks / "hooks.json").write_text('{"hooks": {}}\n')
            (hooks / "session_firewall.py").write_text("print('{}')\n")
            subprocess.check_call(
                ["git", "-C", str(previous_root), "add", "-A"],
                stdout=subprocess.DEVNULL,
            )
            subprocess.check_call(
                ["git", "-C", str(previous_root), "commit", "-qm", "different reference inventory and optional hooks"],
                stdout=subprocess.DEVNULL,
            )
            previous_commit = subprocess.check_output(
                ["git", "-C", str(previous_root), "rev-parse", "HEAD"],
                text=True,
            ).strip()
            previous_product = product_artifact_from_tree(
                previous_root,
                source_identity=previous_commit,
                baseline_identity="baseline",
                source_kind="git_tree",
            )
            for projection_name in ("source_distribution", "plugin_runtime"):
                entries = {
                    entry["path"]: entry
                    for entry in previous_product["projections"][projection_name]["entries"]
                }
                for path in ("hooks/hooks.json", "hooks/session_firewall.py"):
                    self.assertEqual(entries[path]["state"], "present")

            construction, _ = workspace.production_construction()
            construction["previous_root"] = previous_root
            construction["previous_product"] = previous_product
            construction["review_projection"] = build_review_projection(
                baseline=review_snapshot_from_git(previous_root, "HEAD"),
                candidate=review_snapshot_from_git(workspace.root, "HEAD"),
            )
            spec = build_production_spec(**construction)
            self.assertEqual(
                spec["previous_product_artifact_sha256"],
                previous_product["artifact_sha256"],
            )

    def test_hooks_root_redirect_and_non_directory_are_rejected(self):
        for replacement in ("symlink", "file"):
            with CommittedWorkspace() as workspace:
                hooks = workspace.root / "hooks"
                if hooks.exists():
                    shutil.rmtree(hooks)
                if replacement == "symlink":
                    hooks.symlink_to("skills")
                else:
                    hooks.write_text("not a directory", encoding="utf-8")
                with self.assertRaises(IdentityError):
                    product_projections(workspace.root)

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
    def test_public_product_is_v2_with_resolvable_guidance_and_no_default_hooks(self):
        plugin = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(plugin["version"], "2.0.4")
        self.assertEqual(plugin["name"], marketplace["plugins"][0]["name"])
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertNotIn("hooks", plugin)
        skill = (ROOT / "skills/happycodex/SKILL.md").read_text()
        self.assertTrue(skill.startswith("---\nname: happycodex\n"))
        self.assertTrue((ROOT / "skills/happycodex/references/effects.md").is_file())
        self.assertIn("(references/effects.md)", skill)
        self.assertFalse((ROOT / "skills/happycodex/references/execplan.md").exists())
        runtime = product_projections(ROOT)["plugin_runtime"]["entries"]
        hooks = [entry for entry in runtime if entry["path"].startswith("hooks/")]
        self.assertTrue(all(entry["state"] == "absent" for entry in hooks))


    def test_scope_stability_contract_separates_authorization_closure_and_footprint(self):
        inputs = load_production_inputs(ROOT)
        decisions = inputs["oracles"]["core"]["candidate-review"]["fatal"]["continuation"]
        self.assertTrue(decisions["safe_task_owned_surface_extension"])
        self.assertTrue(decisions["safe_additive_incidental_footprint"])
        for scenario in (
            "system_or_shared_install_target",
            "destructive_shared_cache_mutation",
            "uncertain_footprint_classification",
        ):
            self.assertFalse(decisions[scenario])

    def test_root_convergence_contract_is_evidence_gated_and_non_runtime(self):
        inputs = load_production_inputs(ROOT)
        case = inputs["cases"]["core"]["candidate-review"]
        oracle = inputs["oracles"]["core"]["candidate-review"]
        output = inputs["schemas"]["provider_outputs"]["candidate-review"]
        self.assertIn("completed", case["context"]["advisory_pass_scenario"])
        self.assertIn("no new decision-changing evidence", case["context"]["advisory_pass_scenario"])
        self.assertEqual(oracle["fatal"]["advisory_pass_action"], "stop_and_report")
        self.assertEqual(oracle["fatal"]["advisory_pass_status"], "not_go")
        self.assertIn("advisory_pass_action", output["required"])
        self.assertIn("advisory_pass_status", output["required"])

    def test_review_admission_contract_is_public_and_consistent(self):
        inputs = load_production_inputs(ROOT)
        oracle = inputs["oracles"]["core"]["candidate-review"]
        output = inputs["schemas"]["provider_outputs"]["candidate-review"]
        self.assertEqual(
            oracle["fatal"]["terminal_review"],
            "one_fresh_native_read_only_blocker_only",
        )
        self.assertEqual(oracle["fatal"]["mutation_action"], "refreeze")
        self.assertEqual(oracle["fatal"]["exhausted_review_action"], "return_to_user")
        self.assertIn("one_fresh_native_read_only_blocker_only", output["properties"]["terminal_review"]["enum"])

    def test_proportional_blocker_admission_matrix_is_closed_and_consistent(self):
        inputs = load_production_inputs(ROOT)
        candidate = inputs["cases"]["core"]["candidate-review"]
        oracle = inputs["oracles"]["core"]["candidate-review"]
        input_schema = inputs["schemas"]["provider_inputs"]["candidate-review"]
        output_schema = inputs["schemas"]["provider_outputs"]["candidate-review"]
        scenarios = candidate["context"]["finding_admission_scenarios"]
        new_expected = {
            "plan_only_fsync_durability_invariant": False,
            "user_required_crash_durable_ack": True,
            "authorized_alias_audit_history": False,
            "unauthorized_alias_effect_scope": True,
            "verified_authoritative_migration_extra_scan": False,
            "migration_marker_not_consumer_reachable": True,
        }
        process_expected = {
            "healthy_unchanged_monitor_revalidation_gate": False,
            "local_harness_not_effect_ready_exact_final": False,
            "candidate_ready_material_candidate_missing_exact_final": True,
            "reviewed_same_tree_binding_refresh_code_rereview": False,
            "binding_review_tuple_native_mismatch": True,
            "plan_only_permission_gate": False,
            "missing_standard_path_permission": True,
            "plan_only_archive_workaround": False,
            "plan_only_user_decision": False,
            "test_login_zero_effect_recovery_grant": False,
            "generate_unknown_effect_retry": True,
            "metered_read_local_postprocess_recovery_grant": False,
            "metered_read_growing_cost_without_cap": True,
            "explicit_no_limit_causal_recovery_grant": False,
            "explicit_no_limit_blind_retry": True,
            "partial_publish_or_deploy_retry": True,
            "stockai_required_contract_failure": True,
            "plan_only_zero_automatic_retry_ban": False,
            "plan_only_repair_count_limit": False,
        }
        expected = {
            "gpu2_normal_path_bytecode_breaks_run": True,
            "gpu2_plan_only_zero_mib": False,
            "gpu2_manual_injected_pyc": False,
            "gpu2_empty_nonconsumer_tmp": False,
            "gpu2_self_resolve_reconfirmation": False,
            "stockai_required_raw_effect_output_missing": True,
            "stockai_consumer_code_changed": True,
            "stockai_evidence_only_full_suite_rerun": False,
            "stockai_one_finding_per_repair": False,
            "calcifer_required_manual_video_parity_missing": True,
            "calcifer_reconstructible_cache_delete_permission": False,
            "calcifer_disposable_symlink_delete_permission": False,
            "calcifer_external_stop_acceptance_request": False,
            "workflow_candidate_drift": True,
            "workflow_partial_or_ambiguous_effect": True,
            "workflow_target_or_cap_mismatch": True,
            "workflow_no_review_additional_terminal_review": False,
            "workflow_direct_publish_repeated_broad_preflight": False,
            "normal_local_real_outcome_failure": True,
            "normal_local_terminal_review": False,
            "high_risk_reachable_new_material_regression": True,
            "high_risk_user_cap_breach_labeled_cosmetic": True,
            "one_shot_amendment_implies_retry": True,
            "one_shot_amendment_implies_broader_target": True,
            "robustness_required_injection_failure": True,
            "robustness_unrequired_injection_failure": False,
            "unchanged_consumer_evidence_only_full_rerun": False,
            "changed_consumer_input_relevant_checks": True,
            "uncertain_consumer_classification_relevant_checks": True,
            **new_expected,
            **process_expected,
        }
        fields = tuple(expected)
        scenario_schema = input_schema["properties"]["context"]["properties"][
            "finding_admission_scenarios"
        ]
        answer_schema = output_schema["properties"]["finding_admitted"]

        self.assertEqual(tuple(scenarios), fields)
        self.assertEqual(tuple(scenario_schema["properties"]), fields)
        self.assertEqual(scenario_schema["required"], list(fields))
        self.assertFalse(scenario_schema["additionalProperties"])
        self.assertEqual(tuple(answer_schema["properties"]), fields)
        self.assertEqual(answer_schema["required"], list(fields))
        self.assertFalse(answer_schema["additionalProperties"])
        for field in fields:
            self.assertEqual(
                scenario_schema["properties"][field],
                {"type": "string", "enum": [scenarios[field]]},
            )
            self.assertEqual(answer_schema["properties"][field], {"type": "boolean"})
        self.assertEqual(oracle["fatal"]["finding_admitted"], expected)
        self.assertEqual(
            {field: oracle["fatal"]["finding_admitted"][field] for field in new_expected},
            new_expected,
        )
        self.assertEqual(
            {field: oracle["fatal"]["finding_admitted"][field] for field in process_expected},
            process_expected,
        )
        semantics = "true_means_must_block_or_stop_false_means_optional_or_non_blocking"
        self.assertEqual(oracle["fatal"]["finding_admitted_semantics"], semantics)
        self.assertEqual(
            output_schema["properties"]["finding_admitted_semantics"],
            {"type": "string", "enum": [semantics]},
        )
        self.assertIn(
            "For finding_admitted, true means the scenario must block or stop under the "
            "supported-path admission rule; false means it is optional or non-blocking.",
            candidate["prompt"],
        )
        self.assertIn("finding_admission_scenarios", input_schema["properties"]["context"]["required"])
        self.assertIn("finding_admitted_semantics", output_schema["required"])
        self.assertIn("finding_admitted", output_schema["required"])

    def test_optional_routing_keeps_the_remaining_contract_closed(self):
        inputs = load_production_inputs(ROOT)
        case = inputs["cases"]["core"]["context-isolation"]
        oracle = inputs["oracles"]["core"]["context-isolation"]
        input_schema = inputs["schemas"]["provider_inputs"]["context-isolation"]
        output = inputs["schemas"]["provider_outputs"]["context-isolation"]
        answers = {
            "judgment_core": "primary_direct",
            "focused_verification": "primary_direct",
            "bounded_current_fact_lookup": "primary_direct",
            "independent_evidence_bodies": "parallel_read_only_agents_only_when_materially_helpful",
            "external_challenge_or_review": "primary_direct_tool_call_and_observation_assigned_question_only",
            "small_coherent_correction": "primary_direct",
            "agent_unavailable_or_failed": "state_fallback_before_primary_direct_work",
            "explicit_host_delegation_denial": "primary_direct_record_denial",
            "spawn_unavailable_or_failed": "primary_direct_fallback_record_evidence",
            "caller_parameter_rejection_corrected_spawn_succeeds": "use_spawned_worker_after_corrected_call",
            "overlapping_mutable_paths": "single_writer_per_overlap",
            "context_offload_relation": "independent_of_parallelism",
        }
        scenarios = case["context"]["scenarios"]
        fields = tuple(key for key in answers if key != "context_offload_relation")
        schema = input_schema["properties"]["context"]["properties"]["scenarios"]
        self.assertEqual(tuple(scenarios), fields)
        self.assertEqual(tuple(schema["properties"]), fields)
        self.assertEqual(schema["required"], list(fields))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(oracle["fatal"], answers)
        self.assertEqual(tuple(output["properties"]), tuple(answers))
        self.assertEqual(output["required"], list(answers))
        self.assertFalse(output["additionalProperties"])
        for name in fields:
            self.assertEqual(schema["properties"][name], {"type": "string", "enum": [scenarios[name]]})
            self.assertIn(answers[name], output["properties"][name]["enum"])
        for name, expected in oracle["quality"].items():
            self.assertEqual(expected, answers[name])
        retired = {
            "broad_current_fact_recommendation", "stable_large_supporting_evidence",
            "stable_substantial_implementation", "skill_requested_delegation_under_proactive_only_restriction",
        }
        self.assertFalse(retired.intersection(scenarios))
        self.assertFalse(retired.intersection(oracle["fatal"]))
        self.assertFalse(retired.intersection(oracle["quality"]))
        self.assertEqual(case["workspace"], {"remaining_context": "ample", "context_offload_requires_parallelism": False})

    def test_writer_continuity_matrix_is_hard_state_closed_and_consistent(self):
        inputs = load_production_inputs(ROOT)
        case = inputs["cases"]["core"]["writer-continuity"]
        oracle = inputs["oracles"]["core"]["writer-continuity"]
        input_schema = inputs["schemas"]["provider_inputs"]["writer-continuity"]
        output_schema = inputs["schemas"]["provider_outputs"]["writer-continuity"]
        scenarios = {
            "terminal_failure": "fixed_writer_terminated_with_failure",
            "confirmed_unreachable_or_inactive_writer":
                "fixed_writer_confirmed_unreachable_or_terminally_inactive",
            "no_file_diff_elapsed_reasoning_or_wait_active_writer":
                "no_file_diff_after_elapsed_reasoning_or_wait_while_fixed_writer_active",
            "live_no_blocker_or_progress_report":
                "fixed_writer_reports_live_progress_or_no_blocker",
            "uncertain_liveness_without_hard_evidence":
                "fixed_writer_liveness_uncertain_without_terminal_or_unreachable_evidence",
        }
        actions = {
            "terminal_failure": "reconstruct_from_state",
            "confirmed_unreachable_or_inactive_writer": "reconstruct_from_state",
            "no_file_diff_elapsed_reasoning_or_wait_active_writer": "continue_fixed_writer",
            "live_no_blocker_or_progress_report": "continue_fixed_writer",
            "uncertain_liveness_without_hard_evidence": "focused_status_query",
        }
        scenario_schema = input_schema["properties"]["context"]["properties"]["scenarios"]
        action_schema = output_schema["properties"]["continuity_actions"]

        self.assertIn("independently", case["prompt"])
        self.assertEqual(case["context"]["scenarios"], scenarios)
        self.assertEqual(case["workspace"], {
            "fixed_writer_selected": True, "index_clean": True,
        })
        self.assertEqual(tuple(scenario_schema["properties"]), tuple(scenarios))
        self.assertEqual(scenario_schema["required"], list(scenarios))
        self.assertFalse(scenario_schema["additionalProperties"])
        self.assertEqual(tuple(action_schema["properties"]), tuple(actions))
        self.assertEqual(action_schema["required"], list(actions))
        self.assertFalse(action_schema["additionalProperties"])
        for name, facts in scenarios.items():
            with self.subTest(scenario=name):
                self.assertEqual(
                    scenario_schema["properties"][name],
                    {"type": "string", "enum": [facts]},
                )
                self.assertEqual(
                    action_schema["properties"][name]["enum"][0], actions[name],
                )

        loss_predicate = "terminal_failure_or_confirmed_unreachability_only"
        self.assertEqual(oracle["fatal"]["overlap_policy"], "one_writer")
        self.assertEqual(oracle["fatal"]["continuity_loss_predicate"], loss_predicate)
        self.assertEqual(oracle["fatal"]["continuity_actions"], actions)
        self.assertFalse(oracle["fatal"]["writer_reported_blocker_proves_loss"])
        self.assertFalse(oracle["fatal"]["summary_authority"])
        self.assertEqual(oracle["quality"]["continuity_loss_predicate"], loss_predicate)
        self.assertEqual(oracle["quality"]["continuity_actions"], actions)
        self.assertFalse(oracle["quality"]["summary_authority"])
        self.assertEqual(
            output_schema["properties"]["continuity_loss_predicate"]["enum"][0],
            loss_predicate,
        )
        self.assertIn("writer_reported_blocker_proves_loss", output_schema["required"])
        self.assertIn("summary_authority", output_schema["required"])

        raw_skill = (ROOT / "skills/happycodex/SKILL.md").read_text()


    def test_process_proportionality_contract_is_closed_and_consistent(self):
        inputs = load_production_inputs(ROOT)
        effect = inputs["cases"]["core"]["effect-closure"]
        oracle = inputs["oracles"]["core"]["effect-closure"]
        output = inputs["schemas"]["provider_outputs"]["effect-closure"]

        self.assertEqual(
            effect["prompt"],
            "Classify material effect outcomes and bounded causal recovery without inferring success.",
        )
        self.assertEqual(oracle["fatal"]["not_landed_action"], "bounded_causal_recovery")
        self.assertEqual(
            oracle["fatal"]["retry_requires"],
            "authoritative_effect_side_zero_effect",
        )
        self.assertEqual(
            oracle["quality"]["retry_requires"],
            "authoritative_effect_side_zero_effect",
        )
        self.assertIn(
            "bounded_causal_recovery",
            output["properties"]["not_landed_action"]["enum"],
        )
        self.assertNotIn(
            "bounded_recovery",
            output["properties"]["not_landed_action"]["enum"],
        )
        self.assertIn(
            "authoritative_effect_side_zero_effect",
            output["properties"]["retry_requires"]["enum"],
        )
        self.assertNotIn(
            "authenticated_zero_effect",
            output["properties"]["retry_requires"]["enum"],
        )


    def test_session_guardrails_are_closed_and_consistent(self):
        inputs = load_production_inputs(ROOT)

        candidate = inputs["cases"]["core"]["candidate-review"]
        candidate_oracle = inputs["oracles"]["core"]["candidate-review"]
        candidate_input = inputs["schemas"]["provider_inputs"]["candidate-review"]
        candidate_output = inputs["schemas"]["provider_outputs"]["candidate-review"]
        self.assertEqual(
            candidate["context"]["review_budget"],
            "user_explicit_repair_and_replacement_limit_exhausted",
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

    def test_goal_continuation_contract_is_independent_closed_and_oracle_blind(self):
        inputs = load_production_inputs(ROOT)
        candidate = inputs["cases"]["core"]["candidate-review"]
        oracle = inputs["oracles"]["core"]["candidate-review"]
        input_schema = inputs["schemas"]["provider_inputs"]["candidate-review"]
        output_schema = inputs["schemas"]["provider_outputs"]["candidate-review"]
        scenarios = candidate["context"]["continuation_scenarios"]
        expected = {
            "lost_goal_identity": False,
            "post_go_ungranted_effects": False,
            "narrow_reply_named_repair": False,
            "same_boundary_candidate_change": True,
            "preauthorized_not_yet_repair": True,
            "safe_task_owned_surface_extension": True,
            "safe_additive_incidental_footprint": True,
            "system_or_shared_install_target": False,
            "destructive_shared_cache_mutation": False,
            "uncertain_footprint_classification": False,
            "exhausted_repair_budget": False,
            "pending_user_decision": False,
        }
        fields = tuple(expected)

        self.assertEqual(
            candidate["prompt"],
            "Freeze the consumer input and decide whether terminal review is required. "
            "Classify each continuation_scenarios and finding_admission_scenarios entry "
            "independently using only its own facts. "
            "For finding_admitted, true means the scenario must block or stop under the "
            "supported-path admission rule; false means it is optional or non-blocking. "
            "Apply the existing top-level review_budget only to "
            "automatic_continuation_allowed and exhausted_review_action.",
        )
        self.assertNotIn("review_budget", scenarios)

        scenario_schema = input_schema["properties"]["context"]["properties"]["continuation_scenarios"]
        continuation_schema = output_schema["properties"]["continuation"]
        self.assertEqual(tuple(scenarios), fields)
        self.assertEqual(len(set(scenarios.values())), len(fields))
        self.assertTrue(all(type(value) is str and value for value in scenarios.values()))
        self.assertEqual(tuple(scenario_schema["properties"]), fields)
        self.assertEqual(scenario_schema["required"], list(fields))
        self.assertFalse(scenario_schema["additionalProperties"])
        self.assertEqual(tuple(continuation_schema["properties"]), fields)
        self.assertEqual(continuation_schema["required"], list(fields))
        self.assertFalse(continuation_schema["additionalProperties"])
        for field in fields:
            self.assertEqual(
                scenario_schema["properties"][field],
                {"type": "string", "enum": [scenarios[field]]},
            )
            self.assertEqual(continuation_schema["properties"][field], {"type": "boolean"})
        self.assertFalse(input_schema["properties"]["context"]["additionalProperties"])
        self.assertFalse(output_schema["additionalProperties"])
        self.assertIn("continuation_scenarios", input_schema["properties"]["context"]["required"])
        self.assertIn("continuation", output_schema["required"])
        neutral_facts = " ".join(scenarios.values()).lower()
        for conclusion in ("should continue", "must continue", "should stop", "must stop"):
            self.assertNotIn(conclusion, neutral_facts)
        self.assertEqual(oracle["fatal"]["continuation"], expected)
        self.assertIs(oracle["fatal"]["automatic_continuation_allowed"], False)
        self.assertEqual(oracle["fatal"]["exhausted_review_action"], "return_to_user")
        sentinel = "PRIVATE-GOAL-CONTINUATION-ORACLE"
        changed = deepcopy(inputs)
        changed["oracles"]["core"]["candidate-review"]["fatal"]["continuation"]["lost_goal_identity"] = sentinel
        public = public_provider_inputs(changed)
        self.assertNotIn(sentinel, json.dumps(public, sort_keys=True))
        self.assertNotIn(json.dumps(expected, sort_keys=True), json.dumps(public, sort_keys=True))

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
