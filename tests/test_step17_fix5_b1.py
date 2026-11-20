"""Step 17 fix wave 5, Slice 1 defect tests: rows FW5-01, FW5-02,
and FW5-09 at crucible.mod02 (T17R4-01, T17R4-02, T17R4-09).

FW5-01: a negative integer position or carried position past the
digit limit, handed by keyword, inside a state dict, or as carried
positions, stands refused in the named draw form stating the true
ground, and no bare interpreter digit limit sentence escapes.

FW5-02: encode_candidate_input judges the field name key form
before any digit text conversion, and a huge integer key, and any
key in no field name form, refuses in the named form of the door
stating the ground and that no encoding stands returned.

FW5-09: the draw door refusal for a negative position handed in
digit text form states the true ground, that a position stands as
a whole number at or above zero and the handed position stands
below zero, in the named draw form.

Huge values stand judged by type and stored value, never by a
printed repr of a huge result.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod02 as mod02

HUGE = 10 ** 5000
NEG = -HUGE
BARE = "Exceeds the limit"
BARE2 = "set_int_max_str_digits"


def _state():
    return mod02.initial_stream_state("alpha", carried_positions=0)


def _assert_named_draw_refusal(test_case, fn):
    with test_case.assertRaises(ValueError) as caught:
        fn()
    text = str(caught.exception)
    test_case.assertIn("draw_from_stream stands refused", text)
    test_case.assertIn("whole number at or above zero", text)
    test_case.assertIn("no draw stands made", text)
    test_case.assertNotIn(BARE, text)
    test_case.assertNotIn(BARE2, text)
    return text


class TestFW501DrawNegativeHuge(unittest.TestCase):

    def test_keyword_position_negative_huge_with_state(self):
        _assert_named_draw_refusal(self, lambda: mod02.draw_from_stream(
            "alpha", position=NEG, state=_state()))

    def test_positional_position_negative_huge(self):
        _assert_named_draw_refusal(self, lambda: mod02.draw_from_stream(
            "alpha", NEG, 0))

    def test_state_dict_position_negative_huge(self):
        state = {"stream_class": "alpha", "position": NEG,
                 "carried_positions": 0}
        _assert_named_draw_refusal(self, lambda: mod02.draw_from_stream(
            state=state))

    def test_carried_positions_negative_huge(self):
        _assert_named_draw_refusal(self, lambda: mod02.draw_from_stream(
            "alpha", position=1, carried_positions=NEG))

    def test_state_dict_carried_negative_huge(self):
        state = {"stream_class": "alpha", "position": 1,
                 "carried_positions": NEG}
        _assert_named_draw_refusal(self, lambda: mod02.draw_from_stream(
            state=state))

    def test_negative_huge_position_with_huge_carried(self):
        _assert_named_draw_refusal(self, lambda: mod02.draw_from_stream(
            "alpha", position=NEG, carried_positions=HUGE + 1))


class TestFW502EncodeKeyForm(unittest.TestCase):

    def _assert_named_encode_refusal(self, values):
        with self.assertRaises(ValueError) as caught:
            mod02.encode_candidate_input(values)
        text = str(caught.exception)
        self.assertIn("encode_candidate_input stands refused", text)
        self.assertIn("no encoding stands returned", text)
        self.assertNotIn(BARE, text)
        self.assertNotIn(BARE2, text)
        return text

    def test_huge_integer_key_refused_named(self):
        self._assert_named_encode_refusal({HUGE: "a"})

    def test_negative_huge_integer_key_refused_named(self):
        self._assert_named_encode_refusal({NEG: "a"})

    def test_none_key_refused_named(self):
        self._assert_named_encode_refusal({None: "a"})

    def test_tuple_key_refused_named(self):
        self._assert_named_encode_refusal({("a",): "a"})

    def test_object_key_refused_named(self):
        self._assert_named_encode_refusal({object(): "a"})

    def test_bytes_key_refused_named(self):
        self._assert_named_encode_refusal({b"a": "a"})


class TestFW509DrawNegativeTextGround(unittest.TestCase):

    def _assert_true_ground(self, fn):
        with self.assertRaises(ValueError) as caught:
            fn()
        text = str(caught.exception)
        self.assertIn("draw_from_stream stands refused", text)
        self.assertIn("whole number at or above zero", text)
        self.assertIn("below zero", text)
        self.assertNotIn("in no numeric form", text)
        self.assertNotIn(BARE, text)
        self.assertNotIn(BARE2, text)
        return text

    def test_negative_huge_digit_text_with_state(self):
        self._assert_true_ground(lambda: mod02.draw_from_stream(
            "alpha", position="-" + "9" * 5000, state=_state()))

    def test_negative_small_digit_text_with_state(self):
        self._assert_true_ground(lambda: mod02.draw_from_stream(
            "alpha", position="-5", state=_state()))

    def test_negative_digit_text_inside_state_dict(self):
        state = {"stream_class": "alpha", "position": "-5",
                 "carried_positions": 0}
        self._assert_true_ground(lambda: mod02.draw_from_stream(
            state=state))


class TestSlice1Controls(unittest.TestCase):

    def test_control_small_negative_int_refuses_named(self):
        text = _assert_named_draw_refusal(
            self, lambda: mod02.draw_from_stream(
                "alpha", position=-5, state=_state()))
        self.assertIn("-5", text)

    def test_control_positive_huge_position_served_whole(self):
        result = mod02.draw_from_stream(
            "alpha", position=HUGE, state=_state())
        self.assertEqual(result["failure"], mod02.STREAM_EXHAUSTED_FAILURE)
        self.assertEqual(result["position"], HUGE)

    def test_control_plain_integer_key_encodes(self):
        encoded = mod02.encode_candidate_input({5: "val"})
        self.assertIn("5", encoded)

    def test_control_text_key_encodes(self):
        self.assertEqual(
            mod02.encode_candidate_input({"a": "one", "b": "two"}),
            mod02.encode_candidate_input({"b": "two", "a": "one"}))

    def test_control_huge_value_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod02.encode_candidate_input({"a": HUGE})
        self.assertIn("no encoding stands returned",
                      str(caught.exception))


if __name__ == "__main__":
    unittest.main()
