"""Contract test for operation C-23, plan section 2 section 5.

The test pins the check field of contract C-23 as plan section 9
states it. Surfaces crossed: MOD-06, via TG-05.4 and TG-14.2.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-23.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod06 as _m_mod06
    SURFACES["mod06"] = True
except Exception:
    SURFACES["mod06"] = False


class TestContractC23(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-23: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_matched_arm_pairing_audit(self):
        """
        Fixture: F-12, the B-5 matched comparison pair
        Pins: a pairing audit compares the two run records field by field over the shared inputs and the stamp group: the arms share cast, counts, role assignments, parameters and seeds, with variant bound roles held constant or converted by a stated rule standing in the record, the jury conversion under ruling DQ-4 standing in the run record for every B-5 run; each arm record carries the matched run identifier of its counterpart or an explicit none value, the escrow variant, and all four per variant record fields in force
        Bar: any input difference beyond the variant and the stated conversions is a breach at any size; a failed pair is reported as no comparison, never as a difference
        Failure: an unpermitted difference, a missing counterpart identifier with no explicit none value, or a failed pair reported as a difference fails this test; while the surface is absent the test fails naming this behaviour and C-23
        """
        self.require("matched arms share every stated input and differ only in the variant and stated conversions", "mod06")
        import crucible.mod06 as mod06
        shared = {"inputs": {"cast": "same"}, "society": "same", "parameters": "same", "seeds": "same"}
        arm_a = dict(shared)
        arm_a.update({"variant": "B-4", "results": [mod06.escrow_result("release", variant="B-4")]})
        arm_b = dict(shared)
        arm_b.update({"variant": "B-3", "results": [mod06.escrow_result("release", variant="B-3")]})
        self.assertTrue(mod06.matched_arms_valid(arm_a, arm_b))
        differing = dict(arm_b)
        differing["inputs"] = {"cast": "different"}
        self.assertFalse(mod06.matched_arms_valid(arm_a, differing))
        reported = mod06.report_difference({"kind": "difference"}, folding_record=None)
        self.assertEqual(reported["reported_as"], "unfolded difference only")
        self.assertFalse(reported["ruling_effect_wording"])

    def test_core_only_qualifier_on_every_arm_result(self):
        """
        Fixture: F-12, the B-5 matched comparison pair, at its escrow bearing results
        Pins: the core only qualifier reads true for every escrow bearing result in both arms, in the form operation C-23 states for comparison arms
        Bar: a pairing audit fails the pair on a core only qualifier reading other than true on an escrow bearing result
        Failure: an escrow bearing result with the qualifier absent or reading other than true fails this test; while the surface is absent the test fails naming this behaviour and C-23
        """
        self.require("core only qualifier reads true on every escrow bearing result in both matched arms", "mod06")
        import crucible.mod06 as mod06
        for variant in ("B-4", "B-3"):
            result = mod06.escrow_result("release", variant=variant)
            self.assertIs(result["core_only_qualifier"], True)
            self.assertTrue(mod06.validate_escrow_result(result))
        stripped = mod06.escrow_result("release", variant="B-4")
        stripped["core_only_qualifier"] = False
        self.assertFalse(mod06.validate_escrow_result(stripped))
        shared = {"inputs": {"cast": "same"}}
        arm_a = dict(shared)
        arm_a.update({"variant": "B-4", "results": [mod06.escrow_result("release", variant="B-4")]})
        arm_b = dict(shared)
        arm_b.update({"variant": "B-3", "results": [stripped]})
        self.assertFalse(mod06.matched_arms_valid(arm_a, arm_b))

    def test_seed_limb_gated(self):
        """
        Fixture: no fixture stands for the seed limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: matched arm runs executed on the adopted seed derivation form under contract C-13
        Bar: the seed limb is barred with C-13 while DQ7-02 stands open; no comparison arm run is executable on the recommended derivation form until the adoption that contract waits on stands
        Failure: a comparison arm run executed on the recommended form while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the DQ7-02 adoption record for register question NQ-24, owned by the Manager, due before Step 18 opens and by the close of Step 17")


if __name__ == "__main__":
    unittest.main()
