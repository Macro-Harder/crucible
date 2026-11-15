"""Fix wave 16 pins, Builder 5: rows R16-018, R16-019, R16-046,
R16-050, R16-051, R16-052, R16-053, R16-058, R16-059, R16-082,
R16-083, R16-084, and R16-085.

MOD-11 headline part text and registry key dress under settlement
S-15, MOD-11 stem er, est, able, ible, and compound forms beside
the R14-033 bound and the R15-044 merge bound, and MOD-12 sample,
sweep, and family forms.
"""
import subprocess
import sys
import unittest

import crucible.mod11 as mod11
import crucible.mod12 as mod12


FIELD10_TEXT = (
    "seam status: no cross seam effect; "
    "kill check: self checked only; "
    "dependence mark: DQ-164 confirmation form, recording that "
    "DQ-164 stands settled as confirmation only; "
    "Parley Q3 statement: no part of the result encodes Parley "
    "Q3 behaviour; "
    "core only qualifier: this unit is a core only result; "
    "anchor scenario statement: no anchor scenario is used in "
    "this unit."
)

CLAIM_TEXT = (
    "At the sampled points within the stated scope, the result "
    "holds for the sampled points only, and nothing is claimed "
    "beyond the stated limits."
)

GROUNDING_TEXT = (
    "This unit rests on the retained run records within the "
    "stated scope, and its limits are that nothing is claimed "
    "beyond the sampled points in this unit."
)

FIELD10_PART_A = "seam status: no cross"
FIELD10_PART_B = FIELD10_TEXT[len("seam status: no cross "):]


def compliant_unit():
    unit = {field: "value for " + field
            for field in mod11.HEADLINE_UNIT_FIELDS}
    unit["claim_sentence"] = CLAIM_TEXT
    unit["grounding_sentence"] = GROUNDING_TEXT
    unit["qualifiers_and_markings_block"] = FIELD10_TEXT
    unit["holding_region"] = {"sampled_points": [
        {"axis_values": {"farm size": 200}, "outcome": "holds"}]}
    unit["failure_region"] = {"sampled_points": [
        {"axis_values": {"farm size": 800}, "outcome": "fails"}]}
    return unit


def readout_for(rule):
    return {"quantities": [
        {"name": "sample share", "recorded_number": 3,
         "class_based": True, "class_rule": rule}]}


def nest(depth, leaf):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def run_fresh(code, seed):
    result = subprocess.run(
        [sys.executable, "-c", code],
        env={"PYTHONHASHSEED": str(seed), "PATH": "/usr/bin:/bin",
             "PYTHONPATH": "."},
        capture_output=True, text=True, cwd=".")
    return result.stdout.strip()


class TestR16018PartTextSetDress(unittest.TestCase):
    def test_set_dress_composes_seam_value(self):
        text = mod11._part_text({FIELD10_PART_A, FIELD10_PART_B})
        self.assertIn("no cross seam effect", text.lower())

    def test_frozenset_dress_field10_stands(self):
        value = frozenset({FIELD10_PART_A, FIELD10_PART_B})
        self.assertTrue(mod11._field10_stands(value))

    def test_set_dress_unit_validates(self):
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = {
            FIELD10_PART_A, FIELD10_PART_B}
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_cross_process_set_dress_stable(self):
        code = (
            "import crucible.mod11 as m;"
            "u={f:'value for '+f for f in m.HEADLINE_UNIT_FIELDS};"
            "u['claim_sentence']=%r;"
            "u['grounding_sentence']=%r;"
            "u['qualifiers_and_markings_block']={%r,%r};"
            "u['holding_region']={'sampled_points':[{'axis_values':"
            "{'farm size':200},'outcome':'holds'}]};"
            "u['failure_region']={'sampled_points':[{'axis_values':"
            "{'farm size':800},'outcome':'fails'}]};"
            "print(m.validate_headline_unit(u))"
        ) % (CLAIM_TEXT, GROUNDING_TEXT,
             FIELD10_PART_A, FIELD10_PART_B)
        for seed in (0, 2, 3, 99):
            with self.subTest(seed=seed):
                self.assertEqual(run_fresh(code, seed), "True")

    def test_plain_and_list_controls_hold(self):
        self.assertTrue(mod11.validate_headline_unit(compliant_unit()))
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = [
            FIELD10_PART_A, FIELD10_PART_B]
        self.assertTrue(mod11.validate_headline_unit(unit))


