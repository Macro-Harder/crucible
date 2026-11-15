"""Fix wave 15, Builder 1 pins: rows R15-001 to R15-010.

Each test pins a defect the Round 15 register states for the
dict node, segmentation, and enumeration family, on the proving
acts the source papers used (Red 1 Findings 1 to 8 and Blue 1
Findings 1 and 2). Time pins state the bounds the settlements
state: 4 seconds on the MOD-06 seven part payload acts under
S-12, and 4 seconds on the actor resolver acts under the S-10
candidate discipline, the figure Blue 1 records the cost
passing at 24 letters.
"""

import time
import unittest

from crucible import mod01, mod03, mod04, mod05, mod06, mod10, mod12, mod14


class TestR15001Mod10MoneyNode(unittest.TestCase):
    """R15-001: the MOD-10 Recorder money walk never judges the
    dict node, so a split marker and a split pair stand retained
    at RecorderStore.retain_run_record."""

    def test_split_marker_forms_carry(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"real_mo": 5, "ney": 5}))
        self.assertTrue(mod10._carries_real_money_field(
            {"real_mo": 5, "": 5, "ney": 5}))
        self.assertTrue(mod10._carries_real_money_field(
            {"REAL_MO": 5, "NEY": 5}))

    def test_split_pair_forms_carry(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"amou": 5, "nt": 5, "curr": 5, "ency": 5}))
        self.assertTrue(mod10._carries_real_money_field(
            {"amou": 5, "nt": 5, "currency": "x"}))
        self.assertTrue(mod10._carries_real_money_field(
            {"amount": 5, "curr": 5, "ency": 5}))

    def test_nested_positions_carry(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"wrap": {"real_mo": 5, "ney": 5}}))
        self.assertTrue(mod10._carries_real_money_field(
            {"wrap": [{"real_mo": 5, "ney": 5}]}))
        self.assertTrue(mod10._carries_real_money_field(
            {"wrap": ({"amou": 5, "nt": 5, "curr": 5, "ency": 5},)}))

    def test_gate_refuses_split_forms(self):
        store = mod10.RecorderStore()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "r2", "payload": {"real_mo": 5, "ney": 5}})
        store = mod10.RecorderStore()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "r3", "payload": {
                    "amou": 5, "nt": 5, "curr": 5, "ency": 5}})

    def test_controls_hold(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"real_money": 5}))
        self.assertTrue(mod10._carries_real_money_field(
            {"amount": 5, "currency": "x"}))
        self.assertFalse(mod10._carries_real_money_field(
            {"amou": 5, "nt": 5}))
        self.assertFalse(mod10._carries_real_money_field(
            {"clean": 5}))
        self.assertTrue(mod10._carries_real_money_field(
            {("real_mo", "ney"): 5}))
        store = mod10.RecorderStore()
        store.retain_run_record({"run_id": "r4", "payload": {"clean": 5}})


class TestR15002Mod12MoneyNode(unittest.TestCase):
    """R15-002: the MOD-12 barred money walk never judges the
    dict node, so the split marker and split pair validate at
    validate_run_record and draw no failure at its companion."""

    def test_split_forms_carry(self):
        self.assertTrue(mod12._carries_barred_money_value(
            {"real_mo": 5, "ney": 5}))
        self.assertTrue(mod12._carries_barred_money_value(
            {"REAL_MO": 5, "NEY": 5}))
        self.assertTrue(mod12._carries_barred_money_value(
            {"real_mo": 5, "": 5, "ney": 5}))
        self.assertTrue(mod12._carries_barred_money_value(
            {"amou": 5, "nt": 5, "curr": 5, "ency": 5}))
        self.assertTrue(mod12._carries_barred_money_value(
            {"amou": 5, "nt": 5, "currency": "x"}))
        self.assertTrue(mod12._carries_barred_money_value(
            {"w": [{"real_mo": 5, "ney": 5}]}))

    def test_gate_and_companion_on_split_forms(self):
        base = {"run_class": "screening", "seed_domain": "screening"}
        split_marker = dict(base)
        split_marker["payload"] = {"real_mo": 5, "ney": 5}
        self.assertFalse(mod12.validate_run_record(split_marker))
        self.assertNotEqual(
            mod12.run_record_validation_failures(split_marker), [])
        split_pair = dict(base)
        split_pair["payload"] = {"amou": 5, "nt": 5, "curr": 5, "ency": 5}
        self.assertFalse(mod12.validate_run_record(split_pair))

    def test_controls_hold(self):
        self.assertTrue(mod12._carries_barred_money_value(
            {"real_money": 5}))
        self.assertTrue(mod12._carries_barred_money_value(
            {"amount": 5, "currency": "x"}))
        self.assertTrue(mod12._carries_barred_money_value(
            {("real_mo", "ney"): 5}))
        self.assertFalse(mod12._carries_barred_money_value(
            {"clean": 5}))
        base = {"run_class": "screening", "seed_domain": "screening"}
        self.assertTrue(mod12.validate_run_record(base))


