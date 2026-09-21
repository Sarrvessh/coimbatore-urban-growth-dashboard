"""Query real Landsat scenes; saves a manifest before downstream download/compositing."""
import json
from pystac_client import Client
import planetary_computer as pc
from src.data.boundary import fetch_boundary
from src.utils.paths import path, config

def find_scenes():
    cfg=config(); bbox=list(fetch_boundary().to_crs(4326).total_bounds)
    catalog=Client.open(cfg['imagery']['catalog'], modifier=pc.sign_inplace); result={}
    for year in cfg['imagery']['years']:
        search=catalog.search(collections=[cfg['imagery']['collections'][year]], bbox=bbox, datetime=f'{year}-01-01/{year}-03-31', query={'eo:cloud_cover': {'lt': cfg['imagery']['max_cloud_cover']}})
        items=sorted(search.item_collection(), key=lambda i:i.properties.get('eo:cloud_cover',100))[:3]
        result[str(year)]=[{'id':i.id,'datetime':str(i.datetime),'cloud_cover':i.properties.get('eo:cloud_cover'),'assets':list(i.assets)} for i in items]
    path('data','raw','landsat_scene_manifest.json').write_text(json.dumps(result,indent=2)); return result

if __name__ == '__main__': find_scenes()
