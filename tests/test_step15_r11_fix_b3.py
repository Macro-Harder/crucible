"""Pins for fix wave 10, Builder 3, MOD-03 limbs.

Rows: R10-002 (carrying and stripping gates routing container
keys to a str only helper), R10-003 MOD-03 limb (joined reading
of a container key), R10-007 MOD-03 limb (memoryview and
bytearray stored text in the helper), and R10-008 MOD-03 limb
(the iterative container walk standing at depth 2000).
"""

import unittest

from crucible import mod03


class TestR10002BytesPartInTupleKey(unittest.TestCase):

    def test_predicate_control_bytes_single_tuple(self):
        self.assertTrue(mod03._is_barred_key((b"ground_truth",)))

    def test_carries_bytes_tuple_key(self):
        self.assertTrue(
            mod03.record_carries_ground_truth({(b"ground_truth",): 1}))

    def test_carries_bytes_tuple_key_membership(self):
        self.assertTrue(
            mod03.record_carries_ground_truth({(b"membership",): 1}))

    def test_carries_bytes_part_beside_str_part(self):
        self.assertTrue(mod03.record_carries_ground_truth(
            {(b"ground_truth", "x"): 1}))

    def test_carries_bytes_tuple_key_nested_in_value(self):
        record = {"features": {(b"canary",): "x"}}
        self.assertTrue(mod03.record_carries_ground_truth(record))

    def test_validate_detection_refuses_bytes_tuple_key(self):
        self.assertFalse(
            mod03.validate_detection_input({(b"ground_truth",): 1}))

    def test_validate_adjudication_refuses_bytes_tuple_key(self):
        self.assertFalse(
            mod03.validate_adjudication_input({(b"membership",): 1}))

    def test_strip_removes_bytes_tuple_key(self):
        record = {(b"ground_truth",): 1, "activity": 2}
        self.assertEqual({"activity": 2}, mod03.strip_ground_truth(record))

    def test_strip_removes_bytes_tuple_key_nested(self):
        record = {"features": {(b"membership",): 1, "activity": 2}}
        stripped = mod03.strip_ground_truth(record)
        self.assertEqual({"features": {"activity": 2}}, stripped)


class TestR10003JoinedContainerReading(unittest.TestCase):

    def test_joined_ground_truth(self):
        self.assertTrue(mod03._is_barred_key(("ground", "truth")))

    def test_joined_ground_underscore_truth(self):
        self.assertTrue(mod03._is_barred_key(("ground", "_truth")))

    def test_joined_membership_split(self):
        self.assertTrue(mod03._is_barred_key(("mem", "bership")))

    def test_joined_membership_split_two_even_parts(self):
        self.assertTrue(mod03._is_barred_key(("member", "ship")))

    def test_joined_canary_split(self):
        self.assertTrue(mod03._is_barred_key(("can", "ary")))

    def test_joined_three_parts(self):
        self.assertTrue(mod03._is_barred_key(("gro", "und_tr", "uth")))

    def test_joined_separator_as_own_part(self):
        self.assertTrue(mod03._is_barred_key(("ground", "_", "truth")))

    def test_joined_bytes_parts(self):
        self.assertTrue(mod03._is_barred_key((b"ground", b"truth")))

    def test_joined_mixed_str_and_bytes_parts(self):
        self.assertTrue(mod03._is_barred_key(("ground", b"truth")))

    def test_joined_list_key_form(self):
        self.assertTrue(mod03._is_barred_key(["ground", "truth"]))

    def test_joined_nested_container(self):
        self.assertTrue(mod03._is_barred_key((("ground", "truth"),)))

    def test_joined_nested_container_beside_clean_part(self):
        self.assertTrue(mod03._is_barred_key((("la", "bel"), "x")))

    def test_joined_public_carries(self):
        self.assertTrue(mod03.record_carries_ground_truth(
            {("ground", "truth"): 1}))

    def test_joined_public_validate_refused(self):
        self.assertFalse(mod03.validate_detection_input(
            {("mem", "bership"): 1}))

    def test_joined_public_strip_removes(self):
        record = {("ground", "truth"): 1, "activity": 2}
        self.assertEqual({"activity": 2}, mod03.strip_ground_truth(record))

    def test_joined_clean_control_not_barred(self):
        self.assertFalse(mod03._is_barred_key(("ground", "clean")))
        self.assertFalse(mod03._is_barred_key(("acti", "vity")))
        self.assertFalse(mod03.record_carries_ground_truth(
            {("acti", "vity"): 1}))


