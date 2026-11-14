"""Step 14 re-run pins, builder B2, slices S-02 and S-03.

Pins for R5-A6-05 at MOD-03 (barred keys split inside their marker
words, read through the folded reading) and for the MOD-02 limb of
TA-32 (generator state carriage carrying held positions).
"""
import unittest

from crucible import mod02, mod03


SPLIT_KEYS = (
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

LEET_KEYS = (
    "c4nary", "m3mbership", "gr0undtruth", "s1eeper",
)


class TestR5A605Mod03BarredFold(unittest.TestCase):
    def test_split_keys_read_barred(self):
        for key in SPLIT_KEYS:
            record = {"feature_values": {key: "v"}}
            self.assertTrue(
                mod03.record_carries_ground_truth(record), key)
            self.assertFalse(mod03.validate_detection_input(record), key)
            self.assertFalse(
                mod03.validate_adjudication_input(record), key)

    def test_split_keys_are_stripped(self):
        for key in SPLIT_KEYS:
            record = {"feature_values": {key: "v", "activity": 1}}
            stripped = mod03.strip_ground_truth(record)
            self.assertNotIn(key, stripped["feature_values"], key)
            self.assertEqual(stripped["feature_values"]["activity"], 1)

    def test_leet_substituted_keys_read_barred(self):
        for key in LEET_KEYS:
            record = {"feature_values": {key: "v"}}
            self.assertTrue(
                mod03.record_carries_ground_truth(record), key)

    def test_controls_hold(self):
        clean = {"feature_values": {"activity": 1}}
        self.assertFalse(mod03.record_carries_ground_truth(clean))
        self.assertTrue(mod03.validate_detection_input(clean))
        self.assertEqual(mod03.strip_ground_truth(clean), clean)
        for key in ("canary_token", "canary", "ground_truth"):
            self.assertTrue(mod03.record_carries_ground_truth(
                {"feature_values": {key: "v"}}), key)
        for key in ("labels", "labelled", "xsleeper"):
            self.assertFalse(mod03.record_carries_ground_truth(
                {"feature_values": {key: "v"}}), key)


class TestTa32Mod02Carriage(unittest.TestCase):
    def test_checkpoint_carries_held_positions(self):
        state = mod02.checkpoint_generator_state(
            run_id="run-b02", stream_classes=["alpha", "beta"],
            positions={"alpha": 7, "beta": 3})
        self.assertEqual(state["stream_states"]["alpha"]["position"], 7)
        self.assertEqual(state["stream_states"]["beta"]["position"], 3)

    def test_resume_consumes_held_state_field_for_field(self):
        held = mod02.checkpoint_generator_state(
            run_id="run-b02", stream_classes=["alpha"],
            positions={"alpha": 11})
        consumed = mod02.resume_consumed_generator_state(
            run_id="run-b02", scope="non detection", held_state=held)
        self.assertEqual(held, consumed)
        self.assertTrue(
            mod02.validate_generator_state_carriage(held, consumed))

    def test_resume_consumes_stream_states_mapping(self):
        held = {"run_id": "run-b02",
                "stream_states": {"alpha": {"position": 5}},
                "stream_inventory_standing":
                    "inventory named in the adoption record",
                "carriage": "generator state for checkpoints"}
        consumed = mod02.resume_consumed_generator_state(
            held_state=held)
        self.assertEqual(held, consumed)

    def test_default_carriage_unchanged(self):
        held = mod02.checkpoint_generator_state(
            run_id="run-b02", stream_classes=["alpha"])
        self.assertEqual(
            held["stream_states"]["alpha"]["position"], 0)
        consumed = mod02.resume_consumed_generator_state(
            run_id="run-b02", scope="non detection",
            stream_classes=["alpha"])
        self.assertEqual(held, consumed)


if __name__ == "__main__":
    unittest.main()
