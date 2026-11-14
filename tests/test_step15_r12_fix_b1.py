"""Step 15 second run, fix wave 11 pins, Builder 1.

Pins for rows R11-001 and R11-002 under settlement S-3 of the
Round 11 register, proving the acts stated in Red 1 Findings
1 and 2 of design/steps/step-15-rerun-r11-red1.md.

Row R11-001: one shared folded letter map governs MOD-10 and
MOD-14 in the MOD-10 transliteration reading (pi as p, rho
as r, gamma as g, eta as e, nu as n, omega as o), so a folded
actor dress composed with plain replacements resolves to the
same party at both flag acts in both directions.

Row R11-002: an actor value that is stored text under limbs
2, 3, and 6 of the governing settlement (bytes, containers,
bytearray, and memoryview) stands read as that stored text
at both normalisers and at the person bar, and neither
normaliser passes such a dress through untouched. Other non
text actor forms stand as themselves.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14

PI = "\u03c0"
RHO = "\u03c1"
GAMMA = "\u03b3"
ETA = "\u03b7"
NU = "\u03bd"
OMEGA = "\u03c9"
SIGMA = "\u03c3"
OMICRON = "\u03bf"
ALPHA = "\u03b1"
MU = "\u03bc"

PERSON_DRESS_1 = PI + ETA + RHO + "qq" + NU
PERSON_DRESS_2 = PI + ETA + RHO + "xz" + NU
PERSON_DRESS_3 = PI + ETA + RHO + "q" + OMEGA + NU
PROGRAM_DRESS_1 = PI + RHO + "q" + GAMMA + RHO + "qm"
PROGRAM_DRESS_2 = PI + RHO + OMEGA + GAMMA + RHO + "qm"
GREEK_PERSON = PI + ETA + RHO + SIGMA + OMICRON + NU
GREEK_PROGRAM = PI + RHO + OMICRON + GAMMA + RHO + ALPHA + MU


class B1Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def core_record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def mod10_promote(self, actor):
        return mod10.apply_flag_evaluation(
            self.core_record(),
            outcome="promote", tier="Tier 2", actor=actor,
            inputs={"flag_conditions_fired": ["condition a"]})

    def mod14_promote(self, actor):
        return mod14.flag_evaluation(
            self.core_record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 2", actor=actor)


class TestR11001SharedFoldedLetterMap(B1Base):
    SIX = [(PI, "p"), (RHO, "r"), (GAMMA, "g"),
           (ETA, "e"), (NU, "n"), (OMEGA, "o")]

    def test_six_letters_read_the_mod10_way_at_mod14(self):
        for letter, latin in self.SIX:
            with self.subTest(letter=repr(letter)):
                self.assertEqual(mod14._LETTER_MAP[letter], latin)
                self.assertEqual(
                    mod14._canonicalise_text(letter), latin)
                self.assertEqual(
                    mod10._canonical_text(
                        letter, mod10._TRANSLITERATION_MAP), latin)

    def test_person_dresses_normalise_person_at_both(self):
        for dress in (PERSON_DRESS_1, PERSON_DRESS_2,
                      PERSON_DRESS_3, PERSON_DRESS_1.upper()):
            with self.subTest(dress=dress):
                self.assertEqual(
                    mod10._normalised_actor(dress), "person")
                self.assertEqual(
                    mod14._normalise_actor(dress), "person")

    def test_person_dresses_barred_at_both_flag_acts(self):
        for dress in (PERSON_DRESS_1, PERSON_DRESS_2,
                      PERSON_DRESS_3, PERSON_DRESS_1.upper()):
            with self.subTest(dress=dress):
                with self.assertRaises(ValueError):
                    self.mod10_promote(dress)
                with self.assertRaises(ValueError):
                    self.mod14_promote(dress)

    def test_program_dresses_normalise_program_at_both(self):
        for dress in (PROGRAM_DRESS_1, PROGRAM_DRESS_2):
            with self.subTest(dress=dress):
                self.assertEqual(
                    mod10._normalised_actor(dress), "program")
                self.assertEqual(
                    mod14._normalise_actor(dress), "program")

    def test_program_dresses_effected_at_both_flag_acts(self):
        for dress in (PROGRAM_DRESS_1, PROGRAM_DRESS_2):
            with self.subTest(dress=dress):
                for act in (self.mod10_promote, self.mod14_promote):
                    result = act(dress)
                    self.assertEqual(
                        result["retention_tier"], "Tier 2")
                    self.assertEqual(
                        result["flag_evaluation"]["actor"],
                        "program")

    def test_pure_greek_controls_agree_at_both_acts(self):
        self.assertEqual(
            mod10._normalised_actor(GREEK_PERSON), "person")
        self.assertEqual(
            mod14._normalise_actor(GREEK_PERSON), "person")
        with self.assertRaises(ValueError):
            self.mod10_promote(GREEK_PERSON)
        with self.assertRaises(ValueError):
            self.mod14_promote(GREEK_PERSON)
        self.assertEqual(
            mod10._normalised_actor(GREEK_PROGRAM), "program")
        self.assertEqual(
            mod14._normalise_actor(GREEK_PROGRAM), "program")
        for act in (self.mod10_promote, self.mod14_promote):
            result = act(GREEK_PROGRAM)
            self.assertEqual(result["retention_tier"], "Tier 2")
            self.assertEqual(
                result["flag_evaluation"]["actor"], "program")


class TestR11002StoredTextActorDresses(B1Base):
    PERSON_DRESSES = [
        b"person",
        bytearray(b"person"),
        memoryview(b"person"),
        ["person"],
        ("person",),
        {"person"},
    ]

    def test_person_dresses_normalise_person_at_both(self):
        for dress in self.PERSON_DRESSES:
            with self.subTest(dress=repr(dress)):
                self.assertEqual(
                    mod10._normalised_actor(dress), "person")
                self.assertEqual(
                    mod14._normalise_actor(dress), "person")

    def test_person_dresses_barred_at_both_flag_acts(self):
        for dress in self.PERSON_DRESSES:
            with self.subTest(dress=repr(dress)):
                with self.assertRaises(ValueError):
                    self.mod10_promote(dress)
                with self.assertRaises(ValueError):
                    self.mod14_promote(dress)

    def test_bytes_spelling_variants_read_as_person(self):
        for dress in (b"PERSON", b"the person", b"p3r50n"):
            with self.subTest(dress=repr(dress)):
                self.assertEqual(
                    mod10._normalised_actor(dress), "person")
                self.assertEqual(
                    mod14._normalise_actor(dress), "person")
                with self.assertRaises(ValueError):
                    self.mod10_promote(dress)
                with self.assertRaises(ValueError):
                    self.mod14_promote(dress)

    def test_bytes_program_dress_effected_naming_program(self):
        for dress in (b"program", bytearray(b"program"),
                      memoryview(b"program"), ["program"]):
            with self.subTest(dress=repr(dress)):
                self.assertEqual(
                    mod10._normalised_actor(dress), "program")
                self.assertEqual(
                    mod14._normalise_actor(dress), "program")
                for act in (self.mod10_promote,
                            self.mod14_promote):
                    result = act(dress)
                    self.assertEqual(
                        result["retention_tier"], "Tier 2")
                    self.assertEqual(
                        result["flag_evaluation"]["actor"],
                        "program")

    def test_container_parts_in_bytes_dress_read_as_person(self):
        for dress in ([b"person"], (bytearray(b"person"),),
                      [memoryview(b"person")]):
            with self.subTest(dress=repr(dress)):
                self.assertEqual(
                    mod10._normalised_actor(dress), "person")
                self.assertEqual(
                    mod14._normalise_actor(dress), "person")
                with self.assertRaises(ValueError):
                    self.mod14_promote(dress)

    def test_joined_container_parts_read_as_one_actor(self):
        for dress in (["per", "son"], ("pro", "gram"),
                      [b"per", b"son"], [["person"]]):
            with self.subTest(dress=repr(dress)):
                expected = (
                    "person" if "son" in repr(dress)
                    or "person" in repr(dress) else "program")
                self.assertEqual(
                    mod10._normalised_actor(dress), expected)
                self.assertEqual(
                    mod14._normalise_actor(dress), expected)

    def test_other_non_text_forms_stand_as_themselves(self):
        for form in (123, 5.5, None, [123], {"a": 1}):
            with self.subTest(form=repr(form)):
                self.assertEqual(
                    mod10._normalised_actor(form), form)
                self.assertEqual(
                    mod14._normalise_actor(form), form)

    def test_plain_str_controls_stand(self):
        self.assertEqual(mod10._normalised_actor("person"),
                         "person")
        self.assertEqual(mod14._normalise_actor("person"),
                         "person")
        with self.assertRaises(ValueError):
            self.mod10_promote("person")
        with self.assertRaises(ValueError):
            self.mod14_promote("person")
        result = self.mod14_promote("program")
        self.assertEqual(result["flag_evaluation"]["actor"],
                         "program")


if __name__ == "__main__":
    unittest.main()
