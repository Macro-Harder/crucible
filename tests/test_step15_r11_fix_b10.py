# Step 15 rerun, fix wave 10, Builder 10 pins.
# Rows R10-029, R10-030, R10-031, R10-032, R10-051, R10-054, and
# the crucible/mod10.py limb of R10-033, all at crucible/mod10.py.
import unittest

import crucible.mod10 as mod10


class LyingStr(str):
    def __new__(cls, stored, reported=None):
        obj = str.__new__(cls, stored)
        obj.reported = stored if reported is None else reported
        return obj

    def __str__(self):
        return self.reported


def delivery(day, viewer, components=(1, 2, 3, 4)):
    return {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": list(components),
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 1,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 1},
    }


def identities(run_id, pairs):
    mod10.retain_daily_aggregate_deliveries(
        run_id, [delivery(day, viewer) for day, viewer in pairs])
    return [
        record["record_identity"]
        for record in mod10.daily_aggregates_for_run(run_id)]


class B10Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestR10029IdentityDistinct(B10Base):
    def test_colon_pair_identities_distinct(self):
        found = identities("runA", [("a", "b:c"), ("a:b", "c")])
        self.assertEqual(len(found), 2)
        self.assertNotEqual(found[0], found[1])

    def test_colon_pair_manifest_identities_distinct(self):
        identities("runA", [("a", "b:c"), ("a:b", "c")])
        manifest = mod10.aggregate_manifest_for_run("runA")
        found = [entry["record_identity"] for entry in manifest]
        self.assertEqual(len(found), 2)
        self.assertNotEqual(found[0], found[1])

    def test_none_day_and_text_none_identities_distinct(self):
        found = identities("runB", [(None, "v1"), ("None", "v1")])
        self.assertEqual(len(found), 2)
        self.assertNotEqual(found[0], found[1])

    def test_none_viewer_and_text_none_identities_distinct(self):
        found = identities("runV", [(1, None), (1, "None")])
        self.assertEqual(len(found), 2)
        self.assertNotEqual(found[0], found[1])

    def test_viewer_identity_reads_stored_not_reported_text(self):
        viewer = LyingStr("storedname", "reportedname")
        found = identities("runZ", [("a", viewer)])
        self.assertEqual(len(found), 1)
        self.assertIn("storedname", found[0])
        self.assertNotIn("reportedname", found[0])

    def test_day_identity_reads_stored_not_reported_text(self):
        day = LyingStr("5", "reportedname")
        found = identities("runW", [(day, "v1")])
        self.assertEqual(len(found), 1)
        self.assertIn("5", found[0])
        self.assertNotIn("reportedname", found[0])

    def test_same_stored_pair_identity_stable(self):
        first = identities("runS", [("a", "v")])
        mod10.reset_stores()
        second = identities("runS", [("a", "v")])
        self.assertEqual(first, second)


class TestR10030SortTieBreaker(B10Base):
    FORMS = (5, "5", "05", "٥", "５")

    def test_numbered_forms_share_numeric_value_not_key(self):
        keys = [mod10._day_sort_key((day, "v")) for day in self.FORMS]
        for key in keys:
            self.assertEqual(key[0], 0)
            self.assertEqual(key[1], 5)
        self.assertEqual(len(set(keys)), len(self.FORMS))

    def test_int_day_key_exact_new_form(self):
        self.assertEqual(
            mod10._day_sort_key((5, "viewer1")),
            (0, 5, "int:5", "viewer1", "str:7:viewer1"))

    def test_digit_text_day_key_exact_new_form(self):
        self.assertEqual(
            mod10._day_sort_key(("5", "viewer1")),
            (0, 5, "str:1:5", "viewer1", "str:7:viewer1"))

    def test_parseable_unicode_digit_day_key_exact_new_form(self):
        self.assertEqual(
            mod10._day_sort_key(("٥", "viewer1")),
            (0, 5, "str:1:٥", "viewer1", "str:7:viewer1"))

    def test_numbered_order_stable_across_input_order(self):
        items = [(day, "v") for day in self.FORMS]
        forward = sorted(items, key=mod10._day_sort_key)
        backward = sorted(
            list(reversed(items)), key=mod10._day_sort_key)
        self.assertEqual(forward, backward)

    def test_identity_distinct_for_int_and_digit_text_forms(self):
        first = identities("runN", [(5, "v")])
        mod10.reset_stores()
        second = identities("runN", [("5", "v")])
        self.assertNotEqual(first, second)

    def test_control_day_five_orders_before_day_six_each_form(self):
        for day in (5, "5"):
            with self.subTest(day=day):
                self.assertLess(
                    mod10._day_sort_key((day, "v")),
                    mod10._day_sort_key((6, "v")))

    def test_control_int_minus_one_first_and_fallback_after(self):
        items = [(100, "v"), ("-1", "v"), (-1, "v")]
        ordered = [
            day for day, viewer in sorted(
                items, key=mod10._day_sort_key)]
        self.assertEqual(ordered, [-1, 100, "-1"])


