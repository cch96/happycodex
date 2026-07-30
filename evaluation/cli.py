from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import stat
from typing import Any

from evaluation import live
from evaluation.core.identity import (
    PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
    PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
    canonical_sha256,
    codex_identity,
    engine_inventory,
    invocation_profile,
    package_identities,
    sha256_bytes,
)
from evaluation.core.impact import (
    DEFAULT_EFFORT,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    build_snapshot,
)
from evaluation.core.ledger import (
    GATE_ORDER,
    MODEL_GATES,
    append_record,
    apply_record,
    derive_failed,
    derive_pending,
    derive_receipt_tip,
    ledger_sha256,
    load_ledger,
    validate_gate_plan,
    validate_gate_receipt,
    validate_ledger,
)


ROOT = Path(__file__).resolve().parents[1]


def _write_private_json(path: Path, value: dict[str, Any]) -> None:
    path = path.absolute()
    parent = path.parent
    if (
        not path.is_absolute()
        or path.exists()
        or path.is_symlink()
        or parent.is_symlink()
        or not parent.is_dir()
        or stat.S_IMODE(parent.stat().st_mode) != 0o700
    ):
        raise ValueError("record output must be absent beneath a private directory")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        payload = (
            json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode()
            + b"\n"
        )
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _utc_after(previous: str | None = None) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if previous is not None:
        prior = datetime.strptime(
            previous,
            "%Y-%m-%dT%H:%M:%SZ",
        ).replace(tzinfo=timezone.utc)
        now = max(now, prior + timedelta(seconds=1))
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def verify_command() -> int:
    ledger, current, _impact = live.load_state()
    inventory = engine_inventory(ROOT)
    derived = live.derived_release_state(ledger, repo=ROOT)
    payload = {
        "schema_version": 1,
        "status": "ok",
        "ledger_state": derived["state"],
        "ledger_sha256": ledger_sha256(ledger, repo=ROOT),
        "snapshot_sha256": canonical_sha256(current),
        "engine_manifest_sha256": inventory["manifest_sha256"],
        "pending_gates": derived["pending_gates"],
        "coverage": derived["coverage"],
        "receipt_tip": derived["receipt_tip"],
        "freeze_eligibility": derived["freeze_eligibility"],
        "failed": derived["failed"],
        "certified": derived["certified"],
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def impact_command(public: Path | None = None) -> int:
    ledger, current, impact = live.load_state()
    if public is not None and package_identities(public) != {
        "artifact_sha256": PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
        "semantic_sha256": PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
    }:
        raise ValueError("public path does not equal frozen public-0.2 archive")
    print(
        json.dumps(
            {
                "snapshot": current,
                "impact": impact,
                "candidate": ledger["candidate"],
                "plans": ledger["plans"],
                "derived": live.derived_release_state(ledger, repo=ROOT),
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 2 if ledger["candidate"] is None else 0


def request_command(args: argparse.Namespace) -> int:
    """Build, but never persist or execute, the next exact GatePlan."""
    repo = args.repo.resolve()
    ledger = load_ledger(repo / "evaluation" / "results" / "current.json")
    validate_ledger(ledger, repo=repo)
    if ledger["candidate"] is None or derive_failed(ledger):
        raise ValueError("GatePlan request requires an active clean candidate")
    if len(ledger["plans"]) != len(ledger["receipts"]):
        raise ValueError("the current GatePlan needs a receipt first")
    pending = derive_pending(ledger)["gates"]
    if not pending or args.gate != pending[0]:
        raise ValueError("request is not for the next pending gate")
    snapshot = build_snapshot(repo)
    candidate = ledger["candidate"]
    output = args.output.absolute()
    cost = {
        "model_calls": args.model_calls,
        "uncached_input_tokens": args.uncached_input_tokens,
        "output_tokens": args.output_tokens,
        "wall_milliseconds": args.wall_milliseconds,
    }
    public = None
    public_identity = None
    if args.gate in MODEL_GATES:
        from evaluation.corpus import engine as corpus_engine

        codex = codex_identity()
        corpus_engine.provider_transport_schema(corpus_engine.OUTPUT_SCHEMA)
        if package_identities(repo) != {
            "artifact_sha256": candidate["package_artifact_sha256"],
            "semantic_sha256": candidate["package_semantic_sha256"],
        }:
            raise ValueError("candidate package drifted before GatePlan request")
        if args.gate == "holdout":
            from evaluation.holdout import engine as holdout_engine

            if args.public is None:
                raise ValueError("holdout request requires exact public-0.2 path")
            public = args.public.resolve()
            public_identity = package_identities(public)
            if public_identity != {
                "artifact_sha256": PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
                "semantic_sha256": PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
            }:
                raise ValueError("public path does not equal frozen public-0.2 archive")
            holdout_engine.resolve_output(output, repo, public)
        else:
            corpus_engine.resolve_output_path(output, plugin=repo)
        units = {
            "calibration": ["subthreshold-control"],
            "corpus": sorted(snapshot["corpus"]["cases"]),
            "holdout": sorted(snapshot["holdout"]["pairs"]),
        }[args.gate]
        arm = "blinded-pair" if args.gate == "holdout" else "candidate"
        profile = live.model_gate_profile(
            gate=args.gate,
            repo=repo,
            output=output,
            claim_root=args.claim_root,
            model=snapshot["settings"]["model"],
            effort=snapshot["settings"]["effort"],
            timeout_ms=snapshot["settings"]["timeout_seconds"] * 1000,
            arm=arm,
            codex_sha256=codex["sha256"],
            public=public,
        )
        resources = live.model_gate_resource_digests(
            candidate=candidate,
            snapshot=snapshot,
            profile=profile,
            codex=codex,
            public_identity=public_identity,
        )
    else:
        if args.profile is None or not args.unit or not args.resource_sha256:
            raise ValueError(
                "non-model request needs profile, units, and resource digests"
            )
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        units = sorted(args.unit)
        resources = sorted(args.resource_sha256)
    draft = {
        "schema_version": 1,
        "record_type": "GatePlan",
        "candidate_sha256": candidate["candidate_sha256"],
        "snapshot_sha256": canonical_sha256(snapshot),
        "gate": args.gate,
        "created_at": _utc_after(
            ledger["receipts"][-1]["created_at"]
            if ledger["receipts"]
            else candidate["created_at"]
        ),
        "profile": profile,
        "cost_ceiling": cost,
        "units": units,
        "resource_digests": resources,
        "output": str(output),
    }
    approval_request = {
        "domain": "happycodex/0.6.5/gate-approval-request",
        **draft,
    }
    request_sha256 = canonical_sha256(approval_request)
    approval_line = (
        f"AUTHORIZE HappyCodex 0.6.5 gate {args.gate} exactly once "
        f"for request {request_sha256}"
    )
    plan = {
        **draft,
        "approval_request_sha256": request_sha256,
        "approval_content_sha256": sha256_bytes(
            (approval_line + "\n").encode()
        ),
    }
    plan["plan_sha256"] = canonical_sha256(plan)
    validate_gate_plan(plan)
    if args.gate in MODEL_GATES:
        live.validate_model_gate_plan(
            plan,
            candidate=candidate,
            snapshot=snapshot,
            repo=repo,
            output=output,
            claim_root=args.claim_root,
            model=snapshot["settings"]["model"],
            effort=snapshot["settings"]["effort"],
            timeout_ms=snapshot["settings"]["timeout_seconds"] * 1000,
            arm="blinded-pair" if args.gate == "holdout" else "candidate",
            codex=codex,
            public=public,
            public_identity=public_identity,
        )
    append_record(ledger, plan, repo=repo)
    _write_private_json(args.record, plan)
    print(
        json.dumps(
            {
                "schema_version": 1,
                "status": "approval_required",
                "gate": args.gate,
                "approval_request": approval_request,
                "approval_request_sha256": request_sha256,
                "approval_line": approval_line,
                "approval_content_sha256": plan[
                    "approval_content_sha256"
                ],
                "plan_sha256": plan["plan_sha256"],
                "record": str(args.record.absolute()),
                "effects": {
                    **_zero_effects(),
                    "outputs_created": 1,
                    "subprocesses": 1 if args.gate in MODEL_GATES else 0,
                },
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
    )
    return 0


def receipt_command(args: argparse.Namespace) -> int:
    """Prepare one GateReceipt from immutable launch results without applying it."""
    repo = args.repo.resolve()
    ledger = load_ledger(repo / "evaluation" / "results" / "current.json")
    validate_ledger(ledger, repo=repo)
    if len(ledger["plans"]) != len(ledger["receipts"]) + 1:
        raise ValueError("receipt preparation requires exactly one open GatePlan")
    plan = ledger["plans"][-1]
    results = live.collect_plan_results(plan, args.claim_root)
    unit_results = [
        {
            "unit": result["unit"],
            "status": result["status"],
            "result_sha256": result["result_sha256"],
        }
        for result in results
    ]
    result = (
        "succeeded"
        if all(item["status"] == "succeeded" for item in unit_results)
        else "failed"
    )
    receipt = {
        "schema_version": 1,
        "record_type": "GateReceipt",
        "candidate_sha256": ledger["candidate"]["candidate_sha256"],
        "plan_sha256": plan["plan_sha256"],
        "gate": plan["gate"],
        "sequence": len(ledger["receipts"]),
        "created_at": _utc_after(plan["created_at"]),
        "evidence_commit": args.evidence_commit,
        "unit_results": unit_results,
        "result": result,
        "output_sha256": canonical_sha256(results),
        "parent_receipt_sha256": derive_receipt_tip(ledger),
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    validate_gate_receipt(receipt)
    append_record(ledger, receipt, repo=repo)
    _write_private_json(args.record, receipt)
    print(
        json.dumps(
            {
                "schema_version": 1,
                "status": "receipt_ready",
                "gate": plan["gate"],
                "result": result,
                "receipt_sha256": receipt["receipt_sha256"],
                "record": str(args.record.absolute()),
                "effects": {
                    **_zero_effects(),
                    "outputs_created": 1,
                    "receipts_created": 1,
                },
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


def apply_command(args: argparse.Namespace) -> int:
    repo = args.repo.resolve()
    record = json.loads(args.record.read_text(encoding="utf-8"))
    after = apply_record(
        repo=repo,
        ledger_path=args.ledger,
        expected_predecessor_sha256=args.expected,
        record=record,
    )
    print(
        json.dumps(
            {
                "schema_version": 1,
                "status": "applied",
                "record_type": record.get("record_type"),
                "ledger_sha256": canonical_sha256(after),
                "derived": live.derived_release_state(after, repo=repo),
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


def _zero_effects() -> dict[str, int]:
    return {
        "launches_created": 0,
        "actions_consumed": 0,
        "fixtures_created": 0,
        "outputs_created": 0,
        "receipts_created": 0,
        "workspaces_created": 0,
        "subprocesses": 0,
        "model_calls": 0,
        "network_calls": 0,
    }


def executor_command(args: argparse.Namespace) -> int:
    if not args.dry_run:
        raise ValueError("live calibration requires Root/Host effect orchestration")
    payload = {
        "schema_generation": 7,
        "command": "executor",
        "dry_run": True,
        "calibration_route": "corpus --calibrate",
        "invocation_profile": invocation_profile(
            model=args.model,
            effort=args.effort,
            timeout_seconds=args.timeout,
            arm=args.arm,
            session_mode="fresh",
        ),
        "effects": _zero_effects(),
        "gate_plan_is_permission": False,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def _gate_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", default=DEFAULT_EFFORT)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m evaluation.cli",
        description="HappyCodex clean-break certification engine",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="validate the release ledger")
    impact = commands.add_parser(
        "impact",
        help="derive full-refresh impact without authorizing effects",
    )
    impact.add_argument("--public", type=Path)
    request = commands.add_parser(
        "request",
        help="prepare the next exact GatePlan and canonical approval line",
    )
    request.add_argument("--repo", type=Path, default=Path.cwd())
    request.add_argument("--gate", choices=GATE_ORDER, required=True)
    request.add_argument("--output", type=Path, required=True)
    request.add_argument("--claim-root", type=Path, required=True)
    request.add_argument("--public", type=Path)
    request.add_argument("--record", type=Path, required=True)
    request.add_argument("--profile", type=Path)
    request.add_argument("--unit", action="append")
    request.add_argument("--resource-sha256", action="append")
    request.add_argument("--model-calls", type=int, required=True)
    request.add_argument("--uncached-input-tokens", type=int, required=True)
    request.add_argument("--output-tokens", type=int, required=True)
    request.add_argument("--wall-milliseconds", type=int, required=True)
    receipt = commands.add_parser(
        "receipt",
        help="prepare a GateReceipt from immutable launch results",
    )
    receipt.add_argument("--repo", type=Path, default=Path.cwd())
    receipt.add_argument("--claim-root", type=Path, required=True)
    receipt.add_argument("--evidence-commit", required=True)
    receipt.add_argument("--record", type=Path, required=True)
    apply = commands.add_parser(
        "apply",
        help="atomically append one complete release record",
    )
    apply.add_argument("--repo", type=Path, default=Path.cwd())
    apply.add_argument(
        "--ledger",
        type=Path,
        default=Path("evaluation/results/current.json"),
    )
    apply.add_argument("--expected", required=True)
    apply.add_argument("--record", type=Path, required=True)

    executor = commands.add_parser(
        "executor",
        help="inspect the calibration route without executing it",
    )
    _gate_options(executor)
    executor.add_argument("--arm", choices=("candidate",), default="candidate")
    executor.add_argument("--plugin", type=Path, default=ROOT)
    executor.add_argument("--output", type=Path)

    corpus = commands.add_parser("corpus", help="inspect or run behavior cases")
    corpus.add_argument("--plugin", type=Path, default=ROOT)
    corpus.add_argument("--case", action="append", dest="cases")
    corpus.add_argument("--list", action="store_true")
    corpus.add_argument("--calibrate", action="store_true")
    _gate_options(corpus)
    corpus.add_argument(
        "--arm",
        choices=("candidate", "public-0.2"),
        default="candidate",
    )
    corpus.add_argument("--output", type=Path)

    holdout = commands.add_parser("holdout", help="inspect or run blinded holdouts")
    holdout.add_argument("--candidate", type=Path, default=ROOT)
    holdout.add_argument("--public", type=Path)
    holdout.add_argument("--output", type=Path)
    holdout.add_argument("--list", action="store_true")
    _gate_options(holdout)
    host_run = commands.add_parser(
        "host-run",
        help="Host-only execution of the next persisted model GatePlan",
    )
    host_run.add_argument("--repo", type=Path, default=Path.cwd())
    host_run.add_argument("--claim-root", type=Path, required=True)
    host_run.add_argument("--public", type=Path)
    host_run.add_argument("--approval-content", required=True)
    host_run.add_argument("--infrastructure-generation")
    return parser


def run_authorized(
    args: argparse.Namespace,
    launches: dict[str, dict[str, Any]],
    claim_root: Path,
    capability: object,
) -> int:
    """Host-only dispatch; validated content is not provenance or permission."""
    if args.command in {"executor", "corpus"}:
        repo = args.plugin.resolve()
    elif args.command == "holdout":
        repo = args.candidate.resolve()
    else:
        raise ValueError("authorized dispatch requires a model-reaching gate")
    ledger = load_ledger(repo / "evaluation" / "results" / "current.json")
    validate_ledger(ledger, repo=repo)
    if ledger["candidate"] is None or derive_failed(ledger):
        raise ValueError("authorized dispatch requires an active clean candidate")
    gate = (
        "calibration"
        if args.command == "executor"
        or (args.command == "corpus" and getattr(args, "calibrate", False))
        else args.command
    )
    pending = derive_pending(ledger)["gates"]
    if not pending or gate != pending[0]:
        raise ValueError("authorized dispatch is not the next pending gate")
    plan = next(
        (item for item in ledger["plans"] if item["gate"] == gate),
        None,
    )
    if plan is None:
        raise ValueError("authorized dispatch has no persisted GatePlan")
    live.validate_capability(capability, plan=plan)
    if set(launches) != set(plan["units"]):
        raise ValueError("launches do not equal the persisted GatePlan")
    launches = {
        unit: live.validate_launch(
            launches[unit],
            plan=plan,
            unit=unit,
        )
        for unit in plan["units"]
    }
    snapshot = build_snapshot(repo)
    codex = codex_identity()
    public = None
    public_identity = None
    if gate == "holdout":
        if args.public is None:
            raise ValueError("exact public-0.2 package path is required")
        public = args.public.resolve()
        public_identity = package_identities(public)
        if public_identity != {
            "artifact_sha256": PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
            "semantic_sha256": PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
        }:
            raise ValueError("public path does not equal frozen public-0.2 archive")
    live.validate_model_gate_plan(
        plan,
        candidate=ledger["candidate"],
        snapshot=snapshot,
        repo=repo,
        output=args.output,
        claim_root=claim_root,
        model=args.model,
        effort=args.effort,
        timeout_ms=args.timeout * 1000,
        arm="blinded-pair" if gate == "holdout" else args.arm,
        codex=codex,
        public=public,
        public_identity=public_identity,
    )

    if gate in {"calibration", "corpus"}:
        from evaluation.corpus import engine as corpus_engine

        if gate == "calibration":
            args.cases = ["subthreshold-control"]
            args.calibrate = True
        return corpus_engine.run_authorized(
            args,
            launches,
            claim_root,
            capability,
        )
    if gate == "holdout":
        from evaluation.holdout import engine as holdout_engine

        return holdout_engine.run_authorized(
            args,
            launches,
            claim_root,
            capability,
        )
    raise ValueError("authorized dispatch requires a model-reaching gate")


def host_run_command(args: argparse.Namespace) -> int:
    """Host adapter: mint one process-local capability and dispatch its plan."""
    repo = args.repo.resolve()
    ledger = load_ledger(repo / "evaluation" / "results" / "current.json")
    validate_ledger(ledger, repo=repo)
    pending = derive_pending(ledger)["gates"]
    if not pending or pending[0] not in MODEL_GATES:
        raise ValueError("next pending gate is not model-reaching")
    gate = pending[0]
    plan = next(
        (item for item in ledger["plans"] if item["gate"] == gate),
        None,
    )
    if plan is None:
        raise ValueError("model gate has no persisted GatePlan")
    capability = live.mint_host_capability(plan, args.approval_content)
    launches = {
        unit: live.build_launch(
            plan,
            unit,
            infrastructure_generation=args.infrastructure_generation,
        )
        for unit in plan["units"]
    }
    profile = plan["profile"]
    common = {
        "model": profile["model"],
        "effort": profile["effort"],
        "timeout": profile["timeout_ms"] // 1000,
        "output": Path(plan["output"]),
    }
    if gate in {"calibration", "corpus"}:
        dispatched = argparse.Namespace(
            command="corpus",
            plugin=repo,
            cases=(
                ["subthreshold-control"]
                if gate == "calibration"
                else list(plan["units"])
            ),
            calibrate=gate == "calibration",
            arm=profile["arm"],
            **common,
        )
    else:
        if args.public is None:
            raise ValueError("holdout run requires exact public-0.2 path")
        dispatched = argparse.Namespace(
            command="holdout",
            candidate=repo,
            public=args.public.resolve(),
            **common,
        )
    return run_authorized(
        dispatched,
        launches,
        args.claim_root,
        capability,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            return verify_command()
        if args.command == "impact":
            return impact_command(args.public)
        if args.command == "request":
            return request_command(args)
        if args.command == "receipt":
            return receipt_command(args)
        if args.command == "apply":
            return apply_command(args)
        if args.command == "executor":
            return executor_command(args)
        if args.command in {"corpus", "holdout"}:
            if args.list or args.dry_run:
                from evaluation.corpus import engine as corpus_engine
                from evaluation.holdout import engine as holdout_engine

                return {
                    "corpus": corpus_engine.run_command,
                    "holdout": holdout_engine.run_command,
                }[args.command](args)
            raise ValueError(
                "live execution requires Root/Host launch orchestration"
            )
        if args.command == "host-run":
            return host_run_command(args)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
