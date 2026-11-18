"""Step 16 fix wave, Builder 6 rows R16-05, R16-06, R16-07, R16-09, R16-18.

Documentation and construction surface. Every test in this file
states a check that failed on the landed product at head
d0fb43375412de52011e885e2f537d0086864bd7 before the cure.
Copyright: J.P. Picard aka Macro-Harder.
"""
import pathlib
import unittest

import crucible
from crucible import mod01, mod10

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

MOD10_UNDOCUMENTED_21 = [
    "retain_run_record", "read_run_record", "validate_run_record_set",
    "event_log_fields", "daily_snapshot_fields", "storage_accounting",
    "validate_storage_accounting", "retention_policy_table",
    "validate_storage_claim", "apply_flag_evaluation",
    "validate_retention_report", "append_annotation",
    "validate_annotation_claim", "validate_retention_sizing",
    "retention_met", "pre_registered_full_log_sample",
    "validate_sample_record", "validate_retention_record",
    "store_indexes", "validate_store_placement", "store_lookup",
]

MODULE_PURPOSES = {
    "mod01": "Types and validation",
    "mod02": "Seed and Stream Engine",
    "mod03": "Society Generator",
    "mod04": "Tick Engine",
    "mod05": "Parley Core",
    "mod06": "Escrow Core",
    "mod07": "Escrow Adapter",
    "mod08": "Detection Layer",
    "mod09": "Attacker Seat",
    "mod10": "Recorder and stores",
    "mod11": "Reporter",
    "mod12": "Sweep Controller",
    "mod13": "Replication Checker",
    "mod14": "Shell",
    "mod16": "Integration surface",
}


def guide_text():
    return README + "\n" + (crucible.__doc__ or "")


class TestR1605Readme(unittest.TestCase):
    def test_readme_states_what_package_offers_today(self):
        self.assertIn("What the package offers today", README)

    def test_readme_shows_how_to_import(self):
        self.assertIn("import crucible", README)
        self.assertIn("from crucible import mod01", README)

    def test_readme_states_where_forms_live(self):
        self.assertIn("mod01", README)
        self.assertIn("FORM_TYPES", README)

    def test_readme_states_dq702_gate(self):
        self.assertIn("DQ7-02", README)
        self.assertIn("gated", README)
        self.assertIn("no seed", README.lower())

    def test_readme_claims_no_surface_that_does_not_exist(self):
        self.assertNotIn("nothing to install", README)
        self.assertIn("does not run a simulation today", README)


class TestR1606SurfaceGuide(unittest.TestCase):
    def test_guide_names_each_module_by_purpose(self):
        text = guide_text()
        for module, purpose in MODULE_PURPOSES.items():
            self.assertIn(module, text, module)
            self.assertIn(purpose, text, module)

    def test_guide_states_corrected_exported_total(self):
        text = guide_text()
        self.assertIn("641", text)
        self.assertIn("summed", text)

    def test_guide_marks_entry_points_against_internal(self):
        text = guide_text()
        self.assertIn("User entry points", text)
        self.assertIn("Internal surface", text)
        self.assertIn("validate_record", text)
        self.assertIn("underscore", text)


class TestR1607Constructors(unittest.TestCase):
    def test_named_constructors_exist(self):
        self.assertTrue(callable(getattr(mod01, "build_sweep_point", None)))
        self.assertTrue(callable(getattr(mod01, "build_run_record", None)))

    def test_field_ownership_covers_forms_2_and_4_exactly(self):
        ownership = mod01.FORM_FIELD_OWNERSHIP
        for fid in ("2", "4"):
            named = set()
            for group in ownership[fid].values():
                named.update(group)
            self.assertEqual(named, set(mod01.form_fields(fid)), fid)

    def test_form4_seed_fields_are_never_fill(self):
        never = mod01.FORM_FIELD_OWNERSHIP["4"]["never_fill"]
        self.assertIn("root_seed_reference", never)
        self.assertIn("derived_run_seed_identifier", never)

    def test_build_sweep_point_validates(self):
        point = mod01.build_sweep_point(point_identifier="point-b6")
        self.assertTrue(mod01.validate_record("2", point))

    def test_build_run_record_validates(self):
        record = mod01.build_run_record(run_class="headline")
        self.assertTrue(mod01.validate_record("4", record))

    def test_build_run_record_refuses_seed_fields_naming_gate(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_run_record(root_seed_reference="seed-x")
        self.assertIn("DQ7-02", str(caught.exception))

    def test_template_path_still_stands(self):
        self.assertTrue(mod01.validate_record(
            "2", mod01.minimal_valid_instance("2")))
        self.assertTrue(mod01.validate_record(
            "4", mod01.minimal_valid_instance("4")))

    def test_form_classes_state_ownership(self):
        for fid in ("2", "4"):
            doc = mod01.FORM_TYPES[fid].__doc__ or ""
            self.assertIn("user supplies", doc, fid)
            self.assertIn("never fill", doc, fid)


class TestR1609Docstrings(unittest.TestCase):
    def test_mod10_21_callables_carry_full_docstrings(self):
        for name in MOD10_UNDOCUMENTED_21:
            doc = getattr(mod10, name).__doc__ or ""
            self.assertTrue(doc.strip(), name)
            self.assertIn("Arguments", doc, name)
            self.assertIn("Returns", doc, name)
            self.assertIn("Failure", doc, name)

    def test_form_types_classes_carry_docstrings(self):
        self.assertEqual(len(mod01.FORM_TYPES), 38)
        for fid, cls in mod01.FORM_TYPES.items():
            doc = cls.__doc__ or ""
            self.assertTrue(doc.strip(), fid)
            self.assertIn(fid, doc, fid)
            self.assertIn("fields", doc, fid)


class TestR1618DailyAggregatesSeparation(unittest.TestCase):
    def test_two_shapes_separated_by_name(self):
        self.assertTrue(callable(getattr(
            mod10, "validate_recorder_daily_aggregate_rows", None)))
        self.assertTrue(callable(getattr(
            mod10, "validate_form14_daily_aggregates_record", None)))

    def test_validate_daily_aggregates_docstring_states_its_shape(self):
        doc = mod10.validate_daily_aggregates.__doc__ or ""
        self.assertIn("Recorder", doc)
        self.assertIn("Form 14", doc)
        self.assertIn("not", doc)

    def test_canonical_form14_passes_its_own_named_act(self):
        record = mod01.minimal_valid_instance("14")
        self.assertTrue(mod10.validate_form14_daily_aggregates_record(record))
        self.assertFalse(mod10.validate_recorder_daily_aggregate_rows([record]))

    def test_recorder_row_passes_recorder_act(self):
        rows = mod10.daily_aggregates_for_run("run-b6-shape")
        self.assertTrue(mod10.validate_recorder_daily_aggregate_rows(rows))


if __name__ == "__main__":
    unittest.main()
