"""CSV upload parsing and validation for user-provided geological points."""
import csv
import io
import math
import numpy as np

REQUIRED_COLUMNS = {"x", "y", "z"}
OPTIONAL_COLUMNS = {"label"}
MAX_LABEL_LENGTH = 80

def build_uploaded_points_template():
    """Return a small CSV template for mine/well coordinate uploads."""
    return "x,y,z,label\n0,0,-100,Example Site\n10,5,-120,Example Site\n"

def downsample_grouped_points(groups, max_points, seed):
    """Deterministically downsample grouped points to an overall max count."""
    if not isinstance(groups, dict):
        raise TypeError("groups must be a dictionary of label -> point list.")
    if not isinstance(max_points, int) or isinstance(max_points, bool):
        raise TypeError("max_points must be an integer.")
    if max_points <= 0:
        raise ValueError("max_points must be greater than 0.")

    _validate_groups_for_downsampling(groups)

    total_points = sum(len(points) for points in groups.values())
    if total_points <= max_points:
        return {label: list(points) for label, points in groups.items()}

    if not isinstance(seed, int) or isinstance(seed, bool):
        raise TypeError("seed must be an integer.")

    rng = np.random.default_rng(seed)
    sampled = {label: [] for label in groups}

    all_points = []
    for label in sorted(groups):
        all_points.extend((label, point) for point in groups[label])

    indices = np.arange(len(all_points))
    keep = rng.choice(indices, size=max_points, replace=False)
    for idx in np.sort(keep):
        label, point = all_points[idx]
        sampled[label].append(point)

    return {label: points for label, points in sampled.items() if points}

def _validate_groups_for_downsampling(groups):
    for label, points in groups.items():
        if not isinstance(points, (list, tuple)):
            raise TypeError(f"points for label '{label}' must be a list or tuple.")
        for point in points:
            if not isinstance(point, (list, tuple)) or len(point) != 3:
                raise ValueError(f"invalid point shape for label '{label}'; expected (x, y, z).")
            x_val, y_val, z_val = point
            for axis_value in (x_val, y_val, z_val):
                if isinstance(axis_value, bool) or not isinstance(axis_value, (int, float, np.integer, np.floating)):
                    raise TypeError(f"point coordinates for label '{label}' must be numeric.")
                if not math.isfinite(axis_value):
                    raise ValueError(f"point coordinates for label '{label}' must be finite.")

def parse_uploaded_points(uploaded_bytes, coordinate_bounds=None):
    """Parse uploaded CSV bytes into grouped points by label.

    Expected columns:
    - Required: x, y, z
    - Optional: label (defaults to "Uploaded")
    """
    if not isinstance(uploaded_bytes, (bytes, bytearray, memoryview)):
        raise TypeError("uploaded_bytes must be bytes-like.")

    payload = bytes(uploaded_bytes)

    try:
        # Accept UTF-8 with or without BOM for common spreadsheet exports.
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc

    text = _strip_comment_lines(text)

    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise ValueError("CSV is missing a header row.")

    normalized = _normalize_fieldnames(reader.fieldnames)
    if not REQUIRED_COLUMNS.issubset(normalized):
        raise ValueError("CSV must include columns: x, y, z")

    bounds = _normalize_coordinate_bounds(coordinate_bounds)

    groups = {}
    row_count = 0
    for row in reader:
        row_count += 1
        row_number = reader.line_num - 1
        key_map = {k.strip().lower(): v for k, v in row.items() if k is not None}

        if not any((value or "").strip() for value in key_map.values()):
            continue

        x_val = _parse_coordinate_value(key_map, "x", row_number)
        y_val = _parse_coordinate_value(key_map, "y", row_number)
        z_val = _parse_coordinate_value(key_map, "z", row_number)
        _validate_coordinate_bounds(x_val, y_val, z_val, bounds, row_number)

        label = _normalize_label(key_map.get("label"), row_number)
        groups.setdefault(label, []).append((x_val, y_val, z_val))

    if row_count == 0:
        raise ValueError("CSV contains no data rows.")

    if not groups:
        raise ValueError("CSV contains no valid coordinate rows.")

    return groups

def _strip_comment_lines(text):
    lines = text.splitlines()
    filtered = [line for line in lines if not line.lstrip().startswith("#")]
    return "\n".join(filtered)

def _normalize_coordinate_bounds(coordinate_bounds):
    if coordinate_bounds is None:
        return None

    if not isinstance(coordinate_bounds, tuple) or len(coordinate_bounds) != 2:
        raise TypeError("coordinate_bounds must be a (min_value, max_value) tuple.")

    min_value, max_value = coordinate_bounds
    if isinstance(min_value, bool) or isinstance(max_value, bool):
        raise TypeError("coordinate_bounds values must be numeric.")
    numeric_types = (int, float, np.integer, np.floating)
    if not isinstance(min_value, numeric_types) or not isinstance(max_value, numeric_types):
        raise TypeError("coordinate_bounds values must be numeric.")
    if not (math.isfinite(min_value) and math.isfinite(max_value)):
        raise ValueError("coordinate_bounds values must be finite.")
    if min_value >= max_value:
        raise ValueError("coordinate_bounds min_value must be less than max_value.")

    return float(min_value), float(max_value)

def _normalize_fieldnames(fieldnames):
    normalized = []
    for name in fieldnames:
        if name is None:
            continue
        key = name.strip().lower()
        if key:
            normalized.append(key)

    if len(set(normalized)) != len(normalized):
        raise ValueError("CSV contains duplicate column names.")

    return set(normalized)

def _parse_coordinate_value(key_map, field_name, row_number):
    raw_value = (key_map.get(field_name) or "").strip()

    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric values at row {row_number}") from exc

    if not math.isfinite(value):
        raise ValueError(f"Invalid numeric values at row {row_number}")

    return value

def _validate_coordinate_bounds(x_val, y_val, z_val, bounds, row_number):
    if bounds is None:
        return

    min_value, max_value = bounds
    if not (min_value <= x_val <= max_value):
        raise ValueError(f"x out of bounds at row {row_number}")
    if not (min_value <= y_val <= max_value):
        raise ValueError(f"y out of bounds at row {row_number}")
    if not (min_value <= z_val <= max_value):
        raise ValueError(f"z out of bounds at row {row_number}")

def _normalize_label(raw_label, row_number):
    label = (raw_label or "Uploaded").strip() or "Uploaded"
    if len(label) > MAX_LABEL_LENGTH:
        raise ValueError(
            f"Label too long at row {row_number}; maximum length is {MAX_LABEL_LENGTH} characters"
        )
    return label