"""Pins for fix wave 26, builder b2: row R26-002 of the
Round 26 register.

R26-002: the RecorderStore.__init__ record iteration past
the store file load guard stands outside the guard, so a
hand written store file whose records value stands in no
record form (records as int, null, text, or mapping; list
entries as integer, null, text, or list), or a record with
an unhashable list or dict run_id, escapes bare
AttributeError or TypeError instead of the named
LookupFailure the guard stated form promises for a store
file that could not be read as a store. The cure stands at
the construction load act alone: those handings deliver
the same named LookupFailure, in its landed wording, that
construction already delivers for its other load failures.

Distinguishing pins fail on the pristine basis and pass on
the cured copy. Control pins pass on both trees.
"""
import json
import os
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


class B2Base(unittest.TestCase):

    def assert_named_load_failure(self, exc, path):
        self.assertIsInstance(exc, mod10.LookupFailure)
        self.assertIn("could not be read as a store", str(exc))
        self.assertIn("the store file at " + path, str(exc))
        self.assertEqual(exc.failure["name"], "one lookup resolution failure")
        self.assertEqual(exc.failure["run_status"], "failed")
        self.assertEqual(exc.failure["complete"], False)
        self.assertEqual(exc.failure["store_path"], path)

    def assert_payload_named_failure(self, payload):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, payload)
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)


class TestR26002Distinguishing(B2Base):

    def test_distinguishing_records_int(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": 123})

    def test_distinguishing_records_null(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": None})

    def test_distinguishing_records_text(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": "abc"})

    def test_distinguishing_records_mapping(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": {"run_id": "a"}})

    def test_distinguishing_entry_integer(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": [123]})

    def test_distinguishing_entry_null(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": [None]})

    def test_distinguishing_entry_text(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": ["a-run"]})

    def test_distinguishing_entry_list(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep", "records": [["a-run"]]})

    def test_distinguishing_run_id_list_unhashable(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep",
             "records": [{"run_id": ["a", "b"], "marker": "x"}]})

    def test_distinguishing_run_id_dict_unhashable(self):
        self.assert_payload_named_failure(
            {"store_kind": "sweep",
             "records": [{"run_id": {"x": 1}, "marker": "x"}]})


class TestR26002Controls(B2Base):

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

    def test_control_beyond_limit_identifier_named_load_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_identifier_text("run_id"))
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)

    def test_control_beyond_limit_ordinary_new_store_named_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_ordinary_text())
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.new_store(store_kind="sweep", path=path)
            self.assert_named_load_failure(ctx.exception, path)


if __name__ == "__main__":
    unittest.main()
