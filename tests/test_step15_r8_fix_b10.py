import unittest
import crucible.mod07 as mod07
import crucible.mod11 as mod11

FIELD10_TEXT = (
    "seam status: no cross seam effect; "
    "kill check: self checked only; "
    "dependence mark: DQ-164 confirmation form, recording that "
    "DQ-164 stands settled as confirmation only; "
    "Parley Q3 statement: no part of the result encodes Parley "
    "Q3 behaviour; "
    "core only qualifier: this unit is a core only result; "
    "anchor scenario statement: no anchor scenario is used in "
    "this unit."
)
FIELD10_NO_DEPENDENCE_TEXT = (
    "seam status: no cross seam effect; "
    "kill check: self checked only; "
    "dependence: no dependence mark applies; "
    "Parley Q3 statement: no part of the result encodes Parley "
    "Q3 behaviour; "
    "core only qualifier: this unit is a core only result; "
    "anchor scenario statement: no anchor scenario is used in "
    "this unit."
)
CLAIM_TEXT = (
    "At the sampled points within the stated scope, the result "
    "holds for the sampled points only, and nothing is claimed "
    "beyond the stated limits."
)
GROUNDING_TEXT = (
    "This unit rests on the retained run records within the "
    "stated scope, and its limits are that nothing is claimed "
    "beyond the sampled points in this unit."
)

def anchor_field10(scenario):
    return (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording that "
        "DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes Parley "
        "Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: anchor scenario " + scenario +
        " is used in this unit, awaiting a ruling, citing DQ-163."
    )

def compliant_unit():
    unit = {field: "value for " + field for field in mod11.HEADLINE_UNIT_FIELDS}
    unit["claim_sentence"] = CLAIM_TEXT
    unit["grounding_sentence"] = GROUNDING_TEXT
    unit["qualifiers_and_markings_block"] = FIELD10_TEXT
    unit["holding_region"] = {"sampled_points": [{"axis_values": {"farm size": 200}, "outcome": "holds"}]}
    unit["failure_region"] = {"sampled_points": [{"axis_values": {"farm size": 800}, "outcome": "fails"}]}
    return unit

def unit_with_claim_extra(sentence, field10=None):
    unit = compliant_unit()
    unit["claim_sentence"] = CLAIM_TEXT + " " + sentence
    if field10 is not None:
        unit["qualifiers_and_markings_block"] = field10
    return unit

