from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError
from enum import Enum
from hashlib import sha256
from inspect import signature
from pathlib import Path
import unittest
from unittest import mock

import evaluation.semantic as semantic
from evaluation.semantic.types import _issue_authority, _make_report
from evaluation.semantic import (
    ActionKind,
    AuthorityProvenance,
    CapacityError,
    EffectDecision,
    Facts,
    Id,
    InfraKind,
    NextAction,
    ProgressReport,
    SemanticError,
    TaskBinding,
    canonical_bytes,
    enforce_effect,
    make_attempt_key,
    make_progress_key,
    parse_facts,
    reduce_facts,
    replay_report,
)


HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64


def raw_envelope() -> dict[str, object]:
    return {
        "schema_generation": 6,
        "task_binding": {
            "task_id": "task-a",
            "root_task_id": "root-a",
            "executor_task_id": "executor-a",
            "owner_label": "owner-a",
            "destination_id": "destination-a",
            "lineage_digest": HEX_A,
            "role_config_digest": HEX_B,
            "repository_digest": HEX_B,
            "outcome_digest": HEX_C,
        },
        "facts": {
            "claims": [{"id": "claim-a", "state": "OPEN", "evidence": ["source-a"]}],
            "findings": [
                {"id": "finding-a", "state": "OPEN", "evidence": ["source-a"]}
            ],
            "gates": [
                {
                    "id": "gate-a",
                    "state": "OPEN",
                    "family_id": "family-a",
                    "evidence": ["source-a"],
                }
            ],
            "checks": [{"id": "check-a", "state": "PASS", "evidence": ["source-a"]}],
            "families": [
                {"id": "family-a", "state": "OPEN", "evidence": ["source-a"]}
            ],
            "replacements": [
                {
                    "id": "infra-a",
                    "kind": "REPLACED",
                    "prior": HEX_A,
                    "current": HEX_B,
                    "evidence": ["source-a"],
                }
            ],
            "paths": [
                {
                    "id": "path-a",
                    "repository_id": "repository-a",
                    "path": "src/app.py",
                }
            ],
            "markers": [{"id": "marker-a", "value": "MARKER-A"}],
        },
        "administration": {
            "authority_receipts": [{"id": "authority-a", "value": HEX_A}],
            "resource_claims": [{"id": "resource-a", "value": HEX_A}],
            "receipts": [{"id": "receipt-a", "value": HEX_A}],
            "cursors": [{"id": "cursor-a", "value": "offset-1"}],
            "timestamps": [{"id": "timestamp-a", "value": 1}],
            "consumptions": [{"id": "attempt-a", "value": HEX_A}],
        },
    }


def terminal_envelope() -> dict[str, object]:
    candidate = raw_envelope()
    candidate["facts"]["checks"][0]["state"] = "PASS"
    candidate["facts"]["claims"][0]["state"] = "VERIFIED"
    candidate["facts"]["findings"][0]["state"] = "RESOLVED"
    candidate["facts"]["families"][0]["state"] = "CLOSED"
    candidate["facts"]["gates"][0]["state"] = "SATISFIED"
    return candidate


def adapter_authority(
    binding: TaskBinding,
    action: object,
    *,
    channel: str = "current_task_user",
    root_task: Id | None = None,
    source_task: Id | None = None,
    target_task: Id | None = None,
    executor_task: Id | None = None,
    destination: Id | None = None,
    lineage: Id | None = None,
    target: Id | None = None,
    scope: Id | None = None,
) -> AuthorityProvenance:
    return _issue_authority(
        channel=channel,
        root_task=root_task or binding.root_task,
        source_task=source_task or binding.task,
        target_task=target_task or binding.task,
        executor_task=executor_task or binding.executor_task,
        destination=destination or binding.destination,
        lineage=lineage or binding.lineage,
        message_id=Id("message", "message-a"),
        turn_id=Id("turn", "turn-a"),
        content_digest=Id("content", HEX_C),
        target=target or action.target,
        scope=scope or action.scope,
    )


