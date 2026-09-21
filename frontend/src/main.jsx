import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ImageOverlay, MapContainer, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './new.css';

const mapYears = [2010, 2015, 2020, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030];
const bounds = [[10.21836, 76.65844], [11.40656, 77.29951]];

function InitialExtent() {
  const map = useMap();
  useEffect(() => map.fitBounds(bounds), [map]);
  return null;
}

function App() {
  const [year, setYear] = useState(2020);
  const [methodologyOpen, setMethodologyOpen] = useState(false);
  const mapRef = useRef(null);
  const future = year >= 2024;
  const layerOpacity = future ? 1 : .82;
  const baselineLegend = [['#a63d40', 'Existing built-up', '2023 reference land cover'], ['#377f3f', 'Vegetation', '2023 reference land cover'], ['#b9c95a', 'Agriculture', '2023 reference land cover'], ['#2a78b8', 'Water', '2023 reference land cover'], ['#b68b5a', 'Open land', '2023 reference land cover']];
  const elapsedYears = year - 2023;
  const annualizedPercent = endpoint => (100 * (1 - (1 - endpoint) ** (elapsedYears / 7))).toFixed(1);
  const legend = future
    ? [['#ffe78f', 'Low likelihood', `Model probability · ${annualizedPercent(.08)}–${annualizedPercent(.16)}%`], ['#f6bd60', 'Moderate likelihood', `Model probability · ${annualizedPercent(.16)}–${annualizedPercent(.28)}%`], ['#e86f43', 'Elevated likelihood', `Model probability · ${annualizedPercent(.28)}–${annualizedPercent(.42)}%`], ['#9a2225', 'Highest likelihood', `Model probability · ${annualizedPercent(.42)}%+`], ...baselineLegend]
    : [['#a63d40', 'Built-up', 'Settlement and impervious land'], ['#377f3f', 'Vegetation', 'Trees and perennial cover'], ['#b9c95a', 'Agriculture', 'Cropland and managed fields'], ['#2a78b8', 'Water', 'Rivers, tanks, and reservoirs'], ['#b68b5a', 'Open land', 'Bare ground and scrub']];

  useEffect(() => {
    mapYears.forEach(mapYear => { const image = new Image(); image.src = `/maps/layer-${mapYear}.png`; });
  }, []);

  return <main>
    <header><b><em />Urban Growth</b><span className="location">Coimbatore, Tamil Nadu</span><span className="status">Interactive atlas</span></header>
    <section className="intro"><h1>Growth, mapped across time.</h1><span>Explore the changing urban landscape, from observed land cover to an evidence-led 2030 transition model.</span></section>
    <section className="workspace">
      <div className="map">
        <MapContainer ref={mapRef} center={[10.88, 76.98]} zoom={9} scrollWheelZoom className="leaf">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap contributors" opacity={future ? .55 : 1} />
          {future && <ImageOverlay url="/maps/layer-2023.png" bounds={bounds} opacity={.72} zIndex={499} />}
          <ImageOverlay url={`/maps/layer-${year}.png`} bounds={bounds} opacity={layerOpacity} zIndex={500} />
          <InitialExtent />
        </MapContainer>
        <div className="maptag"><strong>{year}</strong><span>{future ? `${year === 2030 ? 'XGBoost 2030 projection' : 'Annualized XGBoost scenario'} over 2023 land-cover context` : 'Reference land cover'}</span></div>
        <button className="reset-map" onClick={() => mapRef.current?.fitBounds(bounds)} aria-label="Reset map view">Reset view</button>
      </div>
      <aside>
        <h2>Temporal backtest</h2>
        <p className="evidence-meta"><span>Spatially held out</span><span>Exploratory model</span></p>
        <div className="metrics"><div><b>0.129</b><span>PR-AUC</span></div><div><b>0.061</b><span>F1 score</span></div><div><b>0.847</b><span>ROC-AUC</span></div><div><b>3.1%</b><span>Spatial IoU</span></div></div>
        <p className="note">The 2030 layer is for exploration. It is not a development forecast.</p>
        <button className="detail" onClick={() => setMethodologyOpen(true)}>View methodology</button>
      </aside>
    </section>
    <section className="timeline">
      <div><span>Timeline</span><b>{year}</b></div>
      <input aria-label="Map year" type="range" min="0" max={mapYears.length - 1} step="1" value={mapYears.indexOf(year)} onChange={event => setYear(mapYears[+event.target.value])} />
      <nav>{mapYears.map(stop => <button key={stop} onClick={() => setYear(stop)} className={stop === year ? 'active' : ''}>{stop === 2030 ? '2030 projection' : stop}</button>)}</nav>
      <p className="timeline-note">Each slider stop maps directly to one rendered layer. 2024–2029 are annualized scenarios derived from the cumulative 2030 XGBoost probability.</p>
    </section>
    <section className="legend">
      <div className="legend-intro"><h2>{future ? `${year} prediction & land cover` : 'Land cover key'}</h2><p>{future ? 'Warm colours are the annualized XGBoost probability output. The complete district beneath remains the 2023 reference land-cover context where prediction is not applicable.' : 'Observed reference classification for the selected year.'}</p></div>
      <div className="legend-items">{legend.map(([color, name, detail]) => <div className="legend-item" key={name}><i style={{ background: color }} /><div><b>{name}</b><span>{detail}</span></div></div>)}</div>
    </section>
    <section className="model-details" aria-labelledby="model-details-title">
      <div className="model-heading"><p>Model record</p><h2 id="model-details-title">What produced the prediction maps</h2><span>Every scenario map is traceable to the same tested transition model.</span></div>
      <div className="model-grid">
        <article><b>01</b><h3>Spatial inputs</h3><p>Coimbatore district boundary, Landsat-derived spectral indices, and historical land-cover classes were aligned on a 100 m grid in EPSG:32643.</p><div className="feature-list"><span>NDVI</span><span>NDBI</span><span>NDWI</span><span>Historical LULC</span></div></article>
        <article><b>02</b><h3>Model selection</h3><p>Logistic regression, random forest, and XGBoost were compared with five geographic blocks held apart to reduce spatial leakage.</p><div className="model-result"><strong>XGBoost</strong><span>Selected by spatial PR-AUC: 0.077</span></div></article>
        <article><b>03</b><h3>Independent check</h3><p>A separate 2020–2025 temporal holdout tested whether the approach could transfer across time rather than only across nearby places.</p><div className="model-result"><strong>PR-AUC 0.129</strong><span>ROC-AUC 0.847 · Spatial IoU 3.1%</span></div></article>
        <article><b>04</b><h3>Scenario generation</h3><p>The 2030 surface is the XGBoost transition probability. 2024–2029 apply a constant annual-hazard transformation of that cumulative probability.</p><div className="model-result"><strong>Exploratory use</strong><span>Use for discussion, not a planning decision.</span></div></article>
      </div>
    </section>
    <footer>Pan and scroll to zoom the map. 2030 is a modelled probability, not a guaranteed outcome.</footer>
    {methodologyOpen && <div className="modal" onClick={() => setMethodologyOpen(false)}><article onClick={event => event.stopPropagation()}><button aria-label="Close methodology" onClick={() => setMethodologyOpen(false)}>×</button><h2>How this view was produced</h2><p>Historical reference layers use ESA CCI (2010–2020) and Esri annual land cover (2023). Landsat spectral indices and historical land cover form the model inputs on a 100 m grid.</p><p>Logistic regression, random forest, and XGBoost were compared using five spatial blocks. XGBoost was selected, then tested on a separate 2020–2025 temporal holdout.</p><p>The 2030 overlay is the project’s exploratory XGBoost urban-transition probability. Because F1 and spatial IoU remain low, use every prediction map as a discussion layer only—not a planning decision.</p></article></div>}
  </main>;
}

createRoot(document.getElementById('app')).render(<App />);
