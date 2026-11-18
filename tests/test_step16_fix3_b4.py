"""Step 16 fix wave 3, builder 4: row F3-04 (Low), ruling T16-42.

Test first tests for the mod04 container dress escape at the
prototype order bar: a barred order value carried in a single
part container dress (list, tuple, set, frozenset) passed both
mod04 checks while mod01 barred the identical record at Form 4.
The cure bound reads the barred value at the mod04 checks
through the same stored text reading the mod01 doors apply,
container dresses included, so the identical record draws the
identical bar at mod04 as at mod01. Bytes, bytearray, and
memoryview dresses already stand barred and keep standing
barred. Near values and lawful values keep passing, so no new
barred value stands invented (OP-16).

Bench basis for every figure in the fix paper: bench
Python 3.14.4, Carry 6.

Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

from crucible import mod01, mod04


BARRED_TEXTS = (
    "prototype order",
    "prototype",
    "Prototype Order",
    " prototype order ",
    "prototype  order",
)

CONTAINER_DRESSES = (
    ("list", lambda value: [value]),
    ("tuple", lambda value: (value,)),
    ("set", lambda value: {value}),
    ("frozenset", lambda value: frozenset({value})),
)


class TestF304ContainerDress(unittest.TestCase):

    def _headline_run(self, order):
        record = mod01.minimal_valid_instance("4")
        record["run_class"] = "headline"
        record["scheduling_order_identifier"] = order
        return record

    def _mod04_record(self, order):
        return {"run_class": "headline",
                "scheduling_order_identifier": order}

    def test_container_dressed_barred_values_fail_mod04_checks(self):
        for dress_name, dress in CONTAINER_DRESSES:
            for text in BARRED_TEXTS:
                order = dress(text)
                record = self._mod04_record(order)
                self.assertFalse(
                    mod04.validate_run_scheduling_order(record),
                    (dress_name, text))
                self.assertFalse(
                    mod04.headline_order_stands(record),
                    (dress_name, text))

    def test_container_dressed_barred_values_match_mod01_bar(self):
        # The identical record stands barred at mod01 Form 4;
        # the mod04 checks must draw the identical bar.
        for dress_name, dress in CONTAINER_DRESSES:
            for text in BARRED_TEXTS:
                order = dress(text)
                self.assertFalse(
                    mod01.validate_record(
                        "4", self._headline_run(order)),
                    (dress_name, text))
                record = self._mod04_record(order)
                self.assertFalse(
                    mod04.validate_run_scheduling_order(record),
                    (dress_name, text))
                self.assertFalse(
                    mod04.headline_order_stands(record),
                    (dress_name, text))

    def test_nested_single_part_container_dress_fails_mod04(self):
        for order in ([["prototype order"]], (("Prototype Order",),),
                      [{"prototype"}]):
            record = self._mod04_record(order)
            self.assertFalse(
                mod01.validate_record("4", self._headline_run(order)),
                repr(order))
            self.assertFalse(
                mod04.validate_run_scheduling_order(record), repr(order))
            self.assertFalse(
                mod04.headline_order_stands(record), repr(order))

    def test_bytes_like_dresses_stay_barred_at_mod04(self):
        for order in (b"prototype order", bytearray(b"Prototype Order"),
                      memoryview(b"prototype")):
            record = self._mod04_record(order)
            self.assertFalse(
                mod04.validate_run_scheduling_order(record), repr(order))
            self.assertFalse(
                mod04.headline_order_stands(record), repr(order))

    def test_container_dressed_near_values_stand_unbarred(self):
        # No new barred value stands invented (OP-16): a barred
        # word carried beside other words, or extended, inside a
        # container dress stands as a lawful order value, exactly
        # as the same text stands unbarred at mod01.
        for dress_name, dress in CONTAINER_DRESSES:
            for text in ("prototype order A", "my prototype order",
                         "prototypes", "fixed prototype ordering",
                         "fixed order A"):
                order = dress(text)
                self.assertTrue(
                    mod01.validate_record(
                        "4", self._headline_run(order)),
                    (dress_name, text))
                record = self._mod04_record(order)
                self.assertTrue(
                    mod04.validate_run_scheduling_order(record),
                    (dress_name, text))
                self.assertTrue(
                    mod04.headline_order_stands(record),
                    (dress_name, text))

    def test_multi_part_and_dict_dresses_match_mod01(self):
        # A multi part container stores no single text at the
        # mod01 doors and a dict dress reads no order text
        # there; the mod04 checks answer the same way.
        for order in (["prototype order", "fixed order A"],
                      ("prototype", "fixed order A"),
                      {"order": "prototype order"}):
            self.assertTrue(
                mod01.validate_record("4", self._headline_run(order)),
                repr(order))
            record = self._mod04_record(order)
            self.assertTrue(
                mod04.validate_run_scheduling_order(record), repr(order))
            self.assertTrue(
                mod04.headline_order_stands(record), repr(order))

    def test_plain_values_stand_as_before(self):
        for text in BARRED_TEXTS:
            record = self._mod04_record(text)
            self.assertFalse(
                mod04.validate_run_scheduling_order(record), text)
            self.assertFalse(mod04.headline_order_stands(record), text)
        record = self._mod04_record("fixed order A")
        self.assertTrue(mod04.validate_run_scheduling_order(record))
        self.assertTrue(mod04.headline_order_stands(record))


if __name__ == "__main__":
    unittest.main()
