"""Step 15, second run, fix wave 4 pins. MOD-08 rows R4-021
and R4-030 limb d.

R4-021: the MOD-08 folded barred reading carries the shared
sister reading for the Cherokee letters, the Coptic letters,
the section sign as s, and the plus sign as t, so membership
and ground_truth keys dressed in those letters stand barred
at MOD-08.

R4-030 limb d: the MOD-08 undirected copy tests its depth
bound on containers only, on the stated basis of R3-056, so a
chain of 101 containers stands within the bound and a chain
of 102 containers stands past it.

No detection score is reported as a pass or as a fail in this
file: barred readings, acceptance readings, and copy readings
only.
"""
import unittest

from crucible import mod08


def record_with_nested_key(key):
    return {
        "agent_identifier": "agent-b6",
        "day": 1,
        "feature_values": {"activity": 2},
        "records_for_agent_and_day": [{"wrap": {key: 1}}],
    }


def list_chain(depth, leaf="leaf"):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def tuple_chain(depth, leaf="leaf"):
    value = leaf
    for _ in range(depth):
        value = (value,)
    return value


def dict_chain(depth, leaf="leaf"):
    value = leaf
    for _ in range(depth):
        value = {"k": value}
    return value


def dress(word, index, glyph):
    return word[:index] + glyph + word[index + 1:]


MEMBERSHIP = "membership"
GROUND_TRUTH = "ground_truth"

CHEROKEE_COPTIC_BY_LETTER = {
    "m": ("\u13b7", "\uab87", "\u2c99", "\u2c98"),
    "e": ("\u13ac", "\uab7c", "\u2c89", "\u2c88"),
    "r": ("\u13d2", "\uaba2", "\u2ca3", "\u2ca2"),
    "o": ("\u13be", "\uab8e", "\u2c9f", "\u2c9e"),
    "n": ("\u13c1", "\uab91", "\u2c9b", "\u2c9a"),
    "a": ("\u13aa", "\uab7a", "\u2c81", "\u2c80"),
    "l": ("\u13de", "\uabae", "\u2c97", "\u2c96"),
    "y": ("\u13ef", "\uabbf", "\u2ca9", "\u2ca8"),
}


def miss_probe_keys():
    keys = []
    for word in (MEMBERSHIP, GROUND_TRUTH):
        for index, letter in enumerate(word):
            glyphs = []
            if letter in CHEROKEE_COPTIC_BY_LETTER:
                glyphs = list(CHEROKEE_COPTIC_BY_LETTER[letter])
            if letter == "s":
                glyphs = ["\u00a7"]
            if letter == "t":
                glyphs = ["+"]
            for glyph in glyphs:
                keys.append(dress(word, index, glyph))
    return tuple(keys)


MISS_KEYS = miss_probe_keys()

NAMED_KEYS = (
    dress(MEMBERSHIP, 6, "\u00a7"),
    dress(GROUND_TRUTH, 7, "+"),
    dress(GROUND_TRUTH, 10, "+"),
    dress(MEMBERSHIP, 0, "\u13b7"),
    dress(MEMBERSHIP, 1, "\u13ac"),
    dress(MEMBERSHIP, 0, "\u2c98"),
    dress(MEMBERSHIP, 1, "\u2c89"),
    dress(MEMBERSHIP, 5, "\uaba2"),
    dress(GROUND_TRUTH, 4, "\u2c9b"),
    dress(GROUND_TRUTH, 2, "\u13be"),
)

EXTRA_SISTER_KEYS = (
    dress("canary", 1, "\u13aa"),
    dress("canary", 1, "\uab7a"),
    dress("canary", 1, "\u2c81"),
    dress("canary", 1, "\u2c80"),
    dress("canary", 5, "\u13ef"),
    dress("canary", 5, "\uabbf"),
    dress("canary", 5, "\u2ca9"),
    dress("canary", 5, "\u2ca8"),
    dress("label", 0, "\u13de"),
    dress("label", 0, "\uabae"),
    dress("label", 0, "\u2c97"),
    dress("label", 0, "\u2c96"),
)

PLAIN_BARRED_KEYS = ("membership", "ground_truth", "canary", "label")

CLEAN_KEYS = ("activity", "notes")


class TestR4021MissProbeSet(unittest.TestCase):

    def test_miss_probe_set_has_39_keys(self):
        self.assertEqual(len(MISS_KEYS), 39)
        self.assertEqual(len(set(MISS_KEYS)), 39)

    def test_each_miss_key_is_barred_at_mod08(self):
        for key in MISS_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_acceptance_refuses_each_miss_key(self):
        for key in MISS_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(
                        record_with_nested_key(key))

    def test_named_register_forms_are_barred(self):
        for key in NAMED_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(
                        record_with_nested_key(key))

    def test_extra_sister_classes_for_a_l_and_y_are_barred(self):
        for key in EXTRA_SISTER_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_maps_carry_the_four_classes(self):
        for letter_map in (mod08._HOMOGLYPH_MAP,
                           mod08._TRANSLITERATION_MAP):
            for glyphs in CHEROKEE_COPTIC_BY_LETTER.values():
                for glyph in glyphs:
                    with self.subTest(glyph=glyph):
                        self.assertIn(glyph.lower(), letter_map)
            self.assertEqual(letter_map.get("\u00a7"), "s")
            self.assertEqual(letter_map.get("+"), "t")

    def test_plain_barred_keys_still_refused(self):
        for key in PLAIN_BARRED_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(
                        record_with_nested_key(key))

    def test_clean_keys_still_accepted_and_not_barred(self):
        for key in CLEAN_KEYS:
            with self.subTest(key=key):
                self.assertFalse(mod08._is_barred_key(key))
                accepted = mod08.accept_detection_input(
                    record_with_nested_key(key))
                self.assertEqual(accepted["agent_identifier"], "agent-b6")


class TestR4030LimbDUndirectedCopy(unittest.TestCase):

    def test_list_chain_of_101_containers_is_copied(self):
        chain = list_chain(101)
        copied = mod08._undirected_copy(chain)
        self.assertEqual(copied, chain)
        self.assertIsNot(copied, chain)

    def test_list_chain_of_102_containers_is_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._undirected_copy(list_chain(102))

    def test_list_chain_of_100_containers_is_copied_control(self):
        chain = list_chain(100)
        self.assertEqual(mod08._undirected_copy(chain), chain)

    def test_tuple_chain_of_101_containers_is_copied(self):
        chain = tuple_chain(101)
        self.assertEqual(mod08._undirected_copy(chain), chain)

    def test_tuple_chain_of_102_containers_is_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._undirected_copy(tuple_chain(102))

    def test_dict_chain_of_101_containers_is_copied(self):
        chain = dict_chain(101)
        self.assertEqual(mod08._undirected_copy(chain), chain)

    def test_dict_chain_of_102_containers_is_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._undirected_copy(dict_chain(102))

    def test_scalar_leaf_at_depth_101_is_copied(self):
        for leaf in ("leaf", 7, 2.5, None, True):
            with self.subTest(leaf=leaf):
                chain = list_chain(101, leaf=leaf)
                self.assertEqual(mod08._undirected_copy(chain), chain)

    def test_find_barred_boundary_control_both_ways(self):
        self.assertEqual(mod08._find_barred(list_chain(101)), [])
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._find_barred(list_chain(102))

    def test_shallow_copy_still_copies_values(self):
        value = {"a": [1, (2, 3), {"b": "c"}], "d": {4, 5}}
        copied = mod08._undirected_copy(value)
        self.assertEqual(copied, value)
        self.assertIsNot(copied, value)


if __name__ == "__main__":
    unittest.main()
