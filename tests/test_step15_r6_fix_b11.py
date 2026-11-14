"""Pins for fix wave 5, Builder 11.

Rows R5-012 MOD-03 limb, R5-013 MOD-03 limb, R5-019, R5-020,
R5-021, R5-023 MOD-03 limb, and R5-032. Each test states its
distinguishing case with controls both ways.
"""

import time
import unittest

from crucible import mod02, mod03, mod07


SHORT_I = "\u0439"
CHI = "\u03c7"
CANARY_DRESS = "\u0441a\u043da\u0440\u0439"
MEMBERSHIP_CORE = "membe\u0440\u0441\u043dip"


class EvilInt(int):
    """An int subclass storing 99 whose equality answers True."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class EvilList(list):
    """A list subclass storing two inputs whose length reads 1."""

    def __len__(self):
        return 1


class EvilTuple(tuple):
    """A tuple subclass storing two inputs whose length reads 1."""

    def __len__(self):
        return 1


class EvilName(str):
    """A str subclass storing gamma whose hash and equality
    readings answer as beta."""

    def __hash__(self):
        return str.__hash__("beta")

    def __eq__(self, other):
        return str.__eq__("beta", other)

    def __ne__(self, other):
        return not str.__eq__("beta", other)


class LieStr(str):
    """A str subclass key whose equality answers False."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class LieEdge(dict):
    """A dict edge whose get reading supplies a pair other than
    the pair it stores."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)


def shared_shape(depth):
    value = "leaf"
    for _ in range(depth):
        value = [value, value]
    return value


class TestR5012ShortIReading(unittest.TestCase):

    def test_composite_canary_dress_barred(self):
        self.assertTrue(mod03._is_barred_key(CANARY_DRESS))

    def test_single_dress_canary_barred(self):
        self.assertTrue(mod03._is_barred_key("canar" + SHORT_I))

    def test_compound_key_needing_both_readings_barred(self):
        key = SHORT_I + "s_honest_" + CANARY_DRESS
        self.assertTrue(mod03._is_barred_key(key))

    def test_record_end_to_end_barred(self):
        self.assertTrue(
            mod03.record_carries_ground_truth({CANARY_DRESS: "v"}))

    def test_controls(self):
        self.assertTrue(mod03._is_barred_key("canary"))
        self.assertFalse(mod03._is_barred_key("canari"))
        self.assertFalse(mod03._is_barred_key("clean_field"))


class TestR5013CountingBasis(unittest.TestCase):

    def test_short_i_option_set_is_i_and_y(self):
        options = set()
        for letter_map in (
                mod03._WIDE_LETTER_MAP, mod03._HOMOGLYPH_MAP,
                mod03._ALT_LETTER_MAP):
            options.add(mod03._canonical_text(SHORT_I, letter_map))
        self.assertEqual(options, {"i", "y"})

    def test_chi_option_set_is_x_and_h(self):
        options = set()
        for letter_map in (
                mod03._WIDE_LETTER_MAP, mod03._HOMOGLYPH_MAP,
                mod03._ALT_LETTER_MAP):
            options.add(mod03._canonical_text(CHI, letter_map))
        self.assertEqual(options, {"x", "h"})

    def test_core_barred_alone(self):
        self.assertTrue(mod03._is_barred_key(MEMBERSHIP_CORE))

    def test_filler_forms_stand_on_the_past_bound_side(self):
        self.assertFalse(
            mod03._is_barred_key(MEMBERSHIP_CORE + SHORT_I * 13))
        self.assertFalse(
            mod03._is_barred_key(MEMBERSHIP_CORE + CHI * 13))

    def test_controls(self):
        self.assertTrue(mod03._is_barred_key("membership"))
        self.assertFalse(
            mod03._is_barred_key("activity" + SHORT_I * 13))


class TestR5019CardinalityBaseReadings(unittest.TestCase):

    def setUp(self):
        self.stream_set = {
            "stream_class_inventory": ["alpha", "beta"]}

    def test_int_subclass_count_storing_99_refused(self):
        counts = {"alpha": 1, "beta": EvilInt(99)}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts=counts, stream_set=self.stream_set))

    def test_list_subclass_count_lying_length_refused(self):
        counts = {"alpha": 1, "beta": EvilList(["one", "two"])}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts=counts, stream_set=self.stream_set))

    def test_tuple_subclass_count_lying_length_refused(self):
        counts = {"alpha": 1, "beta": EvilTuple(("one", "two"))}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts=counts, stream_set=self.stream_set))

    def test_lying_class_name_refused(self):
        counts = {"alpha": 1, EvilName("gamma"): 1}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts=counts, stream_set=self.stream_set))

    def test_controls(self):
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": 1},
            stream_set=self.stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": 99},
            stream_set=self.stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": ["one", "two"]},
            stream_set=self.stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "gamma": 1},
            stream_set=self.stream_set))
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": ["one"]},
            stream_set=self.stream_set))


class TestR5020RuleStateKeyForms(unittest.TestCase):

    FIELDS = (
        "reputation", "stake_held", "band", "decided_effect",
        "contract_effect")

    def test_tuple_key_field_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod03.validate_generator_output(
                    [{(field,): "v"}]))

    def test_frozenset_key_field_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod03.validate_generator_output(
                    [{frozenset((field,)): "v"}]))

    def test_nested_tuple_key_field_refused(self):
        self.assertFalse(mod03.validate_generator_output(
            [{(("reputation",),): "v"}]))

    def test_tuple_key_inside_value_dict_refused(self):
        self.assertFalse(mod03.validate_generator_output(
            [{"outer": {("band",): "v"}}]))

    def test_lying_equality_plain_key_refused(self):
        self.assertFalse(mod03.validate_generator_output(
            [{LieStr("reputation"): "v"}]))

    def test_controls(self):
        self.assertFalse(mod03.validate_generator_output(
            [{"reputation": 1}]))
        self.assertTrue(mod03.validate_generator_output(
            [{("ordinary",): "v"}]))
        self.assertTrue(mod03.validate_generator_output(
            [{"clean": "v"}]))


class TestR5021FarmEdgeBaseGet(unittest.TestCase):

    def test_lying_get_edge_counts_by_stored_pair(self):
        edge = LieEdge(
            {"voucher": "a", "vouchee": "c"},
            {"voucher": "a", "vouchee": "b"})
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2, [edge])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_controls(self):
        cross = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": "a", "vouchee": "c"}])
        self.assertEqual(
            cross["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})
        internal = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": "a", "vouchee": "b"}])
        self.assertEqual(
            internal["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})


class TestR5023SharedContainerRewalk(unittest.TestCase):

    def test_shared_shape_depth_19_answers_quickly(self):
        start = time.monotonic()
        result = mod03.record_carries_ground_truth(shared_shape(19))
        elapsed = time.monotonic() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 3.0)

    def test_shared_shape_holding_barred_key_found(self):
        shared = {"canary": "v"}
        value = [[shared, shared], [shared, shared]]
        self.assertTrue(mod03.record_carries_ground_truth(value))

    def test_controls(self):
        self.assertTrue(mod03.record_carries_ground_truth(
            {"canary": "v"}))
        self.assertFalse(mod03.record_carries_ground_truth(
            {"clean": "v"}))
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.record_carries_ground_truth(cyclic)


def tracer_set_with(field, value):
    records = mod07.tracer_passage_records("run-1")
    records[0][field] = value
    return records


class TestR5032TracerBlankForms(unittest.TestCase):

    FIELDS = ("point_in_run", "what_in_fact_passed")

    def test_whitespace_bytes_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, b"   ")))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, b"\t\n")))

    def test_whitespace_bytearray_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, bytearray(b"  "))))

    def test_empty_memoryview_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, memoryview(b""))))

    def test_controls(self):
        self.assertTrue(mod07.validate_tracer_passage_set(
            mod07.tracer_passage_records("run-1")))
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertTrue(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, b" x")))
                self.assertTrue(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, bytearray(b" x"))))
                self.assertTrue(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, memoryview(b"x"))))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, b"")))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, "")))


if __name__ == "__main__":
    unittest.main()
