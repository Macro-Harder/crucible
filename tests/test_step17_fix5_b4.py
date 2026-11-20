"""Step 17, fix wave 5, Builder 4 defect tests.

Rows: FW5-04 (Medium, T17R4-04) and FW5-14 (Low, T17R4-14).

FW5-04: the mod03 farm size guard at _guard_farm_size judged a
farm size handing through the handing own comparison answers,
so a negative size in dressed int subclass form passed the
guard and built farms, while its plain twin refused in the
named NamedGeneratorFailure form. The cure judges the handing
on its plain value.

FW5-14: make_archetype_record served an identifier handing in
no identifier form whole in silence, and construct_farm placed
member handings in no identifier form into built farms in
silence. The cure refuses each such handing in named form, in
the identity form the mod10 retention door states.

Each defect test fails on the uncured tree and passes on the
cured tree. Each control passes on both trees.
Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

from crucible import mod03


class LyingInt(int):
    """An int subclass whose comparison answers lie, in the
    filing form of Red 1 S17R4-RED1-02: greater or equal and
    less or equal each answer True, less and greater each
    answer False, whatever the plain value stands at."""

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False


class AlwaysLessInt(int):
    """An int subclass whose less reading answers True against
    every other value, so a plain positive value reads as
    below zero through its own comparisons."""

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __ge__(self, other):
        return False

    def __gt__(self, other):
        return False


class TestFW504FarmSizePlainValue(unittest.TestCase):

    def test_construct_farm_lying_negative_five_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(["a", "b"], farm_size=LyingInt(-5))
        self.assertIn(
            "the farm size is not a non negative whole count",
            str(caught.exception))
        self.assertIn("-5", str(caught.exception))

    def test_construct_farm_lying_negative_one_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(
                ["a", "b", "c"], farm_size=LyingInt(-1))
        self.assertIn(
            "the farm size is not a non negative whole count",
            str(caught.exception))

    def test_build_farm_lying_negative_five_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.build_farm(["a", "b"], farm_size=LyingInt(-5))
        self.assertIn(
            "the farm size is not a non negative whole count",
            str(caught.exception))

    def test_build_cast_lying_negative_five_refuses(self):
        records = [mod03.make_archetype_record(
            archetype_id="a1", behaviour={"action": "vouch"},
            farm_member=True)]
        point = {"population": 1, "archetype_mix": {"a1": 1},
                 "farm_size": LyingInt(-5)}
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.build_cast(point, records, strategy_class="fixed")
        self.assertIn(
            "the farm size is not a non negative whole count",
            str(caught.exception))

    def test_always_less_positive_size_serves_whole(self):
        result = mod03.construct_farm(
            ["a", "b", "c"], farm_size=AlwaysLessInt(2))
        self.assertEqual(
            [farm["member_ids"] for farm in result["farms"]],
            [["a", "b"], ["c"]])

    def test_control_plain_negative_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(["a", "b"], farm_size=-5)

    def test_control_float_size_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(["a", "b"], farm_size=2.0)

    def test_control_bool_size_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(["a", "b"], farm_size=True)

    def test_control_plain_size_builds(self):
        result = mod03.construct_farm(["a", "b", "c"], farm_size=2)
        self.assertEqual(
            [farm["member_ids"] for farm in result["farms"]],
            [["a", "b"], ["c"]])

    def test_control_lying_positive_size_builds(self):
        result = mod03.construct_farm(
            ["a", "b", "c"], farm_size=LyingInt(2))
        self.assertEqual(
            [farm["member_ids"] for farm in result["farms"]],
            [["a", "b"], ["c"]])


class TestFW514ArchetypeIdentity(unittest.TestCase):

    def test_make_record_none_identifier_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.make_archetype_record(archetype_id=None)
        self.assertIn("identity less record", str(caught.exception))
        self.assertIn("no record stands built", str(caught.exception))

    def test_make_record_positional_none_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.make_archetype_record(None)
        self.assertIn("identity less record", str(caught.exception))
        self.assertIn("no record stands built", str(caught.exception))

    def test_make_record_empty_identifier_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.make_archetype_record(archetype_id="")
        self.assertIn("identity less record", str(caught.exception))
        self.assertIn("no record stands built", str(caught.exception))

    def test_make_record_whitespace_identifier_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.make_archetype_record(archetype_id="   ")
        self.assertIn("identity less record", str(caught.exception))
        self.assertIn("whitespace only", str(caught.exception))
        self.assertIn("no record stands built", str(caught.exception))

    def test_make_record_non_text_identifier_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.make_archetype_record(archetype_id=7)
        self.assertIn("identity less record", str(caught.exception))
        self.assertIn("no identifier form", str(caught.exception))
        self.assertIn("no record stands built", str(caught.exception))

    def test_control_make_record_valid_identifier_builds(self):
        record = mod03.make_archetype_record(
            archetype_id="honest", behaviour={"action": "vouch"})
        self.assertEqual(record["archetype_id"], "honest")
        self.assertEqual(record["behaviour"], {"action": "vouch"})


class TestFW514FarmMemberIdentity(unittest.TestCase):

    def test_construct_farm_none_member_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm([None, "a", "b"], farm_size=2)
        self.assertIn("identity less member", str(caught.exception))
        self.assertIn("no farm stands built", str(caught.exception))

    def test_construct_farm_empty_member_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(["", "a", "b"], farm_size=2)
        self.assertIn("identity less member", str(caught.exception))
        self.assertIn("no farm stands built", str(caught.exception))

    def test_construct_farm_whitespace_member_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(["   ", "a", "b"], farm_size=2)
        self.assertIn("identity less member", str(caught.exception))
        self.assertIn("whitespace only", str(caught.exception))
        self.assertIn("no farm stands built", str(caught.exception))

    def test_build_farm_none_member_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.build_farm([None, "a"], farm_size=2)
        self.assertIn("identity less member", str(caught.exception))
        self.assertIn("no farm stands built", str(caught.exception))

    def test_construct_farm_none_member_no_size_refuses(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm([None, "a"])
        self.assertIn("identity less member", str(caught.exception))
        self.assertIn("no farm stands built", str(caught.exception))

    def test_size_guard_stands_before_member_refusal(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(
                [None, "a"], farm_size=LyingInt(-5))
        self.assertIn(
            "the farm size is not a non negative whole count",
            str(caught.exception))

    def test_control_construct_farm_valid_members_build(self):
        result = mod03.construct_farm(["a", "b"], farm_size=2)
        self.assertEqual(
            [farm["member_ids"] for farm in result["farms"]],
            [["a", "b"]])

    def test_control_construct_farm_scalar_members_build(self):
        result = mod03.construct_farm([1, 2], 1, [(1, 1)])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_control_construct_farm_object_member_builds(self):
        member = object()
        result = mod03.construct_farm([member, "b"], 1, [(member, member)])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_control_construct_farm_empty_member_list_builds(self):
        result = mod03.construct_farm([], farm_size=2)
        self.assertEqual(result["farms"], [])


if __name__ == "__main__":
    unittest.main()
