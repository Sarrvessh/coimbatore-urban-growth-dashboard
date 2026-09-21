import numpy as np, joblib, rasterio
from src.utils.paths import path
def main():
    from src.utils.paths import config
    qc=config().get('quality_control',{})
    if qc.get('ml_paused') or not qc.get('lulc_qc_passed'):
        raise RuntimeError('Prediction is paused: corrected LULC layers have not passed QC.')
    bundle=joblib.load(path('models','final_model.joblib')); idx=np.load(path('data','processed','landsat_2025_indices.npz'))
    with rasterio.open(path('data','processed','lulc_2025.tif')) as src: lulc=src.read(1); profile=src.profile
    rows,cols=np.indices(lulc.shape); x=profile['transform'].c+(cols+.5)*profile['transform'].a; y=profile['transform'].f+(rows+.5)*profile['transform'].e
    data={'x':x.ravel(),'y':y.ravel(),'ndvi':idx['ndvi'].ravel(),'ndbi':idx['ndbi'].ravel(),'ndwi':idx['ndwi'].ravel(),'historical_lulc':lulc.ravel()}
    import pandas as pd; frame=pd.DataFrame(data); valid=(lulc.ravel()>0)&(lulc.ravel()!=1)&frame[bundle['features']].notna().all(axis=1); out=np.full(lulc.size,np.nan,dtype='float32'); out[valid]=bundle['model'].predict_proba(frame.loc[valid,bundle['features']])[:,1]; out=out.reshape(lulc.shape)
    profile.update(dtype='float32',nodata=np.nan,compress='lzw');
    with rasterio.open(path('outputs','predictions','urban_growth_probability_2030.tif'),'w',**profile) as dst: dst.write(out,1)
    cats=np.where(np.isnan(out),0,np.minimum((out/.2).astype('uint8')+1,5)); profile.update(dtype='uint8',nodata=0)
    with rasterio.open(path('outputs','predictions','urban_growth_susceptibility_2030.tif'),'w',**profile) as dst: dst.write(cats,1)
if __name__=='__main__': main()
