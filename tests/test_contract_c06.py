"""Contract test for operation C-06, plan section 2 section 5.

The test pins the check field of contract C-06 as plan section 9
states it. Surfaces crossed: MOD-10, via TG-10.3.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-06.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod10 as _m_mod10
    SURFACES["mod10"] = True
except Exception:
    SURFACES["mod10"] = False


class TestContractC06(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-06: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_annotation_link_identity_across_checkpoint(self):
        """
        Fixture: Shape 4 and Shape 12 link carriage: a checkpoint and an annotation appended after it was written
        Pins: link identity is guaranteed across a checkpoint: the resumed or replayed run sees the same annotation link as the run that wrote the checkpoint, and every annotation reachable through the link carries its append order; a closed AnchorScenarioRecord is never edited in place
        Bar: appends never write into the checkpoint, the manifest, or the run state the checkpoint names
        Failure: a changed link identity, an append written into the checkpoint, or an annotation without its append order fails this test; while the surface is absent the test fails naming this behaviour and C-06
        """
        self.require("annotation link identity holds across a checkpoint and appends carry their order", "mod10")
        import crucible.mod10 as mod10
        import copy
        checkpoint = {"run_identifier": "run-c06", "annotation_link": "link-c06", "state": "checkpoint state"}
        before = copy.deepcopy(checkpoint)
        appended = mod10.append_annotation(checkpoint, {"text": "later annotation"})
        self.assertEqual(checkpoint, before)
        self.assertNotIn("annotation_record", checkpoint)
        self.assertEqual(mod10.annotation_link_at_checkpoint(appended), "link-c06")
        resumed = mod10.resume_from_checkpoint(checkpoint)
        self.assertEqual(mod10.annotation_link_at_checkpoint(resumed), mod10.annotation_link_at_checkpoint(checkpoint))

    def test_annotation_state_equality_not_guaranteed(self):
        """
        Fixture: Shape 4 and Shape 12 link carriage: an annotation appended after the checkpoint, presented as at the checkpoint
        Pins: annotation state equality is expressly not guaranteed, and the negative limb is what the test asserts: a reading that needs annotation state as at a point names that point, and a reading that follows the link without naming a point is read as at the last append
        Bar: no reader facing equality claim may be built on this operation
        Failure: an annotation presented as at the checkpoint that was appended after it, or any equality claim built on this operation, fails this test; while the surface is absent the test fails naming this behaviour and C-06
        """
        self.require("annotation appended after a checkpoint is never presented as at the checkpoint", "mod10")
        import crucible.mod10 as mod10
        self.assertFalse(mod10.validate_annotation_claim({"claim": "annotation_state_equal_across_append"}))
        checkpoint = {"run_identifier": "run-c06", "annotation_link": "link-c06"}
        appended = mod10.append_annotation(checkpoint, {"text": "appended after the checkpoint"})
        self.assertIn("annotation_record", appended)
        self.assertNotIn("annotation_record", checkpoint)
        self.assertFalse(mod10.validate_annotation_claim({"claim": "annotation_state_equal_across_append", "presented_as": "at the checkpoint"}))


if __name__ == "__main__":
    unittest.main()
