"""Step 16 fix wave 3, Builder 2: row F3-02.

Test first tests for the row charged to Builder 2 in
design/steps/step-16-fix3-charge.md section 1, under ruling
T16-40 at design/steps/step-16-r3-register.md section 5: the
record_validation_failures general naming rule at
crucible/mod01.py. The cure bound is a general rule over the
door failure generation, not a further enumeration of fault
classes: every entry that door returns names its field, and
where a rule or a bar produces the fault, names the rule in
the standing entry form; the generic fallback sentence is
drawn by no fault at that door.

The scan tests stand in the manner of the Round 3 Red 4
mutation scan (design/steps/step-16-r3-audit-red-4.md,
finding R3-RED4-N01): the minimal valid instances of Forms
1 to 23, each field set in turn to the hostile values the
scan used, plus each field deleted in turn. Wherever the
mutated record stands refused, no entry may carry the
generic fallback wording, and an entry must name the field
at fault: the mutated field itself, its completeness pair
spelling where the pair carries one field under two
spellings, or the conditional field a discriminator set
True leaves required.

Bench basis for every figure in the fix paper: bench
Python 3.14.4, Carry 6.

Copyright: J.P. Picard aka Macro-Harder.
"""

import copy
import unittest

from crucible import mod01


GENERIC_FALLBACK_WORDING = "a stated rule of this form stands unmet"

HOSTILE_VALUES = (
    5,
    3.5,
    True,
    ["hostile item"],
    {"hostile_key": "hostile value"},
    "",
    "stated value",
    "prototype order",
    "open: OP-13 value stands open",
    "xxx",
    b"xxx",
)

SCAN_FORM_IDS = tuple(
    fid for fid in mod01.FORM_IDS
    if fid.isdigit() and 1 <= int(fid) <= 23)

PAIR_SLUG_BY_PROSE = dict(mod01.COMPLETENESS_KEY_PAIRS)


def _named_entry(failures, field):
    for entry in failures:
        if ("field " + field + ":") in entry:
            return entry
    return None


def _accepted_names(form_id, field, value):
    """The field names an entry may name for a fault on the
    given field: the field itself; for a Form 1 completeness
    prose spelling, its pair slug, the one field the pair
    carries; for a condition discriminator handed the value
    True, the conditional field the discriminator leaves
    required and standing absent."""
    names = [field]
    if form_id == "1" and field in PAIR_SLUG_BY_PROSE:
        names.append(PAIR_SLUG_BY_PROSE[field])
    if value is True:
        for condition in mod01.field_conditions(form_id):
            if condition["discriminator"] == field:
                names.append(condition["field"])
    return names


def _scan_form(form_id, fields=None):
    """Every scan violation on one form, as a list of texts.
    A violation stands where a mutated or deleted field
    leaves the record refused, and either an entry carries
    the generic fallback wording or no entry names an
    accepted field for the fault. The fields argument
    restricts the scan to a named subset of the form fields,
    so the bench run carries the scan in parallel parts."""
    violations = []
    base = mod01.minimal_valid_instance(form_id)
    probes = []
    for field in list(base.keys()):
        if fields is not None and field not in fields:
            continue
        for value in HOSTILE_VALUES:
            probes.append((field, value, False))
        probes.append((field, None, True))
    for field, value, deleted in probes:
        instance = copy.deepcopy(base)
        if deleted:
            del instance[field]
        else:
            instance[field] = copy.deepcopy(value)
        failures = mod01.record_validation_failures(
            form_id, instance)
        if not failures:
            continue
        for entry in failures:
            if GENERIC_FALLBACK_WORDING in entry:
                violations.append(
                    "form " + form_id + " field " + field
                    + " fault drew the generic fallback entry")
                break
        else:
            names = _accepted_names(form_id, field, value)
            if not any(
                    _named_entry(failures, name) is not None
                    for name in names):
                violations.append(
                    "form " + form_id + " field " + field
                    + " fault named none of "
                    + ", ".join(names))
    return violations


class TestMutationScanGeneralNaming(unittest.TestCase):
    """One test per scanned form, generated below, so the
    split bench run carries the scan in parallel."""


def _make_scan_test(form_id, fields, part):
    def test(self):
        violations = _scan_form(form_id, fields)
        self.assertEqual(
            violations, [],
            "form " + form_id + " part " + str(part)
            + " scan violations: "
            + " | ".join(violations[:12]))
    return test


for _fid in SCAN_FORM_IDS:
    _fields = list(mod01.minimal_valid_instance(_fid).keys())
    _chunks = [
        _fields[start:start + 6]
        for start in range(0, len(_fields), 6)]
    for _part, _chunk in enumerate(_chunks):
        setattr(
            TestMutationScanGeneralNaming,
            "test_scan_form_" + _fid + "_part" + str(_part),
            _make_scan_test(_fid, _chunk, _part))
del _fid, _fields, _chunks, _part, _chunk


