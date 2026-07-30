from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from typing import Any

from evaluation.core.identity import (
    BLOCKER_CLASSES,
    PERMISSION_FIELDS,
    PERMISSION_VALUES,
    RECOVERY_ACTIONS,
    RECOVERY_MANIFEST_PATTERN,
    RECOVERY_PENDING_GATES,
    RECOVERY_STATE_FIELDS,
    canonical_sha256,
    permission_assertions_invalid,
    sha256_bytes,
    source_archive_identity,
)
from evaluation.core.impact import validate_gate_plan, validate_snapshot, validate_successor
from evaluation.core.schema import CONTRACTS, validate_named
from evaluation.holdout.compare import adaptive_next


LIVE_SLOTS = ("executor", "corpus", "holdout")
EVIDENCE_SLOTS = (
    "executor", "corpus", "holdout", "receipt", "review", "isolated_install",
)
PENDING_GATES = (
    "corpus", "executor_pilot", "holdout", "isolated_install", "receipt", "review",
)
LEDGER_FIELDS = frozenset(CONTRACTS["schemas"]["ledger"]["required"])
EVIDENCE_KINDS = {
    "executor": "executor_calibration",
    "corpus": "corpus_summary",
    "holdout": "holdout_summary",
    "receipt": "offline_summary",
    "review": "review_summary",
    "isolated_install": "offline_summary",
}
COST_FIELDS = {
    "schema_version", "gate", "basis", "basis_sha256", "basis_receipt_sha256",
    "model_calls", "uncached_input_tokens", "output_tokens", "combined_tokens",
    "wall_milliseconds", "cost_sha256",
}
AUTHORITY_FIELDS = {
    "schema_version", "gate", "phase", "impact_token", "invocation_sha256",
    "action", "request_sha256", "affirmative_sha256", "host", "authority_sha256",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
RECOVERY_MANIFEST_PATH = "docs/execplans/recovery-manifest.json"


def _unique_strings(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(type(item) is not str or not item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"invalid {label}")
    return value


def _validate_recovery_manifest(native: dict[str, Any], case_id: str) -> None:
    markers = [
        item
        for item in native["recovery_oracle"].get("marker_ids", [])
        if type(item) is str and RECOVERY_MANIFEST_PATTERN.fullmatch(item)
    ]
    if len(markers) != 1:
        raise ValueError(f"invalid Recovery Manifest marker: {case_id}")
    digest = RECOVERY_MANIFEST_PATTERN.fullmatch(markers[0]).group(1)
    content = native["post_compaction_transition"]["files"].get(
        RECOVERY_MANIFEST_PATH
    )
    if type(content) is not str or sha256_bytes(content.encode()) != digest:
        raise ValueError(f"Recovery Manifest digest mismatch: {case_id}")
    manifest = json.loads(content)
    validate_named(CONTRACTS, "recovery_manifest", manifest)
    repositories = manifest["repositories"]
    claim = manifest["resource_claim"]
    resources = claim["resources"]
    convergence = manifest["convergence"]
    families = convergence["families"]
    tests = manifest["tests"]
    selected = manifest["selected_checkpoint"]
    agents = manifest["agents"]
    selected_ok = (
        (
            (
                type(selected["ref"]) is str
                and re.fullmatch(
                    r"refs/(?!.*(?:\.\.|//|@\{|\\))[A-Za-z0-9._/-]*[A-Za-z0-9_-]",
                    selected["ref"],
                ) is not None
            )
            if selected["archive"] is None
            else selected["ref"] is None
            and type(selected["archive"]) is str
            and re.fullmatch(r"sha256:[0-9a-f]{64}", selected["archive"]) is not None
        )
    )
    if (
        len({item["namespace"] for item in repositories}) != len(repositories)
        or {item.partition(":")[0] for item in resources}
        != {"worktree", "ref", "ledger", "output", "activation"}
        or not selected_ok
        or len({item["family_id"] for item in families}) != len(families)
        or tests["accepted_failures"] > tests["failed"]
        or any(item["receipt_reproduced"] is not True for item in agents)
        or len({item["id"] for item in agents}) != len(agents)
        or any(
            (item["recurrence"] == 0 and not item["repair_batch"].endswith("/instance"))
            or (item["recurrence"] > 0 and not item["repair_batch"].endswith("/boundary"))
            or (item["status"] == "boundary_required" and item["recurrence"] != 1)
            or (
                item["recurrence"] >= 2
                and (
                    item["status"] != "open"
                    or convergence["phase"] != "focused_hardening"
                    or "user_selection" not in manifest["gates"]
                )
            )
            for item in families
        )
    ):
        raise ValueError(f"invalid Recovery Manifest state: {case_id}")


def validate_case_input(case: dict[str, Any], path: Path) -> None:
    validate_named(CONTRACTS, "case", case)
    if "$happycodex:happycodex" not in case["prompt"]:
        raise ValueError(f"invalid case envelope: {path}")
    fixture, oracle = case["fixture"], case["oracle"]
    if not fixture.get("commits"):
        raise ValueError(f"case needs a commit: {case['id']}")
    expected = oracle.get("expected", {})
    if set(expected) != PERMISSION_FIELDS or permission_assertions_invalid(expected):
        raise ValueError(f"invalid permission state: {case['id']}")
    accepted = _unique_strings(
        oracle.get("accepted_baseline_failures", []), "accepted baseline failures"
    )
    if len(accepted) != len(set(accepted)):
        raise ValueError(f"ambiguous accepted baseline failures: {case['id']}")
    prompts = [case["prompt"]]
    native = fixture.get("native_compaction_resume")
    if native is not None:
        native_fields = {
            "prepare_prompt",
            "fresh_recovery_prompt",
            "auto_compact_token_limit",
            "post_compaction_transition",
            "recovery_oracle",
        }
        if (
            not isinstance(native, dict)
            or set(native) != native_fields
            or type(native["auto_compact_token_limit"]) is not int
            or native["auto_compact_token_limit"] <= 0
            or set(native["recovery_oracle"])
            != RECOVERY_STATE_FIELDS
            - {"baseline_revision", "baseline_tree", "current_revision", "current_tree"}
        ):
            raise ValueError(f"invalid native compaction: {case['id']}")
        _validate_recovery_manifest(native, case["id"])
        prompts += [native["prepare_prompt"], native["fresh_recovery_prompt"]]
    identities = set()
    for key, item_fields, identity_field in (
        ("required_classifications", {"identity", "domain", "state"}, "identity"),
        ("required_blocker_classifications", {"identity", "class"}, "identity"),
        ("required_anchored_blockers", {"anchor", "class"}, "anchor"),
        ("required_anchored_classifications", {"anchor", "domain", "state"}, "anchor"),
    ):
        values = oracle.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"invalid {key}: {case['id']}")
        for item in values:
            identity = item.get(identity_field) if isinstance(item, dict) else None
            if (
                not isinstance(item, dict)
                or set(item) != item_fields
                or type(identity) is not str
                or not identity.strip()
            ):
                raise ValueError(f"invalid {key}: {case['id']}")
            identities.add(identity)
    classes = oracle.get("required_blocker_classes", [])
    if not isinstance(classes, list) or any(item not in BLOCKER_CLASSES for item in classes):
        raise ValueError(f"invalid blocker class: {case['id']}")
    coverage = oracle.get("coverage_assertions")
    if coverage is not None and (
        not isinstance(coverage, list)
        or len(coverage) != len(case["covers"])
        or {item.get("tag") for item in coverage} != set(case["covers"])
        or any(
            item.get("kind") != "recovery"
            and item.get("identity", item.get("anchor")) not in identities
            for item in coverage
        )
    ):
        raise ValueError(f"invalid coverage assertions: {case['id']}")
    prompt = " ".join(prompts).casefold()
    if any(item.casefold() in prompt for item in oracle.get("prompt_forbidden", [])):
        raise ValueError(f"prompt leaks oracle term: {case['id']}")


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode:
        raise ValueError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def validate_evidence_commit(
    repo: Path, *, source_commit: str, evidence_commit: str
) -> None:
    """Require evidence to be a strict, HEAD-reachable descendant of source."""
    source = _git(repo, "rev-parse", "--verify", f"{source_commit}^{{commit}}")
    evidence = _git(repo, "rev-parse", "--verify", f"{evidence_commit}^{{commit}}")
    head = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    if source == evidence:
        raise ValueError("evidence commit must strictly postdate source")
    for ancestor, descendant, message in (
        (source, evidence, "evidence commit does not descend from source"),
        (evidence, head, "evidence commit is not reachable from HEAD"),
    ):
        result = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", ancestor, descendant],
            check=False,
            capture_output=True,
        )
        if result.returncode:
            raise ValueError(message)


