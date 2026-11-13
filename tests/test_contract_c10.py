"""Contract test for operation C-10, plan section 2 section 5.

The test pins the check field of contract C-10 as plan section 9
states it. Surfaces crossed: MOD-01 and MOD-12, via TG-01.3 and TG-12.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-10.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod01 as _m_mod01
    SURFACES["mod01"] = True
except Exception:
    SURFACES["mod01"] = False
try:
    import crucible.mod12 as _m_mod12
    SURFACES["mod12"] = True
except Exception:
    SURFACES["mod12"] = False


class TestContractC10(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-10: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_seal_match_check(self):
        """
        Fixture: Shape 1 seal passage: a sealed family manifest and run records carrying matching family version and manifest hash values
        Pins: validation compares the version and hash in every run record against the sealed manifest and passes only on a match; the sealed family does not change under the runs recorded from it
        Bar: no divergence is tolerated: a mismatched run record is a failed record at the moment of reading, not a divergent copy to be reconciled later
        Failure: a mismatched record that validates, or a sealed family changed under its runs, fails this test; while a crossed surface is absent the test fails naming this behaviour and C-10
        """
        self.require("run record version and hash match the sealed family manifest", "mod01", "mod12")
        import crucible.mod01 as mod01
        import crucible.mod12 as mod12
        manifest = {"family_version": "v1", "manifest_hash": "hash-1"}
        self.assertTrue(mod01.validate_family_seal_match(manifest, {"family_version": "v1", "manifest_hash": "hash-1"}))
        self.assertFalse(mod01.validate_family_seal_match(manifest, {"family_version": "v1", "manifest_hash": "hash-9"}))
        family = mod12.make_family_record(family_id="fam-c10")
        sealed = mod12.seal_family_record(family)
        self.assertTrue(sealed["sealed"])
        self.assertEqual(sealed["family_id"], "fam-c10")

    def test_edit_creates_a_new_family_identifier(self):
        """
        Fixture: Shape 1 seal passage: a family record edited after sealing
        Pins: any edit to a sealed family record creates a new family identifier and runs under the new identifier start again; a claimed edit under a sealed identifier, with no new identifier issued, fails the seal check
        Bar: change is by new identifier only; no edit path exists under a sealed identifier
        Failure: an edit standing under the sealed identifier, or runs continuing under it after an edit, fails this test; while a crossed surface is absent the test fails naming this behaviour and C-10
        """
        self.require("edit to a sealed family creates a new family identifier and runs start again", "mod01", "mod12")
        import crucible.mod12 as mod12
        sealed = mod12.seal_family_record(mod12.make_family_record(family_id="fam-c10"))
        edited = mod12.apply_family_edit(sealed, change={"field": "value"})
        self.assertNotEqual(edited["family_id"], "fam-c10")
        self.assertEqual(edited["runs_under"], edited["family_id"])
        reused = {"family_id": "fam-c10", "sealed": True, "edited_after_seal": True, "identifier_changed": False}
        self.assertFalse(mod12.validate_family_record(reused))


if __name__ == "__main__":
    unittest.main()
