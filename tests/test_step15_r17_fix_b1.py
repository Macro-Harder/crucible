"""Fix wave 16, Builder 1 pins for Round 16 rows R16-001, R16-002,
R16-003, R16-005, R16-006, R16-020, R16-047, R16-048, and R16-049.

Each defect pin states the charged defect form of its register row
with the proving acts its source paper used, beside the controls
that paper states. Timing pins state the bound the register states
for the enumeration rows: the sister readings answer at once, so a
two second bound stands far past the cured form and far inside the
uncured factorial and cross product costs the papers record.
"""

import time
import unittest

from crucible import mod04, mod06, mod08, mod10, mod12


class TestR16001Mod08VerdictNode(unittest.TestCase):
    """R16-001: the MOD-08 barred verdict walk judges each dict
    entry on its own and never the dict node on the joined reading
    of its keys in stored order."""

    def _out(self, extra):
        output = {"profile_bound_label": mod08.PROFILE_LABEL_CARRIAGE}
        output.update(extra)
        return output

    def test_walk_split_verdict(self):
        self.assertTrue(
            mod08._carries_barred_verdict({"verd": "pass", "ict": 1}))

    def test_gate_split_forms_refused(self):
        for extra in (
                {"verd": "pass", "ict": 1},
                {"res": "fail", "ult": 1},
                {"out": "failed", "come": 1}):
            with self.subTest(extra=extra):
                self.assertFalse(mod08.validate_output(self._out(extra)))

    def test_gate_split_score_forms_refused(self):
        for extra in (
                {"score_ver": "pass", "dict": 1},
                {"scor": "passed", "e_result": 1}):
            with self.subTest(extra=extra):
                self.assertFalse(mod08.validate_output(self._out(extra)))

    def test_gate_folded_and_substring_splits_refused(self):
        self.assertFalse(mod08.validate_output(
            self._out({"VERD": "Pass", "ICT": 1})))
        self.assertFalse(mod08.validate_output(
            self._out({"myver": "fail", "dict": 1})))

    def test_gate_empty_middle_split_refused(self):
        self.assertFalse(mod08.validate_output(
            self._out({"verd": "pass", "": 1, "ict": 1})))

    def test_gate_nested_splits_refused(self):
        for extra in (
                {"w": {"verd": "pass", "ict": 1}},
                {"w": [{"verd": "pass", "ict": 1}]},
                {"w": ({"verd": "pass", "ict": 1},)},
                {"a": {"b": {"c": {"verd": "pass", "ict": 1}}}}):
            with self.subTest(extra=extra):
                self.assertFalse(mod08.validate_output(self._out(extra)))

    def test_walk_container_key_split(self):
        self.assertTrue(mod08._carries_barred_verdict(
            {("verd", "ict"): "pass"}))

    def test_controls_hold(self):
        self.assertFalse(mod08.validate_output(
            self._out({"verdict": "pass"})))
        self.assertFalse(mod08.validate_output(
            self._out({"myverdict": "fail"})))
        self.assertTrue(mod08.validate_output(
            self._out({"clean": 1})))
        self.assertTrue(mod08.validate_output(
            self._out({"verd": "pass", "clean": 1, "ict": 1})))


class TestR16002Mod06MiddleKeys(unittest.TestCase):
    """R16-002: the MOD-06 dict node limbs do not step past a key
    whose reading stands empty in the walk folded forms."""

    def test_marker_separator_middles_barred(self):
        for middle in ("___", " ", "-"):
            with self.subTest(middle=middle):
                self.assertTrue(mod06._payload_carries_barred(
                    {"real_mo": 5, middle: 5, "ney": 5}))

    def test_marker_digit_middles_barred(self):
        for middle in ("0", "123"):
            with self.subTest(middle=middle):
                self.assertTrue(mod06._payload_carries_barred(
                    {"real_mo": 5, middle: 5, "ney": 5}))

    def test_anchor_middles_barred(self):
        for middle in ("___", " ", "-", "0", "123"):
            with self.subTest(middle=middle):
                self.assertTrue(mod06._payload_carries_barred(
                    {"anch": 1, middle: 1, "or_set": 1}))

    def test_pair_digit_middles_barred(self):
        for middle in ("0", "123"):
            with self.subTest(middle=middle):
                self.assertTrue(mod06._payload_carries_barred(
                    {"amou": 5, middle: 5, "nt": 5, "currency": "x"}))

    def test_gate_and_nested_forms_refused(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "k1", payload={"real_mo": 5, "___": 5, "ney": 5})
        for payload in (
                {"w": {"real_mo": 5, "___": 5, "ney": 5}},
                {"w": [{"real_mo": 5, "0": 5, "ney": 5}]},
                {"w": ({"real_mo": 5, "___": 5, "ney": 5},)},
                {"a": {"b": {"c": {"real_mo": 5, "___": 5, "ney": 5}}}}):
            with self.subTest(payload=payload):
                self.assertTrue(mod06._payload_carries_barred(payload))

    def test_controls_hold(self):
        self.assertTrue(mod06._payload_carries_barred(
            {"real___money": 5}))
        self.assertTrue(mod06._payload_carries_barred(
            {"real_mo": 5, "ney": 5}))
        self.assertTrue(mod06._payload_carries_barred(
            {"amou": 5, "___": 5, "nt": 5, "currency": "x"}))
        self.assertFalse(mod06._payload_carries_barred(
            {"real_mo": 5, "clean": 5, "ney": 5}))
        result = mod06.escrow_result(
            "k1", payload={"real_mo": 5, "clean": 5, "ney": 5})
        self.assertEqual(result["kind"], "k1")


