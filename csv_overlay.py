"""CSV upload parsing and validation for user-provided geological points."""

import csv
import io


REQUIRED_COLUMNS = {"x", "y", "z"}
OPTIONAL_COLUMNS = {"label"}


def parse_uploaded_points(uploaded_bytes):
    """Parse uploaded CSV bytes into grouped points by label.

    Expected columns:
    - Required: x, y, z
    - Optional: label (defaults to "Uploaded")
    """
    text = uploaded_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise ValueError("CSV is missing a header row.")

    normalized = {name.strip().lower() for name in reader.fieldnames if name}
    if not REQUIRED_COLUMNS.issubset(normalized):
        raise ValueError("CSV must include columns: x, y, z")

    groups = {}
    row_count = 0
    for row in reader:
        row_count += 1
        key_map = {k.strip().lower(): v for k, v in row.items() if k is not None}
        try:
            x_val = float(key_map["x"])
            y_val = float(key_map["y"])
            z_val = float(key_map["z"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric values at row {row_count}") from exc

        label = key_map.get("label", "Uploaded").strip() or "Uploaded"
        groups.setdefault(label, []).append((x_val, y_val, z_val))

    if row_count == 0:
        raise ValueError("CSV contains no data rows.")

    return groups