def validate_source_anchor(
    value: Any, *, repo: Path | None = None
) -> dict[str, str]:
    validate_named(CONTRACTS, "source_anchor", value)
    if repo is not None:
        archived = source_archive_identity(repo, value["source_commit"])
        expected = {
            "source_commit": archived["source_commit"],
            "source_tree": archived["source_tree"],
            "package_artifact_sha256": archived["package"]["artifact_sha256"],
            "package_semantic_sha256": archived["package"]["semantic_sha256"],
            "engine_manifest_sha256": archived["engine_manifest_sha256"],
            "executor_role_sha256": archived["executor_role_sha256"],
        }
        if any(value[field] != digest for field, digest in expected.items()):
            raise ValueError("source anchor does not match Git archive")
    return value


def _sealed(value: Any, field: str) -> bool:
    if not isinstance(value, dict) or _SHA256.fullmatch(str(value.get(field))) is None:
        return False
    payload = dict(value)
    digest = payload.pop(field)
    return digest == canonical_sha256(payload)


def _exact_record(value: Any, fields: set[str], seal: str | None = None) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == fields
        and value.get("schema_version") == 1
        and (seal is None or _sealed(value, seal))
    )


def _exact_range(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"min", "max"}
        and all(type(value[key]) is int and value[key] >= 0 for key in value)
        and value["min"] <= value["max"]
    )


