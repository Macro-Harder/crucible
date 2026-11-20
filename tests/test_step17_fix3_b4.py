"""Step 17 fix wave 3, Builder 4 tests: Slice 4, the mod10
aggregate family. Rows FW3-04, FW3-15, FW3-16, FW3-21, FW3-43.

Each defect test reproduces the filing defect of its row on the
uncured tree (the landed tree carrying the Slice 1, Slice 2, and
Slice 3 cures, uncured for these rows). FW3-04 stands stated in
the open in the builder paper: its charged reading escape did
not reproduce on the uncured chain tree in isolation, on the
filing forms or on the Purple 5 form, so its tests stand as
controls pinning the served whole standing the reading path
already delivers, and no cure stands invented for it.
Standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod10

HUGE = 10 ** 5000


def delivery(**kw):
    base = {
        "simulated_day": 1,
        "viewer_id": "viewer-1",
        "joint_outcome_components": [1, 2, 3, 4],
        "component_denominators": [10, 10, 10, 10],
        "honest_share": 0.5,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0.5},
    }
    base.update(kw)
    return base


class LyingFloat(float):
    """A float whose comparison readings report every value as
    standing inside the closed unit range."""

    def __le__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False


class LyingInt(int):
    """An int whose comparison readings report every value as
    at or above zero."""

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return True


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)


class TestFW304HugeIntegerAggregate(Base):
    """FW3-04 (Medium, T17R2-04): the aggregate retention and
    reading doors judge a huge integer component in one stated
    form. On the uncured chain tree the reading path already
    serves the huge component whole, as these controls pin; the
    row stands reported in the open in the builder paper."""

    def test_huge_component_served_whole_at_reading(self):
        mod10.retain_daily_aggregate_deliveries(
            "huge-run",
            [delivery(joint_outcome_components=[HUGE, 0, 0, 0],
                      component_denominators=[HUGE, 1, 1, 1])])
        records = mod10.daily_aggregates_for_run("huge-run")
        self.assertEqual(
            records[0]["joint_outcome_components"][0], HUGE)

    def test_huge_denominator_served_whole_at_reading(self):
        mod10.retain_daily_aggregate_deliveries(
            "huge-den",
            [delivery(joint_outcome_components=[1, 0, 0, 0],
                      component_denominators=[HUGE, 1, 1, 1])])
        records = mod10.daily_aggregates_for_run("huge-den")
        self.assertEqual(
            records[0]["component_denominators"][0], HUGE)

    def test_filing_form_huge_component_judged_in_named_form(self):
        """The filing form carries a component above its own
        denominator, so on the cured tree it stands refused at
        retention in named form under the FW3-15 validator
        form, and no bare interpreter text stands delivered at
        any door of the act."""
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "huge-filing",
                [{"simulated_day": 2, "viewer_id": "v1",
                  "joint_outcome_components": [HUGE],
                  "component_denominators": [1.0]}])
        self.assertIn("in named form", str(caught.exception))
        self.assertNotIn(
            "Exceeds the limit", str(caught.exception))


class TestFW315ValidatorForm(Base):
    """FW3-15 (Medium, T17R2-15): aggregate retention, building,
    and rederivation hold their figures to the module own
    validator form, refusing an impossible component in named
    form at the door that takes it."""

    def test_component_above_denominator_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "imp-1",
                [delivery(joint_outcome_components=[11, 0, 0, 0])])
        self.assertIn(
            "daily aggregate delivery in named form",
            str(caught.exception))
        records = mod10.daily_aggregates_for_run("imp-1")
        self.assertIn("form", records[0])

    def test_negative_component_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "imp-2",
                [delivery(joint_outcome_components=[-1, 0, 0, 0])])
        self.assertIn(
            "daily aggregate delivery in named form",
            str(caught.exception))

    def test_negative_denominator_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "imp-3",
                [delivery(component_denominators=[-5, 1, 1, 1])])
        self.assertIn(
            "daily aggregate delivery in named form",
            str(caught.exception))

    def test_rederive_impossible_component_no_totals(self):
        result = mod10.rederive_regime_classification(
            [delivery(joint_outcome_components=[-5, 0, 0, 0])])
        self.assertIsNone(result)

    def test_control_ordinary_delivery_retained_and_valid(self):
        mod10.retain_daily_aggregate_deliveries("ok-1", [delivery()])
        records = mod10.daily_aggregates_for_run("ok-1")
        self.assertTrue(mod10.validate_daily_aggregates(records))

    def test_control_rederive_ordinary_totals(self):
        result = mod10.rederive_regime_classification([delivery()])
        self.assertEqual(result["component_totals"], [1, 2, 3, 4])


class TestFW316GatePassingShareForm(Base):
    """FW3-16 (Medium, T17R2-16): record_gate_passing_share
    judges its share handing in the stated share form, refusing
    a handing in no share form in named form."""

    def _refused(self, share):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share(
                "gate-run", "epoch-1", share)
        self.assertIn(
            "in no stated share form", str(caught.exception))
        self.assertEqual(
            mod10.gate_passing_shares_for_run("gate-run"), {})

    def test_nan_share_refused(self):
        self._refused(float("nan"))

    def test_share_above_one_refused(self):
        self._refused(2.5)

    def test_text_share_refused(self):
        self._refused("text")

    def test_none_share_refused(self):
        self._refused(None)

    def test_negative_share_refused(self):
        self._refused(-0.5)

    def test_proportion_negative_numerator_refused(self):
        self._refused({"numerator": -1, "denominator": 2})

    def test_control_plain_share_recorded(self):
        mod10.record_gate_passing_share("gate-ok", "epoch-1", 0.5)
        got = mod10.gate_passing_shares_for_run("gate-ok")
        self.assertEqual(got["epoch-1"]["share"], 0.5)

    def test_control_proportion_share_recorded(self):
        share = {"numerator": 2, "denominator": 3,
                 "computed_by": "MOD-05 Parley Core"}
        mod10.record_gate_passing_share("gate-ok2", "epoch-1", share)
        got = mod10.gate_passing_shares_for_run("gate-ok2")
        self.assertEqual(got["epoch-1"]["share"], share)

    def test_control_unit_shares_recorded(self):
        mod10.record_gate_passing_share("gate-ok3", "epoch-1", 0)
        mod10.record_gate_passing_share("gate-ok3", "epoch-2", 1)
        got = mod10.gate_passing_shares_for_run("gate-ok3")
        self.assertEqual(len(got), 2)


class TestFW321ShareStoredForm(Base):
    """FW3-21 (Medium, T17R2-21): the delivery share judge
    judges a share on its stored form, refusing a share outside
    the closed unit range or carrying a negative numerator in
    named form."""

    def test_lying_float_honest_share_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "lie-1", [delivery(honest_share=LyingFloat(5.0))])
        self.assertIn(
            "in no stated share form", str(caught.exception))

    def test_lying_float_gate_share_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "lie-2",
                [delivery(gate_passing_shares={
                    "epoch-1": LyingFloat(9.0)})])
        self.assertIn(
            "in no stated share form", str(caught.exception))

    def test_lying_negative_numerator_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "lie-3",
                [delivery(honest_share={
                    "numerator": LyingInt(-3), "denominator": 10})])
        self.assertIn(
            "in no stated share form", str(caught.exception))

    def test_proportion_above_unit_range_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "lie-4",
                [delivery(honest_share={
                    "numerator": 30, "denominator": 10})])
        self.assertIn(
            "in no stated share form", str(caught.exception))

    def test_control_plain_and_proportion_shares_retained(self):
        mod10.retain_daily_aggregate_deliveries("lie-ok", [delivery(
            honest_share={"numerator": 1, "denominator": 2})])
        records = mod10.daily_aggregates_for_run("lie-ok")
        self.assertEqual(
            records[0]["honest_share"],
            {"numerator": 1, "denominator": 2})


class TestFW343StoredQuotient(Base):
    """FW3-43 (Low, T17R2-43): the delivery share judge holds a
    stored quotient to the proportion form the module validator
    states, refusing a quotient in no finite form or
    disagreeing with its parts in named form."""

    def test_quotient_nan_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "q-1",
                [delivery(honest_share={
                    "numerator": 1, "denominator": 2,
                    "quotient": float("nan")})])
        self.assertIn(
            "in no stated share form", str(caught.exception))

    def test_quotient_disagreeing_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "q-2",
                [delivery(honest_share={
                    "numerator": 1, "denominator": 2,
                    "quotient": 0.9})])
        self.assertIn(
            "in no stated share form", str(caught.exception))

    def test_gate_quotient_disagreeing_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "q-3",
                [delivery(gate_passing_shares={"epoch-1": {
                    "numerator": 1, "denominator": 4,
                    "quotient": 0.5}})])
        self.assertIn(
            "in no stated share form", str(caught.exception))

    def test_control_quotient_agreeing_retained(self):
        mod10.retain_daily_aggregate_deliveries(
            "q-ok",
            [delivery(honest_share={
                "numerator": 1, "denominator": 2, "quotient": 0.5})])
        records = mod10.daily_aggregates_for_run("q-ok")
        self.assertEqual(records[0]["honest_share"]["quotient"], 0.5)


if __name__ == "__main__":
    unittest.main()
