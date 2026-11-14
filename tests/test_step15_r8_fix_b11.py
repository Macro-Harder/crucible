import unittest

from crucible import mod04, mod06, mod08, mod10, mod11, mod14


def count_distinct_containers(value, _seen=None):
    if _seen is None:
        _seen = set()
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if id(value) in _seen:
            return 0
        _seen.add(id(value))
        total = 1
        if isinstance(value, dict):
            parts = []
            for key, item in dict.items(value):
                parts.append(key)
                parts.append(item)
        else:
            parts = list(value)
        for part in parts:
            total += count_distinct_containers(part, _seen)
        return total
    return 0


def shared_tuple_dag(depth):
    value = (1,)
    for _ in range(depth):
        value = (value, value)
    return value


def shared_set_dag(depth):
    value = [1]
    for _ in range(depth):
        value = [value, value]
    return value


COPY_ACTS = (
    ("mod04", mod04._guarded_copy),
    ("mod06", mod06._undirected_copy),
    ("mod08", mod08._undirected_copy),
    ("mod10", mod10._safe_copy),
    ("mod11", mod11._quoted_copy),
)


class TestR7018CopyActMemoCost(unittest.TestCase):

    def test_shared_tuple_part_is_one_copy_at_each_act(self):
        for name, act in COPY_ACTS:
            with self.subTest(act=name):
                shared = (1, 2)
                result = act([shared, shared])
                self.assertIs(result[0], result[1])

    def test_shared_set_part_is_one_copy_at_each_act(self):
        for name, act in COPY_ACTS:
            with self.subTest(act=name):
                shared = {1, 2}
                result = act([shared, shared])
                self.assertIs(result[0], result[1])

    def test_shared_frozenset_part_is_one_copy_at_each_act(self):
        for name, act in COPY_ACTS:
            with self.subTest(act=name):
                shared = frozenset((1, 2))
                result = act([shared, shared])
                self.assertIs(result[0], result[1])

    def test_shared_tuple_dag_container_count_stays_linear(self):
        for name, act in COPY_ACTS:
            with self.subTest(act=name):
                result = act(shared_tuple_dag(10))
                self.assertLessEqual(count_distinct_containers(result), 12)

    def test_mod14_freeze_shared_set_cost_limb(self):
        shared = {1, 2}
        result = mod14._freeze([shared, shared])
        self.assertIs(result[0], result[1])

    def test_mod14_freeze_shared_frozenset_cost_limb(self):
        shared = frozenset((1, 2))
        result = mod14._freeze([shared, shared])
        self.assertIs(result[0], result[1])

    def test_mod14_freeze_tuple_dag_container_count_stays_linear(self):
        result = mod14._freeze(shared_tuple_dag(10))
        self.assertLessEqual(count_distinct_containers(result), 12)

    def test_controls_plain_and_shared_dict_and_list(self):
        for name, act in COPY_ACTS:
            with self.subTest(act=name):
                shared_dict = {"a": 1}
                shared_list = [1]
                result = act([shared_dict, shared_dict,
                                shared_list, shared_list])
                self.assertIs(result[0], result[1])
                self.assertIs(result[2], result[3])
                self.assertEqual(act({"x": (1, {2})}), {"x": (1, {2})})


class TestR7024Mod14FreezeIdentity(unittest.TestCase):

    def test_shared_set_is_one_copy(self):
        shared = {1, 2}
        result = mod14._freeze([shared, shared])
        self.assertIs(result[0], result[1])

    def test_shared_frozenset_is_one_copy(self):
        shared = frozenset((1, 2))
        result = mod14._freeze([shared, shared])
        self.assertIs(result[0], result[1])

    def test_cyclic_tuple_through_list_is_one_copy(self):
        lst = []
        tup = (lst,)
        lst.append(tup)
        result = mod14._freeze(tup)
        self.assertIs(result[0][0], result)

    def test_cyclic_tuple_through_dict_is_one_copy(self):
        holder = {}
        tup = (holder,)
        holder["t"] = tup
        result = mod14._freeze(tup)
        self.assertIs(result[0]["t"], result)

    def test_controls_shared_dict_list_tuple_and_cyclic_list(self):
        shared = (1, 2)
        result = mod14._freeze([shared, shared])
        self.assertIs(result[0], result[1])
        cyclic = []
        cyclic.append(cyclic)
        frozen = mod14._freeze(cyclic)
        self.assertIs(frozen[0], frozen)


CC_FORMS = ("\x00", "\x07", "\x1b", "\x7f", "\x00\x07\x1b")
FILLER_FORMS = ("\u1160", "\u3164", "\uffa0", "\u1160\u3164\uffa0")
MARK_FORMS = ("\u20dd", "\u0903", "\u20dd\u0903", "\u0301")
# Filler forms in code points: U+1160, U+3164, U+FFA0.
# Mark forms in code points: U+20DD (Me), U+0903 (Mc), U+0301 (Mn).


class TestR7026BlankConditionClass(unittest.TestCase):

    def test_mod10_cc_only_states_no_condition(self):
        for form in CC_FORMS:
            with self.subTest(form=repr(form)):
                self.assertFalse(mod10._has_stated_condition([form]))

    def test_mod10_filler_only_states_no_condition(self):
        for form in FILLER_FORMS:
            with self.subTest(form=repr(form)):
                self.assertFalse(mod10._has_stated_condition([form]))

    def test_mod10_lone_mark_only_states_no_condition(self):
        for form in MARK_FORMS:
            with self.subTest(form=repr(form)):
                self.assertFalse(mod10._has_stated_condition([form]))

    def test_mod14_cc_only_states_no_condition(self):
        for form in CC_FORMS:
            with self.subTest(form=repr(form)):
                self.assertFalse(mod14._has_stated_condition([form]))
                self.assertEqual(mod14._stated_text(form), "")

    def test_mod14_filler_only_states_no_condition(self):
        for form in FILLER_FORMS:
            with self.subTest(form=repr(form)):
                self.assertFalse(mod14._has_stated_condition([form]))
                self.assertEqual(mod14._stated_text(form), "")

    def test_mod14_lone_mark_only_states_no_condition(self):
        for form in MARK_FORMS:
            with self.subTest(form=repr(form)):
                self.assertFalse(mod14._has_stated_condition([form]))
                self.assertEqual(mod14._stated_text(form), "")

    def test_mod10_promotion_with_cc_only_condition_refused(self):
        record = {"retention_tier": "Tier 1"}
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 2",
                inputs={"flag_conditions_fired": ["\x07"]})

    def test_controls_readable_conditions_still_state(self):
        self.assertTrue(mod10._has_stated_condition(["real condition"]))
        self.assertTrue(mod14._has_stated_condition(["real condition"]))
        self.assertTrue(mod10._has_stated_condition(["\x07 real"]))
        self.assertTrue(mod14._has_stated_condition(["ᅠ real"]))
        self.assertFalse(mod10._has_stated_condition(["​"]))
        self.assertFalse(mod14._has_stated_condition(["⠀"]))


if __name__ == "__main__":
    unittest.main()
