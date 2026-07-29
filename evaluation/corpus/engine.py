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
    BLOCKER_CLASSES,
    CORPUS_SEMANTIC_PATHS,
    CONVERGENCE_PHASES,
    FILESYSTEM_ISOLATION_POLICY,
    PACKAGE_PATHS,
    PERMISSION_FIELDS,
    PERMISSION_PROFILE,
    PERMISSION_VALUES,
    PUBLIC_040_PACKAGE_ARTIFACT_SHA256,
    RECOVERY_ACTIONS,
    RECOVERY_GATE_FIELDS,
    RECOVERY_MANIFEST_PATTERN,
    RECOVERY_PENDING_GATES,
    RECOVERY_STATE_FIELDS,
    canonical_sha256,
    case_semantic_sha256,
    classifications_share_identity,
    engine_inventory,
    engine_paths_sha256,
    invocation_profile,
    identity_match_values,
    is_nonblank_identity,
    package_identities,
    package_manifest_sha256,
    read_json,
    recovery_manifest_projection,
    recovery_summary_consistent,
    selected_package_paths,
    sha256_bytes,
    toolchain_identity,
    validate_invocation_profile,
    workspace_file_manifest,
)
from evaluation.semantic import make_attempt_key, parse_facts, reduce_facts

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
    "writes. Raw permission fields are assertions checked against the semantic reducer, "
    "not authority. Put every material finding and blocker under one exact shared "
    f"identity. {IDENTITY_PROJECTION_TEXT} Use open_gates only from the closed control "
    "gate vocabulary and copy recovery pending_gates in checkpoint order without "
    "inferring downstream gates. Recovery controls must include every durable Git, "
    "plan, test, worktree, delegated-agent, and Recovery Manifest fact; live_agents "
    "contains delegated receipts, never the Root writer. Do not inspect evaluator "
    "code or hidden oracles."
)
OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["continue", "stop_for_user", "complete", "incomplete"],
        },
        "qualifies": {"type": "boolean"},
        "execplan_condition": {
            "type": "string",
            "enum": ["not_required", "missing", "usable", "needs_amendment"],
        },
        "protocol_may_product_write": {"type": "boolean"},
        "protocol_review_mode": {
            "type": "string",
            "enum": ["none", "focused_hardening", "exact_final"],
        },
        "protocol_may_complete": {"type": "boolean"},
        "finding_classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "identity": {
                        "type": "string", "minLength": 1, "maxLength": 160,
                        "pattern": r"\S", "description": IDENTITY_PROJECTION_TEXT,
                    },
                    "domain": {
                        "type": "string",
                        "enum": ["secret", "baseline_failure", "receipt", "other"],
                    },
                    "state": {
                        "type": "string",
                        "enum": [
                            "baseline_unchanged", "resolved", "candidate_new", "unknown"
                        ],
                    },
                    "anchors": {
                        "type": "array",
                        "items": {"type": "string", "maxLength": 4_096},
                    },
                },
                "required": ["identity", "domain", "state", "anchors"],
            },
        },
        "blocker_classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "identity": {
                        "type": "string", "minLength": 1, "maxLength": 160,
                        "pattern": r"\S",
                    },
                    "class": {"type": "string", "enum": sorted(BLOCKER_CLASSES)},
                    "blocking": {"type": "boolean"},
                    "reason": {"type": "string", "maxLength": 240},
                },
                "required": ["identity", "class", "blocking", "reason"],
            },
        },
        "open_gates": {
            "type": "array",
            "items": {"type": "string", "enum": list(RECOVERY_PENDING_GATES)},
        },
        "evidence": {
            "type": "array",
            "items": {"type": "string", "maxLength": 240},
        },
        "reason": {"type": "string", "maxLength": 1_200},
        "recovery_state": {
            "type": ["object", "null"],
            "additionalProperties": False,
            "properties": {
                "baseline_revision": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "baseline_tree": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "current_revision": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "current_tree": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "writer": {"type": "string", "enum": ["Root", "unknown"]},
                "milestone_phase": {
                    "type": "string", "enum": list(CONVERGENCE_PHASES),
                },
                "next_action": {"type": "string", "enum": list(RECOVERY_ACTIONS)},
                "pending_gates": {
                    "type": "array",
                    "items": {"type": "string", "enum": list(RECOVERY_PENDING_GATES)},
                },
                "tests": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "passed": {"type": "integer", "minimum": 0},
                        "failed": {"type": "integer", "minimum": 0},
                        "accepted_failures": {"type": "integer", "minimum": 0},
                        "marker_ids": {
                            "type": "array",
                            "items": {"type": "string", "maxLength": 160},
                        },
                    },
                    "required": [
                        "passed", "failed", "accepted_failures", "marker_ids"
                    ],
                },
                "worktree": {
                    "type": "string", "enum": ["clean", "dirty", "unknown"],
                },
                "live_agents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "id": {"type": "string", "maxLength": 160},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "terminal", "missing"],
                            },
                            "receipt_reproduced": {"type": "boolean"},
                        },
                        "required": ["id", "status", "receipt_reproduced"],
                    },
                },
                "marker_ids": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 160},
                },
            },
            "required": sorted(RECOVERY_STATE_FIELDS),
        },
    },
    "required": [
        "decision", "qualifies", "execplan_condition",
        "protocol_may_product_write", "protocol_review_mode",
        "protocol_may_complete", "finding_classifications",
        "blocker_classifications", "open_gates", "evidence", "reason",
        "recovery_state",
    ],
}


