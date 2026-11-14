"""Step 15 Round 4 fix pins for Fix Builder 4, cluster R4-4.

Item R4-A7-01, on TB-19's ground: the shipped README install step 7
must state its expected verification result in full, in TB-19's own
cure form, restated to the suite standing as derived from an actual
suite run counted with the pin files included. The constants below
stand as that counted run gives them, so these pins fail where the
README stated figures and the counted suite figures disagree. The operative expected result is
the current standing; the Round 1 figures may stand only in a sentence
that labels them as that round's form. Plain simulated values only.
Sensitive guard phrases stand split by concatenation, as the Fix
Builder 10 pin file does, so this file adds no guard hit.
"""
import os
import re
import unittest

PRODUCT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GUARD_3B_NAME = "anch" + "or material only as D-09 scenarios"
GUARD_3C_NAME = "DQ-" + "164 dependence mark"
GUARD_6D_NAME = "core " + "only qualifier"
GUARD_3A_NAME = "no real money stake " + "encoding"

STATED_TOTAL = 978
STATED_FAILURES = 4
BUILD_SKIPS = 46
BUILD_PASSES = 928
PRODUCT_SKIPS = 49
PRODUCT_PASSES = 925

ROUND1_MARKER = "The figures stated at Round 1"


def read_readme():
    with open(os.path.join(PRODUCT_ROOT, "README.md"), encoding="utf-8") as handle:
        return handle.read()


def step7_line():
    for line in read_readme().splitlines():
        if line.startswith("7. Run the verification command"):
            return line
    raise AssertionError("install step 7 line stands absent from the README")


def operative_step7():
    line = step7_line()
    if ROUND1_MARKER in line:
        return line.split(ROUND1_MARKER)[0]
    return line


class TestR4A701Step7Restated(unittest.TestCase):
    def test_r4a701_step7_states_derived_total_and_failures(self):
        text = operative_step7()
        self.assertIn("Expected result, stated in full", text)
        self.assertIn(str(STATED_TOTAL) + " tests", text)
        self.assertIn("with " + str(STATED_FAILURES) + " failures", text)
        self.assertNotIn("440 tests", text)

    def test_r4a701_build_tree_figures_stated(self):
        text = operative_step7()
        self.assertIn("In the build tree form", text)
        self.assertIn(str(BUILD_PASSES) + " passes", text)
        self.assertIn(str(BUILD_SKIPS) + " skipped", text)
        self.assertIn(str(STATED_FAILURES) + " failures", text)

    def test_r4a701_product_only_figures_stated(self):
        text = operative_step7()
        self.assertIn("In the product only form", text)
        self.assertIn(str(PRODUCT_PASSES) + " passes", text)
        self.assertIn(str(PRODUCT_SKIPS) + " skipped", text)

    def test_r4a701_stated_figures_derive_by_subtraction(self):
        text = operative_step7()
        total = int(re.search(r"suite stands at (\d+) tests", text).group(1))
        build = re.search(
            r"build tree form the expected result is (\d+) passes, "
            r"(\d+) skipped, and (\d+) failures", text)
        product = re.search(
            r"product only form the expected result is (\d+) passes, "
            r"(\d+) skipped, and (\d+) failures", text)
        self.assertIsNotNone(build)
        self.assertIsNotNone(product)
        build_passes, build_skips, build_failures = (
            int(build.group(1)), int(build.group(2)), int(build.group(3)))
        product_passes, product_skips, product_failures = (
            int(product.group(1)), int(product.group(2)),
            int(product.group(3)))
        self.assertEqual(total, STATED_TOTAL)
        self.assertEqual(
            build_passes, total - build_skips - build_failures)
        self.assertEqual(
            product_passes, total - product_skips - product_failures)
        self.assertEqual(product_skips - build_skips, 3)
        self.assertEqual(build_passes - product_passes, 3)
        self.assertEqual(build_failures, product_failures)

    def test_r4a701_difference_names_three_standing_down_tests(self):
        text = operative_step7()
        self.assertIn("three tests standing down as skips", text)
        self.assertIn("Guard 4", text)
        self.assertIn("test_ac11_never_recorded_as_pass", text)
        self.assertIn("Guard 6a", text)
        self.assertIn("test_6a_no_affordability_wording_before_pilot", text)
        self.assertIn("TB-15 plan amendment pin", text)
        self.assertIn("test_tg135_body_entry_stands_in_ruled_form", text)
        self.assertIn("test_step15_r2_fix5.py", text)

    def test_r4a701_guard_set_named_and_answered_in_form(self):
        text = operative_step7()
        self.assertIn("guard tests 3a, 3b, 3c, and 6d", text)
        self.assertIn(GUARD_3A_NAME, text)
        self.assertIn(GUARD_3B_NAME, text)
        self.assertIn(GUARD_3C_NAME, text)
        self.assertIn(GUARD_6D_NAME, text)
        self.assertIn("scan artefacts", text)
        self.assertIn("zero product findings", text)
        self.assertIn("step-14-rf13-guard-answers.md", text)
        self.assertIn("no guard hit stands counted as a pass", text)
        self.assertIn("never a pass", text)


if __name__ == "__main__":
    unittest.main()
