"""Pins for fix wave 28, builder b1: row R28-001 of the
Round 28 register.

R28-001: the cured iterative writer at crucible/mod10.py
RecorderStore._flush renders non text dict keys unquoted,
an int key through int.__repr__, a float key through
json.dumps, and bool and None keys as the bare literals
true, false, and null, so a guard accepted retention
carrying such a key reports DELIVERED while the written
store file is not JSON, and reopening raises the named
LookupFailure with every record of the store unreachable.
The landed json.dump writing delivered the same handings
whole with keys in the quoted json key form. The cure
stands at the writer key rendering step alone: every
admissible key (str, int, float including the NaN and
Infinity forms, bool, None) renders exactly as the landed
json.dump writing rendered it, in the quoted json key
form. Nothing else in the writer changes: not the sorting
step, not the depth walk, not the scalar leaf rendering,
not the error forms, and not any limit.

Sorting note, stated in the open: a dict mixing text keys
with non text keys, and a dict mixing bool and None keys,
raise at the sorting step inside the writer, in the same
standing the standard json writing raises at its sort, at
both poles. Those mixed forms therefore stand in this file
as controls standing as before, not as delivered handings.
The delivered mixed distinguishing handing of this file
mixes non text key types that sort together (int, float,
and bool keys in one dict).

Basis: every pole of this file stands proved on the PC
bench interpreter, Python 3.14.4, recursion limit 1,000
and integer limit 4,300, the suite route the standing
orders charge. Carry 6 stands beside the deep controls:
on the bench, Python 3.14.4, a store file nested 10,000
deep loads whole inside the guarded json.load reading
where Python 3.12.3 raises RecursionError, so the four
b3 depth pins of earlier waves cannot pass on the bench
in any composition; the deep controls here stand at
1,000 and 2,500 deep, inside the register band.

Distinguishing pins fail on the pristine basis and pass
on the cured copy. Control pins pass on both trees.
Distinguishing count: 12. Control count: 12.
"""
import json
import os
import sys
import tempfile
import unittest

from crucible import mod10

FLUSH = "recorder store flush failure"
NAN = float("nan")
INF = float("inf")


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


def measure_list_depth(value):
    depth = 0
    node = value
    while isinstance(node, list):
        depth += 1
        node = node[0]
    return depth, node


def round_tripped(value):
    return json.loads(json.dumps(value, sort_keys=True))


class B1Base(unittest.TestCase):

    def make_store(self, tmp):
        path = os.path.join(tmp, "store.json")
        write_json(path, {"store_kind": "sweep", "records": [
            {"run_id": "kept", "marker": "k"}]})
        store = mod10.RecorderStore(store_kind="sweep", path=path)
        self.assertEqual(store.index(), ["kept"])
        return store, path

    def assert_field_delivered_whole(self, field):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
            record = {"run_id": "new1", "field": field}
            result = store.retain_run_record(record)
            self.assertEqual(result["run_id"], "new1")
            self.assertEqual(store.index(), ["kept", "new1"])
            self.assertTrue(store.has_run_record("new1"))
            expected_records = [
                {"run_id": "kept", "marker": "k"},
                {"run_id": "new1", "field": field}]
            expected_payload = {
                "store_kind": "sweep", "records": expected_records}
            with open(path, "rb") as handle:
                raw = handle.read()
            self.assertEqual(
                raw,
                json.dumps(
                    expected_payload, sort_keys=True).encode("utf-8"))
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.assertEqual(data["store_kind"], "sweep")
            self.assertEqual(len(data["records"]), 2)
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(reopened.index(), ["kept", "new1"])
            self.assertEqual(
                reopened.read_run_record("kept"),
                {"run_id": "kept", "marker": "k"})
            self.assertEqual(
                reopened.read_run_record("new1"),
                {"run_id": "new1", "field": round_tripped(field)})


