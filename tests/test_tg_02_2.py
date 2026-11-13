"""Test group TG-02.2. Domain and stream separation, at input form level.

Slice S-02, MOD-02 Seed and Stream Engine. Suite convention: this file tries
to import the product module for its slice, package crucible, module mod02,
and records whether the surface stands. While the surface stands absent, each
test fails with a message naming the pinned behaviour and its group.
This group pins the input form only. No behaviour in this group rests on the
recommended derivation mechanism, which stands unadopted at DQ7-02.
"""
import unittest

try:
    from crucible import mod02
    SURFACE = mod02
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-02.2"
DOMAINS = ("screening", "held out confirmation")


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


class TestDomainVocabularyClosure(unittest.TestCase):
    def test_domain_vocabulary_has_exactly_two_values(self):
        """Fixture: SeedDerivationInput values with domain screening and domain held out confirmation, derived from the closed two value vocabulary at Shape 5.
        Pins: the domain vocabulary has exactly two values, held apart, per Shape 5.
        Bar: the mapping states no bar on either stated value in its own position.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, a vocabulary of any other size fails.
        """
        behaviour = "the seed domain vocabulary has exactly two values, screening and held out confirmation, per Shape 5"
        require_surface(self, behaviour, "domain_vocabulary")
        self.assertEqual(tuple(SURFACE.domain_vocabulary()), DOMAINS)

    def test_invented_third_domain_fails(self):
        """Fixture: a SeedDerivationInput value carrying an invented third domain, derived from the vocabulary at Shape 5.
        Pins: a domain outside the two stated values fails validation at input form level.
        Bar: no third domain may enter by silence or by invention in a test fixture.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, acceptance of the invented domain fails.
        """
        behaviour = "a SeedDerivationInput with an invented third domain fails validation"
        require_surface(self, behaviour, "validate_domain")
        self.assertFalse(SURFACE.validate_domain("invented third domain"))

    def test_confirmation_seed_from_screening_domain_fails(self):
        """Fixture: F-18, the canonical scale and readout set, for the separation limb the mapping names: screening and held out confirmation seeds form separate families under that fixture.
        Pins: a derivation that draws a confirmation seed from the screening domain fails this group.
        Bar: screening and held out confirmation seeds form separate families, per fixture F-18 and the separation at Shape 5.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, such a derivation validating fails.
        """
        behaviour = "a derivation drawing a confirmation seed from the screening domain fails, per F-18 separation"
        require_surface(self, behaviour, "validate_derivation_domain_use")
        self.assertFalse(SURFACE.validate_derivation_domain_use(purpose="held out confirmation", seed_domain="screening"))
        self.assertTrue(SURFACE.validate_derivation_domain_use(purpose="held out confirmation", seed_domain="held out confirmation"))


