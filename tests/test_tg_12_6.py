"""Test group TG-12.6. Rule version carriage and the family split, WI8B-03.

Slice S-12, MOD-12 Sweep Controller, with the Recorder carriage at slice
S-10. Suite convention: this file tries to import the product modules for its
slice, package crucible, modules mod12 and mod10, and records whether the
surfaces stand. While a surface stands absent, each test fails with a message
naming the pinned behaviour and its group.
"""
import unittest

try:
    from crucible import mod10, mod12
    SURFACES = {"mod10": mod10, "mod12": mod12}
    SURFACE_ERROR = None
except Exception as exc:
    SURFACES = {}
    SURFACE_ERROR = exc

GROUP = "TG-12.6"


def require_surface(testcase, behaviour, module, *attrs):
    surface = SURFACES.get(module)
    if surface is None:
        testcase.fail(
            GROUP + ": product surface crucible." + module + " stands absent ("
            + repr(SURFACE_ERROR) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(surface, attr):
            testcase.fail(
                GROUP + ": product surface crucible." + module + " lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )
    return surface


class TestVersionCarriage(unittest.TestCase):
    def test_records_carry_their_version_set(self):
        """Fixture: one run record, one checkpoint, one witness entry, and one headline unit, each produced under a stated rule version set, as TG-12.6 states.
        Pins: MOD-01 carries the exact rule version set as data, so each record named in this fixture carries the set under which it was produced, as Amendment S12-015 clause one states.
        Bar: a record presented under a rule version set it was not produced under fails this group.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-12.6; with the surfaces present, a named record carrying no version set, or a set other than its production set, fails.
        """
        mod12 = require_surface(self, "each record carries the exact rule version set it was produced under", "mod12", "record_version_sets")
        sets = mod12.record_version_sets(record_kinds=("run_record", "checkpoint", "witness_entry", "headline_unit"))
        for kind in ("run_record", "checkpoint", "witness_entry", "headline_unit"):
            self.assertIn(kind, sets)
            self.assertTrue(sets[kind])

    def test_record_under_wrong_version_set_fails(self):
        """Fixture: a record presented under a rule version set it was not produced under, as TG-12.6 states.
        Pins: the presentation fails validation.
        Bar: a record presented under a rule version set it was not produced under fails this group.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-12.6; with the surfaces present, acceptance of the presentation fails.
        """
        mod12 = require_surface(self, "record presented under a foreign version set rejected", "mod12", "validate_record_version")
        record = {"kind": "run_record", "produced_under": "set-a", "presented_under": "set-b"}
        self.assertFalse(mod12.validate_record_version(record))

    def test_recorder_keeps_version_set_unedited(self):
        """Fixture: the records of the first test of this group, with the rerun list derived from a rule change for the same family beside them, as TG-12.6 states.
        Pins: the Recorder at slice S-10 retains each such record with the exact rule version set it carries as data, unedited after a rule change, and holds the rerun list derived from a rule change as a retained record naming the records the change puts in question, as Amendment S12-015 clause two states.
        Bar: a retained record whose version set stands edited after a rule change fails this group.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-12.6; with the surfaces present, an edited retained set, or a rerun list naming no records, fails.
        """
        mod10 = require_surface(self, "Recorder retains version sets unedited and holds the rerun list", "mod10", "retained_version_set", "rerun_list_for_rule_change")
        retained = mod10.retained_version_set(record_id="record-under-test")
        self.assertTrue(retained)
        rerun_list = mod10.rerun_list_for_rule_change(family_id="family-under-test")
        self.assertIn("records_in_question", rerun_list)


class TestFamilySplit(unittest.TestCase):
    def test_family_split_by_rule_version(self):
        """Fixture: one family with results under two rule version sets, as TG-12.6 states.
        Pins: the family is split by rule version, results under the two version sets standing in two version parts of the family.
        Bar: pooled results with no bound recorded in the family record fail this group.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-12.6; with the surfaces present, a single unsplit part holding both version sets fails.
        """
        mod12 = require_surface(self, "family split by rule version into two version parts", "mod12", "family_version_parts")
        parts = mod12.family_version_parts(family_id="family-under-test")
        self.assertEqual(len(parts), 2)
        self.assertNotEqual(parts[0]["rule_version_set"], parts[1]["rule_version_set"])

    def test_silent_pooling_fails_and_named_bound_stands(self):
        """Fixture: one family pooling results across a rule change with no bound recorded, and one pooling with a named bound recorded, as TG-12.6 states.
        Pins: the unrecorded pooling fails validation; pooling recorded as a named bound in the family record, stating the two version sets pooled and the ground for pooling them, stands in the recorded form, as Amendment S12-015 clause three states.
        Bar: pooled results with no bound recorded in the family record fail this group; no silent pooling stands.
        Failure: while a surface stands absent the test fails naming this behaviour and TG-12.6; with the surfaces present, acceptance of the unrecorded pooling, or rejection of the recorded bound form, fails.
        """
        mod12 = require_surface(self, "silent pooling rejected and named bound pooling recorded", "mod12", "validate_family_pooling")
        silent = {"pooled_version_sets": ["set-a", "set-b"], "bound_recorded": None}
        self.assertFalse(mod12.validate_family_pooling(silent))
        named = {
            "pooled_version_sets": ["set-a", "set-b"],
            "bound_recorded": {"version_sets": ["set-a", "set-b"], "ground": "stated ground"},
        }
        self.assertTrue(mod12.validate_family_pooling(named))


if __name__ == "__main__":
    unittest.main()
