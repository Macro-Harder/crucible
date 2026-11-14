"""Step 15 second run, fix wave 7, seat 9. MOD-12 pins.

Pins for register rows R7-008, R7-021, and R7-023. Each defect
pin was written before its cure and run against the unmodified
module; the counts stand recorded in the paper for this seat.
Lawful controls pass on the unmodified module and on the cured
module alike.
"""

import unittest

from crucible import mod12


class TestR7008DecomposedReadings(unittest.TestCase):
    """Row R7-008: the fold reads decomposed and case folded
    characters through its letter maps."""

    AMOUNT_CASES = (
        "a\u00b5ount",
        "\u0386mount",
        "am\u038cunt",
        "\u04d0mount",
        "amo\u04eent",
        "am\u01feunt",
        "amou\u1d51t",
        "\uff20mount",
        "amoun\u207a",
    )
    CURRENCY_CASES = (
        "curr\u0388ncy",
        "curr\u0400ncy",
        "cu\u03f1rency",
        "cu\u1d68rency",
        "currenc\u04f9",
        "currenc\u03cb",
    )
    ANCHOR_CASES = (
        "anchor_\u03f2cenario_values",
        "anc\u210for_scenario_values",
        "anchor_\uff04cenario_values",
    )
    MARKER_CASES = (
        "real\u00b5oney",
        "rea\u2048money",
    )

    # Two amount cases stand out of the canonical equality pin:
    # the Cyrillic u with macron reads canonically as y, with its
    # u reading standing in the alt readings, and the superscript
    # plus sign reads as t through the alt readings only. Both
    # names stand pinned at the match acts below.
    CANONICAL_AMOUNT_CASES = (
        "a\u00b5ount",
        "\u0386mount",
        "am\u038cunt",
        "\u04d0mount",
        "am\u01feunt",
        "amou\u1d51t",
        "\uff20mount",
    )

    def test_canonicalised_name_reads_decomposed_forms(self):
        for key in self.CANONICAL_AMOUNT_CASES:
            with self.subTest(key=key):
                self.assertEqual(
                    mod12._canonicalised_name(key), "amount")

    def test_canonicalise_mapped_reads_decomposed_forms(self):
        self.assertEqual(
            mod12._canonicalise_mapped("a\u00b5ount"), "amount")
        self.assertEqual(
            mod12._canonicalise_mapped("\u0386mount"), "amount")
        self.assertEqual(
            mod12._canonicalise_mapped("cu\u03f1rency"), "currency")

    def test_amount_names_match(self):
        for key in self.AMOUNT_CASES:
            with self.subTest(key=key):
                self.assertTrue(
                    mod12._folded_name_matches(key, "amount"))

    def test_currency_names_match(self):
        for key in self.CURRENCY_CASES:
            with self.subTest(key=key):
                self.assertTrue(
                    mod12._folded_name_matches(key, "currency"))

    def test_anchor_names_match(self):
        for key in self.ANCHOR_CASES:
            with self.subTest(key=key):
                self.assertTrue(mod12._folded_name_matches(
                    key, mod12._ANCHOR_VALUES_FIELD_FOLDED))

    def test_marker_names_carry(self):
        for key in self.MARKER_CASES:
            with self.subTest(key=key):
                self.assertTrue(mod12._folded_name_carries(
                    key, mod12._MONEY_MARKER_FOLDED))

    def test_combined_kinds_in_one_name(self):
        key = "4\u00b5\u038c\u0443\u043dt"
        self.assertTrue(mod12._folded_name_matches(key, "amount"))

    def test_lawful_controls_stand_admitted(self):
        self.assertFalse(mod12._folded_name_matches("amounx", "amount"))
        self.assertFalse(
            mod12._folded_name_matches("a\u00b5ountx", "amount"))
        self.assertFalse(mod12._folded_name_carries(
            "rea\u00b5oneyx", mod12._MONEY_MARKER_FOLDED))
        self.assertEqual(mod12._canonicalised_name("amount"), "amount")
        self.assertEqual(
            mod12._canonicalised_name("currency"), "currency")


class TestR7008PublicActs(unittest.TestCase):
    """Row R7-008 at the public acts of the module."""

    def _record_with_amount_key(self, key):
        return {
            "run_class": "screening",
            "seed_domain": "screening",
            "payload": {key: 5, "currency": "usd"},
        }

    def test_dressed_amount_pair_stands_barred(self):
        for key in ("a\u00b5ount", "am\u038cunt"):
            with self.subTest(key=key):
                record = self._record_with_amount_key(key)
                self.assertTrue(
                    mod12._carries_barred_money_value(record))
                self.assertFalse(mod12.validate_run_record(record))

    def test_dressed_anchor_key_count_stands_judged(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "anchor_\u03f2cenario_values": [1, 2],
        }
        self.assertFalse(mod12.validate_run_record(record))

    def test_dressed_anchor_key_with_three_values_passes(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "anchor_\u03f2cenario_values": [1, 2, 3],
        }
        self.assertTrue(mod12.validate_run_record(record))

    def test_plain_amount_pair_control_stands_barred(self):
        record = self._record_with_amount_key("amount")
        self.assertTrue(mod12._carries_barred_money_value(record))
        self.assertFalse(mod12.validate_run_record(record))


