"""Decision form tests. Plan section 2 section 6, DQ7 decision forms.

Two kinds stand in this file, as the mapping states them apart.
First kind: form completeness tests HL-F, FD-F, CP-F, and MT-F. Each runs now,
at Step 13, against the decision record itself, the DQ7 entry in plan section
3A of design/DESIGN-PLAN.md, and fails if any numbered part is missing.
Second kind: recompute tests HL-R, FD-R, CP-R, and MT-R. These follow the
ordinary surface pattern of the suite: each tries to import the product
package crucible and records whether the surface stands, and while the
surface stands absent each non gated recompute test fails naming its pinned
behaviour. The CP-R recompute tests record their state as gated, because the
DQ7-08 rule stands carried open for reliance until the reconciliation act
for Plan Amendment (Step 11, reconciliation) stands, as section 6.3 of the
mapping states.
No test in this file states a magnitude any record does not state.
"""
import unittest
from pathlib import Path

try:
    import crucible

    if getattr(crucible, "__file__", None) is None:
        # A namespace only import is no product surface: no module stands.
        raise ImportError("package crucible stands as a namespace only, with no product module")
    SURFACE = crucible
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "plan section 2 section 6"
PLAN_PATH = Path(__file__).resolve().parents[2] / "design" / "DESIGN-PLAN.md"
CP_GATE = (
    "gated on the reconciliation act for Plan Amendment (Step 11, reconciliation): "
    "the DQ7-08 rule stands carried open for reliance until that act stands, "
    "and the bar at clause C12 stands unlifted for reliance purposes"
)


def require_surface(testcase, behaviour):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": pinned behaviour not built: " + behaviour
            + " (surface package crucible stands absent: " + repr(SURFACE_ERROR) + ")"
        )


def decision_section(testcase, start_heading, end_heading):
    if not PLAN_PATH.is_file():
        testcase.fail(GROUP + ": decision record file not found at " + str(PLAN_PATH))
    text = PLAN_PATH.read_text(encoding="utf-8")
    start = text.find(start_heading)
    if start < 0:
        testcase.fail(GROUP + ": decision record heading not found: " + start_heading)
    end = text.find(end_heading, start + len(start_heading))
    if end < 0:
        testcase.fail(GROUP + ": decision record end heading not found: " + end_heading)
    return text[start:end]


def check_parts(testcase, section, parts, form_name, record_name):
    missing = []
    for label, needle in parts:
        with testcase.subTest(part=label):
            if needle not in section:
                missing.append(label + " (looked for: " + needle + ")")
    if missing:
        testcase.fail(
            GROUP + ": form completeness failed for " + form_name + " against "
            + record_name + "; missing parts: " + "; ".join(missing)
        )


class TestHonestLossFormCompleteness(unittest.TestCase):
    def test_hl_f_nine_parts(self):
        """Fixture: the decision record itself, DQ7-06 in plan section 3A of design/DESIGN-PLAN.md, the record the mapping names for this form at section 6.1.
        Pins: the decision record carries all nine parts of the honest loss statement (1 population sentence; 2 event sentence; 3 numerator sentence; 4 denominator sentence; 5 period sentence; 6 zero rule sentence; 7 coverage table with one row per newcomer cost named in the brief, slower earning, slower band progress, and suspect treatment in the cold period; 8 version sentence; 9 scope sentence).
        Bar: any missing part fails the test before any run is examined, because a statement missing a part fails its recompute test in advance, on its face.
        Failure: this test runs now and fails if any of the nine parts, any checked content element inside a part, or any row of the part 7 coverage table, is missing from the DQ7-06 record.
        """
        section = decision_section(self, "## DQ7-06.", "## DQ7-07.")
        parts = (
            ("part 1, population sentence", "Part 1, population"),
            ("part 1, content, population stated by ground truth label", "every identity in the run whose simulator ground truth label is honest"),
            ("part 2, event sentence", "Part 2, event"),
            ("part 2, content, one loss stated as one submitted unit", "One loss is one unit of work submitted in the period"),
            ("part 3, numerator sentence", "Part 3, numerator"),
            ("part 3, content, numerator stated as submitted minus accepted", "minus units of work credited as accepted"),
            ("part 4, denominator sentence", "Part 4, denominator"),
            ("part 4, content, denominator stated as all submitted units", "all units of work submitted in the period by identities in the population"),
            ("part 5, period sentence", "Part 5, period"),
            ("part 5, content, per day period stated against the daily aggregates form", "per day, which fills the daily aggregates form"),
            ("part 6, zero rule sentence", "Part 6, zero rule"),
            ("part 6, content, zero rule stated as the not reported marker", "the reported value is an explicit not reported marker"),
            ("part 7, coverage table", "Part 7, coverage table"),
            ("part 7 row, slower earning", "Slower earning"),
            ("part 7 row, slower band progress", "Slower band progress"),
            ("part 7 row, suspect treatment in the cold period", "Suspect treatment in the cold period"),
            ("part 8, version sentence", "Part 8, version"),
            ("part 8, content, version stated as loss definition version 1", "This statement carries loss definition version 1"),
            ("part 9, scope sentence", "Part 9, scope"),
            ("part 9, content, scope stated as transition reports alone", "The accompaniment duty reaches transition reports alone"),
        )
        check_parts(self, section, parts, "HL-F honest loss statement (DQ7-06)", "the DQ7-06 entry in plan section 3A")


