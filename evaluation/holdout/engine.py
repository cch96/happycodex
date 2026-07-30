#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from typing import Any, Callable

from evaluation.core.identity import (
    canonical_sha256,
    invocation_profile,
    sha256_bytes,
)
from evaluation.core.receipt import sanitized_case_receipt, write_new_json
from evaluation.core.schema import CONTRACTS, validate_named
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
    compare_pair,
    decision_metrics,
)


ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_ROOT = ROOT / "evaluation" / "holdouts"
MANIFEST_PATH = HOLDOUT_ROOT / "manifest.json"
HOLDOUT_ARM_WORKERS = 2


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def adaptive_frontier(pair_ids: list[str], outcomes: list[str]) -> list[str]:
    action = adaptive_next(outcomes)
    index = len(outcomes)
    if action in {"run_first", "run_second", "run_third"} and index < len(pair_ids):
        return [pair_ids[index]]
    return []


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    path = path.resolve()
    holdout_root = path.parent
    repo_root = holdout_root.parents[1]
    raw = json.loads(path.read_text(encoding="utf-8"))
    validate_named(CONTRACTS, "holdout_manifest", raw)
    loaded: list[dict[str, Any]] = []
    pair_ids: set[str] = set()
    case_ids: set[str] = set()
    for raw_pair in raw["pairs"]:
        pair_id = raw_pair["id"]
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
    return {"schema_version": 1, "manifest_sha256": file_sha256(path),
            "pairs": loaded}


def _validate_pair_launch(
    launch: dict[str, Any],
    *,
    pair: dict[str, Any],
    candidate: Path,
    public: Path,
    model: str,
    effort: str,
    timeout: int,
) -> None:
    from evaluation.live import validate_launch

    launch = validate_launch(launch, unit=pair["id"])
    if (
        launch["gate"] != "holdout"
        or launch["invocation"]["model"] != model
        or launch["invocation"]["effort"] != effort
        or launch["invocation"]["timeout_ms"] != timeout * 1000
        or launch["invocation"]["arm"] != "blinded-pair"
    ):
        raise ValueError("launch does not bind holdout invocation")
    if pair["case"]["id"] != f"holdout-{pair['id']}":
        raise ValueError("holdout pair identity is invalid")
    for plugin in (candidate, public):
        if not plugin.resolve().is_dir():
            raise ValueError("holdout plugin must be an existing directory")
    invocation_profile(
        model=model,
        effort=effort,
        timeout_seconds=timeout,
        arm="blinded-pair",
    )


