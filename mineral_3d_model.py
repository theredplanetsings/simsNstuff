"""
3D Mineral Deposit Modeling Program

3d Visualisation of random deposits of silver, gold, iron, copper, and coal w/ matplotlib.

__author__ = "https://github.com/theredplanetsings"
__date__ = "01/7/2025"
"""
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# defining minerals and their colors
minerals = {
    'Silver': 'gray',
    'Gold': 'gold',
    'Iron': 'brown',
    'Copper': 'orange',
    'Coal': 'black'
}

st.title('3D Mineral Deposit Modeling Program')
st.markdown('Visualise random 3D deposits of silver, gold, iron, copper, and coal.')

# mineral selection
st.sidebar.markdown('**Select minerals to display:**')
selected_minerals = [m for m in minerals if st.sidebar.checkbox(m, value=True)]

# controls
n_deposits = st.sidebar.slider('Number of deposits per mineral', 10, 500, 100, 10)
random_seed = st.sidebar.number_input('Random seed', value=42, step=1)

# modeling mode selection (now using radio for click-only)
modeling_mode = st.sidebar.radio(
    'Modeling mode',
    ['Gaussian blobs', 'Veins', 'Layers', 'Voxel grid']
)

# random 3D coordinates for each mineral, depending on modeling mode
deposits = {}
np.random.seed(random_seed)

for mineral in minerals:
    if modeling_mode == 'Gaussian blobs':
        # each deposit is a 3D Gaussian blob
        center = np.random.uniform(-50, 50, size=3)
        coords = np.random.normal(loc=center, scale=10, size=(n_deposits, 3))
    elif modeling_mode == 'Veins':
        # simulate a vein as a random walk in 3D
        start = np.random.uniform(-50, 50, size=3)
        steps = np.random.normal(loc=0, scale=3, size=(n_deposits, 3))
        coords = np.cumsum(np.vstack([start, steps]), axis=0)[:n_deposits]
    elif modeling_mode == 'Layers':
        # deposits in a planar/ellipsoidal layer
        center = np.random.uniform(-50, 50, size=3)
        # random points in a plane with some thickness
        theta = np.random.uniform(0, 2*np.pi, n_deposits)
        r = np.random.normal(20, 5, n_deposits)
        x = center[0] + r * np.cos(theta)
        y = center[1] + r * np.sin(theta)
        z = center[2] + np.random.normal(0, 2, n_deposits)  # thin layer
        coords = np.column_stack([x, y, z])
    elif modeling_mode == 'Voxel grid':
        # fill a 3D grid and sample high-density region
        grid_size = 30
        grid = np.zeros((grid_size, grid_size, grid_size))
        # create a blob in the grid
        cx, cy, cz = np.random.randint(10, 20, size=3)
        for _ in range(n_deposits * 2):
            x = int(np.clip(np.random.normal(cx, 4), 0, grid_size-1))
            y = int(np.clip(np.random.normal(cy, 4), 0, grid_size-1))
            z = int(np.clip(np.random.normal(cz, 4), 0, grid_size-1))
            grid[x, y, z] += 1
        # sample points from high-density voxels
        xs, ys, zs = np.where(grid > 0)
        idx = np.random.choice(len(xs), size=min(n_deposits, len(xs)), replace=False)
        coords = np.column_stack([
            xs[idx] * 3 - 45,
            ys[idx] * 3 - 45,
            zs[idx] * 3 - 45
        ])
    else:
        coords = np.zeros((n_deposits, 3))
    deposits[mineral] = coords

# prepares our plotly 3d scatter plot
fig = go.Figure()

for mineral in selected_minerals:
    coords = deposits[mineral]
    fig.add_trace(go.Scatter3d(
        x=coords[:, 0],
        y=coords[:, 1],
        z=coords[:, 2],
        mode='markers',
        marker=dict(size=7, color=minerals[mineral]),
        name=mineral
    ))

fig.update_layout(
    title='3D Mineral Deposit Model',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
    ),
    legend_title_text='Minerals',
    margin=dict(l=0, r=0, b=0, t=40)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('---')
st.markdown('**Instructions:**')
st.markdown('1. Use the sidebar to select minerals and adjust deposit count.\n2. To run this app:')
st.code('streamlit run mineral_3d_model.py', language='bash')