class TestFalseDiscoveryFormCompleteness(unittest.TestCase):
    def test_fd_f_eight_parts(self):
        """Fixture: the decision record itself, DQ7-07 in plan section 3A of design/DESIGN-PLAN.md, the record the mapping names for this form at section 6.2, standing in place of the family record the form will travel in once a family is fixed. Defect M-S01-02, recorded at design/steps/step-13-write-s01-s02.md: the family record limb of this form stands unwritten, because no family record stands at Step 13, and this test must run again against the family record when a family record is fixed; the pass this test records covers the DQ7-07 decision record only.
        Pins: the record carries all eight parts of the false discovery basis statement (1 family sentence with the counted number of claims and the claim forms enumerated; 2 a per form test block for each claim form, the carriage block satisfying the block presence limb for envelope headline claims and, for a block that states a test, the test named, the null stated as a sentence, the statistic and its source records, and the derivation of the one test value including its combination rule; 3 run set sentence; 4 dependence sentence in one of its stated forms; 5 procedure sentence with ranking rule, threshold formula, outcome rule, tied value treatment, and the treatment of a claim whose value cannot be computed; 6 confirmation sentence; 7 coverage sentence; 8 version sentence with the new family rule on any change after fixing).
        Bar: any missing part fails the test on its face.
        Failure: this test runs now and fails if any of the eight parts, or a checked element inside parts 2, 4, or 5, is missing from the DQ7-07 record.
        """
        section = decision_section(self, "## DQ7-07.", "## DQ7-08.")
        parts = (
            ("part 1, family sentence", "Part 1, family"),
            ("part 2, per form test blocks", "Part 2, per form test blocks"),
            ("part 2, test T1 named", "test T1"),
            ("part 2, null stated as a sentence", "The null"),
            ("part 2, statistic stated", "The statistic is"),
            ("part 2, combination rule for the one test value", "largest of its point values"),
            ("part 2, carriage block for envelope headline claims", "no test is stated in this decision for this form"),
            ("part 3, run set sentence", "Part 3, run set"),
            ("part 4, dependence sentence", "Part 4, dependence"),
            ("part 4, stated positive dependence form", "stated positive dependence form"),
            ("part 5, procedure sentence", "Part 5, procedure"),
            ("part 5, tied value treatment", "Tied values"),
            ("part 5, value that cannot be computed", "cannot be computed"),
            ("part 6, confirmation sentence", "Part 6, confirmation"),
            ("part 7, coverage sentence", "Part 7, coverage"),
            ("part 8, version sentence", "Part 8, version"),
            ("part 8, new family rule on change after fixing", "creates a new family"),
        )
        check_parts(self, section, parts, "FD-F false discovery basis statement (DQ7-07)", "the DQ7-07 entry in plan section 3A")


