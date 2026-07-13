#!/usr/bin/env python3
"""Run a fresh native Codex review and retain a verified, secret-free receipt."""

from __future__ import annotations

import argparse
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, BinaryIO, Iterable, Iterator


MODEL = "gpt-5.6-sol"
EFFORT = "max"
SANDBOX = "read-only"
APPROVAL = "never"
NETWORK = "restricted"
DEFAULT_TIMEOUT_SECONDS = 3600.0
SERIES_SCHEMA = 1
MAX_REVIEW_ATTEMPTS = 2
_LIBC = ctypes.CDLL(None, use_errno=True)
TASK_CONTRACT_START = "--- TASK CONTRACT START ---"
TASK_CONTRACT_END = "--- TASK CONTRACT END ---"


class ReviewRunnerError(RuntimeError):
    """Raised when review isolation, execution, or receipt verification fails."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(mode)


def _read_private(path: Path, label: str) -> bytes:
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    except OSError as exc:
        raise ReviewRunnerError(f"cannot open private {label}: {path}") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ReviewRunnerError(
                f"{label} must be a private regular file (mode 0600 or stricter)"
            )
        chunks = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def _git(
    repo: Path,
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args], cwd=repo, env=env, capture_output=True, text=True
    )
    if check and completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ReviewRunnerError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return completed


def _resolve_commit(
    repo: Path, revision: str, env: dict[str, str] | None = None
) -> str:
    return _git(
        repo, "rev-parse", f"{revision}^{{commit}}", env=env
    ).stdout.strip()


def _status(repo: Path, env: dict[str, str] | None = None) -> str:
    return _git(
        repo, "status", "--porcelain=v1", "--untracked-files=all", env=env
    ).stdout


def _masked_index_paths(
    repo: Path, env: dict[str, str] | None = None
) -> list[str]:
    listing = subprocess.run(
        ["git", "ls-files", "-v", "-z"],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
    ).stdout
    masked: list[str] = []
    for record in (item for item in listing.split(b"\0") if item):
        tag, _, path = record.partition(b" ")
        if tag == b"S" or tag.islower():
            masked.append(os.fsdecode(path))
    return masked


def _git_visible_hash(
    repo: Path, env: dict[str, str] | None = None
) -> str:
    digest = hashlib.sha256()
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
    ).stdout
    for encoded in sorted(part for part in listing.split(b"\0") if part):
        path = repo / os.fsdecode(encoded)
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        if path.is_symlink():
            data = os.readlink(path).encode("utf-8", errors="surrogateescape")
            kind = b"L"
        elif path.is_file():
            data = None
            kind = b"F"
        else:
            continue
        digest.update(kind)
        digest.update(stat.S_IMODE(path.lstat().st_mode).to_bytes(4, "big"))
        if data is None:
            _update_file_hash(digest, path)
        else:
            digest.update(len(data).to_bytes(8, "big"))
            digest.update(data)
    return digest.hexdigest()


def _update_file_hash(digest: Any, path: Path) -> None:
    with path.open("rb") as stream:
        expected = os.fstat(stream.fileno()).st_size
        digest.update(expected.to_bytes(8, "big"))
        observed = 0
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            observed += len(chunk)
            digest.update(chunk)
    if observed != expected:
        raise ReviewRunnerError(f"file changed while hashing: {path}")


def _filesystem_hash(root: Path) -> str:
    """Hash every clone entry, including ignored files and Git metadata."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: str(item.relative_to(root))):
        relative = str(path.relative_to(root))
        encoded = relative.encode("utf-8", errors="surrogateescape")
        mode = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            kind = b"L"
            data = os.readlink(path).encode("utf-8", errors="surrogateescape")
        elif path.is_file():
            kind = b"F"
            data = None
        elif path.is_dir():
            kind = b"D"
            data = b""
        else:
            kind = b"O"
            data = b""
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(kind)
        digest.update(mode.to_bytes(4, "big"))
        if data is None:
            _update_file_hash(digest, path)
        else:
            digest.update(len(data).to_bytes(8, "big"))
            digest.update(data)
    return digest.hexdigest()


