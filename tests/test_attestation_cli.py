from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from evaluation.host import attestation_from_raw
from tests.attestation_fixtures import (
    HOST_CONTRACT, PROFILES, REVEALED_AT, REVIEW_BRIEF, ROOT, TOTAL_CAP, SHA,
    attest_all, bundle, passing_report, write_json,
)


class FreshProcessTests(unittest.TestCase):
    def test_fake_subprocess_raw_stream_verifies_end_to_end(self):
        selected, baseline, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        payload = {
            "started_at": "2026-08-02T00:00:00Z", "frozen_at": "2026-08-02T00:00:10Z",
            "report": passing_report(unit),
            "usage": {"input_tokens": 10, "cached_input_tokens": 0, "cache_write_input_tokens": 0, "output_tokens": 2, "reasoning_output_tokens": 0},
        }
        completed = subprocess.run(
            ["python3", str(ROOT / "tests" / "fake_external_host.py")],
            input=json.dumps(payload), text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        raw = completed.stdout.encode()
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"], raw=raw,
            host_metadata={key: payload[key] for key in ("started_at", "frozen_at")} | {"exit_code": 0, "timed_out": False},
            authority_sha256=SHA["a"],
        )
        self.assertEqual(record["verdict"], "pass")
        self.assertEqual(baseline["external_role_config_sha256"], selected["external_role_config_sha256"])

    def test_cli_materializes_from_versioned_production_inputs(self):
        selected, baseline, spec, blind_mapping = bundle()
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            values = {
                "product": selected, "previous": baseline, "profiles": PROFILES,
                "cap": TOTAL_CAP, "mapping": blind_mapping, "brief": REVIEW_BRIEF,
                "host": HOST_CONTRACT,
            }
            paths = {}
            for name, value in values.items():
                paths[name] = temp / f"{name}.json"
                write_json(paths[name], value)
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "materialize", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--profiles", str(paths["profiles"]), "--total-cap", str(paths["cap"]),
                    "--mapping", str(paths["mapping"]), "--review-brief", str(paths["brief"]),
                    "--host-contract", str(paths["host"]),
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), spec)

    def test_cli_verifies_records_only_with_fixed_host_raw(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws = attest_all(selected, baseline, spec)
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
                write_json(attestation_path, record)
                raw_path.write_bytes(raws[unit_id])
                repeated.extend(["--attestation", str(attestation_path), "--raw", f"{unit_id}={raw_path}"])
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "verify", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--spec", str(paths["spec"]), "--mapping", str(paths["mapping"]),
                    "--revealed-at", REVEALED_AT,
                    *repeated,
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["verified"])
        self.assertNotIn("certified", result)

    def test_cli_rejects_legacy_host_flags(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws = attest_all(selected, baseline, spec)
        record = records[0]
        unit_id = record["unit_id"]
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            paths = {name: temp / f"{name}.json" for name in ("product", "previous", "spec", "mapping", "attestation", "legacy")}
            for name, value in (("product", selected), ("previous", baseline), ("spec", spec), ("mapping", blind_mapping), ("attestation", record), ("legacy", {})):
                write_json(paths[name], value)
            raw_path = temp / "raw.jsonl"
            raw_path.write_bytes(raws[unit_id])
            old_data_flag = "--" + "pro" + "of"
            old_command_flag = old_data_flag + "-ver" + "ifier-command"
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "verify", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--spec", str(paths["spec"]), "--attestation", str(paths["attestation"]),
                    "--raw", f"{unit_id}={raw_path}", old_data_flag, f"{unit_id}={paths['legacy']}",
                    old_command_flag, "/usr/bin/true",
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unrecognized arguments", completed.stderr)


if __name__ == "__main__":
    unittest.main()