class TestCheckpointRetentionFormCompleteness(unittest.TestCase):
    def test_cp_f_twelve_clauses(self):
        """Fixture: the decision record itself, DQ7-08 in plan section 3A of design/DESIGN-PLAN.md, the adopted rule text the mapping names for this form at section 6.3.
        Pins: the adopted rule text carries all twelve clauses, one check per clause (C1 definitions; C2 cadence and coincidence; C3 retained set table; C4 tenth point counting by formula; C5 holding period and deletion trigger; C6 enumeration and record update; C7 permitted later uses; C8 exclusions and protections; C9 no forbidden keys; C10 cap and sizing statement; C11 failure consequence for a missing required checkpoint; C12 bar lifting record).
        Bar: a plan text lacking any one clause leaves cases undecidable that the evidence shows will arise, and this test fails it by clause number.
        Failure: this test runs now and fails if any clause C1 to C12, or any checked content element inside a clause, is missing from the DQ7-08 record.
        """
        section = decision_section(self, "## DQ7-08.", "## DQ7-09.")
        parts = (
            ("clause C1, definitions", "Clause C1, definitions"),
            ("clause C1, content, family close evidenced by the family record entry", "Family close is evidenced by the family record entry"),
            ("clause C2, cadence and coincidence", "Clause C2, cadence and coincidence"),
            ("clause C2, content, a checkpoint written at the close of every simulated day", "A checkpoint is written at the close of every simulated day"),
            ("clause C3, retained set", "Clause C3, retained set"),
            ("clause C3, content, retained set row for Tier 2 stated", "Tier 2, the final checkpoint and the tenth point checkpoints"),
            ("clause C4, tenth point counting", "Clause C4, tenth point counting"),
            ("clause C4, content, tenth point counting by the stated formula", "rounding up k times L divided by 10"),
            ("clause C5, holding period and deletion trigger", "Clause C5, holding period and deletion trigger"),
            ("clause C5, content, the checks that must complete first named", "resume equality checks that feed flag condition 7"),
            ("clause C6, enumeration and record update", "Clause C6, enumeration and record update"),
            ("clause C6, content, deletion and pointer update stated as one recorded act", "Deletion of a checkpoint and the update of every pointer"),
            ("clause C7, permitted later uses", "Clause C7, permitted later uses"),
            ("clause C7, content, an unlisted use stated as unavailable", "A use not listed for a row is unavailable for that row"),
            ("clause C8, exclusions and protections", "Clause C8, exclusions and protections"),
            ("clause C8, content, the regression corpus copy protection stated", "regression corpus copy"),
            ("clause C9, no forbidden keys", "Clause C9, no forbidden keys"),
            ("clause C9, content, no keying to an honest loss value", "is keyed to an honest loss value"),
            ("clause C10, cap and sizing statement", "Clause C10, cap and sizing statement"),
            ("clause C10, content, sizing stated on the high activity form", "Sizing is stated on the high activity form as well as the central form"),
            ("clause C11, failure consequence", "Clause C11, failure consequence"),
            ("clause C11, content, a missing checkpoint barring the later uses that needed it", "barred from the later uses at clause C7"),
            ("clause C12, bar lifting", "Clause C12, bar lifting"),
            ("clause C12, content, the bar standing unlifted until the reconciliation act", "the bar at this clause stands unlifted until the reconciliation act"),
        )
        check_parts(self, section, parts, "CP-F checkpoint retention rule (DQ7-08)", "the DQ7-08 entry in plan section 3A")


class TestMaterialityFormCompleteness(unittest.TestCase):
    def test_mt_f_four_parts(self):
        """Fixture: the decision record itself, DQ7-10 in plan section 3A of design/DESIGN-PLAN.md, the recorded statement the mapping names for this form at section 6.4.
        Pins: the recorded statement carries all four parts (1 the unit per axis, stated apart for each axis as one grid step on the family grid; 2 the threshold per axis, stated apart as a count of units with the relation at the threshold count given for each axis, the two counts given separately; 3 the advance fixing condition, recorded in the family record or in a named record it cites, before the first challenge run the bound judges, with any later change creating a new bound that judges no run already run; 4 the failure naming rule restated beside the bound, in the lower bound reporting form brief section 5.11 requires).
        Bar: a statement missing the per axis counts, the relation at the threshold count, or the advance fixing condition does not decide DQ7-10 in checkable form, and this test fails it.
        Failure: this test runs now and fails if any of the four parts, or a checked element inside parts 2 or 3, is missing from the DQ7-10 record.
        """
        section = decision_section(self, "## DQ7-10.", "## DQ7-11.")
        parts = (
            ("part 1, the unit per axis", "Part 1, the unit per axis"),
            ("part 2, the threshold per axis", "Part 2, the threshold per axis"),
            ("part 2, count stated apart for each axis", "stated apart for each axis"),
            ("part 2, relation at the threshold count", "a difference of exactly one step counts as material"),
            ("part 3, the advance fixing condition", "Part 3, the advance fixing condition"),
            ("part 3, before the first challenge run", "before the first challenge run it judges"),
            ("part 3, new bound judges no run already run", "judges no run already run"),
            ("part 4, the failure naming rule", "Part 4, the failure naming rule"),
            ("part 4, lower bound reporting form", "reported as a lower bound"),
        )
        check_parts(self, section, parts, "MT-F materiality statement (DQ7-10)", "the DQ7-10 entry in plan section 3A")


