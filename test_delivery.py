import unittest

from delivery import calculate_delivery_cost


INVALID_RESULT = (-1, "0000-00-00")


class DeliveryCalculationTests(unittest.TestCase):
    def call_delivery(self, *args, **kwargs):
        """Return an exception as a value so invalid-input tests stay readable."""
        try:
            return calculate_delivery_cost(*args, **kwargs)
        except Exception as error:  # the contract promises a sentinel instead
            return error

    def test_returns_base_cost_for_standard_package(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 100, "обычный"),
            (700, "2026-09-04"),
        )

    def test_accepts_minimum_weight_boundary(self):
        self.assertEqual(
            calculate_delivery_cost(0.1, 1, "обычный"),
            (205, "2026-09-04"),
        )

    def test_rejects_weight_below_minimum(self):
        self.assertEqual(
            calculate_delivery_cost(0.09, 100, "обычный"),
            INVALID_RESULT,
        )

    def test_accepts_maximum_weight_boundary(self):
        self.assertEqual(
            calculate_delivery_cost(50.0, 5000, "обычный"),
            (37800, "2026-09-13"),
        )

    def test_rejects_weight_above_maximum(self):
        self.assertEqual(
            calculate_delivery_cost(50.01, 100, "обычный"),
            INVALID_RESULT,
        )

    def test_rejects_distance_outside_supported_range(self):
        for distance in (0, 5001):
            with self.subTest(distance=distance):
                self.assertEqual(
                    calculate_delivery_cost(1.0, distance, "обычный"),
                    INVALID_RESULT,
                )

    def test_rejects_unknown_package_type(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 100, "нестандартный"),
            INVALID_RESULT,
        )

    def test_applies_medium_weight_coefficient(self):
        self.assertEqual(
            calculate_delivery_cost(10.0, 100, "обычный"),
            (840, "2026-09-04"),
        )

    def test_applies_heavy_weight_coefficient(self):
        self.assertEqual(
            calculate_delivery_cost(20.0, 100, "обычный"),
            (1050, "2026-09-04"),
        )

    def test_weight_equal_to_five_has_no_coefficient(self):
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, "обычный"),
            (700, "2026-09-04"),
        )

    def test_adds_fragile_package_surcharge(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 100, "хрупкий"),
            (1000, "2026-09-04"),
        )

    def test_adds_dangerous_package_surcharge(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 100, "опасный"),
            (1700, "2026-09-04"),
        )

    def test_applies_express_price_discount(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 1000, "обычный", is_express=True),
            (2600, "2026-09-04"),
        )

    def test_calculates_regular_delivery_date_for_long_distance(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 1000, "обычный"),
            (5200, "2026-09-05"),
        )

    def test_express_delivery_takes_at_least_one_day(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 1, "обычный", is_express=True),
            (102, "2026-09-04"),
        )

    def test_rejects_non_numeric_weight(self):
        self.assertEqual(
            self.call_delivery("1", 100, "обычный"),
            INVALID_RESULT,
        )

    def test_rejects_non_numeric_distance(self):
        self.assertEqual(
            self.call_delivery(1.0, "100", "обычный"),
            INVALID_RESULT,
        )

    def test_rejects_non_boolean_express_flag(self):
        self.assertEqual(
            self.call_delivery(1.0, 100, "обычный", is_express="yes"),
            INVALID_RESULT,
        )

    def test_express_reduces_two_day_delivery_to_one_day(self):
        self.assertEqual(
            calculate_delivery_cost(1.0, 1000, "обычный", is_express=True)[1],
            "2026-09-04",
        )


if __name__ == "__main__":
    unittest.main()