class TestR16046PartTextBufferDress(unittest.TestCase):
    def test_part_text_reads_buffers_by_stored_bytes(self):
        self.assertEqual(mod11._part_text(b"holds whole"), "holds whole")
        self.assertEqual(
            mod11._part_text(bytearray(b"holds whole")), "holds whole")
        self.assertEqual(
            mod11._part_text(memoryview(b"holds whole")), "holds whole")

    def test_memoryview_field10_validates(self):
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = memoryview(
            FIELD10_TEXT.encode("utf-8"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_memoryview_claim_sentence_validates(self):
        unit = compliant_unit()
        unit["claim_sentence"] = memoryview(CLAIM_TEXT.encode("utf-8"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_bytes_and_bytearray_controls_hold(self):
        for dress in (FIELD10_TEXT.encode("utf-8"),
                      bytearray(FIELD10_TEXT.encode("utf-8"))):
            unit = compliant_unit()
            unit["qualifiers_and_markings_block"] = dress
            with self.subTest(dress=type(dress)):
                self.assertTrue(mod11.validate_headline_unit(unit))


class TestR16019RegistryKeyDress(unittest.TestCase):
    def test_frozenset_key_reads_field_in_any_order(self):
        entry = {frozenset({"claim", "_identifier"}): "cid-1"}
        self.assertEqual(
            mod11._registry_stored_value(entry, "claim_identifier"),
            "cid-1")

    def test_frozenset_key_outcome_not_missing(self):
        entry = {frozenset({"come", "out"}): "reported"}
        self.assertNotIn(
            "outcome", mod11._registry_missing_fields(entry))

    def test_cross_process_registry_key_stable(self):
        code = (
            "import crucible.mod11 as m;"
            "e={frozenset({'claim','_identifier'}):'cid-1'};"
            "print(m._registry_stored_value(e,'claim_identifier'))"
        )
        for seed in (0, 2, 3, 99):
            with self.subTest(seed=seed):
                self.assertEqual(run_fresh(code, seed), "cid-1")

    def test_registry_key_text_deterministic_sorted(self):
        self.assertEqual(
            mod11._registry_key_text(frozenset({"zz", "aa"})), "aazz")

    def test_plain_and_tuple_key_controls_hold(self):
        self.assertEqual(
            mod11._registry_stored_value(
                {"claim_identifier": "cid-2"}, "claim_identifier"),
            "cid-2")
        self.assertEqual(
            mod11._registry_stored_value(
                {("claim_", "identifier"): "cid-3"}, "claim_identifier"),
            "cid-3")


class TestR16050ErEstEForm(unittest.TestCase):
    def test_houser_housest_tabler_tablest_not_readable(self):
        for word in ("houser", "housest", "tabler", "tablest"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_e_form_yields_no_no_gradable_base(self):
        self.assertNotIn("house", mod11._readable_stem("houser"))
        self.assertNotIn("house", mod11._readable_stem("housest"))
        self.assertNotIn("table", mod11._readable_stem("tabler"))
        self.assertNotIn("table", mod11._readable_stem("tablest"))

    def test_readout_refuses_charged_spellings(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("housest tablest result")))

    def test_controls_hold(self):
        for word in ("realest", "goodest", "wrongest", "chairest",
                     "bookest", "windowest", "sunner", "sunnest",
                     "dogger", "doggest"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)
        for word in ("happier", "happiest", "nicer", "nicest"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word), word)


class TestR16051ErEstIBranch(unittest.TestCase):
    def test_manier_maniest_not_readable(self):
        for word in ("manier", "maniest"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_i_branch_yields_no_many(self):
        self.assertNotIn("many", mod11._readable_stem("manier"))
        self.assertNotIn("many", mod11._readable_stem("maniest"))

    def test_readout_refuses_manier_maniest(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("manier maniest result")))

    def test_controls_hold(self):
        self.assertFalse(mod11._is_readable_word("manyer"))
        self.assertFalse(mod11._is_readable_word("manyest"))
        self.assertTrue(mod11._is_readable_word("happier"))
        self.assertTrue(mod11._is_readable_word("happiest"))


class TestR16052AbleIbleNextRing(unittest.TestCase):
    CHARGED = ("writible", "makible", "payible", "sellible",
               "wearible", "noticible", "managible", "permissable")

    def test_charged_cross_spellings_not_readable(self):
        for word in self.CHARGED:
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_readout_refuses_charged_spellings(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("writible permissable result")))

    def test_cured_controls_hold(self):
        for word in ("convertable", "accessable", "breakible",
                     "readible", "washible", "usible"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_lawful_controls_hold(self):
        for word in ("writable", "payable", "noticeable",
                     "manageable", "permissible", "breakability",
                     "convertibility", "accessible", "washable"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word), word)


class TestR16053CompoundInformationies(unittest.TestCase):
    def test_informationies_not_readable(self):
        self.assertFalse(mod11._is_readable_word("informationies"))

    def test_readout_refuses_informationies(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("informationies result holds")))

    def test_r14_033_bound_forms_stand(self):
        for word in ("informationes", "informations"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word), word)
                self.assertEqual(mod11._readable_stem(word), [])

    def test_toothes_refused_on_ruling_h(self):
        self.assertFalse(mod11._is_readable_word("toothes"))
        self.assertEqual(mod11._readable_stem("toothes"), [])

    def test_barred_plural_controls_hold(self):
        for word in ("sheepes", "childs", "mouses", "tooths",
                     "datas", "halfs", "wifies", "lifies"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)
        self.assertTrue(mod11._is_readable_word("parties"))
        self.assertTrue(mod11._is_readable_word("stories"))


