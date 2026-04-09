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


if __name__ == "__main__":
    unittest.main()
