#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

from evaluation.core.identity import (
    PACKAGE_PATHS,
    canonical_sha256,
    case_semantic_sha256,
    engine_category_sha256,
    engine_inventory,
    package_identities,
    package_manifest_sha256,
    read_json,
    selected_package_paths,
    sha256_bytes,
    workspace_file_manifest,
)
from evaluation.core.receipt import write_new_json
from evaluation.corpus.contract import (
    BASE_COMMAND_PATHS,
    BLOCKER_CLASSES,
    DISABLED_FEATURES,
    EVALUATOR_CONTEXT,
    FILESYSTEM_ISOLATION_POLICY,
    FIXED_GIT_DATE,
    OUTPUT_SCHEMA,
    PARENT_CONTEXT_ENV,
    PERMISSION_FIELDS,
    PERMISSION_PROFILE,
    RECOVERY_GATE_FIELDS,
    RECOVERY_STATE_FIELDS,
    REQUIRED_TAGS,
)

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evaluation" / "cases"
EXPECTED_CANDIDATE_SKILL_ENTRIES = frozenset(
    {
        "SKILL.md",
        "agents",
        "agents/openai.yaml",
        "references",
        "references/execplan.md",
    }
)
EXPECTED_PUBLIC_02_SKILL_ENTRIES = frozenset(
    {
        "SKILL.md",
        "agents",
        "agents/openai.yaml",
        "references",
        "references/external-review.md",
        "references/task-packets.md",
    }
)
EXPECTED_PUBLIC_02_PACKAGE_MANIFEST_SHA256 = (
    "77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89"
)
EXPECTED_SKILL_ENTRIES_BY_ARM = {
    "candidate": EXPECTED_CANDIDATE_SKILL_ENTRIES,
    "public-0.2": EXPECTED_PUBLIC_02_SKILL_ENTRIES,
}
EXPECTED_COMMON_PACKAGE_ENTRIES = frozenset(
    {
        ".agents",
        ".agents/plugins",
        ".agents/plugins/marketplace.json",
        ".codex-plugin",
        ".codex-plugin/plugin.json",
        "README.md",
        "skills",
        "skills/happycodex",
    }
)
CODEX_BINARY_RAW = shutil.which("codex")
CODEX_BINARY = Path(CODEX_BINARY_RAW).resolve() if CODEX_BINARY_RAW else None
RG_BINARY_RAW = shutil.which("rg")
RG_BINARY = Path(RG_BINARY_RAW).resolve() if RG_BINARY_RAW else None
NATIVE_TOOL_BINARIES = (
    ("apply_patch", CODEX_BINARY),
    ("codex", CODEX_BINARY),
    ("codex-linux-sandbox", CODEX_BINARY),
    ("rg", RG_BINARY),
)
SOURCE_CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).resolve()


