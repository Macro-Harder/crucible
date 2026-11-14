"""Step 15 rerun fix wave 9 pins, Builder 1.

Pins for rows R9-001, R9-002, R9-003, R9-004 (MOD-14 limb),
R9-005, R9-011 (MOD-14 _stated_text limb), R9-012 and
R9-013 (MOD-14 limb), all at crucible/mod14.py.

The resolver pins cover the anywhere composition reading
(one transposed pair at any positions beside up to three
replacements, resolving only past a change total of three
with no transposed pair among the remaining positions) at
the actor and target readings, the three pairs composition
at nonadjacent and mixed patterns at the target reading,
and the fall through of resolver only dresses to the mixed
added limb. The condition pins cover handed entries read
by their stored characters, a handed container read
through the base iteration reading, and blank entries in
bytes, bytearray and memoryview forms.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14


class IteratingStr(str):
    """A string storing one text and iterating as another."""

    def __new__(cls, stored, iterated):
        value = str.__new__(cls, stored)
        value._iterated = iterated
        return value

    def __iter__(self):
        return iter(self._iterated)


class IteratingList(list):
    """A list storing entries and iterating as others."""

    def __new__(cls, stored, iterated):
        value = list.__new__(cls)
        value._iterated = iterated
        return value

    def __init__(self, stored, iterated):
        list.__init__(self, stored)

    def __iter__(self):
        return iter(self._iterated)


class B1Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def core_record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def shell_promote(self, actor, fired=None):
        return mod14.flag_evaluation(
            self.core_record(),
            inputs={"flag_conditions_fired": fired or ["condition a"]},
            outcome="promote", tier="Tier 3", actor=actor)


class TestR9001ActorAnywhereComposition(B1Base):
    FORMS = ["qgqrqam", "qraqroq", "qqrqoam", "paqqqrm",
             "pqqmqag", "paoxqrz"]

    def test_forms_resolve_program_at_mod14(self):
        for form in self.FORMS:
            with self.subTest(form=form):
                self.assertEqual(
                    mod14._resolve_actor_word(form), "program")
                self.assertEqual(
                    mod14._normalise_actor(form), "program")

    def test_forms_agree_with_mod10(self):
        for form in self.FORMS:
            with self.subTest(form=form):
                self.assertEqual(
                    mod10._resolve_actor_word(form), "program")
                self.assertEqual(
                    mod14._resolve_actor_word(form),
                    mod10._resolve_actor_word(form))

    def test_forms_promote_at_shell_act(self):
        for form in self.FORMS:
            with self.subTest(form=form):
                self.assertEqual(
                    self.shell_promote(form)["retention_tier"],
                    "Tier 3")


class TestR9002TargetAnywhereComposition(B1Base):
    FORMS = {
        "ezqxwrito": "overwrite",
        "ezqxrseds": "supersede",
        "nzqxtiod": "deletion",
        "tzqxeci": "inspect",
        "dzqoxr": "record",
        "dzqxes": "sealed",
        "dzqxec": "closed",
    }

    def test_forms_resolve_to_own_word(self):
        for form, word in self.FORMS.items():
            with self.subTest(form=form):
                self.assertEqual(mod14._resolve_word(form), word)

    def test_delete_on_dressed_record_target_refused(self):
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "closed run dzqoxr",
             "path": "other rule"}))

    def test_dressed_overwrite_act_refused_on_closed_record(self):
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "ezqxwrito", "target": "closed run record",
             "path": "flag rule"}))


class TestR9003FallThroughBarsLawfulActs(B1Base):
    def test_fetch_dress_resolves_fetch(self):
        self.assertEqual(mod14._resolve_word("hzqxf"), "fetch")

    def test_fetch_dress_allowed_on_checkpoint_set(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "hzqxf", "target": "checkpoint set",
             "path": "other rule"}))

    def test_inspect_dress_allowed_on_sealed_record(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "tzqxeci", "target": "sealed family record",
             "path": "other rule"}))

    def test_destroy_total_three_dress_stands_as_itself(self):
        self.assertEqual(mod14._resolve_word("yoztred"), "yoztred")
        self.assertEqual(
            mod14._normalise_name("yoztred family record"),
            "yoztred family record")

    def test_destroy_dress_phrase_edit_and_delete_allowed(self):
        for kind in ("edit", "delete"):
            with self.subTest(kind=kind):
                self.assertTrue(mod14.validate_operator_action(
                    {"kind": kind,
                     "target": "yoztred family record",
                     "path": "other rule"}))

    def test_replace_total_three_dress_stands_as_itself(self):
        self.assertEqual(mod14._resolve_word("erpzaec"), "erpzaec")


class TestR9004ActorFallThrough(B1Base):
    def test_three_pairs_one_replacement_resolve_program(self):
        for form in ("agmrzpo", "rpgoarq", "marqorp"):
            with self.subTest(form=form):
                self.assertEqual(
                    mod14._resolve_actor_word(form), "program")
                self.assertEqual(
                    mod14._normalise_actor(form), "program")

    def test_resolver_only_dresses_stand_as_themselves(self):
        for form in ("mzagrop", "mrazrop", "mragzop"):
            with self.subTest(form=form):
                self.assertEqual(
                    mod14._resolve_actor_word(form), form)
                self.assertEqual(mod14._normalise_actor(form), form)


class TestR9005TargetThreePairsComposition(B1Base):
    FORMS = [
        "hccepkqint", "hccepkoqnt", "hccepkoiqt", "hccepkoinq",
        "hccepkqqnt", "hccepkoqqt", "hccepkqinq", "hccepkoiqq",
        "tniqkpoehc", "tnickpqehc", "hcxqzoptni", "txiqozkenc",
        "conctzhiek", "hcxckoptni",
    ]

    def test_forms_resolve_checkpoint(self):
        for form in self.FORMS:
            with self.subTest(form=form):
                self.assertEqual(
                    mod14._resolve_word(form), "checkpoint")

    def test_delete_on_dressed_checkpoint_set_refused(self):
        for form in ("hccepkqint", "txiqozkenc", "conctzhiek"):
            with self.subTest(form=form):
                self.assertFalse(mod14.validate_operator_action(
                    {"kind": "delete", "target": form + " set",
                     "path": "other rule"}))

    def test_adjacent_three_pairs_three_replacements_control(self):
        for form in ("hccepkxqzt", "hccepkoxqz"):
            with self.subTest(form=form):
                self.assertEqual(
                    mod14._resolve_word(form), "checkpoint")


class TestR9011StatedTextStoredCharacters(B1Base):
    def test_stored_blank_iterating_real_states_nothing(self):
        entry = IteratingStr("​", "real")
        self.assertEqual(mod14._stated_text(entry), "")
        self.assertFalse(mod14._has_stated_condition([entry]))

    def test_stored_real_iterating_blank_states_condition(self):
        entry = IteratingStr("real", "​")
        self.assertEqual(mod14._stated_text(entry), "real")
        self.assertTrue(mod14._has_stated_condition([entry]))

    def test_shell_gate_refuses_stored_blank_entry(self):
        entry = IteratingStr("​", "real")
        with self.assertRaises(mod14.NamedShellFailure):
            self.shell_promote("program", fired=[entry])


class TestR9012ContainerBaseIteration(B1Base):
    def test_list_subclass_read_by_stored_entries(self):
        fired = IteratingList(["​"], ["real"])
        self.assertFalse(mod14._has_stated_condition(fired))

    def test_list_subclass_stored_real_states_condition(self):
        fired = IteratingList(["real"], ["​"])
        self.assertTrue(mod14._has_stated_condition(fired))


class TestR9013BytesBlankEntries(B1Base):
    BLANK = [b"", b" ", "​".encode("utf-8"),
             memoryview(b" "), bytearray(b"\x00")]

    def test_blank_bytes_forms_state_no_condition(self):
        for entry in self.BLANK:
            with self.subTest(entry=repr(entry)):
                self.assertFalse(
                    mod14._has_stated_condition([entry]))

    def test_real_bytes_form_states_condition(self):
        self.assertTrue(mod14._has_stated_condition([b"real"]))

    def test_shell_gate_refuses_blank_bytes_entry(self):
        with self.assertRaises(mod14.NamedShellFailure):
            self.shell_promote("program", fired=[b""])


class TestStandingControls(B1Base):
    def test_b12_resolver_only_forms_stand_as_themselves(self):
        for form in ("eprosx", "eprxno", "epsrox", "xresno"):
            with self.subTest(form=form):
                self.assertEqual(
                    mod14._resolve_actor_word(form), form)

    def test_b12_anywhere_controls_still_resolve(self):
        self.assertEqual(mod14._resolve_actor_word("nqzjop"), "person")
        self.assertEqual(mod14._resolve_actor_word("eprxxx"), "person")
        self.assertEqual(
            mod14._resolve_word("tqzjkpoinc"), "checkpoint")
        self.assertEqual(
            mod14._resolve_word("chpqzejint"), "checkpoint")
        self.assertEqual(
            mod14._resolve_word("tzqxkpoinc"), "checkpoint")

    def test_two_pairs_upper_form_control(self):
        self.assertEqual(
            mod14._resolve_word("tnzqxpoihc"), "checkpoint")

    def test_three_pairs_alone_controls(self):
        self.assertEqual(mod14._resolve_actor_word("nosrep"), "person")
        self.assertEqual(mod14._resolve_word("eteled"), "delete")

    def test_two_pairs_one_replacement_target_stands_as_itself(self):
        self.assertEqual(
            mod14._resolve_word("tnzqxjoihc"), "tnzqxjoihc")

    def test_plain_condition_controls(self):
        self.assertFalse(mod14._has_stated_condition([""]))
        self.assertFalse(mod14._has_stated_condition(["​"]))
        self.assertTrue(mod14._has_stated_condition(["real"]))
        self.assertFalse(mod14._has_stated_condition([None]))


if __name__ == "__main__":
    unittest.main()