class TestRed4NamedCases(unittest.TestCase):
    """The named cases of the Red 4 scan, proved in full."""

    def _assert_named(self, form_id, record, field):
        failures = mod01.record_validation_failures(
            form_id, record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(failures, field)
        self.assertIsNotNone(entry)
        self.assertIn("next step:", entry)
        return entry

    def test_form2_decay_arm_int_names_field(self):
        record = mod01.minimal_valid_instance("2")
        record["belongs_to_decay_arm"] = 5
        self._assert_named("2", record, "belongs_to_decay_arm")

    def test_form2_decay_arm_text_names_field(self):
        record = mod01.minimal_valid_instance("2")
        record["belongs_to_decay_arm"] = "xxx"
        self._assert_named("2", record, "belongs_to_decay_arm")

    def test_form4_anchor_values_scalar_names_field(self):
        record = mod01.minimal_valid_instance("4")
        record["anchor_scenario_values"] = 5
        self._assert_named("4", record, "anchor_scenario_values")

    def test_form5_parameter_values_scalar_names_field(self):
        record = mod01.minimal_valid_instance("5")
        record["parameter_values"] = 5
        self._assert_named("5", record, "parameter_values")

    def test_form10_lost_contact_scalar_names_field(self):
        record = mod01.minimal_valid_instance("10")
        record["lost_contact_clause_on"] = 5
        self._assert_named("10", record, "lost_contact_clause_on")

    def test_form13_anchor_run_scalar_names_field(self):
        record = mod01.minimal_valid_instance("13")
        record["is_anchor_scenario_run"] = 5
        self._assert_named("13", record, "is_anchor_scenario_run")


class TestBarredOrderVariantNaming(unittest.TestCase):
    """The barred order variant limb of ruling T16-40: a
    variant barred by the folded reading the inner judgement
    applies draws the named prototype bar entry, as the
    literal does."""

    VARIANTS = (
        "Prototype Order",
        "PROTOTYPE ORDER",
        " prototype order ",
        "prototype  order",
        "prototype\torder",
        "Prototype",
        "PROTOTYPE",
        " prototype ",
    )

    def _assert_bar_entry(self, form_id, record):
        failures = mod01.record_validation_failures(
            form_id, record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(
            failures, "scheduling_order_identifier")
        self.assertIsNotNone(entry)
        self.assertIn("prototype order bar", entry)
        self.assertIn("next step:", entry)

    def test_form1_variants_draw_named_bar_entry(self):
        for variant in self.VARIANTS:
            with self.subTest(variant=variant):
                record = mod01.minimal_valid_family_record()
                record["scheduling_order_identifier"] = variant
                self._assert_bar_entry("1", record)

    def test_form4_variants_draw_named_bar_entry(self):
        for variant in self.VARIANTS:
            with self.subTest(variant=variant):
                record = mod01.minimal_valid_instance("4")
                record["run_class"] = "headline"
                record["scheduling_order_identifier"] = variant
                self._assert_bar_entry("4", record)


class TestMissingSpellingNaming(unittest.TestCase):
    """The missing spelling limb of ruling T16-40, the
    F2-09 edge fault: a Form 1 record with one completeness
    prose spelling deleted draws a named entry for the
    field, where the standing classes draw named entries."""

    def test_each_prose_spelling_deleted_names_its_field(self):
        for prose, slug in mod01.COMPLETENESS_KEY_PAIRS:
            with self.subTest(prose=prose):
                record = mod01.minimal_valid_family_record()
                del record[prose]
                failures = mod01.record_validation_failures(
                    "1", record)
                self.assertTrue(failures)
                for entry in failures:
                    self.assertNotIn(
                        GENERIC_FALLBACK_WORDING, entry)
                entry = _named_entry(failures, slug)
                self.assertIsNotNone(entry)
                self.assertIn(prose, entry)
                self.assertIn("next step:", entry)


class TestStandingNamedClassesKept(unittest.TestCase):
    """Controls: the classes fix wave 2 already named keep
    their standing wording under this cure."""

    def test_placeholder_pair_keeps_standing_wording(self):
        record = mod01.minimal_valid_family_record()
        record["farm_size_steps"] = "stated value"
        record["farm size steps"] = "stated value"
        failures = mod01.record_validation_failures("1", record)
        entry = _named_entry(failures, "farm_size_steps")
        self.assertIsNotNone(entry)
        self.assertIn("placeholder", entry)
        self.assertIn("next step:", entry)

    def test_diverged_pair_keeps_standing_wording(self):
        record = mod01.minimal_valid_family_record()
        record["farm_size_steps"] = "one supplied text"
        record["farm size steps"] = "a different supplied text"
        failures = mod01.record_validation_failures("1", record)
        entry = _named_entry(failures, "farm_size_steps")
        self.assertIsNotNone(entry)
        self.assertIn("diverged", entry)
        self.assertIn("next step:", entry)

    def test_literal_bar_keeps_standing_wording(self):
        record = mod01.minimal_valid_family_record()
        record["scheduling_order_identifier"] = "prototype order"
        failures = mod01.record_validation_failures("1", record)
        entry = _named_entry(
            failures, "scheduling_order_identifier")
        self.assertIsNotNone(entry)
        self.assertIn("prototype order", entry)
        self.assertIn("bar", entry)
        self.assertIn("next step:", entry)

    def test_valid_records_still_draw_no_entries(self):
        for form_id in SCAN_FORM_IDS:
            with self.subTest(form_id=form_id):
                record = mod01.minimal_valid_instance(form_id)
                self.assertEqual(
                    mod01.record_validation_failures(
                        form_id, record),
                    [])


if __name__ == "__main__":
    unittest.main()
