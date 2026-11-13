"""Test group TG-02.1. The adoption gate.

Slice S-02, MOD-02 Seed and Stream Engine. Suite convention: this file tries
to import the product module for its slice, package crucible, module mod02,
and records whether the surface stands. While the surface stands absent, each
non gated test fails with a message naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Standing: the whole seed mechanic stands in recommended and unadopted form
while register question NQ-24 stands open, held as DQ7-02, open point OP-01.
No executable behaviour test in this file rests on the recommended form until
an adoption record stands.
"""
import unittest

try:
    from crucible import mod02
    SURFACE = mod02
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-02.1"
ADOPTION_GATE = (
    "gated on the DQ7-02 adoption record for NQ-24 and the NQ-60 seed items: "
    "no adoption record stands, DQ7-02 stands CARRIED OPEN in full"
)


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": pinned behaviour not built: " + behaviour
            + " (surface crucible.mod02 stands absent: " + repr(SURFACE_ERROR) + ")"
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": pinned behaviour not built: " + behaviour
                + " (surface crucible.mod02 lacks " + attr + ")"
            )


class TestAdoptionGate(unittest.TestCase):
    def test_unadopted_form_cannot_run(self):
        """Fixture: a family record whose derivation version names the recommended form with no adoption record behind it, derived from the input form at Shape 5; no inventory fixture is assigned to this group in the mapping.
        Pins: validation fails the family record, per Contract A, and no reportable run starts on the recommended form.
        Bar: a suite run that produces a reportable run on the recommended form fails this group, whatever its other results.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.1; with the surface present, such a family record validating, or a reportable run starting on it, fails.
        """
        behaviour = "a family record naming the recommended derivation form with no adoption record fails validation, per Contract A"
        require_surface(self, behaviour, "validate_family_derivation")
        self.assertFalse(SURFACE.validate_family_derivation(version="recommended form", adoption_record=None))

    def test_adoption_record_binding_accepts_adopted_triple(self):
        """Fixture: an adoption record, when one stands, naming the derivation version, the stream inventory, and the generator it adopts. State: gated on that record.
        Pins: the engine accepts exactly the adopted triple.
        Bar: register entry E-22 is not read as adoptable form while the NQ-60 seed items stand open; a test citing that entry as the adoption fails this group.
        Failure: gated form only; this test never passes while no adoption record stands.
        """
        self.skipTest(ADOPTION_GATE)

    def test_adoption_record_binding_rejects_other_version(self):
        """Fixture: an adoption record, when one stands, beside a run naming a derivation version other than the adopted one. State: gated on that record.
        Pins: the engine rejects a run naming any version other than the adopted triple.
        Bar: register entry E-22 is not read as adoptable form while the NQ-60 seed items stand open.
        Failure: gated form only; this test never passes while no adoption record stands.
        """
        self.skipTest(ADOPTION_GATE)


class TestArithmeticDerivationNegativeFixture(unittest.TestCase):
    """Negative fixture folded from Amendment G1-C13, cluster R1-028."""

    def test_derivation_by_arithmetic_on_root_seed_fails(self):
        """Fixture: a family record whose adoption text derives a stream seed by arithmetic on a root seed, in the negative fixture form Amendment G1-C13 states; no inventory fixture is assigned to this test in the mapping.
        Pins: validation of that family record fails, on the ground stated at paper R-01 claim E8, and the record supplies no run, no replicate, and no battery input.
        Bar: a validation record that passes such a family record fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.1; with the surface present, such a family record validating fails.
        """
        behaviour = "a family record deriving stream seeds by arithmetic on a root seed fails validation, per Amendment G1-C13"
        require_surface(self, behaviour, "validate_family_derivation_text")
        self.assertFalse(SURFACE.validate_family_derivation_text("derive by arithmetic on a root seed"))

    def test_derivation_by_small_increment_on_root_seed_fails(self):
        """Fixture: a family record whose adoption text derives a stream seed by a small increment on a root seed, in the negative fixture form Amendment G1-C13 states.
        Pins: validation of that family record fails, on the ground stated at paper R-01 claim E8, and the record supplies no run, no replicate, and no battery input.
        Bar: a validation record that passes such a family record fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.1; with the surface present, such a family record validating fails.
        """
        behaviour = "a family record deriving stream seeds by a small increment on a root seed fails validation, per Amendment G1-C13"
        require_surface(self, behaviour, "validate_family_derivation_text")
        self.assertFalse(SURFACE.validate_family_derivation_text("derive by a small increment on a root seed"))

    def test_derivation_by_random_start_in_shared_sequence_fails(self):
        """Fixture: a family record whose adoption text derives a stream seed by a random starting point in a shared sequence, in the negative fixture form Amendment G1-C13 states.
        Pins: validation of that family record fails, on the ground stated at paper R-01 claim E8, and the record supplies no run, no replicate, and no battery input.
        Bar: a validation record that passes such a family record fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.1; with the surface present, such a family record validating fails.
        """
        behaviour = "a family record deriving stream seeds by a random starting point in a shared sequence fails validation, per Amendment G1-C13"
        require_surface(self, behaviour, "validate_family_derivation_text")
        self.assertFalse(SURFACE.validate_family_derivation_text("derive by a random starting point in a shared sequence"))


if __name__ == "__main__":
    unittest.main()
