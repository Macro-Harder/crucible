"""Pins for Round 15 rows R15-011 to R15-024, Fix Wave 15 Builder 2.

Each pin proves the handed reading defect of its row on the pristine
tree and passes only where the act reads the stored contents through
base class readings, under settlement S-1. Standard library only.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod05 as mod05
import crucible.mod06 as mod06
import crucible.mod08 as mod08
import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod14 as mod14
import crucible.mod16 as mod16


class FakeGet(dict):
    """A dict whose own get reports fabricated values."""

    def __init__(self, stored, fake):
        super().__init__(stored)
        self._fake = fake

    def get(self, key, default=None):
        if key in self._fake:
            return self._fake[key]
        return dict.get(self, key, default)


class RaisingGet(dict):
    def get(self, key, default=None):
        raise RuntimeError("fabricated get failure")


class FakeProtocol(dict):
    """A dict whose contains and getitem report fabricated values."""

    def __init__(self, stored, fake):
        super().__init__(stored)
        self._fake = fake

    def __contains__(self, key):
        return True

    def __getitem__(self, key):
        if key in self._fake:
            return self._fake[key]
        return dict.__getitem__(self, key)


class FakeItems(dict):
    def items(self):
        return iter(())


class FakeIterList(list):
    """A list whose own iteration yields fabricated elements."""

    def __init__(self, stored, fake):
        super().__init__(stored)
        self._fake = fake

    def __iter__(self):
        return iter(self._fake)


class FakeIterDict(dict):
    """A dict whose own iteration yields fabricated keys."""

    def __init__(self, stored, fake_keys):
        super().__init__(stored)
        self._fake_keys = fake_keys

    def __iter__(self):
        return iter(self._fake_keys)


class TestR15011(unittest.TestCase):
    def test_run_command_reads_stored_kind(self):
        payload = FakeGet({"kind": "bogus_kind"}, {"kind": "sweep"})
        result = mod14.run_command("store_kind_check", payload)
        self.assertFalse(result["store_kind_ok"])

    def test_run_command_raising_get_does_not_fabricate(self):
        payload = FakeGet({"kind": "sweep"}, {"kind": "bogus_kind"})
        result = mod14.run_command("store_kind_check", payload)
        self.assertTrue(result["store_kind_ok"])


class TestR15012(unittest.TestCase):
    def test_work_credit_reads_stored_event(self):
        event = FakeProtocol(
            {"agent_identifier": "a", "accepted": False},
            {"agent_identifier": "ghost", "accepted": True})
        result = mod05.work_credit([event])
        self.assertIn("a", result["counters"])
        self.assertNotIn("ghost", result["counters"])
        self.assertEqual(result["counters"]["a"]["accepted"], 0)

    def test_aggregate_reputation_reads_stored_inputs(self):
        inputs = FakeProtocol(
            {"agent_identifier": "a", "accepted_work": 1,
             "vouches_received": [], "penalties": 0},
            {"accepted_work": 100})
        result = mod05.aggregate_reputation(inputs)
        self.assertEqual(result["score"], 1)

    def test_realised_degree_by_epoch_items(self):
        edges = [{"voucher": "a", "vouchee": "b"}]
        by_epoch = FakeItems({"e1": edges})
        result = mod05.realised_degree_distribution(
            edges, by_epoch=by_epoch)
        self.assertIn("e1", result["by_epoch"])


class TestR15013(unittest.TestCase):
    def test_graph_snapshot_validator_reads_stored_fields(self):
        edges = [
            {"voucher": "a", "vouchee": "b",
             "component_definition_version": "v1"},
            {"voucher": "b", "vouchee": "a",
             "component_definition_version": "v1"},
        ]
        snap = mod05.graph_snapshot(edges, component_definition_version="v1")
        stored = dict(snap)
        stored["component_list"] = "bogus"
        fake = FakeGet(stored, snap)
        self.assertFalse(mod05.validate_graph_snapshot(fake, edges))

    def test_headline_claim_reads_stored_threshold(self):
        counts = {
            name: {"share": {"numerator": 0, "denominator": 1}}
            for name in mod05.EXCLUDED_CLASSES
        }
        run = {"excluded_class_counts_and_shares": counts}
        family = FakeGet({}, {"excluded_share_threshold": 0.5})
        self.assertFalse(
            mod05.validate_headline_adjudication_claim(family, run))

    def test_headline_claim_nested_counts_items(self):
        counts = {
            name: {"share": {"numerator": 0, "denominator": 1}}
            for name in mod05.EXCLUDED_CLASSES
        }
        forged = mod05.FORGED_VOUCH_BASIS_CLASS
        counts[forged] = {"share": {"numerator": 1, "denominator": 1}}
        run = {"excluded_class_counts_and_shares": FakeItems(counts)}
        family = {"excluded_share_threshold": 10.0}
        self.assertFalse(
            mod05.validate_headline_adjudication_claim(family, run))


class TestR15014(unittest.TestCase):
    def test_score_bearing_figure_reads_stored_share(self):
        share = FakeProtocol(
            {"numerator": 1, "denominator": 2},
            {"numerator": 100, "denominator": 2})
        self.assertEqual(mod05.score_bearing_figure(10, share), 5.0)

    def test_recompute_share_reads_stored_mappings(self):
        logged = FakeProtocol({"e1": 5}, {"e1": 999})
        recomputed = {"e1": 5}
        result = mod05.recompute_share(logged, recomputed)
        self.assertEqual(result["divergence_count"], 0)


class TestR15015(unittest.TestCase):
    def _arms(self):
        shared = {"inputs": {"cast": "same"}, "society": "same",
                  "parameters": "same", "seeds": "same"}
        arm_a = dict(shared)
        arm_a.update({"variant": "B-4", "results": [
            mod06.escrow_result("release", variant="B-4")]})
        arm_b = dict(shared)
        arm_b.update({"variant": "B-3", "results": [
            mod06.escrow_result("release", variant="B-3")]})
        return arm_a, arm_b

    def test_matched_arms_read_stored_variant(self):
        arm_a, arm_b = self._arms()
        fake_b = FakeGet(arm_b, {"variant": "B-4"})
        self.assertTrue(mod06.matched_arms_valid(arm_a, fake_b))

    def test_matched_arms_raising_get(self):
        arm_a, arm_b = self._arms()
        try:
            result = mod06.matched_arms_valid(arm_a, RaisingGet(arm_b))
        except RuntimeError:
            self.fail("raising get escaped bare")
        self.assertTrue(result)


class TestR15016(unittest.TestCase):
    def test_dq_table_plain_empty(self):
        self.assertFalse(mod06.validate_dq_arrival_table([]))

    def test_dq_table_reads_stored_final_column(self):
        rows = mod06.dq_arrival_table()
        rows[0] = FakeGet(rows[0], {"final_column": ""})
        dict.__setitem__(rows[0], "final_column", "filled")
        self.assertFalse(mod06.validate_dq_arrival_table(rows))

    def test_dq_table_iteration_reads_stored_rows(self):
        fake_rows = FakeIterList([], mod06.dq_arrival_table())
        self.assertFalse(mod06.validate_dq_arrival_table(fake_rows))


class TestR15017(unittest.TestCase):
    def test_checkpoint_count_reads_stored_row(self):
        row = FakeProtocol(
            {"retained_per_run": 1, "runs": 1},
            {"retained_per_run": 10, "runs": 10})
        self.assertEqual(mod10.checkpoint_count_c10([row]), 1)

    def test_cumulative_projection_reads_stored_record(self):
        record = FakeGet(
            {"size": 5, "artefact_class": "a"},
            {"size": 999, "artefact_class": "ghost"})
        result = mod10.cumulative_storage_projection(
            [record], [{"retained_per_run": 1, "runs": 1}])
        self.assertEqual(
            result["retained_actuals_by_artefact_class"], {"a": 5})


class TestR15018(unittest.TestCase):
    def test_transition_figure_reads_stored_replicate(self):
        rep = FakeGet({"first_terminal_regime": "X"},
                      {"competing_exit": True})
        result = mod11.transition_figure([rep])
        self.assertEqual(result["competing_events"], 0)
        self.assertEqual(
            result["cumulative_incidence"]["X"]["count"], 1)

    def test_next_weekly_container_reads_stored_held(self):
        previous = FakeGet({"held_units": []}, {"held_units": ["u1"]})
        result = mod11.next_weekly_container("w1", previous, ["u2"])
        self.assertNotIn("u1", result["headline_units"])
        self.assertIn("u2", result["headline_units"])

    def test_claim_enters_family_reads_stored_claims(self):
        family = FakeGet({"headline_claims": []},
                         {"headline_claims": ["c1"]})
        self.assertFalse(mod11.claim_enters_family(family, "c1", False))


class TestR15019(unittest.TestCase):
    def test_refusal_coverage_reads_stored_record(self):
        record = FakeGet(
            {"contract": "", "slice": "s",
             "enforcing_test": "test_x", "refusal": "r"},
            {"contract": "fabricated"})
        self.assertFalse(mod16.validate_refusal_coverage([record]))

    def test_refusal_coverage_raising_get(self):
        record = RaisingGet(
            {"contract": "c", "slice": "s",
             "enforcing_test": "test_x", "refusal": "r"})
        try:
            result = mod16.validate_refusal_coverage([record])
        except RuntimeError:
            self.fail("raising get escaped bare")
        self.assertTrue(result)


class TestR15020(unittest.TestCase):
    def test_dual_rule_reads_stored_synthetic(self):
        family = FakeGet(
            {"synthetic": False, "retained_under_first_rule": True,
             "retained_under_second_rule": True},
            {"synthetic": True})
        with self.assertRaises(Exception):
            mod14.dual_rule_retention_simulation([family])


class TestR15021(unittest.TestCase):
    def test_divergence_companion_reads_stored_band(self):
        plain = {"viewer_id": "v1", "identity": "i1", "band": "X",
                 "completeness_state": "complete"}
        other = FakeGet(
            {"viewer_id": "v2", "identity": "i1", "band": "X",
             "completeness_state": "complete"},
            {"band": "Z"})
        result = mod04.divergence_companion(components=[plain, other])
        self.assertEqual(result["band_differing_share"], 0.0)
        self.assertEqual(result["differing_identity_count"], 0)


class TestR15022(unittest.TestCase):
    def test_retention_met_conditions_dict_iteration(self):
        conditions = FakeIterDict({9: "x"}, [1, 2, 3])
        record = {
            "later_evaluation": {
                "conditions": conditions, "inputs": "i", "outcome": "o"},
            "summary_record_written": True,
            "retained_forms_pointed_to": True,
        }
        self.assertFalse(mod10.retention_met(record))

    def test_retention_met_plain_control(self):
        record = {
            "later_evaluation": {
                "conditions": [1, 2, 3], "inputs": "i", "outcome": "o"},
            "summary_record_written": True,
            "retained_forms_pointed_to": True,
        }
        self.assertTrue(mod10.retention_met(record))


class TestR15023(unittest.TestCase):
    def test_work_credit_iteration_reads_stored_events(self):
        fake_events = FakeIterList(
            [], [{"agent_identifier": "ghost", "accepted": True}])
        result = mod05.work_credit(fake_events)
        self.assertEqual(result["events_used"], 0)
        self.assertEqual(result["counters"], {})

    def test_recomputation_sample_reads_stored_records(self):
        fake_records = FakeIterList(["r1"], ["r1", "ghost"])
        result = mod05.recomputation_sample(fake_records)
        self.assertEqual(result, ["r1"])


class TestR15024(unittest.TestCase):
    def test_use_naming_reads_stored_uses(self):
        artefact = {"uses_named": ["conformance"]}
        fake_uses = FakeIterList(["assumption"], ["conformance"])
        with self.assertRaises(mod08.SilentUseMovement):
            mod08.validate_use_naming(artefact, fake_uses)


if __name__ == "__main__":
    unittest.main()
