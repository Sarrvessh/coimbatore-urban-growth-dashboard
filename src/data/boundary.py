"""Download and normalize a Coimbatore boundary from geoBoundaries."""
import json
import requests
import geopandas as gpd
from src.utils.paths import path, config

def fetch_boundary():
    cfg = config(); target = path('data', 'processed', 'coimbatore_boundary.gpkg')
    if target.exists(): return gpd.read_file(target)
    response = requests.get(cfg['study_area']['boundary_url'], timeout=60)
    response.raise_for_status()
    metadata = response.json()
    # geoBoundaries' country/ADM endpoint currently returns one dataset metadata
    # object, while older variants returned a list. Support both defensively.
    if isinstance(metadata, list):
        metadata = next((r for r in metadata if isinstance(r, dict)), None)
    if not isinstance(metadata, dict) or not metadata.get('gjDownloadURL'):
        raise RuntimeError('geoBoundaries did not provide an ADM2 GeoJSON download URL.')
    source_url = metadata['gjDownloadURL']
    raw_response = requests.get(source_url, timeout=120)
    raw_response.raise_for_status()
    raw = raw_response.json()
    gdf = gpd.GeoDataFrame.from_features(raw['features'], crs='EPSG:4326')
    attribute_columns = [c for c in gdf.columns if c != 'geometry']
    matches = gdf[attribute_columns].astype(str).apply(
        lambda row: row.str.contains('coimbatore', case=False, regex=False).any(), axis=1
    )
    gdf = gdf[matches].copy()
    if gdf.empty:
        raise RuntimeError('Coimbatore was absent from the downloaded India ADM2 boundary dataset.')
    gdf['geometry'] = gdf.geometry.make_valid()
    gdf = gdf[gdf.geometry.notna()].dissolve().to_crs(cfg['project']['crs_projected'])
    gdf.to_file(target, layer='coimbatore_boundary', driver='GPKG')
    path('data','processed','coimbatore_boundary_provenance.json').write_text(json.dumps({'source':source_url, 'crs':cfg['project']['crs_projected']}, indent=2))
    return gdf

if __name__ == '__main__': fetch_boundary()
