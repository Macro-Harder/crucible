"""Fix wave 2 pins, Fix Builder 11.

R2-021, MOD-02: a handed in StreamSet that no stated form can read
stands refused in the module named failure form, ValueError, instead
of falling back to the no StreamSet behaviour.
R2-050, MOD-09: bond_search refuses a non finite griefing factor in
NamedAttackerFailure form instead of returning it as the worst factor.
"""

import math
import unittest

from crucible import mod02, mod09


class TestR2021MalformedStreamSetRefused(unittest.TestCase):
    def test_nameless_inventory_entry_refused(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"a": 1, "zz": 1},
                stream_set={"stream_class_inventory": [{"foo": 1}]})

    def test_non_record_stream_set_refused(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"a": 1, "zz": 1}, stream_set=12345)

    def test_string_stream_set_refused(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"a": 1, "zz": 1}, stream_set="ab")

    def test_typed_stream_set_with_no_inventory_refused(self):
        typed = mod02.StreamSet({"adjudication_stream": "a"})
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"adjudication_stream": 1}, stream_set=typed)

    def test_inventory_stated_as_one_string_refused(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"a": 1, "b": 1},
                stream_set={"stream_class_inventory": "ab"})

    def test_unhashable_class_entry_raises_named_failure(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"a": 1},
                stream_set={"stream_class_inventory": [["a"]]})


class TestR2021WellFormedStreamSetsStillPassBothWays(unittest.TestCase):
    def test_dict_stream_set_both_ways(self):
        stream_set = {"stream_class_inventory": ["class a", "class b"]}
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"class a": 1, "class b": 1}, stream_set=stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"class a": 1}, stream_set=stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"class a": 1, "class b": 1, "class zz": 1},
            stream_set=stream_set))

    def test_typed_stream_set_both_ways(self):
        typed = mod02.StreamSet(
            {"stream_class_inventory": ["class a", "class b"],
             "adjudication_stream": "class a"})
        self.assertTrue(mod02.validate_stream_cardinality(
            {"class a": 1, "class b": 1}, typed))
        self.assertFalse(mod02.validate_stream_cardinality(
            {"class a": 1}, typed))
        self.assertFalse(mod02.validate_stream_cardinality(
            {"class a": 1, "class b": 1, "class zz": 1}, typed))

    def test_list_stream_set_both_ways(self):
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"a": 1}, stream_set=["a"]))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"a": 1, "zz": 1}, stream_set=["a"]))

    def test_named_entry_stream_set_both_ways(self):
        stream_set = {"stream_class_inventory": [
            {"stream_class_identifier": "class a"},
            {"name": "class b"},
        ]}
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"class a": 1, "class b": 1}, stream_set=stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"class a": 1}, stream_set=stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"class a": 1, "class b": 1, "class zz": 1},
            stream_set=stream_set))

    def test_no_stream_set_behaviour_unchanged(self):
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"a": 1}))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"a": 2}))


class TestR2050BondSearchNonFiniteFactor(unittest.TestCase):
    def test_infinite_factor_from_harm_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"harm": math.inf, "attacker_cost": 1}])

    def test_negative_infinite_factor_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"harm": -math.inf, "attacker_cost": 1}])

    def test_nan_factor_from_harm_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"harm": math.nan, "attacker_cost": 1}])

    def test_nan_factor_from_evaluator_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"parameter_set": {"lien_multiplier": 2}}],
                griefing_evaluator=lambda params: math.nan)

    def test_infinite_factor_from_evaluator_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(
                [{"parameter_set": {"lien_multiplier": 2}}],
                griefing_evaluator=lambda params: math.inf)

    def test_finite_factor_still_returned(self):
        result = mod09.bond_search(
            [{"harm": 2, "attacker_cost": 1}])
        self.assertEqual(result["worst_griefing_factor"], 2)


if __name__ == "__main__":
    unittest.main()
