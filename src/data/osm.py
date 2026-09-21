"""Acquire OSM transport, industrial and water features in UTM 43N."""
import osmnx as ox
from src.data.boundary import fetch_boundary
from src.utils.paths import path, config

def fetch_osm():
    crs = config()['project']['crs_projected']; poly = fetch_boundary().to_crs(4326).geometry.iloc[0]
    for name, tags in {'roads': {'highway': True}, 'railways': {'railway': True}, 'industrial': {'landuse': 'industrial'}, 'water': {'natural': 'water'}}.items():
        target = path('data','external',f'{name}.gpkg')
        if not target.exists():
            layer = ox.features_from_polygon(poly, tags).reset_index().to_crs(crs)
            layer[layer.geometry.notna()].to_file(target, layer=name, driver='GPKG')

if __name__ == '__main__': fetch_osm()
