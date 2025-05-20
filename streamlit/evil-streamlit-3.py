import streamlit as st
import pandas as pd

# --- Page config ---
st.set_page_config(page_title="Landfill SDSS Allocation Tool", layout="wide")
st.title("Landfill SDSS: Tonnage Allocation & Metrics")
st.markdown(
    "Allocate at least 1,250 t/day across candidate landfill sites, rank using weights, and flag feasible options."
)

# --- Site data ---
site_data = [
    {"Site": "Seneca Meadows Landfill",      "Tipping_Fee": 85,    "Project_Name": "Valley Infill - DEIS",      "Design_Capacity_tpd": 1250, "Service_Horizon_(yr)": 20, "Electric_Power_MW": 20,  "Hydrological_Risk": 0.298, "EJ_Rating": 0.4},
    {"Site": "Chaffee Solid Waste Facility", "Tipping_Fee": 48.75, "Project_Name": "Chaffee Vertical Expansion", "Design_Capacity_tpd": 1197, "Service_Horizon_(yr)": 7,  "Electric_Power_MW": 0,   "Hydrological_Risk": 0.227, "EJ_Rating": 0.2},
    {"Site": "DANC Regional Landfill",      "Tipping_Fee": 65.5,  "Project_Name": "DANC Lateral Expansion",     "Design_Capacity_tpd": 437,  "Service_Horizon_(yr)": 40, "Electric_Power_MW": 0,   "Hydrological_Risk": 0.102, "EJ_Rating": 0.5},
    {"Site": "Bath Landfill Eastern Expansion","Tipping_Fee":60,   "Project_Name":"Bath Eastern Expansion",     "Design_Capacity_tpd": 850,  "Service_Horizon_(yr)":20, "Electric_Power_MW":7.8, "Hydrological_Risk": 0.38,  "EJ_Rating": 0.5},
    {"Site": "Hyland Landfill",             "Tipping_Fee": 55,    "Project_Name": "Hyland Lateral & Vertical Mod", "Design_Capacity_tpd":1200, "Service_Horizon_(yr)":25, "Electric_Power_MW":15.1,"Hydrological_Risk":0.62,  "EJ_Rating":0.3},
    {"Site": "OCRRA Site 31 Landfill",     "Tipping_Fee": 62,    "Project_Name": "OCRRA Site 31 Permit Renewal",   "Design_Capacity_tpd":480,  "Service_Horizon_(yr)":25, "Electric_Power_MW":8.2, "Hydrological_Risk":0.32,  "EJ_Rating":0.5},
    {"Site": "Bristol Hill Landfill (Cell 5)","Tipping_Fee":68.5, "Project_Name":"Bristol Hill Cell 5 Liner Contract","Design_Capacity_tpd":600,  "Service_Horizon_(yr)":15, "Electric_Power_MW":8.9, "Hydrological_Risk":0.434, "EJ_Rating":0.7},
    {"Site": "Potential Site H (Plattekill)","Tipping_Fee":85,   "Project_Name":"UCRRA Site H Candidate",        "Design_Capacity_tpd":3000, "Service_Horizon_(yr)":30, "Electric_Power_MW":43.2,"Hydrological_Risk":0.491, "EJ_Rating":0.2},
    {"Site": "Potential Site I (Plattekill)","Tipping_Fee":85,   "Project_Name":"UCRRA Site I Candidate",        "Design_Capacity_tpd":2700, "Service_Horizon_(yr)":30, "Electric_Power_MW":33.2,"Hydrological_Risk":0.74,  "EJ_Rating":0.5}
]

# DataFrame and constants
ndf = pd.DataFrame(site_data)
max_fee = ndf['Tipping_Fee'].max()
min_horizon = int(ndf['Service_Horizon_(yr)'].min())

# --- Sidebar: Ranking Weights & Thresholds ---
st.sidebar.header("1) Ranking Weights & Threshold")
w_cost     = st.sidebar.slider("Cost weight",      0.0, 1.0, 0.3)
w_capacity = st.sidebar.slider("Capacity weight",  0.0, 1.0, 0.3)
w_risk     = st.sidebar.slider("HydroRisk weight", 0.0, 1.0, 0.2)
w_ej       = st.sidebar.slider("EJ weight",        0.0, 1.0, 0.2)
# Normalize
w_sum = w_cost + w_capacity + w_risk + w_ej
w_cost, w_capacity, w_risk, w_ej = [w/w_sum for w in (w_cost, w_capacity, w_risk, w_ej)]
thresh = st.sidebar.slider("Min. feasibility score", 0.0, 1.0, 0.2)

# --- Sidebar: Phase Buckets Configuration ---
st.sidebar.header("2) Phase Buckets Configuration")
st.sidebar.write(f"Phase 1 max ≤ smallest horizon = {min_horizon} yr")
phase1 = st.sidebar.number_input(
    "Phase 1 duration (yr)", min_value=1, max_value=min_horizon, value=min(min_horizon,5), step=1
)
horizon = st.sidebar.number_input(
    "Total horizon (yr)", min_value=phase1+1, value=max(phase1+1,20), step=1
)

# --- Compute static feasibility ---
feas = []
for _, r in ndf.iterrows():
    cost_scr = 1 - r['Tipping_Fee']/max_fee
    cap_scr  = 1.0
    risk_scr = 1 - r['Hydrological_Risk']
    ej_scr   = 1 - r['EJ_Rating']
    feas.append(w_cost*cost_scr + w_capacity*cap_scr + w_risk*risk_scr + w_ej*ej_scr)
