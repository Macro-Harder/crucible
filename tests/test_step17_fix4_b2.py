"""Step 17 fix wave 4, Slice 2 defect and control tests.

Rows: FW4-08 (the mod10 gate passing share epoch cycle and
depth door) and FW4-09 (the mod10 store writer non text key
door, carried on its probe: the charged handings stand served
whole on the uncured tree, pinned here as controls).
"""
import os
import tempfile
import unittest

from crucible import mod10


def _deep_epoch(levels):
    epoch = "leaf"
    for _ in range(levels):
        epoch = [epoch]
    return epoch


class TestFW408EpochShape(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def test_fw408_cyclic_dict_epoch_refused_named_form(self):
        epoch = {}
        epoch["self"] = epoch
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("fw408-cyc-dict", epoch, 0.5)
        text = str(caught.exception)
        self.assertIn("gate passing share in named form", text)
        self.assertIn("cyclic", text)
        self.assertIn("no share stands returned", text)
        self.assertEqual(
            mod10.gate_passing_shares_for_run("fw408-cyc-dict"), {})

    def test_fw408_cyclic_list_epoch_refused_named_form(self):
        epoch = []
        epoch.append(epoch)
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("fw408-cyc-list", epoch, 0.5)
        text = str(caught.exception)
        self.assertIn("gate passing share in named form", text)
        self.assertIn("cyclic", text)
        self.assertIn("no share stands returned", text)
        self.assertEqual(
            mod10.gate_passing_shares_for_run("fw408-cyc-list"), {})

    def test_fw408_cyclic_tuple_epoch_refused_named_form(self):
        inner = []
        epoch = (inner,)
        inner.append(epoch)
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("fw408-cyc-tuple", epoch, 0.5)
        text = str(caught.exception)
        self.assertIn("gate passing share in named form", text)
        self.assertIn("cyclic", text)
        self.assertIn("no share stands returned", text)
        self.assertEqual(
            mod10.gate_passing_shares_for_run("fw408-cyc-tuple"), {})

    def test_fw408_cyclic_key_epoch_refused_named_form(self):
        epoch = {}
        epoch[(1, 2)] = "x"
        epoch["loop"] = epoch
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("fw408-cyc-key", epoch, 0.5)
        text = str(caught.exception)
        self.assertIn("gate passing share in named form", text)
        self.assertIn("cyclic", text)
        self.assertIn("no share stands returned", text)
        self.assertEqual(
            mod10.gate_passing_shares_for_run("fw408-cyc-key"), {})

    def test_fw408_deep_2000_epoch_refused_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share(
                "fw408-deep-2000", _deep_epoch(2000), 0.5)
        text = str(caught.exception)
        self.assertIn("gate passing share in named form", text)
        self.assertIn("deeper than", text)
        self.assertIn("no share stands returned", text)
        self.assertEqual(
            mod10.gate_passing_shares_for_run("fw408-deep-2000"), {})

    def test_fw408_deep_200_epoch_refused_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share(
                "fw408-deep-200", _deep_epoch(200), 0.5)
        text = str(caught.exception)
        self.assertIn("gate passing share in named form", text)
        self.assertIn("deeper than", text)
        self.assertIn("no share stands returned", text)
        self.assertEqual(
            mod10.gate_passing_shares_for_run("fw408-deep-200"), {})

    def test_control_plain_int_epoch_served(self):
        out = mod10.record_gate_passing_share("fw408-ctl-int", 3, 0.5)
        self.assertEqual(out["share"], 0.5)
        shares = mod10.gate_passing_shares_for_run("fw408-ctl-int")
        self.assertEqual(len(shares), 1)

    def test_control_text_epoch_served(self):
        out = mod10.record_gate_passing_share(
            "fw408-ctl-text", "epoch-1", 0.5)
        self.assertEqual(out["share"], 0.5)
        shares = mod10.gate_passing_shares_for_run("fw408-ctl-text")
        self.assertEqual(len(shares), 1)

    def test_control_huge_int_epoch_served_whole(self):
        out = mod10.record_gate_passing_share(
            "fw408-ctl-huge", 10 ** 5000, 0.5)
        self.assertEqual(out["share"], 0.5)
        shares = mod10.gate_passing_shares_for_run("fw408-ctl-huge")
        self.assertEqual(len(shares), 1)

    def test_control_dict_epoch_with_huge_key_served(self):
        out = mod10.record_gate_passing_share(
            "fw408-ctl-dict", {10 ** 5000: "x", "a": 1}, 0.5)
        self.assertEqual(out["share"], 0.5)
        shares = mod10.gate_passing_shares_for_run("fw408-ctl-dict")
        self.assertEqual(len(shares), 1)

    def test_control_nested_epoch_within_bound_served(self):
        out = mod10.record_gate_passing_share(
            "fw408-ctl-nested", _deep_epoch(50), 0.5)
        self.assertEqual(out["share"], 0.5)
        shares = mod10.gate_passing_shares_for_run("fw408-ctl-nested")
        self.assertEqual(len(shares), 1)

    def test_control_bad_share_named_form_stands(self):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("fw408-ctl-share", 3, 7)
        self.assertIn(
            "gate passing share in named form", str(caught.exception))


class TestFW409ServedWholeControls(unittest.TestCase):
    """The charged FW4-09 handings stand served whole on the
    uncured tree at every door probed, so these controls pin
    that standing in the open and no cure stands invented."""

    def setUp(self):
        mod10.reset_stores()

    def test_control_module_small_int_key_served_whole(self):
        mod10.retain_run_record({"run_id": "fw409-c1", 7: 1})
        got = mod10.read_run_record("fw409-c1")
        self.assertEqual(got[7], 1)
        self.assertEqual(got["run_id"], "fw409-c1")

    def test_control_module_huge_int_key_served_whole(self):
        mod10.retain_run_record({"run_id": "fw409-h0", "v": 1})
        mod10.retain_run_record({"run_id": "fw409-h1", 10 ** 5000: 1})
        self.assertEqual(mod10.read_run_record("fw409-h0")["v"], 1)
        got = mod10.read_run_record("fw409-h1")
        self.assertEqual(got[10 ** 5000], 1)
        mod10.retain_run_record({"run_id": "fw409-h2", "v": 2})
        self.assertEqual(mod10.read_run_record("fw409-h2")["v"], 2)

    def test_control_class_small_int_key_served_whole(self):
        store = mod10.new_store(store_kind="sweep")
        store.retain_run_record({"run_id": "fw409-c2", 7: 1})
        got = store.read_run_record("fw409-c2")
        self.assertEqual(got[7], 1)

    def test_control_file_huge_int_key_served_and_reopened(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.new_store(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "fw409-f1", 10 ** 5000: "x"})
            got = store.read_run_record("fw409-f1")
            self.assertEqual(got[10 ** 5000], "x")
            reopened = mod10.new_store(store_kind="sweep", path=path)
            got2 = reopened.read_run_record("fw409-f1")
            keys = [k for k in got2 if k != "run_id"]
            self.assertEqual(len(keys), 1)
            self.assertEqual(got2[keys[0]], "x")

    def test_control_nested_huge_int_key_served_whole(self):
        mod10.retain_run_record(
            {"run_id": "fw409-n1", "n": {10 ** 5000: "x"}})
        got = mod10.read_run_record("fw409-n1")
        self.assertEqual(got["n"][10 ** 5000], "x")

    def test_control_huge_int_value_served_whole(self):
        mod10.retain_run_record({"run_id": "fw409-v1", "v": 10 ** 5000})
        got = mod10.read_run_record("fw409-v1")
        self.assertEqual(got["v"], 10 ** 5000)


if __name__ == "__main__":
    unittest.main()
