"""

Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

"""


import unittest
from crucible.mod13 import (
    NamedReplicationFailure,
    extend_history,
    rerun_reading_validation_failures,
    resume_claim_validation_failures,
    verdict_record,
    verdict_record_validation_failures,
)
from crucible.mod12 import NamedControllerFailure, winning_regime


class EqTrueStr(str):
    __hash__ = str.__hash__

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class EqFalseStr(str):
    __hash__ = str.__hash__

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True


class RaisingStr(str):
    __hash__ = str.__hash__

    def __eq__(self, other):
        raise RuntimeError("raising equality")

    def __ne__(self, other):
        raise RuntimeError("raising equality")


class AlwaysEqObject:
    __hash__ = object.__hash__

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class StrLyingStr(str):
    __hash__ = str.__hash__

    def __str__(self):
        return "exact replay alone"


class ReprLyingStr(str):
    __hash__ = str.__hash__
    lying_repr = "''"

    def __repr__(self):
        return type(self).lying_repr


def repr_lying(stored, lying):
    cls = type("ReprLying_" + stored.replace(" ", "_"), (ReprLyingStr,), {})
    cls.lying_repr = lying
    return cls(stored)


class ReprLyingObject:
    def __repr__(self):
        return "[segment]"


class PlainObject:
    pass


def history_v1():
    return [{"rule_set_version": "v1", "run_id": "run-1", "payload": 1}]


def valid_verdict():
    return verdict_record("claim-1")


class TestR20023ExtendHistoryJudgement(unittest.TestCase):
    def test_version_lying_eq_true_other_version_refused(self):
        with self.assertRaises(NamedReplicationFailure):
            extend_history(history_v1(), {"rule_set_version": EqTrueStr("v2")})

    def test_version_lying_eq_false_same_version_extended(self):
        result = extend_history(history_v1(), {"rule_set_version": EqFalseStr("v1")})
        self.assertEqual(len(result), 2)

    def test_version_raising_eq_same_version_extended(self):
        result = extend_history(history_v1(), {"rule_set_version": RaisingStr("v1")})
        self.assertEqual(len(result), 2)

    def test_version_always_eq_object_refused(self):
        with self.assertRaises(NamedReplicationFailure):
            extend_history(history_v1(), {"rule_set_version": AlwaysEqObject()})

    def test_version_bytes_same_version_extended(self):
        result = extend_history(history_v1(), {"rule_set_version": b"v1"})
        self.assertEqual(len(result), 2)

    def test_link_lying_eq_true_other_link_refused(self):
        with self.assertRaises(NamedReplicationFailure):
            extend_history(history_v1(), {"linked_run": EqTrueStr("run-9")})

    def test_link_lying_eq_false_same_link_extended(self):
        result = extend_history(history_v1(), {"linked_run": EqFalseStr("run-1")})
        self.assertEqual(len(result), 2)

    def test_link_raising_eq_same_link_extended(self):
        result = extend_history(history_v1(), {"linked_run": RaisingStr("run-1")})
        self.assertEqual(len(result), 2)

    def test_link_bytes_same_link_extended(self):
        result = extend_history(history_v1(), {"linked_run": b"run-1"})
        self.assertEqual(len(result), 2)

    def test_boolean_version_not_judged_as_number_one(self):
        hist = [{"rule_set_version": 1, "run_id": "run-1", "payload": 1}]
        with self.assertRaises(NamedReplicationFailure):
            extend_history(hist, {"rule_set_version": True})

    def test_control_plain_same_version_extended(self):
        result = extend_history(
            history_v1(), {"rule_set_version": "v1", "linked_run": "run-1"})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["segment_order"], 2)

    def test_control_plain_other_version_refused(self):
        with self.assertRaises(NamedReplicationFailure):
            extend_history(history_v1(), {"rule_set_version": "v2"})

    def test_control_plain_other_link_refused(self):
        with self.assertRaises(NamedReplicationFailure):
            extend_history(history_v1(), {"linked_run": "run-9"})

    def test_control_no_fields_extended_and_stamped(self):
        result = extend_history(history_v1(), {"payload": 2})
        self.assertEqual(result[1]["rule_set_version"], "v1")
        self.assertEqual(result[1]["linked_run"], "run-1")

    def test_control_bytes_other_version_refused(self):
        with self.assertRaises(NamedReplicationFailure):
            extend_history(history_v1(), {"rule_set_version": b"v2"})


class TestR20041VerdictRecordSentence(unittest.TestCase):
    def test_lying_str_standard_named_on_stored_text(self):
        with self.assertRaises(NamedReplicationFailure) as caught:
            verdict_record("claim-1", standard=StrLyingStr("bogus standard"))
        self.assertIn("unknown replication standard: bogus standard", str(caught.exception))

    def test_bytes_standard_named_on_stored_text(self):
        with self.assertRaises(NamedReplicationFailure) as caught:
            verdict_record("claim-1", standard=b"bogus standard")
        self.assertIn("unknown replication standard: bogus standard", str(caught.exception))

    def test_control_plain_unknown_standard_named(self):
        with self.assertRaises(NamedReplicationFailure) as caught:
            verdict_record("claim-1", standard="bogus standard")
        self.assertIn("unknown replication standard: bogus standard", str(caught.exception))

    def test_control_valid_standard_record_made(self):
        record = verdict_record("claim-1", standard="exact replay alone")
        self.assertEqual(record["standard_applied"], "exact replay alone")


