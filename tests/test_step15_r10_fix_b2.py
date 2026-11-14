"""Step 15 rerun fix wave 9 pins, Builder 2, MOD-10 limbs.

Row R9-004: a program actor dressed by three disjoint
transposed pairs beside one replacement resolves as program
at the MOD-10 resolver, and a program actor in a resolver
only dress (two disjoint transposed pairs beside one
replacement, a change total of three) stands as itself at
the MOD-10 resolver, in each case without falling through
to the mixed added person reading.
Row R9-011: the MOD-10 flag condition reading reads a handed
entry by its stored characters, not by an iteration reading
the entry itself supplies.
Row R9-013: the MOD-10 flag condition reading judges bytes,
bytearray, and memoryview entries on their decoded stored
text, so blank bytes forms state no condition, matching the
string form and MOD-07.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10


THREE_PAIRS_ONE_REPLACEMENT = [
    "agmrzpo", "rpgoarq", "marqorp", "ompaqgr", "mgarzop",
]

RESOLVER_ONLY = [
    "mzagrop", "mrazrop", "mragzop",
]

MIXED_PERSON = [
    "qersonx", "pesronx", "nersopx", "qersonxxxxxx",
]

BLANK_BYTES_FORMS = [
    b"", b" ", "\u200b".encode("utf-8"),
    bytearray(b"\x00"), bytearray(b"  "),
    memoryview(b" "), memoryview("\u200b".encode("utf-8")),
]

READABLE_BYTES_FORMS = [
    b"real", bytearray(b"real"), memoryview(b"real"),
    b"\xff",
]


class IterLieStr(str):
    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __iter__(self):
        return iter(self._lie)


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def promote(self, actor="program", fired=None):
        if fired is None:
            fired = ["condition a"]
        return mod10.apply_flag_evaluation(
            self.record(), outcome="promote", tier="Tier 2",
            actor=actor, inputs={"flag_conditions_fired": fired})


class TestR9004ThreePairsBesideOneReplacement(B2Base):
    def test_resolves_to_program_at_resolver(self):
        for actor in THREE_PAIRS_ONE_REPLACEMENT:
            with self.subTest(actor=actor):
                self.assertEqual(
                    mod10._resolve_actor_word(actor), "program")

    def test_resolves_to_program_at_normaliser(self):
        for actor in THREE_PAIRS_ONE_REPLACEMENT:
            with self.subTest(actor=actor):
                self.assertEqual(
                    mod10._normalised_actor(actor), "program")

    def test_promotes_at_flag_act_under_own_name(self):
        for actor in THREE_PAIRS_ONE_REPLACEMENT:
            with self.subTest(actor=actor):
                result = self.promote(actor=actor)
                self.assertEqual(result["retention_tier"], "Tier 2")
                self.assertEqual(
                    result["flag_evaluation"]["actor"], "program")

    def test_three_pairs_alone_control_still_resolves(self):
        self.assertEqual(mod10._resolve_actor_word("rpgoarm"), "program")
        self.assertEqual(mod10._normalised_actor("rpgoarm"), "program")


class TestR9004ResolverOnlyDresses(B2Base):
    def test_stand_as_themselves_at_resolver(self):
        for actor in RESOLVER_ONLY:
            with self.subTest(actor=actor):
                self.assertEqual(
                    mod10._resolve_actor_word(actor), actor)

    def test_stand_as_themselves_at_normaliser(self):
        for actor in RESOLVER_ONLY:
            with self.subTest(actor=actor):
                self.assertEqual(
                    mod10._normalised_actor(actor), actor)

    def test_promote_at_flag_act(self):
        for actor in RESOLVER_ONLY:
            with self.subTest(actor=actor):
                self.assertEqual(
                    self.promote(actor=actor)["retention_tier"],
                    "Tier 2")

    def test_composed_controls_still_resolve(self):
        self.assertEqual(mod10._resolve_actor_word("mzaxrop"), "program")
        self.assertEqual(mod10._resolve_actor_word("epsrno"), "person")
        self.assertEqual(mod10._resolve_actor_word("xpsrxx"), "xpsrxx")

    def test_mixed_added_controls_still_resolve_person(self):
        for actor in MIXED_PERSON:
            with self.subTest(actor=actor):
                self.assertEqual(
                    mod10._resolve_actor_word(actor), "person")

    def test_mixed_added_controls_still_refused(self):
        for actor in MIXED_PERSON:
            with self.subTest(actor=actor):
                with self.assertRaises(ValueError):
                    self.promote(actor=actor)

    def test_plain_controls(self):
        self.assertEqual(
            self.promote(actor="program")["retention_tier"], "Tier 2")
        with self.assertRaises(ValueError):
            self.promote(actor="person")


class TestR9011StoredCharacters(B2Base):
    def test_stored_blank_iterating_real_states_no_condition(self):
        entry = IterLieStr("\u200b", "real")
        self.assertFalse(mod10._has_stated_condition([entry]))

    def test_stored_real_iterating_blank_states_condition(self):
        entry = IterLieStr("real", "\u200b")
        self.assertTrue(mod10._has_stated_condition([entry]))

    def test_stored_blank_iterating_real_promotion_refused(self):
        entry = IterLieStr("\u200b", "real")
        with self.assertRaises(ValueError):
            self.promote(fired=[entry])

    def test_stored_real_iterating_blank_promotion_effects(self):
        entry = IterLieStr("real", "\u200b")
        self.assertEqual(
            self.promote(fired=[entry])["retention_tier"], "Tier 2")

    def test_handled_as_the_fired_value_itself(self):
        self.assertFalse(mod10._has_stated_condition(
            IterLieStr("\u200b", "real")))
        self.assertTrue(mod10._has_stated_condition(
            IterLieStr("real", "\u200b")))


class TestR9013BytesEntries(B2Base):
    def test_blank_bytes_forms_state_no_condition(self):
        for entry in BLANK_BYTES_FORMS:
            with self.subTest(entry=repr(entry)):
                self.assertFalse(mod10._has_stated_condition([entry]))

    def test_blank_bytes_forms_promotion_refused(self):
        for entry in BLANK_BYTES_FORMS:
            with self.subTest(entry=repr(entry)):
                with self.assertRaises(ValueError):
                    self.promote(fired=[entry])

    def test_readable_bytes_forms_state_condition(self):
        for entry in READABLE_BYTES_FORMS:
            with self.subTest(entry=repr(entry)):
                self.assertTrue(mod10._has_stated_condition([entry]))

    def test_readable_bytes_forms_promotion_effects(self):
        for entry in READABLE_BYTES_FORMS:
            with self.subTest(entry=repr(entry)):
                self.assertEqual(
                    self.promote(fired=[entry])["retention_tier"],
                    "Tier 2")

    def test_string_form_controls(self):
        self.assertFalse(mod10._has_stated_condition([""]))
        self.assertFalse(mod10._has_stated_condition([" "]))
        self.assertFalse(mod10._has_stated_condition(["\u200b"]))
        self.assertTrue(mod10._has_stated_condition(["real"]))
        with self.assertRaises(ValueError):
            self.promote(fired=[""])


if __name__ == "__main__":
    unittest.main()
