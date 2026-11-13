"""Test group TG-10.5. Store separation and one lookup resolution.

Slice S-10, MOD-10 Recorder and stores. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod10, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
"""
import unittest

try:
    from crucible import mod10
    SURFACE = mod10
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-10.5"
STORE_KINDS = ("sweep", "pilot", "live")


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": product surface crucible.mod10 stands absent ("
            + repr(SURFACE_ERROR) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": product surface crucible.mod10 lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )


class TestStoreSeparation(unittest.TestCase):
    def test_three_stores_no_shared_index(self):
        """Fixture: F-04 carriage in checkpoint manifests beside sweep, pilot, and live history records, as TG-10.5 states.
        Pins: the sweep, pilot, and live history stores share no index, per Contract G and brief section 7.6.
        Bar: a lookup that resolves across stores in one step fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.5; with the surface present, any index shared between two of the three stores fails.
        """
        require_surface(self, "three stores share no index", "store_indexes")
        indexes = SURFACE.store_indexes()
        self.assertEqual(tuple(sorted(indexes.keys())), ("live", "pilot", "sweep"))
        self.assertIsNot(indexes["sweep"], indexes["pilot"])
        self.assertIsNot(indexes["sweep"], indexes["live"])
        self.assertIsNot(indexes["pilot"], indexes["live"])
        seen = []
        for kind in STORE_KINDS:
            for entry in indexes[kind]:
                self.assertNotIn(entry, seen)
                seen.append(entry)

    def test_pilot_artefacts_apart_with_confinement_label(self):
        """Fixture: a pilot artefact beside sweep results, as TG-10.5 states.
        Pins: pilot artefacts are stored apart from sweep results with their confinement label in the same artefact as the number, per brief section 6.2 seventh.
        Bar: a pilot artefact stored inside the sweep store, or carrying its number with no confinement label in the same artefact, fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.5; with the surface present, either form fails.
        """
        require_surface(self, "pilot artefacts apart with confinement label in the same artefact", "validate_store_placement")
        good = {"kind": "pilot", "store": "pilot", "value": 1, "confinement_label": "pilot confined"}
        self.assertTrue(SURFACE.validate_store_placement(good))
        in_sweep = {"kind": "pilot", "store": "sweep", "value": 1, "confinement_label": "pilot confined"}
        self.assertFalse(SURFACE.validate_store_placement(in_sweep))
        no_label = {"kind": "pilot", "store": "pilot", "value": 1}
        self.assertFalse(SURFACE.validate_store_placement(no_label))

    def test_cross_store_lookup_fails(self):
        """Fixture: a lookup addressed across two stores in one step, as TG-10.5 states.
        Pins: the lookup is rejected; resolution stands as one lookup inside the retained records of one run, in one store.
        Bar: a lookup that resolves across stores in one step fails this group; Contract H resolution is one lookup inside the retained records of the run, tested at TG-13.5.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.5; with the surface present, a cross store resolution fails.
        """
        require_surface(self, "cross store lookup in one step rejected", "store_lookup")
        with self.assertRaises(Exception):
            SURFACE.store_lookup(store_kinds=("sweep", "pilot"), key="any-key")
        with self.assertRaises(Exception):
            SURFACE.store_lookup(store_kinds=("pilot", "live"), key="any-key")


if __name__ == "__main__":
    unittest.main()
