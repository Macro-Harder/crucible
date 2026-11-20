"""Step 17 fix wave 4, Slice 9 defect tests.

Rows: FW4-16 (mod09 make_strategy refuses an identifier handing
in no identifier form), FW4-17 (mod04 gate refusal first sentence
in clean subject and verb form), FW4-18 (mod16 fixture_record
telling on an identifier naming no fixture).
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod04, mod09, mod16


class TestFW416MakeStrategyIdentifier(unittest.TestCase):

    def test_none_identifier_refused_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as cm:
            mod09.make_strategy(None)
        message = str(cm.exception)
        self.assertIn("no strategy stands built", message)
        self.assertIn("identifier", message)

    def test_integer_identifier_refused_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as cm:
            mod09.make_strategy(7)
        message = str(cm.exception)
        self.assertIn("no strategy stands built", message)
        self.assertIn("text form", message)

    def test_empty_identifier_refused_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as cm:
            mod09.make_strategy("")
        self.assertIn("no strategy stands built", str(cm.exception))

    def test_whitespace_identifier_refused_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as cm:
            mod09.make_strategy("   ")
        self.assertIn("no strategy stands built", str(cm.exception))

    def test_text_identifier_builds_whole(self):
        record = mod09.make_strategy("conditional briber")
        self.assertEqual(record["strategy_identifier"],
                         "conditional briber")


class TestFW417GateRefusalSentence(unittest.TestCase):

    def _first_sentence(self, message):
        return message.split(". ")[0] + "."

    def test_module_run_first_sentence_clean(self):
        with self.assertRaises(mod04.GatedRun) as cm:
            mod04.run()
        message = str(cm.exception)
        self.assertEqual(
            self._first_sentence(message),
            "DERIVATION-GATED: an executable run stands gated "
            "on DQ7-02.")
        self.assertNotIn("executable runs stands", message)

    def test_module_tick_first_sentence_clean(self):
        with self.assertRaises(mod04.GatedRun) as cm:
            mod04.tick()
        message = str(cm.exception)
        self.assertTrue(message.startswith(
            "DERIVATION-GATED: an executable run stands gated "
            "on DQ7-02."))
        self.assertNotIn("stands gated on DQ7-02, a", message)

    def test_gate_limbs_unchanged(self):
        with self.assertRaises(mod04.GatedRun) as cm:
            mod04.TickEngine().run()
        message = str(cm.exception)
        self.assertIn("No adoption record stands for this gate",
                      message)
        self.assertIn("Nothing stands for the operator to do",
                      message)
        self.assertEqual(cm.exception.failure, "DERIVATION-GATED")
        self.assertEqual(cm.exception.gate, "DQ7-02")

    def test_running_delivery_first_sentence_clean(self):
        point = mod04.DeliveryPoint("point one", "destination one")
        with self.assertRaises(mod04.GatedRun) as cm:
            point.deliver_running({})
        message = str(cm.exception)
        self.assertTrue(message.startswith(
            "DERIVATION-GATED: a running delivery stands gated "
            "on DQ7-02."))
        self.assertNotIn("running delivery stands gated on "
                         "DQ7-02 stands", message)


class TestFW418FixtureRecordTelling(unittest.TestCase):

    def test_misspelled_identifier_telling_limbs(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as cm:
            mod16.fixture_record("F-0l")
        message = str(cm.exception)
        self.assertIn("fixture lookup failure", message)
        self.assertIn("names no fixture", message)
        self.assertIn("fixture_inventory", message)
        self.assertIn("30 standing", message)

    def test_unknown_identifier_telling_limbs(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as cm:
            mod16.fixture_record("F-99")
        message = str(cm.exception)
        self.assertIn("names no fixture", message)
        self.assertIn("next step", message.lower())

    def test_valid_fixture_still_served(self):
        line = mod16.fixture_record("F-01")
        self.assertEqual(line["fixture"], "F-01")
        self.assertEqual(len(mod16.fixture_inventory()), 30)

    def test_huge_identifier_stays_bounded(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as cm:
            mod16.fixture_record("x" * 5000)
        self.assertLessEqual(len(str(cm.exception)), 1500)


if __name__ == "__main__":
    unittest.main()
