from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nautilus_protocol.projections import load_projection, validate_strategic, validate_tactical


class TacticalProjectionTests(unittest.TestCase):
    def setUp(self):
        self.document = load_projection(ROOT / "fixtures" / "tactical.valid.json")

    def test_valid_tactical_fixture(self):
        self.assertTrue(validate_tactical(self.document).valid)

    def test_tactical_requires_operational_source(self):
        changed = copy.deepcopy(self.document)
        changed["sourceSnapshots"] = []
        self.assertIn("Operational", " ".join(validate_tactical(changed).errors))

    def test_deliverables_reference_existing_evidence(self):
        changed = copy.deepcopy(self.document)
        changed["content"]["deliverables"][0]["evidenceIds"] = ["missing"]
        self.assertIn("unknown evidence", " ".join(validate_tactical(changed).errors))

    def test_tactical_accepts_optional_source_grounded_checkpoints(self):
        checkpoint = self.document["content"]["meaningCheckpoints"][0]
        self.assertEqual("provisional", checkpoint["state"])
        self.assertTrue(checkpoint["sourceReferences"])
        self.assertTrue(validate_tactical(self.document).valid)

    def test_tactical_rejects_invalid_checkpoint_state(self):
        changed = copy.deepcopy(self.document)
        changed["content"]["meaningCheckpoints"][0]["state"] = "invented"
        self.assertIn("state", " ".join(validate_tactical(changed).errors))

    def test_tactical_remains_compatible_without_checkpoints(self):
        changed = copy.deepcopy(self.document)
        changed["content"].pop("meaningCheckpoints")
        self.assertTrue(validate_tactical(changed).valid)


class StrategicProjectionTests(unittest.TestCase):
    def setUp(self):
        self.document = load_projection(ROOT / "fixtures" / "strategic.valid.json")

    def test_valid_strategic_fixture(self):
        self.assertTrue(validate_strategic(self.document).valid)

    def test_realizations_reference_existing_impacts(self):
        changed = copy.deepcopy(self.document)
        changed["content"]["realizations"][0]["impactIds"] = ["missing"]
        self.assertIn("unknown impacts", " ".join(validate_strategic(changed).errors))

    def test_value_lenses_are_both_required_and_source_grounded(self):
        changed = copy.deepcopy(self.document)
        changed["content"]["realizations"][0].pop("integrativeValue")
        errors = " ".join(validate_strategic(changed).errors)
        self.assertIn("integrativeValue", errors)

    def test_projection_cannot_claim_another_namespace(self):
        changed = copy.deepcopy(self.document)
        changed["namespace"] = "other-extension"
        self.assertIn("namespace", " ".join(validate_strategic(changed).errors))

    def test_strategic_accepts_consolidated_checkpoint_with_correction_boundary(self):
        checkpoint = self.document["content"]["meaningCheckpoints"][0]
        self.assertEqual("consolidated", checkpoint["state"])
        self.assertIn("without rewriting", checkpoint["correctionBoundary"])
        self.assertTrue(validate_strategic(self.document).valid)

    def test_checkpoint_rejects_unknown_fields_and_empty_sources(self):
        changed = copy.deepcopy(self.document)
        checkpoint = changed["content"]["meaningCheckpoints"][0]
        checkpoint["privateReasoning"] = "not publication evidence"
        checkpoint["sourceReferences"] = []
        errors = " ".join(validate_strategic(changed).errors)
        self.assertIn("unexpected field", errors)
        self.assertIn("sourceReferences", errors)

    def test_strategic_remains_compatible_without_checkpoints(self):
        changed = copy.deepcopy(self.document)
        changed["content"].pop("meaningCheckpoints")
        self.assertTrue(validate_strategic(changed).valid)


if __name__ == "__main__":
    unittest.main()
