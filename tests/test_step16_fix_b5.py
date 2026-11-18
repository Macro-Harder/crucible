"""Step 16 fix wave, Builder 5: R16-08 and R16-12.

The refusal convention, as stated in the open in
design/steps/step-16-fix-5.md section 1 before this cure stood
built: one delivery form per stop class, carrying named failure
content at every stop (a named failure, the field or the ground
in words, and the next step in words, or at a raising door the
consequence in words).

Classes under test:
G, the DQ7-02 gate stop: the gated refusal dict at record doors,
the raised GatedRun at executable doors, both naming the gate,
the ground, and the next step as the decision on the DQ7-02
adoption record, seed_drawn False in the record form.
I, the input failure stop: the named input failure dict at record
doors, completed with ground_in_words and next_step.
L, the lookup failure stop: the raised LookupFailure naming the
failure, the identifier, and the next step.
The DQ7-02 gate content stands preserved in substance by every
test here: the gate named, the ground stated, seed_drawn False.
No seed stands drawn by any test.
"""
import unittest

from crucible import mod02, mod04, mod10, mod12


class TestR1612Mod04GateWording(unittest.TestCase):
    """R16-12: the mod04 GatedRun closing clause names the decision
    on the DQ7-02 adoption record, as mod02 and mod12 state it."""

    def test_tick_engine_run_message_names_adoption_record_decision(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.TickEngine().run()
        text = str(caught.exception)
        self.assertIn("decision on the DQ7-02 adoption record", text)
        self.assertNotIn("a decision elsewhere", text)

    def test_tick_message_names_adoption_record_decision(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.TickEngine().tick()
        text = str(caught.exception)
        self.assertIn("decision on the DQ7-02 adoption record", text)
        self.assertNotIn("a decision elsewhere", text)

    def test_delivery_message_names_adoption_record_decision(self):
        engine = mod04.TickEngine()
        with self.assertRaises(mod04.GatedRun) as caught:
            engine.detection_delivery.deliver_running({})
        text = str(caught.exception)
        self.assertIn("decision on the DQ7-02 adoption record", text)
        self.assertNotIn("a decision elsewhere", text)

    def test_gate_content_preserved_in_mod04_message(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.TickEngine().run()
        text = str(caught.exception)
        self.assertIn("DERIVATION-GATED", text)
        self.assertIn("DQ7-02", text)
        self.assertIn("No adoption record stands for this gate", text)
        self.assertIn("nothing was started or drawn", text)


class TestR1608GateDictFormStands(unittest.TestCase):
    """R16-08, class G at record doors: the gated dict already
    carries the full named content; these pins state that the
    cure leaves it standing in substance."""

    def test_mod02_gated_refusal_content(self):
        refusal = mod02.derive_seed()
        self.assertEqual(refusal["failure"], "DERIVATION-GATED")
        self.assertEqual(refusal["gate"], "DQ7-02")
        self.assertFalse(refusal["seed_drawn"])
        self.assertIn("adoption record", refusal["ground_in_words"])
        self.assertIn(
            "decision on the DQ7-02 adoption record",
            refusal["next_step"])

    def test_mod12_gated_start_content(self):
        refusal = mod12.start_run(
            run_class="screening", family_id="fam-b5")
        self.assertEqual(refusal["failure"], "DERIVATION-GATED")
        self.assertEqual(refusal["gate"], "DQ7-02")
        self.assertFalse(refusal["seed_drawn"])
        self.assertFalse(refusal["run_started"])
        self.assertIn("adoption record", refusal["ground_in_words"])
        self.assertIn(
            "decision on the DQ7-02 adoption record",
            refusal["next_step"])


class TestR1608InputFailureDictContent(unittest.TestCase):
    """R16-08, class I at record doors: the named input failure
    dict carries ground_in_words and next_step beside its failure,
    as the gated dict does."""

    def _assert_full_content(self, result):
        self.assertEqual(result["status"], "input failure")
        self.assertFalse(result["run_started"])
        self.assertFalse(result["seed_drawn"])
        self.assertIn("ground_in_words", result)
        self.assertIn("next_step", result)
        self.assertTrue(result["ground_in_words"])
        self.assertTrue(result["next_step"])

    def test_start_run_missing_class(self):
        self._assert_full_content(mod12.start_run(family_id="fam-b5"))

    def test_start_run_bad_class(self):
        result = mod12.start_run(run_class="bogus", family_id="fam-b5")
        self._assert_full_content(result)
        self.assertIn("bogus", result["failure"])

    def test_start_run_missing_family(self):
        result = mod12.start_run(run_class="screening")
        self._assert_full_content(result)
        self.assertIn("family identifier", result["failure"])

    def test_start_sweep_missing_family(self):
        self._assert_full_content(mod12.start_sweep())

    def test_input_failure_next_step_names_the_correction(self):
        result = mod12.start_run(run_class="bogus", family_id="fam-b5")
        self.assertIn("no seed stands drawn", result["next_step"])


class TestR1608Mod02TextRefusalContent(unittest.TestCase):
    """R16-08, class I at the mod02 derivation text door: the two
    thinner dict contents (not a text, and the barred form) carry
    a next_step beside their ground, as the gated branch does."""

    def test_not_a_text_refusal_carries_next_step(self):
        refusal = mod02.derivation_text_refusal(123)
        self.assertEqual(refusal["failure"], "INVALID-TEXT")
        self.assertFalse(refusal["valid"])
        self.assertIn("next_step", refusal)
        self.assertTrue(refusal["next_step"])

    def test_barred_form_refusal_carries_next_step(self):
        refusal = mod02.derivation_text_refusal(
            "derive by arithmetic on a root seed")
        self.assertEqual(refusal["failure"], "BARRED-DERIVATION-FORM")
        self.assertFalse(refusal["valid"])
        self.assertIn("next_step", refusal)
        self.assertTrue(refusal["next_step"])

    def test_gated_branch_keeps_full_content(self):
        refusal = mod02.derivation_text_refusal(
            "an ordinary derivation text")
        self.assertEqual(refusal["failure"], "DERIVATION-GATED")
        self.assertFalse(refusal["seed_drawn"])
        self.assertIn(
            "decision on the DQ7-02 adoption record",
            refusal["next_step"])


class TestR1608LookupFailureContent(unittest.TestCase):
    """R16-08, class L: the LookupFailure message stands pinned
    in its exact form by the existing suite (args[0] equality
    pins in test_step15_r21_fix_b2 and the mod14 error carriage
    message pins in test_step15_r16_fix_b10). The convention's
    next step clause conflicts with those pins, so this door's
    cure stands HELD for the coordinator, stated in the open in
    the fix paper section 4. These tests guard the pinned form
    and the named failure record as they stand."""

    def test_lookup_failure_message_pinned_form_stands(self):
        failure = mod10.LookupFailure("run-absent-b5")
        self.assertEqual(
            failure.args[0],
            "one lookup resolution failure: run-absent-b5")

    def test_lookup_failure_record_stands(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.read_run_record("run-absent-b5")
        failure = caught.exception.failure
        self.assertEqual(failure["name"], "one lookup resolution failure")
        self.assertEqual(failure["run_identifier"], "run-absent-b5")
        self.assertFalse(failure["complete"])


if __name__ == "__main__":
    unittest.main()
