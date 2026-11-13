"""Test group TG-01.1. Required field completeness, one test per record form.

Slice S-01, MOD-01 Types and validation. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod01, and
records whether the surface stands. While the surface stands absent, each non
gated test fails with a message naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
The census is the adopted census of plan section 3: 38 record forms, Forms 1
to 37 and Form 13A, plus the decided ViewRecord counted beside the 38. Test
group TG-01.1 runs no required field test on the ViewRecord, as plan section
3 section 4.2 item 7 states; its coverage stands gated at TG-11.1 only.
Forms 36 and 37 run on their landed field lists only, 8 fields for Form 36
EventLog and 3 fields for Form 37 DailySnapshot, in the transliteration the
suite uses for those lists. Their remainder stands gated in this file.
"""
import unittest

try:
    from crucible import mod01
    SURFACE = mod01
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-01.1"

# Each entry: form identifier, form name, fixture basis note.
FORMS = (
    ("1", "SweepFamilyRecord", "the brief field list for that form at Shape 1"),
    ("2", "SweepPoint", "the brief field list for that form at Shape 2"),
    ("3", "AssumptionRecord", "the brief field list for that form at Shape 3, no field optional"),
    ("4", "RunRecord", "the brief field list for that form at Shape 4, in its seven groups"),
    ("5", "SeedDerivationInput", "the field list for that form at Shape 5, in its recommended form only"),
    ("6", "StreamSet", "the inventory for that form at Shape 6, in its recommended form only"),
    ("7", "AgentState", "the brief field list for that form at Shape 7"),
    ("8", "VouchEdge", "the brief field list for that form at Shape 8, first form"),
    ("9", "GraphSnapshot", "the brief field list for that form at Shape 8, second form"),
    ("10", "EscrowContractState", "the brief field list for that form at Shape 9"),
    ("11", "AdjudicationCase", "the brief field list for that form at Shape 10"),
    ("12", "DetectionState", "the brief field list for that form at Shape 11"),
    ("13", "CheckpointManifest", "the brief field list for that form at Shape 12"),
    ("13A", "CheckpointState", "the field list for that form at its landing text in plan section 3"),
    ("14", "DailyAggregates", "the brief field list for that form at Shape 13"),
    ("15", "JointOutcomeVector", "the brief field list for that form at Shape 14"),
    ("16", "HeadlineResultUnit", "the brief field list for that form at Shape 15, fourteen fields, every field required"),
    ("17", "AnchorScenarioRecord", "the brief field list for that form at Shape 16, exactly three values"),
    ("18", "InterpretationLogEntry", "the brief field list for that form at Shape 17"),
    ("19", "DetectionInput", "the field list for that form defined inside Shape 7, and nothing else"),
    ("20", "AnnotationRecord", "the closed field list for that form in the Shape 16 passage"),
    ("21", "AnnotationCheckRecord", "the closed field list for that form in the Shape 16 passage"),
    ("22", "SweepFamilyRegistry", "the field list for that form at brief section 2.4"),
    ("23", "FamilyManifest", "the contents the brief supports for that form, and no further field list"),
    ("24", "SweepManifest", "the contents the brief supports for that form, and no further field list"),
    ("25", "PilotRecord", "the contents by use the brief supports for that form"),
    ("26", "SummaryRecord", "the duties the brief loads on that form, as plan section 3 states them"),
    ("27", "DetectionOutput", "the brief stated payload for that form at Contract F"),
    ("28", "ReplicationVerdictRecord", "the brief stated fields for that form at Contract J"),
    ("29", "TracerPassageRecord", "the brief stated contents for that form at Contract D"),
    ("30", "GatePassingShareRecord", "the brief stated contents for that form at the logging duty passage"),
    ("31", "ReadingLoadPricingRecord", "the contents the brief supports for that form"),
    ("32", "SettingsLineageTestRecord", "the contents the brief supports for that form"),
    ("33", "RetentionRecord", "the contents the brief supports for that form at the retention criterion"),
    ("34", "DisagreementCatalogue", "the contents the brief supports for that form at Contract J; no field list is stated in the brief and none is invented here"),
    ("35", "WeeklyContainer", "the contents the brief supports for that form; no field list beyond the units it holds is stated"),
    ("36", "EventLog", "the landed field list for that form in plan section 3, 8 fields, and no part beyond that list"),
    ("37", "DailySnapshot", "the landed field list for that form in plan section 3, 3 fields, and no part beyond that list"),
)

