"""Reusable schema-v3 records and a disposable committed workspace."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any, Callable

from evaluation.canonical import canonical_sha256, canonical_text, sealed
from evaluation.holdout import judge_fixed_holdouts
from evaluation.host import construct_attestation, construct_release_receipt
from evaluation.identity import product_artifact_from_tree, review_projection_from_git
from evaluation.manifest import build_production_spec, load_production_inputs
from evaluation.policy import PROJECTION_NAMES, UNIT_TOPOLOGY
from evaluation.provider import (
    evaluation_authority_request_payload, exact_final_effect_subject,
    release_authority_request_payload, release_effect_subject,
)
from evaluation.records import build_eval_spec, build_product_artifact
from evaluation.verify import (
    attestation_evidence_statement, authenticate_attestation,
    release_evidence_statement, verify_effect_sequence, verify_evaluation,
    verify_release,
)
from tests.fake_external_host import FakeExternalBoundary


ROOT = Path(__file__).resolve().parents[1]


def sha(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def reseal(record: dict[str, Any], mutate: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    body = deepcopy({key: value for key, value in record.items() if key != "record_sha256"})
    mutate(body)
    return sealed(body)


def _projection(seed: str, name: str) -> dict[str, Any]:
    body = f"{seed}:{name}".encode()
    entries = [{
        "path": f"{name}.txt", "mode": "100644", "state": "present",
        "sha256": hashlib.sha256(body).hexdigest(), "size_bytes": len(body),
    }]
    return {"entries": entries, "projection_sha256": canonical_sha256(entries)}


def fake_product(seed: str) -> dict[str, Any]:
    return build_product_artifact(
        source_provenance={"kind": "content_snapshot", "identity": seed, "baseline_identity": "base"},
        projections={name: _projection(seed, name) for name in PROJECTION_NAMES},
    )


class RecordFactory:
    """Build internally consistent records without any real external effect."""

    def __init__(self, *, recovery_cap: int = 1, absolute_wall: int = 5000):
        self.boundary = FakeExternalBoundary(recovery_cap=recovery_cap)
        self.product = fake_product("candidate")
        self.previous_product = fake_product("previous")
        self.contract_sha = sha("fixed-review-contract")
        self.schema = {
            "type": "object", "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"], "additionalProperties": False,
        }
        self.exact_schema = deepcopy(
            load_production_inputs(ROOT)["schemas"]["provider_outputs"]["exact_final"]
        )
        self.oracle = {"fatal": {"ok": True}, "quality": {"ok": True}}
        self.mappings = {
            f"holdout-{sample}": {
                f"holdout-{sample}-a": "candidate", f"holdout-{sample}-b": "baseline",
            }
            for sample in ("recovery", "safety", "scope")
        }
        self.inputs: dict[str, dict[str, Any]] = {}
        self.schemas: dict[str, dict[str, Any]] = {}
        self.oracles: dict[str, dict[str, Any] | None] = {}
        units = []
        for topology in UNIT_TOPOLOGY:
            if topology.stage == "exact_final":
                provider_input = {
                    "candidate_product_artifact_sha256": self.product["artifact_sha256"],
                    "review_policy_sha256": self.contract_sha,
                    "review_projection_sha256": sha("review-projection"),
                    "response_schema": canonical_text(self.exact_schema),
                }
                schema, oracle = self.exact_schema, None
                oracle_identity = canonical_sha256({
                    "review_contract_sha256": self.contract_sha,
                    "response_schema_sha256": canonical_sha256(schema),
                })
                effect = exact_final_effect_subject(
                    candidate_product_artifact_sha256=self.product["artifact_sha256"],
                    review_contract_sha256_value=self.contract_sha,
                )
            else:
                provider_input = {
                    "unit_id": topology.unit_id,
                    "response_schema": canonical_text(self.schema),
                }
                schema, oracle = self.schema, self.oracle
                oracle_identity = canonical_sha256(oracle)
                effect = sha(f"effect:{topology.unit_id}")
            self.inputs[topology.unit_id] = provider_input
            self.schemas[topology.unit_id] = schema
            self.oracles[topology.unit_id] = oracle
            units.append({
                **topology._asdict(),
                "provider_input_sha256": canonical_sha256(provider_input),
                "oracle_sha256": oracle_identity,
                "invocation_sha256": sha(f"invocation:{topology.unit_id}"),
                "effect_subject_sha256": effect,
            })
        pairs = [{
            "pair_id": pair_id, "sample_id": pair_id.removeprefix("holdout-"),
            "unit_ids": list(mapping),
            "mapping_commitment_sha256": canonical_sha256(mapping),
        } for pair_id, mapping in self.mappings.items()]
        self.spec = build_eval_spec(
            product_artifact_sha256=self.product["artifact_sha256"],
            previous_product_artifact_sha256=self.previous_product["artifact_sha256"],
            component_identities={name: sha(f"component:{name}") for name in (
                "provider_input", "oracle", "harness",
            )},
            review_contract_sha256=self.contract_sha, units=units, holdout_pairs=pairs,
            caps={
                "model_calls": 12, "candidate_token_ratio_milli": 1250,
                "unit_wall_milliseconds": 1000,
                "absolute_wall_milliseconds": absolute_wall,
                "recovery_attempts": recovery_cap,
            },
        )
        self.evaluation_request = evaluation_authority_request_payload(
            self.spec, expected_component_identities=self.spec["component_identities"],
            product=self.product, previous_product=self.previous_product,
        )
        self.evaluation_authority = self.boundary.issue_authority(
            self.evaluation_request, kind="evaluation",
        )

    def unit(self, unit_id: str) -> dict[str, Any]:
        return next(unit for unit in self.spec["units"] if unit["unit_id"] == unit_id)

    def go_report(self) -> dict[str, Any]:
        provider_input = self.inputs["exact-final"]
        return {
            "neutral": True,
            "reviewed": {
                "candidate_product_artifact_sha256": provider_input["candidate_product_artifact_sha256"],
                "review_policy_sha256": provider_input["review_policy_sha256"],
                "review_projection_sha256": provider_input["review_projection_sha256"],
            },
            "coverage": {"complete": True, "unverified": []},
            "decision": "GO", "findings": [],
        }

    def not_yet_report(self, *, classification: str = "obligation_failure") -> dict[str, Any]:
        report = self.go_report()
        report["decision"] = "NOT_YET"
        report["findings"] = [{
            "classification": classification, "reproduction": "python -m unittest",
            "evidence": ["tests/test.py:1"], "materiality": "release blocker",
            "candidate_new": classification == "candidate_new_material_regression",
            "summary": "reproduced material failure",
        }]
        return report

    def make_attestation(
        self, unit_id: str, *, outcome: str = "landed", attempt: int = 0,
        prior: list[dict[str, Any]] | None = None, report: dict[str, Any] | None = None,
        wall: int = 10, cumulative: int | None = None,
        input_tokens: int = 5, output_tokens: int = 5,
        started_at: str | None = None, finished_at: str | None = None,
        product_sha256: str | None = None, execution_root: str = "/external/root-a",
        boundary: FakeExternalBoundary | None = None,
    ) -> dict[str, Any]:
        prior = prior or []
        unit = self.unit(unit_id)
        reached = outcome != "not_landed"
        complete = outcome == "landed"
        if report is None:
            report = self.go_report() if unit["stage"] == "exact_final" else {"ok": True}
        if started_at is None:
            started_at = "2026-08-08T00:00:06Z" if unit_id == "exact-final" else "2026-08-08T00:00:01Z"
        if finished_at is None:
            finished_at = "2026-08-08T00:00:07Z" if unit_id == "exact-final" else "2026-08-08T00:00:05Z"
        if cumulative is None:
            cumulative = sum(item["observation"]["attempt_wall_milliseconds"] for item in prior) + wall
        if product_sha256 is None:
            label = next((mapping[unit_id] for mapping in self.mappings.values() if unit_id in mapping), "candidate")
            product_sha256 = (
                self.product["artifact_sha256"] if label == "candidate"
                else self.previous_product["artifact_sha256"]
            )
        observation = {
            "provider_reached": reached, "response_complete": complete,
            "started_at": started_at, "finished_at": finished_at,
            "model_calls": int(reached), "input_tokens": input_tokens if reached else 0,
            "output_tokens": output_tokens if reached else 0,
            "attempt_wall_milliseconds": wall,
            "effect_cumulative_wall_milliseconds": cumulative,
            "recovery_history_sha256": canonical_sha256([item["record_sha256"] for item in prior]),
            "raw_sha256": sha(f"raw:{unit_id}:{attempt}:{cumulative}:{outcome}"),
        }
        statement = {
            "kind": "provider_terminal", "schema_version": 3,
            "spec_sha256": self.spec["spec_sha256"],
            "spec_subject_sha256": self.spec["spec_subject_sha256"],
            "product_artifact_sha256": product_sha256, "unit_id": unit_id,
            "stage": unit["stage"], "provider_input_sha256": unit["provider_input_sha256"],
            "invocation_sha256": unit["invocation_sha256"],
            "effect_subject_sha256": unit["effect_subject_sha256"], "attempt": attempt,
            "attempt_identity_sha256": canonical_sha256({
                "effect_subject_sha256": unit["effect_subject_sha256"], "attempt": attempt,
            }),
            "evaluation_authority_request_sha256": self.evaluation_request["request_sha256"],
            "authority_identity": self.evaluation_authority["authority_identity"],
            "authority_sha256": self.evaluation_authority["authority_sha256"],
            "report": report, "observation": observation, "effect_outcome": outcome,
        }
        signer = boundary or self.boundary
        binding = signer.sign_terminal(statement, execution_root=execution_root)
        return construct_attestation(
            statement, binding, response_schema=self.schemas[unit_id],
            oracle=self.oracles[unit_id], provider_input=self.inputs[unit_id],
        )

    def authenticate(self, record: dict[str, Any], *, boundary: FakeExternalBoundary | None = None):
        return authenticate_attestation(
            record, spec=self.spec, provider_input=self.inputs[record["unit_id"]],
            response_schema=self.schemas[record["unit_id"]],
            oracle=self.oracles[record["unit_id"]], authenticator=boundary or self.boundary,
            evaluation_authority_request=self.evaluation_request,
            evaluation_authority=self.evaluation_authority,
            authority_validator=boundary or self.boundary,
        )

    def terminal(self, unit_id: str, records: list[dict[str, Any]] | None = None):
        records = records or [self.make_attestation(unit_id)]
        return verify_effect_sequence(
            [self.authenticate(record) for record in records], spec=self.spec, unit_id=unit_id,
        )

    def full_evaluation(self):
        terminals = [self.terminal(unit.unit_id) for unit in UNIT_TOPOLOGY]
        holdouts = [terminal for terminal in terminals if terminal.record["stage"] == "holdout"]
        result = judge_fixed_holdouts(spec=self.spec, terminals=holdouts, mappings=self.mappings)
        return terminals, result, verify_evaluation(
            spec=self.spec, terminals=terminals, holdout_result=result,
        )

    def release(self, evaluation, *, outcome: str = "landed", mutate_statement=None):
        evaluated = evaluation.result
        projection = self.product["projections"]["plugin_runtime"]
        destination, target, rollback = "local-plugin-cache", "happycodex@0.14.0", "rollback-v013"
        effect = release_effect_subject(
            product_artifact_sha256=self.product["artifact_sha256"], destination=destination,
            target_identity=target, rollback_identity=rollback,
            installed_projection_sha256=projection["projection_sha256"],
        )
        request = release_authority_request_payload(
            product_artifact_sha256=self.product["artifact_sha256"],
            eval_spec_sha256=self.spec["spec_sha256"],
            prerequisite_attestation_sha256s=evaluated["prerequisite_attestation_sha256s"],
            exact_final_attestation_sha256=evaluated["exact_final_attestation_sha256"],
            holdout_result_sha256=evaluated["holdout_result_sha256"],
            release_effect_subject_sha256=effect,
        )
        authority = self.boundary.issue_authority(request, kind="release")
        landed = outcome == "landed"
        observation = {
            "effect_reached": outcome != "not_landed", "readback_complete": landed,
            "started_at": "2026-08-08T00:00:08Z", "finished_at": "2026-08-08T00:00:09Z",
            "attempt_wall_milliseconds": 10, "effect_cumulative_wall_milliseconds": 10,
            "recovery_history_sha256": canonical_sha256([]), "raw_sha256": sha("release-raw"),
            "observed_destination": destination if landed else None,
            "observed_product_artifact_sha256": self.product["artifact_sha256"] if landed else None,
            "observed_target_identity": target if landed else None,
            "observed_rollback_identity": rollback if landed else None,
            "observed_installed_projection_sha256": projection["projection_sha256"] if landed else None,
        }
        statement = {
            "kind": "release_terminal", "schema_version": 3,
            "product_artifact_sha256": self.product["artifact_sha256"],
            "eval_spec_sha256": self.spec["spec_sha256"],
            "spec_subject_sha256": self.spec["spec_subject_sha256"],
            "prerequisite_attestation_sha256s": evaluated["prerequisite_attestation_sha256s"],
            "exact_final_attestation_sha256": evaluated["exact_final_attestation_sha256"],
            "holdout_result_sha256": evaluated["holdout_result_sha256"],
            "release_authority_request_sha256": request["request_sha256"],
            "release_authority_identity": authority["authority_identity"],
            "release_authority_sha256": authority["authority_sha256"],
            "release_effect_subject_sha256": effect, "attempt": 0,
            "attempt_identity_sha256": canonical_sha256({"effect_subject_sha256": effect, "attempt": 0}),
            "destination": destination, "target_identity": target,
            "rollback_identity": rollback, "installed_projection": projection,
            "observation": observation, "outcome": outcome,
        }
        if mutate_statement:
            mutate_statement(statement)
        binding = self.boundary.sign_terminal(statement, execution_root="/external/release-root")
        receipt = construct_release_receipt(statement, binding)
        verified = verify_release(
            receipt, evaluation=evaluation, product=self.product, spec=self.spec,
            authenticator=self.boundary, release_authority=authority,
            authority_validator=self.boundary,
        )
        return receipt, verified


class CommittedWorkspace:
    """A temporary clean commit containing the current candidate bytes."""

    def __enter__(self):
        self._temporary = tempfile.TemporaryDirectory(prefix="happycodex-v3-tests-")
        self.root = Path(self._temporary.name)
        paths = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT,
        ).split(b"\0")
        for encoded in paths:
            if not encoded:
                continue
            relative = encoded.decode()
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        self._git("init", "-q")
        self._git("config", "user.name", "Offline Tests")
        self._git("config", "user.email", "offline-tests@example.invalid")
        self._git("add", "-A")
        self._git("commit", "-qm", "baseline")
        self.baseline = self._git("rev-parse", "HEAD")
        return self

    def __exit__(self, *_):
        self._temporary.cleanup()

    def _git(self, *arguments: str) -> str:
        return subprocess.check_output(["git", "-C", str(self.root), *arguments], text=True).strip()

    def commit(self, message: str = "candidate") -> str:
        self._git("add", "-A")
        self._git("commit", "-qm", message)
        return self._git("rev-parse", "HEAD")

    def production_construction(self) -> tuple[dict[str, Any], dict[str, Any]]:
        commit = self._git("rev-parse", "HEAD")
        product = product_artifact_from_tree(
            self.root, source_identity=commit, baseline_identity=self.baseline, source_kind="git_tree",
        )
        projection = review_projection_from_git(
            self.root, baseline=self.baseline, candidate=commit,
        )
        mappings = {
            f"holdout-{sample}": {
                f"holdout-{sample}-a": "candidate", f"holdout-{sample}-b": "baseline",
            } for sample in ("recovery", "safety", "scope")
        }
        construction = {
            "root": self.root, "previous_root": self.root,
            "product": product, "previous_product": product,
            "review_projection": projection, "holdout_mappings": mappings,
            "caps": {
                "model_calls": 12, "candidate_token_ratio_milli": 1250,
                "unit_wall_milliseconds": 1000, "absolute_wall_milliseconds": 12000,
                "recovery_attempts": 1,
            },
        }
        return construction, build_production_spec(**construction)


def write_json(path: Path, value: Any) -> Path:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return path


__all__ = (
    "CommittedWorkspace", "ROOT", "RecordFactory", "fake_product", "reseal", "sha",
    "write_json",
)
