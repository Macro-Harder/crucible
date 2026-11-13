"""Test group TG-01.5. The reconciliation surface (AC-14).

Slice S-01, MOD-01 Types and validation. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod01, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
The five source forms are the forms brief section 10 names for AC-14: ARB,
BOO, PAM, RFO, and RET, carried at register duplicated finding DUP-4.
"""
import unittest

try:
    from crucible import mod01
    SURFACE = mod01
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-01.5"
SOURCE_FORMS = ("ARB", "BOO", "PAM", "RFO", "RET")


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": pinned behaviour not built: " + behaviour
            + " (surface crucible.mod01 stands absent: " + repr(SURFACE_ERROR) + ")"
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": pinned behaviour not built: " + behaviour
                + " (surface crucible.mod01 lacks " + attr + ")"
            )


def trace_with_one_load_bearing_entry_removed(testcase):
    trace = [dict(entry) for entry in SURFACE.reconciliation_trace()]
    kept = []
    removed = False
    for entry in trace:
        if not removed and entry.get("load_bearing"):
            removed = True
            continue
        kept.append(entry)
    testcase.assertTrue(removed, "the complete trace carries no load bearing entry to remove")
    return kept


class TestReconciliationTraceCompleteness(unittest.TestCase):
    def test_reconciliation_trace_complete(self):
        """Fixture: the reconciliation trace for the single RunRecord, listing every field, its source record form among the five forms the brief names (ARB, BOO, PAM, RFO, RET), and its place in the single record; the basis is the AC-14 statement in brief section 10, and no inventory fixture is assigned to this group in the mapping.
        Pins: no field any of the five treats as load bearing is dropped, per AC-14, and every field in the trace names its source form and its place in the single record.
        Bar: the mapping states no bar on a complete trace checked in the form this group requires.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.5; with the surface present, a trace dropping a load bearing field, or leaving a field with no source form or no place, fails.
        """
        behaviour = "reconciliation trace lists every field with its source form and its place, dropping no load bearing field, per AC-14"
        require_surface(self, behaviour, "reconciliation_trace")
        # Expected set transcribed from the reconciliation table record
        # design/steps/step-14-f08-reconciliation-table.md, section 5,
        # with 99 rows in total: ARB 8, BOO 5, PAM 17, RFO 20, and RET 49.
        # Each row states the expected field, its source form, and its
        # place in the single RunRecord exactly as that record states
        # them.
        expected = (
            ("Arbiter accuracy value applied, stated as a labelled assumption", "ARB", "Interpretation choices group"),
            ("Assumption set identifier, for the accuracy row the run used", "ARB", "Assumption record group"),
            ("Row identifier, for the accuracy row inside its named set", "ARB", "Assumption record group"),
            ("Sensitivity range in force, for the accuracy value", "ARB", "Assumption record group"),
            ("Error direction for the accuracy value, in the symmetric split form or the directional pair form", "ARB", "Interpretation choices group, beside the accuracy value that group carries"),
            ("Dependence mark citing DQ-164, in the form: depends on Parley Q1, Q2, or Q5 as applicable, unconfirmed, pending DQ-164; the Q2 limb is not optional for accuracy results", "ARB", "Reserved matter group, dependence labels"),
            ("Mark citing DQ-163, for any run that used an anchor scenario", "ARB", "Reserved matter group, dependence labels"),
            ("Excluded adjudication class counts and shares, for each of the four excluded classes ARB defines", "ARB", "Outcome and retention group"),
            ("Anchor scenario identifier, marked under DQ-163, including the explicit empty set marker where the scenario is the empty anchor set", "BOO", "Reserved matter group, as one of the three values of the AnchorScenarioRecord"),
            ("Assumption set identifier, for the run", "BOO", "Assumption record group"),
            ("Row identifiers inside the named set, for the run, naming in particular the vouch formation, honest vouching propensity, internal vouch density, and adjudication accuracy rows in force", "BOO", "Assumption record group"),
            ("Dependence stamp: Q1 and Q2 dependence marked on the run as a whole, and Q5 dependence marked where its field 6 or field 7 answers feed suspect or freeze handling", "BOO", "Reserved matter group, dependence labels"),
            ("Core only qualifier, where escrow results are reported alongside", "BOO", "Variant stamp group"),
            ("Run identifier", "PAM", "Identity and design group"),
            ("Sweep identifier", "PAM", "Identity and design group"),
            ("Population size", "PAM", "Identity and design group"),
            ("Run length", "PAM", "Identity and design group, as run length in days"),
            ("Root seed reference", "PAM", "Identity and design group"),
            ("Derived run seed identifier", "PAM", "Identity and design group"),
            ("Assumption set identifier (the set name, in PAM words)", "PAM", "Assumption record group"),
            ("Row identifiers, for every behaviour parameter used", "PAM", "Assumption record group"),
            ("Interpretation choice identifier, one entry per point, P-01 to P-30, with no point omitted", "PAM", "Interpretation choices group"),
            ("Reading applied, one entry per point (the reading taken, in PAM words)", "PAM", "Interpretation choices group"),
            ("Value or values used in this run, for a parameterised judgement entry", "PAM", "Assumption record group, as the value used for that behaviour parameter"),
            ("Sensitivity range, for a parameterised judgement entry", "PAM", "Assumption record group, as the sensitivity range fixed before runs for that behaviour parameter"),
            ("Dependence field, present for every entry: the dependence statement in PAM stated words for an entry resting on a Q1, Q2, or Q5 confirmation, or the statement that no such dependence applies to that entry", "PAM", "Reserved matter group, dependence labels"),
            ("Pause cap value in force, for this variant", "PAM", "Variant stamp group, as the pause value in force, stated as extension and total"),
            ("Escrow variant", "PAM", "Variant stamp group"),
            ("Rule version set, carrying the ruling fold version element PAM names", "PAM", "Variant stamp group"),
            ("Parley test total source used, where a total is cited, naming the 120 count or the 122 count, or stating that no test total is cited", "PAM", "Log entry inside the run record"),
            ("Value or swept range, for every assumed parameter the result depends on", "RFO", "Assumption record group, as the value used for that behaviour parameter"),
            ("Sensitivity range, for every assumed parameter the result depends on", "RFO", "Assumption record group"),
            ("Provenance label (the assumption label, in RFO words), for every assumed parameter", "RFO", "Assumption record group, as the provenance label for that behaviour parameter"),
            ("Assumption set identifier", "RFO", "Assumption record group"),
            ("Row identifiers, for every entry in its assumption record", "RFO", "Assumption record group"),
            ("Interpretation choice identifier, for every choice the result rests on", "RFO", "Interpretation choices group"),
            ("Reading applied, for every choice the result rests on, stated as a choice and not as a fact of the source text", "RFO", "Interpretation choices group"),
            ("Arbiter accuracy value, where behavioural adjudication is involved, as a labelled assumption", "RFO", "Interpretation choices group"),
            ("Escrow variant named in the variant stamp, B-4 or B-3, and both variants named for a difference result", "RFO", "Variant stamp group, as the escrow variant"),
            ("Pause cap value in force, for that variant, wherever a pause related value appears", "RFO", "Variant stamp group, as the pause value in force, stated as extension and total"),
            ("Core only qualifier, where the result concerns the escrow", "RFO", "Variant stamp group"),
            ("Dependence marking citing DQ-164, where any part of the result depends on Parley Q1, Q2, or Q5", "RFO", "Reserved matter group, dependence labels"),
            ("Anchor scenario marking, where the result uses anchor material: scenario only, marked citing DQ-163, with no favoured point", "RFO", "Reserved matter group, dependence labels, with the scenario values in the same group"),
            ("Calibration claim field, whose only permitted value reads: no calibration claim, self consistency only", "RFO", "Joined done test group"),
            ("Sweep family identifier", "RFO", "Identity and design group, as sweep family identifier"),
            ("Root seed reference (the root seed, in RFO words)", "RFO", "Identity and design group"),
            ("Sweep identifier", "RFO", "Identity and design group"),
            ("Population size", "RFO", "Identity and design group"),
            ("Run length", "RFO", "Identity and design group, as run length in days"),
            ("Rule version set", "RFO", "Variant stamp group"),
            ("Sweep identifier", "RET", "Identity and design group"),
            ("Sweep family identifier", "RET", "Identity and design group"),
            ("Run identifier", "RET", "Identity and design group"),
            ("Sweep point identifier", "RET", "Identity and design group"),
            ("Run class, one of screening, confirmation, headline, or validation", "RET", "Identity and design group"),
            ("Design kind", "RET", "Identity and design group"),
            ("Replicate group identifier", "RET", "Identity and design group"),
            ("Replicate index within its group", "RET", "Identity and design group"),
            ("Population size", "RET", "Identity and design group"),
            ("Run length in days", "RET", "Identity and design group"),
            ("Horizon variant marker", "RET", "Identity and design group"),
            ("Control values", "RET", "Identity and design group"),
            ("Root seed reference", "RET", "Identity and design group"),
            ("Derived run seed identifier", "RET", "Identity and design group"),
            ("Separate stream identifiers, for each purpose stream the run used", "RET", "Identity and design group"),
            ("Assumption set identifier", "RET", "Assumption record group"),
            ("Row identifier inside its named set, for every behaviour parameter the run used", "RET", "Assumption record group"),
            ("Value used, for every behaviour parameter the run used", "RET", "Assumption record group"),
            ("Sensitivity range as fixed before runs, for every behaviour parameter the run used", "RET", "Assumption record group"),
            ("Provenance label, reading labelled assumption for every unfitted parameter", "RET", "Assumption record group"),
            ("Escrow variant", "RET", "Variant stamp group"),
            ("Matched run identifier, of the counterpart run in the other variant", "RET", "Variant stamp group"),
            ("Pause cap value in force, for this variant, stated as extension and total", "RET", "Variant stamp group, as the pause value in force"),
            ("Rule version set: Parley amendment level applied, escrow folding version, and Vigil likelihood ratio table version", "RET", "Variant stamp group"),
            ("Core only qualifier, a boolean field that must read true for every escrow bearing result", "RET", "Variant stamp group"),
            ("Interpretation choice identifier, for every interpretation choice that applies to this run", "RET", "Interpretation choices group"),
            ("Reading applied, for every interpretation choice that applies to this run", "RET", "Interpretation choices group"),
            ("Parameter reference, where the choice enters as a labelled assumption (the parameter or rule point affected, in Form 4 words)", "RET", "Interpretation choices group"),
            ("Arbiter accuracy value and its row reference, carried explicitly in this group", "RET", "Interpretation choices group"),
            ("Dependence label listing DQ-164, wherever the run depends on Parley Q1, Q2, or Q5", "RET", "Reserved matter group, dependence labels"),
            ("Dependence entry recording, for any anchor scenario run, the mark citing DQ-163", "RET", "Reserved matter group, dependence labels"),
            ("Correlation statement, or the joint design reference where correlated parameters were swept jointly", "RET", "Reserved matter group"),
            ("Scenario identifier, for an anchor scenario run, one of three values and no fourth", "RET", "Reserved matter group"),
            ("Anchor set description, as a scenario setting, one of three values and no fourth", "RET", "Reserved matter group"),
            ("Mark citing DQ-163, for an anchor scenario run, one of three values and no fourth", "RET", "Reserved matter group"),
            ("Joint outcome vector, as end of run values", "RET", "Outcome and retention group"),
            ("Regime classification", "RET", "Outcome and retention group"),
            ("Winning criterion evaluation, as three stored values", "RET", "Outcome and retention group"),
            ("Retention tier reached", "RET", "Outcome and retention group"),
            ("List of flag conditions that fired, by condition number, or an empty list", "RET", "Outcome and retention group"),
            ("Pointers to the daily aggregates, to snapshots where retained, to the event log where retained, and to the final checkpoint where retained", "RET", "Outcome and retention group"),
            ("End of run full state hash", "RET", "Outcome and retention group"),
            ("Store kind field", "RET", "Outcome and retention group"),
            ("Timing pilot record reference, or the provisional grid marker, as the sole either or carriage of that pair", "RET", "Joined done test group"),
            ("Folding record reference", "RET", "Joined done test group"),
            ("Seam check reference", "RET", "Joined done test group"),
            ("NQ-10 listing version, with the list of any DQ-5 to DQ-30 items the run exercises, or an explicit none value", "RET", "Joined done test group"),
            ("NQ-6 classification marker", "RET", "Joined done test group"),
            ("Calibration claim field, whose only permitted value reads: no calibration claim, self consistency only", "RET", "Joined done test group"),
        )
        self.assertEqual(len(expected), 99)
        trace = SURFACE.reconciliation_trace()
        self.assertTrue(trace)
        for entry in trace:
            self.assertIn(entry["source_form"], SOURCE_FORMS)
            self.assertTrue(entry["place_in_single_record"])
            self.assertTrue(entry["field"])
        presented = {
            (
                entry["field"],
                entry["source_form"],
                entry["place_in_single_record"],
            )
            for entry in trace
        }
        for field, source_form, place in expected:
            self.assertIn(
                (field, source_form, place),
                presented,
                "expected field missing from trace: "
                + field
                + " ("
                + source_form
                + ", "
                + place
                + ")",
            )

    def test_trace_checked_by_independent_reader(self):
        """Fixture: the reconciliation trace for the single RunRecord, with its reader check recorded, on the basis stated for the trace in this group.
        Pins: the trace stands checked by a reader who did not perform the reconciliation, in the pattern decision D-20 states for the folding duty.
        Bar: a trace checked by its own author does not satisfy this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.5; with the surface present, a trace whose only recorded check is by its author standing as satisfied fails.
        """
        behaviour = "reconciliation trace is checked by a reader who did not perform the reconciliation, per D-20"
        require_surface(self, behaviour, "reconciliation_trace_check")
        check = SURFACE.reconciliation_trace_check()
        self.assertNotEqual(check["checker"], check["reconciler"])
        self.assertTrue(check["recorded"])


