"""Harmonize authoritative public LULC products to the project grid.
2010/2015/2020: ESA CCI 300 m. Latest: Esri annual LULC 2023 (10 m).
"""
import json, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.features import geometry_mask
from pystac_client import Client
import planetary_computer as pc
from scipy.ndimage import generic_filter
from src.data.preprocess import _grid
from src.utils.paths import path

def esa_map(a):
    out=np.zeros(a.shape,dtype='uint8'); out[np.isin(a,[190])]=1
    out[((a>=50)&(a<=180))]=2; out[(a>=10)&(a<=40)]=3
    out[a==210]=4; out[np.isin(a,[200,201,202,220])]=5; return out
def esri_map(a):
    out=np.zeros(a.shape,dtype='uint8'); out[a==7]=1; out[np.isin(a,[2,4,11])]=2
    out[a==5]=3; out[a==1]=4; out[np.isin(a,[8,9])]=5; return out
def mode(v):
    v=v[v>0]; return np.bincount(v.astype('uint8')).argmax() if len(v) else 0
def make(year,collection,item_id,asset,mapper):
    area,tr,w,h=_grid(); inside=geometry_mask(area.geometry,out_shape=(h,w),transform=tr,invert=True)
    c=Client.open('https://planetarycomputer.microsoft.com/api/stac/v1',modifier=pc.sign_inplace)
    item=next(iter(c.search(collections=[collection],ids=[item_id]).item_collection()))
    dest=np.zeros((h,w),dtype='uint16')
    with rasterio.open(item.assets[asset].href) as src:
        reproject(rasterio.band(src,1),dest,src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs=area.crs,resampling=Resampling.nearest,src_nodata=src.nodata,dst_nodata=0)
    out=mapper(dest); out[~inside]=0
    out=generic_filter(out,mode,size=3,mode='nearest').astype('uint8'); out[~inside]=0
    profile={'driver':'GTiff','height':h,'width':w,'count':1,'dtype':'uint8','crs':area.crs,'transform':tr,'nodata':0,'compress':'lzw'}
    target=path('data','processed',f'lulc_reference_{year}.tif')
    with rasterio.open(target,'w',**profile) as dst: dst.write(out,1)
    valid=inside&(out>0); px=abs(tr.a*tr.e)/1e6
    stats={'year':year,'source_collection':collection,'source_item':item_id,'valid_coverage_pct':round(100*valid.sum()/inside.sum(),3),'nodata_pct':round(100*(inside&~valid).sum()/inside.sum(),3),'builtup_km2':round(float((out==1).sum()*px),3),'filter':'3x3 majority'}
    path('outputs','tables',f'lulc_qc_{year}.json').write_text(json.dumps(stats,indent=2)); return stats
def main():
    rows=[]
    for y in [2010,2015,2020]:
        prefix='C3S' if y==2020 else 'ESACCI'; version='v2.1.1' if y==2020 else 'v2.0.7cds'
        rows.append(make(y,'esa-cci-lc',f'{prefix}-LC-L4-LCCS-Map-300m-P1Y-{y}-{version}-N00E045','lccs_class',esa_map))
    rows.append(make(2023,'io-lulc-annual-v02','43P-2023','data',esri_map))
    path('outputs','tables','lulc_qc_summary.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__': main()
