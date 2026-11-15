import unittest

from crucible import mod06, mod08


class LieStr(str):
    def __new__(cls, stored, reading):
        obj = str.__new__(cls, stored)
        obj._reading = reading
        return obj

    def __str__(self):
        return self._reading

    def __repr__(self):
        return self._reading


def chain(length, leaf):
    node = leaf
    for _ in range(length):
        node = {"a": node}
    return node


def escrow_sentence(payload):
    try:
        mod06.escrow_result("kind", payload=payload)
    except ValueError as error:
        return str(error)
    return ""


def detection_record(inner):
    return {
        "agent_identifier": "agent-1",
        "day": 3,
        "feature_values": {},
        "records_for_agent_and_day": [inner],
    }


def detection_sentence(record):
    try:
        mod08.accept_detection_input(record)
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


def use_naming_sentence(artefact, run_record_uses=None):
    try:
        mod08.validate_use_naming(artefact, run_record_uses)
    except mod08.SilentUseMovement as error:
        return str(error)
    return ""


class TestR19011DeepNamer(unittest.TestCase):
    def test_anchor_at_105_names_ground_control(self):
        sentence = escrow_sentence(chain(105, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_108_names_ground_control(self):
        sentence = escrow_sentence(chain(108, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_109_names_ground_control(self):
        sentence = escrow_sentence(chain(109, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_110_names_ground_control(self):
        sentence = escrow_sentence(chain(110, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_111_names_ground(self):
        sentence = escrow_sentence(chain(111, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_115_names_ground(self):
        sentence = escrow_sentence(chain(115, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_150_names_ground(self):
        sentence = escrow_sentence(chain(150, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_500_names_ground(self):
        sentence = escrow_sentence(chain(500, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_anchor_at_900_names_ground(self):
        sentence = escrow_sentence(chain(900, {"anchor_set": 1}))
        self.assertIn("a supplied anchor set (anchor_set)", sentence)

    def test_real_money_at_150_names_ground(self):
        sentence = escrow_sentence(chain(150, {"real_money_value": 1}))
        self.assertIn("a real money value (real_money_value)", sentence)

    def test_pair_at_150_names_ground(self):
        sentence = escrow_sentence(
            chain(150, {"amount": 1, "currency": "x"}))
        self.assertIn("an amount and currency pair", sentence)

    def test_chain_at_1005_depth_ground_control(self):
        sentence = escrow_sentence(chain(1005, {"anchor_set": 1}))
        self.assertIn("depth bound ground alone", sentence)


class TestR19012SentenceStoredText(unittest.TestCase):
    def test_use_naming_record_side_names_stored(self):
        sentence = use_naming_sentence(
            {"uses_named": ["conformance"]},
            [LieStr("bogus", "conformance")])
        self.assertIn(
            "the artefact names conformance while the run record "
            "names bogus", sentence)

    def test_use_naming_artefact_side_names_stored(self):
        sentence = use_naming_sentence(
            {"uses_named": [LieStr("assumption", "conformance")]},
            ["conformance"])
        self.assertIn(
            "the artefact names assumption while the run record "
            "names conformance", sentence)

    def test_use_naming_both_sides_name_stored(self):
        sentence = use_naming_sentence(
            {"uses_named": [LieStr("conformance", "assumption")]},
            ["assumption"])
        self.assertIn(
            "the artefact names conformance while the run record "
            "names assumption", sentence)

    def test_use_naming_unnamed_names_stored(self):
        sentence = use_naming_sentence(
            {"uses_named": [LieStr("bogus", "conformance")]})
        self.assertIn("a use stands unnamed: bogus", sentence)

    def test_outside_fields_names_stored(self):
        record = detection_record([])
        record[LieStr("evil_field", "day")] = 1
        sentence = detection_sentence(record)
        self.assertIn("fields outside DetectionInput: evil_field",
                      sentence)

    def test_mode_unnamed_names_stored(self):
        try:
            mod08.score_day([], mode=LieStr("bogus", "conformance"))
        except mod08.NamedDetectionFailure as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("scoring mode stands unnamed: bogus", sentence)

    def test_table_unrecorded_names_stored(self):
        try:
            mod08.conformance_statement(LieStr("XX-9", "LR-1"))
        except mod08.NamedDetectionFailure as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn(
            "conformance statement names no recorded table: XX-9",
            sentence)

    def test_variant_names_stored(self):
        try:
            mod06.escrow_result(
                "kind", variant=LieStr("X9", "B-4"))
        except ValueError as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9", sentence)

    def test_plain_unnamed_use_control(self):
        sentence = use_naming_sentence({"uses_named": ["bogus"]})
        self.assertIn("a use stands unnamed: bogus", sentence)

    def test_plain_mismatch_control(self):
        sentence = use_naming_sentence(
            {"uses_named": ["conformance"]}, ["bogus"])
        self.assertIn(
            "the artefact names conformance while the run record "
            "names bogus", sentence)

    def test_plain_outside_field_control(self):
        record = detection_record([])
        record["evil_field"] = 1
        sentence = detection_sentence(record)
        self.assertIn("fields outside DetectionInput: evil_field",
                      sentence)

    def test_plain_mode_control(self):
        try:
            mod08.score_day([], mode="bogus")
        except mod08.NamedDetectionFailure as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("scoring mode stands unnamed: bogus", sentence)

    def test_plain_table_control(self):
        try:
            mod08.conformance_statement("XX-9")
        except mod08.NamedDetectionFailure as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn(
            "conformance statement names no recorded table: XX-9",
            sentence)

    def test_plain_variant_control(self):
        try:
            mod06.escrow_result("kind", variant="X9")
        except ValueError as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9", sentence)

    def test_valid_variant_control(self):
        result = mod06.escrow_result("kind", variant="B-4")
        self.assertEqual(result["variant"], "B-4")


class TestR19056ContainerKeyPath(unittest.TestCase):
    def test_tuple_split_key_path_names_label(self):
        sentence = detection_sentence(
            detection_record({("la", "bel"): 1}))
        self.assertIn("/records_for_agent_and_day[0]/label", sentence)

    def test_tuple_single_key_path_names_label(self):
        sentence = detection_sentence(
            detection_record({("label",): 1}))
        self.assertIn("/records_for_agent_and_day[0]/label", sentence)

    def test_frozenset_key_path_names_label(self):
        sentence = detection_sentence(
            detection_record({frozenset({"label"}): 1}))
        self.assertIn("/records_for_agent_and_day[0]/label", sentence)

    def test_plain_label_key_control(self):
        sentence = detection_sentence(detection_record({"label": 1}))
        self.assertIn("/records_for_agent_and_day[0]/label", sentence)

    def test_nonbarred_container_key_control(self):
        sentence = detection_sentence(
            detection_record({("inn", "ocent"): 1}))
        self.assertEqual(sentence, "")


if __name__ == "__main__":
    unittest.main()