class PublicSurfaceTests(unittest.TestCase):
    def test_public_surface_is_closed_and_bounded(self) -> None:
        self.assertEqual(
            semantic.__all__,
            (
                "ActionKind",
                "AuthorityProvenance",
                "CapacityError",
                "EffectDecision",
                "EffectGate",
                "Facts",
                "Id",
                "InfraKind",
                "NextAction",
                "ProgressReport",
                "SemanticError",
                "TaskBinding",
                "canonical_bytes",
                "enforce_effect",
                "make_attempt_key",
                "make_progress_key",
                "parse_facts",
                "reduce_facts",
                "replay_report",
            ),
        )
        self.assertLessEqual(len(semantic.__all__), 20)
        for retired in (
            "AdminFacts",
            "MachineEnvelope",
            "StateProjection",
            "canonical_set",
            "make_state_key",
        ):
            self.assertFalse(hasattr(semantic, retired), retired)
        for private_seam in ("_issue_authority", "_make_facts", "_make_report"):
            self.assertFalse(hasattr(semantic, private_seam), private_seam)
        self.assertFalse(hasattr(AuthorityProvenance, "from_adapter"))
        self.assertEqual(tuple(signature(AuthorityProvenance).parameters), ())
        self.assertEqual(tuple(signature(Facts).parameters), ())
        self.assertEqual(tuple(signature(ProgressReport).parameters), ())

    def test_final_semantic_package_is_exact(self) -> None:
        root = Path(semantic.__file__).parent
        self.assertEqual(
            {path.name for path in root.glob("*.py")},
            {"__init__.py", "types.py", "canonical.py", "parse.py", "decide.py"},
        )


class PrimaryKeyAndParseTests(unittest.TestCase):
    def test_identical_primary_key_duplicates_reject_in_every_domain(self) -> None:
        template = raw_envelope()
        for section in ("facts", "administration"):
            for domain, records in template[section].items():
                candidate = copy.deepcopy(template)
                candidate[section][domain].append(copy.deepcopy(records[0]))
                with self.subTest(section=section, domain=domain):
                    with self.assertRaisesRegex(SemanticError, "duplicate primary key"):
                        parse_facts(candidate)

    def test_conflicting_primary_key_duplicates_reject_in_every_domain(self) -> None:
        template = raw_envelope()
        for section in ("facts", "administration"):
            for domain, records in template[section].items():
                candidate = copy.deepcopy(template)
                conflict = copy.deepcopy(records[0])
                mutable = next(key for key in conflict if key != "id")
                value = conflict[mutable]
                if isinstance(value, list):
                    conflict[mutable] = [*value, "different"]
                elif isinstance(value, int):
                    conflict[mutable] = value + 1
                else:
                    conflict[mutable] = f"{value}-different"
                candidate[section][domain].append(conflict)
                with self.subTest(section=section, domain=domain):
                    with self.assertRaisesRegex(SemanticError, "duplicate primary key"):
                        parse_facts(candidate)

    def test_derived_state_and_authority_injection_reject(self) -> None:
        for field in (
            "next_action",
            "phase",
            "permission",
            "projection",
            "blocker",
            "authority_provenance",
        ):
            candidate = raw_envelope()
            candidate[field] = {}
            with self.subTest(field=field):
                with self.assertRaisesRegex(SemanticError, "unknown"):
                    parse_facts(candidate)

    def test_wrong_tags_and_deep_mutability_reject_or_freeze(self) -> None:
        with self.assertRaisesRegex(SemanticError, "root_task"):
            TaskBinding(
                task=Id("task", "task-a"),
                root_task=Id("task", "root-a"),
                executor_task=Id("executor_task", "executor-a"),
                owner=Id("owner", "owner-a"),
                destination=Id("destination", "destination-a"),
                lineage=Id("lineage", HEX_A),
                role_config=Id("role_config", HEX_B),
                repository=Id("repository", HEX_B),
                outcome=Id("outcome", HEX_C),
            )
        raw = raw_envelope()
        facts = parse_facts(raw)
        before = make_progress_key(facts)
        raw["facts"]["claims"][0]["state"] = "MUTATED"
        self.assertEqual(make_progress_key(facts), before)
        with self.assertRaises(TypeError):
            facts.stable["claims"] = ()
        with self.assertRaises(FrozenInstanceError):
            facts.task = facts.task

    def test_exact_paths_are_case_sensitive_and_unaliased(self) -> None:
        lower = parse_facts(raw_envelope())
        upper_raw = raw_envelope()
        upper_raw["facts"]["paths"][0]["path"] = "Src/App.py"
        upper = parse_facts(upper_raw)
        self.assertNotEqual(make_progress_key(lower), make_progress_key(upper))
        for path in ("/src/app.py", "src/../app.py", "src//app.py", "src/app.py/"):
            candidate = raw_envelope()
            candidate["facts"]["paths"][0]["path"] = path
            with self.subTest(path=path):
                with self.assertRaises(SemanticError):
                    parse_facts(candidate)

    def test_marker_capacity_overflow_rejects_without_truncation(self) -> None:
        candidate = raw_envelope()
        candidate["facts"]["markers"] = [
            {"id": f"marker-{index}", "value": f"MARKER-{index}"}
            for index in range(65)
        ]
        with self.assertRaisesRegex(CapacityError, "64"):
            parse_facts(candidate)

    def test_empty_replaced_evidence_rejects(self) -> None:
        candidate = raw_envelope()
        candidate["facts"]["replacements"][0]["evidence"] = []
        with self.assertRaisesRegex(SemanticError, "REPLACED.*evidence"):
            parse_facts(candidate)