class TestR10031RetentionWholeDay(B10Base):
    def test_int_and_digit_text_day_count_once(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "runDup", [delivery(1, "v"), delivery("1", "v")])
        self.assertEqual(count, 1)
        records = mod10.daily_aggregates_for_run("runDup")
        self.assertEqual(len(records), 1)

    def test_rederivation_counts_day_once_amounts_not_doubled(self):
        mod10.retain_daily_aggregate_deliveries(
            "runDup", [delivery(1, "v"), delivery("1", "v")])
        records = mod10.daily_aggregates_for_run("runDup")
        result = mod10.rederive_regime_classification(records)
        self.assertEqual(result["days"], 1)
        self.assertEqual(result["component_totals"], [1, 2, 3, 4])

    def test_leading_zero_text_day_count_once(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "runZ1", [delivery(1, "v"), delivery("01", "v")])
        self.assertEqual(count, 1)

    def test_signed_and_spaced_text_day_count_once(self):
        for form in ("+1", " 1 "):
            with self.subTest(form=form):
                mod10.reset_stores()
                count = mod10.retain_daily_aggregate_deliveries(
                    "runZ2", [delivery(1, "v"), delivery(form, "v")])
                self.assertEqual(count, 1)

    def test_control_distinct_days_count_separately(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "runD", [delivery(1, "v"), delivery(2, "v")])
        self.assertEqual(count, 2)

    def test_control_same_day_distinct_viewers_count_separately(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "runDv", [delivery(1, "v"), delivery("1", "w")])
        self.assertEqual(count, 2)


class TestR10032NonTextSegments(B10Base):
    def test_numbered_viewer_forms_take_distinct_keys(self):
        keys = [
            mod10._day_sort_key((5, viewer))
            for viewer in (None, "", 123)]
        self.assertEqual(len(set(keys)), 3)

    def test_fallback_day_forms_take_distinct_keys(self):
        keys = [
            mod10._day_sort_key((day, "v"))
            for day in (None, "", 1.5, True, 0.0)]
        for key in keys:
            self.assertEqual(key[0], 1)
        self.assertEqual(len(set(keys)), 5)

    def test_fallback_key_exact_new_form(self):
        self.assertEqual(
            mod10._day_sort_key(("later", "viewer1")),
            (1, 0, "later", "str:5:later",
             "viewer1", "str:7:viewer1"))

    def test_unparseable_unicode_digit_key_new_form_no_raise(self):
        self.assertEqual(
            mod10._day_sort_key(("⁵", "viewer1")),
            (1, 0, "⁵", "str:1:⁵",
             "viewer1", "str:7:viewer1"))

    def test_viewer_order_stable_across_retention_order(self):
        pair = [delivery("later", None), delivery("later", "")]
        mod10.retain_daily_aggregate_deliveries("runO1", pair)
        first = [
            record["viewer_id"]
            for record in mod10.daily_aggregates_for_run("runO1")]
        mod10.retain_daily_aggregate_deliveries(
            "runO2", list(reversed(pair)))
        second = [
            record["viewer_id"]
            for record in mod10.daily_aggregates_for_run("runO2")]
        self.assertEqual(first, second)
        self.assertEqual(first, [None, ""])

    def test_day_order_stable_across_retention_order(self):
        pair = [delivery(None, "v"), delivery("", "v")]
        mod10.retain_daily_aggregate_deliveries("runO3", pair)
        first = [
            record["simulated_day"]
            for record in mod10.daily_aggregates_for_run("runO3")]
        mod10.retain_daily_aggregate_deliveries(
            "runO4", list(reversed(pair)))
        second = [
            record["simulated_day"]
            for record in mod10.daily_aggregates_for_run("runO4")]
        self.assertEqual(first, second)
        self.assertEqual(first, [None, ""])


