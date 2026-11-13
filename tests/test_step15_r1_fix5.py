"""Step 15 Round 1 fix pins, cluster 5 (forms as specified).

Each test pins the cured behaviour of one register item taken by
cluster 5, in the triage cure shape for that item. These tests stand
written before the cures and stand seen to fail on the uncured tree.
"""

import copy
import pathlib
import unittest
from decimal import getcontext, setcontext, Context

from crucible import mod01, mod03, mod06, mod08, mod09


PRODUCT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _form4(**overrides):
    instance = mod01.minimal_valid_instance("4")
    instance.update(overrides)
    return instance


class TestTB02ImportFallbacks(unittest.TestCase):
    def test_no_try_except_import_fallback_in_mod08_mod09(self):
        for name in ("mod08.py", "mod09.py"):
            text = (PRODUCT_ROOT / "crucible" / name).read_text()
            self.assertNotIn("except Exception", text, name)
            self.assertNotIn("= None", text.split("__all__")[0], name)

    def test_mod09_carries_no_redeclared_op11_constants(self):
        text = (PRODUCT_ROOT / "crucible" / "mod09.py").read_text()
        self.assertNotIn('"honest adaptive rewiring"', text)
        self.assertNotIn('"adaptive sleeper concealment"', text)

    def test_accessors_never_return_none_on_standing_tree(self):
        self.assertIsNotNone(mod08.mod01_surface())
        self.assertIsNotNone(mod09.mod03_catalogue_record())
        self.assertEqual(mod09.catalogue_gaps(), mod03.catalogue_gaps())
        self.assertEqual(mod09.CATALOGUE_STANDING, mod03.CATALOGUE_STANDING)


class TestTA17FamilySealKey(unittest.TestCase):
    def test_plan_named_records_match(self):
        manifest = {"family_version": "v1",
                    "sealed_family_record_hash": "h1"}
        record = {"family_version": "v1", "family_manifest_hash": "h1"}
        self.assertTrue(mod01.validate_family_seal_match(manifest, record))

    def test_plan_named_records_mismatch(self):
        manifest = {"family_version": "v1",
                    "sealed_family_record_hash": "h1"}
        bad_hash = {"family_version": "v1", "family_manifest_hash": "h2"}
        bad_version = {"family_version": "v2",
                       "family_manifest_hash": "h1"}
        self.assertFalse(mod01.validate_family_seal_match(manifest, bad_hash))
        self.assertFalse(
            mod01.validate_family_seal_match(manifest, bad_version))


class TestTA05TA06Route10Bars(unittest.TestCase):
    def test_real_money_scalar_field_fails(self):
        instance = _form4(real_money_value=500)
        self.assertFalse(mod01.validate_record("4", instance))
        self.assertFalse(mod01.run_is_reportable("4", instance))

    def test_real_money_amount_currency_dict_fails(self):
        instance = _form4(real_money={"amount": 500, "currency": "USD"})
        self.assertFalse(mod01.validate_record("4", instance))

    def test_unmutated_form4_still_passes(self):
        self.assertTrue(mod01.validate_record("4", _form4()))

    def test_fourth_anchor_value_dict_and_list_fail(self):
        four_dict = {"a": 1, "b": 2, "c": 3, "d": 4}
        four_list = ["a", "b", "c", "d"]
        self.assertFalse(mod01.validate_record(
            "4", _form4(anchor_scenario_values=four_dict)))
        self.assertFalse(mod01.validate_record(
            "4", _form4(anchor_scenario_values=four_list)))
        self.assertFalse(mod01.run_is_reportable(
            "4", _form4(anchor_scenario_values=four_list)))

    def test_three_anchor_values_still_pass(self):
        three = ["a", "b", "c"]
        self.assertTrue(mod01.validate_record(
            "4", _form4(anchor_scenario_values=three)))


