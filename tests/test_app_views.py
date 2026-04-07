import unittest

from app_views import build_points_csv, format_point_group_summary


class BuildPointsCsvTests(unittest.TestCase):
    def test_build_points_csv_formats_rows(self):
        csv_text = build_points_csv({"Mine A": [(1.23456789, 2.0, 3.1)]}, "m")
        lines = csv_text.strip().splitlines()

        self.assertEqual(lines[0], "deposit_type,x,y,z,z_unit")
        self.assertEqual(lines[1], "Mine A,1.234568,2.000000,3.100000,m")

    def test_build_points_csv_with_multiple_labels(self):
        csv_text = build_points_csv({"Mine A": [(1, 2, 3)], "Well B": [(4, 5, 6)]}, "m")
        lines = csv_text.strip().splitlines()

        self.assertEqual(lines[0], "deposit_type,x,y,z,z_unit")
        self.assertIn("Mine A,1.000000,2.000000,3.000000,m", lines)
        self.assertIn("Well B,4.000000,5.000000,6.000000,m", lines)

    def test_build_points_csv_header_only_when_no_points(self):
        csv_text = build_points_csv({}, "m")
        lines = csv_text.strip().splitlines()

        self.assertEqual(lines, ["deposit_type,x,y,z,z_unit"])

    def test_build_points_csv_orders_labels_stably(self):
        csv_text = build_points_csv({"Well B": [(4, 5, 6)], "Mine A": [(1, 2, 3)]}, "m")
        lines = csv_text.strip().splitlines()

        self.assertEqual(lines[1], "Mine A,1.000000,2.000000,3.000000,m")
        self.assertEqual(lines[2], "Well B,4.000000,5.000000,6.000000,m")

    def test_build_points_csv_quotes_labels_with_commas(self):
        csv_text = build_points_csv({"Mine, Sector A": [(1, 2, 3)]}, "m")
        lines = csv_text.strip().splitlines()

        self.assertEqual(lines[1], '"Mine, Sector A",1.000000,2.000000,3.000000,m')


class FormatPointGroupSummaryTests(unittest.TestCase):
    def test_format_point_group_summary_handles_singular(self):
        summary = format_point_group_summary(total_points=1, group_count=1)
        self.assertEqual(summary, "Loaded 1 point across 1 label group.")

    def test_format_point_group_summary_handles_plural(self):
        summary = format_point_group_summary(total_points=12, group_count=3)
        self.assertEqual(summary, "Loaded 12 points across 3 label groups.")


if __name__ == "__main__":
    unittest.main()