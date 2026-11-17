import unittest

from crucible import mod09


class LieFive:
    """An object in no charged form whose repr reading answers 5."""

    def __repr__(self):
        return "5"


class LieZero:
    """An object in no charged form whose repr reading answers 0."""

    def __repr__(self):
        return "0"


class LieTwo:
    """An object in no charged form whose repr reading answers 2."""

    def __repr__(self):
        return "2"


class LieOnePointFive:
    """An object in no charged form whose repr reading
    answers 1.5."""

    def __repr__(self):
        return "1.5"


class LieRangeForm:
    """An object in no range form whose repr reading answers a
    range form."""

    def __repr__(self):
        return "[0, 5]"


class LieClassListForm:
    """An object in no class list form whose repr reading answers
    a class list form."""

    def __repr__(self):
        return "['alpha', 'beta']"


class LieListForm:
    """An object in no list form whose repr reading answers a
    list form."""

    def __repr__(self):
        return "['alpha']"


class LieRecordForm:
    """An object in no record form whose repr reading answers a
    record form."""

    def __repr__(self):
        return "{'fixture': 'F-26'}"


class RaisingRepr:
    """An object in no charged form whose repr reading raises."""

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class LyingStr:
    """An object outside the fixed class whose string reading
    answers alpha, a member of the class."""

    def __str__(self):
        return "alpha"


class RaisingStr:
    """An object outside the fixed class whose string reading
    raises."""

    def __str__(self):
        raise RuntimeError("string reading raises")


class LyingRungFive(int):
    """A ladder position storing an outside rung whose repr
    reading answers 5, a rung inside the whole rungs."""

    def __repr__(self):
        return "5"


class LyingRungThree(int):
    """A ladder position storing an outside rung whose repr
    reading answers 3, a rung inside the whole rungs."""

    def __repr__(self):
        return "3"


def refusal(act, *args, **kwargs):
    try:
        act(*args, **kwargs)
    except mod09.NamedAttackerFailure as failure:
        return str(failure)
    raise AssertionError("the act delivered no refusal")


class TestR21025Distinguishing(unittest.TestCase):
    def test_range_object_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": LieFive(),
             "in_protocol_payoff": 0})
        self.assertEqual(
            message,
            "external profit sweep rejected: the stated range "
            "stands in no range form: LieFive()")

    def test_range_object_repr_range_form_named_on_stored_form(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": LieRangeForm(),
             "in_protocol_payoff": 0})
        self.assertEqual(
            message,
            "external profit sweep rejected: the stated range "
            "stands in no range form: LieRangeForm()")


class TestR21025Controls(unittest.TestCase):
    def test_plain_number_range_named_as_five(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": 5, "in_protocol_payoff": 0})
        self.assertEqual(
            message,
            "external profit sweep rejected: the stated range "
            "stands in no range form: 5")


class TestR21026Distinguishing(unittest.TestCase):
    def test_range_value_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": [LieFive()],
             "in_protocol_payoff": 0})
        self.assertEqual(
            message,
            "external profit sweep rejected: a stated range "
            "value stands in no numeric form: LieFive()")

    def test_range_value_repr_zero_named_on_stored_form(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": [LieZero()],
             "in_protocol_payoff": 0})
        self.assertEqual(
            message,
            "external profit sweep rejected: a stated range "
            "value stands in no numeric form: LieZero()")


class TestR21026Controls(unittest.TestCase):
    def test_plain_text_range_value_named_as_x(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": ["x"],
             "in_protocol_payoff": 0})
        self.assertEqual(
            message,
            "external profit sweep rejected: a stated range "
            "value stands in no numeric form: 'x'")


class TestR21027Distinguishing(unittest.TestCase):
    def test_largest_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": [0, 10],
             "in_protocol_payoff": 0},
            largest_in_protocol_payoff=LieFive())
        self.assertEqual(
            message,
            "external profit sweep rejected: the largest in "
            "protocol payoff stands in no numeric form: LieFive()")

    def test_largest_repr_two_named_on_stored_form(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": [0, 10],
             "in_protocol_payoff": 0},
            largest_in_protocol_payoff=LieTwo())
        self.assertEqual(
            message,
            "external profit sweep rejected: the largest in "
            "protocol payoff stands in no numeric form: LieTwo()")