def _slot_map(value: Any, names: tuple[str, ...], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(names):
        raise ValueError(f"invalid {label} slots")
    return value


def _validate_planning(ledger: dict[str, Any]) -> None:
    snapshot, anchor = ledger["snapshot"], ledger["source_anchor"]
    impact = ledger["planned_impact"]
    plans, cost = ledger["planned_invocations"], ledger["cost"]
    authorities, evidence = ledger["authorities"], ledger["accepted_evidence"]
    validate_named(CONTRACTS, "planned_impact", impact)
    scope = impact["initial_scope"]
    if (
        not _sealed(impact, "impact_token")
        or impact["snapshot_sha256"] != canonical_sha256(snapshot)
        or impact["source_anchor_sha256"] != canonical_sha256(anchor)
        or not isinstance(scope, dict)
        or set(scope) != {
            "gates", "corpus_cases", "holdout_pairs", "adaptive_policy_sha256",
        }
        or scope["gates"] != list(PENDING_GATES)
        or scope["corpus_cases"] != sorted(snapshot["corpus"]["cases"])
        or scope["holdout_pairs"] != sorted(snapshot["holdout"]["pairs"])
        or _SHA256.fullmatch(str(scope["adaptive_policy_sha256"])) is None
        or impact["initial_scope_sha256"] != canonical_sha256(scope)
        or not _exact_range(impact["live_calls"])
    ):
        raise ValueError("invalid immutable planned impact")
    calibration = evidence["executor"]
    ranges = (
        "model_calls", "uncached_input_tokens", "output_tokens",
        "combined_tokens", "wall_milliseconds",
    )
    for gate, item in cost.items():
        if item is None:
            continue
        basis = "source-derived" if gate == "executor" else "executor-calibration"
        receipt = None if gate == "executor" else (
            calibration["receipt_sha256"] if calibration else None
        )
        if (
            not _exact_record(item, COST_FIELDS, "cost_sha256")
            or (item["gate"], item["basis"], item["basis_receipt_sha256"])
            != (gate, basis, receipt)
            or _SHA256.fullmatch(str(item["basis_sha256"])) is None
            or any(not _exact_range(item[field]) for field in ranges)
        ):
            raise ValueError(f"invalid calibration cost basis: {gate}")
    for gate, plan in plans.items():
        if (plan is None) != (cost[gate] is None):
            raise ValueError("plan and cost must appear together")
        if plan is None:
            continue
        units = ["subthreshold-control"] if gate == "executor" else scope[
            "corpus_cases" if gate == "corpus" else "holdout_pairs"
        ]
        try:
            normalized = validate_gate_plan(plan)
        except ValueError as exc:
            raise ValueError(f"invalid persisted gate plan: {gate}") from exc
        if (
            gate != "executor" and calibration is None
            or normalized != plan
            or not _sealed(plan, "invocation_sha256")
            or (plan["gate"], plan["phase"])
            != (gate, "calibration" if gate == "executor" else "evaluation")
            or plan["impact_token"] != impact["impact_token"]
            or plan["role_config_sha256"] != snapshot["role"]["executor_sha256"]
            or plan["cost_sha256"] != cost[gate]["cost_sha256"]
            or plan["units"] != units
        ):
            raise ValueError(f"invalid persisted gate plan: {gate}")
    seen = set()
    for gate, item in authorities.items():
        if item is None:
            continue
        plan = plans[gate]
        host = item.get("host") if isinstance(item, dict) else None
        if (
            plan is None
            or not _exact_record(item, AUTHORITY_FIELDS, "authority_sha256")
            or item["gate"] != gate
            or item["phase"] != plan["phase"]
            or item["impact_token"] != impact["impact_token"]
            or item["invocation_sha256"] != plan["invocation_sha256"]
            or item["action"] != plan["action"]
            or any(_SHA256.fullmatch(str(item[field])) is None for field in ("request_sha256", "affirmative_sha256"))
            or not isinstance(host, dict)
            or set(host) != {
                "task_id", "message_id", "turn_id", "content_sha256", "role_config_sha256",
            }
            or host["role_config_sha256"] != plan["role_config_sha256"]
            or item["authority_sha256"] in seen
        ):
            raise ValueError(f"invalid distinct persisted authority: {gate}")
        seen.add(item["authority_sha256"])


def validate_evidence_record(item: Any, snapshot: dict[str, Any],
                             impact: dict[str, Any], invocations: dict[str, Any],
                             authorities: dict[str, Any], *, slot: str | None = None) -> None:
    validate_named(CONTRACTS, "evidence_record", item)
    slot = slot or item["gate"]
    producer, subject = item["producer"], item["subject"]
    if (
        slot not in EVIDENCE_SLOTS
        or not _sealed(item, "receipt_sha256")
        or item["kind"] != EVIDENCE_KINDS[slot]
        or item["gate"] != slot
        or Path(str(item["path"])).name != f"{item['content_sha256']}.json"
        or item["impact_token"] != impact["impact_token"]
        or producer.get("schema_version") != 1
        or subject.get("gate") != slot
        or subject.get("source_anchor_sha256") != impact["source_anchor_sha256"]
        or subject.get("snapshot_sha256") != impact["snapshot_sha256"]
    ):
        raise ValueError("invalid evidence slot, kind, units, receipt, producer, or subject")
    if slot in LIVE_SLOTS:
        plan, authority = invocations[slot], authorities[slot]
        if (
            plan is None or authority is None
            or item["invocation_sha256"] != plan["invocation_sha256"]
            or item["authority_sha256"] != authority["authority_sha256"]
            or item["pre_effect_grant_sha256"] != authority["authority_sha256"]
        ):
            raise ValueError("evidence does not bind exact authority")
    elif item["invocation_sha256"] is not None or item["authority_sha256"] is not None:
        raise ValueError("offline evidence borrowed live authority")
    if slot == "executor":
        actual = item["actual"]
        if (
            item["units"] != ["subthreshold-control"]
            or item["transcript"] != []
            or not isinstance(actual, dict)
            or set(actual) != {
                "model_calls", "uncached_input_tokens", "output_tokens",
                "combined_tokens", "wall_milliseconds",
            }
            or any(type(value) is not int or value < 0 for value in actual.values())
            or actual["model_calls"] != 1
            or actual["combined_tokens"] != actual["uncached_input_tokens"] + actual["output_tokens"]
        ):
            raise ValueError("invalid single Executor calibration evidence")
    elif slot == "corpus":
        if item["units"] != impact["initial_scope"]["corpus_cases"] or item["transcript"] != []:
            raise ValueError("corpus evidence is not exact")
    elif slot == "holdout":
        transcript = item["transcript"]
        pairs = impact["initial_scope"]["holdout_pairs"]
        if (
            not isinstance(transcript, list)
            or not transcript
            or len(transcript) > 3
            or any(
                not isinstance(row, dict)
                or set(row) != {"pair_id", "outcome", "receipt_sha256"}
                or row["pair_id"] != pairs[index]
                or row["outcome"] not in {"better", "equal", "uncertain", "regression"}
                or _SHA256.fullmatch(str(row["receipt_sha256"])) is None
                for index, row in enumerate(transcript)
            )
            or item["units"] != [row["pair_id"] for row in transcript]
            or adaptive_next([row["outcome"] for row in transcript]) not in {"stop", "reject"}
        ):
            raise ValueError("invalid adaptive holdout transcript")
    elif item["units"] != [] or item["transcript"] != [] or item["actual"] is not None:
        raise ValueError("offline evidence has live result fields")


def verify_evidence_object(repo: Path, *, source_commit: str, evidence_commit: str,
                           path: str, blob: str, content_sha256: str,
                           producer: dict[str, Any], subject: dict[str, Any]) -> dict[str, Any]:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != path:
        raise ValueError("evidence path is not normalized")
    validate_evidence_commit(repo, source_commit=source_commit, evidence_commit=evidence_commit)
    listing = _git(repo, "ls-tree", evidence_commit, "--", path).splitlines()
    if len(listing) != 1:
        raise ValueError("evidence commit:path is not exact")
    metadata, listed_path = listing[0].split("\t", 1)
    mode, kind, actual_blob = metadata.split()
    if listed_path != path or mode != "100644" or kind != "blob" or actual_blob != blob:
        raise ValueError("evidence blob does not match commit:path")
    raw = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "blob", f"{evidence_commit}:{path}"],
        check=True, capture_output=True,
    ).stdout
    if sha256_bytes(raw) != content_sha256:
        raise ValueError("evidence content hash mismatch")
    summary = json.loads(raw)
    if summary != {"schema_version": 1, "producer": producer, "subject": subject}:
        raise ValueError("evidence producer or subject mismatch")
    return summary


