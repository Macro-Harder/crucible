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


class TestStep15Fix1ViewEdge(unittest.TestCase):
    """Step 15 Round 1 fix pins: TA-02, TA-45, C-28, and C-29, on the MOD-04 view edge."""

    def test_barred_field_check_reads_every_group_at_any_depth(self):
        mod04 = require_surface(self, "barred field check reads every group recursively", "mod04", "view_record_carries_barred_field")
        top = {"view_contents": [{"membership": "x"}]}
        self.assertTrue(mod04.view_record_carries_barred_field(top))
        nested = {"view_contents": [{"outer": {"inner": {"ground_truth": "x"}}}]}
        self.assertTrue(mod04.view_record_carries_barred_field(nested))
        listed = {"view_contents": [[{"label": "x"}]]}
        self.assertTrue(mod04.view_record_carries_barred_field(listed))
        grouped = {"view_contents": [], "reputation_and_band_values": {"deep": {"membership": "x"}}}
        self.assertTrue(mod04.view_record_carries_barred_field(grouped))
        clean = {"view_contents": [{"kind": "daily_record"}], "reputation_and_band_values": {"score": 1}}
        self.assertFalse(mod04.view_record_carries_barred_field(clean))
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(contents=[{"outer": {"ground_truth": "x"}}])

    def test_selection_requires_a_stated_viewer_match_and_a_stated_day(self):
        mod04 = require_surface(self, "selection requires a stated viewer match and a stated day", "mod04", "select_view_records")
        records = [
            {"viewer_id": "viewer-1", "day": 3, "kind": "own"},
            {"day": 3, "kind": "unscoped"},
            {"viewer_id": "viewer-1", "kind": "undated"},
            {"viewer_id": "viewer-2", "day": 3, "kind": "cross viewer"},
            {"viewer_identifier": "viewer-1", "day": 3, "kind": "view field name"},
            {"viewer_identifier": "viewer-2", "day": 3, "kind": "view field name cross"},
        ]
        selected = mod04.select_view_records(records, "viewer-1", 5)
        self.assertEqual([item["kind"] for item in selected], ["own", "view field name"])

    def test_selection_applies_the_ruling_entry_5_position_rule(self):
        mod04 = require_surface(self, "selection applies the first seen day and arising position rule", "mod04", "select_view_records")
        records = [
            {"viewer_id": "viewer-1", "first_seen_day": 5, "arising_position": 9, "kind": "same day late"},
            {"viewer_id": "viewer-1", "first_seen_day": 5, "arising_position": 2, "kind": "same day early"},
            {"viewer_id": "viewer-1", "first_seen_day": 3, "arising_position": 99, "kind": "earlier day"},
            {"viewer_id": "viewer-1", "first_seen_day": 4, "kind": "day before"},
        ]
        selected = mod04.select_view_records(records, "viewer-1", 5, as_of_position=5)
        self.assertEqual(
            [item["kind"] for item in selected],
            ["same day early", "earlier day", "day before"],
        )

    def test_builder_stamps_the_handed_in_position_and_arrival_values(self):
        mod04 = require_surface(self, "the ViewRecord builder stamps handed in position and per item arrival values", "mod04", "build_view_record")
        contents = [
            {"kind": "a", "first_seen_day": 3, "delay": 2},
            {"kind": "b", "first_seen_day": 5, "delay": 0},
        ]
        record = mod04.build_view_record(
            day=5, contents=contents,
            run_record={"scheduling_position_identifier": "position-9"},
        )
        self.assertEqual(record["scheduling_position_identifier"], "position-9")
        self.assertEqual(record["first_seen_day_per_record"], {"0": 3, "1": 5})
        self.assertEqual(record["delay_applied_per_record"], {"0": 2, "1": 0})
        self.assertEqual(record["arrival_group_form"], "derived from contents")
        bare = mod04.build_view_record(day=5, contents=[{"kind": "a"}])
        self.assertIsNone(bare["scheduling_position_identifier"])
        self.assertEqual(bare["first_seen_day_per_record"], {"0": None})
        self.assertIn("not derived", bare["arrival_group_form"])

    def test_divergence_companion_computes_over_identities_and_bands(self):
        mod04 = require_surface(self, "the divergence companion computes the share of identities whose band differs across viewers", "mod04", "divergence_companion")
        components = []
        bands = {"id-1": ("high", "high"), "id-2": ("low", "high"), "id-3": ("mid", "mid")}
        for identity, pair in bands.items():
            for viewer, band in zip(("viewer-1", "viewer-2"), pair):
                components.append({"identity": identity, "viewer_id": viewer, "band": band})
        companion = mod04.divergence_companion(components=components)
        self.assertAlmostEqual(companion["band_differing_share"], 1 / 3)
        self.assertEqual(companion["differing_identity_count"], 1)
        self.assertEqual(companion["identity_count"], 3)
        self.assertEqual(companion["viewer_count"], 2)
        agreeing = [dict(item, band="same") for item in components]
        self.assertEqual(mod04.divergence_companion(components=agreeing)["band_differing_share"], 0)
        differing = []
        for identity in bands:
            differing.append({"identity": identity, "viewer_id": "viewer-1", "band": "low"})
            differing.append({"identity": identity, "viewer_id": "viewer-2", "band": "high"})
        self.assertEqual(mod04.divergence_companion(components=differing)["band_differing_share"], 1)
        no_band = mod04.divergence_companion(components=[{"viewer_id": "viewer-1", "component_values": [1]}])
        self.assertIsNone(no_band["band_differing_share"])


