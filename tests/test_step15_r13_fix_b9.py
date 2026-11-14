"""Pins for fix wave 12, Builder 9, Group 9.

Rows R12-071 to R12-073 and R12-078 of the Round 12 register.
Each test pins a defect form stated in its row with the proving
acts its source paper used, beside plain controls standing both
ways. MOD-04 rows rest on Blue 4 Finding 3 and Yellow 4 Findings
1 and 3. The MOD-05 row rests on Blue 5 Finding 1.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod05 as mod05


class GetLie(dict):
    """A dict storing one set of values and reporting another
    set through its own get reading, in the form the Round 12
    papers used."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = dict(reported)

    def get(self, key, default=None):
        if key in self._reported:
            return self._reported[key]
        return dict.get(self, key, default)


def lawful_share():
    return {"numerator": 1, "denominator": 2}


class TestR12071BuildViewRecordFreeze(unittest.TestCase):

    def test_rule_version_set_list_is_frozen(self):
        handed = [1, 2]
        record = mod04.build_view_record(
            contents=[], rule_version_set=handed)
        self.assertIsNot(record["rule_version_set"], handed)
        handed.append(99)
        self.assertEqual(record["rule_version_set"], [1, 2])

    def test_position_argument_list_is_frozen(self):
        handed = ["pos-1"]
        record = mod04.build_view_record(contents=[], position=handed)
        self.assertIsNot(
            record["scheduling_position_identifier"], handed)
        handed.append("pos-99")
        self.assertEqual(
            record["scheduling_position_identifier"], ["pos-1"])

    def test_position_from_run_record_positions_by_day_is_frozen(self):
        handed = ["pos-1"]
        run_record = {"positions_by_day": {"1": handed}}
        record = mod04.build_view_record(
            contents=[], run_record=run_record)
        self.assertIsNot(
            record["scheduling_position_identifier"], handed)
        handed.append("pos-99")
        self.assertEqual(
            record["scheduling_position_identifier"], ["pos-1"])

    def test_first_seen_day_inside_contents_is_frozen(self):
        seen = [5]
        item = {"first_seen_day": seen, "delay": 1}
        record = mod04.build_view_record(contents=[item])
        placed = record["first_seen_day_per_record"]["0"]
        self.assertIsNot(placed, seen)
        seen.append(99)
        self.assertEqual(
            record["first_seen_day_per_record"]["0"], [5])
        self.assertEqual(
            record["view_contents"][0]["first_seen_day"], [5])

    def test_delay_inside_contents_is_frozen(self):
        applied = [2]
        item = {"first_seen_day": 5, "delay": applied}
        record = mod04.build_view_record(contents=[item])
        placed = record["delay_applied_per_record"]["0"]
        self.assertIsNot(placed, applied)
        applied.append(99)
        self.assertEqual(record["delay_applied_per_record"]["0"], [2])

    def test_frozen_contents_control_stands(self):
        shared = [1, 2]
        item = {"first_seen_day": 5, "delay": 1, "payload": shared}
        record = mod04.build_view_record(
            contents=[item],
            reputation_and_band={"payload": shared},
            graph_position={"payload": shared})
        shared.append(99)
        self.assertEqual(record["view_contents"][0]["payload"], [1, 2])
        self.assertIs(
            record["view_contents"][0]["payload"],
            record["reputation_and_band_values"]["payload"])


class TestR12072ReportabilityAndOrderGates(unittest.TestCase):

    def test_projection_passed_reads_stored_value(self):
        lying = GetLie(
            {"projection_canary_passed": False},
            {"projection_canary_passed": True})
        self.assertFalse(mod04.projection_passed_for_run(lying))
        self.assertFalse(mod04.projection_passed_for_run(
            {"projection_canary_passed": False}))
        mirror = GetLie(
            {"projection_canary_passed": True},
            {"projection_canary_passed": False})
        self.assertTrue(mod04.projection_passed_for_run(mirror))

    def test_run_is_reportable_reads_stored_canary(self):
        stored = {
            "projection_canary_passed": False,
            "scheduling_order_identifier": "order-1",
            "run_class": "screening",
            "reportable": True,
        }
        lying = GetLie(stored, {"projection_canary_passed": True})
        self.assertFalse(mod04.run_is_reportable(lying))
        self.assertFalse(mod04.run_is_reportable(dict(stored)))
        passed = dict(stored)
        passed["projection_canary_passed"] = True
        self.assertTrue(mod04.run_is_reportable(passed))

    def test_scheduling_order_reads_stored_run_class(self):
        stored = {
            "run_class": "headline",
            "scheduling_order_identifier": "prototype",
        }
        lying = GetLie(stored, {"run_class": "screening"})
        self.assertFalse(mod04.validate_run_scheduling_order(lying))
        self.assertFalse(
            mod04.validate_run_scheduling_order(dict(stored)))
        stated = {
            "run_class": "headline",
            "scheduling_order_identifier": "order-1",
        }
        self.assertTrue(mod04.validate_run_scheduling_order(stated))

    def test_headline_order_reads_stored_order(self):
        stored = {
            "run_class": "headline",
            "scheduling_order_identifier": "prototype",
        }
        lying = GetLie(
            stored, {"scheduling_order_identifier": "order-1"})
        self.assertFalse(mod04.headline_order_stands(lying))
        self.assertFalse(mod04.headline_order_stands(dict(stored)))
        mirror = GetLie(
            {"run_class": "headline",
             "scheduling_order_identifier": "order-1"},
            {"scheduling_order_identifier": "prototype"})
        self.assertTrue(mod04.headline_order_stands(mirror))