class TestStreamCardinality(unittest.TestCase):
    def test_exactly_one_input_per_stream_class(self):
        """Fixture: a run StreamSet with one SeedDerivationInput value for each stream class in the set, derived from the handover rule at Shape 5 and operation C-13; the inventory the set is read against is the inventory the adoption record names, in the standing this group states.
        Pins: exactly one SeedDerivationInput value for each stream class in the run StreamSet, and no other count, per operation C-13.
        Bar: the eighteen class inventory at Shape 6 stands as a recommendation only; this test pins cardinality against the named inventory, not against a count stated here.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, a set at any other count per class validating fails.
        """
        behaviour = "exactly one SeedDerivationInput per stream class in the run StreamSet, per operation C-13"
        require_surface(self, behaviour, "validate_stream_cardinality")
        self.assertTrue(SURFACE.validate_stream_cardinality(counts={"class a": 1, "class b": 1}))

    def test_missing_derivation_input_fails(self):
        """Fixture: a run StreamSet with one derivation input missing for a stream class in the set, derived from operation C-13.
        Pins: a stream class with no derivation input fails the cardinality check.
        Bar: no missing input may be supplied by substitution, drawing, or assignment in completion order, in the form Shape 5 bars.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, such a set validating fails.
        """
        behaviour = "a run StreamSet missing a derivation input for a stream class fails the C-13 cardinality check"
        require_surface(self, behaviour, "validate_stream_cardinality")
        self.assertFalse(SURFACE.validate_stream_cardinality(counts={"class a": 1, "class b": 0}))

    def test_duplicate_derivation_input_fails(self):
        """Fixture: a run StreamSet with a duplicate derivation input for one stream class, derived from operation C-13.
        Pins: a stream class with two derivation inputs fails the cardinality check.
        Bar: the count is exactly one per class and no other count, per operation C-13.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, such a set validating fails.
        """
        behaviour = "a run StreamSet with a duplicate derivation input for a stream class fails the C-13 cardinality check"
        require_surface(self, behaviour, "validate_stream_cardinality")
        self.assertFalse(SURFACE.validate_stream_cardinality(counts={"class a": 2, "class b": 1}))

    def test_cardinality_pinned_to_named_inventory_not_to_eighteen(self):
        """Fixture: no inventory fixture; the basis is the standing of the Shape 6 inventory as a recommendation only, as plan section 3 Form 6 states it.
        Pins: tests pin cardinality against the inventory the adoption record names, not against the number eighteen as a settled fact.
        Bar: a test or suite statement presenting the eighteen class inventory as a settled fact fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, a cardinality check keyed to a fixed count of eighteen in place of the named inventory fails.
        """
        behaviour = "stream cardinality is pinned against the inventory the adoption record names, not against eighteen as a settled fact"
        require_surface(self, behaviour, "cardinality_basis")
        self.assertEqual(SURFACE.cardinality_basis(), "inventory named in the adoption record")


class TestStreamExhausted(unittest.TestCase):
    """Named failure STREAM-EXHAUSTED, folded from Amendment TG4-16."""

    def test_stream_exhausted_records_named_failure(self):
        """Fixture: a run in which a purpose stream is drawn past the position that stream carries during the run, derived from the stream state form at Shape 6; no inventory fixture is assigned to this test in the mapping.
        Pins: drawing past the position a purpose stream carries records the named failure STREAM-EXHAUSTED, naming the stream class identifier and the position reached; the run carries run status failed, its partial records are marked partial under the PD-06 form, and the run supports no witness, headline, screening, or confirmation claim.
        Bar: a run in that state supporting any of those claims fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, a past position draw returning no named failure, or a failed run of that form supporting a claim, fails.
        """
        behaviour = "drawing past a stream position records STREAM-EXHAUSTED, the run status failed, partial records marked, and no claim supported"
        require_surface(self, behaviour, "draw_from_stream")
        result = SURFACE.draw_from_stream(stream_class="class a", position=1, carried_positions=1)
        self.assertEqual(result["failure"], "STREAM-EXHAUSTED")
        self.assertEqual(result["run_status"], "failed")
        self.assertTrue(result["partial_records_marked"])
        self.assertFalse(result["supports_claim"])

    def test_stream_exhausted_recovery_is_fresh_run_only(self):
        """Fixture: a run that has recorded STREAM-EXHAUSTED, on the basis stated for that failure in this group.
        Pins: recovery is a fresh run on a stream state sized for the run length fixed in the family record.
        Bar: recovery is never a silent refill, a wrap, or a draw from another stream class.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.2; with the surface present, any refill, wrap, or cross class draw offered as recovery fails.
        """
        behaviour = "STREAM-EXHAUSTED recovery is a fresh run only, never a silent refill, a wrap, or a draw from another stream class"
        require_surface(self, behaviour, "stream_recovery_forms")
        self.assertEqual(tuple(SURFACE.stream_recovery_forms()), ("fresh run",))


if __name__ == "__main__":
    unittest.main()