def neutral_review_brief(
    *,
    operative_request: str,
    scope: str,
    baseline_failures: list[str],
    objective_verification: dict[str, Any],
    exclusions: list[str],
    writer_narrative: str,
    historical_findings: list[str],
) -> dict[str, Any]:
    allowed = {
        "operative_request": operative_request,
        "scope": scope,
        "baseline_failures": baseline_failures,
        "objective_verification": objective_verification,
        "exclusions": exclusions,
    }
    brief = json.dumps(
        allowed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return {
        "brief": brief,
        "brief_sha256": sha256_bytes(brief.encode()),
        "writer_narrative_sha256": sha256_bytes(writer_narrative.encode()),
        "historical_findings_sha256": canonical_sha256(historical_findings),
    }


def semantic_input_sha256_from_package(
    case: dict[str, Any],
    *,
    package_semantic_sha256: str,
    model: str,
    effort: str,
    timeout: int,
    arm: str = "candidate",
) -> str:
    inventory = engine_inventory(ROOT)
    shared_semantic = engine_category_sha256(
        inventory,
        "semantic",
        paths={"evaluation/corpus/contract.py"},
    )
    return case_semantic_sha256(
        case,
        shared_semantic_sha256=shared_semantic,
        package_semantic_sha256=package_semantic_sha256,
        model=model,
        effort=effort,
        timeout=timeout,
        arm=arm,
    )


def semantic_input_sha256(
    case: dict[str, Any],
    *,
    plugin: Path,
    model: str,
    effort: str,
    timeout: int,
    arm: str = "candidate",
) -> str:
    return semantic_input_sha256_from_package(
        case,
        package_semantic_sha256=package_identities(plugin)["semantic_sha256"],
        model=model,
        effort=effort,
        timeout=timeout,
        arm=arm,
    )


def run(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    kwargs: dict[str, Any] = {
        "cwd": cwd,
        "env": env,
        "timeout": timeout,
        "check": False,
        "capture_output": True,
        "text": True,
    }
    if input_text is None:
        kwargs["stdin"] = subprocess.DEVNULL
    else:
        kwargs["input"] = input_text
    return subprocess.run(argv, **kwargs)


def prepare_native_tool_bin(temp: Path) -> Path:
    missing_tools = [
        name
        for name, binary in NATIVE_TOOL_BINARIES
        if binary is None or not binary.is_file()
    ]
    if missing_tools:
        raise RuntimeError(
            f"native tools required for evaluator isolation: {missing_tools}"
        )
    temp = temp.resolve()
    if not temp.is_dir():
        raise ValueError("evaluation temp must be an existing directory")
    bin_dir = temp / "bin"
    bin_dir.mkdir(exist_ok=True)
    for name, binary in NATIVE_TOOL_BINARIES:
        assert binary is not None
        target = bin_dir / name
        try:
            os.link(binary, target)
        except OSError:
            shutil.copy2(binary, target)
    return bin_dir


def permission_profile_args(
    *, tool_bin: Path, user_home: Path, select_default: bool = True
) -> list[str]:
    tool_bin = tool_bin.resolve()
    user_home = user_home.resolve()
    command_path = os.pathsep.join((str(tool_bin), *BASE_COMMAND_PATHS))
    filesystem = (
        '{":minimal"="read",":workspace_roots"={"."="read"},'
        f'{json.dumps(str(tool_bin))}="read"}}'
    )
    args: list[str] = []
    if select_default:
        args.extend(("-c", f'default_permissions="{PERMISSION_PROFILE}"'))
    args.extend(
        (
            "-c",
            f'permissions.{PERMISSION_PROFILE}.description="fixture read only"',
            "-c",
            f"permissions.{PERMISSION_PROFILE}.filesystem={filesystem}",
            "-c",
            f"permissions.{PERMISSION_PROFILE}.network.enabled=false",
            "-c",
            'shell_environment_policy.inherit="none"',
            "-c",
            "shell_environment_policy.ignore_default_excludes=false",
            "-c",
            "shell_environment_policy.set="
            f"{{PATH={json.dumps(command_path)},HOME={json.dumps(str(user_home))}}}",
        )
    )
    return args


def deterministic_git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = FIXED_GIT_DATE
    env["GIT_COMMITTER_DATE"] = FIXED_GIT_DATE
    return env


def load_cases() -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for path in sorted(CASES.glob("*.json")):
        case = read_json(path)
        validate_case(case, path)
        if case["id"] in loaded:
            raise ValueError(f"duplicate case id: {case['id']}")
        loaded[case["id"]] = case
    covered = {tag for case in loaded.values() for tag in case["covers"]}
    missing = REQUIRED_TAGS - covered
    if missing:
        raise ValueError(f"corpus missing required tags: {sorted(missing)}")
    return loaded


def validate_case(case: dict[str, Any], path: Path) -> None:
    required = {"schema_version", "id", "covers", "prompt", "fixture", "oracle"}
    if set(case) != required or case["schema_version"] != 1:
        raise ValueError(f"invalid case envelope: {path}")
    if not re.fullmatch(r"[a-z0-9-]+", case["id"]):
        raise ValueError(f"invalid case id: {case['id']}")
    fixture = case["fixture"]
    if not fixture.get("commits"):
        raise ValueError(f"case needs at least one commit: {case['id']}")
    if "$happycodex:happycodex" not in case["prompt"]:
        raise ValueError(f"case does not invoke skill: {case['id']}")
    expected = case["oracle"].get("expected", {})
    if set(expected) != PERMISSION_FIELDS:
        raise ValueError(f"case must constrain all permission fields: {case['id']}")
    accepted = case["oracle"].get("accepted_baseline_failures", [])
    if (
        not isinstance(accepted, list)
        or any(not isinstance(identity, str) or not identity for identity in accepted)
        or len({identity.casefold() for identity in accepted}) != len(accepted)
    ):
        raise ValueError(f"invalid accepted baseline failures: {case['id']}")
    for index, identity in enumerate(accepted):
        for other in accepted[index + 1 :]:
            if finding_identity_matches(identity, other) or finding_identity_matches(
                other, identity
            ):
                raise ValueError(f"ambiguous accepted baseline failures: {case['id']}")
    native = fixture.get("native_compaction_resume")
    prompts = [case["prompt"]]
    if native is not None:
        if set(native) != {
            "prepare_prompt",
            "fresh_recovery_prompt",
            "auto_compact_token_limit",
            "post_compaction_transition",
            "recovery_oracle",
        }:
            raise ValueError(f"invalid native compaction config: {case['id']}")
        transition = native["post_compaction_transition"]
        if (
            "$happycodex:happycodex" not in native["prepare_prompt"]
            or "$happycodex:happycodex" not in native["fresh_recovery_prompt"]
            or not isinstance(native["auto_compact_token_limit"], int)
            or native["auto_compact_token_limit"] <= 0
            or set(transition) != {"message", "files"}
            or not isinstance(transition["message"], str)
            or not transition["message"]
            or not isinstance(transition["files"], dict)
            or not transition["files"]
            or set(native["recovery_oracle"])
            != RECOVERY_STATE_FIELDS
            - {
                "baseline_revision",
                "baseline_tree",
                "current_revision",
                "current_tree",
            }
        ):
            raise ValueError(f"invalid native compaction values: {case['id']}")
        prompts.extend((native["prepare_prompt"], native["fresh_recovery_prompt"]))
    for entry in fixture["commits"]:
        generated = generated_fixture_files(entry.get("generated_files"))
        overlap = set(generated) & set(entry["files"])
        if overlap:
            raise ValueError(
                f"generated fixture overlaps explicit files: {sorted(overlap)}"
            )
    blocker_classes = case["oracle"].get("required_blocker_classes", [])
    if (
        not isinstance(blocker_classes, list)
        or any(item not in BLOCKER_CLASSES for item in blocker_classes)
        or len(set(blocker_classes)) != len(blocker_classes)
    ):
        raise ValueError(f"invalid blocker classes: {case['id']}")
    required_findings = case["oracle"].get("required_classifications", [])
    if not isinstance(required_findings, list):
        raise ValueError(f"invalid required classifications: {case['id']}")
    finding_keys: set[str] = set()
    for finding in required_findings:
        if not isinstance(finding, dict):
            raise ValueError(f"invalid required classification: {case['id']}")
        states = finding.get("state")
        states = states if isinstance(states, list) else [states]
        if (
            set(finding) != {"identity", "domain", "state"}
            or not isinstance(finding["identity"], str)
            or not finding["identity"]
            or finding["domain"]
            not in {"secret", "baseline_failure", "receipt", "other"}
            or not states
            or len(set(states)) != len(states)
            or any(
                state
                not in {
                    "baseline_unchanged",
                    "resolved",
                    "candidate_new",
                    "unknown",
                }
                for state in states
            )
        ):
            raise ValueError(f"invalid required classification: {case['id']}")
        folded_identity = finding["identity"].casefold()
        if folded_identity in finding_keys:
            raise ValueError(f"duplicate required classification: {case['id']}")
        if any(
            finding_identity_matches(finding["identity"], other)
            or finding_identity_matches(other, finding["identity"])
            for other in finding_keys
        ):
            raise ValueError(f"ambiguous required classification: {case['id']}")
        finding_keys.add(folded_identity)
    required_blockers = case["oracle"].get("required_blocker_classifications", [])
    if not isinstance(required_blockers, list):
        raise ValueError(f"invalid required blockers: {case['id']}")
    blocker_keys: set[str] = set()
    for blocker in required_blockers:
        if not isinstance(blocker, dict):
            raise ValueError(f"invalid required blocker: {case['id']}")
        if (
            set(blocker) != {"identity", "class"}
            or not isinstance(blocker["identity"], str)
            or not blocker["identity"]
            or blocker["class"] not in BLOCKER_CLASSES
        ):
            raise ValueError(f"invalid required blocker: {case['id']}")
        folded_identity = blocker["identity"].casefold()
        if folded_identity in blocker_keys:
            raise ValueError(f"duplicate required blocker: {case['id']}")
        if any(
            finding_identity_matches(blocker["identity"], other)
            or finding_identity_matches(other, blocker["identity"])
            for other in blocker_keys
        ):
            raise ValueError(f"ambiguous required blocker: {case['id']}")
        blocker_keys.add(folded_identity)
    required_anchored = case["oracle"].get("required_anchored_blockers", [])
    if not isinstance(required_anchored, list):
        raise ValueError(f"invalid required anchored blockers: {case['id']}")
    anchored_keys: set[tuple[str, tuple[str, ...]]] = set()
    for blocker in required_anchored:
        classes = blocker.get("class") if isinstance(blocker, dict) else None
        classes = classes if isinstance(classes, list) else [classes]
        if (
            not isinstance(blocker, dict)
            or set(blocker) != {"anchor", "class"}
            or not isinstance(blocker["anchor"], str)
            or not blocker["anchor"]
            or not classes
            or len(set(classes)) != len(classes)
            or any(item not in BLOCKER_CLASSES for item in classes)
        ):
            raise ValueError(f"invalid required anchored blocker: {case['id']}")
        key = (blocker["anchor"].casefold(), tuple(sorted(classes)))
        if key in anchored_keys:
            raise ValueError(f"duplicate required anchored blocker: {case['id']}")
        anchored_keys.add(key)
    required_anchored_findings = case["oracle"].get(
        "required_anchored_classifications", []
    )
    if not isinstance(required_anchored_findings, list):
        raise ValueError(f"invalid required anchored classifications: {case['id']}")
    for finding in required_anchored_findings:
        states = finding.get("state") if isinstance(finding, dict) else None
        states = states if isinstance(states, list) else [states]
        if (
            not isinstance(finding, dict)
            or set(finding) != {"anchor", "domain", "state"}
            or not isinstance(finding["anchor"], str)
            or not finding["anchor"]
            or finding["domain"]
            not in {"secret", "baseline_failure", "receipt", "other"}
            or not states
            or len(set(states)) != len(states)
            or any(
                state
                not in {
                    "baseline_unchanged",
                    "resolved",
                    "candidate_new",
                    "unknown",
                }
                for state in states
            )
        ):
            raise ValueError(f"invalid required anchored classification: {case['id']}")
    coverage = case["oracle"].get("coverage_assertions")
    if coverage is not None:
        if (
            not isinstance(coverage, list)
            or any(not isinstance(item, dict) for item in coverage)
            or {item["tag"] for item in coverage if "tag" in item}
            != set(case["covers"])
        ):
            raise ValueError(f"invalid coverage assertions: {case['id']}")
        if len(coverage) != len(case["covers"]):
            raise ValueError(f"invalid coverage assertions: {case['id']}")
        targets: set[tuple[str, ...]] = set()
        for assertion in coverage:
            kind = assertion.get("kind")
            if kind == "recovery":
                expected_keys = {"tag", "kind"}
            elif kind == "anchored_blocker":
                expected_keys = {"tag", "kind", "anchor", "class"}
            else:
                expected_keys = {"tag", "kind", "identity"}
            raw_identity = assertion.get("identity", "")
            identity = raw_identity.casefold() if isinstance(raw_identity, str) else ""
            raw_anchor = assertion.get("anchor", "")
            anchor = raw_anchor.casefold() if isinstance(raw_anchor, str) else ""
            blocker_classes = assertion.get("class", "")
            blocker_classes = (
                blocker_classes
                if isinstance(blocker_classes, list)
                else [blocker_classes]
            )
            blocker_key = (anchor, tuple(sorted(blocker_classes)))
            if (
                set(assertion) != expected_keys
                or (kind == "finding" and identity not in finding_keys)
                or (kind == "blocker" and identity not in blocker_keys)
                or (kind == "anchored_blocker" and blocker_key not in anchored_keys)
                or kind
                not in {
                    "finding",
                    "blocker",
                    "anchored_blocker",
                    "recovery",
                }
            ):
                raise ValueError(f"invalid coverage assertions: {case['id']}")
            target = (
                (kind, anchor, *blocker_key[1])
                if kind == "anchored_blocker"
                else (kind, identity)
            )
            if target in targets:
                raise ValueError(f"duplicate coverage target: {case['id']}")
            targets.add(target)
            if kind == "recovery" and not (
                expected.get("execplan_condition") == "needs_amendment"
                and expected.get("protocol_may_product_write") is False
                and expected.get("protocol_may_review") is False
                and expected.get("protocol_may_complete") is False
            ):
                raise ValueError(f"invalid recovery coverage assertion: {case['id']}")
    prompt_folded = " ".join(prompts).casefold()
    for hidden in case["oracle"].get("prompt_forbidden", []):
        if hidden.casefold() in prompt_folded:
            raise ValueError(f"prompt leaks oracle term {hidden!r}: {case['id']}")


def apply_files(repo: Path, files: dict[str, str | None]) -> None:
    for relative, content in files.items():
        target = repo / relative
        if not target.resolve().is_relative_to(repo.resolve()):
            raise ValueError(f"fixture path escapes repo: {relative}")
        if content is None:
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def generated_fixture_files(config: dict[str, Any] | None) -> dict[str, str]:
    if config is None:
        return {}
    required = {"prefix", "suffix", "count", "content", "last_content"}
    if set(config) != required:
        raise ValueError("generated fixture config has unexpected fields")
    prefix = config["prefix"]
    suffix = config["suffix"]
    count = config["count"]
    content = config["content"]
    last_content = config["last_content"]
    if (
        not isinstance(prefix, str)
        or not prefix
        or not isinstance(suffix, str)
        or not isinstance(count, int)
        or not 1 <= count <= 5_000
        or not isinstance(content, str)
        or not isinstance(last_content, str)
    ):
        raise ValueError("invalid generated fixture config")
    generated: dict[str, str] = {}
    for index in range(count):
        relative = f"{prefix}{index:04d}{suffix}"
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or relative in generated:
            raise ValueError(f"generated fixture path is unsafe: {relative}")
        template = last_content if index == count - 1 else content
        generated[relative] = template.replace("{index}", f"{index:04d}")
    return generated


def render_fixture_files(
    files: dict[str, str | None],
    commits: list[str],
    trees: list[str],
    product_digests: list[str],
    review_projections: list[dict[str, Any]],
) -> dict[str, str | None]:
    rendered: dict[str, str | None] = {}
    pattern = re.compile(
        r"\{\{(COMMIT|TREE|PRODUCT_SHA256|REVIEW_BASE|REVIEW_CANDIDATE|"
        r"REVIEW_OUTPUT_BLOB|REVIEW_OUTPUT_SHA256|REVIEW_CHALLENGER_BLOB|"
        r"REVIEW_CHALLENGER_SHA256)_(\d+)\}\}"
    )
    for relative, content in files.items():
        if content is None:
            rendered[relative] = None
            continue

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key in {"COMMIT", "TREE", "PRODUCT_SHA256"}:
                values: list[str] = {
                    "COMMIT": commits,
                    "TREE": trees,
                    "PRODUCT_SHA256": product_digests,
                }[key]
            else:
                projection_key = {
                    "REVIEW_BASE": "baseline_commit",
                    "REVIEW_CANDIDATE": "candidate_commit",
                    "REVIEW_OUTPUT_BLOB": "output_blob",
                    "REVIEW_OUTPUT_SHA256": "output_sha256",
                    "REVIEW_CHALLENGER_BLOB": "challenger_blob",
                    "REVIEW_CHALLENGER_SHA256": "challenger_sha256",
                }[key]
                values = [item[projection_key] for item in review_projections]
            index = int(match.group(2))
            if index >= len(values):
                raise ValueError(
                    f"fixture placeholder {match.group(0)} is not yet available"
                )
            return values[index]

        rendered[relative] = pattern.sub(replace, content)
    return rendered


def product_manifest_sha256_at(repo: Path, revision: str, excluded: str | None) -> str:
    lines = run(["git", "ls-tree", "-r", revision], cwd=repo).stdout.splitlines()
    if excluded is not None:
        lines = [line for line in lines if not line.endswith(f"\t{excluded}")]
    manifest = "\n".join(lines) + "\n"
    return sha256_bytes(manifest.encode())


def product_manifest_sha256(repo: Path, excluded: str | None) -> str:
    return product_manifest_sha256_at(repo, "HEAD", excluded)


def product_tree(repo: Path, revision: str, excluded: str) -> str:
    with tempfile.TemporaryDirectory(prefix="happycodex-review-index-") as raw:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(raw) / "index")
        read = run(["git", "read-tree", revision], cwd=repo, env=env)
        if read.returncode:
            raise RuntimeError(read.stderr)
        removed = run(
            ["git", "update-index", "--force-remove", "--", excluded],
            cwd=repo,
            env=env,
        )
        if removed.returncode:
            raise RuntimeError(removed.stderr)
        written = run(["git", "write-tree"], cwd=repo, env=env)
        if written.returncode:
            raise RuntimeError(written.stderr)
        return written.stdout.strip()


def create_challenger_receipt(
    repo: Path, config: dict[str, Any], commits: list[str]
) -> dict[str, Any]:
    terminal_index = config["terminal"]
    if terminal_index != len(commits) - 1:
        raise ValueError("challenger receipt must be created at its terminal revision")
    name = config["name"]
    predispatch_record = commits[config["predispatch"]]
    terminal_record = commits[terminal_index]
    receipt = (
        f"task={config['task']}\n"
        f"dispatch_revision={commits[0]}\n"
        f"predispatch_record={predispatch_record}\n"
        f"terminal_record={terminal_record}\n"
        "terminal_status=complete\nmode=read-only\ndelegation=none\n"
        "brief=verbatim request without Root inventory\n"
        f"return={config['return']}\n"
        f"root_reproduction={config['root_reproduction']}\n"
    )
    stored = run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input_text=receipt)
    if stored.returncode:
        raise RuntimeError(stored.stderr)
    blob = stored.stdout.strip()
    ref = f"refs/happycodex-eval/{name}/challenger"
    updated = run(["git", "update-ref", ref, blob], cwd=repo)
    if updated.returncode:
        raise RuntimeError(updated.stderr)
    return {
        "name": name,
        "blob": blob,
        "sha256": sha256_bytes(receipt.encode()),
        "ref": ref,
        "predispatch_record": predispatch_record,
        "terminal_record": terminal_record,
        "created_after_commit_index": terminal_index,
    }


