import csv
import io
import json
from datetime import datetime, timezone
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from csv_overlay import build_uploaded_points_template, downsample_grouped_points, parse_uploaded_points
from generators import generate_petroleum_deposits, generate_realistic_deposits
from real_data import format_production_summary, get_sample_production_data
from usgs_data import format_usgs_summary, get_latest_usgs_values, get_sample_usgs_mineral_data

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

CHART_TEMPLATE = "plotly_white"
UPLOAD_COORDINATE_BOUNDS = (-10000.0, 10000.0)

MINERAL_PRESETS = {
    "Custom": None,
    "High-Grade Veins": {
        "mode": "Hydrothermal veins",
        "n_deposits": 180,
        "depth_factor": 1.3,
        "structural_complexity": 4,
    },
    "Layered Basin": {
        "mode": "Sedimentary layers",
        "n_deposits": 140,
        "depth_factor": 1.0,
        "structural_complexity": 3,
    },
    "Placer Field": {
        "mode": "Placer deposits",
        "n_deposits": 220,
        "depth_factor": 0.8,
        "structural_complexity": 2,
    },
}

PETROLEUM_PRESETS = {
    "Custom": None,
    "Tight Traps": {
        "basin_size": 40,
        "reservoir_count": 5,
        "trap_efficiency": 0.8,
    },
    "Broad Basin": {
        "basin_size": 80,
        "reservoir_count": 3,
        "trap_efficiency": 0.6,
    },
    "Shallow Hydrates": {
        "basin_size": 55,
        "reservoir_count": 4,
        "trap_efficiency": 0.5,
    },
}

def _resolve_preset(selection, presets):
    chosen = presets.get(selection)
    if chosen is None:
        return {}
    if not isinstance(chosen, dict):
        raise TypeError("preset values must be dictionaries or None.")
    return dict(chosen)

def _render_model_assumptions(z_label, detail_line):
    with st.expander("Model assumptions and units"):
        st.markdown("- X and Y represent conceptual basin coordinates in kilometres.")
        st.markdown(f"- Z {z_label} in metres.")
        st.markdown(f"- {detail_line}")

def _build_line_figure(years, values, name, line_color, title, yaxis_title):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=years,
            y=values,
            mode="lines+markers",
            name=name,
            line=dict(color=line_color, width=3),
            marker=dict(size=8),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=yaxis_title,
        hovermode="x unified",
        template=CHART_TEMPLATE,
        height=400,
    )
    return fig

def _build_cross_section_figure(points_by_label, axis_choice, title):
    if axis_choice not in {"X-Z", "Y-Z"}:
        raise ValueError("axis_choice must be 'X-Z' or 'Y-Z'.")

    fig = go.Figure()
    x_title = "X (km)"

    for label in sorted(points_by_label):
        coords = _coerce_xyz_array(points_by_label[label])
        if coords is None:
            continue

        if axis_choice == "X-Z":
            x_vals = coords[:, 0]
            z_vals = coords[:, 2]
            x_title = "X (km)"
        else:
            x_vals = coords[:, 1]
            z_vals = coords[:, 2]
            x_title = "Y (km)"

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=z_vals,
                mode="markers",
                name=label,
                marker=dict(size=6, opacity=0.75),
            )
        )

    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        xaxis_title=x_title,
        yaxis_title="Z (m)",
        height=360,
    )
    return fig

def _coerce_xyz_array(coords):
    try:
        array = np.asarray(coords, dtype=float)
    except (TypeError, ValueError):
        return None
    if array.size == 0:
        return None
    if array.ndim != 2 or array.shape[1] != 3:
        return None
    return array

def _build_usgs_latest_rows(limit=None):
    records = get_latest_usgs_values(limit=limit)
    return [(entry["mineral"], entry["year"], entry["value"]) for entry in records]

