import unittest

from crucible import mod14


OLD_SENTENCE = (
    "Validation reads checkpoint manifests beside the run record "
    "to compare seeds, settings, and rule versions.")
NEW_SENTENCE = "Validation reads the action record alone."


class LyingBytes(bytes):
    def __str__(self):
        return "figure"


class TestStoredTextBytesLimbs(unittest.TestCase):
    def test_bytes_stored_text_decoded(self):
        self.assertEqual(mod14._stored_text(b"money"), "money")

    def test_bytes_subclass_read_on_stored_bytes(self):
        self.assertEqual(mod14._stored_text(LyingBytes(b"money")), "money")

    def test_undecodable_bytes_dropped(self):
        self.assertEqual(mod14._stored_text(b"mon\xffey"), "money")

    def test_bytearray_stored_text_decoded(self):
        self.assertEqual(mod14._stored_text(bytearray(b"money")), "money")

    def test_memoryview_stored_text_decoded(self):
        self.assertEqual(
            mod14._stored_text(memoryview(b"anchor_set")), "anchor_set")

    def test_bytes_key_form(self):
        self.assertEqual(mod14._pilot_key_form(b"money"), "money")
        self.assertEqual(
            mod14._pilot_key_form(memoryview(b"anchor_set")), "anchorset")

    def test_screen_bytes_key_raises(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14._screen_pilot_key(b"money")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14._screen_pilot_key(b"anchor_set")

    def test_screen_memoryview_key_raises(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14._screen_pilot_key(memoryview(b"money"))

    def test_pilot_run_bytes_dict_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {b"money": 1})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {b"anchor_set": 1})

    def test_pilot_run_nested_bytes_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"x": {b"money": 1}})

    def test_pilot_run_memoryview_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {memoryview(b"money"): 1})


class TestPilotContainerLimbs(unittest.TestCase):
    def test_single_part_tuple_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {("money",): 1})

    def test_second_position_tuple_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {("x", "money"): 1})

    def test_split_tuple_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {("mon", "ey"): 1})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {("anchor", "_set"): 1})

    def test_bytes_part_in_tuple_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {(b"money",): 1})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {("mo", b"ney"): 1})

    def test_nested_container_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {(("mon", "ey"),): 1})

    def test_single_item_list_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", ["money"])

    def test_second_item_list_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", ["x", "money"])

    def test_second_item_tuple_artefact_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", ("x", "money"))

    def test_bytes_item_list_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", ["x", b"money"])

    def test_bytes_item_set_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {b"money"})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"figure": {b"money"}})

    def test_memoryview_item_set_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {memoryview(b"money")})

    def test_split_part_set_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {("mon", "ey")})


class TestRunbookSentence(unittest.TestCase):
    def test_no_act_performs_the_stated_comparison(self):
        action = {
            "kind": "edit", "target": "checkpoint set",
            "path": "deletion rule",
            "manifest_seed": 1, "run_record_seed": 2,
            "manifest_rule_version": 1, "run_record_rule_version": 2,
        }
        verdict = mod14.validate_operator_action_with_reason(action)
        self.assertTrue(verdict["allowed"], verdict)

    def test_runbook_step_seven_sentence_corrected(self):
        step = mod14.operator_runbook()["steps"][6]
        self.assertNotIn(OLD_SENTENCE, step)
        self.assertIn(NEW_SENTENCE, step)

    def test_docstring_sentence_corrected(self):
        doc = " ".join(mod14.validate_operator_action.__doc__.split())
        self.assertNotIn(OLD_SENTENCE, doc)
        self.assertIn(NEW_SENTENCE, doc)


class TestStandingControls(unittest.TestCase):
    def test_plain_barred_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"money": 1})

    def test_plain_value_under_harmless_key_passes(self):
        output = mod14.pilot_run("timing", {"note": "money"})
        self.assertEqual(output["confinement_label"], "pilot confined")

    def test_harmless_artefact_passes(self):
        output = mod14.pilot_run("timing", {"figure": 1})
        self.assertEqual(output["figure"], 1)
        output = mod14.pilot_run("timing", ["figure", 1])
        self.assertEqual(output["confinement_label"], "pilot confined")

    def test_harmless_container_key_passes(self):
        output = mod14.pilot_run("timing", {("figure", "x"): 1})
        self.assertEqual(output["confinement_label"], "pilot confined")

    def test_pilot_stamp_forms_stand(self):
        output = mod14.pilot_run("timing", {"figure": 1})
        self.assertEqual(output["confinement_label"], "pilot confined")
        self.assertEqual(
            output["form"],
            "pilot artefact, stored apart from sweep results")

    def test_resolver_five_drop_words_resolve_at_mod14(self):
        for word in ("am", "ga", "gm", "gr", "oa", "og", "om", "or",
                     "pa", "pg", "pm", "ra", "rg", "rm", "rr"):
            self.assertEqual(mod14._resolve_actor_word(word), "program", word)

    def test_resolver_spaced_actor_normalises_at_mod14(self):
        self.assertEqual(mod14._normalise_actor("p m"), "program")


if __name__ == "__main__":
    unittest.main()
