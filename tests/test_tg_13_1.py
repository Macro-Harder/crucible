"""Test group TG-13.1. The retirement test, run by the checker the brief names.
Slice S-13, Reporter and family registry, MOD-11. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod11, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod11 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod11 absent, pinned behaviour unmet: " + behaviour)


class TestTG131(unittest.TestCase):
    def test_f01_fails_in_full(self):
        """
        Fixture: F-01, the centre only headline unit W-CENTRE-ONLY.
        Pins: A checker built from this fixture runs all fifteen retirement checks T-01 to T-15 with the centre quarantine rule, in the version of the report format paper pinned in the family record before runs, and records exactly the brief verdict for F-01 in full: 3 checks passed, 9 checks failed, 3 checks not applicable of 15 checks, plus the centre quarantine breach, with the nine named fails at T-02, T-03, T-04, T-05, T-06, T-07, T-08, T-10, and T-11.
        Bar: A checker that runs only the checks named in a summary of the example fails this group; the full fifteen stand or the checker does not. The F-01 verdict stands in full and is never merged with the F-02 tally.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.1 and this behaviour; a checker recording any other tally for F-01, or omitting the centre quarantine breach, fails this test when the surface stands.
        """
        require_surface(self, "TG-13.1", "F-01 retirement verdict in full, 3 passed, 9 failed, 3 not applicable of 15, plus the centre quarantine breach")
        m = _surface_module
        verdicts = m.retirement_verdicts("F-01")
        self.assertEqual(tuple(sorted(verdicts)), tuple(sorted(m.RETIREMENT_CHECKS)))
        self.assertEqual(len(verdicts), 15)
        tally = m.retirement_tally("F-01")
        self.assertEqual(tally["passed"], 3)
        self.assertEqual(tally["failed"], 9)
        self.assertEqual(tally["not_applicable"], 3)
        self.assertEqual(tally["total"], 15)
        self.assertEqual(
            tally["failed_checks"],
            ["T-02", "T-03", "T-04", "T-05", "T-06", "T-07",
             "T-08", "T-10", "T-11"])
        self.assertTrue(tally["centre_quarantine_breach"])

    def test_f02_tally_kept_apart(self):
        """
        Fixture: F-02, worked example EX-01.
        Pins: The checker records the EX-01 tally as its own, as a tally only: 8 passed, 5 not applicable, 2 failed, the fails at T-04 and T-06, and never merges it with the F-01 tally.
        Bar: EX-01 carries no passing verdict into the brief, and a unit modelled on it is not published on its strength. No test may merge the two tallies, and no test may promote any other fixture to a verdict the brief does not give.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.1 and this behaviour; a record merging the two tallies, or promoting EX-01 to a passing verdict, fails this test when the surface stands.
        """
        require_surface(self, "TG-13.1", "F-02 tally kept apart as a tally only, 8 passed, 5 not applicable, 2 failed at T-04 and T-06")
        m = _surface_module
        tally = m.retirement_tally("EX-01")
        self.assertEqual(tally["passed"], 8)
        self.assertEqual(tally["not_applicable"], 5)
        self.assertEqual(tally["failed"], 2)
        self.assertEqual(tally["failed_checks"], ["T-04", "T-06"])
        self.assertNotIn("centre_quarantine_breach", tally)
        f01 = m.retirement_tally("F-01")
        self.assertEqual(f01["failed"], 9)
        self.assertNotEqual(tally["failed_checks"], f01["failed_checks"])

    def test_publication_record_per_unit(self):
        """
        Fixture: One real headline unit with its publication record.
        Pins: Each unit carries a publication record naming the retirement test run that covered it, the version that run used, the verdict on each check, and every failure that run recorded, per AC-4.
        Bar: A unit covered by no recorded test run, or by a run with an unrecorded failure, is not published; a suite that publishes first and records later fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.1 and this behaviour; a unit published with no publication record, or with an unrecorded failure, fails this test when the surface stands.
        """
        require_surface(self, "TG-13.1", "publication record per headline unit naming the covering run, its version, each check verdict, and every recorded failure")
        m = _surface_module
        verdicts = m.retirement_verdicts("F-01")
        failures = [c for c in m.RETIREMENT_CHECKS if verdicts[c] == "failed"]
        record = {
            "test_run": "retirement run 1",
            "version": "report format paper version pinned in the family record",
            "verdicts": verdicts,
            "failures_recorded": failures,
        }
        self.assertTrue(m.validate_publication_record(record))
        self.assertTrue(m.unit_is_publishable({"publication_record": record}))
        unrecorded = dict(record, failures_recorded=failures[:-1])
        self.assertFalse(m.validate_publication_record(unrecorded))
        self.assertFalse(m.unit_is_publishable(
            {"publication_record": unrecorded}))
        self.assertFalse(m.unit_is_publishable({}))

    def test_registry_and_registrar_duty(self):
        """
        Fixture: One SweepFamilyRegistry entry for a family, with its run log, inspected before runs and after runs.
        Pins: The Reporter, as family registrar, judges the registry fields by phase, the before runs fields for lateness and the after runs fields for completeness, and the entry stands compared against the run log by a checker who did not compile the registry, in the form plan section 3, Form 22, states for the registry.
        Restatement, recorded under the Step 14 re-run Manager ruling on TA-56: the comparison stands stated only where a run log stands among the inputs of the judging act. An entry judged with no run log among its inputs states no comparison, and an entry judged with a run log in hand states the comparison, as the two limbs below pin. The earlier form of this pin, which asserted the comparison on a call carrying no run log, stands restated by that ruling, and the restatement stands recorded in the closing cure paper of the re-run.
        Bar: A registry entry compiled and checked by the same person fails this group, and an entry whose fields stand unjudged in either phase fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.1 and this behaviour; an entry checked by its compiler, or unjudged in either phase, fails this test when the surface stands.
        """
        require_surface(self, "TG-13.1", "registry fields judged by phase and compared against the run log by a checker who did not compile the registry")
        m = _surface_module
        entry = {"phase_judgements": {"before_runs": "judged",
                                      "after_runs": "judged"}}
        judged = m.judge_registry_entry(
            entry, compiler="registrar",
            checker="independent checker",
            run_log={"runs": ["retirement run 1"]})
        self.assertEqual(judged["before_runs_judged_for"], "lateness")
        self.assertEqual(judged["after_runs_judged_for"], "completeness")
        self.assertTrue(judged["compared_against_run_log"])
        no_log = m.judge_registry_entry(entry, compiler="registrar",
                                        checker="independent checker")
        self.assertFalse(no_log["compared_against_run_log"])
        self.assertTrue(m.validate_registry_entry(
            entry, compiler="registrar", checker="independent checker",
            run_log={"runs": ["retirement run 1"]}))
        self.assertFalse(m.validate_registry_entry(
            entry, compiler="registrar", checker="registrar",
            run_log={"runs": ["retirement run 1"]}))
        unjudged = {"phase_judgements": {"before_runs": "judged"}}
        self.assertFalse(m.validate_registry_entry(
            unjudged, compiler="registrar", checker="independent checker",
            run_log={"runs": ["retirement run 1"]}))


if __name__ == "__main__":
    unittest.main()
