"""Step 17 fix wave 1, Builder 2 tests (Slice 2).

Rows covered: FW-17 (retain width bound), FW-18 (recorder
retention and reading growth form), FW-21 (store identity
judged on the stored text form), FW-22 (retention held to the
stated validation, and the aggregate delivery day refusal),
FW-26 (daily aggregate reading paths return copies apart),
FW-33 (daily aggregate validator impossible components, and
the retention day key), FW-34 (replacement delivery standing
and the retention return count).

Each defect test stands written against the filing defect on
the base tree at product head
9f938470807f90b7c8c6d9882fde1105c807e0a1, to fail there for
the reason its builder paper states, and to pass on the fixed
tree. Control tests that pass on both trees stand marked as
controls in the builder paper.
"""
import unittest

from crucible import mod01
from crucible import mod10


def _delivery(day=1, viewer="v1", components=(1, 0, 0, 0),
              denominators=(1, 1, 1, 1), shares=None):
    return {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": list(components),
        "component_denominators": list(denominators),
        "honest_share": 0,
        "epochs_ending_on_day": ["e1"],
        "gate_passing_shares": (
            {"e1": 0} if shares is None else shares),
        "divergence_companion": {"nil_divergence_components": []},
    }


class _LyingStr(str):
    """A text identifier whose equality always answers True and
    whose hash is the hash of another identifier, as filing
    R4-01 states the hostile handing."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash("run-1")


class _EvilStr(str):
    """A text identifier whose equality always answers True and
    whose hash is the hash of the identifier retained before
    it, as filing P4-F08 states the hostile handing."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash("a")


class TestFW17WidthBound(unittest.TestCase):

    def test_wide_flat_record_refused_in_named_form(self):
        store = mod10.new_store("sweep")
        record = {"run_id": "wide-1"}
        for position in range(20000):
            record["k" + str(position)] = position
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(record)
        self.assertIn("width", str(caught.exception))
        self.assertEqual(store.index(), [])

    def test_wide_nested_record_refused_in_named_form(self):
        store = mod10.new_store("sweep")
        record = {
            "run_id": "wide-2",
            "items": [[position] for position in range(6000)],
        }
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(record)
        self.assertIn("width", str(caught.exception))
        self.assertEqual(store.index(), [])

    def test_ordinary_record_retained(self):
        store = mod10.new_store("sweep")
        record = {"run_id": "plain-1"}
        for position in range(100):
            record["k" + str(position)] = position
        store.retain_run_record(record)
        self.assertEqual(
            store.read_run_record("plain-1")["k99"], 99)


class TestFW18GrowthForm(unittest.TestCase):

    def _counting_store(self, size=300):
        store = mod10.new_store("sweep")
        for position in range(size):
            store.retain_run_record(
                {"run_id": "run-%04d" % position, "v": position})
        return store

    def test_read_does_not_scan_the_whole_store(self):
        store = self._counting_store()
        calls = []
        original = mod10._base_value_eq

        def counting(left, right):
            calls.append(1)
            return original(left, right)

        mod10._base_value_eq = counting
        try:
            record = store.read_run_record("run-0299")
        finally:
            mod10._base_value_eq = original
        self.assertEqual(record["v"], 299)
        self.assertLessEqual(len(calls), 5)

    def test_missing_read_does_not_scan_the_whole_store(self):
        store = self._counting_store()
        calls = []
        original = mod10._base_value_eq

        def counting(left, right):
            calls.append(1)
            return original(left, right)

        mod10._base_value_eq = counting
        try:
            self.assertFalse(store.has_run_record("run-absent"))
        finally:
            mod10._base_value_eq = original
        self.assertLessEqual(len(calls), 5)

    def test_duplicate_judgement_does_not_scan_the_whole_store(self):
        store = self._counting_store()
        calls = []
        original = mod10._base_value_eq

        def counting(left, right):
            calls.append(1)
            return original(left, right)

        mod10._base_value_eq = counting
        try:
            with self.assertRaises(ValueError):
                store.retain_run_record(
                    {"run_id": "run-0100", "v": -1})
        finally:
            mod10._base_value_eq = original
        self.assertLessEqual(len(calls), 5)
        self.assertEqual(store.read_run_record("run-0100")["v"], 100)