def create_review_projection(
    repo: Path,
    config: dict[str, Any],
    commits: list[str],
    challenger_receipts: list[dict[str, Any]],
) -> dict[str, Any]:
    baseline_source = commits[config["baseline"]]
    candidate_source = commits[config["candidate"]]
    excluded = config.get("exclude")
    name = config["name"]
    if config.get("mode", "synthetic") == "source":
        baseline_commit = baseline_source
        candidate_commit = candidate_source
    else:
        if excluded is None:
            raise ValueError("synthetic review projection requires an excluded path")
        baseline_tree = product_tree(repo, baseline_source, excluded)
        candidate_tree = product_tree(repo, candidate_source, excluded)
        baseline = run(
            ["git", "commit-tree", baseline_tree, "-m", "synthetic baseline"],
            cwd=repo,
            env=deterministic_git_env(),
        )
        if baseline.returncode:
            raise RuntimeError(baseline.stderr)
        baseline_commit = baseline.stdout.strip()
        candidate = run(
            [
                "git",
                "commit-tree",
                candidate_tree,
                "-p",
                baseline_commit,
                "-m",
                "synthetic candidate",
            ],
            cwd=repo,
            env=deterministic_git_env(),
        )
        if candidate.returncode:
            raise RuntimeError(candidate.stderr)
        candidate_commit = candidate.stdout.strip()
    prefix = f"refs/happycodex-eval/{name}"
    for suffix, commit in (
        ("baseline", baseline_commit),
        ("candidate", candidate_commit),
    ):
        updated = run(["git", "update-ref", f"{prefix}/{suffix}", commit], cwd=repo)
        if updated.returncode:
            raise RuntimeError(updated.stderr)
    diff_units = run(
        ["git", "diff", "--name-only", baseline_commit, candidate_commit], cwd=repo
    ).stdout.splitlines()
    configured_limit = config.get("coverage_limit")
    if configured_limit is not None and (
        not isinstance(configured_limit, int) or configured_limit <= 0
    ):
        raise ValueError("review coverage limit must be a positive integer")
    coverage_limit = len(diff_units) if configured_limit is None else configured_limit
    inspected_diff_units = diff_units[:coverage_limit]
    omitted_diff_units = diff_units[coverage_limit:]
    decisive_tail = config.get("decisive_tail", "")
    if decisive_tail and decisive_tail not in omitted_diff_units:
        raise ValueError("decisive review tail must be an actually omitted diff unit")
    coverage_complete = not omitted_diff_units
    review_task = config.get("review_task", "review-task-9")
    obligations = ",".join(
        config.get("obligations", ["greeting-change", "unrelated-output-preservation"])
    )
    queries = config.get(
        "queries",
        "return-hello:baseline-1/candidate-0;format_name:baseline-2/candidate-2",
    )
    inspected_paths = ",".join(
        inspected_diff_units
        if configured_limit is not None
        else config.get("inspected_paths", ["TASK.md", "app.py", "tests/test_app.py"])
    )
    evidence = config.get(
        "evidence",
        "synthetic diff, listed source paths, and executable tests inspected",
    )
    source_baseline_manifest = product_manifest_sha256_at(
        repo, baseline_source, excluded
    )
    source_candidate_manifest = product_manifest_sha256_at(
        repo, candidate_source, excluded
    )
    projected_baseline_manifest = product_manifest_sha256_at(
        repo, baseline_commit, None
    )
    projected_candidate_manifest = product_manifest_sha256_at(
        repo, candidate_commit, None
    )
    if source_baseline_manifest != projected_baseline_manifest:
        raise ValueError("review baseline projection differs from source product")
    if source_candidate_manifest != projected_candidate_manifest:
        raise ValueError("review candidate projection differs from source product")
    brief_receipt = neutral_review_brief(
        operative_request=config.get(
            "operative_request", config.get("brief", "verbatim task")
        ),
        scope=f"{baseline_source}..{candidate_source}",
        baseline_failures=config.get("baseline_failures", []),
        objective_verification={
            "source_baseline_manifest_sha256": source_baseline_manifest,
            "source_candidate_manifest_sha256": source_candidate_manifest,
            "projected_baseline_manifest_sha256": projected_baseline_manifest,
            "projected_candidate_manifest_sha256": projected_candidate_manifest,
            "baseline_manifest_equal": True,
            "candidate_manifest_equal": True,
            "diff_unit_count": len(diff_units),
            "diff_units_sha256": canonical_sha256(diff_units),
        },
        exclusions=[excluded] if excluded else [],
        writer_narrative=config.get("writer_narrative", ""),
        historical_findings=config.get("historical_findings", []),
    )
    contract_projection = config.get(
        "contract_projection",
        "operative sources, normalized Outcome, frozen claims, acceptance oracles",
    )
    contract_mapping = config.get(
        "contract_mapping",
        "greeting-change<->O1;unrelated-output-preservation<->P1",
    )
    configured_model_source = config.get(
        "configured_model_source",
        "fixture-explicit" if "model" in config else "evaluator-default",
    )
    receipt = (
        f"review_task={review_task}\n"
        "terminal_status=complete\n"
        f"configured_model_source={configured_model_source}\n"
        f"model={config.get('model', 'gpt-5.6-sol')}\n"
        f"effective_model={config.get('model', 'gpt-5.6-sol')}\n"
        f"effort={config.get('effort', 'max')}\n"
        f"effective_effort={config.get('effort', 'max')}\n"
        f"effective_permission_profile={config.get('permission_profile', 'read-only-isolated')}\n"
        f"effective_network={config.get('network', 'disabled')}\n"
        f"effective_write_access={config.get('write_access', 'none')}\n"
        f"authorization={config.get('authorization', 'environment-authorized')}\n"
        f"degradation={config.get('degradation', 'none')}\n"
        f"baseline_commit={baseline_commit}\n"
        f"candidate_commit={candidate_commit}\n"
        f"source_baseline_commit={baseline_source}\n"
        f"source_candidate_commit={candidate_source}\n"
        f"source_baseline_manifest_sha256={source_baseline_manifest}\n"
        f"source_candidate_manifest_sha256={source_candidate_manifest}\n"
        f"projected_baseline_manifest_sha256={projected_baseline_manifest}\n"
        f"projected_candidate_manifest_sha256={projected_candidate_manifest}\n"
        "baseline_manifest_equal=true\ncandidate_manifest_equal=true\n"
        f"excluded_path={excluded or 'none'}\n"
        f"diff_unit_count={len(diff_units)}\n"
        f"diff_units={','.join(diff_units)}\n"
        f"coverage_limit={coverage_limit}\n"
        f"inspected_diff_units={','.join(inspected_diff_units)}\n"
        f"omitted_diff_units={','.join(omitted_diff_units)}\n"
        f"decisive_tail={decisive_tail or 'none'}\n"
        f"independent_obligations={obligations}\n"
        "phase_1_inventory_frozen=true\n"
        f"phase_1_correctness_complete={str(coverage_complete).lower()}\n"
        "phase_1_diff_unit_coverage="
        f"{'complete' if coverage_complete else 'incomplete'}\n"
        f"phase_2_contract_projection={contract_projection}\n"
        f"contract_mapping={contract_mapping}\n"
        f"queries={queries}\n"
        f"inspected_paths={inspected_paths}\n"
        f"evidence={evidence}\n"
        f"brief={brief_receipt['brief']}\n"
        f"brief_sha256={brief_receipt['brief_sha256']}\n"
        "writer_narrative_withheld_sha256="
        f"{brief_receipt['writer_narrative_sha256']}\n"
        "historical_findings_withheld_sha256="
        f"{brief_receipt['historical_findings_sha256']}\n"
        f"workspace={config.get('workspace', 'isolated synthetic repository; original history and ExecPlan unavailable')}\n"
        "external_reads=none\ncontamination=none\n"
        f"truncation={'none' if coverage_complete else 'detected'}\n"
        "limitations="
        f"{'none' if coverage_complete else f'{len(omitted_diff_units)} omitted diff units'}\n"
        "findings="
        f"{'none' if coverage_complete else 'completion-blocking incomplete diff coverage'}\n"
    )
    output = run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input_text=receipt)
    if output.returncode:
        raise RuntimeError(output.stderr)
    output_blob = output.stdout.strip()
    updated = run(["git", "update-ref", f"{prefix}/output", output_blob], cwd=repo)
    if updated.returncode:
        raise RuntimeError(updated.stderr)
    challenger_blob = ""
    challenger_sha256 = ""
    challenger_name = config.get("challenger_receipt")
    if challenger_name:
        matches = [
            receipt
            for receipt in challenger_receipts
            if receipt["name"] == challenger_name
        ]
        if len(matches) != 1:
            raise ValueError(
                f"review projection requires one prior challenger receipt: {challenger_name}"
            )
        challenger_blob = matches[0]["blob"]
        challenger_sha256 = matches[0]["sha256"]
        if matches[0]["ref"] != f"{prefix}/challenger":
            raise ValueError("challenger and review projection namespaces differ")
    return {
        "baseline_commit": baseline_commit,
        "candidate_commit": candidate_commit,
        "source_baseline_commit": baseline_source,
        "source_candidate_commit": candidate_source,
        "source_baseline_manifest_sha256": source_baseline_manifest,
        "source_candidate_manifest_sha256": source_candidate_manifest,
        "brief": brief_receipt,
        "output_blob": output_blob,
        "output_sha256": sha256_bytes(receipt.encode()),
        "challenger_blob": challenger_blob,
        "challenger_sha256": challenger_sha256,
        "ref_prefix": prefix,
        "diff_unit_count": len(diff_units),
        "diff_units": diff_units,
        "coverage_limit": coverage_limit,
        "inspected_diff_units": inspected_diff_units,
        "omitted_diff_units": omitted_diff_units,
        "decisive_tail": decisive_tail,
    }


