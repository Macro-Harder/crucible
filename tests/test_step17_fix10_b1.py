"""Step 17 fix wave 10, Builder 1 defect tests (FW10-01, Medium,
ruling T17R9-01, Slice 1, mod05).

The argument count family at the owed enumeration doors of
mod05: at each of the 46 doors named in the charge, an extra
argument handing past the full signature, in keyword form and
in positional form, must stand refused in the named form of
the module, a ValueError stating the door, the beyond ground,
and the next step, in the FW8-01 cure form, instead of
escaping as a bare interpreter TypeError. The 44 class A doors
escape in both handing forms on the uncured tree; the 2 class
B doors, compute_share and vouch, escape in positional form
and stand in named form in keyword form on the uncured tree,
their keyword tests standing as controls. Outcomes stand
judged by stored value in code, never by a repr of a returned
value (T17R3-23).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod05 as mod05


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, door_word, call):
    with case.assertRaises(ValueError) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    case.assertIn(door_word, message)
    case.assertIn("beyond", message)
    case.assertIn("next step", message.lower())
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


class TestFW1001Mod05Doors(unittest.TestCase):

    def test_defect_accept_work_extra_keyword(self):
        check_named_refusal(
            self, "accept_work",
            lambda: mod05.accept_work(events=1, extra_kw=1))

    def test_defect_accept_work_extra_positional(self):
        check_named_refusal(
            self, "accept_work",
            lambda: mod05.accept_work(1, 1))

    def test_defect_accuracy_ranges_stand_unmerged_extra_keyword(self):
        check_named_refusal(
            self, "accuracy_ranges_stand_unmerged",
            lambda: mod05.accuracy_ranges_stand_unmerged(ranges=1, extra_kw=1))

    def test_defect_accuracy_ranges_stand_unmerged_extra_positional(self):
        check_named_refusal(
            self, "accuracy_ranges_stand_unmerged",
            lambda: mod05.accuracy_ranges_stand_unmerged(1, 1))

    def test_defect_adjudicate_extra_keyword(self):
        check_named_refusal(
            self, "adjudicate",
            lambda: mod05.adjudicate(case=1, accuracy_value=1, assumption_set=1, row=1, error_direction=1, outcome=1, derived_from=1, extra_kw=1))

    def test_defect_adjudicate_extra_positional(self):
        check_named_refusal(
            self, "adjudicate",
            lambda: mod05.adjudicate(1, 1, 1, 1, 1, 1, 1, 1))

    def test_defect_adjudication_input_failure_class_extra_keyword(self):
        check_named_refusal(
            self, "adjudication_input_failure_class",
            lambda: mod05.adjudication_input_failure_class(extra_kw=1))

    def test_defect_adjudication_input_failure_class_extra_positional(self):
        check_named_refusal(
            self, "adjudication_input_failure_class",
            lambda: mod05.adjudication_input_failure_class(1))

    def test_defect_adjudication_outcome_extra_keyword(self):
        check_named_refusal(
            self, "adjudication_outcome",
            lambda: mod05.adjudication_outcome(case=1, extra_kw=1))

    def test_defect_adjudication_outcome_extra_positional(self):
        check_named_refusal(
            self, "adjudication_outcome",
            lambda: mod05.adjudication_outcome(1, 1))

    def test_defect_aggregation_interface_extra_keyword(self):
        check_named_refusal(
            self, "aggregation_interface",
            lambda: mod05.aggregation_interface(extra_kw=1))

    def test_defect_aggregation_interface_extra_positional(self):
        check_named_refusal(
            self, "aggregation_interface",
            lambda: mod05.aggregation_interface(1))

    def test_defect_aggregation_score_extra_keyword(self):
        check_named_refusal(
            self, "aggregation_score",
            lambda: mod05.aggregation_score(inputs=1, extra_kw=1))

    def test_defect_aggregation_score_extra_positional(self):
        check_named_refusal(
            self, "aggregation_score",
            lambda: mod05.aggregation_score(1, 1))

    def test_defect_alternation_result_extra_keyword(self):
        check_named_refusal(
            self, "alternation_result",
            lambda: mod05.alternation_result(decay_slice=1, same_or_different_retention=1, prior_bad_phase_count=1, highest_band=1, bad_phases_before_exclusion=1, ring_highest_band=1, ring_bad_phases_before_exclusion=1, reported_as=1, extra_kw=1))

    def test_defect_alternation_result_extra_positional(self):
        check_named_refusal(
            self, "alternation_result",
            lambda: mod05.alternation_result(1, 1, 1, 1, 1, 1, 1, 1, 1))

    def test_defect_band_membership_extra_keyword(self):
        check_named_refusal(
            self, "band_membership",
            lambda: mod05.band_membership(score=1, bands=1, evaluation_order=1, extra_kw=1))

    def test_defect_band_membership_extra_positional(self):
        check_named_refusal(
            self, "band_membership",
            lambda: mod05.band_membership(1, 1, 1, 1))

    def test_defect_band_transition_extra_keyword(self):
        check_named_refusal(
            self, "band_transition",
            lambda: mod05.band_transition(scores=1, boundary=1, distance_slices=1, form=1, extra_kw=1))

    def test_defect_band_transition_extra_positional(self):
        check_named_refusal(
            self, "band_transition",
            lambda: mod05.band_transition(1, 1, 1, 1, 1))

    def test_defect_boundary_neighbourhood_extra_keyword(self):
        check_named_refusal(
            self, "boundary_neighbourhood",
            lambda: mod05.boundary_neighbourhood(scores=1, boundary=1, distance_slices=1, extra_kw=1))

    def test_defect_boundary_neighbourhood_extra_positional(self):
        check_named_refusal(
            self, "boundary_neighbourhood",
            lambda: mod05.boundary_neighbourhood(1, 1, 1, 1))

    def test_defect_challenge_outcome_extra_keyword(self):
        check_named_refusal(
            self, "challenge_outcome",
            lambda: mod05.challenge_outcome(case=1, extra_kw=1))

    def test_defect_challenge_outcome_extra_positional(self):
        check_named_refusal(
            self, "challenge_outcome",
            lambda: mod05.challenge_outcome(1, 1))

    def test_defect_compare_aggregation_extra_keyword(self):
        check_named_refusal(
            self, "compare_aggregation",
            lambda: mod05.compare_aggregation(inputs=1, extra_kw=1))

    def test_defect_compare_aggregation_extra_positional(self):
        check_named_refusal(
            self, "compare_aggregation",
            lambda: mod05.compare_aggregation(1, 1))

    def test_defect_component_extra_keyword(self):
        check_named_refusal(
            self, "component",
            lambda: mod05.component(edges=1, component_definition_version=1, extra_kw=1))

    def test_defect_component_extra_positional(self):
        check_named_refusal(
            self, "component",
            lambda: mod05.component(1, 1, 1))

    def test_defect_component_cap_check_extra_keyword(self):
        check_named_refusal(
            self, "component_cap_check",
            lambda: mod05.component_cap_check(edges=1, cap_edges=1, extra_kw=1))

    def test_defect_component_cap_check_extra_positional(self):
        check_named_refusal(
            self, "component_cap_check",
            lambda: mod05.component_cap_check(1, 1, 1))

    def test_defect_cost_statement_extra_keyword(self):
        check_named_refusal(
            self, "cost_statement",
            lambda: mod05.cost_statement(record=1, extra_kw=1))

    def test_defect_cost_statement_extra_positional(self):
        check_named_refusal(
            self, "cost_statement",
            lambda: mod05.cost_statement(1, 1))

    def test_defect_cost_statement_valid_extra_keyword(self):
        check_named_refusal(
            self, "cost_statement_valid",
            lambda: mod05.cost_statement_valid(record=1, extra_kw=1))

    def test_defect_cost_statement_valid_extra_positional(self):
        check_named_refusal(
            self, "cost_statement_valid",
            lambda: mod05.cost_statement_valid(1, 1))

    def test_defect_credit_work_extra_keyword(self):
        check_named_refusal(
            self, "credit_work",
            lambda: mod05.credit_work(events=1, extra_kw=1))

    def test_defect_credit_work_extra_positional(self):
        check_named_refusal(
            self, "credit_work",
            lambda: mod05.credit_work(1, 1))

    def test_defect_decay_result_extra_keyword(self):
        check_named_refusal(
            self, "decay_result",
            lambda: mod05.decay_result(half_life_days=1, reported_as=1, extra_kw=1))

    def test_defect_decay_result_extra_positional(self):
        check_named_refusal(
            self, "decay_result",
            lambda: mod05.decay_result(1, 1, 1))

    def test_defect_decay_slices_extra_keyword(self):
        check_named_refusal(
            self, "decay_slices",
            lambda: mod05.decay_slices(extra_kw=1))

    def test_defect_decay_slices_extra_positional(self):
        check_named_refusal(
            self, "decay_slices",
            lambda: mod05.decay_slices(1))

    def test_defect_eligibility_extra_keyword(self):
        check_named_refusal(
            self, "eligibility",
            lambda: mod05.eligibility(score=1, bands=1, evaluation_order=1, panel_minimum=1, cap_maximum=1, extra_kw=1))

    def test_defect_eligibility_extra_positional(self):
        check_named_refusal(
            self, "eligibility",
            lambda: mod05.eligibility(1, 1, 1, 1, 1, 1))

    def test_defect_evaluation_order_record_extra_keyword(self):
        check_named_refusal(
            self, "evaluation_order_record",
            lambda: mod05.evaluation_order_record(order=1, batch=1, extra_kw=1))

    def test_defect_evaluation_order_record_extra_positional(self):
        check_named_refusal(
            self, "evaluation_order_record",
            lambda: mod05.evaluation_order_record(1, 1, 1))

    def test_defect_excluded_class_counts_extra_keyword(self):
        check_named_refusal(
            self, "excluded_class_counts",
            lambda: mod05.excluded_class_counts(cases=1, extra_kw=1))

    def test_defect_excluded_class_counts_extra_positional(self):
        check_named_refusal(
            self, "excluded_class_counts",
            lambda: mod05.excluded_class_counts(1, 1))

    def test_defect_feeder_position_extra_keyword(self):
        check_named_refusal(
            self, "feeder_position",
            lambda: mod05.feeder_position(feeder=1, edges=1, extra_kw=1))

    def test_defect_feeder_position_extra_positional(self):
        check_named_refusal(
            self, "feeder_position",
            lambda: mod05.feeder_position(1, 1, 1))

    def test_defect_graph_facts_extra_keyword(self):
        check_named_refusal(
            self, "graph_facts",
            lambda: mod05.graph_facts(edges=1, by_epoch=1, component_definition_version=1, extra_kw=1))

    def test_defect_graph_facts_extra_positional(self):
        check_named_refusal(
            self, "graph_facts",
            lambda: mod05.graph_facts(1, 1, 1, 1))

    def test_defect_graph_snapshot_extra_keyword(self):
        check_named_refusal(
            self, "graph_snapshot",
            lambda: mod05.graph_snapshot(edges=1, component_definition_version=1, edge_list_reference=1, extra_kw=1))

    def test_defect_graph_snapshot_extra_positional(self):
        check_named_refusal(
            self, "graph_snapshot",
            lambda: mod05.graph_snapshot(1, 1, 1, 1))

    def test_defect_panel_inputs_extra_keyword(self):
        check_named_refusal(
            self, "panel_inputs",
            lambda: mod05.panel_inputs(case=1, extra_kw=1))

    def test_defect_panel_inputs_extra_positional(self):
        check_named_refusal(
            self, "panel_inputs",
            lambda: mod05.panel_inputs(1, 1))

    def test_defect_population_figure_extra_keyword(self):
        check_named_refusal(
            self, "population_figure",
            lambda: mod05.population_figure(envelope_value=1, shares=1, record_state=1, extra_kw=1))

    def test_defect_population_figure_extra_positional(self):
        check_named_refusal(
            self, "population_figure",
            lambda: mod05.population_figure(1, 1, 1, 1))

    def test_defect_realised_degree_distribution_extra_keyword(self):
        check_named_refusal(
            self, "realised_degree_distribution",
            lambda: mod05.realised_degree_distribution(edges=1, by_epoch=1, extra_kw=1))

    def test_defect_realised_degree_distribution_extra_positional(self):
        check_named_refusal(
            self, "realised_degree_distribution",
            lambda: mod05.realised_degree_distribution(1, 1, 1))

    def test_defect_recomputation_sample_extra_keyword(self):
        check_named_refusal(
            self, "recomputation_sample",
            lambda: mod05.recomputation_sample(records=1, extra_kw=1))

    def test_defect_recomputation_sample_extra_positional(self):
        check_named_refusal(
            self, "recomputation_sample",
            lambda: mod05.recomputation_sample(1, 1))

    def test_defect_reputation_and_band_values_extra_keyword(self):
        check_named_refusal(
            self, "reputation_and_band_values",
            lambda: mod05.reputation_and_band_values(agents_scores=1, bands=1, viewer=1, evaluation_order=1, extra_kw=1))

    def test_defect_reputation_and_band_values_extra_positional(self):
        check_named_refusal(
            self, "reputation_and_band_values",
            lambda: mod05.reputation_and_band_values(1, 1, 1, 1, 1))

    def test_defect_score_bearing_figure_extra_keyword(self):
        check_named_refusal(
            self, "score_bearing_figure",
            lambda: mod05.score_bearing_figure(envelope_value=1, share=1, extra_kw=1))

    def test_defect_score_bearing_figure_extra_positional(self):
        check_named_refusal(
            self, "score_bearing_figure",
            lambda: mod05.score_bearing_figure(1, 1, 1))

    def test_defect_share_for_epoch_extra_keyword(self):
        check_named_refusal(
            self, "share_for_epoch",
            lambda: mod05.share_for_epoch(epoch=1, eligible=1, passing=1, extra_kw=1))

    def test_defect_share_for_epoch_extra_positional(self):
        check_named_refusal(
            self, "share_for_epoch",
            lambda: mod05.share_for_epoch(1, 1, 1, 1))

    def test_defect_undelivered_share_extra_keyword(self):
        check_named_refusal(
            self, "undelivered_share",
            lambda: mod05.undelivered_share(extra_kw=1))

    def test_defect_undelivered_share_extra_positional(self):
        check_named_refusal(
            self, "undelivered_share",
            lambda: mod05.undelivered_share(1))

    def test_defect_validate_band_transition_result_extra_keyword(self):
        check_named_refusal(
            self, "validate_band_transition_result",
            lambda: mod05.validate_band_transition_result(result=1, extra_kw=1))

    def test_defect_validate_band_transition_result_extra_positional(self):
        check_named_refusal(
            self, "validate_band_transition_result",
            lambda: mod05.validate_band_transition_result(1, 1))

    def test_defect_validate_evaluation_order_extra_keyword(self):
        check_named_refusal(
            self, "validate_evaluation_order",
            lambda: mod05.validate_evaluation_order(record=1, extra_kw=1))

    def test_defect_validate_evaluation_order_extra_positional(self):
        check_named_refusal(
            self, "validate_evaluation_order",
            lambda: mod05.validate_evaluation_order(1, 1))

    def test_defect_validate_graph_snapshot_extra_keyword(self):
        check_named_refusal(
            self, "validate_graph_snapshot",
            lambda: mod05.validate_graph_snapshot(snapshot=1, edges=1, extra_kw=1))

    def test_defect_validate_graph_snapshot_extra_positional(self):
        check_named_refusal(
            self, "validate_graph_snapshot",
            lambda: mod05.validate_graph_snapshot(1, 1, 1))

    def test_defect_validate_headline_adjudication_claim_extra_keyword(self):
        check_named_refusal(
            self, "validate_headline_adjudication_claim",
            lambda: mod05.validate_headline_adjudication_claim(family_record=1, run_record=1, extra_kw=1))

    def test_defect_validate_headline_adjudication_claim_extra_positional(self):
        check_named_refusal(
            self, "validate_headline_adjudication_claim",
            lambda: mod05.validate_headline_adjudication_claim(1, 1, 1))

    def test_defect_validate_logged_share_extra_keyword(self):
        check_named_refusal(
            self, "validate_logged_share",
            lambda: mod05.validate_logged_share(logged=1, extra_kw=1))

    def test_defect_validate_logged_share_extra_positional(self):
        check_named_refusal(
            self, "validate_logged_share",
            lambda: mod05.validate_logged_share(1, 1))

    def test_defect_validate_panel_inputs_extra_keyword(self):
        check_named_refusal(
            self, "validate_panel_inputs",
            lambda: mod05.validate_panel_inputs(inputs=1, extra_kw=1))

    def test_defect_validate_panel_inputs_extra_positional(self):
        check_named_refusal(
            self, "validate_panel_inputs",
            lambda: mod05.validate_panel_inputs(1, 1))

    def test_defect_validate_proportion_extra_keyword(self):
        check_named_refusal(
            self, "validate_proportion",
            lambda: mod05.validate_proportion(record=1, extra_kw=1))

    def test_defect_validate_proportion_extra_positional(self):
        check_named_refusal(
            self, "validate_proportion",
            lambda: mod05.validate_proportion(1, 1))

    def test_defect_validate_report_reading_extra_keyword(self):
        check_named_refusal(
            self, "validate_report_reading",
            lambda: mod05.validate_report_reading(divergence_count=1, resolved=1, extra_kw=1))

    def test_defect_validate_report_reading_extra_positional(self):
        check_named_refusal(
            self, "validate_report_reading",
            lambda: mod05.validate_report_reading(1, 1, 1))

    def test_defect_validate_run_share_logs_extra_keyword(self):
        check_named_refusal(
            self, "validate_run_share_logs",
            lambda: mod05.validate_run_share_logs(record=1, extra_kw=1))

    def test_defect_validate_run_share_logs_extra_positional(self):
        check_named_refusal(
            self, "validate_run_share_logs",
            lambda: mod05.validate_run_share_logs(1, 1))

    def test_defect_validate_view_wording_extra_keyword(self):
        check_named_refusal(
            self, "validate_view_wording",
            lambda: mod05.validate_view_wording(wording=1, extra_kw=1))

    def test_defect_validate_view_wording_extra_positional(self):
        check_named_refusal(
            self, "validate_view_wording",
            lambda: mod05.validate_view_wording(1, 1))

    def test_defect_compute_share_extra_keyword(self):
        check_named_refusal(
            self, "compute_share",
            lambda: mod05.compute_share(eligible=1, passing=1, epoch=1, extra_kw=1))

    def test_defect_compute_share_extra_positional(self):
        check_named_refusal(
            self, "compute_share",
            lambda: mod05.compute_share(1, 1, 1, 1))

    def test_defect_vouch_extra_keyword(self):
        check_named_refusal(
            self, "vouch",
            lambda: mod05.vouch(voucher=1, vouchee=1, stake=1, creation_day=1, lifetime=1, score_bearing=1, component_identifier=1, component_definition_version=1, extra_kw=1))

    def test_defect_vouch_extra_positional(self):
        check_named_refusal(
            self, "vouch",
            lambda: mod05.vouch(1, 1, 1, 1, 1, 1, 1, 1, 1))


if __name__ == "__main__":
    unittest.main()
