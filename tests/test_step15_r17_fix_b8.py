import unittest

from crucible import mod03, mod04, mod05, mod07, mod08, mod10, mod11


def message_of(fn):
    try:
        fn()
    except Exception as exc:
        return str(exc)
    raise AssertionError("no exception raised")


class RaisingIter:
    def __iter__(self):
        raise RuntimeError("iter boom")


class RaisingIterList(list):
    def __iter__(self):
        raise RuntimeError("iter boom")


class TestR16077WeeklyCountConsequences(unittest.TestCase):

    def test_dict_records_sentence_states_consequence(self):
        text = message_of(lambda: mod11.weekly_count({}, "W1"))
        self.assertIn("stands in no list form", text)
        self.assertIn("and no weekly count stands certified without it", text)

    def test_no_field_sentence_states_consequence(self):
        text = message_of(lambda: mod11.weekly_count(
            [{"week": "W1"}], "W1"))
        self.assertIn("carries no headline_unit_identifiers field", text)
        self.assertIn("and no weekly count stands certified without it", text)

    def test_none_field_sentence_states_consequence(self):
        text = message_of(lambda: mod11.weekly_count(
            [{"week": "W1", "headline_unit_identifiers": None}], "W1"))
        self.assertIn("standing at no value", text)
        self.assertIn("and no weekly count stands certified without it", text)

    def test_unreadable_field_sentence_states_consequence(self):
        text = message_of(lambda: mod11.weekly_count(
            [{"week": "W1", "headline_unit_identifiers": 42}], "W1"))
        self.assertIn("the count cannot read: int", text)
        self.assertIn("and no weekly count stands certified without it", text)

    def test_controls_hold(self):
        text = message_of(lambda: mod11.weekly_count(None, "W1"))
        self.assertEqual(
            text,
            "weekly_count stands refused: no summary_records stand "
            "supplied: a list of summary records stands required, "
            "and no weekly count stands certified without it")
        self.assertEqual(mod11.weekly_count(
            [{"week": "W1", "headline_unit_identifiers": ["u1"]}], "W1"), 1)


class TestR16078RetirementVerdictSentence(unittest.TestCase):

    def test_verdicts_sentence_names_fixtures_and_consequence(self):
        text = message_of(lambda: mod11.retirement_verdicts("F-99"))
        self.assertIn("no retirement verdict stands recorded for: F-99", text)
        self.assertIn("F-01", text)
        self.assertIn("F-02", text)
        self.assertIn("EX-01", text)
        self.assertIn("no verdicts and no tally stand returned", text)

    def test_tally_sentence_stands_whole(self):
        text = message_of(lambda: mod11.retirement_tally("F-99"))
        self.assertIn("F-01, F-02, and EX-01", text)
        self.assertIn("no verdicts and no tally stand returned", text)

    def test_controls_hold(self):
        self.assertIn("T-01", mod11.retirement_verdicts("F-01"))
        self.assertIn("T-01", mod11.retirement_verdicts("F-02"))
        self.assertIn("T-01", mod11.retirement_verdicts("EX-01"))
        self.assertEqual(
            mod11.retirement_tally("F-01")["fixture"], "F-01")


class TestR16079Mod10SentenceCompleteness(unittest.TestCase):

    def test_tier_sentence_states_consequence(self):
        text = message_of(lambda: mod10.apply_flag_evaluation(
            {}, outcome=None, tier="Tier 9"))
        self.assertIn("flag evaluation tier outside", text)
        self.assertIn("Tier 0, Tier 1, Tier 2, and Tier 3", text)
        self.assertIn("and no flag evaluation stands performed", text)

    def test_already_written_sentence_complete(self):
        record = {"deferred_evaluations": [{"firing": 1}]}
        text = message_of(lambda: mod10.apply_deferred_evaluation(
            record, 1, inputs={"x": 1}, outcome="o"))
        self.assertIn("apply_deferred_evaluation", text)
        self.assertIn("already stands written", text)
        self.assertIn("firings 1 and 2", text)
        self.assertIn("and no evaluation stands written", text)

    def test_cross_stores_sentence_complete(self):
        text = message_of(lambda: mod10.store_lookup(
            store_kinds=["sweep", "pilot"], key="k"))
        self.assertIn("across stores in one step is rejected", text)
        self.assertIn("exactly one store kind", text)
        self.assertIn("no record lookup stands performed", text)

    def test_outcome_control_holds(self):
        text = message_of(lambda: mod10.apply_flag_evaluation(
            {}, outcome="bogus"))
        self.assertEqual(
            text,
            "flag evaluation outcome outside the stated vocabulary: "
            "bogus; the outcomes the rule names stand as promote and "
            "demote, and no flag evaluation stands performed")

    def test_unknown_kind_control_holds(self):
        text = message_of(lambda: mod10.store_lookup(
            store_kinds=["bogus"], key="k"))
        self.assertEqual(
            text,
            "unknown store kind: bogus; a store kind stands among "
            "sweep, pilot, and live, and no record lookup stands "
            "performed on an unknown kind")


