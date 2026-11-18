"""Step 15, second run, fix wave 10 pins for Builder 11.

Each defect test pins one charged defect instance from the
Round 10 register on the MOD-12 loci in crucible/mod12.py:
the crucible/mod12.py limb of R10-001 at _stored_text and
_folded_money_key, R10-023 at apply_family_edit and at the
sealed edit check in validate_family_record, and R10-040 at
seal_family_record. The stored text pins stand under section 2
of the Round 10 register, the governing stored text settlement:
stored text is read through base readings only, bytes and
bytearray and memoryview values are read by decoding their
stored bytes as UTF-8 with undecodable bytes dropped, and
container keys are read part by part, joined in order, and as
a single part container. Control tests stand both ways beside
each family. Values are simulated and test values only.
"""
# Step 16 fix merge: pin dispositions for this file stand in design/steps/step-16-fix-merge.md.
import unittest

from crucible import mod12


def run_record(extra):
    record = {"run_class": "screening", "seed_domain": "screening"}
    record.update(extra)
    return record


class LyingBytes(bytes):
    """A bytes subclass storing one text and reporting another
    through its own string reading."""

    def __str__(self):
        return "harmless"


class DenySealDict(dict):
    """A dict subclass storing a sealed record whose own get
    reading denies the seal."""

    def get(self, key, default=None):
        if key == "sealed":
            return False
        return dict.get(self, key, default)


class DenySealedEditDict(dict):
    """A dict subclass storing a sealed and edited record whose
    own get reading denies both marks."""

    def get(self, key, default=None):
        if key in ("sealed", "edited_after_seal"):
            return None
        return dict.get(self, key, default)


class RaisingGetDict(dict):
    """A dict subclass storing a change whose own get reading
    raises instead of answering."""

    def get(self, key, default=None):
        raise RuntimeError("hostile get reading")


class RaisingContainsDict(dict):
    """A dict subclass storing a change whose own contains
    reading raises instead of answering."""

    def __contains__(self, key):
        raise RuntimeError("hostile contains reading")


class FalseText(str):
    """A text value storing ordinary text whose own truth
    reading answers False."""

    def __bool__(self):
        return False


class TrueText(str):
    """A text value storing no text whose own truth reading
    answers True."""

    def __bool__(self):
        return True


class RaisingText(str):
    """A text value storing ordinary text whose own truth
    reading raises instead of answering."""

    def __bool__(self):
        raise RuntimeError("hostile truth reading")


class FalseList(list):
    """A list value storing one item whose own truth reading
    answers False."""

    def __bool__(self):
        return False


class TestR10001Mod12StoredText(unittest.TestCase):

    def test_defect_bytes_amount_currency_pair_refused(self):
        record = run_record({b"amount": 5, b"currency": "unit"})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_bytes_real_money_marker_refused(self):
        record = run_record({b"real_money_note": 1})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_bytes_undecodable_bytes_dropped(self):
        record = run_record({b"real_money\xffnote": 1})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_bytes_subclass_lying_string_reading(self):
        record = run_record({LyingBytes(b"real_money_note"): 1})
        self.assertFalse(mod12.validate_run_record(record))
        self.assertEqual(
            mod12._stored_text(LyingBytes(b"real_money")),
            "real_money")

    def test_defect_bytearray_and_memoryview_helper_readings(self):
        self.assertEqual(
            mod12._stored_text(bytearray(b"real_money")),
            "real_money")
        self.assertEqual(
            mod12._stored_text(memoryview(b"real_money")),
            "real_money")
        self.assertEqual(
            mod12._folded_money_key(bytearray(b"real_money")),
            "realmoney")
        self.assertEqual(
            mod12._folded_money_key(memoryview(b"real_money")),
            "realmoney")

    def test_defect_memoryview_key_refused(self):
        record = run_record({memoryview(b"real_money_note"): 1})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_single_part_container_pair_refused(self):
        record = run_record(
            {("amount",): 5, ("currency",): "unit"})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_split_container_pair_refused(self):
        record = run_record(
            {("amo", "unt"): 5, ("cur", "rency"): "unit"})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_bytes_inside_container_pair_refused(self):
        record = run_record(
            {(b"amount",): 5, (b"currency",): "unit"})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_split_container_marker_refused(self):
        record = run_record({("real_", "money_note"): 1})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_nested_bytes_pair_refused(self):
        record = run_record(
            {"inner": {b"amount": 5, b"currency": "unit"}})
        self.assertFalse(mod12.validate_run_record(record))

    def test_defect_bytes_anchor_field_wrong_count_refused(self):
        record = run_record({b"anchor_scenario_values": [1, 2]})
        self.assertFalse(mod12.validate_run_record(record))

    def test_control_plain_record_valid(self):
        self.assertTrue(mod12.validate_run_record(
            run_record({"note": 1})))

    def test_control_str_pair_refused_as_before(self):
        record = run_record({"amount": 5, "currency": "unit"})
        self.assertFalse(mod12.validate_run_record(record))

    def test_control_bytes_harmless_key_valid(self):
        record = run_record({b"harmless_note": 1})
        self.assertTrue(mod12.validate_run_record(record))

    def test_control_bytes_anchor_field_count_three_valid(self):
        record = run_record(
            {b"anchor_scenario_values": [1, 2, 3]})
        self.assertTrue(mod12.validate_run_record(record))


