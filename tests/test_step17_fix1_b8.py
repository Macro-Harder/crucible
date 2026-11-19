"""Step 17 fix wave 1, Builder 8 tests (Slice 8).

Rows FW-38 and FW-39. Each defect test reproduces its filing
defect on the base tree at product head
9f938470807f90b7c8c6d9882fde1105c807e0a1 and passes on the
fixed tree. Control tests pin the standings that already hold.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod08 as mod08

SEPARATIONS = [
    "authorship separation",
    "knowledge separation",
    "record separation",
]


def delivered(kind):
    return {"event": {"kind": kind}}


def frozen_set():
    sealed_set = mod08.create_sealed_set()
    mod08.freeze_sealed_set(sealed_set)
    return sealed_set


class TestFW38DeliveryCompleteness(unittest.TestCase):
    def test_defect_filing_case_processing_type_not_counted(self):
        events = [
            {"kind": "gossip intake"},
            {"kind": "work completion"},
        ]
        deliveries = [delivered("work completion")]
        self.assertTrue(
            mod04.delivery_completeness(events, deliveries))

    def test_defect_every_processing_type_excluded(self):
        for processing in mod04.PROCESSING_TYPES:
            events = [
                {"kind": processing},
                {"kind": "work completion"},
            ]
            deliveries = [delivered("work completion")]
            self.assertTrue(
                mod04.delivery_completeness(events, deliveries),
                processing)

    def test_defect_processing_only_day_needs_no_delivery(self):
        events = [{"kind": "trust evaluation"}]
        self.assertTrue(mod04.delivery_completeness(events, []))

    def test_defect_processing_delivery_stands_outside_count(self):
        events = [{"kind": "work completion"}]
        deliveries = [
            delivered("work completion"),
            delivered("pairwise collusion evaluation"),
        ]
        self.assertTrue(
            mod04.delivery_completeness(events, deliveries))

    def test_control_generated_event_undelivered_is_incomplete(self):
        events = [
            {"kind": "work completion"},
            {"kind": "day_close"},
        ]
        deliveries = [delivered("work completion")]
        self.assertFalse(
            mod04.delivery_completeness(events, deliveries))

    def test_control_duplicate_deliveries_do_not_complete(self):
        events = [
            {"kind": "work completion"},
            {"kind": "work completion"},
        ]
        deliveries = [delivered("work completion")] * 3
        self.assertFalse(
            mod04.delivery_completeness(events, deliveries))

    def test_control_empty_day_is_complete(self):
        self.assertTrue(mod04.delivery_completeness([], []))

    def test_control_exact_delivery_is_complete(self):
        events = [{"kind": "work completion"}]
        deliveries = [delivered("work completion")]
        self.assertTrue(
            mod04.delivery_completeness(events, deliveries))


class TestFW39AuthorSealedClass(unittest.TestCase):
    def test_defect_duplicate_identifier_refused(self):
        sealed_set = frozen_set()
        mod08.author_sealed_class(
            sealed_set, "sleeper class", "id-1", SEPARATIONS)
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.author_sealed_class(
                sealed_set, "sleeper class", "id-1", SEPARATIONS)
        self.assertIn("id-1", str(caught.exception))
        self.assertEqual(len(sealed_set["authored"]), 1)

    def test_defect_duplicate_identifier_refused_across_kinds(self):
        sealed_set = frozen_set()
        mod08.author_sealed_class(
            sealed_set, "sleeper class", "id-1", SEPARATIONS)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                sealed_set, "honest challenge variant", "id-1",
                SEPARATIONS)
        self.assertEqual(len(sealed_set["authored"]), 1)

    def test_defect_filing_sequence_seals_over_distinct_only(self):
        sealed_set = frozen_set()
        mod08.author_sealed_class(
            sealed_set, "sleeper class", "id-1", SEPARATIONS)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                sealed_set, "sleeper class", "id-1", SEPARATIONS)
        mod08.author_sealed_class(
            sealed_set, "honest challenge variant", "id-2",
            SEPARATIONS)
        mod08.seal_sealed_set(sealed_set)
        identifiers = [
            entry["identifier"] for entry in sealed_set["authored"]]
        self.assertEqual(identifiers, ["id-1", "id-2"])
        standing = mod08.score_sealed(sealed_set)
        self.assertEqual(
            standing["standing"], "sealed until scoring closes")

    def test_control_distinct_identifiers_accepted(self):
        sealed_set = frozen_set()
        mod08.author_sealed_class(
            sealed_set, "sleeper class", "id-1", SEPARATIONS)
        entry = mod08.author_sealed_class(
            sealed_set, "sleeper class", "id-2", SEPARATIONS)
        self.assertEqual(entry["identifier"], "id-2")
        self.assertEqual(len(sealed_set["authored"]), 2)

    def test_control_authoring_before_freezing_refused(self):
        sealed_set = mod08.create_sealed_set()
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                sealed_set, "sleeper class", "id-1", SEPARATIONS)

    def test_control_sealing_needs_both_kinds(self):
        sealed_set = frozen_set()
        mod08.author_sealed_class(
            sealed_set, "sleeper class", "id-1", SEPARATIONS)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.seal_sealed_set(sealed_set)


if __name__ == "__main__":
    unittest.main()
