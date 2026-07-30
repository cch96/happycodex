from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .model import (
    Anchor,
    CanonicalReport,
    ControlBlocker,
    Finding,
    FrozenMap,
    MachineFacts,
    ModelObservation,
    NextAction,
    SemanticError,
)


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_GIT_OID = re.compile(r"^[0-9a-f]{40}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/=+@-]*$")
_DOMAIN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_EXECPLAN = frozenset({"not_required", "missing", "usable", "needs_amendment"})
_EXECPLAN_ORDER = ("not_required", "missing", "usable", "needs_amendment")
_FINDING_DOMAINS = frozenset({"secret", "baseline_failure", "receipt", "other"})
_FINDING_STATE_ORDER = (
    "baseline_unchanged",
    "resolved",
    "candidate_new",
    "unknown",
)
_FINDING_STATES = frozenset(_FINDING_STATE_ORDER)
_BLOCKER_CLASS_ORDER = (
    "exhaustive_claim",
    "frozen_acceptance",
    "original_goal",
    "production_condition",
    "safety_data_integrity",
)
_BLOCKER_CLASSES = frozenset(_BLOCKER_CLASS_ORDER)
_GATES = (
    "user_selection",
    "contract_freeze",
    "red_oracle",
    "product_edit",
    "checks",
    "reconciliation",
    "candidate_freeze",
    "exact_final_review",
    "release",
)
_ACTIONS = frozenset(
    {
        "ASK_USER",
        "RECONCILE",
        "IMPLEMENT",
        "CHECK",
        "FREEZE",
        "EXACT_FINAL",
        "RELEASE",
        "CLOSE",
    }
)
_MILESTONE_PHASES = frozenset(
    {"working", "candidate_frozen", "exact_final", "closed"}
)
_RECOVERY_ACTIONS = frozenset(
    {
        "ask_user",
        "create_execplan",
        "complete_boundary_union",
        "create_contract_freeze_revision",
        "observe_red",
        "implement",
        "run_checks",
        "reconciliation",
        "freeze_candidate",
        "exact_final_review",
        "release",
        "none",
        "unknown",
    }
)
_RECOVERY_FIELDS = (
    "baseline_revision",
    "baseline_tree",
    "current_revision",
    "current_tree",
    "live_agents",
    "marker_ids",
    "milestone_phase",
    "next_action",
    "pending_gates",
    "tests",
    "worktree",
    "writer",
)


