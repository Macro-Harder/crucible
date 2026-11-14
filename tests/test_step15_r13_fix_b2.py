"""Step 15 second run, fix wave 12 pins, Builder 2.

Pins for rows R12-009, R12-044, R12-074, and R12-075 of the
Round 12 register, under settlement S-7 for row R12-009.

Row R12-009: theta reads th and phi reads ph at both MOD-10
and MOD-14, the MOD-14 readings governing, so one actor dress
reads as one party at both flag acts, proved on the composed
dresses of Red 4 Finding 1 of the Round 12 papers. The agreed
party for each dress is the party the governing MOD-14 reading
gives it, as the pins below state dress by dress.

Row R12-044: the MOD-14 flag evaluation promotion limb reads
the fired conditions through the stored record and the stored
inputs, never through a get reading either handed value
supplies, proved on the acts of Yellow 4 Finding 2.

Row R12-074: the MOD-14 weekly headline count reads the week
and the headline unit identifiers through the stored record,
proved on the acts of Yellow 4 Finding 4.

Row R12-075: the MOD-14 outside call check reads the call log,
its call entries, and the manifest through their stored
contents, proved on the acts of Yellow 4 Finding 5.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14

THETA = "\u03b8"
PHI = "\u03c6"

PERSON_DRESSES = (
    "p" + THETA + "ersn",
    "pr" + THETA + "son",
    PHI + "persn",
    "pe" + PHI + "rsn",
)
PROGRAM_DRESSES = (
    "progra" + THETA,
    "pro" + THETA + "ram",
    "pr" + PHI + "gram",
    "p" + PHI + "ogram",
)


class LyingDict(dict):
    """A dict storing one set of values and reporting another
    set through its own get reading, for the keys named in the
    reported mapping. Every other key reads as stored."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = dict(reported)

    def get(self, key, default=None):
        if key in self._reported:
            return self._reported[key]
        return dict.get(self, key, default)


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def core_record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def mod10_promote(self, actor):
        return mod10.apply_flag_evaluation(
            self.core_record(),
            outcome="promote", tier="Tier 2", actor=actor,
            inputs={"flag_conditions_fired": ["condition a"]})

    def mod14_promote(self, actor):
        return mod14.flag_evaluation(
            self.core_record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 2", actor=actor)


class TestR12009ThetaAndPhiReadings(B2Base):
    def test_theta_and_phi_read_th_and_ph_at_both_maps(self):
        self.assertEqual(mod14._LETTER_MAP[THETA], "th")
        self.assertEqual(mod14._LETTER_MAP[PHI], "ph")
        self.assertEqual(
            mod10._canonical_text(THETA, mod10._TRANSLITERATION_MAP),
            "th")
        self.assertEqual(
            mod10._canonical_text(PHI, mod10._TRANSLITERATION_MAP),
            "ph")
        self.assertEqual(mod14._canonicalise_text(THETA), "th")
        self.assertEqual(mod14._canonicalise_text(PHI), "ph")

    def test_red_person_dresses_read_as_the_governing_party_at_both(self):
        # Settlement S-7 makes the MOD-14 readings govern, so the
        # dresses Red 4 names in the person direction, which read
        # as program at MOD-14, read as program at both modules
        # and stand effected at both flag acts under that name.
        for dress in PERSON_DRESSES + (PERSON_DRESSES[0].upper(),):
            with self.subTest(dress=dress):
                self.assertEqual(mod10._normalised_actor(dress), "program")
                self.assertEqual(mod14._normalise_actor(dress), "program")

    def test_red_person_dresses_effected_at_both_flag_acts(self):
        for dress in PERSON_DRESSES:
            with self.subTest(dress=dress):
                for act in (self.mod10_promote, self.mod14_promote):
                    result = act(dress)
                    self.assertEqual(result["retention_tier"], "Tier 2")
                    self.assertEqual(
                        result["flag_evaluation"]["actor"], "program")

    def test_red_program_dresses_read_as_the_governing_party_at_both(self):
        # The dresses Red 4 names in the program direction read
        # as person at MOD-14 under the governing readings, so
        # they read as person at both modules and stand barred
        # at both flag acts.
        for dress in PROGRAM_DRESSES:
            with self.subTest(dress=dress):
                self.assertEqual(mod10._normalised_actor(dress), "person")
                self.assertEqual(mod14._normalise_actor(dress), "person")

    def test_red_program_dresses_barred_at_both_flag_acts(self):
        for dress in PROGRAM_DRESSES:
            with self.subTest(dress=dress):
                with self.assertRaises(ValueError):
                    self.mod10_promote(dress)
                with self.assertRaises(ValueError):
                    self.mod14_promote(dress)

    def test_plain_and_pure_greek_controls_stand(self):
        self.assertEqual(mod10._normalised_actor("person"), "person")
        self.assertEqual(mod14._normalise_actor("person"), "person")
        with self.assertRaises(ValueError):
            self.mod10_promote("person")
        with self.assertRaises(ValueError):
            self.mod14_promote("person")
        for act in (self.mod10_promote, self.mod14_promote):
            result = act("program")
            self.assertEqual(result["retention_tier"], "Tier 2")

    def test_other_non_text_actor_forms_stand_as_themselves(self):
        for form in ({"actor": "person"}, 42):
            with self.subTest(form=form):
                self.assertEqual(mod10._normalised_actor(form), form)
                self.assertEqual(mod14._normalise_actor(form), form)


class TestR12044FlagEvaluationFiredConditions(B2Base):
    def promote(self, summary_record, inputs):
        return mod14.flag_evaluation(
            summary_record, inputs=inputs, outcome="promote",
            tier="Tier 3", actor="program")

    def test_record_reporting_fired_it_does_not_store_is_refused(self):
        record = LyingDict(
            {"retention_tier": "Tier 1"},
            {"flag_conditions_fired": ["promote"]})
        with self.assertRaises(mod14.NamedShellFailure):
            self.promote(record, {})

    def test_record_storing_fired_it_reports_empty_promotes(self):
        record = LyingDict(
            {"retention_tier": "Tier 1",
             "flag_conditions_fired": ["promote"]},
            {"flag_conditions_fired": []})
        result = self.promote(record, {})
        self.assertEqual(result["retention_tier"], "Tier 3")

    def test_inputs_reporting_fired_they_do_not_store_is_refused(self):
        record = {"retention_tier": "Tier 1"}
        inputs = LyingDict({}, {"flag_conditions_fired": ["promote"]})
        with self.assertRaises(mod14.NamedShellFailure):
            self.promote(record, inputs)

    def test_inputs_storing_fired_they_report_empty_promotes(self):
        record = {"retention_tier": "Tier 1"}
        inputs = LyingDict(
            {"flag_conditions_fired": ["promote"]},
            {"flag_conditions_fired": []})
        result = self.promote(record, inputs)
        self.assertEqual(result["retention_tier"], "Tier 3")

    def test_plain_controls_stand_both_ways(self):
        with self.assertRaises(mod14.NamedShellFailure):
            self.promote({"retention_tier": "Tier 1"}, {})
        result = self.promote(
            {"retention_tier": "Tier 1",
             "flag_conditions_fired": ["promote"]}, {})
        self.assertEqual(result["retention_tier"], "Tier 3")


class TestR12074WeeklyHeadlineCount(unittest.TestCase):
    def test_record_of_another_week_reporting_this_week_counts_zero(self):
        record = LyingDict(
            {"week": "2026-W2",
             "headline_unit_identifiers": ["a", "b", "c"]},
            {"week": "2026-W1"})
        self.assertEqual(mod14.weekly_headline_count([record], "2026-W1"), 0)
        self.assertEqual(mod14.weekly_headline_count([record], "2026-W2"), 3)

    def test_record_of_the_week_reporting_another_week_counts(self):
        record = LyingDict(
            {"week": "2026-W1", "headline_unit_identifiers": ["x"]},
            {"week": "2026-W9"})
        self.assertEqual(mod14.weekly_headline_count([record], "2026-W1"), 1)

    def test_identifiers_read_as_stored_not_as_reported(self):
        record = LyingDict(
            {"week": "2026-W1", "headline_unit_identifiers": ["real"]},
            {"headline_unit_identifiers": ["ghost-1", "ghost-2"]})
        self.assertEqual(mod14.weekly_headline_count([record], "2026-W1"), 1)

    def test_plain_controls_stand(self):
        records = [
            {"week": "2026-W1", "headline_unit_identifiers": ["a", "b"]},
            {"week": "2026-W1", "headline_unit_identifiers": ["b", "c"]},
            {"week": "2026-W2", "headline_unit_identifiers": ["z"]},
            {"week": "2026-W1", "headline_unit_identifiers": "solo"},
        ]
        self.assertEqual(mod14.weekly_headline_count(records, "2026-W1"), 4)
        self.assertEqual(mod14.weekly_headline_count(records, "2026-W2"), 1)


class TestR12075OutsideCallCheck(unittest.TestCase):
    def test_log_reporting_no_calls_it_stores_one_outside(self):
        log = LyingDict(
            {"calls": [{"outside_call": True}]},
            {"calls": [], "entries": []})
        result = mod14.outside_call_check({"entries": []}, log)
        self.assertEqual(result["outcome"], "outside calls present")

    def test_log_stored_under_entries_reporting_none(self):
        log = LyingDict(
            {"entries": [{"outside_call": True}]},
            {"calls": [], "entries": []})
        result = mod14.outside_call_check({"entries": []}, log)
        self.assertEqual(result["outcome"], "outside calls present")

    def test_call_entry_reporting_no_outside_call_it_stores_one(self):
        entry = LyingDict(
            {"outside_call": True}, {"outside_call": False})
        result = mod14.outside_call_check(
            {"entries": []}, {"calls": [entry]})
        self.assertEqual(result["outcome"], "outside calls present")

    def test_manifest_entries_read_as_stored_both_ways(self):
        manifest = LyingDict({"entries": ["a", "b"]}, {"entries": []})
        result = mod14.outside_call_check(manifest, {"calls": []})
        self.assertEqual(result["manifest_entries"], 2)
        empty = LyingDict({"entries": []}, {"entries": ["a", "b"]})
        result = mod14.outside_call_check(empty, {"calls": []})
        self.assertEqual(result["manifest_entries"], 0)

    def test_plain_controls_stand(self):
        result = mod14.outside_call_check(
            {"entries": ["a"]}, {"calls": [{"outside_call": False}]})
        self.assertEqual(result["outcome"], "no outside calls read")
        self.assertEqual(result["manifest_entries"], 1)
        result = mod14.outside_call_check(
            {"entries": []}, {"entries": [{"outside_call": True}]})
        self.assertEqual(result["outcome"], "outside calls present")


if __name__ == "__main__":
    unittest.main()
