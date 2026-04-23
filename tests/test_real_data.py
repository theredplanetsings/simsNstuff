import unittest
from real_data import format_production_summary, get_latest_production_values, get_sample_production_data
from usgs_data import format_usgs_summary, get_latest_usgs_values, get_sample_usgs_mineral_data

class RealDataHelpersTests(unittest.TestCase):
    def test_get_sample_production_data_has_expected_series(self):
        data = get_sample_production_data()

        self.assertIn("coal_production", data)
        self.assertIn("crude_oil_production", data)
        self.assertIn("natural_gas_production", data)
        self.assertGreaterEqual(len(data["coal_production"]), 5)

    def test_format_production_summary_contains_key_sections(self):
        summary = format_production_summary()

        self.assertIn("U.S. Production Trends", summary)
        self.assertIn("Coal Production", summary)
        self.assertIn("Crude Oil", summary)
        self.assertIn("Natural Gas", summary)

    def test_format_production_summary_honors_limit(self):
        summary = format_production_summary(limit=1)

        self.assertEqual(summary.count("- 2024:"), 3)

    def test_format_production_summary_rejects_invalid_limit(self):
        with self.assertRaisesRegex(ValueError, "limit must be greater than 0"):
            format_production_summary(limit=0)

    def test_format_production_summary_rejects_too_large_limit(self):
        with self.assertRaisesRegex(ValueError, "limit must be less than or equal to 5"):
            format_production_summary(limit=6)

    def test_get_latest_production_values_returns_stable_order(self):
        latest = get_latest_production_values(limit=2)

        self.assertEqual(len(latest), 2)
        self.assertEqual(latest[0]["series"], "coal_production")
        self.assertEqual(latest[1]["series"], "crude_oil_production")

    def test_get_latest_production_values_rejects_invalid_limit(self):
        with self.assertRaisesRegex(TypeError, "limit must be an integer or None"):
            get_latest_production_values(limit=1.5)

    def test_get_latest_production_values_rejects_too_large_limit(self):
        with self.assertRaisesRegex(ValueError, "limit must be less than or equal to 3"):
            get_latest_production_values(limit=4)

    def test_get_latest_production_values_skips_empty_series(self):
        import real_data

        original = real_data.get_sample_production_data
        real_data.get_sample_production_data = lambda: {
            "coal_production": [],
            "crude_oil_production": [("2024", 1.0)],
            "natural_gas_production": [("2024", 2.0)],
        }
        try:
            latest = get_latest_production_values()
            self.assertEqual([entry["series"] for entry in latest], ["crude_oil_production", "natural_gas_production"])
        finally:
            real_data.get_sample_production_data = original

class UsgsDataHelpersTests(unittest.TestCase):
    def test_get_sample_usgs_data_contains_expected_commodities(self):
        data = get_sample_usgs_mineral_data()

        for commodity in ["Gold", "Silver", "Iron", "Copper", "Coal"]:
            self.assertIn(commodity, data)
            self.assertGreaterEqual(len(data[commodity]), 5)

    def test_format_usgs_summary_contains_snapshot_header(self):
        summary = format_usgs_summary()

        self.assertIn("USGS-Style Mineral Production Snapshot", summary)
        self.assertIn("Gold", summary)
        self.assertIn("Copper", summary)

    def test_format_usgs_summary_is_alphabetically_ordered(self):
        summary = format_usgs_summary()

        self.assertLess(summary.find("**Coal"), summary.find("**Copper"))
        self.assertLess(summary.find("**Copper"), summary.find("**Gold"))

    def test_format_usgs_summary_honors_limit(self):
        summary = format_usgs_summary(limit=2)

        self.assertEqual(summary.count("- **"), 2)

    def test_format_usgs_summary_formats_values_with_separators(self):
        summary = format_usgs_summary(limit=1)
        self.assertIn("8,400", summary)

    def test_format_usgs_summary_rejects_invalid_limit(self):
        with self.assertRaisesRegex(TypeError, "limit must be an integer or None"):
            format_usgs_summary(limit=1.5)

    def test_format_usgs_summary_rejects_too_large_limit(self):
        with self.assertRaisesRegex(ValueError, "limit must be less than or equal to 5"):
            format_usgs_summary(limit=6)

    def test_get_latest_usgs_values_returns_stable_order(self):
        latest = get_latest_usgs_values(limit=2)

        self.assertEqual(len(latest), 2)
        self.assertEqual(latest[0]["mineral"], "Coal")
        self.assertEqual(latest[1]["mineral"], "Copper")

    def test_get_latest_usgs_values_rejects_invalid_limit(self):
        with self.assertRaisesRegex(TypeError, "limit must be an integer or None"):
            get_latest_usgs_values(limit=1.5)

    def test_usgs_helpers_skip_missing_series(self):
        import usgs_data

        original = usgs_data.get_sample_usgs_mineral_data
        usgs_data.get_sample_usgs_mineral_data = lambda: {
            "Gold": [("2024", 1)],
            "Copper": [],
        }
        try:
            summary = format_usgs_summary()
            latest = get_latest_usgs_values()
            self.assertIn("Gold", summary)
            self.assertNotIn("Copper", summary)
            self.assertEqual([entry["mineral"] for entry in latest], ["Gold"])
        finally:
            usgs_data.get_sample_usgs_mineral_data = original

if __name__ == "__main__":
    unittest.main()