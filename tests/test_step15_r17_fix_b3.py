# Step 15 rerun, fix wave 16, Builder 3 pins.
# Rows R16-036, R16-037, R16-038, R16-056, and R16-057: the copy
# family at MOD-09 and MOD-11, the element copy limb at MOD-07,
# and the MOD-07 joint run recursion family, under settlement S-1.
# Every pin states the standing its register row charges, with
# the proving acts the source papers used.
import unittest

import crucible.mod07 as mod07
import crucible.mod09 as mod09
import crucible.mod11 as mod11


def nested(depth, leaf="x"):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def approved_choice(identifier="c1"):
    return mod07.make_adapter_choice(
        identifier, "reading", "point", "v1", "fold",
        approval={
            "approver": "Project Manager",
            "choice_identifier": identifier,
            "effects": "decision level values",
            "standing": "approved",
        })


def joint_run(choice, **extra):
    run = {
        "adapter_choices": [choice],
        "tracer_passage_records": mod07.tracer_passage_records("r1"),
        "positive_control": mod07.positive_control_record(),
        "cross_seam_effects": [],
    }
    run.update(extra)
    return run


class TestR16036AttackerCostSummaryCopies(unittest.TestCase):
    def test_attacker_cost_copied_apart(self):
        run = {"run_identifier": "w1", "attacker_cost": [100],
               "harm": {}, "regime_classification": "plain"}
        summary = mod09.attacker_cost_summary(run)
        self.assertIsNot(summary["attacker_cost"], run["attacker_cost"])
        run["attacker_cost"].append(999)
        self.assertEqual(summary["attacker_cost"], [100])
        summary["attacker_cost"].append(7)
        self.assertEqual(run["attacker_cost"], [100, 999])

    def test_harm_copied_apart(self):
        run = {"run_identifier": "w1", "attacker_cost": 5,
               "harm": {"nested": [1]}, "regime_classification": "plain"}
        summary = mod09.attacker_cost_summary(run)
        self.assertIsNot(summary["harm"], run["harm"])
        run["harm"]["nested"].append(2)
        self.assertEqual(summary["harm"], {"nested": [1]})

    def test_witness_carriage_composed_summary_copied_apart(self):
        run = {"run_identifier": "w1", "attacker_cost": [100],
               "harm": {}, "regime_classification": "plain"}
        carriage = mod09.witness_carriage(run)
        carried = carriage["attacker_cost_summary"]["attacker_cost"]
        self.assertIsNot(carried, run["attacker_cost"])
        run["attacker_cost"].append(999)
        self.assertEqual(carried, [100])

    def test_plain_summary_control_holds(self):
        run = {"run_identifier": "w1", "attacker_cost": 5, "harm": 3,
               "regime_classification": "plain"}
        summary = mod09.attacker_cost_summary(run)
        self.assertEqual(summary["attacker_cost"], 5)
        self.assertEqual(summary["harm"], 3)
        self.assertEqual(
            summary["standing"], "descriptive figure beside the witness")
        self.assertEqual(summary["classification_before"], "plain")
        self.assertEqual(summary["classification_after"], "plain")


class TestR16037ReporterInputsCopies(unittest.TestCase):
    def test_divergence_count_list_copied_apart(self):
        records = {"divergence_count": [2], "blocked_family_mark": {}}
        inputs = mod11.reporter_inputs_for_family(records)
        self.assertIsNot(
            inputs["divergence_count"], records["divergence_count"])
        records["divergence_count"].append(99)
        self.assertEqual(inputs["divergence_count"], [2])

    def test_divergence_count_dict_copied_apart(self):
        records = {"divergence_count": {"parts": [1]},
                   "blocked_family_mark": {}}
        inputs = mod11.reporter_inputs_for_family(records)
        self.assertIsNot(
            inputs["divergence_count"], records["divergence_count"])
        records["divergence_count"]["parts"].append(2)
        self.assertEqual(inputs["divergence_count"], {"parts": [1]})

    def test_cured_mark_and_scalar_controls_hold(self):
        records = {"divergence_count": 2,
                   "blocked_family_mark": {"share": [1]}}
        inputs = mod11.reporter_inputs_for_family(records)
        self.assertEqual(inputs["divergence_count"], 2)
        self.assertIsNot(
            inputs["blocked_family_mark"], records["blocked_family_mark"])
        records["blocked_family_mark"]["share"].append(2)
        self.assertEqual(
            inputs["blocked_family_mark"], {"share": [1]})


class TestR16038FoldingAndFeedbackPartCopies(unittest.TestCase):
    def test_record_folding_part_copied_apart(self):
        part = {"ruling": ["a"]}
        record = mod07.record_folding(
            {"choice_identifier": "c1"}, [part])
        carried = record["rulings_recorded"][0]
        self.assertIsNot(carried, part)
        part["ruling"].append("b")
        self.assertEqual(carried, {"ruling": ["a"]})

    def test_classify_seam_feedback_part_copied_apart(self):
        part = {"standing": ["a"]}
        record = mod07.classify_seam_feedback(
            "OS-1", {"choice_identifier": "c1"}, [part, {"other": 1}])
        carried = record["both_standings_carried"][0]
        self.assertIsNot(carried, part)
        part["standing"].append("b")
        self.assertEqual(carried, {"standing": ["a"]})

    def test_stored_parts_reading_control_holds(self):
        class LyingList(list):
            def __iter__(self):
                return iter(["DQ-9"])

        record = mod07.record_folding(
            {"choice_identifier": "c1"}, LyingList(["DQ-5"]))
        self.assertEqual(record["rulings_recorded"], ["DQ-5"])


