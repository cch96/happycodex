from __future__ import annotations

import io
from itertools import permutations
import json
import math
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
from typing import Any

from evaluation.core.identity import (
    canonical_json_bytes,
    canonical_sha256,
    case_semantic_sha256,
    engine_category_sha256,
    engine_inventory,
    normalize_package_modes,
    package_identities,
    sha256_bytes,
)
from evaluation.core.impact import (
    historical_cost_receipt,
    impact_token,
    plan_impact,
    validate_impact,
    validate_snapshot,
)
from evaluation.corpus.contract import (
    BLOCKER_CLASSES,
    FILESYSTEM_ISOLATION_POLICY,
    PERMISSION_FIELDS,
    PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
    RECOVERY_GATE_FIELDS,
)
from evaluation.holdout.blind import completed_quality
from evaluation.holdout.compare import (
    adaptive_next,
    aggregate_quality,
    cost_gate,
    sum_metrics,
)


LEDGER_FIELDS = {
    "schema_version",
    "state",
    "snapshot",
    "prior_evidence",
    "pending",
    "historical_cost",
    "live_authority",
    "certification",
}
PENDING_FIELDS = {"reasons", "corpus_cases", "holdout_pairs", "review"}
AUTHORITY_FIELDS = {
    "schema_version",
    "source",
    "approval_request_sha256",
    "approval_response",
    "approval_response_sha256",
    "snapshot_sha256",
    "impact",
    "impact_token",
    "invocations",
}
CORPUS_INVOCATION_FIELDS = {
    "command",
    "package_semantic_sha256",
    "package_artifact_sha256",
    "model",
    "effort",
    "timeout_seconds",
    "arm",
    "cases",
}
HOLDOUT_INVOCATION_FIELDS = {
    "command",
    "candidate_semantic_sha256",
    "candidate_artifact_sha256",
    "public_semantic_sha256",
    "public_artifact_sha256",
    "model",
    "effort",
    "timeout_seconds",
    "pairs",
}
CERTIFICATION_FIELDS = {
    "schema_version",
    "successor_source_commit",
    "successor_source_tree",
    "snapshot_sha256",
    "engine_manifest_sha256",
    "coverage",
    "evidence",
    "live_authority_sha256",
}
COVERAGE_FIELDS = {"corpus", "holdout"}
EVIDENCE_LOCATOR_FIELDS = {"commit", "path", "git_blob", "sha256"}
CORPUS_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "impact_token",
    "live_authority_sha256",
    "arm",
    "model",
    "effort",
    "timeout_seconds",
    "passed",
    "total",
    "uncached_input_tokens",
    "telemetry_complete",
    "output_tokens",
    "elapsed_seconds",
    "cases",
}
CASE_RECEIPT_FIELDS = {
    "schema_version",
    "engine_generation",
    "id",
    "metadata_sha256",
    "installation",
    "model",
    "effort",
    "timeout_seconds",
    "timed_out",
    "elapsed_seconds",
    "exit_code",
    "semantic_input_sha256",
    "identities",
    "events_sha256",
    "stderr_sha256",
    "usage",
    "usage_phases",
    "uncached_input_tokens",
    "passed",
    "result",
    "fresh_recovery_result",
    "oracle_failures",
    "native_compaction",
    "thread_id_sha256",
    "resume_thread_id_sha256",
    "fresh_recovery_thread_id_sha256",
    "filesystem_isolation",
}
HOLDOUT_RUN_FIELDS = {
    "schema_version",
    "engine_generation",
    "impact_token",
    "live_authority_sha256",
    "manifest_sha256",
    "identities",
    "model",
    "effort",
    "timeout_seconds",
    "pair_ids",
    "case_sha256",
}
PAIR_RECEIPT_FIELDS = {
    "schema_version",
    "engine_generation",
    "id",
    "case_id",
    "case_sha256",
    "outside_diff_boundary",
    "oracle_kind",
    "mapping_commitment_file_sha256",
    "pre_reveal_decision_file_sha256",
    "mapping_reveal_file_sha256",
    "pre_reveal_decision_sha256",
    "mapping_commitment_sha256",
    "outcome",
    "metrics",
    "arms",
}
HOLDOUT_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "run_receipt_sha256",
    "adaptive_history",
    "adaptive_terminal_action",
    "pairs_run",
    "pair_receipts",
    "cost_gate",
}
OFFLINE_GATES = frozenset({"receipt", "isolated_install"})
OFFLINE_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "source_commit",
    "source_ledger_sha256",
    "snapshot_sha256",
    "engine_manifest_sha256",
    "gates",
    "receipt_artifact_sha256",
    "isolated_installation",
}

INSTALLATION_RECEIPT_FIELDS = {
    "source_skill_sha256",
    "installed_skill_sha256",
    "source_package_manifest_sha256",
    "installed_package_manifest_sha256",
    "plugin_sha256",
}
FILESYSTEM_RECEIPT_FIELDS = {
    "mechanism",
    "profile",
    "default_access",
    "workspace",
    "nonworkspace",
    "native_tools",
    "network",
    "selection",
    "policy_sha256",
}
RESULT_RECEIPT_FIELDS = {
    "result_sha256",
    *PERMISSION_FIELDS,
    "finding_classifications",
    "blocker_classifications",
    "open_gates_count",
    "open_gates_sha256",
    "goal_pause_handoff_present",
    "evidence_count",
    "evidence_sha256",
    "reason_sha256",
    "recovery_state",
}
FINDING_RECEIPT_FIELDS = {
    "identity_sha256",
    "identity_casefold_sha256",
    "identity_match_sha256s",
    "domain",
    "state",
    "anchors_count",
    "anchors_sha256",
    "anchor_sha256s",
}
BLOCKER_RECEIPT_FIELDS = {
    "identity_sha256",
    "identity_casefold_sha256",
    "identity_match_sha256s",
    "class",
    "blocking",
    "reason_sha256",
}
RECOVERY_RECEIPT_FIELDS = {
    "recovery_state_sha256",
    "baseline_revision",
    "baseline_tree",
    "current_revision",
    "current_tree",
    "writer",
    "milestone_phase",
    "next_action",
    "pending_gates",
    "tests",
    "worktree",
    "live_agents",
    "marker_ids_count",
    "marker_ids_sha256",
}
RECOVERY_TEST_FIELDS = {
    "passed",
    "failed",
    "accepted_failures",
    "marker_ids_count",
    "marker_ids_sha256",
}
RECOVERY_AGENT_FIELDS = {"id_sha256", "status", "receipt_reproduced"}
COMPACTION_PHASE_FIELDS = {
    "phase_sha256",
    "rollout_path_sha256",
    "rollout_sha256",
    "rollout_byte_count",
    "rollout_prefix_sha256",
    "compaction_event_count",
    "context_compacted_marker_count",
    "event_types",
    "rollout_match_count",
}
NATIVE_COMPACTION_FIELDS = {
    "native_compaction_sha256",
    "auto_compact_token_limit",
    "compaction_event_count",
    "resumed_same_thread",
    "before_resume",
    "after_resume",
    "post_compaction_transition_sha256",
    "fresh_control",
}
FRESH_CONTROL_FIELDS = {
    "fresh_control_sha256",
    "thread_id_sha256",
    "distinct_from_resumed_task",
    "no_resume_handle",
    "no_conversation_summary",
    "prompt_sha256",
    "equivalent_gate_fields",
    "allowed_label_differences_sha256",
}
RECOVERY_WRITERS = {"Root", "unknown"}
RECOVERY_PHASES = {
    "bootstrap",
    "boundary_investigation",
    "boundary_union_reproduced",
    "contract_frozen",
    "implementation",
    "review",
    "release",
    "complete",
    "unknown",
}
RECOVERY_ACTIONS = {
    "ask_user",
    "create_execplan",
    "complete_boundary_union",
    "create_contract_freeze_revision",
    "observe_red",
    "implement",
    "run_checks",
    "review",
    "release",
    "none",
    "unknown",
}
RECOVERY_PENDING_GATES = {
    "user_selection",
    "contract_freeze",
    "red_oracle",
    "product_edit",
    "checks",
    "review",
    "release",
}
RECOVERY_WORKTREE_STATES = {"clean", "dirty", "unknown"}
RECOVERY_AGENT_STATES = {"pending", "terminal", "missing"}
COMPACTION_EVENT_TYPES = {"compacted", "context_compacted"}


def _require_digest(value: Any, *, length: int, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise ValueError(f"invalid {label}")


def _validate_ordered_names(value: Any, *, label: str) -> None:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
        or value != sorted(set(value))
    ):
        raise ValueError(f"invalid authorized {label}")


