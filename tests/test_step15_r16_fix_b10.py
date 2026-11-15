"""Pins for fix wave 15, Builder 10: rows R15-068 to R15-078
and R15-086 to R15-089 of the Round 15 register.

R15-068: MOD-13 extend_history, its no list form sentence,
renders the handed history through the safe repr form.
R15-069: MOD-13 verdict_record renders its standard and its
outcome through a safe string form.
R15-070: MOD-06 pause_cap renders an unknown variant through
the refusal text form.
R15-071: MOD-06 run_instruction reads its handed name and
renders its refusal sentences through a safe string form.
R15-072: MOD-03 archetype_catalogue renders a handed record
through the refusal repr form.
R15-073: MOD-03 build_cast and its farm size guard render
handed values through the refusal repr form at six sites.
R15-074: MOD-03 cold_society_degree renders its day and its
operands through the refusal repr form.
R15-075: MOD-04 view copy guard states its consequence in
its depth form and its counting and consequence in its
cycle form.
R15-076: MOD-14 error_carriage answers a failure handed in
no text and no exception form.
R15-077: MOD-14 error_carriage renders a handed exception
whose string reading raises.
R15-078: MOD-14 error_carriage leaves no repr escape residue
in the KeyError family sentences it carries.
R15-086: MOD-13 extend_history states its consequence at
five further sentences.
R15-087: MOD-14 write_store names the missing record fault
and the wrong form fault apart, with the lawful form and
the consequence.
R15-088: MOD-14 outside_call_check value refusal sentences
name the number form the act honours.
R15-089: MOD-14 flag_evaluation tier limb, outside_call_check
log key limb, and pilot_run use and barred key limbs render
handed values through a safe form.
"""

import unittest

from crucible import mod03, mod04, mod06, mod10, mod13, mod14, mod16


class ReprRaises:
    """A plain value whose repr reading raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr boom")


class StrRaises:
    """A plain value whose str reading raises RuntimeError."""

    def __str__(self):
        raise RuntimeError("str boom")


class StrReprRaises:
    """A plain value whose str and repr readings both raise."""

    def __str__(self):
        raise RuntimeError("str boom")

    def __repr__(self):
        raise RuntimeError("repr boom")


class StrReprRaisesStr(str):
    """Stores text; its str and repr readings both raise."""

    def __str__(self):
        raise RuntimeError("str boom")

    def __repr__(self):
        raise RuntimeError("repr boom")


class ReprRaisesStr(str):
    """Stores text; its repr reading raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr boom")


class BadStr(str):
    """Stores text; its str reading raises RuntimeError."""

    def __str__(self):
        raise RuntimeError("str boom")


class BadExc(Exception):
    """An exception whose str reading raises RuntimeError."""

    def __str__(self):
        raise RuntimeError("str boom")


def deep_list(depth):
    value = "leaf"
    for _ in range(depth):
        value = [value]
    return value


SEGMENT = {"rule_set_version": "v", "run_id": "r"}


