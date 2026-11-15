# Step 15 rerun, fix wave 13, Builder 3 pins.
# Rows R13-010 to R13-016, R13-025, and R13-043: the MOD-07 and
# MOD-12 joint run, companion, readout, choice pair, and sample
# family. Every pin states the standing the register charges,
# with the proving acts the source papers used.
import unittest

import crucible.mod07 as mod07
import crucible.mod12 as mod12


class AlwaysEq:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


def valid_run():
    return {
        "adapter_choices": [],
        "tracer_passage_records": mod07.tracer_passage_records("r1"),
        "positive_control": mod07.positive_control_record(),
        "cross_seam_effects": [],
    }


def complete_readout():
    return {
        "claim_in_bounding_form": True,
        "bound_fixed_in_advance": True,
        "search_complete": True,
        "material_failure_found": False,
        "search_completed_at_rung": 6,
        "tolerance_and_replication_rule": True,
        "confirmation_under_family_discipline": True,
        "assumption_set_and_rows_inside_result": True,
        "check_artefact_battery": {"passed": [
            "A-01", "A-02", "A-03", "A-04", "A-05", "A-06",
            "A-07", "A-08", "A-09", "A-10", "A-11"]},
    }


class TestR13010JointRunSingleRecordEffect(unittest.TestCase):
    def test_dict_settled_effect_fails_and_no_headline(self):
        run = valid_run()
        run["cross_seam_effects"] = {
            "kind": "vouch lien", "lien_state": "settled"}
        self.assertFalse(mod07.validate_joint_run(run))
        failure = mod07.joint_run_failure(run)
        self.assertIsNotNone(failure)
        self.assertEqual(
            failure["name"], "cross seam effect carries settled wording")
        self.assertFalse(
            mod07.seam_headline_claim_stands(run, ["OS-1"]))

    def test_dict_lawful_effect_and_other_no_list_forms_fail(self):
        for effects in (
                {"lien_state": "computed not settled"},
                "settled wording text", 42):
            run = valid_run()
            run["cross_seam_effects"] = effects
            self.assertFalse(mod07.validate_joint_run(run), repr(effects))
            self.assertIsNotNone(
                mod07.joint_run_failure(run), repr(effects))
            self.assertFalse(
                mod07.seam_headline_claim_stands(run, ["OS-1"]),
                repr(effects))

    def test_list_controls(self):
        run = valid_run()
        run["cross_seam_effects"] = [{"lien_state": "settled"}]
        self.assertEqual(
            mod07.joint_run_failure(run)["name"],
            "cross seam effect carries settled wording")
        self.assertIsNone(mod07.joint_run_failure(valid_run()))
        self.assertTrue(
            mod07.seam_headline_claim_stands(valid_run(), ["OS-1"]))
        run2 = valid_run()
        run2["cross_seam_effects"] = {
            "kind": "vouch lien", "lien_state": "settled"}
        self.assertIsNotNone(mod07.joint_run_failure(run2))


class TestR13011AdapterChoicesSetForm(unittest.TestCase):
    def test_empty_set_and_frozenset_stand(self):
        for choices in (set(), frozenset()):
            run = valid_run()
            run["adapter_choices"] = choices
            self.assertTrue(mod07.validate_joint_run(run), repr(choices))
            self.assertIsNone(mod07.joint_run_failure(run), repr(choices))
            self.assertTrue(
                mod07.seam_headline_claim_stands(run, ["OS-1"]),
                repr(choices))


