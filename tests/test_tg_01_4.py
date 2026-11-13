"""Test group TG-01.4. Failure representation and canonical forms.

Slice S-01, MOD-01 Types and validation. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod01, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
The named failure forms are the forms the plan names for open point OP-23, as
carried at Form 4 items 2, 2A, and 2B in plan section 3. The canonical form
limb stands under open point OP-24 in the scope the mapping states.
"""
import unittest

try:
    from crucible import mod01
    SURFACE = mod01
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-01.4"


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


class TestNamedFailureRepresentation(unittest.TestCase):
    def test_failure_is_a_named_value(self):
        """Fixture: a failed run under Contract A in each named failure form the plan names for open point OP-23, derived from the failure forms at Form 4 items 2, 2A, and 2B; no inventory fixture is assigned to this group in the mapping.
        Pins: a failure is a value with a name, never a partial record presented as complete, and the run status field reads failed with the named failure stated where the failure ends the run.
        Bar: the mapping states no bar on a named failure value carried in this form.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.4; with the surface present, a failure returned with no name fails.
        """
        behaviour = "a failure under Contract A is a value with a name, per open point OP-23"
        require_surface(self, behaviour, "named_failure_forms", "failure_value")
        forms = tuple(SURFACE.named_failure_forms())
        self.assertTrue(forms)
        for form in forms:
            value = SURFACE.failure_value(form)
            self.assertTrue(value["name"])

    def test_partial_records_of_failed_run_are_marked(self):
        """Fixture: partial records of a failed run under Contract A, derived from the failed run field rule at Form 4 item 2A.
        Pins: partial records of a failed run are marked so they can never be presented as complete, and a required field of a failed run record carries its value or the explicit none or unknown value the stage rule assigns it.
        Bar: no partial record is ever presented as a complete record, in the general rule plan section 3 section 7 states.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.4; with the surface present, an unmarked partial record of a failed run fails.
        """
        behaviour = "partial records of a failed run are marked so they can never be presented as complete"
        require_surface(self, behaviour, "partial_record_is_marked")
        self.assertTrue(SURFACE.partial_record_is_marked(run_status="failed", partial=True))

    def test_failed_run_record_does_not_validate_as_completed(self):
        """Fixture: a failed run record presented for validation as a completed run, derived from the run status field at Form 4 item 2.
        Pins: a failed run record does not validate as a completed run.
        Bar: a failed run record that validates as a completed run fails this group outright.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.4; with the surface present, such a record validating as completed fails.
        """
        behaviour = "a failed run record does not validate as a completed run"
        require_surface(self, behaviour, "validate_run_status")
        self.assertFalse(SURFACE.validate_run_status(record_status="failed", presented_as="completed"))


class TestCanonicalForms(unittest.TestCase):
    def test_seed_derivation_inputs_recorded_strings_only(self):
        """Fixture: the same logical seed derivation input rendered twice, including a parameter value rendered as a recorded string, derived from the field list at Shape 5.
        Pins: seed derivation inputs enter in recorded string form and never as binary float renderings, per Shape 5, and the same input renders in one canonical form in that stated scope.
        Bar: the rule for seed derivation inputs holds in that stated scope and extends to no other field by this test.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.4; with the surface present, a binary float rendering of a derivation input passing fails.
        """
        behaviour = "seed derivation inputs enter as recorded strings and never as binary float renderings, per Shape 5"
        require_surface(self, behaviour, "validate_derivation_input_rendering")
        self.assertTrue(SURFACE.validate_derivation_input_rendering("recorded string"))
        self.assertFalse(SURFACE.validate_derivation_input_rendering(binary_float=1.5))

    def test_canonical_form_only_where_plan_states_it(self):
        """Fixture: the same logical state rendered twice per hashed field, including proportions in Shape 14, reputation scores in Shape 7, and seed derivation inputs, derived from those shapes.
        Pins: a field enters the state hash in one canonical form only where a plan level record has stated that form for that field, per open point OP-24.
        Bar: no test claims a canonical form for a hashed field a plan level record has not stated one for.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.4; with the surface present, a field entering the hash in two forms, or in a form no record states, fails.
        """
        behaviour = "a hashed field enters the state hash in one canonical form only where a plan level record states that form, per OP-24"
        require_surface(self, behaviour, "canonical_form_for_field")
        for field in ("proportion", "reputation score", "seed derivation input"):
            form = SURFACE.canonical_form_for_field(field)
            if form is not None:
                self.assertTrue(form["stated_on_plan_level_record"])

    def test_no_byte_level_hash_equality_claimed_while_op24_open(self):
        """Fixture: a hash equality claim stated across two independent renderings of the same logical state, derived from the bar at open point OP-24.
        Pins: until the plan states a canonical form per hashed field, no byte level hash equality is claimed across independent renderings, and AC-1 tests at TG-14.1 pin the field list and the order only.
        Bar: a claim of byte level hash equality across independent renderings while OP-24 stands open fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.4; with the surface present, such a claim standing in a suite or run artefact fails.
        """
        behaviour = "no byte level hash equality claim stands across independent renderings while OP-24 stands open"
        require_surface(self, behaviour, "hash_equality_claim_permitted")
        self.assertFalse(SURFACE.hash_equality_claim_permitted(basis="independent renderings"))


if __name__ == "__main__":
    unittest.main()
