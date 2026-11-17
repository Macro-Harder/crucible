"""Pins for Round 20 rows R20-014, R20-015, R20-016, R20-025,
R20-026, R20-048, and R20-049.

MOD-16 equality, membership, and sentence family, Builder 6 of
fix wave 20, under settlement S-16 and ruling (an). Each pin
states the defect its row charges in the distinguishing case,
beside the plain controls the source papers ran.
"""
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod16


class AlwaysEq:
    """A value in no stated form whose equality answers True
    against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 1


class RaisingEq:
    """A value in no stated form whose equality readings raise."""

    def __eq__(self, other):
        raise RuntimeError("raising equality")

    def __ne__(self, other):
        raise RuntimeError("raising inequality")

    def __hash__(self):
        return 1


class FalseEqStr(str):
    """A str subclass whose equality answers False against every
    value, whatever text it stores."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __hash__(self):
        return str.__hash__(self)


class TrueEqStr(str):
    """A str subclass whose equality answers True against every
    value, whatever text it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(self)


class RaisingEqStr(str):
    """A str subclass whose equality readings raise, whatever
    text it stores."""

    def __eq__(self, other):
        raise RuntimeError("raising equality")

    def __ne__(self, other):
        raise RuntimeError("raising inequality")

    def __hash__(self):
        return str.__hash__(self)


class LyingStr(str):
    """A str subclass whose string reading answers a fixed other
    text, whatever text it stores. Its equality stands plain."""

    LYING = ""

    def __str__(self):
        return self.LYING


class LyingStrF01(LyingStr):
    LYING = "F-01"


class LyingStrScreening(LyingStr):
    LYING = "screening"


class RaisingStr(str):
    """A str subclass whose string reading raises."""

    def __str__(self):
        raise RuntimeError("raising string")


class LyingInt(int):
    """An int subclass whose int conversion answers a fixed other
    number, whatever number it stores."""

    LYING = 0

    def __int__(self):
        return self.LYING


class LyingIntFive(LyingInt):
    LYING = 5


class RaisingInt:
    """A value in no number form whose int conversion raises."""

    def __int__(self):
        raise RuntimeError("raising conversion")


def fixture_line(**overrides):
    line = {
        "ran": True,
        "showed": "x",
        "does_not_show": "y",
        "value_source": "brief",
    }
    line.update(overrides)
    return line


def folding_record(count):
    return {
        "discharged_by_slice_tests_alone": False,
        "checker_distinct_from_folder": True,
        "seam_cases_per_ruling": {"DQ-1": count},
    }


class TestR20014ValidateFixtureRecord(unittest.TestCase):
    def test_always_equal_source_refused(self):
        self.assertFalse(mod16.validate_fixture_record(
            fixture_line(value_source=AlwaysEq())))

    def test_raising_source_refused_no_escape(self):
        self.assertFalse(mod16.validate_fixture_record(
            fixture_line(value_source=RaisingEq())))

    def test_false_eq_brief_source_validated(self):
        self.assertTrue(mod16.validate_fixture_record(
            fixture_line(value_source=FalseEqStr("brief"))))

    def test_true_eq_nowhere_source_refused(self):
        self.assertFalse(mod16.validate_fixture_record(
            fixture_line(value_source=TrueEqStr("nowhere"))))

    def test_bytes_brief_source_validated(self):
        self.assertTrue(mod16.validate_fixture_record(
            fixture_line(value_source=b"brief")))

    def test_control_plain_brief(self):
        self.assertTrue(mod16.validate_fixture_record(fixture_line()))

    def test_control_plain_register_source(self):
        self.assertTrue(mod16.validate_fixture_record(
            fixture_line(value_source="brief or evidence register")))

    def test_control_plain_nowhere(self):
        self.assertFalse(mod16.validate_fixture_record(
            fixture_line(value_source="nowhere")))

    def test_control_not_run_record(self):
        line = fixture_line(ran=False)
        del line["value_source"]
        self.assertTrue(mod16.validate_fixture_record(line))


class TestR20015ValidateConfirmationResult(unittest.TestCase):
    def test_false_eq_run_class_screening_refused(self):
        record = {"run_class": FalseEqStr("confirmation"),
                  "seed_domain": "screening"}
        self.assertFalse(mod16.validate_confirmation_result(record))

    def test_false_eq_seed_domain_refused(self):
        record = {"run_class": "confirmation",
                  "seed_domain": FalseEqStr("screening")}
        self.assertFalse(mod16.validate_confirmation_result(record))

    def test_false_eq_domain_refused(self):
        record = {"run_class": "confirmation",
                  "domain": FalseEqStr("screening")}
        self.assertFalse(mod16.validate_confirmation_result(record))

    def test_raising_run_class_no_escape(self):
        record = {"run_class": RaisingEq(), "seed_domain": "screening"}
        self.assertTrue(mod16.validate_confirmation_result(record))

    def test_raising_seed_domain_no_escape(self):
        record = {"run_class": "confirmation",
                  "seed_domain": RaisingEq()}
        self.assertTrue(mod16.validate_confirmation_result(record))

    def test_raising_eq_str_confirmation_screening_refused(self):
        record = {"run_class": RaisingEqStr("confirmation"),
                  "seed_domain": "screening"}
        self.assertFalse(mod16.validate_confirmation_result(record))

    def test_control_confirmation_screening_seed(self):
        record = {"run_class": "confirmation",
                  "seed_domain": "screening"}
        self.assertFalse(mod16.validate_confirmation_result(record))

    def test_control_confirmation_screening_domain(self):
        record = {"run_class": "confirmation", "domain": "screening"}
        self.assertFalse(mod16.validate_confirmation_result(record))

    def test_control_confirmation_held_out(self):
        record = {"run_class": "confirmation",
                  "seed_domain": "held out confirmation"}
        self.assertTrue(mod16.validate_confirmation_result(record))

    def test_control_no_run_class(self):
        self.assertFalse(mod16.validate_confirmation_result({}))

    def test_control_other_run_class(self):
        record = {"run_class": "screening",
                  "seed_domain": "screening"}
        self.assertTrue(mod16.validate_confirmation_result(record))


class TestR20016ValidateHeadlineClaim(unittest.TestCase):
    def test_false_eq_validation_material_refused(self):
        result = {"headline_claim": True,
                  "material": FalseEqStr("validation")}
        self.assertFalse(mod16.validate_headline_claim(result))

    def test_raising_material_no_escape(self):
        result = {"headline_claim": True, "material": RaisingEq()}
        self.assertTrue(mod16.validate_headline_claim(result))

    def test_always_eq_material_passes_apart(self):
        result = {"headline_claim": True, "material": AlwaysEq()}
        self.assertTrue(mod16.validate_headline_claim(result))

    def test_raising_eq_str_validation_material_refused(self):
        result = {"headline_claim": True,
                  "material": RaisingEqStr("validation")}
        self.assertFalse(mod16.validate_headline_claim(result))

    def test_control_validation_material(self):
        result = {"headline_claim": True, "material": "validation"}
        self.assertFalse(mod16.validate_headline_claim(result))

    def test_control_sweep_material(self):
        result = {"headline_claim": True, "material": "sweep"}
        self.assertTrue(mod16.validate_headline_claim(result))

    def test_control_validation_material_flag(self):
        result = {"headline_claim": True, "material": "sweep",
                  "validation_material": True}
        self.assertFalse(mod16.validate_headline_claim(result))

    def test_control_no_headline_claim_field(self):
        self.assertFalse(mod16.validate_headline_claim({}))

    def test_control_no_claim_standing(self):
        result = {"headline_claim": False, "material": "validation"}
        self.assertTrue(mod16.validate_headline_claim(result))


class TestR20025HorizonApplication(unittest.TestCase):
    def test_boolean_point_not_number_one(self):
        self.assertFalse(mod16.horizon_application(True, (1,)))

    def test_boolean_selected_not_number_one(self):
        self.assertFalse(mod16.horizon_application(1, (True,)))

    def test_decimal_point_outside_plain_limb(self):
        self.assertFalse(mod16.horizon_application(Decimal(1), (1,)))

    def test_fraction_point_outside_plain_limb(self):
        self.assertFalse(mod16.horizon_application(Fraction(1, 1), (1,)))

    def test_always_equal_point_refused(self):
        self.assertFalse(mod16.horizon_application(AlwaysEq(), (1,)))

    def test_raising_point_no_escape(self):
        self.assertFalse(mod16.horizon_application(RaisingEq(), (1,)))

    def test_false_eq_text_point_selected(self):
        self.assertTrue(mod16.horizon_application(
            FalseEqStr("a"), ("a",)))

    def test_raising_eq_text_point_selected(self):
        self.assertTrue(mod16.horizon_application(
            RaisingEqStr("a"), ("a",)))

    def test_control_number_selected(self):
        self.assertTrue(mod16.horizon_application(1, (1, 2)))

    def test_control_number_not_selected(self):
        self.assertFalse(mod16.horizon_application(3, (1, 2)))

    def test_control_text_selected(self):
        self.assertTrue(mod16.horizon_application("a", ("a",)))

    def test_control_named_text_point(self):
        selected = ("witness point 1", "decay point 1")
        self.assertTrue(mod16.horizon_application(
            "witness point 1", selected))
        self.assertFalse(mod16.horizon_application(
            "grid point 9", selected))

    def test_control_float_matches_int_point(self):
        self.assertTrue(mod16.horizon_application(1.0, (1,)))

    def test_control_boolean_matches_boolean(self):
        self.assertTrue(mod16.horizon_application(True, (True,)))

    def test_control_none_selected(self):
        self.assertFalse(mod16.horizon_application(1, None))


class TestR20026ValidateFoldingDischarge(unittest.TestCase):
    def test_boolean_count_refused(self):
        self.assertFalse(mod16.validate_folding_discharge(
            folding_record(True)))

    def test_lying_int_count_refused(self):
        self.assertFalse(mod16.validate_folding_discharge(
            folding_record(LyingIntFive(0))))

    def test_raising_conversion_count_no_escape(self):
        self.assertFalse(mod16.validate_folding_discharge(
            folding_record(RaisingInt())))

    def test_control_count_one(self):
        self.assertTrue(mod16.validate_folding_discharge(
            folding_record(1)))

    def test_control_count_zero(self):
        self.assertFalse(mod16.validate_folding_discharge(
            folding_record(0)))

    def test_control_count_two(self):
        self.assertTrue(mod16.validate_folding_discharge(
            folding_record(2)))

    def test_control_int_subclass_stored_count(self):
        self.assertTrue(mod16.validate_folding_discharge(
            folding_record(LyingIntFive(3))))

    def test_control_empty_mapping(self):
        record = folding_record(1)
        record["seam_cases_per_ruling"] = {}
        self.assertFalse(mod16.validate_folding_discharge(record))

    def test_control_slice_tests_alone(self):
        record = folding_record(1)
        record["discharged_by_slice_tests_alone"] = True
        self.assertFalse(mod16.validate_folding_discharge(record))

    def test_control_checker_folded(self):
        record = folding_record(1)
        record["checker_distinct_from_folder"] = False
        self.assertFalse(mod16.validate_folding_discharge(record))

    def test_control_whole_record(self):
        self.assertTrue(mod16.validate_folding_discharge(
            mod16.folding_check_record()))


class TestR20048FixtureRecordSentence(unittest.TestCase):
    def test_lying_str_identifier_named_on_stored_text(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as caught:
            mod16.fixture_record(LyingStrF01("F-99"))
        message = str(caught.exception)
        self.assertIn("F-99", message)
        self.assertNotIn("F-01", message)

    def test_raising_str_identifier_named_on_stored_text(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as caught:
            mod16.fixture_record(RaisingStr("F-99"))
        self.assertIn("F-99", str(caught.exception))

    def test_control_plain_unknown_identifier(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as caught:
            mod16.fixture_record("F-99")
        self.assertIn("F-99", str(caught.exception))

    def test_control_plain_known_identifier(self):
        line = mod16.fixture_record("F-01")
        self.assertEqual(line["fixture"], "F-01")

    def test_control_plain_second_identifier(self):
        line = mod16.fixture_record("F-02")
        self.assertEqual(line["fixture"], "F-02")


class TestR20049ExerciseRunClassSentence(unittest.TestCase):
    def test_lying_str_run_class_named_on_stored_text(self):
        with self.assertRaises(ValueError) as caught:
            mod16.exercise_run_class(LyingStrScreening("bogus class"))
        message = str(caught.exception)
        self.assertIn("bogus class", message)
        self.assertNotIn("screening", message)

    def test_raising_str_run_class_named_on_stored_text(self):
        with self.assertRaises(ValueError) as caught:
            mod16.exercise_run_class(RaisingStr("bogus class"))
        self.assertIn("bogus class", str(caught.exception))

    def test_control_plain_unknown_run_class(self):
        with self.assertRaises(ValueError) as caught:
            mod16.exercise_run_class("bogus")
        self.assertIn("bogus", str(caught.exception))

    def test_control_plain_confirmation_carried(self):
        result = mod16.exercise_run_class("confirmation")
        self.assertEqual(result["run_class"], "confirmation")
        self.assertFalse(result["exercised_end_to_end"])


if __name__ == "__main__":
    unittest.main()
