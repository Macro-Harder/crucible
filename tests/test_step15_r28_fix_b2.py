"""Pins for fix wave 28, builder b2: row R28-002 of the
Round 28 register.

R28-002: the cured iterative writer in RecorderStore._flush
sorts the dict items as (key, value) pairs, where the json
writing it replaced, json.dump of the payload with sort_keys,
sorts by the key alone, so two keys that stand equal under
equality while standing as distinct entries of one dict stand
ordered by their values in the cured writing and in their
standing entry order in the json writing. The cure stands at
the writer sorting step alone: the writer ordering stands
restated to sort by key alone as json sort_keys does,
preserving standing entry order among equal keys, and nothing
else in the writer changes.

The distinguishing construction is the Red 4 construction of
finding R28-RED4-02: the integer 1 and an int subclass key
equal to 1 whose hash stands set apart, so both entries stand
in the one dict, with string values whose value order differs
from the standing entry order. The same equal keys principle
stands dressed in a text form, a str subclass key equal to a
plain text key with its hash set apart, at which dress the
writer key rendering stands in its quoted json form at both
poles, so the expected written bytes stand stated in full. A
dict valued tie stands as a further dress: at the landed pole
the pair sorting raises on the dict values, and under the
ruled key alone ordering the entries stand delivered in
standing entry order.

Reference basis, stated in the open: the ruled ordering, sort
by key alone preserving standing entry order among equal
keys, stands as the reference for the tie dresses, taken from
ruling T28-2. A json.dumps act with sort_keys does not stand
used as the tie reference, because on the bench interpreter,
Python 3.14.4, the json encoder itself stands in the
sorted(dct.items()) form and pair sorts the tie by value, as
a probe act of this seat shows on both the bench interpreter
and the local Python 3.12.3. For plain distinct key payloads,
where the key alone and pair forms agree, the controls stand
byte identical to the json reference rendering, json.dumps
of the store payload with sort_keys, in the landed writing
form.

Distinguishing pins fail on the landed basis and pass on the
cured copy. Control pins pass on both trees.
Distinguishing count: 7. Control count: 13.
"""
import json
import os
import sys
import tempfile
import unittest
from decimal import Decimal

from crucible import mod10

FLUSH = "recorder store flush failure"


class ApartInt(int):
    """An int key equal to 1 whose hash stands set apart."""

    def __new__(cls):
        return int.__new__(cls, 1)

    def __hash__(self):
        return 99991


class ApartStr(str):
    """A text key equal to the plain key k, hash set apart."""

    def __new__(cls):
        return str.__new__(cls, "k")

    def __hash__(self):
        return 88883


def write_raw(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def value_order(text, first=b'"zzz"', second=b'"aaa"'):
    raw = text.encode("utf-8") if isinstance(text, str) else text
    return raw.index(first) < raw.index(second)


def nested_list_text(depth, run_id="deep-run"):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "' + run_id + '", "field": '
        + "[" * depth + "1" + "]" * depth + "}]}")


def nested_dict_text(depth):
    return (
        '{"store_kind": "sweep", "records": ['
        '{"run_id": "deep-run", "field": '
        + '{"a": ' * depth + "1" + "}" * depth + "}]}")


def measure_depth(value, kind):
    depth = 0
    node = value
    if kind == "list":
        while isinstance(node, list):
            depth += 1
            node = node[0]
    else:
        while isinstance(node, dict):
            depth += 1
            node = node["a"]
    return depth, node


class B2Base(unittest.TestCase):

    def tearDown(self):
        self.assertEqual(sys.getrecursionlimit(), 1000)
        self.assertEqual(sys.get_int_max_str_digits(), 4300)

    def retain_and_read(self, tmp, record):
        path = os.path.join(tmp, "store.json")
        store = mod10.RecorderStore(store_kind="sweep", path=path)
        store.retain_run_record(record)
        return store, path, read_text(path)

    def direct_store(self, tmp, record):
        path = os.path.join(tmp, "store.json")
        write_json(path, {"store_kind": "sweep", "records": []})
        store = mod10.RecorderStore(store_kind="sweep", path=path)
        store._records = {"x-run": record}
        return store, path


