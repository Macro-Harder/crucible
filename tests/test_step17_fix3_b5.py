"""Step 17 fix wave 3, Builder 5 tests: Slice 5, the remaining
mod10 doors. Rows FW3-22, FW3-23, FW3-44.

Each defect test reproduces the filing defect of its row on the
uncured tree (the landed tree carrying the Slice 1, Slice 2,
Slice 3, and Slice 4 cures, uncured for these rows).
Standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod10


class HashRaisingId(str):
    """A run identifier whose hash reading raises a RuntimeError,
    the Purple 5 filing form at R2-PURPLE5-01."""

    def __hash__(self):
        raise RuntimeError("hostile hash reading")


class BoolRaisingId(str):
    """A run identifier whose truth reading raises a RuntimeError,
    so any door that consults its truth before judging its stored
    text stands escaped bare."""

    def __bool__(self):
        raise RuntimeError("hostile truth reading")


class UnhashableId(str):
    """A run identifier whose hash reading raises a TypeError,
    the form the uncured door already refuses in named form."""

    def __hash__(self):
        raise TypeError("unhashable identifier")


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)


class TestFW322RunIdentifierStoredForm(Base):
    """FW3-22 (Medium, T17R2-22): retention judges a run
    identifier on its stored text form before any supplied
    reading stands consulted, and a hostile identifier stands
    refused in the module named form."""

    def test_hash_raising_run_id_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record(
                {"run_id": HashRaisingId("hostile-run")})
        self.assertIn(
            "identity less record", str(caught.exception))
        with self.assertRaises(mod10.LookupFailure):
            mod10.read_run_record("hostile-run")

    def test_hash_raising_run_identifier_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record(
                {"run_identifier": HashRaisingId("hostile-run-2")})
        self.assertIn(
            "identity less record", str(caught.exception))
        with self.assertRaises(mod10.LookupFailure):
            mod10.read_run_record("hostile-run-2")

    def test_bool_raising_id_judged_on_stored_text(self):
        """The truth reading stands never consulted: the record
        stands retained under the plain text the identifier
        stores, and reads back under that text."""
        mod10.retain_run_record(
            {"run_id": BoolRaisingId("bool-run"), "marker": 7})
        got = mod10.read_run_record("bool-run")
        self.assertEqual(got["run_id"], "bool-run")
        self.assertEqual(type(got["run_id"]), str)
        self.assertEqual(got["marker"], 7)

    def test_control_plain_record_retained_and_read(self):
        mod10.retain_run_record({"run_id": "plain-run", "marker": 3})
        got = mod10.read_run_record("plain-run")
        self.assertEqual(got["marker"], 3)

    def test_control_unhashable_id_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record(
                {"run_id": UnhashableId("unhashable-run")})
        self.assertIn(
            "identity less record", str(caught.exception))

    def test_control_second_record_for_same_run_refused(self):
        mod10.retain_run_record({"run_id": "dup-run"})
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record({"run_id": "dup-run"})
        self.assertIn(
            "second record for the same run", str(caught.exception))


class TestFW323Gc08ReadDoorKind(Base):
    """FW3-23 (Medium, T17R2-23): the GC-08 read door judges its
    kind in the retain door form, refusing a kind outside the
    closed set in named form stating the kinds that stand."""

    def _refused(self, kind, owner_id):
        with self.assertRaises(ValueError) as caught:
            mod10.gc08_record(kind, owner_id)
        self.assertIn(
            "unknown GC-08 record kind", str(caught.exception))
        self.assertIn(
            "dependency_manifest", str(caught.exception))
        self.assertIn("call_log", str(caught.exception))

    def test_mistyped_kind_refused_in_named_form(self):
        mod10.retain_gc08_record(
            "call_log", {"calls": []}, "owner-1")
        self._refused("call-log", "owner-1")

    def test_none_kind_refused_in_named_form(self):
        self._refused(None, "owner-1")

    def test_arguments_in_wrong_order_refused_in_named_form(self):
        mod10.retain_gc08_record(
            "dependency_manifest", {"deps": []}, "owner-2")
        self._refused("owner-2", "dependency_manifest")

    def test_non_text_kind_refused_in_named_form(self):
        self._refused(7, "owner-1")

    def test_control_retained_record_read_back(self):
        mod10.retain_gc08_record(
            "dependency_manifest", {"deps": ["a"]}, "owner-3")
        got = mod10.gc08_record("dependency_manifest", "owner-3")
        self.assertEqual(got, {"deps": ["a"]})

    def test_control_absent_record_lookup_failure(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.gc08_record("call_log", "nobody")
        self.assertEqual(
            caught.exception.failure["record_kind"], "call_log")
        self.assertEqual(
            caught.exception.failure["run_identifier"], "nobody")

    def test_control_retain_door_bad_kind_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_gc08_record("bogus", {}, "owner-9")
        self.assertIn(
            "unknown GC-08 record kind", str(caught.exception))


class TestFW344CheckpointCountForm(Base):
    """FW3-44 (Low, T17R2-44): checkpoint_count_c10 delivers a
    non iterable handing in the module named failure form."""

    def _refused(self, rows):
        with self.assertRaises(ValueError) as caught:
            mod10.checkpoint_count_c10(rows)
        self.assertIn(
            "checkpoint count in named form", str(caught.exception))

    def test_integer_handing_refused_in_named_form(self):
        self._refused(42)

    def test_none_handing_refused_in_named_form(self):
        self._refused(None)

    def test_fraction_handing_refused_in_named_form(self):
        self._refused(3.5)

    def test_control_list_rows_counted(self):
        rows = [{"retained_per_run": 2, "runs": 3,
                 "held_corpus_copies": 1}]
        self.assertEqual(mod10.checkpoint_count_c10(rows), 7)

    def test_control_generator_rows_counted(self):
        rows = (row for row in [
            {"retained_per_run": 1, "runs": 2}])
        self.assertEqual(mod10.checkpoint_count_c10(rows), 2)

    def test_control_text_handing_refused_in_named_form(self):
        self._refused("abc")

    def test_control_non_record_row_refused_in_named_form(self):
        self._refused([42])


if __name__ == "__main__":
    unittest.main()
