"""Test group TG-10.1. One run record, complete or invalid.

Slice S-10, MOD-10 Recorder and stores. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod10, and
records whether the surface stands. While the surface stands absent, each non
gated test fails with a message naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Forms 36 and 37 field names below are transliterations of the landed field
lists in plan section 3, 8 fields for Form 36 EventLog and 3 fields for
Form 37 DailySnapshot. No field beyond those lists is named anywhere here.
"""
import unittest

try:
    from crucible import mod10
    SURFACE = mod10
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-10.1"

EVENTLOG_FIELDS = (
    "run_identifier",
    "journal_position",
    "event_identifier",
    "simulated_day",
    "event_imported_row_form",
    "agent_identifier",
    "superseded_from_journal_position",
    "resume_attempt_identifier",
)
DAILY_SNAPSHOT_FIELDS = (
    "run_identifier",
    "simulated_day",
    "daily_state_as_delivered",
)
SEVEN_GROUPS = (
    "assumption_record",
    "identity_and_design",
    "interpretation_choices",
    "joined_done_test",
    "outcome_and_retention",
    "reserved_matter",
    "variant_stamp",
)


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": product surface crucible.mod10 stands absent ("
            + repr(SURFACE_ERROR) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": product surface crucible.mod10 lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )


class TestSingleRecordPerRun(unittest.TestCase):
    def test_single_record_per_run(self):
        """Fixture: a completed run inspected across all stores, as TG-10.1 states.
        Pins: exactly one RunRecord exists for the run, in the seven group form Shape 4 names, reconciling the five source forms under AC-14.
        Bar: a second record for the same run, or a group filled by a writer other than its owner, fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.1; with the surface present, a run holding zero or two run records fails.
        """
        require_surface(self, "single record per run", "run_records_for_run")
        completed = {
            "run_id": "run-under-test",
            "run_identifier": "run-under-test",
            "groups": {name: {} for name in SEVEN_GROUPS},
        }
        try:
            SURFACE.retain_run_record(completed)
        except ValueError:
            pass
        records = SURFACE.run_records_for_run(run_id="run-under-test")
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertIn("groups", record)
        self.assertEqual(tuple(sorted(record["groups"])), SEVEN_GROUPS)

    def test_second_record_or_foreign_writer_fails(self):
        """Fixture: a run holding two run records, and a run record group filled by a writer other than its owner, as TG-10.1 states.
        Pins: the Recorder rejects both forms; neither stands as the one run record.
        Bar: a second record for the same run, or a group filled by a writer other than its owner, fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.1; with the surface present, acceptance of either form fails.
        """
        require_surface(self, "second record or foreign writer rejected", "validate_run_record_set")
        duplicate = [{"run_id": "r"}, {"run_id": "r"}]
        self.assertFalse(SURFACE.validate_run_record_set(duplicate))
        foreign = [{"run_id": "r", "group_writers": {"outcome": "not-the-owner"}}]
        self.assertFalse(SURFACE.validate_run_record_set(foreign))