class TestDroppedFieldDetection(unittest.TestCase):
    def test_dropped_load_bearing_field_fails_reader_check(self):
        """Fixture: the complete reconciliation trace with one load bearing entry removed from it, the reduced trace alone presented to the reader check, on the basis stated for the trace in this group.
        Pins: the reader check fails on a trace with a load bearing field removed, judged on the contents of the trace presented and on no separate statement about it.
        Bar: the criterion is recorded as failed on such a trace, in the form the next test in this group pins.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.5; with the surface present, a reader check passing such a trace fails.
        """
        behaviour = "reader check fails on a reconciliation trace with one load bearing field removed"
        require_surface(self, behaviour, "reconciliation_trace", "check_reconciliation_trace")
        trace = trace_with_one_load_bearing_entry_removed(self)
        self.assertFalse(SURFACE.check_reconciliation_trace(trace))

    def test_partial_reconciliation_is_not_a_pass(self):
        """Fixture: the complete reconciliation trace with one load bearing entry removed from it, the reduced trace alone presented for its criterion verdict, on the basis stated for the trace in this group.
        Pins: the criterion is recorded as failed, not as passed with a note, on a trace with a load bearing field dropped.
        Bar: partial reconciliation is not a pass form for AC-14.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.5; with the surface present, a partial trace recorded as passed, in any wording, fails.
        """
        behaviour = "partial reconciliation is recorded as failed for AC-14, never as passed with a note"
        require_surface(self, behaviour, "reconciliation_trace", "reconciliation_criterion_verdict")
        trace = trace_with_one_load_bearing_entry_removed(self)
        verdict = SURFACE.reconciliation_criterion_verdict(trace)
        self.assertEqual(verdict, "failed")


if __name__ == "__main__":
    unittest.main()
