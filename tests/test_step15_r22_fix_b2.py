"""Step 15, second run, fix wave 22, Builder 2 pins.

Group 2, row R22-002: crucible/mod02.py derivation_input_record
at its parameter rendering, crucible/mod02.py
run_record_derivation_fields at its parameter dict reading,
and typed_derivation_input standing on the first act, MOD-02.
The derivation acts stand cured so a stored parameter value
stands read through the stored pair form, with no
dict.__getitem__ re-read through the supplied key, so a
colliding key whose equality reading raises once armed never
escapes bare at the parameter limbs.

Pins whose names carry control stand as the controls,
passing on the pristine tree and on the cured tree alike.
Every other pin stands distinguishing, failing or erroring
on the pristine tree and passing on the cured tree.
"""

import unittest

from crucible import mod02


class CollidingKey(str):
    """A text key storing one text, hashing as another stated
    text, whose equality and inequality readings raise
    RuntimeError once the class flag stands up."""

    armed = False
    collide_with = "alpha"

    def __hash__(self):
        return str.__hash__(CollidingKey.collide_with)

    def __eq__(self, other):
        if CollidingKey.armed:
            raise RuntimeError("armed equality raises")
        return str.__eq__(self, other)

    def __ne__(self, other):
        if CollidingKey.armed:
            raise RuntimeError("armed inequality raises")
        return str.__ne__(self, other)


def colliding_params(colliding_first=True):
    """Build a parameter mapping carrying the plain key alpha
    storing 1 beside a further key storing zzz-other, hashing
    as alpha, in the stated insertion order. The class flags
    stand disarmed on return."""
    CollidingKey.collide_with = "alpha"
    CollidingKey.armed = False
    params = {}
    if colliding_first:
        params[CollidingKey("zzz-other")] = "zzz-value"
        params["alpha"] = "1"
    else:
        params["alpha"] = "1"
        params[CollidingKey("zzz-other")] = "zzz-value"
    return params


def record_with_params(params):
    return {
        "derivation_version": "v1",
        "domain": "screening",
        "root_seed_reference": "seed-1",
        "scenario_identifier": "scen-1",
        "run_identifier": "run-1",
        "stream_class_identifier": "class-1",
        "parameter_values": params,
    }


class Base(unittest.TestCase):
    def setUp(self):
        CollidingKey.armed = False
        CollidingKey.collide_with = "alpha"

    def tearDown(self):
        CollidingKey.armed = False
        CollidingKey.collide_with = "alpha"


class TestR22002DerivationInputRecord(Base):
    def test_record_colliding_first_armed_renders_both(self):
        record = record_with_params(colliding_params(True))
        CollidingKey.armed = True
        try:
            result = mod02.derivation_input_record(record)
        finally:
            CollidingKey.armed = False
        self.assertEqual(
            result["parameter_values"],
            ("alpha=1", "zzz-other=zzz-value"))
        self.assertEqual(result["domain"], "screening")
        self.assertEqual(result["derivation_version_string"], "v1")
        self.assertEqual(result["recorded_root_seed"], "seed-1")
        self.assertEqual(result["scenario_identifier"], "scen-1")
        self.assertEqual(result["run_identifier"], "run-1")
        self.assertEqual(
            result["stream_class_identifier"], "class-1")

    def test_record_colliding_second_armed_renders_both(self):
        record = record_with_params(colliding_params(False))
        CollidingKey.armed = True
        try:
            result = mod02.derivation_input_record(record)
        finally:
            CollidingKey.armed = False
        self.assertEqual(
            result["parameter_values"],
            ("alpha=1", "zzz-other=zzz-value"))
        self.assertEqual(result["domain"], "screening")
        self.assertEqual(result["derivation_version_string"], "v1")

    def test_record_control_plain_record(self):
        record = record_with_params({"beta": "2", "alpha": "1"})
        result = mod02.derivation_input_record(record)
        self.assertEqual(
            result["parameter_values"], ("alpha=1", "beta=2"))
        self.assertEqual(result["domain"], "screening")
        self.assertEqual(result["derivation_version_string"], "v1")
        self.assertEqual(result["recorded_root_seed"], "seed-1")

    def test_record_control_colliding_unarmed(self):
        record = record_with_params(colliding_params(True))
        result = mod02.derivation_input_record(record)
        self.assertEqual(
            result["parameter_values"],
            ("alpha=1", "zzz-other=zzz-value"))

    def test_record_control_non_dict(self):
        self.assertEqual(mod02.derivation_input_record("nope"), {})


