"""Pins for fix wave 13, Builder 10, Group 10.

Rows R13-049 and R13-056 to R13-059 of the Round 13 register.
"""
import unittest

from crucible import mod03, mod04, mod05, mod06, mod07, mod08, mod10, mod13, mod14


def _deep_list(n):
    value = 1
    for _ in range(n):
        value = [value]
    return value


def _deep_dict(n):
    value = 1
    for _ in range(n):
        value = {"a": value}
    return value


def _cyclic_list():
    value = []
    value.append(value)
    return value


class TestR13049Mod10BooleanValidators(unittest.TestCase):
    def _non_record_returns_false(self, act, control):
        for handed in (None, 42, "text"):
            self.assertIs(act(handed), False)
        self.assertIsInstance(act(control), bool)

    def test_storage_claim(self):
        self._non_record_returns_false(mod10.validate_storage_claim, {})

    def test_store_placement(self):
        self._non_record_returns_false(mod10.validate_store_placement, {})

    def test_sample_record(self):
        self._non_record_returns_false(mod10.validate_sample_record, {})

    def test_retention_record(self):
        self._non_record_returns_false(mod10.validate_retention_record, {})

    def test_retention_report(self):
        self._non_record_returns_false(mod10.validate_retention_report, {})

    def test_retention_sizing(self):
        control = {"workings": {"central_form": {}, "high_form": {"events_per_agent_per_day": 1}}}
        self._non_record_returns_false(mod10.validate_retention_sizing, control)
        self.assertIs(mod10.validate_retention_sizing(control), True)

    def test_annotation_claim(self):
        self._non_record_returns_false(mod10.validate_annotation_claim, {})

    def test_daily_aggregates(self):
        self.assertIs(mod10.validate_daily_aggregates(42), False)
        self.assertIs(mod10.validate_daily_aggregates([42]), False)
        self.assertIs(mod10.validate_daily_aggregates(
            [{"viewer_id": "v1"}]), True)


