import unittest

import crucible.mod04 as mod04


def _frozenset_chain(depth):
    value = 1
    for _ in range(depth):
        value = frozenset((value,))
    return value


def _tuple_chain(depth):
    value = 1
    for _ in range(depth):
        value = (value,)
    return value


def _list_chain(depth, leaf="needle"):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def _state(feature_values):
    return {
        "agent_identifier": "agent-1",
        "day": 1,
        "feature_values": feature_values,
        "rule_records": [],
    }


class LyingGetRecord(dict):
    def __init__(self, stored, lies):
        super().__init__(stored)
        self._lies = lies

    def get(self, key, default=None):
        if key in self._lies:
            return self._lies[key]
        return default


class DeepcopyTrojan:
    def __deepcopy__(self, memo):
        return {"membership": 1}


class TestR3002SelectViewRecordsBaseDictRead(unittest.TestCase):
    def test_lying_get_viewer_day_and_position_do_not_admit(self):
        stored = {
            "viewer_id": "other-viewer",
            "first_seen_day": 11,
            "arising_position": 99,
        }
        lies = {
            "viewer_id": "viewer-1",
            "first_seen_day": 10,
            "arising_position": 0,
        }
        record = LyingGetRecord(stored, lies)
        selected = mod04.select_view_records(
            [record], "viewer-1", 5, delay=-6, as_of_position=1)
        self.assertEqual(selected, [])

    def test_lying_get_day_and_position_do_not_admit_matching_viewer(self):
        stored = {
            "viewer_id": "viewer-1",
            "first_seen_day": 11,
            "arising_position": 99,
        }
        lies = {"first_seen_day": 10, "arising_position": 0}
        record = LyingGetRecord(stored, lies)
        selected = mod04.select_view_records(
            [record], "viewer-1", 5, delay=-6, as_of_position=1)
        self.assertEqual(selected, [])

    def test_lying_get_alternate_field_names_do_not_admit(self):
        stored = {
            "viewer_identifier": "other-viewer",
            "day": 11,
            "position": 99,
        }
        lies = {
            "viewer_identifier": "viewer-1",
            "day": 10,
            "position": 0,
        }
        record = LyingGetRecord(stored, lies)
        selected = mod04.select_view_records(
            [record], "viewer-1", 5, delay=-6, as_of_position=1)
        self.assertEqual(selected, [])

    def test_plain_lawful_record_still_admitted(self):
        record = {
            "viewer_id": "viewer-1",
            "first_seen_day": 3,
            "arising_position": 0,
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", 5, delay=-6, as_of_position=1)
        self.assertEqual(len(selected), 1)

    def test_plain_excluded_record_still_excluded(self):
        record = {
            "viewer_id": "viewer-1",
            "first_seen_day": 11,
            "arising_position": 99,
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", 5, delay=-6, as_of_position=1)
        self.assertEqual(selected, [])


class TestR3016CleaningSetNestingBound(unittest.TestCase):
    def test_set_wrapped_frozenset_chain_past_bound_refused(self):
        state = _state({"x": {_frozenset_chain(150)}})
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(state)

    def test_set_wrapped_frozenset_chain_far_past_bound_named_form(self):
        state = _state({"x": {_frozenset_chain(500)}})
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(state)

    def test_set_nesting_mid_chain_refused(self):
        state = _state({"x": {"k": {_frozenset_chain(150)}}})
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(state)

    def test_shallow_set_value_projects_intact(self):
        state = _state({"x": {_frozenset_chain(3)}})
        projected = mod04.project_detection_input(state)
        self.assertEqual(projected["feature_values"]["x"], {_frozenset_chain(3)})

    def test_plain_frozenset_chain_past_bound_still_refused(self):
        state = _state({"x": _frozenset_chain(150)})
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(state)


class TestR3017CleaningLeafCopyUndirected(unittest.TestCase):
    def test_trojan_leaf_does_not_materialise_barred_dict(self):
        state = _state({"x": DeepcopyTrojan(), "ok": 2})
        projected = mod04.project_detection_input(state)
        self.assertNotEqual(projected["feature_values"]["x"], {"membership": 1})
        self.assertFalse(
            mod04.view_record_carries_barred_field(projected))

    def test_trojan_leaf_nested_in_dict_does_not_materialise(self):
        state = _state({"x": {"inner": DeepcopyTrojan()}})
        projected = mod04.project_detection_input(state)
        self.assertFalse(
            mod04.view_record_carries_barred_field(projected))

    def test_plain_barred_dict_still_stripped(self):
        state = _state({"x": {"membership": 1}, "ok": 2})
        projected = mod04.project_detection_input(state)
        self.assertEqual(projected["feature_values"], {"x": {}, "ok": 2})


class TestR3018ValueAppearsSetAndBound(unittest.TestCase):
    def test_canary_inside_set_reads_present(self):
        self.assertTrue(mod04._value_appears("needle", {"x", "needle"}))

    def test_canary_inside_frozenset_reads_present(self):
        node = {"k": frozenset(("needle",))}
        self.assertTrue(mod04._value_appears("needle", node))

    def test_canary_absent_from_set_reads_absent(self):
        self.assertFalse(mod04._value_appears("needle", {"x", "other"}))

    def test_canary_in_list_and_tuple_still_present(self):
        self.assertTrue(mod04._value_appears("needle", ["x", ["needle"]]))
        self.assertTrue(mod04._value_appears("needle", ("x", ("needle",))))

    def test_deep_projection_refused_in_named_form(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04._value_appears("needle", _list_chain(150))

    def test_far_deep_projection_named_form_not_recursion_error(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04._value_appears("needle", _list_chain(2000))

    def test_shallow_chain_still_answers(self):
        self.assertTrue(mod04._value_appears("needle", _list_chain(50)))
        self.assertFalse(mod04._value_appears("absent", _list_chain(50)))


class TestR3046ViewCopyGuardKeyPosition(unittest.TestCase):
    def test_frozenset_chain_key_past_bound_refused(self):
        record = {"view": {_frozenset_chain(150): 1}}
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view(record)

    def test_tuple_chain_key_past_bound_refused(self):
        record = {"view": {_tuple_chain(150): 1}}
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view(record)

    def test_dict_chain_value_past_bound_still_refused(self):
        value = "leaf"
        for _ in range(150):
            value = {"k": value}
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view({"view": value})

    def test_shallow_key_record_still_held(self):
        record = {"view": {_frozenset_chain(3): 1}}
        held = mod04.hold_view(record)
        self.assertTrue(held["held"])


class TestR3026SymbolReadingsMod04Limb(unittest.TestCase):
    def test_cent_sign_reads_as_c(self):
        record = {"\u00a2anary": 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_section_sign_reads_as_s(self):
        record = {"i\u00a7_honest": 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_plus_sign_reads_as_t(self):
        record = {"ground_+ruth": 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_symbol_dressed_key_stripped_from_projection(self):
        state = _state({"\u00a2anary": 1, "clean_field": 2})
        projected = mod04.project_detection_input(state)
        self.assertEqual(projected["feature_values"], {"clean_field": 2})

    def test_plain_and_clean_controls(self):
        self.assertTrue(
            mod04.view_record_carries_barred_field({"canary": 1}))
        self.assertFalse(
            mod04.view_record_carries_barred_field({"clean_field": 1}))


class TestR3051CherokeeCopticReadingsMod04Limb(unittest.TestCase):
    def test_cherokee_m_in_membership(self):
        record = {"\u13b7embership": 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_cherokee_e_in_membership(self):
        record = {"m\u13acmbership": 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_coptic_m_in_membership(self):
        record = {"\u2c99embership": 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_coptic_e_in_membership(self):
        record = {"m\u2c89mbership": 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_cherokee_dressed_key_stripped_from_projection(self):
        state = _state({"\u13b7embership": 1, "clean_field": 2})
        projected = mod04.project_detection_input(state)
        self.assertEqual(projected["feature_values"], {"clean_field": 2})

    def test_coptic_dressed_key_stripped_from_projection(self):
        state = _state({"\u2c99embership": 1, "clean_field": 2})
        projected = mod04.project_detection_input(state)
        self.assertEqual(projected["feature_values"], {"clean_field": 2})

    def test_clean_control_still_clean(self):
        self.assertFalse(
            mod04.view_record_carries_barred_field({"clean_field": 1}))


if __name__ == "__main__":
    unittest.main()
