"""
3D Mineral Deposit Modeling Program

3d Visualisation of random deposits of silver, gold, iron, copper, and coal w/ matplotlib.
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

# random 3D coordinates for each mineral
deposits = {}
np.random.seed(random_seed)
for mineral in minerals:
    # every deposit is a cluster in a different region
    center = np.random.uniform(-50, 50, size=3)
    coords = np.random.normal(loc=center, scale=10, size=(n_deposits, 3))
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