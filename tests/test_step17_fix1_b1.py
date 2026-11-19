"""Step 17 fix wave 1, Builder 1 tests: the mod10 store core rows
FW-01, FW-02, FW-10, FW-11, FW-12, FW-13, FW-20, FW-35, and FW-42.

Each test reproduces the defect its row names on the base tree and
passes on the fixed tree. File stores stand built in temporary
directories only. Standard library only.
"""
import json
import math
import os
import tempfile
import threading
import unittest

from crucible import mod10


def write_store_file(path, records, kind="sweep", extra=None):
    payload = {"store_kind": kind, "records": records}
    if extra:
        payload.update(extra)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def deep_record(depth):
    record = {"run_id": "b1-deep"}
    node = record
    for _ in range(depth):
        node["nest"] = {}
        node = node["nest"]
    node["leaf"] = 1
    return record


class TempDirBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "store.json")


class TestFW01LoadGuards(TempDirBase):
    """FW-01 (T17-01): the store file load path applies the
    retention guards, refusing a barred file in the named store
    file form and losing no record in silence."""

    def test_load_duplicate_identifier_refused(self):
        write_store_file(self.path, [
            {"run_id": "b1-dup", "v": 1},
            {"run_id": "b1-dup", "v": 2},
        ])
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_load_missing_identifier_refused(self):
        write_store_file(self.path, [{"v": 1}])
        with self.assertRaises(mod10.LookupFailure):
            mod10.RecorderStore(store_kind="sweep", path=self.path)

    def test_load_empty_identifier_refused(self):
        write_store_file(self.path, [{"run_id": "", "v": 1}])
        with self.assertRaises(mod10.LookupFailure):
            mod10.RecorderStore(store_kind="sweep", path=self.path)

    def test_load_nontext_identifier_refused(self):
        write_store_file(self.path, [{"run_id": 7, "v": 1}])
        with self.assertRaises(mod10.LookupFailure):
            mod10.RecorderStore(store_kind="sweep", path=self.path)

    def test_load_real_money_record_refused(self):
        write_store_file(self.path, [
            {"run_id": "b1-money", "amount": 5, "currency": "USD"},
        ])
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_load_deep_record_refused(self):
        write_store_file(self.path, [deep_record(120)])
        with self.assertRaises(mod10.LookupFailure):
            mod10.RecorderStore(store_kind="sweep", path=self.path)

    def test_load_clean_file_opens(self):
        write_store_file(self.path, [{"run_id": "b1-clean", "v": 1}])
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(store.read_run_record("b1-clean"),
                         {"run_id": "b1-clean", "v": 1})


