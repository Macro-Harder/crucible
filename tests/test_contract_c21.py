"""Contract test for operation C-21, plan section 2 section 5.

The test pins the check field of contract C-21 as plan section 9
states it. Surfaces crossed: MOD-05, via TG-04.5.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-21.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod05 as _m_mod05
    SURFACES["mod05"] = True
except Exception:
    SURFACES["mod05"] = False


class TestContractC21(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-21: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_outcome_travels_with_its_accuracy_parameter(self):
        """
        Fixture: F-16, the arbiter accuracy point sets: one case record set scored at two accuracy points
        Pins: each outcome, slashable, not slashable, or a named no determination disposition, travels with the arbiter accuracy value applied, its assumption set and row reference, and the error direction named beside the value, in the symmetric split form or the directional pair form, with the component name, the set, the row, the value and its error direction in the run record; the ground truth label reference is held apart from the panel inputs
        Bar: the accuracy value may not be derived from panel size, band gates or fee size, and the four set ranges beside the points stand unmerged; a panel input set containing the label, or a field derived from it, fails in the same form as the canary failure at TG-09.3
        Failure: an outcome or accuracy value missing any carriage element, a derived from statement for the value, or merged set ranges fails this test; while the surface is absent the test fails naming this behaviour and C-21
        """
        self.require("adjudication outcome travels with its accuracy value, set, row and error direction", "mod05")
        import crucible.mod05 as mod05
        case = {"case_identifier": "case-c21", "ground_truth_label_reference": "label-ref apart"}
        first = mod05.adjudicate(case, accuracy_value=0.9, assumption_set="set-1", row="row-1", error_direction="symmetric split", outcome="slashable")
        for field in ("arbiter_accuracy_value", "assumption_set_identifier", "row_identifier", "error_direction"):
            self.assertIn(field, first)
        self.assertEqual(first["outcome"], "slashable")
        second = mod05.adjudicate(case, accuracy_value=0.7, assumption_set="set-1", row="row-2", error_direction="directional pair", outcome="not slashable")
        self.assertEqual(second["arbiter_accuracy_value"], 0.7)
        self.assertNotEqual(first["panel_inputs"], None)
        self.assertEqual(first["ground_truth_label_reference"], "label-ref apart")
        with self.assertRaises(ValueError):
            mod05.adjudicate(case, accuracy_value=0.9, assumption_set="set-1", row="row-1", error_direction="symmetric split", derived_from="panel size")
        self.assertTrue(mod05.accuracy_ranges_stand_unmerged(["r1", "r2", "r3", "r4"]))
        self.assertFalse(mod05.accuracy_ranges_stand_unmerged(["r1", "r2"]))

    def test_excluded_class_counts_and_forged_basis_bar(self):
        """
        Fixture: F-16 beside a run record inspected for its excluded adjudication class counts and shares
        Pins: the counts and shares for the four excluded classes stand in every run record, and a family record that fixes no excluded share threshold supports no headline adjudication claim
        Bar: no accuracy figure stands for the forged vouch basis class while NQ-56 stands open: where the adjacent arbitrated share for a forged vouch basis is above zero in a run a headline claim rests on, the claim fails validation while NQ-56 stands open
        Failure: a run record missing the excluded class counts, an accuracy figure for the forged vouch basis class, or a headline claim standing on an above zero adjacent share fails this test; while the surface is absent the test fails naming this behaviour and C-21
        """
        self.require("excluded class counts stand in every run record and no accuracy figure stands for the forged vouch basis class", "mod05")
        import crucible.mod05 as mod05
        cases = [{"excluded_class": mod05.EXCLUDED_CLASSES[0]}, {"excluded_class": mod05.EXCLUDED_CLASSES[0]}, {"excluded_class": mod05.EXCLUDED_CLASSES[1]}]
        counts = mod05.excluded_class_counts(cases)
        self.assertEqual(len(counts), 4)
        for name in mod05.EXCLUDED_CLASSES:
            self.assertIn("count", counts[name])
            self.assertIn("share", counts[name])
        self.assertEqual(counts[mod05.EXCLUDED_CLASSES[0]]["count"], 2)
        family = {"excluded_share_threshold": 0.9}
        forged_run = {"excluded_class_counts_and_shares": mod05.excluded_class_counts([{"excluded_class": mod05.FORGED_VOUCH_BASIS_CLASS}])}
        self.assertFalse(mod05.validate_headline_adjudication_claim(family, forged_run))
        self.assertFalse(mod05.validate_headline_adjudication_claim({}, forged_run))


if __name__ == "__main__":
    unittest.main()
