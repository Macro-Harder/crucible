"""Step 17 fix wave 6, Slice 4 defect tests (FW6-04, ruling T17R5-05).

Family: the unbounded refusal echo at fresh doors, and the bare
unexpected keyword escape at the mod02 make_derivation_input door.
Filings: Orange 4 T17R5-O4-01 (mod01 build_sweep_point and
build_run_record unknown field echo) and T17R5-O4-02 (mod12
start_run and start_sweep extra keyword carriage, with the mod02
make_derivation_input bare TypeError).

Bound the cure states, door by door, in the FW4-10 and FW5-08
form: a handed value stands rendered at 120 characters beside a
length statement. For one handed name of 100,000 characters, a
cured refusal message, and each cured refusal carriage field,
stands at 600 characters or fewer in total, the fixed refusal
text of the door included. The defect tests below state that
bound and the handing scale of the filings: refusal messages at
100,118 characters, carriages at 100,004 and 100,154 characters,
and the bare TypeError at 100,061 characters, each on a handed
name of 100,000 repetitions of one character. Those counts stand
as the measure of the cure owed, never as the verdict of a test:
each defect test fails on the uncured tree because the telling
or carriage stands past the 600 character bound, or because a
bare TypeError escapes, and passes on the cured tree.

Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

from crucible import mod01, mod02, mod12

HUGE_NAME = "h" * 100000
BOUND = 600


def carriage_len(value):
    return len(str(value))


class TestFW604Mod01UnknownField(unittest.TestCase):
    """mod01 build_sweep_point and build_run_record, unknown field."""

    def test_defect_build_sweep_point_huge_unknown_field(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_sweep_point(**{HUGE_NAME: 1})
        message = str(caught.exception)
        self.assertLessEqual(len(message), BOUND)
        self.assertIn("bounded rendering", message)
        self.assertIn("100000", message)
        self.assertIn("no record stands built", message)

    def test_defect_build_run_record_huge_unknown_field(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_run_record(**{HUGE_NAME: 1})
        message = str(caught.exception)
        self.assertLessEqual(len(message), BOUND)
        self.assertIn("bounded rendering", message)
        self.assertIn("100000", message)
        self.assertIn("no record stands built", message)

    def test_control_build_sweep_point_small_unknown_field(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_sweep_point(nope=1)
        message = str(caught.exception)
        self.assertEqual(len(message), 122)
        self.assertIn("unknown field for Form 2: nope", message)

    def test_control_build_run_record_small_unknown_field(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_run_record(nope=1)
        message = str(caught.exception)
        self.assertEqual(len(message), 122)
        self.assertIn("unknown field for Form 4: nope", message)

    def test_control_build_sweep_point_served_whole(self):
        record = mod01.build_sweep_point()
        self.assertIsInstance(record, dict)


class TestFW604Mod12ExtraKeywordCarriage(unittest.TestCase):
    """mod12 start_run and start_sweep, extra keyword carriage."""

    def check_carriage(self, record):
        self.assertIn("unexpected_keyword_handings", record)
        self.assertIn("extra_handing_note", record)
        self.assertLessEqual(
            carriage_len(record["unexpected_keyword_handings"]), BOUND)
        self.assertLessEqual(len(record["extra_handing_note"]), BOUND)
        self.assertIn(
            "bounded rendering",
            str(record["unexpected_keyword_handings"]))
        self.assertIn("bounded rendering", record["extra_handing_note"])
        self.assertIn("100000", record["extra_handing_note"])

    def test_defect_start_run_huge_extra_keyword(self):
        record = mod12.start_run(**{HUGE_NAME: 1})
        self.check_carriage(record)

    def test_defect_start_run_full_huge_extra_keyword(self):
        record = mod12.start_run(
            run_class="screening", family_id="fam-1", **{HUGE_NAME: 1})
        self.check_carriage(record)
        self.assertFalse(record.get("seed_drawn", False))

    def test_defect_start_sweep_huge_extra_keyword(self):
        record = mod12.start_sweep(family_id="fam-1", **{HUGE_NAME: 1})
        self.check_carriage(record)

    def test_control_start_run_small_extra_keyword(self):
        record = mod12.start_run(
            run_class="screening", family_id="fam-1", nope=1)
        self.assertEqual(record["unexpected_keyword_handings"], ["nope"])
        self.assertIn("nope", record["extra_handing_note"])
        self.assertLessEqual(len(record["extra_handing_note"]), BOUND)

    def test_control_start_sweep_small_extra_keyword(self):
        record = mod12.start_sweep(family_id="fam-1", nope=1)
        self.assertEqual(record["unexpected_keyword_handings"], ["nope"])
        self.assertIn("nope", record["extra_handing_note"])


class TestFW604Mod02MakeDerivationInput(unittest.TestCase):
    """mod02 make_derivation_input, unexpected keyword handing."""

    def test_defect_make_derivation_input_huge_keyword(self):
        with self.assertRaises(ValueError) as caught:
            mod02.make_derivation_input(**{HUGE_NAME: 1})
        self.assertNotIsInstance(caught.exception, TypeError)
        message = str(caught.exception)
        self.assertLessEqual(len(message), BOUND)
        self.assertIn("make_derivation_input", message)
        self.assertIn("no derivation input stands built", message)
        self.assertIn("bounded rendering", message)
        self.assertIn("100000", message)

    def test_defect_make_derivation_input_small_keyword(self):
        with self.assertRaises(ValueError) as caught:
            mod02.make_derivation_input(domain="screening", nope=1)
        self.assertNotIsInstance(caught.exception, TypeError)
        message = str(caught.exception)
        self.assertIn("make_derivation_input", message)
        self.assertIn("nope", message)
        self.assertIn("no derivation input stands built", message)
        self.assertLessEqual(len(message), BOUND)

    def test_control_make_derivation_input_served_whole(self):
        built = mod02.make_derivation_input(domain="screening")
        self.assertEqual(built["domain"], "screening")

    def test_control_make_derivation_input_domain_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod02.make_derivation_input(domain="bogus")
        self.assertIn(
            "domain outside the two value vocabulary",
            str(caught.exception))


if __name__ == "__main__":
    unittest.main()
