import streamlit as st
import pandas as pd

# --- Page config ---
st.set_page_config(page_title="Landfill SDSS Allocation Tool", layout="wide")
st.title("Landfill SDSS: Tonnage Allocation & Metrics")
st.markdown(
    "Allocate ≥1,250 t/day across candidate landfill sites, rank by feasibility, and manage multi-phase horizons with revenue estimates."
)

# --- Site data ---
site_data = [
    {"Site": "Seneca Meadows Landfill",      "Tipping_Fee": 85,    "Project_Name": "Valley Infill - DEIS",      "Design_Capacity_tpd": 1250, "Service_Horizon_(yr)": 20, "Electric_Power_MW": 20,  "Hydrological_Risk": 0.298, "EJ_Rating": 0.4, "Dist_to_rail_mi": 0.5, "Dist_to_hwy_mi": 0.3},
    {"Site": "Chaffee Solid Waste Facility", "Tipping_Fee": 48.75, "Project_Name": "Chaffee Vertical Expansion", "Design_Capacity_tpd": 1197, "Service_Horizon_(yr)": 7,  "Electric_Power_MW": 0,   "Hydrological_Risk": 0.227, "EJ_Rating": 0.2, "Dist_to_rail_mi": None, "Dist_to_hwy_mi": 1.0},
    {"Site": "DANC Regional Landfill",      "Tipping_Fee": 65.5,  "Project_Name": "DANC Lateral Expansion",     "Design_Capacity_tpd": 437,  "Service_Horizon_(yr)": 40, "Electric_Power_MW": 0,   "Hydrological_Risk": 0.102, "EJ_Rating": 0.5, "Dist_to_rail_mi": None, "Dist_to_hwy_mi": 2.0},
    {"Site": "Bath Landfill Eastern Expansion","Tipping_Fee":60,   "Project_Name":"Bath Eastern Expansion",     "Design_Capacity_tpd": 850,  "Service_Horizon_(yr)":20, "Electric_Power_MW":7.8, "Hydrological_Risk": 0.38,  "EJ_Rating": 0.5, "Dist_to_rail_mi": None, "Dist_to_hwy_mi": 1.0},
    {"Site": "Hyland Landfill",             "Tipping_Fee": 55,    "Project_Name": "Hyland Lateral & Vertical Mod", "Design_Capacity_tpd":1200, "Service_Horizon_(yr)":25, "Electric_Power_MW":15.1,"Hydrological_Risk":0.62,  "EJ_Rating":0.3, "Dist_to_rail_mi": None, "Dist_to_hwy_mi": 0.5},
    {"Site": "OCRRA Site 31 Landfill",     "Tipping_Fee": 62,    "Project_Name": "OCRRA Site 31 Permit Renewal",   "Design_Capacity_tpd":480,  "Service_Horizon_(yr)":25, "Electric_Power_MW":8.2, "Hydrological_Risk":0.32,  "EJ_Rating":0.5, "Dist_to_rail_mi": 1.0, "Dist_to_hwy_mi": None},
    {"Site": "Bristol Hill Landfill (Cell 5)","Tipping_Fee":68.5, "Project_Name":"Bristol Hill Cell 5 Liner Contract","Design_Capacity_tpd":600,  "Service_Horizon_(yr)":15, "Electric_Power_MW":8.9, "Hydrological_Risk":0.434, "EJ_Rating":0.7, "Dist_to_rail_mi": 2.0, "Dist_to_hwy_mi": 2.0},
    {"Site": "Potential Site H (Plattekill)","Tipping_Fee":85,   "Project_Name":"UCRRA Site H Candidate",        "Design_Capacity_tpd":3000, "Service_Horizon_(yr)":30, "Electric_Power_MW":43.2,"Hydrological_Risk":0.491, "EJ_Rating":0.2, "Dist_to_rail_mi": 5.0, "Dist_to_hwy_mi": 1.0},
    {"Site": "Potential Site I (Plattekill)","Tipping_Fee":85,   "Project_Name":"UCRRA Site I Candidate",        "Design_Capacity_tpd":2700, "Service_Horizon_(yr)":30, "Electric_Power_MW":33.2,"Hydrological_Risk":0.74,  "EJ_Rating":0.5, "Dist_to_rail_mi": 5.0, "Dist_to_hwy_mi": 1.0}
]
ndf = pd.DataFrame(site_data)
max_fee = ndf['Tipping_Fee'].max()

# --- Sidebar: Ranking Weights & Threshold ---
st.sidebar.header("1) Ranking Weights & Threshold")
w_cost     = st.sidebar.slider("Cost weight",      0.0, 1.0, 0.3)
w_capacity = st.sidebar.slider("Capacity weight",  0.0, 1.0, 0.3)
w_risk     = st.sidebar.slider("HydroRisk weight", 0.0, 1.0, 0.2)
w_ej       = st.sidebar.slider("EJ weight",        0.0, 1.0, 0.2)
w_sum = w_cost + w_capacity + w_risk + w_ej
w_cost, w_capacity, w_risk, w_ej = [w/w_sum for w in (w_cost, w_capacity, w_risk, w_ej)]
thresh = st.sidebar.slider("Min. feasibility score", 0.0, 1.0, 0.2)
# Pre-compute feasibility
ndf['Feasibility'] = (
    (1-ndf['Tipping_Fee']/max_fee)*w_cost
    +1.0*w_capacity
    +(1-ndf['Hydrological_Risk'])*w_risk
    + (1-ndf['EJ_Rating'])*w_ej
)

