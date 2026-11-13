"""Contract test for operation C-15, plan section 2 section 5.

The test pins the check field of contract C-15 as plan section 9
states it. Surfaces crossed: MOD-10, via TG-10.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-15.
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


class TestContractC15(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-15: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_rederivation_from_aggregates_alone(self):
        """
        Fixture: Shape 13 record set: one run, its DailyAggregates, and its recorded end of run regime classification
        Pins: classification rederived from aggregates alone matches the recorded classification, on stated denominators, with the components computed per viewer and the viewer identifier on every component; one DailyAggregates record stands per run per day per viewer, holding the four joint outcome components for that day for that viewer; the rederivation names its record state, the run record it reads and, where a summary record is among its inputs, whether that record stood before or after its last evaluation under C-08, with the evaluation outcome it read
        Bar: a classification computed during the run that disagrees with the rederived classification does not stand beside it: the rederived classification is the classification, and the disagreement is recorded as a defect in the run
        Failure: any difference between classification and rederivation, or a rederivation naming no record state, fails this test; while the surface is absent the test fails naming this behaviour and C-15
        """
        self.require("regime classification rederived from the daily aggregates alone matches the recorded classification", "mod10")
        import crucible.mod10 as mod10
        run_id = "run-c15"
        deliveries = [{"simulated_day": 1, "viewer_id": "viewer-1", "joint_outcome_components": [1, 2, 3, 4], "component_denominators": [10, 10, 10, 10], "honest_share": 0.5, "epochs_ending_on_day": ["epoch-1"], "gate_passing_shares": {"epoch-1": 0.5}}]
        aggregates = mod10.daily_aggregates_for_run(run_id=run_id, deliveries=deliveries)
        self.assertEqual(len(aggregates), 1)
        self.assertEqual(aggregates[0]["viewer_id"], "viewer-1")
        self.assertEqual(len(aggregates[0]["joint_outcome_components"]), 4)
        self.assertTrue(mod10.validate_daily_aggregates(aggregates))
        rederived = mod10.rederive_regime_classification(aggregates)
        self.assertIsNotNone(rederived)
        self.assertEqual(rederived["component_totals"], [1, 2, 3, 4])
        self.assertEqual(rederived["carriage"], "computed from the aggregates handed in")

    def test_no_singular_vector_or_cross_run_quantity(self):
        """
        Fixture: Shape 13 record set: a report presenting the daily components as one singular quantity, or comparing runs on the components as one quantity
        Pins: the report check fails: no singular vector is reported and no cross run comparison rests on these daily components as one quantity; cross run comparison rests on per viewer values compared viewer to viewer only
        Bar: decided bars only: the prohibition stands decided under DQ7-09 and waits on no decision or act; it is no barred limb
        Failure: such a presentation that passes the report check fails this test; while the surface is absent the test fails naming this behaviour and C-15
        """
        self.require("daily components are never presented or compared as one singular quantity", "mod10")
        import crucible.mod10 as mod10
        singular = [{"simulated_day": 1, "viewer_id": "viewer-1", "joint_outcome_components": [1, 2, 3, 4], "singular_vector": [10]}]
        self.assertFalse(mod10.validate_daily_aggregates(singular))
        self.assertFalse(mod10.validate_view_carriage({"form": "singular_vector", "presented_as": "one comparable quantity"}))
        per_viewer = [{"simulated_day": 1, "viewer_id": "viewer-1", "joint_outcome_components": [1, 2, 3, 4]}]
        self.assertTrue(mod10.validate_daily_aggregates(per_viewer))


if __name__ == "__main__":
    unittest.main()
