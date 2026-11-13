"""Guard tests of plan section 2 section 8. Tests that guard the carried bars.

One file for all guards, as the author paper for this cluster states. Each guard
names the act it forbids and the artefact set it scans, in its docstrings, and
each guard test prints its scan set size and its hit count, and fails on an
empty scan set, so a vacuous pass is visible as one, as section 8 requires.
Scan sets are resolved from this file location. The suite scan set is every
test file under product/tests except this guard file itself, which is excluded
because it carries the guard patterns as data. The Step 13 reporting artefact
scan set is every step-13 file under design/steps. The golden and result scan
set is every file under product outside product/tests. A guard whose scan set
consists only of Step 13 reporting artefacts stands down as a recorded skip
in a tree where the design steps directory stands absent, because its scan
object does not exist in such a tree; the same guard stands in full force
whenever that directory stands present, and a present directory with an
empty scan set still fails as a vacuous pass. A guard whose scan set also
covers product artefacts runs on those artefacts in either tree and does
not stand down. Guards run against the
artefacts as they stand and require no product surface. Several guards check
per unit inside their loci, a unit being one test function with its docstring,
or per artefact block, as their docstrings state.
"""
import re
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PRODUCT_DIR = TESTS_DIR.parent
ROOT_DIR = PRODUCT_DIR.parent
SELF_NAME = Path(__file__).name

DQ163_MARK = "DQ-163 RULED by Captain JP, defer until Parley exists"

ARTEFACT_LABELS = (
    ("readout", r"(?m)^\s*Detector facing readout:"),
    ("report form", r"(?m)^\s*Headline report form \(frozen\)"),
    ("look register", r"(?m)^\s*Look register:"),
    ("operator log", r"(?m)^\s*Operator look and choice log:"),
)


def suite_files():
    return sorted(p for p in TESTS_DIR.glob("test_*.py") if p.name != SELF_NAME)


def step13_files():
    steps = ROOT_DIR / "design" / "steps"
    if not steps.is_dir():
        return []
    return sorted(steps.glob("step-13-*.md"))


def golden_files():
    return sorted(
        p for p in PRODUCT_DIR.rglob("*")
        if p.is_file() and TESTS_DIR not in p.parents and "__pycache__" not in p.parts
    )


def read(path):
    return path.read_text(encoding="utf-8", errors="replace")


def line_hits(files, pattern, exclude_line=None):
    rx = re.compile(pattern, re.IGNORECASE)
    hits = []
    for path in files:
        for lineno, line in enumerate(read(path).splitlines(), 1):
            if rx.search(line) and (exclude_line is None or not exclude_line(line)):
                hits.append(path.name + ":" + str(lineno) + ": " + line.strip()[:120])
    return hits


def test_units(text):
    starts = [m.start() for m in re.finditer(r"(?m)^\s*def test_", text)]
    units = []
    bounds = [0] + starts + [len(text)]
    for i in range(len(bounds) - 1):
        chunk = text[bounds[i]:bounds[i + 1]]
        m = re.search(r"def (test_\w+)", chunk)
        name = m.group(1) if m else "(file head)"
        dm = re.search(r'"""(.*?)"""', chunk, re.DOTALL)
        doc = dm.group(1) if dm else ""
        units.append((name, chunk, doc))
    return units


def fixture_line_of(doc):
    for line in doc.splitlines():
        if "Fixture:" in line:
            return line
    return ""


def artefact_blocks(files):
    blocks = []
    for path in files:
        text = read(path)
        found = []
        for kind, pattern in ARTEFACT_LABELS:
            for m in re.finditer(pattern, text):
                found.append((m.start(), kind))
        found.sort()
        for i, (start, kind) in enumerate(found):
            end = found[i + 1][0] if i + 1 < len(found) else len(text)
            blocks.append((kind, path.name, text[start:end]))
    return blocks


class GuardBase(unittest.TestCase):
    def require_design_steps(self, guard_id):
        if not (ROOT_DIR / "design" / "steps").is_dir():
            print(
                "GUARD " + guard_id + " stands down: the design steps tree stands absent "
                "in this tree, so the scan object of this guard does not exist here"
            )
            self.skipTest(
                "GUARD " + guard_id + " stands down in this tree: the design steps tree "
                "stands absent, so the Step 13 reporting artefacts this guard scans do "
                "not exist in a product only tree"
            )

    def run_guard(self, guard_id, files, violations, extra=""):
        print(
            "GUARD " + guard_id + " scan set: " + str(len(files)) + " files"
            + ("; " + extra if extra else "")
            + "; violations: " + str(len(violations))
        )
        self.assertGreater(
            len(files), 0,
            "GUARD " + guard_id + ": scan set is empty, a vacuous pass is a failed guard under section 8",
        )
        self.assertEqual(
            [], violations,
            "GUARD " + guard_id + " forbids the act named in its docstring; violations: " + "; ".join(violations[:10]),
        )


