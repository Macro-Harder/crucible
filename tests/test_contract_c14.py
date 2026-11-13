"""Contract test for operation C-14, plan section 2 section 5.

The test pins the check field of contract C-14 as plan section 9
states it. Surfaces crossed: MOD-04, via TG-09.2.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-14.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod04 as _m_mod04
    SURFACES["mod04"] = True
except Exception:
    SURFACES["mod04"] = False


class TestContractC14(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-14: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_one_fixed_order_per_family_stated_in_record(self):
        """
        Fixture: Contract C and Shape 1 identifier: two runs of the same point under one family record
        Pins: one fixed order per family, stated in the record: all events inside one simulated day, in every run of the family, are applied in the order named in the family record, and neither run holds an order of its own; the order a run used stands in its record
        Bar: the order itself stands unfixed on the record, at the scheduling order position carried at contract C-14 and open point OP-08, gap G-7; tests pin carriage and the bar, not a chosen order
        Failure: runs of one family reaching different end of day states by order, or a run record stating no order, fails this test; while the surface is absent the test fails naming this behaviour and C-14
        """
        self.require("one fixed scheduling order per family, stated in every run record", "mod04")
        import crucible.mod04 as mod04
        family = mod04.scheduling_order_record("fam-c14", "order-1")
        self.assertEqual(family["scheduling_order_identifier"], "order-1")
        self.assertTrue(family["fixed_per_family"])
        first = mod04.run_record_with_order({"run_id": "run-1", "run_class": "screening"}, family["scheduling_order_identifier"])
        second = mod04.run_record_with_order({"run_id": "run-2", "run_class": "screening"}, family["scheduling_order_identifier"])
        self.assertEqual(first["scheduling_order_identifier"], second["scheduling_order_identifier"])
        self.assertTrue(mod04.validate_run_scheduling_order(first))
        self.assertFalse(mod04.validate_run_scheduling_order({"run_id": "run-3", "run_class": "screening"}))

    def test_prototype_order_bars_headline_use(self):
        """
        Fixture: Contract C and Shape 1 identifier: a headline run whose scheduling order identifier is absent, or reads prototype order
        Pins: validation fails the run and it is not reportable; the same failure applies to any run presented for a headline claim, and to a run under an identifier no family record states
        Bar: any ordering used in a prototype or pilot artefact supports no headline claim
        Failure: such a run that validates or supports a headline claim fails this test; while the surface is absent the test fails naming this behaviour and C-14
        """
        self.require("headline run with an absent or prototype scheduling order identifier fails validation", "mod04")
        import crucible.mod04 as mod04
        prototype = {"run_id": "run-h", "run_class": "headline", "scheduling_order_identifier": "prototype"}
        self.assertFalse(mod04.validate_run_scheduling_order(prototype))
        self.assertFalse(mod04.headline_order_stands(prototype))
        absent = {"run_id": "run-h", "run_class": "headline"}
        self.assertFalse(mod04.validate_run_scheduling_order(absent))
        stated = {"run_id": "run-h", "run_class": "headline", "scheduling_order_identifier": "order-1"}
        self.assertTrue(mod04.validate_run_scheduling_order(stated))
        self.assertTrue(mod04.headline_order_stands(stated))


if __name__ == "__main__":
    unittest.main()
