"""CSV upload parsing and validation for user-provided geological points."""

import csv
import io
import math


REQUIRED_COLUMNS = {"x", "y", "z"}
OPTIONAL_COLUMNS = {"label"}


def parse_uploaded_points(uploaded_bytes):
    """Parse uploaded CSV bytes into grouped points by label.

    Expected columns:
    - Required: x, y, z
    - Optional: label (defaults to "Uploaded")
    """
    if not isinstance(uploaded_bytes, (bytes, bytearray, memoryview)):
        raise TypeError("uploaded_bytes must be bytes-like.")

    payload = bytes(uploaded_bytes)

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc

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

        if not any((value or "").strip() for value in key_map.values()):
            continue

        try:
            x_val = float((key_map.get("x") or "").strip())
            y_val = float((key_map.get("y") or "").strip())
            z_val = float((key_map.get("z") or "").strip())

            if not all(math.isfinite(val) for val in (x_val, y_val, z_val)):
                raise ValueError("non-finite coordinate")
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric values at row {row_count}") from exc

        label = (key_map.get("label") or "Uploaded").strip() or "Uploaded"
        groups.setdefault(label, []).append((x_val, y_val, z_val))

    if row_count == 0:
        raise ValueError("CSV contains no data rows.")

    if not groups:
        raise ValueError("CSV contains no valid coordinate rows.")

    return groups
