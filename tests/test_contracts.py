from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "happycodex"
SKILL = SKILL_ROOT / "SKILL.md"
EXECPLAN = SKILL_ROOT / "references" / "execplan.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
CLAIM_HELPER = SKILL_ROOT / "scripts" / "resource_claim.py"
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
README = ROOT / "README.md"
EXECUTOR_ROLE = ROOT / "evaluation" / "executor-role.json"

EXPECTED_RUNTIME_FILES = {
    "skills/happycodex/SKILL.md",
    "skills/happycodex/agents/openai.yaml",
    "skills/happycodex/references/execplan.md",
    "skills/happycodex/scripts/resource_claim.py",
}
FORBIDDEN_PLUGIN_SURFACES = (
    ".app.json",
    ".mcp.json",
    "hooks.json",
    "hooks",
    "apps",
    "mcp",
    "scripts",
    "skills/happycodex/hooks",
)
RELEASE_VERSION = re.compile(r"^0\.6\.5$")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative_files(root: Path) -> set[str]:
    return {
        path.relative_to(ROOT).as_posix() for path in root.rglob("*") if path.is_file()
    }


def parse_simple_yaml_mapping(text: str) -> dict[str, object]:
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, separator, raw_value = raw_line.strip().partition(":")
        if not separator or not key:
            raise ValueError(f"unsupported YAML line: {raw_line!r}")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        value = raw_value.strip()
        if value:
            parent[key] = json.loads(value) if value.startswith('"') else value
        else:
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
    return root


