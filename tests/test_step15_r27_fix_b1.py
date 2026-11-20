"""Pins for fix wave 27, builder b1: row R27-001 of the
Round 27 register.

R27-001: a store the construction guard accepts whole,
carrying a record field nested 1,000 to 5,000 deep, is write
dead at the _flush json writing: json.dump inside _flush
raises RecursionError at those depths, so every retention on
such a store fails with the named recorder store flush
failure, with clean rollback and the prior file standing
whole, where the construction reading and the _flush disk
reading each accept the same dress whole. The same dress at
500 deep retains whole. The cure stands at the _flush writing
limb alone: that handing stands delivered whole, the written
file reading back whole with the deep field intact, and no
limb outside the writing limb changes.

Basis (Carry 6): every pole of this file stands proved on the
PC bench interpreter, Python 3.14.4, recursion limit 1,000
and integer limit 4,300, the suite route the standing orders
charge. On that interpreter the defect reproduces at the
register band whole: a loaded store carrying a list nested
991 deep retains whole and one nested 993 deep stands write
dead, the band edge bracketed at 991 to 993, the same bracket
the local Python 3.12.3 probe finds. Under the per test
runner basis the pins themselves run on, the same edge
stands bracketed at 970 to 980: the 970 deep dress retains
whole and the 980 deep dress stands write dead on the
pristine tree, the runner call stack standing deeper than a
direct probe call stack. The edge pins of this file stand on
the runner basis: 970 deep as the below band control and
993 deep as the distinguishing dress. The bench interpreter
also accepts loaded stores far past the register band, and
those standings stand pinned here as bench extensions: list
dresses at 10,000 and 50,000 deep load whole on the bench,
stand write dead on the pristine tree, and stand delivered
whole after the cure. A disk file swapped to 10,000 deep
after construction fails at the writing on the bench (its
direct _flush traceback ends at the json.dump line), so the
swapped 10,000 deep handing stands distinguishing on this
basis; a disk file swapped to 100,000 deep fails at the
_flush disk reading on the bench and stands as a reading
limb control. On the local Python 3.12.3 interpreter the
construction reading refuses the 10,000 deep dress whole, so
the bench extension pins state a bench standing only, in the
Carry 6 form.

Distinguishing pins fail on the pristine basis and pass on
the cured copy. Control pins pass on both trees.
Distinguishing count: 12. Control count: 17.
"""
import json
import os
import sys
import tempfile
import unittest

from crucible import mod10

BIG = "9" * 5001
FLUSH = "recorder store flush failure"


def write_raw(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def nested_list_text(depth, run_id="deep-run"):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "' + run_id + '", "field": '
        + "[" * depth + "1" + "]" * depth + "}]}")


def nested_list_second_text(depth):
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


def big_ordinary_text():
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "plain-run", "amount": ' + BIG + "}]}")


def measure_list_depth(value):
    depth = 0
    node = value
    while isinstance(node, list):
        depth += 1
        node = node[0]
    return depth, node


def measure_dict_depth(value):
    depth = 0
    node = value
    while isinstance(node, dict):
        depth += 1
        node = node["a"]
    return depth, node


class B1Base(unittest.TestCase):

    def load_deep_store(self, tmp, depth, kind="list"):
        path = os.path.join(tmp, "store.json")
        if kind == "dict":
            write_raw(path, nested_dict_text(depth))
        else:
            write_raw(path, nested_list_text(depth))
        store = mod10.RecorderStore(store_kind="sweep", path=path)
        self.assertEqual(store.index(), ["deep-run"])
        return store, path

    def read_file_records(self, path):
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data["records"]

    def assert_retained_deep_whole(self, store, path, depth,
                                   kind="list"):
        result = store.retain_run_record(
            {"run_id": "new1", "marker": 1})
        self.assertEqual(result["run_id"], "new1")
        self.assertEqual(store.index(), ["deep-run", "new1"])
        self.assertTrue(store.has_run_record("new1"))
        self.assertEqual(
            store.read_run_record("new1"),
            {"run_id": "new1", "marker": 1})
        records = self.read_file_records(path)
        self.assertEqual(len(records), 2)
        by_id = {rec["run_id"]: rec for rec in records}
        self.assertEqual(by_id["new1"]["marker"], 1)
        if kind == "dict":
            seen, innermost = measure_dict_depth(
                by_id["deep-run"]["field"])
        else:
            seen, innermost = measure_list_depth(
                by_id["deep-run"]["field"])
        self.assertEqual(seen, depth)
        self.assertEqual(innermost, 1)


