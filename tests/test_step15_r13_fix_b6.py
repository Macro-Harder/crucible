# Step 15 rerun, fix wave 12, Builder 6 pins.
# Rows R12-034 to R12-043: MOD-07 and MOD-12 handed readings.
# Every pin hands a value whose stored contents and reported
# readings differ, and states that the act under cure reads the
# stored contents, never the handed reading.
import unittest

import crucible.mod07 as mod07
import crucible.mod12 as mod12


class LyingGetDict(dict):
    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)


class LyingGetItemDict(dict):
    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)

    def __getitem__(self, key):
        return dict.__getitem__(self._reported, key)


class LyingGetOnlyDict(dict):
    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)


class LyingList(list):
    def __init__(self, stored, reported):
        list.__init__(self, stored)
        self._reported = list(reported)

    def __iter__(self):
        return iter(self._reported)

    def __len__(self):
        return len(self._reported)

    def __contains__(self, item):
        return item in self._reported


class AlwaysEq:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash("screening")


class EqStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash("screening")


class FalsyStr(str):
    def __bool__(self):
        return False


class TruthyStr(str):
    def __bool__(self):
        return True


class TruthyObj:
    def __bool__(self):
        return True


class HashKey(str):
    def __new__(cls, stored):
        obj = str.__new__(cls, stored)
        obj._unrelated = "zzz-unrelated-" + stored
        return obj

    def __hash__(self):
        return hash(self._unrelated)

    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        return str.__eq__(self._unrelated, str.__str__(other))

    def __ne__(self, other):
        return not self.__eq__(other)


class DeepcopyLeaf:
    def __deepcopy__(self, memo):
        return "LIE"


def valid_choice():
    return mod07.make_adapter_choice(
        "choice-1", "reading A", "point", "gov v1", "fold v1",
        approval={"approver": "Project Manager",
                  "choice_identifier": "choice-1",
                  "effects": ["effect one"],
                  "standing": "approved"})


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


def failing_readout():
    return {
        "claim_in_bounding_form": False,
        "bound_fixed_in_advance": False,
        "search_complete": False,
        "material_failure_found": True,
        "search_completed_at_rung": 5,
        "tolerance_and_replication_rule": False,
        "confirmation_under_family_discipline": False,
        "assumption_set_and_rows_inside_result": False,
        "check_artefact_battery": {"passed": []},
    }


class TestR12034JointRunFailure(unittest.TestCase):
    def test_settled_effect_reported_clean(self):
        stored = valid_run()
        stored["tracer_passage_records"] = []
        stored["positive_control"] = None
        stored["cross_seam_effects"] = [{"lien_state": "settled"}]
        lying = LyingGetDict(stored, valid_run())
        self.assertFalse(mod07.validate_joint_run(stored))
        self.assertIsNotNone(mod07.joint_run_failure(lying))
        self.assertFalse(
            mod07.seam_headline_claim_stands(lying, ["OS-1"]))

    def test_unapproved_choice_reported_clean(self):
        stored = {
            "adapter_choices": [{}],
            "tracer_passage_records": [],
            "positive_control": None,
            "cross_seam_effects": [{"lien_state": "settled"}],
        }
        lying = LyingGetDict(stored, valid_run())
        self.assertIsNotNone(mod07.joint_run_failure(lying))
        self.assertFalse(
            mod07.seam_headline_claim_stands(lying, ["OS-1"]))

    def test_valid_run_reported_barred_mirror(self):
        lying = LyingGetDict(valid_run(), {
            "adapter_choices": [{}],
            "tracer_passage_records": [],
            "positive_control": None,
            "cross_seam_effects": [{"lien_state": "settled"}],
        })
        self.assertIsNone(mod07.joint_run_failure(lying))
        self.assertTrue(
            mod07.seam_headline_claim_stands(lying, ["OS-1"]))

    def test_plain_controls(self):
        self.assertIsNone(mod07.joint_run_failure(valid_run()))
        bad = valid_run()
        bad["cross_seam_effects"] = [{"lien_state": "settled"}]
        self.assertIsNotNone(mod07.joint_run_failure(bad))


