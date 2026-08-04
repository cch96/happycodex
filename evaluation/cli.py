from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Any

from evaluation.identity import evaluator_components, load_json, product_artifact_from_git
from evaluation.manifest import materialize_eval_spec
from evaluation.provider import build_fixed_host_policy, host_contract_from_policy
from evaluation.records import (
    RECORD_TYPES, canonical_sha256, evaluation_authority_request_payload,
    validate_eval_spec, validate_evaluation_authority_payload, validate_record,
)
from evaluation.verify import exact_final_authority_proposal, verify_evaluation, verify_release


def _print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


def _records(paths: list[Path]) -> list[dict[str, Any]]:
    return [validate_record(load_json(path.resolve())) for path in paths]


def inventory_command(args: argparse.Namespace) -> int:
    _print(
        {
            "durable_record_types": sorted(RECORD_TYPES),
            "components": evaluator_components(args.repo.resolve()),
            "active_ledger": False,
        }
    )
    return 0


def product_command(args: argparse.Namespace) -> int:
    _print(
        product_artifact_from_git(
            args.repo.resolve(), args.revision,
            external_role_config_sha256=args.external_role_config_sha256,
        )
    )
    return 0


def request_command(args: argparse.Namespace) -> int:
    spec = validate_eval_spec(load_json(args.spec.resolve()))
    # This is deliberately only a request digest. It cannot mint approval text,
    # signatures, capabilities, plans, or receipts.
    proposal = evaluation_authority_request_payload(spec)
    _print({"authority_request_sha256": canonical_sha256(proposal), "proposal": proposal})
    return 0


def materialize_command(args: argparse.Namespace) -> int:
    _print(
        materialize_eval_spec(
            root=args.repo.resolve(), candidate=validate_record(load_json(args.product.resolve())),
            previous=validate_record(load_json(args.previous_product.resolve())),
            profiles=load_json(args.profiles.resolve()), total_cap=load_json(args.total_cap.resolve()),
            holdout_mapping=load_json(args.mapping.resolve()),
            review_brief=load_json(args.review_brief.resolve()),
            host_contract=load_json(args.host_contract.resolve()),
        )
    )
    return 0


def _write_private(path: Path, value: Any) -> None:
    body = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view = memoryview(body)
        while view: view = view[os.write(descriptor, view):]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _copy_private(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"private input is not a regular file: {source}")
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view = memoryview(source.read_bytes())
        while view: view = view[os.write(descriptor, view):]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _remove_private_tree(root: Path) -> None:
    if not root.exists(): return
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if not path.is_symlink(): path.chmod(0o700 if path.is_dir() else 0o600)
    root.chmod(0o700); shutil.rmtree(root)


def _relocate(value: Any, source: Path, destination: Path) -> Any:
    if type(value) is dict: return {key: _relocate(item, source, destination) for key, item in value.items()}
    if type(value) is list: return [_relocate(item, source, destination) for item in value]
    if type(value) is str and (value == str(source) or value.startswith(str(source) + "/")):
        return str(destination) + value[len(str(source)):]
    return value


