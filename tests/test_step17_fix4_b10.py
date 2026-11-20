"""Step 17 fix wave 4, Builder 10 defect tests.

Slice 10, the FW3-24 defect test isolation row: FW4-22, as
charged at design/steps/step-17-fix4-charge.md and stated at
the Round 3 register ruling T17R3-22. The defect stands in
the evidence form of the landed test file
tests/test_step17_fix3_b8.py alone: run whole in one process
in the ordinary unittest form, its three FW3-24 defect tests
error in TestFW324HeadlineBuildFromRun.setUp at its
mod10.retain_run_record call, because the class retains the
run identifier run-fw324-resolves at every setUp and carries
no store reset, so the second retention in the same process
stands refused and the tests never reach the mod11 door they
charge. The same tests pass alone and under split per test
routing. The cure stands in that landed test file alone, in
its class setup, and no product file stands charged by this
row. Each defect test below reproduces the filing defect on
the uncured tree and passes on the cured tree: the whole
file serial run check stands beside a serial run of the
FW3-24 class alone and a split per test run of its three
defect tests, each in its own subprocess. Control tests pin
the standings that already hold.
"""
import os
import subprocess
import sys
import unittest

PRODUCT_ROOT = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
B8_MODULE = "tests.test_step17_fix3_b8"
FW324_CLASS = B8_MODULE + ".TestFW324HeadlineBuildFromRun"
FW324_DEFECT_TESTS = (
    "test_defect_non_mapping_values_named_ground_delivered",
    "test_defect_values_fault_uses_the_returned_channel",
    "test_control_valid_values_build",
)


def _run_unittest(*names):
    env = dict(os.environ)
    env["PYTHONPATH"] = (
        os.path.join(PRODUCT_ROOT, "tests") + os.pathsep
        + PRODUCT_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "unittest"] + list(names),
        cwd=PRODUCT_ROOT, capture_output=True, text=True, env=env)


class TestFW422WholeFileSerialRun(unittest.TestCase):
    def test_defect_whole_file_serial_run_stands_ok(self):
        proc = _run_unittest(B8_MODULE)
        self.assertIn("Ran 39 tests", proc.stderr)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        self.assertIn("OK", proc.stderr)

    def test_defect_fw324_class_serial_run_stands_ok(self):
        proc = _run_unittest(FW324_CLASS)
        self.assertIn("Ran 4 tests", proc.stderr)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        self.assertIn("OK", proc.stderr)

    def test_defect_fw324_tests_split_per_test_stand_ok(self):
        for name in FW324_DEFECT_TESTS:
            proc = _run_unittest(FW324_CLASS + "." + name)
            self.assertEqual(proc.returncode, 0,
                             name + ": " + proc.stderr[-1000:])
            self.assertIn("OK", proc.stderr)

    def test_control_single_fw324_test_stands_ok(self):
        proc = _run_unittest(
            FW324_CLASS + ".test_control_valid_values_build")
        self.assertEqual(proc.returncode, 0, proc.stderr[-1000:])
        self.assertIn("OK", proc.stderr)


if __name__ == "__main__":
    unittest.main()
