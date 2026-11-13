"""Test group TG-02.3. Generator determinism battery, gated.

Slice S-02, MOD-02 Seed and Stream Engine. Suite convention: this file tries
to import the product module for its slice, package crucible, module mod02,
and records whether the surface stands. While the surface stands absent, each
non gated test fails with a message naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
The determinism test of this group stands gated on the DQ7-02 adoption
record. The joined input uniqueness test of this group is not gated on the
adoption it completes, as its own bar states.
"""
import unittest

try:
    from crucible import mod02
    SURFACE = mod02
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-02.3"


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


class TestDeterminismGated(unittest.TestCase):
    def test_same_inputs_same_derived_seeds(self):
        """Fixture: one root seed reference derived twice through the adopted mechanism, once the adoption stands. State: gated on the adoption record.
        Pins: two derivations from the same inputs give the same run seeds and the same stream states, per operation C-13.
        Bar: this test runs only after the adoption record stands; before that point its recorded state is gated, never passed, and the suite may not be cited as proving determinism of derivation.
        Failure: gated form only; this test never passes while the adoption record does not stand.
        """
        self.skipTest(
            "gated on the DQ7-02 adoption record: generator determinism battery runs only after the adoption record stands"
        )


class TestBatterySampleSize(unittest.TestCase):
    def test_battery_sample_size_stated_in_advance(self):
        """Fixture: the battery record for the generator tests, carrying its sample size stated in advance; the size itself stands open at open point OP-22, NQ-60 item 4, and no size value is stated in this test.
        Pins: the sample size stands stated in advance before the battery runs, owned by the design team at Step 10 with the test authors at Step 13, per open point OP-22.
        Bar: this test pins the presence and the advance standing of the size, and no magnitude, because no record states one.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, a battery record with no advance size stated fails.
        """
        behaviour = "the generator battery sample size stands stated in advance on the battery record, per OP-22"
        require_surface(self, behaviour, "battery_record_counts_as_run")
        self.assertTrue(SURFACE.battery_record_counts_as_run({"advance_sample_size_stated": True}))

    def test_battery_without_advance_size_does_not_count(self):
        """Fixture: a battery record for the generator tests with no sample size stated in advance on its record.
        Pins: a battery run with no advance size on its record does not count as run.
        Bar: a battery result counted as run on such a record fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, such a battery counting as run fails.
        """
        behaviour = "a generator battery run with no advance sample size on its record does not count as run"
        require_surface(self, behaviour, "battery_record_counts_as_run")
        self.assertFalse(SURFACE.battery_record_counts_as_run({"advance_sample_size_stated": False}))


class TestJoinedInputUniqueness(unittest.TestCase):
    """Folded from Amendment G1-C09, restated at Amendment R1-029.

    This test set is not gated on the adoption it completes.
    """

    def test_differing_field_produces_different_encoded_input(self):
        """Fixture: the candidate derivation function and encoding, as the adoption record will state them, tested on the candidate encoding before any adoption record stands; no inventory fixture is assigned to this test in the mapping.
        Pins: two derivation inputs that differ in any field produce different encoded inputs.
        Bar: no adoption record is complete under condition 1 of the DQ7-02 grounds unless the candidate encoding has passed this test and the adoption record cites the test result.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, two inputs differing in a field encoding to the same input fail.
        """
        behaviour = "two derivation inputs differing in any field produce different encoded inputs, per Amendment G1-C09"
        require_surface(self, behaviour, "encode_candidate_input")
        first = SURFACE.encode_candidate_input({"a": "one", "b": "two"})
        second = SURFACE.encode_candidate_input({"a": "one", "b": "changed"})
        self.assertNotEqual(first, second)

    def test_empty_value_boundary_case(self):
        """Fixture: the candidate derivation function and encoding, on field boundary cases with empty values, as Amendment G1-C09 names them.
        Pins: two derivation inputs that differ in any field produce different encoded inputs, shown over the empty value boundary cases the adoption record names.
        Bar: no adoption record is complete under condition 1 of the DQ7-02 grounds unless the candidate encoding has passed this test and the adoption record cites the test result.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, an empty value case colliding with a stated value case fails.
        """
        behaviour = "joined input uniqueness holds over empty value boundary cases, per Amendment G1-C09"
        require_surface(self, behaviour, "encode_candidate_input")
        first = SURFACE.encode_candidate_input({"a": "", "b": "two"})
        second = SURFACE.encode_candidate_input({"a": "one", "b": "two"})
        self.assertNotEqual(first, second)

    def test_separator_value_boundary_case(self):
        """Fixture: the candidate derivation function and encoding, on values containing a separator character the encoding uses, as Amendment G1-C09 names them. The separator character itself is read from the candidate encoding at run time and is not chosen in this test.
        Pins: two derivation inputs that differ in any field produce different encoded inputs, shown over values containing any separator character the encoding uses.
        Bar: no adoption record is complete under condition 1 of the DQ7-02 grounds unless the candidate encoding has passed this test and the adoption record cites the test result.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, a separator value case colliding across a field split fails.
        """
        behaviour = "joined input uniqueness holds over values containing a separator character the encoding uses, per Amendment G1-C09"
        require_surface(self, behaviour, "encode_candidate_input", "candidate_separator")
        sep = SURFACE.candidate_separator()
        first = SURFACE.encode_candidate_input({"a": "x" + sep + "y", "b": "z"})
        second = SURFACE.encode_candidate_input({"a": "x", "b": "y" + sep + "z"})
        self.assertNotEqual(first, second)

    def test_coinciding_concatenation_boundary_case(self):
        """Fixture: the candidate derivation function and encoding, on values whose concatenation coincides across different field splits, as Amendment G1-C09 names them.
        Pins: two derivation inputs that differ in any field produce different encoded inputs, shown over the coinciding concatenation cases.
        Bar: no adoption record is complete under condition 1 of the DQ7-02 grounds unless the candidate encoding has passed this test and the adoption record cites the test result; a suite summary that reports the determinism test of this group as covering input uniqueness fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, two inputs whose concatenations coincide across different splits encoding alike fails.
        """
        behaviour = "joined input uniqueness holds where concatenations coincide across different field splits, per Amendment G1-C09"
        require_surface(self, behaviour, "encode_candidate_input")
        first = SURFACE.encode_candidate_input({"a": "ab", "b": "c"})
        second = SURFACE.encode_candidate_input({"a": "a", "b": "bc"})
        self.assertNotEqual(first, second)


