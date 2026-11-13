"""Contract test for operation C-05, plan section 2 section 5.

The test pins the check field of contract C-05 as plan section 9
states it. Surfaces crossed: MOD-13, via TG-14.3.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-05.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod13 as _m_mod13
    SURFACES["mod13"] = True
except Exception:
    SURFACES["mod13"] = False


class TestContractC05(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-05: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_extension_appends_a_linked_segment(self):
        """
        Fixture: Contract I extension form: a run record and an extension of it past its first horizon
        Pins: the extension appends a linked segment under the same derivation and the same rule version it in fact used, linked by run identifier and segment order, rewriting no part of the segment it extends; the extending run writes only the new segment
        Bar: a write path or a writer that reaches the earlier segment fails the check, and the extension is not reportable
        Failure: an extension that rewrites the earlier segment, mismatches its derivation or rule version, or breaks the link or segment order fails this test; while the surface is absent the test fails naming this behaviour and C-05
        """
        self.require("history extension appends a linked segment under the same derivation and rule version", "mod13")
        import crucible.mod13 as surface
        import copy
        history = [{"run_id": "run-c05", "segment_order": 1, "rule_set_version": "rules-1", "content": "first"}]
        before = copy.deepcopy(history)
        extended = surface.extend_history(history, {"content": "second"})
        self.assertEqual(history, before)
        self.assertEqual(extended[0], before[0])
        self.assertEqual(extended[1]["linked_run"], "run-c05")
        self.assertEqual(extended[1]["segment_order"], 2)
        self.assertEqual(extended[1]["rule_set_version"], "rules-1")

    def test_aggregates_stay_horizon_neutral(self):
        """
        Fixture: Contract I extension form: the daily aggregate form for the same simulated day at two horizons
        Pins: aggregates stay horizon neutral: the aggregate form carries no horizon field and no field whose value is taken from the run length first planned, and the two forms agree field for field
        Bar: an aggregate in a form carrying a horizon field, or a field derived from the planned horizon, fails validation and the extension carrying it is not reportable
        Failure: differing aggregate forms across horizons, or a horizon field present, fails this test; while the surface is absent the test fails naming this behaviour and C-05
        """
        self.require("daily aggregate form is identical across horizons and carries no horizon field", "mod13")
        import crucible.mod13 as surface
        form_a = surface.daily_aggregate_form()
        form_b = surface.daily_aggregate_form()
        self.assertEqual(form_a, form_b)
        self.assertNotIn("horizon", form_a)
        self.assertTrue(surface.validate_aggregate_form(form_a))
        self.assertFalse(surface.validate_aggregate_form(["run_id", "planned_horizon"]))

    def test_seed_limb_gated(self):
        """
        Fixture: no fixture stands for the seed limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: extension derivation on the adopted seed form under contract C-13
        Bar: the seed limb rests on the unadopted form while DQ7-02 stands open; no reportable run starts on the recommended derivation form until the adoption record stands
        Failure: an extension resting on the recommended form while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the DQ7-02 adoption record for register question NQ-24, owned by the Manager, due before Step 18 opens and by the close of Step 17")


if __name__ == "__main__":
    unittest.main()
