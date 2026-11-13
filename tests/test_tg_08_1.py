"""Test group TG-08.1. Slice S-08, module mod09.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod09, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
This group is not a check of the consolidated R20-A, R20-B and
R20-C duty. That duty is checked at test group TG-08.2 only, under
Step 12 Amendment R1-010.
"""
import unittest

try:
    import crucible.mod09 as _module
    SURFACE_STANDS = True
except Exception:
    _module = None
    SURFACE_STANDS = False


def _require_entry(case, behaviour, names):
    if not SURFACE_STANDS:
        case.fail(
            "TG 08.1: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 08.1: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG081(unittest.TestCase):

    def test_strategy_class_fixed_before_the_run(self):
        """Fixture: a run record inspected for its strategy class and ladder position
        Pins: the strategies exercised in a run are drawn from the fixed strategy class for that run, and the class and the ladder position stand in the run record
        Bar: a strategy introduced mid run, or a ladder position absent from the record, fails this group; the catalogue the plan names under OP-11 is the only source of strategy identifiers a test may use; this group pins no part of the consolidated R20 duty
        Failure: the test fails while the run record cannot show a fixed strategy class and a ladder position
        """
        _require_entry(self, "strategies are drawn from the fixed strategy class stated in the run record", ["run_search", "search", "AttackerSeat"])
        surface = _module
        carriage = surface.run_record_carriage(
            ["conditional briber", "junk share"], 6,
            "catalogue version 1", "ladder definition pointer",
            "ladder version 1", strategies=["conditional briber"])
        self.assertEqual(
            carriage["strategy_class"],
            ["conditional briber", "junk share"])
        self.assertEqual(carriage["ladder_position"], 6)
        self.assertEqual(
            carriage["strategies_exercised"], ["conditional briber"])
        with self.assertRaises(surface.NamedAttackerFailure):
            surface.run_record_carriage(
                ["conditional briber"], 6, "catalogue version 1",
                "ladder definition pointer", "ladder version 1",
                strategies=["outside strategy"])

    def test_mid_run_strategy_or_missing_position_fails(self):
        """Fixture: a run record with a strategy introduced mid run, and one with no ladder position
        Pins: a strategy introduced mid run, or a ladder position absent from the record, fails this group
        Bar: mid run introduction and a missing ladder position are barred forms
        Failure: the test fails while the surface cannot reject a mid run strategy or a missing ladder position
        """
        _require_entry(self, "a mid run strategy and a missing ladder position are rejected", ["run_search", "search", "AttackerSeat"])
        surface = _module
        carriage = surface.run_record_carriage(
            ["conditional briber"], 6, "catalogue version 1",
            "ladder definition pointer", "ladder version 1",
            strategies=["conditional briber"])
        record = surface.build_search_record(
            carriage, points_tried=["point one"],
            per_point_outcome=[{"point": "point one",
                                "outcome": "no failure"}],
            bond_candidates=[{
                "parameter_set": {"lien multiplier": 2,
                                  "lien floor": 5,
                                  "cost rule prices": 3},
                "harm": 10, "attacker_cost": 4}],
            budget="stated budget",
            neighbourhood={"definition": "adjacent points",
                           "step sizes": [1]},
            starting_points=["point zero"],
            order_of_search=["point one"])
        self.assertTrue(surface.validate_search_record(record))
        import copy
        tampered = copy.deepcopy(record)
        tampered["mid_run_strategies"] = ["late strategy"]
        self.assertFalse(surface.validate_search_record(tampered))
        with self.assertRaises(surface.NamedAttackerFailure):
            surface.run_record_carriage(
                ["conditional briber"], None, "catalogue version 1",
                "ladder definition pointer", "ladder version 1")
        missing = copy.deepcopy(record)
        del missing["run_record"]["ladder_position"]
        self.assertFalse(surface.validate_search_record(missing))

    def test_catalogue_and_ladder_version_carriage(self):
        """Fixture: a run record inspected for the catalogue version or hash of the class definition in force and the ladder definition pointer and version in force, per Amendment TG4-54
        Pins: the run record carries, beside the strategy class and the ladder position, the catalogue version or hash of the class definition in force and the ladder definition pointer and version in force for the run
        Bar: this text settles no part of OP-11, which stands open; this group pins no part of the consolidated R20 duty
        Failure: the test fails while the run record lacks the catalogue version or hash or the ladder definition pointer and version
        """
        _require_entry(self, "catalogue version or hash and ladder definition pointer and version stand in the run record", ["run_search", "search", "AttackerSeat"])
        surface = _module
        carriage = surface.run_record_carriage(
            ["conditional briber"], 6, "catalogue version 1",
            "ladder definition pointer", "ladder version 1")
        self.assertEqual(
            carriage["catalogue_version_or_hash"],
            "catalogue version 1")
        self.assertEqual(
            carriage["ladder_definition_pointer"],
            "ladder definition pointer")
        self.assertEqual(
            carriage["ladder_definition_version"],
            "ladder version 1")
        self.assertEqual(
            carriage["catalogue_standing"], "open at OP-11")
        with self.assertRaises(surface.NamedAttackerFailure):
            surface.run_record_carriage(
                ["conditional briber"], 6, None,
                "ladder definition pointer", "ladder version 1")
        with self.assertRaises(surface.NamedAttackerFailure):
            surface.run_record_carriage(
                ["conditional briber"], 6, "catalogue version 1",
                None, "ladder version 1")


if __name__ == "__main__":
    unittest.main()
