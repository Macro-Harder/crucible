"""Pin tests for rows R10-036, R10-037, R10-038, and R10-039.

Row R10-036 covers validate_adoption_record and
validate_derivation_input judging completeness by the plain
truthiness of a stored field value, which dispatches to a
length or bool reading the value itself supplies. Row R10-037
covers _state_from_held selecting the stored stream map by
an or test, so a dict subclass map reporting itself empty
loses its stored streams. Row R10-038 covers _position_value
applying plain int conversion to a stored position, which
dispatches to an int reading the value itself supplies,
against the base reading in _plain_number. Row R10-039 covers
the dict mode of _base_value_eq pairing a left key with the
first right key that matches it on stored text, keeping no
record of right keys already paired, where the set mode of
the same helper removes each matched candidate. Every
judgement stands on the stored contents read through base
class operations.
"""

import unittest

from crucible import mod02


class LenLieStr(str):
    """A string storing one text whose length reading reports
    a handed number."""

    def __new__(cls, stored, reported):
        value = str.__new__(cls, stored)
        value._reported = reported
        return value

    def __len__(self):
        return self._reported


class BoolLieStr(str):
    """A string storing one text whose bool reading reports
    a handed standing."""

    def __new__(cls, stored, reported):
        value = str.__new__(cls, stored)
        value._reported = reported
        return value

    def __bool__(self):
        return self._reported


class LenLieDict(dict):
    """A dict storing a handed mapping whose length reading
    reports zero."""

    def __len__(self):
        return 0


class BoolLieDict(dict):
    """A dict storing a handed mapping whose bool reading
    reports False."""

    def __bool__(self):
        return False


class IntLie(int):
    """An int storing one number whose int reading reports
    a handed number."""

    def __new__(cls, stored, reported):
        value = int.__new__(cls, stored)
        value._reported = reported
        return value

    def __int__(self):
        return self._reported


class HashLieStr(str):
    """A string storing one text whose hash reading reports
    a handed number, so two such keys storing one text can
    stand in one dict under different hashes."""

    def __new__(cls, stored, reported_hash):
        value = str.__new__(cls, stored)
        value._reported_hash = reported_hash
        return value

    def __hash__(self):
        return self._reported_hash


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


def paired_dict(first_value, second_value, reverse=False):
    first_key = HashLieStr("a", 111)
    second_key = HashLieStr("a", 222)
    result = {}
    if reverse:
        result[second_key] = second_value
        result[first_key] = first_value
    else:
        result[first_key] = first_value
        result[second_key] = second_value
    return result


class TestR10036AdoptionCompleteness(unittest.TestCase):

    def test_empty_generator_with_length_five_stands_refused(self):
        record = complete_adoption()
        record["generator"] = LenLieStr("", 5)
        self.assertIs(mod02.validate_adoption_record(record), False)

    def test_empty_version_with_length_two_stands_refused(self):
        record = complete_adoption()
        record["derivation_version"] = LenLieStr("", 2)
        self.assertIs(mod02.validate_adoption_record(record), False)

    def test_empty_inventory_with_length_four_stands_refused(self):
        record = complete_adoption()
        record["stream_inventory"] = LenLieStr("", 4)
        self.assertIs(mod02.validate_adoption_record(record), False)

    def test_complete_generator_with_length_zero_passes(self):
        record = complete_adoption()
        record["generator"] = LenLieStr("gen", 0)
        self.assertIs(mod02.validate_adoption_record(record), True)

    def test_complete_generator_with_bool_false_passes(self):
        record = complete_adoption()
        record["generator"] = BoolLieStr("gen", False)
        self.assertIs(mod02.validate_adoption_record(record), True)

    def test_empty_generator_with_bool_true_stands_refused(self):
        record = complete_adoption()
        record["generator"] = BoolLieStr("", True)
        self.assertIs(mod02.validate_adoption_record(record), False)

    def test_family_derivation_follows_the_stored_triple(self):
        blank = complete_adoption()
        blank["generator"] = LenLieStr("", 5)
        self.assertIs(mod02.validate_family_derivation(
            version="v1", adoption_record=blank), False)
        complete = complete_adoption()
        complete["generator"] = LenLieStr("gen", 0)
        self.assertIs(mod02.validate_family_derivation(
            version="v1", adoption_record=complete), True)

    def test_plain_adoption_records_stand_both_ways(self):
        self.assertIs(mod02.validate_adoption_record(
            complete_adoption()), True)
        blank = complete_adoption()
        blank["generator"] = ""
        self.assertIs(mod02.validate_adoption_record(blank), False)
        self.assertIs(mod02.validate_adoption_record({}), False)
        self.assertIs(mod02.validate_adoption_record(None), False)


