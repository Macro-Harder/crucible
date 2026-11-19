# Step 15 rerun, fix wave 15, Builder 7 pins.
# Rows R15-054 to R15-059 and R15-094: the MOD-07 and MOD-12
# joint run, dependency, choice pair, family, and sample forms.
# Every pin states the standing its register row charges, with
# the proving acts the source papers used.
import unittest

import crucible.mod07 as mod07
import crucible.mod12 as mod12


def family(**changes):
    record = mod12.make_family_record()
    record.update(changes)
    return record


def valid_run(effects=None):
    return {
        "adapter_choices": [],
        "tracer_passage_records": mod07.tracer_passage_records("r1"),
        "positive_control": mod07.positive_control_record(),
        "cross_seam_effects": [] if effects is None else effects,
    }


def sample_n(first, second):
    runs = [{"run_class": "screening", "run_id": first},
            {"run_class": "screening", "run_id": second}]
    return mod12.sample_statement(runs)


class TestR15054SampleKindSeparation(unittest.TestCase):
    def test_print_alike_across_types_count_two(self):
        for first, second in (
                (1.0, "1.0"), (True, "True"),
                (["run1"], "['run1']"),
                (("run1",), "('run1',)"),
                ({"run1"}, "{'run1'}"),
                ({"a": 1}, "{'a': 1}")):
            result = sample_n(first, second)
            self.assertEqual(result["n"], 2, (repr(first), repr(second)))
            self.assertEqual(
                result["runs_completed_by_class"]["screening"], 2)

    def test_conflated_across_kinds_count_two(self):
        for first, second in ((1, True), (2, 2.0), ([1], [True])):
            result = sample_n(first, second)
            self.assertEqual(result["n"], 2, (repr(first), repr(second)))

    def test_cured_controls_hold(self):
        self.assertEqual(sample_n("r1", "r2")["n"], 2)
        self.assertEqual(sample_n(b"r1", "r1")["n"], 1)
        self.assertEqual(sample_n(1, "1")["n"], 1)
        self.assertEqual(sample_n(["1"], "1")["n"], 2)
        one = {"run_class": "screening", "run_id": "r1"}
        self.assertEqual(mod12.sample_statement([one, dict(one)])["n"], 1)


class TestR15055ChoicePairCycleGuard(unittest.TestCase):
    def _pair(self, field, value_log, value_run):
        base = mod07.make_adapter_choice(
            "c1", "reading", "point", "v1", "fold")
        log_entry = mod07.interpretation_log_entry(base)
        run_entry = mod07.run_record_entry(base)
        log_entry[field] = value_log
        run_entry[field] = value_run
        return log_entry, run_entry

    def test_cyclic_text_field_returns_verdict_not_recursion(self):
        first = []
        first.append(first)
        second = []
        second.append(second)
        log_entry, run_entry = self._pair(
            "choice_identifier", first, second)
        self.assertFalse(mod07.validate_choice_pair(log_entry, run_entry))
        log_entry, run_entry = self._pair(
            "choice_identifier", first, first)
        self.assertTrue(mod07.validate_choice_pair(log_entry, run_entry))

    def test_cyclic_marks_return_verdict_not_recursion(self):
        first = {}
        first["self"] = first
        second = {}
        second["self"] = second
        log_entry, run_entry = self._pair(
            "dependence_marks", first, second)
        self.assertFalse(mod07.validate_choice_pair(log_entry, run_entry))

    def test_joint_run_surface_answers_on_cyclic_marks(self):
        cyclic = []
        cyclic.append(cyclic)
        choice = mod07.make_adapter_choice(
            "c1", "reading", "point", "v1", "fold")
        stored_entry = {
            "choice_identifier": "c1",
            "reading_applied": "reading",
            "governing_text_version": "v1",
            "dependence_marks": cyclic,
        }
        run = valid_run()
        run["adapter_choices"] = [choice]
        run["interpretation_log_entries"] = [dict(stored_entry)]
        run["run_record_entries"] = [dict(stored_entry)]
        self.assertIsInstance(mod07.validate_joint_run(run), bool)
        self.assertIsNotNone(mod07.joint_run_failure(run))
        self.assertIsInstance(
            mod07.seam_headline_claim_stands(run, ["OS-1"]), bool)

    def test_plain_controls_hold(self):
        base = mod07.make_adapter_choice(
            "c1", "reading", "point", "v1", "fold")
        self.assertTrue(mod07.validate_choice_pair(
            mod07.interpretation_log_entry(base),
            mod07.run_record_entry(base)))


