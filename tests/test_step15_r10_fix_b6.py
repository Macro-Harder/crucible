"""Pin tests for rows R9-014, R9-015, and R9-030 at MOD-02.

Row R9-014 covers validate_adoption_record,
validate_derivation_input, and validate_family_derivation
reading a handed record through its own get, contains, and
values readings. Row R9-015 covers _state_from_held reading
held state through its own contains, get, item, and iteration
readings, through both checkpoint_generator_state and
resume_consumed_generator_state. Row R9-030 covers
_base_value_eq raising a bare RecursionError on deep acyclic
states, judged through validate_generator_state_carriage.
Every judgement stands on the stored contents read through
base class operations, and the deep equality helper answers
deep acyclic forms while its cyclic behaviour stands kept.
"""

import unittest
from decimal import Decimal

from crucible import mod02


class AllLieDict(dict):
    """A dict whose get, contains, keys, and item readings all
    report a handed mapping, whatever it stores."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)

    def __contains__(self, key):
        return key in self._reported

    def __getitem__(self, key):
        return self._reported[key]

    def keys(self):
        return list(self._reported.keys())


class ValuesLieDict(dict):
    """A dict whose values reading reports handed values."""

    def __init__(self, stored, reported_values):
        dict.__init__(self, stored)
        self._reported_values = reported_values

    def values(self):
        return list(self._reported_values)


class HeldLieDict(dict):
    """A dict whose contains and get readings report one
    handed value for every key, and whose item reading does
    the same, whatever it stores."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def __contains__(self, key):
        return True

    def get(self, key, default=None):
        return self._reported

    def __getitem__(self, key):
        return self._reported


class IterLieDict(dict):
    """A dict whose iteration reading yields handed names and
    whose item reading reports a handed position record."""

    def __init__(self, stored, reported_names):
        dict.__init__(self, stored)
        self._reported_names = reported_names

    def __iter__(self):
        return iter(list(self._reported_names))

    def __getitem__(self, key):
        return {"position": 9}