class TestR12035Mod07Neighbours(unittest.TestCase):
    def test_dependency_record_stored(self):
        stored = {"edges": [("MOD-05", "MOD-06")],
                  "joint_dependent": "MOD-05"}
        reported = {"edges": [], "joint_dependent": "MOD-07"}
        self.assertFalse(
            mod07.validate_dependency_record(
                LyingGetDict(stored, reported)))
        self.assertTrue(mod07.validate_dependency_record(
            LyingGetDict(mod07.dependency_record(), stored)))

    def test_slash_report_stored(self):
        stored = {"remainder_named_as_settled": True,
                  "remainder_destination": "dest",
                  "c12_standings_carried": list(mod07.C12_STANDINGS)}
        reported = {"remainder_named_as_settled": False,
                    "remainder_destination": None,
                    "c12_standings_carried": list(mod07.C12_STANDINGS)}
        self.assertFalse(mod07.validate_slash_report(
            LyingGetDict(stored, reported)))
        self.assertTrue(mod07.validate_slash_report(
            LyingGetDict(reported, stored)))

    def test_feedback_classification_stored(self):
        stored = {"both_standings_carried": ["one"],
                  "treatment_recorded_as": "rule",
                  "paired_sensitivity_runs_required": 99}
        reported = {"both_standings_carried": ["a", "b"],
                    "treatment_recorded_as": "adapter choice",
                    "paired_sensitivity_runs_required": 1}
        self.assertFalse(mod07.validate_feedback_classification(
            LyingGetDict(stored, reported)))
        self.assertTrue(mod07.validate_feedback_classification(
            LyingGetDict(reported, stored)))

    def test_entries_read_stored_choice(self):
        stored = {"choice_identifier": "stored-id",
                  "approval": {"approver": "Project Manager"}}
        reported = {"choice_identifier": "ghost",
                    "approval": {"approver": "Ghost"}}
        choice = LyingGetDict(stored, reported)
        self.assertEqual(
            mod07.interpretation_log_entry(choice)[
                "choice_identifier"], "stored-id")
        entry = mod07.run_record_entry(choice)
        self.assertEqual(entry["choice_identifier"], "stored-id")
        self.assertEqual(
            entry["approval"], {"approver": "Project Manager"})

    def test_record_folding_and_seam_report_stored(self):
        choice = LyingGetDict(
            {"choice_identifier": "stored-id"},
            {"choice_identifier": "ghost"})
        self.assertEqual(
            mod07.record_folding(choice, ["R-1"])[
                "choice_identifier"], "stored-id")
        effect = LyingGetDict(
            {"kind": "storedkind", "value": 111},
            {"kind": "ghostkind", "value": 222})
        report = mod07.seam_effect_report(effect)
        self.assertEqual(report["effect"], "storedkind")
        self.assertEqual(report["value"], 111)

    def test_reading_for_result_stored(self):
        entry = LyingGetDict(
            {"choice_identifier": "STORED"},
            {"choice_identifier": "REPORTED"})
        self.assertIsNone(mod07.reading_for_result([entry], "REPORTED"))
        found = mod07.reading_for_result([entry], "STORED")
        self.assertIsNotNone(found)
        self.assertEqual(
            dict.get(found, "choice_identifier"), "STORED")


