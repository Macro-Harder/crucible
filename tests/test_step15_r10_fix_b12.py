import inspect
import unittest

import crucible.mod10 as mod10


class AlwaysEqual:
    """A value storing one thing whose equality reading answers
    True against everything."""

    def __init__(self, carried):
        self.carried = carried

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash(self.carried)


class LyingEqStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(self)


class LyingEqInt(int):
    def __new__(cls, stored):
        return int.__new__(cls, stored)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return int.__hash__(self)


class LyingDay(str):
    """A text day storing one text, reporting another through its
    string reading, and answering isdigit as handed."""

    def __new__(cls, stored, reported, digit_answer):
        obj = str.__new__(cls, stored)
        obj.reported = reported
        obj.digit_answer = digit_answer
        return obj

    def __str__(self):
        return self.reported

    def isdigit(self):
        return self.digit_answer


class ReportingStr(str):
    def __new__(cls, stored, reported):
        obj = str.__new__(cls, stored)
        obj.reported = reported
        return obj

    def __str__(self):
        return self.reported


RETAINED = {
    "run_identifier": "r10-b12-run",
    "simulated_day": 3,
    "store_kind": "sweep",
    "payload": "original",
    "run_values": {"count": 3, "tags": ["a", "b"]},
}


def handed_with(**changes):
    handed = dict(RETAINED)
    handed.update(changes)
    return handed


def delivery(day, viewer):
    return {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": [1, 1, 1, 1],
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 1,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 1},
    }


