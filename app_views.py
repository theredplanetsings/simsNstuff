import csv
import io

import plotly.graph_objects as go
import streamlit as st

from csv_overlay import parse_uploaded_points
from generators import generate_petroleum_deposits, generate_realistic_deposits
from real_data import format_production_summary, get_sample_production_data
from usgs_data import format_usgs_summary, get_sample_usgs_mineral_data


MINERALS = {
    "Silver": "gray",
    "Gold": "gold",
    "Iron": "brown",
    "Copper": "orange",
    "Coal": "black",
}

PETROLEUM = {
    "Oil": "darkgreen",
    "Natural Gas": "lightblue",
    "Oil Shale": "darkslategray",
    "Gas Hydrates": "dodgerblue",
}


def build_points_csv(points_by_label, unit_label):
    """Convert grouped 3D points into CSV text for download."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["deposit_type", "x", "y", "z", "z_unit"])

    for label, coords in points_by_label.items():
        for x, y, z in coords:
            writer.writerow([label, f"{x:.6f}", f"{y:.6f}", f"{z:.6f}", unit_label])

    return output.getvalue()


def render_sidebar_intro():
    st.sidebar.markdown("### Available Features")
    st.sidebar.markdown("- Mineral deposit modelling")
    st.sidebar.markdown("- Petroleum deposit modelling")
    st.sidebar.markdown("- Real Data: EIA energy trends")
    st.sidebar.markdown("- Real Data: USGS mineral snapshot")
    st.sidebar.markdown("- CSV upload for custom mine/well overlays")


def render_mineral_view():
    st.header("Mineral Deposit Modelling")

    st.sidebar.markdown("**Select minerals to display:**")
    selected_minerals = [m for m in MINERALS if st.sidebar.checkbox(m, value=True)]

    if not selected_minerals:
        st.warning("Please select at least one mineral to display the model.")
        return

    st.sidebar.markdown("**Mineral Parameters:**")
    n_deposits = st.sidebar.slider("Number of deposits per mineral", 10, 500, 100, 10)
    random_seed = st.sidebar.number_input("Random seed", value=42, step=1)

    modeling_mode = st.sidebar.radio(
        "Geological modelling mode",
        ["Orebody systems", "Hydrothermal veins", "Sedimentary layers", "Contact metamorphic", "Placer deposits"],
    )

    st.sidebar.markdown("**Geological Parameters:**")
    depth_factor = st.sidebar.slider("Depth influence", 0.1, 2.0, 1.0, 0.1)
    structural_complexity = st.sidebar.slider("Structural complexity", 1, 5, 3, 1)

    deposits = {}
    for mineral in selected_minerals:
        deposits[mineral] = generate_realistic_deposits(
            mineral, modeling_mode, n_deposits, random_seed, depth_factor, structural_complexity
        )

    fig_minerals = go.Figure()
    for mineral in selected_minerals:
        coords = deposits[mineral]
        fig_minerals.add_trace(
            go.Scatter3d(
                x=coords[:, 0],
                y=coords[:, 1],
                z=coords[:, 2],
                mode="markers",
                marker=dict(size=6, color=MINERALS[mineral], opacity=0.8, line=dict(color="white", width=1)),
                name=mineral,
                hovertemplate=f"<b>{mineral}</b><br>X: %{{x:.1f}}<br>Y: %{{y:.1f}}<br>Depth: %{{z:.1f}}<extra></extra>",
            )
        )

    fig_minerals.update_layout(
        title=f"3D Mineral Deposit Model - {modeling_mode}",
        scene=dict(
            xaxis_title="Easting (km)",
            yaxis_title="Northing (km)",
            zaxis_title="Elevation (m)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
        ),
        legend_title_text="Minerals",
        margin=dict(l=0, r=0, b=0, t=40),
        height=600,
    )

    st.plotly_chart(fig_minerals, use_container_width=True)

    st.markdown("### Geological Context")
    if modeling_mode == "Orebody systems":
        st.info("**Orebody Systems:** Pipe-like or lode deposits formed by hydrothermal processes. Often associated with igneous intrusions.")
    elif modeling_mode == "Hydrothermal veins":
        st.info("**Hydrothermal Veins:** Fracture-filling deposits with branching patterns. Common for precious metals.")
    elif modeling_mode == "Sedimentary layers":
        st.info("**Sedimentary Layers:** Stratiform deposits in sedimentary rocks. Common for coal and iron formations.")
    elif modeling_mode == "Contact metamorphic":
        st.info("**Contact Metamorphic:** Deposits formed in aureoles around igneous intrusions through thermal metamorphism.")
    elif modeling_mode == "Placer deposits":
        st.info("**Placer Deposits:** Concentration of heavy minerals in alluvial sediments. Common for gold and gemstones.")

    with st.expander("Model assumptions and units"):
        st.markdown("- X and Y represent conceptual basin coordinates in kilometres.")
        st.markdown("- Z is modelled elevation/depth output in metres.")
        st.markdown("- These are synthetic datasets for exploration and visualisation only.")

    mineral_csv = build_points_csv(deposits, "m")
    st.download_button(
        "Download mineral points (CSV)",
        data=mineral_csv,
        file_name="mineral_deposits.csv",
        mime="text/csv",
    )


def render_petroleum_view():
    st.header("Petroleum Deposit Modelling")

    st.sidebar.markdown("**Select petroleum deposits to display:**")
    selected_petroleum = [p for p in PETROLEUM if st.sidebar.checkbox(p, value=True, key=f"pet_{p}")]

    if not selected_petroleum:
        st.warning("Please select at least one petroleum deposit type to display the model.")
        return

    st.sidebar.markdown("**Petroleum Parameters:**")
    basin_size = st.sidebar.slider("Basin size (km)", 20, 100, 50, 10)
    reservoir_count = st.sidebar.slider("Number of reservoirs", 1, 8, 3, 1)
    trap_efficiency = st.sidebar.slider("Trap efficiency", 0.1, 1.0, 0.6, 0.1)
    pet_random_seed = st.sidebar.number_input("Random seed", value=42, step=1, key="pet_seed")

    petroleum_deposits = {}
    for pet_type in selected_petroleum:
        petroleum_deposits[pet_type] = generate_petroleum_deposits(
            pet_type, basin_size, reservoir_count, trap_efficiency, pet_random_seed
        )

    fig_petroleum = go.Figure()
    for pet_type in selected_petroleum:
        coords = petroleum_deposits[pet_type]
        if len(coords) > 0:
            fig_petroleum.add_trace(
                go.Scatter3d(
                    x=coords[:, 0],
                    y=coords[:, 1],
                    z=coords[:, 2],
                    mode="markers",
                    marker=dict(size=8, color=PETROLEUM[pet_type], opacity=0.7, line=dict(color="black", width=1)),
                    name=pet_type,
                    hovertemplate=f"<b>{pet_type}</b><br>X: %{{x:.1f}}<br>Y: %{{y:.1f}}<br>Depth: %{{z:.0f}}m<extra></extra>",
                )
            )

    fig_petroleum.update_layout(
        title="3D Petroleum Deposit Model - Sedimentary Basin",
        scene=dict(
            xaxis_title="Easting (km)",
            yaxis_title="Northing (km)",
            zaxis_title="Depth (m)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
        ),
        legend_title_text="Petroleum Deposits",
        margin=dict(l=0, r=0, b=0, t=40),
        height=600,
    )

    st.plotly_chart(fig_petroleum, use_container_width=True)

    st.markdown("### Petroleum Geology")
    st.info(
        """
    **Petroleum Systems:** Hydrocarbon deposits form through source rock maturation, migration, and trapping.
    - **Source rocks** generate oil and gas through thermal maturation
    - **Migration** occurs along permeable pathways
    - **Traps** concentrate hydrocarbons (structural, stratigraphic, combination)
    - **Seal rocks** prevent further migration
    """
    )

    with st.expander("Model assumptions and units"):
        st.markdown("- X and Y represent conceptual basin coordinates in kilometres.")
        st.markdown("- Z represents modelled depth in metres.")
        st.markdown("- Generated reservoirs are simplified trap analogues, not field-calibrated predictions.")

    petroleum_csv = build_points_csv(petroleum_deposits, "m")
    st.download_button(
        "Download petroleum points (CSV)",
        data=petroleum_csv,
        file_name="petroleum_deposits.csv",
        mime="text/csv",
    )


def render_real_data_view():
    st.header("Real-World Commodity Production Data")
    real_data_source = st.radio(
        "Select real-world dataset:",
        ["EIA Energy", "USGS Minerals"],
        horizontal=True,
    )

    if real_data_source == "EIA Energy":
        st.markdown(format_production_summary())

        with st.expander("Production Trends Chart"):
            data = get_sample_production_data()

            coal_years, coal_values = zip(*data["coal_production"])
            fig_coal = go.Figure()
            fig_coal.add_trace(
                go.Scatter(
                    x=coal_years,
                    y=coal_values,
                    mode="lines+markers",
                    name="Coal Production",
                    line=dict(color="black", width=3),
                    marker=dict(size=8),
                )
            )
            fig_coal.update_layout(
                title="U.S. Coal Production (Million Short Tons)",
                xaxis_title="Year",
                yaxis_title="Production (M tons)",
                hovermode="x unified",
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig_coal, use_container_width=True)

            oil_years, oil_values = zip(*data["crude_oil_production"])
            fig_oil = go.Figure()
            fig_oil.add_trace(
                go.Scatter(
                    x=oil_years,
                    y=oil_values,
                    mode="lines+markers",
                    name="Crude Oil Production",
                    line=dict(color="darkgreen", width=3),
                    marker=dict(size=8),
                )
            )
            fig_oil.update_layout(
                title="U.S. Crude Oil Production (Million Barrels/Day)",
                xaxis_title="Year",
                yaxis_title="Production (M bbl/day)",
                hovermode="x unified",
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig_oil, use_container_width=True)

            gas_years, gas_values = zip(*data["natural_gas_production"])
            fig_gas = go.Figure()
            fig_gas.add_trace(
                go.Scatter(
                    x=gas_years,
                    y=gas_values,
                    mode="lines+markers",
                    name="Natural Gas Production",
                    line=dict(color="lightblue", width=3),
                    marker=dict(size=8),
                )
            )
            fig_gas.update_layout(
                title="U.S. Natural Gas Production (Billion Cubic Feet/Day)",
                xaxis_title="Year",
                yaxis_title="Production (Bcf/day)",
                hovermode="x unified",
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig_gas, use_container_width=True)

        st.markdown("### Data Source")
        st.info(
            """
            **U.S. Energy Information Administration (EIA):**
            - Annual production statistics for coal, crude oil, and natural gas
            - Official government data: https://www.eia.gov/opendata/
            """
        )
    else:
        st.markdown(format_usgs_summary())
        usgs_data = get_sample_usgs_mineral_data()

        minerals_latest = []
        for mineral_name, series in usgs_data.items():
            year, value = series[-1]
            minerals_latest.append((mineral_name, year, value))

        fig_usgs = go.Figure(
            data=[
                go.Bar(
                    x=[entry[0] for entry in minerals_latest],
                    y=[entry[2] for entry in minerals_latest],
                    marker=dict(color=[MINERALS.get(entry[0], "slategray") for entry in minerals_latest]),
                    text=[str(entry[2]) for entry in minerals_latest],
                    textposition="outside",
                )
            ]
        )
        fig_usgs.update_layout(
            title="Latest USGS-Style Mineral Production Snapshot",
            xaxis_title="Commodity",
            yaxis_title="Production (mixed commodity units)",
            template="plotly_dark",
            height=450,
        )
        st.plotly_chart(fig_usgs, use_container_width=True)

        st.markdown("### Data Source")
        st.info(
            """
            **USGS National Minerals Information Center:**
            - Commodity statistics and annual mineral summaries
            - Official data portal: https://www.usgs.gov/centers/national-minerals-information-center
            """
        )

    st.markdown("### Upload Your Own Mine/Well Coordinates")
    uploaded_file = st.file_uploader(
        "Upload CSV with columns: x, y, z, label (optional)",
        type=["csv"],
        key="uploaded_real_points",
    )

    if uploaded_file is not None:
        try:
            grouped_points = parse_uploaded_points(uploaded_file.getvalue())

            fig_uploaded = go.Figure()
            palette = [
                "#e76f51",
                "#2a9d8f",
                "#264653",
                "#f4a261",
                "#457b9d",
                "#8ab17d",
            ]

            for idx, (label, points) in enumerate(grouped_points.items()):
                xs = [pt[0] for pt in points]
                ys = [pt[1] for pt in points]
                zs = [pt[2] for pt in points]
                fig_uploaded.add_trace(
                    go.Scatter3d(
                        x=xs,
                        y=ys,
                        z=zs,
                        mode="markers",
                        marker=dict(
                            size=7,
                            color=palette[idx % len(palette)],
                            opacity=0.85,
                            line=dict(color="white", width=1),
                        ),
                        name=label,
                        hovertemplate=f"<b>{label}</b><br>X: %{{x:.2f}}<br>Y: %{{y:.2f}}<br>Z: %{{z:.2f}}<extra></extra>",
                    )
                )

            fig_uploaded.update_layout(
                title="Uploaded Mine/Well Coordinates (3D)",
                scene=dict(
                    xaxis_title="X",
                    yaxis_title="Y",
                    zaxis_title="Z",
                    camera=dict(eye=dict(x=1.4, y=1.4, z=1.1)),
                ),
                template="plotly_dark",
                height=560,
            )

            st.success(f"Loaded {sum(len(v) for v in grouped_points.values())} points across {len(grouped_points)} label group(s).")
            st.plotly_chart(fig_uploaded, use_container_width=True)
        except ValueError as exc:
            st.error(f"CSV validation error: {exc}")