class TestTA27Discriminators(unittest.TestCase):
    def test_hostile_discriminators_fail_on_three_forms(self):
        cases = (("2", "decay_slice"), ("10", "lost_contact_clock_state"),
                 ("13", "anchor_scenario_identity"))
        for form_id, _field in cases:
            condition = mod01.field_conditions(form_id)[0]
            disc = condition["discriminator"]
            for bad in (1, "true", "yes", ["x"]):
                instance = mod01.minimal_valid_instance(form_id)
                instance[disc] = bad
                instance.pop(condition["field"], None)
                self.assertFalse(
                    mod01.validate_record(form_id, instance),
                    (form_id, bad))

    def test_stated_true_and_false_standings_kept(self):
        for form_id in ("2", "10", "13"):
            condition = mod01.field_conditions(form_id)[0]
            held = mod01.minimal_valid_instance(
                form_id, condition_holds=condition)
            self.assertTrue(mod01.validate_record(form_id, held))
            plain = mod01.minimal_valid_instance(form_id)
            self.assertTrue(mod01.validate_record(form_id, plain))


class TestTA28Form36EntryKinds(unittest.TestCase):
    def test_invented_entry_kind_fails(self):
        instance = mod01.minimal_valid_instance(
            "36", entry_kind="ordinary")
        instance["entry_kind"] = "invented kind"
        self.assertFalse(mod01.validate_record("36", instance))

    def test_ordinary_entry_with_supersession_fields_fails(self):
        instance = mod01.minimal_valid_instance(
            "36", entry_kind="ordinary")
        instance["superseded_from_journal_position"] = "stated value"
        instance["resume_attempt_identifier"] = "stated value"
        self.assertFalse(mod01.validate_record("36", instance))

    def test_ordinary_entry_with_agent_identifier_fails(self):
        instance = mod01.minimal_valid_instance(
            "36", entry_kind="ordinary")
        instance["agent_identifier"] = "stated value"
        self.assertFalse(mod01.validate_record("36", instance))

    def test_lawful_kinds_still_pass(self):
        for kind in ("ordinary", "agent", "supersession"):
            instance = mod01.minimal_valid_instance("36", entry_kind=kind)
            self.assertTrue(mod01.validate_record("36", instance), kind)


class TestTA42ReservedMatterContainers(unittest.TestCase):
    def test_reserved_value_as_dict_key_fails(self):
        reserved = mod01.RESERVED_MATTER_VALUES[0]
        instance = _form4(control_values={reserved: "ordinary"})
        self.assertFalse(mod01.validate_record("4", instance))

    def test_reserved_value_in_set_and_frozenset_fails(self):
        reserved = mod01.RESERVED_MATTER_VALUES[1]
        self.assertFalse(mod01.validate_record(
            "4", _form4(control_values={reserved})))
        self.assertFalse(mod01.validate_record(
            "4", _form4(control_values=frozenset([reserved]))))

    def test_value_position_still_fails_and_clean_passes(self):
        reserved = mod01.RESERVED_MATTER_VALUES[2]
        self.assertFalse(mod01.validate_record(
            "4", _form4(control_values=[reserved])))
        self.assertTrue(mod01.validate_record("4", _form4()))


class TestForm13Additions(unittest.TestCase):
    FIELDS = (
        "resume_attempt_identifier", "journal_event_count_at_checkpoint",
        "last_event_identifier", "build_identifier",
        "dependency_manifest_hash", "parent_checkpoint_identifier",
        "branch_cluster_identifier", "production_or_recovery_class",
        "form_standing_value", "annotation_link_identifier",
    )

    def test_fields_stand_on_form13_list(self):
        fields = mod01.form_fields("13")
        for field in self.FIELDS:
            self.assertIn(field, fields)

    def test_manifest_lacking_each_required_addition_fails(self):
        for field in self.FIELDS:
            if field == "annotation_link_identifier":
                continue
            instance = mod01.minimal_valid_instance("13")
            del instance[field]
            self.assertFalse(mod01.validate_record("13", instance), field)

    def test_minimal_manifest_validates_and_standing_value_pending(self):
        instance = mod01.minimal_valid_instance("13")
        self.assertTrue(mod01.validate_record("13", instance))
        self.assertIn("pending", instance["form_standing_value"])
        self.assertIn("OP-24", instance["form_standing_value"])

    def test_annotation_link_conditional_on_anchor_run(self):
        condition = [c for c in mod01.field_conditions("13")
                     if c["field"] == "annotation_link_identifier"]
        self.assertEqual(len(condition), 1)
        held = mod01.minimal_valid_instance(
            "13", condition_holds=condition[0])
        self.assertIn("annotation_link_identifier", held)
        self.assertTrue(mod01.validate_record("13", held))
        plain = mod01.minimal_valid_instance("13")
        self.assertNotIn("annotation_link_identifier", plain)
        self.assertTrue(mod01.validate_record("13", plain))


