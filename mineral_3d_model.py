"""
Sims N Stuff -

A 3D Geological Deposit Modelling Programme

3D Visualisation of realistic mineral and petroleum deposits using advanced geological modelling.

__author__ = "https://github.com/theredplanetsings"
__date__ = "03/7/2025"
"""
import streamlit as st
import plotly.graph_objects as go

from generators import generate_petroleum_deposits, generate_realistic_deposits

# defining minerals and their colors
minerals = {
    "Silver": "gray",
    "Gold": "gold",
    "Iron": "brown",
    "Copper": "orange",
    "Coal": "black",
}

# petroleum deposit types
petroleum = {
    "Oil": "darkgreen",
    "Natural Gas": "lightblue",
    "Oil Shale": "darkslategray",
    "Gas Hydrates": "lightcyan",
}

st.title("Sims N Stuff")
st.markdown("Visualise realistic 3D deposits of minerals and petroleum using advanced geological modelling.")

deposit_type = st.radio(
    "Select deposit type:",
    ["Mineral Deposits", "Petroleum Deposits"],
    horizontal=True,
)

if deposit_type == "Mineral Deposits":
    st.header("Mineral Deposit Modelling")

    st.sidebar.markdown("**Select minerals to display:**")
    selected_minerals = [m for m in minerals if st.sidebar.checkbox(m, value=True)]

    if selected_minerals:
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
    else:
        st.warning("Please select at least one mineral to display the model.")

    if selected_minerals:
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
                    marker=dict(size=6, color=minerals[mineral], opacity=0.8),
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

else:
    st.header("Petroleum Deposit Modelling")

    st.sidebar.markdown("**Select petroleum deposits to display:**")
    selected_petroleum = [p for p in petroleum if st.sidebar.checkbox(p, value=True, key=f"pet_{p}")]

    if selected_petroleum:
        st.sidebar.markdown("**Petroleum Parameters:**")
        basin_size = st.sidebar.slider("Basin size (km)", 20, 100, 50, 10)
        reservoir_count = st.sidebar.slider("Number of reservoirs", 1, 8, 3, 1)
        trap_efficiency = st.sidebar.slider("Trap efficiency", 0.1, 1.0, 0.6, 0.1)
        pet_random_seed = st.sidebar.number_input("Random seed", value=42, step=1, key="pet_seed")
    else:
        st.warning("Please select at least one petroleum deposit type to display the model.")

    if selected_petroleum:
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
                        marker=dict(size=8, color=petroleum[pet_type], opacity=0.7),
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

st.markdown("---")
st.markdown("**Instructions:**")
st.markdown("1. Use the sidebar to select deposit types and adjust geological parameters.")
st.markdown("2. Switch between mineral and petroleum deposit tabs.")
st.markdown("3. Explore different geological modelling modes for realistic deposit patterns.")
st.code("streamlit run mineral_3d_model.py", language="bash")
