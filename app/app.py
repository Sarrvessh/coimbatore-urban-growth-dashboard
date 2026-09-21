"""A simple historical-to-susceptibility map timeline."""
from pathlib import Path
import numpy as np
import rasterio
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'processed'; O=ROOT/'outputs'/'predictions'
st.set_page_config(page_title='Coimbatore Growth',layout='wide')
st.markdown('<style>.stApp{background:#edf0e8}.block-container{max-width:1120px;padding-top:2rem}</style>',unsafe_allow_html=True)
st.title('Coimbatore Urban Growth')
st.caption('Move through time to see reference land cover transition toward the 2030 urban-growth susceptibility surface.')

sources={2010:P/'lulc_reference_2010.tif',2015:P/'lulc_reference_2015.tif',2020:P/'lulc_reference_2020.tif',2023:P/'lulc_reference_2023.tif',2030:O/'urban_growth_susceptibility_2030.tif'}
year=st.slider('Year',2010,2030,2020,1)
keys=sorted(sources); before=max(k for k in keys if k<=year); after=min(k for k in keys if k>=year)
def rgb(tif,future=False):
 with rasterio.open(tif) as s: a=s.read(1); n=s.nodata
 invalid=(a==n) if n is not None else ~np.isfinite(a)
 pal=np.array([[237,240,232],[166,61,64],[55,127,63],[185,201,90],[42,120,184],[182,139,90]],dtype=np.uint8)
 if future: pal=np.array([[237,240,232],[70,130,90],[166,196,110],[240,194,74],[225,125,52],[179,55,48]],dtype=np.uint8)
 out=pal[np.clip(a.astype(int),0,5)]; out[invalid]=[237,240,232]; return out
first=rgb(sources[before],before==2030); second=rgb(sources[after],after==2030)
mix=0 if before==after else (year-before)/(after-before); image=((1-mix)*first+mix*second).astype('uint8')
st.image(image,use_container_width=True,caption=f'{year}: transition between {before} and {after}' if before!=after else str(year))
if year<2030:
 st.markdown('**Land-cover legend:** <span style="color:#a63d40">■ Built-up</span> · <span style="color:#377f3f">■ Vegetation</span> · <span style="color:#b9c95a">■ Agriculture</span> · <span style="color:#2a78b8">■ Water</span> · <span style="color:#b68b5a">■ Barren/open</span>',unsafe_allow_html=True)
else:
 st.markdown('**2030 susceptibility legend:** <span style="color:#46825a">■ Very low</span> · <span style="color:#a6c46e">■ Low</span> · <span style="color:#f0c24a">■ Moderate</span> · <span style="color:#e17d34">■ High</span> · <span style="color:#b33730">■ Very high</span>',unsafe_allow_html=True)
st.caption('2010–2020 use ESA CCI reference LULC. 2023 uses Esri reference LULC. 2030 is a modelled susceptibility layer, not a guarantee of development.')
