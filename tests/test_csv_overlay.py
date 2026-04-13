import unittest
from csv_overlay import build_uploaded_points_template, downsample_grouped_points, parse_uploaded_points

class TestCsvOverlay(unittest.TestCase):
    def test_build_uploaded_points_template_has_required_columns(self):
        csv_text = build_uploaded_points_template()
        lines = csv_text.strip().splitlines()

        self.assertEqual(lines[0], "x,y,z,label")
        self.assertGreaterEqual(len(lines), 2)

    def test_parse_uploaded_points_groups_labels(self):
        payload = (
            "x,y,z,label\n"
            "1,2,3,Mine A\n"
            "4,5,6,Mine A\n"
            "7,8,9,Well B\n"
        ).encode("utf-8")

        parsed = parse_uploaded_points(payload)

        self.assertIn("Mine A", parsed)
        self.assertIn("Well B", parsed)
        self.assertEqual(len(parsed["Mine A"]), 2)
        self.assertEqual(parsed["Well B"][0], (7.0, 8.0, 9.0))

    def test_parse_uploaded_points_defaults_label(self):
        payload = "x,y,z\n1,2,3\n".encode("utf-8")

        parsed = parse_uploaded_points(payload)

        self.assertIn("Uploaded", parsed)
        self.assertEqual(parsed["Uploaded"], [(1.0, 2.0, 3.0)])

    def test_parse_uploaded_points_requires_xyz_columns(self):
        payload = "a,b,c\n1,2,3\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "CSV must include columns: x, y, z"):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_rejects_bad_numeric_values(self):
        payload = "x,y,z\n1,two,3\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "Invalid numeric values at row 1"):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_rejects_blank_rows(self):
        payload = "x,y,z\n\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "CSV contains no data rows."):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_rejects_non_utf8_payload(self):
        payload = b"\xff\xfe\x00\x00"

        with self.assertRaisesRegex(ValueError, "CSV must be UTF-8 encoded"):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_rejects_non_bytes_payload(self):
        with self.assertRaisesRegex(TypeError, "uploaded_bytes must be bytes-like"):
            parse_uploaded_points("x,y,z\n1,2,3\n")

    def test_parse_uploaded_points_accepts_bytearray_payload(self):
        payload = bytearray("x,y,z\n1,2,3\n", "utf-8")

        parsed = parse_uploaded_points(payload)

        self.assertEqual(parsed, {"Uploaded": [(1.0, 2.0, 3.0)]})

    def test_parse_uploaded_points_rejects_header_only_csv(self):
        payload = "x,y,z\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "CSV contains no data rows."):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_uses_default_label_when_blank(self):
        payload = "x,y,z,label\n1,2,3,\n".encode("utf-8")

        parsed = parse_uploaded_points(payload)

        self.assertEqual(parsed, {"Uploaded": [(1.0, 2.0, 3.0)]})

    def test_parse_uploaded_points_accepts_whitespace_in_headers(self):
        payload = " X , Y , Z , Label \n1,2,3,Mine A\n".encode("utf-8")

        parsed = parse_uploaded_points(payload)

        self.assertEqual(parsed, {"Mine A": [(1.0, 2.0, 3.0)]})

    def test_parse_uploaded_points_rejects_duplicate_normalized_headers(self):
        payload = "x, X ,y,z\n1,2,3,4\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "CSV contains duplicate column names"):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_rejects_non_finite_values(self):
        payload = "x,y,z\n1,nan,3\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "Invalid numeric values at row 1"):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_ignores_unrelated_columns(self):
        payload = "x,y,z,label,notes\n1,2,3,Mine A,priority\n".encode("utf-8")

        parsed = parse_uploaded_points(payload)

        self.assertEqual(parsed, {"Mine A": [(1.0, 2.0, 3.0)]})

    def test_parse_uploaded_points_rejects_whitespace_only_rows(self):
        payload = "x,y,z\n , , \n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "CSV contains no valid coordinate rows"):
            parse_uploaded_points(payload)

    def test_parse_uploaded_points_applies_coordinate_bounds(self):
        payload = "x,y,z\n1,2,3\n".encode("utf-8")

        parsed = parse_uploaded_points(payload, coordinate_bounds=(-10, 10))

        self.assertEqual(parsed, {"Uploaded": [(1.0, 2.0, 3.0)]})

    def test_parse_uploaded_points_rejects_out_of_bounds_coordinate(self):
        payload = "x,y,z\n99999,2,3\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "Invalid numeric values at row 1"):
            parse_uploaded_points(payload, coordinate_bounds=(-10, 10))

    def test_parse_uploaded_points_rejects_bad_coordinate_bounds_shape(self):
        payload = "x,y,z\n1,2,3\n".encode("utf-8")

        with self.assertRaisesRegex(TypeError, r"coordinate_bounds must be a \(min_value, max_value\) tuple"):
            parse_uploaded_points(payload, coordinate_bounds=[-10, 10])

    def test_parse_uploaded_points_rejects_inverted_coordinate_bounds(self):
        payload = "x,y,z\n1,2,3\n".encode("utf-8")

        with self.assertRaisesRegex(ValueError, "coordinate_bounds min_value must be less than max_value"):
            parse_uploaded_points(payload, coordinate_bounds=(5, 1))

    def test_parse_uploaded_points_rejects_boolean_coordinate_bounds_values(self):
        payload = "x,y,z\n1,2,3\n".encode("utf-8")

        with self.assertRaisesRegex(TypeError, "coordinate_bounds values must be numeric"):
            parse_uploaded_points(payload, coordinate_bounds=(False, 10))

    def test_downsample_grouped_points_keeps_total_under_limit(self):
        groups = {
            "A": [(float(i), 0.0, 0.0) for i in range(20)],
            "B": [(float(i), 1.0, 1.0) for i in range(20)],
        }

        sampled = downsample_grouped_points(groups, max_points=10, seed=42)
        total = sum(len(v) for v in sampled.values())

        self.assertEqual(total, 10)

    def test_downsample_grouped_points_is_deterministic(self):
        groups = {"A": [(float(i), 0.0, 0.0) for i in range(50)]}

        first = downsample_grouped_points(groups, max_points=12, seed=42)
        second = downsample_grouped_points(groups, max_points=12, seed=42)

        self.assertEqual(first, second)

    def test_downsample_grouped_points_passthrough_when_under_limit(self):
        groups = {"A": [(1.0, 2.0, 3.0)]}

        sampled = downsample_grouped_points(groups, max_points=10, seed=42)

        self.assertEqual(sampled, groups)

    def test_downsample_grouped_points_rejects_non_positive_max(self):
        with self.assertRaisesRegex(ValueError, "max_points must be greater than 0"):
            downsample_grouped_points({"A": [(1.0, 2.0, 3.0)]}, max_points=0, seed=42)

if __name__ == "__main__":
    unittest.main()