"""Step 15 rerun fix wave 3, seat 8. MOD-12 items.

Pins for register rows R3-038, R3-045, and the MOD-12 limb of
R3-056. Each pin was written before its cure and the failing
counts on the unmodified tree stand recorded in the paper for
this seat.
"""
import unittest

from crucible import mod12


def list_chain(length):
    value = "leaf"
    for _ in range(length):
        value = [value]
    return value


def frozenset_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = frozenset((value,))
    return value


def tuple_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = (value,)
    return value


def run_record_with_key_chain(chain):
    return {"run_class": "screening", "seed_domain": "screening",
            "payload": {chain: 1}}


class TestR3038ClaimsBareString(unittest.TestCase):
    def test_string_claims_under_headline_claims_refused_named(self):
        record = mod12.make_family_record()
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(
                record, change={"headline_claims": "claim-one"})

    def test_string_claims_under_claims_alias_refused_named(self):
        record = mod12.make_family_record()
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(
                record, change={"claims": "claim-one"})

    def test_set_claims_refused_named(self):
        record = mod12.make_family_record()
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(
                record, change={"headline_claims": {"claim-one"}})

    def test_dict_claims_refused_named(self):
        record = mod12.make_family_record()
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(
                record,
                change={"headline_claims": {"claim-one": True}})

    def test_list_claims_control_lands_with_one_kill_check(self):
        record = mod12.make_family_record()
        edited = mod12.apply_family_edit(
            record, change={"headline_claims": ["claim-one"]})
        self.assertEqual(edited["headline_claims"], ["claim-one"])
        self.assertEqual(len(edited["kill_check_fields"]), 1)
        self.assertEqual(
            edited["kill_check_fields"][0]["claim"], "claim-one")

    def test_tuple_claims_control_lands(self):
        record = mod12.make_family_record()
        edited = mod12.apply_family_edit(
            record, change={"headline_claims": ("claim-one",)})
        self.assertEqual(edited["headline_claims"], ["claim-one"])

    def test_empty_list_claims_control_lands_empty(self):
        record = mod12.make_family_record()
        edited = mod12.apply_family_edit(
            record, change={"headline_claims": []})
        self.assertEqual(edited["headline_claims"], [])
        self.assertEqual(edited["kill_check_fields"], [])


class TestR3045ShapeWalkKeyPosition(unittest.TestCase):
    def test_frozenset_chain_key_past_bound_fails_validation(self):
        record = run_record_with_key_chain(frozenset_chain(150))
        self.assertFalse(mod12.validate_run_record(record))

    def test_tuple_chain_key_past_bound_fails_validation(self):
        record = run_record_with_key_chain(tuple_chain(150))
        self.assertFalse(mod12.validate_run_record(record))

    def test_frozenset_chain_key_at_depth_2000_fails_validation(self):
        record = run_record_with_key_chain(frozenset_chain(2000))
        self.assertFalse(mod12.validate_run_record(record))

    def test_shallow_frozenset_chain_key_control_passes(self):
        record = run_record_with_key_chain(frozenset_chain(10))
        self.assertTrue(mod12.validate_run_record(record))

    def test_frozenset_chain_key_change_refused_named(self):
        record = mod12.make_family_record()
        change = {"note": {frozenset_chain(150): 1}}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change=change)

    def test_tuple_chain_key_change_refused_named(self):
        record = mod12.make_family_record()
        change = {"note": {tuple_chain(150): 1}}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change=change)

    def test_frozenset_chain_key_change_at_2000_refused_named(self):
        record = mod12.make_family_record()
        change = {"note": {frozenset_chain(2000): 1}}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change=change)

    def test_value_position_chain_control_still_refused(self):
        record = {"run_class": "screening",
                  "seed_domain": "screening",
                  "payload": frozenset_chain(150)}
        self.assertFalse(mod12.validate_run_record(record))


class TestR3056ContainersOnlyCounting(unittest.TestCase):
    def test_list_chain_of_101_admitted_by_shape_walk(self):
        self.assertFalse(mod12._shape_exceeds_bounds(list_chain(101)))

    def test_list_chain_of_102_refused_by_shape_walk(self):
        self.assertTrue(mod12._shape_exceeds_bounds(list_chain(102)))

    def test_list_chain_of_100_admitted_by_shape_walk(self):
        self.assertFalse(mod12._shape_exceeds_bounds(list_chain(100)))

    def test_list_chain_of_103_refused_by_shape_walk(self):
        self.assertTrue(mod12._shape_exceeds_bounds(list_chain(103)))


if __name__ == "__main__":
    unittest.main()