class TestR15003Mod05AdjudicateNode(unittest.TestCase):
    """R15-003: adjudicate judges its case through
    _panel_barred_keys, which never judges the dict node, so a
    split ground truth name stands adjudicated and delivered."""

    def test_split_node_named(self):
        self.assertEqual(
            mod05._panel_barred_keys({"ground_": 1, "truth": 1}),
            ["ground_truth"])

    def test_gate_refuses_split_case(self):
        with self.assertRaises(ValueError):
            mod05.adjudicate(
                {"case_identifier": "c1", "ground_": 1, "truth": 1},
                accuracy_value=0.5, assumption_set="a", row="r",
                outcome="slashable", error_direction="x")

    def test_controls_hold(self):
        self.assertEqual(
            mod05._panel_barred_keys({"ground_truth": 1}),
            ["ground_truth"])
        self.assertEqual(mod05._panel_barred_keys({"clean": 1}), [])
        self.assertFalse(
            mod05.validate_panel_inputs({"ground_": 1, "truth": 1}))


class TestR15004Mod10ViewNode(unittest.TestCase):
    """R15-004: run_view_leak_check never judges the handed view
    record's own node, so a barred name split across two keys of
    the record itself stands reportable."""

    def _record(self, extra):
        record = mod04.build_view_record()
        record.update(extra)
        return record

    def test_split_top_node_refused(self):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(
                self._record({"ground_": "clean", "truth": "clean"}))

    def test_controls_hold(self):
        result = mod10.run_view_leak_check(self._record({}))
        self.assertTrue(result["reportable"])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(
                self._record({"ground_truth": "clean"}))
        nested = mod04.build_view_record(
            contents=None, graph_position=None)
        nested["view_contents"] = {"ground_": 1, "truth": 1}
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(nested)


class TestR15005Mod01ReservedNode(unittest.TestCase):
    """R15-005: the MOD-01 reserved matter walk never judges the
    dict node, so a reserved value split across two keys of one
    dict validates at validate_record. Cure form under ruling 2:
    the joined exact reading."""

    def test_split_forms_carry(self):
        self.assertTrue(mod01._carries_reserved_matter(
            {"banked real money stake ": 1, "behaviour": 1}))
        self.assertTrue(mod01._carries_reserved_matter(
            {"w": {"banked real money stake ": 1, "behaviour": 1}}))
        self.assertTrue(mod01._carries_reserved_matter(
            {"w": [{"provisional anchor ": 1, "set": 1}]}))
        self.assertTrue(mod01._carries_reserved_matter(
            {"provisional anchor ": 1, "set": 1}))

    def test_gate_refuses_split_form(self):
        instance = mod01.minimal_valid_instance("1")
        instance["zz_res"] = {
            "banked real money stake ": 1, "behaviour": 1}
        self.assertFalse(mod01.validate_record("1", instance))

    def test_controls_hold(self):
        self.assertTrue(mod01._carries_reserved_matter(
            {"banked real money stake behaviour": 1}))
        self.assertTrue(mod01._carries_reserved_matter(
            {"x": "banked real money stake behaviour"}))
        self.assertFalse(mod01._carries_reserved_matter({"clean": 1}))
        instance = mod01.minimal_valid_instance("1")
        self.assertTrue(mod01.validate_record("1", instance))
        instance["zz_res"] = {"banked real money stake behaviour": 1}
        self.assertFalse(mod01.validate_record("1", instance))


class TestR15006Mod03RuleStateNode(unittest.TestCase):
    """R15-006: the MOD-03 rule state walk never judges the dict
    node, so a rule state field name split across two keys passes
    validate_generator_output. Cure form under ruling 3: the
    joined exact reading."""

    def test_split_forms_carry(self):
        self.assertTrue(mod03._value_carries_rule_state(
            {"reputa": 1, "tion": 1}))
        self.assertFalse(mod03.validate_generator_output(
            [{"reputa": 1, "tion": 1}]))
        self.assertFalse(mod03.validate_generator_output(
            [{"decided_": 1, "effect": 1}]))
        self.assertFalse(mod03.validate_generator_output(
            [{"w": {"reputa": 1, "tion": 1}}]))
        self.assertFalse(mod03.validate_generator_output(
            [{"w": [{"reputa": 1, "tion": 1}]}]))

    def test_controls_hold(self):
        self.assertFalse(mod03.validate_generator_output(
            [{"reputation": 1}]))
        self.assertTrue(mod03.validate_generator_output(
            [{"clean": 1}]))