class TestR21027Controls(unittest.TestCase):
    def test_plain_text_largest_named_as_x(self):
        message = refusal(
            mod09.sweep_external_profit,
            {"external_profit_range": [0, 10],
             "in_protocol_payoff": 0},
            largest_in_protocol_payoff="x")
        self.assertEqual(
            message,
            "external profit sweep rejected: the largest in "
            "protocol payoff stands in no numeric form: 'x'")


class TestR21028Distinguishing(unittest.TestCase):
    def test_class_object_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.run_record_carriage,
            LieFive(), 0, "v1", "ptr", "1")
        self.assertEqual(
            message,
            "run record rejected: the fixed strategy class "
            "stands in no class list form: LieFive()")

    def test_class_object_repr_list_form_named_on_stored_form(self):
        message = refusal(
            mod09.run_record_carriage,
            LieClassListForm(), 0, "v1", "ptr", "1")
        self.assertEqual(
            message,
            "run record rejected: the fixed strategy class "
            "stands in no class list form: LieClassListForm()")


class TestR21028Controls(unittest.TestCase):
    def test_plain_number_class_named_as_five(self):
        message = refusal(
            mod09.run_record_carriage, 5, 0, "v1", "ptr", "1")
        self.assertEqual(
            message,
            "run record rejected: the fixed strategy class "
            "stands in no class list form: 5")


class TestR21029Distinguishing(unittest.TestCase):
    def test_strategies_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], 0, "v1", "ptr", "1", strategies=LieFive())
        self.assertEqual(
            message,
            "run record rejected: the strategies exercised "
            "stand in no list form: LieFive()")

    def test_strategies_repr_list_form_named_on_stored_form(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], 0, "v1", "ptr", "1",
            strategies=LieListForm())
        self.assertEqual(
            message,
            "run record rejected: the strategies exercised "
            "stand in no list form: LieListForm()")


class TestR21029Controls(unittest.TestCase):
    def test_plain_number_strategies_named_as_five(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], 0, "v1", "ptr", "1", strategies=5)
        self.assertEqual(
            message,
            "run record rejected: the strategies exercised "
            "stand in no list form: 5")


class TestR21030Distinguishing(unittest.TestCase):
    def test_rung_storing_nine_repr_five_named_as_nine(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], LyingRungFive(9), "v1", "ptr", "1")
        self.assertEqual(
            message,
            "run record rejected: the ladder position stands "
            "outside the whole rungs 0 to 6 of the search "
            "ladder: 9")

    def test_rung_storing_eight_repr_three_named_as_eight(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], LyingRungThree(8), "v1", "ptr", "1")
        self.assertEqual(
            message,
            "run record rejected: the ladder position stands "
            "outside the whole rungs 0 to 6 of the search "
            "ladder: 8")


class TestR21030Controls(unittest.TestCase):
    def test_plain_rung_nine_named_as_nine(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], 9, "v1", "ptr", "1")
        self.assertEqual(
            message,
            "run record rejected: the ladder position stands "
            "outside the whole rungs 0 to 6 of the search "
            "ladder: 9")


class TestR21031Distinguishing(unittest.TestCase):
    def test_strategy_str_alpha_named_on_stored_form(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], 0, "v1", "ptr", "1",
            strategies=[LyingStr()])
        self.assertEqual(
            message,
            "strategy outside the fixed class stands "
            "rejected: LyingStr()")

    def test_strategy_str_raising_named_on_stored_form(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], 0, "v1", "ptr", "1",
            strategies=[RaisingStr()])
        self.assertEqual(
            message,
            "strategy outside the fixed class stands "
            "rejected: RaisingStr()")


