# Step 15 rerun, fix wave 14, Builder 7 pins.
# Rows R14-049 to R14-057 and R14-076: the MOD-07 and MOD-12
# joint run, dependency, choice pair, family, and sample forms.
# Every pin states the standing its register row charges, with
# the proving acts the source papers used.
import unittest

import crucible.mod07 as mod07
import crucible.mod12 as mod12


class AlwaysEq:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class RaisingEq:
    def __eq__(self, other):
        raise RuntimeError("equality reading raises")

    def __ne__(self, other):
        raise RuntimeError("equality reading raises")

    __hash__ = object.__hash__


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


class TestR14049FamilyDressReading(unittest.TestCase):
    def test_ecology_point_in_dress_stands_barred(self):
        for dress in (b"fixed", bytearray(b"fixed"),
                      memoryview(b"fixed"), ["fix", "ed"],
                      ("fix", "ed")):
            record = family(ecology_point=dress)
            record.pop("amendment_landed", None)
            self.assertFalse(
                mod12.validate_family_record(record), repr(dress))
            failures = mod12.family_record_validation_failures(record)
            self.assertTrue(
                any("ecology" in item for item in failures),
                repr(dress))
        plain = family(ecology_point="fixed")
        plain.pop("amendment_landed", None)
        self.assertFalse(mod12.validate_family_record(plain))
        self.assertTrue(mod12.validate_family_record(family()))

    def test_kill_claim_in_dress_stands_judged(self):
        for dress in (b"headline claim 1",
                      bytearray(b"headline claim 1"),
                      ["headline ", "claim 1"],
                      ("headline ", "claim 1")):
            record = family()
            record["kill_check_fields"] = [{"claim": dress}]
            record["kill_checks"] = [{"claim": dress}]
            self.assertTrue(
                mod12.validate_family_record(record), repr(dress))
            self.assertEqual(
                mod12.family_record_validation_failures(record), [],
                repr(dress))

    def test_standing_claims_in_bytes_dress_match_plain_check(self):
        record = family()
        record["headline_claims"] = [b"headline claim 1"]
        record["claims"] = [b"headline claim 1"]
        record["kill_check_fields"] = [{"claim": "headline claim 1"}]
        record["kill_checks"] = [{"claim": "headline claim 1"}]
        self.assertTrue(mod12.validate_family_record(record))
        self.assertEqual(
            mod12.family_record_validation_failures(record), [])


class TestR14050FamilyKillEqualityReading(unittest.TestCase):
    def test_equality_lying_claim_standing_nowhere_fails(self):
        record = family()
        record["kill_check_fields"] = [{"claim": AlwaysEq()}]
        record["kill_checks"] = [{"claim": AlwaysEq()}]
        self.assertFalse(mod12.validate_family_record(record))
        failures = mod12.family_record_validation_failures(record)
        self.assertTrue(
            any("kill check" in item for item in failures))

    def test_raising_equality_claim_fails_without_escape(self):
        record = family()
        record["kill_check_fields"] = [{"claim": RaisingEq()}]
        record["kill_checks"] = [{"claim": RaisingEq()}]
        self.assertFalse(mod12.validate_family_record(record))
        self.assertTrue(
            mod12.family_record_validation_failures(record))


class TestR14051FamilyKillDictCarriage(unittest.TestCase):
    def test_single_dict_check_naming_absent_claim_fails(self):
        record = family()
        record["kill_checks"] = {"claim": "no such claim"}
        record["kill_check_fields"] = []
        self.assertFalse(mod12.validate_family_record(record))
        self.assertTrue(
            any("kill check" in item for item in
                mod12.family_record_validation_failures(record)))

    def test_dict_keyed_by_absent_claim_fails(self):
        record = family()
        record["kill_check_fields"] = {"no such claim": True}
        record["kill_checks"] = []
        self.assertFalse(mod12.validate_family_record(record))
        self.assertTrue(
            any("kill check" in item for item in
                mod12.family_record_validation_failures(record)))

    def test_single_dict_check_naming_standing_claim_passes(self):
        record = family()
        record["kill_checks"] = {"claim": "headline claim 1"}
        record["kill_check_fields"] = {"claim": "headline claim 1"}
        self.assertTrue(mod12.validate_family_record(record))
        self.assertEqual(
            mod12.family_record_validation_failures(record), [])


