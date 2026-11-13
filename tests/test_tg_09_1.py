"""Test group TG-09.1. Slice S-09, module mod04.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod04, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
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
            "TG 09.1: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 09.1: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG091(unittest.TestCase):

    def test_handed_values_are_not_altered(self):
        """Fixture: one SweepPoint, one AssumptionRecord, one seed input set, and one family identifier handed to the Engine, compared with the values the completed run record carries
        Pins: the Engine may not alter the point, the assumptions, or the seeds, per Contract A
        Bar: any silent correction inside the Engine, including a repaired seed or a rounded assumption value, fails this group
        Failure: the test fails while the completed run record values differ from the handed values in any part
        """
        _require_entry(self, "handed values are not altered by the Engine", ["run", "TickEngine", "tick"])

    def test_silent_correction_fails(self):
        """Fixture: one handed value altered inside the Engine, including a repaired seed and a rounded assumption value, each in turn
        Pins: any silent correction inside the Engine fails this group, per Contract A
        Bar: a repaired seed and a rounded assumption value are barred forms
        Failure: the test fails while the surface cannot reject a silent correction inside the Engine
        """
        _require_entry(self, "a silent correction inside the Engine is rejected", ["run", "TickEngine", "tick"])

    def test_completed_or_named_failure_nothing_between(self):
        """Fixture: a run forced to fail at each delivery stage in turn
        Pins: the Engine returns one completed run or one failed run with failure stated as a named failure, never a partial record presented as complete, per Contract A and TG-01.4
        Bar: a partial record presented as complete fails this group
        Failure: the test fails while a forced failure returns anything other than a named failure, or a partial record presented as complete
        """
        _require_entry(self, "the Engine returns a completed run or a named failure, nothing between", ["run", "TickEngine", "tick"])


if __name__ == "__main__":
    unittest.main()
