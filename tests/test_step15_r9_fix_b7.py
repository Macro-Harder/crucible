"""Step 15 rerun fix wave 8 pins, Builder 7.

Pins for rows R8-001, R8-002, and the MOD-14 limb of row
R8-005 of the Round 8 register, all at the resolver
crucible/mod14.py _resolve_against and its consumers.

R8-001 and R8-002: a word whose differing positions stand
as two transposed pairs at any positions composed with two
replaced letters, six differing positions and a change
total of four, inside the resolver stated composition form
of up to two transpositions with up to three replacements,
resolves to its candidate at the actor reading and at the
target reading through _resolve_word alike.

R8-005, MOD-14 limb: a word built from two transposed
pairs and one replaced letter stands as itself where
exactly one pair stands adjacent. The older composition
limb must stop counting the adjacent pair as the
transposition with the three remaining positions as
replacements, in the direction the completion cure of step
record Entry 47 set for the anywhere limb, while the
charged R7-003 forms and the completion cure forms keep
their standings.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14


class B7Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def shell_promote(self, actor):
        return mod14.flag_evaluation(
            self.record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3", actor=actor)

    def assert_shell_refuses_person(self, actor):
        self.assertEqual(mod14._resolve_actor_word(actor), "person")
        self.assertEqual(mod14._normalise_actor(actor), "person")
        with self.assertRaises(ValueError):
            self.shell_promote(actor)

    def assert_shell_promotes(self, actor):
        self.assertEqual(
            self.shell_promote(actor)["retention_tier"], "Tier 3")


class TestDefects(B7Base):
    def test_r8_001_actor_two_pairs_anywhere_two_replacements(self):
        # person dressed by two transposed pairs standing at
        # nonadjacent positions, and by one adjacent pair with
        # one pair standing at a distance, with two letters
        # replaced in each form.
        for actor in (
                "nsqezp", "noxxep", "sozpex", "nszexp",
                "oznqpr", "soxpez", "epnzxr"):
            with self.subTest(actor=actor):
                self.assert_shell_refuses_person(actor)

    def test_r8_002_target_two_pairs_anywhere_two_replacements(self):
        for target in (
                "tneqkpzihc", "ctzcopkiqh", "cozctxhink"):
            with self.subTest(target=target):
                self.assertEqual(
                    mod14._resolve_word(target), "checkpoint")
                self.assertFalse(mod14.validate_operator_action(
                    {"kind": "delete", "target": target + " set",
                     "path": "other rule"}))
        # record dressed the same way, pairs at positions 0
        # and 5 and at positions 1 and 3, replacements at
        # positions 2 and 4.
        self.assertEqual(mod14._resolve_word("dozeqr"), "record")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "edit", "target": "sealed family dozeqr",
             "path": "other rule"}))

    def test_r8_005_actor_one_adjacent_pair_stands_as_itself(self):
        # person dressed by the edge pair at positions 0 and
        # 5, the adjacent pair at positions 3 and 4, and one
        # replacement at position 1: change total three.
        self.assertEqual(mod14._resolve_actor_word("nqrosp"), "nqrosp")
        self.assertEqual(mod14._normalise_actor("nqrosp"), "nqrosp")
        # The same form carried through the letter map, with
        # the Cyrillic o at position 3.
        cyrillic = "nqr\u043esp"
        self.assertEqual(mod14._normalise_actor(cyrillic), "nqrosp")
        # This pin asserts the MOD-14 reading. The shell flag
        # act hands the normalised actor to the MOD-10 act,
        # whose own limb of this row stands charged apart
        # from the MOD-14 limb cured here.

    def test_r8_005_target_one_adjacent_pair_stands_as_itself(self):
        # checkpoint dressed by the edge pair, one adjacent
        # pair, and one replacement stands as itself, and the
        # act on it stands allowed.
        self.assertEqual(
            mod14._resolve_word("thekcpqinc"), "thekcpqinc")
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "thekcpqinc set",
             "path": "other rule"}))
        # record dressed the same way no longer resolves as
        # record, and an edit on the sealed family form
        # stands allowed. At _resolve_word the form reads as
        # the unrelated word closed under the stated five
        # replacement form, the kind of unrelated reading
        # Red 3 recorded for drqzer in Finding 1.
        self.assertNotEqual(mod14._resolve_word("dqocrr"), "record")
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "sealed family dqocrr",
             "path": "other rule"}))


class TestControls(B7Base):
    def test_control_adjacent_two_pairs_two_replacements_actor(self):
        self.assert_shell_refuses_person("epqosz")
        self.assert_shell_refuses_person("epsrxx")

    def test_control_adjacent_two_pairs_two_replacements_target(self):
        self.assertEqual(mod14._resolve_word("hcekcpqizt"), "checkpoint")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "hcekcpqizt set",
             "path": "other rule"}))

    def test_control_two_adjacent_pairs_one_replacement_itself(self):
        # The completion cure standing: two adjacent pairs
        # with one replacement, change total three, stands
        # as itself and promotes.
        self.assertEqual(mod14._normalise_actor("eprosx"), "eprosx")
        self.assert_shell_promotes("eprosx")

    def test_control_r7_003_anywhere_pair_three_replacements(self):
        self.assert_shell_refuses_person("nqzjop")
        self.assert_shell_refuses_person("eprxxx")
        self.assertEqual(mod14._resolve_word("tqzjkpoinc"), "checkpoint")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "tqzjkpoinc set",
             "path": "other rule"}))

    def test_control_past_stated_form_actor_stands_as_itself(self):
        # One transposed pair with four replaced letters:
        # the replacement count stands past the stated
        # composition form of up to three replacements.
        self.assertEqual(mod14._normalise_actor("epxxxx"), "epxxxx")
        self.assert_shell_promotes("epxxxx")

    def test_control_past_stated_form_target_stands_as_itself(self):
        # Two transposed pairs with four replaced letters,
        # eight differing positions, past the stated form.
        self.assertEqual(
            mod14._resolve_word("tnzqxjoihc"), "tnzqxjoihc")
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": "tnzqxjoihc set",
             "path": "other rule"}))

    def test_control_plain_and_lawful_actors(self):
        self.assert_shell_refuses_person("person")
        self.assert_shell_promotes("program")
        self.assert_shell_promotes("alice")


if __name__ == "__main__":
    unittest.main()
