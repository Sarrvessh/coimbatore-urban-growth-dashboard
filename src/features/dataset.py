"""Build leakage-safe temporal transition samples from aligned historical rasters."""
import numpy as np
import pandas as pd
import rasterio
from src.utils.paths import path

def make(start,end):
    base=path('data','processed',f'lulc_{start}.tif'); future=path('data','processed',f'lulc_{end}.tif'); idx=np.load(path('data','processed',f'landsat_{start}_indices.npz'))
    with rasterio.open(base) as a, rasterio.open(future) as b:
        old=a.read(1); new=b.read(1); rows,cols=np.indices(old.shape); xs,ys=rasterio.transform.xy(a.transform,rows,cols)
        x=np.asarray(xs).reshape(old.shape); y=np.asarray(ys).reshape(old.shape)
    valid=(old>0)&(new>0)&np.isfinite(idx['ndvi'])&np.isfinite(idx['ndbi'])&np.isfinite(idx['ndwi'])
    # Existing built-up is excluded: it cannot transition into urban land.
    valid &= old != 1
    d=pd.DataFrame({'cell_id':np.flatnonzero(valid),'x':x[valid],'y':y[valid],'ndvi':idx['ndvi'][valid],'ndbi':idx['ndbi'][valid],'ndwi':idx['ndwi'][valid],'historical_lulc':old[valid],'became_urban':(new[valid]==1).astype('uint8')})
    # 5×5 geographic blocks are spatial groups, not a random split.
    d['block']=pd.factorize(pd.cut(d.x,5).astype(str)+'_'+pd.cut(d.y,5).astype(str))[0]
    out=path('data','processed',f"{'train' if (start,end)==(2015,2020) else 'test'}_{start}_{end}.csv"); d.to_csv(out,index=False); return out
def main(): make(2015,2020); make(2020,2025)
if __name__=='__main__': main()
