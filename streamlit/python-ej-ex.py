import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import pandas as pd
import numpy as np

# --- CONFIGURATION ---
TARGET_CRS   = 'EPSG:2260'    # NAD83 / NY East (ft US)
BUFFER_FT    = 500 * 3.28084  # 500 m ≈ 1 640 ft
WEIGHTS      = {'air':0.4, 'diesel':0.25, 'prox':0.2, 'demo':0.15}

# --- 1) LOAD & BUFFER SITES ---
sites = (gpd.read_file('landfills.geojson')
           .to_crs(TARGET_CRS))
sites['geometry'] = sites.geometry.buffer(BUFFER_FT)

# --- 2) RASTER METRICS: air toxics & diesel PM ---
rasters = {
    'air':    'air_toxics.tif',
    'diesel': 'diesel_pm.tif'
}

# --- 3) Demographics metrics (for now?): Census blocks ---
blocks = gpd.read_file('census_bg.shp').to_crs(TARGET_CRS)

# --- 4) EJ TRACTS for proximity ---
tracts = gpd.read_file('ej_tracts.shp').to_crs(TARGET_CRS)
tract_centroids = tracts.geometry.centroid

results = []
for _, site in sites.iterrows():
    geom = [mapping(site.geometry)]
    vals = {}

    # a) raster means within buffer
    for name, path in rasters.items():
        with rasterio.open(path) as src:
            arr, _ = mask(src, geom, crop=True)
            data = arr[0]
            valid = data != src.nodata
            vals[name] = float(data[valid].mean())

    # b) demographic: % low-income & % POC (maybe lol)
    clipped = gpd.overlay(blocks, gpd.GeoDataFrame(geometry=[site.geometry], crs=TARGET_CRS),
                          how='intersection')
    # area‐weighted average of each %
    areas = clipped.geometry.area
    demo_low  = (clipped['pct_low_income'] * areas).sum() / areas.sum()
    demo_poc  = (clipped['pct_poc']        * areas).sum() / areas.sum()
    vals['demo'] = float((demo_low + demo_poc) / 2)

    # c) proximity: inverse distance to nearest EJ tract centroid
    dists = tract_centroids.distance(site.geometry.centroid)
    nearest_m = dists.min()
    vals['prox'] = float(1 / (nearest_m/5280 + 1))  # convert ft→mi, invert+1

    results.append({
        'Site': site['Site'],
        **vals
    })

df = pd.DataFrame(results)

# --- 5) NORMALIZE to [0,1] across all sites ---
for col in ['air','diesel','demo','prox']:
    mn, mx = df[col].min(), df[col].max()
    df[col] = (df[col] - mn) / (mx - mn)

# --- 6) COMPOSITE EJIndex ---
df['EJIndex'] = sum(df[c]*w for c,w in WEIGHTS.items())

print(df[['Site','air','diesel','demo','prox','EJIndex']])