def _validate_invocation(invocation: Any) -> None:
    if not isinstance(invocation, dict):
        raise ValueError("invalid authorized invocation")
    command = invocation.get("command")
    fields = {
        "corpus": CORPUS_INVOCATION_FIELDS,
        "holdout": HOLDOUT_INVOCATION_FIELDS,
    }.get(command)
    if fields is None or set(invocation) != fields:
        raise ValueError("invalid authorized invocation envelope")
    for field in ("model", "effort"):
        if not isinstance(invocation[field], str) or not invocation[field]:
            raise ValueError(f"invalid authorized invocation field: {field}")
    timeout = invocation["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("invalid authorized invocation field: timeout_seconds")
    if command == "corpus":
        digest_fields = ("package_semantic_sha256", "package_artifact_sha256")
        if invocation["arm"] != "candidate":
            raise ValueError("authorized corpus invocation must use candidate arm")
        _validate_ordered_names(invocation["cases"], label="corpus cases")
    else:
        digest_fields = (
            "candidate_semantic_sha256",
            "candidate_artifact_sha256",
            "public_semantic_sha256",
            "public_artifact_sha256",
        )
        _validate_ordered_names(invocation["pairs"], label="holdout pairs")
        if invocation["public_artifact_sha256"] != PUBLIC_02_PACKAGE_ARTIFACT_SHA256:
            raise ValueError("authorized holdout does not use frozen public-0.2")
    for field in digest_fields:
        _require_digest(invocation[field], length=64, label=field)


def _expected_authority_commands(impact: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    if impact["corpus_cases"]:
        commands.append("corpus")
    if impact["holdout_pairs"]:
        commands.append("holdout")
    return commands


def affirmative_approval_response(approval_request_sha256: str) -> str:
    _require_digest(
        approval_request_sha256,
        length=64,
        label="approval request digest",
    )
    return f"APPROVE HAPPYCODEX LIVE COST {approval_request_sha256}\n"


def validate_live_authority(authority: Any, *, snapshot: dict[str, Any]) -> None:
    if not isinstance(authority, dict) or set(authority) != AUTHORITY_FIELDS:
        raise ValueError("live authority is not persisted")
    if authority.get("schema_version") != 1:
        raise ValueError("invalid live authority schema")
    validate_snapshot(snapshot)
    if not isinstance(authority.get("source"), str) or not re.fullmatch(
        r"current-task/user/[a-z0-9][a-z0-9._/-]*", authority["source"]
    ):
        raise ValueError("invalid live authority source")
    response = authority.get("approval_response")
    if not isinstance(response, str) or not response or len(response) > 10_000:
        raise ValueError("invalid approval response")
    if authority.get("approval_response_sha256") != sha256_bytes(response.encode()):
        raise ValueError("approval response digest mismatch")
    snapshot_sha256 = canonical_sha256(snapshot)
    if authority.get("snapshot_sha256") != snapshot_sha256:
        raise ValueError("live authority snapshot mismatch")
    impact = authority.get("impact")
    if not isinstance(impact, dict):
        raise ValueError("invalid authorized impact")
    validate_impact(impact, snapshot)
    token = impact_token(snapshot, impact)
    if authority.get("impact_token") != token:
        raise ValueError("live authority impact token mismatch")
    invocations = authority.get("invocations")
    if not isinstance(invocations, list):
        raise ValueError("live authority requires exact invocations")
    expected_commands = _expected_authority_commands(impact)
    if [
        item.get("command") for item in invocations if isinstance(item, dict)
    ] != expected_commands:
        raise ValueError("live authority does not cover complete impact scope")
    if not expected_commands:
        raise ValueError("live authority cannot authorize a zero-call impact")
    settings = snapshot["settings"]
    package = snapshot["package"]
    for invocation in invocations:
        _validate_invocation(invocation)
        if (
            invocation["model"] != settings["model"]
            or invocation["effort"] != settings["effort"]
            or invocation["timeout_seconds"] != settings["timeout_seconds"]
        ):
            raise ValueError("authorized invocation settings mismatch")
        if invocation["command"] == "corpus":
            candidate = {
                "semantic_sha256": invocation["package_semantic_sha256"],
                "artifact_sha256": invocation["package_artifact_sha256"],
            }
            if invocation["cases"] != impact["corpus_cases"]:
                raise ValueError("live authority does not cover complete impact scope")
        else:
            candidate = {
                "semantic_sha256": invocation["candidate_semantic_sha256"],
                "artifact_sha256": invocation["candidate_artifact_sha256"],
            }
            if invocation["pairs"] != impact["holdout_pairs"]:
                raise ValueError("live authority does not cover complete impact scope")
        if candidate != package:
            raise ValueError("authorized invocation package mismatch")
    request = {
        "schema_version": 1,
        "snapshot_sha256": snapshot_sha256,
        "impact": impact,
        "impact_token": token,
        "invocations": invocations,
    }
    request_sha256 = canonical_sha256(request)
    if authority.get("approval_request_sha256") != request_sha256:
        raise ValueError("approval request digest mismatch")
    if response != affirmative_approval_response(request_sha256):
        raise ValueError("approval response is not the canonical affirmative grant")


def _authorization_boundary() -> tuple[type[Any], Any]:
    class AuthorizedInvocation:
        """Immutable process-local proof of exact persisted authority validation."""

        __slots__ = ("__payload_json",)

        def __new__(cls, *_args: Any, **_kwargs: Any) -> Any:
            raise TypeError("authorized invocation capabilities are validator-minted")

        def __setattr__(self, _name: str, _value: Any) -> None:
            raise AttributeError("authorized invocation capabilities are immutable")

        @property
        def authority_sha256(self) -> str:
            return self._payload()["authority_sha256"]

        @property
        def command(self) -> str:
            return self.descriptor()["command"]

        @property
        def impact_token(self) -> str:
            return self._payload()["impact_token"]

        def descriptor(self) -> dict[str, Any]:
            return self._payload()["descriptor"]

        def snapshot(self) -> dict[str, Any]:
            return self._payload()["snapshot"]

        def _payload(self) -> dict[str, Any]:
            return json.loads(self.__payload_json)

        def __copy__(self) -> Any:
            raise TypeError("authorized invocation capabilities cannot be copied")

        def __deepcopy__(self, _memo: dict[int, Any]) -> Any:
            raise TypeError("authorized invocation capabilities cannot be copied")

        def __reduce__(self) -> Any:
            raise TypeError("authorized invocation capabilities cannot be serialized")

    def mint(
        *,
        descriptor: dict[str, Any],
        snapshot: dict[str, Any],
        impact_token_value: str,
        authority_sha256: str,
    ) -> AuthorizedInvocation:
        capability = object.__new__(AuthorizedInvocation)
        object.__setattr__(
            capability,
            "_AuthorizedInvocation__payload_json",
            canonical_json_bytes(
                {
                    "authority_sha256": authority_sha256,
                    "descriptor": descriptor,
                    "impact_token": impact_token_value,
                    "snapshot": snapshot,
                }
            ),
        )
        return capability

    def require_authorized_invocation(
        authority: Any,
        *,
        snapshot: dict[str, Any],
        impact: dict[str, Any],
        invocation: dict[str, Any],
    ) -> AuthorizedInvocation:
        validate_live_authority(authority, snapshot=snapshot)
        validate_impact(impact, snapshot)
        if authority["impact"] != impact:
            raise ValueError("live authority does not match current impact")
        _validate_invocation(invocation)
        requested = canonical_sha256(invocation)
        authorized = {canonical_sha256(item) for item in authority["invocations"]}
        if requested not in authorized:
            raise ValueError("invocation is not authorized")
        return mint(
            descriptor=invocation,
            snapshot=snapshot,
            impact_token_value=authority["impact_token"],
            authority_sha256=canonical_sha256(authority),
        )

    return AuthorizedInvocation, require_authorized_invocation


AuthorizedInvocation, require_authorized_invocation = _authorization_boundary()
del _authorization_boundary


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        stdin=subprocess.DEVNULL,
    )


def _require_reachable_commit(repo: Path, commit: str, *, label: str) -> None:
    _require_digest(commit, length=40, label=label)
    exists = _run_git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
    reachable = _run_git(repo, "merge-base", "--is-ancestor", commit, "HEAD")
    if exists.returncode or reachable.returncode:
        raise ValueError(f"reachable certification evidence missing: {label}")


def _build_native_evidence_oracle(
    case: dict[str, Any], *, scratch: Path
) -> dict[str, Any] | None:
    native = case["fixture"].get("native_compaction_resume")
    if native is None:
        return None
    from evaluation.corpus.engine import (
        apply_post_compaction_transition,
        build_fixture,
        expected_recovery_state,
    )

    fixture_repo = scratch / case["id"]
    fixture = build_fixture(case, fixture_repo)
    transition = apply_post_compaction_transition(
        fixture_repo, native["post_compaction_transition"], fixture
    )
    return {
        "recovery_state": expected_recovery_state(native, fixture, transition),
        "post_compaction_transition_sha256": canonical_sha256(transition),
    }


def _validate_source_identity(
    repo: Path,
    commit: str,
    snapshot: dict[str, Any],
    live_authority: dict[str, Any] | None,
) -> dict[str, Any]:
    archive = _run_git(repo, "archive", "--format=tar", commit)
    if archive.returncode:
        raise ValueError("cannot read certification successor source")
    with tempfile.TemporaryDirectory(prefix="happycodex-certified-source-") as raw:
        root = Path(raw)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as source:
            for member in source.getmembers():
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts:
                    raise ValueError("unsafe certification successor archive")
                if member.issym() or member.islnk():
                    target = PurePosixPath(member.linkname)
                    if target.is_absolute() or ".." in target.parts:
                        raise ValueError("unsafe certification successor archive link")
            source.extractall(root)
        try:
            normalize_package_modes(root)
            source_package = package_identities(root)
            inventory = engine_inventory(root)
        except (OSError, ValueError) as exc:
            raise ValueError("invalid certification successor source") from exc
        if source_package != snapshot["package"]:
            raise ValueError("certification source package mismatch")
        if inventory["manifest_sha256"] != snapshot["engine"]["manifest_sha256"]:
            raise ValueError("certification successor engine mismatch")
        source_ledger_path = root / "evaluation" / "results" / "current.json"
        try:
            source_ledger_bytes = source_ledger_path.read_bytes()
            source_ledger = json.loads(source_ledger_bytes)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid certification source authority ledger") from exc
        if (
            not isinstance(source_ledger, dict)
            or source_ledger.get("state") != "refresh_required"
            or source_ledger.get("snapshot") != snapshot
            or source_ledger.get("live_authority") != live_authority
            or source_ledger.get("certification") is not None
        ):
            raise ValueError("certification source authority was not persisted")
        try:
            validate_ledger(source_ledger, repo=root)
        except (OSError, ValueError) as exc:
            raise ValueError("invalid certification source authority ledger") from exc
        try:
            from evaluation.corpus.engine import load_cases

            corpus_cases = load_cases(root / "evaluation" / "cases")
        except (OSError, ValueError) as exc:
            raise ValueError("invalid certification successor corpus") from exc
        if set(corpus_cases) != set(snapshot["corpus"]["cases"]):
            raise ValueError("certification successor corpus scope mismatch")
        manifest_path = root / "evaluation" / "holdouts" / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_bytes())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "invalid certification successor holdout manifest"
            ) from exc
        rows = manifest.get("pairs") if isinstance(manifest, dict) else None
        if (
            not isinstance(manifest, dict)
            or manifest.get("schema_version") != 1
            or not isinstance(rows, list)
        ):
            raise ValueError("invalid certification successor holdout manifest")
        descriptors: dict[str, dict[str, Any]] = {}
        pair_order: list[str] = []
        holdout_root = (root / "evaluation" / "holdouts").resolve()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                raise ValueError("invalid certification successor holdout descriptor")
            pair_id = row["id"]
            relative = row.get("case_path")
            if not isinstance(relative, str):
                raise ValueError("invalid certification successor holdout case")
            case_path = (root / relative).resolve()
            if (
                pair_id in descriptors
                or not case_path.is_relative_to(holdout_root)
                or not case_path.is_file()
            ):
                raise ValueError("invalid certification successor holdout case")
            try:
                case = json.loads(case_path.read_bytes())
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(
                    "invalid certification successor holdout case"
                ) from exc
            if not isinstance(case, dict) or not isinstance(case.get("id"), str):
                raise ValueError("invalid certification successor holdout case")
            pair_order.append(pair_id)
            descriptors[pair_id] = {
                "case": case,
                "case_sha256": sha256_bytes(case_path.read_bytes()),
                "outside_diff_boundary": row.get("outside_diff_boundary"),
                "oracle_kind": row.get("oracle_kind"),
            }
        if set(pair_order) != set(snapshot["holdout"]["pairs"]):
            raise ValueError("certification successor holdout scope mismatch")
        native_evidence_oracles: dict[str, dict[str, Any]] = {}
        all_cases = [*corpus_cases.values()]
        all_cases.extend(descriptor["case"] for descriptor in descriptors.values())
        scratch = root / ".native-evidence"
        for case in all_cases:
            try:
                expected = _build_native_evidence_oracle(case, scratch=scratch)
            except (OSError, RuntimeError, ValueError) as exc:
                raise ValueError(
                    "invalid certification native evidence oracle"
                ) from exc
            if expected is None:
                continue
            case_id = case["id"]
            prior = native_evidence_oracles.get(case_id)
            if prior is not None and prior != expected:
                raise ValueError("conflicting certification native evidence oracle")
            native_evidence_oracles[case_id] = expected
        return {
            "ledger": source_ledger,
            "ledger_sha256": sha256_bytes(source_ledger_bytes),
            "engine": inventory,
            "corpus_semantic_sha256": engine_category_sha256(
                inventory,
                "semantic",
                paths={"evaluation/corpus/contract.py"},
            ),
            "corpus_cases": corpus_cases,
            "native_evidence_oracles": native_evidence_oracles,
            "holdout_manifest_sha256": sha256_bytes(manifest_path.read_bytes()),
            "holdout_pair_order": pair_order,
            "holdout_descriptors": descriptors,
        }