class TestDailyAggregatesSufficiency(unittest.TestCase):
    def test_daily_aggregates_sufficiency(self):
        """Fixture: a run whose end of run regime classification is rederived from its DailyAggregates alone, as TG-10.1 states.
        Pins: one aggregates record per run per day, holding the four joint outcome components for that day with the same denominators defined per day, plus the honest share for that day, plus the gate passing share for each epoch ending on that day, so the classification can be rederived from the aggregates alone.
        Bar: the components stand computed per viewer with the viewer identifier on every component and the divergence companion beside the form; no singular vector is reported.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.1; with the surface present, aggregates that cannot rederive the classification fail.
        """
        require_surface(self, "daily aggregates sufficiency", "daily_aggregates_for_run", "rederive_regime_classification")
        aggregates = SURFACE.daily_aggregates_for_run(run_id="run-under-test")
        self.assertTrue(aggregates)
        days = []
        for record in aggregates:
            self.assertIn("simulated_day", record)
            days.append(record["simulated_day"])
            self.assertIn("viewer_id", record)
            self.assertEqual(len(record["joint_outcome_components"]), 4)
            self.assertIn("component_denominators", record)
            self.assertEqual(len(record["component_denominators"]), 4)
            self.assertIn("honest_share", record)
            self.assertIn("gate_passing_shares", record)
            self.assertIn("epochs_ending_on_day", record)
            self.assertEqual(
                tuple(sorted(record["gate_passing_shares"])),
                tuple(sorted(record["epochs_ending_on_day"])),
            )
            self.assertIn("divergence_companion", record)
        self.assertEqual(len(days), len(set(days)))
        self.assertIsNotNone(SURFACE.rederive_regime_classification(aggregates))

    def test_singular_vector_or_missing_viewer_fails(self):
        """Fixture: daily aggregates carrying one component with no viewer identifier, and a singular vector form, as TG-10.1 states.
        Pins: both forms fail validation; cross run comparison rests on per viewer values compared viewer to viewer only.
        Bar: no singular vector is reported, and no cross run comparison rests on these daily components as one quantity.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.1; with the surface present, acceptance of either form fails.
        """
        require_surface(self, "singular vector and viewerless component rejected", "validate_daily_aggregates")
        no_viewer = [{"joint_outcome_components": [0, 0, 0, 0]}]
        self.assertFalse(SURFACE.validate_daily_aggregates(no_viewer))
        singular = [{"viewer_id": "v", "singular_vector": [0, 0, 0, 0]}]
        self.assertFalse(SURFACE.validate_daily_aggregates(singular))


class TestLandedFormLists(unittest.TestCase):
    def test_eventlog_landed_field_list(self):
        """Fixture: no inventory fixture; the landed field list of Form 36 EventLog in plan section 3, 8 fields, as the task charge states.
        Pins: the store surface for the EventLog carries exactly the 8 landed fields and no other field.
        Bar: a field invented beyond the landed list fails this test; a hash or digest field is named in no part of this test, standing in exclusion 1 of the OP-18 design act.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.1; with the surface present, a field list differing from the landed list fails.
        """
        require_surface(self, "EventLog landed field list of 8 fields", "event_log_fields")
        self.assertEqual(tuple(SURFACE.event_log_fields()), EVENTLOG_FIELDS)

    def test_daily_snapshot_landed_field_list(self):
        """Fixture: no inventory fixture; the landed field list of Form 37 DailySnapshot in plan section 3, 3 fields, as the task charge states.
        Pins: the store surface for the DailySnapshot carries exactly the 3 landed fields and no other field.
        Bar: a field invented beyond the landed list fails this test; no subfield of the daily state is named in this test, standing in exclusion 7 of the OP-18 design act.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.1; with the surface present, a field list differing from the landed list fails.
        """
        require_surface(self, "DailySnapshot landed field list of 3 fields", "daily_snapshot_fields")
        self.assertEqual(tuple(SURFACE.daily_snapshot_fields()), DAILY_SNAPSHOT_FIELDS)

    def test_eventlog_remainder_gated_on_op18(self):
        """Fixture: none; the remainder of Form 36 beyond its landed list.
        Pins: no behaviour; this test records its state as gated on OP-18, BLOCKED-CARRIED on the 11 exclusions of the design act at design steps step-12-op18-design-act.
        Bar: no test rests on a gap the exclusions name, among them the internal fields of the imported event rows at OP-12 and the form of the EventLog completeness statement.
        Failure: gated form only; this test never passes while OP-18 stands blocked.
        """
        self.skipTest("gated on OP-18: remainder of Form 36 EventLog stands BLOCKED-CARRIED on the 11 exclusions")

    def test_daily_snapshot_remainder_gated_on_op18(self):
        """Fixture: none; the remainder of Form 37 beyond its landed list.
        Pins: no behaviour; this test records its state as gated on OP-18, BLOCKED-CARRIED on the 11 exclusions of the design act at design steps step-12-op18-design-act.
        Bar: no test rests on a gap the exclusions name, among them the subfield list of the daily state.
        Failure: gated form only; this test never passes while OP-18 stands blocked.
        """
        self.skipTest("gated on OP-18: remainder of Form 37 DailySnapshot stands BLOCKED-CARRIED on the 11 exclusions")


if __name__ == "__main__":
    unittest.main()
