"""Step 16 fix wave 2, builder 4: row F2-06 (Low), ruling T16-29.

Test first tests for the prototype order bar reading evasion:
the bar read its value by exact string match only, at mod01
Forms 1 and 4 and in the mod04 value set in the same form, so
case and spacing variants of the barred words validated True
where the literal validated False. The cure reads the value
through the product standing folded and dressed reading, the
same reading the validator applies to stored text elsewhere,
so variants of the two charged literals stand barred at the
same surfaces. No new barred value stands invented (OP-16),
and the two charged literals themselves stand barred exactly
as before.

Bench basis for every figure in the fix paper: bench
Python 3.14.4, Carry 6.

Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

from crucible import mod01, mod04


# The variants charged at ruling T16-29, stated in the open:
# the capitalised form, the literal with surrounding spaces,
# and the literal with a doubled internal space, for each of
# the two charged literals (the brief literal and the shortened
# literal the product bar already refused).
BARRED_VARIANTS = (
    "Prototype Order",
    " prototype order ",
    "prototype  order",
    "Prototype",
    " prototype ",
)

CHARGED_LITERALS = ("prototype order", "prototype")

LEGITIMATE_ORDER = "fixed order A"


class TestF206BarReadingVariants(unittest.TestCase):

    def _headline_run(self, order):
        record = mod01.minimal_valid_instance("4")
        record["run_class"] = "headline"
        record["scheduling_order_identifier"] = order
        return record

    def _form1_record(self, order):
        record = mod01.minimal_valid_instance("1")
        record["scheduling_order_identifier"] = order
        return record

    def _mod04_record(self, order):
        return {"run_class": "headline",
                "scheduling_order_identifier": order}

    def test_variants_fail_mod01_form4_validation(self):
        for variant in BARRED_VARIANTS:
            record = self._headline_run(variant)
            self.assertFalse(
                mod01.validate_record("4", record), variant)
            self.assertFalse(
                bool(mod01.run_is_reportable("4", record)), variant)

    def test_variants_fail_mod01_form1_validation(self):
        for variant in BARRED_VARIANTS:
            record = self._form1_record(variant)
            self.assertFalse(
                mod01.validate_record("1", record), variant)

    def test_variants_fail_mod04_order_checks(self):
        for variant in BARRED_VARIANTS:
            record = self._mod04_record(variant)
            self.assertFalse(
                mod04.validate_run_scheduling_order(record), variant)
            self.assertFalse(
                mod04.headline_order_stands(record), variant)

    def test_charged_literals_stay_barred_at_every_surface(self):
        for literal in CHARGED_LITERALS:
            self.assertFalse(mod01.validate_record(
                "4", self._headline_run(literal)), literal)
            self.assertFalse(mod01.validate_record(
                "1", self._form1_record(literal)), literal)
            self.assertFalse(mod04.validate_run_scheduling_order(
                self._mod04_record(literal)), literal)
            self.assertFalse(mod04.headline_order_stands(
                self._mod04_record(literal)), literal)

    def test_legitimate_order_values_still_validate(self):
        record = self._headline_run(LEGITIMATE_ORDER)
        self.assertTrue(mod01.validate_record("4", record))
        self.assertTrue(bool(mod01.run_is_reportable("4", record)))
        self.assertTrue(mod01.validate_record(
            "1", self._form1_record(LEGITIMATE_ORDER)))
        self.assertTrue(mod04.validate_run_scheduling_order(
            self._mod04_record(LEGITIMATE_ORDER)))
        self.assertTrue(mod04.headline_order_stands(
            self._mod04_record(LEGITIMATE_ORDER)))

    def test_near_values_stand_unbarred(self):
        # No new barred value stands invented (OP-16): values
        # that merely carry the barred words beside other words,
        # or extend them, stand as legitimate order values.
        for value in ("prototype order A", "my prototype order",
                      "prototypes", "fixed prototype ordering"):
            self.assertTrue(mod01.validate_record(
                "4", self._headline_run(value)), value)
            self.assertTrue(mod04.validate_run_scheduling_order(
                self._mod04_record(value)), value)
            self.assertTrue(mod04.headline_order_stands(
                self._mod04_record(value)), value)


if __name__ == "__main__":
    unittest.main()
