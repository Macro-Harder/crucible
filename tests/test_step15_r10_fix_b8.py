"""Step 15, second run, fix wave 9 pins for Builder 8.

Each defect test pins one charged defect instance from the
Round 9 register on the MOD-12 loci in crucible/mod12.py:
R9-021 and R9-022 at seal_family_record, and R9-028 at
admit_claim. Control tests stand both ways beside each family,
including the _freeze identity standings and the MOD-12 seal
controls the Round 9 Builder 12 pins carry. Values are
simulated and test values only.
"""
import unittest

from crucible import mod12


def list_chain(count):
    value = "leaf"
    for _ in range(count):
        value = [value]
    return value


def chain_depth(value):
    depth = 0
    while isinstance(value, list):
        depth += 1
        value = value[0]
    return depth


def cyclic_list():
    value = []
    value.append(value)
    return value


class RaisingGetDict(dict):
    """A dict subclass storing a record whose own get reading
    raises instead of answering."""

    def get(self, key, default=None):
        raise RuntimeError("hostile get reading")


class TruthRaising:
    """An object whose truth test raises."""

    def __bool__(self):
        raise RuntimeError("hostile truth reading")


class TruthRaisingGetDict(dict):
    """A dict subclass storing a record whose own get reading
    returns an object whose truth test raises."""

    def get(self, key, default=None):
        return TruthRaising()


