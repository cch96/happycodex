"""Pure command surface plus mechanically derived offline checks."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from evaluation.canonical import ContractError, canonical_sha256
from evaluation.identity import (
    evaluator_components, review_snapshot_from_git, validate_review_projection,
)
from evaluation.manifest import (
    build_production_spec, qualified_evaluation_authority_request,
    qualify_production_spec,
)
from evaluation.policy import RECORD_TYPES, UNIT_TOPOLOGY
from evaluation.records import validate_record

class CliError(ContractError):
    pass

def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CliError(f"cannot load {path}") from exc
    if type(value) is not dict:
        raise CliError(f"{path} is not a JSON object")
    return value

def _print(value: Any, *, stream: Any = sys.stdout) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2), file=stream)

def _construction(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "root": args.repo.resolve(), "previous_root": args.previous_repo.resolve(),
        "product": validate_record(_load(args.product)),
        "previous_product": validate_record(_load(args.previous_product)),
        "review_projection": validate_review_projection(_load(args.review_projection)),
        "holdout_mappings": _load(args.mappings), "caps": _load(args.caps),
    }

def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments], capture_output=True, text=True,
        env={"PATH": os.defpath, "LC_ALL": "C", "GIT_CONFIG_GLOBAL": "/dev/null",
             "GIT_CONFIG_NOSYSTEM": "1", "GIT_OPTIONAL_LOCKS": "0"},
    )
    if completed.returncode:
        raise CliError(f"git {' '.join(arguments)} failed")
    return completed.stdout.strip()

def _snapshot_loc(projection: dict[str, Any]) -> dict[str, Any]:
    modules = {}
    for entry in projection["candidate"]["entries"]:
        path = entry["path"]
        if path.startswith("evaluation/") and path.endswith(".py"):
            body = base64.b64decode(entry["content"], validate=True)
            modules[path] = len(body.splitlines())
    total = sum(modules.values())
    return {
        "modules": modules, "total": total, "practical_limit": 3200,
        "hard_limit": 3600, "module_limit": 600,
        "practical_within_limit": total <= 3200,
        "hard_within_limit": total <= 3600,
        "modules_within_limit": all(lines <= 600 for lines in modules.values()),
    }

def run_mechanical_checks(root: Path, review_projection: dict[str, Any]) -> dict[str, Any]:
    """Run the fixed offline suite against the exact clean candidate snapshot."""
    root = root.resolve(strict=True)
    projection = validate_review_projection(review_projection)
    candidate = projection["candidate"]
    if (
        _git(root, "rev-parse", "HEAD^{commit}") != candidate["commit"]
        or _git(root, "rev-parse", "HEAD^{tree}") != candidate["tree"]
        or _git(root, "status", "--porcelain=v1", "--untracked-files=all")
        or review_snapshot_from_git(root, candidate["commit"]) != candidate
    ):
        raise CliError("working source differs from the immutable candidate snapshot")
    system_skills = Path.home() / ".codex/skills/.system"
    commands = (
        (sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"),
        (sys.executable, "-B", "-c", "import evaluation.canonical,evaluation.cli,evaluation.holdout,evaluation.host,evaluation.identity,evaluation.manifest,evaluation.oracle,evaluation.policy,evaluation.provider,evaluation.records,evaluation.schemas,evaluation.verify"),
        (sys.executable, "-B", str(system_skills / "skill-creator/scripts/quick_validate.py"), "skills/happycodex"),
        (sys.executable, "-B", str(system_skills / "plugin-creator/scripts/validate_plugin.py"), "."),
        ("git", "diff", "--check"),
    )
    results = []
    with tempfile.TemporaryDirectory(prefix="happycodex-v3-checks-") as cache:
        environment = {"PATH": os.defpath, "LC_ALL": "C", "PYTHONPYCACHEPREFIX": cache}
        for command in commands:
            completed = subprocess.run(
                command, cwd=root, env=environment, capture_output=True, text=False,
            )
            results.append({
                "command": list(command), "returncode": completed.returncode,
                "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
                "passed": completed.returncode == 0,
            })
    loc = _snapshot_loc(projection)
    body = {
        "candidate_snapshot_sha256": projection["candidate_snapshot_sha256"],
        "candidate_commit": candidate["commit"], "candidate_tree": candidate["tree"],
        "checks": results, "production_python_loc": loc,
        "passed": all(item["passed"] for item in results)
        and loc["practical_within_limit"] and loc["hard_within_limit"]
        and loc["modules_within_limit"],
    }
    return {**body, "checks_sha256": canonical_sha256(body)}

def _handle(args: argparse.Namespace) -> int:
    if args.command == "inventory":
        _print({
            "durable_record_types": list(RECORD_TYPES),
            "unit_topology": [unit._asdict() for unit in UNIT_TOPOLOGY],
            "component_identities": evaluator_components(args.repo.resolve()),
            "active_ledger": False, "external_authentication": "unavailable",
        })
    elif args.command == "materialize":
        _print(build_production_spec(**_construction(args)))
    elif args.command == "qualify":
        spec = validate_record(_load(args.spec))
        qualify_production_spec(spec, **_construction(args))
        _print({"qualified": True, "spec_sha256": spec["spec_sha256"]})
    elif args.command == "authority":
        spec = validate_record(_load(args.spec))
        request = qualified_evaluation_authority_request(spec, **_construction(args))
        _print({
            "authority_request": request, "authority_authenticated": False,
            "notice": "This unsigned request cannot manufacture user authority.",
        })
    elif args.command == "validate":
        value = _load(args.path)
        validated = (
            validate_review_projection(value)
            if value.get("projection_type") == "ReviewProjection" else validate_record(value)
        )
        _print({"valid": True, "identity": validated.get("record_sha256", validated.get("projection_sha256"))})
    elif args.command == "checks":
        _print(run_mechanical_checks(args.repo, _load(args.review_projection)))
    else:
        _print({
            "status": "UNVERIFIED", "authenticated": False,
            "reason": "The CLI has no external authenticator; use evaluation.verify inside the external boundary.",
        })
        return 2
    return 0

def _add_construction(command: argparse.ArgumentParser, *, spec: bool = False) -> None:
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--previous-repo", type=Path, required=True)
    for name in ("product", "previous-product", "review-projection", "mappings", "caps"):
        command.add_argument(f"--{name}", type=Path, required=True)
    if spec:
        command.add_argument("--spec", type=Path, required=True)

def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="HappyCodex v3 thin-verifier tools")
    subcommands = result.add_subparsers(dest="command", required=True)
    inventory = subcommands.add_parser("inventory")
    inventory.add_argument("--repo", type=Path, default=Path.cwd())
    for name in ("materialize", "qualify", "authority"):
        _add_construction(subcommands.add_parser(name), spec=name != "materialize")
    validate = subcommands.add_parser("validate")
    validate.add_argument("path", type=Path)
    checks = subcommands.add_parser("checks")
    checks.add_argument("--repo", type=Path, default=Path.cwd())
    checks.add_argument("--review-projection", type=Path, required=True)
    subcommands.add_parser("verify")
    return result

def main(argv: list[str] | None = None) -> int:
    try:
        return _handle(parser().parse_args(argv))
    except (ContractError, OSError) as exc:
        _print({"error": str(exc)}, stream=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())

__all__ = ("CliError", "main", "parser", "run_mechanical_checks")