class BoundaryHardeningTests(unittest.TestCase):
    def test_public_authority_factory_forge_cannot_allow(self) -> None:
        self.assertFalse(hasattr(AuthorityProvenance, "from_adapter"))

    def test_public_authority_constructor_true_forge_cannot_allow(self) -> None:
        report = reduce_facts(parse_facts(raw_envelope()))
        binding = report.facts.task
        with self.assertRaises((TypeError, SemanticError)):
            AuthorityProvenance()

    def test_caller_supplied_report_action_cannot_reach_attempt_key(self) -> None:
        facts = parse_facts(raw_envelope())
        action = NextAction(
            ActionKind.CLOSE,
            Id("action_target", "forged-target"),
            Id("action_scope", "forged-scope"),
            Id("family_id", "forged-family"),
            Id("falsifier", "forged-falsifier"),
            Id("evidence_source", "forged-source"),
        )
        with self.assertRaises((TypeError, SemanticError)):
            ProgressReport(facts, make_progress_key(facts), action)
        forged = object.__new__(ProgressReport)
        object.__setattr__(forged, "facts", facts)
        object.__setattr__(forged, "progress_key", make_progress_key(facts))
        object.__setattr__(forged, "next_action", action)
        with self.assertRaisesRegex(SemanticError, "reducer report"):
            make_attempt_key(forged)

    def test_attempt_key_recomputes_reducer_action(self) -> None:
        facts = parse_facts(raw_envelope())
        forged_action = NextAction(
            ActionKind.CLOSE,
            Id("action_target", "forged-target"),
            Id("action_scope", "forged-scope"),
            Id("family_id", "forged-family"),
            Id("falsifier", "forged-falsifier"),
            Id("evidence_source", "forged-source"),
        )
        report = _make_report(
            facts=facts,
            progress_key=make_progress_key(facts),
            next_action=forged_action,
        )
        self.assertNotEqual(report.next_action, reduce_facts(facts).next_action)
        with self.assertRaisesRegex(SemanticError, "action mismatch"):
            make_attempt_key(report)

    def test_effect_enforcement_recomputes_reducer_action(self) -> None:
        facts = parse_facts(raw_envelope())
        forged_action = NextAction(
            ActionKind.CLOSE,
            Id("action_target", "forged-target"),
            Id("action_scope", "forged-scope"),
            Id("family_id", "forged-family"),
            Id("falsifier", "forged-falsifier"),
            Id("evidence_source", "forged-source"),
        )
        report = _make_report(
            facts=facts,
            progress_key=make_progress_key(facts),
            next_action=forged_action,
        )
        self.assertNotEqual(report.next_action, reduce_facts(facts).next_action)
        authority = adapter_authority(report.facts.task, forged_action)
        with self.assertRaisesRegex(SemanticError, "action mismatch"):
            enforce_effect(report, authority)

    def test_str_enum_identity_is_rejected(self) -> None:
        class Sneaky(str, Enum):
            VALUE = "sneaky"

        with self.assertRaisesRegex(SemanticError, "identity"):
            Id("task", Sneaky.VALUE)

        class TextSubclass(str):
            pass

        with self.assertRaisesRegex(SemanticError, "identity"):
            Id("task", TextSubclass("sneaky"))

    def test_duplicate_evidence_rejects_and_order_is_canonical(self) -> None:
        duplicate = raw_envelope()
        duplicate["facts"]["claims"][0]["evidence"] = ["source-a", "source-a"]
        with self.assertRaisesRegex(SemanticError, "duplicate.*evidence"):
            parse_facts(duplicate)

        unsorted = raw_envelope()
        unsorted["facts"]["claims"][0]["evidence"] = ["source-z", "source-a"]
        facts = parse_facts(unsorted)
        self.assertEqual(
            facts.stable["claims"][0].payload["evidence"],
            ("source-a", "source-z"),
        )
        ordered = raw_envelope()
        ordered["facts"]["claims"][0]["evidence"] = ["source-a", "source-z"]
        self.assertEqual(
            make_progress_key(facts),
            make_progress_key(parse_facts(ordered)),
        )

    def test_facts_and_record_constructors_cannot_bypass_parser(self) -> None:
        facts = parse_facts(raw_envelope())
        with self.assertRaises((TypeError, SemanticError)):
            Facts(
                facts.schema_generation,
                facts.task,
                facts.stable,
                facts.administration,
            )
        forged = object.__new__(Facts)
        object.__setattr__(forged, "schema_generation", facts.schema_generation)
        object.__setattr__(forged, "task", facts.task)
        object.__setattr__(forged, "stable", facts.stable)
        object.__setattr__(forged, "administration", facts.administration)
        with self.assertRaisesRegex(SemanticError, "parser-issued"):
            make_progress_key(forged)

        from evaluation.semantic.types import _Record

        with self.assertRaisesRegex(SemanticError, "payload.*id"):
            _Record(Id("claim_id", "claim-a"), {"id": "override"})

    def test_parser_enforces_exact_states_and_tagged_gate_family(self) -> None:
        for domain in ("checks", "claims", "families", "findings", "gates"):
            candidate = raw_envelope()
            candidate["facts"][domain][0]["state"] = "ARBITRARY"
            with self.subTest(domain=domain):
                with self.assertRaisesRegex(SemanticError, f"{domain}.*state"):
                    parse_facts(candidate)

        facts = parse_facts(raw_envelope())
        family = facts.stable["gates"][0].payload["family_id"]
        self.assertIs(type(family), Id)
        self.assertEqual(family.tag, "family_id")

    def test_open_state_derives_safe_action_without_close(self) -> None:
        for domain, unresolved_state, expected, scope in (
            ("checks", "PENDING", ActionKind.VERIFY, "family:task:task-a"),
            ("claims", "OPEN", ActionKind.RECONCILE, "family:task:task-a"),
            ("findings", "OPEN", ActionKind.IMPLEMENT_BATCH, "family:task:task-a"),
            ("families", "OPEN", ActionKind.IMPLEMENT_BATCH, "family:family-a"),
            ("gates", "OPEN", ActionKind.RECONCILE, "family:family-a"),
        ):
            candidate = terminal_envelope()
            candidate["facts"][domain][0]["state"] = unresolved_state
            report = reduce_facts(parse_facts(candidate))
            with self.subTest(domain=domain):
                self.assertIs(
                    report.next_action.kind,
                    expected,
                    f"open {domain} must not produce CLOSE",
                )
                self.assertEqual(
                    report.next_action.scope,
                    Id("action_scope", scope),
                )

    def test_all_terminal_without_work_closes(self) -> None:
        report = reduce_facts(parse_facts(terminal_envelope()))
        self.assertIs(report.next_action.kind, ActionKind.CLOSE)
        alternatives = terminal_envelope()
        alternatives["facts"]["checks"][0]["state"] = "BASELINE_ACCEPTED"
        alternatives["facts"]["claims"][0]["state"] = "N/A"
        alternatives["facts"]["findings"][0]["state"] = "BASELINE_ACCEPTED"
        alternatives["facts"]["families"][0]["state"] = "N/A"
        alternatives["facts"]["gates"][0]["state"] = "WAIVED"
        self.assertIs(
            reduce_facts(parse_facts(alternatives)).next_action.kind,
            ActionKind.CLOSE,
        )