class TestR16058StoredIdsDepth(unittest.TestCase):
    def test_deep_equal_identifiers_answer_equal(self):
        first = nest(600, "r1")
        second = nest(600, "r1")
        self.assertTrue(mod12._stored_ids_equal(first, second))

    def test_deep_differing_identifiers_answer_apart(self):
        first = nest(600, "r1")
        second = nest(600, "r2")
        self.assertFalse(mod12._stored_ids_equal(first, second))

    def test_sample_statement_deep_ids_count_once(self):
        runs = [
            {"run_id": nest(600, "r1"), "run_class": "screening"},
            {"run_id": nest(600, "r1"), "run_class": "screening"},
        ]
        self.assertEqual(mod12.sample_statement(runs)["n"], 1)

    def test_sample_statement_deep_differing_ids_count_two(self):
        runs = [
            {"run_id": nest(600, "r1"), "run_class": "screening"},
            {"run_id": nest(600, "r2"), "run_class": "screening"},
        ]
        self.assertEqual(mod12.sample_statement(runs)["n"], 2)

    def test_controls_hold(self):
        self.assertEqual(mod12.sample_statement([
            {"run_id": nest(300, "r1"), "run_class": "screening"},
            {"run_id": nest(300, "r1"), "run_class": "screening"},
        ])["n"], 1)
        cyclic = []
        cyclic.append(cyclic)
        self.assertEqual(mod12.sample_statement([
            {"run_id": cyclic, "run_class": "screening"},
            {"run_id": cyclic, "run_class": "screening"},
        ])["n"], 1)


class TestR16059SweepManifestShapeGuard(unittest.TestCase):
    def test_deep_hash_value_refused_in_named_form(self):
        record = {"family_identifier": "f", "family_version": "v",
                  "family_manifest_hash": nest(800, "x")}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.sweep_manifest(record)

    def test_cyclic_hash_value_refused_in_named_form(self):
        cyclic = []
        cyclic.append(cyclic)
        record = {"family_identifier": "f", "family_version": "v",
                  "family_manifest_hash": cyclic}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.sweep_manifest(record)

    def test_shallow_and_moderate_controls_return_manifest(self):
        record = {"family_identifier": "f", "family_version": "v",
                  "family_manifest_hash": nest(30, "x")}
        manifest = mod12.sweep_manifest(record)
        self.assertEqual(manifest["family_identifier"], "f")
        self.assertEqual(manifest["family_version"], "v")
        plain = mod12.sweep_manifest(
            mod12.make_family_record())
        self.assertEqual(plain["family_identifier"], "family-under-test")