ndf['Feasibility'] = feas

# --- Sidebar: Allocation (only feasible sites) ---
st.sidebar.header("3) Select & Allocate (≥1250 t/d)")
st.sidebar.write("Sites below feasibility threshold are disabled.")
alloc, total = {}, 0
for _, r in ndf.iterrows():
    s = r['Site']
    if r['Feasibility'] >= thresh:
        st.sidebar.markdown(f"<span style='color:green'>{s}</span>", unsafe_allow_html=True)
        qty = st.sidebar.number_input(
            f"Tons/day @ {s}", 0, r['Design_Capacity_tpd'], 0, step=25, key=s
        )
        alloc[s] = qty; total += qty
    else:
        st.sidebar.markdown(f"<span style='color:lightgray'>{s} (unavailable)</span>", unsafe_allow_html=True)

if total < 1250:
    st.sidebar.error(f"Total = {total} t/d (must ≥ 1250)")
else:
    st.sidebar.success(f"Total allocation = {total} t/d")

# --- Main: Display allocation & metrics ---
st.subheader("Allocation & Metrics View")
if total >= 1250:
    # Selected records
    recs = []
    for s, q in alloc.items():
        if q > 0:
            rec = ndf[ndf['Site']==s].iloc[0].to_dict()
            rec['Assigned_tpd'] = int(q)
            recs.append(rec)
    df_sel = pd.DataFrame(recs)
    
    # Dynamic scores
    df_sel['Cost_score']     = (1 - df_sel['Tipping_Fee']/max_fee)
    df_sel['Capacity_score'] = df_sel['Assigned_tpd']/df_sel['Design_Capacity_tpd']
    df_sel['Risk_score']     = 1 - df_sel['Hydrological_Risk']
    df_sel['EJ_score']       = 1 - df_sel['EJ_Rating']
    df_sel['Composite']      = (
        w_cost*df_sel['Cost_score'] + w_capacity*df_sel['Capacity_score']
        + w_risk*df_sel['Risk_score'] + w_ej*df_sel['EJ_score']
    )
    
    # Formatting
    df_fmt = df_sel.copy()
    df_fmt['Tipping_Fee']       = df_fmt['Tipping_Fee'].round(2)
    df_fmt['Electric_Power_MW'] = df_fmt['Electric_Power_MW'].round(2)
    df_fmt['EJ_Rating']         = df_fmt['EJ_Rating'].round(2)
    df_fmt['Composite']         = df_fmt['Composite'].round(2)
    df_fmt['Service_Horizon_(yr)'] = df_fmt['Service_Horizon_(yr)'].astype(int)
    df_fmt['Design_Capacity_tpd'] = df_fmt['Design_Capacity_tpd'].astype(int)
    df_fmt['Assigned_tpd']      = df_fmt['Assigned_tpd'].astype(int)

    cols = [
        'Site','Project_Name','Service_Horizon_(yr)','Electric_Power_MW',
        'Assigned_tpd','Tipping_Fee','Design_Capacity_tpd',
        'Hydrological_Risk','EJ_Rating','Composite'
    ]
    st.table(df_fmt[cols].sort_values('Composite', ascending=False))

    # Phase calculations and price estimates
    st.subheader("Phase Capacities & Price Estimates")
    phase2_years = horizon - phase1
    # Phase 1
    p1 = df_sel[['Site','Assigned_tpd','Tipping_Fee']].copy()
    p1['Phase1_Capacity']    = p1['Assigned_tpd'] * 365 * phase1
    p1['Phase1_Revenue_$']    = p1['Phase1_Capacity'] * p1['Tipping_Fee']
    p1['P1_Rev_per_yr_$']     = p1['Phase1_Revenue_$'] / phase1
    st.markdown(f"**Phase 1: {phase1} years**")
    st.table(
        p1[['Site','Phase1_Capacity','Phase1_Revenue_$','P1_Rev_per_yr_$']]
        .round(2)
    )
    # Phase 2
    p2 = df_sel[['Site','Assigned_tpd','Tipping_Fee']].copy()
    p2['Phase2_Capacity']    = p2['Assigned_tpd'] * 365 * phase2_years
    p2['Phase2_Revenue_$']    = p2['Phase2_Capacity'] * p2['Tipping_Fee']
    p2['P2_Rev_per_yr_$']     = p2['Phase2_Revenue_$'] / phase2_years
    st.markdown(f"**Phase 2: {phase2_years} years**")
    st.table(
        p2[['Site','Phase2_Capacity','Phase2_Revenue_$','P2_Rev_per_yr_$']]
        .round(2)
    )

    # Map selectors and placeholders
    st.subheader("Maps: Select Site View")
    map_site = st.selectbox("Site for map views", df_sel['Site'], index=0)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Hydro-Risk Map")
        st.write(f"Map view for {map_site}")
        st.info("⚙️ Insert GeoJSON/folium map here")
    with c2:
        st.subheader("EJ Index Map")
        st.write(f"Map view for {map_site}")
        st.info("⚙️ Insert GeoJSON/folium map here")

    if st.button("Recompute & Analyze Phase Buckets"):
        st.success("Phase analysis stub triggered.")
else:
    st.info("Allocate at least 1,250 t/d across available sites to view metrics.")