class TestStep15Round2Fix1ViewDepth(unittest.TestCase):
    """Step 15 Round 2 fix pins for R2-A7-03: the view select and build acts stand under the TA-03 depth bound and its named failure form."""

    def _deep(self, depth):
        value = "leaf"
        for _ in range(depth):
            value = {"k": value}
        return value

    def test_selection_raises_named_failure_on_deep_record(self):
        mod04 = require_surface(self, "selection raises the named failure on a record nested beyond the bound", "mod04", "select_view_records")
        record = {"viewer_id": "v1", "first_seen_day": 1, "payload": self._deep(2000)}
        with self.assertRaises(mod04.NamedFailure):
            mod04.select_view_records([record], "v1", 1)

    def test_builder_raises_named_failure_on_deep_contents(self):
        mod04 = require_surface(self, "the builder raises the named failure on contents nested beyond the bound", "mod04", "build_view_record")
        contents = [{"first_seen_day": 1, "delay": 0, "payload": self._deep(2000)}]
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(contents=contents, position="p", rule_version_set="rv")

    def test_builder_raises_named_failure_on_deep_groups(self):
        mod04 = require_surface(self, "the builder raises the named failure on a group value nested beyond the bound", "mod04", "build_view_record")
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=[{"first_seen_day": 1, "delay": 0}],
                position="p", rule_version_set="rv",
                reputation_and_band={"payload": self._deep(2000)},
            )
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=[{"first_seen_day": 1, "delay": 0}],
                position="p", rule_version_set="rv",
                graph_position={"payload": self._deep(2000)},
            )

    def test_selection_and_builder_raise_named_failure_on_cyclic_content(self):
        mod04 = require_surface(self, "selection and the builder raise the named failure on cyclic content", "mod04", "select_view_records", "build_view_record")
        cyclic = {}
        cyclic["self"] = cyclic
        record = {"viewer_id": "v1", "first_seen_day": 1, "payload": cyclic}
        with self.assertRaises(mod04.NamedFailure):
            mod04.select_view_records([record], "v1", 1)
        item = {"first_seen_day": 1, "delay": 0}
        item["self"] = item
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(contents=[item], position="p", rule_version_set="rv")

    def test_moderately_deep_content_still_stands(self):
        mod04 = require_surface(self, "selection and the builder still stand on content inside the bound", "mod04", "select_view_records", "build_view_record")
        record = {"viewer_id": "v1", "first_seen_day": 1, "payload": self._deep(50)}
        selected = mod04.select_view_records([record], "v1", 1)
        self.assertEqual(len(selected), 1)
        built = mod04.build_view_record(
            contents=[{"first_seen_day": 1, "delay": 0, "payload": self._deep(50)}],
            position="p", rule_version_set="rv",
        )
        self.assertEqual(built["form"], "ViewRecord")


if __name__ == "__main__":
    unittest.main()
