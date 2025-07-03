# simsNstuff
## 3D Mineral Deposit Modelling Programme

A Streamlit webapp to visualise random 3D deposits of silver, gold, iron, copper, and coal. 

**Live App:** https://simsnstuff.streamlit.app/

You can:
- Select which minerals to display (sidebar checkboxes)
- Adjust the number of deposits per mineral (sidebar slider)
- Change the random seed for reproducibility (sidebar number input)
- Choose the deposit modelling mode (sidebar radio buttons, click-only)
- Interact with the 3D model in your browser (Plotly)

*Note: This app uses British English spelling throughout.*

### Requirements
- Python 3.8+
- Packages: numpy, streamlit, plotly

Install requirements (if needed):
```
pip install numpy streamlit plotly
```

### Running the App Locally
From your project directory, run:
```
streamlit run mineral_3d_model.py
```
If `streamlit` is not in your PATH, use the full path to your Miniconda Scripts folder:
```
C:/Users/[userprofilehere]/AppData/Local/miniconda3/Scripts/streamlit.exe run mineral_3d_model.py
```

### Deployment
The app is deployed on Streamlit Cloud and requires a `requirements.txt` file containing the necessary dependencies.

### Features
- Interactive 3D visualisation (Plotly)
- Sidebar controls for mineral selection, deposit count, random seed, and modelling mode
- Colour-coded minerals
- Click-only radio buttons for modelling mode selection

### Modelling Modes
The app supports four different 3D mineral deposit modelling styles. Use the sidebar to select one:

- **Gaussian blobs:** Each mineral forms a cluster in 3D space (default, similar to previous version).
- **Veins:** Simulates mineral veins as random walks in 3D.
- **Layers:** Deposits are distributed in a planar or ellipsoidal layer.
- **Voxel grid:** Deposits fill a 3D grid, visualising high-density regions.

Switch between these modes to explore different geological scenarios for each mineral type.