class TestFW21StoredTextIdentity(unittest.TestCase):

    def test_lying_identifier_kept_apart_from_the_genuine_run(self):
        store = mod10.new_store("sweep")
        store.retain_run_record({"run_id": "run-1", "v": "GENUINE"})
        store.retain_run_record(
            {"run_id": _LyingStr("other"), "v": "ATTACKER"})
        self.assertEqual(
            [str(item) for item in store.index()],
            ["run-1", "other"])
        self.assertEqual(
            store.read_run_record("run-1")["v"], "GENUINE")
        self.assertEqual(
            store.read_run_record("other")["v"], "ATTACKER")
        self.assertTrue(store.has_run_record("other"))

    def test_record_read_back_under_the_same_evil_identifier(self):
        store = mod10.new_store("sweep")
        store.retain_run_record({"run_id": "a", "v": "FIRST"})
        store.retain_run_record(
            {"run_id": _EvilStr("zzz"), "v": "SECOND"})
        self.assertEqual(
            [str(item) for item in store.index()], ["a", "zzz"])
        self.assertEqual(store.read_run_record("a")["v"], "FIRST")
        self.assertEqual(
            store.read_run_record(_EvilStr("zzz"))["v"], "SECOND")
        self.assertEqual(store.read_run_record("zzz")["v"], "SECOND")

    def test_plain_duplicate_still_refused(self):
        store = mod10.new_store("sweep")
        store.retain_run_record({"run_id": "run-1", "v": "GENUINE"})
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-1", "v": "SECOND"})
        self.assertEqual(
            store.read_run_record("run-1")["v"], "GENUINE")


