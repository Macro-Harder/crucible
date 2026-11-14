"""Step 15 rerun fix wave 9 pins, rows R9-023, R9-029, and
R9-037, at crucible/mod13.py, with the registry validity gate
limb at crucible/mod11.py.

Row R9-023: extend_history guards the handed history through
base class iteration but copies it through plain iteration, so
a list or tuple subclass storing one valid segment and yielding
that segment plus a past bound chain or a cycle returns the
whole yielded shape copied, and a yielded 2000 chain raises a
bare RecursionError.

Row R9-029: the extend_history bound refusal asserts the handed
history or the appended segment stands past the bound even
where the sole ground is a shallow cycle, and names neither the
ground nor the input that carries it.

Row R9-037: the registry comparison in its stated form stands
unbuilt. The brief at section 2.4 and the plan at Form 22 item 4
and section 6.1 item 13 place a comparison act in MOD-13, the
checker that did not compile the registry, reading the retained
run records as the run log, every bearing run in the claim
entry, failed runs in and pilot runs out, before any headline
claim is reported. MOD-13 carries no registry act, and the
MOD-11 judging acts validate an entry with no run log present
and with a mismatched run log.

Control pins stand both ways: plain and within bound extensions
copy whole, the MOD-13 pins of tests/test_step15_r9_fix_b12.py
stand whole in mirrored form, the freeze identity standings of
rows R7-023 and R7-024 stand at MOD-13, and the MOD-11 judging
forms that already stood, the legacy run log form and the same
person bar, stand unchanged. Values are simulated and test
values only.
"""
import unittest

from crucible import mod11, mod13


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


VALID_SEGMENT = {"rule_set_version": "v1", "run_id": "r1"}


class YieldingList(list):
    """A list subclass whose stored contents and whose yielded
    contents differ: the base storage holds the stored list,
    and its own iteration yields the yielded list."""

    def __init__(self, stored, yielded):
        list.__init__(self, stored)
        self._yielded = yielded

    def __iter__(self):
        return iter(self._yielded)


class YieldingTuple(tuple):
    """A tuple subclass with the same split as YieldingList."""

    def __new__(cls, stored, yielded):
        return tuple.__new__(cls, stored)

    def __init__(self, stored, yielded):
        self._yielded = yielded

    def __iter__(self):
        return iter(self._yielded)


def registry_entry(**overrides):
    entry = {
        "claim_identifier": "claim-1",
        "sweep_family_identifier": "fam-1",
        "phase_judgements": {
            "before_runs": "judged",
            "after_runs": "judged",
        },
        "screening_run_identifiers": ["run-1", "run-2"],
        "held_out_confirmation_run_identifiers": ["run-3"],
    }
    entry.update(overrides)
    return entry


def run_record(run_id, run_class="screening", status="completed"):
    return {
        "run_identifier": run_id,
        "sweep_family_identifier": "fam-1",
        "run_class": run_class,
        "run_status": status,
    }


MATCHING_LOG = [
    run_record("run-1", "screening", "completed"),
    run_record("run-2", "screening", "failed"),
    run_record("run-3", "confirmation", "completed"),
]


class TestR9023CopyThroughGuardReading(unittest.TestCase):

    def test_list_yielded_past_bound_chain_not_copied(self):
        yielded = [dict(VALID_SEGMENT), list_chain(150)]
        history = YieldingList([dict(VALID_SEGMENT)], yielded)
        result = mod13.extend_history(history, {"rule_set_version": "v1"})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["run_id"], "r1")
        self.assertEqual(result[1]["segment_order"], 2)

    def test_list_yielded_cyclic_dict_not_copied(self):
        cyclic = {}
        cyclic["self"] = cyclic
        yielded = [dict(VALID_SEGMENT), cyclic]
        history = YieldingList([dict(VALID_SEGMENT)], yielded)
        result = mod13.extend_history(history, {"rule_set_version": "v1"})
        self.assertEqual(len(result), 2)

    def test_list_yielded_cyclic_list_not_copied(self):
        cyclic = []
        cyclic.append(cyclic)
        yielded = [dict(VALID_SEGMENT), cyclic]
        history = YieldingList([dict(VALID_SEGMENT)], yielded)
        result = mod13.extend_history(history, {"rule_set_version": "v1"})
        self.assertEqual(len(result), 2)

    def test_list_yielded_deep_chain_raises_no_bare_recursion(self):
        yielded = [dict(VALID_SEGMENT), list_chain(2000)]
        history = YieldingList([dict(VALID_SEGMENT)], yielded)
        result = mod13.extend_history(history, {"rule_set_version": "v1"})
        self.assertEqual(len(result), 2)

    def test_tuple_yielded_past_bound_chain_not_copied(self):
        yielded = [dict(VALID_SEGMENT), list_chain(150)]
        history = YieldingTuple([dict(VALID_SEGMENT)], yielded)
        result = mod13.extend_history(history, {"rule_set_version": "v1"})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["run_id"], "r1")


