"""Test group TG-05.4, slice S-05, MOD-06 Escrow Core.

Suite form: Python standard library unittest, one file per test group.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each test body first requires the product surface: while the surface
is absent the test fails, naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only. No real money stake
behaviour stands in any fixture, branch or variable in this file.
"""
import unittest

try:
    from crucible import mod06 as _mod
    SURFACE = True
    SURFACE_ERROR = ""
except Exception as exc:
    _mod = None
    SURFACE = False
    SURFACE_ERROR = str(exc)


class TestTG054(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-05.4: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_sham_variant_control_gated(self):
        """
        Fixture: F-11, the sham variant control. Recorded state: gated, never passed, until both records named in the Bar stand
        Pins: when the gate opens: the same rule text carried under both variant stamps, B-4 and B-3, over matched replicates; any difference the sham control shows is a fold or stamping effect, not a ruling effect, and is reported as such; the control is not a zero baseline
        Bar: the control is gated on two records standing first, the equivalence margin at NQ-49 fixed on the record, and the seam check under the duty at decision D-02 condition three read with D-20; until both stand, no sham result is reported and no ruling effect wording is used
        Failure: a sham result reported, or ruling effect wording used, before both records stand fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: TG-05.4 sham control gate: equivalence margin at NQ-49 fixed on the record, and the seam check under decision D-02 condition three read with D-20; neither record stands")

    def test_folding_duty_before_ruling_effect_wording(self):
        """
        Fixture: F-12, the B-5 matched comparison pair, at the core limb
        Pins: no B-5 difference is reported as a ruling effect until the folding is recorded ruling by ruling against the ruling text, with seam tests written against the ruling text and at least one seam case per ruling checked by a reader who did not perform that folding, per open point OP-21
        Bar: the ten ruling text gaps G-1 to G-10 stand filled by no inference; a seam test that supplies a gap value by inference fails this group
        Failure: a B-5 difference reported as a ruling effect with no folding record, or a seam case supplying a gap value by inference, fails this test; while the surface is absent the test fails naming this behaviour and TG-05.4
        """
        self.require_surface("no B-5 difference is reported as a ruling effect before the ruling by ruling folding record stands")
        shown = _mod.report_difference({"delta": 1})
        self.assertEqual(shown["reported_as"], "unfolded difference only")
        self.assertFalse(shown["ruling_effect_wording"])
        inferred = {"entries": [{
            "ruling": "DQ-1", "filled_by_inference": True,
            "checked_by_independent_reader": True}]}
        self.assertFalse(_mod.validate_folding_record(inferred))
        unchecked = {"entries": [{
            "ruling": "DQ-1", "checked_by_independent_reader": False}]}
        self.assertFalse(_mod.validate_folding_record(unchecked))
        folded = {"entries": [{
            "ruling": "DQ-1", "checked_by_independent_reader": True}]}
        self.assertTrue(_mod.validate_folding_record(folded))
        shown_folded = _mod.report_difference({"delta": 1}, folding_record=folded)
        self.assertTrue(shown_folded["ruling_effect_wording"])

    def test_unfolded_difference_is_not_a_ruling_effect(self):
        """
        Fixture: F-12, the B-5 matched comparison pair, at the core limb, unfolded limb
        Pins: a B-5 difference with no folding record behind it is reported as an unfolded difference only, in no ruling effect wording
        Bar: ruling effect wording with no folding record fails this group
        Failure: an unfolded difference worded as a ruling effect fails this test; while the surface is absent the test fails naming this behaviour and TG-05.4
        """
        self.require_surface("unfolded B-5 difference carries no ruling effect wording")
        shown = _mod.report_difference({"delta": 2}, folding_record=None)
        self.assertFalse(shown["ruling_effect_wording"])
        self.assertIn("unfolded", shown["reported_as"])
        self.assertEqual(_mod.ruling_text_gaps(), [
            "G-1", "G-2", "G-3", "G-4", "G-5",
            "G-6", "G-7", "G-8", "G-9", "G-10"])


if __name__ == "__main__":
    unittest.main()