def _load_evidence(
    repo: Path,
    locator: Any,
    *,
    label: str,
    source_commit: str,
) -> tuple[dict[str, Any], str]:
    if not isinstance(locator, dict) or set(locator) != EVIDENCE_LOCATOR_FIELDS:
        raise ValueError(f"invalid certification evidence locator: {label}")
    commit = locator["commit"]
    _require_reachable_commit(repo, commit, label=f"{label} commit")
    if commit == source_commit:
        raise ValueError(
            f"certification evidence must strictly postdate source: {label}"
        )
    after_source = _run_git(repo, "merge-base", "--is-ancestor", source_commit, commit)
    if after_source.returncode:
        raise ValueError(f"certification evidence predates source: {label}")
    path = locator["path"]
    if not isinstance(path, str):
        raise ValueError(f"invalid certification evidence path: {label}")
    relative = PurePosixPath(path)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.parts[:3] != ("evaluation", "results", "evidence")
        or relative.suffix != ".json"
    ):
        raise ValueError(f"unsafe certification evidence path: {label}")
    blob = _run_git(repo, "rev-parse", f"{commit}:{path}")
    content = _run_git(repo, "show", f"{commit}:{path}")
    if blob.returncode or content.returncode:
        raise ValueError(f"reachable certification evidence missing: {label}")
    actual_blob = blob.stdout.decode().strip()
    _require_digest(locator.get("git_blob"), length=40, label=f"{label} blob")
    if locator["git_blob"] != actual_blob:
        raise ValueError(f"certification evidence blob mismatch: {label}")
    actual_sha256 = sha256_bytes(content.stdout)
    _require_digest(locator.get("sha256"), length=64, label=f"{label} sha256")
    if locator["sha256"] != actual_sha256:
        raise ValueError(f"certification evidence digest mismatch: {label}")
    try:
        payload = json.loads(content.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"certification evidence is not JSON: {label}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"certification evidence must be an object: {label}")
    return payload, actual_sha256


def _load_prior_certified_ledger(
    repo: Path,
    prior: dict[str, Any],
    *,
    source_commit: str,
) -> dict[str, Any]:
    commit = prior.get("source_commit")
    _require_reachable_commit(repo, commit, label="prior certified ledger commit")
    if commit == source_commit:
        raise ValueError("prior certified ledger must predate successor source")
    ancestor = _run_git(repo, "merge-base", "--is-ancestor", commit, source_commit)
    if ancestor.returncode:
        raise ValueError("prior certified ledger must predate successor source")
    path = prior.get("source_path")
    if path != "evaluation/results/current.json":
        raise ValueError("incremental certification requires a prior 0.4 ledger")
    content = _run_git(repo, "show", f"{commit}:{path}")
    if content.returncode:
        raise ValueError("prior certified ledger is unreachable")
    if prior.get("sha256") != sha256_bytes(content.stdout):
        raise ValueError("prior certified ledger digest mismatch")
    try:
        ledger = json.loads(content.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("prior certified ledger is not JSON") from exc
    if not isinstance(ledger, dict) or ledger.get("state") != "certified":
        raise ValueError("incremental certification requires prior certified state")
    validate_ledger(ledger, repo=repo)
    return ledger


def _validate_coverage(
    coverage: Any,
    *,
    snapshot: dict[str, Any],
    impact: dict[str, Any],
) -> tuple[set[str], bool]:
    if not isinstance(coverage, dict) or set(coverage) != COVERAGE_FIELDS:
        raise ValueError("invalid certification coverage manifest")
    refreshed: dict[str, set[str]] = {}
    for label, available in (
        ("corpus", set(snapshot["corpus"]["cases"])),
        ("holdout", set(snapshot["holdout"]["pairs"])),
    ):
        values = coverage.get(label)
        if (
            not isinstance(values, dict)
            or set(values) != available
            or any(value not in {"refreshed", "prior"} for value in values.values())
        ):
            raise ValueError(f"invalid certification {label} coverage")
        refreshed[label] = {
            name for name, disposition in values.items() if disposition == "refreshed"
        }
    if refreshed["corpus"] != set(impact["corpus_cases"]):
        raise ValueError("certification corpus coverage does not match impact")
    if refreshed["holdout"] != set(impact["holdout_pairs"]):
        raise ValueError("certification holdout coverage does not match impact")
    evidence_fields: set[str] = set()
    if refreshed["corpus"]:
        evidence_fields.add("corpus_summary")
    if refreshed["holdout"]:
        evidence_fields.update({"holdout_run", "holdout_summary"})
    carries_prior = any(
        disposition == "prior"
        for label in ("corpus", "holdout")
        for disposition in coverage[label].values()
    )
    return evidence_fields, carries_prior


def _offline_gates(impact: dict[str, Any]) -> set[str]:
    return set(impact["gates"]) & OFFLINE_GATES


def _validate_offline_summary(
    payload: Any,
    *,
    snapshot: dict[str, Any],
    source_commit: str,
    source_ledger_sha256: str,
    gates: set[str],
) -> None:
    if not isinstance(payload, dict) or set(payload) != OFFLINE_SUMMARY_FIELDS:
        raise ValueError("invalid offline certification evidence")
    expected_gates = sorted(gates)
    if (
        not gates
        or not gates.issubset(OFFLINE_GATES)
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.4"
        or payload.get("source_commit") != source_commit
        or payload.get("source_ledger_sha256") != source_ledger_sha256
        or payload.get("snapshot_sha256") != canonical_sha256(snapshot)
        or payload.get("engine_manifest_sha256")
        != snapshot["engine"]["manifest_sha256"]
        or payload.get("gates") != expected_gates
    ):
        raise ValueError("offline certification evidence identity mismatch")
    expected_receipt = (
        snapshot["engine"]["categories"]["artifact"] if "receipt" in gates else None
    )
    if payload.get("receipt_artifact_sha256") != expected_receipt:
        raise ValueError("offline receipt evidence mismatch")
    installation = payload.get("isolated_installation")
    if "isolated_install" in gates:
        _validate_installation_receipt(
            installation,
            package=snapshot["package"],
            case_id="offline certification",
        )
    elif installation is not None:
        raise ValueError("unexpected offline installation evidence")


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _casefold_text_sha256(value: Any) -> str:
    return sha256_bytes(str(value).casefold().encode())


def _validate_digest_list(value: Any, *, label: str, required: bool) -> None:
    if (
        not isinstance(value, list)
        or (required and not value)
        or value != sorted(set(value))
    ):
        raise ValueError(f"invalid {label} digest list")
    for item in value:
        _require_digest(item, length=64, label=label)


def _matches_unordered_list_digest(value: Any, expected: list[Any]) -> bool:
    if len(expected) > 8:
        raise ValueError("recovery marker set is too large to verify exactly")
    expected_digests = {
        canonical_sha256(list(order)) for order in set(permutations(expected))
    }
    return value in expected_digests


def _validate_recovery_oracle_receipt(
    value: dict[str, Any], *, oracle: dict[str, Any], label: str
) -> None:
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        if field in oracle and value[field] != oracle[field]:
            raise ValueError(f"invalid {label} recovery oracle receipt: {field}")
    for field in (
        "writer",
        "milestone_phase",
        "next_action",
        "pending_gates",
        "worktree",
    ):
        if value[field] != oracle[field]:
            raise ValueError(f"invalid {label} recovery oracle receipt: {field}")
    tests = value["tests"]
    expected_tests = oracle["tests"]
    for field in ("passed", "failed", "accepted_failures"):
        if tests[field] != expected_tests[field]:
            raise ValueError(f"invalid {label} recovery oracle tests: {field}")
    expected_test_markers = expected_tests["marker_ids"]
    if tests["marker_ids_count"] != len(
        expected_test_markers
    ) or not _matches_unordered_list_digest(
        tests["marker_ids_sha256"], expected_test_markers
    ):
        raise ValueError(f"invalid {label} recovery oracle test markers")
    expected_agents = [
        {
            "id_sha256": sha256_bytes(str(agent["id"]).encode()),
            "status": agent["status"],
            "receipt_reproduced": agent["receipt_reproduced"],
        }
        for agent in oracle["live_agents"]
    ]
    if sorted(value["live_agents"], key=canonical_sha256) != sorted(
        expected_agents, key=canonical_sha256
    ):
        raise ValueError(f"invalid {label} recovery oracle agents")
    expected_markers = oracle["marker_ids"]
    if value["marker_ids_count"] != len(
        expected_markers
    ) or not _matches_unordered_list_digest(
        value["marker_ids_sha256"], expected_markers
    ):
        raise ValueError(f"invalid {label} recovery oracle markers")


def _validate_case_oracle_receipt(
    value: dict[str, Any], *, case: dict[str, Any], label: str
) -> None:
    oracle = case["oracle"]
    findings = value["finding_classifications"]
    blockers = value["blocker_classifications"]
    from evaluation.corpus.engine import fixture_requires_goal_pause_handoff

    if (
        fixture_requires_goal_pause_handoff(case["fixture"])
        and value["decision"] == "stop_for_user"
        and value["goal_pause_handoff_present"] is not True
    ):
        raise ValueError(f"missing {label} oracle Goal-pause handoff receipt")
    for required in oracle.get("required_classifications", []):
        states = required["state"]
        allowed_states = states if isinstance(states, list) else [states]
        identity = _casefold_text_sha256(required["identity"])
        if not any(
            identity in finding["identity_match_sha256s"]
            and finding["domain"] == required["domain"]
            and finding["state"] in allowed_states
            for finding in findings
        ):
            raise ValueError(f"missing {label} oracle classification receipt")
    for required_class in oracle.get("required_blocker_classes", []):
        if not any(
            blocker["class"] == required_class and blocker["blocking"] is True
            for blocker in blockers
        ):
            raise ValueError(f"missing {label} oracle blocker-class receipt")
    for required in oracle.get("required_blocker_classifications", []):
        identity = _casefold_text_sha256(required["identity"])
        if not any(
            identity in blocker["identity_match_sha256s"]
            and blocker["class"] == required["class"]
            and blocker["blocking"] is True
            for blocker in blockers
        ):
            raise ValueError(f"missing {label} oracle blocker receipt")
    for required in oracle.get("required_anchored_blockers", []):
        anchor = _casefold_text_sha256(required["anchor"])
        classes = required["class"]
        allowed_classes = classes if isinstance(classes, list) else [classes]
        anchored = [
            finding
            for finding in findings
            if finding["identity_casefold_sha256"] == anchor
            or anchor in finding["anchor_sha256s"]
        ]
        if not any(
            blocker["identity_casefold_sha256"] == finding["identity_casefold_sha256"]
            and blocker["class"] in allowed_classes
            and blocker["blocking"] is True
            for finding in anchored
            for blocker in blockers
        ):
            raise ValueError(f"missing {label} oracle anchored blocker receipt")
    for required in oracle.get("required_anchored_classifications", []):
        anchor = _casefold_text_sha256(required["anchor"])
        states = required["state"]
        allowed_states = states if isinstance(states, list) else [states]
        if not any(
            (
                finding["identity_casefold_sha256"] == anchor
                or anchor in finding["anchor_sha256s"]
            )
            and finding["domain"] == required["domain"]
            and finding["state"] in allowed_states
            for finding in findings
        ):
            raise ValueError(f"missing {label} oracle anchored classification receipt")
    if value["decision"] == "complete" or value["protocol_may_complete"] is True:
        accepted = [
            _casefold_text_sha256(identity)
            for identity in oracle.get("accepted_baseline_failures", [])
        ]
        for finding in findings:
            if (
                finding["domain"] == "baseline_failure"
                and finding["state"] == "baseline_unchanged"
                and sum(
                    identity in finding["identity_match_sha256s"]
                    for identity in accepted
                )
                != 1
            ):
                raise ValueError(
                    f"invalid {label} accepted baseline classification receipt"
                )


def _validate_recovery_receipt(value: Any, *, label: str) -> None:
    if not isinstance(value, dict) or set(value) != RECOVERY_RECEIPT_FIELDS:
        raise ValueError(f"invalid {label} recovery receipt")
    _require_digest(
        value.get("recovery_state_sha256"), length=64, label=f"{label} recovery"
    )
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        _require_digest(value.get(field), length=40, label=f"{label} recovery {field}")
    pending_gates = value.get("pending_gates")
    if (
        value.get("writer") not in RECOVERY_WRITERS
        or value.get("milestone_phase") not in RECOVERY_PHASES
        or value.get("next_action") not in RECOVERY_ACTIONS
        or value.get("worktree") not in RECOVERY_WORKTREE_STATES
        or not isinstance(pending_gates, list)
        or any(gate not in RECOVERY_PENDING_GATES for gate in pending_gates)
    ):
        raise ValueError(f"invalid {label} recovery receipt")
    tests = value.get("tests")
    if not isinstance(tests, dict) or set(tests) != RECOVERY_TEST_FIELDS:
        raise ValueError(f"invalid {label} recovery tests receipt")
    if any(
        not _nonnegative_int(tests.get(field))
        for field in ("passed", "failed", "accepted_failures", "marker_ids_count")
    ):
        raise ValueError(f"invalid {label} recovery tests receipt")
    _require_digest(
        tests.get("marker_ids_sha256"),
        length=64,
        label=f"{label} recovery test markers",
    )
    agents = value.get("live_agents")
    if not isinstance(agents, list):
        raise ValueError(f"invalid {label} recovery agents receipt")
    for agent in agents:
        if (
            not isinstance(agent, dict)
            or set(agent) != RECOVERY_AGENT_FIELDS
            or agent.get("status") not in RECOVERY_AGENT_STATES
            or not isinstance(agent.get("receipt_reproduced"), bool)
        ):
            raise ValueError(f"invalid {label} recovery agent receipt")
        _require_digest(
            agent.get("id_sha256"), length=64, label=f"{label} recovery agent"
        )
    if not _nonnegative_int(value.get("marker_ids_count")):
        raise ValueError(f"invalid {label} recovery marker receipt")
    _require_digest(
        value.get("marker_ids_sha256"),
        length=64,
        label=f"{label} recovery markers",
    )


def _validate_result_receipt(
    value: Any,
    *,
    label: str,
    required: bool,
    recovery_required: bool | None,
    expected_permissions: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if value is None:
        if required:
            raise ValueError(f"missing {label} result receipt")
        return None
    if not isinstance(value, dict) or set(value) != RESULT_RECEIPT_FIELDS:
        raise ValueError(f"invalid {label} result receipt")
    for field in (
        "result_sha256",
        "open_gates_sha256",
        "evidence_sha256",
        "reason_sha256",
    ):
        _require_digest(value.get(field), length=64, label=f"{label} result {field}")
    if (
        value.get("decision")
        not in {"continue", "stop_for_user", "complete", "incomplete"}
        or not isinstance(value.get("qualifies"), bool)
        or value.get("execplan_condition")
        not in {"not_required", "missing", "usable", "needs_amendment"}
        or any(
            not isinstance(value.get(field), bool)
            for field in (
                "protocol_may_product_write",
                "protocol_may_review",
                "protocol_may_complete",
            )
        )
        or not _nonnegative_int(value.get("open_gates_count"))
        or not _nonnegative_int(value.get("evidence_count"))
        or not isinstance(value.get("goal_pause_handoff_present"), bool)
    ):
        raise ValueError(f"invalid {label} result receipt")
    findings = value.get("finding_classifications")
    blockers = value.get("blocker_classifications")
    if not isinstance(findings, list) or not isinstance(blockers, list):
        raise ValueError(f"invalid {label} result classifications")
    for finding in findings:
        if (
            not isinstance(finding, dict)
            or set(finding) != FINDING_RECEIPT_FIELDS
            or finding.get("domain")
            not in {"secret", "baseline_failure", "receipt", "other"}
            or finding.get("state")
            not in {"baseline_unchanged", "resolved", "candidate_new", "unknown"}
            or not _nonnegative_int(finding.get("anchors_count"))
        ):
            raise ValueError(f"invalid {label} result finding receipt")
        for field in (
            "identity_sha256",
            "identity_casefold_sha256",
            "anchors_sha256",
        ):
            _require_digest(
                finding.get(field), length=64, label=f"{label} finding {field}"
            )
        _validate_digest_list(
            finding.get("identity_match_sha256s"),
            label=f"{label} finding identity matches",
            required=True,
        )
        if finding["identity_casefold_sha256"] not in finding["identity_match_sha256s"]:
            raise ValueError(f"invalid {label} result finding identity matches")
        _validate_digest_list(
            finding.get("anchor_sha256s"),
            label=f"{label} finding anchors",
            required=finding["anchors_count"] > 0,
        )
        if finding["anchors_count"] == 0 and finding["anchor_sha256s"]:
            raise ValueError(f"invalid {label} result finding anchors")
    for blocker in blockers:
        if (
            not isinstance(blocker, dict)
            or set(blocker) != BLOCKER_RECEIPT_FIELDS
            or blocker.get("class") not in BLOCKER_CLASSES
            or not isinstance(blocker.get("blocking"), bool)
        ):
            raise ValueError(f"invalid {label} result blocker receipt")
        for field in (
            "identity_sha256",
            "identity_casefold_sha256",
            "reason_sha256",
        ):
            _require_digest(
                blocker.get(field), length=64, label=f"{label} blocker {field}"
            )
        _validate_digest_list(
            blocker.get("identity_match_sha256s"),
            label=f"{label} blocker identity matches",
            required=True,
        )
        if blocker["identity_casefold_sha256"] not in blocker["identity_match_sha256s"]:
            raise ValueError(f"invalid {label} result blocker identity matches")
    blocker_identities = [item["identity_casefold_sha256"] for item in blockers]
    if len(set(blocker_identities)) != len(blocker_identities):
        raise ValueError(f"invalid {label} duplicate blocker receipt")
    if expected_permissions is not None:
        for field in PERMISSION_FIELDS:
            allowed = expected_permissions.get(field)
            allowed = allowed if isinstance(allowed, list) else [allowed]
            if value.get(field) not in allowed:
                raise ValueError(f"invalid {label} oracle permission receipt")
    completion_claimed = (
        value["decision"] == "complete" or value["protocol_may_complete"] is True
    )
    if completion_claimed and (
        value["decision"] != "complete"
        or value["protocol_may_complete"] is not True
        or value["open_gates_count"] != 0
        or any(item["blocking"] is True for item in blockers)
        or any(item["state"] in {"candidate_new", "unknown"} for item in findings)
    ):
        raise ValueError(f"invalid {label} completion receipt")
    recovery = value.get("recovery_state")
    if recovery_required is True:
        _validate_recovery_receipt(recovery, label=label)
    elif recovery_required is False:
        if recovery is not None:
            raise ValueError(f"unexpected {label} recovery receipt")
    elif recovery is not None:
        _validate_recovery_receipt(recovery, label=label)
    return value


def _validate_compaction_phase(value: Any, *, label: str) -> None:
    if not isinstance(value, dict) or set(value) != COMPACTION_PHASE_FIELDS:
        raise ValueError(f"invalid native compaction {label} receipt")
    for field in ("phase_sha256", "rollout_path_sha256", "rollout_sha256"):
        _require_digest(value.get(field), length=64, label=f"native {label} {field}")
    prefix_sha256 = value.get("rollout_prefix_sha256")
    if prefix_sha256 is not None:
        _require_digest(
            prefix_sha256,
            length=64,
            label=f"native {label} rollout_prefix_sha256",
        )
    event_types = value.get("event_types")
    if (
        any(
            not _nonnegative_int(value.get(field))
            for field in (
                "compaction_event_count",
                "context_compacted_marker_count",
                "rollout_byte_count",
                "rollout_match_count",
            )
        )
        or not isinstance(event_types, list)
        or any(event not in COMPACTION_EVENT_TYPES for event in event_types)
        or value["compaction_event_count"] != event_types.count("compacted")
        or value["context_compacted_marker_count"]
        != event_types.count("context_compacted")
        or value["rollout_match_count"] != 1
        or value["compaction_event_count"] < 1
    ):
        raise ValueError(f"invalid native compaction {label} receipt")


def _validate_native_compaction(
    value: Any,
    *,
    case: dict[str, Any],
    receipt: dict[str, Any],
    result: dict[str, Any] | None,
    fresh_result: dict[str, Any] | None,
    native_evidence_oracle: dict[str, Any] | None,
) -> None:
    native = case["fixture"].get("native_compaction_resume")
    if native is None:
        if value is not None:
            raise ValueError("unexpected native compaction receipt")
        return
    if not isinstance(value, dict) or set(value) != NATIVE_COMPACTION_FIELDS:
        raise ValueError("missing or invalid native compaction receipt")
    if not isinstance(native_evidence_oracle, dict) or set(native_evidence_oracle) != {
        "recovery_state",
        "post_compaction_transition_sha256",
    }:
        raise ValueError("missing native evidence oracle")
    for field in (
        "native_compaction_sha256",
        "post_compaction_transition_sha256",
    ):
        _require_digest(value.get(field), length=64, label=f"native {field}")
    if (
        value["post_compaction_transition_sha256"]
        != native_evidence_oracle["post_compaction_transition_sha256"]
    ):
        raise ValueError("invalid native post-compaction transition receipt")
    if (
        value.get("auto_compact_token_limit") != native["auto_compact_token_limit"]
        or not _nonnegative_int(value.get("compaction_event_count"))
        or value["compaction_event_count"] < 1
        or value.get("resumed_same_thread") is not True
    ):
        raise ValueError("invalid native compaction receipt")
    _validate_compaction_phase(value.get("before_resume"), label="before-resume")
    _validate_compaction_phase(value.get("after_resume"), label="after-resume")
    before = value["before_resume"]
    after = value["after_resume"]
    if (
        value["compaction_event_count"] != before["compaction_event_count"]
        or after["rollout_path_sha256"] != before["rollout_path_sha256"]
        or after["rollout_sha256"] == before["rollout_sha256"]
        or before["rollout_prefix_sha256"] is not None
        or after["rollout_prefix_sha256"] != before["rollout_sha256"]
        or after["rollout_byte_count"] <= before["rollout_byte_count"]
        or after["event_types"][: len(before["event_types"])] != before["event_types"]
    ):
        raise ValueError("invalid native compaction rollout relationship")
    fresh = value.get("fresh_control")
    if not isinstance(fresh, dict) or set(fresh) != FRESH_CONTROL_FIELDS:
        raise ValueError("missing or invalid native fresh-control receipt")
    for field in (
        "fresh_control_sha256",
        "thread_id_sha256",
        "prompt_sha256",
        "allowed_label_differences_sha256",
    ):
        _require_digest(value=fresh.get(field), length=64, label=f"native {field}")
    if (
        fresh.get("distinct_from_resumed_task") is not True
        or fresh.get("no_resume_handle") is not True
        or fresh.get("no_conversation_summary") is not True
        or fresh.get("equivalent_gate_fields")
        != [*sorted(RECOVERY_GATE_FIELDS), "recovery_state"]
    ):
        raise ValueError("invalid native fresh-control receipt")
    primary_thread = receipt["thread_id_sha256"]
    resume_thread = receipt["resume_thread_id_sha256"]
    fresh_thread = receipt["fresh_recovery_thread_id_sha256"]
    missing_thread = sha256_bytes(b"None")
    if (
        primary_thread == missing_thread
        or resume_thread != primary_thread
        or fresh_thread == missing_thread
        or fresh_thread == primary_thread
        or fresh["thread_id_sha256"] != fresh_thread
    ):
        raise ValueError("invalid native thread-control receipt")
    if (
        result is None
        or fresh_result is None
        or any(result[field] != fresh_result[field] for field in RECOVERY_GATE_FIELDS)
    ):
        raise ValueError("invalid native recovery-control receipt")
    allowed_differences = {
        field: [result[field], fresh_result[field]]
        for field in ("decision", "execplan_condition")
        if result[field] != fresh_result[field]
    }
    if fresh["allowed_label_differences_sha256"] != canonical_sha256(
        allowed_differences
    ):
        raise ValueError("invalid native recovery-control labels receipt")
    recovery = result["recovery_state"]
    fresh_recovery = fresh_result["recovery_state"]
    if not isinstance(recovery, dict) or not isinstance(fresh_recovery, dict):
        raise ValueError("invalid native recovery-control state receipt")
    recovery_oracle = native_evidence_oracle["recovery_state"]
    _validate_recovery_oracle_receipt(recovery, oracle=recovery_oracle, label="primary")
    _validate_recovery_oracle_receipt(
        fresh_recovery, oracle=recovery_oracle, label="fresh"
    )
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        if recovery[field] != fresh_recovery[field]:
            raise ValueError(f"invalid native recovery-control state: {field}")


def _validate_installation_receipt(
    value: Any, *, package: dict[str, str], case_id: str
) -> None:
    if not isinstance(value, dict) or set(value) != INSTALLATION_RECEIPT_FIELDS:
        raise ValueError(f"invalid corpus evidence installation: {case_id}")
    for field in INSTALLATION_RECEIPT_FIELDS:
        _require_digest(value.get(field), length=64, label=f"case installation {field}")
    if (
        value["source_skill_sha256"] != value["installed_skill_sha256"]
        or value["source_package_manifest_sha256"] != package["artifact_sha256"]
        or value["installed_package_manifest_sha256"] != package["artifact_sha256"]
    ):
        raise ValueError(f"corpus evidence installation mismatch: {case_id}")


def _validate_isolation_receipt(value: Any, *, case_id: str) -> None:
    if not isinstance(value, dict) or set(value) != FILESYSTEM_RECEIPT_FIELDS:
        raise ValueError(f"invalid corpus evidence isolation: {case_id}")
    expected = {
        field: FILESYSTEM_ISOLATION_POLICY[field]
        for field in FILESYSTEM_RECEIPT_FIELDS - {"policy_sha256"}
    }
    if any(value.get(field) != expected[field] for field in expected):
        raise ValueError(f"corpus evidence isolation mismatch: {case_id}")
    expected_policy_sha256 = canonical_sha256(
        {
            **FILESYSTEM_ISOLATION_POLICY,
            "workspace_root": "<case-temp>/repo",
            "native_tool_root": "<case-temp>/bin",
        }
    )
    if value.get("policy_sha256") != expected_policy_sha256:
        raise ValueError(f"corpus evidence isolation policy mismatch: {case_id}")


def _validate_case_identity(
    receipt: Any,
    snapshot: dict[str, Any],
    case_id: str,
    *,
    case: dict[str, Any],
    native_evidence_oracle: dict[str, Any] | None,
    expected_passed: bool = True,
    semantic_sha256: str,
    package: dict[str, str],
    engine: dict[str, Any],
) -> None:
    settings = snapshot["settings"]
    if (
        not isinstance(receipt, dict)
        or set(receipt) != CASE_RECEIPT_FIELDS
        or receipt.get("schema_version") != 1
        or receipt.get("engine_generation") != "0.4"
        or receipt.get("id") != case_id
        or not isinstance(case, dict)
        or case.get("id") != case_id
    ):
        raise ValueError("invalid corpus evidence case")
    passed = receipt.get("passed")
    timed_out = receipt.get("timed_out")
    if (
        not isinstance(passed, bool)
        or not isinstance(timed_out, bool)
        or receipt.get("model") != settings["model"]
        or receipt.get("effort") != settings["effort"]
        or receipt.get("timeout_seconds") != settings["timeout_seconds"]
    ):
        raise ValueError(f"corpus evidence case did not pass: {case_id}")
    if receipt.get("semantic_input_sha256") != semantic_sha256:
        raise ValueError(f"corpus evidence semantic identity mismatch: {case_id}")
    identities = receipt.get("identities")
    if not isinstance(identities, dict) or set(identities) != {
        "engine",
        "package",
        "toolchain",
    }:
        raise ValueError(f"corpus evidence identities missing: {case_id}")
    if identities.get("engine") != engine:
        raise ValueError(f"corpus evidence engine mismatch: {case_id}")
    if identities.get("package") != package:
        raise ValueError(f"corpus evidence package mismatch: {case_id}")
    if identities.get("toolchain") != snapshot["settings"]["toolchain"]:
        raise ValueError(f"corpus evidence toolchain mismatch: {case_id}")
    for field in (
        "metadata_sha256",
        "events_sha256",
        "stderr_sha256",
        "thread_id_sha256",
        "resume_thread_id_sha256",
        "fresh_recovery_thread_id_sha256",
    ):
        _require_digest(receipt.get(field), length=64, label=f"case {field}")
    _validate_installation_receipt(
        receipt.get("installation"), package=package, case_id=case_id
    )
    failures = receipt.get("oracle_failures")
    if expected_passed:
        if failures != {"count": 0, "sha256": canonical_sha256([])}:
            raise ValueError(f"corpus evidence oracle failed: {case_id}")
    elif (
        not isinstance(failures, dict)
        or set(failures) != {"count", "sha256"}
        or not isinstance(failures.get("count"), int)
        or isinstance(failures.get("count"), bool)
        or failures["count"] <= 0
        or failures.get("sha256") == canonical_sha256([])
    ):
        raise ValueError(f"invalid failed-arm oracle evidence: {case_id}")
    else:
        _require_digest(
            failures.get("sha256"), length=64, label="failed-arm oracle failures"
        )
    quality = completed_quality(
        passed=passed,
        timed_out=timed_out,
        exit_code=receipt.get("exit_code"),
        oracle_failures_count=failures["count"],
    )
    if (quality == "pass") is not expected_passed:
        raise ValueError(f"corpus evidence case outcome mismatch: {case_id}")
    elapsed = receipt.get("elapsed_seconds")
    uncached = receipt.get("uncached_input_tokens")
    usage = receipt.get("usage")
    phases = receipt.get("usage_phases")
    required_usage = {"input_tokens", "cached_input_tokens", "output_tokens"}
    native = case["fixture"].get("native_compaction_resume") is not None
    expected_phases = 3 if native else 1
    if (
        not isinstance(usage, dict)
        or not isinstance(phases, list)
        or len(phases) != expected_phases
        or any(
            not isinstance(phase, dict)
            or not required_usage.issubset(phase)
            or any(
                not isinstance(key, str)
                or not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
                for key, value in phase.items()
            )
            for phase in phases
        )
    ):
        raise ValueError(f"invalid corpus evidence telemetry: {case_id}")
    combined_usage = {
        key: sum(phase.get(key, 0) for phase in phases)
        for key in sorted({key for phase in phases for key in phase})
    }
    if (
        usage != combined_usage
        or usage["cached_input_tokens"] > usage["input_tokens"]
        or uncached != usage["input_tokens"] - usage["cached_input_tokens"]
    ):
        raise ValueError(f"invalid corpus evidence telemetry: {case_id}")
    expected_permissions = case["oracle"]["expected"] if expected_passed else None
    result_receipt = _validate_result_receipt(
        receipt.get("result"),
        label=f"case {case_id}",
        required=True,
        recovery_required=True if native and expected_passed else None,
        expected_permissions=expected_permissions,
    )
    if expected_passed:
        _validate_case_oracle_receipt(
            result_receipt, case=case, label=f"case {case_id}"
        )
    fresh_result_receipt = None
    if native:
        fresh_result_receipt = _validate_result_receipt(
            receipt.get("fresh_recovery_result"),
            label=f"case {case_id} fresh recovery",
            required=expected_passed,
            recovery_required=True if expected_passed else None,
            expected_permissions=expected_permissions,
        )
        if expected_passed:
            _validate_case_oracle_receipt(
                fresh_result_receipt,
                case=case,
                label=f"case {case_id} fresh recovery",
            )
    elif receipt.get("fresh_recovery_result") is not None:
        raise ValueError(f"unexpected fresh recovery result receipt: {case_id}")
    _validate_native_compaction(
        receipt.get("native_compaction"),
        case=case,
        receipt=receipt,
        result=result_receipt,
        fresh_result=fresh_result_receipt,
        native_evidence_oracle=native_evidence_oracle,
    )
    _validate_isolation_receipt(receipt.get("filesystem_isolation"), case_id=case_id)
    if (
        not isinstance(receipt.get("exit_code"), int)
        or isinstance(receipt.get("exit_code"), bool)
        or not isinstance(elapsed, (int, float))
        or isinstance(elapsed, bool)
        or not math.isfinite(elapsed)
        or elapsed < 0
        or not isinstance(uncached, int)
        or isinstance(uncached, bool)
        or uncached < 0
    ):
        raise ValueError(f"invalid corpus evidence telemetry: {case_id}")


def _validate_corpus_summary(
    payload: dict[str, Any],
    snapshot: dict[str, Any],
    source: dict[str, Any],
    live_authority: dict[str, Any],
) -> None:
    settings = snapshot["settings"]
    cases = payload.get("cases")
    if (
        set(payload) != CORPUS_SUMMARY_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.4"
        or payload.get("impact_token") != live_authority["impact_token"]
        or payload.get("live_authority_sha256") != canonical_sha256(live_authority)
        or payload.get("arm") != "candidate"
        or payload.get("model") != settings["model"]
        or payload.get("effort") != settings["effort"]
        or payload.get("timeout_seconds") != settings["timeout_seconds"]
        or payload.get("telemetry_complete") is not True
        or not isinstance(cases, list)
    ):
        raise ValueError("invalid corpus certification evidence")
    by_id = {
        item.get("id"): item
        for item in cases
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    expected = set(live_authority["impact"]["corpus_cases"])
    if not expected:
        raise ValueError("corpus certification evidence has no authorized scope")
    if set(by_id) != expected or len(by_id) != len(cases):
        raise ValueError("corpus certification evidence is incomplete")
    if payload.get("total") != len(expected) or payload.get("passed") != len(expected):
        raise ValueError("corpus certification evidence is not all-pass")
    for case_id in sorted(expected):
        _validate_case_identity(
            by_id[case_id],
            snapshot,
            case_id,
            case=source.get("corpus_cases", {}).get(case_id),
            native_evidence_oracle=source.get("native_evidence_oracles", {}).get(
                case_id
            ),
            semantic_sha256=snapshot["corpus"]["cases"][case_id],
            package=snapshot["package"],
            engine=source["engine"],
        )
    if (
        payload.get("uncached_input_tokens")
        != sum(item["uncached_input_tokens"] for item in cases)
        or payload.get("output_tokens")
        != sum(item["usage"]["output_tokens"] for item in cases)
        or payload.get("elapsed_seconds")
        != round(sum(item["elapsed_seconds"] for item in cases), 3)
    ):
        raise ValueError("corpus certification evidence telemetry mismatch")


def _validate_holdout_run(
    payload: dict[str, Any],
    snapshot: dict[str, Any],
    authority: dict[str, Any],
    source: dict[str, Any],
) -> tuple[list[str], dict[str, str]]:
    settings = snapshot["settings"]
    identities = payload.get("identities")
    packages = identities.get("packages") if isinstance(identities, dict) else None
    engine = identities.get("engine") if isinstance(identities, dict) else None
    pair_ids = payload.get("pair_ids")
    if (
        set(payload) != HOLDOUT_RUN_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.4"
        or payload.get("impact_token") != authority["impact_token"]
        or payload.get("live_authority_sha256") != canonical_sha256(authority)
        or payload.get("manifest_sha256") != source["holdout_manifest_sha256"]
        or payload.get("model") != settings["model"]
        or payload.get("effort") != settings["effort"]
        or payload.get("timeout_seconds") != settings["timeout_seconds"]
        or engine != source["engine"]
        or not isinstance(packages, dict)
        or set(packages) != {"candidate", "public-0.2"}
        or packages.get("candidate") != snapshot["package"]
        or not isinstance(pair_ids, list)
        or pair_ids != source["holdout_pair_order"]
        or payload.get("case_sha256")
        != {
            pair_id: descriptor["case_sha256"]
            for pair_id, descriptor in source["holdout_descriptors"].items()
        }
        or identities.get("toolchain") != snapshot["settings"]["toolchain"]
    ):
        raise ValueError("invalid holdout run certification evidence")
    holdout_invocation = next(
        (item for item in authority["invocations"] if item["command"] == "holdout"),
        None,
    )
    public = packages.get("public-0.2")
    if holdout_invocation is not None:
        if not isinstance(public, dict) or public != {
            "semantic_sha256": holdout_invocation["public_semantic_sha256"],
            "artifact_sha256": holdout_invocation["public_artifact_sha256"],
        }:
            raise ValueError("holdout public evidence does not match authority")
    elif (
        not isinstance(public, dict)
        or set(public) != {"semantic_sha256", "artifact_sha256"}
        or public.get("artifact_sha256") != PUBLIC_02_PACKAGE_ARTIFACT_SHA256
    ):
        raise ValueError("invalid holdout public evidence")
    return pair_ids, public


def _validate_arm_identity(
    receipt: Any,
    snapshot: dict[str, Any],
    *,
    arm: str,
    expected_passed: bool,
    descriptor: dict[str, Any],
    package: dict[str, str],
    source: dict[str, Any],
) -> None:
    settings = snapshot["settings"]
    semantic_sha256 = case_semantic_sha256(
        descriptor["case"],
        shared_semantic_sha256=source["corpus_semantic_sha256"],
        package_semantic_sha256=package["semantic_sha256"],
        model=settings["model"],
        effort=settings["effort"],
        timeout=settings["timeout_seconds"],
        arm=arm,
    )
    _validate_case_identity(
        receipt,
        snapshot,
        descriptor["case"]["id"],
        case=descriptor["case"],
        native_evidence_oracle=source.get("native_evidence_oracles", {}).get(
            descriptor["case"]["id"]
        ),
        expected_passed=expected_passed,
        semantic_sha256=semantic_sha256,
        package=package,
        engine=source["engine"],
    )


def _validate_holdout_summary(
    payload: dict[str, Any],
    snapshot: dict[str, Any],
    *,
    run_pair_ids: list[str],
    run_sha256: str,
    public_package: dict[str, str],
    source: dict[str, Any],
) -> None:
    receipts = payload.get("pair_receipts")
    if (
        set(payload) != HOLDOUT_SUMMARY_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.4"
        or payload.get("run_receipt_sha256") != run_sha256
        or not isinstance(receipts, list)
        or payload.get("pairs_run") != len(receipts)
        or not receipts
    ):
        raise ValueError("invalid holdout summary certification evidence")
    pair_ids = [item.get("id") for item in receipts if isinstance(item, dict)]
    if pair_ids != run_pair_ids[: len(pair_ids)] or len(pair_ids) != len(receipts):
        raise ValueError("holdout summary pair ordering mismatch")
    outcomes = [item.get("outcome") for item in receipts]
    if not all(isinstance(outcome, str) for outcome in outcomes):
        raise ValueError("invalid holdout outcome evidence")
    terminal_action = adaptive_next(outcomes)
    if (
        payload.get("adaptive_history") != outcomes
        or payload.get("adaptive_terminal_action") != terminal_action
    ):
        raise ValueError("holdout adaptive evidence mismatch")
    if terminal_action not in {"stop", "reject"}:
        raise ValueError("holdout adaptive evidence is not terminal")
    for receipt in receipts:
        if not isinstance(receipt, dict) or set(receipt) != PAIR_RECEIPT_FIELDS:
            raise ValueError("invalid holdout pair evidence")
        descriptor = source["holdout_descriptors"].get(receipt["id"])
        if (
            receipt.get("schema_version") != 1
            or receipt.get("engine_generation") != "0.4"
            or not isinstance(descriptor, dict)
            or receipt.get("case_id") != descriptor["case"]["id"]
            or receipt.get("case_sha256") != descriptor["case_sha256"]
            or receipt.get("outside_diff_boundary")
            is not descriptor["outside_diff_boundary"]
            or receipt.get("oracle_kind") != descriptor["oracle_kind"]
        ):
            raise ValueError("holdout pair does not match source descriptor")
        for field in (
            "mapping_commitment_file_sha256",
            "pre_reveal_decision_file_sha256",
            "mapping_reveal_file_sha256",
            "pre_reveal_decision_sha256",
            "mapping_commitment_sha256",
        ):
            _require_digest(
                receipt.get(field), length=64, label=f"holdout pair {field}"
            )
        arms = receipt.get("arms") if isinstance(receipt, dict) else None
        if not isinstance(arms, dict) or set(arms) != {"candidate", "public-0.2"}:
            raise ValueError("invalid holdout arm evidence")
        candidate_passed = (
            arms["candidate"].get("passed")
            if isinstance(arms["candidate"], dict)
            else None
        )
        public_passed = (
            arms["public-0.2"].get("passed")
            if isinstance(arms["public-0.2"], dict)
            else None
        )
        if not isinstance(candidate_passed, bool) or not isinstance(
            public_passed, bool
        ):
            raise ValueError("invalid holdout arm outcome evidence")
        derived_outcome = (
            "regression"
            if not candidate_passed
            else "better"
            if not public_passed
            else "equal"
        )
        if receipt.get("outcome") != derived_outcome:
            raise ValueError("holdout outcome mismatch")
        _validate_arm_identity(
            arms["candidate"],
            snapshot,
            arm="candidate",
            expected_passed=candidate_passed,
            descriptor=descriptor,
            package=snapshot["package"],
            source=source,
        )
        _validate_arm_identity(
            arms["public-0.2"],
            snapshot,
            arm="public-0.2",
            expected_passed=public_passed,
            descriptor=descriptor,
            package=public_package,
            source=source,
        )
        expected_metrics = {
            arm: {
                "uncached_input_tokens": arms[arm]["uncached_input_tokens"],
                "output_tokens": arms[arm]["usage"]["output_tokens"],
                "elapsed_seconds": arms[arm]["elapsed_seconds"],
            }
            for arm in ("candidate", "public-0.2")
        }
        if receipt.get("metrics") != expected_metrics:
            raise ValueError("holdout arm metrics mismatch")
    quality = aggregate_quality(outcomes)
    aggregate = {
        arm: sum_metrics([receipt["metrics"][arm] for receipt in receipts])
        for arm in ("candidate", "public-0.2")
    }
    expected_gate = cost_gate(
        aggregate["candidate"], aggregate["public-0.2"], quality=quality
    )
    if (
        payload.get("cost_gate") != expected_gate
        or not expected_gate["release_permitted"]
    ):
        raise ValueError("holdout cost/quality evidence does not permit certification")


def _validate_certification_receipt(
    certification: Any,
    *,
    snapshot: dict[str, Any],
    prior_evidence: dict[str, Any],
    historical_cost: dict[str, Any],
    live_authority: dict[str, Any] | None,
    repo: Path | None,
) -> None:
    if (
        not isinstance(certification, dict)
        or set(certification) != CERTIFICATION_FIELDS
    ):
        raise ValueError("invalid certification receipt")
    if certification.get("schema_version") != 1:
        raise ValueError("invalid certification receipt schema")
    snapshot_sha256 = canonical_sha256(snapshot)
    if certification.get("snapshot_sha256") != snapshot_sha256:
        raise ValueError("certification receipt snapshot mismatch")
    if (
        certification.get("engine_manifest_sha256")
        != snapshot["engine"]["manifest_sha256"]
    ):
        raise ValueError("certification receipt engine manifest mismatch")
    if certification.get("live_authority_sha256") != canonical_sha256(live_authority):
        raise ValueError("certification receipt authority mismatch")
    if live_authority is not None:
        validate_live_authority(live_authority, snapshot=snapshot)
    if repo is None or not (repo / ".git").exists():
        raise ValueError("reachable certification evidence requires a Git repository")
    repo = repo.resolve()
    source_commit = certification.get("successor_source_commit")
    _require_reachable_commit(repo, source_commit, label="successor source commit")
    tree = _run_git(repo, "rev-parse", f"{source_commit}^{{tree}}")
    if (
        tree.returncode
        or certification.get("successor_source_tree") != tree.stdout.decode().strip()
    ):
        raise ValueError("certification successor source tree mismatch")
    source = _validate_source_identity(
        repo,
        source_commit,
        snapshot,
        live_authority,
    )
    if source["ledger"]["prior_evidence"] != prior_evidence:
        raise ValueError("prior certified ledger digest or locator mismatch")
    if source["ledger"]["historical_cost"] != historical_cost:
        raise ValueError("certification source historical cost mismatch")
    source_pending = source["ledger"]["pending"]
    if source_pending["review"] is not True:
        raise ValueError("certification source must retain the external review gate")
    incremental = (
        source["ledger"]["prior_evidence"].get("source_path")
        == "evaluation/results/current.json"
    )
    if incremental:
        prior = _load_prior_certified_ledger(
            repo,
            source["ledger"]["prior_evidence"],
            source_commit=source_commit,
        )
        try:
            expected_impact = plan_impact(
                prior["snapshot"],
                snapshot,
                pending=source_pending,
            )
        except (OSError, ValueError) as exc:
            raise ValueError("invalid incremental certification impact") from exc
    else:
        try:
            expected_impact = plan_impact(
                snapshot,
                snapshot,
                pending=source_pending,
            )
        except (OSError, ValueError) as exc:
            raise ValueError("invalid certification source pending impact") from exc
    live_required = expected_impact["live_calls"]["maximum"] > 0
    if live_required:
        if live_authority is None:
            raise ValueError("nonzero certification impact requires live authority")
        if expected_impact != live_authority["impact"]:
            raise ValueError("certification source authority impact mismatch")
    elif live_authority is not None:
        raise ValueError("zero-live certification must not carry live authority")
    evidence_fields, carries_prior = _validate_coverage(
        certification.get("coverage"),
        snapshot=snapshot,
        impact=expected_impact,
    )
    offline_gate_set = _offline_gates(expected_impact)
    if offline_gate_set:
        evidence_fields.add("offline_summary")
    if carries_prior and not incremental:
        raise ValueError("certification prior coverage does not match source lineage")
    evidence = certification.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != evidence_fields:
        if offline_gate_set and (
            not isinstance(evidence, dict) or "offline_summary" not in evidence
        ):
            raise ValueError("offline certification evidence is required")
        raise ValueError("invalid certification evidence envelope")
    loaded: dict[str, dict[str, Any]] = {}
    evidence_sha: dict[str, str] = {}
    for label in sorted(evidence_fields):
        loaded[label], evidence_sha[label] = _load_evidence(
            repo,
            evidence[label],
            label=label,
            source_commit=source_commit,
        )
    if "corpus_summary" in loaded:
        if live_authority is None:
            raise AssertionError("corpus evidence cannot exist without live authority")
        _validate_corpus_summary(
            loaded["corpus_summary"],
            snapshot,
            source,
            live_authority,
        )
    if "holdout_run" in loaded:
        if live_authority is None:
            raise AssertionError("holdout evidence cannot exist without live authority")
        pair_ids, public_package = _validate_holdout_run(
            loaded["holdout_run"], snapshot, live_authority, source
        )
        _validate_holdout_summary(
            loaded["holdout_summary"],
            snapshot,
            run_pair_ids=pair_ids,
            run_sha256=evidence_sha["holdout_run"],
            public_package=public_package,
            source=source,
        )
    if "offline_summary" in loaded:
        _validate_offline_summary(
            loaded["offline_summary"],
            snapshot=snapshot,
            source_commit=source_commit,
            source_ledger_sha256=source["ledger_sha256"],
            gates=offline_gate_set,
        )


def validate_ledger(ledger: dict[str, Any], *, repo: Path | None = None) -> None:
    if set(ledger) != LEDGER_FIELDS or ledger.get("schema_version") != 1:
        raise ValueError("invalid certification ledger envelope")
    state = ledger.get("state")
    if state not in {"refresh_required", "certified"}:
        raise ValueError("invalid certification ledger state")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("invalid certification snapshot")
    validate_snapshot(snapshot)
    prior = ledger.get("prior_evidence")
    if not isinstance(prior, dict):
        raise ValueError("invalid prior evidence")
    for field in ("source_commit", "source_path", "sha256"):
        if not isinstance(prior.get(field), str):
            raise ValueError(f"invalid prior evidence field: {field}")
    _require_digest(prior["source_commit"], length=40, label="prior evidence commit")
    _require_digest(prior["sha256"], length=64, label="prior evidence digest")
    pending = ledger.get("pending")
    if not isinstance(pending, dict) or set(pending) != PENDING_FIELDS:
        raise ValueError("invalid pending refresh envelope")
    if (
        not isinstance(pending["reasons"], list)
        or not all(isinstance(item, str) and item for item in pending["reasons"])
        or pending["reasons"] != sorted(set(pending["reasons"]))
    ):
        raise ValueError("invalid pending reasons")
    for field in ("corpus_cases", "holdout_pairs"):
        value = pending[field]
        if (
            not isinstance(value, list)
            or not all(isinstance(item, str) and item for item in value)
            or value != sorted(set(value))
        ):
            raise ValueError(f"invalid pending scope: {field}")
    if not isinstance(pending["review"], bool):
        raise ValueError("invalid pending review gate")
    if ledger.get("historical_cost") != historical_cost_receipt():
        raise ValueError("invalid historical cost receipt")
    live_authority = ledger.get("live_authority")
    if live_authority is not None:
        validate_live_authority(live_authority, snapshot=snapshot)
    certification = ledger.get("certification")
    if state == "refresh_required":
        if certification is not None:
            raise ValueError("refresh-required ledger cannot carry certification")
        if not (
            pending["reasons"]
            or pending["corpus_cases"]
            or pending["holdout_pairs"]
            or pending["review"]
        ):
            raise ValueError("refresh-required ledger must name a pending gate")
    else:
        if (
            pending["reasons"]
            or pending["corpus_cases"]
            or pending["holdout_pairs"]
            or pending["review"]
        ):
            raise ValueError("certified ledger cannot retain pending gates")
        _validate_certification_receipt(
            certification,
            snapshot=snapshot,
            prior_evidence=prior,
            historical_cost=ledger["historical_cost"],
            live_authority=live_authority,
            repo=repo,
        )


def load_ledger(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("certification ledger must be an object")
    repo = path.resolve().parents[2]
    validate_ledger(value, repo=repo)
    return value


def ledger_sha256(ledger: dict[str, Any], *, repo: Path | None = None) -> str:
    validate_ledger(ledger, repo=repo)
    return canonical_sha256(ledger)
