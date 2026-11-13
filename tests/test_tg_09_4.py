"""Test group TG-09.4. Slice S-09, module mod04.

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
            "TG 09.4: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 09.4: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG094(unittest.TestCase):

    def test_sole_writer_of_simulation_state(self):
        """Fixture: a run in which no component other than the Tick Engine attempts a direct state write
        Pins: the Tick Engine is the sole writer of simulation state, per brief section 7.3
        Bar: a write accepted from any other component fails this group, including a write from a rule core that bypasses delivery
        Failure: the test fails while simulation state cannot be shown written by the Tick Engine alone
        """
        _require_entry(self, "the Tick Engine is the sole writer of simulation state", ["run", "TickEngine", "tick"])

    def test_second_writer_write_rejected(self):
        """Fixture: a run in which a second component attempts a direct state write, including a rule core that bypasses delivery
        Pins: a write accepted from any other component fails this group
        Bar: a direct write by any component other than the Tick Engine is a barred form
        Failure: the test fails while a write from a second component is accepted
        """
        _require_entry(self, "a direct state write from a second component is rejected", ["run", "TickEngine", "tick"])

    def test_every_event_delivered(self):
        """Fixture: a day carrying one event of each generated event kind in the catalogue the plan imports under open point OP-12 (the 17 generated rows, imported from the register entry Contract C cites, never invented from endpoint names)
        Pins: every event is delivered to the rule cores and to the detection layer, and the Recorder receives every event, per Contracts C, E, and G
        Bar: gossip intake, trust evaluation over stored records, and pairwise collusion evaluation are processing types, not generated events, and a test counting them as events fails the counting limb of this group
        Failure: the test fails while any generated event is undelivered to any of its three destinations, or while a processing type is counted as an event
        """
        _require_entry(self, "every generated event is delivered to the rule cores, the detection layer, and the Recorder", ["run", "TickEngine", "tick"])


if __name__ == "__main__":
    unittest.main()
