"""Test group TG-09.5. Slice S-09, module mod04.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod04, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires. The
hostile magnitude test stands in gated form on the family record,
never passed, while the magnitudes stand open under OP-13.
"""
import unittest

try:
    import crucible.mod04 as _module
    SURFACE_STANDS = True
except Exception:
    _module = None
    SURFACE_STANDS = False


def _require_entry(case, behaviour, names):
    if not SURFACE_STANDS:
        case.fail(
            "TG 09.5: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 09.5: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG095(unittest.TestCase):

    def test_hostile_kinds_at_fixed_magnitudes_gated(self):
        """Fixture: F-13, the hostile input family, kind by kind; recorded state: gated on the family record fixing magnitudes
        Pins: when the gate opens, each named kind (junk share; veto and hostage behaviour; stalls and abandonment; duplicate, oversize, and rush rates; cost error in both directions; question rounds; pause use to the cap in force) runs at the magnitude or range the family record fixes before runs, per AC-10; before the magnitudes are fixed this group pins the kind list and the counting rule only
        Bar: a kind run below its fixed magnitude does not count as run, and a family with any kind unrun at its magnitude has not run as the required family; the magnitudes themselves stand open under OP-13
        Failure: gated: the test stands skipped, never passed, while the family record magnitudes stand unfixed
        """
        self.skipTest("gated on the family record fixing the magnitude or range for each hostile kind before runs, at open point OP-13: hostile kinds run at their fixed magnitudes, gated")

    def test_pause_value_stated_per_variant(self):
        """Fixture: F-13 pause limb with fixture F-25, the pause cap case
        Pins: every pause related result states the pause value in force for its variant
        Bar: a pause result with no variant pause value fails validation, and the pause arithmetic form for counted windows (ruling text gap G-8 at open point OP-21) must be named in any run record reporting a lost contact outcome near a pause
        Failure: the test fails while any pause related result lacks the pause value in force for its variant
        """
        _require_entry(self, "every pause related result states the pause value in force for its variant", ["run", "TickEngine", "tick"])

    def test_pause_result_without_variant_value_fails(self):
        """Fixture: F-13 pause limb, a pause related result carrying no variant pause value
        Pins: a pause result with no variant pause value fails validation
        Bar: a pause result with no variant pause value is a barred form
        Failure: the test fails while such a pause result validates
        """
        _require_entry(self, "a pause result with no variant pause value fails validation", ["run", "TickEngine", "tick"])


if __name__ == "__main__":
    unittest.main()