def prepare_exact_request_command(args: argparse.Namespace) -> int:
    destination = args.destination.absolute()
    staging = destination.with_name(destination.name + ".staging")
    if destination.exists() or destination.is_symlink() or staging.exists() or staging.is_symlink():
        raise ValueError("exact request destination or staging path already exists")
    product = validate_record(load_json(args.product.resolve()))
    previous_product = validate_record(load_json(args.previous_product.resolve()))
    previous_spec = validate_record(load_json(args.previous_spec.resolve()))
    profiles, total_cap = load_json(args.profiles.resolve()), load_json(args.total_cap.resolve())
    effect_cap = load_json(args.effect_cap.resolve())
    mapping, brief = load_json(args.mapping.resolve()), load_json(args.review_brief.resolve())
    attestation_paths = _named_paths(args.attestation, "attestation")
    raw_paths = _named_paths(args.raw, "raw")
    if set(attestation_paths) != set(raw_paths) or len(attestation_paths) != 11 or "exact-final" in attestation_paths:
        raise ValueError("exact request requires exactly eleven named non-exact prerequisites")
    attestations = []
    for unit_id, path in sorted(attestation_paths.items()):
        record = validate_record(load_json(path))
        if record.get("unit_id") != unit_id: raise ValueError("named attestation unit differs")
        attestations.append(record)
    raw_streams = {unit_id: raw_paths[unit_id].read_bytes() for unit_id in sorted(raw_paths)}
    published = False
    try:
        staging.mkdir(mode=0o700)
        execution = staging / "execution"; execution.mkdir(mode=0o700)
        for name in ("units", "raw", "attestations", "claims"):
            (execution / name).mkdir(mode=0o700)
        private = staging / "private"; private.mkdir(mode=0o700)
        private_evaluation = private / "evaluation"; private_evaluation.mkdir(mode=0o700)
        role = private / "happycodex_executor.toml"
        oracle = private_evaluation / "hidden-oracles-v1.json"
        _copy_private(args.external_role_config.resolve(), role)
        _copy_private(args.hidden_oracle.resolve(), oracle)
        mapping_path = staging / "holdout-mapping.json"; _write_private(mapping_path, mapping)
        exact_source = execution / "exact-final-source"
        shutil.copytree(args.exact_source.resolve(), exact_source, copy_function=shutil.copy2)
        staging_policy = build_fixed_host_policy(
            execution_root=execution, binary_path=args.provider_binary.resolve(),
            external_role_config_path=role, exact_final_source=exact_source,
            holdout_mapping_path=mapping_path, private_oracle_path=oracle,
            behavior_model=profiles["behavior"]["model"],
            behavior_effort=profiles["behavior"]["effort"],
        )
        contract = host_contract_from_policy(staging_policy)
        spec = materialize_eval_spec(
            root=args.repo.resolve(), candidate=product, previous=previous_product,
            profiles=profiles, total_cap=total_cap, holdout_mapping=mapping,
            review_brief=brief, host_contract=contract,
        )
        proposal = exact_final_authority_proposal(
            root=args.repo.resolve(), product=product, previous_product=previous_product,
            previous_spec=previous_spec, spec=spec, attestations=attestations,
            raw_streams=raw_streams, holdout_mapping=mapping,
            mapping_revealed_at=args.revealed_at, total_cap=effect_cap,
        )
        validate_evaluation_authority_payload(spec, proposal)
        request_sha = canonical_sha256(proposal)
        line = f"APPROVE HAPPYCODEX EVALUATION {request_sha}"
        outputs = {
            "product.json": product, "previous-product.json": previous_product,
            "previous-eval-spec.json": previous_spec, "profiles.json": profiles,
            "total-cap.json": total_cap, "effect-cap.json": effect_cap,
            "review-brief.json": brief, "host-contract.json": contract,
            "host-policy.json": _relocate(staging_policy, staging, destination),
            "eval-spec.json": spec,
            "authority-request.json": {
                "authority_request_sha256": request_sha,
                "selected_unit_ids": proposal["selected_unit_ids"],
                "canonical_approval_line": {"text": line, "authoritative": False},
                "proposal": proposal,
            },
        }
        for name, value in outputs.items(): _write_private(staging / name, value)
        os.rename(staging, destination); published = True
        if host_contract_from_policy(outputs["host-policy.json"]) != contract:
            raise ValueError("published host policy identity differs")
        _print({
            "destination": str(destination), "authority_request_sha256": request_sha,
            "eval_spec_record_sha256": spec["record_sha256"],
            "exact_final_source_sha256": outputs["host-policy.json"]["workspace_policy"]["exact_final_source_sha256"],
            "prerequisite_count": len(proposal["prerequisites"]),
            "selected_unit_ids": proposal["selected_unit_ids"],
            "canonical_approval_line": {"text": line, "authoritative": False},
        })
        return 0
    except Exception:
        _remove_private_tree(destination if published else staging)
        raise


def _named_paths(values: list[str], label: str) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        unit_id, separator, raw_path = value.partition("=")
        if not separator or not unit_id or not raw_path or unit_id in result:
            raise ValueError(f"{label} must be unique UNIT=PATH values")
        result[unit_id] = Path(raw_path).resolve()
    return result


def _evidence(args: argparse.Namespace):
    raw_paths = _named_paths(args.raw, "raw")
    return {unit_id: path.read_bytes() for unit_id, path in raw_paths.items()}


def verify_command(args: argparse.Namespace) -> int:
    product = validate_record(load_json(args.product.resolve()))
    previous_product = validate_record(load_json(args.previous_product.resolve()))
    spec = validate_record(load_json(args.spec.resolve()))
    attestations = _records(args.attestation)
    mapping = load_json(args.mapping.resolve()) if args.mapping else None
    raw_streams = _evidence(args)
    result = verify_evaluation(
        root=args.repo.resolve(), product=product, spec=spec, attestations=attestations,
        raw_streams=raw_streams,
        previous_product=previous_product,
        holdout_mapping=mapping, mapping_revealed_at=args.revealed_at,
    )
    _print(result)
    return 0 if result["verified"] else 2


