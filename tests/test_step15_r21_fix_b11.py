"""

Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

Pins for fix wave 21, builder b11, Group 11: MOD-10 stored repr
and sentences, rows R21-020, R21-040, R21-041, R21-042, R21-043,
R21-044, R21-045, and R21-046 of the Round 21 register.

Distinguishing pins fail or error on the pristine basis and pass
on the cured copy. Control pins pass on both trees.
"""


import unittest
from decimal import Decimal
from fractions import Fraction
from crucible import mod01, mod03, mod04, mod05, mod07
import os
import subprocess
import sys
from crucible import mod10


class LieStr(str):
    def __new__(cls, stored, reading):
        obj = str.__new__(cls, stored)
        obj._reading = reading
        return obj

    def __str__(self):
        return self._reading

    def __repr__(self):
        return repr(self._reading)


class RaiseStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __str__(self):
        raise RuntimeError("string reading raises")

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class EqFalseStr(str):
    def __eq__(self, other):
        return False

    __hash__ = str.__hash__


class EqTrueStr(str):
    def __eq__(self, other):
        return True

    __hash__ = str.__hash__


class RaiseEqStr(str):
    def __eq__(self, other):
        raise RuntimeError("equality reading raises")

    __hash__ = str.__hash__


class AlwaysEq:
    def __eq__(self, other):
        return True


class RaiseEq:
    def __eq__(self, other):
        raise RuntimeError("equality reading raises")


class RaiseEqInt(int):
    def __new__(cls, value):
        return int.__new__(cls, value)

    def __eq__(self, other):
        raise RuntimeError("equality reading raises")

    __hash__ = int.__hash__


def run_adjudicate(**overrides):
    kwargs = {
        "accuracy_value": 0.5,
        "assumption_set": "set-1",
        "row": "row-1",
        "error_direction": "symmetric",
    }
    kwargs.update(overrides)
    return mod05.adjudicate({"case_identifier": "case-1"}, **kwargs)


def adjudicate_message(**overrides):
    try:
        run_adjudicate(**overrides)
    except ValueError as error:
        return str(error)
    return ""


class TestR20017DerivedFrom(unittest.TestCase):
    def test_eq_false_barred_source_refused(self):
        with self.assertRaises(ValueError) as caught:
            run_adjudicate(derived_from=EqFalseStr("panel size"))
        self.assertIn("may not be derived from panel size", str(caught.exception))
        self.assertIsNotNone(getattr(caught.exception, "failure_class", None))

    def test_eq_true_honest_source_admitted(self):
        result = run_adjudicate(derived_from=EqTrueStr("honest measurement"))
        self.assertEqual(result["outcome"], "no determination")

    def test_raise_eq_barred_source_named_failure(self):
        with self.assertRaises(ValueError) as caught:
            run_adjudicate(derived_from=RaiseEqStr("panel size"))
        self.assertIn("may not be derived from panel size", str(caught.exception))

    def test_raise_eq_honest_source_admitted(self):
        result = run_adjudicate(derived_from=RaiseEqStr("honest measurement"))
        self.assertEqual(result["outcome"], "no determination")

    def test_plain_barred_source_refused_control(self):
        with self.assertRaises(ValueError):
            run_adjudicate(derived_from="panel size")

    def test_plain_honest_source_admitted_control(self):
        result = run_adjudicate(derived_from="honest measurement")
        self.assertEqual(result["outcome"], "no determination")

    def test_no_source_admitted_control(self):
        result = run_adjudicate()
        self.assertEqual(result["outcome"], "no determination")


class TestR20018DecayResult(unittest.TestCase):
    def test_boolean_true_no_extension(self):
        result = mod05.decay_result(True)
        self.assertNotIn("extension", result)

    def test_always_equal_value_no_extension(self):
        result = mod05.decay_result(AlwaysEq())
        self.assertNotIn("extension", result)

    def test_raise_eq_value_delivered_no_extension(self):
        result = mod05.decay_result(RaiseEq())
        self.assertNotIn("extension", result)

    def test_raise_eq_int_one_extension(self):
        result = mod05.decay_result(RaiseEqInt(1))
        self.assertIn("extension", result)

    def test_decimal_three_no_extension(self):
        result = mod05.decay_result(Decimal(3))
        self.assertNotIn("extension", result)

    def test_fraction_one_no_extension(self):
        result = mod05.decay_result(Fraction(1))
        self.assertNotIn("extension", result)

    def test_one_extension_control(self):
        self.assertIn("extension", mod05.decay_result(1))

    def test_three_extension_control(self):
        self.assertIn("extension", mod05.decay_result(3))

    def test_two_no_extension_control(self):
        self.assertNotIn("extension", mod05.decay_result(2))

    def test_default_no_extension_control(self):
        self.assertNotIn("extension", mod05.decay_result())


