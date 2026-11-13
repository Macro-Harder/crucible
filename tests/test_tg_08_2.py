"""Test group TG-08.2. Slice S-08, module mod09.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod09, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
This group is the single check for the consolidated R20-A, R20-B
and R20-C duty, under Manager settlement S-5 and Step 12 Amendment
R1-010. No test in this file encodes real money stake behaviour:
test value only, in simulated units only, under DQ-162.
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
            "TG 08.2: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 08.2: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG082(unittest.TestCase):

    def test_selfish_mining_as_a_search_point_only(self):
        """Fixture: F-26, the selfish mining named case
        Pins: the case is used in exactly one way, as a strategy search point, with the contest at entry C-7 carried beside that use (inside its model, attackers below 25 percent can still gain under a proposed countermeasure, and with propagation delay modelled the threshold vanishes, both standings carried)
        Bar: the case is never a deployed failure case, and a test asserting either standing as settled fails this group
        Failure: the test fails while F-26 is used in any way other than as a strategy search point, or while either C-7 standing is asserted as settled
        """
        _require_entry(self, "F-26 stands as a strategy search point only, with both C-7 standings carried", ["run_search", "search", "AttackerSeat"])
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
            order_of_search=["point one"],
            case_uses=[{"fixture": "F-26"}])
        use = record["case_uses"][0]
        self.assertEqual(use["use"], "strategy search point only")
        self.assertFalse(use["deployed_failure_case"])
        self.assertFalse(use["standings_asserted_as_settled"])
        self.assertEqual(len(use["standings_carried"]), 2)
        self.assertIn("below 25 percent",
                      use["standings_carried"][0])
        self.assertIn("threshold vanishes",
                      use["standings_carried"][1])
        self.assertEqual(
            surface.SELFISH_MINING_CASE["use"],
            "strategy search point only")
        import copy
        tampered = copy.deepcopy(record)
        tampered["case_uses"][0]["use"] = "deployed failure case"
        self.assertFalse(surface.validate_search_record(tampered))

    def test_stopping_rule_conditions(self):
        """Fixture: a search record at rung 6 completion and at rung 0
        Pins: the readout point stands where the stopping rule at brief section 5.11 states it, with the zero attacker control at rung 0 carried as item INV-5 and battery check A-01 in that passage
        Bar: a readout called established before its stopping conditions stand met fails this group and TG-12.2 with it
        Failure: the test fails while a readout is called established before its stopping conditions stand met
        """
        _require_entry(self, "the readout point stands where the stopping rule states it", ["run_search", "search", "AttackerSeat"])
        surface = _module
        at_zero = surface.stopping_rule_state(0)
        self.assertFalse(at_zero["readout_point"])
        self.assertEqual(
            at_zero["rung_zero_control"]["carriage"],
            ("item INV-5", "battery check A-01"))
        self.assertEqual(
            at_zero["rung_zero_control"]["control"],
            "zero attacker control")
        at_six = surface.stopping_rule_state(6)
        self.assertTrue(at_six["readout_point"])
        self.assertFalse(at_six["established"])
        below = surface.stopping_rule_state(3)
        self.assertFalse(below["readout_point"])
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
        with self.assertRaises(surface.NamedAttackerFailure):
            surface.readout(record, established=True)

    def test_bond_parameter_search_stands_performed(self):
        """Fixture: a search record for one family, inspected for its bond parameter search limb; values in simulated units only, test value only under DQ-162
        Pins: slice S-08 has run one optimisation search above the fixed search ladder over the bond parameter space, namely lien multiplier, lien floor, and cost rule prices, each over its estimated sweep range as a labelled assumption, searching for the parameter set that maximises the griefing factor found in R-09-1, and the record reports the worst griefing factor found and the parameter set that produced it, in simulated units only, as Act A-18 states
        Bar: a clean fixed ladder with no optimisation search is reported as no counterexample found on those rungs, never as proof that no bond breaking parameter set exists, and a search record with no optimisation search limb, or with no worst griefing factor and no parameter set reported, fails this group; this test changes no bond parameter from its unsettled standing
        Failure: the test fails while the search record lacks the optimisation search limb, the worst griefing factor, or the parameter set
        """
        _require_entry(self, "the bond parameter search stands performed and reported in simulated units only", ["run_search", "search", "bond_search", "AttackerSeat"])
        surface = _module
        result = surface.bond_search([
            {"parameter_set": {"lien multiplier": 2,
                               "lien floor": 5,
                               "cost rule prices": 3},
             "harm": 10, "attacker_cost": 4},
            {"parameter_set": {"lien multiplier": 3,
                               "lien floor": 5,
                               "cost rule prices": 3},
             "harm": 9, "attacker_cost": 2},
        ])
        self.assertEqual(result["worst_griefing_factor"], 4.5)
        self.assertEqual(
            result["parameter_set"],
            {"lien multiplier": 3, "lien floor": 5,
             "cost rule prices": 3})
        self.assertEqual(
            result["parameter_space"],
            ["lien multiplier", "lien floor", "cost rule prices"])
        self.assertEqual(
            result["units"],
            "simulated units only, test value only under DQ-162")
        self.assertFalse(result["bond_parameters_changed"])
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
        limb = record["bond_parameter_search"]
        self.assertIsNotNone(limb["worst_griefing_factor"])
        self.assertTrue(limb["parameter_set"])

    def test_consolidated_r20_duty_single_check(self):
        """Fixture: a search bearing run record and a readout that reports an attacker search result, under Manager settlement S-5 and Step 12 Amendment R1-010
        Pins: TG-08.2 is the single check for the consolidated R20-A, R20-B and R20-C duty: the R20-B search record field list stands as the record duty for every search bearing run (search budget, points tried, neighbourhood definition and step sizes, starting points, order of search, per point outcome, and every adaptation); the R20-A coverage sentence stands inside every readout that reports an attacker search result, in the same unit as the readout wording; the R20-C sentence stands as the only form for reporting that a search found no failure; and stopping condition 2 at DQ7-10 in slice S-12 is never quoted without the R20-A coverage sentence in the same unit
        Bar: no coverage number is stated for the confined strategy class in any readout; TG-08.1, TG-12.2, and TG-14.2 pin no part of this duty again
        Failure: the test fails while any limb of the consolidated duty stands unchecked here, or while a coverage number for the confined strategy class stands in a readout
        """
        _require_entry(self, "the consolidated R20-A, R20-B and R20-C duty stands checked at TG-08.2 only", ["run_search", "search", "readout", "AttackerSeat"])
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
        fields = record["search_record"]
        for key in ("search_budget", "points_tried",
                    "neighbourhood_definition_and_step_sizes",
                    "starting_points", "order_of_search",
                    "per_point_outcome", "every_adaptation"):
            self.assertIn(key, fields)
        unit = surface.readout(
            record, found_failure=False,
            wording="readout wording for the search result")
        self.assertEqual(
            unit["coverage_sentence"], surface.COVERAGE_SENTENCE)
        self.assertIn("wording", unit)
        self.assertIsNone(
            unit["coverage_number_for_confined_class"])
        self.assertEqual(
            unit["no_failure_sentence"],
            surface.NO_FAILURE_SENTENCE)


if __name__ == "__main__":
    unittest.main()
