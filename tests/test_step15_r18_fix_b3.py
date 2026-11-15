# Step 15 rerun, fix wave 17, Builder 3 pins.
# Rows R17-001, R17-004, and R17-051: the barred gate family at
# MOD-06 and MOD-08, under settlement S-14 for the MOD-06 rows.
# Row R17-001 charges the dict node limbs of the MOD-06 payload
# walk, which step past separator only, space only, dash only,
# and digit only middle keys and do not step past a middle key
# standing as a Cyrillic hard sign or soft sign. Row R17-004
# charges the MOD-08 barred verdict value limb and the walk per
# entry key limb, which judge a verdict value in buffer dress
# and a key through readings the handed value supplies, where
# the module stored text act states the stored form. Row
# R17-051 charges the MOD-08 validate_output label limb, which
# judges the profile bound label through the handed equality
# reading. OP-16 stands open: every pin here rests only on the
# shipped guard stated names and values, and no pin charges
# any value OP-16 reserves.
import unittest

import crucible.mod06 as mod06
import crucible.mod08 as mod08


LABEL_FIELD = mod08.PROFILE_BOUND_LABEL_FIELD
CARRIAGE = mod08.PROFILE_LABEL_CARRIAGE

HARD_LOWER = "ъ"
HARD_UPPER = "Ъ"
SOFT_LOWER = "ь"
SOFT_UPPER = "Ь"


def escrow_refused(payload):
    try:
        mod06.escrow_result("result", payload=payload)
    except ValueError:
        return True
    return False


def output(extra):
    record = {LABEL_FIELD: CARRIAGE}
    record.update(extra)
    return record


class LyingVerdictValue(str):
    def __new__(cls):
        return str.__new__(cls, "pass")

    def strip(self, *args, **kwargs):
        return "innocuous"

    def lower(self):
        return "innocuous"


class LyingVerdictKey(str):
    def __new__(cls):
        return str.__new__(cls, "verdict")

    def __str__(self):
        return "innocuous"

    def lower(self):
        return "innocuous"


class LyingLabel(str):
    def __new__(cls, text="bogus"):
        return str.__new__(cls, text)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(str.__str__(self))


class RefusingLabel(str):
    def __new__(cls):
        return str.__new__(cls, CARRIAGE)

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __hash__(self):
        return str.__hash__(str.__str__(self))


class TestR17001MoneyMarkerHardSignMiddle(unittest.TestCase):
    def test_money_split_hard_sign_lower_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, HARD_LOWER: 1, "money": 1}))

    def test_money_split_hard_sign_upper_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, HARD_UPPER: 1, "money": 1}))

    def test_money_split_soft_sign_lower_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, SOFT_LOWER: 1, "money": 1}))

    def test_money_split_soft_sign_upper_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, SOFT_UPPER: 1, "money": 1}))

    def test_money_split_doubled_hard_sign_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, HARD_LOWER + HARD_LOWER: 1, "money": 1}))

    def test_money_split_sign_with_digit_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, HARD_LOWER + "1": 1, "money": 1}))

    def test_money_split_sign_with_separator_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, SOFT_LOWER + "-": 1, "money": 1}))

    def test_money_split_mixed_signs_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, HARD_LOWER + SOFT_LOWER: 1, "money": 1}))


class TestR17001AnchorMarkerHardSignMiddle(unittest.TestCase):
    def test_anchor_split_hard_sign_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"anchor": 1, HARD_LOWER: 1, "set": 1}))

    def test_anchor_split_soft_sign_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"anchor": 1, SOFT_UPPER: 1, "set": 1}))


class TestR17001PairNameHardSignMiddle(unittest.TestCase):
    def test_amount_split_hard_sign_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"amou": 1, HARD_LOWER: 1, "nt": 1,
             "curr": 1, "ency": 1}))

    def test_currency_split_soft_sign_middle_refused(self):
        self.assertTrue(escrow_refused(
            {"amount": 1, "curr": 1, SOFT_LOWER: 1, "ency": 1}))


