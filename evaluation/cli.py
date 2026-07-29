from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluation import live
from evaluation.core.identity import (
    canonical_sha256,
    engine_inventory,
    invocation_profile,
)
from evaluation.core.impact import DEFAULT_EFFORT, DEFAULT_MODEL, DEFAULT_TIMEOUT
from evaluation.core.ledger import ledger_sha256


ROOT = Path(__file__).resolve().parents[1]


def verify_command() -> int:
    ledger, current, impact = live.load_state()
    inventory = engine_inventory(ROOT)
    payload = {
        "schema_version": 1,
        "status": "ok",
        "ledger_state": ledger["state"],
        "ledger_sha256": ledger_sha256(ledger, repo=ROOT),
        "snapshot_sha256": canonical_sha256(current),
        "engine_manifest_sha256": inventory["manifest_sha256"],
        "pending_gates": impact["gates"],
        "authorities_persisted": {
            gate: authority is not None
            for gate, authority in ledger["authorities"].items()
        },
        "certified": ledger["state"] == "certified",
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def impact_command(public: Path | None = None) -> int:
    del public
    live.load_state()
    raise ValueError(
        "generation-6 cost envelope and exact gate invocations are not persisted"
    )


def executor_command(args: argparse.Namespace) -> int:
    if not args.dry_run:
        raise ValueError(
            "live executor pilot requires separate exact user authority"
        )
    payload = {
        "schema_generation": 6,
        "command": "executor",
        "dry_run": True,
        "invocation_profile": invocation_profile(
            model=args.model,
            effort=args.effort,
            timeout_seconds=args.timeout,
            arm=args.arm,
            session_mode="fresh",
        ),
        "effects": {
            "capabilities_minted": 0,
            "attempts_claimed": 0,
            "authorities_consumed": 0,
            "fixtures_created": 0,
            "outputs_created": 0,
            "workspaces_created": 0,
            "subprocesses": 0,
            "model_calls": 0,
            "network_calls": 0,
        },
        "gate_authority_required": True,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m evaluation.cli",
        description="HappyCodex clean-break certification engine",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="validate identities and the evidence ledger")
    impact = commands.add_parser(
        "impact", help="inspect pending gates; fail closed until cost is persisted"
    )
    impact.add_argument(
        "--public",
        type=Path,
        help="bind the pinned public-0.4.0 package into the proposed holdout invocation",
    )

    executor = commands.add_parser(
        "executor", help="inspect the separately gated Executor pilot"
    )
    executor.add_argument("--dry-run", action="store_true")
    executor.add_argument("--model", default=DEFAULT_MODEL)
    executor.add_argument("--effort", default=DEFAULT_EFFORT)
    executor.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    executor.add_argument("--arm", choices=("candidate",), default="candidate")

    corpus = commands.add_parser("corpus", help="inspect or run behavior cases")
    corpus.add_argument("--plugin", type=Path, default=ROOT)
    corpus.add_argument("--case", action="append", dest="cases")
    corpus.add_argument("--list", action="store_true")
    corpus.add_argument("--dry-run", action="store_true")
    corpus.add_argument("--model", default=DEFAULT_MODEL)
    corpus.add_argument("--effort", default=DEFAULT_EFFORT)
    corpus.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    corpus.add_argument(
        "--arm", choices=("candidate", "public-0.4.0"), default="candidate"
    )
    corpus.add_argument("--output", type=Path)
    corpus.add_argument("--bind-impact")

    holdout = commands.add_parser("holdout", help="inspect or run blinded holdouts")
    holdout.add_argument("--candidate", type=Path, default=ROOT)
    holdout.add_argument("--public", type=Path)
    holdout.add_argument("--output", type=Path)
    holdout.add_argument("--model", default=DEFAULT_MODEL)
    holdout.add_argument("--effort", default=DEFAULT_EFFORT)
    holdout.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    holdout.add_argument("--list", action="store_true")
    holdout.add_argument("--dry-run", action="store_true")
    holdout.add_argument("--bind-impact")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "verify":
        return verify_command()
    if args.command == "impact":
        try:
            return impact_command(args.public)
        except (OSError, RuntimeError, ValueError) as exc:
            parser.error(str(exc))
    if args.command == "executor":
        try:
            return executor_command(args)
        except ValueError as exc:
            parser.error(str(exc))
    if args.command in {"corpus", "holdout"}:
        return live.run_command(args, parser)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
