"""Test group TG-01.3. Family record completeness and the seal.

Slice S-01, MOD-01 Types and validation. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod01, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
The completeness fields named here are the fields the brief names for the
SweepFamilyRecord at Shape 1, in plan section 3 Form 1 item 1. Values that
stand open under open point OP-13 enter as open markers only.
"""
import unittest

try:
    from crucible import mod01
    SURFACE = mod01
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-01.3"

COMPLETENESS_FIELDS = (
    "farm size steps",
    "patience steps",
    "the longer horizon value",
    "the confidence interval method",
    "the reporting resolution for each of the three traces",
    "the decay arm donor items",
)


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": pinned behaviour not built: " + behaviour
            + " (surface crucible.mod01 stands absent: " + repr(SURFACE_ERROR) + ")"
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": pinned behaviour not built: " + behaviour
                + " (surface crucible.mod01 lacks " + attr + ")"
            )


def make_missing_field_test(field):
    def test(self):
        behaviour = "a family record missing " + field + " supports no reportable run"
        require_surface(self, behaviour, "minimal_valid_family_record", "family_supports_reportable_run")
        record = SURFACE.minimal_valid_family_record()
        del record[field]
        self.assertFalse(SURFACE.family_supports_reportable_run(record))

    test.__doc__ = (
        "Fixture: a SweepFamilyRecord missing " + field
        + ", derived from the brief field list at Shape 1; no inventory fixture is assigned to this group in the mapping.\n"
        "Pins: a family record missing any one of the completeness fields the brief names supports no reportable run; this test pins the case of " + field + ".\n"
        "Bar: values that stand open under open point OP-13 enter as open markers, never as invented numbers, so an open marker in this position stands as present and an absent field does not.\n"
        "Failure: while the surface stands absent the test fails naming this behaviour and TG-01.3; with the surface present, a family record missing this field supporting a reportable run fails."
    )
    return test


class TestFamilyCompletenessBar(unittest.TestCase):
    def test_complete_family_record_supports_reportable_run(self):
        """Fixture: a SweepFamilyRecord carrying every completeness field the brief names before any run in the family is reportable, derived from the brief field list at Shape 1, with open OP-13 values carried as open markers.
        Pins: a family record carrying every named completeness field supports a reportable run on the completeness limb.
        Bar: the mapping states no bar on a complete family record on this limb.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.3; with the surface present, a complete family record failing the completeness limb fails.
        """
        behaviour = "a complete SweepFamilyRecord supports a reportable run on the completeness limb"
        require_surface(self, behaviour, "minimal_valid_family_record", "family_supports_reportable_run")
        record = SURFACE.minimal_valid_family_record()
        self.assertTrue(SURFACE.family_supports_reportable_run(record))

    def test_open_op13_values_enter_as_open_markers(self):
        """Fixture: a SweepFamilyRecord whose completeness fields, the six fields open point OP-13 names, carry open markers in place of numbers, derived from the brief field list at Shape 1, and the same record with one marker replaced by a number.
        Pins: every completeness field that stands open under OP-13 carries an open marker carrying the OP-13 label, never an invented number, and a record carrying the markers stands complete on those fields, while a record with a marker replaced by a number fails the completeness limb.
        Bar: a test that supplies an invented step value to make the record complete fails this group; the number in the replacement case stands only as the barred act under test, asserted to fail, and as no fixture value and no step value.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.3; with the surface present, a validator rejecting the open marker form, a completeness field standing without its marker, or a record whose marker stands replaced by a number supporting a reportable run, fails.
        """
        behaviour = "OP-13 open values enter the family record as open markers, never as invented numbers"
        require_surface(self, behaviour, "minimal_valid_family_record", "family_supports_reportable_run")
        record = SURFACE.minimal_valid_family_record()
        for field in COMPLETENESS_FIELDS:
            self.assertIn(field, record)
            value = record[field]
            self.assertIsInstance(value, str, field)
            self.assertTrue(value.startswith("open:"), field)
            self.assertIn("OP-13", value)
        self.assertTrue(SURFACE.family_supports_reportable_run(record))
        replaced = SURFACE.minimal_valid_family_record()
        invented_number = 1
        replaced[COMPLETENESS_FIELDS[0]] = invented_number
        self.assertFalse(SURFACE.family_supports_reportable_run(replaced))


for _field in COMPLETENESS_FIELDS:
    _slug = _field.replace(" ", "_").replace(",", "")
    setattr(TestFamilyCompletenessBar, "test_missing_" + _slug, make_missing_field_test(_field))


del _field, _slug


class TestFamilySealMatching(unittest.TestCase):
    def test_family_seal_matching_values_pass(self):
        """Fixture: a sealed family manifest and a run record carrying family version and manifest hash values matching the sealed manifest, derived from the seal passage at Shape 1 and Form 23.
        Pins: a run record whose version and hash match the sealed manifest passes the seal matching check, per Shape 1.
        Bar: seal matching on this form is a recorded value comparison, as Form 23 states, and this test claims no stronger seal property.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.3; with the surface present, a matching run record failing the check fails.
        """
        behaviour = "run record version and hash matching the sealed family manifest pass seal matching"
        require_surface(self, behaviour, "validate_family_seal_match")
        manifest = {"family_version": "v", "sealed_family_record_hash": "h"}
        record = {"family_version": "v", "family_manifest_hash": "h"}
        self.assertTrue(SURFACE.validate_family_seal_match(manifest, record))

    def test_family_seal_mismatched_version_fails(self):
        """Fixture: a sealed family manifest and a run record carrying a mismatched family version, derived from the seal passage at Shape 1.
        Pins: validation fails a run record whose family version does not match the sealed manifest, per Shape 1.
        Bar: any edit to a sealed family record creates a new family identifier, tested at TG-12.1; this group pins only the match check.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.3; with the surface present, a mismatched version passing the check fails.
        """
        behaviour = "run record with a family version mismatching the sealed manifest fails validation"
        require_surface(self, behaviour, "validate_family_seal_match")
        manifest = {"family_version": "v", "sealed_family_record_hash": "h"}
        record = {"family_version": "other version", "family_manifest_hash": "h"}
        self.assertFalse(SURFACE.validate_family_seal_match(manifest, record))

    def test_family_seal_mismatched_hash_fails(self):
        """Fixture: a sealed family manifest and a run record carrying a mismatched manifest hash value, derived from the seal passage at Shape 1.
        Pins: validation fails a run record whose manifest hash does not match the sealed manifest, per Shape 1.
        Bar: any edit to a sealed family record creates a new family identifier, tested at TG-12.1; this group pins only the match check.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.3; with the surface present, a mismatched hash passing the check fails.
        """
        behaviour = "run record with a manifest hash mismatching the sealed manifest fails validation"
        require_surface(self, behaviour, "validate_family_seal_match")
        manifest = {"family_version": "v", "sealed_family_record_hash": "h"}
        record = {"family_version": "v", "family_manifest_hash": "other hash"}
        self.assertFalse(SURFACE.validate_family_seal_match(manifest, record))


if __name__ == "__main__":
    unittest.main()
