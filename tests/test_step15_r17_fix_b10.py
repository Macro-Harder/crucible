"""Pins for fix wave 16, Builder 10, rows R16-060 to R16-074.

Each charged row carries at least one pin proving the defect on
the pristine tree: a rendering limb rendering a handed value
through its plain str or repr reading, so a value whose reading
raises escapes bare in place of the act own named sentence.
Controls beside each defect pin keep the plain control wording
exact, so a cure that changes the plain sentence fails here.
"""
import unittest

from crucible import mod01, mod02, mod03, mod04, mod05, mod07
from crucible import mod08, mod09, mod10, mod11, mod12, mod14, mod16


class ReprBad:
    def __repr__(self):
        raise RuntimeError("repr boom")

    def __str__(self):
        return "reprbad text"


class StrBad:
    def __str__(self):
        raise RuntimeError("str boom")

    def __repr__(self):
        return "strbad repr"


class BothBad:
    def __str__(self):
        raise RuntimeError("str boom")

    def __repr__(self):
        raise RuntimeError("repr boom")


class StrSubBad(str):
    def __new__(cls, text):
        return str.__new__(cls, text)

    def __str__(self):
        raise RuntimeError("str boom")

    def __repr__(self):
        raise RuntimeError("repr boom")


def headline_values():
    values = {field: "value for " + field
              for field in mod11.HEADLINE_UNIT_FIELDS
              if field not in ("checkability_fields",
                               "run_registry_line")}
    values["claim_sentence"] = (
        "At the sampled points within the stated scope, the "
        "result holds for the sampled points only, and nothing "
        "is claimed beyond the stated limits.")
    values["grounding_sentence"] = (
        "This unit rests on the retained run records within "
        "the stated scope, and its limits are that nothing is "
        "claimed beyond the sampled points in this unit.")
    values["qualifiers_and_markings_block"] = (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording "
        "that DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes "
        "Parley Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: no anchor scenario is "
        "used in this unit.")
    return values


class TestR16060ViewGuardPath(unittest.TestCase):
    def test_build_view_record_bad_key_builds(self):
        record = mod04.build_view_record(
            contents=[{StrSubBad("k"): 1}])
        self.assertIsInstance(record, dict)

    def test_hold_view_bad_key_holds(self):
        held = mod04.hold_view({StrSubBad("k"): 1})
        self.assertTrue(held["held"])

    def test_write_checkpoint_bad_key_writes(self):
        with self.assertRaises(mod04.NamedFailure) as cm:
            mod04.write_checkpoint({StrSubBad("k"): 1})
        self.assertIn("no checkpoint stands written",
                      str(cm.exception))

    def test_per_viewer_bad_key_returns(self):
        result = mod04.per_viewer_components(
            components=[{StrSubBad("k"): 1}])
        self.assertEqual(len(result), 1)

    def test_control_plain_key_and_depth_sentence(self):
        record = mod04.build_view_record(contents=[{"k": 1}])
        self.assertIsInstance(record, dict)
        deep = current = []
        for _ in range(105):
            nxt = []
            current.append(nxt)
            current = nxt
        with self.assertRaises(Exception) as cm:
            mod04.build_view_record(contents=[deep])
        self.assertIn("no view record or copy stands",
                      str(cm.exception))


class _FailureProp:
    @property
    def failure(self):
        raise RuntimeError("attr boom")


class _GateProp:
    @property
    def gate(self):
        raise RuntimeError("attr boom")


class TestR16061ErrorCarriageGetattr(unittest.TestCase):
    def test_failure_property_carried(self):
        carriage = mod14.error_carriage(_FailureProp())
        self.assertTrue(carriage["operator_sees_failure"])

    def test_gate_property_carried(self):
        carriage = mod14.error_carriage(_GateProp())
        self.assertTrue(carriage["operator_sees_failure"])

    def test_control_plain_exception(self):
        carriage = mod14.error_carriage(ValueError("plain boom"))
        self.assertIn("plain boom", carriage["failure"])


