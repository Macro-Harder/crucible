"""Contract test for operation C-13, plan section 2 section 5.

The test pins the check field of contract C-13 as plan section 9
states it. Surfaces crossed: MOD-02, via TG-02.1 to TG-02.3.
Contract C-13 stands carried on the DQ7-02 bar in full. Its behaviour
tests stand in gated form, recording the bar and the decision waited
on. Its gate limb, the Contract A validation check, stands live in
the bar form the mapping states: the test passes at Step 13 only by
showing that the barred claim cannot be made, here that no run may
start on the unadopted form.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod02 as _m_mod02
    SURFACES["mod02"] = True
except Exception:
    SURFACES["mod02"] = False


class TestContractC13(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-13: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_unadopted_form_cannot_run_bar_live(self):
        """
        Fixture: Shapes 5 and 6 input forms: a family record whose derivation version names the recommended form with no adoption record behind it
        Pins: the Contract A validation check: validation reads the family record derivation version and confirms an adoption record stands for the form it names; no adoption record, no run; the family record fails validation and no run in that family is reportable. This is the live gate limb of a contract barred in full
        Bar: the whole mechanic stands in recommended and unadopted form; entry E-22 is not read as adoptable form while the NQ-60 seed items stand open, and deciding DQ7-01 does not by itself release this bar
        Failure: a reportable run starting on the recommended form, or such a family record passing validation, fails this test; while the surface is absent the test fails naming this behaviour and C-13
        """
        self.require("family record naming an unadopted derivation form fails validation and supplies no run", "mod02")
        import crucible.mod02 as mod02
        self.assertFalse(mod02.validate_family_derivation(version="recommended form", adoption_record=None))
        standing = mod02.gate_standing()
        self.assertEqual(standing["gate"], "DQ7-02")
        self.assertIsNone(standing["adoption_record"])
        refusal = mod02.derive_seed({"derivation_version": "recommended form"})
        self.assertEqual(refusal["failure"], "DERIVATION-GATED")
        self.assertEqual(refusal["gate"], "DQ7-02")
        self.assertFalse(refusal["seed_drawn"])
        self.assertFalse(mod02.validate_family_derivation_text("derive by arithmetic on a root seed"))
        self.assertFalse(mod02.validate_family_derivation_text("a derivation text with no barred form"))
        gated = mod02.derivation_text_refusal("a derivation text with no barred form")
        self.assertEqual(gated["failure"], "DERIVATION-GATED")
        self.assertEqual(gated["gate"], "DQ7-02")
        self.assertFalse(gated["valid"])

    def test_same_inputs_same_seeds_gated(self):
        """
        Fixture: no behavioural fixture stands while the contract stands barred in full. Recorded state: gated, never passed
        Pins: when the gate opens: the same root seed reference and the same derivation inputs give the same derived seeds, every time, in every run, in every component, and a checkpoint generator state matches the state a rederivation and advance reaches
        Bar: contract C-13 stands carried on the DQ7-02 bar in full; no barred limb is rested on while the bar stands
        Failure: a determinism claim made while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the DQ7-02 adoption record for register question NQ-24 and the NQ-60 seed items, owned by the Manager, due before Step 18 opens and by the close of Step 17")

    def test_domain_separation_and_cardinality_gated(self):
        """
        Fixture: no behavioural fixture stands while the contract stands barred in full. Recorded state: gated, never passed
        Pins: when the gate opens: screening and held out confirmation domains held apart in the form the adoption record states, and exactly one SeedDerivationInput value for each stream class in the run StreamSet, and no other count
        Bar: contract C-13 stands carried on the DQ7-02 bar in full; the eighteen class inventory at Shape 6 stands as a recommendation only and no test pins cardinality against the number eighteen as a settled fact
        Failure: a domain separation or cardinality claim rested on the unadopted form fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the DQ7-02 adoption record for register question NQ-24 and the NQ-60 seed items, owned by the Manager, due before Step 18 opens and by the close of Step 17")


if __name__ == "__main__":
    unittest.main()
