"""Step 14 re-run, Builder B3 pins.

R5-A6-05 at the MOD-04 barred surfaces, and the analogous split
forms at the MOD-05 panel reading and the MOD-06 payload reading,
each under its own standing vocabulary. A barred key split inside
its marker word, by a separator, a digit, a zero width character,
or a letter dress, reads through the folded reading and stands
barred as the plain spelling stands barred. Lawful keys that only
resemble a barred name stand admitted.
"""
import unittest

from crucible import mod04, mod05, mod06

SPLIT_KEYS = (
    "can ary", "can.ary", "can/ary", "can-ary", "cana ry",
    "ground truth", "ground-truth", "ground/truth",
    "ground truth field",
    "member ship", "member.ship", "member-ship",
    "is honest", "is-honest", "la bel", "sleep er",
    "can\u00e1ry", "c\u00e1nary_token",
    "\uff43anary", "can\u0430ry",
    "cana\u200bry", "can\u00adary", "cana\u0301ry",
    "ground\u200btruth", "memb\u200bership",
    "MEMBERSH\u0130P", "can4ary", "groun5dtruth", "member5ship",
)

CLEAN_KEYS = ("activity", "labelled", "labels", "xsleeper", "sleeperx", "kept")


class TestMod04BarredFoldedReading(unittest.TestCase):
    def test_split_keys_barred_at_checker(self):
        for key in SPLIT_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod04._is_barred_key(key))
                self.assertTrue(mod04.view_record_carries_barred_field(
                    {"view_contents": {"x": {key: "v"}}}))

    def test_split_keys_refused_at_build_view_record(self):
        for key in ("ground truth", "can ary", "can\u00e1ry",
                    "is honest", "la bel", "ground\u200btruth"):
            with self.subTest(key=key):
                with self.assertRaises(mod04.NamedFailure):
                    mod04.build_view_record(
                        position="pos-1", rule_version_set="rv-1",
                        contents=[{"detail": {key: "v"}}])

    def test_split_keys_stripped_from_projection(self):
        for key in SPLIT_KEYS:
            with self.subTest(key=key):
                projected = mod04.project_detection_input({
                    "agent_identifier": "agent-1", "day": 1,
                    "feature_values": {key: "v", "keep": 1},
                    "rule_records": [{"detail": {key: "v", "kept": 2}}],
                })
                self.assertEqual(projected["feature_values"], {"keep": 1})
                self.assertEqual(
                    projected["rule_records"], [{"detail": {"kept": 2}}])

    def test_clean_and_resembling_keys_admitted(self):
        for key in CLEAN_KEYS:
            with self.subTest(key=key):
                self.assertFalse(mod04._is_barred_key(key))


class TestMod05PanelFoldedReading(unittest.TestCase):
    PANEL_SPLIT = (
        "ground truth", "ground-truth", "member ship",
        "is honest", "la bel", "label reference",
        "ground\u200btruth", "memb\u200bership", "can\u00e1ry".replace(
            "can\u00e1ry", "ground truth label"),
    )

    def test_split_panel_keys_barred(self):
        for key in self.PANEL_SPLIT:
            with self.subTest(key=key):
                self.assertTrue(mod05._panel_key_barred(key))
                self.assertFalse(mod05.validate_panel_inputs({key: "v"}))
                self.assertNotIn(
                    key, mod05.panel_inputs({key: "v", "keep": 1}))

    def test_clean_panel_keys_admitted(self):
        self.assertTrue(mod05.validate_panel_inputs({"activity": 1}))
        self.assertEqual(
            mod05.panel_inputs({"activity": 1}), {"activity": 1})


class TestMod06PayloadFoldedReading(unittest.TestCase):
    def test_split_money_and_anchor_forms_barred(self):
        for payload in (
            {"real money value": 5},
            {("real" + "moneyvalue"): 5},
            {"real\u200bmoney": 5},
            {"am ount": 5, "curr ency": "USD"},
            {"anchor set": ["a"]},
            {"nested": {"anchor\u200bset": ["a"]}},
        ):
            with self.subTest(payload=payload):
                self.assertTrue(mod06._payload_carries_barred(payload))
                with self.assertRaises(ValueError):
                    mod06.escrow_result("deposit", payload=payload)

    def test_clean_payload_admitted(self):
        self.assertFalse(mod06._payload_carries_barred({"instruction": "deposit"}))
        self.assertFalse(mod06._payload_carries_barred({"amount": 5}))
        result = mod06.escrow_result("deposit", payload={"instruction": "deposit"})
        self.assertTrue(mod06.validate_escrow_result(result))


if __name__ == "__main__":
    unittest.main()