def derive_coverage(snapshot: dict[str, Any], evidence: dict[str, Any],
                    *, prior: Any = None) -> dict[str, Any]:
    if prior is not None:
        raise ValueError("prior or waived coverage is forbidden")
    _slot_map(evidence, EVIDENCE_SLOTS, "evidence")
    records = sorted((item for item in evidence.values() if item), key=lambda item: item["sequence"])
    receipts = [item["receipt_sha256"] for item in records]
    if len(receipts) != len(set(receipts)):
        raise ValueError("duplicate evidence receipt")
    corpus = evidence["corpus"]["units"] if evidence["corpus"] else []
    holdout = evidence["holdout"]["units"] if evidence["holdout"] else []
    if not set(corpus) <= set(snapshot["corpus"]["cases"]) or not set(holdout) <= set(snapshot["holdout"]["pairs"]):
        raise ValueError("coverage contains unknown identity")
    result = {
        "schema_version": 1, "corpus_cases": corpus, "holdout_pairs": holdout,
        "gates": [slot for slot in EVIDENCE_SLOTS if evidence[slot]],
        "evidence_sha256": receipts,
    }
    result["coverage_sha256"] = canonical_sha256(result)
    return result


def derive_pending(ledger: dict[str, Any]) -> dict[str, Any]:
    evidence, snapshot = ledger["accepted_evidence"], ledger["snapshot"]
    corpus_done = set(evidence["corpus"]["units"]) if evidence["corpus"] else set()
    holdout_pairs = sorted(snapshot["holdout"]["pairs"])
    frontier = [] if evidence["holdout"] else holdout_pairs[:1]
    slots = {
        "executor_pilot": evidence["executor"], "corpus": evidence["corpus"],
        "holdout": evidence["holdout"], "receipt": evidence["receipt"],
        "review": evidence["review"], "isolated_install": evidence["isolated_install"],
    }
    return {
        "gates": [gate for gate in PENDING_GATES if not slots[gate]],
        "corpus_cases": [case for case in sorted(snapshot["corpus"]["cases"]) if case not in corpus_done],
        "holdout_pairs": frontier,
    }