class TestForm27Additions(unittest.TestCase):
    def test_threshold_fields_and_statement_on_form27_list(self):
        fields = mod01.form_fields("27")
        for field in ("threshold_formula_table_identifier",
                      "threshold_formula_table_version",
                      "standing_statement"):
            self.assertIn(field, fields)


class TestTB03ExtendCatalogue(unittest.TestCase):
    def _records(self):
        return [mod03.make_archetype_record(
            archetype_id="honest", behaviour={"action": "wait"},
            parameter_rows=[{"row": "honest row"}])]

    def test_extension_record_carries_four_limbs(self):
        new = mod03.make_archetype_record(
            archetype_id="sleeper", behaviour={"action": "wait"},
            parameter_rows=[{"row": "sleeper row"}])
        result = mod03.extend_catalogue(
            self._records(), new, strategy_class="fixed class")
        self.assertIn("version_stamp", result)
        self.assertIn("family_labelling_before", result)
        self.assertIn("family_labelling_after", result)
        self.assertEqual(result["family_labelling_before"], ["honest"])
        self.assertEqual(
            result["family_labelling_after"], ["honest", "sleeper"])
        self.assertIn("generator_code_entry", result)
        self.assertEqual(
            result["generator_code_entry"]["archetype_id"], "sleeper")
        self.assertEqual(
            result["generator_code_entry"]["generator_signature"],
            new["generator_signature"])
        self.assertIn("pricing_record", result)
        self.assertIsNone(result["pricing_record"]["figure"])
        self.assertIn("no figure stated",
                      result["pricing_record"]["figure_standing"])


class TestTA68CatalogueHonesty(unittest.TestCase):
    def test_duplicate_identifier_fails_by_name(self):
        records = [mod03.make_archetype_record(archetype_id="honest"),
                   mod03.make_archetype_record(archetype_id="honest")]
        with self.assertRaises(ValueError):
            mod03.archetype_catalogue(records)

    def test_missing_identifier_fails_by_name(self):
        records = [mod03.make_archetype_record(archetype_id=None)]
        with self.assertRaises(ValueError):
            mod03.archetype_catalogue(records)

    def test_sound_catalogue_unchanged(self):
        records = [mod03.make_archetype_record(archetype_id="honest")]
        catalogue = mod03.archetype_catalogue(records)
        self.assertEqual(set(catalogue["entries"]), {"honest"})


