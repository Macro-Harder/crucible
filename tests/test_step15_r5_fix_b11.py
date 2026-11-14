"""Pins for fix wave 4, Builder 11.

Rows R4-011, R4-010, R4-020, R4-034, R4-035, the MOD-03 limb of
R4-015, the MOD-03 limb of R4-018, and R4-032. Each test states
its distinguishing case with controls both ways.
"""

import unittest

from crucible import mod02, mod03, mod07


class LyingCounts(dict):
    """A counts mapping whose items reading reports only a
    lawful subset of what it stores."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = reported

    def items(self):
        return list(self._reported)


def tuple_key_chain(depth):
    key = "leaf"
    for _ in range(depth):
        key = (key,)
    return key


def frozenset_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = frozenset((value,))
    return value


class TestR4011CountsBaseRead(unittest.TestCase):

    def test_stored_extra_class_and_bad_count_refused(self):
        counts = LyingCounts({"a": 1, "b": 99}, [("a", 1)])
        stream_set = {"stream_class_inventory": ["a"]}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts=counts, stream_set=stream_set))

    def test_stored_gamma_two_reported_clean_refused(self):
        counts = LyingCounts(
            {"gamma": 2}, [("alpha", 1), ("beta", 1)])
        stream_set = {"stream_class_inventory": ["alpha", "beta"]}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts=counts, stream_set=stream_set))

    def test_controls_both_ways(self):
        stream_set = {"stream_class_inventory": ["alpha", "beta"]}
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": 1}, stream_set=stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": 2}, stream_set=stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"alpha": 1}, stream_set=stream_set))
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": 1}))


class TestR4010BarredStringInContainerKey(unittest.TestCase):

    def test_tuple_key(self):
        record = {("membership",): 1}
        self.assertTrue(mod03.record_carries_ground_truth(record))
        self.assertFalse(mod03.validate_detection_input(record))
        self.assertFalse(mod03.validate_adjudication_input(record))
        self.assertEqual(mod03.strip_ground_truth(record), {})

    def test_nested_tuple_key(self):
        record = {(("ground_truth",),): 1}
        self.assertTrue(mod03.record_carries_ground_truth(record))
        self.assertEqual(mod03.strip_ground_truth(record), {})

    def test_frozenset_key(self):
        record = {frozenset(("canary",)): 1}
        self.assertTrue(mod03.record_carries_ground_truth(record))
        self.assertEqual(mod03.strip_ground_truth(record), {})

    def test_tuple_key_inside_value_dict(self):
        record = {"wrap": {("membership",): 1}}
        self.assertTrue(mod03.record_carries_ground_truth(record))
        self.assertFalse(mod03.validate_detection_input(record))
        self.assertEqual(
            mod03.strip_ground_truth(record), {"wrap": {}})

    def test_controls_both_ways(self):
        clean = {("clean",): 1, ("other", "fields"): 2}
        self.assertFalse(mod03.record_carries_ground_truth(clean))
        self.assertTrue(mod03.validate_detection_input(clean))
        self.assertEqual(mod03.strip_ground_truth(clean), clean)
        plain = {"membership": 1}
        self.assertTrue(mod03.record_carries_ground_truth(plain))
        self.assertEqual(mod03.strip_ground_truth(plain), {})


class TestR4020StripTraversesSets(unittest.TestCase):

    def test_frozenset_chain_150_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.strip_ground_truth({"wrap": frozenset_chain(150)})

    def test_frozenset_chain_102_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._strip_ground_truth_value(frozenset_chain(102))

    def test_set_holding_frozenset_chain_refused(self):
        value = {"wrap": {frozenset_chain(120)}}
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.strip_ground_truth(value)

    def test_boundary_and_clean_controls(self):
        chain = frozenset_chain(101)
        self.assertEqual(
            mod03._strip_ground_truth_value(chain), chain)
        record = {"wrap": {"a", "b"}, "items": frozenset((1, 2))}
        self.assertEqual(mod03.strip_ground_truth(record), record)
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.record_carries_ground_truth(
                {"wrap": frozenset_chain(102)})


class TestR4034RuleStateKeyPosition(unittest.TestCase):

    def test_key_chain_150_raises_named_form(self):
        record = {tuple_key_chain(150): "clean"}
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._value_carries_rule_state(record)

    def test_key_chain_total_102_raises_named_form(self):
        record = {tuple_key_chain(101): "clean"}
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._value_carries_rule_state(record)

    def test_public_surface_raises_named_form(self):
        record = {tuple_key_chain(150): "clean"}
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.validate_generator_output([record])

    def test_controls_both_ways(self):
        within = {tuple_key_chain(100): "clean"}
        self.assertFalse(mod03._value_carries_rule_state(within))
        self.assertTrue(mod03.validate_generator_output([within]))
        self.assertTrue(mod03._value_carries_rule_state(
            {"reputation": 5}))
        self.assertFalse(mod03._value_carries_rule_state(
            {"clean": 5}))


class TestR4035FarmDictEdgeVoucher(unittest.TestCase):

    def test_dict_edge_no_voucher_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=2, edges=[{"vouchee": "b"}])

    def test_dict_edge_none_voucher_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=2,
                edges=[{"voucher": None, "vouchee": "b"}])

    def test_controls_both_ways(self):
        result = mod03.construct_farm(
            ["a", "b"], farm_size=2,
            edges=[{"voucher": "a", "vouchee": "b"}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1})
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=2, edges=[{"voucher": "a"}])
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=2, edges=[{}])


class TestR4015Mod03CompositeFold(unittest.TestCase):

    def barred(self, key):
        return mod03.record_carries_ground_truth({"wrap": {key: 1}})

    def test_membership_transliteration_and_homoglyph(self):
        key = "member\u0441hi\u0440"
        self.assertIn("membership", mod03._folded_readings(key))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(self.barred(key))
        self.assertFalse(mod03.validate_detection_input(
            {"wrap": {key: 1}}))

    def test_canary_three_letter_mix(self):
        key = "\u0441ana\u0440\u0443"
        self.assertIn("canary", mod03._folded_readings(key))
        self.assertTrue(self.barred(key))

    def test_controls_both_ways(self):
        self.assertTrue(self.barred("membership"))
        self.assertTrue(self.barred("canary"))
        self.assertTrue(self.barred("member\u0441hip"))
        self.assertTrue(self.barred("member\u0441hi\u0440".replace("\u0440", "p")))
        self.assertFalse(self.barred("clean_field"))
        self.assertFalse(self.barred("ordinary"))


class TestR4018Mod03EnAndErFold(unittest.TestCase):

    def barred(self, key):
        return mod03.record_carries_ground_truth({"wrap": {key: 1}})

    def test_is_honest_en_at_both_positions(self):
        key = "is_\u043do\u043dest"
        self.assertIn("ishonest", mod03._folded_readings(key))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(self.barred(key))
        self.assertFalse(mod03.validate_detection_input(
            {"wrap": {key: 1}}))

    def test_sleeper_er_at_p_and_final_r(self):
        key = "slee\u0440e\u0440"
        self.assertIn("sleeper", mod03._folded_readings(key))
        self.assertTrue(self.barred(key))

    def test_controls_both_ways(self):
        self.assertTrue(self.barred("is_honest"))
        self.assertTrue(self.barred("sleeper"))
        self.assertFalse(self.barred("clean_field"))
        self.assertFalse(self.barred("honest"))


class TestR4032TracerEmptyBytes(unittest.TestCase):

    def set_field(self, field, value):
        records = mod07.tracer_passage_records("run-1")
        records[0][field] = value
        return records

    def test_point_in_run_empty_bytes(self):
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.set_field("point_in_run", b"")))

    def test_point_in_run_empty_bytearray(self):
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.set_field("point_in_run", bytearray(b""))))

    def test_what_passed_empty_bytes(self):
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.set_field("what_in_fact_passed", b"")))

    def test_what_passed_empty_bytearray(self):
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.set_field("what_in_fact_passed", bytearray(b""))))

    def test_controls_both_ways(self):
        records = mod07.tracer_passage_records("run-1")
        self.assertTrue(mod07.validate_tracer_passage_set(records))
        self.assertTrue(mod07.validate_tracer_passage_set(
            self.set_field("point_in_run", b"stated point")))
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.set_field("point_in_run", "")))


if __name__ == "__main__":
    unittest.main()