class TestR12036Mod07Reporting(unittest.TestCase):
    def test_classify_and_slash_outcome_stored(self):
        treatment = LyingGetDict(
            {"choice_identifier": "stored-choice"},
            {"choice_identifier": "ghost"})
        result = mod07.classify_seam_feedback(
            "OS-1", treatment, ["a", "b"])
        self.assertEqual(
            result["treatment_choice_identifier"], "stored-choice")
        outcome = LyingGetDict({"value": 111}, {"value": 222})
        self.assertEqual(
            mod07.slash_outcome_report(outcome)["value"], 111)

    def test_ruling_effect_reports_stored_difference(self):
        folding = mod07.record_folding(
            {"choice_identifier": "choice-1"}, ["R-1"])
        stored = {"seam_choice_identifiers": [],
                  "rulings_claimed": []}
        reported = {"seam_choice_identifiers": ["choice-1"],
                    "rulings_claimed": ["R-1"]}
        self.assertFalse(mod07.ruling_effect_reporting_stands(
            LyingGetDict(stored, reported), [folding]))
        lawful = {"seam_choice_identifiers": ["choice-1"],
                  "rulings_claimed": ["R-1"]}
        self.assertTrue(mod07.ruling_effect_reporting_stands(
            LyingGetDict(lawful, stored), [folding]))

    def test_append_reading_keeps_stored_entries(self):
        old = {"choice_identifier": "old-entry"}
        log = LyingList([old], [])
        updated = mod07.append_reading(log, valid_choice())
        self.assertEqual(len(updated), 2)
        self.assertEqual(updated[0], old)

    def test_entry_acts_do_not_honour_deepcopy_protocol(self):
        leaf = DeepcopyLeaf()
        choice = {"choice_identifier": leaf}
        entry = mod07.interpretation_log_entry(choice)
        self.assertIs(entry["choice_identifier"], leaf)
        effect = {"kind": "k", "value": leaf}
        self.assertIs(mod07.seam_effect_report(effect)["value"], leaf)


class TestR12037ReadoutStatus(unittest.TestCase):
    def test_readout_get_lie(self):
        lying = LyingGetDict(failing_readout(), complete_readout())
        result = mod12.readout_status(lying)
        self.assertEqual(result["form"], "lower_bound")
        self.assertEqual(len(result["unmet_conditions"]), 6)
        mirror = LyingGetDict(complete_readout(), failing_readout())
        self.assertEqual(
            mod12.readout_status(mirror)["form"], "established")

    def test_battery_get_and_list_lies(self):
        readout = complete_readout()
        readout["check_artefact_battery"] = LyingGetDict(
            {"passed": []},
            {"passed": complete_readout()[
                "check_artefact_battery"]["passed"]})
        self.assertEqual(
            mod12.readout_status(readout)["form"], "lower_bound")
        readout2 = complete_readout()
        readout2["check_artefact_battery"] = {"passed": LyingList(
            [], complete_readout()[
                "check_artefact_battery"]["passed"])}
        self.assertEqual(
            mod12.readout_status(readout2)["form"], "lower_bound")

    def test_rung_equality_and_truth_lies(self):
        readout = complete_readout()
        readout["search_completed_at_rung"] = AlwaysEq()
        self.assertEqual(
            mod12.readout_status(readout)["form"], "lower_bound")
        readout2 = complete_readout()
        readout2["claim_in_bounding_form"] = TruthyObj()
        self.assertEqual(
            mod12.readout_status(readout2)["form"], "lower_bound")

    def test_plain_controls(self):
        self.assertEqual(mod12.readout_status(
            complete_readout())["form"], "established")
        self.assertEqual(mod12.readout_status(
            failing_readout())["form"], "lower_bound")