def release_command(args: argparse.Namespace) -> int:
    product = validate_record(load_json(args.product.resolve()))
    previous_product = validate_record(load_json(args.previous_product.resolve()))
    spec = validate_record(load_json(args.spec.resolve()))
    attestations = _records(args.attestation)
    mapping = load_json(args.mapping.resolve())
    raw_streams = _evidence(args)
    evaluation = verify_evaluation(
        root=args.repo.resolve(), product=product, spec=spec, attestations=attestations,
        raw_streams=raw_streams,
        previous_product=previous_product,
        holdout_mapping=mapping, mapping_revealed_at=args.revealed_at,
    )
    receipt = validate_record(load_json(args.release_receipt.resolve()))
    destination = load_json(args.destination.resolve())
    rollback = load_json(args.rollback.resolve())
    result = verify_release(
        product=product, evaluation=evaluation, receipt=receipt,
        destination=destination, rollback=rollback,
    )
    _print(result)
    return 0


def record_command(args: argparse.Namespace) -> int:
    record = validate_record(load_json(args.path.resolve()))
    _print({"valid": True, "record_type": record["record_type"], "record_sha256": record["record_sha256"]})
    return 0


def _add_evidence_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--raw", action="append", required=True, help="UNIT=PATH")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Stateless HappyCodex evaluator attestation tools")
    sub = result.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory")
    inventory.add_argument("--repo", type=Path, default=Path.cwd())
    inventory.set_defaults(handler=inventory_command)

    product = sub.add_parser("product")
    product.add_argument("--repo", type=Path, default=Path.cwd())
    product.add_argument("--revision", required=True)
    product.add_argument("--external-role-config-sha256", required=True)
    product.set_defaults(handler=product_command)

    request = sub.add_parser("authority-request")
    request.add_argument("--spec", type=Path, required=True)
    request.set_defaults(handler=request_command)

    materialize = sub.add_parser("materialize")
    materialize.add_argument("--repo", type=Path, default=Path.cwd())
    materialize.add_argument("--product", type=Path, required=True)
    materialize.add_argument("--previous-product", type=Path, required=True)
    materialize.add_argument("--profiles", type=Path, required=True)
    materialize.add_argument("--total-cap", type=Path, required=True)
    materialize.add_argument("--mapping", type=Path, required=True)
    materialize.add_argument("--review-brief", type=Path, required=True)
    materialize.add_argument("--host-contract", type=Path, required=True)
    materialize.set_defaults(handler=materialize_command)

    prepare = sub.add_parser("prepare-exact-request")
    for flag in (
        "product", "previous-product", "previous-spec", "profiles", "total-cap",
        "effect-cap", "mapping", "review-brief", "provider-binary",
        "external-role-config", "hidden-oracle", "exact-source", "destination",
    ):
        prepare.add_argument(f"--{flag}", type=Path, required=True)
    prepare.add_argument("--repo", type=Path, default=Path.cwd())
    prepare.add_argument("--revealed-at", required=True)
    prepare.add_argument("--attestation", action="append", required=True)
    prepare.add_argument("--raw", action="append", required=True)
    prepare.set_defaults(handler=prepare_exact_request_command)

    verify = sub.add_parser("verify")
    verify.add_argument("--product", type=Path, required=True)
    verify.add_argument("--previous-product", type=Path, required=True)
    verify.add_argument("--spec", type=Path, required=True)
    verify.add_argument("--attestation", type=Path, action="append", required=True)
    verify.add_argument("--mapping", type=Path)
    verify.add_argument("--revealed-at")
    _add_evidence_arguments(verify)
    verify.set_defaults(handler=verify_command)

    release = sub.add_parser("verify-release")
    release.add_argument("--product", type=Path, required=True)
    release.add_argument("--previous-product", type=Path, required=True)
    release.add_argument("--spec", type=Path, required=True)
    release.add_argument("--attestation", type=Path, action="append", required=True)
    release.add_argument("--mapping", type=Path, required=True)
    release.add_argument("--revealed-at", required=True)
    release.add_argument("--release-receipt", type=Path, required=True)
    release.add_argument("--destination", type=Path, required=True)
    release.add_argument("--rollback", type=Path, required=True)
    _add_evidence_arguments(release)
    release.set_defaults(handler=release_command)

    record = sub.add_parser("validate-record")
    record.add_argument("path", type=Path)
    record.set_defaults(handler=record_command)

    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
