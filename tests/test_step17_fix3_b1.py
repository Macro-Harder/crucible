"""Step 17 fix wave 3, Builder 1 tests: Slice 1, the mod10 store
load and integrity core. Rows FW3-01, FW3-02, FW3-09, FW3-11,
FW3-30, FW3-33, and FW3-59.

Each defect test reproduces the defect its row names on the
uncured tree at product head ab4a8cce and passes on the cured
tree. File stores stand built in temporary directories only.
Standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import hashlib
import json
import os
import tempfile
import unittest

from crucible import mod10


def deep_record(depth, rid="b1-deep"):
    record = {"run_id": rid}
    node = record
    for _ in range(depth):
        node["nest"] = {}
        node = node["nest"]
    node["leaf"] = 1
    return record


def old_unkeyed_digest(records):
    """The pre cure integrity signal: a plain SHA 256 over the
    canonical written form of the records, the form any hand
    that can write the file can recompute from the file alone."""
    canonical_text = mod10._serialize_store_text({"records": records})
    canonical = json.loads(canonical_text, parse_int=mod10._json_int)
    return hashlib.sha256(
        mod10._serialize_store_text(
            {"records": canonical["records"]}).encode("utf-8")
    ).hexdigest()


class TempDirBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "store.json")

    def make_store(self, records=((("run_id", "r1"), ("v", 1)),)):
        store = mod10.RecorderStore(store_kind="sweep", path=self.path)
        for pairs in records:
            store.retain_run_record(dict(pairs))
        return store

    def read_payload(self):
        with open(self.path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def write_payload(self, payload):
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)

    def read_text(self):
        with open(self.path, "r", encoding="utf-8") as handle:
            return handle.read()

    def write_text(self, text):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(text)


class TestFW301GuardedReload(TempDirBase):
    """FW3-01 (High, T17R2-01): every act of an open file backed
    store reloads through the guarded load path, and no flush
    writes an integrity signal over a record set that has not
    passed the load guards."""

    def test_reload_value_tamper_refused_at_act(self):
        store = self.make_store()
        payload = self.read_payload()
        payload["records"][0]["v"] = 999
        self.write_payload(payload)
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.read_run_record("r1")
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_reload_injected_money_record_refused_at_act(self):
        store = self.make_store()
        payload = self.read_payload()
        payload["records"].append(
            {"run_id": "inj", "amount": 5, "currency": "USD"})
        self.write_payload(payload)
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.index()
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_flush_does_not_reseal_tampered_set(self):
        store = self.make_store()
        payload = self.read_payload()
        payload["records"][0]["v"] = 999
        self.write_payload(payload)
        tampered_text = self.read_text()
        with self.assertRaises(mod10.LookupFailure):
            store.retain_run_record({"run_id": "r2", "v": 2})
        self.assertEqual(self.read_text(), tampered_text)

    def test_reload_deep_record_refused_in_store_file_form(self):
        store = self.make_store()
        payload = self.read_payload()
        payload["records"].append(deep_record(120))
        self.write_payload(payload)
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.index()
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])


class TestFW302IntegrityFamily(TempDirBase):
    """FW3-02 (High, T17R2-02): the store refuses in named form a
    file whose integrity member stands absent where the file
    carries records, whose signal stands recomputed in the
    unkeyed form, and whose member names stand duplicated."""

    def test_product_file_opens_clean(self):
        self.make_store()
        fresh = mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertEqual(fresh.index(), ["r1"])
        self.assertEqual(fresh.read_run_record("r1")["v"], 1)

    def test_open_missing_integrity_with_records_refused(self):
        self.make_store()
        payload = self.read_payload()
        del payload["integrity"]
        self.write_payload(payload)
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])
        self.assertIn("integrity", caught.exception.args[0])

    def test_open_unkeyed_recomputed_digest_refused(self):
        self.make_store()
        payload = self.read_payload()
        payload["records"][0]["v"] = 999
        payload["records"].append({"run_id": "injected", "v": 2})
        payload["integrity"] = old_unkeyed_digest(payload["records"])
        self.write_payload(payload)
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_open_duplicate_records_member_refused(self):
        self.make_store()
        clean = self.read_payload()
        tampered_records = [{"run_id": "r1", "v": 999}]
        text = (
            '{"store_kind": "sweep", "records": '
            + json.dumps(clean["records"])
            + ', "records": ' + json.dumps(tampered_records)
            + ', "integrity": "'
            + old_unkeyed_digest(tampered_records) + '"}')
        self.write_text(text)
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_open_duplicate_integrity_member_refused(self):
        self.make_store()
        clean = self.read_payload()
        text = (
            '{"store_kind": "sweep", "records": '
            + json.dumps(clean["records"])
            + ', "integrity": "bogus", "integrity": "'
            + clean["integrity"] + '"}')
        self.write_text(text)
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])


class TestFW309WhitespaceIdentifierAtLoad(TempDirBase):
    """FW3-09 (Medium, T17R2-09): the load path judges the
    identifier form the retention door judges, whitespace
    judged missing included."""

    def test_load_space_identifier_refused(self):
        self.write_payload({"store_kind": "sweep", "records": [
            {"run_id": " ", "v": 1}]})
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_load_tab_identifier_refused(self):
        self.write_payload({"store_kind": "sweep", "records": [
            {"run_id": "\t", "v": 1}]})
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])


class TestFW311UnreadableOrAbsentAtAct(TempDirBase):
    """FW3-11 (Medium, T17R2-11): every act of an open file
    backed store delivers an unreadable or absent store file
    in the named store file failure form, and no flush
    destroys retained records on an empty standing the file
    does not state."""

    def test_act_on_nonjson_file_named_failure(self):
        store = self.make_store()
        self.write_text("this is not json at all")
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.index()
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_act_on_deleted_file_named_failure(self):
        store = self.make_store()
        os.remove(self.path)
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.index()
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_retain_after_delete_refused_and_no_silent_rewrite(self):
        store = self.make_store()
        os.remove(self.path)
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.retain_run_record({"run_id": "r2", "v": 2})
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])
        self.assertFalse(os.path.exists(self.path))


class TestFW330NoUsableKindLabel(TempDirBase):
    """FW3-30 (Low, T17R2-30): opening a store file whose kind
    label stands absent or in no usable form stands refused in
    named form."""

    def test_open_null_kind_label_refused(self):
        self.write_payload({"store_kind": None, "records": []})
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_open_missing_kind_label_refused(self):
        self.write_payload({"records": []})
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="pilot", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])


class TestFW333KindCarriage(TempDirBase):
    """FW3-33 (Low, T17R2-33): the store constructor carries
    the kind as its stated kind text, judged through the
    canonical kind reading the module level doors use."""

    def test_constructor_stores_plain_kind_text(self):
        class AlwaysEqualText(str):
            def __eq__(self, other):
                return True

            def __ne__(self, other):
                return False

            __hash__ = str.__hash__

        store = mod10.RecorderStore(store_kind=AlwaysEqualText("sweep"))
        self.assertIs(type(store.store_kind), str)
        self.assertTrue(str.__eq__(store.store_kind, "sweep"))
        self.assertFalse(str.__eq__(store.store_kind, "pilot"))

    def test_constructor_bytes_kind_stores_plain_text(self):
        store = mod10.RecorderStore(store_kind=b"sweep")
        self.assertIs(type(store.store_kind), str)
        self.assertTrue(str.__eq__(store.store_kind, "sweep"))


class TestFW359ExtraTopLevelMembers(TempDirBase):
    """FW3-59 (Low, T17R2-59): the store open and flush doors
    state the standing of top level members outside the judged
    form, refusing them in named form at open."""

    def test_open_extra_top_level_member_refused(self):
        self.make_store()
        payload = self.read_payload()
        payload["operator_note"] = "placed by another hand"
        self.write_payload(payload)
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.RecorderStore(store_kind="sweep", path=self.path)
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])

    def test_reload_extra_top_level_member_refused(self):
        store = self.make_store()
        payload = self.read_payload()
        payload["operator_note"] = "placed by another hand"
        self.write_payload(payload)
        with self.assertRaises(mod10.LookupFailure) as caught:
            store.index()
        self.assertIn("could not be read as a store",
                      caught.exception.args[0])


if __name__ == "__main__":
    unittest.main()
