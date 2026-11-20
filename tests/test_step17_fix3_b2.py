"""Step 17 fix wave 3, Builder 2 tests: Slice 2, the mod10
concurrency, writer, and open and close doors. Rows FW3-03,
FW3-10, FW3-26, FW3-27, FW3-49, and FW3-60.

Each defect test reproduces the defect its row names on the
uncured tree (the landed tree carrying the Slice 1 cure, uncured
for these rows) and passes on the cured tree. File stores stand
built in temporary directories only. Standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

from crucible import mod10

PRODUCT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(mod10.__file__)))

WORKER_SOURCE = textwrap.dedent("""
    import os
    import sys
    import time

    sys.path.insert(0, sys.argv[4])
    from crucible import mod10

    path = sys.argv[1]
    prefix = sys.argv[2]
    count = int(sys.argv[3])
    barrier = path + ".barrier"
    deadline = time.time() + 60
    while not os.path.exists(barrier):
        if time.time() > deadline:
            print("BARRIER TIMEOUT")
            sys.exit(3)
        time.sleep(0.01)
    store = mod10.new_store("sweep", path=path)
    errors = 0
    for i in range(count):
        try:
            store.retain_run_record(
                {"run_id": prefix + "-" + str(i),
                 "payload": {"i": i, "text": "x" * 50}})
        except Exception as exc:
            errors += 1
            print("ERROR", type(exc).__name__, exc)
    print("DONE errors", errors)
