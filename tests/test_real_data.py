import unittest
from real_data import format_production_summary, get_sample_production_data
from usgs_data import format_usgs_summary, get_sample_usgs_mineral_data

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

    def test_format_usgs_summary_rejects_invalid_limit(self):
        with self.assertRaisesRegex(TypeError, "limit must be an integer or None"):
            format_usgs_summary(limit=1.5)

if __name__ == "__main__":
    unittest.main()