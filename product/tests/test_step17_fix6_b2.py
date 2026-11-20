"""Step 17 fix wave 6, Slice 2 defect tests: row FW6-02 at
crucible.mod02 (T17R5-03).

FW6-02: the mod02 draw door refusal for a negative integer
position, handed by keyword, positionally, or inside a state
dict, states the true ground in the named draw form, that a
position stands as a whole number at or above zero and the
handed position stands below zero, in the form the carried
positions limb and the digit text limb of the same door
already state. On the uncured tree the integer position limb
states instead that the position argument stands as a number
in no admitted position form, which stands false for a
negative integer: a negative integer stands in an admitted
integer form, and its true ground is that it stands below
zero.

Huge values stand judged by type and stored value, never by
a printed repr of a huge result.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod02 as mod02

HUGE = 10 ** 5000
NEG = -HUGE
BARE = "Exceeds the limit"
BARE2 = "set_int_max_str_digits"
FALSE_GROUND = "in no admitted position form"
TRUE_GROUND = "the position argument stands below zero"
TRUE_RULE = ("a position stands as a whole number at or "
             "above zero, and the handed position stands "
             "below zero")


class StoredNegInt(int):
    """An int handing storing a plain negative value, read
    through its base integer reading."""


def _state():
    return mod02.initial_stream_state("alpha", carried_positions=0)


def _assert_true_ground(test_case, fn):
    with test_case.assertRaises(ValueError) as caught:
        fn()
    text = str(caught.exception)
    test_case.assertIn("draw_from_stream stands refused", text)
    test_case.assertIn(TRUE_GROUND, text)
    test_case.assertIn(TRUE_RULE, text)
    test_case.assertIn("no draw stands made", text)
    test_case.assertNotIn(FALSE_GROUND, text)
    test_case.assertNotIn(BARE, text)
    test_case.assertNotIn(BARE2, text)
    return text


class TestFW602DrawIntegerPositionGround(unittest.TestCase):

    def test_defect_keyword_small_negative_int_true_ground(self):
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            "alpha", position=-5, state=_state()))

    def test_defect_keyword_huge_negative_int_true_ground(self):
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            "alpha", position=NEG, state=_state()))

    def test_defect_keyword_negative_int_no_state_true_ground(self):
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            "alpha", position=-5, carried_positions=0))

    def test_defect_positional_small_negative_int_true_ground(self):
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            "alpha", -5, 0))

    def test_defect_positional_huge_negative_int_true_ground(self):
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            "alpha", NEG, 0))

    def test_defect_state_dict_small_negative_int_true_ground(self):
        state = {"stream_class": "alpha", "position": -5,
                 "carried_positions": 0}
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            state=state))

    def test_defect_state_dict_huge_negative_int_true_ground(self):
        state = {"stream_class": "alpha", "position": NEG,
                 "carried_positions": 0}
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            state=state))

    def test_defect_stored_negative_int_true_ground(self):
        _assert_true_ground(self, lambda: mod02.draw_from_stream(
            "alpha", position=StoredNegInt(-5), carried_positions=0))


class TestSlice2Controls(unittest.TestCase):

    def test_control_positive_huge_position_served_whole(self):
        result = mod02.draw_from_stream(
            "alpha", position=HUGE, state=_state())
        self.assertEqual(result["failure"],
                         mod02.STREAM_EXHAUSTED_FAILURE)
        self.assertEqual(result["position"], HUGE)

    def test_control_inside_carried_returns_gated_refusal(self):
        result = mod02.draw_from_stream(
            "alpha", position=1, carried_positions=3)
        self.assertEqual(result["position"], 1)
        self.assertFalse(result["seed_drawn"])

    def test_control_negative_digit_text_states_below_zero(self):
        text = _assert_true_ground(
            self, lambda: mod02.draw_from_stream(
                "alpha", position="-5", state=_state()))
        self.assertIn("-5", text)

    def test_control_carried_negative_int_states_below_zero(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                "alpha", position=1, carried_positions=-5)
        text = str(caught.exception)
        self.assertIn("draw_from_stream stands refused", text)
        self.assertIn(
            "the carried positions argument stands below zero",
            text)
        self.assertIn("no draw stands made", text)

    def test_control_fractional_position_form_ground_stands(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                "alpha", position=1.5, carried_positions=3)
        text = str(caught.exception)
        self.assertIn("draw_from_stream stands refused", text)
        self.assertIn(FALSE_GROUND, text)
        self.assertIn("no draw stands made", text)

    def test_control_non_numeric_text_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                "alpha", position="abc", carried_positions=3)
        text = str(caught.exception)
        self.assertIn("draw_from_stream stands refused", text)
        self.assertIn("in no numeric form", text)

    def test_control_bool_position_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                "alpha", position=True, carried_positions=3)
        self.assertIn("draw_from_stream stands refused",
                      str(caught.exception))


if __name__ == "__main__":
    unittest.main()
