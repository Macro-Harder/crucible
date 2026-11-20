"""Step 17 fix wave 4, Builder 1 defect tests, Slice 1.

Rows FW4-01, FW4-07, FW4-12, FW4-13, and FW4-14, at the mod10
store telling and open doors. Each defect test reproduces the
filing defect of its row on the uncured tree and passes on the
cured tree. Controls pass on both trees.
Copyright: J.P. Picard aka Macro-Harder.
"""
import os
import shutil
import unittest
import uuid
from unittest import mock

import crucible.mod10 as mod10


class local_temp_dir:
    def __enter__(self):
        base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".fix4b1_tmp")
        self.path = os.path.join(
            base, "case-%d-%s" % (os.getpid(), uuid.uuid4().hex[:12]))
        os.makedirs(self.path, exist_ok=True)
        return self.path

    def __exit__(self, *exc):
        shutil.rmtree(self.path, ignore_errors=True)
        return False


class B1Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestFW401ReloadNamedForm(B1Base):
    def test_fw401_retention_armed_serializer_named_flush_form(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "run-fw4-a"})
            with mock.patch(
                    "crucible.mod10.json.dumps",
                    side_effect=OSError("interrupted")):
                with self.assertRaises(ValueError) as caught:
                    store.retain_run_record({"run_id": "run-fw4-b"})
            text = str(caught.exception)
            self.assertIn("recorder store flush failure", text)
            self.assertIn("prior store file stands whole", text)
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(
                reopened.read_run_record("run-fw4-a"),
                {"run_id": "run-fw4-a"})
            with self.assertRaises(mod10.LookupFailure):
                reopened.read_run_record("run-fw4-b")

    def test_fw401_reload_reading_armed_serializer_named_store_form(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            first = mod10.RecorderStore(store_kind="sweep", path=path)
            first.retain_run_record({"run_id": "run-fw4-a"})
            second = mod10.RecorderStore(store_kind="sweep", path=path)
            second.retain_run_record({"run_id": "run-fw4-b"})
            with mock.patch(
                    "crucible.mod10.json.dumps",
                    side_effect=OSError("interrupted")):
                with self.assertRaises(mod10.LookupFailure) as caught:
                    first.read_run_record("run-fw4-a")
            text = caught.exception.args[0]
            self.assertIn("could not be read as a store", text)

    def test_fw401_fresh_open_armed_serializer_named_store_form(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "run-fw4-a"})
            with mock.patch(
                    "crucible.mod10.json.dumps",
                    side_effect=OSError("interrupted")):
                with self.assertRaises(mod10.LookupFailure) as caught:
                    mod10.RecorderStore(store_kind="sweep", path=path)
            text = caught.exception.args[0]
            self.assertIn("could not be read as a store", text)

    def test_fw401_reload_has_armed_serializer_named_store_form(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            first = mod10.RecorderStore(store_kind="sweep", path=path)
            first.retain_run_record({"run_id": "run-fw4-a"})
            second = mod10.RecorderStore(store_kind="sweep", path=path)
            second.retain_run_record({"run_id": "run-fw4-b"})
            with mock.patch(
                    "crucible.mod10.json.dumps",
                    side_effect=OSError("interrupted")):
                with self.assertRaises(mod10.LookupFailure) as caught:
                    first.has_run_record("run-fw4-a")
            text = caught.exception.args[0]
            self.assertIn("could not be read as a store", text)


class TestFW407NewStorePathForm(B1Base):
    def _check_no_path_form(self, handed):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.new_store(store_kind="sweep", path=handed)
        text = caught.exception.args[0]
        self.assertIn("could not be read as a store", text)
        self.assertIn("next step", text)
        self.assertIn("path", text)

    def test_fw407_list_path_refused_named_form(self):
        self._check_no_path_form(["store.json"])

    def test_fw407_dict_path_refused_named_form(self):
        self._check_no_path_form({"path": "store.json"})

    def test_fw407_float_path_refused_named_form(self):
        self._check_no_path_form(1.5)

    def test_fw407_integer_path_refused_and_no_store_created(self):
        self._check_no_path_form(7)


class TestFW412LookupFailureTelling(B1Base):
    def test_fw412_missing_record_printed_form_has_no_keyerror_quoting(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.read_run_record("run-fw4-missing")
        printed = str(caught.exception)
        self.assertFalse(printed.startswith("'"))
        self.assertFalse(printed.startswith('"'))
        self.assertTrue(
            printed.startswith(mod10.ONE_LOOKUP_FAILURE_NAME + ":"))
        self.assertIn("run-fw4-missing", printed)

    def test_fw412_missing_record_states_next_step(self):
        store = mod10.RecorderStore(store_kind="sweep")
        store.retain_run_record({"run_id": "run-fw4-kept"})
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.read_run_record("run-fw4-missing")
        printed = str(caught.exception)
        self.assertIn("next step", printed)
        self.assertIn("check", printed)
        self.assertIn("retained", printed)


class TestFW413StoreOpenFailureName(B1Base):
    def test_fw413_directory_open_carries_own_failure_name(self):
        with local_temp_dir() as tmp:
            with self.assertRaises(mod10.LookupFailure) as caught:
                mod10.new_store(store_kind="sweep", path=tmp)
            failure = caught.exception.failure
            self.assertNotEqual(
                failure["name"], mod10.ONE_LOOKUP_FAILURE_NAME)
            text = caught.exception.args[0]
            self.assertFalse(
                text.startswith(mod10.ONE_LOOKUP_FAILURE_NAME))
            self.assertIn("directory", text)
            self.assertIn("next step", text)

    def test_fw413_plain_file_open_carries_own_failure_name(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "plain.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("plain text, not a store")
            with self.assertRaises(mod10.LookupFailure) as caught:
                mod10.new_store(store_kind="sweep", path=path)
            failure = caught.exception.failure
            self.assertNotEqual(
                failure["name"], mod10.ONE_LOOKUP_FAILURE_NAME)
            text = caught.exception.args[0]
            self.assertFalse(
                text.startswith(mod10.ONE_LOOKUP_FAILURE_NAME))
            self.assertIn("next step", text)


class TestFW414FlushMissingDirectory(B1Base):
    def test_fw414_retain_flush_sentence_names_handed_path(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "missing-dir", "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            with self.assertRaises(ValueError) as caught:
                store.retain_run_record({"run_id": "run-fw4-a"})
            text = str(caught.exception)
            self.assertIn(path, text)
            self.assertIn("directory", text)
            self.assertIn("next step", text)
            self.assertIn("must stand first", text)
            self.assertNotIn(".tmp-", text)

    def test_fw414_clear_flush_sentence_names_handed_path(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "missing-dir", "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            with self.assertRaises(ValueError) as caught:
                store.clear()
            text = str(caught.exception)
            self.assertIn(path, text)
            self.assertIn("directory", text)
            self.assertIn("must stand first", text)
            self.assertNotIn(".tmp-", text)


class TestB1Controls(B1Base):
    def test_control_plain_retain_and_read_whole(self):
        store = mod10.RecorderStore(store_kind="sweep")
        store.retain_run_record({"run_id": "run-fw4-control"})
        self.assertEqual(
            store.read_run_record("run-fw4-control"),
            {"run_id": "run-fw4-control"})

    def test_control_valid_file_path_opens_and_retains(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.new_store(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "run-fw4-control"})
            reopened = mod10.new_store(store_kind="sweep", path=path)
            self.assertEqual(
                reopened.read_run_record("run-fw4-control"),
                {"run_id": "run-fw4-control"})

    def test_control_missing_record_name_stands_lookup_name(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.read_run_record("run-fw4-missing")
        self.assertEqual(
            caught.exception.failure["name"],
            mod10.ONE_LOOKUP_FAILURE_NAME)


if __name__ == "__main__":
    unittest.main()