class TestR16003Mod12UnorderedBound(unittest.TestCase):
    """R16-003: the MOD-12 unordered limb enumerates every ordering
    with no part count bound, its 4096 bound counting distinct
    composed texts only."""

    def test_nine_part_set_answers_at_once(self):
        start = time.perf_counter()
        texts = mod12._key_stored_texts(frozenset(range(9)))
        elapsed = time.perf_counter() - start
        self.assertEqual(texts, {""})
        self.assertLess(elapsed, 2.0)

    def test_dress_eq_nine_part_set_answers_at_once(self):
        start = time.perf_counter()
        result = mod12._dress_eq(set(range(9)), "fixed")
        elapsed = time.perf_counter() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 2.0)

    def test_controls_hold(self):
        self.assertEqual(
            mod12._key_stored_texts(frozenset({"fix", "ed"})),
            {"fixed", "edfix"})
        self.assertEqual(
            mod12._key_stored_texts(frozenset(range(7))), {""})


class TestR16006Mod12OrderedBound(unittest.TestCase):
    """R16-006: the MOD-12 ordered limb builds the full cross
    product before testing its 4096 bound."""

    def _part(self, letters, pair):
        return (frozenset(letters), frozenset(pair))

    def test_cross_product_pair_answers_at_once(self):
        part_p = self._part("abcdef", "gh")
        part_q = self._part("ijklmn", "op")
        self.assertEqual(len(mod12._key_stored_texts(part_p)), 1440)
        start = time.perf_counter()
        texts = mod12._key_stored_texts((part_p, part_q))
        elapsed = time.perf_counter() - start
        self.assertEqual(texts, {mod12._key_stored_text((part_p, part_q))})
        self.assertLess(elapsed, 2.0)

    def test_pair_of_256_text_parts_falls_back(self):
        part_a = tuple(
            frozenset(pair) for pair in (
                ("a", "b"), ("c", "d"), ("e", "f"), ("g", "h"),
                ("i", "j"), ("k", "l"), ("m", "n"), ("o", "p")))
        self.assertEqual(len(mod12._key_stored_texts(part_a)), 256)
        texts = mod12._key_stored_texts((part_a, part_a))
        self.assertEqual(texts, {mod12._key_stored_text((part_a, part_a))})

    def test_ordered_control_under_bound(self):
        part_p = self._part("abcdef", "gh")
        self.assertEqual(len(mod12._key_stored_texts((part_p, "z"))), 1440)


class TestR16005Mod10ViewNodeExactNames(unittest.TestCase):
    """R16-005: the MOD-10 run_view_leak_check record node judges
    only the whole joined text, so the exact form barred names
    split across two keys stand reportable."""

    def _record(self, extra):
        record = mod04.build_view_record()
        record.update(extra)
        return record

    def test_split_label_and_sleeper_refused(self):
        for extra in ({"lab": "clean", "el": "clean"},
                      {"slee": "clean", "per": "clean"}):
            with self.subTest(extra=extra):
                with self.assertRaises(ValueError):
                    mod10.run_view_leak_check(self._record(extra))

    def test_split_honest_and_farm_refused(self):
        for extra in ({"is_ho": "clean", "nest": "clean"},
                      {"is_fa": "clean", "rm": "clean"}):
            with self.subTest(extra=extra):
                with self.assertRaises(ValueError):
                    mod10.run_view_leak_check(self._record(extra))

    def test_group_limb_split_with_further_key_refused(self):
        record = mod04.build_view_record(
            contents=None, graph_position=None)
        record["view_contents"] = {
            "lab": "clean", "el": "clean", "note": "clean"}
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)

    def test_controls_hold(self):
        result = mod10.run_view_leak_check(self._record({}))
        self.assertTrue(result["reportable"])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(self._record({"label": "clean"}))
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(
                self._record({"ground_": "clean", "truth": "clean"}))