class TestR7019LexiconWords(unittest.TestCase):
    def test_word_dog(self):
        self.assertTrue(mod11._is_readable_word("dog"))
    def test_word_cat(self):
        self.assertTrue(mod11._is_readable_word("cat"))
    def test_word_sat(self):
        self.assertTrue(mod11._is_readable_word("sat"))
    def test_word_sun(self):
        self.assertTrue(mod11._is_readable_word("sun"))
    def test_word_man(self):
        self.assertTrue(mod11._is_readable_word("man"))
    def test_word_dance(self):
        self.assertTrue(mod11._is_readable_word("dance"))
    def test_word_ball(self):
        self.assertTrue(mod11._is_readable_word("ball"))
    def test_word_fire(self):
        self.assertTrue(mod11._is_readable_word("fire"))
    def test_word_bread(self):
        self.assertTrue(mod11._is_readable_word("bread"))
    def test_word_coffee(self):
        self.assertTrue(mod11._is_readable_word("coffee"))
    def test_word_sky(self):
        self.assertTrue(mod11._is_readable_word("sky"))
    def test_word_city(self):
        self.assertTrue(mod11._is_readable_word("city"))
    def test_word_chair(self):
        self.assertTrue(mod11._is_readable_word("chair"))
    def test_word_desert(self):
        self.assertTrue(mod11._is_readable_word("desert"))
    def test_word_harbor(self):
        self.assertTrue(mod11._is_readable_word("harbor"))
    def test_word_meadow(self):
        self.assertTrue(mod11._is_readable_word("meadow"))
    def test_word_sunset(self):
        self.assertTrue(mod11._is_readable_word("sunset"))
    def test_word_sunrise(self):
        self.assertTrue(mod11._is_readable_word("sunrise"))
    def test_word_thunder(self):
        self.assertTrue(mod11._is_readable_word("thunder"))
    def test_word_lightning(self):
        self.assertTrue(mod11._is_readable_word("lightning"))
    def test_word_rainbow(self):
        self.assertTrue(mod11._is_readable_word("rainbow"))
    def test_word_breeze(self):
        self.assertTrue(mod11._is_readable_word("breeze"))
    def test_word_shadow(self):
        self.assertTrue(mod11._is_readable_word("shadow"))
    def test_word_mirror(self):
        self.assertTrue(mod11._is_readable_word("mirror"))
    def test_word_candle(self):
        self.assertTrue(mod11._is_readable_word("candle"))
    def test_word_button(self):
        self.assertTrue(mod11._is_readable_word("button"))
    def test_word_wallet(self):
        self.assertTrue(mod11._is_readable_word("wallet"))
    def test_word_basket(self):
        self.assertTrue(mod11._is_readable_word("basket"))
    def test_word_kettle(self):
        self.assertTrue(mod11._is_readable_word("kettle"))
    def test_word_blanket(self):
        self.assertTrue(mod11._is_readable_word("blanket"))
    def test_word_pillow(self):
        self.assertTrue(mod11._is_readable_word("pillow"))
    def test_word_curtain(self):
        self.assertTrue(mod11._is_readable_word("curtain"))
    def test_word_carpet(self):
        self.assertTrue(mod11._is_readable_word("carpet"))
    def test_word_ladder(self):
        self.assertTrue(mod11._is_readable_word("ladder"))
    def test_word_hammer(self):
        self.assertTrue(mod11._is_readable_word("hammer"))
    def test_word_needle(self):
        self.assertTrue(mod11._is_readable_word("needle"))
    def test_word_thread(self):
        self.assertTrue(mod11._is_readable_word("thread"))
    def test_word_copper(self):
        self.assertTrue(mod11._is_readable_word("copper"))
    def test_word_marble(self):
        self.assertTrue(mod11._is_readable_word("marble"))
    def test_word_velvet(self):
        self.assertTrue(mod11._is_readable_word("velvet"))
    def test_word_cotton(self):
        self.assertTrue(mod11._is_readable_word("cotton"))
    def test_word_wooden(self):
        self.assertTrue(mod11._is_readable_word("wooden"))
    def test_word_gold(self):
        self.assertTrue(mod11._is_readable_word("gold"))
    def test_word_zinc(self):
        self.assertTrue(mod11._is_readable_word("zinc"))
    def test_word_east(self):
        self.assertTrue(mod11._is_readable_word("east"))
    def test_word_joyfully(self):
        self.assertTrue(mod11._is_readable_word("joyfully"))
    def test_word_actor(self):
        self.assertTrue(mod11._is_readable_word("actor"))
    def test_word_boundary(self):
        self.assertTrue(mod11._is_readable_word("boundary"))
    def test_word_canary(self):
        self.assertTrue(mod11._is_readable_word("canary"))
    def test_word_carriage(self):
        self.assertTrue(mod11._is_readable_word("carriage"))
    def test_word_closure(self):
        self.assertTrue(mod11._is_readable_word("closure"))
    def test_word_defect(self):
        self.assertTrue(mod11._is_readable_word("defect"))
    def test_word_ledger(self):
        self.assertTrue(mod11._is_readable_word("ledger"))
    def test_word_mechanism(self):
        self.assertTrue(mod11._is_readable_word("mechanism"))
    def test_word_partition(self):
        self.assertTrue(mod11._is_readable_word("partition"))
    def test_word_probability(self):
        self.assertTrue(mod11._is_readable_word("probability"))
    def test_word_reputation(self):
        self.assertTrue(mod11._is_readable_word("reputation"))
    def test_word_settlement(self):
        self.assertTrue(mod11._is_readable_word("settlement"))
    def test_word_anxiously(self):
        self.assertTrue(mod11._is_readable_word("anxiously"))
    def test_word_eagerly(self):
        self.assertTrue(mod11._is_readable_word("eagerly"))
    def test_word_nervously(self):
        self.assertTrue(mod11._is_readable_word("nervously"))
    def test_word_furthermore(self):
        self.assertTrue(mod11._is_readable_word("furthermore"))
    def test_word_nevertheless(self):
        self.assertTrue(mod11._is_readable_word("nevertheless"))
    def test_word_nonetheless(self):
        self.assertTrue(mod11._is_readable_word("nonetheless"))
    def test_word_consequently(self):
        self.assertTrue(mod11._is_readable_word("consequently"))
    def test_word_accordingly(self):
        self.assertTrue(mod11._is_readable_word("accordingly"))
    def test_word_precision(self):
        self.assertTrue(mod11._is_readable_word("precision"))
    def test_word_reliability(self):
        self.assertTrue(mod11._is_readable_word("reliability"))
    def test_word_validity(self):
        self.assertTrue(mod11._is_readable_word("validity"))
    def test_word_boy(self):
        self.assertTrue(mod11._is_readable_word("boy"))
    def test_word_girl(self):
        self.assertTrue(mod11._is_readable_word("girl"))
    def test_word_eye(self):
        self.assertTrue(mod11._is_readable_word("eye"))