class TestR12038Mod12ValidationTail(unittest.TestCase):
    def check(self, act, stored, reported, expected_stored):
        self.assertEqual(
            act(LyingGetDict(stored, reported)), expected_stored)

    def test_claim_label_stored(self):
        self.assertEqual(mod12.claim_label(LyingGetDict(
            {}, {"settings_lineage": "x"})),
            "screening finding only")
        self.assertEqual(mod12.claim_label(LyingGetDict(
            {"settings_lineage": "x"}, {})),
            "claim with settings lineage")

    def test_look_grid_screening_cost_stored(self):
        self.check(mod12.validate_look_decision,
                   {"registered": False,
                    "entry_written_after_decision": True},
                   {"registered": True,
                    "entry_written_after_decision": False}, False)
        self.check(mod12.validate_grid_claim,
                   {"claim": "affordable", "pilot_landed": False},
                   {"claim": "other", "pilot_landed": True}, False)
        self.check(mod12.validate_screening_claim,
                   {"fixture": "F-17", "standing": "adopted scope"},
                   {"fixture": "F-99", "standing": "weighed"}, False)
        self.check(mod12.validate_cost_claim,
                   {"basis_fixture": "F-20"},
                   {"basis_fixture": "F-99"}, False)
        self.check(mod12.validate_cost_claim,
                   {"basis_fixture": "F-99"},
                   {"basis_fixture": "F-20"}, True)

    def test_seed_placement_and_record_version_stored(self):
        self.check(mod12.validate_seed_placement,
                   {"replicates_inside_base_design": True,
                    "confirmation_family": "a",
                    "screening_family": "a"},
                   {"replicates_inside_base_design": False,
                    "confirmation_family": "a",
                    "screening_family": "b"}, False)
        self.check(mod12.validate_record_version,
                   {"produced_under": "v1", "presented_under": "v2"},
                   {"produced_under": "v1", "presented_under": "v1"},
                   False)
        self.assertFalse(mod12.validate_record_version({}))
        self.assertTrue(mod12.validate_record_version(
            {"produced_under": "v1", "presented_under": "v1"}))

    def test_family_pooling_stored(self):
        stored = {"pooled_version_sets": ["a", "b"],
                  "bound_recorded": None}
        reported = {"pooled_version_sets": ["a", "b"],
                    "bound_recorded": {
                        "version_sets": ["a", "b"], "ground": "g"}}
        self.assertFalse(mod12.validate_family_pooling(
            LyingGetDict(stored, reported)))
        lawful = {"pooled_version_sets": ["a", "b"],
                  "bound_recorded": {
                      "version_sets": ["a", "b"], "ground": "g"}}
        self.assertTrue(mod12.validate_family_pooling(
            LyingGetDict(lawful, stored)))

    def test_sweep_and_decay_nested_stored(self):
        family = LyingGetDict(
            {"name": "hostile", "standing": "optional"},
            {"name": "hostile", "standing": "required",
             "magnitudes": [1]})
        self.assertFalse(mod12.validate_sweep_programme(
            {"families": [family]}))
        programme = LyingGetDict(
            {"families": [{"name": "hostile",
                           "standing": "optional"}]},
            {"families": [{"name": "hostile",
                           "standing": "required",
                           "magnitudes": [1]}]})
        self.assertFalse(mod12.validate_sweep_programme(programme))
        plane = LyingGetDict(
            {"companion_table": None},
            {"companion_table": ["row"]})
        self.assertFalse(mod12.validate_decay_readout(
            {"planes": [plane]}))
        self.assertTrue(mod12.validate_decay_readout(
            {"planes": [{"companion_table": ["row"]}]}))


class TestR12039SampleStatement(unittest.TestCase):
    def test_ghost_run_from_get_and_item(self):
        run = LyingGetItemDict(
            {"run_class": "validation", "run_id": "stored-id"},
            {"run_class": "screening", "run_id": "ghost"})
        result = mod12.sample_statement([run])
        self.assertEqual(
            result["runs_completed_by_class"]["validation"], 1)
        self.assertEqual(
            result["runs_completed_by_class"]["screening"], 0)
        self.assertIn("stored-id", result["sample"])
        self.assertNotIn("ghost", result["sample"])

    def test_equality_lying_class_not_counted(self):
        run = {"run_class": EqStr("bogus"), "run_id": "r1"}
        result = mod12.sample_statement([run])
        self.assertEqual(result["n"], 0)

    def test_stored_class_counted_when_get_lies(self):
        run = LyingGetOnlyDict(
            {"run_class": "confirmation", "run_id": "r2"},
            {"run_class": "bogus", "run_id": "ghost"})
        result = mod12.sample_statement([run])
        self.assertEqual(
            result["runs_completed_by_class"]["confirmation"], 1)
        self.assertIn("r2", result["sample"])

    def test_no_bare_key_error(self):
        run = LyingGetOnlyDict(
            {"run_class": "bogus", "run_id": "r3"},
            {"run_class": "screening", "run_id": "ghost"})
        result = mod12.sample_statement([run])
        self.assertEqual(result["n"], 0)


