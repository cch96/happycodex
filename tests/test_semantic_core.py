from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from evaluation.semantic import (
    AdminFacts,
    Arm,
    AttemptKey,
    AttemptScope,
    AttemptTarget,
    BaselineAcceptance,
    CandidateIdentity,
    CapacityError,
    CheckFact,
    CheckId,
    CheckState,
    ClaimFact,
    ClaimId,
    ClaimState,
    CompletionTag,
    ControlBlocker,
    Decision,
    DecisionTarget,
    DecisionTargetId,
    DigestAnchor,
    EvidenceKind,
    EvidenceRef,
    EvidenceSourceId,
    ExecutorIdentity,
    FalsifierId,
    Finding,
    FindingCatalog,
    FindingId,
    FindingStatus,
    GateFact,
    GateId,
    GateState,
    GateWorkId,
    GitCommit,
    GitTree,
    GoalFact,
    GoalState,
    InfrastructureId,
    InfrastructureTransition,
    InfrastructureTransitionKind,
    InvocationProfileIdentity,
    MachineEnvelope,
    Marker,
    MarkerId,
    ModelObservation,
    ReceiptAnchor,
    ReceiptKind,
    ReceiptLink,
    ReceiptLinkHash,
    RepoPath,
    RepositoryId,
    ResolutionEvidence,
    ResourceClaim,
    ResourceId,
    SafeText,
    SemanticValidationError,
    Sha256,
    SourceIdentity,
    StateKey,
    StateProjection,
    canonical_bytes,
    canonical_set,
    canonical_sha256,
    freeze_mapping,
    make_attempt_key,
    make_receipt_link_hash,
    make_state_key,
    parse_model_observation,
    parse_repo_path,
)


HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
GIT_A = "a" * 40
GIT_B = "b" * 40