class TestR10007MemoryviewAndBytearray(unittest.TestCase):

    def test_stored_text_memoryview(self):
        self.assertEqual(
            "ground_truth", mod03._stored_text(memoryview(b"ground_truth")))

    def test_stored_text_bytearray(self):
        self.assertEqual(
            "ground_truth", mod03._stored_text(bytearray(b"ground_truth")))

    def test_stored_text_memoryview_clean(self):
        self.assertEqual(
            "activity", mod03._stored_text(memoryview(b"activity")))

    def test_memoryview_bare_key_barred(self):
        self.assertTrue(mod03._is_barred_key(memoryview(b"membership")))
        self.assertTrue(mod03._is_barred_key(memoryview(b"ground_truth")))

    def test_memoryview_key_public_gates(self):
        key = memoryview(b"membership")
        self.assertTrue(mod03.record_carries_ground_truth({key: 1}))
        self.assertFalse(mod03.validate_detection_input({key: 1}))
        self.assertEqual(
            {"activity": 2},
            mod03.strip_ground_truth({key: 1, "activity": 2}))

    def test_memoryview_part_in_tuple_key(self):
        key = (memoryview(b"ground_truth"),)
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(mod03.record_carries_ground_truth({key: 1}))
        record = {key: 1, "activity": 2}
        self.assertEqual({"activity": 2}, mod03.strip_ground_truth(record))

    def test_memoryview_split_joined(self):
        key = (memoryview(b"gro"), memoryview(b"und_truth"))
        self.assertTrue(mod03._is_barred_key(key))

    def test_bytearray_part_in_list_key(self):
        self.assertTrue(mod03._is_barred_key([bytearray(b"membership")]))

    def test_bytearray_split_joined(self):
        key = (bytearray(b"ground"), bytearray(b"truth"))
        self.assertTrue(mod03._is_barred_key(key))

    def test_memoryview_and_bytearray_clean_controls(self):
        self.assertFalse(mod03._is_barred_key(memoryview(b"activity")))
        self.assertFalse(mod03._is_barred_key([bytearray(b"activity")]))


class TestR10008DepthStanding(unittest.TestCase):

    def test_depth_2000_barred_leaf(self):
        key = "membership"
        for _ in range(2000):
            key = (key,)
        self.assertTrue(mod03._is_barred_key(key))

    def test_depth_2000_clean_leaf(self):
        key = "clean"
        for _ in range(2000):
            key = (key,)
        self.assertFalse(mod03._is_barred_key(key))

    def test_depth_500_joined_leaf(self):
        key = ("ground", "truth")
        for _ in range(500):
            key = (key,)
        self.assertTrue(mod03._is_barred_key(key))

    def test_depth_500_joined_clean_leaf(self):
        key = ("acti", "vity")
        for _ in range(500):
            key = (key,)
        self.assertFalse(mod03._is_barred_key(key))


class TestControlsKept(unittest.TestCase):

    def test_plain_controls(self):
        self.assertTrue(mod03._is_barred_key("membership"))
        self.assertTrue(mod03._is_barred_key(b"membership"))
        self.assertTrue(mod03._is_barred_key(("membership", "x")))
        self.assertFalse(mod03._is_barred_key("activity"))
        self.assertFalse(mod03._is_barred_key(("activity", "x")))

    def test_plain_public_controls(self):
        self.assertTrue(
            mod03.record_carries_ground_truth({"membership": 1}))
        self.assertEqual(
            {"activity": 2},
            mod03.strip_ground_truth({"membership": 1, "activity": 2}))
        self.assertTrue(
            mod03.validate_detection_input({"activity": 2}))


if __name__ == "__main__":
    unittest.main()