EVENTLOG_LANDED_FIELDS = (
    "run_identifier",
    "journal_position",
    "event_identifier",
    "simulated_day",
    "event_imported_row_form",
    "agent_identifier",
    "superseded_from_journal_position",
    "resume_attempt_identifier",
)
DAILY_SNAPSHOT_LANDED_FIELDS = (
    "run_identifier",
    "simulated_day",
    "daily_state_as_delivered",
)


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


def make_eventlog_test():
    def test(self):
        behaviour = (
            "required field absence fails validation for Form 36 EventLog, split by entry kind, "
            "and the run that produced it is not reportable"
        )
        require_surface(self, behaviour, "form_fields", "minimal_valid_instance", "validate_record", "run_is_reportable")
        # The landed list stands asserted as the form field list of Form 36,
        # not as one unconditional required set.
        self.assertEqual(tuple(SURFACE.form_fields("36")), EVENTLOG_LANDED_FIELDS)
        ordinary_entry_fields = (
            "journal_position",
            "event_identifier",
            "simulated_day",
            "event_imported_row_form",
        )
        conditional_fields = (
            "agent_identifier",
            "superseded_from_journal_position",
            "resume_attempt_identifier",
        )
        # The log field and the ordinary entry fields stand required on an
        # ordinary instance: deleting any one of them fails validation.
        self.assertTrue(SURFACE.validate_record("36", SURFACE.minimal_valid_instance("36", entry_kind="ordinary")))
        for field in ("run_identifier",) + ordinary_entry_fields:
            instance = SURFACE.minimal_valid_instance("36", entry_kind="ordinary")
            del instance[field]
            self.assertFalse(
                SURFACE.validate_record("36", instance),
                "Form 36 accepted an ordinary entry with required field absent: " + str(field),
            )
            self.assertFalse(SURFACE.run_is_reportable("36", instance))
        # Absence side of both conditions: an ordinary entry is a non agent
        # entry and no supersession entry, so it validates with every
        # conditional field absent.
        for field in conditional_fields:
            instance = SURFACE.minimal_valid_instance("36", entry_kind="ordinary")
            instance.pop(field, None)
            self.assertTrue(
                SURFACE.validate_record("36", instance),
                "Form 36 rejected an ordinary entry for the absence of conditional field: " + str(field),
            )
        # Field 6 stands required on an agent entry: deleting it fails.
        agent = SURFACE.minimal_valid_instance("36", entry_kind="agent")
        self.assertIn("agent_identifier", agent)
        del agent["agent_identifier"]
        self.assertFalse(SURFACE.validate_record("36", agent))
        # Fields 7 and 8 stand required on a supersession entry only:
        # deleting either one fails.
        for field in ("superseded_from_journal_position", "resume_attempt_identifier"):
            instance = SURFACE.minimal_valid_instance("36", entry_kind="supersession")
            self.assertIn(field, instance)
            del instance[field]
            self.assertFalse(
                SURFACE.validate_record("36", instance),
                "Form 36 accepted a supersession entry with required field absent: " + str(field),
            )

    test.__doc__ = (
        "Fixture: minimally valid instances of Form 36 EventLog by entry kind (an ordinary entry, an agent entry, and a supersession entry), derived from the landed field list for that form in plan section 3, Form 36, item 1, with one required field removed per run.\n"
        "Pins: the landed list stands as the form field list of Form 36, not as one unconditional required set; the log field and the ordinary entry fields stand required on an ordinary instance; field 6, agent identifier, stands required on an agent entry and its absence stands accepted on a non agent entry; fields 7 and 8 stand required on a supersession entry only; one case stands on each side of each condition; a record with a required field absent fails validation, and the run that produced it is not reportable, on its landed list only, the remainder of the form standing gated in this file.\n"
        "Bar: no form may treat a required field as optional by silence, and no conditional field stands required where its stated condition does not hold.\n"
        "Failure: while the surface stands absent the test fails naming this behaviour and TG-01.1; with the surface present, a form accepting a record with a required field absent in the entry kind that requires it fails."
    )
    return test