class TestTB04CoreInstructionRefusals(unittest.TestCase):
    def test_unnamed_request_refused_as_unnamed_not_excluded(self):
        with self.assertRaises(Exception) as caught:
            mod06.run_instruction("some_unlisted_instruction")
        self.assertNotIsInstance(caught.exception, mod06.ExcludedSubpath)
        self.assertIn("unnamed", str(caught.exception))

    def test_excluded_subpath_refusal_kept(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("pool_init")
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(
                "deposit", context={"profile": "backup extended profile"})

    def test_named_instructions_still_run(self):
        run = mod06.run_instruction("deposit")
        self.assertEqual(run["payload"]["instruction"], "deposit")


class TestC48RefusalWording(unittest.TestCase):
    def test_replace_backup_key_refusal_reads_as_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod06.run_instruction("replace_backup_key")
        message = str(caught.exception)
        self.assertIn("replace_backup_key", message)
        self.assertIn("refused", message)
        self.assertIn("backup key registration at setup", message)


class TestMOD08Items(unittest.TestCase):
    RECORD = {"agent_identifier": "agent-1", "day": 1,
              "feature_values": {"activity": 4},
              "records_for_agent_and_day": []}

    def test_ta41_is_farm_rejected_at_depth(self):
        record = copy.deepcopy(self.RECORD)
        record["feature_values"] = {"activity": 4}
        record["records_for_agent_and_day"] = [{"nested": {"is_farm": 1}}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)
        record2 = copy.deepcopy(self.RECORD)
        record2["records_for_agent_and_day"] = [[{"is_farm": 1}]]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record2)

    def test_ta24_day_and_identifier_forms_rejected(self):
        for bad_day in ("1", -1, 10 ** 30, 1.5, True):
            record = copy.deepcopy(self.RECORD)
            record["day"] = bad_day
            with self.assertRaises(mod08.NamedDetectionFailure,
                                   msg=repr(bad_day)):
                mod08.accept_detection_input(record)
        record = copy.deepcopy(self.RECORD)
        record["agent_identifier"] = 42
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)
        accepted = mod08.accept_detection_input(copy.deepcopy(self.RECORD))
        self.assertEqual(accepted["day"], 1)

    def test_ta25_unconsumable_feature_values_fail_by_name(self):
        for bad in ("text", None, True, float("nan"), float("inf")):
            record = copy.deepcopy(self.RECORD)
            record["feature_values"] = {"activity": bad}
            with self.assertRaises(mod08.NamedDetectionFailure,
                                   msg=repr(bad)):
                mod08.score_day([record])

    def test_ta16_decimal_context_independence(self):
        record = copy.deepcopy(self.RECORD)
        record["feature_values"] = {"a": 0.1234567, "b": 0.7654321,
                                    "c": 1.1111111}
        results = []
        for prec in (6, 28):
            setcontext(Context(prec=prec))
            try:
                results.append(mod08.score_day([copy.deepcopy(record)]))
            finally:
                setcontext(Context(prec=28))
        first, second = results
        self.assertEqual(first["verdict_states"], second["verdict_states"])
        self.assertEqual(
            first["detection_states"][0]["accumulator_values"],
            second["detection_states"][0]["accumulator_values"])

    def test_ta40_permuted_delivery_compares_same(self):
        first = [dict(self.RECORD, agent_identifier="agent-a", day=1),
                 dict(self.RECORD, agent_identifier="agent-b", day=2)]
        second = [copy.deepcopy(first[1]), copy.deepcopy(first[0])]
        check = mod08.compare_verdict_determinism(first, second)
        self.assertTrue(check["same"])
        outcome = mod08.record_verdict_difference(first, second)
        self.assertIsNone(outcome["event"])
        self.assertTrue(outcome["run_reportable"])
        changed = [copy.deepcopy(first[0]),
                   dict(self.RECORD, agent_identifier="agent-b", day=2,
                        feature_values={"activity": 400})]
        self.assertFalse(
            mod08.compare_verdict_determinism(first, changed)["same"])

    def test_ta72_accumulator_carries_gated_marker(self):
        state = mod08.detection_state_record(copy.deepcopy(self.RECORD))
        self.assertIn("accumulator_standing", state)
        self.assertIn("TG-07.5", state["accumulator_standing"])

    def test_c57_brackets_carry_label_and_none_verdict(self):
        for builder in (mod08.oracle_control_bracket,
                        mod08.null_control_bracket):
            bracket = builder()
            self.assertEqual(
                bracket["profile_bound_label"],
                mod08.PROFILE_LABEL_CARRIAGE)
            self.assertIsNone(bracket["score_verdict"])
            self.assertTrue(mod08.validate_output(bracket))

    def test_c59_nested_and_renamed_verdicts_fail(self):
        base = {"profile_bound_label": mod08.PROFILE_LABEL_CARRIAGE,
                "score_verdict": None}
        nested = copy.deepcopy(base)
        nested["inner"] = {"score_verdict": "pass"}
        self.assertFalse(mod08.validate_output(nested))
        renamed = copy.deepcopy(base)
        renamed["result"] = "pass"
        self.assertFalse(mod08.validate_output(renamed))
        nested_fail = copy.deepcopy(base)
        nested_fail["inner"] = {"score_verdict": "fail"}
        self.assertFalse(mod08.validate_output(nested_fail))
        renamed_fail = copy.deepcopy(base)
        renamed_fail["result"] = "failed"
        self.assertFalse(mod08.validate_output(renamed_fail))
        conforming = copy.deepcopy(base)
        conforming["note"] = "the wording pass appears in plain text"
        self.assertTrue(mod08.validate_output(conforming))
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.report([nested])

    def test_c61_sealed_set_records_carry_label(self):
        sealed = mod08.create_sealed_set()
        self.assertEqual(
            sealed["profile_bound_label"], mod08.PROFILE_LABEL_CARRIAGE)
        self.assertIsNone(sealed["score_verdict"])
        mod08.freeze_sealed_set(sealed)
        self.assertEqual(
            sealed["profile_bound_label"], mod08.PROFILE_LABEL_CARRIAGE)
        mod08.author_sealed_class(
            sealed, "sleeper class", "s1",
            separations=["authorship separation", "knowledge separation",
                         "record separation"])
        mod08.author_sealed_class(
            sealed, "honest challenge variant", "h1",
            separations=["authorship separation", "knowledge separation",
                         "record separation"])
        mod08.seal_sealed_set(sealed)
        self.assertEqual(
            sealed["profile_bound_label"], mod08.PROFILE_LABEL_CARRIAGE)
        self.assertIsNone(sealed["score_verdict"])

    def test_c24_c25_detection_output_form27(self):
        result = mod08.score_day(
            [copy.deepcopy(self.RECORD)], run_identifier="run-1")
        output = result["detection_output"]
        self.assertIn("verdict_states_and_accumulator_updates", output)
        self.assertNotIn("verdict_states_by_agent_and_day", output)
        self.assertNotIn("accumulator_updates_by_agent_and_day", output)
        self.assertNotIn("score_verdict", output)
        self.assertEqual(
            output["threshold_formula_table_identifier"],
            "threshold formula table")
        self.assertTrue(output["threshold_formula_table_version"])
        self.assertIn("self consistency only",
                      output["standing_statement"])
        self.assertIn("OP-16", output["standing_statement"])
        self.assertTrue(mod01.validate_record("27", output))


