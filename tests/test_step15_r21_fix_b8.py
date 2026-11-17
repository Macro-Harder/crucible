"""Pins for fix wave 20, Builder 8, Group 8, rows R20-032 to R20-040.

The MOD-02, MOD-03, and MOD-12 sentence rendering family under
the Orange 1 sentence form, on ruling (as). At every charged
locus the act judges the handed value on its form or stored
text and the judgement stands correct; the refusal or failure
sentence alone then renders the handed value through the string
or repr reading the value itself supplies, so the sentence names
a value the act did not judge. Each charged row carries
distinguishing pins stating the cured sentence, which fail on
the pristine code, and controls stating standings that hold on
the pristine code and on the cured code alike, the plain control
wording standing exact, so a cure that moves a judgement or
changes a plain sentence fails here.


Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

Pins for fix wave 21, Builder 8, Group 8, rows R21-016 and R21-017.

The MOD-13 sentence family, on ruling (bb). At each charged
locus the act judges the handed value on its stored text and
the judgement stands correct; the failure sentence alone then
renders the handed point or outcome through the repr reading
the value itself supplies, so the sentence names a value the
act did not judge. Each distinguishing pin hands the charged
act a text value storing one text whose repr reading answers
another, or raises, and states the cured sentence, which
names the stored text. Each control hands a plain value and
states a standing that holds on the pristine code and on the
cured code alike.
"""


import unittest
from crucible import mod02, mod03, mod12
from crucible import mod13


