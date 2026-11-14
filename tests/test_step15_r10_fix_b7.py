import unittest

from crucible import mod07


PASSAGE_FIELDS = ("point_in_run", "what_in_fact_passed")


def records_with(field, value):
    records = mod07.tracer_passage_records("run-b7")
    records[0][field] = value
    return records


class IterationLieStr(str):
    def __new__(cls, stored, iterated):
        obj = super().__new__(cls, stored)
        obj._iterated = iterated
        return obj

    def __iter__(self):
        return iter(self._iterated)


CS_CN_CO_TEXTS = (
    "\ud800",
    "\u0378",
    "\ue000",
    "\uf8ff",
    "\uffff",
    "\ud800\u0378\ue000",
    "\u200b\ue000",
    "\u0378\uffff",
)


class TestR9011PassageStoredCharacters(unittest.TestCase):

    def test_r9011_blank_storing_real_iterating_states_nothing(self):
        for stored in ("", "   ", "\u200b", "\u0000", "\u2800"):
            handed = IterationLieStr(stored, "real")
            with self.subTest(stored=repr(stored)):
                self.assertFalse(
                    mod07._passage_text_states_something(handed))
                self.assertTrue(
                    mod07._passage_field_is_blank(handed))
        for field in PASSAGE_FIELDS:
            handed = IterationLieStr("\u200b", "real")
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    records_with(field, handed)))

    def test_r9011_real_storing_blank_iterating_states_something(self):
        for stored, iterated in (
                ("real text", "\u200b"), ("x", ""), ("plain", "   ")):
            handed = IterationLieStr(stored, iterated)
            with self.subTest(stored=stored, iterated=repr(iterated)):
                self.assertTrue(
                    mod07._passage_text_states_something(handed))
                self.assertFalse(
                    mod07._passage_field_is_blank(handed))
        for field in PASSAGE_FIELDS:
            handed = IterationLieStr("real text", "\u200b")
            with self.subTest(field=field):
                self.assertTrue(mod07.validate_tracer_passage_set(
                    records_with(field, handed)))


class TestR9017PassageBlankCategories(unittest.TestCase):

    def test_r9017_direct_helper_cs_cn_co_state_nothing(self):
        for value in CS_CN_CO_TEXTS:
            with self.subTest(value=repr(value)):
                self.assertFalse(
                    mod07._passage_text_states_something(value))

    def test_r9017_string_forms_validate_as_blank(self):
        for field in PASSAGE_FIELDS:
            for value in CS_CN_CO_TEXTS:
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        records_with(field, value)))
                    self.assertTrue(
                        mod07._passage_field_is_blank(value))

    def test_r9017_bytes_forms_validate_as_blank(self):
        for field in PASSAGE_FIELDS:
            for value in (
                    "\ue000".encode("utf-8"),
                    "\u0378".encode("utf-8"),
                    "\ue000\u0378".encode("utf-8"),
                    "\uffff".encode("utf-8"),
            ):
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        records_with(field, value)))
                    self.assertTrue(
                        mod07._passage_field_is_blank(value))

    def test_r9017_bytearray_forms_validate_as_blank(self):
        for field in PASSAGE_FIELDS:
            for value in (
                    bytearray("\ue000".encode("utf-8")),
                    bytearray("\u0378".encode("utf-8")),
                    bytearray("\ue000\u0378".encode("utf-8")),
            ):
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        records_with(field, value)))
                    self.assertTrue(
                        mod07._passage_field_is_blank(value))

    def test_r9017_memoryview_forms_validate_as_blank(self):
        for field in PASSAGE_FIELDS:
            for value in (
                    memoryview("\ue000".encode("utf-8")),
                    memoryview("\u0378".encode("utf-8")),
                    memoryview("\ue000\u0378".encode("utf-8")),
            ):
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        records_with(field, value)))
                    self.assertTrue(
                        mod07._passage_field_is_blank(value))


class TestControlsStanding(unittest.TestCase):

    def test_control_so_category_still_states_something(self):
        for value in ("\u2603", "\u00a9", "\u2660"):
            with self.subTest(value=repr(value)):
                self.assertTrue(
                    mod07._passage_text_states_something(value))
                self.assertFalse(
                    mod07._passage_field_is_blank(value))
        for field in PASSAGE_FIELDS:
            self.assertTrue(mod07.validate_tracer_passage_set(
                records_with(field, "\u2603")))
            self.assertTrue(mod07.validate_tracer_passage_set(
                records_with(field, "\u2603".encode("utf-8"))))
            self.assertTrue(mod07.validate_tracer_passage_set(
                records_with(field, bytearray(
                    "\u2603".encode("utf-8")))))
            self.assertTrue(mod07.validate_tracer_passage_set(
                records_with(field, memoryview(
                    "\u2603".encode("utf-8")))))

    def test_control_readable_text_validates_in_all_forms(self):
        for field in PASSAGE_FIELDS:
            for value in (
                    "plain readable text",
                    "x",
                    "plain readable text".encode("utf-8"),
                    bytearray("plain".encode("utf-8")),
                    memoryview("plain".encode("utf-8")),
            ):
                with self.subTest(field=field, value=repr(value)):
                    self.assertTrue(mod07.validate_tracer_passage_set(
                        records_with(field, value)))

    def test_control_standing_blank_classes_still_blank(self):
        for field in PASSAGE_FIELDS:
            for value in (
                    "", "   ", "\u00a0", "\u200b", "\ufeff",
                    "\u034f", "\u2800", "\u115f",
                    "\u0000", "\u0007", "\u001b", "\u007f",
                    "\u0903", "\u093e", "\u20dd", "\u0488",
                    "\u1160", "\u3164", "\uffa0",
                    "\u200b".encode("utf-8"),
                    b"\x00",
                    bytearray(b"\x00"),
                    memoryview("\u1160".encode("utf-8")),
                    memoryview(b"\x00"),
            ):
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        records_with(field, value)))

    def test_control_real_text_beside_cs_cn_co_states_something(self):
        for value in ("\ue000x", "x\u0378", "\ud800 with a letter x"):
            with self.subTest(value=repr(value)):
                self.assertTrue(
                    mod07._passage_text_states_something(value))
        for field in PASSAGE_FIELDS:
            self.assertTrue(mod07.validate_tracer_passage_set(
                records_with(field, "\ue000x")))
            self.assertTrue(mod07.validate_tracer_passage_set(
                records_with(field, "\u0000 with a letter x")))

    def test_control_honest_text_forms_judged_by_stored_text(self):
        self.assertTrue(mod07._passage_text_states_something("real"))
        self.assertFalse(mod07._passage_text_states_something(""))
        self.assertFalse(mod07._passage_text_states_something("   "))
        handed = IterationLieStr("real text", "real text")
        self.assertTrue(mod07._passage_text_states_something(handed))


if __name__ == "__main__":
    unittest.main()
