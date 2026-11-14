"""Step 15 Round 2 fix pins for cluster R2-2, Fix Builder 2.

Each test pins one charged cure: R2-A7-02, the MOD-10 view leak
runner reading the one barred vocabulary the cured MOD-04 checker
and the cured MOD-03 helper stand on, at any depth and in any
group, with case handled as those surfaces handle it; and the
MOD-10 limb of R2-A7-06, delete_checkpoint requiring a stated,
well formed clause C5 trigger and deletion rule path in their
standing named forms. Tests reset the module stores around
themselves so their standing does not depend on suite order.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod10 as mod10


class Fix2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


def _view(contents=None, rep=None, graph=None):
    base = mod04.build_view_record(
        run_id="run-r2fix2-view", viewer_id="viewer-1", day=5,
        contents=[{"note": "clean", "first_seen_day": 1, "delay": 0}],
        position="pos-1", rule_version_set="rv-1")
    if contents is not None:
        base["view_contents"] = contents
    if rep is not None:
        base["reputation_and_band_values"] = rep
    if graph is not None:
        base["graph_position_as_seen"] = graph
    return base


class TestR2A702ViewLeakVocabulary(Fix2Base):
    def test_clean_view_passes_the_runner(self):
        result = mod10.run_view_leak_check(_view())
        self.assertTrue(result["reportable"])
        self.assertEqual(
            result["forms_run"], ["canary", "field_validation", "timing"])

    def test_every_standing_barred_name_refused_in_contents(self):
        names = (
            "ground_truth", "ground_truth_field", "membership",
            "honest_membership", "farm_membership", "is_honest",
            "is_farm", "canary", "canary_value", "membership_value",
            "sleeper", "ground_truth_label", "label",
        )
        for name in names:
            record = _view(contents=[{name: "CANARYVAL"}])
            self.assertTrue(
                mod04.view_record_carries_barred_field(record), name)
            with self.assertRaises(ValueError, msg=name) as caught:
                mod10.run_view_leak_check(record)
            self.assertIn("canary", str(caught.exception), name)

    def test_barred_names_refused_in_reputation_and_graph_groups(self):
        cases = (
            _view(rep={"farm_membership": "x"}),
            _view(rep={"ground_truth_field": "x"}),
            _view(rep={"membership_value": "x"}),
            _view(rep={"canary": "x"}),
            _view(graph={"ground_truth": "CANARYVAL"}),
            _view(graph={"membership": "CANARYVAL"}),
            _view(graph={"label": "CANARYVAL"}),
            _view(graph={"canary_value": "CANARYVAL"}),
        )
        for record in cases:
            with self.assertRaises(ValueError) as caught:
                mod10.run_view_leak_check(record)
            self.assertIn("canary", str(caught.exception))

    def test_capitalised_forms_refused_as_the_cured_surfaces_refuse(self):
        cases = (
            _view(contents=[{"Ground_Truth": "CANARYVAL"}]),
            _view(contents=[{"Canary_Value": "CANARYVAL"}]),
            _view(rep={"MEMBERSHIP": "CANARYVAL"}),
            _view(graph={"SLEEPER": "CANARYVAL"}),
        )
        for record in cases:
            self.assertTrue(mod04.view_record_carries_barred_field(record))
            with self.assertRaises(ValueError):
                mod10.run_view_leak_check(record)

    def test_mod03_variant_forms_refused(self):
        cases = (
            _view(contents=[{"groundtruth": "x"}]),
            _view(contents=[{"canary_copy": "x"}]),
            _view(contents=[{"sleeper_membership_score": "x"}]),
            _view(rep={"honest_or_farm_membership": "x"}),
            _view(rep={"membership_ground_truth": "x"}),
        )
        for record in cases:
            with self.assertRaises(ValueError):
                mod10.run_view_leak_check(record)

    def test_barred_key_at_any_depth_and_in_any_wrapper_refused(self):
        deep_bottom = {"ground_truth": "x"}
        for _ in range(2000):
            deep_bottom = {"k": deep_bottom}
        cases = (
            _view(contents=[{"a": {"canary": "CANARYVAL"}}]),
            _view(contents=[[{"a": [{"canary_value": "CANARYVAL"}]}]]),
            _view(contents=[{"a": ({"is_farm": "x"},)}]),
            _view(contents=[{"payload": deep_bottom}]),
        )
        for record in cases:
            with self.assertRaises(ValueError):
                mod10.run_view_leak_check(record)
        deep_clean = "leaf"
        for _ in range(2000):
            deep_clean = {"k": deep_clean}
        result = mod10.run_view_leak_check(
            _view(contents=[{"payload": deep_clean}]))
        self.assertTrue(result["reportable"])

    def test_cyclic_content_read_without_looping(self):
        cyclic = {"note": "clean", "first_seen_day": 1, "delay": 0}
        cyclic["self"] = cyclic
        result = mod10.run_view_leak_check(_view(contents=[cyclic]))
        self.assertTrue(result["reportable"])
        cyclic["canary"] = "CANARYVAL"
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(_view(contents=[cyclic]))

    def test_values_and_legitimate_sibling_keys_pass(self):
        record = _view(contents=[{
            "note": "canary", "activity": "stated",
            "labelled_assumptions": "stated", "labels": "stated",
            "first_seen_day": 1, "delay": 0}])
        result = mod10.run_view_leak_check(record)
        self.assertTrue(result["reportable"])

    def test_release_and_retention_follow_the_runner(self):
        for record in (
                _view(graph={"ground_truth": "CANARYVAL"}),
                _view(contents=[{"Ground_Truth": "CANARYVAL"}]),
                _view(contents=[{"a": {"canary": "CANARYVAL"}}])):
            with self.assertRaises(Exception):
                mod04.release_view(mod04.hold_view(record))
            with self.assertRaises(ValueError):
                mod10.retain_view_record(record)
            self.assertEqual(
                mod10.view_records_for_run("run-r2fix2-view"), [])
        released = mod04.release_view(mod04.hold_view(_view()))
        self.assertTrue(released["released"])
        mod10.retain_view_record(_view())
        self.assertEqual(
            len(mod10.view_records_for_run("run-r2fix2-view")), 1)


class TestR2A706DeleteCheckpointForm(Fix2Base):
    def _seed(self):
        mod10.retain_checkpoint(
            {"run_identifier": "run-r2fix2-del", "simulated_day": 3})

    def _refused_and_kept(self, trigger, rule_path):
        self._seed()
        with self.assertRaises(ValueError):
            mod10.delete_checkpoint(
                "run-r2fix2-del", 3, trigger=trigger, rule_path=rule_path)
        self.assertEqual(
            len(mod10.checkpoints_for_run("run-r2fix2-del")), 1)
        mod10.reset_stores()

    def test_stated_forms_delete(self):
        self._seed()
        act = mod10.delete_checkpoint(
            "run-r2fix2-del", 3, trigger="clause C5 stated trigger",
            rule_path="stated deletion rule path")
        self.assertEqual(act["removed"], 1)
        self.assertEqual(act["trigger"], "clause C5 stated trigger")
        self.assertEqual(act["rule_path"], "stated deletion rule path")
        self.assertEqual(act["actor"], "Recorder")
        self.assertEqual(mod10.checkpoints_for_run("run-r2fix2-del"), [])

    def test_standing_named_forms_delete(self):
        self._seed()
        act = mod10.delete_checkpoint(
            "run-r2fix2-del", 3, trigger="Clause C5 deletion trigger",
            rule_path="deletion rule")
        self.assertEqual(act["removed"], 1)
        self._seed()
        act = mod10.delete_checkpoint(
            "run-r2fix2-del", 3, trigger="clause_C5 stated trigger",
            rule_path="deletion_rule")
        self.assertEqual(act["removed"], 1)

    def test_nonsense_empty_and_wrong_typed_values_refused(self):
        for trigger, rule_path in (
                ("nonsense", "nonsense"),
                ("", ""),
                ("   ", "   "),
                (123, False),
                (None, None),
                (["clause C5 stated trigger"], {"path": "deletion rule"})):
            self._refused_and_kept(trigger, rule_path)

    def test_each_limb_refused_on_its_own(self):
        self._refused_and_kept("clause C5 stated trigger", "nonsense")
        self._refused_and_kept("clause C5 stated trigger", "")
        self._refused_and_kept("clause C5 stated trigger", 123)
        self._refused_and_kept("nonsense", "stated deletion rule path")
        self._refused_and_kept("", "stated deletion rule path")
        self._refused_and_kept(False, "stated deletion rule path")
        self._refused_and_kept(
            "holding period complete", "stated deletion rule path")
        self._refused_and_kept(
            "clause C5 stated trigger", "some other rule path")

    def test_clause_c8_protection_still_refuses(self):
        self._seed()
        with self.assertRaises(ValueError):
            mod10.delete_checkpoint(
                "run-r2fix2-del", 3, trigger="clause C5 stated trigger",
                rule_path="stated deletion rule path",
                regression_corpus_copy=True)
        self.assertEqual(
            len(mod10.checkpoints_for_run("run-r2fix2-del")), 1)


if __name__ == "__main__":
    unittest.main()