class TestR20028Mod03Walks(unittest.TestCase):
    def raising_record(self):
        return {"outer": {RaiseStr("plainkey"): 1}}

    def test_record_carries_ground_truth_raising_key(self):
        self.assertFalse(mod03.record_carries_ground_truth(self.raising_record()))

    def test_validate_generator_output_raising_key(self):
        self.assertTrue(mod03.validate_generator_output([self.raising_record()]))

    def test_strip_ground_truth_raising_key(self):
        result = mod03.strip_ground_truth(self.raising_record())
        self.assertEqual(result, {"outer": {"plainkey": 1}})

    def test_plain_record_carries_control(self):
        self.assertFalse(mod03.record_carries_ground_truth({"outer": {"plainkey": 1}}))

    def test_plain_validate_control(self):
        self.assertTrue(mod03.validate_generator_output([{"outer": {"plainkey": 1}}]))

    def test_plain_strip_control(self):
        result = mod03.strip_ground_truth({"outer": {"plainkey": 1}})
        self.assertEqual(result, {"outer": {"plainkey": 1}})

    def test_barred_record_control(self):
        self.assertTrue(mod03.record_carries_ground_truth({"ground_truth": 1}))


class TestR20029PanelWalks(unittest.TestCase):
    def test_validate_panel_inputs_raising_key(self):
        self.assertTrue(mod05.validate_panel_inputs({RaiseStr("plainkey"): 1}))

    def test_barred_keys_raising_key(self):
        found = mod05._panel_barred_keys({RaiseStr("ground_truth"): 1})
        self.assertEqual(found, ["ground_truth"])

    def test_barred_keys_lying_key(self):
        found = mod05._panel_barred_keys({LieStr("ground_truth", "innocent"): 1})
        self.assertEqual(found, ["ground_truth"])

    def test_adjudicate_lying_barred_key_sentence(self):
        case = {LieStr("ground_truth", "innocent"): 1}
        try:
            mod05.adjudicate(
                case, accuracy_value=0.5, assumption_set="set-1",
                row="row-1", error_direction="symmetric")
            self.fail("adjudicate should refuse a barred key case")
        except ValueError as error:
            self.assertIn("membership key: ground_truth", str(error))
            self.assertNotIn("innocent", str(error))

    def test_adjudicate_raising_barred_key_named_failure(self):
        case = {RaiseStr("ground_truth"): 1}
        with self.assertRaises(ValueError) as caught:
            mod05.adjudicate(
                case, accuracy_value=0.5, assumption_set="set-1",
                row="row-1", error_direction="symmetric")
        self.assertIn("membership key: ground_truth", str(caught.exception))
        self.assertIsNotNone(getattr(caught.exception, "failure_class", None))

    def test_validate_plain_key_control(self):
        self.assertTrue(mod05.validate_panel_inputs({"plainkey": 1}))

    def test_validate_barred_key_control(self):
        self.assertFalse(mod05.validate_panel_inputs({"ground_truth": 1}))

    def test_barred_keys_plain_control(self):
        self.assertEqual(mod05._panel_barred_keys({"ground_truth": 1}), ["ground_truth"])

    def test_adjudicate_plain_barred_sentence_control(self):
        message = adjudicate_message()
        self.assertEqual(message, "")
        case = {"ground_truth": 1}
        try:
            mod05.adjudicate(
                case, accuracy_value=0.5, assumption_set="set-1",
                row="row-1", error_direction="symmetric")
            self.fail("adjudicate should refuse a barred key case")
        except ValueError as error:
            self.assertIn("membership key: ground_truth", str(error))