class TestR10036DerivationInputCompleteness(unittest.TestCase):

    def test_empty_version_with_length_two_stands_refused(self):
        record = complete_derivation_input()
        record["derivation_version"] = LenLieStr("", 2)
        self.assertIs(mod02.validate_derivation_input(record), False)

    def test_complete_version_with_length_zero_passes(self):
        record = complete_derivation_input()
        record["derivation_version"] = LenLieStr("v1", 0)
        self.assertIs(mod02.validate_derivation_input(record), True)

    def test_complete_version_with_bool_false_passes(self):
        record = complete_derivation_input()
        record["derivation_version"] = BoolLieStr("v1", False)
        self.assertIs(mod02.validate_derivation_input(record), True)

    def test_plain_derivation_inputs_stand_both_ways(self):
        self.assertIs(mod02.validate_derivation_input(
            complete_derivation_input()), True)
        blank = complete_derivation_input()
        blank["derivation_version"] = ""
        self.assertIs(mod02.validate_derivation_input(blank), False)
        self.assertIs(mod02.validate_derivation_input({}), False)
        self.assertIs(mod02.validate_derivation_input(None), False)


class TestR10037StreamMapSelection(unittest.TestCase):

    def test_length_lie_map_keeps_its_streams_at_checkpoint(self):
        stream_map = LenLieDict({"real": {"position": 2}})
        held = {"stream_states": stream_map, "run_id": "r"}
        carried = mod02.checkpoint_generator_state(
            run_id="r", held_state=held)
        self.assertEqual(
            carried["stream_states"], {"real": {"position": 2}})

    def test_length_lie_map_keeps_its_streams_at_resume(self):
        stream_map = LenLieDict({"real": {"position": 2}})
        held = {"stream_states": stream_map, "run_id": "r"}
        carried = mod02.resume_consumed_generator_state(
            run_id="r", held_state=held)
        self.assertEqual(
            carried["stream_states"], {"real": {"position": 2}})

    def test_bool_lie_map_keeps_its_streams(self):
        stream_map = BoolLieDict({"real": {"position": 2}})
        held = {"stream_states": stream_map, "run_id": "r"}
        carried = mod02.checkpoint_generator_state(
            run_id="r", held_state=held)
        self.assertEqual(
            carried["stream_states"], {"real": {"position": 2}})

    def test_plain_stream_maps_stand_both_ways(self):
        held = {"stream_states": {"real": {"position": 2}}}
        carried = mod02.checkpoint_generator_state(held_state=held)
        self.assertEqual(
            carried["stream_states"], {"real": {"position": 2}})
        empty = mod02.checkpoint_generator_state(
            held_state={"stream_states": {}})
        self.assertEqual(empty["stream_states"], {})


class TestR10038PositionValue(unittest.TestCase):

    def test_direct_int_lie_position_carries_its_stored_number(self):
        held = {"stream_states": {"s1": IntLie(2, 99)}}
        carried = mod02.checkpoint_generator_state(held_state=held)
        self.assertEqual(
            carried["stream_states"], {"s1": {"position": 2}})

    def test_dict_entry_int_lie_position_carries_stored_number(self):
        entry = {"position": IntLie(2, 99)}
        held = {"stream_states": {"s1": entry}}
        carried = mod02.checkpoint_generator_state(held_state=held)
        self.assertEqual(
            carried["stream_states"], {"s1": {"position": 2}})

    def test_position_value_helper_reads_the_stored_number(self):
        self.assertEqual(mod02._position_value(IntLie(2, 99)), 2)
        self.assertEqual(
            mod02._position_value({"position": IntLie(2, 99)}), 2)
        self.assertEqual(mod02._plain_number(IntLie(2, 99)), 2)

    def test_int_lie_position_carries_at_resume(self):
        held = {"stream_states": {"s1": IntLie(2, 99)}}
        carried = mod02.resume_consumed_generator_state(
            held_state=held)
        self.assertEqual(
            carried["stream_states"], {"s1": {"position": 2}})

    def test_plain_positions_stand_as_before(self):
        held = {"stream_states": {"s2": 5, "s1": {"position": 3}}}
        carried = mod02.checkpoint_generator_state(held_state=held)
        self.assertEqual(carried["stream_states"], {
            "s1": {"position": 3}, "s2": {"position": 5}})


class TestR10039DictPairing(unittest.TestCase):

    def test_repaired_pairing_answers_true_at_the_carriage_act(self):
        held = paired_dict(1, 2)
        consumed = paired_dict(1, 2, reverse=True)
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), True)

    def test_repaired_pairing_answers_true_at_the_helper(self):
        held = paired_dict(1, 2)
        consumed = paired_dict(1, 2, reverse=True)
        self.assertIs(mod02._base_value_eq(held, consumed), True)

    def test_a_differing_pair_multiset_answers_false(self):
        held = paired_dict(1, 2)
        consumed = paired_dict(1, 3, reverse=True)
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), False)

    def test_a_right_key_stands_paired_only_once(self):
        held = paired_dict(1, 1)
        consumed = paired_dict(1, 2, reverse=True)
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), False)

    def test_shallow_and_set_forms_stand_both_ways(self):
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"a": 1}), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"a": 2}), False)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": {1, 2}}, {"a": {2, 1}}), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": {1, 2}}, {"a": {1, 3}}), False)


if __name__ == "__main__":
    unittest.main()
