"""Create aligned 100 m Landsat stacks and spectral-rule LULC from selected PC scenes."""
import json
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from rasterio.features import geometry_mask
from rasterio.crs import CRS
from pystac_client import Client
import planetary_computer as pc
from src.data.boundary import fetch_boundary
from src.features.raster import indices, spectral_lulc
from src.utils.paths import path, config

def _grid():
    a=fetch_boundary(); c=config(); size=c['project']['cell_size_m']; x0,y0,x1,y1=a.total_bounds
    w=int(np.ceil((x1-x0)/size)); h=int(np.ceil((y1-y0)/size)); return a,from_origin(x0,y1,size,size),w,h
def _bands(year):
    # Planetary Computer exposes harmonised semantic keys for Landsat C2 L2.
    return {'blue':'blue','green':'green','red':'red','nir':'nir08','swir':'swir16'}
def process_year(year):
    out=path('data','processed',f'landsat_{year}_indices.npz'); lulc=path('data','processed',f'lulc_{year}.tif')
    if out.exists() and lulc.exists(): return
    c=config(); manifest=json.loads(path('data','raw','landsat_scene_manifest.json').read_text()); item_id=manifest[str(year)][0]['id']
    a,transform,w,h=_grid(); catalog=Client.open(c['imagery']['catalog'],modifier=pc.sign_inplace)
    inside = geometry_mask(a.geometry, out_shape=(h,w), transform=transform, invert=True)
    item=next(i for i in catalog.search(collections=[c['imagery']['collections'][year]],ids=[item_id]).item_collection())
    arrays={}
    for name,key in _bands(year).items():
        with rasterio.open(item.assets[key].href) as src:
            dest=np.full((h,w),np.nan,dtype='float32')
            reproject(rasterio.band(src,1),dest,src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs=a.crs,resampling=Resampling.bilinear,src_nodata=src.nodata,dst_nodata=np.nan)
            dest = dest*0.0000275-0.2; dest[~inside]=np.nan; arrays[name]=dest
    ind=indices(arrays['green'],arrays['red'],arrays['nir'],arrays['swir'])
    for value in ind.values(): value[~inside]=np.nan
    np.savez_compressed(out,**ind)
    profile={'driver':'GTiff','height':h,'width':w,'count':1,'dtype':'uint8','crs':a.crs,'transform':transform,'nodata':0,'compress':'lzw'}
    classified=spectral_lulc(**ind); classified[~inside]=0
    with rasterio.open(lulc,'w',**profile) as dst: dst.write(classified,1)
def main():
    for y in config()['imagery']['years']: process_year(y)
if __name__=='__main__': main()
