"""Test group TG-01.2. Stated value sets and stated bars inside validators.

Slice S-01, MOD-01 Types and validation. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod01, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
No value in this file rests on any item from DQ-5 to DQ-30, and no fixture,
branch, or variable in this file encodes the banked stake behaviour the brief
bars at AC-6; stake values, where a form carries them, stand in test value
only, under DQ-162.
"""
import unittest

try:
    from crucible import mod01
    SURFACE = mod01
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-01.2"

LIEN_VALUES = (
    "no lien in force",
    "computed not settled",
    "settled in the chosen escrow",
    "released",
)
STORE_KINDS = ("sweep", "pilot", "live")


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


class TestLienStateValueSet(unittest.TestCase):
    def test_lien_state_accepts_exactly_four_values(self):
        """Fixture: EscrowContractState instances carrying each of the four lien values in turn, derived from the field list at Shape 9; no inventory fixture is assigned to this group in the mapping.
        Pins: the lien state field accepts exactly the four stated values (no lien in force; computed not settled; settled in the chosen escrow; released), per Shape 9, in the positions the Shape 9 bar permits.
        Bar: the mapping states no bar on the four values in their own positions beyond the cross seam limb tested separately in this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, rejection of a stated value in a permitted position fails.
        """
        behaviour = "lien state field accepts exactly the four stated values per Shape 9"
        require_surface(self, behaviour, "validate_lien_state")
        for value in LIEN_VALUES:
            self.assertTrue(SURFACE.validate_lien_state(value, cross_seam=False), value)

    def test_lien_state_rejects_invented_fifth_value(self):
        """Fixture: an EscrowContractState instance carrying a fifth invented lien value, derived from the field list at Shape 9.
        Pins: a lien value outside the stated set of four fails validation.
        Bar: a validator may not coerce a value into the permitted set and may not treat an unstated value as permitted by silence.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, acceptance of the invented value fails.
        """
        behaviour = "lien state field rejects a fifth invented value outside the Shape 9 set"
        require_surface(self, behaviour, "validate_lien_state")
        self.assertFalse(SURFACE.validate_lien_state("invented fifth lien value", cross_seam=False))

    def test_lien_cross_seam_settled_or_released_fails_while_nq45_open(self):
        """Fixture: EscrowContractState instances carrying settled in the chosen escrow, and then released, for a cross seam effect, derived from the field list at Shape 9.
        Pins: while register question NQ-45 stands open, a record carrying settled or released for a cross seam effect fails validation; this limb is tested here and again at TG-06.3.
        Bar: no settled wording stands for any seam effect while NQ-45 stands open, as the guard at plan section 2 section 8 item 6(c) states.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, a cross seam record validating as settled or released fails.
        """
        behaviour = "cross seam lien record carrying settled or released fails validation while NQ-45 stands open"
        require_surface(self, behaviour, "validate_lien_state")
        self.assertFalse(SURFACE.validate_lien_state("settled in the chosen escrow", cross_seam=True))
        self.assertFalse(SURFACE.validate_lien_state("released", cross_seam=True))
        self.assertTrue(SURFACE.validate_lien_state("computed not settled", cross_seam=True))


class TestCalibrationFieldValue(unittest.TestCase):
    def test_calibration_field_permits_only_no_claim_value(self):
        """Fixture: DetectionState and summary record instances carrying the calibration claim field at its only permitted value, the value the RunRecord form states, reading no calibration claim with self consistency wording only; derived from the brief field lists for those forms.
        Pins: the permitted value is the sole value the calibration claim field may carry, per decision D-13.
        Bar: self consistency wording only; no record may carry a calibration claim in any form.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, rejection of the sole permitted value fails.
        """
        behaviour = "calibration claim field carries its sole permitted value, no calibration claim, self consistency only"
        require_surface(self, behaviour, "validate_calibration_field")
        self.assertTrue(SURFACE.validate_calibration_field("no calibration claim, self consistency only"))

    def test_calibration_claim_in_any_form_fails(self):
        """Fixture: DetectionState and summary record instances with the calibration claim field set to a claim value.
        Pins: no record may carry a calibration claim in any form, under decision D-13.
        Bar: a test or fixture asserting calibration fails this group before it runs.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, a record carrying a calibration claim validating fails.
        """
        behaviour = "no record carries a calibration claim in any form, under decision D-13"
        require_surface(self, behaviour, "validate_calibration_field")
        self.assertFalse(SURFACE.validate_calibration_field("calibrated"))


