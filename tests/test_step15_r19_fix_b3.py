# Step 15 rerun, fix wave 18, Builder 3 pins.
# Group 3: the barred gate and sentence family at MOD-06 and
# MOD-08, under settlement S-14. Rows R18-001, R18-020,
# R18-021, R18-022, R18-023, R18-024, R18-025, R18-059, and
# R18-060. OP-16 stands OPEN: every pin here rests only on
# the shipped guard stated names, barred values, and
# carriage value, and no pin charges any value OP-16
# reserves.
import unittest

import crucible.mod06 as mod06
import crucible.mod08 as mod08


LABEL_FIELD = mod08.PROFILE_BOUND_LABEL_FIELD
CARRIAGE = mod08.PROFILE_LABEL_CARRIAGE


class LieStr(str):
    def __new__(cls, stored, shown):
        obj = str.__new__(cls, stored)
        obj._shown = shown
        return obj

    def __str__(self):
        return self._shown


class EvilBoth(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(str.__str__(self))


class RaiseBoth(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __str__(self):
        raise RuntimeError("boom-str")

    def __repr__(self):
        raise RuntimeError("boom-str")


class ImpersonatingKey(str):
    def __new__(cls):
        return str.__new__(cls, "bogus_key")

    def __hash__(self):
        return str.__hash__(LABEL_FIELD)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


def figure(extra=None):
    record = {LABEL_FIELD: CARRIAGE, "score_verdict": None}
    if extra:
        record.update(extra)
    return record


def deep_figure(wraps):
    fig = figure()
    for _ in range(wraps):
        fig = figure({"a": fig})
    return fig


def chain_payload(containers):
    value = 1
    for _ in range(containers):
        value = {"a": value}
    return value


def escrow_sentence(payload):
    try:
        mod06.escrow_result("result", payload=payload)
    except ValueError as error:
        return str(error)
    return ""


def report_sentence(fig):
    try:
        mod08.report([fig])
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


def detection_sentence(record):
    try:
        mod08.accept_detection_input(record)
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


def detection_record(inner):
    return {
        "agent_identifier": "agent-1",
        "day": 3,
        "feature_values": {},
        "records_for_agent_and_day": [inner],
    }


class TestR18001FrozensetSplit(unittest.TestCase):
    def test_frozenset_split_names_refused(self):
        cases = [
            {frozenset({"ver", "d", "ict"}): "pass"},
            {frozenset({"res", "u", "lt"}): "fail"},
            {frozenset({"ver", "dict"}): "pass"},
            {frozenset({"res", "ult"}): "fail"},
            {frozenset({"score", "_ver", "dict"}): "pass"},
        ]
        for extra in cases:
            self.assertFalse(mod08.validate_output(figure(extra)))

    def test_frozenset_split_nested_refused(self):
        cases = [
            {"wrap": {frozenset({"ver", "d", "ict"}): "pass"}},
            {"wrap": {frozenset({"res", "ult"}): "fail"}},
        ]
        for extra in cases:
            self.assertFalse(mod08.validate_output(figure(extra)))

    def test_frozenset_split_beside_other_key_refused(self):
        extra = {frozenset({"ver", "dict"}): "pass", "other": "x"}
        self.assertFalse(mod08.validate_output(figure(extra)))

    def test_tuple_split_control_refused(self):
        self.assertFalse(
            mod08.validate_output(figure({("ver", "dict"): "pass"})))

    def test_frozenset_whole_name_control_refused(self):
        self.assertFalse(mod08.validate_output(
            figure({frozenset({"verdict"}): "pass"})))

    def test_clean_output_control_validates(self):
        self.assertTrue(mod08.validate_output(figure()))


class TestR18020EscrowSentenceGround(unittest.TestCase):
    def test_cycle_sentence_names_cycle_not_barred(self):
        payload = {"x": 1}
        payload["self"] = payload
        sentence = escrow_sentence(payload)
        self.assertTrue(sentence)
        self.assertIn("revisits", sentence)
        self.assertNotIn("carries a barred value", sentence)

    def test_depth_sentence_names_bound_not_barred(self):
        sentence = escrow_sentence(chain_payload(102))
        self.assertTrue(sentence)
        self.assertIn("depth bound", sentence)
        self.assertNotIn("carries a barred value", sentence)

    def test_clean_chain_control_returned(self):
        result = mod06.escrow_result(
            "result", payload=chain_payload(100))
        self.assertEqual(result["kind"], "result")

    def test_plain_barred_control_names_barred_value(self):
        sentence = escrow_sentence({"real_money_value": 5})
        self.assertIn("carries a barred value", sentence)
        self.assertIn("a real money value", sentence)

    def test_shared_container_control_returned(self):
        shared = {"amount": 1}
        result = mod06.escrow_result(
            "result", payload={"one": shared, "two": shared})
        self.assertEqual(result["kind"], "result")


class TestR18021ReportCycleDepthGround(unittest.TestCase):
    def test_report_cycle_ground_names_cycle(self):
        fig = figure()
        fig["self"] = fig
        self.assertFalse(mod08.validate_output(fig))
        sentence = report_sentence(fig)
        self.assertIn("cycle", sentence)
        self.assertNotIn("barred pass or fail verdict", sentence)

    def test_report_depth_ground_names_bound(self):
        fig = deep_figure(101)
        self.assertFalse(mod08.validate_output(fig))
        sentence = report_sentence(fig)
        self.assertIn("bound", sentence)
        self.assertNotIn("barred pass or fail verdict", sentence)

    def test_report_plain_barred_control_names_verdict_ground(self):
        sentence = report_sentence(figure({"score_verdict": "pass"}))
        self.assertIn("barred pass or fail verdict", sentence)

    def test_deep_control_at_bound_validates(self):
        self.assertTrue(mod08.validate_output(deep_figure(100)))


class TestR18022NamerGround(unittest.TestCase):
    def test_lying_key_names_anchor_not_real_money(self):
        payload = {
            LieStr("innocent", "real_money_value"): 5,
            "anchor_set": ["x"],
        }
        sentence = escrow_sentence(payload)
        self.assertIn("a supplied anchor set", sentence)
        self.assertNotIn("(real_money_value)", sentence)

    def test_split_pair_names_pair(self):
        payload = {"am": 1, "ount": 2, "curr": 3, "ency": 4}
        sentence = escrow_sentence(payload)
        self.assertIn("an amount and currency pair", sentence)

    def test_split_real_money_names_real_money(self):
        sentence = escrow_sentence({"real_mo": 5, "ney": 6})
        self.assertIn("a real money value", sentence)

    def test_split_anchor_names_anchor(self):
        sentence = escrow_sentence({"anch": None, "or_set": None})
        self.assertIn("a supplied anchor set", sentence)

    def test_homoglyph_anchor_names_anchor(self):
        sentence = escrow_sentence({"аnchor_set": ["x"]})
        self.assertIn("a supplied anchor set", sentence)

    def test_plain_real_money_control(self):
        sentence = escrow_sentence({"real_money_value": 5})
        self.assertIn("a real money value (real_money_value)", sentence)

    def test_plain_pair_control(self):
        sentence = escrow_sentence({"amount": 1, "currency": 2})
        self.assertIn("an amount and currency pair", sentence)

    def test_plain_anchor_control(self):
        sentence = escrow_sentence({"anchor_set": ["x"]})
        self.assertIn("a supplied anchor set (anchor_set)", sentence)


class TestR18023RenderingSites(unittest.TestCase):
    def test_namer_raising_key_beside_pair_delivers(self):
        payload = {"amount": 1, "currency": 2, RaiseBoth("x"): 5}
        sentence = escrow_sentence(payload)
        self.assertIn("an amount and currency pair", sentence)

    def test_namer_raising_key_storing_barred_name_delivers(self):
        sentence = escrow_sentence({RaiseBoth("real_money_value"): 5})
        self.assertIn("a real money value", sentence)

    def test_find_barred_raising_key_delivers(self):
        record = detection_record({RaiseBoth("label"): 1})
        sentence = detection_sentence(record)
        self.assertIn("barred field present", sentence)
        self.assertIn("/label", sentence)

    def test_author_sealed_raising_kind_delivers(self):
        sealed = mod08.freeze_sealed_set(mod08.create_sealed_set())
        try:
            mod08.author_sealed_class(
                sealed, RaiseBoth("bogus"), "id-1",
                separations=list(mod08._SEPARATIONS))
        except mod08.NamedDetectionFailure as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("authored kind stands unnamed", sentence)

    def test_plain_barred_field_control(self):
        sentence = detection_sentence(detection_record({"label": 1}))
        self.assertIn("/records_for_agent_and_day[0]/label", sentence)

    def test_plain_unnamed_kind_control(self):
        sealed = mod08.freeze_sealed_set(mod08.create_sealed_set())
        try:
            mod08.author_sealed_class(
                sealed, "bogus", "id-1",
                separations=list(mod08._SEPARATIONS))
        except mod08.NamedDetectionFailure as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("authored kind stands unnamed: bogus", sentence)


class TestR18024LabelFieldLookup(unittest.TestCase):
    def test_dressed_key_impersonating_field_not_validated(self):
        record = {ImpersonatingKey(): CARRIAGE, "verdict": "innocuous"}
        self.assertFalse(mod08.validate_output(record))

    def test_dressed_key_report_refused(self):
        record = {ImpersonatingKey(): CARRIAGE, "verdict": "innocuous"}
        self.assertTrue(report_sentence(record))

    def test_missing_label_control_refused(self):
        self.assertFalse(mod08.validate_output({"verdict": "innocuous"}))

    def test_plain_bogus_key_control_refused(self):
        record = {"bogus_key": CARRIAGE, "verdict": "innocuous"}
        self.assertFalse(mod08.validate_output(record))

    def test_proper_label_control_validates(self):
        self.assertTrue(mod08.validate_output(figure()))


class TestR18025ReportGroundSelection(unittest.TestCase):
    def test_locus_verdict_key_named(self):
        sentence = report_sentence(figure({"verdict": "pass"}))
        self.assertIn("(verdict)", sentence)
        self.assertNotIn("(score_verdict)", sentence)

    def test_locus_outcome_key_named(self):
        sentence = report_sentence(figure({"outcome": "fail"}))
        self.assertIn("(outcome)", sentence)
        self.assertNotIn("(score_verdict)", sentence)

    def test_locus_result_key_named(self):
        sentence = report_sentence(figure({"result": "pass"}))
        self.assertIn("(result)", sentence)
        self.assertNotIn("(score_verdict)", sentence)

    def test_locus_nested_under_outcome_named(self):
        extra = {"outcome": [{"verdict": "pass"}]}
        sentence = report_sentence(figure(extra))
        self.assertNotIn("(score_verdict)", sentence)
        self.assertIn("(verdict)", sentence)

    def test_locus_split_keys_named(self):
        extra = {"ver": "pass", "dict": "x"}
        sentence = report_sentence(figure(extra))
        self.assertIn("(verdict)", sentence)
        self.assertNotIn("(score_verdict)", sentence)

    def test_lying_label_names_label_ground(self):
        fig = {LABEL_FIELD: EvilBoth("bogus"), "score_verdict": None}
        sentence = report_sentence(fig)
        self.assertIn("profile bound label", sentence)
        self.assertNotIn("barred pass or fail verdict", sentence)

    def test_true_score_verdict_control_names_score_verdict(self):
        sentence = report_sentence(figure({"score_verdict": "pass"}))
        self.assertIn("(score_verdict)", sentence)

    def test_plain_bogus_label_control_names_label_ground(self):
        fig = {LABEL_FIELD: "bogus", "score_verdict": None}
        sentence = report_sentence(fig)
        self.assertIn("profile bound label", sentence)


class TestR18059FindBarredPathName(unittest.TestCase):
    def test_lying_key_names_stored_path(self):
        record = detection_record({LieStr("label", "innocent"): 1})
        sentence = detection_sentence(record)
        self.assertIn("/records_for_agent_and_day[0]/label", sentence)
        self.assertNotIn("/innocent", sentence)

    def test_plain_label_control_path(self):
        sentence = detection_sentence(detection_record({"label": 1}))
        self.assertIn("/records_for_agent_and_day[0]/label", sentence)

    def test_split_name_control_parent_path(self):
        record = detection_record({"la": 1, "bel": 2})
        sentence = detection_sentence(record)
        self.assertIn(
            "DetectionInput: /records_for_agent_and_day[0]", sentence)
        self.assertNotIn("/la", sentence)


class TestR18060UseNamingSentence(unittest.TestCase):
    def test_both_uses_against_one_states_both_sides(self):
        artefact = {"uses_named": ["conformance", "assumption"]}
        try:
            mod08.validate_use_naming(artefact, ["conformance"])
        except mod08.SilentUseMovement as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("conformance", sentence)
        self.assertIn("assumption", sentence)
        self.assertNotIn("names one use while", sentence)

    def test_one_use_against_bogus_states_both_sides(self):
        artefact = {"uses_named": ["conformance"]}
        try:
            mod08.validate_use_naming(artefact, ["bogus"])
        except mod08.SilentUseMovement as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("conformance", sentence)
        self.assertIn("bogus", sentence)
        self.assertNotIn("names one use while", sentence)

    def test_matching_uses_control_returns_true(self):
        artefact = {"uses_named": ["conformance"]}
        self.assertTrue(
            mod08.validate_use_naming(artefact, ["conformance"]))

    def test_no_use_control_sentence(self):
        try:
            mod08.validate_use_naming({"uses_named": []})
        except mod08.SilentUseMovement as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("neither use stands named", sentence)

    def test_unnamed_use_control_sentence(self):
        try:
            mod08.validate_use_naming({"uses_named": ["bogus"]})
        except mod08.SilentUseMovement as error:
            sentence = str(error)
        else:
            sentence = ""
        self.assertIn("a use stands unnamed", sentence)


if __name__ == "__main__":
    unittest.main()