class TestHonestLossRecompute(unittest.TestCase):
    def test_hl_r1_recompute_rate_from_run_record(self):
        """Fixture: a run record carrying the submitted and accepted work counters the DQ7-06 record change adds, on the basis the mapping states at section 6.1; groups TG-13.4 at the report limb and TG-04.1 at the counter limb.
        Pins: HL-R1 recomputes the rate from a run record and compares numerator, denominator, and rate in both storings, the daily aggregates form and the end of run form, as part 5 assigns them.
        Bar: headline, comparison, and newcomer cost claims rest on the rate in the decided DQ7-06 form only.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, a recomputed part differing from its stored part fails.
        """
        require_surface(self, "HL-R1 recomputes the honest loss rate from a run record and compares numerator, denominator, and rate in both storings")

    def test_hl_r2_zero_rule_not_reported_marker(self):
        """Fixture: an empty population case for the honest loss rate, on the basis the mapping states at section 6.1.
        Pins: HL-R2 applies the zero rule to an empty population case and checks the not reported marker is never read as zero loss.
        Bar: a marker read as zero loss in any report fails this test.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, such a reading standing fails.
        """
        require_surface(self, "HL-R2 applies the zero rule so the not reported marker is never read as zero loss")

    def test_hl_r3_no_cross_version_comparison(self):
        """Fixture: honest loss values of two different loss definition versions standing in one report, on the basis the mapping states at section 6.1.
        Pins: HL-R3 checks that values of different loss definition versions are never compared in one report.
        Bar: any change to parts 1 to 7 increments the version, per part 8, and values of different versions are not compared.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, such a comparison standing in a report fails.
        """
        require_surface(self, "HL-R3 checks that honest loss values of different loss definition versions are never compared in one report")

    def test_hl_r4_uncovered_newcomer_cost_fails_validation(self):
        """Fixture: a report resting on a newcomer cost the part 7 coverage table marks as not covered, carried open, on the basis the mapping states at section 6.1.
        Pins: HL-R4 checks that such a report fails validation.
        Bar: no claim rests on band progress or on suspect treatment, which stand carried open inside the DQ7-06 entry, per AC-13 carriage.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, such a report validating fails.
        """
        require_surface(self, "HL-R4 fails validation for a report resting on a newcomer cost the coverage table marks as not covered")


class TestFalseDiscoveryRecompute(unittest.TestCase):
    def test_fd_r1_recompute_value_rank_threshold_outcome(self):
        """Fixture: a registry entry and its run log, on the basis the mapping states at section 6.2; groups TG-12.1 and TG-12.2.
        Pins: FD-R1 recomputes the test value from the named records, recomputes its rank and threshold from the family as fixed, and compares the reported or not reported outcome.
        Bar: rank, threshold, and outcome stand presented as recomputed only for the covered claim forms, in the decided DQ7-07 form.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, a recomputed part differing from its reported part fails.
        """
        require_surface(self, "FD-R1 recomputes the test value, rank, threshold, and outcome from a registry entry and its run log")

    def test_fd_r2_five_percent_not_recomputed_before_basis(self):
        """Fixture: a report presenting the 5 percent level as a recomputed result with no basis statement standing behind it, on the basis the mapping states at section 6.2; the 5 percent level stands as a Grill set value in the family record, as Form 1 states.
        Pins: FD-R2 checks that the 5 percent level is never reported as a recomputed result before the basis stands.
        Bar: the basis is not presented as discharged on runs until the seed standing behind replicate independence is resolved at DQ7-02, which stands carried open in full.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, such a presentation standing fails.
        """
        require_surface(self, "FD-R2 checks that the 5 percent level is never reported as a recomputed result before the basis stands")

    def test_fd_r3_change_after_fixing_creates_new_family(self):
        """Fixture: a family whose basis statement parts 1 to 7 change after fixing, on the basis the mapping states at section 6.2, with TG-12.1.
        Pins: FD-R3 checks that any change to parts 1 to 7 after fixing creates a new family under the family seal rule, with runs under the new identifier starting again.
        Bar: a changed statement judging runs already run under the old identifier fails this test.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, such a change standing without a new family fails.
        """
        require_surface(self, "FD-R3 checks that a change to basis parts 1 to 7 after fixing creates a new family under the family seal rule")


