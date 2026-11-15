import unittest

from crucible import mod08


class ReprRaising:
    def __repr__(self):
        raise RuntimeError("repr boom")


class ReprRaisingValue:
    def __repr__(self):
        raise ValueError("repr boom value")


class ReprRaisingType:
    def __repr__(self):
        raise TypeError("repr boom type")


class ReprRaisingFloat(float):
    def __repr__(self):
        raise RuntimeError("repr boom float")


class ReprRaisingInt(int):
    def __repr__(self):
        raise RuntimeError("repr boom int")


class StrRaising:
    def __str__(self):
        raise RuntimeError("str boom")


class StrRaisingValue:
    def __str__(self):
        raise ValueError("str boom value")


class StrRaisingStr(str):
    def __str__(self):
        raise RuntimeError("str boom str")


def profile_set_with(streams):
    return {
        "profiles": list(mod08.F06_PROFILES),
        "streams_per_profile": streams,
    }


class TestR17027ScoreProfilesRendering(unittest.TestCase):

    def assert_no_number_sentence(self, streams):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score_profiles(profile_set_with(streams))
        text = str(caught.exception)
        self.assertIn(
            "profile set rejected: the streams per profile "
            "value stands in no number form: ", text)
        self.assertGreater(
            len(text),
            len("profile set rejected: the streams per profile "
                "value stands in no number form: "))

    def test_repr_raising_object_runtime(self):
        self.assert_no_number_sentence(ReprRaising())

    def test_repr_raising_object_value(self):
        self.assert_no_number_sentence(ReprRaisingValue())

    def test_repr_raising_object_type(self):
        self.assert_no_number_sentence(ReprRaisingType())

    def test_control_plain_text_streams(self):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score_profiles(profile_set_with("abc"))
        self.assertEqual(
            str(caught.exception),
            "profile set rejected: the streams per profile "
            "value stands in no number form: 'abc'")

    def test_control_bool_streams(self):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score_profiles(profile_set_with(True))
        self.assertEqual(
            str(caught.exception),
            "profile set rejected: the streams per profile "
            "value stands in no number form: True")

    def test_control_finite_sentence_on_plain_float_form(self):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score_profiles(
                profile_set_with(ReprRaisingFloat(float("inf"))))
        self.assertEqual(
            str(caught.exception),
            "profile set rejected: the streams per profile "
            "value stands in no finite number form: inf")

    def test_control_below_count_int_form(self):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score_profiles(profile_set_with(ReprRaisingInt(5)))
        self.assertEqual(
            str(caught.exception),
            "profile set stands below the F-06 stream count")

    def test_control_valid_set_returns_record(self):
        result = mod08.score_profiles(profile_set_with(1000))
        self.assertEqual(result["fixture"], "F-06")
        self.assertEqual(result["profiles"], list(mod08.F06_PROFILES))


class TestR17028ValidateUseNamingRendering(unittest.TestCase):

    def assert_unnamed_sentence(self, use):
        with self.assertRaises(mod08.SilentUseMovement) as caught:
            mod08.validate_use_naming({"uses_named": [use]})
        text = str(caught.exception)
        self.assertIn("use naming check: a use stands unnamed: ", text)
        self.assertGreater(
            len(text), len("use naming check: a use stands unnamed: "))

    def test_str_raising_object_runtime(self):
        self.assert_unnamed_sentence(StrRaising())

    def test_str_raising_object_value(self):
        self.assert_unnamed_sentence(StrRaisingValue())

    def test_str_raising_str_subclass(self):
        self.assert_unnamed_sentence(StrRaisingStr("bogus"))

    def test_control_plain_bogus_use(self):
        with self.assertRaises(mod08.SilentUseMovement) as caught:
            mod08.validate_use_naming({"uses_named": ["bogus"]})
        self.assertEqual(
            str(caught.exception),
            "use naming check: a use stands unnamed: bogus")

    def test_control_lawful_use_returns_true(self):
        self.assertTrue(
            mod08.validate_use_naming({"uses_named": ["conformance"]}))

    def test_control_no_use_named(self):
        with self.assertRaises(mod08.SilentUseMovement) as caught:
            mod08.validate_use_naming({"uses_named": []})
        self.assertEqual(
            str(caught.exception),
            "use naming check: neither use stands named in the "
            "artefact")


if __name__ == "__main__":
    unittest.main()
