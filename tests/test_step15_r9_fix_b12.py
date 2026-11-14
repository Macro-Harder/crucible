import unittest

from crucible import mod07, mod12, mod13


def list_chain(count):
    value = "leaf"
    for _ in range(count):
        value = [value]
    return value


def chain_depth(value):
    depth = 0
    while isinstance(value, list):
        depth += 1
        value = value[0]
    return depth


class ReportingStr(str):
    def __str__(self):
        return "content"

    def strip(self, *args):
        return "content"


class NamedKey:
    def __init__(self, carried, reported):
        self.carried = carried
        self.reported = reported

    def __str__(self):
        return self.reported

    def __hash__(self):
        return hash(self.carried)

    def __eq__(self, other):
        if isinstance(other, NamedKey):
            return self.carried == other.carried
        return NotImplemented


def tracer_records_with(field, value):
    records = mod07.tracer_passage_records("run-b12")
    records[0][field] = value
    return records


PASSAGE_FIELDS = ("point_in_run", "what_in_fact_passed")


class TestR8024Mod07NextBlankClass(unittest.TestCase):

    def test_defect_next_blank_class_refused_in_all_forms(self):
        charged = (
            "\u0000", "\u0007", "\u001b", "\u007f",
            "\u0903", "\u093e",
            "\u20dd", "\u0488",
            "\u1160", "\u3164", "\uffa0",
        )
        for field in PASSAGE_FIELDS:
            for value in charged:
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        tracer_records_with(field, value)))
            for value in (
                    "\u0903".encode("utf-8"),
                    "\u1160".encode("utf-8"),
                    "\u20dd".encode("utf-8"),
                    b"\x00",
                    memoryview("\u1160".encode("utf-8")),
                    memoryview(b"\x00"),
                    ReportingStr("\u0000"),
            ):
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        tracer_records_with(field, value)))


class TestR8020Mod12SealBoundGuard(unittest.TestCase):

    def test_defect_past_bound_record_refused_in_named_form(self):
        for count in (120, 2000):
            with self.subTest(count=count):
                record = mod12.make_family_record()
                record["deep_field"] = list_chain(count)
                with self.assertRaises(mod12.NamedControllerFailure):
                    mod12.seal_family_record(record)


class TestR8010Mod12StoredTextFallback(unittest.TestCase):

    def test_defect_non_text_key_judged_by_no_supplied_name(self):
        reporting = NamedKey("figure", "amount")
        self.assertIsNone(mod12._stored_text(reporting))
        self.assertFalse(mod12._folded_name_matches(reporting, "amount"))
        self.assertNotIn("amount", mod12._folded_money_variants(reporting))
        self.assertFalse(mod12._carries_barred_money_value(
            {reporting: 10, "currency": "USD"}))
        escaping = NamedKey("amount", "figure")
        self.assertIsNone(mod12._stored_text(escaping))
        self.assertFalse(mod12._folded_name_matches(escaping, "amount"))
        agreeing = NamedKey("figure", "figure")
        self.assertFalse(mod12._folded_name_matches(agreeing, "figure"))


class TestR8021Mod13ExtendHistoryBoundGuard(unittest.TestCase):

    def test_defect_past_bound_segment_refused_in_named_form(self):
        for count in (120, 2000):
            with self.subTest(count=count):
                history = [{"rule_set_version": "v1", "run_id": "r1"}]
                segment = {
                    "rule_set_version": "v1",
                    "run_id": "r1",
                    "deep_field": list_chain(count),
                }
                with self.assertRaises(mod13.NamedReplicationFailure):
                    mod13.extend_history(history, segment)


class TestControlsStandingBothWays(unittest.TestCase):

    def test_control_mod07_readable_and_cured_blank_classes(self):
        for field in PASSAGE_FIELDS:
            self.assertTrue(mod07.validate_tracer_passage_set(
                tracer_records_with(field, "plain readable text")))
            self.assertTrue(mod07.validate_tracer_passage_set(
                tracer_records_with(field, "\u0000 with a letter x")))
            for value in (
                    "", "   ", "\u00a0", "\u200b", "\ufeff",
                    "\u034f", "\u2800", "\u115f",
                    "\u200b".encode("utf-8"),
            ):
                with self.subTest(field=field, value=repr(value)):
                    self.assertFalse(mod07.validate_tracer_passage_set(
                        tracer_records_with(field, value)))

    def test_control_mod12_within_bound_seal_copies_whole(self):
        record = mod12.make_family_record()
        record["deep_field"] = list_chain(50)
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])
        self.assertEqual(chain_depth(sealed["deep_field"]), 50)
        boundary = mod12.make_family_record()
        boundary["deep_field"] = list_chain(100)
        sealed_boundary = mod12.seal_family_record(boundary)
        self.assertTrue(sealed_boundary["sealed"])
        self.assertEqual(chain_depth(sealed_boundary["deep_field"]), 100)
        shared = [1, 2]
        record = mod12.make_family_record()
        record["first"] = shared
        record["second"] = shared
        sealed = mod12.seal_family_record(record)
        self.assertIs(sealed["first"], sealed["second"])
        self.assertEqual(sealed["first"], [1, 2])

    def test_control_mod13_within_bound_extend_copies_whole(self):
        history = [{"rule_set_version": "v1", "run_id": "r1"}]
        segment = {
            "rule_set_version": "v1",
            "run_id": "r1",
            "deep_field": list_chain(50),
        }
        extended = mod13.extend_history(history, segment)
        self.assertEqual(len(extended), 2)
        self.assertEqual(extended[1]["segment_order"], 2)
        self.assertEqual(chain_depth(extended[1]["deep_field"]), 50)
        shared = [1, 2]
        segment = {
            "rule_set_version": "v1",
            "run_id": "r1",
            "first": shared,
            "second": shared,
        }
        extended = mod13.extend_history(history, segment)
        self.assertIs(extended[1]["first"], extended[1]["second"])
        self.assertEqual(extended[1]["first"], [1, 2])

    def test_control_freeze_identity_standings_mod12_mod13(self):
        for freeze in (mod12._freeze, mod13._freeze):
            shared_set = {1, 2}
            result = freeze([shared_set, shared_set])
            self.assertIs(result[0], result[1])
            shared_frozen = frozenset((1, 2))
            result = freeze([shared_frozen, shared_frozen])
            self.assertIs(result[0], result[1])
            shared_tuple = (1, 2)
            result = freeze([shared_tuple, shared_tuple])
            self.assertIs(result[0], result[1])
            holder = []
            cyclic = (holder,)
            holder.append(cyclic)
            copied = freeze(holder)
            self.assertIs(copied[0][0], copied)

    def test_control_mod12_plain_text_names_still_judged(self):
        self.assertEqual(mod12._stored_text("amount"), "amount")
        self.assertTrue(mod12._folded_name_matches("amount", "amount"))
        self.assertFalse(mod12._folded_name_matches("figure", "amount"))
        self.assertTrue(mod12._carries_barred_money_value(
            {"amount": 10, "currency": "USD"}))
        self.assertFalse(mod12._carries_barred_money_value(
            {"figure": 10, "currency": "USD"}))


if __name__ == "__main__":
    unittest.main()