class TestR27001Distinguishing(B1Base):

    def test_distinguishing_1000_deep_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 1000)
            self.assert_retained_deep_whole(store, path, 1000)

    def test_distinguishing_2500_deep_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 2500)
            self.assert_retained_deep_whole(store, path, 2500)

    def test_distinguishing_5000_deep_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 5000)
            self.assert_retained_deep_whole(store, path, 5000)

    def test_distinguishing_993_deep_band_edge_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 993)
            self.assert_retained_deep_whole(store, path, 993)

    def test_distinguishing_1000_deep_dict_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 1000, "dict")
            self.assert_retained_deep_whole(
                store, path, 1000, "dict")

    def test_distinguishing_5000_deep_dict_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 5000, "dict")
            self.assert_retained_deep_whole(
                store, path, 5000, "dict")

    def test_distinguishing_10000_deep_bench_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 10000)
            self.assert_retained_deep_whole(store, path, 10000)

    def test_distinguishing_50000_deep_bench_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 50000)
            self.assert_retained_deep_whole(store, path, 50000)

    def test_distinguishing_second_retention_after_deep(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 5000)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            result = store.retain_run_record(
                {"run_id": "new2", "marker": 2})
            self.assertEqual(result["run_id"], "new2")
            self.assertEqual(
                store.index(), ["deep-run", "new1", "new2"])
            records = self.read_file_records(path)
            self.assertEqual(len(records), 3)
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_list_depth(
                by_id["deep-run"]["field"])
            self.assertEqual(seen, 5000)
            self.assertEqual(innermost, 1)
            self.assertEqual(by_id["new2"]["marker"], 2)

    def test_distinguishing_deep_second_record_retains(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_second_text(2500))
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(
                store.index(), ["plain-run", "deep-run"])
            store.retain_run_record({"run_id": "new1", "marker": 1})
            records = self.read_file_records(path)
            self.assertEqual(len(records), 3)
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_list_depth(
                by_id["deep-run"]["field"])
            self.assertEqual(seen, 2500)
            self.assertEqual(innermost, 1)
            self.assertEqual(by_id["plain-run"]["marker"], "plain")

    def test_distinguishing_swapped_2500_deep_retains(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(
                path, {"store_kind": "sweep", "records": []})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            write_raw(path, nested_list_text(2500))
            store.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(store.index(), ["new1"])
            records = self.read_file_records(path)
            self.assertEqual(len(records), 2)
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_list_depth(
                by_id["deep-run"]["field"])
            self.assertEqual(seen, 2500)
            self.assertEqual(innermost, 1)

    def test_distinguishing_swapped_10000_deep_bench_retains(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(
                path, {"store_kind": "sweep", "records": []})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            write_raw(path, nested_list_text(10000))
            store.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(store.index(), ["new1"])
            records = self.read_file_records(path)
            self.assertEqual(len(records), 2)
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_list_depth(
                by_id["deep-run"]["field"])
            self.assertEqual(seen, 10000)
            self.assertEqual(innermost, 1)


class TestR27001Controls(B1Base):

    def test_control_500_deep_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 500)
            self.assert_retained_deep_whole(store, path, 500)

    def test_control_970_deep_below_band_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 970)
            self.assert_retained_deep_whole(store, path, 970)

    def test_control_800_deep_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 800)
            self.assert_retained_deep_whole(store, path, 800)

    def test_control_plain_store_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep", "records": [
                {"run_id": "a-run", "marker": "one"}]})
            with self.assertRaises(mod10.LookupFailure) as caught:
                mod10.RecorderStore(
                    store_kind="sweep", path=path)
            self.assertIn("could not be read as a store",
                          caught.exception.args[0])
            self.assertIn("integrity signal stands absent",
                          caught.exception.args[0])

    def test_control_missing_file_store_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "absent.json")
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            records = self.read_file_records(path)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["run_id"], "new1")

    def test_control_empty_records_store_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(
                path, {"store_kind": "sweep", "records": []})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(store.index(), ["new1"])
            self.assertEqual(len(self.read_file_records(path)), 1)

    def test_control_beyond_limit_integer_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, big_ordinary_text())
            with self.assertRaises(mod10.LookupFailure) as ctx:
                mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertIn(
                "could not be read as a store", str(ctx.exception))
            self.assertEqual(
                ctx.exception.failure["store_path"], path)

    def test_control_swapped_beyond_limit_flush_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(
                path, {"store_kind": "sweep", "records": []})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            write_raw(path, big_ordinary_text())
            with open(path, "rb") as handle:
                before = handle.read()
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "marker": 1})
            self.assertIn(FLUSH, str(ctx.exception))
            self.assertNotIsInstance(
                ctx.exception, mod10.LookupFailure)
            self.assertFalse(store.has_run_record("new1"))
            self.assertEqual(store.index(), [])
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_control_swapped_100000_deep_flush_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(
                path, {"store_kind": "sweep", "records": []})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            write_raw(path, nested_list_text(100000))
            with open(path, "rb") as handle:
                before = handle.read()
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "marker": 1})
            self.assertIn(FLUSH, str(ctx.exception))
            self.assertIsInstance(
                ctx.exception.__cause__, RecursionError)
            self.assertFalse(store.has_run_record("new1"))
            self.assertEqual(store.index(), [])
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_control_swapped_malformed_passed_over(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep", "records": [
                {"run_id": "kept", "marker": "k"}]})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            write_raw(path, "{not json")
            store.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(store.index(), ["kept", "new1"])
            records = self.read_file_records(path)
            self.assertEqual(
                {rec["run_id"] for rec in records},
                {"kept", "new1"})

    def test_control_swapped_integer_record_passed_over(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep", "records": [
                {"run_id": "kept", "marker": "k"}]})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            write_json(path, {"store_kind": "sweep",
                              "records": [7]})
            store.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(store.index(), ["kept", "new1"])
            records = self.read_file_records(path)
            self.assertEqual(
                {rec["run_id"] for rec in records},
                {"kept", "new1"})

    def test_control_clear_on_deep_store_delivered(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 2500)
            store.clear()
            self.assertEqual(store.index(), [])
            self.assertEqual(self.read_file_records(path), [])

    def test_control_read_deep_record_named_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.load_deep_store(tmp, 500)
            self.assertTrue(store.has_run_record("deep-run"))
            with self.assertRaises(ValueError) as ctx:
                store.read_run_record("deep-run")
            self.assertIn(
                "deep or cyclic record in named form",
                str(ctx.exception))

    def test_control_unserializable_record_flush_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep", "records": [
                {"run_id": "kept", "marker": "k"}]})
            with self.assertRaises(mod10.LookupFailure) as caught:
                mod10.RecorderStore(
                    store_kind="sweep", path=path)
            self.assertIn("could not be read as a store",
                          caught.exception.args[0])
            self.assertIn("integrity signal stands absent",
                          caught.exception.args[0])

    def test_control_blocked_tmp_path_flush_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_json(path, {"store_kind": "sweep", "records": [
                {"run_id": "kept", "marker": "k"}]})
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            os.mkdir(path + ".tmp")
            with open(path, "rb") as handle:
                before = handle.read()
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "marker": 1})
            self.assertIn(FLUSH, str(ctx.exception))
            self.assertFalse(store.has_run_record("new1"))
            self.assertEqual(store.index(), ["kept"])
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_control_deep_retention_refused_named_form(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            deep = 1
            for _ in range(150):
                deep = [deep]
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "field": deep})
            self.assertIn(
                "deep or cyclic record in named form",
                str(ctx.exception))
            self.assertEqual(store.index(), [])

    def test_control_limits_stand_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(sys.getrecursionlimit(), 1000)
            self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()
