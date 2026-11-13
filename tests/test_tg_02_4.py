"""Test group TG-02.4. Generator state in checkpoints.

Slice S-02, MOD-02 Seed and Stream Engine. Suite convention: this file tries
to import the product module for its slice, package crucible, module mod02,
and records whether the surface stands. While the surface stands absent, each
test fails with a message naming the pinned behaviour and its group.
This group pins carriage only, as its mapping entry states.
"""
import unittest

try:
    from crucible import mod02
    SURFACE = mod02
    SURFACE_ERROR = None
except Exception as exc:  # surface absent is the expected Step 13 state
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-02.4"


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": pinned behaviour not built: " + behaviour
            + " (surface crucible.mod02 stands absent: " + repr(SURFACE_ERROR) + ")"
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": pinned behaviour not built: " + behaviour
                + " (surface crucible.mod02 lacks " + attr + ")"
            )


class TestCheckpointGeneratorStateRoundTrip(unittest.TestCase):
    def test_checkpoint_generator_state_round_trip(self):
        """Fixture: a CheckpointManifest carrying generator state for every stream, resumed in the non detection scope, derived from the field list at Shape 12; no inventory fixture is assigned to this group in the mapping.
        Pins: the state the checkpoint holds is the state the resume path consumes, field for field, per operation C-01.
        Bar: this group pins carriage only; resume equality itself is pinned at TG-14.1 under AC-2 and carries the detection carve out stated there, and no equality claim beyond carriage is made here.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.4; with the surface present, a checkpoint whose held state differs from the consumed state in any field fails.
        """
        behaviour = "checkpoint generator state is consumed by the resume path field for field, per operation C-01"
        require_surface(self, behaviour, "checkpoint_generator_state", "resume_consumed_generator_state")
        held = SURFACE.checkpoint_generator_state(run_id="run-under-test")
        self.assertTrue(held)
        consumed = SURFACE.resume_consumed_generator_state(run_id="run-under-test", scope="non detection")
        self.assertEqual(held, consumed)

    def test_checkpoint_generator_state_field_mismatch_fails(self):
        """Fixture: a CheckpointManifest whose generator state for one stream differs from the state the resume path would consume for that stream, derived from the field list at Shape 12.
        Pins: a field level difference between the held state and the consumed state fails the carriage check, because the pin is field for field identity of carriage.
        Bar: this group pins carriage only, as the happy path test in this group states, and no resume equality verdict is claimed here.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-02.4; with the surface present, such a mismatch passing the carriage check fails.
        """
        behaviour = "a field level mismatch between checkpoint generator state held and consumed fails the C-01 carriage check"
        require_surface(self, behaviour, "validate_generator_state_carriage")
        held = {"stream a": {"position": "p1"}}
        consumed = {"stream a": {"position": "p2"}}
        self.assertFalse(SURFACE.validate_generator_state_carriage(held, consumed))
        self.assertTrue(SURFACE.validate_generator_state_carriage(held, held))


if __name__ == "__main__":
    unittest.main()
