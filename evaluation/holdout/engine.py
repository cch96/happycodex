#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import tempfile
from typing import Any, Callable

from evaluation.core.identity import (
    canonical_sha256,
    engine_inventory,
    package_identities,
    package_manifest_sha256,
    sha256_bytes,
    toolchain_identity,
)
from evaluation.core.receipt import sanitized_case_receipt, write_new_json
from evaluation.corpus import engine as corpus_engine
from evaluation.holdout.blind import (
    ACTUAL_ARMS,
    ALIASES,
    blind_view,
    freeze_blind_decision,
    reveal_mapping,
    seal_mapping,
    validate_reveal,
)
from evaluation.holdout.compare import (
    adaptive_next,
    aggregate_quality,
    compare_pair,
    cost_gate,
    decision_metrics,
    sum_metrics,
)


ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_ROOT = ROOT / "evaluation" / "holdouts"
MANIFEST_PATH = HOLDOUT_ROOT / "manifest.json"


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    path = path.resolve()
    holdout_root = path.parent
    repo_root = holdout_root.parents[1]
    raw = json.loads(path.read_text(encoding="utf-8"))
    if set(raw) != {"schema_version", "pairs"} or raw["schema_version"] != 1:
        raise ValueError("invalid holdout manifest envelope")
    pairs = raw["pairs"]
    if not isinstance(pairs, list) or len(pairs) != 3:
        raise ValueError("holdout manifest must freeze exactly three pairs")
    loaded: list[dict[str, Any]] = []
    pair_ids: set[str] = set()
    case_ids: set[str] = set()
    expected_fields = {
        "id",
        "case_path",
        "outside_diff_boundary",
        "oracle_kind",
    }
    for raw_pair in pairs:
        if not isinstance(raw_pair, dict) or set(raw_pair) != expected_fields:
            raise ValueError("invalid holdout pair envelope")
        pair_id = raw_pair["id"]
        if not isinstance(pair_id, str) or not re.fullmatch(r"[a-z0-9-]+", pair_id):
            raise ValueError(f"invalid holdout pair id: {pair_id!r}")
        if pair_id in pair_ids:
            raise ValueError(f"duplicate holdout pair id: {pair_id}")
        pair_ids.add(pair_id)
        relative = Path(raw_pair["case_path"])
        case_path = (repo_root / relative).resolve()
        if (
            relative.is_absolute()
            or not case_path.is_relative_to(holdout_root)
            or case_path.suffix != ".json"
            or not case_path.is_file()
        ):
            raise ValueError(f"unsafe holdout case path: {relative}")
        case = json.loads(case_path.read_text(encoding="utf-8"))
        corpus_engine.validate_case(case, case_path)
        if case["id"] in case_ids:
            raise ValueError(f"duplicate holdout case id: {case['id']}")
        case_ids.add(case["id"])
        if not isinstance(raw_pair["outside_diff_boundary"], bool):
            raise ValueError(f"invalid boundary marker: {pair_id}")
        if raw_pair["oracle_kind"] not in {"mechanical", "behavioral"}:
            raise ValueError(f"invalid oracle kind: {pair_id}")
        loaded.append(
            {
                **raw_pair,
                "case_path": case_path,
                "case": case,
                "case_sha256": file_sha256(case_path),
            }
        )
    if not any(pair["outside_diff_boundary"] for pair in loaded[:2]):
        raise ValueError("first two holdouts need an outside-diff boundary")
    if not any(
        pair["oracle_kind"] in {"mechanical", "behavioral"} for pair in loaded[:2]
    ):
        raise ValueError("first two holdouts need a mechanical or behavioral oracle")
    return {
        "schema_version": 1,
        "manifest_sha256": file_sha256(path),
        "pairs": loaded,
    }