class TestR15068ExtendHistoryRepr(unittest.TestCase):

    def test_history_repr_raises_draws_named_refusal(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(ReprRaises(), dict(SEGMENT))
        text = str(caught.exception)
        self.assertIn("no list form", text)
        self.assertIn("no extension stands made", text)

    def test_history_text_repr_raises_draws_named_refusal(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(
                ReprRaisesStr("text"), dict(SEGMENT))
        self.assertIn(
            "no extension stands made", str(caught.exception))

    def test_plain_integer_history_control(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(42, dict(SEGMENT))
        text = str(caught.exception)
        self.assertIn("42", text)
        self.assertIn("no extension stands made", text)


class TestR15069VerdictRecordStr(unittest.TestCase):

    def test_standard_str_raises_draws_named_refusal(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record("c1", standard=StrRaises())
        self.assertIn(
            "unknown replication standard",
            str(caught.exception))

    def test_outcome_str_raises_draws_named_refusal(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record("c1", outcome=StrRaises())
        self.assertIn(
            "unknown verdict outcome", str(caught.exception))

    def test_standard_both_raise_draws_named_refusal(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record("c1", standard=StrReprRaises())
        self.assertIn(
            "unknown replication standard",
            str(caught.exception))

    def test_plain_bogus_controls_render_the_value(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record("c1", standard="bogus")
        self.assertIn("bogus", str(caught.exception))
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record("c1", outcome="bogus")
        self.assertIn("bogus", str(caught.exception))


class TestR15070PauseCapStr(unittest.TestCase):

    def test_variant_str_raises_draws_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod06.pause_cap(variant=StrRaises())
        self.assertIn("unknown variant", str(caught.exception))

    def test_variant_both_raise_draws_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod06.pause_cap(variant=StrReprRaises())
        self.assertIn("unknown variant", str(caught.exception))

    def test_plain_unknown_variant_control(self):
        with self.assertRaises(ValueError) as caught:
            mod06.pause_cap(variant="bogus")
        self.assertIn("bogus", str(caught.exception))


class TestR15071RunInstructionName(unittest.TestCase):

    def test_name_str_raises_draws_named_refusal(self):
        with self.assertRaises(mod06.UnnamedInstruction):
            mod06.run_instruction(StrRaises())

    def test_plain_unnamed_control(self):
        with self.assertRaises(
                mod06.UnnamedInstruction) as caught:
            mod06.run_instruction("bogus_name")
        self.assertIn("bogus_name", str(caught.exception))


class TestR15072ArchetypeCatalogueRepr(unittest.TestCase):

    def test_record_repr_raises_draws_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod03.archetype_catalogue(records=[ReprRaises()])
        self.assertIn("no record form", str(caught.exception))

    def test_plain_integer_record_control(self):
        with self.assertRaises(ValueError) as caught:
            mod03.archetype_catalogue(records=[42])
        self.assertIn("42", str(caught.exception))


class TestR15073BuildCastRepr(unittest.TestCase):

    def test_point_repr_raises(self):
        with self.assertRaises(
                mod03.NamedGeneratorFailure) as caught:
            mod03.build_cast(
                ReprRaises(), [], strategy_class="fixed")
        self.assertIn("cast rejected", str(caught.exception))

    def test_mix_repr_raises(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                {"population_size": 0,
                 "archetype_mix": ReprRaises()},
                [], strategy_class="fixed")

    def test_population_repr_raises(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                {"population_size": ReprRaises(),
                 "archetype_mix": {}},
                [], strategy_class="fixed")

    def test_farm_size_guard_repr_raises(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                {"population_size": 0, "archetype_mix": {},
                 "farm_size": ReprRaises()},
                [], strategy_class="fixed")

    def test_initial_edge_text_repr_raises(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                {"population_size": 0, "archetype_mix": {}},
                [], strategy_class="fixed",
                initial_edges=[ReprRaisesStr("x")])

    def test_initial_edge_pair_repr_raises(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                {"population_size": 0, "archetype_mix": {}},
                [], strategy_class="fixed",
                initial_edges=[ReprRaises()])

    def test_plain_point_control(self):
        with self.assertRaises(
                mod03.NamedGeneratorFailure) as caught:
            mod03.build_cast(42, [], strategy_class="fixed")
        self.assertIn("42", str(caught.exception))


class TestR15074ColdSocietyDegreeRepr(unittest.TestCase):

    def test_day_repr_raises(self):
        with self.assertRaises(
                mod03.NamedGeneratorFailure) as caught:
            mod03.cold_society_degree(ReprRaises())
        self.assertIn(
            "cold society degree rejected", str(caught.exception))

    def test_operand_repr_raises(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(100, envelope=ReprRaises())

    def test_plain_day_control(self):
        with self.assertRaises(
                mod03.NamedGeneratorFailure) as caught:
            mod03.cold_society_degree("bogus")
        self.assertIn("bogus", str(caught.exception))

    def test_plain_operand_control(self):
        with self.assertRaises(
                mod03.NamedGeneratorFailure) as caught:
            mod03.cold_society_degree(100, envelope="bogus")
        self.assertIn("bogus", str(caught.exception))


class TestR15075ViewCopyGuard(unittest.TestCase):

    def test_depth_form_states_consequence(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.build_view_record(contents=[deep_list(120)])
        text = str(caught.exception)
        self.assertIn("view record copy bound reached", text)
        self.assertIn("counting every container", text)
        self.assertIn(
            "no view record or copy stands made or returned",
            text)

    def test_cycle_form_states_counting_and_consequence(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.build_view_record(contents=[cyclic])
        text = str(caught.exception)
        self.assertIn("view record copy found a cycle", text)
        self.assertIn("counting every container", text)
        self.assertIn(
            "no view record or copy stands made or returned",
            text)

    def test_plain_contents_control_builds(self):
        record = mod04.build_view_record(contents=[])
        self.assertIsInstance(record, dict)


class TestR15076ErrorCarriageVars(unittest.TestCase):

    def test_no_dict_attribute_forms_return_a_carriage(self):
        for value in (42, 1.5, True, None, ["x"], ("t",),
                      {"a": 1}, {"s"}, b"bytes"):
            carriage = mod14.error_carriage(value)
            self.assertTrue(
                carriage["operator_sees_failure"], repr(value))
            self.assertTrue(carriage["failure_value"])
            self.assertTrue(carriage["failure"])
            self.assertFalse(carriage["swallowed"])

    def test_plain_exception_control(self):
        carriage = mod14.error_carriage(ValueError("plain"))
        self.assertIn("plain", carriage["failure"])
        self.assertTrue(carriage["operator_sees_failure"])


class TestR15077ErrorCarriageStr(unittest.TestCase):

    def test_str_raising_exception_returns_a_carriage(self):
        carriage = mod14.error_carriage(BadExc())
        self.assertTrue(carriage["operator_sees_failure"])
        self.assertIn("BadExc", carriage["failure"])
        self.assertTrue(carriage["failure_value"])

    def test_plain_exception_control(self):
        carriage = mod14.error_carriage(
            ValueError("plain failure"))
        self.assertIn("plain failure", carriage["failure"])


class TestR15078ErrorCarriageEscapes(unittest.TestCase):

    def test_both_quotes_identifier_clean_at_read_store(self):
        result = mod14.run_command("read_store", {
            "run_id": "a'b\"c", "store_kind": "sweep"})
        self.assertIn("failure", result)
        self.assertNotIn("\\", result["failure"])
        self.assertIn("a'b\"c", result["failure"])
        message = result["failure_value"].get("message", "")
        self.assertEqual(
            message, "one lookup resolution failure: a'b\"c")
        self.assertEqual(
            result["failure_value"].get("run_identifier"),
            "a'b\"c")

    def test_backslash_identifier_clean_at_read_store(self):
        result = mod14.run_command("read_store", {
            "run_id": "a\\b", "store_kind": "sweep"})
        message = result["failure_value"].get("message", "")
        self.assertEqual(
            message, "one lookup resolution failure: a\\b")

    def test_control_character_identifier_clean(self):
        result = mod14.run_command("read_store", {
            "run_id": "a\nb\tc", "store_kind": "sweep"})
        message = result["failure_value"].get("message", "")
        self.assertEqual(
            message, "one lookup resolution failure: a\nb\tc")
        self.assertNotIn("\\n", message)
        self.assertNotIn("\\t", message)

    def test_fixture_lookup_both_quotes_clean(self):
        carriage = mod14.error_carriage(
            mod16.FixtureLookupFailure("x'y\"z"))
        self.assertNotIn("\\", carriage["failure"])
        self.assertIn("x'y\"z", carriage["failure"])

    def test_plain_key_error_both_quotes_clean(self):
        carriage = mod14.error_carriage(KeyError("k'y\"z"))
        self.assertNotIn("\\", carriage["failure"])
        self.assertIn("k'y\"z", carriage["failure"])

    def test_single_quote_kind_control(self):
        result = mod14.run_command("read_store", {
            "run_id": "o'brien", "store_kind": "sweep"})
        self.assertIn("failure", result)
        self.assertNotIn('"', result["failure"])


class TestR15086ExtendHistoryConsequence(unittest.TestCase):

    def test_segment_form_sentence_states_consequence(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history([dict(SEGMENT)], "not a record")
        self.assertIn(
            "no extension stands made", str(caught.exception))

    def test_no_version_sentence_states_consequence(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history([{"x": 1}], dict(SEGMENT))
        self.assertIn(
            "no extension stands made", str(caught.exception))

    def test_no_run_identifier_sentence_states_consequence(
            self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(
                [{"rule_set_version": "v"}], dict(SEGMENT))
        self.assertIn(
            "no extension stands made", str(caught.exception))

    def test_other_version_sentence_states_consequence(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(
                [dict(SEGMENT)],
                {"rule_set_version": "other", "run_id": "r"})
        self.assertIn(
            "no extension stands made", str(caught.exception))

    def test_other_link_sentence_states_consequence(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(
                [dict(SEGMENT)],
                {"rule_set_version": "v", "linked_run": "zzz"})
        self.assertIn(
            "no extension stands made", str(caught.exception))

    def test_valid_extension_control(self):
        result = mod13.extend_history(
            [dict(SEGMENT)],
            {"rule_set_version": "v", "run_id": "r2"})
        self.assertEqual(len(result), 2)


class TestR15087WriteStoreSentence(unittest.TestCase):

    def test_missing_record_names_absence_and_consequence(
            self):
        result = mod14.run_command("write_store", {})
        failure = result["failure"]
        self.assertIn("no record", failure)
        self.assertIn("nothing stands written", failure)

    def test_wrong_form_record_names_form_and_consequence(
            self):
        for record in ("text", [1]):
            result = mod14.run_command(
                "write_store", {"record": record})
            failure = result["failure"]
            self.assertIn("no mapping form", failure)
            self.assertIn("nothing stands written", failure)

    def test_missing_and_wrong_form_sentences_differ(self):
        missing = mod14.run_command("write_store", {})["failure"]
        wrong = mod14.run_command(
            "write_store", {"record": "text"})["failure"]
        self.assertNotEqual(missing, wrong)
        self.assertNotIn(
            "write_store carries no record to write", missing)
        self.assertNotIn(
            "write_store carries no record to write", wrong)


class TestR15088OutsideCallVocabulary(unittest.TestCase):

    def _refusal_text(self, mark):
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.outside_call_check(
                {}, {"calls": [{"outside_call": mark}]})
        return str(caught.exception)

    def test_text_bogus_sentence_names_number_form(self):
        self.assertIn(
            "as the number 1 or 0", self._refusal_text("bogus"))

    def test_float_mark_sentence_names_number_form(self):
        self.assertIn(
            "as the number 1 or 0", self._refusal_text(1.0))

    def test_number_marks_control(self):
        result = mod14.outside_call_check(
            {}, {"calls": [{"outside_call": 1}]})
        self.assertEqual(result["outcome"], "outside calls present")
        result = mod14.outside_call_check(
            {}, {"calls": [{"outside_call": 0}]})
        self.assertEqual(result["outcome"], "no outside calls read")


class TestR15089SafeRenderings(unittest.TestCase):

    def test_flag_tier_str_raises_direct(self):
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                {"run_id": "r"}, outcome="promote",
                tier=StrReprRaises())
        self.assertIn(
            "flag evaluation tier outside", str(caught.exception))

    def test_flag_tier_str_raises_at_shell(self):
        result = mod14.run_command("flag_evaluation", {
            "summary_record": {"run_id": "r"},
            "inputs": {"flag_conditions_fired": ["c"]},
            "outcome": "promote", "tier": StrReprRaises()})
        self.assertIn(
            "flag evaluation tier outside", result["failure"])
        self.assertNotIn("RuntimeError", result["failure"])

    def test_log_key_str_raises_direct(self):
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.outside_call_check({}, {StrReprRaises(): []})
        self.assertIn(
            "carries a key the check cannot read",
            str(caught.exception))

    def test_log_key_str_raises_at_shell(self):
        result = mod14.run_command("outside_call_check", {
            "dependency_manifest": {},
            "call_log": {StrReprRaises(): []}})
        self.assertIn(
            "carries a key the check cannot read",
            result["failure"])
        self.assertNotIn("RuntimeError", result["failure"])

    def test_pilot_use_str_raises_direct(self):
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.pilot_run(StrReprRaises())
        self.assertIn("pilot use outside", str(caught.exception))

    def test_pilot_use_str_raises_at_shell(self):
        result = mod14.run_command("run_pilot", {
            "use": StrReprRaises(), "artefact": {}})
        self.assertIn("pilot use outside", result["failure"])
        self.assertNotIn("RuntimeError", result["failure"])

    def test_pilot_barred_key_str_raises_direct(self):
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.pilot_run("timing", {BadStr("money"): 1})
        self.assertIn("barred entry", str(caught.exception))

    def test_pilot_barred_key_str_raises_at_shell(self):
        result = mod14.run_command("run_pilot", {
            "use": "timing", "artefact": {BadStr("money"): 1}})
        self.assertIn("barred entry", result["failure"])
        self.assertNotIn("RuntimeError", result["failure"])

    def test_plain_controls_render_the_value(self):
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                {"run_id": "r"},
                inputs={"flag_conditions_fired": ["c"]},
                outcome="promote", tier="Tier 9")
        self.assertIn("Tier 9", str(caught.exception))
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.pilot_run("bogus")
        self.assertIn("bogus", str(caught.exception))
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.outside_call_check({}, {"bogus": []})
        self.assertIn("bogus", str(caught.exception))
        with self.assertRaises(
                mod14.NamedShellFailure) as caught:
            mod14.pilot_run("timing", {"money": 1})
        self.assertIn("money", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
