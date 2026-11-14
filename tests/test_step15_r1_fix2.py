# Step 15 Round 1 fix tests, cluster 2. MOD-14 and MOD-12 surfaces.
import json
import unittest
from pathlib import Path

import crucible.mod01 as mod01
import crucible.mod04 as mod04
import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod12 as mod12
import crucible.mod14 as mod14

MONEY_KEY = "real_" + "money_value"
ANCHOR_VALUES_KEY = "anchor_" + "scenario_values"
ANCHOR_SET_KEY = "anchor_" + "set"


def conforming_unit():
    unit = {field: "value for " + field for field in mod11.HEADLINE_UNIT_FIELDS}
    unit["claim_sentence"] = (
        "At the sampled points within the stated scope, the result "
        "holds for the sampled points only, and nothing is claimed "
        "beyond the stated limits.")
    unit["grounding_sentence"] = (
        "This unit rests on the retained run records within the "
        "stated scope, and its limits are that nothing is claimed "
        "beyond the sampled points in this unit.")
    unit["qualifiers_and_markings_block"] = (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording that "
        "DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes Parley "
        "Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: no anchor scenario is used in "
        "this unit.")
    return unit


class TestShellCommands(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def test_all_nine_commands_delegate_or_fail_by_name(self):
        started = mod14.run_command(
            "start_run", {"run_class": "screening", "family_id": "fam-1"},
            run_id="run-1")
        self.assertEqual(started["failure"], "DERIVATION-GATED")
        self.assertFalse(started["run_started"])
        swept = mod14.run_command(
            "start_sweep", {"family_id": "fam-1"}, run_id="run-1")
        self.assertEqual(swept["failure"], "DERIVATION-GATED")
        self.assertFalse(swept["run_started"])
        kind = mod14.run_command("store_kind_check", {"kind": "sweep"})
        self.assertTrue(kind["store_kind_ok"])
        written = mod14.run_command(
            "write_store",
            {"record": {"run_id": "run-fix2", "run_identifier": "run-fix2"},
             "store_kind": "sweep"})
        self.assertNotEqual(written.get("form"), "carriage only in this act")
        self.assertEqual(written["run_id"], "run-fix2")
        read = mod14.run_command(
            "read_store", {"run_id": "run-fix2", "store_kind": "sweep"})
        self.assertEqual(read["run_id"], "run-fix2")
        missing = mod14.run_command(
            "read_store", {"run_id": "run-absent", "store_kind": "sweep"},
            run_id="run-9")
        self.assertIn("failure", missing)
        self.assertFalse(missing["swallowed"])
        pilot = mod14.run_command(
            "run_pilot", {"use": "timing", "artefact": {"figure": 3}})
        self.assertEqual(pilot["confinement_label"], "pilot confined")
        self.assertEqual(pilot["figure"], 3)
        barred = mod14.run_command(
            "run_pilot", {"use": "behaviour fitting", "artefact": {"figure": 3}},
            run_id="run-2")
        self.assertIn("failure", barred)
        self.assertNotIn("confinement_label", barred.get("form", ""))
        self.assertIn("confinement", json.dumps(barred).lower())
        report = mod14.run_command("assemble_report", {"family_id": "fam-1"},
                                   run_id="run-3")
        self.assertNotEqual(report.get("form"), "carriage only in this act")
        self.assertTrue(report.get("not_built"))
        self.assertIn("failure", report)
        outside = mod14.run_command(
            "outside_call_check",
            {"dependency_manifest": {"entries": []},
             "call_log": {"calls": [{"outside_call": False}]}})
        self.assertEqual(outside["field"], "outside_call_check")
        self.assertEqual(outside["outcome"], "no outside calls read")
        records = [
            {"week": "W1", "headline_unit_identifiers": ["u1", "u2"]},
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
        ]
        counted = mod14.run_command(
            "weekly_headline_count",
            {"summary_records": records, "week": "W1"})
        self.assertEqual(counted["count"], 2)
        unknown = mod14.run_command("no_such_command", {}, run_id="run-9")
        self.assertIn("failure", unknown)
        self.assertFalse(unknown["swallowed"])

    def test_pilot_runner_screens_barred_artefact(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"figure": 1, MONEY_KEY: 999})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"figure": 1, ANCHOR_SET_KEY: ["a", "b"]})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run(
                "timing", {"figure": 1, "settles_population_behaviour_rate": True})
        out = mod14.pilot_run("timing", {"figure": 1})
        self.assertEqual(out["confinement_label"], "pilot confined")
        self.assertEqual(out["figure"], 1)

    def test_operator_action_normalises_act_and_target(self):
        bad = [
            {"kind": "delete", "target": "sealed family record"},
            {"kind": "destroy", "target": "checkpoint set"},
            {"target": "sealed family record"},
            {"kind": "edit", "target": "Sealed Family Record"},
            {"kind": "edit", "target": "sealed family records"},
            {"kind": "edit", "target": "sealed_family_record"},
            {"kind": "remove", "target": "closed run record", "path": "direct"},
            {"kind": "update", "target": "checkpoint sets", "path": "direct"},
        ]
        for action in bad:
            self.assertFalse(mod14.validate_operator_action(action), action)
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed run record", "path": "flag rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": "checkpoint set", "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "checkpoint set"}))

    def test_program_check_surfaces_carry_reasons(self):
        bogus = mod14.run_command("store_kind_check", {"kind": "bogus"})
        self.assertFalse(bogus["store_kind_ok"])
        self.assertIn("sweep", bogus["valid_kinds"])
        self.assertEqual(bogus["kind_standing"], "unknown")
        self.assertTrue(bogus["reason"])
        missing = mod14.run_command("store_kind_check", {})
        self.assertFalse(missing["store_kind_ok"])
        self.assertEqual(missing["kind_standing"], "missing")
        verdict = mod14.validate_operator_action_with_reason(
            {"kind": "edit", "target": "sealed family record"})
        self.assertFalse(verdict["allowed"])
        self.assertIn("sealed family record", verdict["reason"])

    def test_error_carriage_preserves_failure_fields(self):
        try:
            mod10.read_run_record("run-absent")
            self.fail("lookup should fail")
        except mod10.LookupFailure as failure:
            carriage = mod14.error_carriage(failure, run_id="run-9", stage="read")
        self.assertEqual(carriage["run_identifier"], "run-absent")
        self.assertEqual(carriage["run_status"], "failed")
        self.assertFalse(carriage["complete"])
        self.assertTrue(carriage["name"])
        gated = mod04.GatedRun("gated act under test")
        carriage = mod14.error_carriage(gated, run_id="run-9", stage="start")
        self.assertEqual(carriage["gate"], mod04.GATE_EXECUTABLE_RUNS)
        self.assertEqual(carriage["failure_value"]["failure"],
                         mod04.GATED_FAILURE_NAME)

    def test_flag_evaluation_bounds(self):
        record = {"run_id": "r1", "retention_tier": "Tier 2",
                  "flag_conditions_fired": ["condition a"]}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                record, inputs={"flag_conditions_fired": ["condition a"]},
                outcome="promote", tier="Tier 99 invented")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                record, inputs={"flag_conditions_fired": ["condition a"]},
                outcome="promote", tier=None)
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(record, inputs=None, outcome="promote",
                                  tier="Tier 3")
        bare = {"run_id": "r2", "retention_tier": "Tier 2"}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(bare, inputs="some inputs", outcome="promote",
                                  tier="Tier 3")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(None, inputs="x", outcome="promote",
                                  tier="Tier 3")
        promoted = mod14.flag_evaluation(
            record, inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3")
        self.assertEqual(promoted["retention_tier"], "Tier 3")

    def test_weekly_headline_count_canonical_field_and_named_failure(self):
        records = [
            {"week": "W1", "headline_unit_identifiers": ["u1", "u2"]},
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W2", "headline_unit_identifiers": ["u3"]},
        ]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 2)
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count([{"week": "W1"}], "W1")
        own = mod10.summary_record_for_run("run-absent")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count([own], "W1")

    def test_confined_programme_forms(self):
        contract = mod14.sweep_level_determinism_contract(
            {"material_class": "pilot confined", "figure": 1})
        self.assertEqual(contract["confinement"], "pilot confined material only")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.sweep_level_determinism_contract({"material_class": "sweep"})
        census = mod14.nondeterminism_census(
            {"confinement_label": "pilot confined", "figure": 1})
        self.assertIn("pilot confined material only", census["face_statement"])
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.nondeterminism_census({"figure": 1})
        families = [
            {"synthetic": True, "retained_under_first_rule": True,
             "retained_under_second_rule": False},
            {"synthetic": True, "retained_under_first_rule": True,
             "retained_under_second_rule": True},
        ]
        paired = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(paired["paired_field"]["first_rule_retained"], 2)
        self.assertEqual(paired["paired_field"]["second_rule_retained"], 1)
        self.assertNotIn("total", paired)
        self.assertNotIn("total", paired["paired_field"])
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.dual_rule_retention_simulation([{"synthetic": False}])

    def test_flag_evaluation_listed_and_dispatched(self):
        entries = {e["command"]: e for e in mod14.command_surface()}
        self.assertIn("flag_evaluation", entries)
        record = {"run_id": "r1", "retention_tier": "Tier 2",
                  "flag_conditions_fired": ["condition a"]}
        out = mod14.run_command(
            "flag_evaluation",
            {"summary_record": record,
             "inputs": {"flag_conditions_fired": ["condition a"]},
             "outcome": "promote", "tier": "Tier 3"})
        self.assertEqual(out["retention_tier"], "Tier 3")
        refused = mod14.run_command(
            "flag_evaluation",
            {"summary_record": record, "outcome": "promote",
             "tier": "Tier 99 invented"}, run_id="run-4")
        self.assertIn("failure", refused)
        self.assertFalse(refused["swallowed"])

    def test_command_surface_documents_inputs(self):
        entries = {e["command"]: e for e in mod14.command_surface()}
        self.assertEqual(len(entries), 10)
        for name, entry in entries.items():
            self.assertTrue(entry["purpose"], name)
            self.assertIn("required_inputs", entry)
            self.assertIn("optional_inputs", entry)
            self.assertIn("run_command", entry["example"])
        readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(
            encoding="utf-8")
        for name in entries:
            self.assertIn(name, readme)
        self.assertIn("run_command", readme)
        runbook = mod14.operator_runbook()
        self.assertIn("outside call", runbook["outside_call_wording_standing"])

    def test_runbook_parity_with_readme(self):
        readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(
            encoding="utf-8")
        section = readme.split("## Operator runbook", 1)[1]
        steps = []
        for line in section.splitlines():
            line = line.strip()
            if len(line) > 3 and line[0].isdigit() and line[1] == ".":
                steps.append(line[2:].strip().rstrip(".").lower())
        mine = [s.rstrip(".").lower()
                for s in mod14.operator_runbook()["steps"]]
        self.assertEqual(mine, steps)