def run_pair(
    pair: dict[str, Any],
    *,
    candidate: Path,
    public: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    evaluator: Callable[..., dict[str, Any]] = corpus_engine.evaluate_case,
) -> dict[str, Any]:
    pair_output = output / pair["id"]
    pair_output.mkdir(parents=True, exist_ok=False)
    sealed = seal_mapping(pair["id"])
    commitment_sha = write_new_json(
        pair_output / "01-mapping-commitment.json", sealed.public_receipt()
    )
    plugins = {"candidate": candidate, "public-0.2": public}
    inverse = {alias: arm for arm, alias in sealed._mapping.items()}
    raw: dict[str, dict[str, Any]] = {}
    for alias in ALIASES:
        arm = inverse[alias]
        raw[alias] = evaluator(
            pair["case"],
            plugin=plugins[arm],
            output=pair_output / "raw" / alias,
            model=model,
            effort=effort,
            timeout=timeout,
            arm=arm,
        )
    views = {alias: blind_view(raw[alias]) for alias in ALIASES}
    decision = freeze_blind_decision(views)
    decision_sha = write_new_json(pair_output / "02-pre-reveal-decision.json", decision)
    reveal = reveal_mapping(
        sealed, pre_reveal_decision_sha256=canonical_sha256(decision)
    )
    validate_reveal(reveal, decision)
    reveal_sha = write_new_json(pair_output / "03-mapping-reveal.json", reveal)
    outcome = compare_pair(decision, reveal)
    metrics = decision_metrics(decision, reveal)
    sanitized: dict[str, Any] = {}
    for arm in ACTUAL_ARMS:
        alias = reveal["mapping"][arm]
        metadata_path = (
            pair_output / "raw" / alias / pair["case"]["id"] / "metadata.json"
        )
        sanitized[arm] = sanitized_case_receipt(
            raw[alias], metadata_sha256=file_sha256(metadata_path)
        )
    receipt = {
        "schema_version": 1,
        "engine_generation": "0.4",
        "id": pair["id"],
        "case_id": pair["case"]["id"],
        "case_sha256": pair["case_sha256"],
        "outside_diff_boundary": pair["outside_diff_boundary"],
        "oracle_kind": pair["oracle_kind"],
        "mapping_commitment_file_sha256": commitment_sha,
        "pre_reveal_decision_file_sha256": decision_sha,
        "mapping_reveal_file_sha256": reveal_sha,
        "pre_reveal_decision_sha256": canonical_sha256(decision),
        "mapping_commitment_sha256": reveal["mapping_commitment_sha256"],
        "outcome": outcome,
        "metrics": metrics,
        "arms": sanitized,
    }
    write_new_json(pair_output / "04-pair-receipt.json", receipt)
    return receipt


def resolve_output(requested: Path | None, *plugins: Path) -> Path:
    output = (
        requested.expanduser().resolve()
        if requested is not None
        else Path(tempfile.mkdtemp(prefix="happycodex-holdouts-")).resolve()
    )
    for protected in (ROOT.resolve(), *(plugin.resolve() for plugin in plugins)):
        if output == protected or output.is_relative_to(protected):
            raise ValueError("raw holdout output must stay outside source and plugins")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("raw holdout output directory must be empty")
    return output


