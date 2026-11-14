"""Fix wave 6 pins, Builder 3: MOD-03 and MOD-04 rows of Round 6.

Rows pinned: R6-021, R6-022, R6-025, R6-020 (MOD-03 limb),
R6-019 (MOD-03 and MOD-04 limbs), R6-033, R6-009 (MOD-04 limb),
R6-010 (MOD-03 and MOD-04 limbs), R6-007 (MOD-04 limb).
Each charged defect form fails on the unmodified modules and
passes on the cured copy; lawful controls pass both ways.
"""
import time
import unittest

from crucible import mod03, mod04


BARRED_DICT = {"amount": 10, "currency": "USD"}


class LyingName(str):
    """A text value storing one name whose hash and equality
    readings answer as another name."""

    def __new__(cls, stored, answers_as):
        obj = str.__new__(cls, stored)
        obj._answers_as = answers_as
        return obj

    def __hash__(self):
        return str.__hash__(self._answers_as)

    def __eq__(self, other):
        return str.__eq__(self._answers_as, other)

    def __ne__(self, other):
        return not str.__eq__(self._answers_as, other)


class LyingGetEdge(dict):
    """A dict edge storing a cross farm pair whose own get
    reading supplies an internal pair."""

    def get(self, key, default=None):
        if key == "voucher":
            return "a"
        if key == "vouchee":
            return "a"
        return default


class EmptyIterList(list):
    def __iter__(self):
        return iter(())


class LyingLenTuple(tuple):
    def __len__(self):
        return 3


class LyingItemList(list):
    """Stores (a, c); its item reading answers a at 0 and b at 1."""

    def __getitem__(self, index):
        return ("a", "b")[index]


class LyingItemTuple(tuple):
    def __getitem__(self, index):
        return ("a", "b")[index]


class EmptyIterTuple(tuple):
    def __iter__(self):
        return iter(())


class ListFedSet(set):
    def __new__(cls, items=()):
        if isinstance(items, list):
            return dict(BARRED_DICT)
        return set.__new__(cls)


class ListFedFrozenset(frozenset):
    def __new__(cls, items=()):
        if isinstance(items, list):
            return dict(BARRED_DICT)
        return frozenset.__new__(cls, items)


class DeepcopyCarrier:
    def __deepcopy__(self, memo):
        return dict(BARRED_DICT)


def chain(containers, leaf="leaf"):
    value = leaf
    for _ in range(containers):
        value = [value]
    return value


def shared_shape(depth):
    value = {"leaf": 1}
    for _ in range(depth):
        value = [value, value]
    return value


class TestR6021FarmMembershipStoredText(unittest.TestCase):
    def test_dict_edge_lying_voucher_counts_cross(self):
        result = mod03.construct_farm(
            ["a", "b"], 1,
            [{"voucher": LyingName("a", "b"), "vouchee": "b"}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_tuple_edge_lying_voucher_counts_cross(self):
        result = mod03.construct_farm(
            ["a", "b"], 1, [(LyingName("a", "b"), "b")])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_dict_edge_non_member_names_lying_as_members(self):
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": LyingName("zzz", "a"),
              "vouchee": LyingName("yyy", "b")}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_plain_cross_pair_control(self):
        result = mod03.construct_farm(["a", "b"], 1, [("a", "b")])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_plain_internal_pair_control(self):
        result = mod03.construct_farm(["a", "b"], 1, [("a", "a")])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_lying_get_dict_edge_control(self):
        edge = LyingGetEdge({"voucher": "a", "vouchee": "b"})
        result = mod03.construct_farm(["a", "b"], 1, [edge])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})


class TestR6022FarmBaseReadings(unittest.TestCase):
    def test_edge_set_empty_iteration_still_counted(self):
        edges = EmptyIterList([("a", "a")])
        result = mod03.construct_farm(["a", "b"], 1, edges)
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_member_set_empty_iteration_still_builds_farms(self):
        members = EmptyIterList(["a", "b"])
        result = mod03.construct_farm(members, 1, [("a", "a")])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})
        self.assertEqual(
            [farm["farm_id"] for farm in result["farms"]],
            ["farm-0", "farm-1"])

    def test_tuple_edge_lying_length_still_a_pair(self):
        edge = LyingLenTuple(("a", "a"))
        result = mod03.construct_farm(["a", "b"], 1, [edge])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_list_edge_lying_items_read_by_storage(self):
        edge = LyingItemList(["a", "c"])
        result = mod03.construct_farm(["a", "b", "c", "d"], 2, [edge])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_tuple_edge_lying_items_read_by_storage(self):
        edge = LyingItemTuple(("a", "c"))
        result = mod03.construct_farm(["a", "b", "c", "d"], 2, [edge])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_empty_iteration_tuple_edge_control(self):
        edge = EmptyIterTuple(("a", "a"))
        result = mod03.construct_farm(["a", "b"], 1, [edge])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})


