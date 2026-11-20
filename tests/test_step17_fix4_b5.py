"""Step 17 fix wave 4, Slice 5 defect and control tests.

Rows: FW4-04 (the mod12 run record validators judge the numeric
fields of a run record) and FW4-05 (band_membership and
eligibility judge the band entry form before the unpack).
Written before any cure, against the uncured tree.
"""

import unittest

import crucible.mod01 as mod01
import crucible.mod05 as mod05
import crucible.mod12 as mod12


def _screening_record():
    record = mod01.build_run_record()
    record["run_class"] = "screening"
    record["seed_domain"] = "screening"
    return record


class TestFW404Mod12NumericFields(unittest.TestCase):

    def test_control_unmutated_record_validates(self):
        record = _screening_record()
        self.assertEqual(
            mod12.run_record_validation_failures(record), [])
        self.assertTrue(mod12.validate_run_record(record))

    def test_control_whole_counts_validate(self):
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            record = _screening_record()
            record[field] = 5
            self.assertEqual(
                mod12.run_record_validation_failures(record), [],
                field)
            self.assertTrue(
                mod12.validate_run_record(record), field)

    def test_control_zero_replicate_index_validates(self):
        record = _screening_record()
        record["replicate_index"] = 0
        self.assertEqual(
            mod12.run_record_validation_failures(record), [])
        self.assertTrue(mod12.validate_run_record(record))

    def test_control_integral_float_validates(self):
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            record = _screening_record()
            record[field] = 5.0
            self.assertTrue(
                mod12.validate_run_record(record), field)

    def test_control_placeholder_standing_validates(self):
        record = _screening_record()
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            self.assertEqual(record[field], "stated value")
        self.assertTrue(mod12.validate_run_record(record))

    def _assert_refused(self, field, value):
        record = _screening_record()
        record[field] = value
        failures = mod12.run_record_validation_failures(record)
        self.assertNotEqual(failures, [], (field, value))
        self.assertIn(field, failures[0])
        self.assertFalse(
            mod12.validate_run_record(record), (field, value))

    def test_defect_non_finite_refused(self):
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            for value in (
                    float("nan"), float("inf"), float("-inf")):
                self._assert_refused(field, value)

    def test_defect_boolean_refused(self):
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            self._assert_refused(field, True)
            self._assert_refused(field, False)

    def test_defect_negative_refused(self):
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            self._assert_refused(field, -5)

    def test_defect_text_refused(self):
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            self._assert_refused(field, "hostile")

    def test_defect_fractional_refused(self):
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            self._assert_refused(field, 2.5)

    def test_defect_zero_refused_where_field_states_a_count(self):
        self._assert_refused("population_size", 0)
        self._assert_refused("run_length_in_days", 0)


class TestFW405Mod05BandEntries(unittest.TestCase):

    def _assert_named_refusal(self, bands):
        with self.assertRaises(ValueError) as caught:
            mod05.band_membership(
                5, bands, evaluation_order="O-1")
        text = str(caught.exception)
        self.assertIn("band_membership stands refused", text)
        self.assertIn("no band stands returned", text)
        self.assertNotIn("unpack", text)
        self.assertNotIn("not iterable", text)

    def test_control_plain_bands_served(self):
        result = mod05.band_membership(
            5, [("low", 0), ("high", 10)],
            evaluation_order="O-1")
        self.assertEqual(result["band"], "low")

    def test_control_empty_bands_served(self):
        result = mod05.band_membership(
            5, [], evaluation_order="O-1")
        self.assertIsNone(result["band"])

    def test_control_huge_score_and_minimum_served(self):
        huge = 10 ** 5000
        result = mod05.band_membership(
            huge, [("low", 0), ("high", 10)],
            evaluation_order="O-1")
        self.assertEqual(result["band"], "high")
        result = mod05.band_membership(
            5, [("low", huge)], evaluation_order="O-1")
        self.assertIsNone(result["band"])

    def test_control_non_finite_minimum_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod05.band_membership(
                5, [("high", float("nan"))],
                evaluation_order="O-1")
        self.assertIn(
            "band_membership stands refused",
            str(caught.exception))

    def test_control_non_finite_score_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod05.band_membership(
                float("nan"), [("low", 0)],
                evaluation_order="O-1")
        self.assertIn(
            "band_membership stands refused",
            str(caught.exception))

    def test_defect_integer_entry_refused_in_named_form(self):
        self._assert_named_refusal([1])

    def test_defect_three_part_entry_refused_in_named_form(self):
        self._assert_named_refusal([("band", 1, "extra")])

    def test_defect_none_bands_refused_in_named_form(self):
        self._assert_named_refusal(None)

    def test_defect_text_bands_refused_in_named_form(self):
        self._assert_named_refusal("ab")

    def test_defect_text_entry_refused_in_named_form(self):
        self._assert_named_refusal(["x"])

    def test_defect_one_part_entry_refused_in_named_form(self):
        self._assert_named_refusal([("a",)])

    def test_defect_none_entry_refused_in_named_form(self):
        self._assert_named_refusal([None])

    def test_defect_non_iterable_bands_refused_in_named_form(self):
        self._assert_named_refusal(5)

    def test_defect_dict_entry_refused_in_named_form(self):
        self._assert_named_refusal([{"low": 0, "high": 10}])

    def test_defect_bytes_entry_refused_in_named_form(self):
        self._assert_named_refusal([b"ab"])

    def test_defect_eligibility_integer_entry_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.eligibility(5, [1], evaluation_order="O-1")
        text = str(caught.exception)
        self.assertIn("band_membership stands refused", text)
        self.assertIn("no band stands returned", text)

    def test_defect_eligibility_none_bands_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.eligibility(5, None, evaluation_order="O-1")
        text = str(caught.exception)
        self.assertIn("band_membership stands refused", text)
        self.assertIn("no band stands returned", text)


if __name__ == "__main__":
    unittest.main()