class TestR16082KillCheckBareStandingClaims(unittest.TestCase):
    def record_with(self, standing):
        record = mod12.make_family_record()
        record["headline_claims"] = standing
        record["claims"] = standing
        record["kill_check_fields"] = [
            mod12.kill_check_for_claim("totally foreign claim")]
        record["kill_checks"] = record["kill_check_fields"]
        return record

    def test_bare_text_standing_claims_judged(self):
        record = self.record_with("headline claim 1")
        self.assertTrue(mod12._kill_check_names_absent(record))
        self.assertFalse(mod12.validate_family_record(record))
        self.assertTrue(mod12.family_record_validation_failures(record))

    def test_bytes_standing_claims_judged(self):
        record = self.record_with(b"headline claim 1")
        self.assertTrue(mod12._kill_check_names_absent(record))

    def test_scalar_standing_claims_judged(self):
        record = self.record_with(7)
        self.assertTrue(mod12._kill_check_names_absent(record))

    def test_controls_hold(self):
        record = self.record_with(["headline claim 1"])
        self.assertTrue(mod12._kill_check_names_absent(record))
        standing = mod12.make_family_record()
        self.assertFalse(mod12._kill_check_names_absent(standing))


class TestR16083ApplyFamilyEditDressClaims(unittest.TestCase):
    def test_bytes_claim_in_edit_does_not_draw_refusal(self):
        record = mod12.make_family_record()
        edited = mod12.apply_family_edit(
            record, {"kill_check_fields": [
                {"claim": b"headline claim 1"}]})
        self.assertIsInstance(edited, dict)

    def test_list_claim_in_edit_does_not_draw_refusal(self):
        record = mod12.make_family_record()
        edited = mod12.apply_family_edit(
            record, {"kill_check_fields": [
                {"claim": ["headline claim 1"]}]})
        self.assertIsInstance(edited, dict)

    def test_bytes_claim_with_claims_change_does_not_draw_refusal(self):
        record = mod12.make_family_record()
        edited = mod12.apply_family_edit(record, {
            "claims": ["headline claim 1"],
            "kill_check_fields": [{"claim": b"headline claim 1"}]})
        self.assertIsInstance(edited, dict)

    def test_foreign_claim_controls_still_refused(self):
        record = mod12.make_family_record()
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(
                record, {"kill_check_fields": [
                    {"claim": b"foreign claim"}]})
        edited = mod12.apply_family_edit(
            record, {"kill_check_fields": [
                {"claim": "headline claim 1"}]})
        self.assertIsInstance(edited, dict)


class TestR16084SampleNameQuoting(unittest.TestCase):
    def test_name_with_quote_and_separator_named_as_one(self):
        result = mod12.sample_statement(
            [{"run_id": 'a", "b', "run_class": "screening"}])
        self.assertEqual(result["n"], 1)
        self.assertEqual(
            result["sample"],
            'the runs named in this statement: "a\\", \\"b"')

    def test_separator_only_control_holds(self):
        result = mod12.sample_statement(
            [{"run_id": "a, b", "run_class": "screening"}])
        self.assertEqual(
            result["sample"],
            'the runs named in this statement: "a, b"')

    def test_plain_name_control_holds(self):
        result = mod12.sample_statement(
            [{"run_id": "u1", "run_class": "screening"}])
        self.assertEqual(
            result["sample"], "the runs named in this statement: u1")


class TestR16085SampleMappingRuns(unittest.TestCase):
    def test_mapping_runs_counted(self):
        result = mod12.sample_statement(
            {"r1": {"run_id": "u1", "run_class": "screening"}})
        self.assertEqual(result["n"], 1)
        self.assertEqual(
            result["runs_completed_by_class"]["screening"], 1)

    def test_two_entry_mapping_counted(self):
        result = mod12.sample_statement({
            "r1": {"run_id": "u1", "run_class": "screening"},
            "r2": {"run_id": "u2", "run_class": "validation"}})
        self.assertEqual(result["n"], 2)

    def test_list_and_generator_controls_hold(self):
        run = {"run_id": "u1", "run_class": "screening"}
        self.assertEqual(mod12.sample_statement([run])["n"], 1)
        self.assertEqual(
            mod12.sample_statement(iter([run]))["n"], 1)
        self.assertEqual(mod12.sample_statement([])["n"], 0)


if __name__ == "__main__":
    unittest.main()
