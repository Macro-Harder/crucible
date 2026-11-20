"""Step 17 fix wave 8, Slice 2 defect tests (FW8-01, T17R7-02).

The extra argument family at the six charged doors of mod12 and
mod13: at each door, an extra argument handing, in positional
form and in keyword form, stands refused in the named form of
its module, stating the door, the ground, and the next step, and
no bare interpreter TypeError escapes. The family doors of the
same sentinel signature in mod13, resume_check and
publishable_on_replication, stand read at the cure test writing
and worked in the same form. Doors already standing in named
form at the charged handings (the start door keyword carriage,
the score_detection_outputs keyword form, and replay_check in
both forms) stand pinned as standing tests. Outcomes stand
judged by stored value in code, never by a repr (T17R3-23).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod12, mod13


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "positional argument but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, exc_type, door_words, call,
                        ground_word="beyond"):
    """The call refuses in named form: the module named type,
    never a bare TypeError, the message carrying the door, the
    ground word, a next step, and no bare interpreter phrase."""
    with case.assertRaises(exc_type) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    for word in door_words:
        case.assertIn(word, message)
    case.assertIn(ground_word, message)
    case.assertIn("next step", message)
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


def check_start_refusal(case, result, action):
    """A start door refusal stands in the named dict form of the
    module: the door action, a ground in words carrying the
    beyond ground, a next step, and the gated standings unmoved,
    run_started False and seed_drawn False."""
    case.assertIsInstance(result, dict)
    case.assertEqual(result["action"], action)
    case.assertIn("beyond", result["ground_in_words"])
    case.assertIn("next_step", result)
    case.assertTrue(result["next_step"])
    case.assertIs(result["run_started"], False)
    case.assertIs(result["seed_drawn"], False)
    return result


class TestFW801Mod12StartDoors(unittest.TestCase):

    def test_defect_start_run_extra_positional(self):
        result = mod12.start_run("screening", "fam-1", 1)
        check_start_refusal(self, result, "start run")

    def test_defect_start_sweep_extra_positional(self):
        result = mod12.start_sweep("fam-1", 1)
        check_start_refusal(self, result, "start sweep")

    def test_standing_start_run_extra_keyword_named(self):
        result = mod12.start_run("screening", "fam-1", extra_kw=1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["unexpected_keyword_handings"],
                         ["extra_kw"])
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)
        self.assertIn("ground_in_words", result)
        self.assertIn("next_step", result)

    def test_standing_start_sweep_extra_keyword_named(self):
        result = mod12.start_sweep("fam-1", extra_kw=1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["unexpected_keyword_handings"],
                         ["extra_kw"])
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)
        self.assertIn("ground_in_words", result)
        self.assertIn("next_step", result)

    def test_control_start_run_gated(self):
        result = mod12.start_run("screening", "fam-1")
        self.assertIsInstance(result, dict)
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)

    def test_control_start_sweep_gated(self):
        result = mod12.start_sweep("fam-1")
        self.assertIsInstance(result, dict)
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)


class TestFW801Mod12RecordDoors(unittest.TestCase):

    def test_defect_seal_family_record_extra_positional(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, ("family record",),
            lambda: mod12.seal_family_record(record, 1))

    def test_defect_seal_family_record_extra_keyword(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, ("family record",),
            lambda: mod12.seal_family_record(record, extra_kw=1))

    def test_defect_validate_family_record_extra_positional(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, ("family record",),
            lambda: mod12.validate_family_record(record, 1))

    def test_defect_validate_family_record_extra_keyword(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, ("family record",),
            lambda: mod12.validate_family_record(record, extra_kw=1))

    def test_control_seal_family_record_served(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        self.assertIsInstance(sealed, dict)
        self.assertIs(sealed["sealed"], True)

    def test_control_validate_family_record_plain(self):
        self.assertIs(mod12.validate_family_record({}), False)


class TestFW801Mod13ChargedDoors(unittest.TestCase):

    def test_defect_score_detection_outputs_extra_positional(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("score detection outputs",),
            lambda: mod13.score_detection_outputs([], "a", "k", "r", 1))

    def test_defect_validate_replay_claim_extra_positional(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("validate replay claim",),
            lambda: mod13.validate_replay_claim({}, 1))

    def test_defect_validate_replay_claim_extra_keyword(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("validate replay claim",),
            lambda: mod13.validate_replay_claim({}, extra_kw=1))

    def test_standing_score_detection_outputs_extra_keyword(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("score detection outputs",),
            lambda: mod13.score_detection_outputs([], extra_kw=1))

    def test_control_score_detection_outputs_served(self):
        result = mod13.score_detection_outputs(
            [], authored_by="a", knowledge="k", records_position="r")
        self.assertEqual(result["outputs_scored"], 0)

    def test_control_validate_replay_claim_served(self):
        self.assertIs(mod13.validate_replay_claim({}), True)


class TestFW801Mod13FamilyDoors(unittest.TestCase):

    def test_defect_resume_check_extra_positional(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure, ("resume check",),
            lambda: mod13.resume_check({}, {}, 1))

    def test_defect_resume_check_extra_keyword(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure, ("resume check",),
            lambda: mod13.resume_check({}, {}, extra_kw=1))

    def test_defect_publishable_on_replication_extra_positional(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("publishable on replication",),
            lambda: mod13.publishable_on_replication({}, {}, 1))

    def test_defect_publishable_on_replication_extra_keyword(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("publishable on replication",),
            lambda: mod13.publishable_on_replication({}, {},
                                                     extra_kw=1))

    def test_standing_replay_check_extra_positional_named(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure, ("replay check",),
            lambda: mod13.replay_check({}, {}, 1),
            ground_word="beyond")

    def test_standing_replay_check_extra_keyword_named(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure, ("replay check",),
            lambda: mod13.replay_check({}, {}, extra_kw=1),
            ground_word="beyond")

    def test_control_resume_check_served(self):
        result = mod13.resume_check({}, {})
        self.assertIsInstance(result, dict)
        self.assertIn("equal_in_scope", result)

    def test_control_publishable_on_replication_plain(self):
        self.assertIs(mod13.publishable_on_replication({}, {}), False)


if __name__ == "__main__":
    unittest.main()