""")


class TempDirBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "store.json")


class TestFW303CrossProcess(TempDirBase):
    """FW3-03 (High, T17R2-03): concurrent retention from separate
    processes on one store file path stands reconciled, locked, or
    refused in named form; no retained record stands lost in
    silence across processes."""

    def run_workers(self, workers, per_worker):
        worker_path = os.path.join(self._tmp.name, "worker.py")
        with open(worker_path, "w", encoding="utf-8") as handle:
            handle.write(WORKER_SOURCE)
        env = dict(os.environ)
        env["PYTHONPATH"] = PRODUCT_ROOT
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        procs = []
        for k in range(workers):
            procs.append(subprocess.Popen(
                [sys.executable, worker_path, self.path,
                 "w" + str(k), str(per_worker), PRODUCT_ROOT],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, env=env))
        with open(self.path + ".barrier", "w", encoding="utf-8") as handle:
            handle.write("go")
        outputs = []
        for proc in procs:
            out, _ = proc.communicate(timeout=300)
            outputs.append(out)
            self.assertEqual(proc.returncode, 0, out)
            self.assertIn("DONE errors 0", out)
        return outputs

    def test_cross_process_retention_all_land(self):
        self.run_workers(4, 40)
        fresh = mod10.new_store("sweep", path=self.path)
        index = fresh.index()
        self.assertEqual(len(index), 160)
        for k in range(4):
            for i in range(40):
                record = fresh.read_run_record(
                    "w" + str(k) + "-" + str(i))
                self.assertEqual(record["payload"]["i"], i)

    def test_cross_process_retention_second_shape_all_land(self):
        self.run_workers(3, 30)
        fresh = mod10.new_store("sweep", path=self.path)
        self.assertEqual(len(fresh.index()), 90)

    def test_two_instances_one_process_control(self):
        first = mod10.new_store("sweep", path=self.path)
        second = mod10.new_store("sweep", path=self.path)
        for i in range(20):
            first.retain_run_record({"run_id": "a-" + str(i), "v": i})
            second.retain_run_record({"run_id": "b-" + str(i), "v": i})
        fresh = mod10.new_store("sweep", path=self.path)
        self.assertEqual(len(fresh.index()), 40)


class TestFW310WriterCollision(TempDirBase):
    """FW3-10 (Medium, T17R2-10): the store writer refuses in named
    form, or renders in a stated distinct form, two keys that share
    one stored text."""

    def test_int_and_text_key_collision_refused(self):
        store = mod10.new_store("sweep", path=self.path)
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(
                {"run_id": "keys", 1: "a", "1": "b"})
        self.assertIn("store writer form", str(caught.exception))
        self.assertIn("one stored text", str(caught.exception))
        self.assertFalse(store.has_run_record("keys"))

    def test_bool_and_text_key_collision_refused_nested(self):
        store = mod10.new_store("sweep", path=self.path)
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(
                {"run_id": "keys2",
                 "data": {True: "a", "true": "b"}})
        self.assertIn("store writer form", str(caught.exception))
        self.assertIn("one stored text", str(caught.exception))

    def test_distinct_keys_control_written_whole(self):
        store = mod10.new_store("sweep", path=self.path)
        store.retain_run_record(
            {"run_id": "keys3", "data": {1: "a", "b": 2, False: "f"}})
        fresh = mod10.new_store("sweep", path=self.path)
        self.assertEqual(
            fresh.read_run_record("keys3"),
            {"run_id": "keys3",
             "data": {"1": "a", "b": 2, "false": "f"}})


class TestFW326OpenDoors(TempDirBase):
    """FW3-26 (Medium, T17R2-26): the store open doors deliver a
    wrong path, a directory, and a file that is not a store in the
    named store file form, stating the path ground and the next
    step."""

    def test_directory_path_store_file_form_with_ground_and_step(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.new_store("sweep", path=self._tmp.name)
        text = caught.exception.args[0]
        self.assertIn("could not be read as a store", text)
        self.assertIn("directory", text)
        self.assertIn("next step", text)

    def test_file_that_is_not_a_store_form_with_step(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("this is not a store {{{")
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.new_store("sweep", path=self.path)
        text = caught.exception.args[0]
        self.assertIn("could not be read as a store", text)
        self.assertIn("next step", text)

    def test_missing_parent_control_defers_to_flush(self):
        bad = os.path.join(self._tmp.name, "nope", "store.json")
        store = mod10.new_store("sweep", path=bad)
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record({"run_id": "mp-1", "v": 1})
        self.assertIn("no store file stands", str(caught.exception))

    def test_new_path_in_existing_directory_control(self):
        store = mod10.new_store("sweep", path=self.path)
        store.retain_run_record({"run_id": "ok-1", "v": 1})
        self.assertEqual(
            store.read_run_record("ok-1"), {"run_id": "ok-1", "v": 1})


class TestFW327RunClose(unittest.TestCase):
    """FW3-27 (Medium, T17R2-27): the run close act reports a
    release only for a run standing retained under the kind handed
    in, and refuses a run that stands nowhere, or under another
    kind, in named form."""

    def setUp(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)

    def test_close_run_standing_nowhere_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.close_run_retention("ghost", "Tier 1")
        self.assertIn("no release stands recorded", str(caught.exception))
        self.assertIn("stands nowhere", str(caught.exception))

    def test_close_run_under_wrong_kind_refused(self):
        for day in (1, 2):
            mod10.retain_checkpoint(
                {"run_id": "real", "simulated_day": day},
                store_kind="pilot")
        with self.assertRaises(ValueError) as caught:
            mod10.close_run_retention("real", "Tier 0", store_kind="sweep")
        self.assertIn("pilot", str(caught.exception))
        self.assertIn("no release stands recorded", str(caught.exception))
        self.assertEqual(
            len(mod10.checkpoints_for_run("real", store_kind="pilot")), 2)

    def test_close_run_under_true_kind_control(self):
        for day in (1, 2):
            mod10.retain_checkpoint(
                {"run_id": "real2", "simulated_day": day},
                store_kind="pilot")
        record = mod10.close_run_retention(
            "real2", "Tier 0", store_kind="pilot")
        self.assertTrue(record["release_recorded"])
        self.assertEqual(record["released_days"], [1, 2])
        self.assertEqual(
            mod10.checkpoints_for_run("real2", store_kind="pilot"), [])


class TestFW349StoreLookupGround(unittest.TestCase):
    """FW3-49 (Low, T17R2-49): the store lookup refusal states the
    ground of the handing actually made, naming a missing store
    handing as missing. S16-R01 stands NOT settled: this row states
    the ground of the handing actually made and nothing more."""

    def setUp(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)

    def test_lookup_with_no_arguments_names_missing_store(self):
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup()
        text = str(caught.exception)
        self.assertIn("missing", text)
        self.assertIn("no store kind stands named", text)
        self.assertNotIn("across stores", text)

    def test_lookup_with_empty_kind_list_names_missing_store(self):
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup([], "x")
        text = str(caught.exception)
        self.assertIn("missing", text)
        self.assertNotIn("across stores", text)

    def test_lookup_across_stores_control_keeps_its_ground(self):
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup(["sweep", "pilot"], "x")
        self.assertIn("across stores", str(caught.exception))

    def test_lookup_single_store_control(self):
        mod10.retain_run_record({"run_id": "lk-1", "v": 7})
        record = mod10.store_lookup(["sweep"], "lk-1")
        self.assertEqual(record, {"run_id": "lk-1", "v": 7})


class TestFW360RefusalLabels(TempDirBase):
    """FW3-60 (Low, T17R2-60): the mod10 refusal grounds render
    every handed form with a stated label, container forms
    included."""

    def write_payload_text(self, text):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_store_kind_object_label_rendered(self):
        self.write_payload_text(
            '{"store_kind": {"x": 1}, "records": []}')
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.new_store("sweep", path=self.path)
        self.assertIn("{'x': 1}", caught.exception.args[0])

    def test_store_kind_list_label_rendered(self):
        self.write_payload_text(
            '{"store_kind": ["sweep"], "records": []}')
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.new_store("sweep", path=self.path)
        self.assertIn("['sweep']", caught.exception.args[0])

    def test_gc08_kind_container_label_rendered(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_gc08_record(["sweep"], {}, "owner-1")
        text = str(caught.exception)
        self.assertIn("['sweep']", text)
        self.assertNotIn("kind: ;", text)

    def test_text_kind_label_control_rendered(self):
        store = mod10.new_store("sweep", path=self.path)
        store.retain_run_record({"run_id": "lbl-1", "v": 1})
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.new_store("pilot", path=self.path)
        self.assertIn("sweep", caught.exception.args[0])


if __name__ == "__main__":
    unittest.main()
