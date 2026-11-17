"""Pins for fix wave 23, builder b7, Group 7: the MOD-10
_safe_str family, rows R23-009 to R23-011 of the Round 23
register, on Ruling 9 at step record Entry 219.

The defect, one family at three loci in crucible/mod10.py:
each locus renders or judges a handed value through
_safe_str, the string reading the value itself supplies.
(R23-009) run_view_leak_check renders the handed field at
its per field canary sentence through _safe_str.
(R23-010) RecorderStore.retain_run_record renders the
handed run identifier at its duplicate retention refusal
through _safe_str. (R23-011) validate_retention_record
judges the handed governing rule through _safe_str.
The cure: render or judge on the stored form at each
locus, never through a reading the handed value supplies,
in the family form of the cured vocabulary loci, each
locus standing on its own row handings.

Distinguishing pins fail on the pristine basis and pass
on the cured copy. Control pins pass on both trees.
"""
import unittest

from crucible import mod10


class LyingStr(str):
    """A text value storing one text whose string reading
    answers another text."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie


class RaisingStr(str):
    """A text value storing one text whose string reading
    raises."""

    def __str__(self):
        raise RuntimeError("string reading raises")


def view_record(extra_key=None, extra_value=None):
    record = {
        "run_identifier": "run-1",
        "viewer_identifier": "viewer-1",
        "simulated_day": 5,
        "scheduling_position_identifier": "s",
        "rule_version_set": "r",
        "view_contents": {},
        "reputation_and_band_values": {},
        "graph_position_as_seen": {},
        "first_seen_day_per_record": {"rec-1": 3},
        "delay_applied_per_record": {},
        "completeness_state": "complete",
        "building_component": "c",
        "delivering_contract": "d",
        "selection_rule_version": "v",
    }
    if extra_key is not None:
        record[extra_key] = extra_value
    return record


class TestR23009CanaryFieldLimb(unittest.TestCase):

    def test_distinguishing_lying_field_names_stored_field(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                LyingStr("extra", "FIELD-LIE"),
                {"ground_truth": 1}))
        message = str(ctx.exception)
        self.assertIn("field extra carries a barred key", message)
        self.assertNotIn("FIELD-LIE", message)

    def test_distinguishing_lying_barred_field_names_stored(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                LyingStr("canary", "innocent_field"), {}))
        message = str(ctx.exception)
        self.assertIn("field canary carries a barred key", message)
        self.assertNotIn("innocent_field", message)

    def test_distinguishing_raising_field_names_stored_field(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                RaisingStr("canary"), {}))
        message = str(ctx.exception)
        self.assertIn("field canary carries a barred key", message)
        self.assertNotIn("object at", message)

    def test_distinguishing_bytes_field_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(b"canary", {}))
        message = str(ctx.exception)
        self.assertIn("field canary carries a barred key", message)
        self.assertNotIn("b'canary'", message)

    def test_control_plain_field_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "extra", {"ground_truth": 1}))
        self.assertIn(
            "field extra carries a barred key", str(ctx.exception))

    def test_control_plain_barred_field_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record("canary", {}))
        self.assertIn(
            "field canary carries a barred key", str(ctx.exception))


class TestR23010DuplicateRetentionRefusal(unittest.TestCase):

    def duplicate_message(self, rid):
        store = mod10.RecorderStore()
        store.retain_run_record({"run_id": rid})
        with self.assertRaises(ValueError) as ctx:
            store.retain_run_record({"run_id": rid})
        return str(ctx.exception)

    def test_distinguishing_lying_identifier_names_stored_run(self):
        message = self.duplicate_message(
            LyingStr("run-1", "run-FAKE"))
        self.assertIn(
            "second record for the same run is rejected: run-1",
            message)
        self.assertNotIn("run-FAKE", message)

    def test_distinguishing_raising_identifier_names_stored(self):
        message = self.duplicate_message(RaisingStr("run-1"))
        self.assertIn(
            "second record for the same run is rejected: run-1",
            message)
        self.assertNotIn("object at", message)

    def test_control_plain_identifier_names_plain_text(self):
        message = self.duplicate_message("run-1")
        self.assertIn(
            "second record for the same run is rejected: run-1",
            message)

    def test_control_distinct_identifier_retained(self):
        store = mod10.RecorderStore()
        store.retain_run_record({"run_id": "run-1"})
        result = store.retain_run_record({"run_id": "run-2"})
        self.assertEqual(result["run_id"], "run-2")


class TestR23011GoverningRuleLimb(unittest.TestCase):

    def test_distinguishing_lying_benign_rule_judged_stored(self):
        self.assertTrue(mod10.validate_retention_record({
            "governing_rule": LyingStr("benign", "DQ7-08-x"),
            "reliance": "governing"}))

    def test_distinguishing_lying_barred_rule_judged_stored(self):
        self.assertFalse(mod10.validate_retention_record({
            "governing_rule": LyingStr("DQ7-08-x", "benign"),
            "reliance": "governing"}))

    def test_distinguishing_raising_barred_rule_judged_stored(self):
        self.assertFalse(mod10.validate_retention_record({
            "governing_rule": RaisingStr("DQ7-08-x"),
            "reliance": "governing"}))

    def test_control_plain_benign_rule_validates(self):
        self.assertTrue(mod10.validate_retention_record({
            "governing_rule": "benign", "reliance": "governing"}))

    def test_control_plain_barred_rule_refused(self):
        self.assertFalse(mod10.validate_retention_record({
            "governing_rule": "DQ7-08-x", "reliance": "governing"}))

    def test_control_barred_rule_other_reliance_validates(self):
        self.assertTrue(mod10.validate_retention_record({
            "governing_rule": "DQ7-08-x", "reliance": "other"}))


if __name__ == "__main__":
    unittest.main()
