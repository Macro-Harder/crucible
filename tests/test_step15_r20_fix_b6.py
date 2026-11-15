"""Pins for Round 19 rows R19-002, R19-027, R19-032, R19-042,
R19-049, R19-050, and R19-051.

MOD-12, MOD-13, and MOD-16 family, Builder 6 of fix wave 19.
Each pin states the defect its row charges in the distinguishing
case, beside the plain controls the source papers ran.
"""
import unittest

from crucible import mod03
from crucible import mod08
from crucible import mod12
from crucible import mod13
from crucible import mod16


class AlwaysEq:
    """A value in no stated form whose equality answers True
    against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 1


class RaisingEq:
    """A value in no stated form whose equality readings raise."""

    def __eq__(self, other):
        raise RuntimeError("raising equality")

    def __ne__(self, other):
        raise RuntimeError("raising inequality")

    def __hash__(self):
        return 1


class LyingStr(str):
    """A str subclass whose equality answers True against every
    value, whatever text it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(self)


class RaisingEqStr(str):
    """A str subclass whose equality readings raise, whatever
    text it stores."""

    def __eq__(self, other):
        raise RuntimeError("raising equality")

    def __ne__(self, other):
        raise RuntimeError("raising inequality")

    def __hash__(self):
        return str.__hash__(self)


class StrRaisingStr(str):
    """A str subclass whose string reading raises."""

    def __str__(self):
        raise RuntimeError("string reading raises")

    __repr__ = object.__repr__


class CollidingRaisingKey(str):
    """A str subclass key storing a stated field name as its
    text, hashing as that name, and raising on every equality
    reading once the class flag stands up. The record stands
    built while the flag stands down, in the armed key form
    the earlier waves state."""

    armed = False

    def __new__(cls, target):
        return str.__new__(cls, target)

    def __hash__(self):
        return str.__hash__(str.__str__(self))

    def __eq__(self, other):
        if CollidingRaisingKey.armed:
            raise RuntimeError("colliding equality")
        return str.__eq__(self, other)

    def __ne__(self, other):
        if CollidingRaisingKey.armed:
            raise RuntimeError("colliding inequality")
        return str.__ne__(self, other)


def _with_colliding(record, target, value):
    CollidingRaisingKey.armed = False
    handed = dict(record)
    handed[CollidingRaisingKey(target)] = value
    CollidingRaisingKey.armed = True
    return handed


class LyingFloatInBounds(float):
    """A float subclass whose greater and lesser readings both
    answer True, so any stated band appears to contain it."""

    def __gt__(self, other):
        return True

    def __lt__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return True


class LyingFloatGreater(float):
    """A float subclass whose greater reading answers True
    against every value."""

    def __gt__(self, other):
        return True

    def __ge__(self, other):
        return True


class LyingFloatLesser(float):
    """A float subclass whose lesser reading answers True
    against every value."""

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True


class LyingIntAtLeast(int):
    """An int subclass whose at least reading answers True
    against every value."""

    def __ge__(self, other):
        return True


class LyingMagnitude:
    """A value in no number form whose at least reading answers
    True against every value."""

    def __ge__(self, other):
        return True


class TestR19002FixtureRecord(unittest.TestCase):
    def test_bogus_identifier_refused(self):
        with self.assertRaises(mod16.FixtureLookupFailure):
            mod16.fixture_record(AlwaysEq())

    def test_raising_identifier_named_failure(self):
        with self.assertRaises(mod16.FixtureLookupFailure):
            mod16.fixture_record(RaisingEq())

    def test_raising_equality_str_storing_f02_delivered(self):
        record = mod16.fixture_record(RaisingEqStr("F-02"))
        self.assertEqual(str.__str__(record["fixture"]), "F-02")

    def test_lying_str_storing_absent_id_refused(self):
        with self.assertRaises(mod16.FixtureLookupFailure):
            mod16.fixture_record(LyingStr("F-99"))

    def test_plain_f02_control(self):
        record = mod16.fixture_record("F-02")
        self.assertEqual(record["fixture"], "F-02")

    def test_plain_f01_control(self):
        record = mod16.fixture_record("F-01")
        self.assertEqual(record["fixture"], "F-01")

    def test_plain_absent_control(self):
        with self.assertRaises(mod16.FixtureLookupFailure):
            mod16.fixture_record("F-99")


