"""Pins for Round 17 rows R17-007, R17-022, R17-023, R17-024,
R17-025, R17-026, R17-035, and R17-049.

MOD-09 readout, catalogue, rendering, and summary family,
Builder 4 of fix wave 17. Each pin states the defect its row
charges in the distinguishing case, beside the plain controls
the source papers ran.
"""
import unittest

from crucible import mod09


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


NO_FAILURE = (
    "The search found no failure at the points the search record "
    "names.")


def _no_failure_present(unit):
    return unit.get("no_failure_sentence") == NO_FAILURE


class ReprBoom:
    def __repr__(self):
        raise RuntimeError("boom-repr")


class ReprBoomValue:
    def __repr__(self):
        raise ValueError("boom-repr-value")


class StrBoom:
    def __str__(self):
        raise RuntimeError("boom-str")


class FloatBoom(float):
    def __repr__(self):
        raise RuntimeError("boom-repr-float")


class TestR17007ReadoutMixedPointMapping(unittest.TestCase):
    def _present(self, per_point_outcome):
        unit = mod09.readout(
            _record(per_point_outcome=per_point_outcome),
            found_failure=False)
        return _no_failure_present(unit)

    def _present_mixed(self, entry):
        return self._present([{"outcome": "no failure"}, entry])

    def test_failure_beside_plain_integer_seen(self):
        self.assertFalse(self._present_mixed(
            {"p1": "failure found", "p2": 5}))

    def test_text_failure_beside_integer_point_seen(self):
        self.assertFalse(self._present_mixed(
            {"p1": 5, "p2": "failure found"}))

    def test_failure_beside_boolean_seen(self):
        self.assertFalse(self._present_mixed(
            {"p1": "failure found", "p2": True}))

    def test_failure_beside_none_seen(self):
        self.assertFalse(self._present_mixed(
            {"p1": "failure found", "p2": None}))

    def test_failure_beside_float_seen(self):
        self.assertFalse(self._present_mixed(
            {"p1": "failure found", "p2": 2.5}))

    def test_record_form_failure_beside_integer_seen(self):
        self.assertFalse(self._present_mixed(
            {"p1": {"outcome": "failure found"}, "p2": 5}))

    def test_entry_without_outcome_key_control(self):
        self.assertFalse(self._present([{"search_point": 1}]))

    def test_clean_mixed_control(self):
        self.assertTrue(self._present_mixed(
            {"p1": "no failure", "p2": "no failure"}))

    def test_pure_form_control(self):
        self.assertFalse(self._present_mixed(
            {"p1": "failure found"}))


class TestR17022AttackerPayoffRendering(unittest.TestCase):
    def test_in_protocol_repr_raising_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(
                {"in_protocol_payoff": ReprBoom()}, 5)

    def test_external_repr_raising_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(
                {"in_protocol_payoff": 10}, ReprBoom())

    def test_value_error_repr_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(
                {"in_protocol_payoff": ReprBoomValue()}, 5)

    def test_nonfinite_float_repr_raising_in_protocol(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(
                {"in_protocol_payoff": FloatBoom(float("inf"))}, 5)

    def test_nonfinite_float_repr_raising_external(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(
                {"in_protocol_payoff": 1}, FloatBoom(float("nan")))

    def test_plain_controls(self):
        self.assertEqual(mod09.attacker_payoff(
            {"in_protocol_payoff": 10}, 5), 15)
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff(
                {"in_protocol_payoff": float("inf")}, 5)
        self.assertIn("no finite numeric form", str(caught.exception))


class TestR17023AttackerCostSummaryRendering(unittest.TestCase):
    def test_repr_raising_run_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_cost_summary(ReprBoom())

    def test_plain_integer_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_cost_summary(123)
        self.assertIn("no record form", str(caught.exception))
        self.assertIn("123", str(caught.exception))

    def test_summary_over_repr_raising_classification_renders(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "r5", "attacker_cost": 5, "harm": 3,
            "regime_classification": ReprBoom()})
        self.assertIn("attacker_cost", repr(summary))

    def test_summary_over_repr_raising_cost_renders(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "r5", "attacker_cost": ReprBoom(),
            "harm": 3, "regime_classification": "X"})
        self.assertIn("attacker_cost", repr(summary))

    def test_summary_over_nested_repr_raising_harm_renders(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "r5", "attacker_cost": 5,
            "harm": {"parts": [ReprBoom()]},
            "regime_classification": "X"})
        self.assertIn("attacker_cost", repr(summary))

    def test_plain_summary_control(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "r1", "attacker_cost": 42, "harm": 7,
            "regime_classification": "X"})
        self.assertEqual(summary["attacker_cost"], 42)
        self.assertEqual(summary["classification_before"], "X")
        self.assertIn("descriptive figure", repr(summary))


