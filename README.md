# Sims N Stuff: 3D Mineral/Petroleum Deposit Modelling Programme

Streamlit webapp for visualising 3D deposits of minerals & petroleum with geological modelling.

**Dashboard:** https://simsnstuff.streamlit.app/

### What You Can Do:
- **Mineral Deposits:** Model silver, gold, iron, copper, and coal using realistic geological formations
- **Petroleum Deposits:** Simulate oil, natural gas, oil shale, and gas hydrates in sedimentary basins
- **Real Data:** Visualise U.S. commodity production trends from official EIA sources (coal, crude oil, natural gas)
- **USGS Mineral Statistics:** View selected commodity snapshots for gold, silver, iron, copper, and coal
- **CSV Upload Overlay:** Upload your own mine or well coordinates and visualise them in 3D
- Switch between deposit types using radio button selection
- Adjust geological parameters for realistic modelling
- Interact with 3D models in your browser (Plotly)

### Requirements
- Python 3.8+
- Packages: numpy, streamlit, plotly, scipy

Install requirements (if needed):
```
pip install -r requirements.txt
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
On macOS/Linux, you can also run:
```
python -m streamlit run mineral_3d_model.py
```

### Deployment
The app is deployed on Streamlit Cloud and requires a `requirements.txt` file containing the necessary dependencies.

### Features
- **Multi-View Interface:** Switch between mineral, petroleum, and real-data views
- **Interactive 3D Visualisation:** Plotly-powered 3D scatter plots with hover information
- **Conditional Sidebar Controls:** Only relevant parameters show based on selected deposit type
- **Realistic Geological Modelling:** Based on actual geological principles and formations
- **Colour-coded Deposits:** Easy identification of different mineral and petroleum types
- **Click-only Controls:** Radio buttons prevent accidental text input
- **Export Ready:** Download generated mineral and petroleum point clouds as CSV files

## Changelog

### 2026-04-06
- Hardened CSV upload parsing to reject non-finite coordinates (`NaN`/`Inf`) and validate bytes-like input payloads.
- Expanded CSV parser contract tests for whitespace-heavy headers, blank rows, extra columns, and payload type handling.
- Added broader generator validation coverage for boolean and non-finite seed/count/efficiency edge cases.
- Made CSV export output deterministic by sorting label groups before writing rows.
- Extracted uploaded-point success-message formatting into a reusable helper with dedicated tests.
- Expanded CI test coverage to run unit tests on both Python 3.10 and 3.11.

### 2026-04-05
- Hardened seed and numeric validation paths in generator logic with clearer error handling.
- Expanded edge-case unit coverage for generators, CSV parsing, and CSV export formatting.
- Improved generation performance by vectorizing petroleum deposit point creation.
- Refactored repeated plotting and assumptions UI code into reusable app view helpers.
- Unified Plotly chart styling across mineral, petroleum, real-data, and uploaded-data views.
- Added baseline project quality tooling (`pyproject.toml`) and CI test workflow (`.github/workflows/tests.yml`).

### Earlier Updates
- Added clearer captions and widget help text for a more guided UI.
- Removed the unused live EIA fetch stub and kept the real-data helpers focused.
- Hardened CSV parsing and generator input validation for invalid inputs.
- Split the Streamlit UI into reusable view modules for easier maintenance.
- Deterministic generation with stable seeds and local RNG usage.
- Faster rendering by generating only selected deposit types.
- Refactored generation code into reusable modules with unit tests.
- Improved docs and project hygiene (`requirements.txt` bounds and `.gitignore` cleanup).
- Added CSV exports and clearer model assumptions in the UI.
- Added Real Data mode with EIA energy production trends.
- Added USGS mineral statistics snapshot view.
- Added CSV upload + validation for custom mine/well 3D overlays.

### Running Tests
From the project root, run:
```
python -m unittest discover -s tests -p "test_*.py"
```

### Developer Workflow
Recommended local quality checks before opening a PR:

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run tests:
```
python -m unittest discover -s tests -p "test_*.py"
```

3. Lint and format checks (if Ruff is installed):
```
ruff check .
ruff format --check .
```

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

## Licence

Creative Commons Zero v1.0 Universal (CC0) - Public domain dedication for maximum freedom
