"""Pins for Round 16 rows R16-013 to R16-017, R16-025, and
R16-039 to R16-045.

MOD-09 search, readout, and catalogue forms with the MOD-02
generator state and plain equality forms, Builder 4 of fix
wave 16. Each test pins the defect its row states with the
proving acts the source papers used (Red 4, Blue 4, and
Orange 2 of Round 16), beside the plain controls those
papers ran.
"""
import subprocess
import sys
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod02, mod09


def _carriage(strategies=("conditional briber",), position=6):
    return mod09.run_record_carriage(
        list(strategies), position, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategies))


def _record(per_point_outcome=None, swept=(0, 5)):
    if per_point_outcome is None:
        per_point_outcome = [{"point": "point one",
                              "outcome": "no failure"}]
    return mod09.build_search_record(
        _carriage(), points_tried=["point one"],
        per_point_outcome=per_point_outcome,
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=swept)


NO_FAILURE = "The search found no failure at the points the search record names."


def _no_failure_present(unit):
    return unit.get("no_failure_sentence") == NO_FAILURE


class EqTrueInt(int):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class EqFalseInt(int):
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = int.__hash__


class LtGtFalseInt(int):
    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False

    __hash__ = int.__hash__


class GtTrueInt(int):
    def __gt__(self, other):
        return True

    __hash__ = int.__hash__


class AddInt(int):
    def __add__(self, other):
        return 999999

    __radd__ = __add__


class AddFloat(float):
    def __add__(self, other):
        return 999.0

    __radd__ = __add__


class DivFloat(float):
    def __truediv__(self, other):
        return 424242.0


class TruthFalseFloat(float):
    def __bool__(self):
        return False


class GtTrueFloat(float):
    def __gt__(self, other):
        return True

    __hash__ = float.__hash__


class GtFalseFloat(float):
    def __gt__(self, other):
        return False

    __hash__ = float.__hash__


class GeTrueFloat(float):
    def __ge__(self, other):
        return True

    __hash__ = float.__hash__


class GeFalseFloat(float):
    def __ge__(self, other):
        return False

    __hash__ = float.__hash__


class FalseTruthDict(dict):
    def __bool__(self):
        return False


class GhostIterList(list):
    def __iter__(self):
        return iter(["ghost-stream"])


class EmptyIterList(list):
    def __iter__(self):
        return iter([])


class FalseTruthTuple(tuple):
    def __bool__(self):
        return False


class EvilRepr:
    def __init__(self, tag):
        self.tag = tag

    def __hash__(self):
        return hash(self.tag)

    def __repr__(self):
        raise RuntimeError("supplied repr raises")


class SeedRepr:
    def __init__(self, tag):
        self.tag = tag

    def __hash__(self):
        return hash(self.tag)

    def __repr__(self):
        return str(hash(self.tag))


