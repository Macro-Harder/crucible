# Step 15 rerun Round 9 fix wave 9 tests, Builder 11.
# Row R9-039, the product README opening description.
# Plain file reading only.
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


def readme_text():
    return README.read_text(encoding="utf-8")


class TestR9039ReadmeHorizon(unittest.TestCase):

    def test_no_years_claim(self):
        text = readme_text().lower()
        self.assertNotIn("simulated years", text)
        self.assertNotIn("year", text)

    def test_corrected_horizon_statement(self):
        text = readme_text()
        self.assertIn("across extended runs", text)
        self.assertIn(
            "hundreds of agents trading, vouching, and defecting "
            "across extended runs",
            text,
        )

    def test_opening_description_stands(self):
        text = readme_text()
        self.assertIn("Crucible is a Monte Carlo agent society simulator.", text)
        self.assertIn("trust rules, escrow, and detection", text)
        self.assertIn(
            "to measure the conditions under which bad actors start winning.",
            text,
        )

    def test_readiness_language_stands(self):
        text = readme_text()
        self.assertIn(
            "Status: in development. There is no release yet "
            "and nothing to install.",
            text,
        )

    def test_no_build_or_register_talk(self):
        text = readme_text()
        self.assertNotIn("180", text)
        self.assertNotIn("register", text.lower())
        self.assertNotIn("Step 15", text)
        self.assertNotIn("fix wave", text.lower())

    def test_trimmed_size_class_stands(self):
        size = README.stat().st_size
        self.assertEqual(size, 436)


if __name__ == "__main__":
    unittest.main()
