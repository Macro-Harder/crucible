"""Step 17 fix wave 5, Slice 7 defect tests, row FW5-11.

The mod11 retirement doors, retirement_verdicts and
retirement_tally, escape with a bare RecursionError on a
cyclic list handing and on a list nested 2000 levels deep
(Red 5, S17R4-RED5-03). The cure charges both doors to judge
a list handing for cycle and depth before their acts, so a
cyclic or over deep list refuses in the named form of the
door, stating the ground and that no verdict stands
returned. The neighbouring malformed handings at the same
doors already refuse in the named form on the base tree and
stand here as controls, beside the valid fixture controls.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod11


def _cyclic_list():
    cyc = []
    cyc.append(cyc)
    return cyc


def _nested_cycle():
    inner = []
    outer = [inner]
    inner.append(outer)
    return outer


def _deep_list(levels=2000):
    deep = 1
    for _ in range(levels):
        deep = [deep]
    return deep


class TestFW511CyclicList(unittest.TestCase):
    def test_verdicts_cyclic_list_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts(_cyclic_list())
        message = str(caught.exception)
        self.assertIn("cyclic", message)
        self.assertIn("no verdict stands returned", message)

    def test_tally_cyclic_list_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_tally(_cyclic_list())
        message = str(caught.exception)
        self.assertIn("cyclic", message)
        self.assertIn("no verdict stands returned", message)

    def test_verdicts_nested_cycle_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts(_nested_cycle())
        message = str(caught.exception)
        self.assertIn("cyclic", message)
        self.assertIn("no verdict stands returned", message)


class TestFW511DeepList(unittest.TestCase):
    def test_verdicts_deep_list_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts(_deep_list())
        message = str(caught.exception)
        self.assertIn("depth", message)
        self.assertIn("no verdict stands returned", message)

    def test_tally_deep_list_refuses_named(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_tally(_deep_list())
        message = str(caught.exception)
        self.assertIn("depth", message)
        self.assertIn("no verdict stands returned", message)


class TestFW511Controls(unittest.TestCase):
    def test_valid_f01_verdicts_served_whole(self):
        verdicts = mod11.retirement_verdicts("F-01")
        self.assertEqual(verdicts["T-01"], "passed")
        self.assertEqual(len(verdicts), 15)

    def test_valid_ex01_tally_served_whole(self):
        tally = mod11.retirement_tally("EX-01")
        self.assertEqual(tally["total"], 15)
        self.assertEqual(tally["fixture"], "EX-01")

    def test_cyclic_dict_refuses_named_control(self):
        cyc = {}
        cyc["self"] = cyc
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts(cyc)
        self.assertIn(
            "no retirement verdict stands recorded for",
            str(caught.exception))

    def test_empty_list_refuses_named_control(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts([])
        self.assertIn(
            "no retirement verdict stands recorded for",
            str(caught.exception))

    def test_text_handling_refuses_named_control(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_tally("junk")
        self.assertIn(
            "no retirement verdict stands recorded for",
            str(caught.exception))


if __name__ == "__main__":
    unittest.main()