class TestInterStreamElement(unittest.TestCase):
    """Battery record rule folded from Amendment G1-C12."""

    def test_battery_record_states_inter_stream_element(self):
        """Fixture: the battery record for the candidate battery, in the form Amendment G1-C12 states; no inventory fixture is assigned to this test in the mapping.
        Pins: the battery record states, beside the single stream results for each test family, the result of the inter stream element for that family, namely the interleaved or pairwise stream comparison result over the streams the verdict rests on, recorded before any second level verdict for that family is read.
        Bar: streams whose mutual independence stands not shown by that element supply no verdict, in either direction.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, a battery record lacking the inter stream element result for a family fails.
        """
        behaviour = "the battery record states the inter stream element result beside the single stream results for each family, per Amendment G1-C12"
        require_surface(self, behaviour, "validate_battery_record")
        record = {"single_stream_results": {"family a": "stated"}, "inter_stream_element": {"family a": "stated"}}
        self.assertTrue(SURFACE.validate_battery_record(record))
        incomplete = {"single_stream_results": {"family a": "stated"}, "inter_stream_element": {}}
        self.assertFalse(SURFACE.validate_battery_record(incomplete))

    def test_verdict_before_inter_stream_element_is_gated(self):
        """Fixture: a battery verdict recorded before the inter stream element result for its family stands recorded, in the form Amendment G1-C12 states.
        Pins: such a verdict is recorded as gated, never as passed, and no report may cite such a verdict as a battery result.
        Bar: a report citing such a verdict as a battery result fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, such a verdict recorded as passed fails.
        """
        behaviour = "a battery verdict recorded before its inter stream element result is recorded as gated, never as passed, per Amendment G1-C12"
        require_surface(self, behaviour, "battery_verdict_state")
        state = SURFACE.battery_verdict_state(inter_stream_element_recorded=False, verdict_recorded=True)
        self.assertEqual(state, "gated")


class TestBatteryResultForms(unittest.TestCase):
    """Result forms folded from Amendment TG4-14."""

    def test_battery_result_is_passed_failed_or_gated(self):
        """Fixture: a generator battery result in every state after its gate opens as well as before it, in the form Amendment TG4-14 states.
        Pins: a generator battery result stands as one of passed, failed, or gated, in every state.
        Bar: a battery result recorded in any other state fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, a result in a fourth state fails.
        """
        behaviour = "a generator battery result stands as one of passed, failed, or gated, per Amendment TG4-14"
        require_surface(self, behaviour, "battery_result_states")
        self.assertEqual(tuple(SURFACE.battery_result_states()), ("passed", "failed", "gated"))

    def test_failed_battery_writes_failure_record(self):
        """Fixture: a failed generator battery, in the form Amendment TG4-14 states; the two differing outputs are named by reference only, and no output value is stated in this test.
        Pins: a failed battery writes a battery failure record naming the derivation input set, the advance sample size, the first mismatching stream class, and the two differing outputs by reference.
        Bar: a failed battery with no such record, or with a record missing a named part, fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, a failed battery writing no complete failure record fails.
        """
        behaviour = "a failed battery writes a failure record naming the input set, the advance size, the first mismatching class, and the two outputs by reference, per TG4-14"
        require_surface(self, behaviour, "battery_failure_record_fields")
        fields = tuple(SURFACE.battery_failure_record_fields())
        for named in ("derivation input set", "advance sample size", "first mismatching stream class", "two differing outputs by reference"):
            self.assertIn(named, fields)

    def test_failed_battery_voids_determinism_and_bars_runs(self):
        """Fixture: a failed generator battery for one derivation version, in the form Amendment TG4-14 states.
        Pins: a failed battery voids every determinism statement for that derivation version and bars its runs from reportable use until a corrected version passes a fresh battery.
        Bar: a determinism statement or a reportable run standing for a version whose battery failed, before a corrected version passes, fails this group. This test settles no sample size and adopts no derivation form, and no part of NQ-60 item 4 is settled by it.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.3; with the surface present, such a statement or run standing fails.
        """
        behaviour = "a failed battery voids determinism statements for its version and bars its runs until a corrected version passes a fresh battery, per TG4-14"
        require_surface(self, behaviour, "determinism_statement_permitted")
        self.assertFalse(SURFACE.determinism_statement_permitted(battery_state="failed", corrected_battery_passed=False))


if __name__ == "__main__":
    unittest.main()