class TestR21031Controls(unittest.TestCase):
    def test_plain_number_strategy_named_as_five(self):
        message = refusal(
            mod09.run_record_carriage,
            ["alpha"], 0, "v1", "ptr", "1", strategies=[5])
        self.assertEqual(
            message,
            "strategy outside the fixed class stands "
            "rejected: 5")


class TestR21032Distinguishing(unittest.TestCase):
    def test_candidate_harm_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.bond_search,
            [{"harm": LieFive(), "attacker_cost": 2}])
        self.assertEqual(
            message,
            "bond parameter search rejected: a candidate "
            "carries a harm or a cost in no numeric form: "
            "dict({'attacker_cost'=2, 'harm'=LieFive()})")

    def test_candidate_harm_repr_raising_named_on_stored_form(self):
        message = refusal(
            mod09.bond_search,
            [{"harm": RaisingRepr(), "attacker_cost": 2}])
        self.assertEqual(
            message,
            "bond parameter search rejected: a candidate "
            "carries a harm or a cost in no numeric form: "
            "dict({'attacker_cost'=2, 'harm'=RaisingRepr()})")


class TestR21032Controls(unittest.TestCase):
    def test_candidate_plain_text_harm_named_in_refusal(self):
        message = refusal(
            mod09.bond_search,
            [{"harm": "x", "attacker_cost": 2}])
        self.assertTrue(message.startswith(
            "bond parameter search rejected: a candidate "
            "carries a harm or a cost in no numeric form: "))
        self.assertIn("'x'", message)


class TestR21033Distinguishing(unittest.TestCase):
    def test_factor_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.bond_search,
            [{"parameter_set": {"stake": 1}}],
            griefing_evaluator=lambda params: LieFive())
        self.assertEqual(
            message,
            "bond parameter search rejected: a griefing "
            "factor stands in no finite numeric form: LieFive()")

    def test_factor_repr_one_point_five_named_on_stored_form(self):
        message = refusal(
            mod09.bond_search,
            [{"parameter_set": {"stake": 1}}],
            griefing_evaluator=lambda params: LieOnePointFive())
        self.assertEqual(
            message,
            "bond parameter search rejected: a griefing "
            "factor stands in no finite numeric form: "
            "LieOnePointFive()")


class TestR21033Controls(unittest.TestCase):
    def test_plain_text_factor_named_as_x(self):
        message = refusal(
            mod09.bond_search,
            [{"parameter_set": {"stake": 1}}],
            griefing_evaluator=lambda params: "x")
        self.assertEqual(
            message,
            "bond parameter search rejected: a griefing "
            "factor stands in no finite numeric form: 'x'")


class TestR21034Distinguishing(unittest.TestCase):
    def test_case_use_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.build_search_record,
            {}, [], [], [], case_uses=[LieFive()])
        self.assertEqual(
            message,
            "search record rejected: a case use stands in "
            "no record form: LieFive()")

    def test_case_use_repr_record_form_named_on_stored_form(self):
        message = refusal(
            mod09.build_search_record,
            {}, [], [], [], case_uses=[LieRecordForm()])
        self.assertEqual(
            message,
            "search record rejected: a case use stands in "
            "no record form: LieRecordForm()")


class TestR21034Controls(unittest.TestCase):
    def test_plain_number_case_use_named_as_five(self):
        message = refusal(
            mod09.build_search_record,
            {}, [], [], [], case_uses=[5])
        self.assertEqual(
            message,
            "search record rejected: a case use stands in "
            "no record form: 5")


class TestR21035Distinguishing(unittest.TestCase):
    def test_carriage_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.readout, {"run_record": LieFive()})
        self.assertEqual(
            message,
            "readout rejected: the run record carriage stands "
            "in no record form: LieFive()")

    def test_carriage_repr_raising_named_on_stored_form(self):
        message = refusal(
            mod09.readout, {"run_record": RaisingRepr()})
        self.assertEqual(
            message,
            "readout rejected: the run record carriage stands "
            "in no record form: RaisingRepr()")


