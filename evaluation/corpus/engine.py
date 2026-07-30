#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Any, Callable

from evaluation.core.identity import (
    FILESYSTEM_ISOLATION_POLICY,
    PACKAGE_PATHS,
    PERMISSION_PROFILE,
    PUBLIC_02_ARM,
    PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
    PUBLIC_02_SKILL_ENTRIES,
    RECOVERY_MANIFEST_PATTERN,
    RECOVERY_STATE_FIELDS,
    canonical_sha256,
    case_semantic_sha256,
    codex_identity,
    engine_inventory,
    invocation_profile,
    package_identities,
    package_manifest_sha256,
    recovery_manifest_projection,
    recovery_summary_consistent,
    selected_package_paths,
    sha256_bytes,
    validate_invocation_profile,
    workspace_file_manifest,
)
from evaluation.core.ledger import validate_case_input as validate_case
from evaluation.core.schema import CONTRACTS, validate_named
from evaluation.semantic import (
    build_report,
    parse_machine_facts,
    parse_model_observation,
    parse_report,
    report_to_raw,
)

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evaluation" / "cases"
CORPUS_MAX_WORKERS = 4
RECOVERY_MANIFEST_PATH = "docs/execplans/recovery-manifest.json"
BASE_COMMAND_PATHS = ("/usr/local/bin", "/usr/bin", "/bin")
PARENT_CONTEXT_ENV = ("CODEX_REMOTE_PAYLOAD", "CODEX_THREAD_ID", "PWD", "OLDPWD")
DISABLED_FEATURES = (
    "apps",
    "goals",
    "hooks",
    "memories",
    "remote_plugin",
    "multi_agent",
)
FIXED_GIT_DATE = "2000-01-01T00:00:00+00:00"


OUTPUT_SCHEMA = CONTRACTS["schemas"]["model_observation"]


def provider_transport_schema(
    value: Any,
    definitions: dict[str, Any] | None = None,
) -> Any:
    """Inline internal bare refs and omit provider-rejected uniqueness hints."""
    known = CONTRACTS["schemas"] if definitions is None else definitions

    def project(item: Any, stack: tuple[str, ...]) -> Any:
        if isinstance(item, dict):
            if "$ref" in item:
                if set(item) != {"$ref"} or type(item["$ref"]) is not str:
                    raise ValueError("provider schema requires one bare reference")
                name = item["$ref"]
                if name not in known:
                    raise ValueError(f"unknown provider schema reference: {name}")
                if name in stack:
                    raise ValueError(f"cyclic provider schema reference: {name}")
                return project(known[name], (*stack, name))
            return {
                key: project(child, stack)
                for key, child in item.items()
                if key != "uniqueItems"
            }
        if isinstance(item, list):
            return [project(child, stack) for child in item]
        return item

    return project(value, ())


def validate_output_result(value: Any) -> dict[str, Any]:
    try:
        validated = validate_named(CONTRACTS, "model_observation", value)
    except ValueError as exc:
        required = set(OUTPUT_SCHEMA["required"])
        if isinstance(value, dict) and set(value) != required:
            raise ValueError("result top-level fields are invalid") from exc
        raise
    parse_model_observation(validated)
    return validated