class TestR16080Mod11BareEscapes(unittest.TestCase):

    def assert_named(self, fn, act, consequence):
        with self.assertRaises(ValueError) as caught:
            fn()
        text = str(caught.exception)
        self.assertIn(act, text)
        self.assertIn("stands refused", text)
        self.assertIn(consequence, text)
        self.assertNotIn("invalid literal", text)
        self.assertNotIn("not iterable", text)
        self.assertNotIn("bad operand", text)
        self.assertNotIn("has no attribute", text)
        self.assertNotIn("not supported between", text)

    def test_classify_text_day(self):
        self.assert_named(
            lambda: mod11.classify_run_outcome("x", "steady"),
            "classify_run_outcome", "no outcome stands classified")

    def test_classify_list_day(self):
        self.assert_named(
            lambda: mod11.classify_run_outcome(["x"], "steady"),
            "classify_run_outcome", "no outcome stands classified")

    def test_honest_loss_text(self):
        self.assert_named(
            lambda: mod11.honest_loss_rate_h1("x", "y"),
            "honest_loss_rate_h1", "no loss rate stands computed")

    def test_honest_loss_text_second(self):
        self.assert_named(
            lambda: mod11.honest_loss_rate_h1(10, "y"),
            "honest_loss_rate_h1", "no loss rate stands computed")

    def test_point_standing_text(self):
        self.assert_named(
            lambda: mod11.point_standing("x"),
            "point_standing", "no point standing stands returned")

    def test_point_standing_none(self):
        self.assert_named(
            lambda: mod11.point_standing(None),
            "point_standing", "no point standing stands returned")

    def test_moved_reading_text(self):
        self.assert_named(
            lambda: mod11.moved_reading("x", "y"),
            "moved_reading", "no moved reading stands returned")

    def test_moved_reading_none(self):
        self.assert_named(
            lambda: mod11.moved_reading(None, 1),
            "moved_reading", "no moved reading stands returned")

    def test_top_up_text(self):
        self.assert_named(
            lambda: mod11.top_up_applies("x"),
            "top_up_applies", "no top up judgement stands returned")

    def test_transition_figure_text(self):
        self.assert_named(
            lambda: mod11.transition_figure("text"),
            "transition_figure", "no transition figure stands computed")

    def test_transition_figure_list_of_int(self):
        self.assert_named(
            lambda: mod11.transition_figure([1]),
            "transition_figure", "no transition figure stands computed")

    def test_controls_classify_and_point(self):
        self.assertEqual(
            mod11.classify_run_outcome(10, "steady")["outcome"],
            "horizon insufficient")
        self.assertEqual(
            mod11.classify_run_outcome(30, "steady")["outcome"], "steady")
        self.assertEqual(
            mod11.point_standing(30)["standing"], "at floor")
        self.assertEqual(
            mod11.point_standing(29)["standing"], "below floor")

    def test_controls_moved_topup_honest(self):
        self.assertTrue(mod11.moved_reading(5, 3))
        self.assertFalse(mod11.moved_reading(1, 3))
        self.assertTrue(mod11.top_up_applies(0.5))
        self.assertFalse(mod11.top_up_applies(0.05))
        self.assertEqual(
            mod11.honest_loss_rate_h1(10, 4),
            {"form": "H1", "numerator": 6, "denominator": 10})

    def test_control_transition_figure(self):
        result = mod11.transition_figure(
            [{"first_terminal_regime": "A"}])
        self.assertEqual(result["denominator"], 1)
        self.assertEqual(
            result["cumulative_incidence"]["A"]["count"], 1)


