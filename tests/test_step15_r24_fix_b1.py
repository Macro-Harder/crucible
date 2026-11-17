"""Pins for fix wave 24, builder b1: rows R24-001 and R24-002 of
the Round 24 register.

R24-001: the composed buffer kind form escapes bare TypeError at
_canonical_store_kind and at its callers outside store_lookup,
on a buffer handing storing a listed kind, because the widened
_store_kind_stands judgement passes the buffer and the conversion
loop then reads the handed buffer itself through str.__eq__.
The cure stands at the composed form: buffer forms stand judged
and converted on stored text, in the form _store_kind_stands
now states, with no bare escape at any caller, the four
conditional readers included.

R24-002: the RecorderStore construction judgement judges the
handed kind on text form alone, so a buffer storing a listed
kind draws the self contradicting unknown kind refusal naming
that kind while listing it. The cure stands at the construction
judgement: the kind stands judged on its stored text for the
buffer forms, sentence forms unchanged.

Distinguishing pins fail on the pristine basis and pass on the
cured copy. Control pins pass on both trees.
"""
import unittest

from crucible import mod10


def buffers(text):
    raw = text.encode("utf-8")
    return (bytes(raw), bytearray(raw), memoryview(raw))


class B1Base(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()


class TestR24001CanonicalDirect(B1Base):

    def test_distinguishing_bytes_sweep(self):
        self.assertEqual(mod10._canonical_store_kind(bytes(b"sweep")), "sweep")

    def test_distinguishing_bytearray_pilot(self):
        self.assertEqual(
            mod10._canonical_store_kind(bytearray(b"pilot")), "pilot")

    def test_distinguishing_memoryview_live(self):
        self.assertEqual(
            mod10._canonical_store_kind(memoryview(b"live")), "live")

    def test_distinguishing_all_buffer_listed_pairings(self):
        for plain in ("sweep", "pilot", "live"):
            for kind_value in buffers(plain):
                self.assertEqual(
                    mod10._canonical_store_kind(kind_value), plain)

    def test_control_plain_text_listed(self):
        for plain in ("sweep", "pilot", "live"):
            self.assertEqual(mod10._canonical_store_kind(plain), plain)

    def test_control_buffer_bogus_named_bogus(self):
        for kind_value in buffers("bogus"):
            with self.assertRaises(ValueError) as ctx:
                mod10._canonical_store_kind(kind_value)
            self.assertIn("unknown store kind: bogus;", str(ctx.exception))

    def test_control_plain_text_bogus_named_bogus(self):
        with self.assertRaises(ValueError) as ctx:
            mod10._canonical_store_kind("bogus")
        self.assertIn("unknown store kind: bogus;", str(ctx.exception))

    def test_control_plain_object_named_unknown(self):
        with self.assertRaises(ValueError):
            mod10._canonical_store_kind(object())


class TestR24001UnconditionalCallers(B1Base):

    def test_distinguishing_retain_run_record_bytes_sweep(self):
        record = {"run_id": "run-b1-retain", "marker": "retain"}
        returned = mod10.retain_run_record(
            dict(record), store_kind=bytes(b"sweep"))
        self.assertEqual(returned, record)
        self.assertEqual(
            mod10.read_run_record("run-b1-retain", store_kind="sweep"),
            record)

    def test_distinguishing_read_run_record_bytes_sweep(self):
        record = {"run_id": "run-b1-read", "marker": "read"}
        mod10.retain_run_record(dict(record), store_kind="sweep")
        self.assertEqual(
            mod10.read_run_record("run-b1-read", store_kind=bytes(b"sweep")),
            record)

    def test_distinguishing_retain_event_log_entry_bytes_sweep(self):
        entry = {"run_identifier": "run-b1-event", "journal_position": 1}
        mod10.retain_event_log_entry(dict(entry), store_kind=bytes(b"sweep"))
        held = mod10.event_log_entries("run-b1-event", store_kind="sweep")
        self.assertEqual(len(held), 1)
        self.assertEqual(held[0]["journal_position"], 1)

    def test_distinguishing_retain_daily_snapshot_bytes_sweep(self):
        snap = {"run_identifier": "run-b1-snap", "marker": "snap"}
        mod10.retain_daily_snapshot(dict(snap), store_kind=bytes(b"sweep"))
        held = mod10.daily_snapshots("run-b1-snap", store_kind="sweep")
        self.assertEqual(len(held), 1)

    def test_distinguishing_retain_checkpoint_bytes_sweep(self):
        manifest = {"run_identifier": "run-b1-ckpt", "simulated_day": 3}
        mod10.retain_checkpoint(dict(manifest), store_kind=bytes(b"sweep"))
        held = mod10.checkpoints_for_run("run-b1-ckpt", store_kind="sweep")
        self.assertEqual(len(held), 1)

    def test_control_retain_run_record_buffer_bogus(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_run_record(
                {"run_id": "run-b1-bogus"}, store_kind=bytes(b"bogus"))
        self.assertIn("unknown store kind: bogus;", str(ctx.exception))

    def test_control_read_run_record_plain_bogus(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.read_run_record("run-b1-none", store_kind="bogus")
        self.assertIn("unknown store kind: bogus;", str(ctx.exception))


class TestR24001ConditionalReaders(B1Base):

    def test_distinguishing_event_log_entries_bytes_sweep(self):
        mod10.retain_event_log_entry(
            {"run_identifier": "run-b1-evread", "journal_position": 7},
            store_kind="sweep")
        held = mod10.event_log_entries(
            "run-b1-evread", store_kind=bytes(b"sweep"))
        self.assertEqual(len(held), 1)
        self.assertEqual(held[0]["journal_position"], 7)

    def test_distinguishing_daily_snapshots_bytearray_pilot(self):
        mod10.retain_daily_snapshot(
            {"run_identifier": "run-b1-snapread", "marker": "x"},
            store_kind="pilot")
        held = mod10.daily_snapshots(
            "run-b1-snapread", store_kind=bytearray(b"pilot"))
        self.assertEqual(len(held), 1)

    def test_distinguishing_checkpoint_state_at_memoryview_live(self):
        state = {"agent_states": "stated", "simulation_clock_value": 4}
        mod10.retain_checkpoint(
            {"run_identifier": "run-b1-state", "simulated_day": 4,
             "checkpoint_state": dict(state)},
            store_kind="live")
        self.assertEqual(
            mod10.checkpoint_state_at(
                "run-b1-state", 4, store_kind=memoryview(b"live")),
            state)

    def test_distinguishing_checkpoints_for_run_bytes_sweep(self):
        mod10.retain_checkpoint(
            {"run_identifier": "run-b1-ckread", "simulated_day": 2},
            store_kind="sweep")
        held = mod10.checkpoints_for_run(
            "run-b1-ckread", store_kind=bytes(b"sweep"))
        self.assertEqual(len(held), 1)

    def test_control_conditional_reader_buffer_bogus_empty(self):
        self.assertEqual(
            mod10.event_log_entries(
                "run-b1-absent", store_kind=bytes(b"bogus")), [])
        self.assertEqual(
            mod10.daily_snapshots(
                "run-b1-absent", store_kind=bytes(b"bogus")), [])
        self.assertEqual(
            mod10.checkpoints_for_run(
                "run-b1-absent", store_kind=bytes(b"bogus")), [])
        self.assertIsNone(
            mod10.checkpoint_state_at(
                "run-b1-absent", 1, store_kind=bytes(b"bogus")))

    def test_control_conditional_reader_plain_object_empty(self):
        self.assertEqual(
            mod10.event_log_entries("run-b1-absent", store_kind=object()),
            [])

    def test_control_conditional_reader_plain_listed_absent(self):
        self.assertEqual(
            mod10.event_log_entries("run-b1-absent", store_kind="sweep"),
            [])


class TestR24002Construction(B1Base):

    def test_distinguishing_recorder_store_bytes_sweep(self):
        store = mod10.RecorderStore(store_kind=bytes(b"sweep"))
        self.assertEqual(store.store_kind, "sweep")

    def test_distinguishing_recorder_store_bytearray_pilot(self):
        store = mod10.RecorderStore(store_kind=bytearray(b"pilot"))
        self.assertEqual(store.store_kind, "pilot")

    def test_distinguishing_recorder_store_memoryview_live(self):
        store = mod10.RecorderStore(store_kind=memoryview(b"live"))
        self.assertEqual(store.store_kind, "live")

    def test_distinguishing_new_store_bytes_sweep(self):
        store = mod10.new_store(store_kind=bytes(b"sweep"))
        self.assertEqual(store.store_kind, "sweep")
        store.retain_run_record({"run_id": "run-b1-newstore"})
        self.assertEqual(
            store.read_run_record("run-b1-newstore")["run_id"],
            "run-b1-newstore")

    def test_distinguishing_new_store_all_buffer_pairings(self):
        for plain in ("sweep", "pilot", "live"):
            for kind_value in buffers(plain):
                store = mod10.new_store(store_kind=kind_value)
                self.assertEqual(store.store_kind, plain)

    def test_control_plain_text_listed_constructs(self):
        for plain in ("sweep", "pilot", "live"):
            store = mod10.RecorderStore(store_kind=plain)
            self.assertEqual(store.store_kind, plain)
            store = mod10.new_store(store_kind=plain)
            self.assertEqual(store.store_kind, plain)

    def test_control_buffer_bogus_named_bogus(self):
        for kind_value in buffers("bogus"):
            with self.assertRaises(ValueError) as ctx:
                mod10.RecorderStore(store_kind=kind_value)
            self.assertIn("unknown store kind: bogus;", str(ctx.exception))
            with self.assertRaises(ValueError) as ctx:
                mod10.new_store(store_kind=kind_value)
            self.assertIn("unknown store kind: bogus;", str(ctx.exception))

    def test_control_plain_text_bogus_named_bogus(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.RecorderStore(store_kind="bogus")
        self.assertIn("unknown store kind: bogus;", str(ctx.exception))

    def test_control_plain_object_refused(self):
        with self.assertRaises(ValueError):
            mod10.RecorderStore(store_kind=object())


if __name__ == "__main__":
    unittest.main()
