"""Step 17 fix wave 6, Builder 1 defect tests (FW6-01, T17R5-01).

Row: at the mod05 recompute_share door, a mapping handing whose
epoch key stands as an integer past the interpreter digit limit,
at either argument and at either sign, stands served whole or
refused in the named recompute form stating the ground and that
no share stands returned, and no bare interpreter digit limit
sentence escapes at the door.

Every outcome below stands judged by stored value in code and by
the whole text of a refusal, never by a repr of a returned result
carrying a huge key. Huge keys stand compared by equality and by
type only.

Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

from crucible import mod05

HUGE = 10 ** 5000
BOUND = 10 ** 4300
BELOW = 10 ** 4299

BARE_FRAGMENTS = (
    "Exceeds the limit",
    "for integer string conversion",
    "set_int_max_str_digits",
)


def _assert_named_recompute_refusal(case, logged, recomputed):
    with case.assertRaises(ValueError) as caught:
        mod05.recompute_share(logged, recomputed)
    message = str(caught.exception)
    case.assertIn("recompute_share stands refused", message)
    case.assertIn("epoch key", message)
    case.assertIn("digit limit", message)
    case.assertIn("no share stands returned", message)
    for fragment in BARE_FRAGMENTS:
        case.assertNotIn(fragment, message)


class TestFW601RecomputeEpochKey(unittest.TestCase):
    """Defect tests: each failed on the uncured tree, where the
    handing escapes as the bare interpreter digit limit sentence
    alone, and passes on the cured tree."""

    def test_both_arguments_huge_positive(self):
        _assert_named_recompute_refusal(
            self, {HUGE: 1}, {HUGE: 1})

    def test_first_argument_only_huge(self):
        _assert_named_recompute_refusal(
            self, {HUGE: 1}, {"e1": 1})

    def test_second_argument_only_huge(self):
        _assert_named_recompute_refusal(
            self, {"e1": 1}, {HUGE: 1})

    def test_both_arguments_negative_huge(self):
        _assert_named_recompute_refusal(
            self, {-HUGE: 1}, {-HUGE: 1})

    def test_first_argument_only_negative_huge(self):
        _assert_named_recompute_refusal(
            self, {-HUGE: 1}, {"e1": 1})

    def test_second_argument_only_negative_huge(self):
        _assert_named_recompute_refusal(
            self, {"e1": 1}, {-HUGE: 1})

    def test_huge_key_differing_values(self):
        _assert_named_recompute_refusal(
            self, {HUGE: 1}, {HUGE: 2})

    def test_bound_key_4300(self):
        _assert_named_recompute_refusal(
            self, {BOUND: 1}, {BOUND: 1})


class TestFW601Controls(unittest.TestCase):
    """Controls: each passes on both the uncured and cured trees."""

    def test_below_bound_key_served_whole_equal(self):
        result = mod05.recompute_share({BELOW: 1}, {BELOW: 1})
        self.assertEqual(result["divergence_count"], 0)
        self.assertEqual(result["divergent_epochs"], [])

    def test_below_bound_key_served_whole_differing(self):
        result = mod05.recompute_share({BELOW: 1}, {BELOW: 2})
        self.assertEqual(result["divergence_count"], 1)
        self.assertEqual(len(result["divergent_epochs"]), 1)
        self.assertEqual(result["divergent_epochs"][0], BELOW)
        self.assertIs(type(result["divergent_epochs"][0]), int)

    def test_huge_share_value_served_whole(self):
        result = mod05.recompute_share(
            {"e1": HUGE}, {"e1": HUGE})
        self.assertEqual(result["divergence_count"], 0)
        self.assertEqual(result["divergent_epochs"], [])

    def test_small_integer_and_text_keys_served_whole(self):
        result = mod05.recompute_share({7: 1}, {7: 2})
        self.assertEqual(result["divergence_count"], 1)
        self.assertEqual(result["divergent_epochs"], [7])
        result = mod05.recompute_share({"e1": 1}, {"e1": 1})
        self.assertEqual(result["divergence_count"], 0)

    def test_non_mapping_handing_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.recompute_share([1], {1: 1})
        message = str(caught.exception)
        self.assertIn("recompute_share stands refused", message)
        self.assertIn("no mapping form", message)
        self.assertIn("no share stands returned", message)


if __name__ == "__main__":
    unittest.main()