class TestR7019ControlsAndActs(unittest.TestCase):
    def test_invented_strings_still_count_as_no_word(self):
        for word in ("blorple", "snizzle", "frumious", "quandrix"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word))
    def test_plain_sentence_counts(self):
        self.assertEqual(mod11._plain_word_count("the dog and the cat sat in the sun"), 6)
        self.assertEqual(mod11._plain_word_count("chair desert harbor"), 3)
    def test_readout_canary_boundary_passes(self):
        readout = {"quantities": [{"name": "canary boundary", "recorded_number": 3, "class_based": True, "class_rule": "canary boundary reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))
    def test_readout_precision_reliability_passes(self):
        readout = {"quantities": [{"name": "precision reliability", "recorded_number": 3, "class_based": True, "class_rule": "precision reliability validity stand"}]}
        self.assertTrue(mod11.validate_readout(readout))
    def test_readout_actor_ledger_passes(self):
        readout = {"quantities": [{"name": "actor ledger", "recorded_number": 3, "class_based": True, "class_rule": "actor ledger reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

class TestR7020ParleyFormsWherever(unittest.TestCase):
    def test_spaced_q_far_direct(self):
        self.assertEqual(mod11._parley_grounds_stated("this claim rests on parley in the matter of the ruling marked q2"), {"2"})
    def test_spaced_q_far_denied_fails(self):
        unit = unit_with_claim_extra("This claim rests on Parley in the matter of the ruling marked Q2.", field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))
    def test_spaced_q_far_conforming_passes(self):
        unit = unit_with_claim_extra("This claim rests on Parley in the matter of the ruling marked Q2.")
        self.assertTrue(mod11.validate_headline_unit(unit))
    def test_separated_q_far_direct(self):
        self.assertEqual(mod11._parley_grounds_stated("this claim rests on parley and on the ruling in the record marked q 2 in full"), {"2"})
    def test_separated_q_far_denied_fails(self):
        unit = unit_with_claim_extra("This claim rests on Parley and on the ruling in the record marked q 2 in full.", field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))
    def test_question_stated_as_two_direct(self):
        self.assertEqual(mod11._parley_grounds_stated("parley question stated two"), {"2"})
    def test_question_stated_sentence_denied_fails(self):
        unit = unit_with_claim_extra("This claim rests on the Parley question stated as two in the record.", field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))
    def test_question_stated_sentence_conforming_passes(self):
        unit = unit_with_claim_extra("This claim rests on the Parley question stated as two in the record.")
        self.assertTrue(mod11.validate_headline_unit(unit))
    def test_question_published_recorded_as_two_denied_fails(self):
        unit = unit_with_claim_extra("This claim rests on the Parley question published and recorded as two.", field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))
    def test_numbered_as_two_direct(self):
        self.assertEqual(mod11._parley_grounds_stated("parley question numbered as two"), {"2"})
    def test_numbered_as_two_denied_fails(self):
        unit = unit_with_claim_extra("This claim rests on the Parley question numbered as two.", field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))
    def test_numbered_as_two_conforming_passes(self):
        unit = unit_with_claim_extra("This claim rests on the Parley question numbered as two.")
        self.assertTrue(mod11.validate_headline_unit(unit))
    def test_testanchor_direct(self):
        self.assertTrue(mod11._anchor_ground_stated("the result rests on testanchor an-9"))
    def test_testanchor_denied_fails(self):
        unit = unit_with_claim_extra("The result rests on testanchor AN-9.")
        self.assertFalse(mod11.validate_headline_unit(unit))
    def test_testanchor_conforming_passes(self):
        unit = unit_with_claim_extra("The result rests on testanchor AN-9.", field10=anchor_field10("AN-9"))
        self.assertTrue(mod11.validate_headline_unit(unit))
    def test_r6028_controls_still_stand(self):
        self.assertEqual(mod11._parley_grounds_stated("parley question numbered two"), {"2"})
        self.assertEqual(mod11._parley_grounds_stated("parley q2"), {"2"})
        self.assertTrue(mod11._anchor_ground_stated("the result rests on scenarioanchor an-9"))
        self.assertTrue(mod11._anchor_ground_stated("the result rests on anchortest an-9"))
        self.assertEqual(mod11._parley_grounds_stated("parley question with no stated number"), set())
        self.assertFalse(mod11._anchor_ground_stated("the result rests on a plain point"))

class LyingStrip(str):
    def strip(self, *args, **kwargs):
        return "content"

def tracer_set_with(field, value):
    records = mod07.tracer_passage_records("run-b10")
    records[0][field] = value
    return records

BLANK_CHARS = ["\u200b", "\ufeff", "\u00ad", "\u2060", "\u034f", "\u180b", "\ufe00", "\ufe0f", "\u2800", "\u115f"]
FIELDS = ("point_in_run", "what_in_fact_passed")

class TestR7025TracerBlank(unittest.TestCase):
    def test_valid_set_control(self):
        self.assertTrue(mod07.validate_tracer_passage_set(mod07.tracer_passage_records("run-b10")))
    def test_content_control(self):
        for field in FIELDS:
            self.assertTrue(mod07.validate_tracer_passage_set(tracer_set_with(field, "seam")))
    def test_each_blank_char_both_fields(self):
        for field in FIELDS:
            for char in BLANK_CHARS:
                with self.subTest(field=field, code=hex(ord(char))):
                    self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, char)))
    def test_mixed_blank_string(self):
        for field in FIELDS:
            self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, " \u200b ")))
    def test_bytes_blank_forms(self):
        for field in FIELDS:
            for value in ("\u200b".encode("utf-8"), "\u2800".encode("utf-8")):
                with self.subTest(field=field, value=value):
                    self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, value)))
    def test_bytearray_blank_form(self):
        for field in FIELDS:
            self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, bytearray("\u200b".encode("utf-8")))))
    def test_memoryview_blank_forms(self):
        for field in FIELDS:
            for value in ("\u200b".encode("utf-8"), "\u115f".encode("utf-8")):
                with self.subTest(field=field, value=value):
                    self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, memoryview(value))))
    def test_lying_strip_blank_stored(self):
        for field in FIELDS:
            self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, LyingStrip("   "))))
            self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, LyingStrip(""))))
            self.assertFalse(mod07.validate_tracer_passage_set(tracer_set_with(field, LyingStrip("\u200b"))))

if __name__ == "__main__":
    unittest.main()
