import streamlit as st
import subprocess
import json

st.set_page_config(page_title="Seneca Hills Landfill", layout="wide")

st.title("Landfill Scenario Configurator - Seneca Meadow Site")
st.markdown("Use the sliders and checkboxes below to configure your expansion scenario. Then run the model to check for compliance issues! (hopefully lol)")

# --- Sidebar for Parameters ---
st.sidebar.header("Controls (tentative)")

expansion_acreage = st.sidebar.slider("Expansion Acreage (acres)", 0, 100, 30)
height_increase_ft = st.sidebar.slider("Height Increase (ft)", 0, 100, 50)
buffer_installed = st.sidebar.checkbox("Install Riparian Buffer", value=True)
turbine_efficiency_pct = st.sidebar.slider("Turbine Efficiency (%)", 25.0, 45.0, 34.5)
fill_rate_tpd = st.sidebar.slider("Fill Rate (tons/day)", 4000, 10000, 7500)
rng_upgrade = st.sidebar.checkbox("Adopt RNG Upgrade?", value=False)

# --- External Policy Driver ---
policy_pressure = st.sidebar.checkbox("Activate Policy Pressure (stricter VOC limits)", value=False)

# --- Scenario Object ---
scenario = {
    "spatial_params": {
        "expansion_acreage": expansion_acreage,
        "height_increase_ft": height_increase_ft,
        "buffer_installed": buffer_installed
    },
    "nonspatial_params": {
        "fill_rate_tpd": fill_rate_tpd,
        "turbine_efficiency_pct": turbine_efficiency_pct,
        "rng_upgrade": rng_upgrade
    },
    "external_drivers": {
        "policy_pressure": {"active": policy_pressure}
    }
}

# --- Show scenario JSON ---
st.subheader("Current Scenario")
st.json(scenario)

# --- Run Model Button ---
if st.button("Run Scenario Model!"):
    st.success("Scenario launched!")
    # Here you would normally save to JSON, then call your QGIS backend script.
    with open("scenario.json", "w") as f:
        json.dump(scenario, f, indent=2)

    # Example subprocess to call a QGIS Processing script
    try:
        subprocess.run([
            "python3", "qgis_model_runner.py", "scenario.json"
        ], check=True)
        st.success("QGIS Model processing completed successfully!")
    except subprocess.CalledProcessError:
        st.error("QGIS Model processing failed. Check logs.")

# --- Instructions ---
st.info("""
**Other stuff**
1. Streamlit saves `scenario.json` file.
2. Streamlit triggers an external call to a Python script (e.g., `qgis_model_runner.py`).
3. `qgis_model_runner.py` reads `scenario.json`, opens QGIS Processing Engine, modifies layers, runs tools (but not now ofc)
4. Outputs (e.g., updated maps, rasters, reports) are saved and can be reloaded here.
""")