class TestR16081Mod10ReadingEscapes(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def assert_lookup(self, fn):
        with self.assertRaises(mod10.LookupFailure) as caught:
            fn()
        self.assertEqual(
            caught.exception.failure["name"],
            "one lookup resolution failure")
        self.assertFalse(caught.exception.failure["complete"])

    def test_summary_list_identifier(self):
        self.assert_lookup(
            lambda: mod10.summary_record_for_run(["x"]))

    def test_retention_list_identifier(self):
        self.assert_lookup(
            lambda: mod10.retention_record_for_run(["x"]))

    def test_reserve_hold_list_identifier(self):
        self.assert_lookup(
            lambda: mod10.reserve_hold_for_run(["x"]))

    def test_view_records_list_identifier(self):
        self.assert_lookup(
            lambda: mod10.view_records_for_run(["x"]))

    def test_restore_check_non_iterable_present(self):
        with self.assertRaises(ValueError) as caught:
            mod10.restore_check(
                {"relative_identifier": "checkpoints/a"}, 42)
        text = str(caught.exception)
        self.assertIn("restore_check", text)
        self.assertIn("stands refused", text)
        self.assertNotIn("not iterable", text)

    def test_control_summary_absent_form_only(self):
        result = mod10.summary_record_for_run("nope-b8")
        self.assertEqual(result["form"], "form_only")
        self.assertFalse(result["record_found"])

    def test_control_reserve_and_view_absent(self):
        self.assertIsNone(mod10.reserve_hold_for_run("nope-b8"))
        self.assertEqual(mod10.view_records_for_run("nope-b8"), [])

    def test_control_restore_answers(self):
        portable = {"relative_identifier": "checkpoints/a"}
        self.assertTrue(mod10.restore_check(portable, {"checkpoints/a"}))
        self.assertFalse(mod10.restore_check(portable, {"other"}))

    def test_control_read_run_lookup(self):
        self.assert_lookup(lambda: mod10.read_run_record(["x"]))


class TestR16087FiveActEscapes(unittest.TestCase):

    def test_headline_number(self):
        text = message_of(lambda: mod03.run_headline_reportable(42))
        self.assertIn("run_headline_reportable", text)
        self.assertIn("stands refused", text)
        self.assertNotIn("not iterable", text)
        with self.assertRaises(ValueError):
            mod03.run_headline_reportable(42)

    def test_headline_none(self):
        with self.assertRaises(ValueError) as caught:
            mod03.run_headline_reportable(None)
        self.assertIn("stands refused", str(caught.exception))

    def test_headline_raising_list_reads_stored(self):
        record = mod03.make_archetype_record(archetype_id="stored-1")
        handed = RaisingIterList(["stored-1"])
        self.assertTrue(
            mod03.run_headline_reportable(handed, [record]))

    def test_work_credit_number(self):
        with self.assertRaises(ValueError) as caught:
            mod05.work_credit(42)
        self.assertIn("work_credit", str(caught.exception))
        self.assertIn("stands refused", str(caught.exception))
        self.assertNotIn("not iterable", str(caught.exception))

    def test_credit_work_number(self):
        with self.assertRaises(ValueError):
            mod05.credit_work(42)

    def test_accept_work_number(self):
        with self.assertRaises(ValueError):
            mod05.accept_work(42)

    def test_work_credit_raising_iter(self):
        with self.assertRaises(ValueError) as caught:
            mod05.work_credit(RaisingIter())
        self.assertIn("stands refused", str(caught.exception))

    def test_append_reading_number(self):
        with self.assertRaises(ValueError) as caught:
            mod07.append_reading(42, "c")
        self.assertIn("append_reading", str(caught.exception))
        self.assertIn("no reading stands appended", str(caught.exception))

    def test_append_reading_raising_iter(self):
        with self.assertRaises(ValueError) as caught:
            mod07.append_reading(RaisingIter(), "c")
        self.assertIn("no reading stands appended", str(caught.exception))

    def test_report_number(self):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.report(42)
        self.assertIn("report stands refused", str(caught.exception))

    def test_report_raising_iter(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.report(RaisingIter())

    def test_flip_number(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.flip_trial_record(candidate_forms=42)
        self.assertIn("candidate_forms", str(caught.exception))

    def test_flip_raising_iter(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.flip_trial_record(candidate_forms=RaisingIter())

    def test_controls_named_neighbours_hold(self):
        text = message_of(lambda: mod05.work_credit(["text-event"]))
        self.assertEqual(text, "a work event carries no agent identifier")
        text = message_of(lambda: mod07.append_reading("textlog", "c"))
        self.assertIn("no reading stands appended", text)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.report(["textfig"])

    def test_controls_plain_forms_hold(self):
        self.assertTrue(mod03.run_headline_reportable([]))
        result = mod04.flip_trial_record()
        self.assertEqual(
            result["candidate_forms"], ["per viewer form", "singular form"])
        self.assertFalse(result["run_result"])
        report = mod08.report([])
        self.assertEqual(report["figures"], [])


if __name__ == "__main__":
    unittest.main()
