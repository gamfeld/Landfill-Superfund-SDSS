import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np

# target CRS
TARGET_CRS = 'EPSG:2260'  # NAD83 / New York East (ftUS)

# --- 1) Load & buffer your landfill polygon ---
landfill = (
    gpd.read_file('landfill.geojson')
       .to_crs(TARGET_CRS)
)
# 500 m ≈ 500 * 3.28084 = 1 640 ft
buffer_geom = landfill.buffer(1640)
buffer_area = buffer_geom.area.sum()

# --- 2) Vector hazard layers (all reprojected) ---
vector_layers = {
    'fema_floodplain':   'fema_floodplain.shp',
    'national_wetlands': 'wetlands.shp',
    'hydric_soils':      'hydric_soils.shp',
    'wellhead_areas':    'wellhead_protection.shp',
}

fractions = {}
for name, path in vector_layers.items():
    hazard = gpd.read_file(path).to_crs(TARGET_CRS)
    inter = gpd.overlay(
        gpd.GeoDataFrame(geometry=buffer_geom, crs=TARGET_CRS),
        hazard, how='intersection'
    )
    area_in_zone = inter.geometry.area.sum()
    fractions[name] = area_in_zone / buffer_area

# --- 3) Raster hazard: depth‐to‐water < 1 m ---
# assume 'depth_to_water.tif' is already in EPSG:2260; otherwise wrap it in a WarpedVRT.
with rasterio.open('depth_to_water.tif') as src:
    # mask with buffer footprint
    out_image, out_transform = mask(src, buffer_geom.geometry, crop=True)
    data = out_image[0]
    valid = data != src.nodata
    hazard = (data < 1.0) & valid
    fractions['depth_to_water'] = hazard.sum() / valid.sum()

# --- 4) Composite score ---
hydro_risk = np.mean(list(fractions.values()))

# --- Output ---
print("Layer fractions:")
for k, v in fractions.items():
    print(f"  {k}: {v:.2%}")
print(f"\nComposite HydroRisk = {hydro_risk:.2%}")
