"""Pins for Round 18 rows R18-016, R18-017, R18-018, R18-044,
and R18-045.

MOD-09 readout, catalogue, and carriage family, Builder 4 of
fix wave 18. Each pin states the defect its row charges in
the distinguishing case, beside the plain controls the source
papers ran.
"""
import time
import unittest
from decimal import Decimal
from fractions import Fraction

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


def _present(per_point_outcome):
    unit = mod09.readout(
        _record(per_point_outcome=per_point_outcome),
        found_failure=False)
    return _no_failure_present(unit)


class ReprBoom:
    def __repr__(self):
        raise RuntimeError("boom-repr")


class TestR18016ListAgainstDictCarriage(unittest.TestCase):
    def test_failure_beside_outcome_under_fellow_point_key(self):
        self.assertFalse(_present(
            [{"outcome": "no failure", "p1": "failure found"}]))

    def test_failure_beside_point_and_outcome_keys(self):
        self.assertFalse(_present(
            [{"point": "p1", "outcome": "no failure",
              "p2": "failure found"}]))

    def test_failure_in_nested_record_beside_outcome(self):
        self.assertFalse(_present(
            [{"outcome": "no failure",
              "detail": {"outcome": "failure found"}}]))

    def test_dict_carriage_control(self):
        self.assertFalse(_present(
            {"outcome": "no failure", "p1": "failure found"}))

    def test_clean_entry_control(self):
        self.assertTrue(_present(
            [{"outcome": "no failure", "p1": "no failure"}]))


class TestR18017FellowValueFormsOutsideGate(unittest.TestCase):
    def _present_with(self, entry):
        return _present([{"p0": "clean"}, entry])

    def test_failure_beside_decimal_fellow(self):
        self.assertFalse(self._present_with(
            {"p1": "failure found", "p2": Decimal(5)}))

    def test_failure_beside_fraction_fellow(self):
        self.assertFalse(self._present_with(
            {"p1": "failure found", "p2": Fraction(1, 2)}))

    def test_failure_beside_plain_object_fellow(self):
        self.assertFalse(self._present_with(
            {"p1": "failure found", "p2": object()}))

    def test_failure_beside_range_fellow(self):
        self.assertFalse(self._present_with(
            {"p1": "failure found", "p2": range(3)}))

    def test_cured_scalar_fellow_control(self):
        self.assertFalse(self._present_with(
            {"p1": "failure found", "p2": 5}))

    def test_top_level_dict_control(self):
        self.assertFalse(_present(
            {"p0": "clean", "p1": "failure found",
             "p2": Decimal(5)}))

    def test_clean_beside_decimal_fellow_control(self):
        self.assertTrue(self._present_with(
            {"p1": "no failure", "p2": Decimal(5)}))


class TestR18018ListEntryClassification(unittest.TestCase):
    def _present_with_clean(self, entry):
        return _present([{"p0": "clean"}, entry])

    def test_failure_beside_clean_outcome_key(self):
        self.assertFalse(self._present_with_clean(
            {"outcome": "clean", "p1": "failure found"}))

    def test_failure_under_point_named_point(self):
        self.assertFalse(self._present_with_clean(
            {"point": "failure found", "p2": "clean"}))

    def test_bare_text_failure_entry(self):
        self.assertFalse(self._present_with_clean("failure found"))

    def test_bare_list_failure_entry(self):
        self.assertFalse(self._present_with_clean(["failure found"]))

    def test_dict_carriage_outcome_control(self):
        self.assertFalse(_present(
            {"outcome": "clean", "p1": "failure found"}))

    def test_dict_carriage_point_control(self):
        self.assertFalse(_present(
            {"point": "failure found", "p2": "clean"}))

    def test_clean_sibling_alone_control(self):
        self.assertTrue(_present([{"p0": "clean"}]))

    def test_bare_clean_entry_control(self):
        self.assertTrue(self._present_with_clean("no failure"))


class TestR18044CatalogueReprKeyLimb(unittest.TestCase):
    def test_self_key_object_bounded(self):
        class Keyed:
            pass

        holder = Keyed()
        vars(holder)[holder] = 1
        self.assertIsInstance(mod09._catalogue_repr(holder), str)

    def test_self_key_object_at_public_gate(self):
        class Keyed:
            pass

        holder = Keyed()
        vars(holder)[holder] = 1
        catalogue = mod09.strategy_catalogue({holder})
        self.assertIn("identifiers", catalogue)

    def test_key_linked_chain_within_bound_cost(self):
        class Link:
            pass

        links = [Link() for _ in range(16)]
        for index in range(15):
            vars(links[index])[links[index + 1]] = index
        started = time.perf_counter()
        rendered = mod09._catalogue_repr(links[0])
        elapsed = time.perf_counter() - started
        self.assertIsInstance(rendered, str)
        self.assertLess(elapsed, 0.5)

    def test_value_cycle_control(self):
        class Valued:
            pass

        holder = Valued()
        vars(holder)["self"] = holder
        self.assertEqual(
            mod09._catalogue_repr(holder), "Valued(self=Valued)")

    def test_plain_control(self):
        self.assertEqual(
            mod09._catalogue_repr((1, "a")), "(1, 'a')")


class TestR18045WitnessCarriageRendering(unittest.TestCase):
    def test_repr_raising_identifier_renders(self):
        carriage = mod09.witness_carriage({
            "run_identifier": ReprBoom(),
            "regime_classification": "X"})
        self.assertIn("witness_run", repr(carriage))

    def test_repr_raising_classification_renders(self):
        carriage = mod09.witness_carriage({
            "run_identifier": "r5",
            "regime_classification": ReprBoom()})
        self.assertIn("regime_classification", repr(carriage))

    def test_repr_raising_identifier_no_envelope_renders(self):
        carriage = mod09.witness_carriage({
            "run_identifier": ReprBoom(),
            "regime_classification": "X"}, False)
        self.assertIn("witness_run", repr(carriage))

    def test_plain_control(self):
        carriage = mod09.witness_carriage({
            "run_identifier": "r1", "regime_classification": "X"})
        self.assertEqual(carriage["witness_run"], "r1")
        self.assertEqual(carriage["regime_classification"], "X")
        self.assertIn("attacker_cost_summary", carriage)


if __name__ == "__main__":
    unittest.main()
