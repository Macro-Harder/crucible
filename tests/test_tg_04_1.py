import unittest

try:
    import crucible.mod05 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod05 absent, pinned behaviour unmet: " + behaviour)


def require_api(case, group, behaviour, names):
    require_surface(case, group, behaviour)
    for name in names:
        if hasattr(_surface_module, name):
            return getattr(_surface_module, name)
    case.fail(group + ": surface stands but no callable for pinned behaviour: " + behaviour)


class TestTG041(unittest.TestCase):
    def test_accepted_work_accounting(self):
        """
        Fixture: A day of work completions with known acceptance outcomes, including the external work issuance axis values. No inventory fixture.
        Pins: The work and acceptance counters that enter the AC-1 hash list and the denominator of the primary order parameter are computed from the same events, with numerator, denominator, and proportion stored apart, per Shape 14.
        Bar: The mapping states the bar in the companion failure path test of this group.
        Failure: Fails while crucible.mod05 stands absent, and fails if the counters are computed from different events or the parts stand unstored.
        """
        require_api(self, "TG-04.1", "work and acceptance counters computed from the same events with parts stored apart", ["work_credit", "accept_work", "credit_work"])
        surface = _surface_module
        events = [
            {"agent_identifier": "agent-a", "accepted": True},
            {"agent_identifier": "agent-a", "accepted": True},
            {"agent_identifier": "agent-a", "accepted": False},
            {"agent_identifier": "agent-a", "accepted": True},
        ]
        result = surface.work_credit(events)
        self.assertEqual(result["events_used"], 4)
        self.assertTrue(result["same_event_set"])
        counter = result["counters"]["agent-a"]
        self.assertEqual(counter["submitted"], 4)
        self.assertEqual(counter["accepted"], 3)
        self.assertEqual(counter["proportion"], {"numerator": 3, "denominator": 4})
        self.assertEqual(result["totals"]["proportion"], {"numerator": 3, "denominator": 4})

    def test_proportion_without_parts_fails(self):
        """
        Fixture: A day of work completions with known acceptance outcomes, as in the happy path test of this group, with the proportion stored without its numerator and denominator.
        Pins: A proportion is stored only with its numerator and denominator stored apart, per Shape 14, because AC-3 rederivation and the honest loss coverage tests read the parts, not the quotient alone.
        Bar: A proportion stored without its numerator and denominator fails this group.
        Failure: Fails while crucible.mod05 stands absent, and fails if a proportion stored without its parts is accepted.
        """
        require_api(self, "TG-04.1", "proportion stored without numerator and denominator is rejected", ["work_credit", "accept_work", "credit_work"])
        surface = _surface_module
        self.assertTrue(surface.validate_proportion({"numerator": 3, "denominator": 4}))
        self.assertFalse(surface.validate_proportion({"proportion": 0.75}))
        self.assertFalse(surface.validate_proportion({"numerator": 3}))
        with self.assertRaises(ValueError):
            surface.proportion_record(None, 4)
        with self.assertRaises(ValueError):
            surface.proportion_record(3, None)


if __name__ == "__main__":
    unittest.main()
