"""Fix wave 3 pins, Builder 11.

Pins for register rows R3-011, R3-014, R3-015, R3-026, R3-031,
R3-032, R3-044, R3-047, R3-051, R3-054, R3-055, R3-056, R3-058,
R3-059, R3-061, and R3-062, each in its distinguishing case.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from crucible import mod02, mod03, mod07

ROOT = Path(__file__).resolve().parent.parent


def deep_list(depth=150):
    value = "leaf"
    for _ in range(depth):
        value = [value]
    return value


def deep_key_dict(depth=150):
    key = "leaf"
    for _ in range(depth):
        key = (key,)
    return {key: "ok"}


def deep_tuple_key(depth=150):
    key = "leaf"
    for _ in range(depth):
        key = (key,)
    return {key: "clean"}


class LyingStr(str):
    __hash__ = str.__hash__

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class TestR3011FoldClasses(unittest.TestCase):
    def barred(self, key):
        return mod03.record_carries_ground_truth({"wrap": {key: 1}})

    def test_cyrillic_e_as_e(self):
        self.assertTrue(self.barred("m\u044dmbership"))
        self.assertFalse(mod03.validate_detection_input(
            {"wrap": {"m\u044dmbership": 1}}))

    def test_cyrillic_el_as_l(self):
        self.assertTrue(self.barred("labe\u043b"))
        self.assertTrue(self.barred("\u043babel"))

    def test_greek_psi_as_ps(self):
        self.assertTrue(self.barred("membershi\u03c8"))

    def test_greek_omega_as_o(self):
        self.assertTrue(self.barred("gr\u03c9und_truth"))

    def test_controls_both_ways(self):
        self.assertTrue(self.barred("membership"))
        self.assertFalse(self.barred("clean_field"))


class TestR3026SymbolReadings(unittest.TestCase):
    def barred(self, key):
        return mod03.record_carries_ground_truth({"wrap": {key: 1}})

    def test_cent_sign_as_c(self):
        self.assertTrue(self.barred("\u00a2anary"))

    def test_section_sign_as_s(self):
        self.assertTrue(self.barred("member\u00a7hip"))

    def test_plus_sign_as_t(self):
        self.assertTrue(self.barred("ground_+ruth"))


class TestR3051CherokeeCoptic(unittest.TestCase):
    def barred(self, key):
        return mod03.record_carries_ground_truth({"wrap": {key: 1}})

    def test_cherokee_letter(self):
        self.assertTrue(self.barred("\u13b7embership"))
        self.assertTrue(self.barred("lab\u13acl"))

    def test_coptic_letter(self):
        self.assertTrue(self.barred("l\u2c81bel"))
        self.assertTrue(self.barred("g\u2ca3ound_truth"))


class LyingList(list):
    def __iter__(self):
        return iter(["alpha", "beta"])


class LyingEntry(dict):
    def get(self, key, default=None):
        return "alpha"


class LyingStreamDict(dict):
    def __contains__(self, key):
        return True

    def __getitem__(self, key):
        return ["alpha", "beta"]


class TestR3014StreamSetProtocols(unittest.TestCase):
    def not_admitted(self, counts, stream_set):
        try:
            result = mod02.validate_stream_cardinality(
                counts=counts, stream_set=stream_set)
        except ValueError:
            return
        self.assertFalse(result)

    def test_inventory_iteration_limb(self):
        inventory = LyingList(["gamma"])
        self.not_admitted(
            {"alpha": 1, "beta": 1},
            {"stream_class_inventory": inventory})

    def test_entry_get_limb(self):
        entry = LyingEntry({"bogus": 1})
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"alpha": 1},
                stream_set={"stream_class_inventory": [entry]})

    def test_dict_containment_and_item_limb(self):
        stream_set = LyingStreamDict({"gamma": 1})
        self.not_admitted({"alpha": 1, "beta": 1}, stream_set)

    def test_plain_control_both_ways(self):
        stream_set = {"stream_class_inventory": ["alpha", "beta"]}
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"alpha": 1, "beta": 1}, stream_set=stream_set))
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"alpha": 1}, stream_set=stream_set))


class TestR3015PlainDictNoInventory(unittest.TestCase):
    def test_plain_dict_no_inventory_refused(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"alpha": 1, "beta": 1},
                stream_set={"alpha": 1, "beta": 1})


class TestR3031CopyGuardKeyPosition(unittest.TestCase):
    def test_make_adapter_choice_deep_key_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod07.make_adapter_choice(
                "c1", "reading", "point", "gov", "fold",
                approval=deep_key_dict())
        self.assertIn("adapter copy stands refused", str(caught.exception))

    def test_seam_effect_report_deep_key_refused(self):
        with self.assertRaises(ValueError):
            mod07.seam_effect_report(deep_key_dict())

    def test_shallow_tuple_key_control(self):
        choice = mod07.make_adapter_choice(
            "c1", "reading", "point", "gov", "fold",
            approval={("a", "b"): 1})
        self.assertEqual(choice["choice_identifier"], "c1")


class TestR3032UnguardedCopySurfaces(unittest.TestCase):
    def test_interpretation_log_entry_deep(self):
        with self.assertRaises(ValueError):
            mod07.interpretation_log_entry(
                {"choice_identifier": deep_list()})

    def test_run_record_entry_deep(self):
        with self.assertRaises(ValueError):
            mod07.run_record_entry(
                {"choice_identifier": "c1", "approval": deep_list()})

    def test_append_reading_deep(self):
        with self.assertRaises(ValueError):
            mod07.append_reading(
                [{"choice_identifier": deep_list()}],
                {"choice_identifier": "c2"})

    def test_reading_for_result_deep(self):
        with self.assertRaises(ValueError):
            mod07.reading_for_result(
                [{"choice_identifier": "c1", "extra": deep_list()}],
                "c1")

    def test_slash_outcome_report_deep(self):
        with self.assertRaises(ValueError):
            mod07.slash_outcome_report({"value": deep_list()})

    def test_slash_outcome_report_cycle(self):
        cyclic = {}
        cyclic["self"] = cyclic
        with self.assertRaises(ValueError):
            mod07.slash_outcome_report({"value": cyclic})

    def test_shallow_controls(self):
        choice = {"choice_identifier": "c1"}
        self.assertEqual(
            mod07.interpretation_log_entry(choice)["choice_identifier"],
            "c1")
        report = mod07.slash_outcome_report({"value": 5})
        self.assertEqual(report["value"], 5)


class TestR3047GroundTruthKeyPosition(unittest.TestCase):
    def test_carries_deep_key_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.record_carries_ground_truth(deep_tuple_key())

    def test_strip_deep_key_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.strip_ground_truth(deep_tuple_key())

    def test_shallow_control(self):
        self.assertFalse(mod03.record_carries_ground_truth(
            {("clean",): 1}))
        self.assertEqual(
            mod03.strip_ground_truth({("clean",): 1}), {("clean",): 1})


class TestR3054AnchorMarkEquality(unittest.TestCase):
    def test_lying_mark_refused(self):
        record = mod03.anchor_scenario("AN-1", "setting")
        record["mark"] = LyingStr("wrong-mark")
        self.assertFalse(mod03.validate_anchor_scenario(record))

    def test_controls_both_ways(self):
        record = mod03.anchor_scenario("AN-1", "setting")
        self.assertTrue(mod03.validate_anchor_scenario(record))
        record["mark"] = "wrong-mark"
        self.assertFalse(mod03.validate_anchor_scenario(record))


class LyingFloat(float):
    def __mul__(self, other):
        return 999999

    def __rmul__(self, other):
        return 999999


class LyingInt(int):
    def __le__(self, other):
        return True


class TestR3055ColdSocietyOperators(unittest.TestCase):
    def test_lying_multiplication(self):
        result = mod03.cold_society_degree(
            100, envelope=LyingFloat(2.0), gate_passing_share=3.0)
        self.assertEqual(result, 6.0)

    def test_lying_day_comparison(self):
        result = mod03.cold_society_degree(
            LyingInt(500), envelope=2.0, gate_passing_share=3.0)
        self.assertEqual(result, 6.0)

    def test_plain_controls(self):
        self.assertEqual(mod03.cold_society_degree(
            100, envelope=2.0, gate_passing_share=3.0), 6.0)
        self.assertEqual(mod03.cold_society_degree(90), 0)


class TestR3056CountingBasisControl(unittest.TestCase):
    def test_mod03_boundary_lengths_containers_only(self):
        self.assertFalse(mod03.record_carries_ground_truth(deep_list(101)))
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.record_carries_ground_truth(deep_list(102))


class TestR3059FarmDictEdgeNoVouchee(unittest.TestCase):
    def test_empty_dict_edge_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(["a", "b"], farm_size=1, edges=[{}])

    def test_dict_edge_no_vouchee_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=1, edges=[{"voucher": "a"}])

    def test_valid_dict_edge_control(self):
        result = mod03.construct_farm(
            ["a", "b"], farm_size=2,
            edges=[{"voucher": "a", "vouchee": "b"}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1})


class TestR3061TracerContentlessNonString(unittest.TestCase):
    def set_field(self, field, value):
        records = mod07.tracer_passage_records("run-1")
        records[0][field] = value
        return records

    def test_point_in_run_non_string_blank(self):
        for value in ([], {}, False):
            with self.subTest(value=value):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    self.set_field("point_in_run", value)))

    def test_what_in_fact_passed_non_string_blank(self):
        for value in ([], {}, False):
            with self.subTest(value=value):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    self.set_field("what_in_fact_passed", value)))

    def test_control_valid_set(self):
        records = mod07.tracer_passage_records("run-1")
        self.assertTrue(mod07.validate_tracer_passage_set(records))


class TestR3062TracerNonStringItem(unittest.TestCase):
    def test_non_string_items_return_false(self):
        for value in (123, [], {}):
            with self.subTest(value=value):
                records = mod07.tracer_passage_records("run-1")
                records[0]["open_semantic_item"] = value
                self.assertFalse(
                    mod07.validate_tracer_passage_set(records))


class TestR3044ReverseOrder(unittest.TestCase):
    def run_unittest(self, args):
        return subprocess.run(
            [sys.executable, "-m", "unittest"] + args,
            cwd=str(ROOT), capture_output=True, text=True, timeout=600)

    def test_reverse_pair_order(self):
        proc = self.run_unittest([
            "tests.test_tg_10_3.TestFlagRuleAmendmentForm."
            "test_flag_rule_amendment_form",
            "tests.test_tg_10_1.TestSingleRecordPerRun."
            "test_single_record_per_run"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_reverse_file_order(self):
        proc = self.run_unittest([
            "tests.test_tg_10_5", "tests.test_tg_10_4",
            "tests.test_tg_10_3", "tests.test_tg_10_2",
            "tests.test_tg_10_1"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class TestR3058RemovalForm(unittest.TestCase):
    def test_tg103_test_supplies_fired_inputs_and_reads_form(self):
        source = (ROOT / "tests" / "test_tg_10_3.py").read_text()
        start = source.index("def test_person_promotion_and_demotion_fail")
        body = source[start:start + 2500]
        self.assertIn("flag_conditions_fired", body)
        self.assertIn("inputs", body)
        self.assertIn("promotion by a person after close is barred", body)
        self.assertIn("the flag rule never demotes", body)

    def run_tg103_under_mutant(self, old, new):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "tree"
            shutil.copytree(
                ROOT, target,
                ignore=shutil.ignore_patterns("__pycache__", ".git"))
            path = target / "crucible" / "mod10.py"
            text = path.read_text()
            self.assertIn(old, text)
            path.write_text(text.replace(old, new, 1))
            proc = subprocess.run(
                [sys.executable, "-m", "unittest",
                 "tests.test_tg_10_3"],
                cwd=str(target), capture_output=True, text=True,
                timeout=600)
            return proc

    def test_person_bar_removal_kills_tg103_test(self):
        proc = self.run_tg103_under_mutant(
            '        raise ValueError("promotion by a person after '
            'close is barred")',
            "        pass")
        self.assertNotEqual(proc.returncode, 0,
                            proc.stdout + proc.stderr)

    def test_demote_bar_removal_kills_tg103_test(self):
        proc = self.run_tg103_under_mutant(
            '        raise ValueError("the flag rule never demotes")',
            "        pass")
        self.assertNotEqual(proc.returncode, 0,
                            proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
