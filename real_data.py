"""Sample real-world commodity data helpers for the Streamlit app."""
SERIES_CONFIG = (
    ("coal_production", "Coal Production", "M tons", "Million short tons"),
    ("crude_oil_production", "Crude Oil", "M bbl/day", "Million barrels/day"),
    ("natural_gas_production", "Natural Gas", "Bcf/day", "Billion cubic feet/day"),
)
MAX_SUMMARY_YEARS = 5
MAX_LATEST_SERIES = len(SERIES_CONFIG)

def _format_compact_number(value):
    formatted = f"{float(value):,.2f}"
    return formatted.rstrip("0").rstrip(".")

def _format_series_block(label, series, short_unit, long_unit, limit):
    lines = [f"**{label}** ({long_unit})"]
    for year, value in series[:limit]:
        lines.append(f"- {year}: {_format_compact_number(value)}{short_unit}")
    lines.append("")
    return lines

def get_sample_production_data():
    """
    Return representative recent production data for demonstration.
    Data based on typical EIA reported values (2020-2024).
    """
    return {
        "coal_production": [
            ("2024", 562.5),  # Million short tons
            ("2023", 585.3),
            ("2022", 614.1),
            ("2021", 577.3),
            ("2020", 538.4),
        ],
        "crude_oil_production": [
            ("2024", 13.2),  # Million barrels per day
            ("2023", 13.1),
            ("2022", 12.8),
            ("2021", 11.2),
            ("2020", 11.3),
        ],
        "natural_gas_production": [
            ("2024", 104.5),  # Billion cubic feet per day
            ("2023", 102.3),
            ("2022", 99.1),
            ("2021", 95.3),
            ("2020", 91.8),
        ],
    }

def format_production_summary(limit=3):
    """
    Return formatted summary of real production data for UI display.
    """
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit must be an integer.")
    if limit <= 0:
        raise ValueError("limit must be greater than 0.")
    if limit > MAX_SUMMARY_YEARS:
        raise ValueError(f"limit must be less than or equal to {MAX_SUMMARY_YEARS}.")

    data = get_sample_production_data()

    lines = ["**U.S. Production Trends (2020-2024)**", ""]
    for key, label, short_unit, long_unit in SERIES_CONFIG:
        lines.extend(_format_series_block(label, data[key], short_unit, long_unit, limit))
    return "\n".join(lines).rstrip()

def get_latest_production_values(limit=None):
    """Return latest-year value records for production series in stable display order."""
    if limit is not None:
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer or None.")
        if limit <= 0:
            raise ValueError("limit must be greater than 0 when provided.")
        if limit > MAX_LATEST_SERIES:
            raise ValueError(
                f"limit must be less than or equal to {MAX_LATEST_SERIES} when provided."
            )

    data = get_sample_production_data()
    selected_series = SERIES_CONFIG if limit is None else SERIES_CONFIG[:limit]

    records = []
    for key, label, short_unit, long_unit in selected_series:
        latest_year, latest_value = data[key][-1]
        records.append(
            {
                "series": key,
                "label": label,
                "year": latest_year,
                "value": latest_value,
                "short_unit": short_unit,
                "long_unit": long_unit,
            }
        )

    return records