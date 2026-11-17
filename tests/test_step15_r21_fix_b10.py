import unittest

from crucible import mod06


class LieStr(str):
    def __new__(cls, stored, reading):
        obj = str.__new__(cls, stored)
        obj._reading = reading
        return obj

    def __str__(self):
        return self._reading

    def __repr__(self):
        return self._reading


class RaiseStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __str__(self):
        raise RuntimeError("string reading refused")


def contract_sentence(**kwargs):
    try:
        mod06.escrow_contract_state("contract-1", **kwargs)
    except ValueError as error:
        return str(error)
    return ""


def pause_sentence(variant):
    try:
        mod06.pause_cap(variant)
    except ValueError as error:
        return str(error)
    return ""


class TestR20052VariantSentence(unittest.TestCase):
    def test_lying_variant_names_stored(self):
        sentence = contract_sentence(variant=LieStr("X9", "B-4"))
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_raising_variant_names_stored(self):
        sentence = contract_sentence(variant=RaiseStr("X9"))
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_bytes_variant_names_stored(self):
        sentence = contract_sentence(variant=b"X9")
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_plain_variant_control(self):
        sentence = contract_sentence(variant="X9")
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_valid_b4_control(self):
        state = mod06.escrow_contract_state(
            "contract-1", variant="B-4")
        self.assertEqual(state["variant"], "B-4")

    def test_valid_b3_control(self):
        state = mod06.escrow_contract_state(
            "contract-1", variant="B-3")
        self.assertEqual(state["variant"], "B-3")


class TestR20053LienStateSentence(unittest.TestCase):
    def test_lying_lien_names_stored(self):
        sentence = contract_sentence(
            variant="B-4",
            lien_state=LieStr("bogus lien", "no lien in force"))
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_raising_lien_names_stored(self):
        sentence = contract_sentence(
            variant="B-4", lien_state=RaiseStr("bogus lien"))
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_bytes_lien_names_stored(self):
        sentence = contract_sentence(
            variant="B-4", lien_state=b"bogus lien")
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_plain_lien_control(self):
        sentence = contract_sentence(
            variant="B-4", lien_state="bogus lien")
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_valid_lien_control(self):
        state = mod06.escrow_contract_state(
            "contract-1", variant="B-4", lien_state="released")
        self.assertEqual(state["lien_state"], "released")


class TestR20054PauseCapSentence(unittest.TestCase):
    def test_lying_variant_names_stored(self):
        sentence = pause_sentence(LieStr("X9", "B-4"))
        self.assertIn("for an unknown variant: X9", sentence)

    def test_raising_variant_names_stored(self):
        sentence = pause_sentence(RaiseStr("X9"))
        self.assertIn("for an unknown variant: X9", sentence)

    def test_bytes_variant_names_stored(self):
        sentence = pause_sentence(b"X9")
        self.assertIn("for an unknown variant: X9", sentence)

    def test_plain_variant_control(self):
        sentence = pause_sentence("X9")
        self.assertIn("for an unknown variant: X9", sentence)

    def test_valid_b4_control(self):
        result = mod06.pause_cap("B-4")
        self.assertEqual(result["total_percent"], 400)

    def test_valid_b3_control(self):
        result = mod06.pause_cap("B-3")
        self.assertEqual(result["variant"], "B-3")


if __name__ == "__main__":
    unittest.main()
