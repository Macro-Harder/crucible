"""Step 14 re-run closing cure pins.

One file for the five closing cure items: TA-56 and C-37 at
MOD-11 under the Manager rulings of the re-run, and the residual
special Latin letter class at MOD-01, MOD-03, MOD-04, MOD-10,
and MOD-14 under the Lead Engineer findings F-LE-R-01,
F-LE-R-02, and F-LE-R-03. The barred money name below stands
built by joining parts, so this file carries no joined spelling
of its own.
"""
import unittest

from crucible import mod01, mod03, mod04, mod10, mod11, mod12, mod14


_MONEY_PLAIN = "real" + "money" + "value"

_SPECIAL_LATIN = (
    ("\u00e6", "ae"), ("\u0153", "oe"), ("\u00f8", "o"),
    ("\u0111", "d"), ("\u0142", "l"), ("\u00df", "ss"),
    ("\u00fe", "th"), ("\u00f0", "d"), ("\u0127", "h"),
    ("\u014b", "n"), ("\u0192", "f"), ("\u0131", "i"),
    ("\u0167", "t"),
)

_SPECIAL_LATIN_CAPITALS = (
    ("\u00c6", "ae"), ("\u0152", "oe"), ("\u00d8", "o"),
    ("\u0110", "d"), ("\u0141", "l"), ("\u1e9e", "ss"),
    ("\u00de", "th"), ("\u00d0", "d"), ("\u0126", "h"),
    ("\u014a", "n"), ("\u0191", "f"), ("\u0166", "t"),
)


def _form4(**overrides):
    instance = mod01.minimal_valid_instance("4")
    instance.update(overrides)
    return instance


def _run_record(entry=None):
    record = {"run_class": "screening", "seed_domain": "screening"}
    if entry:
        record.update(entry)
    return record


class TestTA56RegistryRunLogClaim(unittest.TestCase):
    ENTRY = {"phase_judgements": {"before_runs": "judged",
                                  "after_runs": "judged"}}

    def test_no_run_log_among_inputs_states_no_comparison(self):
        judged = mod11.judge_registry_entry(
            self.ENTRY, compiler="registrar",
            checker="independent checker")
        self.assertEqual(judged["before_runs_judged_for"], "lateness")
        self.assertEqual(judged["after_runs_judged_for"], "completeness")
        self.assertFalse(judged["compared_against_run_log"])

    def test_run_log_handed_in_states_the_comparison(self):
        judged = mod11.judge_registry_entry(
            self.ENTRY, compiler="registrar",
            checker="independent checker",
            run_log={"runs": ["run-1"]})
        self.assertTrue(judged["compared_against_run_log"])
        self.assertTrue(mod11.validate_registry_entry(
            self.ENTRY, compiler="registrar",
            checker="independent checker",
            run_log={"runs": ["run-1"]}))

    def test_run_log_carried_on_the_entry_states_the_comparison(self):
        entry = dict(self.ENTRY, run_log={"runs": ["run-1"]})
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="independent checker")
        self.assertTrue(judged["compared_against_run_log"])

    def test_compiler_as_checker_states_no_comparison(self):
        judged = mod11.judge_registry_entry(
            self.ENTRY, compiler="registrar", checker="registrar",
            run_log={"runs": ["run-1"]})
        self.assertFalse(judged["compared_against_run_log"])
        self.assertFalse(mod11.validate_registry_entry(
            self.ENTRY, compiler="registrar", checker="registrar",
            run_log={"runs": ["run-1"]}))


