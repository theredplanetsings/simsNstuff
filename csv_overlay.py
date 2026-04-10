"""CSV upload parsing and validation for user-provided geological points."""

import csv
import io
import math

import numpy as np


REQUIRED_COLUMNS = {"x", "y", "z"}
OPTIONAL_COLUMNS = {"label"}


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
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc

    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise ValueError("CSV is missing a header row.")

    normalized = {name.strip().lower() for name in reader.fieldnames if name}
    if not REQUIRED_COLUMNS.issubset(normalized):
        raise ValueError("CSV must include columns: x, y, z")

    bounds = _normalize_coordinate_bounds(coordinate_bounds)

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
            _validate_coordinate_bounds(x_val, y_val, z_val, bounds)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric values at row {row_count}") from exc

        label = (key_map.get("label") or "Uploaded").strip() or "Uploaded"
        groups.setdefault(label, []).append((x_val, y_val, z_val))

    if row_count == 0:
        raise ValueError("CSV contains no data rows.")

    if not groups:
        raise ValueError("CSV contains no valid coordinate rows.")

    return groups


def _normalize_coordinate_bounds(coordinate_bounds):
    if coordinate_bounds is None:
        return None

    if not isinstance(coordinate_bounds, tuple) or len(coordinate_bounds) != 2:
        raise TypeError("coordinate_bounds must be a (min_value, max_value) tuple.")

    min_value, max_value = coordinate_bounds
    if isinstance(min_value, bool) or isinstance(max_value, bool):
        raise TypeError("coordinate_bounds values must be numeric.")
    if not isinstance(min_value, (int, float)) or not isinstance(max_value, (int, float)):
        raise TypeError("coordinate_bounds values must be numeric.")
    if not (math.isfinite(min_value) and math.isfinite(max_value)):
        raise ValueError("coordinate_bounds values must be finite.")
    if min_value >= max_value:
        raise ValueError("coordinate_bounds min_value must be less than max_value.")

    return float(min_value), float(max_value)


def _validate_coordinate_bounds(x_val, y_val, z_val, bounds):
    if bounds is None:
        return

    min_value, max_value = bounds
    if not (min_value <= x_val <= max_value):
        raise ValueError("x out of bounds")
    if not (min_value <= y_val <= max_value):
        raise ValueError("y out of bounds")
    if not (min_value <= z_val <= max_value):
        raise ValueError("z out of bounds")
