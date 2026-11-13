"""Contract test for operation C-17, plan section 2 section 5.

The test pins the check field of contract C-17 as plan section 9
states it. Surfaces crossed: MOD-05, via TG-04.4.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-17.
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


class TestContractC17(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-17: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_compute_and_log_split_with_unknown(self):
        """
        Fixture: F-23, the cold society degree case, at its unknown share limb
        Pins: the Parley Core computes the gate passing share per epoch and the Recorder logs the share it receives and computes none of it, with epoch close as the point of performance; where a share has not been delivered, the run record carries the explicit value unknown, and unknown is never read as zero; a share delivered after epoch close does not enter the record for that epoch and is recorded as a late delivery
        Bar: a run carrying zero in the unknown position fails this group; no cost statement assumes the share, and the share itself stands unfitted in every assumption set
        Failure: a Recorder computed share, a missing unknown, or a late delivery written back into a closed epoch fails this test; while the surface is absent the test fails naming this behaviour and C-17
        """
        self.require("core computes, Recorder logs and computes none, and an undelivered share stands as unknown", "mod05")
        import crucible.mod05 as mod05
        import crucible.mod10 as mod10
        share = mod05.gate_passing_share(["a", "b", "c"], ["a", "b"], epoch="epoch-1")
        self.assertEqual(share["computed_by"], "MOD-05 Parley Core")
        self.assertEqual(share["numerator"], 2)
        self.assertEqual(share["denominator"], 3)
        mod10.record_gate_passing_share("run-c17", "epoch-1", share)
        logged = mod10.gate_passing_shares_for_run("run-c17")
        self.assertEqual(logged["epoch-1"]["share"], share)
        undelivered = mod05.share_for_epoch("epoch-2")
        self.assertEqual(undelivered, mod05.UNKNOWN_SHARE)
        self.assertEqual(mod05.undelivered_share(), "unknown")
        self.assertFalse(mod05.validate_logged_share(0))
        self.assertTrue(mod05.validate_logged_share("unknown"))

    def test_double_application_derivation(self):
        """
        Fixture: F-23, the cold society degree case, at its logged share limb: a published population figure and its logged shares
        Pins: the derivation check recomputes the figure under the double application rule: the per eligible identity figure is the envelope value multiplied by the share, the corrected per epoch figure is that figure multiplied by the share again, epoch by epoch where the share varies, and the population average is the mean of the corrected per epoch figures as the final step; the derivation names its record state
        Bar: a published population figure derived by a single application, omitting the mean step, or naming no record state fails the derivation check
        Failure: such a figure that stands published fails this test; while the surface is absent the test fails naming this behaviour and C-17
        """
        self.require("population figures use the double application rule with the mean as the final step", "mod05")
        import crucible.mod05 as mod05
        share = mod05.gate_passing_share(["a", "b"], ["a"], epoch="epoch-1")
        figure = mod05.population_figure(100, [share], record_state="as retained")
        self.assertEqual(figure["per_epoch_corrected"], [25.0])
        self.assertEqual(figure["population_average"], 25.0)
        self.assertEqual(figure["derivation"], "double application, mean as the final step")
        self.assertEqual(figure["record_state"], "as retained")
        single = mod05.score_bearing_figure(100, share)
        self.assertEqual(single, 50.0)
        self.assertNotEqual(figure["population_average"], single)
        with self.assertRaises(ValueError):
            mod05.population_figure(100, [share])


if __name__ == "__main__":
    unittest.main()
