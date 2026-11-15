"""Pins for fix wave 13, Builder 8: rows R13-033, R13-034,
R13-046, and R13-047 of the Round 13 register.

R13-033: MOD-13 validate_verdict_record and its companion read
the claim identifier through stored readings, never through a
truth or length reading the value itself supplies.
R13-034: MOD-13 validate_rerun_reading stands paired with a
named failures companion stating its grounds apart.
R13-046: MOD-13 resume and aggregate companions state a
positional fault as a positional fault, not as a membership
fault.
R13-047: MOD-14 error carriage carries the structured failure
value on the plain exception paths, in the twice stated form,
and the weekly count refuses a non list summary records
argument in named form.
"""

import unittest

from crucible import mod13, mod14


class LenBoom(list):
    def __len__(self):
        raise RuntimeError("len boom")


class BoolBoom:
    def __bool__(self):
        raise RuntimeError("bool boom")


def lawful_verdict():
    return mod13.verdict_record("claim-1")


def carriage_texts(value, out):
    if isinstance(value, dict):
        for item in value.values():
            carriage_texts(item, out)
    elif isinstance(value, str):
        out.append(value)
    return out


class TestR13033VerdictIdentifierStoredReading(unittest.TestCase):

    def test_validate_len_raising_identifier_present_form(self):
        record = lawful_verdict()
        record["claim_identifier"] = LenBoom([1])
        self.assertTrue(mod13.validate_verdict_record(record))

    def test_validate_bool_raising_identifier_present_form(self):
        record = lawful_verdict()
        record["claim_identifier"] = BoolBoom()
        self.assertTrue(mod13.validate_verdict_record(record))

    def test_validate_len_raising_empty_identifier_refused(self):
        record = lawful_verdict()
        record["claim_identifier"] = LenBoom([])
        self.assertFalse(mod13.validate_verdict_record(record))

    def test_companion_present_forms_answer_plain(self):
        for hostile in (LenBoom([1]), BoolBoom()):
            record = lawful_verdict()
            record["claim_identifier"] = hostile
            self.assertEqual(
                mod13.verdict_record_validation_failures(record), [])

    def test_companion_empty_len_raising_identifier_named(self):
        record = lawful_verdict()
        record["claim_identifier"] = LenBoom([])
        failures = mod13.verdict_record_validation_failures(record)
        self.assertTrue(
            any("claim_identifier" in item for item in failures),
            failures)

    def test_publishable_failures_no_bare_error(self):
        record = lawful_verdict()
        record["claim_identifier"] = LenBoom([1])
        failures = mod13.publishable_on_replication_failures(
            {"claim_identifier": "claim-1"}, record)
        self.assertTrue(failures)
        record2 = lawful_verdict()
        record2["claim_identifier"] = BoolBoom()
        failures2 = mod13.publishable_on_replication_failures(
            {"claim_identifier": "claim-1"}, record2)
        self.assertTrue(failures2)

    def test_sibling_and_lawful_controls(self):
        for hostile in (LenBoom([1]), BoolBoom()):
            self.assertFalse(mod13.validate_replay_claim(
                {"hash_equality_claimed": hostile}))
            self.assertFalse(mod13.validate_probe_claim(
                {"margin_or_method_presented_as_settled": hostile}))
        record = lawful_verdict()
        self.assertTrue(mod13.validate_verdict_record(record))
        self.assertEqual(
            mod13.verdict_record_validation_failures(record), [])
        self.assertTrue(mod13.publishable_on_replication(
            {"claim_identifier": "claim-1"}, record))


class TestR13034RerunReadingCompanion(unittest.TestCase):

    def test_corrected_ground_named(self):
        reading = {"read_as": "corrected version of the original"}
        self.assertFalse(mod13.validate_rerun_reading(reading))
        failures = mod13.rerun_reading_validation_failures(reading)
        self.assertTrue(failures)
        self.assertTrue(
            any("corrected version" in item for item in failures),
            failures)

    def test_overwrites_ground_named(self):
        reading = {"overwrites_original": True}
        self.assertFalse(mod13.validate_rerun_reading(reading))
        failures = mod13.rerun_reading_validation_failures(reading)
        self.assertTrue(failures)
        self.assertTrue(
            any("overwrites" in item for item in failures), failures)

    def test_two_grounds_told_apart(self):
        corrected = mod13.rerun_reading_validation_failures(
            {"read_as": "corrected version of the original"})
        overwrites = mod13.rerun_reading_validation_failures(
            {"overwrites_original": True})
        self.assertNotEqual(corrected, overwrites)

    def test_other_read_as_ground_named(self):
        reading = {"read_as": "the settled account of the run"}
        self.assertFalse(mod13.validate_rerun_reading(reading))
        self.assertTrue(
            mod13.rerun_reading_validation_failures(reading))

    def test_non_record_and_lawful_controls(self):
        self.assertFalse(mod13.validate_rerun_reading("text"))
        self.assertTrue(
            mod13.rerun_reading_validation_failures("text"))
        for reading in (
                {},
                {"read_as": "difference between two rule sets only"}):
            self.assertTrue(mod13.validate_rerun_reading(reading))
            self.assertEqual(
                mod13.rerun_reading_validation_failures(reading), [])