class TestR9029RefusalStatesTrueGround(unittest.TestCase):

    def refusal_text(self, history, segment):
        with self.assertRaises(mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(history, segment)
        return str(caught.exception)

    def test_segment_shallow_cycle_names_segment_and_cycle_only(self):
        cyclic = []
        cyclic.append(cyclic)
        segment = {"rule_set_version": "v1", "held": cyclic}
        text = self.refusal_text([dict(VALID_SEGMENT)], segment)
        self.assertIn("segment", text)
        self.assertTrue("cycle" in text or "cyclic" in text)
        self.assertNotIn("past the bound", text)

    def test_history_shallow_cycle_names_history_and_cycle_only(self):
        cyclic = []
        cyclic.append(cyclic)
        history = [dict(VALID_SEGMENT), {"held": cyclic}]
        text = self.refusal_text(history, {"rule_set_version": "v1"})
        self.assertIn("history", text)
        self.assertTrue("cycle" in text or "cyclic" in text)
        self.assertNotIn("past the bound", text)

    def test_segment_past_bound_names_segment_and_bound_only(self):
        segment = {"rule_set_version": "v1", "deep_field": list_chain(150)}
        text = self.refusal_text([dict(VALID_SEGMENT)], segment)
        self.assertIn("segment", text)
        self.assertIn("past the bound", text)
        self.assertNotIn("cycle", text)
        self.assertNotIn("cyclic", text)

    def test_history_past_bound_names_history_and_bound_only(self):
        history = [dict(VALID_SEGMENT, deep_field=list_chain(150))]
        text = self.refusal_text(history, {"rule_set_version": "v1"})
        self.assertIn("history", text)
        self.assertIn("past the bound", text)
        self.assertNotIn("cycle", text)
        self.assertNotIn("cyclic", text)


class TestR9037RegistryComparisonBuiltInMod13(unittest.TestCase):

    def test_mod13_act_matching_log_with_failed_run_listed_passes(self):
        self.assertTrue(hasattr(mod13, "compare_registry_against_run_log"))
        result = mod13.compare_registry_against_run_log(
            registry_entry(), MATCHING_LOG)
        self.assertTrue(result["performed"])
        self.assertTrue(result["passed"])
        self.assertEqual(result["missing_run_identifiers"], [])

    def test_mod13_failed_run_missing_from_entry_fails(self):
        log = MATCHING_LOG + [run_record("run-9", "headline", "failed")]
        result = mod13.compare_registry_against_run_log(
            registry_entry(), log)
        self.assertTrue(result["performed"])
        self.assertFalse(result["passed"])
        self.assertIn("run-9", result["missing_run_identifiers"])

    def test_mod13_pilot_run_stands_outside_the_log(self):
        log = MATCHING_LOG + [run_record("pilot-1", "pilot", "completed")]
        result = mod13.compare_registry_against_run_log(
            registry_entry(), log)
        self.assertTrue(result["performed"])
        self.assertTrue(result["passed"])
        self.assertEqual(result["missing_run_identifiers"], [])

    def test_mod13_no_run_log_states_no_performed_comparison(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), None)
        self.assertFalse(result["performed"])
        self.assertFalse(result["passed"])

    def test_mod11_no_run_log_entry_not_valid(self):
        judged = mod11.judge_registry_entry(
            registry_entry(), compiler="registrar", checker="checker")
        self.assertFalse(judged["compared_against_run_log"])
        self.assertFalse(judged["valid"])
        self.assertFalse(mod11.validate_registry_entry(
            registry_entry(), compiler="registrar", checker="checker"))

    def test_mod11_mismatched_run_log_entry_not_valid(self):
        log = MATCHING_LOG + [run_record("run-9", "headline", "failed")]
        self.assertFalse(mod11.validate_registry_entry(
            registry_entry(), compiler="registrar", checker="checker",
            run_log=log))


class TestControlsStandingBothWays(unittest.TestCase):

    def test_control_plain_extend_stands(self):
        result = mod13.extend_history(
            [dict(VALID_SEGMENT)], {"note": "next"})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["segment_order"], 2)
        self.assertEqual(result[1]["linked_run"], "r1")
        self.assertEqual(result[1]["rule_set_version"], "v1")

    def test_control_b12_within_bound_extend_copies_whole(self):
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

    def test_control_b12_past_bound_segment_refused_in_named_form(self):
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

    def test_control_freeze_identity_standings_mod13(self):
        shared_set = {1, 2}
        result = mod13._freeze([shared_set, shared_set])
        self.assertIs(result[0], result[1])
        shared_frozen = frozenset((1, 2))
        result = mod13._freeze([shared_frozen, shared_frozen])
        self.assertIs(result[0], result[1])
        shared_tuple = (1, 2)
        result = mod13._freeze([shared_tuple, shared_tuple])
        self.assertIs(result[0], result[1])
        holder = []
        cyclic = (holder,)
        holder.append(cyclic)
        copied = mod13._freeze(holder)
        self.assertIs(copied[0][0], copied)

    def test_control_mod11_legacy_run_log_form_still_valid(self):
        entry = {"phase_judgements": {"before_runs": "judged",
                                      "after_runs": "judged"}}
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="independent checker",
            run_log={"runs": ["retirement run 1"]})
        self.assertTrue(judged["compared_against_run_log"])
        self.assertTrue(mod11.validate_registry_entry(
            entry, compiler="registrar", checker="independent checker",
            run_log={"runs": ["retirement run 1"]}))

    def test_control_mod11_same_person_still_refused(self):
        self.assertFalse(mod11.validate_registry_entry(
            registry_entry(), compiler="registrar", checker="registrar",
            run_log=MATCHING_LOG))

    def test_control_mod11_matching_run_record_log_valid(self):
        judged = mod11.judge_registry_entry(
            registry_entry(), compiler="registrar", checker="checker",
            run_log=MATCHING_LOG)
        self.assertTrue(judged["compared_against_run_log"])
        self.assertTrue(judged["valid"])
        self.assertTrue(mod11.validate_registry_entry(
            registry_entry(), compiler="registrar", checker="checker",
            run_log=MATCHING_LOG))


if __name__ == "__main__":
    unittest.main()
