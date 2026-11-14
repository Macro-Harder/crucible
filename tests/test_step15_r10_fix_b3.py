"""Fix wave 9 pins: MOD-01 rows R9-006 to R9-009.

Row R9-006: the closed form branch judges every key by its
stored characters or as no name, for non text keys as for text.
Row R9-007: the required field presence act reads the record
stored keys through base dict operations, never the handed
hash or equality readings.
Row R9-008: validate_store_addressing reads container forms
outside the five named kinds through base class readings of
their stored contents, not the handed tuple conversion.
Row R9-009: store_index builds its namespace token from the
stored kind as validate_store_kind judges it.
Each defect method fails on the uncured module and passes on
the cured module. Control methods pass both ways.
"""
import unittest
from collections import deque, UserDict, UserList

from crucible import mod01


class NonTextEqLieKey:
    """A non text key storing no field name whose equality
    reading answers True against every value. One form carries
    a hash reading answering as an allowed field, the other
    carries an ordinary object hash."""

    def __init__(self, hash_of=None):
        if hash_of is None:
            self._hash = object.__hash__(self)
        else:
            self._hash = hash_of

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class HashEqLieKey(str):
    """A text key storing one field name whose hash reading
    answers as another field and whose equality reading
    answers True against every value."""

    def __new__(cls, stored, answers_hash_of):
        obj = str.__new__(cls, stored)
        obj._answers_hash_of = answers_hash_of
        return obj

    def __hash__(self):
        return str.__hash__(self._answers_hash_of)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class IterLieDeque(deque):
    """A deque storing stated items whose iteration reading
    yields only the single kind sweep."""

    def __iter__(self):
        return iter(("sweep",))


class IterLieUserList(UserList):
    """A UserList storing stated items whose iteration reading
    yields only the single kind sweep."""

    def __iter__(self):
        return iter(("sweep",))


class IterLieUserDict(UserDict):
    """A UserDict storing stated items whose iteration reading
    yields only the single kind sweep."""

    def __iter__(self):
        return iter(("sweep",))


class ReportedKind(str):
    """A text kind storing one value while its string reading
    reports another value."""

    def __new__(cls, stored, reported):
        obj = str.__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported

    def __hash__(self):
        return str.__hash__(str.__str__(self))


def record_missing_first_required(form_id):
    required = mod01.required_fields(form_id)
    first = required[0]
    second = required[1]
    instance = mod01.minimal_valid_instance(form_id)
    del instance[first]
    lie = HashEqLieKey(second, first)
    instance[lie] = "stated value"
    return instance


class TestR9006ClosedFormNonTextKeys(unittest.TestCase):

    def test_r9_006_defect_hash_lie_non_text_key_all_closed(self):
        for form_id in ("16", "17", "19", "20", "21"):
            with self.subTest(form_id=form_id):
                allowed = mod01.form_fields(form_id)
                lie = NonTextEqLieKey(
                    hash_of=str.__hash__(allowed[0]))
                instance = {lie: "x", **mod01.minimal_valid_instance(form_id)}
                self.assertFalse(
                    mod01.validate_record(form_id, instance))

    def test_r9_006_defect_plain_hash_non_text_key_all_closed(self):
        for form_id in ("16", "17", "19", "20", "21"):
            with self.subTest(form_id=form_id):
                lie = NonTextEqLieKey()
                instance = {lie: "x", **mod01.minimal_valid_instance(form_id)}
                self.assertFalse(
                    mod01.validate_record(form_id, instance))

    def test_r9_006_control_plain_minimal_validates_all_closed(self):
        for form_id in ("16", "17", "19", "20", "21"):
            with self.subTest(form_id=form_id):
                instance = mod01.minimal_valid_instance(form_id)
                self.assertTrue(
                    mod01.validate_record(form_id, instance))

    def test_r9_006_control_plain_extra_field_refused(self):
        instance = mod01.minimal_valid_instance("16")
        instance["evil_extra_field"] = "x"
        self.assertFalse(mod01.validate_record("16", instance))

    def test_r9_006_control_honest_non_text_key_refused(self):
        instance = mod01.minimal_valid_instance("16")
        instance[12345] = "x"
        self.assertFalse(mod01.validate_record("16", instance))

    def test_r9_006_control_text_lie_storing_allowed_name(self):
        lie = HashEqLieKey("claim_sentence", "claim_sentence")
        instance = {lie: "x", **mod01.minimal_valid_instance("16")}
        self.assertTrue(mod01.validate_record("16", instance))

    def test_r9_006_control_text_lie_storing_extra_name_refused(self):
        lie = HashEqLieKey(
            "evil_extra_field",
            "headline_unit_identifier_and_issue_date")
        instance = {lie: "x", **mod01.minimal_valid_instance("16")}
        self.assertFalse(mod01.validate_record("16", instance))


