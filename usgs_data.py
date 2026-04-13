"""USGS mineral commodity statistics integration helpers."""
USGS_UNITS = {
    "Gold": "tonnes",
    "Silver": "tonnes",
    "Iron": "million tonnes",
    "Copper": "thousand tonnes",
    "Coal": "million tonnes",
}

def get_sample_usgs_mineral_data():
    """Return representative USGS-style annual mineral production statistics.

    Values are illustrative recent global mine production estimates aligned with
    commonly reported USGS commodity categories.
    """
    return {
        "Gold": [
            ("2020", 3200),
            ("2021", 3150),
            ("2022", 3100),
            ("2023", 3000),
            ("2024", 3050),
        ],
        "Silver": [
            ("2020", 25000),
            ("2021", 24800),
            ("2022", 25500),
            ("2023", 26000),
            ("2024", 26200),
        ],
        "Iron": [
            ("2020", 2400),
            ("2021", 2550),
            ("2022", 2500),
            ("2023", 2580),
            ("2024", 2620),
        ],
        "Copper": [
            ("2020", 20600),
            ("2021", 21000),
            ("2022", 21800),
            ("2023", 22100),
            ("2024", 22400),
        ],
        "Coal": [
            ("2020", 7800),
            ("2021", 8100),
            ("2022", 8300),
            ("2023", 8350),
            ("2024", 8400),
        ],
    }

def format_usgs_summary(limit=None):
    """Build a markdown summary block for Streamlit display."""
    if limit is not None:
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer or None.")
        if limit <= 0:
            raise ValueError("limit must be greater than 0 when provided.")

    data = get_sample_usgs_mineral_data()
    lines = [
        "**USGS-Style Mineral Production Snapshot (2020-2024)**",
        "",
        "Approximate global mine production trends for selected commodities.",
        "",
    ]
    mineral_names = sorted(data.keys())
    if limit is not None:
        mineral_names = mineral_names[:limit]

    for mineral in mineral_names:
        series = data[mineral]
        latest_year, latest_value = series[-1]
        lines.append(f"- **{mineral} ({latest_year})**: {latest_value} {USGS_UNITS[mineral]}")

    return "\n".join(lines)