class TestR13012DependencyRecordEdgeDress(unittest.TestCase):
    def test_barred_edge_in_bytes_and_mixed_dress(self):
        for edges in (
                [(b"MOD-05", b"MOD-06")],
                [(b"MOD-05", "MOD-06")],
                [("MOD-05", b"MOD-06")],
                [(memoryview(b"MOD-05"), memoryview(b"MOD-06"))]):
            record = {"edges": edges, "joint_dependent": "MOD-07"}
            self.assertFalse(
                mod07.validate_dependency_record(record), repr(edges))
        self.assertFalse(mod07.validate_dependency_record(
            {"edges": [("MOD-05", "MOD-06")],
             "joint_dependent": "MOD-07"}))
        self.assertTrue(
            mod07.validate_dependency_record(mod07.dependency_record()))

    def test_unhashable_edge_parts_return_false(self):
        for edges in (
                [(bytearray(b"MOD-05"), bytearray(b"MOD-06"))],
                [(["MOD-0", "5"], ["MOD-0", "6"])]):
            record = {"edges": edges, "joint_dependent": "MOD-07"}
            self.assertFalse(
                mod07.validate_dependency_record(record), repr(edges))

    def test_bytes_joint_dependent_and_joint_edges_in_dress(self):
        self.assertTrue(mod07.validate_dependency_record(
            {"edges": [], "joint_dependent": b"MOD-07"}))
        self.assertFalse(mod07.validate_dependency_record(
            {"edges": [(b"MOD-05", b"MOD-08"), (b"MOD-06", b"MOD-08")],
             "joint_dependent": "MOD-07"}))
class TestR13013TracerRecordsNoListForm(unittest.TestCase):
    def test_text_number_and_bytes_forms_named_no_list_form(self):
        for records in ("some text", 5, 5.5, b"bytes"):
            run = valid_run()
            run["tracer_passage_records"] = records
            failure = mod07.joint_run_failure(run)
            self.assertIsNotNone(failure, repr(records))
            self.assertEqual(
                failure["name"],
                "joint run tracer passage records stand in no list "
                "form fails", repr(records))

    def test_absent_and_dict_controls(self):
        run = valid_run()
        del run["tracer_passage_records"]
        self.assertEqual(
            mod07.joint_run_failure(run)["name"],
            "joint run missing a tracer passage record fails")
        run2 = valid_run()
        run2["tracer_passage_records"] = {"OS-1": "x"}
        self.assertEqual(
            mod07.joint_run_failure(run2)["name"],
            "joint run tracer passage records stand in no list "
            "form fails")
        run3 = valid_run()
        run3["tracer_passage_records"] = "some text"
        self.assertEqual(
            mod07.joint_run_failure(run3)["name"],
            "joint run tracer passage records stand in no list "
            "form fails")


class TestR13014FamilyRecordCompanion(unittest.TestCase):
    def faults(self):
        ecology = mod12.make_family_record()
        ecology["ecology_point"] = "fixed"
        ecology.pop("amendment_landed", None)
        top_up = mod12.make_family_record()
        top_up["data_dependent_top_up"] = "stated top up"
        top_up.pop("look_register", None)
        sealed = mod12.make_family_record()
        sealed["sealed"] = True
        sealed["edited_after_seal"] = True
        sealed.pop("identifier_changed", None)
        kill = mod12.make_family_record()
        ghost = [{"claim": "ghost-claim"}]
        kill["kill_check_fields"] = list(ghost)
        kill["kill_checks"] = list(ghost)
        return (ecology, top_up, sealed, kill)

    def test_four_gates_named_by_companion(self):
        for record in self.faults():
            self.assertFalse(mod12.validate_family_record(record))
            self.assertTrue(
                mod12.family_record_validation_failures(record),
                repr(record.get("ecology_point")))

    def test_companion_names_each_gate_and_control_stays_empty(self):
        names = []
        for record in self.faults():
            names.extend(mod12.family_record_validation_failures(record))
        joined = " ".join(names)
        self.assertIn("ecology", joined)
        self.assertIn("top up", joined)
        self.assertIn("identifier", joined)
        self.assertIn("kill check", joined)
        self.assertEqual(
            mod12.family_record_validation_failures(
                mod12.make_family_record()), [])


class TestR13015ReadoutRungDefault(unittest.TestCase):
    def test_absent_rung_fails_condition_2(self):
        readout = complete_readout()
        del readout["search_completed_at_rung"]
        status = mod12.readout_status(readout)
        self.assertEqual(status["form"], "lower_bound")
        self.assertIn(2, status["unmet_conditions"])
        readout2 = complete_readout()
        readout2["search_completed_at_rung"] = 6.0
        self.assertEqual(
            mod12.readout_status(readout2)["form"], "lower_bound")
        self.assertEqual(
            mod12.readout_status(complete_readout())["form"],
            "established")


