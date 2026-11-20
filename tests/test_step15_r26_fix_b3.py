"""Pins for fix wave 26, builder b3: row R26-003 of the
Round 26 register.

R26-003: a hand written store file nested about 10,000 deep
escapes bare RecursionError inside the RecorderStore.__init__
guarded json.load reading, a class the cured guard tuple does
not name, where the guard stated form promises the named
LookupFailure for a store file that could not be read as a
store. The same dress at 3,000 deep loads whole. The cure
stands at the construction load guard alone: that handing
delivers the same named LookupFailure, in its landed wording,
that construction already delivers for its other load
failures.

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


def nested_list_text(depth, field="field"):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "deep-run", "' + field + '": '
        + "[" * depth + "1" + "]" * depth + "}]}")


def nested_list_second_record_text(depth):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "plain-run", "marker": "plain"}, '
        '{"run_id": "deep-run", "field": '
        + "[" * depth + "1" + "]" * depth + "}]}")


def nested_dict_text(depth):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "deep-run", "field": '
        + '{"a": ' * depth + "1" + "}" * depth + "}]}")


def big_identifier_text(field="run_id"):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"' + field + '": ' + BIG + ', "marker": "big"}, '
        '{"run_id": "plain-run", "marker": "plain"}]}')


def big_ordinary_text():
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "plain-run", "amount": ' + BIG + "}]}")


class B3Base(unittest.TestCase):

    def assert_named_load_failure(self, exc, path):
        self.assertIsInstance(exc, mod10.LookupFailure)
        self.assertNotIsInstance(exc, RecursionError)
        self.assertIn("could not be read as a store", str(exc))
        self.assertIn("the store file at " + path, str(exc))
        self.assertEqual(exc.failure["name"], "one store file open failure")
        self.assertEqual(exc.failure["run_status"], "failed")
        self.assertEqual(exc.failure["complete"], False)
        self.assertEqual(exc.failure["store_path"], path)


class TestR26003Distinguishing(B3Base):

    def test_distinguishing_10000_deep_list_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(10000))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_deeper_100000_deep_list_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(100000))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_10000_deep_list_new_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(10000))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.new_store(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_10000_deep_dict_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_dict_text(10000))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_distinguishing_10000_deep_second_record_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_second_record_text(10000))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)


class TestR26003Controls(B3Base):

    def test_control_3000_deep_loads_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(3000))
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(store.index(), ["deep-run"])

    def test_control_500_deep_loads_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(500))
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(store.index(), ["deep-run"])

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

    def test_control_beyond_limit_integer_identifier_named_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_identifier_text("run_id"))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_control_beyond_limit_integer_ordinary_named_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_ordinary_text())
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
