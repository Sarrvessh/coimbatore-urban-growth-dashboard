# Product

<!-- impeccable:product-schema 1 -->

## Platform
web

## Stack
delegated: Python 3.11, Streamlit and a reproducible geospatial ML pipeline, selected because the brief explicitly requires a lightweight dashboard and GIS analysis.

## Users
Urban-planning researchers and GIS/ML students evaluating historical built-up expansion and modelled urban-growth susceptibility in Coimbatore.

## Product Purpose
Turn openly sourced satellite and GIS inputs into traceable historical LULC, spatially validated urban-transition models, a cautious 2030 susceptibility surface, and report-ready outputs.

## Positioning
The project separates spatial cross-validation from the independent temporal 2025 backtest and records every source, fallback, and derived result.

## Capabilities and Constraints
Uses projected CRS EPSG:32643 for metric operations; does not invent data or metrics; QGIS processing is optional because QGIS MCP was unavailable when scaffolded.

## Evidence on Hand
No downloaded datasets or measured results are present at project creation. Public-source acquisition is performed by the pipeline and provenance is saved with outputs.

## Product Principles
- Reproducible, cache-aware stages.
- Temporal and spatial leakage controls.
- Cautious interpretation of model probabilities.
- Clear separation of observed, derived, and predicted data.
