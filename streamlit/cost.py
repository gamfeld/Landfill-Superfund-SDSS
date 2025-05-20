import pandas as pd

data = {
    'Site': ['Seneca Meadows', 'Chaffee', 'DANC'],
    'Tipping_Fee': [85, 48.75, 65.5],   # $/ton
    'Dist_City_mi': [250, 300, 275],    # miles to NYC boundary
    'Dist_Rail_mi': [0.5, 1.0, 2.0],    # miles to nearest rail spur
    'Dist_Hwy_mi': [0.3, 1.0, 2.0]        # miles to nearest interstate
}
df = pd.DataFrame(data)

# --- WEIGHTS (arbitrary) --- 
w_fee, w_city, w_rail, w_hwy = 0.4, 0.3, 0.2, 0.1

# Normalize each column to [0,1]... 
for col in ['TFee', 'Dist_C', 'Dist_Rail_mi', 'Dist_Hwy_mi']:
    mn, mx = df[col].min(), df[col].max()
    df[col + '_norm'] = (df[col] - mn) / (mx - mn)

# --- COMPOSITE --- # 
df['CostIndex'] = (
    w_fee  * df['Tipping_Fee_norm']
  + w_city * df['Dist_City_mi_norm']
  + w_rail * df['Dist_Rail_mi_norm']
  + w_hwy  * df['Dist_Hwy_mi_norm']
)

print(df[['Site','CostIndex']])