class TestFW22StatedValidation(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_form4_record_missing_a_required_field_refused(self):
        record = mod01.build_run_record()
        del record["population_size"]
        self.assertFalse(mod01.validate_record("4", record))
        store = mod10.new_store("sweep")
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(record)
        self.assertIn("validation", str(caught.exception))
        self.assertEqual(store.index(), [])

    def test_valid_form4_record_retained(self):
        record = mod01.build_run_record()
        self.assertTrue(mod01.validate_record("4", record))
        store = mod10.new_store("sweep")
        store.retain_run_record(record)
        read_back = store.read_run_record(record["run_identifier"])
        self.assertEqual(
            read_back["population_size"],
            record["population_size"])

    def test_plain_small_record_still_retained(self):
        store = mod10.new_store("sweep")
        store.retain_run_record({"run_id": "small-1", "v": 1})
        self.assertEqual(store.read_run_record("small-1")["v"], 1)

    def test_delivery_with_no_day_refused_in_named_form(self):
        delivery = _delivery()
        del delivery["simulated_day"]
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "run-noday", [delivery])
        self.assertIn("day", str(caught.exception))
        aggregates = mod10.daily_aggregates_for_run("run-noday")
        self.assertEqual(aggregates[0].get("form"), mod10.FORM_ONLY)

    def test_delivery_with_none_day_refused_in_named_form(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_aggregate_deliveries(
                "run-noneday", [_delivery(day=None)])

    def test_delivery_with_nan_day_refused_in_named_form(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_aggregate_deliveries(
                "run-nanday", [_delivery(day=float("nan"))])

    def test_usable_day_forms_still_retained(self):
        for position, day in enumerate(
                (1, 0, -1, 1.0, True, "1", "abc")):
            count = mod10.retain_daily_aggregate_deliveries(
                "run-days-" + str(position), [_delivery(day=day)])
            self.assertEqual(count, 1)


class TestFW26CopiesApart(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_mutating_a_read_result_leaves_the_retained_shares(self):
        delivery = _delivery(shares={"e1": {"nested": 1}})
        mod10.retain_daily_aggregate_deliveries("runA", [delivery])
        first = mod10.daily_aggregates_for_run("runA")
        first[0]["gate_passing_shares"]["e1"]["nested"] = 999
        first[0]["gate_passing_share_per_epoch"]["e1"]["nested"] = 888
        second = mod10.daily_aggregates_for_run("runA")
        self.assertEqual(
            second[0]["gate_passing_shares"], {"e1": {"nested": 1}})
        self.assertEqual(
            second[0]["gate_passing_share_per_epoch"],
            {"e1": {"nested": 1}})

    def test_mutating_components_and_epochs_stays_apart(self):
        mod10.retain_daily_aggregate_deliveries(
            "runB", [_delivery()])
        first = mod10.daily_aggregates_for_run("runB")
        first[0]["joint_outcome_components"][0] = 777
        first[0]["epochs_ending_on_day"].append("evil")
        second = mod10.daily_aggregates_for_run("runB")
        self.assertEqual(
            second[0]["joint_outcome_components"], [1, 0, 0, 0])
        self.assertEqual(second[0]["epochs_ending_on_day"], ["e1"])


class TestFW33ValidatorAndDayKey(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def _row(self, components, denominators):
        return {
            "run_id": "run-v",
            "viewer_id": "v1",
            "joint_outcome_components": list(components),
            "component_denominators": list(denominators),
        }

    def test_negative_component_refused(self):
        row = self._row([-5, 0, 0, 0], [1, 1, 1, 1])
        self.assertFalse(mod10.validate_daily_aggregates([row]))
        failures = mod10.daily_aggregates_validation_failures([row])
        self.assertTrue(
            any("component" in failure for failure in failures))

    def test_component_above_denominator_refused(self):
        row = self._row([10, 0, 0, 0], [1, 1, 1, 1])
        self.assertFalse(mod10.validate_daily_aggregates([row]))

    def test_negative_denominator_refused(self):
        row = self._row([0, 0, 0, 0], [-1, 1, 1, 1])
        self.assertFalse(mod10.validate_daily_aggregates([row]))

    def test_valid_row_still_validates(self):
        row = self._row([1, 0, 0, 0], [1, 1, 1, 1])
        self.assertTrue(mod10.validate_daily_aggregates([row]))
        self.assertEqual(
            mod10.daily_aggregates_validation_failures([row]), [])

    def test_int_day_and_text_day_stand_apart(self):
        deliveries = [
            _delivery(day=1, components=(1, 0, 0, 0),
                      denominators=(4, 4, 4, 4)),
            _delivery(day="1", components=(2, 0, 0, 0),
                      denominators=(4, 4, 4, 4)),
        ]
        mod10.retain_daily_aggregate_deliveries(
            "run-days", deliveries)
        aggregates = mod10.daily_aggregates_for_run("run-days")
        served = sorted(
            tuple(record["joint_outcome_components"])
            for record in aggregates)
        self.assertEqual(
            served, [(1, 0, 0, 0), (2, 0, 0, 0)])

    def test_same_day_form_still_one_delivery(self):
        mod10.retain_daily_aggregate_deliveries(
            "run-same", [_delivery(day=1)])
        mod10.retain_daily_aggregate_deliveries(
            "run-same",
            [_delivery(day=1, components=(3, 0, 0, 0))])
        aggregates = mod10.daily_aggregates_for_run("run-same")
        self.assertEqual(len(aggregates), 1)
        self.assertEqual(
            aggregates[0]["joint_outcome_components"], [3, 0, 0, 0])


class TestFW34ReplacementStandingAndCount(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_retention_return_counts_the_deliveries_handed_in(self):
        first = mod10.retain_daily_aggregate_deliveries(
            "runX", [
                _delivery(day=1, components=(1, 2, 3, 4),
                          denominators=(10, 10, 10, 10)),
                _delivery(day=2, components=(10, 0, 0, 0),
                          denominators=(10, 10, 10, 10)),
            ])
        self.assertEqual(first, 2)
        second = mod10.retain_daily_aggregate_deliveries(
            "runX", [
                _delivery(day=1, components=(9, 9, 9, 9),
                          denominators=(10, 10, 10, 10)),
            ])
        self.assertEqual(second, 1)

    def test_replacement_delivery_states_its_standing_truly(self):
        mod10.retain_daily_aggregate_deliveries(
            "runY", [_delivery(day=1, components=(1, 0, 0, 0))])
        mod10.retain_daily_aggregate_deliveries(
            "runY", [_delivery(day=1, components=(9, 0, 0, 0))])
        aggregates = mod10.daily_aggregates_for_run("runY")
        self.assertEqual(len(aggregates), 1)
        self.assertEqual(
            aggregates[0]["joint_outcome_components"], [9, 0, 0, 0])
        self.assertNotEqual(
            aggregates[0]["amendment_standing"],
            "as originally written")
        self.assertIn(
            "replaced", aggregates[0]["amendment_standing"])

    def test_first_delivery_keeps_the_original_standing(self):
        mod10.retain_daily_aggregate_deliveries(
            "runZ", [_delivery(day=1)])
        aggregates = mod10.daily_aggregates_for_run("runZ")
        self.assertEqual(
            aggregates[0]["amendment_standing"],
            "as originally written")

    def test_replacement_inside_one_call_states_its_standing(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "runW", [
                _delivery(day=1, components=(1, 0, 0, 0)),
                _delivery(day=1, components=(5, 0, 0, 0)),
            ])
        self.assertEqual(count, 2)
        aggregates = mod10.daily_aggregates_for_run("runW")
        self.assertEqual(len(aggregates), 1)
        self.assertEqual(
            aggregates[0]["joint_outcome_components"], [5, 0, 0, 0])
        self.assertIn(
            "replaced", aggregates[0]["amendment_standing"])


if __name__ == "__main__":
    unittest.main()
