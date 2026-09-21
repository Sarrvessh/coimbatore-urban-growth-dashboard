"""Write web-ready PNGs and aligned urban-transition rasters from real LULC inputs."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import numpy as np, rasterio, matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from src.utils.paths import path, config
LULC=['#000000','#a63d40','#377f3f','#b9c95a','#2a78b8','#b68b5a']
def render(arr,out,cmap,bounds,title):
    plt.figure(figsize=(9,7)); plt.imshow(arr,cmap=cmap,norm=BoundaryNorm(bounds,len(cmap.colors))); plt.title(title); plt.axis('off'); plt.tight_layout(); plt.savefig(out,dpi=180,bbox_inches='tight'); plt.close()
def main():
    cm=ListedColormap(LULC); change_cm=ListedColormap(['#000000','#e45756','#ffffff'])
    years=[2010,2015,2020,2025]; rasters={}
    for y in years:
        with rasterio.open(path('data','processed',f'lulc_{y}.tif')) as src: rasters[y]=src.read(1); profile=src.profile
        render(rasters[y],path('outputs','maps',f'lulc_{y}.png'),cm,range(7),f'Coimbatore LULC {y} (spectral-rule derived)')
    rows=[]
    for a,b in zip(years,years[1:]):
        old,new=rasters[a],rasters[b]
        # 255 is NoData; 0 remains a valid "remained non-urban" observation.
        change=np.full(old.shape,255,dtype='uint8'); inside=(old>0)&(new>0); change[inside]=0
        change[inside&(old!=1)&(new==1)]=1; change[inside&(old==1)&(new==1)]=2
        profile.update(dtype='uint8',nodata=255,compress='lzw')
        out=path('outputs','predictions',f'urban_change_{a}_{b}.tif')
        with rasterio.open(out,'w',**profile) as dst: dst.write(change,1)
        render(np.ma.masked_equal(change,255),path('outputs','maps',f'urban_change_{a}_{b}.png'),change_cm,range(4),f'Urban change {a}–{b}')
        pixel=abs(profile['transform'].a*profile['transform'].e)/1e6; rows.append({'period':f'{a}-{b}','start_builtup_km2':float((old==1).sum()*pixel),'end_builtup_km2':float((new==1).sum()*pixel),'new_urban_km2':float((change==1).sum()*pixel)})
    import pandas as pd; pd.DataFrame(rows).to_csv(path('outputs','tables','urban_change_summary.csv'),index=False)
if __name__=='__main__': main()
