"""Pins for fix wave 23, builder b4, Group 4: MOD-10 buffer kind
judgements, rows R23-005 and R23-006 of the Round 23 register, on
coordinator Ruling 8 at step record Entry 219.

The defect: at retain_gc08_record the kind judgement reads stored
text only where the handed value stands as str, and at store_lookup
_store_kind_stands does the same, so a buffer form (bytes,
bytearray, memoryview) storing a listed kind stands judged unknown,
while the sentence at each locus renders that same buffer through
_vocabulary_text on its stored text and names the value as unknown
while listing it in the same breath. The cure: judge the kind on
stored text for the buffer forms (str, bytes, bytearray,
memoryview) at each locus, as the companion outcome limb of
apply_flag_evaluation already judges, the sentence forms unchanged,
each locus standing test first on its own row handings.

Distinguishing pins fail on the pristine basis and pass on the
cured copy. Control pins pass on both trees.
"""
import unittest

from crucible import mod10


def buffers(text):
    raw = text.encode("utf-8")
    return (bytes(raw), bytearray(raw), memoryview(raw))


class TestR23005RetainGc08Record(unittest.TestCase):

    def check_retained(self, kind_value, plain_kind, tag):
        record = {"marker": tag}
        returned = mod10.retain_gc08_record(kind_value, record, tag)
        self.assertEqual(returned, record)
        self.assertEqual(mod10.gc08_record(plain_kind, tag), record)

    def test_distinguishing_bytes_dependency_manifest(self):
        self.check_retained(
            bytes(b"dependency_manifest"), "dependency_manifest",
            "owner-b4-gc-bytes-dep")

    def test_distinguishing_bytearray_dependency_manifest(self):
        self.check_retained(
            bytearray(b"dependency_manifest"), "dependency_manifest",
            "owner-b4-gc-bytearray-dep")

    def test_distinguishing_memoryview_dependency_manifest(self):
        self.check_retained(
            memoryview(b"dependency_manifest"), "dependency_manifest",
            "owner-b4-gc-memoryview-dep")

    def test_distinguishing_bytes_call_log(self):
        self.check_retained(
            bytes(b"call_log"), "call_log", "owner-b4-gc-bytes-call")

    def test_distinguishing_bytearray_call_log(self):
        self.check_retained(
            bytearray(b"call_log"), "call_log",
            "owner-b4-gc-bytearray-call")

    def test_distinguishing_memoryview_call_log(self):
        self.check_retained(
            memoryview(b"call_log"), "call_log",
            "owner-b4-gc-memoryview-call")

    def test_control_buffer_bogus_named_bogus(self):
        for kind_value in buffers("bogus"):
            with self.assertRaises(ValueError) as ctx:
                mod10.retain_gc08_record(kind_value, {}, "owner-b4-gc-bogus")
            self.assertIn(
                "unknown GC-08 record kind: bogus;", str(ctx.exception))

    def test_control_plain_text_listed_kinds_retained(self):
        self.check_retained(
            "dependency_manifest", "dependency_manifest",
            "owner-b4-gc-plain-dep")
        self.check_retained(
            "call_log", "call_log", "owner-b4-gc-plain-call")

    def test_control_plain_text_bogus_named_bogus(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record("bogus", {}, "owner-b4-gc-plain-bogus")
        self.assertIn(
            "unknown GC-08 record kind: bogus;", str(ctx.exception))


class TestR23006StoreLookup(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def check_lookup(self, kind_value, plain_kind, tag):
        run_id = "run-b4-" + tag
        mod10.retain_run_record(
            {"run_id": run_id, "marker": tag}, store_kind=plain_kind)
        record = mod10.store_lookup(key=run_id, store_kind=kind_value)
        self.assertEqual(record.get("run_id"), run_id)
        self.assertEqual(record.get("marker"), tag)

    def test_distinguishing_bytes_sweep(self):
        self.check_lookup(bytes(b"sweep"), "sweep", "bytes-sweep")

    def test_distinguishing_bytearray_sweep(self):
        self.check_lookup(bytearray(b"sweep"), "sweep", "bytearray-sweep")

    def test_distinguishing_memoryview_sweep(self):
        self.check_lookup(memoryview(b"sweep"), "sweep", "memoryview-sweep")

    def test_distinguishing_bytes_pilot(self):
        self.check_lookup(bytes(b"pilot"), "pilot", "bytes-pilot")

    def test_distinguishing_bytearray_pilot(self):
        self.check_lookup(bytearray(b"pilot"), "pilot", "bytearray-pilot")

    def test_distinguishing_memoryview_pilot(self):
        self.check_lookup(
            memoryview(b"pilot"), "pilot", "memoryview-pilot")

    def test_distinguishing_bytes_live(self):
        self.check_lookup(bytes(b"live"), "live", "bytes-live")

    def test_distinguishing_bytearray_live(self):
        self.check_lookup(bytearray(b"live"), "live", "bytearray-live")

    def test_distinguishing_memoryview_live(self):
        self.check_lookup(memoryview(b"live"), "live", "memoryview-live")

    def test_control_buffer_bogus_named_bogus(self):
        for kind_value in buffers("bogus"):
            with self.assertRaises(ValueError) as ctx:
                mod10.store_lookup(key="run-b4-bogus", store_kind=kind_value)
            self.assertIn("unknown store kind: bogus;", str(ctx.exception))

    def test_control_plain_text_listed_kinds_lookup(self):
        self.check_lookup("sweep", "sweep", "plain-sweep")
        self.check_lookup("pilot", "pilot", "plain-pilot")
        self.check_lookup("live", "live", "plain-live")

    def test_control_plain_text_bogus_named_bogus(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(key="run-b4-bogus", store_kind="bogus")
        self.assertIn("unknown store kind: bogus;", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