def make_required_field_test(form_id, form_name, basis):
    if form_id == "36":
        return make_eventlog_test()

    def test(self):
        behaviour = (
            "required field absence fails validation for Form " + form_id
            + " " + form_name + ", and the run that produced it is not reportable"
        )
        require_surface(self, behaviour, "required_fields", "minimal_valid_instance", "validate_record", "run_is_reportable")
        fields = tuple(SURFACE.required_fields(form_id))
        self.assertTrue(fields, "no required fields stated for Form " + form_id)
        if form_id == "37":
            self.assertEqual(fields, DAILY_SNAPSHOT_LANDED_FIELDS)
        for field in fields:
            instance = SURFACE.minimal_valid_instance(form_id)
            del instance[field]
            self.assertFalse(
                SURFACE.validate_record(form_id, instance),
                "Form " + form_id + " accepted with required field absent: " + str(field),
            )
            self.assertFalse(SURFACE.run_is_reportable(form_id, instance))
        # A conditional field is required exactly where its stated condition
        # holds: one case on each side of every stated condition for the form.
        for condition in getattr(SURFACE, "field_conditions", lambda f: ())(form_id):
            holding = SURFACE.minimal_valid_instance(form_id, condition_holds=condition)
            del holding[condition["field"]]
            self.assertFalse(SURFACE.validate_record(form_id, holding))
            not_holding = SURFACE.minimal_valid_instance(form_id, condition_holds=None)
            not_holding.pop(condition["field"], None)
            self.assertTrue(SURFACE.validate_record(form_id, not_holding))

    pins = (
        "Pins: a record with a required field absent fails validation, and the run that produced it is not reportable, under the general rule at the head of brief section 5.3; a conditional field is required exactly where its stated condition holds, with one case on each side of every stated condition"
    )
    if form_id in ("36", "37"):
        pins += " on its landed list only, the remainder of the form standing gated in this file."
    elif form_id in ("34", "35"):
        pins += ". Coverage for this form stands at contents level only under defect M-S01-01, on the contents the brief supports for the form, and claims no field level coverage for the form."
    else:
        pins += "."
    test.__doc__ = (
        "Fixture: a minimally valid instance of Form " + form_id + " " + form_name
        + ", derived from " + basis + ", with one required field removed per run.\n"
        + pins + "\n"
        "Bar: no form may treat a required field as optional by silence.\n"
        "Failure: while the surface stands absent the test fails naming this behaviour and TG-01.1; with the surface present, a form accepting a record with a required field absent fails."
    )
    return test


class TestRequiredFieldCompleteness(unittest.TestCase):
    pass


for _form_id, _form_name, _basis in FORMS:
    _test = make_required_field_test(_form_id, _form_name, _basis)
    _name = "test_required_field_absence_form_" + _form_id.lower().replace("a", "a")
    setattr(TestRequiredFieldCompleteness, _name, _test)
del _form_id, _form_name, _basis, _test, _name