class TestR9016ResumeFinalComparison(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()
        mod10.retain_checkpoint(dict(RETAINED))

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_lying_equality_payload_value_refused(self):
        handed = handed_with(payload=AlwaysEqual("TAMPERED"))
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_defect_lying_equality_nested_in_dict_refused(self):
        handed = handed_with(
            run_values={"count": 3, "tags": ["a", AlwaysEqual("x")]})
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_defect_lying_equality_in_list_refused(self):
        handed = handed_with(
            run_values={"count": 3, "tags": [AlwaysEqual("a"), "b"]})
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_defect_lying_equality_text_payload_refused(self):
        handed = handed_with(payload=LyingEqStr("TAMPERED"))
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_defect_lying_equality_number_payload_refused(self):
        handed = handed_with(payload=LyingEqInt(9))
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_control_plain_exact_copy_resumes(self):
        resumed = mod10.resume_from_checkpoint(dict(RETAINED))
        self.assertEqual(dict.get(resumed, "payload"), "original")
        self.assertEqual(
            dict.get(resumed, "run_values"),
            {"count": 3, "tags": ["a", "b"]})

    def test_control_plain_tamper_refused(self):
        handed = handed_with(payload="TAMPERED")
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_control_plain_nested_tamper_refused(self):
        handed = handed_with(run_values={"count": 4, "tags": ["a", "b"]})
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_control_string_whole_day_form_resumes(self):
        handed = handed_with(simulated_day="3")
        resumed = mod10.resume_from_checkpoint(handed)
        self.assertEqual(dict.get(resumed, "payload"), "original")


class TestR9018DaySortKeyStoredText(unittest.TestCase):
    def test_defect_isdigit_lie_storing_digit_day_sorts_as_day(self):
        day = LyingDay("5", "zzz", False)
        self.assertEqual(
            mod10._day_sort_key((day, "viewer1")), (0, 5, "viewer1"))

    def test_defect_isdigit_lie_storing_text_day_keys_by_stored_text(self):
        day = LyingDay("notaday", "5", True)
        self.assertEqual(
            mod10._day_sort_key((day, "viewer1")),
            (1, 0, "notaday", "viewer1"))

    def test_defect_reported_day_text_not_in_fallback_key(self):
        day = ReportingStr("later", "zzz")
        self.assertEqual(
            mod10._day_sort_key((day, "viewer1")),
            (1, 0, "later", "viewer1"))

    def test_defect_reported_viewer_not_in_numbered_key(self):
        viewer = ReportingStr("v-real", "v-fake")
        self.assertEqual(
            mod10._day_sort_key((5, viewer)), (0, 5, "v-real"))

    def test_defect_reported_viewer_not_in_fallback_key(self):
        viewer = ReportingStr("v-real", "v-fake")
        self.assertEqual(
            mod10._day_sort_key(("later", viewer)),
            (1, 0, "later", "v-real"))

    def test_control_plain_digit_text_sorts_as_day(self):
        self.assertEqual(
            mod10._day_sort_key(("5", "viewer1")), (0, 5, "viewer1"))

    def test_control_int_day_sorts_as_day(self):
        self.assertEqual(
            mod10._day_sort_key((5, "viewer1")), (0, 5, "viewer1"))

    def test_control_parseable_unicode_digit_sorts_as_day(self):
        self.assertEqual(
            mod10._day_sort_key(("\u0665", "viewer1")), (0, 5, "viewer1"))


class TestR9019FallbackKeyDistinct(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_colon_pair_keys_distinct(self):
        left = mod10._day_sort_key(("a", "b:c"))
        right = mod10._day_sort_key(("a:b", "c"))
        self.assertEqual(left, (1, 0, "a", "b:c"))
        self.assertEqual(right, (1, 0, "a:b", "c"))
        self.assertNotEqual(left, right)

    def test_defect_none_day_and_text_none_keys_distinct(self):
        left = mod10._day_sort_key((None, "v1"))
        right = mod10._day_sort_key(("None", "v1"))
        self.assertEqual(left, (1, 0, "", "v1"))
        self.assertEqual(right, (1, 0, "None", "v1"))
        self.assertNotEqual(left, right)

    def test_defect_colon_pair_order_stable_across_retention_order(self):
        pair = [delivery("a", "b:c"), delivery("a:b", "c")]
        mod10.retain_daily_aggregate_deliveries("r10-b12-tie-1", pair)
        first = [
            (record["simulated_day"], record["viewer_id"])
            for record in mod10.daily_aggregates_for_run("r10-b12-tie-1")]
        mod10.retain_daily_aggregate_deliveries(
            "r10-b12-tie-2", list(reversed(pair)))
        second = [
            (record["simulated_day"], record["viewer_id"])
            for record in mod10.daily_aggregates_for_run("r10-b12-tie-2")]
        self.assertEqual(first, [("a", "b:c"), ("a:b", "c")])
        self.assertEqual(first, second)

    def test_defect_none_pair_order_stable_across_retention_order(self):
        pair = [delivery(None, "v1"), delivery("None", "v1")]
        mod10.retain_daily_aggregate_deliveries("r10-b12-none-1", pair)
        first = [
            (record["simulated_day"], record["viewer_id"])
            for record in mod10.daily_aggregates_for_run("r10-b12-none-1")]
        mod10.retain_daily_aggregate_deliveries(
            "r10-b12-none-2", list(reversed(pair)))
        second = [
            (record["simulated_day"], record["viewer_id"])
            for record in mod10.daily_aggregates_for_run("r10-b12-none-2")]
        self.assertEqual(first, [(None, "v1"), ("None", "v1")])
        self.assertEqual(first, second)


class TestR9020FallbackOrderingStated(unittest.TestCase):
    def test_defect_day_sort_key_docstring_states_ordering(self):
        raw = inspect.getdoc(mod10._day_sort_key)
        self.assertIsNotNone(raw)
        doc = " ".join(raw.split())
        self.assertIn("after all numbered days", doc)
        self.assertIn("stored text of the day", doc)
        self.assertIn("stored text of the viewer", doc)

    def test_defect_aggregate_acts_state_ordering(self):
        for act in (mod10.daily_aggregates_for_run,
                    mod10.aggregate_manifest_for_run):
            raw = inspect.getdoc(act)
            self.assertIsNotNone(raw)
            doc = " ".join(raw.split())
            self.assertIn("numbered days first", doc)

    def test_control_mixed_placements_match_stated_ordering(self):
        items = [
            (100, "v"), ("-1", "v"), (-1, "v"), ("+2", "v"),
            ("\u2460", "v"), ("later", "v"), (10, "v"),
        ]
        ordered = [
            day for day, viewer in sorted(items, key=mod10._day_sort_key)]
        self.assertEqual(
            ordered, [-1, 10, 100, "+2", "-1", "later", "\u2460"])

    def test_control_text_minus_one_after_day_100_int_minus_one_first(self):
        items = [(100, "v"), ("-1", "v"), (-1, "v")]
        ordered = [
            day for day, viewer in sorted(items, key=mod10._day_sort_key)]
        self.assertEqual(ordered, [-1, 100, "-1"])

    def test_control_nontext_day_heads_the_later_group(self):
        items = [("later", "v"), (None, "v"), (5, "v")]
        ordered = [
            day for day, viewer in sorted(items, key=mod10._day_sort_key)]
        self.assertEqual(ordered, [5, None, "later"])


class TestR8025CrashCureKept(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_control_unparseable_unicode_digit_no_raise_fallback(self):
        for char in ("\u2075", "\u00b2", "\u00b3", "\u2460"):
            with self.subTest(code=hex(ord(char))):
                key = mod10._day_sort_key((char, "viewer1"))
                self.assertEqual(key, (1, 0, char, "viewer1"))

    def test_control_unparseable_day_aggregates_whole(self):
        mod10.retain_daily_aggregate_deliveries(
            "r10-b12-agg", [delivery("\u2075", "viewer1")])
        records = mod10.daily_aggregates_for_run("r10-b12-agg")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["simulated_day"], "\u2075")
        manifest = mod10.aggregate_manifest_for_run("r10-b12-agg")
        self.assertEqual(len(manifest), 1)

    def test_control_nondigit_text_fallback_separate_segments(self):
        self.assertEqual(
            mod10._day_sort_key(("later", "viewer1")),
            (1, 0, "later", "viewer1"))


if __name__ == "__main__":
    unittest.main()