class TestR14052ChoicePairTextFields(unittest.TestCase):
    def entries(self, log_field, run_field, field):
        base = {"choice_identifier": "c1", "reading_applied": "r",
                "governing_text_version": "v", "dependence_marks": []}
        log_entry = dict(base)
        run_entry = dict(base)
        log_entry[field] = log_field
        run_entry[field] = run_field
        return log_entry, run_entry

    def test_equality_lying_text_fields_disagree(self):
        for field in ("choice_identifier", "reading_applied",
                      "governing_text_version"):
            log_entry, run_entry = self.entries(
                AlwaysEq(), AlwaysEq(), field)
            self.assertFalse(
                mod07.validate_choice_pair(log_entry, run_entry), field)
            log_entry, run_entry = self.entries(
                [AlwaysEq()], [AlwaysEq()], field)
            self.assertFalse(
                mod07.validate_choice_pair(log_entry, run_entry), field)

    def test_raising_equality_text_field_fails_without_escape(self):
        log_entry, run_entry = self.entries(
            RaisingEq(), RaisingEq(), "choice_identifier")
        self.assertFalse(
            mod07.validate_choice_pair(log_entry, run_entry))

    def test_plain_controls_hold(self):
        log_entry, run_entry = self.entries("r", "r", "reading_applied")
        self.assertTrue(
            mod07.validate_choice_pair(log_entry, run_entry))
        log_entry, run_entry = self.entries(
            "r", "other", "reading_applied")
        self.assertFalse(
            mod07.validate_choice_pair(log_entry, run_entry))


