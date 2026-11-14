"""Fix wave 7 pins, Builder 3: MOD-01 rows R7-004, R7-005, R7-011.

Row R7-004: the value judgements inside the record validation
branches stand on the stored text through base class operations.
Row R7-005: the validation acts outside the inner function read
handed records and values through base class operations only.
Row R7-011: the fold judges no name from a string reading a non
text key itself supplies.
Each defect form fails on the uncured module and passes on the
cured module. Lawful controls pass both ways.
"""
import unittest

from crucible import mod01


class EqStr(str):
    """A text value whose equality reading answers True against
    every value and whose inequality reading answers False, while
    the text it stores stands as given. Its hash is the plain
    string hash of the stored text."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(str.__str__(self))


class PrefixLieStr(str):
    """A text value whose startswith reading answers True for
    every prefix, while the text it stores stands as given."""

    def startswith(self, prefix, *args):
        return True


class MarkerLieStr(str):
    """A text value whose startswith reading answers True and
    whose contains reading answers True for every part, while
    the text it stores stands as given."""

    def startswith(self, prefix, *args):
        return True

    def __contains__(self, part):
        return True


class GetLieDict(dict):
    """A dict whose get reading answers from a supplied lie
    mapping, while its stored contents stand as given."""

    def __init__(self, stored, lie):
        dict.__init__(self, stored)
        self._lie = dict(lie)

    def get(self, key, default=None):
        if key in self._lie:
            return self._lie[key]
        return dict.get(self, key, default)


class ContainsLieDict(dict):
    """A dict storing nothing whose contains reading answers
    True for every key and whose item reading supplies a valid
    open marker value for every key."""

    def __contains__(self, key):
        return True

    def __getitem__(self, key):
        return "open: OP-13 value stands open"


class StrObj:
    """A non text key object storing a private string and
    reporting it through its own string reading, with identity
    hash and identity equality."""

    def __init__(self, reported):
        self._reported = reported

    def __str__(self):
        return self._reported


def form4_with(field, value):
    instance = mod01.minimal_valid_instance("4")
    instance[field] = value
    return instance


class TestR7004ValueJudgements(unittest.TestCase):
    def test_calibration_eq_lie_bogus_fails(self):
        self.assertFalse(mod01.validate_calibration_field(EqStr("bogus")))

    def test_calibration_eq_lie_storing_permitted_value_passes(self):
        value = EqStr(mod01.CALIBRATION_FIELD_VALUE)
        self.assertTrue(mod01.validate_calibration_field(value))

    def test_store_kind_eq_lie_bogus_fails(self):
        self.assertFalse(mod01.validate_store_kind(EqStr("bogus")))

    def test_store_kind_eq_lie_storing_valid_kind_passes(self):
        self.assertTrue(mod01.validate_store_kind(EqStr("sweep")))

    def test_lien_eq_lie_bogus_fails(self):
        self.assertFalse(mod01.validate_lien_state(EqStr("bogus lien")))

    def test_lien_eq_lie_storing_valid_state_passes(self):
        self.assertTrue(mod01.validate_lien_state(EqStr("no lien in force")))

    def test_lien_eq_lie_storing_released_cross_seam_fails(self):
        self.assertFalse(
            mod01.validate_lien_state(EqStr("released"), cross_seam=True))

    def test_form4_calibration_eq_lie_fails(self):
        instance = form4_with("calibration_claim_field", EqStr("bogus"))
        self.assertFalse(mod01.validate_record("4", instance))

    def test_form4_store_kind_eq_lie_fails(self):
        instance = form4_with("store_kind", EqStr("bogus"))
        self.assertFalse(mod01.validate_record("4", instance))

    def test_form10_lien_eq_lie_fails(self):
        instance = mod01.minimal_valid_instance("10")
        instance["lien_state"] = EqStr("bogus lien")
        self.assertFalse(mod01.validate_record("10", instance))

    def test_form1_slug_prefix_lie_fails(self):
        instance = mod01.minimal_valid_instance("1")
        instance["farm_size_steps"] = PrefixLieStr("a closed value, no marker")
        self.assertFalse(mod01.validate_record("1", instance))

    def test_form1_slug_prefix_lie_storing_open_marker_passes(self):
        instance = mod01.minimal_valid_instance("1")
        instance["farm_size_steps"] = PrefixLieStr(
            "open: OP-13 value stands open")
        self.assertTrue(mod01.validate_record("1", instance))

    def test_plain_controls_both_ways(self):
        self.assertFalse(mod01.validate_calibration_field("bogus"))
        self.assertTrue(mod01.validate_calibration_field(
            mod01.CALIBRATION_FIELD_VALUE))
        self.assertFalse(mod01.validate_store_kind("bogus"))
        self.assertTrue(mod01.validate_store_kind("pilot"))
        self.assertFalse(mod01.validate_lien_state("bogus lien"))
        self.assertTrue(mod01.validate_lien_state("released"))
        self.assertTrue(mod01.validate_record(
            "4", mod01.minimal_valid_instance("4")))
        self.assertTrue(mod01.validate_record(
            "10", mod01.minimal_valid_instance("10")))
        self.assertTrue(mod01.validate_record(
            "1", mod01.minimal_valid_instance("1")))


class TestR7005ActsOutsideInner(unittest.TestCase):
    def test_seal_match_record_get_lie_fails(self):
        manifest = {"family_version": "v1",
                    "sealed_family_record_hash": "h1"}
        record = GetLieDict(
            {"family_version": "v2", "family_manifest_hash": "h2"},
            {"family_version": "v1", "family_manifest_hash": "h1"})
        self.assertFalse(mod01.validate_family_seal_match(manifest, record))

    def test_seal_match_manifest_get_lie_fails(self):
        manifest = GetLieDict(
            {"family_version": "v9",
             "sealed_family_record_hash": "h9"},
            {"family_version": "v1",
             "sealed_family_record_hash": "h1"})
        record = {"family_version": "v1", "family_manifest_hash": "h1"}
        self.assertFalse(mod01.validate_family_seal_match(manifest, record))

    def test_seal_match_stored_match_with_get_lie_passes(self):
        manifest = {"family_version": "v1",
                    "sealed_family_record_hash": "h1"}
        record = GetLieDict(
            {"family_version": "v1", "family_manifest_hash": "h1"},
            {"family_version": "v9", "family_manifest_hash": "h9"})
        self.assertTrue(mod01.validate_family_seal_match(manifest, record))

    def test_seal_match_plain_controls(self):
        manifest = {"family_version": "v1",
                    "sealed_family_record_hash": "h1"}
        matching = {"family_version": "v1", "family_manifest_hash": "h1"}
        mismatched = {"family_version": "v1", "family_manifest_hash": "h9"}
        self.assertTrue(mod01.validate_family_seal_match(manifest, matching))
        self.assertFalse(
            mod01.validate_family_seal_match(manifest, mismatched))

    def test_family_completeness_text_lie_fails(self):
        record = mod01.minimal_valid_family_record()
        record["farm size steps"] = MarkerLieStr(
            "closed value, no marker at all")
        self.assertFalse(mod01.family_supports_reportable_run(record))

    def test_family_completeness_text_lie_run_not_reportable(self):
        instance = mod01.minimal_valid_instance("1")
        instance["farm size steps"] = MarkerLieStr(
            "closed value, no marker at all")
        self.assertFalse(mod01.run_is_reportable("1", instance))

    def test_family_completeness_contains_lie_dict_fails(self):
        self.assertFalse(
            mod01.family_supports_reportable_run(ContainsLieDict()))

    def test_family_completeness_plain_controls(self):
        record = mod01.minimal_valid_family_record()
        self.assertTrue(mod01.family_supports_reportable_run(record))
        missing = mod01.minimal_valid_family_record()
        del missing["farm size steps"]
        self.assertFalse(mod01.family_supports_reportable_run(missing))

    def test_reportable_run_get_lie_failed_fails(self):
        stored = mod01.minimal_valid_instance("4")
        dict.__setitem__(stored, "run_status", "failed")
        instance = GetLieDict(stored, {"run_status": "completed"})
        self.assertFalse(mod01.run_is_reportable("4", instance))

    def test_reportable_run_plain_controls(self):
        failed = mod01.minimal_valid_instance("4")
        failed["run_status"] = "failed"
        self.assertFalse(mod01.run_is_reportable("4", failed))
        self.assertTrue(mod01.run_is_reportable(
            "4", mod01.minimal_valid_instance("4")))

    def test_partial_marking_get_lie_fails(self):
        record = GetLieDict(
            {"partial": True, "marked_partial": False},
            {"marked_partial": True})
        self.assertFalse(mod01.partial_record_is_marked(record=record))

    def test_partial_marking_stored_marked_with_get_lie_passes(self):
        record = GetLieDict(
            {"partial": True, "marked_partial": True},
            {"marked_partial": False})
        self.assertTrue(mod01.partial_record_is_marked(record=record))

    def test_partial_marking_plain_controls(self):
        self.assertTrue(mod01.partial_record_is_marked(
            record={"partial": True, "marked_partial": True}))
        self.assertFalse(mod01.partial_record_is_marked(
            record={"partial": True, "marked_partial": False}))

    def test_run_status_get_lie_fails(self):
        record = GetLieDict(
            {"run_status": "failed", "presented_as": "completed"},
            {"run_status": "completed"})
        self.assertFalse(mod01.validate_run_status(record=record))

    def test_run_status_eq_lie_bogus_fails(self):
        self.assertFalse(mod01.validate_run_status(
            record_status=EqStr("bogus"), presented_as=None))

    def test_run_status_eq_lie_storing_completed_passes(self):
        self.assertTrue(mod01.validate_run_status(
            record_status=EqStr("completed"), presented_as="completed"))

    def test_run_status_plain_controls(self):
        self.assertTrue(mod01.validate_run_status(
            record_status="completed", presented_as="completed"))
        self.assertFalse(mod01.validate_run_status(
            record_status="failed", presented_as="completed"))

    def test_version_stamp_get_lie_supplying_field_fails(self):
        stamp = GetLieDict(
            {"family_version": "v1", "family_manifest_hash": "h1"},
            {"rule_version_set": "r1"})
        self.assertFalse(mod01.validate_version_stamp(stamp))

    def test_version_stamp_get_lie_supplying_sealed_hash_fails(self):
        stamp = GetLieDict(
            {"family_version": "v1", "family_manifest_hash": "h2",
             "rule_version_set": "r1"},
            {"family_manifest_hash": "h1"})
        self.assertFalse(mod01.validate_version_stamp(
            stamp, sealed_family_hash="h1"))

    def test_version_stamp_stored_complete_with_get_lie_passes(self):
        stamp = GetLieDict(
            {"family_version": "v1", "family_manifest_hash": "h1",
             "rule_version_set": "r1"},
            {"family_version": None})
        self.assertTrue(mod01.validate_version_stamp(
            stamp, sealed_family_hash="h1"))

    def test_version_stamp_plain_controls(self):
        complete = {"family_version": "v1", "family_manifest_hash": "h1",
                    "rule_version_set": "r1"}
        incomplete = {"family_version": "v1", "family_manifest_hash": "h1"}
        mismatched = {"family_version": "v1",
                      "family_manifest_hash": "h9",
                      "rule_version_set": "r1"}
        self.assertTrue(mod01.validate_version_stamp(
            complete, sealed_family_hash="h1"))
        self.assertFalse(mod01.validate_version_stamp(incomplete))
        self.assertFalse(mod01.validate_version_stamp(
            mismatched, sealed_family_hash="h1"))


class TestR7011NonTextKeyFold(unittest.TestCase):
    def test_normalised_characters_non_text_key_is_empty(self):
        self.assertEqual(
            mod01._normalised_characters(StrObj("amount")), [])

    def test_normalised_characters_text_control(self):
        self.assertEqual(mod01._normalised_characters("Ab"), ["a", "b"])

    def test_folded_key_matches_non_text_reporting_amount_is_false(self):
        self.assertFalse(
            mod01._folded_key_matches(StrObj("amount"), "amount"))

    def test_folded_key_carries_non_text_reporting_marker_is_false(self):
        self.assertFalse(
            mod01._folded_key_carries(StrObj("realmoney"), "realmoney"))

    def test_carries_real_money_non_text_keys_is_false(self):
        value = {StrObj("amount"): 10, StrObj("currency"): "USD"}
        self.assertFalse(mod01._carries_real_money_value(value))

    def test_form4_record_with_non_text_money_keys_validates(self):
        instance = mod01.minimal_valid_instance("4")
        instance["control_values"] = {
            StrObj("amount"): 10, StrObj("currency"): "USD"}
        self.assertTrue(mod01.validate_record("4", instance))

    def test_form4_record_with_plain_money_keys_fails_control(self):
        instance = mod01.minimal_valid_instance("4")
        instance["control_values"] = {"amount": 10, "currency": "USD"}
        self.assertFalse(mod01.validate_record("4", instance))

    def test_form4_record_with_clean_text_keys_validates_control(self):
        instance = mod01.minimal_valid_instance("4")
        instance["control_values"] = {"note": 10, "unit": "USD"}
        self.assertTrue(mod01.validate_record("4", instance))

    def test_carries_real_money_bytes_keys_is_false_control(self):
        value = {b"amount": 10, b"currency": "USD"}
        self.assertFalse(mod01._carries_real_money_value(value))


if __name__ == "__main__":
    unittest.main()