class TestR15007Mod14PilotNode(unittest.TestCase):
    """R15-007: the MOD-14 pilot artefact screen never judges
    the dict node, so a barred pilot entry split across two keys
    stands delivered stamped with the pilot confined label."""

    def test_split_forms_refused(self):
        for artefact in (
                {"mo": 1, "ney": 1},
                {"anchor": 1, "set": 1},
                {"MO": 1, "NEY": 1},
                {"mo": 1, "": 1, "ney": 1},
                {"w": {"mo": 1, "ney": 1}},
                {"w": [{"mo": 1, "ney": 1}]}):
            with self.assertRaises(mod14.NamedShellFailure):
                mod14.pilot_run("timing", artefact)

    def test_controls_hold(self):
        for artefact in ({"money": 1}, {"anchor set": 1},
                         {("mo", "ney"): 1}):
            with self.assertRaises(mod14.NamedShellFailure):
                mod14.pilot_run("timing", artefact)
        output = mod14.pilot_run("timing", {"mo": 1, "net": 1})
        self.assertEqual(output["confinement_label"], "pilot confined")


class TestR15008Mod04FirstBarredField(unittest.TestCase):
    """R15-008: the MOD-04 locating companion _first_barred_field
    never judges the dict node, so build_view_record refuses a
    split barred node under its generic sentence alone."""

    def test_split_node_located(self):
        self.assertEqual(
            mod04._first_barred_field({"ground_": 1, "truth": 1}),
            "ground_truth")
        located = mod04._barred_group_and_field(
            {"view_contents": {"ground_": 1, "truth": 1}})
        self.assertIsNotNone(located)
        self.assertEqual(located[0], "contents")
        self.assertEqual(
            mod04._barred_field_label(located[1]), "ground_truth")

    def test_gate_sentence_names_split_field(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.build_view_record(
                contents=[{"ground_": 1, "truth": 1}])
        self.assertIn("ground_truth", str(caught.exception))

    def test_controls_hold(self):
        self.assertEqual(
            mod04._first_barred_field({"ground_truth": 1}),
            "ground_truth")
        self.assertIsNone(mod04._first_barred_field({"clean": 1}))
        self.assertTrue(mod04.view_record_carries_barred_field(
            {"view_contents": {"ground_": 1, "truth": 1}}))


class TestR15009Mod06SevenPartForms(unittest.TestCase):
    """R15-009: two clean seven part frozenset key forms one
    feature past the R14-006 cure form, the non ASCII part form
    and the one part tuple container form, fall back to the
    standing candidate enumeration and cost past the S-12 bound
    of 4 seconds."""

    NON_ASCII = frozenset(["\u00e0", "m", "0", "u", "n", "t", "z"])
    TUPLE_PART = frozenset([("a",), "m", "0", "u", "n", "t", "z"])

    def test_non_ascii_form_within_bound(self):
        payload = {self.NON_ASCII: 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)
        start = time.time()
        self.assertFalse(mod06._key_reads_as(self.NON_ASCII, "amount"))
        self.assertLess(time.time() - start, 4.0)

    def test_tuple_part_form_within_bound(self):
        payload = {self.TUPLE_PART: 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)
        start = time.time()
        self.assertFalse(mod06._key_reads_as(self.TUPLE_PART, "amount"))
        self.assertLess(time.time() - start, 4.0)

    def test_escrow_gate_within_bound(self):
        for key in (self.NON_ASCII, self.TUPLE_PART):
            start = time.time()
            result = mod06.escrow_result("release", payload={key: 1})
            self.assertLess(time.time() - start, 4.0)
            self.assertEqual(result["kind"], "release")

    def test_controls_hold(self):
        six = frozenset(["\u00e0", "m", "0", "u", "n", "t"])
        self.assertTrue(mod06._key_reads_as(six, "amount"))
        ascii_form = frozenset(["a", "m", "0", "u", "n", "t", "z"])
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred({ascii_form: 1}))
        self.assertLess(time.time() - start, 4.0)


class TestR15010ActorResolverBound(unittest.TestCase):
    """R15-010: the added letters limb of _resolve_actor_word at
    MOD-10 and MOD-14 runs every combination of cut positions
    with no candidate cap reaching that candidate space, so a
    clean actor word costs seconds growing about fourfold per
    four letters."""

    def test_mod10_long_word_within_bound(self):
        start = time.time()
        self.assertEqual(mod10._resolve_actor_word("z" * 24), "z" * 24)
        self.assertLess(time.time() - start, 4.0)

    def test_mod10_normalised_within_bound(self):
        start = time.time()
        self.assertEqual(mod10._normalised_actor("z" * 24), "z" * 24)
        self.assertLess(time.time() - start, 4.0)

    def test_mod14_long_word_within_bound(self):
        start = time.time()
        self.assertEqual(mod14._resolve_actor_word("z" * 24), "z" * 24)
        self.assertLess(time.time() - start, 4.0)

    def test_controls_hold(self):
        self.assertEqual(mod10._resolve_actor_word("person"), "person")
        self.assertEqual(mod10._normalised_actor("person"), "person")
        self.assertEqual(mod14._resolve_actor_word("person"), "person")
        self.assertEqual(mod14._normalise_actor("person"), "person")
        self.assertEqual(
            mod10._resolve_actor_word("personzz"), "person")


if __name__ == "__main__":
    unittest.main()