def build_fixture(case: dict[str, Any], repo: Path) -> dict[str, Any]:
    repo.mkdir(parents=True)
    init = run(["git", "init", "-b", "main"], cwd=repo)
    if init.returncode:
        raise RuntimeError(init.stderr)
    run(["git", "config", "user.name", "HappyCodex Eval"], cwd=repo)
    run(["git", "config", "user.email", "eval@example.invalid"], cwd=repo)
    commits: list[str] = []
    trees: list[str] = []
    product_digests: list[str] = []
    review_projections: list[dict[str, Any]] = []
    challenger_receipts: list[dict[str, Any]] = []
    product_exclude = case["fixture"].get("product_exclude")
    for entry in case["fixture"]["commits"]:
        projection_configs = entry.get("review_projections")
        if projection_configs is None and "review_projection" in entry:
            projection_configs = [entry["review_projection"]]
        for projection_config in projection_configs or []:
            review_projections.append(
                create_review_projection(
                    repo, projection_config, commits, challenger_receipts
                )
            )
        rendered_files = render_fixture_files(
            entry["files"],
            commits,
            trees,
            product_digests,
            review_projections,
        )
        generated_files = generated_fixture_files(entry.get("generated_files"))
        overlap = set(rendered_files) & set(generated_files)
        if overlap:
            raise ValueError(
                f"generated fixture overlaps explicit files: {sorted(overlap)}"
            )
        apply_files(repo, {**rendered_files, **generated_files})
        run(["git", "add", "-A"], cwd=repo)
        result = run(
            ["git", "commit", "-m", entry["message"]],
            cwd=repo,
            env=deterministic_git_env(),
        )
        if result.returncode:
            raise RuntimeError(result.stderr)
        commits.append(run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip())
        trees.append(run(["git", "rev-parse", "HEAD^{tree}"], cwd=repo).stdout.strip())
        product_digests.append(product_manifest_sha256(repo, product_exclude))
        for challenger_config in entry.get("challenger_receipts", []):
            receipt = create_challenger_receipt(repo, challenger_config, commits)
            if any(item["name"] == receipt["name"] for item in challenger_receipts):
                raise ValueError(f"duplicate challenger receipt: {receipt['name']}")
            challenger_receipts.append(receipt)
    staged_files = render_fixture_files(
        case["fixture"].get("staged_files", {}),
        commits,
        trees,
        product_digests,
        review_projections,
    )
    apply_files(repo, staged_files)
    if staged_files:
        staged = run(["git", "add", "--", *sorted(staged_files)], cwd=repo)
        if staged.returncode:
            raise RuntimeError(staged.stderr)
    apply_files(
        repo,
        render_fixture_files(
            case["fixture"].get("dirty_files", {}),
            commits,
            trees,
            product_digests,
            review_projections,
        ),
    )
    apply_files(
        repo,
        render_fixture_files(
            case["fixture"].get("untracked_files", {}),
            commits,
            trees,
            product_digests,
            review_projections,
        ),
    )
    status = run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=repo
    ).stdout
    return {
        "commits": commits,
        "trees": trees,
        "product_manifest_sha256": product_digests,
        "review_projections": review_projections,
        "challenger_receipts": challenger_receipts,
        "head": run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip(),
        "tree": run(["git", "rev-parse", "HEAD^{tree}"], cwd=repo).stdout.strip(),
        "status_before": status,
        "files": workspace_file_manifest(repo),
        "product_exclude": product_exclude,
    }


def apply_post_compaction_transition(
    repo: Path, config: dict[str, Any], fixture: dict[str, Any]
) -> dict[str, Any]:
    pre_head = fixture["head"]
    pre_status = fixture["status_before"]
    pre_files_sha256 = canonical_sha256(fixture["files"])
    rendered = render_fixture_files(
        config["files"],
        fixture["commits"],
        fixture["trees"],
        fixture["product_manifest_sha256"],
        fixture["review_projections"],
    )
    apply_files(repo, rendered)
    added = run(["git", "add", "-A"], cwd=repo)
    if added.returncode:
        raise RuntimeError(added.stderr)
    committed = run(
        ["git", "commit", "-m", config["message"]],
        cwd=repo,
        env=deterministic_git_env(),
    )
    if committed.returncode:
        raise RuntimeError(committed.stderr)
    head = run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    tree = run(["git", "rev-parse", "HEAD^{tree}"], cwd=repo).stdout.strip()
    fixture["commits"].append(head)
    fixture["trees"].append(tree)
    fixture["product_manifest_sha256"].append(
        product_manifest_sha256(repo, fixture["product_exclude"])
    )
    status = run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=repo
    ).stdout
    files = workspace_file_manifest(repo)
    fixture.update(
        {"head": head, "tree": tree, "status_before": status, "files": files}
    )
    return {
        "message": config["message"],
        "pre_head": pre_head,
        "pre_status": pre_status,
        "pre_files_sha256": pre_files_sha256,
        "head": head,
        "tree": tree,
        "status": status,
        "files": files,
        "files_sha256": canonical_sha256(files),
        "changed_paths": sorted(config["files"]),
    }