class TestR22002TypedDerivationInput(Base):
    def test_typed_colliding_first_armed_renders_both(self):
        record = record_with_params(colliding_params(True))
        CollidingKey.armed = True
        try:
            result = mod02.typed_derivation_input(record)
        finally:
            CollidingKey.armed = False
        self.assertEqual(
            result.values["parameter_values"],
            ("alpha=1", "zzz-other=zzz-value"))
        self.assertEqual(result.values["domain"], "screening")
        self.assertEqual(
            result.values["derivation_version_string"], "v1")

    def test_typed_colliding_second_armed_renders_both(self):
        record = record_with_params(colliding_params(False))
        CollidingKey.armed = True
        try:
            result = mod02.typed_derivation_input(record)
        finally:
            CollidingKey.armed = False
        self.assertEqual(
            result.values["parameter_values"],
            ("alpha=1", "zzz-other=zzz-value"))
        self.assertEqual(result.values["domain"], "screening")

    def test_typed_control_plain_record(self):
        record = record_with_params({"alpha": "1"})
        result = mod02.typed_derivation_input(record)
        self.assertEqual(
            result.values["parameter_values"], ("alpha=1",))
        self.assertEqual(result.values["domain"], "screening")
        self.assertEqual(
            result.values["derivation_version_string"], "v1")


class TestR22002RunRecordDerivationFields(Base):
    def test_run_record_colliding_first_armed_renders_both(self):
        record = record_with_params(colliding_params(True))
        CollidingKey.armed = True
        try:
            result = mod02.run_record_derivation_fields(record)
        finally:
            CollidingKey.armed = False
        self.assertEqual(result["derivation_version"], "v1")
        self.assertEqual(
            result["parameter_values"],
            {"alpha": "1", "zzz-other": "zzz-value"})
        self.assertEqual(
            list(result["parameter_values"].keys()),
            ["alpha", "zzz-other"])

    def test_run_record_colliding_second_armed_renders_both(self):
        record = record_with_params(colliding_params(False))
        CollidingKey.armed = True
        try:
            result = mod02.run_record_derivation_fields(record)
        finally:
            CollidingKey.armed = False
        self.assertEqual(result["derivation_version"], "v1")
        self.assertEqual(
            result["parameter_values"],
            {"alpha": "1", "zzz-other": "zzz-value"})
        self.assertEqual(
            list(result["parameter_values"].keys()),
            ["alpha", "zzz-other"])

    def test_run_record_control_plain_sorted(self):
        record = record_with_params(
            {"z": "last", "a": "first", "m": "mid"})
        result = mod02.run_record_derivation_fields(record)
        self.assertEqual(result["derivation_version"], "v1")
        self.assertEqual(
            list(result["parameter_values"].keys()),
            ["a", "m", "z"])
        self.assertEqual(
            result["parameter_values"],
            {"a": "first", "m": "mid", "z": "last"})

    def test_run_record_control_colliding_unarmed(self):
        record = record_with_params(colliding_params(True))
        result = mod02.run_record_derivation_fields(record)
        pairs = sorted(
            (str.__str__(key), item)
            for key, item in dict.items(
                result["parameter_values"]))
        self.assertEqual(
            pairs, [("alpha", "1"), ("zzz-other", "zzz-value")])

    def test_run_record_control_non_dict(self):
        self.assertEqual(
            mod02.run_record_derivation_fields("nope"),
            {"derivation_version": None, "parameter_values": {}})


if __name__ == "__main__":
    unittest.main()
