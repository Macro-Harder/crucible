"""Step 15 fix wave 11, Builder 6 pins.

Rows R11-071 to R11-080: the handed readings Yellow 2 charged at
MOD-13, MOD-09, MOD-08, and the MOD-10 and MOD-12 limbs of its
Finding 9. Every pin uses the exact proving act form of the
Yellow 2 paper: a dict or list subclass that stores one set of
contents and reports another through its own get, contains,
item, iteration, length, truth, or equality reading, against
plain controls standing both ways. Stored contents govern.
"""
import unittest

import crucible.mod08 as mod08
import crucible.mod09 as mod09
import crucible.mod10 as mod10
import crucible.mod12 as mod12
import crucible.mod13 as mod13


class GetLieDict(dict):
    """Stores stored, reports reported through get."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)


class FullLieDict(dict):
    """Stores stored, reports reported through get, contains,
    and item readings."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)

    def __contains__(self, key):
        return dict.__contains__(self._reported, key)

    def __getitem__(self, key):
        return dict.__getitem__(self._reported, key)


class BoolLieDict(dict):
    """Stores stored, reports itself empty through truth."""

    def __bool__(self):
        return False


class IterLieList(list):
    """Stores stored, iterates as reported."""

    def __init__(self, stored, reported):
        list.__init__(self, stored)
        self._reported = reported

    def __iter__(self):
        return list.__iter__(self._reported)


class ContainsLieList(list):
    """Stores stored, reports every name as contained."""

    def __contains__(self, item):
        return True


class LenLieList(list):
    """Stores stored, reports a lying length."""

    def __init__(self, stored, reported_len):
        list.__init__(self, stored)
        self._reported_len = reported_len

    def __len__(self):
        return self._reported_len


class LenLieDict(dict):
    """Stores stored, reports a lying length."""

    def __init__(self, stored, reported_len):
        dict.__init__(self, stored)
        self._reported_len = reported_len

    def __len__(self):
        return self._reported_len


class FormLieList(list):
    """Stores stored, reports horizon absent, iterates as the
    daily form, for the aggregate form act."""

    def __init__(self, stored, reported):
        list.__init__(self, stored)
        self._reported = reported

    def __contains__(self, item):
        return False

    def __iter__(self):
        return list.__iter__(self._reported)


def _carriage(strategies=("conditional briber",)):
    return mod09.run_record_carriage(
        ["conditional briber"], 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategies))


