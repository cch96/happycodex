from __future__ import annotations

from copy import deepcopy
import hashlib
import unittest

from evaluation.canonical import canonical_sha256
from evaluation.host import (
    construct_attestation, construct_release_receipt, external_boundary_notice,
)
from evaluation.identity import review_projection_from_git
from evaluation.manifest import (
    ManifestError, build_production_spec, qualified_evaluation_authority_request,
)
from evaluation.verify import (
    VerifyError, attestation_evidence_statement, external_trust_notice,
    release_evidence_statement, verify_effect_sequence,
)
from tests.attestation_fixtures import CommittedWorkspace, RecordFactory, reseal


class PureHostAdapterTests(unittest.TestCase):
    def test_attestation_constructor_round_trips_external_statement(self):
        factory = RecordFactory()
        record = factory.make_attestation("qualification-routing")
        rebuilt = construct_attestation(
            attestation_evidence_statement(record), record["evidence_binding"],
            response_schema=factory.schemas[record["unit_id"]],
            oracle=factory.oracles[record["unit_id"]],
            provider_input=factory.inputs[record["unit_id"]],
        )
        self.assertEqual(rebuilt, record)
        self.assertEqual(factory.authenticate(rebuilt).record, record)

    def test_release_constructor_round_trips_external_statement(self):
        factory = RecordFactory(); _, _, evaluation = factory.full_evaluation()
        receipt, _ = factory.release(evaluation)
        rebuilt = construct_release_receipt(
            release_evidence_statement(receipt), receipt["evidence_binding"],
        )
        self.assertEqual(rebuilt, receipt)

    def test_host_checks_digest_but_cannot_authenticate_signature(self):
        factory = RecordFactory()
        record = factory.make_attestation("qualification-routing")
        binding = deepcopy(record["evidence_binding"])
        binding["signature"] = "not-authenticated-by-host"
        rebuilt = construct_attestation(
            attestation_evidence_statement(record), binding,
            response_schema=factory.schemas[record["unit_id"]],
            oracle=factory.oracles[record["unit_id"]],
            provider_input=factory.inputs[record["unit_id"]],
        )
        with self.assertRaises(VerifyError):
            factory.authenticate(rebuilt)

    def test_host_and_verifier_notices_name_external_nonproofs(self):
        host_notice = external_boundary_notice().lower()
        verifier_notice = external_trust_notice().lower()
        for word in ("authority", "authenticate", "one-shot", "time", "readback"):
            self.assertIn(word, host_notice + verifier_notice)


class QualifiedProjectionRepairTests(unittest.TestCase):
    def test_tampered_readable_content_rejected_on_qualified_path(self):
        with CommittedWorkspace() as workspace:
            construction, _ = workspace.production_construction()
            projection = deepcopy(construction["review_projection"])
            entry = next(item for item in projection["candidate"]["entries"] if item["path"] == "AGENTS.md")
            entry["content"] = "ZmFrZQ=="
            entry["sha256"] = hashlib.sha256(b"fake").hexdigest()
            entry["size_bytes"] = 4
            snapshot = projection["candidate"]
            snapshot["snapshot_sha256"] = canonical_sha256({
                key: snapshot[key] for key in snapshot if key != "snapshot_sha256"
            })
            projection["changed_paths"] = ["AGENTS.md"]
            projection["candidate_snapshot_sha256"] = snapshot["snapshot_sha256"]
            projection["projection_sha256"] = canonical_sha256({
                key: projection[key] for key in projection if key != "projection_sha256"
            })
            construction["review_projection"] = projection
            spec = build_production_spec(**construction)
            with self.assertRaises(ManifestError):
                qualified_evaluation_authority_request(spec, **construction)

    def test_stale_source_commit_and_fake_diff_are_rejected_before_authority(self):
        with CommittedWorkspace() as workspace:
            path = workspace.root / "evaluation/README.md"
            path.write_text(path.read_text() + "\ncandidate\n", encoding="utf-8")
            workspace.commit()
            construction, _ = workspace.production_construction()
            stale = review_projection_from_git(
                workspace.root, baseline=workspace.baseline, candidate=workspace.baseline,
            )
            construction["review_projection"] = stale
            spec = build_production_spec(**construction)
            with self.assertRaises(ManifestError):
                qualified_evaluation_authority_request(spec, **construction)
        with CommittedWorkspace() as workspace:
            construction, _ = workspace.production_construction()
            projection = deepcopy(construction["review_projection"])
            projection["changed_paths"] = ["FAKE_DIFF.patch"]
            projection["projection_sha256"] = canonical_sha256({
                key: projection[key] for key in projection if key != "projection_sha256"
            })
            construction["review_projection"] = projection
            with self.assertRaises(Exception):
                build_production_spec(**construction)

    def test_dirty_source_built_after_drift_still_cannot_reach_authority(self):
        with CommittedWorkspace() as workspace:
            construction, _ = workspace.production_construction()
            path = workspace.root / "evaluation/oracle.py"
            path.write_text(path.read_text() + "\n# dirty before spec\n", encoding="utf-8")
            dirty_spec = build_production_spec(**construction)
            with self.assertRaisesRegex(ManifestError, "clean Git HEAD"):
                qualified_evaluation_authority_request(dirty_spec, **construction)


class RelationshipRepairTests(unittest.TestCase):
    def test_same_exact_effect_cannot_cross_spec_relationship(self):
        first = RecordFactory(absolute_wall=5000)
        second = RecordFactory(absolute_wall=6000)
        self.assertEqual(
            first.unit("exact-final")["effect_subject_sha256"],
            second.unit("exact-final")["effect_subject_sha256"],
        )
        record = first.make_attestation("exact-final")
        authenticated = first.authenticate(record)
        with self.assertRaisesRegex(VerifyError, "relationship"):
            verify_effect_sequence([authenticated], spec=second.spec, unit_id="exact-final")

    def test_assessment_and_binding_relabels_cannot_survive_reseal(self):
        for mutate in (
            lambda body: body["assessment"].__setitem__("passed", False),
            lambda body: body["claim"].__setitem__("report_sha256", "0" * 64),
            lambda body: body["observation"].__setitem__("raw_sha256", "1" * 64),
        ):
            factory = RecordFactory(); record = factory.make_attestation("qualification-routing")
            forged = reseal(record, mutate)
            with self.assertRaises(Exception):
                factory.authenticate(forged)


if __name__ == "__main__":
    unittest.main()