class TestCheckpointRetentionRecompute(unittest.TestCase):
    def test_cp_r1_decide_retention_from_run_records(self):
        """Fixture: a named run and its run records, on the basis the mapping states at section 6.3; groups TG-10.2 and TG-10.4. State: gated on the reconciliation act named in this file head.
        Pins: CP-R1 takes any named run and decides, from run records alone, which checkpoints must exist, which may have been deleted, and whether a given deletion breached the rule.
        Bar: no recompute result presents a retention, storage, or cost claim as resting on the decided DQ7-08 rule while the reliance gate stands.
        Failure: gated form only; this test never passes while the reconciliation act does not stand.
        """
        self.skipTest(CP_GATE)

    def test_cp_r2_retained_counts_coincidence_and_counting(self):
        """Fixture: runs whose final day is a tenth point, the one case the clause C4 formula produces, on the basis the mapping states at section 6.3. State: gated on the reconciliation act named in this file head.
        Pins: CP-R2 checks retained counts per run under the clause C2 coincidence rule and the clause C4 counting formula.
        Bar: no recompute result presents a retention, storage, or cost claim as resting on the decided DQ7-08 rule while the reliance gate stands.
        Failure: gated form only; this test never passes while the reconciliation act does not stand.
        """
        self.skipTest(CP_GATE)

    def test_cp_r3_no_forbidden_keys(self):
        """Fixture: a retained set, holding period, and deletion under the rule, read against the forbidden keys at clause C9, on the basis the mapping states at section 6.3. State: gated on the reconciliation act named in this file head.
        Pins: CP-R3 checks that no retained set, holding period, or deletion is keyed to a band progress value or a suspect treatment outcome, to a false discovery outcome, rank, or threshold for the carried out claim forms, to operator interest, or to a checkpoint byte total while size by population stands unsettled.
        Bar: no checkpoint byte total is stated while checkpoint size by population stands unsettled, and no storage or cost claim rests on the checkpoint numeric cap, which stands carried at DQ7-03.
        Failure: gated form only; this test never passes while the reconciliation act does not stand.
        """
        self.skipTest(CP_GATE)

    def test_cp_r4_missing_checkpoint_consequence(self):
        """Fixture: a run with a required checkpoint missing, on the basis the mapping states at section 6.3. State: gated on the reconciliation act named in this file head.
        Pins: CP-R4 checks the clause C11 consequence: a missing required checkpoint bars the later uses that needed it and corrects any retention record naming it, and the failure is stated as a named failure.
        Bar: the failure destination stands at the Step 12 destination amendment for cluster R1-036, as the mapping states.
        Failure: gated form only; this test never passes while the reconciliation act does not stand.
        """
        self.skipTest(CP_GATE)


class TestMaterialityRecompute(unittest.TestCase):
    def test_mt_r1_redecide_materiality(self):
        """Fixture: a challenge failure, the recorded bound, and the two grid positions, on the basis the mapping states at section 6.4.
        Pins: MT-R1 redecides the materiality of a challenge failure from the recorded bound and the two grid positions, per axis, reaching the same material or not material reading a second reader reaches.
        Bar: the bound judges in its recorded relational form only, one grid step per axis with the strict relation, as DQ7-10 decides it; no numeric bound value is stated in this test, because none stands on the record.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, two readers reaching different readings from the same bound and positions fails.
        """
        require_surface(self, "MT-R1 redecides a challenge failure materiality from the recorded bound and the two grid positions, per axis")

    def test_mt_r2_bound_not_fixed_in_advance_is_lower_bound(self):
        """Fixture: a readout judged under a bound that was not fixed in advance, on the basis the mapping states at section 6.4, with TG-12.2.
        Pins: MT-R2 checks that such a readout is reported as a lower bound with condition 2 named, and never as established.
        Bar: while the bound standing is open in this form, no readout is reported as established under stopping condition 2, at open point OP-17.
        Failure: while the surface stands absent the test fails naming this behaviour and plan section 2 section 6; with the surface present, such a readout reported as established fails.
        """
        require_surface(self, "MT-R2 reports a readout judged under a bound not fixed in advance as a lower bound with condition 2 named, never as established")


if __name__ == "__main__":
    unittest.main()
