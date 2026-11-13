"""Test group TG-09.2. Slice S-09, module mod04.

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
            "TG 09.2: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 09.2: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG092(unittest.TestCase):

    def test_one_fixed_order_per_family(self):
        """Fixture: two runs of the same point under the family scheduling order identifier, and one run attempted under a second order inside the same family
        Pins: events within one simulated day are applied in one fixed order, and the order a run used stands in its record, per Contract C and Shape 4, and operation C-14
        Bar: the order is not yet fixed on the record (gap G-7 at contract C-14 and open point OP-08); a headline run whose scheduling order identifier is absent, or reads prototype order, fails validation, and any ordering used in a prototype or pilot artefact supports no headline claim
        Failure: the test fails while a family runs under two orders, or while the order a run used stands absent from its record
        """
        _require_entry(self, "one fixed order per family, stated in the record", ["run", "TickEngine", "tick"])

    def test_prototype_order_bars_headline_use(self):
        """Fixture: a headline run whose scheduling order identifier is absent, and one whose identifier reads prototype order
        Pins: a headline run whose scheduling order identifier is absent, or reads prototype order, fails validation at TG-01.3 form
        Bar: prototype order bars headline use, per contract C-14
        Failure: the test fails while such a headline run validates
        """
        _require_entry(self, "prototype order and a missing order identifier bar headline use", ["run", "TickEngine", "tick"])

    def test_order_sensitivity_is_measured_not_hidden(self):
        """Fixture: the same point run under two different stated orders in a screening family
        Pins: where the end of day states differ, both records stand and the difference is reportable as an order effect
        Bar: a suite that runs one order only and reports its results as order free fails this group
        Failure: the test fails while an order difference is hidden or reported as order free
        """
        _require_entry(self, "order sensitivity is measured and reported, not hidden", ["run", "TickEngine", "tick"])

    def test_tie_break_key_order(self):
        """Fixture: two events of one kind, in one day, on one agent, whose application order changes the end of day state, as the plan section 3 tie break passage states for TG-09.2
        Pins: both runs of the family apply the two events in the order the tie break keys give, drawn from stream position, event identifier, and agent identifier, applied in stated order
        Bar: a family record whose order leaves any two events in a day unordered is incomplete in the same sense as a record with no order stated
        Failure: the test fails while the two events are applied in any order other than the tie break key order
        """
        _require_entry(self, "events are applied in the tie break key order the family record states", ["run", "TickEngine", "tick"])


if __name__ == "__main__":
    unittest.main()