def run_holdouts(
    *,
    candidate: Path,
    public: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    authorization: Any,
) -> dict[str, Any]:
    from evaluation.core.ledger import AuthorizedInvocation

    if not isinstance(authorization, AuthorizedInvocation):
        raise ValueError("live holdout execution requires a validated capability")
    descriptor = authorization.descriptor()
    if descriptor.get("command") != "holdout":
        raise ValueError("invalid holdout execution capability")
    manifest = load_manifest()
    pair_ids = [pair["id"] for pair in manifest["pairs"]]
    if (
        descriptor.get("pairs") != sorted(pair_ids)
        or descriptor.get("model") != model
        or descriptor.get("effort") != effort
        or descriptor.get("timeout_seconds") != timeout
    ):
        raise ValueError("holdout execution does not match the validated capability")
    candidate_manifest = package_manifest_sha256(candidate)
    public_manifest = package_manifest_sha256(public)
    if public_manifest != corpus_engine.EXPECTED_PUBLIC_02_PACKAGE_MANIFEST_SHA256:
        raise ValueError(
            "public-0.2 package manifest mismatch: "
            f"got {public_manifest}, expected "
            f"{corpus_engine.EXPECTED_PUBLIC_02_PACKAGE_MANIFEST_SHA256}"
        )
    package_manifests = {
        "candidate": candidate_manifest,
        "public-0.2": public_manifest,
    }
    package_identity = {
        "candidate": package_identities(candidate),
        "public-0.2": package_identities(public),
    }
    if package_identity != {
        "candidate": {
            "semantic_sha256": descriptor.get("candidate_semantic_sha256"),
            "artifact_sha256": descriptor.get("candidate_artifact_sha256"),
        },
        "public-0.2": {
            "semantic_sha256": descriptor.get("public_semantic_sha256"),
            "artifact_sha256": descriptor.get("public_artifact_sha256"),
        },
    }:
        raise ValueError("holdout packages do not match the validated capability")
    run_receipt = {
        "schema_version": 1,
        "engine_generation": "0.4",
        "impact_token": authorization.impact_token,
        "live_authority_sha256": authorization.authority_sha256,
        "manifest_sha256": manifest["manifest_sha256"],
        "identities": {
            "engine": engine_inventory(ROOT),
            "packages": package_identity,
            "toolchain": toolchain_identity(),
        },
        "model": model,
        "effort": effort,
        "timeout_seconds": timeout,
        "pair_ids": pair_ids,
        "case_sha256": {pair["id"]: pair["case_sha256"] for pair in manifest["pairs"]},
    }
    write_new_json(output / "00-run-receipt.json", run_receipt)
    receipts: list[dict[str, Any]] = []
    outcomes: list[str] = []
    while True:
        action = adaptive_next(outcomes)
        if action in {"reject", "stop"}:
            break
        pair = manifest["pairs"][len(outcomes)]
        receipt = run_pair(
            pair,
            candidate=candidate,
            public=public,
            output=output,
            model=model,
            effort=effort,
            timeout=timeout,
        )
        receipts.append(receipt)
        outcomes.append(receipt["outcome"])
    if {
        arm: package_manifest_sha256(path)
        for arm, path in (("candidate", candidate), ("public-0.2", public))
    } != package_manifests:
        raise RuntimeError("evaluated package changed during holdouts")
    quality = aggregate_quality(outcomes)
    aggregate = {
        arm: sum_metrics([receipt["metrics"][arm] for receipt in receipts])
        for arm in ACTUAL_ARMS
    }
    gate = cost_gate(aggregate["candidate"], aggregate["public-0.2"], quality=quality)
    summary = {
        "schema_version": 1,
        "engine_generation": "0.4",
        "run_receipt_sha256": file_sha256(output / "00-run-receipt.json"),
        "adaptive_history": outcomes,
        "adaptive_terminal_action": adaptive_next(outcomes),
        "pairs_run": len(receipts),
        "pair_receipts": receipts,
        "cost_gate": gate,
    }
    write_new_json(output / "summary.json", summary)
    return summary


def run_command(args: Any) -> int:
    manifest = load_manifest()
    if args.list:
        for pair in manifest["pairs"]:
            print(pair["id"])
        return 0
    if args.dry_run:
        print(
            json.dumps(
                {
                    "manifest_sha256": manifest["manifest_sha256"],
                    "pairs": [
                        {
                            key: pair[key]
                            for key in (
                                "id",
                                "case_sha256",
                                "outside_diff_boundary",
                                "oracle_kind",
                            )
                        }
                        for pair in manifest["pairs"]
                    ],
                    "adaptive_policy": [
                        "first regression rejects",
                        "otherwise second pair is mandatory",
                        "split or uncertainty runs the third pair",
                    ],
                },
                indent=2,
            )
        )
        return 0
    raise SystemExit("live holdout execution is available only through evaluation.cli")


def run_authorized(args: Any, authorization: Any) -> int:
    from evaluation.core.ledger import AuthorizedInvocation

    if not isinstance(authorization, AuthorizedInvocation):
        raise SystemExit("live holdout execution requires a validated capability")
    if args.public is None:
        raise SystemExit("--public is required for a live paired run")
    candidate = args.candidate.expanduser().resolve()
    public = args.public.expanduser().resolve()
    try:
        output = resolve_output(args.output, candidate, public)
        summary = run_holdouts(
            candidate=candidate,
            public=public,
            output=output,
            model=args.model,
            effort=args.effort,
            timeout=args.timeout,
            authorization=authorization,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(summary, indent=2))
    return 0 if summary["cost_gate"]["release_permitted"] else 1