class TestR20070EntryKindSentence(unittest.TestCase):
    def kind_message(self, kind):
        try:
            mod01.minimal_valid_instance("36", entry_kind=kind)
        except ValueError as error:
            return str(error)
        return ""

    def test_lying_kind_names_stored(self):
        message = self.kind_message(LieStr("bogus", "ordinary"))
        self.assertIn("unknown entry kind: bogus;", message)

    def test_raising_kind_names_stored(self):
        message = self.kind_message(RaiseStr("bogus"))
        self.assertIn("unknown entry kind: bogus;", message)

    def test_bytes_kind_names_stored(self):
        message = self.kind_message(b"bogus")
        self.assertIn("unknown entry kind: bogus;", message)
        self.assertNotIn("b'bogus'", message)

    def test_plain_kind_control(self):
        message = self.kind_message("bogus")
        self.assertIn("unknown entry kind: bogus;", message)

    def test_lying_agent_kind_admitted_control(self):
        instance = mod01.minimal_valid_instance(
            "36", entry_kind=LieStr("agent", "bogus"))
        self.assertEqual(str.__str__(instance["entry_kind"]), "agent")

    def test_plain_ordinary_control(self):
        instance = mod01.minimal_valid_instance("36", entry_kind="ordinary")
        self.assertEqual(instance["entry_kind"], "ordinary")


class TestR20071FormLookup(unittest.TestCase):
    def test_form_name_lying_named_form(self):
        self.assertEqual(mod01.form_name(LieStr("22", "99")), "SweepFamilyRegistry")

    def test_form_name_lying_unnamed_form(self):
        self.assertIsNone(mod01.form_name(LieStr("99", "22")))

    def test_form_fields_lying_named_form(self):
        self.assertNotEqual(mod01.form_fields(LieStr("22", "99")), ())

    def test_required_fields_lying_named_form(self):
        self.assertNotEqual(mod01.required_fields(LieStr("22", "99")), ())

    def test_form_name_plain_control(self):
        self.assertEqual(mod01.form_name("22"), "SweepFamilyRegistry")

    def test_form_name_unnamed_control(self):
        self.assertIsNone(mod01.form_name("99"))

    def test_form_fields_plain_control(self):
        self.assertNotEqual(mod01.form_fields("22"), ())

    def test_form_name_int_control(self):
        self.assertEqual(mod01.form_name(36), "EventLog")


class TestR20072CompletenessSentence(unittest.TestCase):
    def state_message(self, state):
        try:
            mod04.build_view_record(completeness=state)
        except mod04.NamedFailure as error:
            return str(error)
        return ""

    def test_lying_state_names_stored(self):
        message = self.state_message(LieStr("bogus", "complete"))
        self.assertIn("outside the closed vocabulary: bogus", message)
        self.assertNotIn(": complete", message)

    def test_raising_state_names_stored(self):
        message = self.state_message(RaiseStr("bogus"))
        self.assertIn("outside the closed vocabulary: bogus", message)

    def test_bytes_state_names_stored(self):
        message = self.state_message(b"bogus")
        self.assertIn("outside the closed vocabulary: bogus", message)
        self.assertNotIn("b'bogus'", message)

    def test_plain_state_control(self):
        message = self.state_message("bogus")
        self.assertIn("outside the closed vocabulary: bogus", message)

    def test_complete_state_control(self):
        record = mod04.build_view_record(completeness="complete")
        self.assertEqual(record["completeness_state"], "complete")


class TestR20073AccuracySentence(unittest.TestCase):
    def test_lying_accuracy_names_stored(self):
        message = adjudicate_message(accuracy_value=LieStr("bogus", "42"))
        self.assertIn("in no numeric form: 'bogus'", message)

    def test_raising_accuracy_names_stored(self):
        message = adjudicate_message(accuracy_value=RaiseStr("bogus"))
        self.assertIn("in no numeric form: 'bogus'", message)

    def test_bytes_accuracy_names_stored(self):
        message = adjudicate_message(accuracy_value=b"bogus")
        self.assertIn("in no numeric form: 'bogus'", message)
        self.assertNotIn("b'bogus'", message)

    def test_plain_accuracy_control(self):
        message = adjudicate_message(accuracy_value="bogus")
        self.assertIn("in no numeric form: 'bogus'", message)

    def test_valid_accuracy_control(self):
        result = run_adjudicate(accuracy_value=0.5)
        self.assertEqual(result["arbiter_accuracy_value"], 0.5)


