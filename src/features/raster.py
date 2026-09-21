"""Spectral-index and conservative spectral-rule LULC utilities for pre-clipped reflectance rasters.
Rules are a transparent fallback only; replace with a documented labelled classifier when labels exist.
"""
import numpy as np
import rasterio

def safe_ratio(a,b): return np.divide(a-b,a+b,out=np.full(a.shape,np.nan,dtype='float32'),where=(a+b)!=0)
def indices(green,red,nir,swir): return {'ndvi':safe_ratio(nir,red),'ndbi':safe_ratio(swir,nir),'ndwi':safe_ratio(green,nir)}
def spectral_lulc(ndvi,ndbi,ndwi):
    # 1 built-up, 2 vegetation, 3 agriculture/open vegetation, 4 water, 5 barren/open; no ground-truth claim.
    out=np.full(ndvi.shape,5,dtype='uint8'); out[ndvi>0.45]=2; out[(ndvi>0.15)&(ndvi<=0.45)]=3; out[ndwi>0.15]=4; out[(ndbi>0.05)&(ndvi<0.3)&(ndwi<0.1)]=1; return out
def write_like(path, array, profile, nodata=-9999):
    profile.update(count=1,dtype=array.dtype,nodata=nodata,compress='lzw')
    with rasterio.open(path,'w',**profile) as dst: dst.write(array,1)
