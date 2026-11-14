"""Step 15 second run fix pins for Fix Builder 11.

Items R1-064, R1-065, and R1-083. The README install step 7 must state
the suite figures a counted run gives, the suite figure pins must hold
those derived figures rather than the stale ones, and the operator
runbook must name the module to import run_command from. Plain values
only.
"""
import os
import unittest

import crucible.mod14 as mod14

PRODUCT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_ROOT = os.path.join(PRODUCT_ROOT, "tests")
ROUND1_MARKER = "The figures stated at Round 1"


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def read_readme():
    return read_text(os.path.join(PRODUCT_ROOT, "README.md"))


def operative_step7():
    for line in read_readme().splitlines():
        if line.startswith("7. Run the verification command"):
            if ROUND1_MARKER in line:
                return line.split(ROUND1_MARKER)[0]
            return line
    raise AssertionError("install step 7 line stands absent")


class TestR1064Step7Restated(unittest.TestCase):
    def test_step7_states_counted_figures(self):
        text = operative_step7()
        self.assertIn("978 tests", text)
        self.assertIn("928 passes", text)
        self.assertIn("46 skipped", text)
        self.assertIn("925 passes", text)
        self.assertIn("49 skipped", text)
        self.assertIn("4 failures", text)

    def test_step7_no_stale_figures_in_operative_part(self):
        text = operative_step7()
        self.assertNotIn("858 tests", text)
        self.assertNotIn("808 passes", text)
        self.assertNotIn("805 passes", text)


class TestR1065PinsDerived(unittest.TestCase):
    def test_r4_pin_holds_derived_figures_not_stale(self):
        source = read_text(os.path.join(TESTS_ROOT, "test_step15_r4_fix4.py"))
        self.assertIn("978", source)
        self.assertIn("928", source)
        self.assertIn("925", source)
        self.assertNotIn("858", source)
        self.assertNotIn("808", source)
        self.assertNotIn("805", source)

    def test_fix10_pin_holds_derived_figures_not_stale(self):
        source = read_text(os.path.join(TESTS_ROOT, "test_step15_fix10.py"))
        self.assertIn("978 tests", source)
        self.assertIn("928 passes", source)
        self.assertIn("925 passes", source)
        self.assertNotIn("858 tests", source)
        self.assertNotIn("808 passes", source)
        self.assertNotIn("805 passes", source)

    def test_pins_match_readme_operative_figures(self):
        text = operative_step7()
        self.assertIn("978 tests", text)
        source = read_text(os.path.join(TESTS_ROOT, "test_step15_r4_fix4.py"))
        self.assertIn("STATED_TOTAL = 978", source)


class TestR1083RunbookModule(unittest.TestCase):
    def test_runbook_names_mod14_for_run_command(self):
        text = read_readme()
        runbook = text.split("## Operator runbook", 1)[1]
        self.assertIn("crucible.mod14", runbook)
        self.assertIn("run_command", runbook)

    def test_mod14_carries_run_command(self):
        self.assertTrue(callable(mod14.run_command))


if __name__ == "__main__":
    unittest.main()
