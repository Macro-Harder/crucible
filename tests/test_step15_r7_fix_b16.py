"""Step 15 rerun fix wave 6 completion pins, row R6-005 core limb.

Pins for the core flag actor normaliser standing short of the
shell normaliser on the merged tree: the shell resolver reads a
person actor carrying seven added letters and a person actor
carrying five replacements as the plain actor it names, while
the core resolver left both dresses as themselves, so a
promotion stood effected at the core act only. Control pins
cover the neighbouring totals on both sides of each bound and
the lawful actor forms. Values are simulated and test values
only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14


class B16Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def core_record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def core_promote(self, actor):
        return mod10.apply_flag_evaluation(
            self.core_record(), outcome="promote", tier="Tier 2",
            actor=actor,
            inputs={"flag_conditions_fired": ["condition a"]})

    def shell_promote(self, actor):
        return mod14.flag_evaluation(
            self.core_record(),
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

    def assert_both_read_as_themselves(self, actor):
        self.assertEqual(mod10._normalised_actor(actor), actor)
        self.assertEqual(mod14._normalise_actor(actor), actor)
        self.assert_both_promote(actor)


class TestSevenAddedLettersDefect(B16Base):
    def test_suffix_form_normalises_at_both(self):
        self.assertEqual(
            mod10._normalised_actor("personxxxxxxx"), "person")
        self.assertEqual(
            mod14._normalise_actor("personxxxxxxx"), "person")

    def test_suffix_form_refused_at_both_acts(self):
        self.assert_both_refuse_person("personxxxxxxx")

    def test_interspersed_form_normalises_at_both(self):
        self.assertEqual(
            mod10._normalised_actor("pxexrxsxoxnxx"), "person")
        self.assertEqual(
            mod14._normalise_actor("pxexrxsxoxnxx"), "person")

    def test_interspersed_form_refused_at_both_acts(self):
        self.assert_both_refuse_person("pxexrxsxoxnxx")


class TestFiveReplacementsDefect(B16Base):
    def test_first_form_normalises_at_both(self):
        self.assertEqual(mod10._normalised_actor("qzxvjn"), "person")
        self.assertEqual(mod14._normalise_actor("qzxvjn"), "person")

    def test_first_form_refused_at_both_acts(self):
        self.assert_both_refuse_person("qzxvjn")

    def test_second_form_normalises_at_both(self):
        self.assertEqual(mod10._normalised_actor("xxxxxn"), "person")
        self.assertEqual(mod14._normalise_actor("xxxxxn"), "person")

    def test_second_form_refused_at_both_acts(self):
        self.assert_both_refuse_person("xxxxxn")


class TestNeighbouringControls(B16Base):
    def test_six_added_letters_suffix_refused_at_both(self):
        self.assert_both_refuse_person("personxxxxxx")

    def test_six_added_letters_interspersed_refused_at_both(self):
        self.assert_both_refuse_person("pxexrxsxoxnx")

    def test_composed_five_differing_refused_at_both(self):
        self.assert_both_refuse_person("eprxxx")

    def test_four_replacements_refused_at_both(self):
        self.assert_both_refuse_person("qzxvon")

    def test_eight_added_letters_promotes_at_both(self):
        self.assert_both_read_as_themselves("personxxxxxxxx")

    def test_six_replacements_promotes_at_both(self):
        self.assert_both_read_as_themselves("xxxxxo")


class TestLawfulControls(B16Base):
    def test_plain_person_resolves_and_refused_at_both(self):
        self.assert_both_refuse_person("person")

    def test_alice_promotes_at_both_acts(self):
        self.assert_both_promote("alice")

    def test_program_promotes_at_both_acts(self):
        self.assert_both_promote("program")


if __name__ == "__main__":
    unittest.main()
