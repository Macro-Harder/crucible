"""Test group TG-02.5. Open limbs carried as non claims.

Slice S-02, MOD-02 Seed and Stream Engine. Suite convention: this file tries
to import the product module for its slice, package crucible, module mod02,
and records whether the surface stands. While the surface stands absent, each
test fails with a message naming the pinned behaviour and its group.
The open limbs are NQ-60 items 5, 6, and 7, at open point OP-22.
"""
import unittest

try:
    from crucible import mod02
    SURFACE = mod02
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-02.5"


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


class TestNoSecrecyProperty(unittest.TestCase):
    def test_no_secrecy_property_claimed(self):
        """Fixture: any suite or run wording claiming a seed secrecy property; the scan set is the wording set the surface reports for the suite and its runs, and no wording value is invented in this test.
        Pins: no secrecy property is claimed while NQ-60 item 6 stands open, per open point OP-22.
        Bar: wording, not mechanism; a claim in a comment, a fixture label, or a report line fails this group equally.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.5; with the surface present, any wording in the scan set claiming a seed secrecy property fails.
        """
        behaviour = "no seed secrecy property is claimed in any suite or run wording while NQ-60 item 6 stands open, per OP-22"
        require_surface(self, behaviour, "wording_claims_secrecy_property")
        self.assertFalse(SURFACE.wording_claims_secrecy_property(scope="suite and run wording"))


class TestOpenLimbsCarriedOpen(unittest.TestCase):
    def test_substream_and_resampling_named_settled_fails(self):
        """Fixture: a run record naming a substream extension rule or an analysis resampling method as settled, derived from the run record form at Shape 4.
        Pins: both stand open, NQ-60 items 5 and 7, and a run record naming either as settled fails validation on that limb.
        Bar: the D-05 duty that names no resampling method is not filled by a test.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.5; with the surface present, such a run record validating fails.
        """
        behaviour = "substream extension and analysis resampling stand open at NQ-60 items 5 and 7 and may not be named as settled in a run record"
        require_surface(self, behaviour, "validate_open_limb_standing")
        self.assertFalse(SURFACE.validate_open_limb_standing("substream extension", named_as="settled"))
        self.assertFalse(SURFACE.validate_open_limb_standing("analysis resampling", named_as="settled"))
        self.assertTrue(SURFACE.validate_open_limb_standing("substream extension", named_as="open"))

    def test_no_test_fixes_substream_or_resampling_form(self):
        """Fixture: no inventory fixture; the basis is the bar this group states on its own tests, read over the suite source the surface reports.
        Pins: no test in the suite fixes the substream extension limb or the resampling limb by choosing a form for either.
        Bar: a test that fixes either by choosing a form fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.5; with the surface present, a suite test choosing a form for either limb standing in the suite fails.
        """
        behaviour = "no suite test fixes the substream extension rule or the resampling method by choosing a form"
        require_surface(self, behaviour, "suite_fixes_open_limb")
        self.assertFalse(SURFACE.suite_fixes_open_limb("substream extension"))
        self.assertFalse(SURFACE.suite_fixes_open_limb("analysis resampling"))


if __name__ == "__main__":
    unittest.main()