class TestR6025CyrillicReadings(unittest.TestCase):
    def test_yery_dressed_canary_barred(self):
        self.assertTrue(mod03._is_barred_key("canar\u044b"))

    def test_capital_yery_dressed_canary_barred(self):
        self.assertTrue(mod03._is_barred_key("canar\u042b"))

    def test_yery_record_carries_ground_truth(self):
        self.assertTrue(
            mod03.record_carries_ground_truth({"canar\u044b": 1}))

    def test_yu_fold_reading(self):
        self.assertIn("yu", mod03._folded_readings("\u044e"))

    def test_ya_fold_reading(self):
        self.assertIn("ya", mod03._folded_readings("\u044f"))

    def test_plain_canary_control(self):
        self.assertTrue(mod03._is_barred_key("canary"))

    def test_invented_and_lawful_controls(self):
        self.assertFalse(mod03._is_barred_key("blorple"))
        self.assertFalse(mod03._is_barred_key("summary"))


CORE = "\u0441a\u043dary"


class TestR6010CountingBasis(unittest.TestCase):
    def test_eta_eleven_mod03_barred(self):
        self.assertTrue(mod03._is_barred_key(CORE + "\u03b7" * 11))

    def test_theta_eleven_mod03_barred(self):
        self.assertTrue(mod03._is_barred_key(CORE + "\u03b8" * 11))

    def test_eta_eleven_mod04_barred_control(self):
        self.assertTrue(mod04._is_barred_key(CORE + "\u03b7" * 11))

    def test_theta_eleven_mod04_barred_control(self):
        self.assertTrue(mod04._is_barred_key(CORE + "\u03b8" * 11))

    def test_eta_ten_both_barred_control(self):
        self.assertTrue(mod03._is_barred_key(CORE + "\u03b7" * 10))
        self.assertTrue(mod04._is_barred_key(CORE + "\u03b7" * 10))

    def test_theta_ten_both_barred_control(self):
        self.assertTrue(mod03._is_barred_key(CORE + "\u03b8" * 10))
        self.assertTrue(mod04._is_barred_key(CORE + "\u03b8" * 10))

    def test_core_alone_both_barred_control(self):
        self.assertTrue(mod03._is_barred_key(CORE))
        self.assertTrue(mod04._is_barred_key(CORE))

    def test_short_i_and_chi_eleven_both_barred_control(self):
        self.assertTrue(mod03._is_barred_key(CORE + "\u0439" * 11))
        self.assertTrue(mod04._is_barred_key(CORE + "\u0439" * 11))
        self.assertTrue(mod03._is_barred_key(CORE + "\u03c7" * 11))
        self.assertTrue(mod04._is_barred_key(CORE + "\u03c7" * 11))


TRIPLE04 = "\u0441" + "4" + "\u043d" + "ar9y"


class TestR6009Mod04CombinedFold(unittest.TestCase):
    def test_triple_key_barred_at_mod04(self):
        self.assertTrue(mod04._is_barred_key(TRIPLE04))

    def test_triple_key_stripped_from_projection(self):
        projected = mod04.project_detection_input({
            "agent_identifier": "a", "day": 1,
            "feature_values": {TRIPLE04: 1}, "rule_records": []})
        self.assertEqual(projected["feature_values"], {})

    def test_triple_key_barred_at_mod03_control(self):
        self.assertTrue(mod03._is_barred_key(TRIPLE04))

    def test_one_and_two_kind_controls_barred(self):
        for key in ("canary", "c4nary", "cana9ry",
                    "\u0441a\u043dary", "\u04414\u043dary",
                    "\u0441a\u043dar9y"):
            self.assertTrue(mod04._is_barred_key(key), key)

    def test_lawful_and_invented_controls(self):
        self.assertFalse(mod04._is_barred_key("summary"))
        self.assertFalse(mod04._is_barred_key("blorple9"))
        projected = mod04.project_detection_input({
            "agent_identifier": "a", "day": 1,
            "feature_values": {"summary": 1}, "rule_records": []})
        self.assertEqual(projected["feature_values"], {"summary": 1})


def projection(features=None, rule_records=None):
    return mod04.project_detection_input({
        "agent_identifier": "a", "day": 1,
        "feature_values": features if features is not None else {},
        "rule_records": rule_records if rule_records is not None else []})


class TestR6033CleaningDepthBasis(unittest.TestCase):
    def test_chain_101_rule_record_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            projection(rule_records=[chain(101)])

    def test_chain_101_feature_value_refused_control(self):
        with self.assertRaises(mod04.NamedFailure):
            projection(features={"k": chain(101)})

    def test_chain_100_both_delivered_control(self):
        self.assertEqual(
            len(projection(features={"k": chain(100)})["feature_values"]["k"]),
            1)
        self.assertEqual(
            len(projection(rule_records=[chain(100)])["rule_records"][0]), 1)

    def test_chain_102_both_refused_control(self):
        with self.assertRaises(mod04.NamedFailure):
            projection(features={"k": chain(102)})
        with self.assertRaises(mod04.NamedFailure):
            projection(rule_records=[chain(102)])