class TestFW02Integrity(TempDirBase):
    """FW-02 (T17-02): the file backed store carries an integrity
    signal over its records, checked at load."""

    def test_integrity_signal_written(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-int", "v": 1})
        with open(self.path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        self.assertIn("integrity", payload)
        self.assertTrue(payload["integrity"])

    def test_tampered_file_refused_at_load(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-tamper", "v": 1})
        with open(self.path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        payload["records"][0]["v"] = 999
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])


class TestFW10TwoInstances(TempDirBase):
    """FW-10 (T17-12): two live store objects on one file path
    stand reconciled; no silent loss, destruction, or
    resurrection, and a stale clear takes no foreign record."""

    def test_cross_instance_read_reconciled(self):
        first = mod10.RecorderStore(store_kind="sweep", path=self.path)
        second = mod10.RecorderStore(store_kind="sweep", path=self.path)
        first.retain_run_record({"run_id": "b1-x1", "v": 1})
        self.assertEqual(second.read_run_record("b1-x1"),
                         {"run_id": "b1-x1", "v": 1})

    def test_cross_instance_duplicate_refused(self):
        first = mod10.RecorderStore(store_kind="sweep", path=self.path)
        second = mod10.RecorderStore(store_kind="sweep", path=self.path)
        first.retain_run_record({"run_id": "b1-x2", "v": 1})
        with self.assertRaises(ValueError):
            second.retain_run_record({"run_id": "b1-x2", "v": 2})
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(fresh.read_run_record("b1-x2"),
                         {"run_id": "b1-x2", "v": 1})

    def test_stale_clear_takes_no_foreign_record(self):
        first = mod10.RecorderStore(store_kind="sweep", path=self.path)
        stale = mod10.RecorderStore(store_kind="sweep", path=self.path)
        first.retain_run_record({"run_id": "b1-x3", "v": 1})
        stale.clear()
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(fresh.read_run_record("b1-x3"),
                         {"run_id": "b1-x3", "v": 1})

    def test_cleared_record_not_resurrected_by_stale_retain(self):
        first = mod10.RecorderStore(store_kind="sweep", path=self.path)
        first.retain_run_record({"run_id": "b1-x4", "v": 1})
        stale = mod10.RecorderStore(store_kind="sweep", path=self.path)
        first.clear()
        stale.retain_run_record({"run_id": "b1-x5", "v": 2})
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        with self.assertRaises(mod10.LookupFailure):
            fresh.read_run_record("b1-x4")
        self.assertEqual(fresh.read_run_record("b1-x5"),
                         {"run_id": "b1-x5", "v": 2})


class TestFW11ConcurrentRetain(TempDirBase):
    """FW-11 (T17-13): concurrent retention on one store instance
    stands safe or refused in named form, deterministically."""

    def test_concurrent_retain_all_land(self):
        for trial in range(3):
            path = os.path.join(
                self._tmp.name, "conc-%d.json" % trial)
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            errors = []
            barrier = threading.Barrier(8)

            def worker(slot):
                barrier.wait()
                for step in range(50):
                    try:
                        store.retain_run_record(
                            {"run_id": "b1-c-%d-%d" % (slot, step)})
                    except Exception as exc:
                        errors.append(exc)

            threads = [
                threading.Thread(target=worker, args=(slot,))
                for slot in range(8)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(errors, [])
            fresh = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(len(fresh.index()), 400)


class TestFW12KindCheck(TempDirBase):
    """FW-12 (T17-14): opening a store file under a kind that
    differs from the kind label the file carries stands refused
    in named form."""

    def test_kind_mismatch_refused(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-kind", "v": 1})
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="pilot", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_kind_match_opens(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-kind2", "v": 1})
        reopened = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(reopened.read_run_record("b1-kind2"),
                         {"run_id": "b1-kind2", "v": 1})


class TestFW13OpenDoors(TempDirBase):
    """FW-13 (T17-15): the store open and load doors deliver every
    path and file failure in the module named failure form."""

    def test_directory_path_named_failure(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self._tmp.name)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_permission_denied_path_named_failure(self):
        write_store_file(self.path, [{"run_id": "b1-perm", "v": 1}])
        os.chmod(self.path, 0)
        self.addCleanup(os.chmod, self.path, 0o600)
        with self.assertRaises(mod10.LookupFailure):
            mod10.RecorderStore(store_kind="sweep", path=self.path)


class TestFW20WriterForm(TempDirBase):
    """FW-20 (T17-24): the store writer carries one stated form
    for keys and values across both store forms, and its refusals
    speak in the module named form."""

    def test_mixed_type_keys_written_by_stored_text(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record(
            {"run_id": "b1-w1", "data": {1: "a", "b": 2, False: "f"}})
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(
            fresh.read_run_record("b1-w1"),
            {"run_id": "b1-w1",
             "data": {"1": "a", "b": 2, "false": "f"}})

    def test_nonfinite_value_refused_in_named_form(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(
                {"run_id": "b1-w2", "v": float("nan")})
        self.assertIn("non finite", str(caught.exception))
        self.assertFalse(store.has_run_record("b1-w2"))

    def test_nonfinite_key_refused_in_named_form(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(
                {"run_id": "b1-w3",
                 "data": {float("inf"): "a", float("-inf"): "b"}})
        self.assertIn("non finite", str(caught.exception))

    def test_nan_keys_not_silently_merged(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "b1-w4",
                 "data": {float("nan"): "a", float("nan"): "b"}})

    def test_big_int_value_written_whole(self):
        big = 10 ** 5000
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-w5", "v": big})
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(fresh.read_run_record("b1-w5"),
                         {"run_id": "b1-w5", "v": big})

    def test_big_int_key_written_whole(self):
        big = 10 ** 5000
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-w6", "data": {big: "a"}})
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(fresh.read_run_record("b1-w6"),
                         {"run_id": "b1-w6", "data": {str(big): "a"}})

    def test_written_file_is_strict_json(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-w7", "v": 1.5})

        def refuse_constant(text):
            raise ValueError("non strict token " + text)

        with open(self.path, "r", encoding="utf-8") as handle:
            payload = json.load(handle, parse_constant=refuse_constant)
        self.assertEqual(payload["records"][0]["v"], 1.5)

    def test_index_order_survives_flush_and_reload(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-w8-zeta"})
        store.retain_run_record({"run_id": "b1-w8-alpha"})
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(fresh.index(), ["b1-w8-zeta", "b1-w8-alpha"])


class TestFW35FlushText(TempDirBase):
    """FW-35 (T17-40): the flush refusal text states the file
    standing as it stands."""

    def test_flush_refusal_no_prior_file_states_none(self):
        path = os.path.join(self._tmp.name, "missing-dir", "store.json")
        store = mod10.RecorderStore(store_kind="sweep", path=path)
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record({"run_id": "b1-f1", "v": 1})
        text = str(caught.exception)
        self.assertIn("no store file stands", text)
        self.assertNotIn("prior store file stands whole", text)

    def test_flush_refusal_prior_file_states_whole(self):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        store.retain_run_record({"run_id": "b1-f2", "v": 1})
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record({"run_id": "b1-f3", "v": object()})
        self.assertIn("prior store file stands whole",
                      str(caught.exception))


class TestFW42LookupRendering(unittest.TestCase):
    """FW-42 (T17-52): the lookup failure forms render the
    identifier handed in and the store kind searched, from the
    failure record, adding no next step clause."""

    def setUp(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)

    def test_store_read_names_kind_searched(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.read_run_record("b1-absent", store_kind="pilot")
        failure = caught.exception
        self.assertIn("pilot", failure.args[0])
        self.assertEqual(failure.failure["record_kind"], "pilot")
        self.assertEqual(failure.failure["run_identifier"], "b1-absent")

    def test_list_identifier_rendered(self):
        store = mod10.new_store("sweep")
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.read_run_record(["alpha", "beta"])
        self.assertIn("alpha", caught.exception.args[0])
        self.assertIn("sweep", caught.exception.args[0])

    def test_none_identifier_rendered(self):
        failure = mod10.LookupFailure(None)
        self.assertIn("None", failure.args[0])

    def test_empty_identifier_rendered(self):
        failure = mod10.LookupFailure("")
        self.assertIn("''", failure.args[0])

    def test_none_store_kind_rendered_in_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup(store_kinds=(None,), key="b1-x")
        self.assertIn("None", str(caught.exception))

    def test_pinned_plain_message_stands(self):
        failure = mod10.LookupFailure("run-x")
        self.assertEqual(
            failure.args[0], "one lookup resolution failure: run-x")


if __name__ == "__main__":
    unittest.main()
