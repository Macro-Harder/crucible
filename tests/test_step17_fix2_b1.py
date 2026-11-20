"""Step 17 fix wave 2, Builder 1 tests.

Row FW-32 (Low, T17-37), the mod12 limb of filing B2-03 alone:
the top_up_applies door of crucible.mod12. Each defect test
reproduces the filing defect on the base tree at product head
afca4cad2ee8927784159819a4e25736f2bbbdaa, where a probability
standing in no finite form or outside the closed range from
zero to one silently answers False, and passes on the cured
tree, where the door refuses those handings in the named form
of the cured mod11 sibling door. Control tests pin the
standings that already hold, and the non numeric refusal test
pins the door standing refusal in its current form so the
cure cannot widen, narrow, or reword it in silence.
"""
import unittest

import crucible.mod12 as mod12


class TestFW32Mod12TopUpApplies(unittest.TestCase):
    def test_defect_above_one_refused_outside_range_form(self):
        for handing in (1.5, 5.0):
            with self.assertRaises(
                    mod12.NamedControllerFailure) as caught:
                mod12.top_up_applies(handing, 30)
            self.assertIn(
                "top_up_applies stands refused",
                str(caught.exception))
            self.assertIn(
                "outside the closed range from zero to one",
                str(caught.exception))

    def test_defect_below_zero_refused_outside_range_form(self):
        with self.assertRaises(
                mod12.NamedControllerFailure) as caught:
            mod12.top_up_applies(-0.5, 30)
        self.assertIn(
            "top_up_applies stands refused", str(caught.exception))
        self.assertIn(
            "outside the closed range from zero to one",
            str(caught.exception))

    def test_defect_nan_refused_no_finite_form(self):
        with self.assertRaises(
                mod12.NamedControllerFailure) as caught:
            mod12.top_up_applies(float("nan"), 30)
        self.assertIn(
            "top_up_applies stands refused", str(caught.exception))
        self.assertIn(
            "stands in no finite form", str(caught.exception))

    def test_defect_infinite_refused_no_finite_form(self):
        for handing in (float("inf"), float("-inf")):
            with self.assertRaises(
                    mod12.NamedControllerFailure) as caught:
                mod12.top_up_applies(handing, 30)
            self.assertIn(
                "top_up_applies stands refused",
                str(caught.exception))
            self.assertIn(
                "stands in no finite form", str(caught.exception))

    def test_non_numeric_handings_refused_in_current_form(self):
        for handing in ("high", None, True):
            with self.assertRaises(
                    mod12.NamedControllerFailure) as caught:
                mod12.top_up_applies(handing, 30)
            self.assertIn(
                "top up rule inputs are not numbers",
                str(caught.exception))

    def test_control_in_range_stands_true(self):
        self.assertTrue(mod12.top_up_applies(0.5, 30))

    def test_control_strict_bounds_stand_false(self):
        self.assertTrue(mod12.top_up_applies(0.1, 30))
        self.assertTrue(mod12.top_up_applies(0.9, 30))

    def test_control_closed_range_endpoints_stand_false(self):
        self.assertFalse(mod12.top_up_applies(0.0, 30))
        self.assertFalse(mod12.top_up_applies(1.0, 30))

    def test_control_below_band_and_replicates_limb_stand_false(self):
        self.assertFalse(mod12.top_up_applies(0.05, 30))
        self.assertFalse(mod12.top_up_applies(0.5, 29))


if __name__ == "__main__":
    unittest.main()
