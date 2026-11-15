import unittest

from crucible import mod10, mod14


class EvilBoth(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class LyingEqStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class LyingIter:
    def __init__(self, stored):
        self.stored = stored

    def __iter__(self):
        return iter([1, 2, 3])


class LyingIterStr(str):
    def __iter__(self):
        return iter([1, 2, 3])


class LyingEqObj:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


def met_record(**overrides):
    record = {
        "state": "OPEN",
        "later_evaluation": {
            "conditions": [1, 2, 3],
            "inputs": {"x": 1},
            "outcome": "done",
        },
        "summary_record_written": True,
        "retained_forms_pointed_to": ["a"],
    }
    record.update(overrides)
    return record


def flag_record(tier="Tier 1"):
    return {"retention_tier": tier, "flag_conditions_fired": ["c"]}


FIRED = {"flag_conditions_fired": ["c"]}


class TestR16004FlagBytesLimb(unittest.TestCase):
    def test_core_demotion_bytes_current_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record(b"Tier 3"), outcome="promote",
                tier="Tier 1", inputs=dict(FIRED))
        self.assertIn("never demotes", str(caught.exception))

    def test_shell_demotion_bytes_current_refused(self):
        with self.assertRaises(Exception) as caught:
            mod14.flag_evaluation(
                flag_record(b"Tier 3"), outcome="promote",
                tier="Tier 1", inputs=dict(FIRED))
        self.assertIn("never demotes", str(caught.exception))

    def test_core_bytes_outcome_promotes(self):
        result = mod10.apply_flag_evaluation(
            flag_record("Tier 1"), outcome=b"promote",
            tier="Tier 2", inputs=dict(FIRED))
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_core_bytes_tier_promotes(self):
        result = mod10.apply_flag_evaluation(
            flag_record("Tier 1"), outcome="promote",
            tier=b"Tier 2", inputs=dict(FIRED))
        self.assertEqual(
            mod10._stored_text(result["retention_tier"]), "Tier 2")

    def test_core_bytearray_tier_promotes(self):
        result = mod10.apply_flag_evaluation(
            flag_record("Tier 1"), outcome="promote",
            tier=bytearray(b"Tier 2"), inputs=dict(FIRED))
        self.assertEqual(
            mod10._stored_text(result["retention_tier"]), "Tier 2")

    def test_shell_bytes_current_and_tier_demotion_refused(self):
        with self.assertRaises(Exception) as caught:
            mod14.flag_evaluation(
                flag_record(bytearray(b"Tier 3")), outcome="promote",
                tier=b"Tier 1", inputs=dict(FIRED))
        self.assertIn("never demotes", str(caught.exception))

    def test_plain_demotion_control_refused(self):
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                flag_record("Tier 3"), outcome="promote",
                tier="Tier 1", inputs=dict(FIRED))

    def test_plain_promotion_control(self):
        result = mod10.apply_flag_evaluation(
            flag_record("Tier 1"), outcome="promote",
            tier="Tier 2", inputs=dict(FIRED))
        self.assertEqual(result["retention_tier"], "Tier 2")


class TestR16021RetentionStateLimb(unittest.TestCase):
    def test_state_bytes_refused(self):
        self.assertFalse(mod10.retention_met(
            met_record(state=b"DECLARED NOT CLOSED")))

    def test_state_bytearray_refused(self):
        self.assertFalse(mod10.retention_met(
            met_record(state=bytearray(b"DECLARED NOT CLOSED"))))

    def test_state_lying_eq_open_met(self):
        self.assertTrue(mod10.retention_met(
            met_record(state=LyingEqStr("OPEN"))))

    def test_state_plain_closed_control(self):
        self.assertFalse(mod10.retention_met(
            met_record(state="DECLARED NOT CLOSED")))

    def test_state_plain_open_control(self):
        self.assertTrue(mod10.retention_met(met_record()))


class TestR16022RetentionConditionsFallback(unittest.TestCase):
    def record_with(self, conditions):
        record = met_record()
        record["later_evaluation"] = {
            "conditions": conditions,
            "inputs": {"x": 1},
            "outcome": "done",
        }
        return record

    def test_lying_iteration_object_not_met(self):
        self.assertFalse(mod10.retention_met(
            self.record_with(LyingIter(9))))

    def test_lying_iteration_text_not_met(self):
        self.assertFalse(mod10.retention_met(
            self.record_with(LyingIterStr("zzz"))))

    def test_scalar_int_returns_false(self):
        self.assertFalse(mod10.retention_met(self.record_with(5)))

    def test_scalar_float_returns_false(self):
        self.assertFalse(mod10.retention_met(self.record_with(5.0)))

    def test_scalar_bool_returns_false(self):
        self.assertFalse(mod10.retention_met(self.record_with(True)))

    def test_scalar_plain_object_returns_false(self):
        self.assertFalse(mod10.retention_met(self.record_with(object())))

    def test_plain_list_control(self):
        self.assertTrue(mod10.retention_met(self.record_with([1, 2, 3])))

    def test_plain_wrong_list_control(self):
        self.assertFalse(mod10.retention_met(self.record_with([9])))

    def test_dict_form_control(self):
        self.assertTrue(mod10.retention_met(
            self.record_with({1: "a", 2: "b", 3: "c"})))


