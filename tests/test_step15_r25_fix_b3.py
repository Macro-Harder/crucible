"""Pins for fix wave 25, builder b3: row R25-003 of the
Round 25 register.

R25-003: the RecorderStore.__init__ store file load guard
catches json.JSONDecodeError, TypeError, and KeyError only,
building the named LookupFailure for a store file that could
not be read as a store, but the interpreter limit failure of
json.load on a hand written store file carrying an integer
beyond the limit (5,001 digits, over the default limit of
4,300) anywhere in its records is a plain ValueError and not
a JSONDecodeError instance, so construction escapes bare
ValueError and the named form stands never delivered. The
cure stands at the load guard alone: that handing delivers
the same named LookupFailure, in its landed wording, that
construction already delivers for its other load failures.

Distinguishing pins fail on the pristine basis and pass on
the cured copy. Control pins pass on both trees.
"""
import json
import os
import sys
import tempfile
import unittest

from crucible import mod10

BIG = "9" * 5001


def write_raw(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def big_identifier_text(field="run_id"):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"' + field + '": ' + BIG + ', "marker": "big"}, '
        '{"run_id": "plain-run", "marker": "plain"}]}')


def big_ordinary_text():
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "plain-run", "amount": ' + BIG + '}]}')


class B3Base(unittest.TestCase):

    def assert_named_load_failure(self, exc, path):
        self.assertIsInstance(exc, mod10.LookupFailure)
        self.assertIn("could not be read as a store", str(exc))
        self.assertIn("the store file at " + path, str(exc))
        self.assertEqual(exc.failure["name"], "one store file open failure")
        self.assertEqual(exc.failure["run_status"], "failed")
        self.assertEqual(exc.failure["complete"], False)
        self.assertEqual(exc.failure["store_path"], path)


class TestR25003Distinguishing(B3Base):

    def test_distinguishing_identifier_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_identifier_text("run_id"))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_ordinary_field_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_ordinary_text())
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_identifier_new_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_identifier_text("run_identifier"))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.new_store(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_ordinary_field_new_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_ordinary_text())
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.new_store(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_negative_identifier_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(
                path,
                '{"store_kind": "sweep", "records": ['
                '{"run_id": -' + BIG + '}]}')
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)


class TestR25003Controls(B3Base):

    def test_control_valid_text_records_load_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            records = [
                {"run_id": "a-run", "marker": "one"},
                {"run_id": "b-run", "marker": "two"},
            ]
            write_json(path, {"store_kind": "sweep", "records": records})
            with self.assertRaises(mod10.LookupFailure) as caught:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertIn("could not be read as a store",
                          caught.exception.args[0])
            self.assertIn("integrity signal stands absent",
                          caught.exception.args[0])

    def test_control_valid_integer_forms_load_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            records = [
                {"run_id": 10, "amount": 12345},
                {"run_id": 2, "amount": 7},
            ]
            write_json(path, {"store_kind": "sweep", "records": records})
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(store.index(), [10, 2])
            self.assertEqual(store.read_run_record(10), records[0])

    def test_control_valid_run_identifier_form_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            records = [{"run_identifier": "x-run", "marker": "x"}]
            write_json(path, {"store_kind": "sweep", "records": records})
            with self.assertRaises(mod10.LookupFailure) as caught:
                mod10.new_store(store_kind="sweep", path=path)
            self.assertIn("could not be read as a store",
                          caught.exception.args[0])
            self.assertIn("integrity signal stands absent",
                          caught.exception.args[0])

    def test_control_empty_records_file_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep", "records": []})
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(store.index(), [])

    def test_control_missing_file_constructs_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "absent.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(store.index(), [])

    def test_control_malformed_json_named_load_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, "{not json")
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_control_wrong_shape_list_named_load_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, [1, 2, 3])
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_control_missing_records_key_named_load_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep"})
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_control_flush_disk_reading_named_failure_standing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep", "records": []})
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            write_raw(path, big_identifier_text("run_id"))
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record({"run_id": "new-run", "marker": "n"})
            self.assertNotIsInstance(ctx.exception, mod10.LookupFailure)
            self.assertIn("recorder store flush failure", str(ctx.exception))
            self.assertFalse(store.has_run_record("new-run"))
            self.assertEqual(store.index(), [])
            self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()