class TestR10051ResumeDayForm(B10Base):
    MANIFEST = {
        "run_identifier": "runL",
        "simulated_day": 1,
        "store_kind": "sweep",
        "payload": "original",
    }

    def setUp(self):
        super().setUp()
        mod10.retain_checkpoint(dict(self.MANIFEST))

    def handed(self, day):
        handed = dict(self.MANIFEST)
        handed["simulated_day"] = day
        return handed

    def test_text_day_resumes_and_returns_retained_day_form(self):
        resumed = mod10.resume_from_checkpoint(self.handed("1"))
        self.assertEqual(resumed["simulated_day"], 1)
        self.assertIs(type(resumed["simulated_day"]), int)
        self.assertEqual(resumed, self.MANIFEST)

    def test_other_text_whole_day_forms_return_retained_form(self):
        for form in ("01", "+1", " 1 "):
            with self.subTest(form=form):
                resumed = mod10.resume_from_checkpoint(
                    self.handed(form))
                self.assertEqual(resumed["simulated_day"], 1)
                self.assertIs(type(resumed["simulated_day"]), int)

    def test_float_day_refused_in_integrity_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(self.handed(1.0))
        self.assertIn(
            "checkpoint integrity refusal", str(caught.exception))

    def test_bool_day_refused_in_integrity_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(self.handed(True))
        self.assertIn(
            "checkpoint integrity refusal", str(caught.exception))

    def test_checkpoint_state_at_rejects_float_and_bool_queries(self):
        state = {"agent_states": "stated"}
        mod10.retain_checkpoint({
            "run_identifier": "runS1", "simulated_day": 1,
            "checkpoint_state": state})
        self.assertEqual(
            mod10.checkpoint_state_at("runS1", 1), state)
        self.assertEqual(
            mod10.checkpoint_state_at("runS1", "1"), state)
        self.assertIsNone(mod10.checkpoint_state_at("runS1", 1.0))
        self.assertIsNone(mod10.checkpoint_state_at("runS1", True))

    def test_control_exact_copy_resumes(self):
        resumed = mod10.resume_from_checkpoint(dict(self.MANIFEST))
        self.assertEqual(resumed, self.MANIFEST)

    def test_control_tampered_copy_refused(self):
        handed = dict(self.MANIFEST)
        handed["payload"] = "TAMPERED"
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(handed)


class TestR10054BytearrayEquality(B10Base):
    MANIFEST = {
        "run_identifier": "runBA",
        "simulated_day": 3,
        "store_kind": "sweep",
        "payload": bytearray(b"abc"),
    }

    def test_equal_bytearray_checkpoint_resumes(self):
        mod10.retain_checkpoint(dict(self.MANIFEST))
        handed = dict(self.MANIFEST)
        handed["payload"] = bytearray(b"abc")
        self.assertIsNot(
            handed["payload"], self.MANIFEST["payload"])
        resumed = mod10.resume_from_checkpoint(handed)
        self.assertEqual(bytes(resumed["payload"]), b"abc")

    def test_base_value_eq_bytearray_forms(self):
        self.assertTrue(mod10._base_value_eq(
            bytearray(b"abc"), bytearray(b"abc")))
        self.assertFalse(mod10._base_value_eq(
            bytearray(b"abc"), bytearray(b"abd")))
        self.assertTrue(mod10._base_value_eq(
            memoryview(b"abc"), memoryview(b"abc")))
        self.assertTrue(mod10._base_value_eq(
            b"abc", bytearray(b"abc")))

    def test_control_differing_bytearray_checkpoint_refused(self):
        mod10.retain_checkpoint(dict(self.MANIFEST))
        handed = dict(self.MANIFEST)
        handed["payload"] = bytearray(b"abd")
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(handed)


class TestR10033Mod10ResolverLimb(B10Base):
    WORDS = (
        "am", "ga", "gm", "gr", "oa", "og", "om", "or",
        "pa", "pg", "pm", "ra", "rg", "rm", "rr")

    def test_five_drop_words_resolve_to_program(self):
        for word in self.WORDS:
            with self.subTest(word=word):
                self.assertEqual(
                    mod10._resolve_actor_word(word), "program")

    def test_five_drop_words_normalise_to_program(self):
        for word in self.WORDS:
            with self.subTest(word=word):
                self.assertEqual(
                    mod10._normalised_actor(word), "program")

    def test_flag_act_records_program_for_pm(self):
        record = {"run_id": "runF", "retention_tier": "Tier 2"}
        promoted = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 3", actor="pm",
            inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertEqual(
            promoted["flag_evaluation"]["actor"], "program")
        self.assertEqual(promoted["retention_tier"], "Tier 3")

    def test_all_two_letter_words_agree_with_mod14_resolver(self):
        import itertools

        import crucible.mod14 as mod14
        for first, second in itertools.product(
                "abcdefghijklmnopqrstuvwxyz", repeat=2):
            word = first + second
            with self.subTest(word=word):
                self.assertEqual(
                    mod10._resolve_actor_word(word),
                    mod14._resolve_actor_word(word))

    def test_controls_resolver_standing_kept(self):
        self.assertEqual(mod10._resolve_actor_word("program"),
                         "program")
        self.assertEqual(mod10._resolve_actor_word("person"),
                         "person")
        self.assertEqual(mod10._resolve_actor_word("zz"), "zz")


if __name__ == "__main__":
    unittest.main()