def _mapping(
    value: object,
    *,
    name: str,
    fields: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    if type(value) is not dict:
        raise SemanticError(f"{name} must be an exact object")
    if any(type(key) is not str for key in value):
        raise SemanticError(f"{name} keys must be exact strings")
    if fields is not None and set(value) != set(fields):
        missing = tuple(sorted(set(fields) - set(value)))
        unknown = tuple(sorted(set(value) - set(fields)))
        raise SemanticError(
            f"{name} fields mismatch: missing={missing}, unknown={unknown}"
        )
    return value


def _list(value: object, *, name: str, maximum: int = 4096) -> list[Any]:
    if type(value) is not list:
        raise SemanticError(f"{name} must be an exact array")
    if len(value) > maximum:
        raise SemanticError(f"{name} exceeds capacity {maximum}")
    return value


def _text(
    value: object,
    *,
    name: str,
    maximum: int = 16384,
    identifier: bool = False,
) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise SemanticError(f"{name} must be non-empty exact canonical text")
    if len(value) > maximum:
        raise SemanticError(f"{name} exceeds capacity {maximum}")
    if identifier and _IDENTIFIER.fullmatch(value) is None:
        raise SemanticError(f"{name} is not a canonical identifier")
    return value


def _digest(value: object, *, name: str) -> str:
    text = _text(value, name=name)
    if _DIGEST.fullmatch(text) is None:
        raise SemanticError(f"{name} must be a lowercase SHA-256")
    return text


def _enum(value: object, allowed: frozenset[str], *, name: str) -> str:
    text = _text(value, name=name)
    if text not in allowed:
        raise SemanticError(f"{name} has an unknown value")
    return text


def _bool(value: object, *, name: str) -> bool:
    if type(value) is not bool:
        raise SemanticError(f"{name} must be an exact boolean")
    return value


def _int(value: object, *, name: str) -> int:
    if type(value) is not int or value < 0:
        raise SemanticError(f"{name} must be a nonnegative exact integer")
    return value


def _texts(
    value: object,
    *,
    name: str,
    allowed: tuple[str, ...] | None = None,
    identifier: bool = False,
    canonical_order: bool = True,
) -> tuple[str, ...]:
    parsed = tuple(
        _text(item, name=f"{name}[]", identifier=identifier)
        for item in _list(value, name=name)
    )
    if len(parsed) != len(set(parsed)):
        raise SemanticError(f"{name} must be unique")
    if allowed is not None and any(item not in allowed for item in parsed):
        raise SemanticError(f"{name} contains an unknown value")
    if canonical_order:
        order = (
            tuple(item for item in allowed if item in parsed)
            if allowed is not None
            else tuple(sorted(parsed))
        )
        if parsed != order:
            raise SemanticError(f"{name} must use canonical order")
    return parsed


def _freeze(value: object, *, name: str = "value") -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return tuple(_freeze(item, name=f"{name}[]") for item in value)
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise SemanticError(f"{name} keys must be exact strings")
        return FrozenMap(
            tuple(
                (key, _freeze(value[key], name=f"{name}.{key}"))
                for key in sorted(value)
            )
        )
    raise SemanticError(f"{name} contains an unsupported or mutable value")


def _thaw(value: object) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is tuple:
        return [_thaw(item) for item in value]
    if type(value) is FrozenMap:
        return {key: _thaw(item) for key, item in value._items}
    raise SemanticError("unrecognized trusted value")


def _anchor(value: object, *, name: str) -> Anchor:
    record = _mapping(value, name=name)
    kind = _text(record.get("kind"), name=f"{name}.kind")
    if kind == "path":
        record = _mapping(
            value,
            name=name,
            fields=("kind", "repository", "value"),
        )
        repository = _text(
            record["repository"],
            name=f"{name}.repository",
            identifier=True,
        )
        path = _text(record["value"], name=f"{name}.value", maximum=4096)
        if (
            path.startswith("/")
            or "\\" in path
            or any(item in ("", ".", "..") for item in path.split("/"))
        ):
            raise SemanticError(f"{name} path must be exact and relative")
        return Anchor("path", repository, path)
    if kind == "marker":
        record = _mapping(value, name=name, fields=("kind", "value"))
        marker = _text(
            record["value"], name=f"{name}.value", identifier=True
        )
        return Anchor("marker", "marker", marker)
    if kind == "digest":
        record = _mapping(
            value,
            name=name,
            fields=("kind", "label", "value"),
        )
        label = _text(record["label"], name=f"{name}.label", identifier=True)
        raw = _text(record["value"], name=f"{name}.value")
        if _DIGEST.fullmatch(raw) is None and _GIT_OID.fullmatch(raw) is None:
            raise SemanticError(f"{name}.value must be a Git oid or SHA-256")
        return Anchor("digest", label, raw)
    raise SemanticError(f"{name} has an unknown anchor kind")


def _anchors(value: object, *, name: str) -> tuple[Anchor, ...]:
    parsed = tuple(
        sorted(
            _anchor(item, name=f"{name}[]")
            for item in _list(value, name=name, maximum=256)
        )
    )
    if not parsed or len(parsed) != len(set(parsed)):
        raise SemanticError(f"{name} must be non-empty and unique")
    return parsed


def _finding(value: object, *, name: str) -> Finding:
    record = _mapping(
        value,
        name=name,
        fields=("id", "domain", "status", "anchors", "blocker"),
    )
    blocker = record["blocker"]
    blocker_class: str | None = None
    blocker_reason: str | None = None
    if blocker is not None:
        block = _mapping(
            blocker,
            name=f"{name}.blocker",
            fields=("class", "reason"),
        )
        blocker_class = _enum(
            block["class"],
            _BLOCKER_CLASSES,
            name=f"{name}.blocker.class",
        )
        blocker_reason = _text(
            block["reason"],
            name=f"{name}.blocker.reason",
            maximum=32768,
        )
    status = _enum(record["status"], _FINDING_STATES, name=f"{name}.status")
    if status == "resolved" and blocker is not None:
        raise SemanticError("resolved finding cannot carry a blocker")
    return Finding(
        finding_id=_text(record["id"], name=f"{name}.id", identifier=True),
        domain=_enum(record["domain"], _FINDING_DOMAINS, name=f"{name}.domain"),
        status=status,
        anchors=_anchors(record["anchors"], name=f"{name}.anchors"),
        blocker_class=blocker_class,
        blocker_reason=blocker_reason,
    )


def _findings(value: object, *, name: str) -> tuple[Finding, ...]:
    parsed = tuple(
        sorted(
            (
                _finding(item, name=f"{name}[]")
                for item in _list(value, name=name, maximum=4096)
            ),
            key=lambda item: item.finding_id,
        )
    )
    ids = tuple(item.finding_id for item in parsed)
    if len(ids) != len(set(ids)):
        raise SemanticError(f"{name} contains duplicate FindingIds")
    return parsed


def _task_binding(value: object) -> FrozenMap:
    fields = (
        "task_id",
        "root_task_id",
        "executor_task_id",
        "owner_label",
        "destination_id",
        "lineage_digest",
        "role_config_digest",
        "repository_digest",
        "outcome_digest",
        "invocation_profile_digest",
    )
    record = _mapping(value, name="task_binding", fields=fields)
    parsed: dict[str, str] = {}
    for field in fields[:5]:
        parsed[field] = _text(
            record[field],
            name=f"task_binding.{field}",
            identifier=True,
        )
    for field in fields[5:]:
        parsed[field] = _digest(
            record[field], name=f"task_binding.{field}"
        )
    if len(
        {
            parsed["task_id"],
            parsed["root_task_id"],
            parsed["executor_task_id"],
        }
    ) != 3:
        raise SemanticError("task identities must be distinct")
    return FrozenMap(tuple((key, parsed[key]) for key in sorted(parsed)))


def parse_machine_facts(value: object) -> MachineFacts:
    record = _mapping(
        value,
        name="MachineFacts",
        fields=(
            "schema_generation",
            "task_binding",
            "accepted_baseline_failures",
            "infrastructure_generation",
        ),
    )
    generation = _int(record["schema_generation"], name="schema_generation")
    if generation != 7:
        raise SemanticError("only schema generation 7 is accepted")
    return MachineFacts(
        schema_generation=generation,
        task_binding=_task_binding(record["task_binding"]),
        accepted_baseline_failures=_texts(
            record["accepted_baseline_failures"],
            name="accepted_baseline_failures",
            identifier=True,
        ),
        infrastructure_generation=_digest(
            record["infrastructure_generation"],
            name="infrastructure_generation",
        ),
    )


def _recovery(value: object) -> FrozenMap | None:
    if value is None:
        return None
    record = _mapping(value, name="recovery", fields=_RECOVERY_FIELDS)
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        raw = _text(record[field], name=f"recovery.{field}")
        if _GIT_OID.fullmatch(raw) is None:
            raise SemanticError(f"recovery.{field} must be a Git oid")
    if record["writer"] != "Root" or record["worktree"] not in {"clean", "dirty"}:
        raise SemanticError("recovery writer or worktree state is invalid")
    _enum(
        record["milestone_phase"],
        _MILESTONE_PHASES,
        name="recovery.milestone_phase",
    )
    _enum(
        record["next_action"],
        _RECOVERY_ACTIONS,
        name="recovery.next_action",
    )
    _texts(
        record["pending_gates"],
        name="recovery.pending_gates",
        allowed=_GATES,
    )
    _texts(record["marker_ids"], name="recovery.marker_ids", identifier=True)
    tests = _mapping(
        record["tests"],
        name="recovery.tests",
        fields=("accepted_failures", "failed", "marker_ids", "passed"),
    )
    for field in ("accepted_failures", "failed", "passed"):
        _int(tests[field], name=f"recovery.tests.{field}")
    if tests["accepted_failures"] != tests["failed"]:
        raise SemanticError("recovery contains unaccepted test failures")
    _texts(
        tests["marker_ids"],
        name="recovery.tests.marker_ids",
        identifier=True,
    )
    agents = _list(record["live_agents"], name="recovery.live_agents")
    agent_ids: set[str] = set()
    for item in agents:
        agent = _mapping(
            item,
            name="recovery.live_agent",
            fields=("id", "receipt_reproduced", "status"),
        )
        identity = _text(
            agent["id"], name="recovery.live_agent.id", identifier=True
        )
        if (
            identity in agent_ids
            or agent["status"] != "terminal"
            or agent["receipt_reproduced"] is not True
        ):
            raise SemanticError("recovery live agent is not uniquely terminal")
        agent_ids.add(identity)
    frozen = _freeze(record, name="recovery")
    if type(frozen) is not FrozenMap:
        raise AssertionError("recovery freeze failed")
    return frozen


def parse_model_observation(value: object) -> ModelObservation:
    record = _mapping(
        value,
        name="ModelObservation",
        fields=(
            "qualifies",
            "execplan_condition",
            "findings",
            "open_gates",
            "evidence",
            "reason",
            "recovery",
        ),
    )
    return ModelObservation(
        qualifies=_bool(record["qualifies"], name="qualifies"),
        execplan_condition=_enum(
            record["execplan_condition"],
            _EXECPLAN,
            name="execplan_condition",
        ),
        findings=_findings(record["findings"], name="findings"),
        open_gates=_texts(
            record["open_gates"],
            name="open_gates",
            allowed=_GATES,
        ),
        evidence=_texts(
            record["evidence"],
            name="evidence",
            canonical_order=False,
        ),
        reason=_text(record["reason"], name="reason", maximum=32768),
        recovery=_recovery(record["recovery"]),
    )


def _anchor_raw(value: Anchor) -> dict[str, str]:
    if type(value) is not Anchor:
        raise SemanticError("exact Anchor required")
    return value.semantic_value()


def _finding_raw(value: Finding) -> dict[str, object]:
    if type(value) is not Finding:
        raise SemanticError("exact Finding required")
    blocker = (
        None
        if value.blocker_class is None
        else {"class": value.blocker_class, "reason": value.blocker_reason}
    )
    return {
        "id": value.finding_id,
        "domain": value.domain,
        "status": value.status,
        "anchors": [_anchor_raw(item) for item in value.anchors],
        "blocker": blocker,
    }


def _facts_raw(value: MachineFacts) -> dict[str, object]:
    if type(value) is not MachineFacts:
        raise SemanticError("exact MachineFacts required")
    return {
        "schema_generation": value.schema_generation,
        "task_binding": _thaw(value.task_binding),
        "accepted_baseline_failures": list(value.accepted_baseline_failures),
        "infrastructure_generation": value.infrastructure_generation,
    }


def _observation_raw(value: ModelObservation) -> dict[str, object]:
    if type(value) is not ModelObservation:
        raise SemanticError("exact ModelObservation required")
    return {
        "qualifies": value.qualifies,
        "execplan_condition": value.execplan_condition,
        "findings": [_finding_raw(item) for item in value.findings],
        "open_gates": list(value.open_gates),
        "evidence": list(value.evidence),
        "reason": value.reason,
        "recovery": None if value.recovery is None else _thaw(value.recovery),
    }


def _blocker_raw(value: ControlBlocker) -> dict[str, object]:
    if type(value) is not ControlBlocker:
        raise SemanticError("exact ControlBlocker required")
    return {
        "finding_id": value.finding_id,
        "class": value.blocker_class,
        "anchors": [_anchor_raw(item) for item in value.anchors],
    }


def _action_raw(value: NextAction) -> dict[str, str]:
    if type(value) is not NextAction:
        raise SemanticError("exact NextAction required")
    return value.semantic_value()


def report_to_raw(value: CanonicalReport) -> dict[str, object]:
    from .reducer import validate_report

    validate_report(value)
    return {
        "schema_generation": 7,
        "facts": _facts_raw(value.facts),
        "observation": _observation_raw(value.observation),
        "findings": [_finding_raw(item) for item in value.findings],
        "blockers": [_blocker_raw(item) for item in value.blockers],
        "next_action": _action_raw(value.next_action),
        "state_key": value.state_key,
        "action_key": value.action_key,
    }


def parse_report(value: object) -> CanonicalReport:
    record = _mapping(
        value,
        name="CanonicalReport",
        fields=(
            "schema_generation",
            "facts",
            "observation",
            "findings",
            "blockers",
            "next_action",
            "state_key",
            "action_key",
        ),
    )
    if _int(record["schema_generation"], name="schema_generation") != 7:
        raise SemanticError("only schema generation 7 reports are accepted")
    from .reducer import build_report

    report = build_report(
        parse_machine_facts(record["facts"]),
        parse_model_observation(record["observation"]),
    )
    if report_to_raw(report) != value:
        raise SemanticError("stored report differs from pure generation-7 reduction")
    return report


def _canonical_value(value: object) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [_canonical_value(item) for item in value]
    if type(value) is tuple:
        return [_canonical_value(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise SemanticError("canonical mapping keys must be exact strings")
        return {key: _canonical_value(value[key]) for key in sorted(value)}
    if type(value) is FrozenMap:
        return {key: _canonical_value(item) for key, item in value._items}
    if type(value) is Anchor:
        return _canonical_value(value.semantic_value())
    if type(value) is Finding:
        return _canonical_value(value.semantic_value())
    if type(value) is MachineFacts:
        return _canonical_value(value.semantic_value())
    if type(value) is ControlBlocker:
        return _canonical_value(value.semantic_value())
    if type(value) is NextAction:
        return _canonical_value(value.semantic_value())
    if type(value) is ModelObservation:
        return _canonical_value(_observation_raw(value))
    if type(value) is CanonicalReport:
        return _canonical_value(report_to_raw(value))
    raise SemanticError("canonical encoding rejects untrusted or mutable values")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        _canonical_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def semantic_digest(kind: str, value: object) -> str:
    domain = _text(kind, name="hash domain", maximum=128)
    if _DOMAIN.fullmatch(domain) is None:
        raise SemanticError("hash domain must be lowercase kebab-case")
    return hashlib.sha256(
        f"happycodex/schema7/{domain}\0".encode("ascii")
        + canonical_bytes(value)
    ).hexdigest()


__all__ = (
    "canonical_bytes",
    "parse_machine_facts",
    "parse_model_observation",
    "parse_report",
    "report_to_raw",
    "semantic_digest",
)