class TestR20042OutcomeSentence(unittest.TestCase):
    def test_lying_repr_outcome_named_on_stored_text(self):
        record = valid_verdict()
        record["outcome"] = repr_lying("bogus", "'rests'")
        failures = verdict_record_validation_failures(record)
        self.assertTrue(any("'bogus'" in item for item in failures), failures)

    def test_control_plain_outcome_named(self):
        record = valid_verdict()
        record["outcome"] = "bogus"
        failures = verdict_record_validation_failures(record)
        self.assertTrue(any("'bogus'" in item for item in failures), failures)

    def test_control_valid_record_no_failures(self):
        self.assertEqual(verdict_record_validation_failures(valid_verdict()), [])


class TestR20043StandardAppliedSentence(unittest.TestCase):
    def test_lying_repr_standard_named_on_stored_text(self):
        record = valid_verdict()
        record["standard_applied"] = repr_lying("bogus standard", "'exact replay alone'")
        failures = verdict_record_validation_failures(record)
        self.assertTrue(any("'bogus standard'" in item for item in failures), failures)

    def test_control_plain_standard_named(self):
        record = valid_verdict()
        record["standard_applied"] = "bogus standard"
        failures = verdict_record_validation_failures(record)
        self.assertTrue(any("'bogus standard'" in item for item in failures), failures)

    def test_control_valid_record_no_failures(self):
        self.assertEqual(verdict_record_validation_failures(valid_verdict()), [])


class TestR20044ScopeSentence(unittest.TestCase):
    def test_lying_repr_scope_named_on_stored_text(self):
        claim = {"detection_scope": repr_lying("world scope", "'verdict level only'")}
        failures = resume_claim_validation_failures(claim)
        self.assertTrue(any("'world scope'" in item for item in failures), failures)

    def test_control_plain_scope_named(self):
        claim = {"detection_scope": "world scope"}
        failures = resume_claim_validation_failures(claim)
        self.assertTrue(any("'world scope'" in item for item in failures), failures)

    def test_control_valid_scope_no_failures(self):
        self.assertEqual(
            resume_claim_validation_failures({"detection_scope": "verdict level only"}), [])


class TestR20045PointSentence(unittest.TestCase):
    def test_lying_repr_point_named_on_stored_text(self):
        claim = {"detection_comparison_points": [
            repr_lying("bogus point", "'run close'"), "run close"]}
        failures = resume_claim_validation_failures(claim)
        self.assertTrue(any("'bogus point'" in item for item in failures), failures)

    def test_control_plain_point_named(self):
        claim = {"detection_comparison_points": ["bogus point", "run close"]}
        failures = resume_claim_validation_failures(claim)
        self.assertTrue(any("'bogus point'" in item for item in failures), failures)

    def test_control_valid_points_no_failures(self):
        claim = {"detection_comparison_points": [
            "first verdict state after resume", "run close"]}
        self.assertEqual(resume_claim_validation_failures(claim), [])


class TestR20046ReadingSentence(unittest.TestCase):
    def test_lying_repr_reading_named_on_stored_text(self):
        reading = {"read_as": repr_lying(
            "bogus reading", "'difference between two rule sets only'")}
        failures = rerun_reading_validation_failures(reading)
        self.assertTrue(any("'bogus reading'" in item for item in failures), failures)

    def test_control_plain_reading_named(self):
        failures = rerun_reading_validation_failures({"read_as": "bogus reading"})
        self.assertTrue(any("'bogus reading'" in item for item in failures), failures)

    def test_control_valid_reading_no_failures(self):
        self.assertEqual(rerun_reading_validation_failures(
            {"read_as": "difference between two rule sets only"}), [])


class TestR20047HistoryFormSentence(unittest.TestCase):
    def test_lying_repr_history_not_named_as_list_form(self):
        with self.assertRaises(NamedReplicationFailure) as caught:
            extend_history(ReprLyingObject(), {"rule_set_version": "v1"})
        message = str(caught.exception)
        self.assertIn("stands in no list form", message)
        self.assertNotIn("[segment]", message)

    def test_control_plain_text_history_named(self):
        with self.assertRaises(NamedReplicationFailure) as caught:
            extend_history("notalist", {"rule_set_version": "v1"})
        self.assertIn("'notalist'", str(caught.exception))

    def test_control_plain_object_history_named(self):
        with self.assertRaises(NamedReplicationFailure) as caught:
            extend_history(PlainObject(), {"rule_set_version": "v1"})
        self.assertIn("stands in no list form", str(caught.exception))


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


PAIR_MESSAGE = (
    "winning regime entry is not an attacker and honest pair: ")