class TestR16056ChoiceApprovalRecursion(unittest.TestCase):
    def cyclic_choice(self):
        first = []
        first.append(first)
        second = []
        second.append(second)
        choice = approved_choice()
        choice["choice_identifier"] = first
        choice["approval"]["choice_identifier"] = second
        return choice

    def test_cyclic_identifier_answers_at_choice_act(self):
        self.assertFalse(mod07.choice_approval_stands(self.cyclic_choice()))

    def test_cyclic_identifier_answers_at_joint_acts(self):
        run = joint_run(self.cyclic_choice())
        self.assertFalse(mod07.validate_joint_run(run))
        self.assertIsNotNone(mod07.joint_run_failure(run))
        self.assertFalse(mod07.seam_headline_claim_stands(run, ["OS-1"]))

    def test_same_cyclic_identifier_object_stands_approved(self):
        cyclic = []
        cyclic.append(cyclic)
        choice = approved_choice()
        choice["choice_identifier"] = cyclic
        choice["approval"]["choice_identifier"] = cyclic
        self.assertTrue(mod07.choice_approval_stands(choice))

    def test_deep_identifier_answers_at_choice_act(self):
        choice = approved_choice()
        choice["choice_identifier"] = nested(600)
        choice["approval"]["choice_identifier"] = nested(600)
        self.assertIsInstance(mod07.choice_approval_stands(choice), bool)

    def test_deep_identifier_answers_at_joint_acts(self):
        choice = approved_choice()
        choice["choice_identifier"] = nested(600)
        choice["approval"]["choice_identifier"] = nested(600)
        run = joint_run(choice)
        self.assertIsInstance(mod07.validate_joint_run(run), bool)
        self.assertIsNotNone(mod07.joint_run_failure(run))
        self.assertFalse(mod07.seam_headline_claim_stands(run, ["OS-1"]))

    def test_plain_controls_hold(self):
        choice = approved_choice()
        self.assertTrue(mod07.choice_approval_stands(choice))
        run = joint_run(choice)
        self.assertTrue(mod07.validate_joint_run(run))
        self.assertIsNone(mod07.joint_run_failure(run))
        self.assertTrue(mod07.seam_headline_claim_stands(run, ["OS-1"]))
        other = approved_choice()
        other["approval"]["choice_identifier"] = "c2"
        self.assertFalse(mod07.choice_approval_stands(other))


class TestR16057StoredPairFallbackRefusal(unittest.TestCase):
    def deep_marks_choice(self):
        choice = approved_choice()
        choice["dependence_marks"] = nested(150)
        return choice

    def stored_entry(self, builder, marks):
        entry = builder(approved_choice())
        entry["dependence_marks"] = marks
        return entry

    def assert_joint_acts_answer(self, run):
        self.assertFalse(mod07.validate_joint_run(run))
        failure = mod07.joint_run_failure(run)
        self.assertIsNotNone(failure)
        self.assertFalse(mod07.seam_headline_claim_stands(run, ["OS-1"]))

    def test_deep_marks_no_side_stored_answers(self):
        self.assert_joint_acts_answer(joint_run(self.deep_marks_choice()))

    def test_deep_marks_one_log_side_stored_answers(self):
        entry = self.stored_entry(
            mod07.interpretation_log_entry, nested(150))
        run = joint_run(
            self.deep_marks_choice(), interpretation_log_entries=[entry])
        self.assert_joint_acts_answer(run)

    def test_deep_marks_one_run_side_stored_answers(self):
        entry = self.stored_entry(mod07.run_record_entry, nested(150))
        run = joint_run(
            self.deep_marks_choice(), run_record_entries=[entry])
        self.assert_joint_acts_answer(run)

    def test_cyclic_marks_no_side_stored_answers(self):
        cyclic = []
        cyclic.append(cyclic)
        choice = approved_choice()
        choice["dependence_marks"] = cyclic
        self.assert_joint_acts_answer(joint_run(choice))

    def test_both_sides_stored_controls_hold(self):
        log_entry = self.stored_entry(
            mod07.interpretation_log_entry, nested(150))
        run_entry = self.stored_entry(mod07.run_record_entry, nested(150))
        run = joint_run(
            self.deep_marks_choice(),
            interpretation_log_entries=[log_entry],
            run_record_entries=[run_entry])
        self.assert_joint_acts_answer(run)

    def test_plain_no_side_control_holds(self):
        run = joint_run(approved_choice())
        self.assertTrue(mod07.validate_joint_run(run))
        self.assertIsNone(mod07.joint_run_failure(run))
        self.assertTrue(mod07.seam_headline_claim_stands(run, ["OS-1"]))


if __name__ == "__main__":
    unittest.main()
