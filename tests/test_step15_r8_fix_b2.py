"""Step 15 rerun fix wave 7 pins, Builder 2, rows R7-001 to R7-003.

Row R7-001: flag actor normalisers at MOD-10 and MOD-14, actor
forms mixing added letters with replacements or a transposition.
Row R7-002: MOD-14 target resolver, protected target words
carrying added letters with replacements.
Row R7-003: a transposed pair at a word edges, composed with
three replacements, at both flag acts and at the target
resolver.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14


def actor_form(added, replacements):
    letters = list("person")
    for index, char in replacements:
        letters[index] = char
    return "".join(letters) + "x" * added


def target_form(added, replacements):
    letters = list("checkpoint")
    for index, char in replacements:
        letters[index] = char
    return "".join(letters) + "x" * added


ACTOR_MIXED = (
    actor_form(1, ((0, "q"),)),
    actor_form(1, ((0, "q"), (1, "z"))),
    actor_form(2, ((0, "q"),)),
    actor_form(3, ((0, "q"),)),
    actor_form(3, ((0, "q"), (1, "z"))),
    actor_form(4, ((0, "q"), (1, "z"))),
    actor_form(6, ((0, "q"),)),
    actor_form(5, ((0, "q"), (1, "z"))),
)

TARGET_MIXED = (
    target_form(1, ((0, "q"),)),
    target_form(1, ((0, "q"), (1, "z"))),
    target_form(2, ((0, "q"),)),
    target_form(3, ((0, "q"),)),
    target_form(3, ((0, "q"), (1, "z"))),
    target_form(4, ((0, "q"), (1, "z"))),
    target_form(6, ((0, "q"),)),
    target_form(5, ((0, "q"), (1, "z"))),
)


class FlagBase(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def core_promote(self, actor):
        return mod10.apply_flag_evaluation(
            self.record(), outcome="promote", tier="Tier 2",
            actor=actor,
            inputs={"flag_conditions_fired": ["condition a"]})

    def shell_promote(self, actor):
        return mod14.flag_evaluation(
            self.record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3", actor=actor)

    def assert_both_refuse_person(self, actor):
        self.assertEqual(mod10._normalised_actor(actor), "person")
        self.assertEqual(mod14._normalise_actor(actor), "person")
        with self.assertRaises(ValueError):
            self.core_promote(actor)
        with self.assertRaises(ValueError):
            self.shell_promote(actor)

    def assert_both_promote(self, actor):
        self.assertEqual(
            self.core_promote(actor)["retention_tier"], "Tier 2")
        self.assertEqual(
            self.shell_promote(actor)["retention_tier"], "Tier 3")


class TestR7001MixedActorForms(FlagBase):
    def test_mixed_forms_resolve_in_agreement(self):
        for actor in ACTOR_MIXED:
            with self.subTest(actor=actor):
                self.assertEqual(
                    mod10._resolve_actor_word(actor), "person")
                self.assertEqual(
                    mod14._resolve_actor_word(actor), "person")
                self.assertEqual(
                    mod10._normalised_actor(actor), "person")
                self.assertEqual(
                    mod14._normalise_actor(actor), "person")

    def test_mixed_forms_refused_at_both_flag_acts(self):
        for actor in ACTOR_MIXED:
            with self.subTest(actor=actor):
                self.assert_both_refuse_person(actor)

    def test_charged_six_added_one_replacement(self):
        self.assert_both_refuse_person("qersonxxxxxx")

    def test_charged_five_added_two_replacements(self):
        self.assert_both_refuse_person("qzrsonxxxxx")

    def test_total_two_form(self):
        self.assert_both_refuse_person("qersonx")

    def test_added_with_adjacent_transposition(self):
        self.assert_both_refuse_person("pesronx")

    def test_added_with_edge_transposition(self):
        self.assert_both_refuse_person("nersopx")


class TestR7001PureBoundControls(FlagBase):
    def test_seven_added_letters_still_refused(self):
        self.assert_both_refuse_person("personxxxxxxx")

    def test_five_replacements_still_refused(self):
        self.assert_both_refuse_person("qzxvjn")

    def test_eight_added_letters_still_promotes(self):
        self.assertEqual(
            mod10._normalised_actor("personxxxxxxxx"),
            "personxxxxxxxx")
        self.assertEqual(
            mod14._normalise_actor("personxxxxxxxx"),
            "personxxxxxxxx")
        self.assert_both_promote("personxxxxxxxx")

    def test_six_replacements_still_promotes(self):
        self.assertEqual(mod10._normalised_actor("xxxxxo"), "xxxxxo")
        self.assertEqual(mod14._normalise_actor("xxxxxo"), "xxxxxo")
        self.assert_both_promote("xxxxxo")

    def test_boundary_eight_added_six_replacements_promotes(self):
        actor = "qzxvjq" + "x" * 8
        self.assertEqual(mod10._normalised_actor(actor), actor)
        self.assertEqual(mod14._normalise_actor(actor), actor)
        self.assert_both_promote(actor)

    def test_lawful_program_promotes(self):
        self.assert_both_promote("program")

    def test_lawful_alice_promotes(self):
        self.assert_both_promote("alice")

    def test_plain_person_still_refused(self):
        self.assert_both_refuse_person("person")


class TestR7002MixedTargetForms(unittest.TestCase):
    def test_mixed_forms_resolve(self):
        for word in TARGET_MIXED:
            with self.subTest(word=word):
                self.assertEqual(mod14._resolve_word(word), "checkpoint")

    def test_mixed_forms_barred_at_validate_operator_action(self):
        for word in TARGET_MIXED:
            with self.subTest(word=word):
                self.assertFalse(mod14.validate_operator_action(
                    {"kind": "delete",
                     "target": word + " set",
                     "path": "other rule"}))

    def test_charged_six_added_one_replacement(self):
        self.assertEqual(
            mod14._resolve_word("qheckpointxxxxxx"), "checkpoint")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "qheckpointxxxxxx set",
             "path": "other rule"}))

    def test_charged_five_added_two_replacements(self):
        self.assertEqual(
            mod14._resolve_word("qzeckpointxxxxx"), "checkpoint")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "qzeckpointxxxxx set",
             "path": "other rule"}))

    def test_total_two_form(self):
        self.assertEqual(mod14._resolve_word("qheckpointx"), "checkpoint")

    def test_plain_target_control_still_barred(self):
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "checkpoint set",
             "path": "other rule"}))

    def test_seven_added_pure_control_still_resolves(self):
        self.assertEqual(
            mod14._resolve_word("checkpointxxxxxxx"), "checkpoint")

    def test_read_on_mixed_target_control_still_allowed(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "qheckpointx set",
             "path": "other rule"}))


class TestR7003EdgeTranspositionWithReplacements(FlagBase):
    def test_actor_edge_pair_with_three_replacements_resolves(self):
        self.assertEqual(mod10._resolve_actor_word("nqzjop"), "person")
        self.assertEqual(mod14._resolve_actor_word("nqzjop"), "person")

    def test_actor_edge_pair_refused_at_both_flag_acts(self):
        self.assert_both_refuse_person("nqzjop")

    def test_target_edge_pair_with_three_replacements_resolves(self):
        self.assertEqual(mod14._resolve_word("tqzjkpoinc"), "checkpoint")

    def test_target_edge_pair_barred_at_validate_operator_action(self):
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "tqzjkpoinc set",
             "path": "other rule"}))

    def test_target_inner_pair_with_three_replacements_resolves(self):
        self.assertEqual(mod14._resolve_word("chpqzejint"), "checkpoint")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "chpqzejint set",
             "path": "other rule"}))

    def test_plain_edge_transposition_control_still_resolves(self):
        self.assertEqual(mod14._resolve_word("tqzjkpoinc".replace(
            "qzj", "hec")), "checkpoint")


if __name__ == "__main__":
    unittest.main()
