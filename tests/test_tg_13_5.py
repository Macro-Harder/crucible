"""Test group TG-13.5. One lookup building and headline accounting, operation C-22.
Slice S-13, Reporter and family registry, MOD-11. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod11, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod11 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod11 absent, pinned behaviour unmet: " + behaviour)


class TestTG135(unittest.TestCase):
    def test_one_lookup_or_named_failure(self):
        """
        Fixture: A headline unit attempted from a record that does not resolve in one lookup.
        Pins: No unit is built, and no unit rests on that record, per Contract H. The failure is stated as a named failure, and its destination stands at the Step 12 destination amendment for cluster R1-036.
        Bar: Provenance lives inside the unit, never in a separate file, caption store, or registry only; a unit whose provenance resolves only outside itself fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.5 and this behaviour; a unit built from a record that does not resolve in one lookup fails this test when the surface stands.
        """
        require_surface(self, "TG-13.5", "one lookup building, no unit built from a record that does not resolve in one lookup, failure stated as a named failure")
        m = _surface_module
        import crucible.mod10 as mod10
        family = {}
        failed = m.build_headline_unit_from_run("run-tg135-absent", {}, family_record=family)
        self.assertFalse(failed["built"])
        self.assertIsNone(failed["unit"])
        self.assertEqual(failed["failure"]["name"], mod10.ONE_LOOKUP_FAILURE_NAME)
        self.assertEqual(failed["failure"]["record"], "run-tg135-absent")
        self.assertEqual(family["named_failures"], [failed["failure"]])
        mod10.retain_run_record({"run_id": "run-tg135-resolves", "run_identifier": "run-tg135-resolves", "record_state": "as retained"})
        values = {field: "value for " + field for field in m.HEADLINE_UNIT_FIELDS if field not in ("checkability_fields", "run_registry_line")}
        built = m.build_headline_unit_from_run("run-tg135-resolves", values)
        self.assertTrue(built["built"])
        self.assertIsNone(built["failure"])
        self.assertTrue(m.validate_headline_unit(built["unit"]))
        provenance = built["unit"]["checkability_fields"]
        self.assertEqual(provenance["record"], "run-tg135-resolves")
        self.assertTrue(provenance["inside_unit"])

    def test_weekly_count_counts_units_once(self):
        """
        Fixture: A week in which one headline unit is supported by many runs.
        Pins: The weekly headline reading load is computed from the stored summary records alone as distinct headline unit identifiers whose witness records fall in that week, one unit counting once however many runs support it, per Shape 1.
        Bar: A count that rises with supporting runs fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.5 and this behaviour; a weekly count rising with supporting runs fails this test when the surface stands.
        """
        require_surface(self, "TG-13.5", "weekly count counts distinct headline unit identifiers once, however many runs support each unit")
        m = _surface_module
        records = [
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W1", "headline_unit_identifiers": ["u1", "u2"]},
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W2", "headline_unit_identifiers": ["u3"]},
        ]
        self.assertEqual(m.weekly_count(records, "W1"), 2)
        direct = len({identifier for record in records if record["week"] == "W1" for identifier in record["headline_unit_identifiers"]})
        self.assertEqual(m.weekly_count(records, "W1"), direct)
        more_runs = list(records)
        for _ in range(5):
            more_runs.append({"week": "W1", "headline_unit_identifiers": ["u1"]})
        self.assertEqual(m.weekly_count(more_runs, "W1"), 2)
        self.assertEqual(m.weekly_count(records, "W2"), 1)

    def test_weekly_cap_ruled_form(self):
        """
        Fixture: A week whose stored summary records name 25 distinct headline units, and a week naming a 26th unit.
        Pins: The weekly count counts units once, as the entry above states. At the cap, Manager ruling Entry 20 at design/steps/step-14-manager-rulings.md rules the behaviour: the Reporter holds the 26th unit, held units stand reported as held, and held units stand released into the next weekly container in arrival order. This test pins that ruled behaviour at 25, 26, and 27 units and on the following container.
        Bar: A container that refuses, drops, or silently counts a unit beyond the cap fails this group; a held unit reported as counted, or a held unit released out of arrival order, fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.5 and this behaviour; a container standing at odds with the ruled holding and release form fails this test when the surface stands.
        """
        require_surface(self, "TG-13.5", "weekly cap ruled form under Manager ruling Entry 20, units beyond the cap held, reported as held, and released into the next weekly container in arrival order")
        m = _surface_module
        units25 = ["u%02d" % n for n in range(1, 26)]
        units26 = units25 + ["u26"]
        units27 = units26 + ["u27"]
        records25 = [{"week": "W25", "headline_unit_identifiers": units25}]
        records26 = [{"week": "W26", "headline_unit_identifiers": units26}]
        self.assertEqual(m.weekly_count(records25, "W25"), 25)
        self.assertEqual(m.weekly_count(records26, "W26"), 26)
        at_cap = m.make_weekly_container("W25", units25)
        self.assertEqual(at_cap["cap"], 25)
        self.assertEqual(at_cap["count"], 25)
        self.assertEqual(at_cap["headline_units"], units25)
        self.assertEqual(at_cap["held_units"], [])
        self.assertEqual(at_cap["held_count"], 0)
        one_beyond = m.make_weekly_container("W26", units26)
        self.assertEqual(one_beyond["count"], 25)
        self.assertEqual(one_beyond["headline_units"], units25)
        self.assertEqual(one_beyond["held_units"], ["u26"])
        self.assertEqual(one_beyond["held_count"], 1)
        self.assertTrue(one_beyond["held_reported_as_held"])
        beyond = m.make_weekly_container("W26", units27)
        self.assertEqual(beyond["count"], 25)
        self.assertEqual(beyond["headline_units"], units25)
        self.assertEqual(beyond["held_units"], ["u26", "u27"])
        self.assertEqual(beyond["held_count"], 2)
        self.assertTrue(beyond["held_reported_as_held"])
        following = m.next_weekly_container("W27", beyond, ["u28"])
        self.assertEqual(following["headline_units"], ["u26", "u27", "u28"])
        self.assertEqual(following["count"], 3)
        self.assertEqual(following["held_units"], [])

    def test_reporter_input_carriage_for_divergence_block(self):
        """
        Fixture: The retained records for one family at slice S-10, carrying the divergence count computed at slice S-04 for that family, in one form with the count standing as computed, and in a second form with a blocked family mark standing in those records, naming the affected family and the affected share, where a count for that family stands nonzero and unresolved, as Amendment S12-008 clause one states the carriage.
        Pins: The count, or the mark where it stands, stands among the inputs the Reporter reads for that family, carried through the retained records at slice S-10, and while the mark stands the Reporter builds no headline unit resting on the affected share for that family, and no report reads the affected share for that family as standing as reported.
        Bar: A headline unit built for a marked family resting on its affected share fails this group, and a build path in which the count or the mark never reaches the Reporter inputs fails this group at the carriage limb, whether or not any report reads the share.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.5 and this behaviour; a headline unit built on a marked family affected share fails this test when the surface stands.
        """
        require_surface(self, "TG-13.5", "divergence count or blocked family mark carried through retained records at S-10 into the Reporter inputs, no headline unit built on a marked family affected share")
        m = _surface_module
        plain_inputs = m.reporter_inputs_for_family({"divergence_count": 3})
        self.assertEqual(plain_inputs["divergence_count"], 3)
        self.assertIsNone(plain_inputs["blocked_family_mark"])
        self.assertTrue(m.share_report_stands(plain_inputs, "share-a"))
        mark = {"affected_family": "family-a", "affected_share": "share-a", "count": 2, "resolved": False}
        marked_inputs = m.reporter_inputs_for_family({"divergence_count": 2, "blocked_family_mark": mark})
        self.assertEqual(marked_inputs["divergence_count"], 2)
        self.assertEqual(marked_inputs["blocked_family_mark"], mark)
        self.assertEqual(marked_inputs["blocked_family_mark"]["affected_family"], "family-a")
        self.assertEqual(marked_inputs["blocked_family_mark"]["affected_share"], "share-a")
        self.assertFalse(m.share_report_stands(marked_inputs, "share-a"))
        self.assertTrue(m.share_report_stands(marked_inputs, "share-b"))
        resolved_inputs = m.reporter_inputs_for_family({"divergence_count": 2, "blocked_family_mark": dict(mark, resolved=True)})
        self.assertTrue(m.share_report_stands(resolved_inputs, "share-a"))


if __name__ == "__main__":
    unittest.main()
