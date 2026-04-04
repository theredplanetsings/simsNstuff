"""USGS mineral commodity statistics integration helpers."""


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


def format_usgs_summary():
    """Build a markdown summary block for Streamlit display."""
    data = get_sample_usgs_mineral_data()
    lines = [
        "**USGS-Style Mineral Production Snapshot (2020-2024)**",
        "",
        "Approximate global mine production trends for selected commodities.",
        "",
    ]

    units = {
        "Gold": "tonnes",
        "Silver": "tonnes",
        "Iron": "million tonnes",
        "Copper": "thousand tonnes",
        "Coal": "million tonnes",
    }

    for mineral, series in data.items():
        latest_year, latest_value = series[-1]
        lines.append(f"- **{mineral} ({latest_year})**: {latest_value} {units[mineral]}")

    return "\n".join(lines)