class ProgressAndReplayTests(unittest.TestCase):
    def test_parse_reduce_serialize_replay_roundtrip(self) -> None:
        report = reduce_facts(parse_facts(raw_envelope()))
        replayed = replay_report(report.to_wire())
        self.assertEqual(report, replayed)
        self.assertEqual(report.progress_key, make_progress_key(report.facts))

    def test_stored_progress_key_and_action_mismatch_reject(self) -> None:
        report = reduce_facts(parse_facts(raw_envelope()))
        wrong_key = report.to_wire()
        wrong_key["progress_key"] = HEX_C
        with self.assertRaisesRegex(SemanticError, "progress key mismatch"):
            replay_report(wrong_key)
        wrong_action = report.to_wire()
        wrong_action["next_action"]["target"] = "different"
        with self.assertRaisesRegex(SemanticError, "action mismatch"):
            replay_report(wrong_action)

    def test_attempt_key_accepts_only_reducer_report(self) -> None:
        self.assertEqual(tuple(signature(make_attempt_key).parameters), ("report",))
        report = reduce_facts(parse_facts(raw_envelope()))
        first = make_attempt_key(report)
        changed = raw_envelope()
        changed["facts"]["gates"][0]["evidence"] = ["source-b"]
        self.assertNotEqual(first, make_attempt_key(reduce_facts(parse_facts(changed))))
        tampered = copy.copy(report)
        object.__setattr__(tampered, "progress_key", Id("progress_key", HEX_C))
        with self.assertRaisesRegex(SemanticError, "progress key mismatch"):
            make_attempt_key(tampered)

    def test_admin_only_changes_do_not_change_progress_or_attempt(self) -> None:
        baseline_report = reduce_facts(parse_facts(raw_envelope()))
        for domain in raw_envelope()["administration"]:
            candidate = raw_envelope()
            candidate["administration"][domain][0]["value"] = (
                2 if domain == "timestamps" else f"{HEX_B}-{domain}"
            )
            report = reduce_facts(parse_facts(candidate))
            with self.subTest(domain=domain):
                self.assertEqual(report.progress_key, baseline_report.progress_key)
                self.assertEqual(make_attempt_key(report), make_attempt_key(baseline_report))

    def test_only_evidenced_replacement_changes_progress(self) -> None:
        first = reduce_facts(parse_facts(raw_envelope()))
        changed = raw_envelope()
        changed["facts"]["replacements"][0]["current"] = HEX_C
        second = reduce_facts(parse_facts(changed))
        self.assertNotEqual(first.progress_key, second.progress_key)

    def test_canonical_encoder_is_single_exact_and_rejects_mutable_input(self) -> None:
        self.assertEqual(canonical_bytes({"b": 2, "a": 1}), b'{"a":1,"b":2}')
        with self.assertRaisesRegex(SemanticError, "mutable"):
            canonical_bytes({"a": [1]})

        class SneakyKey(str, Enum):
            VALUE = "sneaky"

        with self.assertRaisesRegex(SemanticError, "mapping keys"):
            canonical_bytes({SneakyKey.VALUE: 1})


class AuthorityEnforcementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = reduce_facts(parse_facts(raw_envelope()))
        self.binding = self.report.facts.task

    def test_direct_target_allows(self) -> None:
        gate = enforce_effect(
            self.report,
            adapter_authority(self.binding, self.report.next_action),
        )
        self.assertIs(gate.decision, EffectDecision.ALLOW)

    def test_legitimate_cross_task_asks_user(self) -> None:
        gate = enforce_effect(
            self.report,
            adapter_authority(
                self.binding,
                self.report.next_action,
                channel="cross_task_user_delegation",
                source_task=Id("task", "other-task"),
            ),
        )
        self.assertIs(gate.decision, EffectDecision.ASK_USER)

    def test_missing_and_spoofed_authority_refuse(self) -> None:
        self.assertIs(
            enforce_effect(self.report, None).decision,
            EffectDecision.REFUSE,
        )
        spoofed = object.__new__(AuthorityProvenance)
        gate = enforce_effect(self.report, spoofed)
        self.assertIs(gate.decision, EffectDecision.REFUSE)
        self.assertEqual(gate.reason, "spoofed")

    def test_wrong_binding_or_action_metadata_refuses(self) -> None:
        variants = {
            "root": {"root_task": Id("root_task", "root-other")},
            "destination": {"destination": Id("destination", "destination-other")},
            "lineage": {"lineage": Id("lineage", HEX_C)},
            "executor": {"executor_task": Id("executor_task", "executor-other")},
            "target_task": {
                "source_task": Id("task", "task-other"),
                "target_task": Id("task", "task-other"),
            },
            "target": {"target": Id("action_target", "target-other")},
            "scope": {"scope": Id("action_scope", "scope-other")},
        }
        for reason, changes in variants.items():
            gate = enforce_effect(
                self.report,
                adapter_authority(self.binding, self.report.next_action, **changes),
            )
            with self.subTest(reason=reason):
                self.assertIs(gate.decision, EffectDecision.REFUSE)
                self.assertEqual(gate.reason, f"wrong_{reason}")

    def test_reduce_and_enforce_are_pure_and_side_effect_free(self) -> None:
        facts = parse_facts(raw_envelope())
        authority = adapter_authority(self.binding, self.report.next_action)
        with (
            mock.patch("builtins.open", side_effect=AssertionError("I/O forbidden")),
            mock.patch("subprocess.run", side_effect=AssertionError("process forbidden")),
        ):
            self.assertEqual(reduce_facts(facts), reduce_facts(facts))
            self.assertEqual(
                enforce_effect(self.report, authority),
                enforce_effect(self.report, authority),
            )


