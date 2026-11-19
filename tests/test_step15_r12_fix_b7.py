# Step 15 rerun, fix wave 11, Builder 7 pins.
# Rows R11-081 to R11-090: the MOD-12, MOD-07, and MOD-09 handed
# readings and the MOD-04 build_view_record handed readings.
# Every pin hands a value whose stored contents and reported
# readings differ, and states that the act under cure reads the
# stored contents, never the handed reading.
# Plain simulated values only.
import unittest

import crucible.mod04 as mod04
import crucible.mod07 as mod07
import crucible.mod09 as mod09
import crucible.mod12 as mod12


class LyingGetDict(dict):
    """A dict storing one mapping and reporting another through
    its get, contains, item, and items readings."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)

    def __contains__(self, key):
        return dict.__contains__(self._reported, key)

    def __getitem__(self, key):
        return dict.__getitem__(self._reported, key)

    def items(self):
        return dict.items(self._reported)


class RaisingGetDict(dict):
    """A dict whose get reading raises for one stated key."""

    def __init__(self, stored, raise_key):
        dict.__init__(self, stored)
        self._raise_key = raise_key

    def get(self, key, default=None):
        if key == self._raise_key:
            raise RuntimeError("handed get reading raised")
        return dict.get(self, key, default)


class AlwaysRaisingGetDict(dict):
    """A dict whose get reading always raises."""

    def get(self, key, default=None):
        raise RuntimeError("handed get reading raised")


class LyingStr(str):
    """A text value storing one text and reporting another
    through its string reading."""

    def __new__(cls, stored, reported):
        obj = str.__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported


class LyingLowerStr(str):
    """A text value whose lower reading reports another wording."""

    def __new__(cls, stored, reported_lower):
        obj = str.__new__(cls, stored)
        obj._reported_lower = reported_lower
        return obj

    def lower(self):
        return self._reported_lower


class LyingStripStr(str):
    """A text value whose strip reading reports a stated version."""

    def strip(self, *args):
        return "v1"


class LyingList(list):
    """A list storing one part set and iterating, measuring, and
    testing membership as another."""

    def __init__(self, stored, reported):
        list.__init__(self, stored)
        self._reported = list(reported)

    def __iter__(self):
        return iter(self._reported)

    def __len__(self):
        return len(self._reported)

    def __contains__(self, item):
        return item in self._reported


def lawful_search_record():
    carriage = mod09.run_record_carriage(
        ["conditional briber"], 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=["conditional briber"])
    return mod09.build_search_record(
        carriage, points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": "no failure"}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=[0, 5])


def valid_choice():
    return mod07.make_adapter_choice(
        "choice-1", "reading A", "point", "gov v1", "fold v1",
        approval={"approver": "Project Manager",
                  "choice_identifier": "choice-1",
                  "effects": ["effect one"],
                  "standing": "approved"})


def valid_joint_run():
    return {
        "adapter_choices": [],
        "tracer_passage_records": mod07.tracer_passage_records("r1"),
        "positive_control": mod07.positive_control_record(),
        "cross_seam_effects": [],
    }


class TestR11081Mod12HandedReadings(unittest.TestCase):
    def test_admit_claim_stored_results_seen_bars(self):
        family = LyingGetDict(
            {"results_seen": True}, {"results_seen": False})
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.admit_claim(family, "claim one")

    def test_admit_claim_mirror_admits(self):
        family = LyingGetDict(
            {"results_seen": False}, {"results_seen": True})
        result = mod12.admit_claim(family, "claim one")
        self.assertTrue(result["admitted"])

    def test_validate_run_record_reads_stored_class(self):
        stored = {"run_class": "confirmation",
                  "seed_domain": "held out confirmation",
                  "relabelled_from": "screening"}
        reported = dict(stored)
        reported["run_class"] = "screening"
        run = LyingGetDict(stored, reported)
        self.assertFalse(mod12.validate_run_record(run))

    def test_failures_of_complete_record_are_none(self):
        complete = mod12.make_family_record()
        lying = LyingGetDict(complete, {})
        self.assertEqual(
            mod12.family_record_validation_failures(lying),
            ["the reportable run judgement stands refused"])

    def test_failures_of_empty_record_are_named(self):
        complete = mod12.make_family_record()
        lying = LyingGetDict({}, complete)
        self.assertTrue(
            mod12.family_record_validation_failures(lying))

    def test_validate_family_record_ecology_limb_reads_stored(self):
        record = mod12.make_family_record()
        record["ecology_point"] = "fixed"
        record["amendment_landed"] = False
        reported = dict(record)
        reported["ecology_point"] = "open"
        lying = LyingGetDict(record, reported)
        self.assertFalse(mod12.validate_family_record(lying))

    def test_validate_kill_check_reads_stored(self):
        stored = {"name": "", "killing_result": "",
                  "data_outside_artefact": False,
                  "judge_outside_artefact": False}
        reported = mod12.kill_check_for_claim("claim one")
        check = LyingGetDict(stored, reported)
        self.assertFalse(mod12.validate_kill_check(check))

    def test_sweep_manifest_carries_stored_values(self):
        stored = {"family_identifier": "stored-id",
                  "family_id": "stored-id",
                  "family_version": "stored version",
                  "family_manifest_hash": "stored-hash",
                  "seal": {"hash": "stored-seal-hash"}}
        reported = {"family_identifier": "lied-id",
                    "family_id": "lied-id",
                    "family_version": "lied version",
                    "family_manifest_hash": "lied-hash",
                    "seal": {"hash": "lied-seal-hash"}}
        manifest = mod12.sweep_manifest(LyingGetDict(stored, reported))
        self.assertEqual(manifest["family_identifier"], "stored-id")
        self.assertEqual(manifest["family_version"], "stored version")
        self.assertEqual(
            manifest["sealed_family_record_hash"], "stored-hash")


class TestR11082Mod12StoredScalarForms(unittest.TestCase):
    def test_seal_carries_stored_version_and_hash_text(self):
        record = mod12.make_family_record()
        version = LyingStr("stored version 9", "reported version 1")
        hashed = LyingStr("stored hash 9", "reported hash 1")
        record["family_version"] = version
        record["family_manifest_hash"] = hashed
        sealed = mod12.seal_family_record(record)
        self.assertEqual(str(sealed["seal"]["version"]),
                         "stored version 9")
        self.assertEqual(str(sealed["seal"]["hash"]), "stored hash 9")
        self.assertIsNot(sealed["seal"]["version"], version)

    def test_sealed_edit_new_id_from_stored_identifier(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record("family-A-stored"))
        handed = LyingStr("family-A-stored", "family-B-reported")
        sealed["family_identifier"] = handed
        sealed["family_id"] = handed
        edited = mod12.apply_family_edit(sealed)
        self.assertEqual(edited["family_identifier"],
                         "family-A-stored-edited-1")


class TestR11083Mod12EditClaimsReading(unittest.TestCase):
    def test_edit_claims_come_from_stored_claims(self):
        record = mod12.make_family_record()
        claims = LyingList(["stored claim A"], ["reported claim B"])
        edited = mod12.apply_family_edit(
            record, {"headline_claims": claims})
        self.assertEqual(edited["headline_claims"], ["stored claim A"])
        self.assertEqual(
            [check["claim"] for check in edited["kill_check_fields"]],
            ["stored claim A"])
        self.assertEqual(
            [check["claim"] for check in edited["kill_checks"]],
            ["stored claim A"])


class TestR11084Mod07HandedReadings(unittest.TestCase):
    def test_choice_approval_reads_stored_approval(self):
        choice = valid_choice()
        stored_approval = {"approver": "Someone Else",
                           "choice_identifier": "choice-1",
                           "effects": ["effect one"],
                           "standing": "refused"}
        reported_approval = {"approver": "Project Manager",
                             "choice_identifier": "choice-1",
                             "effects": ["effect one"],
                             "standing": "approved"}
        choice["approval"] = LyingGetDict(
            stored_approval, reported_approval)
        self.assertFalse(mod07.choice_approval_stands(choice))
        self.assertFalse(mod07.validate_adapter_choice(choice))

    def test_choice_pair_reads_stored_readings(self):
        base = {"choice_identifier": "choice-1",
                "reading_applied": "reading A",
                "governing_text_version": "gov v1",
                "dependence_marks": ["mark one"]}
        log_entry = dict(base)
        stored_run = dict(base)
        stored_run["reading_applied"] = "reading B"
        run_entry = LyingGetDict(stored_run, base)
        self.assertFalse(
            mod07.validate_choice_pair(log_entry, run_entry))

    def test_cross_seam_effect_reads_stored_lien_state(self):
        settled = LyingGetDict(
            {"lien_state": "settled"},
            {"lien_state": "computed not settled"})
        self.assertFalse(mod07.validate_cross_seam_effect(settled))
        computed = LyingGetDict(
            {"lien_state": "computed not settled"},
            {"lien_state": "settled"})
        self.assertTrue(mod07.validate_cross_seam_effect(computed))

    def test_joint_run_reads_stored_effects(self):
        run = valid_joint_run()
        run["cross_seam_effects"] = [
            {"kind": "vouch release", "lien_state": "settled"}]
        reported = valid_joint_run()
        lying = LyingGetDict(run, reported)
        self.assertFalse(mod07.validate_joint_run(lying))

    def test_folding_record_reads_stored_limbs(self):
        stored = {"choice_identifier": "choice-1",
                  "rulings_recorded": [],
                  "recorded_ruling_by_ruling": False,
                  "gaps_carried_open": [],
                  "gaps_filled_by_inference": ["G-1"]}
        reported = mod07.record_folding(valid_choice(), ["G-1"])
        lying = LyingGetDict(stored, reported)
        self.assertFalse(mod07.validate_folding_record(lying))


class TestR11085Mod07SeamWording(unittest.TestCase):
    def test_settled_wording_with_computed_lower_is_refused(self):
        text = LyingLowerStr(
            "the cross seam effect is settled in the chosen escrow",
            "the cross seam effect is computed not settled")
        self.assertFalse(mod07.validate_seam_wording(text))

    def test_computed_wording_with_settled_lower_stands(self):
        text = LyingLowerStr(
            "the effect is computed not settled",
            "the effect is settled")
        self.assertTrue(mod07.validate_seam_wording(text))


class TestR11086Mod07PassageSetContainer(unittest.TestCase):
    def test_container_storing_nothing_does_not_validate(self):
        valid = mod07.tracer_passage_records("run-x")
        container = LyingList([], valid)
        self.assertFalse(mod07.validate_tracer_passage_set(container))

    def test_container_storing_valid_set_validates(self):
        valid = mod07.tracer_passage_records("run-x")
        container = LyingList(valid, valid[:3])
        self.assertTrue(mod07.validate_tracer_passage_set(container))


class TestR11087Mod09CarriageReadings(unittest.TestCase):
    def test_search_record_with_no_stored_class_is_not_certified(self):
        record = lawful_search_record()
        record = dict(record)
        carriage = dict(record["run_record"])
        carriage["strategy_class"] = LyingList(
            [], ["conditional briber"])
        record["run_record"] = carriage
        self.assertFalse(mod09.validate_search_record(record))
        self.assertFalse(mod09.validate_search_record(
            record, fixed_class=["conditional briber"]))

    def test_carriage_with_no_stored_class_is_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(
                LyingList([], ["conditional briber"]), 6,
                "catalogue version 1", "ladder definition pointer",
                "ladder version 1",
                strategies=["conditional briber"])

    def test_carriage_blank_stored_version_is_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(
                ["conditional briber"], 6,
                LyingStripStr("   "), "ladder definition pointer",
                "ladder version 1")


class TestR11088Mod09PayoffSweepReadout(unittest.TestCase):
    def test_attacker_payoff_reads_stored_payoff(self):
        strategy = LyingGetDict(
            {"in_protocol_payoff": 5}, {"in_protocol_payoff": 100})
        self.assertEqual(mod09.attacker_payoff(strategy, 3), 8)

    def test_attacker_payoff_with_no_stored_payoff_fails_by_name(self):
        strategy = LyingGetDict({}, {"in_protocol_payoff": 7})
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(strategy, 3)

    def test_sweep_reads_stored_range(self):
        strategy = LyingGetDict(
            {"external_profit_range": [5], "in_protocol_payoff": 5},
            {"external_profit_range": [0, 5],
             "in_protocol_payoff": 5})
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.sweep_external_profit(
                strategy, largest_in_protocol_payoff=3)

    def test_readout_reads_stored_ladder_position(self):
        carriage = LyingGetDict(
            {"ladder_position": 0, "strategies_exercised": []},
            {"ladder_position": 6, "strategies_exercised": []})
        record = {"run_record": carriage,
                  "external_profit_swept_values": []}
        unit = mod09.readout(record)
        self.assertEqual(unit["readout_status"],
                         "not at the readout point")


class TestR11089Mod12ValidateFamilyRecordLimbs(unittest.TestCase):
    def test_kill_check_lists_read_stored(self):
        record = mod12.make_family_record()
        bad = mod12.kill_check_for_claim(
            "claim that no longer stands")
        record["kill_check_fields"] = [bad]
        record["kill_checks"] = [bad]
        reported = dict(record)
        reported["kill_check_fields"] = []
        reported["kill_checks"] = []
        lying = LyingGetDict(record, reported)
        self.assertFalse(mod12.validate_family_record(lying))

    def test_raising_get_does_not_escape_validation(self):
        record = mod12.make_family_record()
        record["ecology_point"] = "fixed"
        record["amendment_landed"] = False
        raising = RaisingGetDict(record, "kill_check_fields")
        self.assertFalse(mod12.validate_family_record(raising))


class TestR11090Mod04BuildViewRecordReadings(unittest.TestCase):
    def test_position_read_from_stored_run_record(self):
        run_record = LyingGetDict(
            {"scheduling_position_identifier": "stored-pos"},
            {"scheduling_position_identifier": "fabricated-pos"})
        record = mod04.build_view_record(run_record=run_record)
        self.assertEqual(
            record["scheduling_position_identifier"], "stored-pos")

    def test_raising_run_record_get_does_not_escape(self):
        run_record = AlwaysRaisingGetDict(
            {"scheduling_position_identifier": "stored-pos"})
        record = mod04.build_view_record(run_record=run_record)
        self.assertEqual(
            record["scheduling_position_identifier"], "stored-pos")

    def test_arrival_values_read_from_stored_items(self):
        item = LyingGetDict(
            {"first_seen_day": 1, "delay": 0},
            {"first_seen_day": 42, "delay": 9})
        record = mod04.build_view_record(contents=[item])
        self.assertEqual(record["first_seen_day_per_record"],
                         {"0": 1})
        self.assertEqual(record["delay_applied_per_record"],
                         {"0": 0})
        self.assertEqual(record["arrival_group_form"],
                         "derived from contents")

    def test_raising_item_get_does_not_escape(self):
        item = AlwaysRaisingGetDict(
            {"first_seen_day": 1, "delay": 0})
        record = mod04.build_view_record(contents=[item])
        self.assertEqual(record["first_seen_day_per_record"],
                         {"0": 1})
        self.assertEqual(record["delay_applied_per_record"],
                         {"0": 0})


if __name__ == "__main__":
    unittest.main()
