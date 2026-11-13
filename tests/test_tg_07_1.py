"""Test group TG-07.1. Slice S-07, module mod08.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod08, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
"""
import unittest

try:
    import crucible.mod08 as _module
    SURFACE_STANDS = True
except Exception:
    _module = None
    SURFACE_STANDS = False


def _require_entry(case, behaviour, names):
    if not SURFACE_STANDS:
        case.fail(
            "TG 07.1: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 07.1: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG071(unittest.TestCase):

    def test_detection_input_accepted(self):
        """Fixture: a delivery attempt carrying a DetectionInput record
        Pins: the Detection Layer accepts DetectionInput, per Contract E and TG-09.3
        Bar: acceptance of any other agent level form fails this group
        Failure: the test fails while no mod08 surface accepts DetectionInput
        """
        _require_entry(self, "the layer accepts DetectionInput only", ["accept_detection_input", "score", "DetectionLayer"])
        surface = _module
        record = {
            "agent_identifier": "agent-07-1",
            "day": 2,
            "feature_values": {"activity": 3},
            "records_for_agent_and_day": [{"kind": "daily_record"}],
        }
        accepted = surface.accept_detection_input(record)
        self.assertEqual(accepted["agent_identifier"], "agent-07-1")
        self.assertEqual(accepted["day"], 2)
        self.assertEqual(accepted["feature_values"], {"activity": 3})
        self.assertEqual(
            accepted["records_for_agent_and_day"],
            [{"kind": "daily_record"}])
        projected_form = {
            "agent_identifier": "agent-07-1",
            "day": 2,
            "feature_values": {"activity": 3},
            "rule_records": [{"kind": "daily_record"}],
        }
        self.assertEqual(
            surface.accept_detection_input(projected_form), accepted)
        layer = surface.DetectionLayer()
        self.assertEqual(layer.accept_detection_input(record), accepted)
        scored = surface.score(record)
        self.assertEqual(
            scored["verdict_states"][0]["agent_identifier"],
            "agent-07-1")

    def test_agent_state_rejected(self):
        """Fixture: a delivery attempt carrying an AgentState record
        Pins: the Detection Layer rejects every agent level form other than DetectionInput, per Contract E
        Bar: acceptance of AgentState or any other agent level form fails this group
        Failure: the test fails while the surface accepts, or cannot show rejection of, an AgentState delivery
        """
        _require_entry(self, "AgentState delivery is rejected", ["accept_detection_input", "score", "DetectionLayer"])
        surface = _module
        agent_level_state = {
            "agent_identifier": "agent-07-1",
            "archetype_identifier": "honest",
            "membership_ground_truth": "hidden",
            "reputation_score_by_viewer": {},
            "band": "band value",
            "stake_held": 5,
            "vouch_edges_given_and_received": [],
            "work_history_summary": {},
        }
        with self.assertRaises(surface.NamedDetectionFailure):
            surface.accept_detection_input(agent_level_state)
        with self.assertRaises(surface.NamedDetectionFailure):
            surface.score(agent_level_state)
        nested = {
            "agent_identifier": "agent-07-1",
            "day": 2,
            "feature_values": {"nested": {"membership": "hidden"}},
            "records_for_agent_and_day": [],
        }
        with self.assertRaises(surface.NamedDetectionFailure):
            surface.accept_detection_input(nested)
        import pathlib
        source_text = pathlib.Path(surface.__file__).read_text(
            encoding="utf-8")
        self.assertNotIn("Agent" + "State", source_text)

    def test_scoring_changes_no_rule_state(self):
        """Fixture: a scoring day over a known society state, with the full state compared before and after scoring
        Pins: the layer returns verdict states and accumulator updates and changes no reputation, stake, or contract state, per Contract E
        Bar: any state difference outside the detection state fails this group and marks the run invalid for detection reporting
        Failure: the test fails while scoring cannot be shown to leave reputation, stake, and contract state unchanged
        """
        _require_entry(self, "scoring changes no reputation, stake, or contract state", ["score_day", "score", "DetectionLayer"])
        surface = _module
        import copy
        society = {
            "agent-07-1": {
                "reputation": 10, "stake_held": 5,
                "contract_state": "open",
            },
        }
        before = copy.deepcopy(society)
        records = [{
            "agent_identifier": "agent-07-1", "day": 1,
            "feature_values": {"activity": 4},
            "records_for_agent_and_day": [],
        }]
        result = surface.score_day(records, society_state=society)
        self.assertEqual(society, before)
        self.assertFalse(result["rule_state_changed"])
        self.assertTrue(result["run_valid_for_detection_reporting"])
        self.assertEqual(len(result["verdict_states"]), 1)
        self.assertIn(
            result["verdict_states"][0]["verdict_state"],
            surface.VERDICT_LADDER)
        self.assertEqual(len(result["accumulator_updates"]), 1)
        self.assertEqual(
            result["accumulator_updates"][0]["agent_identifier"],
            "agent-07-1")

    def test_state_change_marks_run_invalid(self):
        """Fixture: a scoring day in which a reputation, stake, or contract value differs after scoring
        Pins: a state difference outside the detection state marks the run invalid for detection reporting
        Bar: a run with such a difference reported as valid for detection fails this group
        Failure: the test fails while the surface cannot mark such a run invalid
        """
        _require_entry(self, "an outside state change marks the run invalid for detection reporting", ["score_day", "score", "DetectionLayer"])
        surface = _module
        records = [{
            "agent_identifier": "agent-07-1", "day": 1,
            "feature_values": {"activity": 4},
            "records_for_agent_and_day": [],
        }]
        steady = {"reputation": "one value"}
        result = surface.score_day(records, society_state=steady)
        self.assertTrue(result["run_valid_for_detection_reporting"])

        class Snapshot(dict):
            def __deepcopy__(self, memo):
                return {"reputation": "snapshot before scoring"}

        shifting = Snapshot({"reputation": "value after scoring"})
        marked = surface.score_day(records, society_state=shifting)
        self.assertTrue(marked["rule_state_changed"])
        self.assertFalse(marked["run_valid_for_detection_reporting"])


class TestStep15Fix1RecursionBounds(unittest.TestCase):
    """Step 15 Round 1 fix pins: TA-03, on the MOD-08 barred key search."""

    def _record(self, feature_values):
        return {
            "agent_identifier": "agent-deep",
            "day": 1,
            "feature_values": feature_values,
            "records_for_agent_and_day": [],
        }

    def test_cyclic_input_raises_the_module_named_failure(self):
        cyclic = {}
        cyclic["self"] = cyclic
        with self.assertRaises(_module.NamedDetectionFailure):
            _module.accept_detection_input(self._record({"loop": cyclic}))

    def test_deep_input_raises_the_module_named_failure(self):
        deep = {"leaf": 1}
        for _ in range(2000):
            deep = {"nested": deep}
        with self.assertRaises(_module.NamedDetectionFailure) as caught:
            _module.accept_detection_input(self._record({"deep": deep}))
        self.assertIn("nested", str(caught.exception))

    def test_ordinary_input_still_accepted(self):
        accepted = _module.accept_detection_input(self._record({"activity": 1}))
        self.assertEqual(accepted["agent_identifier"], "agent-deep")


if __name__ == "__main__":
    unittest.main()
