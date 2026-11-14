"""Step 14 re-run, Builder B5 pins for MOD-09, slice S-08.

These pins stand written test first against the residual forms of
the Step 15 Round 1 findings TA-30, TA-73, and TB-48 that the
re-run probes found still standing in the current tree: wrongly
typed values inside bond search candidates and external profit
sweeps escaping as bare Python errors, search record fields with
no content passing the completeness check, malformed subrecords
crashing the boolean checker and the readout, and a strategy class
standing in no list form being read as its characters. Every
quantity here stands in simulated units only, test value only
under DQ-162.
"""
import copy
import unittest

import crucible.mod09 as mod09


def _carriage():
    return mod09.run_record_carriage(
        ["conditional briber"], 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=["conditional briber"])


def _record():
    return mod09.build_search_record(
        _carriage(), points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": "no failure"}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=[0, 5])


class TestB05BondSearchTyping(unittest.TestCase):

    def test_non_numeric_harm_or_cost_raises_named_failure(self):
        for candidate in (
                {"parameter_set": {"lien multiplier": 2},
                 "harm": "ten", "attacker_cost": 4},
                {"parameter_set": {"lien multiplier": 2},
                 "harm": 10, "attacker_cost": "four"},
                {"parameter_set": {"lien multiplier": 2},
                 "harm": True, "attacker_cost": 4},
                {"parameter_set": {"lien multiplier": 2},
                 "harm": 10, "attacker_cost": True}):
            with self.assertRaises(
                    mod09.NamedAttackerFailure, msg=repr(candidate)):
                mod09.bond_search([candidate])

    def test_evaluator_result_in_no_numeric_form_raises_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"parameter_set": {"lien multiplier": 2}}],
                griefing_evaluator=lambda params: "high")
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"parameter_set": {"lien multiplier": 2}},
                 {"parameter_set": {"lien multiplier": 3}}],
                griefing_evaluator=lambda params: None)

    def test_well_formed_search_unchanged(self):
        result = mod09.bond_search([{
            "parameter_set": {"lien multiplier": 2},
            "harm": 10, "attacker_cost": 4}])
        self.assertEqual(result["worst_griefing_factor"], 2.5)


class TestB05SweepTyping(unittest.TestCase):

    def test_sweep_on_no_record_raises_named_failure(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.sweep_external_profit(None)

    def test_sweep_range_values_in_no_numeric_form_raises_named(self):
        strategy = mod09.make_strategy(
            "conditional briber", in_protocol_payoff=1,
            external_profit_range=[0, "five"])
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.sweep_external_profit(strategy)
        strategy = mod09.make_strategy(
            "conditional briber", in_protocol_payoff=1,
            external_profit_range=[0, True])
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.sweep_external_profit(strategy)

    def test_well_formed_sweep_unchanged(self):
        strategy = mod09.make_strategy(
            "conditional briber", in_protocol_payoff=2,
            external_profit_range=[0, 3])
        swept = mod09.sweep_external_profit(strategy)
        self.assertEqual(
            [entry["attacker_payoff"] for entry in swept], [2, 5])


class TestB05SearchRecordContent(unittest.TestCase):

    def test_empty_content_fields_fail_validation(self):
        record = _record()
        self.assertTrue(mod09.validate_search_record(record))
        for key, empty in (
                ("search_budget", ""),
                ("points_tried", []),
                ("neighbourhood_definition_and_step_sizes", {}),
                ("starting_points", []),
                ("order_of_search", []),
                ("per_point_outcome", [])):
            hollow = copy.deepcopy(record)
            hollow["search_record"][key] = empty
            self.assertFalse(
                mod09.validate_search_record(hollow), key)

    def test_no_adaptation_record_still_validates(self):
        record = _record()
        self.assertEqual(record["search_record"]["every_adaptation"],
                         [])
        self.assertTrue(mod09.validate_search_record(record))

    def test_malformed_subrecords_fail_validation_not_crash(self):
        record = _record()
        for key, bad in (("search_record", None),
                         ("case_uses", ["not a record"])):
            broken = copy.deepcopy(record)
            broken[key] = bad
            self.assertFalse(
                mod09.validate_search_record(broken), key)


class TestB05ReadoutCarriage(unittest.TestCase):

    def test_readout_on_malformed_carriage_raises_named_failure(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout({"run_record": "not a record"})
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout({"run_record": None})
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout({
                "run_record": {
                    "ladder_position": 6,
                    "strategies_exercised": None},
                "external_profit_swept_values": [1]})

    def test_boolean_swept_value_is_no_positive_profit_value(self):
        unit = mod09.readout({
            "run_record": {
                "ladder_position": 6,
                "strategies_exercised": ["conditional briber"]},
            "external_profit_swept_values": [True]})
        self.assertEqual(unit.get("result_kind"),
                         "in protocol result only")


class TestB05RunRecordClassForm(unittest.TestCase):

    def test_strategy_class_in_no_list_form_raises_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(
                "conditional briber", 6, "catalogue version 1",
                "ladder definition pointer", "ladder version 1",
                strategies=["conditional"])
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(
                {"conditional briber": 1}, 6, "catalogue version 1",
                "ladder definition pointer", "ladder version 1")

    def test_hostile_kind_counts_in_no_numeric_form_read_unrun(self):
        covered = mod09.search_record_covers_hostile_kinds(
            {"hostile_kind_runs": {"junk share": "many"}},
            {"junk share": 5})
        self.assertFalse(covered["junk share"])

    def test_witness_carriage_on_no_record_raises_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.witness_carriage(None)
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_cost_summary(None)


if __name__ == "__main__":
    unittest.main()
