"""Step 17 fix wave 10, Builder 3 tests for FW10-02 (Medium,
T17R9-02), at crucible.mod10.retain_run_record and
crucible.mod10.read_run_record.

The filing shape, O2-R9-01 of Orange 2: a plain record mapping
with two entries, the key 10 to the power 5000 (an integer of
5001 digits) mapped to the text "x" and the key "run_id" mapped
to a run identifier text, handed to retain_run_record with the
store kind "sweep".

Every judgement in this file stands on stored value in code,
never on a repr or a string rendering of a returned record
(T17R3-23): no test in this file calls str or repr on a record
carrying the huge integer key, on the key itself, or on any
record read back from the store. The digits of the huge integer
stand judged by a chunk built digit reading in this file, built
from base integer operations alone. Message lengths stand
measured in code on the stored message string of an exception,
in the filing form.

The defect tests pin the cured behaviour the row states: the
handing stands refused in the named form of the module stating
the door, the ground, and the next step, with no bare
interpreter digit limit text escaping and no record or stub
retained behind a refusal, or the handing stands served whole,
as the module own standing forms govern. A test that finds the
handing served whole passes on that standing and states it in
its name; a test that finds a refusal judges the refusal form
whole. The readback limbs run in fresh processes, in the
filing form.

Copyright: J.P. Picard aka Macro-Harder.
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

from crucible import mod10

HUGE = 10 ** 5000
DIGIT_LIMIT_TEXT = (
    "Exceeds the limit (4300 digits) for integer string conversion")


def _digits(value):
    """The decimal digits of a plain integer, built in digit
    chunks from base integer operations, so an integer past
    the interpreter digit limit stands judged whole without
    any string conversion of the integer itself."""
    remaining = int.__int__(value)
    sign = ""
    if remaining < 0:
        sign = "-"
        remaining = -remaining
    chunks = []
    while remaining:
        remaining, chunk = divmod(remaining, 10 ** 9)
        chunks.append(chunk)
    if not chunks:
        return "0"
    parts = [str(chunks[-1])]
    for chunk in reversed(chunks[:-1]):
        parts.append(str(chunk).rjust(9, "0"))
    return sign + "".join(parts)


def _huge_keys(record):
    return [
        key for key in dict.keys(record)
        if isinstance(key, int) and not isinstance(key, bool)]


def _judge_handing(test, label, fn, args):
    """Run one handing and judge its standing by stored value.

    Returns ("served", record) where the door serves the
    handing, or ("refused", exception) where it refuses. A
    refusal stands judged whole here: it never carries the
    bare interpreter digit limit text, and where it stands as
    a bare ValueError of 117 characters carrying that text
    the test fails on that stored form."""
    try:
        record = fn(*args)
    except BaseException as exc:
        message = str(exc)
        test.assertNotIn(
            DIGIT_LIMIT_TEXT, message,
            label + " escaped with bare interpreter digit limit text")
        test.assertFalse(
            len(message) == 117 and "integer string conversion" in message,
            label + " escaped in the filing bare form at 117 characters")
        return ("refused", exc)
    return ("served", record)


def _judge_refusal_form(test, label, exc):
    """Judge one refusal in the named form of the module: the
    door, a ground in product words, and a next step stand in
    the stored message."""
    message = str(exc)
    test.assertTrue(
        "retain_run_record" in message or "read_run_record" in message
        or "lookup" in message.lower() or "record" in message.lower(),
        label + " refusal names no door and no record ground: "
        + message[:200])
    test.assertIn(
        "next step", message,
        label + " refusal states no next step: " + message[:200])


def _judge_served_record(test, label, record, run_id):
    """Judge one served record whole by stored value: the huge
    integer key stands present with its digits whole and its
    value standing, and the run identifier stands as handed."""
    test.assertIsInstance(record, dict, label + " served no record")
    huge = _huge_keys(record)
    test.assertEqual(
        len(huge), 1, label + " served record carries no huge key")
    test.assertEqual(
        _digits(huge[0]), "1" + "0" * 5000,
        label + " huge key digits stand moved")
    test.assertEqual(
        dict.__getitem__(record, huge[0]), "x",
        label + " huge key value stands moved")
    test.assertEqual(
        dict.get(record, "run_id"), run_id,
        label + " run identifier stands moved")


_FRESH_PROBE = '''
import sys
sys.path.insert(0, sys.argv[1])
from crucible import mod10

HUGE = 10 ** 5000
LIMIT = "Exceeds the limit"

def digits(value):
    remaining = int.__int__(value)
    chunks = []
    while remaining:
        remaining, chunk = divmod(remaining, 10 ** 9)
        chunks.append(chunk)
    if not chunks:
        return "0"
    parts = [str(chunks[-1])]
    for chunk in reversed(chunks[:-1]):
        parts.append(str(chunk).rjust(9, "0"))
    return "".join(parts)

def attempt(fn, args):
    try:
        return ("served", fn(*args))
    except BaseException as exc:
        return ("exc", exc)

standing, value = attempt(
    mod10.read_run_record, ("never-retained-xyz", "sweep"))
assert standing == "exc", "control read served"
assert type(value).__name__ == "LookupFailure", type(value).__name__
assert len(str(value)) == 249, len(str(value))
print("CONTROL_NEVER 249 LookupFailure")

standing, value = attempt(
    mod10.retain_run_record,
    ({HUGE: "x", "run_id": "probe6-id"}, "sweep"))
if standing == "exc":
    message = str(value)
    assert LIMIT not in message, "bare digit limit text at retention"
    assert len(message) != 117, "bare 117 character form at retention"
    print("RETENTION_REFUSED_NAMED " + type(value).__name__)
    standing2, value2 = attempt(
        mod10.read_run_record, ("probe6-id", "sweep"))
    assert standing2 == "exc", "refused identifier read back served"
    assert type(value2).__name__ == "LookupFailure", (
        "refused identifier read back as " + type(value2).__name__)
    print("READBACK_AFTER_REFUSAL LookupFailure", len(str(value2)))
else:
    record = value
    huge = [k for k in dict.keys(record)
            if isinstance(k, int) and not isinstance(k, bool)]
    assert len(huge) == 1, "served record carries no huge key"
    assert digits(huge[0]) == "1" + "0" * 5000, "huge key digits moved"
    assert dict.__getitem__(record, huge[0]) == "x", "huge value moved"
    assert dict.get(record, "run_id") == "probe6-id", "run id moved"
    print("RETENTION_SERVED_WHOLE")
    standing2, value2 = attempt(
        mod10.read_run_record, ("probe6-id", "sweep"))
    assert standing2 == "served", "retained identifier read refused"
    record2 = value2
    huge2 = [k for k in dict.keys(record2)
             if isinstance(k, int) and not isinstance(k, bool)]
    assert len(huge2) == 1, "readback carries no huge key"
    assert digits(huge2[0]) == "1" + "0" * 5000, "readback digits moved"
    assert dict.__getitem__(record2, huge2[0]) == "x", "readback value moved"
    assert dict.get(record2, "run_id") == "probe6-id", "readback id moved"
    print("READBACK_SERVED_WHOLE")

standing, value = attempt(
    mod10.read_run_record, ("other-id-abc", "sweep"))
assert standing == "exc", "other unretained read served"
assert type(value).__name__ == "LookupFailure", type(value).__name__
assert len(str(value)) == 243, len(str(value))
print("CONTROL_OTHER 243 LookupFailure")
print("FRESH_PROBE_DONE")
'''


class TestFW1002PlainShape(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_plain_shape_retention_standing(self):
        standing, value = _judge_handing(
            self, "plain retention", mod10.retain_run_record,
            ({HUGE: "x", "run_id": "fw10-plain-a"}, "sweep"))
        if standing == "refused":
            _judge_refusal_form(self, "plain retention", value)
        else:
            _judge_served_record(
                self, "plain retention", value, "fw10-plain-a")

    def test_plain_shape_readback_standing(self):
        standing, value = _judge_handing(
            self, "plain retention", mod10.retain_run_record,
            ({HUGE: "x", "run_id": "fw10-plain-b"}, "sweep"))
        standing2, value2 = _judge_handing(
            self, "plain readback", mod10.read_run_record,
            ("fw10-plain-b", "sweep"))
        if standing == "refused":
            _judge_refusal_form(self, "plain retention", value)
            self.assertEqual(
                standing2, "refused",
                "readback of a refused identifier stands served")
            self.assertIsInstance(
                value2, mod10.LookupFailure,
                "readback of a refused identifier stands in no "
                "LookupFailure form")
        else:
            self.assertEqual(
                standing2, "served",
                "readback of a retained identifier stands refused")
            _judge_served_record(
                self, "plain readback", value2, "fw10-plain-b")

    def test_plain_shape_filing_sequence_fresh_process(self):
        product_root = pathlib.Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as scratch:
            probe = pathlib.Path(scratch) / "fw10_fresh_probe.py"
            probe.write_text(_FRESH_PROBE, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(probe), str(product_root)],
                capture_output=True, text=True)
        self.assertEqual(
            proc.returncode, 0,
            "fresh process filing sequence failed: "
            + proc.stdout[-800:] + proc.stderr[-800:])
        self.assertIn("CONTROL_NEVER 249 LookupFailure", proc.stdout)
        self.assertIn("CONTROL_OTHER 243 LookupFailure", proc.stdout)
        self.assertTrue(
            "RETENTION_SERVED_WHOLE" in proc.stdout
            or "RETENTION_REFUSED_NAMED" in proc.stdout,
            "fresh process states no retention standing: "
            + proc.stdout[-800:])
        if "RETENTION_SERVED_WHOLE" in proc.stdout:
            self.assertIn("READBACK_SERVED_WHOLE", proc.stdout)
        else:
            self.assertIn("READBACK_AFTER_REFUSAL LookupFailure",
                          proc.stdout)
        self.assertIn("FRESH_PROBE_DONE", proc.stdout)


class TestFW1002BuiltShapes(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_built_shape_extra_fields_huge_key_standing(self):
        built = {
            "run_id": "fw10-built-a",
            "run_identifier": "fw10-built-a",
            "kind": "sweep",
            HUGE: "x",
        }
        standing, value = _judge_handing(
            self, "built retention", mod10.retain_run_record,
            (built, "sweep"))
        standing2, value2 = _judge_handing(
            self, "built readback", mod10.read_run_record,
            ("fw10-built-a", "sweep"))
        if standing == "refused":
            _judge_refusal_form(self, "built retention", value)
            self.assertEqual(standing2, "refused")
            self.assertIsInstance(value2, mod10.LookupFailure)
        else:
            self.assertEqual(standing2, "served")
            _judge_served_record(
                self, "built readback", value2, "fw10-built-a")

    def test_huge_integer_value_standing(self):
        record = {"run_id": "fw10-value-a", "amount_field": HUGE}
        standing, value = _judge_handing(
            self, "value retention", mod10.retain_run_record,
            (record, "sweep"))
        standing2, value2 = _judge_handing(
            self, "value readback", mod10.read_run_record,
            ("fw10-value-a", "sweep"))
        if standing == "refused":
            _judge_refusal_form(self, "value retention", value)
            self.assertEqual(standing2, "refused")
            self.assertIsInstance(value2, mod10.LookupFailure)
        else:
            self.assertEqual(standing2, "served")
            carried = dict.get(value2, "amount_field")
            self.assertIsInstance(carried, int)
            self.assertEqual(_digits(carried), "1" + "0" * 5000)

    def test_nested_huge_integer_key_standing(self):
        record = {"run_id": "fw10-nest-a", "inner": {HUGE: "y"}}
        standing, value = _judge_handing(
            self, "nested retention", mod10.retain_run_record,
            (record, "sweep"))
        standing2, value2 = _judge_handing(
            self, "nested readback", mod10.read_run_record,
            ("fw10-nest-a", "sweep"))
        if standing == "refused":
            _judge_refusal_form(self, "nested retention", value)
            self.assertEqual(standing2, "refused")
            self.assertIsInstance(value2, mod10.LookupFailure)
        else:
            self.assertEqual(standing2, "served")
            inner = dict.get(value2, "inner")
            self.assertIsInstance(inner, dict)
            huge = _huge_keys(inner)
            self.assertEqual(len(huge), 1)
            self.assertEqual(_digits(huge[0]), "1" + "0" * 5000)
            self.assertEqual(dict.__getitem__(inner, huge[0]), "y")

    def test_file_backed_store_huge_key_standing(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = str(pathlib.Path(scratch) / "store.json")
            store = mod10.new_store("sweep", path)
            standing, value = _judge_handing(
                self, "file retention", store.retain_run_record,
                ({HUGE: "x", "run_id": "fw10-file-a"},))
            fresh = mod10.new_store("sweep", path)
            standing2, value2 = _judge_handing(
                self, "file readback", fresh.read_run_record,
                ("fw10-file-a",))
            if standing == "refused":
                _judge_refusal_form(self, "file retention", value)
                self.assertEqual(standing2, "refused")
                self.assertIsInstance(value2, mod10.LookupFailure)
            else:
                self.assertEqual(standing2, "served")
                self.assertEqual(
                    dict.get(value2, "run_id"), "fw10-file-a")
                digit_keys = [
                    key for key in dict.keys(value2)
                    if isinstance(key, str) and len(key) == 5001]
                self.assertEqual(len(digit_keys), 1)
                self.assertEqual(digit_keys[0], "1" + "0" * 5000)
                self.assertEqual(
                    dict.__getitem__(value2, digit_keys[0]), "x")


class TestFW1002Controls(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_control_never_retained_lookup_failure_249(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.read_run_record("never-retained-xyz", "sweep")
        self.assertEqual(len(str(caught.exception)), 249)

    def test_control_other_unretained_lookup_failure_243(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.read_run_record("other-id-abc", "sweep")
        self.assertEqual(len(str(caught.exception)), 243)

    def test_control_missing_id_lookup_failure_241(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.read_run_record("missing-id", "sweep")
        self.assertEqual(len(str(caught.exception)), 241)

    def test_control_ordinary_record_served_whole(self):
        record = {"run_id": "fw10-ordinary-a", "kind": "sweep"}
        returned = mod10.retain_run_record(record, "sweep")
        self.assertEqual(dict.get(returned, "run_id"), "fw10-ordinary-a")
        back = mod10.read_run_record("fw10-ordinary-a", "sweep")
        self.assertEqual(dict.get(back, "run_id"), "fw10-ordinary-a")
        self.assertEqual(dict.get(back, "kind"), "sweep")

    def test_control_huge_text_record_served_whole(self):
        record = {"run_id": "fw10-big-a", "payload": "y" * 50000}
        mod10.retain_run_record(record, "sweep")
        back = mod10.read_run_record("fw10-big-a", "sweep")
        self.assertEqual(dict.get(back, "payload"), "y" * 50000)


if __name__ == "__main__":
    unittest.main()