class TestR28001Distinguishing(B1Base):

    def test_distinguishing_int_key_single(self):
        self.assert_field_delivered_whole({5: "x"})

    def test_distinguishing_int_keys_plain_negative_big(self):
        self.assert_field_delivered_whole(
            {-5: "neg", 0: "zero", 42: "plain", 10 ** 20: "big"})

    def test_distinguishing_float_keys_plain(self):
        self.assert_field_delivered_whole(
            {1.5: "a", -2.5: "b", 3.0: "c"})

    def test_distinguishing_float_key_nan(self):
        self.assert_field_delivered_whole({NAN: "x"})

    def test_distinguishing_float_key_infinity(self):
        self.assert_field_delivered_whole({INF: "x"})

    def test_distinguishing_float_key_minus_infinity(self):
        self.assert_field_delivered_whole({-INF: "x"})

    def test_distinguishing_float_key_negative_zero(self):
        self.assert_field_delivered_whole({-0.0: "x", 1.5: "y"})

    def test_distinguishing_bool_keys_both_distinct(self):
        self.assert_field_delivered_whole({True: "yes", False: "no"})

    def test_distinguishing_none_key(self):
        self.assert_field_delivered_whole({None: "x"})

    def test_distinguishing_mixed_nontext_keys_one_dict(self):
        self.assert_field_delivered_whole(
            {2: "int", 2.5: "float", False: "bool"})

    def test_distinguishing_nontext_key_nested_at_depth(self):
        node = {7: "bottom"}
        for _ in range(12):
            node = {"level": node}
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
            store.retain_run_record({"run_id": "new1", "field": node})
            with open(path, "rb") as handle:
                raw = handle.read()
            expected_payload = {
                "store_kind": "sweep",
                "records": [
                    {"run_id": "kept", "marker": "k"},
                    {"run_id": "new1", "field": node}]}
            self.assertEqual(
                raw,
                json.dumps(
                    expected_payload, sort_keys=True).encode("utf-8"))
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            seen = reopened.read_run_record("new1")["field"]
            for _ in range(12):
                seen = seen["level"]
            self.assertEqual(seen, {"7": "bottom"})

    def test_distinguishing_second_retention_after_nontext(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record(
                {"run_id": "new1", "field": {11: "x"}})
            store.retain_run_record({"run_id": "new2", "marker": 2})
            self.assertEqual(store.index(), ["new1", "new2"])
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.assertEqual(len(data["records"]), 2)
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(reopened.index(), ["new1", "new2"])
            self.assertEqual(
                reopened.read_run_record("new1"),
                {"run_id": "new1", "field": {"11": "x"}})
            self.assertEqual(
                reopened.read_run_record("new2"),
                {"run_id": "new2", "marker": 2})


class TestR28001Controls(B1Base):

    def test_control_plain_text_keys_whole(self):
        self.assert_field_delivered_whole(
            {"a": 1, "b": [1, 2], "c": {"d": "e"}})

    def test_control_deep_1000_loaded_retains_plain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(1000))
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            with open(path, "r", encoding="utf-8") as handle:
                records = json.load(handle)["records"]
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_list_depth(
                by_id["deep-run"]["field"])
            self.assertEqual(seen, 1000)
            self.assertEqual(innermost, 1)

    def test_control_deep_2500_loaded_retains_plain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(2500))
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            with open(path, "r", encoding="utf-8") as handle:
                records = json.load(handle)["records"]
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_list_depth(
                by_id["deep-run"]["field"])
            self.assertEqual(seen, 2500)
            self.assertEqual(innermost, 1)

    def test_control_circular_retention_refused_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            cyclic = {"run_id": "new1"}
            cyclic["self"] = cyclic
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(cyclic)
            self.assertIn(
                "deep or cyclic record in named form",
                str(ctx.exception))
            self.assertEqual(store.index(), [])

    def test_control_circular_writer_error_form(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
            with open(path, "rb") as handle:
                before = handle.read()
            cyclic = {"run_id": "circ"}
            cyclic["self"] = cyclic
            store._records["circ"] = cyclic
            with self.assertRaises(ValueError) as ctx:
                store._flush()
            self.assertIn(
                "Circular reference detected", str(ctx.exception))
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)
            self.assertFalse(os.path.exists(path + ".tmp"))

    def test_control_bad_key_tuple_flush_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
            with open(path, "rb") as handle:
                before = handle.read()
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "field": {(1, 2): "x"}})
            self.assertIn(FLUSH, str(ctx.exception))
            self.assertIn(
                "keys must be str, int, float, bool or None",
                str(ctx.exception))
            self.assertFalse(store.has_run_record("new1"))
            self.assertEqual(store.index(), ["kept"])
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_control_unserializable_leaf_flush_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
            with open(path, "rb") as handle:
                before = handle.read()
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "blob": object()})
            self.assertIn(FLUSH, str(ctx.exception))
            self.assertIn(
                "is not JSON serializable", str(ctx.exception))
            self.assertFalse(store.has_run_record("new1"))
            self.assertEqual(store.index(), ["kept"])
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_control_blocked_tmp_path_flush_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
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

    def test_control_mixed_text_int_keys_sort_standing(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
            with open(path, "rb") as handle:
                before = handle.read()
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "field": {"a": 1, 5: "x"}})
            self.assertIn(FLUSH, str(ctx.exception))
            self.assertIsInstance(ctx.exception.__cause__, TypeError)
            self.assertFalse(store.has_run_record("new1"))
            self.assertEqual(store.index(), ["kept"])
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_control_mixed_bool_none_keys_sort_standing(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.make_store(tmp)
            with open(path, "rb") as handle:
                before = handle.read()
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(
                    {"run_id": "new1", "field": {True: "a", None: "b"}})
            self.assertIn(FLUSH, str(ctx.exception))
            self.assertIsInstance(ctx.exception.__cause__, TypeError)
            self.assertFalse(store.has_run_record("new1"))
            self.assertEqual(store.index(), ["kept"])
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_control_missing_and_empty_stores_plain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "absent.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            with open(path, "r", encoding="utf-8") as handle:
                self.assertEqual(len(json.load(handle)["records"]), 1)
            path2 = os.path.join(tmp, "empty.json")
            write_json(path2, {"store_kind": "sweep", "records": []})
            store2 = mod10.RecorderStore(store_kind="sweep", path=path2)
            store2.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(store2.index(), ["new1"])

    def test_control_limits_stand_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            self.assertEqual(sys.getrecursionlimit(), 1000)
            self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()