def _apply_3d_layout(
    fig,
    *,
    title,
    xaxis_title,
    yaxis_title,
    zaxis_title,
    height,
    camera_eye=(1.5, 1.5, 1.2),
):
    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        scene=dict(
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            zaxis_title=zaxis_title,
            camera=dict(eye=dict(x=camera_eye[0], y=camera_eye[1], z=camera_eye[2])),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=height,
    )


def _add_grouped_scatter3d_traces(
    fig,
    grouped_points,
    color_for_group,
    *,
    marker_size,
    opacity,
    line_color,
    hovertemplate_for_group,
):
    for index, label in enumerate(sorted(grouped_points)):
        coords = _coerce_xyz_array(grouped_points[label])
        if coords is None or len(coords) == 0:
            continue

        fig.add_trace(
            go.Scatter3d(
                x=coords[:, 0],
                y=coords[:, 1],
                z=coords[:, 2],
                mode="markers",
                marker=dict(
                    size=marker_size,
                    color=color_for_group(label, index),
                    opacity=opacity,
                    line=dict(color=line_color, width=1),
                ),
                name=label,
                hovertemplate=hovertemplate_for_group(label),
            )
        )

def build_points_csv(points_by_label, unit_label):
    """Convert grouped 3D points into CSV text for download."""
    if not isinstance(points_by_label, dict):
        raise TypeError("points_by_label must be a dictionary.")
    if not isinstance(unit_label, str):
        raise TypeError("unit_label must be a string.")
    if not unit_label.strip():
        raise ValueError("unit_label must not be empty.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["deposit_type", "x", "y", "z", "z_unit"])

    for label in sorted(points_by_label):
        coords = _coerce_xyz_array(points_by_label[label])
        if coords is None:
            continue
        for x, y, z in coords:
            writer.writerow([label, f"{x:.6f}", f"{y:.6f}", f"{z:.6f}", unit_label])

    return output.getvalue()

def format_point_group_summary(total_points, group_count):
    if not isinstance(total_points, int) or isinstance(total_points, bool):
        raise TypeError("total_points must be an integer.")
    if not isinstance(group_count, int) or isinstance(group_count, bool):
        raise TypeError("group_count must be an integer.")
    if total_points < 0:
        raise ValueError("total_points must be greater than or equal to 0.")
    if group_count < 0:
        raise ValueError("group_count must be greater than or equal to 0.")

    point_label = "point" if total_points == 1 else "points"
    group_label = "label group" if group_count == 1 else "label groups"
    return f"Loaded {total_points} {point_label} across {group_count} {group_label}."

def summarize_point_groups(points_by_label):
    summaries = []
    for label in sorted(points_by_label):
        coords = _coerce_xyz_array(points_by_label[label])
        if coords is None:
            continue

        xs = coords[:, 0]
        ys = coords[:, 1]
        zs = coords[:, 2]

        count = len(coords)
        summaries.append(
            {
                "Label": label,
                "Count": count,
                "Min Z": round(float(zs.min()), 2),
                "Max Z": round(float(zs.max()), 2),
                "Mean Z": round(float(zs.mean()), 2),
                "Centroid X": round(float(xs.mean()), 2),
                "Centroid Y": round(float(ys.mean()), 2),
                "Centroid Z": round(float(zs.mean()), 2),
            }
        )
    return summaries

def build_group_summary_csv(summaries):
    """Convert tabular summary rows into CSV text for download."""
    if not isinstance(summaries, list):
        raise TypeError("summaries must be a list of dictionaries.")

    output = io.StringIO()
    fieldnames = ["Label", "Count", "Min Z", "Max Z", "Mean Z", "Centroid X", "Centroid Y", "Centroid Z"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in summaries:
        if not isinstance(row, dict):
            raise TypeError("each summary row must be a dictionary.")
        writer.writerow({key: row.get(key, "") for key in fieldnames})
    return output.getvalue()

def build_metadata_json(view_name, parameters):
    if not isinstance(view_name, str):
        raise TypeError("view_name must be a string.")
    if not view_name.strip():
        raise ValueError("view_name must not be empty.")
    if not isinstance(parameters, dict):
        raise TypeError("parameters must be a dictionary.")

    payload = {
        "view": view_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "parameters": parameters,
    }
    return json.dumps(payload, indent=2, sort_keys=True)

@st.cache_data(show_spinner=False)
def _get_cached_production_data():
    return get_sample_production_data()

@st.cache_data(show_spinner=False)
def _get_cached_usgs_data():
    return get_sample_usgs_mineral_data()

def render_view_header(title, subtitle):
    st.header(title)
    st.caption(subtitle)

def render_sidebar_intro():
    return None

def render_mineral_view():
    render_view_header(
        "Mineral Deposit Modelling",
        "Explore different synthetic orebody styles, then tune density and structure from the sidebar.",
    )

    st.sidebar.markdown("**Select minerals to display:**")
    st.sidebar.caption("All selected minerals share the same geological mode and random seed.")
    selected_minerals = [m for m in MINERALS if st.sidebar.checkbox(m, value=True)]

    if not selected_minerals:
        st.warning("Please select at least one mineral to display the model.")
        return

    st.sidebar.markdown("**Mineral Presets:**")
    mineral_preset = st.sidebar.selectbox(
        "Scenario preset",
        list(MINERAL_PRESETS.keys()),
        help="Use a preset to quickly load representative mineral modelling settings.",
    )
    mineral_defaults = _resolve_preset(mineral_preset, MINERAL_PRESETS)

    st.sidebar.markdown("**Mineral Parameters:**")
    n_deposits = st.sidebar.slider(
        "Number of deposits per mineral",
        10,
        500,
        mineral_defaults.get("n_deposits", 100),
        10,
        help="Higher values increase point density and rendering time.",
    )
    random_seed = st.sidebar.number_input(
        "Random seed",
        value=42,
        step=1,
        help="Use the same seed to reproduce the same deposit layout.",
    )

    modeling_mode = st.sidebar.radio(
        "Geological modelling mode",
        ["Orebody systems", "Hydrothermal veins", "Sedimentary layers", "Contact metamorphic", "Placer deposits"],
        index=[
            "Orebody systems",
            "Hydrothermal veins",
            "Sedimentary layers",
            "Contact metamorphic",
            "Placer deposits",
        ].index(mineral_defaults.get("mode", "Orebody systems")),
    )

    st.sidebar.markdown("**Geological Parameters:**")
    depth_factor = st.sidebar.slider(
        "Depth influence",
        0.1,
        2.0,
        mineral_defaults.get("depth_factor", 1.0),
        0.1,
        help="Scales the vertical spread of the generated deposit.",
    )
    structural_complexity = st.sidebar.slider(
        "Structural complexity",
        1,
        5,
        mineral_defaults.get("structural_complexity", 3),
        1,
        help="Controls branching, layering, and scatter.",
    )
    mineral_noise = st.sidebar.slider(
        "Uncertainty noise",
        0.0,
        5.0,
        0.0,
        0.1,
        help="Adds random perturbation to synthetic coordinates.",
    )

    deposits = {}
    for mineral in selected_minerals:
        deposits[mineral] = generate_realistic_deposits(
            mineral,
            modeling_mode,
            n_deposits,
            random_seed,
            depth_factor,
            structural_complexity,
            noise_scale=mineral_noise,
        )

    fig_minerals = go.Figure()
    _add_grouped_scatter3d_traces(
        fig_minerals,
        deposits,
        lambda label, index: MINERALS[label],
        marker_size=6,
        opacity=0.8,
        line_color="white",
        hovertemplate_for_group=lambda label: (
            f"<b>{label}</b><br>X: %{{x:.1f}}<br>Y: %{{y:.1f}}<br>Depth: %{{z:.1f}}<extra></extra>"
        ),
    )

    _apply_3d_layout(
        fig_minerals,
        title=f"3D Mineral Deposit Model - {modeling_mode}",
        xaxis_title="Easting (km)",
        yaxis_title="Northing (km)",
        zaxis_title="Elevation (m)",
        height=600,
    )
    fig_minerals.update_layout(legend_title_text="Minerals")

    st.plotly_chart(fig_minerals, use_container_width=True)
    cross_axis = st.radio("Mineral cross-section", ["X-Z", "Y-Z"], horizontal=True)
    st.plotly_chart(
        _build_cross_section_figure(deposits, cross_axis, f"Mineral Cross-Section ({cross_axis})"),
        use_container_width=True,
    )
    st.markdown("### Deposit Summary")
    mineral_summary = summarize_point_groups({k: v.tolist() for k, v in deposits.items()})
    st.table(mineral_summary)
    st.download_button(
        "Download mineral summary (CSV)",
        data=build_group_summary_csv(mineral_summary),
        file_name="mineral_summary.csv",
        mime="text/csv",
    )

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

    _render_model_assumptions(
        "is modelled elevation/depth output",
        "These are synthetic datasets for exploration and visualisation only.",
    )

    mineral_csv = build_points_csv(deposits, "m")
    st.download_button(
        "Download mineral points (CSV)",
        data=mineral_csv,
        file_name="mineral_deposits.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download mineral metadata (JSON)",
        data=build_metadata_json(
            "Mineral Deposits",
            {
                "selected_minerals": selected_minerals,
                "preset": mineral_preset,
                "mode": modeling_mode,
                "n_deposits": n_deposits,
                "random_seed": int(random_seed),
                "depth_factor": depth_factor,
                "structural_complexity": structural_complexity,
                "uncertainty_noise": mineral_noise,
            },
        ),
        file_name="mineral_metadata.json",
        mime="application/json",
    )

def render_petroleum_view():
    render_view_header(
        "Petroleum Deposit Modelling",
        "Model synthetic hydrocarbon basins with traps, reservoirs, and depth patterns.",
    )

    st.sidebar.markdown("**Select petroleum deposits to display:**")
    st.sidebar.caption("Each selected deposit type is generated with the same basin settings and seed.")
    selected_petroleum = [p for p in PETROLEUM if st.sidebar.checkbox(p, value=True, key=f"pet_{p}")]

    if not selected_petroleum:
        st.warning("Please select at least one petroleum deposit type to display the model.")
        return

    st.sidebar.markdown("**Petroleum Presets:**")
    petroleum_preset = st.sidebar.selectbox(
        "Basin preset",
        list(PETROLEUM_PRESETS.keys()),
        help="Use a preset to quickly load representative petroleum basin settings.",
    )
    petroleum_defaults = _resolve_preset(petroleum_preset, PETROLEUM_PRESETS)

    st.sidebar.markdown("**Petroleum Parameters:**")
    basin_size = st.sidebar.slider(
        "Basin size (km)",
        20,
        100,
        petroleum_defaults.get("basin_size", 50),
        10,
        help="Larger basins spread reservoirs across a wider area.",
    )
    reservoir_count = st.sidebar.slider(
        "Number of reservoirs",
        1,
        8,
        petroleum_defaults.get("reservoir_count", 3),
        1,
        help="More reservoirs add more trap clusters.",
    )
    trap_efficiency = st.sidebar.slider(
        "Trap efficiency",
        0.1,
        1.0,
        petroleum_defaults.get("trap_efficiency", 0.6),
        0.1,
        help="Higher values concentrate more points into each trap.",
    )
    petroleum_noise = st.sidebar.slider(
        "Uncertainty noise",
        0.0,
        25.0,
        0.0,
        0.5,
        key="pet_noise",
        help="Adds random perturbation to synthetic coordinates.",
    )
    pet_random_seed = st.sidebar.number_input(
        "Random seed",
        value=42,
        step=1,
        key="pet_seed",
        help="Use the same seed to keep basin geometry reproducible.",
    )

    petroleum_deposits = {}
    for pet_type in selected_petroleum:
        petroleum_deposits[pet_type] = generate_petroleum_deposits(
            pet_type,
            basin_size,
            reservoir_count,
            trap_efficiency,
            pet_random_seed,
            noise_scale=petroleum_noise,
        )

    fig_petroleum = go.Figure()
    _add_grouped_scatter3d_traces(
        fig_petroleum,
        petroleum_deposits,
        lambda label, index: PETROLEUM[label],
        marker_size=8,
        opacity=0.7,
        line_color="black",
        hovertemplate_for_group=lambda label: (
            f"<b>{label}</b><br>X: %{{x:.1f}}<br>Y: %{{y:.1f}}<br>Depth: %{{z:.0f}}m<extra></extra>"
        ),
    )

    _apply_3d_layout(
        fig_petroleum,
        title="3D Petroleum Deposit Model - Sedimentary Basin",
        xaxis_title="Easting (km)",
        yaxis_title="Northing (km)",
        zaxis_title="Depth (m)",
        height=600,
    )
    fig_petroleum.update_layout(legend_title_text="Petroleum Deposits")

    st.plotly_chart(fig_petroleum, use_container_width=True)
    petroleum_axis = st.radio("Petroleum cross-section", ["X-Z", "Y-Z"], horizontal=True)
    st.plotly_chart(
        _build_cross_section_figure(
            petroleum_deposits, petroleum_axis, f"Petroleum Cross-Section ({petroleum_axis})"
        ),
        use_container_width=True,
    )
    st.markdown("### Reservoir Summary")
    petroleum_summary = summarize_point_groups({k: v.tolist() for k, v in petroleum_deposits.items()})
    st.table(petroleum_summary)
    st.download_button(
        "Download petroleum summary (CSV)",
        data=build_group_summary_csv(petroleum_summary),
        file_name="petroleum_summary.csv",
        mime="text/csv",
    )

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

    _render_model_assumptions(
        "represents modelled depth",
        "Generated reservoirs are simplified trap analogues, not field-calibrated predictions.",
    )

    petroleum_csv = build_points_csv(petroleum_deposits, "m")
    st.download_button(
        "Download petroleum points (CSV)",
        data=petroleum_csv,
        file_name="petroleum_deposits.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download petroleum metadata (JSON)",
        data=build_metadata_json(
            "Petroleum Deposits",
            {
                "selected_petroleum": selected_petroleum,
                "preset": petroleum_preset,
                "basin_size": basin_size,
                "reservoir_count": reservoir_count,
                "trap_efficiency": trap_efficiency,
                "random_seed": int(pet_random_seed),
                "uncertainty_noise": petroleum_noise,
            },
        ),
        file_name="petroleum_metadata.json",
        mime="application/json",
    )

def render_real_data_view():
    render_view_header(
        "Real-World Commodity Production Data",
        "Compare sample EIA and USGS-style summaries, or overlay your own coordinate data.",
    )
    real_data_source = st.radio(
        "Select real-world dataset:",
        ["EIA Energy", "USGS Minerals"],
        horizontal=True,
        help="Switch between energy production trends and mineral production snapshots.",
    )

    if real_data_source == "EIA Energy":
        st.markdown(format_production_summary())

        with st.expander("Production Trends Chart"):
            data = _get_cached_production_data()

            coal_years, coal_values = zip(*data["coal_production"])
            fig_coal = _build_line_figure(
                coal_years,
                coal_values,
                "Coal Production",
                "black",
                "U.S. Coal Production (Million Short Tons)",
                "Production (M tons)",
            )
            st.plotly_chart(fig_coal, use_container_width=True)

            oil_years, oil_values = zip(*data["crude_oil_production"])
            fig_oil = _build_line_figure(
                oil_years,
                oil_values,
                "Crude Oil Production",
                "darkgreen",
                "U.S. Crude Oil Production (Million Barrels/Day)",
                "Production (M bbl/day)",
            )
            st.plotly_chart(fig_oil, use_container_width=True)

            gas_years, gas_values = zip(*data["natural_gas_production"])
            fig_gas = _build_line_figure(
                gas_years,
                gas_values,
                "Natural Gas Production",
                "lightblue",
                "U.S. Natural Gas Production (Billion Cubic Feet/Day)",
                "Production (Bcf/day)",
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
        minerals_latest = _build_usgs_latest_rows()

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
            template=CHART_TEMPLATE,
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
    st.download_button(
        "Download CSV template",
        data=build_uploaded_points_template(),
        file_name="uploaded_points_template.csv",
        mime="text/csv",
    )
    uploaded_file = st.file_uploader(
        "Upload CSV with columns: x, y, z, label (optional)",
        type=["csv"],
        key="uploaded_real_points",
        help="Upload a UTF-8 CSV with x, y, z columns; label is optional.",
    )

    downsample_enabled = st.checkbox(
        "Downsample large uploads",
        value=True,
        help="Keeps rendering responsive for very large uploaded datasets.",
    )
    max_uploaded_points = st.slider(
        "Max uploaded points to plot",
        100,
        10000,
        3000,
        100,
        help="If the uploaded dataset exceeds this limit, a deterministic sample is plotted.",
    )
    downsample_seed = st.number_input(
        "Downsample seed",
        value=42,
        step=1,
        help="Use the same seed to keep the sampled subset stable.",
    )

    if uploaded_file is not None:
        try:
            grouped_points = parse_uploaded_points(
                uploaded_file.getvalue(), coordinate_bounds=UPLOAD_COORDINATE_BOUNDS
            )
            original_total = sum(len(v) for v in grouped_points.values())

            if downsample_enabled:
                grouped_points = downsample_grouped_points(
                    grouped_points, max_points=max_uploaded_points, seed=int(downsample_seed)
                )
            displayed_total = sum(len(v) for v in grouped_points.values())

            fig_uploaded = go.Figure()
            palette = [
                "#e76f51",
                "#2a9d8f",
                "#264653",
                "#f4a261",
                "#457b9d",
                "#8ab17d",
            ]

            _add_grouped_scatter3d_traces(
                fig_uploaded,
                grouped_points,
                lambda label, idx: palette[idx % len(palette)],
                marker_size=7,
                opacity=0.85,
                line_color="white",
                hovertemplate_for_group=lambda label: (
                    f"<b>{label}</b><br>X: %{{x:.2f}}<br>Y: %{{y:.2f}}<br>Z: %{{z:.2f}}<extra></extra>"
                ),
            )

            _apply_3d_layout(
                fig_uploaded,
                title="Uploaded Mine/Well Coordinates (3D)",
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                height=560,
                camera_eye=(1.4, 1.4, 1.1),
            )

            st.success(
                format_point_group_summary(
                    total_points=displayed_total,
                    group_count=len(grouped_points),
                )
            )
            if displayed_total < original_total:
                st.caption(f"Showing a deterministic subset: {displayed_total} of {original_total} uploaded points.")
            st.plotly_chart(fig_uploaded, use_container_width=True)
            st.markdown("### Uploaded Data Summary")
            uploaded_summary = summarize_point_groups(grouped_points)
            st.table(uploaded_summary)
            st.download_button(
                "Download uploaded summary (CSV)",
                data=build_group_summary_csv(uploaded_summary),
                file_name="uploaded_summary.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download uploaded points (CSV)",
                data=build_points_csv({k: list(v) for k, v in grouped_points.items()}, "unitless"),
                file_name="uploaded_points.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download uploaded metadata (JSON)",
                data=build_metadata_json(
                    "Uploaded Overlay",
                    {
                        "downsample_enabled": downsample_enabled,
                        "max_uploaded_points": max_uploaded_points,
                        "downsample_seed": int(downsample_seed),
                        "displayed_points": displayed_total,
                        "original_points": original_total,
                        "label_count": len(grouped_points),
                    },
                ),
                file_name="uploaded_metadata.json",
                mime="application/json",
            )
        except ValueError as exc:
            st.error(f"CSV validation error: {exc}")