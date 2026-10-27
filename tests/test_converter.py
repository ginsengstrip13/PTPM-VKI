import unittest

from converter import Converter


class ConverterTests(unittest.TestCase):
    def test_smallest_positive_value(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_positive_fraction_is_truncated(self):
        result = Converter.do(65.7)
        self.assertEqual(result, 65)
        self.assertIs(type(result), int)

    def test_value_just_below_upper_threshold(self):
        self.assertEqual(Converter.do(100.6), 100)

    def test_upper_threshold(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_value_above_upper_threshold(self):
        self.assertEqual(Converter.do(150.3), 1000)

    def test_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_value_closest_to_zero(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_lower_boundary_of_negative_truncation(self):
        self.assertEqual(Converter.do(-30.4), -35)

    def test_negative_saturation_threshold(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_value_below_negative_threshold(self):
        self.assertEqual(Converter.do(-94.5), -2000)


if __name__ == "__main__":
    unittest.main()
