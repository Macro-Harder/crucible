import unittest

from crucible import mod07


PASSAGE_FIELDS = ("point_in_run", "what_in_fact_passed")


def records_with(field, value):
    records = mod07.tracer_passage_records("run-r11-b6")
    records[0][field] = value
    return records


def wrapped_records(wrapper):
    records = mod07.tracer_passage_records("run-r11-b6")
    return [wrapper(record) for record in records]


class LyingBytes(bytes):
    def __new__(cls, stored, reported):
        obj = super().__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported

    def decode(self, *args, **kwargs):
        return self._reported


class LyingBytearray(bytearray):
    def __str__(self):
        return getattr(self, "_reported", "reported")


class PassageLieGetDict(dict):
    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = reported

    def get(self, key, default=None):
        if key in PASSAGE_FIELDS:
            return self._reported
        return dict.get(self, key, default)


class AllLieGetDict(dict):
    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported


class PassageRaisingGetDict(dict):
    def get(self, key, default=None):
        if key in PASSAGE_FIELDS:
            raise RuntimeError("handed get raises")
        return dict.get(self, key, default)


class AllRaisingGetDict(dict):
    def get(self, key, default=None):
        raise RuntimeError("handed get raises")


class TestR10007Mod07StoredTextHelperForm(unittest.TestCase):

    def test_bytes_decoded_from_stored_bytes(self):
        self.assertEqual(mod07._stored_text(b"real text"), "real text")
        self.assertEqual(mod07._stored_text(b""), "")
        self.assertEqual(
            mod07._stored_text("real".encode("utf-8")), "real")

    def test_bytearray_decoded_from_stored_bytes(self):
        self.assertEqual(
            mod07._stored_text(bytearray(b"real text")), "real text")
        self.assertEqual(mod07._stored_text(bytearray(b"")), "")

    def test_memoryview_decoded_from_stored_bytes(self):
        self.assertEqual(
            mod07._stored_text(memoryview(b"real text")), "real text")
        self.assertEqual(mod07._stored_text(memoryview(b"")), "")
        self.assertEqual(
            mod07._stored_text(memoryview(bytearray(b"seam"))), "seam")

    def test_undecodable_bytes_dropped(self):
        self.assertEqual(mod07._stored_text(b"re\xffal"), "real")
        self.assertEqual(mod07._stored_text(b"\xff\xfe"), "")
        self.assertEqual(
            mod07._stored_text(memoryview(b"re\xffal")), "real")
        self.assertEqual(
            mod07._stored_text(bytearray(b"re\xffal")), "real")

    def test_bytes_subclass_read_by_stored_not_reported(self):
        self.assertEqual(
            mod07._stored_text(LyingBytes(b"real", "reported")), "real")
        self.assertEqual(
            mod07._stored_text(LyingBytes(b"", "reported")), "")
        self.assertEqual(
            mod07._stored_text(LyingBytes(b"reported", "")), "reported")

    def test_bytearray_subclass_read_by_stored_not_reported(self):
        handed = LyingBytearray(b"real")
        handed._reported = "reported"
        self.assertEqual(str(handed), "reported")
        self.assertEqual(mod07._stored_text(handed), "real")

    def test_passage_text_states_something_for_binary_forms(self):
        for handed in (b"real", bytearray(b"real"),
                       memoryview(b"real")):
            with self.subTest(handed=repr(handed)):
                self.assertTrue(
                    mod07._passage_text_states_something(handed))
        for handed in (b" ", b"\xe2\x80\x8b",
                       bytearray(b" "),
                       memoryview("\u200b".encode("utf-8")),
                       memoryview(b" ")):
            with self.subTest(handed=repr(handed)):
                self.assertFalse(
                    mod07._passage_text_states_something(handed))

    def test_stored_text_controls_standing(self):
        self.assertEqual(mod07._stored_text("plain"), "plain")
        self.assertEqual(mod07._stored_text(""), "")
        self.assertEqual(mod07._stored_text(None), "")
        self.assertEqual(mod07._stored_text(123), "")


class TestR10041PassageSetBaseRecordReading(unittest.TestCase):

    def test_blank_stored_passage_reported_real_refused(self):
        for field in PASSAGE_FIELDS:
            for stored_blank in ("", "   ", "\u200b"):
                records = wrapped_records(
                    lambda record: PassageLieGetDict(record, "real text"))
                records[0][field] = stored_blank
                with self.subTest(field=field, stored=repr(stored_blank)):
                    self.assertFalse(
                        mod07.validate_tracer_passage_set(records))

    def test_real_stored_passage_reported_blank_validates(self):
        for field in PASSAGE_FIELDS:
            for reported in ("", "\u200b", None):
                records = wrapped_records(
                    lambda record, rep=reported:
                        PassageLieGetDict(record, rep))
                records[0][field] = "real passage text"
                with self.subTest(field=field, reported=repr(reported)):
                    self.assertTrue(
                        mod07.validate_tracer_passage_set(records))

    def test_raising_passage_get_judged_by_stored(self):
        records = wrapped_records(PassageRaisingGetDict)
        self.assertTrue(mod07.validate_tracer_passage_set(records))
        for field in PASSAGE_FIELDS:
            records = wrapped_records(PassageRaisingGetDict)
            records[0][field] = "\u200b"
            with self.subTest(field=field):
                self.assertFalse(
                    mod07.validate_tracer_passage_set(records))

    def test_raising_all_get_judged_by_stored(self):
        records = wrapped_records(AllRaisingGetDict)
        self.assertTrue(mod07.validate_tracer_passage_set(records))
        records = wrapped_records(AllRaisingGetDict)
        records[0]["what_in_fact_passed"] = ""
        self.assertFalse(mod07.validate_tracer_passage_set(records))

    def test_all_lie_get_judged_by_stored(self):
        records = wrapped_records(
            lambda record: AllLieGetDict(record, "real text"))
        self.assertTrue(mod07.validate_tracer_passage_set(records))
        records = wrapped_records(
            lambda record: AllLieGetDict(record, "real text"))
        records[0]["point_in_run"] = "\u200b"
        self.assertFalse(mod07.validate_tracer_passage_set(records))

    def test_controls_honest_records_standing(self):
        self.assertTrue(mod07.validate_tracer_passage_set(
            mod07.tracer_passage_records("run-r11-b6")))
        for field in PASSAGE_FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    records_with(field, "")))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    records_with(field, "\u200b")))
                self.assertTrue(mod07.validate_tracer_passage_set(
                    records_with(field, b"real passage")))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    records_with(field, memoryview(b" "))))


if __name__ == "__main__":
    unittest.main()