class TestR15056KillCheckClaimsCarriage(unittest.TestCase):
    def _record_with_claims(self, claims):
        record = family()
        record["headline_claims"] = claims
        record["claims"] = claims
        record["kill_check_fields"] = [{"claim": "no such claim"}]
        record["kill_checks"] = [{"claim": "no such claim"}]
        return record

    def test_absent_claim_fails_in_other_carriages(self):
        for claims in ({"headline claim 1"},
                       frozenset({"headline claim 1"}),
                       {"headline claim 1": True}):
            record = self._record_with_claims(claims)
            self.assertFalse(
                mod12.validate_family_record(record), repr(claims))
            failures = mod12.family_record_validation_failures(record)
            self.assertTrue(
                any("kill check" in item for item in failures),
                repr(claims))

    def test_controls_hold(self):
        self.assertFalse(mod12.validate_family_record(family()))
        self.assertEqual(
            mod12.family_record_validation_failures(family()),
            ["the reportable run judgement stands refused"])
        record = self._record_with_claims(("headline claim 1",))
        self.assertFalse(mod12.validate_family_record(record))


class TestR15057EdgeTextSetDress(unittest.TestCase):
    def test_lawful_lien_state_in_set_dress_passes(self):
        for state in ({"computed not settled"},
                      frozenset({"computed not settled"}),
                      ["computed not ", {"settled"}]):
            effect = {"lien_state": state}
            self.assertTrue(
                mod07.validate_cross_seam_effect(effect), repr(state))

    def test_joint_run_with_set_dress_lien_state(self):
        run = valid_run(effects=[{"lien_state": {"computed not settled"}}])
        self.assertTrue(mod07.validate_joint_run(run))
        self.assertTrue(
            mod07.seam_headline_claim_stands(run, ["OS-1"]))

    def test_lawful_joint_dependent_in_set_dress_passes(self):
        for dependent in ({"MOD-07"}, frozenset({"MOD-07"}),
                          ["MOD-", {"07"}]):
            record = {"edges": [("MOD-05", "MOD-07"),
                                ("MOD-06", "MOD-07")],
                      "joint_dependent": dependent}
            self.assertTrue(
                mod07.validate_dependency_record(record), repr(dependent))

    def test_barred_edge_part_in_set_dress_refused(self):
        record = {"edges": [({"MOD-05"}, "MOD-06")],
                  "joint_dependent": "MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(record))

    def test_cured_dress_controls_hold(self):
        for state in (("computed ", "not settled"),
                      ["computed ", ["not settled"]],
                      ["computed ", b"not settled"]):
            self.assertTrue(mod07.validate_cross_seam_effect(
                {"lien_state": state}), repr(state))


class TestR15058DependencyDictOfEdgeRecords(unittest.TestCase):
    def test_barred_edge_as_dict_value_record_refused(self):
        for source, target in (("MOD-05", "MOD-06"),
                               ("MOD-06", "MOD-05")):
            record = {
                "edges": {"e1": {"source": source, "target": target}},
                "joint_dependent": "MOD-07"}
            self.assertFalse(
                mod07.validate_dependency_record(record), (source, target))

    def test_controls_hold(self):
        self.assertTrue(
            mod07.validate_dependency_record(mod07.dependency_record()))
        record = {
            "edges": {"source": "MOD-05", "target": ["MOD-06"]},
            "joint_dependent": "MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(record))
        record = {
            "edges": {"e1": {"source": "MOD-05", "target": "MOD-07"},
                      "e2": {"source": "MOD-06", "target": "MOD-07"}},
            "joint_dependent": "MOD-07"}
        self.assertTrue(mod07.validate_dependency_record(record))


class TestR15059StoredValuesCycleGuard(unittest.TestCase):
    def test_two_cyclic_identifiers_answer_a_count(self):
        first = []
        first.append(first)
        second = []
        second.append(second)
        result = sample_n(first, second)
        self.assertEqual(result["n"], 2)

    def test_same_cyclic_identifier_counts_once(self):
        cyclic = []
        cyclic.append(cyclic)
        result = sample_n(cyclic, cyclic)
        self.assertEqual(result["n"], 1)

    def test_family_acts_answer_on_cyclic_claim(self):
        cyclic = []
        cyclic.append(cyclic)
        record = family()
        record["headline_claims"] = [cyclic]
        record["claims"] = [cyclic]
        record["kill_check_fields"] = [{"claim": cyclic}]
        record["kill_checks"] = [{"claim": cyclic}]
        self.assertIsInstance(mod12.validate_family_record(record), bool)
        self.assertIsInstance(
            mod12.family_record_validation_failures(record), list)


class TestR15094SampleNamingQuoting(unittest.TestCase):
    def test_separator_identifier_named_as_one_run(self):
        runs = [{"run_class": "screening", "run_id": "a, b"}]
        result = mod12.sample_statement(runs)
        self.assertEqual(result["n"], 1)
        self.assertIn('"a, b"', result["sample"])

    def test_plain_names_unquoted_as_before(self):
        runs = [{"run_class": "screening", "run_id": "r1"},
                {"run_class": "screening", "run_id": "r2"}]
        result = mod12.sample_statement(runs)
        self.assertEqual(
            result["sample"],
            "the runs named in this statement: r1, r2")


if __name__ == "__main__":
    unittest.main()