class ReportingGetDict(dict):
    """A dict subclass storing one record and reporting other
    values through its own get reading for named keys."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = dict(reported)

    def get(self, key, default=None):
        if key in self._reported:
            return self._reported[key]
        return dict.get(self, key, default)


class TestR9021SealVersionAndHashReadings(unittest.TestCase):

    def test_defect_reported_past_bound_version_seals_stored(self):
        reported = list_chain(150)
        record = ReportingGetDict(
            mod12.make_family_record(),
            {"family_version": reported})
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 1")
        self.assertEqual(sealed["seal_version"], "version 1")
        self.assertIsNot(sealed["seal"]["version"], reported)

    def test_defect_reported_past_bound_hash_seals_stored(self):
        reported = list_chain(150)
        record = ReportingGetDict(
            mod12.make_family_record(),
            {"family_manifest_hash": reported})
        sealed = mod12.seal_family_record(record)
        self.assertEqual(
            sealed["seal"]["hash"],
            "manifest hash supplied as a record value, not computed")
        self.assertEqual(
            sealed["seal_hash"],
            "manifest hash supplied as a record value, not computed")
        self.assertIsNot(sealed["seal"]["hash"], reported)

    def test_defect_reported_cyclic_version_seals_stored(self):
        reported = cyclic_list()
        record = ReportingGetDict(
            mod12.make_family_record(),
            {"family_version": reported})
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 1")
        self.assertIsNot(sealed["seal"]["version"], reported)

    def test_defect_reported_cyclic_hash_seals_stored(self):
        reported = cyclic_list()
        record = ReportingGetDict(
            mod12.make_family_record(),
            {"family_manifest_hash": reported})
        sealed = mod12.seal_family_record(record)
        self.assertEqual(
            sealed["seal_hash"],
            "manifest hash supplied as a record value, not computed")
        self.assertIsNot(sealed["seal"]["hash"], reported)

    def test_defect_reported_text_version_seals_stored_text(self):
        record = ReportingGetDict(
            mod12.make_family_record(),
            {"family_version": "REPORTED-VERSION",
             "family_manifest_hash": "REPORTED-HASH"})
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 1")
        self.assertEqual(
            sealed["seal"]["hash"],
            "manifest hash supplied as a record value, not computed")

    def test_defect_stored_version_value_copied_not_sealed_by_identity(self):
        stored = list_chain(50)
        record = mod12.make_family_record()
        record["family_version"] = stored
        sealed = mod12.seal_family_record(record)
        self.assertEqual(chain_depth(sealed["seal"]["version"]), 50)
        self.assertIsNot(sealed["seal"]["version"], stored)
        self.assertIsNot(sealed["seal_version"], stored)

    def test_defect_stored_hash_value_copied_not_sealed_by_identity(self):
        stored = list_chain(50)
        record = mod12.make_family_record()
        record["family_manifest_hash"] = stored
        sealed = mod12.seal_family_record(record)
        self.assertEqual(chain_depth(sealed["seal"]["hash"]), 50)
        self.assertIsNot(sealed["seal"]["hash"], stored)
        self.assertIsNot(sealed["seal_hash"], stored)


class TestR9022SealGuardBeforeHandedReadings(unittest.TestCase):

    def test_defect_past_bound_raising_get_meets_named_bound_refusal(self):
        stored = mod12.make_family_record()
        stored["deep_field"] = list_chain(120)
        record = RaisingGetDict(stored)
        with self.assertRaises(mod12.NamedControllerFailure) as caught:
            mod12.seal_family_record(record)
        self.assertIn("deeper than the stated bound", str(caught.exception))

    def test_defect_past_bound_truth_raising_get_meets_named_refusal(self):
        stored = mod12.make_family_record()
        stored["deep_field"] = list_chain(120)
        record = TruthRaisingGetDict(stored)
        with self.assertRaises(mod12.NamedControllerFailure) as caught:
            mod12.seal_family_record(record)
        self.assertIn("deeper than the stated bound", str(caught.exception))

    def test_defect_raising_get_complete_record_seals_from_stored(self):
        record = RaisingGetDict(mod12.make_family_record())
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])
        self.assertEqual(sealed["seal"]["version"], "version 1")
        self.assertEqual(
            sealed["seal"]["hash"],
            "manifest hash supplied as a record value, not computed")

    def test_defect_reported_completeness_on_empty_stored_refused_named(self):
        reported = {
            item: "reported present"
            for item in mod12.FAMILY_COMPLETENESS_ITEMS}
        record = ReportingGetDict({}, reported)
        with self.assertRaises(mod12.NamedControllerFailure) as caught:
            mod12.seal_family_record(record)
        self.assertIn("completeness items missing", str(caught.exception))


class TestR9028AdmitClaimBoundGuard(unittest.TestCase):

    def test_defect_past_bound_claim_refused_in_named_form(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.admit_claim({}, claim=list_chain(120))

    def test_defect_deep_claim_refused_named_not_bare_recursion(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.admit_claim({}, claim=list_chain(2000))

    def test_defect_cyclic_claim_refused_in_named_form(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.admit_claim({}, claim=cyclic_list())

    def test_defect_cyclic_claim_in_dict_refused_in_named_form(self):
        claim = {"name": "claim"}
        claim["self"] = claim
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.admit_claim({}, claim=claim)


class TestControlsStandingBothWays(unittest.TestCase):

    def test_control_plain_record_seals_with_stored_version_and_hash(self):
        record = mod12.make_family_record()
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])
        self.assertEqual(sealed["seal"]["version"], "version 1")
        self.assertEqual(
            sealed["seal"]["hash"],
            "manifest hash supplied as a record value, not computed")
        self.assertEqual(sealed["seal_version"], sealed["seal"]["version"])
        self.assertEqual(sealed["seal_hash"], sealed["seal"]["hash"])
        self.assertEqual(
            sealed["sweep_manifest"]["family_version"], "version 1")

    def test_control_custom_stored_version_and_hash_seal_as_stored(self):
        record = mod12.make_family_record()
        record["family_version"] = "version 7"
        record["family_manifest_hash"] = "stored hash value"
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["version"], "version 7")
        self.assertEqual(sealed["seal"]["hash"], "stored hash value")

    def test_control_missing_completeness_item_refused_named(self):
        record = mod12.make_family_record()
        del record["farm size steps"]
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)

    def test_control_empty_record_refused_named(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record({})

    def test_control_past_bound_plain_record_refused_named(self):
        for count in (120, 2000):
            with self.subTest(count=count):
                record = mod12.make_family_record()
                record["deep_field"] = list_chain(count)
                with self.assertRaises(mod12.NamedControllerFailure):
                    mod12.seal_family_record(record)

    def test_control_cyclic_plain_record_refused_named(self):
        record = mod12.make_family_record()
        record["deep_field"] = cyclic_list()
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)

    def test_control_within_bound_seal_copies_whole(self):
        record = mod12.make_family_record()
        record["deep_field"] = list_chain(50)
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])
        self.assertEqual(chain_depth(sealed["deep_field"]), 50)
        boundary = mod12.make_family_record()
        boundary["deep_field"] = list_chain(100)
        sealed_boundary = mod12.seal_family_record(boundary)
        self.assertTrue(sealed_boundary["sealed"])
        self.assertEqual(chain_depth(sealed_boundary["deep_field"]), 100)
        shared = [1, 2]
        record = mod12.make_family_record()
        record["first"] = shared
        record["second"] = shared
        sealed = mod12.seal_family_record(record)
        self.assertIs(sealed["first"], sealed["second"])
        self.assertEqual(sealed["first"], [1, 2])

    def test_control_freeze_identity_standings(self):
        shared_set = {1, 2}
        result = mod12._freeze([shared_set, shared_set])
        self.assertIs(result[0], result[1])
        shared_frozen = frozenset((1, 2))
        result = mod12._freeze([shared_frozen, shared_frozen])
        self.assertIs(result[0], result[1])
        shared_tuple = (1, 2)
        result = mod12._freeze([shared_tuple, shared_tuple])
        self.assertIs(result[0], result[1])
        holder = []
        cyclic = (holder,)
        holder.append(cyclic)
        copied = mod12._freeze(holder)
        self.assertIs(copied[0][0], copied)

    def test_control_admit_plain_claim_copied(self):
        claim = {"name": "plain claim", "parts": [1, 2]}
        admitted = mod12.admit_claim({}, claim=claim)
        self.assertTrue(admitted["admitted"])
        self.assertEqual(admitted["claim"], claim)
        self.assertIsNot(admitted["claim"], claim)
        self.assertIsNot(admitted["claim"]["parts"], claim["parts"])

    def test_control_admit_within_bound_claim_copies_whole(self):
        for count in (50, 100):
            with self.subTest(count=count):
                admitted = mod12.admit_claim({}, claim=list_chain(count))
                self.assertTrue(admitted["admitted"])
                self.assertEqual(chain_depth(admitted["claim"]), count)

    def test_control_admit_shared_claim_parts_keep_identity(self):
        shared = [1, 2]
        admitted = mod12.admit_claim(
            {}, claim={"first": shared, "second": shared})
        self.assertIs(admitted["claim"]["first"], admitted["claim"]["second"])
        self.assertEqual(admitted["claim"]["first"], [1, 2])

    def test_control_admit_no_claim_and_text_claim(self):
        self.assertEqual(
            mod12.admit_claim({}), {"admitted": True, "claim": None})
        self.assertEqual(
            mod12.admit_claim({}, claim="a claim"),
            {"admitted": True, "claim": "a claim"})

    def test_control_admit_after_results_seen_still_barred_named(self):
        family = mod12.make_family_record()
        family["results_seen"] = True
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.admit_claim(family, claim={"name": "late claim"})


if __name__ == "__main__":
    unittest.main()