NON_NUMERIC_MESSAGE = (
    "winning regime entry carries a non numeric share: ")


def winning_pairs(count=30):
    return [(0.9, 0.1) for _ in range(count)]


def with_entry_at(position, entry, count=30):
    shares = winning_pairs(count)
    shares[position] = entry
    return shares


class IterRaises:
    """An entry standing in no pair form whose iteration raises
    the exception kind it is handed, once, at the unpacking."""

    def __init__(self, exc):
        self._exc = exc

    def __iter__(self):
        raise self._exc


class RaisingIterMeta(type):
    def __iter__(cls):
        raise RuntimeError("iteration raises")


class ClassEntry(metaclass=RaisingIterMeta):
    """An entry standing as a class whose iteration raises
    RuntimeError through its metaclass."""


class LyingReprEntry:
    """An entry standing in no pair form whose repr reading
    answers the pair form it is handed."""

    def __init__(self, text="(0.9, 0.1)"):
        self._text = text

    def __repr__(self):
        return self._text


class RaisingReprEntry:
    """An entry standing in no pair form whose repr reading
    raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr raises")


class TestR21014UnpackEscape(unittest.TestCase):
    """Row R21-014: the entry unpacking limb of winning_regime
    stands inside the named failure reach for every raising
    kind an entry iteration supplies."""

    def test_runtime_error_instance_entry_draws_named_failure(self):
        shares = with_entry_at(15, IterRaises(RuntimeError("boom")))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_runtime_error_class_entry_draws_named_failure(self):
        shares = with_entry_at(15, ClassEntry)
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_key_error_entry_draws_named_failure(self):
        shares = with_entry_at(15, IterRaises(KeyError("boom")))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_attribute_error_entry_draws_named_failure(self):
        shares = with_entry_at(15, IterRaises(AttributeError("boom")))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_overflow_error_entry_draws_named_failure(self):
        shares = with_entry_at(15, IterRaises(OverflowError("boom")))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_os_error_entry_draws_named_failure(self):
        shares = with_entry_at(15, IterRaises(OSError("boom")))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_control_winning_pairs_return_true(self):
        self.assertTrue(winning_regime(winning_pairs()))

    def test_control_three_value_entries_draw_named_failure(self):
        shares = [(0.9, 0.1, 0.0) for _ in range(30)]
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_control_value_error_entry_draws_named_failure(self):
        shares = with_entry_at(15, IterRaises(ValueError("boom")))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_control_plain_int_entry_draws_named_failure(self):
        shares = with_entry_at(15, 5)
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertTrue(
            str(caught.exception).startswith(PAIR_MESSAGE))

    def test_control_twenty_nine_pairs_return_false(self):
        self.assertFalse(winning_regime(winning_pairs(29)))

    def test_control_losing_pair_returns_false(self):
        shares = with_entry_at(20, (0.1, 0.9))
        self.assertFalse(winning_regime(shares))


class TestR21015PairFormRendering(unittest.TestCase):
    """Row R21-015: the pair form refusal of winning_regime
    renders the handed entry through the module stored form
    rendering, so an entry standing in no pair form stands
    named by the form it stands in, never by a repr reading
    it supplies."""

    def test_lying_repr_pair_of_shares_names_kind(self):
        shares = with_entry_at(29, LyingReprEntry("(0.9, 0.1)"))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertEqual(
            str(caught.exception), PAIR_MESSAGE + "LyingReprEntry")

    def test_lying_repr_three_one_names_kind(self):
        shares = with_entry_at(29, LyingReprEntry("(3, 1)"))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertEqual(
            str(caught.exception), PAIR_MESSAGE + "LyingReprEntry")

    def test_raising_repr_entry_names_kind(self):
        shares = with_entry_at(29, RaisingReprEntry())
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertEqual(
            str(caught.exception), PAIR_MESSAGE + "RaisingReprEntry")

    def test_three_lying_repr_parts_render_by_kind(self):
        entry = (
            LyingReprEntry(), LyingReprEntry(), LyingReprEntry())
        shares = with_entry_at(29, entry)
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertEqual(
            str(caught.exception),
            PAIR_MESSAGE
            + "(LyingReprEntry, LyingReprEntry, LyingReprEntry)")

    def test_control_plain_int_entry_names_five(self):
        shares = with_entry_at(29, 5)
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertEqual(str(caught.exception), PAIR_MESSAGE + "5")

    def test_control_non_numeric_share_sentence(self):
        shares = with_entry_at(29, ("x", 0.1))
        with self.assertRaises(NamedControllerFailure) as caught:
            winning_regime(shares)
        self.assertEqual(
            str(caught.exception),
            NON_NUMERIC_MESSAGE + "('x', 0.1)")

    def test_control_winning_pairs_return_true(self):
        self.assertTrue(winning_regime(winning_pairs()))

    def test_control_losing_pair_returns_false(self):
        shares = with_entry_at(3, (0.2, 0.8))
        self.assertFalse(winning_regime(shares))


if __name__ == "__main__":
    unittest.main()
