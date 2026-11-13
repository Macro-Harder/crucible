"""Test group TG-12.4. Hostile family ownership.

Slice S-12, MOD-12 Sweep Controller. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod12, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
"""
import unittest

try:
    from crucible import mod12
    SURFACE = mod12
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-12.4"


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": product surface crucible.mod12 stands absent ("
            + repr(SURFACE_ERROR) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": product surface crucible.mod12 lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )


class TestHostileFamilyOwnership(unittest.TestCase):
    def test_hostile_family_required(self):
        """Fixture: F-13, the hostile input family, as TG-12.4 states.
        Pins: the hostile input family runs as a required sweep family under the Controller, with magnitudes fixed in the family record before runs, in the form TG-09.5 pins at execution.
        Bar: a sweep programme with the hostile family absent, optional, or sampled below magnitude has not run as required.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.4; with the surface present, a programme whose hostile family is not required, or whose magnitudes stand unfixed before runs, fails.
        """
        require_surface(self, "hostile input family runs as a required sweep family", "hostile_family_status")
        status = SURFACE.hostile_family_status(fixture="F-13")
        self.assertEqual(status["standing"], "required")
        self.assertTrue(status["magnitudes_fixed_before_runs"])

    def test_hostile_family_absent_or_optional_fails(self):
        """Fixture: a sweep programme with the hostile family absent, and one with the hostile family optional, as TG-12.4 states.
        Pins: both programmes fail validation as not run as required, whatever their other families show.
        Bar: a sweep programme with the hostile family absent or optional has not run as required.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.4; with the surface present, acceptance of either programme fails.
        """
        require_surface(self, "sweep programme with hostile family absent or optional rejected", "validate_sweep_programme")
        self.assertFalse(SURFACE.validate_sweep_programme({"families": []}))
        self.assertFalse(SURFACE.validate_sweep_programme(
            {"families": [{"name": "hostile", "standing": "optional"}]}
        ))

    def test_kind_below_fixed_magnitude_not_run(self):
        """Fixture: F-13 at one kind run below the magnitude fixed in the family record before runs, as slice S-08 states for that fixture and TG-12.4 carries.
        Pins: that kind does not count as run, and the family does not count as run as required on its strength.
        Bar: a kind run below its fixed magnitude does not count as run.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.4; with the surface present, counting the below magnitude kind as run fails.
        """
        require_surface(self, "hostile kind run below its fixed magnitude does not count as run", "hostile_kind_counts_as_run")
        self.assertFalse(SURFACE.hostile_kind_counts_as_run(kind="kind-under-test", ran_at=1, fixed_magnitude=2))
        self.assertTrue(SURFACE.hostile_kind_counts_as_run(kind="kind-under-test", ran_at=2, fixed_magnitude=2))


if __name__ == "__main__":
    unittest.main()
