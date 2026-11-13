"""Test group TG-14.3. Scoring harness separation, Contract F.
Slice S-14, Replication Checker and scoring interface, MOD-13. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod13, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod13 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod13 absent, pinned behaviour unmet: " + behaviour)


class TestTG143(unittest.TestCase):
    def test_scoring_sits_outside_the_run(self):
        """
        Fixture: F-08 at the harness limb, the sealed late class test set.
        Pins: Scoring consumes records after the run, under the three separations, authorship, knowledge, and record separation, and no scoring code runs inside the run boundary.
        Bar: Adoption of the separate profile author team form stands open; until it stands adopted on the record, tests pin the three separations as record properties, who authored, what they could know, and where the records sit, not as a team form.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.3 and this behaviour; scoring code running inside the run boundary fails this test when the surface stands.
        """
        require_surface(self, "TG-14.3", "scoring sits outside the run boundary under the three separations of authorship, knowledge, and record separation")
        import crucible.mod13 as surface
        position = surface.scoring_harness_position()
        self.assertEqual(position["position"], "outside the run boundary")
        self.assertFalse(position["inside_detection_module"])
        genuine = {
            "run_identifier": "run-tg143",
            "scoring_day_range": [1],
            "verdict_states_and_accumulator_updates": [],
            "profile_bound_label": "profile bound label attached (value set open at OP-16)",
        }
        record = surface.score_detection_outputs(
            [dict(genuine), dict(genuine)],
            authored_by="profile authors, named on the record",
            knowledge="no ground truth and no membership",
            records_position="records held outside the run",
        )
        self.assertTrue(surface.validate_scoring_record(record))
        self.assertEqual(set(record["separations"].keys()), {"authorship", "knowledge", "record separation"})
        self.assertFalse(record["inside_run_boundary"])
        self.assertIsNone(record["value_returned_into_run"])

    def test_witness_rerun_is_difference_only(self):
        """
        Fixture: A witness rerun under a later rule set, per operation C-04.
        Pins: The rerun is a new run linked to the original, carrying the rule set version identity it ran under, and is read as a report of the difference between two rule sets and nothing more.
        Bar: A rerun that overwrites the original result, the original run record, or the original witness standing fails this group, as does any wording treating the newer record as the corrected version of the older one.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.3 and this behaviour; a rerun overwriting the original, or worded as its corrected version, fails this test when the surface stands.
        """
        require_surface(self, "TG-14.3", "witness rerun as a new linked run read as difference only, original result, record, and standing untouched")
        import crucible.mod13 as surface
        import copy
        original = {"run_id": "run-1", "result": "original result", "standing": "witness"}
        before = copy.deepcopy(original)
        rerun = surface.witness_rerun(original, rule_set_version="rules-2")
        self.assertEqual(original, before)
        self.assertNotEqual(rerun["run_id"], "run-1")
        self.assertEqual(rerun["linked_to"], "run-1")
        self.assertEqual(rerun["rule_set_version"], "rules-2")
        self.assertFalse(rerun["verdicts_transferred"])
        self.assertTrue(surface.validate_rerun_reading({"read_as": "difference between two rule sets only"}))
        self.assertFalse(surface.validate_rerun_reading({"read_as": "corrected version of the original"}))
        self.assertFalse(surface.validate_rerun_reading({"overwrites_original": True}))

    def test_history_extension_appends_never_rewrites(self):
        """
        Fixture: A history extended past its first horizon, per operation C-05, at its non seed limbs.
        Pins: The extension appends a new linked segment, linked by run identifier and segment order, under the same rule set version as the segment it extends, rewriting no part of the segment it extends, and daily aggregates stay horizon neutral.
        Bar: An extension rewriting any part of the segment it extends, or daily aggregates that change meaning with the horizon, fails this group. The seed derivation limb of the extension stands in gated form in the companion test in this file.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.3 and this behaviour; an extension rewriting its original segment fails this test when the surface stands.
        """
        require_surface(self, "TG-14.3", "history extension appends a new linked segment under the same rule set version, rewriting nothing, daily aggregates horizon neutral")
        import crucible.mod13 as surface
        import copy
        history = [{"run_id": "run-1", "segment_order": 1, "rule_set_version": "rules-1", "content": "first segment"}]
        before = copy.deepcopy(history)
        extended = surface.extend_history(history, {"content": "second segment"})
        self.assertEqual(history, before)
        self.assertEqual(len(extended), 2)
        self.assertEqual(extended[0], before[0])
        self.assertEqual(extended[1]["linked_run"], "run-1")
        self.assertEqual(extended[1]["segment_order"], 2)
        self.assertEqual(extended[1]["rule_set_version"], "rules-1")
        self.assertTrue(surface.validate_aggregate_form(surface.daily_aggregate_form()))
        self.assertFalse(surface.validate_aggregate_form(["run_id", "horizon"]))

    def test_history_extension_seed_limb_gated(self):
        """
        Fixture: A history extended past its first horizon, at its seed derivation limb only. State recorded as gated on the DQ7-02 adoption record.
        Pins: The extension runs under the same seed derivation as the segment it extends. The seed derivation limb rests on the recommended and unadopted form while NQ-24 stands open, at TG-02.1, so this limb records its state as gated on adoption, as TG-14.3 states for extension tests wherever they consume derived seeds.
        Bar: A seed limb result presented as passed before the adoption record stands fails this group.
        Failure: Gated form only; this test never passes while the DQ7-02 adoption record does not stand.
        """
        self.skipTest("Gated: the DQ7-02 adoption record for the seed derivation form, TG-02.1, register question NQ-24")


class TestStep15Fix1Mod13ScoringAndHistory(unittest.TestCase):
    """Step 15 Round 1 fix pins: TA-36, TA-38, TB-51, C-58, and the MOD-13 limb of TA-30."""

    SEPARATIONS = {
        "authored_by": "profile authors, named on the record",
        "knowledge": "no ground truth and no membership",
        "records_position": "records held outside the run",
    }
    LABEL = "profile bound label attached (value set open at OP-16)"

    def _genuine_output(self):
        return {
            "run_identifier": "run-fix1",
            "scoring_day_range": [1],
            "verdict_states_and_accumulator_updates": [],
            "profile_bound_label": self.LABEL,
        }

    def test_extend_history_fails_where_version_or_link_stands_absent(self):
        require_surface(self, "TG-14.3", "history extension fails in named form where the rule set version does not stand on the record")
        import crucible.mod13 as surface
        no_version = [{"run_id": "run-1", "segment_order": 1, "content": "first"}]
        with self.assertRaises(surface.NamedReplicationFailure):
            surface.extend_history(no_version, {"content": "second"})
        no_link = [{"segment_order": 1, "rule_set_version": "rules-1", "content": "first"}]
        with self.assertRaises(surface.NamedReplicationFailure):
            surface.extend_history(no_link, {"content": "second"})
        history = [{"run_id": "run-1", "segment_order": 1, "rule_set_version": "rules-1", "content": "first"}]
        extended = surface.extend_history(history, {"content": "second"})
        self.assertEqual(extended[1]["rule_set_version"], "rules-1")
        self.assertEqual(extended[1]["linked_run"], "run-1")
        stated = surface.extend_history(history, {"content": "second", "rule_set_version": "rules-1"})
        self.assertEqual(stated[1]["rule_set_version"], "rules-1")

    def test_score_detection_outputs_refuses_a_non_list_input(self):
        require_surface(self, "TG-14.3", "scoring refuses a non list input in the named failure form")
        import crucible.mod13 as surface
        with self.assertRaises(surface.NamedReplicationFailure):
            surface.score_detection_outputs("0123456789", **self.SEPARATIONS)

    def test_score_detection_outputs_requires_supplied_separations(self):
        require_surface(self, "TG-14.3", "scoring requires the three separations as record properties and supplies none itself")
        import crucible.mod13 as surface
        with self.assertRaises(surface.NamedReplicationFailure):
            surface.score_detection_outputs([self._genuine_output()])

    def test_score_detection_outputs_refuses_non_record_inputs(self):
        require_surface(self, "TG-14.3", "scoring counts only checkable DetectionOutput records")
        import crucible.mod13 as surface
        with self.assertRaises(surface.NamedReplicationFailure):
            surface.score_detection_outputs([{}, None], **self.SEPARATIONS)
        with self.assertRaises(surface.NamedReplicationFailure):
            surface.score_detection_outputs([{"output": 1}], **self.SEPARATIONS)

    def test_scoring_record_carries_the_stated_label(self):
        require_surface(self, "TG-14.3", "the Contract F scoring record carries the label in its stated carriage value and its validator checks it")
        import crucible.mod13 as surface
        record = surface.score_detection_outputs([self._genuine_output()], **self.SEPARATIONS)
        self.assertEqual(record["outputs_scored"], 1)
        self.assertEqual(record["profile_bound_label"], self.LABEL)
        self.assertEqual(record["separations"]["authorship"], self.SEPARATIONS["authored_by"])
        self.assertTrue(surface.validate_scoring_record(record))
        unlabelled_input = self._genuine_output()
        del unlabelled_input["profile_bound_label"]
        carried = surface.score_detection_outputs([unlabelled_input], **self.SEPARATIONS)
        self.assertEqual(carried["profile_bound_label"], self.LABEL)
        missing_label = dict(record)
        del missing_label["profile_bound_label"]
        self.assertFalse(surface.validate_scoring_record(missing_label))
        paraphrase = dict(record)
        paraphrase["profile_bound_label"] = "carriage form, value set open at OP-16"
        self.assertFalse(surface.validate_scoring_record(paraphrase))

    def test_verdict_record_on_no_claim_names_the_actual_defect(self):
        require_surface(self, "TG-14.3", "verdict record on no claim identifier names that defect")
        import crucible.mod13 as surface
        with self.assertRaises(surface.NamedReplicationFailure) as caught:
            surface.verdict_record(None)
        self.assertIn("claim identifier", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