class TestR19027ShapeCause(unittest.TestCase):
    def _cyclic(self):
        record = {}
        record[StrRaisingStr("loopkey")] = record
        return record

    def test_seal_cyclic_str_raising_key_named_refusal(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(self._cyclic())

    def test_edit_cyclic_str_raising_key_named_refusal(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(self._cyclic())

    def test_seal_plain_record_control(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        self.assertTrue(sealed["sealed"])

    def test_edit_plain_record_control(self):
        edited = mod12.apply_family_edit(mod12.make_family_record())
        self.assertIn("family_identifier", edited)

    def test_plain_cyclic_record_named_refusal_control(self):
        record = {}
        record["loop"] = record
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)


class TestR19032ExerciseRunClass(unittest.TestCase):
    def test_bogus_object_class_refused(self):
        with self.assertRaises(ValueError):
            mod16.exercise_run_class(AlwaysEq())

    def test_lying_str_storing_bogus_class_refused(self):
        with self.assertRaises(ValueError):
            mod16.exercise_run_class(LyingStr("bogus"))

    def test_raising_equality_str_storing_confirmation_carried(self):
        result = mod16.exercise_run_class(RaisingEqStr("confirmation"))
        self.assertTrue(result["carried_unexercised_here"])
        self.assertEqual(
            str.__str__(result["run_class"]), "confirmation")

    def test_plain_confirmation_control(self):
        result = mod16.exercise_run_class("confirmation")
        self.assertTrue(result["carried_unexercised_here"])
        self.assertFalse(result["exercised_end_to_end"])

    def test_plain_headline_control(self):
        result = mod16.exercise_run_class("headline")
        self.assertTrue(result["carried_unexercised_here"])

    def test_plain_bogus_control(self):
        with self.assertRaises(ValueError):
            mod16.exercise_run_class("bogus")


class TestR19042StoredPairsReadings(unittest.TestCase):
    def tearDown(self):
        CollidingRaisingKey.armed = False

    def test_mod03_catalogue_colliding_raising_key(self):
        record = _with_colliding(
            {"parameter_rows": [], "generator_signature": "sig"},
            "archetype_id", "A-1")
        catalogue = mod03.archetype_catalogue([record])
        self.assertEqual(list(catalogue["entries"]), ["A-1"])
        self.assertEqual(
            catalogue["entries"]["A-1"]["generator_signature"], "sig")

    def test_mod08_use_naming_colliding_raising_key(self):
        artefact = _with_colliding({}, "uses_named", ["conformance"])
        self.assertTrue(mod08.validate_use_naming(artefact))

    def test_mod13_scoring_colliding_raising_key(self):
        record = _with_colliding(
            {"run_identifier": "run-1",
             "verdict_states_and_accumulator_updates": "v"},
            "scoring_day_range", "days")
        result = mod13.score_detection_outputs(
            [record], authored_by="a", knowledge="k",
            records_position="p")
        self.assertEqual(result["outputs_scored"], 1)

    def test_mod03_plain_control(self):
        catalogue = mod03.archetype_catalogue(
            [{"archetype_id": "A-1", "parameter_rows": [],
              "generator_signature": "sig"}])
        self.assertEqual(list(catalogue["entries"]), ["A-1"])

    def test_mod08_plain_control(self):
        self.assertTrue(mod08.validate_use_naming(
            {"uses_named": ["conformance"]}))

    def test_mod13_plain_control(self):
        result = mod13.score_detection_outputs(
            [{"run_identifier": "run-1", "scoring_day_range": "days",
              "verdict_states_and_accumulator_updates": "v"}],
            authored_by="a", knowledge="k", records_position="p")
        self.assertEqual(result["outputs_scored"], 1)

    def test_mod13_missing_field_control(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.score_detection_outputs(
                [{"run_identifier": "run-1",
                  "verdict_states_and_accumulator_updates": "v"}],
                authored_by="a", knowledge="k", records_position="p")


class TestR19049TopUpApplies(unittest.TestCase):
    def test_probability_storing_5_refused(self):
        self.assertFalse(mod12.top_up_applies(
            LyingFloatInBounds(5.0), 40))

    def test_count_storing_29_refused(self):
        self.assertFalse(mod12.top_up_applies(
            0.5, LyingIntAtLeast(29)))

    def test_plain_inside_control(self):
        self.assertTrue(mod12.top_up_applies(0.5, 40))

    def test_plain_count_below_control(self):
        self.assertFalse(mod12.top_up_applies(0.5, 20))

    def test_plain_probability_outside_control(self):
        self.assertFalse(mod12.top_up_applies(5.0, 40))

    def test_text_probability_named_failure_control(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.top_up_applies("high", 30)


class TestR19050WinningRegime(unittest.TestCase):
    def test_attacker_storing_01_not_winning(self):
        shares = [(LyingFloatGreater(0.1), 0.9)] * 30
        self.assertFalse(mod12.winning_regime(shares))

    def test_honest_storing_09_not_beaten(self):
        shares = [(0.5, LyingFloatLesser(0.9))] * 30
        self.assertFalse(mod12.winning_regime(shares))

    def test_plain_winning_control(self):
        self.assertTrue(mod12.winning_regime([(0.9, 0.1)] * 30))

    def test_plain_losing_control(self):
        self.assertFalse(mod12.winning_regime([(0.1, 0.9)] * 30))

    def test_short_list_control(self):
        self.assertFalse(mod12.winning_regime([(0.9, 0.1)] * 29))


class TestR19051HostileKindCountsAsRun(unittest.TestCase):
    def test_text_ran_at_not_counted(self):
        self.assertFalse(mod12.hostile_kind_counts_as_run(
            kind="k", ran_at="text", fixed_magnitude=5))

    def test_no_number_form_not_counted(self):
        self.assertFalse(mod12.hostile_kind_counts_as_run(
            kind="k", ran_at=LyingMagnitude(), fixed_magnitude=5))

    def test_boolean_ran_at_not_counted(self):
        self.assertFalse(mod12.hostile_kind_counts_as_run(
            kind="k", ran_at=True, fixed_magnitude=1))

    def test_plain_at_magnitude_control(self):
        self.assertTrue(mod12.hostile_kind_counts_as_run(
            kind="k", ran_at=10, fixed_magnitude=5))

    def test_plain_below_magnitude_control(self):
        self.assertFalse(mod12.hostile_kind_counts_as_run(
            kind="k", ran_at=3, fixed_magnitude=5))

    def test_none_control(self):
        self.assertFalse(mod12.hostile_kind_counts_as_run(
            kind="k", ran_at=None, fixed_magnitude=5))


if __name__ == "__main__":
    unittest.main()