def _record():
    return mod09.build_search_record(
        _carriage(), points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": "no failure"}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2,
                              "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=[0, 5])


class TestR11071Mod13Claims(unittest.TestCase):

    def test_replay_claim_stored_barred_fails(self):
        plain = {"hash_equality_claimed": True}
        self.assertFalse(mod13.validate_replay_claim(plain))
        lying = GetLieDict(
            {"hash_equality_claimed": True},
            {"hash_equality_claimed": False})
        self.assertFalse(mod13.validate_replay_claim(lying))
        plain_clean = {"hash_equality_claimed": False}
        self.assertTrue(mod13.validate_replay_claim(plain_clean))

    def test_replay_claim_mirror(self):
        lying = GetLieDict(
            {"hash_equality_claimed": False},
            {"hash_equality_claimed": True})
        self.assertTrue(mod13.validate_replay_claim(lying))

    def test_replay_claim_completeness_stored_barred_fails(self):
        lying = GetLieDict(
            {"detection_state_completeness_claimed": True},
            {"detection_state_completeness_claimed": False})
        self.assertFalse(mod13.validate_replay_claim(lying))

    def test_resume_claim_stored_barred_fails(self):
        plain = {
            "detection_scope": "state level",
            "detection_comparison_points": ["foreign point"],
        }
        self.assertFalse(mod13.validate_resume_claim(plain))
        lying = GetLieDict(plain, {
            "detection_scope": "verdict level only",
            "detection_comparison_points":
                list(mod13.DETECTION_COMPARISON_POINTS),
        })
        self.assertFalse(mod13.validate_resume_claim(lying))
        plain_clean = {
            "detection_scope": "verdict level only",
            "detection_comparison_points":
                list(mod13.DETECTION_COMPARISON_POINTS),
        }
        self.assertTrue(mod13.validate_resume_claim(plain_clean))

    def test_resume_claim_points_list_reading(self):
        claim = {
            "detection_scope": "verdict level only",
            "detection_comparison_points": IterLieList(
                ["foreign point"],
                list(mod13.DETECTION_COMPARISON_POINTS)),
        }
        self.assertFalse(mod13.validate_resume_claim(claim))

    def test_probe_claim_stored_barred_fails(self):
        plain = {"margin_or_method_presented_as_settled": True}
        self.assertFalse(mod13.validate_probe_claim(plain))
        lying = GetLieDict(
            plain, {"margin_or_method_presented_as_settled": False})
        self.assertFalse(mod13.validate_probe_claim(lying))
        lying2 = GetLieDict(
            {"catalogue_presented_as_settled": True},
            {"catalogue_presented_as_settled": False})
        self.assertFalse(mod13.validate_probe_claim(lying2))
        self.assertTrue(mod13.validate_probe_claim(
            {"margin_or_method_presented_as_settled": False}))


class TestR11072Mod13DetectionOutput(unittest.TestCase):

    def _complete(self):
        return {
            "run_identifier": "run-1",
            "scoring_day_range": [1, 2],
            "verdict_states_and_accumulator_updates": {"v": 1},
        }

    def test_is_detection_output_stored_empty_fails(self):
        self.assertFalse(mod13._is_detection_output({}))
        self.assertTrue(
            mod13._is_detection_output(self._complete()))
        lying = FullLieDict({}, self._complete())
        self.assertFalse(mod13._is_detection_output(lying))

    def test_score_detection_outputs_stored_empty_raises(self):
        supplied = {
            "authored_by": "author", "knowledge": "known",
            "records_position": "outside",
        }
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.score_detection_outputs([{}], **supplied)
        result = mod13.score_detection_outputs(
            [self._complete()], **supplied)
        self.assertEqual(result["outputs_scored"], 1)
        lying = FullLieDict({}, self._complete())
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.score_detection_outputs([lying], **supplied)


class TestR11073Mod13WitnessRerun(unittest.TestCase):

    def test_witness_rerun_stored_linkage(self):
        plain = {"run_id": "R9", "rule_set_version": "v2"}
        rerun = mod13.witness_rerun(plain)
        self.assertEqual(rerun["run_id"], "R9-rerun")
        self.assertEqual(rerun["linked_to"], "R9")
        self.assertEqual(
            rerun["original_rule_set_version"], "v2")
        lying = GetLieDict(
            {"run_id": "STORED", "rule_set_version": "vStored"},
            {"run_id": "REPORTED", "rule_set_version": "vRep"})
        rerun = mod13.witness_rerun(lying)
        self.assertEqual(rerun["run_id"], "STORED-rerun")
        self.assertEqual(rerun["linked_to"], "STORED")
        self.assertEqual(
            rerun["original_rule_set_version"], "vStored")

    def test_witness_rerun_truth_lie_uses_stored(self):
        lying = BoolLieDict(
            {"run_id": "STORED", "rule_set_version": "vStored"})
        rerun = mod13.witness_rerun(lying)
        self.assertEqual(rerun["run_id"], "STORED-rerun")
        self.assertEqual(rerun["linked_to"], "STORED")


class TestR11074Mod13AggregateForm(unittest.TestCase):

    def test_aggregate_form_stored_horizon_fails(self):
        daily = mod13.daily_aggregate_form()
        self.assertTrue(mod13.validate_aggregate_form(daily))
        self.assertFalse(
            mod13.validate_aggregate_form(daily + ["horizon"]))
        lying = FormLieList(daily + ["horizon"], daily)
        self.assertFalse(mod13.validate_aggregate_form(lying))


class TestR11075Mod09Subcontainers(unittest.TestCase):

    def test_strategy_class_contains_lie(self):
        record = _record()
        self.assertTrue(mod09.validate_search_record(record))
        record["run_record"]["strategy_class"] = ContainsLieList(
            ["conditional briber"])
        record["run_record"]["strategies_exercised"] = [
            "outside strategy"]
        self.assertFalse(mod09.validate_search_record(record))

    def test_strategies_exercised_iteration_lie(self):
        record = _record()
        record["run_record"]["strategies_exercised"] = IterLieList(
            ["outside strategy"], [])
        self.assertFalse(mod09.validate_search_record(record))

    def test_case_uses_iteration_lie(self):
        record = _record()
        record["case_uses"] = IterLieList([{
            "fixture": "F-26",
            "use": "deployed failure case use",
        }], [])
        self.assertFalse(mod09.validate_search_record(record))
        plain_bad = _record()
        plain_bad["case_uses"] = [{
            "fixture": "F-26",
            "use": "deployed failure case use",
        }]
        self.assertFalse(mod09.validate_search_record(plain_bad))

    def test_mid_run_strategies_length_lie(self):
        record = _record()
        record["mid_run_strategies"] = LenLieList(
            ["introduced strategy"], 0)
        self.assertFalse(mod09.validate_search_record(record))

    def test_bond_parameter_set_length_lie(self):
        record = _record()
        record["bond_parameter_search"]["parameter_set"] = (
            LenLieDict({}, 1))
        self.assertFalse(mod09.validate_search_record(record))


class TestR11076Mod09Computation(unittest.TestCase):

    def test_attacker_payoff_stored_empty_raises(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff({}, 3)
        lying = FullLieDict({}, {"in_protocol_payoff": 5})
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(lying, 3)
        plain = mod09.make_strategy(
            "conditional briber", in_protocol_payoff=5)
        self.assertEqual(mod09.attacker_payoff(plain, 3), 8)

    def test_sweep_stored_empty_raises(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.sweep_external_profit({})
        lying = FullLieDict({}, {
            "external_profit_range": [0, 10],
            "in_protocol_payoff": 1,
        })
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.sweep_external_profit(lying)

    def test_bond_search_stored_empty_raises(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search([{}])
        lying = GetLieDict({}, {
            "parameter_set": {"lien multiplier": 2},
            "attacker_cost": 1, "harm": 10,
        })
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search([lying])

    def test_build_search_record_from_lying_candidate_raises(self):
        lying = GetLieDict({}, {
            "parameter_set": {"lien multiplier": 2},
            "attacker_cost": 1, "harm": 10,
        })
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.build_search_record(
                _carriage(), points_tried=["point one"],
                per_point_outcome=[{"point": "point one",
                                    "outcome": "no failure"}],
                bond_candidates=[lying],
                budget="stated budget",
                neighbourhood={"definition": "adjacent points",
                               "step sizes": [1]},
                starting_points=["point zero"],
                order_of_search=["point one"],
                external_profit_swept_values=[0, 5])


class TestR11077Mod09Readout(unittest.TestCase):

    def test_readout_stored_empty(self):
        plain = mod09.readout({})
        self.assertEqual(
            plain["readout_status"], "not at the readout point")
        self.assertEqual(
            plain["result_kind"], "in protocol result only")
        carriage = {
            "ladder_position": 6,
            "strategies_exercised": ["conditional briber"],
        }
        lying = GetLieDict({}, {
            "run_record": carriage,
            "external_profit_swept_values": [5],
        })
        result = mod09.readout(lying)
        self.assertEqual(
            result["readout_status"], "not at the readout point")
        self.assertEqual(
            result["result_kind"], "in protocol result only")


class TestR11078Mod09Witness(unittest.TestCase):

    def test_attacker_cost_summary_stored_empty(self):
        plain = mod09.attacker_cost_summary({})
        self.assertIsNone(plain["attacker_cost"])
        self.assertIsNone(plain["harm"])
        lying = GetLieDict({}, {
            "run_identifier": "reported-run",
            "attacker_cost": 99, "harm": 99,
            "regime_classification": "reported class",
        })
        summary = mod09.attacker_cost_summary(lying)
        self.assertIsNone(summary["witness_run"])
        self.assertIsNone(summary["attacker_cost"])
        self.assertIsNone(summary["harm"])
        self.assertIsNone(summary["classification_before"])
        self.assertIsNone(summary["classification_after"])
        carriage = mod09.witness_carriage(lying)
        self.assertIsNone(carriage["witness_run"])
        self.assertIsNone(carriage["regime_classification"])
        self.assertIsNone(
            carriage["attacker_cost_summary"]["attacker_cost"])


class TestR11079RunRecords(unittest.TestCase):

    def test_mod12_validate_run_record_get_lie(self):
        plain_barred = {
            "run_class": "confirmation",
            "seed_domain": "screening",
        }
        self.assertFalse(mod12.validate_run_record(plain_barred))
        plain_lawful = {
            "run_class": "screening",
            "seed_domain": "screening",
        }
        self.assertTrue(mod12.validate_run_record(plain_lawful))
        lying = GetLieDict(plain_barred, plain_lawful)
        self.assertFalse(mod12.validate_run_record(lying))

    def test_mod10_validate_run_record_set_get_lie(self):
        self.assertFalse(mod10.validate_run_record_set([{}]))
        owned = {"run_id": "run-b6", "group_writers": {}}
        self.assertTrue(mod10.validate_run_record_set([owned]))
        lying = GetLieDict({}, {
            "run_id": "run-b6", "group_writers": {},
        })
        self.assertFalse(mod10.validate_run_record_set([lying]))


class TestR11080Mod08AuthorSealed(unittest.TestCase):

    def _sealed_set(self):
        return {
            "detector_frozen": True,
            "sealed": False,
            "scoring_closed": True,
            "stage": "unsealed after scoring closed",
            "authored": [],
        }

    def test_author_sealed_class_get_lie(self):
        plain = self._sealed_set()
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                plain, "sleeper class", "sleeper-1",
                separations=("authorship separation", "knowledge separation",
                             "record separation"))
        self.assertEqual(plain["authored"], [])
        lying = GetLieDict(self._sealed_set(), {
            "detector_frozen": True,
            "sealed": False,
            "scoring_closed": False,
            "stage": "frozen",
            "authored": [],
        })
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                lying, "sleeper class", "sleeper-1",
                separations=("authorship separation", "knowledge separation",
                             "record separation"))
        stored_authored = dict.__getitem__(lying, "authored")
        self.assertEqual(stored_authored, [])


if __name__ == "__main__":
    unittest.main()
