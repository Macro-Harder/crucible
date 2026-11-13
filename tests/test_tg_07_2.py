"""Test group TG-07.2. Slice S-07, module mod08.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod08, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
"""
import unittest

try:
    import crucible.mod08 as _module
    SURFACE_STANDS = True
except Exception:
    _module = None
    SURFACE_STANDS = False


def _require_entry(case, behaviour, names):
    if not SURFACE_STANDS:
        case.fail(
            "TG 07.2: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 07.2: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG072(unittest.TestCase):

    def test_profile_set_self_consistency_figures(self):
        """Fixture: F-06, the recorded Vigil profile set (slow leak, drifter, prepositioner, and colluder, plus one honest profile, at at least 1,000 streams per profile); provenance label: self scored
        Pins: scoring over the set reproduces its carried figures in their carried form (false ACCUSED 0.0, false WATCH 0.129, false NOTICED 0.31), over the verdict ladder and features the fixture names, at record level only
        Bar: the figures are self scored and carried as self consistency figures only under decision D-13
        Failure: the test fails while scoring over F-06 does not reproduce the carried figures in their carried form
        """
        _require_entry(self, "F-06 self consistency figures reproduce at record level only", ["score_profiles", "score", "DetectionLayer"])
        surface = _module
        result = surface.score_profiles()
        self.assertEqual(
            result["figures"],
            {"false ACCUSED": 0.0, "false WATCH": 0.129,
             "false NOTICED": 0.31})
        self.assertEqual(
            tuple(result["profiles"]),
            ("slow leak", "drifter", "prepositioner", "colluder",
             "honest"))
        self.assertGreaterEqual(
            result["minimum_streams_per_profile"], 1000)
        self.assertEqual(result["provenance_label"], "self scored")
        self.assertTrue(result["record_level_only"])
        self.assertEqual(
            result["verdict_ladder"],
            ["UNOBSERVED", "NO-SIGNAL", "NOTICED", "WATCH",
             "ACCUSED"])

    def test_figures_not_presented_as_calibration(self):
        """Fixture: F-06, the recorded Vigil profile set; provenance label: self scored
        Pins: no test or report presents the F-06 figures as calibration, or as accuracy against the world
        Bar: a test or report presenting them as calibration, or as accuracy against the world, fails this group
        Failure: the test fails while any surface output words the F-06 figures as calibration or as accuracy against the world
        """
        _require_entry(self, "F-06 figures carry no calibration claim", ["score_profiles", "report", "DetectionLayer"])
        surface = _module
        result = surface.score_profiles()
        self.assertEqual(
            result["calibration"],
            "no calibration claim, self consistency only")
        self.assertEqual(result["calibration"],
                         surface.CALIBRATION_STANDING)
        self.assertEqual(
            result["standing"], "self consistency figures only")
        report = surface.report([])
        self.assertEqual(
            report["calibration"],
            "no calibration claim, self consistency only")

    def test_threshold_naming_on_conformance_statements(self):
        """Fixture: one conformance statement per threshold reading in the register, including the contested pair at finding C-6 (epoch weighted values against the unweighted figure)
        Pins: every conformance statement names the threshold set and the table value it checks, and carries the contested label where the register carries one, per AC-12
        Bar: formula and table are conformance material only, never assumption material
        Failure: the test fails while any conformance statement omits its threshold set, its table value, or a required contested label
        """
        _require_entry(self, "every conformance statement names its threshold set and table value", ["conformance_statement", "check_conformance", "DetectionLayer"])
        surface = _module
        for name in ("epoch weighted", "unweighted"):
            statement = surface.conformance_statement(
                table_identifier="LR-1", threshold_set=name)
            self.assertEqual(statement["threshold_set"], name)
            self.assertIn("table_value", statement)
            self.assertEqual(
                statement["contested_label"],
                "contested at finding C-6")
        weighted = surface.conformance_statement(
            threshold_set="epoch weighted")
        self.assertEqual(weighted["table_value"], 320)
        unweighted = surface.conformance_statement(
            threshold_set="unweighted")
        self.assertEqual(unweighted["table_value"], 160)

    def test_no_epoch_watch_gate_on_unweighted_figures(self):
        """Fixture: one conformance statement per threshold reading in the register, including the contested pair at finding C-6
        Pins: no epoch watch gate is built or reported on the unweighted figures
        Bar: an epoch watch gate built or reported on the unweighted figures fails this group
        Failure: the test fails while the surface cannot show that no epoch watch gate rests on the unweighted figures
        """
        _require_entry(self, "no epoch watch gate rests on the unweighted figures", ["conformance_statement", "check_conformance", "DetectionLayer"])
        surface = _module
        self.assertFalse(surface.epoch_watch_gate_on_unweighted())
        statement = surface.conformance_statement(
            threshold_set="unweighted")
        self.assertFalse(statement["epoch_watch_gate_on_unweighted"])
        layer = surface.DetectionLayer()
        other = layer.conformance_statement(
            threshold_set="unweighted")
        self.assertFalse(other["epoch_watch_gate_on_unweighted"])

    def test_oracle_and_null_controls_bracket_every_figure(self):
        """Fixture: F-06, the recorded Vigil profile set, run once with the oracle control and once with the null detector control of picked proposal INV8B-11, at the profile point sets of the fixture set; provenance label: self scored
        Pins: every detection figure the slice produces stands reported with its oracle and null bracket beside it, priced per point set bracketed, making no calibration claim and adopting no outside sleeper class
        Bar: a detection figure reported without its bracket, or outside the point sets its bracket covers, fails this group
        Failure: the test fails while any reported detection figure lacks its oracle and null bracket
        """
        _require_entry(self, "every detection figure stands reported with its oracle and null bracket", ["score_profiles", "report", "DetectionLayer"])
        surface = _module
        result = surface.score_profiles()
        controls = [b["control"] for b in result["bracket"]]
        self.assertEqual(controls, ["oracle", "null"])
        for bracket in result["bracket"]:
            self.assertEqual(
                bracket["point_sets"], list(result["profiles"]))
            self.assertEqual(bracket["outside_classes_adopted"], [])
            self.assertEqual(
                bracket["calibration"],
                "no calibration claim, self consistency only")


if __name__ == "__main__":
    unittest.main()