class TestR7021ThetaReadings(unittest.TestCase):
    """Row R7-021: the theta t reading and its capital and
    symbol forms stand recorded in the fold."""

    THETA_FORMS = ("\u03b8", "\u0398", "\u03d1", "\u03f4")

    def test_theta_amount_keys_match(self):
        for form in self.THETA_FORMS:
            with self.subTest(form=form):
                self.assertTrue(mod12._folded_name_matches(
                    "amoun" + form, "amount"))

    def test_theta_amount_keys_fold_to_amount(self):
        for form in self.THETA_FORMS:
            with self.subTest(form=form):
                self.assertEqual(
                    mod12._folded_money_key("amoun" + form), "amount")

    def test_theta_amount_pair_stands_barred(self):
        for form in self.THETA_FORMS:
            with self.subTest(form=form):
                record = {
                    "run_class": "screening",
                    "seed_domain": "screening",
                    "payload": {"amoun" + form: 5, "currency": "usd"},
                }
                self.assertTrue(
                    mod12._carries_barred_money_value(record))
                self.assertFalse(mod12.validate_run_record(record))

    def test_theta_combined_form_matches(self):
        key = "4\u043c0\u0443\u043d\u03b8"
        self.assertTrue(mod12._folded_name_matches(key, "amount"))

    def test_theta_th_reading_stands_preserved(self):
        self.assertIn(
            "amounth", mod12._folded_money_variants("amoun\u03b8"))

    def test_theta_lawful_control_stands_admitted(self):
        self.assertFalse(
            mod12._folded_name_matches("amoun\u03b8x", "amount"))


class TestR7023FreezeIdentity(unittest.TestCase):
    """Row R7-023: the set, frozenset, and tuple branches of
    the copy act carry memo entries in the stated form."""

    def test_shared_set_stands_as_one_part(self):
        shared = {1, 2}
        frozen = mod12._freeze([shared, shared])
        self.assertIs(frozen[0], frozen[1])
        self.assertEqual(frozen[0], shared)

    def test_shared_set_in_dict_stands_as_one_part(self):
        shared = {3}
        frozen = mod12._freeze({"a": shared, "b": shared})
        self.assertIs(frozen["a"], frozen["b"])

    def test_shared_frozenset_stands_as_one_part(self):
        shared = frozenset((1, 2))
        frozen = mod12._freeze([shared, shared])
        self.assertIs(frozen[0], frozen[1])
        self.assertEqual(frozen[0], shared)

    def test_cyclic_tuple_through_list_stands_as_one_part(self):
        inner = []
        cycle = (inner,)
        inner.append(cycle)
        frozen = mod12._freeze(cycle)
        self.assertIs(frozen[0][0], frozen)

    def test_cyclic_tuple_through_dict_stands_as_one_part(self):
        holder = {}
        cycle = (holder,)
        holder["self"] = cycle
        frozen = mod12._freeze(cycle)
        self.assertIs(frozen[0]["self"], frozen)

    def test_frozenset_shared_inside_a_tuple_cycle(self):
        shared = frozenset((7,))
        inner = []
        cycle = (inner, shared)
        inner.append(cycle)
        frozen = mod12._freeze([cycle, shared])
        self.assertIs(frozen[0][0][0], frozen[0])
        self.assertIs(frozen[0][1], frozen[1])

    def test_shared_tuple_control_stands_as_one_part(self):
        shared = (1, 2)
        frozen = mod12._freeze([shared, shared])
        self.assertIs(frozen[0], frozen[1])

    def test_shared_dict_and_list_controls_stand_as_one_part(self):
        shared_dict = {"x": 1}
        shared_list = [1]
        frozen = mod12._freeze(
            [shared_dict, shared_dict, shared_list, shared_list])
        self.assertIs(frozen[0], frozen[1])
        self.assertIs(frozen[2], frozen[3])

    def test_copy_contents_stand_unchanged(self):
        value = {"a": [{1, 2}, frozenset((3,)), (4, 5)], "b": "text"}
        frozen = mod12._freeze(value)
        self.assertEqual(frozen, value)
        self.assertIsNot(frozen, value)


if __name__ == "__main__":
    unittest.main()
