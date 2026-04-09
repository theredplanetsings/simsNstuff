import unittest

from csv_overlay import build_uploaded_points_template, parse_uploaded_points


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


if __name__ == "__main__":
    unittest.main()