class TestR20074OutcomeSentence(unittest.TestCase):
    def test_lying_outcome_names_stored(self):
        message = adjudicate_message(outcome=LieStr("bogus", "slashable"))
        self.assertIn("outside the stated vocabulary: 'bogus'", message)

    def test_raising_outcome_names_stored(self):
        message = adjudicate_message(outcome=RaiseStr("bogus"))
        self.assertIn("outside the stated vocabulary: 'bogus'", message)

    def test_bytes_outcome_names_stored(self):
        message = adjudicate_message(outcome=b"bogus")
        self.assertIn("outside the stated vocabulary: 'bogus'", message)
        self.assertNotIn("b'bogus'", message)

    def test_plain_outcome_control(self):
        message = adjudicate_message(outcome="bogus")
        self.assertIn("outside the stated vocabulary: 'bogus'", message)

    def test_valid_outcome_control(self):
        result = run_adjudicate(outcome="slashable")
        self.assertEqual(result["outcome"], "slashable")


class TestR20075TracerResultSentence(unittest.TestCase):
    def result_message(self, result):
        try:
            mod07.make_tracer_passage_record("OS-1", "point-1", "what passed", result)
        except ValueError as error:
            return str(error)
        return ""

    def test_lying_result_names_stored(self):
        message = self.result_message(LieStr("bogus", "blocked"))
        self.assertIn("outside the stated set: bogus", message)
        self.assertNotIn(": blocked", message)

    def test_raising_result_names_stored(self):
        message = self.result_message(RaiseStr("bogus"))
        self.assertIn("outside the stated set: bogus", message)

    def test_bytes_result_names_stored(self):
        message = self.result_message(b"bogus")
        self.assertIn("outside the stated set: bogus", message)
        self.assertNotIn("b'bogus'", message)

    def test_plain_result_control(self):
        message = self.result_message("bogus")
        self.assertIn("outside the stated set: bogus", message)

    def test_lying_stated_result_delivered_control(self):
        record = mod07.make_tracer_passage_record(
            "OS-1", "point-1", "what passed", LieStr("blocked", "bogus"))
        self.assertEqual(str.__str__(record["result"]), "blocked")


class TestR20076TracerRunRecords(unittest.TestCase):
    def test_lying_run_named_in_records(self):
        records = mod07.tracer_passage_records(LieStr("run-9", "run-1"))
        self.assertEqual(len(records), 14)
        for record in records:
            self.assertIn("in run run-9", record["point_in_run"])
            self.assertNotIn("run-1", record["point_in_run"])

    def test_raising_run_named_in_records(self):
        records = mod07.tracer_passage_records(RaiseStr("run-9"))
        for record in records:
            self.assertIn("in run run-9", record["point_in_run"])

    def test_bytes_run_named_in_records(self):
        records = mod07.tracer_passage_records(b"run-9")
        for record in records:
            self.assertIn("in run run-9", record["point_in_run"])
            self.assertNotIn("b'run-9'", record["point_in_run"])

    def test_plain_run_control(self):
        records = mod07.tracer_passage_records("run-9")
        self.assertEqual(len(records), 14)
        for record in records:
            self.assertIn("in run run-9", record["point_in_run"])

    def test_record_items_control(self):
        records = mod07.tracer_passage_records("run-9")
        self.assertEqual(records[0]["open_semantic_item"], "OS-1")
        self.assertEqual(records[-1]["open_semantic_item"], "OS-14")


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


