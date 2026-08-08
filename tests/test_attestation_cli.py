from __future__ import annotations

import base64
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from evaluation.cli import CliError, main, parser, run_mechanical_checks
from tests.attestation_fixtures import CommittedWorkspace, ROOT, write_json


def construction_arguments(directory: Path, workspace, construction, *, spec=None):
    paths = {
        "product": write_json(directory / "product.json", construction["product"]),
        "previous-product": write_json(directory / "previous-product.json", construction["previous_product"]),
        "review-projection": write_json(directory / "review.json", construction["review_projection"]),
        "mappings": write_json(directory / "mappings.json", construction["holdout_mappings"]),
        "caps": write_json(directory / "caps.json", construction["caps"]),
    }
    arguments = ["--repo", str(workspace.root), "--previous-repo", str(workspace.root)]
    for name, path in paths.items():
        arguments.extend((f"--{name}", str(path)))
    if spec is not None:
        arguments.extend(("--spec", str(write_json(directory / "spec.json", spec))))
    return arguments


class CliCommandTests(unittest.TestCase):
    def invoke(self, *arguments: str):
        return subprocess.run(
            [sys.executable, "-B", "-m", "evaluation.cli", *arguments],
            cwd=ROOT, capture_output=True, text=True,
        )

    def test_parser_exposes_only_pure_v3_commands(self):
        choices = next(
            action.choices for action in parser()._actions if getattr(action, "choices", None)
        )
        self.assertEqual(set(choices), {
            "inventory", "materialize", "qualify", "authority", "validate", "checks", "verify",
        })
        for retired in ("prepare-exact-request", "execute", "verify-release", "replay"):
            self.assertNotIn(retired, choices)

    def test_materialize_qualify_authority_and_validate_round_trip(self):
        with CommittedWorkspace() as workspace, tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            construction, spec = workspace.production_construction()
            materialized = self.invoke("materialize", *construction_arguments(directory, workspace, construction))
            self.assertEqual(materialized.returncode, 0, materialized.stderr)
            self.assertEqual(json.loads(materialized.stdout), spec)
            for command in ("qualify", "authority"):
                completed = self.invoke(
                    command, *construction_arguments(directory, workspace, construction, spec=spec),
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                value = json.loads(completed.stdout)
                if command == "qualify":
                    self.assertTrue(value["qualified"])
                else:
                    self.assertFalse(value["authority_authenticated"])
                    self.assertEqual(value["authority_request"]["spec_sha256"], spec["spec_sha256"])
            valid = self.invoke("validate", str(directory / "spec.json"))
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertTrue(json.loads(valid.stdout)["valid"])

    def test_verify_is_truthfully_unverified_without_external_authenticator(self):
        completed = self.invoke("verify")
        self.assertEqual(completed.returncode, 2)
        value = json.loads(completed.stdout)
        self.assertEqual(value["status"], "UNVERIFIED")
        self.assertFalse(value["authenticated"])

    def test_source_drift_stops_qualify_and_authority(self):
        with CommittedWorkspace() as workspace, tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            construction, spec = workspace.production_construction()
            path = workspace.root / "evaluation/provider.py"
            path.write_text(path.read_text() + "\n# drift\n", encoding="utf-8")
            for command in ("qualify", "authority"):
                completed = self.invoke(
                    command, *construction_arguments(directory, workspace, construction, spec=spec),
                )
                self.assertEqual(completed.returncode, 2)
                self.assertIn("error", json.loads(completed.stderr))


class MechanicalChecksTests(unittest.TestCase):
    def test_results_and_loc_are_derived_from_bound_candidate_snapshot(self):
        with CommittedWorkspace() as workspace:
            construction, _ = workspace.production_construction()
            projection = construction["review_projection"]
            real_run = subprocess.run
            def offline_result(command, *args, **kwargs):
                if command[0] == "git" and "-C" in command:
                    return real_run(command, *args, **kwargs)
                return subprocess.CompletedProcess(command, 0, b"derived stdout", b"derived stderr")
            with patch("evaluation.cli.subprocess.run", side_effect=offline_result):
                result = run_mechanical_checks(workspace.root, projection)
            expected = sum(
                len(base64.b64decode(entry["content"]).splitlines())
                for entry in projection["candidate"]["entries"]
                if entry["path"].startswith("evaluation/") and entry["path"].endswith(".py")
            )
            self.assertEqual(result["candidate_snapshot_sha256"], projection["candidate_snapshot_sha256"])
            self.assertEqual(result["production_python_loc"]["total"], expected)
            self.assertEqual(result["production_python_loc"]["total"], sum(
                result["production_python_loc"]["modules"].values()
            ))
            self.assertTrue(result["passed"])
            self.assertTrue(all(item["returncode"] == 0 for item in result["checks"]))
            with self.assertRaises(TypeError):
                run_mechanical_checks(workspace.root, projection, claimed_line_count=1)

    def test_candidate_commit_tree_snapshot_and_clean_worktree_are_required(self):
        with CommittedWorkspace() as workspace:
            construction, _ = workspace.production_construction()
            projection = construction["review_projection"]
            path = workspace.root / "evaluation/README.md"
            path.write_text(path.read_text() + "\ndirty\n", encoding="utf-8")
            with self.assertRaisesRegex(CliError, "immutable candidate"):
                run_mechanical_checks(workspace.root, projection)

    def test_direct_main_verify_does_not_claim_authentication(self):
        output = StringIO()
        with patch("evaluation.cli._print") as emit:
            status = main(["verify"])
        self.assertEqual(status, 2)
        value = emit.call_args.args[0]
        self.assertFalse(value["authenticated"])
        self.assertEqual(value["status"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