REQUIRED_TAGS = {
    "request-paraphrase", "unsupported-amendment", "uncertain-qualification",
    "midflight-escalation", "subthreshold-control", "clean-qualifying-control",
    "missed-boundary", "legacy-path", "missing-worker", "missing-deploy",
    "pre-freeze-compaction", "post-freeze-compaction", "lost-scout",
    "dirty-untracked", "baseline-failure", "authorized-rebaseline", "no-commit",
    "secret-output", "baseline-secret", "review-anchoring", "declared-dependency",
    "ledger-review-mismatch", "review-fallback", "goal-divergence", "submodule",
    "multi-repository", "omitted-diff-unit", "truncated-search",
    "persistence-transition", "concurrency-transition", "receipt-mismatch",
    "review-admin-cycle", "repository-policy", "exact-final-positive",
    "archive-positive", "no-commit-unselected",
}
IDENTITY_PROJECTION_TEXT = (
    "Use each explicitly labeled material marker, locator, digest, or path as one "
    "exact, nonblank, stable identity; paraphrases and aliases are not equivalent."
)
EVALUATOR_CONTEXT = (
    "This invocation is an observational checkpoint only. RED-test edits are product "
    "writes. Report observations only; the evaluator derives the sole NextAction. "
    "Put every material finding and its optional blocker in one finding with one exact "
    f"shared id. {IDENTITY_PROJECTION_TEXT} Encode each anchor as exactly one typed "
    "object: repository-relative path, lifecycle marker, or labeled Git/SHA-256 "
    "digest. Use repository `fixture` for fixture paths. Use open_gates only from the "
    "closed control gate vocabulary and copy recovery.pending_gates in checkpoint "
    "order without inferring downstream gates. Recovery controls must include every "
    "durable Git, plan, test, worktree, delegated-agent, and Recovery Manifest fact; "
    "live_agents contains delegated receipts, never the Root writer. Do not inspect "
    "evaluator code or hidden oracles."
)
EXPECTED_CANDIDATE_SKILL_ENTRIES = frozenset(
    {
        "SKILL.md",
        "agents",
        "agents/openai.yaml",
        "references",
        "references/execplan.md",
        "scripts",
        "scripts/resource_claim.py",
    }
)
EXPECTED_PUBLIC_02_SKILL_ENTRIES = frozenset(PUBLIC_02_SKILL_ENTRIES)
EXPECTED_PUBLIC_02_PACKAGE_MANIFEST_SHA256 = PUBLIC_02_PACKAGE_ARTIFACT_SHA256
EXPECTED_SKILL_ENTRIES_BY_ARM = {
    "candidate": EXPECTED_CANDIDATE_SKILL_ENTRIES,
    PUBLIC_02_ARM: EXPECTED_PUBLIC_02_SKILL_ENTRIES,
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
    return case_semantic_sha256(
        case,
        evaluator_bundle_sha256=inventory["manifest_sha256"],
        package_semantic_sha256=package_semantic_sha256,
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


def _exact_object(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"invalid {label}")
    return value


def _unique_strings(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(type(item) is not str or not item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"invalid {label}")
    return value


def load_cases(cases_root: Path | None = None) -> dict[str, dict[str, Any]]:
    root = CASES if cases_root is None else cases_root.resolve()
    loaded = {}
    for path in sorted(root.glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        validate_case(case, path)
        if case["id"] in loaded:
            raise ValueError(f"duplicate case id: {case['id']}")
        loaded[case["id"]] = case
    covered = {tag for case in loaded.values() for tag in case["covers"]}
    if REQUIRED_TAGS - covered:
        raise ValueError("corpus is missing required coverage")
    return loaded


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
    if config.get("mode", "synthetic") == "source":
        baseline, candidate = baseline_source, candidate_source
    else:
        if excluded is None:
            raise ValueError("synthetic review requires an excluded path")
        baseline = run(
            [
                "git",
                "commit-tree",
                product_tree(repo, baseline_source, excluded),
                "-m",
                "synthetic baseline",
            ],
            cwd=repo,
            env=deterministic_git_env(),
        ).stdout.strip()
        candidate = run(
            [
                "git",
                "commit-tree",
                product_tree(repo, candidate_source, excluded),
                "-p",
                baseline,
                "-m",
                "synthetic candidate",
            ],
            cwd=repo,
            env=deterministic_git_env(),
        ).stdout.strip()
    prefix = f"refs/happycodex-eval/{config['name']}"
    for suffix, revision in (("baseline", baseline), ("candidate", candidate)):
        if run(["git", "update-ref", f"{prefix}/{suffix}", revision], cwd=repo).returncode:
            raise RuntimeError("review ref update failed")
    diff = run(["git", "diff", "--name-only", baseline, candidate], cwd=repo).stdout.splitlines()
    limit = config.get("coverage_limit", len(diff))
    inspected, omitted = diff[:limit], diff[limit:]
    tail = config.get("decisive_tail", "")
    if type(limit) is not int or limit <= 0 or tail and tail not in omitted:
        raise ValueError("invalid review coverage boundary")
    manifests = {
        "source_baseline": product_manifest_sha256_at(repo, baseline_source, excluded),
        "source_candidate": product_manifest_sha256_at(repo, candidate_source, excluded),
        "projected_baseline": product_manifest_sha256_at(repo, baseline, None),
        "projected_candidate": product_manifest_sha256_at(repo, candidate, None),
    }
    if manifests["source_baseline"] != manifests["projected_baseline"] or (
        manifests["source_candidate"] != manifests["projected_candidate"]
    ):
        raise ValueError("review projection differs from source product")
    brief = neutral_review_brief(
        operative_request=config.get("operative_request", "verbatim task"),
        scope=f"{baseline_source}..{candidate_source}",
        baseline_failures=config.get("baseline_failures", []),
        objective_verification={
            "diff_unit_count": len(diff),
            "diff_units_sha256": canonical_sha256(diff),
            **{f"{key}_manifest_sha256": value for key, value in manifests.items()},
        },
        exclusions=[excluded] if excluded else [],
        writer_narrative=config.get("writer_narrative", ""),
        historical_findings=config.get("historical_findings", []),
    )
    complete = not omitted
    fields = {
        "terminal_status": "complete",
        "configured_model_source": config.get(
            "configured_model_source", "evaluator-default"
        ),
        "effective_model": config.get("model", "gpt-5.6-sol"),
        "effective_effort": config.get("effort", "max"),
        "baseline_commit": baseline,
        "candidate_commit": candidate,
        **{f"{key}_manifest_sha256": value for key, value in manifests.items()},
        "phase_1_inventory_frozen": "true",
        "phase_1_correctness_complete": str(complete).lower(),
        "phase_1_diff_unit_coverage": "complete" if complete else "incomplete",
        "diff_units": ",".join(diff),
        "inspected_diff_units": ",".join(inspected),
        "omitted_diff_units": ",".join(omitted),
        "decisive_tail": tail or "none",
        "independent_obligations": ",".join(config.get("obligations", [])),
        "contract_mapping": config.get("contract_mapping", ""),
        "brief": brief["brief"],
        "brief_sha256": brief["brief_sha256"],
        "truncation": "none" if complete else "detected",
        "limitations": "none" if complete else f"{len(omitted)} omitted diff units",
    }
    receipt = "".join(f"{key}={value}\n" for key, value in fields.items())
    stored = run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input_text=receipt)
    output_blob = stored.stdout.strip()
    if stored.returncode or run(
        ["git", "update-ref", f"{prefix}/output", output_blob], cwd=repo
    ).returncode:
        raise RuntimeError("review receipt persistence failed")
    challenger_blob = challenger_sha256 = ""
    challenger_name = config.get("challenger_receipt")
    if challenger_name:
        matches = [item for item in challenger_receipts if item["name"] == challenger_name]
        if len(matches) != 1 or matches[0]["ref"] != f"{prefix}/challenger":
            raise ValueError("review requires one matching challenger")
        challenger_blob, challenger_sha256 = matches[0]["blob"], matches[0]["sha256"]
    return {
        "baseline_commit": baseline,
        "candidate_commit": candidate,
        "source_baseline_commit": baseline_source,
        "source_candidate_commit": candidate_source,
        "source_baseline_manifest_sha256": manifests["source_baseline"],
        "source_candidate_manifest_sha256": manifests["source_candidate"],
        "brief": brief,
        "output_blob": output_blob,
        "output_sha256": sha256_bytes(receipt.encode()),
        "challenger_blob": challenger_blob,
        "challenger_sha256": challenger_sha256,
        "ref_prefix": prefix,
        "diff_unit_count": len(diff),
        "diff_units": diff,
        "coverage_limit": limit,
        "inspected_diff_units": inspected,
        "omitted_diff_units": omitted,
        "decisive_tail": tail,
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
    members = {
        f"skills/happycodex/{relative}" for relative in skill_entries
    }
    return EXPECTED_COMMON_PACKAGE_ENTRIES | members | {
        parent.as_posix()
        for member in members
        for parent in Path(member).parents
        if parent.as_posix() not in {"", "."}
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
    source_auth = source_home.resolve() / "auth.json"
    if not source_auth.is_file():
        raise RuntimeError(f"Codex auth unavailable at expected path: {source_auth}")
    tool_bin = prepare_native_tool_bin(parent)
    home = parent / "codex-home"
    home.mkdir()
    user_home = parent / "user-home"
    user_home.mkdir()
    auth = home / "auth.json"
    shutil.copyfile(source_auth, auth)
    auth.chmod(0o600)
    env = os.environ.copy()
    for key in PARENT_CONTEXT_ENV:
        env.pop(key, None)
    env["HOME"] = str(user_home)
    env["CODEX_HOME"] = str(home)
    env["PATH"] = os.pathsep.join((str(tool_bin), *BASE_COMMAND_PATHS))
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


_EVENT_BINDING_FIELDS = {
    "provider", "session_id", "thread_id", "action_id", "launch_key"
}
_USAGE_FIELDS = {
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
}
_PREFIX_ITEM_FIELDS = {
    "collab_tool_call": {
        "agents_states", "id", "prompt", "receiver_thread_ids",
        "sender_thread_id", "status", "tool", "type",
    },
    "command_execution": {
        "aggregated_output", "command", "exit_code", "id", "status", "type",
    },
    "todo_list": {"id", "items", "type"},
    "web_search": {"action", "id", "query", "type"},
}


def _exact_event(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"invalid terminal event: {label}")
    return value


def _event_binding(value: Any) -> dict[str, Any]:
    binding = _exact_event(value, _EVENT_BINDING_FIELDS, "binding")
    if (
        any(
            type(binding[field]) is not str or not binding[field]
            for field in ("provider", "session_id", "action_id", "launch_key")
        )
        or re.fullmatch(r"[0-9a-f]{64}", binding["launch_key"]) is None
        or (
            binding["thread_id"] is not None
            and (type(binding["thread_id"]) is not str or not binding["thread_id"])
        )
    ):
        raise ValueError("invalid terminal event binding")
    return binding


def _prefix_item(value: Any, allowed: set[str]) -> dict[str, Any]:
    item_type = value.get("type") if isinstance(value, dict) else None
    fields = _PREFIX_ITEM_FIELDS.get(item_type)
    if (
        item_type not in allowed
        or fields is None
        or set(value) != fields
        or type(value["id"]) is not str
        or not value["id"]
    ):
        raise ValueError("terminal prefix item is outside invocation profile")
    return value


def _same_prefix(started: dict[str, Any], completed: dict[str, Any]) -> bool:
    if started["id"] != completed["id"] or started["type"] != completed["type"]:
        return False
    item_type = started["type"]
    if item_type == "collab_tool_call":
        fields = ("tool", "sender_thread_id", "receiver_thread_ids", "prompt")
    elif item_type == "command_execution":
        fields = ("command",)
    elif item_type == "web_search":
        fields = tuple(started)
    else:
        return True
    return all(started[field] == completed[field] for field in fields)


def parse_events(
    stdout: str,
    *,
    binding: dict[str, Any],
    invocation_profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int], str, dict[str, Any]]:
    expected = _event_binding(binding)
    profile = validate_invocation_profile(invocation_profile)
    allowed = set(profile["tools"]["event_item_types"])
    lines = stdout.splitlines()
    if len(lines) < 4 or any(not line for line in lines):
        raise ValueError("terminal stream lacks unique completion EOF")
    try:
        events = [json.loads(line) for line in lines]
    except json.JSONDecodeError as exc:
        raise ValueError("invalid terminal event JSON") from exc
    thread = _exact_event(events[0], {"type", "thread_id"}, "thread")
    turn = _exact_event(events[1], {"type"}, "turn")
    thread_id = thread["thread_id"]
    if (
        thread["type"] != "thread.started"
        or type(thread_id) is not str
        or not thread_id
        or expected["thread_id"] not in {None, thread_id}
        or turn["type"] != "turn.started"
    ):
        raise ValueError("terminal thread or turn binding mismatch")
    pending = {}
    terminal = None
    terminal_ordinal = None
    for ordinal, raw in enumerate(events[2:-1], 2):
        event = _exact_event(raw, {"type", "item"}, "item")
        item = event["item"]
        item_type = item.get("type") if isinstance(item, dict) else None
        item_id = item.get("id") if isinstance(item, dict) else None
        if event["type"] == "item.completed" and item_type == "agent_message":
            if terminal is not None:
                raise ValueError("duplicate terminal agent result")
            terminal = _exact_event(item, {"id", "type", "text"}, "agent result")
            terminal_ordinal = ordinal
            continue
        item = _prefix_item(item, allowed)
        if terminal is not None:
            raise ValueError("prefix event follows terminal result")
        if event["type"] == "item.started":
            if item_id in pending:
                raise ValueError("duplicate terminal prefix start")
            pending[item_id] = item
        elif event["type"] == "item.updated":
            if item_type != "todo_list" or item_id not in pending:
                raise ValueError("invalid terminal prefix update")
        elif event["type"] == "item.completed":
            started = pending.pop(item_id, None)
            if started is None or not _same_prefix(started, item):
                raise ValueError("terminal prefix binding changed")
        else:
            raise ValueError("unknown terminal event shape")
    if pending or terminal is None or type(terminal["text"]) is not str:
        raise ValueError("terminal item sequence is incomplete")
    try:
        final = json.loads(terminal["text"])
    except json.JSONDecodeError as exc:
        raise ValueError("terminal agent result is not JSON") from exc
    completion = _exact_event(events[-1], {"type", "usage"}, "completion")
    validate_output_result(final)
    usage = _exact_event(completion["usage"], _USAGE_FIELDS, "usage")
    if (
        completion["type"] != "turn.completed"
        or not isinstance(final, dict)
        or any(type(usage[field]) is not int or usage[field] < 0 for field in usage)
    ):
        raise ValueError("invalid terminal result or usage completion")
    stream_sha256 = sha256_bytes(stdout.encode())
    turn_id = canonical_sha256(
        {
            "thread_id": thread_id,
            "action_id": expected["action_id"],
            "launch_key": expected["launch_key"],
            "terminal_ordinal": terminal_ordinal,
            "stream_sha256": stream_sha256,
        }
    )
    projection = {
        "provenance": "validated_invocation+native_stream",
        "provider": expected["provider"],
        "session_id": expected["session_id"],
        "thread_id": thread_id,
        "turn_id": turn_id,
        "action_id": expected["action_id"],
        "launch_key": expected["launch_key"],
        "result_id": terminal["id"],
        "result_sha256": canonical_sha256(final),
        "stream_sha256": stream_sha256,
        "terminal_ordinal": terminal_ordinal,
    }
    return final, usage, thread_id, projection


_RESULT_CONTEXT_FIELDS = frozenset(
    {
        "task_id",
        "root_task_id",
        "executor_task_id",
        "owner_label",
        "destination_id",
        "lineage_digest",
        "role_config_digest",
        "repository_digest",
        "outcome_digest",
        "invocation_profile",
        "accepted_baseline_failures",
    }
)
def _repository_binding_digest(
    case_id: str,
    baseline_revision: str,
    baseline_tree: str,
) -> str:
    return canonical_sha256(
        {
            "domain": "happycodex/0.6.5/repository",
            "repositories": [
                {
                    "namespace": f"case:{case_id}",
                    "baseline_revision": baseline_revision,
                    "baseline_tree": baseline_tree,
                }
            ],
        }
    )


def _outcome_binding_digest(operative_request: str) -> str:
    return canonical_sha256(
        {
            "domain": "happycodex/0.6.5/outcome",
            "operative_request": operative_request,
        }
    )


def canonical_report_from_result(
    result: dict[str, Any],
    *,
    context: dict[str, Any],
) -> dict[str, Any]:
    observation = parse_model_observation(validate_output_result(result))
    if not isinstance(context, dict) or set(context) != _RESULT_CONTEXT_FIELDS:
        raise ValueError("canonical report context is invalid")
    profile = validate_invocation_profile(context["invocation_profile"])
    for field in _RESULT_CONTEXT_FIELDS - {
        "invocation_profile",
        "accepted_baseline_failures",
    }:
        if type(context[field]) is not str or not context[field]:
            raise ValueError(f"canonical report context field is invalid: {field}")
    accepted = context["accepted_baseline_failures"]
    if accepted != sorted(set(_unique_strings(accepted, "accepted baseline identities"))):
        raise ValueError("accepted baseline identities are invalid")
    facts = parse_machine_facts(
        {
            "schema_generation": 7,
            "task_binding": {
                "task_id": context["task_id"],
                "root_task_id": context["root_task_id"],
                "executor_task_id": context["executor_task_id"],
                "owner_label": context["owner_label"],
                "destination_id": context["destination_id"],
                "lineage_digest": context["lineage_digest"],
                "role_config_digest": context["role_config_digest"],
                "repository_digest": context["repository_digest"],
                "outcome_digest": context["outcome_digest"],
                "invocation_profile_digest": canonical_sha256(profile),
            },
            "accepted_baseline_failures": accepted,
            "infrastructure_generation": canonical_sha256(
                {
                    "domain": "happycodex/0.6.5/infrastructure",
                    "binary": profile["binary"],
                    "tools": profile["tools"],
                    "network": profile["network"],
                    "hooks": profile["hooks"],
                    "role_config_digest": context["role_config_digest"],
                }
            ),
        }
    )
    recovery = result["recovery"]
    if recovery is not None:
        manifest = recovery_manifest_projection(recovery)
        if (
            manifest["recovery_manifest_count"] != 1
            or type(manifest["recovery_manifest_sha256"]) is not str
            or not recovery_summary_consistent(recovery)
        ):
            raise ValueError("invalid Recovery Manifest or summary")
    return report_to_raw(build_report(facts, observation))


def invoke_codex(
    launch: dict[str, Any],
    claim_root: Path,
    *,
    argv: list[str],
    cwd: Path,
    env: dict[str, str],
    timeout: int,
) -> tuple[subprocess.CompletedProcess[str], bool, float]:
    from evaluation.live import validate_consumed_action, validate_launch

    launch = validate_launch(launch)
    validate_consumed_action(launch, claim_root)
    if (
        launch["invocation"]["model"] not in argv
        or launch["invocation"]["effort"] not in " ".join(argv)
        or launch["invocation"]["timeout_ms"] != timeout * 1000
    ):
        raise ValueError("launch invocation does not bind model execution")
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


class InfrastructureFailure(RuntimeError):
    """A model subprocess failed before producing behavior evidence."""


def _persist_phase_raw(
    case_output: Path,
    phase: str,
    completed: subprocess.CompletedProcess[str],
) -> None:
    (case_output / f"{phase}-events.jsonl").write_text(
        completed.stdout, encoding="utf-8"
    )
    (case_output / f"{phase}-stderr.txt").write_text(completed.stderr, encoding="utf-8")


def _require_model_phase_success(
    completed: subprocess.CompletedProcess[str],
    *,
    timed_out: bool,
    phase: str,
) -> None:
    if timed_out:
        raise InfrastructureFailure(f"codex {phase} timed out")
    if completed.returncode != 0:
        raise InfrastructureFailure(f"codex {phase} exit {completed.returncode}")


def compaction_receipt(
    home: Path,
    thread_id: str | None,
    *,
    prefix_length: int | None = None,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "rollout_path": None,
        "rollout_sha256": None,
        "rollout_byte_count": 0,
        "rollout_prefix_sha256": None,
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
    if prefix_length is not None and (
        not isinstance(prefix_length, int)
        or isinstance(prefix_length, bool)
        or prefix_length < 0
        or prefix_length > len(content)
    ):
        raise ValueError("invalid compaction rollout prefix length")
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
        "rollout_byte_count": len(content),
        "rollout_prefix_sha256": (
            sha256_bytes(content[:prefix_length]) if prefix_length is not None else None
        ),
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


def evaluator_codex_argv(
    *,
    repo: Path,
    schema: Path,
    config: list[str],
    prompt: str,
    thread: str | None = None,
) -> list[str]:
    """Build both fresh and resume evaluator invocations through one path."""
    argv = ["codex", "exec"]
    if thread is not None:
        argv.append("resume")
    argv += ["--json", "--ignore-rules"]
    if thread is None:
        argv += ["--ephemeral", "-C", str(repo)]
    argv += [
        *config,
        "--output-schema",
        str(schema),
        *disabled_feature_args(),
        *([thread] if thread else []),
        prompt,
    ]
    return argv


def finding_identity_matches(actual: str, expected: str) -> bool:
    return type(actual) is str and type(expected) is str and actual == expected


def finding_has_anchor(finding: Any, expected: dict[str, Any]) -> bool:
    return any(
        anchor.semantic_value() == expected for anchor in finding.anchors
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
    report: dict[str, Any],
    oracle: dict[str, Any],
    *,
    expected_recovery_state: dict[str, Any] | None = None,
    fixture: dict[str, Any] | None = None,
) -> list[str]:
    parsed = parse_report(report)
    observation = parsed.observation
    failures: list[str] = []
    if parsed.next_action.kind != oracle["expected_action"]:
        failures.append(
            "next_action: got "
            f"{parsed.next_action.kind!r}, expected {oracle['expected_action']!r}"
        )
    required_observation = oracle["required_observation"]
    if observation.qualifies is not required_observation["qualifies"]:
        failures.append(
            "qualifies: got "
            f"{observation.qualifies!r}, expected "
            f"{required_observation['qualifies']!r}"
        )
    if (
        observation.execplan_condition
        not in required_observation["execplan_conditions"]
    ):
        failures.append(
            "execplan_condition: got "
            f"{observation.execplan_condition!r}, expected one of "
            f"{required_observation['execplan_conditions']!r}"
        )
    raw_observation = report["observation"]
    if expected_recovery_state is not None:
        failures += recovery_state_failures(
            "recovery",
            raw_observation.get("recovery"),
            expected_recovery_state,
        )
    findings = parsed.findings
    blockers = parsed.blockers
    if (
        fixture is not None
        and fixture_requires_goal_pause_handoff(fixture)
        and parsed.next_action.kind == "ASK_USER"
        and "user_selection" not in observation.open_gates
    ):
        failures.append("active Goal lacks explicit pause handoff")
    for expected in oracle.get("required_findings", []):
        if not any(
            finding_identity_matches(item.finding_id, expected["id"])
            and item.domain == expected["domain"]
            and item.status in expected["statuses"]
            for item in findings
        ):
            failures.append(f"missing finding: {expected['id']}")
    for expected in oracle.get("required_blockers", []):
        if not any(
            finding_identity_matches(item.finding_id, expected["id"])
            and item.blocker_class in expected["classes"]
            for item in blockers
        ):
            failures.append(f"missing blocker: {expected['id']}")
    for blocker_class in oracle.get("required_blocker_classes", []):
        if not any(item.blocker_class == blocker_class for item in blockers):
            failures.append(f"missing blocking class: {blocker_class}")
    used_blockers: set[str] = set()
    for expected in oracle.get("required_anchored_blockers", []):
        matches = {
            blocker.finding_id
            for blocker in blockers
            if finding_has_anchor(blocker, expected["anchor"])
            and blocker.blocker_class in expected["classes"]
        }
        if not matches:
            failures.append(f"missing anchored blocker: {expected['anchor']}")
        elif len(matches) != 1 or used_blockers & matches:
            failures.append("distinct anchored blocker required")
        used_blockers |= matches
    used_findings: set[str] = set()
    for expected in oracle.get("required_anchored_findings", []):
        matches = {
            item.finding_id
            for item in findings
            if finding_has_anchor(item, expected["anchor"])
            and item.domain == expected["domain"]
            and item.status in expected["statuses"]
        }
        if not matches:
            failures.append(f"missing anchored finding: {expected['anchor']}")
        elif len(matches) != 1 or used_findings & matches:
            failures.append("distinct anchored finding required")
        used_findings |= matches
    return failures


def recovery_control_failures(
    *,
    primary: dict[str, Any],
    primary_thread_id: str | None,
    fresh: dict[str, Any],
    fresh_thread_id: str | None,
    expected_state: dict[str, Any] | None = None,
) -> list[str]:
    primary_report = parse_report(primary)
    fresh_report = parse_report(fresh)
    failures: list[str] = []
    if not fresh_thread_id:
        failures.append("fresh recovery control emitted no thread id")
    elif fresh_thread_id == primary_thread_id:
        failures.append("fresh recovery control reused the resumed task")
    for field in ("qualifies", "execplan_condition", "open_gates"):
        fresh_value = getattr(fresh_report.observation, field)
        primary_value = getattr(primary_report.observation, field)
        if fresh_value != primary_value:
            failures.append(
                f"fresh recovery control disagrees on {field}: "
                f"{fresh_value!r} != {primary_value!r}"
            )
    if (
        fresh_report.next_action.kind,
        fresh_report.next_action.target,
    ) != (
        primary_report.next_action.kind,
        primary_report.next_action.target,
    ):
        failures.append("fresh recovery control disagrees on NextAction")
    primary_state = primary["observation"].get("recovery")
    fresh_state = fresh["observation"].get("recovery")
    if isinstance(primary_state, dict) and isinstance(fresh_state, dict):
        for field in sorted(RECOVERY_STATE_FIELDS):
            if normalized_recovery_value(
                field, fresh_state.get(field)
            ) != normalized_recovery_value(field, primary_state.get(field)):
                failures.append(
                    f"fresh recovery control disagrees on recovery.{field}"
                )
    elif fresh_state != primary_state:
        failures.append("fresh recovery control disagrees on recovery")
    if expected_state is not None:
        for label, state in (("primary", primary_state), ("fresh", fresh_state)):
            failures.extend(
                recovery_state_failures(
                    f"{label} recovery", state, expected_state
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


def _validate_case_launch(
    launch: dict[str, Any],
    *,
    case: dict[str, Any],
    plugin: Path,
    model: str,
    effort: str,
    timeout: int,
    arm: str,
    launch_unit: str | None,
) -> None:
    if launch_unit is not None and launch_unit != case["id"]:
        expected_unit = launch_unit
    else:
        expected_unit = case["id"]
    from evaluation.live import validate_launch

    launch = validate_launch(launch, unit=expected_unit)
    if (
        launch["invocation"]["model"] != model
        or launch["invocation"]["effort"] != effort
        or launch["invocation"]["timeout_ms"] != timeout * 1000
        or launch["invocation"]["arm"] != arm
    ):
        raise ValueError("launch invocation profile drift")
    if not plugin.resolve().is_dir():
        raise ValueError("evaluated plugin must be an existing directory")
    invocation_profile(
        model=model,
        effort=effort,
        timeout_seconds=timeout,
        arm=arm,
        session_mode=(
            "fresh-with-bounded-resume"
            if "native_compaction_resume" in case["fixture"]
            else "fresh"
        ),
    )


def _phase_event_binding(
    launch: dict[str, Any],
    *,
    case_id: str,
    arm: str,
    phase: str,
    session_scope: str,
    thread_id: str | None,
    profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    from evaluation.live import validate_launch

    launch = validate_launch(launch)
    profile = validate_invocation_profile(profile, require_bound_binary=True)
    binding = {
        "provider": profile["provider"],
        "session_id": canonical_sha256(
            {
                "launch_key": launch["launch_key"],
                "unit": launch["unit"],
                "case_id": case_id,
                "arm": arm,
                "session_scope": session_scope,
            }
        ),
        "thread_id": thread_id,
        "action_id": f"case:{case_id}:{arm}:{phase}",
        "launch_key": launch["launch_key"],
    }
    return binding, profile


def evaluate_case(
    case: dict[str, Any],
    *,
    plugin: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    arm: str,
    launch: dict[str, Any],
    claim_root: Path,
    launch_unit: str | None = None,
) -> dict[str, Any]:
    _validate_case_launch(
        launch,
        case=case,
        plugin=plugin,
        model=model,
        effort=effort,
        timeout=timeout,
        arm=arm,
        launch_unit=launch_unit,
    )
    case_output = output / case["id"]
    if case_output.exists():
        if case_output.is_symlink() or not case_output.is_dir():
            raise ValueError("reserved launch output is not a real directory")
    else:
        case_output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix=f"happycodex-{case['id']}-") as raw:
        temp = Path(raw)
        repo = temp / "repo"
        fixture = build_fixture(case, repo)
        package = temp / "package"
        source_package = package_identities(plugin)
        copy_plugin_package(plugin, package, arm=arm)
        if package_identities(package) != source_package:
            raise RuntimeError("copied package differs from evaluated source")
        input_digest = semantic_input_sha256_from_package(
            case,
            package_semantic_sha256=source_package["semantic_sha256"],
            model=model,
            effort=effort,
            timeout=timeout,
            arm=arm,
        )
        codex = codex_identity()
        native = case["fixture"].get("native_compaction_resume")
        profile = invocation_profile(
            model=model,
            effort=effort,
            timeout_seconds=timeout,
            arm=arm,
            binary_identity_sha256=codex["sha256"],
            session_mode="fresh-with-bounded-resume" if native else "fresh",
        )
        accepted = sorted(
            case["oracle"].get("accepted_baseline_failures", [])
        )
        context = {
            "task_id": f"case:{case['id']}:{arm}",
            "root_task_id": "root:evaluator",
            "executor_task_id": "executor:evaluator",
            "owner_label": "happycodex-evaluator",
            "destination_id": "repository:happycodex",
            "lineage_digest": input_digest,
            "role_config_digest": canonical_sha256(
                FILESYSTEM_ISOLATION_POLICY
            ),
            "repository_digest": _repository_binding_digest(
                case["id"], fixture["commits"][0], fixture["trees"][0]
            ),
            "outcome_digest": _outcome_binding_digest(case["prompt"]),
            "invocation_profile": profile,
            "accepted_baseline_failures": accepted,
        }
        home, env = isolated_home(temp)
        tool_bin = temp / "bin"
        installation = install_plugin(package, home, env)
        schema = temp / "response-schema.json"
        schema.write_text(
            json.dumps(provider_transport_schema(OUTPUT_SCHEMA)),
            encoding="utf-8",
        )
        config = [
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
        if native:
            config += [
                "-c",
                f"model_auto_compact_token_limit={native['auto_compact_token_limit']}",
            ]
        phases: list[dict[str, Any]] = []

        def execute(
            name: str, prompt: str, thread: str | None = None
        ) -> tuple[dict[str, Any], str]:
            argv = evaluator_codex_argv(
                repo=repo,
                schema=schema,
                config=config,
                prompt=prompt,
                thread=thread,
            )
            completed, timed_out, elapsed = invoke_codex(
                launch,
                claim_root,
                argv=argv,
                cwd=repo,
                env=env,
                timeout=timeout,
            )
            _persist_phase_raw(case_output, name, completed)
            _require_model_phase_success(completed, timed_out=timed_out, phase=name)
            binding, bound_profile = _phase_event_binding(
                launch,
                case_id=case["id"],
                arm=arm,
                phase=name,
                session_scope=name,
                thread_id=thread,
                profile=profile,
            )
            result, usage, reported_thread, terminal = parse_events(
                completed.stdout,
                binding=binding,
                invocation_profile=bound_profile,
            )
            phases.append(
                {
                    "argv": [*argv[:-1], "<prompt>"],
                    "completed": completed,
                    "elapsed": elapsed,
                    "timed_out": timed_out,
                    "usage": usage,
                    "terminal": terminal,
                }
            )
            return result, reported_thread

        prompt = f"{EVALUATOR_CONTEXT}\n\n{case['prompt']}"
        fresh_result = None
        fresh_report = None
        native_receipt = None
        if native:
            _prepared, thread_id = execute(
                "prepare", f"{EVALUATOR_CONTEXT}\n\n{native['prepare_prompt']}"
            )
            if not thread_id:
                raise InfrastructureFailure("prepare emitted no thread id")
            before = compaction_receipt(home, thread_id)
            transition = apply_post_compaction_transition(
                repo, native["post_compaction_transition"], fixture
            )
            expected = expected_recovery_state(native, fixture, transition)
            result, resume_thread = execute("resume", prompt, thread_id)
            fresh_prompt = f"{EVALUATOR_CONTEXT}\n\n{native['fresh_recovery_prompt']}"
            fresh_result, fresh_thread = execute("fresh-recovery", fresh_prompt)
            report = canonical_report_from_result(result, context=context)
            fresh_report = canonical_report_from_result(
                fresh_result,
                context={**context, "task_id": context["task_id"] + ":fresh"},
            )
            failures = match_oracle(
                report,
                case["oracle"],
                expected_recovery_state=expected,
                fixture=case["fixture"],
            )
            failures += match_oracle(
                fresh_report,
                case["oracle"],
                expected_recovery_state=expected,
                fixture=case["fixture"],
            )
            failures += recovery_control_failures(
                primary=report,
                primary_thread_id=thread_id,
                fresh=fresh_report,
                fresh_thread_id=fresh_thread,
                expected_state=expected,
            )
            native_receipt = {
                "before_resume": before,
                "after_resume": compaction_receipt(
                    home, thread_id, prefix_length=before["rollout_byte_count"]
                ),
                "resumed_same_thread": resume_thread == thread_id,
                "fresh_control": {
                    "thread_id": fresh_thread,
                    "distinct_from_resumed_task": fresh_thread != thread_id,
                    "no_resume_handle": True,
                    "no_conversation_summary": True,
                    "prompt_sha256": sha256_bytes(fresh_prompt.encode()),
                },
            }
        else:
            result, thread_id = execute("initial", prompt)
            resume_thread = fresh_thread = None
            report = canonical_report_from_result(result, context=context)
            failures = match_oracle(
                report,
                case["oracle"],
                fixture=case["fixture"],
            )
        if workspace_file_manifest(repo) != fixture["files"]:
            failures.append("read-only task changed fixture")
        usage_phases = [phase["usage"] for phase in phases]
        usage = combined_usage(*usage_phases)
        events = [phase["completed"].stdout for phase in phases]
        stderr = [phase["completed"].stderr for phase in phases]
        metadata = {
            "schema_version": 1,
            "case": case["id"],
            "arm": arm,
            "model": model,
            "effort": effort,
            "timeout_seconds": timeout,
            "timed_out": any(phase["timed_out"] for phase in phases),
            "elapsed_seconds": round(sum(phase["elapsed"] for phase in phases), 3),
            "exit_code": phases[-1]["completed"].returncode,
            "thread_id": thread_id,
            "resume_thread_id": resume_thread,
            "fresh_recovery_thread_id": fresh_thread,
            "terminal_projections": [phase["terminal"] for phase in phases],
            "semantic_input_sha256": input_digest,
            "invocation_profile": profile,
            "accepted_baseline_failures": accepted,
            "identities": {
                "engine": engine_inventory(ROOT),
                "package": source_package,
                "codex": codex,
            },
            "filesystem_isolation": FILESYSTEM_ISOLATION_POLICY,
            "installation": installation,
            "usage": usage,
            "usage_phases": usage_phases,
            "uncached_input_tokens": usage["input_tokens"] - usage["cached_input_tokens"],
            "events_sha256": canonical_sha256(
                [sha256_bytes(item.encode()) for item in events]
            ),
            "stderr_sha256": canonical_sha256(
                [sha256_bytes(item.encode()) for item in stderr]
            ),
            "native_compaction": native_receipt,
            "result": result,
            "canonical_report": report,
            "fresh_recovery_result": fresh_result,
            "fresh_recovery_canonical_report": fresh_report,
            "oracle_failures": failures,
            "passed": not failures,
            "command": phases[-1]["argv"],
        }
        for name, value in (("events.jsonl", events[-1]), ("stderr.txt", stderr[-1])):
            (case_output / name).write_text(value, encoding="utf-8")
        (case_output / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return metadata


def resolve_output_path(requested: Path | None, *, plugin: Path) -> Path:
    if requested is None or not requested.is_absolute():
        raise ValueError("an explicit absolute raw output path is required")
    if requested.is_symlink() or requested.exists():
        raise ValueError("raw output path must be absent and not a symlink")
    parent = requested.parent
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("raw output parent must be an existing real directory")
    output = requested.resolve()
    root = ROOT.resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError("raw output must stay outside the repository")
    plugin = plugin.resolve()
    if output == plugin or output.is_relative_to(plugin):
        raise ValueError("raw output must stay outside the evaluated plugin")
    return output


def create_output_root(output: Path) -> Path:
    if output.is_symlink() or output.exists():
        raise ValueError("raw output changed or became a symlink")
    parent = output.parent
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(parent, flags)
    try:
        os.mkdir(output.name, mode=0o700, dir_fd=descriptor)
        opened = os.open(output.name, flags, dir_fd=descriptor)
        os.close(opened)
    except FileExistsError as exc:
        raise ValueError("raw output changed or became a symlink") from exc
    finally:
        os.close(descriptor)
    return output


def run_command(args: Any) -> int:
    cases = load_cases()
    if args.list:
        for case_id in cases:
            print(case_id)
        return 0
    calibrate = bool(getattr(args, "calibrate", False))
    selected = ["subthreshold-control"] if calibrate else (args.cases or list(cases))
    unknown = set(selected) - set(cases)
    if unknown:
        raise SystemExit(f"unknown cases: {sorted(unknown)}")
    if args.dry_run:
        print(
            json.dumps(
                {
                    "cases": selected,
                    "calibrate": calibrate,
                    "coverage": sorted(REQUIRED_TAGS),
                    "invocation_profile": invocation_profile(
                        model=args.model,
                        effort=args.effort,
                        timeout_seconds=args.timeout,
                        arm=args.arm,
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
    raise SystemExit("live corpus execution is available only through evaluation.cli")


def _evaluate_cases_bounded(
    case_ids: list[str],
    evaluate: Callable[[str], dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep a bounded frontier, preserve order, and stop replenishing on failure."""
    if not case_ids:
        return []
    worker_count = min(CORPUS_MAX_WORKERS, len(case_ids))
    results: list[dict[str, Any] | None] = [None] * len(case_ids)
    next_index = 0
    failure: BaseException | None = None
    stopped = threading.Event()
    lock = threading.Lock()

    def worker() -> None:
        nonlocal next_index, failure
        while not stopped.is_set():
            with lock:
                if stopped.is_set() or next_index >= len(case_ids):
                    return
                index = next_index
                next_index += 1
            try:
                results[index] = evaluate(case_ids[index])
            except BaseException as exc:
                with lock:
                    if failure is None:
                        failure = exc
                    stopped.set()
                return

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        workers = [executor.submit(worker) for _index in range(worker_count)]
        for future in workers:
            future.result()
    if failure is not None:
        raise failure
    if any(result is None for result in results):
        raise AssertionError("corpus scheduler lost a completed result")
    return [result for result in results if result is not None]


def _launch_result(metadata: dict[str, Any], launch: dict[str, Any]) -> dict[str, Any]:
    usage = {
        "model_calls": len(metadata["usage_phases"]),
        "uncached_input_tokens": metadata["uncached_input_tokens"],
        "output_tokens": metadata["usage"]["output_tokens"],
        "wall_milliseconds": round(metadata["elapsed_seconds"] * 1000),
    }
    result = {
        "schema_generation": 7,
        "action_key": launch["action_key"],
        "launch_key": launch["launch_key"],
        "unit": launch["unit"],
        "status": "succeeded" if metadata["passed"] else "failed",
        "effect": "provider_reached",
        "output_sha256": canonical_sha256(metadata),
        "usage": usage,
    }
    result["result_sha256"] = canonical_sha256(result)
    return result


def run_authorized(
    args: Any,
    launches: dict[str, dict[str, Any]],
    claim_root: Path,
) -> int:
    from evaluation import live

    if not isinstance(launches, dict) or not launches:
        raise ValueError("authorized corpus run requires launches")
    prepared = {
        key: live.validate_launch(value, unit=key)
        for key, value in launches.items()
    }
    cases = load_cases()
    calibrate = bool(getattr(args, "calibrate", False))
    selected = (
        ["subthreshold-control"]
        if calibrate
        else sorted(args.cases or cases)
    )
    unknown = set(selected) - set(cases)
    if unknown:
        raise ValueError(f"unknown cases: {sorted(unknown)}")
    if set(prepared) != set(selected):
        raise ValueError("launch units do not equal selected corpus cases")
    output = resolve_output_path(args.output, plugin=args.plugin)
    gate = "calibration" if calibrate else "corpus"
    for case_id in selected:
        launch = live.validate_launch(
            prepared[case_id],
            unit=case_id,
            timeout_ms=args.timeout * 1000,
            output=output / case_id,
        )
        if (
            launch["gate"] != gate
            or launch["invocation"]["model"] != args.model
            or launch["invocation"]["effort"] != args.effort
            or launch["invocation"]["arm"] != args.arm
        ):
            raise ValueError("launch does not bind corpus invocation")
    provider_transport_schema(OUTPUT_SCHEMA)
    codex_identity()
    package_identities(args.plugin)

    def evaluate_authorized(case_id: str) -> dict[str, Any]:
        launch = prepared[case_id]
        live.reserve_launch(launch, claim_root)
        live.consume_action(launch, claim_root)
        metadata = evaluate_case(
            cases[case_id],
            plugin=args.plugin,
            output=output,
            model=args.model,
            effort=args.effort,
            timeout=args.timeout,
            arm=args.arm,
            launch=launch,
            claim_root=claim_root,
            launch_unit=case_id,
        )
        live.write_launch_result(
            launch,
            claim_root,
            _launch_result(metadata, launch),
        )
        return metadata

    results = _evaluate_cases_bounded(
        selected,
        evaluate_authorized,
    )
    print(json.dumps({
        "schema_version": 1,
        "engine_generation": "0.6.5",
        "gate": gate,
        "cases": selected,
        "passed": all(result["passed"] for result in results),
        "receipts": [canonical_sha256(result) for result in results],
    }, sort_keys=True))
    return 0