def expected_permission_failures(
    expected: dict[str, Any], *, recovery_state: dict[str, Any] | None = None
) -> list[str]:
    """Validate only the closed raw assertion vocabulary; reducer owns semantics."""
    del recovery_state
    failures: list[str] = []
    for field, allowed in PERMISSION_VALUES.items():
        raw = expected.get(field)
        values = raw if isinstance(raw, list) else [raw]
        if (
            not values
            or len({(type(value), value) for value in values}) != len(values)
            or any(value not in allowed or type(value) is not type(next(iter(allowed)))
                   for value in values)
        ):
            failures.append(f"invalid {field}: {raw!r}")
    return failures
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
EXPECTED_PUBLIC_040_SKILL_ENTRIES = frozenset(
    {
        "SKILL.md",
        "agents",
        "agents/openai.yaml",
        "references",
        "references/execplan.md",
    }
)
EXPECTED_PUBLIC_040_PACKAGE_MANIFEST_SHA256 = PUBLIC_040_PACKAGE_ARTIFACT_SHA256
EXPECTED_SKILL_ENTRIES_BY_ARM = {
    "candidate": EXPECTED_CANDIDATE_SKILL_ENTRIES,
    "public-0.4.0": EXPECTED_PUBLIC_040_SKILL_ENTRIES,
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
    shared_semantic = engine_paths_sha256(inventory, CORPUS_SEMANTIC_PATHS)
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


def validate_recovery_manifest(native: dict[str, Any], *, case_id: str) -> None:
    """Bind the recovery marker to one complete canonical manifest artifact."""
    oracle = native["recovery_oracle"]
    markers = oracle.get("marker_ids", [])
    manifest_markers = [
        marker
        for marker in markers
        if isinstance(marker, str) and RECOVERY_MANIFEST_PATTERN.fullmatch(marker)
    ]
    if len(manifest_markers) != 1:
        raise ValueError(f"invalid Recovery Manifest marker: {case_id}")
    digest = RECOVERY_MANIFEST_PATTERN.fullmatch(manifest_markers[0]).group(1)
    transition_files = native["post_compaction_transition"]["files"]
    matches = [
        (relative, content)
        for relative, content in transition_files.items()
        if relative == RECOVERY_MANIFEST_PATH
        and isinstance(content, str)
        and sha256_bytes(content.encode()) == digest
    ]
    if len(matches) != 1:
        raise ValueError(f"Recovery Manifest digest mismatch: {case_id}")
    try:
        manifest = json.loads(matches[0][1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid Recovery Manifest JSON: {case_id}") from exc
    required = {
        "schema_version",
        "repositories",
        "resource_claim",
        "selected_checkpoint",
        "convergence",
        "writer",
        "tests",
        "agents",
        "gates",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError(f"invalid Recovery Manifest envelope: {case_id}")
    repositories = manifest["repositories"]
    if (
        not isinstance(repositories, list)
        or not repositories
        or any(
            not isinstance(repository, dict)
            or set(repository) != {"namespace", "revision", "tree"}
            or not isinstance(repository["namespace"], str)
            or not repository["namespace"]
            or re.fullmatch(r"[0-9a-f]{40}", repository["revision"]) is None
            or re.fullmatch(r"[0-9a-f]{40}", repository["tree"]) is None
            for repository in repositories
        )
        or len({repository["namespace"] for repository in repositories})
        != len(repositories)
    ):
        raise ValueError(f"invalid Recovery Manifest repositories: {case_id}")
    claim = manifest["resource_claim"]
    resources = claim.get("resources") if isinstance(claim, dict) else None
    if (
        not isinstance(claim, dict)
        or set(claim) != {"owner", "owner_token_sha256", "resources"}
        or claim["owner"] != "Root"
        or re.fullmatch(r"[0-9a-f]{64}", claim["owner_token_sha256"]) is None
        or not isinstance(resources, list)
        or len(resources) != 5
        or any(
            not isinstance(resource, str)
            or re.fullmatch(
                r"(?:worktree|ref|ledger|output|activation):.+",
                resource,
            )
            is None
            for resource in resources
        )
        or len(resources) != len(set(resources))
        or {resource.split(":", 1)[0] for resource in resources}
        != {"worktree", "ref", "ledger", "output", "activation"}
    ):
        raise ValueError(f"invalid Recovery Manifest resource claim: {case_id}")
    selected = manifest["selected_checkpoint"]
    if (
        not isinstance(selected, dict)
        or set(selected) != {"ref", "archive"}
        or (
            (
                not isinstance(selected["ref"], str)
                or re.fullmatch(
                    r"refs/(?!.*(?:\.\.|//|@\{|\\))[A-Za-z0-9._/-]*"
                    r"[A-Za-z0-9_-]",
                    selected["ref"],
                )
                is None
            )
            if selected["archive"] is None
            else (
                selected["ref"] is not None
                or not isinstance(selected["archive"], str)
                or re.fullmatch(r"sha256:[0-9a-f]{64}", selected["archive"]) is None
            )
        )
    ):
        raise ValueError(f"invalid Recovery Manifest checkpoint: {case_id}")
    convergence = manifest["convergence"]
    families = convergence.get("families") if isinstance(convergence, dict) else None
    family_ids = (
        [
            family.get("family_id")
            for family in families
            if isinstance(family, dict) and isinstance(family.get("family_id"), str)
        ]
        if isinstance(families, list)
        else []
    )
    if (
        not isinstance(convergence, dict)
        or set(convergence) != {"phase", "families"}
        or convergence["phase"] not in CONVERGENCE_PHASES
        or not isinstance(families, list)
        or not families
        or len(family_ids) != len(families)
        or len(set(family_ids)) != len(family_ids)
        or any(
            not isinstance(family, dict)
            or set(family) != {"family_id", "status", "repair_batch", "recurrence"}
            or not isinstance(family["family_id"], str)
            or not family["family_id"].strip()
            or family["status"] not in {"open", "boundary_required", "closed"}
            or re.fullmatch(r".+/(?:instance|boundary)", family["repair_batch"]) is None
            or type(family["recurrence"]) is not int
            or family["recurrence"] < 0
            for family in families
        )
    ):
        raise ValueError(f"invalid Recovery Manifest convergence state: {case_id}")
    manifest_gates = manifest["gates"] if isinstance(manifest["gates"], list) else []
    for family in families:
        batch_kind = family["repair_batch"].rsplit("/", 1)[1]
        recurrence = family["recurrence"]
        status = family["status"]
        if (
            (recurrence == 0 and batch_kind != "instance")
            or (recurrence > 0 and batch_kind != "boundary")
            or (status == "boundary_required" and recurrence != 1)
            or (
                recurrence >= 2
                and (
                    status != "open"
                    or convergence["phase"] != "focused_hardening"
                    or "user_selection" not in manifest_gates
                )
            )
        ):
            raise ValueError(
                f"invalid Recovery Manifest convergence transition: {case_id}"
            )
    agents = manifest["agents"]
    agent_ids = (
        [
            agent.get("id")
            for agent in agents
            if isinstance(agent, dict) and isinstance(agent.get("id"), str)
        ]
        if isinstance(agents, list)
        else []
    )
    if (
        not isinstance(agents, list)
        or len(agent_ids) != len(agents)
        or len(set(agent_ids)) != len(agent_ids)
        or any(
            not isinstance(agent, dict)
            or set(agent) != {"id", "status", "receipt_reproduced"}
            or not isinstance(agent["id"], str)
            or not agent["id"].strip()
            or agent["status"] != "terminal"
            or agent["receipt_reproduced"] is not True
            for agent in agents
        )
    ):
        raise ValueError(f"invalid Recovery Manifest agents: {case_id}")
    tests = manifest["tests"]
    if (
        not isinstance(tests, dict)
        or set(tests) != {"passed", "failed", "accepted_failures"}
        or any(type(tests[field]) is not int or tests[field] < 0 for field in tests)
        or tests["accepted_failures"] > tests["failed"]
        or manifest["schema_version"] != 1
        or manifest["writer"] != "Root"
        or not isinstance(manifest["gates"], list)
        or not manifest["gates"]
        or any(
            not isinstance(gate, str) or not gate.strip() for gate in manifest["gates"]
        )
        or len(manifest["gates"]) != len(set(manifest["gates"]))
    ):
        raise ValueError(f"invalid Recovery Manifest state: {case_id}")


def load_cases(cases_root: Path | None = None) -> dict[str, dict[str, Any]]:
    cases_root = CASES if cases_root is None else cases_root.resolve()
    loaded: dict[str, dict[str, Any]] = {}
    for path in sorted(cases_root.glob("*.json")):
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
    permission_failures = expected_permission_failures(expected)
    if permission_failures:
        raise ValueError(
            f"invalid permission state: {case['id']}: " + "; ".join(permission_failures)
        )
    accepted = case["oracle"].get("accepted_baseline_failures", [])
    if (
        not isinstance(accepted, list)
        or any(not is_nonblank_identity(identity) for identity in accepted)
        or len(set(accepted)) != len(accepted)
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
        validate_recovery_manifest(native, case_id=case["id"])
        recovery_permission_failures = expected_permission_failures(
            expected, recovery_state=native["recovery_oracle"]
        )
        if recovery_permission_failures:
            raise ValueError(
                f"invalid recovery permission state: {case['id']}: "
                + "; ".join(recovery_permission_failures)
            )
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
            or not is_nonblank_identity(finding["identity"])
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
        identity = finding["identity"]
        if identity in finding_keys:
            raise ValueError(f"duplicate required classification: {case['id']}")
        if any(
            finding_identity_matches(finding["identity"], other)
            or finding_identity_matches(other, finding["identity"])
            for other in finding_keys
        ):
            raise ValueError(f"ambiguous required classification: {case['id']}")
        finding_keys.add(identity)
    required_blockers = case["oracle"].get("required_blocker_classifications", [])
    if not isinstance(required_blockers, list):
        raise ValueError(f"invalid required blockers: {case['id']}")
    blocker_keys: set[str] = set()
    for blocker in required_blockers:
        if not isinstance(blocker, dict):
            raise ValueError(f"invalid required blocker: {case['id']}")
        if (
            set(blocker) != {"identity", "class"}
            or not is_nonblank_identity(blocker["identity"])
            or blocker["class"] not in BLOCKER_CLASSES
        ):
            raise ValueError(f"invalid required blocker: {case['id']}")
        identity = blocker["identity"]
        if identity in blocker_keys:
            raise ValueError(f"duplicate required blocker: {case['id']}")
        if any(
            finding_identity_matches(blocker["identity"], other)
            or finding_identity_matches(other, blocker["identity"])
            for other in blocker_keys
        ):
            raise ValueError(f"ambiguous required blocker: {case['id']}")
        blocker_keys.add(identity)
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
        key = (blocker["anchor"], tuple(sorted(classes)))
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
            identity = raw_identity if isinstance(raw_identity, str) else ""
            raw_anchor = assertion.get("anchor", "")
            anchor = raw_anchor if isinstance(raw_anchor, str) else ""
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
                and expected.get("protocol_review_mode")
                in {"none", "focused_hardening"}
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


_EVENT_BINDING_FIELDS = frozenset(
    {
        "provider",
        "session_id",
        "thread_id",
        "action_id",
        "attempt_key",
    }
)
_USAGE_FIELDS = frozenset(
    {
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
    }
)
_PREFIX_ITEM_FIELDS = {
    "collab_tool_call": frozenset(
        {
            "agents_states",
            "id",
            "prompt",
            "receiver_thread_ids",
            "sender_thread_id",
            "status",
            "tool",
            "type",
        }
    ),
    "command_execution": frozenset(
        {
            "aggregated_output",
            "command",
            "exit_code",
            "id",
            "status",
            "type",
        }
    ),
    "todo_list": frozenset({"id", "items", "type"}),
    "web_search": frozenset({"action", "id", "query", "type"}),
}


def _exact_event(value: Any, fields: set[str] | frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError(f"invalid terminal event: {label}")
    return value


def _event_binding(value: Any) -> dict[str, Any]:
    binding = _exact_event(value, _EVENT_BINDING_FIELDS, "binding")
    if any(
        type(binding[field]) is not str or not binding[field]
        for field in ("provider", "session_id", "action_id", "attempt_key")
    ) or (
        binding["thread_id"] is not None
        and (type(binding["thread_id"]) is not str or not binding["thread_id"])
    ):
        raise ValueError("invalid terminal event binding")
    if re.fullmatch(r"[0-9a-f]{64}", binding["attempt_key"]) is None:
        raise ValueError("invalid terminal AttemptKey binding")
    return binding


def _prefix_item(value: Any, *, allowed_types: frozenset[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("invalid terminal prefix item")
    item_type = value.get("type")
    fields = _PREFIX_ITEM_FIELDS.get(item_type)
    if item_type not in allowed_types or fields is None or set(value) != fields:
        raise ValueError("terminal prefix item is outside the invocation profile")
    if type(value.get("id")) is not str or not value["id"]:
        raise ValueError("invalid terminal prefix identity")
    if item_type == "collab_tool_call":
        if (
            not isinstance(value["agents_states"], dict)
            or value["prompt"] is not None
            or not isinstance(value["receiver_thread_ids"], list)
            or any(type(item) is not str for item in value["receiver_thread_ids"])
            or any(
                type(value[field]) is not str or not value[field]
                for field in ("sender_thread_id", "status", "tool")
            )
        ):
            raise ValueError("invalid collab_tool_call event")
    elif item_type == "command_execution":
        if (
            type(value["aggregated_output"]) is not str
            or type(value["command"]) is not str
            or value["exit_code"] is not None
            and type(value["exit_code"]) is not int
            or type(value["status"]) is not str
        ):
            raise ValueError("invalid command_execution event")
    elif item_type == "todo_list":
        if not isinstance(value["items"], list):
            raise ValueError("invalid todo_list event")
    elif (
        not isinstance(value["action"], dict)
        or type(value["query"]) is not str
    ):
        raise ValueError("invalid web_search event")
    return value


def _prefix_transition(
    started: dict[str, Any],
    current: dict[str, Any],
    *,
    event_type: str,
) -> None:
    item_type = started["type"]
    if current["id"] != started["id"] or current["type"] != item_type:
        raise ValueError("terminal prefix identity changed")
    if item_type == "collab_tool_call":
        for field in (
            "tool",
            "sender_thread_id",
            "receiver_thread_ids",
            "prompt",
        ):
            if current[field] != started[field]:
                raise ValueError("collab_tool_call binding changed")
        if started["status"] != "in_progress" or current["status"] != "completed":
            raise ValueError("invalid collab_tool_call status transition")
    elif item_type == "command_execution":
        if current["command"] != started["command"]:
            raise ValueError("command_execution binding changed")
        if started["status"] != "in_progress" or current["status"] != "completed":
            raise ValueError("invalid command_execution status transition")
        if started["exit_code"] is not None:
            raise ValueError("command_execution start has an exit code")
    elif item_type == "todo_list":
        if event_type == "item.updated":
            return
    elif current != started:
        raise ValueError("web_search binding changed")


def parse_events(
    stdout: str,
    *,
    binding: dict[str, Any],
    invocation_profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int], str, dict[str, Any]]:
    expected = _event_binding(binding)
    profile = validate_invocation_profile(invocation_profile)
    allowed_types = frozenset(profile["tools"]["event_item_types"])
    lines = stdout.splitlines()
    if len(lines) < 4 or any(not line for line in lines):
        raise ValueError("terminal event stream must end at the unique completion EOF")
    try:
        events = [json.loads(line) for line in lines]
    except json.JSONDecodeError as error:
        raise ValueError("invalid terminal event JSON") from error

    thread = _exact_event(
        events[0],
        {"type", "thread_id"},
        "thread.started",
    )
    if (
        thread["type"] != "thread.started"
        or type(thread["thread_id"]) is not str
        or not thread["thread_id"]
        or (
            expected["thread_id"] is not None
            and thread["thread_id"] != expected["thread_id"]
        )
    ):
        raise ValueError("terminal thread binding mismatch")
    thread_id = thread["thread_id"]

    started = _exact_event(
        events[1],
        {"type"},
        "turn.started",
    )
    if started["type"] != "turn.started":
        raise ValueError("terminal turn binding mismatch")

    prefix_items: dict[str, dict[str, Any]] = {}
    completed_prefix: set[str] = set()
    terminal_item: dict[str, Any] | None = None
    terminal_ordinal: int | None = None
    for ordinal, raw_event in enumerate(events[2:-1], start=2):
        event = _exact_event(
            raw_event,
            {"type", "item"},
            "bounded item event",
        )
        item = event["item"]
        if not isinstance(item, dict):
            raise ValueError("invalid terminal item event")
        item_id = item.get("id")
        item_type = item.get("type")
        if (
            type(item_id) is not str
            or not item_id
            or type(item_type) is not str
            or not item_type
        ):
            raise ValueError("invalid terminal item identity")
        if event["type"] == "item.started":
            item = _prefix_item(item, allowed_types=allowed_types)
            if (
                terminal_item is not None
                or item_id in prefix_items
            ):
                raise ValueError("invalid terminal prefix start")
            prefix_items[item_id] = item
            continue
        if event["type"] == "item.updated":
            item = _prefix_item(item, allowed_types=allowed_types)
            if (
                terminal_item is not None
                or item_type != "todo_list"
                or item_id not in prefix_items
                or item_id in completed_prefix
            ):
                raise ValueError("invalid terminal prefix update")
            _prefix_transition(
                prefix_items[item_id],
                item,
                event_type=event["type"],
            )
            continue
        if event["type"] != "item.completed":
            raise ValueError("unknown terminal event shape")
        if item_type in allowed_types:
            item = _prefix_item(item, allowed_types=allowed_types)
            if (
                terminal_item is not None
                or item_id not in prefix_items
                or item_id in completed_prefix
            ):
                raise ValueError("invalid terminal prefix completion")
            _prefix_transition(
                prefix_items[item_id],
                item,
                event_type=event["type"],
            )
            completed_prefix.add(item_id)
            continue
        if item_type != "agent_message" or terminal_item is not None:
            raise ValueError("invalid or duplicate terminal agent result")
        terminal_item = _exact_event(
            item,
            {"id", "type", "text"},
            "terminal agent result",
        )
        if type(terminal_item["text"]) is not str:
            raise ValueError("terminal agent result text is invalid")
        terminal_ordinal = ordinal
    if set(prefix_items) != completed_prefix:
        raise ValueError("terminal prefix item lacks matching completion")
    if terminal_item is None or terminal_ordinal is None:
        raise ValueError("terminal agent result is missing")
    try:
        final = json.loads(terminal_item["text"])
    except json.JSONDecodeError as error:
        raise ValueError("terminal agent result is not JSON") from error
    if not isinstance(final, dict):
        raise ValueError("terminal agent result must be an object")

    completion = _exact_event(
        events[-1],
        {"type", "usage"},
        "turn.completed",
    )
    if completion["type"] != "turn.completed":
        raise ValueError("terminal completion binding mismatch")
    result_sha256 = canonical_sha256(final)
    usage = _exact_event(completion["usage"], _USAGE_FIELDS, "usage completion")
    if any(
        type(usage[field]) is not int or usage[field] < 0 for field in _USAGE_FIELDS
    ):
        raise ValueError("invalid terminal usage completion")
    stream_sha256 = sha256_bytes(stdout.encode())
    turn_id = canonical_sha256(
        {
            "thread_id": thread_id,
            "action_id": expected["action_id"],
            "attempt_key": expected["attempt_key"],
            "terminal_ordinal": terminal_ordinal,
            "stream_sha256": stream_sha256,
        }
    )
    terminal = {
        "provenance": "validated_invocation+native_stream",
        "provider": expected["provider"],
        "session_id": expected["session_id"],
        "thread_id": thread_id,
        "turn_id": turn_id,
        "action_id": expected["action_id"],
        "attempt_key": expected["attempt_key"],
        "result_id": terminal_item["id"],
        "result_sha256": result_sha256,
        "stream_sha256": stream_sha256,
        "terminal_ordinal": terminal_ordinal,
    }
    return final, usage, thread_id, terminal


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
_FINDING_STATES = {
    "baseline_unchanged": "BASELINE_ACCEPTED",
    "resolved": "RESOLVED",
    "candidate_new": "CANDIDATE_NEW",
    "unknown": "UNKNOWN",
}
_ACTION_ASSERTIONS = {
    "ASK_USER": ("stop_for_user", False, "none", False),
    "CLOSE": ("complete", False, "none", True),
    "EXACT_FINAL": ("continue", False, "exact_final", False),
    "FOCUSED_REVIEW": ("continue", False, "focused_hardening", False),
    "FREEZE_CANDIDATE": ("continue", False, "none", False),
    "IMPLEMENT_BATCH": ("continue", True, "none", False),
    "RECONCILE": ("incomplete", False, "none", False),
    "VERIFY": ("continue", False, "none", False),
}


def _exact_nonblank_strings(value: Any, *, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(type(item) is not str or not item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"{label} must contain unique exact identities")
    return value


def _repository_binding_digest(
    case_id: str,
    baseline_revision: str,
    baseline_tree: str,
) -> str:
    return canonical_sha256(
        {
            "domain": "happycodex/0.6/repository",
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
            "domain": "happycodex/0.6/outcome",
            "operative_request": operative_request,
        }
    )


def semantic_result_projection(
    result: dict[str, Any],
    *,
    context: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError("raw result must be an object")
    if not isinstance(context, dict) or set(context) != _RESULT_CONTEXT_FIELDS:
        raise ValueError("semantic result context is invalid")
    try:
        profile = validate_invocation_profile(context["invocation_profile"])
    except ValueError as exc:
        raise ValueError("invocation_profile is invalid") from exc
    for field in _RESULT_CONTEXT_FIELDS - {
        "invocation_profile",
        "accepted_baseline_failures",
    }:
        if type(context[field]) is not str or not context[field]:
            raise ValueError(f"semantic result context field is invalid: {field}")
    accepted_baseline = context["accepted_baseline_failures"]
    if (
        not isinstance(accepted_baseline, list)
        or any(type(item) is not str or not item for item in accepted_baseline)
        or accepted_baseline != sorted(set(accepted_baseline))
    ):
        raise ValueError("accepted baseline identities are invalid")

    raw_sha256 = canonical_sha256(result)
    source = f"result:{raw_sha256}"
    findings = result.get("finding_classifications", [])
    blockers = result.get("blocker_classifications", [])
    if not isinstance(findings, list) or not isinstance(blockers, list):
        raise ValueError("result classifications must be arrays")
    if any(
        not isinstance(item, dict)
        or set(item) != {"identity", "domain", "state", "anchors"}
        for item in findings
    ):
        raise ValueError("finding classifications are invalid")
    identities = _exact_nonblank_strings(
        [item["identity"] for item in findings],
        label="finding identities",
    )
    if len(identities) != len(findings):
        raise ValueError("finding classifications are invalid")
    if any(
        not isinstance(item, dict)
        or set(item) != {"identity", "class", "blocking", "reason"}
        for item in blockers
    ):
        raise ValueError("blocker classifications are invalid")
    blocker_identities = _exact_nonblank_strings(
        [item["identity"] for item in blockers],
        label="blocker identities",
    )
    if len(blocker_identities) != len(blockers):
        raise ValueError("blocker classifications are invalid")
    if any(identity not in identities for identity in blocker_identities):
        raise ValueError("blocker identity lacks an exact finding")
    for item in findings:
        if (
            item["domain"] not in {"secret", "baseline_failure", "receipt", "other"}
            or item["state"] not in _FINDING_STATES
            or not isinstance(item["anchors"], list)
            or any(type(anchor) is not str for anchor in item["anchors"])
            or len(item["anchors"]) != len(set(item["anchors"]))
        ):
            raise ValueError("finding classification is invalid")
    for item in blockers:
        if (
            item["class"] not in BLOCKER_CLASSES
            or type(item["blocking"]) is not bool
            or type(item["reason"]) is not str
        ):
            raise ValueError("blocker classification is invalid")
        finding = next(
            candidate
            for candidate in findings
            if candidate["identity"] == item["identity"]
        )
        if item["blocking"] is True and finding["state"] == "resolved":
            raise ValueError("resolved finding is blocking")

    recovery = result.get("recovery_state")
    if recovery is not None:
        if not isinstance(recovery, dict) or set(recovery) != RECOVERY_STATE_FIELDS:
            raise ValueError("recovery state has invalid structure")
        if recovery.get("writer") != "Root":
            raise ValueError("unknown writer in recovery")
        if recovery.get("worktree") not in {"clean", "dirty"}:
            raise ValueError("unknown worktree in recovery")
        if recovery.get("milestone_phase") not in CONVERGENCE_PHASES:
            raise ValueError("unknown convergence phase in recovery")
        if recovery.get("next_action") not in RECOVERY_ACTIONS:
            raise ValueError("unknown recovery action")
        recovery_gates = recovery.get("pending_gates")
        if (
            not isinstance(recovery_gates, list)
            or len(recovery_gates) != len(set(recovery_gates))
            or any(gate not in RECOVERY_PENDING_GATES for gate in recovery_gates)
        ):
            raise ValueError("invalid recovery pending gates")
        tests = recovery.get("tests")
        if (
            not isinstance(tests, dict)
            or set(tests)
            != {"passed", "failed", "accepted_failures", "marker_ids"}
            or any(
                type(tests[field]) is not int or tests[field] < 0
                for field in ("passed", "failed", "accepted_failures")
            )
            or tests["accepted_failures"] > tests["failed"]
        ):
            raise ValueError("invalid recovery tests")
        if tests["failed"] > tests["accepted_failures"]:
            raise ValueError("unaccepted failure in recovery tests")
        agents = recovery.get("live_agents")
        if not isinstance(agents, list):
            raise ValueError("invalid recovery agents")
        for agent in agents:
            if not isinstance(agent, dict) or set(agent) != {
                "id",
                "status",
                "receipt_reproduced",
            }:
                raise ValueError("invalid recovery agent")
            if agent["status"] == "missing":
                raise ValueError("missing agent in recovery")
            if agent["status"] != "terminal":
                raise ValueError("nonterminal recovery agent")
            if agent["receipt_reproduced"] is not True:
                raise ValueError("unreproduced recovery receipt")
        manifest = recovery_manifest_projection(recovery)
        if manifest["recovery_manifest_count"] == 0:
            raise ValueError("missing Recovery Manifest")
        if manifest["recovery_manifest_count"] != 1:
            raise ValueError("duplicate Recovery Manifest")
        if not isinstance(manifest["recovery_manifest_sha256"], str):
            raise ValueError("invalid Recovery Manifest")
        if not recovery_summary_consistent(recovery):
            raise ValueError("recovery summary mismatch")

    open_gates = _exact_nonblank_strings(
        result.get("open_gates", []),
        label="open gates",
    )
    if any(gate not in RECOVERY_PENDING_GATES for gate in open_gates):
        raise ValueError("open gate is outside the exact lifecycle vocabulary")
    qualifies = result.get("qualifies")
    execplan = result.get("execplan_condition")
    if type(qualifies) is not bool or execplan not in {
        "not_required",
        "missing",
        "usable",
        "needs_amendment",
    }:
        raise ValueError("raw qualification facts are invalid")
    finding_records = []
    for item in findings:
        state = _FINDING_STATES[item["state"]]
        if state == "BASELINE_ACCEPTED" and item["identity"] not in accepted_baseline:
            state = "UNKNOWN"
        finding_records.append(
            {
                "id": f"finding:{canonical_sha256(item['identity'])}",
                "state": state,
                "evidence": [source],
            }
        )
    blocking = any(item["blocking"] is True for item in blockers)
    unresolved = blocking or any(
        record["state"] in {"CANDIDATE_NEW", "UNKNOWN"}
        for record in finding_records
    )
    needs_reconciliation = unresolved or execplan in {"missing", "needs_amendment"}
    facts_envelope = {
        "schema_generation": 6,
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
        },
        "facts": {
            "checks": [
                {"id": "result-schema", "state": "PASS", "evidence": [source]},
                {
                    "id": "execplan",
                    "state": (
                        "PASS"
                        if execplan in {"usable", "not_required"}
                        else "FAIL"
                    ),
                    "evidence": [source],
                },
            ],
            "claims": [
                {
                    "id": "qualification",
                    "state": "VERIFIED" if qualifies else "N/A",
                    "evidence": [source],
                }
            ],
            "families": [
                {
                    "id": "evaluator",
                    "state": "OPEN" if needs_reconciliation else "CLOSED",
                    "evidence": [source],
                }
            ],
            "findings": finding_records,
            "gates": [
                {
                    "id": gate,
                    "state": "OPEN",
                    "family_id": "evaluator",
                    "evidence": [source],
                }
                for gate in open_gates
            ],
            "markers": [],
            "paths": [],
            "replacements": [],
        },
        "administration": {
            "authority_receipts": [],
            "consumptions": [],
            "cursors": [],
            "receipts": [
                {
                    "id": "invocation-profile",
                    "value": canonical_sha256(profile),
                }
            ],
            "resource_claims": [],
            "timestamps": [],
        },
    }
    report = reduce_facts(parse_facts(facts_envelope))
    action_kind = report.next_action.kind.value
    expected_assertions = _ACTION_ASSERTIONS.get(action_kind)
    if expected_assertions is None:
        raise ValueError(f"unsupported evaluator action: {action_kind}")
    raw_assertions = (
        result.get("decision"),
        result.get("protocol_may_product_write"),
        result.get("protocol_review_mode"),
        result.get("protocol_may_complete"),
    )
    if raw_assertions != expected_assertions:
        raise ValueError(
            "raw protocol assertions diverge from reducer action: "
            f"{raw_assertions!r} != {expected_assertions!r}"
        )
    return {
        "schema_generation": 6,
        "raw_result_sha256": raw_sha256,
        "invocation_profile_sha256": canonical_sha256(profile),
        "accepted_baseline_sha256": canonical_sha256(accepted_baseline),
        "report": report.to_wire(),
        "attempt_key": make_attempt_key(report).value,
    }


def semantic_result_failures(
    result: dict[str, Any],
    *,
    accepted_baseline_failures: list[str] | None = None,
) -> list[str]:
    if not PERMISSION_FIELDS.issubset(result):
        return []
    accepted = sorted(accepted_baseline_failures or [])
    try:
        semantic_result_projection(
            result,
            context={
                "task_id": "case:offline-oracle",
                "root_task_id": "root:evaluator",
                "executor_task_id": "executor:evaluator",
                "owner_label": "happycodex-evaluator",
                "destination_id": "repository:happycodex",
                "lineage_digest": canonical_sha256(result),
                "role_config_digest": canonical_sha256(
                    {
                        "filesystem_isolation": FILESYSTEM_ISOLATION_POLICY,
                        "disabled_features": DISABLED_FEATURES,
                    }
                ),
                "repository_digest": _repository_binding_digest(
                    "offline-oracle",
                    "0" * 40,
                    "0" * 40,
                ),
                "outcome_digest": _outcome_binding_digest(
                    "validate exact evaluator result assertions"
                ),
                "invocation_profile": invocation_profile(
                    model="offline-oracle",
                    effort="deterministic",
                    timeout_seconds=1,
                    arm="candidate",
                ),
                "accepted_baseline_failures": accepted,
            },
        )
    except ValueError as exc:
        return [str(exc)]
    return []


def structural_result_failures(result: dict[str, Any]) -> list[str]:
    findings = result.get("finding_classifications", [])
    blockers = result.get("blocker_classifications", [])
    try:
        if not isinstance(findings, list) or not isinstance(blockers, list):
            raise ValueError("result classifications must be arrays")
        finding_ids = _exact_nonblank_strings(
            [
                item.get("identity")
                for item in findings
                if isinstance(item, dict)
            ],
            label="finding identities",
        )
        blocker_ids = _exact_nonblank_strings(
            [
                item.get("identity")
                for item in blockers
                if isinstance(item, dict)
            ],
            label="blocker identities",
        )
        if len(finding_ids) != len(findings) or len(blocker_ids) != len(blockers):
            raise ValueError("result classifications are invalid")
        if any(identity not in finding_ids for identity in blocker_ids):
            raise ValueError("blocker identity lacks an exact finding")
    except ValueError as exc:
        return [str(exc)]
    return []


def _validated_capability(authorization: Any) -> Any:
    del authorization
    raise ValueError("generation-6 live capability is unavailable until Batch3")


def invoke_codex(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
    authorization: Any = None,
) -> tuple[subprocess.CompletedProcess[str], bool, float]:
    _validated_capability(authorization)
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


def finding_identity_matches(actual: str, expected: str) -> bool:
    return type(actual) is str and type(expected) is str and actual == expected


def finding_has_anchor(finding: dict[str, Any], expected: str) -> bool:
    return any(
        type(item) is str and item == expected
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
    failures.extend(structural_result_failures(result))
    failures.extend(
        semantic_result_failures(
            result,
            accepted_baseline_failures=oracle.get(
                "accepted_baseline_failures", []
            ),
        )
    )
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
    if (
        fixture is not None
        and fixture_requires_goal_pause_handoff(fixture)
        and result.get("decision") == "stop_for_user"
        and not any(
            gate == "user_selection"
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
    anchored_blocker_matches: list[list[frozenset[str]]] = []
    for expected in oracle.get("required_anchored_blockers", []):
        anchor = expected["anchor"]
        allowed_classes = expected["class"]
        if not isinstance(allowed_classes, list):
            allowed_classes = [allowed_classes]
        anchored_findings = [
            finding
            for finding in actual_findings
            if finding_has_anchor(finding, anchor)
        ]
        matches = [
            identity_match_values(finding.get("identity", ""))
            for finding in anchored_findings
            for blocker in actual_blockers
            if classifications_share_identity(finding, blocker)
            and blocker.get("class") in allowed_classes
            and blocker.get("blocking") is True
        ]
        anchored_blocker_matches.append(matches)
        if not matches:
            failures.append(
                f"missing anchored blocker: {expected['anchor']} {allowed_classes}"
            )
    if anchored_blocker_matches and (
        any(len(matches) != 1 for matches in anchored_blocker_matches)
        or len(
            {
                next(iter(matches[0]))
                for matches in anchored_blocker_matches
                if len(matches) == 1 and len(matches[0]) == 1
            }
        )
        != len(anchored_blocker_matches)
    ):
        failures.append("distinct anchored blocker required for each material item")
    anchored_classification_matches: list[list[frozenset[str]]] = []
    for expected in oracle.get("required_anchored_classifications", []):
        anchor = expected["anchor"]
        allowed_states = expected["state"]
        if not isinstance(allowed_states, list):
            allowed_states = [allowed_states]
        matches = [
            identity_match_values(finding.get("identity", ""))
            for finding in actual_findings
            if finding_has_anchor(finding, anchor)
            and finding.get("domain") == expected["domain"]
            and finding.get("state") in allowed_states
        ]
        anchored_classification_matches.append(matches)
        if not matches:
            failures.append(
                "missing anchored classification: "
                f"{expected['anchor']} {expected['domain']} {allowed_states}"
            )
    if anchored_classification_matches and (
        any(len(matches) != 1 for matches in anchored_classification_matches)
        or len(
            {
                next(iter(matches[0]))
                for matches in anchored_classification_matches
                if len(matches) == 1 and len(matches[0]) == 1
            }
        )
        != len(anchored_classification_matches)
    ):
        failures.append(
            "distinct anchored classification required for each material item"
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


def _validate_case_capability(
    authorization: Any,
    *,
    case: dict[str, Any],
    plugin: Path,
    model: str,
    effort: str,
    timeout: int,
    arm: str,
    unit_id: str | None,
) -> None:
    del authorization, case, plugin, model, effort, timeout, arm, unit_id
    raise ValueError("generation-6 live capability is unavailable until Batch3")


def _phase_event_binding(
    authorization: Any,
    *,
    case_id: str,
    arm: str,
    phase: str,
    session_scope: str,
    thread_id: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    capability = _validated_capability(authorization)
    descriptor = capability.descriptor()
    profile = validate_invocation_profile(
        descriptor.get("invocation_profile"),
        require_bound_binary=True,
    )
    binding = {
        "provider": profile["provider"],
        "session_id": canonical_sha256(
            {
                "authority_sha256": capability.authority_sha256,
                "attempt_key": descriptor.get("attempt_id"),
                "case_id": case_id,
                "arm": arm,
                "session_scope": session_scope,
            }
        ),
        "thread_id": thread_id,
        "action_id": f"case:{case_id}:{arm}:{phase}",
        "attempt_key": descriptor.get("attempt_id"),
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
    authorization: Any = None,
    authorization_unit: str | None = None,
) -> dict[str, Any]:
    _validate_case_capability(
        authorization,
        case=case,
        plugin=plugin,
        model=model,
        effort=effort,
        timeout=timeout,
        arm=arm,
        unit_id=authorization_unit,
    )
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
        descriptor = _validated_capability(authorization).descriptor()
        effective_profile = validate_invocation_profile(
            descriptor.get("invocation_profile"),
            require_bound_binary=True,
        )
        accepted_baseline_failures = sorted(
            case["oracle"].get("accepted_baseline_failures", [])
        )
        semantic_context = {
            "task_id": f"case:{case['id']}:{arm}",
            "root_task_id": "root:evaluator",
            "executor_task_id": "executor:evaluator",
            "owner_label": "happycodex-evaluator",
            "destination_id": "repository:happycodex",
            "lineage_digest": input_digest,
            "role_config_digest": canonical_sha256(
                {
                    "filesystem_isolation": FILESYSTEM_ISOLATION_POLICY,
                    "disabled_features": DISABLED_FEATURES,
                }
            ),
            "repository_digest": _repository_binding_digest(
                case["id"],
                fixture["commits"][0],
                fixture["trees"][0],
            ),
            "outcome_digest": _outcome_binding_digest(case["prompt"]),
            "invocation_profile": effective_profile,
            "accepted_baseline_failures": accepted_baseline_failures,
        }
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
            authorization=authorization,
        )
        initial_phase = "prepare" if native else "initial"
        _persist_phase_raw(case_output, initial_phase, initial)
        _require_model_phase_success(
            initial,
            timed_out=initial_timed_out,
            phase=initial_phase,
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
        terminal_projections: list[dict[str, Any]] = []
        thread_id: str | None = None
        resume_thread_id: str | None = None
        fresh_recovery_thread_id: str | None = None
        fresh_recovery_result: dict[str, Any] | None = None
        failures: list[str] = []
        native_receipt: dict[str, Any] | None = None
        recovery_expected: dict[str, Any] | None = None
        if initial.returncode == 0:
            try:
                initial_binding, profile = _phase_event_binding(
                    authorization,
                    case_id=case["id"],
                    arm=arm,
                    phase=initial_phase,
                    session_scope="native-primary" if native else "initial",
                    thread_id=None,
                )
                (
                    initial_final,
                    initial_usage,
                    thread_id,
                    initial_terminal,
                ) = parse_events(
                    initial.stdout,
                    binding=initial_binding,
                    invocation_profile=profile,
                )
                terminal_projections.append(initial_terminal)
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
                    authorization=authorization,
                )
                _persist_phase_raw(case_output, "resume", resumed)
                _require_model_phase_success(
                    resumed,
                    timed_out=resume_timed_out,
                    phase="resume",
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
                        resume_binding, profile = _phase_event_binding(
                            authorization,
                            case_id=case["id"],
                            arm=arm,
                            phase="resume",
                            session_scope="native-primary",
                            thread_id=thread_id,
                        )
                        (
                            final,
                            resume_usage,
                            resume_thread_id,
                            resume_terminal,
                        ) = parse_events(
                            resumed.stdout,
                            binding=resume_binding,
                            invocation_profile=profile,
                        )
                        terminal_projections.append(resume_terminal)
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
                native_receipt["after_resume"] = compaction_receipt(
                    home,
                    thread_id,
                    prefix_length=before_resume["rollout_byte_count"],
                )
                if (
                    native_receipt["after_resume"]["rollout_byte_count"]
                    <= before_resume["rollout_byte_count"]
                    or native_receipt["after_resume"]["rollout_prefix_sha256"]
                    != before_resume["rollout_sha256"]
                ):
                    failures.append("native rollout was not append-consistent")
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
                    authorization=authorization,
                )
                _persist_phase_raw(case_output, "fresh-recovery", fresh_completed)
                _require_model_phase_success(
                    fresh_completed,
                    timed_out=fresh_timed_out,
                    phase="fresh recovery",
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
                        fresh_binding, profile = _phase_event_binding(
                            authorization,
                            case_id=case["id"],
                            arm=arm,
                            phase="fresh-recovery",
                            session_scope="fresh-recovery",
                            thread_id=None,
                        )
                        (
                            fresh_recovery_result,
                            fresh_usage,
                            fresh_recovery_thread_id,
                            fresh_terminal,
                        ) = parse_events(
                            fresh_completed.stdout,
                            binding=fresh_binding,
                            invocation_profile=profile,
                        )
                        terminal_projections.append(fresh_terminal)
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

        semantic_result: dict[str, Any] | None = None
        fresh_recovery_semantic_result: dict[str, Any] | None = None
        try:
            semantic_result = semantic_result_projection(
                final,
                context=semantic_context,
            )
            if fresh_recovery_result is not None:
                fresh_recovery_semantic_result = semantic_result_projection(
                    fresh_recovery_result,
                    context={
                        **semantic_context,
                        "task_id": f"case:{case['id']}:{arm}:fresh-recovery",
                    },
                )
        except ValueError as exc:
            failures.append(str(exc))

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
            "terminal_projections": terminal_projections,
            "prompt_sha256": sha256_bytes(prompt.encode()),
            "prepare_prompt_sha256": (
                sha256_bytes(initial_prompt.encode()) if native else None
            ),
            "semantic_input_sha256": input_digest,
            "invocation_profile": effective_profile,
            "accepted_baseline_failures": accepted_baseline_failures,
            "identities": {
                "engine": engine_inventory(ROOT),
                "package": copied_package,
                "toolchain": toolchain_identity(),
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
            "semantic_result": semantic_result,
            "fresh_recovery_result": fresh_recovery_result,
            "fresh_recovery_semantic_result": fresh_recovery_semantic_result,
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
            json.dumps(
                {
                    "cases": selected,
                    "coverage": sorted(REQUIRED_TAGS),
                    "invocation_profile": invocation_profile(
                        model=args.model,
                        effort=args.effort,
                        timeout_seconds=args.timeout,
                        arm=args.arm,
                    ),
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


def run_authorized(args: Any, authorization: Any) -> int:
    del args, authorization
    raise SystemExit("generation-6 live capability is unavailable until Batch3")
