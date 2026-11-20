"""Step 17, fix wave 4, Slice 3 defect tests: FW4-03.

Row FW4-03 (Medium, T17R3-03): the file backed retention act
stands bounded in growth form, so the per act cost of a retain
stands governed by the act and not by the whole store volume
already retained, proved by measurement at rising retained
counts against the in memory control form.

The defect tests state the growth form charged and the bound
the cure states, and judge counted work, never a timing figure
as a verdict, in the FW3-06 form. The charged form: on the
uncured tree one file backed retain takes whole standing
passes over every record already retained, a serialization of
the whole records standing for the integrity signal, a second
serialization of its canonical form, a third serialization of
the whole payload, and a merge scan whose key comparisons grow
with the square of the standing. The bound the cure states:
one retain serializes no whole standing pass at all, serializes
at most BOUND_SERIALIZED_CHARS_PER_ACT characters in total
(the handed record own fragments, a small multiple of its own
size), and takes at most BOUND_KEY_COMPARISONS_PER_ACT key
comparisons, at standing 150 and at standing 300 alike, the
same bound at both standings. The remaining whole store pass a
retention act takes stands as byte passes at library speed,
the joined file text, its keyed signal over that text, and
the file write itself, which the sealed single payload format
carries, as the FW3-06 cure states for its own flush write.

Copyright: J.P. Picard aka Macro-Harder.
"""
import json
import os
import tempfile
import unittest
from unittest import mock

import crucible.mod10 as mod10

BOUND_SERIALIZED_CHARS_PER_ACT = 2000
BOUND_KEY_COMPARISONS_PER_ACT = 1000


def _record(number):
    return {"run_id": "r%04d" % number, "v": 1}


class _SerializeCounter:
    """Counts whole standing serialization passes and the total
    characters serialized while it stands installed."""

    def __init__(self, real):
        self.real = real
        self.whole_calls = 0
        self.chars = 0

    def __call__(self, payload):
        text = self.real(payload)
        if isinstance(payload, dict) and isinstance(
                payload.get("records"), list):
            self.whole_calls += 1
        self.chars += len(text)
        return text


class _EqCounter:
    """Counts key comparisons through _base_value_eq while it
    stands installed."""

    def __init__(self, real):
        self.real = real
        self.calls = 0

    def __call__(self, left, right):
        self.calls += 1
        return self.real(left, right)


def _build(path, count):
    store = mod10.new_store("sweep", path=path)
    for number in range(count):
        store.retain_run_record(_record(number))
    return store


def _measured_retain(store, record):
    serialize = _SerializeCounter(mod10._serialize_store_text)
    equals = _EqCounter(mod10._base_value_eq)
    with mock.patch.object(
            mod10, "_serialize_store_text", serialize), \
            mock.patch.object(mod10, "_base_value_eq", equals):
        store.retain_run_record(record)
    return serialize, equals


class TestFW403BoundedGrowth(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "store.json")

    def test_fw403_retain_serialization_bounded_at_rising_standings(self):
        store = _build(self.path, 150)
        serialize, _equals = _measured_retain(store, _record(150))
        self.assertEqual(serialize.whole_calls, 0)
        self.assertLessEqual(
            serialize.chars, BOUND_SERIALIZED_CHARS_PER_ACT)
        for number in range(151, 300):
            store.retain_run_record(_record(number))
        serialize, _equals = _measured_retain(store, _record(300))
        self.assertEqual(serialize.whole_calls, 0)
        self.assertLessEqual(
            serialize.chars, BOUND_SERIALIZED_CHARS_PER_ACT)

    def test_fw403_retain_key_comparisons_bounded_at_rising_standings(self):
        store = _build(self.path, 150)
        _serialize, equals = _measured_retain(store, _record(150))
        self.assertLessEqual(
            equals.calls, BOUND_KEY_COMPARISONS_PER_ACT)
        for number in range(151, 300):
            store.retain_run_record(_record(number))
        _serialize, equals = _measured_retain(store, _record(300))
        self.assertLessEqual(
            equals.calls, BOUND_KEY_COMPARISONS_PER_ACT)

    def test_fw403_batch_serialization_bounded_by_the_batch(self):
        store = _build(self.path, 300)
        serialize = _SerializeCounter(mod10._serialize_store_text)
        with mock.patch.object(
                mod10, "_serialize_store_text", serialize):
            for number in range(300, 325):
                store.retain_run_record(_record(number))
        self.assertEqual(serialize.whole_calls, 0)
        self.assertLessEqual(
            serialize.chars, 25 * BOUND_SERIALIZED_CHARS_PER_ACT)


class TestFW403Controls(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "store.json")

    def test_control_written_file_matches_reference_form(self):
        store = mod10.new_store("sweep", path=self.path)
        store.retain_run_record({"run_id": "a", "v": 1})
        store.retain_run_record({"run_id": "b", 7: "x", "v": 2})
        store.retain_run_record(
            {"run_id": "c", "pair": ("p", "q"), "v": 3})
        store.retain_run_record(
            {"run_id": "d", "big": 10 ** 5000, "f": 1.5})
        store.retain_run_record({"run_id": "e", "v": 5})
        with open(self.path, "rb") as handle:
            written = handle.read()
        reopened = mod10.new_store("sweep", path=self.path)
        loaded = [
            reopened.read_run_record(rid) for rid in reopened.index()]
        reference = mod10._serialize_store_text({
            "store_kind": "sweep",
            "records": loaded,
            "integrity": mod10._store_integrity_signal(loaded, "sweep"),
        })
        self.assertEqual(written, reference.encode("utf-8"))

    def test_control_reopen_and_second_instance_read_whole(self):
        store = _build(self.path, 40)
        reopened = mod10.new_store("sweep", path=self.path)
        self.assertEqual(len(reopened.index()), 40)
        self.assertEqual(
            reopened.read_run_record("r0039"), _record(39))
        reopened.retain_run_record(_record(40))
        self.assertEqual(store.read_run_record("r0040"), _record(40))
        self.assertEqual(len(store.index()), 41)

    def test_control_tampered_file_refused_at_open(self):
        _build(self.path, 5)
        with open(self.path, "r", encoding="utf-8") as handle:
            text = handle.read()
        tampered = text.replace('"v": 1', '"v": 9', 1)
        self.assertNotEqual(tampered, text)
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(tampered)
        with self.assertRaises(mod10.LookupFailure):
            mod10.new_store("sweep", path=self.path)

    def test_control_clear_empties_file_backed_store(self):
        store = _build(self.path, 20)
        store.clear()
        self.assertEqual(store.index(), [])
        reopened = mod10.new_store("sweep", path=self.path)
        self.assertEqual(reopened.index(), [])
        with open(self.path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        self.assertEqual(payload["records"], [])

    def test_control_failed_retention_not_served_prior_file_whole(self):
        store = _build(self.path, 10)
        with open(self.path, "rb") as handle:
            before = handle.read()
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "bad", "v": {1, 2}})
        with open(self.path, "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertFalse(store.has_run_record("bad"))
        store.retain_run_record(_record(10))
        self.assertEqual(store.read_run_record("r0010"), _record(10))

    def test_control_in_memory_store_stands_whole(self):
        store = mod10.new_store("sweep")
        for number in range(50):
            store.retain_run_record(_record(number))
        self.assertEqual(len(store.index()), 50)
        self.assertEqual(store.read_run_record("r0049"), _record(49))


if __name__ == "__main__":
    unittest.main()
