"""Step 16 fix wave 7, Builder 1 tests.

Rows F7-01 to F7-04, ruling T16-73, on the First-user Advocate
re-drive findings RD-01 to RD-04.

Row F7-01 (RD-01, Medium): the StatedJudgement returned at the
family door tests in a boolean context as its truth_value
stands, at every door that returns one. The open marker family
stands truth_value False, so its judgement must test False;
the supplied family stands truth_value True, so its judgement
must test True.

Row F7-02 (RD-02, Medium): record_validation_failures names a
fault, in the standing failure form (field, rule, next step),
for a value standing in a container form (dict, list, or set)
in a field whose stated form is scalar, and validate_record
agrees, answering False where such a fault stands. A Form 2
record carrying population_size as a dict stands as the pin.

Row F7-03 (RD-03, Low): a named companion answer at the mod10
daily aggregates door states which stated value
validate_daily_aggregates refuses on the formally valid
Form 14 template record, and why, while
validate_daily_aggregates keeps its boolean signature and its
standing answers.

Row F7-04 (RD-04, Low): a docstring cover test in the U-09
form, extended to mod01, mod04, mod05, and mod06: every
exported callable the re-drive counts undocumented in those
modules carries a docstring at the mod10 standard, stating
its arguments, its return, and its failure form in plain
words.

Test first: every defect test in this file was written
against the landed product at head
142a1a5882ce17245375a1e3cb849014a31cc8aa and stands to fail
there for the reason its row states, except the guard tests,
which pass there and must keep passing. Supplied completeness
values in this file are test inputs only, standing for no
design value and adopted nowhere (OP-16). No seed is drawn,
read from a clock, or assigned in completion order (DQ7-02).
Bench Python 3.14.4 stands as the interpreter basis for every
figure in the builder paper.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01
from crucible import mod04
from crucible import mod05
from crucible import mod06
from crucible import mod10
from crucible import mod12

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)


def supplied_family():
    record = mod12.make_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


class TestF701JudgementBooleanStandsAsTruthValue(unittest.TestCase):

    def test_open_marker_family_judgement_tests_false(self):
        record = mod01.minimal_valid_family_record()
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement.truth_value)
        self.assertEqual(bool(judgement), judgement.truth_value)
        self.assertFalse(judgement)

    def test_supplied_family_judgement_tests_true(self):
        judgement = mod01.family_supports_reportable_run(
            supplied_family())
        self.assertTrue(judgement.truth_value)
        self.assertEqual(bool(judgement), judgement.truth_value)
        self.assertTrue(judgement)

    def test_run_is_reportable_judgement_tests_as_truth_value(self):
        record = mod01.minimal_valid_family_record()
        judgement = mod01.run_is_reportable("1", record)
        self.assertEqual(bool(judgement), judgement.truth_value)
        self.assertFalse(judgement)


class TestF702ContainerValueInScalarFieldNamed(unittest.TestCase):

    def test_dict_valued_population_size_named_and_refused(self):
        record = mod01.minimal_valid_instance("2")
        record["population_size"] = {"not": "a number"}
        failures = mod01.record_validation_failures("2", record)
        self.assertTrue(
            any("population_size" in failure for failure in failures),
            failures)
        self.assertTrue(
            any("container" in failure for failure in failures),
            failures)
        self.assertTrue(
            any("next step" in failure for failure in failures),
            failures)
        self.assertFalse(mod01.validate_record("2", record))

    def test_list_and_set_valued_population_size_named(self):
        for container in (["not", "a", "number"], {"not a number"}):
            record = mod01.minimal_valid_instance("2")
            record["population_size"] = container
            failures = mod01.record_validation_failures("2", record)
            self.assertTrue(
                any("population_size" in failure
                    for failure in failures),
                failures)
            self.assertFalse(mod01.validate_record("2", record))

    def test_stated_form_values_validate_as_before(self):
        record = mod01.minimal_valid_instance("2")
        self.assertEqual(
            mod01.record_validation_failures("2", record), [])
        self.assertTrue(mod01.validate_record("2", record))
        point = mod01.build_sweep_point(point_identifier="point-f7")
        self.assertTrue(mod01.validate_record("2", point))


class TestF703DailyAggregatesCompanionNamesReason(unittest.TestCase):

    def test_companion_names_reason_for_form14_template(self):
        companion = getattr(
            mod10, "daily_aggregates_validation_failures", None)
        self.assertTrue(callable(companion))
        record = mod01.minimal_valid_instance("14")
        self.assertTrue(
            mod10.validate_form14_daily_aggregates_record(record))
        self.assertFalse(mod10.validate_daily_aggregates([record]))
        failures = companion([record])
        self.assertTrue(failures)
        self.assertTrue(
            any("viewer_id" in failure for failure in failures),
            failures)
        self.assertTrue(
            any("Form 14" in failure for failure in failures),
            failures)

    def test_companion_empty_for_recorder_rows(self):
        companion = getattr(
            mod10, "daily_aggregates_validation_failures", None)
        self.assertTrue(callable(companion))
        rows = mod10.daily_aggregates_for_run("run-f7-companion")
        self.assertTrue(mod10.validate_daily_aggregates(rows))
        self.assertEqual(companion(rows), [])

    def test_boolean_door_keeps_standing_answers(self):
        rows = mod10.daily_aggregates_for_run("run-f7-boolean")
        self.assertTrue(mod10.validate_daily_aggregates(rows))
        self.assertFalse(mod10.validate_daily_aggregates([]))
        self.assertFalse(mod10.validate_daily_aggregates(None))


MOD01_UNDOCUMENTED_5 = [
    "named_failure_forms", "reserved_matter_values",
    "validate_provenance_block", "validate_store_kind",
    "validate_version_stamp",
]

MOD04_UNDOCUMENTED_6 = [
    "AlterationBarred", "DetectionLayerDeliveryPoint",
    "RuleCoreDeliveryPoint", "canary_appears_in_projection",
    "run", "tick",
]

MOD05_UNDOCUMENTED_12 = [
    "accept_work", "adjudication_outcome", "aggregation_interface",
    "aggregation_score", "band_transition", "challenge_outcome",
    "compare_aggregation", "compute_share", "cost_statement",
    "credit_work", "undelivered_share", "validate_run_share_logs",
]

MOD06_UNDOCUMENTED_5 = [
    "allowed_subpaths", "excluded_subpaths",
    "instruction_refusal_class", "pause_value_in_force",
    "profiles",
]


class TestF704DocstringCover(unittest.TestCase):

    def _assert_full_docstrings(self, module, names):
        for name in names:
            doc = getattr(module, name).__doc__ or ""
            self.assertTrue(doc.strip(), name)
            self.assertIn("Arguments", doc, name)
            self.assertIn("Returns", doc, name)
            self.assertIn("Failure", doc, name)

    def test_mod01_five_carry_full_docstrings(self):
        self._assert_full_docstrings(mod01, MOD01_UNDOCUMENTED_5)

    def test_mod04_six_carry_full_docstrings(self):
        self._assert_full_docstrings(mod04, MOD04_UNDOCUMENTED_6)

    def test_mod05_twelve_carry_full_docstrings(self):
        self._assert_full_docstrings(mod05, MOD05_UNDOCUMENTED_12)

    def test_mod06_five_carry_full_docstrings(self):
        self._assert_full_docstrings(mod06, MOD06_UNDOCUMENTED_5)


if __name__ == "__main__":
    unittest.main()