class LyingStr(str):
    """A text value storing one text whose string reading
    answers another text."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie


class RaisingStr(str):
    """A text value storing one text whose string reading
    raises."""

    def __str__(self):
        raise RuntimeError("string reading raises")


class LyingRepr:
    """A plain object whose repr reading answers a stated
    firing number it does not stand as."""

    def __init__(self, lie):
        self._lie = lie

    def __repr__(self):
        return self._lie


SET_TEXTS = (
    "alpha", "bravo", "charlie", "delta",
    "echo", "foxtrot", "golf", "hotel")


SORTED_SET_RENDER = (
    "{'alpha', 'bravo', 'charlie', 'delta', "
    "'echo', 'foxtrot', 'golf', 'hotel'}")


def view_record(run_id, item, seen_day, viewer="viewer-1"):
    return {
        "run_identifier": run_id,
        "viewer_identifier": viewer,
        "simulated_day": 5,
        "scheduling_position_identifier": "s",
        "rule_version_set": "r",
        "view_contents": {},
        "reputation_and_band_values": {},
        "graph_position_as_seen": {},
        "first_seen_day_per_record": {item: seen_day},
        "delay_applied_per_record": {},
        "completeness_state": "complete",
        "building_component": "c",
        "delivering_contract": "d",
        "selection_rule_version": "v",
    }


class TestR21020StoredReprSetLimb(unittest.TestCase):

    def test_distinguishing_set_renders_sorted(self):
        self.assertEqual(
            mod10._stored_repr(set(SET_TEXTS)), SORTED_SET_RENDER)

    def test_distinguishing_frozenset_renders_sorted(self):
        self.assertEqual(
            mod10._stored_repr(frozenset(SET_TEXTS)),
            SORTED_SET_RENDER)

    def test_distinguishing_checkpoint_sentence_renders_sorted(self):
        manifest = {
            "run_identifier": "run-x",
            "journal_position": set(SET_TEXTS),
        }
        result = mod10.checkpoint_position_check(manifest)
        self.assertIn(SORTED_SET_RENDER, result["outcome"])

    def test_distinguishing_order_stable_across_processes(self):
        root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        code = (
            "from crucible import mod10;"
            "m={'run_identifier':'run-x','journal_position':"
            "{'alpha','bravo','charlie','delta','echo',"
            "'foxtrot','golf','hotel'}};"
            "print(mod10.checkpoint_position_check(m)['outcome'])"
        )
        outcomes = []
        for seed in ("0", "1", "2", "3", "4", "5",
                    "6", "7", "8", "9", "10", "42"):
            env = dict(os.environ)
            env["PYTHONHASHSEED"] = seed
            proc = subprocess.run(
                [sys.executable, "-c", code],
                cwd=root, env=env, capture_output=True, text=True,
                timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            outcomes.append(proc.stdout.strip())
        self.assertEqual(len(set(outcomes)), 1)
        self.assertIn(SORTED_SET_RENDER, outcomes[0])

    def test_control_list_renders_in_stored_order(self):
        self.assertEqual(
            mod10._stored_repr(["bravo", "alpha"]),
            "['bravo', 'alpha']")

    def test_control_plain_text_and_number_render(self):
        self.assertEqual(mod10._stored_repr("alpha"), "'alpha'")
        self.assertEqual(mod10._stored_repr(5), "5")


class TestR21040RetainGc08Record(unittest.TestCase):

    def test_distinguishing_lying_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record(
                LyingStr("bogus-kind", "dependency_manifest"),
                {}, "owner-1")
        message = str(ctx.exception)
        self.assertIn("unknown GC-08 record kind: bogus-kind;", message)
        self.assertNotIn("kind: dependency_manifest", message)

    def test_distinguishing_raising_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record(
                RaisingStr("bogus-kind"), {}, "owner-1")
        self.assertIn(
            "unknown GC-08 record kind: bogus-kind;",
            str(ctx.exception))

    def test_control_plain_kind_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record("bogus", {}, "owner-1")
        self.assertIn(
            "unknown GC-08 record kind: bogus;", str(ctx.exception))


class TestR21041StoreLookup(unittest.TestCase):

    def test_distinguishing_lying_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(
                key="k", store_kind=LyingStr("bogus-kind", "sweep"))
        message = str(ctx.exception)
        self.assertIn("unknown store kind: bogus-kind;", message)
        self.assertNotIn("kind: sweep", message)

    def test_distinguishing_raising_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(
                key="k", store_kind=RaisingStr("bogus-kind"))
        self.assertIn(
            "unknown store kind: bogus-kind;", str(ctx.exception))

    def test_control_plain_kind_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(key="k", store_kind="bogus")
        self.assertIn(
            "unknown store kind: bogus;", str(ctx.exception))


class TestR21042ApplyFlagEvaluation(unittest.TestCase):

    def test_distinguishing_lying_outcome_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation(
                {}, outcome=LyingStr("bogus-outcome", "promote"))
        message = str(ctx.exception)
        self.assertIn(
            "outside the stated vocabulary: bogus-outcome;", message)
        self.assertNotIn("vocabulary: promote", message)

    def test_distinguishing_raising_outcome_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation(
                {}, outcome=RaisingStr("bogus-outcome"))
        self.assertIn(
            "outside the stated vocabulary: bogus-outcome;",
            str(ctx.exception))

    def test_control_plain_outcome_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation({}, outcome="bogus-outcome")
        self.assertIn(
            "outside the stated vocabulary: bogus-outcome;",
            str(ctx.exception))


class TestR21043ApplyDeferredEvaluation(unittest.TestCase):

    def test_distinguishing_lying_repr_one_not_named_as_firing(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_deferred_evaluation({}, LyingRepr("1"))
        message = str(ctx.exception)
        self.assertIn("stands outside the stated firings 1 and 2", message)
        self.assertNotIn("the firing 1 stands outside", message)

    def test_distinguishing_lying_repr_two_not_named_as_firing(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_deferred_evaluation({}, LyingRepr("2"))
        message = str(ctx.exception)
        self.assertIn("stands outside the stated firings 1 and 2", message)
        self.assertNotIn("the firing 2 stands outside", message)

    def test_control_plain_firing_five_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_deferred_evaluation({}, 5)
        self.assertIn(
            "the firing 5 stands outside the stated firings",
            str(ctx.exception))


class TestR21044SummaryRecordForRun(unittest.TestCase):

    def test_distinguishing_lying_identifier_names_stored_text(self):
        result = mod10.summary_record_for_run(
            LyingStr("run-x", "run-y"))
        self.assertIn("for run run-x", result["statement"])
        self.assertNotIn("run-y", result["statement"])

    def test_distinguishing_raising_identifier_names_stored_text(self):
        result = mod10.summary_record_for_run(RaisingStr("run-x"))
        self.assertIn("for run run-x", result["statement"])

    def test_control_plain_identifier_named(self):
        result = mod10.summary_record_for_run("run-x")
        self.assertIn("for run run-x", result["statement"])


class TestR21045RunViewLeakCheckViewName(unittest.TestCase):

    def test_distinguishing_lying_run_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                LyingStr("run-real", "run-fake"), "rec-1", 9))
        message = str(ctx.exception)
        self.assertIn("view run-real/viewer-1", message)
        self.assertNotIn("run-fake", message)

    def test_distinguishing_lying_viewer_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "run-1", "rec-1", 9,
                viewer=LyingStr("viewer-real", "viewer-fake")))
        message = str(ctx.exception)
        self.assertIn("view run-1/viewer-real", message)
        self.assertNotIn("viewer-fake", message)

    def test_distinguishing_raising_run_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                RaisingStr("run-real"), "rec-1", 9))
        self.assertIn(
            "view run-real/viewer-1", str(ctx.exception))

    def test_control_plain_view_named_in_failure(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record("run-1", "rec-1", 9))
        self.assertIn("view run-1/viewer-1", str(ctx.exception))

    def test_control_plain_view_named_on_pass(self):
        result = mod10.run_view_leak_check(
            view_record("run-1", "rec-1", 3))
        self.assertEqual(result["view"], "run-1/viewer-1")
        self.assertTrue(result["reportable"])


class TestR21046RunViewLeakCheckRecordItem(unittest.TestCase):

    def test_distinguishing_lying_item_after_day_names_stored(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "run-1", LyingStr("rec-real", "rec-fake"), 9))
        message = str(ctx.exception)
        self.assertIn("record rec-real first seen after", message)
        self.assertNotIn("rec-fake", message)

    def test_distinguishing_lying_item_nonfinite_names_stored(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "run-1", LyingStr("rec-real", "rec-fake"),
                float("inf")))
        message = str(ctx.exception)
        self.assertIn(
            "record rec-real states a day in a non finite form",
            message)
        self.assertNotIn("rec-fake", message)

    def test_distinguishing_raising_item_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "run-1", RaisingStr("rec-real"), 9))
        self.assertIn(
            "record rec-real first seen after", str(ctx.exception))

    def test_control_plain_item_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record("run-1", "rec-1", 9))
        self.assertIn(
            "record rec-1 first seen after", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
