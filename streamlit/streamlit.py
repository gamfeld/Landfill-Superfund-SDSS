import streamlit as st
import pandas as pd

# --- Page config ---
st.set_page_config(page_title="Landfill SDSS Allocation Tool", layout="wide")
st.title("Landfill SDSS: Tonnage Allocation & Metrics")
st.markdown(
    "Allocate a total of 1,250 t/day across candidate landfill sites, then rank selected sites using custom weights."
)

# --- Site data ---
site_data = [
    {"Site": "Seneca Meadows Landfill",      "Tipping_Fee": 85,    "Project_Name": "Valley Infill - DEIS",      "Design_Capacity_tpd": 1125, "Hydrological_Risk": 0.298, "EJ_Rating": 0.4},
    {"Site": "Chaffee Solid Waste Facility", "Tipping_Fee": 48.75, "Project_Name": "Chaffee Vertical Expansion", "Design_Capacity_tpd": 1197, "Hydrological_Risk": 0.227, "EJ_Rating": 0.2},
    {"Site": "DANC Regional Landfill",      "Tipping_Fee": 65.5,  "Project_Name": "DANC Lateral Expansion",     "Design_Capacity_tpd": 437,  "Hydrological_Risk": 0.102, "EJ_Rating": 0.5},
    {"Site": "Bath Landfill Eastern Expansion","Tipping_Fee":60,   "Project_Name":"Bath Easter",                 "Design_Capacity_tpd": 850,  "Hydrological_Risk": 0.38,  "EJ_Rating": 0.5},
    {"Site": "Hyland Landfill",             "Tipping_Fee": 55,    "Project_Name": "Hyland Lateral and Vertical Mod", "Design_Capacity_tpd":1200, "Hydrological_Risk":0.62,  "EJ_Rating":0.3},
    {"Site": "OCRRA Site 31 Landfill",     "Tipping_Fee": 62,    "Project_Name": "OCRRA Site 31 Permit Renewal",   "Design_Capacity_tpd":480,  "Hydrological_Risk":0.32,  "EJ_Rating":0.5},
    {"Site": "Bristol Hill Landfill (Cell 5)","Tipping_Fee":68.5, "Project_Name":"Bristol Hill Cell 5 Liner Contract","Design_Capacity_tpd":600,  "Hydrological_Risk":0.434, "EJ_Rating":0.7},
    {"Site": "Potential Site H (Plattekill)","Tipping_Fee":85,   "Project_Name":"UCRRA Site H Candidate",        "Design_Capacity_tpd":3000, "Hydrological_Risk":0.491, "EJ_Rating":0.2},
    {"Site": "Potential Site I (Plattekill)","Tipping_Fee":85,   "Project_Name":"UCRRA Site I Candidate",        "Design_Capacity_tpd":2700, "Hydrological_Risk":0.74,  "EJ_Rating":0.5}
]

df_sites = pd.DataFrame(site_data)
capacity_lookup = df_sites.set_index('Site')['Design_Capacity_tpd'].to_dict()

# --- Sidebar: Allocation ---
st.sidebar.header("1) Select Sites & Allocate Tonnage")
sites = df_sites['Site'].tolist()
selected = st.sidebar.multiselect("Choose sites", sites, default=["Seneca Meadows Landfill"])

# Initialize allocations
if 'alloc' not in st.session_state:
    st.session_state.alloc = {s: 0 for s in sites}
    st.session_state.alloc['Seneca Meadows Landfill'] = 1250

total = 0
for site in selected:
    max_cap = capacity_lookup[site]
    alloc = st.sidebar.number_input(
        f"T/d @ {site}", min_value=0, value=st.session_state.alloc.get(site, 0), step=25, key=site
    )
    st.session_state.alloc[site] = alloc
    total += alloc
    if alloc > max_cap:
        st.sidebar.error(f"Allocation for {site} ({alloc}) exceeds capacity ({max_cap})")

# Enforce total
if total != 1250:
    st.sidebar.error(f"Total = {total} t/d (must = 1250)")
else:
    st.sidebar.success("Total allocation = 1,250 t/d")

# --- Sidebar: Ranking Weights ---
st.sidebar.header("2) Ranking Weights")
w_cost     = st.sidebar.slider("Cost weight",     0.0, 1.0, 0.3)
w_capacity = st.sidebar.slider("Capacity weight", 0.0, 1.0, 0.3)
w_risk     = st.sidebar.slider("HydroRisk weight",0.0, 1.0, 0.2)
w_ej       = st.sidebar.slider("EJ weight",       0.0, 1.0, 0.2)
# Normalize
w_sum = w_cost + w_capacity + w_risk + w_ej
w_cost, w_capacity, w_risk, w_ej = [w/w_sum for w in (w_cost, w_capacity, w_risk, w_ej)]

# --- Main: Display & Compute ---
st.subheader("Allocated Sites Overview & Rankings")
if total == 1250:
    selected_data = []
    for site in selected:
        data = df_sites[df_sites['Site']==site].iloc[0].to_dict()
        assigned = st.session_state.alloc[site]
        data['Assigned_tpd'] = assigned
        # Compute scores
        max_fee = df_sites['Tipping_Fee'].max()
        cost_score     = 1 - data['Tipping_Fee']/max_fee
        capacity_score = assigned / data['Design_Capacity_tpd']
        risk_score     = 1 - data['Hydrological_Risk']
        ej_score       = 1 - data['EJ_Rating']
        composite = (w_cost*cost_score + w_capacity*capacity_score 
                     + w_risk*risk_score + w_ej*ej_score)
        data.update({
            'Cost_score': round(cost_score,3),
            'Capacity_score': round(capacity_score,3),
            'Risk_score': round(risk_score,3),
            'EJ_score': round(ej_score,3),
            'Composite': round(composite,3)
        })
        selected_data.append(data)
    df_sel = pd.DataFrame(selected_data).sort_values('Composite', ascending=False)
    st.table(df_sel)

    # Map placeholders
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hydro-Risk Map")
        st.info("⚙️ Insert GeoJSON/folium map here")
    with col2:
        st.subheader("EJ Index Map")
        st.info("⚙️ Insert GeoJSON/folium map here")

    if st.button("Recompute Rankings & Feasibility"):
        st.success("Rankings updated.")
else:
    st.info("Adjust allocations to total exactly 1,250 t/d to view rankings.")