class TestR10023FamilyEditHandedReadings(unittest.TestCase):

    def test_defect_record_get_denying_seal_still_new_id(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record(family_id="fam-b11"))
        edited = mod12.apply_family_edit(
            DenySealDict(sealed), change={"field": "value"})
        self.assertEqual(edited["family_id"], "fam-b11-edited-1")
        self.assertEqual(
            edited["family_identifier"], "fam-b11-edited-1")
        self.assertTrue(edited["identifier_changed"])
        self.assertTrue(edited["edited_after_seal"])
        self.assertFalse(edited["sealed"])

    def test_defect_change_get_raising_edit_uses_stored(self):
        change = RaisingGetDict({"field": "value"})
        edited = mod12.apply_family_edit(
            mod12.make_family_record(), change=change)
        self.assertEqual(edited["field"], "value")

    def test_defect_change_contains_raising_claims_apply(self):
        change = RaisingContainsDict(
            {"headline_claims": ["brand new claim"]})
        edited = mod12.apply_family_edit(
            mod12.make_family_record(), change=change)
        self.assertEqual(edited["headline_claims"],
                         ["brand new claim"])
        self.assertEqual(edited["claims"], ["brand new claim"])

    def test_defect_check_get_raising_standing_claim_passes(self):
        change = {
            "headline_claims": ["headline claim 1"],
            "kill_check_fields": [
                RaisingGetDict({"claim": "headline claim 1"})],
        }
        edited = mod12.apply_family_edit(
            mod12.make_family_record(), change=change)
        self.assertEqual(edited["headline_claims"],
                         ["headline claim 1"])

    def test_defect_check_get_raising_stale_claim_refused(self):
        change = {
            "headline_claims": ["brand new claim"],
            "kill_check_fields": [
                RaisingGetDict({"claim": "headline claim 1"})],
        }
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(
                mod12.make_family_record(), change=change)

    def test_defect_validate_get_denying_sealed_edit_fails(self):
        record = mod12.make_family_record()
        record["sealed"] = True
        record["edited_after_seal"] = True
        self.assertFalse(mod12.validate_family_record(
            DenySealedEditDict(record)))

    def test_control_plain_sealed_edit_changes_id(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record(family_id="fam-b11"))
        edited = mod12.apply_family_edit(
            sealed, change={"field": "value"})
        self.assertEqual(edited["family_id"], "fam-b11-edited-1")

    def test_control_plain_unsealed_edit_keeps_id(self):
        record = mod12.make_family_record(family_id="fam-b11")
        edited = mod12.apply_family_edit(
            record, change={"field": "value"})
        self.assertEqual(edited["family_id"], "fam-b11")
        self.assertNotIn("identifier_changed", edited)

    def test_control_validate_plain_sealed_edit_fails(self):
        record = mod12.make_family_record()
        record["sealed"] = True
        record["edited_after_seal"] = True
        self.assertFalse(mod12.validate_family_record(record))


class TestR10040SealStoredPresence(unittest.TestCase):

    def test_defect_false_truth_completeness_item_seals(self):
        record = mod12.make_family_record()
        record["farm size steps"] = FalseText("present text")
        record["farm_size_steps"] = FalseText("present text")
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])

    def test_defect_false_truth_list_item_seals(self):
        record = mod12.make_family_record()
        record["farm size steps"] = FalseList(["present item"])
        record["farm_size_steps"] = FalseList(["present item"])
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])

    def test_defect_true_truth_empty_item_refused(self):
        record = mod12.make_family_record()
        record["farm size steps"] = TrueText("")
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)

    def test_defect_raising_truth_completeness_item_seals(self):
        record = mod12.make_family_record()
        record["farm size steps"] = RaisingText("present text")
        record["farm_size_steps"] = RaisingText("present text")
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])

    def test_defect_false_truth_version_and_hash_kept(self):
        record = mod12.make_family_record()
        record["family_version"] = FalseText("version 9")
        record["family_manifest_hash"] = FalseText("hash 9")
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 9")
        self.assertEqual(sealed["seal_version"], "version 9")
        self.assertEqual(sealed["seal"]["hash"], "hash 9")
        self.assertEqual(sealed["seal_hash"], "hash 9")

    def test_defect_true_truth_empty_version_and_hash_default(self):
        record = mod12.make_family_record()
        record["family_version"] = TrueText("")
        record["family_manifest_hash"] = TrueText("")
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 1")
        self.assertIsNone(sealed["seal"]["hash"])
        self.assertEqual(
            sealed["seal"]["hash_standing"],
            "no hash value stands on the record; "
            "no hash stands computed by this seal")

    def test_defect_raising_truth_version_kept(self):
        record = mod12.make_family_record()
        record["family_version"] = RaisingText("version 7")
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 7")

    def test_control_plain_seal_keeps_stored_version_and_hash(self):
        record = mod12.make_family_record()
        record["family_manifest_hash"] = "stored hash value"
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 1")
        self.assertEqual(
            sealed["seal"]["hash"],
            "stored hash value")

    def test_control_missing_item_refused_as_before(self):
        record = mod12.make_family_record()
        del record["farm size steps"]
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)


if __name__ == "__main__":
    unittest.main()
