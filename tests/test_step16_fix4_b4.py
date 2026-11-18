"""Step 16 fix wave 4, builder 4: row F4-04 (Low), ruling T16-52.

Test first tests for the mod04 run_class dress separation: mod04
read run_class by plain dict.get equality while mod01 Form 4 reads
it through _stored_text_dress, so a headline class carried in a
stored text dress separated the identical record at the two mod04
checks (a barred order passed validate_run_scheduling_order, a
lawful order failed headline_order_stands). The cure bound reads
run_class at the mod04 checks on the same stored text terms as
the rest of the product, so one record stands or falls the same
at both mod04 checks, matching the plain form outcome for the
identical record. No new barred value stands invented (OP-16):
every order value named is a charged literal or a lawful control,
and every class value named is the headline class, its dress, a
near class, or a lawful non headline class.

Bench basis for every figure in the fix paper: bench
Python 3.14.4, Carry 6.

Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

from crucible import mod01, mod04


HEADLINE_DRESSES = (
    ("bytes", b"headline"),
    ("bytearray", bytearray(b"headline")),
    ("memoryview", memoryview(b"headline")),
    ("list", ["headline"]),
    ("tuple", ("headline",)),
    ("set", {"headline"}),
    ("frozenset", frozenset({"headline"})),
    ("nested list", [["headline"]]),
    ("list of bytes", [b"headline"]),
)

BARRED_ORDER = "prototype order"
LAWFUL_ORDER = "fixed order A"


class TestF404RunClassDressParity(unittest.TestCase):

    def _headline_run(self, run_class, order):
        record = mod01.minimal_valid_instance("4")
        record["run_class"] = run_class
        record["scheduling_order_identifier"] = order
        return record

    def _mod04_record(self, run_class, order):
        return {"run_class": run_class,
                "scheduling_order_identifier": order}

    def test_dressed_headline_barred_order_refused_at_both_checks(self):
        plain = self._mod04_record("headline", BARRED_ORDER)
        self.assertFalse(mod04.validate_run_scheduling_order(plain))
        self.assertFalse(mod04.headline_order_stands(plain))
        for dress_name, dressed_class in HEADLINE_DRESSES:
            record = self._mod04_record(dressed_class, BARRED_ORDER)
            self.assertFalse(
                mod04.validate_run_scheduling_order(record), dress_name)
            self.assertFalse(
                mod04.headline_order_stands(record), dress_name)

    def test_dressed_headline_barred_order_matches_mod01_bar(self):
        for dress_name, dressed_class in HEADLINE_DRESSES:
            self.assertFalse(
                mod01.validate_record(
                    "4", self._headline_run(dressed_class, BARRED_ORDER)),
                dress_name)
            record = self._mod04_record(dressed_class, BARRED_ORDER)
            self.assertFalse(
                mod04.validate_run_scheduling_order(record), dress_name)
            self.assertFalse(
                mod04.headline_order_stands(record), dress_name)

    def test_dressed_headline_lawful_order_passes_both_checks(self):
        plain = self._mod04_record("headline", LAWFUL_ORDER)
        self.assertTrue(mod04.validate_run_scheduling_order(plain))
        self.assertTrue(mod04.headline_order_stands(plain))
        for dress_name, dressed_class in HEADLINE_DRESSES:
            self.assertTrue(
                mod01.validate_record(
                    "4", self._headline_run(dressed_class, LAWFUL_ORDER)),
                dress_name)
            record = self._mod04_record(dressed_class, LAWFUL_ORDER)
            self.assertTrue(
                mod04.validate_run_scheduling_order(record), dress_name)
            self.assertTrue(
                mod04.headline_order_stands(record), dress_name)

    def test_dressed_non_headline_class_stands_as_plain(self):
        plain = self._mod04_record("screening", BARRED_ORDER)
        self.assertTrue(mod04.validate_run_scheduling_order(plain))
        self.assertFalse(mod04.headline_order_stands(plain))
        for dressed_class in (b"screening", bytearray(b"screening"),
                              ["screening"], ("screening",)):
            self.assertTrue(
                mod01.validate_record(
                    "4", self._headline_run(dressed_class, BARRED_ORDER)),
                repr(dressed_class))
            record = self._mod04_record(dressed_class, BARRED_ORDER)
            self.assertTrue(
                mod04.validate_run_scheduling_order(record),
                repr(dressed_class))
            self.assertFalse(
                mod04.headline_order_stands(record), repr(dressed_class))

    def test_no_single_text_and_near_class_dresses_match_mod01(self):
        # A multi part container stores no single class text at
        # the mod01 doors, and the class reading stands exact, so
        # a case variant of the headline class stands not headline
        # there; the mod04 checks answer the same way, so the
        # barred order draws no bar and no headline standing.
        for run_class in (["headline", "screening"], b"Headline",
                          ["Headline"], {"headline": True}):
            self.assertTrue(
                mod01.validate_record(
                    "4", self._headline_run(run_class, BARRED_ORDER)),
                repr(run_class))
            record = self._mod04_record(run_class, BARRED_ORDER)
            self.assertTrue(
                mod04.validate_run_scheduling_order(record),
                repr(run_class))
            self.assertFalse(
                mod04.headline_order_stands(record), repr(run_class))

    def test_plain_headline_stands_as_before(self):
        record = self._mod04_record("headline", BARRED_ORDER)
        self.assertFalse(mod04.validate_run_scheduling_order(record))
        self.assertFalse(mod04.headline_order_stands(record))
        record = self._mod04_record("headline", LAWFUL_ORDER)
        self.assertTrue(mod04.validate_run_scheduling_order(record))
        self.assertTrue(mod04.headline_order_stands(record))


if __name__ == "__main__":
    unittest.main()