class TestR21035Controls(unittest.TestCase):
    def test_plain_number_carriage_named_as_five(self):
        message = refusal(mod09.readout, {"run_record": 5})
        self.assertEqual(
            message,
            "readout rejected: the run record carriage stands "
            "in no record form: 5")


class TestR21036Distinguishing(unittest.TestCase):
    def test_exercised_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.readout,
            {"run_record": {
                "ladder_position": 0,
                "strategies_exercised": LieFive()}})
        self.assertEqual(
            message,
            "readout rejected: the strategies exercised stand "
            "in no list form: LieFive()")

    def test_exercised_repr_raising_named_on_stored_form(self):
        message = refusal(
            mod09.readout,
            {"run_record": {
                "ladder_position": 0,
                "strategies_exercised": RaisingRepr()}})
        self.assertEqual(
            message,
            "readout rejected: the strategies exercised stand "
            "in no list form: RaisingRepr()")


class TestR21036Controls(unittest.TestCase):
    def test_plain_number_exercised_named_as_five(self):
        message = refusal(
            mod09.readout,
            {"run_record": {
                "ladder_position": 0,
                "strategies_exercised": 5}})
        self.assertEqual(
            message,
            "readout rejected: the strategies exercised stand "
            "in no list form: 5")


class TestR21037Distinguishing(unittest.TestCase):
    def test_swept_repr_five_named_on_stored_form(self):
        message = refusal(
            mod09.readout,
            {"run_record": {"ladder_position": 0},
             "external_profit_swept_values": LieFive()})
        self.assertEqual(
            message,
            "readout rejected: the external profit swept "
            "values stand in no list form: LieFive()")

    def test_swept_repr_raising_named_on_stored_form(self):
        message = refusal(
            mod09.readout,
            {"run_record": {"ladder_position": 0},
             "external_profit_swept_values": RaisingRepr()})
        self.assertEqual(
            message,
            "readout rejected: the external profit swept "
            "values stand in no list form: RaisingRepr()")


class TestR21037Controls(unittest.TestCase):
    def test_plain_number_swept_named_as_five(self):
        message = refusal(
            mod09.readout,
            {"run_record": {"ladder_position": 0},
             "external_profit_swept_values": 5})
        self.assertEqual(
            message,
            "readout rejected: the external profit swept "
            "values stand in no list form: 5")


class TestR21038Distinguishing(unittest.TestCase):
    def test_witness_repr_five_named_on_stored_form(self):
        message = refusal(mod09.attacker_cost_summary, LieFive())
        self.assertEqual(
            message,
            "attacker cost summary rejected: the witness run "
            "stands in no record form: LieFive()")

    def test_witness_repr_record_form_named_on_stored_form(self):
        message = refusal(
            mod09.attacker_cost_summary, LieRecordForm())
        self.assertEqual(
            message,
            "attacker cost summary rejected: the witness run "
            "stands in no record form: LieRecordForm()")


class TestR21038Controls(unittest.TestCase):
    def test_plain_number_witness_named_as_five(self):
        message = refusal(mod09.attacker_cost_summary, 5)
        self.assertEqual(
            message,
            "attacker cost summary rejected: the witness run "
            "stands in no record form: 5")


class TestR21039Distinguishing(unittest.TestCase):
    def test_witness_repr_five_named_on_stored_form(self):
        message = refusal(mod09.witness_carriage, LieFive())
        self.assertEqual(
            message,
            "witness carriage rejected: the witness run "
            "stands in no record form: LieFive()")

    def test_witness_repr_record_form_named_on_stored_form(self):
        message = refusal(mod09.witness_carriage, LieRecordForm())
        self.assertEqual(
            message,
            "witness carriage rejected: the witness run "
            "stands in no record form: LieRecordForm()")


class TestR21039Controls(unittest.TestCase):
    def test_plain_number_witness_named_as_five(self):
        message = refusal(mod09.witness_carriage, 5)
        self.assertEqual(
            message,
            "witness carriage rejected: the witness run "
            "stands in no record form: 5")


if __name__ == "__main__":
    unittest.main()
