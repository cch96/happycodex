#!/usr/bin/env python3
"""Atomically claim HappyCodex shared mutable resources without a service."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
from typing import Any


SCHEMA_VERSION = 1
FILESYSTEM_ROLES = {"worktree", "ledger", "output", "activation"}
RESOURCE_ROLES = FILESYSTEM_ROLES | {"ref"}
CLAIM_ROOT_NAME = ".happycodex-resource-claims"
GIT_CLAIM_ROOT_NAME = "happycodex-resource-claims"
CLAIM_RECORD_NAME = "claim"
TOKEN_PATTERN = re.compile(r"[0-9a-f]{64}")


class ClaimError(RuntimeError):
    """A claim cannot be acquired, proved, or released safely."""


@dataclass(frozen=True)
class Resource:
    role: str
    locator: str
    canonical_key: str
    claim_root: Path

    @property
    def claim_dir(self) -> Path:
        digest = hashlib.sha256(self.canonical_key.encode()).hexdigest()
        return self.claim_root / f"{digest}.claim"

    @property
    def spec(self) -> str:
        return f"{self.role}={self.locator}"


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _absolute_path(raw: str, *, label: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        raise ClaimError(f"{label} must be an absolute path")
    return path.resolve(strict=False)


def _git_common_dir(path: Path, *, required: bool) -> Path | None:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        if required:
            raise ClaimError(f"Git resource is not in a repository: {path}")
        return None
    common = Path(completed.stdout.strip())
    if not common.is_absolute():
        common = (path / common).resolve(strict=False)
    else:
        common = common.resolve(strict=False)
    if not common.is_dir():
        raise ClaimError(f"Git common directory is unavailable: {common}")
    return common


def _parse_resource(spec: str) -> Resource:
    role, separator, raw_locator = spec.partition("=")
    if not separator or role not in RESOURCE_ROLES or not raw_locator:
        raise ClaimError(f"invalid resource specification: {spec!r}")
    if role == "ref":
        raw_repo, separator, ref = raw_locator.partition("::")
        if not separator or not ref:
            raise ClaimError("ref resource must be REPOSITORY::REF")
        repo = _absolute_path(raw_repo, label="ref repository")
        common = _git_common_dir(repo, required=True)
        assert common is not None
        checked = subprocess.run(
            ["git", "check-ref-format", ref],
            check=False,
            capture_output=True,
            text=True,
        )
        if checked.returncode:
            raise ClaimError(f"invalid Git ref: {ref!r}")
        locator = f"{repo}::{ref}"
        return Resource(
            role=role,
            locator=locator,
            canonical_key=f"ref:{common}:{ref}",
            claim_root=common / GIT_CLAIM_ROOT_NAME,
        )

    path = _absolute_path(raw_locator, label=f"{role} resource")
    if role == "worktree":
        if not path.is_dir():
            raise ClaimError(f"worktree resource is unavailable: {path}")
        common = _git_common_dir(path, required=True)
        assert common is not None
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
        if (
            completed.returncode
            or Path(completed.stdout.strip()).resolve(strict=False) != path
        ):
            raise ClaimError(f"resource is not a worktree root: {path}")
        claim_root = common / GIT_CLAIM_ROOT_NAME
    else:
        if not path.parent.is_dir():
            raise ClaimError(f"resource parent is unavailable: {path.parent}")
        claim_root = path.parent / CLAIM_ROOT_NAME
    return Resource(
        role=role,
        locator=str(path),
        canonical_key=f"fs:{path}",
        claim_root=claim_root,
    )


def _resources(specs: list[str]) -> list[Resource]:
    if not specs:
        raise ClaimError("at least one resource is required")
    by_key: dict[str, Resource] = {}
    for spec in specs:
        resource = _parse_resource(spec)
        prior = by_key.get(resource.canonical_key)
        if prior is not None and prior.spec != resource.spec:
            raise ClaimError(
                "one canonical resource was declared with multiple roles or locators"
            )
        by_key[resource.canonical_key] = resource
    return [by_key[key] for key in sorted(by_key)]


def _claim_record(
    resource: Resource,
    *,
    owner: str,
    task: str,
    execplan: Path,
    token: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "canonical_key": resource.canonical_key,
        "resource": resource.spec,
        "owner": owner,
        "task": task,
        "execplan": str(execplan),
        "owner_token": token,
    }


def _write_new(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def _remove_empty_root(root: Path) -> None:
    try:
        root.rmdir()
    except OSError:
        pass


def _rollback(acquired: list[tuple[Resource, bytes]]) -> None:
    for resource, expected in reversed(acquired):
        metadata = resource.claim_dir / CLAIM_RECORD_NAME
        try:
            if metadata.read_bytes() == expected:
                metadata.unlink()
                resource.claim_dir.rmdir()
                _remove_empty_root(resource.claim_root)
        except OSError:
            continue


def acquire(
    *,
    resources: list[str],
    owner: str,
    task: str,
    execplan: str,
    receipt: str,
) -> dict[str, Any]:
    """Acquire every sorted resource or leave no newly acquired claim behind."""
    if not owner.strip() or not task.strip():
        raise ClaimError("owner and task must be nonblank")
    execplan_path = _absolute_path(execplan, label="ExecPlan")
    receipt_path = _absolute_path(receipt, label="receipt")
    if not receipt_path.parent.is_dir():
        raise ClaimError("receipt parent must already exist")
    parsed = _resources(resources)
    token = secrets.token_hex(32)
    acquired: list[tuple[Resource, bytes]] = []
    try:
        for resource in parsed:
            resource.claim_root.mkdir(mode=0o700, exist_ok=True)
            try:
                resource.claim_dir.mkdir(mode=0o700)
            except FileExistsError as error:
                raise ClaimError(
                    f"resource is already claimed: {resource.canonical_key}"
                ) from error
            record = _claim_record(
                resource,
                owner=owner,
                task=task,
                execplan=execplan_path,
                token=token,
            )
            encoded = _canonical_json(record)
            try:
                _write_new(resource.claim_dir / CLAIM_RECORD_NAME, encoded)
            except Exception:
                resource.claim_dir.rmdir()
                raise
            acquired.append((resource, encoded))

        value = {
            "schema_version": SCHEMA_VERSION,
            "owner": owner,
            "task": task,
            "execplan": str(execplan_path),
            "owner_token": token,
            "claims": [
                {
                    "resource": resource.spec,
                    "canonical_key": resource.canonical_key,
                    "claim_dir": str(resource.claim_dir),
                    "claim_sha256": _sha256(encoded),
                }
                for resource, encoded in acquired
            ],
        }
        _write_new(receipt_path, _canonical_json(value))
        return value
    except Exception:
        _rollback(acquired)
        raise


def _load_receipt(path: str) -> tuple[Path, dict[str, Any], list[Resource]]:
    receipt_path = _absolute_path(path, label="receipt")
    try:
        value = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ClaimError("claim receipt is missing or invalid") from error
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "owner",
        "task",
        "execplan",
        "owner_token",
        "claims",
    }:
        raise ClaimError("claim receipt has an invalid envelope")
    if (
        value["schema_version"] != SCHEMA_VERSION
        or not isinstance(value["owner"], str)
        or not value["owner"].strip()
        or not isinstance(value["task"], str)
        or not value["task"].strip()
        or not isinstance(value["execplan"], str)
        or not isinstance(value["owner_token"], str)
        or TOKEN_PATTERN.fullmatch(value["owner_token"]) is None
        or not isinstance(value["claims"], list)
        or not value["claims"]
    ):
        raise ClaimError("claim receipt has invalid identity fields")
    resources: list[Resource] = []
    keys: list[str] = []
    for claim in value["claims"]:
        if not isinstance(claim, dict) or set(claim) != {
            "resource",
            "canonical_key",
            "claim_dir",
            "claim_sha256",
        }:
            raise ClaimError("claim receipt has an invalid member")
        resource = _parse_resource(claim["resource"])
        if (
            claim["canonical_key"] != resource.canonical_key
            or claim["claim_dir"] != str(resource.claim_dir)
            or not isinstance(claim["claim_sha256"], str)
            or TOKEN_PATTERN.fullmatch(claim["claim_sha256"]) is None
        ):
            raise ClaimError(
                "claim receipt member does not match its canonical resource"
            )
        resources.append(resource)
        keys.append(resource.canonical_key)
    if keys != sorted(set(keys)):
        raise ClaimError("claim receipt resources are not unique and sorted")
    return receipt_path, value, resources


def _verified_claims(
    receipt: dict[str, Any], resources: list[Resource]
) -> list[tuple[Resource, bytes]]:
    execplan = _absolute_path(receipt["execplan"], label="ExecPlan")
    verified: list[tuple[Resource, bytes]] = []
    for resource, member in zip(resources, receipt["claims"], strict=True):
        expected = _canonical_json(
            _claim_record(
                resource,
                owner=receipt["owner"],
                task=receipt["task"],
                execplan=execplan,
                token=receipt["owner_token"],
            )
        )
        metadata = resource.claim_dir / CLAIM_RECORD_NAME
        try:
            actual = metadata.read_bytes()
        except OSError as error:
            raise ClaimError(
                f"claim is missing or unreadable: {resource.canonical_key}"
            ) from error
        if actual != expected or member["claim_sha256"] != _sha256(expected):
            raise ClaimError(f"claim identity mismatch: {resource.canonical_key}")
        verified.append((resource, expected))
    return verified


def verify(*, receipt: str) -> dict[str, Any]:
    """Prove the receipt still owns every canonical resource."""
    _, value, resources = _load_receipt(receipt)
    _verified_claims(value, resources)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "verified",
        "owner": value["owner"],
        "task": value["task"],
        "owner_token": value["owner_token"],
        "resource_count": len(resources),
    }


def release(*, receipt: str) -> dict[str, Any]:
    """Release only claims still matching the receipt's exact owner token."""
    _, value, resources = _load_receipt(receipt)
    verified = _verified_claims(value, resources)
    for resource, expected in reversed(verified):
        release_dir = resource.claim_dir.with_name(
            f"{resource.claim_dir.name}.release-{value['owner_token']}"
        )
        try:
            resource.claim_dir.rename(release_dir)
            metadata = release_dir / CLAIM_RECORD_NAME
            if metadata.read_bytes() != expected:
                release_dir.rename(resource.claim_dir)
                raise ClaimError(
                    f"claim changed during release: {resource.canonical_key}"
                )
            metadata.unlink()
            release_dir.rmdir()
            _remove_empty_root(resource.claim_root)
        except OSError as error:
            raise ClaimError(
                f"claim could not be safely released: {resource.canonical_key}"
            ) from error
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "released",
        "owner": value["owner"],
        "task": value["task"],
        "owner_token": value["owner_token"],
        "resource_count": len(resources),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    acquire_parser = commands.add_parser("acquire")
    acquire_parser.add_argument("--owner", required=True)
    acquire_parser.add_argument("--task", required=True)
    acquire_parser.add_argument("--execplan", required=True)
    acquire_parser.add_argument("--receipt", required=True)
    acquire_parser.add_argument("--resource", action="append", required=True)
    for command in ("verify", "release"):
        command_parser = commands.add_parser(command)
        command_parser.add_argument("--receipt", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "acquire":
            result = acquire(
                resources=args.resource,
                owner=args.owner,
                task=args.task,
                execplan=args.execplan,
                receipt=args.receipt,
            )
        elif args.command == "verify":
            result = verify(receipt=args.receipt)
        else:
            result = release(receipt=args.receipt)
    except (ClaimError, OSError, ValueError) as error:
        print(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "blocked",
                    "reason": str(error),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
