from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from evaluation.host import attestation_from_raw
from tests.attestation_fixtures import (
    PROFILE, REVEALED_AT, REVIEW_BRIEF, ROOT, TOTAL_CAP, SHA,
    attest_all, bundle, host_proof, passing_report, write_json,
)


class FreshProcessTests(unittest.TestCase):
    def test_fake_subprocess_raw_stream_verifies_end_to_end(self):
        selected, baseline, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        payload = {
            "started_at": "2026-08-02T00:00:00Z", "frozen_at": "2026-08-02T00:00:10Z",
            "report": passing_report(unit),
            "usage": {"model_calls": 1, "input_tokens": 10, "output_tokens": 2, "wall_milliseconds": 10},
            "terminal": {"classification": "success", "provider_reached": True, "complete": True},
        }
        completed = subprocess.run(
            ["python3", str(ROOT / "tests" / "fake_external_host.py")],
            input=json.dumps(payload), text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        raw = completed.stdout.encode()
        proof = host_proof(unit, raw)
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"], raw=raw,
            authority_sha256=SHA["a"], host_proof=proof,
        )
        self.assertEqual(record["verdict"], "pass")
        self.assertNotEqual(baseline["external_role_config_sha256"], selected["external_role_config_sha256"])

    def test_cli_materializes_from_versioned_production_inputs(self):
        selected, baseline, spec, blind_mapping = bundle()
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            values = {
                "product": selected, "previous": baseline, "profile": PROFILE,
                "cap": TOTAL_CAP, "mapping": blind_mapping, "brief": REVIEW_BRIEF,
            }
            paths = {}
            for name, value in values.items():
                paths[name] = temp / f"{name}.json"
                write_json(paths[name], value)
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "materialize", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--profile", str(paths["profile"]), "--total-cap", str(paths["cap"]),
                    "--mapping", str(paths["mapping"]), "--review-brief", str(paths["brief"]),
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), spec)

    def test_cli_verifies_records_only_with_external_raw_and_proof(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws, proofs = attest_all(selected, baseline, spec)
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            fixed = {"product": selected, "previous": baseline, "spec": spec, "mapping": blind_mapping}
            paths = {}
            for name, value in fixed.items():
                paths[name] = temp / f"{name}.json"
                write_json(paths[name], value)
            repeated = []
            for index, record in enumerate(records):
                unit_id = record["unit_id"]
                attestation_path = temp / f"attestation-{index}.json"
                raw_path = temp / f"raw-{index}.jsonl"
                proof_path = temp / f"proof-{index}.json"
                write_json(attestation_path, record)
                raw_path.write_bytes(raws[unit_id])
                write_json(proof_path, proofs[unit_id])
                repeated.extend(["--attestation", str(attestation_path), "--raw", f"{unit_id}={raw_path}", "--proof", f"{unit_id}={proof_path}"])
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "verify", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--spec", str(paths["spec"]), "--mapping", str(paths["mapping"]),
                    "--revealed-at", REVEALED_AT, "--proof-verifier-command", "/usr/bin/true",
                    *repeated,
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["verified"])
        self.assertNotIn("certified", result)

    def test_cli_rejects_external_proof_verifier_failure(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws, proofs = attest_all(selected, baseline, spec)
        record = records[0]
        unit_id = record["unit_id"]
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            paths = {name: temp / f"{name}.json" for name in ("product", "previous", "spec", "mapping", "attestation", "proof")}
            for name, value in (("product", selected), ("previous", baseline), ("spec", spec), ("mapping", blind_mapping), ("attestation", record), ("proof", proofs[unit_id])):
                write_json(paths[name], value)
            raw_path = temp / "raw.jsonl"
            raw_path.write_bytes(raws[unit_id])
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "verify", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--spec", str(paths["spec"]), "--attestation", str(paths["attestation"]),
                    "--raw", f"{unit_id}={raw_path}", "--proof", f"{unit_id}={paths['proof']}",
                    "--proof-verifier-command", "/usr/bin/false",
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