def expected_skill_entries_for_arm(arm: str) -> frozenset[str]:
    try:
        return EXPECTED_SKILL_ENTRIES_BY_ARM[arm]
    except KeyError as exc:
        raise ValueError(f"unknown evaluation arm: {arm}") from exc


def expected_package_entries_for_arm(arm: str) -> frozenset[str]:
    skill_entries = expected_skill_entries_for_arm(arm)
    return EXPECTED_COMMON_PACKAGE_ENTRIES | {
        f"skills/happycodex/{relative}" for relative in skill_entries
    }


def copy_plugin_package(
    source: Path, destination: Path, *, arm: str = "candidate"
) -> None:
    expected_entries = expected_package_entries_for_arm(arm)
    paths = selected_package_paths(source)
    actual_entries = {path.relative_to(source).as_posix() for path in paths}
    if actual_entries != expected_entries or any(path.is_symlink() for path in paths):
        unexpected = sorted(actual_entries - expected_entries)
        missing = sorted(expected_entries - actual_entries)
        raise RuntimeError(
            f"unexpected runtime surface for {arm}: "
            f"unexpected={unexpected}, missing={missing}"
        )
    destination.mkdir(parents=True)
    for relative in PACKAGE_PATHS:
        item = source / relative
        if not item.exists():
            raise FileNotFoundError(item)
        target = destination / relative
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def isolated_home(
    parent: Path, *, source_home: Path = SOURCE_CODEX_HOME
) -> tuple[Path, dict[str, str]]:
    home = parent / "codex-home"
    home.mkdir()
    user_home = parent / "user-home"
    user_home.mkdir()
    source_auth = source_home.resolve() / "auth.json"
    if not source_auth.is_file():
        raise RuntimeError(f"Codex auth unavailable at expected path: {source_auth}")
    auth = home / "auth.json"
    shutil.copyfile(source_auth, auth)
    auth.chmod(0o600)
    env = os.environ.copy()
    for key in PARENT_CONTEXT_ENV:
        env.pop(key, None)
    env["HOME"] = str(user_home)
    env["CODEX_HOME"] = str(home)
    env["PATH"] = os.pathsep.join((str(parent / "bin"), *BASE_COMMAND_PATHS))
    return home, env


def install_plugin(package: Path, home: Path, env: dict[str, str]) -> dict[str, Any]:
    added = run(
        ["codex", "plugin", "marketplace", "add", str(package), "--json"],
        cwd=package,
        env=env,
    )
    if added.returncode:
        raise RuntimeError(added.stderr)
    installed = run(
        ["codex", "plugin", "add", "happycodex@happycodex", "--json"],
        cwd=package,
        env=env,
    )
    if installed.returncode:
        raise RuntimeError(installed.stderr)
    add_data = json.loads(added.stdout)
    install_data = json.loads(installed.stdout)
    installed_path = Path(install_data["installedPath"])
    receipt = installed_package_receipt(package, installed_path)
    return {
        "marketplace": add_data,
        "plugin": install_data,
        **receipt,
        "isolated_home": str(home),
    }


def installed_package_receipt(source: Path, installed: Path) -> dict[str, str]:
    source_skill = source / "skills" / "happycodex" / "SKILL.md"
    installed_skill = installed / "skills" / "happycodex" / "SKILL.md"
    source_digest = sha256_bytes(source_skill.read_bytes())
    installed_digest = sha256_bytes(installed_skill.read_bytes())
    if source_digest != installed_digest:
        raise RuntimeError("installed Skill hash differs from packaged candidate")
    source_package_digest = package_manifest_sha256(source)
    installed_package_digest = package_manifest_sha256(installed)
    if source_package_digest != installed_package_digest:
        raise RuntimeError("installed package manifest differs from packaged candidate")
    return {
        "source_skill_sha256": source_digest,
        "installed_skill_sha256": installed_digest,
        "source_package_manifest_sha256": source_package_digest,
        "installed_package_manifest_sha256": installed_package_digest,
    }


def parse_events(stdout: str) -> tuple[dict[str, Any], dict[str, int], str | None]:
    final: dict[str, Any] | None = None
    usage: dict[str, int] = {}
    thread_id: str | None = None
    for line in stdout.splitlines():
        event = json.loads(line)
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                try:
                    final = json.loads(item.get("text", ""))
                except json.JSONDecodeError:
                    pass
        if event.get("type") == "turn.completed":
            usage = event.get("usage", {})
    if final is None:
        raise RuntimeError("Codex emitted no schema-valid final object")
    return final, usage, thread_id


def invoke_codex(
    argv: list[str], *, cwd: Path, env: dict[str, str], timeout: int
) -> tuple[subprocess.CompletedProcess[str], bool, float]:
    started = time.monotonic()
    try:
        completed = run(argv, cwd=cwd, env=env, timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = (
            exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        )
        stderr = (
            exc.stderr.decode()
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "timeout")
        )
        completed = subprocess.CompletedProcess(argv, 124, stdout, stderr)
        timed_out = True
    return completed, timed_out, time.monotonic() - started


def compaction_receipt(home: Path, thread_id: str | None) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "rollout_path": None,
        "rollout_sha256": None,
        "compaction_event_count": 0,
        "context_compacted_marker_count": 0,
        "event_types": [],
    }
    if not thread_id:
        return receipt
    matches = sorted((home / "sessions").rglob(f"*{thread_id}*.jsonl"))
    if len(matches) != 1:
        receipt["rollout_match_count"] = len(matches)
        return receipt
    rollout = matches[0]
    content = rollout.read_bytes()
    event_types: list[str] = []
    for raw_line in content.splitlines():
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "compacted":
            event_types.append("compacted")
        elif (
            event.get("type") == "event_msg"
            and event.get("payload", {}).get("type") == "context_compacted"
        ):
            event_types.append("context_compacted")
    return {
        "rollout_path": rollout.relative_to(home).as_posix(),
        "rollout_sha256": sha256_bytes(content),
        "compaction_event_count": event_types.count("compacted"),
        "context_compacted_marker_count": event_types.count("context_compacted"),
        "event_types": event_types,
        "rollout_match_count": 1,
    }


def combined_usage(*phases: dict[str, int]) -> dict[str, int]:
    keys = {
        key
        for phase in phases
        for key, value in phase.items()
        if isinstance(value, int)
    }
    return {key: sum(phase.get(key, 0) for phase in phases) for key in sorted(keys)}


def disabled_feature_args() -> list[str]:
    return [item for feature in DISABLED_FEATURES for item in ("--disable", feature)]


def finding_identity_matches(actual: str, expected: str) -> bool:
    actual_folded = actual.casefold()
    expected_folded = expected.casefold()
    return actual_folded == expected_folded or any(
        actual_folded.endswith(f"{delimiter}{expected_folded}")
        for delimiter in (":", "/")
    )


def finding_has_anchor(finding: dict[str, Any], expected: str) -> bool:
    expected_folded = expected.casefold()
    return str(finding.get("identity", "")).casefold() == expected_folded or any(
        isinstance(item, str) and item.casefold() == expected_folded
        for item in finding.get("anchors", [])
    )


def normalized_recovery_value(field: str, value: Any) -> Any:
    if field == "marker_ids" and isinstance(value, list):
        return sorted(value)
    if field == "live_agents" and isinstance(value, list):
        return sorted(value, key=canonical_sha256)
    if field == "tests" and isinstance(value, dict):
        normalized = dict(value)
        markers = normalized.get("marker_ids")
        if isinstance(markers, list):
            normalized["marker_ids"] = sorted(markers)
        return normalized
    return value


def fixture_requires_goal_pause_handoff(fixture: dict[str, Any]) -> bool:
    goal: str | None = None
    for commit in fixture.get("commits", []):
        files = commit.get("files", {})
        if "GOAL.md" in files:
            value = files["GOAL.md"]
            goal = value if isinstance(value, str) else None
    for layer in ("staged_files", "dirty_files", "untracked_files"):
        files = fixture.get(layer, {})
        if "GOAL.md" in files:
            value = files["GOAL.md"]
            goal = value if isinstance(value, str) else None
    if goal is None:
        return False
    folded = goal.casefold()
    return (
        "status: active" in folded
        and "agent-side goal pause action: unavailable" in folded
    )


def recovery_state_failures(
    label: str, actual: Any, expected: dict[str, Any]
) -> list[str]:
    if not isinstance(actual, dict):
        return [f"{label} is not a structured object"]
    failures: list[str] = []
    for field in sorted(RECOVERY_STATE_FIELDS):
        actual_value = actual.get(field)
        expected_value = expected.get(field)
        if normalized_recovery_value(field, actual_value) != normalized_recovery_value(
            field, expected_value
        ):
            failures.append(
                f"{label}.{field}: got {actual_value!r}, expected {expected_value!r}"
            )
    return failures


