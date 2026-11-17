"""Pins for fix wave 20, builder b4, group 4, MOD-14 family.

Rows R20-002, R20-007, R20-030, and R20-069 of the Round 20
register. Every distinguishing pin fails or errors on the
pristine code for its charged defect and passes after the
cure; the plain controls pass before and after.
"""

import unittest

from crucible import mod14
from crucible.mod14 import NamedShellFailure


class BoolLiar:
    """A stored object whose truth reading answers the
    opposite of the value it stores."""

    def __init__(self, stored):
        self.stored = stored

    def __bool__(self):
        return not self.stored


class RaiseBool:
    """A stored object whose truth reading raises."""

    def __bool__(self):
        raise RuntimeError("armed truth reading")


class StrLie(str):
    """A text value storing one word whose string and repr
    readings answer another word."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie

    def __repr__(self):
        return self._lie


class RaiseStr(str):
    """A text value whose string and repr readings raise."""

    def __str__(self):
        raise RuntimeError("armed string reading")

    def __repr__(self):
        raise RuntimeError("armed repr reading")


class LieRepr:
    """A plain object whose repr and string readings answer
    a stated different text."""

    def __init__(self, lie):
        self._lie = lie

    def __repr__(self):
        return self._lie

    def __str__(self):
        return self._lie


class ArmedKey:
    """A dict key whose hash reading raises once armed."""

    def __init__(self, name):
        self.name = name
        self.armed = False

    def __hash__(self):
        if self.armed:
            raise RuntimeError("armed hash reading")
        return hash(self.name)

    def __eq__(self, other):
        return self is other


class ArmedStrKey(str):
    """A text key whose hash reading raises once armed."""

    armed = False

    def __hash__(self):
        if self.armed:
            raise RuntimeError("armed hash reading")
        return str.__hash__(self)


def _armed_record(key, value):
    record = {key: value}
    key.armed = True
    return record


class TestR20002DualRuleMarks(unittest.TestCase):
    def test_synthetic_bool_liar_storing_true_admitted(self):
        families = [{
            "synthetic": BoolLiar(True),
            "retained_under_first_rule": True,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 0})

    def test_paired_counts_on_stored_marks_not_supplied_truth(self):
        families = [{
            "synthetic": True,
            "retained_under_first_rule": BoolLiar(True),
            "retained_under_second_rule": BoolLiar(False),
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 1})

    def test_raising_truth_at_synthetic_mark_no_bare_escape(self):
        families = [{
            "synthetic": RaiseBool(),
            "retained_under_first_rule": True,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 0})

    def test_raising_truth_at_retained_marks_no_bare_escape(self):
        families = [{
            "synthetic": True,
            "retained_under_first_rule": RaiseBool(),
            "retained_under_second_rule": RaiseBool(),
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 1})

    def test_control_plain_marks(self):
        refused = [{"synthetic": False,
                    "retained_under_first_rule": True}]
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(refused)
        families = [{
            "synthetic": True,
            "retained_under_first_rule": True,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 0})

    def test_control_stored_text_and_number_marks(self):
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(
                [{"synthetic": ""}])
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(
                [{"synthetic": {}}])
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(
                [{"synthetic": 0}])
        result = mod14.dual_rule_retention_simulation([{
            "synthetic": "yes",
            "retained_under_first_rule": 0,
            "retained_under_second_rule": 2,
        }])
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 0, "second_rule_retained": 1})

    def test_control_bool_liar_storing_false_also_present(self):
        families = [{
            "synthetic": BoolLiar(False),
            "retained_under_first_rule": False,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 0, "second_rule_retained": 0})


class TestR20007PlainStoredCopy(unittest.TestCase):
    def test_armed_hash_key_carried_whole(self):
        key = ArmedKey("k")
        record = _armed_record(key, "v")
        copied = mod14._plain_stored_copy(record)
        self.assertEqual(len(copied), 1)
        self.assertEqual(list(copied.values()), ["v"])

    def test_armed_text_key_carried_under_numbered_form(self):
        key = ArmedStrKey("field")
        record = _armed_record(key, 7)
        copied = mod14._plain_stored_copy(record)
        self.assertEqual(len(copied), 1)
        self.assertEqual(list(copied.values()), [7])
        carried_key = list(copied.keys())[0]
        self.assertIsInstance(carried_key, str)
        self.assertIn("(carried key 2)", str.__str__(carried_key))

    def test_flag_evaluation_delegation_reached_on_armed_key(self):
        key = ArmedKey("extra")
        record = {"retention_tier": "Tier 2"}
        record[key] = "x"
        key.armed = True
        result = mod14.flag_evaluation(
            record, inputs={}, outcome=None, tier=None)
        self.assertIn("flag_evaluation", result)

    def test_control_plain_record_copied_whole(self):
        record = {"a": 1, "b": {"nested": True}}
        copied = mod14._plain_stored_copy(record)
        self.assertEqual(copied, record)
        self.assertIsNot(copied, record)

    def test_control_no_mapping_form_stands_as_itself(self):
        handed = [1, 2]
        self.assertIs(mod14._plain_stored_copy(handed), handed)


class TestR20030SafeTextSites(unittest.TestCase):
    def test_screen_pilot_key_sentence_names_stored_key(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run(
                "timing", [StrLie("money", "CLEAN-TEXT")])
        message = str(caught.exception)
        self.assertIn("pilot confined label: money", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_pilot_use_sentence_names_stored_use(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run(
                StrLie("bogus", "CLEAN-TEXT"), {"figure": 1})
        message = str(caught.exception)
        self.assertIn("procedure rates: bogus", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_unknown_command_sentence_names_stored_command(self):
        result = mod14.run_command(StrLie("boguscmd", "CLEAN-TEXT"))
        message = result["failure"]
        self.assertIn("unknown shell command: boguscmd", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_call_log_key_sentence_names_stored_key(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.outside_call_check(
                {}, {StrLie("boguskey", "CLEAN-TEXT"): []})
        message = str(caught.exception)
        self.assertIn("cannot read: boguskey", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_raising_text_use_names_stored_use(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run(RaiseStr("bogus"), {"figure": 1})
        message = str(caught.exception)
        self.assertIn("procedure rates: bogus", message)
        self.assertNotIn("object at", message)

    def test_raising_text_command_names_stored_command(self):
        result = mod14.run_command(RaiseStr("boguscmd"))
        message = result["failure"]
        self.assertIn("unknown shell command: boguscmd", message)
        self.assertNotIn("object at", message)

    def test_bytes_command_names_stored_text(self):
        result = mod14.run_command(b"bogus-cmd")
        message = result["failure"]
        self.assertIn("unknown shell command: bogus-cmd", message)
        self.assertNotIn("b'bogus-cmd'", message)

    def test_bytes_call_log_key_names_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.outside_call_check({}, {b"boguskey": []})
        message = str(caught.exception)
        self.assertIn("cannot read: boguskey", message)
        self.assertNotIn("b'boguskey'", message)

    def test_control_plain_use_and_command_named(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run("bogus", {"figure": 1})
        self.assertIn("procedure rates: bogus", str(caught.exception))
        result = mod14.run_command("bogus-cmd")
        self.assertIn("unknown shell command: bogus-cmd",
                      result["failure"])


class TestR20069WeeklyIdentifierSentence(unittest.TestCase):
    def _records(self, identifier):
        return [{"week": "W1",
                 "headline_unit_identifiers": [identifier]}]

    def test_lying_text_identifier_named_on_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(StrLie("bogus-id", "u999")), "W1")
        message = str(caught.exception)
        self.assertIn("'bogus-id'", message)
        self.assertNotIn("u999", message)

    def test_lying_repr_object_named_on_its_form_not_its_reading(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(LieRepr("u999")), "W1")
        message = str(caught.exception)
        self.assertNotIn("u999", message)
        self.assertIn("LieRepr", message)

    def test_raising_text_identifier_named_on_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(RaiseStr("bogus-id")), "W1")
        message = str(caught.exception)
        self.assertIn("'bogus-id'", message)
        self.assertNotIn("object at", message)

    def test_bytes_identifier_named_on_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(b"bogus-id"), "W1")
        message = str(caught.exception)
        self.assertIn("'bogus-id'", message)
        self.assertNotIn("b'bogus-id'", message)

    def test_control_plain_number_identifier_named(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(self._records(123), "W1")
        self.assertIn("unvalidated contents: 123",
                      str(caught.exception))

    def test_control_plain_text_identifier_named_in_repr_dress(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records("bogus-id"), "W1")
        self.assertIn("'bogus-id'", str(caught.exception))

    def test_control_valid_identifiers_counted(self):
        records = [{"week": "W1",
                    "headline_unit_identifiers": ["u1", "u2", "u1"]}]
        self.assertEqual(
            mod14.weekly_headline_count(records, "W1"), 2)


if __name__ == "__main__":
    unittest.main()
