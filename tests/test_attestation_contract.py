from __future__ import annotations

import ast
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import unittest

from evaluation.identity import evaluator_components
from evaluation.provider import FORBIDDEN_PROVIDER_FIELDS, provider_projection
from evaluation.records import RECORD_TYPES
from tests.attestation_fixtures import CANDIDATE_REVISION, bundle


ROOT = Path(__file__).resolve().parents[1]
PRESERVED_SKILL_TREE = "d9e525a267fbf36669d409ba1b4b009a6beeeea5"
CORE_ROLES = {
    "goal-divergence",
    "no-commit-secret",
    "qualification-high-risk",
    "qualification-low-risk",
    "qualification-midflight",
}
HOLDOUTS = {"holdout-recovery", "holdout-safety", "holdout-scope"}


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def manifest() -> dict:
    return json.loads(read(".codex-plugin/plugin.json"))


def skill_parts() -> tuple[dict[str, str], str]:
    raw = read("skills/happycodex/SKILL.md")
    opening, frontmatter, body = raw.split("---", 2)
    if opening:
        raise AssertionError("frontmatter must start at byte zero")
    fields = {}
    for line in frontmatter.strip().splitlines():
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, body.lstrip("\n")


class RepositoryContractTests(unittest.TestCase):
    def test_published_v065_is_immutable_and_current_plan_is_version_derived(self):
        self.assertEqual(CANDIDATE_REVISION, "HEAD")
        self.assertEqual(git("rev-parse", "v0.6.5:skills/happycodex"), PRESERVED_SKILL_TREE)
        latest_tag = git("describe", "--tags", "--abbrev=0", "HEAD")
        self.assertRegex(latest_tag, r"^v\d+\.\d+\.\d+$")
        released_version = latest_tag.removeprefix("v")
        current = manifest()["version"]
        self.assertRegex(current, r"^\d+\.\d+\.\d+$")
        self.assertGreater(tuple(map(int, current.split("."))), tuple(map(int, released_version.split("."))))
        slug = current.replace(".", "-")
        self.assertTrue((ROOT / f"docs/execplans/happycodex-{slug}-clean-break.md").is_file())

    def test_plugin_manifest_and_skill_frontmatter_are_structurally_aligned(self):
        plugin = manifest()
        fields, _ = skill_parts()
        self.assertEqual(plugin["name"], fields["name"])
        self.assertEqual(set(fields), {"name", "description"})
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertEqual(plugin["interface"]["displayName"], "HappyCodex")
        self.assertEqual(plugin["interface"]["capabilities"], ["Read", "Write"])

    def test_product_surfaces_fit_hard_size_budgets(self):
        _, body = skill_parts()
        self.assertLessEqual(len(body.splitlines()), 160)
        self.assertLessEqual(len(body.split()), 1100)
        reference = read("skills/happycodex/references/execplan.md")
        self.assertLessEqual(len(reference.splitlines()), 60)
        self.assertLessEqual(len(reference.split()), 400)
        self.assertLessEqual(len(read("README.md").splitlines()), 100)
        self.assertLessEqual(len(read("README.en.md").splitlines()), 100)

    def test_product_tree_has_only_portable_declarative_surfaces(self):
        root = ROOT / "skills/happycodex"
        files = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(
            files,
            {"SKILL.md", "agents/openai.yaml", "references/execplan.md"},
        )
        self.assertFalse((root / "scripts").exists())

    def test_product_delegates_permissions_to_native_codex(self):
        skill = read("skills/happycodex/SKILL.md")
        template = read("skills/happycodex/references/execplan.md")
        normalized_skill = " ".join(skill.split())
        self.assertIn("Use native Codex permissions", normalized_skill)
        self.assertIn("do not model or repeat them in HappyCodex", normalized_skill)
        self.assertIn("derive changed paths from Git at closure", normalized_skill)
        self.assertNotIn("Ask again only", skill)
        self.assertNotIn("per-path approval", skill)
        self.assertNotIn("grant history", skill)
        self.assertNotIn("Re-ask only", template)
        self.assertNotIn("exact mutable set", template)
        self.assertIn("Workspace or project boundary", template)

    def test_product_guidance_is_isolated_from_evaluator_maintenance(self):
        skill = read("skills/happycodex/SKILL.md")
        self.assertNotIn("evaluation/", skill)
        links = re.findall(r"\]\(([^)]+)\)", skill)
        self.assertFalse(any(link.startswith("evaluation") for link in links))

    def test_current_execplan_is_one_static_record(self):
        version = manifest()["version"].replace(".", "-")
        candidates = sorted((ROOT / "docs/execplans").glob(f"happycodex-{version}*"))
        self.assertEqual([path.name for path in candidates], [f"happycodex-{version}-clean-break.md"])
        plan = candidates[0].read_text(encoding="utf-8")
        self.assertLessEqual(len(plan.splitlines()), 80)
        headings = {line for line in plan.splitlines() if line.startswith("## ")}
        self.assertEqual(
            headings,
            {
                "## Verbatim request",
                "## Outcome",
                "## Envelope",
                "## Baseline and allowed breaks",
                "## Design decision",
                "## Checks, done, and stops",
            },
        )

    def test_public_readmes_are_concise_bilingual_entrypoints(self):
        zh, en = read("README.md"), read("README.en.md")
        self.assertIn("[English](README.en.md)", zh)
        self.assertIn("[简体中文](README.md)", en)
        for surface in (zh, en):
            self.assertEqual(surface.count("codex plugin marketplace add"), 1)
            self.assertEqual(surface.count("$happycodex:happycodex"), 1)
            self.assertLessEqual(sum(line.startswith("## ") for line in surface.splitlines()), 5)

    def test_evaluator_inventory_remains_fixed(self):
        evaluation = ROOT / "evaluation"
        production = {
            name: json.loads((evaluation / name).read_text())
            for name in (
                "manifest-v1.json",
                "provider-fixtures-v1.json",
                "hidden-oracles-v1.json",
                "report-schemas-v1.json",
            )
        }
        self.assertEqual(set(production["manifest-v1.json"]["core_roles"]), CORE_ROLES)
        self.assertEqual(set(production["manifest-v1.json"]["holdout_samples"]), HOLDOUTS)
        self.assertEqual(set(production["provider-fixtures-v1.json"]["core"]), CORE_ROLES)
        self.assertEqual(set(production["hidden-oracles-v1.json"]["core"]), CORE_ROLES)
        self.assertEqual(set(production["report-schemas-v1.json"]["core"]), CORE_ROLES)
        self.assertEqual(set(production["provider-fixtures-v1.json"]["holdouts"]), HOLDOUTS)
        self.assertEqual(set(production["hidden-oracles-v1.json"]["holdouts"]), HOLDOUTS)
        self.assertIsInstance(production["report-schemas-v1.json"]["holdout"], dict)

    def test_eval_spec_topology_has_fixed_behavior_holdout_and_final_units(self):
        selected, baseline, spec, mapping = bundle()
        self.assertTrue(selected and baseline and mapping)
        stages = Counter(unit["stage"] for unit in spec["units"])
        self.assertEqual(stages, {"behavior": 5, "holdout": 6, "exact_final": 1})
        self.assertEqual(len(spec["units"]), 12)

    def test_core_fixture_boundaries_remain_decision_shaping(self):
        fixtures = json.loads(read("evaluation/provider-fixtures-v1.json"))["core"]
        oracles = json.loads(read("evaluation/hidden-oracles-v1.json"))["core"]
        low = fixtures["qualification-low-risk"]
        self.assertEqual(
            {key: low["fixture"][key] for key in ("confirmed", "bounded", "read_only", "local")},
            {"confirmed": True, "bounded": True, "read_only": True, "local": True},
        )
        self.assertEqual(oracles["qualification-low-risk"]["fatal"], {"qualifies": False, "effects.applied": False})
        secret = fixtures["no-commit-secret"]
        self.assertTrue(secret["fixture"]["secret_present"])
        self.assertIsNone(secret["fixture"]["selected_archive"])
        self.assertTrue(secret["workspace"]["git_index_clean"])
        self.assertIsNone(secret["workspace"]["approved_durable_location"])

    def test_midflight_fixture_keeps_qualification_after_new_fact(self):
        fixtures = json.loads(read("evaluation/provider-fixtures-v1.json"))
        oracles = json.loads(read("evaluation/hidden-oracles-v1.json"))
        schemas = json.loads(read("evaluation/report-schemas-v1.json"))
        case = fixtures["core"]["qualification-midflight"]
        self.assertEqual(case["fixture"]["qualification_boundary"], "after-new-fact")
        self.assertFalse(case["workspace"]["plan_covers_write"])
        self.assertFalse(case["workspace"]["candidate_frozen"])
        self.assertEqual(oracles["core"]["qualification-midflight"]["fatal"], {"qualifies": True, "candidate.frozen": False})
        self.assertEqual(set(schemas["core"]["qualification-midflight"]["required"]), {"qualifies", "candidate", "next_action"})

    def test_provider_projection_is_constructed_from_a_closed_allowlist(self):
        case = {
            "role_id": "qualification-low-risk",
            "sample_id": None,
            "prompt": "decide",
            "fixture": {"bounded": True},
            "workspace": {"execution_required": False},
            "runtime": {"network": False},
            "response_schema": {"type": "object"},
        }
        projection = provider_projection(
            case=case,
            product_semantic_sha256="1" * 64,
            external_role_config_sha256="2" * 64,
            profile={"model": "fake", "effort": "high", "tools": ["command_execution"], "timeout_seconds": 30},
        )
        self.assertEqual(
            set(projection),
            {
                "schema_version", "role_id", "sample_id",
                "product_semantic_sha256", "external_role_config_sha256",
                "fixture", "workspace", "prompt", "runtime",
                "response_schema", "neutral_review_brief", "profile",
            },
        )
        self.assertFalse(set(projection) & set(FORBIDDEN_PROVIDER_FIELDS))

    def test_holdout_provider_inputs_are_oracle_blind(self):
        fixtures = json.loads(read("evaluation/provider-fixtures-v1.json"))["holdouts"]
        oracles = json.loads(read("evaluation/hidden-oracles-v1.json"))["holdouts"]
        self.assertEqual(len({case["prompt"] for case in fixtures.values()}), 1)
        oracle_payloads = {json.dumps(value, sort_keys=True) for value in oracles.values()}
        for case in fixtures.values():
            projection = json.dumps(case, sort_keys=True)
            self.assertFalse({"oracle", "expected", "mapping"} & set(case))
            self.assertTrue(all(payload not in projection for payload in oracle_payloads))

    def test_holdouts_are_exactly_three_frozen_pairs(self):
        selected, baseline, spec, mapping = bundle()
        self.assertEqual({pair["pair_id"] for pair in spec["holdouts"]}, HOLDOUTS)
        self.assertEqual(set(mapping), HOLDOUTS)
        for pair in spec["holdouts"]:
            units = [unit for unit in spec["units"] if unit["unit_id"] in pair["unit_ids"]]
            self.assertEqual(len(units), 2)
            self.assertEqual(
                {unit["product_semantic_sha256"] for unit in units},
                {selected["package_semantic_sha256"], baseline["package_semantic_sha256"]},
            )

    def test_only_four_durable_record_types_exist(self):
        expected = {"ProductArtifact", "EvalSpec", "Attestation", "ReleaseReceipt"}
        self.assertEqual(set(RECORD_TYPES), expected)
        discovered = set()
        for path in (ROOT / "evaluation").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and node.value in RECORD_TYPES:
                    discovered.add(node.value)
        self.assertEqual(discovered, expected)

    def test_stateless_evaluator_has_no_ledger_or_retired_engines(self):
        retired = {
            "evaluation/results/current.json",
            "evaluation/contracts-v7.json",
            "evaluation/live.py",
            "evaluation/core/ledger.py",
            "evaluation/core/receipt.py",
            "evaluation/semantic/replay.py",
            "evaluation/corpus/engine.py",
            "evaluation/holdout/engine.py",
        }
        self.assertFalse(any((ROOT / path).exists() for path in retired))

    def test_evaluator_python_stays_within_module_and_total_budgets(self):
        modules = list((ROOT / "evaluation").rglob("*.py"))
        counts = {path: len(path.read_text(encoding="utf-8").splitlines()) for path in modules}
        self.assertLessEqual(sum(counts.values()), 3600)
        self.assertTrue(all(count <= 600 for count in counts.values()), counts)

    def test_evaluator_identity_separates_provider_oracle_and_harness(self):
        components = evaluator_components(ROOT)
        self.assertEqual(
            set(components),
            {
                "evaluator_bundle_sha256",
                "provider_component_sha256",
                "oracle_component_sha256",
                "harness_component_sha256",
            },
        )
        self.assertEqual(len(set(components.values())), 4)

    def test_effect_caps_and_token_qualification_remain_separate(self):
        spec = bundle()[2]
        self.assertEqual(set(spec["effect_cap"]), {"model_calls", "wall_milliseconds"})
        self.assertEqual(set(spec["token_qualification"]), {"input_tokens", "output_tokens"})
        self.assertNotIn("total_cap", spec)


if __name__ == "__main__":
    unittest.main()
