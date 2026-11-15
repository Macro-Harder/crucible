"""Fix wave 17 pins, Builder 1: rows R17-002, R17-005, R17-006,
R17-019, R17-020, R17-036, R17-037, and R17-046.

MOD-11 registry key texts, part text, stem, and figure family
under settlements S-10 and S-15. Each pin stands in the
distinguishing case standard: it fails on the pristine code
for the charged defect and passes after the cure, beside the
controls that hold on both.
"""
import time
import unittest

import crucible.mod11 as mod11


FIELD10_TEXT = (
    "seam status: no cross seam effect; "
    "kill check: self checked only; "
    "dependence mark: DQ-164 confirmation form, recording that "
    "DQ-164 stands settled as confirmation only; "
    "Parley Q3 statement: no part of the result encodes Parley "
    "Q3 behaviour; "
    "core only qualifier: this unit is a core only result; "
    "anchor scenario statement: no anchor scenario is used in "
    "this unit."
)


def empty_chain(depth):
    value = ()
    for _ in range(depth):
        value = (value,)
    return value


def two_text_part(extra):
    return frozenset({"a", "b", extra})


def options_tuple(count, first, second):
    return tuple(frozenset({first, second}) for _ in range(count))


def readout_for(name):
    return {"quantities": [
        {"name": name, "recorded_number": 3,
         "class_based": True, "class_rule": "sample share holds"}]}


class TestR17002UnorderedRegistryKeyTexts(unittest.TestCase):
    def test_eight_parts_each_two_texts_falls_back(self):
        key = frozenset(
            two_text_part(empty_chain(i)) for i in range(8))
        self.assertEqual(
            mod11._registry_key_texts(key),
            {mod11._registry_key_text(key)})

    def test_nine_empty_parts_answer_at_once(self):
        key = frozenset(empty_chain(i) for i in range(9))
        start = time.monotonic()
        result = mod11._registry_key_texts(key)
        elapsed = time.monotonic() - start
        self.assertEqual(result, {""})
        self.assertLess(elapsed, 1.0)


class TestR17005CrossProductBuiltBeforeBound(unittest.TestCase):
    def test_ordered_pair_total_checked_before_building(self):
        left = options_tuple(10, "a", "b")
        right = options_tuple(11, "a", "b")
        key = (left, right)
        start = time.monotonic()
        result = mod11._registry_key_texts(key)
        elapsed = time.monotonic() - start
        self.assertEqual(result, {mod11._registry_key_text(key)})
        self.assertLess(elapsed, 1.5)

    def test_unordered_pair_total_checked_before_building(self):
        left = options_tuple(10, "a", "b")
        right = options_tuple(11, "c", "d")
        key = frozenset({left, right})
        start = time.monotonic()
        result = mod11._registry_key_texts(key)
        elapsed = time.monotonic() - start
        self.assertEqual(result, {mod11._registry_key_text(key)})
        self.assertLess(elapsed, 1.5)


class TestR17006NestedUnorderedPartText(unittest.TestCase):
    def nested(self):
        return frozenset(
            frozenset("t%d%d" % (i, j) for j in range(6))
            for i in range(6))

    def test_nested_unordered_text_stays_bounded(self):
        self.assertLess(len(mod11._part_text(self.nested())), 1000000)

    def test_single_level_unordered_control_holds(self):
        text = mod11._part_text(frozenset({"ab", "cd"}))
        self.assertIn("ab cd", text)
        self.assertIn("cd ab", text)


class LyingStrKey(str):
    def __str__(self):
        return FIELD10_TEXT


class LyingStrObject:
    def __str__(self):
        return FIELD10_TEXT


class TestR17019PartTextBaseReadings(unittest.TestCase):
    def test_dict_key_lying_str_does_not_stand(self):
        value = {LyingStrKey("nothing stored"): "x"}
        self.assertFalse(mod11._field10_stands(value))

    def test_plain_object_lying_str_does_not_stand(self):
        self.assertFalse(mod11._field10_stands(LyingStrObject()))

    def test_plain_controls_hold(self):
        self.assertTrue(mod11._field10_stands({FIELD10_TEXT: "x"}))
        self.assertFalse(mod11._field10_stands(object()))
        self.assertEqual(mod11._part_text(7), "7")


class TestR17020RegistryKeyDepthBound(unittest.TestCase):
    def nest(self, depth, leaf):
        value = leaf
        for _ in range(depth):
            value = (value,)
        return value

    def test_key_texts_at_depth_2000_answer_empty(self):
        self.assertEqual(
            mod11._registry_key_texts(self.nest(2000, "x")), {""})

    def test_key_text_at_depth_2000_answers_empty(self):
        self.assertEqual(
            mod11._registry_key_text(self.nest(2000, "x")), "")

    def test_depth_50_control_holds(self):
        self.assertEqual(
            mod11._registry_key_texts(self.nest(50, "x")), {"x"})
        self.assertEqual(
            mod11._registry_key_text(self.nest(50, "x")), "x")


class TestR17036ToothesCompound(unittest.TestCase):
    def test_toothes_not_readable(self):
        self.assertFalse(mod11._is_readable_word("toothes"))

    def test_readout_refuses_toothes(self):
        self.assertFalse(mod11.validate_readout(readout_for("toothes")))

    def test_bound_forms_stand(self):
        self.assertTrue(mod11._is_readable_word("informationes"))
        self.assertTrue(mod11._is_readable_word("informations"))
        self.assertFalse(mod11._is_readable_word("informationies"))


class TestR17037YUndoublingRefusal(unittest.TestCase):
    def test_undoubled_no_y_bases_yield_no_stem(self):
        for word, base in (("bookky", "book"), ("chairry", "chair"),
                           ("windowwy", "window")):
            with self.subTest(word=word):
                self.assertNotIn(base, mod11._readable_stem(word))
                self.assertFalse(mod11._is_readable_word(word))

    def test_readout_refuses_bookky(self):
        self.assertFalse(mod11.validate_readout(readout_for("bookky")))

    def test_y_controls_hold(self):
        self.assertTrue(mod11._is_readable_word("happy"))
        self.assertFalse(mod11._is_readable_word("booky"))


class TestR17046TransitionFigureUnhashableRegime(unittest.TestCase):
    def test_unhashable_regime_draws_named_refusal(self):
        for regime in (["a"], {"a": 1}, {"a"}):
            with self.subTest(regime=type(regime).__name__):
                with self.assertRaises(ValueError) as caught:
                    mod11.transition_figure(
                        [{"first_terminal_regime": regime}])
                self.assertIn(
                    "transition_figure stands refused",
                    str(caught.exception))

    def test_location_for_endpoint_unhashable_regime(self):
        figure = mod11.transition_figure(
            [{"first_terminal_regime": "a"}])
        self.assertIsNone(
            mod11.location_for_endpoint(figure, ["a"], 0.5))

    def test_plain_control_holds(self):
        figure = mod11.transition_figure(
            [{"first_terminal_regime": "a"}])
        self.assertEqual(
            figure["cumulative_incidence"]["a"]["count"], 1)
        self.assertEqual(
            mod11.location_for_endpoint(figure, "a", 0.5),
            {"regime": "a", "endpoint": 0.5, "share": 1.0})


if __name__ == "__main__":
    unittest.main()