class TestR9007RequiredFieldPresence(unittest.TestCase):

    def test_r9_007_defect_missing_first_required_closed_16(self):
        instance = record_missing_first_required("16")
        self.assertFalse(mod01.validate_record("16", instance))

    def test_r9_007_defect_missing_first_required_open_forms(self):
        for form_id in ("1", "2", "3", "5", "10"):
            with self.subTest(form_id=form_id):
                instance = record_missing_first_required(form_id)
                self.assertFalse(
                    mod01.validate_record(form_id, instance))

    def test_r9_007_control_plain_minimal_validates(self):
        for form_id in ("16", "1", "2", "3", "5", "10"):
            with self.subTest(form_id=form_id):
                instance = mod01.minimal_valid_instance(form_id)
                self.assertTrue(
                    mod01.validate_record(form_id, instance))

    def test_r9_007_control_plain_missing_required_refused(self):
        for form_id in ("16", "1", "2", "3", "5", "10"):
            with self.subTest(form_id=form_id):
                instance = mod01.minimal_valid_instance(form_id)
                first = mod01.required_fields(form_id)[0]
                del instance[first]
                self.assertFalse(
                    mod01.validate_record(form_id, instance))

    def test_r9_007_control_lie_key_storing_present_field(self):
        instance = mod01.minimal_valid_instance("16")
        self.assertTrue(mod01.validate_record("16", instance))


class TestR9008StoreAddressingOutsideNamedKinds(unittest.TestCase):

    def test_r9_008_defect_iter_lie_deque_two_kinds_refused(self):
        addressing = IterLieDeque(["bogus", "pilot"])
        self.assertFalse(mod01.validate_store_addressing(addressing))

    def test_r9_008_defect_iter_lie_deque_one_bogus_refused(self):
        addressing = IterLieDeque(["bogus"])
        self.assertFalse(mod01.validate_store_addressing(addressing))

    def test_r9_008_defect_iter_lie_userlist_refused(self):
        for stored in (["bogus"], ["bogus", "pilot"]):
            with self.subTest(stored=stored):
                addressing = IterLieUserList(stored)
                self.assertFalse(
                    mod01.validate_store_addressing(addressing))

    def test_r9_008_defect_iter_lie_userdict_refused(self):
        addressing = IterLieUserDict({"bogus": 1, "pilot": 2})
        self.assertFalse(mod01.validate_store_addressing(addressing))

    def test_r9_008_control_iter_lie_deque_storing_sweep(self):
        addressing = IterLieDeque(["sweep"])
        self.assertTrue(mod01.validate_store_addressing(addressing))

    def test_r9_008_control_iter_lie_userlist_storing_sweep(self):
        addressing = IterLieUserList(["sweep"])
        self.assertTrue(mod01.validate_store_addressing(addressing))

    def test_r9_008_control_plain_deque_both_ways(self):
        self.assertTrue(mod01.validate_store_addressing(deque(["sweep"])))
        self.assertTrue(mod01.validate_store_addressing(deque(["pilot"])))
        self.assertFalse(mod01.validate_store_addressing(deque(["bogus"])))
        self.assertFalse(mod01.validate_store_addressing(deque([])))
        self.assertFalse(
            mod01.validate_store_addressing(deque(["sweep", "pilot"])))

    def test_r9_008_control_plain_userlist_both_ways(self):
        self.assertTrue(
            mod01.validate_store_addressing(UserList(["sweep"])))
        self.assertFalse(
            mod01.validate_store_addressing(UserList(["bogus"])))
        self.assertFalse(
            mod01.validate_store_addressing(UserList(["sweep", "pilot"])))

    def test_r9_008_control_named_kinds_held(self):
        self.assertTrue(mod01.validate_store_addressing(["sweep"]))
        self.assertTrue(mod01.validate_store_addressing(("sweep",)))
        self.assertTrue(mod01.validate_store_addressing({"sweep"}))
        self.assertTrue(mod01.validate_store_addressing({"sweep": 1}))
        self.assertFalse(mod01.validate_store_addressing(["bogus"]))
        self.assertFalse(
            mod01.validate_store_addressing(["sweep", "pilot"]))


class TestR9009StoreIndexStoredKind(unittest.TestCase):

    def test_r9_009_defect_storing_sweep_reporting_pilot(self):
        kind = ReportedKind("sweep", "pilot")
        self.assertTrue(mod01.validate_store_kind(kind))
        self.assertEqual("store namespace: sweep", mod01.store_index(kind))

    def test_r9_009_defect_storing_pilot_reporting_sweep(self):
        kind = ReportedKind("pilot", "sweep")
        self.assertTrue(mod01.validate_store_kind(kind))
        self.assertEqual("store namespace: pilot", mod01.store_index(kind))

    def test_r9_009_defect_storing_bogus_reporting_sweep(self):
        kind = ReportedKind("bogus", "sweep")
        self.assertFalse(mod01.validate_store_kind(kind))
        self.assertEqual("store namespace: bogus", mod01.store_index(kind))

    def test_r9_009_control_plain_kinds_both_ways(self):
        self.assertEqual(
            "store namespace: sweep", mod01.store_index("sweep"))
        self.assertEqual(
            "store namespace: pilot", mod01.store_index("pilot"))
        self.assertEqual(
            "store namespace: live", mod01.store_index("live"))
        indexes = [mod01.store_index(kind) for kind in mod01.STORE_KINDS]
        self.assertEqual(3, len(set(indexes)))


if __name__ == "__main__":
    unittest.main()