# --- Sidebar: Allocation ---
st.sidebar.header("2) Select & Allocate ≥1250 t/d")
alloc, total = {}, 0
for _, r in ndf.iterrows():
    if r['Feasibility'] >= thresh:
        st.sidebar.markdown(f"<span style='color:green'>{r['Site']}</span>", unsafe_allow_html=True)
        qty = st.sidebar.number_input(f"T/d @ {r['Site']}", 0, r['Design_Capacity_tpd'], 0, step=25)
        alloc[r['Site']] = qty
        total += qty
    else:
        st.sidebar.markdown(f"<span style='color:lightgray'>{r['Site']} (unavailable)</span>", unsafe_allow_html=True)
if total < 1250:
    st.sidebar.error(f"Total = {total}, must ≥ 1250")
else:
    st.sidebar.success(f"Total allocation = {total}")

# Determine min horizon from selected sites
selected_sites = [s for s,q in alloc.items() if q>0]
min_horizon = int(ndf.loc[ndf['Site'].isin(selected_sites), 'Service_Horizon_(yr)'].min()) if selected_sites else int(ndf['Service_Horizon_(yr)'].min())

# --- Sidebar: Phase Setup ---
st.sidebar.header("3) Phase Setup")
n_phases = st.sidebar.number_input("Number of phases", min_value=1, max_value=5, value=1)
horizon = st.sidebar.number_input("Total horizon (yr)", min_value=1, value=min_horizon)
_durs, sum_d = [], 0
for i in range(1, n_phases+1):
    if i == 1:
        max_d = min(min_horizon, horizon - (n_phases - 1))
    else:
        max_d = horizon - sum_d - (n_phases - i)
    dur = st.sidebar.number_input(f"Phase {i} duration (yr)", 1, int(max_d), int(max_d))
    _durs.append(dur)
    sum_d += dur
if sum_d != horizon:
    st.sidebar.error(f"Sum of phases = {sum_d}, must = {horizon}")
else:
    st.sidebar.success(f"Phases sum to {horizon} yrs")
durations = _durs

# --- Main display ---
st.subheader("Allocation, Metrics & Phases")
if total >= 1250 and sum_d == horizon:
    # Build selected DataFrame
    df_sel = pd.DataFrame([
        {**ndf[ndf['Site']==s].iloc[0].to_dict(), 'Assigned_tpd': alloc[s]}
        for s in selected_sites if alloc[s] > 0
    ])
    # Compute metrics
    df_sel['Cost_score']     = (1 - df_sel['Tipping_Fee']/max_fee)
    df_sel['Capacity_score'] = df_sel['Assigned_tpd'] / df_sel['Design_Capacity_tpd']
    df_sel['Risk_score']     = 1 - df_sel['Hydrological_Risk']
    df_sel['EJ_score']       = 1 - df_sel['EJ_Rating']
    df_sel['Composite']      = (
        w_cost*df_sel['Cost_score'] + w_capacity*df_sel['Capacity_score']
        + w_risk*df_sel['Risk_score'] + w_ej*df_sel['EJ_score']
    )
    # Format
    for col in ['Tipping_Fee','Electric_Power_MW','EJ_Rating','Composite']:
        df_sel[col] = df_sel[col].round(2)
    df_sel[['Service_Horizon_(yr)','Design_Capacity_tpd','Assigned_tpd']] = \
        df_sel[['Service_Horizon_(yr)','Design_Capacity_tpd','Assigned_tpd']].astype(int)
    display_cols = [
        'Site','Project_Name','Service_Horizon_(yr)','Electric_Power_MW',
        'Assigned_tpd','Tipping_Fee','Design_Capacity_tpd',
        'Dist_to_rail_mi','Dist_to_hwy_mi',
        'Hydrological_Risk','EJ_Rating','Composite'
    ]
    st.table(df_sel[display_cols].sort_values('Composite', ascending=False))

    # Phase analysis & totals
    for idx, dur in enumerate(durations, 1):
        cap = df_sel['Assigned_tpd'] * 365 * dur
        rev = cap * df_sel['Tipping_Fee']
        per_yr = rev / dur
        st.subheader(f"Phase {idx} ({dur} yrs)")
        tbl = pd.DataFrame({
            'Site': df_sel['Site'],
            f'Phase{idx}_Cap': cap,
            f'/nPhase{idx}_Rev': rev,
            f'/nP{idx}_Rev_per_yr': per_yr
        })
        st.table(tbl.round(2))
        st.markdown(f"**Totals**: Cap={cap.sum():,.0f} t·yr, Rev=${rev.sum():,.2f}, Rev/yr avg=${per_yr.sum():,.2f}")

    # Maps using user-specified dummy files
    map_site = st.selectbox("Map view site", df_sel['Site'])
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Hydro-Risk Map")
        st.image('/home/gamfeld/Hunter/S25/GTECH-361/Project/Data/TEP.png', caption=f"Hydro-Risk: {map_site}")
    with c2:
        st.subheader("EJ Index Map")
        st.image('/home/gamfeld/Hunter/S25/GTECH-361/Project/Data/EJSCREEN.tiff', caption=f"EJ Index: {map_site}")
else:
    if total < 1250:
        st.info("Allocate at least 1,250 t/d in sidebar.")
    if sum_d != horizon:
        st.info("Ensure phase durations sum to total horizon.")