class TestR12073DeliveryCompleteness(unittest.TestCase):

    def test_event_kind_reads_stored_value(self):
        event = GetLie({"kind": "work completion"}, {"kind": "gossip"})
        deliveries = [{"event": {"kind": "gossip"}}]
        self.assertFalse(mod04.delivery_completeness([event], deliveries))
        self.assertFalse(mod04.delivery_completeness(
            [{"kind": "work completion"}], deliveries))
        self.assertTrue(mod04.delivery_completeness(
            [{"kind": "gossip"}], deliveries))

    def test_delivery_entry_reads_stored_event(self):
        entry = GetLie(
            {"event": {"kind": "work completion"}},
            {"event": {"kind": "gossip"}})
        events = [{"kind": "gossip"}]
        self.assertFalse(mod04.delivery_completeness(events, [entry]))

    def test_nested_event_kind_reads_stored_value(self):
        inner = GetLie({"kind": "work completion"}, {"kind": "gossip"})
        entry = {"event": inner}
        events = [{"kind": "gossip"}]
        self.assertFalse(mod04.delivery_completeness(events, [entry]))


class TestR12078CostStatementPlainForm(unittest.TestCase):

    def test_share_log_in_no_log_form_is_invalid(self):
        for bad in (0, "text", True, [], {}):
            record = {
                "share_log": bad,
                "degree_distribution_log": {"a": 1},
            }
            self.assertFalse(
                mod05.cost_statement_valid(record), repr(bad))

    def test_degree_log_in_no_log_form_is_invalid(self):
        for bad in (0, False, ""):
            record = {
                "share_log": [lawful_share()],
                "degree_distribution_log": bad,
            }
            self.assertFalse(
                mod05.cost_statement_valid(record), repr(bad))

    def test_consumers_carry_the_same_refusal(self):
        bad_share = {
            "share_log": 0,
            "degree_distribution_log": {"a": 1},
        }
        self.assertEqual(mod05.cost_statement(bad_share), {"valid": False})
        self.assertFalse(mod05.validate_run_share_logs(bad_share))
        bad_degree = {
            "share_log": [lawful_share()],
            "degree_distribution_log": 0,
        }
        self.assertEqual(mod05.cost_statement(bad_degree), {"valid": False})
        self.assertFalse(mod05.validate_run_share_logs(bad_degree))

    def test_controls_stand_both_ways(self):
        lawful = {
            "share_log": [lawful_share()],
            "degree_distribution_log": {"a": 1},
        }
        self.assertTrue(mod05.cost_statement_valid(lawful))
        self.assertTrue(mod05.cost_statement_valid({
            "share_log": (lawful_share(),),
            "degree_distribution_log": {"a": 1},
        }))
        self.assertTrue(mod05.cost_statement_valid({
            "share_log": lawful_share(),
            "degree_distribution_log": {"a": 1},
        }))
        self.assertTrue(mod05.cost_statement_valid({
            "share_log": [lawful_share()],
            "degree_distribution_log": {},
        }))
        self.assertFalse(mod05.cost_statement_valid(
            {"degree_distribution_log": {"a": 1}}))
        self.assertFalse(mod05.cost_statement_valid(
            {"share_log": [lawful_share()]}))
        self.assertFalse(mod05.cost_statement_valid({
            "share_log": None,
            "degree_distribution_log": {"a": 1},
        }))
        self.assertFalse(mod05.cost_statement_valid({
            "share_log": [lawful_share()],
            "degree_distribution_log": None,
        }))
        fitted = dict(lawful)
        fitted["assumption_share"] = {"fitted": True}
        self.assertFalse(mod05.cost_statement_valid(fitted))
        self.assertFalse(mod05.cost_statement_valid({
            "share_log": [0],
            "degree_distribution_log": {"a": 1},
        }))
        self.assertFalse(mod05.cost_statement_valid({
            "share_log": [{"numerator": 0, "denominator": 0}],
            "degree_distribution_log": {"a": 1},
        }))


if __name__ == "__main__":
    unittest.main()