class TestR16020Mod12ClaimFieldDress(unittest.TestCase):
    """R16-020: the MOD-12 claim field scan takes the one sorted
    text of a frozenset key, so a claim split in that dress stands
    unfound."""

    def _record(self, check):
        record = mod12.make_family_record()
        checks = [check]
        record["kill_check_fields"] = checks
        record["kill_checks"] = checks
        return record

    def test_absent_claim_in_split_dress_refused(self):
        record = self._record({frozenset({"aim", "cl"}): "no such claim"})
        self.assertFalse(mod12.validate_family_record(record))
        self.assertTrue(mod12.family_record_validation_failures(record))

    def test_controls_hold(self):
        absent_plain = self._record({"claim": "no such claim"})
        self.assertFalse(mod12.validate_family_record(absent_plain))
        absent_sorted = self._record(
            {frozenset({"cla", "im"}): "no such claim"})
        self.assertFalse(mod12.validate_family_record(absent_sorted))
        standing = self._record(
            {frozenset({"aim", "cl"}): "headline claim 1"})
        self.assertFalse(mod12.validate_family_record(standing))
        self.assertEqual(
            mod12.family_record_validation_failures(standing),
            ["the reportable run judgement stands refused"])


class TestR16047Mod12AnchorFieldDress(unittest.TestCase):
    """R16-047: the MOD-12 anchor count limb reads the one sorted
    text of a frozenset key, so the count never runs in that dress."""

    def _run(self, key, values):
        run = {"run_class": "screening", "seed_domain": "validation"}
        run[key] = values
        return run

    def test_frozenset_split_count_runs(self):
        run = self._run(frozenset({"anchor_scenario", "_values"}), [1, 2])
        self.assertFalse(mod12.validate_run_record(run))
        failures = mod12.run_record_validation_failures(run)
        self.assertTrue(any("anchor" in failure for failure in failures))

    def test_controls_hold(self):
        tuple_run = self._run(("anchor_scenario", "_values"), [1, 2])
        self.assertFalse(mod12.validate_run_record(tuple_run))
        lawful = self._run(
            frozenset({"anchor_scenario", "_values"}), [1, 2, 3])
        self.assertTrue(mod12.validate_run_record(lawful))


class TestR16048Mod12RunFieldDress(unittest.TestCase):
    """R16-048: the MOD-12 run field scan takes the one sorted text
    of a frozenset key, so a split field name stands unfound."""

    def test_split_run_class_found(self):
        run = {frozenset({"run_", "class"}): "screening",
               "seed_domain": "validation"}
        self.assertTrue(mod12.validate_run_record(run))
        self.assertEqual(mod12.run_record_validation_failures(run), [])

    def test_split_seed_domain_found(self):
        run = {"run_class": "screening",
               frozenset({"seed_", "domain"}): "validation"}
        self.assertTrue(mod12.validate_run_record(run))
        self.assertEqual(mod12.run_record_validation_failures(run), [])

    def test_controls_hold(self):
        run = {("run_", "class"): "screening",
               "seed_domain": "validation"}
        self.assertTrue(mod12.validate_run_record(run))
        whole = {frozenset({"run_class"}): "screening",
                 "seed_domain": "validation"}
        self.assertTrue(mod12.validate_run_record(whole))


class TestR16049Mod12SampleClassDress(unittest.TestCase):
    """R16-049: the MOD-12 sample statement reads a run class in
    set dress through the one sorted text, beside _dress_eq."""

    def test_set_split_class_counted(self):
        statement = mod12.sample_statement(
            [{"run_class": {"screen", "ing"}, "run_id": "r1"}])
        self.assertEqual(statement["n"], 1)
        self.assertEqual(
            statement["runs_completed_by_class"]["screening"], 1)

    def test_frozenset_split_class_counted(self):
        statement = mod12.sample_statement(
            [{"run_class": frozenset({"screen", "ing"}), "run_id": "r1"}])
        self.assertEqual(statement["n"], 1)
        self.assertEqual(
            statement["runs_completed_by_class"]["screening"], 1)

    def test_controls_hold(self):
        for dress in (["screen", "ing"], {"screening"}, "screening"):
            with self.subTest(dress=dress):
                statement = mod12.sample_statement(
                    [{"run_class": dress, "run_id": "r1"}])
                self.assertEqual(statement["n"], 1)
        self.assertTrue(mod12.validate_run_record(
            {"run_class": {"screen", "ing"},
             "seed_domain": "validation"}))


if __name__ == "__main__":
    unittest.main()
