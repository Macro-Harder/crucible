"""Test group TG-06.3, slice S-06, MOD-07 Escrow Adapter.

Suite form: Python standard library unittest, one file per test group.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each test body first requires the product surface: while the surface
is absent the test fails, naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only. No real money stake
behaviour stands in any fixture, branch or variable in this file.
"""
import unittest

try:
    from crucible import mod07 as _mod
    SURFACE = True
    SURFACE_ERROR = ""
except Exception as exc:
    _mod = None
    SURFACE = False
    SURFACE_ERROR = str(exc)


class TestTG063(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-06.3: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_interim_reporting_rule(self):
        """
        Fixture: a joint run producing a vouch lien amount, a vouch release and a slash outcome
        Pins: every such effect is reported as computed in Parley and not settled in the chosen escrow, while NQ-45 stands open, and the lien state for a cross seam effect never reads settled or released in a validated record, as TG-01.2 also pins
        Bar: wording drift from computed toward settled, in any artefact, fails this group; the 21 seam gaps, creation 7, release 6, slash execution 8, are the standing reason, and no test narrows them by choosing a reading
        Failure: an effect reported as settled or released across the seam, in any wording, fails this test; while the surface is absent the test fails naming this behaviour and TG-06.3
        """
        self.require_surface("every cross seam effect reports as computed in Parley and not settled in the chosen escrow")
        for kind in ("vouch lien amount", "vouch release", "slash outcome"):
            report = _mod.seam_effect_report({"kind": kind, "value": 1})
            self.assertEqual(
                report["reporting"],
                "computed in Parley and not settled in the chosen escrow")
            self.assertEqual(report["lien_state"], "computed not settled")
            self.assertTrue(_mod.validate_seam_wording(report["reporting"]))
        self.assertEqual(_mod.seam_gap_counts(),
                         {"creation": 7, "release": 6, "slash execution": 8})

    def test_settled_wording_for_seam_effect_fails(self):
        """
        Fixture: a joint run record carrying settled or released as the lien state of a cross seam effect
        Pins: validation fails the record while NQ-45 stands open
        Bar: the lien state field holds four values only, and settled and released are barred for cross seam effects while NQ-45 stands open, per contract C-20
        Failure: such a record that validates fails this test; while the surface is absent the test fails naming this behaviour and TG-06.3
        """
        self.require_surface("record with settled or released lien state across the seam fails validation")
        lien_values = _mod.mod01.LIEN_STATES
        for state in (lien_values[2], lien_values[3]):
            effect = {"kind": "vouch lien amount", "lien_state": state}
            self.assertFalse(_mod.validate_cross_seam_effect(effect))
        computed = {"kind": "vouch lien amount",
                    "lien_state": "computed not settled"}
        self.assertTrue(_mod.validate_cross_seam_effect(computed))
        self.assertFalse(_mod.validate_seam_wording(
            "the vouch lien stands settled as an escrow outcome"))
        self.assertFalse(_mod.validate_seam_wording(
            "the vouch release was released at the seam"))

    def test_slash_remainder_non_claim(self):
        """
        Fixture: a slash outcome inspected for its remainder destination
        Pins: the chosen escrow core has no cost pool account on either wording of contested entry C-12, and no result names a remainder destination as settled
        Bar: both standings of C-12 travel with the fixture; a test resting on either standing alone fails this group
        Failure: a result naming a remainder destination as settled, or a case resting on one standing of C-12 alone, fails this test; while the surface is absent the test fails naming this behaviour and TG-06.3
        """
        self.require_surface("no slash remainder destination is named as settled and both standings of C-12 travel")
        report = _mod.slash_outcome_report({"value": 1})
        self.assertIsNone(report["remainder_destination"])
        self.assertFalse(report["remainder_named_as_settled"])
        self.assertFalse(report["cost_pool_account_named_as_settled"])
        self.assertEqual(tuple(report["c12_standings_carried"]),
                         _mod.C12_STANDINGS)
        self.assertEqual(len(report["c12_standings_carried"]), 2)
        self.assertTrue(_mod.validate_slash_report(report))
        settled = dict(report, remainder_destination="cost pool",
                       remainder_named_as_settled=True)
        self.assertFalse(_mod.validate_slash_report(settled))
        one_standing = dict(report,
                            c12_standings_carried=[_mod.C12_STANDINGS[0]])
        self.assertFalse(_mod.validate_slash_report(one_standing))

    def test_folding_recorded_before_ruling_effect_wording_at_adapter(self):
        """
        Fixture: F-12, the B-5 matched comparison pair, at the adapter limb
        Pins: every adapter choice in the joint run stands recorded against the ruling text it touches, ruling by ruling, and no B-5 difference resting on a seam effect from this slice is reported as a ruling effect until that recording stands
        Bar: a seam result reported as a ruling effect with no folding recording behind it fails this group, and the ten ruling text gaps G-1 to G-10 stand filled by no inference in the recording
        Failure: a seam result worded as a ruling effect with no folding recording, or a recording supplying a gap value by inference, fails this test; while the surface is absent the test fails naming this behaviour and TG-06.3
        """
        self.require_surface("adapter choices are folded against the ruling text before any ruling effect wording at the seam")
        choice = _mod.make_adapter_choice(
            "ch-5", "reading", "rule point", "governing text v1",
            "B-4 fold v1")
        difference = {"seam_choice_identifiers": ["ch-5"],
                      "rulings_claimed": ["DQ-1"]}
        self.assertFalse(
            _mod.ruling_effect_reporting_stands(difference, []))
        folding = _mod.record_folding(choice, ["DQ-1", "DQ-2"])
        self.assertTrue(_mod.validate_folding_record(folding))
        self.assertEqual(tuple(folding["gaps_carried_open"]),
                         _mod.RULING_TEXT_GAPS)
        self.assertTrue(
            _mod.ruling_effect_reporting_stands(difference, [folding]))
        inferred = dict(folding, gaps_filled_by_inference=["G-8"])
        self.assertFalse(_mod.validate_folding_record(inferred))
        self.assertFalse(
            _mod.ruling_effect_reporting_stands(difference, [inferred]))


if __name__ == "__main__":
    unittest.main()