class TestR16062ErrorCarriageTextBranch(unittest.TestCase):
    def test_text_subclass_bad_carriage_renders(self):
        bad = StrSubBad("hello")
        carriage = mod14.error_carriage(bad)
        self.assertEqual(carriage["failure"], "hello")
        self.assertIs(type(carriage["failure_value"]["message"]), str)
        self.assertIn("hello", repr(carriage))

    def test_control_plain_text(self):
        carriage = mod14.error_carriage("hello")
        self.assertEqual(carriage["failure"], "hello")
        self.assertEqual(carriage["failure_value"]["message"], "hello")


class TestR16063Adjudicate(unittest.TestCase):
    def _args(self, **kw):
        args = dict(case={}, accuracy_value=0.5, assumption_set="a",
                    row="r", error_direction="d", outcome=None)
        args.update(kw)
        return args

    def test_accuracy_repr_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod05.adjudicate(**self._args(accuracy_value=ReprBad()))
        self.assertIn("in no numeric form", str(cm.exception))

    def test_outcome_repr_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod05.adjudicate(**self._args(outcome=ReprBad()))
        self.assertIn("outside the stated", str(cm.exception))

    def test_controls_exact(self):
        with self.assertRaises(ValueError) as cm:
            mod05.adjudicate(**self._args(accuracy_value="abc"))
        self.assertIn("in no numeric form: 'abc'", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            mod05.adjudicate(**self._args(outcome="bogus"))
        self.assertIn("vocabulary: 'bogus'", str(cm.exception))


class TestR16064Mod03StrSites(unittest.TestCase):
    def test_build_cast_mix_count_bad_identifier(self):
        point = {"population_size": 1,
                 "archetype_mix": {StrSubBad("a1"): "x"}}
        with self.assertRaises(Exception) as cm:
            mod03.build_cast(point, [], strategy_class="fixed")
        self.assertIn("mix count for", str(cm.exception))

    def test_build_cast_outside_records_bad_identifier(self):
        point = {"population_size": 1,
                 "archetype_mix": {StrSubBad("zz"): 1}}
        with self.assertRaises(Exception) as cm:
            mod03.build_cast(point, [], strategy_class="fixed")
        self.assertIn("outside", str(cm.exception))

    def test_catalogue_duplicate_bad_identifier(self):
        bad = StrSubBad("a1")
        records = [{"archetype_id": bad}, {"archetype_id": bad}]
        with self.assertRaises(ValueError) as cm:
            mod03.archetype_catalogue(records)
        self.assertIn("duplicate archetype identifier",
                      str(cm.exception))

    def test_control_duplicate_plain_str_form(self):
        records = [{"archetype_id": "a1"}, {"archetype_id": "a1"}]
        with self.assertRaises(ValueError) as cm:
            mod03.archetype_catalogue(records)
        self.assertIn("stands in the record set: a1",
                      str(cm.exception))


class TestR16065WitnessCarriage(unittest.TestCase):
    def test_witness_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.witness_carriage(ReprBad())
        self.assertIn("no record form", str(cm.exception))
        self.assertNotIsInstance(cm.exception, RuntimeError)

    def test_control_plain_int(self):
        with self.assertRaises(Exception) as cm:
            mod09.witness_carriage(42)
        self.assertIn("no record form: 42", str(cm.exception))


class TestR16066WinningRegime(unittest.TestCase):
    def test_winning_entry_not_pair(self):
        with self.assertRaises(Exception) as cm:
            mod12.winning_regime([ReprBad()] * 30)
        self.assertIn("not an attacker and honest pair",
                      str(cm.exception))

    def test_winning_entry_non_numeric(self):
        with self.assertRaises(Exception) as cm:
            mod12.winning_regime([[ReprBad(), 1]] * 30)
        self.assertIn("non numeric share", str(cm.exception))

    def test_top_up_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod12.top_up_applies(ReprBad(), 30)
        self.assertIn("not numbers", str(cm.exception))

    def test_controls_exact(self):
        with self.assertRaises(Exception) as cm:
            mod12.winning_regime([123] * 30)
        self.assertIn("pair: 123", str(cm.exception))
        with self.assertRaises(Exception) as cm:
            mod12.top_up_applies("x", 30)
        self.assertIn("('x', 30)", str(cm.exception))


class TestR16067Tracer(unittest.TestCase):
    def test_result_str_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod07.make_tracer_passage_record(
                "item", "point", "what passed", StrBad())
        self.assertIn("tracer result outside the stated set",
                      str(cm.exception))

    def test_records_run_id_str_bad(self):
        records = mod07.tracer_passage_records(StrBad())
        self.assertEqual(len(records), len(mod07.OPEN_SEMANTIC_ITEMS))

    def test_control_plain_bogus_result(self):
        with self.assertRaises(ValueError) as cm:
            mod07.make_tracer_passage_record(
                "item", "point", "what passed", "bogus")
        self.assertIn("outside the stated set: bogus;",
                      str(cm.exception))


class TestR16068Mod16(unittest.TestCase):
    def test_exercise_run_class_str_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod16.exercise_run_class(StrBad())
        self.assertIn("unknown run class", str(cm.exception))

    def test_fixture_lookup_construction_str_bad(self):
        bad = StrBad()
        failure = mod16.FixtureLookupFailure(bad)
        self.assertIn("fixture lookup failure", str(failure))
        self.assertEqual(failure.failure["name"],
                         "fixture lookup failure")

    def test_fixture_record_str_bad(self):
        with self.assertRaises(mod16.FixtureLookupFailure):
            mod16.fixture_record(StrBad())

    def test_controls_exact(self):
        with self.assertRaises(ValueError) as cm:
            mod16.exercise_run_class("bogus")
        self.assertEqual(str(cm.exception), "unknown run class: bogus")
        failure = mod16.FixtureLookupFailure("F-99")
        self.assertIn("fixture lookup failure: F-99", str(failure))


class TestR16069Mod09Rendering(unittest.TestCase):
    def test_readout_carriage_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.readout({"run_record": ReprBad()})
        self.assertIn("no record form", str(cm.exception))
        self.assertNotIsInstance(cm.exception, RuntimeError)

    def test_readout_exercised_repr_bad(self):
        record = {"run_record": {
            "ladder_position": 0,
            "strategies_exercised": ReprBad()}}
        with self.assertRaises(Exception) as cm:
            mod09.readout(record)
        self.assertIn("no list form", str(cm.exception))

    def test_readout_swept_repr_bad(self):
        record = {"run_record": {"ladder_position": 0,
                                 "strategies_exercised": []},
                  "external_profit_swept_values": ReprBad()}
        with self.assertRaises(Exception) as cm:
            mod09.readout(record)
        self.assertIn("no list form", str(cm.exception))

    def test_carriage_class_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.run_record_carriage(ReprBad(), 0, "v", "p", "1")
        self.assertIn("no class list form", str(cm.exception))

    def test_carriage_strategies_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.run_record_carriage(
                ["a"], 0, "v", "p", "1", strategies=ReprBad())
        self.assertIn("in no list form", str(cm.exception))

    def test_carriage_ladder_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.run_record_carriage(["a"], ReprBad(), "v", "p", "1")
        self.assertIn("whole rungs 0 to 6", str(cm.exception))

    def test_sweep_strategy_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.sweep_external_profit(ReprBad())
        self.assertIn("in no record form", str(cm.exception))
        self.assertNotIsInstance(cm.exception, RuntimeError)

    def test_sweep_range_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.sweep_external_profit(
                {"external_profit_range": ReprBad()})
        self.assertIn("no range form", str(cm.exception))

    def test_sweep_value_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.sweep_external_profit(
                {"external_profit_range": [ReprBad()]})
        self.assertIn("no numeric form", str(cm.exception))

    def test_sweep_largest_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod09.sweep_external_profit(
                {"external_profit_range": [0, 5],
                 "in_protocol_payoff": 1},
                largest_in_protocol_payoff=ReprBad())
        self.assertIn("no numeric form", str(cm.exception))

    def test_controls_exact(self):
        with self.assertRaises(Exception) as cm:
            mod09.readout({"run_record": 42})
        self.assertIn("no record form: 42", str(cm.exception))
        with self.assertRaises(Exception) as cm:
            mod09.sweep_external_profit(42)
        self.assertIn("in no record form: 42", str(cm.exception))


class TestR16070AcceptDetectionInput(unittest.TestCase):
    def _record(self, **kw):
        record = {"agent_identifier": "a1", "day": 1,
                  "feature_values": {}}
        record.update(kw)
        return record

    def test_identifier_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod08.accept_detection_input(
                self._record(agent_identifier=ReprBad()))
        self.assertIn("identifier form", str(cm.exception))
        self.assertNotIsInstance(cm.exception, RuntimeError)

    def test_day_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod08.accept_detection_input(self._record(day=ReprBad()))
        self.assertIn("day form", str(cm.exception))

    def test_outside_field_str_bad_key(self):
        record = self._record()
        record[StrSubBad("zzz")] = 1
        with self.assertRaises(Exception) as cm:
            mod08.accept_detection_input(record)
        self.assertIn("fields outside DetectionInput",
                      str(cm.exception))

    def test_feature_name_repr_bad(self):
        record = self._record(feature_values={ReprBad(): 1})
        with self.assertRaises(Exception) as cm:
            mod08.accept_detection_input(record)
        self.assertIn("feature name stands in no", str(cm.exception))

    def test_control_plain_identifier(self):
        with self.assertRaises(Exception) as cm:
            mod08.accept_detection_input(
                self._record(agent_identifier=42))
        self.assertIn("identifier form: 42", str(cm.exception))


class TestR16071Mod10Rendering(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def test_flag_outcome_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10.apply_flag_evaluation(
                {}, outcome=StrSubBad("bogus"))
        self.assertIn("outside the stated vocabulary",
                      str(cm.exception))
        self.assertIn("promote and demote", str(cm.exception))

    def test_flag_tier_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10.apply_flag_evaluation(
                {}, outcome=None, tier=StrSubBad("Tier 9"))
        self.assertIn("tier outside the tiers", str(cm.exception))

    def test_flag_no_rise_bad(self):
        record = {"retention_tier": "Tier 2"}
        with self.assertRaises(ValueError) as cm:
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier=StrSubBad("Tier 2"),
                inputs={"flag_conditions_fired": ["c1"]})
        self.assertIn("no effected promotion", str(cm.exception))

    def test_deferred_firing_repr_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10.apply_deferred_evaluation({}, ReprBad())
        self.assertIn("outside the stated firings", str(cm.exception))

    def test_store_lookup_kind_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10.store_lookup(store_kinds=(StrBad(),), key="k")
        self.assertIn("unknown store kind", str(cm.exception))

    def test_close_retention_tier_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10.close_run_retention("run-x", StrSubBad("Tier 9"))
        self.assertIn("unknown retention tier", str(cm.exception))

    def test_retain_gc08_kind_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10.retain_gc08_record(StrBad(), {}, "owner-1")
        self.assertIn("unknown GC-08 record kind", str(cm.exception))

    def test_recorder_store_kind_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10.RecorderStore(store_kind=StrBad())
        self.assertIn("unknown store kind", str(cm.exception))

    def test_summary_absence_bad_run_id(self):
        result = mod10.summary_record_for_run(StrBad())
        self.assertFalse(result["record_found"])
        self.assertIn("no summary record", result["statement"])

    def test_validate_retention_governing_bad(self):
        self.assertTrue(mod10.validate_retention_record(
            {"governing_rule": StrBad(), "reliance": "governing"}))

    def test_lookup_failure_bad_run_id(self):
        failure = mod10.LookupFailure(StrBad())
        self.assertIn("one lookup resolution failure", str(failure))

    def test_lookup_failure_bad_record_kind(self):
        failure = mod10.LookupFailure("run-1", record_kind=StrBad())
        self.assertIn("for record kind", str(failure))

    def test_canonical_store_kind_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod10._canonical_store_kind(StrBad())
        self.assertIn("unknown store kind", str(cm.exception))

    def test_duplicate_retention_bad_rid(self):
        store = mod10.new_store("sweep")
        bad = StrSubBad("dup-1")
        store.retain_run_record({"run_id": bad})
        with self.assertRaises(ValueError) as cm:
            store.retain_run_record({"run_id": bad})
        self.assertIn("second record for the same run is rejected",
                      str(cm.exception))

    def test_shell_flag_bad_outcome_carriage(self):
        carriage = mod14.run_command("flag_evaluation", {
            "summary_record": {}, "inputs": None,
            "outcome": StrSubBad("bogus"), "tier": "Tier 3"})
        self.assertIn("outside the stated vocabulary",
                      carriage["failure"])
        self.assertNotIn("RuntimeError", carriage["failure"])

    def test_controls_exact(self):
        with self.assertRaises(ValueError) as cm:
            mod10.apply_flag_evaluation({}, outcome="bogus")
        self.assertIn("vocabulary: bogus;", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            mod10.store_lookup(store_kinds=("bogus",), key="k")
        self.assertIn("unknown store kind: bogus;", str(cm.exception))


class TestR16072WeeklyRendering(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def _weekly_record(self, identifiers):
        return [{"week": "W1",
                 "headline_unit_identifiers": identifiers}]

    def test_mod11_weekly_scalar_repr_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod11.weekly_count(self._weekly_record([ReprBad()]), "W1")
        self.assertIn("in no unit identifier form", str(cm.exception))

    def test_mod11_weekly_container_repr_bad_counts_one(self):
        count = mod11.weekly_count(
            self._weekly_record([[ReprBad()]]), "W1")
        self.assertEqual(count, 1)

    def test_mod11_make_container_repr_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod11.make_weekly_container("W1", [ReprBad()])
        self.assertIn("weekly container stands refused",
                      str(cm.exception))

    def test_mod14_weekly_scalar_repr_bad(self):
        with self.assertRaises(Exception) as cm:
            mod14.weekly_headline_count(
                self._weekly_record([ReprBad()]), "W1")
        self.assertIn("in no unit identifier form", str(cm.exception))

    def test_mod14_weekly_container_repr_bad_counts_one(self):
        count = mod14.weekly_headline_count(
            self._weekly_record([[ReprBad()]]), "W1")
        self.assertEqual(count, 1)

    def test_quote_extra_field_str_bad_key(self):
        unit = headline_values()
        unit[StrBad()] = "extra"
        with self.assertRaises(ValueError) as cm:
            mod11.quote_headline_unit(unit)
        self.assertIn("fields beyond the closed unit",
                      str(cm.exception))

    def test_first_sentence_both_bad(self):
        bad = BothBad()
        self.assertEqual(mod11.first_sentence(bad),
                         object.__repr__(bad).split(".", 1)[0])

    def test_retirement_verdicts_str_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod11.retirement_verdicts(StrBad())
        self.assertIn("no retirement verdict stands recorded for",
                      str(cm.exception))

    def test_build_from_run_bad_run_id_named_failure(self):
        result = mod11.build_headline_unit_from_run(BothBad(), {})
        self.assertFalse(result["built"])
        self.assertEqual(result["failure"]["name"],
                         mod10.ONE_LOOKUP_FAILURE_NAME)

    def test_build_from_run_bad_store_kind_carriage(self):
        result = mod11.build_headline_unit_from_run(
            "missing-run", {}, store_kind=StrBad())
        self.assertFalse(result["built"])
        self.assertIn("unknown store kind", result["failure"]["name"])
        self.assertNotIn("RuntimeError", result["failure"]["name"])

    def test_build_from_run_bad_run_id_resolved(self):
        bad = StrSubBad("run-bad-1")
        mod10.retain_run_record(
            {"run_id": bad, "run_identifier": bad,
             "record_state": "as retained"})
        result = mod11.build_headline_unit_from_run(
            bad, headline_values())
        self.assertTrue(result["built"])

    def test_controls_plain_identifier(self):
        for act in (mod11.weekly_count, mod14.weekly_headline_count):
            with self.assertRaises(Exception) as cm:
                act(self._weekly_record([123]), "W1")
            self.assertIn("unvalidated contents: 123",
                          str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            mod11.make_weekly_container("W1", [123])
        self.assertIn("contents: 123", str(cm.exception))


class TestR16073FourModuleRendering(unittest.TestCase):
    def test_mod01_form_name_str_bad(self):
        self.assertIsNone(mod01.form_name(StrBad()))

    def test_mod01_form_fields_str_bad(self):
        self.assertEqual(mod01.form_fields(StrBad()), ())

    def test_mod01_validate_record_str_bad(self):
        self.assertFalse(mod01.validate_record(StrBad(), {}))

    def test_mod02_domain_str_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod02.make_derivation_input(domain=StrBad())
        self.assertIn("domain outside the two value vocabulary",
                      str(cm.exception))

    def test_mod02_draw_position_repr_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(position=ReprBad(),
                                   carried_positions=10)
        self.assertIn("position argument stands in no numeric form",
                      str(cm.exception))

    def test_mod02_draw_carried_repr_bad(self):
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(position=1,
                                   carried_positions=ReprBad())
        self.assertIn("carried positions argument stands in no",
                      str(cm.exception))

    def test_mod04_completeness_str_bad(self):
        with self.assertRaises(Exception) as cm:
            mod04.build_view_record(completeness=StrSubBad("bogus"))
        self.assertIn("completeness state outside the closed",
                      str(cm.exception))

    def test_mod08_conformance_table_str_bad(self):
        with self.assertRaises(Exception) as cm:
            mod08.conformance_statement(table_identifier=StrBad())
        self.assertIn("names no recorded table", str(cm.exception))

    def test_mod08_conformance_threshold_str_bad(self):
        with self.assertRaises(Exception) as cm:
            mod08.conformance_statement(threshold_set=StrBad())
        self.assertIn("no recorded threshold set", str(cm.exception))

    def test_mod08_score_mode_str_bad(self):
        with self.assertRaises(Exception) as cm:
            mod08.score_day([], mode=StrBad())
        self.assertIn("scoring mode stands unnamed", str(cm.exception))

    def test_mod08_score_use_str_bad(self):
        with self.assertRaises(Exception) as cm:
            mod08.score_day([], mode="conformance", uses=[StrBad()])
        self.assertIn("scoring use stands unnamed", str(cm.exception))

    def test_controls_exact(self):
        with self.assertRaises(ValueError) as cm:
            mod02.make_derivation_input(domain="bogus")
        self.assertIn("vocabulary: bogus;", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(position="abc", carried_positions=10)
        self.assertIn("no numeric form: 'abc'", str(cm.exception))
        with self.assertRaises(Exception) as cm:
            mod04.build_view_record(completeness="bogus")
        self.assertIn("vocabulary: bogus", str(cm.exception))
        with self.assertRaises(Exception) as cm:
            mod08.conformance_statement(table_identifier="bogus")
        self.assertIn("recorded table: bogus", str(cm.exception))
        with self.assertRaises(Exception) as cm:
            mod08.score_day([], mode="bogus")
        self.assertIn("stands unnamed: bogus", str(cm.exception))


class TestR16074UnknownCommand(unittest.TestCase):
    def test_unknown_command_str_bad(self):
        carriage = mod14.run_command(StrSubBad("boguscmd"))
        self.assertIn("unknown shell command", carriage["failure"])
        self.assertIn("flag_evaluation", carriage["failure"])
        self.assertNotIn("RuntimeError", carriage["failure"])

    def test_control_plain_unknown(self):
        carriage = mod14.run_command("bogus")
        self.assertIn("unknown shell command: bogus;",
                      carriage["failure"])


if __name__ == "__main__":
    unittest.main()
