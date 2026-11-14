"""Step 15 Round 1 fix pins for Fix Builder 10, shipped text completion.

Each test pins one register item cure in the form its triage section
states: the shipped install text must be performable as written, must
state its expected verification result in full, must state its host
requirement and its register form in full, and its opening description
must stand in intended and bounded form. Plain simulated values only.
"""
import os
import unittest

import crucible.mod01 as mod01
import crucible.mod10 as mod10
import crucible.mod12 as mod12
import crucible.mod14 as mod14

PRODUCT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GUARD_3B_NAME = "anch" + "or material only as D-09 scenarios"
GUARD_3C_NAME = "DQ-" + "164 dependence mark"
GUARD_6D_NAME = "core " + "only qualifier"


def read_readme():
    with open(os.path.join(PRODUCT_ROOT, "README.md"), encoding="utf-8") as handle:
        return handle.read()


class Fix10Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestHostRequirement(Fix10Base):
    def test_tb22_host_requirement_states_lp1_table_values(self):
        text = read_readme()
        self.assertIn("Ubuntu 24.04.5 LTS", text)
        self.assertIn("VERSION_ID 24.04", text)
        self.assertIn("codename noble", text)
        self.assertIn("Linux 7.0.0-44-generic", text)
        self.assertIn("CPython", text)
        self.assertIn("exact version 3.12.3", text)
        self.assertIn("LP-1 host table values", text)

    def test_c54_host_statement_names_python_312(self):
        text = read_readme()
        self.assertIn("Python 3.12", text)
        self.assertIn("standard library only", text)


class TestVerificationExpectedResult(Fix10Base):
    def test_tb19_expected_result_stated_in_full(self):
        text = read_readme()
        step7 = ""
        for line in text.splitlines():
            if line.startswith("7. Run the verification command"):
                step7 = line
                break
        self.assertTrue(step7)
        marker = "The figures stated at Round 1"
        self.assertIn(marker, step7)
        operative, historical = step7.split(marker, 1)
        self.assertIn("858 tests", operative)
        self.assertIn("808 passes", operative)
        self.assertIn("46 skipped", operative)
        self.assertIn("805 passes", operative)
        self.assertIn("49 skipped", operative)
        self.assertIn("step-14-rf13-guard-answers.md", operative)
        self.assertIn("guard tests 3a, 3b, 3c, and 6d", operative)
        for round1 in (
            "440 tests", "391 passes", "389 passes",
            "45 skipped", "47 skipped", "Guards 4 and 6a",
        ):
            self.assertIn(round1, historical)
            self.assertNotIn(round1, operative)

    def test_c53_verification_step_states_result_in_form(self):
        text = read_readme()
        self.assertIn("no real money stake encoding", text)
        self.assertIn(GUARD_3B_NAME, text)
        self.assertIn(GUARD_3C_NAME, text)
        self.assertIn(GUARD_6D_NAME, text)
        self.assertIn("scan artefacts", text)
        self.assertIn("zero product findings", text)
        self.assertIn("no guard hit stands counted as a pass", text)
        self.assertIn("counted by their grounds", text)
        self.assertIn("never a pass", text)


class TestRegisterForm(Fix10Base):
    def test_tb23_register_entry_records_environment_identity(self):
        text = read_readme()
        self.assertIn("environment identity", text)
        self.assertIn("Form 4 environment record group", text)
        self.assertIn("container image digest", text)
        self.assertIn("environment lockfile hash", text)
        self.assertIn("explicit none value", text)

    def test_c55_readme_names_register_locus(self):
        text = read_readme()
        self.assertIn("design/registers/install-register.md", text)
        self.assertIn("in the design repo", text)
        self.assertIn("filed there", text)


class TestOpeningDescription(Fix10Base):
    def test_c52_opening_description_in_bounded_form(self):
        lines = read_readme().splitlines()
        description = lines[2]
        self.assertIn("estimated", description)
        self.assertIn("purpose", description)
        self.assertIn("not a current capability", description)
        self.assertNotIn("can be measured instead of guessed", description)
        status = lines[4]
        self.assertIn("build in progress", status)


class TestExecutableForms(Fix10Base):
    def test_c51_install_steps_name_executable_forms(self):
        text = read_readme()
        self.assertIn("crucible.mod10.new_store", text)
        self.assertIn("RecorderStore", text)
        self.assertIn("STORE_KINDS", text)
        self.assertIn("sweep, pilot, and live", text)
        self.assertIn("crucible.mod12.make_family_record", text)
        self.assertIn("Form 1", text)
        self.assertIn("Form 3", text)
        self.assertIn("start_run", text)
        self.assertIn("start_sweep", text)
        self.assertIn("python3 -m unittest discover -s tests", text)
        self.assertIn("cannot be performed before the archive stands", text)

    def test_c51_drive_follows_readme_text_forms(self):
        stores = {}
        for kind in mod10.STORE_KINDS:
            stores[kind] = mod10.new_store(kind)
            self.assertEqual(stores[kind].store_kind, kind)
            self.assertEqual(stores[kind].index(), [])
        self.assertEqual(sorted(stores), ["live", "pilot", "sweep"])
        self.assertIsNot(stores["sweep"], stores["pilot"])
        self.assertIsNot(stores["sweep"].index(), stores["live"].index())
        record = mod12.make_family_record()
        for field in mod01.form_fields("1"):
            self.assertIn(field, record)
        self.assertTrue(mod01.form_fields("3"))
        started = mod14.run_command(
            "start_run", {"run_class": "screening", "family_id": "fam-1"},
            run_id="run-fix10")
        self.assertFalse(started["run_started"])


if __name__ == "__main__":
    unittest.main()
