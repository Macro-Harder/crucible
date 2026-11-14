"""Step 14 re-run pins for builder B7, MOD-10 recorder and stores.

Each test pins one weighed item on the MOD-10 surface: the money
name and the Amount and Currency shape in letter and digit dresses
(R5-A6-01 at MOD-10), and barred keys split inside their marker
words at the MOD-10 runner (R5-A6-05 at MOD-10). The file uses
plain simulated values only. Tests reset the module stores around
themselves so their standing does not depend on suite order.
"""
import unittest

import crucible.mod10 as mod10


MONEY_NAME_DRESSES = (
    "r\u00e9almoneyvalue",
    "realm\u00f3neyvalue",
    "r\u00ebal_money_value",
    "\uff52ealmoneyvalue",
    "\uff52\uff45\uff41\uff4c\uff4d\uff4f\uff4e\uff45\uff59"
    "\uff56\uff41\uff4c\uff55\uff45",
    "re\u0430lmoneyvalue",
    "realm\u043eneyvalue",
    "realm\u03bfneyvalue",
    "\u0440\u0435\u0430\u043b\u043c\u0430\u043d\u0438value",
    "real5moneyvalue",
    "real\u0665moneyvalue",
    "real\uff15moneyvalue",
    "rea1moneyvalue",
    "re4lmoneyvalue",
)

SHAPE_DRESSES = (
    {"Amo\u00fcnt": 5, "Curr\u00e9ncy": "USD"},
    {"\uff21\uff4d\uff4f\uff55\uff4e\uff54": 5,
     "\uff23\uff55\uff52\uff52\uff45\uff4e\uff43\uff59": "USD"},
    {"\u0410mount": 5, "Currency": "USD"},
    {"Amo5unt": 5, "Curr5ency": "USD"},
    {"Amount5": 5, "Currency5": "USD"},
)

BARRED_SPLIT_KEYS = (
    "can ary", "can.ary", "can/ary", "can-ary", "cana ry",
    "ground truth", "ground-truth", "ground/truth",
    "ground truth field",
    "member ship", "member.ship", "member-ship",
    "is honest", "is-honest", "la bel", "sleep er",
    "can\u00e1ry", "c\u00e1nary_token",
    "\uff43anary",
    "can\u0430ry",
    "cana\u200bry",
    "can\u00adary",
    "cana\u0301ry",
    "ground\u200btruth", "memb\u200bership",
    "MEMBERSH\u0130P",
    "can4ary", "groun5dtruth", "member5ship",
)


class B07Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestMoneyDressesAtRetention(B07Base):
    def test_r5a601_money_name_dresses_refused_at_retention(self):
        for index, name in enumerate(MONEY_NAME_DRESSES):
            store = mod10.RecorderStore(store_kind="sweep")
            record = {"run_id": "run-b07-money-%d" % index, name: 500}
            with self.assertRaises(ValueError, msg=name):
                store.retain_run_record(record)

    def test_r5a601_shape_dresses_refused_at_retention(self):
        for index, shape in enumerate(SHAPE_DRESSES):
            store = mod10.RecorderStore(store_kind="sweep")
            record = {"run_id": "run-b07-shape-%d" % index,
                      "stake": dict(shape)}
            with self.assertRaises(ValueError, msg=repr(shape)):
                store.retain_run_record(record)

    def test_r5a601_controls_hold(self):
        store = mod10.RecorderStore(store_kind="sweep")
        plain_name = "real_" + "money_value"
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-b07-plain", plain_name: 5})
        kept_none = store.retain_run_record(
            {"run_id": "run-b07-none", "real" + "moneyvalue": None})
        self.assertEqual(kept_none["run_id"], "run-b07-none")
        kept_amount_only = store.retain_run_record(
            {"run_id": "run-b07-amount-only", "amount": 5})
        self.assertEqual(kept_amount_only["run_id"], "run-b07-amount-only")
        kept_lawful = store.retain_run_record({
            "run_id": "run-b07-lawful",
            "caf\u00e9_menu": "stated",
            "na\u00efve_notes": "stated",
            "amount_notes": 5,
            "currency_notes": "stated",
        })
        self.assertEqual(kept_lawful["run_id"], "run-b07-lawful")


class TestBarredSplitKeysAtRunner(B07Base):
    def view_record(self, contents):
        return {
            "run_identifier": "run-b07-view",
            "viewer_identifier": "viewer-1",
            "simulated_day": 5,
            "scheduling_position_identifier": "position-1",
            "rule_version_set": "rule-set-1",
            "view_contents": contents,
            "reputation_and_band_values": {"band": "stated"},
            "graph_position_as_seen": "stated",
            "first_seen_day_per_record": {"item": 3},
            "delay_applied_per_record": {"item": 1},
            "completeness_state": "complete",
            "building_component": "Recorder",
            "delivering_contract": "stated",
            "selection_rule_version": "rule-set-1",
        }

    def test_r5a605_split_keys_read_barred(self):
        for key in BARRED_SPLIT_KEYS:
            self.assertTrue(mod10._is_barred_view_key(key), msg=key)

    def test_r5a605_runner_refuses_split_keys(self):
        for key in BARRED_SPLIT_KEYS:
            record = self.view_record([{"detail": {key: "v"}}])
            with self.assertRaises(ValueError, msg=key):
                mod10.run_view_leak_check(record)

    def test_r5a605_view_retention_refuses_split_keys(self):
        record = self.view_record([{"detail": {"ground truth": "v"}}])
        with self.assertRaises(ValueError):
            mod10.retain_view_record(record, tier="Tier 2")
        self.assertEqual(mod10.view_records_for_run("run-b07-view"), [])

    def test_r5a605_controls_hold(self):
        for key in ("labelled", "labels", "activity", "ordinary_key"):
            self.assertFalse(mod10._is_barred_view_key(key), msg=key)
        result = mod10.run_view_leak_check(
            self.view_record([{"activity": "stated"}]))
        self.assertTrue(result["reportable"])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(
                self.view_record([{"canary": "v"}]))


if __name__ == "__main__":
    unittest.main()
