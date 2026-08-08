from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import unittest

from evaluation.policy import RECORD_TYPES, UNIT_TOPOLOGY
from tests.attestation_fixtures import ROOT


class EvaluatorStructureTests(unittest.TestCase):
    def modules(self):
        return {path.stem: path for path in (ROOT / "evaluation").glob("*.py")}

    def test_import_dag_is_acyclic(self):
        modules = self.modules()
        graph = {name: set() for name in modules}
        for name, path in modules.items():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("evaluation."):
                    dependency = node.module.split(".", 1)[1]
                    if dependency in graph:
                        graph[name].add(dependency)
        visiting, visited = set(), set()
        def visit(name):
            if name in visiting:
                self.fail(f"evaluation import cycle reaches {name}")
            if name in visited:
                return
            visiting.add(name)
            for dependency in graph[name]:
                visit(dependency)
            visiting.remove(name); visited.add(name)
        for name in graph:
            visit(name)

    def test_execution_imports_exist_only_in_cli_and_git_identity(self):
        allowed = {"cli": {"subprocess", "tempfile", "os"}, "identity": {"subprocess"}}
        for name, path in self.modules().items():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = {
                alias.name.split(".")[0]
                for node in ast.walk(tree) if isinstance(node, ast.Import)
                for alias in node.names
            }
            prohibited = imports & {"subprocess", "socket", "requests", "urllib", "tempfile"}
            self.assertEqual(prohibited, allowed.get(name, set()) & prohibited, name)

    def test_line_budgets_are_computed_from_current_source(self):
        counts = {
            path.name: len(path.read_bytes().splitlines())
            for path in (ROOT / "evaluation").glob("*.py")
        }
        self.assertLessEqual(sum(counts.values()), 3200, counts)
        self.assertTrue(all(lines <= 600 for lines in counts.values()), counts)

    def test_topology_and_record_inventory_are_literal_and_unique(self):
        self.assertEqual(len(RECORD_TYPES), 4)
        self.assertEqual(len(set(RECORD_TYPES)), 4)
        self.assertEqual(len(UNIT_TOPOLOGY), 12)
        self.assertEqual(len({unit.unit_id for unit in UNIT_TOPOLOGY}), 12)

    def test_index_is_untouched_and_v065_tree_is_preserved(self):
        staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        self.assertEqual(staged.returncode, 0)
        tree = subprocess.check_output(
            ["git", "rev-parse", "refs/tags/v0.6.5:skills/happycodex"], cwd=ROOT, text=True,
        ).strip()
        self.assertEqual(tree, "d9e525a267fbf36669d409ba1b4b009a6beeeea5")


if __name__ == "__main__":
    unittest.main()
