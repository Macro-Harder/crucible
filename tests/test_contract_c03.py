"""Contract test for operation C-03, plan section 2 section 5.

The test pins the check field of contract C-03 as plan section 9
states it. Surfaces crossed: MOD-13, via TG-14.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-03.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod13 as _m_mod13
    SURFACES["mod13"] = True
except Exception:
    SURFACES["mod13"] = False


class TestContractC03(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-03: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_replay_identity_over_run_fact_fields(self):
        """
        Fixture: the AC-1 field list: an original run and its replay on the same scenario, the same seed set and the same code version
        Pins: the two produce an identical headline unit over the run fact fields of that unit and agreement field for field over the AC-1 field list in its stated order, with Form 16 fields 1 and 10 outside the identity; or the non deterministic marking and its use bars follow
        Bar: no completeness is claimed over the detection state, which stands excluded from the hash list; summary record fields written after close under C-08 stand outside the replayed state
        Failure: a different headline unit on the run fact fields that stands unmarked, or a marked run used as a witness, headline or confirmation run, fails this test; while the surface is absent the test fails naming this behaviour and C-03
        """
        self.require("replay agrees field for field over the AC-1 list or the run is marked non deterministic and barred", "mod13")
        import crucible.mod01 as mod01
        import crucible.mod13 as surface
        fields = list(mod01.state_hash_field_list())
        facts = {field: "value for " + field for field in fields}
        facts["headline_unit"] = {"unit": "unit-1"}
        check = surface.replay_check(facts, dict(facts))
        self.assertTrue(check["deterministic"])
        self.assertTrue(check["identical_headline_unit"])
        changed_unit = dict(facts)
        changed_unit["headline_unit"] = {"unit": "unit-2"}
        marked = surface.replay_check(facts, changed_unit)
        self.assertTrue(marked["marked_non_deterministic"])
        for use in ("witness", "headline support", "confirmation support"):
            self.assertFalse(surface.use_stands_for_marked_run(use))
        self.assertFalse(check["detection_state_completeness_claimed"])

    def test_field_list_and_order_pinned_only(self):
        """
        Fixture: the AC-1 field list in its stated order, as the check field states it while OP-24 stands open
        Pins: the check claims the field list and its order only; a hashed score value that is a NaN, an infinite value or a subnormal binary64 value gives the named failure HASH-VALUE-BARRED: the run carries run status failed, no state hash is stated, and the run is barred from witness, headline and confirmation use
        Bar: while OP-24 stands open no check, witness bar or replay verdict rests on a computed hash equality, and AC-1 stands unimplementable in its state hash limb
        Failure: a verdict resting on a computed hash equality, or a barred hashed value carried without the named failure, fails this test; while the surface is absent the test fails naming this behaviour and C-03
        """
        self.require("AC-1 check pins the field list and its order, with HASH-VALUE-BARRED for barred hashed values", "mod13")
        import crucible.mod01 as mod01
        import crucible.mod13 as surface
        fields = list(mod01.state_hash_field_list())
        pinned = surface.ac1_check({field: "value" for field in fields})
        self.assertEqual(pinned["field_list"], fields)
        self.assertEqual(pinned["order"], fields)
        self.assertEqual(pinned["pins"], "field list and order only")
        self.assertFalse(pinned["hash_equality_claimed"])
        barred = surface.ac1_check({fields[0]: float("nan"), fields[1]: float("inf")})
        self.assertEqual(barred["values"][fields[0]], "HASH-VALUE-BARRED")
        self.assertEqual(barred["values"][fields[1]], "HASH-VALUE-BARRED")
        self.assertFalse(surface.validate_replay_claim({"hash_equality_claimed": True}))
        self.assertTrue(surface.validate_replay_claim({"hash_equality_claimed": False}))

    def test_hash_equality_claim_gated(self):
        """
        Fixture: no fixture stands for the hash equality limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: hash equality over the AC-1 field list under a canonical form per hashed field and a named hash function
        Bar: OP-24 bar carried in words: until a canonical form per hashed field and a named hash function stand on a plan level record, no hash equality claim stands; the detection exclusion stands as the recorded Candidate B form only, carried open for reliance until the reconciliation act stands
        Failure: a hash equality claim made while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: a canonical form per hashed field and a named hash function on a plan level record under OP-24")


if __name__ == "__main__":
    unittest.main()
