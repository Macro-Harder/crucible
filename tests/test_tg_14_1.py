"""Test group TG-14.1. Exact replay and resume equality, AC-1 and AC-2.
Slice S-14, Replication Checker and scoring interface, MOD-13. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod13, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod13 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod13 absent, pinned behaviour unmet: " + behaviour)


class TestTG141(unittest.TestCase):
    def test_replay_identity_over_named_field_list(self):
        """
        Fixture: One scenario, seed set, and code version run twice.
        Pins: The field list AC-1 states and its order, field for field, and an identical headline unit, or the run is marked non deterministic. Until a canonical form per hashed field stands stated on a plan level record, this test pins the field list and the order only and claims no byte level hash equality across independent renderings, per open point OP-24.
        Bar: Summary record fields written or amended after run close stand outside the list because the hash is a statement about end of run state, and this test claims no completeness over the detection state.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.1 and this behaviour; a replay differing on any listed field without the non deterministic marking fails this test when the surface stands.
        """
        require_surface(self, "TG-14.1", "replay identity over the AC-1 field list and its order only, non deterministic marking on any difference")
        import crucible.mod01 as mod01
        import crucible.mod13 as surface
        fields = list(mod01.state_hash_field_list())
        facts = {field: "value for " + field for field in fields}
        facts["headline_unit"] = {"unit": "unit-1"}
        check = surface.replay_check(facts, dict(facts))
        self.assertEqual(check["field_list"], fields)
        self.assertEqual(check["order"], fields)
        self.assertTrue(check["deterministic"])
        self.assertFalse(check["hash_equality_claimed"])
        self.assertFalse(check["detection_state_completeness_claimed"])
        changed = dict(facts)
        changed[fields[0]] = "a different value"
        marked = surface.replay_check(facts, changed)
        self.assertTrue(marked["marked_non_deterministic"])
        self.assertIn(fields[0], marked["differing_fields"])
        pinned = surface.ac1_check(facts)
        self.assertEqual(pinned["field_list"], fields)
        self.assertEqual(pinned["values"][fields[0]], "HASH-VALUE-BARRED")

    def test_non_deterministic_consequences(self):
        """
        Fixture: A run marked non deterministic, offered in turn as a witness, as headline support, and as confirmation support.
        Pins: The run is barred from all three uses; it may still feed a screening observation labelled as a screening observation, and a timing or cost figure under the pilot confinement at decision D-07, and no other use.
        Bar: Any fourth use fails this group.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.1 and this behaviour; a non deterministic run used as witness, headline support, or confirmation support fails this test when the surface stands.
        """
        require_surface(self, "TG-14.1", "run marked non deterministic barred from witness, headline support, and confirmation support")
        import crucible.mod13 as surface
        for use in ("witness", "headline support", "confirmation support"):
            self.assertFalse(surface.use_stands_for_marked_run(use))
        self.assertTrue(surface.use_stands_for_marked_run("screening observation", labelled_screening=True))
        self.assertFalse(surface.use_stands_for_marked_run("screening observation"))
        self.assertTrue(surface.use_stands_for_marked_run("pilot timing"))
        self.assertTrue(surface.use_stands_for_marked_run("pilot cost"))
        self.assertFalse(surface.use_stands_for_marked_run("headline claim"))

    def test_resume_equality_in_stated_scope(self):
        """
        Fixture: A run interrupted and resumed from its checkpoint, compared with the uninterrupted run.
        Pins: The resumed run reaches the same state on every part of its state in the non detection scope, per AC-2 and operation C-02; a resume check failure promotes the run to full retention and bars its use as a witness until the difference is explained.
        Bar: No resume equality for the detection part stands in any form wider than verdict level, in any artefact, including a test name or a suite summary line; the detection part limb of this comparison stands in gated form in the companion test in this file.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.1 and this behaviour; a resumed run differing in the non detection scope without promotion to full retention and the witness bar fails this test when the surface stands.
        """
        require_surface(self, "TG-14.1", "resume equality in the non detection scope, full retention promotion and witness bar on a resume check failure")
        import crucible.mod01 as mod01
        import crucible.mod13 as surface
        fields = list(mod01.state_hash_field_list())
        facts = {field: "value for " + field for field in fields}
        verdicts = {"first verdict state after resume": "verdict-a", "run close": "verdict-b"}
        original = dict(facts)
        original["detection_verdicts"] = dict(verdicts)
        resumed = dict(facts)
        resumed["detection_verdicts"] = dict(verdicts)
        check = surface.resume_check(original, resumed)
        self.assertTrue(check["equal_in_scope"])
        self.assertEqual(check["detection_comparison_points"], ["first verdict state after resume", "run close"])
        self.assertEqual(check["detection_scope"], "verdict level only")
        differing = dict(facts)
        differing[fields[1]] = "another value"
        differing["detection_verdicts"] = dict(verdicts)
        failed = surface.resume_check(original, differing)
        self.assertFalse(failed["equal_in_scope"])
        self.assertTrue(failed["promoted_to_full_retention"])
        self.assertTrue(failed["witness_use_barred"])
        self.assertEqual(failed["first_divergence"], fields[1])
        self.assertFalse(surface.validate_resume_claim({"detection_scope": "state level"}))

    def test_resume_detection_part_verdict_level_gated(self):
        """
        Fixture: A run interrupted and resumed from its checkpoint, at the detection part only. State recorded as gated on the reconciliation act for Plan Amendment (Step 11, reconciliation).
        Pins: The detection part of a joint run stands compared at verdict level only, per agent per day, at the first verdict state after resume and again at run close, as the DQ7-01 decision states. While the gate stands, this test records a gated state and no resume equality claim for the detection part stands in any artefact.
        Bar: No resume equality for the detection part in any form wider than verdict level, and no gated state read as a pass, fails this group.
        Failure: Gated form only; this test never passes while the reconciliation act does not stand.
        """
        self.skipTest("Gated: the reconciliation act for Plan Amendment (Step 11, reconciliation), the DQ7-01 reliance gate at TG-14.1")


class TestStep15Fix1TA01(unittest.TestCase):
    """Step 15 Round 1 fix pins for TA-01: a check must not pass on absence."""

    def _fields(self):
        import crucible.mod01 as mod01
        return list(mod01.state_hash_field_list())

    def test_replay_check_fails_on_absent_fields(self):
        require_surface(self, "TG-14.1", "replay check names missing AC-1 fields as divergence")
        import crucible.mod13 as surface
        fields = self._fields()
        for first, second in (({}, {}), (None, None), ({"a": 1}, {"b": 2})):
            check = surface.replay_check(first, second)
            self.assertFalse(check["deterministic"])
            self.assertTrue(check["marked_non_deterministic"])
            self.assertEqual(check["missing_fields"], fields)
            for field in fields:
                self.assertIn(field, check["differing_fields"])

    def test_replay_check_partial_record_fails(self):
        require_surface(self, "TG-14.1", "replay check fails on a partial AC-1 record")
        import crucible.mod13 as surface
        fields = self._fields()
        facts = {field: "value for " + field for field in fields}
        facts["headline_unit"] = {"unit": "unit-1"}
        partial = {fields[0]: facts[fields[0]], "headline_unit": {"unit": "unit-1"}}
        check = surface.replay_check(facts, partial)
        self.assertFalse(check["deterministic"])
        self.assertEqual(check["missing_fields"], fields[1:])

    def test_resume_check_fails_on_absent_fields(self):
        require_surface(self, "TG-14.1", "resume check names missing AC-1 fields, promotes, and bars witness use")
        import crucible.mod13 as surface
        fields = self._fields()
        for original, resumed in (({}, {}), (None, None), ({"a": 1}, {"b": 2})):
            check = surface.resume_check(original, resumed)
            self.assertFalse(check["equal_in_scope"])
            self.assertTrue(check["promoted_to_full_retention"])
            self.assertTrue(check["witness_use_barred"])
            self.assertEqual(check["missing_fields"], fields)
            self.assertIsNotNone(check["divergence_record"])

    def test_genuine_records_still_agree(self):
        require_surface(self, "TG-14.1", "genuine AC-1 records still return equality")
        import crucible.mod13 as surface
        fields = self._fields()
        facts = {field: "value for " + field for field in fields}
        facts["headline_unit"] = {"unit": "unit-1"}
        self.assertTrue(surface.replay_check(facts, dict(facts))["deterministic"])
        verdicts = {"first verdict state after resume": "verdict-a", "run close": "verdict-b"}
        original = dict(facts)
        original["detection_verdicts"] = dict(verdicts)
        resumed = dict(facts)
        resumed["detection_verdicts"] = dict(verdicts)
        self.assertTrue(surface.resume_check(original, resumed)["equal_in_scope"])


class TestStep15Round2Fix1NullDress(unittest.TestCase):
    """Step 15 Round 2 fix pins for R2-A7-01: a check must not pass on a field standing present with the value None, and a resume must not pass on mutually absent detection verdicts."""

    def _fields(self):
        import crucible.mod01 as mod01
        return list(mod01.state_hash_field_list())

    def _genuine_facts(self):
        fields = self._fields()
        facts = {field: "value for " + field for field in fields}
        facts["headline_unit"] = "u"
        return fields, facts

    def test_replay_check_fails_on_null_dressed_fields(self):
        require_surface(self, "TG-14.1", "replay check names null dressed AC-1 fields as missing")
        import crucible.mod13 as surface
        fields = self._fields()
        first = {field: None for field in fields}
        first["headline_unit"] = "u"
        second = {field: None for field in fields}
        second["headline_unit"] = "u"
        check = surface.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertTrue(check["marked_non_deterministic"])
        self.assertEqual(check["missing_fields"], fields)
        for field in fields:
            self.assertIn(field, check["differing_fields"])

    def test_replay_check_fails_on_one_sided_null_field(self):
        require_surface(self, "TG-14.1", "replay check names a one sided null AC-1 field as missing")
        import crucible.mod13 as surface
        fields, facts = self._genuine_facts()
        other = dict(facts)
        other[fields[3]] = None
        check = surface.replay_check(facts, other)
        self.assertFalse(check["deterministic"])
        self.assertEqual(check["missing_fields"], [fields[3]])
        self.assertIn(fields[3], check["differing_fields"])

    def test_replay_check_fails_on_null_headline_unit(self):
        require_surface(self, "TG-14.1", "replay check fails where the headline unit stands null on both sides")
        import crucible.mod13 as surface
        fields, facts = self._genuine_facts()
        first = dict(facts)
        first["headline_unit"] = None
        second = dict(facts)
        second["headline_unit"] = None
        check = surface.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertFalse(check["identical_headline_unit"])

    def test_replay_check_still_agrees_on_stated_falsy_values(self):
        require_surface(self, "TG-14.1", "replay check still agrees on stated falsy AC-1 values")
        import crucible.mod13 as surface
        fields = self._fields()
        for value in (0, False, ""):
            facts = {field: value for field in fields}
            facts["headline_unit"] = "u"
            self.assertTrue(surface.replay_check(facts, dict(facts))["deterministic"])

    def test_resume_check_fails_on_null_dressed_fields(self):
        require_surface(self, "TG-14.1", "resume check names null dressed AC-1 fields, promotes, and bars witness use")
        import crucible.mod13 as surface
        fields = self._fields()
        first = {field: None for field in fields}
        first["headline_unit"] = "u"
        second = {field: None for field in fields}
        second["headline_unit"] = "u"
        check = surface.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertTrue(check["promoted_to_full_retention"])
        self.assertTrue(check["witness_use_barred"])
        self.assertEqual(check["missing_fields"], fields)
        self.assertIsNotNone(check["divergence_record"])

    def test_resume_check_fails_on_mutually_absent_verdicts(self):
        require_surface(self, "TG-14.1", "resume check fails where no detection verdict stands on either side")
        import crucible.mod13 as surface
        fields, facts = self._genuine_facts()
        points = surface.detection_comparison_points()
        bare = surface.resume_check(dict(facts), dict(facts))
        self.assertFalse(bare["equal_in_scope"])
        self.assertTrue(bare["promoted_to_full_retention"])
        self.assertTrue(bare["witness_use_barred"])
        self.assertEqual(bare["missing_fields"], [])
        self.assertEqual(bare["first_divergence"], points[0])
        self.assertIsNotNone(bare["divergence_record"])
        emptied_first = dict(facts)
        emptied_first["detection_verdicts"] = {}
        emptied_second = dict(facts)
        emptied_second["detection_verdicts"] = {}
        emptied = surface.resume_check(emptied_first, emptied_second)
        self.assertFalse(emptied["equal_in_scope"])
        self.assertTrue(emptied["promoted_to_full_retention"])
        self.assertTrue(emptied["witness_use_barred"])
        nulled_first = dict(facts)
        nulled_first["detection_verdicts"] = {point: None for point in points}
        nulled_second = dict(facts)
        nulled_second["detection_verdicts"] = {point: None for point in points}
        nulled = surface.resume_check(nulled_first, nulled_second)
        self.assertFalse(nulled["equal_in_scope"])
        self.assertTrue(nulled["promoted_to_full_retention"])
        self.assertTrue(nulled["witness_use_barred"])

    def test_resume_check_verdict_controls_still_stand(self):
        require_surface(self, "TG-14.1", "resume check still agrees on genuine verdicts and still diverges on a one sided verdict absence")
        import crucible.mod13 as surface
        fields, facts = self._genuine_facts()
        verdicts = {"first verdict state after resume": "verdict-a", "run close": "verdict-b"}
        original = dict(facts)
        original["detection_verdicts"] = dict(verdicts)
        resumed = dict(facts)
        resumed["detection_verdicts"] = dict(verdicts)
        self.assertTrue(surface.resume_check(original, resumed)["equal_in_scope"])
        one_sided = surface.resume_check(original, dict(facts))
        self.assertFalse(one_sided["equal_in_scope"])
        self.assertTrue(one_sided["promoted_to_full_retention"])
        self.assertTrue(one_sided["witness_use_barred"])


if __name__ == "__main__":
    unittest.main()