def _evaluate_pair_arms(
    evaluate_alias: Callable[[str], dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Evaluate each arm once; exceptions abort, completed failures remain evidence."""
    with ThreadPoolExecutor(max_workers=HOLDOUT_ARM_WORKERS) as executor:
        results = executor.map(evaluate_alias, ALIASES)
        return dict(zip(ALIASES, results, strict=True))


def run_pair(
    pair: dict[str, Any],
    *,
    candidate: Path,
    public: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    launch: dict[str, Any],
    claim_root: Path,
    evaluator: Callable[..., dict[str, Any]] = corpus_engine.evaluate_case,
) -> dict[str, Any]:
    _validate_pair_launch(
        launch,
        pair=pair,
        candidate=candidate,
        public=public,
        model=model,
        effort=effort,
        timeout=timeout,
    )
    pair_output = output / pair["id"]
    if pair_output.is_symlink() or not pair_output.is_dir():
        raise ValueError("reserved holdout launch output is not a real directory")
    sealed = seal_mapping(pair["id"])
    commitment_sha = write_new_json(
        pair_output / "01-mapping-commitment.json", sealed.public_receipt()
    )
    plugins = {"candidate": candidate, "public-0.2": public}
    inverse = {alias: arm for arm, alias in sealed._mapping.items()}

    def evaluate_alias(alias: str) -> dict[str, Any]:
        arm = inverse[alias]
        return evaluator(
            pair["case"],
            plugin=plugins[arm],
            output=pair_output / "raw" / alias,
            model=model,
            effort=effort,
            timeout=timeout,
            arm=arm,
            launch=launch,
            claim_root=claim_root,
            launch_unit=pair["id"],
        )

    raw = _evaluate_pair_arms(evaluate_alias)
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
        "engine_generation": "0.6.5",
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
    if requested is None or not requested.is_absolute():
        raise ValueError("an explicit absolute raw output path is required")
    if requested.is_symlink() or requested.exists():
        raise ValueError("raw holdout output path must be absent and not a symlink")
    parent = requested.parent
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("raw holdout output parent must be an existing real directory")
    output = requested.resolve()
    for protected in (ROOT.resolve(), *(plugin.resolve() for plugin in plugins)):
        if output == protected or output.is_relative_to(protected):
            raise ValueError("raw holdout output must stay outside source and plugins")
    return output


def run_holdouts(
    *,
    candidate: Path,
    public: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    launches: dict[str, dict[str, Any]],
    claim_root: Path,
) -> dict[str, Any]:
    from evaluation import live

    if not isinstance(launches, dict) or not launches:
        raise ValueError("authorized holdout run requires launches")
    prepared = {
        key: live.validate_launch(value, unit=key)
        for key, value in launches.items()
    }
    manifest = load_manifest()
    output = resolve_output(output, candidate, public)
    pair_ids = [pair["id"] for pair in manifest["pairs"]]
    if set(prepared) != set(pair_ids):
        raise ValueError("launch units do not equal holdout pairs")
    for pair_id in pair_ids:
        launch = live.validate_launch(
            prepared[pair_id],
            unit=pair_id,
            timeout_ms=timeout * 1000,
            output=output / pair_id,
        )
        if (
            launch["gate"] != "holdout"
            or launch["invocation"]["model"] != model
            or launch["invocation"]["effort"] != effort
            or launch["invocation"]["arm"] != "blinded-pair"
        ):
            raise ValueError("launch does not bind holdout invocation")
    corpus_engine.provider_transport_schema(corpus_engine.OUTPUT_SCHEMA)
    corpus_engine.codex_identity()
    for plugin in (candidate, public):
        corpus_engine.package_identities(plugin)
    receipts = []
    outcomes = []
    by_id = {pair["id"]: pair for pair in manifest["pairs"]}
    while frontier := adaptive_frontier(pair_ids, outcomes):
        pair = by_id[frontier[0]]
        launch = prepared[pair["id"]]
        live.reserve_launch(launch, claim_root)
        live.consume_action(launch, claim_root)
        receipt = run_pair(
            pair,
            candidate=candidate,
            public=public,
            output=output,
            model=model,
            effort=effort,
            timeout=timeout,
            launch=launch,
            claim_root=claim_root,
        )
        usage = {
            "model_calls": sum(
                len(arm["usage_phases"]) for arm in receipt["arms"].values()
            ),
            "uncached_input_tokens": sum(
                arm["uncached_input_tokens"] for arm in receipt["arms"].values()
            ),
            "output_tokens": sum(
                arm["usage"]["output_tokens"] for arm in receipt["arms"].values()
            ),
            "wall_milliseconds": round(
                max(arm["elapsed_seconds"] for arm in receipt["arms"].values())
                * 1000
            ),
        }
        effect_result = {
            "schema_generation": 7,
            "action_key": launch["action_key"],
            "launch_key": launch["launch_key"],
            "unit": launch["unit"],
            "status": (
                "failed" if receipt["outcome"] == "regression" else "succeeded"
            ),
            "effect": "provider_reached",
            "output_sha256": canonical_sha256(receipt),
            "usage": usage,
        }
        effect_result["result_sha256"] = canonical_sha256(effect_result)
        live.write_launch_result(launch, claim_root, effect_result)
        receipts.append(receipt)
        outcomes.append(receipt["outcome"])
    return {
        "schema_version": 1,
        "engine_generation": "0.6.5",
        "manifest_sha256": manifest["manifest_sha256"],
        "pairs": [receipt["id"] for receipt in receipts],
        "outcomes": outcomes,
        "receipts": [canonical_sha256(receipt) for receipt in receipts],
    }


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
                    "invocation_profile": invocation_profile(
                        model=args.model,
                        effort=args.effort,
                        timeout_seconds=args.timeout,
                        arm="blinded-pair",
                    ),
                    "effects": {
                        "launches_created": 0,
                        "actions_consumed": 0,
                        "fixtures_created": 0,
                        "outputs_created": 0,
                        "receipts_created": 0,
                        "workspaces_created": 0,
                        "subprocesses": 0,
                        "model_calls": 0,
                        "network_calls": 0,
                    },
                },
                indent=2,
            )
        )
        return 0
    raise SystemExit("live holdout execution is available only through evaluation.cli")


def run_authorized(
    args: Any,
    launches: dict[str, dict[str, Any]],
    claim_root: Path,
) -> int:
    if args.public is None:
        raise ValueError("exact public-0.2 package path is required")
    result = run_holdouts(
        candidate=args.candidate,
        public=args.public,
        output=args.output,
        model=args.model,
        effort=args.effort,
        timeout=args.timeout,
        launches=launches,
        claim_root=claim_root,
    )
    print(json.dumps(result, sort_keys=True))
    return 0
