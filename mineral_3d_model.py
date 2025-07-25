"""
Sims N Stuff -

A 3D Geological Deposit Modelling Programme

3D Visualisation of realistic mineral and petroleum deposits using advanced geological modelling.

__author__ = "https://github.com/theredplanetsings"
__date__ = "03/7/2025"
"""
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy.spatial.distance import cdist

# defining minerals and their colors
minerals = {
    'Silver': 'gray',
    'Gold': 'gold',
    'Iron': 'brown',
    'Copper': 'orange',
    'Coal': 'black'
}

# petroleum deposit types
petroleum = {
    'Oil': 'darkgreen',
    'Natural Gas': 'lightblue',
    'Oil Shale': 'darkslategray',
    'Gas Hydrates': 'lightcyan'
}

st.title('Sims N Stuff')
st.markdown('Visualise realistic 3D deposits of minerals and petroleum using advanced geological modelling.')

# Use radio buttons to select deposit type instead of tabs
deposit_type = st.radio(
    "Select deposit type:",
    ["Mineral Deposits", "Petroleum Deposits"],
    horizontal=True
)

if deposit_type == "Mineral Deposits":
    st.header("Mineral Deposit Modelling")
    
    # mineral selection
    st.sidebar.markdown('**Select minerals to display:**')
    selected_minerals = [m for m in minerals if st.sidebar.checkbox(m, value=True)]

    # Only show mineral controls if minerals are selected
    if selected_minerals:
        st.sidebar.markdown('**Mineral Parameters:**')
        n_deposits = st.sidebar.slider('Number of deposits per mineral', 10, 500, 100, 10)
        random_seed = st.sidebar.number_input('Random seed', value=42, step=1)

        # enhanced modeling mode selection
        modeling_mode = st.sidebar.radio(
            'Geological modelling mode',
            ['Orebody systems', 'Hydrothermal veins', 'Sedimentary layers', 'Contact metamorphic', 'Placer deposits']
        )
        
        # geological parameters
        st.sidebar.markdown('**Geological Parameters:**')
        depth_factor = st.sidebar.slider('Depth influence', 0.1, 2.0, 1.0, 0.1)
        structural_complexity = st.sidebar.slider('Structural complexity', 1, 5, 3, 1)
    else:
        st.warning("Please select at least one mineral to display the model.")

    def generate_realistic_deposits(mineral, mode, n_deposits, seed, depth_factor, complexity):
        """Generate geologically realistic mineral deposits"""
        np.random.seed(seed + hash(mineral) % 1000)
        
        if mode == 'Orebody systems':
            # Create pipe-like or lode-like orebodies
            center = np.random.uniform(-30, 30, size=3)
            # Elongated body with preferred orientation
            strike = np.random.uniform(0, 2*np.pi)
            dip = np.random.uniform(np.pi/6, np.pi/2)
            
            # Generate points along the orebody axis
            length = np.random.uniform(20, 40)
            t = np.random.uniform(0, length, n_deposits)
            
            # Main axis direction
            axis = np.array([np.cos(strike), np.sin(strike), -np.sin(dip)])
            
            coords = []
            for i, pos in enumerate(t):
                base_pos = center + pos * axis
                # Add scatter perpendicular to main axis
                scatter = np.random.normal(0, 3 + pos*0.1, 3)
                scatter = scatter - np.dot(scatter, axis) * axis  # Remove component along axis
                coords.append(base_pos + scatter)
            
            coords = np.array(coords)
            
        elif mode == 'Hydrothermal veins':
            # Create branching vein systems
            start = np.random.uniform(-40, 40, size=3)
            coords = [start]
            
            current_pos = start.copy()
            branch_points = []
            
            for i in range(n_deposits - 1):
                # Main vein direction with some variation
                direction = np.random.normal([0.5, 0.3, -0.2], 0.3)
                direction = direction / np.linalg.norm(direction)
                
                step_size = np.random.uniform(1, 4)
                current_pos = current_pos + direction * step_size
                coords.append(current_pos.copy())
                
                # Occasional branching
                if np.random.random() < 0.1 and len(branch_points) < complexity:
                    branch_points.append(current_pos.copy())
            
            # Add branch veins
            for branch_start in branch_points:
                branch_length = np.random.randint(5, 15)
                branch_pos = branch_start.copy()
                for _ in range(branch_length):
                    if len(coords) >= n_deposits:
                        break
                    direction = np.random.normal([0, 0, -0.5], 0.4)
                    direction = direction / np.linalg.norm(direction)
                    branch_pos = branch_pos + direction * np.random.uniform(1, 3)
                    coords.append(branch_pos.copy())
            
            coords = np.array(coords[:n_deposits])
            
        elif mode == 'Sedimentary layers':
            # Create stratified deposits
            n_layers = np.random.randint(2, complexity + 1)
            coords = []
            
            for layer in range(n_layers):
                layer_center = np.random.uniform(-40, 40, size=3)
                layer_center[2] = -20 - layer * 10  # Deeper layers
                
                points_in_layer = n_deposits // n_layers
                if layer == n_layers - 1:
                    points_in_layer = n_deposits - len(coords)
                
                # Create elliptical layer
                for _ in range(points_in_layer):
                    theta = np.random.uniform(0, 2*np.pi)
                    r = np.random.exponential(15)
                    x = layer_center[0] + r * np.cos(theta)
                    y = layer_center[1] + r * np.sin(theta)
                    z = layer_center[2] + np.random.normal(0, 2)
                    coords.append([x, y, z])
            
            coords = np.array(coords)
            
        elif mode == 'Contact metamorphic':
            # Create aureole around igneous intrusion
            intrusion_center = np.random.uniform(-20, 20, size=3)
            coords = []
            
            for _ in range(n_deposits):
                # Distance from intrusion affects probability
                distance = np.random.exponential(8)
                theta = np.random.uniform(0, 2*np.pi)
                phi = np.random.uniform(0, np.pi)
                
                x = intrusion_center[0] + distance * np.sin(phi) * np.cos(theta)
                y = intrusion_center[1] + distance * np.sin(phi) * np.sin(theta)
                z = intrusion_center[2] + distance * np.cos(phi)
                
                coords.append([x, y, z])
            
            coords = np.array(coords)
            
        elif mode == 'Placer deposits':
            # Create alluvial/stream deposits
            # Simulate valley/stream bed
            valley_direction = np.random.uniform(0, 2*np.pi)
            valley_axis = np.array([np.cos(valley_direction), np.sin(valley_direction), 0])
            
            coords = []
            stream_center = np.random.uniform(-30, 30, size=3)
            stream_center[2] = 0  # Near surface
            
            for i in range(n_deposits):
                # Follow valley direction
                distance_along = np.random.normal(0, 20)
                distance_across = np.random.exponential(5)
                if np.random.random() < 0.5:
                    distance_across *= -1
                
                pos = stream_center + distance_along * valley_axis
                pos[0] += distance_across * valley_axis[1]  # Perpendicular
                pos[1] -= distance_across * valley_axis[0]
                pos[2] += np.random.exponential(2)  # Slightly buried
                
                coords.append(pos)
            
            coords = np.array(coords)
        
        # Apply depth factor - deeper deposits are less dense
        coords[:, 2] *= depth_factor
        
        return coords

    # Generate deposits using enhanced models
    if selected_minerals:
        deposits = {}
        np.random.seed(random_seed)
        
        for mineral in minerals:
            deposits[mineral] = generate_realistic_deposits(
                mineral, modeling_mode, n_deposits, random_seed, depth_factor, structural_complexity
            )

        # Create 3D plot for minerals
        fig_minerals = go.Figure()

        for mineral in selected_minerals:
            coords = deposits[mineral]
            fig_minerals.add_trace(go.Scatter3d(
                x=coords[:, 0],
                y=coords[:, 1],
                z=coords[:, 2],
                mode='markers',
                marker=dict(size=6, color=minerals[mineral], opacity=0.8),
                name=mineral,
                hovertemplate=f'<b>{mineral}</b><br>X: %{{x:.1f}}<br>Y: %{{y:.1f}}<br>Depth: %{{z:.1f}}<extra></extra>'
            ))

        fig_minerals.update_layout(
            title=f'3D Mineral Deposit Model - {modeling_mode}',
            scene=dict(
                xaxis_title='Easting (km)',
                yaxis_title='Northing (km)', 
                zaxis_title='Elevation (m)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            legend_title_text='Minerals',
            margin=dict(l=0, r=0, b=0, t=40),
            height=600
        )

        st.plotly_chart(fig_minerals, use_container_width=True)
        
        # Add geological information
        st.markdown("### Geological Context")
        if modeling_mode == 'Orebody systems':
            st.info("**Orebody Systems:** Pipe-like or lode deposits formed by hydrothermal processes. Often associated with igneous intrusions.")
        elif modeling_mode == 'Hydrothermal veins':
            st.info("**Hydrothermal Veins:** Fracture-filling deposits with branching patterns. Common for precious metals.")
        elif modeling_mode == 'Sedimentary layers':
            st.info("**Sedimentary Layers:** Stratiform deposits in sedimentary rocks. Common for coal and iron formations.")
        elif modeling_mode == 'Contact metamorphic':
            st.info("**Contact Metamorphic:** Deposits formed in aureoles around igneous intrusions through thermal metamorphism.")
        elif modeling_mode == 'Placer deposits':
            st.info("**Placer Deposits:** Concentration of heavy minerals in alluvial sediments. Common for gold and gemstones.")

else:  # Petroleum Deposits
    st.header("Petroleum Deposit Modelling")
    
    # petroleum selection
    st.sidebar.markdown('**Select petroleum deposits to display:**')
    selected_petroleum = [p for p in petroleum if st.sidebar.checkbox(p, value=True, key=f"pet_{p}")]
    
    # Only show petroleum controls if deposits are selected
    if selected_petroleum:
        # petroleum controls
        st.sidebar.markdown('**Petroleum Parameters:**')
        basin_size = st.sidebar.slider('Basin size (km)', 20, 100, 50, 10)
        reservoir_count = st.sidebar.slider('Number of reservoirs', 1, 8, 3, 1)
        trap_efficiency = st.sidebar.slider('Trap efficiency', 0.1, 1.0, 0.6, 0.1)
        pet_random_seed = st.sidebar.number_input('Random seed', value=42, step=1, key="pet_seed")
    else:
        st.warning("Please select at least one petroleum deposit type to display the model.")
    def generate_petroleum_deposits(deposit_type, basin_size, reservoir_count, trap_efficiency, seed):
        """Generate realistic petroleum deposits"""
        np.random.seed(seed + hash(deposit_type) % 1000)
        
        reservoirs = []
        
        for reservoir_id in range(reservoir_count):
            # Create sedimentary basin structure
            basin_center = np.random.uniform(-basin_size/2, basin_size/2, size=2)
            
            if deposit_type == 'Oil':
                # Oil tends to be in structural highs
                depth_base = np.random.uniform(-3000, -1500)
                thickness = np.random.uniform(50, 200)
                
            elif deposit_type == 'Natural Gas':
                # Gas migrates higher, often caps oil
                depth_base = np.random.uniform(-2500, -800)
                thickness = np.random.uniform(30, 150)
                
            elif deposit_type == 'Oil Shale':
                # Source rock, typically deeper and more extensive
                depth_base = np.random.uniform(-4000, -2000)
                thickness = np.random.uniform(100, 500)
                
            elif deposit_type == 'Gas Hydrates':
                # Shallow marine or permafrost
                depth_base = np.random.uniform(-1000, -200)
                thickness = np.random.uniform(20, 100)
            
            # Create anticline or fault trap structure
            trap_type = np.random.choice(['anticline', 'fault_trap', 'stratigraphic'])
            
            if trap_type == 'anticline':
                # Dome-shaped structure
                n_points = int(100 * trap_efficiency)
                coords = []
                
                for _ in range(n_points):
                    # Distance from crest
                    r = np.random.exponential(basin_size / 8)
                    theta = np.random.uniform(0, 2*np.pi)
                    
                    x = basin_center[0] + r * np.cos(theta)
                    y = basin_center[1] + r * np.sin(theta)
                    
                    # Anticlinal structure - higher at center
                    elevation_factor = np.exp(-r / (basin_size / 6))
                    z = depth_base + thickness * elevation_factor + np.random.normal(0, thickness/10)
                    
                    coords.append([x, y, z])
                    
            elif trap_type == 'fault_trap':
                # Fault-bounded reservoir
                n_points = int(80 * trap_efficiency)
                coords = []
                
                # Fault orientation
                fault_strike = np.random.uniform(0, 2*np.pi)
                fault_normal = np.array([-np.sin(fault_strike), np.cos(fault_strike)])
                
                for _ in range(n_points):
                    # Points on upthrown side of fault
                    distance_from_fault = np.random.exponential(basin_size / 10)
                    along_fault = np.random.uniform(-basin_size/4, basin_size/4)
                    
                    pos = basin_center + distance_from_fault * fault_normal
                    pos += along_fault * np.array([np.cos(fault_strike), np.sin(fault_strike)])
                    
                    x, y = pos
                    z = depth_base + np.random.uniform(0, thickness)
                    
                    coords.append([x, y, z])
                    
            else:  # stratigraphic trap
                # Pinch-out or unconformity trap
                n_points = int(60 * trap_efficiency)
                coords = []
                
                for _ in range(n_points):
                    x = basin_center[0] + np.random.normal(0, basin_size/6)
                    y = basin_center[1] + np.random.normal(0, basin_size/6)
                    z = depth_base + np.random.uniform(0, thickness)
                    
                    coords.append([x, y, z])
            
            reservoirs.extend(coords)
        
        return np.array(reservoirs) if reservoirs else np.zeros((0, 3))
    
    # Generate petroleum deposits
    if selected_petroleum:
        petroleum_deposits = {}
        
        for pet_type in petroleum:
            petroleum_deposits[pet_type] = generate_petroleum_deposits(
                pet_type, basin_size, reservoir_count, trap_efficiency, pet_random_seed
            )
        
        # Create 3D plot for petroleum
        fig_petroleum = go.Figure()
        
        for pet_type in selected_petroleum:
            coords = petroleum_deposits[pet_type]
            if len(coords) > 0:
                fig_petroleum.add_trace(go.Scatter3d(
                    x=coords[:, 0],
                    y=coords[:, 1], 
                    z=coords[:, 2],
                    mode='markers',
                    marker=dict(size=8, color=petroleum[pet_type], opacity=0.7),
                    name=pet_type,
                    hovertemplate=f'<b>{pet_type}</b><br>X: %{{x:.1f}}<br>Y: %{{y:.1f}}<br>Depth: %{{z:.0f}}m<extra></extra>'
                ))
        
        fig_petroleum.update_layout(
            title='3D Petroleum Deposit Model - Sedimentary Basin',
            scene=dict(
                xaxis_title='Easting (km)',
                yaxis_title='Northing (km)',
                zaxis_title='Depth (m)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            legend_title_text='Petroleum Deposits',
            margin=dict(l=0, r=0, b=0, t=40),
            height=600
        )
        
        st.plotly_chart(fig_petroleum, use_container_width=True)
        
        # Add petroleum geology information  
        st.markdown("### Petroleum Geology")
        st.info("""
        **Petroleum Systems:** Hydrocarbon deposits form through source rock maturation, migration, and trapping.
        - **Source rocks** generate oil and gas through thermal maturation
        - **Migration** occurs along permeable pathways  
        - **Traps** concentrate hydrocarbons (structural, stratigraphic, combination)
        - **Seal rocks** prevent further migration
        """)

st.markdown('---')
st.markdown('**Instructions:**')
st.markdown('1. Use the sidebar to select deposit types and adjust geological parameters.')
st.markdown('2. Switch between mineral and petroleum deposit tabs.')
st.markdown('3. Explore different geological modelling modes for realistic deposit patterns.')
st.code('streamlit run mineral_3d_model.py', language='bash')