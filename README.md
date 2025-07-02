# simsNstuff

## 3D Mineral Deposit Modeling Program

Streamlit webapp visualises random 3D deposits of silver, gold, iron, copper, and coal. You can:
- Select which minerals to display
- Adjust the number of deposits per mineral
- Change the random seed for reproducibility
- Interact with the 3D model in your browser

### Requirements
- Python 3.8+
- Packages: numpy, streamlit, plotly

Install requirements (if needed):
```
pip install numpy streamlit plotly
```

### Running the App
From your project directory, run:
```
streamlit run mineral_3d_model.py
```
Or, if `streamlit` is not in your PATH, use the full path to your Miniconda Scripts folder:
```
C:/Users/[userprofilehere]/AppData/Local/miniconda3/Scripts/streamlit.exe run mineral_3d_model.py
```

### Features
- Interactive 3D visualisation (Plotly)
- Sidebar controls for mineral selection and deposit count
- Color-coded minerals