class TestR16013CarriageRange(unittest.TestCase):
    def test_position_99_in_lying_dress_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(
                ["a"], LtGtFalseInt(99), "v", "p", "pv")

    def test_negative_position_in_lying_dress_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(
                ["a"], LtGtFalseInt(-1), "v", "p", "pv")

    def test_position_3_with_lying_greater_refused_control(self):
        # Stored 3 stands inside the rungs; a greater reading
        # answering True must not refuse it.
        carriage = mod09.run_record_carriage(
            ["a"], GtTrueInt(3), "v", "p", "pv")
        self.assertEqual(carriage["ladder_position"], 3)

    def test_plain_controls(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(["a"], 99, "v", "p", "pv")
        carriage = mod09.run_record_carriage(
            ["a"], 3, "v", "p", "pv")
        self.assertEqual(carriage["ladder_position"], 3)


class TestR16014AttackerPayoff(unittest.TestCase):
    def test_int_dress_payoff_on_stored_values(self):
        result = mod09.attacker_payoff(
            {"in_protocol_payoff": AddInt(5)}, 3)
        self.assertEqual(result, 8)

    def test_float_dress_first_operand(self):
        result = mod09.attacker_payoff(
            {"in_protocol_payoff": AddFloat(2.0)}, 3.0)
        self.assertEqual(result, 5.0)

    def test_float_dress_second_operand(self):
        result = mod09.attacker_payoff(
            {"in_protocol_payoff": 2.0}, AddFloat(3.0))
        self.assertEqual(result, 5.0)

    def test_plain_control(self):
        self.assertEqual(mod09.attacker_payoff(
            {"in_protocol_payoff": 2.0}, 3.0), 5.0)


class TestR16015BondSearch(unittest.TestCase):
    def test_division_dress_factor_on_stored_values(self):
        result = mod09.bond_search([{
            "parameter_set": {"lien multiplier": 2},
            "harm": DivFloat(4.0), "attacker_cost": 2.0}])
        self.assertEqual(result["worst_griefing_factor"], 2.0)

    def test_worst_pick_not_moved_by_division_dress(self):
        result = mod09.bond_search([
            {"parameter_set": {"name": "first"},
             "harm": DivFloat(100.0), "attacker_cost": 1.0},
            {"parameter_set": {"name": "second"},
             "harm": 50.0, "attacker_cost": 1.0}])
        self.assertEqual(result["worst_griefing_factor"], 100.0)
        self.assertEqual(
            result["parameter_set"], {"name": "first"})

    def test_cost_truth_dress_candidate_still_scored(self):
        result = mod09.bond_search([{
            "parameter_set": {"lien multiplier": 2},
            "harm": 10.0, "attacker_cost": TruthFalseFloat(2.0)}])
        self.assertEqual(result["worst_griefing_factor"], 5.0)

    def test_worst_pick_not_moved_by_factor_comparison_dress(self):
        factors = iter([50.0, GtTrueFloat(1.0)])

        def evaluator(params):
            return next(factors)

        result = mod09.bond_search(
            [{"parameter_set": {"name": "first"}},
             {"parameter_set": {"name": "second"}}],
            griefing_evaluator=evaluator)
        self.assertEqual(result["worst_griefing_factor"], 50.0)
        self.assertEqual(
            result["parameter_set"], {"name": "first"})

    def test_zero_cost_still_unscored_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search([{
                "parameter_set": {"lien multiplier": 2},
                "harm": 10.0, "attacker_cost": 0}])


class TestR16016CoversHostileKinds(unittest.TestCase):
    def _family(self):
        return {kind: 10 for kind in mod09.HOSTILE_INPUT_KINDS}

    def _record(self, ran):
        runs = {kind: 10 for kind in mod09.HOSTILE_INPUT_KINDS}
        kind = mod09.HOSTILE_INPUT_KINDS[0]
        runs[kind] = ran
        return {"hostile_kind_runs": runs}, kind

    def test_below_fixed_in_lying_dress_not_covered(self):
        record, kind = self._record(GeTrueFloat(1.0))
        covered = mod09.search_record_covers_hostile_kinds(
            record, self._family())
        self.assertIs(covered[kind], False)

    def test_above_fixed_in_lying_dress_covered(self):
        record, kind = self._record(GeFalseFloat(99.0))
        covered = mod09.search_record_covers_hostile_kinds(
            record, self._family())
        self.assertIs(covered[kind], True)

    def test_plain_controls(self):
        record, kind = self._record(1.0)
        self.assertIs(mod09.search_record_covers_hostile_kinds(
            record, self._family())[kind], False)
        record, kind = self._record(99.0)
        self.assertIs(mod09.search_record_covers_hostile_kinds(
            record, self._family())[kind], True)


class TestR16017CarriedGeneratorState(unittest.TestCase):
    def test_ghost_iteration_classes_not_carried(self):
        state = mod02.checkpoint_generator_state(
            "r", stream_classes=GhostIterList(["a", "b"]))
        self.assertEqual(
            sorted(state["stream_states"]), ["a", "b"])

    def test_empty_iteration_classes_still_carried(self):
        state = mod02.checkpoint_generator_state(
            "r", stream_classes=EmptyIterList(["a"]))
        self.assertEqual(sorted(state["stream_states"]), ["a"])

    def test_false_truth_tuple_classes_still_carried(self):
        state = mod02.checkpoint_generator_state(
            "r", stream_classes=FalseTruthTuple(("a",)))
        self.assertEqual(sorted(state["stream_states"]), ["a"])

    def test_resume_entrance_same_form(self):
        state = mod02.resume_consumed_generator_state(
            "r", stream_classes=GhostIterList(["a", "b"]))
        self.assertEqual(
            sorted(state["stream_states"]), ["a", "b"])

    def test_plain_control(self):
        state = mod02.checkpoint_generator_state(
            "r", stream_classes=["a", "b"])
        self.assertEqual(
            sorted(state["stream_states"]), ["a", "b"])


class TestR16025ReadoutWalkLimbs(unittest.TestCase):
    def test_list_entry_in_point_mapping_form_seen(self):
        unit = mod09.readout(_record(per_point_outcome=[
            {"outcome": "no failure"},
            {"p1": {"outcome": "failure found"}}]),
            found_failure=False)
        self.assertFalse(_no_failure_present(unit))

    def test_list_entry_point_mapping_text_form_seen(self):
        unit = mod09.readout(_record(per_point_outcome=[
            {"outcome": "no failure"},
            {"p1": "failure found"}]),
            found_failure=False)
        self.assertFalse(_no_failure_present(unit))

    def test_top_level_dict_outcome_beside_point_keys_seen(self):
        unit = mod09.readout(_record(per_point_outcome={
            "outcome": "no failure", "p1": "failure found"}),
            found_failure=False)
        self.assertFalse(_no_failure_present(unit))

    def test_clean_point_mapping_control(self):
        unit = mod09.readout(_record(per_point_outcome={
            "p1": {"outcome": "no failure"}}),
            found_failure=False)
        self.assertTrue(_no_failure_present(unit))


class TestR16039StoppingRuleState(unittest.TestCase):
    def test_eq_true_position_5_not_readout_point(self):
        state = mod09.stopping_rule_state(EqTrueInt(5))
        self.assertIs(state["readout_point"], False)
        self.assertNotIn("rung_zero_control", state)

    def test_eq_false_position_6_is_readout_point(self):
        state = mod09.stopping_rule_state(EqFalseInt(6))
        self.assertIs(state["readout_point"], True)

    def test_eq_true_position_5_no_rung_zero_control(self):
        state = mod09.stopping_rule_state(EqTrueInt(5))
        self.assertNotIn("rung_zero_control", state)

    def test_plain_controls(self):
        self.assertIs(
            mod09.stopping_rule_state(5)["readout_point"], False)
        self.assertIs(
            mod09.stopping_rule_state(6)["readout_point"], True)
        self.assertIn(
            "rung_zero_control", mod09.stopping_rule_state(0))


class TestR16040ReadoutSweptPositivity(unittest.TestCase):
    def test_positive_value_with_lying_greater_counts(self):
        unit = mod09.readout(_record(swept=(0, GtFalseFloat(5.0))),
                             found_failure=False)
        self.assertEqual(
            unit["result_kind"], "economic security result")

    def test_nonpositive_value_with_lying_greater_not_counted(self):
        unit = mod09.readout(_record(swept=(0, GtTrueFloat(-5.0))),
                             found_failure=False)
        self.assertEqual(
            unit["result_kind"], "in protocol result only")

    def test_zero_value_with_lying_greater_not_counted(self):
        unit = mod09.readout(_record(swept=(GtTrueFloat(0.0),)),
                             found_failure=False)
        self.assertEqual(
            unit["result_kind"], "in protocol result only")

    def test_plain_controls(self):
        unit = mod09.readout(_record(swept=(0, 5.0)),
                             found_failure=False)
        self.assertEqual(
            unit["result_kind"], "economic security result")
        unit = mod09.readout(_record(swept=(0, -5.0)),
                             found_failure=False)
        self.assertEqual(
            unit["result_kind"], "in protocol result only")


class TestR16041MakeStrategyParameters(unittest.TestCase):
    def test_false_truth_dict_parameters_kept(self):
        strategy = mod09.make_strategy(
            "s", parameters=FalseTruthDict({"a": 1}))
        self.assertEqual(strategy["parameters"], {"a": 1})

    def test_plain_controls(self):
        self.assertEqual(mod09.make_strategy(
            "s", parameters={"a": 1})["parameters"], {"a": 1})
        self.assertEqual(mod09.make_strategy(
            "s", parameters={})["parameters"], {})
        self.assertEqual(mod09.make_strategy(
            "s")["parameters"], {})


class TestR16042RecordedOutcomeContent(unittest.TestCase):
    def _sentence_present(self, per_point_outcome):
        unit = mod09.readout(
            _record(per_point_outcome=per_point_outcome),
            found_failure=False)
        return _no_failure_present(unit)

    def test_point_mapping_empty_text_records_nothing(self):
        self.assertFalse(self._sentence_present({"p1": ""}))

    def test_point_mapping_empty_list_records_nothing(self):
        self.assertFalse(self._sentence_present({"p1": []}))

    def test_point_mapping_zero_records_nothing(self):
        self.assertFalse(self._sentence_present({"p1": 0}))

    def test_entry_empty_text_records_nothing(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": ""}]))

    def test_entry_empty_list_records_nothing(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": []}]))

    def test_entry_empty_dict_records_nothing(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": {}}]))

    def test_entry_false_records_nothing(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": False}]))

    def test_entry_zero_records_nothing(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": 0}]))

    def test_genuine_outcome_control(self):
        self.assertTrue(self._sentence_present(
            [{"outcome": "no failure"}]))
        self.assertTrue(self._sentence_present(
            {"p1": "no failure"}))

    def test_cured_absence_controls(self):
        self.assertFalse(self._sentence_present(
            [{"point": "point one"}]))
        self.assertFalse(self._sentence_present(
            [{"outcome": None}]))
        self.assertFalse(self._sentence_present({"p1": None}))
        self.assertFalse(self._sentence_present({"p1": {}}))


class TestR16043OutcomeFailureDictDress(unittest.TestCase):
    def _sentence_present(self, per_point_outcome):
        unit = mod09.readout(
            _record(per_point_outcome=per_point_outcome),
            found_failure=False)
        return _no_failure_present(unit)

    def test_dict_outcome_value_failure_seen(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": {"status": "failure found"}}]))

    def test_dict_outcome_key_failure_seen(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": {"failure found": "note"}}]))

    def test_dict_outcome_nested_outcome_failure_seen(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": {"outcome": "failure found"}}]))

    def test_list_entry_inside_point_mapping_seen(self):
        self.assertFalse(self._sentence_present(
            {"p1": [{"outcome": "failure found"}],
             "p2": {"outcome": "no failure"}}))

    def test_tuple_entry_inside_point_mapping_seen(self):
        self.assertFalse(self._sentence_present(
            {"p1": ({"outcome": "failure found"},),
             "p2": {"outcome": "no failure"}}))

    def test_controls(self):
        self.assertFalse(self._sentence_present(
            [{"outcome": "failure found"}]))
        self.assertFalse(self._sentence_present(
            {"p1": ["failure", "found"]}))
        self.assertTrue(self._sentence_present(
            [{"outcome": {"status": "no failure"}}]))


class TestR16044PlainEqualityKindFirst(unittest.TestCase):
    def test_boolean_version_not_validated_against_number(self):
        self.assertIs(mod02.validate_family_derivation(
            version=True,
            adoption_record={
                "derivation_version": 1,
                "stream_inventory": "inv",
                "generator": "gen"}), False)

    def test_decimal_version_not_validated_against_number(self):
        self.assertIs(mod02.validate_family_derivation(
            version=Decimal(1),
            adoption_record={
                "derivation_version": 1,
                "stream_inventory": "inv",
                "generator": "gen"}), False)

    def test_fraction_version_not_validated_against_number(self):
        self.assertIs(mod02.validate_family_derivation(
            version=Fraction(1, 1),
            adoption_record={
                "derivation_version": 1,
                "stream_inventory": "inv",
                "generator": "gen"}), False)

    def test_boolean_class_name_not_matched_to_integer_class(self):
        self.assertIs(mod02.validate_stream_cardinality(
            counts={True: 1}, stream_set=[1]), False)

    def test_same_kind_controls(self):
        self.assertIs(mod02.validate_family_derivation(
            version=1,
            adoption_record={
                "derivation_version": 1,
                "stream_inventory": "inv",
                "generator": "gen"}), True)
        self.assertIs(mod02.validate_family_derivation(
            version=Decimal(1),
            adoption_record={
                "derivation_version": Decimal(1),
                "stream_inventory": "inv",
                "generator": "gen"}), True)
        self.assertIs(mod02.validate_family_derivation(
            version=Fraction(1, 1),
            adoption_record={
                "derivation_version": Fraction(1, 1),
                "stream_inventory": "inv",
                "generator": "gen"}), True)
        self.assertIs(mod02.validate_family_derivation(
            version=True,
            adoption_record={
                "derivation_version": True,
                "stream_inventory": "inv",
                "generator": "gen"}), True)

    def test_carriage_decimal_same_kind_control(self):
        self.assertIs(mod02.validate_generator_state_carriage(
            {"d": Decimal(3)}, {"d": Decimal(3)}), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"d": Decimal(3)}, {"d": 3}), False)


class TestR16045CatalogueReprFallback(unittest.TestCase):
    def test_raising_repr_part_does_not_escape_catalogue(self):
        catalogue = mod09.strategy_catalogue({EvilRepr("x")})
        self.assertIn(
            "identifiers", catalogue)

    def test_raising_repr_part_inside_tuple(self):
        catalogue = mod09.strategy_catalogue(
            {(EvilRepr("x"),)})
        self.assertTrue(any(
            isinstance(name, tuple) for name in
            catalogue["identifiers"]))

    def test_supplied_repr_text_not_taken(self):
        representation = mod09._catalogue_repr(SeedRepr("m"))
        self.assertNotEqual(representation, str(hash("m")))

    def test_seed_order_stable_across_hash_seeds(self):
        script = (
            "from crucible import mod09\n"
            "class SeedRepr:\n"
            "    def __init__(self, tag):\n"
            "        self.tag = tag\n"
            "    def __hash__(self):\n"
            "        return hash(self.tag)\n"
            "    def __repr__(self):\n"
            "        return str(hash(self.tag))\n"
            "catalogue = mod09.strategy_catalogue(\n"
            "    {(SeedRepr('m'),), (SeedRepr('n'),)})\n"
            "tuples = [name for name in catalogue['identifiers']\n"
            "          if isinstance(name, tuple)]\n"
            "print(','.join(name[0].tag for name in tuples))\n")
        orders = []
        for seed in ("0", "3"):
            completed = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONHASHSEED": seed, "PATH": "/usr/bin:/bin",
                     "PYTHONPATH": "."},
                capture_output=True, text=True, cwd=".")
            self.assertEqual(completed.returncode, 0,
                             completed.stderr)
            orders.append(completed.stdout.strip())
        self.assertEqual(orders[0], orders[1])
        self.assertEqual(orders[0], "m,n")


if __name__ == "__main__":
    unittest.main()