class TestMOD09Items(unittest.TestCase):
    def test_ta29_ladder_positions_bounded(self):
        for bad in (7, 100, 6.5, -5):
            state = mod09.stopping_rule_state(bad)
            self.assertFalse(state["readout_point"], bad)
            with self.assertRaises(mod09.NamedAttackerFailure, msg=repr(bad)):
                mod09.run_record_carriage(
                    ["conditional briber"], bad, "catalogue version 1",
                    "ladder definition pointer", "ladder version 1")
        self.assertFalse(mod09.stopping_rule_state(0)["readout_point"])
        self.assertTrue(mod09.stopping_rule_state(6)["readout_point"])
        carriage = mod09.run_record_carriage(
            ["conditional briber"], 6, "catalogue version 1",
            "ladder definition pointer", "ladder version 1")
        self.assertEqual(carriage["ladder_position"], 6)

    def test_tb48_readout_on_missing_record_named_failure(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(None)
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout("not a record")

    def test_ta73_search_record_content_and_swept_carriage(self):
        carriage = mod09.run_record_carriage(
            ["conditional briber"], 6, "catalogue version 1",
            "ladder definition pointer", "ladder version 1",
            strategies=["conditional briber"])
        record = mod09.build_search_record(
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
            external_profit_swept_values=[0, 7])
        self.assertTrue(mod09.validate_search_record(record))
        self.assertEqual(record["external_profit_swept_values"], [0, 7])
        unit = mod09.readout(record)
        self.assertNotEqual(unit.get("result_kind"),
                            "in protocol result only")
        hollow = copy.deepcopy(record)
        for key in hollow["search_record"]:
            hollow["search_record"][key] = None
        self.assertFalse(mod09.validate_search_record(hollow))


if __name__ == "__main__":
    unittest.main()
