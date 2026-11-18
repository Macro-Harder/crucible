"""Step 16 fix wave 4, Builder 1 tests.

Row F4-01 (Medium, ruling T16-49): the forgery pair. A sealed
standing that the seal act did not write passes as sealed, in
two limbs: (a) at the validation and reportable doors, a record
carrying only the four seal keys present, sealed True, and a
seal dict passes, no door reading the seal contents against
the form the seal act writes; (b) at the seal act, a never
sealed record already carrying hand placed edit keys seals,
the helper never reading the edited identifier suffix form,
the sealed value, or any prior seal.

Test first: every defect test in this file was written against
the landed product at head
1e1c33acdd33d2a8bdf081754cbca226a3ce355a and stands to fail
there for the reason its name states, except the preserved
side tests, which pass there and must keep passing. The bench
runs of this file stand owed while the PC bench tunnel stands
closed, as the builder paper states in the open.

Supplied completeness values in this file are test inputs
only, standing for no design value and adopted nowhere
(OP-16). No seed is drawn, read from a clock, or assigned in
completion order (DQ7-02). Bench Python 3.14.4 stands as the
interpreter basis for every figure in the builder paper.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01
from crucible import mod11
from crucible import mod12

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)

SEAL_KEYS = (
    "seal",
    "seal_version",
    "seal_hash",
    "sweep_manifest",
)

EDIT_KEYS = (
    "runs_under",
    "edited_after_seal",
    "identifier_changed",
    "runs_start_again",
)


def supplied_family():
    record = mod12.make_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def sealed_supplied():
    return mod12.seal_family_record(supplied_family())


def sealed_with_recorded_hash():
    record = supplied_family()
    record["family_manifest_hash"] = "supplied hash value for the test"
    return mod12.seal_family_record(record)


def forged_sealed():
    """The Red 1 forged standing, as finding R4-RED1-N01 files
    it: the four seal keys hand placed, sealed True, a seal dict
    carrying invented version, hash, and hash standing values,
    a seal_version and a seal_hash that disagree with that dict
    and with each other, and a sweep_manifest value no sweep
    act produced for the record."""
    record = supplied_family()
    record["sealed"] = True
    record["seal"] = {
        "version": "invented version",
        "hash": "invented hash",
        "hash_standing": "invented hash standing",
    }
    record["seal_version"] = "a second invented version"
    record["seal_hash"] = "a second invented hash"
    record["sweep_manifest"] = "no sweep act produced this value"
    return record


def assert_refused_at_doors(case, record):
    failures = mod12.family_record_validation_failures(record)
    case.assertTrue(
        any(key in failure for failure in failures
            for key in SEAL_KEYS + EDIT_KEYS),
        failures)
    case.assertFalse(mod12.validate_family_record(record))
    case.assertFalse(mod11.validate_family_record(record))
    judgement = mod01.family_supports_reportable_run(record)
    case.assertFalse(judgement.truth_value)
    case.assertTrue(
        any(key in judgement.extra_fields
            for key in SEAL_KEYS + EDIT_KEYS),
        judgement.extra_fields)
    standing = mod01.family_reportable_standing(record)
    case.assertFalse(standing["supports_reportable_run"])
    case.assertFalse(mod01.run_is_reportable("1", record))


class TestF401ForgedSealedStandingRefused(unittest.TestCase):

    def test_forged_sealed_standing_refused_at_validation_and_doors(self):
        assert_refused_at_doors(self, forged_sealed())

    def test_seal_version_disagreeing_with_seal_dict_refused(self):
        record = sealed_supplied()
        record["seal_version"] = "a version the seal act did not write"
        assert_refused_at_doors(self, record)

    def test_seal_hash_disagreeing_with_seal_dict_refused(self):
        record = sealed_with_recorded_hash()
        record["seal_hash"] = "a hash the seal act did not write"
        assert_refused_at_doors(self, record)

    def test_family_manifest_hash_disagreeing_with_seal_refused(self):
        record = sealed_with_recorded_hash()
        record["family_manifest_hash"] = "another hash altogether"
        assert_refused_at_doors(self, record)

    def test_seal_dict_hash_standing_not_the_seal_act_form_refused(self):
        record = sealed_supplied()
        seal = dict(record["seal"])
        seal["hash_standing"] = "invented hash standing"
        record["seal"] = seal
        assert_refused_at_doors(self, record)

    def test_seal_dict_version_not_the_family_version_refused(self):
        record = sealed_supplied()
        seal = dict(record["seal"])
        seal["version"] = "version the record does not carry"
        record["seal"] = seal
        record["seal_version"] = seal["version"]
        assert_refused_at_doors(self, record)

    def test_sweep_manifest_not_the_seal_act_manifest_refused(self):
        record = sealed_supplied()
        record["sweep_manifest"] = {
            "family_identifier": "an identifier the record "
            "does not carry",
            "family_version": "a version the record does not carry",
            "sealed_family_record_hash": "a hash the record "
            "does not carry",
        }
        assert_refused_at_doors(self, record)

    def test_seal_dict_with_a_further_key_refused(self):
        record = sealed_supplied()
        seal = dict(record["seal"])
        seal["further"] = "a key the seal act does not write"
        record["seal"] = seal
        assert_refused_at_doors(self, record)


class TestF401HandPlacedEditKeysRefusedAtSeal(unittest.TestCase):

    def test_never_sealed_hand_placed_edit_keys_refused_at_seal(self):
        record = supplied_family()
        record["runs_under"] = record["family_id"]
        record["edited_after_seal"] = True
        record["identifier_changed"] = True
        record["runs_start_again"] = True
        with self.assertRaises(
                mod12.NamedControllerFailure) as caught:
            mod12.seal_family_record(record)
        self.assertTrue(
            any(key in str(caught.exception) for key in EDIT_KEYS),
            str(caught.exception))

    def test_hand_placed_edit_keys_claiming_sealed_refused_at_seal(self):
        record = supplied_family()
        record["family_id"] = record["family_id"] + "-edited-1"
        record["family_identifier"] = record["family_id"]
        record["sealed"] = True
        record["runs_under"] = record["family_id"]
        record["edited_after_seal"] = True
        record["identifier_changed"] = True
        record["runs_start_again"] = True
        with self.assertRaises(
                mod12.NamedControllerFailure) as caught:
            mod12.seal_family_record(record)
        self.assertTrue(
            any(key in str(caught.exception) for key in EDIT_KEYS),
            str(caught.exception))


class TestF401PreservedProductForms(unittest.TestCase):

    def test_product_sealed_record_still_validates_everywhere(self):
        sealed = sealed_supplied()
        self.assertEqual(
            mod12.family_record_validation_failures(sealed), [])
        self.assertTrue(mod12.validate_family_record(sealed))
        self.assertTrue(mod11.validate_family_record(sealed))
        judgement = mod01.family_supports_reportable_run(sealed)
        self.assertTrue(judgement.truth_value)
        self.assertEqual(judgement.extra_fields, ())
        self.assertTrue(mod01.run_is_reportable("1", sealed))

    def test_product_sealed_record_with_recorded_hash_still_validates(self):
        sealed = sealed_with_recorded_hash()
        self.assertEqual(sealed["seal_hash"],
                         "supplied hash value for the test")
        self.assertEqual(
            mod12.family_record_validation_failures(sealed), [])
        self.assertTrue(mod12.validate_family_record(sealed))
        self.assertTrue(mod11.validate_family_record(sealed))
        self.assertTrue(
            mod01.family_supports_reportable_run(sealed).truth_value)
        self.assertTrue(mod01.run_is_reportable("1", sealed))

    def test_product_edited_record_still_validates_everywhere(self):
        edited = mod12.apply_family_edit(sealed_supplied())
        self.assertEqual(
            mod12.family_record_validation_failures(edited), [])
        self.assertTrue(mod12.validate_family_record(edited))
        self.assertTrue(mod11.validate_family_record(edited))
        self.assertTrue(
            mod01.family_supports_reportable_run(edited).truth_value)
        self.assertTrue(mod01.run_is_reportable("1", edited))

    def test_edited_record_seals_again_and_validates(self):
        edited = mod12.apply_family_edit(sealed_supplied())
        resealed = mod12.seal_family_record(edited)
        self.assertTrue(resealed["sealed"])
        self.assertEqual(
            mod12.family_record_validation_failures(resealed), [])
        self.assertTrue(mod12.validate_family_record(resealed))
        self.assertTrue(mod11.validate_family_record(resealed))
        self.assertTrue(
            mod01.family_supports_reportable_run(
                resealed).truth_value)
        self.assertTrue(mod01.run_is_reportable("1", resealed))

    def test_unsealed_edit_record_still_stands(self):
        edited = mod12.apply_family_edit(supplied_family())
        self.assertIn("runs_under", edited)
        self.assertEqual(
            mod12.family_record_validation_failures(edited), [])
        self.assertTrue(mod12.validate_family_record(edited))
        self.assertTrue(mod11.validate_family_record(edited))
        self.assertTrue(
            mod01.family_supports_reportable_run(edited).truth_value)
        self.assertTrue(mod01.run_is_reportable("1", edited))

    def test_made_record_sealed_still_validates(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        self.assertEqual(
            mod12.family_record_validation_failures(sealed), [])
        self.assertTrue(mod12.validate_family_record(sealed))
        self.assertTrue(mod11.validate_family_record(sealed))
        self.assertTrue(
            mod01.family_supports_reportable_run(sealed).truth_value)
        self.assertTrue(mod01.run_is_reportable("1", sealed))


if __name__ == "__main__":
    unittest.main()