class TestR28002Distinguishing(B2Base):

    def test_distinguishing_int_tie_plain_entry_order(self):
        tie = {1: "zzz", ApartInt(): "aaa"}
        record = {"run_id": "tie-run", "field": tie}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertTrue(value_order(raw))
        self.assertEqual(
            raw,
            '{"records": [{"field": {"1": "zzz", "1": "aaa"}, '
            '"run_id": "tie-run"}], "store_kind": "sweep"}')
        key_only = sorted(tie.items(), key=lambda pair: pair[0])
        self.assertEqual(
            [value for _key, value in key_only], ["zzz", "aaa"])

    def test_distinguishing_int_tie_plain_reversed_entry(self):
        tie = {ApartInt(): "zzz", 1: "aaa"}
        record = {"run_id": "tie-run", "field": tie}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertTrue(value_order(raw))
        self.assertEqual(
            raw,
            '{"records": [{"field": {"1": "zzz", "1": "aaa"}, '
            '"run_id": "tie-run"}], "store_kind": "sweep"}')
        key_only = sorted(tie.items(), key=lambda pair: pair[0])
        self.assertEqual(
            [value for _key, value in key_only], ["zzz", "aaa"])

    def test_distinguishing_int_tie_nested_entry_order(self):
        tie = {1: "zzz", ApartInt(): "aaa"}
        record = {"run_id": "tie-run",
                  "field": {"outer": [{"inner": tie}]}}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertTrue(value_order(raw))
        self.assertEqual(
            raw,
            '{"records": [{"field": {"outer": [{"inner": '
            '{"1": "zzz", "1": "aaa"}}]}, "run_id": "tie-run"}], '
            '"store_kind": "sweep"}')
        key_only = sorted(tie.items(), key=lambda pair: pair[0])
        self.assertEqual(
            [value for _key, value in key_only], ["zzz", "aaa"])

    def test_distinguishing_int_tie_nested_reversed_entry(self):
        tie = {ApartInt(): "zzz", 1: "aaa"}
        record = {"run_id": "tie-run",
                  "field": {"outer": {"inner": tie}}}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertTrue(value_order(raw))
        self.assertEqual(
            raw,
            '{"records": [{"field": {"outer": {"inner": '
            '{"1": "zzz", "1": "aaa"}}}, "run_id": "tie-run"}], '
            '"store_kind": "sweep"}')
        key_only = sorted(tie.items(), key=lambda pair: pair[0])
        self.assertEqual(
            [value for _key, value in key_only], ["zzz", "aaa"])

    def test_distinguishing_text_tie_plain_byte_reference(self):
        tie = {"k": "zzz", ApartStr(): "aaa"}
        record = {"run_id": "tie-run", "field": tie}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertEqual(
            raw,
            '{"records": [{"field": {"k": "zzz", "k": "aaa"}, '
            '"run_id": "tie-run"}], "store_kind": "sweep"}')
        key_only = sorted(tie.items(), key=lambda pair: pair[0])
        self.assertEqual(
            [value for _key, value in key_only], ["zzz", "aaa"])

    def test_distinguishing_text_tie_nested_byte_reference(self):
        tie = {ApartStr(): "zzz", "k": "aaa"}
        record = {"run_id": "tie-run",
                  "field": {"outer": [tie]}}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertEqual(
            raw,
            '{"records": [{"field": {"outer": [{"k": "zzz", '
            '"k": "aaa"}]}, "run_id": "tie-run"}], '
            '"store_kind": "sweep"}')
        key_only = sorted(tie.items(), key=lambda pair: pair[0])
        self.assertEqual(
            [value for _key, value in key_only], ["zzz", "aaa"])

    def test_distinguishing_dict_valued_tie_delivered(self):
        tie = {1: {"a": 1}, ApartInt(): {"b": 2}}
        record = {"run_id": "tie-run", "field": tie}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertEqual(
            raw,
            '{"records": [{"field": {"1": {"a": 1}, "1": {"b": 2}}, '
            '"run_id": "tie-run"}], "store_kind": "sweep"}')