class TestR13016ReadoutBatteryCount(unittest.TestCase):
    def test_duplicate_marks_do_not_pad_to_eleven(self):
        readout = complete_readout()
        readout["check_artefact_battery"] = {"passed": [
            "A-04", "A-05", "A-09", "A-10", "A-11",
            "A-04", "A-04", "A-04", "A-04", "A-04", "A-04"]}
        status = mod12.readout_status(readout)
        self.assertEqual(status["form"], "lower_bound")
        self.assertIn(5, status["unmet_conditions"])
        self.assertEqual(
            mod12.readout_status(complete_readout())["form"],
            "established")

    def test_entries_naming_no_check_do_not_pad(self):
        readout = complete_readout()
        readout["check_artefact_battery"] = {"passed": [
            "A-04", "A-05", "A-09", "A-10", "A-11",
            "junk", "junk", "junk", "junk", "junk", "junk"]}
        status = mod12.readout_status(readout)
        self.assertEqual(status["form"], "lower_bound")
        self.assertIn(5, status["unmet_conditions"])

    def test_bare_true_battery_meets_nothing(self):
        readout = complete_readout()
        readout["check_artefact_battery"] = True
        status = mod12.readout_status(readout)
        self.assertEqual(status["form"], "lower_bound")
        self.assertIn(5, status["unmet_conditions"])


class TestR13025ChoicePairDependenceMarks(unittest.TestCase):
    def entries(self, log_marks, run_marks):
        base = {"choice_identifier": "c1", "reading_applied": "r",
                "governing_text_version": "v"}
        log_entry = dict(base)
        log_entry["dependence_marks"] = log_marks
        run_entry = dict(base)
        run_entry["dependence_marks"] = run_marks
        return log_entry, run_entry

    def test_equality_lying_mark_on_log_side(self):
        log_entry, run_entry = self.entries(
            [AlwaysEq()], ["completely different"])
        self.assertFalse(mod07.validate_choice_pair(log_entry, run_entry))
        plain_log, plain_run = self.entries(["a"], ["b"])
        self.assertFalse(mod07.validate_choice_pair(plain_log, plain_run))
        same_log, same_run = self.entries(["a"], ["a"])
        self.assertTrue(mod07.validate_choice_pair(same_log, same_run))

    def test_equality_lying_mark_on_run_side(self):
        log_entry, run_entry = self.entries(
            ["completely different"], [AlwaysEq()])
        self.assertFalse(mod07.validate_choice_pair(log_entry, run_entry))


class TestR13043SampleStatement(unittest.TestCase):
    def test_class_only_record_counts_no_run(self):
        result = mod12.sample_statement([{"run_class": "screening"}])
        self.assertEqual(result["n"], 0)
        self.assertEqual(
            result["runs_completed_by_class"]["screening"], 0)
        self.assertEqual(result["sample"], "none")

    def test_same_run_handed_twice_counts_once(self):
        run = {"run_class": "screening", "run_id": "r1",
               "seed_domain": "screening domain"}
        result = mod12.sample_statement([run, dict(run)])
        self.assertEqual(result["n"], 1)
        self.assertEqual(
            result["runs_completed_by_class"]["screening"], 1)
        self.assertEqual(result["sample"].count("r1"), 1)
        other = {"run_class": "headline", "run_id": "r2",
                 "seed_domain": "held out"}
        result2 = mod12.sample_statement([run, other])
        self.assertEqual(result2["n"], 2)

    def test_run_identifier_field_counts_and_dedupes(self):
        run = {"run_class": "validation", "run_identifier": "v1",
               "seed_domain": "held out"}
        result = mod12.sample_statement([run, dict(run)])
        self.assertEqual(result["n"], 1)
        self.assertEqual(
            result["runs_completed_by_class"]["validation"], 1)
        self.assertIn("v1", result["sample"])


if __name__ == "__main__":
    unittest.main()
