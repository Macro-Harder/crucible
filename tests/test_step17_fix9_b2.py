"""Step 17 fix wave 9, Slice 2 defect tests (FW9-01, T17R8-01).

The extra argument family in keyword form and in positional
form at the 26 owed doors of mod11: at each door named in
the slice, the door handed its ordinary arguments plus one
extra argument must refuse in the named form of its module,
stating the door, the ground, and the next step, instead of
escaping as a bare interpreter TypeError. Doors of mod11
already cured in earlier waves stand as controls in the
same form, and plain handings at cured doors stand served
whole as controls.

Judgement stands by stored value in code: the exception type
and the stored message text, never by a repr.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod11


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, door_word, call):
    """The call refuses in named form: ValueError, never a bare
    TypeError, the message carrying the door, the beyond ground,
    a next step, and no bare interpreter phrase."""
    with case.assertRaises(ValueError) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    case.assertIn(door_word, message)
    case.assertIn("beyond", message)
    case.assertIn("next step", message)
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


class TestFW901Mod11Charged(unittest.TestCase):

    def test_defect_first_sentence_extra_keyword(self):
        check_named_refusal(
            self, "first_sentence",
            lambda: mod11.first_sentence(*("Alpha. Beta",), extra_kw=1))

    def test_defect_first_sentence_extra_positional(self):
        check_named_refusal(
            self, "first_sentence",
            lambda: mod11.first_sentence(*("Alpha. Beta",), 1))

    def test_defect_location_for_endpoint_extra_keyword(self):
        check_named_refusal(
            self, "location_for_endpoint",
            lambda: mod11.location_for_endpoint(*(None, None, None), extra_kw=1))

    def test_defect_location_for_endpoint_extra_positional(self):
        check_named_refusal(
            self, "location_for_endpoint",
            lambda: mod11.location_for_endpoint(*(None, None, None), 1))

    def test_defect_make_weekly_container_extra_keyword(self):
        check_named_refusal(
            self, "make_weekly_container",
            lambda: mod11.make_weekly_container(*(None, []), extra_kw=1))

    def test_defect_make_weekly_container_extra_positional(self):
        check_named_refusal(
            self, "make_weekly_container",
            lambda: mod11.make_weekly_container(*(None, []), 1))

    def test_defect_moved_reading_extra_keyword(self):
        check_named_refusal(
            self, "moved_reading",
            lambda: mod11.moved_reading(*(2, 1), extra_kw=1))

    def test_defect_moved_reading_extra_positional(self):
        check_named_refusal(
            self, "moved_reading",
            lambda: mod11.moved_reading(*(2, 1), 1))

    def test_defect_next_weekly_container_extra_keyword(self):
        check_named_refusal(
            self, "next_weekly_container",
            lambda: mod11.next_weekly_container(*(None, None, []), extra_kw=1))

    def test_defect_next_weekly_container_extra_positional(self):
        check_named_refusal(
            self, "next_weekly_container",
            lambda: mod11.next_weekly_container(*(None, None, []), 1))

    def test_defect_point_standing_extra_keyword(self):
        check_named_refusal(
            self, "point_standing",
            lambda: mod11.point_standing(*(30,), extra_kw=1))

    def test_defect_point_standing_extra_positional(self):
        check_named_refusal(
            self, "point_standing",
            lambda: mod11.point_standing(*(30,), 1))

    def test_defect_record_first_observed_extra_keyword(self):
        check_named_refusal(
            self, "record_first_observed",
            lambda: mod11.record_first_observed(*(1, 2, 3), extra_kw=1))

    def test_defect_record_first_observed_extra_positional(self):
        check_named_refusal(
            self, "record_first_observed",
            lambda: mod11.record_first_observed(*(1, 2, 3, False), 1))

    def test_defect_region_shift_steps_extra_keyword(self):
        check_named_refusal(
            self, "region_shift_steps",
            lambda: mod11.region_shift_steps(*(None, None), extra_kw=1))

    def test_defect_region_shift_steps_extra_positional(self):
        check_named_refusal(
            self, "region_shift_steps",
            lambda: mod11.region_shift_steps(*(None, None), 1))

    def test_defect_reporter_inputs_for_family_extra_keyword(self):
        check_named_refusal(
            self, "reporter_inputs_for_family",
            lambda: mod11.reporter_inputs_for_family(*([],), extra_kw=1))

    def test_defect_reporter_inputs_for_family_extra_positional(self):
        check_named_refusal(
            self, "reporter_inputs_for_family",
            lambda: mod11.reporter_inputs_for_family(*([],), 1))

    def test_defect_share_report_stands_extra_keyword(self):
        check_named_refusal(
            self, "share_report_stands",
            lambda: mod11.share_report_stands(*(None, None), extra_kw=1))

    def test_defect_share_report_stands_extra_positional(self):
        check_named_refusal(
            self, "share_report_stands",
            lambda: mod11.share_report_stands(*(None, None), 1))

    def test_defect_top_up_applies_extra_keyword(self):
        check_named_refusal(
            self, "top_up_applies",
            lambda: mod11.top_up_applies(*(0.5,), extra_kw=1))

    def test_defect_top_up_applies_extra_positional(self):
        check_named_refusal(
            self, "top_up_applies",
            lambda: mod11.top_up_applies(*(0.5,), 1))

    def test_defect_transition_figure_extra_keyword(self):
        check_named_refusal(
            self, "transition_figure",
            lambda: mod11.transition_figure(*([],), extra_kw=1))

    def test_defect_transition_figure_extra_positional(self):
        check_named_refusal(
            self, "transition_figure",
            lambda: mod11.transition_figure(*([],), 1))

    def test_defect_transition_wording_extra_keyword(self):
        check_named_refusal(
            self, "transition_wording",
            lambda: mod11.transition_wording(*(None, None), extra_kw=1))

    def test_defect_transition_wording_extra_positional(self):
        check_named_refusal(
            self, "transition_wording",
            lambda: mod11.transition_wording(*(None, None, None), 1))

    def test_defect_unit_is_publishable_extra_keyword(self):
        check_named_refusal(
            self, "unit_is_publishable",
            lambda: mod11.unit_is_publishable(*(None,), extra_kw=1))

    def test_defect_unit_is_publishable_extra_positional(self):
        check_named_refusal(
            self, "unit_is_publishable",
            lambda: mod11.unit_is_publishable(*(None,), 1))

    def test_defect_validate_bounding_headline_extra_keyword(self):
        check_named_refusal(
            self, "validate_bounding_headline",
            lambda: mod11.validate_bounding_headline(*(None, None, None), extra_kw=1))

    def test_defect_validate_bounding_headline_extra_positional(self):
        check_named_refusal(
            self, "validate_bounding_headline",
            lambda: mod11.validate_bounding_headline(*(None, None, None), 1))

    def test_defect_validate_disclosure_form_extra_keyword(self):
        check_named_refusal(
            self, "validate_disclosure_form",
            lambda: mod11.validate_disclosure_form(*(None,), extra_kw=1))

    def test_defect_validate_disclosure_form_extra_positional(self):
        check_named_refusal(
            self, "validate_disclosure_form",
            lambda: mod11.validate_disclosure_form(*(None,), 1))

    def test_defect_validate_envelope_claim_extra_keyword(self):
        check_named_refusal(
            self, "validate_envelope_claim",
            lambda: mod11.validate_envelope_claim(*(None,), extra_kw=1))

    def test_defect_validate_envelope_claim_extra_positional(self):
        check_named_refusal(
            self, "validate_envelope_claim",
            lambda: mod11.validate_envelope_claim(*(None,), 1))

    def test_defect_validate_family_record_extra_keyword(self):
        check_named_refusal(
            self, "validate_family_record",
            lambda: mod11.validate_family_record(*(None,), extra_kw=1))

    def test_defect_validate_family_record_extra_positional(self):
        check_named_refusal(
            self, "validate_family_record",
            lambda: mod11.validate_family_record(*(None,), 1))

    def test_defect_validate_headline_unit_extra_keyword(self):
        check_named_refusal(
            self, "validate_headline_unit",
            lambda: mod11.validate_headline_unit(*(None,), extra_kw=1))

    def test_defect_validate_headline_unit_extra_positional(self):
        check_named_refusal(
            self, "validate_headline_unit",
            lambda: mod11.validate_headline_unit(*(None,), 1))

    def test_defect_validate_observation_time_extra_keyword(self):
        check_named_refusal(
            self, "validate_observation_time",
            lambda: mod11.validate_observation_time(*(None,), extra_kw=1))

    def test_defect_validate_observation_time_extra_positional(self):
        check_named_refusal(
            self, "validate_observation_time",
            lambda: mod11.validate_observation_time(*(None,), 1))

    def test_defect_validate_publication_record_extra_keyword(self):
        check_named_refusal(
            self, "validate_publication_record",
            lambda: mod11.validate_publication_record(*(None,), extra_kw=1))

    def test_defect_validate_publication_record_extra_positional(self):
        check_named_refusal(
            self, "validate_publication_record",
            lambda: mod11.validate_publication_record(*(None,), 1))

    def test_defect_validate_readout_extra_keyword(self):
        check_named_refusal(
            self, "validate_readout",
            lambda: mod11.validate_readout(*(None,), extra_kw=1))

    def test_defect_validate_readout_extra_positional(self):
        check_named_refusal(
            self, "validate_readout",
            lambda: mod11.validate_readout(*(None,), 1))

    def test_defect_validate_registry_entry_extra_keyword(self):
        check_named_refusal(
            self, "validate_registry_entry",
            lambda: mod11.validate_registry_entry(*(None, None, None), extra_kw=1))

    def test_defect_validate_registry_entry_extra_positional(self):
        check_named_refusal(
            self, "validate_registry_entry",
            lambda: mod11.validate_registry_entry(*(None, None, None, None), 1))

    def test_defect_validate_transition_report_extra_keyword(self):
        check_named_refusal(
            self, "validate_transition_report",
            lambda: mod11.validate_transition_report(*(None,), extra_kw=1))

    def test_defect_validate_transition_report_extra_positional(self):
        check_named_refusal(
            self, "validate_transition_report",
            lambda: mod11.validate_transition_report(*(None,), 1))

    def test_defect_validate_transition_unit_extra_keyword(self):
        check_named_refusal(
            self, "validate_transition_unit",
            lambda: mod11.validate_transition_unit(*(None,), extra_kw=1))

    def test_defect_validate_transition_unit_extra_positional(self):
        check_named_refusal(
            self, "validate_transition_unit",
            lambda: mod11.validate_transition_unit(*(None,), 1))

    def test_defect_validate_working_range_claim_extra_keyword(self):
        check_named_refusal(
            self, "validate_working_range_claim",
            lambda: mod11.validate_working_range_claim(*("x", "x", "x", "x"), extra_kw=1))

    def test_defect_validate_working_range_claim_extra_positional(self):
        check_named_refusal(
            self, "validate_working_range_claim",
            lambda: mod11.validate_working_range_claim(*("x", "x", "x", "x"), 1))


class TestFW901Mod11Controls(unittest.TestCase):

    def test_control_judge_registry_entry_extra_keyword(self):
        check_named_refusal(
            self, "judge_registry_entry",
            lambda: mod11.judge_registry_entry(
                None, None, None, extra_kw=1))

    def test_control_judge_registry_entry_extra_positional(self):
        check_named_refusal(
            self, "judge_registry_entry",
            lambda: mod11.judge_registry_entry(
                None, None, None, None, 1))

    def test_control_retirement_verdicts_extra_keyword(self):
        check_named_refusal(
            self, "retirement_verdicts",
            lambda: mod11.retirement_verdicts("F-01", extra_kw=1))

    def test_control_retirement_verdicts_extra_positional(self):
        check_named_refusal(
            self, "retirement_verdicts",
            lambda: mod11.retirement_verdicts("F-01", 1))

    def test_control_make_headline_unit_extra_keyword(self):
        check_named_refusal(
            self, "make_headline_unit",
            lambda: mod11.make_headline_unit({}, extra_kw=1))

    def test_control_make_headline_unit_extra_positional(self):
        check_named_refusal(
            self, "make_headline_unit",
            lambda: mod11.make_headline_unit({}, 1))

    def test_control_first_sentence_served(self):
        self.assertEqual(mod11.first_sentence("Alpha. Beta"), "Alpha")

    def test_control_moved_reading_served(self):
        self.assertTrue(mod11.moved_reading(2, 1))

    def test_control_validate_observation_time_served(self):
        self.assertFalse(mod11.validate_observation_time(None))


if __name__ == "__main__":
    unittest.main()
