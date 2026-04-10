import unittest

import numpy as np
import json

from app_views import (
    _build_cross_section_figure,
    _resolve_preset,
    build_group_summary_csv,
    build_metadata_json,
    build_points_csv,
    format_point_group_summary,
    summarize_point_groups,
)


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


class ResolvePresetTests(unittest.TestCase):
    def test_resolve_preset_returns_preset_values(self):
        presets = {"Custom": None, "A": {"foo": 1}}
        self.assertEqual(_resolve_preset("A", presets), {"foo": 1})

    def test_resolve_preset_returns_empty_dict_for_custom(self):
        presets = {"Custom": None}
        self.assertEqual(_resolve_preset("Custom", presets), {})

    def test_resolve_preset_returns_empty_dict_for_unknown(self):
        presets = {"Custom": None}
        self.assertEqual(_resolve_preset("Unknown", presets), {})


class SummarizePointGroupsTests(unittest.TestCase):
    def test_summarize_point_groups_builds_expected_metrics(self):
        summaries = summarize_point_groups({"Mine A": [(0.0, 1.0, -10.0), (2.0, 3.0, -6.0)]})

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0]["Label"], "Mine A")
        self.assertEqual(summaries[0]["Count"], 2)
        self.assertEqual(summaries[0]["Min Z"], -10.0)
        self.assertEqual(summaries[0]["Max Z"], -6.0)
        self.assertEqual(summaries[0]["Mean Z"], -8.0)

    def test_summarize_point_groups_ignores_empty_groups(self):
        summaries = summarize_point_groups({"Mine A": []})
        self.assertEqual(summaries, [])


class BuildGroupSummaryCsvTests(unittest.TestCase):
    def test_build_group_summary_csv_writes_header_and_rows(self):
        csv_text = build_group_summary_csv(
            [
                {
                    "Label": "Mine A",
                    "Count": 2,
                    "Min Z": -10.0,
                    "Max Z": -6.0,
                    "Mean Z": -8.0,
                    "Centroid X": 1.0,
                    "Centroid Y": 2.0,
                    "Centroid Z": -8.0,
                }
            ]
        )
        lines = csv_text.strip().splitlines()

        self.assertEqual(
            lines[0],
            "Label,Count,Min Z,Max Z,Mean Z,Centroid X,Centroid Y,Centroid Z",
        )
        self.assertEqual(lines[1], "Mine A,2,-10.0,-6.0,-8.0,1.0,2.0,-8.0")

    def test_build_group_summary_csv_header_only_when_empty(self):
        csv_text = build_group_summary_csv([])
        self.assertEqual(
            csv_text.strip(),
            "Label,Count,Min Z,Max Z,Mean Z,Centroid X,Centroid Y,Centroid Z",
        )


class CrossSectionFigureTests(unittest.TestCase):
    def test_cross_section_uses_x_axis_for_xz(self):
        points = {"A": np.array([[1.0, 2.0, -3.0]])}
        fig = _build_cross_section_figure(points, "X-Z", "Test")

        self.assertEqual(fig.layout.xaxis.title.text, "X (km)")
        self.assertEqual(fig.layout.yaxis.title.text, "Z (m)")
        self.assertEqual(len(fig.data), 1)

    def test_cross_section_uses_y_axis_for_yz(self):
        points = {"A": np.array([[1.0, 2.0, -3.0]])}
        fig = _build_cross_section_figure(points, "Y-Z", "Test")

        self.assertEqual(fig.layout.xaxis.title.text, "Y (km)")


class MetadataJsonTests(unittest.TestCase):
    def test_build_metadata_json_contains_expected_fields(self):
        payload = build_metadata_json("Mineral Deposits", {"seed": 42})
        data = json.loads(payload)

        self.assertEqual(data["view"], "Mineral Deposits")
        self.assertEqual(data["parameters"]["seed"], 42)
        self.assertIn("generated_at", data)


if __name__ == "__main__":
    unittest.main()