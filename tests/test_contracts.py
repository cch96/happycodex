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


def headings(path: Path) -> list[str]:
    return re.findall(r"^#{1,6} .+$", read(path), flags=re.MULTILINE)


def section_rows(path: Path, heading: str) -> list[list[str]]:
    _, separator, tail = read(path).partition(f"## {heading}\n")
    if not separator:
        return []
    section = tail.split("\n## ", 1)[0]
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {
            "-",
            " ",
        }:
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


class HappyCodexContractTests(unittest.TestCase):
    def test_g013_manifest_and_executor_role_are_exact_artifacts(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.6.0")
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
            item["path"]: item["category"]
            for item in engine_inventory(ROOT)["entries"]
        }
        self.assertEqual(entries["evaluation/executor-role.json"], "artifact")

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
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".", 1)[0])
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(imported - allowed, set())

    def test_runtime_has_exact_event_driven_structure(self) -> None:
        self.assertEqual(
            headings(SKILL),
            [
                "# HappyCodex",
                "## Select and freeze",
                "## Roles and grants",
                "## Event correction",
                "## Implement and recover",
                "## Safety invariants",
                "## Review and complete",
            ],
        )
        rows = section_rows(SKILL, "Event correction")
        self.assertEqual(rows[0], ["Event", "Required correction"])
        self.assertEqual(
            [row[0] for row in rows[1:]],
            [
                "`repeated_attempt_failure`",
                "`new_family`",
                "`repair_batch_end`",
                "`pre_effect`",
                "`candidate_freeze`",
            ],
        )
        self.assertTrue(all(len(row) == 2 and len(row[1].split()) >= 10 for row in rows[1:]))

    def test_runtime_has_exact_safety_matrix(self) -> None:
        rows = section_rows(SKILL, "Safety invariants")
        self.assertEqual(rows[0], ["Boundary", "Invariant"])
        self.assertEqual(
            [row[0] for row in rows[1:]],
            [
                "`authority`",
                "`recovery`",
                "`resource_claim`",
                "`review_isolation`",
                "`cost`",
                "`no_commit`",
                "`goal`",
                "`secret`",
                "`baseline_failure`",
            ],
        )
        self.assertTrue(all(len(row) == 2 and len(row[1].split()) >= 12 for row in rows[1:]))

    def test_runtime_is_bounded_and_maintainer_independent(self) -> None:
        runtime = read(SKILL) + read(EXECPLAN)
        self.assertLessEqual(sum(len(read(path).splitlines()) for path in (SKILL, EXECPLAN)), 262)
        self.assertLessEqual(sum(len(read(path).split()) for path in (SKILL, EXECPLAN)), 2_200)
        self.assertNotIn("evaluation/", runtime)
        self.assertNotIn("timer", runtime.casefold())
        self.assertNotIn("cross-root", runtime.casefold())
        self.assertNotIn("fable", runtime.casefold())

    def test_execplan_template_has_typed_control_tables(self) -> None:
        self.assertEqual(
            section_rows(EXECPLAN, "Roles and authority")[0],
            [
                "Grant",
                "Sequence",
                "Executor",
                "Exact prestate",
                "Paths/resources",
                "Operations/effects",
                "Acceptance",
                "Stop conditions",
                "State",
            ],
        )
        self.assertEqual(
            section_rows(EXECPLAN, "Claims")[0],
            [
                "Claim",
                "Type",
                "Observable contract",
                "Falsifier/oracle",
                "Evidence and source identity",
                "State",
            ],
        )
        self.assertEqual(
            section_rows(EXECPLAN, "Families and event state")[0],
            [
                "Family",
                "Invariant/boundary",
                "Members",
                "Six-surface evidence",
                "Batch",
                "Recurrence",
                "ProgressKey/AttemptKey",
                "Status",
            ],
        )

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
        self.assertEqual(manifest["version"], "0.6.0")
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

    def test_schema_contract_and_validator_obey_exact_dialect_and_budgets(
        self,
    ) -> None:
        from evaluation.core.schema import load_contracts

        contract_path = ROOT / "evaluation" / "contracts-v6.json"
        lines = read(contract_path).splitlines()
        self.assertGreaterEqual(len(lines), 520)
        self.assertLessEqual(len(lines), 650)
        contracts = load_contracts(contract_path)
        schemas = contracts["schemas"]
        self.assertLessEqual(len(schemas), 30)
        allowed = {
            "$ref", "type", "properties", "required", "additionalProperties",
            "items", "enum", "pattern", "minLength", "maxLength", "minimum",
            "maximum", "minItems", "maxItems", "uniqueItems",
        }
        property_count = 0
        pending = list(schemas.values())
        while pending:
            node = pending.pop()
            self.assertLessEqual(set(node), allowed)
            properties = node.get("properties", {})
            property_count += len(properties)
            if properties:
                self.assertEqual(set(properties), set(node["required"]))
                self.assertIs(node["additionalProperties"], False)
                pending.extend(properties.values())
            if "items" in node:
                pending.append(node["items"])
        self.assertLessEqual(property_count, 220)

        schema_path = ROOT / "evaluation" / "core" / "schema.py"
        source = read(schema_path)
        self.assertLessEqual(len(source.splitlines()), 80)
        self.assertNotIn(";", source)
        self.assertGreaterEqual(source.count("\n\n"), 5)
        tree = ast.parse(source)
        compound = (
            ast.AsyncFor, ast.AsyncFunctionDef, ast.AsyncWith, ast.ClassDef,
            ast.For, ast.FunctionDef, ast.If, ast.Try, ast.While, ast.With,
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertEqual(len(node.names), 1)
                modules = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertEqual(len(node.names), 1)
                modules = [node.module.split(".", 1)[0]]
            else:
                modules = []
            self.assertLessEqual(
                set(modules), {"__future__", "json", "pathlib", "re", "typing"}
            )
            if isinstance(node, compound) and node.body:
                self.assertGreater(node.body[0].lineno, node.lineno)

        opaque = set()
        pending = [(f"schemas.{name}", schema) for name, schema in schemas.items()]
        while pending:
            path, node = pending.pop()
            properties = node.get("properties", {})
            kinds = [node.get("type")] if isinstance(node.get("type"), str) else (
                node.get("type") or []
            )
            if "object" in kinds and not properties:
                opaque.add(path)
            pending.extend(
                (f"{path}.properties.{name}", child)
                for name, child in properties.items()
            )
            if "items" in node:
                pending.append((f"{path}.items", node["items"]))
        self.assertEqual(opaque, {
            "schemas.case.properties.fixture",
            "schemas.case.properties.oracle",
            "schemas.evidence_record.properties.actual",
            "schemas.evidence_record.properties.producer",
            "schemas.evidence_record.properties.subject",
            "schemas.evidence_record.properties.transcript.items",
            "schemas.gate_plan.properties.template.properties.env",
            "schemas.ledger.properties.accepted_evidence",
            "schemas.ledger.properties.authorities",
            "schemas.ledger.properties.certification",
            "schemas.ledger.properties.cost",
            "schemas.ledger.properties.coverage",
            "schemas.ledger.properties.freeze",
            "schemas.ledger.properties.planned_impact",
            "schemas.ledger.properties.planned_invocations",
            "schemas.ledger.properties.source_anchor",
            "schemas.planned_impact.properties.initial_scope",
            "schemas.planned_impact.properties.live_calls",
            "schemas.snapshot.properties.corpus.properties.cases",
            "schemas.snapshot.properties.engine.properties.categories",
            "schemas.snapshot.properties.engine.properties.scopes",
            "schemas.snapshot.properties.holdout.properties.pairs",
            "schemas.tool_identity",
        })

        ceilings = {
            "evaluation/cli.py": 185,
            "evaluation/live.py": 470,
            "evaluation/core/identity.py": 630,
            "evaluation/core/impact.py": 490,
            "evaluation/core/ledger.py": 670,
            "evaluation/core/receipt.py": 260,
            "evaluation/core/schema.py": 80,
            "evaluation/corpus/engine.py": 2150,
            "evaluation/holdout/blind.py": 195,
            "evaluation/holdout/compare.py": 155,
            "evaluation/holdout/engine.py": 340,
        }
        for relative, ceiling in ceilings.items():
            self.assertLessEqual(len(read(ROOT / relative).splitlines()), ceiling, relative)
        semantic = list((ROOT / "evaluation" / "semantic").glob("*.py"))
        initializers = [
            ROOT / "evaluation" / "__init__.py",
            ROOT / "evaluation" / "core" / "__init__.py",
            ROOT / "evaluation" / "corpus" / "__init__.py",
            ROOT / "evaluation" / "holdout" / "__init__.py",
        ]
        self.assertLessEqual(sum(len(read(path).splitlines()) for path in semantic), 1200)
        self.assertLessEqual(sum(len(read(path).splitlines()) for path in initializers), 15)
        self.assertEqual(sum(ceilings.values()) + 1200 + 15, 6840)
        production = [
            path for path in (ROOT / "evaluation").rglob("*.py")
            if "__pycache__" not in path.parts
        ]
        self.assertLessEqual(sum(len(read(path).splitlines()) for path in production), 6850)


if __name__ == "__main__":
    unittest.main()