class TestR17001NestedHardSignMiddle(unittest.TestCase):
    def test_nested_dict_money_split_hard_sign_refused(self):
        self.assertTrue(escrow_refused(
            {"outer": {"real": 1, HARD_LOWER: 1, "money": 1}}))

    def test_list_nested_money_split_hard_sign_refused(self):
        self.assertTrue(escrow_refused(
            [{"real": 1, HARD_LOWER: 1, "money": 1}]))

    def test_tuple_nested_money_split_hard_sign_refused(self):
        self.assertTrue(escrow_refused(
            ({"real": 1, SOFT_LOWER: 1, "money": 1},)))

    def test_depth_three_money_split_hard_sign_refused(self):
        self.assertTrue(escrow_refused(
            {"one": {"two": {"three":
                {"real": 1, HARD_UPPER: 1, "money": 1}}}}))


class TestR17001Controls(unittest.TestCase):
    def test_plain_split_control_refused(self):
        self.assertTrue(escrow_refused({"real": 1, "money": 1}))

    def test_separator_middle_control_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, "-": 1, "money": 1}))

    def test_digit_middle_control_refused(self):
        self.assertTrue(escrow_refused(
            {"real": 1, "7": 1, "money": 1}))

    def test_letter_middle_control_returned(self):
        self.assertFalse(escrow_refused(
            {"real": 1, "x": 1, "money": 1}))

    def test_sign_key_alone_control_returned(self):
        self.assertFalse(escrow_refused(
            {HARD_LOWER: 1, "note": "plain"}))

    def test_innocent_payload_control_returned(self):
        self.assertFalse(escrow_refused(
            {"note": "plain", "count": 2}))


class TestR17004BufferVerdictValues(unittest.TestCase):
    def test_bytes_pass_value_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": b"pass"})))

    def test_bytes_fail_value_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": b"fail"})))

    def test_bytearray_fail_value_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": bytearray(b"fail")})))

    def test_memoryview_fail_value_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": memoryview(b"fail")})))

    def test_bytes_passed_at_score_verdict_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"score_verdict": b"passed"})))

    def test_bytes_value_nested_in_list_entry_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"records": [{"verdict": b"pass"}]})))

    def test_bytes_value_under_split_pair_opening_key_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"ver": b"pass", "dict": "x"})))


class TestR17004HandedReadings(unittest.TestCase):
    def test_lying_str_value_holding_pass_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": LyingVerdictValue()})))

    def test_lying_str_key_holding_verdict_refused(self):
        self.assertFalse(mod08.validate_output(
            output({LyingVerdictKey(): "pass"})))


class TestR17004Controls(unittest.TestCase):
    def test_plain_pass_control_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": "pass"})))

    def test_spaced_pass_control_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": " pass "})))

    def test_upper_pass_control_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"verdict": "PASS"})))

    def test_split_pair_plain_control_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"ver": "pass", "dict": "x"})))

    def test_list_nested_plain_control_refused(self):
        self.assertFalse(mod08.validate_output(
            output({"records": [{"verdict": "pass"}]})))

    def test_bytes_innocent_value_control_returned(self):
        self.assertTrue(mod08.validate_output(
            output({"verdict": b"watch"})))

    def test_clean_output_control_returned(self):
        self.assertTrue(mod08.validate_output(
            output({"score_verdict": None, "figure": 3})))


class TestR17051LabelLimb(unittest.TestCase):
    def test_lying_label_holding_bogus_refused(self):
        self.assertFalse(mod08.validate_output(
            {LABEL_FIELD: LyingLabel()}))

    def test_label_storing_carriage_with_refusing_equality(self):
        self.assertTrue(mod08.validate_output(
            {LABEL_FIELD: RefusingLabel()}))


class TestR17051Controls(unittest.TestCase):
    def test_plain_carriage_control_returned(self):
        self.assertTrue(mod08.validate_output(
            {LABEL_FIELD: CARRIAGE}))

    def test_plain_bogus_control_refused(self):
        self.assertFalse(mod08.validate_output(
            {LABEL_FIELD: "bogus"}))

    def test_bytes_carriage_control_refused(self):
        self.assertFalse(mod08.validate_output(
            {LABEL_FIELD: CARRIAGE.encode("utf-8")}))

    def test_missing_label_control_refused(self):
        self.assertFalse(mod08.validate_output({"figure": 3}))


if __name__ == "__main__":
    unittest.main()