class TestR28002Controls(B2Base):

    def test_control_text_keys_ordering_byte_reference(self):
        field = {"b": 1, "a": 2, "m": 3}
        record = {"run_id": "plain-run", "field": field}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        reference = json.dumps(
            {"store_kind": "sweep", "records": [
                {"run_id": "plain-run", "field": field}]},
            sort_keys=True)
        self.assertEqual(raw, reference)
        self.assertIn('{"a": 2, "b": 1, "m": 3}', raw)

    def test_control_int_keys_ordering(self):
        field = {10: "y", 2: "x"}
        record = {"run_id": "plain-run", "field": field}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertEqual(
            raw,
            '{"records": [{"field": {"2": "x", "10": "y"}, '
            '"run_id": "plain-run"}], "store_kind": "sweep"}')
        reference = json.dumps(
            {"store_kind": "sweep", "records": [
                {"run_id": "plain-run", "field": field}]},
            sort_keys=True)
        self.assertTrue(
            reference.index('"x"') < reference.index('"y"'))

    def test_control_mixed_keys_in_separate_dicts(self):
        field = {
            "t": {"b": 1, "a": 2},
            "i": {10: "y", 2: "x"},
            "f": {1.5: "y", 0.5: "x"},
            "b": {True: "y", False: "x"},
            "n": {None: "only"},
        }
        record = {"run_id": "plain-run", "field": field}
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, raw = self.retain_and_read(tmp, record)
        self.assertEqual(
            raw,
            '{"records": [{"field": {'
            '"b": {"false": "x", "true": "y"}, '
            '"f": {"0.5": "x", "1.5": "y"}, '
            '"i": {"2": "x", "10": "y"}, '
            '"n": {"null": "only"}, '
            '"t": {"a": 2, "b": 1}}, '
            '"run_id": "plain-run"}], "store_kind": "sweep"}')

    def test_control_mixed_text_and_int_keys_raise(self):
        field = {"a": 1, 2: 2}
        record = {"run_id": "x-run", "field": field}
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.direct_store(tmp, record)
            before = read_text(path)
            with self.assertRaises(TypeError):
                store._flush()
            self.assertEqual(read_text(path), before)
        with self.assertRaises(TypeError):
            json.dumps(
                {"store_kind": "sweep", "records": [record]},
                sort_keys=True)

    def test_control_deep_list_1000_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_list_text(1000))
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            with open(path, "r", encoding="utf-8") as handle:
                records = json.load(handle)["records"]
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_depth(
                by_id["deep-run"]["field"], "list")
            self.assertEqual(seen, 1000)
            self.assertEqual(innermost, 1)

    def test_control_deep_dict_2500_retains_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            write_raw(path, nested_dict_text(2500))
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "new1", "marker": 1})
            with open(path, "r", encoding="utf-8") as handle:
                records = json.load(handle)["records"]
            by_id = {rec["run_id"]: rec for rec in records}
            seen, innermost = measure_depth(
                by_id["deep-run"]["field"], "dict")
            self.assertEqual(seen, 2500)
            self.assertEqual(innermost, 1)

    def test_control_plain_payload_byte_reference_and_reopen(self):
        record = {"run_id": "plain-run", "marker": "one", "n": 2}
        with tempfile.TemporaryDirectory() as tmp:
            store, path, raw = self.retain_and_read(tmp, record)
            reference = json.dumps(
                {"store_kind": "sweep", "records": [record]},
                sort_keys=True)
            self.assertEqual(raw, reference)
            fresh = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(fresh.read_run_record("plain-run"), record)
            self.assertEqual(store.index(), ["plain-run"])

    def test_control_circular_at_writing_raises(self):
        cycle = {}
        cycle["self"] = cycle
        record = {"run_id": "x-run", "field": cycle}
        with tempfile.TemporaryDirectory() as tmp:
            store, path = self.direct_store(tmp, record)
            before = read_text(path)
            with self.assertRaises(ValueError) as ctx:
                store._flush()
            self.assertIn(
                "Circular reference detected", str(ctx.exception))
            self.assertEqual(read_text(path), before)
            self.assertFalse(os.path.exists(path + ".tmp"))

    def test_control_circular_at_retention_refused(self):
        cycle = []
        cycle.append(cycle)
        record = {"run_id": "new1", "field": cycle}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(
                store_kind="sweep", path=path)
            with self.assertRaises(ValueError) as ctx:
                store.retain_run_record(record)
            self.assertIn(
                "deep or cyclic record in named form",
                str(ctx.exception))
            self.assertEqual(store.index(), [])

    def test_control_bad_keys_at_writing_raise(self):
        cases = [
            ({(1, 2): "x"}, "not tuple"),
            ({Decimal("1.5"): "x"}, "not Decimal"),
        ]
        for field, fragment in cases:
            with self.subTest(fragment=fragment):
                record = {"run_id": "x-run", "field": field}
                with tempfile.TemporaryDirectory() as tmp:
                    store, path = self.direct_store(tmp, record)
                    before = read_text(path)
                    with self.assertRaises(TypeError) as ctx:
                        store._flush()
                    self.assertIn(
                        "keys must be str, int, float, bool or None, ",
                        str(ctx.exception))
                    self.assertIn(fragment, str(ctx.exception))
                    self.assertEqual(read_text(path), before)

    def test_control_unserializable_leaf_at_writing_raises(self):
        cases = [
            ({"leaf": {1, 2}}, "set"),
            ({"leaf": object()}, "object"),
        ]
        for field, type_name in cases:
            with self.subTest(type_name=type_name):
                record = {"run_id": "x-run", "field": field}
                with tempfile.TemporaryDirectory() as tmp:
                    store, path = self.direct_store(tmp, record)
                    before = read_text(path)
                    with self.assertRaises(TypeError) as ctx:
                        store._flush()
                    self.assertIn(
                        "Object of type " + type_name
                        + " is not JSON serializable",
                        str(ctx.exception))
                    self.assertEqual(read_text(path), before)

    def test_control_unserializable_retention_flush_failure(self):
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

    def test_control_limits_stand_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            _store, _path, _raw = self.retain_and_read(
                tmp, {"run_id": "plain-run", "marker": 1})
            self.assertEqual(sys.getrecursionlimit(), 1000)
            self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()
