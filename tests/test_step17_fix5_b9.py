"""Step 17 fix wave 5, Slice 9 defect and control tests.

Row FW5-08 (Low, T17R4-08): the unbounded refusal echo family
at fresh doors. At every door named by the 17 filings of the
ruling, a refusal or failure message or a refusal carriage
renders a handed value whole, so the telling grows with the
handing past any bound. The cure form is the FW4-10 bounded
rendering form: a rendering standing at 120 characters or
fewer stands whole; a longer rendering stands as its first
120 characters beside a length statement naming the standing
length and the 120 character bound, so the ground and the
next step of every refusal stand readable at the head of the
message and no telling grows with the handing.

Each defect test hands the filing handing at the filing scale
and requires the refusal in its named form, the bounded
rendering marker in the telling, the ground in product words,
and the telling under the stated cap. Each control pins a
standing the cure must preserve: a short handing rendered
whole with no marker, a served whole standing, or a held
bounded standing at a sibling door.

Python standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod01 as mod01
import crucible.mod02 as mod02
import crucible.mod04 as mod04
import crucible.mod06 as mod06
import crucible.mod08 as mod08
import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod12 as mod12
import crucible.mod14 as mod14

HUGE = 10 ** 5000
CAP = 1200
MARKER = "[bounded rendering: the handed value stands at "


def assert_bounded(test, text, ground, cap=CAP):
    test.assertIn(MARKER, text)
    test.assertIn(ground, text)
    test.assertLessEqual(len(text), cap)


class TestFW508Mod01Failures(unittest.TestCase):
    """O4-05: record_validation_failures, the outside field
    sentence names the handed field twice at its whole length."""

    def test_defect_huge_field_name_entry_bounded(self):
        form = mod01.FORM_IDS[0]
        record = mod01.minimal_valid_instance(form)
        record["h" * 100000] = 1
        entries = mod01.record_validation_failures(form, record)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        assert_bounded(self, entry, "the form names no such field")
        self.assertNotIn("h" * 500, entry)

    def test_control_small_field_name_stands_whole(self):
        form = mod01.FORM_IDS[0]
        record = mod01.minimal_valid_instance(form)
        record["h" * 10] = 1
        entries = mod01.record_validation_failures(form, record)
        self.assertEqual(len(entries), 1)
        self.assertIn("h" * 10, entries[0])
        self.assertNotIn(MARKER, entries[0])

    def test_control_valid_record_no_failures(self):
        form = mod01.FORM_IDS[0]
        record = mod01.minimal_valid_instance(form)
        self.assertEqual(
            mod01.record_validation_failures(form, record), [])


class TestFW508Mod02Derivation(unittest.TestCase):
    """O4-01: make_derivation_input, the domain refusal embeds
    the handed domain whole in text and in bytes form."""

    def test_defect_domain_text_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod02.make_derivation_input(domain="d" * 100000)
        assert_bounded(self, str(caught.exception),
                       "domain outside the two value vocabulary")
        self.assertNotIn("d" * 500, str(caught.exception))

    def test_defect_domain_bytes_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod02.make_derivation_input(domain=b"d" * 100000)
        assert_bounded(self, str(caught.exception),
                       "domain outside the two value vocabulary")

    def test_control_short_domain_stands_whole(self):
        with self.assertRaises(ValueError) as caught:
            mod02.make_derivation_input(domain="bogus")
        self.assertIn("bogus", str(caught.exception))
        self.assertNotIn(MARKER, str(caught.exception))


class TestFW508Mod02Draw(unittest.TestCase):
    """RED3-02, Y3-02, O4-02: the draw door refusals render the
    handed position or carried positions whole."""

    def setUp(self):
        self.state = mod02.initial_stream_state("s", 3)

    def test_defect_negative_int_position_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                position=-(10 ** 4000), state=self.state)
        assert_bounded(self, str(caught.exception),
                       "stands as a number in no admitted position form")

    def test_defect_negative_digit_text_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                position="-" + "9" * 5000, state=self.state)
        text = str(caught.exception)
        assert_bounded(self, text, "stands below zero")
        self.assertNotIn("9" * 500, text)

    def test_defect_bad_text_position_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream("s", "9" * 100000 + "x", 3)
        assert_bounded(self, str(caught.exception),
                       "stands in no numeric form")

    def test_defect_list_position_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream("s", [0] * 100000, 3)
        assert_bounded(self, str(caught.exception),
                       "stands in no numeric form")

    def test_defect_bad_carried_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream("s", 0, "x" * 100000)
        text = str(caught.exception)
        assert_bounded(self, text, "carried positions")
        self.assertNotIn("x" * 500, text)

    def test_control_small_negative_stands_whole(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(position=-5, state=self.state)
        text = str(caught.exception)
        self.assertIn("-5", text)
        self.assertNotIn(MARKER, text)

    def test_control_positive_huge_position_served_whole(self):
        record = mod02.draw_from_stream(
            position=HUGE, state=self.state)
        self.assertEqual(record["position"], HUGE)


class TestFW508GateSurface(unittest.TestCase):
    """O4-03: the DQ7-02 gate refusal surface at mod02 and
    mod04 names an extra keyword handing at its whole length.
    The gate holds in both acts; the telling size alone stands
    charged."""

    def test_defect_mod02_gate_note_and_names_bounded(self):
        record = mod02.derive_seed(None, **{"h" * 100000: 1})
        self.assertFalse(record["seed_drawn"])
        note = record["extra_handing_note"]
        assert_bounded(self, note, "stand outside the stated form")
        names = record["unexpected_keyword_handings"]
        self.assertEqual(len(names), 1)
        self.assertIn(MARKER, names[0])
        self.assertLessEqual(len(names[0]), CAP)

    def test_defect_mod04_gate_message_bounded(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.tick(**{"h" * 100000: 1})
        text = str(caught.exception)
        assert_bounded(self, text, "DERIVATION-GATED")
        self.assertNotIn("h" * 500, text)

    def test_control_gate_refusal_without_extra_unchanged(self):
        record = mod02.derive_seed(None)
        self.assertFalse(record["seed_drawn"])
        self.assertNotIn("extra_handing_note", record)
        self.assertNotIn("unexpected_keyword_handings", record)

    def test_control_mod04_plain_gate_message(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.tick()
        text = str(caught.exception)
        self.assertIn("DERIVATION-GATED", text)
        self.assertNotIn(MARKER, text)


class TestFW508Mod06(unittest.TestCase):
    """B1-02 and O1-02: run_instruction, the unnamed instruction
    refusal echoes the name whole. B1-03: escrow_contract_state,
    the variant refusal echoes the variant whole, and the lien
    state refusal at the same door echoes in the same form."""

    def test_defect_run_instruction_6000_bounded(self):
        with self.assertRaises(mod06.UnnamedInstruction) as caught:
            mod06.run_instruction("z" * 6000)
        text = str(caught.exception)
        assert_bounded(self, text, "instruction stands unnamed")
        self.assertNotIn("z" * 500, text)

    def test_defect_run_instruction_5000_bounded(self):
        with self.assertRaises(mod06.UnnamedInstruction) as caught:
            mod06.run_instruction("x" * 5000)
        assert_bounded(self, str(caught.exception),
                       "no instruction stands run")

    def test_defect_variant_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c1", variant="z" * 6000)
        text = str(caught.exception)
        assert_bounded(self, text,
                       "stands outside the B-3 and B-4 set")
        self.assertNotIn("z" * 500, text)

    def test_defect_lien_state_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state(
                "c1", variant="B-4", lien_state="z" * 6000)
        assert_bounded(self, str(caught.exception),
                       "stands outside the closed four value set")

    def test_control_none_name_stands_whole(self):
        with self.assertRaises(mod06.UnnamedInstruction) as caught:
            mod06.run_instruction(None)
        self.assertNotIn(MARKER, str(caught.exception))
        self.assertLessEqual(len(str(caught.exception)), 200)

    def test_control_short_variant_stands_whole(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c1", variant="Z-9")
        self.assertIn("Z-9", str(caught.exception))
        self.assertNotIn(MARKER, str(caught.exception))

    def test_control_valid_variant_served_whole(self):
        state = mod06.escrow_contract_state("c1", variant="B-4")
        self.assertEqual(state["variant"], "B-4")


class TestFW508Mod08(unittest.TestCase):
    """B1-04: accept_detection_input, the outside fields refusal
    echoes a field name whole."""

    def test_defect_outside_field_name_bounded(self):
        with self.assertRaises(
                mod08.NamedDetectionFailure) as caught:
            mod08.accept_detection_input({"z" * 6000: 1})
        text = str(caught.exception)
        assert_bounded(self, text, "fields outside DetectionInput")
        self.assertNotIn("z" * 500, text)

    def test_control_huge_int_key_held_bounded(self):
        with self.assertRaises(
                mod08.NamedDetectionFailure) as caught:
            mod08.accept_detection_input({HUGE: 1})
        self.assertLessEqual(len(str(caught.exception)), 200)

    def test_control_short_field_name_stands_whole(self):
        with self.assertRaises(
                mod08.NamedDetectionFailure) as caught:
            mod08.accept_detection_input({"bogus": 1})
        self.assertIn("bogus", str(caught.exception))
        self.assertNotIn(MARKER, str(caught.exception))


class TestFW508Mod10Share(unittest.TestCase):
    """B1-01: record_gate_passing_share, the share form refusal
    echoes the epoch whole, the epoch shape judgement standing
    after the share form judgement at this door."""

    def setUp(self):
        mod10.reset_stores()

    def test_defect_huge_epoch_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("e1", HUGE, {"bad": 1})
        assert_bounded(self, str(caught.exception),
                       "stands in no stated share form")

    def test_defect_text_epoch_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share(
                "e2", "z" * 6000, {"bad": 1})
        text = str(caught.exception)
        assert_bounded(self, text, "stands in no stated share form")
        self.assertNotIn("z" * 500, text)

    def test_control_plain_epoch_stands_whole(self):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("e3", 3, {"bad": 1})
        text = str(caught.exception)
        self.assertIn("epoch 3", text)
        self.assertNotIn(MARKER, text)

    def test_control_valid_share_recorded(self):
        mod10.record_gate_passing_share("ok", 3, 0.5)
        shares = mod10.gate_passing_shares_for_run("ok")
        self.assertTrue(shares)


class TestFW508Mod10Aggregate(unittest.TestCase):
    """O1-01: retain_daily_aggregate_deliveries, the aggregate
    refusal echo at the component and viewer fields, at the
    FW3-04 locus named in the filing."""

    def setUp(self):
        mod10.reset_stores()

    def test_defect_component_text_bounded(self):
        delivery = {
            "simulated_day": 1, "viewer_id": "v1",
            "joint_outcome_components": [1, 0, 0, 0],
            "component_denominators": ["x" * 5000, 1, 1, 1],
            "honest_share": 0, "gate_passing_shares": {},
            "epochs_ending_on_day": []}
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries("ra", [delivery])
        text = str(caught.exception)
        assert_bounded(self, text, "stand in a non numeric form")
        self.assertNotIn("x" * 500, text)

    def test_defect_viewer_text_bounded(self):
        delivery = {
            "simulated_day": 1, "viewer_id": "x" * 5000,
            "joint_outcome_components": [HUGE, 0, 0, 0],
            "component_denominators": [1, 1, 1, 1],
            "honest_share": 0, "gate_passing_shares": {},
            "epochs_ending_on_day": []}
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries("rb", [delivery])
        text = str(caught.exception)
        assert_bounded(self, text, "stand impossible")
        self.assertNotIn("x" * 500, text)

    def test_control_valid_delivery_retained_whole(self):
        delivery = {
            "simulated_day": 1, "viewer_id": "v1",
            "joint_outcome_components": [1, 0, 0, 0],
            "component_denominators": [2, 1, 1, 1],
            "honest_share": 0, "gate_passing_shares": {},
            "epochs_ending_on_day": []}
        count = mod10.retain_daily_aggregate_deliveries(
            "rc", [delivery])
        self.assertEqual(count, 1)


class TestFW508Mod10Duplicate(unittest.TestCase):
    """O4-06: retain_run_record, the duplicate record refusal
    embeds the handed run identifier whole, where the reading
    door of the same module bounds the same identifier."""

    def setUp(self):
        mod10.reset_stores()

    def test_defect_duplicate_huge_id_bounded(self):
        mod10.retain_run_record({"run_id": "h" * 100000, "v": 1})
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record({"run_id": "h" * 100000, "v": 2})
        text = str(caught.exception)
        assert_bounded(self, text,
                       "second record for the same run is rejected")
        self.assertNotIn("h" * 500, text)

    def test_control_duplicate_small_id_stands_whole(self):
        mod10.retain_run_record({"run_id": "dup-small", "v": 1})
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record({"run_id": "dup-small", "v": 2})
        text = str(caught.exception)
        self.assertIn("dup-small", text)
        self.assertNotIn(MARKER, text)
        stored = mod10.read_run_record("dup-small")
        self.assertEqual(stored["v"], 1)

    def test_control_lookup_huge_id_held_bounded(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.read_run_record("q" * 100000)
        self.assertLessEqual(len(str(caught.exception)), 1000)
        self.assertIn(MARKER, str(caught.exception))


class TestFW508Mod11Headline(unittest.TestCase):
    """O5-01: make_headline_unit, the fields beyond the closed
    unit refusal echoes handed field names without bound."""

    def test_defect_one_extra_field_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit({"x" * 5000: 1})
        text = str(caught.exception)
        assert_bounded(self, text, "fields beyond the closed unit")
        self.assertNotIn("x" * 500, text)

    def test_defect_two_extra_fields_bounded(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit(
                {"x" * 3000: 1, "y" * 3000: 2})
        text = str(caught.exception)
        assert_bounded(self, text, "fields beyond the closed unit")
        self.assertNotIn("x" * 500, text)
        self.assertNotIn("y" * 500, text)

    def test_control_short_extra_key_stands_whole(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit({"bogus_field": 1})
        self.assertIn("bogus_field", str(caught.exception))
        self.assertNotIn(MARKER, str(caught.exception))

    def test_control_missing_values_named_form_stands(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit()
        self.assertIn("a handing stands missing",
                      str(caught.exception))


class TestFW508Mod12StartRun(unittest.TestCase):
    """O4-04: start_run, the named input failure embeds the
    handed run class whole in both fields of the refusal
    record. The family identifier ground at the same door
    echoes in the same form on a container handing."""

    def test_defect_run_class_bounded_both_fields(self):
        record = mod12.start_run(run_class="h" * 100000)
        self.assertFalse(record["run_started"])
        self.assertFalse(record["seed_drawn"])
        assert_bounded(self, record["failure"],
                       "run class missing or outside")
        assert_bounded(self, record["ground_in_words"],
                       "run class missing or outside")
        self.assertNotIn("h" * 500, record["failure"])

    def test_defect_family_list_ground_bounded(self):
        record = mod12.start_run(
            run_class="screening", family_id=["x"] * 100000)
        self.assertEqual(record["status"], "input failure")
        assert_bounded(self, record["failure"],
                       "family identifier missing")
        assert_bounded(self, record["ground_in_words"],
                       "family identifier missing")

    def test_control_short_class_stands_whole(self):
        record = mod12.start_run(run_class="bogus")
        self.assertIn("bogus", record["ground_in_words"])
        self.assertNotIn(MARKER, record["ground_in_words"])

    def test_control_lawful_start_gated(self):
        record = mod12.start_run(
            run_class="screening", family_id="fam-1")
        self.assertFalse(record["run_started"])
        self.assertFalse(record["seed_drawn"])


class TestFW508Mod14Shell(unittest.TestCase):
    """Y2-01 and O2-01: run_command, the unknown command
    carriage echoes the handed command without bound, in its
    failure text and in its carriage fields; pilot_run, the
    pilot use refusal echoes the handed use whole."""

    def test_defect_run_command_100k_bounded(self):
        carriage = mod14.run_command("x" * 100000)
        self.assertTrue(carriage["operator_sees_failure"])
        assert_bounded(self, carriage["failure"],
                       "unknown shell command")
        self.assertNotIn("x" * 500, carriage["failure"])
        stage = carriage["stage"]
        self.assertIsInstance(stage, str)
        self.assertIn(MARKER, stage)
        self.assertLessEqual(len(stage), CAP)

    def test_defect_run_command_200k_bounded(self):
        carriage = mod14.run_command("z" * 200000, {})
        assert_bounded(self, carriage["failure"],
                       "unknown shell command")
        message = carriage["failure_value"]["message"]
        assert_bounded(self, message, "unknown shell command")
        self.assertNotIn("z" * 500, carriage["failure"])

    def test_defect_pilot_use_bounded(self):
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.pilot_run("u" * 200000, {})
        text = str(caught.exception)
        assert_bounded(self, text, "pilot use outside")
        self.assertNotIn("u" * 500, text)

    def test_control_short_command_stands_whole(self):
        carriage = mod14.run_command("bogus-command")
        self.assertIn("bogus-command", carriage["failure"])
        self.assertNotIn(MARKER, carriage["failure"])
        self.assertEqual(carriage["stage"], "bogus-command")

    def test_control_pilot_valid_use_served_whole(self):
        output = mod14.pilot_run("timing", {"figure": 1})
        self.assertEqual(output["confinement_label"],
                         "pilot confined")
        self.assertEqual(output["use"], "timing")


class TestFW508NeighbouringCuresStand(unittest.TestCase):
    """Controls at the shared files: the earlier slice cures
    standing in the same modules stand preserved whole."""

    def test_control_slice1_negative_text_ground_stands(self):
        state = mod02.initial_stream_state("s", 3)
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(position="-5", state=state)
        self.assertIn("the handed position stands below zero",
                      str(caught.exception))

    def test_control_slice5_form4_entries_stand(self):
        record = mod01.build_run_record()
        record["sweep_identifier"] = object()
        failures = mod01.record_validation_failures("4", record)
        self.assertTrue(
            any("sweep_identifier" in entry for entry in failures))


if __name__ == "__main__":
    unittest.main()