class TestStoreKindCheck(unittest.TestCase):
    def test_store_kinds_are_distinct_namespaces(self):
        """Fixture: records addressed to each of the three separated stores (sweep, pilot, live), derived from the store kind field the brief states; no inventory fixture is assigned to this group in the mapping.
        Pins: store kinds are distinct namespaces with no shared index, per Contract G and brief section 7.6, and a record addressed to its own store kind resolves in that namespace.
        Bar: the mapping states no bar on a record addressed to its own store kind.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, two store kinds sharing an index fail.
        """
        behaviour = "store kinds are distinct namespaces with no shared index, per Contract G"
        require_surface(self, behaviour, "store_index", "validate_store_addressing")
        indexes = [SURFACE.store_index(kind) for kind in STORE_KINDS]
        self.assertEqual(len(set(indexes)), 3)
        for kind in STORE_KINDS:
            self.assertTrue(
                SURFACE.validate_store_addressing((kind,)),
                "a record addressed to this store kind alone does not validate in its own namespace: " + kind,
            )

    def test_record_addressed_across_two_stores_fails(self):
        """Fixture: one record addressed across two stores, derived from the store kind field the brief states.
        Pins: a record addressed across two stores fails validation, because the store kinds are distinct namespaces with no shared index.
        Bar: a record may not resolve in two namespaces at once.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, acceptance of the cross addressed record fails.
        """
        behaviour = "a record addressed across two stores fails validation"
        require_surface(self, behaviour, "validate_store_addressing")
        self.assertFalse(SURFACE.validate_store_addressing(("sweep", "pilot")))

    def test_pilot_artefact_resolving_in_sweep_namespace_fails(self):
        """Fixture: a pilot artefact addressed so that it would resolve inside a sweep namespace, and the reverse case, derived from the store kind field the brief states.
        Pins: a pilot artefact resolving inside a sweep namespace, or the reverse, fails validation.
        Bar: pilot artefacts stand stored apart from sweep results with no shared index, in the form Form 25 states.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, either cross resolution validating fails.
        """
        behaviour = "a pilot artefact resolving inside a sweep namespace, or the reverse, fails validation"
        require_surface(self, behaviour, "validate_store_addressing")
        self.assertFalse(SURFACE.validate_store_addressing(("pilot", "sweep")))
        self.assertFalse(SURFACE.validate_store_addressing(("sweep", "pilot")))


class TestReservedMatterBar(unittest.TestCase):
    def test_reserved_matter_value_in_family_record_fails(self):
        """Fixture: a minimally valid SweepFamilyRecord, derived from the brief field list at Shape 1, with one ordinary field set to a value drawn from the banked or reserved matter the surface states, and the same record with no such value standing as the control case.
        Pins: reserved and banked matter cannot be smuggled in as ordinary field values in a family record; the control case pins that the record validates without the reserved value, so rejection stands on the reserved matter bar and not on incompleteness.
        Bar: the banked items guard at plan section 2 section 8 item 3 applies to this record as to every suite artefact.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, a family record carrying such a value validating, or the control record failing to validate, fails.
        """
        behaviour = "reserved and banked matter cannot stand as an ordinary field value in a SweepFamilyRecord"
        require_surface(self, behaviour, "minimal_valid_instance", "required_fields", "reserved_matter_values", "validate_record")
        self.assertTrue(SURFACE.reserved_matter_values())
        control = SURFACE.minimal_valid_instance("1")
        self.assertTrue(SURFACE.validate_record("1", control))
        record = SURFACE.minimal_valid_instance("1")
        field = SURFACE.required_fields("1")[0]
        record[field] = SURFACE.reserved_matter_values()[0]
        self.assertFalse(SURFACE.validate_record("1", record))

    def test_reserved_matter_value_in_run_record_fails(self):
        """Fixture: a minimally valid RunRecord, derived from the brief field list at Shape 4, with one ordinary field set to a value drawn from the banked or reserved matter the surface states, and the same record with no such value standing as the control case; the RunRecord reserved matter group itself carries no such value in any field.
        Pins: reserved and banked matter cannot be smuggled in as ordinary field values in a run record, and the barred banked stake behaviour appears in no field value, per AC-6; the control case pins that the record validates without the reserved value, so rejection stands on the reserved matter bar and not on incompleteness.
        Bar: Parley Q3 behaviour appears in no field value, per AC-6 and the banked items guard at plan section 2 section 8 item 3; DQ-162 stands ruled as test value only and supplies no such behaviour.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.2; with the surface present, a run record carrying such a value validating, or the control record failing to validate, fails.
        """
        behaviour = "reserved and banked matter cannot stand as an ordinary field value in a RunRecord"
        require_surface(self, behaviour, "minimal_valid_instance", "required_fields", "reserved_matter_values", "validate_record")
        self.assertTrue(SURFACE.reserved_matter_values())
        control = SURFACE.minimal_valid_instance("4")
        self.assertTrue(SURFACE.validate_record("4", control))
        record = SURFACE.minimal_valid_instance("4")
        field = SURFACE.required_fields("4")[0]
        record[field] = SURFACE.reserved_matter_values()[0]
        self.assertFalse(SURFACE.validate_record("4", record))


if __name__ == "__main__":
    unittest.main()