class TestForms36And37Remainder(unittest.TestCase):
    def test_forms_36_37_free_parts_on_landed_lists(self):
        """Fixture: minimally valid instances of Form 36 EventLog and Form 37 DailySnapshot on their landed lists, as mod01 now builds them, with one landed field removed per run; a minimally valid instance of Form 13 CheckpointManifest and of Form 14 DailyAggregates for the free limbs at exclusions 8 and 11.
        Pins: the allocated form of the remainder under the Manager ruling at Entry 1 (M-FL1-1) of design/steps/step-14-manager-rulings.md. The landed lists stand exercised: Form 36 carries 8 fields and Form 37 carries 3 fields, exactly the lists in this file; deleting a field the landed list requires fails validation and the record is not reportable. Exclusion 1 (hash and digest fields) bars no part of TG-01.1, so no gated test stands for it in this class and the landed lists stand exercised without any hash or digest field. Field 5 of Form 36 itself and Field 3 of Form 37 itself stand free and exercised as landed fields, while their internals and subfields stand gated at exclusions 2 and 7. The fields exclusion 8 names stand as Form 13 fields and the Form 13 instance stands exercised, as the ruling states Form 13 tests stand free. The daily aggregates stand as Form 14 and the Form 14 instance stands exercised, as the ruling states their tests stand free there.
        Bar: no field beyond the landed lists is invented or exercised in this test; a suite summary counting either form as covered in full fails this group, because the barred parts in the gated tests of this class stand open under OP-18 BLOCKED-CARRIED.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.1; with the surface present, a landed list differing from the lists in this file, or an instance validating with a required landed field absent, fails.
        """
        behaviour = (
            "the parts of Forms 36 and 37 the Manager ruling at Entry 1 (M-FL1-1) states free at TG-01.1 "
            "stand exercised on the landed lists, 8 fields for Form 36 and 3 fields for Form 37"
        )
        require_surface(self, behaviour, "form_fields", "required_fields", "minimal_valid_instance", "validate_record", "run_is_reportable")
        self.assertEqual(tuple(SURFACE.form_fields("36")), EVENTLOG_LANDED_FIELDS)
        self.assertEqual(len(EVENTLOG_LANDED_FIELDS), 8)
        self.assertEqual(tuple(SURFACE.form_fields("37")), DAILY_SNAPSHOT_LANDED_FIELDS)
        self.assertEqual(len(DAILY_SNAPSHOT_LANDED_FIELDS), 3)
        for field in EVENTLOG_LANDED_FIELDS + DAILY_SNAPSHOT_LANDED_FIELDS:
            self.assertNotIn("hash", field)
            self.assertNotIn("digest", field)
        self.assertTrue(SURFACE.validate_record("36", SURFACE.minimal_valid_instance("36", entry_kind="ordinary")))
        for field in ("run_identifier", "journal_position", "event_identifier", "simulated_day", "event_imported_row_form"):
            instance = SURFACE.minimal_valid_instance("36", entry_kind="ordinary")
            del instance[field]
            self.assertFalse(
                SURFACE.validate_record("36", instance),
                "Form 36 accepted an ordinary entry with free landed field absent: " + str(field),
            )
            self.assertFalse(SURFACE.run_is_reportable("36", instance))
        self.assertTrue(SURFACE.validate_record("37", SURFACE.minimal_valid_instance("37")))
        self.assertEqual(tuple(SURFACE.required_fields("37")), DAILY_SNAPSHOT_LANDED_FIELDS)
        for field in DAILY_SNAPSHOT_LANDED_FIELDS:
            instance = SURFACE.minimal_valid_instance("37")
            del instance[field]
            self.assertFalse(
                SURFACE.validate_record("37", instance),
                "Form 37 accepted with free landed field absent: " + str(field),
            )
            self.assertFalse(SURFACE.run_is_reportable("37", instance))
        form_13_fields = tuple(SURFACE.form_fields("13"))
        for field in ("full_state_hash", "generator_state_per_stream", "journal_position", "rule_version_set"):
            self.assertIn(field, form_13_fields)
        self.assertTrue(SURFACE.validate_record("13", SURFACE.minimal_valid_instance("13")))
        self.assertTrue(SURFACE.validate_record("14", SURFACE.minimal_valid_instance("14")))

    def test_exclusion_02_imported_row_internals_gated(self):
        """Fixture: no fixture stands for the row internals of Form 36 Field 5.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 2, the imported event row internals at Form 36 Field 5: field tests and unknown field tests for the row internals only. Field 5 itself as a landed field stands free and stands exercised in test_forms_36_37_free_parts_on_landed_lists.
        Bar: a test resting on the row internals while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 2 (imported event row internals, Form 36 Field 5): TG-01.1 field and unknown field tests for Field 5 row internals only stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_03_completeness_statement_gated(self):
        """Fixture: no fixture stands for the form of the EventLog completeness statement.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 3, the EventLog completeness statement form: tests asserting the log own completeness statement. The position check stands free at contract C-11 under the ruling, and the landed field tests in this group stand free.
        Bar: a test asserting the log own completeness statement in any form while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 3 (EventLog completeness statement form): TG-01.1 tests asserting the log own completeness statement stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_04_stream_position_gated(self):
        """Fixture: no fixture stands for stream position as an entry field of Form 36.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 4, stream position as an entry field: tests naming stream position. The landed field journal_position is a distinct field, stands free, and stands exercised in test_forms_36_37_free_parts_on_landed_lists; the append audit stands free at contract C-11 under the ruling.
        Bar: a test naming stream position as an entry field while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 4 (stream position as an entry field): TG-01.1 tests naming stream position stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_05_retention_tier_and_store_kind_gated(self):
        """Fixture: no fixture stands for a retention tier field or a store kind field on Form 36 or Form 37.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 5, retention tier and store kind fields: field tests for those two fields on both forms. Contract C-11 stands free under the ruling, and the other landed field tests in this group stand free.
        Bar: a field test for a retention tier field or a store kind field on either form while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 5 (retention tier and store kind fields): TG-01.1 field tests for those two fields on both forms stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_06_time_fields_gated(self):
        """Fixture: no fixture stands for a wall clock, timestamp or date of writing field on Form 36 or Form 37.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 6, wall clock, timestamp and date of writing: time field tests on both forms. The append audit and the position check stand free at contract C-11 under the ruling, and the other landed field tests in this group stand free.
        Bar: a time field test on either form while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 6 (wall clock, timestamp, date of writing): TG-01.1 time field tests on both forms stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_07_daily_state_subfields_gated(self):
        """Fixture: no fixture stands inside Form 37 Field 3 for the subfields of the daily state.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 7, the DailySnapshot daily state subfields at Form 37 Field 3: tests inside Field 3. Field 3 itself as a landed field stands free and stands exercised in test_forms_36_37_free_parts_on_landed_lists, and contract C-11 stands free under the ruling.
        Bar: a test inside Field 3 while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 7 (DailySnapshot daily state subfields, Form 37 Field 3): TG-01.1 tests inside Field 3 stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_08_form_37_checkpoint_fields_gated(self):
        """Fixture: no fixture stands for generator state, a rule version set, a full state hash, a journal position or a last event identifier as fields of Form 37.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 8: tests naming those fields on Form 37. Those fields stand as Form 13 fields, Form 13 tests stand free under the ruling, and the Form 13 instance stands exercised in test_forms_36_37_free_parts_on_landed_lists.
        Bar: a test naming any of those fields as a field of Form 37 while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 8 (generator state, rule version set, full state hash, journal position, last event identifier on Form 37): TG-01.1 tests naming those fields on Form 37 stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_09_viewer_identifier_gated(self):
        """Fixture: no fixture stands for a viewer identifier or a per viewer form on Form 37.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 9, a viewer identifier and a per viewer form on Form 37: per viewer tests for Form 37. Contract C-11 stands free under the ruling, and the other landed field tests for Form 37 stand free.
        Bar: a per viewer test for Form 37 while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 9 (viewer identifier and per viewer form on Form 37): TG-01.1 per viewer tests for Form 37 stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_10_intra_day_edge_count_gated(self):
        """Fixture: no fixture stands for the count of intra day only edges as a field of Form 37.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 10, the intra day only edge count on Form 37: tests for that count field. The computation of that count elsewhere stands free under the ruling, and contract C-11 stands free.
        Bar: a test for that count field on Form 37 while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 10 (intra day only edge count on Form 37): TG-01.1 tests for that count field stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )

    def test_exclusion_11_daily_aggregate_contents_gated(self):
        """Fixture: no fixture stands for daily aggregate contents as fields of Form 37.
        Pins: no behaviour; this test records, in allocated form, only the part the ruling bars at TG-01.1 for exclusion 11, daily aggregate contents on Form 37: tests treating aggregates as Form 37 fields. The aggregates stand as Form 14, their tests stand free there under the ruling, and the Form 14 instance stands exercised in test_forms_36_37_free_parts_on_landed_lists.
        Bar: a test treating an aggregate as a field of Form 37 while OP-18 stands BLOCKED-CARRIED on this exclusion fails this group.
        Failure: gated form only; this test never passes while the exclusion stands open.
        """
        self.skipTest(
            "gated in allocated form under Manager ruling Entry 1 (M-FL1-1) at design/steps/step-14-manager-rulings.md, exclusion 11 (daily aggregate contents on Form 37): TG-01.1 tests treating aggregates as Form 37 fields stand gated; OP-18 BLOCKED-CARRIED, the exclusion stands open"
        )


class TestUnknownFieldRejection(unittest.TestCase):
    def test_unknown_field_rejection_headline_result_unit(self):
        """Fixture: a valid HeadlineResultUnit instance carrying one field the form does not name; no inventory fixture, the basis is the closed unit form at Shape 15.
        Pins: the HeadlineResultUnit, the one form a source states as closed, at Shape 15 in its closed unit form, rejects unnamed fields.
        Bar: closedness for every other form in the census stands unstated and carried as unstated; no test in this group extends the closed form rule to any other form until a source states that form as closed.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.1; with the surface present, a HeadlineResultUnit accepting an unnamed field fails.
        """
        behaviour = "HeadlineResultUnit rejects unnamed fields, as the one closed form at Shape 15"
        require_surface(self, behaviour, "minimal_valid_instance", "validate_record")
        instance = SURFACE.minimal_valid_instance("16")
        instance["field_the_form_does_not_name"] = "value"
        self.assertFalse(SURFACE.validate_record("16", instance))

    def test_unknown_field_range_kind_in_f01_position_rejected(self):
        """Fixture: F-01, the centre only headline unit, whose extra Range kind field is the standing example of this failure.
        Pins: the extra Range kind field in fixture F-01 is rejected in that position as well.
        Bar: the F-01 tally stands as the brief states it, 3 checks passed, 9 checks failed, and 3 checks not applicable of 15 checks, and is never merged with the F-02 tally.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-01.1; with the surface present, acceptance of the Range kind field in the F-01 position fails.
        """
        behaviour = "the extra Range kind field in fixture F-01 is rejected in its position"
        require_surface(self, behaviour, "minimal_valid_instance", "validate_record")
        instance = SURFACE.minimal_valid_instance("16")
        instance["range_kind"] = "value"
        self.assertFalse(SURFACE.validate_record("16", instance))


if __name__ == "__main__":
    unittest.main()
