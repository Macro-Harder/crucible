"""Step 17 fix wave 3, Slice 12 defect tests for row FW3-54.

The public act argument escape family across modules: a named
public act handed a missing or extra argument must deliver
that handing in the named form of its module, the refusal form
its sibling doors speak, or the judged form the act itself
answers in, and never as bare interpreter text of the form
"missing 1 required positional argument" or "takes 0
positional arguments but 1 was given". The handings stand as
the Round 2 filing R2O5-03 states them, act by act.
"""
import unittest

from crucible import mod06, mod07, mod09, mod11, mod13


def bare_escape(exc):
    text = str(exc)
    return ("required positional argument" in text
            or "positional arguments but" in text
            or "takes 0 positional" in text)


class TestMod06ArgumentEscape(unittest.TestCase):
    def test_defect_enter_ruling_missing_arguments(self):
        with self.assertRaises(ValueError) as caught:
            mod06.enter_ruling(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("enter_ruling stands refused",
                      str(caught.exception))

    def test_control_enter_ruling_full(self):
        rows = [{"item": "i1", "standing": "open",
                 "final_column": ""}]
        updated = mod06.enter_ruling(rows, "i1", "ruled text")
        self.assertEqual(updated[0]["final_column"], "ruled text")


class TestMod07ArgumentEscape(unittest.TestCase):
    def test_defect_make_adapter_choice_missing_arguments(self):
        with self.assertRaises(ValueError) as caught:
            mod07.make_adapter_choice(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("make_adapter_choice stands refused",
                      str(caught.exception))

    def test_defect_seam_status_extra_argument(self):
        with self.assertRaises(ValueError) as caught:
            mod07.seam_status(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("seam_status stands refused",
                      str(caught.exception))

    def test_defect_reading_for_result_missing_argument(self):
        with self.assertRaises(ValueError) as caught:
            mod07.reading_for_result(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("reading_for_result stands refused",
                      str(caught.exception))

    def test_control_make_adapter_choice_full(self):
        record = mod07.make_adapter_choice(
            "choice-1", "reading one", "point one", "text v1",
            "variant one")
        self.assertEqual(record["recorded_as"], "adapter choice")
        self.assertEqual(record["choice_identifier"], "choice-1")

    def test_control_seam_status_no_argument(self):
        result = mod07.seam_status()
        self.assertIn("seam_status", result)

    def test_control_reading_for_result_full(self):
        log = [{"choice_identifier": "c1", "reading": "r"}]
        self.assertEqual(
            mod07.reading_for_result(log, "c1")["reading"], "r")
        self.assertIsNone(mod07.reading_for_result(log, "absent"))


class TestMod09ArgumentEscape(unittest.TestCase):
    def _carriage(self):
        return mod09.run_record_carriage(
            ["conditional briber"], 6, "catalogue version 1",
            "ladder definition pointer", "ladder version 1",
            strategies=["conditional briber"])

    def _record_kwargs(self):
        return dict(
            points_tried=["point one"],
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

    def test_defect_build_search_record_missing_arguments(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.build_search_record(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("search record rejected",
                      str(caught.exception))

    def test_defect_run_search_missing_arguments(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.run_search(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("search record rejected",
                      str(caught.exception))

    def test_defect_search_missing_arguments(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.search(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("search record rejected",
                      str(caught.exception))

    def test_defect_attacker_payoff_missing_argument(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("attacker payoff rejected",
                      str(caught.exception))

    def test_control_build_search_record_full(self):
        record = mod09.build_search_record(
            self._carriage(), **self._record_kwargs())
        self.assertIn("search_record", record)

    def test_control_run_search_full(self):
        record = mod09.run_search(
            self._carriage(), **self._record_kwargs())
        self.assertIn("search_record", record)

    def test_control_search_full(self):
        record = mod09.search(
            self._carriage(), **self._record_kwargs())
        self.assertIn("search_record", record)

    def test_control_attacker_payoff_full(self):
        self.assertEqual(
            mod09.attacker_payoff({"in_protocol_payoff": 3}, 4), 7)


class TestMod11ArgumentEscape(unittest.TestCase):
    def test_defect_build_headline_unit_from_run_missing_values(self):
        with self.assertRaises(ValueError) as caught:
            mod11.build_headline_unit_from_run(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn(
            "build_headline_unit_from_run stands refused",
            str(caught.exception))

    def test_defect_judge_registry_entry_missing_arguments(self):
        with self.assertRaises(ValueError) as caught:
            mod11.judge_registry_entry({})
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("judge_registry_entry stands refused",
                      str(caught.exception))

    def test_defect_classify_run_outcome_missing_argument(self):
        with self.assertRaises(ValueError) as caught:
            mod11.classify_run_outcome(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("classify_run_outcome stands refused",
                      str(caught.exception))

    def test_defect_weekly_count_missing_argument(self):
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("weekly_count stands refused",
                      str(caught.exception))

    def test_defect_honest_loss_rate_missing_argument(self):
        with self.assertRaises(ValueError) as caught:
            mod11.honest_loss_rate_h1(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("honest_loss_rate_h1 stands refused",
                      str(caught.exception))

    def test_defect_claim_enters_family_missing_argument(self):
        self.assertFalse(mod11.claim_enters_family(None, None))

    def test_control_build_headline_unit_from_run_absent_run(self):
        result = mod11.build_headline_unit_from_run(
            "run-fw354-absent", {})
        self.assertFalse(result["built"])
        self.assertIsNone(result["unit"])

    def test_control_judge_registry_entry_full(self):
        entry = {"phase_judgements": {
            "before_runs": "judged", "after_runs": "judged"}}
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar",
            checker="independent checker")
        self.assertEqual(judged["before_runs_judged_for"],
                         "lateness")
        self.assertFalse(judged["compared_against_run_log"])

    def test_control_classify_run_outcome_full(self):
        result = mod11.classify_run_outcome(30, "steady")
        self.assertEqual(result["outcome"], "steady")

    def test_control_weekly_count_full(self):
        records = [{"week": 3,
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod11.weekly_count(records, 3), 1)

    def test_control_honest_loss_rate_full(self):
        result = mod11.honest_loss_rate_h1(10, 10)
        self.assertEqual(result["numerator"], 0)
        self.assertEqual(result["denominator"], 10)

    def test_control_claim_enters_family_full(self):
        family = {"headline_claims": ["claim one"]}
        self.assertTrue(mod11.claim_enters_family(
            family, "claim one", False))
        self.assertFalse(mod11.claim_enters_family(
            family, "claim one", True))


class TestMod13ArgumentEscape(unittest.TestCase):
    def test_defect_publishable_on_replication_missing_argument(self):
        self.assertFalse(mod13.publishable_on_replication(None))

    def test_defect_resume_check_missing_argument(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.resume_check(None)
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("resume check", str(caught.exception))

    def test_control_publishable_on_replication_full(self):
        self.assertFalse(
            mod13.publishable_on_replication("claim one", None))

    def test_control_resume_check_full(self):
        result = mod13.resume_check({}, {})
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