class TestR13056EscrowContractStateWording(unittest.TestCase):
    def test_variant_full_form(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c1", variant="B-9")
        text = str(caught.exception)
        self.assertIn("escrow_contract_state stands refused", text)
        self.assertIn("B-9", text)
        self.assertIn("no escrow contract state stands returned", text)
        with self.assertRaises(ValueError) as caught2:
            mod06.escrow_result("k", variant="B-9")
        self.assertIn("escrow_result stands refused", str(caught2.exception))

    def test_lien_full_form(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c1", lien_state="bogus lien")
        text = str(caught.exception)
        self.assertIn("escrow_contract_state stands refused", text)
        self.assertIn("bogus lien", text)
        self.assertIn("no escrow contract state stands returned", text)
        state = mod06.escrow_contract_state("c1")
        self.assertEqual(state["variant"], "B-4")


class TestR13057AgentIdentifierSentence(unittest.TestCase):
    def _record(self, identifier):
        return {"agent_identifier": identifier, "day": 1,
                "feature_values": {"activity": 2},
                "records_for_agent_and_day": []}

    def test_type_and_empty_faults_read_apart_and_carry_value(self):
        with self.assertRaises(Exception) as caught_number:
            mod08.accept_detection_input(self._record(123))
        with self.assertRaises(Exception) as caught_empty:
            mod08.accept_detection_input(self._record(""))
        number_text = str(caught_number.exception)
        empty_text = str(caught_empty.exception)
        self.assertNotEqual(number_text, empty_text)
        self.assertIn("123", number_text)
        self.assertIn("''", empty_text)
        accepted = mod08.accept_detection_input(self._record("agent-1"))
        self.assertEqual(accepted["agent_identifier"], "agent-1")


class TestR13058FarmEdgeForm(unittest.TestCase):
    def test_number_edge_states_form_not_size(self):
        with self.assertRaises(Exception) as caught:
            mod03.construct_farm(["m1", "m2"], farm_size=2, edges=[5])
        text = str(caught.exception)
        self.assertNotIn("size two", text)
        self.assertIn("form", text)
        self.assertIn("5", text)
        with self.assertRaises(Exception) as caught_size:
            mod03.construct_farm(["m1", "m2"], farm_size=2, edges=[["m1", "m2", "m1"]])
        self.assertIn("size two", str(caught_size.exception))


class TestR13059DepthCycleCompleteness(unittest.TestCase):
    def test_mod14_pilot_depth_full_form(self):
        with self.assertRaises(Exception) as caught:
            mod14.pilot_run("timing", _deep_list(105))
        text = str(caught.exception)
        self.assertIn("100", text)
        self.assertIn("at root", text)
        self.assertIn("count", text)
        self.assertIn("no pilot run stands performed", text)

    def test_mod14_pilot_cycle_full_form(self):
        with self.assertRaises(Exception) as caught:
            mod14.pilot_run("timing", _cyclic_list())
        text = str(caught.exception)
        self.assertIn("cycle", text)
        self.assertIn("at root", text)
        self.assertIn("stands refused", text)
        self.assertIn("no pilot run stands performed", text)

    def test_mod03_guard_counting_and_consequence(self):
        with self.assertRaises(Exception) as caught:
            mod03._traversal_guard(_deep_list(3), 101, set(), "root/a")
        text = str(caught.exception)
        self.assertIn("count", text)
        self.assertIn("no traversal stands performed", text)
        cyclic = _cyclic_list()
        with self.assertRaises(Exception) as caught_cycle:
            mod03._traversal_guard(cyclic, 0, {id(cyclic)}, "root/a")
        self.assertIn("no traversal stands performed", str(caught_cycle.exception))
        with self.assertRaises(ValueError) as caught_pole:
            mod05.panel_inputs(_deep_dict(105))
        pole = str(caught_pole.exception)
        self.assertIn("count", pole)
        self.assertIn("no panel inputs stand returned", pole)

    def test_mod04_guards_counting_and_consequence(self):
        with self.assertRaises(Exception) as caught:
            mod04._clean_value(_cyclic_list())
        self.assertIn("no cleaning stands performed", str(caught.exception))
        with self.assertRaises(Exception) as caught2:
            mod04._value_appears("x", _deep_list(105))
        text = str(caught2.exception)
        self.assertIn("count", text)
        self.assertIn("no presence answer stands", text)

    def test_mod07_copy_guard_counting_and_consequence(self):
        with self.assertRaises(Exception) as caught:
            mod07._copy_guard(_deep_list(105))
        text = str(caught.exception)
        self.assertIn("count", text)
        self.assertIn("no copy stands made", text)
        with self.assertRaises(Exception) as caught_cycle:
            mod07._copy_guard(_cyclic_list())
        self.assertIn("no copy stands made", str(caught_cycle.exception))

    def test_mod08_barred_guards_counting_and_consequence(self):
        with self.assertRaises(Exception) as caught:
            mod08._find_barred(_deep_list(105))
        text = str(caught.exception)
        self.assertIn("count", text)
        self.assertIn("no delivery stands accepted", text)
        with self.assertRaises(Exception) as caught_cycle:
            mod08._find_barred(_cyclic_list())
        self.assertIn("no delivery stands accepted", str(caught_cycle.exception))
        with self.assertRaises(Exception) as caught_copy:
            mod08._undirected_copy(_deep_list(105))
        text_copy = str(caught_copy.exception)
        self.assertIn("count", text_copy)
        self.assertIn("no copy stands made", text_copy)

    def test_mod13_guards_counting_and_consequence(self):
        with self.assertRaises(Exception) as caught:
            mod13._strict_eq(_deep_list(105), _deep_list(105))
        text = str(caught.exception)
        self.assertIn("count", text)
        self.assertIn("no comparison stands performed", text)
        with self.assertRaises(Exception) as caught2:
            mod13.extend_history([_deep_list(105)], {"rule_set_version": "v", "run_id": "r"})
        self.assertIn("count", str(caught2.exception))


if __name__ == "__main__":
    unittest.main()