class TestR13046CompanionPositionalWording(unittest.TestCase):

    def test_resume_reversed_points_state_position(self):
        claim = {"detection_comparison_points": [
            "run close", "first verdict state after resume"]}
        self.assertFalse(mod13.validate_resume_claim(claim))
        failures = mod13.resume_claim_validation_failures(claim)
        self.assertTrue(failures)
        for item in failures:
            self.assertNotIn("outside the two named points", item)
        self.assertTrue(any(
            "run close" in item and (
                "position" in item or "order" in item)
            for item in failures), failures)

    def test_resume_duplicate_points_state_position(self):
        for points in (
                ["run close", "run close"],
                ["first verdict state after resume",
                 "first verdict state after resume"]):
            claim = {"detection_comparison_points": points}
            self.assertFalse(mod13.validate_resume_claim(claim))
            failures = mod13.resume_claim_validation_failures(claim)
            self.assertTrue(failures)
            for item in failures:
                self.assertNotIn("outside the two named points", item)

    def test_resume_foreign_point_keeps_membership_wording(self):
        claim = {"detection_comparison_points": [
            "bogus point", "run close"]}
        failures = mod13.resume_claim_validation_failures(claim)
        self.assertTrue(any(
            "outside the two named points" in item
            for item in failures), failures)

    def test_resume_lawful_control(self):
        claim = {"detection_comparison_points": [
            "first verdict state after resume", "run close"]}
        self.assertTrue(mod13.validate_resume_claim(claim))
        self.assertEqual(
            mod13.resume_claim_validation_failures(claim), [])

    def test_aggregate_reversed_form_states_order(self):
        form = list(reversed(mod13.daily_aggregate_form()))
        self.assertFalse(mod13.validate_aggregate_form(form))
        failures = mod13.aggregate_form_validation_failures(form)
        self.assertTrue(failures)
        for item in failures:
            self.assertNotIn(
                "outside the daily aggregate form", item)
        self.assertTrue(any(
            "order" in item for item in failures), failures)

    def test_aggregate_swapped_form_states_order(self):
        form = mod13.daily_aggregate_form()
        form[0], form[1] = form[1], form[0]
        self.assertFalse(mod13.validate_aggregate_form(form))
        failures = mod13.aggregate_form_validation_failures(form)
        self.assertTrue(failures)
        for item in failures:
            self.assertNotIn(
                "outside the daily aggregate form", item)
        self.assertTrue(any(
            "order" in item for item in failures), failures)

    def test_aggregate_foreign_and_lawful_controls(self):
        form = mod13.daily_aggregate_form()
        form[2] = "bogus_field"
        failures = mod13.aggregate_form_validation_failures(form)
        self.assertTrue(any(
            "outside the daily aggregate form" in item
            for item in failures), failures)
        daily = mod13.daily_aggregate_form()
        self.assertTrue(mod13.validate_aggregate_form(daily))
        self.assertEqual(
            mod13.aggregate_form_validation_failures(daily), [])


class TestR13047Mod14ErrorCarriage(unittest.TestCase):

    def test_read_store_bogus_kind_carries_failure_value(self):
        carriage = mod14.run_command(
            "read_store", {"run_id": "nope", "store_kind": "bogus"})
        self.assertIn("unknown store kind: bogus", carriage["failure"])
        self.assertTrue(carriage["failure_value"])
        self.assertEqual(
            carriage["failure_value"].get("name"), "ValueError")
        message = carriage["failure_value"].get("message", "")
        self.assertEqual(message, carriage["failure"])
        self.assertTrue(message.startswith(
            carriage["failure_value"]["name"]))
        self.assertNotIn("'", message)
        texts = carriage_texts(carriage, [])
        self.assertEqual(sum(
            1 for item in texts
            if "unknown store kind: bogus" in item), 2, texts)

    def test_write_store_bogus_kind_carries_failure_value(self):
        carriage = mod14.run_command(
            "write_store",
            {"record": {"run_id": "x"}, "store_kind": "bogus"})
        self.assertIn("unknown store kind: bogus", carriage["failure"])
        self.assertTrue(carriage["failure_value"])
        message = carriage["failure_value"].get("message", "")
        self.assertEqual(message, carriage["failure"])
        texts = carriage_texts(carriage, [])
        self.assertEqual(sum(
            1 for item in texts
            if "unknown store kind: bogus" in item), 2, texts)

    def test_weekly_count_number_records_named_not_raw(self):
        carriage = mod14.run_command(
            "weekly_headline_count",
            {"summary_records": 42, "week": "W1"})
        self.assertNotIn("not iterable", carriage["failure"])
        self.assertIn("weekly", carriage["failure"])
        self.assertIn("summary_records", carriage["failure"])
        self.assertIn("list", carriage["failure"])
        self.assertTrue(carriage["failure_value"])
        message = carriage["failure_value"].get("message", "")
        self.assertIn("summary_records", message)

    def test_weekly_count_direct_act_named_failure(self):
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.weekly_headline_count(42, "W1")
        self.assertIn("summary_records", str(caught.exception))
        self.assertIn("list", str(caught.exception))

    def test_error_carriage_plain_exception_direct(self):
        carriage = mod14.error_carriage(ValueError(
            "unknown store kind: bogus; a store kind stands among "
            "sweep, pilot, and live"))
        self.assertTrue(carriage["failure_value"])
        self.assertEqual(
            carriage["failure_value"].get("message"),
            carriage["failure"])

    def test_bounded_control_paths_stand(self):
        carriage = mod14.run_command("bogus_cmd", run_id="r1")
        texts = carriage_texts(carriage, [])
        self.assertEqual(sum(
            1 for item in texts
            if "unknown store kind" not in item
            and "unknown shell command: bogus_cmd" in item), 2, texts)
        store = mod14.run_command(
            "read_store", payload={"run_id": "nope"}, run_id="r1")
        message = store["failure_value"].get("message", "")
        self.assertNotIn("'", message)
        self.assertTrue(message.startswith(
            store["failure_value"]["name"]))


if __name__ == "__main__":
    unittest.main()
