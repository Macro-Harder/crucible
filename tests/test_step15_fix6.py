"""Step 15 Round 1 fix pins for cluster 6, test statement and shipped text.

Each test pins one register item cure in the form its triage section
states: the stated form of a test must say what its body proves, the
gated C-11 test set must stand in the allocated form ruling Entry 9
allows, the C-01 contract pin must present no computable integrity
verdict while OP-24 stands open, and the shipped README install
procedure must state no distribution artefact in the present tense
that does not exist. Plain simulated values only.
"""
import os
import unittest

import crucible.mod10 as mod10

PRODUCT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_product_file(*parts):
    with open(os.path.join(PRODUCT_ROOT, *parts), encoding="utf-8") as handle:
        return handle.read()


class Fix6Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestStatedForms(Fix6Base):
    def test_tb15_tg135_stated_form_is_the_ruled_form(self):
        text = read_product_file("tests", "test_tg_13_5.py")
        self.assertIn("Manager ruling Entry 20", text)
        self.assertIn("held units stand reported as held", text)
        self.assertIn("released into the next weekly container in arrival order", text)
        self.assertNotIn("pins no outcome at the cap", text)
        self.assertNotIn("no test pins a held, refused, or carried outcome", text)
        self.assertNotIn("test_weekly_cap_open_element", text)

    def test_tb16_tg044_stated_form_is_the_ruled_form(self):
        text = read_product_file("tests", "test_tg_04_4.py")
        self.assertIn("Manager ruling Entry 21", text)
        self.assertNotIn("stand open at cluster R1-035", text)
        self.assertNotIn("never records a pass", text)
        self.assertNotIn("records a skip naming the R1-035 settlement", text)
        self.assertIn("resolver limb", text)
        self.assertIn("undemonstrated", text)
        self.assertIn("199", text)
        self.assertIn("2500", text)

    def test_c11_share_report_stands_docstring_states_its_form(self):
        text = read_product_file("crucible", "mod11.py")
        start = text.index("def share_report_stands")
        docstring = text[start:start + 900]
        self.assertIn("Report whether a report may read", docstring)
        self.assertIn("returns a boolean only", docstring)
        self.assertNotIn("no headline unit resting on it stands built", docstring)


class TestC11AllocatedForm(Fix6Base):
    def test_c11_test_set_stands_in_allocated_form(self):
        text = read_product_file("tests", "test_contract_c11.py")
        self.assertNotIn("test_append_audit_and_position_check_gated_on_op18_remainder", text)
        self.assertIn("test_position_check_free_limb", text)
        self.assertIn("checkpoint_position_check", text)
        self.assertIn("test_position_check_stream_position_limb_gated", text)
        self.assertIn("test_append_audit_completeness_limb_gated", text)
        self.assertIn("stream position limb", text)
        self.assertIn("completeness limb", text)

    def test_c12_position_check_free_limb_behaviour(self):
        run_id = "run-fix6-position"
        for n in (1, 2, 3):
            mod10.retain_event_log_entry(
                {"run_identifier": run_id, "journal_position": n})
        inside = mod10.checkpoint_position_check(
            {"run_identifier": run_id, "journal_position": 2})
        self.assertTrue(inside["reportable"])
        outside = mod10.checkpoint_position_check(
            {"run_identifier": run_id, "journal_position": 99})
        self.assertFalse(outside["reportable"])
        self.assertEqual(outside["failure_under"], "C-09")
        self.assertIn("retention failure", outside["outcome"])


class TestC27Battery(Fix6Base):
    def test_c27_inv8b03_battery_outcome_is_not_computable(self):
        manifest = {"run_identifier": "run-fix6-battery", "simulated_day": 3,
                    "state_reference": "state-1"}
        altered = dict(manifest, state_reference="state-2")
        transplanted = dict(manifest, run_identifier="run-fix6-other")
        stale = dict(manifest, simulated_day=1)
        for candidate in (dict(manifest), altered, transplanted, stale):
            result = mod10.checkpoint_integrity_check(manifest, candidate)
            self.assertEqual(result["outcome"], "not computable")
            self.assertEqual(result["alteration"], "not computable")
            self.assertEqual(result["transplant"], "not computable")
            self.assertEqual(result["staleness"], "not computable")
            self.assertFalse(result["state_hash_equality_claimed"])
            for key, value in result.items():
                if key == "state_hash_equality_claimed":
                    continue
                self.assertNotIsInstance(value, bool)

    def test_c27_c01_pin_presents_no_computable_verdict(self):
        text = read_product_file("tests", "test_contract_c01.py")
        self.assertIn("not computable", text)
        self.assertNotIn('same["alteration_detected"]', text)
        self.assertNotIn('["alteration_detected"])', text)


class TestReadmeBoundedForm(Fix6Base):
    def test_c49_readme_install_procedure_is_bounded(self):
        text = read_product_file("README.md")
        self.assertNotIn("The product ships as one versioned release archive", text)
        self.assertNotIn("One manifest inside the archive lists every file it contains", text)
        self.assertNotIn("as the final build document lists them", text)
        self.assertIn("does not stand built yet", text)
        self.assertIn("after Step 17 closes", text)
        self.assertIn("before the first install act of Step 18", text)
        self.assertIn("License: Apache License 2.0. Copyright 2026 J.P. Picard aka Macro-Harder.", text)
        self.assertIn("run_command('start_run'", text)


if __name__ == "__main__":
    unittest.main()
