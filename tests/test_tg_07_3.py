"""Test group TG-07.3. Slice S-07, module mod08.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod08, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
"""
import unittest

try:
    import crucible.mod08 as _module
    SURFACE_STANDS = True
except Exception:
    _module = None
    SURFACE_STANDS = False


def _require_entry(case, behaviour, names):
    if not SURFACE_STANDS:
        case.fail(
            "TG 07.3: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 07.3: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG073(unittest.TestCase):

    def test_both_uses_named_when_value_moves(self):
        """Fixture: one likelihood ratio table value used once as conformance material and once as an assumption probability, with both uses named in the artefact
        Pins: a value may move from one use to the other inside one artefact only where both uses stand named, per Contract E
        Bar: an artefact carrying the value in one use while the run record names the other, or neither, fails this group
        Failure: the test fails while the surface cannot show both uses named for a value used in both ways
        """
        _require_entry(self, "a table value used in both ways names both uses", ["score", "conformance_statement", "DetectionLayer"])
        surface = _module
        artefact = {"value": 4.0,
                    "uses_named": ["conformance", "assumption"]}
        self.assertTrue(surface.validate_use_naming(
            artefact, ["conformance", "assumption"]))
        self.assertTrue(surface.validate_use_naming(artefact))

    def test_silent_movement_between_uses_fails(self):
        """Fixture: one likelihood ratio table value carried in one use in an artefact while the run record names the other use, or neither
        Pins: no silent movement between conformance use and assumption use stands inside one artefact, per Contract E
        Bar: an artefact carrying the value in one use while the run record names the other, or neither, fails this group
        Failure: the test fails while the surface cannot reject a silent movement between uses
        """
        _require_entry(self, "silent movement between conformance use and assumption use is rejected", ["score", "conformance_statement", "DetectionLayer"])
        surface = _module
        silent = {"value": 4.0, "uses_named": ["conformance"]}
        with self.assertRaises(surface.SilentUseMovement):
            surface.validate_use_naming(silent, ["assumption"])
        unnamed = {"value": 4.0, "uses_named": []}
        with self.assertRaises(surface.SilentUseMovement):
            surface.validate_use_naming(unnamed, ["conformance"])
        bare = {"value": 4.0}
        with self.assertRaises(surface.SilentUseMovement):
            surface.validate_use_naming(bare, ["conformance"])


if __name__ == "__main__":
    unittest.main()