class TestFamilyRecord(unittest.TestCase):
    def test_family_record_shape_one_form_and_validator_agreement(self):
        record = mod12.make_family_record(family_id="fam-fix2")
        for field in mod01.form_fields("1"):
            self.assertIn(field, record)
        self.assertTrue(mod12.validate_family_record(record))
        self.assertTrue(mod11.validate_family_record(record))
        sealed = mod12.seal_family_record(record)
        self.assertIsInstance(sealed["seal"], dict)
        self.assertTrue(sealed["seal"]["version"])
        self.assertTrue(sealed["seal"]["hash"])
        manifest = sealed.get("sweep_manifest") or mod12.sweep_manifest(record)
        self.assertEqual(manifest["family_identifier"], "fam-fix2")
        old = {"family_id": "fam-old", "sealed": False, "claims": ["c"],
               "kill_checks": [], "scheduling_order_identifier": None,
               "registry_basis_fields": {}, "results_seen": False,
               "form": "family record"}
        self.assertFalse(mod12.validate_family_record(old))
        self.assertFalse(mod11.validate_family_record(old))

    def test_family_completeness_before_seal(self):
        record = mod12.make_family_record(family_id="fam-fix2")
        for item in mod12.FAMILY_COMPLETENESS_ITEMS:
            self.assertIn(item, record)
            broken = dict(record)
            del broken[item]
            self.assertFalse(mod12.validate_family_record(broken), item)
            with self.assertRaises(mod12.NamedControllerFailure):
                mod12.seal_family_record(broken)
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])

    def test_family_validator_names_missing_fields(self):
        self.assertFalse(mod12.validate_family_record({}))
        failures = mod12.family_record_validation_failures({})
        self.assertTrue(failures)
        joined = " ".join(failures)
        self.assertIn("family_identifier", joined)
        complete = mod12.make_family_record(family_id="fam-fix2")
        self.assertEqual(mod12.family_record_validation_failures(complete), [])


