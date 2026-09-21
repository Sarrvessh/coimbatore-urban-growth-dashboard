from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
def path(*parts):
    p = ROOT.joinpath(*parts); p.parent.mkdir(parents=True, exist_ok=True); return p
def config():
    with open(ROOT / 'config' / 'config.yaml', encoding='utf-8') as f: return yaml.safe_load(f)
def ensure_layout():
    for p in ['data/raw','data/interim','data/processed','data/external','models','outputs/maps','outputs/figures','outputs/tables','outputs/predictions','outputs/metrics','qgis/project','qgis/styles','qgis/exports','notebooks','app']:
        (ROOT / p).mkdir(parents=True, exist_ok=True)