class TypedStateTests(unittest.TestCase):
    def evidence(
        self,
        identity: str = HEX_A,
        *,
        source: str = "source-main",
        kind: EvidenceKind = EvidenceKind.SOURCE,
    ) -> EvidenceRef:
        return EvidenceRef(kind, Sha256(identity), EvidenceSourceId(source))

    def finding(
        self,
        *,
        status: FindingStatus = FindingStatus.OPEN,
        claim_text: str = "typed progress exists",
        falsifier_text: str = "an equivalent attempt is repeated",
        claim_id: str = "claim-progress",
        falsifier_id: str = "falsifier-repeat",
        evidence: tuple[EvidenceRef, ...] = (),
        anchors: tuple[object, ...] | None = None,
    ) -> Finding:
        if anchors is None:
            anchors = (Marker(MarkerId("semantic-core")),)
        return Finding.proposed(
            finding_id=FindingId("finding-progress"),
            claim_id=ClaimId(claim_id),
            falsifier_id=FalsifierId(falsifier_id),
            status=status,
            anchors=anchors,
            claim_text=SafeText(claim_text),
            falsifier_text=SafeText(falsifier_text),
            evidence=evidence,
        )

    def projection(self, **changes: object) -> StateProjection:
        source = SourceIdentity(
            commit=GitCommit(GIT_A),
            tree=GitTree(GIT_B),
            package_semantic=Sha256(HEX_A),
            package_artifact=Sha256(HEX_B),
            engine_manifest=Sha256(HEX_C),
            config=Sha256("d" * 64),
        )
        executor = ExecutorIdentity(
            provider="codex",
            session="session-fixed",
            thread="thread-fixed",
            owner="executor-fixed",
            role_config=Sha256("e" * 64),
            actual_profile=Sha256("f" * 64),
            permission_profile=Sha256("1" * 64),
            write_scope=Sha256("2" * 64),
        )
        profile = InvocationProfileIdentity(
            provider="codex",
            binary=Sha256("3" * 64),
            model="gpt-5.6-sol",
            effort="high",
            timeout_seconds=600,
            tool_surface=Sha256("4" * 64),
            network=False,
            mcp=Sha256("5" * 64),
            hooks=Sha256("6" * 64),
            settings=Sha256("7" * 64),
        )
        values: dict[str, object] = {
            "schema_generation": 6,
            "source": source,
            "candidate": None,
            "executor": executor,
            "invocation_profile": profile,
            "claimed_resources": (
                ResourceClaim(ResourceId("ledger"), Sha256("8" * 64)),
            ),
            "claims": (
                ClaimFact(
                    ClaimId("claim-progress"),
                    "outcome",
                    ClaimState.OPEN,
                    (Marker(MarkerId("claim-anchor")),),
                    (),
                ),
            ),
            "goal": GoalFact(GoalState.NONE, None, True),
            "gates": (
                GateFact(
                    GateId.IMPLEMENTATION,
                    GateState.OPEN,
                    GateWorkId("i-01"),
                    (),
                ),
            ),
            "checks": (
                CheckFact(
                    CheckId("typed-state-red"),
                    Sha256("9" * 64),
                    CheckState.FAIL,
                    None,
                    self.evidence("0" * 64, kind=EvidenceKind.CHECK),
                ),
            ),
            "accepted_evidence": (self.evidence(),),
            "infrastructure_replacements": (),
            "findings": (self.finding(),),
            "blockers": (
                ControlBlocker(
                    "implementation-open",
                    GateId.IMPLEMENTATION,
                    FindingId("finding-progress"),
                    (Marker(MarkerId("blocker-anchor")),),
                ),
            ),
            "decision_target": DecisionTarget(
                Decision.IMPLEMENT_BATCH,
                DecisionTargetId("i-01"),
                AttemptScope("semantic-core"),
            ),
        }
        values.update(changes)
        return StateProjection(**values)

    def envelope(self, projection: StateProjection | None = None, **admin: object) -> MachineEnvelope:
        facts = {
            "authority_receipts": (),
            "approval_receipts": (),
            "grant_lifecycle": (),
            "receipt_lifecycle": (),
            "receipt_head": None,
            "cursor": None,
            "consumed_attempts": (),
            "timestamps": (),
            "turn_ids": (),
            "random_ids": (),
        }
        facts.update(admin)
        return MachineEnvelope(projection or self.projection(), AdminFacts(**facts))

    def test_tagged_scalars_are_validated_and_not_cross_type_equal(self) -> None:
        self.assertNotEqual(FindingId("same"), ClaimId("same"))
        self.assertNotEqual(ClaimId("same"), FalsifierId("same"))
        self.assertNotEqual(FalsifierId("same"), EvidenceSourceId("same"))
        for factory, bad in (
            (FindingId, ""),
            (ClaimId, " leading"),
            (FalsifierId, "trailing "),
            (EvidenceSourceId, "UPPER_CASE"),
            (Sha256, "A" * 64),
            (Sha256, "a" * 63),
            (GitCommit, "a" * 39),
            (GitTree, "g" * 40),
        ):
            with self.subTest(factory=factory.__name__, bad=bad):
                with self.assertRaises(SemanticValidationError):
                    factory(bad)

    def test_repo_path_is_exact_relative_case_sensitive_and_unaliased(self) -> None:
        upper = RepoPath(RepositoryId("repo-main"), "Src/Thing.py")
        lower = RepoPath(RepositoryId("repo-main"), "src/Thing.py")
        self.assertNotEqual(upper, lower)
        for path in (
            "/absolute",
            "../escape",
            "a/../b",
            "a/./b",
            "a//b",
            "a\\b",
            "a/",
            ".",
            "",
        ):
            with self.subTest(path=path):
                with self.assertRaises(SemanticValidationError):
                    RepoPath(RepositoryId("repo-main"), path)

        parsed = parse_repo_path(
            {"tag": "RepoPath", "repository_id": "repo-main", "path": "Src/Thing.py"}
        )
        self.assertEqual(parsed, upper)
        for malformed in (
            {"tag": "repo_path", "repository_id": "repo-main", "path": "x"},
            {"tag": "RepoPath", "repository_id": "repo-main", "path": "x", "extra": 1},
            {"tag": "RepoPath", "repository_id": "repo-main"},
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaises(SemanticValidationError):
                    parse_repo_path(malformed)

    def test_frozen_records_tuples_and_mappings_cannot_mutate(self) -> None:
        finding = self.finding()
        with self.assertRaises(FrozenInstanceError):
            finding.status = FindingStatus.RESOLVED  # type: ignore[misc]
        frozen = freeze_mapping({"b": 2, "a": 1})
        self.assertEqual(tuple(frozen), ("a", "b"))
        with self.assertRaises(TypeError):
            frozen["c"] = 3  # type: ignore[index]
        projection = self.projection()
        self.assertIsInstance(projection.findings, tuple)

    def test_canonical_encoding_is_exact_ordered_and_fail_closed(self) -> None:
        self.assertEqual(canonical_bytes({"b": 2, "a": 1}), b'{"a":1,"b":2}')
        self.assertNotEqual(canonical_bytes(("a", "b")), canonical_bytes(("b", "a")))
        self.assertEqual(
            canonical_set((ClaimId("b"), ClaimId("a"))),
            (ClaimId("a"), ClaimId("b")),
        )
        with self.assertRaisesRegex(SemanticValidationError, "duplicate"):
            canonical_set((ClaimId("a"), ClaimId("a")))
        self.assertEqual(canonical_bytes(True), b"true")
        self.assertEqual(canonical_bytes(False), b"false")
        for value in (float("nan"), 1.0, float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(SemanticValidationError):
                    canonical_bytes(value)
        self.assertNotEqual(
            canonical_sha256("domain-a", {"x": 1}),
            canonical_sha256("domain-b", {"x": 1}),
        )

    def test_unknown_enum_and_bool_as_int_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            Decision("implement_batch")
        with self.assertRaises(ValueError):
            GateState("open")
        with self.assertRaises(SemanticValidationError):
            StateProjection(**{**self.projection().__dict__, "schema_generation": True})
        with self.assertRaises(SemanticValidationError):
            InvocationProfileIdentity(
                provider="codex",
                binary=Sha256(HEX_A),
                model="model",
                effort="high",
                timeout_seconds=True,
                tool_surface=Sha256(HEX_B),
                network=False,
                mcp=Sha256(HEX_C),
                hooks=Sha256("d" * 64),
                settings=Sha256("e" * 64),
            )

    def test_finding_semantic_identity_ignores_display_rewording(self) -> None:
        first = self.finding()
        second = self.finding(
            claim_text="cosmetically rewritten claim",
            falsifier_text="cosmetically rewritten falsifier",
        )
        self.assertEqual(first.semantic_identity(), second.semantic_identity())
        self.assertEqual(
            make_state_key(self.projection(findings=(first,))),
            make_state_key(self.projection(findings=(second,))),
        )

    def test_finding_semantic_identity_changes_for_typed_semantics(self) -> None:
        base = self.finding()
        variants = (
            self.finding(claim_id="claim-other"),
            self.finding(falsifier_id="falsifier-other"),
            self.finding(anchors=(Marker(MarkerId("other-anchor")),)),
            self.finding(evidence=(self.evidence(HEX_B),)),
        )
        for variant in variants:
            with self.subTest(variant=variant):
                self.assertNotEqual(base.semantic_identity(), variant.semantic_identity())

        resolved = Finding.resolved(
            finding_id=base.finding_id,
            claim_id=base.claim_id,
            falsifier_id=base.falsifier_id,
            anchors=base.anchors,
            claim_text=base.claim_text,
            falsifier_text=base.falsifier_text,
            evidence=(self.evidence(HEX_B),),
            resolution=ResolutionEvidence(self.evidence(HEX_B, kind=EvidenceKind.CHECK)),
        )
        self.assertNotEqual(base.semantic_identity(), resolved.semantic_identity())

    def test_finding_resolution_and_baseline_acceptance_require_typed_proof(self) -> None:
        base = self.finding()
        with self.assertRaises(SemanticValidationError):
            Finding(
                base.finding_id,
                base.claim_id,
                base.falsifier_id,
                FindingStatus.RESOLVED,
                base.anchors,
                base.claim_text,
                base.falsifier_text,
                (),
            )
        with self.assertRaises(SemanticValidationError):
            Finding(
                base.finding_id,
                base.claim_id,
                base.falsifier_id,
                FindingStatus.BASELINE_ACCEPTED,
                base.anchors,
                base.claim_text,
                base.falsifier_text,
                (),
            )
        accepted = Finding.baseline_accepted(
            finding_id=base.finding_id,
            claim_id=base.claim_id,
            falsifier_id=base.falsifier_id,
            anchors=base.anchors,
            claim_text=base.claim_text,
            falsifier_text=base.falsifier_text,
            evidence=(self.evidence(HEX_C),),
            acceptance=BaselineAcceptance(
                authority=self.evidence(HEX_B, kind=EvidenceKind.AUTHORITY),
                baseline=Sha256(HEX_C),
            ),
        )
        self.assertEqual(accepted.status, FindingStatus.BASELINE_ACCEPTED)

    def test_model_observation_accepts_only_new_open_or_unknown_catalog_entries(self) -> None:
        catalog = FindingCatalog(
            namespace="semantic-core",
            existing_finding_ids=(FindingId("existing-finding"),),
            claim_ids=(ClaimId("claim-progress"),),
            falsifier_ids=(FalsifierId("falsifier-repeat"),),
        )
        raw = {
            "observations": ["bounded observation"],
            "proposed_findings": [
                {
                    "tag": "Finding",
                    "finding_id": "finding-progress",
                    "claim_id": "claim-progress",
                    "falsifier_id": "falsifier-repeat",
                    "status": "OPEN",
                    "anchors": [
                        {"tag": "Marker", "marker_id": "semantic-core"}
                    ],
                    "claim_text": "typed progress exists",
                    "falsifier_text": "equivalent work repeats",
                    "evidence": [],
                }
            ],
        }
        parsed = parse_model_observation(raw, catalog=catalog)
        self.assertIsInstance(parsed, ModelObservation)
        self.assertEqual(parsed.proposed_findings[0].status, FindingStatus.OPEN)
        for status in ("RESOLVED", "BASELINE_ACCEPTED"):
            malformed = {**raw, "proposed_findings": [{**raw["proposed_findings"][0], "status": status}]}
            with self.subTest(status=status):
                with self.assertRaises(SemanticValidationError):
                    parse_model_observation(malformed, catalog=catalog)
        for key, value in (
            ("finding_id", "existing-finding"),
            ("claim_id", "claim-outside-catalog"),
            ("falsifier_id", "falsifier-outside-catalog"),
        ):
            malformed = {**raw, "proposed_findings": [{**raw["proposed_findings"][0], key: value}]}
            with self.subTest(key=key):
                with self.assertRaises(SemanticValidationError):
                    parse_model_observation(malformed, catalog=catalog)
        with self.assertRaises(SemanticValidationError):
            parse_model_observation({**raw, "decision": "CLOSE"}, catalog=catalog)

    def test_state_key_ignores_all_administrative_lifecycle_fields(self) -> None:
        baseline = make_state_key(self.envelope())
        variants = (
            self.envelope(authority_receipts=(Sha256(HEX_A),)),
            self.envelope(approval_receipts=(Sha256(HEX_B),)),
            self.envelope(grant_lifecycle=("GRANTED", "RECEIPTED")),
            self.envelope(receipt_lifecycle=("intent", "receipt")),
            self.envelope(receipt_head=ReceiptLinkHash(HEX_A)),
            self.envelope(cursor="object:12/20"),
            self.envelope(consumed_attempts=(AttemptKey(HEX_B),)),
            self.envelope(timestamps=("2026-07-29T13:00:00Z",)),
            self.envelope(turn_ids=("turn-random",)),
            self.envelope(random_ids=("attempt-random",)),
        )
        for variant in variants:
            with self.subTest(admin=variant.admin):
                self.assertEqual(baseline, make_state_key(variant))

    def test_state_key_changes_for_each_semantic_projection_dimension(self) -> None:
        base = self.projection()
        base_key = make_state_key(base)
        candidate = CandidateIdentity(
            commit=GitCommit("c" * 40),
            tree=GitTree("d" * 40),
            package_semantic=base.source.package_semantic,
            package_artifact=base.source.package_artifact,
            engine_manifest=base.source.engine_manifest,
            config=base.source.config,
            snapshot=Sha256("e" * 64),
        )
        replacement = InfrastructureTransition(
            InfrastructureTransitionKind.REPLACED,
            InfrastructureId("runner"),
            Sha256(HEX_A),
            Sha256(HEX_B),
            (self.evidence(HEX_C, kind=EvidenceKind.RECOVERY),),
        )
        variants = {
            "candidate": replace(base, candidate=candidate),
            "check": replace(
                base,
                checks=(replace(base.checks[0], state=CheckState.PASS),),
            ),
            "goal": replace(base, goal=GoalFact(GoalState.ACTIVE, Sha256(HEX_A), True)),
            "gate": replace(
                base,
                gates=(replace(base.gates[0], state=GateState.SATISFIED),),
            ),
            "decision_target": replace(
                base,
                decision_target=DecisionTarget(
                    Decision.VERIFY,
                    DecisionTargetId("typed-state-check"),
                    AttemptScope("semantic-core"),
                ),
            ),
            "replacement": replace(base, infrastructure_replacements=(replacement,)),
            "finding_status": replace(
                base,
                findings=(
                    Finding.resolved(
                        finding_id=base.findings[0].finding_id,
                        claim_id=base.findings[0].claim_id,
                        falsifier_id=base.findings[0].falsifier_id,
                        anchors=base.findings[0].anchors,
                        claim_text=base.findings[0].claim_text,
                        falsifier_text=base.findings[0].falsifier_text,
                        evidence=(self.evidence(HEX_B),),
                        resolution=ResolutionEvidence(
                            self.evidence(HEX_B, kind=EvidenceKind.CHECK)
                        ),
                    ),
                ),
            ),
            "finding_anchor": replace(
                base,
                findings=(self.finding(anchors=(Marker(MarkerId("changed")),)),),
            ),
            "finding_evidence": replace(
                base,
                findings=(self.finding(evidence=(self.evidence(HEX_B),)),),
            ),
            "accepted_evidence": replace(
                base,
                accepted_evidence=(self.evidence(HEX_B),),
            ),
        }
        for name, variant in variants.items():
            with self.subTest(name=name):
                self.assertNotEqual(base_key, make_state_key(variant))

    def test_transient_infrastructure_events_do_not_enter_state_projection(self) -> None:
        for kind in (
            InfrastructureTransitionKind.STARTED,
            InfrastructureTransitionKind.FAILED,
            InfrastructureTransitionKind.RECOVERED,
        ):
            with self.subTest(kind=kind):
                with self.assertRaises(SemanticValidationError):
                    StateProjection(
                        **{
                            **self.projection().__dict__,
                            "infrastructure_replacements": (
                                InfrastructureTransition(
                                    kind,
                                    InfrastructureId("runner"),
                                    Sha256(HEX_A),
                                    Sha256(HEX_B),
                                    (),
                                ),
                            ),
                        }
                    )

    def test_attempt_key_uses_only_typed_preimage(self) -> None:
        state_key = make_state_key(self.envelope())
        base = make_attempt_key(
            state_key,
            Decision.VERIFY,
            AttemptTarget(DecisionTargetId("typed-state-check")),
            AttemptScope("semantic-core"),
            FalsifierId("falsifier-repeat"),
            EvidenceSourceId("source-main"),
        )
        reworded = make_attempt_key(
            make_state_key(
                self.envelope(
                    replace(
                        self.projection(),
                        findings=(
                            self.finding(
                                claim_text="display rewrite",
                                falsifier_text="another display rewrite",
                            ),
                        ),
                    ),
                    random_ids=("different",),
                    turn_ids=("turn-2",),
                )
            ),
            Decision.VERIFY,
            AttemptTarget(DecisionTargetId("typed-state-check")),
            AttemptScope("semantic-core"),
            FalsifierId("falsifier-repeat"),
            EvidenceSourceId("source-main"),
        )
        self.assertEqual(base, reworded)
        variants = (
            make_attempt_key(
                state_key,
                Decision.IMPLEMENT_BATCH,
                AttemptTarget(DecisionTargetId("typed-state-check")),
                AttemptScope("semantic-core"),
                FalsifierId("falsifier-repeat"),
                EvidenceSourceId("source-main"),
            ),
            make_attempt_key(
                state_key,
                Decision.VERIFY,
                AttemptTarget(DecisionTargetId("other-target")),
                AttemptScope("semantic-core"),
                FalsifierId("falsifier-repeat"),
                EvidenceSourceId("source-main"),
            ),
            make_attempt_key(
                state_key,
                Decision.VERIFY,
                AttemptTarget(DecisionTargetId("typed-state-check")),
                AttemptScope("other-scope"),
                FalsifierId("other-falsifier"),
                EvidenceSourceId("other-source"),
            ),
        )
        for variant in variants:
            self.assertNotEqual(base, variant)

    def test_receipt_link_validates_sequence_and_never_feeds_state_key(self) -> None:
        state_key = make_state_key(self.envelope())
        attempt = make_attempt_key(
            state_key,
            Decision.VERIFY,
            AttemptTarget(DecisionTargetId("typed-state-check")),
            AttemptScope("semantic-core"),
            FalsifierId("falsifier-repeat"),
            EvidenceSourceId("source-main"),
        )
        genesis = ReceiptLink(0, None, Sha256(HEX_A), attempt, EvidenceKind.CHECK)
        genesis_hash = make_receipt_link_hash(genesis)
        next_link = ReceiptLink(1, genesis_hash, Sha256(HEX_B), attempt, EvidenceKind.CHECK)
        self.assertNotEqual(genesis_hash, make_receipt_link_hash(next_link))
        with self.assertRaises(SemanticValidationError):
            ReceiptLink(True, None, Sha256(HEX_A), attempt, EvidenceKind.CHECK)
        with self.assertRaises(SemanticValidationError):
            ReceiptLink(1, None, Sha256(HEX_A), attempt, EvidenceKind.CHECK)
        with self.assertRaises(SemanticValidationError):
            ReceiptLink(0, ReceiptLinkHash(HEX_A), Sha256(HEX_A), attempt, EvidenceKind.CHECK)
        self.assertEqual(
            state_key,
            make_state_key(self.envelope(receipt_head=make_receipt_link_hash(next_link))),
        )

    def test_capacity_overflow_rejects_without_truncation_or_eviction(self) -> None:
        with self.assertRaises(CapacityError) as raised:
            canonical_set(
                (ClaimId("a"), ClaimId("b"), ClaimId("c")),
                max_items=2,
            )
        self.assertEqual(raised.exception.limit, 2)
        self.assertEqual(raised.exception.actual, 3)

    def test_anchor_union_is_exact_and_case_sensitive(self) -> None:
        anchors = (
            RepoPath(RepositoryId("repo-main"), "Src/Thing.py"),
            Marker(MarkerId("marker")),
            DigestAnchor("config", Sha256(HEX_A)),
            ReceiptAnchor(ReceiptKind("check"), Sha256(HEX_B)),
        )
        finding = self.finding(anchors=anchors)
        self.assertEqual(len(finding.anchors), 4)
        self.assertNotEqual(
            finding.semantic_identity(),
            self.finding(
                anchors=(
                    RepoPath(RepositoryId("repo-main"), "src/Thing.py"),
                    *anchors[1:],
                )
            ).semantic_identity(),
        )

    def test_supporting_enums_are_exact(self) -> None:
        self.assertEqual(Arm.CANDIDATE.value, "CANDIDATE")
        self.assertEqual(CompletionTag.COMPLETE.value, "COMPLETE")
        self.assertEqual(GateId.CANDIDATE_FREEZE.value, "CANDIDATE_FREEZE")
        self.assertEqual(EvidenceKind.OFFLINE_SUMMARY.value, "OFFLINE_SUMMARY")
        with self.assertRaises(ValueError):
            CompletionTag("complete")


if __name__ == "__main__":
    unittest.main()