class EqDict(dict):
    """A dict whose equality reading answers True always."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = None


def complete_adoption():
    return {
        "derivation_version": "v1",
        "stream_inventory": "inventory",
        "generator": "generator",
    }


def complete_derivation_input():
    return {
        "derivation_version": "v1",
        "domain": "screening",
        "root_seed_reference": "root",
        "scenario_identifier": "scenario",
        "run_identifier": "run",
        "stream_class_identifier": "stream",
        "parameter_values": {"alpha": "1", "beta": "2"},
    }


def deep_dict(depth, leaf):
    value = leaf
    for _ in range(depth):
        value = {"level": value}
    return value


def deep_list(depth, leaf):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def deep_mixed(depth, leaf):
    value = leaf
    for index in range(depth):
        if index % 2:
            value = {"level": value}
        else:
            value = [value]
    return value


class TestR9014AdoptionRecord(unittest.TestCase):

    def test_get_lie_storing_nothing_stands_refused(self):
        record = AllLieDict({}, complete_adoption())
        self.assertIs(mod02.validate_adoption_record(record), False)

    def test_get_lie_storing_a_partial_triple_stands_refused(self):
        stored = {"derivation_version": "v1"}
        record = AllLieDict(stored, complete_adoption())
        self.assertIs(mod02.validate_adoption_record(record), False)

    def test_get_lie_storing_complete_reporting_bogus_passes(self):
        record = AllLieDict(complete_adoption(), {})
        self.assertIs(mod02.validate_adoption_record(record), True)

    def test_plain_records_stand_both_ways(self):
        self.assertIs(mod02.validate_adoption_record(
            complete_adoption()), True)
        self.assertIs(mod02.validate_adoption_record({}), False)
        partial = complete_adoption()
        del partial["generator"]
        self.assertIs(mod02.validate_adoption_record(partial), False)
        blank = complete_adoption()
        blank["generator"] = ""
        self.assertIs(mod02.validate_adoption_record(blank), False)
        self.assertIs(mod02.validate_adoption_record(None), False)

    def test_get_lie_storing_complete_reporting_complete_passes(self):
        record = AllLieDict(complete_adoption(), complete_adoption())
        self.assertIs(mod02.validate_adoption_record(record), True)


class TestR9014DerivationInput(unittest.TestCase):

    def test_all_lie_storing_nothing_stands_refused(self):
        record = AllLieDict({}, complete_derivation_input())
        self.assertIs(mod02.validate_derivation_input(record), False)

    def test_all_lie_storing_a_partial_input_stands_refused(self):
        stored = complete_derivation_input()
        del stored["run_identifier"]
        record = AllLieDict(stored, complete_derivation_input())
        self.assertIs(mod02.validate_derivation_input(record), False)

    def test_values_lie_storing_a_non_text_value_stands_refused(self):
        stored = complete_derivation_input()
        stored["parameter_values"] = ValuesLieDict(
            {"alpha": 7}, ["1"])
        record = stored
        self.assertIs(mod02.validate_derivation_input(record), False)

    def test_values_lie_storing_text_reporting_non_text_passes(self):
        stored = complete_derivation_input()
        stored["parameter_values"] = ValuesLieDict(
            {"alpha": "1"}, [7])
        self.assertIs(mod02.validate_derivation_input(stored), True)

    def test_all_lie_storing_complete_reporting_bogus_passes(self):
        record = AllLieDict(complete_derivation_input(), {})
        self.assertIs(mod02.validate_derivation_input(record), True)

    def test_plain_inputs_stand_both_ways(self):
        self.assertIs(mod02.validate_derivation_input(
            complete_derivation_input()), True)
        self.assertIs(mod02.validate_derivation_input({}), False)
        bad_domain = complete_derivation_input()
        bad_domain["domain"] = "bogus"
        self.assertIs(mod02.validate_derivation_input(bad_domain),
                      False)
        blank_version = complete_derivation_input()
        blank_version["derivation_version"] = ""
        self.assertIs(mod02.validate_derivation_input(blank_version),
                      False)
        bad_param = complete_derivation_input()
        bad_param["parameter_values"] = {"alpha": 7}
        self.assertIs(mod02.validate_derivation_input(bad_param),
                      False)
        self.assertIs(mod02.validate_derivation_input(None), False)

    def test_all_lie_storing_complete_reporting_complete_passes(self):
        record = AllLieDict(
            complete_derivation_input(), complete_derivation_input())
        self.assertIs(mod02.validate_derivation_input(record), True)


class TestR9014FamilyDerivation(unittest.TestCase):

    def test_adoption_all_lie_storing_nothing_stands_refused(self):
        adoption = AllLieDict({}, complete_adoption())
        self.assertIs(mod02.validate_family_derivation(
            version="v1", adoption_record=adoption), False)

    def test_family_all_lie_storing_nothing_stands_refused(self):
        family = AllLieDict({}, {
            "derivation_version": "v1",
            "adoption_record": complete_adoption(),
        })
        self.assertIs(mod02.validate_family_derivation(
            family_record=family), False)

    def test_family_storing_complete_reporting_bogus_passes(self):
        family = AllLieDict({
            "derivation_version": "v1",
            "adoption_record": complete_adoption(),
        }, {"derivation_version": "bogus", "adoption_record": {}})
        self.assertIs(mod02.validate_family_derivation(
            family_record=family), True)

    def test_plain_family_forms_stand_both_ways(self):
        self.assertIs(mod02.validate_family_derivation(
            version="v1", adoption_record=complete_adoption()), True)
        self.assertIs(mod02.validate_family_derivation(
            version="v2", adoption_record=complete_adoption()), False)
        self.assertIs(mod02.validate_family_derivation(
            version="v1", adoption_record=None), False)
        self.assertIs(mod02.validate_family_derivation(
            version="v1", adoption_record={"derivation_version": "v1"}),
            False)
        self.assertIs(mod02.validate_family_derivation(
            family_record={
                "derivation_version": "v1",
                "adoption_record": complete_adoption(),
            }), True)

    def test_adoption_all_lie_storing_complete_passes(self):
        adoption = AllLieDict(complete_adoption(), complete_adoption())
        self.assertIs(mod02.validate_family_derivation(
            version="v1", adoption_record=adoption), True)


class TestR9015StateFromHeld(unittest.TestCase):

    def test_held_lie_storing_nothing_fabricates_no_stream(self):
        reported = {"streamX": {"position": 7}}
        held = HeldLieDict({}, reported)
        carried = mod02.checkpoint_generator_state(
            run_id="r", held_state=held)
        self.assertEqual(carried["stream_states"], {})
        resumed = mod02.resume_consumed_generator_state(
            run_id="r", held_state=HeldLieDict({}, reported))
        self.assertEqual(resumed["stream_states"], {})

    def test_iter_lie_storing_nothing_fabricates_no_stream(self):
        held = IterLieDict({}, ["streamY"])
        carried = mod02.checkpoint_generator_state(
            run_id="r", held_state=held)
        self.assertEqual(carried["stream_states"], {})
        resumed = mod02.resume_consumed_generator_state(
            run_id="r", held_state=IterLieDict({}, ["streamY"]))
        self.assertEqual(resumed["stream_states"], {})

    def test_held_get_lie_storing_a_real_state_passes_on_stored(self):
        stored = {
            "stream_states": {"real": {"position": 2}},
            "run_id": "stored run",
        }
        held = HeldLieDict(stored, {"streamX": {"position": 7}})
        carried = mod02.checkpoint_generator_state(held_state=held)
        self.assertEqual(
            carried["stream_states"], {"real": {"position": 2}})

    def test_position_get_lie_storing_a_real_position_passes(self):
        entry = AllLieDict({"position": 2}, {"position": 99})
        held = {"stream_states": {"s1": entry}}
        carried = mod02.checkpoint_generator_state(held_state=held)
        self.assertEqual(
            carried["stream_states"], {"s1": {"position": 2}})

    def test_plain_held_forms_stand_both_ways(self):
        held = {
            "stream_states": {"s2": 5, "s1": {"position": 3}},
            "run_id": "x",
        }
        carried = mod02.checkpoint_generator_state(held_state=held)
        self.assertEqual(carried["stream_states"], {
            "s1": {"position": 3}, "s2": {"position": 5}})
        self.assertEqual(carried["run_id"], "x")
        flat = {"beta": {"position": 4}, "alpha": 1}
        carried = mod02.resume_consumed_generator_state(
            held_state=flat)
        self.assertEqual(carried["stream_states"], {
            "alpha": {"position": 1}, "beta": {"position": 4}})
        empty = mod02.checkpoint_generator_state(held_state={})
        self.assertEqual(empty["stream_states"], {})
        no_held = mod02.checkpoint_generator_state(run_id="n")
        self.assertEqual(no_held["stream_states"], {})


class TestR9030DeepEquality(unittest.TestCase):

    def test_deep_dict_agreeing_at_2000_answers_true(self):
        held = deep_dict(2000, "leaf")
        consumed = deep_dict(2000, "leaf")
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), True)

    def test_deep_dict_differing_at_2000_answers_false(self):
        held = deep_dict(2000, "leaf")
        consumed = deep_dict(2000, "other")
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), False)

    def test_deep_list_agreeing_at_2000_answers_true(self):
        held = deep_list(2000, 1)
        consumed = deep_list(2000, 1)
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), True)

    def test_deep_list_differing_at_2000_answers_false(self):
        held = deep_list(2000, 1)
        consumed = deep_list(2000, 2)
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), False)

    def test_deep_mixed_agreeing_and_differing_answer(self):
        held = deep_mixed(2000, "leaf")
        self.assertIs(mod02.validate_generator_state_carriage(
            held, deep_mixed(2000, "leaf")), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            held, deep_mixed(2000, "other")), False)

    def test_deep_state_inside_the_carriage_form_answers(self):
        held = {"run_id": "r", "stream_states": deep_dict(1500, 3)}
        consumed = {"run_id": "r", "stream_states": deep_dict(1500, 3)}
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), True)
        other = {"run_id": "r", "stream_states": deep_dict(1500, 4)}
        self.assertIs(mod02.validate_generator_state_carriage(
            held, other), False)

    def test_cyclic_dict_pair_keeps_recursion_error(self):
        held = {}
        held["self"] = held
        consumed = {}
        consumed["self"] = consumed
        with self.assertRaises(RecursionError):
            mod02.validate_generator_state_carriage(held, consumed)

    def test_cyclic_list_pair_keeps_recursion_error(self):
        held = []
        held.append(held)
        consumed = []
        consumed.append(consumed)
        with self.assertRaises(RecursionError):
            mod02.validate_generator_state_carriage(held, consumed)

    def test_shallow_carriage_forms_stand_both_ways(self):
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"a": 1}), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"a": 2}), False)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": EqDict({"p": 1})}, {"a": {"p": 1}}), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": EqDict({"p": 1})}, {"a": {"p": 9}}), False)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": {1, 2}, "b": (1, "x"), "c": b"data",
             "d": Decimal(3)}, {"a": {2, 1}, "b": (1, "x"),
             "c": b"data", "d": Decimal(3)}), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": [1, 2]}, {"a": (1, 2)}), False)


if __name__ == "__main__":
    unittest.main()