def derive_failed(ledger: dict[str, Any]) -> list[str]:
    evidence = ledger["accepted_evidence"]["holdout"]
    if not evidence:
        return []
    outcomes = [row["outcome"] for row in evidence["transcript"]]
    return ["holdout"] if adaptive_next(outcomes) == "reject" else []


def _empty_lifecycle(ledger: dict[str, Any]) -> bool:
    null_fields = ("planned_impact", "receipt_head", "freeze", "certification")
    slot_fields = ("planned_invocations", "cost", "authorities",
                   "accepted_evidence")
    return (
        all(ledger[field] is None for field in null_fields)
        and all(value is None for field in slot_fields for value in ledger[field].values())
        and ledger["coverage"] == {}
    )


def validate_ledger(ledger: dict[str, Any], *, repo: Path | None = None) -> None:
    validate_named(CONTRACTS, "ledger", ledger)
    snapshot = ledger["snapshot"]
    validate_snapshot(snapshot)
    plans = _slot_map(ledger["planned_invocations"], LIVE_SLOTS, "invocation")
    cost = _slot_map(ledger["cost"], LIVE_SLOTS, "cost")
    authorities = _slot_map(ledger["authorities"], LIVE_SLOTS, "authority")
    evidence = _slot_map(ledger["accepted_evidence"], EVIDENCE_SLOTS, "evidence")
    anchor, impact = ledger["source_anchor"], ledger["planned_impact"]
    if anchor is None:
        if ledger["state"] != "refresh_required" or not _empty_lifecycle(ledger):
            raise ValueError("pre-anchor generation-6 ledger must be null-slot genesis")
        return
    validated = validate_source_anchor(anchor, repo=repo)
    expected = {
        "package_artifact_sha256": snapshot["package"]["artifact_sha256"],
        "package_semantic_sha256": snapshot["package"]["semantic_sha256"],
        "engine_manifest_sha256": snapshot["engine"]["manifest_sha256"],
        "executor_role_sha256": snapshot["role"]["executor_sha256"],
        "public_baseline_sha256": canonical_sha256(snapshot["public_baseline"]),
    }
    if any(validated[field] != digest for field, digest in expected.items()):
        raise ValueError("source anchor does not match snapshot")
    if impact is None:
        if not _empty_lifecycle({**ledger, "source_anchor": None}):
            raise ValueError("anchored empty state has dependent lifecycle data")
        if ledger["state"] != "refresh_required":
            raise ValueError("anchored empty state must remain refresh_required")
        return
    _validate_planning(ledger)
    records = sorted((item for item in evidence.values() if item), key=lambda item: item["sequence"])
    parent = None
    for sequence, item in enumerate(records):
        slot = item["gate"]
        validate_evidence_record(item, snapshot, impact, plans, authorities, slot=slot)
        if item["sequence"] != sequence or item["parent_receipt_sha256"] != parent:
            raise ValueError("evidence sequence or parent receipt chain is not exact")
        parent = item["receipt_sha256"]
    if records and repo is None:
        raise ValueError("populated evidence requires repository")
    for item in records:
        verify_evidence_object(
            repo, source_commit=anchor["source_commit"], evidence_commit=item["evidence_commit"],
            path=item["path"], blob=item["blob"], content_sha256=item["content_sha256"],
            producer=item["producer"], subject=item["subject"],
        )
    if ledger["receipt_head"] != parent:
        raise ValueError("receipt head does not match exact evidence chain")
    coverage = derive_coverage(snapshot, evidence)
    if ledger["coverage"] != (coverage if records else {}):
        raise ValueError("coverage is not exactly derived once")
    freeze = ledger["freeze"]
    prerequisites = ("executor", "corpus", "holdout", "receipt")
    if freeze is not None:
        if any(evidence[slot] is None for slot in prerequisites):
            raise ValueError("invalid candidate freeze")
        first = sorted((evidence[slot] for slot in prerequisites), key=lambda item: item["sequence"])
        payload = {
            "schema_version": 1,
            "source_anchor_sha256": canonical_sha256(anchor),
            "receipt_head": first[-1]["receipt_sha256"],
            "coverage_sha256": coverage["coverage_sha256"],
        }
        payload["freeze_sha256"] = canonical_sha256(payload)
        if freeze != payload or derive_failed(ledger):
            raise ValueError("invalid candidate freeze")
    if evidence["review"] and freeze is None:
        raise ValueError("review evidence requires freeze")
    if evidence["isolated_install"] and evidence["review"] is None:
        raise ValueError("install evidence requires review")
    certification = ledger["certification"]
    if certification is None:
        if ledger["state"] != "refresh_required":
            raise ValueError("certified state requires certification")
        return
    payload = {
        "schema_version": 1,
        "source_anchor_sha256": canonical_sha256(anchor),
        "snapshot_sha256": canonical_sha256(snapshot),
        "authorities": {gate: authorities[gate]["authority_sha256"] for gate in LIVE_SLOTS},
        "executor_evidence_sha256": evidence["executor"]["receipt_sha256"],
        "evidence_receipts": [item["receipt_sha256"] for item in records],
        "coverage_sha256": coverage["coverage_sha256"],
        "freeze_sha256": freeze["freeze_sha256"],
        "receipt_head": parent,
    }
    payload["certification_sha256"] = canonical_sha256(payload)
    if (
        ledger["state"] != "certified"
        or any(value is None for value in authorities.values())
        or any(value is None for value in evidence.values())
        or derive_pending(ledger)["gates"]
        or derive_failed(ledger)
        or certification != payload
    ):
        raise ValueError("certification does not bind exact completed DAG")


def validate_prior_git_successor(repo: Path, path: str, after: dict[str, Any]) -> None:
    before = json.loads(_git(repo, "show", f"HEAD:{path}"))
    if before == after:
        return
    validate_successor(before, after, repo=repo)
    if before["source_anchor"] != after["source_anchor"] and (
        after["source_anchor"]["source_commit"] != _git(repo, "rev-parse", "HEAD^{commit}")
    ):
        raise ValueError("release reanchor must bind current HEAD")


def replay_planned_lifecycle(ledger: dict[str, Any], *, repo: Path | None = None) -> dict[str, Any]:
    validate_ledger(ledger, repo=repo)
    if ledger["planned_impact"] is None:
        raise ValueError("refresh-required genesis has no persisted planned impact")
    return dict(ledger["planned_impact"])


def load_ledger(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    repo = path.resolve().parents[2]
    validate_ledger(value, repo=repo)
    validate_prior_git_successor(
        repo, path.resolve().relative_to(repo).as_posix(), value
    )
    return value


def ledger_sha256(ledger: dict[str, Any], *, repo: Path | None = None) -> str:
    validate_ledger(ledger, repo=repo)
    return canonical_sha256(ledger)
