# simsNstuff
## 3D Geological Deposit Modelling Programme

A Streamlit webapp to visualise realistic 3D deposits of minerals and petroleum using advanced geological modelling.

**Live Demo:** https://simsnstuff.streamlit.app/

### What You Can Do:
- **Mineral Deposits:** Model silver, gold, iron, copper, and coal using realistic geological formations
- **Petroleum Deposits:** Simulate oil, natural gas, oil shale, and gas hydrates in sedimentary basins
- Switch between deposit types using radio button selection
- Adjust geological parameters for realistic modelling
- Interact with 3D models in your browser (Plotly)

*Note: This app uses British English spelling throughout.*

### Requirements
- Python 3.8+
- Packages: numpy, streamlit, plotly, scipy

Install requirements (if needed):
```
pip install numpy streamlit plotly scipy
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
- **Dual Mode Interface:** Switch between mineral and petroleum deposit modelling
- **Interactive 3D Visualisation:** Plotly-powered 3D scatter plots with hover information
- **Conditional Sidebar Controls:** Only relevant parameters show based on selected deposit type
- **Realistic Geological Modelling:** Based on actual geological principles and formations
- **Colour-coded Deposits:** Easy identification of different mineral and petroleum types
- **Click-only Controls:** Radio buttons prevent accidental text input

### Mineral Deposit Modelling Modes
Advanced geological modelling styles for mineral deposits:

- **Orebody Systems:** Pipe-like or lode deposits formed by hydrothermal processes, often associated with igneous intrusions
- **Hydrothermal Veins:** Fracture-filling deposits with branching patterns, common for precious metals
- **Sedimentary Layers:** Stratiform deposits in sedimentary rocks, typical for coal and iron formations
- **Contact Metamorphic:** Deposits formed in aureoles around igneous intrusions through thermal metamorphism
- **Placer Deposits:** Concentration of heavy minerals in alluvial sediments, common for gold and gemstones

### Petroleum Deposit Features
Realistic petroleum system modelling includes:

- **Oil:** Structural high accumulations in anticlines and fault traps
- **Natural Gas:** Higher migration patterns with gas cap formations
- **Oil Shale:** Source rock distributions in deeper sedimentary basins
- **Gas Hydrates:** Shallow marine and permafrost deposit formations

### Geological Parameters
- **Depth Influence:** Controls how depth affects deposit density and distribution
- **Structural Complexity:** Influences fracturing, trap formation, and geological complexity
- **Basin Size:** Controls petroleum basin dimensions and reservoir distribution
- **Trap Efficiency:** Affects hydrocarbon concentration and migration patterns

Switch between different modes to explore various geological scenarios for each deposit type.
