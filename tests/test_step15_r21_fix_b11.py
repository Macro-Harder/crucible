import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod01, mod03, mod04, mod05, mod07


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