class TestControllerValidators(unittest.TestCase):
    def test_run_record_validation(self):
        self.assertFalse(mod12.validate_run_record({}))
        self.assertFalse(mod12.validate_run_record(
            {"run_class": "headline", "seed_domain": "screening"}))
        self.assertFalse(mod12.validate_run_record(
            {"run_class": "confirmation", "seed_domain": "screening"}))
        self.assertTrue(mod12.validate_run_record(
            {"run_class": "screening", "seed_domain": "screening"}))
        self.assertTrue(mod12.validate_run_record(
            {"run_class": "headline", "seed_domain": "held_out"}))
        self.assertFalse(mod12.validate_run_record({"run_class": "headline"}))
        money = {"run_class": "screening", "seed_domain": "screening",
                 MONEY_KEY: 500}
        self.assertFalse(mod12.validate_run_record(money))
        nested = {"run_class": "screening", "seed_domain": "screening",
                  "payload": {"amount": 5, "currency": "test value"}}
        self.assertFalse(mod12.validate_run_record(nested))
        four = {"run_class": "screening", "seed_domain": "screening",
                ANCHOR_VALUES_KEY: ["a", "b", "c", "d"]}
        self.assertFalse(mod12.validate_run_record(four))
        three = {"run_class": "screening", "seed_domain": "screening",
                 ANCHOR_VALUES_KEY: ["a", "b", "c"]}
        self.assertTrue(mod12.validate_run_record(three))

    def test_readout_status_six_conditions(self):
        full = {
            "claim_in_bounding_form": True,
            "bound_fixed_in_advance": True,
            "search_complete": True,
            "material_failure_found": False,
            "search_completed_at_rung": 6,
            "tolerance_and_replication_rule": "stated rule",
            "confirmation_under_family_discipline": True,
            "check_artefact_battery": {
                "passed": ["A-01", "A-02", "A-03", "A-04", "A-05", "A-06",
                           "A-07", "A-08", "A-09", "A-10", "A-11"]},
            "assumption_set_and_rows_inside_result": True,
        }
        self.assertEqual(mod12.readout_status(full)["form"], "established")
        cases = [
            ("claim_in_bounding_form", False, 1),
            ("search_complete", False, 2),
            ("bound_fixed_in_advance", False, 2),
            ("tolerance_and_replication_rule", None, 3),
            ("confirmation_under_family_discipline", False, 4),
            ("check_artefact_battery", {"passed": ["A-04"]}, 5),
            ("assumption_set_and_rows_inside_result", False, 6),
        ]
        for key, value, condition in cases:
            broken = dict(full)
            broken[key] = value
            status = mod12.readout_status(broken)
            self.assertNotEqual(status["form"], "established", key)
            self.assertEqual(status["named_condition"], condition, key)
        legacy = {"search_complete": False, "material_failure_found": True,
                  "bound_fixed_in_advance": True}
        status = mod12.readout_status(legacy)
        self.assertEqual(status["form"], "lower_bound")
        self.assertEqual(status["named_condition"], 2)

    def test_decay_arm_readout_named_slices(self):
        readout = mod12.decay_arm_readout(fixture="F-14")
        rows = readout["planes"][0]["companion_table"]
        expected = ["7 days", "about 14 days", "about 69 days",
                    "180 day run length scale", "about 693 days", "infinite"]
        self.assertEqual([row["half_life"] for row in rows[:6]], expected)
        text = json.dumps(readout)
        self.assertNotIn("control value", text)
        self.assertNotIn("result value", text)
        self.assertNotIn("stated per slice", text)

    def test_sample_statement_on_readouts_and_refusals(self):
        refusal = mod12.start_run(run_class="screening", family_id="fam-1")
        statement = refusal["sample_statement"]
        self.assertEqual(statement["n"], 0)
        self.assertEqual(statement["sample"], "none")
        for count in statement["runs_completed_by_class"].values():
            self.assertEqual(count, 0)
        self.assertIn("DQ7-02", statement["bound"])
        runs = [{"run_class": "screening"}, {"run_class": "screening"},
                {"run_class": "headline"}]
        readout = mod12.screening_readout(fixture="F-17", runs=runs)
        statement = readout["sample_statement"]
        self.assertEqual(statement["runs_completed_by_class"]["screening"], 2)
        self.assertEqual(statement["runs_completed_by_class"]["headline"], 1)
        decay = mod12.decay_arm_readout(fixture="F-14")
        self.assertIn("sample_statement", decay)

    def test_sweep_programme_hostile_magnitudes(self):
        self.assertFalse(mod12.validate_sweep_programme(
            {"families": [{"name": "hostile", "standing": "required"}]}))
        self.assertTrue(mod12.validate_sweep_programme(
            {"families": [{"name": "hostile", "standing": "required",
                           "magnitudes": {"kind a": 3}}]}))
        self.assertFalse(mod12.validate_sweep_programme({"families": []}))

    def test_record_version_sets_canonical_order(self):
        first = mod12.record_version_sets(
            record_kinds=("witness_entry", "checkpoint", "run_record"))
        second = mod12.record_version_sets(
            record_kinds=("run_record", "witness_entry", "checkpoint"))
        self.assertEqual(list(first.keys()), sorted(first.keys()))
        self.assertEqual(json.dumps(first), json.dumps(second))

    def test_winning_regime_and_top_up_named_failures(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.winning_regime([("only-one",)] * 30)
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.top_up_applies("high", 30)
        self.assertTrue(mod12.winning_regime([(0.6, 0.4)] * 30))
        self.assertTrue(mod12.top_up_applies(0.5, 30))
        self.assertFalse(mod12.top_up_applies(0.1, 30))

    def test_gated_refusal_form_and_input_validation(self):
        bogus = mod12.start_run(run_class="bogus", family_id="fam-1")
        self.assertNotEqual(bogus.get("failure"), "DERIVATION-GATED")
        self.assertFalse(bogus["run_started"])
        self.assertIn("input", bogus["failure"].lower())
        missing_family = mod14.run_command(
            "start_run", {"run_class": "screening"})
        self.assertIn("input", missing_family["failure"].lower())
        missing_class = mod14.run_command("start_run", {"family_id": "fam-1"})
        self.assertIn("input", missing_class["failure"].lower())
        gated = mod12.start_run(run_class="screening", family_id="fam-1")
        self.assertEqual(gated["failure"], "DERIVATION-GATED")
        self.assertIn("adoption record", gated["ground_in_words"])
        self.assertTrue(gated["next_step"])


class TestHeadlineEnvelope(unittest.TestCase):
    def test_probe_units_fail_validation_and_quotation(self):
        all_x = {field: "x" for field in mod11.HEADLINE_UNIT_FIELDS}
        self.assertFalse(mod11.validate_headline_unit(all_x))
        empty_region = conforming_unit()
        empty_region["holding_region"] = ""
        self.assertFalse(mod11.validate_headline_unit(empty_region))
        hidden = conforming_unit()
        hidden["assumption_record"] = "redacted"
        hidden["witness_block"] = "see elsewhere"
        self.assertFalse(mod11.validate_headline_unit(hidden))
        with self.assertRaises(Exception):
            mod11.quote_headline_unit(hidden)
        everywhere = conforming_unit()
        everywhere["claim_sentence"] = "The claim holds everywhere."
        everywhere["qualifiers_and_markings_block"] = "none"
        self.assertFalse(mod11.validate_headline_unit(everywhere))
        structured = conforming_unit()
        structured["holding_region"] = {"prose": "farm size 200 to 400"}
        self.assertFalse(mod11.validate_headline_unit(structured))
        good = conforming_unit()
        self.assertTrue(mod11.validate_headline_unit(good))
        self.assertEqual(mod11.quote_headline_unit(good), good)

    def test_envelope_claim_on_unit_shape(self):
        good = conforming_unit()
        self.assertTrue(mod11.validate_envelope_claim(good))
        hidden = conforming_unit()
        hidden["assumption_record"] = "redacted"
        self.assertFalse(mod11.validate_envelope_claim(hidden))
        claim = {"scope": "sampled points and stated ranges only",
                 "holds": False, "failure_witness": "witness point P-7",
                 "claims_between_points": False,
                 "monotonicity_claimed": False,
                 "interpolation_claimed": False}
        self.assertTrue(mod11.validate_envelope_claim(claim))
        self.assertFalse(mod11.validate_envelope_claim(
            dict(claim, claims_between_points=True)))


if __name__ == "__main__":
    unittest.main()