class TestR14053DependencyEdgesDictCarriage(unittest.TestCase):
    def test_barred_edge_as_dict_key_fails(self):
        record = {"edges": {("MOD-05", "MOD-06"): True},
                  "joint_dependent": "MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(record))

    def test_barred_edge_in_source_target_dict_form_fails(self):
        record = {"edges": {"MOD-05": "MOD-06"},
                  "joint_dependent": "MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(record))

    def test_controls_hold(self):
        self.assertTrue(
            mod07.validate_dependency_record(mod07.dependency_record()))
        self.assertFalse(mod07.validate_dependency_record(
            {"edges": [("MOD-05", "MOD-06")],
             "joint_dependent": "MOD-07"}))


class TestR14054DependencyCyclicEdgePart(unittest.TestCase):
    def test_cyclic_edge_part_returns_false_without_escape(self):
        cyclic = []
        cyclic.append(cyclic)
        record = {"edges": [(cyclic, "MOD-06")],
                  "joint_dependent": "MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(record))

    def test_deep_acyclic_edge_part_still_judged(self):
        deep = "MOD-05"
        for _ in range(200):
            deep = [deep]
        record = {"edges": [(deep, "MOD-06")],
                  "joint_dependent": "MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(record))
        self.assertTrue(
            mod07.validate_dependency_record(mod07.dependency_record()))


class TestR14055DependencyJointDependentDress(unittest.TestCase):
    def lawful(self, joint):
        return {"edges": [("MOD-05", "MOD-07"), ("MOD-06", "MOD-07")],
                "joint_dependent": joint}

    def test_lawful_joint_dependent_in_dress_passes(self):
        for dress in (b"MOD-07", bytearray(b"MOD-07"),
                      memoryview(b"MOD-07"), ["MOD-", "07"],
                      ("MOD-", "07")):
            self.assertTrue(
                mod07.validate_dependency_record(self.lawful(dress)),
                repr(dress))
        self.assertTrue(mod07.validate_dependency_record(
            {"edges": [], "joint_dependent": b"MOD-07"}))

    def test_barred_direction_holds_in_dress(self):
        record = {"edges": [(b"MOD-05", b"MOD-08"),
                            (b"MOD-06", b"MOD-08")],
                  "joint_dependent": b"MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(record))
        self.assertTrue(
            mod07.validate_dependency_record(self.lawful("MOD-07")))


class TestR14056CrossSeamDress(unittest.TestCase):
    def test_lawful_state_in_dress_stands(self):
        for dress in (b"computed not settled",
                      bytearray(b"computed not settled"),
                      memoryview(b"computed not settled"),
                      ["computed not ", "settled"]):
            effect = {"lien_state": dress}
            self.assertTrue(
                mod07.validate_cross_seam_effect(effect), repr(dress))
            run = valid_run([effect])
            self.assertTrue(mod07.validate_joint_run(run), repr(dress))
            self.assertIsNone(mod07.joint_run_failure(run), repr(dress))
            self.assertTrue(
                mod07.seam_headline_claim_stands(run, ["OS-1"]),
                repr(dress))

    def test_barred_state_in_dress_stands_refused(self):
        for dress in (b"settled in the chosen escrow",
                      ["rele", "ased"], b"released"):
            effect = {"lien_state": dress}
            self.assertFalse(
                mod07.validate_cross_seam_effect(effect), repr(dress))
            run = valid_run([effect])
            self.assertFalse(mod07.validate_joint_run(run), repr(dress))
            failure = mod07.joint_run_failure(run)
            self.assertIsNotNone(failure, repr(dress))
            self.assertEqual(
                failure["name"],
                "cross seam effect carries settled wording",
                repr(dress))
        self.assertTrue(mod07.validate_cross_seam_effect(
            {"lien_state": "computed not settled"}))


class TestR14057SeamHeadlineItemsTouchedForm(unittest.TestCase):
    def test_items_in_no_iterable_form_return_false(self):
        run = valid_run()
        self.assertFalse(mod07.seam_headline_claim_stands(run, None))
        self.assertFalse(mod07.seam_headline_claim_stands(run, 5))

    def test_controls_hold(self):
        run = valid_run()
        self.assertTrue(mod07.seam_headline_claim_stands(run, ["OS-1"]))
        self.assertFalse(mod07.seam_headline_claim_stands(run, "OS-1"))
        self.assertTrue(
            mod07.seam_headline_claim_stands(run, {"OS-1": 1}))
        self.assertFalse(
            mod07.seam_headline_claim_stands(run, {"OS-99"}))
        self.assertTrue(mod07.seam_headline_claim_stands(
            run, (item for item in ["OS-1"])))


class TestR14076SampleStatementPrintedNames(unittest.TestCase):
    def test_int_and_text_identifiers_printing_alike_count_once(self):
        runs = [{"run_class": "screening", "run_id": 1},
                {"run_class": "screening", "run_id": "1"}]
        result = mod12.sample_statement(runs)
        self.assertEqual(result["n"], 1)
        self.assertEqual(
            result["runs_completed_by_class"]["screening"], 1)
        self.assertEqual(result["sample"].count("1"), 1)
        readout = mod12.screening_readout(runs=runs)
        self.assertEqual(readout["sample_statement"]["n"], 1)

    def test_controls_hold(self):
        runs = [{"run_class": "screening", "run_id": b"r1"},
                {"run_class": "screening", "run_id": "r1"}]
        self.assertEqual(mod12.sample_statement(runs)["n"], 1)
        runs = [{"run_class": "screening", "run_id": "r1"},
                {"run_class": "screening", "run_id": "r2"}]
        result = mod12.sample_statement(runs)
        self.assertEqual(result["n"], 2)
        self.assertEqual(
            result["runs_completed_by_class"]["screening"], 2)
        one = {"run_class": "screening", "run_id": "r1"}
        self.assertEqual(
            mod12.sample_statement([one, dict(one)])["n"], 1)


if __name__ == "__main__":
    unittest.main()
