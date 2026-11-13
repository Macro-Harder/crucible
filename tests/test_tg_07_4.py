"""Test group TG-07.4. Slice S-07, module mod08.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod08, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
Standing bound: while the OP-16 values stand unfixed, no detection
score is reported as a pass or as a fail, and detection outputs carry
their profile bound label, per plan section 9 head rule 4 and
contract C-16. No test in this file invents the OP-16 values.
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
            "TG 07.4: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 07.4: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG074(unittest.TestCase):

    def test_sealed_late_class_discipline(self):
        """Fixture: F-08, the sealed late class test set, in its conditional form
        Pins: the detector is frozen first; at least one sleeper class and one honest challenge variant are then authored under the three separations (authorship, knowledge, record separation) and sealed until scoring closes, per Contract F
        Bar: the set stands expressly subject to the adoption decisions at NQ-51 and NQ-63; no score from the recorded profile set alone states or implies a result on the sealed classes
        Failure: the test fails while the sealed set cannot be shown frozen first, authored under the three separations, and sealed until scoring closes
        """
        _require_entry(self, "sealed late class discipline holds in its conditional form", ["score_sealed", "sealed_classes", "DetectionLayer"])
        surface = _module
        sealed = surface.create_sealed_set()
        surface.freeze_sealed_set(sealed)
        self.assertTrue(sealed["detector_frozen"])
        separations = ["authorship separation",
                       "knowledge separation",
                       "record separation"]
        surface.author_sealed_class(
            sealed, "sleeper class", "late sleeper one", separations)
        surface.author_sealed_class(
            sealed, "honest challenge variant",
            "honest variant one", separations)
        surface.seal_sealed_set(sealed)
        self.assertTrue(sealed["sealed"])
        standing = surface.score_sealed(sealed)
        self.assertIsNone(standing["result_on_sealed_classes"])
        self.assertEqual(
            standing["profile_set_result_on_sealed_classes"],
            "no result stated or implied")
        self.assertEqual(
            sealed["adoption_standing"],
            "subject to the adoption decisions at NQ-51 and NQ-63")

    def test_early_unseal_or_authoring_before_freezing_fails(self):
        """Fixture: F-08, the sealed late class test set, in a suite that unseals early, or authors before freezing
        Pins: a suite that unseals early, or authors before freezing, fails this group
        Bar: early unsealing and authoring before freezing are barred forms
        Failure: the test fails while the surface cannot reject an early unseal or authoring before freezing
        """
        _require_entry(self, "early unsealing and authoring before freezing are rejected", ["score_sealed", "sealed_classes", "DetectionLayer"])
        surface = _module
        separations = ["authorship separation",
                       "knowledge separation",
                       "record separation"]
        sealed = surface.create_sealed_set()
        with self.assertRaises(surface.NamedDetectionFailure):
            surface.author_sealed_class(
                sealed, "sleeper class", "late sleeper one",
                separations)
        surface.freeze_sealed_set(sealed)
        surface.author_sealed_class(
            sealed, "sleeper class", "late sleeper one", separations)
        surface.author_sealed_class(
            sealed, "honest challenge variant",
            "honest variant one", separations)
        surface.seal_sealed_set(sealed)
        with self.assertRaises(surface.NamedDetectionFailure):
            surface.unseal_sealed_set(sealed, scoring_closed=False)
        self.assertTrue(sealed["sealed"])
        surface.unseal_sealed_set(sealed, scoring_closed=True)
        self.assertFalse(sealed["sealed"])

    def test_outside_classes_deferred_in_the_open(self):
        """Fixture: F-07, the seven outside sleeper classes O-1 to O-7 plus honest challenge variants; provenance label: author claim, with labelled assumption ranges carried in the register entry
        Pins: version 1 detection is reported without the seven classes as one bounded self consistency report, with every figure carrying its profile bound label and the deferred classes named and visible in the record as deferred
        Bar: the brief adopts none of the seven classes; a figure reported without its profile bound label, or a report in which a deferred class is invisible, fails this group
        Failure: the test fails while the version 1 report omits a profile bound label or hides a deferred class
        """
        _require_entry(self, "outside classes stand deferred in the open with profile bound labels carried", ["score_profiles", "report", "DetectionLayer"])
        surface = _module
        result = surface.report([])
        self.assertEqual(
            [entry["class"] for entry in result["deferred_classes"]],
            ["O-1", "O-2", "O-3", "O-4", "O-5", "O-6", "O-7"])
        self.assertTrue(all(
            entry["standing"] == "deferred"
            for entry in result["deferred_classes"]))
        self.assertTrue(result["deferred_classes_visible"])
        self.assertEqual(result["outside_classes_adopted"], [])
        self.assertEqual(
            result["profile_bound_label"],
            surface.PROFILE_LABEL_CARRIAGE)

    def test_figure_without_profile_bound_label_fails(self):
        """Fixture: F-07, the seven outside sleeper classes O-1 to O-7 plus honest challenge variants; provenance label: author claim, with labelled assumption ranges carried in the register entry
        Pins: a figure reported without its profile bound label fails this group
        Bar: every figure carries its profile bound label, and a deferred class stays named and visible in the record as deferred
        Failure: the test fails while the surface cannot reject a figure reported without its profile bound label
        """
        _require_entry(self, "a figure without its profile bound label is rejected", ["score_profiles", "report", "DetectionLayer"])
        surface = _module
        bare = {"agent_identifier": "agent-07-4", "day": 1,
                "verdict_state": "WATCH"}
        self.assertFalse(surface.validate_output(bare))
        with self.assertRaises(surface.NamedDetectionFailure):
            surface.report([bare])
        labelled = surface.score_day([{
            "agent_identifier": "agent-07-4", "day": 1,
            "feature_values": {"activity": 4},
            "records_for_agent_and_day": [],
        }])["verdict_states"][0]
        self.assertTrue(surface.validate_output(labelled))
        result = surface.report([labelled])
        self.assertEqual(result["figures"], [labelled])

    def test_no_pass_or_fail_score_while_verdict_rule_unfixed(self):
        """Fixture: a scoring run inspected for its output form, while the OP-16 values stand unfixed at settlement register Entry 15
        Pins: while the OP-16 values stand unfixed, no detection score is reported as a pass or as a fail, and detection outputs carry their profile bound label, per plan section 9 head rule 4 and contract C-16
        Bar: reporting a detection score as a pass or as a fail while the verdict rule limb stands unfixed fails this group; no test invents the OP-16 values
        Failure: the test fails while any detection output reports a score as a pass or as a fail, or lacks its profile bound label
        """
        _require_entry(self, "no detection score is reported as pass or fail while OP-16 stands unfixed, and outputs carry their profile bound label", ["score", "report", "DetectionLayer"])
        surface = _module
        result = surface.score_day([{
            "agent_identifier": "agent-07-4", "day": 1,
            "feature_values": {"activity": 4},
            "records_for_agent_and_day": [],
        }])
        self.assertIsNone(result["score_verdict"])
        self.assertNotIn("score_verdict", result["detection_output"])
        for output in result["verdict_states"]:
            self.assertIsNone(output["score_verdict"])
            self.assertIn(output["verdict_state"],
                          surface.VERDICT_LADDER)
        report = surface.report(result["verdict_states"])
        self.assertIsNone(report["score_verdict"])
        self.assertEqual(
            report["pass_or_fail_reporting"],
            "not reported while OP-16 stands open")
        marked = dict(result["verdict_states"][0])
        marked["score_verdict"] = "pass"
        self.assertFalse(surface.validate_output(marked))

    def test_no_invented_label_values_for_form_27(self):
        """Fixture: a scoring run inspected for its profile bound label values, for the Form 27 label set
        Pins: the profile bound label value set stands open at OP-16; this test pins the absence of invented label values and the carriage of the label itself
        Bar: a test inventing label values before that naming fails this group
        Failure: the test fails while any surface output carries an invented profile bound label value
        """
        _require_entry(self, "no invented profile bound label values stand for the Form 27 label set", ["score", "report", "DetectionLayer"])
        surface = _module
        result = surface.score_day([{
            "agent_identifier": "agent-07-4", "day": 1,
            "feature_values": {"activity": 4},
            "records_for_agent_and_day": [],
        }])
        output = result["detection_output"]
        self.assertEqual(
            output["profile_bound_label"],
            surface.PROFILE_LABEL_CARRIAGE)
        self.assertIn(
            "value set open at OP-16",
            output["profile_bound_label"])
        invented = dict(output)
        invented["profile_bound_label"] = "invented label value"
        self.assertFalse(surface.validate_output(invented))


if __name__ == "__main__":
    unittest.main()
