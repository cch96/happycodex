from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError
from enum import Enum
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
    ProvenanceKind,
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
        },
        "facts": {
            "claims": [{"id": "claim-a", "state": "OPEN", "evidence": ["source-a"]}],
            "findings": [
                {"id": "finding-a", "state": "OPEN", "evidence": ["source-a"]}
            ],
            "gates": [{"id": "gate-a", "state": "OPEN", "evidence": ["source-a"]}],
            "checks": [{"id": "check-a", "state": "PASS", "evidence": ["source-a"]}],
            "families": [
                {"id": "family-a", "state": "OPEN", "evidence": ["source-a"]}
            ],
            "pending": [
                {
                    "id": "pending-a",
                    "priority": 10,
                    "kind": "IMPLEMENT_BATCH",
                    "target": "kernel",
                    "scope": "batch-1",
                    "falsifier_id": "falsifier-a",
                    "evidence_source_id": "source-a",
                }
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
    candidate["facts"]["pending"] = []
    return candidate


def adapter_authority(
    binding: TaskBinding,
    action: object,
    *,
    kind: ProvenanceKind = ProvenanceKind.DIRECT,
    issuer: Id | None = None,
    destination: Id | None = None,
    lineage: Id | None = None,
    target: Id | None = None,
    scope: Id | None = None,
) -> AuthorityProvenance:
    return _issue_authority(
        kind=kind,
        issuer=issuer or binding.root_task,
        destination=destination or binding.destination,
        lineage=lineage or binding.lineage,
        source_event=Id("source_event", HEX_C),
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
                "ProvenanceKind",
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
            AuthorityProvenance(
                ProvenanceKind.DIRECT,
                binding.root_task,
                binding.destination,
                binding.lineage,
                Id("source_event", HEX_C),
                report.next_action.target,
                report.next_action.scope,
                True,
            )

    def test_caller_supplied_report_action_cannot_reach_attempt_key(self) -> None:
        facts = parse_facts(raw_envelope())
        action = NextAction(
            ActionKind.CLOSE,
            Id("action_target", "forged-target"),
            Id("action_scope", "forged-scope"),
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

    def test_parser_enforces_exact_states_and_tagged_pending_values(self) -> None:
        for domain in ("checks", "claims", "families", "findings", "gates"):
            candidate = raw_envelope()
            candidate["facts"][domain][0]["state"] = "ARBITRARY"
            with self.subTest(domain=domain):
                with self.assertRaisesRegex(SemanticError, f"{domain}.*state"):
                    parse_facts(candidate)

        facts = parse_facts(raw_envelope())
        pending = facts.stable["pending"][0].payload
        for field, tag in (
            ("target", "action_target"),
            ("scope", "action_scope"),
            ("falsifier_id", "falsifier"),
            ("evidence_source_id", "evidence_source"),
        ):
            with self.subTest(field=field):
                self.assertIs(type(pending[field]), Id)
                self.assertEqual(pending[field].tag, tag)

    def test_open_state_without_pending_reconciles(self) -> None:
        for domain, unresolved_state in (
            ("checks", "PENDING"),
            ("claims", "OPEN"),
            ("findings", "OPEN"),
            ("families", "OPEN"),
            ("gates", "OPEN"),
        ):
            candidate = terminal_envelope()
            candidate["facts"][domain][0]["state"] = unresolved_state
            report = reduce_facts(parse_facts(candidate))
            with self.subTest(domain=domain):
                self.assertIs(
                    report.next_action.kind,
                    ActionKind.RECONCILE,
                    f"open {domain} without pending must not produce CLOSE",
                )
                self.assertEqual(
                    report.next_action.scope,
                    Id("action_scope", domain),
                )

    def test_open_state_with_pending_close_reconciles(self) -> None:
        candidate = terminal_envelope()
        candidate["facts"]["claims"][0]["state"] = "OPEN"
        candidate["facts"]["pending"] = [
            {
                "id": "pending-close",
                "priority": 0,
                "kind": "CLOSE",
                "target": "task-a",
                "scope": "task",
                "falsifier_id": "all-terminal",
                "evidence_source_id": "facts",
            }
        ]
        report = reduce_facts(parse_facts(candidate))
        self.assertIs(report.next_action.kind, ActionKind.RECONCILE)
        self.assertEqual(report.next_action.scope, Id("action_scope", "claims"))

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
        changed["facts"]["pending"][0]["falsifier_id"] = "falsifier-b"
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

    def test_legitimate_delegation_asks_user(self) -> None:
        gate = enforce_effect(
            self.report,
            adapter_authority(
                self.binding,
                self.report.next_action,
                kind=ProvenanceKind.DELEGATED,
            ),
        )
        self.assertIs(gate.decision, EffectDecision.ASK_USER)

    def test_missing_and_spoofed_authority_refuse(self) -> None:
        self.assertIs(
            enforce_effect(self.report, None).decision,
            EffectDecision.REFUSE,
        )
        spoofed = object.__new__(AuthorityProvenance)
        for name, value in (
            ("kind", ProvenanceKind.DIRECT),
            ("issuer", self.binding.root_task),
            ("destination", self.binding.destination),
            ("lineage", self.binding.lineage),
            ("source_event", Id("source_event", HEX_C)),
            ("target", self.report.next_action.target),
            ("scope", self.report.next_action.scope),
        ):
            object.__setattr__(spoofed, name, value)
        gate = enforce_effect(self.report, spoofed)
        self.assertIs(gate.decision, EffectDecision.REFUSE)
        self.assertEqual(gate.reason, "spoofed")

    def test_wrong_issuer_destination_lineage_target_or_scope_refuses(self) -> None:
        variants = {
            "issuer": {"issuer": Id("root_task", "root-other")},
            "destination": {"destination": Id("destination", "destination-other")},
            "lineage": {"lineage": Id("lineage", HEX_C)},
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
        self.assertEqual(
            {item.value for item in ProvenanceKind},
            {"DIRECT", "DELEGATED"},
        )
        self.assertEqual({item.value for item in InfraKind}, {"REPLACED"})


if __name__ == "__main__":
    unittest.main()
