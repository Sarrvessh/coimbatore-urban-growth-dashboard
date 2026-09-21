"""Safe stage runner. Each stage is cache-aware and produces only sourced/derived outputs."""
import argparse
from src.utils.paths import ensure_layout
from src.data.boundary import fetch_boundary
from src.data.osm import fetch_osm
from src.data.imagery import find_scenes
from src.data.preprocess import main as preprocess
from src.features.grid import distances
from src.features.dataset import main as dataset
from src.models.train import train
from src.visualization.maps import main as maps

STAGES={'boundary':fetch_boundary,'osm':fetch_osm,'scenes':find_scenes,'preprocess':preprocess,'dataset':dataset,'train':train,'maps':maps,'features':distances}
def main():
    p=argparse.ArgumentParser(); p.add_argument('stage',choices=[*STAGES,'all']); args=p.parse_args(); ensure_layout()
    for key in (STAGES if args.stage=='all' else [args.stage]):
        print(f'Running {key}'); STAGES[key]()
if __name__=='__main__': main()