class EnumBoundaryTests(unittest.TestCase):
    def test_exact_enums_are_closed(self) -> None:
        self.assertEqual(
            {item.value for item in ActionKind},
            {
                "DISCOVER",
                "RECONCILE",
                "IMPLEMENT_BATCH",
                "VERIFY",
                "FOCUSED_REVIEW",
                "EXACT_FINAL",
                "ASK_USER",
                "FREEZE_CANDIDATE",
                "CLOSE",
                "REFUSE",
            },
        )
        self.assertEqual(
            {item.value for item in EffectDecision},
            {"ALLOW", "ASK_USER", "REFUSE"},
        )
        self.assertFalse(hasattr(semantic, "ProvenanceKind"))
        self.assertEqual({item.value for item in InfraKind}, {"REPLACED"})


class G008FactsOnlyRedTests(unittest.TestCase):
    def envelope(self) -> dict[str, object]:
        candidate = terminal_envelope()
        candidate["task_binding"]["repository_digest"] = HEX_B
        candidate["task_binding"]["outcome_digest"] = HEX_C
        candidate["facts"].pop("pending", None)
        candidate["facts"]["gates"][0]["family_id"] = "family-a"
        return candidate

    def test_pending_and_other_derived_action_inputs_reject(self) -> None:
        for field in ("pending", "action", "decision", "projection", "blocker"):
            for location in ("top", "facts", "gate"):
                candidate = raw_envelope()
                target = (
                    candidate
                    if location == "top"
                    else candidate["facts"]
                    if location == "facts"
                    else candidate["facts"]["gates"][0]
                )
                target[field] = []
                with self.subTest(field=field, location=location):
                    with self.assertRaisesRegex(SemanticError, "unknown"):
                        parse_facts(candidate)

    def test_repository_and_outcome_digests_bind_progress(self) -> None:
        baseline = self.envelope()
        first = make_progress_key(parse_facts(baseline))
        for field in ("repository_digest", "outcome_digest"):
            changed = copy.deepcopy(baseline)
            changed["task_binding"][field] = HEX_A
            with self.subTest(field=field):
                self.assertNotEqual(first, make_progress_key(parse_facts(changed)))

    def test_gate_facts_derive_the_complete_action(self) -> None:
        candidate = self.envelope()
        candidate["facts"]["gates"] = [
            {
                "id": "product_edit",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-a"],
            }
        ]
        action = reduce_facts(parse_facts(candidate)).next_action
        self.assertIs(action.kind, ActionKind.IMPLEMENT_BATCH)
        self.assertEqual(action.target, Id("action_target", "gate:product_edit"))
        self.assertEqual(action.scope, Id("action_scope", "family:family-a"))
        self.assertEqual(action.family, Id("family_id", "family-a"))
        self.assertEqual(action.falsifier, Id("falsifier", "gate:product_edit:open"))
        evidence_digest = sha256(
            b"happycodex/0.6/evidence-source\0"
            + canonical_bytes(("source-a",))
        ).hexdigest()
        self.assertEqual(
            action.evidence_source,
            Id("evidence_source", f"evidence:{evidence_digest}"),
        )

    def test_all_gate_mappings_order_unknown_and_referential_integrity(self) -> None:
        gate_map = (
            ("user_selection", ActionKind.ASK_USER),
            ("contract_freeze", ActionKind.VERIFY),
            ("red_oracle", ActionKind.VERIFY),
            ("product_edit", ActionKind.IMPLEMENT_BATCH),
            ("checks", ActionKind.VERIFY),
            ("family_hardening", ActionKind.IMPLEMENT_BATCH),
            ("boundary_repair", ActionKind.IMPLEMENT_BATCH),
            ("reconciliation", ActionKind.RECONCILE),
            ("focused_review", ActionKind.FOCUSED_REVIEW),
            ("candidate_freeze", ActionKind.FREEZE_CANDIDATE),
            ("exact_final_review", ActionKind.EXACT_FINAL),
            ("release", ActionKind.VERIFY),
        )
        for gate, expected in gate_map:
            candidate = self.envelope()
            candidate["facts"]["gates"] = [
                {
                    "id": gate,
                    "state": "OPEN",
                    "family_id": "family-a",
                    "evidence": ["source-a"],
                }
            ]
            with self.subTest(gate=gate):
                self.assertIs(
                    reduce_facts(parse_facts(candidate)).next_action.kind,
                    expected,
                )

        ordered = self.envelope()
        ordered["facts"]["gates"] = [
            {
                "id": "exact_final_review",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-a"],
            },
            {
                "id": "user_selection",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-b"],
            },
        ]
        reversed_input = copy.deepcopy(ordered)
        reversed_input["facts"]["gates"].reverse()
        self.assertEqual(
            reduce_facts(parse_facts(ordered)).next_action,
            reduce_facts(parse_facts(reversed_input)).next_action,
        )
        self.assertIs(
            reduce_facts(parse_facts(ordered)).next_action.kind,
            ActionKind.ASK_USER,
        )

        unknown = self.envelope()
        unknown["facts"]["gates"] = [
            {
                "id": "unknown_gate",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-a"],
            }
        ]
        self.assertIs(
            reduce_facts(parse_facts(unknown)).next_action.kind,
            ActionKind.RECONCILE,
        )
        for mutation, message in (
            ({"family_id": "missing-family"}, "family"),
            ({"evidence": []}, "evidence"),
        ):
            invalid = copy.deepcopy(unknown)
            invalid["facts"]["gates"][0].update(mutation)
            with self.subTest(mutation=mutation):
                with self.assertRaisesRegex(SemanticError, message):
                    parse_facts(invalid)

    def test_unresolved_state_preempts_downstream_and_family_boundary_discovers(
        self,
    ) -> None:
        failed_check = self.envelope()
        failed_check["facts"]["checks"][0]["state"] = "FAIL"
        failed_check["facts"]["gates"] = [
            {
                "id": "product_edit",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-a"],
            }
        ]
        self.assertNotIn(
            reduce_facts(parse_facts(failed_check)).next_action.kind,
            {
                ActionKind.IMPLEMENT_BATCH,
                ActionKind.FOCUSED_REVIEW,
                ActionKind.EXACT_FINAL,
                ActionKind.FREEZE_CANDIDATE,
            },
        )

        unresolved = self.envelope()
        unresolved["facts"]["findings"][0]["state"] = "UNKNOWN"
        unresolved["facts"]["gates"] = [
            {
                "id": "exact_final_review",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-a"],
            }
        ]
        self.assertIsNot(
            reduce_facts(parse_facts(unresolved)).next_action.kind,
            ActionKind.EXACT_FINAL,
        )

        boundary = self.envelope()
        boundary["facts"]["families"][0]["state"] = "BOUNDARY_REQUIRED"
        self.assertIs(
            reduce_facts(parse_facts(boundary)).next_action.kind,
            ActionKind.DISCOVER,
        )
        boundary["facts"]["gates"] = [
            {
                "id": "product_edit",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-a"],
            }
        ]
        self.assertIs(
            reduce_facts(parse_facts(boundary)).next_action.kind,
            ActionKind.DISCOVER,
        )

    def test_user_gate_preempts_unresolved_and_blocked_effect_gate_reconciles(
        self,
    ) -> None:
        user_gate = self.envelope()
        user_gate["facts"]["findings"][0]["state"] = "UNKNOWN"
        user_gate["facts"]["families"][0]["state"] = "OPEN"
        user_gate["facts"]["gates"] = [
            {
                "id": "user_selection",
                "state": "OPEN",
                "family_id": "family-a",
                "evidence": ["source-a"],
            }
        ]
        self.assertIs(
            reduce_facts(parse_facts(user_gate)).next_action.kind,
            ActionKind.ASK_USER,
        )

        blocked = self.envelope()
        blocked["facts"]["gates"] = [
            {
                "id": "product_edit",
                "state": "BLOCKED",
                "family_id": "family-a",
                "evidence": ["source-a"],
            }
        ]
        self.assertIs(
            reduce_facts(parse_facts(blocked)).next_action.kind,
            ActionKind.RECONCILE,
        )

    def test_unlinked_fact_uses_stable_task_family(self) -> None:
        candidate = self.envelope()
        candidate["facts"]["claims"][0]["state"] = "OPEN"
        action = reduce_facts(parse_facts(candidate)).next_action
        self.assertEqual(action.family, Id("family_id", "task:task-a"))
        self.assertEqual(action.scope, Id("action_scope", "family:task:task-a"))

    def test_forged_family_replay_rejects(self) -> None:
        report = reduce_facts(parse_facts(self.envelope()))
        forged = report.to_wire()
        forged["next_action"]["family_id"] = "forged-family"
        with self.assertRaisesRegex(SemanticError, "action mismatch"):
            replay_report(forged)

    def issue(
        self,
        report: ProgressReport,
        *,
        channel: str = "current_task_user",
        root_task: Id | None = None,
        source_task: Id | None = None,
        target_task: Id | None = None,
        executor_task: Id | None = None,
    ) -> AuthorityProvenance:
        binding = report.facts.task
        return _issue_authority(
            channel=channel,
            root_task=root_task or binding.root_task,
            source_task=source_task or binding.task,
            target_task=target_task or binding.task,
            executor_task=executor_task or binding.executor_task,
            destination=binding.destination,
            lineage=binding.lineage,
            message_id=Id("message", "message-a"),
            turn_id=Id("turn", "turn-a"),
            content_digest=Id("content", HEX_C),
            target=report.next_action.target,
            scope=report.next_action.scope,
        )

    def test_authority_kind_is_derived_and_decisions_bind_tasks(self) -> None:
        self.assertNotIn("kind", signature(_issue_authority).parameters)
        for field in (
            "channel",
            "root_task",
            "source_task",
            "target_task",
            "executor_task",
            "destination",
            "lineage",
            "message_id",
            "turn_id",
            "content_digest",
            "target",
            "scope",
        ):
            with self.subTest(field=field):
                self.assertIn(field, signature(_issue_authority).parameters)

        report = reduce_facts(parse_facts(self.envelope()))
        direct = self.issue(report)
        self.assertIs(
            enforce_effect(report, direct).decision,
            EffectDecision.ALLOW,
        )
        cross = self.issue(
            report,
            channel="cross_task_user_delegation",
            source_task=Id("task", "other-task"),
        )
        self.assertIs(
            enforce_effect(report, cross).decision,
            EffectDecision.ASK_USER,
        )
        wrong_executor = self.issue(
            report,
            executor_task=Id("executor_task", "other-executor"),
        )
        self.assertEqual(
            enforce_effect(report, wrong_executor).reason,
            "wrong_executor",
        )
        wrong_target = self.issue(
            report,
            source_task=Id("task", "other-task"),
            target_task=Id("task", "other-task"),
        )
        self.assertEqual(
            enforce_effect(report, wrong_target).reason,
            "wrong_target_task",
        )
        object.__setattr__(cross, "channel", "current_task_user")
        self.assertIs(
            enforce_effect(report, cross).decision,
            EffectDecision.REFUSE,
        )
        forged_kind = self.issue(report)
        object.__setattr__(forged_kind, "kind", cross.kind)
        self.assertIs(
            enforce_effect(report, forged_kind).decision,
            EffectDecision.REFUSE,
        )

        class Channel(str, Enum):
            DIRECT = "current_task_user"

        with self.assertRaisesRegex(SemanticError, "channel"):
            self.issue(report, channel=Channel.DIRECT)


if __name__ == "__main__":
    unittest.main()