def match_oracle(
    result: dict[str, Any],
    oracle: dict[str, Any],
    *,
    expected_recovery_state: dict[str, Any] | None = None,
    fixture: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []
    for field, expected in oracle["expected"].items():
        allowed = expected if isinstance(expected, list) else [expected]
        if result.get(field) not in allowed:
            failures.append(f"{field}: got {result.get(field)!r}, expected {allowed!r}")
    if expected_recovery_state is not None:
        failures.extend(
            recovery_state_failures(
                "recovery_state",
                result.get("recovery_state"),
                expected_recovery_state,
            )
        )
    actual_findings = result.get("finding_classifications", [])
    actual_blockers = result.get("blocker_classifications", [])
    seen_blocker_identities: set[str] = set()
    for blocker in actual_blockers:
        identity = str(blocker.get("identity", ""))
        identity_key = identity.casefold()
        if identity_key in seen_blocker_identities:
            failures.append(f"multiple blocker classifications: {identity}")
        seen_blocker_identities.add(identity_key)
    if (
        fixture is not None
        and fixture_requires_goal_pause_handoff(fixture)
        and result.get("decision") == "stop_for_user"
        and not any(
            isinstance(gate, str) and "/goal pause" in gate
            for gate in result.get("open_gates", [])
        )
    ):
        failures.append(
            "active Goal with unavailable native pause lacks explicit /goal pause handoff"
        )
    for expected in oracle.get("required_classifications", []):
        allowed_states = expected["state"]
        if not isinstance(allowed_states, list):
            allowed_states = [allowed_states]
        matches = [
            finding
            for finding in actual_findings
            if finding_identity_matches(
                finding.get("identity", ""), expected["identity"]
            )
            and finding.get("domain") == expected["domain"]
            and finding.get("state") in allowed_states
        ]
        if not matches:
            failures.append(
                "missing classification: "
                f"{expected['identity']} {expected['domain']} {allowed_states}"
            )
    for expected_class in oracle.get("required_blocker_classes", []):
        if not any(
            item.get("class") == expected_class and item.get("blocking") is True
            for item in actual_blockers
        ):
            failures.append(f"missing blocking class: {expected_class}")
    for expected in oracle.get("required_blocker_classifications", []):
        matches = [
            item
            for item in actual_blockers
            if finding_identity_matches(item.get("identity", ""), expected["identity"])
            and item.get("class") == expected["class"]
            and item.get("blocking") is True
        ]
        if not matches:
            failures.append(
                f"missing blocking identity: {expected['identity']} {expected['class']}"
            )
    for expected in oracle.get("required_anchored_blockers", []):
        anchor = expected["anchor"].casefold()
        allowed_classes = expected["class"]
        if not isinstance(allowed_classes, list):
            allowed_classes = [allowed_classes]
        anchored_findings = [
            finding
            for finding in actual_findings
            if finding_has_anchor(finding, anchor)
        ]
        matches = [
            (finding, blocker)
            for finding in anchored_findings
            for blocker in actual_blockers
            if str(blocker.get("identity", "")).casefold()
            == str(finding.get("identity", "")).casefold()
            and blocker.get("class") in allowed_classes
            and blocker.get("blocking") is True
        ]
        if not matches:
            failures.append(
                f"missing anchored blocker: {expected['anchor']} {allowed_classes}"
            )
    for expected in oracle.get("required_anchored_classifications", []):
        anchor = expected["anchor"].casefold()
        allowed_states = expected["state"]
        if not isinstance(allowed_states, list):
            allowed_states = [allowed_states]
        matches = [
            finding
            for finding in actual_findings
            if finding_has_anchor(finding, anchor)
            and finding.get("domain") == expected["domain"]
            and finding.get("state") in allowed_states
        ]
        if not matches:
            failures.append(
                "missing anchored classification: "
                f"{expected['anchor']} {expected['domain']} {allowed_states}"
            )
    completion_claimed = (
        result.get("decision") == "complete"
        or result.get("protocol_may_complete") is True
    )
    if completion_claimed:
        if result.get("decision") != "complete" or not result.get(
            "protocol_may_complete"
        ):
            failures.append("completion decision and permission disagree")
        if result.get("open_gates"):
            failures.append("completion has nonempty open_gates")
        for blocker in actual_blockers:
            if blocker.get("blocking") is True:
                failures.append(
                    "completion has blocking finding: "
                    f"{blocker.get('identity', '<missing>')}"
                )
        accepted = oracle.get("accepted_baseline_failures", [])
        for finding in actual_findings:
            identity = finding.get("identity", "")
            state = finding.get("state")
            if state in {"candidate_new", "unknown"}:
                failures.append(f"completion has {state} finding: {identity}")
            if finding.get("domain") == "baseline_failure" and state == (
                "baseline_unchanged"
            ):
                accepted_matches = [
                    expected
                    for expected in accepted
                    if finding_identity_matches(identity, expected)
                ]
                if not accepted_matches:
                    failures.append(
                        f"completion has unaccepted baseline failure: {identity}"
                    )
                elif len(accepted_matches) > 1:
                    failures.append(
                        "completion has ambiguous accepted baseline failure: "
                        f"{identity} matches {accepted_matches!r}"
                    )
    return failures


def recovery_control_failures(
    *,
    primary: dict[str, Any],
    primary_thread_id: str | None,
    fresh: dict[str, Any],
    fresh_thread_id: str | None,
    expected_state: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []
    if not fresh_thread_id:
        failures.append("fresh recovery control emitted no thread id")
    elif fresh_thread_id == primary_thread_id:
        failures.append("fresh recovery control reused the resumed task")
    for field in sorted(RECOVERY_GATE_FIELDS):
        if fresh.get(field) != primary.get(field):
            failures.append(
                f"fresh recovery control disagrees on {field}: "
                f"{fresh.get(field)!r} != {primary.get(field)!r}"
            )
    primary_state = primary.get("recovery_state")
    fresh_state = fresh.get("recovery_state")
    if isinstance(primary_state, dict) and isinstance(fresh_state, dict):
        for field in sorted(RECOVERY_STATE_FIELDS):
            if normalized_recovery_value(
                field, fresh_state.get(field)
            ) != normalized_recovery_value(field, primary_state.get(field)):
                failures.append(
                    f"fresh recovery control disagrees on recovery_state.{field}"
                )
    elif fresh_state != primary_state:
        failures.append("fresh recovery control disagrees on recovery_state")
    if expected_state is not None:
        for label, state in (("primary", primary_state), ("fresh", fresh_state)):
            failures.extend(
                recovery_state_failures(
                    f"{label} recovery_state", state, expected_state
                )
            )
    return failures


def expected_recovery_state(
    native: dict[str, Any],
    fixture: dict[str, Any],
    transition: dict[str, Any],
) -> dict[str, Any]:
    configured = native["recovery_oracle"]
    return {
        "baseline_revision": fixture["commits"][0],
        "baseline_tree": fixture["trees"][0],
        "current_revision": transition["head"],
        "current_tree": transition["tree"],
        **configured,
    }


def evaluate_case(
    case: dict[str, Any],
    *,
    plugin: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    arm: str,
) -> dict[str, Any]:
    case_output = output / case["id"]
    case_output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix=f"happycodex-{case['id']}-") as raw:
        temp = Path(raw)
        repo = temp / "repo"
        fixture = build_fixture(case, repo)
        package = temp / "package"
        source_package = package_identities(plugin)
        copy_plugin_package(plugin, package, arm=arm)
        copied_package = package_identities(package)
        if copied_package != source_package:
            raise RuntimeError("copied package identities differ from evaluated source")
        input_digest = semantic_input_sha256_from_package(
            case,
            package_semantic_sha256=copied_package["semantic_sha256"],
            model=model,
            effort=effort,
            timeout=timeout,
            arm=arm,
        )
        tool_bin = prepare_native_tool_bin(temp)
        home, env = isolated_home(temp)
        installation = install_plugin(package, home, env)
        schema = temp / "response-schema.json"
        schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
        prompt = f"{EVALUATOR_CONTEXT}\n\n{case['prompt']}"
        native = case["fixture"].get("native_compaction_resume")
        config_args = [
            "-m",
            model,
            "-c",
            f'model_reasoning_effort="{effort}"',
            "-c",
            'approval_policy="never"',
            *permission_profile_args(
                tool_bin=tool_bin,
                user_home=temp / "user-home",
            ),
        ]
        fresh_config_args = [*config_args]
        if native:
            config_args.extend(
                [
                    "-c",
                    "model_auto_compact_token_limit="
                    f"{native['auto_compact_token_limit']}",
                    "-c",
                    'model_auto_compact_token_limit_scope="body_after_prefix"',
                ]
            )
        initial_prompt = (
            f"{EVALUATOR_CONTEXT}\n\n{native['prepare_prompt']}" if native else prompt
        )
        initial_argv = [
            "codex",
            "exec",
            "--json",
            *([] if native else ["--ephemeral"]),
            "--ignore-rules",
            "-C",
            str(repo),
            *config_args,
            "--output-schema",
            str(schema),
            *disabled_feature_args(),
            initial_prompt,
        ]
        started_at = datetime.now(timezone.utc)
        initial, initial_timed_out, initial_elapsed = invoke_codex(
            initial_argv,
            cwd=repo,
            env=env,
            timeout=timeout,
        )
        completed = initial
        elapsed = initial_elapsed
        timed_out = initial_timed_out
        raw_events = [initial.stdout]
        raw_stderr = [initial.stderr]
        commands = [[*initial_argv[:-1], "<prepare-prompt>" if native else "<prompt>"]]
        ended_at = datetime.now(timezone.utc)
        final: dict[str, Any] = {}
        usage_phases: list[dict[str, int]] = []
        thread_id: str | None = None
        resume_thread_id: str | None = None
        fresh_recovery_thread_id: str | None = None
        fresh_recovery_result: dict[str, Any] | None = None
        failures: list[str] = []
        native_receipt: dict[str, Any] | None = None
        recovery_expected: dict[str, Any] | None = None
        if initial.returncode == 0:
            try:
                initial_final, initial_usage, thread_id = parse_events(initial.stdout)
                usage_phases.append(initial_usage)
                if not native:
                    final = initial_final
                    failures.extend(
                        match_oracle(final, case["oracle"], fixture=case["fixture"])
                    )
            except (ValueError, RuntimeError) as exc:
                failures.append(str(exc))
        else:
            failures.append(f"codex initial exit {initial.returncode}")

        if native:
            before_resume = compaction_receipt(home, thread_id)
            native_receipt = {
                "auto_compact_token_limit": native["auto_compact_token_limit"],
                "before_resume": before_resume,
                "compaction_event_count": before_resume["compaction_event_count"],
                "resumed_same_thread": False,
            }
            if before_resume["compaction_event_count"] < 1:
                failures.append("native compaction event unavailable before resume")
            if thread_id:
                pre_transition_status = run(
                    ["git", "status", "--porcelain=v1", "--untracked-files=all"],
                    cwd=repo,
                ).stdout
                pre_transition_files = workspace_file_manifest(repo)
                if pre_transition_status != fixture["status_before"]:
                    failures.append("native preparation changed fixture status")
                if pre_transition_files != fixture["files"]:
                    failures.append("native preparation changed fixture content")
                transition = apply_post_compaction_transition(
                    repo, native["post_compaction_transition"], fixture
                )
                recovery_expected = expected_recovery_state(native, fixture, transition)
                native_receipt["post_compaction_transition"] = transition
                # Native proof path: codex exec resume <thread> <prompt>.
                resume_argv = [
                    "codex",
                    "exec",
                    "resume",
                    "--json",
                    "--ignore-rules",
                    *config_args,
                    "--output-schema",
                    str(schema),
                    *disabled_feature_args(),
                    thread_id,
                    prompt,
                ]
                resumed, resume_timed_out, resume_elapsed = invoke_codex(
                    resume_argv,
                    cwd=repo,
                    env=env,
                    timeout=timeout,
                )
                completed = resumed
                elapsed += resume_elapsed
                timed_out = timed_out or resume_timed_out
                ended_at = datetime.now(timezone.utc)
                raw_events.append(resumed.stdout)
                raw_stderr.append(resumed.stderr)
                commands.append([*resume_argv[:-1], "<prompt>"])
                if resumed.returncode == 0:
                    try:
                        final, resume_usage, resume_thread_id = parse_events(
                            resumed.stdout
                        )
                        usage_phases.append(resume_usage)
                        failures.extend(
                            match_oracle(
                                final,
                                case["oracle"],
                                expected_recovery_state=recovery_expected,
                                fixture=case["fixture"],
                            )
                        )
                    except (ValueError, RuntimeError) as exc:
                        failures.append(str(exc))
                else:
                    failures.append(f"codex resume exit {resumed.returncode}")
                native_receipt["resumed_same_thread"] = resume_thread_id == thread_id
                native_receipt["after_resume"] = compaction_receipt(home, thread_id)
                if not native_receipt["resumed_same_thread"]:
                    failures.append("resume did not report the same native thread")

                fresh_prompt = (
                    f"{EVALUATOR_CONTEXT}\n\n{native['fresh_recovery_prompt']}"
                )
                fresh_argv = [
                    "codex",
                    "exec",
                    "--json",
                    "--ephemeral",
                    "--ignore-rules",
                    "-C",
                    str(repo),
                    *fresh_config_args,
                    "--output-schema",
                    str(schema),
                    *disabled_feature_args(),
                    fresh_prompt,
                ]
                fresh_completed, fresh_timed_out, fresh_elapsed = invoke_codex(
                    fresh_argv,
                    cwd=repo,
                    env=env,
                    timeout=timeout,
                )
                completed = fresh_completed
                elapsed += fresh_elapsed
                timed_out = timed_out or fresh_timed_out
                ended_at = datetime.now(timezone.utc)
                raw_events.append(fresh_completed.stdout)
                raw_stderr.append(fresh_completed.stderr)
                commands.append([*fresh_argv[:-1], "<fresh-recovery-prompt>"])
                if fresh_completed.returncode == 0:
                    try:
                        (
                            fresh_recovery_result,
                            fresh_usage,
                            fresh_recovery_thread_id,
                        ) = parse_events(fresh_completed.stdout)
                        usage_phases.append(fresh_usage)
                        failures.extend(
                            match_oracle(
                                fresh_recovery_result,
                                case["oracle"],
                                expected_recovery_state=recovery_expected,
                                fixture=case["fixture"],
                            )
                        )
                        failures.extend(
                            recovery_control_failures(
                                primary=final,
                                primary_thread_id=thread_id,
                                fresh=fresh_recovery_result,
                                fresh_thread_id=fresh_recovery_thread_id,
                                expected_state=recovery_expected,
                            )
                        )
                    except (ValueError, RuntimeError) as exc:
                        failures.append(str(exc))
                else:
                    failures.append(
                        f"codex fresh recovery exit {fresh_completed.returncode}"
                    )
                native_receipt["fresh_control"] = {
                    "thread_id": fresh_recovery_thread_id,
                    "distinct_from_resumed_task": (
                        fresh_recovery_thread_id is not None
                        and fresh_recovery_thread_id != thread_id
                    ),
                    "no_resume_handle": True,
                    "no_conversation_summary": True,
                    "prompt_sha256": sha256_bytes(fresh_prompt.encode()),
                    "equivalent_gate_fields": [
                        *sorted(RECOVERY_GATE_FIELDS),
                        "recovery_state",
                    ],
                    "allowed_label_differences": {
                        field: [final.get(field), fresh_recovery_result.get(field)]
                        for field in ("decision", "execplan_condition")
                        if fresh_recovery_result is not None
                        and final.get(field) != fresh_recovery_result.get(field)
                    },
                }
            else:
                failures.append("native preparation emitted no resumable thread id")

        status_after = run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=repo
        ).stdout
        if status_after != fixture["status_before"]:
            failures.append("read-only task changed fixture status")
        files_after = workspace_file_manifest(repo)
        if files_after != fixture["files"]:
            failures.append("read-only task changed fixture content")

        required_usage = ("input_tokens", "cached_input_tokens", "output_tokens")
        expected_phases = 3 if native else 1
        usage = combined_usage(*usage_phases)
        if len(usage_phases) != expected_phases or not all(
            all(isinstance(phase.get(key), int) for key in required_usage)
            for phase in usage_phases
        ):
            failures.append("required token telemetry unavailable")
            uncached: int | None = None
        else:
            uncached = usage["input_tokens"] - usage["cached_input_tokens"]
        phase_events_digests = [sha256_bytes(item.encode()) for item in raw_events]
        phase_stderr_digests = [sha256_bytes(item.encode()) for item in raw_stderr]
        events_digest = (
            phase_events_digests[0]
            if len(phase_events_digests) == 1
            else canonical_sha256(phase_events_digests)
        )
        stderr_digest = (
            phase_stderr_digests[0]
            if len(phase_stderr_digests) == 1
            else canonical_sha256(phase_stderr_digests)
        )
        metadata = {
            "schema_version": 1,
            "case": case["id"],
            "covers": case["covers"],
            "arm": arm,
            "model": model,
            "effort": effort,
            "codex_cli_version": run(
                ["codex", "--version"], cwd=repo, env=env
            ).stdout.strip(),
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "timeout_seconds": timeout,
            "timed_out": timed_out,
            "elapsed_seconds": round(elapsed, 3),
            "exit_code": completed.returncode,
            "thread_id": thread_id,
            "resume_thread_id": resume_thread_id,
            "fresh_recovery_thread_id": fresh_recovery_thread_id,
            "prompt_sha256": sha256_bytes(prompt.encode()),
            "prepare_prompt_sha256": (
                sha256_bytes(initial_prompt.encode()) if native else None
            ),
            "semantic_input_sha256": input_digest,
            "identities": {
                "engine": engine_inventory(ROOT),
                "package": copied_package,
            },
            "filesystem_isolation": {
                **FILESYSTEM_ISOLATION_POLICY,
                "workspace_root": "<case-temp>/repo",
                "native_tool_root": "<case-temp>/bin",
            },
            "fixture": fixture,
            "installation": installation,
            "usage": usage,
            "usage_phases": usage_phases,
            "uncached_input_tokens": uncached,
            "events_sha256": events_digest,
            "phase_events_sha256": phase_events_digests,
            "stderr_sha256": stderr_digest,
            "phase_stderr_sha256": phase_stderr_digests,
            "native_compaction": native_receipt,
            "result": final,
            "fresh_recovery_result": fresh_recovery_result,
            "oracle_failures": failures,
            "passed": not failures,
            "command": commands[-1],
            "commands": commands,
        }
        if native:
            (case_output / "prepare-events.jsonl").write_text(
                raw_events[0], encoding="utf-8"
            )
            (case_output / "prepare-stderr.txt").write_text(
                raw_stderr[0], encoding="utf-8"
            )
            if len(raw_events) > 2:
                (case_output / "fresh-recovery-events.jsonl").write_text(
                    raw_events[2], encoding="utf-8"
                )
                (case_output / "fresh-recovery-stderr.txt").write_text(
                    raw_stderr[2], encoding="utf-8"
                )
        primary_index = 1 if native and len(raw_events) > 1 else -1
        (case_output / "events.jsonl").write_text(
            raw_events[primary_index], encoding="utf-8"
        )
        (case_output / "stderr.txt").write_text(
            raw_stderr[primary_index], encoding="utf-8"
        )
        (case_output / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return metadata


def text_sha256(value: Any) -> str:
    return sha256_bytes(str(value).encode())


def sanitized_recovery_receipt(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    receipt: dict[str, Any] = {"recovery_state_sha256": canonical_sha256(value)}
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        item = value.get(field)
        receipt[field] = (
            item
            if isinstance(item, str) and re.fullmatch(r"[0-9a-f]{40}", item)
            else None
        )
    for field in ("writer", "milestone_phase", "next_action", "worktree"):
        receipt[field] = value.get(field)
    pending = value.get("pending_gates", [])
    receipt["pending_gates"] = pending if isinstance(pending, list) else []
    tests = value.get("tests", {})
    markers = tests.get("marker_ids", []) if isinstance(tests, dict) else []
    receipt["tests"] = {
        key: tests.get(key) if isinstance(tests, dict) else None
        for key in ("passed", "failed", "accepted_failures")
    }
    receipt["tests"].update(
        {
            "marker_ids_count": len(markers) if isinstance(markers, list) else 0,
            "marker_ids_sha256": canonical_sha256(markers),
        }
    )
    agents = value.get("live_agents", [])
    receipt["live_agents"] = (
        [
            {
                "id_sha256": text_sha256(agent.get("id", "")),
                "status": agent.get("status"),
                "receipt_reproduced": agent.get("receipt_reproduced"),
            }
            for agent in agents
            if isinstance(agent, dict)
        ]
        if isinstance(agents, list)
        else []
    )
    marker_ids = value.get("marker_ids", [])
    receipt["marker_ids_count"] = len(marker_ids) if isinstance(marker_ids, list) else 0
    receipt["marker_ids_sha256"] = canonical_sha256(marker_ids)
    return receipt


def sanitized_result_receipt(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        return {"result_sha256": canonical_sha256(value)}
    receipt: dict[str, Any] = {"result_sha256": canonical_sha256(value)}
    for field in sorted(PERMISSION_FIELDS):
        receipt[field] = value.get(field)
    findings = value.get("finding_classifications", [])
    receipt["finding_classifications"] = (
        [
            {
                "identity_sha256": text_sha256(item.get("identity", "")),
                "domain": item.get("domain"),
                "state": item.get("state"),
                "anchors_count": len(item.get("anchors", []))
                if isinstance(item.get("anchors", []), list)
                else 0,
                "anchors_sha256": canonical_sha256(item.get("anchors", [])),
            }
            for item in findings
            if isinstance(item, dict)
        ]
        if isinstance(findings, list)
        else []
    )
    blockers = value.get("blocker_classifications", [])
    receipt["blocker_classifications"] = (
        [
            {
                "identity_sha256": text_sha256(item.get("identity", "")),
                "class": item.get("class"),
                "blocking": item.get("blocking"),
                "reason_sha256": text_sha256(item.get("reason", "")),
            }
            for item in blockers
            if isinstance(item, dict)
        ]
        if isinstance(blockers, list)
        else []
    )
    for field in ("open_gates", "evidence"):
        items = value.get(field, [])
        receipt[f"{field}_count"] = len(items) if isinstance(items, list) else 0
        receipt[f"{field}_sha256"] = canonical_sha256(items)
    receipt["reason_sha256"] = text_sha256(value.get("reason", ""))
    receipt["recovery_state"] = sanitized_recovery_receipt(value.get("recovery_state"))
    return receipt


def sanitized_compaction_phase(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return {
        "phase_sha256": canonical_sha256(value),
        "rollout_path_sha256": text_sha256(value.get("rollout_path", "")),
        "rollout_sha256": value.get("rollout_sha256"),
        "compaction_event_count": value.get("compaction_event_count"),
        "context_compacted_marker_count": value.get("context_compacted_marker_count"),
        "event_types": value.get("event_types", []),
        "rollout_match_count": value.get("rollout_match_count"),
    }


def sanitized_native_compaction_receipt(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    receipt = {
        "native_compaction_sha256": canonical_sha256(value),
        "auto_compact_token_limit": value.get("auto_compact_token_limit"),
        "compaction_event_count": value.get("compaction_event_count"),
        "resumed_same_thread": value.get("resumed_same_thread"),
        "before_resume": sanitized_compaction_phase(value.get("before_resume")),
        "after_resume": sanitized_compaction_phase(value.get("after_resume")),
    }
    if "post_compaction_transition" in value:
        receipt["post_compaction_transition_sha256"] = canonical_sha256(
            value["post_compaction_transition"]
        )
    fresh = value.get("fresh_control")
    if isinstance(fresh, dict):
        receipt["fresh_control"] = {
            "fresh_control_sha256": canonical_sha256(fresh),
            "thread_id_sha256": text_sha256(fresh.get("thread_id", "")),
            "distinct_from_resumed_task": fresh.get("distinct_from_resumed_task"),
            "no_resume_handle": fresh.get("no_resume_handle"),
            "no_conversation_summary": fresh.get("no_conversation_summary"),
            "prompt_sha256": fresh.get("prompt_sha256"),
            "equivalent_gate_fields": fresh.get("equivalent_gate_fields", []),
            "allowed_label_differences_sha256": canonical_sha256(
                fresh.get("allowed_label_differences", {})
            ),
        }
    return receipt


def sanitized_case_receipt(
    result: dict[str, Any], *, metadata_sha256: str
) -> dict[str, Any]:
    installation = result.get("installation", {})
    safe_installation = {
        key: installation.get(key)
        for key in (
            "source_skill_sha256",
            "installed_skill_sha256",
            "source_package_manifest_sha256",
            "installed_package_manifest_sha256",
        )
    }
    plugin = installation.get("plugin", {})
    if plugin:
        safe_installation["plugin_sha256"] = canonical_sha256(plugin)
    receipt = {
        "schema_version": 1,
        "engine_generation": "0.4",
        "id": result["case"],
        "metadata_sha256": metadata_sha256,
        "installation": safe_installation,
        **{
            key: result.get(key)
            for key in (
                "model",
                "effort",
                "timeout_seconds",
                "timed_out",
                "elapsed_seconds",
                "exit_code",
                "semantic_input_sha256",
                "identities",
                "events_sha256",
                "stderr_sha256",
                "usage",
                "usage_phases",
                "uncached_input_tokens",
                "passed",
            )
        },
        "result": sanitized_result_receipt(result.get("result")),
        "fresh_recovery_result": sanitized_result_receipt(
            result.get("fresh_recovery_result")
        ),
        "oracle_failures": {
            "count": len(result.get("oracle_failures", [])),
            "sha256": canonical_sha256(result.get("oracle_failures", [])),
        },
        "native_compaction": sanitized_native_compaction_receipt(
            result.get("native_compaction")
        ),
    }
    for field in ("thread_id", "resume_thread_id", "fresh_recovery_thread_id"):
        receipt[f"{field}_sha256"] = text_sha256(result.get(field, ""))
    isolation = result.get("filesystem_isolation", {})
    receipt["filesystem_isolation"] = {
        key: isolation.get(key)
        for key in (
            "mechanism",
            "profile",
            "default_access",
            "workspace",
            "nonworkspace",
            "native_tools",
            "network",
            "selection",
        )
    }
    receipt["filesystem_isolation"]["policy_sha256"] = canonical_sha256(isolation)
    return receipt


def resolve_output_path(requested: Path | None, *, plugin: Path) -> Path:
    output = (
        requested.expanduser().resolve()
        if requested is not None
        else Path(tempfile.mkdtemp(prefix="happycodex-corpus-results-")).resolve()
    )
    root = ROOT.resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError("raw output must stay outside the repository")
    plugin = plugin.expanduser().resolve()
    if output == plugin or output.is_relative_to(plugin):
        raise ValueError("raw output must stay outside the evaluated plugin")
    if output.exists() and any(output.iterdir()):
        raise ValueError("raw output directory must be empty")
    return output


def run_command(args: Any) -> int:
    cases = load_cases()
    if args.list:
        for case_id in cases:
            print(case_id)
        return 0
    selected = args.cases or list(cases)
    unknown = set(selected) - set(cases)
    if unknown:
        raise SystemExit(f"unknown cases: {sorted(unknown)}")
    if args.dry_run:
        print(
            json.dumps({"cases": selected, "coverage": sorted(REQUIRED_TAGS)}, indent=2)
        )
        return 0
    plugin = args.plugin.resolve()
    try:
        output = resolve_output_path(args.output, plugin=plugin)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    output.mkdir(parents=True, exist_ok=True)
    results = [
        evaluate_case(
            cases[case_id],
            plugin=plugin,
            output=output,
            model=args.model,
            effort=args.effort,
            timeout=args.timeout,
            arm=args.arm,
        )
        for case_id in selected
    ]
    summary = {
        "schema_version": 1,
        "engine_generation": "0.4",
        "arm": args.arm,
        "model": args.model,
        "effort": args.effort,
        "timeout_seconds": args.timeout,
        "passed": sum(result["passed"] for result in results),
        "total": len(results),
        "uncached_input_tokens": sum(
            result["uncached_input_tokens"]
            for result in results
            if result["uncached_input_tokens"] is not None
        ),
        "telemetry_complete": all(
            result["uncached_input_tokens"] is not None for result in results
        ),
        "output_tokens": sum(
            result["usage"].get("output_tokens", 0) for result in results
        ),
        "elapsed_seconds": round(
            sum(result["elapsed_seconds"] for result in results), 3
        ),
        "cases": [
            sanitized_case_receipt(
                result,
                metadata_sha256=sha256_bytes(
                    (output / result["case"] / "metadata.json").read_bytes()
                ),
            )
            for result in results
        ],
    }
    write_new_json(output / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] == summary["total"] else 1