class LyingStr(str):
    """A text value storing one text whose string and repr
    readings answer another text."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie

    def __repr__(self):
        return "'" + self._lie + "'"


class ReprLiar:
    """A plain object standing in no stated form whose repr
    reading answers a stated form."""

    def __init__(self, lie):
        self._lie = lie

    def __repr__(self):
        return self._lie


class ReprRaises:
    """A plain object whose repr reading raises."""

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class TestR20032DomainSentence(unittest.TestCase):
    def test_lying_domain_named_on_stored_text(self):
        with self.assertRaises(ValueError) as cm:
            mod02.make_derivation_input(
                domain=LyingStr("bogus", "screening"))
        self.assertIn("vocabulary: bogus;", str(cm.exception))

    def test_bytes_domain_named_on_stored_text(self):
        with self.assertRaises(ValueError) as cm:
            mod02.make_derivation_input(domain=b"bogus")
        self.assertIn("vocabulary: bogus;", str(cm.exception))

    def test_control_plain_domain(self):
        with self.assertRaises(ValueError) as cm:
            mod02.make_derivation_input(domain="bogus")
        self.assertIn("vocabulary: bogus;", str(cm.exception))

    def test_control_stated_domain_builds(self):
        result = mod02.make_derivation_input(domain="screening")
        self.assertEqual(result["domain"], "screening")


class TestR20033PositionSentence(unittest.TestCase):
    def test_lying_position_named_on_form(self):
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(
                position=ReprLiar("5"), carried_positions=10)
        self.assertIn("no numeric form: ReprLiar;",
                      str(cm.exception))

    def test_control_plain_text_position(self):
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(
                position="abc", carried_positions=10)
        self.assertIn("no numeric form: 'abc';", str(cm.exception))

    def test_control_raising_repr_position_delivered(self):
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(
                position=ReprRaises(), carried_positions=10)
        self.assertIn("position argument stands in no numeric form",
                      str(cm.exception))
        self.assertNotIsInstance(cm.exception, RuntimeError)


class TestR20034CarriedPositionsSentence(unittest.TestCase):
    def test_lying_carried_named_on_form(self):
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(
                position=1, carried_positions=ReprLiar("10"))
        self.assertIn("no numeric form: ReprLiar;",
                      str(cm.exception))

    def test_control_plain_text_carried(self):
        with self.assertRaises(ValueError) as cm:
            mod02.draw_from_stream(
                position=1, carried_positions="xyz")
        self.assertIn("no numeric form: 'xyz';", str(cm.exception))


class TestR20035MixCountSentence(unittest.TestCase):
    def test_lying_identifier_named_on_stored_text(self):
        point = {"population_size": 1,
                 "archetype_mix": {LyingStr("arch-1", "arch-9"): -1}}
        with self.assertRaises(Exception) as cm:
            mod03.build_cast(point, [], strategy_class="fixed")
        self.assertIn("mix count for arch-1 is not",
                      str(cm.exception))

    def test_control_plain_identifier(self):
        point = {"population_size": 1,
                 "archetype_mix": {"arch-1": -1}}
        with self.assertRaises(Exception) as cm:
            mod03.build_cast(point, [], strategy_class="fixed")
        self.assertIn("mix count for arch-1 is not",
                      str(cm.exception))

    def test_control_count_rendering_exact(self):
        point = {"population_size": 1,
                 "archetype_mix": {"arch-1": -1}}
        with self.assertRaises(Exception) as cm:
            mod03.build_cast(point, [], strategy_class="fixed")
        self.assertIn("whole count: -1", str(cm.exception))


class TestR20036MixOutsideRecordsSentence(unittest.TestCase):
    def test_lying_identifier_named_on_stored_text(self):
        point = {"population_size": 1,
                 "archetype_mix": {LyingStr("arch-9", "arch-1"): 1}}
        records = [{"archetype_id": "arch-1"}]
        with self.assertRaises(Exception) as cm:
            mod03.build_cast(point, records, strategy_class="fixed")
        self.assertIn("outside the records supplied: arch-9",
                      str(cm.exception))

    def test_control_plain_identifier(self):
        point = {"population_size": 1,
                 "archetype_mix": {"arch-9": 1}}
        records = [{"archetype_id": "arch-1"}]
        with self.assertRaises(Exception) as cm:
            mod03.build_cast(point, records, strategy_class="fixed")
        self.assertIn("outside the records supplied: arch-9",
                      str(cm.exception))

    def test_control_cast_builds(self):
        point = {"population_size": 1,
                 "archetype_mix": {"arch-1": 1}}
        records = [{"archetype_id": "arch-1"}]
        cast = mod03.build_cast(point, records,
                                strategy_class="fixed")
        self.assertEqual(cast["population"], 1)
        self.assertEqual(cast["cast"][0]["archetype_id"], "arch-1")


class TestR20037RunClassSentence(unittest.TestCase):
    def test_lying_run_class_named_on_stored_text(self):
        run = {"run_class": LyingStr("bogus", "screening"),
               "seed_domain": "screening"}
        failures = mod12.run_record_validation_failures(run)
        self.assertEqual(1, len(failures))
        self.assertIn("validation): 'bogus'", failures[0])

    def test_dress_run_class_named_on_stored_text(self):
        run = {"run_class": ("bo", "gus"),
               "seed_domain": "screening"}
        failures = mod12.run_record_validation_failures(run)
        self.assertEqual(1, len(failures))
        self.assertIn("validation): 'bogus'", failures[0])

    def test_control_plain_run_class(self):
        run = {"run_class": "bogus", "seed_domain": "screening"}
        failures = mod12.run_record_validation_failures(run)
        self.assertEqual(1, len(failures))
        self.assertIn("validation): 'bogus'", failures[0])

    def test_control_stated_run_class_no_run_class_failure(self):
        run = {"run_class": "screening", "seed_domain": "screening"}
        failures = mod12.run_record_validation_failures(run)
        for failure in failures:
            self.assertNotIn("run_class stands outside", failure)


class TestR20038WinningRegimeSentence(unittest.TestCase):
    def test_lying_entry_named_on_form(self):
        entries = [(ReprLiar("0.9"), 0.1)] * 30
        with self.assertRaises(Exception) as cm:
            mod12.winning_regime(entries)
        self.assertIn("non numeric share: (ReprLiar, 0.1)",
                      str(cm.exception))

    def test_control_plain_entry(self):
        entries = [("x", 0.1)] * 30
        with self.assertRaises(Exception) as cm:
            mod12.winning_regime(entries)
        self.assertIn("non numeric share: ('x', 0.1)",
                      str(cm.exception))

    def test_control_winning_pair_returns_true(self):
        self.assertTrue(mod12.winning_regime([(0.9, 0.1)] * 30))

    def test_control_pair_sentence_uncharged_locus(self):
        with self.assertRaises(Exception) as cm:
            mod12.winning_regime([123] * 30)
        self.assertIn("is not an attacker and honest pair: 123",
                      str(cm.exception))


class TestR20039TopUpSentence(unittest.TestCase):
    def test_lying_pair_named_on_form(self):
        with self.assertRaises(Exception) as cm:
            mod12.top_up_applies(ReprLiar("0.5"), ReprLiar("30"))
        self.assertIn("not numbers: (ReprLiar, ReprLiar)",
                      str(cm.exception))

    def test_control_plain_pair(self):
        with self.assertRaises(Exception) as cm:
            mod12.top_up_applies("x", 30)
        self.assertIn("not numbers: ('x', 30)", str(cm.exception))

    def test_control_top_up_answers(self):
        self.assertTrue(mod12.top_up_applies(0.5, 30))
        self.assertFalse(mod12.top_up_applies(5.0, 30))


class TestR20040ClaimsFormSentence(unittest.TestCase):
    def test_lying_claims_named_on_form(self):
        with self.assertRaises(Exception) as cm:
            mod12.apply_family_edit(
                {}, {"claims": ReprLiar("['claim']")})
        self.assertIn("tuple form: ReprLiar", str(cm.exception))

    def test_control_plain_claims(self):
        with self.assertRaises(Exception) as cm:
            mod12.apply_family_edit({}, {"claims": "notalist"})
        self.assertIn("tuple form: 'notalist'", str(cm.exception))

    def test_control_valid_claims_edit_lands(self):
        edited = mod12.apply_family_edit({}, {"claims": ["claim A"]})
        self.assertEqual(edited["claims"], ["claim A"])


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


class ReprLieStr(str):
    """A text value storing one text whose repr reading
    answers a stated different text."""

    def __new__(cls, stored, lie):
        value = str.__new__(cls, stored)
        value._lie = lie
        return value

    def __repr__(self):
        return self._lie


class ReprRaiseStr(str):
    """A text value storing one text whose repr reading
    raises."""

    def __repr__(self):
        raise RuntimeError("repr reading raises")


def swapped_claim(first_point):
    return {
        "detection_comparison_points": [
            first_point,
            "first verdict state after resume",
        ]
    }


def valid_verdict(outcome):
    return {
        "claim_identifier": "C-1",
        "outcome": outcome,
        "standard_applied": "exact replay alone",
        "replication_statement": mod13.REPLICATION_STATEMENT,
        "replication_statement_sentences": list(
            mod13.REPLICATION_STATEMENT_SENTENCES),
    }


class TestR21016OrderSentence(unittest.TestCase):
    def test_order_sentence_lying_repr_names_stored_point(self):
        failures = mod13.resume_claim_validation_failures(
            swapped_claim(ReprLieStr("run close", "'LYING-NAME'")))
        self.assertEqual(len(failures), 1)
        self.assertIn("'run close'", failures[0])
        self.assertNotIn("LYING-NAME", failures[0])

    def test_order_sentence_repr_naming_other_point(self):
        failures = mod13.resume_claim_validation_failures(
            swapped_claim(ReprLieStr(
                "run close", "'first verdict state after resume'")))
        self.assertEqual(len(failures), 1)
        self.assertIn("'run close'", failures[0])
        self.assertNotIn(
            "first verdict state after resume", failures[0])

    def test_order_sentence_raising_repr_names_stored_point(self):
        failures = mod13.resume_claim_validation_failures(
            swapped_claim(ReprRaiseStr("run close")))
        self.assertEqual(len(failures), 1)
        self.assertIn("'run close'", failures[0])

    def test_control_plain_swapped_points_name_run_close(self):
        failures = mod13.resume_claim_validation_failures(
            swapped_claim("run close"))
        self.assertEqual(len(failures), 1)
        self.assertIn("'run close'", failures[0])

    def test_control_plain_points_in_named_order_pass(self):
        claim = {
            "detection_comparison_points": [
                "first verdict state after resume",
                "run close",
            ]
        }
        self.assertEqual(
            mod13.resume_claim_validation_failures(claim), [])

    def test_control_plain_outside_point_named(self):
        claim = {
            "detection_comparison_points": [
                "zzz",
                "run close",
            ]
        }
        failures = mod13.resume_claim_validation_failures(claim)
        self.assertEqual(len(failures), 1)
        self.assertIn("'zzz'", failures[0])


class TestR21017OutcomeSentence(unittest.TestCase):
    def test_outcome_sentence_lying_repr_names_stored_outcome(self):
        failures = mod13.publishable_on_replication_failures(
            {"claim_identifier": "C-1"},
            valid_verdict(ReprLieStr("does not rest", "'rests'")))
        self.assertEqual(len(failures), 1)
        self.assertIn("'does not rest'", failures[0])
        self.assertNotIn("stands as 'rests',", failures[0])

    def test_outcome_sentence_raising_repr_names_stored_outcome(self):
        failures = mod13.publishable_on_replication_failures(
            {"claim_identifier": "C-1"},
            valid_verdict(ReprRaiseStr("does not rest")))
        self.assertEqual(len(failures), 1)
        self.assertIn("'does not rest'", failures[0])

    def test_control_plain_outcome_does_not_rest_named(self):
        failures = mod13.publishable_on_replication_failures(
            {"claim_identifier": "C-1"},
            valid_verdict("does not rest"))
        self.assertEqual(len(failures), 1)
        self.assertIn("'does not rest'", failures[0])

    def test_control_plain_outcome_rests_passes(self):
        failures = mod13.publishable_on_replication_failures(
            {"claim_identifier": "C-1"},
            valid_verdict("rests"))
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
