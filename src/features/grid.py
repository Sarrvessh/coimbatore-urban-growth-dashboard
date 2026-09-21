"""Create the common 100 m analysis lattice and metric distance covariates."""
import numpy as np
import geopandas as gpd
from shapely.geometry import box, Point
from src.data.boundary import fetch_boundary
from src.utils.paths import path, config

def grid():
    out=path('data','processed','analysis_grid.gpkg')
    if out.exists(): return gpd.read_file(out)
    area=fetch_boundary(); cell=config()['project']['cell_size_m']; minx,miny,maxx,maxy=area.total_bounds
    cells=[box(x,y,x+cell,y+cell) for x in np.arange(minx,maxx,cell) for y in np.arange(miny,maxy,cell)]
    g=gpd.GeoDataFrame({'cell_id':range(len(cells))},geometry=cells,crs=area.crs)
    g=g[g.centroid.within(area.geometry.iloc[0])].copy(); g.to_file(out,driver='GPKG'); return g

def distances():
    g=grid(); crs=g.crs
    sources={'road_distance_m':'roads','rail_distance_m':'railways','industrial_distance_m':'industrial','water_distance_m':'water'}
    for col,name in sources.items():
        f=path('data','external',f'{name}.gpkg')
        if f.exists():
            layer=gpd.read_file(f).to_crs(crs); g[col]=g.centroid.apply(lambda p: layer.distance(p).min())
    x,y=config()['study_area']['city_centre_wgs84']; centre=gpd.GeoSeries([Point(x,y)],crs=4326).to_crs(crs).iloc[0]
    g['city_centre_distance_m']=g.centroid.distance(centre)
    g.to_file(path('data','processed','analysis_grid_features.gpkg'),driver='GPKG'); return g

if __name__ == '__main__': distances()
