"""Test group TG-11.2. Viewer divergence carriage and the flip trial, as bounded records.

Slice S-11, per viewer view carriage. Suite convention: this file tries to
import the product modules for the view edges its group names, package
crucible, modules mod04, mod05, and mod10, and records whether the surfaces
stand. While a surface stands absent, each test fails with a message naming
the pinned behaviour and its group.
"""
import unittest

SURFACES = {}
SURFACE_ERRORS = {}
try:
    from crucible import mod04
    SURFACES["mod04"] = mod04
    SURFACE_ERRORS["mod04"] = None
except Exception as exc:
    SURFACE_ERRORS["mod04"] = exc
try:
    from crucible import mod05
    SURFACES["mod05"] = mod05
    SURFACE_ERRORS["mod05"] = None
except Exception as exc:
    SURFACE_ERRORS["mod05"] = exc
try:
    from crucible import mod10
    SURFACES["mod10"] = mod10
    SURFACE_ERRORS["mod10"] = None
except Exception as exc:
    SURFACE_ERRORS["mod10"] = exc

GROUP = "TG-11.2"


def require_surface(testcase, behaviour, module, *attrs):
    surface = SURFACES.get(module)
    if surface is None:
        testcase.fail(
            GROUP + ": product surface crucible." + module + " stands absent ("
            + repr(SURFACE_ERRORS.get(module)) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(surface, attr):
            testcase.fail(
                GROUP + ": product surface crucible." + module + " lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )
    return surface


class TestDivergenceCarriage(unittest.TestCase):
    def test_divergence_reported_as_spread(self):
        """Fixture: a run with gossip delay in force, scored over all viewers of the run, with the per viewer components and the divergence companion the run records, as TG-11.2 states.
        Pins: the JointOutcomeVector and the daily components stand computed per viewer with the viewer identifier on every component, the divergence companion stands beside that form in the daily aggregates and at end of run, and the carriage reports a spread of per viewer results.
        Bar: no singular vector is reported, no cross run comparison rests on the outcome vector or the daily components as one quantity, and the vector is not presented as one comparable quantity in any run.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-11.2; with the surfaces present, a carriage with no divergence companion, or a component with no viewer identifier, fails.
        """
        mod04 = require_surface(self, "divergence reported as a spread of per viewer results", "mod04", "per_viewer_components", "divergence_companion")
        components = mod04.per_viewer_components(run_id="run-under-test")
        self.assertTrue(components)
        for component in components:
            self.assertIn("viewer_id", component)
        companion = mod04.divergence_companion(run_id="run-under-test")
        self.assertIn("daily_aggregates", companion)
        self.assertIn("end_of_run", companion)
        self.assertIn("band_differing_share", companion["end_of_run"])

    def test_singular_vector_presentation_fails(self):
        """Fixture: a carriage presenting the outcome vector as one singular comparable quantity, as TG-11.2 states.
        Pins: the presentation fails validation at the Recorder view edge.
        Bar: no singular vector is reported, and the vector is not presented as one comparable quantity in any run.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-11.2; with the surfaces present, acceptance of the singular presentation fails.
        """
        mod10 = require_surface(self, "singular vector presentation rejected", "mod10", "validate_view_carriage")
        carriage = {"form": "singular_vector", "presented_as": "one comparable quantity"}
        self.assertFalse(mod10.validate_view_carriage(carriage))


class TestFlipTrial(unittest.TestCase):
    def test_flip_trial_is_property_record(self):
        """Fixture: the viewer flip trial record form the slices paper names, as TG-11.2 states.
        Pins: the trial reports a property of candidate forms and restates the bar on a singular presentation on the face of the trial record.
        Bar: a trial record cited as a run result fails this group.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-11.2; with the surfaces present, a trial record with no property statement, or no bar restated on its face, fails.
        """
        mod04 = require_surface(self, "flip trial is a property record, never a run result", "mod04", "flip_trial_record")
        record = mod04.flip_trial_record(trial_id="trial-under-test")
        self.assertEqual(record["kind"], "property_of_candidate_forms")
        self.assertIn("singular_presentation_bar", record)

    def test_flip_trial_cited_as_run_result_fails(self):
        """Fixture: a citation of a flip trial record as a run result, as TG-11.2 states.
        Pins: the citation fails validation at the Recorder view edge.
        Bar: a trial record cited as a run result fails this group.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-11.2; with the surfaces present, acceptance of the citation fails.
        """
        mod10 = require_surface(self, "flip trial cited as a run result rejected", "mod10", "validate_view_carriage")
        carriage = {"form": "flip_trial_record", "cited_as": "run_result"}
        self.assertFalse(mod10.validate_view_carriage(carriage))


class TestRecordEnforcedScope(unittest.TestCase):
    def test_record_enforced_for_agent_held_views(self):
        """Fixture: wording describing boundaries one and two of brief section 7 as record enforced for agent held views under the decided ViewRecord carriage, as TG-11.2 states.
        Pins: that description stands permitted for agent held views, and for no wider class.
        Bar: the wording fails this group wherever it appears for any wider class.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-11.2; with the surfaces present, a rejection of the agent held view wording fails.
        """
        mod05 = require_surface(self, "record enforced description permitted for agent held views only", "mod05", "validate_view_wording")
        wording = {"description": "record enforced", "scope": "agent held views"}
        self.assertTrue(mod05.validate_view_wording(wording))

    def test_record_enforced_wider_class_fails(self):
        """Fixture: wording describing boundaries one and two of brief section 7 as record enforced for a class wider than agent held views, including in a test name or a fixture label, as TG-11.2 states.
        Pins: the wording fails validation in every such position.
        Bar: the wording fails this group wherever it appears for any wider class, including in a test name or a fixture label.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-11.2; with the surfaces present, acceptance of the wider wording fails.
        """
        mod05 = require_surface(self, "record enforced description for a wider class rejected", "mod05", "validate_view_wording")
        self.assertFalse(mod05.validate_view_wording({"description": "record enforced", "scope": "all views"}))
        self.assertFalse(mod05.validate_view_wording({"description": "record enforced", "scope": "presented views"}))
        self.assertFalse(mod05.validate_view_wording({"description": "record enforced", "scope": "all views", "test_name": "test_record_enforced_for_all_views"}))
        self.assertFalse(mod05.validate_view_wording({"description": "record enforced", "scope": "all views", "fixture_label": "record enforced for all views"}))


if __name__ == "__main__":
    unittest.main()