class TestGuard1NoRestOnOpenItems(GuardBase):
    def test_no_rest_on_oi_1_to_oi_7(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file.
        Pins: Guard 1 of section 8. No fixture value, no test expectation, and no cited figure in the suite derives from material any of open items OI-1 to OI-7 covers. The forbidden act: a suite artefact resting on any of OI-1 to OI-7, detected here as any reference to an OI item in any fixture, expectation, or provenance position in the scan set, in any line position, with a line that states the bar or the open standing itself excluded as a standing statement and not as a rest. Recorded detection limit: a derivation that names no OI item in any position cannot be detected by a text scan; that limit stands recorded here, and discharge of an item stays in the bar form below, by full read plus fresh trace, and never by this guard.
        Bar: Discharge of an OI item is item by item, by a full read plus a fresh trace, or a ruling of out of scope, owned by the Project Manager; this guard never discharges an item.
        Failure: Fails on any OI reference in any fixture, expectation, or provenance position in the scan set outside a standing statement, and fails on an empty scan set.
        """
        files = suite_files()
        hits = line_hits(
            files, r"\bOI-[1-7]\b",
            exclude_line=lambda line: any(w in line.lower() for w in ("no ", "not ", "never", "barred", "forbids", "fails")),
        )
        self.run_guard("1, no rest on OI-1 to OI-7", files, hits)


class TestGuard2NoClaimOnUnpricedForms(GuardBase):
    def test_no_claim_on_unpriced_forms(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, read for its cost, timing, and scale expectations.
        Pins: Guard 2 of section 8, DQ7-05. The forbidden act: any compute or cost statement in a suite expectation, fixture label, or report fixture resting on the priced forms of Selector items S5-12 or S5-13 before their pricing stands recorded.
        Bar: No compute or cost claim rests on either priced form until its pricing stands recorded; a statement that needs either form states the unpriced standing instead.
        Failure: Fails on any occurrence of either item identifier in the scan set, and fails on an empty scan set.
        """
        files = suite_files()
        self.run_guard("2, no claim on unpriced forms S5-12 and S5-13", files, line_hits(files, r"\bS5-1[23]\b"))


class TestGuard3BankedItems(GuardBase):
    def test_no_real_money_stake_encoding(self):
        """
        Fixture: The scan set stated in this file header: the suite source, and every golden or result file under product outside product/tests.
        Pins: Guard 3 of section 8, first scan, AC-6. The forbidden act: any run, branch, variable, fixture, or test encoding real money stake behaviour for Parley Q3, detected here as a real money or currency stake identifier in code or fixtures. DQ-162 stands ruled: test value only.
        Bar: Parley Q3 behaviour appears in no branch, variable, fixture, or test, in any form.
        Failure: Fails on any matching identifier in the scan set, and fails on an empty scan set.
        """
        files = suite_files() + golden_files()
        hits = line_hits(files, r"real_money|realMoney|stake_currency|stake_usd|usd_stake|currency_stake")
        self.run_guard("3a, banked items, no real money stake encoding", files, hits,
                       extra="golden and result files in set: " + str(len(golden_files())))

    def test_anchor_material_only_as_scenarios(self):
        """
        Fixture: The scan set stated in this file header: the suite source and the fixture inventory as it stands in the suite files.
        Pins: Guard 3 of section 8, second scan, AC-6. The forbidden act: anchor material standing anywhere except as D-09 scenarios carrying the mark in the ruled form, DQ-163 ruled, defer until Parley exists, with no provisional anchor set; detected here as a provisional or default anchor set assignment, or a fixture resting on a provisional anchor set, and, as the positive half of the bar, by the classification check stated here. Classification: every anchor occurrence in the scan set is classified by its unit. A presentation unit, a unit whose pins state the values an AnchorScenarioRecord carries, must state the D-09 scenario form and carry the mark in its ruled form in that same unit. A unit presenting the empty anchor set case is classified as presenting no anchor material, and must state in that unit that the case sets no estate default anchor set. Every other anchor occurrence is classified as a reference, a form naming, an in place reference to a scenario presented at its presentation unit, or carriage of a closed record, and a reference line stating scenario content of its own fails this guard. The positive check is not vacuous: a suite holding no presentation unit fails this guard.
        Bar: No provisional anchor set and no estate default anchor set stands in any suite artefact.
        Failure: Fails on any matching assignment or fixture line in the scan set, on any presentation unit missing the D-09 scenario form or the ruled mark, on an empty anchor set unit missing its no default statement, on a reference line stating scenario content of its own, on a suite holding no presentation unit, and fails on an empty scan set.
        """
        files = suite_files()
        hits = line_hits(files, r"default_anchor_set\s*=|provisional_anchor_set\s*=|Fixture:[^\n]*provisional anchor")
        presentations = 0
        empty_controls = 0
        references = 0
        for path in files:
            for name, unit, doc in test_units(read(path)):
                fixture = fixture_line_of(doc)
                if "empty anchor set" in fixture.lower():
                    empty_controls += 1
                    if "no estate default anchor set" not in unit and "sets no estate default" not in unit:
                        hits.append(path.name + ": " + name + ": empty anchor set unit states no no default bar")
                    continue
                if "AnchorScenarioRecord carries" in unit:
                    presentations += 1
                    if "D-09" not in unit:
                        hits.append(path.name + ": " + name + ": anchor scenario presentation states no D-09 scenario form")
                    if DQ163_MARK not in unit:
                        hits.append(path.name + ": " + name + ": anchor scenario presentation carries no DQ-163 mark in its ruled form")
                    continue
                for line in unit.splitlines():
                    if "anchor" in line.lower():
                        references += 1
                        if re.search(r"anchor set description|scenario setting|anchor set (is|are|stands)|anchor scenario (carries|states|holds|presents)", line, re.IGNORECASE):
                            hits.append(path.name + ": " + name + ": reference line states anchor scenario content outside a presentation unit: " + line.strip()[:120])
        if presentations == 0:
            hits.append("no anchor scenario presentation unit stands in the suite, so the positive check stands unexercised")
        self.run_guard("3b, banked items, anchor material only as D-09 scenarios", files, hits,
                       extra="anchor scenario presentation units: " + str(presentations)
                       + "; empty anchor set control units: " + str(empty_controls)
                       + "; reference occurrences classified: " + str(references))

    def test_dq164_dependence_mark_not_silent(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file.
        Pins: Guard 3 of section 8, third scan, AC-6. The forbidden act: a suite artefact stating a result dependence on Parley Q1, Q2, or Q5 with no DQ-164 dependence mark in its confirmation form in the result unit itself, with a copy in the run record. The check runs per result unit, one test function with its docstring. The trigger is widened to any statement of dependence on Q1, Q2, or Q5 in any wording: a unit naming Parley Q1, Parley Q2, or Parley Q5 together with any dependence wording, depends, dependence, dependent, reliance, relies, based on, rests on, resting on, grounded on, or a use wording, stands triggered. A triggered unit passes only where that same unit carries the mark in its confirmation form, DQ-164 with the confirmation only standing stated, and states the copy in the run record in that same unit. DQ-164 stands settled as confirmation only, and the Q2 limb of the mark is not optional for accuracy results.
        Bar: Silence on the dependence mark counts as fail, in the same form as retirement checks T-08 and T-10.
        Failure: Fails on any triggered result unit missing the mark in its confirmation form inside the unit, or missing the run record copy statement inside the unit, and fails on an empty scan set.
        """
        files = suite_files()
        violations = []
        triggered = 0
        dep_words = ("depend", "reli", "based on", "rests on", "resting on", "rest on", "grounded on", "uses", "using")
        for path in files:
            for name, unit, doc in test_units(read(path)):
                if not re.search(r"Parley\s+Q\s*[125]\b", unit):
                    continue
                low = unit.lower()
                if not any(w in low for w in dep_words):
                    continue
                triggered += 1
                if "DQ-164" not in unit or "confirmation only" not in low:
                    violations.append(path.name + ": " + name + ": states a Parley Q dependence with no DQ-164 mark in its confirmation form inside the result unit")
                if not re.search(r"(copy|carried|recorded)[^\n]{0,80}run record|run record[^\n]{0,80}(copy|carried)", unit, re.IGNORECASE):
                    violations.append(path.name + ": " + name + ": states a Parley Q dependence with no run record copy stated inside the result unit")
        self.run_guard("3c, banked items, DQ-164 dependence mark", files, violations,
                       extra="triggered result units stating a Parley Q1, Q2, or Q5 dependence: " + str(triggered))


class TestGuard4AC11NonPassState(GuardBase):
    def test_ac11_never_recorded_as_pass(self):
        """
        Fixture: The scan set stated in this file header: every Step 13 reporting artefact under design/steps, the artefact set section 8 item 4 names as every Step 13 reporting artefact that carries a criterion verdict, taken as the whole standing set.
        Pins: Guard 4 of section 8. The forbidden act: any suite summary, coverage report, or criterion checklist recording AC-11, or the retention limb of any slice, as met, satisfied, or passed on the strength of a retention record that states only that the late promotion gap is declared in words, while the gap stands declared not closed.
        Bar: DECLARED NOT CLOSED is a non pass state in the brief own words; recording it as any form of pass is a suite defect, not a reporting preference.
        Failure: Fails on any scan set line recording AC-11 as passed, met, or satisfied outside a non pass wording, and fails on an empty scan set in a tree where the design steps directory stands present. Recorded state in a product only tree: stands down as a skip while that directory stands absent, because the scan object does not exist there.
        """
        self.require_design_steps("4, AC-11 non pass state")
        files = step13_files()
        hits = line_hits(
            files, r"AC-11\b[^.\n]{0,60}\b(passed|met|satisfied)\b",
            exclude_line=lambda line: "non pass" in line.lower() or "not pass" in line.lower()
            or "never" in line.lower() or "no form of pass" in line.lower(),
        )
        self.run_guard("4, AC-11 non pass state", files, hits)


class TestGuard5NoClaimOnUnadoptedSeedForm(GuardBase):
    def test_no_reportable_run_on_recommended_seed_form(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, with the Step 13 reporting artefacts.
        Pins: Guard 5 of section 8, DQ7-02, TG-02.1 restated at suite level. The forbidden act: any test result, fixture, or suite summary presenting a run on the recommended seed form as reportable, or replay wording claiming more than the unadopted recommendation supports. Detection stands widened to both word orders, the form named before the reportable wording and the reportable wording before the form, to the reportable run noun form in either order, and across a line break, inside a window of 160 characters in the file text. A match whose enclosing sentence carries a barring wording stands excluded, in the form this guard has always used, extended to the whole sentence because a barring wording governs the claim in its sentence in either order.
        Bar: A successful replay is evidence about the replayed run only, and no result is worded as evidence about agents, about a transition in the world, or about detection calibration.
        Failure: Fails on any scan set match presenting a recommended form run as reportable, in either word order or across a line break, outside a barring wording in its sentence, and fails on an empty scan set.
        """
        files = suite_files() + step13_files()
        patterns = (
            re.compile(r"recommended (seed|derivation) form.{0,160}?reportable", re.IGNORECASE | re.DOTALL),
            re.compile(r"reportable.{0,160}?recommended (seed|derivation) form", re.IGNORECASE | re.DOTALL),
        )
        barring = ("not ", "no ", "never", "barred", "barring", "bars", "fails", "forbids", "forbidden", "bar ")
        violations = []
        for path in files:
            text = read(path)
            seen = set()
            for pattern in patterns:
                for match in pattern.finditer(text):
                    back = max(text.rfind(".", 0, match.start()), text.rfind("\n", 0, match.start()))
                    ends = [i for i in (text.find(".", match.end()), text.find("\n", match.end())) if i >= 0]
                    forward = min(ends) if ends else len(text)
                    sentence = text[back + 1:forward + 1].lower()
                    if any(w in sentence for w in barring):
                        continue
                    key = (match.start(), match.end())
                    if key in seen:
                        continue
                    seen.add(key)
                    violations.append(path.name + ": " + match.group(0).replace("\n", " ")[:140])
        self.run_guard("5, no claim on the unadopted seed form", files, violations)


class TestGuard6RemainingStandingBars(GuardBase):
    def test_6a_no_affordability_wording_before_pilot(self):
        """
        Fixture: The scan set stated in this file header: every Step 13 reporting artefact under design/steps.
        Pins: Guard 6(a) of section 8. The forbidden act: affordability wording for a grid, in a reporting artefact, before the timing pilot lands, at TG-12.3.
        Bar: No affordability wording before the timing pilot lands; a statement resting on a figure is not affordability wording, and wording that states the bar itself is not the barred act.
        Failure: Fails on any scan set line asserting a grid or point as affordable, or asserting affordability as a result, outside a barring wording, and fails on an empty scan set in a tree where the design steps directory stands present. Recorded state in a product only tree: stands down as a skip while that directory stands absent, because the scan object does not exist there.
        """
        self.require_design_steps("6a, provisional grids, no affordability wording")
        files = step13_files()
        hits = line_hits(
            files, r"\b(grid|point|run)s?\b[^\n]{0,60}\baffordable\b|\baffordability (statement|result|claim) (stands|is|was) ",
            exclude_line=lambda line: any(w in line.lower() for w in ("no ", "not ", "never", "bar", "before the", "fails")),
        )
        self.run_guard("6a, provisional grids, no affordability wording", files, hits)

    def test_6b_decay_face_statements(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, restricted in the check to the files at the loci section 8 item 6(b) names, TG-04.3 and the C-18 contract tests, because the face statement duty attaches to decay arm results and aggregation comparisons at those loci and to no other mention of decay.
        Pins: Guard 6(b) of section 8. The forbidden act: a decay or aggregation artefact missing either AC-8 face statement while NQ-58 stands open, at TG-04.3: that neither decay arm tests Candidate 1 as written, and that the aggregation comparison is unspecified for Candidate 1 as written. The check stands applied per artefact inside the loci: an artefact unit is one test unit at a locus whose docstring, the Fixture and Pins statement of the test, presents a decay arm result or an aggregation comparison, and each covered unit must carry both face statements in that same unit, so one compliant unit no longer covers another unit in the same file.
        Bar: A result missing either face statement fails its group even where its numbers are correct.
        Failure: Fails on any covered artefact unit inside the loci missing either face statement, and fails on an empty scan set.
        """
        files = suite_files()
        trigger = [p for p in files if p.name in ("test_tg_04_3.py", "test_contract_c18.py")]
        violations = []
        covered = 0
        for path in trigger:
            for name, unit, doc in test_units(read(path)):
                if "decay arm result" not in doc and "aggregation comparison" not in doc:
                    continue
                covered += 1
                if "neither decay arm tests Candidate 1 as written" not in unit:
                    violations.append(path.name + ": " + name + ": artefact unit missing decay arm face statement")
                if "aggregation comparison is unspecified for Candidate 1 as written" not in unit:
                    violations.append(path.name + ": " + name + ": artefact unit missing aggregation comparison face statement")
        self.run_guard("6b, decay face statements", files, violations,
                       extra="triggered locus files, TG-04.3 and the C-18 contract tests: " + str(len(trigger))
                       + "; covered artefact units inside the loci: " + str(covered))

    def test_6c_computed_not_settled(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, restricted in the check to the file at the locus section 8 item 6(c) names, TG-06.3, because the settled wording bar attaches to seam effect reporting at that locus; the same words standing as a Shape 9 lien value at another locus, or inside a rejection assertion, are not the barred act.
        Pins: Guard 6(c) of section 8. The forbidden act: settled wording for any seam effect while NQ-45 stands open, at TG-06.3; detected here as a line in the locus file carrying the settled in the chosen escrow wording without its negated ruled form.
        Bar: Every seam effect reports as computed in Parley and not settled in the chosen escrow while NQ-45 stands open.
        Failure: Fails on any locus file line carrying the settled wording outside its negated ruled form, and fails on an empty scan set.
        """
        files = suite_files()
        locus = [p for p in files if p.name == "test_tg_06_3.py"]
        hits = line_hits(locus, r"settled in the chosen escrow",
                         exclude_line=lambda line: "not settled in the chosen escrow" in line)
        self.run_guard("6c, computed not settled", files, hits,
                       extra="triggered locus files, TG-06.3: " + str(len(locus)))

    def test_6d_core_only_qualifier(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, checked per result unit across the whole suite.
        Pins: Guard 6(d) of section 8. The forbidden act: an escrow result without the core only qualifier, at TG-05.1. The check stands applied per result: a result unit is one test unit stating an escrow bearing result or an escrow result, and each such unit must carry the core only qualifier wording in that same unit, so one qualified unit no longer covers another result in the same file.
        Bar: Silence on the qualifier check counts as fail, never as not applicable.
        Failure: Fails on any result unit stating an escrow result with no core only qualifier wording in that unit, and fails on an empty scan set.
        """
        files = suite_files()
        violations = []
        covered = 0
        for path in files:
            for name, unit, doc in test_units(read(path)):
                if not re.search(r"escrow bearing result|escrow result", unit, re.IGNORECASE):
                    continue
                covered += 1
                if "core only" not in unit:
                    violations.append(path.name + ": " + name + ": result unit carries an escrow result with no core only qualifier wording in the unit")
        self.run_guard("6d, core only qualifier", files, violations,
                       extra="covered result units carrying an escrow result: " + str(covered))

    def test_6e_no_calibration_claim(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, with the Step 13 reporting artefact set.
        Pins: Guard 6(e) of section 8. The forbidden act: a detection figure worded as calibration in any artefact, at TG-07.2, detected here in code level assignment forms and in prose claim forms over both scan sets: the claim phrase stated of a record or a figure, a calibrated figure, result, readout, or score wording, and a figure, result, readout, or score worded, presented, reported, shown, or given as calibration. Barring wording stands excluded in the form Guards 4, 5, and 6(a) use. The calibration claim field name itself is not the act: that field carries its sole permitted value, the no claim value, so a line naming the field in that standing is not a claim.
        Bar: No record may carry a calibration claim in any form, under decision D-13; self consistency wording only.
        Failure: Fails on any matching assignment or prose claim wording in either scan set outside a barring wording, and fails on an empty scan set.
        """
        files = suite_files() + step13_files()
        patterns = (
            r"calibration_claim\s*=\s*True|is_calibrated\s*=\s*True|claim_calibration\(",
            r"\bcalibration claim\b(?!\s+field)",
            r"\bcalibrated\b[^\n]{0,30}\b(figure|result|readout|score)\b|\b(figure|result|readout|score)\b[^\n]{0,40}\bcalibrated\b",
            r"\b(figures?|results?|readouts?|scores?)\b[^\n]{0,40}\b(worded as|presented as|reported as|shown as|given as)\b[^\n]{0,20}\bcalibration\b",
            r"\bfigures?\b[^\n]{0,20}\bas calibration\b",
        )
        violations = []
        for path in files:
            for lineno, line in enumerate(read(path).splitlines(), 1):
                low = line.lower()
                if any(w in low for w in ("no ", "not ", "never", "bar", "fail", "forbid", "guard", "without")):
                    continue
                if any(re.search(p, line, re.IGNORECASE) for p in patterns):
                    violations.append(path.name + ":" + str(lineno) + ": " + line.strip()[:140])
        self.run_guard("6e, no calibration claim", files, violations,
                       extra="reporting artefacts in set: " + str(len(step13_files())))

    def test_6f_no_claim_on_superseded_pilot_clause(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file.
        Pins: Guard 6(f) of section 8. The forbidden act: a scale, cost, or D-05 compliance claim resting on the superseded pilot clause in any wording; the scale change form stands decided at DQ7-13 as Form T1. Detection stands restated over the substance of the superseded clause, the flagged clause of Trade 1, in its quoted forms and in the claim forms resting on it: the literal pilot clause naming; the costing response classification, a scale change taken on the pilot record stated as a costing response under the trade; the compliance classification, a scale change stated as no breach of the D-05 ruling, or not a breach of it; the pilot evidence form, a scale change resting on, taken on, or taking effect on pilot record or pilot evidence, in either word order; and the quoted clause opener, if the pilot separates the regimes. The superseding sentence at DQ7-13 part 1, a scale change is a new ruling and not a costing response, and no scale change takes effect on pilot evidence except through that ruling, states the standing form and stands excluded by its barring wording, as any line stating the bar stands excluded.
        Bar: No test rests a scale, cost, or D-05 compliance claim on the superseded pilot clause.
        Failure: Fails on any occurrence of the clause substance, in any of the stated forms, standing as a claim basis in the scan set outside a barring wording, and fails on an empty scan set.
        """
        files = suite_files()
        claim_excl = ("no ", "not ", "never", "bar", "fail", "forbid", "supersed")
        pairs = (
            (r"pilot clause", claim_excl),
            (r"costing response", claim_excl),
            (r"scale change.{0,80}pilot (record|evidence)|pilot (record|evidence).{0,80}scale change",
             claim_excl + ("except through", "new ruling", "until")),
            (r"if the pilot separates the regimes", ("bar", "supersed", "flagged", "quoted")),
            (r"not a breach of the D-05|no breach of the D-05",
             ("barred", "barring", "supersed", "flagged", "may rest", "may not rest", "must not rest", "fails", "forbid")),
        )
        violations = []
        for pattern, excl in pairs:
            violations += line_hits(
                files, pattern,
                exclude_line=lambda line, e=excl: any(w in line.lower() for w in e),
            )
        self.run_guard("6f, Trade 1 scale change form, no claim on the superseded pilot clause",
                       files, violations)

    def test_6g_contested_entries_both_standings(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, restricted in the check to the files at the loci section 8 item 6(g) names, TG-05.2 and TG-08.2, because a contested entry named as a bar reason at another locus, as entry C-5 stands at TG-04.3, is not a fixture touching a contested entry, and the bare identifiers C-1 to C-12 also name consistency operations.
        Pins: Guard 6(g) of section 8. The forbidden act: a test resting on choosing one standing of any contested entry; where a fixture touches a contested entry, both standings travel with it, at TG-05.2 and TG-08.2, in the carriage wording the mapping states at those loci, travel beside or both standings. The check stands applied per fixture inside the loci: a covered fixture unit is one test unit at a locus whose docstring names an inventory fixture and a contested entry C-1 to C-12, and each covered unit must carry its carriage wording, travel beside, travels beside, travel with, both standings, or carried beside, in that same unit, so one carried fixture no longer covers another fixture in the same file.
        Bar: No test rests on choosing one standing of any contested entry C-1 to C-12.
        Failure: Fails on any covered fixture unit inside the loci carrying no carriage wording for the standings in that unit, and fails on an empty scan set.
        """
        files = suite_files()
        trigger = [p for p in files if p.name in ("test_tg_05_2.py", "test_tg_08_2.py")]
        carriage = ("both standings", "travel beside", "travels beside", "travel with", "carried beside", "carries beside")
        violations = []
        covered = 0
        for path in trigger:
            for name, unit, doc in test_units(read(path)):
                if not re.search(r"\bF-\d+\b", doc):
                    continue
                if not re.search(r"\bC-(?:[1-9]|1[0-2])\b", doc):
                    continue
                covered += 1
                if not any(phrase in unit for phrase in carriage):
                    violations.append(path.name + ": " + name + ": fixture unit touches a contested entry with no standings carriage wording in the unit")
        self.run_guard("6g, contested entries", files, violations,
                       extra="triggered locus files, TG-05.2 and TG-08.2: " + str(len(trigger))
                       + "; covered fixture units inside the loci: " + str(covered))

    def test_6h_unclassified_parameters_marked(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file, restricted in the check to files using an unclassified parameter standing.
        Pins: Guard 6(h) of section 8. The forbidden act: a run using a parameter placed in no kind presented as headline reportable before that parameter standing is recorded, at open point OP-14; suite fixtures mark every such parameter with its standing.
        Bar: A file using the unclassified standing with no headline bar wording fails this guard.
        Failure: Fails on any triggered file with no not headline reportable wording, and fails on an empty scan set.
        """
        files = suite_files()
        trigger = [p for p in files if "unclassified" in read(p)]
        violations = [p.name + ": uses the unclassified standing with no headline bar wording"
                      for p in trigger if "not headline reportable" not in read(p)]
        self.run_guard("6h, unclassified parameters", files, violations,
                       extra="triggered files using the unclassified standing: " + str(len(trigger)))

    def test_6i_no_invented_magnitudes(self):
        """
        Fixture: The scan set stated in this file header: every test file in the suite except this guard file.
        Pins: Guard 6(i) of section 8. The forbidden act: a hostile family magnitude, a family grid value, or a battery or sample size entering a suite artefact as a stated value from anywhere except its fixing record, at TG-09.5, TG-02.3, and TG-10.4; detected here as a size or magnitude stated as a plain assigned value in code.
        Bar: Magnitudes and sizes enter only from their fixing records; a fixture whose magnitudes stand open pins the label and the bar, not an invented magnitude.
        Failure: Fails on any matching assigned value in the scan set, and fails on an empty scan set.
        """
        files = suite_files()
        hits = line_hits(files, r"(hostile_magnitude|battery_size|sample_size|grid_step_value)\s*=\s*\d")
        self.run_guard("6i, no invented magnitudes", files, hits)


class TestGuard7OperatorFacingBars(GuardBase):
    def test_7a_knowledge_degree_on_detector_readouts(self):
        """
        Fixture: The scan set stated in this file header: every Step 13 reporting artefact and every test file in the suite, searched for a detector facing readout standing as an artefact, identified by a readout field label line.
        Pins: Guard 7(a) of section 8, one guard for three operator facing bars. The forbidden act: a detector facing readout presented as a result that states no degree of scorer knowledge the attacker held, as Act A-19 states. The check stands restated at artefact level: an artefact is the block of one readout, from its label line to the next artefact label in its file or to the end of its file, and each readout block must state its knowledge degree inside that block, in degree, extent, or held wording tied to knowledge, so a knowledge word elsewhere in a file no longer covers a readout. Recorded duty, in the cure form for this guard: when the first artefact of this kind stands, restate the check at artefact level in the full bar form before any result is cited for that kind; the block level degree check above is that restatement for the degree limb, and it stands unexercised while no readout artefact stands.
        Bar: A readout that states no degree of scorer knowledge the attacker held is not reportable, and a suite record, report, or readout set presenting such a readout as a result fails this guard.
        Failure: Fails on any readout artefact block in the scan set stating no knowledge degree inside the block, and fails on an empty scan set. The artefact count inside the scan set stands in the printed scan line.
        """
        files = step13_files() + suite_files()
        blocks = [b for b in artefact_blocks(files) if b[0] == "readout"]
        violations = []
        for kind, fname, block in blocks:
            if not re.search(r"(degree|extent) of[^\n]{0,60}knowledge|knowledge[^\n]{0,60}(degree|held)", block, re.IGNORECASE):
                violations.append(fname + ": readout artefact block states no degree of scorer knowledge inside the block")
        self.run_guard("7a, knowledge degree", files, violations,
                       extra="detector facing readout artefacts in set: " + str(len(blocks)))

    def test_7b_misreading_stage_before_form_freezes(self):
        """
        Fixture: The scan set stated in this file header: every Step 13 reporting artefact and every test file in the suite, searched for a headline report form standing at its freezing, identified by a report form field label line.
        Pins: Guard 7(b) of section 8. The forbidden act: a headline report form frozen with no misreading red team stage record in the family record for that family, or frozen over a display whose stated reading by a stage reader diverged from the recorded claim, with no redesign before the freezing and no explicit guard sentence on the display naming the divergence, as Act A-12 states. The check stands restated at artefact level in two limbs: an artefact is the block of one frozen form, from its label line to the next artefact label in its file or to the end of its file, and each block must carry its misreading stage record wording, misreading with stage or red team wording, inside that block, so a misreading word elsewhere in a file no longer covers a form; and a block stating a divergence must carry redesign wording or a guard sentence naming inside that block. Recorded duty, in the cure form for this guard: when the first artefact of this kind stands, restate the check at artefact level in the full bar form before any result is cited for that kind; the family record limb of the full bar form, reading the family record for the family the form belongs to, stands as that recorded duty beside this guard, because no artefact of this kind yet stands and no stated form names the family record locus on an artefact, and the block level limbs above stand unexercised while no frozen form artefact stands.
        Bar: A report form frozen with no misreading stage record fails this guard.
        Failure: Fails on any frozen report form artefact block in the scan set carrying no misreading stage record wording inside the block, or stating a divergence with no redesign wording and no guard sentence inside the block, and fails on an empty scan set. The artefact count inside the scan set stands in the printed scan line.
        """
        files = step13_files() + suite_files()
        blocks = [b for b in artefact_blocks(files) if b[0] == "report form"]
        violations = []
        for kind, fname, block in blocks:
            if not (re.search(r"misreading", block, re.IGNORECASE) and re.search(r"stage|red team", block, re.IGNORECASE)):
                violations.append(fname + ": report form artefact block carries no misreading stage record wording inside the block")
            if re.search(r"diverg", block, re.IGNORECASE) and not re.search(r"redesign|guard sentence", block, re.IGNORECASE):
                violations.append(fname + ": report form artefact block states a divergence with no redesign wording and no guard sentence inside the block")
        self.run_guard("7b, misreading stage before a form freezes", files, violations,
                       extra="frozen headline report form artefacts in set: " + str(len(blocks)))

    def test_7c_dual_entry_of_one_interim_read(self):
        """
        Fixture: The scan set stated in this file header: every Step 13 reporting artefact and every test file in the suite, searched for the two named artefact kinds, a look register under Amendment G1-C19 and an operator look and choice log under Act A-12, identified by artefact label lines.
        Pins: Guard 7(c) of section 8. The forbidden act: an interim read standing in one of the two artefacts and not in the other, as Amendment S12-011 states, and a Form 31 load count taken over one artefact only. The load count limb stands checked here in scan form: a line in the scan set stating a Form 31 load count over one artefact only, outside a barring wording, fails this guard. Recorded duty, in the cure form for this guard: when the first artefact of either kind stands, restate the check at artefact level in the full bar form before any result is cited for that kind; the per read limb of the full bar form, one interim read matched between the two artefacts read together, stands as that recorded duty beside this guard, because interim reads carry no identifier form on the current record, so a per read match cannot be restated without inventing an identifier form, and the kind level and load count checks above stand unexercised over artefacts while no artefact of either kind stands.
        Bar: An interim read standing in one artefact and not in the other fails this guard, and a load count taken over one artefact only fails this guard.
        Failure: Fails where exactly one of the two artefact kinds stands in the scan set, fails on any scan set line stating a Form 31 load count over one artefact only outside a barring wording, and fails on an empty scan set. Both artefact counts stand in the printed scan line.
        """
        files = step13_files() + suite_files()
        blocks = artefact_blocks(files)
        look = [b for b in blocks if b[0] == "look register"]
        oplog = [b for b in blocks if b[0] == "operator log"]
        violations = []
        if bool(look) != bool(oplog):
            violations.append("exactly one of the two interim read artefact kinds stands in the scan set")
        violations += line_hits(
            files, r"Form 31[^\n]{0,80}load count[^\n]{0,80}(one artefact only|look register only|operator look and choice log only)",
            exclude_line=lambda line: any(w in line.lower() for w in ("fails", "bar", "no ", "not ")),
        )
        self.run_guard("7c, dual entry of one interim read", files, violations,
                       extra="look register artefacts: " + str(len(look))
                       + "; operator look and choice log artefacts: " + str(len(oplog)))


if __name__ == "__main__":
    unittest.main()
