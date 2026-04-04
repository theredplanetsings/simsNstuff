"""Sample real-world commodity data helpers for the Streamlit app."""


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


def format_production_summary():
    """
    Return formatted summary of real production data for UI display.
    """
    data = get_sample_production_data()

    summary = ""
    summary += "**U.S. Production Trends (2020-2024)**\n\n"

    summary += "**Coal Production** (Million short tons)\n"
    for year, value in data["coal_production"][:3]:
        summary += f"- {year}: {value}M tons\n"

    summary += "\n**Crude Oil** (Million barrels/day)\n"
    for year, value in data["crude_oil_production"][:3]:
        summary += f"- {year}: {value}M bbl/day\n"

    summary += "\n**Natural Gas** (Billion cubic feet/day)\n"
    for year, value in data["natural_gas_production"][:3]:
        summary += f"- {year}: {value}Bcf/day\n"

    return summary