class HappyCodexContractTests(unittest.TestCase):
    def test_g013_manifest_and_executor_role_are_exact_artifacts(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIsNotNone(RELEASE_VERSION.fullmatch(manifest["version"]))
        role = json.loads(EXECUTOR_ROLE.read_text(encoding="utf-8"))
        self.assertEqual(
            role,
            {
                "schema_version": 1,
                "role_id": "happycodex_executor",
                "model": "gpt-5.6-sol",
                "reasoning_effort": "high",
                "writer_policy": "fixed_executor_only",
                "delegation": "forbidden",
                "repository_effects": "exact_grant_and_resource_claim",
                "external_effects": "separate_exact_user_authority",
            },
        )
        from evaluation.core.identity import engine_inventory

        entries = {
            item["path"]: item
            for item in engine_inventory(ROOT)["entries"]
        }
        self.assertIn("evaluation/executor-role.json", entries)

    def test_runtime_surface_is_exact_and_has_no_custom_engine(self) -> None:
        self.assertEqual(relative_files(SKILL_ROOT), EXPECTED_RUNTIME_FILES)
        manifest = json.loads(read(MANIFEST))
        self.assertEqual(manifest["name"], "happycodex")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue({"hooks", "mcpServers", "apps"}.isdisjoint(manifest))
        for relative in FORBIDDEN_PLUGIN_SURFACES:
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_runtime_surface_oracle_detects_untracked_and_hidden_files(self) -> None:
        for relative, content in (
            ("hooks/unexpected.py", b"raise RuntimeError\n"),
            ("__pycache__/hidden.pyc", b"unexpected packaged bytecode"),
        ):
            probe = SKILL_ROOT / relative
            self.assertFalse(probe.exists())
            probe.parent.mkdir()
            probe.write_bytes(content)
            try:
                self.assertIn(
                    probe.relative_to(ROOT).as_posix(), relative_files(SKILL_ROOT)
                )
                self.assertNotEqual(relative_files(SKILL_ROOT), EXPECTED_RUNTIME_FILES)
            finally:
                probe.unlink()
                probe.parent.rmdir()

    def test_python_validation_uses_only_declared_stdlib_dependencies(self) -> None:
        allowed = set(sys.stdlib_module_names) | {
            "__future__",
            "evaluation",
            "tests",
        }
        for path in (
            *sorted((ROOT / "evaluation").rglob("*.py")),
            *sorted((SKILL_ROOT / "scripts").rglob("*.py")),
            *ROOT.glob("tests/*.py"),
        ):
            imported: set[str] = set()
            for node in ast.walk(ast.parse(read(path), filename=str(path))):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif (
                    isinstance(node, ast.ImportFrom)
                    and node.module
                    and node.level == 0
                ):
                    imported.add(node.module.split(".", 1)[0])
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(imported - allowed, set())

    def test_runtime_is_bounded_and_maintainer_independent(self) -> None:
        runtime = read(SKILL) + read(EXECPLAN)
        self.assertLessEqual(sum(len(read(path).splitlines()) for path in (SKILL, EXECPLAN)), 262)
        self.assertLessEqual(sum(len(read(path).split()) for path in (SKILL, EXECPLAN)), 2_200)
        self.assertNotIn("evaluation/", runtime)
        self.assertNotIn("timer", runtime.casefold())
        self.assertNotIn("cross-root", runtime.casefold())
        self.assertNotIn("fable", runtime.casefold())

    def test_claim_helper_is_packaged_and_not_a_runtime_controller(self) -> None:
        tree = ast.parse(read(CLAIM_HELPER), filename=str(CLAIM_HELPER))
        command_names = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value in {"acquire", "verify", "release"}
        }
        self.assertEqual(command_names, {"acquire", "verify", "release"})
        imported = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertTrue({"socket", "threading", "asyncio"}.isdisjoint(imported))

    def test_manifest_and_public_install_surfaces_are_coherent(self) -> None:
        manifest = json.loads(read(MANIFEST))
        self.assertIsNotNone(RELEASE_VERSION.fullmatch(manifest["version"]))
        self.assertEqual(manifest["repository"], "https://github.com/cch96/happycodex")
        marketplace = json.loads(read(MARKETPLACE))
        self.assertEqual(marketplace["name"], "happycodex")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "happycodex")
        self.assertEqual(entry["source"], {"source": "local", "path": "./"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertIn("$happycodex:happycodex", read(README))

    def test_public_release_version_is_exact(self) -> None:
        version = json.loads(read(MANIFEST))["version"]
        self.assertIsNotNone(RELEASE_VERSION.fullmatch(version))
        for invalid in (
            "0.6.0",
            "0.6.5+codex.20260730123456",
            "0.5.0+codex.20260730123456",
            "0.6.0+codex.20260730123456+codex.20260730123457",
        ):
            with self.subTest(version=invalid):
                self.assertIsNone(RELEASE_VERSION.fullmatch(invalid))

    def test_ui_metadata_is_namespaced_and_small(self) -> None:
        interface = parse_simple_yaml_mapping(read(OPENAI_YAML))["interface"]
        self.assertEqual(
            set(interface), {"display_name", "short_description", "default_prompt"}
        )
        self.assertEqual(interface["display_name"], "HappyCodex")
        self.assertLessEqual(len(interface["short_description"]), 64)
        self.assertIn("$happycodex:happycodex", interface["default_prompt"])
        prompts = json.loads(read(MANIFEST))["interface"]["defaultPrompt"]
        self.assertLessEqual(len(prompts), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in prompts))
        self.assertTrue(all("$happycodex:happycodex" in prompt for prompt in prompts))

    def test_public_surfaces_reject_bare_invocation_and_retired_branding(self) -> None:
        paths = (README, MANIFEST, MARKETPLACE, SKILL, EXECPLAN, OPENAI_YAML)
        for path in paths:
            self.assertNotRegex(read(path), r"\$happycodex(?!:happycodex)", path.name)
        retired = (
            "review runner",
            "hash chain",
            "successor receipt",
            "runner epoch",
            "bootstrap attestation",
            "retry challenge",
            "self-hosted review",
            "canonical series",
            "native-codex-loop",
            "native codex loop",
        )
        public_text = "\n".join(read(path) for path in paths).casefold()
        self.assertTrue(all(term not in public_text for term in retired))

    def test_evaluator_cleanly_targets_public_02_baseline(self) -> None:
        active = "\n".join(
            read(path)
            for path in sorted((ROOT / "evaluation").rglob("*.py"))
            if "__pycache__" not in path.parts
        )
        self.assertIn("PUBLIC_02_PACKAGE_ARTIFACT_SHA256", active)
        self.assertIn("PUBLIC_02_PACKAGE_SEMANTIC_SHA256", active)
        self.assertIn("public-0.2", active)
        self.assertNotIn("PUBLIC_040", active)
        self.assertNotIn("public-0.4.0", active)

    def test_repository_has_no_tracked_generated_python_artifacts(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertFalse(
            any("__pycache__" in path or path.endswith(".pyc") for path in tracked)
        )

    def test_schema_dialect_recursively_rejects_exactness_and_wrong_primitives(
        self,
    ) -> None:
        from evaluation.core.schema import validate_structure

        definitions = {
            "leaf": {
                "type": "object",
                "properties": {"count": {"type": "integer"}},
                "required": ["count"],
                "additionalProperties": False,
            }
        }
        schema = {
            "type": "object",
            "properties": {"child": {"$ref": "leaf"}},
            "required": ["child"],
            "additionalProperties": False,
        }
        valid = {"child": {"count": 1}}
        self.assertEqual(validate_structure(valid, schema, definitions), valid)
        invalid = (
            {},
            {"child": {"count": 1}, "extra": True},
            {"child": {}},
            {"child": {"count": 1, "extra": True}},
            {"child": {"count": True}},
            {"child": {"count": "1"}},
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_structure(value, schema, definitions)

    def test_schema_dialect_rejects_value_range_and_cardinality_drift(self) -> None:
        from evaluation.core.schema import validate_structure

        schema = {
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "enum": ["aa", "ab"],
                    "pattern": "^a[a-b]$",
                    "minLength": 2,
                    "maxLength": 2,
                },
                "count": {"type": "integer", "minimum": 1, "maximum": 2},
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 2,
                    "uniqueItems": True,
                },
            },
            "required": ["token", "count", "items"],
            "additionalProperties": False,
        }
        valid = {"token": "aa", "count": 1, "items": ["x", "y"]}
        self.assertEqual(validate_structure(valid, schema, {}), valid)
        for field, value in (
            ("token", "zz"),
            ("token", "a"),
            ("count", 0),
            ("count", 3),
            ("items", []),
            ("items", ["x", "y", "z"]),
            ("items", ["x", "x"]),
        ):
            invalid = copy.deepcopy(valid)
            invalid[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate_structure(invalid, schema, {})

    def test_schema_dialect_rejects_unknown_cyclic_and_deep_references(self) -> None:
        from evaluation.core.schema import validate_structure

        with self.assertRaisesRegex(ValueError, "reference"):
            validate_structure({}, {"$ref": "missing"}, {})
        with self.assertRaisesRegex(ValueError, "cyclic|reference"):
            validate_structure({}, {"$ref": "a"}, {"a": {"$ref": "b"}, "b": {"$ref": "a"}})
        deep = {f"n{index}": {"$ref": f"n{index + 1}"} for index in range(7)}
        deep["n7"] = {"type": "object", "properties": {}, "required": [],
                      "additionalProperties": False}
        with self.assertRaisesRegex(ValueError, "depth|reference"):
            validate_structure({}, {"$ref": "n0"}, deep)

    def test_schema_loader_eagerly_rejects_unused_bad_declarations(self) -> None:
        from evaluation.core.schema import load_contracts

        invalid_sets = {
            "unsupported": {"unused": {"type": "string", "title": "ignored"}},
            "unknown-ref": {"unused": {"$ref": "missing"}},
            "cycle": {"a": {"$ref": "b"}, "b": {"$ref": "a"}},
            "no-op": {"unused": {"type": "integer", "pattern": "^ignored$"}},
        }
        deep = {f"n{index}": {"$ref": f"n{index + 1}"} for index in range(7)}
        deep["n7"] = {"type": "string"}
        invalid_sets["deep"] = deep
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "contracts.json"
            for label, schemas in invalid_sets.items():
                path.write_text(
                    json.dumps({"schema_version": 1, "schemas": schemas}),
                    encoding="utf-8",
                )
                with self.subTest(label=label), self.assertRaises(ValueError):
                    load_contracts(path)

if __name__ == "__main__":
    unittest.main()