class TestR16023RetentionConditionsComparison(unittest.TestCase):
    def test_lying_eq_elements_not_met(self):
        record = met_record()
        record["later_evaluation"] = {
            "conditions": [LyingEqObj(), LyingEqObj(), LyingEqObj()],
            "inputs": {"x": 1},
            "outcome": "done",
        }
        self.assertFalse(mod10.retention_met(record))

    def test_plain_met_control(self):
        self.assertTrue(mod10.retention_met(met_record()))

    def test_plain_unmet_control(self):
        record = met_record()
        record["later_evaluation"] = {
            "conditions": [9, 9, 9],
            "inputs": {"x": 1},
            "outcome": "done",
        }
        self.assertFalse(mod10.retention_met(record))


class TestR16026WriteStoreIdentifierForm(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def check_refused(self, rid):
        result = mod14.run_command(
            "write_store", {"record": {"run_id": rid, "marker": "m"}})
        self.assertIn("failure", result)
        self.assertIn("no identifier form", result["failure"])

    def test_write_int_id_refused(self):
        self.check_refused(123)

    def test_write_float_id_refused(self):
        self.check_refused(1.5)

    def test_write_bool_id_refused(self):
        self.check_refused(True)

    def test_write_bytes_id_refused(self):
        self.check_refused(b"bytes-id")

    def test_direct_retain_int_id_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_run_record({"run_id": 987654, "marker": "m"})

    def test_text_id_round_trip_control(self):
        written = mod14.run_command(
            "write_store",
            {"record": {"run_id": "text-id-b6", "marker": "m"}})
        self.assertNotIn("failure", written)
        read = mod14.run_command(
            "read_store", {"run_id": "text-id-b6"})
        self.assertEqual(read["marker"], "m")


class TestR16028WeeklyWeekComparison(unittest.TestCase):
    def test_stored_lying_week_not_counted(self):
        records = [{"week": EvilBoth("W2"),
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 0)

    def test_handed_lying_week_not_counted(self):
        records = [{"week": "W2",
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(
            mod14.weekly_headline_count(records, EvilBoth("W1")), 0)

    def test_fieldless_other_week_passed_over(self):
        records = [{"week": EvilBoth("W2")}]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 0)

    def test_plain_other_week_control(self):
        records = [{"week": "W2",
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 0)

    def test_plain_same_week_control(self):
        records = [{"week": "W1",
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 1)


class TestR16029ShellDispatch(unittest.TestCase):
    def test_lying_name_empty_payload_unknown(self):
        result = mod14.run_command(EvilBoth("bogus"), {})
        self.assertIn("failure", result)
        self.assertIn("unknown shell command", result["failure"])

    def test_lying_name_sound_payload_unknown(self):
        result = mod14.run_command(
            EvilBoth("bogus"),
            {"run_class": "screening", "family_id": "fam-1"})
        self.assertIn("failure", result)
        self.assertIn("unknown shell command", result["failure"])

    def test_plain_bogus_control_unknown(self):
        result = mod14.run_command("bogus", {})
        self.assertIn("unknown shell command", result["failure"])

    def test_plain_start_run_control(self):
        result = mod14.run_command("start_run", {})
        self.assertNotIn("unknown shell command", str(result))


class TestR16030OutsideCallLogKey(unittest.TestCase):
    def test_lying_key_refused(self):
        log = {"calls": [], EvilBoth("bogus"): 123}
        with self.assertRaises(Exception) as caught:
            mod14.outside_call_check({}, log)
        self.assertIn("cannot read", str(caught.exception))

    def test_plain_bogus_key_control_refused(self):
        with self.assertRaises(Exception):
            mod14.outside_call_check({}, {"calls": [], "bogus": 123})

    def test_plain_clean_control(self):
        result = mod14.outside_call_check({}, {"calls": []})
        self.assertEqual(result["outcome"], "no outside calls read")


class TestR16054ShellOutcomeGate(unittest.TestCase):
    def test_lying_demote_draws_never_demotes(self):
        with self.assertRaises(Exception) as caught:
            mod14.flag_evaluation(
                flag_record("Tier 1"), inputs=None,
                outcome=LyingEqStr("demote"), tier="Tier 2")
        self.assertIn("never demotes", str(caught.exception))

    def test_plain_demote_control(self):
        with self.assertRaises(Exception) as caught:
            mod14.flag_evaluation(
                flag_record("Tier 1"), inputs=None,
                outcome="demote", tier="Tier 2")
        self.assertIn("never demotes", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