class TestR6007Mod04Freeze(unittest.TestCase):
    def test_list_fed_set_freezes_as_set(self):
        frozen = mod04._freeze({"wrap": ListFedSet((1, 2))})
        self.assertEqual(frozen, {"wrap": {1, 2}})
        self.assertIs(type(frozen["wrap"]), set)

    def test_list_fed_frozenset_freezes_as_frozenset(self):
        frozen = mod04._freeze({"wrap": ListFedFrozenset((1, 2))})
        self.assertEqual(frozen, {"wrap": frozenset((1, 2))})
        self.assertIs(type(frozen["wrap"]), frozenset)

    def test_deepcopy_carrier_freezes_as_itself(self):
        carrier = DeepcopyCarrier()
        frozen = mod04._freeze({"wrap": carrier})
        self.assertIs(frozen["wrap"], carrier)

    def test_public_act_delivers_plain_set(self):
        record = mod04.run_record_with_order(
            {"payload": ListFedSet((1, 2))}, "order-1")
        self.assertEqual(record["payload"], {1, 2})
        self.assertIs(type(record["payload"]), set)
        self.assertEqual(record["scheduling_order_identifier"], "order-1")

    def test_plain_containers_control(self):
        frozen = mod04._freeze({"s": {1, 2}, "l": [1, {"a": (3,)}]})
        self.assertEqual(frozen, {"s": {1, 2}, "l": [1, {"a": (3,)}]})


class TestR6019RewalkStanding(unittest.TestCase):
    def test_rule_state_shared_shape_fast(self):
        shape = shared_shape(20)
        start = time.monotonic()
        result = mod03._value_carries_rule_state(shape)
        elapsed = time.monotonic() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 8.0)

    def test_strip_shared_shape_fast(self):
        shape = shared_shape(18)
        start = time.monotonic()
        result = mod03._strip_ground_truth_value(shape)
        elapsed = time.monotonic() - start
        node = result
        for _ in range(18):
            node = node[0]
        self.assertEqual(node, {"leaf": 1})
        self.assertLess(elapsed, 8.0)

    def test_clean_shared_shape_fast(self):
        shape = shared_shape(18)
        start = time.monotonic()
        result = mod04._clean_value(shape)
        elapsed = time.monotonic() - start
        node = result
        for _ in range(18):
            node = node[0]
        self.assertEqual(node, {"leaf": 1})
        self.assertLess(elapsed, 8.0)

    def test_rule_state_shared_barred_control(self):
        shared = {"reputation": 3}
        self.assertFalse(
            mod03.validate_generator_output(
                {"a": shared, "b": shared}))

    def test_strip_shared_barred_both_positions_control(self):
        shared = {"canary": 1, "ok": 2}
        stripped = mod03._strip_ground_truth_value(
            {"a": shared, "b": shared})
        self.assertEqual(stripped, {"a": {"ok": 2}, "b": {"ok": 2}})

    def test_clean_shared_barred_both_positions_control(self):
        shared = {"canary": 1, "ok": 2}
        cleaned = mod04._clean_value({"x": shared, "y": shared})
        self.assertEqual(cleaned, {"x": {"ok": 2}, "y": {"ok": 2}})

    def test_cycle_controls(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._value_carries_rule_state(cyclic)
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._strip_ground_truth_value(cyclic)
        with self.assertRaises(mod04.NamedFailure):
            mod04._clean_value(cyclic)


class TestR6020GroundTruthDepthStanding(unittest.TestCase):
    def setUp(self):
        self.shallow = chain(6, "x")
        self.deep102 = self.shallow
        for _ in range(96):
            self.deep102 = [self.deep102]
        self.deep100 = self.shallow
        for _ in range(94):
            self.deep100 = [self.deep100]

    def test_shallow_first_shared_root_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._value_carries_ground_truth(
                {"a": self.shallow, "b": self.deep102})

    def test_shallow_first_public_act_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.validate_detection_input(
                {"a": self.shallow, "b": self.deep102})

    def test_deep_first_other_order_refused_control(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._value_carries_ground_truth(
                {"b": self.deep102, "a": self.shallow})

    def test_deep_alone_refused_control(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03._value_carries_ground_truth({"b": self.deep102})

    def test_shallow_alone_control(self):
        self.assertFalse(
            mod03._value_carries_ground_truth({"a": self.shallow}))

    def test_longest_path_100_within_bound_control(self):
        root = {"a": self.shallow, "b": self.deep100}
        self.assertFalse(mod03._value_carries_ground_truth(root))
        self.assertTrue(mod03.validate_detection_input(root))


if __name__ == "__main__":
    unittest.main()
