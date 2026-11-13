"""Test group TG-16.1. Fixture inventory discharge.
Slice S-16, integration, fixtures, and the validation run class. No single module
stands for this slice; the Reporter surface that files the inventory, crucible.mod11,
is the suite convention surface named here. Suite form: design/steps/step-13-opening-record.md section 4.
While that surface does not stand, every non gated test in this file fails by name,
stating the pinned behaviour and its group, as plan section 2 rules 1 and 2 state.
The inventory in this group stands at 30 fixtures, F-01 to F-30: fixtures F-28, F-29,
and F-30 stand created and assigned to TG-04.6 by the fixture assignment act at
design/steps/step-13-tg046-fixture-assignment.md, whose section 5 states the inventory
at 30 fixtures for the suite record discharge.
"""
import unittest

try:
    import crucible.mod11 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod11 absent, pinned behaviour unmet: " + behaviour)


class TestTG161(unittest.TestCase):
    def test_per_fixture_integration_record(self):
        """
        Fixture: The full inventory, F-01 to F-30.
        Pins: The integration record states, per fixture, whether it ran, what it showed, and what it does not show, with F-01 and F-02 at the head of the filed inventory, an integration record line standing for each of F-28, F-29, and F-30, and no fixture value invented in this slice.
        Bar: A fixture with no integration record line has not been discharged, whatever the slice level records say. F-01 keeps its verdict stated in full and F-02 its tally only, and no test in this group merges the two or promotes any other fixture to a verdict the brief does not give.
        Failure: Fails while the integrated surface stands absent, naming TG-16.1 and this behaviour; a fixture with no integration record line fails this test when the surface stands.
        """
        require_surface(self, "TG-16.1", "per fixture integration record for F-01 to F-30, F-01 and F-02 at the head, stating whether it ran, what it showed, and what it does not show")
        import crucible.mod16 as surface
        inventory = surface.fixture_inventory()
        self.assertEqual(len(inventory), 30)
        self.assertEqual(inventory[0]["fixture"], "F-01")
        self.assertEqual(inventory[1]["fixture"], "F-02")
        self.assertEqual([line["fixture"] for line in inventory], ["F-%02d" % n for n in range(1, 31)])
        for line in inventory:
            self.assertIn("ran", line)
            self.assertTrue(line["showed"])
            self.assertTrue(line["does_not_show"])
            self.assertTrue(surface.validate_fixture_record(line))

    def test_no_invented_fixture_value_at_integration(self):
        """
        Fixture: The full inventory, F-01 to F-30, inspected at integration for any value the brief or the evidence register does not state.
        Pins: No fixture is recorded as run on a value the brief or the register does not state, and fixtures whose values live in the evidence register carry their provenance labels, author claim, estimated, derived, or self scored, attached.
        Bar: A fixture recorded as run on an invented value, or with a provenance label dropped, fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.1 and this behaviour; a fixture recorded as run on an invented value fails this test when the surface stands.
        """
        require_surface(self, "TG-16.1", "no fixture recorded as run on a value the brief or the evidence register does not state, provenance labels attached")
        import crucible.mod16 as surface
        for line in surface.fixture_inventory():
            self.assertIn("provenance", line)
            self.assertTrue(line["provenance"])
        invented = {"fixture": "F-99", "ran": True, "showed": "a value", "does_not_show": "nothing", "value_source": "invented in this slice"}
        self.assertFalse(surface.validate_fixture_record(invented))

    def test_integration_record_f28(self):
        """
        Fixture: F-28, the band boundary neighbourhood case, created and assigned to TG-04.6 by the fixture assignment act at design/steps/step-13-tg046-fixture-assignment.md section 2, and standing exercised at TG-04.6.
        Pins: The integration record states, for fixture F-28, whether it ran, what it showed, and what it does not show. The fixture carries its standing label from the assignment act section 2: the stated distances, and with them the size of the boundary neighbourhood, stand open, and the distances are fixed in the family record before runs. No distance and no neighbourhood size is invented in this slice.
        Bar: A fixture with no integration record line has not been discharged, whatever the slice level records say, and an integration record stating an invented distance or an invented neighbourhood size for F-28 fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.1 and this behaviour; a missing integration record line for F-28, or an invented value on its line, fails this test when the surface stands.
        """
        require_surface(self, "TG-16.1", "integration record line for F-28, the band boundary neighbourhood case, carrying its standing label, the stated distances and the neighbourhood size standing open and fixed in the family record before runs")
        import crucible.mod16 as surface
        line = surface.fixture_record("F-28")
        self.assertIn("standing label", line["showed"])
        self.assertIn("open", line["showed"])
        self.assertIn("family record", line["showed"])
        self.assertTrue(surface.validate_fixture_record(line))

    def test_integration_record_f29(self):
        """
        Fixture: F-29, the alternation against decay case, created and assigned to TG-04.6 by the fixture assignment act at design/steps/step-13-tg046-fixture-assignment.md section 3, and standing exercised at TG-04.6.
        Pins: The integration record states, for fixture F-29, whether it ran, what it showed, and what it does not show. The fixture carries its standing label from the assignment act section 3: the alternation period stands open, to be stated in the family record before runs. No period value, ring size, or phase length is invented in this slice.
        Bar: A fixture with no integration record line has not been discharged, whatever the slice level records say, and an integration record stating an invented alternation period for F-29 fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.1 and this behaviour; a missing integration record line for F-29, or an invented value on its line, fails this test when the surface stands.
        """
        require_surface(self, "TG-16.1", "integration record line for F-29, the alternation against decay case, carrying its standing label, the alternation period standing open and to be stated in the family record before runs")
        import crucible.mod16 as surface
        line = surface.fixture_record("F-29")
        self.assertIn("standing label", line["showed"])
        self.assertIn("alternation period stands open", line["showed"])
        self.assertIn("family record", line["showed"])
        self.assertTrue(surface.validate_fixture_record(line))

    def test_integration_record_f30(self):
        """
        Fixture: F-30, the one directional vouch feeding case, created and assigned to TG-04.6 by the fixture assignment act at design/steps/step-13-tg046-fixture-assignment.md section 4, and standing exercised at TG-04.6.
        Pins: The integration record states, for fixture F-30, whether it ran, what it showed, and what it does not show. The fixture carries no magnitude beyond its stated structure, per the assignment act section 4: one identity with a clean work record, holding one vouch edge given in one direction only, toward a mutually vouching component, with no vouch received in return. No stake value, score value, or component size is invented in this slice.
        Bar: A fixture with no integration record line has not been discharged, whatever the slice level records say, and an integration record stating an invented magnitude for F-30 fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.1 and this behaviour; a missing integration record line for F-30, or an invented magnitude on its line, fails this test when the surface stands.
        """
        require_surface(self, "TG-16.1", "integration record line for F-30, the one directional vouch feeding case, carrying no magnitude beyond its stated structure")
        import crucible.mod16 as surface
        line = surface.fixture_record("F-30")
        self.assertIn("no magnitude beyond", line["does_not_show"])
        self.assertTrue(surface.validate_fixture_record(line))


if __name__ == "__main__":
    unittest.main()
