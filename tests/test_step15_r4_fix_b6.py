"""Step 15, second run, fix wave 3, Builder 6 pins. MOD-08 items
R3-033 and R3-041.

R3-033: both MOD-08 barred reads count nesting in dict key
position, to the same bound and in the same form as the value
position reading. R3-041: the MOD-08 folded barred reading
stands at the shared folded barred reading used at MOD-03,
MOD-04 and MOD-05, including the homoglyph letters and the
transliteration reading named in the Yellow 2 paper.

No detection score is reported as a pass or as a fail in this
file: verdict readings and barred readings only.
"""
import unittest

from crucible import mod05, mod08


def frozenset_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = frozenset([value])
    return value


def tuple_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = (value,)
    return value


def output_with_extra(extra):
    return {
        mod08.PROFILE_BOUND_LABEL_FIELD: mod08.PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
        "extra": extra,
    }


def record_with_nested_key(key):
    return {
        "agent_identifier": "agent-b6",
        "day": 1,
        "feature_values": {"activity": 2},
        "records_for_agent_and_day": [{"wrap": {key: 1}}],
    }


class TestR3033KeyPositionDepth(unittest.TestCase):

    def test_validate_output_refuses_frozenset_chain_key_past_bound(self):
        output = output_with_extra({frozenset_chain(150): "clean"})
        self.assertFalse(mod08.validate_output(output))

    def test_validate_output_refuses_tuple_chain_key_past_bound(self):
        output = output_with_extra({tuple_chain(150): "clean"})
        self.assertFalse(mod08.validate_output(output))

    def test_validate_output_refuses_frozenset_chain_key_at_2000(self):
        output = output_with_extra({frozenset_chain(2000): "clean"})
        self.assertFalse(mod08.validate_output(output))

    def test_carries_barred_verdict_reads_deep_key_as_barred(self):
        node = {frozenset_chain(150): "clean"}
        self.assertTrue(mod08._carries_barred_verdict(node))
        node = {tuple_chain(150): "clean"}
        self.assertTrue(mod08._carries_barred_verdict(node))

    def test_find_barred_raises_on_frozenset_chain_key_past_bound(self):
        node = {frozenset_chain(150): "clean"}
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._find_barred(node)

    def test_find_barred_raises_on_tuple_chain_key_past_bound(self):
        node = {tuple_chain(150): "clean"}
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._find_barred(node)

    def test_acceptance_refuses_deep_key_shape_in_named_form(self):
        record = {
            "agent_identifier": "agent-b6",
            "day": 1,
            "feature_values": {"activity": 2},
            "records_for_agent_and_day": [{frozenset_chain(150): "clean"}],
        }
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_value_position_chain_past_bound_still_refused(self):
        output = output_with_extra({"held": frozenset_chain(150)})
        self.assertFalse(mod08.validate_output(output))
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._find_barred({"held": frozenset_chain(150)})

    def test_shallow_chain_key_still_admitted(self):
        output = output_with_extra({frozenset_chain(10): "clean"})
        self.assertTrue(mod08.validate_output(output))
        self.assertEqual(mod08._find_barred({frozenset_chain(5): "clean"}), [])
        self.assertFalse(
            mod08._carries_barred_verdict({tuple_chain(5): "clean"}))

    def test_plain_output_still_validates(self):
        output = output_with_extra({"held": "clean"})
        self.assertTrue(mod08.validate_output(output))


DEFECT_KEYS = (
    "μembership",
    "мembership",
    "memβership",
    "m€mbership",
    "гround_truth",
    "ground_tрuth",
)

COVERED_KEYS = (
    "lаbel",
    "ground_тruth",
    "ᴍembership",
)

PLAIN_BARRED_KEYS = ("membership", "ground_truth")

CLEAN_KEYS = ("activity", "notes")


class TestR3041SharedFoldedReading(unittest.TestCase):

    def test_sister_control_bars_each_defect_key(self):
        for key in DEFECT_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod05._panel_key_barred(key))

    def test_mod08_fold_bars_each_defect_key(self):
        for key in DEFECT_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_acceptance_refuses_each_defect_key(self):
        for key in DEFECT_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(record_with_nested_key(key))

    def test_plain_barred_keys_still_refused_at_acceptance(self):
        for key in PLAIN_BARRED_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(record_with_nested_key(key))

    def test_covered_dress_keys_still_refused_at_acceptance(self):
        for key in COVERED_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(record_with_nested_key(key))

    def test_clean_keys_still_accepted(self):
        for key in CLEAN_KEYS:
            with self.subTest(key=key):
                accepted = mod08.accept_detection_input(
                    record_with_nested_key(key))
                self.assertEqual(accepted["agent_identifier"], "agent-b6")
                self.assertFalse(mod08._is_barred_key(key))


if __name__ == "__main__":
    unittest.main()