class TestR12040ValidateRunRecordDress(unittest.TestCase):
    def base(self, **over):
        record = {"run_class": "confirmation",
                  "seed_domain": "held out"}
        record.update(over)
        return record

    def test_seed_domain_bytes_buffer_container(self):
        for dress in (b"screening", bytearray(b"screening"),
                      memoryview(b"screening"), ["screening"],
                      ("screening",)):
            self.assertFalse(
                mod12.validate_run_record(
                    self.base(seed_domain=dress)), repr(dress))
        self.assertFalse(mod12.validate_run_record(self.base(
            run_class="headline",
            seed_domain=bytearray(b"screening"))))

    def test_relabelled_from_bytes(self):
        self.assertFalse(mod12.validate_run_record(
            self.base(relabelled_from=b"screening")))
        self.assertFalse(mod12.validate_run_record(
            self.base(relabelled_from="screening")))

    def test_run_class_read_as_stored_text(self):
        self.assertTrue(mod12.validate_run_record(
            {"run_class": b"screening", "seed_domain": "other"}))
        self.assertFalse(mod12.validate_run_record(
            {"run_class": b"confirmation",
             "seed_domain": b"screening"}))

    def test_hash_lying_keys(self):
        record = {HashKey("run_class"): "screening",
                  HashKey("seed_domain"): "other"}
        self.assertTrue(mod12.validate_run_record(record))

    def test_plain_controls(self):
        self.assertFalse(mod12.validate_run_record(self.base(
            seed_domain="screening")))
        self.assertTrue(mod12.validate_run_record(
            {"run_class": "screening",
             "seed_domain": "screening"}))


class TestR12041SweepManifest(unittest.TestCase):
    def test_hash_truth_lies(self):
        record = {"family_identifier": "fam",
                  "family_version": "v1",
                  "family_manifest_hash": FalsyStr("HASH-STORED"),
                  "seal_hash": "FALLBACK"}
        self.assertEqual(mod12.sweep_manifest(record)[
            "sealed_family_record_hash"], "HASH-STORED")
        mirror = {"family_identifier": "fam",
                  "family_version": "v1",
                  "family_manifest_hash": TruthyStr(""),
                  "seal": {"hash": "SEALHASH"}}
        self.assertEqual(mod12.sweep_manifest(mirror)[
            "sealed_family_record_hash"], "SEALHASH")

    def test_plain_control(self):
        record = {"family_identifier": "fam",
                  "family_version": "v1",
                  "family_manifest_hash": "HASH-STORED",
                  "seal_hash": "FALLBACK"}
        self.assertEqual(mod12.sweep_manifest(record)[
            "sealed_family_record_hash"], "HASH-STORED")


class TestR12042TracerEquality(unittest.TestCase):
    def test_positive_control_equality_lie(self):
        control = {"fixture": AlwaysEq(), "path": AlwaysEq(),
                   "result": AlwaysEq(),
                   "recorded_as_passing": True}
        records = mod07.tracer_passage_records("r1")
        self.assertFalse(
            mod07.validate_tracer_passage_set(records, control))
        self.assertTrue(mod07.validate_tracer_passage_set(records))

    def test_passage_result_equality_lie(self):
        with self.assertRaises(ValueError):
            mod07.make_tracer_passage_record(
                "OS-1", "point", "passed thing", AlwaysEq())
        records = mod07.tracer_passage_records("r1")
        records[0] = dict(records[0])
        records[0]["result"] = AlwaysEq()
        self.assertFalse(
            mod07.validate_tracer_passage_set(records))
        with self.assertRaises(ValueError):
            mod07.make_tracer_passage_record(
                "OS-1", "point", "passed thing", "bogus result")


class TestR12043WinningRegime(unittest.TestCase):
    def test_outer_iteration_lie(self):
        losing = [(0.1, 0.9)] * 30
        winning = [(0.9, 0.1)] * 30
        self.assertFalse(mod12.winning_regime(
            LyingList(losing, winning)))
        self.assertTrue(mod12.winning_regime(winning))
        self.assertFalse(mod12.winning_regime(losing))

    def test_entry_iteration_lie(self):
        entries = [LyingList([0.1, 0.9], [0.9, 0.1])
                   for _ in range(30)]
        self.assertFalse(mod12.winning_regime(entries))


if __name__ == "__main__":
    unittest.main()