class TestC37WeeklyContainerValidation(unittest.TestCase):
    def test_thirty_copies_of_a_plain_string_stand_refused(self):
        with self.assertRaises(ValueError):
            mod11.make_weekly_container("W1", ["plain string"] * 30)

    def test_items_outside_the_identifier_form_stand_refused(self):
        for item in ("plain string", "unit one", "", "U01", 7, None,
                     {"unit": "u01"}, ["u01"]):
            with self.assertRaises(ValueError, msg=repr(item)):
                mod11.make_weekly_container("W1", ["u01", item])

    def test_refusal_names_its_form(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("W1", ["plain string"])
        self.assertIn("refused", str(caught.exception))

    def test_identifier_form_units_stand_counted_as_before(self):
        units25 = ["u%02d" % n for n in range(1, 26)]
        units27 = units25 + ["u26", "u27"]
        at_cap = mod11.make_weekly_container("W25", units25)
        self.assertEqual(at_cap["count"], 25)
        self.assertEqual(at_cap["headline_units"], units25)
        self.assertEqual(at_cap["held_count"], 0)
        beyond = mod11.make_weekly_container("W26", units27)
        self.assertEqual(beyond["count"], 25)
        self.assertEqual(beyond["held_units"], ["u26", "u27"])
        self.assertEqual(beyond["held_count"], 2)
        following = mod11.next_weekly_container("W27", beyond, ["u28"])
        self.assertEqual(following["headline_units"],
                         ["u26", "u27", "u28"])
        self.assertEqual(following["count"], 3)


class TestSpecialLatinFoldCoverage(unittest.TestCase):
    def test_each_surface_fold_reads_the_class(self):
        for letter, reading in _SPECIAL_LATIN + _SPECIAL_LATIN_CAPITALS:
            dressed = "x" + letter + "y"
            expected = "x" + reading + "y"
            self.assertEqual(
                mod01._folded_money_key(dressed), expected, dressed)
            self.assertIn(
                expected, mod03._folded_readings(dressed), dressed)
            self.assertIn(
                expected, mod04._folded_readings(dressed), dressed)
            self.assertIn(
                expected, mod10._fold_variants(dressed), dressed)
            self.assertEqual(
                mod14._canonicalise_text(dressed), expected, dressed)


class TestResidualMoneyDresses(unittest.TestCase):
    DRESSES = (
        "rea\u0142moneyvalue",
        "realm\u00f8neyvalue",
        "realmo\u014beyvalue",
        "REA\u0141MONEYVALUE",
        "realm\u00f8\u014beyvalue",
    )

    def test_mod01_refuses_each_dress(self):
        for name in self.DRESSES:
            instance = _form4(**{name: 500})
            self.assertIs(
                mod01.validate_record("4", instance), False, name)
            self.assertIs(
                mod01.run_is_reportable("4", instance), False, name)

    def test_mod12_agrees_on_each_dress(self):
        for name in self.DRESSES:
            self.assertFalse(
                mod12.validate_run_record(_run_record({name: 500})),
                name)

    def test_mod01_controls_hold(self):
        self.assertIs(mod01.validate_record(
            "4", _form4(**{"caf\u00e9_label": "stated value"})), True)
        self.assertIs(mod01.validate_record(
            "4", _form4(**{"\u043f\u0440\u0438\u043c\u0435\u0440": "x"})),
            True)
        self.assertIs(mod01.validate_record(
            "4", _form4(stake={"amount": 5})), True)
        self.assertIs(mod01.validate_record(
            "4", _form4(**{_MONEY_PLAIN: None})), True)
        self.assertIs(mod01.validate_record(
            "4", _form4(stake={"amount_of_work": 5,
                               "currency_of_record": "stated value"})),
            True)


class TestResidualAnchorDresses(unittest.TestCase):
    NAMES = (
        "anchor_scenario_va\u0142ues",
        "anchor_scenari\u00f8_values",
        "a\u014bchor_scenario_values",
        "ANCHOR_SCENARIO_VA\u0141UES",
    )

    def test_counts_checked_at_mod01_and_mod12(self):
        for name in self.NAMES:
            for count, stands in ((4, False), (2, False), (3, True)):
                values = {"abcd"[index] for index in range(count)}
                self.assertIs(
                    mod01.validate_record(
                        "4", _form4(**{name: set(values)})),
                    stands, (name, count))
                self.assertEqual(
                    mod12.validate_run_record(
                        _run_record({name: set(values)})),
                    stands, (name, count))


class TestResidualMoneyAtMod10(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_dresses_refused_at_retention(self):
        for index, name in enumerate(
                TestResidualMoneyDresses.DRESSES):
            store = mod10.RecorderStore(store_kind="sweep")
            with self.assertRaises(ValueError, msg=name):
                store.retain_run_record(
                    {"run_id": "run-closing-money-%d" % index,
                     name: 500})

    def test_controls_hold_at_retention(self):
        store = mod10.RecorderStore(store_kind="sweep")
        kept_none = store.retain_run_record(
            {"run_id": "run-closing-none", _MONEY_PLAIN: None})
        self.assertEqual(kept_none["run_id"], "run-closing-none")
        kept_amount = store.retain_run_record(
            {"run_id": "run-closing-amount", "amount": 5})
        self.assertEqual(kept_amount["run_id"], "run-closing-amount")
        kept_lawful = store.retain_run_record({
            "run_id": "run-closing-lawful",
            "caf\u00e9_menu": "stated",
            "amount_notes": 5,
            "currency_notes": "stated",
        })
        self.assertEqual(kept_lawful["run_id"], "run-closing-lawful")


class TestResidualBarredKeys(unittest.TestCase):
    KEYS = (
        "ca\u014bary",
        "grou\u014bdtruth",
        "members\u0127ip",
        "groundtrut\u0127",
        "gr\u00f8undtruth",
        "groun\u0111truth",
        "ground\u0167ruth",
        "CA\u014aARY",
        "Members\u0127ip",
        "\u0142abel",
        "s\u0142eeper",
    )

    CLEAN = (
        "activity", "labelled", "labels", "honest_score", "kept",
        "xsleeper", "sleeperx", "caf\u00e9_label",
    )

    def test_barred_at_mod03(self):
        for key in self.KEYS:
            record = {"feature_values": {key: "v"}}
            self.assertTrue(
                mod03.record_carries_ground_truth(record), key)
            self.assertFalse(
                mod03.validate_detection_input(record), key)
            stripped = mod03.strip_ground_truth(
                {"feature_values": {key: "v", "activity": 1}})
            self.assertNotIn(key, stripped["feature_values"], key)

    def test_barred_at_mod04_checker_and_projection(self):
        for key in self.KEYS:
            self.assertTrue(mod04._is_barred_key(key), key)
            self.assertTrue(mod04.view_record_carries_barred_field(
                {"view_contents": {"x": {key: "v"}}}), key)
            projected = mod04.project_detection_input({
                "agent_identifier": "agent-1", "day": 1,
                "feature_values": {key: "v", "keep": 1},
                "rule_records": [{"detail": {key: "v", "kept": 2}}],
            })
            self.assertEqual(projected["feature_values"], {"keep": 1},
                             key)
            self.assertEqual(
                projected["rule_records"], [{"detail": {"kept": 2}}],
                key)

    def test_barred_at_mod10_runner(self):
        for key in self.KEYS:
            self.assertTrue(mod10._is_barred_view_key(key), key)

    def test_clean_keys_admitted_at_all_three(self):
        for key in self.CLEAN:
            self.assertFalse(mod03.record_carries_ground_truth(
                {"feature_values": {key: "v"}}), key)
            self.assertFalse(mod04._is_barred_key(key), key)
            self.assertFalse(mod10._is_barred_view_key(key), key)


class TestMod10RunnerRefusesResidualKeys(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def view_record(self, contents):
        return {
            "run_identifier": "run-closing-view",
            "viewer_identifier": "viewer-1",
            "simulated_day": 5,
            "scheduling_position_identifier": "position-1",
            "rule_version_set": "rule-set-1",
            "view_contents": contents,
            "reputation_and_band_values": {"band": "stated"},
            "graph_position_as_seen": "stated",
            "first_seen_day_per_record": {"item": 3},
            "delay_applied_per_record": {"item": 1},
            "completeness_state": "complete",
            "building_component": "Recorder",
            "delivering_contract": "stated",
            "selection_rule_version": "rule-set-1",
        }

    def test_runner_refuses_each_residual_key(self):
        for key in TestResidualBarredKeys.KEYS:
            record = self.view_record([{"detail": {key: "v"}}])
            with self.assertRaises(ValueError, msg=key):
                mod10.run_view_leak_check(record)

    def test_runner_admits_lawful_record(self):
        result = mod10.run_view_leak_check(
            self.view_record([{"activity": "stated",
                               "caf\u00e9_label": "stated"}]))
        self.assertTrue(result["reportable"])


class TestResidualOperatorDresses(unittest.TestCase):
    TARGETS = (
        "sea\u0142ed family record",
        "cl\u00f8sed run record",
        "sealed family rec\u00f8rd",
        "checkpoi\u014bt set",
        "checkpoint se\u0167",
        "SEA\u0141ED FAMILY RECORD",
    )

    def test_delete_refused_on_each_dress(self):
        for target in self.TARGETS:
            action = {"kind": "delete", "target": target}
            self.assertFalse(
                mod14.validate_operator_action(action), action)

    def test_destroy_refused_on_closed_dress(self):
        action = {"kind": "destroy",
                  "target": "cl\u00f8sed run record",
                  "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action))

    def test_lawful_controls_admitted(self):
        for target in ("sealed family", "family record archive",
                       "record archive", "checkpoint",
                       "caf\u00e9 record archive",
                       "r\u00e9sum\u00e9 file"):
            action = {"kind": "delete", "target": target}
            self.assertTrue(
                mod14.validate_operator_action(action), action)
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed run record",
             "path": "flag rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "sealed family record"}))


if __name__ == "__main__":
    unittest.main()