class TestR17024BondSearchRendering(unittest.TestCase):
    def test_repr_raising_candidate_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search([ReprBoom()])

    def test_repr_raising_harm_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search([{
                "parameter_set": {"lien multiplier": 2},
                "harm": ReprBoom(), "attacker_cost": 2}])

    def test_repr_raising_factor_draws_named_sentence(self):
        def evaluator(params):
            return ReprBoom()

        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"parameter_set": {"lien multiplier": 2}}],
                griefing_evaluator=evaluator)

    def test_plain_controls(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.bond_search([42])
        self.assertIn("42", str(caught.exception))
        result = mod09.bond_search([{
            "parameter_set": {"lien multiplier": 2},
            "harm": 10, "attacker_cost": 4}])
        self.assertEqual(result["worst_griefing_factor"], 2.5)


class TestR17025BuildSearchRecordRendering(unittest.TestCase):
    def _build(self, case_uses):
        return mod09.build_search_record(
            _carriage(), points_tried=["point one"],
            per_point_outcome=[{"point": "point one",
                                "outcome": "no failure"}],
            bond_candidates=[{
                "parameter_set": {"lien multiplier": 2},
                "harm": 10, "attacker_cost": 4}],
            budget="stated budget",
            neighbourhood={"definition": "adjacent points",
                           "step sizes": [1]},
            starting_points=["point zero"],
            order_of_search=["point one"],
            case_uses=case_uses)

    def test_repr_raising_case_use_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            self._build([ReprBoom()])

    def test_plain_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            self._build([42])
        self.assertIn("42", str(caught.exception))


class TestR17026RunRecordCarriageRendering(unittest.TestCase):
    def test_str_raising_strategy_draws_named_sentence(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(
                ["a"], 0, "v", "p", "pv", strategies=[StrBoom()])

    def test_plain_controls(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.run_record_carriage(
                ["a"], 0, "v", "p", "pv", strategies=["bogus"])
        self.assertIn("bogus", str(caught.exception))
        carriage = mod09.run_record_carriage(
            ["a"], 0, "v", "p", "pv", strategies=["a"])
        self.assertEqual(carriage["strategies_exercised"], ["a"])


class TestR17035CatalogueReprBound(unittest.TestCase):
    def test_self_referring_list_bounded(self):
        parts = []
        parts.append(parts)
        self.assertIsInstance(mod09._catalogue_repr(parts), str)

    def test_deeply_nested_list_bounded(self):
        parts = ["leaf"]
        for _ in range(3000):
            parts = [parts]
        self.assertIsInstance(mod09._catalogue_repr(parts), str)

    def test_self_storing_object_catalogue_bounded(self):
        class SelfStoring:
            pass

        holder = SelfStoring()
        holder.stored = holder
        catalogue = mod09.strategy_catalogue({holder})
        self.assertIn("identifiers", catalogue)

    def test_deeply_nested_stored_contents_bounded(self):
        class Storing:
            pass

        head = Storing()
        current = head
        for _ in range(2000):
            nxt = Storing()
            current.child = nxt
            current = nxt
        catalogue = mod09.strategy_catalogue({head})
        self.assertIn("identifiers", catalogue)

    def test_plain_controls(self):
        self.assertEqual(
            mod09._catalogue_repr((1, "a")), "(1, 'a')")
        catalogue = mod09.strategy_catalogue()
        self.assertIn("conditional briber",
                      catalogue["identifiers"])


class TestR17049CostSummaryAbsentFigures(unittest.TestCase):
    def test_empty_run_names_absent_figures(self):
        summary = mod09.attacker_cost_summary({})
        self.assertEqual(summary["absent_fields"], [
            "run_identifier", "attacker_cost", "harm",
            "regime_classification"])
        self.assertIsNone(summary["regime_classification_changed"])
        self.assertIn(
            "no regime classification",
            summary["classification_standing"])

    def test_identifier_only_run_names_absent_figures(self):
        summary = mod09.attacker_cost_summary(
            {"run_identifier": "r2"})
        self.assertEqual(summary["absent_fields"], [
            "attacker_cost", "harm", "regime_classification"])
        self.assertIsNone(summary["regime_classification_changed"])

    def test_classification_only_partial_run(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "r3", "regime_classification": "X"})
        self.assertEqual(summary["absent_fields"], [
            "attacker_cost", "harm"])
        self.assertIs(summary["regime_classification_changed"], False)
        self.assertEqual(summary["classification_before"], "X")
        self.assertEqual(summary["classification_after"], "X")

    def test_complete_run_control(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "r1", "attacker_cost": 42, "harm": 7,
            "regime_classification": "X"})
        self.assertEqual(summary["absent_fields"], [])
        self.assertIs(summary["regime_classification_changed"], False)
        self.assertEqual(
            summary["standing"],
            "descriptive figure beside the witness")
        self.assertEqual(summary["priced_per"], "failure witness run")


if __name__ == "__main__":
    unittest.main()
