"""Test group TG-10.3. Retention tiering and the summary record amendment.

Slice S-10, MOD-10 Recorder and stores. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod10, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
"""
import copy
import unittest

try:
    from crucible import mod10
    SURFACE = mod10
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-10.3"


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


class TestFlagRuleAmendmentForm(unittest.TestCase):
    def test_flag_rule_amendment_form(self):
        """Fixture: a closed run whose flag rule evaluation promotes it after close, as TG-10.3 states.
        Pins: the summary record is a stored record, written at run close with its content computed at that writing from the RunRecord, and the program that evaluates the flag rule writes the promotion, its inputs, and its outcome into that stored summary record itself; the rule may promote any run to Tier 3 and never demotes, per operation C-08.
        Bar: promotion by a person after close is barred, and a reader reads the retention tier and the flag list as they stand at the last evaluation, from the stored record and not from a summary computed on read.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.3; with the surface present, a promotion not written into the stored record by the evaluating program fails.
        """
        require_surface(self, "flag rule amendment written into the stored summary record", "summary_record_for_run", "apply_flag_evaluation")
        record = SURFACE.summary_record_for_run(run_id="run-under-test")
        self.assertEqual(record["written_at"], "run_close")
        updated = SURFACE.apply_flag_evaluation(record, outcome="promote", tier="Tier 3")
        self.assertEqual(updated["retention_tier"], "Tier 3")
        self.assertIn("flag_evaluation", updated)
        self.assertIn("inputs", updated["flag_evaluation"])
        self.assertIn("outcome", updated["flag_evaluation"])

    def test_person_promotion_and_demotion_fail(self):
        """Fixture: a closed run with a promotion attempted by a person after close, and a flag evaluation attempting a demotion, as TG-10.3 states.
        Pins: both acts are rejected; the stored summary record stands unchanged by either.
        Bar: promotion by a person after close is barred, and the flag rule never demotes.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.3; with the surface present, acceptance of either act fails.
        """
        require_surface(self, "person promotion barred and demotion barred", "apply_flag_evaluation")
        record = {"run_id": "r", "retention_tier": "Tier 2", "written_at": "run_close"}
        with self.assertRaises(Exception):
            SURFACE.apply_flag_evaluation(record, outcome="promote", tier="Tier 3", actor="person")
        with self.assertRaises(Exception):
            SURFACE.apply_flag_evaluation(record, outcome="demote", tier="Tier 1")

    def test_interval_tier_presented_as_final_fails(self):
        """Fixture: a report built from interval records presenting an interval tier as final, as TG-10.3 states.
        Pins: the report form fails validation; the tier stands read from the stored summary record at the last evaluation only.
        Bar: a report built from interval records that presents an interval tier as final fails this group and TG-10.4 with it.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.3; with the surface present, acceptance of the report form fails.
        """
        require_surface(self, "interval tier presented as final rejected", "validate_retention_report")
        report = {"source": "interval_records", "tier_claim": "final"}
        self.assertFalse(SURFACE.validate_retention_report(report))


class TestAnnotationAppend(unittest.TestCase):
    def test_annotation_append_does_not_rewrite(self):
        """Fixture: an anchor scenario annotation appended after a checkpoint was written, then a resume from that checkpoint, as TG-10.3 states.
        Pins: the resumed run sees the same annotation link as the run that wrote the checkpoint; a closed AnchorScenarioRecord is never edited in place, and the annotation travels as an AnnotationRecord reached through the link, per Shape 16 and operation C-06.
        Bar: annotation state as at the checkpoint is expressly not claimed, per Contract I.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.3; with the surface present, an in place edit of the closed record, or a changed annotation link on resume, fails.
        """
        require_surface(self, "annotation append does not rewrite the closed record", "append_annotation", "annotation_link_at_checkpoint", "resume_from_checkpoint")
        checkpoint = {"run_id": "r", "annotation_link": "link-1", "anchor_record": {"closed": True, "content": "original anchor content"}}
        closed_before = copy.deepcopy(checkpoint["anchor_record"])
        after = SURFACE.append_annotation(checkpoint, annotation={"note": "appended"})
        self.assertTrue(after["anchor_record"]["closed"])
        self.assertEqual(after["anchor_record"], closed_before)
        self.assertEqual(SURFACE.annotation_link_at_checkpoint(after), "link-1")
        self.assertIn("annotation_record", after)
        resumed = SURFACE.resume_from_checkpoint(after)
        self.assertEqual(SURFACE.annotation_link_at_checkpoint(resumed), "link-1")
        self.assertEqual(resumed["annotation_record"], after["annotation_record"])
        self.assertEqual(resumed["annotation_record"]["note"], "appended")

    def test_annotation_state_equality_claim_fails(self):
        """Fixture: a claim asserting equality of annotation state across an annotation append, as TG-10.3 states.
        Pins: the claim fails validation, because the brief states the negative limb in words.
        Bar: a test asserting equality of annotation state across the append fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.3; with the surface present, acceptance of the equality claim fails.
        """
        require_surface(self, "annotation state equality claim rejected", "validate_annotation_claim")
        claim = {"claim": "annotation_state_equal_across_append"}
        self.assertFalse(SURFACE.validate_annotation_claim(claim))


if __name__ == "__main__":
    unittest.main()