def _copy_private(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise ReviewRunnerError(f"required source file is missing: {source}")
    _write(destination, source.read_bytes(), 0o600)


def _credential_strings(data: bytes) -> tuple[str, ...]:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReviewRunnerError("auth.json must be valid UTF-8 JSON") from exc
    values: set[str] = set()

    def collect(value: Any) -> None:
        if isinstance(value, str) and len(value) >= 16:
            values.add(value)
        elif isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(payload)
    return tuple(sorted(values, key=len, reverse=True))


def _redact_credentials(text: str, credentials: Iterable[str]) -> tuple[str, bool]:
    redacted = text
    found = False
    for credential in credentials:
        if credential in redacted:
            found = True
            redacted = redacted.replace(credential, "[REDACTED_CREDENTIAL]")
    return redacted, found


def _bounded_chunks(stream: BinaryIO, size: int) -> Iterator[bytes]:
    remaining = size
    while remaining:
        chunk = stream.read(min(1024 * 1024, remaining))
        if not chunk:
            raise ReviewRunnerError("Git object stream ended before its declared size")
        remaining -= len(chunk)
        yield chunk


def _chunks_contain_credentials(
    chunks: Iterable[bytes], credentials: tuple[bytes, ...]
) -> bool:
    if not credentials:
        return False
    overlap = max(len(credential) for credential in credentials) - 1
    carry = b""
    for chunk in chunks:
        window = carry + chunk
        if any(credential in window for credential in credentials):
            return True
        carry = window[-overlap:] if overlap else b""
    return False


def _scan_clone_for_credentials(
    clone: Path, credentials: Iterable[str], git_env: dict[str, str]
) -> None:
    encoded = tuple(value.encode("utf-8") for value in credentials)
    if not encoded:
        return
    for path in sorted(clone.rglob("*")):
        relative = path.relative_to(clone)
        if ".git" in relative.parts or path.is_symlink() or not path.is_file():
            continue
        with path.open("rb") as stream:
            if _chunks_contain_credentials(iter(lambda: stream.read(1024 * 1024), b""), encoded):
                raise ReviewRunnerError(
                    "isolated review clone contains credential material"
                )

    listing = subprocess.run(
        ["git", "rev-list", "--objects", "HEAD"],
        cwd=clone,
        env=git_env,
        check=True,
        capture_output=True,
    ).stdout
    object_ids = []
    for line in listing.splitlines():
        object_id = line.split(b" ", 1)[0]
        if re.fullmatch(rb"[0-9a-fA-F]{40,64}", object_id):
            object_ids.append(object_id)
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=clone,
        env=git_env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None
    try:
        for object_id in object_ids:
            process.stdin.write(object_id + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().rstrip(b"\n")
            fields = header.split()
            if len(fields) != 3 or fields[0].lower() != object_id.lower():
                raise ReviewRunnerError("Git object stream returned a malformed header")
            try:
                size = int(fields[2])
            except ValueError as exc:
                raise ReviewRunnerError(
                    "Git object stream returned a malformed size"
                ) from exc
            found = _chunks_contain_credentials(
                _bounded_chunks(process.stdout, size), encoded
            )
            if process.stdout.read(1) != b"\n":
                raise ReviewRunnerError("Git object stream returned a malformed trailer")
            if found:
                raise ReviewRunnerError(
                    "review commit history contains credential material"
                )
        process.stdin.close()
        stderr = process.stderr.read()
        if process.wait() != 0:
            raise ReviewRunnerError(
                "cannot inspect review commit history for credential material: "
                + stderr.decode("utf-8", errors="replace").strip()
            )
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            try:
                stream.close()
            except OSError:
                pass


def _prompt(packet_text: str, base: str, head: str, canary: Path) -> str:
    canary_command = f"test ! -r {shlex.quote(str(canary))}"
    return f"""Act as the stateless independent final reviewer for this task. This is a
read-only audit of HEAD {head} against base {base}. Work only in the current isolated
repository. Do not access any source-repository path mentioned as provenance in the
packet. Do not edit, create commits, invoke external models, use web/MCP/apps/plugins,
or delegate. Treat the packet as complete task context and do not infer the writer's
reasoning or desired verdict.

Before inspecting the change, run exactly `{canary_command}` as the first command. A
nonzero result means the credential boundary failed: stop without reading any credential.
Then run exactly `git diff {base}..{head}` as the first repository command. Additional
read-only inspection may follow; do not issue a verdict from the packet alone.

Use the native review output format. Prioritize material correctness, security,
behavior regressions, contract drift, and missing tests. In each finding, identify
the violated acceptance criterion, concrete evidence, and the smallest reproduction or
verification command. Do not report style preferences without material impact. Use the
overall explanation for residual risk when there are no actionable findings. Never say
a command ran unless you observed it.

--- REVIEW PACKET START ---
{packet_text.rstrip()}
--- REVIEW PACKET END ---
"""


def _field_values(text: str, label: str, *, bullet: bool = False) -> list[str]:
    marker = r"[ \t]*-[ \t]+" if bullet else ""
    pattern = re.compile(
        rf"^{marker}{re.escape(label)}:[ \t]*(.*)$", re.IGNORECASE
    )
    values = []
    for line in text.splitlines():
        match = pattern.fullmatch(line)
        if match:
            value = match.group(1).strip()
            if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
                value = value[1:-1]
            values.append(value)
    return values


def _validate_task_contract(
    data: bytes, base: str, repo: Path
) -> tuple[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReviewRunnerError("task contract must be valid UTF-8") from exc
    required = (
        "objective",
        "acceptance",
        "exclusions",
        "baseline",
        "repository/worktree",
        "goal thread id",
        "goal objective sha256",
        "verification",
        "stop conditions",
    )
    if (
        not text.strip()
        or text != text.rstrip() + "\n"
        or any(len(_field_values(text, label)) != 1 for label in required)
        or any(not _field_values(text, label)[0] for label in required)
        or _field_values(text, "baseline") != [base]
        or _field_values(text, "repository/worktree") != [str(repo)]
    ):
        raise ReviewRunnerError("task contract is incomplete or non-canonical")
    goal_id = _field_values(text, "goal thread id")[0]
    goal_hash = _field_values(text, "goal objective sha256")[0]
    if (goal_id.casefold() == "none") != (goal_hash.casefold() == "none") or (
        goal_id.casefold() != "none" and not re.fullmatch(r"[0-9a-f]{64}", goal_hash)
    ):
        raise ReviewRunnerError("task contract Goal binding is non-canonical")
    return text, _sha256(data)


def _validate_packet(
    packet_text: str,
    base: str,
    head: str,
    repo: Path,
    contract_text: str,
    contract_sha256: str,
) -> None:
    header = packet_text.split(TASK_CONTRACT_START, 1)[0]
    fields = {
        label: _field_values(header, label, bullet=True)
        for label in (
            "objective",
            "repository root",
            "base commit",
            "head commit",
            "task contract sha256",
            "acceptance",
            "applicable instructions",
            "changed paths",
            "verification receipt",
            "scope exclusions",
            "output contract",
        )
    }
    contract_block = (
        f"{TASK_CONTRACT_START}\n{contract_text.rstrip()}\n{TASK_CONTRACT_END}"
    )
    if (
        not packet_text.strip()
        or any(len(values) != 1 or not values[0] for values in fields.values())
        or fields["repository root"] != [str(repo)]
        or fields["base commit"] != [base]
        or fields["head commit"] != [head]
        or fields["task contract sha256"] != [contract_sha256]
        or packet_text.count(TASK_CONTRACT_START) != 1
        or packet_text.count(TASK_CONTRACT_END) != 1
        or packet_text.count(contract_block) != 1
    ):
        raise ReviewRunnerError(
            "review packet is stale, incomplete, duplicated, or non-canonical"
        )


def _profile_bytes(prompt: str, alias_dir: Path) -> bytes:
    # JSON strings are valid TOML basic strings and safely escape newlines and quotes.
    return f"""developer_instructions = {json.dumps(prompt, ensure_ascii=False)}
default_permissions = "native-review"
allow_login_shell = false

[shell_environment_policy]
inherit = "none"
set = {{ PATH = {json.dumps(f"{alias_dir}:/usr/local/bin:/usr/bin:/bin")}, HOME = "/nonexistent", LANG = "C.UTF-8", GIT_CONFIG_NOSYSTEM = "1", GIT_CONFIG_GLOBAL = "/dev/null", GIT_TERMINAL_PROMPT = "0", GIT_LFS_SKIP_SMUDGE = "1" }}
ignore_default_excludes = false

[permissions.native-review]
description = "Read only the isolated review workspace and minimal runtime paths."

[permissions.native-review.filesystem]
":minimal" = "read"
{json.dumps(str(alias_dir))} = "read"

[permissions.native-review.filesystem.":workspace_roots"]
"." = "read"

[permissions.native-review.network]
enabled = false
""".encode("utf-8")


def _command(codex_binary: Path, clone: Path, base: str) -> list[str]:
    trust_override = f'projects.{json.dumps(str(clone))}.trust_level="untrusted"'
    command = [
        str(codex_binary),
        "exec",
        "review",
        "--json",
        "--strict-config",
        "--ignore-rules",
        "-m",
        MODEL,
        "-c",
        f'model_reasoning_effort="{EFFORT}"',
        "-c",
        f'approval_policy="{APPROVAL}"',
        "-c",
        "project_doc_max_bytes=0",
        "-c",
        'web_search="disabled"',
        "-c",
        "tools.web_search=false",
        "-c",
        trust_override,
    ]
    for feature in (
        "plugins",
        "apps",
        "hooks",
        "multi_agent",
        "browser_use",
        "browser_use_external",
        "computer_use",
        "image_generation",
    ):
        command.extend(("--disable", feature))
    command.extend(("--base", base))
    return command


def _profile_preflight_command(
    codex_binary: Path,
    clone: Path,
    codex_home: Path,
    credential_dir: Path,
    canary: Path,
    alias_dir: Path,
    forbidden_paths: Iterable[Path],
    network_port: int,
) -> list[str]:
    denied = [
        canary,
        credential_dir / "auth.json",
        codex_home / "auth.json",
        codex_home / "config.toml",
        *forbidden_paths,
    ]
    checks = [f"test ! -r {shlex.quote(str(path))}" for path in denied]
    checks.extend(
        (
            f"test -r {shlex.quote(str(clone / '.git/HEAD'))}",
            f"test -x {shlex.quote(str(alias_dir / 'codex-linux-sandbox'))}",
            _network_probe_clause(network_port),
        )
    )
    return [
        str(codex_binary),
        "sandbox",
        "-P",
        "native-review",
        "-C",
        str(clone),
        "/bin/sh",
        "-c",
        " && ".join(checks),
    ]


def _network_probe_clause(network_port: int) -> str:
    script = (
        "import errno,socket,sys\n"
        "try:\n"
        "    probe=socket.socket()\n"
        "    probe.settimeout(.2)\n"
        f"    result=probe.connect_ex(('127.0.0.1',{network_port}))\n"
        "except OSError as exc:\n"
        "    sys.exit(0 if exc.errno in (errno.EACCES,errno.EPERM) else 2)\n"
        "sys.exit(0 if result else 1)\n"
    )
    return shlex.join(["python3", "-c", script])


def _parse_events(data: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for number, line in enumerate(data.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except ValueError as exc:
            raise ReviewRunnerError(
                f"review stdout is not JSONL at line {number}: {exc}"
            ) from exc
        if not isinstance(parsed, dict):
            raise ReviewRunnerError(f"review stdout line {number} is not a JSON object")
        events.append(parsed)
    return events


def _final_message(events: Iterable[dict[str, Any]]) -> str:
    messages: list[str] = []
    for event in events:
        if event.get("type") != "item.completed":
            continue
        item = event.get("item", {})
        if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            messages.append(item["text"])
    if not messages:
        raise ReviewRunnerError("review produced no final agent message")
    final = messages[-1].strip()
    if not final:
        raise ReviewRunnerError("review produced an empty final agent message")
    return final + "\n"


def _read_rollout(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except ValueError as exc:
            raise ReviewRunnerError(
                f"invalid rollout JSONL {path}:{number}: {exc}"
            ) from exc
        if isinstance(record, dict):
            records.append(record)
    return records


def _session_meta(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    metas = [
        record.get("payload", {})
        for record in records
        if record.get("type") == "session_meta"
    ]
    if len(metas) != 1:
        raise ReviewRunnerError(f"expected one session_meta record, found {len(metas)}")
    return metas[0]


def _rollouts(codex_home: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    paths = sorted((codex_home / "sessions").rglob("*.jsonl"))
    if len(paths) != 2:
        raise ReviewRunnerError(
            f"expected one outer and one native review rollout, found {len(paths)}"
        )
    outer: list[list[dict[str, Any]]] = []
    reviewers: list[list[dict[str, Any]]] = []
    for path in paths:
        records = _read_rollout(path)
        source = _session_meta(records).get("source")
        if source == "exec":
            outer.append(records)
        elif isinstance(source, dict) and source.get("subagent") == "review":
            reviewers.append(records)
        else:
            raise ReviewRunnerError(f"unexpected rollout source in {path}: {source!r}")
    if len(outer) != 1 or len(reviewers) != 1:
        raise ReviewRunnerError(
            f"expected one outer and one native review rollout; got {len(outer)} and {len(reviewers)}"
        )
    outer_meta = _session_meta(outer[0])
    reviewer_meta = _session_meta(reviewers[0])
    outer_id = outer_meta.get("id") or outer_meta.get("session_id")
    reviewer_id = reviewer_meta.get("id") or reviewer_meta.get("session_id")
    parent_id = reviewer_meta.get("parent_thread_id")
    valid_parent_ids = {outer_id, outer_meta.get("session_id")}
    if (
        not isinstance(outer_id, str)
        or not outer_id
        or not isinstance(reviewer_id, str)
        or not reviewer_id
        or reviewer_id == outer_id
        or parent_id not in valid_parent_ids
    ):
        raise ReviewRunnerError(
            "native review rollout is not a distinct child of the fresh outer exec"
        )
    return outer[0], reviewers[0]


def _contains_substring(value: Any, needle: str) -> bool:
    if isinstance(value, str) and needle in value:
        return True
    if isinstance(value, dict):
        return any(_contains_substring(child, needle) for child in value.values())
    if isinstance(value, list):
        return any(_contains_substring(child, needle) for child in value)
    return False


def _assistant_texts(records: Iterable[dict[str, Any]]) -> list[str]:
    texts: list[str] = []
    for record in records:
        payload = record.get("payload", {})
        if (
            record.get("type") != "response_item"
            or payload.get("type") != "message"
            or payload.get("role") != "assistant"
        ):
            continue
        content = payload.get("content", [])
        if isinstance(content, list):
            combined = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and isinstance(item.get("text"), str)
            ).strip()
            if combined:
                texts.append(combined)
    return texts


def _verify_prompt_and_verdicts(
    outer: list[dict[str, Any]],
    reviewer: list[dict[str, Any]],
    prompt: str,
    review_text: str,
) -> dict[str, Any]:
    if _contains_substring(outer, prompt):
        raise ReviewRunnerError("review packet leaked into the outer control rollout")
    injected = 0
    for record in reviewer:
        payload = record.get("payload", {})
        if (
            record.get("type") == "response_item"
            and payload.get("type") == "message"
            and payload.get("role") == "developer"
        ):
            injected += sum(
                1
                for item in payload.get("content", [])
                if isinstance(item, dict)
                and item.get("type") == "input_text"
                and item.get("text") == prompt
            )
    if injected != 1:
        raise ReviewRunnerError(
            "review packet was not injected once as a developer instruction"
        )
    outer_messages = _assistant_texts(outer)
    reviewer_messages = _assistant_texts(reviewer)
    if not outer_messages or outer_messages[-1] != review_text.strip():
        raise ReviewRunnerError("event review is not the outer rollout's final verdict")
    if not reviewer_messages:
        raise ReviewRunnerError("native reviewer produced no final verdict")
    try:
        verdict = json.loads(reviewer_messages[-1])
    except ValueError as exc:
        raise ReviewRunnerError("native reviewer verdict is not JSON") from exc
    if (
        not isinstance(verdict, dict)
        or not isinstance(verdict.get("findings"), list)
        or verdict.get("overall_correctness")
        not in {"patch is correct", "patch is incorrect"}
        or not isinstance(verdict.get("overall_explanation"), str)
        or not verdict["overall_explanation"].strip()
        or isinstance(verdict.get("overall_confidence_score"), bool)
        or not isinstance(verdict.get("overall_confidence_score"), (int, float))
        or not 0 <= verdict["overall_confidence_score"] <= 1
    ):
        raise ReviewRunnerError("native reviewer verdict schema is invalid")
    if bool(verdict["findings"]) != (
        verdict["overall_correctness"] == "patch is incorrect"
    ):
        raise ReviewRunnerError("native reviewer verdict is internally inconsistent")
    if not verdict["findings"] and review_text.strip() != verdict[
        "overall_explanation"
    ].strip():
        raise ReviewRunnerError("outer no-finding verdict differs from native reviewer")
    for finding in verdict["findings"]:
        location = finding.get("code_location") if isinstance(finding, dict) else None
        line_range = location.get("line_range") if isinstance(location, dict) else None
        priority = finding.get("priority") if isinstance(finding, dict) else None
        confidence = (
            finding.get("confidence_score") if isinstance(finding, dict) else None
        )
        if (
            not isinstance(finding, dict)
            or not isinstance(finding.get("title"), str)
            or not finding["title"].strip()
            or not isinstance(finding.get("body"), str)
            or not finding["body"].strip()
            or isinstance(priority, bool)
            or not isinstance(priority, int)
            or priority not in range(4)
            or isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0 <= confidence <= 1
            or not isinstance(location, dict)
            or not isinstance(location.get("absolute_file_path"), str)
            or not Path(location["absolute_file_path"]).is_absolute()
            or not isinstance(line_range, dict)
            or isinstance(line_range.get("start"), bool)
            or isinstance(line_range.get("end"), bool)
            or not isinstance(line_range.get("start"), int)
            or not isinstance(line_range.get("end"), int)
            or line_range["start"] < 1
            or line_range["end"] < line_range["start"]
            or (
                finding["title"].strip() not in review_text
                and finding["body"].strip() not in review_text
            )
        ):
            raise ReviewRunnerError(
                "outer review omitted or malformed a native reviewer finding"
            )
    return verdict


def _verify_event_binding(
    events: list[dict[str, Any]],
    outer: list[dict[str, Any]],
    canary: Path,
    base: str,
    head: str,
) -> None:
    thread_ids = [
        event.get("thread_id")
        for event in events
        if event.get("type") == "thread.started"
    ]
    outer_id = _session_meta(outer).get("session_id")
    if thread_ids != [outer_id]:
        raise ReviewRunnerError(
            f"event stream is not bound to outer review thread {outer_id}"
        )
    if not any(event.get("type") == "turn.completed" for event in events):
        raise ReviewRunnerError("review event stream has no completed turn")
    commands = [
        (event.get("type"), event.get("item", {}))
        for event in events
        if event.get("type") in {"item.started", "item.completed"}
        and event.get("item", {}).get("type") == "command_execution"
    ]
    canary_text = f"test ! -r {shlex.quote(str(canary))}"

    def shell_payload(command: str) -> str:
        try:
            words = shlex.split(command)
        except ValueError:
            return ""
        if len(words) == 3 and words[0] in {
            "/bin/bash",
            "/usr/bin/bash",
            "/bin/sh",
            "/usr/bin/sh",
        } and words[1] == "-c":
            return words[2]
        return command.strip()

    expected_diff = f"git diff {base}..{head}"
    if len(commands) < 4:
        raise ReviewRunnerError("review command lifecycle evidence is incomplete")
    first = commands[:4]
    if [kind for kind, _ in first] != [
        "item.started",
        "item.completed",
        "item.started",
        "item.completed",
    ]:
        raise ReviewRunnerError("review commands did not start and complete in order")
    canary_started, canary_completed = first[0][1], first[1][1]
    diff_started, diff_completed = first[2][1], first[3][1]
    if (
        canary_started.get("id") != canary_completed.get("id")
        or shell_payload(str(canary_started.get("command", ""))) != canary_text
        or shell_payload(str(canary_completed.get("command", ""))) != canary_text
        or canary_completed.get("exit_code") != 0
    ):
        raise ReviewRunnerError(
            "review did not prove the credential directory is unreadable first"
        )
    if (
        diff_started.get("id") != diff_completed.get("id")
        or shell_payload(str(diff_started.get("command", ""))) != expected_diff
        or shell_payload(str(diff_completed.get("command", ""))) != expected_diff
        or diff_completed.get("exit_code") != 0
        or "diff --git " not in str(diff_completed.get("aggregated_output", ""))
    ):
        raise ReviewRunnerError(
            "review did not inspect the exact non-empty base-to-head diff second"
        )


def _verify_forbidden_tools(records: Iterable[dict[str, Any]]) -> None:
    nested_markers = (
        "tools.web__",
        "tools.mcp__",
        "tools.list_mcp_",
        "tools.read_mcp_",
        "tools.image_gen__",
        "tools.request_plugin_install",
        "tools.spawn_agent",
    )
    forbidden_tokens = (
        "web",
        "mcp",
        "spawn_agent",
        "image_gen",
        "image_generation",
        "request_plugin_install",
        "browser",
        "computer",
        "plugin",
        "app",
        "hook",
        "multi_agent",
    )
    forbidden_event_types = {
        "web_search",
        "web_search_call",
        "mcp_tool_call",
        "mcp_call",
        "image_generation",
        "collab_agent_tool_call",
        "agent_tool_call",
        "subagent_tool_call",
        "dynamic_tool_call",
        "browser_use",
        "computer_use",
    }

    def mappings(value: Any) -> Iterable[dict[str, Any]]:
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from mappings(child)
        elif isinstance(value, list):
            for child in value:
                yield from mappings(child)

    for record in mappings(list(records)):
        event_type = str(record.get("type") or "").lower()
        if event_type in forbidden_event_types:
            raise ReviewRunnerError(f"review used forbidden tool event {event_type}")
        if event_type not in {"custom_tool_call", "function_call"}:
            continue
        name = str(record.get("name", "")).lower()
        namespace = str(record.get("namespace", "")).lower()
        if any(
            token in name or token in namespace
            for token in forbidden_tokens
        ):
            raise ReviewRunnerError(
                f"review used forbidden external tool {namespace}:{name}"
            )
        tool_input = str(record.get("input") or record.get("arguments") or "")
        if any(marker in tool_input for marker in nested_markers):
            raise ReviewRunnerError(
                f"review invoked a forbidden nested tool through {name}"
            )


def _verify_context(
    events: list[dict[str, Any]],
    outer: list[dict[str, Any]],
    reviewer: list[dict[str, Any]],
    clone: Path,
    alias_dir: Path,
    binary: Path,
) -> dict[str, Any]:
    if _session_meta(outer).get("cwd") != str(clone) or _session_meta(reviewer).get(
        "cwd"
    ) != str(clone):
        raise ReviewRunnerError(
            "review rollouts were not created in the isolated clone"
        )
    contexts = [
        record.get("payload", {})
        for record in reviewer
        if record.get("type") == "turn_context"
    ]
    if not contexts:
        raise ReviewRunnerError("native review rollout contains no turn_context")
    expected = {
        "model": MODEL,
        "effort": EFFORT,
        "sandbox": SANDBOX,
        "approval": APPROVAL,
        "network": NETWORK,
    }
    for context in contexts:
        effort = context.get("effort") or context.get("collaboration_mode", {}).get(
            "settings", {}
        ).get("reasoning_effort")
        actual = {
            "model": context.get("model"),
            "effort": effort,
            "sandbox": context.get("sandbox_policy", {}).get("type"),
            "approval": context.get("approval_policy"),
            "network": context.get("permission_profile", {}).get("network"),
        }
        if actual != expected:
            raise ReviewRunnerError(
                f"native review runtime mismatch: expected {expected}, got {actual}"
            )
        if context.get("multi_agent_version") not in {None, "disabled"}:
            raise ReviewRunnerError("native reviewer unexpectedly enabled multi-agent")
        if context.get("cwd") != str(clone) or context.get("workspace_roots") != [
            str(clone)
        ]:
            raise ReviewRunnerError(
                "native reviewer is not confined to the isolated clone root"
            )
        profile = context.get("permission_profile", {})
        filesystem = profile.get("file_system", {}) if isinstance(profile, dict) else {}
        if profile.get("type") != "managed" or filesystem.get("type") != "restricted":
            raise ReviewRunnerError(
                "native reviewer did not apply the restricted permission profile"
            )
        entries = filesystem.get("entries", [])
        if not isinstance(entries, list):
            raise ReviewRunnerError("native reviewer permission entries are malformed")
        allowed_paths = {str(clone), str(alias_dir)}
        runtime_zsh = binary.parent.parent / "codex-resources/zsh/bin/zsh"
        if runtime_zsh.is_file():
            allowed_paths.add(str(runtime_zsh))
        saw_clone = False
        saw_minimal = False
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("access") != "read":
                raise ReviewRunnerError(
                    "native reviewer retained an unexpected filesystem permission"
                )
            path = entry.get("path", {})
            if not isinstance(path, dict):
                raise ReviewRunnerError("native reviewer permission path is malformed")
            if path.get("type") == "special":
                value = path.get("value", {})
                if not isinstance(value, dict) or value.get("kind") != "minimal":
                    raise ReviewRunnerError(
                        "native reviewer retained an unexpected special filesystem root"
                    )
                saw_minimal = True
                continue
            if path.get("type") != "path" or path.get("path") not in allowed_paths:
                raise ReviewRunnerError(
                    "native reviewer retained an unexpected host filesystem path"
                )
            saw_clone = saw_clone or path.get("path") == str(clone)
        if not saw_clone or not saw_minimal:
            raise ReviewRunnerError(
                "native reviewer permission profile omitted required restricted roots"
            )
    _verify_forbidden_tools([*events, *outer, *reviewer])
    return {**expected, "permission_profile": contexts[-1].get("permission_profile")}


def _git_environment(home: Path) -> dict[str, str]:
    return {
        "HOME": str(home),
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_LFS_SKIP_SMUDGE": "1",
        "GIT_NO_LAZY_FETCH": "1",
    }


def _codex_environment(
    home: Path, codex_home: Path, runtime: Path, alias_dir: Path
) -> dict[str, str]:
    environment = _git_environment(home)
    environment.update(
        {
            "HOME": str(home),
            "CODEX_HOME": str(codex_home),
            "XDG_CONFIG_HOME": str(runtime / "xdg/config"),
            "XDG_DATA_HOME": str(runtime / "xdg/data"),
            "XDG_CACHE_HOME": str(runtime / "xdg/cache"),
            "XDG_STATE_HOME": str(runtime / "xdg/state"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_LFS_SKIP_SMUDGE": "1",
            "PATH": f"{alias_dir}:/usr/local/bin:/usr/bin:/bin",
        }
    )
    return environment


def _resolve_binary(binary: Path) -> tuple[Path, str]:
    candidate = shutil.which(str(binary)) if binary.parent == Path(".") else str(binary)
    if not candidate:
        raise ReviewRunnerError(f"cannot locate Codex binary: {binary}")
    resolved = Path(candidate).expanduser().resolve()
    if not resolved.is_file():
        raise ReviewRunnerError(f"Codex binary is not a regular file: {resolved}")
    return resolved, _file_sha256(resolved)


def _containment_command(unshare: Path, command: list[str]) -> list[str]:
    return [
        str(unshare),
        "--user",
        "--map-root-user",
        "--pid",
        "--fork",
        "--mount-proc",
        "--kill-child=SIGKILL",
        "--",
        *command,
    ]


def _resolve_containment_binary() -> Path:
    if sys.platform != "linux":
        raise ReviewRunnerError("native review process containment requires Linux")
    unshare, _ = _resolve_binary(Path("/usr/bin/unshare"))
    try:
        probe = subprocess.run(
            _containment_command(unshare, ["/bin/true"]),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        raise ReviewRunnerError("PID namespace containment preflight timed out") from exc
    if probe.returncode:
        raise ReviewRunnerError("PID namespace containment is unavailable")
    return unshare


def _private_runtime_root() -> Path:
    root = Path(f"/run/user/{os.geteuid()}")
    if root.is_symlink() or not root.is_dir():
        raise ReviewRunnerError("private runtime tmpfs is unavailable")
    metadata = root.stat()
    if metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) & 0o077:
        raise ReviewRunnerError("private runtime directory ownership or mode is unsafe")
    mount_type = None
    best_length = -1
    try:
        for line in Path("/proc/self/mountinfo").read_text().splitlines():
            left, right = line.split(" - ", 1)
            mount = Path(left.split()[4].replace("\\040", " ")).resolve()
            if (root == mount or root.is_relative_to(mount)) and len(str(mount)) > best_length:
                mount_type = right.split()[0]
                best_length = len(str(mount))
    except (OSError, ValueError, IndexError) as exc:
        raise ReviewRunnerError("cannot verify private runtime filesystem") from exc
    if mount_type != "tmpfs":
        raise ReviewRunnerError("private runtime directory is not backed by tmpfs")
    return root


def _pin_executable(source: Path, destination: Path) -> Path:
    try:
        os.link(source, destination)
    except OSError as exc:
        if exc.errno not in {errno.EXDEV, errno.EPERM, errno.EACCES}:
            raise
        shutil.copy2(source, destination)
    return destination


def _prepare_aliases(directory: Path, binary: Path) -> Path:
    directory.mkdir(parents=True, mode=0o700)
    primary = directory / "codex-linux-sandbox"
    _pin_executable(binary, primary)
    for name in ("codex", "codex-execve-wrapper", "apply_patch"):
        os.link(primary, directory / name)
    return directory / "codex"


def _replace_path(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [_replace_path(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: _replace_path(item, old, new) for key, item in value.items()}
    return value


def _run_process(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float,
) -> subprocess.CompletedProcess[str]:
    expected_parent = os.getpid()

    def arm_parent_death_signal() -> None:
        if _LIBC.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
            os._exit(126)
        if os.getppid() != expected_parent:
            os.kill(os.getpid(), signal.SIGKILL)

    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=(os.name == "posix"),
        preexec_fn=arm_parent_death_signal if sys.platform == "linux" else None,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:  # pragma: no cover - Windows fallback
            process.kill()
        stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(
            command, timeout, output=stdout, stderr=stderr
        ) from exc
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def _records_hash(records: Iterable[dict[str, Any]]) -> str:
    canonical = b"".join(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        for record in records
    )
    return _sha256(canonical)


def _prepare_clone(
    repo: Path, clone: Path, bundle: Path, git_env: dict[str, str]
) -> None:
    bundle_result = subprocess.run(
        ["git", "bundle", "create", str(bundle), "HEAD"],
        cwd=repo,
        env=git_env,
        capture_output=True,
        text=True,
    )
    if bundle_result.returncode:
        detail = bundle_result.stderr.strip() or bundle_result.stdout.strip()
        raise ReviewRunnerError(f"failed to create head-only review bundle: {detail}")
    clone_result = subprocess.run(
        ["git", "clone", "--quiet", "--no-tags", str(bundle), str(clone)],
        env=git_env,
        capture_output=True,
        text=True,
    )
    if clone_result.returncode:
        detail = clone_result.stderr.strip() or clone_result.stdout.strip()
        raise ReviewRunnerError(f"failed to clone head-only review bundle: {detail}")
    _git(clone, "checkout", "--quiet", "--detach", "HEAD", env=git_env)
    _git(clone, "remote", "remove", "origin", env=git_env)


def _decode_timeout_stream(value: str | bytes | None) -> bytes:
    if value is None:
        return b""
    return value if isinstance(value, bytes) else value.encode("utf-8")


def run_review(
    *,
    repo: Path,
    base: str,
    head: str,
    packet: Path,
    task_contract: Path,
    output: Path,
    source_codex_home: Path,
    codex_binary: Path = Path("codex"),
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    repo = repo.expanduser().resolve()
    packet_input = packet.expanduser().absolute()
    contract_input = task_contract.expanduser().absolute()
    if packet_input.is_symlink() or contract_input.is_symlink():
        raise ReviewRunnerError("packet and task contract must not be symlinks")
    packet = packet_input.resolve()
    task_contract = contract_input.resolve()
    output_input = output.expanduser().absolute()
    if output_input.is_symlink():
        raise ReviewRunnerError("review output must not be a symlink")
    output = output_input.resolve()
    source_codex_home = source_codex_home.expanduser().resolve()
    source_git_env = _git_environment(Path("/nonexistent"))
    worktree_root = Path(
        _git(repo, "rev-parse", "--show-toplevel", env=source_git_env).stdout.strip()
    ).resolve()
    if repo != worktree_root:
        raise ReviewRunnerError("--repo must name the Git worktree root")
    runner_path = Path(__file__).resolve()
    runner_sha256 = _file_sha256(runner_path)
    resolved_binary, source_binary_sha256 = _resolve_binary(codex_binary)
    containment_binary = _resolve_containment_binary()
    source_containment_sha256 = _file_sha256(containment_binary)
    if timeout_seconds <= 0:
        raise ReviewRunnerError("timeout_seconds must be positive")
    if output == repo or output.is_relative_to(repo):
        raise ReviewRunnerError("review output must be outside the source repository")
    if packet.is_relative_to(repo) or task_contract.is_relative_to(repo):
        raise ReviewRunnerError("packet and task contract must be outside the repository")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ReviewRunnerError(f"output directory is not an empty directory: {output}")
    if _status(repo, source_git_env):
        raise ReviewRunnerError(
            f"source repository must be clean before review: {repo}"
        )
    masked_paths = _masked_index_paths(repo, source_git_env)
    if masked_paths:
        raise ReviewRunnerError(
            "source index masks tracked paths with assume-unchanged/skip-worktree: "
            + ", ".join(masked_paths[:5])
        )
    resolved_base = _resolve_commit(repo, base, source_git_env)
    resolved_head = _resolve_commit(repo, head, source_git_env)
    if _resolve_commit(repo, "HEAD", source_git_env) != resolved_head:
        raise ReviewRunnerError(
            "source repository HEAD does not match the requested review head"
        )
    ancestor = _git(
        repo,
        "merge-base",
        "--is-ancestor",
        resolved_base,
        resolved_head,
        check=False,
        env=source_git_env,
    )
    if ancestor.returncode != 0:
        raise ReviewRunnerError("review base must be an ancestor of the requested head")
    changed = _git(
        repo,
        "diff",
        "--quiet",
        resolved_base,
        resolved_head,
        "--",
        check=False,
        env=source_git_env,
    )
    if changed.returncode == 0:
        raise ReviewRunnerError("review range is empty; base must be the task baseline")
    if changed.returncode != 1:
        raise ReviewRunnerError(
            "cannot determine whether the review range contains changes"
        )
    try:
        contract_data = _read_private(task_contract, "task contract")
        packet_data = _read_private(packet, "review packet")
        contract_text, contract_sha256 = _validate_task_contract(
            contract_data, resolved_base, repo
        )
        packet_text = packet_data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ReviewRunnerError(
            f"cannot read task contract or UTF-8 review packet: {exc}"
        ) from exc
    _validate_packet(
        packet_text,
        resolved_base,
        resolved_head,
        repo,
        contract_text,
        contract_sha256,
    )
    auth_path = source_codex_home / "auth.json"
    try:
        auth_data = auth_path.read_bytes()
    except OSError as exc:
        raise ReviewRunnerError(
            f"required source file is missing: {auth_path}"
        ) from exc
    credentials = _credential_strings(auth_data)
    _, packet_leak = _redact_credentials(packet_text, credentials)
    if packet_leak:
        raise ReviewRunnerError("review packet contains credential material")

    source_head_before = _resolve_commit(repo, "HEAD", source_git_env)
    source_hash_before = _git_visible_hash(repo, source_git_env)
    runtime_root = _private_runtime_root()
    output.mkdir(parents=True, exist_ok=True)
    output.chmod(0o700)

    with tempfile.TemporaryDirectory(
        prefix="native-codex-loop-review-"
    ) as runtime_name, tempfile.TemporaryDirectory(
        prefix="native-codex-loop-credentials-", dir=runtime_root
    ) as credential_name:
        runtime = Path(runtime_name)
        home = runtime / "home"
        codex_home = runtime / "codex"
        credential_dir = Path(credential_name)
        alias_dir = runtime / "bin"
        clone = runtime / "review-repo"
        bundle = runtime / "review.bundle"
        for directory in (home, codex_home):
            directory.mkdir(parents=True)
            directory.chmod(0o700)
        credential_dir.chmod(0o700)
        pinned_binary = _prepare_aliases(alias_dir, resolved_binary)
        pinned_containment = _pin_executable(
            containment_binary, runtime / "unshare"
        )
        binary_sha256 = _file_sha256(pinned_binary)
        containment_sha256 = _file_sha256(pinned_containment)
        if (
            binary_sha256 != source_binary_sha256
            or containment_sha256 != source_containment_sha256
        ):
            raise ReviewRunnerError("failed to pin executable identity")
        _write(credential_dir / "auth.json", auth_data, 0o600)
        (codex_home / "auth.json").symlink_to(credential_dir / "auth.json")
        canary = credential_dir / "sandbox-canary"
        _write(canary, b"must remain unreadable to reviewer tools\n", 0o600)
        models_cache = source_codex_home / "models_cache.json"
        if models_cache.is_file():
            _copy_private(models_cache, codex_home / "models_cache.json")

        git_env = _git_environment(home)
        _prepare_clone(repo, clone, bundle, git_env)
        _scan_clone_for_credentials(clone, credentials, git_env)
        if _resolve_commit(clone, "HEAD", git_env) != resolved_head or _status(
            clone, git_env
        ):
            raise ReviewRunnerError(
                "isolated review clone does not match the requested clean head"
            )
        clone_hash_before = _filesystem_hash(clone)
        reviewed_packet = packet_text
        prompt = _prompt(reviewed_packet, resolved_base, resolved_head, canary)
        _write(codex_home / "config.toml", _profile_bytes(prompt, alias_dir), 0o600)
        _write(output / "packet.md", reviewed_packet.encode("utf-8"), 0o600)

        command = _command(pinned_binary, clone, resolved_base)
        environment = _codex_environment(home, codex_home, runtime, alias_dir)
        forbidden_paths = [repo, packet, task_contract, auth_path]
        if models_cache.is_file():
            forbidden_paths.append(models_cache)
        network_probe = socket.socket()
        network_probe.bind(("127.0.0.1", 0))
        network_probe.listen(1)
        preflight_command = _profile_preflight_command(
            pinned_binary,
            clone,
            codex_home,
            credential_dir,
            canary,
            alias_dir,
            forbidden_paths,
            network_probe.getsockname()[1],
        )
        contained_preflight_command = _containment_command(
            pinned_containment, preflight_command
        )
        try:
            preflight = _run_process(
                contained_preflight_command,
                cwd=clone,
                env=environment,
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise ReviewRunnerError(
                "restricted permission profile preflight timed out"
            ) from exc
        finally:
            network_probe.close()
        preflight_stdout, preflight_stdout_leak = _redact_credentials(
            preflight.stdout, credentials
        )
        preflight_stderr, preflight_stderr_leak = _redact_credentials(
            preflight.stderr, credentials
        )
        _write(
            output / "preflight.log",
            (preflight_stdout + preflight_stderr).encode("utf-8"),
            0o600,
        )
        if preflight_stdout_leak or preflight_stderr_leak:
            raise ReviewRunnerError(
                "permission preflight exposed credential material"
            )
        if preflight.returncode:
            raise ReviewRunnerError(
                "restricted permission profile preflight failed closed"
            )
        version_command = _containment_command(
            pinned_containment, [str(pinned_binary), "--version"]
        )
        try:
            version_result = _run_process(
                version_command,
                cwd=clone,
                env=environment,
                timeout=10,
            )
        except subprocess.TimeoutExpired as exc:
            raise ReviewRunnerError("Codex CLI version probe timed out") from exc
        if version_result.returncode:
            raise ReviewRunnerError("cannot determine Codex CLI version")
        version_stdout, version_stdout_leak = _redact_credentials(
            version_result.stdout, credentials
        )
        _, version_stderr_leak = _redact_credentials(
            version_result.stderr, credentials
        )
        cli_version = version_stdout.strip()
        if version_stdout_leak or version_stderr_leak:
            raise ReviewRunnerError("Codex version probe exposed credential material")
        if (
            len(cli_version) > 128
            or "\n" in cli_version
            or not re.fullmatch(r"codex-cli [0-9A-Za-z.+_-]+", cli_version)
        ):
            raise ReviewRunnerError("Codex CLI version output is malformed")
        contained_command = _containment_command(pinned_containment, command)
        try:
            completed = _run_process(
                contained_command,
                cwd=clone,
                env=environment,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            timeout_stdout = _decode_timeout_stream(exc.stdout).decode(
                "utf-8", errors="replace"
            )
            timeout_stderr = _decode_timeout_stream(exc.stderr).decode(
                "utf-8", errors="replace"
            )
            timeout_stdout, _ = _redact_credentials(timeout_stdout, credentials)
            timeout_stderr, _ = _redact_credentials(timeout_stderr, credentials)
            _write(output / "events.jsonl", timeout_stdout.encode("utf-8"), 0o600)
            _write(output / "stderr.log", timeout_stderr.encode("utf-8"), 0o600)
            raise ReviewRunnerError(
                f"Codex review exceeded timeout of {timeout_seconds:g} seconds"
            ) from exc
        persisted_stdout, stdout_leak = _redact_credentials(
            completed.stdout, credentials
        )
        persisted_stderr, stderr_leak = _redact_credentials(
            completed.stderr, credentials
        )
        _write(output / "events.jsonl", persisted_stdout.encode("utf-8"), 0o600)
        _write(output / "stderr.log", persisted_stderr.encode("utf-8"), 0o600)
        if stdout_leak or stderr_leak:
            raise ReviewRunnerError(
                "review exposed credential material; persisted logs were redacted"
            )
        if completed.returncode:
            raise ReviewRunnerError(
                f"Codex review exited {completed.returncode}; inspect {output / 'stderr.log'}"
            )

        events = _parse_events(persisted_stdout)
        raw_review_text = _final_message(events)
        outer, reviewer = _rollouts(codex_home)
        rollout_text = json.dumps([outer, reviewer], ensure_ascii=False)
        _, rollout_leak = _redact_credentials(rollout_text, credentials)
        if rollout_leak:
            raise ReviewRunnerError("review rollout exposed credential material")
        _verify_event_binding(
            events, outer, canary, resolved_base, resolved_head
        )
        verdict = _verify_prompt_and_verdicts(
            outer, reviewer, prompt, raw_review_text
        )
        public_verdict = _replace_path(verdict, str(clone), str(repo))
        review_text = json.dumps(
            public_verdict, indent=2, sort_keys=True, ensure_ascii=False
        ) + "\n"
        actual = _verify_context(
            events, outer, reviewer, clone, alias_dir, resolved_binary
        )

        clone_status_after = _status(clone, git_env)
        clone_head_after = _resolve_commit(clone, "HEAD", git_env)
        clone_hash_after = _filesystem_hash(clone)
        if (
            clone_status_after
            or clone_head_after != resolved_head
            or _masked_index_paths(clone, git_env)
            or clone_hash_after != clone_hash_before
        ):
            raise ReviewRunnerError(
                "isolated review repository changed during read-only review"
            )
        if (
            _file_sha256(pinned_binary) != binary_sha256
            or _file_sha256(pinned_containment) != containment_sha256
        ):
            raise ReviewRunnerError("review executables changed during execution")

    source_hash_after = _git_visible_hash(repo, source_git_env)
    source_head_after = _resolve_commit(repo, "HEAD", source_git_env)
    try:
        contract_after = _read_private(task_contract, "task contract")
        packet_after = _read_private(packet, "review packet")
        runner_after = _file_sha256(runner_path)
    except OSError as exc:
        raise ReviewRunnerError("review inputs changed or disappeared") from exc
    if (
        source_hash_after != source_hash_before
        or source_head_after != source_head_before
        or _status(repo, source_git_env)
        or _masked_index_paths(repo, source_git_env)
        or contract_after != contract_data
        or packet_after != packet_data
        or runner_after != runner_sha256
    ):
        raise ReviewRunnerError("source repository changed during review")

    usage = next(
        (
            event.get("usage", {})
            for event in reversed(events)
            if event.get("type") == "turn.completed"
        ),
        {},
    )
    receipt: dict[str, Any] = {
        "ok": True,
        "base": resolved_base,
        "head": resolved_head,
        "task_contract_sha256": contract_sha256,
        "review_runner_sha256": runner_sha256,
        "source_packet_sha256": _sha256(packet_data),
        "reviewed_packet_sha256": _sha256(reviewed_packet.encode("utf-8")),
        "instruction_sha256": _sha256(prompt.encode("utf-8")),
        "model": actual["model"],
        "effort": actual["effort"],
        "sandbox": actual["sandbox"],
        "approval": actual["approval"],
        "network": actual["network"],
        "permission_profile": actual["permission_profile"],
        "cli_version": cli_version,
        "codex_binary_sha256": binary_sha256,
        "source_codex_binary": str(resolved_binary),
        "source_codex_binary_sha256": source_binary_sha256,
        "command": command,
        "contained_command": contained_command,
        "containment": {
            "binary": str(pinned_containment),
            "binary_sha256": containment_sha256,
            "source_binary": str(containment_binary),
            "source_binary_sha256": source_containment_sha256,
            "mode": "linux-user-pid-mount-namespace",
        },
        "profile_preflight_command": preflight_command,
        "profile_preflight_sha256": _sha256(
            (preflight_stdout + preflight_stderr).encode("utf-8")
        ),
        "source_git_visible_sha256_before": source_hash_before,
        "source_git_visible_sha256_after": source_hash_after,
        "review_tree_sha256_before": clone_hash_before,
        "review_tree_sha256_after": clone_hash_after,
        "events_sha256": _sha256(persisted_stdout.encode("utf-8")),
        "stderr_sha256": _sha256(persisted_stderr.encode("utf-8")),
        "raw_review_sha256": _sha256(raw_review_text.encode("utf-8")),
        "review_sha256": _sha256(review_text.encode("utf-8")),
        "outer_rollout_sha256": _records_hash(outer),
        "review_rollout_sha256": _records_hash(reviewer),
        "proxy_environment_keys": sorted(
            key
            for key in environment
            if key.upper() in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}
        ),
        "usage": usage,
        "review_file": str(output / "review.md"),
    }
    _write(output / "review.md", review_text.encode("utf-8"), 0o600)
    _write(
        output / "receipt.json",
        (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        0o600,
    )
    return receipt


def _load_series(path: Path, repo: Path, base: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ReviewRunnerError(f"review series state is not a regular file: {path}")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReviewRunnerError(
            f"cannot read review series state {path}: {exc}"
        ) from exc
    if not isinstance(state, dict):
        raise ReviewRunnerError(f"review series state must be a JSON object: {path}")
    attempts = state.get("attempts")
    if (
        state.get("schema_version") != SERIES_SCHEMA
        or state.get("repo") != str(repo)
        or state.get("base") != base
        or not isinstance(attempts, list)
    ):
        raise ReviewRunnerError(f"review series identity or schema mismatch: {path}")
    expected_numbers = list(range(1, len(attempts) + 1))
    if [
        item.get("number") for item in attempts if isinstance(item, dict)
    ] != expected_numbers:
        raise ReviewRunnerError(f"review series attempt history is malformed: {path}")
    return state


def canonical_series_path(source_codex_home: Path, repo: Path, base: str) -> Path:
    identity = f"{repo.expanduser().resolve()}\0{base}".encode("utf-8")
    key = hashlib.sha256(identity).hexdigest()
    return (
        source_codex_home.expanduser().resolve()
        / "native-codex-loop/review-series"
        / key
    )


def _ensure_series_directory(series: Path, source_codex_home: Path) -> None:
    current = source_codex_home
    for name in ("native-codex-loop", "review-series", series.name):
        current = current / name
        if current.is_symlink():
            raise ReviewRunnerError(f"review series path is symlinked: {current}")
        if current.exists() and not current.is_dir():
            raise ReviewRunnerError(f"review series path is not a directory: {current}")
        current.mkdir(mode=0o700, exist_ok=True)
        current.chmod(0o700)


def run_series_review(
    *,
    repo: Path,
    base: str,
    head: str,
    packet: Path,
    task_contract: Path,
    source_codex_home: Path,
    codex_binary: Path = Path("codex"),
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    repo = repo.expanduser().resolve()
    source_codex_home = source_codex_home.expanduser().resolve()
    git_env = _git_environment(Path("/nonexistent"))
    resolved_base = _resolve_commit(repo, base, git_env)
    resolved_head = _resolve_commit(repo, head, git_env)
    series = canonical_series_path(source_codex_home, repo, resolved_base)
    _ensure_series_directory(series, source_codex_home)
    lock = series / ".lock"
    state_path = series / "series.json"
    if lock.is_symlink() or state_path.is_symlink():
        raise ReviewRunnerError("review series contains a symlinked control file")
    try:
        descriptor = os.open(
            lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600
        )
        lock_metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(lock_metadata.st_mode)
            or lock_metadata.st_uid != os.geteuid()
            or stat.S_IMODE(lock_metadata.st_mode) & 0o077
            or lock_metadata.st_nlink != 1
        ):
            raise OSError("unsafe review-series lock metadata")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (FileExistsError, BlockingIOError, OSError) as exc:
        try:
            os.close(descriptor)
        except (OSError, UnboundLocalError):
            pass
        raise ReviewRunnerError(
            f"review series is locked or unsafe: {series}"
        ) from exc
    try:
        os.ftruncate(descriptor, 0)
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.fsync(descriptor)
        if state_path.exists():
            state = _load_series(state_path, repo, resolved_base)
        else:
            unexpected = [path for path in series.iterdir() if path != lock]
            if unexpected:
                raise ReviewRunnerError(
                    f"new review series directory is not empty: {series}"
                )
            state = {
                "schema_version": SERIES_SCHEMA,
                "repo": str(repo),
                "base": resolved_base,
                "attempts": [],
            }
        if len(state["attempts"]) >= MAX_REVIEW_ATTEMPTS:
            raise ReviewRunnerError(
                "review series already used both allowed invocations"
            )
        number = len(state["attempts"]) + 1
        output = series / f"attempt-{number}"
        if output.is_symlink() or output.exists():
            raise ReviewRunnerError(f"review attempt output already exists: {output}")
        attempt = {
            "number": number,
            "head": resolved_head,
            "status": "started",
            "started_at": time.time(),
            "output": str(output),
        }
        state["attempts"].append(attempt)
        _atomic_json(state_path, state)
        try:
            receipt = run_review(
                repo=repo,
                base=resolved_base,
                head=resolved_head,
                packet=packet,
                task_contract=task_contract,
                output=output,
                source_codex_home=source_codex_home,
                codex_binary=codex_binary,
                timeout_seconds=timeout_seconds,
            )
        except BaseException as exc:
            attempt.update(
                {
                    "status": "failed",
                    "finished_at": time.time(),
                    "error_type": type(exc).__name__,
                }
            )
            _atomic_json(state_path, state)
            raise
        receipt.update({"attempt": number, "series_file": str(state_path)})
        _atomic_json(output / "receipt.json", receipt)
        attempt.update(
            {
                "status": "succeeded",
                "finished_at": time.time(),
                "receipt_sha256": _file_sha256(output / "receipt.json"),
            }
        )
        _atomic_json(state_path, state)
        return receipt
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--task-contract", required=True, type=Path)
    parser.add_argument("--source-codex-home", type=Path, default=Path("~/.codex"))
    parser.add_argument("--codex-binary", type=Path, default=Path("codex"))
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        receipt = run_series_review(
            repo=arguments.repo,
            base=arguments.base,
            head=arguments.head,
            packet=arguments.packet,
            task_contract=arguments.task_contract,
            source_codex_home=arguments.source_codex_home,
            codex_binary=arguments.codex_binary,
            timeout_seconds=arguments.timeout_seconds,
        )
    except ReviewRunnerError as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
