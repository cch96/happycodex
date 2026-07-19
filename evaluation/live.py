from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from evaluation.core.identity import package_identities
from evaluation.core.impact import (
    build_snapshot,
    impact_token as snapshot_impact_token,
    plan_impact,
)
from evaluation.core.ledger import load_ledger, require_authorized_invocation
from evaluation.corpus import engine as corpus_engine
from evaluation.holdout import engine as holdout_engine


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "evaluation" / "results" / "current.json"


def _settings_from_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    settings = ledger["snapshot"]["settings"]
    return {
        "model": settings["model"],
        "effort": settings["effort"],
        "timeout": settings["timeout_seconds"],
    }


def load_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    ledger = load_ledger(LEDGER_PATH)
    current = build_snapshot(ROOT, **_settings_from_ledger(ledger))
    impact = plan_impact(ledger["snapshot"], current, pending=ledger["pending"])
    if ledger["state"] == "certified" and impact["gates"]:
        raise ValueError("certified ledger is stale against current inputs")
    return ledger, current, impact


def impact_token(
    ledger: dict[str, Any], current: dict[str, Any], impact: dict[str, Any]
) -> str:
    del ledger
    return snapshot_impact_token(current, impact)


def _require_snapshot_settings(
    args: argparse.Namespace, current: dict[str, Any]
) -> None:
    settings = current["settings"]
    if (
        args.model != settings["model"]
        or args.effort != settings["effort"]
        or args.timeout != settings["timeout_seconds"]
    ):
        raise ValueError("live invocation settings do not match the current snapshot")


def proposed_invocations(
    current: dict[str, Any],
    impact: dict[str, Any],
    *,
    public: Path | None = None,
) -> list[dict[str, Any]]:
    settings = current["settings"]
    invocations: list[dict[str, Any]] = []
    if impact["corpus_cases"]:
        invocations.append(
            {
                "command": "corpus",
                "package_semantic_sha256": current["package"]["semantic_sha256"],
                "package_artifact_sha256": current["package"]["artifact_sha256"],
                "model": settings["model"],
                "effort": settings["effort"],
                "timeout_seconds": settings["timeout_seconds"],
                "arm": "candidate",
                "cases": impact["corpus_cases"],
            }
        )
    if impact["holdout_pairs"] and public is not None:
        public_identity = package_identities(public.expanduser().resolve())
        if (
            public_identity["artifact_sha256"]
            != corpus_engine.EXPECTED_PUBLIC_02_PACKAGE_MANIFEST_SHA256
        ):
            raise ValueError("public-0.2 package manifest mismatch")
        invocations.append(
            {
                "command": "holdout",
                "candidate_semantic_sha256": current["package"]["semantic_sha256"],
                "candidate_artifact_sha256": current["package"]["artifact_sha256"],
                "public_semantic_sha256": public_identity["semantic_sha256"],
                "public_artifact_sha256": public_identity["artifact_sha256"],
                "model": settings["model"],
                "effort": settings["effort"],
                "timeout_seconds": settings["timeout_seconds"],
                "pairs": impact["holdout_pairs"],
            }
        )
    return invocations


def corpus_invocation(
    args: argparse.Namespace,
    *,
    current: dict[str, Any],
    impact: dict[str, Any],
) -> dict[str, Any]:
    _require_snapshot_settings(args, current)
    if args.arm != "candidate":
        raise ValueError("live corpus certification requires the candidate arm")
    cases = corpus_engine.load_cases()
    selected = args.cases or list(cases)
    if len(selected) != len(set(selected)) or set(selected) - set(cases):
        raise ValueError("live corpus invocation has invalid or duplicate cases")
    selected = sorted(selected)
    if selected != impact["corpus_cases"]:
        raise ValueError("live corpus cases must match the current impact scope")
    plugin = args.plugin.expanduser().resolve()
    identities = package_identities(plugin)
    if identities != current["package"]:
        raise ValueError("live corpus package does not match the current snapshot")
    descriptor = next(
        (
            item
            for item in proposed_invocations(current, impact)
            if item["command"] == "corpus"
        ),
        None,
    )
    if descriptor is None:
        raise ValueError("current impact does not authorize a corpus refresh")
    if descriptor["cases"] != selected:
        raise AssertionError("planned corpus scope changed during invocation binding")
    return descriptor


def holdout_invocation(
    args: argparse.Namespace,
    *,
    current: dict[str, Any],
    impact: dict[str, Any],
) -> dict[str, Any]:
    _require_snapshot_settings(args, current)
    if args.public is None:
        raise ValueError("--public is required for a live paired run")
    manifest = holdout_engine.load_manifest()
    pairs = sorted(pair["id"] for pair in manifest["pairs"])
    if pairs != impact["holdout_pairs"]:
        raise ValueError("live holdout pairs must match the current impact scope")
    candidate = package_identities(args.candidate.expanduser().resolve())
    if candidate != current["package"]:
        raise ValueError("live holdout candidate does not match the current snapshot")
    descriptors = proposed_invocations(current, impact, public=args.public)
    descriptor = next(
        (item for item in descriptors if item["command"] == "holdout"), None
    )
    if descriptor is None:
        raise ValueError("current impact does not authorize a holdout refresh")
    if descriptor["pairs"] != pairs:
        raise AssertionError("planned holdout scope changed during invocation binding")
    return descriptor


def run_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    offline_runner = {
        "corpus": corpus_engine.run_command,
        "holdout": holdout_engine.run_command,
    }[args.command]
    if args.list or args.dry_run:
        return offline_runner(args)
    try:
        ledger, current, impact = load_state()
        binding = impact_token(ledger, current, impact)
        if args.bind_impact != binding:
            raise ValueError(
                "live evaluation requires the exact impact_token from a fresh "
                "read-only impact receipt"
            )
        invocation = (
            corpus_invocation(args, current=current, impact=impact)
            if args.command == "corpus"
            else holdout_invocation(args, current=current, impact=impact)
        )
        authorization = require_authorized_invocation(
            ledger["live_authority"],
            snapshot=current,
            impact=impact,
            invocation=invocation,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    live_runner = {
        "corpus": corpus_engine.run_authorized,
        "holdout": holdout_engine.run_authorized,
    }[args.command]
    return live_runner(args, authorization)
